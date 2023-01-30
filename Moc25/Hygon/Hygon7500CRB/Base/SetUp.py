#coding='utf-8'
import re
import os
import time
import subprocess
import logging
import pyautogui
from Hygon7500CRB.BaseLib import BmcLib,SetUpLib
# from Hygon.Base import Update
from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig, Sut01Config
from Hygon7500CRB.BaseLib import SshLib
from batf.SutInit import Sut
from PIL import Image,ImageChops
from batf.Report import stylelog



def Interface_information():
    necessary_msg=['BIOS Vendor','BIOS Version','Release Version','CPU Info','Memory Info','System Date and Time',
        'PCI Device Info','USB Configuration','Console Redirection','Set Administrator Password',
        'Set User Password','HDD Password','User Wait Time','Network Boot','Save and Exit',
        'Load Setup Defaults','BIOS Update','Shutdown System','Reboot System']
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
        data=SetUpLib.get_data(3, Key.RIGHT)
        information.append(data)
        if Sut01Config.Msg.PAGE_MAIN in data:
            break
        try_counts-=1
    information=' '.join(information)
    for i in necessary_msg:
        if i in information:
            logging.info('SetUp界面有{0}'.format(i))
        else:
            stylelog.fail('SetUp界面没有{0}'.format(i))
            count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, Sut01Config.Setup.IN_MEMORY_INFO,6)
    if 'Total Memory' in SetUpLib.get_data(2):
        logging.info('内存信息中包含内存总容量')
    else:
        stylelog.fail('内存信息中没有内存总容量')
        count+=1
    if count==0:
        return True
    else:
        return        
    

    
#USB端口配置
def usb_port_configuration():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_USB_CONFIG,6)
    time.sleep(1)
    datas = SetUpLib.get_data(1)
    data = len(re.findall(':',datas)) - 2
    if data == 3:
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_USB1_DISABLED,6)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.Setup.IN_USB_CONFIG,6)
        time.sleep(1)
        datas = SetUpLib.get_data(1)
        data = len(re.findall(':', datas)) - 2
        if data == 2:
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_USB0_DISABLED,6)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_USB_CONFIG,6)
            time.sleep(1)
            datas = SetUpLib.get_data(1)
            data = len(re.findall(':', datas)) - 2
            if data == 0:
                logging.info('两个端口正常')
                assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.Setup.SET_USB_ENABLED,6)
                time.sleep(1)
                SetUpLib.send_keys(Key.SAVE_RESET)
                return True
            else:
                stylelog.fail('USB0号端口异常')
                return
        else:
            stylelog.fail('USB1号端口异常')
            return
    else:
        stylelog.fail('没有USB设备')
        return



def iommu():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Setup.SET_IOMMU_DISABLED,20)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    while True:
        cmd_result1=SshLib.execute_command(Sut.OS_SSH,'cat /etc/issue')
        logging.info(cmd_result1[0])
        cmd_result2=SshLib.execute_command(Sut.OS_SSH,'dmesg | grep -i iommu')
        logging.info(cmd_result2[0])
        if cmd_result1 and cmd_result2:
            break
    #系统类型不同，判断结果的关键字不同
    if Sut01Config.Msg.OS_TYPE in cmd_result1[0]:
        if Sut01Config.Msg.IOMMU_DISABLED_INFO in cmd_result2[0]:
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
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_IOMMU_ENABLED,20)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH, "dmesg | grep -i iommu")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    if Sut01Config.Msg.IOMMU_ENABLED_INFO in cmd_result:
        logging.info('iommu打开')
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_IOMMU_AUTO,20)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        stylelog.fail('iommu没有打开')
        return



