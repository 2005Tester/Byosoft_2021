import logging
import time
from batf.Report import ReportGen
from InspurStorage.Base import CheckMsg
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.BaseLib import BmcLib,SetUpLib
from batf import core



'''
CheckMsg  case 编号:501~600
'''



@core.test_case(('501', '[TC501]Check Product Msg','检查生产制造信息'))
def product_msg():
    try:
        assert CheckMsg.product_msg()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('502', '[TC502]Check BIOS Msg','检查BIOS信息'))
def bios_msg():
    try:
        assert CheckMsg.bios_msg()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('503', '[TC503]Check Memory Msg','检查内存信息'))
def memory_msg():
    try:
        assert CheckMsg.memory_msg()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('504', '[TC504]Check CPU Msg','检查CPU信息'))
def cpu_msg():
    try:
        assert CheckMsg.cpu_msg()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('505', '[TC505]Check LAN Msg and NVME Msg','板载网卡，NVME信息检查'))
def lan_nvme_msg():
    try:
        assert CheckMsg.lan_nvme_msg()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('506', '[TC506]Memory Training Show','内存Training结果展示'))
def memory_training():
    try:
        assert CheckMsg.memory_training()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('507', '[TC507]Debug Mode','日志打印级别'))
def debug_mode():
    try:
        assert CheckMsg.debug_mode()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('508', '[TC508]GPIO','支持初始化GPIO OK_REDUCE_PWR_R 为 OUTPUT，初始化为无效电平'))
def gpio():
    try:
        assert CheckMsg.gpio()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('509', '[TC509]SMBUS','smbus频率默认配置为100KHZ'))
def smbus():
    try:
        assert CheckMsg.smbus()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('510', '[TC510]NTB Resource Reservation','NTB资源预留'))
def ntb_resource_reservation():
    try:
        assert CheckMsg.ntb_resource_reservation()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('511', '[TC511]Check Bds','Debug,Information,Warning级别启动选项打印'))
def che_bds():
    try:
        assert CheckMsg.che_bds()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('512', '[TC512]Check Postcode','Check Postcode'))
def che_postcode():
    try:
        assert CheckMsg.che_postcode()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('513', '[TC513]Check RAS','Check RAS'))
def che_ras():
    try:
        assert CheckMsg.che_ras()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('514', '[TC514]Check SetUp Clear','检查BIOS SetUp界面整洁'))
def che_debug_mode_clear():
    try:
        assert CheckMsg.che_debug_mode_clear()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail