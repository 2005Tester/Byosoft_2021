# -*- encoding=utf8 -*-
__author__ = "barton"
import logging
from airtest.core.api import *
from pywinauto import keyboard
from airtest.utils.logger import get_logger


auto_setup(__file__)

logger=get_logger("airtest")
logger.setLevel(logging.INFO)

#connect_device("windows:////66066")

STATUS_PASS = 1
STATUS_FAIL = 0

def force_reset():
    touch(Template(r"tpl1588732575954.png", record_pos=(1.189, -0.241), resolution=(1042, 940)))
    if exists(Template(r"tpl1588734153376.png", record_pos=(1.199, -0.066), resolution=(1042, 940))):
        touch(Template(r"tpl1588734153376.png", record_pos=(1.199, -0.066), resolution=(1042, 940)))
    else:
        touch(Template(r"tpl1588125263447.png", record_pos=(0.897, -0.062), resolution=(1249, 1017)))
    if exists(Template(r"tpl1588734216518.png", record_pos=(1.353, 0.25), resolution=(1042, 940))):
        touch(Template(r"tpl1588734216518.png", record_pos=(1.353, 0.25), resolution=(1042, 940)))
    else:
        touch(Template(r"tpl1588124796596.png", record_pos=(1.222, 0.185), resolution=(1094, 932)))

def input_password():
    password = "Admin@9000"
    wait(Template(r"tpl1588735622040.png", record_pos=(1.421, 0.129), resolution=(1042, 940)), 60, interval=3) #waiting for password promption 
        
    touch(Template(r"tpl1588735622040.png", record_pos=(1.421, 0.129), resolution=(1042, 940)))
    sleep(1.0)
    text(password)
    sleep(1.0)
    keyevent("{ENTER}")
    sleep(1.0)
    if exists(Template(r"tpl1589246727794.png", record_pos=(-0.002, 0.041), resolution=(1031, 933))):    #workaround for invalid password issue.
        keyevent("{ENTER}")
        sleep(1.0)
        text(password)
        sleep(1.0)
        keyevent("{ENTER}")
    else:
        pass
    
    keyevent("{ENTER}")
        
        
    #wait(Template(r"tpl1588735657059.png", record_pos=(1.417, 0.118), resolution=(1042, 940)),60)
    #keyevent("{ENTER}")
    return

def wait_for_hotkey_prompt():
    wait(Template(r"tpl1588734826875.png", record_pos=(1.024, -0.153), resolution=(1042, 940)), 90, interval=2) #wait for hotkey prpomption
    touch(Template(r"tpl1588734826875.png", record_pos=(1.024, -0.153), resolution=(1042, 940)))

def boot_to_setup():
    if exists(Template(r"tpl1588726655823.png", record_pos=(1.55, 0.006), resolution=(966, 739))):

        return
    else:
        force_reset()
        wait_for_hotkey_prompt()
        #keyevent("{VK_DELETE}")
        for i in range(3):
            keyevent("{VK_DELETE}")
            sleep(1)
        print("Waiting for password prompt")
        input_password()
           
        return
     
def boot_to_shell():
    if exists(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944))):
        touch(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)))
        sleep(2.0)
        text("echo{SPACE}already{SPACE}in{SPACE}shell")
        text("{ENTER}")
        sleep(2.0)

    else:
        boot_to_setup()
        wait(Template(r"tpl1588735698091.png", record_pos=(1.118, -0.064), resolution=(1042, 940)), 90)
        touch(Template(r"tpl1589266174268.png", record_pos=(-0.01, -0.154), resolution=(1031, 932)))
        touch(Template(r"tpl1589266229955.png", record_pos=(-0.337, -0.055), resolution=(1031, 932)))
        keyevent("{ENTER}")
        
    wait(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)), 30)
    print("[Daily] Boot to uefi shell: PASS")
    return
    
def password_setting():
        
    if exists(Template(r"tpl1589006414567.png", record_pos=(-0.015, 0.018), resolution=(1031, 936))):
        touch(Template(r"tpl1589006439594.png", record_pos=(0.278, 0.147), resolution=(1031, 936)))
    else:
        boot_to_setup()
        sleep(3.0)
        touch(Template(r"tpl1589006439594.png", record_pos=(0.278, 0.147), resolution=(1031, 936)))
    keyevent("{ENTER}")
    wait(Template(r"tpl1589006859333.png", record_pos=(-0.296, -0.17), resolution=(1031, 936)))
    touch(Template(r"tpl1589011209290.png", record_pos=(-0.267, -0.233), resolution=(1031, 936)))
    touch(Template(r"tpl1589011209290.png", record_pos=(-0.267, -0.233), resolution=(1031, 936)))


def boot_to_bootmanager():
    print("Boot to boot menu using hot key: F11")


    force_reset()
    wait_for_hotkey_prompt()
    for i in range(5):
        keyevent("{VK_F11}")
        sleep(1)
    input_password()
    sleep(3)
    
    if exists(Template(r"tpl1589178358928.png", record_pos=(-0.346, -0.188), resolution=(1031, 933))):
        print("[Daily] Boot to Boot manager by hotkey: PASS")
        return STATUS_PASS
    else:
        print("[Daily] Boot to Boot manager by hotkey: FAIL")
        return STATUS_FAIL                  

#boot_to_bootmanager()
#input_password()
#boot_to_setup()
#password_setting()
    

        

