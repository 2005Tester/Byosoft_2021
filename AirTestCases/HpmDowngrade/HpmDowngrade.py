# -*- encoding=utf8 -*-
__author__ = "barton"
import sys
sys.path.append("c:\\autotest")
import logging
from airtest.core.api import *
from airtest.cli.parser import cli_setup
from airtest.utils.logger import get_logger
import updatebios
import datetime

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ])

logger=get_logger("airtest")
logger.setLevel(logging.INFO)
    
def force_reset():
    touch(Template(r"tpl1588732575954.png", record_pos=(1.189, -0.241), resolution=(1042, 940)))
    if exists(Template(r"tpl1592976719320.png", record_pos=(-0.193, -0.085), resolution=(1031, 935))):
        touch(Template(r"tpl1592976719320.png", record_pos=(-0.193, -0.085), resolution=(1031, 935)))

    if exists(Template(r"tpl1588734216518.png", record_pos=(1.353, 0.25), resolution=(1042, 940))):
        touch(Template(r"tpl1588734216518.png", record_pos=(1.353, 0.25), resolution=(1042, 940)))

def test_case():    

    hpm = "C:\\autotest\\hpm\\biosimage.hpm"
    updatebios.upload_bios(hpm)
    updatebios.hpm_update()
    
        
    force_reset()
    
    sleep(30)
    
    wait(Template(r"tpl1592975564138.png", record_pos=(0.013, -0.03), resolution=(1031, 935)), timeout=60,interval=10)

    while exists(Template(r"tpl1592977269104.png", record_pos=(0.006, -0.031), resolution=(1031, 935))):
        sleep(10)
        print("Upgrade in progress...")  

    print("upgrade completed")
    
    wait(Template(r"tpl1593339773774.png", record_pos=(-0.215, 0.046), resolution=(1031, 935)), timeout=60, interval=5)
   
    print("Downgrade to previous release done, booting now...")

    return True
    


if __name__ == '__main__':
    print('-'*80)
    start_time = datetime.datetime.now()
    print("Test started at %s" %(start_time))
    try: 
        test_case()
        print("OK")
    except Exception as e:
        print(e)
        print("FAILED")
    end_time = datetime.datetime.now()
    print("Test finished at %s" %(end_time))
    time_spent = (end_time-start_time).seconds
    print("Ran 1 test in %s.00s" %(time_spent))





