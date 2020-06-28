# -*- encoding=utf8 -*-
__author__ = "barton"

import logging
from airtest.core.api import *
from airtest.utils.logger import get_logger
from pywinauto import keyboard
from airtest.cli.parser import cli_setup
import datetime

auto_setup(__file__, project_root="./testcases")

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ])
using("HaiYan5Common.air")
import HaiYan5Common

logger=get_logger("airtest")
logger.setLevel(logging.INFO) 



def test_case():
    
    HaiYan5Common.switch_to_legacy()
    sleep(60)
    wait(Template(r"tpl1592904562708.png", record_pos=(-0.164, -0.214), resolution=(1031, 935)),timeout=120,interval=10)
    print("Legacy boot pass")
    HaiYan5Common.reset_default()
    return True
    
    
if __name__ == '__main__':
    print('-'*80)
    start_time = datetime.datetime.now()
    print("Test started at %s" %(start_time))
    if test_case():
        print("OK")
    else:
        print("FAILED")
        
    end_time = datetime.datetime.now()
    print("Test finished at %s" %(end_time))
    time_spent = (end_time-start_time).seconds
    print("Ran 1 test in %s.00s" %(time_spent))
