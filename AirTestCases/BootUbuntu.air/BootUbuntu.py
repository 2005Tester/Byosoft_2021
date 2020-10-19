# -*- encoding=utf8 -*-
__author__ = "barton"
import logging
from airtest.utils.logger import get_logger
from airtest.core.api import *

auto_setup(__file__)

logger=get_logger("airtest")
logger.setLevel(logging.INFO)
sleep(30)
wait(Template(r"tpl1589796050102.png", record_pos=(-0.005, 0.017), resolution=(1031, 933)),timeout=120,interval=10)
touch(Template(r"tpl1589796050102.png", record_pos=(-0.005, 0.017), resolution=(1031, 933)))
#wait(Template(r"tpl1589340787696.png", record_pos=(-0.406, -0.275), resolution=(1031, 951)),timeout=120,interval=10)
#touch(Template(r"tpl1589340787696.png", record_pos=(-0.406, -0.275), resolution=(1031, 951)))

sleep(2)

#text("byosoft")
#keyevent("{ENTER}")
#sleep(2)
text("byosoft@123")
keyevent("{ENTER}")
print("[Daily] Boot to Ubuntu: PASS.")