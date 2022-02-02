import logging
import time
from batf.Report import ReportGen
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Base import Ipmitool,IpmBootNormal,IpmBootSpecific
from batf import core



'''
Ipmitool  case 编号:501~600
'''



@core.test_case(('501','[TC501]UEFI PXE ONCE Normal','UEFI模式下IPMITOOL PXE启动一次(normal)'))
def uefi_pxe_once_nor():
    try:
        assert IpmBootNormal.uefi_pxe_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('502','[TC502]UEFI SETUP ONCE Normal','UEFI模式下IPMITOOL Setup启动一次(normal)'))
def uefi_setup_once_nor():

    try:
        assert IpmBootNormal.uefi_setup_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('503','[TC503]UEFI HDD ONCE Normal','UEFI模式下IPMITOOL 硬盘启动一次(normal)'))
def ufei_hdd_once_nor():

    try:
        assert IpmBootNormal.uefi_hdd_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('504','[TC504]UEFI USB ONCE Normal','UEFI模式下IPMITOOL USB启动一次(normal)'))
def uefi_usb_once_nor():
    try:
        assert IpmBootNormal.uefi_usb_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('506','[TC506]UEFI PXE ALWAYS Normal','UEFI模式下IPMITOOL 永久启动到PXE(normal)'))
def uefi_pxe_always_nor():
    try:
        assert IpmBootNormal.uefi_pxe_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('507','[TC507]UEFI SETUP ALWAYS Normal','UEFI模式下IPMITOOL 永久启动到SETUP(normal)'))
def uefi_setup_always_nor():
    try:
        assert IpmBootNormal.uefi_setup_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('508','[TC508]UEFI HDD ALWAYS Normal','UEFI模式下IPMITOOL 永久启动到硬盘(normal)'))
def uefi_hdd_always_nor():
    try:
        assert IpmBootNormal.uefi_hdd_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('509','[TC509]UEFI USB ALWAYS Normal','UEFI模式下IPMITOOL 永久启动到USB(normal)'))
def uefi_usb_always_nor():

    try:
        assert IpmBootNormal.uefi_usb_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('510','[TC510]UEFI ODD ALWAYS Normal','UEFI模式下IPMITOOL 永久启动到ODD(normal)'))
def uefi_odd_always_nor():
    try:
        assert IpmBootNormal.uefi_odd_always_nor()
        assert SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        BmcLib.power_off()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        BmcLib.power_off()
        logging.error(e)
        return core.Status.Fail

    
    
@core.test_case(('511','[TC511]Legacy PXE ONCE Normal','Legacy模式下IPMITOOL启动到PXE一次(normal)'))
def legacy_pxe_once_nor():
    try:
        assert IpmBootNormal.legacy_pxe_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('512','[TC512]Legacy Setup ONCE Normal','Legacy模式下IPMITOOL启动到Setup一次(normal)'))
def legacy_setup_once_nor():
    
    try:
        assert IpmBootNormal.legacy_setup_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('513','[TC513]Legacy USB ONCE Normaal','Legacy模式下IPMITOOL启动到USB一次(normal)'))
def legacy_usb_once_nor():

    try:
        assert IpmBootNormal.legacy_usb_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('514','[TC514]Legacy HDD ONCE Normal','Legacy模式下IPMITOOL启动到HDD一次(normal)'))
def legacy_hdd_once_nor():

    try:
        assert IpmBootNormal.legacy_hdd_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('516','[TC516]Legacy PXE ALWAYS Normal','Legacy模式下IPMITOOL永久启动到PXE(normal)'))
def legacy_pxe_always_nor():

    try:
        assert IpmBootNormal.legacy_pxe_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('517','[TC517]Legacy SETUP ALWAYS Normal','Legacy模式下IPMITOOL永久启动到SETUP(normal)'))
def legacy_setup_always_nor():
    try:
        assert IpmBootNormal.legacy_setup_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('518','[TC518]Legacy USB ALWAYS','Legacy模式下IPMITOOL永久启动到USB(normal)'))
def legacy_usb_always_nor():

    try:
        assert IpmBootNormal.legacy_usb_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('519','[TC519]Legacy HDD ALWAYS Normal','Legacy模式下IPMITOOL永久启动到HDD(normal)'))
def legacy_hdd_always_nor():

    try:
        assert IpmBootNormal.legacy_hdd_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('520','[TC520]Legacy ODD ALWAYS Normal','Legacy模式下IPMITOOL永久启动到ODD(normal)'))
def legacy_odd_always_nor():

    try:
        assert IpmBootNormal.legacy_odd_always_nor()
        assert SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('521', '[TC521]UEFI PXE ONCE Specific', 'UEFI模式下IPMITOOL PXE启动一次(specific)'))
