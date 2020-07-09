# -*- encoding=utf8 -*-
__author__ = "barton"
import logging
from airtest.utils.logger import get_logger
from airtest.core.api import *
from airtest.cli.parser import cli_setup
import datetime

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ])

logger=get_logger("airtest")
logger.setLevel(logging.INFO)

def test_case():
    sleep(30)
    try:
        wait(Template(r"tpl1589796050102.png", record_pos=(-0.005, 0.017), resolution=(1031, 933)),timeout=120,interval=10)
        touch(Template(r"tpl1589796050102.png", record_pos=(-0.005, 0.017), resolution=(1031, 933)))
    except Exception as e:
        print(e)
        return False

    sleep(2)

    text("byosoft@123")
    keyevent("{ENTER}")
    print("[Daily] Boot to Ubuntu: PASS.")
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
