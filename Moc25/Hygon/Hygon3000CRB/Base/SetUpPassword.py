import datetime
from typing import Set
import requests
import re
import os
import time
import logging
from Hygon3000CRB.BaseLib import BmcLib, SetUpLib
from Hygon3000CRB.Config.PlatConfig import Key
from Hygon3000CRB.Config import SutConfig, Sut01Config
from batf.Report import stylelog



# 删除管理员密码
def _del_password(password,Userpassword):
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.F2,Sut01Config.Msg.SEL_LANG, 150, Sut01Config.Msg.HOTKEY_PROMPT_DEL_CN):
        time.sleep(2)
        SetUpLib.send_data(password)
        time.sleep(1)
        if not SetUpLib.wait_message_enter(Sut01Config.Msg.SEL_LANG, 10):
            time.sleep(1)
            SetUpLib.send_data(Userpassword)
            time.sleep(1)
            if SetUpLib.wait_message_enter(Sut01Config.Msg.SEL_LANG, 15):
                logging.info('SetUp用户密码存在，准备进入SetUp删除密码')
                logging.info("SetUpLib: Boot to setup main page successfully")
            else:
                return
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
            time.sleep(1)
            SetUpLib.send_data_enter(Userpassword)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
                logging.info('用户密码删除')
                time.sleep(1)
            else:
                return
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            return True
        else:
            logging.info('SetUp管理员密码存在，准备进入SetUp删除密码')
            logging.info("SetUpLib: Boot to setup main page successfully")
        assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
            logging.info('管理员密码删除')
            time.sleep(1)
        else:
            return
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(Sut01Config.Msg.PSW_SET_STATUS, 5):
            assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(Userpassword)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
                logging.info('用户密码删除')
                time.sleep(1)
            else:
                return
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            return True
        else:
            return True
    else:
        logging.info("SetUpLib: Boot to setup main page successfully")
        return True



# 设置密码长度测试，密码长度小于最少字符数，修改失败测试
def password_security_001():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Ad@01')
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.CHARACTERS_LENGTH_NOT_ENOUGH, 5):
        logging.info('管理员密码长度小于最少字符数，设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('管理员密码长度小于最少字符数，设置成功')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Us@01')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.CHARACTERS_LENGTH_NOT_ENOUGH, 5):
        logging.info('用户密码长度小于最少字符数，设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('用户密码长度小于最少字符数，设置成功')
        return
    return True



# 设置密码长度测试，密码长度等于最少字符数，修改成功测试(测试用密码'Admin@03','Users@03')
def password_security_002(Adminpassword = 'Pap@02', Userpassword = 'Pop@02'):
    assert _del_password('Admin@02','Users@02')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码长度等于最少字符成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码长度等于最少字符失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码长度等于最少字符成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码长度等于最少字符失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('11111111')
    if SetUpLib.wait_message_enter(Sut01Config.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PAGE_MAIN, 100):
        logging.info('设置密码长度为最少字符成功')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试(测试用密码'papbyosoft@04','popbyosoft@04')
def password_security_003(Adminpassword = 'papbyosoft@03', Userpassword = 'popbyosoft@03'):
    assert _del_password('Pap@02', 'Pop@02')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码长度大于最少字符数，小于最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码长度大于最少字符数，小于最大字符数失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码长度大于最少字符数，小于最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码长度大于最少字符数，小于最大字符数失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, Sut01Config.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Pap@02')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码长度大于最少字符数，小于最大字符数成功')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度最大字符数，修改成功测试(测试用密码'Adminadmin@byosoft05','Usersusers@byosoft05')
def password_security_004(Adminpassword = 'Adminadmin@byosoft04',Userpassword = 'Usersusers@byosoft04'):
    assert _del_password('papbyosoft@03','popbyosoft@03')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码长度大于最少字符数，小于最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码长度大于最少字符数，小于最大字符数失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码长度大于最少字符数，小于最大字符数成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码长度大于最少字符数，小于最大字符数失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, Sut01Config.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('papbyosoft@03')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码长度大于最少字符数，小于最大字符数成功')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码长度测试，密码长度超出最大字符数，修改失败测试(测试用密码'Adminadmin@byosoft060','Usersusers@byosofy060')
def password_security_005(Adminpassword = 'Adminadmin@byosoft050',Userpassword = 'Usersusers@byosoft050'):

    assert _del_password('Adminadmin@byosoft04','Usersusers@byosoft04')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Adminadmin@byosoft04')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Adminadmin@byosoft05')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码长度超过最大字符数，密码仍为最大字符数')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 设置密码字符类型测试，只有1种字符类型密码测试
