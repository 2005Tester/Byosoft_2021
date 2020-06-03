# -*- encoding=utf8 -*-
import time
import os
import subprocess
import shutil
import json
import common
import updatebios
import report
from sys import argv

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2


BINARY_DIR='\\\\172.16.0.73\\HY5_Binary'


# define parametres for airtest
device = "\"Windows:///328182\""
TC0 = {'id': 0, 'name':'boot_ubuntu',     'script': "\"C:\\autotest\\testcases\\BootUbuntu.air\"",         'exec':1}
TC1 = {'id': 1, 'name':'boot_to_shell',   'script': "\"C:\\autotest\\testcases\\BootoShell.air\"",         'exec':1}
TC2 = {'id': 2, 'name':'boot_to_setup',   'script': "\"C:\\autotest\\testcases\\BootToSetup.air\"",        'exec':1}
TC3 = {'id': 3, 'name':'boot_to_bm',      'script': "\"C:\\autotest\\testcases\\BootToBootManager.air\"",  'exec':1}
TC4 = {'id': 4, 'name':'sp_boot',         'script': "\"C:\\autotest\\testcases\\SpBoot.air\"",             'exec':1}
TC5 = {'id': 5, 'name':'boot_to_win2019', 'script': "\"C:\\autotest\\testcases\\BootWindows2019.air\"",    'exec':1}


def update_bios():
    if argv[1] == "RUNONCE":
        status == STATUS_PASS #force get_test_image() success to test local image
    else:
        status = common.get_test_image(BINARY_DIR)
        if status == STATUS_PASS:
            if not updatebios.upload_bios('bios\RP001.bin'):
                return STATUS_FAIL

            if not updatebios.program_flash():
                return STATUS_FAIL
       
            if not updatebios.poweron_sut():
                return STATUS_FAIL

            return status

        elif status == STATUS_SKIP:
            return status

"""        
        status = common.get_test_image(BINARY_DIR)
    
    if status == STATUS_PASS:
        if updatebios.upload_bios('bios\RP001.bin'):
            if updatebios.program_flash():
                if updatebios.poweron_sut():
                      return STATUS_PASS
                else:
                    return STATUS_FAIL
            else:
                return STATUS_FAIL
        else:
            return STATUS_FAIL
    elif status == STATUS_SKIP:
        return STATUS_SKIP
   
    else:
        return STATUS_FAIL                        
"""
def run_airtest(script, device, log, overall):
    
    cmd = "airtest run " + script + " --device " + device + " --log " + log
    # command to run test by airtest 
    with open(overall, 'w') as f:
        # run test and write test log to overall log file.
        subprocess.call(cmd, stderr=f, stdout=f)
    
def loop_test(tc_list):
    while True:
        status = update_bios()
        if status == STATUS_PASS:
            os.system("del /f /q tmp\*.*")
            log_dir = common.create_log_dir()       
            for tc in tc_list: 
                if tc['exec'] == 1:
                    overall_log = 'tmp\\' + tc['name']+'.txt'
                    log = "\"" + log_dir + "\\" + tc['name'] + "\""
                    print(log)
                    run_airtest(tc['script'], device, log, overall_log)
                    report.update_result(common.TestRunInfo, tc["id"], overall_log)
                    print("-"*50)  
            report.update_overview(common.TestRunInfo)
            report.gen_html('report\\template', 'tmp\\report.html')
            os.system('copy tmp\*.* ' + log_dir)
            print("Tested Version: ",common.VER_TESTED)
        else:
            print("Will check update in 30 minutes")
            time.sleep(1800)


if __name__ == '__main__':
    
  
    daily_testcases = [TC0, TC1, TC2, TC3, TC4, TC5]
    loop_test(daily_testcases)
  


#c:\autotest>airtest report c:\autotest\testcases\BootUbuntu.air --log_root log\2020-05-09_16-35-09 --outfile log\2020-05-09_16-35-09\report.html --static_root ..\report --lang en --plugin airtest_selenium.report poco.utils.airtest.report