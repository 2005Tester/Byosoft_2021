import logging
import time
from batf import SerialLib
from batf.SutInit import Sut
from D2000.BaseLib import BmcLib, SshLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
import re


# Send a single key, e.g. ENTER, DOWN, UP
def send_key(key):
    Sut.BIOS_COM.send_keys(key)


# send keys with default delay = 1s, e.g. [F10, Y]
def send_keys(keys, delay=1):
    time.sleep(1)
    SerialLib.send_keys_with_delay(Sut.BIOS_COM, keys, delay)


# send data to BIOS serial port向串口发送数据
def send_data(data):
    def cut(obj, sec):
        return [obj[i:i + sec] for i in range(0, len(obj), sec)]

    for i in cut(data, 20):
        SerialLib.send_data(Sut.BIOS_COM, i)
        time.sleep(1)


# send a string and enter to BIOS serial port
def send_data_enter(data):
    def cut(obj, sec):
        return [obj[i:i + sec] for i in range(0, len(obj), sec)]

    for i in cut(data, 20):
        SerialLib.send_data(Sut.BIOS_COM, i)
        time.sleep(1)
    send_key(Key.ENTER)


# 清除缓冲
def clean_buffer():
    time.sleep(1)
    SerialLib.clean_buffer(Sut.BIOS_COM)


def reboot():
    if SutConfig.Env.MACHINE_TYPE.lower() == 'server':
        BmcLib.init_sut()
    else:
        if BmcLib.ping_sut(2):
            try:
                SshLib.reboot('reboot')
                time.sleep(2)
            except:
                pass
        time.sleep(1)
        send_key(Key.CTRL_ALT_DELETE)


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
def enter_menu(key, option_path, try_counts, confirm_msg=None, timeout=5):
    if type(option_path) == str:
        option_path = [option_path]
    logging.info("Go to setup menu:{0}".format(option_path))
    for option in option_path:
        if option in SutConfig.Msg.PAGE_ALL:
            assert back_to_setup_toppage()
            assert boot_to_page(option)
        else:
            logging.info("Locate menu: {0}".format(option))
            if not locate_option(key, [option], try_counts):
                if not locate_option(Key.UP, [option], try_counts):  # 修复当要找的分区在最上面，导致找不到的问题
                    logging.info("Not Found: {0}".format(option))
            send_keys(Key.ENTER)
    if confirm_msg:
        if not wait_message(confirm_msg, timeout):
            logging.info("{0} not captured, may not enter corect menu".format(confirm_msg))
            return
    logging.info("Enter menu: {0} successfully".format(option_path[-1]))
    return True


# locate a setup option by given option name and default value
# setupoption = ['name','value'] e.g. ["Boot Type", "<UEFI Boot Type>"]
# Patten1: Only option name is highlighted, name should be specified, value not required
# Patten2: Only value is highlighted, both name and value need to be specified, e.g.["Boot Type", "<UEFI Boot Type>"]
help_msg = ''


def locate_option(key, setupoption, try_counts, delay=1, readline=False):
    data_before = ''
    ES = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}"
    if len(setupoption) == 1:
        patten = f'(?:{setupoption[0]})' + ES
    elif len(setupoption) == 2:
        patten = ES + "{0}".format(setupoption[1]) + ES + "\s+" + ES + "\s+" + ES + "{0}".format(setupoption[0])

    else:
        logging.info("Incorrect format of parameter: setupoption, should be list")
        return
    logging.info("Locate option: {0}".format(setupoption))
    if wait_message(patten, delay + 1, cleanup=False, readline=readline):
        logging.info("Option found: {0}".format(setupoption))
        return True
    else:
        send_key(key)
        while try_counts:
            data = get_data(delay, cleanup=False)
            if data == data_before and data != '':
                break
            if re.search(patten, data):
                logging.info("Option found: {0}".format(setupoption))
                global help_msg
                if re.findall(f'{setupoption[0]}\s*(.+)', Sut.BIOS_COM.cleanup_data(data)):
                    help_msg = re.findall(f'{setupoption[0]}\s*(.+)', Sut.BIOS_COM.cleanup_data(data))[0].strip()
                return True
            data_before = data
            try_counts -= 1
            Sut.BIOS_COM.send_keys(key)
        logging.info("Option not found: {0}".format(setupoption))


