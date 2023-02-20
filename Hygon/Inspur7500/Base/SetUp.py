# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

def Interface_information():
    necessary_msg = SutConfig.Sup.NECESSARY_MSG
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    information = []
    try_counts = 12
    while try_counts:
        SetUpLib.clean_buffer()
        data = SetUpLib.get_data(3, Key.RIGHT)
        information.append(data)
        if SutConfig.Msg.PAGE_MAIN in data:
            break
        try_counts -= 1
    information = ' '.join(information)
    for i in necessary_msg:
        if i in information:
            logging.info('SetUp界面有{0}'.format(i))
        else:
            stylelog.fail('SetUp界面没有{0}'.format(i))
            wrong_msg.append('SetUp界面没有{0}'.format(i))
            count += 1
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.MEM_INFO], 5)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)
    if re.search('Total Memory|Total Memory Size', data) and re.search('Memory Frequency|Memory Current Frequency',
                                                                       data):
        logging.info('内存信息中包含内存总容量和内存频率')
    else:
        stylelog.fail('内存信息中没有内存总容量和内存频率')
        wrong_msg.append('内存信息中没有内存总容量和内存频率')
        count += 1
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PCIE_INFO], 5)
    SetUpLib.send_key(Key.ENTER)
    if 'PCI Device Info' in SetUpLib.get_data(2):
        logging.info('PCIE信息中包含PCI设备信息')
    else:
        stylelog.fail('PCIE信息中没有PCI设备信息')
        wrong_msg.append('PCIE信息中没有PCI设备信息')
        count += 1
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_CONFIG], 7)
    SetUpLib.send_key(Key.ENTER)
    if 'USB Mass Storage Support' in SetUpLib.get_data(2):
        logging.info('USB配置中包含USB存储设备支持')
    else:
        stylelog.fail('USB配置中没有USB存储设备支持')
        wrong_msg.append('USB配置中没有USB存储设备支持')
        count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


# 修改板载网卡配置
def Onboard_Ethernet_Controller(oem):
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI', 'IPVersion:IPv4', 'OnLan:Disabled', 'PXE:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_LAN, 18, save=True)
    datas = SetUpLib.boot_to_boot_menu(True,reset=False)
    if re.search(SutConfig.Msg.PXE_PORT1, datas):
        stylelog.fail('关闭板载网卡配置失败')
        return
    elif re.search(SutConfig.Msg.PXE_PORT2, datas):
        stylelog.fail('关闭板载网卡配置失败')
        return
    else:
        logging.info('关闭板载网卡配置成功')
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCI_INFO, 10)
    if SetUpLib.wait_message('8088.*Ethernet controller', 3, readline=True):
        stylelog.fail('板载网卡关闭，PCIE中仍有板载网卡')
        return
    else:
        logging.info('板载网卡关闭，PCIE中没有板载网卡')
    if oem is True:
        BmcLib.change_bios_value(['OnLan:Enabled'])
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_LAN, 10, save=True)
    datas = SetUpLib.boot_to_boot_menu(True)
    if re.search(SutConfig.Msg.PXE_PORT1, datas) and re.search(SutConfig.Msg.PXE_PORT1, datas):
        logging.info('打开板载网卡配置成功')
        return True
    else:
        stylelog.fail('打开板载网卡配置失败')
        return


