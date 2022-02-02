import logging, os
from batf import SerialLib, SshLib, MiscLib, core
from batf.SutInit import Sut
from SPR4P.Config import SutConfig
from SPR4P.Config.PlatConfig import Key, Msg, BiosCfg
from SPR4P.BaseLib import SetUpLib, PlatMisc, BmcLib
from batf.Report import ReportGen
from SPR4P.TestCase import UpdateBIOS

# Test case ID: TC300-TC320

##########################################
#         OS and Boot Test Cases         #
##########################################

# function Module : 開啓全打印重啓后，在串口中查找str_flag
def EquipmentModeFlag_ser_log(path,str_flag):
    with open(path, 'r') as r:
        lines = [line.strip('\n') for line in r.readlines() if line.strip()]    #去掉空行和換行符
        if str_flag in lines:
            logging.info("**{} is found ".format(str_flag))
            return True
        else:
            return False

# Boot to SUSE Linux from boot manager
@core.test_case(('300', '[TC300] Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux'))
def boot_to_suse():
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, Msg.SUSE_GRUB)
        # assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
        logging.info("OS Boot Successful")
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


# Boot to SUSE Linux from boot manager
@core.test_case(('301', '[TC301] 装备模式:Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux in Manufacture mode'))
def boot_to_suse_mfg():
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, Msg.SUSE_GRUB)
        # assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
        logging.info("OS Boot Successful")
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


@core.test_case(('302', '[TC302] Move UEFI SUSE Linux to first boot option', 'Move UEFI SUSE Linux to first boot option'))
def move_suse_to_first():
    try:
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5)
        return core.Status.Pass
    except Exception:
        return core.Status.Fail

