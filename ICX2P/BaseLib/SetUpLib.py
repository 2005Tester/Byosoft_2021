import logging
from Core import SerialLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import PowerLib


# Send a single key, e.g. ENTER, DOWN, UP
def send_key(serial, key):
    serial.send_keys(key)


# send keys with default delay = 1s, e.g. [F10, Y]
def send_keys(serial, keys, delay=1):
    serial.send_keys_with_delay(keys, delay=1)


# verify information like CPU, memory in one setup page, option name is highlighted
# infos: list e.g. ['BIOS Revision\s+5.[0-9]{2}']
def verify_info(serial, info_list, trycounts):
    if serial.navigate_and_verify(Key.DOWN, info_list, trycounts):
        return True
    if serial.navigate_and_verify(Key.UP, info_list, trycounts):
        return True


# Verify a few setup options and desired values, option value is highlighted
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
    try:
        return serial.enter_menu(key, option_path, try_counts, confirm_msg)
    except Exception as e:
        logging.error("Exception occur: {0}".format(e))


# locate a setup option by given option name and default value
# setupoption = ['name','value'] e.g. ["Boot Type", "<UEFI Boot Type>"]
# Patten1: Only option name is highlighted, name should be specified, value not required
# Patten2: Only value is highlighted, both name and value need to be specified, e.g.["Boot Type", "<UEFI Boot Type>"]
def locate_option(serial, key, setupoption, try_counts):
    return serial.locate_setup_option(key, setupoption, try_counts)


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    logging.info("SetUpLib: Boot to setup main page")
    logging.info("SetUpLib: Rebooting SUT...")
    if not PowerLib.force_reset(ssh):
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
    if not PowerLib.force_reset(ssh):
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
    SerialLib.send_key(serial, Key.DOWN)
    if SerialLib.is_msg_present(serial, "Boot From File", delay=10):
        logging.info("UEFI boot mode detected.")
        SerialLib.send_keys_with_delay(serial, [Key.RIGHT, Key.RIGHT])
    else:
        logging.info("Legacy boot mode detected")
        SerialLib.send_key(serial, Key.RIGHT)
    SerialLib.send_key(serial, Key.ENTER)
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
    serial.send_keys(Key.ENTER)
    if not serial.is_msg_present(values):
        logging.info("Supported values are not correct.")
        serial.send_keys(Key.ESC)
        return
    logging.info("Supported values are verified.")
    serial.send_keys(Key.ESC)
    return True


# Boot to boot manager with hotkey
def boot_to_bootmanager(serial, ssh):
    key = Key.F11
    msg = "Boot Manager Menu"
    return boot_with_hotkey(serial, ssh, key, msg, 300)


# Switch to legacy mode
def enable_legacy_boot(serial, ssh):
    logging.info("Switch to legacy boot mode")
    if not boot_to_page(serial, ssh, Msg.PAGE_BOOT):
        return
    if not locate_option(serial, Key.DOWN, ["Boot Type", "<UEFIBoot>"], 25):
        return
    logging.info("Change boot type to legacy mode")
    SerialLib.send_key(serial, Key.F5)
    if not locate_option(serial, Key.DOWN, ["Boot Type", "<LegacyBoot>"], 25):
        logging.info("Failed to change boot type.")
        return
    logging.info("Save and reboot")
    SerialLib.send_keys_with_delay(serial, [Key.F10, Key.Y], 5)
    if not SerialLib.is_msg_present(serial, 'Start of legacy boot'):
        logging.info("Not in legacy mode")
        return
    logging.info("Boot in legacy mode")
    return True


# Switch to uefi boot mode
def disable_legacy_boot(serial, ssh):
    logging.info("Switch to uefi boot mode")
    if not boot_to_page(serial, ssh, Msg.PAGE_BOOT):
        return
    if not locate_option(serial, Key.DOWN, ["Boot Type", "<LegacyBoot>"], 25):
        return
    logging.info("Change boot type to UEFI mode")
    SerialLib.send_key(serial, Key.F6)
    if not locate_option(serial, Key.DOWN, ["Boot Type", "<UEFIBoot>"], 25):
        logging.info("Failed to change boot type.")
        return
    logging.info("Save and reboot")
    SerialLib.send_keys_with_delay(serial, [Key.F10, Key.Y], 5)
    if not SerialLib.is_msg_not_present(serial, 'Start of legacy boot', 'BIOS boot completed.'):
        logging.info("Not in UEFI mode")
        return
    logging.info("Boot in UEFI mode")
    return True


# Boot Suse from boot manager
def boot_suse_from_bm(serial, ssh):
    suse_linux = ["SUSE Linux Enterprise\(LUN0\)"]
    msg = "Welcome to GRUB"
    if not boot_to_bootmanager(serial, ssh):
        return
    if not enter_menu(serial, Key.DOWN, suse_linux, 8, msg):
        return
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE):
        return
    logging.info("OS Boot Successful")
    return True


# Move a specific boot option up
def move_boot_option_up(serial, ssh, boot_option, count):
    hdd_group = [Msg.MENU_BOOT_ORDER, Msg.MENU_HDD_BOOT]
    logging.info("Move: {0} {1} times".format(boot_option, count))
    if not boot_to_page(serial, ssh, Msg.PAGE_BOOT):
        return
    if not enter_menu(serial, Key.DOWN, hdd_group, 25, boot_option[0]):
        return
    if not locate_option(serial, Key.DOWN, boot_option, 10):
        return
    logging.info("Move option up")
    for n in range(count):
        SerialLib.send_key(serial, Key.F6)
    logging.info("Save and reboot.")
    SerialLib.send_keys_with_delay(serial, [Key.F10, Key.Y])
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE, delay=600):
        return
    return True


# Update default password, should be called after update bios
def update_default_password(serial, ssh_bmc):
    logging.info("Change BIOS password to non-default.")
    if not PowerLib.force_reset(ssh_bmc):
        return
    if not SerialLib.is_msg_present(serial, Msg.HOTKEY_PROMPT_DEL):
        return
    SerialLib.send_key(serial, Key.DEL)
    if not SerialLib.is_msg_present(serial, Msg.PW_PROMPT):
        return
    SerialLib.send_data(serial, SutConfig.BIOS_PW_DEFAULT)
    SerialLib.send_key(serial, Key.ENTER*2)
    if not SerialLib.is_msg_present(serial, "Enter New Password"):
        return
    SerialLib.send_data(serial, SutConfig.BIOS_PASSWORD)
    SerialLib.send_key(serial, Key.ENTER)
    SerialLib.send_data(serial, SutConfig.BIOS_PASSWORD)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, Msg.HOME_PAGE):
        return
    logging.info("Password changed to non-default successfully")
    return True

