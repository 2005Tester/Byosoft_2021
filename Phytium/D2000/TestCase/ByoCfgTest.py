# -*- encoding=utf8 -*-
import os
import shutil
from D2000.BaseLib import SetUpLib, SshLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from batf import core
from batf.Report import stylelog
import subprocess
import random
import time, logging, re
from batf.SutInit import Sut


def get_path(path):
    while True:
        for i in range(0, len(path)):

            if path[i] == 'ESC' and path[i - 1] != 'ESC' and path[i - 1] != '' and path[i] != '':
                path[i] = ''
                path[i - 1] = ''
        path = [i for i in path if i]
        if 'ESC' not in path:
            break
    return path


def get_option_value_path_dict():
    options = {}
    option_path = SutConfig.Tool.OPTION_PATH

    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ALL[-1])
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    for i in range(0, len(SutConfig.Msg.PAGE_ALL)):
        SetUpLib.clean_buffer()
        data = SetUpLib.get_data(3, Key.RIGHT)
        options[','.join([i.replace(' ', '') for i in
                          re.findall(r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}',
                                     data)])] = \
            SutConfig.Msg.PAGE_ALL[i]
    for index in range(0, len(option_path)):
        if option_path[index] in SutConfig.Msg.PAGE_ALL:
            if len(option_path) > 1 and option_path[index - 1] == option_path[index]:
                if not SetUpLib.locate_option(Key.DOWN, [option_path[index]], 3):
                    if not SetUpLib.locate_option(Key.UP, [option_path[index]], 4):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                SetUpLib.clean_buffer()
                SetUpLib.send_key(Key.ENTER)
                data = SetUpLib.get_data(3)
                for i in range(0, index):
                    if option_path[i] in SutConfig.Msg.PAGE_ALL:
                        sign = i
                    if i > 0:
                        if option_path[i] in SutConfig.Msg.PAGE_ALL and option_path[i - 1] in SutConfig.Msg.PAGE_ALL:
                            sign = i - 1
                new_option_path = option_path[sign:index]
                options[','.join([i.replace(' ', '') for i in
                                  re.findall(
                                      r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}',
                                      data)])] = ','.join(get_path(new_option_path) + [option_path[index]])

            else:
                assert SetUpLib.back_to_setup_toppage()
                assert SetUpLib.boot_to_page(option_path[index])
        elif option_path[index] == 'ESC':
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
        else:
            if not SetUpLib.locate_option(Key.DOWN, [option_path[index]], 25):
                if not SetUpLib.locate_option(Key.UP, [option_path[index]], 28):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.5)
            SetUpLib.clean_buffer()
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(3)

            for i in range(0, index):
                if option_path[i] in SutConfig.Msg.PAGE_ALL:
                    sign = i
                if i > 0:
                    if option_path[i] in SutConfig.Msg.PAGE_ALL and option_path[i - 1] in SutConfig.Msg.PAGE_ALL:
                        sign = i - 1
            new_option_path = option_path[sign:index]
            options[','.join(
                [i.replace(' ', '') for i in
                 re.findall(r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}',
                            data)])] = ','.join(
                get_path(new_option_path) + [option_path[index]])
    if '' in options.keys():
        options.pop('')
    return options


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
                    r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}',
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
            options = options + re.findall(
                r'<.*?> {2,}\w[\w\(\)\. \-/\[\]:]*? {2}|\[\d+\] {2,}\w[\w\(\)\. \-/\[\]:]*? {2}', data)
    return [i.replace(' ', '') for i in options]


# get values of setup option,return a list of values
def get_value_list():
    SEP = "(?:\x1b\[\d+;\d+H){1}"  # value separator
    HLP = "(?:\x1b\[\d+m){3}"  # value hightlight ending flag, last appeared valid
    # VALR = "(\w[\w -/]*\w)"  # bios value name ruler
    VALR = "(\w[\w -:/]*[\w\)+]*)"  # bios value name ruler
    all_patten = re.compile(f"{SEP}{VALR}")
    Sut.BIOS_COM.send_keys(Key.ENTER)
    data = SetUpLib.get_data(3, cleanup=False)

    Sut.BIOS_COM.send_keys(Key.ENTER)
    if re.findall('(?:\x1b\[\d+m){2}(?:\x1b\[\d+;\d+H){2}┌─(.*?)└─', data):
        tmpdata = re.findall('(?:\x1b\[\d+m){2}(?:\x1b\[\d+;\d+H){2}┌─(.*?)└─', data)[0]
    else:
        time.sleep(1)
        Sut.BIOS_COM.send_keys(Key.ENTER)
        data = SetUpLib.get_data(3, cleanup=False)
        Sut.BIOS_COM.send_keys_with_delay(Key.ENTER)
        if re.findall('┐(.*?)└─', data):
            tmpdata = re.findall('┐(.*?)└─', data)[-1]
        else:
            tmpdata = ''
    val_list = all_patten.findall(tmpdata)
    if not val_list:
        logging.error("Fail to match values list")
        return
    logging.info("Current option values: {}".format(val_list))
    return val_list


def compare_all(part):
    num = 0
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(15)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    default = SutConfig.Tool.DEFAULT_OPTION_VALUE
    if SutConfig.Env.MACHINE_TYPE == 'Server' and SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '') in ''.join(part):
        arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
        p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        stdoutput = str(stdoutput).replace("'", '')
        status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
        if status == 'always-off' and '<{0}>{1}'.format(
                SutConfig.Tool.POWER_LOSS_VALUES[0].replace(' ', ''),
                SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '')) in part:
            logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
        elif status == 'previous' and '<{0}>{1}'.format(
                SutConfig.Tool.POWER_LOSS_VALUES[1].replace(' ', ''),
                SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '')) in part:
            logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
        elif status == 'always-on' and '<{0}>{1}'.format(
                SutConfig.Tool.POWER_LOSS_VALUES[2].replace(' ', ''),
                SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '')) in part:
            logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
        else:
            stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in part if
                                                                                    re.search(
                                                                                        f"{SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '')}",
                                                                                        i)]))
            num += 1
        updated_options = [i for i in part if
                           not re.search(f"{SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '')}", i)]
        default_options = [i for i in default if
                           not re.search(f"{SutConfig.Tool.POWER_LOSS_OPTION.replace(' ', '')}", i)]

        if updated_options == default_options and num == 0:
            return True
        else:
            return [sorted(list(set(default_options) - set(updated_options)), key=default_options.index),
                    sorted(list(set(updated_options) - set(default_options)), key=updated_options.index)]
    else:
        if part == default:
            return True
        else:
            return [sorted(list(set(default) - set(part)), key=default.index),
                    sorted(list(set(part) - set(default)), key=part.index)]


