# -*- encoding=utf8 -*-
from ByoTool.Config import *
from ByoTool.BaseLib import *


def go_to_setup(key=SutConfig.Msg.SETUP_KEY, pw_prompt=SutConfig.Tool.POST_PSW_MSG, password='Admin@1'):
    SetUpLib.reboot()
    logging.info("SetUpLib: Booting to setup")
    try_counts = 3
    while try_counts:
        if SutConfig.Env.OEM_SUPPORT:
            BmcLib.enable_serial_normal()
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


def get_random_password():
    return PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=2)


def set_password(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_ADMIN_PSW, 18)
    assert PwdLib.set_admin(password, True)
    return True


def set_password_user(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    assert PwdLib.set_user(password, True)
    return True


def set_password_all(admin, user):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_ADMIN_PSW, 18)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    assert PwdLib.set_user(user, True)
    return True


def del_psw(password):
    go_to_setup(password=password)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_ADMIN_PSW, 18)
    assert PwdLib.del_admin(password, True)
    return True


def del_psw_user(password):
    go_to_setup(password=password)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    assert PwdLib.del_user(password, True)
    return True


def del_psw_all(admin, user):
    go_to_setup(password=admin)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_ADMIN_PSW, 18)
    assert PwdLib.del_admin(admin, True)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    assert PwdLib.del_user(user, True)
    return True


def go_to_setup_del_user(password):
    if go_to_setup(password=password) == [True, True]:
        SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
        PwdLib.del_user(password, True)


def go_to_setup_del_psw(admin='', user=''):
    if go_to_setup(password=admin) == [True, True]:
        SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_ADMIN_PSW, 18)
        PwdLib.del_admin(admin, True)
        if user:
            SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
            PwdLib.del_user(user, True)


def change_options_value():
    SetUpLib.clean_buffer()
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value_ignore(Key.DOWN, SutConfig.Tool.CHANGE_OPTIONS, 25)
    assert SetUpLib.back_to_setup_toppage()
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(3)
    return True


def get_options_value():
    # return SetUpLib.get_all_option_value()
    option_path = SutConfig.Tool.OPTION_PATH
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    SetUpLib.clean_buffer()
    options = []
    trycounts = 12
    while trycounts:
        SetUpLib.clean_buffer()
        time.sleep(1)
        data = SetUpLib.get_data(3, Key.RIGHT)
        options = options + re.findall(r'<.*?> {2,}\w[\w\(\)\. \-/]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/]*? {2}', data)
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
                options = options + re.findall(r'<.*?> {2,}\w[\w\(\)\. \-/]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/]*? {2}',
                                               data)
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
            options = options + re.findall(r'<.*?> {2,}\w[\w\(\)\. \-/]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/]*? {2}', data)
    return [i.replace(' ', '') for i in options]


def change_smbios():
    assert SetUpLib.boot_to_linux_os()
    SetUpLib.linux_mount_usb()
    for key, value in SutConfig.Tool.SMBIOS_CHANGE.items():
        SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYODMI_TYPE_CMD} {key} {value}')
        time.sleep(2)
    return True


def compare_smbios():
    count = 0
    assert SetUpLib.boot_to_linux_os()
    SetUpLib.linux_mount_usb()
    for key, value in SutConfig.Tool.SMBIOS_CHANGE.items():
        if not re.search(value, SshLib.execute_command_limit(Sut.OS_SSH,
                                                             f'{SutConfig.Tool.LINUX_BYODMI_VIEWALL_CMD} {key[0]}')[0]):
            stylelog.fail(f'SMBIOS,type{key},刷新BIOS后改变')
            count += 1
    if count == 0:
        logging.info('SMBIOS刷新BIOS没有改变')
        return True
    else:
        return


def compare_smbios_default():
    count = 0
    assert SetUpLib.boot_to_linux_os()
    SetUpLib.linux_mount_usb()
    for key, value in SutConfig.Tool.SMBIOS_DEFAULT.items():
        if not re.search(value, SshLib.execute_command_limit(Sut.OS_SSH,
                                                             f'{SutConfig.Tool.LINUX_BYODMI_VIEWALL_CMD} {key[0]}')[0]):
            stylelog.fail(f'SMBIOS,type{key},刷新BIOS后没有恢复默认值')
            count += 1
    if count == 0:
        logging.info('SMBIOS刷新BIOS后恢复默认值')
        return True
    else:
        return


def _compare_difference(part1, part2):
    part1_dif = []
    part2_dif = []
    part1_add = []
    part2_add = []
    part1 = sorted(list(set(part1)))
    part2 = sorted(list(set(part2)))
    if sorted(part1) == sorted(part2):
        return True
    else:
        for i in part1:
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
        return part1_dif, part2_dif, part1_add, part2_add


def compare_reserve(changed_options, updated_options):
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(15)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    result = _compare_difference(updated_options, changed_options)
    if result is True:
        return True
    else:
        stylelog.fail('保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for index, i in enumerate(result[0]):
            logging.info(f'刷新后:{i}' + f';刷新前:{result[1][index]}')
        if result[2]:
            logging.info(f'刷新后:{result[2]}')
        if result[3]:
            logging.info(f'刷新前:{result[3]}')
        return False


def _check_bmc(updated_options):
    count = 0
    if re.search(SutConfig.Tool.BMC_LINK_OPTION[0].split('>')[-1], ''.join(updated_options)):
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sol info 1')
        if output:
            if any(re.search('Enabled\s*: false', i) for i in output.splitlines()) and SutConfig.Tool.BMC_LINK_OPTION[
                0] in updated_options:
                logging.info('刷新BIOS后，SOL与BMC保持一致')
            elif any(re.search('Enabled\s*: true', i) for i in output.splitlines()) and SutConfig.Tool.BMC_LINK_OPTION[
                1] in updated_options:
                logging.info('刷新BIOS后，SOL与BMC保持一致')
            else:
                stylelog.fail('刷新BIOS后，SOL和BMC不一致')
                count += 1
    if re.search(SutConfig.Tool.BMC_LINK_OPTION[-1].split('>')[-1], ''.join(updated_options)):
        arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
        p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        stdoutput = str(stdoutput).replace("'", '')
        status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
        if status == 'always-off' and SutConfig.Tool.BMC_LINK_OPTION[2] in updated_options:
            logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')

        elif status == 'previous' and SutConfig.Tool.BMC_LINK_OPTION[3] in updated_options:
            logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')

        elif status == 'always-on' and SutConfig.Tool.BMC_LINK_OPTION[4] in updated_options:
            logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
        else:
            stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options
                                                                                    if
                                                                                    i in SutConfig.Tool.BMC_LINK_OPTION]))
            count += 1
    if count == 0:
        return True
    else:
        return False


def compare_all(part):
    bmc_result = _check_bmc(part)
    count = 0
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(15)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    default = SutConfig.Tool.DEFAULT_OPTION_VALUE
    updated_options = [i for i in part if i not in SutConfig.Tool.BMC_LINK_OPTION]
    default_options = [i for i in default if i not in SutConfig.Tool.BMC_LINK_OPTION]
    result = _compare_difference(updated_options, default_options)
    if result is True:
        logging.info('完全刷新，刷新BIOS后选项变为默认值')
        if bmc_result is False:
            stylelog.fail('完全刷新，刷新BIOS后BMC相关选项异常')
            count += 1
    else:
        stylelog.fail('完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for index, i in enumerate(result[0]):
            logging.info(f'刷新后:{i}' + f';默认值:{result[1][index]}')
        if result[2]:
            logging.info(f'刷新后:{result[2]}')
        if result[3]:
            logging.info(f'默认值:{result[3]}')
        if bmc_result is False:
            stylelog.fail('完全刷新，刷新BIOS后BMC相关选项异常')
            count += 1
        count += 1
    return True if count == 0 else False


@core.test_case(('0000', '[TC0000]Boot to windows os', '启动到windows系统，初始化ssh'))
def flash_tool_0000():
    """
    Name:   启动到windows系统，初始化ssh
    """
    try:
        assert SetUpLib.boot_to_windows_os()
        SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'shutdown -r -t 0')
        time.sleep(15)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0001', '[TC0001]SHELL,Check Flash Tool Version,Help Message', 'Shell下检查Flash工具版本，帮助信息'))
def flash_tool_0001():
    """
    Name:   Shell下检查Flash工具版本，帮助信息

    Steps:  1.Shell下检查Flash工具版本，帮助信息

    Result: 1.工具版本，帮助信息显示正确

    """
    try:
        wrong_msg = []
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_TOOL_VERSION_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        if re.search(SutConfig.Tool.SHELL_TOOL_VERSION_CONFIRM_MSG, data):
            logging.info(data)
            logging.info('Flash Tool 版本验证成功')
        else:
            stylelog.fail(data)
            stylelog.fail('Flash Tool 版本验证失败')
            wrong_msg.append(data + 'Flash Tool 版本验证失败')
            count += 1
        SetUpLib.send_data(SutConfig.Tool.SHELL_TOOL_HELP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data_h = SetUpLib.get_data(2)
        if re.search(SutConfig.Tool.SHELL_TOOL_HELP_CONFIRM_MSG, data_h):
            logging.info(data_h)
            logging.info('Flash Tool 帮助信息验证成功')
        else:
            stylelog.fail(data_h)
            stylelog.fail('Flash Tool 帮助信息验证失败')
            wrong_msg.append(data_h + 'Flash Tool 帮助信息验证失败')
            count += 1
        if count == 0:
            return core.Status.Pass
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0002', '[TC0002]Shell保留升级BIOS', 'Shell保留升级BIOS'))
def flash_tool_0002():
    """
    Name:   Shell保留升级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.SetUp下读取修改后的选项值
            4.Shell下保留升级刷新BIOS
            5.刷新BIOS后进入SetUp读取刷新后的值
            6.对比刷新BIOS前后选项值，SMBIOS值

    Result: 4.刷新BIOS成功
            6.刷新前后选项的值相同，SMBIOS值相同
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(f'{SutConfig.Tool.SHELL_FLASH_CMD_LATEST}')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR, 300):
            logging.info('BIOS更新成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Shell下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留配置刷新，刷新BIOS后SMBIOS没有改变')
            else:
                stylelog.fail('Shell下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0003', '[TC0003]Shell保留降级BIOS', 'Shell保留降级BIOS'))
def flash_tool_0003():
    """
    Name:   Shell保留降级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.SetUp下读取修改后的选项值
            4.Shell下保留降级刷新BIOS
            5.刷新BIOS后进入SetUp读取刷新后的值
            6.对比刷新BIOS前后选项值，SMBIOS值

    Result: 4.刷新BIOS成功
            6.刷新前后选项的值相同，SMBIOS值相同
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(f'{SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS}')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR, 300):
            logging.info('BIOS更新成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Shell下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留配置刷新，刷新BIOS后SMBIOS没有改变')
            else:
                stylelog.fail('Shell下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0004', '[TC0004]Shell完全刷新升级BIOS', 'Shell完全刷新升级BIOS'))
