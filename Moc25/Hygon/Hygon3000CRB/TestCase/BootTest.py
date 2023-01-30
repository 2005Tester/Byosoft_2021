import logging
from batf.Report import ReportGen
from Hygon3000CRB.Base import Boot
from batf import core



'''
Boot case 编号:401~500

'''



@core.test_case(('401','[TC401]Post Information','Post Information Test'))
#SetUp界面信息
def post_information():
    try:
        assert Boot.post_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('402','[TC402]Quick Boot Hot Key','快捷启动F2,F7,F12'))
def quick_boot_hotkey():
    try:
        assert Boot.quick_boot_hotkey()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('403','[TC403]Post Logo','Post Logo检查'))
def post_logo():
    try:
        assert Boot.post_logo()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

