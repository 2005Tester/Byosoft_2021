from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *


def get_hdd_msg(type='tcg', types=None):
    if types is None:
        hdd_name = []
        hdd_boot_name = []
        if re.search(type, SutConfig.Psw.HDD_PASSWORD_NAME_01, re.I):
            hdd_name.append(SutConfig.Psw.HDD_PASSWORD_NAME_01)
            hdd_boot_name.append(SutConfig.Psw.HDD_NAME_01_OS)
        if re.search(type, SutConfig.Psw.HDD_PASSWORD_NAME_02, re.I):
            hdd_name.append(SutConfig.Psw.HDD_PASSWORD_NAME_02)
            hdd_boot_name.append(SutConfig.Psw.HDD_NAME_02_OS)
        if hdd_name:
            return hdd_name[0], hdd_boot_name[0]
        else:
            return None
    else:
        if types == ['tcg', 'ata'] or types == ['ata', 'tcg']:
            if re.search('tcg', SutConfig.Psw.HDD_PASSWORD_NAME_01, re.I) and re.search('ata', SutConfig.Psw.HDD_PASSWORD_NAME_02, re.I):
                return SutConfig.Psw.HDD_PASSWORD_NAME_01, SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.HDD_NAME_01_OS, SutConfig.Psw.HDD_NAME_02_OS
            elif re.search('ata', SutConfig.Psw.HDD_PASSWORD_NAME_01, re.I) and re.search('tcg', SutConfig.Psw.HDD_PASSWORD_NAME_02, re.I):
                return SutConfig.Psw.HDD_PASSWORD_NAME_01, SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.HDD_NAME_01_OS, SutConfig.Psw.HDD_NAME_02_OS
            else:
                return None
        elif types == ['tcg', 'tcg']:
            if re.search('tcg', SutConfig.Psw.HDD_PASSWORD_NAME_01, re.I) and re.search('tcg', SutConfig.Psw.HDD_PASSWORD_NAME_02, re.I):
                return SutConfig.Psw.HDD_PASSWORD_NAME_01, SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.HDD_NAME_01_OS, SutConfig.Psw.HDD_NAME_02_OS
            else:
                return None
        elif types == ['ata', 'ata']:
            if re.search('ata', SutConfig.Psw.HDD_PASSWORD_NAME_01, re.I) and re.search('ata', SutConfig.Psw.HDD_PASSWORD_NAME_02, re.I):
                return SutConfig.Psw.HDD_PASSWORD_NAME_01, SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.HDD_NAME_01_OS, SutConfig.Psw.HDD_NAME_02_OS
            else:
                return None
        else:
            return None


def init_sut():
    BmcLib.init_sut()


def boot_to_setup(key=Key.DEL, is_del=True, password='admin'):
    if password == 'admin':
        password = PwdLib.HDD_PW.ADMIN if PwdLib.HDD_PW.ADMIN else ''
    elif password == 'admin_another':
        password = PwdLib.HDD_PW.ADMIN_ANOTHER if PwdLib.HDD_PW.ADMIN_ANOTHER else ''
    else:
        password = PwdLib.HDD_PW.ADMIN if PwdLib.HDD_PW.ADMIN else ''
    init_sut()
    logging.info("SetUpLib: Booting to setup")
    try_counts = 3
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        result = SetUpLib.boot_with_hotkey_only(key, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE,
                                                SutConfig.Psw.POST_HDD_MSG, password)
        if result == [True, True]:
            if is_del:
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_01], 18)
                if SetUpLib.wait_message(SutConfig.Psw.DISABLE_PSW_NAME, 3):
                    SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
                    PwdLib.del_hdd_psw(password, True)
                SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_02], 18)
                if SetUpLib.wait_message(SutConfig.Psw.DISABLE_PSW_NAME, 3):
                    SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
                    PwdLib.del_hdd_psw(password, True)
                SetUpLib.back_to_setup_toppage()
                return True
            else:
                return [True, True]
        elif result == True:
            return True
        else:
            init_sut()
            try_counts -= 1
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


def boot_to_setup_two(key=Key.DEL, is_del=True):
    if PwdLib.HDD_PW.ADMIN and PwdLib.HDD_PW.ADMIN_ANOTHER:
        init_sut()
        BmcLib.enable_serial_normal()
        if not SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG):
            assert boot_to_setup(is_del=is_del)
            return True
        PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, '')
        if not SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG):
            assert boot_to_setup(is_del=is_del)
            return True
        PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        assert SetUpLib.boot_with_hotkey_only(key, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        if is_del:
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_01,
                                                                               SutConfig.Psw.DISABLE_PSW_NAME], 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_02,
                                                                               SutConfig.Psw.DISABLE_PSW_NAME], 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    elif PwdLib.HDD_PW.ADMIN is not None and PwdLib.HDD_PW.ADMIN_ANOTHER is None:
        assert boot_to_setup(key, is_del, 'admin')
        return True
    elif PwdLib.HDD_PW.ADMIN is None and PwdLib.HDD_PW.ADMIN_ANOTHER is not None:
        assert boot_to_setup(key, is_del, 'admin_another')
        return True
    else:
        assert boot_to_setup(key, is_del)
        return True


def update_bios_setup():
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Msg.PAGE_EXIT, 18)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.SETUP_LATEST, 40, 'Confirmation', timeout=15)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')
    init_sut()
    time.sleep(200)
    BmcLib.enable_serial_normal()
    init_sut()
    return True


def update_bios_shell():
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 30,
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
    SetUpLib.send_data(f'{SutConfig.Upd.SHELL_FLASH_CMD_LATEST}')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SHELL_MSG_NOR, 300):
        logging.info('BIOS 更新成功')
    time.sleep(5)
    init_sut()
    BmcLib.enable_serial_normal()
    return True


@core.test_case(('800', '[TC800]HDD Password Security 000', '硬盘密码前提测试'))
def hdd_password_000():
    """
    Name:   硬盘密码前提测试
    
    Steps:  1.确认config定义的两个硬盘名称和Setup下一致
            2.确认硬盘密码长度最小值最大值
    """
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW, 18)
        data = SetUpLib.get_data(2)
        if not re.search(SutConfig.Psw.HDD_PASSWORD_NAME_01, data):
            SutConfig.Psw.HDD_PASSWORD_NAME_01 = ''
            logging.info('硬盘1名错误')
            count += 1
        else:
            assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.HDD_PASSWORD_NAME_01,
                                                   SutConfig.Psw.ENABLE_HDD_NAME],
                                        5)
            if not re.search(f'{str(PwdLib.HDD_PW.MIN)}\s*to\s*{str(PwdLib.HDD_PW.MAX)}', SetUpLib.help_msg):
                min = re.findall('(\d+)\s*to\s*\d+', SetUpLib.help_msg)[0] if re.findall('(\d+)\s*to\s*\d+',
                                                                                         SetUpLib.help_msg) else None
                max = re.findall('\d+\s*to\s*(\d+)', SetUpLib.help_msg)[0] if re.findall('\d+\s*to\s*(\d+)',
                                                                                         SetUpLib.help_msg) else None
                if min and min in ['6', '8']:
                    PwdLib.HDD_PW.MIN = int(min)
                if max and max in ['20', '32']:
                    PwdLib.HDD_PW.MAX = int(max)

        if not re.search(SutConfig.Psw.HDD_PASSWORD_NAME_02, data):
            SutConfig.Psw.HDD_PASSWORD_NAME_02 = ''
            logging.info('硬盘2名错误')
            count += 1
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW, 18)
            assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.ENABLE_HDD_NAME],
                                        5)
            if not re.search(f'{str(PwdLib.HDD_PW.MIN)}\s*to\s*{str(PwdLib.HDD_PW.MAX)}', SetUpLib.help_msg):
                min = re.findall('(\d+)\s*to\s*\d+', SetUpLib.help_msg)[0] if re.findall('(\d+)\s*to\s*\d+',
                                                                                         SetUpLib.help_msg) else None
                max = re.findall('\d+\s*to\s*(\d+)', SetUpLib.help_msg)[0] if re.findall('\d+\s*to\s*(\d+)',
                                                                                         SetUpLib.help_msg) else None
                if min and min in ['6', '8']:
                    PwdLib.HDD_PW.MIN = int(min)
                if max and max in ['20', '32']:
                    PwdLib.HDD_PW.MAX = int(max)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('801', '[TC801]HDD Password Security 001', 'TCG协议硬盘密码设置检查'))
