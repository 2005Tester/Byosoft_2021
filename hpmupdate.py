# -*- encoding=utf8 -*-
import os
import shutil
import re
from pathlib import Path
import paramiko
import time
import common
import updatebios

STATUS_FAIL = 0
STATUS_PASS = 1
STATUS_SKIP = 2

# Test environment settings
HPM_TEST_PATH = 'hpm'
IMAGE_V1 = os.path.join(HPM_TEST_PATH,'V1') + '\HY5V007.BIN'
HPM_V1 = os.path.join(HPM_TEST_PATH,'V1') + '\\biosimage.hpm'
SUT = "192.168.100.155"
USERNAME = "byosoft"
PW = "byosoft@123"
SCU_DIR = '~/Scu_tool/Linux_17.10/App'    #Scu tool directory on SUT 
# Test environment settings

prt = common.PrintColor()

def check_env():
    pass

def get_test_image():

    test_dir = os.getcwd()
    dst = os.path.join(test_dir,'bios\RP001.bin')
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(IMAGE_V1,dst)
    if os.path.exists(dst):
        return STATUS_PASS
    else:
        print("Failed to copy BIOS image.")
        return STATUS_FAIL

def update_bios():
    status = get_test_image()
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

def fetch_log(src, dst):
    transport = paramiko.Transport((SUT, 22))
    transport.connect(username = USERNAME, password = PW)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(src, dst)
    transport.close()

def dump_setup():
    
    cmd_enter_scu_dir = 'cd ' + SCU_DIR + '\n'
    cmd_dump_setup = "./scu -d"
    cmd_confirm = 'Y\n'

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(SUT,22,USERNAME, PW)
    op=s.invoke_shell()
    
    def send_cmd(cmd):
        op.send(cmd)
        time.sleep(5)
        res=op.recv(1024)
        return(res)

    res = send_cmd(cmd_enter_scu_dir)  #shutdown SUT
    print(res.decode('utf-8'))
    res = send_cmd(cmd_dump_setup)
    print(res.decode('utf-8'))

    
    op.close()
    s.close()


if __name__ =='__main__':
    dump_setup()