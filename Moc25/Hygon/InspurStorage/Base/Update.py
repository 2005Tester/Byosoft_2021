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
import time
import logging
from bs4 import BeautifulSoup
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from InspurStorage.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



def _get_options_value():
    time.sleep(1)
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Msg.PAGE_MAIN,5)
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
        if SutConfig.Msg.PAGE_MAIN in data:
            break
        try_counts-=1

    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Upd.LOC_DEVICE,10)
    for option in SutConfig.Upd.LOC_PART1:
        if option not in SutConfig.Msg.PAGE_ALL:
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

    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.LOC_ADVANCED, 10)
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
    return [i.replace(' ', '') for i in options]



def _change_options_value_part():
    SetUpLib.close_session()#关闭连接
    time.sleep(2)
    SetUpLib.open_session()#打开链接
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN,SutConfig.Upd.CHANGE_PART,12)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(2)
    return True



def _set_password(admin=SutConfig.Upd.PASSWORDS[0],users=SutConfig.Upd.PASSWORDS[1]):
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Msg.PAGE_SECURITY,10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(admin)
    time.sleep(1)
    SetUpLib.send_data(admin)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_ADM,5):
        logging.info('管理员密码{0}设置成功'.format(admin))
    else:
        return
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.SET_USER_PSW,10)
    time.sleep(1)
    SetUpLib.send_data_enter(users)
    time.sleep(1)
    SetUpLib.send_data(users)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS_USE, 3):
        logging.info('用户密码{0}设置成功'.format(users))
    else:
        return
    time.sleep(1)
    return True



def _go_setup_no_psw(password=SutConfig.Upd.PASSWORDS[0],users=SutConfig.Upd.PASSWORDS[1]):
    SetUpLib.reboot()
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        SetUpLib.reboot()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_key(Key.DEL)
    logging.info('Hot Key sent')
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN,60):
        logging.info("SetUpLib: Boot to setup main page successfully")
        return True
    else:
        time.sleep(1)
        SetUpLib.send_data(password)
        if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 60):
            logging.info("SetUpLib: Boot to setup main page successfully")
        else:
            return
        assert _del_password(password,users)
        return True



def _go_to_setup(password=SutConfig.Upd.PASSWORDS[0]):
    logging.info("SetUpLib: Boot to setup main page")
    try_counts = 2
    while try_counts:
        logging.info("Waiting for Hotkey message found...")
        if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200, SutConfig.Msg.HOTKEY_PROMPT_DEL):
            logging.info("Press Del failed, will try again.")
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)
            try_counts -= 1

        else:
            time.sleep(1)
            SetUpLib.send_data(password)
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN,60):
                logging.info("SetUpLib: Boot to setup main page successfully")
                return True



def _del_password(password=SutConfig.Upd.PASSWORDS[0],users=SutConfig.Upd.PASSWORDS[1]):
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Msg.PAGE_SECURITY,10)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_ADM,3):
        logging.info('密码删除')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(users)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS_USE, 5):
        logging.info('用户密码删除')
        time.sleep(1)
    else:
        return
    return True



