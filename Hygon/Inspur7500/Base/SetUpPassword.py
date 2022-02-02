import datetime
from typing import Set
import requests
import re
import os
import time
import logging
from Inspur7500.BaseLib import BmcLib, SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from batf.Report import stylelog



def _del_password(password):
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    BmcLib.enable_serial_normal()
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.DEL,SutConfig.Msg.PAGE_MAIN_CN, 150, SutConfig.Msg.HOTKEY_PROMPT_DEL_CN):
        time.sleep(2)
        SetUpLib.send_data(password)
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 15):
            logging.info('SetUp密码存在，准备进入SetUp删除密码')
            logging.info("SetUpLib: Boot to setup main page successfully")
        else:
            return
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
            logging.info('密码删除')
            time.sleep(1)
        else:
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        return True
    else:
        logging.info("SetUpLib: Boot to setup main page successfully")
        return True



# 设置密码测试，未设置管理员密码直接设置用户密码，设置失败测试
def password_security_001():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.LOC_USER_PSW,8)
    if SetUpLib.wait_message(SutConfig.Psw.ONLY_SET_USER_PSW,readline=True):
        logging.info('未设置管理员密码直接设置用户密码，提示先设置管理员密码')
        SetUpLib.send_key(Key.ENTER)
        return True
    else:
        return



# 设置密码长度测试，密码长度小于最少字符数，修改失败测试
def password_security_002():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Ad@002')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_LENGTH_NOT_ENOUGH, 5):
        logging.info('管理员密码长度小于最少字符数，设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@02')
    time.sleep(1)
    SetUpLib.send_data('Admin@02')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功，开始用户密码长度测试')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('管理员密码设置失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Us@02')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_LENGTH_NOT_ENOUGH, 5):
        logging.info('用户密码长度小于最少字符数，设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@02')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度等于最少字符数，修改成功测试(测试用密码'Ad3~`!@#','Us3$%^&*')
def password_security_003():
    assert _del_password('Admin@02')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Ad3~`!@#')
    time.sleep(1)
    SetUpLib.send_data('Ad3~`!@#')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码长度等于最少字符成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码长度等于最少字符失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Us3$%^&*')
    time.sleep(1)
    SetUpLib.send_data('Us3$%^&*')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码长度等于最少字符成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码长度等于最少字符失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Ad3~`!@#')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码长度为最少字符成功')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Ad3~`!@#')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试(测试用密码'Ad4()_+"-={}[]:;',"Us4'<>,.?/ ")
def password_security_004():
    assert _del_password('Ad3~`!@#')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Ad4()_+"-={}[]:;')
    time.sleep(1)
    SetUpLib.send_data('Ad4()_+"-={}[]:;')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码长度大于最少字符数，小于最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码长度大于最少字符数，小于最大字符数失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter("Us4'<>,.?/ ")
    time.sleep(1)
    SetUpLib.send_data("Us4'<>,.?/ ")
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码长度大于最少字符数，小于最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码长度大于最少字符数，小于最大字符数失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@04')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Ad4()_+"-={}[]:;')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码长度大于最少字符数，小于最大字符数成功')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Ad4()_+"-={}[]:;')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度最大字符数，修改成功测试(测试用密码'Adminadmin@byosoft05','Usersusers@byosoft05')
def password_security_005():
    assert _del_password('Ad4()_+"-={}[]:;')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Adminadmin@byosoft05')
    time.sleep(1)
    SetUpLib.send_data('Adminadmin@byosoft05')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码长度为最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码长度为最大字符数失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Usersusers@byosoft05')
    time.sleep(1)
    SetUpLib.send_data('Usersusers@byosoft05')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码长度为最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码长度为最大字符数失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('Admin@byosoft04')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Adminadmin@byosoft05')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码长度为最大字符数成功')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Adminadmin@byosoft05')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度超出最大字符数，修改失败测试(测试用密码'Adminadmin@byosoft060','Usersusers@byosofy060')
def password_security_006():

    assert _del_password('Adminadmin@byosoft05')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Adminadmin@byosoft060')
    time.sleep(1)
    SetUpLib.send_data('Adminadmin@byosoft060')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Usersusers@byosoft060')
    time.sleep(1)
    SetUpLib.send_data('Usersusers@byosoft060')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Adminadmin@byosoft05')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Adminadmin@byosoft06')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码长度超过最大字符数，密码仍为最大字符数')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Adminadmin@byosoft060')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码字符类型测试，只有1种字符类型密码测试(测试用密码'Admin@07')
