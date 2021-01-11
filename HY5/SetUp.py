#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import datetime
import logging
import time

from Common import Misc
from HY5.Hy5Config import Key
from Common.LogAnalyzer import LogAnalyzer
from HY5 import Hy5TcLib, Hy5Config, Hy5BaseAPI

# smbiosTest
P = LogAnalyzer(Hy5Config.LOG_DIR)


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    msg = "Boot From File"
    logging.info("HaiYan5 Common Test Lib: boot to setup")
    logging.info("Rebooting SUT...")
    if not Hy5TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.boot_with_hotkey(Key.DEL, msg, 300):
        logging.info("Boot to setup failed.")
        return
    return True


# Boot to boot manager without a force reset
def continue_to_bootmanager(serial):
    logging.info("HaiYan5 Common TC: continue boot to bootmanager")
    msg = "Boot Manager Menu"
    if not serial.boot_with_hotkey(Key.F11, msg, 300):
        logging.info("Continue boot to bootmanager failed.")
        return
    logging.info("HaiYan5 Common TC: Boot to bootmanager successful")
    return True


# Boot to BIOS configuration page
def boot_to_bios_config(serial, ssh):
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys_with_delay(Hy5Config.key2Setup)
    if not serial.is_msg_present('System Time'):
        logging.info("Boot to BIOS Configuration Failed")
        return
    logging.info("Boot to BIOS Configuration Pass")
    return True


# Reset BIOS setup to default by pressing F9
def reset_default(serial, ssh):
    logging.info("Reset BIOS to dafault by F9")
    keys = Key.F9 + Key.Y + Key.F10 + Key.Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('BIOS boot completed.'):
        logging.info("Reset dafault by F9:Fail")
        return
    logging.info("Reset dafault by F9:Pass")
    return True


# check whether ME is working in operational state
def check_me_state(serial, ssh):
    tc = ('005', 'Check ME State', 'Verify ME state in operational mode')
    result = Misc.LogHeaderResult(tc, serial)
    keys = Key.RIGHT * 2 + Key.DOWN + Key.ENTER + Key.RIGHT + Key.DOWN * 5 + Key.ENTER
    keys_state = Key.DOWN * 5
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('firmware selected to run'):
        logging.info("Boot to ME Configuration Menu Failed")
        return
    logging.info("Boot to ME Configuration Pass")
    serial.send_keys(keys_state)
    if not serial.is_msg_present('Operational'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Enable full debug message
def enable_full_debug_msg(serial, ssh):
    tc = ('006', 'Enable full debug message', 'Enable serial full debug message')
    result = Misc.LogHeaderResult(tc, serial)
    keys_enable_full_debug = Key.RIGHT + Key.DOWN + Key.ENTER + Key.DOWN * 5 + Key.F5 + Key.F10 + Key.Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys_enable_full_debug)
    if not serial.is_msg_present('^InstallProtocolInterface.'):
        result.log_fail()
        return
    if not serial.is_msg_present('BIOS boot completed.'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Disable full debug message
def disable_full_debug_msg(serial, ssh):
    tc = ('007', 'Disable full debug message', 'Disable serial full debug message')
    result = Misc.LogHeaderResult(tc, serial)
    keys_enable_full_debug = Key.RIGHT + Key.DOWN + Key.ENTER + Key.DOWN * 5 + Key.F6 + Key.F10 + Key.Y
    if not boot_to_bios_config(serial, ssh):
        result.log_fail()
        return
    serial.send_keys(keys_enable_full_debug)
    if not serial.is_msg_not_present('^InstallProtocolInterface.', 'BIOS boot completed.'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Enable legacy boot
def enable_legacy_boot(serial, ssh):
    tc = ('008', 'Enable Legacy Boot', 'Enable Legacy Boot')
    result = Misc.LogHeaderResult(tc, serial)
    keys = Key.RIGHT * 4 + Key.F5 + Key.F10 + Key.Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('Start of legacy boot'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Disable legacy boot
def disable_legacy_boot(serial, ssh):
    tc = ('009', 'Disable Legacy Boot', 'Disable Legacy Boot')
    result = Misc.LogHeaderResult(tc, serial)
    keys = Key.RIGHT * 4 + Key.F6 + Key.F10 + Key.Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_not_present('Start of legacy boot', 'BIOS boot completed.'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Chnage CPU Cores to specific number, n is times of change value hotkey pressed, not core number
def change_cpu_cores(serial, ssh, n, num):
    logging.info("<TC010><Tittle>Change CPU Cores:Start")
    logging.info("<TC010><Description>Change CPU Core counts in setup and verify in OS")
    keys_cpu_core = Key.RIGHT * 1 + Key.DOWN * 8 + Key.ENTER * 2
    if not boot_to_bios_config(serial, ssh):
        return
    logging.info("Changing cpu core counts")
    serial.send_keys_with_delay(keys_cpu_core)
    serial.send_keys(Key.F6 * 14 + Key.F10 + Key.Y)
    time.sleep(5)

    """
    if not continue_to_bootmanager(serial):
        return
    logging.info("Booting to Ubuntu")
    serial.send_keys(DOWN + ENTER) # boot to ubuntu
    if not serial.is_msg_present('byosoft-2488H-V6 login'):
        logging.info("Boot to UEFI Ubuntu:Fail")
        return
    if not Hy5TcLib.verify_cpucore_count(ssh, num):
        logging.info("<TC010><Result>Change CPU Cores:Fail")
        return
    logging.info("<TC010><Result>Change CPU Cores:Pass")
    return True
    """


# check password, for password case only
def checkPWD(serial, pwd1, pwd2):
    if not Hy5BaseAPI.pressDelnp(serial):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.invalid_info, timeout=30):
        return
    serial.send_data(chr(0x0D))
    serial.send_data('22222222')
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.invalid_info, timeout=30):
        return
    serial.send_data(chr(0x0D))
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    serial.send_keys_with_delay([Key.RIGHT, Key.LEFT])
    if not serial.waitString('Continue', timeout=30):
        return
    return True


# Setup: Load default and setting saving - AT test cases below,
def loadDefault(serial, ssh):
    tc = ('013', 'Load default and setting saving Test', 'BIOS Load default Test')
    result = Misc.LogHeaderResult(tc, serial)
    option_bfo = ['<UEFI Boot Type>', '<Boot Retry>']
    option_aft = ['<Legacy Boot Type>', '<Cold Boot>']
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2type)
    if not Hy5BaseAPI.verify_setup_options_down(serial, option_bfo, 14):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'Boot Type'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'Boot Fail Policy'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    serial.send_keys(Key.F10 + Key.Y)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2type)
    if not Hy5BaseAPI.verify_setup_options_down(serial, option_aft, 14):
        result.log_fail()
        if not reset_default(serial, ssh):
            return
    serial.send_keys_with_delay(Hy5Config.key2default)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        if not reset_default(serial, ssh):
            return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2type)
    time.sleep(1)
    if not Hy5BaseAPI.verify_setup_options_down(serial, option_bfo, 14):
        result.log_fail()
        if not reset_default(serial, ssh):
            return
    result.log_pass()
    return True


