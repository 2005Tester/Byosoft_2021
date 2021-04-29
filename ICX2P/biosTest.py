#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import re
import time
from Core import SerialLib
from ICX2P.Config.SutConfig import SysCfg
from ICX2P.Config.PlatConfig import Msg, Key
from ICX2P.Config import SutConfig
from ICX2P.BaseLib import PowerLib, icx2pAPI, SetUpLib
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
    res_lst = []
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
                flag_reset = 1
                res_lst.append(flag_reset)
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
                flag_dc = 2
                res_lst.append(flag_dc)
                return
        except Exception as e:
            logging.error(e)
    logging.debug(res_lst)
    if len(res_lst) != 0:
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


# USB Test
# Precondition: No USB key installed
# OnStart: NA
# OnComplete: USB Configuration Page
def usbTest(serial, ssh):
    tc = ('006', '[TC006]USB Test', 'USB Test')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    msg_list = ['USB Mouse\s+1', 'USB Keyboard\s+1', 'USB Mass Storage\s+0']
    if not icx2pAPI.toBIOS(serial, ssh):
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_USB_CFG, 10, 'USB'):
        result.log_fail(capture=True)
        return

    if not SetUpLib.verify_info(serial, msg_list, 7):
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
    serial.send_data(SutConfig.BIOS_PASSWORD)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if not serial.waitString('Continue', timeout=30):
        return
    result.log_pass()
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


# Testcase_DRAM_RAPL_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup DRAM RAPL page
def dram_rapl_option_check(serial, ssh):
    tc = ('015', '[TC015]Testcase_DRAM_RAPL_001, 菜单项DRAM RAPL选单检查', '支持DRAM RAPL设置')
    result = ReportGen.LogHeaderResult(tc, serial)
    """
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    import os
    os.system('pause')
    """

    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_DRAM_RAPL, 20, Msg.DRAM_RAPL_CONFIG):
        result.log_fail()
        return

    if not icx2pAPI.verify_setup_options_up(serial, SutConfig.dram, 4):
        result.log_fail()
        return
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, r'DisabledEnabled', 10):
        result.log_fail()
        return
    result.log_pass()
    return True


# 检查CDN开关默认值
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Miscellaneous Configuration page
def cnd_default_enable(serial, ssh):
    tc = ('017', '[TC017]检查CDN开关默认值', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys(Key.RIGHT)
    if not SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MISC_CONFIG], 20, 'Miscellaneous'):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.cnd_status, 12):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_SecurityBoot_001
def securityBoot(serial, ssh):
    tc = ('023', 'Secure Boot默认值', 'Secure Boot默认值')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    keys_secure_boot = [Key.RIGHT, Key.DOWN, Key.ENTER]
    secureboot_disable = ['Current Secure Boot State\s+Disabled']
    if not SetUpLib.boot_to_setup(serial, ssh):
        result.log_fail(capture=True)
        return
    logging.info("Enter secure boot configuration.")
    SerialLib.send_keys_with_delay(serial, keys_secure_boot)
    logging.info("Checking secure boot status")
    if not SetUpLib.verify_info(serial, secureboot_disable, 5):
        result.log_fail(capture=True)
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
    if not serial.is_msg_present("Disabled"):
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


# 检查串口log关键信息打印，包括 CPU资源分配 / BIOS版本信息 / PCIE LINK STATUS
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_SerialPrint_001(serial, ssh_bmc):
    tc = ('026', '[TC026]Testcase_SerialPrint_001', '启动关键信息打印测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    cpu_resource = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Stk07" for n in range(SysCfg.CPU_CNT)])
    bios_ver = r"BIOS Revision :\s+\d.\d+"
    pcie_lnk = r"PCIE LINK STATUS:"

    def check_process(timeout):
        assert PowerLib.force_reset(ssh_bmc)
        # CPU Resource Allocation
        cpu_log = SerialLib.cut_log(serial, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 100, timeout, 5)
        logging.debug(cpu_log)
        assert re.search(cpu_resource, cpu_log), "CPU Resource Allocation not found"
        logging.info("CPU Resource Allocation check pass")
        # BIOS Revision
        ver_log = SerialLib.cut_log(serial, "BootType :", "BIOS Date :", 100, timeout, 3)
        logging.debug(ver_log)
        assert re.search(bios_ver, ver_log), "BIOS Revision not found"
        logging.info("BIOS Revision check pass")
        # PCIE LINK STATUS
        pcie_log = SerialLib.cut_log(serial, "EFI1711", "Press Del go to Setup Utility", 100, timeout, 3)
        logging.debug(pcie_log)
        assert re.search(pcie_lnk, pcie_log), "PCIE LINK STATUS not found"
        logging.info("PCIE LINK STATUS check pass")
        return True

    try:
        # Open serial debug message
        assert icx2pAPI.debug_message(ssh_bmc, True)
        assert check_process(timeout=600)
        # Close serial debug message
        assert icx2pAPI.debug_message(ssh_bmc, False)
        assert check_process(timeout=200)
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        result.log_fail()


# 检查串口log打印没有任何错误信息：由于DebugMessage有太多干扰项，系统发生故障时默认打印级别就会打印，因此直接默认模式检查
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_SerialPrint_002(serial, ssh_bmc):
    tc = ('027', '[TC027]Testcase_SerialPrint_003', 'BIOS启动阶段串口报错检查')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    error_msg = ["error", "fail", "assert", "exception"]
    ignore_list = ["IdFromBmc Fail,Status: Device Error"]
    try:
        assert PowerLib.force_reset(ssh_bmc)
        ser_log = SerialLib.cut_log(serial, "BIOS Log @", Msg.BIOS_BOOT_COMPLETE, 120, 120, 3)
        for line in ser_log.split("\n"):
            for err in error_msg:
                if not re.search(err, line, re.I):  # 检查错误信息， 忽略大小写
                    continue
                logging.debug(line)
                for ig in ignore_list:
                    assert re.search(ig, line), line  # 排除例外
        result.log_pass()
        return True
    except AssertionError as e:
        logging.info(e)
        result.log_fail()
