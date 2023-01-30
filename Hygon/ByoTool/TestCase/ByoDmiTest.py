# -*- encoding=utf8 -*-
from ByoTool.Config import *
from ByoTool.BaseLib import *


def check_diff(log1, log2):
    def check_charset(file_path):
        with open(file_path, "rb") as f:
            data = f.read(4)
            charset = chardet.detect(data)['encoding']
        return charset

    logging.info("Comparing {0} and {1}".format(log1, log2))
    try:
        with open(log1, 'r', encoding=check_charset(log1)) as f:
            content_log1 = f.read().splitlines()
        with open(log2, 'r', encoding=check_charset(log2)) as f:
            content_log2 = f.read().splitlines()
    except FileNotFoundError:
        logging.error("Please check whether log file exists.")
        return True
    d = difflib.Differ()
    diffs = list(d.compare(content_log1, content_log2))
    res = []
    for diff in diffs:
        if not re.search("^\s", diff):
            res.append(diff)
    return res


def _update_bios_all():
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


@core.test_case(('1001', '[TC1001]Shell下检查ByoDmi版本，帮助信息', 'Shell下检查ByoDmi版本，帮助信息'))
def byodmi_tool_1001():
    """
    Name:   Shell下检查ByoDmi版本，帮助信息

    Steps:  1.Shell下检查ByoDmi工具的版本，帮助信息

    Result: 1.版本，帮助信息显示正确
    """
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYODMI_VERSION_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYODMI_VERSION_CONFIRM_MSG, 5):

            logging.info('Shell下工具版本验证成功')
        else:
            stylelog.fail('Shell下工具版本验证失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYODMI_HELP_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYODMI_HELP_CONFIRM_MSG, 5):
            logging.info('Shell下工具帮助信息验证成功')
        else:
            stylelog.fail('Shell下工具帮助信息验证失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1002', '[TC1002]Shell下检查ByoDmi,SMBIOS 信息', 'Shell下检查ByoDmi,SMBIOS 信息'))
def byodmi_tool_1002():
    """
    Name:   Shell下检查ByoDmi,SMBIOS 信息

    Steps:  1.对比本地的SMBIOS和工具读取的SMBIOS

    Result: 1.两者一致
    """
    try:
        count = 0
        assert _update_bios_all()
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter('rm -q SMBIOS')
        time.sleep(2)
        SetUpLib.send_data_enter('mkdir SMBIOS')
        time.sleep(2)
        if os.path.exists('ByoTool/Tools/SMBIOS'):
            shutil.rmtree('ByoTool/Tools/SMBIOS')
        os.mkdir('ByoTool/Tools/SMBIOS')
        types = [0, 1, 2, 3, 4, 7, 8, 9, 11, 12, 13, 16, 17, 19, 20, 23, 32, 38, 39, 41, 127]
        for type in types:
            type_file = 'type' + str(type) + '.txt'
            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_VIEWALL_CMD} {type} > SMBIOS\{type_file}')
            time.sleep(2)
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        for type in types:
            type_file = 'type' + str(type) + '.txt'
            type_file_linux = f'{SutConfig.Env.LINUX_BIOS_MOUNT_PATH}SMBIOS/' + type_file
            SshLib.sftp_download_file(Sut.OS_SFTP, type_file_linux, 'ByoTool/Tools/SMBIOS/{0}'.format(type_file))
            time.sleep(1)
        time.sleep(2)
        for type in types:
            logging.info(f'检查SMBIOS,Type{type}')
            differs = check_diff('{0}type{1}.txt'.format(SutConfig.Tool.SMBIOS_PATH_SHELL, str(type)),
                                 'ByoTool/Tools/SMBIOS/type{0}.txt'.format(str(type)))
            if len(differs) == 0:
                logging.info(f'SMBIOS Type{type}验证通过')
            else:
                for differ in differs:
                    stylelog.fail(f'SMBIOS Type{type}验证失败')
                    stylelog.fail(differ)
                    count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1003', '[TC1003]ShellByoDmi修改SMBIOS，验证', 'ShellByoDmi修改SMBIOS，验证'))
