# -*- encoding=utf8 -*-
import logging.config
import re
from pathlib import Path
import time
import os
from Common import ssh
from Common import SutSerial
from Common import LogConfig
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

#log_dir = "C:\\daily\\autolog\\2020-09-22_15-23-59"

def check_log():
    log = LogAnalyzer(log_dir)
    logging.info("<TC900><Tittle>Check BIOS Log:Start")
    logging.info("<TC900><Description>Check whether there are asserts or exception in test")
    if log.check_bios_log():
        logging.info("<TC900><Result>Check BIOS Log:Pass")
    else:
        logging.info("<TC900><Result>Check BIOS Log:Fail")

    logging.info("<TC901><Tittle>SMBIOS Test:Start")
    logging.info("<TC901><Description>Check whether vendor information in SMBIOS is correct")
    if log.check_smbios():
        logging.info("<TC901><Result>SMBIOS Test:Pass")
    else:
        logging.info("<TC901><Result>SMBIOS Test:Fail")


def gen_report():
    report = ReportGenerator(os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.collect_test_result()
    report.write_to_html()


def test_run():
    updatebios.update_bios_ci(ser)
    SetUp.reset_default(ser, sshins)
    Hy5TcLib.sp_boot(ser, sshins)
    if Hy5TcLib.boot_ubuntu(ser, sshins):
        Hy5TcLib.dump_smbios(sshins)
        Hy5TcLib.lspci(sshins)
        Hy5TcLib.dmesg(sshins)
        Hy5TcLib.cpuinfo(sshins)
    SetUp.check_me_state(ser, sshins)
    Hy5TcLib.boot_windows(ser, sshins)
    SetUp.enable_full_debug_msg(ser, sshins)
    SetUp.disable_full_debug_msg(ser, sshins)
    check_log()
    gen_report()


if __name__ == "__main__":
#    cycle = 1
#    while True:
#        logging.info("-"*50 + "\n" + " "*45 + "Test Cycle:{0}".format(cycle))
#        logging.info("-"*50)
    test_run()
#    check_log()
#    gen_report()
#        cycle +=1

