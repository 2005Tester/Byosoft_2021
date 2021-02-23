# -*- encoding=utf8 -*-

__author__ = 'arthur'

import logging
import os
from ICX2P.BaseLib import SshLib
from Report import ReportGen
from Common.LogAnalyzer import LogAnalyzer
from ICX2P import SutConfig


# dmidecode cmd list
cmd = ['dmidecode -t 0','dmidecode -t 1','dmidecode -t 2','dmidecode -t 3','dmidecode -t 4',
       'dmidecode -t 7','dmidecode -t 9','dmidecode -t 13','dmidecode -t 16','dmidecode -t 17',
       'dmidecode -t 19','dmidecode -t 32','dmidecode -t 38','dmidecode -t 39','dmidecode -t 41',
       'dmidecode -t 127','dmidecode -t 128']


# LogAnalyzer
P = LogAnalyzer(SutConfig.LOG_DIR)


# All smbios test cases,
def smbiosTest(serial, ssh):
    # cmd
    tc = ('042', 'SMBIOS-test', 'BIOS正确填写SMBIOS Type信息')
    result = ReportGen.LogHeaderResult(tc, serial)
    # the first data as original smbios table
    # if ssh.login():
    #     logging.info('Done, modify it before test on different platform')
    #     icx2pAPI.dump_smbios(ssh)
    for i in cmd:  # cmd is a list for test the related smbios cases,
        SshLib.dump_info(ssh, i)
        smbios = os.path.join(os.path.dirname(__file__),'Tools')
        if P.check_smbios(SutConfig.LOG_DIR, smbios):
            logging.info('Pass:{0}'.format(i))
        else:
            logging.info('Fail:{0}'.format(i))
            continue
    with open(os.path.join(SutConfig.LOG_DIR, 'test.log'), 'r') as f:
        for line in f.readlines():
            if 'Fail:' in line:
                result.log_fail()
                return False
    result.log_pass()
    return True


# origin data, generate the table,
def smbiosGen(ssh):
    # the first data as original smbios table,
    if ssh.login():
        logging.info('Done, modify it before test on different platform')
        return SshLib.dump_info(ssh,'dmidecode','dmidecode')
