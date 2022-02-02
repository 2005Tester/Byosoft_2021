import logging
import time
from batf import SerialLib
from batf.SutInit import Sut
# from batf.Common import SutSerial
from InspurStorage.BaseLib import BmcLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
import subprocess
import re
from batf.Common import SutSerial



# Send a single key, e.g. ENTER, DOWN, UP发送一次按键
def send_key(key):
    Sut.BIOS_COM.send_keys(key)



# send keys with default delay = 1s, e.g. [F10, Y]间隔一秒，依次发送按键
def send_keys(keys, delay=1):
    SerialLib.send_keys_with_delay(Sut.BIOS_COM, keys, delay)



# send data to BIOS serial port向串口发送数据
def send_data(data):
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(1)



# send a string and enter to BIOS serial port向串口发送数据并延迟一秒后按确定
def send_data_enter(data):
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(2)
    send_key(Key.ENTER)



# verify information like CPU, memory in one setup page, option name is highlighted确认setup界面的信息选项名字高亮
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
    if type(option_path)==str:
        option_path=[option_path]
    logging.info("Go to setup menu:{0}".format(option_path))
    for option in option_path:
        if option in SutConfig.Msg.PAGE_ALL:
            assert back_to_setup_toppage()
            assert boot_to_page(option)
        else:
            logging.info("Locate menu: {0}".format(option))
            if not locate_option(key, [option], try_counts):
                if not locate_option(Key.UP, [option], try_counts): #修复当要找的分区在最上面，导致找不到的问题
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
def locate_option( key, setupoption, try_counts, delay=1,readline=False):
    ES = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}"
    if len(setupoption) == 1:
        if '|' in setupoption[0]:
            patten = setupoption[0].split('|')[0] + ES + '|' + setupoption[0].split('|')[1] + ES
        else:
            if '    ' in setupoption[0]:
                option=setupoption[0].split('    ')
                patten=option[0]+ES+'.*'+option[1]+ES
            else:
                patten = setupoption[0] + ES

    elif len(setupoption) == 2:
        patten = ES + "{0}".format(setupoption[1]) + ES + "\s+" + ES + "\s+" + ES + "{0}".format(setupoption[0])

    else:
        logging.info("Incorrect format of parameter: setupoption, should be list")
        return
    logging.info("Locate option: {0}".format(setupoption))
    # self.receive_data(512)
    while try_counts:
        if wait_message(patten, delay, cleanup=False,readline=readline):
            logging.info("Option found: {0}".format(setupoption))
            return True
        try_counts -= 1
        Sut.BIOS_COM.send_keys(key)
    logging.info("Option not found: {0}".format(setupoption))



def reboot():
    send_data('root')
    time.sleep(0.5)
    send_key(Key.ENTER)
    time.sleep(0.5)
    send_data('Byosoft@123')
    time.sleep(0.5)
    send_key(Key.ENTER)
    time.sleep(0.5)
    send_data_enter('reboot')
    time.sleep(1)
    send_key(Key.CTRL_ALT_DELETE)



def boot_to_setup():
    logging.info("SetUpLib: Boot to setup main page")
    reboot()
    close_session()
    time.sleep(0.5)
    open_session()
    try_counts = 3
    while try_counts:
        logging.info("Waiting for Hotkey message found...")
        if not boot_with_hotkey_only(Key.DEL,SutConfig.Msg.PAGE_MAIN, 300, SutConfig.Msg.POST_MESSAGE):
            logging.info('Boot to setup main page fail')
            reboot()
            try_counts-=1
        else:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True



def continue_to_setup():
    logging.info("SetUpLib: Continue boot to setup main page")
    if not boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 300):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True



def boot_with_hotkey_only(key, msg, timeout=150, hotkey_prompt="Press Del go to Setup Utility", pw_prompt="Press F2", password="Admin@9009"):
    count=0
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
                    count=1
                    logging.info("Hot Key sent")
                if Sut.BIOS_COM.find_msg(pw_prompt, data):
                    Sut.BIOS_COM.send_data(password)
                    Sut.BIOS_COM.send_data(chr(0x0D))  # Send Enter
                    logging.info("Send password...")
                if Sut.BIOS_COM.find_msg(msg, data):
                    return True
        except Exception as e:
            logging.error(e)
            logging.debug("boot_with_hotkey: Please check whether COM port is in use.")
            break

        if Sut.BIOS_COM.is_timeout(start_time, timeout):
            if count==1:
                logging.info('Hot Key sent,but did not find confirm msg')
            else:
                logging.info('{0} not found'.format(hotkey_prompt))
            break



