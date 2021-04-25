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
import unittest
from Core import SerialLib, SshLib
from Report import ReportGen
from ICX2P.SutConfig import Key, Msg
from ICX2P import SutConfig
from ICX2P.BaseLib import icx2pAPI, SetUpLib, Update, PowerLib

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
log_dir = SutConfig.LOG_DIR


# change password
# OnStart:光标停留在"Manage Supervisor Password"
# OnComplete: 修改密码成功, 光标停留在"Manage Supervisor Password"
def change_password(serial, old_password, new_password):
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_1):
        return
    SerialLib.send_data(serial, old_password)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_2):
        return
    SerialLib.send_data(serial, new_password)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        return
    SerialLib.send_data(serial, new_password)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_4):
        return
    SerialLib.send_key(serial, Key.ENTER)
    logging.info("Password is changed from {0} to {1}".format(old_password, new_password))
    return True


# change password
# OnStart:光标停留在"Manage Supervisor Password"
# OnComplete: 修改密码失败, 光标停留在"Manage Supervisor Password"
def change_password_negtive(serial, old_password, new_password):
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_1):
        return
    SerialLib.send_data(serial, old_password)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_2):
        return
    SerialLib.send_data(serial, new_password)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        return
    SerialLib.send_data(serial, new_password)
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SerialLib.send_key(serial, Key.ENTER)
    logging.info("Password change to: {0} is rejected".format(new_password))
    return True


# after set password, checkin password
def checkPWD(serial, pwd1, pwd2):
    if not icx2pAPI.pressDelnp(serial):
        return
    SetUpLib.send_keys(serial, pwd2)
    logging.info("check_password_2")
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_keys(serial, SutConfig.BIOS_PASSWORD)
    logging.info("check_password_BIOS_PASSWORD")
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    time.sleep(1)
    SetUpLib.send_keys(serial, pwd1)
    logging.info("check_password_1 ")
    time.sleep(1)
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_keys(serial, [Key.RIGHT, Key.LEFT])
    if not SerialLib.is_msg_present(serial, 'Continue'):
        return
    return True


def restore_env(serial, ssh_bmc, log_dir):
    path = log_dir
    bin_dir = path + "\\output\\"
    # bin_file = os.listdir(path)
    if not os.path.exists(bin_dir):
        logging.info("output no exist")
        Update.get_test_image(log_dir, 'master', 'debug-build')

    else:
        logging.info("output_file exist")
    if not Update.update_specific_img(log_dir, serial, ssh_bmc):
        logging.info("restore_env  Failed.")
        return
    return True


# 用于新密码机制，外部unipwd工具修改为Admin@909密码
def reset_password_by_unipwd(serial, ssh_bmc, ssh_os):
    icx2pAPI.clearCMOS(ssh_bmc)
    logging.info("Modify PWD to SutConfig.BIOS_PW by unipwd tool")
    if not PowerLib.force_reset(ssh_bmc):
        logging.info("Boot to boot manager fail.")
        return restore_env(serial, ssh_bmc, log_dir)
    if not icx2pAPI.ping_sut():
        logging.info("Ping SUT fail.")
        return restore_env(serial, ssh_bmc, log_dir)
    SshLib.execute_command(ssh_os, r'cd {0};insmod ufudev.ko'.format(SutConfig.UNI_PATH))
    res = SshLib.execute_command(ssh_os,
                                 r'cd {0};./unipwd -set {1}'.format(SutConfig.UNI_PATH, SutConfig.BIOS_PASSWORD))
    logging.info(res)
    if len(res) == 0:
        logging.info('blank, maybe the ko module failed')
        return restore_env(serial, ssh_bmc, log_dir)
    elif 'error' in res:
        logging.info("Modify BIOS PWD:Fail")
        return restore_env(serial, ssh_bmc, log_dir)
    else:
        logging.info('Rebooting the SUT...')
        SshLib.execute_command(ssh_os, 'reboot')
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE):
        return
    logging.info("Modify BIOS PWD:Pass")
    return True


