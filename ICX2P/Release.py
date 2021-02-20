import logging
from ICX2P.SutConfig import Key, Msg
from ICX2P import SutConfig
from ICX2P.BaseLib import icx2pAPI, SetUpLib
from Report import ReportGen


# Test case ID: 9xx

##########################################
#            Release Test Cases          #
##########################################

def me_version_status(serial, ssh):
    tc = ('901', 'ME_Check ME Version and status', 'ME version should be match within BIOS bin file, ME Status shoule be normal.')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    if not SetUpLib.enter_menu(serial, Key.DOWN, ["Server ME Configuration"], 20, "General ME Configuration"):
        result.log_fail()
        return
    me_info = ['Oper. Firmware Version\s+{0}'.format(Msg.ME_VERSION), 
               'Recovery Firmware Version\s+{0}'.format(Msg.ME_VERSION),
               'Current State\s+Operational']
    if not SetUpLib.verify_info(serial, Key.DOWN, me_info, 13):
        result.log_fail()
        return
    logging.info("ME Version and status verified.")
    result.log_pass()
    return True


def legacy_boot(serial, ssh):
#    SetUpLib.enable_legacy_boot(serial, ssh)
    SetUpLib.disable_legacy_boot(serial, ssh)