def uefi_pxe_once_spe():
    try:
        assert IpmBootSpecific.uefi_pxe_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('522', '[TC522]UEFI SETUP ONCE Specific', 'UEFI模式下IPMITOOL Setup启动一次(specific)'))
def uefi_setup_once_spe():
    try:
        assert IpmBootSpecific.uefi_setup_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('523', '[TC523]UEFI HDD ONCE Specific', 'UEFI模式下IPMITOOL 硬盘启动一次(specific)'))
def ufei_hdd_once_spe():
    try:
        assert IpmBootSpecific.uefi_hdd_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('524', '[TC524]UEFI USB ONCE Specific', 'UEFI模式下IPMITOOL USB启动一次(specific)'))
def uefi_usb_once_spe():

    try:
        assert IpmBootSpecific.uefi_usb_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('526', '[TC526]UEFI PXE ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到PXE(specific)'))
def uefi_pxe_always_spe():

    try:
        assert IpmBootSpecific.uefi_pxe_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('527', '[TC527]UEFI SETUP ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到SETUP(specific)'))
def uefi_setup_always_spe():

    try:
        assert IpmBootSpecific.uefi_setup_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('528', '[TC528]UEFI HDD ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到硬盘(specific)'))
def uefi_hdd_always_spe():

    try:
        assert IpmBootSpecific.uefi_hdd_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('529', '[TC529]UEFI USB ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到USB(specific)'))
def uefi_usb_always_spe():

    try:
        assert IpmBootSpecific.uefi_usb_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('530', '[TC530]UEFI ODD ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到ODD(specific)'))
def uefi_odd_always_spe():

    try:
        assert IpmBootSpecific.uefi_odd_always_spe()
        assert SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('531', '[TC531]Legacy PXE ONCE Specific', 'Legacy模式下IPMITOOL启动到PXE一次(specific)'))
def legacy_pxe_once_spe():

    try:
        assert IpmBootSpecific.legacy_pxe_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('532', '[TC532]Legacy Setup ONCE Specific', 'Legacy模式下IPMITOOL启动到Setup一次(specific)'))
def legacy_setup_once_spe():

    try:
        assert IpmBootSpecific.legacy_setup_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('533', '[TC533]Legacy USB ONCE Specific', 'Legacy模式下IPMITOOL启动到USB一次(specific)'))
def legacy_usb_once_spe():

    try:
        assert IpmBootSpecific.legacy_usb_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('534', '[TC534]Legacy HDD ONCE Specific', 'Legacy模式下IPMITOOL启动到HDD一次(specific)'))
def legacy_hdd_once_spe():

    try:
        assert IpmBootSpecific.legacy_hdd_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('536', '[TC536]Legacy PXE ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到PXE(specific)'))
def legacy_pxe_always_spe():

    try:
        assert IpmBootSpecific.legacy_pxe_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('537', '[TC537]Legacy SETUP ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到SETUP(specific)'))
def legacy_setup_always_spe():
    try:
        assert IpmBootSpecific.legacy_setup_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('538', '[TC538]Legacy USB ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到USB(specific)'))
def legacy_usb_always_spe():

    try:
        assert IpmBootSpecific.legacy_usb_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('539', '[TC539]Legacy HDD ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到HDD(specific)'))
def legacy_hdd_always_spe():

    try:
        assert IpmBootSpecific.legacy_hdd_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('540', '[TC540]Legacy ODD ALWAYS Sepcific', 'Legacy模式下IPMITOOL永久启动到ODD(specific)'))
def legacy_odd_always_spe():

    try:
        assert IpmBootSpecific.legacy_odd_always_spe()
        assert SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        time.sleep(5)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(2)
        SetUpLib.open_session()  # 打开链接
        time.sleep(2)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('541','[TC541]FRB2 Watchdog','FRB2 Watchdog'))
def frb2_watchdog():

    try:
        assert Ipmitool.frb2_watchdog()

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('542','[TC542]OS Watchdog','OS Watchdog'))
def os_watchdog():

    try:
        assert Ipmitool.os_watchdog()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('543','[TC543]Power Loss','电源丢失策略'))
def power_loss():

    try:
        assert Ipmitool.power_loss()
        BmcLib.power_off()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('544','[TC544]OEM','OEM命令获取和修改Setup选项'))
def oem():

    try:
        assert Ipmitool.oem()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('545','[TC545]BMC User Test','BMC User Test'))
def bmc_user():
    try:
        assert Ipmitool.bmc_user()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('546','[TC546]SOL','板载SOL'))
def sol():
    try:
        assert Ipmitool.sol()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('547','[TC547]BMC System Log','BMC 系统日志'))
def bmc_system_log():
    try:
        assert Ipmitool.bmc_system_log()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

@core.test_case(('548','[TC548]FRU Message Confirm','FRU 信息验证'))
def fru():
    try:
        assert Ipmitool.fru()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail