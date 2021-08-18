import logging
import time
from Core import SerialLib
from Core.SutInit import Sut
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Key, Msg
from TCE.BaseLib import BmcLib


# Send a single key, e.g. ENTER, DOWN, UP
def send_key(key):
    SerialLib.send_key(Sut.BIOS_COM, key)


# send keys with default delay = 1s, e.g. [F10, Y]
def send_keys(keys, delay=1):
    SerialLib.send_keys_with_delay(Sut.BIOS_COM, keys, delay)


# send data to BIOS serial port
def send_data(data):
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(1)


# send a string and enter to BIOS serial port
def send_data_enter(data):
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(1)
    send_key(Key.ENTER)


# verify information like CPU, memory in one setup page, option name is highlighted
# infos: list e.g. ['BIOS Revision\s+5.[0-9]{2}']
def verify_info(info_list, trycounts):
    if Sut.BIOS_COM.navigate_and_verify(Key.DOWN, info_list, trycounts):
        return True
    if Sut.BIOS_COM.navigate_and_verify(Key.UP, info_list, trycounts):
        return True


# Verify a few setup options and desired values, option value is highlighted
# options: list of setupoption and value e.g.[["IRQ Threshold", "\[7\]"],[RRQ Threshold", "\[7\]]
def verify_options(key, options, trycounts):
    verified_items = []
    for option in options:
        if Sut.BIOS_COM.locate_setup_option(key, option, trycounts):
            verified_items.append(option)
        else:
            logging.info("Option: {0} not verified".format(option))
    if len(verified_items) == len(options):
        logging.info("All the setup options are verified")
        return True
    else:
        logging.info("{0} options not verified".format(len(options) - len(verified_items)))

    # Enter setup menu


def enter_menu(key, option_path, try_counts, confirm_msg):
    try:
        return Sut.BIOS_COM.enter_menu(key, option_path, try_counts, confirm_msg)
    except Exception as e:
        logging.error("Exception occur: {0}".format(e))


# locate a setup option by given option name and default value
# setupoption = ['name','value'] e.g. ["Boot Type", "<UEFI Boot Type>"]
# Patten1: Only option name is highlighted, name should be specified, value not required
# Patten2: Only value is highlighted, both name and value need to be specified, e.g.["Boot Type", "<UEFI Boot Type>"]
def locate_option(key, setupoption, try_counts):
    return Sut.BIOS_COM.locate_setup_option(key, setupoption, try_counts)


# Boot to setup home page (6 icons) after a force reset
def boot_to_setup():
    logging.info("SetUpLib: Boot to setup main page")
    logging.info("SetUpLib: Rebooting SUT...")
    if not BmcLib.force_reset():
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


# Continue boot to setup home page (6 icons) without a force reset
def continue_to_setup():
    logging.info("SetUpLib: Continue boot to setup main page")
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


def boot_with_hotkey(key, msg, timeout):
    hotkey_prompt = Msg.HOTKEY_PROMPT_DEL
    pw_prompt = Msg.PW_PROMPT
    password = SutConfig.Env.BIOS_PASSWORD
    if not BmcLib.force_reset():
        return
    if not Sut.BIOS_COM.boot_with_hotkey(key, msg, timeout, hotkey_prompt, pw_prompt, password):
        return
    logging.info("Boot with hotkey successfully.")
    return True


def continue_boot_with_hotkey(key, msg, timeout):
    hotkey_prompt = Msg.HOTKEY_PROMPT_DEL
    pw_prompt = Msg.PW_PROMPT
    password = SutConfig.Env.BIOS_PASSWORD
    if not Sut.BIOS_COM.boot_with_hotkey(key, msg, timeout, hotkey_prompt, pw_prompt, password):
        return
    logging.info("Boot with hotkey successfully.")
    return True


# Continue Boot to boot manager without a force reset
def continue_to_bootmanager():
    logging.info("SetUpLib: continue boot to bootmanager")
    msg = "Boot Manager Menu"
    if not Sut.BIOS_COM.boot_with_hotkey(Key.F11, msg, 300):
        logging.info("SetUpLib: Continue boot to bootmanager failed.")
        return
    logging.info("SetUpLib: Boot to bootmanager successful")
    return True


