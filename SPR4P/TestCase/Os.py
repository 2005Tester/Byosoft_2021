from SPR4P.Config import *
from SPR4P.BaseLib import *


# Test case ID: TC300-TC320

##########################################
# Operate System Test Cases
# TC 300-350
##########################################


# Boot to SUSE Linux from boot manager
@core.test_case(('300', '[TC300] Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux'))
def boot_to_suse():
    try:
        assert SetUpLib.boot_os_from_bm(Msg.BOOT_OPTION_SUSE)
        logging.info("OS Boot Successful")
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


# Boot to SUSE Linux from boot manager
@core.test_case(('301', '[TC301] 装备模式:Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux in Manufacture mode'))
def boot_to_suse_mfg():
    try:
        assert SetUpLib.boot_os_from_bm(Msg.BOOT_OPTION_SUSE)
        logging.info("OS Boot Successful")
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


@core.test_case(('302', '[TC302] Move UEFI SUSE Linux to first boot option', 'Move UEFI SUSE Linux to first boot option'))
def move_suse_to_first():
    try:
        assert SetUpLib.move_option_in_bootmanager(Msg.BOOT_OPTION_SUSE, 5)
        return core.Status.Pass
    except Exception:
        return core.Status.Fail