def get_cfg_setup(optionvalue, dump):
    option_name_value_byocfg = {}
    option_name_value_setup = {}
    current_value = {}
    current_value_spcial = {}
    dump_all = ''.join(dump)
    for i in optionvalue:
        for j in dump:
            if re.findall('(?:\[|<).*(?:\]|>)(.*)', i)[0] in j.replace(' ', '') and '~' not in j:
                if re.findall('(?:\[|<).*(?:\]|>)(.*)', i)[0] == re.findall('\)*.*\) (.*)', j)[0].replace(' ', ''):

                    option_name = re.findall('\)*.*\) (.*)', j)[0]
                    if dump_all.count(f') {option_name}') > 1:
                        if not re.search('Cbs\w+ = 0x', j, re.I):
                            option_name_value_byocfg[option_name] = re.findall('(0x[0-9A-Za-z]+) =', j)
                            data = re.findall('; *\((.*)\)', j)[0] if re.findall('; *\((.*)\)', j) else ''
                            option_name_value_setup[option_name] = re.split(' *0x[0-9A-Za-z]+ = ', data.strip())[1:]
                    else:
                        option_name_value_byocfg[option_name] = re.findall('(0x[0-9A-Za-z]+) =', j)
                        data = re.findall('; *\((.*)\)', j)[0] if re.findall('; *\((.*)\)', j) else ''
                        option_name_value_setup[option_name] = re.split(' *0x[0-9A-Za-z]+ = ', data.strip())[1:]
                    if not re.search('Cbs\w+ = 0x', j, re.I):
                        current_value[option_name] = re.findall(' = (.*);', j)[0]

            if re.findall('(?:\[|<).*(?:\]|>)(.*)', i)[0] in j.replace(' ', '') and '~' in j:
                if re.findall('(?:\[|<).*(?:\]|>)(.*)', i)[0] == re.findall('\)*.*\) (.*)', j)[0].replace(' ', ''):
                    option_name = re.findall('\)*.*\) (.*)', j)[0]
                    if dump_all.count(f') {option_name}') > 1:
                        if not re.search('Cbs\w+ = 0x', j, re.I):
                            data16 = [i for i in re.findall('\( *(.*) \)', j)[0].replace('~ ', '').split(' ') if i]

                            data16new = hex(
                                int(random.choice(list(range(int(data16[0], 16) + 1, int(data16[-1], 16))))))
                            option_name_value_byocfg[option_name] = data16 + [data16new]
                            option_name_value_setup[option_name] = [str(int(i, 16)) for i in data16 + [data16new]]
                    else:

                        data16 = [i for i in re.findall('\( *(.*) \)', j)[0].replace('~ ', '').split(' ') if i]
                        data16new = hex(
                            int(random.choice(list(range(int(data16[0], 16) + 1, int(data16[-1], 16))))))
                        option_name_value_byocfg[option_name] = data16 + [data16new]
                        option_name_value_setup[option_name] = [str(int(i, 16)) for i in data16 + [data16new]]
                    if not re.search('Cbs\w+ = 0x', j, re.I):
                        current_value_spcial[option_name] = re.findall(' = (.*);', j)[0]

    print(option_name_value_byocfg)
    print(option_name_value_setup)
    print(current_value)
    print(current_value_spcial)
    return option_name_value_byocfg, option_name_value_setup, current_value, current_value_spcial


def get_cfg_setup_by_setup(pathdict, dump):
    option_name_value_byocfg = {}
    option_name_value_setup = {}
    current_value = {}
    current_value_spcial = {}
    option_path = {}
    option_value = []
    for i in list(pathdict.keys()):
        option_value += i.split(',')
    for i in option_value:
        for j in dump:
            if re.findall('(?:\[|<).*(?:\]|>)(.*)', i)[0] in j.replace(' ', '') and '~' not in j:
                option_name = re.findall('\) (.*)', j)[0]
                for key, value in pathdict.items():
                    if option_name.replace(' ', '') in key:
                        option_path[option_name] = value.split(',')
                        option_name_value_byocfg[option_name] = re.findall('\( *(.*) \)', j)[0].split(' ')
                        current_value[option_name] = re.findall(' = (.*);', j)[0]

            if re.findall('(?:\[|<).*(?:\]|>)(.*)', i)[0] in j.replace(' ', '') and '~' in j:
                option_name = re.findall('\) (.*)', j)[0]
                for key, value in pathdict.items():
                    if option_name.replace(' ', '') in key:
                        data16 = [i for i in re.findall('\( *(.*) \)', j)[0].replace('~ ', '').split(' ') if i]
                        if option_name.replace(' ', '') == 'UserWaitTime' and data16[0] == '0x0':
                            data16[0] = '0x2'
                        data16new = hex(
                            int(random.choice(list(range(int(data16[0], 16) + 1, int(data16[-1], 16))))))
                        option_name_value_byocfg[option_name] = data16 + [data16new]
                        current_value_spcial[option_name] = re.findall(' = (.*);', j)[0]
                        option_name_value_setup[option_name] = [str(int(i, 16)) for i in data16 + [data16new]]
    print(option_name_value_byocfg)
    A = []
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(1)
    for i in list(option_path.values()):
        if i not in A:
            A.append(i)

    for value in A:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, value, 18)
        for key in option_path.keys():
            sign = True
            if option_path[key] == value:

                if not SetUpLib.locate_option(Key.DOWN, [SetUpLib.regex_char_handle(key)], 18):
                    if not SetUpLib.locate_option(Key.UP, [SetUpLib.regex_char_handle(key)], 18 + 1):
                        logging.info("Not Found: {0}".format(key))
                        option_name_value_byocfg.pop(key)
                        current_value.pop(key)
                        sign = False
                if sign:
                    time.sleep(1)
                    SetUpLib.clean_buffer()
                    data = get_value_list()
                    if data is None:
                        option_name_value_setup[key] = ['']
                    else:
                        option_name_value_setup[key] = data
                    time.sleep(1)
    print(option_name_value_byocfg)
    print(option_name_value_setup)
    print(current_value)
    print(current_value_spcial)
    return option_name_value_byocfg, option_name_value_setup, current_value, current_value_spcial


