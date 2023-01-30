# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
Boot case 编号:401~500
'''


@core.test_case(('401', '[TC401]Post Information', 'Post Information Test'))
def post_information():
    """
    Name:   Post Information Test

    Steps:  1.检查POST界面显示信息和SetUp下显示是否一致

    Result: 1.显示一致
    """
    try:
        assert Boot.post_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('402', '[TC402]Quick Boot Hot Key', '快捷启动DEL,F11,F12'))
def quick_boot_hotkey():
    """
        Name:   快捷启动DEL,F11,F12

        Steps:  1.POST界面按DEL
                2.POST界面按F11
                3.POST界面按F12

        Result: 1.进入SetUp
                2.进入启动菜单
                3.进入网络启动
        """

    try:
        assert Boot.quick_boot_hotkey()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('403', '[TC403]Boot order ', 'Boot order'))
def boot_order(oem=False):
    """
    Name:   启动顺序

    Steps:  1.进入SetUp,将硬盘调为第一启动顺序,随机修改各启动项的组内顺序
            2.检查启动菜单启动顺序,SetUp下启动顺序与修改的是否一致
            3.依次将剩下的启动组调为第一启动项，随机修改各启动项的组内顺序，重复步骤3

    Result: 2/3.启动顺序与修改的启动顺序一致
    """
    try:
        assert Boot.boot_order(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
