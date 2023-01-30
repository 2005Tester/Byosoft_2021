# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *

# 硬盘顺序与设置硬盘密码时的顺序对应,每个硬盘系统对应
HDD_NAME_01 = SutConfig.Psw.HDD_PASSWORD_NAME_01
HDD_NAME_01_OS = SutConfig.Psw.HDD_NAME_01_OS

HDD_NAME_02 = SutConfig.Psw.HDD_PASSWORD_NAME_02
HDD_NAME_02_OS = SutConfig.Psw.HDD_NAME_02_OS


def _set_hdd_password(hddname, password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname, SutConfig.Psw.SET_HDD_PSW_OPTION], 18)
    assert PwdLib.set_hdd_admin(password, True)
    return True


def _set_hdd_password_two(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_01,
                                                                       SutConfig.Psw.SET_HDD_PSW_OPTION], 18)
    assert PwdLib.set_hdd_admin(password[0], True)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.SET_HDD_PSW_OPTION], 18)
    assert PwdLib.set_hdd_admin_another(password[1], True)
    time.sleep(1)
    return True


def _del_hdd_password(hddname, password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname, SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
    assert PwdLib.del_hdd_psw(password, True)
    return True


def _del_hdd_password_two(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_01,
                                                                       SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
    assert PwdLib.del_hdd_psw(password[0], True)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.HDD_PASSWORD_NAME_02, SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
    assert PwdLib.del_hdd_psw(password[1], True)
    return True


def _boot_to_setup(is_del=True, password='admin'):
    if password == 'admin':
        password = PwdLib.HDD_PW.ADMIN if PwdLib.HDD_PW.ADMIN else ''
    elif password == 'admin_another':
        password = PwdLib.HDD_PW.ADMIN_ANOTHER if PwdLib.HDD_PW.ADMIN_ANOTHER else ''
    else:
        password = PwdLib.HDD_PW.ADMIN if PwdLib.HDD_PW.ADMIN else ''
    BmcLib.init_sut()
    logging.info("SetUpLib: Booting to setup")
    try_counts = 3
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        result = SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE,
                                                SutConfig.Psw.LOGIN_HDD_PSW_PROMPT, password)
        if result == [True, True]:
            if is_del:
                SetUpLib.enter_menu_change_value(Key.DOWN,
                                                 SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_01], 18)
                if SetUpLib.wait_message(SutConfig.Psw.DEL_HDD_PSW_OPTION, 3):
                    SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DEL_HDD_PSW_OPTION, 10)
                    PwdLib.del_hdd_psw(password, True)
                SetUpLib.enter_menu_change_value(Key.DOWN,
                                                 SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_02], 18)
                if SetUpLib.wait_message(SutConfig.Psw.DEL_HDD_PSW_OPTION, 3):
                    SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.DEL_HDD_PSW_OPTION, 10)
                    PwdLib.del_hdd_psw(password, True)
                SetUpLib.back_to_setup_toppage()
                return True
            else:
                return [True, True]
        elif result == True:
            return True
        else:
            BmcLib.init_sut()
            try_counts -= 1
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