def boot_to_setup(key=SutConfig.Msg.SETUP_KEY):
    reboot()
    logging.info("SetUpLib: Booting to setup")
    try_counts = 3
    while try_counts:
        if SutConfig.Env.OEM_SUPPORT:
            BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        if not boot_with_hotkey_only(key, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE):
            # logging.info("{0} not found".format(SutConfig.Msg.POST_MESSAGE))
            reboot()
            try_counts -= 1
        else:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


def continue_to_setup():
    logging.info("SetUpLib: Continue boot to setup main page")
    if not boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


# boot to setup,boot menu,pxe without reset
def boot_with_hotkey_only(key, msg, timeout=250, hotkey_prompt="Press Del go to Setup Utilityasda",
                          pw_prompt="Press F2asdas", password="Admin@9009"):
    count = 0
    psw = False
    start_time = time.time()
    logging.debug("boot_with_hotkey: Receiving data from SUT...")
    Sut.BIOS_COM.session.flushInput()
    while True:
        try:
            if Sut.BIOS_COM.session.in_waiting:
                data = Sut.BIOS_COM.session.readline().decode("utf-8", errors='ignore')
                data = Sut.BIOS_COM.cleanup_data(data)

                if Sut.BIOS_COM.find_msg(hotkey_prompt, data):
                    Sut.BIOS_COM.send_keys(key)
                    count = 1
                    logging.info("Hot Key sent")
                if Sut.BIOS_COM.find_msg(pw_prompt, data):
                    time.sleep(2)
                    Sut.BIOS_COM.send_data(password)
                    time.sleep(2)
                    Sut.BIOS_COM.send_data(chr(0x0D))  # Send Enter
                    logging.info("Send password...")
                    psw = True
                if Sut.BIOS_COM.find_msg(msg, data):
                    if psw == True:
                        return [True, True]
                    else:
                        return True
        except Exception as e:
            logging.error(e)
            logging.debug("boot_with_hotkey: Please check whether COM port is in use.")
            break

        if Sut.BIOS_COM.is_timeout(start_time, timeout):
            if count == 1:
                logging.info('Hot Key sent,but did not find confirm msg')
            else:
                logging.info('{0} not found'.format(hotkey_prompt))
            break


# reset and boot to setup,boot menu,pxe
def boot_with_hotkey(key, msg, timeout, hotkey_prompt):
    reboot()
    try_counts = 3
    while try_counts:
        if SutConfig.Env.OEM_SUPPORT:
            BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        if not boot_with_hotkey_only(key, msg, timeout, hotkey_prompt):
            # logging.info("{0} not found".format(msg))
            reboot()
            try_counts -= 1
        else:
            logging.info("Boot with hotkey successfully.")
            return True

    logging.info("Boot with hotkey fail.")
    return


def boot_to_page(page_name):
    logging.info("SetUpLib: Move to specified setup page")
    if not locate_option(Key.RIGHT, [page_name], 12, 1.5, readline=True):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


