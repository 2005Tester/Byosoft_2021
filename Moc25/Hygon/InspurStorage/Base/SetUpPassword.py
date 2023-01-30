import datetime
from typing import Set
import requests
import re
import os
import time
import logging
from InspurStorage.BaseLib import BmcLib, SetUpLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from batf.Report import stylelog



def del_password(admin=None,user=None):
    logging.info("SetUpLib: Booting to setup")
    SetUpLib.reboot()
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.DEL,SutConfig.Msg.PAGE_MAIN, 250, SutConfig.Msg.HOTKEY_PROMPT_DEL):
        if admin !=None:
            time.sleep(2)
            SetUpLib.send_data(admin)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 15):
                logging.info('SetUp密码存在，准备进入SetUp删除密码')
                logging.info("SetUpLib: Boot to setup main page successfully")
            else:
                return
            assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
                logging.info('密码删除')
                time.sleep(1)
            else:
                return
            time.sleep(2)
            if user:
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_USER_PSW, 18)
                time.sleep(1)
                SetUpLib.send_data_enter(user)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
                    logging.info('删除用户密码')
                else:
                    return
                return True
            else:
                return True
        else:

            time.sleep(2)
            SetUpLib.send_data(user)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 15):
                logging.info('SetUp密码存在，准备进入SetUp删除密码')
                logging.info("SetUpLib: Boot to setup main page successfully")
            else:
                return
            assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_USER_PSW,5)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
                logging.info('密码删除')
                time.sleep(1)
            else:
                return
            time.sleep(2)
            return True
    else:
        logging.info("SetUpLib: Boot to setup main page successfully")
        return True



# 设置密码测试，未设置管理员密码直接设置用户密码，可以设置测试
def password_security_001():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_USER_PSW,8)
    time.sleep(1)
    SetUpLib.send_data_enter('Use123')
    time.sleep(1)
    SetUpLib.send_data('Use123')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码设置成功')
    else:
        stylelog.fail('用户密码设置失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.reboot()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Use123')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN):
        logging.info('输入用户密码成功进入SetUp')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_USER_PSW,18)

    time.sleep(1)
    SetUpLib.send_data_enter('Use123')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)

    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('删除用户密码')
        return True
    else:
        return



# 设置密码长度测试，密码长度小于最少字符数，修改失败测试
def password_security_002():
    assert del_password(user='Use123')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Ad@02')
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
    SetUpLib.send_data_enter('Adm@02')
    time.sleep(1)
    SetUpLib.send_data('Adm@02')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('管理员密码设置成功，开始用户密码长度测试')
        time.sleep(1)
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
    SetUpLib.send_data_enter('Adm@02')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
        return True
    else:
        return



# 设置密码长度测试，密码长度等于最少字符数，修改成功测试
def password_security_003():
    assert SetUpLib.boot_to_setup()
    passwords=['123456','abcdef','ABCDEF','~`!@#$','%^&*()','_-+={[','}]|\:;',"'?<,>.",'"/ 1Ab']
    for password in passwords:
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
        logging.info('管理员密码长度测试')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 5):
            logging.info('设置管理员密码{}长度等于最少字符成功'.format(password))
        else:
            stylelog.fail('设置管理员密码{}长度等于最少字符失败'.format(password))
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        logging.info('用户密码长度测试')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
            logging.info('设置用户密码{}长度等于最少字符成功'.format(password))
            time.sleep(1)
        else:
            stylelog.fail('设置用户密码{}长度等于最少字符失败'.format(password))
            return
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
            logging.info('管理员密码{}删除'.format(password))
            time.sleep(1)
        else:
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
            logging.info('用户密码{}删除'.format(password))
            time.sleep(1)
        else:
            return
    return True



# 设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试
def password_security_004():
    assert SetUpLib.boot_to_setup()
    passwords = ['1234ABCD', '5678abcd', '1290!@#$', 'efghIJKL', 'mnopqrst%^&*()', 'UVWXYZ_-+=']
    for password in passwords:
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
        logging.info('管理员密码长度测试')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 5):
            logging.info('设置管理员密码{}长度等于最少字符成功'.format(password))
        else:
            stylelog.fail('设置管理员密码{}长度等于最少字符失败'.format(password))
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        logging.info('用户密码长度测试')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
            logging.info('设置用户密码{}长度等于最少字符成功'.format(password))
            time.sleep(1)
        else:
            stylelog.fail('设置用户密码{}长度等于最少字符失败'.format(password))
            return

        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
            logging.info('管理员密码{}删除'.format(password))
            time.sleep(1)
        else:
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
            logging.info('用户密码{}删除'.format(password))
            time.sleep(1)
        else:
            return
    return True