def flash_tool_0004():
    """
    Name:   Shell完全刷新升级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell完全刷新升级BIOS
            4.刷新BIOS后进入SetUp读取刷新后的值
            5.对比刷新BIOS后选项值和默认的选项值，SMBIOS值

    Result: 3.刷新BIOS成功
            5.刷新后选项的值和默认值相同，SMBIOS值恢复默认
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(f'{SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL}')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL, 300):
            logging.info("Update BIOS in Shell successed.")
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('SHELL下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下完全刷新，刷新BIOS后SMBIOS变为默认值')
            else:
                stylelog.fail('SHELL下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0005', '[TC0005]Shell完全刷新降级BIOS', 'Shell完全刷新降级BIOS'))
def flash_tool_0005():
    """
    Name:   Shell完全刷新降级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell完全刷新降级BIOS
            4.刷新BIOS后进入SetUp读取刷新后的值
            5.对比刷新BIOS后选项值和默认的选项值，SMBIOS值

    Result: 3.刷新BIOS成功
            5.刷新后选项的值和默认值相同，SMBIOS值恢复默认
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(f'{SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL}')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL, 300):
            logging.info("Update BIOS in Shell successed.")
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('SHELL下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('SHELL下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0006', '[TC0006]Shell下备份BIOS', 'Shell下备份BIOS'))
def flash_tool_0006():
    """
    Name:   Shell下备份BIOS

    Steps:  1.Shell下备份BIOS
            2.Shell下保留配置刷新同时备份BIOS

    Result: 1.成功生成备份文件
            2.保留配置刷新BIOS成功，成功生成备份文件
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_SUC_MSG, 120):
            logging.info('BIOS备份成功')
        else:
            stylelog.fail('BIOS 备份失败')
            wrong_msg.append('BIOS 备份失败')
            count += 1

        time.sleep(3)
        SetUpLib.send_data('ls')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('备份命令执行成功，但没有生成备份文件')
            wrong_msg.append('备份命令执行成功，但没有生成备份文件')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UPDATE_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('刷新BIOS同时备份BIOS成功')
        time.sleep(2)
        SetUpLib.send_data('ls')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('刷新同时备份BIOS，但没有生成备份文件')
            wrong_msg.append('刷新同时备份BIOS，但没有生成备份文件')
            count += 1
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Shell下保留配置刷新同时备份BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Shell下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS改变')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0007', '[TC0007]Shell下只保留Setup,升级更新BIOS', 'Shell下只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0007():
    """
    Name:   Shell下只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0008', '[TC0008]Shell下只保留Setup,降级更新BIOS', 'Shell下只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0008():
    """
    Name:   Shell下只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0009', '[TC0009]Shell下只保留SMBIOS,升级更新BIOS，SetUp恢复默认', 'Shell下只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0009():
    """
    Name:   Shell下只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0010', '[TC00010]Shell下只保留SMBIOS,降级更新BIOS，SetUp恢复默认', 'Shell下只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0010():
    """
    Name:   Shell下只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0011', '[TC0011]Shell Update OA3', 'Shell Update OA3'))
def flash_tool_0011():
    return core.Status.Skip


@core.test_case(('0012', '[TC0012]Shell下工具锁住，BIOS刷新失败测试', 'Shell下工具锁住，BIOS刷新失败测试'))
def flash_tool_0012():
    """
    Name:   Shell下工具锁住，BIOS刷新失败测试

    Steps:  1.Shell下锁住Flash工具
            2.检查工具状态
            3.检查是否可以保留更新BIOS，完全刷新BIOS
            4.检查是否可以更新同时备份BIOS
            5.检查是否可以只保留SetUp更新BIOS
            6.检查是否可以只保留SMBIOS更新BIOS
            7.检查是否可以更新OA3文件
            8.检查是否可以备份BIOS
            9.解锁Flash工具
            10.检查解锁后的工具状态

    Result: 1.成功锁住
            2.工具状态为锁住
            3/4/5/6/7.不可以
            8.可以备份BIOS
            9.成功解锁
            10.工具状态为解锁
    """

    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 5):
            logging.info(f'BIOS 锁住成功')
        else:
            stylelog.fail(f'BIOS 锁住没有提示{SutConfig.Tool.SHELL_LOCK_BIOS_MSG}')
            wrong_msg.append(f'BIOS 锁住没有提示{SutConfig.Tool.SHELL_LOCK_BIOS_MSG}')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_STATUS_MSG, 5):
            logging.info(f'BIOS 锁住,BIOS 状态为{SutConfig.Tool.SHELL_LOCK_STATUS_MSG}')
        else:
            stylelog.fail(f'BIOS 锁住,BIOS 状态不是{SutConfig.Tool.SHELL_LOCK_STATUS_MSG}')
            wrong_msg.append(f'BIOS 锁住,BIOS 状态不是{SutConfig.Tool.SHELL_LOCK_STATUS_MSG}')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_MSG, 5):
            logging.info('BIOS 锁住后，无法保留更新BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以保留更新BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以保留更新BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_MSG, 5):
            logging.info('BIOS 锁住后，无法完全更新BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以完全更新BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以完全更新BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UPDATE_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_MSG, 5):
            logging.info('BIOS 锁住后，无法更新同时备份BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新同时备份BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以更新同时备份BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_MSG, 5):
            logging.info('BIOS 锁住后，无法更新BIOS，只保留SetUp配置')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新BIOS，只保留SetUp配置')
            wrong_msg.append('BIOS 锁住后，仍可以更新BIOS，只保留SetUp配置')
            count += 1
            time.sleep(200)
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_MSG, 5):
            logging.info('BIOS 锁住后，无法更新BIOS，只保留SMBIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新BIOS，只保留SMBIOS')
            wrong_msg.append('BIOS 锁住后，仍可以更新BIOS，只保留SMBIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UPDATE_OA3_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_MSG, 5):
            logging.info('BIOS 锁住后，无法更新OA3文件')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新OA3文件')
            wrong_msg.append('BIOS 锁住后，仍可以更新OA3文件')
            count += 1
            time.sleep(200)
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_SUC_MSG, 120):
            logging.info('BIOS锁住后，可以备份BIOS')
            time.sleep(1)
            SetUpLib.send_data('ls')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
                logging.info('成功生成备份文件')
                time.sleep(1)
                SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('BIOS锁住后可以备份文件，但没有生成备份文件')
                wrong_msg.append('BIOS锁住后可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('BIOS锁住后，无法备份BIOS')
            wrong_msg.append('BIOS锁住后，无法备份BIOS')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 5):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS 解锁失败')
            wrong_msg.append('BIOS 解锁失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG, 5):
            logging.info(f'BIOS解锁，BIOS状态为{SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG}')
        else:
            stylelog.fail(f'BIOS解锁，BIOS状态不是{SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG}')
            wrong_msg.append(f'BIOS解锁，BIOS状态不是{SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG}')
            count += 1
        time.sleep(2)

        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0013', '[TC0013]Shell下解锁后保留刷新BIOS', 'Shell下解锁后保留刷新BIOS'))
def flash_tool_0013():
    """
    Name:   Shell下解锁后保留刷新BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下锁住工具，解锁工具
            4.保留刷新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值保留，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 5):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 5):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        SetUpLib.send_data(f'{SutConfig.Tool.SHELL_FLASH_CMD_LATEST}')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR, 300):
            logging.info('BIOS更新成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()

        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Shell下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Shell下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:

            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0014', '[TC0014]Shell下解锁后完全刷新BIOS', 'Shell下解锁后完全刷新BIOS'))
def flash_tool_0014():
    """
    Name:   Shell下解锁后完全刷新BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下锁住工具，解锁工具
            4.完全刷新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值恢复默认值，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 5):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 5):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        SetUpLib.send_data(f'{SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL}')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL, 300):
            logging.info("Update BIOS in Shell successed.")
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('SHELL下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('SHELL下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0015', '[TC0015]Shell下解锁BIOS，刷新同时备份BIOS', 'Shell下解锁BIOS，刷新同时备份BIOS'))
def flash_tool_0015():
    """
    Name:   Shell下解锁BIOS，刷新同时备份BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下锁住工具，解锁工具
            4.刷新同时备份BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS，备份BIOS
            5.选项值保留，SMBIOS保留
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 5):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 5):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UPDATE_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('刷新BIOS同时备份BIOS成功')
        time.sleep(2)
        SetUpLib.send_data('ls')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('刷新同时备份BIOS，但没有生成备份文件')
            wrong_msg.append('刷新同时备份BIOS，但没有生成备份文件')
            count += 1
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Shell下保留配置刷新同时备份BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Shell下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS改变')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0016', '[TC0016]Shell下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认', 'Shell下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认'))
def flash_tool_0016():
    """
    Name:   Shell下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下锁住工具，解锁工具
            4.只保留Setup,更新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 5):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 5):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0017', '[TC0017]Shell下解锁BIOS，只保留SMBIOS,更新BIOS', 'Shell下解锁BIOS，只保留SMBIOS,更新BIOS，SetUp恢复默认'))
def flash_tool_0017():
    """
    Name:   Shell下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下锁住工具，解锁工具
            4.只保留SMBIOS,更新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 5):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 5):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0018', '[TC0018]Shell下解锁BIOS，更新OA3文件', 'Shell下解锁BIOS，更新OA3文件'))
def flash_tool_0018():
    return core.Status.Skip


@core.test_case(('0019', '[TC0019]Shell下设置管理员密码，保留升级BIOS', 'Shell下设置管理员密码，保留升级BIOS'))
def flash_tool_0019():
    """
    Name:   Shell下设置管理员密码，保留升级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下保留升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Shell下保留刷新BIOS，刷新后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Shell下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
    except Exception as e:
        logging.error(e)

        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0020', '[TC0020]Shell下设置管理员密码，保留降级BIOS', 'Shell下设置管理员密码，保留降级BIOS'))
def flash_tool_0020():
    """
    Name:   Shell下设置管理员密码，保留降级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下保留降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Shell下保留刷新BIOS，刷新后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Shell下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0021', '[TC0021]Shell下设置管理员密码，完全升级BIOS', 'Shell下设置管理员密码，完全升级BIOS'))
def flash_tool_0021():
    """
    Name:   Shell下设置管理员密码，完全升级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下完全升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Shell下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('Shell下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Shell下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0022', '[TC0022]Shell下设置管理员密码，完全降级BIOS', 'Shell下设置管理员密码，完全降级BIOS'))
def flash_tool_0022():
    """
    Name:   Shell下设置管理员密码，完全降级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下完全降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Shell下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('Shell下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Shell下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0023', '[TC0023]Shell下设置管理员密码只保留Setup,升级更新BIOS', 'Shell下设置管理员只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0023():
    """
    Name:   Shell下设置管理员只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)

        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        result_psw = go_to_setup(password=password)

        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Shell下只保留Setup,刷新BIOS后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Shell下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0024', '[TC0024]Shell下设置管理员密码只保留Setup,降级更新BIOS', 'Shell下设置管理员密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0024():
    """
    Name:   Shell下设置管理员密码只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Shell下只保留Setup,刷新BIOS后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Shell下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0025', '[TC0025]Shell下设置管理员密码只保留SMBIOS,升级更新BIOS', 'Shell下设置管理员密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0025():
    """
    Name:   Shell下设置管理员密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Shell下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Shell下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0026', '[TC0026]Shell下设置管理员密码只保留SMBIOS,降级更新BIOS', 'Shell下设置管理员密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0026():
    """
    Name:   Shell下设置管理员密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Shell下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Shell下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0027', '[TC0027]Shell下设置管理员密码,更新OA3', 'Shell下设置管理员密码,更新OA3'))
def flash_tool_0027():
    return core.Status.Skip


@core.test_case(('0028', '[TC0028]Shell下设置管理员密码,备份BIOS,锁住BIOS测试', 'Shell下设置管理员密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0028():
    """
    Name:   Shell下设置管理员密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置管理员密码
            2.Shell下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输错密码提示密码错误
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password(password)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if not SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 3):
            logging.info('Shell下，设置管理员密码，备份BIOS不需要输入密码')
        else:
            stylelog.fail('Shell下，设置管理员密码，备份BIOS仍需要输入密码')
            count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(password)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_SUC_MSG, 120):
            logging.info('Shell下，设置管理员密码，备份BIOS成功')
            time.sleep(1)
            SetUpLib.send_data('ls')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
                logging.info('成功生成备份文件')
                time.sleep(1)
                SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('Shell下，设置管理员密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('Shell下，设置管理员密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('Shell下设置管理员密码，锁住BIOS需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter('111111')
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_FAIL_MSG, 5):
                logging.info('输入错误密码，锁住BIOS失败')
            else:
                stylelog.fail('输入错误密码，仍能锁住BIOS')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
            time.sleep(3)
            SetUpLib.send_data_enter(password)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 10):
                logging.info('成功锁住BIOS')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_STATUS_MSG, 5):
                    logging.info('锁住BIOS，状态为锁住')
                else:
                    stylelog.fail('锁住BIOS，状态不是锁住')
                    count += 1
            else:
                stylelog.fail('锁住BIOS失败')
                count += 1
        else:
            stylelog.fail(('Shell下设置管理员密码，锁住BIOS不需要输入密码'))
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('Shell下设置管理员密码，解锁BIOS需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter('111111')
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_FAIL_MSG, 5):
                logging.info('输入错误密码，锁住BIOS失败')
            else:
                stylelog.fail('输入错误密码，仍能锁住BIOS')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
            time.sleep(3)
            SetUpLib.send_data_enter(password)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 10):
                logging.info('成功解锁BIOS')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG, 5):
                    logging.info('解锁BIOS，状态为解锁')
                else:
                    stylelog.fail('解锁BIOS，状态不是解锁')
                    count += 1
            else:
                stylelog.fail('解锁BIOS失败')
                count += 1
        else:
            stylelog.fail(('Shell下设置管理员密码，解锁BIOS不需要输入密码'))
            count += 1
        go_to_setup(password=password)
        del_psw(password)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0029', '[TC0029]Shell下设置用户密码，保留升级BIOS', 'Shell下设置用户密码，保留升级BIOS'))
def flash_tool_0029():
    """
    Name:   Shell下设置用户密码，保留升级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下保留升级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Shell下保留刷新BIOS，刷新后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Shell下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0030', '[TC0030]Shell下设置用户密码，保留降级BIOS', 'Shell下设置用户密码，保留降级BIOS'))
def flash_tool_0030():
    """
    Name:   Shell下设置用户密码，保留降级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下保留降级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Shell下保留刷新BIOS，刷新后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Shell下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0031', '[TC0031]Shell下设置用户密码，完全升级BIOS', 'Shell下设置用户密码，完全升级BIOS'))
def flash_tool_0031():
    """
    Name:   Shell下设置用户密码，完全升级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下完全升级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Shell下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('Shell下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Shell下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0032', '[TC0032]Shell下设置用户密码，完全降级BIOS', 'Shell下设置用户密码，完全降级BIOS'))
def flash_tool_0032():
    """
    Name:   Shell下设置用户密码，完全降级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下完全降级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Shell下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('Shell下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Shell下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0033', '[TC0033]Shell下设置用户密码只保留Setup,升级更新BIOS', 'Shell下设置用户只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0033():
    """
    Name:   Shell下设置用户只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)

        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        result_psw = go_to_setup(password=password)

        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Shell下只保留Setup,刷新BIOS后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Shell下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0034', '[TC0034]Shell下设置用户密码只保留Setup,降级更新BIOS', 'Shell下设置用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0034():
    """
    Name:   Shell下设置用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Shell下只保留Setup,刷新BIOS后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Shell下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0035', '[TC0035]Shell下设置用户密码只保留SMBIOS,升级更新BIOS', 'Shell下设置用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0035():
    """
    Name:   Shell下设置用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Shell下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Shell下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0036', '[TC0036]Shell下设置用户密码只保留SMBIOS,降级更新BIOS', 'Shell下设置用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0036():
    """
    Name:   Shell下设置用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """

    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data('111111')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入错误密码，提示密码错误')
        else:
            stylelog.fail('输入错误密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Shell下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Shell下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0037', '[TC0037]Shell下设置用户密码,更新OA3', 'Shell下设置用户密码,更新OA3'))
