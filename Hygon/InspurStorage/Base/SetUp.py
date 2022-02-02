#coding='utf-8'
import re
import os
import time
import subprocess
import logging
import pyautogui
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Base import Update,Boot
from InspurStorage.Config.PlatConfig import Key,Key100
from InspurStorage.Config import SutConfig
from InspurStorage.BaseLib import SshLib
from batf.SutInit import Sut
from PIL import Image,ImageChops
from batf.Report import stylelog



#BIOS默认值检查
def bios_default_value():
    default_options=SutConfig.Sup.DEFAULT_OPTIONS
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    options=Update._get_options_value()
    if options==default_options:
        logging.info('BIOS 默认参数检查成功')
        return True
    else:
        stylelog.fail('理论默认值：{}'.format(default_options))
        stylelog.fail('实际默认值：{}'.format(options))
        return



#串口重定向
def console_direction():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.SET_VT100,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(4)
    assert SetUpLib.boot_with_hotkey(Key100.F3, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,12,SutConfig.Msg.PAGE_MAIN)
    time.sleep(2)
    SetUpLib.send_key(Key100.F1)
    if SetUpLib.wait_message(SutConfig.Sup.F1_MSG,3):
        logging.info('VT100终端，F1正常')
        time.sleep(1)
    else:
        stylelog.fail('VT100终端，F1无法使用')
        return
    SetUpLib.send_key(Key100.ESC)
    time.sleep(3)
    SetUpLib.send_key(Key100.ESC)
    if SetUpLib.wait_message(SutConfig.Sup.ESC_MSG,5):
        logging.info('VT100终端，ESC正常')
        time.sleep(1)
    else:
        stylelog.fail('VT100终端，ESC无法使用')
        return
    SetUpLib.send_key(Key100.ESC)
    time.sleep(3)
    SetUpLib.send_key(Key100.F9)
    if SetUpLib.wait_message(SutConfig.Sup.F9_MSG,5):
        logging.info('VT100终端，F9正常')
        time.sleep(1)
    else:
        stylelog.fail('VT100终端，F9无法使用')
        return
    SetUpLib.send_key(Key100.ESC)
    time.sleep(25)
    SetUpLib.send_key(Key100.F10)
    if SetUpLib.wait_message(SutConfig.Sup.F10_MSG,5):
        logging.info('VT100终端，F10正常')
        time.sleep(1)
    else:
        stylelog.fail('VT100终端，F10无法使用')
        return
    SetUpLib.send_key(Key100.ESC)
    time.sleep(5)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.SET_UTF8,18)
    time.sleep(1)
    SetUpLib.send_keys(Key100.SAVE_RESET)
    time.sleep(5)
    return True



#USB存储设备支持
def usb_mass_storage_support():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_USB_STORAGE,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 200):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 200)
    SetUpLib.send_key(Key.F3)
    start = time.time()
    while True:
        end = time.time()
        data = SetUpLib.get_data()
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, data):
            break
        if end - start > 200:
            break
    datas= re.findall('Startup Device Menu(.*)Enter Setup', data)[0]
    if SutConfig.Msg.USB_UEFI not in datas:
        logging.info('USB存储设备支持关闭，启动项中没有USB')
    else:
        stylelog.fail('USB存储设备支持关闭，启动项中仍有USB')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.LINUX_OS,20,SutConfig.Msg.LINUX_OS_MSG)
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS,10):
            logging.info("OS Boot Successed.")
        else:
            return
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE, SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(1)
    result=SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE, SutConfig.Env.LINUX_USB_MOUNT))
    if re.search('已挂载于|already mounted on',result):
        logging.info('USB存储设备关闭，setup下识别不了U盘，系统下能正常识别U盘')
    else:
        stylelog.fail('USB存储设备关闭，setup下识别不了U盘，系统下不能正常识别U盘')
        return
    time.sleep(1)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_STORAGE,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 200):
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 200)
    SetUpLib.send_key(Key.F3)
    start = time.time()
    while True:
        end = time.time()
        data = SetUpLib.get_data()
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, data):
            break
        if end - start > 200:
            break
    datas = re.findall('Startup Device Menu(.*)Enter Setup', data)[0]
    if SutConfig.Msg.USB_UEFI in datas:
        logging.info('USB存储设备支持打开，启动项中有USB')
        return True
    else:
        stylelog.fail('USB存储设备支持打开，启动项中没有USB')
        return


    
