# -*- encoding=utf8 -*-

import datetime
import os
from pathlib import Path
import shutil
from Common import PrintColor
from HY5 import daily
import logging

SKIP_TEST = 2
VER_TESTED = []

prt = PrintColor.PrintColor()

TEST_DIR = "C:\\daily"

TC0 = {'id': 0, 'name': 'Reset Default by F9',      'script': "\"C:\\autotest\\testcases\\ResetDefault\\ResetDefault.py\"",               'exec': 1}
TC1 = {'id': 1, 'name': 'Boot to Ubuntu 18.04',     'script': "\"C:\\autotest\\testcases\\BootUbuntu\\BootUbuntu.py\"",                   'exec': 1}
TC2 = {'id': 2, 'name': 'boot_to_shell',            'script': "\"C:\\autotest\\testcases\\BootoShell\\BootoShell.py\"",                   'exec': 1}
TC3 = {'id': 3, 'name': 'Boot to Setup',            'script': "\"C:\\autotest\\testcases\\BootToSetup\\BootToSetup.py\"",                 'exec': 1}
TC4 = {'id': 4, 'name': 'Boot to Boot Manager',     'script': "\"C:\\autotest\\testcases\\BootToBootManager\\BootToBootManager.py\"",     'exec': 1}
TC5 = {'id': 5, 'name': 'SP Boot by F6',            'script': "\"C:\\autotest\\testcases\\SpBoot\\SpBoot.py\"",                           'exec': 1}
TC6 = {'id': 6, 'name': 'Boot to Windows Server 2019', 'script': "\"C:\\autotest\\testcases\\BootWindows2019\\BootWindows2019.py\"",         'exec': 1}
TC7 = {'id': 7, 'name': 'Legacy Boot',              'script': "\"C:\\autotest\\testcases\\LegacyBoot\\LegacyBoot.py\"",                   'exec': 1}
TC8 = {'id': 8, 'name': 'hpm_downgrade',            'script': "C:\\autotest\\testcases\\HpmDowngrade\\HpmDowngrade.py",                   'exec': 1}

TEST_SCOPE = [TC0, TC1, TC3, TC4, TC5, TC6, TC7]

RESULT_TEMPLATE = {"testPass": 1,
                   "testResult": [
                    {
                       "className": "Reset Default", "methodName": "TC0", "description": "Reset BIOS default by F9", "spendTime": "0s", "status": "", "log": []
                    },
	                {
                       "className":"Boot to Ubuntu","methodName":"TC1","description":"Boot to Ubuntu 18.0 LTS Desktop","spendTime":"0s","status":"","log":[]
                    },
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

TestRunInfo = RESULT_TEMPLATE

def get_test_image(path):
    bios_dir = os.path.join(daily.TEST_DIR, 'bios')
    if not os.path.exists(bios_dir):
        os.mkdir(bios_dir)
    if os.path.exists(path):
        versions = os.listdir(path)
        versions.sort(reverse=True)
        latest_version = versions[1]
        logging.info("Latest Version is: %s" % (latest_version))
        if latest_version in VER_TESTED:
            print("%s has been tested" %(latest_version))
            return SKIP_TEST      
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
            return True
        else:
            logging.error("Failed to copy BIOS image.")
            return




def create_log_dir():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    TestRunInfo['beginTime'] = timestamp
    log_dir = os.path.join(daily.TEST_DIR, 'log\\' + str(timestamp))
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        return log_dir
    except Exception as e:
        logging.error("Failed to create log directory.")