def simplePWDTest(serial, ssh, ssh_os):
    tc = ('031', 'PasswordSecurity_01', ' 简易密码开关默认值测试，密码开关为初始状态')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.key2pwd)
    # #checkin "Simple Password"  Default value "Disabled"
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Simple Password", "<Disabled>"], 20):
        result.log_fail()
        return
    logging.info("Simple Password   <Disabled> ")
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return

    if not change_password_negtive(serial, SutConfig.BIOS_PASSWORD, '11111111'):
        result.log_fail()
        return
    time.sleep(1)
    if not change_password(serial, SutConfig.BIOS_PASSWORD, 'Admin@9001Admin@'):
        result.log_fail()
        return
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, 'Admin@9001Admin@', '11111111'):
        result.log_fail()
        return
    if not reset_password_by_unipwd(serial, ssh, ssh_os):
        restore_env(serial, ssh, log_dir)
        return
    result.log_pass()
    return True


def Simple_password_validity(serial, ssh, ssh_os):
    tc = ('032', 'PasswordSecurity_02', '简易密码开关打开,修改密码为简易密码,简易密码有效性测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.key2pwd)
    # #checkin "Simple Password"  Default value "Disabled"
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Simple Password", "<Disabled>"], 20):
        result.log_fail()
        return
    logging.info("Simple Password   <Disabled> ")
    serial.send_keys(Key.F5)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return
    if not change_password_negtive(serial, SutConfig.BIOS_PASSWORD, '333333'):
        result.log_fail()
        return
    time.sleep(1)
    if not change_password(serial, SutConfig.BIOS_PASSWORD, '22222222'):
        result.log_fail()
        return
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, '22222222', '333333'):
        result.log_fail()
        return
    if not reset_password_by_unipwd(serial, ssh, ssh_os):
        restore_env(serial, ssh, log_dir)
        return
    result.log_pass()
    return True


def Simple_password_disenable(serial, ssh, ssh_os):  # 异常待处理
    tc = ('033', 'PasswordSecurity_03', '设置简易密码并保存后，再次关闭简易密码开关测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.key2pwd)
    # #checkin "Simple Password"  Default value "Disabled"
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Simple Password", "<Disabled>"], 20):
        result.log_fail()
        return
    logging.info("Simple Password   <Enabled> ")
    serial.send_keys(Key.F5)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return
    """
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.BIOS_PASSWORD)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, simple_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, simple_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_4):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    """
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, '44444444', '333333'):
        result.log_fail()
    ###以上，是此用例的前置条件##############
    SetUpLib.send_keys(serial, SutConfig.key2Setup)
    SetUpLib.send_keys(serial, SutConfig.key2pwd)
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Simple Password", "<Enabled>"], 20):
        result.log_fail()
        return
    serial.send_keys(Key.F6)

    logging.info("Simple Password   <Disabled> ")
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return
    """
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, simple_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_7)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, " confirm ",5):
        logging.info('**confirm 找不到 ,显示这个提示**')
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_7)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    """
    if not change_password_negtive(serial, '44444444', '555555'):
        result.log_fail()
        return
    time.sleep(1)
    """
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, simple_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_9)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        result.log_fail()
    SetUpLib.send_keys(serial, new_pwd_9)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_4):
        result.log_fail()
    SetUpLib.send_key(serial, Key.ENTER)
    """
    if not change_password(serial, '44444444', 'Admin@9002'):
        result.log_fail()
        return
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, 'Admin@9002', '555555'):
        result.log_fail()
        return
    if not reset_password_by_unipwd(serial, ssh, ssh_os):
        restore_env(serial, ssh, log_dir)
        return
    result.log_pass()
    return True


def Simple_password_save_enable(serial, ssh, ssh_os):
    tc = ('034', 'PasswordSecurity_04', '简易密码开关打开，设置简易密码后保存生效测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.key2pwd)
    # #checkin "Simple Password"  Default value "Disabled"
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Simple Password", "<Disabled>"], 20):
        result.log_fail()
        return
    logging.info("Simple Password   <Enabled> ")
    serial.send_keys(Key.F5)
    SetUpLib.send_key(serial, Key.ENTER)
    # 以上，为前置条件-简易密码开关打开#
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return
    if not change_password(serial, SutConfig.BIOS_PASSWORD, '55555555'):
        result.log_fail()
        return
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, '55555555', ""):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
    if not checkPWD(serial, '55555555', 'Admin@9001Admin@'):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
    if not checkPWD(serial, '55555555', 'Admin@9002'):
        result.log_fail()
        return
    if not reset_password_by_unipwd(serial, ssh, ssh_os):
        restore_env(serial, ssh, log_dir)
        return
    result.log_pass()
    return True