def boot_to_linux_os(key=SutConfig.Msg.BOOTMENU_KEY):
    if not boot_with_hotkey(key, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        return
    if not select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
        return
    else:
        if BmcLib.ping_sut():
            time.sleep(30)
            logging.info("OS Boot Successed.")
            return True
        else:
            return


def boot_to_windows_os(key=SutConfig.Msg.BOOTMENU_KEY):
    if not boot_with_hotkey(key, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        return
    if not select_boot_option(Key.DOWN, SutConfig.Msg.WINDOWS_OS, 30, ''):
        return
    else:
        if BmcLib.ping_sut():
            time.sleep(30)
            logging.info("OS Boot Successed.")
            return True
        else:
            return


def boot_to_shell(key=SutConfig.Msg.BOOTMENU_KEY):
    if not boot_with_hotkey(key, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        return
    if not select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 30, 'UEFI Interactive Shell'):
        return
    logging.info('Shell Boot Successed.')
    time.sleep(10)
    return True


# Boot to kylin os from boot manager
def boot_os_from_bm(key=SutConfig.Msg.BOOTMENU_KEY, os_type="linux"):
    if not boot_with_hotkey(key, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        return
    if os_type.lower() == "linux":
        if not select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
    elif os_type.lower() == "kylin":
        if not select_boot_option(Key.DOWN, SutConfig.Msg.KYLIN_OS, 30, ''):
            return
    elif os_type.lower() == "centos":
        if not select_boot_option(Key.DOWN, SutConfig.Msg.CENTOS_OS, 30, ''):
            return
    elif os_type.lower() == "uos":
        if not select_boot_option(Key.DOWN, SutConfig.Msg.UOS_OS, 30, ''):
            return
    elif os_type.lower() == "windows":
        if not select_boot_option(Key.DOWN, SutConfig.Msg.WINDOWS_OS, 30, ''):
            return
    else:
        logging.error("OS type is invalid, please double check.")
        return
    if not BmcLib.ping_sut():
        if os_type.lower() == "windows":
            logging.info("Boot Windows failed.")
            logging.info("The system may have gone into recovery mode.")
            logging.info("Try again.")
            if not boot_os_from_bm("windows"):
                return
        else:
            return
    logging.info("OS Boot Successed.")
    time.sleep(10)
    return True


def boot_to_boot_menu(data_save=False):
    reboot()
    if not wait_message(SutConfig.Msg.POST_MESSAGE):
        reboot()
        assert wait_message(SutConfig.Msg.POST_MESSAGE)
    send_key(SutConfig.Msg.BOOTMENU_KEY)
    start = time.time()
    datas = ''
    while True:
        data = get_data(1)
        datas += data
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, data):
            time.sleep(1)
            if data_save:
                return datas
            else:
                return True
        now = time.time()
        if now - start > 60:
            break
    logging.info('Boot to bootmenu fail')
    return


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
    if not BmcLib.ping_sut():
        logging.info("Reset dafault by F9:Fail")
        return
    logging.info("Reset dafault by F9:Pass")
    return True


# judge whether find msg
# delay:time of collect data and judgement
# cleanup:if clean up, judge in data useless data have been cleaned
# readline:if readline,if readline,collect data by row
def wait_message(msg, delay=250, pw_prompt=None, pw=None, cleanup=True, readline=False):
    # return SerialLib.is_msg_present_clean(Sut.BIOS_COM,msg,delay,cleanup=cleanup)
    logging.debug("Waiting for:\"{0}\"".format(msg))
    start_time = time.time()
    data = ''
    clean_data = ''
    while True:
        if Sut.BIOS_COM.session.in_waiting:
            try:
                if readline:
                    data = Sut.BIOS_COM.session.readline().decode("utf-8", errors='ignore')
                    if cleanup:
                        clean_data = Sut.BIOS_COM.cleanup_data(data)
                    else:
                        Sut.BIOS_COM.write_data2log(data)
                else:
                    initial_data = Sut.BIOS_COM.session.read(1024).decode("utf-8", errors='ignore')
                    data = data + initial_data
                    if cleanup:
                        clean_data = Sut.BIOS_COM.cleanup_data(data, save=False)
                        Sut.BIOS_COM.cleanup_data(initial_data)
                    else:
                        Sut.BIOS_COM.write_data2log(initial_data)
            except Exception as e:
                logging.error(e)
                logging.error("is_msg_present_general: error in reading serial data")
            if pw_prompt and Sut.BIOS_COM.find_msg(pw_prompt, data):
                Sut.BIOS_COM.send_data(pw)
                Sut.BIOS_COM.send_data(chr(0x0D))  # Send Enter
                logging.info("Send password...")
            if cleanup:
                if Sut.BIOS_COM.find_msg(msg, clean_data):
                    logging.debug("Message found.")
                    return True
            else:
                if Sut.BIOS_COM.find_msg(msg, data):
                    logging.debug("Message found.")
                    return True

        if Sut.BIOS_COM.is_timeout(start_time, delay):
            if delay > 5:
                data = ''
                logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
            break


# send key ENTER ,then judge whether find msg
def wait_message_enter(msg, delay=250, pw_prompt=None, pw=None, cleanup=True, readline=True):
    # close_session()
    # time.sleep(0.5)
    # open_session()
    # time.sleep(0.5)
    # send_key(Key.ENTER)
    # return SerialLib.is_msg_present_clean(Sut.BIOS_COM, msg, delay, cleanup=cleanup)
    clean_buffer()
    logging.debug("Waiting for:\"{0}\"".format(msg))
    start_time = time.time()
    send_key(Key.ENTER)
    while True:
        if Sut.BIOS_COM.session.in_waiting:
            try:
                if readline:
                    data = Sut.BIOS_COM.session.readline().decode("utf-8", errors='ignore')
                else:
                    data = Sut.BIOS_COM.session.read(1024).decode("utf-8", errors='ignore')
                if cleanup:
                    data = Sut.BIOS_COM.cleanup_data(data)
                else:
                    Sut.BIOS_COM.write_data2log(data)
            except Exception as e:
                logging.error(e)
                logging.error("is_msg_present_general: error in reading serial data")
            if pw_prompt and Sut.BIOS_COM.find_msg(pw_prompt, data):
                Sut.BIOS_COM.send_data(pw)
                Sut.BIOS_COM.send_data(chr(0x0D))  # Send Enter
                logging.info("Send password...")
            if Sut.BIOS_COM.find_msg(msg, data):
                logging.debug("Message found.")
                data = ''
                return True
        if Sut.BIOS_COM.is_timeout(start_time, delay):
            if delay > 5:
                data = ''
                logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
            break


# return serial data
# delay:time of collect data
# key:if key,it will send key ,then collect data
# cleanup:if clean,useless data will be cleaned
# readline:if readline,collect data by row
def get_data(delay=10, key=None, cleanup=True, readline=True):
    start_time = time.time()
    if key != None:
        send_key(key)
    datas = ''
    while True:
        if Sut.BIOS_COM.session.in_waiting:
            try:
                if readline:
                    data = Sut.BIOS_COM.session.readline().decode("utf-8", errors='ignore')
                else:
                    data = Sut.BIOS_COM.session.read(1024).decode("utf-8", errors='ignore')
                datas += data
            except Exception as e:
                logging.error(e)
                logging.error("is_msg_present_general: error in reading serial data")
        if Sut.BIOS_COM.is_timeout(start_time, delay):
            break
    if cleanup:
        datas = Sut.BIOS_COM.cleanup_data(datas)
    else:
        Sut.BIOS_COM.write_data2log(datas)
    return datas


# close serial session
def close_session():
    return Sut.BIOS_COM.close_session()


# open serial session
def open_session():
    return Sut.BIOS_COM.open_session()


# Match a list of strings from serial port
def wait_strings(msg_list, delay=10):
    return SerialLib.is_msg_list_present(Sut.BIOS_COM, msg_list, delay)


# used to navigate to setup top page,
def back_to_setup_toppage(msg='Setup Configuration|配置确认'):
    try:
        try_counts = 10
        while try_counts:
            logging.info('Navigating to top page,')
            send_key(Key.ESC)
            if wait_message(msg, delay=2):
                time.sleep(0.5)
                send_key(Key.DISCARD_CHANGES)
                break

            try_counts -= 1
        logging.info("Current is top page,")
        return True
    except Exception as err:
        logging.debug(err)


# select a boot option in boot manager
# optionname: string, name of setup option
def select_boot_option(key, optionname, try_counts, confirm_msg):
    if len(optionname.replace('\\', '')) > 45 and optionname[-3:] != '...':
        optionname = optionname.replace('\\', '')[:45] + '...'
        optionname = optionname.replace('(', '\(').replace(')', '\)').replace('[', '\[').replace(']', '\]')

    es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
    patten = es + r"\x1B\[40m" + '(?:\x1b\[\d+;\d+H){1}' + f'(?:{optionname})'
    patten_before = es + r"\x1B\[44m" + '(?:\x1b\[\d+;\d+H){1}' + f'(?:{optionname})'
    while try_counts:
        data = get_data(1, cleanup=False)
        if re.search(patten, data):
            logging.info("Boot option found: {0}".format(optionname))
            send_key(Key.ENTER)
            if not wait_message(confirm_msg):
                logging.info("Boot to option: {0} Failed".format(optionname))
                return
            logging.info("Boot to option: {0} successfully".format(optionname))

            return True
        elif re.search(patten_before, data):
            send_key(Key.UP)
            if wait_message(patten, 2, cleanup=False):
                logging.info("Boot option found: {0}".format(optionname))
                send_key(Key.ENTER)
                if not wait_message(confirm_msg):
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
    if key_optionname == Key.DOWN:
        key = Key.UP
    elif key_optionname == Key.UP:
        key = Key.DOWN
    else:
        key = Key.DOWN
    if not locate_option(key_optionname, optionname, try_counts):
        if not locate_option(key, optionname, try_counts + 1):
            time.sleep(1)
            send_key(Key.ENTER)
        else:
            time.sleep(1)
            send_key(Key.ENTER)
    else:
        time.sleep(1)
        send_key(Key.ENTER)
    # assert locate_option(key_optionname, optionname, try_counts), 'locate option -> fail'
    # send_key(Key.ENTER)
    counts = try_counts
    while counts:
        time.sleep(2)
        if wait_message(patten, 2, cleanup=False):
            logging.info("value found: {0}".format(value))
            send_key(Key.ENTER)
            return True
        send_key(key_value)
        counts -= 1
    while try_counts:
        time.sleep(2)
        if wait_message(patten, 2, cleanup=False):
            logging.info("value found: {0}".format(value))
            send_key(Key.ENTER)
            return True
        send_key(Key.UP)
        try_counts -= 1
    logging.info("Value NOT found: {0}".format(value))


SEP = "(?:\x1b\[\d+;\d+H){1}"  # value separator
HLP = "(?:\x1b\[\d+m){3}"  # value hightlight ending flag, last appeared valid
# VALR = "(\w[\w -/]*\w)"  # bios value name ruler
VALR = "(\w[\w -:/]*[\w\)+])"  # bios value name ruler


# get values of setup option,return a list of values
def get_value_list():
    all_patten = re.compile(f"{SEP}{VALR}")
    Sut.BIOS_COM.session.flushInput()
    Sut.BIOS_COM.send_keys_with_delay(Key.ENTER)
    tmpdata = Sut.BIOS_COM.session.readline().decode('utf-8', errors='ignore')
    # tmpdata = Sut.BIOS_COM.receive_data(Sut.BIOS_COM.session.in_waiting)
    Sut.BIOS_COM.send_keys_with_delay(Key.ENTER)
    val_list = all_patten.findall(tmpdata)
    if not val_list:
        logging.error("Fail to match values list")
        return
    logging.info("Current option values: {}".format(val_list))
    return val_list


# locate a value of setup option
# value_str:name of value(without re),type str
def locate_value(value_str):
    all_patten = re.compile(f"{SEP}{VALR}")
    Sut.BIOS_COM.session.flushInput()
    Sut.BIOS_COM.send_keys_with_delay(Key.ENTER)
    tmpdata = Sut.BIOS_COM.receive_data(Sut.BIOS_COM.session.in_waiting)
    Sut.BIOS_COM.write_data2log(tmpdata)
    val_list = all_patten.findall(tmpdata)
    if not val_list:
        logging.error("Fail to match values list")
        return
    logging.info("Current option values: {}".format(val_list))
    hl_patten = re.compile(f"{SEP}{VALR}{HLP}")  # hight patten
    if '|' in value_str:
        if any(i in val_list for i in value_str.split('|')):
            for j in value_str.split('|'):
                if j in val_list:
                    value_str = j
        else:
            logging.error('"{}" not in value list'.format(value_str))
            send_key(Key.ESC)
            return
    else:
        if value_str not in val_list:
            logging.error('"{}" not in value list'.format(value_str))
            send_key(Key.ESC)
            return
    Sut.BIOS_COM.session.flushInput()

    hl_default = hl_patten.findall(tmpdata)
    if hl_default[-1] == value_str:
        logging.info('Current select option is "{}"'.format(value_str))
        return True
    offset = val_list.index(value_str) - val_list.index(hl_default[-1])
    press_key = Key.DOWN if offset > 0 else Key.UP
    key_cnt = abs(offset)
    for k in range(key_cnt):
        send_key(press_key)
        time.sleep(1)
        tmpdata = Sut.BIOS_COM.receive_data(Sut.BIOS_COM.session.in_waiting)
    hl_current = hl_patten.findall(tmpdata)
    if not hl_current:
        logging.error("Fail to verify current select value after key pressed")
        return
    if hl_current[-1] == value_str:
        logging.info('Locate to value "{}" pass'.format(value_str))
        return True
    logging.error('Locate to value "{}" failed'.format(value_str))


# locate option and change value
# key_optionname:UP,DOWN
# optionname:name of option(re)
# try_counts:try counts
# value_str:name of value(withour re)
def change_option_value(key_optionname, optionname, try_counts, value_str, delay=1):
    if key_optionname == Key.DOWN:
        key = Key.UP
    elif key_optionname == Key.UP:
        key = Key.DOWN
    else:
        key = Key.DOWN
    if not locate_option(key_optionname, optionname, try_counts, delay):
        if not locate_option(key, optionname, try_counts + 1):
            time.sleep(0.5)
        else:
            time.sleep(0.5)
    else:
        time.sleep(1.5)
    if locate_value(value_str):
        time.sleep(0.5)
        send_key(Key.ENTER)
        time.sleep(0.5)
        return True
    else:
        logging.info("Value NOT found: {0}".format(value_str))


def locate_menu(key, option_path, try_counts):
    if type(option_path) == str:
        option_path = [option_path]
    logging.info("Go to setup menu:{0}".format(option_path))
    for option in option_path:
        if option in SutConfig.Msg.PAGE_ALL:
            assert back_to_setup_toppage()
            assert boot_to_page(option)
        else:
            logging.info("Locate menu: {0}".format(option))
            if not locate_option(key, [option], try_counts):
                if not locate_option(Key.UP, [option], try_counts + 1):  # 修复当要找的分区在最上面，导致找不到的问题
                    logging.info("Not Found: {0}".format(option))
                    return
            if option != option_path[-1]:
                send_keys(Key.ENTER)
    return True


# go to option,change option value , then go to another option and change value
# key:DOWN (unnecessary to change)
# option_path:a list of option path,e.g.['User Wait Time',{'Boot Mode':'UEFI'},'Console Redirection','USB Configuration',{'USB Mass Storage Support':'Disabled'}]
#            if page name ,it will run boot_to_page;
#            if option name, it will run locate_option;
#            if dict(e.g.{option:value}), it will go to option and change value
# try_counts:as big as possible
def enter_menu_change_value(key, option_path, try_counts):
    if type(option_path) == str:
        option_path = [option_path]
    for index, option in enumerate(option_path):
        if option in SutConfig.Msg.PAGE_ALL:
            if index > 0:
                if len(option_path) > 1 and option_path[index - 1] == option:
                    if not locate_option(key, [option], 3):
                        if not locate_option(Key.UP, [option], 4):
                            time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                    send_key(Key.ENTER)
                else:
                    assert back_to_setup_toppage()
                    assert boot_to_page(option)
            else:
                assert back_to_setup_toppage()
                assert boot_to_page(option)
        elif type(option) == dict:
            if isinstance(list(option.values())[0], int):
                if list(option.keys())[0] == option_path[index - 1] and option_path[
                    index - 1] in SutConfig.Msg.PAGE_ALL:
                    time.sleep(0.5)
                    send_key(Key.ENTER)
                    time.sleep(1)
                    send_data_enter(str(list(option.values())[0]))
                    time.sleep(0.5)
                else:
                    if not locate_option(key, list(option.keys()), try_counts):
                        if not locate_option(Key.UP, list(option.keys()), try_counts + 1):
                            time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                            send_key(Key.ENTER)
                            time.sleep(1)
                            send_data_enter(str(list(option.values())[0]))
                            time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                        send_key(Key.ENTER)
                        time.sleep(1)
                        send_data_enter(str(list(option.values())[0]))
                        time.sleep(0.5)
            else:
                if list(option.keys())[0] == option_path[index - 1] and option_path[
                    index - 1] in SutConfig.Msg.PAGE_ALL:
                    if locate_value(list(option.values())[0]):
                        time.sleep(0.5)
                        send_key(Key.ENTER)
                        time.sleep(0.5)
                    else:
                        logging.info("Value NOT found: {0}".format(list(option.values())[0]))
                else:
                    assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
        else:
            if not locate_option(key, [option], try_counts):
                if not locate_option(Key.UP, [option], try_counts + 1):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.5)
            send_key(Key.ENTER)
    return True


# similar to function enter_menu_change_value,the only difference is if not locate_option it can continue
def enter_menu_change_value_ignore(key, option_path, try_counts):
    if type(option_path) == str:
        option_path = [option_path]
    for index, option in enumerate(option_path):
        if option in SutConfig.Msg.PAGE_ALL:
            if len(option_path) > 1 and option_path[index - 1] == option:
                if not locate_option(key, [option], 3):
                    if not locate_option(Key.UP, [option], 4):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                send_key(Key.ENTER)
            else:
                assert back_to_setup_toppage()
                assert boot_to_page(option)
        elif type(option) == dict:
            if isinstance(list(option.values())[0], int):
                if list(option.keys())[0] == option_path[index - 1] and option_path[
                    index - 1] in SutConfig.Msg.PAGE_ALL:
                    time.sleep(0.5)
                    send_key(Key.ENTER)
                    time.sleep(1)
                    send_data_enter(str(list(option.values())[0]))
                    time.sleep(0.5)
                else:
                    if not locate_option(key, list(option.keys()), try_counts):
                        if not locate_option(Key.UP, list(option.keys()), try_counts + 1):
                            time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                            send_key(Key.ENTER)
                            time.sleep(1)
                            send_data_enter(str(list(option.values())[0]))
                            time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                        send_key(Key.ENTER)
                        time.sleep(1)
                        send_data_enter(str(list(option.values())[0]))
                        time.sleep(0.5)
            else:
                if list(option.keys())[0] == option_path[index - 1] and option_path[
                    index - 1] in SutConfig.Msg.PAGE_ALL:
                    if locate_value(list(option.values())[0]):
                        time.sleep(0.5)
                        send_key(Key.ENTER)
                        time.sleep(0.5)
                    else:
                        logging.info("Value NOT found: {0}".format(list(option.values())[0]))
                else:
                    change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
        else:
            if not locate_option(key, [option], try_counts):
                if not locate_option(Key.UP, [option], try_counts + 1):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.5)
            send_key(Key.ENTER)
    return True