def password_security_006():
    passwords = ['12345678', 'ABCDEFGH', 'abcdefgh', '!@#$%^&*']
    assert _del_password('Adminadmin@byosoft050','Usersusers@byosoft050')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(Sut01Config.Msg.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置管理员密码只有一种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Msg.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置用户密码只有一种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    return True



# 设置密码字符类型测试，2种字符类型密码测试
def password_security_007():
    passwords = ['ADMIN123', 'admin456', 'ADMINadm', 'ADMIN!@#', 'admin!@#', '12345!@#']
    assert _del_password('Adminadmin@byosoft050','Usersusers@byosoft050')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Msg.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置管理员密码只有2种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(Sut01Config.Msg.CHARACTERS_TYPE_NOT_ENOUGH, 5):
            logging.info('设置用户密码只有2种字符类型失败')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            return
    return True





# 设置密码字符类型测试，3种字符类型密码测试(测试用密码Adminpassword)
def password_security_008(Adminpassword = 'admin@08',Userpassword = 'users@08'):
    assert _del_password('Adminadmin@byosoft050','Usersusers@byosoft050')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    logging.info('管理员密码字符类型测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码4种字符类型成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码4种字符类型失败')
        return

    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码4种字符类型成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码4种字符类型失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('adminadmin06')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码4种字符类型成功')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return




# 设置密码字符类型测试，4种字符类型密码测试
def password_security_009(Adminpassword = 'admin@09',Userpassword = 'users@09'):
    assert _del_password('admin@08','users@08')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    logging.info('管理员密码字符类型测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置管理员密码4种字符类型成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置管理员密码4种字符类型失败')
        return

    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('设置用户密码4种字符类型成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码4种字符类型失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('Adminadmin10')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('admin@08')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码4种字符类型成功')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return


# 输入错误密码3次内，提示报错，并可以再次输入测试；输错3次后不允许在输入密码测试；输入错误密码超出阈值测试(测试用密码'Admin@11')
def password_security_010(Adminpassword = 'Admin@10'):
    assert _del_password('admin@09','Users@09')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('管理员密码设置失败')
        return

    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, Sut01Config.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data('admin@09')
    if SetUpLib.wait_message_enter(Sut01Config.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Adminadmin')
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PSW_ERROR_LOCK):
        logging.info('密码第三次输错，屏幕被锁定')
        return True
    else:
        return


# 输入错误密码次数测试，阈值内连续输入错误密码后输入正确密码测试(测试用密码'Admin@11')
def password_security_011():
    assert SetUpLib.boot_with_hotkey(Key.F2, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('第三次输入正确密码，成功进入setup')
        return True
    else:
        return


# 输入错误密码次数测试，超出阈值锁定输入界面，重启后不影响下一次登录(测试用密码'Admin@11')
def password_security_012():

    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第一次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('Adminadm')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码第二次输错')
        time.sleep(2)
    else:
        return
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_ERROR_LOCK, 5):
        logging.info('密码第三次输错，屏幕锁定')
    else:
        return

    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PAGE_MAIN, 100):
        logging.info('输入密码错误，超出阈值锁定输入界面，重启后不影响下一次登录')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@10')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        return True
    else:
        return