def flash_tool_0037():
    return core.Status.Skip


@core.test_case(('0038', '[TC0038]Shell下设置用户密码,备份BIOS,锁住BIOS测试', 'Shell下设置用户密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0038():
    """
    Name:   Shell下设置用户密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置用户密码
            2.Shell下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输错密码提示密码错误
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if not SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 3):
            logging.info('Shell下，设置用户密码，备份BIOS不需要输入密码')
        else:
            stylelog.fail('Shell下，设置用户密码，备份BIOS仍需要输入密码')
            count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(password)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_SUC_MSG, 120):
            logging.info('Shell下，设置用户密码，备份BIOS成功')
            time.sleep(1)
            SetUpLib.send_data('ls')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
                logging.info('成功生成备份文件')
                time.sleep(1)
                SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('Shell下，设置用户密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('Shell下，设置用户密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('Shell下设置用户密码，锁住BIOS需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter('111111')
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_FAIL_MSG, 5):
                logging.info('输入错误密码，锁住BIOS失败')
            else:
                stylelog.fail('输入错误密码，仍能锁住BIOS')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
            time.sleep(3)
            SetUpLib.send_data_enter(password)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 10):
                logging.info('成功锁住BIOS')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_STATUS_MSG, 5):
                    logging.info('锁住BIOS，状态为锁住')
                else:
                    stylelog.fail('锁住BIOS，状态不是锁住')
                    count += 1
            else:
                stylelog.fail('锁住BIOS失败')
                count += 1
        else:
            stylelog.fail('Shell下设置用户密码，锁住BIOS不需要输入密码')
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('Shell下设置用户密码，解锁BIOS需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter('111111')
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_FAIL_MSG, 5):
                logging.info('输入错误密码，锁住BIOS失败')
            else:
                stylelog.fail('输入错误密码，仍能锁住BIOS')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
            time.sleep(3)
            SetUpLib.send_data_enter(password)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 10):
                logging.info('成功解锁BIOS')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG, 5):
                    logging.info('解锁BIOS，状态为解锁')
                else:
                    stylelog.fail('解锁BIOS，状态不是解锁')
                    count += 1
            else:
                stylelog.fail('解锁BIOS失败')
                count += 1
        else:
            stylelog.fail('Shell下设置用户密码，解锁BIOS不需要输入密码')
            count += 1
        go_to_setup(password=password)
        del_psw_user(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0039', '[TC0039]Shell下同时设置管理员密码，用户密码，保留升级BIOS', 'Shell下同时设置管理员，用户密码，保留升级BIOS'))
def flash_tool_0039():
    """
    Name:   Shell下同时设置管理员，用户密码，保留升级BIOS

    Steps:  1.SetUp下设置管理员密码，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下保留升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """

    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('输入管理员密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Shell下保留刷新BIOS，刷新后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Shell下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0040', '[TC0040]Shell下同时设置管理员密码，用户密码，保留降级BIOS', 'Shell下同时设置管理员密码，用户密码，保留降级BIOS'))
def flash_tool_0040():
    """
    Name:   Shell下同时设置管理员密码，用户密码，保留降级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下保留降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('输入管理员密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Shell下保留刷新BIOS，刷新后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Shell下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Shell下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0041', '[TC0041]Shell下同时设置管理员密码，用户密码，完全升级BIOS', 'Shell下同时设置管理员密码，用户密码，完全升级BIOS'))
def flash_tool_0041():
    """
    Name:   Shell下设置管理员，用户密码，完全升级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下完全升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_LATEST_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL):
            logging.info('输入管理员密码，BIOS更新完成')
        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Shell下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('Shell下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Shell下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        go_to_setup_del_psw(admin, user)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0042', '[TC0042]Shell下同时设置管理员密码，用户密码，完全降级BIOS', 'Shell下同时设置管理员密码，用户密码，完全降级BIOS'))
def flash_tool_0042():
    """
    Name:   Shell下同时设置管理员密码，用户密码，完全降级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下完全降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """

    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_FLASH_CMD_PREVIOUS_ALL)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_ALL):
            logging.info('输入管理员密码，BIOS更新完成')
        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Shell下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Shell下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('Shell下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Shell下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0043', '[TC0043]Shell下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS', 'Shell下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0043():
    """
    Name:   Shell下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """

    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)

        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Shell下只保留Setup,刷新BIOS后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Shell下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0044', '[TC0044]Shell下同时设置管理员密码，用户密码,只保留Setup,降级更新BIOS', 'Shell下同时设置管理员密码，用户密码,只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0044():
    """
    Name:   Shell下同时设置管理员密码，用户密码,只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVNVM_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Shell下只保留Setup,刷新BIOS后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Shell下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Shell下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Shell下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Shell下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:

            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0045', '[TC0045]Shell下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS', 'Shell下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0045():
    """
    Name:   Shell下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """

    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_LATEST)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Shell下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Shell下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0046', '[TC0046]Shell下同时设置管理员密码，用户密码,只保留SMBIOS,降级更新BIOS', 'Shell下同时设置管理员密码，用户密码,只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0046():
    """
    Name:   Shell下同时设置管理员密码，用户密码,只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Shell下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """

    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
            logging.info('输入用户密码，提示密码错误')
        else:
            stylelog.fail('输入用户密码，没有提示密码错误')
            return
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_RESVSMBIOS_CMD_PREVIOUS)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，刷新BIO时要求输入BIOS密码')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时没有要求输入BIOS密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_MSG_NOR):
            logging.info('Shell下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Shell下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Shell下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('SHELL下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('SHELL下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0047', '[TC0047]Shell下同时设置管理员密码，用户密码,更新OA3', 'Shell下同时设置管理员密码，用户密码,更新OA3'))
def flash_tool_0047():
    return core.Status.Skip


@core.test_case(('0048', '[TC0048]Shell下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试', 'Shell下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0048():
    """
    Name:   Shell下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置管理员密码
            2.Shell下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输入用户密码提示密码错误
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_all(admin, user)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data(SutConfig.Tool.SHELL_BACKUP_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if not SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 3):
            logging.info('Shell下，同时设置管理员密码，用户密码，备份BIOS不需要输入密码')
        else:
            stylelog.fail('Shell下，同时设置管理员密码，用户密码，备份BIOS仍需要输入密码')
            count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_SUC_MSG, 120):
            logging.info('Shell下，同时设置管理员密码，用户密码，备份BIOS成功')
            time.sleep(1)
            SetUpLib.send_data('ls')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1], 10):
                logging.info('成功生成备份文件')
                time.sleep(1)
                SetUpLib.send_data_enter(f"rm {SutConfig.Tool.SHELL_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('Shell下，同时设置管理员密码，用户密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('Shell下，同时设置管理员密码，用户密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('Shell下同时设置管理员密码，用户密码，锁住BIOS需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_FAIL_MSG, 5):
                logging.info('输入用户密码，锁住BIOS失败')
            else:
                stylelog.fail('输入用户密码，仍能锁住BIOS')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_BIOS_UPDATE_CMD)
            time.sleep(3)
            SetUpLib.send_data_enter(admin)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_BIOS_MSG, 10):
                logging.info('成功锁住BIOS')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_LOCK_STATUS_MSG, 5):
                    logging.info('锁住BIOS，状态为锁住')
                else:
                    stylelog.fail('锁住BIOS，状态不是锁住')
                    count += 1
            else:
                stylelog.fail('锁住BIOS失败')
                count += 1
        else:
            stylelog.fail('Shell下同时设置管理员密码，用户密码，锁住BIOS不需要输入密码')
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('Shell下同时设置管理员密码，用户密码，解锁BIOS需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_FAIL_MSG, 5):
                logging.info('输入用户密码，锁住BIOS失败')
            else:
                stylelog.fail('输入用户密码，仍能锁住BIOS')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_UNLOCK_BIOS_UPDATE_CMD)
            time.sleep(3)
            SetUpLib.send_data_enter(admin)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_BIOS_MSG, 10):
                logging.info('成功解锁BIOS')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_LOCK_STATUS_CMD)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_UNLOCK_STATUS_MSG, 5):
                    logging.info('解锁BIOS，状态为解锁')
                else:
                    stylelog.fail('解锁BIOS，状态不是解锁')
                    count += 1
            else:
                stylelog.fail('解锁BIOS失败')
                count += 1
        else:
            stylelog.fail('Shell下同时设置管理员密码，用户密码，解锁BIOS不需要输入密码')
            count += 1
        go_to_setup(password=admin)
        del_psw_all(admin, user)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0049', '[TC0049]Shell下设置管理员密码,Flash 工具清除密码测试', 'Shell下设置管理员密码,Flash 工具清除密码测试'))
def flash_tool_0049():
    """
    Name:   Shell下设置管理员密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置管理员密码
            2.Shell下工具清除密码

    Result: 2.输入错误密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password(password)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_CLEAN_PSW_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置管理员密码，工具清除密码，需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter('111111')
            if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
                logging.info('输入错误密码，提示密码错误')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_CLEAN_PSW_CMD)
                time.sleep(3)
                SetUpLib.send_data_enter(password)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_CLEAN_PSW_MSG, 5):
                    logging.info('输入正确密码，成功清除密码')
                else:
                    stylelog.fail('输入正确密码，没有清除密码')
                    count += 1
            else:
                stylelog.fail('输入错误密码，没有提示密码错误')
                count += 1
        else:
            stylelog.fail('设置管理员密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=password) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0050', '[TC0050]Shell下设置用户密码,Flash 工具清除密码测试', 'Shell下设置用户密码,Flash 工具清除密码测试'))
def flash_tool_0050():
    """
    Name:   Shell下设置用户密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置用户密码
            2.Shell下工具清除密码

    Result: 2.输入错误密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_CLEAN_PSW_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('设置用户密码，工具清除密码，需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter('111111')
            if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
                logging.info('输入错误密码，提示密码错误')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_CLEAN_PSW_CMD)
                time.sleep(3)
                SetUpLib.send_data_enter(password)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_CLEAN_PSW_MSG, 5):
                    logging.info('输入正确密码，成功清除密码')
                else:
                    stylelog.fail('输入正确密码，没有清除密码')
                    count += 1
            else:
                stylelog.fail('输入错误密码，没有提示密码错误')
                count += 1
        else:
            stylelog.fail('设置用户密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=password) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw_user(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0051', '[TC0051]Shell下同时设置管理员密码，用户密码,Flash 工具清除密码测试', 'Shell下同时设置管理员密码，用户密码,Flash 工具清除密码测试'))
def flash_tool_0051():
    """
    Name:   Shell下设置管理员，用户密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置管理员，用户密码
            2.Shell下工具清除密码

    Result: 2.输入用户密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_all(admin, user)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_CLEAN_PSW_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.TOOL_PASSWORD_MSG, 5):
            logging.info('同时设置管理员密码，用户密码，工具清除密码，需要输入密码')
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            if SetUpLib.wait_message(SutConfig.Tool.WRONG_PSW_MSG, 5):
                logging.info('输入用户密码，提示密码错误')
                time.sleep(1)
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_CLEAN_PSW_CMD)
                time.sleep(3)
                SetUpLib.send_data_enter(admin)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_CLEAN_PSW_MSG, 5):
                    logging.info('输入正确密码，成功清除密码')
                else:
                    stylelog.fail('输入正确密码，没有清除密码')
                    count += 1
            else:
                stylelog.fail('输入错误密码，没有提示密码错误')
                count += 1
        else:
            stylelog.fail('设置用户密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=admin) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw_all(admin, user)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        go_to_setup_del_psw(admin, user)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0052', '[TC0052]Shell下负面测试(错误BIOS,错误OA3,错误命令参数)', 'Shell下负面测试(错误BIOS,错误OA3,错误命令参数)'))
def flash_tool_0052():
    """
    Name:   Shell下负面测试(错误BIOS,错误OA3,错误命令参数)

    Steps:  1.Shell下工具不输入参数
            2.输入错误参数
            3.更新其他平台BIOS
            4.更新为签名的BIOS

    Result: 1/2.提示信息显示正确
            3/4.无法更新
    """
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_EMPTY_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_INPUT_ERR_MSG, 5):
            logging.info('Shell 工具不输入参数，提示输入错误')
        else:
            stylelog.fail('Shell 工具不输入参数，没有提示输入错误')
            count += 1
            time.sleep(200)
        time.sleep(2)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_ERROR_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_INPUT_ERR_MSG, 5):
            logging.info('Shell 工具输入错误参数，提示输入错误')
        else:
            stylelog.fail('Shell 工具输入错误参数，没有提示输入错误')
            count += 1
            time.sleep(200)
        time.sleep(2)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_FLASH_CMD_OTHERS)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UPDATE_OTHERS_MSG, 60):
            logging.info('SHELL 下更新其他平台的BIOS，提示无法更新')
            time.sleep(2)
        else:
            stylelog.fail('SHELL下可以更新其他平台的BIOS')
            count += 1
            time.sleep(200)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_FLASH_CMD_UNSIGNED)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_UPDATE_UNSIGNED_MSG, 60):
            logging.info('SHELL 下更新未签名的BIOS，提示无法更新')
        else:
            stylelog.fail('SHELL下可以更新未签名的BIOS')
            count += 1
            time.sleep(200)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0101', '[TC0101]Linux,Check Flash Tool Version,Help Message', 'Linux下检查Flash工具版本，帮助信息'))