@core.test_case(('2001', '[TC2001]Shell下检查ByoCfg版本，帮助信息', 'Shell下检查ByoCfg版本，帮助信息'))
def byocfg_tool_2001():
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_VERSION_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_VERSION_CONFIRM_MSG, 5):
            logging.info('Shell下工具版本验证成功')
        else:
            stylelog.fail('Shell下工具版本验证失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_HELP_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_HELP_CONFIRM_MSG, 5):
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


@core.test_case(
    ('2002', '[TC2002]Shell下检查ByoCfg变量值与SetUp显示一致,ByoCfg修改变量值测试', 'Shell下检查ByoCfg变量值与SetUp显示一致,ByoCfg修改变量值测试'))
def byocfg_tool_2002():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        path_dict = get_option_value_path_dict()
        print(path_dict)
        option_value = []
        for i in list(path_dict.keys()):
            option_value += i.split(',')
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10).splitlines()[1:-1]
        option_name_value_byocfg, option_name_value_setup, current_value, current_value_spcial = get_cfg_setup_by_setup(
            path_dict, dump)
        for key, value in current_value.items():
            if f"<{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}>{key.replace(' ', '')}" not in option_value:
                stylelog.fail(
                    f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                wrong_msg.append(
                    f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                count += 1

        if current_value_spcial:
            for key, value in current_value_spcial.items():
                if f"[{str(int(value, 16))}]{key.replace(' ', '')}" not in option_value:
                    stylelog.fail(
                        f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{str(int(value, 16))},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                    wrong_msg.append(
                        f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{str(int(value, 16))},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                    count += 1

        logging.info('ByoCfg修改SetUp选项测试..........................................................')
        for i in list(option_name_value_setup.keys()):
            if i in SutConfig.Tool.REMOVE_OPTIONS:
                option_name_value_setup.pop(i)
                option_name_value_byocfg.pop(i)
        num = max([len(i) for i in option_name_value_byocfg.values()])
        change_option_value = {}
        for index in range(0, num):
            logging.info(f'`ByoCfg通过文件修改SetUp选项第{str(index + 1)}轮测试........................................')
            assert SetUpLib.boot_to_shell()
            SetUpLib.shell_bios_file()
            for key, value in option_name_value_byocfg.items():
                if index < len(value):
                    change_option_value[key] = value[index]
                else:
                    change_option_value[key] = random.choice(value)

            print(change_option_value)
            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
            data = SetUpLib.get_data(10).splitlines()[1:-1]
            time.sleep(1)
            if os.path.exists('D2000/Tools/ByoCfg'):
                shutil.rmtree('D2000/Tools/ByoCfg')
            os.mkdir('D2000/Tools/ByoCfg')
            with open('D2000/Tools/ByoCfg/setup.txt', 'w') as f:
                for da in data:
                    f.write(da + '\n')
            f.close()
            time.sleep(2)
            with open('D2000/Tools/ByoCfg/setup.txt', 'r') as f:
                lines = f.readlines()
            f.close()
            time.sleep(2)
            with open('D2000/Tools/ByoCfg/setup.txt', 'w') as f:
                for line in lines:
                    for key, value in change_option_value.items():
                        if key in line:
                            line = re.sub(' = (.*);', f' = {value};', line)
                    if '=' in line:
                        f.write(line)
            time.sleep(2)
            f.close()
            time.sleep(2)
            assert SetUpLib.boot_to_linux_os()
            SetUpLib.linux_mount_usb()
            SshLib.execute_command_limit(Sut.OS_SSH, f'rm -f /mnt/{SutConfig.Env.BIOS_FILE}/input.txt')
            time.sleep(1)
            try_counts = 3
            while try_counts:
                try:
                    assert SshLib.sftp_upload_file(Sut.OS_SFTP, 'D2000/Tools/ByoCfg/setup.txt',
                                                   f'/mnt/{SutConfig.Env.BIOS_FILE}/input.txt',
                                                   str(os.stat('D2000/Tools/ByoCfg/setup.txt').st_size))
                    logging.info('上传成功')
                    break
                except:
                    logging.info('上传失败,2秒后重试')
                    try_counts -= 1
                    time.sleep(2)
            time.sleep(2)
            assert SetUpLib.boot_to_shell()
            SetUpLib.shell_bios_file()
            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_WF} input.txt')
            if SetUpLib.wait_message('success', 5):
                logging.info('修改成功')
            time.sleep(2)
            assert SetUpLib.boot_to_setup()
            change_option_value_setup = get_options_value()
            logging.debug(f'ByoCfg修改选项后，SetUp读取的值{change_option_value_setup}')
            for key, value in change_option_value.items():
                for i in change_option_value_setup:
                    if f">{key.replace(' ', '')}" in i or f"]{key.replace(' ', '')}" in i:

                        if f"<{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}>{key.replace(' ', '')}" != i and f"[{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}]{key.replace(' ', '')}" != i:
                            stylelog.fail(
                                f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                            stylelog.fail(i)
                            wrong_msg.append(
                                f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                            count += 1
                        else:
                            logging.info(
                                f"ByoCfg修改{key}为{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}成功")
            time.sleep(2)
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(15)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)

        logging.info('ByoCfg直接修改SetUp选项值...........................')
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10).splitlines()[1:-1]
        time.sleep(1)
        change_option_value = {}
        for key, value in option_name_value_byocfg.items():
            change_option_value[key] = random.choice(value)
        arg = ''
        for i in dump:
            for key, value in change_option_value.items():
                if key in i:
                    arg += re.findall('(.*) = 0x[0-9A-Za-z]+;', i)[0] + ':' + value + ' '
        time.sleep(1)
        input = f'{SutConfig.Tool.SHELL_BYOCFG_W} {arg}'

        def cut(obj, sec):
            return [obj[i:i + sec] for i in range(0, len(obj), sec)]

        for i in cut(input, 10):
            SetUpLib.send_data(i)
        SetUpLib.send_key(Key.ENTER)
        if not SetUpLib.wait_message('error', 15):
            logging.info('ByoCfg修改成功')
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        change_option_value_setup = get_options_value()
        logging.debug(f'ByoCfg修改选项后，SetUp读取的值{change_option_value_setup}')
        for key, value in change_option_value.items():
            for i in change_option_value_setup:
                if f">{key.replace(' ', '')}" in i or f"]{key.replace(' ', '')}" in i:
                    if f"<{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}>{key.replace(' ', '')}" != i and f"[{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}]{key.replace(' ', '')}" != i:
                        stylelog.fail(
                            f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                        wrong_msg.append(
                            f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                        count += 1
                    else:
                        logging.info(
                            f"ByoCfg修改{key}为{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}成功")
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(15)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2003', '[TC2003]Shell下dump变量值与系统下对比', 'Shell下dump变量值与系统下对比'))
def byocfg_tool_2003():
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump_shell = SetUpLib.get_data(10).splitlines()[1:-1]
        dump_shell = [i.replace(' ', '') for i in dump_shell]
        dump_shell = [i.lower() for i in dump_shell if not re.search('FS\d+:', i, re.I)]
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        dump_linux = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()[0:-1]
        dump_linux = [i.replace(' ', '').lower() for i in dump_linux]
        for i in dump_linux:
            if i not in dump_shell:
                stylelog.fail(f'{i}shell,linux不一致')
                count += 1
        logging.debug(f'shell{dump_shell}')
        logging.debug(f'linux{dump_linux}')
        if count == 0:
            return True
        else:
            stylelog.fail(f'shell下{set(dump_shell) - set(dump_linux)}')
            stylelog.fail(f'linux下{set(dump_linux) - set(dump_shell)}')
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(
    ('2004', '[TC2004]Shell下ByoCfg逐个修改变量值并在系统下验证，ByoCfg恢复默认值测试', 'Shell下ByoCfg逐个修改变量值并在系统下验证，ByoCfg恢复默认值测试'))
def byocfg_tool_2004():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10).splitlines()[1:-1]
        try:
            for i in dump:
                time.sleep(1)
                name = re.findall('(.*) = 0x[0-9A-Za-z]+;', i)
                values = re.findall('\( *(.*) \)', i)
                if name and values:
                    name = name[0]
                    values = re.findall('(0x[0-9A-Za-z]+) ', values[0])
                    for value in values:
                        SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_W} {name}:{value}')
                        data = SetUpLib.get_data(2)
                        if re.search(SutConfig.Tool.SHELL_BYOCFG_UNLOCK_RUN_MSG, data):
                            SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_UNLOCK)
                            time.sleep(2)
                            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_W} {name}:{value}')
                            data = SetUpLib.get_data(2)
                        if re.search("Set.*{}".format(SetUpLib.regex_char_handle(name)), data):
                            logging.info(f'ByoCfg修改{name}{value}成功')
                            time.sleep(1)
                            SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_R} {name}')
                            if SetUpLib.wait_message(f'{value}', 2):
                                logging.info(f'ByoCfg修改{name}{value},验证成功')
                            else:
                                stylelog.fail(f'ByoCfg修改{name}{value},验证失败')
                                wrong_msg.append(f'ByoCfg修改{name}{value},验证失败')
                                count += 1
                        else:
                            stylelog.fail(f'ByoCfg修改{name}{value}失败')
                            wrong_msg.append(f'ByoCfg修改{name}{value}失败')
                            count += 1
        except:
            pass

        logging.info('ByoCfg恢复默认值测试')
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_SET_DEFAULT)
        if SetUpLib.wait_message('Success', 5):
            logging.info('ByoCfg 恢复BIOS为默认值成功')
        time.sleep(1)
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        result = compare_all(changed_options)
        if result == True:
            logging.info('ByoCfg恢复BIOS默认值成功')
        else:
            stylelog.fail('ByoCfg恢复BIOS默认值失败')
            stylelog.fail(f'默认 的选项{result[0]}')
            stylelog.fail(f'恢复后的选项{result[1]}')
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


