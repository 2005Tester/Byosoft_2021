# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *


def _mount_usb_insmod():
    mount_path = SetUpLib.get_linux_usb_dev()
    SshLib.execute_command_limit(Sut.OS_SSH, "mount {0} {1}".format(mount_path,
                                                                    SutConfig.Env.LINUX_USB_MOUNT))
    SshLib.execute_command_limit(Sut.OS_SSH, 'insmod {0}ufudev.ko'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp flash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    SshLib.execute_command_limit(Sut.OS_SSH, 'cd {0};cp ByoFlash /root/'.format(SutConfig.Env.LINUX_BIOS_MOUNT_PATH))
    SshLib.execute_command_limit(Sut.OS_SSH, 'chmod 775 -R *')
    time.sleep(1)
    return True


def _change_options_value_part1():
    SetUpLib.clean_buffer()
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN, SutConfig.Upd.CHANGE_PART1, 25)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    return True


def _change_options_value_part2():
    SetUpLib.clean_buffer()
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN, SutConfig.Upd.CHANGE_PART2, 25)
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    return True


def _change_options_value_part3():
    SetUpLib.clean_buffer()
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN, SutConfig.Upd.CHANGE_PART3_2, 10)
    time.sleep(2)
    return True


def _change_options(change_part):
    if change_part.lower() == 'all':
        _go_to_setup()
        assert _change_options_value_part1()
        assert _change_options_value_part2()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        _go_to_setup()
        assert _change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        _go_to_setup()
        assert _change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        _go_to_setup()
        assert _change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    return True


def set_password(admin=SutConfig.Upd.PASSWORDS[0], users=SutConfig.Upd.PASSWORDS[1]):
    SetUpPassword._go_to_setup(is_del=True)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY, 10)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 10)
    assert PwdLib.set_user(users, True)
    SetUpLib.enter_menu_change_value_ignore(Key.DOWN,
                                            [{SutConfig.Psw.PSW_LOCK_OPTION: 100}] + SutConfig.Psw.SET_TIME_MONTH, 18)
    if SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5):
        time.sleep(1)
        SetUpLib.send_key(Key.UP)
        time.sleep(1)
        SetUpLib.enter_menu_change_value_ignore(Key.DOWN, [{SutConfig.Psw.CHECK_PSW: 'Enabled'},
                                                           {SutConfig.Psw.PSW_COMPLEXITY: 'Enabled'},
                                                           {SutConfig.Psw.PSW_LEN: 10}, {SutConfig.Psw.PSW_RETRY: 6}],
                                                18)
    time.sleep(3)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Psw.POWER_ON_PSW_OPTION: 'Disabled'}], 10, save=True)
    return True


def _go_to_setup(password=SutConfig.Upd.PASSWORDS[0], users=SutConfig.Upd.PASSWORDS[1]):
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    try_counts = 2
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        result = SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 300, SutConfig.Msg.POST_MESSAGE,
                                                SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, password=password)
        if result == [True, True]:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True
        elif result == True:
            assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
            assert PwdLib.set_admin(password, True)
            assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 10)
            assert PwdLib.set_user(users, True)
            assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
            return False
        else:
            BmcLib.power_cycle()
            try_counts -= 1
    return


def del_password(password=SutConfig.Upd.PASSWORDS[0]):
    _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Msg.PAGE_SECURITY], 10)
    assert PwdLib.del_admin(password, True)
    SetUpLib.default_save()
    return True


