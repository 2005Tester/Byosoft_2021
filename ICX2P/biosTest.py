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
from ICX2P.SutConfig import Key, Msg
from ICX2P import SutConfig
from ICX2P.BaseLib import PowerLib, icx2pAPI, SetUpLib, SerialLib
from Report import ReportGen
from Common.LogAnalyzer import LogAnalyzer

P = LogAnalyzer(SutConfig.LOG_DIR)


# POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
def POST_Test(serial, ssh):  # POST: POST Log(TBD) and Information Check
    tc = ('002', 'POST Information Test', 'POST Information Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not PowerLib.force_reset(ssh):
        result.log_fail()
        return
    msg_list = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F6]
    if not serial.waitStrings(msg_list, timeout=300):  # 考虑到满载配置
        result.log_fail()
        return
    result.log_pass()
    return True


# PM: Warm reset n times, Cold reset n times and AC (TBD)
def PM(serial, ssh, n=5):
    tc = ('003', 'Power Control Test', 'Power Control Test')
    result = ReportGen.LogHeaderResult(tc, serial)
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
    result = ReportGen.LogHeaderResult(tc, serial)
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
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Key.RIGHT + Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.PXE_option, timeout=60):
        result.log_fail()
        return
    serial.send_data(SutConfig.default_pwd)
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
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option1):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    msg_list = [SutConfig.msg5, SutConfig.msg6, SutConfig.msg7]
    if not icx2pAPI.verify_setup_options_down(serial, msg_list, 7):
        result.log_fail()
        return
    result.log_pass()
    return True


# Processor/DIMM Test
def ProcessorDIMM(serial, ssh):
    tc = ('007', 'Processor/DIMM Test', 'CPU/DIMM Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option3):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option4):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.CPU_info, 20):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ESC, Key.ESC])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option5, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.DIMM_info, 20):
        result.log_fail()
        return
    result.log_pass()
    return True


# chipsec Test
def chipsecTest(serial, ssh):
    # username - OS user name, pwd - OS user password
    tc = ('008', 'chipsec Test', 'chipsec Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(SutConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.OS, timeout=30):
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
    result = ReportGen.LogHeaderResult(tc, serial)
    if not PowerLib.force_reset(ssh):
        result.log_fail()
        return
    if not serial.waitString(Msg.HOTKEY_PROMPT_DEL, timeout=300):
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
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.SUSE):
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
    serial.send_keys_with_delay(SutConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.SUSE):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
    cmd = 'dmidecode -t 128'
    path = SutConfig.LOG_DIR
    icx2pAPI.dump_smbios(ssh, cmd)
    if not P.smbiosCheck(cmd, path, SutConfig.SMBIOS_TEMPLATE):
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
    if not serial.waitString(SutConfig.invalid_info, timeout=30):
        return
    serial.send_data(chr(0x0D))
    serial.send_data('22222222')
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.invalid_info, timeout=30):
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
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    pxe_boot = ["PXE Boot Capability", "<UEFI:IPv4>"]
    boot_fail_policy = ["Boot Fail Policy", "<Boot Retry>"]
    pxe_boot_2 = ["PXE Boot Capability", "<UEFI:IPv6>"]
    boot_fail_policy_2 = ["Boot Fail Policy", "<Cold Boot>"]
    default_options = [boot_fail_policy, pxe_boot]
    changed_options = [boot_fail_policy_2, pxe_boot_2]
    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return

    # change option boot fail policy from "Boot Retry" to "Cold Boot"
    logging.info("change option boot fail policy from Boot Retry to Cold Boot")
    if not SetUpLib.locate_option(serial, Key.DOWN, boot_fail_policy, 15):
        result.log_fail(capture=True)
        return
    SerialLib.send_key(serial, Key.F5)
    result.capture_screen()

    # change pxe option from IPV4 to IPV6
    logging.info("change pxe option from IPV4 to IPV6")
    if not SetUpLib.locate_option(serial, Key.DOWN, pxe_boot, 15):
        result.log_fail(capture=True)
        return
    SerialLib.send_key(serial, Key.F5)
    result.capture_screen()

    logging.info("Save and reset.")
    SerialLib.send_keys_with_delay(serial, [Key.F10, Key.Y])
    time.sleep(15)

    # Verify modified options
    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return
    result.capture_screen()
    if not SetUpLib.verify_options(serial, Key.DOWN, changed_options, 15):
        result.log_fail(capture=True)
        return
    logging.info("Modified options are verified.")

    logging.info("Reset defaul by hotkey")
    SerialLib.send_keys_with_delay(serial, [Key.F9, Key.Y, Key.F10, Key.Y], delay=5)
    result.capture_screen()
    time.sleep(15)

    # Verify whether options are reset to default
    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return
    result.capture_screen()
    if not SetUpLib.verify_options(serial, Key.DOWN, default_options, 15):
        result.log_fail(capture=True)
        return
    result.capture_screen()

    result.log_pass()
    return True