@core.test_case(('2005', '[TC2005]Shell下ByoCfg锁住测试', 'Shell下ByoCfg锁住测试'))
def byocfg_tool_2005():
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10).splitlines()[1:-1]
        for i in dump:
            name = re.findall('(.*) = 0x[0-9A-Za-z]+;', i)
            values = re.findall('\( *(.*) \)', i)
            if name and values:
                name = name[0]
                values = re.findall('(0x[0-9A-Za-z]+) ', values[0])
                SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_LOCK)
                if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_LOCK_MSG, 5):
                    logging.info('ByoCfg锁住成功')
                    time.sleep(1)
                    SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_W} {name}:{values[0]}')
                    if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_UNLOCK_RUN_MSG, 5):
                        logging.info('ByoCfg锁住,无法修改变量值')
                    else:
                        stylelog.fail('ByoCfg锁住,可以修改变量值')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_R} {name}')
                    if SetUpLib.wait_message(name, 5):
                        logging.info('ByoCfg锁住,可以读取变量值')
                    else:
                        stylelog.fail('ByoCfg锁住,无法读取变量值')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_DUMP} > setup.txt')
                    time.sleep(2)
                    SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_WF} setup.txt')
                    if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_UNLOCK_RUN_MSG, 5):
                        logging.info('ByoCfg锁住,无法通过配置文件修改变量值')
                    else:
                        stylelog.fail('ByoCfg锁住,可以通过配置文件修改变量值')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_UNLOCK)
                    if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_UNLOCK_MSG, 5):
                        logging.info('ByoCfg解锁成功')
                        time.sleep(1)
                        SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_W} {name}:{values[0]}')
                        if SetUpLib.wait_message(name, 5):

                            logging.info('ByoCfg解锁后可以修改变量值')
                        else:
                            stylelog.fail('ByoCfg解锁后不能修改变量值')
                            count += 1
                        time.sleep(1)
                        SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_WF} setup.txt')
                        if SetUpLib.wait_message('success', 5):
                            logging.info('解锁后可以通过配置文件修改变量值')
                        else:
                            stylelog.fail('解锁后不能通过配置文件修改变量值')
                            count += 1
                    else:
                        stylelog.fail('ByoCfg解锁失败')
                        count += 1


                else:
                    stylelog.fail('Shell下ByoCfg锁住失败')
                    count += 1
                break
        time.sleep(3)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_UNLOCK)
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_SET_DEFAULT)
        time.sleep(1)
        SetUpLib.reboot()
        time.sleep(200)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2006', '[TC2006]Shell下ByoCfg负面测试', 'Shell下ByoCfg负面测试'))
