# -*- encoding=utf8 -*-
import time
import datetime
import re
import updatebios
import os
from pathlib import Path
import shutil
import ctypes

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
 
FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01  # text color contains blue.
FOREGROUND_GREEN = 0x02  # text color contains green.
FOREGROUND_RED = 0x04  # text color contains red.
FOREGROUND_INTENSITY = 0x08  # text color is intensified.
 
BACKGROUND_BLUE = 0x10  # background color contains blue.
BACKGROUND_GREEN = 0x20  # background color contains green.
BACKGROUND_RED = 0x40  # background color contains red.
BACKGROUND_INTENSITY = 0x80  # background color is intensified.


STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

class PrintColor:
    ''''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    for information on Windows APIs.'''
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
 
    def set_cmd_color(self, color, handle=std_out_handle):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool
 
    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
 
    def print_red_text(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
 
    def print_green_text(self, print_text):
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
 
    def print_blue_text(self, print_text):
        self.set_cmd_color(FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
 
    def print_red_text_with_blue_bg(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_BLUE | BACKGROUND_INTENSITY)
        print(print_text)
        self.reset_color()


def call_cmd(cmd):
    res = os.popen(cmd)
    print(cmd + '\n'+ res.read()) 

def get_test_image(path):
    if os.path.exists(path):
        versions = os.listdir(path)
        versions.sort(reverse=True)
        latest_version = versions[1]
        print("Latest Version is: %s" % (latest_version))
        if os.path.exists(latest_version + ".tmp"):
            print("%s has been tested" %(latest_version))
            return STATUS_SKIP      
    else:
        print("BIOS image directroy can't be accessed, please check VPN conection. ")
        return STATUS_FAIL

    current_image_dir = os.path.join(path,latest_version)
    p = Path(current_image_dir)   # remote image dir of current version
    test_dir = os.getcwd()
    dst = os.path.join(test_dir,'bios\RP001.bin')
    rp001_image = []
    for b in p.rglob('HY5*.bin'):
        rp001_image.append(b)
    if not rp001_image:
        print("Image for %s not found, please check whether build is finished." %(latest_version))
        return STATUS_FAIL
    else:
        print("BIOS image for test: %s" %(rp001_image[0])) 
        print("Copying bios image to test directory...")
        shutil.copyfile(rp001_image[0],dst)
        if os.path.exists(dst):
            os.system("echo >" + latest_version + ".tmp")
            return STATUS_PASS
        else:
            print("Failed to copy BIOS image.")
            return STATUS_FAIL

# cleanup test binary and log
def clean_up():
    pass

def run_airtest(testcase,device,log_dir):
    print(testcase)

def create_log_dir():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    test_dir = os.getcwd()
    log_dir = os.path.join(test_dir,'log\\'+ str(timestamp))
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        return(log_dir)
    except:
        print("Failed to create log directory.")
    
 
