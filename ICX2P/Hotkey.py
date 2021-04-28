# this script just for hotkey related function test

from Core import SerialLib
from Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, PowerLib


# Test case ID: TC800-850

##########################################
#            Release Test Cases          #
##########################################


# 01 【UEFI模式】POST启动第一屏显示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: OS (BIOS boot completed)
def Testcase_SystemInfo_001(serial, ssh_bmc):
    tc = ('800', '[TC800] Testcase_SystemInfo_003', '01 【UEFI模式】POST启动第一屏显示信息测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    check_list = [Msg.RC_VERSION, Msg.BIOS_REVISION, Msg.BIOS_DATE, Msg.iBMC_VERSION, Msg.iBMC_IP, Msg.CPU_TYPE,
                  Msg.TOTAL_MEMORY]
    check_list_msg = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12]
    try:
        assert PowerLib.force_reset(ssh_bmc), 'force_reset -> fail'
        # bug: if check_list does not exist by designed, will effect verification of the check_list_msg
        assert serial.waitStrings(check_list, timeout=120), 'info_verify -> fail'
        assert serial.waitStrings(check_list_msg, timeout=120), 'hotkey_info_verify -> fail'
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 02 【Legacy模式】POST启动第一屏显示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: OS (BIOS boot completed)
def Testcase_SystemInfo_002(serial, ssh_bmc):
    tc = ('801', '[TC801] Testcase_SystemInfo_003', '02 【Legacy模式】POST启动第一屏显示信息测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    check_list = [Msg.RC_VERSION, Msg.BIOS_REVISION, Msg.BIOS_DATE, Msg.iBMC_VERSION, Msg.iBMC_IP, Msg.CPU_TYPE,
                  Msg.TOTAL_MEMORY]
    check_list_msg = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12]
    try:
        assert SetUpLib.enable_legacy_boot(serial, ssh_bmc), 'enable_legacy_mode -> fail'
        # bug: if check_list does not exist by designed, will effect verification of the check_list_msg
        assert serial.waitStrings(check_list, timeout=120), 'info_verify -> fail'
        assert serial.waitStrings(check_list_msg, timeout=120), 'hotkey_info_verify -> fail'
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 03 按热键后屏幕底部显示提示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SP SETUP
def Testcase_SystemInfo_003(serial, ssh_bmc):
    tc = ('802', '[TC802] Testcase_SystemInfo_003', '03 按热键后屏幕底部显示提示信息测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        assert PowerLib.force_reset(ssh_bmc), 'force_reset -> fail'
        assert SetUpLib.boot_with_hotkey(serial, ssh_bmc, Key.DEL, Msg.HOTKEY_PROMPT_DEL, 300)
        SerialLib.send_key(serial, Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_to_bootmanager(serial, ssh_bmc)
        SerialLib.send_key(serial, Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey(serial, ssh_bmc, Key.F12, Msg.HOTKEY_PROMPT_F12, 300)
        SerialLib.send_key(serial, Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey(serial, ssh_bmc, Key.F6, Msg.HOTKEY_PROMPT_F6, 300)
        assert SetUpLib.disable_legacy_boot(serial, ssh_bmc), 'test_pass_switch_to_uefi_mode -> fail'
        result.log_pass()
    except AssertionError:
        assert SetUpLib.disable_legacy_boot(serial, ssh_bmc), 'test_fail_switch_to_uefi_mode -> fail'
        result.log_fail(capture=True)
