# coding='utf-8'
import re
import time
import logging
from D2000.BaseLib import BmcLib, SetUpLib, SshLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from batf.Report import stylelog
from batf import core


def set_password(admin, user):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(admin)
    time.sleep(1)
    SetUpLib.send_data_enter(admin)
    if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 5):
        logging.info('管理员密码设置成功')
    else:
        stylelog.fail('管理员密码设置失败')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user)
    time.sleep(1)
    SetUpLib.send_data_enter(user)
    if SetUpLib.wait_message(SutConfig.Tool.SET_PSW_SUC_MSG, 5):
        logging.info('用户密码设置成功')
    else:
        stylelog.fail('用户密码设置失败')
        return
    time.sleep(1)
    return True


def go_to_setup(key=SutConfig.Msg.SETUP_KEY, pw_prompt=SutConfig.Tool.POST_PSW_MSG, password='Admin@1'):
    SetUpLib.reboot()
    logging.info("SetUpLib: Booting to setup")
    try_counts = 3
    while try_counts:
        logging.info("Waiting for Hotkey message found...")
        result = SetUpLib.boot_with_hotkey_only(key, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE,
                                                pw_prompt, password)
        if result == [True, True]:
            logging.info("SetUpLib: Boot to setup main page successfully,with password")
            return [True, True]
        elif result == True:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True
        else:
            SetUpLib.reboot()
            try_counts -= 1
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


def del_psw_all(admin, user):
    go_to_setup(password=admin)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_ADMIN_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(admin)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Tool.DEL_PSW_SUC_MSG, 5):
        logging.info('管理员密码删除成功')
    else:
        stylelog.fail('管理员密码删除失败')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Tool.DEL_PSW_SUC_MSG, 5):
        logging.info('用户密码删除成功')
    else:
        stylelog.fail('用户密码删除失败')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    return True


def get_options_value():
    # return Update._get_options_value()
    option_path = SutConfig.Tool.OPTION_PATH
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    SetUpLib.clean_buffer()
    options = []
    trycounts = 12
    while trycounts:
        SetUpLib.clean_buffer()
        data = SetUpLib.get_data(3, Key.RIGHT)
        options = options + re.findall(r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}',
                                       data)
        if SutConfig.Msg.PAGE_MAIN in data:
            break
        trycounts -= 1
    for index, option in enumerate(option_path):
        if option in SutConfig.Msg.PAGE_ALL:
            if len(option_path) > 1 and option_path[index - 1] == option:
                if not SetUpLib.locate_option(Key.DOWN, [option], 3):
                    if not SetUpLib.locate_option(Key.UP, [option], 4):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                SetUpLib.clean_buffer()
                SetUpLib.send_key(Key.ENTER)
                data = SetUpLib.get_data(3)
                options = options + re.findall(
                    r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}', data)
            else:
                assert SetUpLib.back_to_setup_toppage()
                assert SetUpLib.boot_to_page(option)
        elif option == 'ESC':
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            if not SetUpLib.locate_option(Key.DOWN, [option], 25):
                if not SetUpLib.locate_option(Key.UP, [option], 28):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.5)
            SetUpLib.clean_buffer()
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(3)
            options = options + re.findall(
                r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}', data)
    return [i.replace(' ', '') for i in options]


@core.test_case(('301', '[TC301]Upgrade BIOS SetUp', 'SetUp升级BIOS'))
def upgrade_bios_setup():
    try:
        count = 0
        admin = SutConfig.Upd.PASSWORDS[0]
        user = SutConfig.Upd.PASSWORDS[1]
        assert SetUpLib.boot_to_setup()
        assert set_password(admin, user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.CHANGE_OPTIONS, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert go_to_setup(password=admin)
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.UPDATE_BIOS_LATEST, 40, 'Confirmation', timeout=15)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
            logging.info('BIOS 刷新成功')
        time.sleep(100)
        result = go_to_setup(password=admin)
        updated_options = get_options_value()
        default_options = SutConfig.Tool.DEFAULT_OPTION_VALUE

        logging.info(f'默认值:{default_options}')
        logging.info(f'刷新后:{updated_options}')
        if result == True:
            logging.info('SetUp刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('SetUp刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if updated_options == default_options:
            logging.info('SetUp刷新BIOS，刷新BIOS后恢复默认值')
        else:
            stylelog.fail('SetUp刷新BIOS，刷新BIOS后没有恢复默认值')
            count += 1
            for i in updated_options:
                if i not in default_options:
                    logging.info('刷新后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in default_options:
                if i not in updated_options:
                    logging.info('默认的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('302', '[TC302]Downgrade BIOS SetUp', 'SetUp降级BIOS'))
def downgrade_bios_setup():
    try:
        count = 0
        admin = SutConfig.Upd.PASSWORDS[0]
        user = SutConfig.Upd.PASSWORDS[1]
        assert SetUpLib.boot_to_setup()
        assert set_password(admin, user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.CHANGE_OPTIONS, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert go_to_setup(password=admin)
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.UPDATE_BIOS_PREVIOUS, 40, 'Confirmation', timeout=15)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
            logging.info('BIOS 刷新成功')
        time.sleep(100)
        result = go_to_setup(password=admin)
        updated_options = get_options_value()
        default_options = SutConfig.Tool.DEFAULT_OPTION_VALUE

        logging.info(f'默认值:{default_options}')
        logging.info(f'刷新后:{updated_options}')
        if result == True:
            logging.info('SetUp刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('SetUp刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if updated_options == default_options:
            logging.info('SetUp刷新BIOS，刷新BIOS后恢复默认值')
        else:
            stylelog.fail('SetUp刷新BIOS，刷新BIOS后没有恢复默认值')
            count += 1
            for i in updated_options:
                if i not in default_options:
                    logging.info('刷新后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in default_options:
                if i not in updated_options:
                    logging.info('默认的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('303', '[TC303]Update wrong BIOS SetUp(other,unsign)', 'SetUp下更新未签名,其他平台BIOS'))
def update_wrong_bios_setup():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        if SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.UPDATE_BIOS_OTHERS, 40, SutConfig.Upd.UPDATE_OTHERS_MSG,
                               timeout=15):
            logging.info(f'SetUp下更新其他平台的BIOS，提示{SutConfig.Upd.UPDATE_OTHERS_MSG}')
            time.sleep(1)
        else:
            stylelog.fail(f'SetUp下更新其他平台的BIOS，没有提示{SutConfig.Upd.UPDATE_OTHERS_MSG}')
            wrong_msg.append(f'SetUp下更新其他平台的BIOS，没有提示{SutConfig.Upd.UPDATE_OTHERS_MSG}')
            count += 1
        assert SetUpLib.back_to_setup_toppage()
        if SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.UPDATE_BIOS_UNSIGN, 40, SutConfig.Upd.UPDATE_UNSIGN_MSG,
                               timeout=15):
            logging.info(f'SetUp下更新未签名的BIOS，提示{SutConfig.Upd.UPDATE_UNSIGN_MSG}')
            time.sleep(1)
        else:
            if SetUpLib.wait_message_enter(SutConfig.Upd.UPDATE_UNSIGN_MSG, 5):
                logging.info(f'SetUp下更新未签名的BIOS，提示{SutConfig.Upd.UPDATE_UNSIGN_MSG}')
                time.sleep(1)
            else:
                stylelog.fail(f'SetUp下更新未签名的BIOS，没有提示{SutConfig.Upd.UPDATE_UNSIGN_MSG}')
                wrong_msg.append(f'SetUp下更新未签名的BIOS，没有提示{SutConfig.Upd.UPDATE_UNSIGN_MSG}')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
