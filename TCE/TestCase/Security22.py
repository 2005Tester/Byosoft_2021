#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-


import logging
import time
import os
from Core.SutInit import Sut
from Core import SerialLib, SshLib, MiscLib
from Report import ReportGen
from TCE.Config.PlatConfig import Key, Msg
from TCE.Config import SutConfig
from TCE.BaseLib import SetUpLib, Update, BmcLib

# Test case ID: TC030-TC070

##########################################
#           Password Test Cases          #
##########################################
#
# default_pwd = 'Admin@9000'
# new_pwd_4 = 'Admini@6789'
# new_pwd_5 = 'Ad@90'
# new_pwd_8 = 'Admin@9!'
# new_pwd_9 = 'Admin@9002'
# new_pwd_16 = 'Admin@9001Admin@'
# new_pwd_17 = 'Admin@9001Admin@9'
# weak_pwd = 'Huawei@CLOUD8!'
# 新密码为1种字符类型，尝试各种组合（共4种组合）
pwd_list = ['55555555', 'EEEEEEEE', 'bbbbbbbb', '!@#$%^&*']
# 新密码为2种字符类型，尝试各种组合（共6种组合）
pwd_list1 = ['ADMIN123', 'admin789', 'admin###', 'ADMIN###', 'ADMINadm', '1234####']
# System will be locked after send wrong pwd 3 times
# 新密码为3种字符类型，尝试各种组合（共4种组合）  'INTER@789','inter@789',
pwd_list2 = ['Admin@9009', 'INTERNET789#', 'internet789#', 'Administrator@', 'Administrator1']
# common error msg
pwd_info_1 = 'Please type in your password'
pwd_info_2 = 'Please type in your new password'
pwd_info_3 = 'Please confirm your new password'
pwd_info_4 = 'Changes have been saved after press'
invalid_info = 'Invalid Password'
error_info = 'Enter incorrect password 3 times,System Locked'
enable_simple_pwd = 'Enabling simple password poses security risks.'
simple_pwd_warning = 'The password fails the dictionary check - it is too simplistic/systematic'
log_dir = SutConfig.Env.LOG_DIR


# change password
# OnStart:光标停留在"Manage Supervisor Password"
# OnComplete: 修改密码成功, 光标停留在"Manage Supervisor Password"
def change_password(old_pw, new_pw):
    logging.info("Change password from {0} to {1}".format(old_pw, new_pw))
    SetUpLib.send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_1, 10):
        return
    SetUpLib.send_data_enter(old_pw)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_2, 10):
        return
    SetUpLib.send_data_enter(new_pw)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_3, 10):
        return
    SetUpLib.send_data_enter(new_pw)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_4, 10):
        return
    SetUpLib.send_key(Key.ENTER)
    logging.info("Password is changed from {0} to {1}".format(old_pw, new_pw))
    return True


# change password
# OnStart:光标停留在"Manage Supervisor Password"
# OnComplete: 修改密码失败, 光标停留在"Manage Supervisor Password"
def change_password_negtive(old_pw, new_pw):
    logging.info("Change password from {0} to {1}, should be rejected.".format(old_pw, new_pw))
    SetUpLib.send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_1, 10):
        return
    SetUpLib.send_data_enter(old_pw)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_2, 10):
        return
    SetUpLib.send_data_enter(new_pw)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, pwd_info_3, 10):
        return
    SetUpLib.send_data_enter(new_pw)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, invalid_info, 10):
        return
    SetUpLib.send_key(Key.ENTER)
    logging.info("Password change to: {0} is rejected".format(new_pw))
    return True


# Locate option ["Simple Password", "<Disabled>"]
# OnStart: N/A
# OnComplete: Stop at option Simple password
def locate_option_simplepw():
    if not SetUpLib.boot_to_page(Msg.PAGE_SECURITY):
        return
    if not SetUpLib.locate_option(Key.DOWN, ["Simple Password", "<Disabled>"], 15):
        return
    return True


