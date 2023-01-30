from SPR4P.Config import *
from SPR4P.BaseLib import *


####################################
# SMBios Test Case
# TC 400-528
####################################


# Test scope, smbios tables to be tested
TYPES = [0, 1, 2, 3, 4, 7, 9, 13, 16, 17, 19, 38, 39, 41, 127]


def smbios_template_refresh(type_id):
    sut = "".join(re.findall("(Sut\d+)", var.get("SutCfg")))
    template = PlatMisc.root_path()/f"Resource/Smbios/{sut}/type{type_id}.txt"
    bios_ver = PlatMisc.match_config_version().BiosVer
    bios_date = PlatMisc.match_config_version().BiosDate
    refresh_point = {
        0: {"Version: .+": f"Version: {bios_ver}",
            "Release Date: .+": f"Release Date: {bios_date}"},
        19: {"Ending Address: .+": f"Ending Address: 0x{hex(SutConfig.Sys.MEM_SIZE * 2 ** 30 - 1)[2:].upper():>011}",
             "Range Size: .+": f"Range Size: {SutConfig.Sys.MEM_SIZE} GB"},
        }
    if type_id in refresh_point:
        for _pattern, _replace in refresh_point[type_id].items():
            MiscLib.file_str_replace(template, _pattern, _replace)


# Function to test a single type
def smbios_test(ssh, type_n):
    tcid = str(400 + type_n)
    tc = (tcid, '[TC{0}]SMBIOS Type {1}'.format(tcid, type_n), '检查SMBIOS Type {0}信息'.format(type_n))
    result = ReportGen.LogHeaderResult(tc)
    if not PlatMisc.smbios_dump_compare(ssh, type_n):
        result.log_fail()
        return
    result.log_pass()
    return True


# Test all types defined in list TYPES
def smbios_test_all():
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 10):
        if not SetUpLib.boot_to_default_os():
            logging.info("Skip SMBIOS test.")
            return
    for typeid in TYPES:
        smbios_template_refresh(typeid)
        smbios_test(Sut.OS_SSH, typeid)


class _Type128Test:
    def __init__(self, data_t128, data_ser, ssh_os):
        self.type128data = data_t128
        self.ssh_os = ssh_os
        self.base_addr = None
        self.rmt_t128_dic = {}
        self.rmt_serial_dic = {}
        self.serial_log = data_ser
        self.signals = "RxDqs- RxDqs+ RxV- RxV+ TxDq- TxDq+ TxV- TxV+ Ca- Ca+ CaV- CaV+ Cs- Cs+ DcaDfeV- DcaDfeV+"
        # 系统/平台配置
        self.nodes = SutConfig.Sys.CPU_CNT   # 实际安装的CPU数量
        self.channels = 8                       # 平台支持的最大Channel数量
        self.dimms = 2                          # 平台支持的最大DIMM Slot数量
        self.sub_chs = 2                        # 平台支持的最大Sub Channel数量
        self.ranks = 2                          # 平台支持的最大Rank数量

    def get_base_addr(self) -> int:
        """OS下通过RW读取SMBios Type128的数据，获取基地址"""
        patten = r"80(?:\s[0-9A-F]{2}){15}"
        x = re.compile(patten)
        res = x.findall(self.type128data)
        if not len(res) == 1:
            logging.info("Type 128 data doesn't appear to be correct")
            return 0
        address_lst = res[0].split()[4:12]
        address_lst.reverse()
        if not len(address_lst) == 8:
            logging.info("Address should be 64it")
            return 0
        base_addr_str = "".join(address_lst)
        self.base_addr = int(base_addr_str, 16) + 0x10
        logging.info(f"SMBios Type128 base address:{hex(self.base_addr)}")
        return self.base_addr

    def read_rmt_t128(self, ssh_os, base, size=0x2000) -> dict:
        """OS下通过RW读取基地址，获取RMT的测试数据并解析"""
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
                self.rmt_t128_dic[k] = data_valid[k] + data_valid[next_row]
        return self.rmt_t128_dic

    def read_rmt_serial(self) -> dict:
        """从串口中读取RMT数据并解析"""
        pattern_rmt = r'(N\d.C\d.D\d.SC\d.R\d):((?:\s+-*[\d*]+){14})'
        rmt_result = re.findall(pattern_rmt, self.serial_log)
        if not rmt_result:
            logging.info(f"RMT data not found in serial log: {self.serial_log}")
            return self.rmt_serial_dic
        rmt_result = list(map(list, rmt_result))
        for res in rmt_result:
            rank = res[0]
            data = list(map(lambda x: 255 if x == "*" else int(x), res[1].split()))
            self.rmt_serial_dic[rank] = data
        return self.rmt_serial_dic

    def addr_to_rank(self, addr: int) -> str:
        """通过系统地址，转换得到 Nx.Cx.Dx.SCx.Rx,与串口打印的NodeID对齐，用于RMT数据对比"""
        step_size = 0x20  # per rank mem address interval
        offset = addr - self.base_addr
        scalar = int(offset / step_size)
        nodes, channels, dimms, ranks, sub_chs = self.nodes, self.channels, self.dimms, self.ranks, self.sub_chs
        # 物理位置解析
        node_n = int(scalar / (channels * dimms * ranks * sub_chs))
        ch_n = int(scalar / (dimms * ranks * sub_chs)) % channels
        dimm_n = int(scalar / (sub_chs * ranks)) % dimms
        rank_n = int(scalar / sub_chs) % ranks
        sub_ch_n = scalar % sub_chs
        if node_n >= self.nodes:
            return ""
        return f"N{node_n}.C{ch_n}.D{dimm_n}.SC{sub_ch_n}.R{rank_n}"

    def compare_data(self) -> bool:
        """比较OS下读到的RMT数据和串口打印的RMT数据是否一致"""
        fails = 0
        signal_list = self.signals.split()
        for mem_addr, data_mem in self.rmt_t128_dic.items():
            rank_str = self.addr_to_rank(int(mem_addr, 16))
            data_serial = self.rmt_serial_dic.get(rank_str)
            if not data_serial:  # filter out empty rank data
                continue
            for index, value_ser in enumerate(data_serial):
                value_mem = data_mem[index]
                if abs(value_ser) != abs(value_mem):  # verify every signal rmt data
                    logging.info(f"[{rank_str}] {signal_list[index]:8}| serial [{value_ser:3}] | t128 [{value_mem:3}] fail")
                    fails += 1
                    continue
                logging.info(f"[{rank_str}] {signal_list[index]:8}| serial [{value_ser:3}] | t128 [{value_mem:3}] pass")
        return fails == 0

    def run_test(self):
        try:
            assert self.get_base_addr(), "get_base_addr() error"
            assert self.read_rmt_t128(self.ssh_os, self.base_addr), "read_rmt_mem() error"
            assert self.read_rmt_serial(), "read_rmt_serial() error"
            assert self.compare_data(), "compare data failed"
            return True
        except Exception as e:
            logging.info(e)
            logging.info(f"base_addr: {hex(self.base_addr)}")
            logging.info(f"rmt_t128: {self.rmt_t128_dic}")
            logging.info(f"rmt_serial: {self.rmt_serial_dic}")