def Simple_password_save_disable(serial, ssh, ssh_os):
    tc = ('035', 'PasswordSecurity_05', '简易密码开关打开，设置简易密码后不保存退出')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.key2pwd)
    # #checkin "Simple Password"  Default value "Disabled"
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Simple Password", "<Disabled>"], 20):
        result.log_fail()
        return
    logging.info("Simple Password   <Enabled> ")
    serial.send_keys(Key.F5)
    SetUpLib.send_key(serial, Key.ENTER)
    # 以上，为前置条件-简易密码开关打开#
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return
    if not change_password(serial, SutConfig.BIOS_PASSWORD, '66666666'):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
    if not icx2pAPI.pressDelnp(serial):
        return
    SetUpLib.send_keys(serial, "")
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_keys(serial, 'Admin@9001Admin@')
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_keys(serial, '333333')
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
    if not icx2pAPI.pressDelnp(serial):
        return
    SetUpLib.send_keys(serial, '11111111')
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not reset_password_by_unipwd(serial, ssh, ssh_os):
        restore_env(serial, ssh, log_dir)
        return
    result.log_pass()
    return True


class PWD_BiosPasswordSecurity(unittest.TestCase):

    def Testcase_BiosPasswordSecurity_002(self, serial, ssh, ssh_os):
        tc = ('036', 'Testcase_BiosPasswordSecurity_002', '设置密码长度测试_密码长度小于最少字符数，修改失败测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password_negtive(serial, SutConfig.BIOS_PASSWORD, 'Ad@90'))
            logging.info("show invalid_password")
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_003(self, serial, ssh, ssh_os):
        tc = ('037', 'Testcase_BiosPasswordSecurity_003', '设置密码长度度测试_密码长度等于最少字符数，修改成功测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password(serial, SutConfig.BIOS_PASSWORD, 'Admin@9!'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            logging.info("Changes have been saved after press")
            self.assertTrue(checkPWD(serial, 'Admin@9!', '11111111'))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_004(self, serial, ssh, ssh_os):
        tc = ('038', 'Testcase_BiosPasswordSecurity_004', '设置密码长度测试_密码长度大于最少字符数，小于最大字符数，修改成功测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password(serial, SutConfig.BIOS_PASSWORD, 'Admin@9003'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            logging.info("Changes have been saved after press")
            self.assertTrue(checkPWD(serial, 'Admin@9003', '11111111'))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_005_019_021(self, serial, ssh, ssh_os):
        tc = (
            '039', 'Testcase_BiosPasswordSecurity_005_019_021',
            '设置密码长度度测试_密码长度最大字符数，修改成功测试；密码修改时要验证旧密码测试；新密码需要再次输入确认测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password(serial, SutConfig.BIOS_PASSWORD, 'Admin@9001Admin@'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            logging.info("Changes have been saved after press")
            self.assertTrue(checkPWD(serial, 'Admin@9001Admin@', '11111111'))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_006(self, serial, ssh, ssh_os):
        tc = ('040', 'Testcase_BiosPasswordSecurity_006', '设置密码长度测试_密码长度超出最大字符数,修改失败测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 10))
            self.assertTrue(change_password(serial, SutConfig.BIOS_PASSWORD, 'Byosoft@5000soft'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            logging.info("Changes have been saved after press")
            self.assertTrue(checkPWD(serial, 'Byosoft@5000soft', '11111111'))
            # 超出最大字符
            logging.info("Maximum characters exceeded")
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 10))
            self.assertTrue(change_password(serial, 'Byosoft@5000soft', 'Inter@8000Byosof4'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            logging.info("Changes have been saved after press")
            self.assertTrue(checkPWD(serial, 'Inter@8000Byosof', 'Byosoft@5000soft'))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_007(self, serial, ssh, ssh_os):
        tc = ('041', 'Testcase_BiosPasswordSecurity_007', '设置密码字符类型测试_只有1种字符类型密码测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            for i in pwd_list:
                try:
                    self.assertTrue(change_password_negtive(serial, SutConfig.BIOS_PASSWORD, i))
                except:
                    logging.info("eorro password :", format(i))
            SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_008(self, serial, ssh, ssh_os):
        tc = ('042', 'Testcase_BiosPasswordSecurity_008', '设置密码字符类型测试_2种字符类型密码测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            for j in pwd_list1:
                try:
                    self.assertTrue(change_password_negtive(serial, SutConfig.BIOS_PASSWORD, j))
                except:
                    logging.info("error password :", format(j))
            SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_009(self, serial, ssh, ssh_os):
        tc = ('043', 'Testcase_BiosPasswordSecurity_009', '设置密码字符类型测试_3种字符类型密码测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            k = 0
            while k < len(pwd_list2) - 1:
                m = k + 1
                self.assertTrue(icx2pAPI.toBIOSConf(serial))
                SetUpLib.send_keys(serial, SutConfig.key2pwd)
                self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
                SetUpLib.send_key(serial, Key.ENTER)
                self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_1))
                SerialLib.send_data(serial, pwd_list2[k])
                logging.info("input default_pwd")
                SetUpLib.send_key(serial, Key.ENTER)
                self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_2))
                SerialLib.send_data(serial, pwd_list2[m])
                logging.info("input new_pwd")
                SetUpLib.send_key(serial, Key.ENTER)
                self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_3))
                SerialLib.send_data(serial, pwd_list2[m])
                logging.info("confirm new_pwd")
                SetUpLib.send_key(serial, Key.ENTER)
                # 满足密码测试用例规则
                if pwd_list2[m] != 'Administrator1':
                    logging.info("Meet the password test case rules")
                    self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_4))
                    SetUpLib.send_key(serial, Key.ENTER)
                    SetUpLib.send_keys(serial, [Key.F10, Key.Y])
                    self.assertTrue(checkPWD(serial, pwd_list2[m], pwd_list2[k]))
                # 不满足密码测试用例规则
                else:
                    logging.info("Does not meet the password test case rules")
                    self.assertTrue(SerialLib.is_msg_present(serial, invalid_info))
                    logging.info("show invalid_password")
                    SetUpLib.send_key(serial, Key.ENTER)
                    SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
                    self.assertTrue(checkPWD(serial, pwd_list2[k], pwd_list2[m]))
                k = k + 1
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_010(self, serial, ssh, ssh_os):
        tc = ('044', 'Testcase_BiosPasswordSecurity_010', '设置密码字符类型测试_4种字符类型密码')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password(serial, SutConfig.BIOS_PASSWORD, 'Admin@6789'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            logging.info("Changes have been saved after press")
            self.assertTrue(checkPWD(serial, 'Admin@6789', 'Admin6789admin'))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_011_012_014(self, serial, ssh):
        tc = (
        '045', 'Testcase_BiosPasswordSecurity_011,012,014', '输入错误密码次3次内，提示报错，并可以再次输入测试；输错3次后不允许再输入密码测试；输入错误密码超出阈值测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        pwd_error = ['Admin@7890', 'Ad@90', '555555']
        try:
            self.assertTrue(PowerLib.force_reset(ssh))
            logging.info("Booting to setup")
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            SetUpLib.send_key(serial, Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=60))
            for list_error in pwd_error:
                try:
                    SerialLib.send_data(serial, list_error)
                    SetUpLib.send_key(serial, Key.ENTER)
                    logging.info("Send  password...")
                    if list_error != pwd_error[-1]:
                        self.assertTrue(serial.waitString(invalid_info))
                        time.sleep(2)
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString('Enter Current Password'))
                        logging.info("input password again")
                    else:
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString(error_info))
                        logging.info("Enter incorrect password 3 times,System Locked")
                except:
                    logging.info("eorro password :", format(list_error))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_013(self, serial, ssh, ssh_os):
        tc = ('046', 'Testcase_BiosPasswordSecurity_013', '输入错误密码次数测试_阈值内连续输入错误密码后输入正确密码测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        pwd_error = ['Admin@9876', 'Da@89', SutConfig.BIOS_PASSWORD]
        try:
            self.assertTrue(PowerLib.force_reset(ssh))
            logging.info("Booting to setup")
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            SetUpLib.send_key(serial, Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=10))
            for list_error in pwd_error:
                try:
                    SerialLib.send_data(serial, list_error)
                    logging.info("Send password...")
                    SetUpLib.send_key(serial, Key.ENTER)
                    if list_error != pwd_error[-1]:
                        self.assertTrue(serial.waitString(invalid_info, timeout=10))
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString(SutConfig.Msg.PW_PROMPT, timeout=10))
                        logging.info("input password again")
                    else:
                        # self.assertTrue(serial.waitString(SutConfig.pwd_info))
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString('Continue', timeout=60))
                        logging.info("Booting to setup successfully")
                except:
                    logging.info("eorro password :", format(list_error))
                    return
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_014_015(self, serial, ssh):
        tc = ('047', 'Testcase_BiosPasswordSecurity_014_015', '输入错误密码次数测试_超出阈值锁定输入界面，提示报错、并提示复位；超出阈值重启后不影响下一次登录')
        result = ReportGen.LogHeaderResult(tc, serial)
        pwd_error = ['Admin@3456', 'Qa@12', '222222']
        try:
            self.assertTrue(PowerLib.force_reset(ssh))
            logging.info("Booting to setup")
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            SetUpLib.send_key(serial, Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=60))
            for list_error in pwd_error:
                try:
                    SerialLib.send_data(serial, list_error)
                    SetUpLib.send_key(serial, Key.ENTER)
                    logging.info("Send  password...")
                    if list_error != pwd_error[-1]:
                        self.assertTrue(serial.waitString(invalid_info))
                        time.sleep(1)
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString('Enter Current Password'))
                        logging.info("input password again")
                    else:
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString(error_info))
                        logging.info("Enter incorrect password 3 times,System Locked")
                except:
                    logging.info("eorro password :", format(list_error))
                    return
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_016_017(self, serial, ssh):
        tc = ('048', 'Testcase_BiosPasswordSecurity_016', '密码不能明文显示_不显示或用*代替字符测试;任意密码不显示或用*代替字符测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(PowerLib.force_reset(ssh))
            logging.info("Booting to setup")
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            SetUpLib.send_key(serial, Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=10))
            SerialLib.send_data(serial, SutConfig.BIOS_PW_DEFAULT)
            time.sleep(1)
            try:
                result.capture_screen()
                logging.info('get pic pass')
            except:
                logging.info('get pic fail')
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_020(self, serial, ssh):
        tc = ('049', 'Testcase_BiosPasswordSecurity_020', '密码修改验证旧密码测试_输入错误旧密码，不能修改密码')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_1))
            SetUpLib.send_key(serial, 'Inter#9999')
            logging.info("input error password")
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, invalid_info))
            logging.info("show invalid_password")
            SetUpLib.send_key(serial, Key.ENTER)
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_022(self, serial, ssh, ssh_os):
        tc = ('050', 'Testcase_BiosPasswordSecurity_022', '密码修改验证新密码测试_新密码确认时，输入错误新密码，修改失败测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_1))
            SetUpLib.send_key(serial, SutConfig.BIOS_PASSWORD)
            logging.info("input default_pwd")
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_2))
            SetUpLib.send_key(serial, "Admin@9999")
            logging.info("input new_pwd")
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_3))
            SetUpLib.send_key(serial, "Admin@9998")
            logging.info("input error confirm new_pwd")
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, 'Passwords are not the same'))
            SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_025(self, serial, ssh, ssh_os):
        tc = ('051', 'Testcase_BiosPasswordSecurity_025', '历史密码5次范围内重复修改无效,超过5次后可以修改为5次前的密码测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        times_pwd = ['Admin@9009', 'Admin@9010', 'Admin@9012', 'Admin@9013', 'Admin@9014', 'Admin@9009', 'Admin@9015']
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            k = 0
            while k < len(times_pwd) - 2:
                m = k + 1
                self.assertTrue(icx2pAPI.toBIOSConf(serial))
                SetUpLib.send_keys(serial, SutConfig.key2pwd)
                self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
                SetUpLib.send_key(serial, Key.ENTER)
                self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_1))
                serial.send_data(times_pwd[k])
                logging.info("input default_pwd")
                SetUpLib.send_key(serial, Key.ENTER)
                self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_2))
                serial.send_data(times_pwd[m])
                logging.info("input new_pwd")
                SetUpLib.send_key(serial, Key.ENTER)
                self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_3))
                serial.send_data(times_pwd[m])
                logging.info("confirm new_pwd")
                SetUpLib.send_key(serial, Key.ENTER)
                if times_pwd[m] != "Admin@9009":
                    logging.info("Password changed successfully")
                    self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_4))
                    SetUpLib.send_key(serial, Key.ENTER)
                    SetUpLib.send_keys(serial, [Key.F10, Key.Y])
                    self.assertTrue(checkPWD(serial, times_pwd[m], times_pwd[k]))
                else:
                    logging.info("Password changed Failed")
                    self.assertTrue(SerialLib.is_msg_present(serial, invalid_info))
                    logging.info("use old pwd,invalid.")
                    SetUpLib.send_key(serial, Key.ENTER)
                    SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
                    self.assertTrue(checkPWD(serial, times_pwd[k], times_pwd[m]))
                k = k + 1
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password(serial, times_pwd[4], times_pwd[6]))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            self.assertTrue(checkPWD(serial, times_pwd[6], times_pwd[4]))
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def Testcase_BiosPasswordSecurity_028(self, serial, ssh, ssh_os):
        tc = ('052', 'Testcase_BiosPasswordSecurity_028', '开启OS引导时,弹出密码输入框,需要输入管理员密码测试')
        result = ReportGen.LogHeaderResult(tc, serial)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Power On Password", "<Disabled>"], 20))
            SetUpLib.send_keys(serial,[Key.F5,Key.F10, Key.Y])
            logging.info("set Power on Password Enable")
            self.assertTrue(SerialLib.is_msg_present(serial, 'Enter Current Password:'))
            SerialLib.send_data(serial, SutConfig.BIOS_PASSWORD)
            SetUpLib.send_key(serial, Key.ENTER)
            logging.info("reboot ,input BIOS_PASSWORD ")
            time.sleep(30)
            self.assertTrue(icx2pAPI.ping_sut())
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
            logging.info("正常恢复")
        except AssertionError as err:
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
            logging.info("异常恢复")
            result.log_fail()
            return False
        result.log_pass()