def hdd_password_001():
    """
    Name:   TCG协议硬盘密码设置检查

    Steps:  1.开机，进入setup的安全界面，进入硬盘密码页面。
            2.选择并进入该硬盘选项
            3.选择启动硬盘管理员密码,检查弹框内的字符描述正确。
            4.设置符合密码复杂度和密码长度的硬盘密码，确认硬盘密码，检查密码是否设置成功
            5.禁用硬盘密码,关机

    Result: 1.硬盘密码界面有：设置硬盘密码的哈希算法、接入的硬盘信息。
            2.页面只有“启动硬盘管理员密码”可选；设置硬盘密码状态是“未安装”；帮助信息描述无误。
            3.设置硬盘密码对话框的抬头描述正确，对话框内容描述无误。
            4.密码设置成功,界面启用管理员密码选项消失，设置硬盘密码状态变成“已安装”。界面有这些选项：安全擦除硬盘数据、禁用硬盘密码、更改硬盘用户密码、更改硬盘管理员密码。

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW, 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HASH_NAME, hdd_name], 6)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 5)
        assert PwdLib.set_hdd_admin(admin, True), '硬盘密码设置失败'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME, SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 10)
        assert PwdLib.del_hdd_psw(admin, True), '硬盘密码删除失败'
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('802', '[TC802]HDD Password Security 002', 'TCG协议设置硬盘密码的哈希算法'))
def hdd_password_002():
    """
    Name:   TCG协议设置硬盘密码的哈希算法

    Steps:  1.开机，进入setup的安全界面的硬盘密码页面,检查“设置硬盘密码的哈希算法”默认值
            2.使用默认算法设置硬盘管理员密码后，检查“设置硬盘密码的哈希算法”状态,F9后检查状态
            3.关机后再开机，检查POST阶段校验密码是否成功。关机
            4.禁用硬盘密码

    Result: 1.默认值是“SHA-256 Hash”
            2.“设置硬盘密码的哈希算法”状态是灰选，不可更改,按F9后“设置硬盘密码的哈希算法”选项不会恢复为默认值
            3.POST界面输入正确的硬盘管理员密码可以校验成功

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        SetUpLib.default_save()
        assert boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW, 18)
        assert SetUpLib.verify_info([f'<SHA-256 Hash>\s*{SutConfig.Psw.HASH_NAME}'], 3)
        assert SetUpLib.locate_menu(Key.DOWN, [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        if boot_to_setup(is_del=False) != [True, True]:
            logging.info('POST校验硬盘密码失败')
            return
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name,
                                                                           SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('803', '[TC803]HDD Password Security 003', 'TCG协议硬盘管理员密码长度边界值校验'))
def hdd_password_003():
    """
    Name:   TCG协议硬盘管理员密码长度边界值校验

    Steps:  遍历两种算法
            1.检查设置低于8位，符合密码复杂度要求的密码
            2.检查设置高于32位，符合密码复杂度要求的密码
            3.检查设置等于8位，符合密码复杂度要求的密码,新密码，确认密码不一致
            4.检查设置等于8位，符合密码复杂度要求的密码
            5.检查设置等于32位，符合密码复杂度要求的密码
            6.禁用硬盘密码

    Result: 1.设置不成功
            2.设置不成功
            3.设置不成功
            4.设置成功
            5..设置成功


    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    try:

        hash_types = SutConfig.Psw.HASH_TYPE
        random.shuffle(hash_types)
        for hash_type in hash_types:
            password_list = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                             PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4, total=PwdLib.HDD_PW.MAX + 2),
                             PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2, total=PwdLib.HDD_PW.MIN),
                             PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4, total=PwdLib.HDD_PW.MAX)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            assert PwdLib.set_hdd_admin(password_list[0], False, expect=PwdLib.hdd_pw_short)
            assert PwdLib.set_hdd_admin(password_list[1], False, expect=PwdLib.hdd_pw_long)
            assert PwdLib.set_hdd_admin(password_list[2], False, expect=PwdLib.hdd_pw_not_same,
                                        confirm_pw=password_list[3])
            assert PwdLib.set_hdd_admin(password_list[2], True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert PwdLib.set_hdd_admin(password_list[3], True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('804', '[TC804]HDD Password Security 004', 'TCG协议硬盘管理员密码复杂度检查'))
def hdd_password_004():
    """
    Name:  TCG协议硬盘管理员密码复杂度检查

    Steps:  遍历两种算法
            1.检查设置8位，不符合密码复杂度要求的密码

    Result: 1.设置不成功

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    try:
        hash_types = SutConfig.Psw.HASH_TYPE
        random.shuffle(hash_types)
        for hash_type in hash_types:
            password_list = [PwdLib.gen_pw(digit=8, upper=0, lower=0, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=8, lower=0, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=0, lower=8, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=8),
                             PwdLib.gen_pw(digit=4, upper=4, lower=0, symbol=0),
                             PwdLib.gen_pw(digit=4, upper=0, lower=4, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=4, lower=4, symbol=0),
                             PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=0),
                             PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                             PwdLib.gen_pw(digit=0, upper=4, lower=0, symbol=4),
                             PwdLib.gen_pw(digit=0, upper=0, lower=4, symbol=4)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            for password in password_list:
                assert PwdLib.set_hdd_admin(password, False, expect=PwdLib.hdd_pw_simple)

        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('805', '[TC805]HDD Password Security 005', 'TCG协议更改硬盘管理员密码'))
def hdd_password_005():
    """
    Name:   TCG协议更改硬盘管理员密码

    Steps:  1.设置硬盘管理员密码
            2.更改管理员密码，校验时输入错误的管理员密码
            3.重复步骤2两次
            4.开机，更改管理员密码输入正确的管理员密码，设置新密码时，输入符合密码复杂度但是不符合密码长度的硬盘管理员密码。
            5.设置新密码时，输入不符合密码复杂度但是符合密码长度的硬盘管理员密码。
            6.设置新密码时，新密码确认密码不同
            7.设置新密码时，输入符合密码长度和密码复杂度的硬盘管理员密码。
            8.禁用硬盘密码
    Result: 2.原始密码校验失败后，会出现密码错误的弹框，按Enter后退出
            3.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            4/5/6.不能修改不符合规则的硬盘管理员密码
            7.硬盘密码修改成功
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')

    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = [PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                 PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]

    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
        assert PwdLib.set_hdd_admin(new_admin[-1], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_admin[-1], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_admin[-1], None, '1234657890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_ADMIN_NAME], 18)
        assert PwdLib.set_hdd_admin(new_admin[0], False, old_pw=admin, expect=PwdLib.hdd_pw_simple)
        assert PwdLib.set_hdd_admin(new_admin[1], False, old_pw=admin, expect=PwdLib.hdd_pw_short)
        assert PwdLib.set_hdd_admin(new_admin[2], False, old_pw=admin, expect=PwdLib.hdd_pw_not_same,
                                    confirm_pw='123465878')
        assert PwdLib.set_hdd_admin(new_admin[2], True, old_pw=admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw(admin, False)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('806', '[TC806]HDD Password Security 006', 'TCG协议删除硬盘管理员密码'))
def hdd_password_006():
    """
    Name:   TCG协议删除硬盘管理员密码

    Steps:  1.设置硬盘管理员密码
            2.选择“禁用硬盘密码”，弹框出现后输入错误的硬盘管理员密码。
            3.重复步骤2两次
            4.开机，禁用管理员密码输入正确的管理员密码

    Result:
            2.原始密码校验失败后，会出现密码错误的弹框，按Enter后退出
            3.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            4.硬盘管理员密码删除成功

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME],
                                                18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('807', '[TC807]HDD Password Security 007', 'TCG协议硬盘用户密码长度边界值校验'))