def byocfg_tool_2006():
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_ERROR_CMD)
        if SetUpLib.wait_message(SutConfig.Tool.SHELL_BYOCFG_ERR_MSG, 5):
            logging.info('输入错误参数，提示错误')
        else:
            stylelog.fail('输入错误参数，没有提示错误')
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_R} ttest')
        if SetUpLib.wait_message('failed', 5):
            logging.info('检查变量值，输入错误的变量名，提示失败')
        else:
            stylelog.fail('检查变量值，输入错误的变量名，没有提示失败')
            count += 1
        time.sleep(1)
        SetUpLib.send_data_enter(f'{SutConfig.Tool.SHELL_BYOCFG_W} ttest:aaa')
        if SetUpLib.wait_message('failed', 5):
            logging.info('修改变量值，输入错误的变量名，变量值，提示失败')
        else:
            stylelog.fail('修改变量值，输入错误的变量名，变量值，没有提示失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2007', '[TC2007]Shell下ByoCfg修改启动顺序测试', 'Shell下ByoCfg修改启动顺序测试'))
def byocfg_tool_2007():
    try:
        wrong_msg = []
        count = 0
        logging.info('UEFI模式ByoCfg修改启动顺序')
        boot_name_dict_uefi = {}
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.SET_UEFI, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, ['Change Boot order'], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        for key, value in SutConfig.Tool.BOOT_NAME_DICT_UEFI.items():
            if not SetUpLib.locate_option(Key.DOWN, [value], 18):
                if not SetUpLib.locate_option(Key.UP, [value], 18):
                    return
            time.sleep(1)
            boot_name_dict_uefi[key] = get_value_list()

        print(boot_name_dict_uefi)

        def cut(obj, sec):
            return [obj[i:i + sec] for i in range(0, len(obj), sec)]

        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10)
        origin_order = re.findall('UefiBootGroupOrder = (.*);', dump)[0].split(' ')
        for index in range(0, 3):
            new_order = origin_order
            random.shuffle(new_order)
            time.sleep(1)
            order_arg = ' '.join(new_order)
            for i in cut(f'{SutConfig.Tool.SHELL_BYOCFG_W} UefiBootGroupOrder:{order_arg}', 10):
                SetUpLib.send_data(i)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message('Set.*UefiBootGroupOrder', 5):
                logging.info('ByoCfg修改启动顺序成功')
            assert SetUpLib.boot_to_setup()
            changed_uefi_order = ''
            for i in new_order:
                if i in SutConfig.Tool.BOOT_NAME_DICT_UEFI.keys():
                    changed_uefi_order += ' *►* *' + SutConfig.Tool.BOOT_NAME_DICT_UEFI[i] + ' *'
            assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
            time.sleep(1)
            assert SetUpLib.locate_option(Key.DOWN, ['Change Boot order'], 10)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(3)

            print(changed_uefi_order)
            if re.search(changed_uefi_order, data):
                logging.info(f'ByoCfg修改启动顺序为{new_order},验证成功')
            else:
                stylelog.fail(f'ByoCfg修改启动顺序为{new_order},验证失败')
                wrong_msg.append(f'ByoCfg修改启动顺序为{new_order},验证失败')
                count += 1
            assert SetUpLib.boot_to_shell()
            SetUpLib.shell_bios_file()
        logging.info('UEFI模式ByoCfg修改组内启动顺序')
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10).splitlines()[1:-1]
        nums = {}
        name_num = {}
        for key, value in boot_name_dict_uefi.items():
            if value is not None:
                if len(value) >= 2:
                    nums[key] = []
                    for i in value:
                        for j in dump:
                            if i in j:
                                num = re.findall(';Boot(.*) = ', j)[0]
                                name_num[num] = i
                                nums[key].append(num)
        time.sleep(1)
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        origin_order_all = re.findall('BootOrder = ([0-9A-Za-z ]*)',
                                      SetUpLib.get_data(10))[0]
        print(nums)
        print(name_num)
        if nums:
            for key, value in nums.items():
                if ' '.join(value) in origin_order_all:
                    old = ' '.join(value)
                    new = ' '.join(list(set(value)))
                    changed_order_all = origin_order_all.replace(f'{old}', f'{new}')
            print(changed_order_all)
            changed_name_order = {}
            for i in changed_order_all.split(' '):
                for key, value in nums.items():
                    if i in value:
                        changed_name_order[key] = ''
            for i in changed_order_all.split(' '):
                for key, value in nums.items():
                    if i in value:
                        changed_name_order[key] += name_num[i]
            time.sleep(1)
            for i in cut(f'{SutConfig.Tool.SHELL_BYOCFG_W} BootOrder:{changed_order_all}', 10):
                SetUpLib.send_data(i)
            time.sleep(5)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message('Set.*BootOrder', 5):
                logging.info('Byocfg修改组内启动顺序成功')

            datas = SetUpLib.boot_to_boot_menu(True)
            for value in changed_name_order.values():
                if value in datas:
                    logging.info(f'ByoCfg修改启动顺序为{changed_name_order},启动菜单顺序验证成功')
                else:
                    stylelog.fail(f'ByoCfg修改启动顺序为{changed_name_order},启动菜单顺序验证失败')
                    stylelog.fail(f'启动菜单顺序{datas}')
                    wrong_msg.append(f'ByoCfg修改启动顺序为{changed_name_order},启动菜单顺序验证失败')
                    wrong_msg.append(f'启动菜单顺序{datas}')
                    count += 1
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(15)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2008', '[TC2008]Shell下ByoCfg检查重复选项名测试', 'Shell下ByoCfg检查重复选项名测试'))
def byocfg_tool_2008():
    try:
        count = 0
        assert SetUpLib.boot_to_shell()
        SetUpLib.shell_bios_file()
        SetUpLib.send_data_enter(SutConfig.Tool.SHELL_BYOCFG_DUMP)
        dump = SetUpLib.get_data(10).splitlines()
        print(dump)
        name = []
        for i in dump:
            if re.findall('\)*.*\) (.*)', i):
                name.append(re.findall('\)*.*\) (.*)', i)[0])
        for i in name:
            if name.count(i) > 1:
                stylelog.fail(f'{i}重复')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2101', '[TC2101]Linux下检查ByoCfg版本，帮助信息', 'Linux下检查ByoCfg版本，帮助信息'))