# updated by arthur, Testcase_Static_Turbo_001
def staticTurbo(serial, ssh):
    tc = ('021', '静态Turbo默认值测试', '支持静态turbo')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, Hy5Config.option6):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.static_turbo, 5):
        result.log_fail()
        return
    serial.send_keys(Hy5Config.Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'Static Turbo', timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'AutoManualDisabled'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_UFS_001,
def ufs(serial, ssh):
    tc = ('022', 'UFS默认值测试', '支持UFS设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not boot_to_bios_config(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2default)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option6, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option8, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5BaseAPI.verify_setup_options_up(serial, Hy5Config.ufs, 4):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'UFS', timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'Disabled_MaxDisabled_Min'):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_RRQIRQ_001
def rrQIRQ(serial, ssh):
    tc = ('023', 'Setup菜单RRQ和IRQ选项默认值测试', '支持RRQ&IRQ设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option9, timeout=30):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, Hy5Config.option12, 3):
        result.log_fail()
        return
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.local_remote, 12):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'Local/Remote Threshold', timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'DisabledAutoLowMediumHighManual', timeout=15):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.F5, Key.F5, Key.F5, Key.F5])
    if not Hy5BaseAPI.verify_setup_options_down(serial, ['\[7\]\s+IRQ Threshold', '\[7\]\s+RRQ Threshold'], 12):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'IRQ Threshold', timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    serial.send_data('10')
    serial.send_keys_with_delay([Key.ENTER, Key.DOWN, Key.ENTER])
    serial.send_data('20')
    serial.send_keys(Key.ENTER)
    serial.send_keys(Key.F10 + Key.Y)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option9, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.find_setup_option(Key.DOWN, Hy5Config.option12, 3):
        result.log_fail()
        return
    if not Hy5BaseAPI.verify_setup_options_down(serial, ['\[10\]\s+IRQ Threshold', '\[20\]\s+RRQ Threshold'], 12):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_DRAM_RAPL_001
