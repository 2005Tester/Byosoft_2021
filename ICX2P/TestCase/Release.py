import os
import re
import glob
import logging
import filecmp
from batf import SshLib, MiscLib, var, core
from batf.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib, Update, PlatMisc, BmcLib
from ICX2P.BaseLib.PlatMisc import ReleaseTest
from batf.Report import ReportGen
from ICX2P.TestCase import UpdateBIOS

# Test case ID: 9xx

##########################################
#            Release Test Cases          #
##########################################

def _update_bios_img(bios_branch):
    img = Update.get_test_image(SutConfig.Env.LOG_DIR, bios_branch, 'debug-build')
    try:
        assert Update.update_bios(img), 'update bios failed'
        assert SetUpLib.update_default_password(), 'update bios pwd failed'
        assert SetUpLib.boot_suse_from_bm(), 'boot to suse failed'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY), 'ping os ip failed'
        return True
    except Exception as e:
        logging.error(e)
        return False

def bios_parallel_flash():
    tc = ('900', '[TC900] Parallel flash', "Check BIOS version under setup and BMC Web")
    result = ReportGen.LogHeaderResult(tc)
    release_branch = var.get("branch")
    try:
        img = Update.get_test_image(SutConfig.Env.LOG_DIR, release_branch, 'debug-build')
        assert Update.update_bios(img)
        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail(capture=True)


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


# 装备模式BIOS version = 5.xx.
def equip_mode_version_check():
    tc = ('903', '[TC903] 装备模式: Equipment mode version check', '装备模式版本号为5.xx.')
    result = ReportGen.LogHeaderResult(tc)
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


def hpm_upgrade_test():
    tc = ('904', '[TC904] HPM升级保持配置不变', "HPM升级BIOS后，原来设置的非默认BIOS设置不变")
    result = ReportGen.LogHeaderResult(tc)

    new_branch = var.get('branch')
    old_branch = SutConfig.Env.PREVIOUS_BRANCH
    if not ReleaseTest.old_bios:
        ReleaseTest.old_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, old_branch, 'debug-build')
    if not ReleaseTest.new_bios:
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch, 'debug-build')
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
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch, 'debug-build')
    old_branch = SutConfig.Env.PREVIOUS_BRANCH
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


# 比较BIOS升降级时，是否会产生新的FDMlog错误记录
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def compare_fdm_log():
    tc = ('906', '[TC906] Compare FDM Log Size', "Compare FDM Log size with previous BIOS version")
    result = ReportGen.LogHeaderResult(tc)

    new_branch = var.get('branch')
    old_branch = SutConfig.Env.PREVIOUS_BRANCH
    if not ReleaseTest.old_bios:
        ReleaseTest.old_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, old_branch, 'debug-build')
    if not ReleaseTest.new_bios:
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch, 'debug-build')
    flash_latest = False

    def read_fdm(bios_img, test_flag):
        try:
            assert Update.update_bios(bios_img), "update latest bios fail"
            assert SetUpLib.update_default_password(), "update_default_password fail"
            assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5), "move_boot_option_up fail"
            _dump_path = os.path.join(SutConfig.Env.LOG_DIR, f"TC{tc[0]}/{test_flag}")
            _dump_dir = BmcLib.bmc_dumpinfo(path=_dump_path, name="dump", uncom=True)
            return PlatMisc.read_bmc_dump_log(_dump_dir, "dump_info/LogDump/fdm_log")
        except Exception as err:
            logging.info(err)
            return 0
    # main test process
    try:
        # dump latest release fdmlog
        dump_path = os.path.join(SutConfig.Env.LOG_DIR, f"TC{tc[0]}/latest")
        dump_dir = BmcLib.bmc_dumpinfo(path=dump_path, name="dump", uncom=True)
        latest = PlatMisc.read_bmc_dump_log(dump_dir, "dump_info/LogDump/fdm_log")
        # Flash last release img
        downgrade = read_fdm(ReleaseTest.old_bios, "downgrade")
        assert downgrade != 0, "Exception: Read downgrade fdmlog"
        flash_latest = False
        logging.info('Mark Downgrade Flash BIOS as already tested')
        ReleaseTest.downgrade_tested = True
        logging.info('Dump "registry.json" file for later registry compare')
        ReleaseTest.registry_old = Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Registry_old.json")
        assert latest == downgrade, "FDM LOG if different after BIOS downgrade"
        # Flash latest release img back again
        upgrade = read_fdm(ReleaseTest.new_bios, "upgrade")
        assert upgrade != 0, "Exception: Read upgrade fdmlog"
        flash_latest = True
        logging.info('Dump "registry.json" file for later registry compare')
        ReleaseTest.registry_new = Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Registry_new.json")
        assert downgrade == upgrade, "FDM LOG if different after BIOS upgrade"
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()
    finally:
        if not flash_latest:
            Update.update_bios(ReleaseTest.new_bios)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)


