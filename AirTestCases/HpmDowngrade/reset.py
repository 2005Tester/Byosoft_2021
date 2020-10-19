# -*- encoding=utf8 -*-
__author__ = "barton"
import sys
sys.path.append("c:\\autotest")
from airtest.core.api import *
from airtest.cli.parser import cli_setup
from airtest.core.api import using



if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///?title_re=iBMC*",
    ], project_root="C:/autotest/testcases")
    
#using("HpmDowngrade.air")
import HpmDowngrade



if __name__ == '__main__':
    HpmDowngrade.force_reset()
#test_reconnect_r()
