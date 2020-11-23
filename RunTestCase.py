#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging.config
import re
from pathlib import Path
import time
import os
from sys import argv
from Common import ssh
from Common import SutSerial
from Common import LogConfig
from Common import Misc
from HY5 import Hy5Config
from HY5 import Hy5TcLib
from HY5 import updatebios
from HY5 import SetUp
from Report.ReportGen import ReportGenerator
from Common.LogAnalyzer import LogAnalyzer

# Init log setting
log_dir = Hy5Config.LOG_DIR
log_format = LogConfig.gen_config(log_dir)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)

# init seril
ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
# init ssh
sshins = ssh.SshConnection()

#log_dir = "C:\\daily\\HY5\\2020-09-23_17-50-23"

def check_log():
    log = LogAnalyzer(log_dir)
    tc900 = ('900', 'Check BIOS Log', 'Check whether there are asserts or exception in test')
    res900 = Misc.LogHeaderResult(tc900)
    if log.check_bios_log():
        res900.log_pass()
    else:
        res900.log_fail()

    tc901 = ('901', 'SMBIOS Test', 'Check whether vendor information in SMBIOS is correct')
    res901 = Misc.LogHeaderResult(tc901)
    if log.check_smbios():
        res901.log_pass()
    else:
        res901.log_fail()

    tc902 = ('902', 'Verify Default CPU Core counts', 'Check whether Default CPU Core count is correct.')
    res902 = Misc.LogHeaderResult(tc902)
    if log.check_cpuinfo(18):
        res902.log_pass()
    else:
        res902.log_fail()
    

def gen_report():
    template = Hy5Config.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.collect_test_result()
    report.write_to_html()


def debug_run():
    for i in range(100):
        logging.info("Test count {0}".format(i))
        SetUp.change_cpu_cores(ser, sshins)


def test_run():
    updatebios.update_bios_ci(ser)
    SetUp.reset_default(ser, sshins)
    Hy5TcLib.sp_boot(ser, sshins)
    SetUp.check_me_state(ser, sshins)
    Hy5TcLib.boot_windows(ser, sshins)
    if SetUp.enable_full_debug_msg(ser, sshins):
        SetUp.disable_full_debug_msg(ser, sshins)
    if SetUp.enable_legacy_boot(ser, sshins):
        SetUp.disable_legacy_boot(ser, sshins)
    if Hy5TcLib.boot_ubuntu(ser, sshins):
        Hy5TcLib.dump_smbios(sshins)
        Hy5TcLib.lspci(sshins)
        Hy5TcLib.dmesg(sshins)
        Hy5TcLib.cpuinfo(sshins)
#    SetUp.change_cpu_cores(ser, sshins, 14, 4)
    check_log()
    gen_report()


if __name__ == "__main__":
    if argv[1] == "loop":
        cycle = 1
        while True:
            logging.info("-"*50 + "\n" + " "*45 + "Test Cycle:{0}".format(cycle))
            logging.info("-"*50)
            test_run()
            cycle +=1
    elif argv[1] == "debug":
        debug_run()

    elif argv[1] == "latest":
        test_run()