def dramRAPL(serial, ssh):
    tc = ('024', '菜单项DRAM RAPL选单检查', '支持DRAM RAPL设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, Hy5Config.option6):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.UP, Hy5Config.option11):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, 'DRAM RAPL Configuration', 7):
        result.log_fail()
        return
    if not Hy5BaseAPI.verify_setup_options_up(serial, Hy5Config.dram, 4):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.verify_option_value(Key.DOWN, r'DisabledEnabled', timeout=30):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_012, 013, 014
# 输入错误密码次数测试_阈值内输入错误密码, 输入错误密码次数测试_阈值内连续输入错误密码后输入正确密码和输入错误密码次数测试_超出阈值不影响下一次登录
def pwdSecurity(serial, ssh):
    tc = ('025', '输入错误密码次数测试', '输入错误密码次数测试包含密码错误，次数测试和超出阈值不影响下一次登录')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.pressDel(serial, ssh):
        result.log_fail()
        return
    for i in range(2):
        logging.info("Send wrong password...")
        serial.send_data(Hy5Config.new_pwd_9)
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString(Hy5Config.invalid_info, timeout=15):
            result.log_fail()
            return
        serial.send_data(chr(0x0D))  # Send Enter
    logging.info('Send the right password...')
    serial.send_data(Hy5Config.default_pwd)
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString('BIOS Configuration', timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not Hy5BaseAPI.pressDel(serial, ssh):
        result.log_fail()
        return
    for i in range(3):
        logging.info("Send wrong password...")
        serial.send_data(Hy5Config.new_pwd_9)
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString(Hy5Config.invalid_info, timeout=15):
            result.log_fail()
            return
        serial.send_data(chr(0x0D))  # Send Enter
    if not serial.waitString(Hy5Config.error_info, timeout=15):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        return
    result.log_pass()
    return True


# 检查CDN开关默认值
def cnd(serial, ssh):
    tc = ('026', '检查CDN开关默认值', '支持网口CDN特性开关')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys(Key.RIGHT)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option7, timeout=30):
        result.log_fail()
        return
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.cnd_status, 12):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_007, 019, 020, 021, 022
def pwdVerification1(serial, ssh):
    tc = ('027', '密码修改验证', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    # if not Hy5BaseAPI.toBIOS(serial, ssh):
    #     result.log_fail()
    #     return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pwd_item):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=30):
        result.log_fail()
        return
    # Testcase_BiosPasswordSecurity_002 新密码长度小于最少字符数要求（8）
    serial.send_data(Hy5Config.simple_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.invalid_info, timeout=15):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=30):
        result.log_fail()
        return
    serial.send_data(Hy5Config.default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_2, timeout=30):
        result.log_fail()
        return
    serial.send_data(Hy5Config.weak_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_3, timeout=30):
        result.log_fail()
        return
    serial.send_data(Hy5Config.weak_pwd)
    serial.send_data(chr(0x0D))
    # 弱口令验证
    if not serial.waitString(Hy5Config.simple_pwd_warning, timeout=30):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=30):
        result.log_fail()
        return
    serial.send_data(Hy5Config.default_pwd)
    serial.send_data(chr(0x0D))
    # Testcase_BiosPasswordSecurity_004 新密码长度大于最少字符数要求（8）
    serial.send_data(Hy5Config.new_pwd_9)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_2, timeout=30):
        result.log_fail()
        return
    serial.send_data(Hy5Config.new_pwd_9)
    serial.send_data(chr(0x0D))
    time.sleep(1)
    if not serial.waitString(Hy5Config.pwd_info_3, timeout=30):
        result.log_fail()
        return
    serial.send_data(Hy5Config.new_pwd_9)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_4, timeout=30):
        result.log_fail()
        return
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    if not Hy5BaseAPI.toBIOSnp(serial, Hy5Config.new_pwd_9):
        result.log_fail()
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_003, 010 设置密码长度度测试_密码长度等于最少字符数(8)
def pwdVerification2(serial, ssh):
    tc = ('028', '设置密码长度度测试', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.setPWD(serial, ssh, Hy5Config.new_pwd_9, Hy5Config.new_pwd_8):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSnp(serial, Hy5Config.new_pwd_8):
        result.log_fail()
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_005, 006
def pwdVerification3(serial, ssh):
    tc = ('029', '设置密码最大字符数测试', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh, Hy5Config.new_pwd_8):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pwd_item):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=15):
        result.log_fail()
        return
    serial.send_data(Hy5Config.new_pwd_17)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.invalid_info, timeout=15):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not Hy5BaseAPI.setPWDnp(serial, Hy5Config.new_pwd_8, Hy5Config.new_pwd_16):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSnp(serial, Hy5Config.new_pwd_16):
        result.log_fail()
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_008, 009
def pwdVerification4(serial, ssh):
    tc = ('030', '设置密码最大字符数测试', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh, Hy5Config.new_pwd_16):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pwd_item):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=15):
        result.log_fail()
        return
    i = 0
    full_pwd_list = Hy5Config.pwd_list1 + Hy5Config.pwd_list2
    while i < len(full_pwd_list):
        serial.send_data(full_pwd_list[i])
        serial.send_data(chr(0x0D))
        logging.info('send the pwd:{0}'.format(full_pwd_list[i]))
        if len(full_pwd_list) == 8:
            if not serial.waitString(Hy5Config.error_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not Hy5BaseAPI.enterPWD(serial, Hy5Config.new_pwd_16):
                result.log_fail()
                return
        elif len(full_pwd_list) == 5:
            if not serial.waitString(Hy5Config.error_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not Hy5BaseAPI.enterPWD(serial, Hy5Config.new_pwd_16):
                result.log_fail()
                return
        elif len(full_pwd_list) == 2:
            if not serial.waitString(Hy5Config.error_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not Hy5BaseAPI.enterPWD(serial, Hy5Config.new_pwd_16):
                result.log_fail()
                return
        else:
            if not serial.waitString(Hy5Config.invalid_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            serial.send_data(chr(0x0D))
            serial.send_data(chr(0x0D))

        i += 1
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_SimplePassword_001, 002, 003, 004 and 005
def simplePWDTest(serial, ssh):
    tc = ('034', '简易密码开关默认值测试', '支持关闭密码复杂度检测')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh, Hy5Config.new_pwd_16):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.simplePWD_info, 10):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.RIGHT])
    time.sleep(1)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, Hy5Config.pwd_item1, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    if not serial.waitString(Hy5Config.enable_simple_pwd, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, Hy5Config.pwd_item, timeout=30):
        result.log_fail()
        return
    if not Hy5BaseAPI.setPWDwithoutF10(serial, Hy5Config.new_pwd_16, Hy5Config.simple_pwd):
        result.log_fail()
        return
    if not checkPWD(serial, Hy5Config.simple_pwd, Hy5Config.new_pwd_16):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    time.sleep(1)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, Hy5Config.pwd_item1, timeout=30):
        return
    serial.send_keys(Key.F5)
    if not serial.waitString(Hy5Config.enable_simple_pwd, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, Hy5Config.pwd_item, timeout=30):
        result.log_fail()
        return
    if not Hy5BaseAPI.setPWDnp(serial, Hy5Config.new_pwd_16, Hy5Config.simple_pwd):
        result.log_fail()
        return
    if not checkPWD(serial, Hy5Config.new_pwd_16, Hy5Config.simple_pwd):
        result.log_fail()
        return
    result.log_pass()
    return True


