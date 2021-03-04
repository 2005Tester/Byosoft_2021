# -*- encoding=utf8 -*-
import os
from os.path import dirname
from Report import ReportGen
from Common.LogAnalyzer import LogAnalyzer
from ICX2P import SutConfig


# Test case ID: 400-440, 527 reserved
##########################################
####        SMBIOS Test Cases        #####    
##########################################

# Test scope, smbios tables to be tested
TYPES = [0, 1, 2, 3, 4, 7, 9, 13, 16, 17, 19, 38, 39, 41, 127]

# LogAnalyzer
P = LogAnalyzer(SutConfig.LOG_DIR)


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

