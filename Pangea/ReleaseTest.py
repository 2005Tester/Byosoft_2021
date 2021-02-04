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

from Report import ReportGen
from Pangea.SutConfig import Key, Msg
from Pangea.BaseLib import PangeaLib, SetUpLib, PowerLib


# POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
def post_test(serial, ssh):  # POST: POST Log(TBD) and Information Check
    tc = ('002', 'POST Information Test', 'POST Information Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not PowerLib.reboot_system(ssh):
        result.log_fail()
        return
    msg_list = [Msg.HOTKEY_PROMPT, Msg.HOTKEY_PROMPT_F2, Msg.HOTKEY_PROMPT_F7]
    if not serial.waitStrings(msg_list, timeout=300):
        result.log_fail()
        return
    result.log_pass()
    return True


# PM: Warm reset n times, Cold reset n times and AC (TBD)
def warm_reboot_cycling(serial, ssh, n=1):
    tc = ('003', 'Power Control Test', 'Power Control Test + F2')
    result = ReportGen.LogHeaderResult(tc, serial)
    status = 0
    if not PangeaLib.toBIOS(serial, ssh):
        result.log_fail()
        return
    logging.info("Warm reset loops: {0}".format(n))
    for i in range(n):
        try:
            logging.info("Warm reset cycle: {0}".format(i + 1))
            serial.send_keys(Key.CTRL_ALT_DELETE)
            logging.debug("Ctrl + Alt + Del key sent")
            if not PangeaLib.toBIOSnp(serial):
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
            if not PowerLib.power_cycle(ssh):
                return
            if not PangeaLib.toBIOSnp(serial):
                logging.info("DC Cycle Test:Fail")
                status = 2
                continue
        except Exception as e:
            logging.error(e)
    if status == 1 | 2:
        result.log_fail()
        return

    result.log_pass()
    return True


# PXE Test
def pxeTest(serial, ssh, n=1):
    tc = ('004', 'PXE Test', 'PXE Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    msg = 'NBP file downloaded successfully'
    for i in range(n):
        if not PangeaLib.toBIOS(serial, ssh):
            result.log_fail()
            return
        if not SetUpLib.locate_option(serial, Key.RIGHT, [Msg.Boot_OPTION], 7):
            result.log_fail()
            return
        if not SetUpLib.locate_option(serial, Key.DOWN, [Msg.Boot_MANAGER], 7):
            result.log_fail()
            return
        serial.send_keys(Key.ENTER)
        if not SetUpLib.enter_menu(serial, Key.DOWN, [Msg.PXE_PORT], 12, msg):
            result.log_fail()
            return
    result.log_pass()
    return True


# Processor/DIMM information check
def processor_dimm_basic_info(serial, ssh):
    tc = ('007', 'Processor/DIMM Test', 'CPU/DIMM Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not PangeaLib.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not SetUpLib.locate_option(serial, Key.RIGHT, [Msg.CPU_MENU], 7):
        result.log_fail()
        return
    if not SetUpLib.locate_option(serial, Key.DOWN, [Msg.CPU_CONFIG], 12):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not SetUpLib.locate_option(serial, Key.DOWN, [Msg.PROCESSOR_CONFIG], 12):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not SetUpLib.verify_info(serial, ['Microcode Revision\s+0D0001B2  \|  0D0001B2'], 12):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    if not SetUpLib.locate_option(serial, Key.DOWN, [Msg.MEMORY_CONFIG], 12):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not SetUpLib.locate_option(serial, Key.DOWN, [Msg.MEMORY_TOPOLOGY], 70):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not SetUpLib.verify_info(serial, ['Socket0.ChE.Dimm1\: 2933MT/s Samsung SRx4 16GB\s+RDIMM'], 12):
        result.log_fail()
        return

    result.log_pass()
    return True


# Setup: Load default and setting saving - AT test cases below,
def load_default_save_reset(serial, ssh):
    tc = ('011', 'Load default and setting saving Test', 'BIOS Load default Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    option_bfo = ['\[5\]\s+System Shell Timeout', '\<Disable\>\s+Boot Shell First']
    option_aft = ['\[15\]\s+System Shell Timeout', '\<Enable\>\s+Boot Shell First']
    if not PangeaLib.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not SetUpLib.enter_menu(serial, Key.RIGHT, [Msg.Boot_MENU], 12, Msg.Boot_OPTION):
        result.log_fail()
        return
    if not SetUpLib.verify_info(serial, option_bfo, 7):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ESC, Key.ENTER, Key.ENTER, Key.DOWN, Key.ENTER])
    time.sleep(0.1)
    serial.send_keys_with_delay([Key.DOWN, Key.ENTER])
    serial.send_data('15')
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.F10)
    time.sleep(0.1)
    serial.send_data(Key.Y)
    if not PangeaLib.toBIOSnp(serial):
        result.log_fail()
        return
    if not SetUpLib.enter_menu(serial, Key.RIGHT, [Msg.Boot_MENU], 12, Msg.Boot_OPTION):
        result.log_fail()
        return
    if not SetUpLib.verify_info(serial, option_aft, 7):
        result.log_fail()
        if not PangeaLib.reset_default(serial, ssh):
            return
    serial.send_keys(Key.F9)
    time.sleep(0.1)
    serial.send_data(Key.Y)
    time.sleep(20)
    serial.send_keys(Key.F10)
    time.sleep(0.1)
    serial.send_data(Key.Y)
    if not PangeaLib.toBIOSnp(serial):
        result.log_fail()
        if not PangeaLib.reset_default(serial, ssh):
            return
    time.sleep(1)
    if not SetUpLib.verify_info(serial, option_bfo, 7):
        result.log_fail()
        if not PangeaLib.reset_default(serial, ssh):
            return

    result.log_pass()
    return True


# OS Test
def boot_eulerOS(serial, ssh, n=1):
    tc = ('012', 'Boot to UEFI OS Test', 'OS Test')
    result = ReportGen.LogHeaderResult(tc, serial)
    msg = 'Storage login'
    for i in range(n):
        if not PangeaLib.toBIOS(serial, ssh):
            result.log_fail()
            return
        if not SetUpLib.locate_option(serial, Key.RIGHT, [Msg.Boot_OPTION], 7):
            result.log_fail()
            return
        if not SetUpLib.locate_option(serial, Key.DOWN, [Msg.Boot_MANAGER], 7):
            result.log_fail()
            return
        serial.send_keys(Key.ENTER)
        if not SetUpLib.enter_menu(serial, Key.DOWN, [Msg.OS_PORT], 12, msg):
            result.log_fail()
            return
    result.log_pass()
    return True