# 设置密码长度测试，密码长度最大字符数，修改成功测试
def password_security_005():
    passwords = ['123456abcd~`!@#$%^&*','7890EFGHIJKL()_-+={[','mnopqRSTUVWXYZ}]|\:;']
    for password in passwords:
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
        logging.info('管理员密码长度测试')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 5):
            logging.info('设置管理员密码{}长度等于最少字符成功'.format(password))
        else:
            stylelog.fail('设置管理员密码{}长度等于最少字符失败'.format(password))
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        logging.info('用户密码长度测试')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
            logging.info('设置用户密码{}长度等于最少字符成功'.format(password))
            time.sleep(1)
        else:
            stylelog.fail('设置用户密码{}长度等于最少字符失败'.format(password))
            return

        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
            logging.info('管理员密码{}删除'.format(password))
            time.sleep(1)
        else:
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
            logging.info('用户密码{}删除'.format(password))
            time.sleep(1)
        else:
            return
    return True



# 设置密码长度测试，密码长度超出最大字符数，修改失败测试
def password_security_006():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    logging.info('管理员密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin12345~`!@#$%^&*12')
    time.sleep(1)
    SetUpLib.send_data('Admin12345~`!@#$%^&*12')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('设置管理员密码成功')
    else:
        stylelog.fail('设置管理员密码失败')
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users67890~`!@#$%^&*12')
    time.sleep(1)
    SetUpLib.send_data('Users67890~`!@#$%^&*12')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('设置用户密码成功')
        time.sleep(1)
    else:
        stylelog.fail('设置用户密码失败')
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        logging.info('启动失败')
    time.sleep(1)
    SetUpLib.send_data('Users12345~`')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Users67890~`!@#$%^&*')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码长度超过最大字符数，密码仍为最大字符数')
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE):
        logging.info('启动失败')
        SetUpLib.reboot()
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin12345~`')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('密码错误')
        time.sleep(1)
    else:
        return
    SetUpLib.send_data('Admin12345~`!@#$%^&*')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 100):
        logging.info('设置密码长度超过最大字符数，密码仍为最大字符数')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin12345~`!@#$%^&*')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('密码删除')
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users67890~`!@#$%^&*')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码删除')
        time.sleep(1)
    else:
        return
    return True



# 密码不一致测试
def password_security_007():
    assert del_password('Admin12345~`!@#$%^&*','Users67890~`!@#$%^&*')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('密码不一致测试')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@07')
    time.sleep(1)
    SetUpLib.send_data('Admin@007')
    if SetUpLib.wait_message_enter(SutConfig.Psw.NEW_OLD_PSW_DIFF,3):
        logging.info('设置密码时，两次密码不一致，提示密码不一致')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@07')
    time.sleep(1)
    SetUpLib.send_data('Admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 3):
        logging.info('管理员密码设置成功')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@07')
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@007')
    time.sleep(1)
    SetUpLib.send_data('ADMIN@007')
    if SetUpLib.wait_message_enter(SutConfig.Psw.NEW_OLD_PSW_DIFF,3):
        logging.info('修改密码时，两次密码不一致，提示密码不一致')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@07')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('管理员密码删除')
        time.sleep(1)
    else:
        return
    return True



# 密码输错测试
def password_security_008():
    assert del_password('Admin@07')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@08')
    time.sleep(1)
    SetUpLib.send_data('Admin@08')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 3):
        logging.info('管理员密码设置成功')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('第一次密码输错')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('Admin@06')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('第二次密码输错')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('Admin@05')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LOCK, 5):
        logging.info('第三次密码输错，强制重启')
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL,5):
        logging.info('第一次密码输错')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('Admin@06')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_SETUP_PSW_FAIL, 5):
        logging.info('第二次密码输错')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('Admin@08')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN):
        logging.info('第三次输入在正确密码，成功进入SetUp')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)

    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR,5):
        logging.info('密码第一次输错')
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@06')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第二次输错')
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@06')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_LOCK, 5):
        logging.info('密码第三次输错,强制重启')
        SetUpLib.send_key(Key.ENTER)

    else:
        return

    time.sleep(3)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@08')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN):
        logging.info('输入正确密码，成功进入SetUp')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@07')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第一次输错')
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Admin@06')
    if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_CHECK_ERROR, 5):
        logging.info('密码第二次输错')
        SetUpLib.send_key(Key.ENTER)

    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@08')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('管理员密码删除')
        time.sleep(1)
    else:
        return
    return True