# 网络唤醒
def wake_online(oem):
    mac = SutConfig.Sup.MAC_ADDRESS
    if oem is True:
        BmcLib.change_bios_value(['OnLan:Enabled', 'WakeOnLan:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_WAKE_ONLINE, 10, save=True)
    assert SetUpLib.boot_os_from_bm()
    subprocess.Popen(args='./Inspur7500/Tools/wakeonline/WakeMeOnLan.exe /scan', shell=False,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(30)
    SshLib.execute_command_limit(Sut.OS_SSH, 'shutdown -h now')
    time.sleep(20)
    if re.search('\|', mac):
        mac = mac.split('|')
    else:
        mac = [mac]
    try_counts = 3
    while try_counts:
        for i in mac:
            subprocess.Popen(args='./Inspur7500/Tools/wakeonline/WakeMeOnLan.exe /wakeup {0}'.format(i), shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info('发送唤醒命令')
            time.sleep(2)
        try_counts -= 1

    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        stylelog.fail('网络唤醒关闭，但是成功唤醒')
        return
    logging.info('网络唤醒关闭，且无法唤醒')
    if oem is True:
        BmcLib.change_bios_value(['OnLan:Enabled', 'WakeOnLan:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_WAKE_ONLINE, 10, save=True)
    assert SetUpLib.boot_os_from_bm()
    SshLib.execute_command_limit(Sut.OS_SSH, 'shutdown -h now')
    time.sleep(20)
    try_counts = 2
    while try_counts:
        for i in mac:
            subprocess.Popen(args='./Inspur7500/Tools/wakeonline/WakeMeOnLan.exe /wakeup {0}'.format(i), shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info('发送唤醒命令')
            time.sleep(1)
        try_counts -= 1
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        logging.info('网络唤醒打开，且成功唤醒')
        return True
    else:
        stylelog.fail('网络唤醒打开，未成功唤醒')
        return


# USB存储设备支持
def usb_mass_storage_support(oem):
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI', 'USBStorage:Disabled', 'RearUSB:Enabled', 'FrontUSB:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_USB_STORAGE, 10, save=True)
    datas = SetUpLib.boot_to_boot_menu(True)
    if SutConfig.Msg.USB_UEFI not in datas:
        logging.info('USB存储设备支持关闭，启动项中没有USB')
    else:
        stylelog.fail('USB存储设备支持关闭，启动项中仍有USB')
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
    assert BmcLib.ping_sut()
    mount_path = SetUpLib.get_linux_usb_dev()
    result = SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(mount_path, SutConfig.Env.LINUX_USB_MOUNT))
    if len(result[0]) == len(result[1]) == 0:
        logging.info('USB存储设备关闭，setup下识别不了U盘，系统下能正常识别U盘')
    else:
        stylelog.fail('USB存储设备关闭，setup下识别不了U盘，系统下不能正常识别U盘')
        return
    if oem is True:
        BmcLib.change_bios_value(['USBStorage:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_STORAGE, 18, save=True)
    datas = SetUpLib.boot_to_boot_menu(True).split('Startup Device Menu')
    datas = datas[1] if datas else ''
    if SutConfig.Msg.USB_UEFI in datas:
        logging.info('USB存储设备支持打开，启动项中有USB')
        return True
    else:
        stylelog.fail('USB存储设备支持打开，启动项中没有USB')
        return


# USB 端口配置
def usb_port_configuration(oem):
    if oem is True:
        BmcLib.change_bios_value(['USBStorage:Enabled', 'RearUSB:Enabled', 'FrontUSB:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_BOTH, 10, save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
    datas = SetUpLib.get_data(3)
    if re.compile('USB Front[\w\s]* Port').findall(datas) and re.compile('USB Back[\w\s]* Port').findall(datas):
        logging.info('前置USB口，后置USB口都有USB设备')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['RearUSB:Disabled', 'FrontUSB:Enabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_FRONT, 3, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
        data = SetUpLib.get_data(3)
        if re.compile('USB Front[\w\s]* Port').findall(data) and not re.compile('USB Back[\w\s]* Port').findall(data):
            logging.info('前置USB端口打开，后置USB端口关闭，USB设备列表中没有后置USB设备')
        else:
            stylelog.fail('前置USB端口打开，后置USB端口关闭，USB设备列表中仍有后置USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['RearUSB:Enabled', 'FrontUSB:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_BEHIND, 3, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Front[\w\s]* Port').findall(data) and re.compile('USB Back[\w\s]* Port').findall(data):
            logging.info('前置USB端口关闭，后置USB端口打开，USB设备列表中没有前置USB设备')
        else:
            stylelog.fail('前置USB端口关闭，后置USB端口打开，USB设备列表中仍有前置USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['RearUSB:Disabled', 'FrontUSB:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_USB_PORT_BOTH, 3, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Front[\w\s]* Port').findall(data) and not re.compile('USB Back[\w\s]* Port').findall(
                data):
            logging.info('前置USB端口关闭，后置USB端口关闭，USB设备列表中没有USB设备')
        else:
            stylelog.fail('前置USB端口关闭，后置USB端口关闭，USB设备列表中仍有USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['RearUSB:Enabled', 'FrontUSB:Enabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_ALL, 3, save=True)
        return True
    elif re.compile('USB Front[\w\s]* Port').findall(datas):
        logging.info('前置USB口有USB设备')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['FrontUSB:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_USB_PORT_FRONT, 3, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Front[\w\s]* Port').findall(data) and not re.compile('USB Back[\w\s]* Port').findall(
                data):
            logging.info('前置USB端口关闭，USB设备列表中没有USB设备')
        else:
            stylelog.fail('前置USB端口关闭，USB设备列表中仍有USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['FrontUSB:Enabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_FRONT_ONLY, 3, save=True)
        return True
    elif re.compile('USB Back[\w\s]* Port').findall(datas):
        logging.info('U盘在后置USB口')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['RearUSB:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_USB_PORT_BEHIND, 3, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_INFO, 10)
        data = SetUpLib.get_data(3)
        if not re.compile('USB Back[\w\s]* Port').findall(data) and not re.compile('USB Front[\w\s]* Port').findall(
                data):
            logging.info('后置USB端口关闭，USB设备列表中没有USB设备')
        else:
            stylelog.fail('后置USB端口关闭，USB设备列表中仍有USB设备')
            return
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if oem is True:
            BmcLib.change_bios_value(['RearUSB:Enabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_PORT_BEHIND_ONLY, 3, save=True)
        return True
    else:
        stylelog.fail('USB存储设备支持打开，但是没有找到USB存储设备')
        return


# 硬盘绑定
def HDD_bind():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HDD_BIND1, 10, save=True)
    assert SetUpLib.boot_to_boot_menu()
    if SetUpLib.select_boot_option(Key.DOWN, SutConfig.Sup.HDD_BIND_NAME_2_OS, 30, SutConfig.Sup.HDD_BIND_PROMPT):
        logging.info('硬盘绑定打开，无法进入绑定外的硬盘')
    else:
        stylelog.fail('绑定硬盘，但仍可以进入绑定外的硬盘')
        return
    time.sleep(1)
    assert SetUpLib.boot_to_boot_menu()
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Sup.HDD_BIND_NAME_1_OS, 30, '')
    if not SetUpLib.wait_message(SutConfig.Sup.HDD_BIND_PROMPT, 10):
        logging.info('成功进入绑定的硬盘')
    else:
        stylelog.fail('没有进入绑定的硬盘')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HDD_BIND2, 10, save=True)
    assert SetUpLib.boot_to_boot_menu()
    if SetUpLib.select_boot_option(Key.DOWN, SutConfig.Sup.HDD_BIND_NAME_1_OS, 30, SutConfig.Sup.HDD_BIND_PROMPT):
        logging.info('硬盘绑定打开，无法进入绑定外的硬盘')
    else:
        stylelog.fail('绑定硬盘，但仍可以进入绑定外的硬盘')
        return
    time.sleep(1)
    assert SetUpLib.boot_to_boot_menu()
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Sup.HDD_BIND_NAME_2_OS, 30, '')
    if not SetUpLib.wait_message(SutConfig.Sup.HDD_BIND_PROMPT, 10):
        logging.info('成功进入绑定的硬盘')
    else:
        stylelog.fail('没有进入绑定的硬盘')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HDD_BIND3, 10, save=True)
    return True


# 安全启动
def secure_boot():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SECURE_BOOT, 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SECURE_BOOT, 10, save=True)
    assert SetUpLib.boot_to_boot_menu()
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30, SutConfig.Ipm.UEFI_USB_MSG)
    time.sleep(15)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('ls')
    if SutConfig.Env.BIOS_FILE not in SetUpLib.get_data(2):
        fs = SetUpLib.get_shell_fs_num()
        SetUpLib.send_data_enter(fs)
        time.sleep(2)
    SetUpLib.send_data_enter(f'cd {SutConfig.Env.BIOS_FILE}')
    time.sleep(2)
    SetUpLib.send_data(SutConfig.Sup.BACKUP_CMD)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Sup.SECURE_MSG, 60):
        logging.info('安全启动打开，无法使用BIOS刷新工具')
    else:
        stylelog.fail('安全启动打开，仍可以使用BIOS刷新工具')
        wrong_msg.append('安全启动打开，仍可以使用BIOS刷新工具')
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SECURE_BOOT, 10)
    time.sleep(1)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


# 安静启动
def quiet_boot(oem):
    if oem is True:
        BmcLib.change_bios_value(['QuietBoot:Enabled'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_QUIET_BOOT, 10, save=True)
    SetUpLib.clean_buffer()
    start_time = time.time()
    datas = []
    while time.time() - start_time < 200:
        datas.append(SetUpLib.get_data(1))
        if re.search('Press Key in',''.join(datas)):
            datas.append(SetUpLib.get_data(2))
            break
    SetUpLib.send_key(Key.DEL)
    if 'BIOS Version:' not in ''.join(datas):
        logging.info('安静启动打开，启动界面未出现配置信息')
    else:
        stylelog.fail('安静启动打开，启动界面仍出现配置信息')
        return
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
        logging.info('进入setup')
    if oem is True:
        BmcLib.change_bios_value(['QuietBoot:Disabled'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY)
        SetUpLib.send_key(Key.RIGHT)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_QUIET_BOOT, 10, save=True)
    if SetUpLib.wait_message('BIOS Version:', readline=True):
        logging.info('安静启动关闭，启动界面出现配置信息')
        return True


# 用户等待时间
def user_wait_time(oem):
    time_min = 1
    time_random = random.randint(1, 65534)
    count = 0
    if oem is True:
        BmcLib.change_bios_value([f'WaitTime:{time_min}'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Msg.PAGE_BOOT, {SutConfig.Msg.PAGE_BOOT: time_min}],
                                                18,
                                                save=True)
    if SetUpLib.wait_message(f'Press Key in {str(time_min)} seconds', readline=True):
        logging.info(f'修改用户等待时间{time_min}成功')
    else:
        stylelog.fail(f'修改用户等待时间{time_min}失败')
        count += 1
    if oem is True:
        BmcLib.change_bios_value([f'WaitTime:{time_random}'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Msg.PAGE_BOOT, {SutConfig.Msg.PAGE_BOOT: time_random}],
                                                18, save=True)
    if SetUpLib.wait_message(f'Press Key in {str(time_random)} seconds', readline=True):
        logging.info(f'修改用户等待时间{time_random}成功')
    else:
        stylelog.fail(f'修改用户等待时间{time_random}失败')
        count += 1
    if oem is True:
        BmcLib.change_bios_value(['WaitTime:5'])
        BmcLib.init_sut()
    else:
        SetUpLib.send_key(Key.DEL)
        if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_BOOT, {SutConfig.Msg.PAGE_BOOT: 5}],
                                                18, save=True)
    if SetUpLib.wait_message(f'Press Key in 5 seconds', readline=True):
        logging.info('修改用户等待时间5成功')

    else:
        stylelog.fail('修改用户等待时间5失败')
        count += 1
    if count == 0:
        return True
    else:
        return


# SPI BIOS 锁住
def spi_bios_lock(oem):
    if oem is True:
        BmcLib.change_bios_value(['UEFIShell:Enabled', 'SPILock:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SPI, 10, save=True)
    assert SetUpLib.boot_to_boot_menu()
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30, SutConfig.Ipm.UEFI_USB_MSG), '没有找到Shell'
    time.sleep(10)
    logging.info('成功进入Shell')
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('ls')
    if SutConfig.Env.BIOS_FILE not in SetUpLib.get_data(2):
        fs = SetUpLib.get_shell_fs_num()
        SetUpLib.send_data_enter(fs)
        time.sleep(2)
    SetUpLib.send_data_enter(f'cd {SutConfig.Env.BIOS_FILE}')
    time.sleep(2)
    SetUpLib.send_data_enter(SutConfig.Upd.SHELL_FLASH_CMD_LATEST)
    assert SetUpLib.wait_message(SutConfig.Sup.SPI_LOCK_MSG, 5), '没有找到SPI BIOS is Locked in Setup'
    logging.info('BIOS 锁住，无法刷新BIOS')
    if oem is True:
        BmcLib.change_bios_value(['UEFIShell:Enabled', 'SPILock:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SPI, 10, save=True)
    assert SetUpLib.boot_to_boot_menu()
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30, SutConfig.Ipm.UEFI_USB_MSG), '没有找到Shell'
    time.sleep(10)
    logging.info('成功进入Shell')
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('ls')
    if SutConfig.Env.BIOS_FILE not in SetUpLib.get_data(2):
        fs = SetUpLib.get_shell_fs_num()
        SetUpLib.send_data_enter(fs)
        time.sleep(2)
    SetUpLib.send_data_enter(f'cd {SutConfig.Env.BIOS_FILE}')
    time.sleep(2)
    SetUpLib.send_data_enter(SutConfig.Upd.SHELL_FLASH_CMD_LATEST)
    assert SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300)
    logging.info('关闭BIOS锁住，成功刷新BIOS')
    return True


def iommu(oem):
    if oem is True:
        BmcLib.change_bios_value(['IOMMU:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_IOMMU, 10, save=True)
    SetUpLib.boot_os_from_bm()
    cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, 'cat /etc/issue')
    logging.info(cmd_result1[0])
    cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, 'dmesg | grep -i iommu')
    logging.info(cmd_result2[0])
    # 系统类型不同，判断结果的关键字不同
    if SutConfig.Sup.OS_TYPE in cmd_result1[0]:
        if re.search(SutConfig.Sup.IOMMU_DISABLED_INFO, cmd_result2[0]) or len(cmd_result2[0]) == len(
                cmd_result2[1]) == 0:
            logging.info('iommu关闭')
        else:
            stylelog.fail('iommu没有关闭')
            return
    else:
        if len(cmd_result2[0]) == 0 and len(cmd_result2[1]) == 0:
            logging.info('iommu关闭')
        else:
            stylelog.fail('iommu没有关闭')
            return
    if oem is True:
        BmcLib.change_bios_value(['IOMMU:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_IOMMU, 10, save=True)
    SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "dmesg | grep -i iommu")[0]
    if re.search(SutConfig.Sup.IOMMU_ENABLED_INFO, cmd_result):
        logging.info('iommu打开')
        return True
    else:
        stylelog.fail('iommu没有打开')
        return


def svm(oem):
    if oem is True:
        BmcLib.change_bios_value(['VMX:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SVM, 10, save=True)
    SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, 'dmesg | grep kvm')[0]
    logging.info(cmd_result)
    if re.search(SutConfig.Sup.SVM_DISABLED_INFO, cmd_result):
        logging.info('Svm关闭')
    else:
        stylelog.fail('Svm没有关闭')
        return
    if oem is True:
        BmcLib.change_bios_value(['VMX:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SVM, 10, save=True)
    SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, 'dmesg | grep kvm')
    cmd_result = cmd_result[0]
    if 'enabled' in cmd_result:
        logging.info('Svm打开')
        return True
    else:
        stylelog.fail('Svm没有打开')
        return


def sriov(oem):
    # 虚拟网卡
    def virtual():
        eth_bdf = re.findall('\w+:\w+.\w+', SshLib.execute_command_limit(Sut.OS_SSH, 'lspci | grep -i eth')[0])
        buss = [i[:2] for i in eth_bdf]
        ethname_list = []
        for i in eth_bdf:
            ethname_list.append(
                SshLib.execute_command_limit(Sut.OS_SSH, f'cd /sys/bus/pci/devices/0000:{i}/net;ls')[0].strip('\n'))
        bus = []
        result = SshLib.execute_command_limit(Sut.OS_SSH, 'ifconfig | grep -e flags -e inet')[0]
        for i in ethname_list:
            result1 = SshLib.execute_command_limit(Sut.OS_SSH, f'cat /sys/class/net/{i}/device/sriov_totalvfs')
            if result1[1] or result1[0] == '0':
                logging.info(f'{i}不支持SR-IOV')
                bus.append(buss[ethname_list.index(i)])
            elif re.search(f'{i}: flags.*\n\s*inet', result):
                logging.info(f'{i}连接网线，不虚拟网卡')

                # bus.append(buss[ethname_list.index(i)])
            else:
                SshLib.execute_command_limit(Sut.OS_SSH,
                                             f'echo 2 > /sys/class/net/{i}/device/sriov_numvfs')
        buslist = []
        for i in buss:
            if i not in bus:
                buslist.append(i)
        return ethname_list, buslist

    count = 0
    wrong_msg = []
    if oem is True:
        BmcLib.change_bios_value(['SR-IOV:Enabled'])
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Msg.PAGE_ADVANCED, SutConfig.Msg.VIRTUALIZATION], 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        for i in re.findall('\[X\] *(Socket.*?)   ', data):
            SetUpLib.locate_option(Key.DOWN, [SetUpLib.regex_char_handle(i)], 18,exact=False)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SR, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        for i in re.findall('\[X\] *(Socket.*?)   ', data):
            SetUpLib.locate_option(Key.DOWN, [SetUpLib.regex_char_handle(i)], 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    ethname_list, buslist = virtual()
    cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
    if all(re.search(f'{i}:\w+.\w+ Ethernet controller:.*Virtual Function', cmd_result1[0]) or buslist.count(i) < len(
            re.findall(f'{i}:\w+.\w+', cmd_result1[0])) for i in buslist):
        logging.info('SR-IOV 打开，系统下正常显示')
    else:
        stylelog.fail('SR-IOV 打开，系统下异常')
        stylelog.fail(cmd_result1[0])
        wrong_msg.append('SR-IOV 打开，系统下异常')
        count += 1
    if oem is True:
        BmcLib.change_bios_value(['SR-IOV:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SR, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    ethname_list, buslist = virtual()
    cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
    if any(re.search(f'{i}:\w+.\w+ Ethernet controller:.*Virtual Function', cmd_result1[0]) or buslist.count(
            i) < len(re.findall(f'{i}:\w+.\w+', cmd_result1[0])) for i in buslist):
        stylelog.fail('SR-IOV 关闭，系统下异常')
        wrong_msg.append('SR-IOV 关闭，系统下异常')
        count += 1
    else:
        logging.info('SR-IOV 关闭，系统下显示正常')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SR, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    SetUpLib.clean_buffer()
    SetUpLib.send_key(Key.ENTER)
    dict = {}
    data = SetUpLib.get_data(2)
    for i in re.findall('\[[ |X]\] *(Socket.*?)   ', data):
        dict[i] = re.findall('Bus:(\w+) ', i)[0]
    if dict:
        for key, value in dict.items():
            assert SetUpLib.locate_option(Key.DOWN, [SetUpLib.regex_char_handle(key)], 10,exact=False)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)
            assert SetUpLib.boot_os_from_bm()
            ethname_list, buslist = virtual()
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
            buslist_origin = copy(buslist)
            buslist = list(set(buslist))
            if value in buslist:
                buslist.remove(value)
            if buslist:
                if not re.search(f'{value}:\w+.\w+ Ethernet controller:.*Virtual Function',
                                 cmd_result1[0]) or buslist_origin.count(value) == len(
                    re.findall(f'{value}:\w+.\w+', cmd_result1[0])):
                    if all(
                            re.search(f'{i}:\w+.\w+ Ethernet controller:.*Virtual Function',
                                      cmd_result1[0]) or buslist_origin.count(i) < len(
                                re.findall(f'{i}:\w+.\w+', cmd_result1[0])) for i in
                            buslist):
                        logging.info(f'只有{key}SR-IOV关闭')
                    else:
                        stylelog.fail(f'只关闭{key}，系统下异常{cmd_result1[0]}')
                        wrong_msg.append(f'只关闭{key}，系统下异常{cmd_result1[0]}')
                        count += 1
                else:
                    stylelog.fail(f'只关闭{key}，系统下异常{cmd_result1[0]}')
                    wrong_msg.append(f'只关闭{key}，系统下异常{cmd_result1[0]}')
                    count += 1
            else:
                if not re.search('Virtual Function', cmd_result1[0]):
                    logging.info('没有支持SR-IOV的网卡,且系统下没有虚拟网卡')
                else:
                    stylelog.fail(f'没有支持SR-IOV的网卡,但系统下有虚拟网卡,{cmd_result1[0]}')
                    count += 1
                    wrong_msg.append(f'没有支持SR-IOV的网卡,但系统下有虚拟网卡,{cmd_result1[0]}')
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    [SutConfig.Msg.PAGE_ADVANCED, SutConfig.Msg.VIRTUALIZATION], 18)
            assert SetUpLib.locate_option(Key.DOWN, [SetUpLib.regex_char_handle(key)], 10,exact=False)
            SetUpLib.send_keys([Key.ENTER, Key.ESC, Key.ENTER])
            time.sleep(2)
        for i in dict.keys():
            assert SetUpLib.locate_option(Key.DOWN, [SetUpLib.regex_char_handle(i)], 10,exact=False)
            SetUpLib.send_keys([Key.ENTER, Key.ESC, Key.ENTER])
            time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_os_from_bm()
        ethname_list, buslist = virtual()
        cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
        if any(re.search(f'{i}:\w+.\w+ Ethernet controller:.*Virtual Function', cmd_result1[0]) or buslist.count(
                i) < len(re.findall(f'{i}:\w+.\w+', cmd_result1[0])) for i in buslist):
            stylelog.fail('关闭所有网卡SR-IOV，系统下异常')
            wrong_msg.append('关闭所有网卡SR-IOV，系统下异常')
            count += 1
        else:
            logging.info('关闭所有网卡SR-IOV，系统下显示正常')
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def memory_speed():
    count = 0
    wrong_msg = []
    speeds = SutConfig.Sup.MEMORY_SPEED
    for speed in speeds:
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_HYGON + [
            {SutConfig.Sup.MEMORY_SPEED_NAME: f'{speed}MHz'}], 18, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_MEM, 8)
        data = SetUpLib.get_data(3)
        if not re.findall('Memory [a-zA-Z]* *Frequency.*?([0-9]+) MHz', data):
            stylelog.fail('内存信息抓取失败')
            return
        memoryspeed = re.findall('Memory [a-zA-Z]* *Frequency.*?([0-9]+) MHz', data)[0]
        if memoryspeed == str(int(speed) * 2) or memoryspeed == str(int(speed) * 2 - 1):
            logging.info('修改内存频率为{0}MHz,SetUp下内存信息显示{1}MHz'.format(speed, memoryspeed))
        else:
            stylelog.fail('修改内存频率为{0}MHz,SetUp下内存信息显示{1}MHz'.format(speed, memoryspeed))
            wrong_msg.append('修改内存频率为{0}MHz,SetUp下内存信息显示{1}MHz'.format(speed, memoryspeed))
            count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def save_change_esc():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    SetUpLib.default_save()
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_VIRTU, 10)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV', data):
        logging.info('ESC键保存设置成功')
    else:
        stylelog.fail('ESC键保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                       re.findall('IOMMU *<(.*)> *SVM', data),
                                                                       re.findall('SVM *<(.*)> *SR\-IOV', data)))
        wrong_msg.append('ESC键保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                          re.findall('IOMMU *<(.*)> *SVM', data),
                                                                          re.findall('SVM *<(.*)> *SR\-IOV', data)))
        count += 1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_VIRTU, 4, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def save_change():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    SetUpLib.default_save()
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_VIRTU, 10)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV', data):
        logging.info('通过退出菜单的“保存修改”保存设置成功')
    else:
        stylelog.fail('通过退出菜单的“保存修改”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                                re.findall('IOMMU *<(.*)> *SVM', data),
                                                                                re.findall('SVM *<(.*)> *SR\-IOV',
                                                                                           data)))
        wrong_msg.append('通过退出菜单的“保存修改”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                                   re.findall('IOMMU *<(.*)> *SVM',
                                                                                              data),
                                                                                   re.findall('SVM *<(.*)> *SR\-IOV',
                                                                                              data)))
        count += 1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_VIRTU, 4, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def save_and_exit():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    SetUpLib.default_save()
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_VIRTU, 10)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SAV_EXI, 10)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV', data):
        logging.info('通过退出菜单的“保存并且退出”保存设置成功')
    else:
        stylelog.fail('通过退出菜单的“保存并且退出”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                                  re.findall('IOMMU *<(.*)> *SVM',
                                                                                             data),
                                                                                  re.findall('SVM *<(.*)> *SR\-IOV',
                                                                                             data)))
        wrong_msg.append('通过退出菜单的“保存并且退出”保存设置失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                                     re.findall('IOMMU *<(.*)> *SVM',
                                                                                                data),
                                                                                     re.findall('SVM *<(.*)> *SR\-IOV',
                                                                                                data)))
        count += 1
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_VIRTU, 4, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def exit_without_save():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_VIRTU, 10)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_NO_SAV_EXI, 10)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<Enabled> *IOMMU *<Enabled> *SVM *<Enabled> *SR\-IOV', data):
        logging.info('通过退出菜单的“不保存并且退出”设置没有被保存')
    else:
        stylelog.fail('通过退出菜单的“不保存并且退出”设置被保存,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                                  re.findall('IOMMU *<(.*)> *SVM',
                                                                                             data),
                                                                                  re.findall('SVM *<(.*)> *SR\-IOV',
                                                                                             data)))
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_VIRTU, 4)
        wrong_msg.append('通过退出菜单的“不保存并且退出”设置被保存,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                                     re.findall('IOMMU *<(.*)> *SVM',
                                                                                                data),
                                                                                     re.findall('SVM *<(.*)> *SR\-IOV',
                                                                                                data)))
        count += 1
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def load_default():
    default = SutConfig.Sup.VIRTUALIZATION_DEFAULT
    assert SetUpLib.boot_to_setup()
    SetUpLib.default_save()
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_VIRTU, 10, save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV', data):
        logging.info('设置更改成功')
    else:
        stylelog.fail('设置更改失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                   re.findall('IOMMU *<(.*)> *SVM', data),
                                                                   re.findall('SVM *<(.*)> *SR\-IOV', data)))
        return
    time.sleep(2)
    SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.LOAD_DEFAULTS], 7)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(15)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<{0}> *IOMMU *<{1}> *SVM *<{2}> *SR\-IOV'.format(default[0], default[1], default[2]), data):
        logging.info('通过“恢复初始值”恢复初始值成功')
        return True
    else:
        stylelog.fail('通过“恢复初始值”恢复初始值失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                             re.findall('IOMMU *<(.*)> *SVM', data),
                                                                             re.findall('SVM *<(.*)> *SR\-IOV', data)))
        return


