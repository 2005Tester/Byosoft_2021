import logging
import time
from Core import SerialLib
from Core.SutInit import Sut

from Hygon.BaseLib import BmcLib
from Hygon.Config.PlatConfig import Key, Msg


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
    if not BmcLib.init_sut():
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, Msg.PAGE_MAIN, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


# Continue boot to setup home page without a force reset
def continue_to_setup():
    logging.info("SetUpLib: Continue boot to setup main page")
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, Msg.PAGE_MAIN, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


def boot_with_hotkey(key, msg, timeout):
    if not BmcLib.init_sut():
        return
    if not Sut.BIOS_COM.boot_with_hotkey(key, msg, timeout, Msg.HOTKEY_PROMPT_DEL):
        return
    logging.info("Boot with hotkey successfully.")
    return True


# Continue Boot to boot manager without a force reset
def continue_to_bootmanager():
    logging.info("SetUpLib: continue boot to bootmanager")
    if not Sut.BIOS_COM.boot_with_hotkey(Key.F11, Msg.HOTKEY_PROMPT_F11, 300):
        logging.info("SetUpLib: Continue boot to bootmanager failed.")
        return
    logging.info("SetUpLib: Boot to bootmanager successful")
    return True


# boot to a specific page in bios configuration
def boot_to_page(page_name):
    if not boot_to_setup():
        return
    logging.info("SetUpLib: Move to specified setup page")
    if not Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [page_name], 12):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


# Continue boot to specific page in bios configuration without a force reset, assume reset is done in previous step
def continue_to_page(page_name):
    if not continue_to_setup():
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


# Switch to legacy mode
def enable_legacy_boot():
    logging.info("Switch to legacy boot mode")
    if not boot_to_page(Msg.PAGE_BOOT):
        return
    if not locate_option(Key.DOWN, ["Boot Type", "<UEFIBoot>"], 25):
        return
    logging.info("Change boot type to legacy mode")
    send_key(Key.F5)
    if not locate_option(Key.DOWN, ["Boot Type", "<LegacyBoot>"], 25):
        logging.info("Failed to change boot type.")
        return
    logging.info("Save and reboot")
    send_keys([Key.F10, Key.Y], 5)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, 'Start of legacy boot'):
        logging.info("Not in legacy mode")
        return
    logging.info("Boot in legacy mode")
    return True


# Switch to uefi boot mode
def disable_legacy_boot():
    logging.info("Switch to uefi boot mode")
    if not boot_to_page(Msg.PAGE_BOOT):
        return
    if not locate_option(Key.DOWN, ["Boot Type", "<LegacyBoot>"], 25):
        return
    logging.info("Change boot type to UEFI mode")
    send_key(Key.F6)
    if not locate_option(Key.DOWN, ["Boot Type", "<UEFIBoot>"], 25):
        logging.info("Failed to change boot type.")
        return
    logging.info("Save and reboot")
    send_keys([Key.F10, Key.Y], 5)
    if not SerialLib.is_msg_not_present(Sut.BIOS_COM, 'Start of legacy boot', 'BIOS boot completed.'):
        logging.info("Not in UEFI mode")
        return
    logging.info("Boot in UEFI mode")
    return True


# Boot Suse from boot manager
def boot_kylin_from_bm():
    if not boot_to_bootmanager():
        return
    if not enter_menu(Key.DOWN, Msg.Kylin_Os, 8, Msg.ENTER_SETUP):
        return
    if not BmcLib.ping_sut():
        return
    logging.info("OS Boot Successful")
    return True


# Update default password, should be called after update bios
def change_default_language():
    logging.info("Change BIOS password to non-default.")
    if not BmcLib.set_language_to_eng():
        return
    if not BmcLib.init_sut():
        return
    logging.info("Language changed to english successfully")
    return True


# get value of a setupoption
# option_patten: [name, patten of value] e.g. ["MMIO High Base", "<.+>"]
def get_option_value(option_patten, key, try_counts):
    value_patten = "H<(\w+)>\x1B"
    return Sut.BIOS_COM.get_option_value(option_patten, value_patten, key, try_counts)


# set value of a setup option
# Usage Example: option="Performance Profile", from_value="Custom", to_value="Performance", set_key=Key.F5, set_cnt=3
def set_option_value(option, from_value, to_value, set_key, set_cnt, loc_cnt=15):
    logging.info(f'Set [{option}]: {from_value} => {to_value} Start')
    from_option = [option, f"<{from_value}>"]
    to_option = [option, f"<{to_value}>"]
    key_pressd = [set_key] * set_cnt
    if not locate_option(Key.DOWN, from_option, loc_cnt):
        logging.info('local_option -> fail')
        return
    logging.info(f'Try to set [{option}] from <{from_value}> to <{to_value}>...')
    send_keys(key_pressd)
    logging.info('Value set done, start to check if set successfully...')
    if key_pressd:  # avoid mis-locate if set_cnt=0 since verify_options find str first,then send key
        send_keys(Key.UP)
    if not verify_options(Key.DOWN, [to_option], loc_cnt):
        logging.info('Set option value -> fail')
        return
    logging.info(f'Set [{option}]: {from_value} => {to_value} successfully')
    return True


# Boot to BIOS configuration reset default by F9
def reset_default():
    logging.info("Reset BIOS to dafault by F9")
    if not boot_to_setup():
        return
    send_keys(Key.RESET_DEFAULT)
    if not BmcLib.ping_sut():
        logging.info("Reset dafault by F9:Fail")
        return
    logging.info("Reset dafault by F9:Pass")
    return True


# Match a specific patten from serial port, return true if match found, otherwise return None
def wait_message(msg, timeout=150):
    return SerialLib.is_msg_present(Sut.BIOS_COM, msg, timeout)


# Match a list of strings from serial port
def wait_strings(msg_list, delay=10):
    return SerialLib.is_msg_list_present(Sut.BIOS_COM, msg_list, delay)


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
