# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *


def uefi_pxe_once_nor():
    BmcLib.power_off()
    time.sleep(8)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    if boot_mode == 'UEFI':
        logging.info('修改第一启动项为USB')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 18)
        logging.info('修改第一启动项为USB')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
    arg = SutConfig.Env.UEFI_PXE_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL修改PXE启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改PXE启动一次，第一次成功启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改PXE启动一次，第一次没有启动到PXE')
            return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.BOTH_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改PXE启动一次，第二次启动没有启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改PXE启动一次，第二次启动仍启动到PXE')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI PXE启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI PXE启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI PXE启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI PXE启动一次，第二次之后启动模式改变')
            return


def uefi_setup_once_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    logging.info('修改第一启动项为USB')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.UEFI_SETUP_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改SETUP启动一次')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改SETUP启动一次，第一次成功启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改SETUP启动一次，第一次没有启动到Setup')
            return
    else:
        stylelog.fail('启动失败')
        return
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
        logging.info('Ipmitool修改UEFI SetUp启动一次，第一次启动模式更改为UEFI')
    else:
        stylelog.fail('Ipmitool修改UEFI SetUp启动一次，第一次启动模式没有更改为UEFI')
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                     pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改SETUP启动一次，第二次启动并未启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改SETUP启动一次，第二次启动仍启动到SetUp')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI SetUp启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI SetUp启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI SetUp启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI SetUp启动一次，第二次之后启动模式改变')
            return


def uefi_hdd_once_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    if boot_mode == 'UEFI':
        logging.info('修改启动项第一项为USB。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 18)
        logging.info('修改启动项第一项为USB。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    arg = SutConfig.Env.UEFI_HDD_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改硬盘启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    time.sleep(2)
    BmcLib.enable_serial_normal()
    start_time = time.time()
    datas = []
    while time.time() - start_time < 200:
        datas.append(SetUpLib.get_data(1))
        if re.search(SutConfig.Msg.POST_MESSAGE,''.join(datas)):
            datas.append(SetUpLib.get_data(2))
            break
    data = ''.join(datas)
    if re.search(SutConfig.Ipm.OS_MSG, data):
        logging.info('IPMITOOL 修改UEFi硬盘启动一次,第一次启动模式为UEFI')
    else:
        stylelog.fail('IPMITOOL 修改UEFi硬盘启动一次,第一次启动模式为Legacy')
        return
    if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
        logging.info('没有启动到U盘')
    else:
        stylelog.fail('IPMITOOL 修改硬盘启动，但仍启动到U盘')
        return
    if BmcLib.ping_sut():
        logging.info('IPMITOOL 修改硬盘启动一次,第一次成功进入系统')
    else:
        stylelog.fail('IPMITOOL 修改硬盘启动一次,第一次并未进入系统')
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.BOTH_USB_MSG, 50, readline=False):
            stylelog.fail('IPMITOOL 修改硬盘启动一次,第二次启动没有启动到U盘')
            return
        else:
            logging.info('IPMITOOL 修改硬盘启动一次,第二次启动并未启动到硬盘，而是启动到U盘')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI HDD启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI HDD启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI HDD启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI HDD启动一次，第二次之后启动模式改变')
            return


def uefi_usb_once_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 18)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    if boot_mode == 'UEFI':

        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
        logging.info('修改启动项第一项为PXE。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
        logging.info('修改启动项第一项为PXE。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    arg = SutConfig.Env.UEFI_USB_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改USB启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改USB启动一次，第一次成功启动到U盘')
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，第一次没有启动到U盘')
            return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.BOTH_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改USB启动一次，第二次启动并未启动到USB,而是启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，第二次启动没有启动到PXE')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI USB启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI USB启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改UEFI USB启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改UEFI USB启动一次，第二次之后启动模式改变')
            return


def uefi_pxe_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
    logging.info('修改第一启动项为USB')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)

    arg = SutConfig.Env.UEFI_PXE_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久PXE启动')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久PXE启动，第一次成功启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改永久PXE启动，第一次没有启动到PXE')
            return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久PXE启动，第二次启动成功启动到PXE')

        else:
            stylelog.fail('IPMITOOL 修改永久PXE启动，第二次启动并未启动到PXE')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<UEFI>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改UEFI永久PXE启动 ，启动模式被修改为UEFI')
    else:
        stylelog.fail('IPMITOOL 修改UEFI永久PXE启动 ，启动模式没有被修改为UEFI')
        return
    data = datas.replace('►', '').split('Boot Order')[1]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.PXE_BOOT_NAME:
        logging.info('setup下第一启动顺序为内置网络设备')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是内置网络设备而是{0}'.format(options[0]))
        return


