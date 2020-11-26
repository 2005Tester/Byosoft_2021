#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import time
from HY5 import Hy5TcLib, Hy5Config, Hy5BasicFunc
from Common import Misc

# Key mapping
ENTER = [chr(0x0D)]
DEL = [chr(0x7F)]
F2 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x32), chr(0x7e)]
F5 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x35), chr(0x7e)]
F6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
F9 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x30), chr(0x7e)]
F10 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x31), chr(0x7e)]
F11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
F12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]
UP = [chr(0x1b), chr(0x5b), chr(0x41)]
DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
Y = [chr(0x59)]

# set by arthur, a common key order
key2Setup = RIGHT * 2 + DOWN + ENTER
key2PWD = RIGHT * 3 + DOWN + ENTER  # to password page
default_pwd = 'Admin@9000'
new_pwd_9 = 'Admin@9001'
new_pwd_8 = 'Admin@9!'
new_pwd_16 = 'Admin@9001Admin@90'
new_pwd_17 = 'Admin@9001Admin@900'
simple_pwd = '11111111'
weak_pwd = 'Huawei@CLOUD8!'
pwd_list1 = ['ADMIN123', 'admin123', 'admin###', 'ADMIN###', 'ADMINadm', '1234####']  # 新密码为2种字符类型，尝试各种组合（共6种组合）
# System will be locked after send wrong pwd 3 times
pwd_list2 = ['Administrator@', 'admin@123', 'Administrator1', 'ADMIN@123']  # 新密码为3种字符类型，尝试各种组合（共4种组合）
# common error msg
pwd_info_1 = 'Please type in your password'
pwd_info_2 = 'Please type in your new password'
pwd_info_3 = 'Please confirm your new password'
pwd_info_4 = 'Changes have been saved after press'
invalid_info = 'Invalid Password'
error_info = 'Enter incorrect password 3 times,System Locked'
simple_pwd_warning = 'The password fails the dictionary check - it is too simplistic/systematic'
# TPM info
tpm_info = ['TPM Device\s+TPM 2.0', 'TPM2 Active PCR Hash\s+Algorithm+\s+SHA1\, SHA256',
            'TPM2 Hardware Supported Hash\s+Algorithm+\s+SHA1\, SHA256']
# UPI Status
upi_state = ['Current UPI Link Speed\s+Fast', 'Current UPI Link Frequency\s+10\.4\s+GT\/s']


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    msg = "Boot From File"
    logging.info("HaiYan5 Common Test Lib: boot to setup")
    logging.info("Rebooting SUT...")
    if not Hy5TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.boot_with_hotkey(DEL, msg, 300):
        logging.info("Boot to setup failed.")
        return
    return True


# Boot to boot manager without a force reset
def continue_to_bootmanager(serial):
    logging.info("HaiYan5 Common TC: continue boot to bootmanager")
    msg = "Boot Manager Menu"
    if not serial.boot_with_hotkey(F11, msg, 300):
        logging.info("Continue boot to bootmanager failed.")
        return
    logging.info("HaiYan5 Common TC: Boot to bootmanager successful")
    return True


# Boot to BIOS configuration page
def boot_to_bios_config(serial, ssh):
    keys = RIGHT * 2 + DOWN + ENTER
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('System Time'):
        logging.info("Boot to BIOS Configuration Failed")
        return
    logging.info("Boot to BIOS Configuration Pass")
    return True


# Reset BIOS setup to default by pressing F9
def reset_default(serial, ssh):
    logging.info("Reset BIOS to dafault by F9")
    keys = F9 + Y + F10 + Y
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
    keys = RIGHT * 2 + DOWN + ENTER + RIGHT + DOWN * 5 + ENTER
    keys_state = DOWN * 5
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
    keys_enable_full_debug = RIGHT + DOWN + ENTER + DOWN * 5 + F5 + F10 + Y
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
    keys_enable_full_debug = RIGHT + DOWN + ENTER + DOWN * 5 + F6 + F10 + Y
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
    keys = RIGHT * 4 + F5 + F10 + Y
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
    keys = RIGHT * 4 + F6 + F10 + Y
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
    keys_cpu_core = RIGHT * 1 + DOWN * 8 + ENTER * 2
    if not boot_to_bios_config(serial, ssh):
        return
    logging.info("Changing cpu core counts")
    serial.send_keys_with_delay(keys_cpu_core)
    serial.send_keys(F6 * 14 + F10 + Y)
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


# common def, not test cases
# updated by arthur, press Delete
def pressDel(serial, ssh):
    if not Hy5TcLib.force_reset(ssh):
        return
    if not serial.waitString('Press Del go to Setup Utility', timeout=300):
        return
    serial.send_keys(DEL)
    if not serial.waitString("Press F2", timeout=60):
        return
    return True


def pressDelnp(serial):
    if not serial.waitString('Press Del go to Setup Utility', timeout=300):
        return
    serial.send_keys(DEL)
    if not serial.waitString("Press F2", timeout=60):
        return
    return True


# enhanced pwdVerification4 def,
def enterPWD(serial, pwd):
    serial.send_keys_with_delay(Hy5BasicFunc.Key.CTRL_ALT_DELETE)
    if not Hy5BasicFunc.toBIOSnp(serial, pwd):
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    serial.send_keys_with_delay(key2PWD)
    if not serial.waitString(pwd_info_1, timeout=15):
        return
    return True


# set pwd common def function, only for set PWD, do not call it for other cases
# pwd1 - previous password, pwd2 - new password
def setPWD(serial, ssh, pwd1, pwd2):
    if not Hy5BasicFunc.toBIOS(serial, ssh, new_pwd_9):
        return
    time.sleep(0.2)
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    serial.send_keys_with_delay(key2PWD)
    if not serial.waitString(pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    time.sleep(0.2)
    if not serial.waitString(pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_4, timeout=30):
        return
    time.sleep(0.2)
    serial.send_keys_with_delay(ENTER)
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    return True


# set password with no power action first
def setPWDnp(serial, pwd1, pwd2):
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_4, timeout=30):
        return
    serial.send_keys_with_delay(ENTER)
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    return True


# set password with no power action first
def setPWDwithoutF10(serial, pwd1, pwd2):
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_4, timeout=30):
        return
    serial.send_keys_with_delay(ENTER)
    time.sleep(0.2)
    serial.send_keys_with_delay(Hy5BasicFunc.Key.CTRL_ALT_DELETE)
    return True


# def to BIOS Setup - System Time page
def toSysTime(serial):
    if not Hy5BasicFunc.toBIOSnp(serial):
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=30):
        return
    return True


# check password, for password case only
def checkPWD(serial, pwd1, pwd2):
    if not pressDelnp(serial):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(invalid_info, timeout=30):
        return
    serial.send_data(chr(0x0D))
    serial.send_data('22222222')
    serial.send_data(chr(0x0D))
    if not serial.waitString(invalid_info, timeout=30):
        return
    serial.send_data(chr(0x0D))
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    serial.send_keys_with_delay(RIGHT + LEFT)
    if not serial.waitString('Continue', timeout=30):
        return
    return True


# AT test cases below... ...
# Setup: Load default and setting saving
def Load_Default_Test(serial, ssh):
    logging.info("<TC013><Tittle>Load default and setting saving Test:Start")
    logging.info("<TC013><Description>BIOS Load default Test")
    option_bfo = ['<UEFI Boot Type>', '<Boot Retry>']
    option_aft = ['<Legacy Boot Type>', '<Cold Boot>']
    key1 = RIGHT * 4
    key2 = F9 + Y + F10 + Y
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        return
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, option_bfo, 14):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        return
    serial.send_keys_with_delay(LEFT + RIGHT)
    serial.send_keys_with_delay(ENTER + DOWN + ENTER)
    serial.send_keys_with_delay(DOWN * 2 + ENTER + DOWN + ENTER)
    # if not verify_setup_options(serial, options_new, 12):
    #     return
    serial.send_keys(F10 + Y)
    if not Hy5BasicFunc.toBIOSnp(serial):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        return
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, option_aft, 14):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        if not reset_default(serial, ssh):
            return
    serial.send_keys(key2)
    if not Hy5BasicFunc.toBIOSnp(serial):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        if not reset_default(serial, ssh):
            return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        return
    serial.send_keys_with_delay(key1)
    time.sleep(1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, option_bfo, 14):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        if not reset_default(serial, ssh):
            return
    logging.info("<TC013><Result>Load default and setting saving Test:Pass")
    return True