# updated by arthur, Testcase_Static_Turbo_001
def staticTurbo(serial, ssh):
    tc = ('012', 'Testcase_Static_Turbo_001', '静态Turbo默认值测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail(capture=True)
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail(capture=True)
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail(capture=True)
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, SutConfig.option6):
        result.log_fail(capture=True)
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.static_turbo, 5):
        result.log_fail(capture=True)
        return
    serial.send_keys(SutConfig.Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pat, 'Static Turbo', timeout=30):
        result.log_fail(capture=True)
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'AutoManualDisabled'):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


# Testcase_UFS_001,
def ufs(serial, ssh):
    tc = ('013', 'Testcase_UFS_001', 'UFS默认值测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.key2default)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option6, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option8, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_up(serial, SutConfig.ufs, 4):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pat, 'UFS', timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'Disabled_MaxDisabled_Min'):
        result.log_fail()
        return
    result.log_pass()
    return True




# Testcase_DRAM_RAPL_001
def dramRAPL(serial, ssh):
    tc = ('015', 'Testcase_DRAM_RAPL_001, 菜单项DRAM RAPL选单检查', '支持DRAM RAPL设置')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.UP, SutConfig.option6):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.UP, SutConfig.option11):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, 'DRAM RAPL Configuration', 7):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_up(serial, SutConfig.dram, 4):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.verify_option_value(Key.DOWN, r'DisabledEnabled', timeout=30):
        result.log_fail()
        return
    result.log_pass()
    return True


# 检查CDN开关默认值
def cnd(serial, ssh):
    tc = ('017', '检查CDN开关默认值', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys(Key.RIGHT)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option7, timeout=30):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.cnd_status, 12):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_SecurityBoot_001, 004
