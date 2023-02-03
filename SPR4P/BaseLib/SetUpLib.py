import json
import logging
import re
import time
from typing import Union, List
from batf import SerialLib, MiscLib, var
from batf.SutInit import Sut
from SPR4P.Config.PlatConfig import Key, Msg
from SPR4P.Config import SutConfig
from SPR4P.BaseLib import BmcLib


# Send a single key, e.g. ENTER, DOWN, UP
def send_key(key, delay: Union[int, float] = 0):
    """发送一个热键到串口"""
    SerialLib.send_key(Sut.BIOS_COM, key)
    if delay:
        time.sleep(delay)
    return True


# send keys with default delay = 1s, e.g. [F10, Y]
def send_keys(keys, delay: Union[int, float] = 1):
    """发送多个热键到串口，每个按键间隔delay秒"""
    SerialLib.send_keys_with_delay(Sut.BIOS_COM, keys, delay)
    return True


# send test_data to BIOS serial port
def send_data(data: str):
    """发送字符串到串口，延迟1秒"""
    SerialLib.send_data(Sut.BIOS_COM, data)
    time.sleep(1)
    return True


# send a string and enter to BIOS serial port
def send_data_enter(data: str):
    """发送字符串到串口，延迟1秒并按下回车"""
    send_data(data)
    send_key(Key.ENTER)
    return True


def value_format(value: str, integer=False):
    """
    确认选项值的正确格式,按照类型给选项两边加上尖括号或方括号
    :param value:           选项值的字符串
    :param integer: True    -选值的值为整数型(选项值两边如果没有方括号[],则自动加上)
                    False   -选值的值为枚举型(选项值两边如果没有尖括号<>,则自动加上)
                    None    -选值的值为字符型(不做任何处理)
    :return:处理后的字符串
    """
    value = str(value)
    if integer is None:
        return value
    if integer is True:
        if value.startswith("\[") and value.endswith("\]"):
            return value
        if not value.startswith("\["):
            if value.startswith("["):
                value = value.strip("[")
            value = f"\[{value}"
        if not value.endswith("\]"):
            if value.startswith("]"):
                value = value.strip("]")
            value = f"{value}\]"
        return value
    if integer is False:
        if value.startswith("<") and value.endswith(">"):
            return value
        if not value.startswith("<"):
            value = f"<{value}"
        if not value.endswith(">"):
            value = f"{value}>"
        return value


def option_check(option, integer=False):
    """
    选项输入格式转换
    :param option:          如果选项为[option, value]格式,则根据参数integer自动检测value左右两边是否需要添加尖括号或方括号
    :param integer: True    -选值的值为整数型(选项值两边如果没有方括号[],则自动加上)
                    False   -选值的值为枚举型(选项值两边如果没有尖括号<>,则自动加上)
                    None    -选值的值为字符型(不做任何处理)
    :return: 经过处理后的格式: ["key", "<value>"] 或 ["key", "[value]"] 或 "key"
    """
    if isinstance(option, list) and len(option) == 2:
        return [option[0], value_format(option[1], integer)]
    if isinstance(option, list) and len(option) == 1:
        return [option[0], None]
    return option


# Match a list of strings from serial port
def wait_boot_msgs(msgs: Union[list, str], timeout: int = SutConfig.Env.BOOT_DELAY, pw_prompt=None, pw=None):
    """等待POST阶段串口的一个或多个字符串"""
    return Sut.BIOS_COM.is_msg_present_general(msgs, timeout, pw_prompt, pw)


# Match a specific patten from serial port, return true if match found, otherwise return None
def wait_msg(msg: str, timeout: int = 150):
    """等待串口的一个或多个字符串"""
    return SerialLib.is_msg_present_clean(Sut.BIOS_COM, msg, timeout)


# verify information like CPU, memory in one setup page, option name is highlighted
# infos: list e.g. ['BIOS Revision\s+5.[0-9]{2}']
def verify_info(info_list: list, trycounts: int = 40):
    """分别尝试按上键和下键，刷新串口输出，当指定字符串出现时，返回True"""
    if Sut.BIOS_COM.navigate_and_verify(Key.DOWN, info_list, trycounts):
        return True
    if Sut.BIOS_COM.navigate_and_verify(Key.UP, info_list, trycounts):
        return True


