# -*- encoding=utf8 -*-
import random
import sys
import re
import logging.config
from Common import SutSsh
from Common import ssh
from Common import SutSerial
from Common import LogConfig
from RedFish import config
import configparser
from HY5 import daily
from HY5 import updatebios
import Hy5Config

ser = SutSerial.SutControl("com3", 115200, 0.5)

ssh = ssh.SshConnection()

key_del = [chr(0x7F)]
key_f6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
key_f11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
key_f12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]


def Hotkey():
    ser.hotkey_F6()
    """
    sutssh.rebootsut()   
    i=random.randint(1,2)
    if i == 3:
        ser.hotkey_F11() 
    if i == 2:
        ser.hotkey_F6()
    if i == 1:
        ser.hotkey_del()
    """


def testcase(key):

    print("Receiving data from SUT...")
    while True:
        try:
            if ser.session.in_waiting:
                data = ser.session.read(256).decode("utf-8")
                with open('serial.log', 'a') as f:
                    f.write(data)
                if re.search("Press Del go to Setup Utility", data):
                    for char in key:
                        ser.send_data(char)
                    print("Hot Key sent")
                if re.search("Press F2", data):
                    ser.send_data("Admin@9000")
                    ser.send_data(chr(0x0D))  # Send Enter
                    ser.send_data(chr(0x0D))  # Send Enter
                    print("Send password...")
                if re.search("BIOS boot completed.", data):
                    print("BIOS Boot Successful.")
                    SutSsh.rebootsut()
                    return
        except Exception as e:
            print(e)
            print("Please check whether COM port is in use.")
            break


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
    logging.info("Rebooting sut")
    SutSsh.rebootsut()
    logging.info("Reboot sut done")

    """
    if not daily.get_test_image('\\\\172.16.0.73\\HY5_Binary'):
        return
    logging.info("Get test image")
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
    run_ssh_cmds(["dmidecode", "lspci", "dmesg"]) 
    SutSsh.rebootsut()
    ret = ser.hotkey_F11()
    SutSsh.rebootsut()
    logging.info("Test Hotkey F6")
    ret = ser.hotkey_F6()
    """


def run_ssh_cmds(cmd):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        ssh.execute_command(cmd, Hy5Config.LOG_DIR)
        ssh.close_session()

def run_interact_cmds(cmds, strs):
    if ssh.login(Hy5Config.OS_IP, 'byosoft', 'byo@123'):
        ssh.interaction(cmds, strs)
        ssh.close_session()


if __name__ == "__main__":
    # Init log setting
    log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    """
    commands = ["sudo su\n", "byo@123\n"]
    strs = ["password", "root"]
    while True:
        run_interact_cmds(commands, strs)
    """

#    ssh.close_session()

    daily_test()

"""
    for i in range(2):
        print("Test count: %d" % i)
        try:
            testcase(key_f6)
        except Exception as e:
            print(e)
"""
