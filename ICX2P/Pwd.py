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

from Report import ReportGen
from ICX2P.SutConfig import Key
from ICX2P import SutConfig
from ICX2P.BaseLib import icx2pAPI, SetUpLib,Update
from ICX2P.BaseLib import SerialLib


default_pwd = 'Admin@9000'
new_pwd_7 = '333333'
new_pwd_8 = 'Admin@9!'
new_pwd_9 = 'Admin@9002'
new_pwd_16 = 'Admin@9001Admin@90'
new_pwd_17 = 'Admin@9001Admin@900'
simple_pwd = '11111111'
weak_pwd = 'Huawei@CLOUD8!'
# 新密码为2种字符类型，尝试各种组合（共6种组合）
pwd_list1 = ['ADMIN123', 'admin123', 'admin###', 'ADMIN###', 'ADMINadm', '1234####']
# System will be locked after send wrong pwd 3 times
# 新密码为3种字符类型，尝试各种组合（共4种组合）
pwd_list2 = ['Administrator@', 'admin@123', 'Administrator1', 'ADMIN@123']
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



# after set password, checkin password
def checkPWD(serial, pwd1, pwd2):
    if not icx2pAPI.pressDelnp(serial):
        return
    SetUpLib.send_keys(serial, pwd2)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,invalid_info):

        return
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_keys(serial, SutConfig.default_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,invalid_info):
        return
    SetUpLib.send_key(serial, Key.ENTER)
    time.sleep(1)
    SetUpLib.send_keys(serial, pwd1)
    time.sleep(1)
    SetUpLib.send_key(serial, Key.ENTER)
    SetUpLib.send_keys(serial, [Key.RIGHT, Key.LEFT])
    if not SerialLib.is_msg_present(serial,'Continue'):
        return
    return True


def restore_env(serial, log_dir):

    path = log_dir
    bin_dir = log_dir + "\\output\\"
    # bin_file = os.listdir(path)
    if not os.path.exists(bin_dir):
        logging.info("output no exist")
        Update.get_test_image(log_dir)
    else :
        logging.info("output_file exist")
    if not Update.update_specific_img(log_dir, serial):
        logging.info("restore_env  Failed.")
        return
    return True


def simplePWDTest(serial, ssh):
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
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, default_pwd)
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
    if not SerialLib.is_msg_present(serial, invalid_info):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, SutConfig.default_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_16)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_16)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_4):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial,new_pwd_16,simple_pwd):
        result.log_fail()
        return
    if not restore_env(serial, log_dir):
        return
    result.log_pass()
    return True


def Simple_password_validity(serial, ssh):
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
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, default_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_7)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_7)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, default_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial,simple_pwd)
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
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial,simple_pwd,new_pwd_7):
        result.log_fail()
        return
    if not restore_env(serial, log_dir):
        return
    result.log_pass()
    return True

def Simple_password_disenable(serial, ssh):
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
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, default_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_2):
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
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, simple_pwd, new_pwd_7):
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
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, simple_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_2):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, new_pwd_7)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, pwd_info_3):
        result.log_fail()
    SetUpLib.send_keys(serial, new_pwd_7)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, invalid_info):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    time.sleep(1)
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
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, new_pwd_9, new_pwd_7):
        result.log_fail()
        return
    if not restore_env(serial, log_dir):
        return
    result.log_pass()
    return True


def Simple_password_save_enable(serial, ssh):
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
    #以上，为前置条件-简易密码开关打开#
    if not SetUpLib.locate_option(serial, Key.UP, ["Manage Supervisor Password"], 20):
        result.log_fail()
        return
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_1):
        result.log_fail()
        return
    SetUpLib.send_keys(serial, default_pwd)
    SetUpLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial,pwd_info_2):
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
    serial.send_keys(Key.F10 + Key.Y)
    if not checkPWD(serial, simple_pwd, ""):
        result.log_fail()
        return
    SetUpLib.send_key(serial,Key.CTRL_ALT_DELETE)
    if not checkPWD(serial, simple_pwd, new_pwd_16):
        result.log_fail()
        return
    SetUpLib.send_key(serial,Key.CTRL_ALT_DELETE)
    if not checkPWD(serial, simple_pwd, new_pwd_9):
        result.log_fail()
        return
    if not restore_env(serial, log_dir):
        return
    result.log_pass()
    return True