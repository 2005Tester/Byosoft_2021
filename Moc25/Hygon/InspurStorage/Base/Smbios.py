import datetime
import re
import os
import time
import shutil
import difflib
import logging
import pyautogui
from bs4 import BeautifulSoup
from serial.win32 import SetupComm
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from InspurStorage.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



def get_smbios():
    assert SetUpLib.boot_os_from_bm()
    types = [0, 1, 2, 3, 4, 7,  9,  13, 16, 17,  20, 127]
    for type in types:
        type_file = 'type' + str(type) + '.txt'
        data = SetUpLib.execute_command('dmidecode -t {}'.format(type))
        with open('InspurStorage/Tools/SMBIOS/{}'.format(type_file), 'w+') as f:
            f.write(data)
        time.sleep(1)
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    return True



def check_diff(log1, log2):
    logging.info("Comparing {0} and {1}".format(log1, log2))
    try:
        with open(log1, 'r') as f:
            content_log1 = f.read().splitlines()
        with open(log2, 'r') as f:
            content_log2 = f.read().splitlines()
    except FileNotFoundError:
        logging.error("Please check whether log file exists.")
        return True
    d = difflib.Differ()
    diffs = list(d.compare(content_log1, content_log2))
    res = []
    for diff in diffs:
        if not re.search("^\s", diff):
            res.append(diff)
    return res



def type13():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,['CPU Info',{'Select Language':'中文'}],18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_with_hotkey_only(Key.F3, '设备启动菜单', 200, '按 Del 进入固件配置')
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 12,SutConfig.Msg.LINUX_OS_MSG):
        return
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

    data=SetUpLib.execute_command('dmidecode -t 13')
    if re.search('Currently Installed Language: zh\|CN\|unicode',data):
        logging.info('修改语言为中文，type13正确显示')
    else:
        stylelog.fail('修改语言为中文，type13显示错误，{}'.format(re.findall('Currently Installed Language: (.*)  ',data)))
        count+=1
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    assert SetUpLib.boot_with_hotkey_only(Key.DEL, '处理器信息', 200, '按 Del 进入固件配置')
    SetUpLib.back_to_setup_toppage()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,[{'选择语言':'English'}],8)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    data = SetUpLib.execute_command('dmidecode -t 13')
    if re.search('Currently Installed Language: en|US|iso8859-1', data):
        logging.info('修改语言为英文，type13正确显示')
    else:
        stylelog.fail('修改语言为英文，type13显示错误，{}'.format(re.findall('Currently Installed Language: (.*)  ', data)))
        count+=1

    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(1)
    if count==0:
        return True
    else:
        return



def update_smbios():
    count=0
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    SetUpLib.execute_command('{} -t:1 -o:4 -s:oem14'.format(SutConfig.Env.LINUX_SMBIOS_CMD))
    time.sleep(1)
    SetUpLib.execute_command('{} -t:1 -o:7 -s:oem17'.format(SutConfig.Env.LINUX_SMBIOS_CMD))
    time.sleep(1)
    SetUpLib.execute_command('{} -t:2 -o:5 -s:oem25'.format(SutConfig.Env.LINUX_SMBIOS_CMD))
    time.sleep(1)
    SetUpLib.execute_command('{} -t:3 -o:8 -s:oem38'.format(SutConfig.Env.LINUX_SMBIOS_CMD))
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_DEVICE)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('Mother Board Info *oem25',2):
        logging.info('type2 offset5 修改成功')
    else:
        stylelog.fail('type2 offset5 修改失败')
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.LOC_SYS_SUM,18)
    data=SetUpLib.get_data(2)
    if re.search('System Manufacturer *oem14',data):
        logging.info('type1 offset4 修改成功')
    else:
        stylelog.fail('type1 offset4 修改失败')
        count+=1
    if re.search('System Serial Number *oem17',data):
        logging.info('type1 offset7 修改成功')
    else:
        stylelog.fail('type1 offset7 修改失败')
        count+=1
    if re.search('Asset Tag *oem38',data):
        logging.info('type3 offset8 修改成功')
    else:
        stylelog.fail('type3 offset8 修改失败')
        count+=1
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.USB_UEFI],18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('UEFI Interactive Shell',20):
        logging.info('进入Shell')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    SetUpLib.send_data_enter('{0} -all {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.LATEST_BIOS_FILE))
    SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300)
    logging.info('Shell下刷新BIOS成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(2)
    if count==0:
        return True
    else:
        return
