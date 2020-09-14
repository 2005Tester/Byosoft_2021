# -*- encoding=utf8 -*-
import logging
from HY5 import Hy5TcLib
from HY5 import Hy5Config

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


def boot_to_bios_config(serial, ssh):
    keys = RIGHT*2 + DOWN + ENTER
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('System Time'):
        logging.info("Boot to BIOS Configuration Failed")
        return
    logging.info("Boot to BIOS Configuration Pass")
    return True


def check_me_state(serial, ssh):
    logging.info("[*TC Start] Check ME State")
    keys = RIGHT*2 + DOWN + ENTER + RIGHT + DOWN*5 + ENTER
    keys_state = DOWN*5
    if not boot_to_setup(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_present('firmware selected to run'):
        logging.info("Boot to ME Configuration Menu Failed")
        return
    logging.info("Boot to ME Configuration Pass")
    serial.send_keys(keys_state)
    if not serial.is_msg_present('Operational'):
        logging.info("[*TC Result] Check ME State in operational mode: Fail")
        return
    logging.info("[*TC Result] Check ME State in operational mode: Pass")
    return True


def enable_full_debug_msg(serial, ssh):
    logging.info("[*TC Start] Set full debug message.")
    keys_enable_full_debug = RIGHT + DOWN + ENTER + DOWN * 6 + F5 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys_enable_full_debug)
    if not serial.is_msg_present('InstallProtocolInterface.'):
        return
    logging.info("Boot in full debug message mode.")
    return True


def disable_full_debug_msg(serial, ssh):
    logging.info("[*TC Start] Set full debug message.")
    keys_enable_full_debug = RIGHT + DOWN + ENTER + DOWN * 6 + F6 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys_enable_full_debug)
    if not serial.is_msg_present('BIOS boot completed.'):
        logging.info("[*TC Start] Boot failed.")
        return
    return True
