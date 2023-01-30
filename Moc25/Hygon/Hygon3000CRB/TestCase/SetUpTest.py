import logging
import time
from batf.Report import ReportGen
from Hygon3000CRB.Config.PlatConfig import Key
from Hygon3000CRB.BaseLib import BmcLib,SetUpLib
from Hygon3000CRB.Base import SetUp
from Hygon3000CRB.Config import SutConfig
from batf import core



'''
SetUp case 编号: 601~700
'''



@core.test_case(('601','[TC601]Interface Information','界面信息'))
def Interface_information():
    try:
        assert SetUp.Interface_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('602','[TC602]Onboard Ethernet Controller','修改板载网卡配置'))
def Onboard_Ethernet_Controller():
    try:
        assert SetUp.Onboard_Ethernet_Controller()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('603','[TC603]SVM','SVM'))
def svm():
    try:
        assert SetUp.svm()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('604','[TC604]SR-IOV','SR-IOV'))
def sriov():
    try:
        assert SetUp.sriov()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('605','[TC605]USB Mass Storage Support','USB存储设备支持'))
def usb_mass_storage_support():
    try:
        assert SetUp.usb_mass_storage_support()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('606','[TC606]USB Port Configuration','USB端口配置'))
def usb_port_configuration():
    try:
        assert SetUp.usb_port_configuration()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('607','[TC607]Memory Speed','内存频率'))
def memory_speed():
    try:
        assert SetUp.memory_speed()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('608','[TC608]HDD Bind','硬盘绑定'))
def HDD_Bind():
    try:
        assert SetUp.HDD_bind()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.boot_to_page('Set Administrator Password')
        SetUpLib.locate_option(Key.DOWN, ['HDD Bind'], 9)
        SetUpLib.send_key(Key.ENTER)
        SetUpLib.select_option_value(Key.DOWN, ['HDD Bind'], Key.DOWN, 'Unbind', 5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('609','[TC609]IOMMU','IOMMU'))
def iommu():
    try:
        assert SetUp.iommu()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('610','[TC610]Secure Boot','安全启动'))
def secure_boot():
    try:
       assert SetUp.secure_boot()
       return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('611','[TC611]User Wait Time','用户等待时间'))
def user_wait_time():
    try:
        assert SetUp.user_wait_time()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('612', '[TC612]SATA Controller Configuration', 'SATA 控制器配置'))
def sata_controller():
    try:
        assert SetUp.sata_controller()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('613','[TC613]Save Change by ESC','通过ESC键保存设置'))
def save_change_esc():
    try:
        assert SetUp.save_change_esc()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('614','[TC614]Save And Exit','保存并且退出'))
def save_and_exit():
    try:
        assert SetUp.save_and_exit()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('615','[TC615]SATA\/PCIE Switch','SATA\/PCIE切换'))
def SATA_or_PCIE_Switch():
    try:
        assert SetUp.SATA_or_PCIE_Switch()
        return core.Status.Pass
    except Exception as e:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
        assert SetUpLib.locate_option(Key.DOWN, ['SATA\/PCIE Switch'], 20)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.select_option_value(Key.DOWN, ['J112'], Key.DOWN, 'SATA', 4)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        logging.error(e)
        return core.Status.Fail