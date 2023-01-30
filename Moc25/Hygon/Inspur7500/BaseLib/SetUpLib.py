# -*- encoding=utf8 -*-
import logging
import os
import time
from io import BytesIO

from batf import SerialLib, var
from batf.SutInit import Sut
from Inspur7500.BaseLib import BmcLib, SshLib, PwdLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
import re


# Send a sirngle key, e.g. ENTER, DOWN, UP
def send_key(key):
    Sut.BIOS_COM.send_keys(key)


# send keys with default delay = 1s, e.g. [F10, Y]
def send_keys(keys, delay=1):
    for key in keys:
        time.sleep(delay)
        Sut.BIOS_COM.send_keys(key)


# send data to BIOS serial port向串口发送数据
def send_data(data):
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(1)


# send a string and enter to BIOS serial port
def send_data_enter(data):
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(2)
    send_key(Key.ENTER)


# 清除缓存数据
def clean_buffer(timeout=2):
    time.sleep(0.5)
    Sut.BIOS_COM.session.timeout = 0.1
    t_start = time.time()
    data = []
    while not Sut.BIOS_COM.is_timeout(t_start, timeout):
        Sut.BIOS_COM.session.flushInput()
        time.sleep(0.01)
        data.append(Sut.BIOS_COM.session.read(512))
        if data[-5:] == [b'', b'', b'', b'', b'']:
            break
    Sut.BIOS_COM.session.timeout = Sut.BIOS_COM.timeout
    return True


def default_save():
    time.sleep(1)
    send_keys(Key.RESET_DEFAULT)
    time.sleep(15)
    send_keys(Key.SAVE_RESET)
    time.sleep(15)


def write_datalog(data):
    path = re.sub(r':\\[a-zA-Z]+', r':\\logview', var.get('serial_log'))
    os.makedirs(re.sub(r'\\TC\d+.log', '', path), exist_ok=True)
    with open(path, 'a', encoding='utf-8', errors='ignore') as f:
        f.write(data + '\n')


# verify information like CPU, memory in one setup page, option name is highlighted
# infos: list e.g. ['BIOS Revision\s+5.[0-9]{2}']
def verify_info(info_list, trycounts):
    data = get_data(2)
    for i in info_list[:]:
        if re.search(i, data):
            info_list.remove(i)
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


def option(strs, high_pat=(1, 37, 47), high_pat_end=(1, 30, 47)):
    high_pat = '\x1b\[{}m\x1b\[{}m\x1b\[{}m\x1b'.format(*high_pat)
    high_pat_end = '\x1b\[{}m\x1b\[{}m\x1b\[{}m'.format(*high_pat_end)

    class option:
        name = ''
        value = ''
        help = ''

    dict = {}
    op_va = re.findall(f'{high_pat}\[\d+;(\d+)H(.*?){high_pat_end}', strs)
    help_msg = ' '.join(re.findall(';\d*(?:73|91)H(.*?)\s*\x1b', strs))
    option.help = help_msg.strip()
    for op in op_va:
        dict[op[0]] = dict[op[0]] + ' ' + op[1] if op[0] in dict.keys() else op[1]
    option_value = list(dict.values())
    if option_value:
        option.name = option_value[0] if len(option_value) == 1 else option_value[1]
        option.value = option_value[0] if len(option_value) == 2 else ''
    return option


def find_msg(msg, data, exact):
    if (not exact) and re.search(msg, data):
        return True
    if exact and re.search(f'{msg}$', data):
        return True


# locate a setup option by given option name and default value
# setupoption = ['name','value'] e.g. ["Boot Type", "<UEFI Boot Type>"]
# Patten1: Only option name is highlighted, name should be specified, value not required
# Patten2: Only value is highlighted, both name and value need to be specified, e.g.["Boot Type", "<UEFI Boot Type>"]
help_msg = ''


def locate_option(key, setupoption, try_counts, delay=1, exact=True):
    data_before = ''
    name = setupoption[0]
    value = setupoption[1] if len(setupoption) == 2 else ''
    logging.info("Locate option: {0}".format(setupoption))
    data = get_data(delay + 1, cleanup=False)
    current = option(data)
    if find_msg(name, current.name, exact) and re.search(value, current.value):
        logging.info("Option found: {0}".format(setupoption))
        global help_msg
        help_msg = current.help
        return True
    else:
        send_key(key)
        while try_counts:
            data = get_data(delay, cleanup=False)
            if data == data_before and data != '':
                break
            current = option(data)
            if find_msg(name, current.name, exact) and re.search(value, current.value):
                logging.info("Option found: {0}".format(setupoption))
                help_msg = current.help
                return True
            data_before = data
            try_counts -= 1
            send_key(key)
        logging.info("Option not found: {0}".format(setupoption))