#硬盘绑定
def HDD_bind():
    # assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.Setup.HDD1_BIND,9)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7,Sut01Config.Msg.ENTER_BOOTMENU_CN,200,Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    if SetUpLib.select_boot_option(Key.DOWN,Sut01Config.Msg.HDD_BIND_NAME_2_OS[0],20,Sut01Config.Msg.HDD_BIND_PROMPT):
        logging.info('硬盘绑定打开，无法进入绑定外的硬盘')
    else:
        stylelog.fail('绑定硬盘，但仍可以进入绑定外的硬盘')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.boot_with_hotkey(Key.F7,Sut01Config.Msg.ENTER_BOOTMENU_CN,200,Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN,Sut01Config.Msg.HDD_BIND_NAME_1_OS[0],20,'')
    if BmcLib.ping_sut():
        logging.info('成功进入绑定的硬盘')
    else:
        stylelog.fail('没有进入绑定的硬盘')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Setup.HDD2_BIND,9)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.ENTER_BOOTMENU_CN, 200, Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    if SetUpLib.select_boot_option(Key.DOWN, Sut01Config.Msg.HDD_BIND_NAME_1_OS[0], 20, SutConfig.Msg.HDD_BIND_PROMPT):
        logging.info('硬盘绑定打开，无法进入绑定外的硬盘')
    else:
        stylelog.fail('绑定硬盘，但仍可以进入绑定外的硬盘')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.ENTER_BOOTMENU_CN, 200,Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.HDD_BIND_NAME_2_OS[0], 20,'')
    if BmcLib.ping_sut():
        logging.info('成功进入绑定的硬盘')
    else:
        stylelog.fail('没有进入绑定的硬盘')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.HDD_UNBIND,9)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True
    
    

#安全启动
def secure_boot():
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_SECURE_BOOT_AUTO,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_with_hotkey(Key.F7, Sut01Config.Msg.ENTER_BOOTMENU_CN, 200, Sut01Config.Msg.HOTKEY_PROMPT_F11_CN)
    assert SetUpLib.select_boot_option(Key.DOWN, Sut01Config.Msg.SHELL, 20, 'UEFI Interactive Shell')

    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(Sut01Config.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd BIOS')
    time.sleep(2)
    SetUpLib.send_data('ByoFlash.efi bfu -bu backup.bin')
    if SetUpLib.wait_message_enter('Command Error Status: Access Denied', 3):
        logging.info('安全启动打开，无法使用BIOS刷新工具')
    else:
        stylelog.fail('安全启动打开，仍可以使用BIOS刷新工具')
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, Sut01Config.Setup.SET_SECURE_BOOT_MANUAL, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count == 0:
        return True
    else:
        return



#用户等待时间
def user_wait_time():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_USER_WAIT_TIME,3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('5')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Setup.SET_BOOT_FILTER,10)
    time.sleep(1)
    assert SetUpLib.locate_option(Key.DOWN,['Others'], 15)
    SetUpLib.send_key(Key.ADD)
    time.sleep(1)
    SetUpLib.send_key(Key.ADD)
    time.sleep(1)
    SetUpLib.send_key(Key.ADD)
    time.sleep(1)
    SetUpLib.send_key(Key.ADD)
    time.sleep(1)
    SetUpLib.send_key(Key.ADD)
    time.sleep(1)
    SetUpLib.send_key(Key.ADD)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        start = time.time()
        if SetUpLib.wait_message('UEFI Interactive Shell'):
            end = time.time()
            times = end - start
            print(times)
            if 5 < times < 13:
                logging.info('修改用户等待时间5秒成功')
            else:
                stylelog.fail('修改用户等待时间5秒失败')
                return
        else:
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_USER_WAIT_TIME,3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('10')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        start = time.time()
        if SetUpLib.wait_message('UEFI Interactive Shell'):
            end = time.time()
            times = end - start
            print(times)
            if 10 < times < 17:
                logging.info('修改用户等待时间10秒成功')
            else:
                stylelog.fail('修改用户等待时间10秒失败')
                return
        else:
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_USER_WAIT_TIME,3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('20')
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        start = time.time()
        if SetUpLib.wait_message('UEFI Interactive Shell'):
            end = time.time()
            times = end - start
            print(times)
            if 20 < times < 28:
                logging.info('修改用户等待时间20秒成功')
                assert SetUpLib.boot_to_setup()
                assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_USER_WAIT_TIME,3)
                assert SetUpLib.locate_option(Key.DOWN, ['Others'], 15)
                SetUpLib.send_key(Key.SUBTRACT)
                time.sleep(1)
                SetUpLib.send_key(Key.SUBTRACT)
                time.sleep(1)
                SetUpLib.send_key(Key.SUBTRACT)
                time.sleep(1)
                SetUpLib.send_key(Key.SUBTRACT)
                time.sleep(1)
                SetUpLib.send_key(Key.SUBTRACT)
                time.sleep(1)
                SetUpLib.send_key(Key.SUBTRACT)
                time.sleep(1)
                SetUpLib.send_key(Key.RIGHT)
                time.sleep(2)
                SetUpLib.send_keys(Key.SAVE_RESET)
                return True
            else:
                stylelog.fail('修改用户等待时间20秒失败')
                return
        else:
            return
    else:
        return