# 检查BMC是否记录异常告警信息
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def check_bmc_warning():
    tc = ('907', '[TC907] BMC warning info in web', "Check no any warning info")
    result = ReportGen.LogHeaderResult(tc)
    check_result = BmcLib.bmc_warning_check().status
    check_res = BmcLib.bmc_warning_check().message
    if check_result is None:
        result.log_skip()
        return
    flag_error = 0
    if not check_result:
        for _excl in check_res.splitlines()[1:]:
            excl = _excl.split('|')[-1]
            if any(re.search(ex, excl) for ex in SutConfig.Env.BMC_WARN_IG):
                continue
            logging.debug(f"warning message: {excl}")
            flag_error += 1

    if flag_error != 0:
        result.log_fail()
        return False
    result.log_pass()
    return True


# Author: WangQingshan
# 检查新旧版本BIOS的Registry.json文件是否一致
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
@core.test_case(('908', '[TC908] Compare registry.json', "Compare registry.json file with previous version"))
def registry_check():
    new_branch = var.get('branch')
    old_branch = SutConfig.Env.PREVIOUS_BRANCH

    if not ReleaseTest.old_bios:
        ReleaseTest.old_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, old_branch, 'debug-build')
    if not ReleaseTest.new_bios:
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch, 'debug-build')
    flash_latest = True

    try:
        # old branch bios image registry dump
        if not ReleaseTest.registry_old:
            assert Update.update_bios(ReleaseTest.old_bios)
            flash_latest = False
            logging.info("dump old registry")
            ReleaseTest.registry_old = Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Registry_old.json")
        # new branch bios image registry dump
        if not ReleaseTest.registry_new:
            assert Update.update_bios(ReleaseTest.new_bios)
            flash_latest = True
            logging.info("dump new registry")
            ReleaseTest.registry_new = Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR,
                                                                   name="Registry_new.json")
        assert not PlatMisc.check_differ(ReleaseTest.registry_old, ReleaseTest.registry_new
                                         ), "Check old registry is different from new registry"
        logging.info("Check old registry is same with new registry")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if not flash_latest:
            Update.update_bios(ReleaseTest.new_bios)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)


# Author: WangQingshan
# Release BIOS降级测试
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def bios_downgrade_flash():
    tc = ('909', '[TC909] Downgrade flash', "Check BIOS version under setup and BMC Web")
    result = ReportGen.LogHeaderResult(tc)
    new_branch = var.get("branch")
    old_branch = SutConfig.Env.PREVIOUS_BRANCH
    if not ReleaseTest.old_bios:
        ReleaseTest.old_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, old_branch, 'debug-build')
    if not ReleaseTest.new_bios:
        ReleaseTest.new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, new_branch, 'debug-build')

    try:
        if ReleaseTest.downgrade_tested:
            logging.info("Bios downgrade flash is already verified in other test")
            result.log_pass()
            return True
        assert Update.update_bios(ReleaseTest.old_bios)
        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail(capture=True)
    finally:
        if not ReleaseTest.downgrade_tested:
            Update.update_bios(ReleaseTest.new_bios)
            SetUpLib.update_default_password()
            SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5)