def _update_bios(env, update_mode, bios_mode):
    if env.lower() == 'setup':
        if update_mode.lower() == 'normal':
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Msg.PAGE_EXIT, 18)
            if bios_mode.lower() == 'latest':
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 40, 'Confirmation', timeout=15)
            elif bios_mode.lower() == 'previous':
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 40, 'Confirmation', timeout=15)
            elif bios_mode.lower() == 'constant':
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 40, 'Confirmation', timeout=15)
            else:
                stylelog.fail('bios_mode有误')
                return
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
                logging.info('BIOS 刷新成功')
            BmcLib.power_reset()
            time.sleep(5)
        elif update_mode.lower() == 'all':
            assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
            if bios_mode.lower() == 'latest':
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 40, 'Confirmation', timeout=15)
            elif bios_mode.lower() == 'previous':
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_PREVIOUS, 40, 'Confirmation', timeout=15)
            elif bios_mode.lower() == 'constant':
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_CONSTANT, 40, 'Confirmation', timeout=15)
            else:
                stylelog.fail('bios_mode有误')
                return
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
                logging.info('BIOS 刷新成功')
            BmcLib.power_reset()
            time.sleep(200)
    elif env.lower() == 'dos':
        if update_mode.lower() == 'normal':
            assert SetUpLib.boot_to_boot_menu()
            assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 30, SutConfig.Ipm.LEGACY_USB_MSG)
            time.sleep(5)
            logging.info("DOS Boot Successed.")
            time.sleep(2)
            SetUpLib.send_data_enter('cd {}'.format(SutConfig.Env.BIOS_FILE))
            time.sleep(2)
            if bios_mode.lower() == 'latest':
                cmd = SutConfig.Upd.DOS_FLASH_CMD_LATEST
            elif bios_mode.lower() == 'previous':
                cmd = SutConfig.Upd.DOS_FLASH_CMD_PREVIOUS
            elif bios_mode.lower() == 'constant':
                cmd = SutConfig.Upd.DOS_FLASH_CMD_CONSTANT
            else:
                stylelog.fail('bios_mode有误')
                return
            for data in cmd:
                SetUpLib.send_data(data)
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            logging.info("Starting to update BIOS.")
            time.sleep(5)
            if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_NOR, 300, readline=False):
                logging.info("Update BIOS in DOS successed.")
            time.sleep(3)
            BmcLib.power_reset()
            time.sleep(3)
        elif update_mode.lower() == 'all':
            assert SetUpLib.boot_to_boot_menu()
            assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.DOS, 30, SutConfig.Upd.ENT_DOS_MSG)
            time.sleep(5)
            logging.info("DOS Boot Successed.")
            time.sleep(2)
            SetUpLib.send_data_enter('cd {}'.format(SutConfig.Env.BIOS_FILE))
            time.sleep(2)
            if bios_mode.lower() == 'latest':
                cmd = SutConfig.Upd.DOS_FLASH_CMD_LATEST_ALL
            elif bios_mode.lower() == 'previous':
                cmd = SutConfig.Upd.DOS_FLASH_CMD_PREVIOUS_ALL
            elif bios_mode.lower() == 'constant':
                cmd = SutConfig.Upd.DOS_FLASH_CMD_CONSTANT_ALL
            else:
                stylelog.fail('bios_mode有误')
                return
            for data in cmd:
                SetUpLib.send_data(data)
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            logging.info("Starting to update BIOS.")
            time.sleep(5)
            if SetUpLib.wait_message(SutConfig.Upd.DOS_MSG_ALL, 300, readline=False):
                logging.info("Update BIOS in DOS successed.")
            time.sleep(3)
            BmcLib.power_reset()
            time.sleep(200)
    elif env.lower() == 'shell':
        if update_mode.lower() == 'normal':
            assert SetUpLib.boot_to_boot_menu()
            assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30,
                                               SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
            time.sleep(10)
            logging.info("Shell Boot Successed.")
            SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
            time.sleep(2)
            SetUpLib.send_data_enter('ls')
            if SutConfig.Env.BIOS_FILE not in SetUpLib.get_data(2):
                fs = SetUpLib.get_shell_fs_num()
                SetUpLib.send_data_enter(fs)
                time.sleep(2)
            SetUpLib.send_data_enter('cd {}'.format(SutConfig.Env.BIOS_FILE))
            time.sleep(2)
            if bios_mode.lower() == 'latest':
                shell_cmd = SutConfig.Upd.SHELL_FLASH_CMD_LATEST
            elif bios_mode.lower() == 'previous':
                shell_cmd = SutConfig.Upd.SHELL_FLASH_CMD_PREVIOUS
            elif bios_mode.lower() == 'constant':
                shell_cmd = SutConfig.Upd.SHELL_FLASH_CMD_CONSTANT
            else:
                stylelog.fail('bios_mode有误')
                return
            SetUpLib.send_data_enter(shell_cmd)
            if SetUpLib.wait_message(SutConfig.Upd.PASSWORD_MSG, 3):
                SetUpLib.send_data_enter('1111111111')
                assert SetUpLib.wait_message(SutConfig.Upd.WRONG_PSW_MSG, 5), '输入错误密码没有提示密码错误'
                time.sleep(2)
                SetUpLib.send_data_enter(shell_cmd)
                assert SetUpLib.wait_message(SutConfig.Upd.PASSWORD_MSG, 3)
                SetUpLib.send_data_enter(SutConfig.Upd.PASSWORDS[0])
            if SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300):
                logging.info('BIOS 更新成功')

            time.sleep(5)
            BmcLib.power_reset()
            time.sleep(5)
        elif update_mode.lower() == 'all':
            assert SetUpLib.boot_to_boot_menu()
            assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30,
                                               SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
            time.sleep(10)
            logging.info("Shell Boot Successed.")
            SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
            time.sleep(2)
            SetUpLib.send_data_enter('ls')
            if SutConfig.Env.BIOS_FILE not in SetUpLib.get_data(2):
                fs = SetUpLib.get_shell_fs_num()
                SetUpLib.send_data_enter(fs)
                time.sleep(2)
            SetUpLib.send_data_enter('cd {}'.format(SutConfig.Env.BIOS_FILE))
            time.sleep(2)
            if bios_mode.lower() == 'latest':
                shell_cmd = SutConfig.Upd.SHELL_FLASH_CMD_LATEST_ALL
            elif bios_mode.lower() == 'previous':
                shell_cmd = SutConfig.Upd.SHELL_FLASH_CMD_PREVIOUS_ALL
            elif bios_mode.lower() == 'constant':
                shell_cmd = SutConfig.Upd.SHELL_FLASH_CMD_CONSTANT_ALL
            else:
                stylelog.fail('bios_mode有误')
                return
            SetUpLib.send_data_enter(shell_cmd)
            if SetUpLib.wait_message(SutConfig.Upd.PASSWORD_MSG, 3):
                SetUpLib.send_data_enter('1111111111')
                assert SetUpLib.wait_message(SutConfig.Upd.WRONG_PSW_MSG, 5), '输入错误密码没有提示密码错误'
                time.sleep(2)
                SetUpLib.send_data_enter(shell_cmd)
                assert SetUpLib.wait_message(SutConfig.Upd.PASSWORD_MSG, 3)
                SetUpLib.send_data_enter(SutConfig.Upd.PASSWORDS[0])
            if SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_ALL, 300):
                logging.info("Update BIOS in Shell successed.")
            BmcLib.power_reset()
            time.sleep(200)
    elif env.lower() == 'linux':
        if update_mode.lower() == 'normal':
            assert SetUpLib.boot_os_from_bm()
            _mount_usb_insmod()
            if bios_mode.lower() == 'latest':
                linux_cmd = f'{SutConfig.Upd.LINUX_FLASH_CMD_LATEST}\n'
            elif bios_mode.lower() == 'previous':
                linux_cmd = f'{SutConfig.Upd.LINUX_FLASH_CMD_PREVIOUS}\n'
            elif bios_mode.lower() == 'constant':
                linux_cmd = f'{SutConfig.Upd.LINUX_FLASH_CMD_CONSTANT}\n'
            else:
                stylelog.fail('bios_mode有误')
                return
            result = SshLib.invoke_shell(Sut.OS_SSH, linux_cmd, 300, f'{SutConfig.Upd.PASSWORD_MSG}|{SutConfig.Upd.LINUX_MSG_NOR}')
            if re.search(SutConfig.Upd.PASSWORD_MSG, result):
                assert SshLib.interaction(Sut.OS_SSH, [linux_cmd, '111111\n'],
                                          [SutConfig.Upd.PASSWORD_MSG, SutConfig.Upd.WRONG_PSW_MSG]), '没有提示密码错误'
                logging.info('刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
                assert SshLib.interaction(Sut.OS_SSH, [linux_cmd, f'{SutConfig.Upd.PASSWORDS[0]}\n'],
                                          [SutConfig.Upd.PASSWORD_MSG, SutConfig.Upd.LINUX_MSG_NOR])
                logging.info('BIOS更新成功')
            elif re.search(SutConfig.Upd.LINUX_MSG_NOR,result):
                logging.info('BIOS更新成功')
            else:
                stylelog.fail('BIOS更新失败')
                logging.info(result)
            time.sleep(3)
            BmcLib.power_reset()
            time.sleep(5)
        elif update_mode.lower() == 'all':
            assert SetUpLib.boot_os_from_bm()
            _mount_usb_insmod()
            if bios_mode.lower() == 'latest':
                linux_cmd = f'{SutConfig.Upd.LINUX_FLASH_CMD_LATEST_ALL}\n'
            elif bios_mode.lower() == 'previous':
                linux_cmd = f'{SutConfig.Upd.LINUX_FLASH_CMD_PREVIOUS_ALL}\n'
            elif bios_mode.lower() == 'constant':
                linux_cmd = f'{SutConfig.Upd.LINUX_FLASH_CMD_CONSTANT_ALL}\n',
            else:
                stylelog.fail('bios_mode有误')
                return
            result = SshLib.invoke_shell(Sut.OS_SSH, linux_cmd, 300,
                                         f'{SutConfig.Upd.PASSWORD_MSG}|{SutConfig.Upd.LINUX_MSG_ALL}')
            if re.search(SutConfig.Upd.PASSWORD_MSG, result):
                assert SshLib.interaction(Sut.OS_SSH, [linux_cmd, '111111\n'],
                                          [SutConfig.Upd.PASSWORD_MSG, SutConfig.Upd.WRONG_PSW_MSG]), '没有提示密码错误'
                logging.info('刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
                assert SshLib.interaction(Sut.OS_SSH, [linux_cmd, f'{SutConfig.Upd.PASSWORDS[0]}\n'],
                                          [SutConfig.Upd.PASSWORD_MSG, SutConfig.Upd.LINUX_MSG_ALL])
                logging.info('BIOS更新成功')
            elif re.search(SutConfig.Upd.LINUX_MSG_ALL, result):
                logging.info('BIOS更新成功')
            else:
                stylelog.fail('BIOS更新失败')
                logging.info(result)
            time.sleep(3)
            BmcLib.power_reset()
            time.sleep(200)
    elif env.lower() == 'windows':
        if update_mode.lower() == 'normal':
            assert SetUpLib.boot_os_from_bm('windows')
            if bios_mode.lower() == 'latest':
                cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                                       SutConfig.Env.LATEST_BIOS_FILE))
            elif bios_mode.lower() == 'previous':
                cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                                       SutConfig.Env.PREVIOUS_BIOS_FILE))
            elif bios_mode.lower() == 'constant':
                cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "{0} {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                                       SutConfig.Env.CONSTANT_BIOS_FILE))
            else:
                stylelog.fail('bios_mode有误')
                return
            assert re.search(SutConfig.Upd.WINDOWS_MSG_NOR, cmd_result[0]), "Update BIOS in Windows failed."
            logging.info('BIOS更新成功')
            time.sleep(3)
            BmcLib.power_reset()
            time.sleep(5)
        elif update_mode.lower() == 'all':
            assert SetUpLib.boot_os_from_bm('windows')
            if bios_mode.lower() == 'latest':
                cmd_result = SshLib.execute_command_limit(Sut.OS_SSH,
                                                          "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                               SutConfig.Env.LATEST_BIOS_FILE))
            elif bios_mode.lower() == 'previous':
                cmd_result = SshLib.execute_command_limit(Sut.OS_SSH,
                                                          "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                               SutConfig.Env.PREVIOUS_BIOS_FILE))
            elif bios_mode.lower() == 'constant':
                cmd_result = SshLib.execute_command_limit(Sut.OS_SSH,
                                                          "{0} all {1}".format(SutConfig.Upd.WINDOWS_FLASH_TOOL,
                                                                               SutConfig.Env.CONSTANT_BIOS_FILE))
            else:
                stylelog.fail('bios_mode有误')
                return
            assert re.search(SutConfig.Upd.WINDOWS_MSG_ALL, cmd_result[0]), "Update BIOS in Windows failed."
            logging.info('BIOS更新成功')
            BmcLib.power_reset()
            time.sleep(200)
    return True


def _set_psw_option():
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    SetUpLib.enter_menu_change_value_ignore(Key.DOWN,
                                            [{SutConfig.Psw.PSW_LOCK_OPTION: 100}] + SutConfig.Psw.SET_TIME_MONTH, 18)
    if SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5):
        time.sleep(1)
        SetUpLib.send_key(Key.UP)
        time.sleep(1)
        SetUpLib.enter_menu_change_value_ignore(Key.DOWN, [{SutConfig.Psw.CHECK_PSW: 'Enabled'},
                                                           {SutConfig.Psw.PSW_COMPLEXITY: 'Enabled'},
                                                           {SutConfig.Psw.PSW_LEN: 10}, {SutConfig.Psw.PSW_RETRY: 6}],
                                                18)
    time.sleep(1)
    return True


def _is_psw_exist():
    if _go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            return False
    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        return False


def _check_bmc(updated_options):
    count = 0
    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sol info 1')
    if output:
        if any(re.search('Enabled\s*: false', i) for i in output.splitlines()) and SutConfig.Upd.BMC_LINK_OPTION[
            0] in updated_options:
            logging.info('刷新BIOS后，SOL与BMC保持一致')
        elif any(re.search('Enabled\s*: true', i) for i in output.splitlines()) and SutConfig.Upd.BMC_LINK_OPTION[
            1] in updated_options:
            logging.info('刷新BIOS后，SOL与BMC保持一致')
        else:
            stylelog.fail('刷新BIOS后，SOL和BMC不一致')
            count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
    if status == 'always-off' and SutConfig.Upd.BMC_LINK_OPTION[2] in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')

    elif status == 'previous' and SutConfig.Upd.BMC_LINK_OPTION[3] in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')

    elif status == 'always-on' and SutConfig.Upd.BMC_LINK_OPTION[4] in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')

    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options
                                                                                if i in SutConfig.Upd.BMC_LINK_OPTION]))
        count += 1
    if count == 0:
        return True
    else:
        return False