def uefi_setup_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    logging.info('修改第一启动项为USB')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.UEFI_SETUP_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久SETUP启动')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改永久SETUP启动，第一次成功启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改永久SETUP启动，第一次没有启动到Setup')
            return
    else:
        stylelog.fail('启动失败')
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改永久SETUP启动，第二次启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改永久SETUP启动，第二次启动没有启动到SetUp')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<UEFI>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改UEFI永久SetUp启动 ，启动模式被修改为UEFI')
        return True
    else:
        stylelog.fail('IPMITOOL 修改UEFI永久SetUpp启动 ，启动模式没有被修改为UEFI')
        return


def uefi_hdd_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    logging.info('修改启动项第一项为USB。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    arg = SutConfig.Env.UEFI_HDD_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久硬盘启动')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('没有启动到U盘')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动，但仍启动到U盘')
            return
        if BmcLib.ping_sut():
            logging.info('IPMITOOL 修改永久从硬盘启动,第一次启动成功进入系统')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动,第一次启动并未进入系统')
            return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('第二次没有启动到U盘')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动，但仍启动到U盘')
            return
        if BmcLib.ping_sut():
            logging.info('IPMITOOL 修改永久从硬盘启动,第二次启动成功进入系统')

        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动,第二次启动并未进入系统')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<UEFI>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改UEFI永久HDD启动 ，启动模式被修改为UEFI')
    else:
        stylelog.fail('IPMITOOL 修改UEFI永久HDD启动 ，启动模式没有被修改为UEFI')
        return
    data = datas.replace('►', '').split('Boot Order')[1]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.HDD_BOOT_NAME:
        logging.info('setup下第一启动顺序为内置硬盘驱动器')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是内置硬盘驱动器而是{0}'.format(options[0]))
        return


def uefi_usb_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
    logging.info('修改启动项第一项为PXE。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.UEFI_USB_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从USB启动')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从USB启动，第一次成功启动到USB')
        else:
            stylelog.fail('IPMITOOL 修改永久从USB启动，第一次没有启动到USB')
            return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从USB启动，第二次成功启动到USB')
        else:
            logging.info('IPMITOOL 修改永久从USB启动，第二次没有启动到USB')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<UEFI>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改UEFI永久USB启动 ，启动模式被修改为UEFI')
    else:
        stylelog.fail('IPMITOOL 修改UEFI永久USB启动 ，启动模式没有被修改为UEFI')
        return
    data = datas.replace('►', '').split('Boot Order')[1]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.USB_BOOT_NAME:
        logging.info('setup下第一启动顺序为USB闪存驱动器/USB 硬盘')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是USB闪存驱动器/USB 硬盘而是{0}'.format(options[0]))
        return


def uefi_odd_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    logging.info('修改启动项第一项为U盘。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.UEFI_ODD_ALWAYS

    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从ODD启动')

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<UEFI>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改UEFI永久ODD启动 ，启动模式被修改为UEFI')
    else:
        stylelog.fail('IPMITOOL 修改UEFI永久ODD启动 ，启动模式没有被修改为UEFI')
        return
    data = datas.replace('►', '').split('Boot Order')[1]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.ODD_BOOT_NAME:
        logging.info('setup下第一启动顺序为USB CD/DVD光驱')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是USB CD/DVD光驱而是{0}'.format(options[0]))
        return


def legacy_pxe_once_nor():
    BmcLib.power_off()
    time.sleep(8)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mode', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    if boot_mode == 'Legacy':
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
        logging.info('修改第一启动项为USB')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
        logging.info('修改第一启动项为USB')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)

    arg = SutConfig.Env.LEGACY_PXE_ONCE

    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改PXE启动一次')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改PXE启动一次，成功启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改PXE启动一次，没有启动到PXE')
            return
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.BOTH_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改PXE启动一次，第二次并未启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改PXE启动一次，第二次仍启动到PXE')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 3):
            logging.info('Ipmitool修改Legacy PXE启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy PXE启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 3):
            logging.info('Ipmitool修改Legacy PXE启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy PXE启动一次，第二次之后启动模式改变')
            return


def legacy_setup_once_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    logging.info('修改第一启动项为USB')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.LEGACY_SETUP_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改SETUP启动一次')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改SETUP启动一次，第一次成功启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改SETUP启动一次，第一次没有启动到Setup')
            return
    else:
        stylelog.fail('启动失败')
        return
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
        logging.info('Ipmitool修改Legacy SetUp启动一次，第一次启动模式更改为Legacy')
    else:
        stylelog.fail('Ipmitool修改Legacy SetUp启动一次，第一次启动模式没有更改为Legacy')
        return

    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                     pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改SETUP启动一次，第二次启动并未启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改SETUP启动一次，第二次启动仍启动到SetUp')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改Legacy SetUp启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy SetUp启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改Legacy SetUp启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy SetUp启动一次，第二次之后启动模式改变')
            return