# updated by arthur, Testcase_Static_Turbo_001
def staticTurbo(serial, ssh):
    logging.info("<TC021><Tittle>静态Turbo默认值测试:Start")
    logging.info("<TC021><Description>支持静态turbo")
    key1 = RIGHT + DOWN * 8 + ENTER + DOWN * 6 + ENTER
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC021><Result>静态Turbo默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC021><Result>静态Turbo默认值测试:Fail")
        return
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['<Disabled>\s+Static Turbo'], 5):
        logging.info("<TC021><Result>静态Turbo默认值测试:Fail")
        return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER)
    serial.send_keys_with_delay(DOWN + ENTER)
    if not serial.to_highlight_option(DOWN, r'AutoManualDisabled', timeout=30):
        logging.info("<TC021><Result>静态Turbo默认值测试:Fail")
        return
    logging.info("<TC021><Result>静态Turbo默认值测试:Pass")
    return True


# Testcase_UFS_001,
def ufs(serial, ssh):
    logging.info("<TC022><Tittle>UFS默认值测试:Start")
    logging.info("<TC022><Description>支持UFS设置")
    key1 = F9 + Y + F10 + Y
    key2 = RIGHT + DOWN * 8 + ENTER + DOWN * 6 + ENTER
    key3 = DOWN * 2 + ENTER
    if not boot_to_bios_config(serial, ssh):
        logging.info("<TC022><Result>UFS默认值测试:Fail")
        return
    serial.send_keys(key1)
    if not Hy5BasicFunc.toBIOSnp(serial):
        logging.info("<TC022><Result>UFS默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC022><Result>UFS默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2)
    serial.send_keys_with_delay(key3)
    if not Hy5BasicFunc.verify_setup_options_up(serial, ['<Enabled>\s+UFS'], 4):
        logging.info("<TC022><Result>UFS默认值测试:Fail")
        return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER * 2)
    if not serial.to_highlight_option(DOWN, r'Disabled_MaxDisabled_Min', timeout=30):
        logging.info("<TC022><Result>UFS默认值测试:Fail")
        return
    logging.info("<TC022><Result>UFS默认值测试:Pass")
    return True


# Testcase_RRQIRQ_001
def rrQIRQ(serial, ssh):
    logging.info("<TC023><Tittle>Setup菜单RRQ和IRQ选项默认值测试:Start")
    logging.info("<TC023><Description>支持RRQ&IRQ设置")
    key1 = RIGHT + DOWN * 8 + ENTER + DOWN * 2 + ENTER * 2
    key2 = DOWN * 8 + ENTER + DOWN * 4 + ENTER
    key3 = DOWN * 9 + ENTER
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['Local/Remote Threshold\s+<Auto>'], 12):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    # if not serial.to_highlight_option(DOWN, r'Local/Remote Threshold', timeout=60):
    #     logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
    #     return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER)
    serial.send_keys_with_delay(DOWN * 8 + ENTER)
    if not serial.to_highlight_option(DOWN, r'DisabledAutoLowMediumHighManual', timeout=15):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER + DOWN * 4 + ENTER)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['\[7\]\s+IRQ Threshold', '\[7\]\s+RRQ Threshold'], 12):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER)
    serial.send_keys_with_delay(key2)
    serial.send_data('10')
    serial.send_keys_with_delay(ENTER + DOWN + ENTER)
    serial.send_data('20')
    serial.send_keys_with_delay(ENTER)
    serial.send_keys(F10 + Y)
    if not Hy5BasicFunc.toBIOSnp(serial):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC013><Result>Load default and setting saving Test:Fail")
        return
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['\[10\]\s+IRQ Threshold', '\[20\]\s+RRQ Threshold'], 12):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Pass")
    return True


# Testcase_DRAM_RAPL_001
def dramRAPL(serial, ssh):
    logging.info("<TC024><Tittle>菜单项DRAM RAPL选单检查:Start")
    logging.info("<TC024><Description>支持DRAM RAPL设置")
    key1 = RIGHT + DOWN * 8 + ENTER + DOWN * 6 + ENTER
    key2 = DOWN * 11 + ENTER * 2
    key3 = ENTER + DOWN + ENTER + UP
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    serial.send_keys_with_delay(key1)
    serial.send_keys_with_delay(key2)
    if not Hy5BasicFunc.verify_setup_options_up(serial, ['DRAM RAPL\s+<Enabled>'], 4):
        logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(key3)
    if not serial.to_highlight_option(DOWN, r'DisabledEnabled', timeout=30):
        logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Pass")
    return True


