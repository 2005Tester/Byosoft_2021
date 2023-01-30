# -*- encoding=utf8 -*-
from ByoTool.Config import *
from ByoTool.BaseLib import *


def is_uefi_not_retry(delay=150):
    """
    判断轮询完所有网口是否继续轮询
    """
    datas = ''
    start = time.time()
    while True:
        data = SetUpLib.get_data(2, cleanup=False)
        datas += data
        if re.search(SutConfig.Pxe.UEFI_USB_MSG, Sut.BIOS_COM.cleanup_data(datas)):
            break
        end = time.time()
        if end - start > delay:
            break
    if not re.search(SutConfig.Pxe.PXE_START_MSG, Sut.BIOS_COM.cleanup_data(datas)):
        logging.info('不再进行网络重试')
        return True
    else:
        stylelog.fail('仍进行网络重试')
        return


def is_legacy_not_retry(delay=150):
    """
    判断轮询完所有网口是否继续轮询
    """
    datas = ''
    start = time.time()
    while True:
        data = SetUpLib.get_data(2, cleanup=False)
        datas += data
        if re.search(SutConfig.Pxe.LEGACY_USB_MSG, Sut.BIOS_COM.cleanup_data(datas)):
            break
        end = time.time()
        if end - start > delay:
            break
    print(Sut.BIOS_COM.cleanup_data(datas))
    if not re.search(SutConfig.Pxe.LEGACY_PXE_START_MSG, Sut.BIOS_COM.cleanup_data(datas)):
        logging.info('不再进行网络重试')
        return True
    else:
        stylelog.fail('仍进行网络重试')
        return


def set_pxe_first():
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Pxe.LOC_PXE, 18)
    for i in range(6):
        SetUpLib.send_key(Key.ADD)
        time.sleep(1)
    return True


def set_usb_first():
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Pxe.LOC_USB, 18)
    for i in range(6):
        SetUpLib.send_key(Key.ADD)
        time.sleep(1)
    return True


@core.test_case(('5401', '[TC5401]UEFI模式网络重试0次', 'UEFI模式网络重试0次'))
def pxe_retry_01():
    """
    Name:   UEFI模式网络重试0次

    Steps:  1.启动模式设为”UEFI“,将网络引导设为“打开”,网络重试次数设为“0”,U盘调为第一启动项
            2.F12快捷键进行网络启动
            3.网络启动调成为第一启动项，开机POST倒计时不按快捷键自动启动
            4.启动菜单选择网络启动项启动
            5.启动管理器选择网络启动项启动


    Result: 2.网络启动只会轮询一次所有的网口,之后启动到U盘
            3.网络启动只会轮询一次所有的网口,之后启动到U盘
            4.网络启动失败退出到设备启动菜单
            5.网络启动失败退出到Setup启动管理器里
    """
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_UEFI + SutConfig.Pxe.SET_PXE_0, 18)
        assert set_usb_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.info('--------------F12网络启动----------------------------')
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.PXE_START_MSG, 150,
                                         SutConfig.Msg.POST_MESSAGE), 'F12进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        assert is_uefi_not_retry(), '关闭网络重试，仍进行网络重试'
        logging.info('---------------PXE第一启动项网络启动-------------------')
        assert SetUpLib.boot_to_setup()
        assert set_pxe_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 60), 'PXE第一启动项进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        assert is_uefi_not_retry(), '关闭网络重试，仍进行网络重试'
        logging.info('----------------启动菜单网络启动-----------------------')
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.PXE_BOOT_NAME1, 30,
                                           SutConfig.Pxe.PXE_BOOT_NAME1), '进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 150), '网络启动失败没有退回启动菜单'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.PXE_BOOT_NAME2, 30,
                                           SutConfig.Pxe.PXE_BOOT_NAME2), '进入网络启动'
        assert SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 150), '网络启动失败没有退回启动菜单'
        logging.info('----------------启动管理器网络启动-----------------------')
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Pxe.LOC_BOOT_MANAGER + [SutConfig.Pxe.PXE_BOOT_NAME1], 18)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_BOOT_NAME1, 60), '启动管理器进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.BOOT_MANAGER_MSG, 150), '网络启动失败没有退回启动管理器'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Pxe.PXE_BOOT_NAME2], 18)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_BOOT_NAME2, 60), '启动管理器进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.BOOT_MANAGER_MSG, 150), '网络启动失败没有退回启动管理器'
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('5402', '[TC5402]UEFI模式网络重试n次', 'UEFI模式网络重试n次'))
def pxe_retry_02():
    """
    Name:   UEFI模式网络重试n次

    Steps:  1.启动模式设为”UEFI“,将网络引导设为“打开”,网络重试次数设为n,U盘调为第一启动项
            2.F12快捷键进行网络启动
            3.网络启动调成为第一启动项，开机POST倒计时不按快捷键自动启动
            4.启动菜单选择网络启动项启动
            5.启动管理器选择网络启动项启动


    Result: 2.网络启动启动时会轮询n+1所有的网口,之后启动到U盘
            3.网络启动启动时会轮询n+1所有的网口,之后启动到U盘
            4.网络启动启动时会轮询n+1所有的网口,之后退出到设备启动菜单
            5.网络启动启动时会轮询n+1所有的网口,之后退出到Setup启动管理器里
    """

    try:
        retry_count = list(SutConfig.Pxe.SET_PXE_N[-1].values())[0]
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_UEFI + SutConfig.Pxe.SET_PXE_N, 18)
        assert set_usb_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.info('--------------F12网络启动----------------------------')
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.PXE_START_MSG, 150,
                                         SutConfig.Msg.POST_MESSAGE), 'F12进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert is_uefi_not_retry(), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        logging.info('---------------PXE第一启动项网络启动-------------------')
        assert SetUpLib.boot_to_setup()
        assert set_pxe_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 60), 'PXE第一启动项进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert is_uefi_not_retry(), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        logging.info('----------------启动菜单网络启动-----------------------')
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.PXE_BOOT_NAME1, 30,
                                           SutConfig.Pxe.PXE_BOOT_NAME1), '进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        # assert not SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 90), f'网络重试{retry_count}次后，仍进行网络重试'
        assert SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 150), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        logging.info('----------------启动管理器网络启动-----------------------')
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Pxe.LOC_BOOT_MANAGER + [SutConfig.Pxe.PXE_BOOT_NAME1], 18)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_BOOT_NAME1, 60), '启动管理器进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        # assert not SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 90), f'网络重试{retry_count}次后，仍进行网络重试'
        assert SetUpLib.wait_message(SutConfig.Pxe.BOOT_MANAGER_MSG, 150), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('5403', '[TC5403]UEFI模式网络重试无限次', 'UEFI模式网络重试无限次'))