def byodmi_tool_1003():
    """
    Name:   ShellByoDmi修改SMBIOS，验证

    Steps:  1.Shell下ByoDmi工具修改smbios信息
            2.ByoDmi工具自动设置UUID

    Result: 1.修改，验证成功
            2.UUID修改成功
    """

    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        for key, value in SutConfig.Tool.BYODMI_SMBIOS_CHANGE.items():
            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_TYPE_CMD} {key} {value}')
            time.sleep(2)

        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        for key, value in SutConfig.Tool.BYODMI_SMBIOS_CHANGE.items():
            if key == '1 0 8':
                SetUpLib.send_data_enter(f'smbiosview -t {key[0]}')
                data = SetUpLib.get_data(3)
                if all(i.lower() in data.lower() for i in value.split(' ')):
                    logging.info(f'修改{key}为{value}成功')
                else:
                    stylelog.fail(f'修改{key}为{value}失败')
                    count += 1
            else:
                SetUpLib.send_data_enter(f'smbiosview -t {key[0]}')
                if SetUpLib.wait_message(value, 6):
                    logging.info(f'修改{key}为{value}成功')
                else:
                    stylelog.fail(f'修改{key}为{value}失败')
                    count += 1
        logging.info('ByoDmi自动设置UUID')
        time.sleep(1)
        SetUpLib.send_data_enter(f'smbiosview -t 1')
        old_uuid = SetUpLib.get_data(3)
        time.sleep(1)
        SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_TYPE_CMD} 1 0 8 auto')
        time.sleep(2)
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        time.sleep(1)
        SetUpLib.send_data_enter(f'smbiosview -t 1')
        new_uuid = SetUpLib.get_data(3)
        logging.debug(old_uuid)
        logging.debug(new_uuid)
        if new_uuid != old_uuid:
            for i in old_uuid:
                if i not in new_uuid:
                    logging.info(f'修改前的UUID{i}')
            for i in new_uuid:
                if i not in old_uuid:
                    logging.info(f'修改后的UUID{i}')
            logging.info('ByoDmi自动设置UUID成功')
        else:
            stylelog.fail('ByoDmi自动设置UUID失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1004', '[TC1004]Shell下ByoDmi锁住测试', 'Shell下ByoDmi锁住测试'))
def byodmi_tool_1004():
    """
    Name:   Shell下ByoDmi锁住测试

    Steps:  1.Shell下锁住ByoDmi工具
            2.检查是否可以查看SMBIOS信息
            3.检查是否可以修改SMBIOS信息
            4.解锁ByoDmi工具
            5.检查解锁后是否可以修改SMBIOS信息

    Result: 1.工具锁住成功
            2.可以查看SMBIOS信息
            3.不能修改SMBIOS信息
            4.工具解锁成功
            5.可以修改SMBIOS信息
    """
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYODMI_LOCK_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYODMI_LOCK_MSG, 5):
            logging.info('ByoDmi锁住成功')
            time.sleep(1)
            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_VIEWALL_CMD} 1')
            if SetUpLib.wait_message('Type1 message', 5):
                logging.info('ByoDmi锁住,可以查看SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住,不能查看SMBIOS信息')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_VIEW_CMD} 1 0 5')
            if SetUpLib.wait_message('Type1 message', 5):
                logging.info('ByoDmi锁住,可以查看SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住,不能查看SMBIOS信息')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_TYPE_CMD} 1 0 5 oem105')
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYODMI_LOCK_RUN_MSG, 5):
                logging.info('ByoDmi锁住不能修改SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住可以修改SMBIOS信息')
                count += 1
            time.sleep(1)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYODMI_UNLOCK_CMD)
            if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYODMI_UNLOCK_MSG, 5):
                logging.info('ByoDmi解锁成功')
                time.sleep(1)
                SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYODMI_TYPE_CMD} 1 0 5 oem105')
                if SetUpLib.wait_message('Success', 5):
                    logging.info('ByoDmi解锁后可以修改SMBIOS信息')
                else:
                    stylelog.fail('ByoDmi解锁后仍不可以修改SMBIOS信息')
                    count += 1
            else:
                stylelog.fail('ByoDmi解锁失败')
                count += 1
        else:
            stylelog.fail('ByoDmi锁住失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1005', '[TC1005]Shell下ByoDmi负面测试', 'Shell下ByoDmi负面测试'))
