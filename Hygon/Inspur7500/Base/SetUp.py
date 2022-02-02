#coding='utf-8'
import re
import os
import time
import subprocess
import logging
import pyautogui
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Base import Update
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from Inspur7500.BaseLib import SshLib
from batf.SutInit import Sut
from PIL import Image,ImageChops
from batf.Report import stylelog



def Interface_information():
    necessary_msg=['BIOS Vendor','BIOS Core Version','Mother Board Info','CPU Info','Memory Info','System Date and Time',
        'PCIE Info','USB Configuration','Console Redirection','Set Administrator Password','Set User Password','Hdd Password','User Wait Time',
        'PXE Option Rom','Boot Order','Save and Exit','Load Setup Defaults','BIOS Update Parameters','Shutdown System','Reboot System']
    count=0
    assert SetUpLib.boot_to_setup()
    SetUpLib.close_session()#关闭连接
    time.sleep(2)
    SetUpLib.open_session()#打开链接
    time.sleep(2)
    information=[]
    try_counts=12
    while try_counts:
        SetUpLib.close_session()  # 关闭连接
        time.sleep(1)
        SetUpLib.open_session()  # 打开连接
        time.sleep(1)
        data=SetUpLib.get_data(3,Key.RIGHT)
        information.append(data)
        if SutConfig.Msg.PAGE_MAIN_CN in data:
            break
        try_counts-=1
    information=' '.join(information)

    for i in necessary_msg:
        if i in information:
            logging.info('SetUp界面有{0}'.format(i))
        else:
            stylelog.fail('SetUp界面没有{0}'.format(i))
            count+=1
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.MEM_INFO_CN],5)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    if re.search('Total Memory',data) and re.search('Memory Frequency|内存当前频率',data):
        logging.info('内存信息中包含内存总容量和内存频率')
    else:
        stylelog.fail('内存信息中没有内存总容量和内存频率')
        count+=1
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.PCIE_INFO_CN],5)
    SetUpLib.send_key(Key.ENTER)
    if 'PCI Device Info' in SetUpLib.get_data(2):
        logging.info('PCIE信息中包含PCI设备信息')
    else:
        stylelog.fail('PCIE信息中没有PCI设备信息')
        count+=1
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED_CN)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.USB_CONFIG_CN],7)
    SetUpLib.send_key(Key.ENTER)
    if 'USB Mass Storage Support' in SetUpLib.get_data(2):
        logging.info('USB配置中包含USB存储设备支持')
    else:
        stylelog.fail('USB配置中没有USB存储设备支持')
        count+=1
    if count==0:
        return True
    else:
        return        



#修改板载网卡配置
def Onboard_Ethernet_Controller():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_LAN,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        datas=SetUpLib.get_data(10,Key.F11)
    else:
        logging.info('没有开机')
    if re.search(SutConfig.Msg.PXE_PORT1,datas):
        stylelog.fail('关闭板载网卡配置失败')
        return
    elif re.search(SutConfig.Msg.PXE_PORT2,datas):
        stylelog.fail('关闭板载网卡配置失败')
        return
    else:
        logging.info('关闭板载网卡配置成功')
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,20,SutConfig.Msg.PAGE_MAIN_CN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_PCI_INFO,10)
    if SetUpLib.wait_message('8088.*Ethernet controller',3,readline=True):
        stylelog.fail('板载网卡关闭，PCIE中仍有板载网卡')
        return
    else:
        logging.info('板载网卡关闭，PCIE中没有板载网卡')

    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_LAN,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        datas=SetUpLib.get_data(10,Key.F11)
    else:
        logging.info('没有开机')
    if re.search(SutConfig.Msg.PXE_PORT1,datas) and re.search(SutConfig.Msg.PXE_PORT1,datas):
        logging.info('打开板载网卡配置成功')
        return True
    else:
        stylelog.fail('打开板载网卡配置失败')
        return
    
        


