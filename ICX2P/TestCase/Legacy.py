import logging
from ICX2P.Config import SutConfig
from ICX2P.BaseLib import SetUpLib, PlatMisc, BmcLib
from batf import MiscLib, SerialLib, core
from batf.Report import ReportGen
from batf.SutInit import Sut
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.TestCase import UpdateBIOS

# Test case ID: TC500-520

##########################################
#            Legacy Test Cases           #
##########################################


def enable_legacy_boot():
    tc = ('500', '[TC500] Enable Legacy Boot', 'Enable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.enable_legacy_boot():
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def disable_legacy_boot():
    tc = ('501', '[TC501] Disable Legacy Boot', 'Disable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.disable_legacy_boot():
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


# Author: WangQingshan
# 启动到Legacy OS并检查dmesg没有错误
# Precondition: 依赖 enable_legacy_boot()
# OnStart: Legacy Mode
# OnComplete: NA
def boot_to_legacy_os():
    tc = ('502', '[TC502] Boot to legacy OS', 'Boot to legacy OS and check dmesg info')
    result = ReportGen.LogHeaderResult(tc)
    err_ignore = ["XFS .*?: Metadata (?:I/O|CRC) error", "ERST.*? support is initialized", "regulatory.(?:0|db)"]
    try:
        assert BmcLib.force_reset()
        if not SetUpLib.wait_message('Start of legacy boot', 600):
            assert SetUpLib.enable_legacy_boot()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, 600)
        assert not PlatMisc.get_dmesg_keywords(["error", "fail"], err_ignore)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()

# Author: ouyang
# BIOS正常启动过程中，检查OptionROM正确加载，没有错误信息。
# Precondition: 插入一张I350的网卡, 且Slot PXE为默认值Enabled
# OnStart: Legacy Mode
# OnComplete: NA
@core.test_case(('503', '[TC503]BIOS正常启动过程中，检查OptionROM正确加载', 'OptionROM正确加载'))
def testcase_optionrom_001():
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End, 60, 120)
        assert MiscLib.verify_msgs_in_log([SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End], log_cut)
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail


# Author: ouyang
# '1、单板运行，按键进入Setup菜单；
# 2、Setup菜单里关闭外接网卡PXE开关；
# 3、保存复位后，检查启动过程中不加载OptionROM。
# Precondition: 插入一张I350的网卡
# OnStart: Legacy Mode
# OnComplete: NA
@core.test_case(('504', '[TC504] 关闭外接网卡PXE开关', 'OptionROM没有加载'))
def testcase_optionrom_002():
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.NETWORK_CONFIG], 20, 'Network Configuration')
        assert SetUpLib.set_option_value('Slot Pxe', 'Disabled', save=True)
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End, 60, 120)
        assert not MiscLib.verify_msgs_in_log([SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End], log_cut)
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail


# Precondition: BIOS Legacy模式
# Testcase_UEFIBootManager_002
# 1、启动进BootManager界面，检查Manage Custom Boot Options选项，有结果A。
# A：无此选项，或者此选项置灰。
# OnStart: Legacy Mode
# OnComplete: NA
@core.test_case(('505', '[TC505]02【Legacy模式】启动项管理选项置灰', '支持UEFI模式启动项管理'))
def testcase_UEFIBootManager_002():
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert not SetUpLib.locate_option(Key.DOWN, ["Manage Custom Boot Options"], 7)
        return core.Status.Pass
    except AssertionError:
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)
        BmcLib.set_boot_mode("Legacy", once=False)