# Verify a few setup options and desired values, option value is highlighted
# options: list of setupoption and value e.g.[["IRQ Threshold", "7"],["RRQ Threshold", "7"]
#       or dict of setupoption and value e.g.{"IRQ Threshold": "7", "RRQ Threshold": "7"}
# if verify a single option, options = ["Name", "Value"] or [["Name", "Value"]]
def verify_options(options: Union[list, dict], key=Key.DOWN, trycounts: int = 40, integer=False, exact=False):
    """按热键刷新串口输出，验证一个或多个选项是否存在并且值匹配"""
    verified_items = []
    if isinstance(options, list) and isinstance(options[0], str):
        options = [options]
    elif isinstance(options, dict):
        options = [[k, v] for k, v in options.items()]
    for option in options:
        option = option_check(option, integer)
        name, value = option
        if Sut.BIOS_COM.locate_option(key, name, value, trycounts, exact=exact):
            verified_items.append(option)
        else:
            logging.info("Option: {0} not verified".format(option))
    if len(verified_items) == len(options):
        logging.info("All the setup options are verified")
        return True
    else:
        logging.info("{0} options not verified".format(len(options)-len(verified_items)))


# Enter setup menu
# Multi Level Menu: option_path=["PATH1", "PATH2", "PATH3"]
# Single Level Menu: option_path="PATH1" or ["PATH1"]
def enter_menu(option_path: Union[list, str], key=Key.DOWN, try_counts: int = 30, confirm_msg: str = ""):
    """按下热键，定位到一级或多级菜单，每个菜单定位成功后按回车进入"""
    if isinstance(option_path, str):
        option_path = [option_path]
    try:
        return Sut.BIOS_COM.enter_menu(key, option_path, try_counts, confirm_msg, timeout=30)
    except Exception as e:
        logging.error("Exception occur: {0}".format(e))


# locate a setup option by given option name and default value
# Case1: Both name and value is specified.                 setupoption = ["BootType", "<UEFI>"] or ["BootType", "UEFI"]
# Case2: Only name is specified, value is not cared.       setupoption = "BootType"
# Case3: Only have option, no value exist, such as a menu path.   setupoption = ["Socket Configuration"]
def locate_option(setupoption: Union[str, list], key=Key.DOWN, try_counts: int = 40, integer=False, span=None, order=1, exact=True, refresh=False):
    """
    定位单个Setup选项或菜单
    :param setupoption: 菜单/选项
                            - 菜单名/选项名: "BootType"
                            - 菜单和值: ["BootType", "UEFI"]
    :param key: 按键
    :param try_counts: 最大按键次数, 回到定位的起始点时会自动退出
    :param integer: 选项值的类型
                            - True 整数型 [Value]
                            - False 枚举型 <Value>
                            - None 字符型 Value
    :param span: 手动指定选项占几行, 不指定则自动解析
    :param order: 第几个选项, 有重复选项时可使用, 默认第1个
    :param exact: 是否完整匹配, 选择正则匹配使用search还是fullmatch
    :param refresh: 若当前页面串口输出会自刷新,则定位时做特别处理
    :return: True/False, 选项定位成功并且值匹配,返回True
    """
    if isinstance(setupoption, str):
        name, value = setupoption, None
    else:
        setupoption = option_check(setupoption, integer)
        name, value = setupoption
    delay = 0.8 if refresh else 0.5
    return Sut.BIOS_COM.locate_option(key, name, value, try_counts, span=span, order=order, exact=exact, delay=delay, refresh=refresh)