#网络唤醒
def wake_online():
    mac=SutConfig.Sup.MAC_ADDRESS
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_WAKE_ONLINE,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    SshLib.execute_command_limit(Sut.OS_SSH,'shutdown -h now')
    time.sleep(15)
    try_counts=3
    while try_counts:
        subprocess.Popen(args='./Inspur7500/Tools/wakeonline/WakeMeOnLan.exe /wakeup {0}'.format(mac), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('发送唤醒命令')
        time.sleep(2)
        try_counts-=1

    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        stylelog.fail('网络唤醒关闭，但是成功唤醒')
        return
    logging.info('网络唤醒关闭，且无法唤醒')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_WAKE_ONLINE,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    SshLib.execute_command_limit(Sut.OS_SSH,'shutdown -h now')
    time.sleep(20)
    try_counts = 3
    while try_counts:
        subprocess.Popen(args='./Inspur7500/Tools/wakeonline/WakeMeOnLan.exe /wakeup {0}'.format(mac), shell=False,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('发送唤醒命令')
        time.sleep(2)
        try_counts -= 1
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        logging.info('网络唤醒打开，且成功唤醒')
        return True
    else:
        stylelog.fail('网络唤醒打开，未成功唤醒')
        return



#USB存储设备支持
def usb_mass_storage_support():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_USB_STORAGE,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        datas=SetUpLib.get_data(10,Key.F11)

    else:
        logging.info('没有开机')
    if SutConfig.Msg.USB_UEFI not in datas:
        logging.info('USB存储设备支持关闭，启动项中没有USB')
    else:
        stylelog.fail('USB存储设备支持关闭，启动项中仍有USB')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.LINUX_OS,20,'')
    assert BmcLib.ping_sut()
    result=SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(SutConfig.Env.LINUX_USB_DEVICE, SutConfig.Env.LINUX_USB_MOUNT))
    if len(result[0])==len(result[1])==0:
        logging.info('USB存储设备关闭，setup下识别不了U盘，系统下能正常识别U盘')
    else:
        stylelog.fail('USB存储设备关闭，setup下识别不了U盘，系统下不能正常识别U盘')
        return

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_STORAGE,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        datas=SetUpLib.get_data(10,Key.F11)
        datas=datas.split('Startup Device Menu')[1]
    else:
        logging.info('没有开机')
    if SutConfig.Msg.USB_UEFI in datas:
        logging.info('USB存储设备支持打开，启动项中有USB')
        return True
    else:
        stylelog.fail('USB存储设备支持打开，启动项中没有USB')
        return
 

    