def byocfg_tool_2101():
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        if re.search(SutConfig.Tool.LINUX_BYOCFG_VERSION_CONFIRM_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_VERSION_CMD)[0]):
            logging.info('Linux下工具版本验证成功')
        else:
            stylelog.fail('Linux下工具版本验证失败')
            count += 1
        time.sleep(1)
        if re.search(SutConfig.Tool.LINUX_BYOCFG_HELP_CONFIRM_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_HELP_CMD)[0]):
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


@core.test_case(
    ('2102', '[TC2102]Linux下检查ByoCfg变量值与SetUp显示一致,ByoCfg修改变量值测试', 'Linux下检查ByoCfg变量值与SetUp显示一致,ByoCfg修改变量值测试'))
def byocfg_tool_2102():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        path_dict = get_option_value_path_dict()
        option_value = []
        for i in list(path_dict.keys()):
            option_value += i.split(',')
        print(option_value)
        assert SetUpLib.boot_to_linux_os()
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()
        option_name_value_byocfg, option_name_value_setup, current_value, current_value_spcial = get_cfg_setup_by_setup(
            path_dict, dump)
        for key, value in current_value.items():
            if f"<{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}>{key.replace(' ', '')}" not in option_value:
                stylelog.fail(
                    f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                wrong_msg.append(
                    f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                count += 1
        if current_value_spcial:
            for key, value in current_value_spcial.items():
                if f"[{str(int(value, 16))}]{key.replace(' ', '')}" not in option_value:
                    stylelog.fail(
                        f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{str(int(value, 16))},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                    wrong_msg.append(
                        f"{key}ByoCfg读取值与SetUp实际值不符,ByoCfg：{str(int(value, 16))},SetUp:{[i for i in option_value if key.replace(' ', '') in i]}")
                    count += 1

        logging.info('ByoCfg修改SetUp选项测试..........................................................')
        for i in list(option_name_value_setup.keys()):
            if i in SutConfig.Tool.REMOVE_OPTIONS:
                option_name_value_setup.pop(i)
                option_name_value_byocfg.pop(i)

        num = max([len(i) for i in option_name_value_byocfg.values()])
        change_option_value = {}
        for index in range(0, num):
            logging.info(f'ByoCfg通过文件修改SetUp选项第{str(index + 1)}轮测试........................................')
            assert SetUpLib.boot_to_linux_os()
            SetUpLib.linux_mount_usb()
            for key, value in option_name_value_byocfg.items():
                if index < len(value):
                    change_option_value[key] = value[index]
                else:
                    change_option_value[key] = random.choice(value)

            print(change_option_value)
            SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_DUMP} > setup.txt')
            time.sleep(1)
            if os.path.exists('D2000/Tools/ByoCfg'):
                shutil.rmtree('D2000/Tools/ByoCfg')
            os.mkdir('D2000/Tools/ByoCfg')
            SshLib.sftp_download_file(Sut.OS_SFTP, 'setup.txt', 'D2000/Tools/ByoCfg/setup.txt')
            time.sleep(2)
            with open('D2000/Tools/ByoCfg/setup.txt', 'r') as f:
                lines = f.readlines()
            f.close()
            time.sleep(1)
            with open('D2000/Tools/ByoCfg/setup.txt', 'w') as f:
                for line in lines:
                    for key, value in change_option_value.items():
                        if key in line:
                            line = re.sub(' = (.*);', f' = {value};', line)
                    if '=' in line:
                        f.write(line)
            f.close()
            time.sleep(2)
            time.sleep(1)
            try_counts = 3
            while try_counts:
                try:
                    assert SshLib.sftp_upload_file(Sut.OS_SFTP, 'D2000/Tools/ByoCfg/setup.txt',
                                                   'input.txt',
                                                   str(os.stat('D2000/Tools/ByoCfg/setup.txt').st_size))
                    logging.info('上传成功')
                    break
                except:
                    logging.info('上传失败,2秒后重试')
                    try_counts -= 1
                    time.sleep(2)
            time.sleep(2)
            if re.search('Success',
                         SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_WF} input.txt')[0]):
                logging.info('修改成功')
            time.sleep(1)
            assert SetUpLib.boot_to_setup()
            change_option_value_setup = get_options_value()
            logging.debug(f'ByoCfg修改选项后，SetUp读取的值{change_option_value_setup}')
            for key, value in change_option_value.items():

                for i in change_option_value_setup:
                    if f">{key.replace(' ', '')}" in i or f"]{key.replace(' ', '')}" in i:
                        if f"<{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}>{key.replace(' ', '')}" != i and f"[{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}]{key.replace(' ', '')}" != i:
                            stylelog.fail(
                                f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                            stylelog.fail(i)
                            wrong_msg.append(
                                f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                            count += 1
                        else:
                            logging.info(
                                f"ByoCfg修改{key}为{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}成功")
            time.sleep(2)
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(15)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)
        logging.info('ByoCfg直接修改SetUp选项值...........................')
        assert SetUpLib.boot_to_linux_os()
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()
        change_option_value = {}
        for key, value in option_name_value_byocfg.items():
            change_option_value[key] = random.choice(value)
        arg = ''
        for i in dump:
            for key, value in change_option_value.items():
                if key in i:
                    arg += re.findall('(.*) = 0x[0-9A-Za-z]+;', i)[0] + ':' + value + ' '
        time.sleep(1)
        if not re.search('error',
                         SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_W} {arg}')[0]):
            logging.info('ByoCfg修改成功')
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        change_option_value_setup = get_options_value()
        logging.debug(f'ByoCfg修改选项后，SetUp读取的值{change_option_value_setup}')
        for key, value in change_option_value.items():
            for i in change_option_value_setup:
                if f">{key.replace(' ', '')}" in i or f"]{key.replace(' ', '')}" in i:
                    if f"<{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}>{key.replace(' ', '')}" != i and f"[{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}]{key.replace(' ', '')}" != i:
                        stylelog.fail(
                            f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                        wrong_msg.append(
                            f"ByoCfg修改SetUp选项，{key}修改失败,修改的值为：{option_name_value_setup[key][option_name_value_byocfg[key].index(value)]}")
                        count += 1
                    else:
                        logging.info(
                            f"ByoCfg修改{key}为{option_name_value_setup[key][option_name_value_byocfg[key].index(value)].replace(' ', '')}成功")
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(15)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)

        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(
    ('2103', '[TC2103]Linux下ByoCfg逐个修改变量值并在系统下验证，ByoCfg恢复默认值测试', 'Linux下ByoCfg逐个修改变量值并在系统下验证，ByoCfg恢复默认值测试'))
def byocfg_tool_2103():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_linux_os()
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()
        try:
            for i in dump:
                name = re.findall('(.*) = 0x[0-9A-Za-z]+;', i)
                values = re.findall('\( *(.*) \)', i)
                if name and values:
                    name = name[0]
                    values = re.findall('(0x[0-9A-Za-z]+) ', values[0])

                    for value in values:
                        data = \
                            SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_W} {name}:{value}')[
                                0]
                        if re.search(SutConfig.Tool.LINUX_BYOCFG_UNLOCK_RUN_MSG, data):
                            SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_UNLOCK)
                            time.sleep(1)
                            data = \
                                SshLib.execute_command_limit(Sut.OS_SSH,
                                                             f'{SutConfig.Tool.LINUX_BYOCFG_W} {name}:{value}')[0]

                        if re.search(f'Set.*{value}', data, re.I):
                            logging.info(f'ByoCfg修改{name}{value}成功')

                            result = \
                                SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_R} {name}')[0]
                            if re.search(f'{value}', result):
                                logging.info(f'ByoCfg修改{name}{value},验证成功')
                            else:
                                stylelog.fail(f'ByoCfg修改{name}{value},验证失败')
                                stylelog.fail(result)
                                wrong_msg.append(f'ByoCfg修改{name}{value},验证失败')
                                count += 1
                        else:
                            stylelog.fail(f'ByoCfg修改{name}{value}失败')
                            wrong_msg.append(f'ByoCfg修改{name}{value}失败')
                            count += 1
        except:
            pass
        logging.info('ByoCfg恢复默认值测试')
        time.sleep(1)
        if re.search('Success', SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_SET_DEFAULT)[0]):
            logging.info('ByoCfg 恢复BIOS为默认值成功')
        time.sleep(1)
        SetUpLib.reboot()
        time.sleep(200)
        assert SetUpLib.boot_to_setup()
        changed_options = get_options_value()
        print(changed_options)
        result = compare_all(changed_options)
        if result == True:
            logging.info('ByoCfg恢复BIOS默认值成功')
        else:
            stylelog.fail('ByoCfg恢复BIOS默认值失败')
            stylelog.fail(f'默认 的选项{result[0]}')
            stylelog.fail(f'恢复后的选项{result[1]}')
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


