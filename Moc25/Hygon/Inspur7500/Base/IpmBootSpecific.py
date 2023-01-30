# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *


def uefi_pxe_once_spe():
    BmcLib.power_off()
    time.sleep(8)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 18)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改第一启动项为其它（内置SHELL）')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.OTHER_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.PXE_ONCE_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改PXE启动一次')
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
        if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改PXE启动一次，第二次启动没有启动到PXE')
            return True
        else:
            stylelog.fail('IPMITOOL 修改PXE启动一次，第二次启动仍启动到PXE')
            return
    else:
        return


def uefi_setup_once_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.SETUP_ONCE_COMMON
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
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                     pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改SETUP启动一次，第二次启动并未启动到Setup')
            return True
        else:
            stylelog.fail('IPMITOOL 修改SETUP启动一次，第二次启动仍启动到Setup')
            return
    else:
        return


def uefi_hdd_once_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    logging.info('修改启动项第一项为其它（内置Shell）。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.OTHER_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.HDD_ONCE_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改硬盘启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('没有启动到Shell')
        else:
            stylelog.fail('IPMITOOL 修改硬盘启动，但仍启动到Shell')
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
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('找到UEFI Interactive Shell')
            logging.info('IPMITOOL 修改硬盘启动一次,第二次启动并未启动到硬盘，而是启动到Shell')
            return True
        else:
            return
    else:
        return


def uefi_usb_once_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    logging.info('修改启动项第一项为内置硬盘驱动器。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HDD_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.USB_ONCE_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改USB启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改USB启动一次，第一次成功启动到USB')
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，第一次没有启动到USB')
            return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('没有找到UEFI Interactive Shell')
            logging.info('IPMITOOL 修改USB启动一次，第二次启动并未启动到USB')
            if BmcLib.ping_sut():
                logging.info('IPMITOOL 修改USB启动一次，第二次启动到硬盘，成功进入系统')
                return True
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，第二次启动仍启动到USB')
            return
    else:
        return


def uefi_pxe_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改第一启动项为其它（内置SHELL）')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.OTHER_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.PXE_ALWAYS_COMMON
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
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    data = SetUpLib.get_data(2).replace('►', '').split('Boot Order')[1]
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


def uefi_setup_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.SETUP_ALWAYS_COMMON
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
            return True
        else:
            stylelog.fail('IPMITOOL 修改永久SETUP启动，第二次启动没有启动到Setup')
            return
    else:
        return


def uefi_hdd_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    logging.info('修改启动项第一项为其它（内置Shell）。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.OTHER_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    arg = SutConfig.Env.HDD_ALWAYS_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久硬盘启动')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.UEFI_USB_MSG, 50, readline=False):
            logging.info('没有启动到Shell')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动，但仍启动到Shell')
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
            logging.info('第二次没有启动到Shell')
        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动，但仍启动到Shell')
            return
        if BmcLib.ping_sut():
            logging.info('IPMITOOL 修改永久从硬盘启动,第二次启动成功进入系统')

        else:
            stylelog.fail('IPMITOOL 修改永久从硬盘启动,第二次启动并未进入系统')
            return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    data = SetUpLib.get_data(2).replace('►', '').split('Boot Order')[1]
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


def uefi_usb_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    logging.info('修改启动项第一项为内置硬盘驱动器。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HDD_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)

    arg = SutConfig.Env.USB_ALWAYS_COMMON
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
            if BmcLib.ping_sut():
                stylelog.fail('IPMITOOL 修改永久从USB启动，第二次启动到硬盘')
                return
            else:
                return
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    data = SetUpLib.get_data(2).replace('►', '').split('Boot Order')[1]
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


def uefi_odd_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_UEFI, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SHELL, 10)
    logging.info('修改启动项第一项为内置网络设备。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    arg = SutConfig.Env.ODD_ALWAYS_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从ODD启动')
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    data = SetUpLib.get_data(2).replace('►', '').split('Boot Order')[1]
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


def legacy_pxe_once_spe():
    BmcLib.power_off()
    time.sleep(8)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_LAN, 18)
    time.sleep(2)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改启动项第一项为USB。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.PXE_ONCE_COMMON
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
        if not SetUpLib.wait_message(SutConfig.Ipm.LEGACY_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改PXE启动一次，第二次并未启动到PXE')
            return True
        else:
            stylelog.fail('IPMITOOL 修改PXE启动一次，第二次仍启动到PXE')
            return
    else:
        return


def legacy_setup_once_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.SETUP_ONCE_COMMON
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
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                     pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改SETUP启动一次，第二次启动并未启动到Setup')
            return True
        else:
            stylelog.fail('IPMITOOL 修改SETUP启动一次，第二次启动仍启动到Setup')
            return
    else:
        return


def legacy_usb_once_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改启动项第一项为PXE。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.USB_ONCE_COMMON
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
        if not SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改USB启动一次，第二次并未启动到USB')
            return True
        else:
            stylelog.fail('IPMITOOL 修改USB启动一次，第二次仍启动到USB')
            return
    else:
        return


def legacy_hdd_once_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    logging.info('修改启动项第一项为USB。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.HDD_ONCE_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改HDD启动一次')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
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
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if not SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            stylelog.fail('IPMITOOL 修改硬盘启动一次,第二次启动没有启动到U盘')
            return
        else:
            logging.info('IPMITOOL 修改硬盘启动一次,第二次启动并未启动到硬盘，而是启动到U盘')
            return True
    else:
        return


def legacy_pxe_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改启动项第一项为USB。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.PXE_ALWAYS_COMMON
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
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2).replace('►', '').split('Boot Order')
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


def legacy_setup_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    arg = SutConfig.Env.SETUP_ALWAYS_COMMON
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
        logging.info('启动失败')
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 50, pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                 pw=PwdLib.PW.DEFAULT_PW, readline=False):
            logging.info('IPMITOOL 修改永久SETUP启动，第二次启动到Setup')
            return True
        else:
            stylelog.fail('IPMITOOL 修改永久SETUP启动，第二次启动没有启动到Setup')
            return
    else:
        return


def legacy_usb_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改启动项第一项为PXE。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.USB_ALWAYS_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从USB启动')
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从USB启动，第一次成功启动到USB')
        else:
            stylelog.fail('IPMITOOL 修改永久从USB启动，第一次没有启动到USB')
            return
    else:
        return
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_USB_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改永久从USB启动，第二次成功启动到USB')

        else:
            stylelog.fail('IPMITOOL 修改永久从USB启动，第二次没有启动到USB')

    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2).replace('►', '').split('Boot Order')
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


def legacy_hdd_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    logging.info('修改启动项第一项为USB。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.USB_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    arg = SutConfig.Env.HDD_ALWAYS_COMMON
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从HDD启动')
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
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2).replace('►', '').split('Boot Order')
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


def legacy_odd_always_spe():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.BOOT_MODE_LEGACY, 6)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_PXE, 4)
    logging.info('修改启动项第一项为PXE。')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_BOOT_NAME], 15)
    SetUpLib.send_keys([Key.ADD] * 5)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)

    arg = SutConfig.Env.ODD_ALWAYS_COMMON

    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run command: {0}'.format(arg))
    logging.info('IPMITOOL 修改永久从ODD启动')
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_BOOT, 8)
    SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
    datas = SetUpLib.get_data(2).replace('►', '').split('Boot Order')
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