def password_security_007():
    passwords = ['12345678', 'ABCDEFGH', 'abcdefgh', '~`! #$%^','&*()_-+=','{[}]\|";',"':,.<>?/@"]
    assert _del_password('Adminadmin@byosoft060')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置管理员密码只有一种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@07')
    time.sleep(1)
    SetUpLib.send_data('Admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功，开始用户密码字符类型测试')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置用户密码只有一种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@07')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码字符类型测试，2种字符类型密码测试(测试用密码Admin@08)
def password_security_008():
    passwords = ['ADMIN123', 'admin456', 'ADMINadm', 'ADMIN!@#', 'admin~`$', '12345%^&']
    assert _del_password('Admin@07')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置管理员密码只有2种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@08')
    time.sleep(1)
    SetUpLib.send_data('Admin@08')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功，开始用户密码字符类型测试')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置用户密码只有2种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@08')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码字符类型测试，3种字符类型密码测试(测试用密码'Admin@09')
def password_security_009():
    passwords = ['ADMin123', 'ADMin?/.', 'AD123<,>', 'ad123{[]']
    assert _del_password('Admin@08')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置管理员密码只有3种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@09')
    time.sleep(1)
    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功，开始用户密码字符类型测试')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置用户密码只有3种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@09')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码字符类型测试，4种字符类型密码测试
def password_security_010():
    assert _del_password('Admin@09')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码字符类型测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@10')
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码4种字符类型成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码4种字符类型失败')
        return

    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@10')
    time.sleep(1)
    SetUpLib.send_data('Users@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码4种字符类型成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码4种字符类型失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('Adminadmin10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码4种字符类型成功')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@10')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 输入错误密码3次内，提示报错，并可以再次输入测试；输错3次后不允许在输入密码测试；输入错误密码超出阈值测试(测试用密码'Admin@11')
def password_security_011():
    assert _del_password('Admin@10')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@11')
    time.sleep(1)
    SetUpLib.send_data('Admin@11')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('管理员密码设置失败')
        return

    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Adminadmin')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK):
        logging.info('密码第三次输错，屏幕被锁定')
        return True
    else:
        return



# 输入错误密码次数测试，阈值内连续输入错误密码后输入正确密码测试(测试用密码'Admin@11')
def password_security_012():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('第三次输入正确密码，成功进入setup')
        return True
    else:
        return



# 输入错误密码次数测试，超出阈值锁定输入界面，重启后不影响下一次登录(测试用密码'Admin@11')
def password_security_013():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Adminadm')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK, 5):
        logging.info('密码第三次输错，屏幕锁定')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('输入密码错误，超出阈值锁定输入界面，重启后不影响下一次登录')
        return True
    else:
        return



# 输入错误密码等待时间测试，超出阈值锁定时间测试,锁定时间结束，输入正确密码可以进入(测试用密码'Admin@11')
def password_security_014():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
        time.sleep(2)
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_LOCK_OPTION,10)
    time.sleep(1)
    SetUpLib.send_data_enter('60')
    time.sleep(1)
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 6)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('12345678')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('12345678')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('12345678')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LOCK_60S, 5):
        logging.info('密码第三次输错，需等待60秒')
        time.sleep(62)

    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Adminadm')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LOCK_60S):
        logging.info('密码输错三次，需等待60秒')
    else:
        return
    time.sleep(62)
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('锁定时间结束，输入正确密码成功进入setup')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_LOCK_OPTION,10)
    time.sleep(1)
    SetUpLib.send_data_enter('180')
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Adminadm')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LOCK_180S):
        logging.info('密码输错三次，需等待180秒')
        time.sleep(182)
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('输入正确密码成功进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('12345678')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('12345678')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('12345678')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LOCK_180S, 5):
        logging.info('密码第三次输错，需等待180秒')
        time.sleep(182)
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('输入正确密码成功进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@11')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS,5):
        logging.info('删除管理员密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 输入用户密码进入setup测试，进入setup不可以删除用户密码(测试用密码'Admin@15','Users@15')
def password_security_015():
    count=0
    assert _del_password('Admin@11')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@15')
    time.sleep(1)
    SetUpLib.send_data('Admin@15')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('管理员密码设置失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@15')
    time.sleep(1)
    SetUpLib.send_data('Users@15')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('用户密码设置失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('Users@15')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('用户密码进入setup')
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('User Login Type.*User',5,readline=True):
        logging.info('用户密码进入SetUp，用户登陆类型显示普通用户')
    else:
        stylelog.fail('用户密码进入SetUp，用户登录类型不是普通用户')
        count+=1
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SEL_LANG_CN],8):
        logging.info('用户密码进入SetUp，不能更改语言')
    else:
        stylelog.fail('用户密码进入SetUp，可以更改语言')
        count+=1
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED_CN)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SERVER_CONFIG_CN],8):
        logging.info('用户密码进入SetUp,不能进入服务管理')
    else:
        stylelog.fail('用户密码进入SetUp,可以进入服务管理')
        count+=1
    assert SetUpLib.boot_to_page(SutConfig.Msg.SHUTDOWN_SYSTEM_CN)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.BIOS_UPDATE_CN],3):
        logging.info('用户密码进入SetUp,不能更改BIOS固件更新参数')
    else:
        stylelog.fail('用户密码进入SetUp,可以更改BIOS固件更新参数')
        count+=1
    if not SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT_CN):
        logging.info('用户密码进入SetUp，不能更改用户等待时间')
    else:
        stylelog.fail('用户密码进入SetUp，可以更改用户等待时间')
        count+=1
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@15')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.USER_NOT_DEL_PSW, 5):
        logging.info('用户密码进入setup，用户权限无法删除用户密码')
        SetUpLib.send_key(Key.ENTER)

    else:
        count+=1
    if count==0:
        return True
    else:
        return



