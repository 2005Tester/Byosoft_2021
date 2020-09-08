# -*- encoding=utf8 -*-
import logging.config
from Common import ssh
from Common import SutSerial
from Common import LogConfig
from HY5 import Hy5Config
from HY5 import Hy5TcLib
from HY5 import updatebios

if __name__ == "__main__":
    # Init log setting
    log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
    ssh = ssh.SshConnection()

    for i in range(100):
        updatebios.update_bios_ci(ser)
        Hy5TcLib.boot_manager(ser, ssh)
        Hy5TcLib.sp_boot(ser, ssh)
        Hy5TcLib.dc_cycling(ssh, ser, 5)

#    updatebios.update_bios_ci()
#    Hy5TcLib.dc_cycling(ssh, ser, 500)
#    Hy5TcLib.sp_boot(ser, ssh)
#    Hy5TcLib.boot_manager(ser, ssh)
#    testcase(key_f6)