#USB 端口配置
def usb_port_configuration():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_PORT_BOTH,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
    datas=SetUpLib.get_data(3)
    if re.compile('USB Front Port').findall(datas) and re.compile('USB Back Port').findall(datas):
        logging.info('前置USB口，后置USB口都有USB设备')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_PORT_FRONT,3)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
        data = SetUpLib.get_data(3)
        if re.compile('USB Front Port').findall(data) and not re.compile('USB Back Port').findall(data):
            logging.info('前置USB端口打开，后置USB端口关闭，USB设备列表中没有后置USB设备')
        else:
            stylelog.fail('前置USB端口打开，后置USB端口关闭，USB设备列表中仍有后置USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_PORT_BEHIND,3)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Front Port').findall(data) and re.compile('USB Back Port').findall(data):
            logging.info('前置USB端口关闭，后置USB端口打开，USB设备列表中没有前置USB设备')
        else:
            stylelog.fail('前置USB端口关闭，后置USB端口打开，USB设备列表中仍有前置USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_USB_PORT_BOTH,3)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Front Port').findall(data) and not re.compile('USB Back Port').findall(data):
            logging.info('前置USB端口关闭，后置USB端口关闭，USB设备列表中没有USB设备')
        else:
            stylelog.fail('前置USB端口关闭，后置USB端口关闭，USB设备列表中仍有USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_PORT_ALL,3)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        return True
    elif re.compile('USB Front Port').findall(datas):
        logging.info('前置USB口有USB设备')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_USB_PORT_FRONT,3)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Front Port').findall(data) and not re.compile('USB Back Port').findall(data):
            logging.info('前置USB端口关闭，USB设备列表中没有USB设备')
        else:
            stylelog.fail('前置USB端口关闭，USB设备列表中仍有USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_USB_PORT_FRONT_ONLY,3)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        return True
    elif re.compile('USB Back Port').findall(datas):
        logging.info('U盘在后置USB口')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_USB_PORT_BEHIND,3)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_USB_INFO,10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Back Port').findall(data) and not re.compile('USB Front Port').findall(data):
            logging.info('后置USB端口关闭，USB设备列表中没有USB设备')
        else:
            stylelog.fail('后置USB端口关闭，USB设备列表中仍有USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_BEHIND_ONLY, 3)

        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        return True
    else:
        stylelog.fail('USB存储设备支持打开，但是没有找到USB存储设备')
        return



#硬盘绑定
def HDD_bind():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.HDD_BIND1,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11,SutConfig.Msg.ENTER_BOOTMENU_CN,200,SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    if SetUpLib.select_boot_option(Key.DOWN,SutConfig.Sup.HDD_BIND_NAME_2_OS[0],20,SutConfig.Sup.HDD_BIND_PROMPT):
        logging.info('硬盘绑定打开，无法进入绑定外的硬盘')
    else:
        stylelog.fail('绑定硬盘，但仍可以进入绑定外的硬盘')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Sup.HDD_BIND_NAME_1_OS[0],20,'')
    if BmcLib.ping_sut():
        logging.info('成功进入绑定的硬盘')
    else:
        stylelog.fail('没有进入绑定的硬盘')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HDD_BIND2, 10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    if SetUpLib.select_boot_option(Key.DOWN, SutConfig.Sup.HDD_BIND_NAME_1_OS[0], 20, SutConfig.Sup.HDD_BIND_PROMPT):
        logging.info('硬盘绑定打开，无法进入绑定外的硬盘')
    else:
        stylelog.fail('绑定硬盘，但仍可以进入绑定外的硬盘')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Sup.HDD_BIND_NAME_2_OS[0], 20,'')
    if BmcLib.ping_sut():
        logging.info('成功进入绑定的硬盘')
    else:
        stylelog.fail('没有进入绑定的硬盘')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HDD_BIND3, 10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True



#安全启动
def secure_boot():
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SECURE_BOOT,10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SECURE_BOOT,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, 'UEFI Interactive Shell')
    time.sleep(15)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    SetUpLib.send_data('ByoShellFlash.efi bfu -bu backup.bin')
    time.sleep(2)
    if SetUpLib.wait_message_enter('Command Error Status: Security Violation', 3):
        logging.info('安全启动打开，无法使用BIOS刷新工具')
    else:
        stylelog.fail('安全启动打开，仍可以使用BIOS刷新工具')
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.CLOSE_SECURE_BOOT,10)
    
    time.sleep(1)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count == 0:
        return True
    else:
        return



#安静启动
def quiet_boot():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_QUIET_BOOT,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(1)
    SetUpLib.open_session()  # 打开链接
    time.sleep(1)
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if 'Press Key in' in data:
            break
        now = time.time()
        spent_time = (now - start_time)
        if spent_time > 150:
            break
    SetUpLib.send_key(Key.DEL)
    if 'BIOS Version:' not in ''.join(datas):
        logging.info('安静启动打开，启动界面未出现配置信息')
    else:
        stylelog.fail('安静启动打开，启动界面仍出现配置信息')
        return
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN):
        logging.info('进入setup')
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY_CN)
    SetUpLib.send_key(Key.RIGHT)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_QUIET_BOOT, 10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message('BIOS Version:',readline=True):
        logging.info('安静启动关闭，启动界面出现配置信息')
        return True
    
    