# Continue boot to password prompt by pressing hotkey without a force reset
def continue_to_pw_prompt(key):
    logging.info("SetUpLib: continue boot to password prompt by pressing: {0}".format(key))
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOTKEY_PROMPT_DEL):
        return
    send_key(key)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.PW_PROMPT):
        return
    return True


# boot to password prompt by a hotkey
def boot_to_pw_prompt(key):
    logging.info("SetUpLib: Boot to password prompt by pressing: {0}".format(key))
    if not BmcLib.force_reset():
        return
    return continue_to_pw_prompt(key)


# Move from Setup main to BIOS Configuration inforamtion page
# OnStart: Setup main page, cursor on Continue icon
def move_to_bios_config():
    logging.info("Move to \"BIOS Configuration\"")
    send_key(Key.DOWN)
    if SerialLib.is_msg_present(Sut.BIOS_COM, "Boot From File", delay=10):
        logging.info("UEFI boot mode detected.")
        send_keys([Key.RIGHT, Key.RIGHT])
    else:
        logging.info("Legacy boot mode detected")
        send_key(Key.RIGHT)
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, 'System Time'):
        logging.info("SetUpLib: Boot to BIOS Configuration Failed")
        return
    logging.info("SetUpLib: Boot to BIOS Configuration successfully")
    return True


# Boot to BIOS configuration information page
def boot_to_bios_config():
    if not boot_to_setup():
        return
    if not move_to_bios_config():
        return
    return True


# Continue Boot to BIOS configuration information page without a force reset
def continue_to_bios_config():
    if not continue_to_setup():
        return
    if not move_to_bios_config():
        return
    return True


# move to a specific page in bios configuration from setup main
# OnStart: Setup main page, cursor on Continue icon
def move_to_page(page_name):
    if not move_to_bios_config():
        return
    logging.info("SetUpLib: Move to specified setup page")
    if not Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [page_name], 12):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


# boot to a specific page in bios configuration
def boot_to_page(page_name):
    if not boot_to_bios_config():
        return
    logging.info("SetUpLib: Move to specified setup page")
    if not Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [page_name], 12):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


# Continue boot to specific page in bios configuration without a force reset, assume reset is done in previous step
def continue_to_page(page_name):
    if not continue_to_bios_config():
        return
    logging.info("SetUpLib: Move to specified setup page")
    if not Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [page_name], 12):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


# Verify supported values of a setup option, can be called after locate_setup_option()
# valuses: string, e.g: DisabledAutoLowMediumHighManual
def verify_supported_values(values):
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, values):
        logging.info("Supported values are not correct.")
        send_key(Key.ESC)
        return
    logging.info("Supported values are verified.")
    send_key(Key.ESC)
    return True


# Boot to boot manager with hotkey
def boot_to_bootmanager():
    key = Key.F11
    msg = "Boot Manager Menu"
    return boot_with_hotkey(key, msg, 300)


# Boot OS from boot manager
def boot_suse_from_bm(os=Msg.BOOT_OPTION_SUSE, msg=Msg.SUSE_GRUB):
    if not boot_to_bootmanager():
        return
    if not enter_menu(Key.DOWN, os, 8, msg):
        return
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
        return
    logging.info("OS Boot Successful")
    return True


# Boot OS from boot manager without any power action, e.g, used wth F10 + Y in Setup
def continue_to_boot_suse_from_bm(os=Msg.BOOT_OPTION_SUSE, msg=Msg.SUSE_GRUB):
    if not continue_to_bootmanager():
        return
    if not enter_menu(Key.DOWN, os, 8, msg):
        return
    # if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
    #     return
    logging.info("OS Boot Successful")
    return True