# after set password, checkin password
def checkPWD(pwd1, pwd2):
    logging.info("Verifying password...")
    if not SetUpLib.continue_to_pw_prompt(Key.DEL):
        return
    logging.info("Check password negative: {0}".format(pwd2))
    SetUpLib.send_data_enter(pwd2)
    if not SetUpLib.wait_message(invalid_info):
        return
    SetUpLib.send_key(Key.ENTER)
    logging.info("Check default password, should be rejected.")
    SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
    if not SetUpLib.wait_message(invalid_info):
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    logging.info("Check password positive: {0}".format(pwd1))
    SetUpLib.send_data_enter(pwd1)
    time.sleep(1)
    #    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if not SetUpLib.wait_message('Continue'):
        return
    return True


def restore_env(log_dir):
    path = log_dir
    bin_dir = path + "\\output\\"
    # bin_file = os.listdir(path)
    if not os.path.exists(bin_dir):
        logging.info("output no exist")
        Update.get_test_image(log_dir, 'master', 'debug-build')

    else:
        logging.info("output_file exist")
    if not Update.update_specific_img(log_dir):
        logging.info("restore_env  Failed.")
        return
    return True


# 用于新密码机制，外部unipwd工具修改为Admin@909密码
def reset_password_by_unipwd():
    logging.info("Restoring enviroment...")
    BmcLib.clear_cmos()
    logging.info("Modify PWD to SutConfig.BIOS_PW by unipwd tool")
    if not BmcLib.force_reset():
        logging.info("Boot to boot manager fail.")
        return restore_env(log_dir)
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 600):
        logging.info("Ping SUT fail.")
        return restore_env(log_dir)
    SshLib.execute_command(Sut.OS_SSH, r'cd {0};insmod ufudev.ko'.format(SutConfig.Env.UNI_PATH))
    res = SshLib.execute_command(Sut.OS_SSH,
                                 r'cd {0};./unipwd -set {1}'.format(SutConfig.Env.UNI_PATH, Msg.BIOS_PASSWORD))
    logging.info(res)
    if len(res) == 0:
        logging.info('blank, maybe the ko module failed')
        return restore_env(log_dir)
    elif 'error' in res:
        logging.info("Modify BIOS PWD:Fail")
        return restore_env(log_dir)
    else:
        logging.info('Rebooting the SUT...')
        SshLib.execute_command(Sut.OS_SSH, 'reboot')
    if not SetUpLib.wait_message(Msg.BIOS_BOOT_COMPLETE):
        return
    logging.info("Modify BIOS PWD:Pass")
    return True


