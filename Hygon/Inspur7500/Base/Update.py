#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import datetime
import requests
import re
import os
import time
import shutil
import zipfile
import subprocess
import logging
from bs4 import BeautifulSoup
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from Inspur7500.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



def _get_options_value():
    time.sleep(1)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED_CN)
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Msg.PAGE_MAIN_CN,5)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    options = []
    try_counts=12
    while try_counts:
        SetUpLib.close_session()  # 关闭连接
        time.sleep(1)
        SetUpLib.open_session()  # 打开连接
        time.sleep(1)
        data = SetUpLib.get_data(2, Key.RIGHT)
        options = options + re.findall(r'<.*?> {2,}\w[\w \-/]*? {2}|\[\d+\] {2,}\w[\w \-/]*? {2}', data)
        if SutConfig.Msg.PAGE_MAIN_CN in data:
            break
        try_counts-=1
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.LOC_PCIE_INFO,10)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    options = options + re.findall(r'<.*?> {2,}\w[\w \-/]*? {2}', SetUpLib.get_data(2))


    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Upd.LOC_CONSOLE,10)
    for option in SutConfig.Upd.LOC_PART1:
        if not SetUpLib.locate_option(Key.DOWN,[option],18):
            SetUpLib.locate_option(Key.UP, [option], 18)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(1)
        SetUpLib.open_session()  # 打开链接
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        options = options + re.findall(r'<[a-zA-Z0-9].*?> {2,}\w[\w \-/]*? {2}', SetUpLib.get_data(2))
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)

    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.LOC_USB_PORT, 10)
    for option in SutConfig.Upd.LOC_PART2:
        if not SetUpLib.locate_option(Key.DOWN, [option], 18):
            SetUpLib.locate_option(Key.UP, [option], 18)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(1)
        SetUpLib.open_session()  # 打开链接
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        options = options + re.findall(r'<.*?> {2,}\w[\w \-/]*? {2}', SetUpLib.get_data(2))
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)


    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.LOC_HYGON, 10)
    for option in SutConfig.Upd.LOC_PART3:
        if not SetUpLib.locate_option(Key.DOWN,[option],18):
            SetUpLib.locate_option(Key.UP, [option], 18)
        SetUpLib.close_session()  # 关闭连接
        time.sleep(1)
        SetUpLib.open_session()  # 打开链接
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        options = options + re.findall(r'<.*?> {2,}\w[\w \-/]*? {2}', SetUpLib.get_data(2))
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
    return [i.replace(' ', '') for i in options]



def _change_options_value_part1():
    SetUpLib.close_session()#关闭连接
    time.sleep(2)
    SetUpLib.open_session()#打开链接
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN,SutConfig.Upd.CHANGE_PART1,25)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    return True



def _change_options_value_part2():
    SetUpLib.close_session()#关闭连接
    time.sleep(2)
    SetUpLib.open_session()#打开链接
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN,SutConfig.Upd.CHANGE_PART2,25)
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    return True



def _change_options_value_part3():
    SetUpLib.close_session()#关闭连接
    time.sleep(2)
    SetUpLib.open_session()#打开链接
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN,SutConfig.Upd.CHANGE_PART3_2,10)
    time.sleep(2)
    return True



def set_password(admin=SutConfig.Upd.PASSWORDS[0],users=SutConfig.Upd.PASSWORDS[1]):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Msg.PAGE_SECURITY_CN,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(admin)
    time.sleep(1)
    SetUpLib.send_data(admin)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS,5):
        logging.info('管理员密码{0}设置成功'.format(admin))
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.SET_USER_PSW,10)
    time.sleep(1)
    SetUpLib.send_data_enter(users)
    time.sleep(1)
    SetUpLib.send_data(users)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 3):
        logging.info('用户密码{0}设置成功'.format(users))
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)

    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.POWER_ON_PSW_OPTION], 5, 'Disabled')
    time.sleep(1)

    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



