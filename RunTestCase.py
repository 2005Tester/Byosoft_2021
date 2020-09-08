# -*- encoding=utf8 -*-
import logging.config
from Common import ssh
from Common import SutSerial
from Common import LogConfig
from HY5 import Hy5Config
from HY5 import Hy5TcLib
from HY5 import updatebios


def main():
    # Init log setting
    log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    # init seril
    ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
    if not ser:
        return
    # init ssh
    ssh = ssh.SshConnection()

    # Hy5TcLib.dump_smbios(ssh)
    # Hy5TcLib.lspci(ssh)
    # Hy5TcLib.dmesg(ssh)
    Hy5TcLib.boot_ubuntu(ser, ssh)
    # Hy5TcLib.dc_cycling(ssh, ser, 5)


if __name__ == "__main__":
    # Init log setting
    log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    # init seril
    ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
    # init ssh
    ssh = ssh.SshConnection()

    updatebios.update_bios_ci(ser)
    Hy5TcLib.sp_boot(ser, ssh)
    if Hy5TcLib.boot_ubuntu(ser, ssh):
        Hy5TcLib.dump_smbios(ssh)
        Hy5TcLib.lspci(ssh)
        Hy5TcLib.dmesg(ssh)
    Hy5TcLib.boot_windows(ser, ssh)
    
    
    # Hy5TcLib.dc_cycling(ssh, ser, 5)


"""
    for i in range(100):
        ssh.execute_command('dmidecode', Hy5Config.LOG_DIR)
        #updatebios.update_bios_ci(ser)
        Hy5TcLib.boot_manager(ser, ssh)
        Hy5TcLib.sp_boot(ser, ssh)
        Hy5TcLib.dc_cycling(ssh, ser, 5)
"""