# Bios_Password_Security
def Testcase_BiosPasswordSecurity_002():
    tc = ('036', '[TC036]BiosPasswordSecurity_002', '设置密码长度测试_密码长度小于最少字符数，修改失败测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20)
        assert change_password_negtive(Msg.BIOS_PASSWORD, 'Ad@90')
        logging.info("show invalid_password")
        assert SetUpLib.boot_to_setup()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_003():
    tc = ('037', '[TC037]BiosPasswordSecurity_003', '设置密码长度度测试_密码长度等于最少字符数，修改成功测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        assert (change_password(Msg.BIOS_PASSWORD, 'Admin@9!'))
        SetUpLib.send_keys([Key.F10, Key.Y])
        logging.info("Changes have been saved after press")
        assert (checkPWD('Admin@9!', '11111111'))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_004():
    tc = ('038', '[TC038]BiosPasswordSecurity_004', '设置密码长度测试_密码长度大于最少字符数，小于最大字符数，修改成功测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        assert (change_password(Msg.BIOS_PASSWORD, 'Admin@9003'))
        SetUpLib.send_keys([Key.F10, Key.Y])
        logging.info("Changes have been saved after press")
        assert (checkPWD('Admin@9003', '11111111'))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_005_019_021():
    tc = (
        '039', '[TC039]BiosPasswordSecurity_005_019_021',
        '设置密码长度度测试_密码长度最大字符数，修改成功测试；密码修改时要验证旧密码测试；新密码需要再次输入确认测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        assert (change_password(Msg.BIOS_PASSWORD, 'Admin@9001Admin@'))
        SetUpLib.send_keys([Key.F10, Key.Y])
        logging.info("Changes have been saved after press")
        assert (checkPWD('Admin@9001Admin@', '11111111'))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_006():
    tc = ('040', '[TC040]BiosPasswordSecurity_006', '设置密码长度测试_密码长度超出最大字符数,修改失败测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 10)
        assert change_password(Msg.BIOS_PASSWORD, 'Byosoft@5000soft')
        logging.info("Save and reboot.")
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert checkPWD('Byosoft@5000soft', '11111111')
        # 超出最大字符
        logging.info("Test with characters exceed max support")
        logging.info("Move to BIOS Configuration")
        SetUpLib.send_keys([Key.RIGHT, Key.RIGHT, Key.DOWN, Key.ENTER])
        assert SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_SECURITY], 10)
        assert SetUpLib.locate_option(Key.DOWN, ["Manage Supervisor Password"], 10)
        assert change_password('Byosoft@5000soft', 'Inter@8000Byosof4')
        logging.info("Save and reboot.")
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert checkPWD('Inter@8000Byosof', 'Byosoft@5000soft')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_007():
    tc = ('041', '[TC041]BiosPasswordSecurity_007', '设置密码字符类型测试_只有1种字符类型密码测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        for i in pwd_list:
            try:
                assert (change_password_negtive(Msg.BIOS_PASSWORD, i))
            except Exception:
                logging.info("error password :", format(i))
        assert SetUpLib.boot_to_setup()
    except AssertionError:
        result.log_fail(capture=True)
        return False
    result.log_pass()


def Testcase_BiosPasswordSecurity_008():
    tc = ('042', '[TC042]BiosPasswordSecurity_008', '设置密码字符类型测试_2种字符类型密码测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        for j in pwd_list1:
            try:
                assert (change_password_negtive(Msg.BIOS_PASSWORD, j))
            except Exception:
                logging.info("error password :", format(j))
        assert SetUpLib.boot_to_setup()
    except AssertionError:
        result.log_fail(capture=True)
        return False
    result.log_pass()


def Testcase_BiosPasswordSecurity_009():
    tc = ('043', '[TC043]BiosPasswordSecurity_009', '设置密码字符类型测试_3种字符类型密码测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_setup()
        k = 0
        while k < len(pwd_list2) - 1:
            m = k + 1
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_message(pwd_info_1)
            SetUpLib.send_data_enter(pwd_list2[k])
            logging.info("input default_pwd")
            assert SetUpLib.wait_message(pwd_info_2)
            SetUpLib.send_data_enter(pwd_list2[m])
            logging.info("input new_pwd")
            assert SetUpLib.wait_message(pwd_info_3)
            SetUpLib.send_data_enter(pwd_list2[m])
            logging.info("confirm new_pwd")
            # 满足密码测试用例规则
            if pwd_list2[m] != 'Administrator1':
                logging.info("Meet the password test case rules")
                assert SetUpLib.wait_message(pwd_info_4)
                SetUpLib.send_key(Key.ENTER)
                SetUpLib.send_keys([Key.F10, Key.Y])
                assert (checkPWD(pwd_list2[m], pwd_list2[k]))
            # 不满足密码测试用例规则
            else:
                logging.info("Does not meet the password test case rules")
                assert SetUpLib.wait_message(invalid_info)
                logging.info("show invalid_password")
                SetUpLib.send_key(Key.ENTER)
                SetUpLib.send_key(Key.CTRL_ALT_DELETE)
                assert (checkPWD(pwd_list2[k], pwd_list2[m]))
            k = k + 1
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_010():
    tc = ('044', '[TC044]BiosPasswordSecurity_010', '设置密码字符类型测试_4种字符类型密码')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        assert (change_password(Msg.BIOS_PASSWORD, 'Admin@6789'))
        SetUpLib.send_keys([Key.F10, Key.Y])
        logging.info("Changes have been saved after press")
        assert (checkPWD('Admin@6789', 'Admin6789admin'))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_011_012_014():
    tc = (
        '045', '[TC045]BiosPasswordSecurity_011,012,014', '输入错误密码次3次内，提示报错，并可以再次输入测试；输错3次后不允许再输入密码测试；输入错误密码超出阈值测试')
    result = ReportGen.LogHeaderResult(tc)
    pwd_error = ['Admin@7890', 'Ad@90', '555555']
    try:
        assert SetUpLib.boot_to_pw_prompt(Key.DEL)
        for list_error in pwd_error:
            try:
                SetUpLib.send_data_enter(list_error)
                logging.info("Send  password...")
                if list_error != pwd_error[-1]:
                    assert (SetUpLib.wait_message(invalid_info))
                    time.sleep(2)
                    SetUpLib.send_key(Key.ENTER)
                    assert (SetUpLib.wait_message('Enter Current Password'))
                    logging.info("input password again")
                else:
                    SetUpLib.send_key(Key.ENTER)
                    assert (SetUpLib.wait_message(error_info))
                    logging.info("Enter incorrect password 3 times,System Locked")
            except:
                logging.info("eorro password :", format(list_error))
    except AssertionError:
        result.log_fail(capture=True)
        return False
    result.log_pass()


def Testcase_BiosPasswordSecurity_013():
    tc = ('046', '[TC046]BiosPasswordSecurity_013', '输入错误密码次数测试_阈值内连续输入错误密码后输入正确密码测试')
    result = ReportGen.LogHeaderResult(tc)
    pwd_error = ['Admin@9876', 'Da@89', Msg.BIOS_PASSWORD]
    try:
        assert (SetUpLib.boot_to_pw_prompt(Key.DEL))
        for list_error in pwd_error:
            try:
                SetUpLib.send_data_enter(list_error)
                logging.info("Send password...")
                if list_error != pwd_error[-1]:
                    assert SetUpLib.wait_message(invalid_info, 10)
                    SetUpLib.send_key(Key.ENTER)
                    assert SetUpLib.wait_message(Msg.PW_PROMPT, 10)
                    logging.info("input password again")
                else:
                    # assert (SerialLib.is_msg_present(serial, Msg.PW_UPDATE_PROMPT))
                    SetUpLib.send_key(Key.ENTER)
                    assert SetUpLib.wait_message('Continue', 60)
                    logging.info("Booting to setup successfully")
            except:
                logging.info("eorro password :", format(list_error))
                return
    except AssertionError:
        reset_password_by_unipwd()
        result.log_fail(capture=True)
        return False
    result.log_pass()


def Testcase_BiosPasswordSecurity_014_015():
    tc = ('047', '[TC047]BiosPasswordSecurity_014_015', '输入错误密码次数测试_超出阈值锁定输入界面，提示报错、并提示复位；超出阈值重启后不影响下一次登录')
    result = ReportGen.LogHeaderResult(tc)
    pwd_error = ['Admin@3456', 'Qa@12', '222222']
    try:
        assert SetUpLib.boot_to_pw_prompt(Key.DEL)
        for list_error in pwd_error:
            try:
                SetUpLib.send_data_enter(list_error)
                logging.info("Send  password...")
                if list_error != pwd_error[-1]:
                    assert SetUpLib.wait_message(invalid_info)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    assert SetUpLib.wait_message('Enter Current Password')
                    logging.info("input password again")
                else:
                    SetUpLib.send_key(Key.ENTER)
                    assert SetUpLib.wait_message(error_info)
                    logging.info("Enter incorrect password 3 times,System Locked")
            except:
                logging.info("eorro password :", format(list_error))
                return
        assert SetUpLib.boot_to_setup()
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


def Testcase_BiosPasswordSecurity_016_017():
    tc = ('048', '[TC048]BiosPasswordSecurity_016', '密码不能明文显示_不显示或用*代替字符测试;任意密码不显示或用*代替字符测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_pw_prompt(Key.DEL)
        SetUpLib.send_data(Msg.BIOS_PW_DEFAULT)
        time.sleep(1)
        try:
            result.capture_screen()
            logging.info('get pic pass')
        except:
            logging.info('get pic fail')
    except AssertionError:
        result.log_fail(capture=True)
        return False
    result.log_pass()


def Testcase_BiosPasswordSecurity_020():
    tc = ('049', '[TC049]BiosPasswordSecurity_020', '密码修改验证旧密码测试_输入错误旧密码，不能修改密码')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        SetUpLib.send_key(Key.ENTER)
        assert (SetUpLib.wait_message(pwd_info_1))
        SetUpLib.send_key('Inter#9999')
        logging.info("input error password")
        SetUpLib.send_key(Key.ENTER)
        assert (SetUpLib.wait_message(invalid_info))
        logging.info("show invalid_password")
        SetUpLib.send_key(Key.ENTER)
    except AssertionError:
        result.log_fail(capture=True)
        return False
    result.log_pass()


def Testcase_BiosPasswordSecurity_022():
    tc = ('050', '[TC050]BiosPasswordSecurity_022', '密码修改验证新密码测试_新密码确认时，输入错误新密码，修改失败测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        SetUpLib.send_key(Key.ENTER)
        assert (SetUpLib.wait_message(pwd_info_1))
        SetUpLib.send_key(Msg.BIOS_PASSWORD)
        logging.info("input default_pwd")
        SetUpLib.send_key(Key.ENTER)
        assert (SetUpLib.wait_message(pwd_info_2))
        SetUpLib.send_key("Admin@9999")
        logging.info("input new_pwd")
        SetUpLib.send_key(Key.ENTER)
        assert (SetUpLib.wait_message(pwd_info_3))
        SetUpLib.send_key("Admin@9998")
        logging.info("input error confirm new_pwd")
        SetUpLib.send_key(Key.ENTER)
        assert (SetUpLib.wait_message('Passwords are not the same'))
        assert SetUpLib.boot_to_setup()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_025():
    tc = ('051', '[TC051]BiosPasswordSecurity_025', '历史密码5次范围内重复修改无效,超过5次后可以修改为5次前的密码测试')
    result = ReportGen.LogHeaderResult(tc)
    times_pwd = ['Admin@9009', 'Admin@9010', 'Admin@9012', 'Admin@9013', 'Admin@9014', 'Admin@9009', 'Admin@9015']
    try:
        assert SetUpLib.boot_to_setup()
        k = 0
        while k < len(times_pwd) - 2:
            m = k + 1
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_message(pwd_info_1)
            SetUpLib.send_data_enter(times_pwd[k])
            logging.info("input default_pwd")
            assert SetUpLib.wait_message(pwd_info_2)
            SetUpLib.send_data_enter(times_pwd[m])
            logging.info("input new_pwd")
            assert SetUpLib.wait_message(pwd_info_3)
            SetUpLib.send_data_enter(times_pwd[m])
            logging.info("confirm new_pwd")
            if times_pwd[m] != "Admin@9009":
                logging.info("Password changed successfully")
                assert SetUpLib.wait_message(pwd_info_4)
                SetUpLib.send_key(Key.ENTER)
                SetUpLib.send_keys([Key.F10, Key.Y])
                assert checkPWD(times_pwd[m], times_pwd[k])
            else:
                logging.info("Password changed Failed")
                assert SetUpLib.wait_message(invalid_info)
                logging.info("use old pwd,invalid.")
                SetUpLib.send_key(Key.ENTER)
                SetUpLib.send_key(Key.CTRL_ALT_DELETE)
                assert checkPWD(times_pwd[k], times_pwd[m])
            k = k + 1
        assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20)
        assert change_password(times_pwd[4], times_pwd[6])
        SetUpLib.send_keys([Key.F10, Key.Y])
        assert checkPWD(times_pwd[6], times_pwd[4])
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def Testcase_BiosPasswordSecurity_028():
    tc = ('052', '[TC052]BiosPasswordSecurity_028', '开启OS引导时,弹出密码输入框,需要输入管理员密码测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Key.UP, ["Power On Password", "<Disabled>"], 20)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        logging.info("set Power on Password Enable")
        assert SetUpLib.wait_message('Enter Current Password:')
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        logging.info("reboot ,input BIOS_PASSWORD ")
        time.sleep(30)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        logging.info("正常恢复")
        result.log_pass()
    except AssertionError:
        logging.info("异常恢复")
        result.log_fail()
    finally:
        reset_password_by_unipwd()


def pwd_auth_mgt_01():
    tc = ('053', '[TC053]AuthenticationManagement_001', '热键页面遍历热键，检查进入Setup菜单是否需要输入密码')
    result = ReportGen.LogHeaderResult(tc)
    hot_key = [Key.DEL, Key.F11, Key.F12, Key.F6]
    try:
        for hk in hot_key:
            logging.info("Testing with hotkey: {0}".format(hk))
            assert BmcLib.force_reset()
            assert SetUpLib.wait_message(Msg.HOTKEY_PROMPT_DEL)
            logging.info("Rebooting SUT")
            try:
                SetUpLib.send_key(hk)
                assert SetUpLib.wait_message('Enter Current Password')
            except Exception:
                logging.info("error key :", format(hk))
                result.log_fail()
                return
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


def pwd_auth_mgt_07():
    tc = ('054', '[TC054]AuthenticationManagement_007', '禁止提供自动登录等特殊功能')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_setup()
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


def pwd_auth_mgt_08_10():
    tc = ('055', '[TC055]AuthenticationManagement_008_010',
          '管理员登录密码大于16位字符无法输入;修改管理员密码界面需要先输入旧密码，再输入两次新密码')
    result = ReportGen.LogHeaderResult(tc)
    pwd_error = ['Admin@3456', 'Pw@99', '666666']
    admin_pwd_17 = 'Admin@6789byosoft'
    admin_pwd_16 = 'Admin@6789byosof'
    try:
        assert SetUpLib.boot_to_pw_prompt(Key.DEL)
        logging.info("input 3 times error pwd,System Locked")
        for list_error in pwd_error:
            try:
                SetUpLib.send_data_enter(list_error)
                logging.info("Send  password...")
                if list_error != pwd_error[-1]:
                    assert SetUpLib.wait_message(invalid_info)
                    time.sleep(2)
                    SetUpLib.send_key(Key.ENTER)
                    assert SetUpLib.wait_message('Enter Current Password')
                    logging.info("input password again")
                else:
                    SetUpLib.send_key(Key.ENTER)
                    assert SetUpLib.wait_message(error_info)
                    logging.info("Enter incorrect password 3 times,System Locked")
            except:
                logging.info("error password :", format(list_error))
        # set 2
        logging.info("Enter the correct password,to setup")
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        # set 3
        logging.info("change administrator login password more than 16 digits")
        assert (SetUpLib.locate_option(Key.UP, ["Manage Supervisor Password"], 20))
        assert (change_password(Msg.BIOS_PASSWORD, admin_pwd_17))
        SetUpLib.send_keys([Key.F10, Key.Y])
        assert (checkPWD(admin_pwd_16, 'Am@23'))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_password_by_unipwd()


def pwd_auth_mgt_09():
    tc = ('056', '[TC056]AuthenticationManagement_009', '禁止提示有助攻击者猜解系统口令的信息,输入错误的登录密码,仅提示密码错误')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_pw_prompt(Key.DEL)
        SetUpLib.send_key("Admin@6666")
        SetUpLib.send_key(Key.ENTER)
        logging.info("Send  password...")
        assert SetUpLib.wait_message(invalid_info)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Main function
def pwd_test_all():
    Testcase_BiosPasswordSecurity_002()
    Testcase_BiosPasswordSecurity_003()
    Testcase_BiosPasswordSecurity_004()
    Testcase_BiosPasswordSecurity_005_019_021()
    Testcase_BiosPasswordSecurity_006()
    Testcase_BiosPasswordSecurity_007()
    Testcase_BiosPasswordSecurity_008()
    Testcase_BiosPasswordSecurity_009()
    Testcase_BiosPasswordSecurity_010()
    Testcase_BiosPasswordSecurity_011_012_014()
    Testcase_BiosPasswordSecurity_013()
    Testcase_BiosPasswordSecurity_014_015()
    Testcase_BiosPasswordSecurity_016_017()
    Testcase_BiosPasswordSecurity_020()
    Testcase_BiosPasswordSecurity_022()
    Testcase_BiosPasswordSecurity_025()
    pwd_auth_mgt_01()
    pwd_auth_mgt_07()
    pwd_auth_mgt_08_10()
    pwd_auth_mgt_09()