def byodmi_tool_1005():
    """
    Name:   Shell下ByoDmi负面测试

    Steps:  1.Shell下ByoDmi工具输入错误的参数
            2.输入超出范围的Type号
            3.-view输入无效的Type号
            4.-view只输入Type号
            5.-view输入超出范围的Type号

    Result: 1/2/3/4/5.提示信息显示正确
    """
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(f"{SutConfig.Tool.SHELL_BYODMI_VIEWALL_CMD} abc")
        if SetUpLib.wait_message('Input Error|Input type number offset should be dec', 3):

            logging.info('-viewall输入无效Type号，提示Input Error')
        else:
            stylelog.fail(('-viewall输入无效Type号，没有提示Input Error'))
            count += 1
        time.sleep(2)
        SetUpLib.send_data_enter(f"{SutConfig.Tool.SHELL_BYODMI_VIEWALL_CMD} 200")
        if SetUpLib.wait_message('Type200 not exist', 3):
            logging.info('-viewall输入超出范围的Type号，结果提示正确')
        else:
            stylelog.fail('-viewall输入超出范围的Type号，结果提示有误')
            count += 1
        time.sleep(2)
        SetUpLib.send_data_enter(f"{SutConfig.Tool.SHELL_BYODMI_VIEW_CMD} a 0 a")
        if SetUpLib.wait_message('Input Error|Input type number offset should be dec', 5):
            logging.info('-view输入无效Type号，提示Input Error')
        else:
            stylelog.fail('-view输入无效Type号，没有提示Input Error')
            count += 1
        time.sleep(2)
        SetUpLib.send_data_enter(f"{SutConfig.Tool.SHELL_BYODMI_VIEW_CMD} a")
        if SetUpLib.wait_message('Input Error|Not support parameter', 3):

            logging.info('-view只输入Type号，结果为Input Error')
        else:
            stylelog.fail('-view只输入Type号，结果不为Input Error')
            count += 1
        time.sleep(2)
        SetUpLib.send_data_enter(f"{SutConfig.Tool.SHELL_BYODMI_VIEW_CMD} 200 0 2")
        if SetUpLib.wait_message('Number is invalid', 5):
            logging.info('-view输入超出范围的Type号，提示Number is invalid')
        else:
            stylelog.fail('-view输入超出范围的Type号，没有提示Number is invalid')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1101', '[TC1101]Linux下检查ByoDmi版本，帮助信息', 'Linux下检查ByoDmi版本，帮助信息'))
def byodmi_tool_1101():
    """
    Name:   Linux下检查ByoDmi版本，帮助信息

    Steps:  1.Linux下检查ByoDmi工具的版本，帮助信息

    Result: 1.版本，帮助信息显示正确
    """
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        if re.search(SutConfig.Tool.LINUX_BYODMI_VERSION_CONFIRM_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYODMI_VERSION_CMD)[0]):
            logging.info('Linux下工具版本验证成功')
        else:
            stylelog.fail('Linux下工具版本验证失败')
            count += 1
        if re.search(SutConfig.Tool.LINUX_BYODMI_HELP_CONFIRM_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYODMI_HELP_CMD)[0]):
            logging.info('Linux下工具帮助信息验证成功')
        else:
            stylelog.fail('Linux下工具帮助信息验证失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1102', '[TC1102]Linux下检查ByoDmi,SMBIOS 信息', 'Linux下检查ByoDmi,SMBIOS 信息'))
