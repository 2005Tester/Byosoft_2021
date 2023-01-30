# -*- encoding=utf8 -*-
from D2000.BaseLib import SetUpLib, SshLib, BmcLib
from D2000.Config import SutConfig
from D2000.Config.PlatConfig import Key
import time, logging, re
from batf.SutInit import Sut
from batf import core
from batf.Report import stylelog





def boot_to_internal_shell(key=SutConfig.Msg.BOOTMENU_KEY):
    SetUpLib.boot_to_setup()
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
    # assert boot_to_windows_os()
    # output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL)
    # logging.debug(output)
    # if re.search(SutConfig.Tool.WINDOWS_MSG_ALL, output[0]):
    #     logging.info('WINDOWS下BIOS更新成功')
    # else:
    #     stylelog.fail('WINDOWS下更新可能失败')
    # SetUpLib.reboot()
    # time.sleep(200)
    assert SetUpLib.boot_to_linux_os()
    SetUpLib.linux_mount_usb()
    output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL)
    logging.debug(output)
    if re.search(SutConfig.Tool.LINUX_MSG_ALL, output[0]):
        logging.info('LINUX下BIOS更新成功')
    else:
        stylelog.fail('LINUX下更新可能失败')
    SetUpLib.reboot()
    time.sleep(200)
    return True


def _update_bios_normal():
    # assert boot_to_windows_os()
    # output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST)
    # logging.debug(output)
    # if re.search(SutConfig.Tool.WINDOWS_MSG_NOR, output[0]):
    #     logging.info('WINDOWS下BIOS更新成功')
    # else:
    #     stylelog.fail('WINDOWS下更新可能失败')
    # SetUpLib.reboot()
    # time.sleep(10)
    assert SetUpLib.boot_to_linux_os()
    SetUpLib.linux_mount_usb()
    output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST)
    logging.debug(output)
    if re.search(SutConfig.Tool.LINUX_MSG_NOR, output[0]):
        logging.info('LINUX下BIOS更新成功')
    else:
        stylelog.fail('LINUX下更新可能失败')
    SetUpLib.reboot()
    time.sleep(10)
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


@core.test_case(('3001', '[TC3001]默认设定模式测试', '默认设定模式测试'))
def secure_boot_3001():
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
        time.sleep(8)
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
    try:
        count = 0
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DEPLOYED_MODE], 10)
        time.sleep(5)
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
    try:
        count = 0
        _confirm_setup_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.AUDIT_MODE], 10)
        time.sleep(5)
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


@core.test_case(('3101', '[TC3101]用户模式下关闭安全启动', '用户模式下关闭安全启动'))
def secure_boot_3101():
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
        time.sleep(8)
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
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.AUDIT_MODE], 10)
        time.sleep(5)
        SetUpLib.send_key(Key.ESC)
        time.sleep(3)
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
    try:
        count = 0
        _confirm_user_mode()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_INTERNAL_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.DEPLOYED_MODE], 10)
        time.sleep(5)
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


@core.test_case(('3201', '[TC3201]部署模式进入用户模式', '部署模式进入用户模式'))
def secure_boot_3201():
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


@core.test_case(('3301', '[TC3301]审计模式进入部署模式', '审计模式进入部署模式'))
def secure_boot_3301():
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
        time.sleep(8)
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


@core.test_case(('3308', '[TC3308]审计模式验证工具ByoAuditModeTest.efi', '审计模式验证工具ByoAuditModeTest.efi'))
def secure_boot_3308():
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


