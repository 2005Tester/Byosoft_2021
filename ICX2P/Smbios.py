# -*- encoding=utf8 -*-
import os
import re
from os.path import dirname
import logging
from Report import ReportGen
from Common.LogAnalyzer import LogAnalyzer
from ICX2P import SutConfig
from ICX2P.SutConfig import BiosCfg, Msg
from ICX2P.BaseLib import PowerLib, SerialLib, SetUpLib, SshLib


# Test case ID: 400-440, 527 reserved
##########################################
#           Smbios Test Cases            #
##########################################

# Test scope, smbios tables to be tested
TYPES = [0, 1, 2, 3, 4, 7, 9, 13, 16, 17, 19, 38, 39, 41, 127]

# LogAnalyzer
P = LogAnalyzer(SutConfig.LOG_DIR)

# signals in rmt result
SIGNALS = ['RxDqsN', 'RxDqsP', 'RxVrefN', 'RxVrefP', 'TxDqN', 'TxDqP', 'TxVrefN', 'TxVrefP',
           'CmdN', 'CmdP', 'CmdVrefN', 'CmdVrefP', 'CtlN', 'CtlP']


class Type128Test:
    def __init__(self, data, ssh):
        self.address = '0x'
        self.rmt_hob = {}
        self.rmt_dbglog = {}
        self.ranks_dbg_log = []
        self.ranks_mem_data = []
        self.type128data = data

        self.mem_addr = self.get_mem_address()

        self.rmt_from_dbglog(os.path.join(SutConfig.LOG_DIR, 'serial.log'))
        self.convert_memdata(self.get_rmtdata(ssh))
        self.get_ranks()

    def get_rmtdata(self, ssh):
        cmd = 'cd rw &&./rw mmr {0}'.format(self.mem_addr)
        rmt_data = SshLib.execute_command(ssh, cmd)
        return rmt_data

    # get address of RMT result hob from smbios type128 table
    def get_mem_address(self):
        # to match type 128 header and data
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
        for n in range(8):
            self.address = self.address + str(address_lst[n])
        self.address = hex(int(self.address, 16))
        logging.info("Memory address:{0}".format(self.address))
        return self.address

    def get_ranks(self):
        if self.rmt_dbglog:
            self.ranks_dbg_log = list(self.rmt_dbglog.keys())
        else:
            logging.info("No rmt data found in serial debug log")
        if self.rmt_hob:
            self.ranks_mem_data = list(self.rmt_hob.keys())[1:len(self.ranks_dbg_log)+1]
        else:
            logging.info("Memory data is not correct.")
        return self.ranks_dbg_log, self.ranks_mem_data

    # convert Hob data
    def rmt_mem_per_signal(self, rankdata, signal):
        newlist = []
        for data in rankdata:
            data = list(data)
            data_persignal = [(str(data[0])+str(data[1])), (str(data[2])+str(data[3]))]
            data_persignal.reverse()
            newlist += data_persignal
        res = int(newlist[signal], 16)
        return res

    # Convert RMT result data to a list
    def convert_memdata(self, raw_memory):
        # To match patten:66cd6000: 9748 352c 0608 0402 6010 66cd 0000 0000
        patten = r"[0-9a-f]{8}:(?:\s[0-9a-f]{4}){8}"
        x = re.compile(patten)
        data = x.findall(raw_memory)
        for line in data:
            addr = re.findall(r"[0-9a-f]{8}", line)[0]
            value = re.findall(r"(?:\s[0-9a-f]{4}){8}", line)[0].split()
            self.rmt_hob[addr] = value
        return self.rmt_hob

    # Read rmt result data from debug log and convert to a dict
    def rmt_from_dbglog(self, file):
        with open(file, 'r') as f:
            data = f.read()
        pattern_rmt = r'N\d.C\d.D\d.R\d:(?:\s+-*\d\d){14}'

        x = re.compile(pattern_rmt)
        rmt_result = x.findall(data)
        for res in rmt_result:
            rank = res.split(':')[0]
            data = res.split(':')[1].split()
            self.rmt_dbglog[rank] = data
        return self.rmt_dbglog

    def rmt_dbglog_per_signal(self, rank, signal):
        result_rank_signal = self.rmt_dbglog[rank][signal]
        return result_rank_signal.replace('-', '')

    def compare_data(self):
        failures = 0
        x = self.rmt_hob
        if not len(self.ranks_dbg_log) == len(self.ranks_mem_data):
            logging.info("Data read from memory and serial debug log doesn't appear to be correct, please double check")
            return
        for rnk in self.ranks_dbg_log:
            logging.info("Testing rank: {0}".format(rnk))
            for sig in SIGNALS:
                log_data = self.rmt_dbglog_per_signal(rnk, SIGNALS.index(sig))
                mem_data = self.rmt_mem_per_signal(x[self.ranks_mem_data[self.ranks_dbg_log.index(rnk)]], SIGNALS.index(sig))
                logging.info("{0}: {1} - {2}".format(sig, log_data, mem_data))
                if str(log_data) == str(mem_data):
                    logging.info("Pass")
                else:
                    logging.info("Fail")
                    failures += 1
            return failures


# Function to test a single type
def smbios_test(ssh, type):
    tcid = str(400+type)
    tc = (tcid, 'SMBIOS Type {0}'.format(type), '检查SMBIOS Type {0}信息'.format(type))
    result = ReportGen.LogHeaderResult(tc)
    expted_log = os.path.join(dirname(__file__), 'Tools\\Smbios\\type{0}.txt'.format(type))
    if not P.dump_and_verify(ssh, 'dmidecode -t {0}'.format(type), expted_log):
        result.log_fail()
        return
    result.log_pass()
    return True


# Test all types defined in list TYPES
def smbios_test_all(ssh):
    for typeid in TYPES:
        smbios_test(ssh, typeid) 


# Check SMBIOS type128 data for manufacture mode
def smbios_type128(serial, ssh, sshbmc, unitool):
    tc = ('528', 'SMBIOS Type 128', '检查SMBIOS Type 128信息')
    result = ReportGen.LogHeaderResult(tc)
    logging.info("Change setup option to enable RMT")
    res = unitool.set_config(BiosCfg.MFG_RMT)
    if not res:
        logging.info("Change setup by unitool failed.")
        result.log_skip()
        return
    logging.info("Reboot SUT to SUSE")
    if not PowerLib.force_reset(sshbmc):
        result.log_fail()
        return
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE, delay=600):
        result.log_fail()
        return
    type128data = SshLib.execute_command(ssh, "dmidecode -t 128")
    logging.info(type128data)
    test = Type128Test(type128data, ssh)
    test.compare_data()