def boot_to_setup():
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    try_counts = 3
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        if not boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 400, SutConfig.Msg.POST_MESSAGE):
            BmcLib.power_cycle()
            try_counts -= 1
        else:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


def boot_to_boot_menu(data_save=False, reset=True, try_counts=2):
    if try_counts > 0:
        scroll = '(?:\x1b\[\d+;\d+H█)|(?:\x1b\[\d+;\d+H\*)'
        logging.info("SetUpLib: Boot to boot menu")
        if reset:
            if not BmcLib.init_sut():
                logging.info("SetUpLib: Rebooting SUT Failed.")
                return
            BmcLib.enable_serial_normal()
        if not wait_message(SutConfig.Msg.POST_MESSAGE):
            BmcLib.init_sut()
            BmcLib.enable_serial_normal()
            assert wait_message(SutConfig.Msg.POST_MESSAGE)
        clean_buffer()
        logging.info("Hot Key sent")
        send_key(Key.F11)
        start = time.time()
        datas = ''
        while True:
            data = get_data(1, cleanup=False)
            datas += data
            if re.search(SutConfig.Msg.ENTER_BOOTMENU, Sut.BIOS_COM.cleanup_data(data)):
                time.sleep(1)
                if data_save:
                    datas += get_data(2, cleanup=False)
                    if re.search(scroll, datas):
                        clean_buffer()
                        send_key(Key.UP)
                        data1 = get_data(2, cleanup=False)
                        clean_buffer()
                        send_key(Key.DOWN)
                        data2 = get_data(2, cleanup=False)
                        split_data = re.findall('\x1b\[\d+;\d+H([^\x1b]+)\x1b\[1m', data2)[0] if re.findall(
                            '\x1b\[\d+;\d+H([^\x1b]+)\x1b\[1m', data2) else ''
                        datas = data2.split(split_data)[0] + split_data + data1.split(split_data)[-1]

                    logging.debug(Sut.BIOS_COM.cleanup_data(datas))
                    return Sut.BIOS_COM.cleanup_data(datas)
                else:
                    logging.info("SetUpLib: Boot to boot menu successfully")
                    return True
            now = time.time()
            if now - start > 90:
                break
        logging.info('Boot to bootmenu failed')
        if reset:
            return boot_to_boot_menu(data_save, reset, try_counts - 1)
        else:
            return boot_to_boot_menu(data_save, reset, 0)
    return ''


def continue_to_setup():
    logging.info("SetUpLib: Continue boot to setup main page")
    if not boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


# boot to setup,boot menu,pxe without reset
def boot_with_hotkey_only(key, msg, timeout=250, hotkey_prompt="Press Del go to Setup Utilityasda",
                          pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, password=PwdLib.PW.DEFAULT_PW):
    setup_pw_msg = SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT
    setup_pw = PwdLib.PW.DEFAULT_PW
    count = 0
    psw = False
    stop_sign = False
    last = b''
    start_time = time.time()
    logging.debug("boot_with_hotkey: Receiving data from SUT...")
    Sut.BIOS_COM.session.flushInput()
    while True:
        try:
            if Sut.BIOS_COM.session.in_waiting:
                if count == 1 and not stop_sign:
                    time.sleep(0.01)
                    send_key(key)
                data = Sut.BIOS_COM.session.read(1024)
                last2data = last + data
                last2data = Sut.BIOS_COM.cleanup_data(last2data.decode("utf-8", errors='ignore'), False)
                Sut.BIOS_COM.cleanup_data(data.decode("utf-8", errors='ignore'))
                if Sut.BIOS_COM.find_msg(hotkey_prompt, last2data):
                    Sut.BIOS_COM.send_keys(key)
                    if count == 0:
                        logging.info("Hot Key sent")
                    count = 1
                if Sut.BIOS_COM.find_msg(msg, last2data):
                    stop_sign = True
                    if psw == True:
                        return [True, True]
                    else:
                        return True
                if not psw:
                    if Sut.BIOS_COM.find_msg(pw_prompt, last2data):
                        stop_sign = True
                        time.sleep(1)
                        send_data_enter(password)
                        logging.info(f"Send password: {password}")
                        psw = True
                if pw_prompt != setup_pw_msg:
                    if Sut.BIOS_COM.find_msg(setup_pw_msg, last2data):
                        stop_sign = True
                        time.sleep(1)
                        send_data_enter(setup_pw)
                        logging.info(f"Send Setup password: {password}")
                last = data
        except Exception as e:
            logging.error(e)
            logging.debug("boot_with_hotkey: Please check whether COM port is in use.")
            break

        if Sut.BIOS_COM.is_timeout(start_time, timeout):
            if count == 1:
                logging.info('Hot Key sent,but did not find confirm msg')
            else:
                logging.info('{0} not found'.format(hotkey_prompt))
            return


