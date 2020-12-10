# -*- encoding=utf8 -*-

__author__ = 'arthur'

import logging
import os

from Common import Misc
from Common.LogAnalyzer import LogAnalyzer
from HY5 import Hy5TcLib, Hy5Config

# dmidecode cmd list
cmd = ['dmidecode -t 1', 'dmidecode -t 2', 'dmidecode -t 3', 'dmidecode -t 4', 'dmidecode -t 7', 'dmidecode -t 9',
       'dmidecode -t 13', 'dmidecode -t 16', 'dmidecode -t 17', 'dmidecode -t 19', 'dmidecode -t 41']


# LogAnalyzer
P = LogAnalyzer(Hy5Config.LOG_DIR)


# All smbios test cases,
def smbiosTest(serial, ssh):
    # cmd
    tc = ('042', 'BIOS正确填写SMBIOS Type信息', 'SMBIOS需求')
    result = Misc.LogHeaderResult(tc, serial)
    for i in cmd:  # cmd is a list for test the related smbios cases,
        Hy5TcLib.dump_smbios(ssh, i)
        if P.check_smbios(Hy5Config.LOG_DIR, Hy5Config.SMBIOS_DIR):
            logging.info('Pass:{0}'.format(i))
        else:
            logging.info('Fail:{0}'.format(i))
            continue
    with open(os.path.join(Hy5Config.LOG_DIR, 'test.log'), 'r') as f:
        for line in f.readlines():
            if 'Fail:' in line:
                result.log_fail()
                return False

    result.log_pass()
    return True


# origin data, generate the table,
def smbiosGen(ssh):
    # the first data as original smbios table,
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info('Done, modify it before test on different platform')
        return ssh.dump_info('dmidecode', Hy5Config.SMBIOS_DIR)