#用户等待时间
def user_wait_time():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT_CN)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('10')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)   
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message('Press Key in 10 seconds',readline=True):
        logging.info('修改用户等待时间成功')
    else:
        stylelog.fail('修改用户等待时间失败')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT_CN)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('6')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)   
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message('Press Key in 6 seconds',readline=True):
        logging.info('修改用户等待时间成功')
        return True
    else:
        stylelog.fail('修改用户等待时间失败')
        return



#SPI BIOS 锁住
def spi_bios_lock():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SPI,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(4)
    assert SetUpLib.boot_with_hotkey(Key.F11,SutConfig.Msg.ENTER_BOOTMENU_CN,200,SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, 'UEFI Interactive Shell'), '没有找到Shell'
    time.sleep(10)
    logging.info('成功进入Shell')
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    SetUpLib.send_data_enter('ByoShellFlash.efi bfu -bu backup.bin')
    assert SetUpLib.wait_message('SPI BIOS is Locked in Setup',5),'没有找到SPI BIOS is Locked in Setup'
    logging.info('BIOS 锁住，无法备份BIOS')

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SPI,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.boot_with_hotkey(Key.F11,SutConfig.Msg.ENTER_BOOTMENU_CN,200,SutConfig.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 20, 'UEFI Interactive Shell'), '没有找到Shell'
    time.sleep(10)
    logging.info('成功进入Shell')
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    SetUpLib.send_data_enter('ByoShellFlash.efi bfu -bu backup.bin')
    assert SetUpLib.wait_message('Reading Bios................Successed!')
    logging.info('关闭BIOS锁住，成功备份BIOS')
    return True



def iommu():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_IOMMU,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    cmd_result1=SshLib.execute_command_limit(Sut.OS_SSH,'cat /etc/issue')
    logging.info(cmd_result1[0])
    cmd_result2=SshLib.execute_command_limit(Sut.OS_SSH,'dmesg | grep -i iommu')
    logging.info(cmd_result2[0])
    #系统类型不同，判断结果的关键字不同
    if SutConfig.Sup.OS_TYPE in cmd_result1[0]:
        if SutConfig.Sup.IOMMU_DISABLED_INFO in cmd_result2[0]:
            logging.info('iommu关闭')
        else:
            stylelog.fail('iommu没有关闭')
            return
    else:
        if len(cmd_result2[0])==0 and len(cmd_result2[1])==0:
            logging.info('iommu关闭')
        else:
            stylelog.fail('iommu没有关闭')
            return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_IOMMU,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    cmd_result=SshLib.execute_command_limit(Sut.OS_SSH, "dmesg | grep -i iommu")

    cmd_result=cmd_result[0]
    if SutConfig.Sup.IOMMU_ENABLED_INFO in cmd_result:
        logging.info('iommu打开')
        return True
    else:
        stylelog.fail('iommu没有打开')
        return



def svm():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SVM,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, 'dmesg | grep kvm')
    logging.info(cmd_result)
    cmd_result = cmd_result[0]
    if SutConfig.Sup.SVM_DISABLED_INFO in cmd_result:
        logging.info('Svm关闭')
    else:
        stylelog.fail('Svm没有关闭')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SVM,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, 'dmesg | grep kvm')
    cmd_result = cmd_result[0]
    if 'enabled' in cmd_result:
        logging.info('Svm打开')
        return True
    else:
        stylelog.fail('Svm没有打开')
        return