def hdd_password_007():
    """
    Name:   TCG协议硬盘用户密码长度边界值校验

    Steps:  遍历两种算法
            1.设置硬盘管理员密码
            2.选择“更改硬盘用户密码”，输入正确的硬盘管理员密码后，输入低于8位的符合密码复杂度的硬盘用户密码。检查是否可以设置成功。
            3.选择“更改硬盘用户密码”，输入正确的硬盘管理员密码后，输入超过32位的符合密码复杂度的硬盘用户密码。检查是否可以设置成功。
            4.选择“更改硬盘用户密码”，输入正确的硬盘管理员密码后，输入8位的符合密码复杂度的硬盘用户密码。检查是否可以设置成功。
            5.选择“更改硬盘用户密码”，输入正确的硬盘用户密码后，输入32位的符合密码复杂度的硬盘用户密码。检查是否可以设置成功。
            6.选择“禁用硬盘密码”后输入硬盘管理员密码即可删除硬盘密码。关机。

    Result: 2.设置失败
            3.设置失败
            4.设置成功
            5.设置成功
            6.硬盘管理员密码和硬盘用户密码都删除了。

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    hash_types = SutConfig.Psw.HASH_TYPE
    random.shuffle(hash_types)
    try:
        for hash_type in hash_types:
            admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
            user_list = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                         PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4, total=PwdLib.HDD_PW.MAX + 2),
                         PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.HDD_PW.MIN),
                         PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            assert PwdLib.set_hdd_admin(admin, True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
            assert PwdLib.set_hdd_user(user_list[0], False, admin, PwdLib.hdd_pw_short)
            assert PwdLib.set_hdd_user(user_list[1], False, admin, PwdLib.hdd_pw_long)
            assert PwdLib.set_hdd_user(user_list[2], True, admin)
            assert PwdLib.set_hdd_user(user_list[3], True, user_list[2])
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.verify_info(
                [SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 3)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('808', '[TC808]HDD Password Security 008', 'TCG协议硬盘用户密码复杂度检查'))
def hdd_password_008():
    """
    Name:   TCG协议硬盘用户密码复杂度检查

    Steps:  遍历两种算法
            1.设置硬盘管理员密码
            2.选择“更改硬盘用户密码”，输入正确的硬盘管理员密码后，输入8位，不符合密码复杂度的硬盘用户密码。检查是否可以设置成功。
            3.选择“更改硬盘用户密码”，输入正确的硬盘管理员密码后，输入8位，符合密码复杂度的硬盘用户密码。检查是否可以设置成功。
            4.选择“禁用硬盘密码”后输入硬盘管理员密码即可删除硬盘密码。关机。

    Result: 2.设置失败
            3.设置成功
            4.硬盘管理员密码和硬盘用户密码都删除了。

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    hash_types = SutConfig.Psw.HASH_TYPE
    random.shuffle(hash_types)
    try:
        for hash_type in hash_types:
            admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
            user_list = [PwdLib.gen_pw(digit=8, upper=0, lower=0, symbol=0),
                         PwdLib.gen_pw(digit=0, upper=8, lower=0, symbol=0),
                         PwdLib.gen_pw(digit=0, upper=0, lower=8, symbol=0),
                         PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=8),
                         PwdLib.gen_pw(digit=4, upper=4, lower=0, symbol=0),
                         PwdLib.gen_pw(digit=4, upper=0, lower=4, symbol=0),
                         PwdLib.gen_pw(digit=0, upper=4, lower=4, symbol=0),
                         PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=0),
                         PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                         PwdLib.gen_pw(digit=0, upper=4, lower=0, symbol=4),
                         PwdLib.gen_pw(digit=0, upper=0, lower=4, symbol=4),
                         PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.HDD_PW.MIN)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            assert PwdLib.set_hdd_admin(admin, True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
            for user in user_list[:-1]:
                assert PwdLib.set_hdd_user(user, False, admin, expect=PwdLib.hdd_pw_simple)
            assert PwdLib.set_hdd_user(user_list[-1], True, admin)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.verify_info(
                [SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 3)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('809', '[TC809]HDD Password Security 009', 'TCG协议修改硬盘用户密码'))
def hdd_password_009():
    """
    Name:   TCG协议修改硬盘用户密码

    Steps:  1.设置硬盘管理员密码
            2.选择“更改硬盘用户密码”，输入错误的硬盘管理员密码
            3.重复步骤2两次。
            4.选择“更改硬盘用户密码”，输错密码2次，选择“更改硬盘管理员密码”，输错密码1次
            5.选择“ 更改硬盘用户密码”，输错硬盘管理员密码2次后输入正确的管理员密码，输入符合硬盘密码规则的新的硬盘用户密码。
            6.选择“ 更改硬盘用户密码”，输错硬盘用户密码2次后输入正确的用户密码，输入不符合硬盘密码规则的新的硬盘用户密码。
            7.删除硬盘密码

    Result: 2.修改硬盘密码的弹框字符显示正确，输入错误的硬盘密码后会出现硬盘密码错误的提示信息。
            3.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            4.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            5.可以修改硬盘用户密码。
            6.不能修改硬盘用户密码。
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)

    user_list = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                 PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
        assert PwdLib.set_hdd_user(user_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_user(user_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_user(user_list[-1], None, '1234567890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_USER_NAME],
                                    18)
        assert PwdLib.set_hdd_user(user_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_user(user_list[-1], None, '1234567890')
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.CHANGE_ADMIN_NAME], 10)
        assert PwdLib.set_hdd_user(user_list[-1], None, '1234567890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_USER_NAME],
                                    18)
        assert PwdLib.set_hdd_user(user_list[-1], None, '123456789', PwdLib.hdd_pw_invalid)
        assert PwdLib.set_hdd_user(user_list[-1], None, '123456789', PwdLib.hdd_pw_invalid)
        assert PwdLib.set_hdd_user(user_list[-1], True, admin), '修改用户密码输错当前密码2次，第三次输入正确密码仍无法修改'
        assert PwdLib.set_hdd_user(user_list[0], None, '123456789', PwdLib.hdd_pw_invalid)
        assert PwdLib.set_hdd_user(user_list[0], None, '123456789', PwdLib.hdd_pw_invalid)
        assert PwdLib.set_hdd_user(user_list[0], False, user_list[-1], expect=PwdLib.hdd_pw_short)
        assert PwdLib.set_hdd_user(user_list[1], False, user_list[-1], expect=PwdLib.hdd_pw_simple)
        assert PwdLib.set_hdd_user(user_list[2], False, user_list[-1], expect=PwdLib.hdd_pw_not_same,
                                   confirm_pw=user_list[-1])
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('810', '[TC810]HDD Password Security 010', 'TCG协议管理员,用户密码测试'))
def hdd_password_010():
    """
    Name:   TCG协议管理员,用户密码测试

    Steps:  1.设置管理员，用户密码
            2.修改管理员密码,校验输入用户密码
            3.修改用户密码，校验输入管理员，用户密码
            4.POST阶段输错密码2次后输入正确的管理员密码，检查启动菜单，SetUp硬盘状态
            5.POST阶段输错密码2次后输入正确的用户密码，检查启动菜单，SetUp硬盘状态

    Result: 2.提示密码错误
            3.可以修改用户密码
            4/5.密码正确，启动菜单有该硬盘启动项，SetUp硬盘没有被锁住

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)

    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
        assert PwdLib.set_hdd_user(user, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
        assert PwdLib.set_hdd_admin(new_admin, None, user, PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
        assert PwdLib.set_hdd_user(new_user, True, user)
        assert PwdLib.set_hdd_user(user, True, admin)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(admin, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name, data)
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED], 5)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(user, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name, data)
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED], 5)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw(admin, True)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('811', '[TC811]HDD Password Security 011', 'TCG协议删除硬盘管理员&用户密码'))
def hdd_password_011():
    """
    Name:   TCG协议删除硬盘管理员&用户密码

    Steps:  1.设置硬盘管理员密码和用户密码
            2.选择“禁用硬盘密码”，弹框出现后输入错误的硬盘管理员密码。
            3.选择“禁用硬盘密码”，弹框出现后输入正确的硬盘用户密码。
            4.选择“禁用硬盘密码”，输入正确的硬盘管理员密码。关机。

    Result: 2/3.原始密码校验失败后，会出现密码错误的弹框，按Enter后退出。
            4.会出现密码已清除的提示信息。硬盘用户密码和硬盘管理员密码都清除了。
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)

    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
        assert PwdLib.set_hdd_user(user, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw(user, False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw(admin, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 3)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('812', '[TC812]HDD Password Security 012', 'TCG协议硬盘密码状态检查'))
def hdd_password_012():
    """
    Name:   TCG协议硬盘密码状态检查

    Steps:  1.设置硬盘管理员密码，SetUp下F10保存重启
            2.检查设置硬盘密码状态，检查硬盘密码可以修改、禁用
            3.从Setup退出菜单的启动管理器直接选择进入该NVME硬盘的启动项，进入系统后重启，检查设置硬盘密码状态，检查硬盘密码可以修改、禁用
            4.删除硬盘密码
            5.进入系统后重启,检查设置硬盘密码状态
            6.重启进入设备管理菜单，选择Internal EFI Shell启动，进入shell后输入exit退出,返回设备管理菜单后，选择进入setup
            7.检查设置硬盘密码状态
            8.关机后再开机，进入setup设置硬盘密码
            9.从退出菜单的启动管理器选择Internal EFI Shell启动，进入shell后输入exit退出
            10.退出到Setup后，依次执行修改硬盘管理员密码、修改硬盘用户密码、禁用硬盘密码



    Result: 2/3.POST不校验密码，检查硬盘密码可以修改、禁用，硬盘密码可以修改、禁用
            5/7.硬盘是锁定状态，无法启用硬盘密码
            10.从Setup进入shell后回退到硬盘密码界面后，硬盘密码不应该被改动，此时选择硬盘密码相关选项会弹出警告弹窗，需关机重启
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME, SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 10)
        assert PwdLib.set_hdd_admin(new_admin, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
        assert PwdLib.del_hdd_psw(new_admin, True)
        assert PwdLib.set_hdd_admin(admin, True)
        if hasattr(SutConfig.Psw, 'LOC_BOOT_MANAGER'):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_BOOT_MANAGER + [hdd_boot_name], 18)
            if SetUpLib.wait_message(SutConfig.Psw.BOOT_MANAGER_MSG, 10):
                logging.info('该硬盘可能没有安装系统,跳过测试')
                boot_to_setup()
                return core.Status.Skip
        else:
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG)
            assert PwdLib.check_psw_post(admin, '')
            assert SetUpLib.boot_to_boot_menu(reset=False)
            assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
            if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 10):
                logging.info('该硬盘可能没有安装系统,跳过测试')
                boot_to_setup()
                return core.Status.Skip
        assert BmcLib.ping_sut(), '进入硬盘系统失败'
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME, SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
        assert PwdLib.del_hdd_psw(admin, True)
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
        assert BmcLib.ping_sut()
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2)
        assert SetUpLib.boot_to_shell()
        SetUpLib.send_data_enter('exit')
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2)
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        if hasattr(SutConfig.Psw, 'LOC_BOOT_MANAGER'):
            assert PwdLib.set_hdd_admin(admin, True)
            assert boot_to_setup(is_del=False)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_BOOT_MANAGER + [SutConfig.Msg.USB_UEFI],
                                                    18)
            assert SetUpLib.wait_message('UEFI Interactive Shell', 10)
            time.sleep(10)
            SetUpLib.send_data_enter('exit')
            assert SetUpLib.wait_message(SutConfig.Psw.BOOT_MANAGER_MSG, 10)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.ERASE_NAME,18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert boot_to_setup()
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('813', '[TC813]HDD Password Security 013', 'TCG协议硬盘密码输错测试'))
def hdd_password_013():
    """
    Name:   TCG协议硬盘密码输错测试

    Steps:  1.设置硬盘管理员密码
            2.POST阶段校验密码阶段，输入3次错误的硬盘密码
            3.检查启动菜单，SetUp下是否有该硬盘的启动项，安全菜单的硬盘密码，检查是否有该硬盘信息
            4.POST阶段校验密码阶段，输入2次错误的硬盘密码，在输入正确的硬盘密码
            5.检查启动菜单，SetUp下是否有该硬盘的启动项，安全菜单的硬盘密码，检查是否有该硬盘信息
            6.选择“安全擦除硬盘输入”，输入错误的硬盘管理员密码,选择“更改硬盘用户密码”，输入错误的硬盘管理员密码
              ,选择“禁用硬盘密码”，输入错误的硬盘管理员密码
            7.开机，进入setup的安全界面，进入硬盘密码页面,选择“安全擦除硬盘输入”，输入错误的硬盘管理员密码,选择“更改硬盘用户密码”，
              输入错误的硬盘管理员密码
            8.选择“禁用硬盘密码”，输入正确的硬盘管理员密码
            9.启用硬盘管理员密码
            10.选择“禁用硬盘密码”，输入错误的硬盘管理员密码
            11.开机，进入setup的安全界面，进入硬盘密码页面，选择“安全擦除硬盘输入”，输入错误的硬盘管理员密码,选择“更改硬盘用户密码”，
              输入错误的硬盘管理员密码
            12.选择“修改硬盘管理员密码”，输入正确的硬盘管理员密码按Enter键，光标定位到输入新密码时按ESC键退出
            13.选择“禁用硬盘密码”，输入错误的硬盘管理员密码
            14.重复步骤13两次
            15.删除硬盘密码

    Result: 2.会提示硬盘密码错误，有硬盘被锁定的提示。
            3.没有该硬盘的启动项
            4.密码正确
            5.有该硬盘的启动项
            6.累计输入错误3次后会在提示信息后倒计时3秒系统关机
            8.硬盘密码被清除
            10.会提示硬盘密码无效，但是不会出现3秒后关机
            13.会提示硬盘密码无效，但是不会出现3秒后关机
            14.累计输入错误3次后会在提示信息后倒计时3秒系统关机
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name, data), '输错三次密码，启动菜单仍有该启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2), '输错三次密码，硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(admin, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name, data), '输错两次密码，第三次输入正确密码，启动菜单没有该启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED], 5)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.ERASE_NAME, 6)
        assert PwdLib.del_hdd_psw('12345789044',False,PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 6)
        assert PwdLib.set_hdd_admin(admin, None, old_pw='1234567890', expect=PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 6)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.ERASE_NAME, 6)
        assert PwdLib.del_hdd_psw('12345789044',False,PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 6)
        assert PwdLib.set_hdd_admin(admin, None, old_pw='1234567890', expect=PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 10)
        assert PwdLib.del_hdd_psw(admin, True)
        assert PwdLib.set_hdd_admin(new_admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 10)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.ERASE_NAME, 6)
        assert PwdLib.del_hdd_psw('12345789044',False,PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 6)
        assert PwdLib.set_hdd_admin(admin, None, old_pw='1234567890', expect=PwdLib.hdd_pw_invalid)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 6)
        time.sleep(2)
        SetUpLib.send_data_enter(new_admin)
        assert not SetUpLib.wait_message(PwdLib.hdd_pw_invalid, 2)
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 6)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME],
                                    18)
        assert PwdLib.del_hdd_psw(new_admin, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('814', '[TC814]HDD Password Security 014', 'TCG协议硬盘密码ESC跳过测试'))
def hdd_password_014():
    """
    Name:   TCG协议硬盘密码ESC跳过测试

    Steps:  1.设置硬盘管理员密码
            2.POST阶段校验密码阶段，ESC跳过硬盘密码
            3.检查启动菜单，SetUp下是否有该硬盘的启动项，安全菜单的硬盘密码，检查是否有该硬盘信息
            4.POST阶段校验密码阶段，ESC跳过硬盘密码,启动菜单进入Shell，输入reconnect -r,检查是否弹出硬盘密码输入框
            5.删除硬盘密码

    Result: 2.会提示硬盘密码错误，有硬盘被锁定的提示。
            4.不会弹出硬盘密码输入框
            3.没有该硬盘的启动项
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name, data), '跳过密码，启动菜单仍有该启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2), '跳过密码，硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        SetUpLib.boot_to_boot_menu(False, False)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 30, 'UEFI Interactive Shell')
        time.sleep(10)
        SetUpLib.send_data_enter('reconnect -r')
        assert not SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG, 5)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME],
                                    18)
        assert PwdLib.del_hdd_psw(admin, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('815', '[TC815]HDD Password Security 015', 'TCG协议硬盘密码校验测试'))
