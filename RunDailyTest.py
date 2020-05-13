# -*- encoding=utf8 -*-
import common
import updatebios
import os
import subprocess


#BINARY_DIR='\\\\192.168.100.143\\HY5_Binary'
BINARY_DIR='\\\\172.16.0.73\\HY5_Binary'


prt = common.PrintColor()

def update_bios():
    if common.get_test_image(BINARY_DIR):
        prt.print_green_text("Check Wheter Image is copied to local HDD: PASS")
        if updatebios.upload_bios():
            prt.print_green_text("Upload bios to iBMC: PASS")
            if updatebios.program_flash():
                prt.print_green_text("Load bios to iBMC: PASS")
                if updatebios.poweron_sut():
                    prt.print_green_text("Power On SUT: PASS")
                    return 1
                else:
                    return
            else:
                return
        else:
            return
    else:
        return                        

def run_airtest(testcase, device, log):
    
    cmd = "airtest run " + testcase + " --device " + device + " --log " + log
    print(cmd)
    subprocess.call(cmd)

if __name__ == '__main__':
    log_dir = common.create_log_dir()
    device = "\"Windows:///66066\""
    TC0 = {'name':'boot_ubuntu',     'script': "\"C:\\autotest\\testcases\\BootUbuntu.air\"",         'exec':1}
    TC1 = {'name':'boot_to_shell',   'script': "\"C:\\autotest\\testcases\\BootoShell.air\"",         'exec':1}
    TC2 = {'name':'boot_to_setup',   'script': "\"C:\\autotest\\testcases\\BootToSetup.air\"",        'exec':1}
    TC3 = {'name':'boot_to_bm',      'script': "\"C:\\autotest\\testcases\\BootToBootManager.air\"",  'exec':1}
    TC4 = {'name':'boot_to_win2019', 'script': "\"C:\\autotest\\testcases\\BootWindows2019.air\"",    'exec':1}

    
    testcases = [TC0, TC1, TC2, TC3, TC4]
    status = update_bios()
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



#c:\autotest>airtest report c:\autotest\testcases\BootUbuntu.air --log_root log\2020-05-09_16-35-09 --outfile log\2020-05-09_16-35-09\report.html --static_root ..\report --lang en --plugin airtest_selenium.report poco.utils.airtest.report