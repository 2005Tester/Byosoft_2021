#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

import logging
from batf.SutInit import Sut
from batf.Report import ReportGen
from Moc25 import Moc25TcLib
from Moc25.Config.SutConfig import Key
from Moc25.Config.SutConfig import Msg
from Moc25 import SetUp


def boot_AliOS():
    serial = Sut.BIOS_COM
    tc = ('001', 'Boot to AliOS', 'Boot to AliOS')
    result = ReportGen.LogHeaderResult(tc)

    if not Moc25TcLib.force_reset(serial):
        logging.info("Rebooting SUT Failed.")
        return
    if not serial.is_msg_present_general(Msg.OS_MSG, 180):
        result.log_fail()
        return
    if not Moc25TcLib.login_os(serial):
        result.log_fail()
        return
    result.log_pass()
    return True

# Boot to UEFI Shell
def boot_uefi_shell():
    serial = Sut.BIOS_COM
    tc = ('002', 'Boot to UEFI Shell', 'Boot to UEFI Shell')
    result = ReportGen.LogHeaderResult(tc)

    if not SetUp.boot_manager(serial):
        result.log_fail()
        return
    for i in range(0, 16):
        if serial.is_msg_present_general(r'UEFI Internal Shell\x1B\[0m', 2, cleanup=False):
            serial.send_keys(Key.ENTER)
            break
        else:
            serial.send_keys(Key.DOWN)
    if not serial.is_msg_present_general('UEFI Interactive Shell', 3):
        result.log_fail()
        return
    result.log_pass()
    return True


# Boot to AliOS from Boot manager
def boot_AliOS_from_BM(serial):
    tc = ('003', 'Boot to AliOS', 'Boot to AliOS from Bootmanager')
    result = Misc.LogHeaderResult(tc, serial)

    if not SetUp.attempt_boot_option(serial, "Alibaba Cloud Linux"):
        result.log_fail()
        return
    if not serial.is_msg_present_general(Msg.OS_MSG, 180):
        result.log_fail()
        return
    if not Moc25TcLib.login_os(serial):
        result.log_fail()
        return
    result.log_pass()
    return True

# Boot to PXE by hotkey
def pxe_boot(serial):
    tc = ('004', 'PXE Boot by F12', 'PXE Boot by pressing hotkey F12')
    result = Misc.LogHeaderResult(tc, serial)

    msg = "Boot from native PXE LAN"
    if not SetUp.boot_with_hotkey(serial, Key.F12, msg):
        result.log_fail()
        return
    result.log_pass()
    return True


# Boot mode test
def boot_mode_test(serial):
    tc = ('005', '启动模式设置测试', '启动模式设置测试')
    result = Misc.LogHeaderResult(tc, serial)
    logging.info("Verify Boot options in boot manager")
    boot_options = ["Alibaba Cloud Linux", "UEFI PXEv4"]
    if not SetUp.boot_manager(serial):
        result.log_fail()
        return
    if not SetUp.verify_setup_options(serial, boot_options, 10):
        result.log_fail()
        return
    logging.info("Boot options in boot manager verified")

    logging.info("Verify boot options in boot configuration menu")
    if not SetUp.boot_to_setup_bm(serial):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not SetUp.verify_setup_options(serial, boot_options, 10):
        result.log_fail()
        return
    logging.info("Boot options in boot configuration menu verified")
    result.log_pass()
    return True


# HDD boot order test
def hdd_boot_order(serial):
    tc = ('006', '硬盘启动顺序测试', '任何情况下, 启动项目符合HDD->PXE的启动顺序要求')
    result = Misc.LogHeaderResult(tc, serial)
    if not SetUp.locate_boot_bootorder(serial):
        result.log_fail()
        return
   
    boot_order = "{0}\s+UEFI\s+PXEv4".format(Msg.HDD_BOOT_OPTION)
    serial.send_keys(Key.ENTER)
    if not serial.is_msg_present_general(boot_order):
        result.log_fail()
        return
    logging.info("HDD boot order verified")
    result.log_pass()
    return True

# warm reboot cycling    
def warm_reboot_cycling(serial, cycles):
    tc = ('007', 'Warm reboot cycling', 'Warm reboot cycling test: {0} cycles'.format(cycles))
    result = Misc.LogHeaderResult(tc, serial)
    failures = 0
    test_cycle = 1
    while cycles:
        logging.info("Warm reboot cycle: {0}".format(test_cycle))
        if Moc25TcLib.warm_reset(serial):
            if not Moc25TcLib.continue_boot_and_login_os(serial):
                failures +=1
        else:
            failures +=1
            logging.info("Warmreset Fail")
        test_cycle +=1
        cycles -=1
    if not failures == 0:
        logging.info("{0} test cycles of warm reset failed".format(failures))
        result.log_fail()
        return
    logging.info("{0} test cycles of warm reset completed".format(test_cycle-1))
    result.log_pass()
    return True
        
# DC Cycling by IPMI command from ssh
def dc_cycling(serial, ssh, cycles):
    tc = ('008', 'DC cycling', 'DC cycling test: {0} cycles'.format(cycles))
    result = Misc.LogHeaderResult(tc, serial)
    failures = 0
    test_cycle =1
    while cycles:
        logging.info("DC cycle: {0}".format(test_cycle))
        if Moc25TcLib.force_power_cycle_ipmi(ssh):
            if not Moc25TcLib.continue_boot_and_login_os(serial):
                failures +=1
        else:
            failures +=1
            logging.info("IPMI Power cycle command fail")
        test_cycle +=1
        cycles -=1
        logging.info("Failures: {}".format(failures))
        logging.info("*"*80)
    if not failures == 0:
        logging.info("{0} test cycles of DC cycling failed".format(failures))
        result.log_fail()
        return
    logging.info("{0} test cycles of DC cycling completed".format(test_cycle-1))
    result.log_pass()
    return True


# power cycle stress using ipmi command from serial port
def ipmi_powercycle_stress(serial_bios, serial_bmc, cycles):
    tc = ('009', 'Cycling Stress', 'ipmi power cycle test: {0} cycles'.format(cycles))
    result = Misc.LogHeaderResult(tc, serial_bios)
    failures = 0
    test_cycle =1
    while cycles:
        logging.info("DC cycle: {0}".format(test_cycle))
        if Moc25TcLib.power_cycle_ipmi_serial(serial_bmc):
            if not Moc25TcLib.continue_boot_and_login_os(serial_bios):
                failures +=1
                """
                logging.info("Failure found, retry with power on command.")
                serial_bmc.send_data("ipmitool chassis power on\n")
                if not Moc25TcLib.continue_boot_and_login_os(serial_bios):
                    logging.info("Still fail after sending power on command.")
                """               
        else:
            failures +=1
            logging.info("IPMI Power cycle command fail")
        test_cycle +=1
        cycles -=1
        logging.info("Failures: {}".format(failures))
        logging.info("*"*80)
    if not failures == 0:
        logging.info("{0} test cycles of DC cycling failed".format(failures))
        result.log_fail()
        return
    logging.info("{0} test cycles of DC cycling completed".format(test_cycle-1))
    result.log_pass()
    return True