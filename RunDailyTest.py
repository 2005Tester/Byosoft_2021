# -*- encoding=utf8 -*-
import time
import os
import subprocess
import shutil
import json
import common
import updatebios
from Report import GenDailyReport
from sys import argv
from HY5 import daily

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2


BINARY_DIR = '\\\\172.16.0.73\\HY5_Binary'


# define parametres for airtest
device = "\"Windows:///?title_re=iBMC*\""


def update_bios():
    status = common.get_test_image(BINARY_DIR)
    if status == STATUS_PASS:
        if not updatebios.upload_bios(daily.TEST_DIR + '\\bios\\RP001.bin'):
            return STATUS_FAIL

        if not updatebios.program_flash2():
            return STATUS_FAIL
       
        if not updatebios.poweron_sut():
            return STATUS_FAIL

        return status

    elif status == STATUS_SKIP:
        return status


def run_airtest(script, device, log, overall):
    
    cmd = "airtest run " + script + " --device " + device + " --log " + log
    # command to run test by airtest 
    with open(overall, 'w') as f:
        # run test and write test log to overall log file.
        subprocess.call(cmd, stderr=f, stdout=f)


def run_airtest_py(script, device, log, overall):
    
    cmd = "python " + script + " --device " + device + " --log " + log
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
                    GenDailyReport.update_result(common.TestRunInfo, tc["id"], overall_log)
                    print("-"*50)  
            GenDailyReport.update_overview(common.TestRunInfo)
            GenDailyReport.gen_html('report\\template', 'tmp\\report.html')
            os.system('copy tmp\*.* ' + log_dir)
            print("Tested Version: ",common.VER_TESTED)
        else:
            print("Will check update in 30 minutes")
            time.sleep(1800)


def loop_test_py(tc_list):
    while True:
        status = update_bios()
        #status = 1
        if status == STATUS_PASS:
            os.system("del /f /q tmp\*.*")
            log_dir = common.create_log_dir()       
            for tc in tc_list: 
                if tc['exec'] == 1:
                    overall_log = 'tmp\\' + tc['name']+'.txt'
                    log = "\"" + log_dir + "\\" + tc['name'] + "\""
                    print("Running tets case: %s" % tc['name'])
                    run_airtest_py(tc['script'], device, log, overall_log)
                    GenDailyReport.update_result(common.TestRunInfo, tc["id"], overall_log)
                    # print("-"*50)  
            GenDailyReport.update_overview(common.TestRunInfo)
            GenDailyReport.gen_html('report\\template', 'tmp\\report.html')
            os.system('copy tmp\*.* ' + log_dir)
            print("Tested Version: ",common.VER_TESTED)
        else:
            print("Will check update in 30 minutes")
            time.sleep(1800)


if __name__ == '__main__':
    loop_test_py(daily.TEST_SCOPE)
    
  
#    daily_testcases = [TC0, TC1, TC2, TC3, TC4, TC5, TC6]
#    loop_test(daily_testcases)
  


#c:\autotest>airtest report c:\autotest\testcases\BootUbuntu.air --log_root log\2020-05-09_16-35-09 --outfile log\2020-05-09_16-35-09\report.html --static_root ..\report --lang en --plugin airtest_selenium.report poco.utils.airtest.report