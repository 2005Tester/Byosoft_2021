import logging
from Pangea.SutConfig import Key, Msg
from Pangea.BaseLib import SerialLib, PowerLib
from Pangea import SutConfig


# verify information like CPU, memory in one setup page
def verify_info(serial, setup_options, try_count):
    if serial.navigate_and_verify(Key.DOWN, setup_options, try_count):
        return True
    if not len(setup_options) == 0:
        if serial.navigate_and_verify(Key.UP, setup_options, try_count):
            return True


# Verify a few setup options and desired values in one setup page
# options: list of setupoption and value e.g.[["IRQ Threshold", "\[7\]"],[RRQ Threshold", "\[7\]]
def verify_options(serial, key, options, trycounts):
    verified_items = []
    for option in options:
        if serial.locate_setup_option(key, option, trycounts):
            verified_items.append(option)
        else:
            logging.info("Option: {0} not verified".format(option))
    if len(verified_items) == len(options):
        logging.info("All the setup options are verified")
        return True
    else:
        logging.info("{0} options not verified".format(len(options)-len(verified_items)))    


# Enter setup menu
def enter_menu(serial, key, option_path, try_counts, confirm_msg):
    return serial.enter_menu(key, option_path, try_counts, confirm_msg)


# locate a setup option by given option name and default value
def locate_option(serial, key, setupoption, try_counts):
    return serial.locate_setup_option(key, setupoption, try_counts)


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    logging.info("SetUpLib: Boot to setup main page")
    logging.info("SetUpLib: Rebooting SUT...")
    if not PowerLib.reboot_system(ssh):
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    if not serial.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


def boot_with_hotkey(serial, ssh, key, msg, timeout):
    hotkey_prompt = Msg.HOTKEY_PROMPT_DEL
    pw_prompt = Msg.PW_PROMPT
    password = SutConfig.BIOS_PASSWORD 
    if not PowerLib.reboot_system(ssh):
        return
    if not serial.boot_with_hotkey(key, msg, timeout, hotkey_prompt, pw_prompt, password):
        return
    logging.info("Boot with hotkey successfully.")
    return True


# Boot to boot manager without a force reset
def continue_to_bootmanager(serial):
    logging.info("SetUpLib: continue boot to bootmanager")
    msg = "Boot Manager Menu"
    if not serial.boot_with_hotkey(Key.F11, msg, 300):
        logging.info("SetUpLib: Continue boot to bootmanager failed.")
        return
    logging.info("SetUpLib: Boot to bootmanager successful")
    return True


# Boot to BIOS configuration
def boot_to_bios_config(serial, ssh):
    if not boot_to_setup(serial, ssh):
        return
    logging.info("Move to \"BIOS Configuration\"")
    SerialLib.send_keys_with_delay(SutConfig.key2Setup)
    if not serial.is_msg_present('System Time'):
        logging.info("SetUpLib: Boot to BIOS Configuration Failed")
        return
    logging.info("SetUpLib: Boot to BIOS Configuration successfully")
    return True


# boot to specific page in bios configuration
def boot_to_page(serial, ssh, page_name):
    if not boot_to_bios_config(serial, ssh):
        return
    logging.info("SetUpLib: Move to specified setup page")
    if not serial.locate_setup_option(Key.RIGHT, [page_name], 12):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


# Verify supported values of a setup option, can be called after locate_setup_option()
# valuses: string, e.g: DisabledAutoLowMediumHighManual
def verify_supported_values(serial, values):
    SerialLib.send_keys(Key.ENTER)
    if not serial.is_msg_present(values):
        logging.info("Supported values are not correct.")
        SerialLib.send_keys(Key.ESC)
        return
    logging.info("Supported values are verified.")
    SerialLib.send_keys(Key.ESC)  
    return True


# Boot to boot manager with hotkey
def boot_to_bootmanager(serial, ssh):
    key = Key.F11
    msg = "Boot Manager Menu"
    return boot_with_hotkey(serial, ssh, key, msg, 300)