#USB 端口配置
def usb_port_configuration():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
    datas=SetUpLib.get_data(3)
    if re.search('USB device list : * Set USB mass',datas):
        stylelog.fail('没有USB设备')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_USB_PORT,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    data=SetUpLib.get_data(2)
    if re.search(SutConfig.Msg.USB_UEFI,data):
        stylelog.fail('USB端口关闭，启动项中仍有USB')
        count+=1
    else:
        logging.info('USB端口关闭，启动项中没有USB')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
    datas = SetUpLib.get_data(3)
    if re.search('USB device list : * Set USB mass', datas):
        logging.info('USB端口关闭，USB设备列表中没有USB设备')
    else:
        stylelog.fail('USB端口关闭，USB设备列表中仍有USB设备')
        stylelog.fail(datas)
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_PORT,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if count==0:
        return True
    else:
        return



#安全启动
def secure_boot():
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_SECURE_BOOT,10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(25)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SECURE_BOOT,5)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F3, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 20,
                                       SutConfig.Sup.SECURE_MSG), '安全启动打开，仍可以进入到未签名的U盘'
    logging.info('安全启动打开，无法进入到未签名的U盘')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, 'UEFI Interactive Shell'),'安全启动打开，无法进入内置Shell'
    logging.info('安全启动打开，可以进入内置Shell')
    time.sleep(10)
    SetUpLib.send_data_enter('exit')
    time.sleep(2)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 20,SutConfig.Msg.LINUX_OS_MSG),'安全启动打开，仍无法进入加载签名驱动的系统'
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
        return
    logging.info('安全启动打开，可以进入加载签名驱动的系统')
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.CLOSE_SECURE_BOOT, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.Y)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    return True



#网络引导
def network_boot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_NET_BOOT,18)
    if not SetUpLib.wait_message(SutConfig.Msg.PXE_IP_VER,2):
        logging.info('关闭网络引导,网络引导IP版本被隐藏')
    else:
        stylelog.fail('关闭网络引导,网络引导IP版本没有被隐藏')
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        SetUpLib.reboot()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_key(Key.F12)
    if SetUpLib.wait_message('Checking media present...',20):
        stylelog.fail('关闭网络引导,仍可以进入PXE')
        return
    else:
        logging.info('关闭网络引导,无法进入PXE')
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(2)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE,200):
        SetUpLib.reboot()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE,200)
    SetUpLib.send_key(Key.F3)
    while True:
        data=SetUpLib.get_data()
        if re.search(SutConfig.Msg.ENTER_BOOTMENU,data):
            break
    result=re.findall('Startup Device Menu(.*)Enter Setup',data)[0].replace(' ','')
    if not re.search(SutConfig.Msg.PXE_PORT1.replace(' ',''),result) and not re.search(SutConfig.Msg.PXE_PORT2.replace(' ',''),result):
        logging.info('关闭网络引导,启动菜单没有 PXE')
    else:
        stylelog.fail('关闭网络引导,启动菜单仍有PXE')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,12,SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_NET_BOOT,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    return True