# Author: WangQingshan
# 启动到UEFI系统并检查dmesg信息
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def boot_to_uefi_os():
    tc = ('910', '[TC910] Boot to UEFI OS', 'Boot to UEFI OS and check dmesg info')
    result = ReportGen.LogHeaderResult(tc)
    err_ignore = ["XFS .*?: Metadata (?:I/O|CRC) error", "ERST.*? support is initialized", "regulatory.(?:0|db)"]
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_OS, 20, Msg.BIOS_BOOT_COMPLETE)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert not PlatMisc.get_dmesg_keywords(["error", "fail"], err_ignore)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# 装备模式BIOS IIO菜单需要显示IOU信息 测试
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def equip_iou_not_hidden():
    tc = ('911', '[TC911] BIOS bin with equipment mode, IOU not hidden', 'BIOS bin with equipment mode, IOU not hidden')
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
# 装备模式BIOS，用装备工具设置选项/密码/Logo并恢复默认测试
# Precondition: BMC正常登录，KVM开启共享模式
# OnStart: NA
# OnComplete: NA
@core.test_case(('912', '[TC912] Restore BIOS default setting via equipment tool', 'Restore BIOS default setting via equipment tool'))
def equip_tool_set_and_restore():
    try:
        # 抓取默认logo和bios设置
        origin_logo = PlatMisc.save_logo(SutConfig.Env.LOG_DIR, name="origin_logo")
        assert origin_logo
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        default_config = Sut.UNITOOL.read(*BiosCfg.HPM_KEEP)
        # # 修改为非默认
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert PlatMisc.unipwd_tool("set", "admin@9001")
        assert PlatMisc.unilogo_update(name="CustomLogo.bmp")
        # 重启并检查修改结果
        modify_logo = PlatMisc.save_logo(SutConfig.Env.LOG_DIR, name="modify_logo")
        assert modify_logo
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        assert PlatMisc.unipwd_tool("check", "admin@9001")
        # 恢复默认
        assert "Load Default success" in SshLib.execute_command(Sut.OS_SSH, f"cd {SutConfig.Env.UNI_PATH};./unitool -c")
        logging.info("Unitool load default scuuess")
        assert PlatMisc.unipwd_tool("set", Msg.BIOS_PW_DEFAULT)
        assert PlatMisc.unilogo_update(name=os.path.split(origin_logo)[1], path=os.path.split(origin_logo)[0])
        # 重启并检查恢复默认结果
        restore_logo = PlatMisc.save_logo(SutConfig.Env.LOG_DIR, name="restore_logo")
        assert restore_logo
        assert MiscLib.compare_images(origin_logo, restore_logo)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(**default_config)
        assert PlatMisc.unipwd_tool("check", Msg.BIOS_PW_DEFAULT)
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 600):
            BmcLib.force_reset()
            MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        PlatMisc.unipwd_tool("set", Msg.BIOS_PASSWORD)
        BmcLib.clear_cmos()


# Author: WangQingshan
# 检查启动logo
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def post_logo_check():
    tc = ('913', '[TC913] POST Logo', 'Check POST Logo.')
    result = ReportGen.LogHeaderResult(tc)
    try:
        default_logo = os.path.abspath(os.path.join(os.path.dirname(__file__), r"..\Tools\Logo\DefaultLogo.bmp"))
        logging.info(f"Default logo: {default_logo}")
        post_logo = PlatMisc.save_logo(name="post_logo")
        if not post_logo:
            logging.info("Post logo cat't be captured, please confirm the KVM is open as share mode, not private mode")
            result.log_skip()
            return
        assert MiscLib.compare_images(default_logo, post_logo)
        result.log_pass()
    except AssertionError:
        result.log_fail()


# 1、BIOS正常启动；
# 2、检查KVM界面显示的热键信息是否正确，有结果A。
# A：KVM正确显示热键信息，包括DEL、F6、F11、F12。
@core.test_case(('915', '[TC915] 01 BIOS启动阶段KVM热键显示测试', '支持热键配置'))
def kvm_logo_check():
    try:
        default_logo = os.path.abspath(os.path.join(os.path.dirname(__file__), r"..\Tools\Logo\Key.bmp"))
        logging.info(f"Default logo: {default_logo}")
        key_logo = PlatMisc.save_logo(cut_str=Msg.HOTKEY_PROMPT_DEL, name="key_logo", logo_loc=(0, 0, 243, 78))
        if not key_logo:
            logging.info("Post logo can't be captured, please confirm the KVM is open as share mode, not private mode")
            raise AssertionError
        assert MiscLib.compare_images(default_logo, key_logo)
        return core.Status.Pass
    except AssertionError:
        core.capture_screen()
        return core.Status.Fail


