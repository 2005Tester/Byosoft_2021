import logging
import time
from batf.Report import ReportGen
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Base import SetUp
from InspurStorage.Config import SutConfig
from batf import core



'''
SetUp case 编号: 601~700
'''



@core.test_case(('602','[TC602]BIOS Default Value','BIOS 默认值检查'))
def bios_default_value():
    try:
        assert SetUp.bios_default_value()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('603','[TC603]Console_Direction','串口重定向终端类型：VT100，UTF8 ，测试'))
def console_direction():
    try:
        assert SetUp.console_direction()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('604','[TC604]USB Mass Storage Support','USB存储设备支持'))
def usb_mass_storage_support():
    try:
        assert SetUp.usb_mass_storage_support()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_STORAGE, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('605','[TC605]USB Port Configuration','USB端口配置'))
def usb_port_configuration():
    try:
        assert SetUp.usb_port_configuration()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('606','[TC606]Secure Boot','安全启动'))
def secure_boot():
    try:
       assert SetUp.secure_boot()
       return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.CLOSE_SECURE_BOOT, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.Y)
        time.sleep(25)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('607','[TC607]Network Boot','网络引导'))
def network_boot():
    try:
        assert SetUp.network_boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

    

@core.test_case(('608','[TC608]User Wait Time','用户等待时间'))
def user_wait_time():
    try:
        assert SetUp.user_wait_time()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('609','[TC609]Quiet Boot','安静启动'))
def quiet_boot():
    try:
        assert SetUp.quiet_boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('610','[TC610]Close KVM Message','关闭进入OS后的KVM打印信息'))
def close_kvm_msg():
    try:
        assert SetUp.close_kvm_msg()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('611','[TC611]IOMMU','IOMMU'))
def iommu():
    try:
        assert SetUp.iommu()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('612','[TC612]Save Change by ESC','通过ESC键保存设置'))
def save_change_esc():
    try:
        assert SetUp.save_change_esc()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('613','[TC613]Save And Exit','保存并且退出'))
def save_and_exit():
    try:
        assert SetUp.save_and_exit()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('614','[TC614]Load Default','恢复初始值'))
def load_default():
    try:
        assert SetUp.load_default()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('615','[TC615]Load Default By F9','F9快捷键恢复初始值'))
def load_default_f9():
    try:
        assert SetUp.load_default_f9()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('616','[TC616]Reboot System','重启'))
def reboot():
    try:
        assert SetUp.reboot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('617', '[TC617]TPM', 'TPM'))
def tpm():
    try:
        assert SetUp.tpm()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('618', '[TC618]Update Unsign BIOS', '更新未签名的BIOS'))
def update_unsign_bios():
    try:
        assert SetUp.update_unsign_bios()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('619', '[TC619]AER Control', 'AER 控制选项'))
def aer_control():
    try:
        assert SetUp.aer_control()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