# 输入用户密码进入setup测试，进入setup可以修改用户密码(测试用密码'Users@16')
def password_security_016():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@15')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('用户密码进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@15')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@16')
    time.sleep(1)
    SetUpLib.send_data('Users@16')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS):
        logging.info('用户密码进入setup，修改用户密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    BmcLib.power_reset()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('Users@15')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Users@16')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('修改用户密码成功')
        return True
    else:
        return



# 密码不能明文显示，任意密码用*代替字符测试(测试用密码'Admin@15')
def password_security_017():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_data('Admin@15')
    data = SetUpLib.get_data(1, Key.ENTER)

    if '********' in data and 'Admin@15' not in data:
        logging.info('密码不是明文显示，而是用*代替')
        return True
    else:
        return



# 密码修改验证旧密码测试，输入错误旧密码，不能修改密码(测试用密码'Admin@15','Users@16')
def password_security_018():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_data('Admin@15')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        pass
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('管理员密码修改时，输入错误旧密码，无法修改密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('用户密码修改时，输入错误旧密码，无法修改密码')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    return True



# 密码修改验证新密码测试，新密码确认时，输入错误新密码，修改失败测试(测试用密码'Admin@15','Users@16')
def password_security_019():
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@15')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        pass
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@15')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@19')
    time.sleep(1)
    SetUpLib.send_data('Admin@18')
    if SetUpLib.wait_message_enter(SutConfig.Psw.NEW_OLD_PSW_DIFF, 5):
        logging.info('管理员密码修改，新密码确认时，输入错误新密码，修改失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@16')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@19')
    time.sleep(1)
    SetUpLib.send_data('Users@18')
    if SetUpLib.wait_message_enter(SutConfig.Psw.NEW_OLD_PSW_DIFF, 5):
        logging.info('用户密码修改，新密码确认时，输入错误新密码，修改失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@15')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS,5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    return True