def enable_legacy_boot():
    time.sleep(5)
    BmcLib.change_bios_value(['BootMode:Legacy'])
    time.sleep(2)
    BmcLib.power_cycle()
    time.sleep(5)
    # assert boot_to_setup()
    # assert enter_menu_change_value(Key.DOWN,SutConfig.Sup.BOOT_LEGACY,18)
    # time.sleep(1)
    # send_keys(Key.SAVE_RESET)
    # time.sleep(5)
    return True


def disable_legacy_boot():
    time.sleep(5)
    BmcLib.change_bios_value(['BootMode:UEFI'])
    time.sleep(2)
    BmcLib.power_cycle()
    time.sleep(5)
    # assert boot_to_setup()
    # assert enter_menu_change_value(Key.DOWN,SutConfig.Sup.BOOT_UEFI,18)
    # time.sleep(1)
    # send_keys(Key.SAVE_RESET)
    # time.sleep(5)
    return True


def get_shell_fs_num():
    send_data('Map')
    time.sleep(1)
    send_key(Key.ENTER)
    fs = []
    data = get_data(2).replace('\r', '').split('\n')
    for index in range(0, len(data)):
        if re.search('USB', data[index]):
            fs = re.findall('(FS\d+:) ', data[index - 1])
            break
    if fs:
        send_data_enter(fs[0])
        time.sleep(1)
        send_data_enter('ls')
        if SutConfig.Env.BIOS_FILE in get_data(2):
            return fs[0]
        else:
            return ''
    else:
        return ''


