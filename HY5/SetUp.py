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


# Boot to setup home page
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


# Boot to BIOS configuration page
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
    if not serial.is_msg_not_present('^InstallProtocolInterface.','BIOS boot completed.'):
        logging.info("<TC007><Result>Disable full debug message:Fail")
        return
    logging.info("<TC007><Result>Disable full debug message:Pass")
    return True

# Enable legacy boot
def enable_legacy_boot(serial, ssh):
    logging.info("<TC008><Tittle>Enable Legacy Boot:Start")
    logging.info("<TC008><Description>Enable Legacy Boot")
    keys = RIGHT*4 + F5 + F10 + Y
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
    keys = RIGHT*4 + F6 + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    serial.send_keys(keys)
    if not serial.is_msg_not_present('Start of legacy boot','BIOS boot completed.'):
        logging.info("<TC009><Result>Disable Legacy boot:Fail")
        return
    logging.info("<TC009><Result>Disable Legacy boot:Pass")
    return True


# Chnage CPU Cores to specific number, n is times of change value hotkey pressed, not core number
def change_cpu_cores(serial, ssh, n, num):
    logging.info("<TC010><Tittle>Change CPU Cores:Start")
    logging.info("<TC010><Description>Change CPU Core counts in setup and verify in OS")
    keys_cpu_core = RIGHT*1 + DOWN*8 + ENTER*2 + F6*n + F10 + Y
    if not boot_to_bios_config(serial, ssh):
        return
    logging.info("Changing cpu core counts")
    serial.send_keys(keys_cpu_core)
    logging.info("Booting to boot manager")
    serial.hotkey_f11()  # boot to boot manager
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
