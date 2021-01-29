import logging
from ICX2P import SutConfig
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib
from Common import Misc


# Boot to SUSE Linux from boot manager
def boot_to_suse(serial, ssh):
    tc = ('300', 'Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux')
    result = Misc.LogHeaderResult(tc, serial)
    if not SetUpLib.boot_to_bootmanager(serial, ssh):
        result.log_fail()
        return
    suse_linux = ["SUSE Linux Enterprise\(LUN0\)"]
    msg = Msg.BIOS_BOOT_COMPLETE
    if not SetUpLib.enter_menu(serial, Key.DOWN, suse_linux, 8, msg):
        result.log_fail()
        return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True