def boot_with_hotkey(key, msg: str, timeout: int = SutConfig.Env.BOOT_DELAY, password=Msg.BIOS_PASSWORD, prompt=Msg.HOTKEY_PROMPT_F6):
    """
    发送重启命令, 然后按下指定热键, 等待串口关键字, 验证是否能进入指定页面
    :param key: 热键
    :param msg: 确认按键是否成功
    :param timeout: 超时时间
    :param password: BIOS密码(如果password为None,则不会自动输入密码)
    :param prompt: 热键提示信息(如果prompt为None,则不会自动输入密码)
    :return: True/None
    """
    pw_prompt = Msg.PW_PROMPT
    if not BmcLib.force_reset():
        return
    if not Sut.BIOS_COM.boot_with_hotkey(key, msg, timeout, prompt, pw_prompt, password, retry=SutConfig.Env.HOTKEY_RETRY):
        return
    logging.info("Boot with hotkey successfully.")
    return True


def continue_boot_with_hotkey(key, msg: str, timeout: int = SutConfig.Env.BOOT_DELAY, password=Msg.BIOS_PASSWORD, prompt=Msg.HOTKEY_PROMPT_F6):
    """
    不发送重启命令, 按下指定热键, 等待串口关键字, 验证是否能进入指定页面
    :param key: 热键
    :param msg: 确认按键是否成功
    :param timeout: 超时时间
    :param password: BIOS密码(如果password为None,则不会自动输入密码)
    :param prompt: 热键提示信息(如果prompt为None,则不会自动输入密码)
    :return: True/None
    """
    pw_prompt = Msg.PW_PROMPT
    if not Sut.BIOS_COM.boot_with_hotkey(key, msg, timeout, prompt, pw_prompt, password, retry=SutConfig.Env.HOTKEY_RETRY):
        return
    logging.info("Boot with hotkey successfully.")
    return True


def boot_to_setup():
    """发送重启命令, 按下热键启动到BIOS Setup的Front Page页面"""
    logging.info("SetUpLib: Boot to setup main page")
    logging.info("SetUpLib: Rebooting SUT...")
    BmcLib.force_reset()
    logging.info("SetUpLib: Booting to setup")
    if not continue_boot_with_hotkey(Key.DEL, Msg.HOME_PAGE):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


def continue_to_setup():
    """不发送重启命令, 按下热键启动到BIOS Setup的Front Page页面"""
    logging.info("SetUpLib: Continue boot to setup main page")
    if not continue_boot_with_hotkey(Key.DEL, Msg.HOME_PAGE):
        logging.info("SetUpLib: Boot to setup failed.")
        return
    logging.info("SetUpLib: Boot to setup main page successfully")
    return True


# Continue Boot to boot manager without a force reset
def continue_to_bootmanager():
    """不发送重启命令, 按下热键启动到Boot Manager页面"""
    logging.info("SetUpLib: continue boot to bootmanager")
    msg = "Boot Manager Menu"
    if not continue_boot_with_hotkey(Key.F11, msg):
        logging.info("SetUpLib: Continue boot to bootmanager failed.")
        return
    logging.info("SetUpLib: Boot to bootmanager successful")
    return True


# Continue boot to password prompt by pressing hotkey without a force reset
def continue_to_pw_prompt(key=Key.DEL):
    """不发送重启命令, 按下热键启动到BIOS Setup输入密码页面"""
    logging.info("Continue boot to password prompt...")
    return Sut.BIOS_COM.boot_with_hotkey(key, Msg.PW_PROMPT, SutConfig.Env.BOOT_DELAY, Msg.HOTKEY_PROMPT_DEL, retry=SutConfig.Env.HOTKEY_RETRY)


# boot to password prompt by a hotkey
def boot_to_pw_prompt(key=Key.DEL):
    """发送重启命令, 按下热键启动到BIOS Setup输入密码页面"""
    logging.info("Boot to password prompt...")
    BmcLib.force_reset()
    return continue_to_pw_prompt(key)


