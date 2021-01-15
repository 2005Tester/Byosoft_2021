import logging
from ICX2P.SutConfig import Key
from ICX2P import SutConfig
from ICX2P.SutConfig import Msg
from ICX2P.BaseLib import icx2pAPI


# Enter setup menu
def enter_menu(key, option_path, try_counts, confirm_msg, serial):
    return serial.enter_menu(key, option_path, try_counts, confirm_msg)


# locate a setup option by given option name and default value
def locate_option(key, setupoption, try_counts, serial):
    return serial.locate_setup_option(key, setupoption, try_counts)


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    logging.info("SetUpLib: Boot to setup main page")
    logging.info("SetUpLib: Rebooting SUT...")
    if not icx2pAPI.force_reset(ssh):
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    if not serial.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
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
    serial.send_keys_with_delay(SutConfig.key2Setup)
    if not serial.is_msg_present('System Time'):
        logging.info("SetUpLib: Boot to BIOS Configuration Failed")
        return
    logging.info("SetUpLib: Boot to BIOS Configuration successfully")
    return True


# boot to specific page in bios configuration
def boot_to_page(page_name, serial, ssh):
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
def verify_supported_values(values, serial):
    serial.send_keys(Key.ENTER)
    if not serial.is_msg_present(values):
        logging.info("Supported values are not correct.")
        serial.send_keys(Key.ESC)
        return
    logging.info("Supported values are verified.")
    serial.send_keys(Key.ESC)  
    return True


    
