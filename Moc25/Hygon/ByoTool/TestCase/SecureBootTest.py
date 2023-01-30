# -*- encoding=utf8 -*-
from ByoTool.Config import *
from ByoTool.BaseLib import *


def boot_to_internal_shell(key=SutConfig.Msg.BOOTMENU_KEY):
    assert SetUpLib.boot_to_setup()
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if not SetUpLib.boot_with_hotkey(key, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
        return
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30, 'UEFI Interactive Shell'):
        return
    else:
        logging.info('Shell Boot Successed.')
        time.sleep(10)
        return True


def _update_bios_all():
    assert SetUpLib.boot_to_windows_os()
    output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL)
    logging.debug(output)
    if re.search(SutConfig.Tool.WINDOWS_MSG_ALL, output[0]):
        logging.info('WINDOWS下BIOS更新成功')
    else:
        stylelog.fail('WINDOWS下更新可能失败')
    SetUpLib.reboot()
    time.sleep(200)
    # assert boot_to_linux_os()
    # linux_mount_usb()
    # output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL)
    # logging.debug(output)
    # if re.search(SutConfig.Tool.LINUX_MSG_ALL, output[0]):
    #     logging.info('LINUX下BIOS更新成功')
    # else:
    #     stylelog.fail('LINUX下更新可能失败')
    # SetUpLib.reboot()
    # time.sleep(200)
    return True


def _update_bios_normal():
    assert SetUpLib.boot_to_windows_os()
    output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST)
    logging.debug(output)
    if re.search(SutConfig.Tool.WINDOWS_MSG_NOR, output[0]):
        logging.info('WINDOWS下BIOS更新成功')
    else:
        stylelog.fail('WINDOWS下更新可能失败')
    SetUpLib.reboot()
    time.sleep(10)
    # assert boot_to_linux_os()
    # linux_mount_usb()
    # output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST)
    # logging.debug(output)
    # if re.search(SutConfig.Tool.LINUX_MSG_NOR, output[0]):
    #     logging.info('LINUX下BIOS更新成功')
    # else:
    #     stylelog.fail('LINUX下更新可能失败')
    # SetUpLib.reboot()
    # time.sleep(10)
    return True


def _is_key_none():
    count = 0
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
    if not SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
        logging.info('PK Key 为空')
    else:
        stylelog.fail('PK Key 不为空')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    assert \
        SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEK, 'Delete KEK'], 8)
    if not SetUpLib.wait_message('\[.*\]', 5):
        logging.info('KEK Key 为空')
    else:
        stylelog.fail('KEK Key 不为空')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DB, 'Delete Signature'], 8)
    if not SetUpLib.wait_message('\[.*\]', 5):
        logging.info('DB Key 为空')
    else:
        stylelog.fail('DB Key 不为空')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DBX, 'Delete Signature'], 8)
    if not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3):
        logging.info('DBX Key 为空')
    else:
        stylelog.fail('DBX Key 不为空')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DBT, 'Delete Signature'], 8)
    if not SetUpLib.wait_message('\[.*\]', 5):
        logging.info('DBT Key 为空')
    else:
        stylelog.fail('DBT Key 不为空')
        count += 1
    if count == 0:
        return True
    else:
        return


def _is_key():
    count = 0
    if SetUpLib.locate_menu(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Delete Pk'], 10):
        logging.info('PK Key 导入')
        time.sleep(3)
    else:
        stylelog.fail('PK Key 没有导入')
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(5)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEK, 'Delete KEK'], 8)
    if SetUpLib.wait_message('\[.*\]', 5):
        logging.info('KEK Key 导入')
    else:
        stylelog.fail('KEK Key 没有导入')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DB, 'Delete Signature'], 8)
    if SetUpLib.wait_message('\[.*\]', 5):
        logging.info('DB Key 导入')
    else:
        stylelog.fail('DB Key 没有导入')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                            [SutConfig.Sec.DBX, 'Delete Signature', 'Signature List, Entry-1'], 8)
    if SetUpLib.wait_message('\[.*\]', 5):
        logging.info('DBX Key 导入')
    else:
        stylelog.fail('DBX Key 没有导入')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if count == 0:
        return True
    else:
        return


def _is_pk_none():
    count = 0
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
    if not SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
        logging.info('PK Key 为空')
    else:
        stylelog.fail('PK Key 不为空')
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(5)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEK, 'Delete KEK'], 8)
    if SetUpLib.wait_message('\[.*\]', 5):
        logging.info('KEK Key 导入')
    else:
        stylelog.fail('KEK Key 没有导入')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DB, 'Delete Signature'], 8)
    if SetUpLib.wait_message('\[.*\]', 5):
        logging.info('DB Key 导入')
    else:
        stylelog.fail('DB Key 没有导入')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                            [SutConfig.Sec.DBX, 'Delete Signature', 'Signature List, Entry-1'], 8)
    if SetUpLib.wait_message('\[.*\]', 5):
        logging.info('DBX Key 导入')
    else:
        stylelog.fail('DBX Key 没有导入')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if count == 0:
        return True
    else:
        return


def _boot_except_usb():
    count = 0
    if SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 30, SutConfig.Sec.WARNING):
        logging.info('无法进入U盘的Shell')
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        stylelog.fail('可以进入U盘的Shell')
        count += 1
        assert SetUpLib.boot_to_boot_menu()
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30, 'UEFI Interactive Shell'):
        stylelog.fail('进入内置Shell失败')
        assert SetUpLib.boot_to_boot_menu()
        count += 1
    else:
        logging.info('成功进入内置Shell')
        time.sleep(10)
        SetUpLib.send_data_enter('exit')
        time.sleep(2)
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
        return
    else:
        if BmcLib.ping_sut():
            time.sleep(30)
            SetUpLib.reboot()
            logging.info("成功进入Linux系统")
            time.sleep(10)
        else:
            stylelog.fail('进入Linux系统失败')
            count += 1
    if count == 0:
        return True
    else:
        return


def _boot_all():
    count = 0
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 30, 'UEFI Interactive Shell'):
        stylelog.fail('进入U盘Shell失败')
        assert SetUpLib.boot_to_boot_menu()
        count += 1
    else:
        logging.info('成功进入U盘Shell')
        time.sleep(10)
        SetUpLib.send_data_enter('exit')
        time.sleep(2)
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30, 'UEFI Interactive Shell'):
        stylelog.fail('进入内置Shell失败')
        assert SetUpLib.boot_to_boot_menu()
        count += 1
    else:
        logging.info('成功进入内置Shell')
        time.sleep(10)
        SetUpLib.send_data_enter('exit')
        time.sleep(2)
    if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
        return
    else:
        if BmcLib.ping_sut():
            time.sleep(30)
            SetUpLib.reboot()
            time.sleep(10)
            logging.info("成功进入Linux系统")
        else:
            stylelog.fail('进入Linux系统失败')
            count += 1
    if count == 0:
        return True
    else:
        return