def locate_front_page_icon(icon: str):
    """在BIOS Setup的Front Page页面, 定位到指定的图标处"""
    logging.info(f'Locating front page icon: {icon}')
    icon_pattern = "(/ [a-zA-Z ]+ /)"
    send_key(Key.DOWN)
    for i in range(3):
        strs = Sut.BIOS_COM.read_full_buffer()
        strs = Sut.BIOS_COM.drop_style(strs)
        current_icon = re.findall(icon_pattern, strs)
        if current_icon and re.search(icon, current_icon[-1]):
            logging.info(f'Locate success: {icon}')
            return True
        send_key(Key.RIGHT)
    send_key(Key.DOWN)
    for i in range(3):
        strs = Sut.BIOS_COM.read_full_buffer()
        strs = Sut.BIOS_COM.drop_style(strs)
        current_icon = re.findall(icon_pattern, strs)
        if current_icon and re.search(icon, current_icon[-1]):
            logging.info(f'Locate success: {icon}')
            return True
        send_key(Key.RIGHT)
    logging.error(f'Locate icon fail:  {icon}')


# Move from Setup main to BIOS Configuration inforamtion page
# OnStart: Setup main page, cursor on Continue icon
def move_to_bios_config():
    """从Front Page页面移动到BIOS Setup的首页"""
    logging.info('"Enter "Setup Utility" from the front page')
    if not locate_front_page_icon(Msg.SETUP_ICON):
        return
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.PAGE_INFO):
        logging.info("Boot to BIOS Configuration Failed")
        return
    logging.info("Boot to BIOS Configuration success")
    return True


# Boot to BIOS configuration information page
def boot_to_bios_config():
    """发送重启命令, 按下热键启动到BIOS Setup的首页"""
    if not boot_to_setup():
        return
    if not move_to_bios_config():
        return
    return True


# Continue Boot to BIOS configuration information page without a force reset
def continue_to_bios_config():
    """不发送重启命令, 按下热键启动到BIOS Setup的首页"""
    if not continue_to_setup():
        return
    if not move_to_bios_config():
        return
    return True


def back_to_setup_toppage(msg: str = 'Exit now', try_cnt=10):
    """返回到BIOS Setup的最上层页面"""
    logging.info('Navigating to top page...')
    SerialLib.clean_buffer(Sut.BIOS_COM)
    while try_cnt:
        send_key(Key.ESC)
        temp = Sut.BIOS_COM.read_full_buffer(delay=1)
        if re.search(msg, temp):
            send_key(Key.DISCARD_CHANGES)
            logging.info("Current on the top page")
            return True
        try_cnt -= 1


def switch_to_page(page_name: str, key=Key.RIGHT):
    """回到最上层页面，并切换到指定页面"""
    logging.info("Switch to specified setup page...")
    if not back_to_setup_toppage():
        return
    if not Sut.BIOS_COM.navigate_and_verify(key, [page_name], 7):
        logging.error("Specified setup page not found")
        return
    logging.info("Switch to specified setup page success")
    return True


def move_to_page(page_name: str):
    """从FrontPage的'Continue'移动到BIOS Setup的指定页面"""
    if not move_to_bios_config():
        return
    return switch_to_page(page_name)


def boot_to_page(page_name: str):
    """发送重启命令，按下热键启动到BIOS Setup指定页面"""
    if not boot_to_bios_config():
        return
    return switch_to_page(page_name)


def boot_to_page_full_debug(page_name: str, reboot=False):
    """当Serial Debug Message开启时，按一次Hotkey可能不起作用，需要多按几次"""
    hotkey_prompt = Msg.HOTKEY_PROMPT_DEL
    confirm = Msg.HOME_PAGE
    boot_time = SutConfig.Env.BOOT_FULL_DBG
    pw_prompt = Msg.PW_PROMPT
    password = Msg.BIOS_PASSWORD
    if reboot:
        BmcLib.force_reset()
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, confirm, boot_time, hotkey_prompt, pw_prompt, password, retry=5):
        return
    if not move_to_bios_config():
        return
    return switch_to_page(page_name)


# Continue boot to specific page in bios configuration without a force reset, assume reset is done in previous step
def continue_to_page(page_name: str):
    """不发送重启命令，按下热键启动到BIOS Setup指定页面"""
    if not continue_to_bios_config():
        return
    return switch_to_page(page_name)