def sriov():
    ETHERNET_NAME=SutConfig.Sup.ETHERNET_NAME
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SR,10)
    
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH,
                                            'echo 2 > /sys/class/net/{0}/device/sriov_numvfs'.format(ETHERNET_NAME))
    logging.info(cmd_result)

    if len(cmd_result[1]) != 0:
        if '错误' or 'error' in cmd_result[1]:
            logging.info('SR-IOV关闭')
        else:
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SR,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH,
                                      "echo 2 > /sys/class/net/{0}/device/sriov_numvfs".format(ETHERNET_NAME))
    logging.info(cmd_result)

    if len(cmd_result[0]) == 0 and len(cmd_result[1]) == 0:
        cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, 'cat /etc/issue')
        logging.info(cmd_result1)
        cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Et")
        logging.info(cmd_result2)
        if SutConfig.Sup.OS_TYPE in cmd_result1[0]:
            if 'Ethernet Controller Virtual Function' in cmd_result2[0]:
                logging.info('SR-IOV打开')
                return True
            else:
                return
        else:
            if 'Ethernet controller: Device 8088:0119' in cmd_result2[0]:
                logging.info('SR-IOV打开')
                return True
            else:
                return
    else:
        return



def memory_speed():
    count=0
    speeds=SutConfig.Sup.MEMORY_SPEED
    for speed in speeds:
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(2)
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_HYGON,18)
        assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Sup.MEMORY_SPEED_NAME],4,'{0}MHz'.format(speed))
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_MEM,8)
        memoryspeed=re.findall('Memory [a-zA-Z]* *Frequency.*?([0-9]+) MHz',SetUpLib.get_data(3))[0]
        if memoryspeed==str(int(speed)*2) or memoryspeed==str(int(speed)*2-1):
            logging.info('修改内存频率为{0}MHz,SetUp下内存信息显示{1}MHz'.format(speed,memoryspeed))
        else:
            stylelog.fail('修改内存频率为{0}MHz,SetUp下内存信息显示{1}MHz'.format(speed,memoryspeed))
            count+=1
    if count==0:
        return True
    else:
        return
    


