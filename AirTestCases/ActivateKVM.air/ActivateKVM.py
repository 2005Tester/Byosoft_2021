# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *

auto_setup(__file__)


def activate_kvm():
    if exists(Template(r"tpl1588917520757.png", record_pos=(-0.004, -0.106), resolution=(1038, 957))):
        touch(Template(r"tpl1588917533782.png", record_pos=(-0.001, -0.036), resolution=(1038, 957)))
    else:
        wait(Template(r"tpl1588916857582.png", record_pos=(0.098, -0.028), resolution=(1038, 957)),10)
        touch(Template(r"tpl1588916857582.png", record_pos=(0.098, -0.028), resolution=(1038, 957)))
        text("Administrator")
        touch(Template(r"tpl1588916992131.png", record_pos=(0.136, 0.072), resolution=(1038, 957)))
        text("Admin@9000")

        touch(Template(r"tpl1588917014749.png", record_pos=(0.13, 0.278), resolution=(1038, 957)))
        sleep(2.0)
        wait(Template(r"tpl1588917199245.png", record_pos=(-0.363, 0.305), resolution=(1038, 957)))
        text("{DWON 3}")
        touch(Template(r"tpl1588917799458.png", record_pos=(0.423, 0.158), resolution=(1038, 957)))

        
    



    

