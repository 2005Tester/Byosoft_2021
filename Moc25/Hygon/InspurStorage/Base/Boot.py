#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import os
import time
import logging
import pyautogui
from InspurStorage.Base import Update
from InspurStorage.BaseLib import BmcLib,SetUpLib,SshLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from PIL import Image,ImageChops
from batf.Report import  stylelog
from batf.SutInit import Sut
import subprocess
from batf import core



def boot():
    logging.info('SetUp下进入USB测试')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.LOC_BOOT_USB,18)
    if SetUpLib.wait_message('UEFI Interactive Shell', 20):
        logging.info('从SetUp进入USB成功')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data('exit')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_EXIT, 20):
        logging.info('成功返回SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    logging.info('SetUp下进入OS测试')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_BOOT_OS, 18)

    if SetUpLib.wait_message(SutConfig.Msg.LINUX_OS_MSG):
        logging.info('从SetUp进入系统成功')
    else:
        return
    assert SetUpLib.boot_to_setup()
    logging.info('SetUp下进入PXE测试')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_BOOT_PXE, 18)
    if SetUpLib.wait_message('Checking media present...',10):
        logging.info('从SetUp进入PXE成功')
    else:
        return
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    return True



def boot_order():
    order=''.join(SutConfig.Boot.ORDER).replace(' ','')
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.SET_PXE_ALL,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    SetUpLib.send_key(Key.LEFT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    data=SetUpLib.get_data(1)
    data=re.findall('Boot Override(.*)Load defaults',data)[0]
    boot_name_setup=data.replace(' ','')
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE,200):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE,200)
    SetUpLib.send_key(Key.F3)
    start = time.time()
    while True:
        end = time.time()
        data = SetUpLib.get_data()
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, data):
            break
        if end - start > 200:
            break
    boot_name_f3=re.findall('Startup Device Menu(.*)Enter Setup',data)[0].replace(' ','')
    if re.search(order,boot_name_setup) and re.search(order,boot_name_f3):
        logging.info('F3启动菜单启动顺序与SetUp下启动顺序一致与默认启动顺序一直')
    else:
        stylelog.fail('F3启动菜单启动顺序与SetUp下启动顺序不一致与默认启动顺序')
        logging.info('F3启动菜单启动顺序{}'.format(boot_name_f3))
        logging.info('SetUp下启动顺序{}'.format(boot_name_setup))
        logging.info('默认启动顺序{}'.format(order))
        count += 1
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,12,SutConfig.Msg.PAGE_MAIN)
    time.sleep(1)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def change_boot_order():
    count=0
    order=''.join(SutConfig.Boot.CHANGE_ORDER).replace(' ','')
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.SET_PXE_ALL, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.PXE_BOOT_NAME],18)
    try_counts=8
    while try_counts:
        time.sleep(1)
        SetUpLib.send_key(Key.ADD)
        try_counts -= 1
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HDD_BOOT_NAME], 18)
    try_counts = 8
    while try_counts:
        time.sleep(1)
        SetUpLib.send_key(Key.ADD)
        try_counts -=1
    time.sleep(1)
    SetUpLib.send_key(Key.SUBTRACT)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()

    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    SetUpLib.send_key(Key.LEFT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    data = SetUpLib.get_data(1)
    boot_name_setup = re.findall('Boot Override(.*)Load defaults', data)[0].replace(' ','')

    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.USB_UEFI],18)
    if SetUpLib.wait_message_enter('UEFI Interactive Shell', 20):
        logging.info('进入USB成功')
    else:
        return
    time.sleep(10)
    SetUpLib.send_data('exit')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_EXIT, 20):
        logging.info('成功返回SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_BOOT_OS, 18)
    if SetUpLib.wait_message(SutConfig.Msg.LINUX_OS_MSG):
        logging.info('从SetUp进入系统成功')
    else:
        return
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 200):
        SetUpLib.reboot()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 200)
    SetUpLib.send_key(Key.F3)
    start=time.time()
    while True:
        end=time.time()
        datas = SetUpLib.get_data()
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, datas):
            break
        if end-start>200:
            break
    boot_name_f3 = re.findall('Startup Device Menu(.*)Enter Setup', datas)[0].replace(' ','')
    if re.search(order, boot_name_setup) and re.search(order, boot_name_f3):
        logging.info('F3启动菜单启动顺序与SetUp下启动顺序一致与修改后启动顺序一致')
    else:
        stylelog.fail('F3启动菜单启动顺序与SetUp下启动顺序不一致与修改后启动顺序不一致')
        logging.info('F3启动菜单启动顺序{}'.format(boot_name_f3))
        logging.info('SetUp下  启动顺序{}'.format(boot_name_setup))
        logging.info('修改后    启动顺序{}'.format(order))
        count += 1
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        SetUpLib.reboot()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    if SetUpLib.wait_message('Checking media present...'):
        logging.info('修改第一启动项为PXE，成功进入PXE')
    else:
        stylelog.fail('修改第一启动项为PXE，没有进入PXE')
        count+=1
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(4)
    if count==0:
        return True
    else:
        return



#快捷启动
def quick_boot_hotkey():
    assert SetUpLib.boot_with_hotkey(Key.DEL,SutConfig.Msg.PAGE_MAIN,250,SutConfig.Msg.POST_MESSAGE)
    logging.info('DEL进入SetUp成功')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.PXE, 10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F3,SutConfig.Msg.ENTER_BOOTMENU,250,SutConfig.Msg.POST_MESSAGE)
    logging.info('F3进入启动菜单成功')
    assert SetUpLib.boot_with_hotkey(Key.F12,'Checking media present...',250,SutConfig.Msg.POST_MESSAGE)
    logging.info('F12进入PXE成功')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    return True



def pxe_boot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.SET_PXE_ALL,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.LOC_BOOT_PXE,18)
    if SetUpLib.wait_message(SutConfig.Boot.IPV4_MSG,5):
        logging.info('IPv4 PXE启动成功')
    else:
        stylelog.fail('IPv4 PXE启动失败')
        return
    assert SetUpLib.boot_with_hotkey(Key.F3,SutConfig.Msg.ENTER_BOOTMENU,250,SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.PXE_PORT3,12,SutConfig.Boot.IPV6_MSG),'IPv6 PXE 启动失败'
    logging.info('IPv6 PXE 启动成功')
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    return True