# 历史密码5次范围内重复修改无效，超过5次后可以修改为5次前的密码测试(测试用密码'Admin@20','Users@20‘)
def password_security_020():
    assert _del_password('Admin@15')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码5次范围内重复无效测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@20')
    time.sleep(1)
    SetUpLib.send_data('Admin@20')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第一次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)

    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@20')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@001')
    time.sleep(1)
    SetUpLib.send_data('Admin@001')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第二次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@001')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@002')
    time.sleep(1)
    SetUpLib.send_data('Admin@002')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第三次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@002')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@003')
    time.sleep(1)
    SetUpLib.send_data('Admin@003')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第四次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@003')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@004')
    time.sleep(1)
    SetUpLib.send_data('Admin@004')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第五次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@004')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@20')
    time.sleep(1)
    SetUpLib.send_data('Admin@20')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PREVIOUS_5_PSW_SAME, 5):
        logging.info('修改第一次设置的管理员密码不成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@004')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@005')
    time.sleep(1)
    SetUpLib.send_data('Admin@005')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第六次管理员密码修改成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@005')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@20')
    time.sleep(1)
    SetUpLib.send_data('Admin@20')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('修改第一次设置的管理员密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('Admin@005')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Admin@20')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码5次范围内重复无效测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@20')
    time.sleep(1)
    SetUpLib.send_data('Users@20')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第一次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@20')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@001')
    time.sleep(1)
    SetUpLib.send_data('Users@001')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第二次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@001')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@002')
    time.sleep(1)
    SetUpLib.send_data('Users@002')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第三次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@002')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@003')
    time.sleep(1)
    SetUpLib.send_data('Users@003')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第四次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@003')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@004')
    time.sleep(1)
    SetUpLib.send_data('Users@004')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第五次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@004')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@20')
    time.sleep(1)
    SetUpLib.send_data('Users@20')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PREVIOUS_5_PSW_SAME, 5):
        logging.info('修改第一次设置的用户密码不成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@004')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@005')
    time.sleep(1)
    SetUpLib.send_data('Users@005')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第六次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@005')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@20')
    time.sleep(1)
    SetUpLib.send_data('Users@20')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('修改第一次设置用户密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)


    time.sleep(1)
    SetUpLib.send_data('Users@005')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Users@20')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@20')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        pass
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@20')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



# 开机密码测试，打开开机密码，进入系统需要输入开机密码测试(测试用密码'Admin@21','Users@21')
def password_security_021():
    assert _del_password('Admin@20')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@21')
    time.sleep(1)
    SetUpLib.send_data('Admin@21')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@21')
    time.sleep(1)
    SetUpLib.send_data('Users@21')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:

        return
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.POWER_ON_PSW_OPTION], 5, 'Enabled')
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    logging.info('开机密码打开，进入系统需要输入密码')
    time.sleep(5)
    SetUpLib.send_data('Admin@21')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.ENTER_BOOTMENU_CN,15):
        logging.info('进入启动菜单')
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.LINUX_OS,20,''),'开机密码打开，进入系统不需要输入密码'
    if BmcLib.ping_sut():
        logging.info('输入管理员密码成功进入系统')
    else:
        stylelog.fail('输入管理员密码，没有进入系统')
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    logging.info('开机密码打开，进入系统需要输入密码')
    time.sleep(5)
    SetUpLib.send_data('Users@21')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.ENTER_BOOTMENU_CN, 15):
        logging.info('进入启动菜单')
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 20, ''), '开机密码打开，进入系统不需要输入密码'
    if BmcLib.ping_sut():
        logging.info('输入用户密码成功进入系统')
    else:
        stylelog.fail('输入用户密码，没有进入系统')
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data_enter('Admin@21')
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN):
        pass
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.POWER_ON_PSW_OPTION],5, 'Disabled')
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 20, ''), '开机密码打开，进入系统仍需要输入密码'
    logging.info('开机密码关闭，进入系统不需要输入密码')
    if BmcLib.ping_sut():
        logging.info('成功进入系统')
    else:
        stylelog.fail('进入系统失败')
        return
    BmcLib.power_reset()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@21')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@21')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 10):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



def change_date_days(days):
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.DATE_TIME_CN], 6)
    SetUpLib.send_key(Key.ENTER)
    data = re.findall(r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})\]', SetUpLib.get_data(2))[0]
    day = data[1]
    month = data[0]
    year = data[2]
    now = datetime.date(int(year), int(month), int(day))
    delta = datetime.timedelta(days)
    n_date = now + delta
    n_year = n_date.strftime('%Y')
    n_month = n_date.strftime('%m')
    n_day = n_date.strftime('%d')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter(n_month)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter(n_day)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter(n_year)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    data = re.findall(r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})\]', SetUpLib.get_data(2))[0]
    if data[0] == n_month and data[1] == n_day and data[2] == n_year:
        time.sleep(1)
        logging.info('日期修改成功')
    else:
        stylelog.fail('日期修改失败')
        return