def _confirm_setup_mode():
    SetUpLib.boot_to_setup()
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
    time.sleep(1)
    SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)


def _confirm_user_mode():
    SetUpLib.boot_to_setup()
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
    time.sleep(1)
    SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    SetUpLib.locate_option(Key.DOWN, ['Exit Deployed Mode'], 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)


def _confirm_deployed_mode():
    SetUpLib.boot_to_setup()
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
    time.sleep(1)
    SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)


def _confirm_audit_mode():
    SetUpLib.boot_to_setup()
    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
    time.sleep(1)
    SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(5)
    SetUpLib.locate_option(Key.DOWN, ['Exit Deployed Mode'], 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.AUDIT_MODE], 10)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(3)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)


def boot_setup_set_uefi():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.SET_UEFI, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True


@core.test_case(('3001', '[TC3001]默认设定模式测试', '默认设定模式测试'))
def secure_boot_3001():
    """
    Name:   默认设定模式测试

    Steps:  1.全刷BIOS
            2.检查安全启动页面
            3.进入OS,内置Shell,U盘Shell

    Result: 2.安全启动显示关闭，系统模式显示为设定模式，“恢复出厂模式”“重置为设定模式”“进入审计模式”"进入部署模式"显示，且所有的key选项里面都是空值
            3.成功进入OS,内置Shell,U盘Shell
    """
    try:
        count = 0
        _update_bios_all()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('全刷BIOS后,安全启动关闭，安全启动模式为设定模式，恢复出厂模式，重置为设定模式，进入审计模式，进入部署模式显示')
        else:
            stylelog.fail('全刷BIOS后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_all() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3002', '[TC3002]设定模式恢复出厂模式', '设定模式恢复出厂模式'))
def secure_boot_3002():
    """
    Name:   设定模式恢复出厂模式

    Steps:  1.全刷BIOS
            2.恢复出厂模式，检查安全启动页面
            3.进入OS,内置Shell,U盘Shell

    Result: 2.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            3.成功进入OS,内置Shell，不能进入U盘Shell

    """
    try:
        count = 0
        assert _update_bios_all()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESTORE_FACTORY, 10)
        if SetUpLib.wait_message(SutConfig.Sec.RESTORE_MSG, 2):
            SetUpLib.send_key(Key.Y)
        else:
            return
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('恢复出厂模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('恢复出厂模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3003', '[TC3003]设定模式进入部署模式', '设定模式进入部署模式'))
def secure_boot_3003():
    """
    Name:   设定模式进入部署模式
    Condition:  设定模式

    Steps:  1.进入部署模式，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell，不能进入U盘Shell

    """
    try:
        count = 0
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DEPLOYED_MODE], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('进入部署模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('进入部署模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('进入部署模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('进入部署模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)

        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3004', '[TC3004]设定模式进入审计模式', '设定模式进入审计模式'))
def secure_boot_3004():
    """
    Name:   设定模式进入审计模式
    Condition:  设定模式

    Steps:  1.进入审计模式，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示关闭，系统模式显示为审计模式，“恢复出厂模式”“进入审计模式”"进入部署模式"显示，"重置为设定模式"为灰显，且所有的key选项都为空
            2.成功进入OS,内置Shell,U盘Shell
    """
    try:
        count = 0
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.AUDIT_MODE], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Audit Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('进入审计模式，安全启动显示关闭，系统模式显示审计模式,恢复出厂模式，重置为设定模式，进入审计模式，进入部署显示')
        else:
            stylelog.fail('进入审计模式后显示有误')
            stylelog.fail(data)
            count += 1
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10):
            logging.info('重置为设定模式灰显')
        else:
            stylelog.fail('重置为设定模式没有灰显')
            count += 1
        if _is_key_none():
            logging.info('Key全为空')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Audit Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('进入审计模式，安全启动显示关闭，系统模式显示审计模式,恢复出厂模式，重置为设定模式，进入审计模式，进入部署显示')
        else:
            stylelog.fail('进入审计模式后显示有误')
            stylelog.fail(data)
            count += 1
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10):
            logging.info('重置为设定模式灰显')
        else:
            stylelog.fail('重置为设定模式没有灰显')
            count += 1
        if _is_key_none():
            logging.info('Key全为空')
        else:
            count += 1
        time.sleep(2)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_all() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3005', '[TC3005]设定模式打开安全启动', '设定模式打开安全启动'))
def secure_boot_3005():
    """
    Name:   设定模式打开安全启动
    Condition:  设定模式

    Steps:  1.设定模式下打开安全启动，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell,不能进入U盘Shell
    """
    try:
        count = 0
        _confirm_setup_mode()
        assert _update_bios_all()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_SECURE_BOOT, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('设定模式下打开安全启动，系统模式显示部署模式，恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('设定模式下打开安全启动，显示错误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(3)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3006', '[TC3006]设定模式SetUp下恢复默认值', '设定模式SetUp下恢复默认值'))
def secure_boot_3006():
    """
    Name:   设定模式SetUp下恢复默认值
    Condition:  设定模式

    Steps:  1.开机，进setup，按F9
            2.检查安全启动页面
            3.退出，重启进入OS

    Result: 2.退出，重启进入UEFI系统
            3.成功进入OS
    """
    try:
        count = 0
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('F9恢复默认值，安全启动模式仍为设置模式')
        else:
            stylelog.fail('F9恢复默认值，安全启动模式改变')
            stylelog.fail(data)
            count += 1
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        time.sleep(3)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3007', '[TC3007]设定模式打开CSM后打开安全启动', '设定模式打开CSM后打开安全启动'))
def secure_boot_3007():
    """
    Name:   设定模式打开CSM后打开安全启动
    Condition:  设定模式

    Steps:  1.SetUp打开CSM
            2.保存重启,检查安全启动页面
            3.打开安全启动选项
            4.检查CSM

    Result: 4.CSM自动关闭
    """
    try:
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_CSM, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_SECURE_BOOT, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(2)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Sec.CSM_CLOSE_MSG, 3):
            logging.info('打开安全启动CSM自动关闭')
            return True
        else:
            stylelog.fail('打开安全启动CSM没有自动关闭')
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        boot_setup_set_uefi()


