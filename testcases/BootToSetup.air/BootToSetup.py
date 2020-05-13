# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *

auto_setup(__file__)
using("HaiYan5Common.air")
import HaiYan5Common


HaiYan5Common.boot_to_setup()
if exists(Template(r"tpl1589263493143.png", record_pos=(-0.306, -0.157), resolution=(1031, 932))):
    print("[PASS] Boot to setup successfully")
else:
    print("Test fail")
 