def save_change_esc():
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_VIRTU,10)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV',data):
        logging.info('ESC键保存设置成功')
    else:
        stylelog.fail('ESC键保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        count+=1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_VIRTU,4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return


def save_change():
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_VIRTU,10)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV',data):
        logging.info('通过退出菜单的“保存修改”保存设置成功')
    else:
        stylelog.fail('通过退出菜单的“保存修改”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        count+=1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_VIRTU,4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return

def save_and_exit():
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_VIRTU,10)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SAV_EXI,10)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV',data):
        logging.info('通过退出菜单的“保存并且退出”保存设置成功')
    else:
        stylelog.fail('通过退出菜单的“保存并且退出”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        count+=1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_VIRTU,4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return





def exit_without_save():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_VIRTU,10)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_NO_SAV_EXI,10)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<Enabled> *IOMMU *<Enabled> *SVM *<Enabled> *SR\-IOV',data):
        logging.info('通过退出菜单的“不保存并且退出”设置没有被保存')
    else:
        stylelog.fail('通过退出菜单的“不保存并且退出”设置被保存,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_VIRTU,4)
     
        count+=1
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return



def load_default():
    default = SutConfig.Sup.VIRTUALIZATION_DEFAULT
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_VIRTU,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV',data):
        logging.info('设置更改成功')
    else:
        stylelog.fail('设置更改失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.LOAD_DEFAULTS_CN],7)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<{0}> *IOMMU *<{1}> *SVM *<{2}> *SR\-IOV'.format(default[0],default[1],default[2]),data):
        logging.info('通过“恢复初始值”恢复初始值成功')
        return True
    else:
        stylelog.fail('通过“恢复初始值”恢复初始值失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        return




def load_default_f9():
    default = SutConfig.Sup.VIRTUALIZATION_DEFAULT
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_VIRTU,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV',data):
        logging.info('设置更改成功')
    else:
        stylelog.fail('设置更改失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data=SetUpLib.get_data(2)
    if re.search('<{0}> *IOMMU *<{1}> *SVM *<{2}> *SR\-IOV'.format(default[0],default[1],default[2]),data):
        logging.info('通过F9恢复初始值成功')
        return True
    else:
        stylelog.fail('通过F9恢复初始值失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        return



def check_default_bios():

    assert SetUpLib.boot_to_setup()
    time.sleep(3)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    default_options=Update._get_options_value()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.SET_UPDATE_ALL,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.UPDATE_BIOS_PATH,18,'Confirmation')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Flash is updated successfully!',300):
        logging.info('BIOS 刷新成功')

    time.sleep(120)
    BmcLib.enable_serial_only()
    assert SetUpLib.boot_to_setup()
    updated_options=Update._get_options_value()  
    logging.info('默认值为{0}'.format(default_options))
    logging.info('全刷BIOS后的值为{0}'.format(updated_options))
    
    if updated_options==default_options:
        logging.info('全刷方式刷新BIOS后，默认值与F9恢复默认值的结果相同')
        return True
    else:
        logging.info('SetUp下完全刷新，刷新BIOS后配置改变,改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info(i)
        for i in default_options:
            if i not in updated_options:
                logging.info(i)
        return


def sata_controller():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SATA,8)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SATA,10)
    time.sleep(1)
    try_counts = 100
    while try_counts:
        SetUpLib.send_key(Key.DOWN)
        data = SetUpLib.get_data(1)
        if 'M.2 Driver 1' in data:
            break
        try_counts -= 1
    data = data.split('Asmedia Controller')[1]
    if re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
        logging.info('Asmedia控制器1061R_A，Asmedia控制器1061R_B都连接设备')
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SATA_A,4)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SATA,10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and  re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_A，SATA配置下SATA端口被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_A，SATA配置下SATA端口没有被关闭')
            count+=1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SATA_B,4)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SATA,10)
        time.sleep(1)
        try_counts=100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts-=1
        data = data.split('Asmedia Controller')[1]
        if re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and not re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_B，SATA配置下M.2端口被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_B，SATA配置下M.2端口没有被关闭')
            count+=1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SATA,4)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SATA,10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and not re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_A和Asmedia控制器1061R_B，SATA配置下SATA端口和M.2端口都被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_A和Asmedia控制器1061R_B，SATA配置下SATA端口和M.2端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SATA,5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
    elif re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and not re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
        logging.info('Asmedia控制器1061R_A连接设备，Asmedia控制器1061R_B没有连接设备')
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)

        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SATA_A,5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SATA,10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data):
            logging.info('关闭Asmedia控制器1061R_A，SATA配置下SATA端口被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_A，SATA配置下SATA端口没有被关闭')
            count+=1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SATA,5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
    elif not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and  re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
        logging.info('Asmedia控制器1061R_A没有连接设备，Asmedia控制器1061R_B连接设备')
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)

        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.CLOSE_SATA_B,5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Sup.LOC_SATA,10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if not re.compile('M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_B，SATA配置下M.2端口被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_B，SATA配置下M.2端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.OPEN_SATA,5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
    else:
        stylelog.fail('Asmedia控制器1061R_A,Asmedia控制器1061R_B都没有连接设备')
        return
    if count==0:
        return True

    else:
        return


def tpm():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.SET_DTPM,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_TPM2, 18)
    time.sleep(1)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if re.search('TPM Version *{0}'.format(SutConfig.Sup.DTPM_MSG),SetUpLib.get_data(2)):
        logging.info('打开DTPM，SetUp下显示{0}'.format(SutConfig.Sup.DTPM_MSG))
    else:
        stylelog.fail('打开DTPM，SetUp下没有显示{0}'.format(SutConfig.Sup.DTPM_MSG))
        count+=1
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG,readline=True):
        logging.info('打开DTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
    else:
        stylelog.fail('打开DTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count+=1
        BmcLib.init_sut()
    assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.LINUX_OS,20,'')
    if BmcLib.ping_sut():
        logging.info('成功启动到系统')
    else:
        return
    cmd_result=SshLib.execute_command_limit(Sut.OS_SSH,"dmesg | grep -i tpm")
    cmd_result=cmd_result[0]
    if re.search(SutConfig.Sup.DTPM_OS_MSG,cmd_result):
        logging.info('打开DTPM,系统下显示{}'.format(SutConfig.Sup.DTPM_OS_MSG))
    else:
        stylelog.fail('打开DTPM,系统下没有显示{}'.format(SutConfig.Sup.DTPM_OS_MSG))
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Sup.LOC_TCG2,18)
    SetUpLib.send_key(Key.ENTER)
    if re.search('No Action',SetUpLib.get_data(3)):
        logging.info('一次启动后,TPM2操作变为无动作')
    else:
        stylelog.fail('一次启动后,TPM2操作没有变为无动作')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.SET_FTPM,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_TPM2, 18)
    time.sleep(1)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if re.search('TPM Version *{0}'.format(SutConfig.Sup.FTPM_MSG),SetUpLib.get_data(2)):
        logging.info('打开FTPM，SetUp下显示{0}'.format(SutConfig.Sup.FTPM_MSG))
    else:
        stylelog.fail('打开FTPM，SetUp下没有显示{0}'.format(SutConfig.Sup.FTPM_MSG))
        count+=1
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG,readline=True):
        logging.info('打开DTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
    else:
        stylelog.fail('打开DTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count += 1
        BmcLib.init_sut()
    assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU_CN, 200, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 20, '')
    if BmcLib.ping_sut():
        logging.info('成功启动到系统')
    else:
        return

    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "dmesg | grep -i tpm")
    
    cmd_result = cmd_result[0]
    if re.search(SutConfig.Sup.FTPM_OS_MSG, cmd_result):
        logging.info('打开DTPM,系统下显示{}'.format(SutConfig.Sup.FTPM_OS_MSG))
    else:
        stylelog.fail('打开DTPM,系统下没有显示{}'.format(SutConfig.Sup.FTPM_OS_MSG))
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    SetUpLib.send_key(Key.ENTER)
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



