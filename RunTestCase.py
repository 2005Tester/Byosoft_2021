# -*- encoding=utf8 -*-
import random
import sys
import re
import logging.config
from Common import ssh
from Common import SutSerial
from Common import LogConfig
from RedFish import config
import configparser
from HY5 import daily
from HY5 import updatebios
from HY5 import Hy5Config
from HY5 import Hy5TcLib
import time


key_del = [chr(0x7F)]
key_f6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
key_f11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
key_f12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]


def Hotkey():
    ser.hotkey_f6()
    """
    sutssh.rebootsut()   
    i=random.randint(1,2)
    if i == 3:
        ser.hotkey_f11() 
    if i == 2:
        ser.hotkey_f6()
    if i == 1:
        ser.hotkey_del()
    """


def read_data():

    print("Receiving data from SUT...")
    while True:
        if ser.session.in_waiting:
            data = ser.session.read(256).decode("utf-8")
            print(data)

def check_result(str):
    print("Receiving data from SUT...")
    while True:
        if ser.session.in_waiting:
            data = ser.session.read(256).decode("utf-8")
            #print(data)
            if re.search(str, data):
                    print("BIOS Boot Successful.")
                    return

def daily_test():

    if not updatebios.upload_bios(daily.TEST_DIR + '\\bios\\RP001.bin'):
        return
    logging.info("BIOS uploaded to BMC")
    if not updatebios.program_flash():
        return
    logging.info("BIOS updated")   
    if not updatebios.poweron_sut():
        return
    logging.info("Power on successful")
    check_result("BIOS boot completed.")   
    cmds = ["dmidecode", "lspci", "dmesg"]
    for cmd in cmds:
        run_ssh_cmds(cmd) 
    SutSsh.rebootsut()
    ret = ser.hotkey_f11()
    SutSsh.rebootsut()
    logging.info("Test Hotkey F6")
    ret = ser.hotkey_f6()




if __name__ == "__main__":
    # Init log setting
    log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
    ssh = ssh.SshConnection()

    Hy5TcLib.sp_boot(ser, ssh)
    Hy5TcLib.boot_manager(ser, ssh)
#    testcase(key_f6)