# reset and boot to setup,boot menu,pxe
def boot_with_hotkey(key, msg, timeout, hotkey_prompt):
    if not BmcLib.init_sut():
        return
    try_counts = 3
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        if not boot_with_hotkey_only(key, msg, timeout, hotkey_prompt):
            # logging.info("{0} not found".format(msg))
            BmcLib.power_cycle()
            try_counts -= 1
        else:
            logging.info("Boot with hotkey successfully.")
            return True

    logging.info("Boot with hotkey fail.")
    return


def boot_to_page(page_name):
    logging.info("SetUpLib: Move to specified setup page")
    if page_name == SutConfig.Msg.PAGE_ALL[0]:
        ES = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}"
        patten = f'(?:\[0m\x1b\[34m\x1b\[47m\x1b\[\d+;\d+H{page_name}|{page_name}{ES})'
        try_counts = 12
        clean_buffer()
        send_key(Key.RIGHT)
        while try_counts:
            data = get_data(2, cleanup=False)
            if re.search(patten, data):
                logging.info("Option found: {0}".format(page_name))
                return True
            try_counts -= 1
            Sut.BIOS_COM.send_keys(Key.RIGHT)
        logging.info("Option not found: {0}".format(page_name))
    else:
        if not locate_option(Key.RIGHT, [page_name], 12, 2):
            logging.info("SetUpLib: Specified setup page not found.")
            return
        logging.info("SetUpLib: Specified setup page found.")
        return True


# Continue boot to specific page in bios configuration without a force reset, assume reset is done in previous step
def continue_to_page(page_name):
    if not continue_to_setup():
        return
    logging.info("SetUpLib: Move to specified setup page")
    if not locate_option(Key.RIGHT, [page_name], 12):
        logging.info("SetUpLib: Specified setup page not found.")
        return
    logging.info("SetUpLib: Specified setup page found.")
    return True


# Verify supported values of a setup option, can be called after locate_setup_option()
# valuses: string, e.g: DisabledAutoLowMediumHighManual
def verify_supported_values(values):
    send_key(Key.ENTER)
    if not wait_message(values, delay=7):
        logging.info("Supported values are not correct.")
        send_key(Key.ESC)
        return
    logging.info("Supported values are verified.")
    send_key(Key.ESC)
    return True


def boot_os_centos_legacy(change_boot_mode=True):
    if change_boot_mode:
        assert boot_to_setup()
        assert boot_to_page(SutConfig.Msg.PAGE_BOOT)
        assert select_option_value(Key.DOWN, [SutConfig.Msg.BOOT_MODE], Key.DOWN, "Legacy", 6)
        send_keys(Key.SAVE_RESET)
        time.sleep(5)
    if not boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 300, SutConfig.Msg.POST_MESSAGE):
        return
    if not select_boot_option(Key.DOWN, SutConfig.Msg.CENT_OS_Legacy, 12, 'CentOS'):
        return
    if not BmcLib.ping_sut():
        return
    logging.info("OS Boot Successed.")
    return True


# Boot to kylin os from boot manager
def boot_os_from_bm(os_type="linux"):
    if not boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 300, SutConfig.Msg.POST_MESSAGE):
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
    time.sleep(20)
    return True


