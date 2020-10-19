#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

"""
HPM 测试步骤：
1. 旧版本的bin和hpm文件放在hpm/V1目录下面
2. 新版本的bin和hpm放在hpm/V2目录下面
3. cd c:\auttest
4. python hpmupdate.py

测试流程： 更新版本V1 binary -> 更新HPM case 1 -> upload customized scu.xml, change logo, change pw, add option->boot ->scu dump xml () -> Verify
          更新版本V1 binary -> 更新HPM case 2 -> upload customized scu.xml, change logo, change pw, add option->boot ->scu dump xml () -> Verify
          更新版本V1 binary -> 更新HPM case 3 -> upload customized scu.xml, change logo, change pw, add option->boot ->scu dump xml () -> Verify
          更新版本V1 binary -> 更新HPM case 4 -> upload customized scu.xml, change logo, change pw, add option->boot ->scu dump xml () -> Verify

"""

# -*- encoding=utf8 -*-
import os
import shutil
import re
from pathlib import Path
import paramiko
import time
import common
import updatebios
import RunDailyTest

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

# Test environment settings
HPM_TEST_PATH = 'hpm'
IMAGE_V1 = os.path.join(HPM_TEST_PATH,'V1') + '\HY5V007.BIN'
HPM_V1 = os.path.join(HPM_TEST_PATH,'V1') + '\\biosimage.hpm'
SUT = '192.168.100.166'
USERNAME = 'byosoft'
PW = "byosoft@123"
SCU_DIR = '/home/byosoft/Scu_tool/Linux_17.10/App'    #Scu tool directory on SUT 
# Test environment settings

prt = common.PrintColor()

def check_env():
    pass

def get_test_image(image):
    test_dir = os.getcwd()
    dst = os.path.join(test_dir,'bios\\RP001.bin')    #default buios image, if hpm image, change dst to hpm
    if re.search('.hpm', image):
        dst = os.path.join(test_dir,'bios\\bios.hpm')
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(image,dst)
    if os.path.exists(dst):
        return STATUS_PASS
    else:
        print("Failed to copy BIOS image.")
        return STATUS_FAIL

def update_bios(image_src, image_dst): 
    status = get_test_image(image_src)
    if status == STATUS_PASS:
        prt.print_green_text("Check Wheter Image is copied to local HDD: PASS")
        if updatebios.upload_bios(image_dst):
            prt.print_green_text("Upload bios to iBMC: PASS")
            if re.search('.bin', image_dst):
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
                updatebios.hpm_update()
                #update hpm
        else:
            return STATUS_FAIL
    elif status == STATUS_SKIP:
        return STATUS_SKIP
   
    else:
        return STATUS_FAIL   

def fetch_log(src, dst):
    if os.path.exists(dst):
        print("Deleting existing log...")
        os.system('del /f /s '+ dst)
    transport = paramiko.Transport((SUT, 22))
    transport.connect(username = USERNAME, password = PW)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        print("Fetching dump file...")
        sftp.get(src, dst)
        transport.close()
    except IOError:
        print("Can't fetch dump file, please check whether the file exists.")
        transport.close()

def dump_setup():
    cmd_su_root = 'su root\n'
    cmd_input_pw = 'byosoft@123\n'
    cmd_enter_scu_dir = 'cd ' + SCU_DIR + '\n'
    cmd_dump_setup = './scu -d\n'
    cmd_confirm = 'Y\n'
    cmd_insmod = 'insmod scudev.ko\n'

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(SUT,22,USERNAME, PW)
    op=s.invoke_shell()
    
    def send_cmd(cmd):
        op.send(cmd)
        time.sleep(5)
        res=op.recv(1024)
        print(res.decode('utf-8'))
        return(res)

    send_cmd(cmd_su_root) 
    send_cmd(cmd_input_pw) 
    send_cmd(cmd_enter_scu_dir)  
    send_cmd(cmd_insmod)
    send_cmd(cmd_dump_setup)
    time.sleep(10)

    
    op.close()
    s.close()

def verify(testcases):
    log_dir = common.create_log_dir()
    for tc in testcases: 
        if tc['exec'] == 1:
            log = "\"" + log_dir + "\\" + tc['name'] + "\""
            print(log)
            RunDailyTest.run_airtest(tc['script'], RunDailyTest.device, log, 'hpm\\log.txt')
            print("-"*50)

if __name__ =='__main__':
    src = SCU_DIR + '/scu.xml'
    dst = 'hpm\scu.xml'
    TC0 = {'id': 0, 'name':'HpmUpdate',     'script': "\"C:\\autotest\\testcases\\HpmUpdate.air\"",         'exec':1}
    tc_list = [RunDailyTest.TC0]
    tc_list2 = [TC0]
    #dump_setup()
    #fetch_log(src,dst)
    #prt.print_green_text("Updateing BIOS image for V1")
    #update_bios(IMAGE_V1,'bios\\RP001.bin')

    #prt.print_green_text("Booting to Ubuntu with V1...")
    #verify(tc_list)

    prt.print_green_text("Updateing HPM image for V1")
    update_bios(HPM_V1,'bios\\bios.hpm')
    verify(tc_list2)

    prt.print_green_text("Dump setup data using scu tool...")
    dump_setup()

    prt.print_green_text("Downloading scu dump to %s" %(dst))
    fetch_log(src,dst)