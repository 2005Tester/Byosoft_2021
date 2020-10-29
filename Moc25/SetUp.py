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
from Moc25 import Moc25TcLib
from Moc25 import Moc25Config

# Key mapping
ENTER = [chr(0x0D)]
F2 = [chr(0x1b), chr(0x4f), chr(0x51)]
F11 = [chr(0x1b), chr(0x4f), chr(0x5a)]
F12 = [chr(0x1b), chr(0x4f), chr(0x5b)]
UP = [chr(0x1b), chr(0x5b), chr(0x41)]
DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
Y = [chr(0x59)]

# send multiple keys in a row with delay
def send_keys_with_delay(serial, keys, delay):
    for key in keys:
        serial.send_keys(key)
        time.sleep(delay)

# Boot with hotkey
def boot_with_hotkey(serial, ssh, key, msg):
    logging.info("Moc25 Common Test Lib: boot with hotkey")
    logging.info("Rebooting SUT...")
    if not Moc25TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    flag = "Press <F2> to SETUP or <F11> to Boot Menu or <F12> to PXE Boot"
    logging.info("Waiting for {0}".format(flag))
    if not serial.boot_with_hotkey_general(key, flag, msg, 300):
        logging.info("Boot to setup failed.")
        return
    return True


# Boot to boot manaer by hotkey
def boot_manager(serial, ssh):
    logging.info("Moc25 Common Test Lib: boot to boot manager")
    msg = "Please select boot device"
    if not boot_with_hotkey(serial, ssh, F11, msg):
        logging.info("Booting to boot manager failed.")
        return
    return True


# Boot to Setup by hotkey
def boot_to_setup(serial, ssh):
    logging.info("Moc25 Common Test Lib: boot to Setup by F2")
    msg = "Byosoft ByoCore"
    if not boot_with_hotkey(serial, ssh, F2, msg):
        logging.info("Booting to BIOS Setup failed.")
        return
    return True

# Boot to PXE by hotkey
def pxe_boot(serial, ssh):
    logging.info("<TC006><Tittle>PXE Boot by F12:Start")
    logging.info("<TC006><Description>PXE Boot by pressing hotkey F12")
    msg = "Boot from native PXE LAN"
    if not boot_with_hotkey(serial, ssh, F12, msg):
        logging.info("<TC006><Result>PXE Boot by F12:Fail")
        return
    logging.info("<TC006><Result>PXE Boot by F12:Pass")
    return True

# boot to setup menu , socket configuration
def boot_to_skt_config(serial, ssh):
    logging.info("Moc25 Common Test Lib: boot to socket configuration")
    if not boot_to_setup(serial, ssh):
        return
    keys = [RIGHT, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, ENTER]
    send_keys_with_delay(serial, keys, 1)
    if not serial.is_msg_present('Processor Configuration'):
        logging.info("Moc25 Common Test Lib: boot to socket configuration Fail")
        return
    logging.info("Moc25 Common Test Lib: boot to socket configuration Pass")
    return True

# Boot to UEFI Shell
def boot_uefi_shell(serial, ssh):
    logging.info("<TC002><Tittle>Boot to UEFI Shell:Start")
    logging.info("<TC002><Description>Boot to UEFI Shell")
    if not boot_manager(serial, ssh):
        logging.info("<TC002><Result>Boot to UEFI Shell:Fail")
        return
    for i in range(0, 30):
        if not serial.is_msg_present_general('UEFI Internal Shell',2):
            serial.send_keys(DOWN)
        else:
            serial.send_keys(ENTER)
            if serial.is_msg_present_general('UEFI Interactive Shell',30):
                logging.info("<TC002><Result>Boot to UEFI Shell:Pass")
                return True
    logging.info("UEFI Interl Shell not found in bootmanager")
    logging.info("<TC002><Result>Boot to UEFI Shell:Fail")
    return


# check BIOS version
def check_bios_version(serial, ssh):
    logging.info("<TC003><Tittle>Check BIOS Version:Start")
    logging.info("<TC003><Description>Verify Whether BIOS versio is correct in setup main page")
    keys = DOWN
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present_general(Moc25Config.BIOS_VERSION, 120):
        logging.info("<TC003><Result>Check BIOS Version:Fail")
        return
    logging.info("<TC003><Result>Check BIOS Version:Pass")
    return True


# check ME status
def check_me_status(serial, ssh):
    logging.info("<TC004><Tittle>Check ME Status:Start")
    logging.info("<TC004><Description>Verify Whether ME is working in operational mode")
    if not boot_to_setup(serial, ssh):
        return
    keys = [RIGHT, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, ENTER, DOWN, DOWN, DOWN, DOWN, ENTER]
    for key in keys:
        serial.send_keys(key)
        time.sleep(1)
    if not serial.is_msg_present('General ME Configuration'):
        logging.info("<TC004><Result>Check ME Status:Fail")
        return
    keys = [DOWN, DOWN, DOWN, DOWN, DOWN]
    for key in keys:
        serial.send_keys(key)
        time.sleep(1)
    if not serial.is_msg_present('Operational'):
        logging.info("<TC004><Result>Check ME Status:Fail")
        return
    logging.info("<TC004><Result>Check ME Status:Pass")
    return True

# check CPU configuration
def check_cpu_info(serial, ssh):
    logging.info("<TC005><Tittle>Check CPU Information:Start")
    logging.info("<TC005><Description>Verify whether CPU information is correct.")
    if not boot_to_skt_config(serial, ssh):
        return
    serial.send_keys(ENTER)
    if not serial.is_msg_present('Per-Socket Configuration'):
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    send_keys_with_delay(serial, [DOWN, DOWN, DOWN], 1)
    if not serial.is_msg_present('000606C0'):
        logging.info("Processor ID incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    serial.send_keys(DOWN)
    if not serial.is_msg_present('1.600GHz'):
        logging.info("Processor frequency incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    serial.send_keys(DOWN)
    if not serial.is_msg_present('10H'):
        logging.info("Processor Max Ratio incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    serial.send_keys(DOWN)
    if not serial.is_msg_present('08H'):
        logging.info("Processor Min Ratio incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    serial.send_keys(DOWN)
    if not serial.is_msg_present('FD000041'):
        logging.info("Processor Microcode Revision incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    serial.send_keys(DOWN)
    if not serial.is_msg_present('80KB'):
        logging.info("Processor L1 Cache Info incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return
    serial.send_keys(DOWN)
    if not serial.is_msg_present('1280KB'):
        logging.info("Processor L2 Cache Info incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return 
    serial.send_keys(DOWN)
    if not serial.is_msg_present('7680KB'):
        logging.info("Processor L3 Cache Info incorrect")
        logging.info("<TC005><Result>Check CPU Information:Fail")
        return 
    logging.info("<TC005><Result>Check CPU Information:Pass")
    return True