def pxe_retry_03():
    """
    Name:   UEFI模式网络重试无限次

    Steps:  1.启动模式设为”UEFI“,将网络引导设为“打开”,网络重试次数设为“255”
            2.F12快捷键进行网络启动
            3.网络启动调成为第一启动项，开机POST倒计时不按快捷键自动启动
            4.启动菜单选择网络启动项启动
            5.启动管理器选择网络启动项启动


    Result: 2.网络启动启动时会一直轮询所有的网口
            3.网络启动启动时会一直轮询所有的网口
            4.网络启动启动时会一直轮询所有的网口
            5.网络启动启动时会一直轮询所有的网口
    """
    try:
        retry_count = 3
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_UEFI + SutConfig.Pxe.SET_PXE_MAX, 18,
                                                save=True)
        logging.info('--------------F12网络启动----------------------------')
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Pxe.PXE_START_MSG, 150,
                                         SutConfig.Msg.POST_MESSAGE), 'F12进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再重试'
        logging.info(f'不断网络重试')
        logging.info('---------------PXE第一启动项网络启动-------------------')
        assert SetUpLib.boot_to_setup()
        assert set_pxe_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 60), 'PXE第一启动项进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再重试'
        logging.info(f'不断网络重试')
        logging.info('----------------启动菜单网络启动-----------------------')
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.PXE_BOOT_NAME1, 30,
                                           SutConfig.Pxe.PXE_BOOT_NAME1), '进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再重试'
        logging.info(f'不断网络重试')
        logging.info('----------------启动管理器网络启动-----------------------')
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Pxe.LOC_BOOT_MANAGER + [SutConfig.Pxe.PXE_BOOT_NAME1], 18)
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_BOOT_NAME1, 60), '启动管理器进入网络启动失败'
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), '没有轮询一次所有的网口'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.PXE_END_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再重试'
        logging.info(f'不断网络重试')
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('5404', '[TC5404]Legacy模式网络重试0次', 'Leagacy模式网络重试0次'))
def pxe_retry_04():
    """
    Name:   Legacy模式网络重试0次

    Steps:  1.启动模式设为”Legacy“,将网络引导设为“打开”,网络重试次数设为“0”,U盘调为第一启动项
            2.F12快捷键进行网络启动
            3.网络启动调成为第一启动项，开机POST倒计时不按快捷键自动启动
            4.启动菜单选择网络启动项启动
            5.启动管理器选择网络启动项启动


    Result: 2.网络启动只会轮询一次所有的网口,之后启动到U盘
            3.网络启动只会轮询一次所有的网口,之后启动到U盘
            4.网络启动失败后启动到U盘
            5.网络启动失败后启动到U盘
    """
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_LEGACY + SutConfig.Pxe.SET_PXE_0, 18)
        assert set_usb_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.info('--------------F12网络启动----------------------------')
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        SetUpLib.send_key(Key.F12)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60)
        assert is_legacy_not_retry(), '关闭网络重试，仍进行网络重试'
        logging.info('---------------PXE第一启动项网络启动-------------------')
        assert SetUpLib.boot_to_setup()
        assert set_pxe_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60), 'PXE第一启动项进入网络启动失败'
        assert is_legacy_not_retry(), '关闭网络重试，仍进行网络重试'
        logging.info('----------------启动菜单网络启动-----------------------')
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.LEGACY_PXE_BOOT_NAME1, 30,
                                           SutConfig.Pxe.LEGACY_PXE_START_MSG), '进入网络启动失败'
        assert is_legacy_not_retry(), '关闭网络重试，仍进行网络重试'

        logging.info('----------------启动管理器网络启动-----------------------')
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Pxe.LOC_BOOT_MANAGER + [SutConfig.Pxe.LEGACY_PXE_BOOT_NAME1],
                                                18)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60), '启动管理器进入网络启动失败'
        assert is_legacy_not_retry(), '关闭网络重试，仍进行网络重试'
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('5405', '[TC5405]Legacy模式网络重试n次', 'Legacy模式网络重试n次'))
def pxe_retry_05():
    """
    Name:   Legacy模式网络重试n次

    Steps:  1.启动模式设为”Legacy“,将网络引导设为“打开”,网络重试次数设为n,U盘调为第一启动项
            2.F12快捷键进行网络启动
            3.网络启动调成为第一启动项，开机POST倒计时不按快捷键自动启动
            4.启动菜单选择网络启动项启动
            5.启动管理器选择网络启动项启动


    Result: 2.网络启动启动时会轮询n+1所有的网口,之后启动到U盘
            3.网络启动启动时会轮询n+1所有的网口,之后启动到U盘
            4.网络启动启动时会轮询n+1所有的网口,之后启动到U盘
            5.网络启动启动时会轮询n+1所有的网口,之后启动到U盘
    """
    try:
        retry_count = list(SutConfig.Pxe.SET_PXE_N[-1].values())[0]
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_LEGACY + SutConfig.Pxe.SET_PXE_N, 18)
        assert set_usb_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.info('--------------F12网络启动----------------------------')
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        SetUpLib.send_key(Key.F12)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60)
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert is_legacy_not_retry(), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        logging.info('---------------PXE第一启动项网络启动-------------------')
        assert SetUpLib.boot_to_setup()
        assert set_pxe_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60), 'PXE第一启动项进入网络启动失败'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert is_legacy_not_retry(), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        logging.info('----------------启动菜单网络启动-----------------------')
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.LEGACY_PXE_BOOT_NAME1, 30,
                                           SutConfig.Pxe.LEGACY_PXE_START_MSG), '进入网络启动失败'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert is_legacy_not_retry(), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        logging.info('----------------启动管理器网络启动-----------------------')
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Pxe.LOC_BOOT_MANAGER + [SutConfig.Pxe.LEGACY_PXE_BOOT_NAME1],
                                                18)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60), '启动管理器进入网络启动失败'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert is_legacy_not_retry(), f'网络重试{retry_count}次后，仍进行网络重试'
        logging.info(f'网络重试{retry_count}次后，不网络重试')
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('5406', '[TC5406]Legacy模式网络重试无限次', 'Legacy模式网络重试无限次'))
def pxe_retry_06():
    """
    Name:   Legacy模式网络重试无限次

    Steps:  1.启动模式设为”UEFI“,将网络引导设为“打开”,网络重试次数设为“255”
            2.F12快捷键进行网络启动
            3.网络启动调成为第一启动项，开机POST倒计时不按快捷键自动启动
            4.启动菜单选择网络启动项启动
            5.启动管理器选择网络启动项启动


    Result: 2.网络启动启动时会一直轮询所有的网口
            3.网络启动启动时会一直轮询所有的网口
            4.网络启动启动时会一直轮询所有的网口
            5.网络启动启动时会一直轮询所有的网口
    """
    try:
        retry_count = 3
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_LEGACY + SutConfig.Pxe.SET_PXE_MAX, 18)
        assert set_usb_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.info('--------------F12网络启动----------------------------')
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        SetUpLib.send_key(Key.F12)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60)
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再网络重试'
        logging.info(f'不断网络重试')
        logging.info('---------------PXE第一启动项网络启动-------------------')
        assert SetUpLib.boot_to_setup()
        assert set_pxe_first()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 60), 'PXE第一启动项进入网络启动失败'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再网络重试'
        logging.info(f'不断网络重试')
        logging.info('----------------启动菜单网络启动-----------------------')
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Pxe.LEGACY_PXE_BOOT_NAME1, 30,
                                           SutConfig.Pxe.LEGACY_PXE_START_MSG), '进入网络启动失败'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再网络重试'
        logging.info(f'不断网络重试')
        logging.info('----------------启动管理器网络启动-----------------------')
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Pxe.LOC_BOOT_MANAGER + [SutConfig.Pxe.LEGACY_PXE_BOOT_NAME1],
                                                18)
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 90), '启动管理器进入网络启动失败'
        for i in range(retry_count):
            assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG), f'第{i + 1}次网络重试失败'
            logging.info(f'第{i + 1}次网络重试')
        assert SetUpLib.wait_message(SutConfig.Pxe.LEGACY_PXE_START_MSG, 150), f'网络重试{retry_count}次后，不再网络重试'
        logging.info(f'不断网络重试')
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail
