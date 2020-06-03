# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *

auto_setup(__file__)

# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *
from airtest.utils.logger import get_logger
import logging
auto_setup(__file__)
using("HaiYan5Common.air")
import HaiYan5Common

logger=get_logger("airtest")
logger.setLevel(logging.INFO)

"""
Verify added setup option after HPM update:
ServeMEDebug -General - Region_Select Message ["Disable",Enable]	增加
ServeMEDebug -General - Watchdog Control Message [Enable]	增加


"""
def VerifyMEAddedItem():
    HaiYan5Common.boot_to_setup()
    touch(Template(r"tpl1589769898147.png", record_pos=(0.283, 0.127), resolution=(1031, 933)))
    sleep(2)
    touch(Template(r"tpl1589769898147.png", record_pos=(0.283, 0.127), resolution=(1031, 933)))
    sleep(2)
    touch(Template(r"tpl1589770021706.png", record_pos=(-0.388, -0.264), resolution=(1031, 933)))
    sleep(2)
    touch(Template(r"tpl1589770064685.png", record_pos=(-0.324, -0.123), resolution=(1031, 933)))
    
    wait(Template(r"tpl1589770512352.png", record_pos=(-0.32, -0.122), resolution=(1031, 933)))
    keyevent("{ENTER}")
    wait(Template(r"tpl1589770830614.png", record_pos=(-0.315, -0.217), resolution=(1031, 933)))
    snapshot(msg="Please check whether option ServerMEDebug - General - Region_Select Message[Disable,Enable] is added.")

def VerifyMemoryAddedItem():
    pass
      
def verify_hpm_update():
    HaiYan5Common.force_reset()
    wait(Template(r"tpl1590474534066.png", record_pos=(0.01, -0.064), resolution=(1043, 946)))
    sleep(30)
    while(True):
        if exists(Template(r"tpl1590474534066.png", record_pos=(0.01, -0.064), resolution=(1043, 946))):
            sleep(5)
            print("Performing BIOS upgrading ...")
        else:
            break
    wait(Template(r"tpl1590474872679.png", record_pos=(0.008, 0.023), resolution=(1043, 946)), timeout=120,interval=10)
    print('Boot to ubuntu')
    