def byodmi_tool_1102():
    """
    Name:   Linux下检查ByoDmi,SMBIOS 信息

    Steps:  1.对比本地的SMBIOS和工具读取的SMBIOS

    Result: 1.两者一致
    """
    try:
        count = 0
        assert _update_bios_all()
        assert SetUpLib.boot_to_linux_os()
        SshLib.execute_command_limit(Sut.OS_SSH, 'rm -rf SMBIOS;mkdir SMBIOS')
        if os.path.exists('ByoTool/Tools/SMBIOS'):
            shutil.rmtree('ByoTool/Tools/SMBIOS')
        os.mkdir('ByoTool/Tools/SMBIOS')
        types = [0, 1, 2, 3, 4, 7, 8, 9, 11, 12, 13, 16, 17, 19, 20, 23, 32, 38, 39, 41, 127]
        for type in types:
            type_file = 'type' + str(type) + '.txt'
            SshLib.execute_command_limit(Sut.OS_SSH, "./ByoDmi -viewall {0} > SMBIOS/{1}".format(type, type_file))
            type_file_linux = 'SMBIOS/' + type_file
            SshLib.sftp_download_file(Sut.OS_SFTP, type_file_linux, 'ByoTool/Tools/SMBIOS/{0}'.format(type_file))
        time.sleep(2)
        for type in types:
            logging.info(f'检查SMBIOS,Type{type}')
            differs = check_diff('{0}type{1}.txt'.format(SutConfig.Tool.SMBIOS_PATH_LINUX, str(type)),
                                 'ByoTool/Tools/SMBIOS/type{0}.txt'.format(str(type)))
            if len(differs) == 0:
                logging.info(f'SMBIOS Type{type}验证通过')
            else:
                for differ in differs:
                    stylelog.fail(f'SMBIOS Type{type}验证失败')
                    stylelog.fail(differ)
                    count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1103', '[TC1103]LinuxByoDmi修改SMBIOS，验证', 'LinuxByoDmi修改SMBIOS，验证'))