def boot_with_hotkey(key, msg, timeout, hotkey_prompt):
    reboot()
    try_counts=3
    while try_counts:
        logging.info("Waiting for Hotkey message found...")
        if not boot_with_hotkey_only(key, msg, timeout, hotkey_prompt):
            reboot()
            try_counts-=1
        else:
            logging.info("Boot with hotkey successfully.")
            return True
    logging.info("Boot with hotkey fail.")
    return



def boot_to_page(page_name,try_counts=12):
    logging.info("SetUpLib: Move to specified setup page")
    if not locate_option(Key.RIGHT, [page_name], try_counts,1.5,readline=True):
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
    if not wait_message( values, delay=7):
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
    if not boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.HOTKEY_PROMPT_F11):
        return
    if not select_boot_option(Key.DOWN, SutConfig.Msg.CENT_OS_Legacy, 12, 'CentOS'):
        return
    if not BmcLib.ping_sut():
        return
    logging.info("OS Boot Successed.")
    return True



# Boot to kylin os from boot manager
def boot_os_from_bm():
    logging.info('Start booting to os')
    reboot()
    if not boot_with_hotkey_only(Key.F3, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        reboot()
        if not boot_with_hotkey_only(Key.F3, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            return
    if not select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 12,SutConfig.Msg.LINUX_OS_MSG):
        return
    if wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        send_data(SutConfig.Env.OS_PASSWORD)
        if wait_message_enter(SutConfig.Env.LOGIN_SUCCESS,10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    return True



def execute_command(command,delay=10):
    data=''
    send_key(Key.ENTER)
    send_data(command)
    time.sleep(1)
    send_key(Key.ENTER)
    command=re.sub('\|','\|',command)
    start=time.time()
    while True:
        data=data+re.sub(r'\[root.*\]# {}'.format(command),'',get_data(1))
        if re.search(r'\[root.*#',data):
            break
        now=time.time()
        if (now-start)>delay:
            break
    data=re.sub(command,'',data)
    data=re.sub(r'\[root.*#','',data).strip()
    return data



# Boot to Internal Shell
def boot_to_shell():
    try:
        assert boot_to_setup()
        assert boot_to_page(SutConfig.Msg.PAGE_BOOT)
        assert select_option_value(Key.DOWN, [SutConfig.Msg.INTERNAL_SHELL], Key.DOWN, "打开", 6)
        time.sleep(2)
        send_keys(Key.SAVE_RESET)
        logging.info("Enable Shell seccessed.")
        assert boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 100, SutConfig.Msg.HOTKEY_PROMPT_F11), "Press F11 failed."
        assert select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 12, 'Shell'), "Select Shell failed."
        assert wait_message("UEFI Interactive Shell v2.1", 20), "Boot Shell failed."
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
        assert boot_to_setup()
        assert boot_to_page(SutConfig.Msg.PAGE_BOOT)
        assert select_option_value(Key.DOWN, [SutConfig.Msg.BOOT_MODE], Key.DOWN, "Legacy", 6)
        time.sleep(2)
        send_keys(Key.SAVE_RESET)
        logging.info("Change boot mode to legacy seccessed.")
        assert boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.HOTKEY_PROMPT_F11)
        assert select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 8, 'USB')
        assert wait_message("Start booting from USB device...|StartbootingfromUSBdevice...", 20,readline=False), "Boot to DOS failed."
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



def wait_message(msg, delay=150, pw_prompt=None, pw=None, cleanup=True,readline=False):
    # return SerialLib.is_msg_present_clean(Sut.BIOS_COM,msg,delay,cleanup=cleanup)
    logging.debug("Waiting for:\"{0}\"".format(msg))
    start_time = time.time()
    data=''
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
                    initial_data= Sut.BIOS_COM.session.read(1024).decode("utf-8", errors='ignore')
                    data=data+initial_data
                    if cleanup:
                        clean_data =Sut.BIOS_COM.cleanup_data(data,save=False)
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