# 用户更改密码测试
def password_security_009():
    assert del_password('Admin@08')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@09')
    time.sleep(1)
    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 3):
        logging.info('管理员密码设置成功')
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@09')
    time.sleep(1)
    SetUpLib.send_data('Users@09')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码设置成功')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.CLOSE_USE_CHANGE,10)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],3):
        logging.info('不允许用户更改密码，<设置用户密码>选项是灰的')
    else:
        logging.info('不允许用户更改密码，仍可以设置用户密码')
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Users@09')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN):
        logging.info('输入用户密码，成功进入SetUp')
    else:
        return
    if not SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW):
        logging.info('不允许用户更改密码，用户密码进入SetUp，无法更改用户密码')
    else:
        stylelog.fail('不允许用户更改密码，用户密码进入SetUp，可以更改用户密码')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 30):
        logging.info('输入密码时按ESC没有跳过密码启动')
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)

    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_TYPE_ADM):
        logging.info('输入管理员密码，成功进入SetUp')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_USER_PSW],5):
        logging.info('不允许用户更改密码，管理员密码进入SetUp，无法更改用户密码')
    else:
        stylelog.fail('不允许用户更改密码，管理员密码进入SetUp，可以更改用户密码')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.OPEN_USE_CHANGE,5)
    if SetUpLib.locate_option(Key.UP,[SutConfig.Psw.SET_USER_PSW],5):
        logging.info('允许用户更改密码，管理员密码进入SetUp，可以更改用户密码')
    else:
        stylelog.fail('允许用户更改密码，管理员密码进入SetUp，无法更改用户密码')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@09')
    time.sleep(1)
    SetUpLib.send_data_enter('Users@009')
    time.sleep(1)
    SetUpLib.send_data('Users@009')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE,3):
        logging.info('修改用户密码成功')
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Users@009')
    if SetUpLib.wait_message_enter(SutConfig.Psw.LOGIN_TYPE_USE):
        logging.info('输入用户密码，成功进入SetUp,密码权限为用户')
    else:
        return

    if SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW):
        logging.info('允许用户更改密码，用户密码进入SetUp，可以更改用户密码')
    else:
        stylelog.fail('允许用户更改密码，用户密码进入SetUp，无法更改用户密码')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@009')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE,3):
        logging.info('用户密码删除成功')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@09')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN):
        logging.info('输入管理员密码，成功进入SetUp')
    else:
        return
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@09')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE,3):
        logging.info('管理员密码删除成功')
    else:
        return
    return True



# 管理员，用户密码进入系统测试
def password_security_010():
    assert del_password('Admin@09','Users@009')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@10')
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 3):
        logging.info('管理员密码设置成功')
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@10')
    time.sleep(1)
    SetUpLib.send_data('Users@10')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码设置成功')
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.boot_with_hotkey_only(Key.F3, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.F3, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                              SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Msg.ENTER_BOOTMENU):
        logging.info('输入管理员密码成功进入启动菜单')
    else:
        return
    time.sleep(1)
    if SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 12, SutConfig.Msg.LINUX_OS_MSG):
        logging.info('管理员密码成功进入系统')
    else:
        return
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(2)
    if not SetUpLib.boot_with_hotkey_only(Key.F3, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.F3, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                              SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_data('Users@10')
    if SetUpLib.wait_message_enter(SutConfig.Msg.ENTER_BOOTMENU):
        logging.info('输入用户密码成功进入启动菜单')
    else:
        return
    time.sleep(1)
    if SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 12, SutConfig.Msg.LINUX_OS_MSG):
        logging.info('用户密码成功进入系统')
    else:
        return
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                          SutConfig.Msg.POST_MESSAGE)
    time.sleep(2)
    SetUpLib.send_data('Admin@10')
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN):
        logging.info('输入管理员密码，成功进入SetUp')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@10')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('管理员密码删除')
        time.sleep(1)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@10')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码删除')
        time.sleep(1)
    else:
        return
    return True



# 清除用户密码
def password_security_011():
    assert del_password('Admin@10','Users@10')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@11')
    time.sleep(1)
    SetUpLib.send_data('Admin@11')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM, 3):
        logging.info('管理员密码设置成功')
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Users@11')
    time.sleep(1)
    SetUpLib.send_data('Users@11')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码设置成功')
    else:
        return
    time.sleep(1)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.CLEAR_USE_PSW],5)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE,5):
        logging.info('清除用户密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM,5):
        logging.info('清除用户密码，管理员密码依然存在')
    else:
        stylelog.fail('清除用户密码，管理员密码不存在')
        return
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@11')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM, 5):
        logging.info('管理员密码删除')
        time.sleep(1)
    else:
        return
    return True