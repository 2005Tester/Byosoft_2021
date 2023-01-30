import os
import re
import glob
import logging
from batf import SshLib, MiscLib, var, core
from batf.SutInit import Sut
from HY5.Config import SutConfig
from HY5.Config.PlatConfig import Key, Msg, BiosCfg
from HY5.BaseLib import SetUpLib, BmcLib, PlatMisc, Update
from batf.Report import ReportGen
from HY5.BaseLib.PlatMisc import ReleaseTest


# Test case ID: 7xx

##########################################
#            Release Test Cases          #
##########################################



def me_version_status():
    tc = ('700', '[TC700] ME_Check ME Version and status', 'ME version should be match within BIOS bin file, ME Status shoule be normal.')
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
    tc = ('701', '[TC701] Equipment mode flag check', '非装备模式BIOS设置装备模式flag, 预期设置不成功.')
    result = ReportGen.LogHeaderResult(tc)
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 10):
        BmcLib.force_reset()
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 300):
            result.log_skip()
            return
    res = Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG)
    if res:
        result.log_fail()
        return
    logging.info("Unbale to set equipment mode flag.")
    result.log_pass()
    return True

# Author: WangQingshan
# 装备模式BIOS IIO菜单需要显示IOU信息 测试
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def equip_iou_not_hidden():
    tc = ('703', '[TC703] BIOS bin with equipment mode, IOU not hidden', 'BIOS bin with equipment mode, IOU not hidden')
    result = ReportGen.LogHeaderResult(tc)
    iou_info = "IOU\d \(IIO PCIe Port \d\)\s+x(?:16|8|4)"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
        for cpu in range(SutConfig.SysCfg.CPU_CNT):
            assert SetUpLib.enter_menu(Key.DOWN, [f"CPU {cpu+1} Configuration"], 10, iou_info)
            SetUpLib.send_keys([Key.ESC])
        result.log_pass()
    except AssertionError:
        result.log_fail()


# Author: WangQingshan
# Chipsec工具检查是否有fail或warning
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def chipsec_test():
    tc = ('704', '[TC704] Chipsec Test', 'The version is scanned by chipsec without warning')
    result = ReportGen.LogHeaderResult(tc)

    adddc_en = [[Msg.MEMORY_CONFIG, Msg.MEMORY_RAS_CFG], "ADDDC Sparing", "Disabled"]
    warnning_ignored = [
        "WARNING: chipsec.modules.biosguard",
        "WARNING: chipsec.modules.common.debugenabled",
        "WARNING: chipsec.modules.common.uefi.access_platform",
        "WARNING: chipsec.modules.common.uefi.s3bootscript"]

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG], 15, Msg.PROCESSOR_CONFIG)

        assert SetUpLib.enter_menu(Key.DOWN, adddc_en[0], 15, "Memory RAS Configuration Setup")
        assert SetUpLib.set_option_value(adddc_en[1], adddc_en[2], key=Key.UP)
        SetUpLib.send_keys([Key.ESC]*len(adddc_en[0]))

        assert SetUpLib.save_without_reset()

        assert SetUpLib.back_to_front_page("Administer Secure Boot")
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu(Key.UP, ["Secure Boot Factory Options"], 5, "Erase all Secure Boot Settings")
        assert SetUpLib.locate_option(Key.DOWN, ["Restore Secure Boot to Factory Settings"], 3)
        SetUpLib.send_keys([Key.ENTER])
        SetUpLib.send_keys([Key.Y], delay=15)
        SetUpLib.send_keys([Key.ESC])
        assert SetUpLib.locate_option(Key.DOWN, ["Attempt Secure Boot", "\[X\]"], 5)
        SetUpLib.send_keys([Key.ENTER]*2 + Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert SshLib.interaction(Sut.OS_SSH, [f"cd {SutConfig.Env.CHIPSEC_PATH}\n", "python3 chipsec_main.py > chipsec_log.txt"], ["", ""])
        chipsec_log = os.path.join(SutConfig.Env.LOG_DIR, "chipsec_log.txt")
        assert SshLib.sftp_download_file(Sut.OS_SFTP, f"{SutConfig.Env.CHIPSEC_PATH}/chipsec_log.txt", chipsec_log)
        assert os.path.exists(chipsec_log)
        with open(chipsec_log) as ch_log:
            fail_cnt = 0
            warn_cnt = 0
            for line in ch_log.readlines():
                if re.search("WARNING: chipsec\.", line, re.I) and not any(ig in line for ig in warnning_ignored):
                    warn_cnt += 1
                    logging.info(line.strip())
                elif re.search("FAILED: chipsec\.", line, re.I):
                    fail_cnt += 1
                    logging.info(line.strip())
        assert (not fail_cnt) and (not warn_cnt), f"Chipsec test: {fail_cnt} failed, {warn_cnt} warnings"
        logging.info("** Chipsec test pass: No any unexpected fail or warning")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    # finally:
    #     BmcLib.clear_cmos()

# Boot to SUSE Linux from boot manager
def boot_to_suse():
    tc = ('705', '[TC705] Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    if not SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, Msg.SUSE_GRUB):
        result.log_fail()
        return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True

def hpm_upgrade_test():
    tc = ('904', '[TC904] HPM升级保持配置不变', "HPM升级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc)

    new_branch = var.get('branch')
    old_branch = PlatMisc.last_release(new_branch)
    if not ReleaseTest.old_bios:
        ReleaseTest.old_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, old_branch)
    if not ReleaseTest.new_bios:
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch)
    new_path_local = os.path.join(SutConfig.Env.BIOS_PATH, new_branch)
    new_hpm_local = glob.glob(os.path.join(new_path_local, "*.hpm"))
    flash_latest = False

    try:
        assert Update.update_bios(ReleaseTest.old_bios)
        flash_latest = False
        SetUpLib.update_default_password()
        SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.flash_local_hpm(new_hpm_local[0])
        flash_latest = True
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(ReleaseTest.new_bios)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)


def hpm_downgrade_test():
    tc = ('905', '[TC905] HPM降级保持配置不变', "HPM降级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc)

    new_branch = var.get('branch')
    if not ReleaseTest.new_bios:
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch)
    old_branch = PlatMisc.last_release(new_branch)
    old_path_local = os.path.join(SutConfig.Env.BIOS_PATH, old_branch)
    old_hpm_local = glob.glob(os.path.join(old_path_local, "*.hpm"))
    flash_latest = False

    try:
        assert Update.update_bios(ReleaseTest.new_bios)
        flash_latest = True
        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.flash_local_hpm(old_hpm_local[0])
        flash_latest = False
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(ReleaseTest.new_bios)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
