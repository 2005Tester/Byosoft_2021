import os
import glob
import logging
from Core import SshLib, MiscLib
from Core.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import BmcLib, SetUpLib, Update, PlatMisc
from Report import ReportGen
from Common.RedfishLib import Redfish


# Test case ID: 9xx

##########################################
#            Release Test Cases          #
##########################################

def me_version_status():
    tc = ('901', '[TC901] ME_Check ME Version and status', 'ME version should be match within BIOS bin file, ME Status shoule be normal.')
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
def equip_mode_flag_check():
    tc = ('902', '[TC902] Equipment mode flag check', '非装备模式BIOS设置装备模式flag, 预期设置不成功.')
    result = ReportGen.LogHeaderResult(tc)
    res = Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG)
    if res:
        result.log_fail()
        return
    logging.info("Unbale to set equipment mode flag.")
    result.log_pass()
    return True


# 装备模式BIOS version = 5.xx.
def equip_mode_version_check():
    tc = ('903', '[TC903] 装备模式: Equipment mode version check', '装备模式版本号为5.xx.')
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


def hpm_upgrade_test(new_branch):
    tc = ('904', '[TC904] HPM升级保持配置不变', "HPM升级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)

    old_branch = PlatMisc.last_release(new_branch)
    old_bin_download = Update.get_test_image(SutConfig.LOG_DIR, old_branch, 'debug-build')
    new_bin_download = Update.get_test_image(SutConfig.LOG_DIR, new_branch, 'debug-build')
    new_path_local = os.path.join(SutConfig.BIOS_PATH, new_branch)
    new_hpm_local = glob.glob(os.path.join(new_path_local, "*.hpm"))
    flash_latest = False

    try:
        assert Update.update_bios(old_bin_download[0])
        flash_latest = False
        SetUpLib.update_default_password()
        SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.flash_local_hpm(new_hpm_local[0])
        flash_latest = True
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(new_bin_download)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)


def hpm_downgrade_test(new_branch):
    tc = ('905', '[TC905] HPM降级保持配置不变', "HPM降级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)

    new_bin_download = Update.get_test_image(SutConfig.LOG_DIR, new_branch, 'debug-build')
    old_branch = PlatMisc.last_release(new_branch)
    old_path_local = os.path.join(SutConfig.BIOS_PATH, old_branch)
    old_hpm_local = glob.glob(os.path.join(old_path_local, "*.hpm"))
    flash_latest = False

    try:
        assert Update.update_bios(new_bin_download)
        flash_latest = True
        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.flash_local_hpm(old_hpm_local[0])
        flash_latest = False
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(new_bin_download)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)


# 比较BIOS升降级时，是否会产生新的FDMlog错误记录
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def compare_fdm_log(new_branch):
    tc = ('906', '[TC906] Compare FDM Log Size', "Compare FDM Log size with previous BIOS version")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)

    old_branch = PlatMisc.last_release(new_branch)
    new_img = Update.get_test_image(SutConfig.LOG_DIR, new_branch, 'debug-build')
    old_img = Update.get_test_image(SutConfig.LOG_DIR, old_branch, 'debug-build')
    flash_latest = False

    def read_fdm(bios_img, test_flag):
        try:
            assert Update.update_bios(bios_img), "update latest bios fail"
            assert SetUpLib.update_default_password(), "update_default_password fail"
            assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5), "move_boot_option_up fail"
            dump_path = os.path.join(SutConfig.LOG_DIR, f"TC{tc[0]}/{test_flag}")
            if not os.path.exists(dump_path):
                os.makedirs(dump_path)
            assert BmcLib.bmc_dumpinfo(path=dump_path, name="dump", uncom=True)
            assert os.path.isfile(os.path.join(dump_path, rf"dump\dump_info\LogDump\fdm_log")), "fdmlog not found"
            with open(os.path.join(dump_path, r"dump\dump_info\LogDump\fdm_log"), "r") as fdm_log:
                return fdm_log.read()
        except Exception as err:
            logging.info(err)
            return 0

    try:
        # Flash latest release img
        latest = read_fdm(new_img, "latest")
        assert latest != 0, "Exception: Read latest fdmlog"
        flash_latest = True
        # Flash last release img
        downgrade = read_fdm(old_img, "downgrade")
        assert downgrade != 0, "Exception: Read downgrade fdmlog"
        flash_latest = False
        assert latest == downgrade, "FDM LOG if different after BIOS downgrade"
        # Flash latest release img back again
        upgrade = read_fdm(new_img, "upgrade")
        assert upgrade != 0, "Exception: Read upgrade fdmlog"
        flash_latest = True
        assert downgrade == upgrade, "FDM LOG if different after BIOS upgrade"
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(new_img)


# 检查BMC是否记录异常告警信息
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def check_bmc_warning():
    tc = ('907', '[TC907] iBMC warning info in web', "Check no any warning info")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)
    check_result = BmcLib.bmc_warning_check()
    if check_result is None:
        result.log_skip()
        return
    if not check_result:
        result.log_fail()
        return
    result.log_pass()
    return True


# Author: WangQingshan
# 检查新旧版本BIOS的Registry.json文件是否一致
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def registry_check(new_branch):
    tc = ('908', '[TC908] Compare registry.json file with previous version', "Compare registry.json file with previous version")
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)

    old_branch = PlatMisc.last_release(new_branch)
    old_img = Update.get_test_image(SutConfig.LOG_DIR, old_branch, 'debug-build')
    new_img = Update.get_test_image(SutConfig.LOG_DIR, new_branch, 'debug-build')
    rfish = Redfish(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)
    flash_latest = False

    try:
        # old branch bios image registry dump
        assert Update.update_bios(old_img)
        flash_latest = False
        logging.info("dump old registry")
        old_registry = rfish.registry_dump()
        # new branch bios image registry dump
        assert Update.update_bios(new_img)
        flash_latest = True
        logging.info("dump new registry")
        new_registry = rfish.registry_dump()
        assert old_registry == new_registry, "Check old registry is different from new registry"
        logging.info("Check old registry is same with new registry")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(new_img)