# 02 认证管理
class PWD_AUTH_MANAGERMENT(unittest.TestCase):

    def pwd_auth_mgt_01(self, serial, ssh):
        tc = ('600', 'Testcase_AuthenticationManagement_001', '热键页面遍历热键，检查进入Setup菜单是否需要输入密码')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        hot_key = [Key.DEL, Key.F11, Key.F12, Key.F6]
        try:
            for hk in hot_key:
                self.assertTrue(PowerLib.force_reset(ssh))
                self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
                logging.info("Rebooting SUT")
                try:
                    SetUpLib.send_key(serial, hk)
                    self.assertTrue(serial.waitString('Enter Current Password'))
                except:
                    logging.info("error key :", format(hk))
                    return
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def pwd_auth_mgt_07(self, serial, ssh, ssh_os):
        tc = ('601', 'Testcase_AuthenticationManagement_007', '禁止提供自动登录等特殊功能')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def pwd_auth_mgt_08_10(self, serial, ssh, ssh_os):
        tc = ('602', 'Testcase_AuthenticationManagement_008_010',
              '管理员登录密码大于16位字符无法输入,普通用户登录密码大于16位无法输入;修改管理员密码界面需要先输入旧密码，再输入两次新密码')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        pwd_error = ['Admin@3456', 'Pw@99', '666666']
        try:
            self.assertTrue(PowerLib.force_reset(ssh))
            logging.info("Booting to setup")
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            SetUpLib.send_key(serial, Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=60))
            logging.info("input 3 times error pwd,System Locked")
            for list_error in pwd_error:
                try:
                    SerialLib.send_data(serial, list_error)
                    SetUpLib.send_key(serial, Key.ENTER)
                    logging.info("Send  password...")
                    if list_error != pwd_error[-1]:
                        self.assertTrue(serial.waitString(invalid_info))
                        time.sleep(2)
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString('Enter Current Password'))
                        logging.info("input password again")
                    else:
                        SetUpLib.send_key(serial, Key.ENTER)
                        self.assertTrue(serial.waitString(error_info))
                        logging.info("Enter incorrect password 3 times,System Locked")
                except:
                    logging.info("error password :", format(list_error))
            # set 2
            logging.info("Enter the correct password,to setup")
            SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            # set 3
            logging.info("change administrator login password more than 16 digits")
            self.assertTrue(SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20))
            self.assertTrue(change_password(serial, SutConfig.BIOS_PASSWORD, 'Admin@6789byosoft'))
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            self.assertTrue(checkPWD(serial, 'Admin@6789byosof', 'Am@23'))
            # set 4 前置条件
            logging.info("Set step 4 preconditions")
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            self.assertTrue(SetUpLib.locate_option(serial, Key.DOWN, ["Manage User Password"], 5))
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_2))
            SerialLib.send_data(serial, 'Inter@4567')
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_3))
            SerialLib.send_data(serial, 'Inter@4567')
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, pwd_info_4))
            SetUpLib.send_key(serial, Key.ENTER)
            SetUpLib.send_keys(serial, [Key.F10, Key.Y])
            # set 4
            logging.info("Enter the correct login password for ordinary users and log in to the setup menu")
            SetUpLib.send_key(serial, Key.CTRL_ALT_DELETE)
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            SetUpLib.send_key(serial, Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=10))
            SerialLib.send_data(serial, 'Inter@4567')
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(serial.waitString(SutConfig.pwd_info))
            SetUpLib.send_key(serial, Key.ENTER)
            # set 5
            logging.info("Modify the login password of ordinary users with more than 16 digits")
            SetUpLib.send_keys(serial, [Key.RIGHT, Key.ENTER])
            SetUpLib.send_keys(serial, SutConfig.key2pwd)
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, "Enter New Password:"))
            SerialLib.send_data(serial, 'Inter@4567byosoft')
            logging.info('input User_Password ')
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(SerialLib.is_msg_present(serial, invalid_info))
            SetUpLib.send_key(serial, Key.ENTER)
            self.assertTrue(reset_password_by_unipwd(serial, ssh, ssh_os))
        except AssertionError as err:
            reset_password_by_unipwd(serial, ssh, ssh_os)
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def pwd_auth_mgt_09(self, serial, ssh):
        tc = ('603', 'Testcase_AuthenticationManagement_009', '禁止提示有助攻击者猜解系统口令的信息,输入错误的登录密码,仅提示密码错误')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(PowerLib.force_reset(ssh))
            logging.info("Booting to setup")
            self.assertTrue(serial.waitString(SutConfig.Msg.HOTKEY_PROMPT_DEL, timeout=600))
            serial.send_keys(Key.DEL)
            logging.info("Hot Key sent")
            self.assertTrue(serial.waitString(SutConfig.press_f2, timeout=60))
            SetUpLib.send_key(serial, "Admin@6666")
            SetUpLib.send_key(serial, Key.ENTER)
            logging.info("Send  password...")
            self.assertTrue(serial.waitString(invalid_info))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()


