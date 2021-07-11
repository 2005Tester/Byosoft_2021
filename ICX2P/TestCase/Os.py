import logging
from Core import SerialLib
from Core.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib
from Report import ReportGen

# Test case ID: TC300-TC320

##########################################
#         OS and Boot Test Cases         #
##########################################


# Boot to SUSE Linux from boot manager
def boot_to_suse():
    tc = ('300', '[TC300] Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    if not SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, Msg.SUSE_GRUB):
        result.log_fail()
        return
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
        result.log_fail()
        return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


# Boot to SUSE Linux from boot manager
def boot_to_suse_mfg():
    tc = ('301', '[TC301] 装备模式:Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux in Manufacture mode')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    msg = Msg.SUSE_GRUB
    if not SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, msg):
        result.log_fail()
        return
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
        result.log_fail()
        return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


def move_suse_to_first():
    tc = ('302', '[TC302] Move UEFI SUSE Linux to first boot option', 'Move UEFI SUSE Linux to first boot option')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