# 整合密码测试
def pwdSecurityTest(serial, ssh):
    pwdSecurity(serial, ssh)
    pwdVerification1(serial, ssh)
    pwdVerification2(serial, ssh)
    pwdVerification3(serial, ssh)
    pwdVerification4(serial, ssh)
    simplePWDTest(serial, ssh)
    logging.info("密码组合和简易设置验证完成，当前为最后一个密码修改用例，开始恢复环境:更新BIOS")
    Hy5BaseAPI.restore_env(serial)

    return True


# Testcase_SecurityBoot_001, 004
def securityBoot(serial, ssh):
    tc = ('031', 'Secure Boot默认值', 'Secure Boot默认值')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    key1 = [Key.RIGHT, Key.DOWN, Key.ENTER]
    serial.send_keys_with_delay(key1)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.secure_status, 6):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.RIGHT, Key.ENTER])
    serial.send_keys_with_delay([Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, Hy5Config.pat, 'Boot Type'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    time.sleep(0.1)
    serial.send_keys(Key.F10 + Key.Y)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        reset_default(serial, ssh)
        return
    serial.send_keys_with_delay(key1)
    if serial.waitString('Current Secure Boot State'):
        result.log_fail()
        return
    reset_default(serial, ssh)
    result.log_pass()
    return True


# Testcase_TPM_001, 002, 005, 006, 009 TPM芯片测试 (单板已插TPM卡)
# TXT + TPM Test Testcase_TPM_013 单板已插TPM卡 - 待在新板上验证，旧板不支持TXT（或rework板子开启TXT）
def tpm(serial, ssh):
    tc = ('032', 'TPM芯片测试', '支持CBNT')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.tpm_info, 12):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.LEFT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option3):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, 'TXT'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    serial.send_keys(Key.F10 + Key.Y)
    if not serial.waitString('DetectTpmDevice', timeout=120):
        result.log_fail()
        if not reset_default(serial, ssh):
            return
    if not Hy5BaseAPI.toSysTime(serial):
        result.log_fail()
        if not reset_default(serial, ssh):
            return
    serial.send_keys(Hy5Config.key2default)
    if not Hy5BaseAPI.toSysTime(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.tpm_info, 10):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_VTD_002