def boot_to_bootmanager():
    """发送重启命令，按下热键启动到BIOS Boot Manager页面"""
    key = Key.F11
    msg = "Boot Manager Menu"
    return boot_with_hotkey(key, msg, timeout=SutConfig.Env.BOOT_DELAY)


# Switch to legacy mode
def enable_legacy_boot():
    """发送重启命令，启动到BIOS Setup Boot页面, 切换启动模式为Legacy Boot，保存重启"""
    logging.info("Check current boot mode.")
    if not boot_to_setup():
        return
    send_key(Key.DOWN)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, "Boot From File", delay=10):
        logging.info("Already in legacy boot mode.")
        return True
    logging.info("Switch to legacy boot mode")
    send_keys([Key.RIGHT, Key.RIGHT, Key.ENTER])
    if not switch_to_page(Msg.PAGE_BOOT):
        logging.info("Boot configuration page not found.")
        return
    if not locate_option(["Boot Type", "<UEFIBoot>"], Key.DOWN, 25):
        return
    logging.info("Change boot type to legacy mode")
    send_key(Key.F5)
    if not locate_option(["Boot Type", "<LegacyBoot>"], Key.DOWN, 25):
        logging.info("Failed to change boot type.")
        return
    logging.info("Save and reboot")
    send_keys([Key.F10, Key.Y], 5)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, 'Start of legacy boot'):
        logging.info("Not in legacy mode")
        return
    logging.info("Boot in legacy mode")
    return True


def disable_legacy_boot():
    """发送重启命令，启动到BIOS Setup Boot页面, 切换启动模式为UEFI Boot，保存重启"""
    logging.info("Check current boot mode.")
    if not boot_to_setup():
        return
    send_key(Key.DOWN)
    if SerialLib.is_msg_present(Sut.BIOS_COM, "Boot From File", delay=10):
        logging.info("UEFI boot mode detected.")
        return True
    else:
        logging.info("Legacy boot mode detected")
        send_key(Key.RIGHT)
    send_key(Key.ENTER)
    if not Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [Msg.PAGE_BOOT], 12):
        logging.info("Boot configuration page not found.")
        return
    if not locate_option(["Boot Type", "<LegacyBoot>"], Key.DOWN, 25):
        return
    logging.info("Change boot type to UEFI mode")
    send_key(Key.F6)
    if not locate_option(["Boot Type", "<UEFIBoot>"], Key.DOWN, 25):
        logging.info("Failed to change boot type.")
        return
    logging.info("Save and reboot")
    send_keys([Key.F10, Key.Y], 5)
    if not SerialLib.is_msg_not_present(Sut.BIOS_COM, 'Start of legacy boot', 'BIOS boot completed.'):
        logging.info("Not in UEFI mode")
        return
    logging.info("Boot in UEFI mode")
    return True


def boot_os_from_bm(os_name: str = Msg.BOOT_OPTION_OS):
    """发送重启命令, 按下热键启动到Boot Manager, 选择OS启动项，进入OS"""
    if not boot_to_bootmanager():
        return
    if not locate_option(os_name, refresh=True):
        return
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present_clean(Sut.BIOS_COM, msg=Msg.LINUX_GRUB, delay=60):
        return
    if MiscLib.ping_sut(SutConfig.Env.OS_IP, 120):
        logging.info("OS Boot Successful")
        return True


# Boot Suse from boot manager without any power action, e.g, used wth F10 + Y in Setup
def continue_to_os_from_bm(os_name: str = Msg.BOOT_OPTION_OS):
    """不发生重启命令, 按下热键启动到Boot Manager, 选择OS启动项, 进入OS"""
    if not continue_to_bootmanager():
        return
    if not enter_menu(os_name, Key.DOWN, 60, Msg.LINUX_GRUB):
        return
    logging.info("OS Boot Successful")
    return True


def move_option_in_bootmanager(boot_option, count: int = 6, key=Key.F6):
    """发送重启命令, 按下热键启动到Boot Manager, 按下热键调整启动项的顺序"""
    if not boot_to_bootmanager():
        return
    if not locate_option(boot_option, refresh=True):
        return
    send_keys([key] * count, delay=0.5)
    return True