# Author: WangQingshan
# Chipsec工具检查是否有fail或warning
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def chipsec_test():
    tc = ('914', '[TC914] Chipsec Test', 'The version is scanned by chipsec without warning')
    result = ReportGen.LogHeaderResult(tc)

    tme_en = [[Msg.PROCESSOR_CONFIG], "Total Memory Encryption \(TME\)", "Enabled"]
    # sgx_en = [[], "SW Guard Extensions \(SGX\)", "Enabled"]
    uma_base = [[Msg.COMMON_REF_CONFIG], "UMA-Based Clustering", "Disable (All2All)"]
    adddc_en = [[Msg.MEMORY_CONFIG, Msg.MEMORY_RAS_CFG], "ADDDC Sparing", "Disabled"]
    warnning_ignored = [
        "WARNING: chipsec.modules.biosguard",
        "WARNING: chipsec.modules.common.debugenabled",
        "WARNING: chipsec.modules.common.sgx_check",
        "WARNING: chipsec.modules.common.uefi.access_platform",
        "WARNING: chipsec.modules.common.uefi.s3bootscript"]

    try:

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG], 15, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.enter_menu(Key.DOWN, uma_base[0], 15, "MMIO High Base")
        assert SetUpLib.set_option_value(uma_base[1], uma_base[2], key=Key.UP)
        SetUpLib.send_keys([Key.ESC]*len(uma_base[0]))
        assert SetUpLib.enter_menu(Key.DOWN, adddc_en[0], 15, "Memory RAS Configuration Setup")
        assert SetUpLib.set_option_value(adddc_en[1], adddc_en[2], key=Key.UP)
        SetUpLib.send_keys([Key.ESC]*len(adddc_en[0]))
        assert SetUpLib.enter_menu(Key.DOWN, tme_en[0], 15, Msg.ACT_CPU_CORES)
        assert SetUpLib.set_option_value(tme_en[1], tme_en[2], key=Key.UP)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.read(*{"EnableSgx":1})
        assert Sut.UNITOOL.write(EnableSgx=1)

        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys([Key.RIGHT, Key.DOWN, Key.ENTER])
        assert SetUpLib.enter_menu(Key.UP, ["Secure Boot Factory Options"], 5, "Erase all Secure Boot Settings")
        assert SetUpLib.locate_option(Key.DOWN, ["Restore Secure Boot to Factory Settings"], 3)
        SetUpLib.send_keys([Key.ENTER])
        SetUpLib.send_keys([Key.Y], delay=15)
        SetUpLib.send_keys([Key.ESC])
        assert SetUpLib.locate_option(Key.DOWN, ["Attempt Secure Boot", "\[X\]"], 5)
        SetUpLib.send_keys([Key.ENTER]*2 + Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert SshLib.interaction(Sut.OS_SSH, [f"cd {SutConfig.Env.CHIPSEC_PATH}\n", "python3 chipsec_main.py > chipsec_log.txt\n"], ["", ""])
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
    finally:
        BmcLib.clear_cmos()

# 已安装产品规划内的Linux系统；
# 2、已安装acpidump和iasl；
# 3、老BIOS版本已导出所有ACPI表。
# Steps:
# 1、升级新版本BIOS，启动进入OS；
# 2、导出ACPI的数据：使用acpidump导出所有的ACPI表，但这些表都是二进制的
# acpidump > acpi.dat
# 3、分离各表格数据，会生成多个数据文件：上面的输出包含了很多个ACPI表，使用acpixtract命令将它们进行分离
# acpixtract -a acpidump.dat
# 4、反汇编每个表项，然后可以使用cat命令查看表信息，以facp表项为例：
# iasl -d facp.dat，cat apic.dsl
# 5、重复步骤4，使用diff命令对比新老BIOS版本的ACPI表项是否一致。
# Results:
# A：新老版本BIOS的ACPI表项一致。

# defined branch name, used below case tc916 - tc919, do not call.
lst_bios = SutConfig.Env.RELEASE_BRANCH
pre_bios = SutConfig.Env.PREVIOUS_BRANCH
err_msg = 'No such file or directory'


# this def used to tc916,
def _compare_interface_data(bios_branch, tag, ssh_type=Sut.OS_SSH):
    dsl_path = os.path.join(SutConfig.Env.LOG_DIR, bios_branch, tag)
    # if not os.path.exists(dsl_path):
    #     os.makedirs(dsl_path)
    try:
        assert _update_bios_img(bios_branch)
        if tag == 'acpi':
            if not os.path.exists(dsl_path):
                os.makedirs(dsl_path)
            assert SshLib.execute_command(Sut.OS_SSH, 'acpidump > acpi.dat') is not None, 'msg1 none or cmd1 failed'
            assert SshLib.execute_command(Sut.OS_SSH, 'acpixtract -a acpi.dat') is not None, 'msg2 none or cmd2 failed'
            res_dat = SshLib.execute_command(Sut.OS_SSH, 'ls *.dat')
            if res_dat is not None and err_msg not in res_dat:
                for i in res_dat.split('\n'):
                    if len(i) != 0:
                        assert SshLib.execute_command(Sut.OS_SSH, 'iasl -d {0}'.format(i)), '{0} is blank'.format(i)
            res_dsl = SshLib.execute_command(Sut.OS_SSH, 'ls *.dsl')
            if res_dsl is not None and err_msg not in res_dsl:
                for j in res_dsl.split('\n'):
                    if len(j) != 0:
                        assert SshLib.sftp_download_file(Sut.OS_SFTP, j, os.path.join(dsl_path, j))
        elif tag == 'cpuinfo':
            assert SshLib.execute_command(Sut.OS_SSH, 'cat /proc/cpuinfo |grep flags | head -n1 > {0}.txt'.format(bios_branch + tag)) == ''
        elif tag == 'iomem':
            assert SshLib.execute_command(ssh_type, 'cat /proc/iomem > {0}.txt'.format(bios_branch + tag)) == ''
        elif tag == 'ioports':
            assert SshLib.execute_command(ssh_type, 'cat /proc/ioports > {0}.txt'.format(bios_branch + tag)) == ''
        else:
            logging.info('Unknown tag, break')
            raise Exception
        return dsl_path, True
    except Exception as e:
        logging.error(e)
        return dsl_path, False


@core.test_case(('916', '[TC916]  新老版本ACPI表一致性检查', 'Compare ACPI table with previous BIOS version.'))
def acpi_table():
    input_tag = 'acpi'
    try:
        logging.info('compare the 2 versions dsl files...')
        # assume the current bios is latest,
        assert filecmp.dircmp(_compare_interface_data(pre_bios, input_tag)[0], _compare_interface_data(lst_bios, input_tag)[0]), 'ACPI files compare failed'
        logging.info('ACPI files compare pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
    finally:
        SshLib.execute_command(Sut.OS_SSH, 'rm -rf *.dat *.dsl')
        filecmp.clear_cache()
        logging.info('Restore ENV, move suse to first boot option')
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(lst_bios)


# Precondition: EQU BIOS
# OnStart: N/A
# Steps:
# '1、OS下进入装备工具路径， ./uniCfg -w DisableCESMIThrotting: 查看变量设置是否成功，有结果A。
#  A：变量设置成功。
# Completed: SUSE OS
@core.test_case(('920', '[TC920] 01 DisableCESMIThrotting变量检查', '装备测试TU分解用例'))
def testcase_equ_disCEStorm_001():
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config({"DisableCESMIThrotting": 1})
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail


# Author: Fubaolin
# Import BIOS setting under BMC Web
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
# Set
# 1. Export BIOS setting under BMC Web with older BIOS.
# 2. Flash new BIOS.
# 3. Power on system.
# 4. Import BIOS setting at step1.
# 5. Check whether normally import.
# 6. Relogin BIOS setting without any error.
@core.test_case(('917', '[TC917] Import BIOS setting under BMC Web', 'Check whether normally import'))
def testcase_import_bios_setting():
    lst_bios = SutConfig.Env.RELEASE_BRANCH
    pre_bios = SutConfig.Env.PREVIOUS_BRANCH
    cmd_export = f"ipmcget -t config -d export -v /tmp/config.xml"
    cmd_import = "ipmcset -t config -d import -v /tmp/config.xml\n"
    cmd_input ='Input your password:'
    ret_pwd = 'Admin@9001\n'
    ret_confirm = 'successfully'
    cmds = [cmd_import, ret_pwd]
    rets = [cmd_input, ret_confirm]
    dic_cfg = {**BiosCfg.ActiveCpuCores_aft, **BiosCfg.Spread_Spectrum_aft}
    try:
        assert _update_bios_img(pre_bios), 'lst_bios update failed'
        assert Sut.UNITOOL.write(**dic_cfg)
        assert SetUpLib.boot_suse_from_bm(), 'boot to suse failed'  # 修改的参数必须重启后，在config文件中才能导出
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        ret = SshLib.execute_command(Sut.BMC_SSH, cmd_export)
        assert ret_confirm in ret, '**Export BIOS setting -- fail'
        con_xml = os.path.join(SutConfig.Env.LOG_DIR, "config.xml")
        assert SshLib.sftp_download_file(Sut.BMC_SFTP, f"/tmp/config.xml", con_xml)

        assert _update_bios_img(lst_bios), 'lst_bios update failed'
        assert SshLib.sftp_upload_file(Sut.BMC_SFTP, "{}/config.xml".format(SutConfig.Env.LOG_DIR), "/tmp/config.xml", ret_msg="")
        assert SshLib.interaction(Sut.BMC_SSH, cmds, rets), "import config fail"
        assert SetUpLib.boot_suse_from_bm(), 'boot to suse failed'  # config文件导入后必须重启才生效
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert Sut.UNITOOL.check(**dic_cfg)
        logging.info('**check parameters -- pass')
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
