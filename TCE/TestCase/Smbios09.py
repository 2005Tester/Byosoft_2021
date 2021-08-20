# -*- encoding=utf8 -*-
import re
from os.path import dirname
import logging
from Core.SutInit import Sut
from Report import ReportGen
from Core import SerialLib, SshLib, MiscLib
from Common.LogAnalyzer import LogAnalyzer
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import BiosCfg, Msg
from TCE.BaseLib import BmcLib


# Test case ID: 400-440, 527 reserved
##########################################
#           Smbios Test Cases            #
##########################################

# Test scope, smbios tables to be tested
TYPES = [0, 1, 2, 3, 4, 7, 9, 13, 16, 17, 19, 38, 39, 41, 127]

# LogAnalyzer
P = LogAnalyzer(SutConfig.Env.LOG_DIR)

# signals in rmt result
SIGNALS = "RxDqs- RxDqs+  RxV-  RxV+  TxDq-  TxDq+  TxV-  TxV+  Cmd-  Cmd+  CmdV-  CmdV+  Ctl-  Ctl+"


class Type128Test:
    def __init__(self, data_t128, data_ser, ssh_os):
        self.type128data = data_t128
        self.ssh_os = ssh_os
        self.base_addr = None
        self.rmt_mem_dic = {}
        self.rmt_serial_dic = {}
        self.serial_log = data_ser

    # get base address from smbios t128 data
    def get_base_addr(self):
        patten = r"80(?:\s[0-9A-F]{2}){15}"
        x = re.compile(patten)
        res = x.findall(self.type128data)
        if not len(res) == 1:
            logging.info("Type 128 data doesn't appear to be correct")
            return
        address_lst = res[0].split()[4:12]
        address_lst.reverse()
        if not len(address_lst) == 8:
            logging.info("Address should be 64it")
            return
        base_addr_str = "".join(address_lst)
        self.base_addr = int(base_addr_str, 16) + 0x10
        logging.info(f"Smbios Type-128 base address:{hex(self.base_addr)}")
        return self.base_addr

    def read_rmt_mem(self, ssh_os, base, size=0x2000):
        # return {addr: value}
        cmd = f'cd {SutConfig.Env.RW_PATH} &&./rw mmr {hex(base)} {hex(size)}'
        origin_data = SshLib.execute_command(ssh_os, cmd)
        pat = "([0-9a-f]{8}):((?:\s[0-9a-f]{4}){8})"
        patten = re.compile(pat)
        rmt_mem = dict(patten.findall(origin_data))
        data_valid = {}
        for i, rm in rmt_mem.items():
            row_data = list(map(lambda x: int(x, 16), rm.split()))
            if sum(row_data):  # read data not 0
                data_valid[i] = row_data
        for k, v in rmt_mem.items():
            next_row = hex(int(k, 16) + 0x10)[2:]
            if (int(k, 16) >> 4) % 2 != 0 and data_valid.get(next_row):
                self.rmt_mem_dic[k] = data_valid[k] + data_valid[next_row]
        return self.rmt_mem_dic

    def read_rmt_serial(self):
        pattern_rmt = r'(N\d.C\d.D\d.R\d):((?:\s+-*\d\d){14})'
        x = re.compile(pattern_rmt)
        rmt_result = x.findall(self.serial_log)
        if not rmt_result:
            logging.info(f"RMT data not found in serial log: {self.serial_log}")
            return
        rmt_result = list(map(list, rmt_result))
        for res in rmt_result:
            rank = res[0]
            data = list(map(int, res[1].split()))
            self.rmt_serial_dic[rank] = data
        return self.rmt_serial_dic

    def addr_to_rank(self, addr: int):
        step_size = 0x20  # per rank mem addr interval
        offset = addr - self.base_addr
        scalar = int(offset / step_size)
        # icx platform feature, double check this field in different platform
        rank_max = 4
        dimm_max = 2
        ch_max = 8
        node_max = 2
        # location parser
        rank_n = scalar % rank_max
        dimm_n = int(scalar / rank_max) % dimm_max
        ch_n = int(scalar / dimm_max / rank_max) % ch_max
        node_n = int(scalar / ch_max / dimm_max / rank_max)
        if node_n >= node_max:
            return
        return rf"N{node_n}.C{ch_n}.D{dimm_n}.R{rank_n}"

    def compare_data(self):
        result = True
        signal_list = SIGNALS.split()
        for mem_addr, data_mem in self.rmt_mem_dic.items():
            rank_str = self.addr_to_rank(int(mem_addr, 16))
            data_serial = self.rmt_serial_dic.get(rank_str)
            if not data_serial:  # filter out empty rank data
                continue
            for index, value_ser in enumerate(data_serial):
                value_mem = data_mem[index]
                if abs(value_ser) != abs(value_mem):  # verify every signal rmt data
                    logging.info(f"[{rank_str}] {signal_list[index]:7}| serial [{value_ser:3}] | t128 [{value_mem:3}] fail")
                    result = result & False
                    continue
                logging.info(f"[{rank_str}] {signal_list[index]:7}| serial [{value_ser:3}] | t128 [{value_mem:3}] pass")
        return result

    def run_test(self):
        try:
            # data init
            assert self.get_base_addr(), "get_base_addr() error"
            assert self.read_rmt_mem(self.ssh_os, self.base_addr), "read_rmt_mem() error"
            assert self.read_rmt_serial(), "read_rmt_serial() error"
            # debug print
            logging.debug(f"base_addr: {hex(self.base_addr)}")
            logging.debug(f"rmt_mem_dic: {self.rmt_mem_dic}")
            logging.debug(f"rmt_serial_dic: {self.rmt_serial_dic}")
            # compare data
            assert self.compare_data(), "compare data failed"
            return True
        except AssertionError as e:
            logging.info(e)