def hdd_password_015():
    """
    Name:   TCG协议硬盘密码校验测试

    Steps:  1.设置硬盘管理员密码
            2.关机，开机检查POST阶段是否校验密码
            3.SetUp下F10保存重启，检查POST阶段是否校验密码
            4.系统下重启，检查POST阶段是否校验密码

    Result: 2.POST阶段校验密码
            3/4.POST阶段不会校验密码

    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        init_sut()
        if boot_to_setup(is_del=False) != [True, True]:
            logging.info('POST校验硬盘密码失败')
            return
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_boot_menu(reset=False), 'SetUp下F10重启，POST阶段校验密码'
        assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
        if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 10):
            logging.info('该硬盘可能没有安装系统,跳过测试')
            boot_to_setup()
            return core.Status.Skip
        assert BmcLib.ping_sut(), '进入硬盘系统失败'
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_to_boot_menu(reset=False), '系统下重启,POST校验密码'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(admin, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('816', '[TC816]HDD Password Security 016', 'TCG协议硬盘密码更新BIOS'))
def hdd_password_016():
    """
    Name:   TCG协议硬盘密码更新BIOS

    Steps:  1.设置硬盘管理员密码
            2.SetUp下更新BIOS，检查硬盘密码
            3.Shell下更新BIOS，检查硬盘密码
            4.删除密码

    Result: 2/3.更新BIOS后，硬盘密码依然存在
    """
    if not get_hdd_msg('tcg'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('tcg')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        SetUpLib.default_save()
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert boot_to_setup(is_del=False)==[True,True]
        assert update_bios_setup()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), '刷新BIOS后硬盘密码不存在'
        assert PwdLib.check_psw_post(admin,'')
        data=SetUpLib.boot_to_boot_menu(True,False)
        assert re.search(hdd_name,data),'刷新BIOS后启动菜单没有该硬盘启动项'
        assert update_bios_shell()
        assert boot_to_setup(is_del=False)==[True,True],'刷新BIOS后硬盘密码不存在'
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(admin, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail




@core.test_case(('831', '[TC831]HDD Password Security 031', 'ATA协议硬盘密码检查设置'))
def hdd_password_031():
    """
    Name:   ATA协议硬盘密码检查设置

    Steps:  1.开机，进入setup的安全界面，进入硬盘密码页面。
            2.选择并进入该ATA硬盘选项
            3.选择启动硬盘用户密码,检查弹框内的字符描述正确。
            4.设置符合密码复杂度和密码长度的硬盘密码，确认硬盘密码，检查密码是否设置成功
            5.禁用硬盘密码,关机

    Result: 1.硬盘密码界面有：设置硬盘密码的哈希算法、接入的ATA硬盘信息。
            2.页面只有“启动硬盘用户密码”可选；设置硬盘密码状态是“未安装”；帮助信息描述无误。
            3.设置硬盘密码对话框的抬头描述正确，对话框内容描述无误。
            4.密码设置成功,界面启用硬盘用户密码选项消失，设置硬盘密码状态变成“已安装”。界面有这些选项：安全擦除硬盘数据、禁用硬盘密码、更改硬盘用户密码、更改硬盘管理员密码。
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW, 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HASH_NAME, hdd_name], 6)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 5)
        assert PwdLib.set_hdd_admin(user, True), '硬盘密码设置失败'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME,
             SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 10)
        assert PwdLib.del_hdd_psw(user, True), '硬盘密码删除失败'
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('832', '[TC832]HDD Password Security 032', '设置ATA协议硬盘密码的哈希算法'))
def hdd_password_032():
    """
    Name:   设置ATA协议硬盘密码的哈希算法

    Steps:  1.开机，进入setup的安全界面的硬盘密码页面,检查“设置硬盘密码的哈希算法”默认值
            2.使用默认算法设置ATA硬盘密码后，检查“设置硬盘密码的哈希算法”状态,F9后检查状态
            3.关机后再开机，检查POST阶段校验密码是否成功。关机
            4.禁用硬盘密码

    Result: 1.默认值是“SHA-256 Hash”
            2.“设置硬盘密码的哈希算法”状态是灰选，不可更改,按F9后“设置硬盘密码的哈希算法”选项不会恢复为默认值
            3.POST界面输入正确的硬盘管理员密码可以校验成功

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        SetUpLib.default_save()
        assert boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW, 18)
        assert SetUpLib.verify_info([f'<SHA-256 Hash>\s*{SutConfig.Psw.HASH_NAME}'], 3)
        assert SetUpLib.locate_menu(Key.DOWN, [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        if boot_to_setup(is_del=False) != [True, True]:
            logging.info('POST校验硬盘密码失败')
            return
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name,
                                                                           SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('833', '[TC833]HDD Password Security 033', 'ATA协议硬盘用户密码长度边界值校验'))
def hdd_password_033():
    """
    Name:   ATA协议硬盘用户密码长度边界值校验

    Steps:  遍历两种算法
            1.检查设置低于8位，符合密码复杂度要求的密码
            2.检查设置高于32位，符合密码复杂度要求的密码
            3.检查设置等于8位，符合密码复杂度要求的密码,新密码，确认密码不同
            4.检查设置等于8位，符合密码复杂度要求的密码
            5.检查设置等于32位，符合密码复杂度要求的密码
            6.禁用硬盘密码

    Result: 1.设置不成功
            2.设置不成功
            3.设置不成功
            4.设置成功
            5.设置成功

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    try:

        hash_types = SutConfig.Psw.HASH_TYPE
        random.shuffle(hash_types)
        for hash_type in hash_types:
            password_list = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                             PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4, total=PwdLib.HDD_PW.MAX + 2),
                             PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2, total=PwdLib.HDD_PW.MIN),
                             PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4, total=PwdLib.HDD_PW.MAX)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            assert PwdLib.set_hdd_admin(password_list[0], False, expect=PwdLib.hdd_pw_short)
            assert PwdLib.set_hdd_admin(password_list[1], False, expect=PwdLib.hdd_pw_long)
            assert PwdLib.set_hdd_admin(password_list[2], False, expect=PwdLib.hdd_pw_not_same, confirm_pw='1223345565')
            assert PwdLib.set_hdd_admin(password_list[2], True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert PwdLib.set_hdd_admin(password_list[3], True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('834', '[TC834]HDD Password Security 034', 'ATA协议硬盘管理员密码长度边界值校验'))
def hdd_password_034():
    """
    Name:   ATA协议硬盘管理员密码长度边界值校验

    Steps:  遍历两种算法
            1.设置硬盘用户密码
            2.选择“更改硬盘管理员密码”，输入正确的硬盘用户密码后，输入低于8位的符合密码复杂度的硬盘管理员密码。检查是否可以设置成功。
            3.选择“更改硬盘管理员密码”，输入正确的硬盘用户密码后，输入超过32位的符合密码复杂度的硬盘管理员密码。检查是否可以设置成功。
            4.选择“更改硬盘管理员密码”，输入正确的硬盘用户密码后，输入8位的符合密码复杂度的硬盘管理员密码。检查是否可以设置成功。
            5.选择“更改硬盘管理员密码”，输入正确的硬盘用户密码后，输入32位的符合密码复杂度的硬盘管理员密码。检查是否可以设置成功。
            6.选择“禁用硬盘密码”后输入硬盘管理员密码即可删除硬盘密码。关机。
    Result: 1.设置不成功
            2.设置不成功
            3.设置成功
            4.设置成功

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    hash_types = SutConfig.Psw.HASH_TYPE
    random.shuffle(hash_types)
    try:
        for hash_type in hash_types:
            user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
            admin_list = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                          PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4, total=PwdLib.HDD_PW.MAX + 2),
                          PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.HDD_PW.MIN),
                          PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            assert PwdLib.set_hdd_admin(user, True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
            assert PwdLib.set_hdd_admin(admin_list[0], False, user, PwdLib.hdd_pw_short)
            assert PwdLib.set_hdd_admin(admin_list[1], False, user, PwdLib.hdd_pw_long)
            assert PwdLib.set_hdd_admin(admin_list[2], True, user)
            assert PwdLib.set_hdd_admin(admin_list[3], True, admin_list[2])
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.verify_info(
                [SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 3)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('835', '[TC835]HDD Password Security 035', 'ATA协议硬盘用户密码复杂度检查'))
def hdd_password_035():
    """
    Name:   ATA协议硬盘用户密码复杂度检查

    Steps:  遍历两种算法
            1.检查设置8位，不符合密码复杂度要求的密码

    Result: 1.设置不成功

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    try:
        hash_types = SutConfig.Psw.HASH_TYPE
        random.shuffle(hash_types)
        for hash_type in hash_types:
            password_list = [PwdLib.gen_pw(digit=8, upper=0, lower=0, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=8, lower=0, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=0, lower=8, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=8),
                             PwdLib.gen_pw(digit=4, upper=4, lower=0, symbol=0),
                             PwdLib.gen_pw(digit=4, upper=0, lower=4, symbol=0),
                             PwdLib.gen_pw(digit=0, upper=4, lower=4, symbol=0),
                             PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=0),
                             PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                             PwdLib.gen_pw(digit=0, upper=4, lower=0, symbol=4),
                             PwdLib.gen_pw(digit=0, upper=0, lower=4, symbol=4)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            for password in password_list:
                assert PwdLib.set_hdd_admin(password, False, expect=PwdLib.hdd_pw_simple)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('836', '[TC836]HDD Password Security 036', 'ATA协议硬盘管理员密码复杂度检查'))