PWDAUTHMGT = PWD_AUTH_MANAGERMENT()
PBPWS = PWD_BiosPasswordSecurity()


# Main function
def Pwd_test(ser, ssh_bmc, ssh_os):
    simplePWDTest(ser, ssh_bmc, ssh_os)
    Simple_password_validity(ser, ssh_bmc, ssh_os)
    # Simple_password_disenable(ser, ssh_bmc, ssh_os)
    Simple_password_save_enable(ser, ssh_bmc, ssh_os)
    Simple_password_save_disable(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_002(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_003(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_004(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_005_019_021(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_006(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_007(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_008(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_009(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_010(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_011_012_014(ser, ssh_bmc)
    PBPWS.Testcase_BiosPasswordSecurity_013(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_014_015(ser, ssh_bmc)
    PBPWS.Testcase_BiosPasswordSecurity_016_017(ser, ssh_bmc)
    PBPWS.Testcase_BiosPasswordSecurity_020(ser, ssh_bmc)
    PBPWS.Testcase_BiosPasswordSecurity_022(ser, ssh_bmc, ssh_os)
    PBPWS.Testcase_BiosPasswordSecurity_025(ser, ssh_bmc, ssh_os)
    PWDAUTHMGT.pwd_auth_mgt_01(ser, ssh_bmc)
    PWDAUTHMGT.pwd_auth_mgt_07(ser, ssh_bmc, ssh_os)
    PWDAUTHMGT.pwd_auth_mgt_08_10(ser, ssh_bmc, ssh_os)
    PWDAUTHMGT.pwd_auth_mgt_09(ser, ssh_bmc)
