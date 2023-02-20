# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *


# PXE网络引导
def pxe_option_rom(oem):
    if oem is True:
        BmcLib.change_bios_value(['PXE:Disabled','OnLan:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.CLOSE_PXE, 18, save=True)
    datas = SetUpLib.boot_to_boot_menu(True)
    if 'PXE' not in datas:
        logging.info('PXE网络引导关闭，启动项没有出现PXE')
    else:
        stylelog.fail('PXE网络引导关闭，但启动项仍有PXE')
        return
    if oem is True:
        BmcLib.change_bios_value(['PXE:Enabled'])
    else:
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.OPEN_PXE, 18, save=True)
    datas = SetUpLib.boot_to_boot_menu(True)
    if 'PXE' in datas:
        logging.info('PXE网络引导打开，启动项出现PXE')
        return True
    else:
        stylelog.fail('PXE网络引导打开，但启动项没有出现PXE')
        return


def pxe_boot(oem):
    if oem is True:
        BmcLib.change_bios_value(['PXE:Enabled','OnLan:Enabled','BootMode:UEFI','IPVersion:IPv4'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_IPV4, 18, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.IPV4_MSG, 300, SutConfig.Msg.POST_MESSAGE)
    logging.info('IPv4PXE启动成功')
    if oem is True:
        BmcLib.change_bios_value(['IPVersion:IPv6'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_IPV6, 18, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.IPV6_MSG, 300, SutConfig.Msg.POST_MESSAGE)
    logging.info('IPv6PXE启动成功')
    if oem is True:
        BmcLib.change_bios_value(['BootMode:Legacy'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_LEGACY, 18, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F12,SutConfig.Ipm.LEGACY_PXE_MSG , 300, SutConfig.Msg.POST_MESSAGE)
    logging.info('LegacyPXE启动成功')
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_UEFI, 15, save=True)
    return True


# 网络重试
def pxe_retry(oem):
    retry_counts = 3
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI','PXE:Enabled','IPVersion:IPv4','PXERetry:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.CLOSE_PXE_RETRY, 18, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Ipm.UEFI_PXE_MSG, 200, SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(100)
    if BmcLib.ping_sut():
        logging.info('网络启动重试关闭，启动失败后，不再重新尝试，直接进入系统')
    else:
        return
    if oem is True:
        BmcLib.change_bios_value(['PXERetry:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.OPEN_PXE_RETRY, 18, save=True)
    SetUpLib.clean_buffer()
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Ipm.UEFI_PXE_MSG, 200, SutConfig.Msg.POST_MESSAGE)
    counts = 0
    while True:
        if SetUpLib.wait_message(SutConfig.Pxe.PXE_RETRY_MSG, 300):
            counts += 1
            logging.info('第{0}次网络重试'.format(counts))
        else:
            return
        if counts == retry_counts:
            # if not SetUpLib.wait_message(SutConfig.Pxe.PXE_RETRY_MSG,300):
            # logging.info(f'第{counts}次网络启动重试后不再进行重试')
            # if BmcLib.ping_sut():
            # logging.info('第{0}次网络启动重试后进入系统'.format(counts))
            # break
            # else:
            # return
            # else:
            # stylelog.fail(f'第{counts}次网络启动重试后，仍进行网络启动重试')
            # return
            break
    logging.info('网络启动重试打开，启动失败后，不断重新尝试启动。')
    return True


def pxe_retry_legacy(oem):
    count = 0
    wrong_msg = []
    retry_counts = 3
    if oem is True:
        BmcLib.change_bios_value(['BootMode:Legacy','PXE:Enabled','PXERetry:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.CLOSE_PXE_RETRY_LEGACY, 18, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Ipm.LEGACY_PXE_MSG, 200, SutConfig.Msg.POST_MESSAGE)
    if not SetUpLib.wait_message(SutConfig.Pxe.PXE_RETRY_MSG_LEGACY,150):
        logging.info('网络启动重试关闭，启动失败后，不再重新尝试，直接进入系统')
    else:
        stylelog.fail('网络启动重试关闭，仍进行网络启动重试')
        count += 1
        wrong_msg.append('网络启动重试关闭，仍进行网络启动重试')
    if oem is True:
        BmcLib.change_bios_value(['PXERetry:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.OPEN_PXE_RETRY_LEGACY, 18, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Ipm.LEGACY_PXE_MSG, 200, SutConfig.Msg.POST_MESSAGE)
    counts = 0
    while True:
        if SetUpLib.wait_message(SutConfig.Pxe.PXE_RETRY_MSG_LEGACY, 300):
            counts += 1
            logging.info('第{0}次网络重试'.format(counts))
        else:
            assert SetUpLib.boot_to_setup()
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_UEFI, 18, save=True)
            return
        if counts == retry_counts:
            # if not SetUpLib.wait_message(SutConfig.Pxe.PXE_RETRY_MSG,300):
            # logging.info(f'第{counts}次网络启动重试后不再进行重试')
            # if BmcLib.ping_sut():
            # logging.info('第{0}次网络启动重试后进入系统'.format(counts))
            # break
            # else:
            # return
            # else:
            # stylelog.fail(f'第{counts}次网络启动重试后，仍进行网络启动重试')
            # return
            break
    logging.info('网络启动重试打开，启动失败后，不断重新尝试启动。')
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI'])
    else:
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_UEFI, 18, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


# 网络引导版本
def pxe_protocol(oem):
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI','PXE:Enabled','IPVersion:All','OnLan:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_IPV4_6, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
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
    if oem is True:
        BmcLib.change_bios_value(['IPVersion:IPv4'])
    else:
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_IPV4, 18, save=True)
    data1 = SetUpLib.boot_to_boot_menu(True)
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
    if oem is True:
        BmcLib.change_bios_value(['IPVersion:IPv6'])
    else:
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_IPV6, 18, save=True)
    data2 = SetUpLib.boot_to_boot_menu(True)
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
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_ONBOARD, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    if not re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        logging.info('PXE启动网卡选择板载网卡，启动项中只有板载网卡，没有外插网卡')
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡选择板载网卡，启动项中既有板载网卡，也有外插网卡')
        wrong_msg.append('PXE启动网卡选择板载网卡，启动项中既有板载网卡，也有外插网卡')
        count += 1
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡选择板载网卡，启动项中有外插网卡，没有板载网卡')
        wrong_msg.append('PXE启动网卡选择板载网卡，启动项中有外插网卡，没有板载网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡选择板载网卡，启动项中没有外插网卡，也没有板载网卡')
        wrong_msg.append('PXE启动网卡选择板载网卡，启动项中没有外插网卡，也没有板载网卡')
        count += 1
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_ADDON, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    if re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        logging.info('PXE启动网卡选择外插网卡，启动项中只有外插网卡，没有板载网卡')
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡选择外插网卡，启动项中既有外插网卡，也有板载网卡')
        wrong_msg.append('PXE启动网卡选择外插网卡，启动项中既有外插网卡，也有板载网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡选择外插网卡，启动项中有板载网卡，没有外插网卡')
        wrong_msg.append('PXE启动网卡选择外插网卡，启动项中有板载网卡，没有外插网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡选择外插网卡，启动项中没有外插网卡，也没有板载网卡')
        wrong_msg.append('PXE启动网卡选择外插网卡，启动项中没有外插网卡，也没有板载网卡')
        count += 1
    else:
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_NONE, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    if re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        logging.info('PXE启动网卡不进行选择，启动项中既有外插网卡，也有板载网卡')
    elif re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡不进行选择，启动项中有外插网卡，没有板载网卡')
        wrong_msg.append('PXE启动网卡不进行选择，启动项中有外插网卡，没有板载网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡不进行选择，启动项中有板载网卡，没有外插网卡')
        wrong_msg.append('PXE启动网卡不进行选择，启动项中有板载网卡，没有外插网卡')
        count += 1
    elif not re.search(SutConfig.Pxe.PXE_PORT_ADDON, data) and not re.search(SutConfig.Pxe.PXE_PORT_ONBOARD, data):
        stylelog.fail('PXE启动网卡不进行选择，启动项中没有外插网卡，也没有板载网卡')
        wrong_msg.append('PXE启动网卡不进行选择，启动项中没有外插网卡，也没有板载网卡')
        count += 1
    else:
        return
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def pxe_boot_priority(oem):
    count = 0
    wrong_msg = []
    if oem is True:
        BmcLib.change_bios_value(['BootMode:UEFI','IPVersion:IPv4','PXEPriority:Onboard','PXE:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_ONBOARD_PRI, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    data = ''.join(re.findall('UEFI .*?: Port \d .*?IPv4', data))
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, data)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, data)
    pxe_order = SetUpLib.regex_char_handle(''.join(onboard)) + '.*' + SetUpLib.regex_char_handle(''.join(addon))
    if re.search(pxe_order, data):
        logging.info('修改PXE优先级板载优先，启动项中板载优先')
    elif re.search(SetUpLib.regex_char_handle(''.join(addon)) + '.*' + SetUpLib.regex_char_handle(''.join(onboard)), data):
        stylelog.fail('修改PXE优先级板载优先，启动项中外插优先')
        wrong_msg.append('修改PXE优先级板载优先，启动项中外插优先')
        count += 1
    else:
        stylelog.fail('修改PXE优先级板载优先，启动项中既不是板载优先，也不是外插优先')
        stylelog.fail('启动顺序为{0}'.format(data))
        wrong_msg.append('修改PXE优先级板载优先，启动项中既不是板载优先，也不是外插优先')
        wrong_msg.append('启动顺序为{0}'.format(data))
        count += 1
    if oem is True:
        BmcLib.change_bios_value(['PXEPriority:Addon'])
    else:
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_ADDON_PRI, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    data = ''.join(re.findall('UEFI .*?: Port \d .*?IPv4', data))
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, data)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, data)
    pxe_order = SetUpLib.regex_char_handle(''.join(addon)) + '.*' + SetUpLib.regex_char_handle(''.join(onboard))
    if re.search(pxe_order, data):
        logging.info('修改PXE优先级外插优先，启动项中外插优先')
    elif re.search(SetUpLib.regex_char_handle(''.join(onboard)) + '.*' + SetUpLib.regex_char_handle(''.join(addon)), data):
        stylelog.fail('修改PXE优先级外插优先，启动项中板载优先')
        wrong_msg.append('修改PXE优先级外插优先，启动项中板载优先')
        count += 1
    else:
        stylelog.fail('修改PXE优先级外插优先，启动项中既不是外插优先，也不是板载优先')
        stylelog.fail('启动顺序为{0}'.format(data))
        wrong_msg.append('修改PXE优先级外插优先，启动项中既不是外插优先，也不是板载优先')
        wrong_msg.append('启动顺序为{0}'.format(data))
        count += 1
    if oem is True:
        BmcLib.change_bios_value(['PXEPriority:Disabled'])
    else:
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_ADDON_NONE, 18, save=True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def higest_boot_priority():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                            SutConfig.Pxe.SET_ONBOARD_PRI + SutConfig.Pxe.CLOSE_HIGHEST_DEVICE, 18,
                                            save=True)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_BOOT, SutConfig.Msg.PXE_BOOT_NAME], 18)
    all_pxe_device = SetUpLib.get_value_list()
    if not re.search(SutConfig.Pxe.HIGHEST_DEVICE, ''.join(all_pxe_device)):
        logging.info('没有支持测试的设备')
        return 2
    if re.search(SutConfig.Pxe.HIGHEST_DEVICE, all_pxe_device[0]):
        stylelog.fail('PXE启动优先级为板载优先，PXE第一启动项不是板载网卡')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.OPEN_HIGHEST_DEVICE, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    pxe_boot_name = ''.join(re.findall('UEFI .*?: Port \d .*?IPv4', data))
    highest = re.findall(SutConfig.Pxe.HIGHEST_DEVICE, data)
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, data)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, data)
    boot_order = ''.join(highest + onboard) if addon == highest else ''.join(highest + onboard + addon)
    if re.search(SetUpLib.regex_char_handle(boot_order), pxe_boot_name):
        logging.info('高启动优先级设备打开，PXE启动优先级为板载优先，启动菜单启动顺序为高启动优先级设备->板载网卡->外插网卡')
    else:
        stylelog.fail('高启动优先级设备打开，PXE启动优先级为板载优先，启动菜单启动顺序不是高启动优先级设备->板载网卡->外插网卡')
        stylelog.fail(pxe_boot_name)
        return
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_BOOT, SutConfig.Msg.PXE_BOOT_NAME], 18)
    pxe_boot_name = ''.join(SetUpLib.get_value_list())
    highest = re.findall(SutConfig.Pxe.HIGHEST_DEVICE, pxe_boot_name)
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, pxe_boot_name)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, pxe_boot_name)
    boot_order = ''.join(highest + onboard) if addon == highest else ''.join(highest + onboard + addon)
    if re.search(SetUpLib.regex_char_handle(boot_order), pxe_boot_name):
        logging.info('高启动优先级设备打开，PXE启动优先级为板载优先，SetUp启动顺序为高启动优先级设备->板载网卡->外插网卡')
    else:
        stylelog.fail('高启动优先级设备打开，PXE启动优先级为板载优先，SetUp启动顺序不是高启动优先级设备->板载网卡->外插网卡')
        stylelog.fail(pxe_boot_name)
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.CLOSE_HIGHEST_DEVICE, 18, save=True)
    data = SetUpLib.boot_to_boot_menu(True)
    pxe_boot_name = ''.join(re.findall('UEFI .*?: Port \d .*?IPv4', data))
    highest = re.findall(SutConfig.Pxe.HIGHEST_DEVICE, data)
    addon = re.findall(SutConfig.Pxe.PXE_PORT_ADDON, data)
    onboard = re.findall(SutConfig.Pxe.PXE_PORT_ONBOARD, data)
    boot_order = ''.join(onboard + highest) if highest == addon else ''.join(onboard + highest + addon)
    if re.search(SetUpLib.regex_char_handle(boot_order), pxe_boot_name):
        logging.info('高启动优先级设备关闭，PXE启动优先级为板载优先，启动菜单启动顺序为板载网卡->外插网卡')
    else:
        stylelog.fail('高启动优先级设备关闭，PXE启动优先级为板载优先，启动菜单启动顺序不是板载网卡->外插网卡')
        stylelog.fail(pxe_boot_name)
        return
    return True