@core.test_case(('3401', '[TC3401]证书管理', '证书管理'))
def secure_boot_3401():
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
        logging.info('PK选项............................................')
        logging.info('注册PK后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Enroll PK Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 18)
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
        logging.info('删除PK选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK, 'Enroll PK',
                                                           'Enroll PK Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
        if SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
            logging.info('成功注册Key')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                logging.info('删除Key提示确认信息')
                time.sleep(1)
                SetUpLib.send_key(Key.N)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.PK], 10)
                if SetUpLib.locate_option(Key.DOWN, ['Delete Pk'], 4):
                    logging.info('删除Key时按取消，没有删除Key')
                else:
                    stylelog.fail('Key被删除')
                    count += 1
                SetUpLib.back_to_setup_toppage()
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
                time.sleep(1)
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
            else:
                stylelog.fail('删除Key没有提示确认信息')
                count += 1
        else:
            stylelog.fail('注册Key失败')
            count += 1
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('KEK选项............................................')
        logging.info('注册KEK后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 18)
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
        logging.info('删除KEK')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Enroll KEK',
                                                           'Enroll KEK using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
        if SetUpLib.wait_message('\[.*\]', 2):
            logging.info('成功注册Key')
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                logging.info('删除Key提示确认信息')
                time.sleep(1)
                SetUpLib.send_key(Key.N)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                        [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'], 10)
                if SetUpLib.wait_message('\[.*\]', 2):
                    logging.info('删除Key时按取消，没有删除Key')
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                        logging.info('删除Key提示确认信息')
                        time.sleep(1)
                        SetUpLib.send_key(Key.Y)
                        time.sleep(2)
                    else:
                        stylelog.fail('删除Key时没有提示确认信息')
                        count += 1

                else:
                    stylelog.fail('删除Key时按取消，仍删除Key')
                    count += 1
            else:
                stylelog.fail('删除Key时没有提示确认信息')
                count += 1
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.KEK, 'Delete KEK'],
                                                    10)
            if not SetUpLib.wait_message('\[.*\]', 2):
                logging.info('成功删除Key')
            else:
                stylelog.fail('删除Key失败')
                count += 1
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
                time.sleep(1)
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
        else:
            stylelog.fail('注册KEK失败')
            count += 1

        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)

        logging.info('DB选项............................................')
        logging.info('注册DB后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 18)
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

        logging.info('删除DB')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                10)
        if SetUpLib.wait_message('\[.*\]', 2):
            logging.info('成功注册Key')
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                logging.info('删除Key提示确认信息')
                time.sleep(1)
                SetUpLib.send_key(Key.N)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                        [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                        10)
                if SetUpLib.wait_message('\[.*\]', 2):
                    logging.info('删除Key时按取消，没有删除Key')
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                        logging.info('删除Key提示确认信息')
                        time.sleep(1)
                        SetUpLib.send_key(Key.Y)
                        time.sleep(2)
                    else:
                        stylelog.fail('删除Key时没有提示确认信息')
                        count += 1

                else:
                    stylelog.fail('删除Key时按取消，仍删除Key')
                    count += 1
            else:
                stylelog.fail('删除Key时没有提示确认信息')
                count += 1

            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DB, 'Delete Signature'],
                                                    10)
            if not SetUpLib.wait_message('\[.*\]', 2):
                logging.info('成功删除Key')
            else:
                stylelog.fail('删除Key失败')
                count += 1
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
                time.sleep(1)
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)

        else:
            stylelog.fail('注册DB失败')
            count += 1
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)

        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        logging.info('DBX选项............................................')
        logging.info('注册DBX后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 18)
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
        logging.info('注册DB不选择任何文件按提交')
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
        logging.info('删除DBX')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                10)
        if SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 3):
            logging.info('成功注册Key')
            assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Delete All Signature List'], 10)
            time.sleep(2)
            SetUpLib.send_key(Key.N)
            time.sleep(1)
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                    10)
            if SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 4):
                logging.info('删除Key时，取消，Key仍然存在')
                assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Delete All Signature List'], 10)
                time.sleep(2)
                SetUpLib.send_key(Key.Y)
                time.sleep(1)
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
                assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                        [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBX, 'Delete Signature'],
                                                        10)
                if not SetUpLib.locate_option(Key.DOWN, ['Signature List, Entry-1'], 4):
                    logging.info('成功删除Key')
                else:
                    stylelog.fail('删除Key失败')
                    count += 1

            else:
                stylelog.fail('删除Key时，取消，Key不存在')
                count += 1
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        else:
            stylelog.fail('注册Key失败')
            count += 1
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)

        logging.info('DBT选项............................................')
        logging.info('注册DBT后选择放弃')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
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
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.ERROR_KEY_PATH, 18)
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
        logging.info('删除DBT')
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Enroll Signature',
                                                           'Enroll Signature Using File'], 10)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.KEY_PATH, 18)
        time.sleep(3)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, ['Commit Changes and Exit'], 10)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'], 10)
        if SetUpLib.wait_message('\[.*\]', 2):
            logging.info('成功注册Key')
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                logging.info('删除Key提示确认信息')
                time.sleep(1)
                SetUpLib.send_key(Key.N)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                SetUpLib.send_key(Key.ESC)
                time.sleep(5)
                assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                        [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                        10)
                if SetUpLib.wait_message('\[.*\]', 2):
                    logging.info('删除Key时按取消，没有删除Key')
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    if SetUpLib.wait_message(SutConfig.Sec.DEL_KEY_MSG, 3):
                        logging.info('删除Key提示确认信息')
                        time.sleep(1)
                        SetUpLib.send_key(Key.Y)
                        time.sleep(2)
                    else:
                        stylelog.fail('删除Key时没有提示确认信息')
                        count += 1

                else:
                    stylelog.fail('删除Key时按取消，仍删除Key')
                    count += 1
            else:
                stylelog.fail('删除Key时没有提示确认信息')
                count += 1
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    [SutConfig.Sec.KEY_MAN, SutConfig.Sec.DBT, 'Delete Signature'],
                                                    10)
            if not SetUpLib.wait_message('\[.*\]', 2):
                logging.info('成功删除Key')
            else:
                stylelog.fail('删除Key失败')
                count += 1
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
                time.sleep(1)
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)

        else:
            stylelog.fail('注册DBT失败')
            count += 1
            SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)

        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SECURE_BOOT_PATH, 18)
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.RESET_SETUP_MODE, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)

        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