def load_default_f9():
    default = SutConfig.Sup.VIRTUALIZATION_DEFAULT
    assert SetUpLib.boot_to_setup()
    SetUpLib.default_save()
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_VIRTU, 10, save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<Disabled> *IOMMU *<Disabled> *SVM *<Disabled> *SR\-IOV', data):
        logging.info('设置更改成功')
    else:
        stylelog.fail('设置更改失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                   re.findall('IOMMU *<(.*)> *SVM', data),
                                                                   re.findall('SVM *<(.*)> *SR\-IOV', data)))
        return
    SetUpLib.default_save()
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_VIRTU, 10)
    data = SetUpLib.get_data(2)
    if re.search('<{0}> *IOMMU *<{1}> *SVM *<{2}> *SR\-IOV'.format(default[0], default[1], default[2]), data):
        logging.info('通过F9恢复初始值成功')
        return True
    else:
        stylelog.fail('通过F9恢复初始值失败,IOMMU:{0},SVM:{1},SR-IOV:{2}'.format(re.findall('<(.*)> *IOMMU', data),
                                                                        re.findall('IOMMU *<(.*)> *SVM', data),
                                                                        re.findall('SVM *<(.*)> *SR\-IOV', data)))
        return


def check_default_bios():
    default_options = []
    f9_options = []
    ipm_options = []
    updated_options = []
    for i in SutConfig.Upd.DEFAULT_OPTION_VALUE:
        if not re.search('password', i.lower()) and i not in SutConfig.Upd.BMC_LINK_OPTION:
            default_options.append(i)
    logging.info('F9 恢复默认值...............................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_OPTION_VALUE, 18, save=True)
    assert SetUpLib.boot_to_setup()
    SetUpLib.default_save()
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_to_setup()
    for i in SetUpLib.get_all_option_value():
        if not re.search('password', i.lower()) and i not in SutConfig.Upd.BMC_LINK_OPTION:
            f9_options.append(i)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_OPTION_VALUE, 18, save=True)
    time.sleep(20)
    logging.info('IPMITOOL 恢复默认值......................................')
    arg = SutConfig.Env.LOAD_DEFAULT
    BmcLib.output(arg)
    time.sleep(5)
    BmcLib.power_reset()
    time.sleep(200)
    assert SetUpLib.boot_to_setup()
    for i in SetUpLib.get_all_option_value():
        if not re.search('password', i.lower()) and i not in SutConfig.Upd.BMC_LINK_OPTION:
            ipm_options.append(i)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_OPTION_VALUE, 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_UPDATE_ALL, 10, save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.UPDATE_BIOS_PATH, 25, 'Confirmation', timeout=20)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')
    time.sleep(200)
    assert SetUpLib.boot_to_setup()
    for i in SetUpLib.get_all_option_value():
        if not re.search('password', i.lower()) and i not in SutConfig.Upd.BMC_LINK_OPTION:
            updated_options.append(i)
    logging.info('默  认  值为{0}'.format(default_options))
    logging.info('F9 默认 值为{0}'.format(f9_options))
    logging.info('IPM 默认值为{0}'.format(ipm_options))
    logging.info('全刷BIOS值为{0}'.format(updated_options))
    if sorted(list(set(f9_options))) == sorted(list(set(ipm_options))) == sorted(list(set(updated_options))) == sorted(
            list(set(default_options))):
        logging.info('F9恢复默认值，IPM恢复默认值，全刷BIOS恢复默认值与实际默认值相同')
        return True
    else:
        stylelog.fail('F9恢复默认值，IPM恢复默认值，全刷BIOS恢复默认值与实际默认值不同')
        name = ['F9', 'Ipm', '全刷BIOS']
        for ind, options in enumerate([f9_options, ipm_options, updated_options]):
            logging.info('-' * 100)
            result = Update._compare_difference(options, default_options)
            for index, i in enumerate(result[0]):
                stylelog.fail('%-{}s'.format(result[4]) % f'{name[ind]}:{i}' + f';默认值:{result[1][index]}')
            if result[2]:
                stylelog.fail(f'{name[ind]}:{result[2]}')
            if result[3]:
                stylelog.fail(f'默认值:{result[3]}')
        return