# 输入用户密码进入setup测试，进入setup可以删除用户密码(测试用密码'Admin@15','Users@15')
def password_security_013(Adminpassword = 'Admin@13',Userpassword = 'Users@13'):
    count=0
    assert _del_password('Admin@10','Users@09')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('管理员密码设置失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('用户密码设置失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('用户密码进入setup')
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('User Login Type.*User',5):
        logging.info('用户密码进入SetUp，用户登陆类型显示普通用户')
    else:
        stylelog.fail('用户密码进入SetUp，用户登录类型不是普通用户')
        count+=1
    if not SetUpLib.locate_option(Key.DOWN,['Select Language'],6):
        logging.info('用户密码进入SetUp，不能更改语言')
    else:
        stylelog.fail('用户密码进入SetUp，可以更改语言')
        count+=1

    if not SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED):
        logging.info('用户密码进入SetUp,不能更改系统调试模式')
    else:
        stylelog.fail('用户密码进入SetUp,可以更改系统调试模式')
        count+=1
    if not SetUpLib.boot_to_page('Load Setup Defaults'):
        logging.info('用户密码进入SetUp,不能恢复初始值')
    else:
        stylelog.fail('用户密码进入SetUp,可以恢复初始值')
        count+=1
    if not SetUpLib.boot_to_page('User Wait Time'):
        logging.info('用户密码进入SetUp，不能更改用户等待时间')
    else:
        stylelog.fail('用户密码进入SetUp，可以更改用户等待时间')
        count+=1
    if not SetUpLib.boot_to_page('PCIE Configuration'):
        logging.info('用户密码进入SetUp，不能进入PCIE配置')
    else:
        stylelog.fail('用户密码进入SetUp，可以进入PCIE配置')
        count += 1
    assert SetUpLib.boot_to_page(Sut01Config.Msg.SET_USER_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码进入setup，用户权限可以删除用户密码')
        SetUpLib.send_key(Key.ENTER)

    else:
        count+=1
    if count==0:
        return True
    else:
        return



# 输入用户密码进入setup测试，进入setup可以修改用户密码(测试用密码'Users@16')
def password_security_014(Userpassword = 'Users@14'):
    
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@13')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('用户密码设置失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)

    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('用户密码进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_USER_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@15')
    time.sleep(1)
    SetUpLib.send_data('Users@15')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS):
        logging.info('用户密码进入setup，修改用户密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    BmcLib.power_reset()
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)

    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Users@15')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('修改用户密码成功')
        return True
    else:
        return


# 密码不能明文显示，任意密码用*代替字符测试(测试用密码'Admin@15')
def password_security_015():

    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_data('Admin@13')
    data = SetUpLib.get_data(1, Key.ENTER)

    if '********' in data and 'Admin@13' not in data:
        logging.info('密码不是明文显示，而是用*代替')
        return True
    else:
        return


# 密码修改验证旧密码测试，输入错误旧密码，不能修改密码(测试用密码'Admin@15','Users@16')
def password_security_016():

    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_data('Admin@13')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        pass
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PSW_CHECK_ERROR, 5):
        logging.info('管理员密码修改时，输入错误旧密码，无法修改密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('12345678')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_CHECK_ERROR, 5):
        logging.info('用户密码修改时，输入错误旧密码，无法修改密码')
        SetUpLib.send_key(Key.ENTER)
        return True
    else:
        return



# 密码修改验证新密码测试，新密码确认时，输入错误新密码，修改失败测试(测试用密码'Admin@15','Users@16')
def password_security_017():

    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@13')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        pass
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@13')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@19')
    time.sleep(1)
    SetUpLib.send_data('Admin@18')
    if SetUpLib.wait_message_enter(SutConfig.Msg.NEW_OLD_PSW_DIFF, 5):
        logging.info('管理员密码修改，新密码确认时，输入错误新密码，修改失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@15')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@19')
    time.sleep(1)
    SetUpLib.send_data('Users@18')
    if SetUpLib.wait_message_enter(SutConfig.Msg.NEW_OLD_PSW_DIFF, 5):
        logging.info('用户密码修改，新密码确认时，输入错误新密码，修改失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Msg.SET_ADMIN_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@13')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS,5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 6)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@15')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



# 历史密码5次范围内重复修改无效，超过5次后可以修改为5次前的密码测试(测试用密码'Admin@20','Users@20‘)
def password_security_018(Adminpassword = 'Admin@18',Userpassword = 'Users@18'):
    assert _del_password('Admin@13','Users@15')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    logging.info('管理员密码5次范围内重复无效测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第一次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)

    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@001')
    time.sleep(1)
    SetUpLib.send_data('Admin@001')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第五次管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@004')
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PREVIOUS_5_PSW_SAME, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第六次管理员密码修改成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@005')
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('修改第一次设置的管理员密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    assert SetUpLib.boot_with_hotkey(Key.F2, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)


    time.sleep(1)
    SetUpLib.send_data('Admin@005')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    logging.info('用户密码5次范围内重复无效测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第一次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@001')
    time.sleep(1)
    SetUpLib.send_data('Users@001')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第五次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@004')
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PREVIOUS_5_PSW_SAME, 5):
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
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('第六次用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@005')
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('修改第一次设置用户密码成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)


    time.sleep(1)
    SetUpLib.send_data('Users@005')
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        pass
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 6)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return




# 开机密码测试，打开开机密码，进入系统需要输入开机密码测试(测试用密码Adminpassword,'Users@21')
def password_security_019(Adminpassword = 'Admin@19',Userpassword = 'Users@19'):
    assert _del_password('Admin@18','Users@18')
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置成功')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:

        return
    assert SetUpLib.select_option_value(Key.DOWN, [Sut01Config.Msg.POWER_ON_PSW_OPTION], Key.DOWN, 'Enabled',6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    logging.info('开机密码打开，进入系统需要输入密码')
    time.sleep(5)
    SetUpLib.send_data(Adminpassword)
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.ENTER_BOOTMENU_CN,15):
        logging.info('进入启动菜单')
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.LINUX_OS,20,''),'开机密码打开，进入系统不需要输入密码'
    if BmcLib.ping_sut():
        logging.info('输入管理员密码成功进入系统')
    else:
        stylelog.fail('输入管理员密码，没有进入系统')
        return

    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.LOGIN_SETUP_PSW_PROMPT, 200, Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    logging.info('开机密码打开，进入系统需要输入密码')
    time.sleep(5)
    SetUpLib.send_data(Userpassword)
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
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data_enter(Adminpassword)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN):
        pass
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    assert SetUpLib.select_option_value(Key.DOWN, [SutConfig.Msg.POWER_ON_PSW_OPTION],Key.DOWN, 'Disabled',6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    time.sleep(2)
    assert SetUpLib.select_boot_option(Key.DOWN, Sut01Config.Msg.LINUX_OS, 15,''), '开机密码关闭，进入系统仍需要输入密码'
    logging.info('开机密码关闭，进入系统不需要输入密码')
    if BmcLib.ping_sut():
        logging.info('成功进入系统')
    else:
        stylelog.fail('进入系统失败')
        return
    BmcLib.power_reset()
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 10):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 6)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



