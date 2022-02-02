import logging
import time
from batf.Report import ReportGen
from Hygon3000CRB.Config.PlatConfig import Key, Msg
from Hygon3000CRB.BaseLib import BmcLib,SetUpLib
from Hygon3000CRB.Config import SutConfig
from Hygon3000CRB.Base import PXE
from batf import core



'''
PXE  case  编号: 201~250
'''



@core.test_case(('201','[TC201]PXE BOOT','PXE启动IPv4和IPv6'))
def pxe_boot():
    try:
        assert PXE.pxe_boot()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_BOOT_OPTION_FILTER_UEFI, 8)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('202','[TC202]PXE Option Rom','PXE网络引导'))
def pxe_option_rom():
    try:
        assert PXE.pxe_option_rom()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('203','[TC203]PXE Retry','网络启动重试'))
def pxe_retry():
    try:
        assert PXE.pxe_retry()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_PXE_RETRY_DISABLED, 6)
        time.sleep(1)
        SetUpLib.send_data_enter('0')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('204', '[TC204]Net Boot IP Version', '网络引导IP版本'))
def pxe_protocol():
    try:
        assert PXE.pxe_protocol()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('205', '[TC205]HTTP Boot', 'HTTP 启动'))
def Http_Boot():
    try:
        assert PXE.Http_Boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



# @core.test_case(('205', '[TC205]PXE Network', 'PXE启动网卡'))
# def pxe_network():
#     try:
#         assert PXE.pxe_network()
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail



# @core.test_case(('206', '[TC206]PXE BOOT Priority', 'PXE启动优先级'))
# def pxe_boot_priority():
#     try:
#         assert PXE.pxe_boot_priority()
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail