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

from ICX2P.IcxConfig import Key
from ICX2P import IcxConfig
from ICX2P.BaseLib import icx2pAPI
from Common import Misc
from Common.LogAnalyzer import LogAnalyzer

P = LogAnalyzer(IcxConfig.LOG_DIR)


# POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
def POST_Test(serial, ssh):  # POST: POST Log(TBD) and Information Check
    tc = ('002', 'POST Information Test', 'POST Information Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.force_reset(ssh):
        result.log_fail()
        return
    msg_list = [IcxConfig.msg, IcxConfig.msg1, IcxConfig.msg2, IcxConfig.msg3]
    if not serial.waitStrings(msg_list, timeout=300):  # 考虑到满载配置
        result.log_fail()
        return
    result.log_pass()
    return True


# PM: Warm reset n times, Cold reset n times and AC (TBD)
def PM(serial, ssh, n=5):
    tc = ('003', 'Power Control Test', 'Power Control Test')
    result = Misc.LogHeaderResult(tc, serial)
    status = 0
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    logging.info("Warm reset loops: {0}".format(n))
    for i in range(n):
        try:
            logging.info("Warm reset cycle: {0}".format(i + 1))
            serial.send_keys(Key.CTRL_ALT_DELETE)
            logging.debug("Ctrl + Alt + Del key sent")
            if not icx2pAPI.toBIOSnp(serial):
                logging.info("Warm reset Test:Fail")
                status = 1
                continue
        except Exception as e:
            logging.error(e)
    # DC cycle n times
    logging.info("Cold reset loops: {0}".format(n))
    for j in range(n):
        try:
            logging.info("DC reset cycle: {0}".format(j + 1))
            if not icx2pAPI.dcCycle(serial, ssh):
                logging.info("DC cycle Test:Fail")
                status = 2
                return
        except Exception as e:
            logging.error(e)
    if status == 1 and 2:
        result.log_fail()
        return

    result.log_pass()
    return True


# PXE Test
def pxeTest(serial, ssh, n=1):
    tc = ('004', 'PXE Test', 'PXE Test')
    result = Misc.LogHeaderResult(tc, serial)
    for i in range(n):
        if not icx2pAPI.pressF12(serial, ssh):
            result.log_fail()
            return
        if not serial.waitString('NBP file downloaded successfully', timeout=60):
            result.log_fail()
            return
    result.log_pass()
    return True


# Https Test
def httpsTest(serial, ssh):
    tc = ('005', 'Https Test', 'Https Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Key.RIGHT + Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.PXE_option, timeout=60):
        result.log_fail()
        return
    serial.send_data(IcxConfig.default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString('Start HTTPS Boot over IPv4', timeout=30):
        result.log_fail()
        return
    if not serial.waitString('Shell', timeout=60):
        result.log_fail()
        return
    result.log_pass()
    return True


# USB Test
def usbTest(serial, ssh):
    tc = ('006', 'USB Test', 'USB Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option1):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    msg_list = [IcxConfig.msg5, IcxConfig.msg6, IcxConfig.msg7]
    if not icx2pAPI.verify_setup_options_down(serial, msg_list, 7):
        result.log_fail()
        return
    result.log_pass()
    return True


# Processor/DIMM Test
def ProcessorDIMM(serial, ssh):
    tc = ('007', 'Processor/DIMM Test', 'CPU/DIMM Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option3):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option4):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.CPU_info, 20):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ESC, Key.ESC])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option5, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.DIMM_info, 20):
        result.log_fail()
        return
    result.log_pass()
    return True


# chipsec Test
def chipsecTest(serial, ssh):
    # username - OS user name, pwd - OS user password
    tc = ('008', 'chipsec Test', 'chipsec Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(IcxConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.OS, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
    if not icx2pAPI.chipsecMerge(ssh):
        result.log_fail()
        return
    result.log_pass()
    return True


# press F2
def pressF2(serial, ssh):
    tc = ('009', 'Setup菜单用户输入界面按F2切换键盘制式', '支持热键配置')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.force_reset(ssh):
        result.log_fail()
        return
    if not serial.waitString(IcxConfig.msg, timeout=300):
        result.log_fail()
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString("Press F2", timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.F2)
    if not serial.waitString('fr-FR'):
        result.log_fail()
        return
    serial.send_keys(Key.F2)
    if not serial.waitString('ja-JP'):
        result.log_fail()
        return
    serial.send_keys(Key.F2)
    if not serial.waitString('en-US'):
        result.log_fail()
        return
    serial.send_data("Admin@9000")
    serial.send_data(chr(0x0D))  # Send Enter
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if not serial.waitString('Continue', timeout=30):
        return
    result.log_pass()
    return True


def equipmentMode(serial, ssh):
    tc = ('010', 'Equipment Mode Test', '支持Equipment Mode')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.SUSE):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
    if not icx2pAPI.equipment(ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.SUSE):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
    cmd = 'dmidecode -t 128'
    path = IcxConfig.LOG_DIR
    icx2pAPI.dump_smbios(ssh, cmd)
    if not P.smbiosCheck(cmd, path, IcxConfig.SMBIOS_TEMPLATE):
        result.log_fail()
        return
    result.log_pass()
    return True


# check password, for password case only
def checkPWD(serial, pwd1, pwd2):
    if not icx2pAPI.pressDelnp(serial):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.invalid_info, timeout=30):
        return
    serial.send_data(chr(0x0D))
    serial.send_data('22222222')
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.invalid_info, timeout=30):
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
    tc = ('011', 'Load default and setting saving Test', 'BIOS Load default Test')
    result = Misc.LogHeaderResult(tc, serial)
    option_bfo = ['<UEFI Boot Type>', '<Boot Retry>']
    option_aft = ['<Legacy Boot Type>', '<Cold Boot>']
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2type)
    if not icx2pAPI.verify_setup_options_down(serial, option_bfo, 14):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, 'Boot Type'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    if not serial.to_highlight_option(Key.DOWN, 'Boot Fail Policy'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2type)
    if not icx2pAPI.verify_setup_options_down(serial, option_aft, 14):
        result.log_fail()
        if not icx2pAPI.reset_default(serial, ssh):
            return
    serial.send_keys_with_delay(IcxConfig.key2default)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        if not icx2pAPI.reset_default(serial, ssh):
            return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2type)
    time.sleep(1)
    if not icx2pAPI.verify_setup_options_down(serial, option_bfo, 14):
        result.log_fail()
        if not icx2pAPI.reset_default(serial, ssh):
            return
    result.log_pass()
    return True


# updated by arthur, Testcase_Static_Turbo_001
def staticTurbo(serial, ssh):
    tc = ('012', '静态Turbo默认值测试', '支持静态turbo')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, IcxConfig.option6):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.static_turbo, 5):
        result.log_fail()
        return
    serial.send_keys(IcxConfig.Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, 'Static Turbo', timeout=30):
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
    tc = ('013', 'UFS默认值测试', '支持UFS设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2default)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option6, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option8, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_up(serial, IcxConfig.ufs, 4):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, 'UFS', timeout=30):
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
    tc = ('014', 'Setup菜单RRQ和IRQ选项默认值测试', '支持RRQ&IRQ设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option9, timeout=30):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, IcxConfig.option12, 3):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.local_remote, 12):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, 'Local/Remote Threshold', timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'DisabledAutoLowMediumHigh'):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.F5, Key.F5, Key.F5, Key.F5])
    if not icx2pAPI.verify_setup_options_down(serial, ['\[7\]\s+IRQ Threshold', '\[7\]\s+RRQ Threshold'], 12):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, 'IRQ Threshold', timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    serial.send_data('10')
    serial.send_keys_with_delay([Key.ENTER, Key.DOWN, Key.ENTER])
    serial.send_data('20')
    serial.send_keys(Key.ENTER)
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option9, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.find_setup_option(Key.DOWN, IcxConfig.option12, 3):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_down(serial, ['\[10\]\s+IRQ Threshold', '\[20\]\s+RRQ Threshold'], 12):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_DRAM_RAPL_001
def dramRAPL(serial, ssh):
    tc = ('015', '菜单项DRAM RAPL选单检查', '支持DRAM RAPL设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, IcxConfig.option6):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.UP, IcxConfig.option11):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, 'DRAM RAPL Configuration', 7):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_up(serial, IcxConfig.dram, 4):
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
    tc = ('016', '输入错误密码次数测试', '输入错误密码次数测试包含密码错误，次数测试和超出阈值不影响下一次登录')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.pressDel(serial, ssh):
        result.log_fail()
        return
    for i in range(2):
        logging.info("Send wrong password...")
        serial.send_data(IcxConfig.new_pwd_9)
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString(IcxConfig.invalid_info, timeout=15):
            result.log_fail()
            return
        serial.send_data(chr(0x0D))  # Send Enter
    logging.info('Send the right password...')
    serial.send_data(IcxConfig.default_pwd)
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString('BIOS Configuration', timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not icx2pAPI.pressDel(serial, ssh):
        result.log_fail()
        return
    for i in range(3):
        logging.info("Send wrong password...")
        serial.send_data(IcxConfig.new_pwd_9)
        serial.send_data(chr(0x0D))  # Send Enter
        if not serial.waitString(IcxConfig.invalid_info, timeout=15):
            result.log_fail()
            return
        serial.send_data(chr(0x0D))  # Send Enter
    if not serial.waitString(IcxConfig.error_info, timeout=15):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    result.log_pass()
    return True


# 检查CDN开关默认值
def cnd(serial, ssh):
    tc = ('017', '检查CDN开关默认值', '支持网口CDN特性开关')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys(Key.RIGHT)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option7, timeout=30):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.cnd_status, 12):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_007, 019, 020, 021, 022
def pwdVerification1(serial, ssh):
    tc = ('018', '密码修改验证', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    # if not toBIOS(serial, ssh):
    #     result.log_fail()
    #     return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.pwd_item):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(IcxConfig.pwd_info_1, timeout=30):
        result.log_fail()
        return
    # Testcase_BiosPasswordSecurity_002 新密码长度小于最少字符数要求（8）
    serial.send_data(IcxConfig.simple_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.invalid_info, timeout=15):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.pwd_info_1, timeout=30):
        result.log_fail()
        return
    serial.send_data(IcxConfig.default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.pwd_info_2, timeout=30):
        result.log_fail()
        return
    serial.send_data(IcxConfig.weak_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.pwd_info_3, timeout=30):
        result.log_fail()
        return
    serial.send_data(IcxConfig.weak_pwd)
    serial.send_data(chr(0x0D))
    # 弱口令验证
    if not serial.waitString(IcxConfig.simple_pwd_warning, timeout=30):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.pwd_info_1, timeout=30):
        result.log_fail()
        return
    serial.send_data(IcxConfig.default_pwd)
    serial.send_data(chr(0x0D))
    # Testcase_BiosPasswordSecurity_004 新密码长度大于最少字符数要求（8）
    serial.send_data(IcxConfig.new_pwd_9)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.pwd_info_2, timeout=30):
        result.log_fail()
        return
    serial.send_data(IcxConfig.new_pwd_9)
    serial.send_data(chr(0x0D))
    time.sleep(1)
    if not serial.waitString(IcxConfig.pwd_info_3, timeout=30):
        result.log_fail()
        return
    serial.send_data(IcxConfig.new_pwd_9)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.pwd_info_4, timeout=30):
        result.log_fail()
        return
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial, IcxConfig.new_pwd_9):
        result.log_fail()
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_003, 010 设置密码长度度测试_密码长度等于最少字符数(8)
def pwdVerification2(serial, ssh):
    tc = ('019', '设置密码长度度测试', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.setPWD(serial, ssh, IcxConfig.new_pwd_9, IcxConfig.new_pwd_8):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSnp(serial, IcxConfig.new_pwd_8):
        result.log_fail()
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_005, 006
def pwdVerification3(serial, ssh):
    tc = ('020', '设置密码最大字符数测试', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh, IcxConfig.new_pwd_8):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.pwd_item):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(IcxConfig.pwd_info_1, timeout=15):
        result.log_fail()
        return
    serial.send_data(IcxConfig.new_pwd_17)
    serial.send_data(chr(0x0D))
    if not serial.waitString(IcxConfig.invalid_info, timeout=15):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not icx2pAPI.setPWDnp(serial, IcxConfig.new_pwd_8, IcxConfig.new_pwd_16):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSnp(serial, IcxConfig.new_pwd_16):
        result.log_fail()
        return
    logging.info("新密码验证成功，将在最后一个密码修改用例里恢复环境")
    result.log_pass()
    return True


# Testcase_BiosPasswordSecurity_008, 009
def pwdVerification4(serial, ssh):
    tc = ('021', '设置密码最大字符数测试', 'BIOS密码应满足产品网络安全要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh, IcxConfig.new_pwd_16):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.pwd_item):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(IcxConfig.pwd_info_1, timeout=15):
        result.log_fail()
        return
    i = 0
    full_pwd_list = IcxConfig.pwd_list1 + IcxConfig.pwd_list2
    while i < len(full_pwd_list):
        serial.send_data(full_pwd_list[i])
        serial.send_data(chr(0x0D))
        logging.info('send the pwd:{0}'.format(full_pwd_list[i]))
        if len(full_pwd_list) == 8:
            if not serial.waitString(IcxConfig.error_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not icx2pAPI.enterPWD(serial, IcxConfig.new_pwd_16):
                result.log_fail()
                return
        elif len(full_pwd_list) == 5:
            if not serial.waitString(IcxConfig.error_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not icx2pAPI.enterPWD(serial, IcxConfig.new_pwd_16):
                result.log_fail()
                return
        elif len(full_pwd_list) == 2:
            if not serial.waitString(IcxConfig.error_info, timeout=15):
                result.log_fail()
                return
            full_pwd_list.remove(full_pwd_list[i])
            i -= 1
            if not icx2pAPI.enterPWD(serial, IcxConfig.new_pwd_16):
                result.log_fail()
                return
        else:
            if not serial.waitString(IcxConfig.invalid_info, timeout=15):
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
    tc = ('022', '简易密码开关默认值测试', '支持关闭密码复杂度检测')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh, IcxConfig.new_pwd_16):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.simplePWD_info, 10):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.RIGHT])
    time.sleep(1)
    if not serial.to_highlight_option(Key.UP, IcxConfig.pwd_item1, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    if not serial.waitString(IcxConfig.enable_simple_pwd, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, IcxConfig.pwd_item, timeout=30):
        result.log_fail()
        return
    if not icx2pAPI.setPWDwithoutF10(serial, IcxConfig.new_pwd_16, IcxConfig.simple_pwd):
        result.log_fail()
        return
    if not checkPWD(serial, IcxConfig.simple_pwd, IcxConfig.new_pwd_16):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    time.sleep(1)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.pwd_item1, timeout=30):
        return
    serial.send_keys(Key.F5)
    if not serial.waitString(IcxConfig.enable_simple_pwd, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, IcxConfig.pwd_item, timeout=30):
        result.log_fail()
        return
    if not icx2pAPI.setPWDnp(serial, IcxConfig.new_pwd_16, IcxConfig.simple_pwd):
        result.log_fail()
        return
    if not checkPWD(serial, IcxConfig.new_pwd_16, IcxConfig.simple_pwd):
        result.log_fail()
        return
    result.log_pass()
    return True


# 整合密码测试
def pwdSecurityTest(serial, ssh, dst):
    pwdSecurity(serial, ssh)
    pwdVerification1(serial, ssh)
    pwdVerification2(serial, ssh)
    pwdVerification3(serial, ssh)
    pwdVerification4(serial, ssh)
    simplePWDTest(serial, ssh)
    logging.info("密码组合和简易设置验证完成，当前为最后一个密码修改用例，开始恢复环境:更新BIOS")
    if not icx2pAPI.restore_env(serial, dst):
        pass

    return True


# Testcase_SecurityBoot_001, 004
def securityBoot(serial, ssh):
    tc = ('023', 'Secure Boot默认值', 'Secure Boot默认值')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    key1 = [Key.RIGHT, Key.DOWN, Key.ENTER]
    serial.send_keys_with_delay(key1)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.secure_status, 6):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.RIGHT, Key.ENTER])
    serial.send_keys_with_delay([Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, 'Boot Type'):
        result.log_fail()
        return
    serial.send_keys(Key.F5)
    time.sleep(0.1)
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        icx2pAPI.reset_default(serial, ssh)
        return
    serial.send_keys_with_delay(key1)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.secure_status, 6):
        icx2pAPI.reset_default(serial, ssh)
        result.log_fail()
        return
    logging.info('Restore the test Env...')
    icx2pAPI.reset_default(serial, ssh)
    result.log_pass()
    return True


# Testcase_TPM_001, 002, 005, 006, 009 TPM芯片测试 (单板已插TPM卡)
# TXT + TPM Test Testcase_TPM_013 单板已插TPM卡 - 待在新板上验证，旧板不支持TXT（或rework板子开启TXT）
def tpm(serial, ssh):
    tc = ('024', 'TPM芯片测试', '支持CBNT')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.tpm_info, 12):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.LEFT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option3):
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
        if not icx2pAPI.reset_default(serial, ssh):
            return
    if not icx2pAPI.toSysTime(serial):
        result.log_fail()
        if not icx2pAPI.reset_default(serial, ssh):
            return
    serial.send_keys(IcxConfig.key2default)
    if not icx2pAPI.toSysTime(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2pwd)
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.tpm_info, 10):
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
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.pat, 'Intel'):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    serial.send_keys(Key.F5)
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.ping_sut():  # OS flag
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_CPU_COMPA_015, 016 - TBD
def cpuCOMPA(serial, ssh):
    tc = ('026', 'UPI link链路检测测试', 'CPU兼容性测试')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option9):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, IcxConfig.option12, 4):
        result.log_fail()
        return
    serial.send_keys(Key.UP)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option14):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not icx2pAPI.verify_setup_options_down(serial, IcxConfig.upi_state, 4):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_LogTime_001, 002 and 003 串口日志打印