@core.test_case(('3008', '[TC3008]设定模式打开CSM后进入部署模式', '设定模式打开CSM后进入部署模式'))
def secure_boot_3008():
    """
    Name:   设定模式打开CSM后进入部署模式
    Condition:  设定模式

    Steps:  1.SetUp打开CSM
            2.保存重启，安全启动页面进入部署模式
            3.检查CSM

    Result: 3.CSM自动关闭

    """
    try:
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_CSM, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DEPLOYED_MODE], 10)
        time.sleep(1)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(2)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Sec.CSM_CLOSE_MSG, 3):
            logging.info('进入部署模式CSM自动关闭')
            return True
        else:
            stylelog.fail('进入部署模式CSM没有自动关闭')
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        boot_setup_set_uefi()


@core.test_case(('3101', '[TC3101]用户模式下关闭安全启动', '用户模式下关闭安全启动'))
def secure_boot_3101():
    """
    Name:   用户模式下关闭安全启动
    Condition:  用户模式

    Steps:  1.关闭安全启动，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示关闭，系统模式显示为设定模式，PK证书已删除，其他的key仍然存在
            2.成功进入OS,内置Shell,U盘Shell
    """
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.CLOSE_SECURE_BOOT, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()

        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('用户模式关闭安全启动，系统模式显示为设定模式')
        else:
            stylelog.fail('用户模式关闭安全启动，显示有误')
            stylelog.fail(data)
            count += 1
        if _is_pk_none() == True:
            logging.info('用户模式关闭安全启动，PK证书删除，其他Key仍存在')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('用户模式关闭安全启动，系统模式显示为设定模式')
        else:
            stylelog.fail('用户模式关闭安全启动，显示有误')
            stylelog.fail(data)
            count += 1
        if _is_pk_none() == True:
            logging.info('用户模式关闭安全启动，PK证书删除，其他Key仍存在')
        else:
            count += 1
        assert SetUpLib.boot_to_boot_menu()
        if _boot_all() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3102', '[TC3102]用户模式恢复出厂模式', '用户模式恢复出厂模式'))
def secure_boot_3102():
    """
    Name:   用户模式恢复出厂模式
    Condition:  用户模式

    Steps:  1.恢复出厂模式,检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell,不能进入U盘Shell
    """
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESTORE_FACTORY, 10)
        if SetUpLib.wait_message(SutConfig.Sec.RESTORE_MSG, 2):
            SetUpLib.send_key(Key.Y)
        else:
            return
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('恢复出厂模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('恢复出厂模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3103', '[TC3103]用户模式进入审计模式', '用户模式进入审计模式'))
def secure_boot_3103():
    """
    Name:   用户模式进入审计模式
    Condition:  用户模式

    Steps:  1.进入审计模式，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示关闭，系统模式显示为审计模式，“恢复出厂模式”“进入审计模式”"进入部署模式"显示，"重置为设定模式"为灰显，且PK证书已删除，其他的key仍然存在
            2.成功进入OS,内置Shell,U盘Shell
    """
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.AUDIT_MODE], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Audit Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('进入审计模式，安全启动显示关闭，系统模式显示审计模式,恢复出厂模式，重置为设定模式，进入审计模式，进入部署显示')
        else:
            stylelog.fail('进入审计模式后显示有误')
            stylelog.fail(data)
            count += 1
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10):
            logging.info('重置为设定模式灰显')
        else:
            stylelog.fail('重置为设定模式没有灰显')
            count += 1
        if _is_pk_none():
            logging.info('PK证书删除，其他Key仍存在')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Audit Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('进入审计模式，安全启动显示关闭，系统模式显示审计模式,恢复出厂模式，重置为设定模式，进入审计模式，进入部署显示')
        else:
            stylelog.fail('进入审计模式后显示有误')
            stylelog.fail(data)
            count += 1
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10):
            logging.info('重置为设定模式灰显')
        else:
            stylelog.fail('重置为设定模式没有灰显')
            count += 1
        if _is_pk_none():
            logging.info('PK证书删除，其他Key仍存在')
        else:
            count += 1
        time.sleep(2)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_all() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3104', '[TC3104]用户模式进入部署模式', '用户模式进入部署模式'))