def move_boot_option_in_setup(boot_option: str, count: int = 6, key=Key.F6):
    """发送重启命令, 按下热键启动到BIOS Boot页面，按下热键调整启动项的顺序"""
    logging.info("Move: {0} {1} times".format(boot_option, count))
    hdd_group = [Msg.MENU_BOOT_ORDER, Msg.MENU_HDD_BOOT]
    if not boot_to_page(Msg.PAGE_BOOT):
        return
    if not enter_menu(hdd_group, Key.UP, 25, Msg.MENU_HDD_BOOT):
        return
    if not locate_option(boot_option, Key.UP, 10):
        return
    logging.info("Move option up")
    send_keys([key] * count, delay=0.5)
    logging.info("Save and reboot.")
    send_keys([Key.F10, Key.Y])
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.LOGO_SHOW, delay=SutConfig.Env.BOOT_DELAY):
        return
    return True


def update_default_password():
    """发送重启命令，按下热键启动到BIOS Setup, 修改BIOS管理员密码为SutConfig中定义的密码"""
    logging.info("Change BIOS password to non-default.")
    if not BmcLib.force_reset():
        return
    if not Sut.BIOS_COM.boot_with_hotkey(Key.DEL, Msg.PW_PROMPT, SutConfig.Env.BOOT_DELAY, Msg.HOTKEY_PROMPT_DEL, retry=SutConfig.Env.HOTKEY_RETRY):
        return
    send_data_enter(Msg.BIOS_PW_DEFAULT)
    assert wait_msg(Msg.PRESS_ENTER_PROMPT, 15)
    send_key(Key.ENTER)
    if not SerialLib.is_msg_present_clean(Sut.BIOS_COM, Msg.HOME_PAGE):
        return
    move_to_page(Msg.PAGE_SECURITY)
    locate_option(Msg.SET_ADMIN_PW, Key.DOWN)
    send_key(Key.ENTER)
    send_data_enter(Msg.BIOS_PW_DEFAULT)
    send_data_enter(Msg.BIOS_PASSWORD)
    send_data_enter(Msg.BIOS_PASSWORD)
    if not SerialLib.is_msg_present_clean(Sut.BIOS_COM, "Changes have been saved"):
        return
    send_key(Key.ENTER)
    send_keys(Key.SAVE_RESET)
    wait_boot_msgs(Msg.LOGO_SHOW)
    Sut.BIOS_COM.set_password(Msg.BIOS_PASSWORD, Msg.PW_PROMPT)
    logging.info("Password changed to non-default successfully")
    return True


def get_option_value(option_patten: str, key=Key.DOWN, try_counts: int = 40, integer=False, order=1) -> str:
    """
    获取指定选项的值
    :param option_patten:   选项名字符串
    :param key:             定位选项的按键
    :param try_counts:      定位选项的按键次数上限
    :param integer: True    -选值的值为整数型(左右有方括号[])
                    False   -选值的值为枚举型(左右有尖括号<>)
                    None    -选值的值为字符型(获取两边没有[]或<>)
    :return: 返回当前选项的值
    """
    value_pattern = ".+"
    if integer is False:
        value_pattern = "([\x20-\x7E]+)"
    elif integer is True:
        value_pattern = "(\w+)"
    value_match = value_format(value_pattern, integer)
    value_str = Sut.BIOS_COM.get_option_value(option_patten, value_match, key, try_counts, order=order)
    if not value_str:
        raise TypeError(f"Value not found: {option_patten}")
    return value_str.strip()  # <value> 右侧箭头'>'单独占据一行时，导致Value以空格结尾


def get_option_help(option: str, key=Key.DOWN, counts: int = 40) -> str:
    """定位到指定选项，并返回其帮助信息"""
    if locate_option(setupoption=option, key=key, try_counts=counts):
        help_info = Sut.BIOS_COM.current.help
        help_info = re.sub(f"{option}[ -]*", "", help_info).strip()
        logging.info(f"Help message: {help_info}")
        return help_info


