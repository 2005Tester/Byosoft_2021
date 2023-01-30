# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
RedFish  case  编号:901~950
'''


@core.test_case(('901', '[TC901]RedFish 电源管理', 'RedFish 电源管理'))
def power_management():
    try:
        assert RedFish.power_management()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('902', '[TC902]RedFish Check BIOS Version', 'RedFish Check BIOS Version'))
def check_bios_version():
    try:
        assert RedFish.check_bios_version()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('903', '[TC903]RedFish 检查CPU频率', 'RedFish 检查CPU频率'))
def check_cpu_frequency():
    try:
        assert RedFish.check_cpu_frequency()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('904', '[TC904]RedFish 检查CPU核数，线程数', 'RedFish 检查CPU核数，线程数'))
def check_cpu_core_thread():
    try:
        assert RedFish.check_cpu_core_thread()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('905', '[TC905]RedFish 修改超线程', 'RedFish 修改超线程'))
def rfh_change_hyper_thread():
    try:
        assert RedFish.rfh_change_hyper_thread()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('906', '[TC906]RedFish 检查内存信息', 'RedFish 检查内存信息'))
def check_mem():
    try:
        assert RedFish.check_mem()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('907', '[TC907]RedFish 检查硬盘信息', 'RedFish 检查硬盘信息'))
def check_hdd():
    try:
        assert RedFish.check_hdd()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('908', '[TC908]RedFish 修改BIOS Value(随机修改)', 'RedFish 修改BIOS 选项(随机修改)'))
def redfish_change_value():
    try:
        assert RedFish.redfish_change_value()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('909', '[TC909]RedFish 修改BMC用户', 'RedFish 修改BMC 用户'))
def redfish_change_bmc_user():
    try:
        assert RedFish.redfish_change_bmc_user()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('910', '[TC910]RedFish 检查网卡信息', 'RedFish 检查网卡信息'))
def check_network():
    try:
        assert RedFish.check_network()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('911', '[TC911]RedFish 检查PCIE信息', 'RedFish 检查PCIE信息'))
def check_pcie():
    try:
        assert RedFish.check_pcie()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('921', '[TC921]Redfish_change_Setup_verify', 'RedFish_change_SetUp_verify'))
def redfish_change_setup_verify():
    try:
        assert RedFish.redfish_change_setup_verify()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('922', '[TC922]SetUp_change_RedFish_verify', 'SetUp_change_RedFish_verify'))
def setup_change_redfish_verify():
    try:
        assert RedFish.setup_change_redfish_verify()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('931', '[TC931]RedFish 保留升级BIOS', 'RedFish 保留升级BIOS'))
def redfish_upgrade_bios_normal(bios_mode='latest', change_part='all'):
    try:
        assert RedFish.redfish_upgrade_bios_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('932', '[TC932]RedFish 完全升级BIOS', 'RedFish 完全升级BIOS'))
def redfish_upgrade_bios_all(bios_mode='latest', change_part='all'):
    try:
        assert RedFish.redfish_upgrade_bios_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('933', '[TC933]RedFish 保留降级BIOS', 'RedFish 保留降级BIOS'))
def redfish_downgrade_bios_normal(bios_mode='previous', change_part='all'):
    try:
        assert RedFish.redfish_downgrade_bios_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('934', '[TC934]RedFish 完全降级BIOS', 'RedFish 完全降级BIOS'))
def redfish_downgrade_bios_all(bios_mode='previous', change_part='all'):
    try:
        assert RedFish.redfish_downgrade_bios_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
