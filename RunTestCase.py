# -*- encoding=utf8 -*-
import logging.config
import re
from pathlib import Path
import time
from Common import ssh
from Common import SutSerial
from Common import LogConfig
from HY5 import Hy5Config
from HY5 import Hy5TcLib
from HY5 import updatebios
from HY5 import SetUp
from Report.ReportGen import ReportGenerator

# Init log setting
log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)

# init seril
ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
# init ssh
sshins = ssh.SshConnection()


def check_ci_update():
    dir = Hy5Config.BINARY_DIR


def test():
    Hy5TcLib.dump_smbios(sshins)
    Hy5TcLib.lspci(sshins)
    Hy5TcLib.dmesg(sshins)
    Hy5TcLib.cpuinfo(sshins)


def test_run():
    updatebios.update_bios_ci(ser)
    SetUp.reset_default(ser, sshins)
    Hy5TcLib.sp_boot(ser, sshins)
    if Hy5TcLib.boot_ubuntu(ser, sshins):
        Hy5TcLib.dump_smbios(sshins)
        Hy5TcLib.lspci(sshins)
        Hy5TcLib.dmesg(sshins)
        Hy5TcLib.cpuinfo(sshins)
    Hy5TcLib.boot_windows(ser, sshins)
    SetUp.check_me_state(ser, sshins)
    SetUp.enable_full_debug_msg(ser, sshins)
    SetUp.disable_full_debug_msg(ser, sshins)


if __name__ == "__main__":
    report = ReportGenerator("c:\daily\log.txt")
    report.collect_test_result()

"""
if __name__ == "__main__":
    cycle = 1
    while True:
        logging.info("-"*50  + "\n" + " "*45 + "Test Cycle:{0}".format(cycle))
        logging.info("-"*50)
        test_run()
        cycle +=1
"""
