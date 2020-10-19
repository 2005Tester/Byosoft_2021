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
        logging.info("Booting to boot manager failed.")
        return
    return True

# Boot to UEFI Shell
def boot_uefi_shell(serial, ssh):
    logging.info("<TC002><Tittle>Boot to UEFI Shell:Start")
    logging.info("<TC002><Description>Boot to UEFI Shell")
    if not boot_manager(serial, ssh):
        logging.info("<TC002><Result>Boot to UEFI Shell:Fail")
        return
    keys = UP + ENTER
    serial.send_keys(keys)
    print("Boot to UEFI shell")
    if not serial.is_msg_present('UEFI Interactive Shell'):
        logging.info("<TC002><Result>Boot to UEFI Shell:Fail")
        return
    logging.info("<TC002><Result>Boot to UEFI Shell:Pass")
    return True


# check whether ME is working in operational state
def check_bios_version(serial, ssh):
    logging.info("<TC003><Tittle>Check BIOS Version:Start")
    logging.info("<TC003><Description>Verify Whether BIOS versio is correct in setup main page")
    keys = DOWN
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('2.0.ID.AL.E.004.01'):
        logging.info("<TC003><Result>Check BIOS Version:Fail")
        return
    logging.info("<TC003><Result>Check BIOS Version:Pass")
    return True