# 打开装备模式并开启RMT， 重启对比Smbios128和串口RMT数据是否匹配
# Precondition: Linux配置好 unitool和rw工具, os ssh可访问
# OnStart: 进入Linux系统
# OnComplete: clearCMOS后正常启动
@core.test_case(('528', '[TC528]Testcase_MemMargin_002/[TC2618] Testcase_EquipmentTools_029',
                 '装备模式下内存margin测试 | SMBios Type128 测试'))
def smbios_type128():
    """
    Name:       装备模式下内存margin测试
    Condition:  1、开启串口全打印；
                2、升级装备版本；
                3、装备工具已上传OS。
    Steps:      1、启动进OS，使能装备标志位：./uniMem -w EquipmentModeFlag:1；
                2、打开Margin测试相关选项：
                ./uniCfg -w EnableRMT:1；
                3、重启进OS，执行dmidecode -t 128，检查是否记录Margin测试初始地址，有结果A；
                4、使用rw工具读取初始地址位置内容，获取Margin测试结果；
                检查记录结果跟串口打印Margin结果是否一致，有结果B。
    Result:     A：Type128记录初始地址；
                B：Margin测试正常，Margin测试结果保持一致。
    Remark:     1、RMT菜单不联动打印级别（总开关和MRC都不做），如果要看详细打印，需要手工设置（工具或菜单）打印级别。
    """
    try:
        cpu_with_dimm = {dimm[0] for dimm in Sys.DIMM_POP}
        current_bios = BmcLib.get_fw_version().BIOS
        if not current_bios.startswith('1'):  # equip version type: 1.xx.xx
            bios_img = Update.get_test_image("master", build_type="equip")
            assert Update.flash_bios_bin_and_init(bios_img)
        assert SetUpLib.boot_to_default_os()
        logging.info("Change setup option to enable RMT")
        assert Sut.UNITOOL.set_config(BiosCfg.MFG_RMT), "Change setup by unitool failed."
        logging.info("Reboot SUT to Linux")
        assert BmcLib.force_reset()
        ser_rmt_list = []
        for cpu in cpu_with_dimm:
            rmt_per_cpu = SerialLib.cut_log(Sut.BIOS_COM, Msg.RMT_START, Msg.RMT_END, 15, timeout=SutConfig.Env.BOOT_RMT)
            assert rmt_per_cpu, f"Fail to get RMT data for cpu{cpu}"
            ser_rmt_list.append(rmt_per_cpu)
        assert ser_rmt_list, f"No RMT data found in serial log after wait {SutConfig.Env.BOOT_RMT}s"
        ser_rmt_data = "".join(ser_rmt_list)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_RMT)
        type128data = SshLib.execute_command(Sut.OS_SSH, "dmidecode -t 128")
        assert type128data, "Unable to read type128 data"
        logging.debug(type128data)
        test = _Type128Test(type128data, ser_rmt_data, Sut.OS_SSH)
        assert test.run_test(), "SMBIOS Type128 test failed"
        return core.Status.Pass
    except Exception as e:
        logging.info(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