# Boot to Internal Shell
def boot_to_shell():
    try:
        assert boot_to_boot_menu()
        assert select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 12,
                                  'UEFI Interactive Shell'), "Select Shell failed."
        time.sleep(10)
        logging.info("Shell Boot Successed.")
        return True
    except AssertionError as e:
        logging.error(e)
        logging.error("Shell Boot failed.")
        return


# Boot to DOS
def boot_to_dos():
    try:
        assert enable_legacy_boot()
        assert boot_to_boot_menu()
        assert select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 8, 'USB')
        assert wait_message("Start booting from USB device...|StartbootingfromUSBdevice...", 20,
                            readline=False), "Boot to DOS failed."
        time.sleep(5)
        logging.info("DOS Boot Successed.")
        return True
    except AssertionError as e:
        logging.error(e)
        logging.error("DOS Boot failed.")
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
    last = b''
    clean_data = ''
    psw = False
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
                    initial_data = Sut.BIOS_COM.session.read(1024)
                    data = last + initial_data
                    data = data.decode("utf-8", errors='ignore')
                    if cleanup:
                        clean_data = Sut.BIOS_COM.cleanup_data(data, save=False)
                        Sut.BIOS_COM.cleanup_data(initial_data.decode("utf-8", errors='ignore'))
                    else:
                        Sut.BIOS_COM.write_data2log(initial_data.decode("utf-8", errors='ignore'))
                    last = initial_data
            except Exception as e:
                logging.error(e)
                logging.error("is_msg_present_general: error in reading serial data")
            if cleanup:
                if Sut.BIOS_COM.find_msg(msg, clean_data):
                    write_datalog(data)
                    logging.debug("Message found.")
                    return True
            else:
                if Sut.BIOS_COM.find_msg(msg, data):
                    write_datalog(data)
                    logging.debug("Message found.")
                    return True
            if not psw:
                if pw_prompt and Sut.BIOS_COM.find_msg(pw_prompt, data):
                    time.sleep(1)
                    send_data_enter(pw)
                    logging.info("Send password...")
                    psw = True
        if Sut.BIOS_COM.is_timeout(start_time, delay):
            if delay > 5:
                write_datalog(data)
                data = ''
                logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
            break


# send key ENTER ,then judge whether find msg
def wait_message_enter(msg, delay=250, pw_prompt=None, pw=None, cleanup=True, readline=True):
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
                send_data_enter(pw)
                logging.info("Send password...")
            if Sut.BIOS_COM.find_msg(msg, data):
                write_datalog(data)
                logging.debug("Message found.")
                data = ''
                return True
        if Sut.BIOS_COM.is_timeout(start_time, delay):
            if delay > 5:
                write_datalog(data)
                data = ''
                logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
            break


# 读取缓存数据
def read_full_buffer(timeout=2):
    start_time = time.time()
    buffer = BytesIO()
    while True:
        size_in = Sut.BIOS_COM.session.in_waiting
        if size_in:
            try:
                buffer.write(Sut.BIOS_COM.session.read(size_in))
            except Exception as e:
                logging.error(e)
                logging.error("is_msg_present_general: error in reading serial data")
        if Sut.BIOS_COM.is_timeout(start_time, timeout):
            break
    return buffer.getvalue().decode(encoding='utf-8', errors='ignore')


# 返回限定时间内串口中所有数据
# delay:接收数据的时间
# key:如果不为None，则会先执行按键然后接收数据
# cleanup:是否清洗数据
# limit_time: True:强制接收delay秒内所有数据;False:限定时间内如果没有新的数据则停止接收
def get_data(delay=10, key=None, cleanup=True, scroll=False):
    keep_scroll = '(?:\x1b\[\d+;\d+H█\x1b\[\d+;\d+H░)|(?:\x1b\[\d+;\d+H\*\x1b\[\d+;\d+H\+)'
    if key is not None:
        send_key(key)
    data = read_full_buffer(delay)
    if scroll and re.search(f'{keep_scroll}', data):
        send_key(Key.PAGE_DOWN)
        data += read_full_buffer(delay)
    write_datalog(data)
    if cleanup:
        data = Sut.BIOS_COM.cleanup_data(data)
    else:
        Sut.BIOS_COM.write_data2log(data)
    return data


# close serial session
def close_session():
    return Sut.BIOS_COM.close_session()


# open serial session
def open_session():
    return Sut.BIOS_COM.open_session()