# 密码有效期
def password_security_022(password='Admin@22'):
    assert _del_password('Admin@21')
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@22')
    time.sleep(1)
    SetUpLib.send_data('Users@22')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码失败')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.SET_TIME_WEEK,15)
    change_date_days(days=6)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Users@22')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码有效期为7天，6天后用户密码没有失效')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Users@22')
    time.sleep(2)
    if not SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE,5):
        logging.info('设置密码有效期为7天，6天后用户密码SetUp下没有失效')
    else:
        stylelog.fail('设置密码有效期为7天，6天后用户密码SetUp下失效')
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(password)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码有效期为7天，6天后管理员密码没有失效')
    else:
        return

    change_date_days(days=1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后setup下管理员密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后setup下管理员密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('Users@22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后setup下用户密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后setup下用户密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@22')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后进入setup提示用户密码失效')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后进入setup没有提示用户密码失效')
        return

    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后进入setup提示管理员密码失效')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后进入setup没有提示管理员密码失效')
        return

    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.SET_TIME_MONTH,15)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    change_date_days(22)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@22')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码有效期为30天，29天后用户密码没有失效')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('USers@22')
    time.sleep(1)
    if not SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE,5):
        logging.info('设置密码有效期为30天，29天后用户密码SetUp下没有失效')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码有效期为30天，29天后管理员密码没有失效')
    else:
        return
    change_date_days(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后setup下管理员密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后setup下管理员密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('Users@22')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后setup下用户密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后setup下用户密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@22')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后进入setup提示用户密码失效')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后进入setup没有提示用户密码失效')
        return
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后进入setup提示管理员密码失效')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后进入setup没有提示管理员密码失效')
        return
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.SET_TIME_ALWAYS,15)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码有效期为无限期，30天后用户密码没有失效')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(password)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('设置密码有效期为无限期，30天后管理员密码没有失效')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    return True



def password_security_023():
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    BmcLib.enable_serial_normal()
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN_CN, 120, SutConfig.Msg.HOTKEY_PROMPT_DEL_CN):
        time.sleep(2)
        SetUpLib.send_data('Admin@22')
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 15):
            time.sleep(2)
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN,15):
                logging.info('SetUp密码存在，准备进入SetUp删除密码')
                logging.info("SetUpLib: Boot to setup main page successfully")
                assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_data('Admin@22')
                if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                else:
                    return
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
                    logging.info('密码删除')
                    time.sleep(1)
                else:
                    return
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
            else:
                return
        else:
            if SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW):
                logging.info('进入SetUp')
            else:
                return
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('Admin@22')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
                logging.info('密码删除')
                time.sleep(1)
            else:
                return
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
    else:
        logging.info("SetUpLib: Boot to setup main page successfully")

    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@23')
    time.sleep(1)
    SetUpLib.send_data('Admin@23')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.SET_TIME_ALWAYS,15)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN, 30):
        logging.info('输入密码时按ESC没有跳过密码启动')
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@23')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@23')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



# 密码删除测试，删除管理员密码，用户密码也被删除测试(测试用密码'Admin@24','Users@24')
def password_security_024():
    assert _del_password('Admin@23')
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@24')
    time.sleep(1)
    SetUpLib.send_data('Admin@24')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@24')
    time.sleep(1)
    SetUpLib.send_data('Users@24')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@24')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@24')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Psw.ONLY_SET_USER_PSW,3,readline=True):
            logging.info('删除管理员密码，用户密码也被删除')
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('删除管理员密码，用户密码没有被删除')
            SetUpLib.send_key(Key.ESC)
            return
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN_CN, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN_CN, 200, SutConfig.Msg.POST_MESSAGE)
    logging.info('密码删除')
    return True



# 密码删除测试，删除用户密码，只删除用户密码
def password_security_025():
    assert _del_password('Admin@24')
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@25')
    time.sleep(1)
    SetUpLib.send_data('Admin@25')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@25')
    time.sleep(1)
    SetUpLib.send_data('Users@25')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@25')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@25')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Psw.PWS_NOT_SET_STATUS, 5):
            logging.info('删除用户密码')
        else:
            return
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@25')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('删除用户密码，用户密码无法进入setup')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('Admin@25')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@25')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