def hdd_password_036():
    """
    Name:   ATA协议硬盘管理员密码复杂度检查

    Steps:  遍历两种算法
            1.设置硬盘用户密码
            2.选择“更改硬盘管理员密码”，输入正确的硬盘用户密码后，输入8位，不符合密码复杂度的硬盘管理员密码。检查是否可以设置成功。
            3.选择“更改硬盘管理员密码”，输入正确的硬盘用户密码后，输入8位，符合密码复杂度的硬盘管理员密码。检查是否可以设置成功。
            4.选择“禁用硬盘密码”后输入硬盘管理员密码即可删除硬盘密码。关机。

    Result: 2.设置失败
            3.设置成功
            4.硬盘管理员密码和硬盘用户密码都删除了。

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    hash_types = SutConfig.Psw.HASH_TYPE
    random.shuffle(hash_types)
    try:
        for hash_type in hash_types:
            user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
            admin_list = [PwdLib.gen_pw(digit=8, upper=0, lower=0, symbol=0),
                          PwdLib.gen_pw(digit=0, upper=8, lower=0, symbol=0),
                          PwdLib.gen_pw(digit=0, upper=0, lower=8, symbol=0),
                          PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=8),
                          PwdLib.gen_pw(digit=4, upper=4, lower=0, symbol=0),
                          PwdLib.gen_pw(digit=4, upper=0, lower=4, symbol=0),
                          PwdLib.gen_pw(digit=0, upper=4, lower=4, symbol=0),
                          PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=0),
                          PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                          PwdLib.gen_pw(digit=0, upper=4, lower=0, symbol=4),
                          PwdLib.gen_pw(digit=0, upper=0, lower=4, symbol=4),
                          PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.HDD_PW.MIN)]
            assert boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Psw.LOC_HDD_PSW + [{SutConfig.Psw.HASH_NAME: hash_type}],
                                                    18, save=True)
            assert boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN,
                                        SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
            assert PwdLib.set_hdd_admin(user, True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
            for admin in admin_list[:-1]:
                assert PwdLib.set_hdd_admin(admin, False, user, expect=PwdLib.hdd_pw_simple)
            assert PwdLib.set_hdd_admin(admin_list[-1], True, user)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.verify_info(
                [SutConfig.Psw.HDD_PSW_STATUS_NOT_INSTALLED, SutConfig.Psw.ENABLE_HDD_NAME], 3)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('837', '[TC837]HDD Password Security 037', '更改ATA协议硬盘用户密码'))
def hdd_password_037():
    """
    Name:   更改ATA协议硬盘用户密码

    Steps:  1.设置ATA硬盘用户密码
            2.更改管理员密码，校验时输入错误的用户密码
            3.重复步骤2两次
            4.选择“ 更改硬盘用户密码”，输错硬盘用户密码2次，选择“ 更改硬盘管理员密码”，输错硬盘用户密码1次
            5.开机，更改用户密码输入正确的用户密码，设置新密码时，输入符合密码复杂度但是不符合密码长度的硬盘用户密码。
            6.设置新密码时，输入不符合密码复杂度但是符合密码长度的硬盘用户密码。
            7.设置新密码时，输入符合密码长度和密码复杂度的硬盘用户密码,新密码确认密码不一致
            8.设置新密码时，输入符合密码长度和密码复杂度的硬盘用户密码
            9.禁用硬盘密码
    Result: 2.原始密码校验失败后，会出现密码错误的弹框，按Enter后退出
            3/4.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            5/6.不能修改不符合规则的硬盘用户密码
            7.修改失败
            8.硬盘密码修改成功
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = [PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]

    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
        assert PwdLib.set_hdd_admin(new_user[-1], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_user[-1], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_user[-1], None, '1234657890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_USER_NAME], 18)
        assert PwdLib.set_hdd_admin(new_user[-1], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_user[-1], None, '1234657890')
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.CHANGE_ADMIN_NAME], 10)
        assert PwdLib.set_hdd_admin(new_user[-1], None, '1234657890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_USER_NAME], 18)
        assert PwdLib.set_hdd_admin(new_user[0], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_user[0], None, '1234657890')
        assert PwdLib.set_hdd_admin(new_user[0], False, old_pw=user, expect=PwdLib.hdd_pw_simple)
        assert PwdLib.set_hdd_admin(new_user[1], False, old_pw=user, expect=PwdLib.hdd_pw_short)
        assert PwdLib.set_hdd_admin(new_user[2], False, old_pw=user, expect=PwdLib.hdd_pw_not_same,
                                    confirm_pw='1234567895')
        assert PwdLib.set_hdd_admin(new_user[2], True, old_pw=user)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw(user, False)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('838', '[TC838]HDD Password Security 038', '修改ATA协议硬盘管理员密码'))
