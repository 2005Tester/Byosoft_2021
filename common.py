# -*- encoding=utf8 -*-
import time
import datetime
import re
import updatebios
import os
from pathlib import Path
import shutil
import json
from Common import PrintColor
from HY5 import daily

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

VER_TESTED = []

TestRunInfo = daily.RESULT_TEMPLATE


prt = PrintColor.PrintColor()


def get_test_image(path):
    bios_dir = os.path.join(daily.TEST_DIR, 'bios')
    if not os.path.exists(bios_dir):
        os.mkdir(bios_dir)
    if os.path.exists(path):
        versions = os.listdir(path)
        versions.sort(reverse=True)
        latest_version = versions[1]
        print("Latest Version is: %s" % (latest_version))
        if latest_version in VER_TESTED:
            print("%s has been tested" %(latest_version))
            return STATUS_SKIP      
    else:
        print("BIOS image directroy can't be accessed, please check VPN conection. ")
        return STATUS_FAIL

    current_image_dir = os.path.join(path, latest_version)
    p = Path(current_image_dir)   # remote image dir of current version
    dst = os.path.join(bios_dir, 'RP001.bin')
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
            VER_TESTED.append(latest_version)
            prt.print_green_text("Check Wheter Image is copied to local HDD: PASS")
            return STATUS_PASS
        else:
            print("Failed to copy BIOS image.")
            return STATUS_FAIL


def create_log_dir():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    TestRunInfo['beginTime'] = timestamp
    log_dir = os.path.join(daily.TEST_DIR, 'log\\' + str(timestamp))
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        return log_dir
    except Exception as e:
        print("Failed to create log directory.")