def flash_tool_0101():
    """

    Name:   Linux下检查Flash工具版本，帮助信息

    Steps:  1.Linux下检查Flash工具版本，帮助信息

    Result: 1.工具版本，帮助信息显示正确

    """
    try:
        wrong_msg = []
        count = 0
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        result = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_TOOL_VERSION_CMD)
        if re.search(SutConfig.Tool.LINUX_TOOL_VERSION_CONFIRM_MSG, result[0]):
            logging.info(result)
            logging.info('Linux下 Flash Tool版本验证成功')
        else:
            stylelog.fail(result)
            stylelog.fail('Linux下 Flash Tool版本验证失败')
            wrong_msg.append(result + 'Flash Tool 版本验证失败')
            count += 1
        time.sleep(1)
        result_h = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_TOOL_HELP_CMD)
        if re.search(SutConfig.Tool.LINUX_TOOL_HELP_CONFIRM_MSG, result_h[0]):
            logging.info(result_h)
            logging.info('Linux下 Flash Tool帮助信息验证成功')
        else:
            stylelog.fail(result_h)
            stylelog.fail('Linux下 Flash Tool帮助信息验证失败')
            wrong_msg.append(result_h + 'Flash Tool 帮助信息验证失败')
            count += 1
        if count == 0:
            return core.Status.Pass
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0102', '[TC0102]Linux保留升级BIOS', 'Linux保留升级BIOS'))
def flash_tool_0102():
    """

    Name:   Linux保留升级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.SetUp下读取修改后的选项值
            4.Linux下保留升级刷新BIOS
            5.刷新BIOS后进入SetUp读取刷新后的值
            6.对比刷新BIOS前后选项值，SMBIOS值

    Result: 4.刷新BIOS成功
            6.刷新前后选项的值相同，SMBIOS值相同
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST)
        logging.debug(output)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR, output[0]):
            logging.info('Linux下BIOS更新成功')
        else:
            stylelog.fail('Linux下更新可能失败')
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Linux下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0103', '[TC0103]Linux保留降级BIOS', 'Linux保留降级BIOS'))
def flash_tool_0103():
    """

    Name:   Linux保留降级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.SetUp下读取修改后的选项值
            4.Linux下保留降级刷新BIOS
            5.刷新BIOS后进入SetUp读取刷新后的值
            6.对比刷新BIOS前后选项值，SMBIOS值

    Result: 4.刷新BIOS成功
            6.刷新前后选项的值相同，SMBIOS值相同
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS)
        logging.debug(output)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR, output[0]):
            logging.info('Linux下BIOS更新成功')
        else:
            stylelog.fail('Linux下更新可能失败')
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Linux下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0104', '[TC0104]Linux完全刷新升级BIOS', 'Linux完全刷新升级BIOS'))
def flash_tool_0104():
    """

    Name:   Linux完全刷新升级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux完全刷新升级BIOS
            4.刷新BIOS后进入SetUp读取刷新后的值
            5.对比刷新BIOS后选项值和默认的选项值，SMBIOS值

    Result: 3.刷新BIOS成功
            5.刷新后选项的值和默认值相同，SMBIOS值恢复默认
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL)
        logging.debug(output)
        if re.search(SutConfig.Tool.LINUX_MSG_ALL, output[0]):
            logging.info('Linux下BIOS更新成功')
        else:
            stylelog.fail('Linux下更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Linux下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('Linux下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0105', '[TC0105]Linux完全刷新降级BIOS', 'Linux完全刷新降级BIOS'))
def flash_tool_0105():
    """

    Name:   Linux完全刷新降级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux完全刷新降级BIOS
            4.刷新BIOS后进入SetUp读取刷新后的值
            5.对比刷新BIOS后选项值和默认的选项值，SMBIOS值

    Result: 3.刷新BIOS成功
            5.刷新后选项的值和默认值相同，SMBIOS值恢复默认
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        output = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL)
        logging.debug(output)
        if re.search(SutConfig.Tool.LINUX_MSG_ALL, output[0]):
            logging.info('Linux下BIOS更新成功')
        else:
            stylelog.fail('Linux下更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Linux下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('Linux下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0106', '[TC0106]Linux下备份BIOS', 'Linux下备份BIOS'))
def flash_tool_0106():
    """

    Name:   Linux下备份BIOS

    Steps:  1.Linux下备份BIOS
            2.Linux下保留配置刷新同时备份BIOS

    Result: 1.成功生成备份文件
            2.保留配置刷新BIOS成功，成功生成备份文件
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BACKUP_CMD)[0]):
            logging.info('BIOS备份成功')
        else:
            stylelog.fail('BIOS 备份失败')
            wrong_msg.append('BIOS 备份失败')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1], SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('备份命令执行成功，但没有生成备份文件')
            wrong_msg.append('备份命令执行成功，但没有生成备份文件')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UPDATE_BACKUP_CMD)[0]):
            logging.info('刷新BIOS同时备份BIOS成功')
        time.sleep(2)
        if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1], SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('刷新同时备份BIOS，但没有生成备份文件')
            wrong_msg.append('刷新同时备份BIOS，但没有生成备份文件')
            count += 1
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下保留配置刷新同时备份BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Linux下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS改变')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0107', '[TC0107]Linux下只保留Setup,升级更新BIOS', 'Linux下只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0107():
    """

    Name:   Linux下只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST)[0]):
            logging.info('Linux下只保留Setup,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0108', '[TC0108]Linux下只保留Setup,降级更新BIOS', 'Linux下只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0108():
    """

    Name:   Linux下只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS)[0]):
            logging.info('Linux下只保留Setup,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0109', '[TC0109]Linux下只保留SMBIOS,升级更新BIOS', 'Linux下只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0109():
    """

    Name:   Linux下只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST)[0]):
            logging.info('Linux下只保留SMBIOS,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0110', '[TC0110]Linux下只保留SMBIOS,降级更新BIOS', 'Linux下只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0110():
    """

    Name:   Linux下只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS)[0]):
            logging.info('Linux下只保留SMBIOS,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0111', '[TC0111]Linux Update OA3', 'Linux下更新oa3文件'))
def flash_tool_0111():
    return core.Status.Skip


@core.test_case(('0112', '[TC0112]Linux下工具锁住，BIOS刷新失败测试', 'Linux下工具锁住，BIOS刷新失败测试'))
def flash_tool_0112():
    """

    Name:   Linux下工具锁住，BIOS刷新失败测试

    Steps:  1.Linux下锁住Flash工具
            2.检查工具状态
            3.检查是否可以保留更新BIOS，完全刷新BIOS
            4.检查是否可以更新同时备份BIOS
            5.检查是否可以只保留SetUp更新BIOS
            6.检查是否可以只保留SMBIOS更新BIOS
            7.检查是否可以更新OA3文件
            8.检查是否可以备份BIOS
            9.解锁Flash工具
            10.检查解锁后的工具状态

    Result: 1.成功锁住
            2.工具状态为锁住
            3/4/5/6/7.不可以
            8.可以备份BIOS
            9.成功解锁
            10.工具状态为解锁
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info(f'BIOS 锁住成功')
        else:
            stylelog.fail(f'BIOS 锁住没有提示{SutConfig.Tool.LINUX_LOCK_BIOS_MSG}')
            wrong_msg.append(f'BIOS 锁住没有提示{SutConfig.Tool.LINUX_LOCK_BIOS_MSG}')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_STATUS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):

            logging.info(f'BIOS 锁住,BIOS 状态为{SutConfig.Tool.LINUX_LOCK_STATUS_MSG}')
        else:
            stylelog.fail(f'BIOS 锁住,BIOS 状态不是{SutConfig.Tool.LINUX_LOCK_STATUS_MSG}')
            wrong_msg.append(f'BIOS 锁住,BIOS 状态不是{SutConfig.Tool.LINUX_LOCK_STATUS_MSG}')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST)[0]):
            logging.info('BIOS 锁住后，无法保留更新BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以保留更新BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以保留更新BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL)[0]):
            logging.info('BIOS 锁住后，无法完全更新BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以完全更新BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以完全更新BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UPDATE_BACKUP_CMD)[0]):
            logging.info('BIOS 锁住后，无法更新同时备份BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新同时备份BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以更新同时备份BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST)[0]):
            logging.info('BIOS 锁住后，无法更新BIOS，只保留SetUp配置')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新BIOS，只保留SetUp配置')
            wrong_msg.append('BIOS 锁住后，仍可以更新BIOS，只保留SetUp配置')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST)[0]):
            logging.info('BIOS 锁住后，无法更新BIOS，只保留SMBIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新BIOS，只保留SMBIOS')
            wrong_msg.append('BIOS 锁住后，仍可以更新BIOS，只保留SMBIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UPDATE_OA3_CMD)[0]):
            logging.info('BIOS 锁住后，无法更新OA3文件')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新OA3文件')
            wrong_msg.append('BIOS 锁住后，仍可以更新OA3文件')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BACKUP_CMD)[0]):
            logging.info('BIOS锁住后，可以备份BIOS')
            time.sleep(1)
            if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):
                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('BIOS锁住后可以备份文件，但没有生成备份文件')
                wrong_msg.append('BIOS锁住后可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('BIOS锁住后，无法备份BIOS')
            wrong_msg.append('BIOS锁住后，无法备份BIOS')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS 解锁失败')
            wrong_msg.append('BIOS 解锁失败')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
            logging.info(f'BIOS解锁，BIOS状态为{SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG}')
        else:
            stylelog.fail(f'BIOS解锁，BIOS状态不是{SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG}')
            wrong_msg.append(f'BIOS解锁，BIOS状态不是{SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG}')
            count += 1
        time.sleep(2)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0113', '[TC0113]Linux下解锁后保留刷新BIOS', 'Linux下解锁后保留刷新BIOS'))
def flash_tool_0113():
    """

    Name:   Linux下解锁后保留刷新BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下锁住工具，解锁工具
            4.保留刷新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值保留，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST)[0]):
            logging.info('BIOS更新成功')
        else:
            stylelog.fail('BIOS可能更新失败')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()

        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Linux下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0114', '[TC0114]Linux下解锁后完全刷新BIOS', 'Linux下解锁后完全刷新BIOS'))
def flash_tool_0114():
    """

    Name:   Linux下解锁后完全刷新BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下锁住工具，解锁工具
            4.完全刷新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值恢复默认值，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_MSG_ALL,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL)[0]):
            logging.info("Update BIOS in Linux successed.")
        else:
            stylelog.fail('BIOS可能更新失败')

        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('LINUX下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('Linux下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0115', '[TC0115]Linux下解锁BIOS，刷新同时备份BIOS', 'Linux下解锁BIOS，刷新同时备份BIOS'))
def flash_tool_0115():
    """

    Name:   Linux下解锁BIOS，刷新同时备份BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下锁住工具，解锁工具
            4.刷新同时备份BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS，备份BIOS
            5.选项值保留，SMBIOS保留
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UPDATE_BACKUP_CMD)[0]):
            logging.info('刷新BIOS同时备份BIOS成功')
        time.sleep(2)
        if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1], SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")

            time.sleep(1)
        else:
            stylelog.fail('刷新同时备份BIOS，但没有生成备份文件')
            wrong_msg.append('刷新同时备份BIOS，但没有生成备份文件')
            count += 1
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下保留配置刷新同时备份BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('Linux下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS改变')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0116', '[TC0116]Linux下解锁BIOS，只保留Setup,更新BIOS', 'Linux下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认'))
def flash_tool_0116():
    """

    Name:   Linux下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下锁住工具，解锁工具
            4.只保留Setup,更新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST)[0]):
            logging.info('Linux下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0117', '[TC0117]Linux下解锁BIOS，只保留SMBIOS,更新BIOS', 'Linux下解锁BIOS，只保留SMBIOS,更新BIOS，SetUp恢复默认'))
def flash_tool_0117():
    """

    Name:   Linux下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下锁住工具，解锁工具
            4.只保留SMBIOS,更新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST)[0]):
            logging.info('Linux下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0118', '[TC0118]Linux下解锁BIOS，更新OA3文件', 'Linux下解锁BIOS，更新OA3文件'))
def flash_tool_0118():
    return core.Status.Skip


@core.test_case(('0119', '[TC0119]Linux下设置管理员密码，保留升级BIOS', 'Linux下设置管理员密码，保留升级BIOS'))
def flash_tool_0119():
    """

    Name:   Linux下设置管理员密码，保留升级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下保留升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Linux下保留刷新BIOS，刷新后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Linux下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0120', '[TC0120]Linux下设置管理员密码，保留降级BIOS', 'Linux下设置管理员密码，保留降级BIOS'))
def flash_tool_0120():
    """

    Name:   Linux下设置管理员密码，保留降级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下保留降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Linux下保留刷新BIOS，刷新后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Linux下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0121', '[TC0121]Linux下设置管理员密码，完全升级BIOS', 'Linux下设置管理员密码，完全升级BIOS'))
def flash_tool_0121():
    """

    Name:   Linux下设置管理员密码，完全升级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下完全升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Linux下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('Linux下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0122', '[TC0122]Linux下设置管理员密码，完全降级BIOS', 'Linux下设置管理员密码，完全降级BIOS'))
