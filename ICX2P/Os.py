import logging
from Core import SerialLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib
from Report import ReportGen

# Test case ID: TC300-TC320

##########################################
#         OS and Boot Test Cases         #
##########################################


# Boot to SUSE Linux from boot manager
def boot_to_suse(serial):
    tc = ('300', 'Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    suse_linux = ["SUSE Linux Enterprise\(LUN0\)"]
    msg = "Welcome to GRUB"
    if not SetUpLib.enter_menu(Key.DOWN, suse_linux, 20, msg):
        result.log_fail()
        return
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE):
        result.log_fail()
        return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


# Boot to SUSE Linux from boot manager
def boot_to_suse_mfg(serial):
    tc = ('301', '装备模式: Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux in Manufacture mode')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    suse_linux = ["SUSE Linux Enterprise\(LUN0\)"]
    msg = "Welcome to GRUB"
    if not SetUpLib.enter_menu(Key.DOWN, suse_linux, 20, msg):
        result.log_fail()
        return
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE):
        result.log_fail()
        return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


def move_suse_to_first(serial):
    tc = ('302', 'Move UEFI SUSE Linux to first boot option', 'Move UEFI SUSE Linux to first boot option')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