def _boot_to_setup_two(is_del=True):
    if PwdLib.HDD_PW.ADMIN and PwdLib.HDD_PW.ADMIN_ANOTHER:
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT):
            assert _boot_to_setup(is_del=is_del)
            return True
        PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN, '')
        if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT):
            assert _boot_to_setup(is_del=is_del)
            return True
        PwdLib.check_psw_post(PwdLib.HDD_PW.ADMIN_ANOTHER, '')
        assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
        if is_del:
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_01,
                                                                               SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN, True)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [SutConfig.Psw.HDD_PASSWORD_NAME_02,
                                                                               SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
            assert PwdLib.del_hdd_psw(PwdLib.HDD_PW.ADMIN_ANOTHER, True)
        return True
    elif PwdLib.HDD_PW.ADMIN is not None and PwdLib.HDD_PW.ADMIN_ANOTHER is None:
        assert _boot_to_setup(is_del, 'admin')
        return True
    elif PwdLib.HDD_PW.ADMIN is None and PwdLib.HDD_PW.ADMIN_ANOTHER is not None:
        assert _boot_to_setup(is_del, 'admin_another')
        return True
    else:
        assert _boot_to_setup(is_del)
        return True


# 设置硬盘密码长度小于最少字符数，大于最大字符，设置密码时两次输入不一致，
# 只有数字，只有字母，只有特殊符号，数字和特殊符号，字母和特殊符号设置失败测试
def hdd_password_001():
    psw_list = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.HDD_PW.MAX + 2),
                PwdLib.gen_pw(digit=8, upper=0, lower=0, symbol=0),
                PwdLib.gen_pw(digit=0, upper=8, lower=0, symbol=0),
                PwdLib.gen_pw(digit=0, upper=0, lower=8, symbol=8),
                PwdLib.gen_pw(digit=4, upper=0, lower=0, symbol=4),
                PwdLib.gen_pw(digit=0, upper=4, lower=0, symbol=4),
                PwdLib.gen_pw(digit=0, upper=0, lower=4, symbol=4),
                ]
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    assert _boot_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname, SutConfig.Psw.SET_HDD_PSW_OPTION], 18)
    logging.info('设置密码时两次输入不一致测试..........')
    assert PwdLib.set_hdd_admin(psw_list[0], False, expect=PwdLib.hdd_pw_not_same, confirm_pw=psw_list[1])
    logging.info('硬盘密码长度小于最少字符数测试,符合复杂度........')
    assert PwdLib.set_hdd_admin(psw_list[2], False, expect=PwdLib.hdd_pw_short)
    logging.info('硬盘密码长度大于最大字符数测试,符合复杂度...........')
    assert PwdLib.set_hdd_admin(psw_list[3], False, expect=PwdLib.hdd_pw_long)
    logging.info('硬盘密码复杂读不符合要求，长度符合要求...........')
    for psw in psw_list[4:]:
        assert PwdLib.set_hdd_admin(psw, False, expect=PwdLib.hdd_pw_simple)
    return True


# 设置硬盘密码长度等于最小字符数，设置成功测试
def hdd_password_002():
    password = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.HDD_PW.MIN)
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    assert _boot_to_setup()
    logging.info('硬盘密码长度最小，复杂度最小测试..............')
    assert _set_hdd_password(hddname, password)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post('hdd111111', PwdLib.hdd_pw_incorrect), '输入错误密码，没有提示密码错误'
    assert PwdLib.check_psw_post(password, '')
    assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 250, SutConfig.Msg.POST_MESSAGE)
    assert _del_hdd_password(hddname, password)
    return True


# 设置硬盘密码长度等于最小字符数，最大复杂度，设置成功测试
def hdd_password_003():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.HDD_PW.MIN)
    assert _boot_to_setup()
    logging.info('硬盘密码长度最小，复杂度最大测试..............')
    assert _set_hdd_password(hddname, password)
    assert _boot_to_setup(is_del=False) == [True, True]
    assert _del_hdd_password(hddname, password)
    return True


# 设置硬盘密码长度大于最小字符数，小于最大字符数，设置成功测试
def hdd_password_004():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _boot_to_setup()
    logging.info('硬盘密码大于最小字符数，小于最大字符数测试..............')
    assert _set_hdd_password(hddname, password)
    assert _boot_to_setup(is_del=False) == [True, True]
    assert _del_hdd_password(hddname, password)
    return True


# 设置硬盘密码长度等于最大字符数，复杂度最小，设置成功测试
def hdd_password_005():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=3, upper=0, lower=3, symbol=3, total=PwdLib.HDD_PW.MAX)
    assert _boot_to_setup()
    logging.info('设置硬盘密码长度等于最大字符数，复杂度最小测试..............')
    assert _set_hdd_password(hddname, password)
    assert _boot_to_setup(is_del=False) == [True, True]
    assert _del_hdd_password(hddname, password)
    return True