def flash_tool_0122():
    """

    Name:   Linux下设置管理员密码，完全降级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下完全降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Linux下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('Linux下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0123', '[TC0123]Linux下设置管理员密码只保留Setup,升级更新BIOS', 'Linux下设置管理员只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0123():
    """

    Name:   Linux下设置管理员只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Linux下只保留Setup,刷新BIOS后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Linux下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0124', '[TC0124]Linux下设置管理员密码只保留Setup,降级更新BIOS', 'Linux下设置管理员密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0124():
    """

    Name:   Linux下设置管理员密码只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Linux下只保留Setup,刷新BIOS后密码保留')
            del_psw(password)
        else:
            stylelog.fail('Linux下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0125', '[TC0125]Linux下设置管理员密码只保留SMBIOS,升级更新BIOS', 'Linux下设置管理员密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0125():
    """

    Name:   Linux下设置管理员密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0126', '[TC0126]Linux下设置管理员密码只保留SMBIOS,降级更新BIOS', 'Linux下设置管理员密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0126():
    """

    Name:   Linux下设置管理员密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0127', '[TC0127]Linux下设置管理员密码,更新OA3', 'Linux下设置管理员密码,更新OA3'))
def flash_tool_0127():
    return core.Status.Skip


@core.test_case(('0128', '[TC0128]Linux下设置管理员密码,备份BIOS,锁住BIOS测试', 'Linux下设置管理员密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0128():
    """

    Name:   Linux下设置管理员密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置管理员密码
            2.Linux下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输错密码提示密码错误
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password(password)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BACKUP_CMD)[0]):
            logging.info('Linux下，设置管理员密码，备份BIOS不需要密码')

            time.sleep(1)
            if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):

                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('Linux下，设置管理员密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('SLinux下，设置管理员密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD}\n', '111111\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_LOCK_FAIL_MSG]):
            logging.info('Linux下设置管理员密码，锁住BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('Linux下设置管理员密码，锁住BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD}\n', f'{password}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_LOCK_BIOS_MSG]):
            logging.info('输入正确密码成功锁住BIOS')
            if re.search(SutConfig.Tool.LINUX_LOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
                logging.info('锁住BIOS，状态为锁住')
            else:
                stylelog.fail('锁住BIOS，状态不是锁住')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD}\n', '111111\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_UNLOCK_FAIL_MSG]):
            logging.info('Linux下设置管理员密码，解锁BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('Linux下设置管理员密码，解锁BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD}\n', f'{password}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG]):
            logging.info('输入正确密码成功解锁BIOS')
            if re.search(SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
                logging.info('解锁BIOS，状态为解锁')
            else:
                stylelog.fail('解锁BIOS，状态不是解锁')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        go_to_setup(password=password)
        del_psw(password)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0129', '[TC0129]Linux下设置用户密码，保留升级BIOS', 'Linux下设置用户密码，保留升级BIOS'))
def flash_tool_0129():
    """

    Name:   Linux下设置用户密码，保留升级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下保留升级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Linux下保留刷新BIOS，刷新后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Linux下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0130', '[TC0130]Linux下设置用户密码，保留降级BIOS', 'Linux下设置用户密码，保留降级BIOS'))
def flash_tool_0130():
    """

    Name:   Linux下设置用户密码，保留降级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下保留降级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Linux下保留刷新BIOS，刷新后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Linux下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0131', '[TC0131]Linux下设置用户密码，完全升级BIOS', 'Linux下设置用户密码，完全升级BIOS'))
def flash_tool_0131():
    """

    Name:   Linux下设置用户密码，完全升级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下完全升级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Linux下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('Linux下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0132', '[TC0132]Linux下设置用户密码，完全降级BIOS', 'Linux下设置用户密码，完全降级BIOS'))
def flash_tool_0132():
    """

    Name:   Linux下设置用户密码，完全降级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下完全降级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Linux下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('Linux下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0133', '[TC0133]Linux下设置用户密码只保留Setup,升级更新BIOS', 'Linux下设置用户只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0133():
    """

    Name:   Linux下设置用户只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Linux下只保留Setup,刷新BIOS后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Linux下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0134', '[TC0134]Linux下设置用户密码只保留Setup,降级更新BIOS', 'Linux下设置用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0134():
    """

    Name:   Linux下设置用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Linux下只保留Setup,刷新BIOS后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('Linux下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0135', '[TC0135]Linux下设置用户密码只保留SMBIOS,升级更新BIOS', 'Linux下设置用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0135():
    """

    Name:   Linux下设置用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0136', '[TC0136]Linux下设置用户密码只保留SMBIOS,降级更新BIOS', 'Linux下设置用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0136():
    """

    Name:   Linux下设置用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS}\n', '111111\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS}\n', f'{password}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0137', '[TC0137]Linux下设置用户密码,更新OA3', 'Linux下设置用户密码,更新OA3'))
def flash_tool_0137():
    return core.Status.Skip


@core.test_case(('0138', '[TC0138]Linux下设置用户密码,备份BIOS,锁住BIOS测试', 'Linux下设置用户密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0138():
    """

    Name:   Linux下设置用户密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置用户密码
            2.Linux下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输错密码提示密码错误
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BACKUP_CMD)[0]):
            logging.info('Linux下，设置用户密码，备份BIOS不需要密码')

            time.sleep(1)
            if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):

                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('Linux下，设置用户密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('SLinux下，设置用户密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD}\n', '111111\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_LOCK_FAIL_MSG]):
            logging.info('Linux下设置用户密码，锁住BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('Linux下设置用户密码，锁住BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD}\n', f'{password}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_LOCK_BIOS_MSG]):
            logging.info('输入正确密码成功锁住BIOS')
            if re.search(SutConfig.Tool.LINUX_LOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
                logging.info('锁住BIOS，状态为锁住')
            else:
                stylelog.fail('锁住BIOS，状态不是锁住')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD}\n', '111111\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_UNLOCK_FAIL_MSG]):
            logging.info('Linux下设置用户密码，解锁BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('Linux下设置用户密码，解锁BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD}\n', f'{password}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG]):
            logging.info('输入正确密码成功解锁BIOS')
            if re.search(SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
                logging.info('解锁BIOS，状态为解锁')
            else:
                stylelog.fail('解锁BIOS，状态不是解锁')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        go_to_setup(password=password)
        del_psw_user(password)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0139', '[TC0139]Linux下同时设置管理员密码，用户密码，保留升级BIOS', 'Linux下同时设置管理员密码，用户密码，保留升级BIOS'))
def flash_tool_0139():
    """

    Name:   Linux下同时设置管理员，用户密码，保留升级BIOS

    Steps:  1.SetUp下设置管理员密码，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下保留升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Linux下保留刷新BIOS，刷新后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Linux下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        go_to_setup_del_psw(admin, user)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0140', '[TC0140]Linux下同时设置管理员密码，用户密码，保留降级BIOS', 'Linux下同时设置管理员密码，用户密码，保留降级BIOS'))
def flash_tool_0140():
    """

    Name:   Linux下同时设置管理员密码，用户密码，保留降级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下保留降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('Linux下保留刷新BIOS，刷新后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('Linux下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('Linux下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0141', '[TC0141]Linux下同时设置管理员密码，用户密码，完全升级BIOS', 'Linux下同时设置管理员密码，用户密码，完全升级BIOS'))
def flash_tool_0141():
    """

    Name:   Linux下设置管理员，用户密码，完全升级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下完全升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_LATEST_ALL}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Linux下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('Linux下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0142', '[TC0142]Linux下同时设置管理员密码，用户密码，完全降级BIOS', 'Linux下同时设置管理员密码，用户密码，完全降级BIOS'))
def flash_tool_0142():
    """

    Name:   Linux下同时设置管理员密码，用户密码，完全降级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下完全降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_FLASH_CMD_PREVIOUS_ALL}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('Linux下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('Linux下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('Linux下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('Linux下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0143', '[TC0143]Linux下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS', 'Linux下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0143():
    """

    Name:   Linux下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_LATEST}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Linux下只保留Setup,刷新BIOS后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Linux下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0144', '[TC0144]Linux下同时设置管理员密码，用户密码只保留Setup,降级更新BIOS', 'Linux下同时设置管理员密码，用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0144():
    """

    Name:   Linux下同时设置管理员密码，用户密码,只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVNVM_CMD_PREVIOUS}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('Linux下只保留Setup,刷新BIOS后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('Linux下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('Linux下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('Linux下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('Linux下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0145', '[TC0145]Linux下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS', 'Linux下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0145():
    """

    Name:   Linux下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_LATEST}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0146', '[TC0146]Linux下同时设置管理员密码，用户密码只保留SMBIOS,降级更新BIOS', 'Linux下同时设置管理员密码，用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0146():
    """

    Name:   Linux下同时设置管理员密码，用户密码,只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Linux下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS}\n', f'{user}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_RESVSMBIOS_CMD_PREVIOUS}\n', f'{admin}\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.LINUX_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('Linux下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('Linux下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0147', '[TC0147]Linux下同时设置管理员密码，用户密码,更新OA3', 'Linux下设置管理员密码,更新OA3'))
def flash_tool_0147():
    return core.Status.Skip


@core.test_case(('0148', '[TC0148]Linux下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试', 'Linux下设置管理员密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0148():
    """

    Name:   Linux下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置管理员密码
            2.Linux下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输入用户密码提示密码错误
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_all(admin, user)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BACKUP_CMD)[0]):
            logging.info('Linux下，同时设置管理员密码，用户密码，备份BIOS不需要密码')

            time.sleep(1)
            if re.search(SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_SSH, 'ls')[0]):

                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_SSH, f"rm {SutConfig.Tool.LINUX_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('Linux下，同时设置管理员密码，用户密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('Linux下，同时设置管理员密码，用户密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD}\n', f'{user}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_LOCK_FAIL_MSG]):
            logging.info('Linux下同时设置管理员密码，用户密码，锁住BIOS需要密码，输入用户密码，锁住失败')
        else:
            stylelog.fail('Linux下同时设置管理员密码，用户密码，锁住BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_LOCK_BIOS_UPDATE_CMD}\n', f'{admin}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_LOCK_BIOS_MSG]):
            logging.info('输入正确密码成功锁住BIOS')
            if re.search(SutConfig.Tool.LINUX_LOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
                logging.info('锁住BIOS，状态为锁住')
            else:
                stylelog.fail('锁住BIOS，状态不是锁住')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD}\n', f'{user}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_UNLOCK_FAIL_MSG]):
            logging.info('Linux下同时设置管理员密码，用户密码，解锁BIOS需要密码，输入用户密码，锁住失败')
        else:
            stylelog.fail('Linux下同时设置管理员密码，用户密码，解锁BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_UNLOCK_BIOS_UPDATE_CMD}\n', f'{admin}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_UNLOCK_BIOS_MSG]):
            logging.info('输入正确密码成功解锁BIOS')
            if re.search(SutConfig.Tool.LINUX_UNLOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_LOCK_STATUS_CMD)[0]):
                logging.info('解锁BIOS，状态为解锁')
            else:
                stylelog.fail('解锁BIOS，状态不是解锁')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        go_to_setup(password=admin)
        del_psw_all(admin, user)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0149', '[TC0149]Linux下设置管理员密码,Flash 工具清除密码测试', 'Linux下设置管理员密码,Flash 工具清除密码测试'))
def flash_tool_0149():
    """

    Name:   Linux下设置管理员密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置管理员密码
            2.Linux下工具清除密码

    Result: 2.输入错误密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password(password)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_CLEAN_PSW_CMD}\n', '11111\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，工具清除密码，需要输入密码,输入错误密码，提示密码错误')
            time.sleep(2)
            if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_CLEAN_PSW_CMD}\n', f'{password}\n'],
                                  [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_CLEAN_PSW_MSG]):
                logging.info('设置管理员密码，工具清除密码，需要输入密码,输入正确密码，成功清除')
            else:
                stylelog.fail('输入正确密码，没有清除密码')
                count += 1
        else:
            stylelog.fail('设置管理员密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=password) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0150', '[TC0150]Linux下设置用户密码,Flash 工具清除密码测试', 'Linux下设置用户密码,Flash 工具清除密码测试'))
def flash_tool_0150():
    """

    Name:   Linux下设置用户密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置用户密码
            2.Linux下工具清除密码

    Result: 2.输入错误密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_CLEAN_PSW_CMD}\n', '11111\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，工具清除密码，需要输入密码,输入错误密码，提示密码错误')
            time.sleep(2)
            if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_CLEAN_PSW_CMD}\n', f'{password}\n'],
                                  [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_CLEAN_PSW_MSG]):
                logging.info('设置用户密码，工具清除密码，需要输入密码,输入正确密码，成功清除')
            else:
                stylelog.fail('输入正确密码，没有清除密码')
                count += 1
        else:
            stylelog.fail('设置用户密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=password) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw_user(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0151', '[TC0151]Linux下同时设置管理员密码，用户密码,Flash 工具清除密码测试', 'Linux下同时设置管理员密码，用户密码,Flash 工具清除密码测试'))
