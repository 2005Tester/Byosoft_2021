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

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

VER_TESTED = []

TestRunInfo = {"testPass":1,
    "testResult":[
	    {"className":"Boot to Ubuntu","methodName":"TC0","description":"Boot to Ubuntu 18.0 LTS Desktop","spendTime":"0ms","status":"","log":[]},
	    {"className":"Boot to UEFI Shell","methodName":"TC1","description":"Test Boot to UEFI Shell","spendTime":"0ms","status":"","log":[]},
	    {"className":"Boot to Setup","methodName":"TC2","description":"Boot to setu using hotkey: Del","spendTime":"0ms","status":"","log":[]},
	    {"className":"Boot to Boot Manager","methodName":"TC3","description":"Boot to boot manager using hotkey: F11","spendTime":"0ms","status":"","log":[]},
	    {"className":"SP Boot","methodName":"TC4","description":"SP Boot using hotkey: F6","spendTime":"0ms","status":"","log":[]},
	    {"className":"Boot to UEFI Win 2019 ","methodName":"TC5","description":"Boot to UEFI windows server 2019","spendTime":"0ms","status":"","log":[]}
	],
    "testName" :'',
    "testAll"  :'',
	"testPass" :'',
    "testFail" :'',
    "testSkip" :'',
    "beginTime":'',
    "totalTime":''}


prt = printcolor.PrintColor()

def get_test_image(path):
    # Check and download image from automation build
    if os.path.exists(path):
        versions = os.listdir(path)
        versions.sort(reverse=True)
        latest_version = versions[1]
        print("Latest Version is: %s" % (latest_version))
        if latest_version in VER_TESTED:
        #if os.path.exists("tmp\\" + latest_version + ".tmp"):
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
            VER_TESTED.append(latest_version)
            prt.print_green_text("Check Wheter Image is copied to local HDD: PASS")
            return STATUS_PASS
        else:
            print("Failed to copy BIOS image.")
            return STATUS_FAIL

def create_log_dir():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    test_dir = os.getcwd()
    log_dir = os.path.join(test_dir,'log\\'+ str(timestamp))
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        return(log_dir)
    except:
        print("Failed to create log directory.")
    
 