def hdd_password_038():
    """
    Name:   修改ATA协议硬盘管理员密码

    Steps:  1.设置硬盘用户密码
            2.选择“更改硬盘管理员密码”，输入错误的硬盘用户密码
            3.重复步骤2两次。
            4.选择“ 更改硬盘管理员密码”，输错硬盘用户密码2次，选择“ 更改硬盘用户密码”，输错硬盘用户密码1次
            5.选择“ 更改硬盘管理员密码”，输错硬盘密码2次,输入正确的硬盘用户密码后，输入符合硬盘密码规则的新的硬盘管理员密码。
            6.选择“ 更改硬盘管理员密码”，输错硬盘密码2次,输入正确的管理员密码后，输入不符合硬盘密码规则的新的硬盘管理员密码。
            7.删除硬盘密码

    Result: 2.修改硬盘密码的弹框字符显示正确，输入错误的硬盘密码后会出现硬盘密码错误的提示信息。
            3.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            4.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            5.可以修改硬盘管理员密码。
            6.不能修改硬盘管理员密码。
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)

    admin_list = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                  PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                  PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                  PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_ADMIN_NAME],
                                    18)
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890')
        assert SetUpLib.locate_menu(Key.UP, [SutConfig.Psw.CHANGE_USER_NAME], 10)
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890', expect=PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.CHANGE_ADMIN_NAME],
                                    18)
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[-1], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[-1], True, user), '修改管理员密码，当前密码输错2次后，输入正确密码仍修改失败'
        assert PwdLib.set_hdd_admin(admin_list[0], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[0], None, '1234567890')
        assert PwdLib.set_hdd_admin(admin_list[0], False, admin_list[-1], expect=PwdLib.hdd_pw_short)
        assert PwdLib.set_hdd_admin(admin_list[1], False, admin_list[-1], expect=PwdLib.hdd_pw_simple)
        assert PwdLib.set_hdd_admin(admin_list[2], False, admin_list[-1], expect=PwdLib.hdd_pw_not_same,
                                    confirm_pw=admin_list[-1])
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('839', '[TC839]HDD Password Security 039', '删除ATA协议硬盘密码'))
def hdd_password_039():
    """
    Name:   删除ATA协议硬盘密码

    Steps:  1.设置硬盘用户密码
            2.选择“禁用硬盘密码”，弹框出现后输入错误的硬盘密码。
            3.重复步骤2两次
            4.开机，禁用硬盘密码,输错密码2次后输入正确的用户密码
            5.设置管理员，用户密码
            6.禁用硬盘密码,输错密码2次后输入正确的管理员密码
            7.设置硬盘用户密码
            8.修改用户密码时输入禁用密码前设置的用户密码
            9.修改用户密码时输入禁用密码前设置的管理员密码
            10.删除密码时输入禁用密码前设置的管理员密码
    Result:
            2.原始密码校验失败后，会出现密码错误的弹框，按Enter后退出
            3.密码输错合计3次后会出现报错信息，倒计时3秒后系统关机。
            4/6.硬盘密码删除成功
            8.修改用户密码失败
            9.修改用户密码成功
            10.删除密码成功

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user_new = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user_new1 = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user_new2 = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME],
                                                18)
        assert PwdLib.del_hdd_psw('123456789', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('123456789', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw(user, True)
        assert PwdLib.set_hdd_admin(user_new, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
        assert PwdLib.set_hdd_admin(admin, True, user_new)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw('123456789', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('123456789', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw(admin, True)
        assert PwdLib.set_hdd_admin(user_new1, True)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.CHANGE_USER_NAME], 18)
        assert PwdLib.set_hdd_admin(user_new2, None, user_new)
        assert PwdLib.set_hdd_admin(user_new2, True, admin), '禁用硬盘密码时，管理员密码被禁用'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(admin, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('840', '[TC840]HDD Password Security 040', 'ATA协议管理员,用户密码测试'))
def hdd_password_040():
    """
    Name:   ATA协议管理员,用户密码测试

    Steps:  1.设置管理员，用户密码
            2.修改管理员密码,校验输入管理员，用户密码
            3.修改用户密码，校验输入管理员，用户密码
            4.POST阶段输错密码2次后输入正确的管理员密码，检查启动菜单，SetUp硬盘状态
            5.POST阶段输错密码2次后输入正确的用户密码，检查启动菜单，SetUp硬盘状态

    Result: 2.可以修改管理员密码
            3.可以修改用户密码
            4.提示硬盘密码错误,硬盘被锁定
            5.密码正确，启动菜单有该硬盘启动项，SetUp硬盘没有被锁住

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
        assert PwdLib.set_hdd_admin(admin, True, user)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
        assert PwdLib.set_hdd_admin(new_admin, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
        assert PwdLib.set_hdd_admin(new_user, True, new_admin)
        assert PwdLib.set_hdd_admin(user, True, new_user)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(new_admin, PwdLib.hdd_pw_limit_post)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('123456789', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(user, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name, data)
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED], 5)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 18)
        assert PwdLib.del_hdd_psw(new_admin, True)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('841', '[TC841]HDD Password Security 041', 'ATA协议NVME硬盘密码状态检查'))
def hdd_password_041():
    """
    Name:   ATA协议NVME硬盘密码状态检查

    Steps:  1.设置硬盘管理员密码，SetUp下F10保存重启
            2.检查设置硬盘密码状态，检查硬盘密码可以修改、禁用
            3.从Setup退出菜单的启动管理器直接选择进入该NVME硬盘的启动项，进入系统后重启，检查设置硬盘密码状态，检查硬盘密码可以修改、禁用
            4.删除硬盘密码
            5.进入系统后重启,检查设置硬盘密码状态
            6.重启进入设备管理菜单，选择Internal EFI Shell启动，进入shell后输入exit退出,返回设备管理菜单后，选择进入setup
            7.检查设置硬盘密码状态
            8.关机后再开机，进入setup设置硬盘密码
            9.从退出菜单的启动管理器选择Internal EFI Shell启动，进入shell后输入exit退出
            10.退出到Setup后，依次执行修改硬盘管理员密码、修改硬盘用户密码、禁用硬盘密码

    Result: 2/3.POST校验密码，检查硬盘密码可以修改、禁用，硬盘密码可以修改、禁用
            5/7.硬盘是锁定状态，无法启用硬盘密码
            10.从Setup进入shell后回退到硬盘密码界面后，硬盘密码不应该被改动，此时选择硬盘密码相关选项会弹出警告弹窗，需关机重启
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    if not re.search('nvme', hdd_name, re.I):
        logging.info('没有ATA协议的NVME硬盘')
        return core.Status.Skip
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG)
        assert PwdLib.check_psw_post(admin, '')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME, SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 10)
        assert PwdLib.set_hdd_admin(new_admin, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
        assert PwdLib.del_hdd_psw(new_admin, True)
        assert PwdLib.set_hdd_admin(admin, True)
        if hasattr(SutConfig.Psw, 'LOC_BOOT_MANAGER'):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_BOOT_MANAGER + [hdd_boot_name], 18)
            if SetUpLib.wait_message(SutConfig.Psw.BOOT_MANAGER_MSG, 10):
                logging.info('该硬盘可能没有安装系统,跳过测试')
                boot_to_setup()
                return core.Status.Skip
        else:
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG)
            assert PwdLib.check_psw_post(admin, '')
            assert SetUpLib.boot_to_boot_menu(reset=False)
            assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
            if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 10):
                logging.info('该硬盘可能没有安装系统,跳过测试')
                boot_to_setup()
                return core.Status.Skip
        assert BmcLib.ping_sut(), '进入硬盘系统失败'
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG)
        assert PwdLib.check_psw_post(admin, '')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME, SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
        assert PwdLib.del_hdd_psw(admin, True)
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
        assert BmcLib.ping_sut()
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2)
        assert SetUpLib.boot_to_shell()
        SetUpLib.send_data_enter('exit')
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2)
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        if hasattr(SutConfig.Psw, 'LOC_BOOT_MANAGER'):
            assert PwdLib.set_hdd_admin(admin, True)
            assert boot_to_setup(is_del=False)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_BOOT_MANAGER + [SutConfig.Msg.USB_UEFI],
                                                    18)
            assert SetUpLib.wait_message('UEFI Interactive Shell', 10)
            time.sleep(10)
            SetUpLib.send_data_enter('exit')
            assert SetUpLib.wait_message(SutConfig.Psw.BOOT_MANAGER_MSG, 10)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.ERASE_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert boot_to_setup()
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('842', '[TC842]HDD Password Security 042', 'ATA协议SATA硬盘密码状态检查'))
def hdd_password_042():
    """
    Name:   TCG协议硬盘密码状态检查

    Steps:  1.设置硬盘管理员密码，SetUp下F10保存重启
            2.检查设置硬盘密码状态，检查硬盘密码可以修改、禁用
            3.从Setup退出菜单的启动管理器直接选择进入该NVME硬盘的启动项，进入系统后重启，检查设置硬盘密码状态，检查硬盘密码可以修改、禁用
            4.删除硬盘密码
            5.进入系统后重启,检查设置硬盘密码状态
            6.重启进入设备管理菜单，选择Internal EFI Shell启动，进入shell后输入exit退出,返回设备管理菜单后，选择进入setup
            7.检查设置硬盘密码状态
            8.关机后再开机，进入setup设置硬盘密码
            9.从退出菜单的启动管理器选择Internal EFI Shell启动，进入shell后输入exit退出
            10.退出到Setup后，依次执行修改硬盘管理员密码、修改硬盘用户密码、禁用硬盘密码

    Result: 2/3.POST不校验密码，检查硬盘密码可以修改、禁用，硬盘密码可以修改、禁用
            5/7.硬盘是锁定状态，无法启用硬盘密码
            10.从Setup进入shell后回退到硬盘密码界面后，硬盘密码不应该被改动，此时选择硬盘密码相关选项会弹出警告弹窗，需关机重启
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    if not re.search('sata', hdd_name, re.I):
        logging.info('没有ATA协议的SATA硬盘')
        return core.Status.Skip
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info(
            [SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.ERASE_NAME, SutConfig.Psw.DISABLE_PSW_NAME,
             SutConfig.Psw.CHANGE_ADMIN_NAME, SutConfig.Psw.CHANGE_USER_NAME], 6)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 10)
        assert PwdLib.set_hdd_admin(new_admin, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
        assert PwdLib.del_hdd_psw(new_admin, True)
        assert PwdLib.set_hdd_admin(admin, True)
        if hasattr(SutConfig.Psw, 'LOC_BOOT_MANAGER'):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_BOOT_MANAGER + [hdd_boot_name], 18)
            if SetUpLib.wait_message(SutConfig.Psw.BOOT_MANAGER_MSG, 10):
                logging.info('该硬盘可能没有安装系统,跳过测试')
                boot_to_setup()
                return core.Status.Skip
        else:
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG)
            assert PwdLib.check_psw_post(admin, '')
            assert SetUpLib.boot_to_boot_menu(reset=False)
            assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
            if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 10):
                logging.info('该硬盘可能没有安装系统,跳过测试')
                boot_to_setup()
                return core.Status.Skip
        assert BmcLib.ping_sut(), '进入硬盘系统失败'
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 6)
        assert boot_to_setup()
        assert SetUpLib.boot_to_boot_menu()
        assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
        assert BmcLib.ping_sut()
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.SETUP_MESSAGE, 200, SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2)
        assert SetUpLib.boot_to_shell()
        SetUpLib.send_data_enter('exit')
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2)
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        if hasattr(SutConfig.Psw, 'LOC_BOOT_MANAGER'):
            assert PwdLib.set_hdd_admin(admin, True)
            assert boot_to_setup(is_del=False)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_BOOT_MANAGER + [SutConfig.Msg.USB_UEFI],
                                                    18)
            assert SetUpLib.wait_message('UEFI Interactive Shell', 10)
            time.sleep(10)
            SetUpLib.send_data_enter('exit')
            assert SetUpLib.wait_message(SutConfig.Psw.BOOT_MANAGER_MSG, 10)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 10)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.ERASE_NAME, 18)
            assert SetUpLib.wait_message(PwdLib.hdd_pw_frozen, 3), '硬盘没有被冻结'
            SetUpLib.send_keys([Key.ENTER])
            assert boot_to_setup()
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('843', '[TC843]HDD Password Security 043', 'ATA协议硬盘密码输错测试'))
def hdd_password_043():
    """
    Name:   ATA协议硬盘密码输错测试

    Steps:  1.设置硬盘密码
            2.POST阶段校验密码阶段，输入3次错误的硬盘密码
            3.检查启动菜单，SetUp下是否有该硬盘的启动项，安全菜单的硬盘密码，检查是否有该硬盘信息
            4.POST阶段校验密码阶段，输入2次错误的硬盘密码，在输入正确的硬盘密码
            5.检查启动菜单，SetUp下是否有该硬盘的启动项，安全菜单的硬盘密码，检查是否有该硬盘信息
            6.选择“安全擦除硬盘输入”，输入错误的硬盘管理员密码,选择“更改硬盘用户密码”，输入错误的硬盘管理员密码
              ,选择“禁用硬盘密码”，输入错误的硬盘管理员密码
            7.开机，进入setup的安全界面，进入硬盘密码页面,选择“安全擦除硬盘输入”，输入错误的硬盘管理员密码,选择“更改硬盘用户密码”，
              输入错误的硬盘管理员密码
            8.选择“禁用硬盘密码”，输入正确的硬盘管理员密码
            9.启用硬盘管理员密码
            10.选择“禁用硬盘密码”，输入错误的硬盘管理员密码
            11.开机，进入setup的安全界面，进入硬盘密码页面，选择“安全擦除硬盘输入”，输入错误的硬盘管理员密码,选择“更改硬盘用户密码”，
              输入错误的硬盘管理员密码
            12.选择“修改硬盘管理员密码”，输入正确的硬盘管理员密码按Enter键，光标定位到输入新密码时按ESC键退出
            13.选择“禁用硬盘密码”，输入错误的硬盘管理员密码
            14.重复步骤13两次
            15.删除硬盘密码

    Result: 2.会提示硬盘密码错误，有硬盘被锁定的提示。
            3.没有该硬盘的启动项
            4.密码正确
            5.有该硬盘的启动项
            6.累计输入错误3次后会在提示信息后倒计时3秒系统关机
            8.硬盘密码被清除
            10.会提示硬盘密码无效，但是不会出现3秒后关机
            13.会提示硬盘密码无效，但是不会出现3秒后关机
            14.累计输入错误3次后会在提示信息后倒计时3秒系统关机
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name, data), '输错三次密码，启动菜单仍有该启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2), '输错三次密码，硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(user, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name, data), '输错两次密码，第三次输入正确密码，启动菜单没有该启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED], 5)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.ERASE_NAME, 6)
        assert PwdLib.del_hdd_psw('12345789044',False,PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 6)
        assert PwdLib.set_hdd_admin(user, None, old_pw='1234567890', expect=PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 6)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.ERASE_NAME, 6)
        assert PwdLib.del_hdd_psw('12345789044',False,PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 6)
        assert PwdLib.set_hdd_admin(user, None, old_pw='1234567890', expect=PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 10)
        assert PwdLib.del_hdd_psw(user, True)
        assert PwdLib.set_hdd_admin(new_user, True)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 10)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.ERASE_NAME, 6)
        assert PwdLib.del_hdd_psw('12345789044',False,PwdLib.hdd_pw_invalid)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.CHANGE_USER_NAME, 6)
        assert PwdLib.set_hdd_admin(user, None, old_pw='1234567890', expect=PwdLib.hdd_pw_invalid)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CHANGE_ADMIN_NAME, 6)
        time.sleep(2)
        SetUpLib.send_data_enter(new_user)
        assert not SetUpLib.wait_message(PwdLib.hdd_pw_invalid, 2)
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DISABLE_PSW_NAME, 6)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_invalid)
        assert PwdLib.del_hdd_psw('1234567890', False, PwdLib.hdd_pw_limit)
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME],
                                    18)
        assert PwdLib.del_hdd_psw(new_user, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('844', '[TC844]HDD Password Security 044', 'ATA协议硬盘密码ESC跳过测试'))