def legacy_usb_once_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    if boot_mode == 'Legacy':
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
        logging.info('修改启动项第一项为PXE。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
        logging.info('修改启动项第一项为PXE。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    arg = SutConfig.Env.LEGACY_USB_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改USB启动一次')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改USB启动一次，成功启动到USB')
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，没有启动到USB')
            return
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.BOTH_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改USB启动一次，第二次启动并未启动到USB,而是启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，第二次启动没有启动到PXE')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改Legacy USB启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy USB启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改Legacy USB启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy USB启动一次，第二次之后启动模式改变')
            return


def legacy_hdd_once_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 3):
        logging.info('当前启动模式为Legacy')
        boot_mode = 'Legacy'
    else:
        logging.info('当前启动模式为UEFI')
        boot_mode = 'UEFI'
    if boot_mode == 'Legacy':
        logging.info('修改启动项第一项为USB。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 18)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
        logging.info('修改启动项第一项为USB。')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    arg = SutConfig.Env.LEGACY_HDD_ONCE
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改HDD启动一次')
    BmcLib.init_sut()
    time.sleep(2)
    BmcLib.enable_serial_normal()
    start_time = time.time()
    datas = []
    while time.time() - start_time < 200:
        datas.append(SetUpLib.get_data(1))
        if re.search(SutConfig.Msg.POST_MESSAGE, ''.join(datas)):
            datas.append(SetUpLib.get_data(2))
            break
    data = ''.join(datas)
    if re.search(SutConfig.Ipm.OS_MSG, data):
        stylelog.fail('IPMITOOL 修改Legacy 硬盘启动一次,第一次启动模式为UEFI')
        return
    else:
        logging.info('IPMITOOL 修改Legacy 硬盘启动一次,第一次启动模式为Legacy')
    if not SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
        logging.info('没有启动到U盘')
    else:
        stylelog.fail('IPMITOOL 修改硬盘启动，但仍启动到U盘')
        return
    if BmcLib.ping_sut():
        logging.info('IPMITOOL 修改硬盘启动一次,第一次成功进入系统')
    else:
        stylelog.fail('IPMITOOL 修改硬盘启动一次,第一次并未进入系统')
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.BOTH_USB_MSG, 50, readline=False):
            stylelog.fail('IPMITOOL 修改硬盘启动一次,第二次启动没有启动到U盘')
            return
        else:
            logging.info('IPMITOOL 修改硬盘启动一次,第二次启动并未启动到硬盘，而是启动到U盘')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    if boot_mode == 'Legacy':
        if SetUpLib.wait_message('<Legacy>.*Boot Mode', 5):
            logging.info('Ipmitool修改Legacy HDD启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy HDD启动一次，第二次之后启动模式改变')
            return
    else:
        if SetUpLib.wait_message('<UEFI>.*Boot Mode', 5):
            logging.info('Ipmitool修改Legacy HDD启动一次，第二次之后启动模式没有改变')
            return True
        else:
            stylelog.fail('Ipmitool修改Legacy HDD启动一次，第二次之后启动模式改变')
            return


def legacy_pxe_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
    logging.info('修改第一启动项为USB')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.LEGACY_PXE_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从PXE启动')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从PXE启动，第一次成功启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改永久从PXE启动，第一次没有启动到PXE')
            return
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从PXE启动，第二次成功启动到PXE')

        else:
            stylelog.fail('IPMITOOL 修改永久从PXE启动，第二次没有启动到PXE')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<Legacy>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改Legacy永久PXE启动 ，启动模式被修改为Legacy')
    else:
        stylelog.fail('IPMITOOL 修改Legacy永久PXE启动 ，启动模式没有被修改为Legacy')
        return
    datas = datas.replace('►', '').split('Boot Order')
    if len(datas) == 2:
        data = datas[1]
    elif len(datas) == 3:
        data = datas[2]
    else:
        data = datas[2]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.PXE_BOOT_NAME:
        logging.info('setup下第一启动顺序为内置网络设备')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是内置网络设备而是{0}'.format(options[0]))
        return