# Testcase_BiosPasswordSecurity_012, 013, 014
# 输入错误密码次数测试_阈值内输入错误密码, 输入错误密码次数测试_阈值内连续输入错误密码后输入正确密码和输入错误密码次数测试_超出阈值不影响下一次登录
def pwdSecurity(serial, ssh):
    logging.info("<TC025><Tittle>输入错误密码次数测试:Start")
    logging.info("<TC025><Description>输入错误密码次数测试包含密码错误，次数测试和超出阈值不影响下一次登录")
    if not pressDel(serial, ssh):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    for i in range(2):
        logging.info("Send wrong password...")
        serial.send_data(new_pwd_9)
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString(invalid_info, timeout=15):
            logging.info('<TC025><Result>输入错误密码次数测试:Fail')
            return
        serial.send_data(chr(0x0D))  # Send Enter
    logging.info('Send the right password...')
    serial.send_data(default_pwd)
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString('BIOS Configuration', timeout=60):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    serial.send_keys(Hy5BasicFunc.Key.CTRL_ALT_DELETE)
    if not pressDel(serial, ssh):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    for i in range(3):
        logging.info("Send wrong password...")
        serial.send_data(new_pwd_9)
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString(invalid_info, timeout=15):
            logging.info('<TC025><Result>输入错误密码次数测试:Fail')
            return
        serial.send_data(chr(0x0D))  # Send Enter
    if not serial.waitString(error_info, timeout=15):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    serial.send_keys(Hy5BasicFunc.Key.CTRL_ALT_DELETE)
    if not Hy5BasicFunc.toBIOSnp(serial):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    logging.info('<TC025><Result>输入错误密码次数测试:Pass')
    return True


