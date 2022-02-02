#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import os
import time
import logging
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from batf.Report import stylelog



#PXE网络引导
def pxe_option_rom():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.CLOSE_PXE,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
       BmcLib.init_sut()
       BmcLib.enable_serial_normal()
       assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    
    datas=SetUpLib.get_data(10,Key.F11)
    if 'PXE' not in datas:
        logging.info('PXE网络引导关闭，启动项没有出现PXE')
    else:
        stylelog.fail('PXE网络引导关闭，但启动项仍有PXE')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,20,SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.OPEN_PXE,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    datas=SetUpLib.get_data(10,Key.F11)
    if 'PXE' in datas:
        logging.info('PXE网络引导打开，启动项出现PXE')
        return True
    else:
        stylelog.fail('PXE网络引导打开，但启动项没有出现PXE')
        return



def pxe_boot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_IPV4,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.IPV4_MSG, 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('IPv4PXE启动成功')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_IPV6,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.IPV6_MSG, 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('IPv6PXE启动成功')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_LEGACY, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, 'PXE', 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('LegacyPXE启动成功')
    assert SetUpLib.boot_to_setup()

    assert SetUpLib.boot_to_page('User Wait Time')
    assert SetUpLib.select_option_value(Key.DOWN, ['Boot Mode'], Key.DOWN, 'UEFI', 6)
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



# 网络重试
def pxe_retry():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.CLOSE_PXE_RETRY,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.IPV4_MSG, 120, SutConfig.Msg.POST_MESSAGE)
    time.sleep(20)
    if BmcLib.ping_sut():
        logging.info('网络启动重试关闭，启动失败后，不再重新尝试，直接进入系统')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.OPEN_PXE_RETRY,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.IPV4_MSG, 120, SutConfig.Msg.POST_MESSAGE)
    try_counts=3
    counts=0
    while True:
        if SetUpLib.wait_message_enter('timeout'):
            counts+=1
            logging.info('第{0}次网络重试'.format(counts))
        else:
            return
        if counts==try_counts:
            # if BmcLib.ping_sut():
            #     logging.info('第{0}次网络重试后进入系统'.format(counts))
            #     break
            # else:
            #     return
            break
    logging.info('网络启动重试打开，启动失败后，不断重新尝试启动。')
    return True



# 网络引导版本
def pxe_protocol():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_IPV4_6,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)

    data = SetUpLib.get_data(10, Key.F11)
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
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP , 20, SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_IPV4,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data1 = SetUpLib.get_data(10, Key.F11)
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
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_IPV6,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data2 = SetUpLib.get_data(10, Key.F11)
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



def pxe_network():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_ONBOARD,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data = SetUpLib.get_data(10, Key.F11)
    if not re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and  re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        logging.info('PXE启动网卡选择板载网卡，启动项中只有板载网卡，没有外插网卡')
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and  re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡选择板载网卡，启动项中既有板载网卡，也有外插网卡')
        count+=1
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡选择板载网卡，启动项中有外插网卡，没有板载网卡')
        count+=1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡选择板载网卡，启动项中没有外插网卡，也没有板载网卡')
        count+=1
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_ADDON,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data = SetUpLib.get_data(10, Key.F11)
    if re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        logging.info('PXE启动网卡选择外插网卡，启动项中只有外插网卡，没有板载网卡')
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and  re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡选择外插网卡，启动项中既有外插网卡，也有板载网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and  re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡选择外插网卡，启动项中有板载网卡，没有外插网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡选择外插网卡，启动项中没有外插网卡，也没有板载网卡')
        count += 1
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_NONE,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data = SetUpLib.get_data(10, Key.F11)

    if re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        logging.info('PXE启动网卡不进行选择，启动项中既有外插网卡，也有板载网卡')
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡不进行选择，启动项中有外插网卡，没有板载网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and  re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡不进行选择，启动项中有板载网卡，没有外插网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON,data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD,data):
        stylelog.fail('PXE启动网卡不进行选择，启动项中没有外插网卡，也没有板载网卡')
        count += 1
    else:
        return
    if count==0:
        return True
    else:
        return



def pxe_boot_priority():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_ONBOARD_PRI,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data = SetUpLib.get_data(10, Key.F11)
    data = ''.join(re.findall('UEFI .*?: Port \d .*?IPv4', data))
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, data)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, data)
    if ''.join(onboard+addon) in data:
        logging.info('修改PXE优先级板载优先，启动项中板载优先')
    elif ''.join(addon+onboard) in data:
        stylelog.fail('修改PXE优先级板载优先，启动项中外插优先')
        count+=1
    else:
        stylelog.fail('修改PXE优先级板载优先，启动项中既不是板载优先，也不是外插优先')
        stylelog.fail('启动顺序为{0}'.format(re.findall('Device Menu(.*?) *[\^|↑]',data)))
        count+=1
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_ADDON_PRI,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    data = SetUpLib.get_data(10, Key.F11)
    data = ''.join(re.findall('UEFI .*?: Port \d .*?IPv4', data))
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, data)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, data)
    if ''.join(addon+onboard) in data:
        logging.info('修改PXE优先级外插优先，启动项中外插优先')
    elif ''.join(onboard+addon) in data:
        stylelog.fail('修改PXE优先级外插优先，启动项中板载优先')
        count += 1
    else:
        stylelog.fail('修改PXE优先级外插优先，启动项中既不是外插优先，也不是板载优先')
        stylelog.fail('启动顺序为{0}'.format(re.findall('Device Menu(.*?) *[\^|↑]', data)))
        count += 1
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pxe.SET_ADDON_NONE,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if count==0:
        return True
    else:
        return