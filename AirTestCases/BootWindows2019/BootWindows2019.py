# -*- encoding=utf8 -*-
__author__ = "barton"

import logging
from airtest.utils.logger import get_logger
from airtest.core.api import *
from airtest.core.api import using
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
    try:
        HaiYan5Common.boot_to_bootmanager()
    except Exception as e:
        print(e)
        return False    
    sleep(10)
    touch(Template(r"tpl1596428379397.png", record_pos=(-0.241, -0.089), resolution=(1024, 941)))
    try:
        wait(Template(r"tpl1589280594583.png", record_pos=(0.141, 0.03), resolution=(1031, 951)),timeout=60,interval=10) #wait for loginscreen
    except Exception as e:
        print(e)
        return False

    sleep(2)

    print("[Daily Test] Boot to Windows Server 2019: PASS.")

    return True


def test_case2():
    HaiYan5Common.force_reset()
    sleep(10)
    try:
        wait(Template(r"tpl1589280594583.png", record_pos=(0.141, 0.03), resolution=(1031, 951)),timeout=120,interval=10)
    except Exception as e:
        print(e)
        return False
    sleep(2)

    print("[Daily Test] Boot to Windows Server 2019: PASS.")

    return True


if __name__ == '__main__':
    print('-'*80)
    start_time = datetime.datetime.now()
    print("Test started at %s" %(start_time))
    if test_case2():
        print("OK")
    else:
        print("FAILED")
        
    end_time = datetime.datetime.now()
    print("Test finished at %s" %(end_time))
    time_spent = (end_time-start_time).seconds
    print("Ran 1 test in %s.00s" %(time_spent))

