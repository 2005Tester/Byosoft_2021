# -*- encoding=utf8 -*-
import common
import time
import updatebios
import os
import subprocess
import shutil

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

#BINARY_DIR='\\\\192.168.100.143\\HY5_Binary'
BINARY_DIR='\\\\172.16.0.73\\HY5_Binary'
#BINARY_DIR='C:\\HY5V009'

# define parametres passed to airtest

device = "\"Windows:///131604\""
TC0 = {'name':'boot_ubuntu',     'script': "\"C:\\autotest\\testcases\\BootUbuntu.air\"",         'exec':1}
TC1 = {'name':'boot_to_shell',   'script': "\"C:\\autotest\\testcases\\BootoShell.air\"",         'exec':1}
TC2 = {'name':'boot_to_setup',   'script': "\"C:\\autotest\\testcases\\BootToSetup.air\"",        'exec':1}
TC3 = {'name':'boot_to_bm',      'script': "\"C:\\autotest\\testcases\\BootToBootManager.air\"",  'exec':1}
TC4 = {'name':'boot_to_win2019', 'script': "\"C:\\autotest\\testcases\\BootWindows2019.air\"",    'exec':1}


prt = common.PrintColor()

def update_bios():
    status = common.get_test_image(BINARY_DIR)
    if status == STATUS_PASS:
        prt.print_green_text("Check Wheter Image is copied to local HDD: PASS")
        if updatebios.upload_bios():
            prt.print_green_text("Upload bios to iBMC: PASS")
            if updatebios.program_flash():
                prt.print_green_text("Load bios to iBMC: PASS")
                if updatebios.poweron_sut():
                    prt.print_green_text("Power On SUT: PASS")
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

def run_airtest(testcase, device, log):
    
    cmd = "airtest run " + testcase + " --device " + device + " --log " + log
    print(cmd)
    with open('log.txt', 'w') as f:
        subprocess.call(cmd, stdout=f, stderr=f, shell=True)

def loop_test(tc):
    
    while True:
        status = update_bios()
        if status == STATUS_PASS:
            log_dir = common.create_log_dir()
            for tc in testcases: 
                if tc['exec'] == 1:
                    log = "\"" + log_dir + "\\" + tc['name'] + "\""
                    print(log)
                    run_airtest(tc['script'], device, log)
                    print("-"*50)
            shutil.copy('log.txt',log_dir)
        else:
            print("This version hase been tesed, check code update after 60 minutes")
            time.sleep(3600)

def run_latest(tc):
    os.system("del /f /q *.tmp")
    status = update_bios()
    log_dir = common.create_log_dir()
    #status = 1
    if status:
        for tc in testcases: 
            if tc['exec'] == 1:
                log = "\"" + log_dir + "\\" + tc['name'] + "\""
                print(log)
                run_airtest(tc['script'], device, log)
                print("-"*50)
    else:
        print("Daily test didn't run, bios wasn't updated successfully")

if __name__ == '__main__':
    
    testcases = [TC0, TC1, TC2, TC3, TC4]
    loop_test(testcases)
    #run_latest(testcases)




#c:\autotest>airtest report c:\autotest\testcases\BootUbuntu.air --log_root log\2020-05-09_16-35-09 --outfile log\2020-05-09_16-35-09\report.html --static_root ..\report --lang en --plugin airtest_selenium.report poco.utils.airtest.report