def byodmi_tool_1103():
    """
    Name:   LinuxByoDmi修改SMBIOS，验证

    Steps:  1.Linux下ByoDmi工具修改smbios信息
            2.ByoDmi工具自动设置UUID

    Result: 1.修改，验证成功
            2.UUID修改成功
    """
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        for key, value in SutConfig.Tool.BYODMI_SMBIOS_CHANGE.items():
            SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYODMI_TYPE_CMD} {key} {value}')
            time.sleep(1)
        assert SetUpLib.boot_to_linux_os()
        for key, value in SutConfig.Tool.BYODMI_SMBIOS_CHANGE.items():
            if key == '1 0 8':
                data = SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t {key[0]}')[0]
                if all(i in data for i in value.split(' ')):
                    logging.info(f'修改{key}为{value}成功')
                else:
                    stylelog.fail(f'修改{key}为{value}失败')
            else:
                if re.search(value, SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t {key[0]}')[0]):
                    logging.info(f'修改{key}为{value}成功')
                else:
                    stylelog.fail(f'修改{key}为{value}失败')
                    logging.debug(SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t {key[0]}')[0])
                    count += 1
        old_uuid = re.findall('uuid: *(.*)', SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t 1')[0], re.I)
        time.sleep(1)
        SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYODMI_TYPE_CMD} 1 0 8 auto')
        time.sleep(1)
        assert SetUpLib.boot_to_linux_os()
        new_uuid = re.findall('uuid: *(.*)', SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t 1')[0], re.I)
        logging.debug(old_uuid)
        logging.debug(new_uuid)
        if old_uuid != new_uuid and len(new_uuid) == len(old_uuid):
            logging.info('ByoDmi工具自动修改UUID成功')
        else:
            stylelog.fail('ByoDmi工具自动修改UUID失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1104', '[TC1104]Linux下ByoDmi锁住测试', 'Linux下ByoDmi锁住测试'))
def byodmi_tool_1104():
    """
    Name:   Linux下ByoDmi锁住测试

    Steps:  1.Linux下锁住ByoDmi工具
            2.检查是否可以查看SMBIOS信息
            3.检查是否可以修改SMBIOS信息
            4.解锁ByoDmi工具
            5.检查解锁后是否可以修改SMBIOS信息

    Result: 1.工具锁住成功
            2.可以查看SMBIOS信息
            3.不能修改SMBIOS信息
            4.工具解锁成功
            5.可以修改SMBIOS信息
    """
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        if re.search(SutConfig.Tool.LINUX_BYODMI_LOCK_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYODMI_LOCK_CMD)[0]):
            logging.info('ByoDmi锁住成功')
            if re.search('Type1 message',
                         SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYODMI_VIEWALL_CMD} 1')[0]):
                logging.info('ByoDmi锁住,可以查看SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住,不能查看SMBIOS信息')
                count += 1
            if re.search('Type1 message',
                         SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYODMI_VIEW_CMD} 1 0 5')[0]):
                logging.info('ByoDmi锁住,可以查看SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住,不能查看SMBIOS信息')
                count += 1
            if re.search(SutConfig.Tool.LINUX_BYODMI_LOCK_RUN_MSG, SshLib.execute_command_limit(Sut.OS_SSH,
                                                                                                f'{SutConfig.Tool.LINUX_BYODMI_TYPE_CMD} 1 0 5 oem105')[
                0]):
                logging.info('ByoDmi锁住不能修改SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住可以修改SMBIOS信息')
                count += 1
            if re.search(SutConfig.Tool.LINUX_BYODMI_UNLOCK_MSG,
                         SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYODMI_UNLOCK_CMD)[0]):
                logging.info('ByoDmi解锁成功')
                if re.search('Succeed', SshLib.execute_command_limit(Sut.OS_SSH,
                                                                     f'{SutConfig.Tool.LINUX_BYODMI_TYPE_CMD} 1 0 5 oem105')[
                    0]):
                    logging.info('ByoDmi解锁后可以修改SMBIOS信息')
                else:
                    stylelog.fail('ByoDmi解锁后仍不可以修改SMBIOS信息')
                    count += 1
            else:
                stylelog.fail('ByoDmi解锁失败')
                count += 1
        else:
            stylelog.fail('ByoDmi锁住失败')
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1105', '[TC1105]Linux下ByoDmi负面测试', 'Linux下ByoDmi负面测试'))
def byodmi_tool_1105():
    """
    Name:   Linux下ByoDmi负面测试

    Steps:  1.Linux下ByoDmi工具输入错误的参数
            2.输入超出范围的Type号
            3.-view输入无效的Type号
            4.-view只输入Type号
            5.-view输入超出范围的Type号

    Result: 1/2/3/4/5.提示信息显示正确
    """
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search('Input Error',
                     SshLib.execute_command_limit(Sut.OS_SSH, f"{SutConfig.Tool.LINUX_BYODMI_VIEWALL_CMD} abc")[0]):
            logging.info('-viewall输入无效Type号，提示Input Error')
        else:
            stylelog.fail(('-viewall输入无效Type号，没有提示Input Error'))
            count += 1
        if re.search('Invalid type or handle',
                     SshLib.execute_command_limit(Sut.OS_SSH, f"{SutConfig.Tool.LINUX_BYODMI_VIEWALL_CMD} 200")[0]):
            logging.info('-viewall输入超出范围的Type号，结果为Invalid type or handle')
        else:
            stylelog.fail('-viewall输入超出范围的Type号，结果不为Invalid type or handle')
            count += 1
        if re.search('Input Error',
                     SshLib.execute_command_limit(Sut.OS_SSH, f"{SutConfig.Tool.LINUX_BYODMI_VIEW_CMD} a 0 a")[0]):
            logging.info('-view输入无效Type号，提示Input Error')
        else:
            stylelog.fail('-view输入无效Type号，没有提示Input Error')
            count += 1
        if re.search('Input Error|Not support parameter',
                     SshLib.execute_command_limit(Sut.OS_SSH, f"{SutConfig.Tool.LINUX_BYODMI_VIEW_CMD} a")[0]):
            logging.info('-view只输入Type号，结果为Input Error')
        else:
            stylelog.fail('-view只输入Type号，结果不为Input Error')
            count += 1
        if re.search('Invalid type or handle',
                     SshLib.execute_command_limit(Sut.OS_SSH, f"{SutConfig.Tool.LINUX_BYODMI_VIEW_CMD} 200 0 2")[0]):
            logging.info('-view输入超出范围的Type号，提示Invalid type or handle')
        else:
            stylelog.fail('-view输入超出范围的Type号，没有提示Invalid type or handle')
            count += 1
        if count == 0:
            return True
        else:
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1201', '[TC1201]Windows下检查ByoDmi版本，帮助信息', 'Windows下检查ByoDmi版本，帮助信息'))
def byodmi_tool_1201():
    """
    Name:   Windows下检查ByoDmi版本，帮助信息

    Steps:  1.Windows下检查ByoDmi工具的版本，帮助信息

    Result: 1.版本，帮助信息显示正确
    """
    try:
        count = 0
        assert SetUpLib.boot_to_windows_os()
        if re.search(SutConfig.Tool.WINDOWS_BYODMI_VERSION_CONFIRM_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BYODMI_VERSION_CMD)[0]):
            logging.info('Windows下工具版本验证成功')
        else:
            stylelog.fail('Windows下工具版本验证失败')
            count += 1
        if re.search(SutConfig.Tool.WINDOWS_BYODMI_HELP_CONFIRM_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BYODMI_HELP_CMD)[0]):
            logging.info('Windows下工具帮助信息验证成功')
        else:
            stylelog.fail('Windows下工具帮助信息验证失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1202', '[TC1202]Windows下检查ByoDmi,SMBIOS 信息', 'Windows下检查ByoDmi,SMBIOS 信息'))
