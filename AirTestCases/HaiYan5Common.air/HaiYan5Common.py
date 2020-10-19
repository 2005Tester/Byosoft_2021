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
    wait(Template(r"tpl1596435579741.png", record_pos=(-0.0, 0.067), resolution=(1024, 940)), 120, interval=3) #waiting for password promption 
        
    touch(Template(r"tpl1596435579741.png", record_pos=(-0.0, 0.067), resolution=(1024, 940)))
    sleep(1.0)
    text(password)
    sleep(1.0)
    keyevent("{ENTER}")
    sleep(1.0)
    if exists(Template(r"tpl1596435737405.png", record_pos=(0.002, 0.069), resolution=(1024, 940))):    #workaround for invalid password issue.
        keyevent("{ENTER}")
        sleep(1.0)
        text(password)
        sleep(1.0)
        keyevent("{ENTER}")
    else:
        return
    
    wait(Template(r"tpl1596435612648.png", record_pos=(-0.002, 0.057), resolution=(1024, 940)),90)
    keyevent("{ENTER}")
    return

def wait_for_hotkey_prompt():
    wait(Template(r"tpl1596435468383.png", record_pos=(-0.395, -0.222), resolution=(1024, 940)), 90, interval=2) #wait for hotkey prpomption
    touch(Template(r"tpl1596435468383.png", record_pos=(-0.395, -0.222), resolution=(1024, 940)))

def boot_to_setup():
    if exists(Template(r"tpl1596434993798.png", record_pos=(-0.001, 0.033), resolution=(1024, 940))):

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
    touch(Template(r"tpl1596435022477.png", record_pos=(0.278, 0.143), resolution=(1024, 940)))
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
        wait(Template(r"tpl1596435041034.png", record_pos=(-0.307, -0.13), resolution=(1024, 940)), 90)
        touch(Template(r"tpl1596435056745.png", record_pos=(-0.02, -0.126), resolution=(1024, 940)))
        touch(Template(r"tpl1589266229955.png", record_pos=(-0.337, -0.055), resolution=(1031, 932)))
        keyevent("{ENTER}")
        
    wait(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)), 30)
    print("Boot to uefi shell: PASS")
    return
    
def password_setting():
        
    if exists(Template(r"tpl1596434993798.png", record_pos=(-0.001, 0.033), resolution=(1024, 940))):
        touch(Template(r"tpl1596435022477.png", record_pos=(0.278, 0.143), resolution=(1024, 940)))
    else:
        boot_to_setup()
        sleep(3.0)
        touch(Template(r"tpl1596435022477.png", record_pos=(0.278, 0.143), resolution=(1024, 940)))
    keyevent("{ENTER}")
    wait(Template(r"tpl1596435197439.png", record_pos=(-0.296, -0.167), resolution=(1024, 940)))
    touch(Template(r"tpl1596435210019.png", record_pos=(-0.268, -0.235), resolution=(1024, 940)))
    touch(Template(r"tpl1596435210019.png", record_pos=(-0.268, -0.235), resolution=(1024, 940)))


def boot_to_bootmanager():
    print("Boot to boot menu using hot key: F11")


    force_reset()
    wait_for_hotkey_prompt()
    for i in range(5):
        keyevent("{VK_F11}")
        sleep(1)
    input_password()
    sleep(3)
    
    if exists(Template(r"tpl1596435771883.png", record_pos=(-0.354, -0.163), resolution=(1024, 940))):
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
    if exists(Template(r"tpl1596436273059.png", record_pos=(-0.167, 0.208), resolution=(1024, 940))):
        print("Already in legacy mode")
        touch(Template(r"tpl1596435969204.png", record_pos=(-0.309, -0.124), resolution=(1024, 940)))
        keyevent("{ENTER}")
        return
    else:
        sleep(3.0)
        touch(Template(r"tpl1596435980556.png", record_pos=(0.278, 0.148), resolution=(1024, 940)))
        sleep(2.0)
        snapshot(msg="Should be in BIOS configuration page now.")

        keyevent("{ENTER}")
        wait(Template(r"tpl1596436037907.png", record_pos=(-0.295, -0.172), resolution=(1024, 940)))
        touch(Template(r"tpl1596436048573.png", record_pos=(-0.208, -0.238), resolution=(1024, 940)))
        touch(Template(r"tpl1596436048573.png", record_pos=(-0.208, -0.238), resolution=(1024, 940)))
        wait(Template(r"tpl1596436088600.png", record_pos=(-0.198, -0.214), resolution=(1024, 940)))
        keyevent("{ENTER}")
        sleep(2)
        touch(Template(r"tpl1596436129566.png", record_pos=(-0.019, 0.094), resolution=(1024, 940)))
        keyevent("{ENTER}")
        sleep(2)
        keyevent("{F10}")
        sleep(2)
        text("Y")
        return

def reset_default():
    boot_to_bios_configuration()
    keyevent("{F9}")
    touch(Template(r"tpl1596436957759.png", record_pos=(-0.068, 0.07), resolution=(1024, 940)))
    sleep(20.0)
    keyevent("{F10}")
    touch(Template(r"tpl1596437010511.png", record_pos=(-0.068, 0.07), resolution=(1024, 940)))
    keyevent("{Y}")
    sleep(20.0)

    return
    
    
    
    


    

        