@core.test_case(('2104', '[TC2104]Linux下ByoCfg锁住测试', 'Linux下ByoCfg锁住测试'))
def byocfg_tool_2104():
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()
        for i in dump:
            name = re.findall('(.*) = 0x[0-9A-Za-z]+;', i)
            values = re.findall('\( *(.*) \)', i)
            if name and values:
                name = name[0]
                values = re.findall('(0x[0-9A-Za-z]+) ', values[0])
                if re.search(SutConfig.Tool.LINUX_BYOCFG_LOCK_MSG,
                             SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_LOCK)[0]):
                    logging.info('ByoCfg锁住成功')
                    if re.search(SutConfig.Tool.LINUX_BYOCFG_UNLOCK_RUN_MSG, SshLib.execute_command_limit(Sut.OS_SSH,
                                                                                                          f'{SutConfig.Tool.LINUX_BYOCFG_W} {name}:{values[0]}')[
                        0]):
                        logging.info('ByoCfg锁住,无法修改变量值')
                    else:
                        stylelog.fail('ByoCfg锁住,可以修改变量值')
                        count += 1
                    if re.search(f'{name}',
                                 SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_R} {name}')[
                                     0]):
                        logging.info('ByoCfg锁住,可以读取变量值')
                    else:
                        stylelog.fail('ByoCfg锁住,无法读取变量值')
                        count += 1
                    SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_DUMP} > setup.txt')
                    time.sleep(1)
                    if re.search(SutConfig.Tool.LINUX_BYOCFG_UNLOCK_RUN_MSG,
                                 SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_WF} setup.txt',
                                                              decoding='gbk')[0]):
                        logging.info('ByoCfg锁住,无法通过配置文件修改变量值')
                    else:
                        stylelog.fail('ByoCfg锁住,可以通过配置文件修改变量值')
                        count += 1
                    if re.search(SutConfig.Tool.LINUX_BYOCFG_UNLOCK_MSG,
                                 SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_UNLOCK,
                                                              decoding='gbk')[0]):
                        logging.info('ByoCfg解锁成功')
                        if re.search(name, SshLib.execute_command_limit(Sut.OS_SSH,
                                                                        f'{SutConfig.Tool.LINUX_BYOCFG_W} {name}:{values[0]}')[
                            0]):
                            logging.info('ByoCfg解锁后可以修改变量值')
                        else:
                            stylelog.fail('ByoCfg解锁后不能修改变量值')
                            count += 1
                        if not re.search(SutConfig.Tool.LINUX_BYOCFG_UNLOCK_RUN_MSG,
                                         SshLib.execute_command_limit(Sut.OS_SSH,
                                                                      f'{SutConfig.Tool.LINUX_BYOCFG_WF} setup.txt')[
                                             0]):
                            logging.info('解锁后可以通过配置文件修改变量值')
                        else:
                            stylelog.fail('解锁后不能通过配置文件修改变量值')
                            count += 1
                    else:
                        stylelog.fail('ByoCfg解锁失败')
                        count += 1
                else:
                    stylelog.fail('LINUX下ByoCfg锁住失败')
                    count += 1
                break
        SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_UNLOCK, decoding='gbk')
        SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_SET_DEFAULT)
        time.sleep(1)
        SetUpLib.reboot()
        time.sleep(200)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2105', '[TC2105]Linux下ByoCfg负面测试', 'Linux下ByoCfg负面测试'))