def get_all_options(key=Key.UP, counts: int = 40, span=None, refresh=False) -> dict:
    """获取当前页面的所有选项和Value，返回键值对字典"""
    delay = 0.95 if refresh else 0.5
    return Sut.BIOS_COM.get_all_options(key=key, counts=counts, span=span, refresh=refresh, delay=delay)


def load_custom_default():
    """发送重启命令，按下热键启动到BIOS Setup, 定位到 Load Custom Default选项，按回车并保存重启"""
    logging.info("Reset BIOS to Custom dafault")
    try:
        assert boot_to_page(Msg.PAGE_SAVE)
        assert locate_option(Msg.LOAD_CUSTOM_DEFAULT, Key.DOWN, 20)
        send_keys(Key.ENTER_SAVE_RESET)
        return True
    except Exception as e:
        logging.error('load custom default fail', e)


def back_to_front_page(highlight: str = Msg.HOME_PAGE):
    """返回到BIOS Setup的最上层页面，按ESC退出BIOS Setup, 回到Front Page页面的指定图标处"""
    if not back_to_setup_toppage():
        return
    send_key(Key.ESC)
    assert wait_msg("Exit now", 15)
    send_key(Key.Y)
    assert wait_msg(Msg.SETUP_ICON, 15)
    return locate_front_page_icon(highlight)


def load_default_in_setup(save: bool = False):
    """在BIOS Setup中，按下热键恢复默认"""
    send_key(Key.F9)
    if not wait_msg(Msg.LOAD_DEFAULT_PROMPT, timeout=3):
        logging.error("F9 response over 3s")
        return
    send_key(Key.F, delay=3)
    if not save:
        logging.info("Load default without save")
        return True
    logging.info(f'Load default with saving')
    send_keys([Key.F10, Key.Y], 3)
    return True


# auto locate to the option and change the value to target, need enter the menu page first
# value should not contain character of "<>" or "[]"
def set_option_value(option: str, value: str, key=Key.DOWN, loc_cnt: int = 40, save: bool = False, integer=False):
    """定位到指定选项，修改选项的值"""
    logging.info(f'Set {option} -> {value}')
    if not locate_option(option, key, loc_cnt, integer):
        return

    if integer:
        send_keys([Key.ENTER], delay=1)
        send_data(f"{value}")
        send_keys([Key.ENTER], delay=1)
        if get_option_value(option, Key.DOWN, try_counts=3, integer=True) != f"{value}":
            logging.error(f"Set value failed: {option} => {value}")
            return
    else:
        if not Sut.BIOS_COM.locate_value(value, try_limits=64):
            return
        send_key(Key.ENTER)

    if save:
        logging.info(f'Save configuration and reset')
        send_keys(Key.SAVE_RESET, 2)
        assert wait_msg(Msg.CPU_RSC_ALLOC)
    logging.info(f"Set value success: {option} => {value}")
    return True


# locate to the target option and get all support values
def get_all_values(option: str, key=Key.DOWN, loc_cnt: int = 40) -> Union[list, None]:
    """定位到指定选项，获取选项的所有可选值"""
    if not locate_option(option, key, loc_cnt):
        return
    val_list = Sut.BIOS_COM.get_value_list(try_limits=64)
    if not val_list:
        raise TypeError(f"Value list not found: {option}")
    return val_list


def boot_to_default_os(reset=True, uefi=True, timeout=SutConfig.Env.BOOT_DELAY, delay=0):
    """重启到默认系统,并抓取串口日志(启动失败时方便debug)"""
    if reset:
        BmcLib.force_reset()
        SerialLib.clean_buffer(Sut.BIOS_COM)
    if not wait_boot_msgs(Msg.BIOS_BOOT_COMPLETE, timeout):
        return
    os_ip = SutConfig.Env.OS_IP if uefi else SutConfig.Env.OS_IP_LEGACY
    if MiscLib.ping_sut(os_ip, 300):
        time.sleep(delay)
        return True