#用户等待时间
def user_wait_time():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('20')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE,200):
        start = time.time()
        SetUpLib.close_session()
        time.sleep(0.5)
        SetUpLib.open_session()
        if SetUpLib.wait_message('[A-Za-z]'):
            end=time.time()
    spent_time=end-start
    if 18<=int(spent_time)<=22:
        logging.info('修改用户等待时间为 20 秒成功')
    else:
        stylelog.fail('修改用户等待时间20秒失败,实际花费时间{}'.format(spent_time))
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('10')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE,200):
        start = time.time()
        SetUpLib.close_session()
        time.sleep(0.5)
        SetUpLib.open_session()
        if SetUpLib.wait_message('[A-Za-z]'):
            end=time.time()
    spent_time=end-start
    if 8<=int(spent_time)<=12:
        logging.info('修改用户等待时间为 10 秒成功')
    else:
        stylelog.fail('修改用户等待时间10秒失败,实际花费时间{}'.format(spent_time))
        return
    return True



def quiet_boot():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_QUIET_BOOT,18)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HDD_BOOT_NAME], 18)
    try_counts = 8
    while try_counts:
        time.sleep(1)
        SetUpLib.send_key(Key.ADD)
        try_counts -= 1
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    datas=''
    start=time.time()
    while True:
        end=time.time()
        datas+=SetUpLib.get_data()
        if re.search(SutConfig.Env.ROOT_LOGIN,datas):
            break
        if (end-start)>300:
            break
    if re.search(SutConfig.Msg.POST_MESSAGE,datas):
        stylelog.fail('安静启动打开，仍然显示POST信息')
        count+=1
    else:
        logging.info('安静启动打开，不显示POST信息')
    time.sleep(1)
    SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
    time.sleep(2)
    SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
    if SetUpLib.wait_message_enter(SutConfig.Env.LOGIN_SUCCESS, 10):
        logging.info("OS Boot Successed.")
    else:
        return
    time.sleep(1)
    SetUpLib.send_data_enter('systemctl reboot --firmware-setup')
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN,300):
        logging.info('进入SetUp')
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def close_kvm_msg():
    count=0
    logging.info('Start booting to os')
    SetUpLib.reboot()
    if not SetUpLib.boot_with_hotkey_only(Key.F3, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        reboot()
        if not SetUpLib.boot_with_hotkey_only(Key.F3, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            return
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 12, SutConfig.Msg.LINUX_OS_MSG):
        return
    if SetUpLib.wait_message_enter(SutConfig.Env.ROOT_LOGIN):
        data=SetUpLib.get_data(10)
        if re.search('kvm',data):
            stylelog.fail('进入系统后打印KVM信息')
            count+=1
        else:
            logging.info('进入系统后不打印KVM信息')
        SetUpLib.send_data_enter(SutConfig.Env.OS_USER)
        time.sleep(2)
        SetUpLib.send_data(SutConfig.Env.OS_PASSWORD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        datas=SetUpLib.get_data(10)
        if re.search('kvm', data):
            stylelog.fail('进入系统后打印KVM信息')
            count += 1
        else:
            logging.info('进入系统后不打印KVM信息')
    else:
        logging.info("OS Boot Fail.")
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def iommu():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_IOMMU,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    cmd_result=SetUpLib.execute_command('dmesg | grep -i iommu')
    if cmd_result=='':
        logging.info('iommu关闭')
    else:
        stylelog.fail('iommu没有关闭')
        return
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_IOMMU,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    time.sleep(1)
    cmd_result=SetUpLib.execute_command( "dmesg | grep -i iommu")
    if SutConfig.Sup.IOMMU_ENABLED_INFO in cmd_result:
        logging.info('iommu打开')
        time.sleep(1)
        SetUpLib.send_data_enter('reboot')
        time.sleep(2)
        return True
    else:
        stylelog.fail('iommu没有打开')
        SetUpLib.send_data_enter('reboot')
        time.sleep(2)
        return



def save_change_esc():
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    assert Update._change_options_value_part()
    time.sleep(1)
    SetUpLib.back_to_setup_toppage()
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    options=Update._get_options_value()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if options==SutConfig.Sup.CHANGED_VALUES:
        logging.info('通过ESC键保存修改退出成功')
        return True
    else:
        stylelog.fail('通过ESC键保存修改退出失败,{}'.format(options))
        return



def save_and_exit():
    assert SetUpLib.boot_to_setup()
    assert Update._change_options_value_part()
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(1)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SAVE_AND_EXIT], 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    options = Update._get_options_value()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if options == SutConfig.Sup.CHANGED_VALUES:
        logging.info('通过退出菜单的“保存并且退出”保存设置成功')
        return True
    else:
        stylelog.fail('通过退出菜单的“保存并且退出”保存设置失败,{}'.format(options))
        return



def load_default():
    count=0
    assert SetUpLib.boot_to_setup()
    assert Update._change_options_value_part()
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    options = Update._get_options_value()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if options==SutConfig.Sup.DEFAULT_OPTIONS:
        logging.info('通过“恢复初始值”恢复初始值成功')
        return True
    else:
        stylelog.fail('通过“恢复初始值”恢复初始值失败,{}'.format(options))
        return



def load_default_f9():
    assert SetUpLib.boot_to_setup()
    assert Update._change_options_value_part()
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    options = Update._get_options_value()
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(25)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if options == SutConfig.Sup.DEFAULT_OPTIONS:
        logging.info('通过F9恢复初始值成功')
        return True
    else:
        stylelog.fail('通过F9恢复初始值失败,{}'.format(options))
        return



def reboot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.REBOOT_SYSYTEM,10)
    time.sleep(1)
    SetUpLib.send_key(Key.Y)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        logging.info('重启系统成功')
        return True
    else:
        stylelog.fail('重启系统失败')
        return



