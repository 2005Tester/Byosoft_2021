#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import os
import time
import logging
from Hygon7500CRB.BaseLib import BmcLib,SetUpLib
from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig, Sut01Config
from batf.Report import stylelog



#PXE网络引导
def pxe_option_rom():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.BOOT_PCIE_CONFIG,8)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(1)
    name = re.findall('(Riser[A-Z]\_[0-9]\(J[0-9]{3} [0-9]X\))', data)[-1]
    name = re.sub(r'\(', '\(', name)
    name = re.sub(r'\)', '\)', name)
    assert SetUpLib.select_option_value(Key.DOWN,[name],Key.DOWN,'Enabled',30)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PXE.SET_NETWORK_BOOT_DISABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
       BmcLib.init_sut()
       assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    datas=SetUpLib.get_data(10,Key.F7)
    if 'PXE' not in datas:
        logging.info('网络引导关闭，启动项没有出现PXE')
    else:
        stylelog.fail('网络引导关闭，但启动项仍有PXE')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,20,SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PXE.SET_NETWORK_BOOT_ENABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    datas=SetUpLib.get_data(10,Key.F7)
    if 'PXE' in datas:
        logging.info('网络引导打开，启动项出现PXE')
        return True
    else:
        stylelog.fail('网络引导打开，启动项没有出现PXE')
        return



def pxe_boot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.BOOT_PCIE_CONFIG,8)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(1)
    name = re.findall('(Riser[A-Z]\_[0-9]\(J[0-9]{3} [0-9]X\))', data)[-1]
    name = re.sub(r'\(', '\(', name)
    name = re.sub(r'\)', '\)', name)
    assert SetUpLib.select_option_value(Key.DOWN,[name],Key.DOWN,'Enabled',30)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_IP_VERSION_IPv4, 6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Msg.PXE_IPV6_MSG, 150, Sut01Config.Msg.POST_MESSAGE)
    logging.info('IPv4PXE启动成功')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_IP_VERSION_IPv6,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Msg.PXE_IPV6_MSG, 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('IPv6PXE启动成功')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.PXE_LEGACY_BOOT,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, 'PXE', 150, Sut01Config.Msg.POST_MESSAGE)
    logging.info('LegacyPXE启动成功')
    return True



# 网络重试
def pxe_retry():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.PXE.SET_PXE_RETRY_DISABLED,6)
    time.sleep(2)
    SetUpLib.send_data_enter('0')
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Msg.PXE_IPV4_MSG, 120, Sut01Config.Msg.POST_MESSAGE)
    time.sleep(20)
    if BmcLib.ping_sut():
        logging.info('网络启动重试设置次数为0，启动失败后，不再重新尝试，直接进入系统')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PXE.SET_PXE_RETRY_ENABLED,6)
    time.sleep(2)
    SetUpLib.send_data_enter('3')
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Msg.PXE_IPV4_MSG, 120, SutConfig.Msg.POST_MESSAGE)
    try_counts=3
    counts=0
    while True:
        if SetUpLib.wait_message_enter(SutConfig.Msg.PXE_IPV4_MSG_ERROR):
            counts+=1
            logging.info('第{0}次网络重试'.format(counts))
        else:
            return
        if counts==try_counts:
            if BmcLib.ping_sut():
                logging.info('第{0}次网络重试后进入系统'.format(counts))
                break
            # else:
            #     return
            # break
    logging.info('网络启动重试次数设置为3次，启动失败后，重新尝试启动的次数为3次。')
    return True



# 网络引导版本
def pxe_protocol():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.PCIE_CONFIG, 9)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(1)
    name = re.findall('(Riser[A-Z]\_[0-9]\(J[0-9]{3} [0-9]X\))', data)[-1]
    name = re.sub(r'\(','\(',name)
    name = re.sub(r'\)','\)',name)
    assert SetUpLib.select_option_value(Key.DOWN, [name], Key.DOWN, 'Enabled',30)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_IP_VERSION_ALL,9)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data = SetUpLib.get_data(10, Key.F7)
    if 'IPv4' in data and 'IPv6' in data:
        logging.info('修改网络引导版本为IPv4和IPv6，启动项出现IPv4和IPv6')

    elif 'IPv4' in data and 'IPv6' not in data:
        stylelog.fail('修改网络引导版本为IPv4和IPv6，启动项只出现IPv4')
        return
    elif 'IPv6' in data and 'IPv4' not in data:
        stylelog.fail('修改网络引导版本为IPv4和IPv6，启动项只出现IPv6')
        return
    else:
        stylelog.fail('启动项中没有IPv4也没有IPv6')
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_IP_VERSION_IPv4,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data1 = SetUpLib.get_data(10, Key.F7)
    if 'IPv4' in data1 and 'IPv6' not in data1:
        logging.info('修改网络引导版本为IPv4，启动项只出现IPv4')

    elif 'IPv4' in data1 and 'IPv6' in data1:
        stylelog.fail('修改网络引导版本为IPv4，但启动项出现IPv4和IPv6')
        return
    elif 'IPv6' in data1 and 'IPv4' not in data1:
        stylelog.fail('修改网络引导版本为IPv4，但启动项只出现IPv6')
        return
    else:
        stylelog.fail('启动项中没有IPv4也没有IPv6')
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_IP_VERSION_IPv6,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(Sut01Config.Msg.POST_MESSAGE)
    data2 = SetUpLib.get_data(10, Key.F7)
    if 'IPv6' in data2 and 'IPv4' not in data2:
        logging.info('修改网络引导版本为IPv6，启动项只出现IPv6')
        return True
    elif 'IPv6' in data2 and 'IPv4' in data2:
        stylelog.fail('修改网络引导版本为IPv6，但启动项出现IPv6和IPv4')
        return
    elif 'IPv4' in data2 and 'IPv6' not in data2:
        stylelog.fail('修改网络引导版本为IPv6,但启动项只出现IPv4')
        return
    else:
        stylelog.fail('启动项中没有IPv6也没有IPv4')
        return



def Http_Boot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_HTTP_ENABLED1, 10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.ENTER_BOOTMENU_CN, 150, Sut01Config.Msg.POST_MESSAGE)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.HTTP_NAME1],8)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(10)
    if SutConfig.Msg.HTTP_IPV4_MSG in data:
        logging.info('HTTP IPv4启动成功')
    else:
        stylelog.fail('HTTP IPv4启动失败')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_HTTP_ENABLED2,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.ENTER_BOOTMENU_CN, 150, Sut01Config.Msg.POST_MESSAGE)
    assert SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.HTTP_NAME2], 8)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    date = SetUpLib.get_data(10)
    if SutConfig.Msg.HTTP_IPV6_MSG in date:
        logging.info('HTTP IPv6启动成功')
    else:
        stylelog.fail('HTTP IPv6启动失败')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.PXE.SET_HTTP_DISABLED,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True