def _change_smbios():
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_USB, 18)
    time.sleep(0.5)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('fs1:')
    time.sleep(1)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(1)
    SetUpLib.send_data('ByoShellFlash.efi dmi -t:1 -o:5 -s:oem')
    if SetUpLib.wait_message_enter(SutConfig.Upd.SMBIOS_MSG, 20):
        logging.info('更新SMBIOS信息成功')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('exit')
    time.sleep(1)

    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_EXIT, 20):
        logging.info('成功进入SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    return True



def setup_upgrade(bios_mode):
    count=0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Msg.PAGE_EXIT,18)
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
    time.sleep(2)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count+=1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):
            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result=SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)',result)))
        num+=1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('SetUp下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num==0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('SetUp下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num==0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def setup_downgrade(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Msg.PAGE_EXIT, 18)
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
    time.sleep(2)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))

    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('SetUp下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('SetUp下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def setup_keep(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Msg.PAGE_EXIT, 18)
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
    time.sleep(2)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('SetUp下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('SetUp下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def shell_upgrade_normal(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Upd.LOC_USB,18)
    if SetUpLib.wait_message('UEFI Interactive Shell',20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
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
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def shell_upgrade_all(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_USB, 18)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if SutConfig.Upd.PRODUCT_NAME in result:
        logging.info('完全刷新BIOS，刷新后SMBIOS信息恢复默认值')
    else:
        stylelog.fail('完全刷新BIOS，刷新后SMBIOS信息没有恢复默认值，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def shell_downgrade_normal(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_USB, 18)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def shell_downgrade_all(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_USB, 18)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if SutConfig.Upd.PRODUCT_NAME in result:
        logging.info('完全刷新BIOS，刷新后SMBIOS信息恢复默认值')
    else:
        stylelog.fail('完全刷新BIOS，刷新后SMBIOS信息没有恢复默认值，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def shell_keep_normal(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_USB, 18)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def shell_keep_all(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_USB, 18)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    if bios_mode.lower() == 'latest':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.LATEST_BIOS_FILE))
    elif bios_mode.lower() == 'previous':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.PREVIOUS_BIOS_FILE))
    elif bios_mode.lower() == 'constant':
        SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.CONSTANT_BIOS_FILE))
    else:
        stylelog.fail('bios_mode有误')
        return
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if SutConfig.Upd.PRODUCT_NAME in result:
        logging.info('完全刷新BIOS，刷新后SMBIOS信息恢复默认值')
    else:
        stylelog.fail('完全刷新BIOS，刷新后SMBIOS信息没有恢复默认值，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Shell下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def linux_upgrade_normal(bios_mode):
    count=0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS,10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                                     SutConfig.Env.LINUX_USB_MOUNT))
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
    cmd_result = SetUpLib.execute_command(arg,200)
    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(2)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def linux_upgrade_all(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
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
    cmd_result = SetUpLib.execute_command(arg, 200)
    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if SutConfig.Upd.PRODUCT_NAME in result:
        logging.info('完全刷新BIOS，刷新后SMBIOS信息恢复默认值')
    else:
        stylelog.fail('完全刷新BIOS，刷新后SMBIOS信息没有恢复默认值，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def linux_downgrade_normal(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
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
    cmd_result = SetUpLib.execute_command(arg, 200)
    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def linux_downgrade_all(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
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
    cmd_result = SetUpLib.execute_command(arg, 200)
    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(2)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if SutConfig.Upd.PRODUCT_NAME in result:
        logging.info('完全刷新BIOS，刷新后SMBIOS信息恢复默认值')
    else:
        stylelog.fail('完全刷新BIOS，刷新后SMBIOS信息没有恢复默认值，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def linux_keep_normal(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
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
    cmd_result = SetUpLib.execute_command(arg, 200)
    assert re.search(SutConfig.Upd.LINUX_MSG_NOR, cmd_result), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if 'Product Name: oem' in result:
        logging.info('保留配置刷新BIOS，刷新后SMBIOS信息保留')
    else:
        stylelog.fail('保留配置刷新BIOS，刷新后SMBIOS信息没有保留，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return



def linux_keep_all(bios_mode):
    count = 0
    num=0
    assert _go_setup_no_psw()
    assert _change_smbios()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    default_options = _get_options_value()
    assert _set_password()
    time.sleep(1)
    assert _change_options_value_part()
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
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
    cmd_result = SetUpLib.execute_command(arg, 200)
    assert re.search(SutConfig.Upd.LINUX_MSG_ALL, cmd_result), "Update BIOS in Linux failed."
    logging.info('BIOS更新成功')
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    if SetUpLib.boot_to_setup():
        logging.info('刷新BIOS后密码不存在')
    else:
        count += 1
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        _go_to_setup()
        _del_password()
    updated_options = _get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.LOC_OS, 18)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):

            logging.info("OS Boot Successed.")
        else:
            return
    else:
        logging.info("OS Boot Fail.")
    time.sleep(1)
    result = SetUpLib.execute_command('dmidecode -t 1')
    if SutConfig.Upd.PRODUCT_NAME in result:
        logging.info('完全刷新BIOS，刷新后SMBIOS信息恢复默认值')
    else:
        stylelog.fail('完全刷新BIOS，刷新后SMBIOS信息没有恢复默认值，变为{}'.format(re.findall('Product Name: (\w+)', result)))
        num += 1
    time.sleep(2)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    logging.info('刷新后选项值{0}'.format(updated_options))
    logging.info('默认的选项值{0}'.format(default_options))
    if updated_options == default_options:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置恢复默认值')
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
                return True
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
                return
        else:
            stylelog.fail('刷新BIOS后密码存在')
            return
    else:
        logging.info('Linux下刷新BIOS，刷新BIOS后配置没有恢复默认值,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后的选项{0}'.format(i))
        for i in default_options:
            if i not in updated_options:
                logging.info('改变后的选项{0}'.format(i))
        if count == 0:
            logging.info('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后SMBIOS信息正确')
            else:
                stylelog.fail('刷新BIOS后SMBIOS信息错误')
        else:
            stylelog.fail('刷新BIOS后密码存在')
        return


