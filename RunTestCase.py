# -*- encoding=utf8 -*-
import random
import sys
import re
from Common import SutSsh
from Common import SutSerial
from RedFish import config


ser = SutSerial.SutControl("com3", 115200, 0.5)

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


if __name__ == "__main__":

    for i in range(2):
        print("Test count: %d" % i)
        try:
            testcase(key_f6)
        except Exception as e:
            print(e)