def _change_date_days(days):
    assert SetUpLib.boot_to_page('CPU Info')
    assert SetUpLib.locate_option(Key.DOWN, ['System Date and Time'], 6)
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
        SetUpLib.send_key(Key.ESC)
    else:
        stylelog.fail('日期修改失败')
        SetUpLib.send_key(Key.ESC)
        return




    # 密码有效期
def password_security_020(Adminpassword='Admin@20',Userpassword = 'Users@20'):
    assert _del_password('Admin@19','Users@19')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.select_option_value(Key.DOWN, ['Set Password Valid Days'], Key.DOWN, '7 Days', 6)
    _change_date_days(days=6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if not SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，6天后POST界面管理员密码没有失效')
    else:
        stylelog.fail('设置密码有效期为7天，6天后POST界面管理员密码失效')
        return

    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if not SetUpLib.wait_message_enter(Sut01Config.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，6天后setup下管理员密码没有失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，6天后setup下管理员密码失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    _change_date_days(days=1)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后setup下管理员密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后setup下管理员密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(Adminpassword)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后POST界面管理员密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后POST界面管理员密码没有失效')
        return


    # 有效期为30天
    assert SetUpLib.boot_to_page(Sut01Config.Msg.SET_ADMIN_PSW)
    assert SetUpLib.select_option_value(Key.DOWN, ['Set Password Valid Days'], Key.DOWN, '30 Days', 6)
    _change_date_days(days=22)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if not SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，29天后POST界面管理员密码没有失效')
    else:
        stylelog.fail('设置密码有效期为30天，29天后POST界面管理员密码失效')
        return

    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if not SetUpLib.wait_message_enter(Sut01Config.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，29天后setup下管理员密码没有失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，29天后setup下管理员密码失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    _change_date_days(days=1)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后setup下管理员密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后setup下管理员密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(Adminpassword)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后POST界面管理员密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后POST界面管理员密码没有失效')
        return
    # 无限期
    time.sleep(2)
    assert SetUpLib.boot_to_page(Sut01Config.Msg.SET_ADMIN_PSW)
    assert SetUpLib.select_option_value(Key.DOWN, ['Set Password Valid Days'], Key.DOWN, 'Forever',6)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(Adminpassword)
    time.sleep(2)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PAGE_MAIN, 100):
        logging.info('设置密码有效期为无限期，30天后管理员密码没有失效')
    else:
        stylelog.fail('设置密码有效期为30天，30天后管理员密码失效')
        return
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_ADMIN_PSW,4)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 10):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return

    #
    # # 用户密码有效期测试
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('用户密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.select_option_value(Key.DOWN, ['Set Password Valid Days'], Key.DOWN, '7 Days', 6)
    _change_date_days(days=6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if not SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，6天后POST界面用户密码没有失效')
    else:
        stylelog.fail('设置密码有效期为7天，6天后POST界面用户密码失效')
        return

    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if not SetUpLib.wait_message_enter(Sut01Config.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，6天后setup下用户密码没有失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，6天后setup下用户密码失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    _change_date_days(days=1)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(2)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后setup下用户密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后setup下用户密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(Userpassword)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为7天，7天后POST界面用户密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为7天，7天后POST界面用户密码没有失效')
        return


    # 有效期为30天
    assert SetUpLib.boot_to_page(Sut01Config.Msg.SET_ADMIN_PSW)
    assert SetUpLib.select_option_value(Key.DOWN, ['Set Password Valid Days'], Key.DOWN, '30 Days', 6)
    _change_date_days(days=22)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if not SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，29天后POST界面用户密码没有失效')
    else:
        stylelog.fail('设置密码有效期为30天，29天后POST界面用户密码失效')
        return

    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(1)
    SetUpLib.send_data(Userpassword)
    if not SetUpLib.wait_message_enter(Sut01Config.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，29天后setup下用户密码没有失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，29天后setup下用户密码失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    _change_date_days(days=1)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(2)
    SetUpLib.send_data(Userpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后setup下用户密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后setup下用户密码没有失效')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(Userpassword)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PSW_EXPIRE, 5):
        logging.info('设置密码有效期为30天，30天后POST界面用户密码失效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('设置密码有效期为30天，30天后POST界面用户密码没有失效')
        return
    # 无限期
    time.sleep(2)
    assert SetUpLib.boot_to_page(Sut01Config.Msg.SET_ADMIN_PSW)
    assert SetUpLib.select_option_value(Key.DOWN, ['Set Password Valid Days'], Key.DOWN, 'Forever',6)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data(Userpassword)
    time.sleep(2)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.PAGE_MAIN, 100):
        logging.info('设置密码有效期为无限期，30天后用户密码没有失效')
    else:
        stylelog.fail('设置密码有效期为30天，30天后用户密码失效')
        return
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
    time.sleep(1)
    SetUpLib.send_data_enter(Userpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 10):
        logging.info('用户密码删除')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        return True
    else:
        return



# 输入密码时按ESC测试
def password_security_021(Adminpassword='Admin@21'):
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.F2, SutConfig.Msg.SEL_LANG, 120, Sut01Config.Msg.HOTKEY_PROMPT_DEL_CN):
        time.sleep(2)
        SetUpLib.send_data('Admin@20')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data=SetUpLib.get_data(2)
        if re.search(Sut01Config.Msg.LOGIN_SETUP_PSW_FAIL,data):
            SetUpLib.send_data('Users@20')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)

            if SetUpLib.wait_message(SutConfig.Msg.PSW_EXPIRE,2):
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
                time.sleep(1)
                SetUpLib.send_data_enter('Users@20')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 10):
                    logging.info('用户密码删除')
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                else:
                    return
            else:
                assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PSW.SET_USER_PSW,8)
                time.sleep(1)
                SetUpLib.send_data_enter('Users@20')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 10):
                    logging.info('用户密码删除')
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                else:
                    return
        elif re.search(Sut01Config.Msg.PSW_EXPIRE,data):
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            assert SetUpLib.boot_to_page(Sut01Config.Msg.SET_ADMIN_PSW)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('Admin@20')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 10):
                logging.info('管理员密码删除')
                SetUpLib.send_key(Key.ENTER)
                if SetUpLib.wait_message(Sut01Config.Msg.PSW_SET_STATUS, 5):
                    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    SetUpLib.send_data_enter('Users@20')
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
                        logging.info('用户密码删除')
                        time.sleep(1)
                    else:
                        return
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(2)
                else:
                    return
            else:
                return
        else:
            time.sleep(2)
            assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('Admin@20')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
                logging.info('管理员密码删除')
                time.sleep(1)
            else:
                return
            SetUpLib.send_key(Key.ENTER)

            if SetUpLib.wait_message(Sut01Config.Msg.PSW_SET_STATUS, 5):
                assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.SET_USER_PSW], 3)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_data_enter('Users@20')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
                    logging.info('用户密码删除')
                    time.sleep(1)
                else:
                    return
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
            else:
                return

    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码设置')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        return
    assert SetUpLib.select_option_value(Key.DOWN, [SutConfig.Msg.PSW_EXPIRY_DATE],Key.DOWN, 'Forever',6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 30):
        logging.info('输入密码时按ESC没有跳过密码启动')
    else:
        return
    assert SetUpLib.boot_with_hotkey(Key.F2, SutConfig.Msg.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data(Adminpassword)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Msg.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(Adminpassword)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(Sut01Config.Msg.DEL_SETUP_PSW_SUCCESS, 5):
        logging.info('管理员密码删除')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True