def logTime(serial, ssh):
    tc = ('027', '串口日志打印测试', '支持BIOS启动开始和结束信息打印及上报')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.OS, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
    t1 = icx2pAPI.osTime(ssh)
    if not serial.is_msg_present_general('BIOS Log', delay=60):
        result.log_fail()
        return
    with open(IcxConfig.SERIAL_LOG, 'r') as f:
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
    tc = ('028', 'Setup菜单关核选项测试', '支持CPU关核')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option3):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_up(serial, ['<All>\s+Active Processor Cores'], 7):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, 'Active Processor Cores'):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.UP, r'1234567891011121314151617All', timeout=15):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.F6, Key.F6])
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(IcxConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, IcxConfig.option5):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_up(serial, IcxConfig.DIMM_info, 20):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
    if not icx2pAPI.chipsecMerge(ssh):
        result.log_fail()
        return
    cmd = 'dmidecode -t 4'
    path = IcxConfig.LOG_DIR
    icx2pAPI.dump_smbios(ssh, cmd)
    if not P.smbiosCheck(cmd, path, IcxConfig.SMBIOS_TEMPLATE):
        result.log_fail()
        return
    result.log_pass()
    return True


# Main function
def icxbiosTest(serial, ssh, dst, n=1):
    for i in range(n):
        logging.info("BIOS Setup Test Cycle: {0}".format(i + 1))
        POST_Test(serial, ssh)
        PM(serial, ssh)
        pxeTest(serial, ssh)
        httpsTest(serial, ssh)
        usbTest(serial, ssh)
        ProcessorDIMM(serial, ssh)
        chipsecTest(serial, ssh)
        pressF2(serial, ssh)
        loadDefault(serial, ssh)
        staticTurbo(serial, ssh)
        ufs(serial, ssh)
        rrQIRQ(serial, ssh)
        dramRAPL(serial, ssh)
        pwdSecurityTest(serial, ssh, dst)
        securityBoot(serial, ssh)
        vtd(serial, ssh)
        cpuCOMPA(serial, ssh)
        logTime(serial, ssh)
    logging.info('ICX BIOS test completed...')