def sata_controller():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SATA, 8, save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
    data = SetUpLib.get_data(2)
    if 'M.2 Driver 1' not in data:
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
    data = data.split('Asmedia Controller')[1]
    if re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and re.compile(
            'M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
        logging.info('Asmedia控制器1061R_A，Asmedia控制器1061R_B都连接设备')
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SATA_A, 4, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and re.compile(
                'M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_A，SATA配置下SATA端口被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_A，SATA配置下SATA端口没有被关闭')
            wrong_msg.append('关闭Asmedia控制器1061R_A，SATA配置下SATA端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SATA_B, 4, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and not re.compile(
                'M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_B，SATA配置下M.2端口被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_B，SATA配置下M.2端口没有被关闭')
            wrong_msg.append('关闭Asmedia控制器1061R_B，SATA配置下M.2端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SATA, 4, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
        time.sleep(1)
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
        data = data.split('Asmedia Controller')[1]
        if not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and not re.compile(
                'M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
            logging.info('关闭Asmedia控制器1061R_A和Asmedia控制器1061R_B，SATA配置下SATA端口和M.2端口都被关闭')
        else:
            stylelog.fail('关闭Asmedia控制器1061R_A和Asmedia控制器1061R_B，SATA配置下SATA端口和M.2端口没有被关闭')
            wrong_msg.append('关闭Asmedia控制器1061R_A和Asmedia控制器1061R_B，SATA配置下SATA端口和M.2端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SATA, 5, save=True)

    elif re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and not re.compile(
            'M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
        logging.info('Asmedia控制器1061R_A连接设备，Asmedia控制器1061R_B没有连接设备')
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)

        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SATA_A, 5, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
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
            wrong_msg.append('关闭Asmedia控制器1061R_A，SATA配置下SATA端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SATA, 5, save=True)
    elif not re.compile('SATA Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_A)).findall(data) and re.compile(
            'M.2 Driver [0-9] *{0}'.format(SutConfig.Sup.SATA_R_B)).findall(data):
        logging.info('Asmedia控制器1061R_A没有连接设备，Asmedia控制器1061R_B连接设备')
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)

        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SATA_B, 5, save=True)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
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
            wrong_msg.append('关闭Asmedia控制器1061R_B，SATA配置下M.2端口没有被关闭')
            count += 1
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SATA, 5, save=True)
    else:
        stylelog.fail('Asmedia控制器1061R_A,Asmedia控制器1061R_B都没有连接设备')
        return
    if count == 0:
        return True

    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def tpm():
    count = 0
    wrong_msg = []
    base_time = 10  # 时间差,ESC后花费时间与F12后花费时间的差要大于base_time;正常启动到Post时间与F12后启动到Post的时间要小于base_time
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(2)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 5):
        logging.info('当前启动模式为Legacy')
        arg = Sut.OS_LEGACY_SSH
    else:
        logging.info('当前启动模式为UEFI')
        arg = Sut.OS_SSH
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_DTPM, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    start = time.time()
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    spent_time = time.time() - start
    time.sleep(1)
    SetUpLib.send_key(Key.DEL)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_TPM2, 18)
    time.sleep(1)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if re.search('TPM Version *{0}'.format(SutConfig.Sup.DTPM_MSG), SetUpLib.get_data(2)):
        logging.info('打开DTPM，SetUp下显示{0}'.format(SutConfig.Sup.DTPM_MSG))
    else:
        stylelog.fail('打开DTPM，SetUp下没有显示{0}'.format(SutConfig.Sup.DTPM_MSG))
        wrong_msg.append('打开DTPM，SetUp下没有显示{0}'.format(SutConfig.Sup.DTPM_MSG))
        count += 1
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG):
        logging.info('打开DTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        dtpm_esc_start = time.time()
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            dtpm_esc_end = time.time()
            time.sleep(1)
            SetUpLib.send_key(Key.F11)
            if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU):
                assert SetUpLib.boot_to_boot_menu()
        else:
            stylelog.fail('打开DTPM,按ESC后宕机')
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                  SutConfig.Msg.POST_MESSAGE)
    else:
        stylelog.fail('打开DTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        wrong_msg.append('打开DTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count += 1
        BmcLib.init_sut()
        assert SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
    if 'dtpm_esc_start' in dir() and 'dtpm_esc_end' in dir():
        dtpm_esc_spent = dtpm_esc_end - dtpm_esc_start
    else:
        dtpm_esc_spent = 0

    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
    if BmcLib.ping_sut():
        logging.info('成功启动到系统')
    else:
        return

    cmd_result = SshLib.execute_command_limit(arg, "dmesg | grep -i tpm")
    cmd_result = cmd_result[0]
    if re.search(SutConfig.Sup.DTPM_OS_MSG, cmd_result):
        logging.info('打开DTPM,系统下显示{}'.format(SutConfig.Sup.DTPM_OS_MSG))
    else:
        stylelog.fail('打开DTPM,系统下没有显示{}'.format(SutConfig.Sup.DTPM_OS_MSG))
        wrong_msg.append('打开DTPM,系统下没有显示{}'.format(SutConfig.Sup.DTPM_OS_MSG))
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    SetUpLib.send_key(Key.ENTER)
    if re.search('No Action', SetUpLib.get_data(3)):
        logging.info('一次启动后,TPM2操作变为无动作')
    else:
        stylelog.fail('一次启动后,TPM2操作没有变为无动作')
        wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_TPM2, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG):
        logging.info('打开DTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.F12)
        dtpm_f12_start = time.time()
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            dtpm_f12_end = time.time()
            time.sleep(1)
            SetUpLib.send_key(Key.F11)
            if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU):
                assert SetUpLib.boot_to_boot_menu()
        else:
            stylelog.fail('打开DTPM,按F12后宕机')
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_to_boot_menu()
    else:
        stylelog.fail('打开DTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        wrong_msg.append('打开DTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count += 1
        assert SetUpLib.boot_to_boot_menu()
    if 'dtpm_f12_start' in dir() and 'dtpm_f12_end' in dir():
        dtpm_f12_spent = dtpm_f12_end - dtpm_f12_start
    else:
        dtpm_f12_spent = 0
    logging.info(f'正常启动到POST花费时间{spent_time}')
    logging.info(f'DTPM,按ESC后启动到POST花费时间{dtpm_esc_spent}')
    logging.info(f'DTPM,F12后启动到POST花费时间{dtpm_f12_spent}')

    if dtpm_f12_spent - dtpm_esc_spent > base_time and abs(spent_time - dtpm_f12_spent) < base_time:
        logging.info('DTPM,按ESC继续启动,F12重启')
    else:
        stylelog.fail('DTPM,按ESC不是继续启动,F12不是重启')
        count += 1
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_FTPM, 18)
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
    if re.search('TPM Version *{0}'.format(SutConfig.Sup.FTPM_MSG), SetUpLib.get_data(2)):
        logging.info('打开FTPM，SetUp下显示{0}'.format(SutConfig.Sup.FTPM_MSG))
    else:
        stylelog.fail('打开FTPM，SetUp下没有显示{0}'.format(SutConfig.Sup.FTPM_MSG))
        wrong_msg.append('打开FTPM，SetUp下没有显示{0}'.format(SutConfig.Sup.FTPM_MSG))
        count += 1
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG):
        logging.info('打开FTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        ftpm_esc_start = time.time()

        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            ftpm_esc_end = time.time()
            time.sleep(1)
            SetUpLib.send_key(Key.F11)
            if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU):
                assert SetUpLib.boot_to_boot_menu()
        else:
            stylelog.fail('打开FTPM,按ESC后宕机')
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_to_boot_menu()
    else:
        stylelog.fail('打开FTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        wrong_msg.append('打开FTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count += 1
        BmcLib.init_sut()
        assert SetUpLib.boot_to_boot_menu()
    if 'ftpm_esc_start' in dir() and 'ftpm_esc_end' in dir():
        ftpm_esc_spent = ftpm_esc_end - ftpm_esc_start
    else:
        ftpm_esc_spent = 0
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
    if BmcLib.ping_sut():
        time.sleep(15)
        logging.info('成功启动到系统')
    else:
        return
    cmd_result = SshLib.execute_command_limit(arg, "dmesg | grep -i tpm")
    cmd_result = cmd_result[0]
    if re.search(SutConfig.Sup.FTPM_OS_MSG, cmd_result):
        logging.info('打开FTPM,系统下显示{}'.format(SutConfig.Sup.FTPM_OS_MSG))
    else:
        stylelog.fail('打开FTPM,系统下没有显示{}'.format(SutConfig.Sup.FTPM_OS_MSG))
        wrong_msg.append('打开FTPM,系统下没有显示{}'.format(SutConfig.Sup.FTPM_OS_MSG))
        count += 1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    SetUpLib.send_key(Key.ENTER)
    if re.search('No Action', SetUpLib.get_data(3)):
        logging.info('一次启动后,TPM2操作变为无动作')
    else:
        stylelog.fail('一次启动后,TPM2操作没有变为无动作')
        wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_TPM2, 18, save=True)
    if SetUpLib.wait_message(SutConfig.Sup.POST_MSG):
        logging.info('打开FTPM,启动时显示{}'.format(SutConfig.Sup.POST_MSG))
        time.sleep(1)
        SetUpLib.send_key(Key.F12)
        ftpm_f12_start = time.time()
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            ftpm_f12_end = time.time()
            time.sleep(1)
            SetUpLib.send_key(Key.F11)
            if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU):
                assert SetUpLib.boot_to_boot_menu()
        else:
            stylelog.fail('打开FTPM,按F12后宕机')
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_to_boot_menu()
    else:
        stylelog.fail('打开FTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        wrong_msg.append('打开FTPM,启动时没有显示{}'.format(SutConfig.Sup.POST_MSG))
        count += 1
        BmcLib.init_sut()
        assert SetUpLib.boot_to_boot_menu()
    if 'ftpm_f12_start' in dir() and 'ftpm_f12_end' in dir():
        ftpm_f12_spent = ftpm_f12_end - ftpm_f12_start
    else:
        ftpm_f12_spent = 0
    logging.info(f'正常启动到POST花费时间{spent_time}')
    logging.info(f'FTPM,按ESC后启动到POST花费时间{ftpm_esc_spent}')
    logging.info(f'FTPM,按F12后启动到POST花费时间{ftpm_f12_spent}')
    if ftpm_f12_spent - ftpm_esc_spent > base_time and abs(spent_time - ftpm_f12_spent) < base_time:
        logging.info('FTPM,按ESC继续启动,F12重启')
    else:
        stylelog.fail('FTPM,按ESC不是继续启动,F12不是重启')
        count += 1
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_TPM, 18, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def _capture_screen(imgdir, picturename):
    filename = picturename + ".jpg"
    if os.path.exists(imgdir):
        file_path = os.path.join(imgdir, filename)
    else:
        os.mkdir(imgdir)
        file_path = os.path.join(imgdir, filename)
    try:
        screen = pyautogui.screenshot()
        screen.save(file_path)
        logging.info("Screen captured: {0}".format(filename))
        return os.path.join(imgdir, picturename)
    except Exception as e:
        logging.info("Failed to capture screen.")
        logging.error(e)


def find_img(img_path, template_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (0, 0), fx=1, fy=1)
    template = cv2.imread(template_path)
    template = cv2.resize(template, (0, 0), fx=1, fy=1)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_ = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(img_gray, template_, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    # print(result)
    # res大于70%
    loc = list(result[np.where(result >= threshold)])
    if loc != []:
        return True
    else:
        return False


def boot_logo(oem):
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    arg = '{0} fru print'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    data = stdoutput.decode('gbk')
    if re.findall('Product Name *: ([0-9A-Za-z\-]+)', data)[0][-1] == '2':
        version = '2'
    else:
        version = '1'
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    if oem is True:
        BmcLib.change_bios_value(['HideBootLogo:Enabled'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HIDE_BOOT_LOGO, 18, save=True)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    logging.info('Found {}'.format(SutConfig.Msg.POST_MESSAGE))
    _capture_screen(SutConfig.Sup.LOGO_PATH, 'logo')
    img_path = os.path.join(SutConfig.Sup.LOGO_PATH, 'logo.jpg')
    template_path = os.path.join(SutConfig.Sup.LOGO_PATH, 'correctlogo.jpg')
    if find_img(img_path, template_path):
        stylelog.fail('隐藏开机Logo,post界面仍出现Logo')
        wrong_msg.append('隐藏开机Logo,post界面仍出现Logo')
        count += 1
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
        stylelog.fail('Smbios 显示制造商,type1{0},type2{1},type3{2}'.format(re.findall('Manufacturer: ([a-zA-Z]+)', type1),
                                                                       re.findall('Manufacturer: ([a-zA-Z]+)', type2),
                                                                       re.findall('Manufacturer: ([a-zA-Z]+)', type3)))
        wrong_msg.append(
            'Smbios 显示制造商,type1{0},type2{1},type3{2}'.format(re.findall('Manufacturer: ([a-zA-Z]+)', type1),
                                                             re.findall('Manufacturer: ([a-zA-Z]+)', type2),
                                                             re.findall('Manufacturer: ([a-zA-Z]+)', type3)))
        count += 1
    if version == '2':
        value = re.findall('(?:Manufacturer:|Product Name:|Version:|Serial Number:|SKU Number:) (\w+)',
                           type1 + type2 + type3)
        if all(i == 'TBD' for i in value):
            logging.info('隐藏开机Logo，Smbios type1,type2,type3,制造商，版本等显示TBD')
        else:
            stylelog.fail(f'隐藏开机Logo，Smbios type1,type2,type3,制造商，版本等没有显示TBD，{value}')
            wrong_msg.append(f'隐藏开机Logo，Smbios type1,type2,type3,制造商，版本等没有显示TBD，{value}')
            count += 1
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    if version == '2':
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(2)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message('Mother Board Info *TBD', 5):
            logging.info('隐藏开机Logo,SetUp显示TBD')
        else:
            stylelog.fail('隐藏开机Logo,SetUp没有显示TBD')
            wrong_msg.append('隐藏开机Logo,SetUp没有显示TBD')
            count += 1
    if oem is True:
        BmcLib.change_bios_value(['HideBootLogo:Disabled'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SHOW_BOOT_LOGO, 18, save=True)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.power_cycle()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    logging.info('Found {}'.format(SutConfig.Msg.POST_MESSAGE))
    _capture_screen(SutConfig.Sup.LOGO_PATH, 'logo')
    img_path = os.path.join(SutConfig.Sup.LOGO_PATH, 'logo.jpg')
    template_path = os.path.join(SutConfig.Sup.LOGO_PATH, 'correctlogo.jpg')
    if find_img(img_path, template_path):
        logging.info('展示开机Logo，post界面出现Logo')

    else:
        stylelog.fail('展示开机Logo，post界面未出现Logo')
        wrong_msg.append('展示开机Logo，post界面未出现Logo')
        # count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def link_relation(oem):
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_LEGACY, 18)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Sup.UEFI_HII, 2, readline=True):
        stylelog.fail('启动模式Legacy,UEFI HII 配置菜单没有被隐藏')
        wrong_msg.append('启动模式Legacy,UEFI HII 配置菜单没有被隐藏')
        count += 1
    else:
        logging.info('启动模式Legacy,UEFI HII 配置菜单被隐藏')
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SECURE_BOOT, 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SECURE, 18)
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
        wrong_msg.append('Legacy 下打开安全启动,启动模式没有变为UEFI')
        count += 1
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('<UEFI> *Boot Mode', 3, readline=True):
        logging.info('Legacy 下打开安全启动,启动模式变为UEFI')
    else:
        stylelog.fail('Legacy 下打开安全启动,启动模式没有变为UEFI')
        wrong_msg.append('Legacy 下打开安全启动,启动模式没有变为UEFI')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_LEGACY, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_SECURE_BOOT, 10)
    if SetUpLib.wait_message(SutConfig.Sup.CLOSE_SECURE_MSG, 3, readline=True):
        logging.info('启动模式更改为Legacy,安全启动关闭')
    else:
        stylelog.fail('启动模式更改为Legacy,安全启动没有关闭')
        wrong_msg.append('启动模式更改为Legacy,安全启动没有关闭')
        count += 1

    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PXE_OPTION, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    data = SetUpLib.get_data(2)
    if not re.search('{0}|{1}|{2}|{3}'.format(SutConfig.Msg.PXE_NETWORK, SutConfig.Msg.PXE_RETRY,
                                              SutConfig.Msg.PXE_IP_VER, SutConfig.Msg.PXE_BOOT_PRIOROTY), data):
        logging.info('关闭网络引导,没有出现{0}，{1}，{2}，{3}'.format(SutConfig.Msg.PXE_NETWORK, SutConfig.Msg.PXE_RETRY,
                                                         SutConfig.Msg.PXE_IP_VER, SutConfig.Msg.PXE_BOOT_PRIOROTY))

    else:
        stylelog.fail('关闭网络引导,仍出现')
        wrong_msg.append('关闭网络引导,仍出现')
        count += 1
    if oem is True:
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        BmcLib.change_bios_value(['NetworkStack:Disabled'])
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PXE_STACK, 18, save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_UEFI_HII, 18)
    if not SetUpLib.wait_message('Ipv4|Ipv6|VLAN', 3):
        logging.info('网络协议栈关闭,UEFI HII 配置菜单不显示,Ipv4,Ipv6,VLAN')
    else:
        stylelog.fail('网络协议栈关闭,UEFI HII 配置菜单仍显示,Ipv4,Ipv6,VLAN')
        wrong_msg.append('网络协议栈关闭,UEFI HII 配置菜单仍显示,Ipv4,Ipv6,VLAN')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SECURE_BOOT, 10)

    time.sleep(1)
    SetUpLib.send_key(Key.Y)
    time.sleep(1)
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PXE_OPTION, 18, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def option_rom(oem):
    count = 0
    wrong_msg = []
    if oem is True:
        BmcLib.change_bios_value(['BootMode:Legacy', 'OnLan:Enabled', 'OptionRom:Enabled'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_OPTION_ROM, 15, save=True)
    SetUpLib.clean_buffer()
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if re.search(SutConfig.Msg.POST_MESSAGE, data):
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
        wrong_msg.append('Option Rom  中没有板载网卡信息')
        count += 1
    if re.search(SutConfig.Sup.ASMEDIA_MSG, data):
        logging.info('Option Rom  中有Asmedia信息')
    else:
        stylelog.fail('Option Rom  中没有Asmedia信息')
        wrong_msg.append('Option Rom  中没有Asmedia信息')
        count += 1
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
        logging.info('进入SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    if oem is True:
        BmcLib.change_bios_value(['OptionRom:Disabled'])
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_OPTION_ROM, 18, save=True)
    SetUpLib.clean_buffer()
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if re.search(SutConfig.Msg.POST_MESSAGE, data):
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
        wrong_msg.append('关闭OPtion Rom ,Post没有隐藏Option Rom')
        count += 1

    SetUpLib.send_key(Key.DEL)
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
        logging.info('进入SetUp')
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_UEFI, 18, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def tpm_plus():
    count = 0
    wrong_msg = []
    base_time = 10
    logging.info('FTPM测试...............................................................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_FTPM, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    start = time.time()
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    spent = time.time() - start
    SetUpLib.send_key(Key.DEL)
    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_TPM_STATE, 18)
    SetUpLib.clean_buffer()
    SetUpLib.send_key(Key.DOWN)
    result1 = SetUpLib.get_data(1)
    SetUpLib.send_key(Key.DOWN)
    if result1 == SetUpLib.get_data(1):
        logging.info('TPM State 设为关闭，自动隐藏选项')
    else:
        stylelog.fail('TPM State 设为关闭，没有自动隐藏选项')
        wrong_msg.append('TPM State 设为关闭，没有自动隐藏选项')
        count += 1
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if re.search('TPM Version *{0}'.format(SutConfig.Sup.FTPM_MSG), SetUpLib.get_data(2)):
        logging.info('TPM State设为关闭，SetUp下显示{0}'.format(SutConfig.Sup.FTPM_MSG))
    else:
        stylelog.fail('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sup.FTPM_MSG))
        wrong_msg.append('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sup.FTPM_MSG))
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_TPM_STATE, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[0]: 'Disabled'}], 18)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.TPM_LIST[1]], 5) and not SetUpLib.locate_option(Key.UP, [
        SutConfig.Sup.TPM_LIST[2]], 5) and not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.TPM_LIST[3]], 5):
        logging.info(
            f'关闭{SutConfig.Sup.TPM_LIST[0]},{SutConfig.Sup.TPM_LIST[1]}和{SutConfig.Sup.TPM_LIST[2]}和{SutConfig.Sup.TPM_LIST[3]}都置灰')
    else:
        logging.info(
            f'关闭{SutConfig.Sup.TPM_LIST[0]},{SutConfig.Sup.TPM_LIST[1]}、{SutConfig.Sup.TPM_LIST[2]}、{SutConfig.Sup.TPM_LIST[3]}没有置灰')
        wrong_msg.append(
            f'关闭{SutConfig.Sup.TPM_LIST[0]},{SutConfig.Sup.TPM_LIST[1]}、{SutConfig.Sup.TPM_LIST[2]}、{SutConfig.Sup.TPM_LIST[3]}没有置灰')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[0]: 'Enabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[1]: 'Disabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[2]: 'Disabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[3]: 'Disabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.UP, [{SutConfig.Sup.TPM_LIST[0]: 'Disabled'}], 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.DEL)
        if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
            logging.info(f'{SutConfig.Sup.TPM_LIST}都关闭，正常启动')
    else:
        stylelog.fail(f'{SutConfig.Sup.TPM_LIST}都关闭，没有启动')
        wrong_msg.append(f'{SutConfig.Sup.TPM_LIST}都关闭，没有启动')
        count += 1
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)
    # rev=re.findall('Current Rev of TPM2 ACPI Table *(Rev \d)',data)
    ppi = re.findall('Current PPI Version *([\d\.]+)', data)
    hard_support = re.findall('TPM2 Hardware Supported Hash Algorithm *([A-Z\_\d ,]+)BIOS', data)[0].replace(' ',
                                                                                                             '').split(
        ',')
    bios_support = re.findall('BIOS Supported Hash Algorithm *([A-Z\_\d ,]+)TPM', data)[0].replace(' ', '').split(',')
    # assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Sup.REV_NAME],25,delay=2)
    # rev_support=SetUpLib.get_value_list()
    # rev_support.remove(rev[0])
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.PPI_NAME], 25, delay=2)
    ppi_support = SetUpLib.get_value_list()
    ppi_support.remove(ppi[0])
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    for i in range(0, len(ppi_support)):
        # for i in range(0,max([len(ppi_support),len(rev_support)])):
        # if i < len(rev_support):
        #     assert SetUpLib.enter_menu_change_value(Key.DOWN,[{SutConfig.Sup.REV_NAME:rev_support[i]}],18)
        if i < len(ppi_support):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.PPI_NAME: ppi_support[i]}], 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        # if i < len(rev_support):
        #     if re.search(f'Current Rev of TPM2 ACPI Table *{rev_support[i]}',data) :
        #         logging.info(f'修改{SutConfig.Sup.REV_NAME}为{rev_support[i]}，成功')
        #     else:
        #         stylelog.fail(f'修改{SutConfig.Sup.REV_NAME}为{rev_support[i]}，失败')
        #         wrong_msg.append(f'修改{SutConfig.Sup.REV_NAME}为{rev_support[i]}，失败')
        #         count+=1
        if i < len(ppi_support):
            if re.search(f'Current PPI Version *{ppi_support[i]}', data):
                logging.info(f'修改{SutConfig.Sup.PPI_NAME}为{ppi_support[i]}成功')
            else:
                stylelog.fail(f'修改{SutConfig.Sup.PPI_NAME}为{ppi_support[i]}失败')
                wrong_msg.append(f'修改{SutConfig.Sup.PPI_NAME}为{ppi_support[i]}失败')
                count += 1
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(2)
    all_support = [i for i in hard_support if i in bios_support]
    for i in all_support:
        if re.search(f'\[ \] *PCR Bank: {i}', data):
            assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {i}'], 25, delay=2)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {all_support[0]}'], 25, delay=2)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if len(all_support) > 1:
        if SetUpLib.wait_message(f"{SutConfig.Sup.PCR_BANK_MSG}{', '.join(all_support)}", 300):
            logging.info('全选PCR BANK,启动时显示全部PCR BANK')
            SetUpLib.send_key(Key.F12)
            start = time.time()
            if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                end = time.time()
                spent_time = end - start
                if abs(spent_time - spent) < base_time:
                    logging.info('F12后重启')
                else:
                    stylelog.fail('F12没有重启')
                    count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.DEL)
                if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('F12后宕机')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            stylelog.fail('全选PCR BANK,启动时没有显示全部PCR BANK')
            wrong_msg.append('全选PCR BANK,启动时没有显示全部PCR BANK')
            count += 1
            assert SetUpLib.boot_to_setup()
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(2)
    if all(re.search(f'\[X\] *PCR Bank: {i}', data) for i in all_support):
        logging.info('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
    else:
        stylelog.fail('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
        wrong_msg.append('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
        count += 1
    if len(all_support) > 1:
        for i in all_support:
            SetUpLib.send_key(Key.ESC)
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            data = SetUpLib.get_data(2)
            for m in all_support:
                if re.search(f'\[ \] *PCR Bank: {m}', data):
                    assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {m}'], 25, delay=2)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(2)

            for j in all_support:
                if j != i:
                    assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {j}'], 25, delay=2)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)
            if SetUpLib.wait_message(f"{SutConfig.Sup.PCR_BANK_MSG}{i}", 300):
                logging.info(f'选择PCR Bank 为{i},启动时显示{i}')
                SetUpLib.send_key(Key.F12)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) < base_time:
                        logging.info('F12后重启')
                    else:
                        stylelog.fail('F12没有重启')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(Key.DEL)
                    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('F12后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail(f'选择PCR Bank 为{i},启动时没有显示{i}')
                wrong_msg.append(f'选择PCR Bank 为{i},启动时没有显示{i}')
                count += 1
                assert SetUpLib.boot_to_setup()

            assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            data = SetUpLib.get_data(2)
            if re.search(f'Active PCR Banks *{i}', data):
                logging.info(f'选择PCR Bank 为{i},SetUp下显示正常')
            else:
                stylelog.fail(f'选择PCR Bank 为{i},SetUp下显示异常')
                wrong_msg.append(f'选择PCR Bank 为{i},SetUp下显示异常')
                count += 1
    for i in SutConfig.Sup.CHANGE_TPM_VALUE:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Sup.ESC_MSG):
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            start = time.time()
            if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                end = time.time()
                spent_time = end - start
                if abs(spent_time - spent) > base_time:
                    logging.info('ESC后继续启动')
                else:
                    stylelog.fail('ESC没有继续启动')
                    count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.DEL)
                if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('ESC后宕机')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            wrong_msg.append('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
        SetUpLib.send_key(Key.ENTER)
        if re.search('No Action', SetUpLib.get_data(3)):
            logging.info('一次启动后,TPM2操作变为无动作')
        else:
            stylelog.fail('一次启动后,TPM2操作没有变为无动作')
            wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
            count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Sup.ESC_MSG):
            time.sleep(1)
            SetUpLib.send_key(Key.F12)
            start = time.time()
            if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                end = time.time()
                spent_time = end - start
                if abs(spent_time - spent) < base_time:
                    logging.info('F12后重启')
                else:
                    stylelog.fail('F12没有重启')
                    count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.DEL)
                if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('F12后宕机')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            wrong_msg.append('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            count += 1
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
        SetUpLib.send_key(Key.ENTER)
        if re.search('No Action', SetUpLib.get_data(3)):
            logging.info('一次启动后,TPM2操作变为无动作')
        else:
            stylelog.fail('一次启动后,TPM2操作没有变为无动作')
            wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
            count += 1

    logging.info('DTPM测试...............................................................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_DTPM, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_TPM_STATE, 18)
    SetUpLib.clean_buffer()
    SetUpLib.send_key(Key.DOWN)
    result1 = SetUpLib.get_data(1)
    SetUpLib.send_key(Key.DOWN)
    if result1 == SetUpLib.get_data(1):
        logging.info('TPM State 设为关闭，自动隐藏选项')
    else:
        stylelog.fail('TPM State 设为关闭，没有自动隐藏选项')
        wrong_msg.append('TPM State 设为关闭，没有自动隐藏选项')
        count += 1
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if re.search('TPM Version *{0}'.format(SutConfig.Sup.DTPM_MSG), SetUpLib.get_data(2)):
        logging.info('TPM State设为关闭，SetUp下显示{0}'.format(SutConfig.Sup.DTPM_MSG))
    else:
        stylelog.fail('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sup.DTPM_MSG))
        wrong_msg.append('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sup.DTPM_MSG))
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_TPM_STATE, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[0]: 'Disabled'}], 18)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.TPM_LIST[1]], 5) and not SetUpLib.locate_option(Key.UP, [
        SutConfig.Sup.TPM_LIST[2]], 5) and not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.TPM_LIST[3]], 5):
        logging.info(
            f'关闭{SutConfig.Sup.TPM_LIST[0]},{SutConfig.Sup.TPM_LIST[1]}和{SutConfig.Sup.TPM_LIST[2]}和{SutConfig.Sup.TPM_LIST[3]}都置灰')
    else:
        logging.info(
            f'关闭{SutConfig.Sup.TPM_LIST[0]},{SutConfig.Sup.TPM_LIST[1]}、{SutConfig.Sup.TPM_LIST[2]}、{SutConfig.Sup.TPM_LIST[3]}没有置灰')
        wrong_msg.append(
            f'关闭{SutConfig.Sup.TPM_LIST[0]},{SutConfig.Sup.TPM_LIST[1]}、{SutConfig.Sup.TPM_LIST[2]}、{SutConfig.Sup.TPM_LIST[3]}没有置灰')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[0]: 'Enabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[1]: 'Disabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[2]: 'Disabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.TPM_LIST[3]: 'Disabled'}], 18)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.UP, [{SutConfig.Sup.TPM_LIST[0]: 'Disabled'}], 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        SetUpLib.send_key(Key.DEL)
        if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
            logging.info(f'{SutConfig.Sup.TPM_LIST}都关闭，正常启动')
    else:
        stylelog.fail(f'{SutConfig.Sup.TPM_LIST}都关闭，没有启动')
        wrong_msg.append(f'{SutConfig.Sup.TPM_LIST}都关闭，没有启动')
        count += 1
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)
    rev = re.findall('Current Rev of TPM2 ACPI Table *(Rev \d)', data)
    ppi = re.findall('Current PPI Version *([\d\.]+)', data)
    hard_support = re.findall('TPM2 Hardware Supported Hash Algorithm *([A-Z\_\d ,]+)BIOS', data)[0].replace(' ',
                                                                                                             '').split(
        ',')
    bios_support = re.findall('BIOS Supported Hash Algorithm *([A-Z\_\d ,]+)TPM', data)[0].replace(' ', '').split(',')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.REV_NAME], 25, delay=2)
    rev_support = SetUpLib.get_value_list()
    rev_support.remove(rev[0])
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sup.PPI_NAME], 25, delay=2)
    ppi_support = SetUpLib.get_value_list()
    ppi_support.remove(ppi[0])
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    for i in range(0, max([len(ppi_support), len(rev_support)])):
        if i < len(rev_support):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.REV_NAME: rev_support[i]}], 18)
        if i < len(ppi_support):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.PPI_NAME: ppi_support[i]}], 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        if i < len(rev_support):
            if re.search(f'Current Rev of TPM2 ACPI Table *{rev_support[i]}', data):
                logging.info(f'修改{SutConfig.Sup.REV_NAME}为{rev_support[i]}，成功')
            else:
                stylelog.fail(f'修改{SutConfig.Sup.REV_NAME}为{rev_support[i]}，失败')
                wrong_msg.append(f'修改{SutConfig.Sup.REV_NAME}为{rev_support[i]}，失败')
                count += 1
        if i < len(ppi_support):
            if re.search(f'Current PPI Version *{ppi_support[i]}', data):
                logging.info(f'修改{SutConfig.Sup.PPI_NAME}为{ppi_support[i]}成功')
            else:
                stylelog.fail(f'修改{SutConfig.Sup.PPI_NAME}为{ppi_support[i]}失败')
                wrong_msg.append(f'修改{SutConfig.Sup.PPI_NAME}为{ppi_support[i]}失败')
                count += 1
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(2)
    all_support = [i for i in hard_support if i in bios_support]
    for i in all_support:
        if re.search(f'\[ \] *PCR Bank: {i}', data):
            assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {i}'], 25, delay=2)
            SetUpLib.clean_buffer()
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {all_support[0]}'], 25, delay=2)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if len(all_support) > 1:
        if SetUpLib.wait_message(f"{SutConfig.Sup.PCR_BANK_MSG}{', '.join(all_support)}", 300):
            logging.info('全选PCR BANK,启动时显示全部PCR BANK')
            SetUpLib.send_key(Key.F12)
            start = time.time()
            if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                end = time.time()
                spent_time = end - start
                if abs(spent_time - spent) < base_time:
                    logging.info('F12后重启')
                else:
                    stylelog.fail('F12没有重启')
                    count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.DEL)
                if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('F12后宕机')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            stylelog.fail('全选PCR BANK,启动时没有显示全部PCR BANK')
            wrong_msg.append('全选PCR BANK,启动时没有显示全部PCR BANK')
            count += 1
            assert SetUpLib.boot_to_setup()
    else:
        assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(2)
    if all(re.search(f'\[X\] *PCR Bank: {i}', data) for i in all_support):
        logging.info('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
    else:
        stylelog.fail('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
        wrong_msg.append('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
        count += 1
    if len(all_support) > 1:
        for i in all_support:
            SetUpLib.send_key(Key.ESC)
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            data = SetUpLib.get_data(2)
            for m in all_support:
                if re.search(f'\[ \] *PCR Bank: {m}', data):
                    assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {m}'], 25, delay=2)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(2)

            for j in all_support:
                if j != i:
                    assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {j}'], 25, delay=2)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)
            if SetUpLib.wait_message(f"{SutConfig.Sup.PCR_BANK_MSG}{i}", 300):
                logging.info(f'选择PCR Bank 为{i},启动时显示{i}')
                SetUpLib.send_key(Key.F12)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) < base_time:
                        logging.info('F12后重启')
                    else:
                        stylelog.fail('F12没有重启')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(Key.DEL)
                    if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('F12后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail(f'选择PCR Bank 为{i},启动时没有显示{i}')
                wrong_msg.append(f'选择PCR Bank 为{i},启动时没有显示{i}')
                count += 1
                BmcLib.init_sut()
                assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
            assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            data = SetUpLib.get_data(2)
            if re.search(f'Active PCR Banks *{i}', data):
                logging.info(f'选择PCR Bank 为{i},SetUp下显示正常')
            else:
                stylelog.fail(f'选择PCR Bank 为{i},SetUp下显示异常')
                wrong_msg.append(f'选择PCR Bank 为{i},SetUp下显示异常')
                count += 1
    for i in SutConfig.Sup.CHANGE_TPM_VALUE:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Sup.ESC_MSG):
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            start = time.time()
            if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                end = time.time()
                spent_time = end - start
                if abs(spent_time - spent) > base_time:
                    logging.info('ESC后继续启动')
                else:
                    stylelog.fail('ESC没有继续启动')
                    count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.DEL)
                if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('ESC后宕机')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            wrong_msg.append('修改{0}，启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
        SetUpLib.send_key(Key.ENTER)
        if re.search('No Action', SetUpLib.get_data(3)):
            logging.info('一次启动后,TPM2操作变为无动作')
        else:
            stylelog.fail('一次启动后,TPM2操作没有变为无动作')
            wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
            count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Sup.ESC_MSG):
            time.sleep(1)
            SetUpLib.send_key(Key.F12)
            start = time.time()
            if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                end = time.time()
                spent_time = end - start
                if abs(spent_time - spent) < base_time:
                    logging.info('F12后重启')
                else:
                    stylelog.fail('F12没有重启')
                    count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.DEL)
                if not SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 90):
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('F12后宕机')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            wrong_msg.append('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sup.ESC_MSG))
            count += 1
            BmcLib.init_sut()
            assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_TCG2, 18)
        SetUpLib.send_key(Key.ENTER)
        if re.search('No Action', SetUpLib.get_data(3)):
            logging.info('一次启动后,TPM2操作变为无动作')
        else:
            stylelog.fail('一次启动后,TPM2操作没有变为无动作')
            wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
            count += 1
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def tpcm():
    count = 0
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    try:
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_TPCM, 18, save=True)
    except:
        logging.info('无法打开调试模式，跳过测试')
        return 2
    if not SetUpLib.wait_message(SutConfig.Sup.TPCM_MSG, 300):
        stylelog.fail(f'打开TPCM,串口日志中没有{SutConfig.Sup.TPCM_MSG}')
        count+=1
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_TPCM, 18, save=True)
    if SetUpLib.wait_message(SutConfig.Sup.TPCM_MSG, 300):
        stylelog.fail(f'关闭TPCM,串口日志仍出现{SutConfig.Sup.TPCM_MSG}')
        count+=1
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_DEBUG, 18, save=True)
    return True if count == 0 else False
