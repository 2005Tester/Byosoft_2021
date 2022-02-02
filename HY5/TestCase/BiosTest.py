#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import os
from batf import core, SerialLib, MiscLib, SshLib
from batf.SutInit import Sut
from HY5.Config.PlatConfig import Msg, Key
from HY5.Config import SutConfig
from HY5.BaseLib import SetUpLib, BmcLib
from HY5.BaseLib.PlatMisc import ReleaseTest
from batf.Report import ReportGen, stylelog
from batf.Common.LogAnalyzer import LogAnalyzer

P = LogAnalyzer(SutConfig.Env.LOG_DIR)
baseline = os.path.join(os.path.dirname(__file__), r"..\Tools\SetupBase\2288服务器setup菜单基线版本_Byosoft_V0.1.xlsx")


# POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
def post_test():  # POST: POST Log(TBD) and Information Check
    tc = ('101', '[TC101]POST Information Test', 'POST Information Test')
    result = ReportGen.LogHeaderResult(tc)
    msg_list = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F6]
    capture_start = "STOP_DIMMINFO_SYSTEM_TABLE"
    capture_end = "Press F6 go to SP boot"
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, 60, 120)
        assert MiscLib.verify_msgs_in_log(msg_list, log_cut)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# PXE Test
@core.test_case(('102', '[TC102] PXE Hotkey Test', 'PXE HotKey Test'))
def pxe_test(n=1):
    for i in range(n):
        if not SetUpLib.boot_with_hotkey(Key.F12, 'F12 is pressed. Go to PXE boot', 180):
            core.capture_screen()
            return
    ReleaseTest.pxe_boot_uefi = True
    return core.Status.Pass


# USB Test
# Precondition: No USB key installed
# OnStart: NA
# OnComplete: USB Configuration Page
def usb_test():
    tc = ('103', '[TC103]USB Test', 'USB Test')
    result = ReportGen.LogHeaderResult(tc)
    msg_list = ['USB Mouse\s+1', 'USB Keyboard\s+1', f'USB Mass Storage\s+{SutConfig.SysCfg.USB_Storage}']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail(capture=True)
        return
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_USB_CFG, 10, 'USB'):
        result.log_fail(capture=True)
        return
    if not SetUpLib.verify_info(msg_list, 7):
        result.log_fail(capture=True)
        return
    core.capture_screen()
    result.log_pass()
    return True