def wait_message_enter(msg, delay=150, pw_prompt=None, pw=None, cleanup=True,readline=True):
    # close_session()
    # time.sleep(0.5)
    # open_session()
    # time.sleep(0.5)
    # send_key(Key.ENTER)
    # return SerialLib.is_msg_present_clean(Sut.BIOS_COM, msg, delay, cleanup=cleanup)
    Sut.BIOS_COM.close_session()  # 关闭连接
    time.sleep(0.5)
    Sut.BIOS_COM.open_session()  # 打开链接
    time.sleep(0.5)
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



def get_data(delay=10,key=None,cleanup=True):
    start_time = time.time()
    if key != None:
        send_key(key)
    datas = []
    while True:
        if Sut.BIOS_COM.session.in_waiting:
            try:
                data = Sut.BIOS_COM.session.readline().decode("utf-8", errors='ignore')

                if cleanup:
                    data = Sut.BIOS_COM.cleanup_data(data)
                else:
                    Sut.BIOS_COM.write_data2log(data)
                datas.append(data)
            except Exception as e:
                logging.error(e)
                logging.error("is_msg_present_general: error in reading serial data")

        if Sut.BIOS_COM.is_timeout(start_time, delay):
            break
    return ''.join(datas)



def close_session():
    return Sut.BIOS_COM.close_session()



def open_session():
    return Sut.BIOS_COM.open_session()



# Match a list of strings from serial port
def wait_strings(msg_list, delay=10):
    return SerialLib.is_msg_list_present(Sut.BIOS_COM, msg_list, delay)



# used to navigate to setup top page,
def back_to_setup_toppage(msg='Setup Configuration|配置确认'):
    try:
        try_counts=10
        while try_counts:
            logging.info('Navigating to top page,')
            send_key(Key.ESC)
            if wait_message(msg, delay=2):
                time.sleep(0.5)
                send_key(Key.DISCARD_CHANGES)
                break

            try_counts-=1
        logging.info("Current is top page,")
        return True
    except Exception as err:
        logging.debug(err)



# select a boot option in boot manager
# optionname: string, name of setup option
def select_boot_option(key, optionname, try_counts, confirm_msg):
    es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
    optionname=optionname.replace('    ',' ')
    patten = es + optionname + es + r"\x1B\[44m"
    while try_counts:
        if wait_message( patten, 2, cleanup=False):
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
    if key_optionname==Key.DOWN:
        key=Key.UP
    elif key_optionname==Key.UP:
        key=Key.DOWN
    else:
        key=Key.DOWN
    if not locate_option(key_optionname, optionname, try_counts):
        if not locate_option(key, optionname, try_counts+1):
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
        if wait_message( patten, 2, cleanup=False):
            logging.info("value found: {0}".format(value))
            send_key(Key.ENTER)
            return True
        send_key(key_value)
        counts -= 1
    while try_counts:
        time.sleep(2)
        if wait_message( patten, 2, cleanup=False):
            logging.info("value found: {0}".format(value))
            send_key(Key.ENTER)
            return True
        send_key(Key.UP)
        try_counts -= 1
    logging.info("Value NOT found: {0}".format(value))



def choose_boot_option(key, optionname, try_counts):
    es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
    patten = es + optionname + es + r"\x1B\[44m"
    while try_counts:
        time.sleep(1)
        if SerialLib.is_msg_present(Sut.BIOS_COM, patten, 2, cleanup=False):
            logging.info("Boot option found: {0}".format(optionname))
            return True
        send_key(key)
        try_counts -= 1
    logging.info("Boot option NOT found: {0}".format(optionname))



def locate_value(value_str):
    SEP = "(?:\x1b\[\d+;\d+H){1}"  # value separator
    HLP = "(?:\x1b\[\d+m){3}"  # value hightlight ending flag, last appeared valid
    # VALR = "(\w[\w -/]*\w)"  # bios value name ruler
    VALR = "(\w[\w -/:]*[\w\)+])"  # bios value name ruler
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
        value_str0=value_str.split('|')[0]
        value_str1 = value_str.split('|')[1]
        if value_str0 in val_list:
            value_str=value_str0
        elif value_str1 in val_list:
            value_str = value_str1
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