def byodmi_tool_1202():
    """
    Name:   Windows下检查ByoDmi,SMBIOS 信息

    Steps:  1.对比本地的SMBIOS和工具读取的SMBIOS

    Result: 1.两者一致
    """
    try:
        count = 0
        assert _update_bios_all()
        assert SetUpLib.boot_to_windows_os()
        types = [0, 1, 2, 3, 4, 7, 8, 9, 11, 12, 13, 16, 17, 19, 20, 23, 32, 38, 39, 41, 127]
        SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'rmdir /S /Q SMBIOS', decoding='gbk')
        time.sleep(1)
        SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, 'mkdir SMBIOS', decoding='gbk')
        if os.path.exists('ByoTool/Tools/SMBIOS'):
            shutil.rmtree('ByoTool/Tools/SMBIOS')
        os.mkdir('ByoTool/Tools/SMBIOS')
        for type in types:
            type_file = 'type' + str(type) + '.txt'
            SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                         "ByoDmi.exe -viewall {0} > SMBIOS/{1}".format(type, type_file))
            type_file_linux = 'SMBIOS/' + type_file
            SshLib.sftp_download_file(Sut.OS_LEGACY_SFTP, type_file_linux,
                                      'ByoTool/Tools/SMBIOS/{0}'.format(type_file))
        time.sleep(2)
        for type in types:
            logging.info(f'检查SMBIOS,Type{type}')
            differs = check_diff('{0}type{1}.txt'.format(SutConfig.Tool.SMBIOS_PATH_WINDOWS, str(type)),
                                 'ByoTool/Tools/SMBIOS/type{0}.txt'.format(str(type)))
            if len(differs) == 0:
                logging.info(f'SMBIOS Type{type}验证通过')
            else:
                for differ in differs:
                    stylelog.fail(f'SMBIOS Type{type}验证失败')
                    stylelog.fail(differ)
                    count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1203', '[TC1203]WindowsByoDmi修改SMBIOS，验证', 'WindowsByoDmi修改SMBIOS，验证'))