def password_security_026():
    assert _del_password('Admin@25')
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Psw.CHECK_PSW],5,'Enabled')
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Psw.PSW_COMPLEXITY],5,'Disabled')
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.PSW_LEN],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('8')
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.PSW_RETRY],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('3')
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('123456789')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LEN_DIFF, 5):
        logging.info('设置字符长度为8，输入不符合字符长度密码失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('12345678')
    time.sleep(1)
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('987654321')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LEN_DIFF, 5):
        logging.info('设置字符长度为8，输入不符合字符长度密码失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('12345678')
    time.sleep(1)
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.USER_ADMIN_PSW_SAME, 5):
        logging.info('用户密码管理员密码相同设置失败')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('87654321')
    time.sleep(1)
    SetUpLib.send_data('87654321')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.UP,[SutConfig.Psw.SET_ADMIN_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第一次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第二次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK, 5):
        logging.info('第三次密码输错，屏幕锁定')
        time.sleep(1)
    else:
        return
    assert _del_password('12345678')
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.PSW_LEN],8)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('20')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_RETRY], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('10')
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('1234567890123456789')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LEN_DIFF, 5):
        logging.info('设置字符长度为20，输入不符合字符长度密码失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('12345678901234567890')
    time.sleep(1)
    SetUpLib.send_data('12345678901234567890')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return

    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('0123456789012345678')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LEN_DIFF, 5):
        logging.info('设置字符长度为8，输入不符合字符长度密码失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('12345678901234567890')
    time.sleep(1)
    SetUpLib.send_data('12345678901234567890')
    if SetUpLib.wait_message_enter(SutConfig.Psw.USER_ADMIN_PSW_SAME, 5):
        logging.info('用户密码管理员密码相同设置失败')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('01234567890123456789')
    time.sleep(1)
    SetUpLib.send_data('01234567890123456789')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return

    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第一次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第二次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第三次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第四次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第五次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第六次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第七次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第八次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第九次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK, 5):
        logging.info('第十次密码输错，屏幕锁定')
        time.sleep(1)
    else:
        return
    assert _del_password('12345678901234567890')
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Psw.CHECK_PSW],6,'Enabled')
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Psw.PSW_COMPLEXITY],7,'Enabled')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LEN], 8)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('10')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_RETRY], 8)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('5')
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@26')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LEN_DIFF,5):
        logging.info('设置字符长度为10，输入不符合字符长度密码失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('1234567890')
    time.sleep(1)
    SetUpLib.send_data('1234567890')
    if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH):
        logging.info('密码复杂度打开，密码必须包含大小写字母，数字以及特殊符号')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Adminadmin')
    time.sleep(1)
    SetUpLib.send_data('Adminadmin')
    if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH):
        logging.info('密码复杂度打开，密码必须包含大小写字母，数字以及特殊符号')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@2600')
    time.sleep(1)
    SetUpLib.send_data('Admin@2600')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS):
        logging.info('管理员密码设置成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    SetUpLib.send_data('Users@26')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LEN_DIFF, 5):
        logging.info('设置字符长度为10，输入不符合字符长度密码失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@2600')
    time.sleep(1)
    SetUpLib.send_data('Admin@2600')
    if SetUpLib.wait_message_enter(SutConfig.Psw.USER_ADMIN_PSW_SAME, 5):
        logging.info('用户密码管理员密码相同设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('usersusers')
    time.sleep(1)
    SetUpLib.send_data('usersusers')
    if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH):
        logging.info('密码复杂度打开，密码必须包含大小写字母，数字以及特殊符号')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@user')
    time.sleep(1)
    SetUpLib.send_data('Users@user')
    if SetUpLib.wait_message_enter(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH):
        logging.info('密码复杂度打开，密码必须包含大小写字母，数字以及特殊符号')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@2600')
    time.sleep(1)
    SetUpLib.send_data('Users@2600')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS):
        logging.info('用户密码设置成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第一次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第二次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第三次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第四次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK, 5):
        logging.info('第五次用户密码输错，屏幕锁定')
        time.sleep(1)
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('11111111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('111111111')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Admin@26')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第三次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Users@26')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第四次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('1234567890')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK, 5):
        logging.info('密码第五次输错，屏幕被锁定')
        time.sleep(2)
    else:
        return
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@2600')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN):
        logging.info('输入正确密码成功进入SetUp')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第一次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('1234567890')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第二次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Users@2600')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第三次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Adminadmin')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('第四次密码输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@26')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_ERROR_LOCK, 5):
        logging.info('第五次管理员密码输错，屏幕锁定')
        time.sleep(1)
    else:
        return
    assert _del_password('Admin@2600')
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 6, 'Disabled')
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True



#管理员密码和用户密码不允许设置相同测试
def password_security_027():
    assert _del_password('Admin@25')
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@27')
    time.sleep(1)
    SetUpLib.send_data('Admin@27')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@27')
    time.sleep(1)
    SetUpLib.send_data('Admin@27')
    if SetUpLib.wait_message_enter(SutConfig.Psw.USER_ADMIN_PSW_SAME, 5):
        logging.info('用户密码管理员密码相同设置失败')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.UP,[SutConfig.Psw.SET_ADMIN_PSW],3)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@27')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True