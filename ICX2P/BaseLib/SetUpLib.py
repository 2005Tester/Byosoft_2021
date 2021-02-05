from Common import ssh
import logging
import time
from ICX2P.SutConfig import Key
from ICX2P import SutConfig
from ICX2P.SutConfig import Msg
from ICX2P.BaseLib import icx2pAPI, PowerLib


# Send a single key, e.g. ENTER, DOWN, UP 
def send_key(serial, key):
    serial.send_keys(key)


# send keys with default delay = 1s, e.g. [F10, Y]
def send_keys(serial, keys, delay=1):
    serial.send_keys_with_delay(keys, delay=1)


# verify information like CPU, memory in one setup page
def verify_info():
    # todo
    pass


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
    serial.send_keys_with_delay(SutConfig.key2Setup)
    if not serial.is_msg_present('System Time'):
        logging.info("SetUpLib: Boot to BIOS Configuration Failed")
        return
    logging.info("SetUpLib: Boot to BIOS Configuration successfully")
    return True


# boot to specific page in bios configuration
def boot_to_page(serial, page_name, ssh):
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
    

def msg_Strings(self, msg_list=None, timeout=10):
    """
    Read data from Console Redirection port, and wait more than 1 string
    :param msg_list: Multiple strings wait to be captured
    :param timeout: Timeout of wait duration
    :return: True, if all strings get from COM port
             False, script has not captured all strings after timeout
    """
    if msg_list is None:
        msg_list = []
    t_start = time.time()
    tmp = []
    var = ''
    # self.buffer = ""
    while True:
        try:
            count = self.session.inWaiting()  # Serial port buffer data
            if count != 0:
                rev = self.session.read(count).decode()
                self.buffer += rev
                rev = self.cleanup_data(self.buffer)
                for i in range(len(msg_list)):
                    if msg_list[i] not in rev:
                        var = msg_list[i]
                    else:
                        tmp.append(msg_list[i])

            time.sleep(0.1)
        except Exception as e:
            logging.error("Error:{0}".format(e))

        if tmp == msg_list:
            logging.info('Find strings:{0}'.format(tmp))
            return True

        now = time.time()
        spent_time = (now - t_start)
        if spent_time > timeout:
            logging.info("Can not find strings(timeout):{0}".format(var))
            return False