def save_without_exit():
    """切换到Boot页面，选择保存不重启，按回车确认"""
    if not switch_to_page(Msg.PAGE_SAVE):
        return
    if not locate_option(Msg.SAVE_WO_RESET):
        return
    send_key(Key.ENTER)
    if not wait_msg("Save Changes now", 5):
        return
    send_key(Key.ENTER, delay=1)
    if wait_msg(Msg.SAVE_WO_RESET, 15):
        logging.info("Save without exit success")
        return True


def save_with_exit():
    """切换到Boot页面，选择保存并重启退出，按回车确认"""
    if not switch_to_page(Msg.PAGE_SAVE):
        return
    if not locate_option(Msg.SAVE_W_RESET):
        return
    send_key(Key.ENTER)
    if not wait_msg("Save Changes and Exit now", 5):
        return
    send_key(Key.ENTER, delay=1)
    if wait_msg(Msg.CPU_RSC_ALLOC):
        logging.info("Save with exit success")
        return True


def get_main_info(key=Key.UP, counts: int = 40) -> dict:
    """获取main页面的所有选项和Value,因为页面在不停刷新,需要特殊处理"""
    name_overwrite = ["System Time", "System Date"]
    options = get_all_options(key, counts, refresh=True)
    main_options = {}
    for op_name, op_value in options.items():
        if any(ov in op_name for ov in name_overwrite):
            for name_ov in name_overwrite:
                if name_ov in op_name:
                    main_options[name_ov] = op_value
                    break
        else:
            main_options[op_name] = op_value
    logging.info(f"Main page info: \n{json.dumps(main_options, indent=4)}")
    return main_options


def check_grey_option(option: Union[str, list, dict], key=Key.DOWN, counts=40, refresh_keys: list = None, integer=False, span: int = None) -> bool:
    """
    检查某个选项在Setup界面下是否被置灰,并且支持获取置灰选项的值
    option:
            str  - 单个选项名,检查选项是否置灰,选项值忽略. 示例: "option1"
            list - 多个选项名,检查多个选项是否置灰,选项值忽略.  示例:["option1", "option2", ...]
            dict - 单个或多个选项名和选项值,检查选项置灰并且确认选项值匹配.    示例: {"option1":"value1", "option2":"value2", ...}
    refresh_keys:
            list    某些选项需要特殊按键操作,串口才会刷新置灰选项的数据: 示例: [ESC, ENTER] or [LEFT, RIGHT]
    return:
            bool    所有置灰选项都确认到,如果需要确认选项值,则选项值都匹配时,返回True, 否则为False
    """
    if isinstance(option, dict):
        option = {k: value_format(v, integer) for k, v in option.items()}
    return Sut.BIOS_COM.get_grey_option(option, key, counts, refresh_keys, span)


def get_current_option():
    """按某个键之后,获取当前高亮位置的选项名/菜单名"""
    serial_out = Sut.BIOS_COM.read_full_buffer(delay=1)
    current = Sut.BIOS_COM.option(serial_out)
    if current.name is None:
        logging.error("Error to parse current option name")
        return
    logging.info(f"Current option: {current.name}")
    return current.name


def get_post_log(reset=True, timeout=SutConfig.Env.BOOT_DELAY) -> str:
    """返回启动阶段的全部串口日志"""
    if reset:
        BmcLib.force_reset()
    post_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.BIOS_BOOT_COMPLETE, timeout, timeout)
    return post_log


def get_visiable_text(key=Key.ENTER):
    """
    先定位到某个页面,按下键盘,读取串口串口输出,并解析出setup中所有可见的文字,包括置灰和无法选中的部分.
    返回列表,每一行的文字作为列表的一个元素,按行编号从小到大排序.
    """
    send_key(key, delay=1)
    strs = Sut.BIOS_COM.read_full_buffer()
    options_rows = []
    if strs:
        lines = Sut.BIOS_COM._row_column_dict(strs, row_range=Sut.BIOS_COM.body_rows, col_range=Sut.BIOS_COM.body_columns)
        options_rows = list(lines.rows.values())
    return options_rows