def tpm():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.SET_FTPM,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_TPM2, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG):
        logging.info('打开FTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
    else:
        stylelog.fail('打开FTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count += 1
        BmcLib.init_sut()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.DEL)
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN):
            logging.info('进入SetUp')
        else:
            assert SetUpLib.boot_to_setup()
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_TCG2,18)
    if re.search('No Action', SetUpLib.get_data(3)):
        logging.info('一次启动后,TPM2操作变为无动作')
    else:
        stylelog.fail('一次启动后,TPM2操作没有变为无动作')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_TPM, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return



def update_unsign_bios():
    count=0
    assert SetUpLib.boot_with_hotkey(Key.F3,SutConfig.Msg.ENTER_BOOTMENU,200,SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.USB_UEFI,12,'UEFI Interactive Shell')
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(2)
    SetUpLib.send_data_enter('{0} {1}'.format(SutConfig.Upd.SHELL_FLASH_TOOL, SutConfig.Env.UNSIGN_BIOS_FILE))
    if SetUpLib.wait_message(SutConfig.Sup.UPDATE_UNSIGN_MSG):
        logging.info('Shell 下无法更新未签名的BIOS')
    else:
        stylelog.fail('Shell 下可以更新未签名的BIOS')
        count+=1
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    SetUpLib.execute_command("mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                    SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(1)
    result=SetUpLib.execute_command("{0} {1}{2}".format(SutConfig.Env.LINUX_FLASH_CMD, SutConfig.Env.LINUX_BIOS_MOUNT_PATH,
                                  SutConfig.Env.UNSIGN_BIOS_FILE),200)
    assert re.search(SutConfig.Sup.UPDATE_UNSIGN_MSG, result), "Linux 下可以更新未签名的BIOS"
    logging.info('Linux 下无法更新未签名的BIOS')
    time.sleep(4)
    SetUpLib.execute_command("umount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE,
                                                     SutConfig.Env.LINUX_USB_MOUNT))
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def aer_control():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_ERR_MAN,18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_ERR,18)
    if SetUpLib.wait_message('<Disabled> *Platform PCIE AER Report',5):
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(20)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        logging.info('AER 默认关闭')
        return True
    else:
        stylelog.fail('AER默认不是关闭')
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(20)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        return