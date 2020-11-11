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
# common error msg
error_info = 'Enter incorrect password 3 times,System Locked'


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    logging.info("HaiYan5 Common Test Lib: boot to setup")
    logging.info("Rebooting SUT...")
    if not Hy5TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.hotkey_del():
        logging.info("Boot to setup failed.")
        return
    return True


# Boot to boot manager without a force reset
def continue_to_bootmanager(serial):
    logging.info("HaiYan5 Common TC: continue boot to bootmanager")
    if not serial.hotkey_f11():
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
    logging.info("<TC005><Tittle>Check ME State:Start")
    logging.info("<TC005><Description>Verify ME state in operational mode")
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
        logging.info("<TC005><Result>Check ME State:Fail")
        return
    logging.info("<TC005><Result>Check ME State:Pass")
    return True


# Enable full debug message
def enable_full_debug_msg(serial, ssh):
    logging.info("<TC006><Tittle>Enable full debug message:Start")
    logging.info("<TC006><Description>Enable serial full debug message")
    keys_enable_full_debug = RIGHT + DOWN + ENTER + DOWN * 6 + F5 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys_enable_full_debug)
    if not serial.is_msg_present('^InstallProtocolInterface.'):
        return
    if not serial.is_msg_present('BIOS boot completed.'):
        logging.info("<TC006><Result>Enable full debug message:Fail")
        return
    logging.info("<TC006><Result>Enable full debug message:Pass")
    return True


# Disable full debug message
def disable_full_debug_msg(serial, ssh):
    logging.info("<TC007><Tittle>Disable full debug message:Start")
    logging.info("<TC007><Description>Disable serial full debug message")
    keys_enable_full_debug = RIGHT + DOWN + ENTER + DOWN * 6 + F6 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys_enable_full_debug)
    if not serial.is_msg_not_present('^InstallProtocolInterface.', 'BIOS boot completed.'):
        logging.info("<TC007><Result>Disable full debug message:Fail")
        return
    logging.info("<TC007><Result>Disable full debug message:Pass")
    return True


# Enable legacy boot
def enable_legacy_boot(serial, ssh):
    logging.info("<TC008><Tittle>Enable Legacy Boot:Start")
    logging.info("<TC008><Description>Enable Legacy Boot")
    keys = RIGHT * 4 + F5 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('Start of legacy boot'):
        logging.info("<TC008><Result>Enable Legacy boot:Fail")
        return
    logging.info("<TC008><Result>Enable Legacy boot:Pass")
    return True


# Disable legacy boot
def disable_legacy_boot(serial, ssh):
    logging.info("<TC009><Tittle>Disable Legacy Boot:Start")
    logging.info("<TC009><Description>Disable Legacy Boot")
    keys = RIGHT * 4 + F6 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_not_present('Start of legacy boot', 'BIOS boot completed.'):
        logging.info("<TC009><Result>Disable Legacy boot:Fail")
        return
    logging.info("<TC009><Result>Disable Legacy boot:Pass")
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
    serial.send_keys_with_delay(DOWN + ENTER + UP)
    if not serial.waitString('Manual', timeout=60):
        logging.info("<TC021><Result>静态Turbo默认值测试:Fail")
        return
    serial.send_keys_with_delay(UP)
    if not serial.waitString('Auto', timeout=60):
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
    serial.send_keys_with_delay(ENTER)
    serial.send_keys_with_delay(ENTER + DOWN)
    if not serial.waitString('Disabled_Max', timeout=60):
        logging.info("<TC022><Result>UFS默认值测试:Fail")
        return
    serial.send_keys_with_delay(DOWN)
    if not serial.waitString('Disabled_Min', timeout=60):
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
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER)
    serial.send_keys_with_delay(key2)
    if not Hy5BasicFunc.verify_setup_options_down(serial, ['\[7\]\s+IRQ Threshold', '\[7\]\s+RRQ Threshold'], 12):
        logging.info("<TC023><Result>Setup菜单RRQ和IRQ选项默认值测试:Fail")
        return
    serial.send_keys_with_delay(Hy5Config.Key.ESC)
    serial.send_keys_with_delay(ENTER)
    serial.send_keys_with_delay(key3)
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
    if not serial.waitString('Disabled', timeout=60):
        logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Fail")
        return
    logging.info("<TC024><Result>菜单项DRAM RAPL选单检查:Pass")
    return True


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
        serial.send_data("Admin@900X")
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString('Invalid Password', timeout=15):
            logging.info('<TC025><Result>输入错误密码次数测试:Fail')
            return
        serial.send_data(chr(0x0D))  # Send Enter
    logging.info('Send the right password...')
    serial.send_data('Admin@9000')
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString('BIOS Configuration', timeout=60):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    if not pressDel(serial, ssh):
        logging.info('<TC025><Result>输入错误密码次数测试:Fail')
        return
    for i in range(3):
        logging.info("Send wrong password...")
        serial.send_data("Admin@900X")
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString('Invalid Password', timeout=15):
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