# Function to test a single type
def smbios_test(ssh, type, sut):
    tcid = str(400 + type)
    tc = (tcid, '[TC{0}]SMBIOS Type {1}'.format(tcid, type), '检查SMBIOS Type {0}信息'.format(type))
    result = ReportGen.LogHeaderResult(tc)
    expted_log = 'TCE\\Tools\\Smbios\\{0}\\type{1}.txt'.format(sut, type)
    if not P.dump_and_verify(ssh, 'dmidecode -t {0}'.format(type), expted_log):
        result.log_fail()
        return
    result.log_pass()
    return True


# Test all types defined in list TYPES
def smbios_test_all():
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 60):
        logging.info("Skip SMBIOS test.")
        return
    for typeid in TYPES:
        smbios_test(Sut.OS_SSH, typeid, SutConfig.Env.SUT_CONFIG)


# 打开装备模式并开启RMT， 重启对比Smbios128和串口RMT数据是否匹配
# Precondition: Linux配置好 unitool和rw工具, os ssh可访问
# OnStart: 进入Linux系统
# OnComplete: clearCMOS后正常启动
def smbios_type128():
    tc = ('528', '[TC528]Testcase_MemMargin_002', '装备模式下内存margin测试, 检查Smbios Type128信息')
    result = ReportGen.LogHeaderResult(tc)
    logging.info("Change setup option to enable RMT")
    try:
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 5):  # avoid reboot if boot in os
            assert BmcLib.force_reset()
            assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config(BiosCfg.MFG_RMT), "Change setup by unitool failed."
        logging.info("Reboot SUT to Linux")
        assert BmcLib.force_reset()
        ser_rmt_data = SerialLib.cut_log(Sut.BIOS_COM, "START_BSSA_RMT", "Lane Margin", duration=15, timeout=600)
        assert ser_rmt_data, "Invalid RMT data"
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        type128data = SshLib.execute_command(Sut.OS_SSH, "dmidecode -t 128")
        assert type128data, "Unable to read type128 data"
        logging.debug(type128data)
        test = Type128Test(type128data, ser_rmt_data, Sut.OS_SSH)
        assert test.run_test(), "SMBIOS Type128 test failed"
        BmcLib.clear_cmos()
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        BmcLib.clear_cmos()
        result.log_fail()