def secure_boot_3104():
    """
    Name:   用户模式进入部署模式
    Condition:  用户模式

    Steps:  1.进入部署模式，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell,不能进入U盘Shell
    """
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DEPLOYED_MODE], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('进入部署模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('进入部署模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('进入部署模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('进入部署模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)

        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3105', '[TC3105]用户模式重置为设定模式', '用户模式重置为设定模式'))
def secure_boot_3105():
    """
    Name:   用户模式重置为设定模式
    Condition:  用户模式

    Steps:  1.重置为设置模式,检查安全启动页面
            2.重启检查安全启动页面

    Result: 1/2.启动模式显示为设定模式和安全启动状态显示关闭,所以的key已删除
    """

    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('用户模式重置为设定模式，启动模式显示设定模式，安全启动关闭')
        else:
            stylelog.fail('用户模式重置为设定模式显示有误')
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('用户模式重置为设定模式，启动模式显示设定模式，安全启动关闭')
        else:
            stylelog.fail('用户模式重置为设定模式显示有误')
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3106', '[TC3106]用户模式保留刷新BIOS', '用户模式保留刷新BIOS'))
def secure_boot_3106():
    """
    Name:   用户模式保留刷新BIOS
    Condition:  用户模式

    Steps:  1.保留刷新BIOS,检查安全启动页面
            2.进入OS

    Result: 1.安全启动模式没有改变，仍然为用户模式
            2.成功进入OS
    """
    try:
        count = 0
        _confirm_user_mode()
        _update_bios_normal()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *User Mode', data):
            logging.info('保留刷新后安全启动模式没有改变，仍为用户模式')
        else:
            stylelog.fail('保留刷新后安全启动模式改变')
            stylelog.fail(data)
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3107', '[TC3107]用户模式完全刷新BIOS', '用户模式完全刷新BIOS'))
def secure_boot_3107():
    """
    Name:   用户模式完全刷新BIOS
    Condition:  用户模式

    Steps:  1.全刷BIOS，检查安全启动页面
            2.进入OS

    Result: 1.安全启动模式恢复到默认设置模式和所有的证书已被删除
            2.成功进入OS

    """
    try:
        count = 0
        _confirm_user_mode()
        _update_bios_all()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('全刷BIOS后,安全启动关闭，安全启动模式为设定模式，恢复出厂模式，重置为设定模式，进入审计模式，进入部署模式显示')
        else:
            stylelog.fail('全刷BIOS后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return


    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3108', '[TC3108]用户模式恢复默认值', '用户模式恢复默认值'))
def secure_boot_3108():
    """
    Name:   用户模式恢复默认值
    Condition:  用户模式

    Steps:  1.开机，进setup，按F9
            2.检查安全启动页面
            3.进入OS

    Result: 2.安全启动模式没有改变，仍然为用户模式
            3.成功进入OS
    """
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *User Mode', data):
            logging.info('恢复默认值，安全启动模式没有改变')

        else:
            stylelog.fail('恢复默认值，安全启动模式改变')
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3109', '[TC3109]用户模式打开CSM', '用户模式打开CSM'))
def secure_boot_3109():
    """
    Name:   用户模式打开CSM
    Condition:  用户模式

    Steps:  1.SetUp下打开CSM
            2.检查安全启动页面

    Result: 2.安全启动开关自动关闭，系统模式显示为设定模式
    """
    try:
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_CSM, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('打开CSM,安全启动自动关闭，安全启动模式显示为设定模式')
            return True
        else:
            stylelog.fail('打开CSM,安全启动显示有误')
            stylelog.fail(data)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3201', '[TC3201]部署模式进入用户模式', '部署模式进入用户模式'))
def secure_boot_3201():
    """
    Name:   1.部署模式进入用户模式
    Condition:  部署模式

    Steps:  1.点击进入部署模式，再次点击退出部署模式
            2.检查安全启动页面
            3.进入OS,内置Shell,U盘Shell

    Result: 2.安全启动显示打开，系统模式显示为用户模式，“恢复出厂模式”“重置为设定模式”"进入审计模式""进入部署模式"显示，且所有的key选项都导入
            3.成功进入OS,内置Shell,不能进入U盘Shell
    """
    try:
        count = 0
        _confirm_deployed_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Exit Deployed Mode'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *User Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('部署模式进入用户模式，安全启动打开，安全启动模式为用户模式，恢复出厂模式，重置为设定模式，进入审计模式，进入部署模式显示')
        else:
            stylelog.fail('部署模式进入用户模式显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1

        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3202', '[TC3202]部署模式关闭安全启动', '部署模式关闭安全启动'))
def secure_boot_3202():
    """
    Name:   部署模式关闭安全启动
    Condition:  部署模式

    Steps:  1.关闭安全启动，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示关闭，系统模式显示为设定模式，PK证书已删除，其他的key仍然存在
            2.成功进入OS,内置Shell,U盘Shell

    """
    try:
        count = 0
        _confirm_deployed_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.CLOSE_SECURE_BOOT, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('部署模式关闭安全启动，系统模式显示为设定模式')
        else:
            stylelog.fail('部署模式关闭安全启动，显示有误')
            stylelog.fail(data)
            count += 1
        if _is_pk_none() == True:
            logging.info('部署模式关闭安全启动，PK证书删除，其他Key仍存在')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('部署模式关闭安全启动，系统模式显示为设定模式')
        else:
            stylelog.fail('部署模式关闭安全启动，显示有误')
            stylelog.fail(data)
            count += 1
        if _is_pk_none() == True:
            logging.info('部署模式关闭安全启动，PK证书删除，其他Key仍存在')
        else:
            count += 1
        assert SetUpLib.boot_to_boot_menu()
        if _boot_all() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3203', '[TC3203]部署模式重置为设定模式', '部署模式重置为设定模式'))
def secure_boot_3203():
    """
    Name:   部署模式重置为设定模式
    Condition:  部署模式

    Steps:  1.重置为设定模式，检查安全启动页面
            2.退出重启，检查安全启动页面

    Result: 1/2.启动模式显示为设定模式和安全启动状态显示关闭,所有的key已删除

    """
    try:
        count = 0
        _confirm_deployed_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('部署模式重置为设定模式，启动模式显示设定模式，安全启动关闭')
        else:
            stylelog.fail('部署模式重置为设定模式显示有误')
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('部署模式重置为设定模式，启动模式显示设定模式，安全启动关闭')
        else:
            stylelog.fail('部署模式重置为设定模式显示有误')
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3204', '[TC3204]部署模式保留刷新BIOS', '部署模式保留刷新BIOS'))
def secure_boot_3204():
    """
    Name:   部署模式保留刷新BIOS
    Condition:  部署模式

    Steps:  1.保留刷新BIOS，检查安全启动页面
            2.进入OS

    Result: 1.安全启动模式没有改变，仍然为部署模式
            2.成功进入OS
    """
    try:
        count = 0
        _confirm_deployed_mode()
        _update_bios_normal()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data):
            logging.info('保留刷新后安全启动模式没有改变，仍为部署模式')
        else:
            stylelog.fail('保留刷新后安全启动模式改变')
            stylelog.fail(data)
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3205', '[TC3205]部署模式完全刷新BIOS', '部署模式完全刷新BIOS'))
def secure_boot_3205():
    """
    Name:   部署模式完全刷新BIOS
    Condition:  部署模式

    Steps:  1.完全刷新BIOS,检查安全启动页面
            2.进入OS

    Result: 1.安全启动模式恢复到默认设置模式和所有的证书已被删除
            2.成功进入OS
    """
    try:
        count = 0
        _confirm_deployed_mode()
        _update_bios_all()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('全刷BIOS后,安全启动关闭，安全启动模式为设定模式，恢复出厂模式，重置为设定模式，进入审计模式，进入部署模式显示')
        else:
            stylelog.fail('全刷BIOS后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3206', '[TC3206]部署模式恢复默认值', '部署模式恢复默认值'))
def secure_boot_3206():
    """
    Name:   部署模式恢复默认值
    Condition:  部署模式

    Steps:  1.开机，进setup，按F9
            2.检查安全启动页面
            3.进入OS

    Result: 2.安全启动模式没有改变，仍然为部署模式
            3.成功进入OS
    """
    try:
        count = 0
        _confirm_deployed_mode()
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data):
            logging.info('恢复默认值，安全启动模式没有改变')

        else:
            stylelog.fail('恢复默认值，安全启动模式改变')
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3207', '[TC3207]部署模式打开CSM', '部署模式打开CSM'))
def secure_boot_3207():
    """
    Name:   部署模式打开CSM
    Condition:  部署模式

    Steps:  1.SetUp下打开CSM
            2.检查安全启动页面

    Result: 2..安全启动开关自动关闭，系统模式显示为设定模式
    """
    try:
        _confirm_deployed_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_CSM, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('打开CSM,安全启动自动关闭，安全启动模式显示为设定模式')
            return True
        else:
            stylelog.fail('打开CSM,安全启动显示有误')
            stylelog.fail(data)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3301', '[TC3301]审计模式进入部署模式', '审计模式进入部署模式'))