def _compare_difference(part1, part2):
    part1_dif = []
    part2_dif = []
    part1_add = []
    part2_add = []
    max_length = 0
    part1 = sorted(list(set(part1)))
    part2 = sorted(list(set(part2)))
    if sorted(part1) == sorted(part2):
        return True
    else:
        for i in part1:
            max_length = len(i) if len(i) >= max_length else max_length
            found_sign = False
            if i not in part2:
                for j in part2:
                    if re.search("{0}$".format(re.findall('(?:>|])(.+)', i)[0]), j):
                        found_sign = True
                        if i != j:
                            part1_dif.append(i)
                            part2_dif.append(j)
                if not found_sign:
                    part1_add.append(i)
        for i in list(set(part2) - set(part1)):
            if i not in part2_dif:
                part2_add.append(i)
        return part1_dif, part2_dif, part1_add, part2_add, max_length + 5


def _is_reserve_update(updated_options, changed_options, count):
    logging.info(f'刷新后的选项值{updated_options}')
    logging.info(f'刷新前的选项值{changed_options}')
    result = _compare_difference(updated_options, changed_options)
    if result is True:
        logging.info('保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        stylelog.fail('保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for index, i in enumerate(result[0]):
            logging.info('%-{}s'.format(result[4]) % f'刷新后:{i}' + f';刷新前:{result[1][index]}')
        if result[2]:
            logging.info(f'刷新后:{result[2]}')
        if result[3]:
            logging.info(f'刷新前:{result[3]}')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return


def _is_all_update(updated_options, default_options, count, num):
    logging.info(f'刷新后选项值{updated_options}')
    logging.info(f'默认的选项值{default_options}')
    updated_options = [i for i in updated_options if i not in SutConfig.Upd.BMC_LINK_OPTION]
    default_options = [i for i in default_options if i not in SutConfig.Upd.BMC_LINK_OPTION]
    result = _compare_difference(updated_options, default_options)
    if result is True:
        logging.info('完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        elif count is not None:
            stylelog.fail('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
            return
        else:
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
    else:
        stylelog.fail('完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for index, i in enumerate(result[0]):
            logging.info('%-{}s'.format(result[4]) % f'刷新后:{i}' + f';默认值:{result[1][index]}')
        if result[2]:
            logging.info(f'刷新后:{result[2]}')
        if result[3]:
            logging.info(f'默认值:{result[3]}')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        elif count is not None:
            stylelog.fail('刷新BIOS后密码不存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        return


def setup_upgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_NOR, 18, save=True)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('setup', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def setup_upgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_ALL, 18, save=True)
    assert _go_to_setup()
    _update_bios('setup', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def setup_downgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_NOR, 18, save=True)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('setup', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def setup_downgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_ALL, 18, save=True)
    assert _go_to_setup()
    _update_bios('setup', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def dos_upgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18, save=True)
    logging.info("Change boot mode to legacy seccessed.")
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('dos', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def dos_upgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18, save=True)
    logging.info("Change boot mode to legacy seccessed.")
    _update_bios('dos', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def dos_downgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('dos', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def dos_downgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18, save=True)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    _update_bios('dos', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def shell_upgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18, save=True)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('shell', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def shell_upgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18, save=True)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    _update_bios('shell', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def shell_downgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18, save=True)
    logging.info("Enable Shell seccessed.")
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('shell', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def shell_downgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    _update_bios('shell', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def linux_upgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('linux', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def linux_upgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    _update_bios('linux', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def linux_downgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('linux', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def linux_downgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    _update_bios('linux', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def windows_upgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('windows', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def windows_upgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    _update_bios('windows', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def windows_downgrade_normal(bios_mode, change_part):
    assert _change_options(change_part)
    assert _go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    _update_bios('windows', 'normal', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_reserve_update(updated_options, changed_options, count)
    return True


def windows_downgrade_all(bios_mode, change_part):
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    assert _change_options(change_part)
    _update_bios('windows', 'all', bios_mode)
    count = 1 if not _is_psw_exist() else 0
    updated_options = SetUpLib.get_all_option_value()
    num = 1 if not _check_bmc(updated_options) else 0
    if '[60]PasswordLockTime' in updated_options:
        assert _set_psw_option()
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    SetUpLib.clean_buffer()
    assert _is_all_update(updated_options, default_options, count, num)
    return True


def update_bios_setup_normal(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_NOR, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    _update_bios('setup', 'normal', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_setup_all(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_UPDATE_ALL, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    _update_bios('setup', 'all', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_dos_normal(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18, save=True)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    _update_bios('dos', 'normal', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_dos_all(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.SET_DOS, 18, save=True)
    logging.info("Change boot mode to legacy seccessed.")
    time.sleep(5)
    _update_bios('dos', 'all', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_shell_normal(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18, save=True)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    _update_bios('shell', 'normal', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_shell_all(bios_mode):
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18, save=True)
    logging.info("Enable Shell seccessed.")
    time.sleep(5)
    _update_bios('shell', 'all', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_linux_normal(bios_mode):
    _update_bios('linux', 'normal', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_linux_all(bios_mode):
    _update_bios('linux', 'all', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_windows_normal(bios_mode):
    _update_bios('windows', 'normal', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_bios_windows_all(bios_mode):
    _update_bios('windows', 'all', bios_mode)
    assert SetUpLib.boot_to_setup()
    return True


def update_wrong_bios():
    wrong_msg = []
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    if SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_OTHERS, 40, SutConfig.Upd.UPDATE_OTHERS_MSG_SETUP, timeout=15):
        logging.info(f'SetUp下更新其他平台的BIOS，提示{SutConfig.Upd.UPDATE_OTHERS_MSG_SETUP}')
        time.sleep(1)
    else:
        stylelog.fail(f'SetUp下更新其他平台的BIOS，没有提示{SutConfig.Upd.UPDATE_OTHERS_MSG_SETUP}')
        wrong_msg.append(f'SetUp下更新其他平台的BIOS，没有提示{SutConfig.Upd.UPDATE_OTHERS_MSG_SETUP}')
        count += 1
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT)
    if SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_UNSIGNED, 40, SutConfig.Upd.UPDATE_UNSIGNED_MSG_SETUP,
                           timeout=15):
        logging.info(f'SetUp下更新未签名的BIOS，提示{SutConfig.Upd.UPDATE_UNSIGNED_MSG_SETUP}')
        time.sleep(1)
    else:
        if SetUpLib.wait_message_enter(SutConfig.Upd.UPDATE_UNSIGNED_MSG_SETUP, 5):
            logging.info(f'SetUp下更新未签名的BIOS，提示{SutConfig.Upd.UPDATE_UNSIGNED_MSG_SETUP}')
            time.sleep(1)
        else:
            stylelog.fail(f'SetUp下更新未签名的BIOS，没有提示{SutConfig.Upd.UPDATE_UNSIGNED_MSG_SETUP}')
            wrong_msg.append(f'SetUp下更新未签名的BIOS，没有提示{SutConfig.Upd.UPDATE_UNSIGNED_MSG_SETUP}')
            count += 1

    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 300, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 30,
                                       SutConfig.Ipm.UEFI_USB_MSG), "Select Shell failed."
    time.sleep(10)
    logging.info("Shell Boot Successed.")
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('ls')
    if SutConfig.Env.BIOS_FILE not in SetUpLib.get_data(2):
        fs = SetUpLib.get_shell_fs_num()
        SetUpLib.send_data_enter(fs)
        time.sleep(2)
    SetUpLib.send_data_enter('cd {}'.format(SutConfig.Env.BIOS_FILE))
    time.sleep(2)
    SetUpLib.send_data(SutConfig.Upd.SHELL_FLASH_CMD_OTHERS)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Upd.UPDATE_OTHERS_MSG_SHELL, 80):
        logging.info('SHELL 下更新其他平台的BIOS，提示无法更新')
    else:
        stylelog.fail('SHELL下可以更新其他平台的BIOS')
        wrong_msg.append('SHELL下可以更新其他平台的BIOS')
        count += 1
        time.sleep(200)
    time.sleep(5)
    SetUpLib.send_data(SutConfig.Upd.SHELL_FLASH_CMD_UNSIGNED)
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Upd.UPDATE_UNSIGNED_MSG_SHELL, 80):
        logging.info('SHELL 下更新未签名的BIOS，提示无法更新')
    else:
        stylelog.fail('SHELL下可以更新未签名的BIOS')
        wrong_msg.append('SHELL下可以更新未签名的BIOS')
        count += 1
        time.sleep(200)
    assert SetUpLib.boot_os_from_bm()
    _mount_usb_insmod()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Upd.LINUX_FLASH_CMD_OTHERS)
    if re.search(SutConfig.Upd.UPDATE_OTHERS_MSG_LINUX, cmd_result[0]):
        logging.info('Linux下更新其他平台的BIOS，提示无法更新')
    else:
        stylelog.fail('Linux下可以更新其他平台的BIOS')
        wrong_msg.append('Linux下可以更新其他平台的BIOS')
        count += 1
    time.sleep(1)
    cmd_result_unsign = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Upd.LINUX_FLASH_CMD_UNSIGNED)
    if re.search(SutConfig.Upd.UPDATE_UNSIGNED_MSG_LINUX, cmd_result_unsign[0]):
        logging.info('Linux下更新未签名的BIOS，提示无法更新')
    else:
        stylelog.fail('Linux下可以更新未签名的BIOS')
        wrong_msg.append('Linux下可以更新未签名的BIOS')
        count += 1
    print(cmd_result_unsign)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return
