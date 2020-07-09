# -*- encoding=utf8 -*-
__author__ = "barton"
import logging
from airtest.core.api import *
from pywinauto import keyboard
from airtest.utils.logger import get_logger
from airtest.cli.parser import cli_setup

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ], project_root="./testcases")

logger=get_logger("airtest")
logger.setLevel(logging.INFO)

#connect_device("windows:////66066")


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
    wait(Template(r"tpl1588735622040.png", record_pos=(1.421, 0.129), resolution=(1042, 940)), 90, interval=3) #waiting for password promption 
        
    touch(Template(r"tpl1588735622040.png", record_pos=(1.421, 0.129), resolution=(1042, 940)))
    sleep(1.0)
    text(password)
    sleep(1.0)
    keyevent("{ENTER}")
    sleep(1.0)
    if exists(Template(r"tpl1593395950246.png", record_pos=(0.009, 0.045), resolution=(1031, 935))):    #workaround for invalid password issue.
        keyevent("{ENTER}")
        sleep(1.0)
        text(password)
        sleep(1.0)
        keyevent("{ENTER}")
    else:
        return
    
    wait(Template(r"tpl1593396125644.png", record_pos=(0.003, 0.033), resolution=(1031, 935)),90)
    keyevent("{ENTER}")
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
        snapshot(msg="Should be in setup frontpage.")     
        return
    
def boot_to_bios_configuration():

    boot_to_setup()
    sleep(3.0)
    touch(Template(r"tpl1589006439594.png", record_pos=(0.278, 0.147), resolution=(1031, 936)))
    sleep(2.0)
    snapshot(msg="Should be in BIOS configuration page now.")

    
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
    print("Boot to uefi shell: PASS")
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
        print("Boot to Boot manager by hotkey: PASS")
        return True
    else:
        print("Boot to Boot manager by hotkey: FAIL")
        return False 
    
def sp_boot():

    print("SP Boot using hot key: F6")


    force_reset()
    wait_for_hotkey_prompt()
    for i in range(5):
        keyevent("{VK_F6}")
        sleep(1)
    input_password()
    sleep(3) 
    
    wait(Template(r"tpl1590055080651.png", record_pos=(0.003, 0.038), resolution=(1043, 946)),90, interval=2)
    wait(Template(r"tpl1590055647233.png", record_pos=(0.005, 0.071), resolution=(1043, 946)),90, interval=2)
    touch(Template(r"tpl1590055647233.png", record_pos=(0.005, 0.071), resolution=(1043, 946)))
    sleep(5)
    
    if exists(Template(r"tpl1590055358605.png", record_pos=(-0.32, -0.052), resolution=(1043, 946))):
    
        print("SP Boot by hotkey: PASS")
        return True
    else:
        print("SP Boot by hotkey: FAIL")
        return False   
    
def switch_to_legacy():
    boot_to_setup()
    if exists(Template(r"tpl1592906251630.png", record_pos=(-0.152, 0.182), resolution=(1031, 935))):
        print("Already in legacy mode")
        touch(Template(r"tpl1592907179693.png", record_pos=(-0.305, -0.153), resolution=(1031, 935)))
        keyevent("{ENTER}")
        return
    else:
        sleep(3.0)
        touch(Template(r"tpl1589006439594.png", record_pos=(0.278, 0.147), resolution=(1031, 936)))
        sleep(2.0)
        snapshot(msg="Should be in BIOS configuration page now.")

        keyevent("{ENTER}")
        wait(Template(r"tpl1589006859333.png", record_pos=(-0.296, -0.17), resolution=(1031, 936)))
        touch(Template(r"tpl1590143311059.png", record_pos=(-0.205, -0.264), resolution=(1043, 946)))
        touch(Template(r"tpl1590143311059.png", record_pos=(-0.205, -0.264), resolution=(1043, 946)))
        wait(Template(r"tpl1590143370584.png", record_pos=(-0.174, -0.247), resolution=(1043, 946)))
        keyevent("{ENTER}")
        sleep(2)
        touch(Template(r"tpl1590143446657.png", record_pos=(-0.012, 0.063), resolution=(1043, 946)))
        keyevent("{ENTER}")
        sleep(2)
        keyevent("{F10}")
        sleep(2)
        text("Y")
        return

def reset_default():
    boot_to_bios_configuration()
    keyevent("{F9}")
    touch(Template(r"tpl1592905427091.png", record_pos=(-0.071, 0.067), resolution=(1031, 935)))
    sleep(20.0)
    keyevent("{F10}")
    touch(Template(r"tpl1592905427091.png", record_pos=(-0.071, 0.067), resolution=(1031, 935)))
    keyevent("{Y}")

    return
    
    
    
    


    

        