def hdd_password_044():
    """
    Name:   ATA协议硬盘密码ESC跳过测试

    Steps:  1.设置硬盘密码
            2.POST阶段校验密码阶段，ESC跳过硬盘密码
            3.检查启动菜单，SetUp下是否有该硬盘的启动项，安全菜单的硬盘密码，检查是否有该硬盘信息
            4.删除硬盘密码

    Result: 2.会提示硬盘密码错误，有硬盘被锁定的提示。
            3.没有该硬盘的启动项
    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        init_sut()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'POST阶段没有提示输入硬盘密码'
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name, data), '跳过密码，启动菜单仍有该启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 2), '跳过密码，硬盘没有锁住'
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME],
                                    18)
        assert PwdLib.del_hdd_psw(user, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('845', '[TC845]HDD Password Security 045', 'ATA协议NVME硬盘密码校验测试'))
def hdd_password_045():
    """
    Name:   ATA协议NVME硬盘密码校验测试

    Steps:  1.设置用户密码
            2.关机，开机检查POST阶段是否校验密码
            3.SetUp下F10保存重启，检查POST阶段是否校验密码
            4.系统下重启，检查POST阶段是否校验密码

    Result: 2.POST阶段校验密码
            3/4.POST阶段校验密码

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    if not re.search('nvme', hdd_name, re.I):
        logging.info('没有ATA协议的NVME硬盘')
        return core.Status.Skip
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        init_sut()
        assert boot_to_setup(is_del=False) == [True, True], 'POST校验硬盘密码失败'
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'ATA协议NVMESetUp下F10重启，POST阶段没有校验密码'
        assert PwdLib.check_psw_post(user, '')
        assert SetUpLib.boot_to_boot_menu(reset=False)
        assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
        if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 10):
            logging.info('该硬盘可能没有安装系统,跳过后续测试')
            boot_to_setup()
            return core.Status.Skip
        assert BmcLib.ping_sut(), '进入硬盘系统失败'
        time.sleep(10)
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        for i in range(3):
            assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), 'ATA协议NVME系统下重启，POST阶段没有校验密码'
            assert PwdLib.check_psw_post(user, '')
            assert SetUpLib.boot_to_boot_menu(reset=False)
            assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
            assert BmcLib.ping_sut(), '进入硬盘系统失败'
            time.sleep(10)
            SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(user, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('846', '[TC846]HDD Password Security 046', 'ATA协议SATA硬盘密码校验测试'))
def hdd_password_046():
    """
    Name:   ATA协议SATA硬盘密码校验测试

    Steps:  1.设置用户密码
            2.关机，开机检查POST阶段是否校验密码
            3.SetUp下F10保存重启，检查POST阶段是否校验密码
            4.系统下重启，检查POST阶段是否校验密码,SetUp下硬盘状态

    Result: 2.POST阶段校验密码
            3.POST阶段不会校验密码
            4.POST阶段不会校验密码,SetUp下硬盘锁住

    """
    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    if not re.search('sata', hdd_name, re.I):
        logging.info('没有ATA协议的SATA硬盘')
        return core.Status.Skip
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        init_sut()
        assert boot_to_setup(is_del=False) == [True, True], 'POST校验硬盘密码失败'
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_boot_menu(reset=False)
        assert SetUpLib.select_boot_option(Key.DOWN, hdd_boot_name, 30, '')
        if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 10):
            logging.info('该硬盘可能没有安装系统,跳过后续测试')
            boot_to_setup()
            return core.Status.Skip
        assert BmcLib.ping_sut(), '进入硬盘系统失败'
        time.sleep(10)
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        assert SetUpLib.boot_to_boot_menu(reset=False), '系统下重启,POST校验密码'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '系统下重启，硬盘不是锁住状态'
        assert boot_to_setup(is_del=False)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(user, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('847', '[TC847]HDD Password Security 047', 'ATA协议硬盘密码更新BIOS'))