# Match a list of strings from serial port
def wait_strings(msg_list, delay=10):
    return Sut.BIOS_COM.wait_messages(msg_list, delay)


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
        time.sleep(0.5)
        return True
    except Exception as err:
        logging.debug(err)


# select a boot option in boot manager
# optionname: string, name of setup option
def select_boot_option(key, optionname, try_counts, confirm_msg, first_option=None):
    counts = try_counts
    es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
    patten = es + f'(?:{optionname})' + es + r"\x1B\[44m"
    patten_before = es + f'(?:{optionname})' + es + r"\x1B\[40m"
    round_sign = False
    while try_counts:
        data = get_data(1, cleanup=False)
        if re.search(patten, data):
            logging.info("Boot option found: {0}".format(optionname))
            send_key(Key.ENTER)
            if not boot_with_hotkey_only(Key.DEL, confirm_msg, 120):
                logging.info("Boot to option: {0} Failed".format(optionname))
                return
            logging.info("Boot to option: {0} successfully".format(optionname))
            return True
        elif re.search(patten_before, data):
            send_key(Key.UP)
            if wait_message(patten, 2, cleanup=False):
                logging.info("Boot option found: {0}".format(optionname))
                send_key(Key.ENTER)
                if not boot_with_hotkey_only(Key.DEL, confirm_msg, 120):
                    logging.info("Boot to option: {0} Failed".format(optionname))
                    return
                logging.info("Boot to option: {0} successfully".format(optionname))
                return True
        if re.findall('\x1b\[\d+;\d+H(.*?)\x1b\[1m\x1b\[37m\x1b\[44m?', data) == first_option:
            round_sign = True
            logging.info("Boot to option: {0} Failed".format(optionname))
            return
        if try_counts == counts - 1 and first_option is None:
            first_option = re.findall('\x1b\[\d+;\d+H(.*?)\x1b\[1m\x1b\[37m\x1b\[44m?', data)
        send_key(key)
        try_counts -= 1
    if try_counts == 0 and round_sign is False:
        return select_boot_option(key, optionname, counts, confirm_msg, first_option)
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
VALR = "(\w[\w -:/]*[\w\)+]*)"  # bios value name ruler


# get values of setup option,return a list of values
def get_value_list():
    all_patten = re.compile(f"{SEP}{VALR}")
    Sut.BIOS_COM.session.flushInput()
    Sut.BIOS_COM.send_keys_with_delay(Key.ENTER)
    tmpdata = Sut.BIOS_COM.session.readline().decode('utf-8', errors='ignore')
    # tmpdata = Sut.BIOS_COM.receive_data(Sut.BIOS_COM.session.in_waiting)+get_data(1,readline=False,cleanup=False)
    Sut.BIOS_COM.send_keys_with_delay(Key.ENTER)
    write_datalog(tmpdata)
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
    write_datalog(tmpdata)
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
        if k == key_cnt - 1:
            write_datalog(tmpdata)
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
def enter_menu_change_value(key, option_path, try_counts, save=False):
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
    if save:
        time.sleep(1)
        send_keys(Key.SAVE_RESET)
        time.sleep(3)
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
    BmcLib.change_bios_value(['BootMode:Legacy'])
    # assert boot_to_setup()
    # assert enter_menu_change_value(Key.DOWN,SutConfig.Sup.BOOT_LEGACY,18)
    # time.sleep(1)
    # send_keys(Key.SAVE_RESET)
    # time.sleep(5)
    return True


def disable_legacy_boot():
    BmcLib.change_bios_value(['BootMode:UEFI'])
    # assert boot_to_setup()
    # assert enter_menu_change_value(Key.DOWN,SutConfig.Sup.BOOT_UEFI,18)
    # time.sleep(1)
    # send_keys(Key.SAVE_RESET)
    # time.sleep(5)
    return True


def regex_char_handle(strs):
    """正则表达式特殊字符串非转义处理: 在每一个正则敏感字符前加'\'斜杠"""
    return re.sub(r"([$()*+?\[\\^|{}.])", r"\\\1", strs)


def get_shell_fs_num():
    send_data('Map')
    time.sleep(1)
    send_key(Key.ENTER)
    fs = []
    data = get_data(2).splitlines()
    for index in range(0, len(data)):
        if re.search('USB', data[index]):
            fs += re.findall('(FS\d+:) ', data[index - 1])
    if fs:
        num = ''
        for i in fs:
            send_data_enter(i)
            time.sleep(1)
            send_data_enter('ls')
            if SutConfig.Env.BIOS_FILE in get_data(3):
                num = i
                break
        return num
    else:
        return ''


