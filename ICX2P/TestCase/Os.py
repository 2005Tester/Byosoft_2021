import logging
from Core import SerialLib, SshLib, MiscLib
from Core.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib, PlatMisc, BmcLib
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
    # if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
    #     result.log_fail()
    #     return
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
    # if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
    #     result.log_fail()
    #     return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


def move_suse_to_first():
    tc = ('302', '[TC302] Move UEFI SUSE Linux to first boot option', 'Move UEFI SUSE Linux to first boot option')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


# Author: Fubaolin
# 多次执行装备模式脚本测试
# Precondition:EquipmentMode,linux-OS
# OnStart: NA
# OnComplete: NA
def EquipmentModeFlag_test():
    tc = ('303', '[TC303] Equipment_Mode_007', '多次执行装备模式脚本测试')
    result = ReportGen.LogHeaderResult(tc)
    n = 0
    m = 0
    assert BmcLib.force_reset()
    try:
        for n in range(5):
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
            for m in range(10):
                res = Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG)
                if not res:
                    result.log_fail()
                    logging.info("**set equipment mode flag fail.")
                    return
            assert BmcLib.force_reset()
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()