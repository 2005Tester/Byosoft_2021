# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *

auto_setup(__file__)# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *
from pywinauto import keyboard

auto_setup(__file__)
logger=get_logger("airtest")
logger.setLevel(logging.INFO) 

connect_device("windows:////66066")
#wait(Template(r"tpl1588734826875.png", record_pos=(1.024, -0.153), resolution=(1042, 940)), 90, interval=2) #wait for hotkey prpomption
#touch(Template(r"tpl1588734826875.png", record_pos=(1.024, -0.153), resolution=(1042, 940)))
#keyevent("{VK_DELETE}")

wait(Template(r"tpl1588735622040.png", record_pos=(1.421, 0.129), resolution=(1042, 940)), 60, interval=2) #waiting for password promption 
        
touch(Template(r"tpl1588735622040.png", record_pos=(1.421, 0.129), resolution=(1042, 940)))

text("Admin@9000")
#keyevent("{A}""{d}""{m}""{i}""{n}""{@}""{0}""{0}""{0}""{0}")
sleep(2.0)
keyevent("{ENTER}")
sleep(2.0)
wait(Template(r"tpl1588735657059.png", record_pos=(1.417, 0.118), resolution=(1042, 940)),60)
keyevent("{ENTER}")
            




