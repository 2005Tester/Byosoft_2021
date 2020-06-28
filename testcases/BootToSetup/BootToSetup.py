# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *
from airtest.cli.parser import cli_setup
import datetime

auto_setup(__file__, project_root="./testcases")
if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ])
using("HaiYan5Common.air")
import HaiYan5Common

def test_case():
    try:
        HaiYan5Common.boot_to_setup()
    except:
        print("[FAIL] Boot to setup fail.")     
    if exists(Template(r"tpl1589263493143.png", record_pos=(-0.306, -0.157), resolution=(1031, 932))):
        print("[PASS] Boot to setup successfully")
        return True
    else:
        return False
 

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