def hdd_password_047():
    """
    Name:   ATA协议硬盘密码更新BIOS

    Steps:  1.设置硬盘管理员密码
            2.SetUp下更新BIOS，检查硬盘密码
            3.Shell下更新BIOS，检查硬盘密码
            4.删除密码

    Result: 2/3.更新BIOS后，硬盘密码依然存在
    """

    if not get_hdd_msg('ata'):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name, hdd_boot_name = get_hdd_msg('ata')
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup()
        SetUpLib.default_save()
        assert boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(user, True)
        assert boot_to_setup(is_del=False)==[True,True]
        assert update_bios_setup()
        assert SetUpLib.wait_message(SutConfig.Psw.POST_HDD_MSG), '刷新BIOS后硬盘密码不存在'
        assert PwdLib.check_psw_post(user,'')
        data=SetUpLib.boot_to_boot_menu(True,False)
        assert re.search(hdd_name,data),'刷新BIOS后启动菜单没有该硬盘启动项'
        assert update_bios_shell()
        assert boot_to_setup(is_del=False)==[True,True],'刷新BIOS后硬盘密码不存在'
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name, SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(user, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('861', '[TC861]HDD Password Security 061', '多硬盘密码输错测试(两个NVME)'))
def hdd_password_061():
    """
    Name:   多硬盘密码输错测试(两个NVME)

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段两个硬盘密码都输错三次，检查启动菜单，SetUp下硬盘状态
            3.POST阶段第一个硬盘密码输错三次，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段第一个硬盘输入正确密码，第二个硬盘密码输错三次，检查启动菜单，SetUp下硬盘状态
            5.POST阶段两块硬盘都输入正确密码，检查启动菜单，SetUp下硬盘状态
            6.删除两块硬盘密码

    Result: 2.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
            3.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            4.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            5.启动菜单有两块硬盘信息，SetUp下两块硬盘都没有锁住
    """
    if not get_hdd_msg(types=['tcg', 'tcg']):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name1, hdd_name2, hdd_boot_name1, hdd_boot_name2 = get_hdd_msg(types=['tcg', 'tcg'])
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_another = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup_two()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name1, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name2, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin_another(admin_another, True)
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘密码输错三次,启动菜单仍有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘密码输错三次,启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘密码输错三次，启动菜单仍有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567980', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘输错密码三次，启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘输错密码三次,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('862', '[TC862]HDD Password Security 062', '多硬盘ESC跳过密码测试(两个NVME)'))
def hdd_password_062():
    """
    Name:   多硬盘ESC跳过密码测试(两个NVME)

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段两个硬盘都ESC跳过密码，检查启动菜单，SetUp下硬盘状态
            3.POST阶段ESC跳过第一个硬盘密码，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段第一个硬盘输入正确密码，ESC跳过第二个硬盘密码，检查启动菜单，SetUp下硬盘状态
            5.POST阶段两个硬盘都输入正确密码，检查启动菜单，SetUp下硬盘状态
            6.删除两块硬盘密码

    Result: 2.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
            3.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            4.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            5.启动菜单有两块硬盘信息，SetUp下两块硬盘都没有锁住
    """
    if not get_hdd_msg(types=['tcg', 'tcg']):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name1, hdd_name2, hdd_boot_name1, hdd_boot_name2 = get_hdd_msg(types=['tcg', 'tcg'])
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_another = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup_two()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name1, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name2, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin_another(admin_another, True)
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘跳过密码,启动菜单仍有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘跳过密码,启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘跳过密码,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘跳过密码,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘跳过密码，启动菜单仍有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘跳过密码,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘跳过密码，启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘跳过密码,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('863', '[TC863]HDD Password Security 063', '多硬盘密码输错测试(一个NVME，一个SATA)'))
def hdd_password_063():
    """
    Name:   多硬盘密码输错测试(一个NVME，一个SATA)

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段两个硬盘密码都输错三次，检查启动菜单，SetUp下硬盘状态
            3.POST阶段第一个硬盘密码输错三次，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段第一个硬盘输入正确密码，第二个硬盘密码输错三次，检查启动菜单，SetUp下硬盘状态
            5.POST阶段两块硬盘都输入正确密码，检查启动菜单，SetUp下硬盘状态
            6.删除两块硬盘密码

    Result: 2.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
            3.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            4.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            5.启动菜单有两块硬盘信息，SetUp下两块硬盘都没有锁住
    """
    if not get_hdd_msg(types=['tcg', 'ata']):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name1, hdd_name2, hdd_boot_name1, hdd_boot_name2 = get_hdd_msg(types=['tcg', 'ata'])
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_another = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup_two()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name1, SutConfig.Psw.ENABLE_HDD_NAME],
                                    18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name2, SutConfig.Psw.ENABLE_HDD_NAME],
                                    18)
        assert PwdLib.set_hdd_admin_another(admin_another, True)
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘密码输错三次,启动菜单仍有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘密码输错三次,启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘密码输错三次，启动菜单仍有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567980', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘输错密码三次，启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘输错密码三次,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('864', '[TC864]HDD Password Security 064', '多硬盘ESC跳过密码测试(一个NVME，一个SATA)'))
def hdd_password_064():
    """
    Name:   多硬盘ESC跳过密码测试(一个NVME，一个SATA)

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段两个硬盘都ESC跳过密码，检查启动菜单，SetUp下硬盘状态
            3.POST阶段ESC跳过第一个硬盘密码，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段第一个硬盘输入正确密码，ESC跳过第二个硬盘密码，检查启动菜单，SetUp下硬盘状态
            5.POST阶段两个硬盘都输入正确密码，检查启动菜单，SetUp下硬盘状态
            6.删除两块硬盘密码

    Result: 2.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
            3.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            4.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            5.启动菜单有两块硬盘信息，SetUp下两块硬盘都没有锁住
    """
    if not get_hdd_msg(types=['tcg', 'ata']):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name1, hdd_name2, hdd_boot_name1, hdd_boot_name2 = get_hdd_msg(types=['tcg', 'ata'])
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_another = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup_two()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1, SutConfig.Psw.ENABLE_HDD_NAME],
                                    18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2, SutConfig.Psw.ENABLE_HDD_NAME],
                                    18)
        assert PwdLib.set_hdd_admin_another(admin_another, True)
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘跳过密码,启动菜单仍有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘跳过密码,启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘跳过密码,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘跳过密码,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘跳过密码，启动菜单仍有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘跳过密码,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘跳过密码，启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘跳过密码,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('865', '[TC865]HDD Password Security 065', '多硬盘密码输错测试(两个SATA)'))
def hdd_password_065():
    """
    Name:   多硬盘密码输错测试(两个SATA)

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段两个硬盘密码都输错三次，检查启动菜单，SetUp下硬盘状态
            3.POST阶段第一个硬盘密码输错三次，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段第一个硬盘输入正确密码，第二个硬盘密码输错三次，检查启动菜单，SetUp下硬盘状态
            5.POST阶段两块硬盘都输入正确密码，检查启动菜单，SetUp下硬盘状态
            6.删除两块硬盘密码

    Result: 2.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
            3.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            4.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            5.启动菜单有两块硬盘信息，SetUp下两块硬盘都没有锁住
    """
    if not get_hdd_msg(types=['ata', 'ata']):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name1, hdd_name2, hdd_boot_name1, hdd_boot_name2 = get_hdd_msg(types=['ata', 'ata'])
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_another = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup_two()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name1, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name2, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin_another(admin_another, True)
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘密码输错三次,启动菜单仍有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘密码输错三次,启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_limit_post)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘密码输错三次，启动菜单仍有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘密码输错三次,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1234567980', PwdLib.hdd_pw_limit_post)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘输错密码三次，启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘输错密码三次,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('866', '[TC866]HDD Password Security 066', '多硬盘ESC跳过密码测试(两个SATA)'))
def hdd_password_066():
    """
    Name:   多硬盘ESC跳过密码测试(两个SATA)

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段两个硬盘都ESC跳过密码，检查启动菜单，SetUp下硬盘状态
            3.POST阶段ESC跳过第一个硬盘密码，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段第一个硬盘输入正确密码，ESC跳过第二个硬盘密码，检查启动菜单，SetUp下硬盘状态
            5.POST阶段两个硬盘都输入正确密码，检查启动菜单，SetUp下硬盘状态
            6.删除两块硬盘密码

    Result: 2.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
            3.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            4.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            5.启动菜单有两块硬盘信息，SetUp下两块硬盘都没有锁住
    """
    if not get_hdd_msg(types=['ata', 'ata']):
        logging.info('没有支持此项测试的硬盘')
        return core.Status.Skip
    hdd_name1, hdd_name2, hdd_boot_name1, hdd_boot_name2 = get_hdd_msg(types=['ata', 'ata'])
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_another = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert boot_to_setup_two()
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name1, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin(admin, True)
        assert SetUpLib.locate_menu(Key.DOWN,
                                    SutConfig.Psw.LOC_HDD_PSW + [hdd_name2, SutConfig.Psw.ENABLE_HDD_NAME], 18)
        assert PwdLib.set_hdd_admin_another(admin_another, True)
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘跳过密码,启动菜单仍有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘跳过密码,启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘跳过密码,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘跳过密码,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        assert SetUpLib.wait_message(hdd_name2)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert not re.search(hdd_boot_name1, data), '第一个硬盘跳过密码，启动菜单仍有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第一个硬盘跳过密码,SetUp下该硬盘没有锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post('1234567890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post('1235467890', PwdLib.hdd_pw_incorrect)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(key=Key.ESC, expect=PwdLib.hdd_pw_escape)
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert not re.search(hdd_boot_name2, data), '第二个硬盘跳过密码，启动菜单仍有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_MSG], 3), '第二个硬盘跳过密码,SetUp下该硬盘没有锁住'
        init_sut()
        assert SetUpLib.wait_message(hdd_name1)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, hdd_name2, timeout=30)
        assert PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        data = SetUpLib.boot_to_boot_menu(True, False)
        assert re.search(hdd_boot_name1, data), '第一个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert re.search(hdd_boot_name2, data), '第二个硬盘输入正确密码，启动菜单没有该硬盘启动项'
        assert SetUpLib.select_boot_option(Key.UP, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name1], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第一个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hdd_name2], 18)
        assert SetUpLib.verify_info([SutConfig.Psw.HDD_PSW_STATUS_INSTALLED, SutConfig.Psw.DISABLE_PSW_NAME],
                                    3), '第二个硬盘输入正确密码,SetUp下该硬盘仍锁住'
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.DISABLE_PSW_NAME], 18)
        assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