def secure_boot_3301():
    """
    Name:   审计模式进入部署模式
    Condition:  审计模式

    Steps:  1.进入部署模式检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell,不能进入U盘Shell
    """
    try:
        count = 0
        _confirm_audit_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DEPLOYED_MODE], 10)
        time.sleep(5)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('进入部署模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('进入部署模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('进入部署模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('进入部署模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)

        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3302', '[TC3302]审计模式恢复出厂模式', '审计模式恢复出厂模式'))
def secure_boot_3302():
    """
    Name:   审计模式恢复出厂模式
    Condition:  审计模式

    Steps:  1.恢复出厂模式,检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell,不能进入U盘Shell

    """
    try:
        count = 0
        _confirm_audit_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESTORE_FACTORY, 10)
        if SetUpLib.wait_message(SutConfig.Sec.RESTORE_MSG, 2):
            SetUpLib.send_key(Key.Y)
        else:
            return
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('恢复出厂模式，安全启动显示打开，系统模式显示部署模式,恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('恢复出厂模式后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3303', '[TC3303]审计模式打开安全启动', '审计模式打开安全启动'))
def secure_boot_3303():
    """
    Name:   审计模式打开安全启动
    Condition:  审计模式

    Steps:  1.打开安全启动，检查安全启动页面
            2.进入OS,内置Shell,U盘Shell

    Result: 1.安全启动显示打开，系统模式显示为部署模式，“恢复出厂模式”“重置为设定模式”"退出部署"显示，且所有的key选项都导入
            2.成功进入OS,内置Shell,不能进入U盘Shell
    """
    try:
        count = 0
        _confirm_audit_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_SECURE_BOOT, 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Deployed Mode', data) and re.search('<Enabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Exit Deployed Mode', data):
            logging.info('审计模式下打开安全启动，系统模式显示部署模式，恢复出厂模式，重置为设定模式，退出部署显示')
        else:
            stylelog.fail('审计安全启动，显示错误')
            stylelog.fail(data)
            count += 1
        if _is_key() == True:
            logging.info('Key全导入')
        else:
            count += 1
        time.sleep(3)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if _boot_except_usb() == True:
            pass
        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3304', '[TC3304]审计模式保留刷新BIOS', '审计模式保留刷新BIOS'))
def secure_boot_3304():
    """
    Name:   审计模式保留刷新BIOS
    Condition:  审计模式

    Steps:  1.保留刷新BIOS,检查安全启动页面
            2.进入OS

    Result: 1.安全启动模式没有改变，仍然为审计模式
            2.成功进入OS
    """
    try:
        count = 0
        _confirm_audit_mode()
        _update_bios_normal()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Audit Mode', data):
            logging.info('保留刷新后安全启动模式没有改变，仍为审计模式')
        else:
            stylelog.fail('保留刷新后安全启动模式改变')
            stylelog.fail(data)
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3305', '[TC3305]审计模式完全刷新BIOS', '审计模式完全刷新BIOS'))
def secure_boot_3305():
    """
    Name:   审计模式完全刷新BIOS
    Condition:  审计模式

    Steps:  1.完全刷新BIOS,检查安全启动页面
            2.进入OS

    Result: 1.安全启动模式恢复到默认设置模式
            2.成功进入OS
    """
    try:
        count = 0
        _confirm_audit_mode()
        _update_bios_all()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data) and re.search(
                'Restore Factory Keys', data) and re.search('Reset Platform to Setup Mode', data) and re.search(
            'Enter Audit Mode', data) and re.search('Enter Deployed Mode', data):
            logging.info('全刷BIOS后,安全启动关闭，安全启动模式为设定模式，恢复出厂模式，重置为设定模式，进入审计模式，进入部署模式显示')
        else:
            stylelog.fail('全刷BIOS后显示有误')
            stylelog.fail(data)
            count += 1
        if _is_key_none() == True:
            logging.info('Key全为空')
        else:
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3306', '[TC3306]审计模式恢复默认值', '审计模式恢复默认值'))
def secure_boot_3306():
    """
    Name:   1.审计模式恢复默认值
    Condition:  审计模式

    Steps:  1.开机，进setup，按F9
            2.检查安全启动页面
            3.进入OS

    Result: 2.安全启动模式没有改变，仍然为审计模式
            3.成功进入OS
    """
    try:
        count = 0
        _confirm_audit_mode()
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Audit Mode', data):
            logging.info('恢复默认值，安全启动模式没有改变')

        else:
            stylelog.fail('恢复默认值，安全启动模式改变')
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3307', '[TC3307]打开CSM后在审计模式下打开安全启动', '打开CSM后在审计模式下打开安全启动'))
def secure_boot_3307():
    """
    Name:   打开CSM后在审计模式下打开安全启动
    Condition:  审计模式

    Steps:  1.SetUp下打开CSM
            2.打开安全启动，检查CSM

    Result: 2.CSM会自动变成关闭
    """
    try:
        count = 0
        _confirm_audit_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_CSM, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_SECURE_BOOT, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(2)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Sec.CSM_CLOSE_MSG, 3):
            logging.info('打开安全启动CSM自动关闭')
            return True
        else:
            stylelog.fail('打开安全启动CSM没有自动关闭')
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        boot_setup_set_uefi()


