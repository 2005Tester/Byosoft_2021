# -*- encoding=utf8 -*-
__author__ = "barton"
import logging
from airtest.utils.logger import get_logger
from airtest.core.api import *

auto_setup(__file__)

logger=get_logger("airtest")
logger.setLevel(logging.INFO)

using("HaiYan5Common.air")
import HaiYan5Common

HaiYan5Common.boot_to_shell()
text("FS1:\\EFI\\Microsoft\\boot\\bootmgfw.efi")
sleep(2)
keyevent("{ENTER}")
sleep(30)

wait(Template(r"tpl1589280594583.png", record_pos=(0.141, 0.03), resolution=(1031, 951)),timeout=60,interval=10) #wait for loginscreen

sleep(2)

print("[PASS] Boot to Windows Server 2019 Successfully.")