def svm():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_SVM_DISABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep kvm')
        # logging.info(cmd_result)
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    if Sut01Config.Msg.SVM_DISABLED_INFO in cmd_result:
        logging.info('Svm关闭成功')
    else:
        stylelog.fail('Svm没有关闭')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_SVM_ENABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep kvm')
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    if 'enabled' in cmd_result:
        logging.info('Svm打开成功')
        return True
    else:
        stylelog.fail('Svm没有打开')
        return



def sriov():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_SR_IOV_DISABLED,9)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    while True:
        SshLib.execute_command(Sut.OS_SSH, 'echo 2 > /sys/class/net/ens8f0/device/sriov_numvfs')
        time.sleep(3)
        cmd_result = SshLib.execute_command(Sut.OS_SSH, 'dmesg')
        # logging.info(cmd_result)
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    if Sut01Config.Msg.SRIOV_DISABLED_INFO in cmd_result:
        logging.info('SRIOV关闭成功')
    else:
        stylelog.fail('SRIOV没有关闭')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_SR_IOV_ENABLED,9)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    SetUpLib.boot_os_from_bm()
    while True:
        SshLib.execute_command(Sut.OS_SSH, 'echo 2 > /sys/class/net/ens8f0/device/sriov_numvfs')
        time.sleep(3)
        cmd_result = SshLib.execute_command(Sut.OS_SSH, 'dmesg')
        # logging.info(cmd_result)
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    if Sut01Config.Msg.SRIOV_DISABLED_INFO not in cmd_result:
        logging.info('SRIOV打开成功')
        return True
    else:
        stylelog.fail('SRIOV打开失败')
        return



def memory_speed():
    count=0
    speeds=Sut01Config.Msg.MEMORY_SPEED
    assert SetUpLib.boot_to_setup()
    for speed in speeds:
        assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.Setup.SET_MEMORY_SPEED,20)
        time.sleep(2)
        assert SetUpLib.select_option_value(Key.DOWN,[SutConfig.Setup.MEMORY_CLOCK_SPEED],Key.DOWN,'{0}MHz'.format(speed),9)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, Sut01Config.Setup.IN_MEMORY_INFO,6)
        memoryspeed=re.findall(r'Memory Speed .*?([0-9]+) MT/s',SetUpLib.get_data(3))[0]
        if memoryspeed==str(int(speed)*2) or memoryspeed==str(int(speed)*2-1):
            logging.info(r'修改内存频率为{0}MHz,SetUp下内存信息显示{1}MT/s'.format(speed,memoryspeed))
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail(r'修改内存频率为{0}MHz,SetUp下内存信息显示{1}MT/s'.format(speed,memoryspeed))
            count+=1
    if count==0:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, Sut01Config.Setup.SET_MEMORY_SPEED_AUTO,20)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        return