def flash_tool_0151():
    """

    Name:   Linux下设置管理员，用户密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置管理员，用户密码
            2.Linux下工具清除密码

    Result: 2.输入用户密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_all(admin, user)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_CLEAN_PSW_CMD}\n', f'{user}\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，工具清除密码，需要输入密码,输入用户密码，提示密码错误')
            time.sleep(2)
            if SshLib.interaction(Sut.OS_SSH, [f'{SutConfig.Tool.LINUX_CLEAN_PSW_CMD}\n', f'{admin}\n'],
                                  [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.LINUX_CLEAN_PSW_MSG]):
                logging.info('同时设置管理员密码，用户密码，工具清除密码，需要输入密码,输入正确密码，成功清除')
            else:
                stylelog.fail('输入正确密码，没有清除密码')
                count += 1
        else:
            stylelog.fail('同时设置管理员密码，用户密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=admin) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw_all(admin, user)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0152', '[TC0152]Linux下负面测试(错误BIOS,错误OA3,错误命令参数)', 'Linux下负面测试(错误BIOS,错误OA3,错误命令参数)'))
def flash_tool_0152():
    """

    Name:   Linux下负面测试(错误BIOS,错误OA3,错误命令参数)

    Steps:  1.Linux下工具不输入参数
            2.输入错误参数
            3.更新其他平台BIOS
            4.更新为签名的BIOS

    Result: 1/2.提示信息显示正确
            3/4.无法更新
    """
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_INPUT_ERR_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_EMPTY_CMD)[0]):
            logging.info('Linux 工具不输入参数，提示输入错误')
        else:
            stylelog.fail('Linux 工具不输入参数，没有提示输入错误')
            count += 1
            time.sleep(200)
        time.sleep(2)
        if re.search(SutConfig.Tool.LINUX_INPUT_ERR_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_ERROR_CMD)[0]):
            logging.info('Linux 工具输入错误参数，提示输入错误')
        else:
            stylelog.fail('Linux 工具输入错误参数，没有提示输入错误')
            count += 1
            time.sleep(200)
        time.sleep(2)
        if re.search(SutConfig.Tool.LINUX_UPDATE_OTHERS_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_OTHERS)[0]):
            logging.info('Linux 下更新其他平台的BIOS，提示无法更新')
            time.sleep(2)
        else:
            stylelog.fail('Linux下可以更新其他平台的BIOS')
            count += 1
            time.sleep(200)
        if re.search(SutConfig.Tool.LINUX_UPDATE_UNSIGNED_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_FLASH_CMD_UNSIGNED)[0]):
            logging.info('Linux 下更新未签名的BIOS，提示无法更新')
        else:
            stylelog.fail('Linux下可以更新未签名的BIOS')
            count += 1
            time.sleep(200)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0201', '[TC0201]WINDOWS,Check Flash Tool Version,Help Message', 'WINDOWS下检查Flash工具版本，帮助信息'))
def flash_tool_0201():
    """

    Name:   Windows下检查Flash工具版本，帮助信息

    Steps:  1.Windows下检查Flash工具版本，帮助信息

    Result: 1.工具版本，帮助信息显示正确

    """
    try:
        wrong_msg = []
        count = 0
        assert SetUpLib.boot_to_windows_os()
        result = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_TOOL_VERSION_CMD)
        if re.search(SutConfig.Tool.WINDOWS_TOOL_VERSION_CONFIRM_MSG, result[0]):
            logging.info(result)
            logging.info('WINDOWS下 Flash Tool版本验证成功')
        else:
            stylelog.fail(result)
            stylelog.fail('WINDOWS下 Flash Tool版本验证失败')
            wrong_msg.append(result + 'Flash Tool 版本验证失败')
            count += 1
        time.sleep(1)
        result_h = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_TOOL_HELP_CMD)
        if re.search(SutConfig.Tool.WINDOWS_TOOL_HELP_CONFIRM_MSG, result_h[0]):
            logging.info(result_h)
            logging.info('WINDOWS下 Flash Tool帮助信息验证成功')
        else:
            stylelog.fail(result_h)
            stylelog.fail('WINDOWS下 Flash Tool帮助信息验证失败')
            wrong_msg.append(result_h + 'Flash Tool 帮助信息验证失败')
            count += 1
        if count == 0:
            return core.Status.Pass
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0202', '[TC0202]WINDOWS保留升级BIOS', 'WINDOWS保留升级BIOS'))
def flash_tool_0202():
    """

    Name:   Windows保留升级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.SetUp下读取修改后的选项值
            4.Windows下保留升级刷新BIOS
            5.刷新BIOS后进入SetUp读取刷新后的值
            6.对比刷新BIOS前后选项值，SMBIOS值

    Result: 4.刷新BIOS成功
            6.刷新前后选项的值相同，SMBIOS值相同
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()
        output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST)
        logging.debug(output)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR, output[0]):
            logging.info('WINDOWS下BIOS更新成功')
        else:
            stylelog.fail('WINDOWS下更新可能失败')
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('WINDOWS下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0203', '[TC0203]WINDOWS保留降级BIOS', 'WINDOWS保留降级BIOS'))
def flash_tool_0203():
    """

    Name:   Windows保留降级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.SetUp下读取修改后的选项值
            4.Windows下保留降级刷新BIOS
            5.刷新BIOS后进入SetUp读取刷新后的值
            6.对比刷新BIOS前后选项值，SMBIOS值

    Result: 4.刷新BIOS成功
            6.刷新前后选项的值相同，SMBIOS值相同
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()
        output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS)
        logging.debug(output)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR, output[0]):
            logging.info('WINDOWS下BIOS更新成功')
        else:
            stylelog.fail('WINDOWS下更新可能失败')
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('WINDOWS下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0204', '[TC0204]WINDOWS完全刷新升级BIOS', 'WINDOWS完全刷新升级BIOS'))
def flash_tool_0204():
    """

    Name:   Windows完全刷新升级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows完全刷新升级BIOS
            4.刷新BIOS后进入SetUp读取刷新后的值
            5.对比刷新BIOS后选项值和默认的选项值，SMBIOS值

    Result: 3.刷新BIOS成功
            5.刷新后选项的值和默认值相同，SMBIOS值恢复默认
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()
        output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL)
        logging.debug(output)
        if re.search(SutConfig.Tool.WINDOWS_MSG_ALL, output[0]):
            logging.info('WINDOWS下BIOS更新成功')
        else:
            stylelog.fail('WINDOWS下更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('WINDOWS下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('WINDOWS下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0205', '[TC0205]WINDOWS完全刷新降级BIOS', 'WINDOWS完全刷新降级BIOS'))
def flash_tool_0205():
    """

    Name:   Windows完全刷新降级BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows完全刷新降级BIOS
            4.刷新BIOS后进入SetUp读取刷新后的值
            5.对比刷新BIOS后选项值和默认的选项值，SMBIOS值

    Result: 3.刷新BIOS成功
            5.刷新后选项的值和默认值相同，SMBIOS值恢复默认
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        output = SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL)
        logging.debug(output)
        if re.search(SutConfig.Tool.WINDOWS_MSG_ALL, output[0]):
            logging.info('WINDOWS下BIOS更新成功')
        else:
            stylelog.fail('WINDOWS下更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('WINDOWS下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('WINDOWS下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0206', '[TC0206]WINDOWS下备份BIOS', 'WINDOWS下备份BIOS'))
def flash_tool_0206():
    """

    Name:   Windows下备份BIOS

    Steps:  1.Windows下备份BIOS
            2.Windows下保留配置刷新同时备份BIOS

    Result: 1.成功生成备份文件
            2.保留配置刷新BIOS成功，成功生成备份文件
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BACKUP_CMD)[0]):
            logging.info('BIOS备份成功')
        else:
            stylelog.fail('BIOS 备份失败')
            wrong_msg.append('BIOS 备份失败')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('备份命令执行成功，但没有生成备份文件')
            wrong_msg.append('备份命令执行成功，但没有生成备份文件')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UPDATE_BACKUP_CMD)[0]):
            logging.info('刷新BIOS同时备份BIOS成功')
        time.sleep(2)
        if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")
            time.sleep(1)
        else:
            stylelog.fail('刷新同时备份BIOS，但没有生成备份文件')
            wrong_msg.append('刷新同时备份BIOS，但没有生成备份文件')
            count += 1
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下保留配置刷新同时备份BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('WINDOWS下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS改变')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0207', '[TC0207]WINDOWS下只保留Setup,升级更新BIOS', 'WINDOWS下只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0207():
    """

    Name:   Windows下只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST)[0]):
            logging.info('WINDOWS下只保留Setup,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0208', '[TC0208]WINDOWS下只保留Setup,降级更新BIOS', 'WINDOWS下只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0208():
    """

    Name:   Windows下只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS)[0]):
            logging.info('WINDOWS下只保留Setup,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0209', '[TC0209]WINDOWS下只保留SMBIOS,升级更新BIOS', 'WINDOWS下只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0209():
    """

    Name:   Windows下只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST)[0]):
            logging.info('WINDOWS下只保留SMBIOS,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0210', '[TC0210]WINDOWS下只保留SMBIOS,降级更新BIOS', 'WINDOWS下只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0210():
    """

    Name:   Windows下只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值

    Result: 3.成功刷新BIOS
            4.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS)[
                         0]):
            logging.info('WINDOWS下只保留SMBIOS,升级更新BIOS成功')
        else:
            stylelog.fail('更新可能失败')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0211', '[TC0211]WINDOWS Update OA3', 'WINDOWS下更新oa3文件'))
def flash_tool_0211():
    return core.Status.Skip


@core.test_case(('0212', '[TC0212]WINDOWS下工具锁住，BIOS刷新失败测试', 'WINDOWS下工具锁住，BIOS刷新失败测试'))
def flash_tool_0212():
    """

    Name:   Windows下工具锁住，BIOS刷新失败测试

    Steps:  1.Windows下锁住Flash工具
            2.检查工具状态
            3.检查是否可以保留更新BIOS，完全刷新BIOS
            4.检查是否可以更新同时备份BIOS
            5.检查是否可以只保留SetUp更新BIOS
            6.检查是否可以只保留SMBIOS更新BIOS
            7.检查是否可以更新OA3文件
            8.检查是否可以备份BIOS
            9.解锁Flash工具
            10.检查解锁后的工具状态

    Result: 1.成功锁住
            2.工具状态为锁住
            3/4/5/6/7.不可以
            8.可以备份BIOS
            9.成功解锁
            10.工具状态为解锁
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info(f'BIOS 锁住成功')
        else:
            stylelog.fail(f'BIOS 锁住没有提示{SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG}')
            wrong_msg.append(f'BIOS 锁住没有提示{SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG}')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):

            logging.info(f'BIOS 锁住,BIOS 状态为{SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG}')
        else:
            stylelog.fail(f'BIOS 锁住,BIOS 状态不是{SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG}')
            wrong_msg.append(f'BIOS 锁住,BIOS 状态不是{SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG}')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST)[0]):
            logging.info('BIOS 锁住后，无法保留更新BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以保留更新BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以保留更新BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL)[0]):
            logging.info('BIOS 锁住后，无法完全更新BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以完全更新BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以完全更新BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UPDATE_BACKUP_CMD)[0]):
            logging.info('BIOS 锁住后，无法更新同时备份BIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新同时备份BIOS')
            wrong_msg.append('BIOS 锁住后，仍可以更新同时备份BIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST)[0]):
            logging.info('BIOS 锁住后，无法更新BIOS，只保留SetUp配置')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新BIOS，只保留SetUp配置')
            wrong_msg.append('BIOS 锁住后，仍可以更新BIOS，只保留SetUp配置')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST)[0]):
            logging.info('BIOS 锁住后，无法更新BIOS，只保留SMBIOS')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新BIOS，只保留SMBIOS')
            wrong_msg.append('BIOS 锁住后，仍可以更新BIOS，只保留SMBIOS')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UPDATE_OA3_CMD)[0]):
            logging.info('BIOS 锁住后，无法更新OA3文件')
        else:
            stylelog.fail('BIOS 锁住后，仍可以更新OA3文件')
            wrong_msg.append('BIOS 锁住后，仍可以更新OA3文件')
            count += 1
            time.sleep(200)
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BACKUP_CMD)[0]):
            logging.info('BIOS锁住后，可以备份BIOS')
            time.sleep(1)
            if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):
                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                             f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('BIOS锁住后可以备份文件，但没有生成备份文件')
                wrong_msg.append('BIOS锁住后可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('BIOS锁住后，无法备份BIOS')
            wrong_msg.append('BIOS锁住后，无法备份BIOS')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS 解锁失败')
            wrong_msg.append('BIOS 解锁失败')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
            logging.info(f'BIOS解锁，BIOS状态为{SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG}')
        else:
            stylelog.fail(f'BIOS解锁，BIOS状态不是{SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG}')
            wrong_msg.append(f'BIOS解锁，BIOS状态不是{SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG}')
            count += 1
        time.sleep(2)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0213', '[TC0213]WINDOWS下解锁后保留刷新BIOS', 'WINDOWS下解锁后保留刷新BIOS'))
def flash_tool_0213():
    """

    Name:   Windows下解锁后保留刷新BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下锁住工具，解锁工具
            4.保留刷新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值保留，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST)[0]):
            logging.info('BIOS更新成功')
        else:
            stylelog.fail('BIOS可能更新失败')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()

        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下保留配置刷新，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留配置刷新，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('WINDOWS下保留配置刷新，刷新BIOS后SMBIOS改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0214', '[TC0214]WINDOWS下解锁后完全刷新BIOS', 'WINDOWS下解锁后完全刷新BIOS'))
