import re
import logging
from batf import var
from typing import Union
from batf.SolTerm import SolTerm
from SPR4P.Config import SutConfig
from SPR4P.Config.PlatConfig import Key, Msg
from SPR4P.BaseLib.SetUpLib import option_check
from SPR4P.BaseLib import BmcLib


SOL = SolTerm(SutConfig.Env.BMC_IP, SutConfig.Env.BMC_USER, SutConfig.Env.BMC_PASSWORD)


def set_serial_log():
    SOL.set_logfile(var.get('serial_log'))
    return True


def close_sol():
    if SOL.is_sol_active():
        SOL.sol_session.close()
    return True


def send_key(key):
    if SOL.is_sol_active():
        SOL.send_a_key(key)
    return True


def send_keys(keys, delay=1):
    if SOL.is_sol_active():
        SOL.send_multi_keys(keys, delay)
    return True


def send_data(data, enter=False):
    SOL.send_data(data)
    if enter:
        send_key(Key.ENTER)
    return True


def boot_with_hotkey(key, confirm: str, prompt=Msg.HOTKEY_PROMPT_DEL, password=Msg.BIOS_PASSWORD, close=True, reboot=True):
    pw_prompt = Msg.PW_PROMPT
    try:
        if reboot:
            BmcLib.force_reset()
        set_serial_log()
        assert SOL.open_sol("ipmcset -t sol -d activate -v 1 0")
        return SOL.boot_with_hotkey(key, confirm, SutConfig.Env.BOOT_DELAY, prompt, pw_prompt, password, SutConfig.Env.HOTKEY_RETRY)
    finally:
        if close:
            close_sol()


def locate_front_page_icon(icon: str):
    logging.info(f'Locating front page icon: {icon}')
    set_serial_log()
    icon_pattern = "(/ [a-zA-Z ]+ /)"
    send_key(Key.DOWN)
    for i in range(3):
        strs = SOL.read_full_buffer()
        strs = SOL.drop_style(strs)
        current_icon = re.findall(icon_pattern, strs)
        if current_icon and re.search(icon, current_icon[-1]):
            logging.info(f'Locate success: {icon}')
            return True
        send_key(Key.RIGHT)
    send_key(Key.DOWN)
    for i in range(3):
        strs = SOL.read_full_buffer()
        strs = SOL.drop_style(strs)
        current_icon = re.findall(icon_pattern, strs)
        if current_icon and re.search(icon, current_icon[-1]):
            logging.info(f'Locate success: {icon}')
            return True
        send_key(Key.RIGHT)
    logging.error(f'Locate icon fail:  {icon}')


def locate_option(setupoption: Union[str, list], key=Key.DOWN, try_counts: int = 40, integer=False, span=None, order=1, exact=False):
    if isinstance(setupoption, str):
        name, value = setupoption, None
    else:
        setupoption = option_check(setupoption, integer)
        name, value = setupoption
    return SOL.locate_option(key, name, value, try_counts, span=span, order=order, exact=exact)
