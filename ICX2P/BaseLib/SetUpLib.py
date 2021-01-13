import datetime
import logging
import time
from ICX2P.SutConfig import Key
from ICX2P import SutConfig
from ICX2P.SutConfig import Msg
from ICX2P.BaseLib import icx2pAPI


# Boot to setup home page after a force reset
def boot_to_setup(serial, ssh):
    logging.info("SetUpLib: Boot to setup home page")
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


# Boot to BIOS configuration page
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

# Boot to Virtulization Configuration Menu
def boot_to_virtulization_config(serial, ssh):
    if not boot_to_bios_config(serial, ssh):
        return