# Move a specific boot option up
def move_boot_option_up(boot_option, count):
    hdd_group = [Msg.MENU_BOOT_ORDER, Msg.MENU_HDD_BOOT]
    logging.info("Move: {0} {1} times".format(boot_option, count))
    if not boot_to_page(Msg.PAGE_BOOT):
        return
    if not enter_menu(Key.UP, hdd_group, 25, boot_option[0]):
        return
    if not locate_option(Key.UP, boot_option, 10):
        return
    logging.info("Move option up")
    for n in range(count):
        send_key(Key.F6)
    logging.info("Save and reboot.")
    send_keys([Key.F10, Key.Y])
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, delay=600):
        return
    return True


# Update default password, should be called after update bios
def update_default_password():
    logging.info("Change BIOS password to non-default.")
    if not BmcLib.force_reset():
        return
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOTKEY_PROMPT_DEL):
        return
    send_key(Key.DEL)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, '8-16'):
        return
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, "Enter New Password"):
        return
    send_data(SutConfig.Env.BIOS_PASSWORD)
    send_key(Key.ENTER)
    send_data(SutConfig.Env.BIOS_PASSWORD)
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, "Change password success"):
        return
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOME_PAGE):
        return
    logging.info("Password changed to non-default successfully")
    return True


# get value of a setupoption
# option_patten: [name, patten of value] e.g. ["MMIO High Base", "<.+>"]
def get_option_value(option_patten, key, try_counts):
    value_patten = "H<([\w ]+)>\x1B"  # some value contains white space
    return Sut.BIOS_COM.get_option_value(option_patten, value_patten, key, try_counts)


# Boot to BIOS configuration reset default by F9
def reset_default():
    logging.info("Reset BIOS to dafault by F9")
    if not boot_to_bios_config():
        return
    send_keys(Key.RESET_DEFAULT)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
        logging.info("Reset dafault by F9:Fail")
        return
    logging.info("Reset dafault by F9:Pass")
    return True


# Match a specific patten from serial port, return true if match found, otherwise return None
def wait_message(msg, timeout=150):
    return SerialLib.is_msg_present(Sut.BIOS_COM, msg, timeout)


# Match a list of strings from serial port
def wait_strings(msg_list, timeout=10):
    return SerialLib.is_msg_list_present(Sut.BIOS_COM, msg_list, timeout)


# used to navigate to setup top page,
def back_to_setup_toppage(msg='Exit now'):
    try:
        while True:
            logging.info('Navigating to top page,')
            send_key(Key.ESC)
            if wait_message(msg, timeout=6):
                send_key(Key.DISCARD_CHANGES)
                break
            time.sleep(1)
        logging.info("Current is top page,")
        return True
    except Exception as err:
        logging.debug(err)


# back to front page from "BIOS Configuration", highlight: stay at the highlight button
def back_to_front_page(highlight="Continue"):
    if not back_to_setup_toppage():
        return
    send_keys([Key.ESC, Key.Y])
    if locate_option(Key.RIGHT, [highlight], 3):
        logging.info(f"locaet to {highlight} success")
        return True
    send_key(Key.DOWN)
    if locate_option(Key.RIGHT, [highlight], 3):
        logging.info(f"locaet to {highlight} success")
        return True


# auto locate to the option and change the value to target, need enter the menu page first
def set_option_value(option, value, key=Key.DOWN, loc_cnt=15, save=False):
    logging.info(f'Set {option} -> {value}')
    if not locate_option(key, [option, f"<.+>"], loc_cnt):
        return
    if Sut.BIOS_COM.locate_value(value):
        send_keys(Key.ENTER)
        if save:
            logging.info(f'Save configuration and reset')
            send_keys(Key.SAVE_RESET)
        logging.info(f'Set {option} to {value} pass')
        return True


# lcoate to the target option and get all support values
def get_all_values(option, key=Key.DOWN, loc_cnt=15):
    if not locate_option(key, [option, f"<.+>"], loc_cnt):
        return
    values = Sut.BIOS_COM.get_value_list()
    if values:
        return values


# save configurations without reset
def save_without_reset(option=Msg.SAVE_WO_RESET):
    if not back_to_setup_toppage():
        return
    if not locate_option(Key.RIGHT, [Msg.PAGE_SAVE], 6):
        return
    if locate_option(Key.DOWN, [option], 6):
        send_key(Key.ENTER)
        send_keys([Key.ENTER], delay=10)
        return True