def check_grey_out_option(options, option_path, all_path=False):
    assert boot_to_page(SutConfig.Msg.PAGE_MAIN)
    datas = ''
    if all_path:
        trycounts = 12
        while trycounts:
            clean_buffer()
            data = get_data(2, Key.RIGHT, cleanup=False, readline=False)
            datas += data
            if SutConfig.Msg.PAGE_MAIN in data:
                break
            trycounts -= 1
    for index, option in enumerate(option_path):
        if option in SutConfig.Psw.PAGE_ALL:
            if len(option_path) > 1 and option_path[index - 1] == option:
                if not locate_option(Key.DOWN, [option], 3):
                    if not locate_option(Key.UP, [option], 4):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                clean_buffer()
                send_key(Key.ENTER)
                data = get_data(2, cleanup=False, readline=False)
                datas += data
            else:
                assert back_to_setup_toppage()
                assert boot_to_page(option)
        elif option == 'ESC':
            time.sleep(1)
            send_key(Key.ESC)
            time.sleep(1)
        else:
            if not locate_option(Key.DOWN, [option], 25):
                if not locate_option(Key.UP, [option], 28):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.5)
            clean_buffer()
            send_key(Key.ENTER)
            data = get_data(3, cleanup=False, readline=False)
            datas += data
    SEP = '(?:\x1b\[\d+;\d+H)'
    HLP = "(?:\x1b\[\d+m){1}"
    if all(not re.search(f'\x1b\[3[47]m\x1b\[47m{SEP}{i}[\w\s\[\]\(\)<>]*{SEP}*[\w\s\[\]\(\)<>]*{HLP}', datas) for i in
           options):
        logging.info('All options grey out')
        return True
    else:
        for option in options:
            if re.search(f'\x1b\[3[47]m\x1b\[47m{SEP}{option}[\w\s\[\]\(\)<>]*{SEP}*[\w\s\[\]\(\)<>]*{HLP}', datas):
                logging.info(f'"{option}" not grey out')
        return


