# this script just for hotkey related function test
import logging

from Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, BmcLib


# Test case ID: TC800-850

'''
function module, do not call, only used below,
'''


def check_info():
    check_list = [Msg.RC_VERSION, Msg.BIOS_REVISION, Msg.BIOS_DATE, Msg.iBMC_VERSION, Msg.iBMC_IP, Msg.CPU_TYPE,
                  Msg.TOTAL_MEMORY]
    check_list_msg = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12]
    try:
        assert BmcLib.force_reset(), 'force_reset -> fail'
        # bug: if check_list does not exist by designed, will effect verification of the check_list_msg
        assert SetUpLib.wait_strings(check_list, timeout=120), 'info_verify -> fail'
        assert SetUpLib.wait_strings(check_list_msg, timeout=120), 'hotkey_info_verify -> fail'
        return True
    except AssertionError:
        return


def hotkey_press():
    result_list = []
    if not SetUpLib.boot_to_bios_config():
        result_list.append('1')

    if not SetUpLib.boot_to_bootmanager():
        result_list.append('2')

    if not SetUpLib.boot_with_hotkey(Key.F12, 'NBP file downloaded successfully', 120):
        result_list.append('3')

    if not SetUpLib.boot_with_hotkey(Key.F6, 'SmmInstallProtocolInterface: 296EB418-C4C8-4E05-AB59-39E8AF56F00A 0', 120):
        result_list.append('4')

    logging.debug(result_list)
    # check the result,
    if len(result_list) == 0:
        return True
    else:
        return False

##########################################
#            Release Test Cases          #
##########################################


# 01 【UEFI模式】POST启动第一屏显示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: OS (BIOS boot completed)
def system_info_001():
    tc = ('800', '[TC800] Testcase_SystemInfo_003', '01 【UEFI模式】POST启动第一屏显示信息测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert check_info()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 02 【Legacy模式】POST启动第一屏显示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: OS (BIOS boot completed)
def system_info_002():
    tc = ('801', '[TC801] Testcase_SystemInfo_003', '02 【Legacy模式】POST启动第一屏显示信息测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert check_info()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 03 按热键后屏幕底部显示提示信息测试 UEFI
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SP SETUP
def system_info_003():
    tc = ('802', '[TC802] Testcase_SystemInfo_003', '03 按热键后屏幕底部显示提示信息测试 UEFI')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert hotkey_press()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 04 按热键后屏幕底部显示提示信息测试 legacy
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SP SETUP
def system_info_004():
    tc = ('803', '[TC803] Testcase_SystemInfo_004', '04 按热键后屏幕底部显示提示信息测试 legacy')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert hotkey_press()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