def save_change_esc():
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SAVE_CHANGE_ESC_DISABLED, 8)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    data=SetUpLib.get_data(2)
    # print(data)
    if re.search('<Disabled> *SVM Control *<Disabled> *P-State Control *<Disabled> *SR-IOV Support',data):
        logging.info('ESC键保存设置成功')
    else:
        stylelog.fail('ESC键保存设置失败,SVM Control:{0},P\-State Control:{1},SR\-IOV Support:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        count+=1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SAVE_CHANGE_ENABLED, 8)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return



def save_and_exit():
    count=0
    assert SetUpLib.boot_to_setup()
    time.sleep(3)
    SetUpLib.close_session()  # 关闭连接
    time.sleep(2)
    SetUpLib.open_session()  # 打开链接
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, Sut01Config.Setup.SAVE_CHANGE_EXIT_DISABLED,10)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    data=SetUpLib.get_data(2)
    if re.search('<Disabled> *SVM Control *<Disabled> *P-State Control *<Disabled> *SR-IOV Support',data):
        logging.info('通过退出菜单的“Save and Exit”保存设置成功')
    else:
        stylelog.fail('通过退出菜单的“保存修改”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU',data)[0],re.findall('IOMMU *<(.*)> *SVM',data)[0],re.findall('SVM *<(.*)> *SR\-IOV',data)[0]))
        count+=1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SAVE_CHANGE_ENABLED, 8)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return



def sata_controller():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_SATA_INFO,8)
    data = SetUpLib.get_data(1)
    num1=re.findall('SATA Drive (\d)\-\d *\[',data)
    num2 = re.findall('SATA Drive \d\-(\d) *\[', data)
    if num2:
        for i in num2:
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_SATA_CONFIG,8)
            time.sleep(1)
            assert SetUpLib.locate_option(Key.DOWN,['SATA Controller {0}'.format(num1[num2.index(i)])],8)
            assert SetUpLib.select_option_value(Key.DOWN,['SATA Port{0}'.format(i)],Key.DOWN,'Disabled',7)
            time.sleep(2)
            SetUpLib.send_keys(Key.SAVE_RESET)
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_SATA_INFO,8)
            data = SetUpLib.get_data(1)
            if  '\[' not in data:
                logging.info('SATA {0} 关闭成功'.format(i))
            else:
                stylelog.fail('SATA {0} 关闭失败'.format(i))
                return
        for i in num2:
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_SATA_CONFIG,8)
            time.sleep(1)
            assert SetUpLib.locate_option(Key.DOWN, ['SATA Controller {0}'.format(num1[num2.index(i)])], 8)
            assert SetUpLib.select_option_value(Key.DOWN, ['SATA Port{0}'.format(i)], Key.DOWN, 'Enabled', 7)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Setup.SET_SATA_CONTROLLER1_DISABLED, 8)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.IN_SATA_INFO,8)
        time.sleep(1)
        if  '\[' not in data:
            logging.info('SATA Controller关闭成功')
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SET_SATA_CONTROLLER1_ENABLED, 8)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return True
        else:
            stylelog.fail('SATA Controller 1关闭失败')
            return

    else:
        stylelog.fail('没有SATA设备')



def SATA_or_PCIE_Switch():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SATA_PCIE_Switch_PCIE, 20)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    datas = SetUpLib.get_data(10, Key.F7)
    #if SutConfig.Msg.KYLIN_OS not in datas:
    if Sut01Config.Msg.KYLIN_OS_MSG not in datas:
        logging.info('切换PCIE成功')
    else:
        stylelog.fail('切换PCIE失败')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Setup.SATA_PCIE_Switch_SATA, 20)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    datas = SetUpLib.get_data(10, Key.F7)
    #if SutConfig.Msg.KYLIN_OS in datas:
    if SutConfig.Msg.KYLIN_OS_MSG in datas:
        logging.info('切换SATA成功')
        return True
    else:
        stylelog.fail('切换SATA失败')
        return