# 设置硬盘密码长度等于最大字符数，复杂度最大，设置成功测试
def hdd_password_006():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.HDD_PW.MAX)
    assert _boot_to_setup()
    logging.info('硬盘密码等于长度最大，复杂度最大测试..............')
    assert _set_hdd_password(hddname, password)
    assert _boot_to_setup(is_del=False) == [True, True]
    assert _del_hdd_password(hddname, password)
    return True


# 禁用硬盘密码测试
def hdd_password_007():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DEL_HDD_PSW_OPTION], 3)
    assert PwdLib.del_hdd_psw('hdd111111', False, PwdLib.hdd_pw_invalid), '禁用密码时输入错误的密码没有提示密码无效'
    assert PwdLib.del_hdd_psw(password, True)
    return True


# 修改硬盘密码测试，修改为最小长度，最小复杂度，修改成功测试
def hdd_password_008():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_psw = PwdLib.gen_pw(digit=1, upper=1, lower=0, symbol=1, total=PwdLib.HDD_PW.MIN)
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password)
    assert PwdLib.set_hdd_admin(new_psw, True)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post(password, PwdLib.hdd_pw_incorrect), '输入修改前的密码，没有提示密码错误'
    assert PwdLib.check_psw_post(new_psw, '')
    assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 250, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname, SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
    assert PwdLib.del_hdd_psw(password, False, PwdLib.hdd_pw_invalid)
    assert PwdLib.del_hdd_psw(new_psw, True)
    return True


# 修改硬盘密码测试，修改为最大长度，最大复杂度，修改成功测试
def hdd_password_009():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_psw = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.HDD_PW.MAX)
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password)
    assert PwdLib.set_hdd_admin(new_psw, True)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post(password, PwdLib.hdd_pw_incorrect), '输入修改前的密码，没有提示密码错误'
    assert PwdLib.check_psw_post(new_psw, '')
    assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 250, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname, SutConfig.Psw.DEL_HDD_PSW_OPTION], 18)
    assert PwdLib.del_hdd_psw(password, False, PwdLib.hdd_pw_invalid)
    assert PwdLib.del_hdd_psw(new_psw, True)
    return True


# 修改硬盘密码测试，修改为符合长度要求，不符合复杂度要求；符合复杂度要求，不符合长度要求；新密码和确认密码不同，修改失败测试
def hdd_password_010():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    password = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=10, upper=0, lower=0, symbol=0),
                PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1), ]
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password[0])
    logging.info('修改硬盘密码为符合长度要求，不符合复杂度要求测试..................')
    assert PwdLib.set_hdd_admin(password[1], False, expect=PwdLib.hdd_pw_simple)
    logging.info('修改硬盘密码为符合复杂度要求，不符合长度要求测试..................')
    assert PwdLib.set_hdd_admin(password[2], False, expect=PwdLib.hdd_pw_short)
    logging.info('修改硬盘密码新密码和确认密码不同，修改失败测试..................')
    assert PwdLib.set_hdd_admin(password[0], False, expect=PwdLib.hdd_pw_not_same, confirm_pw='hdd111111')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DEL_HDD_PSW_OPTION], 3)
    assert PwdLib.del_hdd_psw(password[0], True)
    return True


# 设置硬盘密码进入系统测试
def hdd_password_011():
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(2)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('<Legacy> *Boot Mod', 5):
        logging.info('当前启动模式为Legacy')
        if HDD_NAME_01_OS == SutConfig.Msg.LEGACY_HDD_BOOT_NAME:
            hddname = HDD_NAME_01
            hddos = HDD_NAME_01_OS
        else:
            hddname = HDD_NAME_02
            hddos = HDD_NAME_02_OS
    else:
        logging.info('当前启动模式为UEFI')
        if HDD_NAME_01_OS == SutConfig.Msg.UEFI_HDD_BOOT_NAME:
            hddname = HDD_NAME_01
            hddos = HDD_NAME_01_OS
        else:
            hddname = HDD_NAME_02
            hddos = HDD_NAME_02_OS
    assert _set_hdd_password(hddname, password)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post(password, '')
    assert SetUpLib.boot_to_boot_menu(False, False)
    assert SetUpLib.select_boot_option(Key.DOWN, hddos, 30, '')
    assert BmcLib.ping_sut(), '第一次没有进入系统'
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post(password, '')
    assert SetUpLib.boot_to_boot_menu(False, False)
    assert SetUpLib.select_boot_option(Key.DOWN, hddos, 30, '')
    assert BmcLib.ping_sut(), '第二次没有进入系统'
    assert _boot_to_setup(is_del=False)
    assert _del_hdd_password(hddname, password)
    return True