def get_linux_usb_dev():
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
    return mount_path


def check_grey_out_option(options, option_path, all_path=False):
    assert boot_to_page(SutConfig.Msg.PAGE_MAIN)
    datas = ''
    if all_path:
        trycounts = 12
        while trycounts:
            clean_buffer()
            data = get_data(3, Key.RIGHT, cleanup=False)
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
                data = get_data(2, cleanup=False)
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
            data = get_data(3, cleanup=False)
            datas += data
    SEP = '(?:\x1b\[\d+;\d+H)'
    HLP = "(?:\x1b\[\d+m){1}"
    if all(not re.search(f'\x1b\[3[47]m\x1b\[47m{SEP}{i}[\w\s\[\]()<>]*{SEP}*[\w\s\[\]()<>]*{HLP}', datas) for i in
           options):
        logging.info('All options grey out')
        return True
    else:
        for option in options:
            if not re.search(option, datas):
                print(f'---------------{option}')
            if re.search(f'\x1b\[3[47]m\x1b\[47m{SEP}{option}[\w\s\[\]()<>]*{SEP}*[\w\s\[\]()<>]*{HLP}', datas):
                logging.info(f'"{option}" not grey out')
            else:
                print(f'{option}灰显')
        return


def get_all_option_value():
    """
    获取SetUp下所有选项及对应的值
    """
    HLP = "(?:\x1b\[\d+m){3,}"
    SEP = "(?:\x1b\[\d+;\d+H){1}"
    all_pattern = f'(?:►|>)({HLP}{SEP}\w.+?\s*)\x1B'
    hlp_pattern = f'{HLP}{SEP}(\w.*?\w)$'
    remove_options = SutConfig.Upd.REMOVE_OPTIONS
    value = "(?:\w[\w -:/]*[\w\)+]*)"
    option_pattern = f'<{value}>\s\s+\w[\w \-/]*?\s\s+|\[[\da-fA-F]+\]\s\s+\w[\w \-/]*?\s\s+'
    options = []

    def get_all_data():
        keep_scroll = '(?:\x1b\[\d+;\d+H█\x1b\[\d+;\d+H░)|(?:\x1b\[\d+;\d+H\*\x1b\[\d+;\d+H\+)'
        data = ''
        data += get_data(2, cleanup=False)
        if re.search(f'{keep_scroll}', data):
            send_key(Key.PAGE_DOWN)
            data += get_data(2, cleanup=False)
            send_key(Key.PAGE_UP)
            clean_buffer()
        return data

    def get_menu(data):
        menu = []
        menu_first = []
        for i in re.findall(all_pattern, data):
            menu.append(Sut.BIOS_COM.cleanup_data(i).strip())
            if re.search(hlp_pattern, i):
                menu_first.append(Sut.BIOS_COM.cleanup_data(i).strip())
        menu = [m for m in menu if m not in remove_options]
        menu_first = [m for m in menu_first if m not in remove_options]
        return menu, menu_first

    def keep_get_data(menu, first_menu_name, options, count=0):
        if menu:
            count += 1
            for name in menu:
                if name not in first_menu_name:
                    enter_menu_change_value(Key.DOWN, [regex_char_handle(name)], 18)
                else:
                    send_key(Key.ENTER)
                data = get_all_data()
                options += re.findall(option_pattern, Sut.BIOS_COM.cleanup_data(data))
                second_menu, second_menu_name = get_menu(data)
                keep_get_data(second_menu, second_menu_name, options, count - 1)
                for i in range(count):
                    time.sleep(1)
                    send_key(Key.ESC)

    assert boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    time.sleep(1)
    send_keys(Key.CONTROL_F11)
    assert boot_to_page(SutConfig.Msg.PAGE_ALL[-1])
    for i in SutConfig.Msg.PAGE_ALL:
        back_to_setup_toppage()
        clean_buffer()
        send_key(Key.RIGHT)
        data = get_all_data()
        options += re.findall(option_pattern, Sut.BIOS_COM.cleanup_data(data))
        first_menu, first_menu_name = get_menu(data)
        keep_get_data(first_menu, first_menu_name, options)
    return [i.replace(' ', '') for i in options]


