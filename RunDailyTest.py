#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import time
import os
import subprocess
from HY5 import updatebios
from Report import GenDailyReport
from sys import argv
from HY5 import daily
from HY5 import Hy5Config
import logging.config
from Common import LogConfig

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2


# define parametres for airtest
device = "\"Windows:///?title_re=iBMC*\""


def update_bios():
    #image_dir = "C:\\daily\\image"
    image_dir = Hy5Config.BINARY_DIR
    image = updatebios.get_test_image(image_dir)
    if image:
        if not updatebios.upload_bios(image):
            return

        if not updatebios.program_flash():
            return
       
        if not updatebios.poweron_sut():
            return
    
        return True


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
            log_dir = daily.create_log_dir()       
            for tc in tc_list: 
                if tc['exec'] == 1:
                    overall_log = 'tmp\\' + tc['name']+'.txt'
                    log = "\"" + log_dir + "\\" + tc['name'] + "\""
                    print(log)
                    run_airtest(tc['script'], device, log, overall_log)
                    GenDailyReport.update_result(daily.TestRunInfo, tc["id"], overall_log)
                    print("-"*50)  
            GenDailyReport.update_overview(daily.TestRunInfo)
            GenDailyReport.gen_html('report\\template', 'tmp\\report.html')
            os.system('copy tmp\*.* ' + log_dir)
            print("Tested Version: ",daily.VER_TESTED)
        else:
            print("Will check update in 30 minutes")
            time.sleep(1800)

def loop_test_py(tc_list):
    while True:
        status = update_bios()
        #status = 1
        if status == STATUS_PASS:
            os.system("del /f /q tmp\*.*")
            log_dir = daily.create_log_dir()       
            for tc in tc_list: 
                if tc['exec'] == 1:
                    overall_log = 'tmp\\' + tc['name']+'.txt'
                    log = "\"" + log_dir + "\\" + tc['name'] + "\""
                    print("Running tets case: %s" % tc['name'])
                    run_airtest_py(tc['script'], device, log, overall_log)
                    GenDailyReport.update_result(daily.TestRunInfo, tc["id"], overall_log)
                    # print("-"*50)  
            GenDailyReport.update_overview(daily.TestRunInfo)
            GenDailyReport.gen_html('report\\template', 'tmp\\report.html')
            os.system('copy tmp\*.* ' + log_dir)
            print("Tested Version: ",daily.VER_TESTED)
        else:
            print("Will check update in 30 minutes")
            time.sleep(1800)


if __name__ == '__main__':
    log_format = LogConfig.gen_config(Hy5Config.LOG_DIR)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    loop_test_py(daily.TEST_SCOPE)
    
  
#    daily_testcases = [TC0, TC1, TC2, TC3, TC4, TC5, TC6]
#    loop_test(daily_testcases)
  


#c:\autotest>airtest report c:\autotest\testcases\BootUbuntu.air --log_root log\2020-05-09_16-35-09 --outfile log\2020-05-09_16-35-09\report.html --static_root ..\report --lang en --plugin airtest_selenium.report poco.utils.airtest.report