def shell_bios_file():
    send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    send_data_enter('ls')
    if SutConfig.Env.BIOS_FILE not in get_data(2):
        fs = get_shell_fs_num()
        send_data_enter(fs)
        time.sleep(2)
    send_data_enter('cd {}'.format(SutConfig.Env.BIOS_FILE))
    time.sleep(2)
    return True


def linux_mount_usb():
    mount_path = SutConfig.Env.LINUX_USB_DEVICE
    disk_list = SshLib.execute_command_limit(Sut.OS_SSH, 'fdisk -l')[0]
    path = re.findall('(/dev/\w+)\s+\*\s+\d+ ', disk_list)
    if path:
        for i in path:
            SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(i, SutConfig.Env.LINUX_USB_MOUNT))
            output = SshLib.execute_command_limit(Sut.OS_SSH, f'cd {SutConfig.Env.LINUX_USB_MOUNT};ls')[0]
            if SutConfig.Env.BIOS_FILE in output:
                mount_path = i
                SshLib.execute_command_limit(Sut.OS_SSH, "umount {0} {1}".format(i,
                                                                                 SutConfig.Env.LINUX_USB_MOUNT))
                break
            else:
                SshLib.execute_command_limit(Sut.OS_SSH, "umount {0} {1}".format(i,
                                                                                 SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(mount_path,
                                                                    SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp ByoCfg /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp ByoDmi /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp ByoFlash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    SshLib.execute_command_limit(Sut.OS_SSH, 'chmod 777 ByoCfg')
    SshLib.execute_command_limit(Sut.OS_SSH, 'chmod 777 ByoDmi')
    SshLib.execute_command_limit(Sut.OS_SSH, 'chmod 777 ByoFlash')
    return True


def regex_char_handle(strs):
    """正则表达式特殊字符串非转义处理: 在每一个正则敏感字符前加'\'斜杠"""
    return re.sub(r"([$()*+?\[\\^|{}.])", r"\\\1", strs)
