# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *
from airtest.cli.parser import cli_setup
from airtest.core.api import using
import datetime

auto_setup(__file__, project_root="./testcases")
if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ])
    
using("HaiYan5Common.air")
import HaiYan5Common



def test_case():
    # Define the test senarior here
    try: 
        HaiYan5Common.boot_to_shell()
        return True
    except:
        print("Boot to uefi shell fail.")
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












