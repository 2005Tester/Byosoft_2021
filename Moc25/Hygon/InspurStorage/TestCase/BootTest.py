import logging
from batf.Report import ReportGen
from InspurStorage.Base import Boot
from batf import core



'''
Boot case 编号:401~500
'''



@core.test_case(('401','[TC401]Boot','启动测试'))
def boot():
    try:
        assert Boot.boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('402','[TC402]Quick Boot Hot Key','快捷启动DEL,F11,F12'))
def quick_boot_hotkey():
    try:
        assert Boot.quick_boot_hotkey()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('403','[TC403]Boot Order','启动顺序'))
def boot_order():
    try:
        assert Boot.boot_order()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('404','[TC404]Change Boot Order','调整启动顺序'))
def change_boot_order():
    try:
        assert Boot.change_boot_order()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('405','[TC405]PXE Boot','PXE 启动'))
def pxe_boot():
    try:
        assert Boot.pxe_boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
