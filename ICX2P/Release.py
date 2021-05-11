import os
import glob
import logging
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import BmcLib, SetUpLib, Update, icx2pAPI
from Report import ReportGen


# Test case ID: 9xx

##########################################
#            Release Test Cases          #
##########################################

def me_version_status():
    tc = ('901', 'ME_Check ME Version and status', 'ME version should be match within BIOS bin file, ME Status shoule be normal.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    if not SetUpLib.enter_menu(Key.DOWN, ["Server ME Configuration"], 20, "General ME Configuration"):
        result.log_fail()
        return
    me_info = ['Oper. Firmware Version\s+{0}'.format(Msg.ME_VERSION), 
               'Recovery Firmware Version\s+{0}'.format(Msg.ME_VERSION),
               'Current State\s+Operational']
    if not SetUpLib.verify_info(me_info, 13):
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


# 装备模式BIOS version = 5.xx.
def equip_mode_version_check():
    tc = ('903', '装备模式: Equipment mode version check', '装备模式版本号为5.xx.')
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)
    mfg_version = ['BIOS Revision\s+5.[0-9]{2}']
    if not SetUpLib.boot_to_bios_config():
        result.log_fail(capture=True)
        return
    logging.info("Verify bios version.")
    if not SetUpLib.verify_info(mfg_version, 30):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def hpm_upgrade_test(serial, ssh_bmc, sftp_bmc, unitool):
    tc = ('904', 'HPM升级保持配置不变', "HPM升级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)

    bios_list = sorted(os.listdir(SutConfig.BIOS_PATH), reverse=True)
    new_path = os.path.join(SutConfig.BIOS_PATH, bios_list[0])
    old_path = os.path.join(SutConfig.BIOS_PATH, bios_list[1])
    old_bin = glob.glob(os.path.join(old_path, "*.bin"))
    new_hpm = glob.glob(os.path.join(new_path, "*.hpm"))

    try:
        assert Update.update_bios(old_bin[0])
        assert icx2pAPI.ping_sut()
        assert unitool.write(**SutConfig.BiosCfg.HPM_KEEP)
        assert Update.flash_local_hpm(serial, ssh_bmc, sftp_bmc, new_hpm[0])
        assert icx2pAPI.ping_sut()
        assert unitool.check(**SutConfig.BiosCfg.HPM_KEEP)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


def hpm_downgrade_test(serial, ssh_bmc, sftp_bmc, unitool):
    tc = ('905', 'HPM降级保持配置不变', "HPM降级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)

    bios_list = sorted(os.listdir(SutConfig.BIOS_PATH), reverse=True)
    new_path = os.path.join(SutConfig.BIOS_PATH, bios_list[0])
    old_path = os.path.join(SutConfig.BIOS_PATH, bios_list[1])
    new_bin = glob.glob(os.path.join(new_path, "*.bin"))
    old_hpm = glob.glob(os.path.join(old_path, "*.hpm"))

    try:
        assert Update.update_bios(new_bin[0])
        assert icx2pAPI.ping_sut()
        assert unitool.write(**SutConfig.BiosCfg.HPM_KEEP)
        assert Update.flash_local_hpm(serial, ssh_bmc, sftp_bmc, old_hpm[0])
        assert icx2pAPI.ping_sut()
        assert unitool.check(**SutConfig.BiosCfg.HPM_KEEP)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