def byodmi_tool_1203():
    """
    Name:   WindowsByoDmi修改SMBIOS，验证

    Steps:  1.Windows下ByoDmi工具修改smbios信息
            2.ByoDmi工具自动设置UUID

    Result: 1.修改，验证成功
            2.UUID修改成功
    """
    try:
        count = 0
        assert SetUpLib.boot_to_windows_os()
        for key, value in SutConfig.Tool.BYODMI_SMBIOS_CHANGE.items():
            SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f'{SutConfig.Tool.WINDOWS_BYODMI_TYPE_CMD} {key} {value}')
            time.sleep(1)
        assert SetUpLib.boot_to_linux_os()
        for key, value in SutConfig.Tool.BYODMI_SMBIOS_CHANGE.items():
            if key == '1 0 8':
                data = SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t {key[0]}')[0]
                if all(i in data for i in value.split(' ')):
                    logging.info(f'修改{key}为{value}成功')
                else:
                    stylelog.fail(f'修改{key}为{value}失败')
            else:
                if re.search(value, SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t {key[0]}')[0]):
                    logging.info(f'修改{key}为{value}成功')
                else:
                    stylelog.fail(f'修改{key}为{value}失败')
                    logging.debug(SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t {key[0]}')[0])
                    count += 1
        old_uuid = re.findall('uuid: *(.*)', SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t 1')[0], re.I)
        time.sleep(1)
        assert SetUpLib.boot_to_windows_os()
        SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f'{SutConfig.Tool.WINDOWS_BYODMI_TYPE_CMD} 1 0 8 auto')
        time.sleep(1)
        assert SetUpLib.boot_to_linux_os()
        new_uuid = re.findall('uuid: *(.*)', SshLib.execute_command_limit(Sut.OS_SSH, f'dmidecode -t 1')[0], re.I)
        logging.debug(old_uuid)
        logging.debug(new_uuid)
        if old_uuid != new_uuid and len(new_uuid) == len(old_uuid):
            logging.info('ByoDmi工具自动修改UUID成功')
        else:
            stylelog.fail('ByoDmi工具自动修改UUID失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1204', '[TC1204]Windows下ByoDmi锁住测试', 'Windows下ByoDmi锁住测试'))
def byodmi_tool_1204():
    """
    Name:   Windows下ByoDmi锁住测试

    Steps:  1.Windows下锁住ByoDmi工具
            2.检查是否可以查看SMBIOS信息
            3.检查是否可以修改SMBIOS信息
            4.解锁ByoDmi工具
            5.检查解锁后是否可以修改SMBIOS信息

    Result: 1.工具锁住成功
            2.可以查看SMBIOS信息
            3.不能修改SMBIOS信息
            4.工具解锁成功
            5.可以修改SMBIOS信息
    """
    try:
        count = 0
        assert SetUpLib.boot_to_windows_os()
        if re.search(SutConfig.Tool.WINDOWS_BYODMI_LOCK_MSG,
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BYODMI_LOCK_CMD)[0]):
            logging.info('ByoDmi锁住成功')
            if re.search('Type1 message', SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                                       f'{SutConfig.Tool.WINDOWS_BYODMI_VIEWALL_CMD} 1')[
                0]):
                logging.info('ByoDmi锁住,可以查看SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住,不能查看SMBIOS信息')
                count += 1
            if re.search('Type1 message', SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                                       f'{SutConfig.Tool.WINDOWS_BYODMI_VIEW_CMD} 1 0 5')[
                0]):
                logging.info('ByoDmi锁住,可以查看SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住,不能查看SMBIOS信息')
                count += 1
            if re.search(SutConfig.Tool.WINDOWS_BYODMI_LOCK_RUN_MSG, SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                                                                  f'{SutConfig.Tool.WINDOWS_BYODMI_TYPE_CMD} 1 0 5 oem105')[
                0]):
                logging.info('ByoDmi锁住不能修改SMBIOS信息')
            else:
                stylelog.fail('ByoDmi锁住可以修改SMBIOS信息')
                count += 1
            if re.search(SutConfig.Tool.WINDOWS_BYODMI_UNLOCK_MSG,
                         SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, SutConfig.Tool.WINDOWS_BYODMI_UNLOCK_CMD)[0]):
                logging.info('ByoDmi解锁成功')
                if re.search('Succeed', SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                                     f'{SutConfig.Tool.WINDOWS_BYODMI_TYPE_CMD} 1 0 5 oem105')[
                    0]):
                    logging.info('ByoDmi解锁后可以修改SMBIOS信息')
                else:
                    stylelog.fail('ByoDmi解锁后仍不可以修改SMBIOS信息')
                    count += 1
            else:
                stylelog.fail('ByoDmi解锁失败')
                count += 1
        else:
            stylelog.fail('ByoDmi锁住失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1205', '[TC1205]Windows下ByoDmi负面测试', 'Windows下ByoDmi负面测试'))
