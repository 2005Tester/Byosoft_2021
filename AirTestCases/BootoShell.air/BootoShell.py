# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *

auto_setup(__file__)

using("HaiYan5Common.air")
import HaiYan5Common


def test_reconnect_r():
    wait(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)))
    text("reconnect{SPACE}-r")
    keyevent("{ENTER}")
    sleep(5)
    wait(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)))
    text("reconnect{SPACE}-r")
    keyevent("{ENTER}")
    sleep(5)
    wait(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)))
    text("reconnect{SPACE}-r")
    keyevent("{ENTER}")
    sleep(5)
    wait(Template(r"tpl1588815378489.png", record_pos=(1.023, 0.001), resolution=(1042, 944)))
    print("Reconnect -r test PASS")

#if __name__ == '__main__':
HaiYan5Common.boot_to_shell()
#test_reconnect_r()