def locateonscreen(img='img/chrome.png', delay=150):
    start_time = time.time()
    while True:
        location = pyautogui.locateOnScreen(img)
        if location != None:
            return True
        time.sleep(1)
        now = time.time()
        spent_time = (now - start_time)
        if spent_time > delay:
            break
    return



def boot_logo():
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HIDE_BOOT_LOGO, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    logging.info('Found {}'.format(SutConfig.Msg.POST_MESSAGE))
    if pyautogui.locateOnScreen(SutConfig.Sup.LOGO_PATH, grayscale=True) != None:
        stylelog.fail('隐藏开机Logo,post界面仍出现Logo')

    else:
        logging.info('隐藏开机Logo,post界面未出现Logo')
    assert SetUpLib.boot_os_from_bm()
    type1 = SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t 1")[0]
    time.sleep(1)
    type2 = SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t 2")[0]
    time.sleep(1)
    type3 = SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t 3")[0]

    if not re.search(SutConfig.Sup.MANUFACTOURER, type1 + type2 + type3) and not re.search(
            SutConfig.Sup.MANUFACTOURER.lower(), type1 + type2 + type3):
        logging.info('Smbios type1,type2,type3,不显示制造商')
    else:
        logging.info('Smbios 显示制造商,type1{0},type2{1},type3{2}'.format(re.findall('Manufacturer: ([a-zA-Z]+)', type1),
                                                                      re.findall('Manufacturer: ([a-zA-Z]+)', type2),
                                                                      re.findall('Manufacturer: ([a-zA-Z]+)', type3)))
        return
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SHOW_BOOT_LOGO, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    logging.info('Found {}'.format(SutConfig.Msg.POST_MESSAGE))
    if pyautogui.locateOnScreen(SutConfig.Sup.LOGO_PATH, grayscale=True) != None:
        logging.info('展示开机Logo，post界面出现Logo')
        return True
    else:
        stylelog.fail('展示开机Logo，post界面未出现Logo')