# 硬盘密码输错测试
def hdd_password_012():
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    hddos = SutConfig.Psw.HDD_NAME_01_OS
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post('hdd12123121', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('hdd12123121', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('hdd@111111', PwdLib.hdd_pw_limit_post)
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos, data), '密码输错三次，启动项仍有硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('输错三次硬盘密码进入setup，无法设置该硬盘的硬盘密码')
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post('hdd111111', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('hdd111111', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post(password, '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddos, data), '密码输错2次后输入正确密码，启动项没有硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert _del_hdd_password(hddname, password)
    return True


# 修改硬盘密码,输入错误密码3次,硬盘锁定
def hdd_password_013():
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.wait_message(PwdLib.hdd_pw_enter_old, 3):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DEL_HDD_PSW_OPTION], 5)
        assert PwdLib.del_hdd_psw(password, True)
        return True
    SetUpLib.send_key(Key.ESC)
    assert PwdLib.set_hdd_admin(password, None, 'hdd122121', PwdLib.hdd_pw_invalid)
    assert PwdLib.set_hdd_admin(password, None, 'hdd122121', PwdLib.hdd_pw_invalid)
    assert PwdLib.set_hdd_admin(password, None, 'hdd122121', PwdLib.hdd_pw_limit)
    assert _boot_to_setup()
    return True


# 硬盘密码输入时按ESC测试
def hdd_password_014():
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    hddname = SutConfig.Psw.HDD_PASSWORD_NAME_01
    hddos = SutConfig.Psw.HDD_NAME_01_OS
    assert _boot_to_setup()
    assert _set_hdd_password(hddname, password)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    assert PwdLib.check_psw_post('12312312312', PwdLib.hdd_pw_escape, key=Key.ESC)
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos, data), '输入密码时按ESC，启动项仍有硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    assert _boot_to_setup(is_del=False)
    assert _del_hdd_password(hddname, password)
    return True


# 多硬盘密码测试
def hdd_password_015():
    password = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    hddname1 = SutConfig.Psw.HDD_PASSWORD_NAME_01
    hddname2 = SutConfig.Psw.HDD_PASSWORD_NAME_02
    assert _boot_to_setup()
    assert _set_hdd_password_two(password)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post(password[1], PwdLib.hdd_pw_incorrect), '输入其他硬盘密码，没有提示密码错误'
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    logging.info('输入第一个硬盘密码，成功进入第一个硬盘，要求输入第二个硬盘密码')
    assert PwdLib.check_psw_post(password[0], PwdLib.hdd_pw_incorrect), '输入其他硬盘密码，没有提示密码错误'
    assert PwdLib.check_psw_post(password[1], '')
    assert SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 250, SutConfig.Msg.POST_MESSAGE)
    assert _del_hdd_password_two(password)
    return True


