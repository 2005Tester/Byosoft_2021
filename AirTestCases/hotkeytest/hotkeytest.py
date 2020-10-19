# -*- encoding=utf8 -*-
__author__ = "barton"
import logging
from airtest.utils.logger import get_logger
from airtest.core.api import *
from airtest.cli.parser import cli_setup

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ])
logger=get_logger("airtest")
logger.setLevel(logging.INFO)

# script content
print("start...")

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
        
        
def testcase():
    while True:
        try:
            boot_to_setup()
        except Exception as e:
            print(e)
        sleep(5)
        try:
            force_reset()
        except Exception as e:
            print(e)
        
testcase()


# generate html report
# from airtest.report.report import simple_report
# simple_report(__file__, logpath=True)