def smbios_to_dict(smbios: str):
    sm_split = re.findall("\nHandle \w+, DMI type (\d+).+?\n([\w ]*)\n([\S\s]+?)(?=\nHandle \w+, DMI type|$)",
                          smbios)
    if not sm_split:
        logging.error("Invalid SMBIOS data")
        return
    smbios_all = {}
    for sm in sm_split:
        type_n = sm[0].strip()
        name = sm[1].strip()
        data = sm[2].strip()

        data = re.sub("\n\t\t", " ", data)
        data = re.sub("\t", "", data)

        data_find = re.findall("(.+?):\s*(.+)", data)
        # print(data_find)
        handle = {"Handle Name": name}
        data_dict = {k[0].strip(): k[1].strip() for k in data_find}
        handle.update(data_dict)
        type_title = f"type{type_n}"
        if type_title not in smbios_all:
            smbios_all[type_title] = []
        if not smbios_all[type_title]:
            smbios_all[type_title] = [handle]
        else:
            smbios_all[type_title].append(handle)
    return smbios_all


def info_dict():
    """
    SetUp下各种信息(CPU信息,内存信息)转换字典
    返回值:字典组成的列表(如两个CPU则每个CPU信息组成一个字典)

    [{ 'CPU Count': '1','CPU Manufacturer': 'Hygon','CPU Version': 'Hygon C86 7280 32-core Processor'},
     {'CPU Version': 'Not Installed'}]
    """
    dict_list = [{}]
    datas = ''
    time.sleep(1)
    send_key(Key.ENTER)
    datas += get_data(2, cleanup=False) + '\n'
    keep_scroll = '(?:\x1b\[\d+;\d+H█\x1b\[\d+;\d+H░)|(?:\x1b\[\d+;\d+H\*\x1b\[\d+;\d+H\+)'  # 翻页标志
    if re.search(keep_scroll, datas):
        try_counts = 15
        while try_counts:
            send_key(Key.PAGE_DOWN)
            data = get_data(2, cleanup=False) + '\n'
            datas += data + '\n'
            if not re.search(keep_scroll, data):
                break
            try_counts -= 1
    for data in datas.splitlines():
        line = sorted(list(set(re.findall('\x1b\[(\d+);\d+H', data))))
        current_row = '0'
        data_dict = dict_list[-1]
        for i in line:
            a = re.findall(f'\x1b\[{i};(\d+)H([\w\-(),:/.\[\]][\w\s\-(),:/.\[\]]+)', data)
            if len(a) == 2:
                if a[0][1].strip() in data_dict.keys():
                    dict_list.append({})
                    data_dict = dict_list[-1]
                data_dict[a[0][1].strip()] = a[1][1].strip()
                current_row = a[1][0]
            elif len(a) == 1:
                if current_row == '0' and data_dict:
                    data_dict[list(data_dict.keys())[-1]] = list(data_dict.values())[-1] + ' ' + a[0][1].strip()
                if a[0][0] == current_row:
                    data_dict[list(data_dict.keys())[-1]] = list(data_dict.values())[-1] + ' ' + a[0][1].strip()
                current_row = a[0][0]
    return dict_list


def change_date_time(datetuple, save=False):
    year, month, day, hour, minute, second = datetuple
    send_keys([Key.DOWN, Key.RIGHT, Key.RIGHT, Key.ENTER])
    time.sleep(1)
    send_data_enter('00')
    send_keys([Key.UP])
    for date in [month, day, year, hour, minute, second]:
        time.sleep(1)
        send_key(Key.ENTER)
        if date:
            time.sleep(1)
            send_data(date)
        time.sleep(1)
        send_key(Key.ENTER)
        time.sleep(1)
        if date == year:
            send_key(Key.DOWN)
            time.sleep(2)
    send_key(Key.ESC)
    clean_buffer()
    send_key(Key.ENTER)
    data = re.findall(r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})]\s*\[(\d+):\s*System Time.*([0-9]{2}):',
                      get_data(2))
    if data:
        data = data[0]
        if data[0] == month and data[1] == day and data[2] == year and data[3] == hour and data[4] == minute:
            logging.info('日期修改成功')
    send_key(Key.ESC)
    time.sleep(1)
    if save:
        send_keys(Key.SAVE_RESET)
        time.sleep(5)