def vtd(serial, ssh):
    tc = ('025', '关闭VT-d功能启动测试', '支持VT-d')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys(Key.RIGHT)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option10, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, 'Intel\(R\) VT for Directed I/O \(VT-d\)'):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.pat, 'Intel\(R\) VT for Directed I/O'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2OS)
    if not serial.find_setup_option(Key.DOWN, IcxConfig.SUSE, 10):
        result.log_fail()
        return
    if not icx2pAPI.ping_sut():  # OS flag
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_CPU_COMPA_015, 016 - TBD
def cpuCOMPA(serial, ssh):
    tc = ('038', 'UPI link链路检测测试', 'CPU兼容性测试')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option9):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, Hy5Config.option12, 4):
        result.log_fail()
        return
    serial.send_keys(Key.UP)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option14):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.upi_state, 4):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_LogTime_001, 002 and 003 串口日志打印
def logTime(serial, ssh):
    tc = ('039', '串口日志打印测试', '支持BIOS启动开始和结束信息打印及上报')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2OS)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.OS, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5TcLib.ping_sut():
        result.log_fail()
        return
    t1 = Hy5TcLib.osTime(ssh)
    if not serial.is_msg_present_general('BIOS Log', delay=60):
        result.log_fail()
        return
    with open(Hy5Config.SERIAL_LOG, 'r') as f:
        while True:
            try:
                line = f.readline()
                if 'BIOS Log' in line:
                    t2 = line.split('@')[-1].rstrip().split('<')[0].lstrip().replace('.', '-').strip()
                    t3 = datetime.datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
                    t_time = (t3 - t1)
                    hour = int(t_time.seconds / 60 / 60)
                    dela_time = int((t_time.seconds - hour * 60 * 60) / 60)
                    # print(t3, t1, hour, dela_time)
                    if dela_time < 5:  # if interval time is less than 5 mins,
                        pass
                    else:
                        print('The BIOS time is not matched with RTC time')
                        result.log_fail()
                        return False
                    break
            except Exception as e:
                print(str(e))
    f.close()
    result.log_pass()
    return True


# Testcase_CoreDisable_001, 002, 003, 004, 005 and 007
def coreDisable(serial, ssh):
    tc = ('043', 'Setup菜单关核选项测试', '支持CPU关核')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option3):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5BaseAPI.verify_setup_options_up(serial, ['<All>\s+Active Processor Cores'], 7):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pat, 'Active Processor Cores'):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.UP, r'1234567891011121314151617All', timeout=15):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.F6, Key.F6])
    serial.send_keys(Key.F10 + Key.Y)
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option5):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5BaseAPI.verify_setup_options_up(serial, Hy5Config.DIMM_info, 20):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not Hy5TcLib.ping_sut():
        result.log_fail()
        return
    if not Hy5TcLib.chipsecMerge(ssh):
        result.log_fail()
        return
    cmd = 'dmidecode -t 4'
    path = Hy5Config.LOG_DIR
    Hy5TcLib.dump_smbios(ssh, cmd)
    if not P.smbiosCheck(cmd, path, Hy5Config.SMBIOS_TEMPLATE):
        result.log_fail()
        return
    result.log_pass()
    return True


# Main function
def biosSetupTest(serial, ssh):
    loadDefault(serial, ssh)
    staticTurbo(serial, ssh)
    ufs(serial, ssh)
    rrQIRQ(serial, ssh)
    dramRAPL(serial, ssh)
    pwdSecurityTest(serial, ssh)
    securityBoot(serial, ssh)
    vtd(serial, ssh)
    cpuCOMPA(serial, ssh)
    logTime(serial, ssh)