# press F2
def press_f2():
    tc = ('104', '[TC104]Setup菜单用户输入界面按F2切换键盘制式', '支持热键配置')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOTKEY_PROMPT_DEL, 300)
        SetUpLib.send_key(Key.DEL)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, "Press F2", 60)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'fr-FR')
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'ja-JP')
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'en-US')
        logging.info("Send password...")
        SetUpLib.send_data(Msg.BIOS_PASSWORD)
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'Continue', 30)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Setup: Load default and setting saving - AT test cases below,
def load_default():
    tc = ('105', '[TC105] Load default and setting saving Test', 'BIOS Load default Test')
    result = ReportGen.LogHeaderResult(tc)
    pxe_boot = ["PXE Boot Capability", "<UEFI:IPv4>"]
    boot_fail_policy = ["Boot Fail Policy", "<Boot Retry>"]
    pxe_boot_2 = ["PXE Boot Capability", "<UEFI:IPv6>"]
    boot_fail_policy_2 = ["Boot Fail Policy", "<Cold Boot>"]
    default_options = [boot_fail_policy, pxe_boot]
    changed_options = [boot_fail_policy_2, pxe_boot_2]
    if not SetUpLib.boot_to_page(Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return

    # change option boot fail policy from "Boot Retry" to "Cold Boot"
    logging.info("***change option boot fail policy from Boot Retry to Cold Boot")
    if not SetUpLib.locate_option(Key.DOWN, boot_fail_policy, 15):
        result.log_fail(capture=True)
        return
    SetUpLib.send_key(Key.F5)

    # change pxe option from IPV4 to IPV6
    logging.info("***change pxe option from IPV4 to IPV6")
    if not SetUpLib.locate_option(Key.DOWN, pxe_boot, 15):
        result.log_fail(capture=True)
        return

    logging.info("***Save and reset.")
    SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)

    # Verify modified options
    if not SetUpLib.boot_to_page(Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return
    result.capture_screen()
    if not SetUpLib.verify_options(Key.DOWN, changed_options, 15):
        result.log_fail(capture=True)
        return
    logging.info("***Modified options are verified.")

    logging.info("***Reset defaul by hotkey")
    SetUpLib.send_keys([Key.F9, Key.Y, Key.F10, Key.Y], 2)

    # Verify whether options are reset to default
    logging.info("***Verify whether options are reset to default")
    if not SetUpLib.continue_to_page(Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return
    if not SetUpLib.verify_options(Key.DOWN, default_options, 15):
        result.log_fail(capture=True)
        return

    result.log_pass()
    return True


# Testcase_DRAM_RAPL_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup DRAM RAPL page
def dram_rapl_option_check():
    tc = ('106', '[TC106]Testcase_DRAM_RAPL_001, 菜单项DRAM RAPL选单检查', '支持DRAM RAPL设置')
    result = ReportGen.LogHeaderResult(tc)
    dram_rapl = [['DRAM RAPL', '<Enabled>']]
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_DRAM_RAPL, 20, Msg.DRAM_RAPL_CONFIG):
        result.log_fail()
        return

    if not SetUpLib.verify_options(Key.DOWN, dram_rapl, 4):
        result.log_fail()
        return
    logging.info("**DRAM rapl default value verified.")
    SetUpLib.send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, r'DisabledEnabled', 10):
        result.log_fail()
        return
    logging.info("**DRAM rapl supported values verified.")
    result.log_pass()
    return True


# Testcase_SecurityBoot_001
def security_boot():
    tc = ('107', '[TC107] Secure Boot默认值', 'Secure Boot默认值')
    result = ReportGen.LogHeaderResult(tc)
    keys_secure_boot = [Key.RIGHT, Key.DOWN, Key.ENTER]
    secureboot_disable = ['Current Secure Boot State\s+Disabled']
    if not SetUpLib.boot_to_setup():
        result.log_fail(capture=True)
        return
    logging.info("Enter secure boot configuration.")
    SetUpLib.send_keys(keys_secure_boot)
    logging.info("Checking secure boot status")
    if not SetUpLib.verify_info(secureboot_disable, 5):
        result.log_fail(capture=True)
        return
    logging.info("**Secure boot default status verified.")
    result.log_pass()
    return True


# PM: Warm reset n times, Cold reset n times and AC (TBD)
@core.test_case(('108', '[TC108] reboot 3次，DC 3次', ' 冷启动， 热启动正常'))
def PM():
    status = 3
    assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
    logging.info("Warm reset loops: {0}".format(status))
    for i in range(status):
        try:
            logging.info("Warm reset cycle: {0}".format(i + 1))
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)   # without delay
            logging.debug("Ctrl + Alt + Del key sent")
            if not SetUpLib.continue_to_page(Msg.PAGE_ADVANCED):
                logging.info("Warm reset Test:Fail")
                status = status-1
                continue
        except Exception as e:
            logging.error(e)
    # DC cycle 3 times
    logging.info("Cold reset loops: {0}".format(status))
    for j in range(status):
        try:
            logging.info("DC reset cycle: {0}".format(j + 1))
            BmcLib.force_power_cycle()
            if not SetUpLib.continue_to_page(Msg.PAGE_ADVANCED):
                logging.info("DC cycle Test:Fail")
                status = status-1
                continue
        except Exception as e:
            logging.error(e)
    if status == 1 and 2:
        return core.Status.Fail
    return core.Status.Pass