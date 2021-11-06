import logging
import time
from batf import SerialLib, MiscLib
from batf.SutInit import Sut

from Hygon.BaseLib import BmcLib
from Hygon.Config.PlatConfig import Key, Msg
from Hygon.Config import SutConfig


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
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, Msg.PAGE_MAIN_CN, 300, Msg.HOTKEY_PROMPT_DEL_CN):
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


def boot_with_hotkey(key, msg, timeout, hotkey_prompt):
    if not BmcLib.init_sut():
        return
    if not Sut.BIOS_COM.boot_with_hotkey(key, msg, timeout, hotkey_prompt):
        return
    logging.info("Boot with hotkey successfully.")
    return True


# boot to a specific page in bios configuration
def boot_to_page(page_name):
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
    if not SerialLib.is_msg_present(Sut.BIOS_COM, values, delay=7):
        logging.info("Supported values are not correct.")
        send_key(Key.ESC)
        return
    logging.info("Supported values are verified.")
    send_key(Key.ESC)
    return True


# Boot to kylin os from boot manager
def boot_kylin_from_bm():
    if not boot_with_hotkey(Key.F11, Msg.ENTER_SETUP_CN, 300, Msg.HOTKEY_PROMPT_F11_CN):
        return
    if not select_boot_option(Key.DOWN, Msg.Kylin_Os, 8, 'Kylin'):
        return
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 300):
        return
    logging.info("OS Boot Successful")
    return True


# get value of a setupoption
# option_patten: [name, patten of value] e.g. ["MMIO High Base", "<.+>"]
def get_option_value(option_patten, key, try_counts):
    value_patten = "H<(\w+)>\x1B"
    return Sut.BIOS_COM.get_option_value(option_patten, value_patten, key, try_counts)


# Boot to BIOS configuration reset default by F9
def reset_default():
    logging.info("Reset BIOS to dafault by F9")
    if not boot_to_setup():
        return
    send_keys(Key.RESET_DEFAULT)
    assert BmcLib.enable_console_direction(), 'console enabled -> fail'
    logging.info('Enable console direction successfully,')
    send_keys(Key.SAVE_RESET)
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 300):
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
def back_to_setup_toppage(msg='确认退出'):
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


# select a boot option in boot manager
# optionname: string, name of setup option
def select_boot_option(key, optionname, try_counts, confirm_msg):
    es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
    patten = es + optionname + es + r"\x1B\[44m"
    while try_counts:
        time.sleep(2)
        if SerialLib.is_msg_present(Sut.BIOS_COM, patten, 2, cleanup=False):
            logging.info("Boot option found: {0}".format(optionname))
            send_key(Key.ENTER)
            if not SerialLib.is_msg_present(Sut.BIOS_COM, confirm_msg):
                logging.info("Boot to option: {0} Failed".format(optionname))
                return
            logging.info("Boot to option: {0} successfully".format(optionname))
            return True
        send_key(key)
        try_counts -= 1
    logging.info("Boot option NOT found: {0}".format(optionname))


# select a value of setup option to change and save,
def select_option_value(key_optionname, optionname, key_value, value, try_counts):
    """
    key_optionname: send key to locate option that waiting to be changed
    optionname: ['name','value'] e.g. ["Boot Type", "<UEFI Boot Type>"]
    key_value: send key to find the value ready to be written
    value: the modified value of the option, e.g 'Enabled'
    trycounts: the counts to send keys
    """
    es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
    patten = es + value + es + r"\x1B\[44m"
    assert locate_option(key_optionname, optionname, try_counts), 'locate option -> fail'
    send_key(Key.ENTER)
    while try_counts:
        time.sleep(2)
        if SerialLib.is_msg_present(Sut.BIOS_COM, patten, 2, cleanup=False):
            logging.info("value found: {0}".format(value))
            send_key(Key.ENTER)
            return True
        send_key(key_value)
        try_counts -= 1
    logging.info("Value NOT found: {0}".format(value))