def change_option_value(key_optionname, optionname,try_counts,value_str,delay=1):
    if key_optionname==Key.DOWN:
        key=Key.UP
    elif key_optionname==Key.UP:
        key=Key.DOWN
    else:
        key=Key.DOWN
    if not locate_option(key_optionname, optionname, try_counts,delay):
        if not locate_option(key, optionname, try_counts+1):
            time.sleep(0.5)
        else:
            time.sleep(0.5)
    else:
        time.sleep(0.5)
    if locate_value(value_str):
        time.sleep(0.5)
        send_key(Key.ENTER)
        time.sleep(0.5)
        return True
    else:
        logging.info("Value NOT found: {0}".format(value_str))



def locate_menu(key, option_path, try_counts):
    if type(option_path)==str:
        option_path=[option_path]
    logging.info("Go to setup menu:{0}".format(option_path))
    for option in option_path:
        if option in SutConfig.Msg.PAGE_ALL:
            assert back_to_setup_toppage()
            assert boot_to_page(option)
        else:
            logging.info("Locate menu: {0}".format(option))
            if not locate_option(key, [option], try_counts):
                if not locate_option(Key.UP, [option], try_counts+1): #修复当要找的分区在最上面，导致找不到的问题
                    logging.info("Not Found: {0}".format(option))
                    return
            if option!=option_path[-1]:
                send_keys(Key.ENTER)
    return True



def enter_menu_change_value(key, option_path, try_counts):
    num=0
    if type(option_path)==str:
        option_path=[option_path]
    for option in option_path:
        if option_path[num-1]!=option:
            if option in SutConfig.Msg.PAGE_ALL:
                assert back_to_setup_toppage()
                assert boot_to_page(option)
            elif type(option)==dict:
                if option_path.index(option)!=0:
                    if type(option_path[option_path.index(option)-1])!=dict:
                        assert change_option_value(key,list(option.keys()),try_counts,list(option.values())[0],2)
                    else:
                        assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
                else:
                    assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0],2)
            else:
                if not locate_option(key, [option], try_counts):
                    if not locate_option(Key.UP, [option], try_counts + 1):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                send_key(Key.ENTER)
        else:
            if num>=1:
                time.sleep(1)
                send_key(Key.ENTER)
            else:
                if option in SutConfig.Msg.PAGE_ALL:
                    assert back_to_setup_toppage()
                    assert boot_to_page(option)
                elif type(option) == dict:
                    if option_path.index(option) != 0:
                        if type(option_path[option_path.index(option) - 1]) != dict:
                            assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0],
                                                       2)
                        else:
                            assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
                    else:
                        assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0], 2)
                else:
                    if not locate_option(key, [option], try_counts):
                        if not locate_option(Key.UP, [option], try_counts + 1):
                            time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                    send_key(Key.ENTER)
        num+=1
    return True



def enter_menu_change_value_ignore(key, option_path, try_counts):
    num = 0
    if type(option_path) == str:
        option_path = [option_path]
    for option in option_path:
        if option_path[num - 1] != option:
            if option in SutConfig.Msg.PAGE_ALL:
                assert back_to_setup_toppage()
                assert boot_to_page(option)
            elif type(option) == dict:
                if option_path.index(option) != 0:
                    if type(option_path[option_path.index(option) - 1]) != dict:
                        assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0], 2)
                    else:
                        assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
                else:
                    assert change_option_value(key, list(option.keys()), try_counts, list(option.values())[0], 2)
            else:
                if not locate_option(key, [option], try_counts):
                    if not locate_option(Key.UP, [option], try_counts + 1):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                send_key(Key.ENTER)
        else:
            if num >= 1:
                time.sleep(1)
                send_key(Key.ENTER)
            else:
                if option in SutConfig.Msg.PAGE_ALL:
                    assert back_to_setup_toppage()
                    assert boot_to_page(option)
                elif type(option) == dict:
                    if option_path.index(option) != 0:
                        if type(option_path[option_path.index(option) - 1]) != dict:
                            change_option_value(key, list(option.keys()), try_counts, list(option.values())[0],
                                                       2)
                        else:
                            change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
                    else:
                        change_option_value(key, list(option.keys()), try_counts, list(option.values())[0], 2)
                else:
                    if not locate_option(key, [option], try_counts):
                        if not locate_option(Key.UP, [option], try_counts + 1):
                            time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                    send_key(Key.ENTER)
        num += 1
    return True





