# 检查CDN开关默认值
def cnd(serial, ssh):
    logging.info("<TC026><Tittle>检查CDN开关默认值:Start")
    logging.info("<TC026><Description>支持网口CDN特性开关")
    key1 = RIGHT + DOWN + ENTER
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC026><Result>检查CDN开关默认值:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC026><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['<Enabled>\s+Network CDN'], 12):
        logging.info("<TC026><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    logging.info("<TC026><Result>菜单项DRAM RAPL选单检查:Pass")
    return True


# Testcase_BiosPasswordSecurity_007, 019, 020, 021, 022
def pwdVerification1(serial, ssh):
    logging.info("<TC027><Tittle>密码修改验证:Start")
    logging.info("<TC027><Description>BIOS密码应满足产品网络安全要求")
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_keys_with_delay(key2PWD)
    if not serial.waitString(pwd_info_1, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    # Testcase_BiosPasswordSecurity_002 新密码长度小于最少字符数要求（8）
    serial.send_data(simple_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(invalid_info, timeout=15):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_1, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_2, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(weak_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_3, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(weak_pwd)
    serial.send_data(chr(0x0D))
    # 弱口令验证
    if not serial.waitString(simple_pwd_warning, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_1, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(default_pwd)
    serial.send_data(chr(0x0D))
    # Testcase_BiosPasswordSecurity_004 新密码长度大于最少字符数要求（8）
    serial.send_data(new_pwd_9)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_2, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(new_pwd_9)
    serial.send_data(chr(0x0D))
    time.sleep(0.2)
    if not serial.waitString(pwd_info_3, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    serial.send_data(new_pwd_9)
    serial.send_data(chr(0x0D))
    if not serial.waitString(pwd_info_4, timeout=30):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    if not Hy5BasicFunc.toBIOSnp(serial, new_pwd_9):
        logging.info("<TC027><Result>密码修改验证:Fail")
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    logging.info("<TC027><Result>密码修改验证:Pass")
    return True


# Testcase_BiosPasswordSecurity_003, 010 设置密码长度度测试_密码长度等于最少字符数(8)
def pwdVerification2(serial, ssh):
    logging.info("<TC028><Tittle>设置密码长度度测试:Start")
    logging.info("<TC028><Description>BIOS密码应满足产品网络安全要求")
    if not setPWD(serial, ssh, new_pwd_9, new_pwd_8):
        logging.info("<TC028><Result>设置密码长度度测试:Fail")
        return
    if not Hy5BasicFunc.toBIOSnp(serial, new_pwd_8):
        logging.info("<TC028><Result>设置密码长度度测试:Fail")
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    logging.info("<TC028><Result>设置密码长度度测试:Pass")
    return True


# Testcase_BiosPasswordSecurity_005, 006
def pwdVerification3(serial, ssh):
    logging.info("<TC029><Tittle>设置密码最大字符数测试:Start")
    logging.info("<TC029><Description>BIOS密码应满足产品网络安全要求")
    if not Hy5BasicFunc.toBIOS(serial, ssh, new_pwd_8):
        logging.info("<TC029><Result>设置密码最大字符数测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    serial.send_keys_with_delay(key2PWD)
    if not serial.waitString(pwd_info_1, timeout=15):
        return
    serial.send_data(new_pwd_17)
    serial.send_data(chr(0x0D))
    if not serial.waitString(invalid_info, timeout=15):
        logging.info("<TC029><Result>设置密码最大字符数测试:Fail")
        return
    serial.send_data(chr(0x0D))
    if not setPWDnp(serial, new_pwd_8, new_pwd_16):
        logging.info("<TC029><Result>设置密码最大字符数测试:Fail")
        return
    if not Hy5BasicFunc.toBIOSnp(serial, new_pwd_16):
        # logging.info("New pwd has failed to be verified, start to restore the test Env - update bios")
        # if not Hy5BasicFunc.Upgrade_Test(serial):
        #     return
        logging.info("<TC029><Result>设置密码最大字符数测试:Fail")
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    logging.info("<TC029><Result>设置密码最大字符数测试:Pass")
    return True


# Testcase_BiosPasswordSecurity_008, 009
def pwdVerification4(serial, ssh):
    logging.info("<TC030><Tittle>设置密码最大字符数测试:Start")
    logging.info("<TC030><Description>BIOS密码应满足产品网络安全要求")
    if not Hy5BasicFunc.toBIOS(serial, ssh, new_pwd_16):
        logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
        return
    serial.send_keys_with_delay(key2PWD)
    if not serial.waitString(pwd_info_1, timeout=15):
        logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
        return
    i = 0
    full_pwd_list = pwd_list1 + pwd_list2
    while i < len(full_pwd_list):
        serial.send_data(full_pwd_list[i])
        serial.send_data(chr(0x0D))
        logging.info('send the pwd:{0}'.format(full_pwd_list[i]))
        if len(full_pwd_list) == 8:
            if not serial.waitString(error_info, timeout=15):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not enterPWD(serial, new_pwd_16):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
        elif len(full_pwd_list) == 5:
            if not serial.waitString(error_info, timeout=15):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not enterPWD(serial, new_pwd_16):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
        elif len(full_pwd_list) == 2:
            if not serial.waitString(error_info, timeout=15):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not enterPWD(serial, new_pwd_16):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
        else:
            if not serial.waitString(invalid_info, timeout=15):
                logging.info("<TC030><Result>设置密码最大字符数测试:Fail")
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            serial.send_data(chr(0x0D))
            serial.send_data(chr(0x0D))

        i += 1
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    logging.info("<TC030><Result>设置密码最大字符数测试:Pass")
    return True


# Testcase_SimplePassword_001, 002, 003, 004 and 005
def simplePWDTest(serial, ssh):
    logging.info("<TC034><Tittle>简易密码开关默认值测试:Start")
    logging.info("<TC034><Description>支持关闭密码复杂度检测")
    if not Hy5BasicFunc.toBIOS(serial, ssh, new_pwd_16):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=30):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    serial.send_keys_with_delay(RIGHT * 3)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['<Disabled>\s+Simple Password'], 10):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    serial.send_keys_with_delay(LEFT + RIGHT + DOWN * 5 + ENTER + DOWN + ENTER * 2)
    time.sleep(0.2)
    serial.send_keys_with_delay(LEFT + RIGHT + DOWN)
    if not setPWDwithoutF10(serial, new_pwd_16, simple_pwd):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    if not checkPWD(serial, simple_pwd, new_pwd_16):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=30):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    serial.send_keys_with_delay(RIGHT * 3 + DOWN * 5 + ENTER + DOWN + ENTER * 2)
    time.sleep(0.2)
    serial.send_keys_with_delay(LEFT + RIGHT + DOWN)
    if not setPWDnp(serial, new_pwd_16, simple_pwd):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    if not checkPWD(serial, new_pwd_16, simple_pwd):
        logging.info("<TC034><Result>简易密码开关默认值测试:Fail")
        return
    logging.info("<TC034><Result>简易密码开关默认值测试:Pass")
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
    if not Hy5BasicFunc.Upgrade_Test(serial):
        return
    return True


# Testcase_SecurityBoot_001, 004
def securityBoot(serial, ssh):
    logging.info("<TC031><Tittle>Secure Boot默认值:Start")
    logging.info("<TC031><Description>支持Secure boot")
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC031><Result>Secure Boot默认值:Fail")
        return
    key1 = RIGHT + DOWN + ENTER
    serial.send_keys_with_delay(key1)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['Current Secure Boot State\s+Disabled'], 6):
        logging.info("<TC031><Result>Secure Boot默认值:Fail")
        return
    serial.send_keys_with_delay(Hy5BasicFunc.Key.ESC)
    serial.send_keys_with_delay(RIGHT + ENTER)
    serial.send_keys_with_delay(RIGHT * 4 + ENTER + DOWN + ENTER)
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    if not Hy5BasicFunc.toBIOSnp(serial):
        logging.info("<TC031><Result>Secure Boot默认值:Fail")
        return
    serial.send_keys_with_delay(RIGHT + DOWN + UP + DOWN)
    if serial.waitString('Administer Secure Boot', timeout=5):
        status = False
    else:
        logging.info("<TC031><Result>Secure Boot默认值:Pass")
        status = True
    logging.info('Restore the test Env...')
    if not reset_default(serial, ssh):
        return

    return status


# Testcase_TPM_001, 002, 005, 006, 009 TPM芯片测试 (单板已插TPM卡)
def tpm(serial, ssh):
    logging.info("<TC032><Tittle>TPM芯片测试:Start")
    logging.info("<TC032><Description>支持CBNT")
    key1 = LEFT * 2 + DOWN + ENTER + DOWN * 6
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=15):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        return
    serial.send_keys_with_delay(RIGHT * 3)
    if not Hy5BasicFunc.verify_setup_options_down(serial, tpm_info, 12):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        return
    serial.send_keys_with_delay(key1)
    serial.send_keys_with_delay(ENTER + DOWN + ENTER)
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    if not serial.waitString('DetectTpmDevice', timeout=120):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        if not reset_default(serial, ssh):
            return
    if not toSysTime(serial):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        if not reset_default(serial, ssh):
            return
    time.sleep(0.2)
    serial.send_keys(F9 + Y + F10 + Y)
    if not toSysTime(serial):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        return
    serial.send_keys_with_delay(RIGHT * 3)
    if not Hy5BasicFunc.verify_setup_options_down(serial, tpm_info, 10):
        logging.info("<TC032><Result>TPM芯片测试:Fail")
        return
    logging.info("<TC032><Result>TPM芯片测试:Pass")
    return True


# TXT + TPM Test Testcase_TPM_013 单板已插TPM卡 - 待在新板上验证，旧板不支持TXT（或rework板子开启TXT）
def txtTPM(serial, ssh):
    logging.info("<TC033><Tittle>TXT打开不影响TPM_硬盘等外设初始化:Start")
    logging.info("<TC033><Description>支持CBNT")
    key1 = RIGHT + DOWN + ENTER + DOWN * 6
    key2 = ENTER + DOWN + ENTER
    key3 = DOWN * 7 + ENTER * 2
    key4 = UP * 6 + ENTER + DOWN + ENTER
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC033><Result>TXT打开不影响TPM_硬盘等外设初始化:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=15):
        logging.info("<TC033><Result>TXT打开不影响TPM_硬盘等外设初始化:Fail")
        return
    serial.send_keys_with_delay(key1)
    serial.send_keys_with_delay(key2)
    serial.send_keys_with_delay(Hy5BasicFunc.Key.ESC)
    time.sleep(0.2)
    serial.send_keys_with_delay(key3)
    serial.send_keys_with_delay(key4)
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    if not serial.waitString('DetectTpmDevice', timeout=120):
        logging.info("<TC033><Result>TXT打开不影响TPM_硬盘等外设初始化:Fail")
        if not reset_default(serial, ssh):
            return
    if not toSysTime(serial):
        logging.info("<TC033><Result>TXT打开不影响TPM_硬盘等外设初始化:Fail")
        if not reset_default(serial, ssh):
            return
    serial.send_keys_with_delay(RIGHT * 3)
    if not Hy5BasicFunc.verify_setup_options_down(serial, tpm_info, 10):
        logging.info("<TC033><Result>TXT打开不影响TPM_硬盘等外设初始化:Fail")
        if not reset_default(serial, ssh):
            return
    logging.info("<TC033><Result>TXT打开不影响TPM_硬盘等外设初始化:Pass")
    if not reset_default(serial, ssh):
        return

    return True


# Testcase_VTD_002
def vtd(serial, ssh):
    logging.info("<TC037><Tittle>关闭VT-d功能启动测试:Start")
    logging.info("<TC037><Description>支持VT-d")
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC037><Result>关闭VT-d功能启动测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=60):
        logging.info("<TC037><Result>关闭VT-d功能启动测试:Fail")
        return
    serial.send_keys_with_delay(RIGHT + DOWN * 2 + ENTER * 3 + DOWN + ENTER)
    time.sleep(0.2)
    serial.send_keys(F10 + Y)
    if not serial.waitString('BIOS boot completed', timeout=300):   # OS flag TBD
        logging.info("<TC037><Result>关闭VT-d功能启动测试:Fail")
        return
    logging.info("<TC037><Result>关闭VT-d功能启动测试:Pass")
    return True