@core.test_case(('3308', '[TC3308]审计模式验证工具ByoAuditModeTest.efi', '审计模式验证工具ByoAuditModeTest.efi'))
def secure_boot_3308():
    """
    Name:   审计模式验证工具ByoAuditModeTest
    Condition:  审计模式

    Steps:  1.进入内置Shell,运行工具ByoAuditModeTest

    Result: 1.日志打印信息显示USB设备，每执行一次会增加一条同样的USB设备信息，无乱码显示
    """
    try:
        count = 0
        _confirm_audit_mode()
        assert SetUpLib.boot_to_boot_menu()
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        else:
            if BmcLib.ping_sut():
                time.sleep(30)
                SetUpLib.reboot()
                logging.info("成功进入Linux系统")
                time.sleep(10)
            else:
                stylelog.fail('进入Linux系统失败')
                count += 1

        assert boot_to_internal_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(f'cd {SutConfig.Sec.BYOAUDIT_TOOL_PATH}')
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Sec.BYOAUDIT_TOOL_NAME)
        data = SetUpLib.get_data(3)
        logging.info(data)
        if re.search(SutConfig.Sec.BYOAUDIT_VERIFY_MSG, data):
            logging.info('审计模式下ByoAuditModeTest.efi工具验证成功')
        else:
            stylelog.fail('审计模式下ByoAuditModeTest.efi工具验证失败')
            count += 1

        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Sec.BYOAUDIT_TOOL_NAME)
        data = SetUpLib.get_data(3)
        logging.info(data)
        if re.search(SutConfig.Sec.BYOAUDIT_VERIFY_MSG, data):
            logging.info('审计模式下ByoAuditModeTest.efi工具验证成功')
        else:
            stylelog.fail('审计模式下ByoAuditModeTest.efi工具验证失败')
            count += 1

        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Sec.BYOAUDIT_TOOL_NAME)
        data = SetUpLib.get_data(3)
        logging.info(data)
        if re.search(SutConfig.Sec.BYOAUDIT_VERIFY_MSG, data):
            logging.info('审计模式下ByoAuditModeTest.efi工具验证成功')
        else:
            stylelog.fail('审计模式下ByoAuditModeTest.efi工具验证失败')
            count += 1

        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Sec.BYOAUDIT_TOOL_NAME)
        data = SetUpLib.get_data(3)
        logging.info(data)
        if re.search(SutConfig.Sec.BYOAUDIT_VERIFY_MSG, data):
            logging.info('审计模式下ByoAuditModeTest.efi工具验证成功')
        else:
            stylelog.fail('审计模式下ByoAuditModeTest.efi工具验证失败')
            count += 1

        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Sec.BYOAUDIT_TOOL_NAME)
        data = SetUpLib.get_data(3)
        logging.info(data)
        if re.search(SutConfig.Sec.BYOAUDIT_VERIFY_MSG, data):
            logging.info('审计模式下ByoAuditModeTest.efi工具验证成功')
        else:
            stylelog.fail('审计模式下ByoAuditModeTest.efi工具验证失败')
            count += 1

        time.sleep(1)
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3401', '[TC3401]PK安全设置项管理', 'PK安全设置项管理'))
def secure_boot_3401():
    """
    Name:   PK安全设置项管理

    Steps:  1.注册PK后选择放弃
            2.注册PK后按ESC
            3.注册PK选择不支持的文件类型
            4.注册PK不选择任何文件按提交
            5.注册PK
            6.删除PK选择放弃
            7.删除PK按ESC
            8.删除PK选择删除

    Result: 1/2/3/4.PK证书没有导入成功
            5.PK证书导入成功，且安全启动显示打开和系统模式显示为用户模式
            6/7.PK证书没有删除成功且仍然可以选择删除
            8.PK证书删除成功,安全启动显示关闭和系统模式为设定模式
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('注册PK后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Enroll PK Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Discard Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        if not SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
            logging.info('PK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('PK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册PK后按ESC')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Enroll PK Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        if not SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
            logging.info('PK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('PK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册PK选择不支持的文件类型')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Enroll PK Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('选择不支持的文件类型，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('选择不支持的文件类型，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        if not SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
            logging.info('PK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('PK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册PK不选择任何文件按提交')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('不选择文件提交，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('不选择文件提交，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        if not SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
            logging.info('PK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('PK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册PK')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Enroll PK Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *User Mode', data) and re.search('<Enabled> *Secure Boot', data):
            logging.info('PK证书导入成功，且安全启动显示打开和系统模式显示为用户模式')
        else:
            stylelog.fail('安全启动不是打开和系统模式不是用户模式')
            count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        assert SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4), '注册PK失败'
        logging.info('删除PK选择放弃')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3), '删除Key没有提示确认信息'
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key(Key.N)
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        assert SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4), 'Key被删除'
        logging.info('删除Key时按取消，没有删除Key')
        logging.info('删除PK按ESC')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3), '删除Key没有提示确认信息'
        time.sleep(1)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        assert SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4), 'Key被删除'
        logging.info('删除Key时按ESC，没有删除Key')
        logging.info('删除PK选择删除')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3), '删除Key没有提示确认信息'
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key(Key.Y)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        data = SetUpLib.get_data(3)
        if re.search('System Mode *Setup Mode', data) and re.search('<Disabled> *Secure Boot', data):
            logging.info('PK证书删除成功，且安全启动显示关闭和系统模式显示为设定模式')
        else:
            stylelog.fail('安全启动不是关闭和系统模式不是设定模式')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3402', '[TC3402]KEK安全设置项管理', 'KEK安全设置项管理'))
def secure_boot_3402():
    """
    Name:   KEK安全设置项管理

    Steps:  1.注册KEK后选择放弃
            2.注册KEK后按ESC
            3.注册KEK选择不支持的文件类型
            4.注册KEK不选择任何文件按提交
            5.注册KEK，不选择GUID
            6.注册KEK输入格式错误的GUID
            7.注册KEK输入字符数不够的GUID
            8.注册KEK输入正确的GUID
            9.删除KEK选择放弃
            10.删除KEK按ESC
            11.删除KEK选择删除

    Result: 1/2/3/4.KEK证书没有导入成功
            5.KEK证书导入成功
            6.提示格式错误
            7.提示字符数不够
            8.KEK证书导入成功，且证书名称显示正确
            9/10.KEK证书没有删除成功
            11.KEK证书删除成功
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('注册KEK后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Discard Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('KEK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('KEK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册KEK后按ESC')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('KEK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('KEK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册KEK选择不支持的文件类型')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('选择不支持的文件类型，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('选择不支持的文件类型，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('KEK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('KEK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册KEK不选择任何文件按提交')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('不选择文件提交，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('不选择文件提交，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('KEK Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('KEK Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册KEK，不选择GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        assert SetUpLib.wait_message('\[.*\]', 2), '注册KEK失败'
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        logging.info('注册KEK输入格式错误的GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.GUID_NAME], 18)
        time.sleep(1)
        SetUpLib.send_data_enter('123456789012346578909876543210123456')
        assert SetUpLib.wait_message(SutConfig.Sec.ERROR_CHARACTERS,3),'输入错误格式的GUID没有提示格式错误'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册KEK输入字符数不够的GUID')
        SetUpLib.send_data_enter('1234567abc')
        assert SetUpLib.wait_message(SutConfig.Sec.LOW_CHARACTERS, 3), '输入字符数不够的GUID没有提示字符数不够'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册KEK输入正确的GUID')
        SetUpLib.send_data_enter('11111111-2222-3333-4444-1234567890ab')
        assert SetUpLib.wait_message('11111111-2222-3333-4444-1234567890ab', 3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        assert SetUpLib.locate_option(Key.DOWN, ['11111111-2222-3333-4444-1234567890AB'], 4), '注册KEK失败'
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('删除KEK选择放弃')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        assert SetUpLib.wait_message('\[.*\]', 2), 'KEK被删除'
        logging.info('删除Key时选择放弃，没有删除Key')
        logging.info('删除KEK按ESC')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        assert SetUpLib.wait_message('\[.*\]', 2), 'KEK被删除'
        logging.info('删除Key时按ESC，没有删除Key')
        time.sleep(1)
        logging.info('删除KEK选择删除')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'],
                                                10)
        assert not SetUpLib.wait_message('\[.*\]', 2), 'KEK删除失败'
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3403', '[TC3403]DB安全设置项管理', 'DB安全设置项管理'))
def secure_boot_3403():
    """
    Name:   DB安全设置项管理

    Steps:  1.注册DB后选择放弃
            2.注册DB后按ESC
            3.注册DB选择不支持的文件类型
            4.注册DB不选择任何文件按提交
            5.注册DB，不选择GUID
            6.注册DB输入字符数不够的GUID
            7.注册DB输入格式错误的GUID
            8.注册DB输入正确的GUID
            9.删除DB选择放弃
            10.删除DB按ESC
            11.删除DB选择删除

    Result: 1/2/3/4.DB证书没有导入成功
            5.DB证书导入成功
            6.提示格式错误
            7.提示字符数不够
            8.DB证书导入成功，且证书名称显示正确
            9/10.DB证书没有删除成功
            11.DB证书删除成功

    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('DB选项............................................')
        logging.info('注册DB后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Discard Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DB Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DB Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DB后按ESC')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DB Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DB Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DB选择不支持的文件类型')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('选择不支持的文件类型，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('选择不支持的文件类型，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DB Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DB Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DB不选择任何文件按提交')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('不选择文件提交，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('不选择文件提交，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DB Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DB Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DB，不选择GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        assert SetUpLib.wait_message('\[.*\]', 2), '注册DB失败'
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        logging.info('注册DB输入字符数不够的GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.GUID_NAME], 18)
        time.sleep(1)
        SetUpLib.send_data_enter('12345678901')
        assert SetUpLib.wait_message(SutConfig.Sec.LOW_CHARACTERS, 3), '输入字符不够的GUID没有提示字符不够'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册DB输入格式错误的GUID')
        SetUpLib.send_data_enter('11111111-2222-3333-4444-1234567890GH')
        assert SetUpLib.wait_message(SutConfig.Sec.ERROR_CHARACTERS, 3), '输入错误格式的GUID没有提示格式错误'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册DB输入正确的GUID')
        SetUpLib.send_data_enter('11111111-2222-3333-4444-1234567890ab')
        assert SetUpLib.wait_message('11111111-2222-3333-4444-1234567890ab', 3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        assert SetUpLib.locate_option(Key.DOWN, ['11111111-2222-3333-4444-1234567890AB'], 4), '注册DB失败'
        logging.info('成功注册Key')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('删除DB选择放弃')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        assert SetUpLib.wait_message('\[.*\]', 2), 'DB被删除'
        logging.info('删除DB按ESC')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        assert SetUpLib.wait_message('\[.*\]', 2), 'DB被删除'
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        assert not SetUpLib.wait_message('\[.*\]', 2), 'DB没有删除'
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3404', '[TC3404]DBX安全设置项管理', 'DBX安全设置项管理'))
def secure_boot_3404():
    """
    Name:   DBX安全设置项管理

    Steps:  1.注册DBX后选择放弃
            2.注册DBX后按ESC
            3.注册DBX选择不支持的文件类型
            4.注册DBX不选择任何文件按提交
            5.注册DBX输入字符数不够的GUID
            6.注册DBX输入格式错误的GUID
            7.注册DBX输入正确的GUID
            8.删除签名列表选择放弃
            9.删除签名列表按ESC
            10.删除签名列表
            11.删除签名列表中单个签名数据且选择放弃
            12.删除签名列表中单个签名数据按ESC
            13.删除签名列表中N个签名数据
            14.删除所有签名列表且选择放弃
            15.删除所有签名列表按ESC
            16.删除所有签名列表

    Result: 1/2/3/4.DBX证书没有导入成功
            5.提示字符数不够
            6.提示格式错误
            7.DBX证书导入成功，且证书名称显示正确
            8/9.DBX证书删除失败
            10.DBX证书删除成功
            11/12.DBX证书删除失败
            13.DBX证书删除成功，且签名数据总数减少N
            14/15.所有签名删除失败
            16.所有签名删除成功
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('注册DBX后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Discard Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                10)
        if not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3):
            logging.info('DBX Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBX Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1

        logging.info('注册DBX后按ESC')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                10)
        if not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3):
            logging.info('DBX Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBX Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DBX选择不支持的文件类型')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('选择不支持的文件类型，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('选择不支持的文件类型，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                10)
        if not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3):
            logging.info('DBX Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBX Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DBX不选择任何文件按提交')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('不选择文件提交，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('不选择文件提交，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                10)
        if not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3):
            logging.info('DBX Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBX Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DBX输入字符数不够的GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.GUID_NAME], 18)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_data_enter('1245687')
        assert SetUpLib.wait_message(SutConfig.Sec.LOW_CHARACTERS, 3), '输入字符数不够的GUID,没有提示字符不够'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)

        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册DBX输入格式错误的GUID')
        SetUpLib.send_data_enter('11111111-2222-3333-444411234567890ab')
        assert SetUpLib.wait_message(SutConfig.Sec.ERROR_CHARACTERS,3),'输入格式错误的GUID,没有提示格式错误'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册DBX输入正确的GUID')
        SetUpLib.send_data_enter('11111111-2222-3333-4444-1234567890ab')
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                10)
        assert SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        assert SetUpLib.locate_option(Key.DOWN, ['Signature Data, Entry-1'], 5)
        assert re.search('11111111-2222-3333-4444-1234567890ab', SetUpLib.help_msg, re.I)
        logging.info('成功注册DBX')
        assert SetUpLib.locate_option(Key.UP, ['Delete All Signature Data'], 18)
        logging.info('删除签名列表选择放弃')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        assert SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3), '删除签名列表选择放弃，仍被删除'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('删除签名列表按ESC')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        assert SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3), '删除签名列表按ESC，仍被删除'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('删除签名列表')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        assert not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3), '没有删除'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_SECURE_BOOT, 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature',
                                                 'Signature List, Entry-1'],
                                                10)
        time.sleep(2)
        SetUpLib.send_key(Key.UP)
        data = SetUpLib.get_data(3)
        max_data = re.findall('Signature Data, Entry-(\d+)\s', data)
        max_num = max_data[-1] if max_data else '0'
        logging.info('删除签名列表中单个签名数据且选择放弃')
        assert SetUpLib.locate_option(Key.DOWN, ['Signature Data, Entry-1'], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        assert SetUpLib.locate_option(Key.UP, ['Delete Checked Signature Data'], 12)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.UP)
        data = re.findall('Signature Data, Entry-(\d+)\s', SetUpLib.get_data(3))
        if data and max_num == data[-1]:
            logging.info('删除签名列表中单个签名数据且选择放弃,没有删除')
        else:
            stylelog.fail('删除签名列表中单个签名数据且选择放弃,被删除')
            return
        logging.info('删除签名列表中单个签名数据按ESC')
        assert SetUpLib.locate_option(Key.DOWN, ['Signature Data, Entry-1'], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        assert SetUpLib.locate_option(Key.UP, ['Delete Checked Signature Data'], 12)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.UP)
        data = re.findall('Signature Data, Entry-(\d+)\s', SetUpLib.get_data(3))
        if data and max_num == data[-1]:
            logging.info('删除签名列表中单个签名数据按ESC,没有删除')
        else:
            stylelog.fail('删除签名列表中单个签名数据按ESC,被删除')
            return
        logging.info('删除签名列表中N个签名数据')
        if len(max_data) > 6:
            for i in range(1, 5):
                option_name = 'Signature Data, Entry-{}'.format(i)
                assert SetUpLib.locate_option(Key.DOWN, [option_name], 10)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
            change_num = 4
        else:
            assert SetUpLib.locate_option(Key.DOWN, ['Signature Data, Entry-1'], 10)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            change_num = 1
        assert SetUpLib.locate_option(Key.UP, ['Delete Checked Signature Data'], 12)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.UP)
        data = re.findall('Signature Data, Entry-(\d+)\s', SetUpLib.get_data(3))
        if data and str(int(max_num) - change_num) == data[-1]:
            logging.info(f'删除{change_num}个DBX证书成功')
        else:
            stylelog.fail(f'删除{change_num}个DBX证书失败,理论{str(int(max_num) - change_num)},实际{data[-1]}')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.locate_option(Key.UP, ['Delete All Signature List'], 5)
        logging.info('删除所有签名列表且选择放弃')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 5), '删除所有签名列表且选择放弃,删除'
        logging.info('删除所有签名列表且选择放弃,没有删除')
        assert SetUpLib.locate_option(Key.UP, ['Delete All Signature List'], 5)
        logging.info('删除所有签名列表按ESC')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 5), '删除所有签名列表按ESC,删除'
        logging.info('删除所有签名列表按ESC,没有删除')
        assert SetUpLib.locate_option(Key.UP, ['Delete All Signature List'], 5)
        logging.info('删除所有签名列表')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.send_key(Key.ENTER)
        assert not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 5), '删除所有签名列表,没有被删除'
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('3405', '[TC3405]DBT安全设置项管理', 'DBT安全设置项管理'))
def secure_boot_3405():
    """
    Name:   DBT安全设置项管理

    Steps:  1.注册DBT后选择放弃
            2.注册DBT后按ESC
            3.注册DBT选择不支持的文件类型
            4.注册DBT不选择任何文件按提交
            5.注册DBT，不选择GUID
            6.注册DBT输入字符数不够的GUID
            7.注册DBT输入格式错误的GUID
            8.注册DBT输入正确的GUID
            9.删除DBT选择放弃
            10.删除DBT按ESC
            11.删除DBT选择删除

    Result: 1/2/3/4.DBT证书没有导入成功
            5.DBT证书导入成功
            6.提示格式错误
            7.提示字符数不够
            8.DBT证书导入成功，且证书名称显示正确
            9/10.DBT证书没有删除成功
            11.DBT证书删除成功
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESTORE_FACTORY], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.RESET_SETUP_MODE], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('DBT选项............................................')
        logging.info('注册DBT后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Discard Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DBT Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBT Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DBT后按ESC')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DBT Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBT Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DBT选择不支持的文件类型')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('选择不支持的文件类型，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('选择不支持的文件类型，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DBT Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBT Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1
        logging.info('注册DBT不选择任何文件按提交')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Commit Changes and Exit'], 10)
        if SetUpLib.wait_message(SutConfig.Sec.ERROR_KEY_MSG, 3):
            logging.info('不选择文件提交，提示文件类型不支持')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('不选择文件提交，没有提示文件类型不支持')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        if not SetUpLib.wait_message('\[.*\]', 2):
            logging.info('DBT Key 为空')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            stylelog.fail('DBT Key 不为空')
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            count += 1

        logging.info('注册DBT，不选择GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        assert SetUpLib.wait_message('\[.*\]', 2), '注册DBT失败'
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        logging.info('注册DBT输入字符数不够的GUID')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 28)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.GUID_NAME], 18)
        time.sleep(1)
        SetUpLib.send_data_enter('12345678901')
        assert SetUpLib.wait_message(SutConfig.Sec.LOW_CHARACTERS, 3), '输入字符不够的GUID没有提示字符不够'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册DBT输入格式错误的GUID')
        SetUpLib.send_data_enter('123456789012346578909876543210123456')
        assert SetUpLib.wait_message(SutConfig.Sec.ERROR_CHARACTERS, 3), '输入错误格式的GUID没有提示格式错误'
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('注册KEK输入正确的GUID')
        SetUpLib.send_data_enter('11111111-2222-3333-4444-1234567890ab')
        assert SetUpLib.wait_message('11111111-2222-3333-4444-1234567890ab', 3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        assert SetUpLib.locate_option(Key.DOWN, ['11111111-2222-3333-4444-1234567890AB'], 4), '注册DB失败'
        logging.info('成功注册Key')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        logging.info('删除DBT选择放弃')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        assert SetUpLib.wait_message('\[.*\]', 2), 'DB被删除'
        logging.info('删除DBT按ESC')
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        time.sleep(1)
        SetUpLib.send_key('\x1b')
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        assert SetUpLib.wait_message('\[.*\]', 2), 'DBT被删除'
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3)
        logging.info('删除Key提示确认信息')
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                10)
        assert not SetUpLib.wait_message('\[.*\]', 2), 'DBT没有删除'
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
