# -*- encoding=utf8 -*-
import time
import datetime
import re
import updatebios
import os
from pathlib import Path
import shutil
import json
import printcolor
from HY5 import daily

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

VER_TESTED = []

TestRunInfo = {"testPass":1,
    "testResult":[
        {"className":"Reset Default","methodName":"TC0","description":"Reset BIOS default by F9","spendTime":"0s","status":"","log":[]},
	    {"className":"Boot to Ubuntu","methodName":"TC1","description":"Boot to Ubuntu 18.0 LTS Desktop","spendTime":"0s","status":"","log":[]},
	    {"className":"Boot to UEFI Shell","methodName":"TC2","description":"Test Boot to UEFI Shell","spendTime":"0s","status":"","log":[]},
	    {"className":"Boot to Setup","methodName":"TC3","description":"Boot to setu using hotkey: Del","spendTime":"0s","status":"","log":[]},
	    {"className":"Boot to Boot Manager","methodName":"TC4","description":"Boot to boot manager using hotkey: F11","spendTime":"0s","status":"","log":[]},
	    {"className":"SP Boot","methodName":"TC5","description":"SP Boot using hotkey: F6","spendTime":"0s","status":"","log":[]},
	    {"className":"Boot to UEFI Win 2019 ","methodName":"TC6","description":"Boot to UEFI windows server 2019","spendTime":"0s","status":"","log":[]},
        {"className":"Legacy Boot ","methodName":"TC7","description":"Legacy Boot (No bootable device)","spendTime":"0s","status":"","log":[]},
        {"className":"HPM Downgrade ","methodName":"TC8","description":"Downgrdae to last official release using hpm","spendTime":"0s","status":"","log":[]}
	],
    "testName" :'',
    "testAll"  :'9',
	"testPass" :'',
    "testFail" :'',
    "testSkip" :'',
    "beginTime":'',
    "totalTime":0}


prt = printcolor.PrintColor()


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