# Testcase_CPU_COMPA_015, 016 - TBD
def cpuCOMPA(serial, ssh):
    logging.info("<TC038><Tittle>UPI link链路检测测试:Start")
    logging.info("<TC038><Description>CPU兼容性测试")
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        logging.info("<TC038><Result>UPI link链路检测测试:Fail")
        return
    serial.send_keys_with_delay(key2Setup)
    if not serial.waitString('System Time', timeout=30):
        logging.info("<TC038><Result>UPI link链路检测测试:Fail")
        return
    serial.send_keys_with_delay(RIGHT + DOWN * 8 + ENTER + DOWN * 2 + ENTER * 3)
    if not Hy5BasicFunc.verify_setup_options_down(serial, upi_state, 4):
        logging.info("<TC038><Result>UPI link链路检测测试:Fail")
        return
    logging.info("<TC038><Result>UPI link链路检测测试:Pass")
    return True


# Testcase_LogTime_001, 002 and 003 串口日志打印
def logTime(serial, ssh, username='byo', pwd='1'):
    tc = ('039', '串口日志打印测试', '支持BIOS启动开始和结束信息打印及上报')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BasicFunc.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys(Hy5BasicFunc.Key.RIGHT)
    serial.send_data(chr(0x0D))
    if not serial.waitString('ubuntu', timeout=15):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.waitString('LTS byo-DH140-V6 ttyS0', timeout=300):
        result.log_fail()
        return
    serial.send_keys_with_delay(ENTER)
    time.sleep(0.1)
    serial.send_data(username)
    serial.send_data(chr(0x0D))
    time.sleep(0.1)
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString("$", timeout=15):
        result.log_fail()
        return
    serial.send_data("sudo hwclock --show")
    serial.send_data(chr(0x0D))
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))
    if not serial.is_msg_present_general('0800'):    # 0800 OS time zone
        result.log_fail()
        return
    serial.send_data('sudo reboot')
    serial.send_data(chr(0x0D))
    time.sleep(0.1)
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))
    if not serial.is_msg_present_general('BIOS Log', delay=60):
        result.log_fail()
        return
    with open(Hy5Config.SERIAL_LOG, 'r') as f:
        while True:
            try:
                line = f.readline()
                if '0800' in line:
                    t0 = line.split('.')[0]
                    t1 = datetime.datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')

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


# Main function
def biosSetupTest(serial, ssh):
    Load_Default_Test(serial, ssh)
    staticTurbo(serial, ssh)
    ufs(serial, ssh)
    rrQIRQ(serial, ssh)
    dramRAPL(serial, ssh)
    pwdSecurityTest(serial, ssh)
    securityBoot(serial, ssh)
    vtd(serial, ssh)
    cpuCOMPA(serial, ssh)
    logTime(serial, ssh)
    logging.info('Hy5 Setup test completed...')