def securityBoot(serial, ssh):
    tc = ('023', 'Secure Boot默认值', 'Secure Boot默认值')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    key1 = [Key.RIGHT, Key.DOWN, Key.ENTER]
    serial.send_keys_with_delay(key1)
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.secure_status, 6):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.RIGHT, Key.ENTER])
    serial.send_keys_with_delay([Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pat, 'Boot Type'):
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
    if serial.waitString('Current Secure Boot State'):
        result.log_fail()
        return
    icx2pAPI.reset_default(serial, ssh)
    result.log_pass()
    return True


# Testcase_TPM_001, 002, 005, 006, 009 TPM芯片测试 (单板已插TPM卡)
# TXT + TPM Test Testcase_TPM_013 单板已插TPM卡 - 待在新板上验证，旧板不支持TXT（或rework板子开启TXT）
def tpm(serial, ssh):
    tc = ('024', 'TPM芯片测试', '支持CBNT')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.key2pwd)
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.tpm_info, 12):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.LEFT, Key.LEFT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option3):
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
    serial.send_keys(SutConfig.key2default)
    if not icx2pAPI.toSysTime(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.key2pwd)
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.tpm_info, 10):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_VTD_002
def vtd(serial, ssh):
    tc = ('025', 'Testcase_VTD_002', '关闭VT-d功能启动测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    vt_d_menu = ["Virtualization Configuration", "Intel\(R\) VT for Directed I/O \(VT-d\)"]
    if not SetUpLib.enter_menu(serial, Key.DOWN, vt_d_menu, 20, "Directed"):
        logging.info("Failed to vir config")
        result.log_fail()
        return
    opt_vt = ["Intel\(R\) VT for Directed I/O", "<Enabled>"]
    if not SetUpLib.locate_option(serial, Key.DOWN, opt_vt, 4):
        result.log_fail()
        return
    logging.info("Diasble VT-d")
    serial.send_keys(Key.F5)
    time.sleep(1)
    logging.info("Verify VT-d is disabled")
    serial.send_keys_with_delay([Key.UP, Key.DOWN])   # Refresh page
    if not serial.is_msg_present("<Disabled>\s+Intel"):
        logging.info("VT-d option is not disaled.")
        result.log_fail()
        return
    logging.info("Save and reboot")
    serial.send_keys(Key.F10 + Key.Y)
    logging.info("Verify OS boot with VT-D disabled.")
    if not serial.is_msg_present(Msg.BIOS_BOOT_COMPLETE):
        logging.info("OS boot failed")
        result.log_fail()
        return

    result.log_pass()
    return True


# Testcase_CPU_COMPA_015, 016 - TBD
def cpuCOMPA(serial, ssh):
    tc = ('026', 'UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option9):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, SutConfig.option12, 4):
        result.log_fail()
        return
    serial.send_keys(Key.UP)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option14):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.upi_state, 4):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_LogTime_001, 002 and 003 串口日志打印
def logTime(serial, ssh):
    tc = ('027', 'Testcase_LogTime_001, 002 and 003, 串口日志打印测试', '支持BIOS启动开始和结束信息打印及上报')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.key2OS)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.OS, timeout=30):
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
    with open(SutConfig.SERIAL_LOG, 'r') as f:
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


# unitool
def auto_unitool_loop(serial, ssh):
    tc = ('061', 'auto unitool loop', '支持unitool loop')
    result = ReportGen.LogHeaderResult(tc, serial)
    f = os.listdir(SutConfig.INI_DIR)
    status = 0
    for root, dirs, files in os.walk(SutConfig.INI_DIR):
        for file in files:
            print(file)
            fw = open(os.path.join('{0}/written_ini'.format(SutConfig.INI_DIR), file), 'rb')
            data = fw.read().decode()
            for i in data.split('\r\n'):
                # print(i)
                if i == '':
                    pass
                else:
                    print(i)
                    if not icx2pAPI.toBIOS(serial, ssh):
                        result.log_fail()
                        return
                    serial.send_keys_with_delay(SutConfig.key2OS)
                    if not serial.find_setup_option(Key.DOWN, SutConfig.SUSE, 10):
                        result.log_fail()
                        return
                    if not icx2pAPI.ping_sut():
                        result.log_fail()
                        return
                    time.sleep(1)
                    ini_data = i
                    if not icx2pAPI.unitool(ssh, ini_data):
                        result.log_fail()
                        return
                    if icx2pAPI.toBIOSnp(serial):
                        serial.send_keys_with_delay(SutConfig.key2OS)
                        if not serial.find_setup_option(Key.DOWN, SutConfig.SUSE, 10):
                            result.log_fail()
                            return
                        if not icx2pAPI.ping_sut():
                            result.log_fail()
                            status = 1
                            icx2pAPI.clearCMOS(ssh)
                            continue
                    else:
                        status = 2
                        icx2pAPI.clearCMOS(ssh)
                        continue
            fw.close()
        print(status)

    logging.debug(status)
    if status == 1 | 2:
        result.log_fail()
        return

    result.log_pass()
    return True


# Main function
def icxbiosTest(serial, ssh, dst):
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
