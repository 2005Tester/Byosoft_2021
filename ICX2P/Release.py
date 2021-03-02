import logging
from ICX2P.SutConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib
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


# 非装备模式BIOS设置装备模式flag, 预期设置不成功.
def equip_mode_flag_check(unitool):
    tc = ('902', 'Equipment mode flag check', '非装备模式BIOS设置装备模式flag, 预期设置不成功.')
    result = ReportGen.LogHeaderResult(tc)
    res = unitool.set_config(BiosCfg.EQUIP_FLAG)
    if res:
        result.log_fail()
        return
    logging.info("Unbale to set equipment mode flag.")
    result.log_pass()
    return True


def legacy_boot(serial, ssh):
    # SetUpLib.enable_legacy_boot(serial, ssh)
    SetUpLib.disable_legacy_boot(serial, ssh)