def byodmi_tool_1205():
    """
    Name:   Windows下ByoDmi负面测试

    Steps:  1.Windows下ByoDmi工具输入错误的参数
            2.输入超出范围的Type号
            3.-view输入无效的Type号
            4.-view只输入Type号
            5.-view输入超出范围的Type号

    Result: 1/2/3/4/5.提示信息显示正确
    """
    try:
        count = 0
        assert SetUpLib.boot_to_windows_os()
        if re.search('Input Error',
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                  f"{SutConfig.Tool.WINDOWS_BYODMI_VIEWALL_CMD} abc")[0]):
            logging.info('-viewall输入无效Type号，提示Input Error')
        else:
            stylelog.fail(('-viewall输入无效Type号，没有提示Input Error'))
            count += 1
        if re.search('Invalid type or handle',
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                  f"{SutConfig.Tool.WINDOWS_BYODMI_VIEWALL_CMD} 200")[0]):
            logging.info('-viewall输入超出范围的Type号，结果为Invalid type or handle')
        else:
            stylelog.fail('-viewall输入超出范围的Type号，结果不为Invalid type or handle')
            count += 1
        if re.search('Input Error',
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f"{SutConfig.Tool.WINDOWS_BYODMI_VIEW_CMD} a 0 a")[
                         0]):
            logging.info('-view输入无效Type号，提示Input Error')
        else:
            stylelog.fail('-view输入无效Type号，没有提示Input Error')
            count += 1
        if re.search('Input Error|Not support parameter!',
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH, f"{SutConfig.Tool.WINDOWS_BYODMI_VIEW_CMD} a")[0]):
            logging.info('-view只输入Type号，结果为Input Error')
        else:
            stylelog.fail('-view只输入Type号，结果不为Input Error')
            count += 1
        if re.search('Invalid type or handle',
                     SshLib.execute_command_limit(Sut.OS_LEGACY_SSH,
                                                  f"{SutConfig.Tool.WINDOWS_BYODMI_VIEW_CMD} 200 0 2")[0]):
            logging.info('-view输入超出范围的Type号，提示Invalid type or handle')
        else:
            stylelog.fail('-view输入超出范围的Type号，没有提示Invalid type or handle')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