def flash_tool_0214():
    """

    Name:   Windows下解锁后完全刷新BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下锁住工具，解锁工具
            4.完全刷新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值恢复默认值，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_MSG_ALL,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL)[0]):
            logging.info("Update BIOS in WINDOWS successed.")
        else:
            stylelog.fail('BIOS可能更新失败')

        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('WINDOWS下完全刷新，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新，刷新BIOS后SMBIOS变为默认值')

            else:
                stylelog.fail('WINDOWS下完全刷新，刷新BIOS后SMBIOS没有变为默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0215', '[TC0215]WINDOWS下解锁BIOS，刷新同时备份BIOS', 'WINDOWS下解锁BIOS，刷新同时备份BIOS'))
def flash_tool_0215():
    """

    Name:   Windows下解锁BIOS，刷新同时备份BIOS

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下锁住工具，解锁工具
            4.刷新同时备份BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS，备份BIOS
            5.选项值保留，SMBIOS保留
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UPDATE_BACKUP_CMD)[0]):
            logging.info('刷新BIOS同时备份BIOS成功')
        time.sleep(2)
        if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):
            logging.info('成功生成备份文件')
            time.sleep(1)
            SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")

            time.sleep(1)
        else:
            stylelog.fail('刷新同时备份BIOS，但没有生成备份文件')
            wrong_msg.append('刷新同时备份BIOS，但没有生成备份文件')
            count += 1
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下保留配置刷新同时备份BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS没有改变')

            else:
                stylelog.fail('WINDOWS下保留配置刷新同时备份BIOS，刷新BIOS后SMBIOS改变')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0216', '[TC0216]WINDOWS下解锁BIOS，只保留Setup,更新BIOS', 'WINDOWS下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认'))
def flash_tool_0216():
    """

    Name:   Windows下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下锁住工具，解锁工具
            4.只保留Setup,更新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值保留，SMBIOS恢复默认值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST)[0]):
            logging.info('WINDOWS下只保留Setup,升级更新BIOS成功')
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')

            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1

        else:
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0217', '[TC0217]WINDOWS下解锁BIOS，只保留SMBIOS,更新BIOS', 'WINDOWS下解锁BIOS，只保留SMBIOS,更新BIOS，SetUp恢复默认'))
def flash_tool_0217():
    """

    Name:   Windows下解锁BIOS，只保留Setup,更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下锁住工具，解锁工具
            4.只保留SMBIOS,更新BIOS
            5.检查选项值，SMBIOS值

    Result: 4.成功刷新BIOS
            5.选项值恢复默认值，SMBIOS保留
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('成功锁住BIOS')
        else:
            stylelog.fail('BIOS锁住失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD)[0]):
            logging.info('BIOS成功解锁')
        else:
            stylelog.fail('BIOS解锁失败')
            return
        time.sleep(1)
        if re.search(SutConfig.Tool.WINDOWS_MSG_NOR,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST)[0]):
            logging.info('WINDOWS下只保留SMBIOS,升级更新BIOS成功')
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('0218', '[TC0218]WINDOWS下解锁BIOS，更新OA3文件', 'WINDOWS下解锁BIOS，更新OA3文件'))
def flash_tool_0218():
    return core.Status.Skip


@core.test_case(('0219', '[TC0219]WINDOWS下设置管理员密码，保留升级BIOS', 'WINDOWS下设置管理员密码，保留升级BIOS'))
def flash_tool_0219():
    """

    Name:   Windows下设置管理员密码，保留升级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下保留升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('WINDOWS下保留刷新BIOS，刷新后密码保留')
            del_psw(password)
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0220', '[TC0220]WINDOWS下设置管理员密码，保留降级BIOS', 'WINDOWS下设置管理员密码，保留降级BIOS'))
def flash_tool_0220():
    """

    Name:   Windows下设置管理员密码，保留降级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下保留降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('WINDOWS下保留刷新BIOS，刷新后密码保留')
            del_psw(password)
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0221', '[TC0221]WINDOWS下设置管理员密码，完全升级BIOS', 'WINDOWS下设置管理员密码，完全升级BIOS'))
def flash_tool_0221():
    """

    Name:   Windows下设置管理员密码，完全升级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下完全升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('WINDOWS下完全刷新BIOS，刷新后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0222', '[TC0222]WINDOWS下设置管理员密码，完全降级BIOS', 'WINDOWS下设置管理员密码，完全降级BIOS'))
def flash_tool_0222():
    """

    Name:   Windows下设置管理员密码，完全降级BIOS

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下完全降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0223', '[TC0223]WINDOWS下设置管理员密码只保留Setup,升级更新BIOS', 'WINDOWS下设置管理员只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0223():
    """

    Name:   Windows下设置管理员只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('WINDOWS下只保留Setup,刷新BIOS后密码保留')
            del_psw(password)
        else:
            stylelog.fail('WINDOWS下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0224', '[TC0224]WINDOWS下设置管理员密码只保留Setup,降级更新BIOS', 'WINDOWS下设置管理员密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0224():
    """

    Name:   Windows下设置管理员密码只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('WINDOWS下只保留Setup,刷新BIOS后密码保留')
            del_psw(password)
        else:
            stylelog.fail('WINDOWS下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0225', '[TC0225]WINDOWS下设置管理员密码只保留SMBIOS,升级更新BIOS', 'WINDOWS下设置管理员密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0225():
    """

    Name:   Windows下设置管理员密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0226', '[TC0226]WINDOWS下设置管理员密码只保留SMBIOS,降级更新BIOS', 'WINDOWS下设置管理员密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0226():
    """

    Name:   Windows下设置管理员密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置管理员密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0227', '[TC0227]WINDOWS下设置管理员密码,更新OA3', 'WINDOWS下设置管理员密码,更新OA3'))
def flash_tool_0227():
    return core.Status.Skip


@core.test_case(('0228', '[TC0228]WINDOWS下设置管理员密码,备份BIOS,锁住BIOS测试', 'WINDOWS下设置管理员密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0228():
    """

    Name:   Windows下设置管理员密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置管理员密码
            2.Windows下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输错密码提示密码错误
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password(password)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BACKUP_CMD)[0]):
            logging.info('WINDOWS下，设置管理员密码，备份BIOS不需要密码')

            time.sleep(1)
            if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):

                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                             f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('WINDOWS下，设置管理员密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('SWINDOWS下，设置管理员密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD}\r\n', '\x08111111\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_LOCK_FAIL_MSG]):
            logging.info('WINDOWS下设置管理员密码，锁住BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('WINDOWS下设置管理员密码，锁住BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{password}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG]):
            logging.info('输入正确密码成功锁住BIOS')
            if re.search(SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
                logging.info('锁住BIOS，状态为锁住')
            else:
                stylelog.fail('锁住BIOS，状态不是锁住')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD}\r\n', '\x08111111\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_UNLOCK_FAIL_MSG]):
            logging.info('WINDOWS下设置管理员密码，解锁BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('WINDOWS下设置管理员密码，解锁BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{password}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG]):
            logging.info('输入正确密码成功解锁BIOS')
            if re.search(SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
                logging.info('解锁BIOS，状态为解锁')
            else:
                stylelog.fail('解锁BIOS，状态不是解锁')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        go_to_setup(password=password)
        del_psw(password)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0229', '[TC0229]WINDOWS下设置用户密码，保留升级BIOS', 'WINDOWS下设置用户密码，保留升级BIOS'))
def flash_tool_0229():
    """

    Name:   Windows下设置用户密码，保留升级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下保留升级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('WINDOWS下保留刷新BIOS，刷新后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0230', '[TC0230]WINDOWS下设置用户密码，保留降级BIOS', 'WINDOWS下设置用户密码，保留降级BIOS'))
def flash_tool_0230():
    """

    Name:   Windows下设置用户密码，保留降级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下保留降级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('WINDOWS下保留刷新BIOS，刷新后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0231', '[TC0231]WINDOWS下设置用户密码，完全升级BIOS', 'WINDOWS下设置用户密码，完全升级BIOS'))
def flash_tool_0231():
    """

    Name:   Windows下设置用户密码，完全升级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下完全升级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0232', '[TC0232]WINDOWS下设置用户密码，完全降级BIOS', 'WINDOWS下设置用户密码，完全降级BIOS'))
def flash_tool_0232():
    """

    Name:   Windows下设置用户密码，完全降级BIOS

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下完全降级BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    sign = False
    count = 0
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0233', '[TC0233]WINDOWS下设置用户密码只保留Setup,升级更新BIOS', 'WINDOWS下设置用户只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0233():
    """

    Name:   Windows下设置用户只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('WINDOWS下只保留Setup,刷新BIOS后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('WINDOWS下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0234', '[TC0234]WINDOWS下设置用户密码只保留Setup,降级更新BIOS', 'WINDOWS下设置用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0234():
    """

    Name:   Windows下设置用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=password)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('WINDOWS下只保留Setup,刷新BIOS后密码保留')
            del_psw_user(password)
        else:
            stylelog.fail('WINDOWS下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0235', '[TC0235]WINDOWS下设置用户密码只保留SMBIOS,升级更新BIOS', 'WINDOWS下设置用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0235():
    """

    Name:   Windows下设置用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0236', '[TC0236]WINDOWS下设置用户密码只保留SMBIOS,降级更新BIOS', 'WINDOWS下设置用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0236():
    """

    Name:   Windows下设置用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，用户密码

    Result: 3.刷新BIOS需要输入密码，输入错误密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_user(password)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS}\r\n', '\x08111111\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，刷新BIOS时要求输入BIOS密码,输入错误密码，提示密码错误')
        else:
            stylelog.fail('设置用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS}\r\n', f'\x08{password}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=password)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_user(password)
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0237', '[TC0237]WINDOWS下设置用户密码,更新OA3', 'WINDOWS下设置用户密码,更新OA3'))
def flash_tool_0237():
    return core.Status.Skip


@core.test_case(('0238', '[TC0238]WINDOWS下设置用户密码,备份BIOS,锁住BIOS测试', 'WINDOWS下设置用户密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0238():
    """

    Name:   Windows下设置用户密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置用户密码
            2.Windows下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输错密码提示密码错误
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BACKUP_CMD)[0]):
            logging.info('WINDOWS下，设置用户密码，备份BIOS不需要密码')

            time.sleep(1)
            if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):

                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                             f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('WINDOWS下，设置用户密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('SWINDOWS下，设置用户密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD}\r\n', '\x08111111\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_LOCK_FAIL_MSG]):
            logging.info('WINDOWS下设置用户密码，锁住BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('WINDOWS下设置用户密码，锁住BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{password}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG]):
            logging.info('输入正确密码成功锁住BIOS')
            if re.search(SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
                logging.info('锁住BIOS，状态为锁住')
            else:
                stylelog.fail('锁住BIOS，状态不是锁住')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD}\r\n', '\x08111111\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_UNLOCK_FAIL_MSG]):
            logging.info('WINDOWS下设置用户密码，解锁BIOS需要密码，输入错误密码，锁住失败')
        else:
            stylelog.fail('WINDOWS下设置用户密码，解锁BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{password}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG]):
            logging.info('输入正确密码成功解锁BIOS')
            if re.search(SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
                logging.info('解锁BIOS，状态为解锁')
            else:
                stylelog.fail('解锁BIOS，状态不是解锁')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        go_to_setup(password=password)
        del_psw_user(password)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0239', '[TC0239]WINDOWS下同时设置管理员密码，用户密码，保留升级BIOS', 'WINDOWS下同时设置管理员密码，用户密码，保留升级BIOS'))
def flash_tool_0239():
    """

    Name:   Windows下同时设置管理员，用户密码，保留升级BIOS

    Steps:  1.SetUp下设置管理员密码，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下保留升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('WINDOWS下保留刷新BIOS，刷新后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0240', '[TC0240]WINDOWS下同时设置管理员密码，用户密码，保留降级BIOS', 'WINDOWS下同时设置管理员密码，用户密码，保留降级BIOS'))
def flash_tool_0240():
    """

    Name:   Windows下同时设置管理员密码，用户密码，保留降级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下保留降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS保留，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios()
        if result_psw == [True, True]:
            logging.info('WINDOWS下保留刷新BIOS，刷新后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有保留')
            count += 1
        if result == True:
            logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
            else:
                stylelog.fail('WINDOWS下保留刷新BIOS，刷新BIOS后SMBIOS保留')
                count += 1

        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0241', '[TC0241]WINDOWS下同时设置管理员密码，用户密码，完全升级BIOS', 'WINDOWS下同时设置管理员密码，用户密码，完全升级BIOS'))
def flash_tool_0241():
    """

    Name:   Windows下设置管理员，用户密码，完全升级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下完全升级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_LATEST_ALL}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0242', '[TC0242]WINDOWS下同时设置管理员密码，用户密码，完全降级BIOS', 'WINDOWS下同时设置管理员密码，用户密码，完全降级BIOS'))
def flash_tool_0242():
    """

    Name:   Windows下同时设置管理员密码，用户密码，完全降级BIOS

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下完全降级BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS恢复默认值，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_FLASH_CMD_PREVIOUS_ALL}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')

        time.sleep(5)
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认值:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新后密码被删除')
        else:
            stylelog.fail('WINDOWS下保留刷新BIOS，刷新后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后配置变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下完全刷新BIOS，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0243', '[TC0243]WINDOWS下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS', 'WINDOWS下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0243():
    """

    Name:   Windows下同时设置管理员密码，用户密码只保留Setup,升级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_LATEST}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('WINDOWS下只保留Setup,刷新BIOS后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('WINDOWS下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)

        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0244', '[TC0244]WINDOWS下同时设置管理员密码，用户密码只保留Setup,降级更新BIOS', 'WINDOWS下同时设置管理员密码，用户密码只保留Setup,降级更新BIOS，SMBIOS恢复默认'))
def flash_tool_0244():
    """

    Name:   Windows下同时设置管理员密码，用户密码,只保留Setup,降级更新BIOS，SMBIOS恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留Setup,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值保留，SMBIOS恢复默认值，密码保留
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=admin)
        changed_options = get_options_value()
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVNVM_CMD_PREVIOUS}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        time.sleep(5)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'刷新前:{changed_options}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_reserve(changed_options, updated_options)
        result_smbios = compare_smbios_default()
        if result_psw == [True, True]:
            logging.info('WINDOWS下只保留Setup,刷新BIOS后密码保留')
            del_psw_all(admin, user)
        else:
            stylelog.fail('WINDOWS下只保留Setup,刷新BIOS后密码被删除')
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留Setup，刷新BIOS后配置没有改变')
            if result_smbios == True:
                logging.info('WINDOWS下只保留Setup，刷新BIOS后SMBIOS恢复默认值')
            else:
                stylelog.fail('WINDOWS下只保留Setup，刷新BIOS后SMBIOS没有恢复默认值')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0245', '[TC0245]WINDOWS下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS', 'WINDOWS下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认'))