# 多硬盘密码输错测试
def hdd_password_016():
    password = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    hddname1 = SutConfig.Psw.HDD_PASSWORD_NAME_01
    hddname2 = SutConfig.Psw.HDD_PASSWORD_NAME_02
    hddos1 = SutConfig.Psw.HDD_NAME_01_OS
    hddos2 = SutConfig.Psw.HDD_NAME_02_OS
    assert _boot_to_setup_two()
    assert _set_hdd_password_two(password)
    # 第一个硬盘密码输错测试
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    logging.info('第一个硬盘密码输错测试.............................................................')
    assert PwdLib.check_psw_post('11111111', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('11111111', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('11111111', PwdLib.hdd_pw_limit_post)
    assert SetUpLib.wait_message(hddname2)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos1, data), '第一个硬盘密码输错三次，启动项仍有硬盘'
    assert re.search(hddos2, data), '第二个硬盘输入正确的密码，启动项中没有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname1], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第一个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [hddname2], 5, 2)
    assert SetUpLib.verify_info([SutConfig.Psw.DEL_HDD_PSW_OPTION], 3)
    logging.info('第二个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    # 第二个硬盘密码输错测试
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    logging.info('第二个硬盘密码输错测试.......................................................')
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_limit_post)
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos2, data), '第二个硬盘密码输错三次，启动项仍有硬盘'
    assert re.search(hddos1, data), '第一个硬盘输入正确的密码，启动项中没有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname2], 18)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第二个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [hddname1], 5)
    assert SetUpLib.verify_info([SutConfig.Psw.DEL_HDD_PSW_OPTION], 3)
    logging.info('第一个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    # 两个硬盘密码输错测试
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    logging.info('两个硬盘密码输错测试.......................................................')
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_limit_post)
    assert SetUpLib.wait_message(hddname2)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('13212123', PwdLib.hdd_pw_limit_post)
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos1, data), '第一个硬盘密码输错三次，启动项中仍有该硬盘'
    assert not re.search(hddos2, data), '第二个硬盘密码输错三次，启动项中仍有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname1], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第一个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [hddname2], 5)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 3)
    logging.info('第二个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post('121322112', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('121322112', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    logging.info('第三次输入第一个硬盘密码，成功进入第一个硬盘，要求输入第二个硬盘密码')
    assert PwdLib.check_psw_post('121322112', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('121322112', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddos1, data) and re.search(hddos2, data)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert _del_hdd_password_two(password)
    return True


# 多硬盘密码输入时按ESC测试
def hdd_password_017():
    password = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    hddname1 = SutConfig.Psw.HDD_PASSWORD_NAME_01
    hddname2 = SutConfig.Psw.HDD_PASSWORD_NAME_02
    hddos1 = SutConfig.Psw.HDD_NAME_01_OS
    hddos2 = SutConfig.Psw.HDD_NAME_02_OS
    assert _boot_to_setup_two()
    assert _set_hdd_password_two(password)
    # 第一个硬盘密码输入时按ESC测试
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    time.sleep(2)
    logging.info('第一个硬盘密码输入时按ESC测试.............................................................')
    assert PwdLib.check_psw_post('12132123', PwdLib.hdd_pw_escape, key=Key.ESC)
    logging.info('第一个硬盘密码输入时按ESC，提示驱动器处于锁定状态')
    assert SetUpLib.wait_message(hddname2)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos1, data), '第一个硬盘密码输入时按ESC，启动项仍有硬盘'
    assert re.search(hddos2, data), '第二个硬盘输入正确的密码，启动项中没有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname1], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第一个硬盘输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [hddname2], 18)
    assert SetUpLib.verify_info([SutConfig.Psw.DEL_HDD_PSW_OPTION], 2)
    logging.info('第二个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    # 第二个硬盘密码输入时按ESC测试
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    logging.info('第二个硬盘密码输入时按ESC测试.......................................................')
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    assert PwdLib.check_psw_post('126544554', PwdLib.hdd_pw_escape, key=Key.ESC)
    logging.info('第二个硬盘输入时按ESC提示驱动器处于锁定状态')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddos1, data), '第一个硬盘输入正确的密码，启动项中没有该硬盘'
    assert not re.search(hddos2, data), '第二个硬盘密码输入时按ESC，启动项仍有硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname2], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第二个硬盘输错输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [hddname1], 5)
    assert SetUpLib.verify_info([SutConfig.Psw.DEL_HDD_PSW_OPTION], 3)
    logging.info('第一个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    # 两个硬盘密码输入时按ESC测试
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    logging.info('两个硬盘密码输入按ESC测试.......................................................')
    assert PwdLib.check_psw_post('111111121', PwdLib.hdd_pw_escape, key=Key.ESC)
    logging.info('第一个硬盘输入时按ESC，提示驱动器处于锁定状态')
    assert SetUpLib.wait_message(hddname2, 30)
    assert PwdLib.check_psw_post('111111121', PwdLib.hdd_pw_escape, key=Key.ESC)
    logging.info('第二个硬盘密码输入时按ESC提示驱动器处于锁定状态')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddos1, data), '第一个硬盘密码输入时按ESC，启动项中仍有该硬盘'
    assert not re.search(hddos2, data), '第二个硬盘密码输入时按ESC，启动项中仍有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.LOC_HDD_PSW + [hddname1], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第一个硬盘密码输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [hddname2], 10)
    assert SetUpLib.verify_info([SutConfig.Psw.HDD_LOCK_STATUS], 2)
    logging.info('第二个硬盘密码输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddos1, data) and re.search(hddos2, data)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
    assert _del_hdd_password_two(password)
    return True


# 多硬盘密码进入系统测试
def hdd_password_018():
    password = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    hddname1 = SutConfig.Psw.HDD_PASSWORD_NAME_01
    hddname2 = SutConfig.Psw.HDD_PASSWORD_NAME_02
    hddos1 = SutConfig.Psw.HDD_NAME_01_OS
    hddos2 = SutConfig.Psw.HDD_NAME_02_OS

    assert _boot_to_setup_two()
    assert _set_hdd_password_two(password)
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post('111111111', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('111111111', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('111111111', PwdLib.hdd_pw_limit_post)
    logging.info('密码第三次输错,第一个硬盘密码输错三次，硬盘被锁定')
    assert SetUpLib.wait_message(hddname2)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert not re.search(hddname1, data), '第一个硬盘密码输错三次，启动项仍有硬盘'
    assert re.search(hddname2, data), '第二个硬盘输入正确的密码，启动项中没有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, hddname2, 30, '')
    logging.info('第二个硬盘第一次成功进入系统')
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    assert PwdLib.check_psw_post('12121212', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('12121212', PwdLib.hdd_pw_incorrect)
    assert PwdLib.check_psw_post('12121212', PwdLib.hdd_pw_limit_post)
    logging.info('密码第三次输错,第二个硬盘密码输错三次，硬盘被锁定')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddos1, data), '第一个硬盘输入正确的密码，启动项中没有该硬盘'
    assert not re.search(hddos2, data), '第二个硬盘密码输错三次，启动项仍有硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, hddname1, 30, '')
    logging.info('第一个硬盘第一次成功进入系统')
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddname1, data), '第一个硬盘输入正确的密码，启动项中没有该硬盘'
    assert re.search(hddname2, data), '第二个硬盘输入正确的密码，启动项中没有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, hddos1, 30, '')
    logging.info('第一个硬盘第二次成功进入系统')
    BmcLib.init_sut()
    assert SetUpLib.wait_message(hddname1)
    assert PwdLib.check_psw_post(password[0], hddname2, 60)
    assert PwdLib.check_psw_post(password[1], '')
    data = SetUpLib.boot_to_boot_menu(True, False)
    assert re.search(hddname1, data), '第一个硬盘输入正确的密码，启动项中没有该硬盘'
    assert re.search(hddname2, data), '第二个硬盘输入正确的密码，启动项中没有该硬盘'
    assert SetUpLib.select_boot_option(Key.DOWN, hddos2, 30, '')
    logging.info('第二个硬盘第二次成功进入系统')
    assert _boot_to_setup_two(is_del=False)
    assert _del_hdd_password_two(password)
    return True


def set_hash_type(type):
    assert SetUpLib.boot_to_setup()
    if type == 'type1':
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_HDD_HASH_TYPE1, 18)
    elif type == 'type2':
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_HDD_HASH_TYPE2, 18)
    else:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_HDD_HASH_TYPE1, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True
