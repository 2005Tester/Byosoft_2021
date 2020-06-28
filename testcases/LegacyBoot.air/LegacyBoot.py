# -*- encoding=utf8 -*-
__author__ = "barton"
auto_setup(__file__)# -*- encoding=utf8 -*-
import logging
from airtest.core.api import *
from airtest.utils.logger import get_logger
from pywinauto import keyboard
using("HaiYan5Common.air")
import HaiYan5Common

auto_setup(__file__)
logger=get_logger("airtest")
logger.setLevel(logging.INFO) 

def test_case():
    
    
    HaiYan5Common.switch_to_legacy()
    sleep(60)
    wait(Template(r"tpl1592904562708.png", record_pos=(-0.164, -0.214), resolution=(1031, 935)),timeout=120,interval=10)
    print("Legacy boot pass")
    HaiYan5Common.reset_default()
    

    
test_case()