def legacy_setup_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    logging.info('修改第一启动项为USB')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.LEGACY_SETUP_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久SETUP启动')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改永久SETUP启动，第一次成功启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改永久SETUP启动，第一次没有启动到Setup')
            return
    else:
        stylelog.fail('启动失败')
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改永久SETUP启动，第二次启动到Setup')
        else:
            stylelog.fail('IPMITOOL 修改永久SETUP启动，第二次启动没有启动到SetUp')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<Legacy>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改Legacy永久SetUp启动 ，启动模式被修改为Legacy')
        return True
    else:
        stylelog.fail('IPMITOOL 修改Legacy永久SetUpp启动 ，启动模式没有被修改为Legacy')
        return


def legacy_usb_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 10)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 8)
    logging.info('修改启动项第一项为PXE。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    arg = SutConfig.Env.LEGACY_USB_ALWAYS

    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从USB启动')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从USB启动，第一次成功启动到U盘')
        else:
            stylelog.fail('IPMITOOL 修改永久从USB启动，第一次没有启动到U盘')
            return
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从USB启动，第二次成功启动到U盘')

        else:
            stylelog.fail('IPMITOOL 修改永久从USB启动，第二次没有启动到U盘')

    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<Legacy>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改Legacy永久USB启动 ，启动模式被修改为Legacy')
    else:
        stylelog.fail('IPMITOOL 修改Legacy永久USB启动 ，启动模式没有被修改为Legacy')
        return
    datas = datas.replace('►', '').split('Boot Order')
    if len(datas) == 2:
        data = datas[1]
    elif len(datas) == 3:
        data = datas[2]
    else:
        data = datas[2]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.USB_BOOT_NAME:
        logging.info('setup下第一启动顺序为USB闪存驱动器/USB 硬盘')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是USB闪存驱动器/USB 硬盘而是{0}'.format(options[0]))
        return


def legacy_hdd_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    logging.info('修改启动项第一项为USB。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    arg = SutConfig.Env.LEGACY_HDD_ALWAYS
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久硬盘启动')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('没有启动到U盘')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动，但仍启动到U盘')
            return
        if BmcLib.ping_sut():
            logging.info('IPMITOOL 修改永久从硬盘启动,第一次启动成功进入系统')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动,第一次启动并未进入系统')
            return
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('第二次没有启动到U盘')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动，但仍启动到U盘')
            return
        if BmcLib.ping_sut():
            logging.info('IPMITOOL 修改永久从硬盘启动,第二次启动成功进入系统')

        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动,第二次启动并未进入系统')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<Legacy>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改Legacy永久HDD启动 ，启动模式被修改为Legacy')
    else:
        stylelog.fail('IPMITOOL 修改Legacy永久HDD启动 ，启动模式没有被修改为Legacy')
        return
    datas = datas.replace('►', '').split('Boot Order')
    if len(datas) == 2:
        data = datas[1]
    elif len(datas) == 3:
        data = datas[2]
    else:
        data = datas[2]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.HDD_BOOT_NAME:
        logging.info('setup下第一启动顺序为内置硬盘驱动器')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是内置硬盘驱动器而是{0}'.format(options[0]))
        return


def legacy_odd_always_nor():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    logging.info('修改启动项第一项为U盘。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.LEGACY_ODD_ALWAYS

    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从ODD启动')

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 10)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2)
    if re.search('<Legacy>.*Boot Mode', datas):
        logging.info('IPMITOOL 修改Legacy永久ODD启动 ，启动模式被修改为Legacy')
    else:
        stylelog.fail('IPMITOOL 修改Legacy永久ODD启动 ，启动模式没有被修改为Legacy')
        return
    datas = datas.replace('►', '').split('Boot Order')

    if len(datas) == 2:
        data = datas[1]
    elif len(datas) == 3:
        data = datas[2]
    else:
        data = datas[2]
    options = []
    for i in data.split('  '):
        if i != '':
            options.append(i.strip(' '))
    if options[0] == SutConfig.Msg.ODD_BOOT_NAME:
        logging.info('setup下第一启动顺序为USB CD/DVD光驱')
        return True
    else:
        stylelog.fail('setup下第一启动顺序不是USB CD/DVD光驱而是{0}'.format(options[0]))
        return
