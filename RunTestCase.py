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
    Hy5TcLib.me_configuration(ser, sshins)


def test_run():
#    updatebios.update_bios_ci(ser)
    Hy5TcLib.sp_boot(ser, sshins)
    if Hy5TcLib.boot_ubuntu(ser, sshins):
        Hy5TcLib.dump_smbios(sshins)
        Hy5TcLib.lspci(sshins)
        Hy5TcLib.dmesg(sshins)
    Hy5TcLib.boot_windows(ser, sshins)
    Hy5TcLib.check_me_state(ser, sshins)


if __name__ == "__main__":
    while True:
        test_run()