def link_relation():
    count = -0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_LEGACY, 18)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Sup.UEFI_HII, 2, readline=True):
        stylelog.fail('启动模式Legacy,UEFI HII 配置菜单没有被隐藏')
        count += 1
    else:
        logging.info('启动模式Legacy,UEFI HII 配置菜单被隐藏')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SECURE_BOOT, 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    if SetUpLib.wait_message('<Enabled> *Secure Boot', 3, readline=True):
        logging.info('安全启动打开')
    else:
        stylelog.fail('安全启动关闭')
        count += 1
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('<UEFI> *Boot Mode', 3, readline=True):
        logging.info('Legacy 下打开安全启动,启动模式变为UEFI')
    else:
        stylelog.fail('Legacy 下打开安全启动,启动模式没有变为UEFI')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_LEGACY, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_SECURE_BOOT, 10)
    if SetUpLib.wait_message('<Disabled> *Secure Boot', 3, readline=True):
        logging.info('启动模式更改为Legacy,安全启动关闭')
    else:
        stylelog.fail('启动模式更改为Legacy,安全启动没有关闭')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PXE_OPTION, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    data = SetUpLib.get_data(2)
    if not re.search('{0}|{1}|{2}|{3}'.format(SutConfig.Msg.PXE_NETWORK_CN, SutConfig.Msg.PXE_RETRY_CN,
                                              SutConfig.Msg.PXE_IP_VER_CN, SutConfig.Msg.PXE_BOOT_PRIOROTY), data):
        logging.info('关闭网络引导,没有出现{0}，{1}，{2}，{3}'.format(SutConfig.Msg.PXE_NETWORK_CN, SutConfig.Msg.PXE_RETRY_CN,
                                                         SutConfig.Msg.PXE_IP_VER_CN, SutConfig.Msg.PXE_BOOT_PRIOROTY))

    else:
        stylelog.fail('关闭网络引导,仍出现')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PXE_STACK, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_UEFI_HII, 18)
    if not SetUpLib.wait_message('Ipv4|Ipv6|VLAN', 3):
        logging.info('网络协议栈关闭,UEFI HII 配置菜单不显示,Ipv4,Ipv6,VLAN')
    else:
        stylelog.fail('网络协议栈关闭,UEFI HII 配置菜单仍显示,Ipv4,Ipv6,VLAN')
        count += 1
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.CLOSE_SECURE_BOOT, 10)

    time.sleep(1)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PXE_OPTION, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count == 0:
        return True
    else:
        return



def option_rom():
    assert SetUpLib.boot_to_setup()

    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_OPTION_ROM, 15)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    time.sleep(1)
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if SutConfig.Msg.HOTKEY_PROMPT_DEL in data:
            break
        now = time.time()
        spent_time = (now - start_time)
        if spent_time > 200:
            break

    data = ''.join(datas)
    if re.search(SutConfig.Sup.ONBOARD_MSG, data):
        logging.info('Option Rom  中有板载网卡信息')
    else:
        stylelog.fail('Option Rom  中没有板载网卡信息')
        return
    if re.search(SutConfig.Sup.ASMEDIA_MSG, data):
        logging.info('Option Rom  中有Asmedia信息')
    else:
        stylelog.fail('Option Rom  中没有Asmedia信息')
        return
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN, 20):
        logging.info('进入SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_OPTION_ROM, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    time.sleep(1)
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if SutConfig.Msg.HOTKEY_PROMPT_DEL in data:
            break
        now = time.time()
        spent_time = (now - start_time)
        if spent_time > 200:
            break

    data = ''.join(datas)

    if not re.search(SutConfig.Sup.ONBOARD_MSG, data) and not re.search(SutConfig.Sup.ASMEDIA_MSG, data):
        logging.info('关闭OPtion Rom ,Post隐藏Option Rom')
    else:
        stylelog.fail('关闭OPtion Rom ,Post没有隐藏Option Rom')
        return

    SetUpLib.send_key(Key.DEL)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN, 20):
        logging.info('进入SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_UEFI, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    return True