def _go_to_setup(password=SutConfig.Upd.PASSWORDS[0],users=SutConfig.Upd.PASSWORDS[1]):
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    try_counts = 2
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.HOTKEY_PROMPT_DEL_CN):
            logging.info("Press Del failed, will try again.")
            BmcLib.power_cycle()
            try_counts -= 1

        else:
            time.sleep(1)
            SetUpLib.send_data(password)
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN_CN, 15):
                logging.info("SetUpLib: Boot to setup main page successfully")
                return True
    time.sleep(10)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_data(password)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS,5):
        logging.info('管理员密码{0}设置成功'.format(password))
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 10)
    time.sleep(1)
    SetUpLib.send_data_enter(users)
    time.sleep(1)
    SetUpLib.send_data(users)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS, 3):
        logging.info('用户密码{0}设置成功'.format(users))
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED_CN)
    return False



def del_password(password=SutConfig.Upd.PASSWORDS[0]):
    _go_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Msg.PAGE_SECURITY_CN,10)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS,3):
        logging.info('密码删除')
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



def setup_upgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower()=='all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_NOR,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Msg.PAGE_EXIT_CN,18)
    if bios_mode.lower()=='latest':
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Upd.SETUP_LATEST,15,'Confirmation')
    elif bios_mode.lower()=='previous':
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Upd.SETUP_PREVIOUS,15,'Confirmation')
    elif bios_mode.lower()=='constant':
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Upd.SETUP_CONSTANT,15,'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG,300):
        logging.info('BIOS 刷新成功')

    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Msg.PAGE_SECURITY_CN,10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项值{0}'.format(updated_options))
    logging.info('改变后的选项值{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def setup_upgrade_all(bios_mode,change_part):
    count = 0
    num=0
    _go_to_setup()
    time.sleep(3)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower()=='all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_ALL,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')


    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data=SetUpLib.get_data(2)
        if re.search('Set User Password *Installed',data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('SetUp下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def setup_downgrade_normal(bios_mode,change_part):
    count = 0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_NOR,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')

    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项值{0}'.format(updated_options))
    logging.info('改变后的选项值{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def setup_downgrade_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower()=='all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_ALL,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')


    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('SetUp下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def setup_keep_normal(bios_mode,change_part):
    count = 0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_NOR,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')

    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项值{0}'.format(updated_options))
    logging.info('改变后的选项值{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def setup_keep_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower()=='all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower()=='three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_ALL,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')


    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
        arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]
    if updated_options == default_options:
        logging.info('SetUp下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def dos_upgrade_normal(bios_mode,change_part):
    count = 0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)

    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = _get_options_value()
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Ipm.LEGACY_USB_MSG)
    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower()=='latest':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower()=='previous':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower()=='constant':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_NOR, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(3)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项值{0}'.format(updated_options))
    logging.info('改变后的选项值{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('DOS下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('DOS下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def dos_upgrade_all(bios_mode,change_part):
    count = 0
    num=0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                          SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                              SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)
    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_ALL, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(3)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status=='always-off' and '<{0}>RestoreACPowerLoss'.format(SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ','')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status=='previous' and '<{0}>RestoreACPowerLoss'.format(SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ','')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status,[i for i in updated_options if re.search('RestoreACPowerLoss', i)]))
        num+=1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]
    if updated_options == default_options:
        logging.info('DOS下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num==0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('DOS下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num==0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def dos_downgrade_normal(bios_mode,change_part):
    count = 0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = _get_options_value()
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                          SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                              SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)
    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower()=='latest':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower()=='previous':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower()=='constant':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_NOR, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(3)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项值{0}'.format(updated_options))
    logging.info('改变后的选项值{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('DOS下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('DOS下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def dos_downgrade_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Upd.CHANGE_PART3_1, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                          SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                              SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)
    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_ALL, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(3)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]
    if updated_options == default_options:
        logging.info('DOS下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('DOS下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def dos_keep_normal(bios_mode,change_part):
    count = 0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = _get_options_value()
    BmcLib.init_sut()
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                          SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                              SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)
    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower()=='latest':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower()=='previous':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower()=='constant':
        cmd='{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_NOR, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(3)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项值{0}'.format(updated_options))
    logging.info('改变后的选项值{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('DOS下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('DOS下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def dos_keep_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                          SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                              SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)
    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_ALL, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(3)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('DOS下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('DOS下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def shell_upgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()

        assert _change_options_value_part2()

        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                     SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20,
                                       SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Shell下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Shell下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def shell_upgrade_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Upd.CHANGE_PART3_1, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()

        assert _change_options_value_part2()

        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("CLOSE_VIRTU Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower()=='latest':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower()=='previous':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower()=='constant':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info("Update BIOS in Shell successed.")
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('SHELL下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SHELL下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def shell_downgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()

        assert _change_options_value_part2()

        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                     SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20,
                                       SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Shell下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Shell下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def shell_downgrade_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()

        assert _change_options_value_part2()

        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower()=='latest':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower()=='previous':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower()=='constant':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info("Update BIOS in Shell successed.")
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))

    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('SHELL下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SHELL下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def shell_keep_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()

        assert _change_options_value_part2()

        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                     SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20,
                                       SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Shell下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Shell下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def shell_keep_all(bios_mode,change_part):
    count = 0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Upd.CHANGE_PART3_1, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()

        assert _change_options_value_part2()

        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower()=='latest':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower()=='previous':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower()=='constant':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info("Update BIOS in Shell successed.")
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1
    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('SHELL下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SHELL下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def linux_upgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
        
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)

    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Linux下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Linux下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def linux_upgrade_all(bios_mode,change_part):
    count=0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)

    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('Linux下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Linux下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def linux_downgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))

    time.sleep(2)
    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    time.sleep(2)
    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)
  
    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1
    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Linux下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Linux下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def linux_downgrade_all(bios_mode,change_part):
    count=0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)

    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('Linux下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Linux下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def linux_keep_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    changed_options = _get_options_value()
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)

    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Linux下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Linux下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def linux_keep_all(bios_mode,change_part):
    count=0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Upd.CHANGE_PART3_1, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))
   
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)

    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('Linux下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Linux下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def windows_upgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    changed_options=_get_options_value()
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower()=='latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower()=='previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower()=='constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_NOR, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Windows下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Windows下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def windows_upgrade_all(bios_mode,change_part):
    count=0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Upd.CHANGE_PART3_1, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_ALL, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('Windows下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Windows下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return
      
        

def windows_downgrade_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    changed_options=_get_options_value()
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_NOR, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Windows下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Windows下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def windows_downgrade_all(bios_mode,change_part):
    count=0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_ALL, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('Windows下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Windows下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')

        return



def windows_keep_normal(bios_mode,change_part):
    count=0
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert _go_to_setup()
    changed_options=_get_options_value()
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_NOR, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后的选项{0}'.format(updated_options))
    logging.info('改变后的选项{0}'.format(changed_options))
    if updated_options == changed_options:
        logging.info('Windows下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Windows下保留配置刷新，刷新BIOS后配置改变，改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in changed_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def windows_keep_all(bios_mode,change_part):
    count=0
    num = 0
    _go_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Upd.CHANGE_PART3_1,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('100')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_TIME_ALWAYS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    assert _go_to_setup()
    default_options = _get_options_value()
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_ALL, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY_CN, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('Set User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    updated_options = _get_options_value()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    logging.info('刷新后选项{0}'.format(updated_options))
    logging.info('默认的选项{0}'.format(default_options))
    if status == 'always-off' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>RestoreACPowerLoss'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search('RestoreACPowerLoss', i)]))
        num += 1
    updated_options = [i for i in updated_options if not re.search('RestoreACPowerLoss', i)]
    default_options = [i for i in default_options if not re.search('RestoreACPowerLoss', i)]

    if updated_options == default_options:
        logging.info('Windows下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('Windows下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return



def update_bios_setup_normal(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_UPDATE_NOR,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST,
                                   15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS,
                                   15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT,
                                   15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')

    BmcLib.power_reset()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_setup_all(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_ALL, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    if bios_mode.lower() == 'latest':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST,
                                   15, 'Confirmation')
    elif bios_mode.lower() == 'previous':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS,
                                   15, 'Confirmation')
    elif bios_mode.lower() == 'constant':
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT,
                                   15, 'Confirmation')
    else:
        stylelog.fail('bios_mode有误')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')

    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True

def update_bios_dos_normal(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)

    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        cmd = '{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        cmd = '{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        cmd = '{0} {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_NOR, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    return True

def update_bios_dos_all(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.SET_DOS,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                          SutConfig.Msg.HOTKEY_PROMPT_F11_CN):
        BmcLib.power_cycle()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                              SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 20, SutConfig.Upd.ENT_DOS_MSG)

    time.sleep(5)
    logging.info("DOS Boot Successed.")
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE)
    elif bios_mode.lower() == 'previous':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        cmd = '{0} -all {1}'.format(SutConfig.Upd.DOS_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return
    for data in cmd:
        SetUpLib.send_data(data)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    logging.info("Starting to update BIOS.")
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_ALL, 300, readline=False):
        logging.info("Update BIOS in DOS successed.")
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_shell_normal(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                     SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20,
                                       SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."

    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    BmcLib.power_reset()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_shell_all(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.OPEN_SHELL,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200,
                                     SutConfig.Msg.HOTKEY_PROMPT_F11_CN), "Press F11 failed."
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20,
                                       SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."

    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    if bios_mode.lower() == 'latest':

        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':

        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':

        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL,SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info("Update BIOS in Shell successed.")
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_linux_normal(bios_mode):
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH,
                                  "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                         SutConfig.Env.LINUX_USB_MOUNT))
        
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
     
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':

        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.LATEST_BIOS_FILE)



    elif bios_mode.lower() == 'previous':

        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.PREVIOUS_BIOS_FILE)
    elif bios_mode.lower() == 'constant':
        arg = "{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                      SutConfig.Env.CONSTANT_BIOS_FILE)


    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)
   

    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_linux_all(bios_mode):
    assert SetUpLib.boot_os_from_bm()

    SshLib.execute_command_limit(Sut.OS_SSH,
                                  "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                         SutConfig.Env.LINUX_USB_MOUNT))
   
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
        
    time.sleep(2)

    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))

    time.sleep(2)
    if bios_mode.lower() == 'latest':

        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.LATEST_BIOS_FILE)

    elif bios_mode.lower() == 'previous':

        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.PREVIOUS_BIOS_FILE)

    elif bios_mode.lower() == 'constant':
        arg = "{0} -all {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                           SutConfig.Env.CONSTANT_BIOS_FILE)
    else:
        stylelog.fail('bios_mode有误')
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, arg)
      


    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result[0]), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_windows_normal(bios_mode):
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))

    else:
        stylelog.fail('bios_mode有误')
        return
    assert re.search(SutConfig.Upd.WINDOWS_MSG_NOR, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    time.sleep(3)
    BmcLib.power_reset()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True



def update_bios_windows_all(bios_mode):
    assert SetUpLib.boot_os_from_bm('windows')
    if bios_mode.lower() == 'latest':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                         SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return

    assert re.search(SutConfig.Upd.WINDOWS_MSG_ALL, cmd_result[0]), "Update BIOS in Windows failed."
    logging.info('BIOS更新成功')
    BmcLib.power_reset()
    time.sleep(120)
    BmcLib.enable_serial_only()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    return True