def flash_tool_0245():
    """

    Name:   Windows下同时设置管理员密码，用户密码只保留SMBIOS,升级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,升级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_LATEST}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)

        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(
    ('0246', '[TC0246]WINDOWS下同时设置管理员密码，用户密码只保留SMBIOS,降级更新BIOS', 'WINDOWS下同时设置管理员密码，用户密码只保留SMBIOS,降级更新BIOS，SetUp恢复默认'))
def flash_tool_0246():
    """

    Name:   Windows下同时设置管理员密码，用户密码,只保留SMBIOS,降级更新BIOS，SetUp恢复默认

    Steps:  1.SetUp下设置管理员，用户密码,修改选项的值为非默认值，保存重启
            2.改变SMBIOS值
            3.Windows下只保留SMBIOS,降级更新BIOS
            4.检查选项值，SMBIOS值，管理员密码

    Result: 3.刷新BIOS需要输入密码，输入用户密码提示密码错误，输入正确密码成功刷新
            4.选项值恢复默认值，SMBIOS保留，密码删除
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        assert set_password_all(admin, user)
        change_options_value()
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        change_smbios()
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS}\r\n', f'\x08{user}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，刷新BIOS时要求输入BIOS密码,输入用户密码，提示密码错误')
        else:
            stylelog.fail('同时设置管理员密码，用户密码，刷新BIOS时,没有要求输入密码')
            return
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_RESVSMBIOS_CMD_PREVIOUS}\r\n', f'\x08{admin}\r\n'],
                              [f'{SutConfig.Tool.TOOL_PASSWORD_MSG}', SutConfig.Tool.WINDOWS_MSG_NOR]):
            logging.info('输入正确密码，BIOS更新完成')
        SetUpLib.reboot()
        time.sleep(200)
        result_psw = go_to_setup(password=admin)
        updated_options = get_options_value()
        logging.info(f'默认:{SutConfig.Tool.DEFAULT_OPTION_VALUE}')
        logging.info(f'刷新后:{updated_options}')
        result = compare_all(updated_options)
        result_smbios = compare_smbios()
        if result_psw == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后密码被删除')
        else:
            stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后密码没有被删除')
            del_psw_all(admin, user)
            count += 1
        if result == True:
            logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后选项变为默认值')
            if result_smbios == True:
                logging.info('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')

            else:
                stylelog.fail('WINDOWS下只保留SMBIOS，刷新BIOS后SMBIOS保留，没有改变')
                count += 1
        else:
            count += 1
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0247', '[TC0247]WINDOWS下同时设置管理员密码，用户密码,更新OA3', 'WINDOWS下设置管理员密码,更新OA3'))
def flash_tool_0247():
    return core.Status.Skip


@core.test_case(('0248', '[TC0248]WINDOWS下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试', 'WINDOWS下设置管理员密码,备份BIOS,锁住BIOS测试'))
def flash_tool_0248():
    """

    Name:   Windows下同时设置管理员密码，用户密码,备份BIOS,锁住BIOS测试

    Steps:  1.SetUp下设置管理员密码
            2.Windows下备份BIOS
            3.锁住工具
            4.解锁工具

    Result: 2.不需要输入密码
            3/4.需要密码，输入用户密码提示密码错误
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_all(admin, user)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_windows_os()

        if re.search(SutConfig.Tool.WINDOWS_BACKUP_SUC_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BACKUP_CMD)[0]):
            logging.info('WINDOWS下，同时设置管理员密码，用户密码，备份BIOS不需要密码')

            time.sleep(1)
            if re.search(SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1],
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'dir', decoding='gbk')[0]):

                logging.info('成功生成备份文件')
                time.sleep(1)
                SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                             f"del {SutConfig.Tool.WINDOWS_BACKUP_CMD.split(' ')[-1]}")
                time.sleep(1)
            else:
                stylelog.fail('WINDOWS下，同时设置管理员密码，用户密码可以备份文件，但没有生成备份文件')
                count += 1
        else:
            stylelog.fail('SWINDOWS下，同时设置管理员密码，用户密码，备份BIOS失败')
            count += 1
        time.sleep(1)
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{user}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_LOCK_FAIL_MSG]):
            logging.info('WINDOWS下同时设置管理员密码，用户密码，锁住BIOS需要密码，输入用户密码，锁住失败')
        else:
            stylelog.fail('WINDOWS下同时设置管理员密码，用户密码，锁住BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_LOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{admin}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_LOCK_BIOS_MSG]):
            logging.info('输入正确密码成功锁住BIOS')
            if re.search(SutConfig.Tool.WINDOWS_LOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
                logging.info('锁住BIOS，状态为锁住')
            else:
                stylelog.fail('锁住BIOS，状态不是锁住')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{user}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_UNLOCK_FAIL_MSG]):
            logging.info('WINDOWS下同时设置管理员密码，用户密码，解锁BIOS需要密码，输入用户密码，锁住失败')
        else:
            stylelog.fail('WINDOWS下同时设置管理员密码，用户密码，解锁BIOS不需要密码')
            count += 1
        if SshLib.interaction(Sut.OS_LEGACY_SSH,
                              [f'{SutConfig.Tool.WINDOWS_UNLOCK_BIOS_UPDATE_CMD}\r\n', f'\x08{admin}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_UNLOCK_BIOS_MSG]):
            logging.info('输入正确密码成功解锁BIOS')
            if re.search(SutConfig.Tool.WINDOWS_UNLOCK_STATUS_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_LOCK_STATUS_CMD)[0]):
                logging.info('解锁BIOS，状态为解锁')
            else:
                stylelog.fail('解锁BIOS，状态不是解锁')
                count += 1
        else:
            stylelog.fail('输入正确密码，锁住BIOS失败')
            count += 1
        go_to_setup(password=admin)
        del_psw_all(admin, user)

        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)

        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0249', '[TC0249]WINDOWS下设置管理员密码,Flash 工具清除密码测试', 'WINDOWS下设置管理员密码,Flash 工具清除密码测试'))
def flash_tool_0249():
    """

    Name:   Windows下设置管理员密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置管理员密码
            2.Windows下工具清除密码

    Result: 2.输入错误密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    password = get_random_password()
    try:
        assert SetUpLib.boot_to_setup()
        set_password(password)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_CLEAN_PSW_CMD}\r\n', '\x0811111\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置管理员密码，工具清除密码，需要输入密码,输入错误密码，提示密码错误')
            time.sleep(2)
            if SshLib.interaction(Sut.OS_LEGACY_SSH,
                                  [f'{SutConfig.Tool.WINDOWS_CLEAN_PSW_CMD}\r\n', f'\x08{password}\r\n'],
                                  [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_CLEAN_PSW_MSG]):
                logging.info('设置管理员密码，工具清除密码，需要输入密码,输入正确密码，成功清除')
            else:
                stylelog.fail('输入正确密码，没有清除密码')
                count += 1
        else:
            stylelog.fail('设置管理员密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=password) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)

        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(password)


@core.test_case(('0250', '[TC0250]WINDOWS下设置用户密码,Flash 工具清除密码测试', 'WINDOWS下设置用户密码,Flash 工具清除密码测试'))
def flash_tool_0250():
    """

    Name:   Windows下设置用户密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置用户密码
            2.Windows下工具清除密码

    Result: 2.输入错误密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    password = get_random_password()
    try:

        assert SetUpLib.boot_to_setup()
        set_password_user(password)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_CLEAN_PSW_CMD}\r\n', '\x0811111\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('设置用户密码，工具清除密码，需要输入密码,输入错误密码，提示密码错误')
            time.sleep(2)
            if SshLib.interaction(Sut.OS_LEGACY_SSH,
                                  [f'{SutConfig.Tool.WINDOWS_CLEAN_PSW_CMD}\r\n', f'\x08{password}\r\n'],
                                  [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_CLEAN_PSW_MSG]):
                logging.info('设置用户密码，工具清除密码，需要输入密码,输入正确密码，成功清除')
            else:
                stylelog.fail('输入正确密码，没有清除密码')
                count += 1
        else:
            stylelog.fail('设置用户密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=password) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw_user(password)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_user(password)


@core.test_case(('0251', '[TC0251]WINDOWS下同时设置管理员密码，用户密码,Flash 工具清除密码测试', 'WINDOWS下同时设置管理员密码，用户密码,Flash 工具清除密码测试'))
def flash_tool_0251():
    """

    Name:   Windows下设置管理员，用户密码,Flash 工具清除密码测试

    Steps:  1.SetUp下设置管理员，用户密码
            2.Windows下工具清除密码

    Result: 2.输入用户密码，提示密码错误，输入正确密码成功清楚密码
    """
    count = 0
    sign = False
    admin = get_random_password()
    user = get_random_password()
    try:
        assert SetUpLib.boot_to_setup()
        set_password_all(admin, user)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_windows_os()

        if SshLib.interaction(Sut.OS_LEGACY_SSH, [f'{SutConfig.Tool.WINDOWS_CLEAN_PSW_CMD}\r\n', f'\x08{user}\r\n'],
                              [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WRONG_PSW_MSG]):
            logging.info('同时设置管理员密码，用户密码，工具清除密码，需要输入密码,输入用户密码，提示密码错误')
            time.sleep(2)
            if SshLib.interaction(Sut.OS_LEGACY_SSH,
                                  [f'{SutConfig.Tool.WINDOWS_CLEAN_PSW_CMD}\r\n', f'\x08{admin}\r\n'],
                                  [SutConfig.Tool.TOOL_PASSWORD_MSG, SutConfig.Tool.WINDOWS_CLEAN_PSW_MSG]):
                logging.info('同时设置管理员密码，用户密码，工具清除密码，需要输入密码,输入正确密码，成功清除')
            else:
                stylelog.fail('输入正确密码，没有清除密码')
                count += 1
        else:
            stylelog.fail('同时设置管理员密码，用户密码，工具清除密码，不需要输入密码')
            count += 1
        if go_to_setup(password=admin) == True:
            logging.info('密码被清除')
        else:
            stylelog.fail('密码没有被清除')
            count += 1
            del_psw_all(admin, user)
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            go_to_setup_del_psw(admin, user)


@core.test_case(('0252', '[TC0252]WINDOWS下负面测试(错误BIOS,错误OA3,错误命令参数)', 'WINDOWS下负面测试(错误BIOS,错误OA3,错误命令参数)'))
def flash_tool_0252():
    """

    Name:   Windows下负面测试(错误BIOS,错误OA3,错误命令参数)

    Steps:  1.Windows下工具不输入参数
            2.输入错误参数
            3.更新其他平台BIOS
            4.更新为签名的BIOS

    Result: 1/2.提示信息显示正确
            3/4.无法更新
    """
    try:
        count = 0
        assert SetUpLib.boot_to_windows_os()
        if re.search(SutConfig.Tool.WINDOWS_INPUT_ERR_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_EMPTY_CMD)[0]):
            logging.info('WINDOWS 工具不输入参数，提示输入错误')
        else:
            stylelog.fail('WINDOWS 工具不输入参数，没有提示输入错误')
            count += 1
            time.sleep(200)
        time.sleep(2)
        if re.search(SutConfig.Tool.WINDOWS_INPUT_ERR_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_ERROR_CMD)[0]):
            logging.info('WINDOWS 工具输入错误参数，提示输入错误')
        else:
            stylelog.fail('WINDOWS 工具输入错误参数，没有提示输入错误')
            count += 1
            time.sleep(200)
        time.sleep(2)
        if re.search(SutConfig.Tool.WINDOWS_UPDATE_OTHERS_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_OTHERS)[0]):
            logging.info('WINDOWS 下更新其他平台的BIOS，提示无法更新')
            time.sleep(2)
        else:
            stylelog.fail('WINDOWS下可以更新其他平台的BIOS')
            count += 1
            time.sleep(200)
        if re.search(SutConfig.Tool.WINDOWS_UPDATE_UNSIGNED_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_FLASH_CMD_UNSIGNED)[0]):
            logging.info('WINDOWS 下更新未签名的BIOS，提示无法更新')
        else:
            stylelog.fail('WINDOWS下可以更新未签名的BIOS')
            count += 1
            time.sleep(200)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