def byocfg_tool_2105():
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        if re.search(SutConfig.Tool.LINUX_BYOCFG_ERR_MSG,
                     SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_ERROR_CMD)[0]):
            logging.info('输入错误参数，提示错误')
        else:
            stylelog.fail('输入错误参数，没有提示错误')
            count += 1
        time.sleep(1)
        if re.search('Failed|not found',
                     SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_R} ttest')[0]):
            logging.info('检查变量值，输入错误的变量名，提示失败')
        else:
            stylelog.fail('检查变量值，输入错误的变量名，没有提示失败')
            count += 1
        if re.search('Failed',
                     SshLib.execute_command_limit(Sut.OS_SSH, f'{SutConfig.Tool.LINUX_BYOCFG_W} ttest:aaa')[0]):
            logging.info('修改变量值，输入错误的变量名，变量值，提示失败')
        else:
            stylelog.fail('修改变量值，输入错误的变量名，变量值，没有提示失败')
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2106', '[TC2106]Linux下ByoCfg修改启动顺序测试', 'Linux下ByoCfg修改启动顺序测试'))
def byocfg_tool_2106():
    try:
        wrong_msg = []
        count = 0
        logging.info('UEFI模式ByoCfg修改启动顺序')
        boot_name_dict_uefi = {}
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.SET_UEFI, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, ['Change Boot order'], 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        for key, value in SutConfig.Tool.BOOT_NAME_DICT_UEFI.items():
            if not SetUpLib.locate_option(Key.DOWN, [value], 18):
                if not SetUpLib.locate_option(Key.UP, [value], 18):
                    return
            time.sleep(1)
            boot_name_dict_uefi[key] = get_value_list()
        print(boot_name_dict_uefi)
        assert SetUpLib.boot_to_linux_os()
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0]
        origin_order = re.findall('UefiBootGroupOrder = (.*);', dump)[0].split(' ')
        print(origin_order)
        for index in range(0, 3):
            new_order = origin_order
            random.shuffle(new_order)
            time.sleep(1)
            order_arg = ' '.join(new_order)
            print(order_arg)
            if re.search(f'Set.*UefiBootGroupOrder',
                         SshLib.execute_command_limit(Sut.OS_SSH,
                                                      f'{SutConfig.Tool.LINUX_BYOCFG_W} UefiBootGroupOrder:{order_arg}')[
                             0]):
                logging.info('ByoCfg修改启动顺序成功')
            assert SetUpLib.boot_to_setup()
            changed_uefi_order = ''
            for i in new_order:
                if i in SutConfig.Tool.BOOT_NAME_DICT_UEFI.keys():
                    changed_uefi_order += ' *►* *' + SutConfig.Tool.BOOT_NAME_DICT_UEFI[i] + ' *'
            assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
            assert SetUpLib.locate_option(Key.DOWN, ['Change Boot order'], 10)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(3)
            print(changed_uefi_order)
            if re.search(changed_uefi_order, data):
                logging.info(f'ByoCfg修改启动顺序为{new_order},验证成功')
            else:
                stylelog.fail(f'ByoCfg修改启动顺序为{new_order},验证失败')
                wrong_msg.append(f'ByoCfg修改启动顺序为{new_order},验证失败')
                count += 1
            assert SetUpLib.boot_to_linux_os()
        logging.info('UEFI模式ByoCfg修改组内启动顺序')
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()
        nums = {}
        name_num = {}
        for key, value in boot_name_dict_uefi.items():
            if value is not None:
                if len(value) >= 2:
                    nums[key] = []
                    for i in value:
                        for j in dump:
                            if i in j:
                                num = re.findall(';Boot(.*) = ', j)[0]
                                name_num[num] = i
                                nums[key].append(num)
        origin_order_all = re.findall('BootOrder = ([0-9A-Za-z ]*)',
                                      SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0])[0]
        print(nums)
        # print(origin_order_all)
        print(name_num)
        if nums:
            for key, value in nums.items():
                if ' '.join(value) in origin_order_all:
                    old = ' '.join(value)
                    new = ' '.join(list(set(value)))
                    changed_order_all = origin_order_all.replace(f'{old}', f'{new}')
            print(changed_order_all)
            changed_name_order = {}
            for i in changed_order_all.split(' '):
                for key, value in nums.items():
                    if i in value:
                        changed_name_order[key] = ''
            for i in changed_order_all.split(' '):
                for key, value in nums.items():
                    if i in value:
                        changed_name_order[key] += name_num[i]
            time.sleep(1)
            if re.search('Set.*BootOrder', SshLib.execute_command_limit(Sut.OS_SSH,
                                                                        f'{SutConfig.Tool.LINUX_BYOCFG_W} BootOrder:{changed_order_all}')[
                0]):
                logging.info('Byocfg修改组内启动顺序成功')
            datas = SetUpLib.boot_to_boot_menu(True)
            for value in changed_name_order.values():
                if value in datas:
                    logging.info(f'ByoCfg修改启动顺序为{changed_name_order},启动菜单顺序验证成功')
                else:
                    stylelog.fail(f'ByoCfg修改启动顺序为{changed_name_order},启动菜单顺序验证失败')
                    stylelog.fail(f'启动菜单顺序{datas}')
                    wrong_msg.append(f'ByoCfg修改启动顺序为{changed_name_order},启动菜单顺序验证失败')
                    wrong_msg.append(f'启动菜单顺序{datas}')
                    count += 1

        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(15)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('2107', '[TC2107]linux下ByoCfg检查重复选项名测试', 'linux下ByoCfg检查重复选项名测试'))
def byocfg_tool_2107():
    try:
        count = 0
        assert SetUpLib.boot_to_linux_os()
        SetUpLib.linux_mount_usb()
        dump = SshLib.execute_command_limit(Sut.OS_SSH, SutConfig.Tool.LINUX_BYOCFG_DUMP)[0].splitlines()
        name = []
        for i in dump:
            if re.findall('\)*.*\) (.*)', i):
                name.append(re.findall('\)*.*\) (.*)', i)[0])
        for i in name:
            if name.count(i) > 1:
                stylelog.fail(f'{i}重复')
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
