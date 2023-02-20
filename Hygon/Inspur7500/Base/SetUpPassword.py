# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *


def _go_to_setup(password=None, is_del=True):
    if password is None:
        password = PwdLib.PW.ADMIN if PwdLib.PW.ADMIN else PwdLib.PW.DEFAULT_PW
        password = password if password else ''
    logging.info("SetUpLib: Booting to setup")
    if not BmcLib.init_sut():
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    try_counts = 3
    while try_counts:
        BmcLib.enable_serial_normal()
        logging.info("Waiting for Hotkey message found...")
        result = SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE,
                                                SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, password)
        if result == [True, True]:
            logging.info("SetUpLib: Boot to setup main page successfully,with password")
            if is_del:
                SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
                PwdLib.del_admin(password, True)
            return [True, True]
        elif result == True:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True
        else:
            BmcLib.power_cycle()
            try_counts -= 1
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


# 设置密码测试，未设置管理员密码直接设置用户密码，设置失败测试
def password_security_001():
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_USER_PSW, 8)
    if not re.search(f'{str(PwdLib.PW.MIN)}\s*to\s*{str(PwdLib.PW.MAX)}', SetUpLib.help_msg):
        min = re.findall('(\d+)\s*to\s*\d+', SetUpLib.help_msg)[0] if re.findall('(\d+)\s*to\s*\d+',
                                                                                 SetUpLib.help_msg) else None
        max = re.findall('\d+\s*to\s*(\d+)', SetUpLib.help_msg)[0] if re.findall('\d+\s*to\s*(\d+)',
                                                                                 SetUpLib.help_msg) else None
        if min and min in ['6', '8']:
            PwdLib.PW.MIN = int(min)
        if max and max in ['20', '32']:
            PwdLib.PW.MAX = int(max)
    assert PwdLib.set_user(user, False, expect=PwdLib.pw_user_only)
    return True


# 设置密码长度测试，密码长度小于最少字符数，修改失败测试
def password_security_002():
    admin = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1)
    user = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1)
    password = PwdLib.gen_pw(digit=2, upper=2, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码长度测试')
    assert PwdLib.set_admin(admin, False, expect=PwdLib.pw_short)
    logging.info('用户密码长度测试')
    assert PwdLib.set_admin(password, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 5)
    assert PwdLib.set_user(user, False, expect=PwdLib.pw_short)
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 5)
    assert PwdLib.del_admin(password, True)
    return True


# 设置密码长度测试，密码长度等于最少字符数，修改成功测试
def password_security_003():
    admin = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.PW.MIN)
    user = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.PW.MIN)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码长度测试')
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    assert PwdLib.set_user(user, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post('1111111111', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试
def password_security_004():
    admin = PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4)
    user = PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=4)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码长度测试')
    assert PwdLib.set_admin(admin, True), '设置管理员密码长度大于最少字符数，小于最大字符数失败'
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    assert PwdLib.set_user(user, True), '设置用户密码长度大于最少字符数，小于最大字符数失败'
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post('1111111111', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 设置密码长度测试，密码长度最大字符数，修改成功测试
def password_security_005():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.PW.MAX)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.PW.MAX)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码长度测试')
    assert PwdLib.set_admin(admin, True), '设置管理员密码长度为最大字符数失败'
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    assert PwdLib.set_user(user, True), '设置用户密码长度为最大字符数失败'
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post('123456787', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 设置密码长度测试，密码长度超出最大字符数，修改失败测试
def password_security_006():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.PW.MAX + 2)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3, total=PwdLib.PW.MAX + 2)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码长度测试')
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码长度测试')
    assert PwdLib.set_user(user, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(admin[:PwdLib.PW.MAX], SutConfig.Msg.PAGE_MAIN, 100)
    logging.info('设置密码长度超过最大字符数，密码仍为最大字符数')
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin[:PwdLib.PW.MAX], True)
    return True


# 设置密码字符类型测试，只有1种字符类型密码测试
def password_security_007():
    passwords = [PwdLib.gen_pw(digit=10, upper=0, lower=0, symbol=0),
                 PwdLib.gen_pw(digit=0, upper=10, lower=0, symbol=0),
                 PwdLib.gen_pw(digit=0, upper=0, lower=10, symbol=0),
                 PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=10),
                 ]
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)

    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        assert PwdLib.set_admin(password, False, expect=PwdLib.pw_simple)
    assert PwdLib.set_admin(admin, True)
    logging.info('管理员密码设置成功，开始用户密码字符类型测试')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        assert PwdLib.set_user(password, False, expect=PwdLib.pw_simple)
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    assert PwdLib.del_admin(admin, True)
    return True


# 设置密码字符类型测试，2种字符类型密码测试
def password_security_008():
    passwords = [PwdLib.gen_pw(digit=5, upper=5, lower=0, symbol=0),
                 PwdLib.gen_pw(digit=5, upper=0, lower=5, symbol=0),
                 PwdLib.gen_pw(digit=5, upper=0, lower=0, symbol=5),
                 PwdLib.gen_pw(digit=0, upper=5, lower=5, symbol=0),
                 PwdLib.gen_pw(digit=0, upper=5, lower=0, symbol=5),
                 PwdLib.gen_pw(digit=0, upper=0, lower=5, symbol=5)]
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        assert PwdLib.set_admin(password, False, expect=PwdLib.pw_simple)
    assert PwdLib.set_admin(admin, True)
    logging.info('管理员密码设置成功，开始用户密码字符类型测试')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        assert PwdLib.set_user(password, False, expect=PwdLib.pw_simple)

    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    assert PwdLib.del_admin(admin, True)
    return True


# 设置密码字符类型测试，3种字符类型密码测试
def password_security_009():
    passwords = [PwdLib.gen_pw(digit=4, upper=4, lower=4, symbol=0),
                 PwdLib.gen_pw(digit=4, upper=4, lower=0, symbol=4),
                 PwdLib.gen_pw(digit=4, upper=0, lower=4, symbol=4),
                 PwdLib.gen_pw(digit=0, upper=4, lower=4, symbol=4)]
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码字符类型测试')
    for password in passwords:
        assert PwdLib.set_admin(password, False, expect=PwdLib.pw_simple)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    for password in passwords:
        assert PwdLib.set_user(password, False, expect=PwdLib.pw_simple)
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    assert PwdLib.del_admin(admin, True)
    return True


# 设置密码字符类型测试，4种字符类型密码测试
def password_security_010():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码字符类型测试')
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码字符类型测试')
    assert PwdLib.set_user(user, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post('12346549847', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post('123465494156', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 输入错误密码3次内，提示报错，并可以再次输入测试；输错3次后不允许在输入密码测试；输入错误密码超出阈值测试
def password_security_011():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try_counts = SutConfig.Psw.TRY_COUNTS
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    for i in range(0, try_counts):
        assert PwdLib.check_psw_post('123456789', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post('123456879', PwdLib.pw_lock)
    logging.info(f'密码第{try_counts + 1}次输错，屏幕被锁定')
    assert _go_to_setup(admin, is_del=False)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 输入错误密码次数测试，阈值内连续输入错误密码后输入正确密码测试
def password_security_012():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try_counts = SutConfig.Psw.TRY_COUNTS
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    for i in range(0, try_counts):
        assert PwdLib.check_psw_post('1234567890', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 输入错误密码次数测试，超出阈值锁定输入界面，重启后不影响下一次登录
def password_security_013():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try_counts = SutConfig.Psw.TRY_COUNTS
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    for i in range(0, try_counts):
        assert PwdLib.check_psw_post('1234567890', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post('1234567890', PwdLib.pw_lock)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 输入错误密码等待时间测试，超出阈值锁定时间测试,锁定时间结束，输入正确密码可以进入
def password_security_014():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try_counts = SutConfig.Psw.TRY_COUNTS
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                            [SutConfig.Psw.LOC_LOCK_OPTION[0], {SutConfig.Psw.LOC_LOCK_OPTION[1]: 60}],
                                            10, save=True)
    assert _go_to_setup(admin, is_del=False)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    for i in range(0, try_counts):
        assert PwdLib.set_admin(new_admin, None, '1234657890', expect=PwdLib.pw_incorrect)
    assert PwdLib.set_admin(new_admin, None, '1234657890', expect=PwdLib.pw_lock_60)
    time.sleep(65)
    assert PwdLib.set_admin(new_admin, None, '123456789', PwdLib.pw_incorrect)
    logging.info('锁定时间结束后，可以继续输入密码')
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    for i in range(0, try_counts):
        assert PwdLib.check_psw_post('1234567890', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post('123456789', PwdLib.pw_lock_60)
    time.sleep(67)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    logging.info('锁定时间结束，输入正确密码成功进入setup')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                            [SutConfig.Psw.LOC_LOCK_OPTION[0], {SutConfig.Psw.LOC_LOCK_OPTION[1]: 180}],
                                            10, save=True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    for i in range(0, try_counts):
        assert PwdLib.check_psw_post('123456789', PwdLib.pw_invalid)
    assert PwdLib.check_psw_post('123456798', PwdLib.pw_lock_180)
    logging.info(f'密码输错{try_counts + 1}次，需等待180秒')
    time.sleep(190)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    for i in range(0, try_counts):
        assert PwdLib.set_admin(new_admin, None, '123456789', PwdLib.pw_incorrect)
    assert PwdLib.set_admin(new_admin, None, '123456789', PwdLib.pw_lock_180)
    logging.info(f'密码第{try_counts + 1}次输错，需等待180秒')
    time.sleep(190)
    assert PwdLib.del_admin(admin, True)
    return True


# 输入用户密码进入setup测试，进入setup不可以删除用户密码
def password_security_015():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    count = 0
    wrong_msg = []
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(user, SutConfig.Msg.PAGE_MAIN, 100)
    time.sleep(2)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message('User Login Type.*User', 5, readline=True):
        logging.info('用户密码进入SetUp，用户登陆类型显示普通用户')
    else:
        stylelog.fail('用户密码进入SetUp，用户登录类型不是普通用户')
        wrong_msg.append('用户密码进入SetUp，用户登录类型不是普通用户')
        count += 1
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SEL_LANG], 8):
        logging.info('用户密码进入SetUp，不能更改语言')
    else:
        stylelog.fail('用户密码进入SetUp，可以更改语言')
        wrong_msg.append('用户密码进入SetUp，可以更改语言')
        count += 1
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.SERVER_CONFIG], 8):
        logging.info('用户密码进入SetUp,不能进入服务管理')
    else:
        stylelog.fail('用户密码进入SetUp,可以进入服务管理')
        wrong_msg.append('用户密码进入SetUp,可以进入服务管理')
        count += 1
    assert SetUpLib.boot_to_page(SutConfig.Msg.SHUTDOWN_SYSTEM)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Msg.BIOS_UPDATE], 3):
        logging.info('用户密码进入SetUp,不能更改BIOS固件更新参数')
    else:
        stylelog.fail('用户密码进入SetUp,可以更改BIOS固件更新参数')
        wrong_msg.append('用户密码进入SetUp,可以更改BIOS固件更新参数')
        count += 1
    if not SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT):
        logging.info('用户密码进入SetUp，不能更改用户等待时间')
    else:
        stylelog.fail('用户密码进入SetUp，可以更改用户等待时间')
        wrong_msg.append('用户密码进入SetUp，可以更改用户等待时间')
        count += 1
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
    assert PwdLib.del_user(user, False, PwdLib.pw_user_del)
    logging.info('用户密码进入setup，用户权限无法删除用户密码')
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


# 输入用户密码进入setup测试，进入setup可以修改用户密码
def password_security_016():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    if not PwdLib.PW.ADMIN:
        assert _go_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 18)
        assert PwdLib.set_admin(admin, True)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        assert PwdLib.set_user(user, True)
    assert _go_to_setup(PwdLib.PW.USER, is_del=False)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
    assert PwdLib.set_user(new_user, True, PwdLib.PW.USER)
    logging.info('用户密码进入setup，成功修改用户密码')
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(PwdLib.PW.USER, SutConfig.Msg.PAGE_MAIN, 100)
    return True


# 密码不能明文显示，任意密码用*代替字符测试
def password_security_017():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    if not PwdLib.PW.ADMIN:
        assert _go_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 18)
        assert PwdLib.set_admin(admin, True)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        assert PwdLib.set_user(user, True)

    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)

    SetUpLib.send_data(PwdLib.PW.ADMIN)
    data = SetUpLib.get_data(2, Key.ENTER)
    if '*' * len(PwdLib.PW.ADMIN) in data and PwdLib.PW.ADMIN not in data:
        logging.info('密码不是明文显示，而是用*代替')
        return True
    else:
        return


# 密码修改验证旧密码测试，输入错误旧密码，不能修改密码
def password_security_018():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    if not PwdLib.PW.ADMIN:
        assert _go_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 18)
        assert PwdLib.set_admin(admin, True)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        assert PwdLib.set_user(user, True)
    assert _go_to_setup(PwdLib.PW.ADMIN, is_del=False)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(new_admin, None, '123456789', PwdLib.pw_incorrect)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(new_user, None, '123456789', PwdLib.pw_incorrect)
    return True


# 密码修改验证新密码测试，新密码确认时，输入错误新密码，修改失败测试
def password_security_019():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    if not PwdLib.PW.ADMIN:
        assert _go_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 18)
        assert PwdLib.set_admin(admin, True)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        assert PwdLib.set_user(user, True)
    assert _go_to_setup(PwdLib.PW.ADMIN, is_del=False)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(new_admin, False, PwdLib.PW.ADMIN, PwdLib.pw_not_same, '123456789')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(new_user, False, PwdLib.PW.USER, PwdLib.pw_not_same, '123456789')
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    assert PwdLib.del_admin(PwdLib.PW.ADMIN, True)
    return True


# 历史密码5次范围内重复修改无效，超过5次后可以修改为5次前的密码测试
def password_security_020():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_list = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                  PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                  PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                  PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                  PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user_list = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
                 PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    logging.info('管理员密码5次范围内重复无效测试')
    assert PwdLib.set_admin(admin, True)
    logging.info('第一次管理员密码设置成功')
    for index in range(0, len(admin_list)):
        if index == 0:
            assert PwdLib.set_admin(admin_list[index], True, admin)
        else:
            assert PwdLib.set_admin(admin_list[index], True, admin_list[index - 1])
        logging.info(f'第{index + 2}次管理员密码设置成功')
    assert PwdLib.set_admin(admin_list[0], False, admin_list[-1], PwdLib.pw_is_history), '修改密码为前五次的密码，没有提示密码不能与前五次密码相同'
    assert PwdLib.set_admin(admin, True, admin_list[-1]), '修改密码为第一次设置的密码，修改失败'

    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(admin_list[-1], PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    logging.info('用户密码5次范围内重复无效测试')
    assert PwdLib.set_user(user, True)
    logging.info('第一次用户密码设置成功')
    for index in range(0, len(user_list)):
        if index == 0:
            assert PwdLib.set_user(user_list[index], True, user)
        else:
            assert PwdLib.set_user(user_list[index], True, user_list[index - 1])
        logging.info(f'第{index + 2}次用户密码设置成功')
    assert PwdLib.set_user(user_list[0], False, user_list[-1], PwdLib.pw_is_history), '修改密码为前五次的密码，没有提示密码不能与前五次密码相同'
    assert PwdLib.set_user(user, True, user_list[-1]), '修改密码为第一次设置的密码，修改失败'
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(user_list[-1], PwdLib.pw_invalid)
    assert PwdLib.check_psw_post(user, SutConfig.Msg.PAGE_MAIN, 100)
    assert _go_to_setup(admin, is_del=False)
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.del_admin(admin, True)
    return True


# 开机密码测试，打开开机密码，进入系统需要输入开机密码测试
def password_security_021():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user, True)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Psw.POWER_ON_PSW_OPTION: 'Enabled'}], 10, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    logging.info('开机密码打开，进入系统需要输入密码')
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.ENTER_BOOTMENU, 50)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''), '开机密码打开，进入系统不需要输入密码'
    assert BmcLib.ping_sut(), '输入管理员密码，没有进入系统'
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    logging.info('开机密码打开，进入系统需要输入密码')
    assert PwdLib.check_psw_post(user, SutConfig.Msg.ENTER_BOOTMENU, 50)

    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''), '开机密码打开，进入系统不需要输入密码'
    assert BmcLib.ping_sut(), '输入用户密码，没有进入系统'
    assert _go_to_setup(is_del=False)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Psw.SET_ADMIN_PSW,
                                                       {SutConfig.Psw.POWER_ON_PSW_OPTION: 'Disabled'}], 5, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''), '开机密码打开，进入系统仍需要输入密码'
    logging.info('开机密码关闭，进入系统不需要输入密码')
    assert BmcLib.ping_sut(), '进入系统失败'
    assert _go_to_setup(is_del=False)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.del_admin(admin, True)
    return True


def get_current_date():
    SetUpLib.clean_buffer()
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(3)
    date = re.findall(
        r'\[([0-9]{2})/ +(?:RTC|System) Date.*([0-9]{2})/([0-9]{4})]\s*\[(\d+):\s*(?:RTC|System) Time.*([0-9]{2}):\s*(?:RTC|System) Time.*([0-9]{2})\]',
        data)
    if date and len(list(date[0])) == 6:
        date_time = list(date[0])
        date_time[0], date_time[1], date_time[2] = date_time[2], date_time[0], date_time[1]
        return date_time
    else:
        logging.info('日期抓取失败')
        return []


def get_delay_date(current_date, delay_date, add=True):
    day, hour, minute, second = delay_date
    now = datetime.datetime.strptime(' '.join(current_date), '%Y %m %d %H %M %S')
    delta = datetime.timedelta(days=day, hours=hour, minutes=minute, seconds=second)
    if add:
        delay_date = now + delta
    else:
        delay_date = now - delta
    return (delay_date.strftime('%Y'), delay_date.strftime('%m'), delay_date.strftime('%d'), delay_date.strftime('%H'),
            delay_date.strftime('%M'), delay_date.strftime('%S'))


# 密码有效期
def password_security_022():
    within_7day = [(6, 23, 50, 00)]  # 有效期7天，不过期;(6, 23, 50, 00)代表6天23小时50分钟0秒后
    out_7day = [(7, 00, 1, 00)]  # 有效期7天，过期;(7, 00, 1, 00)代表7天0小时1分钟0秒后
    within_30day = [(29, 23, 50, 00)]  # 有效期30天，不过期;(29, 23, 50, 00)代表29天23小时50分钟0秒后
    out_30day = [(30, 00, 1, 00)]  # 有效期30天，过期;(30, 00, 1, 00)代表30天0小时1分钟0秒后
    always_day = [('2099', '12', '31', '23', '59', '00'),
                  ('2020', '01', '01', '00', '00','00')]  # 有效期永久，不过期;(2099, 12, 31, 23, 59, 00)代表修改日期为2099年12月31日23时59分00秒
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    # 密码有效期7天
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user, True)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_WEEK + [
        {SutConfig.Psw.POWER_ON_PSW_OPTION: 'Enabled'}], 15)
    assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
    current_date = get_current_date()
    for delay in within_7day:
        strdelay = '{}天{}小时{}分{}秒'.format(*delay)
        delay_date = get_delay_date(current_date, delay)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
        SetUpLib.change_date_time(delay_date, save=True)
        # 用户密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, SutConfig.Msg.PAGE_MAIN, 100), f'设置密码有效期为7天，{strdelay}后用户密码POST界面过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后用户密码POST界面没有过期')
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为7天，{strdelay}后用户密码SetUp下过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后用户密码SetUp没有过期')
        # 管理员密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100), f'设置密码有效期为7天，{strdelay}后管理员密码POST界面过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后管理员密码POST界面没有过期')
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为7天，{strdelay}后管理员密码SetUp下过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后管理员密码SetUp没有过期')
    for delay in out_7day:
        strdelay = '{}天{}小时{}分{}秒'.format(*delay)
        delay_date = get_delay_date(current_date, delay)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
        SetUpLib.change_date_time(delay_date, save=True)
        if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT):
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT)
        assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为7天，开机密码打开，{strdelay}后自行启动用户密码没有过期'
        logging.info(f'设置密码有效期为7天，开机密码打开，{strdelay}后自行启动用户密码过期')
        BmcLib.init_sut()
        SetUpLib.clean_buffer()
        if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT):
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT)
        assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为7天，开机密码打开，{strdelay}后自行启动管理员密码没有过期'
        logging.info(f'设置密码有效期为7天，开机密码打开，{strdelay}后自行启动管理员密码过期')
        # 用户密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后用户密码没有过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后用户密码过期')
        assert SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 100)
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
        assert PwdLib.set_user(new_user, False, user, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后setup下用户密码没有过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后setup下用户密码过期')
        # 管理员密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后管理员密码没有过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后管理员密码过期')
        assert SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 100)
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        assert PwdLib.set_admin(new_admin, False, admin, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后setup下管理员密码没有过期'
        logging.info(f'设置密码有效期为7天，{strdelay}后setup下管理员密码过期')
    # 密码有效期30天
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 15, save=True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(user, SutConfig.Msg.PAGE_MAIN, 100), '设置密码有效期为30天,{}天{}小时{}分{}秒后用户密码过期'.format(
        *out_7day[-1])
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100), '设置密码有效期为30天,{}天{}小时{}分{}秒后管理员密码过期'.format(
        *out_7day[-1])
    for delay in within_30day:
        strdelay = '{}天{}小时{}分{}秒'.format(*delay)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
        delay_date = get_delay_date(current_date, delay)
        SetUpLib.change_date_time(delay_date, save=True)
        # 用户密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, SutConfig.Msg.PAGE_MAIN, 100), f'设置密码有效期为30天，{strdelay}后用户密码POST界面过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后用户密码POST界面没有过期')
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), 'f设置密码有效期为30天，{strdelay}后用户密码SetUp下过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后用户密码SetUp没有过期')
        # 管理员密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100), f'设置密码有效期为30天，{strdelay}后管理员密码POST界面过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后管理员密码POST界面没有过期')
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为30天，{strdelay}后管理员密码SetUp下过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后管理员密码SetUp没有过期')
    for delay in out_30day:
        strdelay = '{}天{}小时{}分{}秒'.format(*delay)
        delay_date = get_delay_date(current_date, delay)
        assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
        SetUpLib.change_date_time(delay_date, save=True)
        if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT):
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT)
        assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为30天，开机密码打开，{strdelay}后自行启动用户密码没有过期'
        logging.info(f'设置密码有效期为30天，开机密码打开，{strdelay}后自行启动用户密码过期')
        BmcLib.init_sut()
        SetUpLib.clean_buffer()
        if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT):
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT)
        assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为30天，开机密码打开，{strdelay}后自行管理员启动密码没有过期'
        logging.info(f'设置密码有效期为30天，开机密码打开，{strdelay}后自行启动管理员密码过期')
        # 用户密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后用户密码没有过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后用户密码过期')
        assert SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 100)
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_USER_PSW)
        assert PwdLib.set_user(new_user, False, user, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后setup下用户密码没有过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后setup下用户密码过期')
        # 管理员密码
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后管理员密码没有过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后管理员密码过期')
        assert SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 100)
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        assert PwdLib.set_admin(new_admin, False, admin, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后setup下管理员密码没有过期'
        logging.info(f'设置密码有效期为30天，{strdelay}后setup下管理员密码过期')
    # 密码有效期永久
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15, save=True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(user, SutConfig.Msg.PAGE_MAIN, 100), '设置密码有效期为永久,{}天{}小时{}分{}秒后管理员密码过期'.format(
        *out_30day[-1])
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100), '设置密码有效期为永久,{}天{}小时{}分{}秒后管理员密码过期'.format(
        *out_30day[-1])
    for date in always_day:
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
        SetUpLib.change_date_time(date)
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), '设置密码有效期为永久，时间{}年{}月{}日{}时{}分{}秒，管理员密码过期'.format(
            *tuple(date))
        logging.info('设置密码有效期为永久，时间{}年{}月{}日{}时{}分{}秒，管理员密码没有过期'.format(*tuple(date)))
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 18)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), '设置密码有效期为永久，时间{}年{}月{}日{}时{}分{}秒，用户密码过期'.format(
            *tuple(date))
        logging.info('设置密码有效期为永久，时间{}年{}月{}日{}时{}分{}秒，用户密码没有过期'.format(*tuple(date)))
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Psw.POWER_ON_PSW_OPTION: 'Disabled'}], 15)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.del_admin(admin, True)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Msg.DATE_TIME], 18)
    SetUpLib.change_date_time(current_date, save=True)
    return True


def password_security_023():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    BmcLib.enable_serial_normal()
    logging.info("Waiting for Hotkey message found...")
    if PwdLib.PW.ADMIN is not None:
        result = SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 150, SutConfig.Msg.POST_MESSAGE,
                                                pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,
                                                password=PwdLib.PW.ADMIN)
        if not result:
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 30):
                assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_data(PwdLib.PW.ADMIN)
                if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
                    logging.info('密码删除')
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
        elif result == [True, True]:
            assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data(PwdLib.PW.ADMIN)
            if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
                logging.info('密码删除')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
        else:
            logging.info("SetUpLib: Boot to setup main page successfully")
    else:
        result = SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 150, SutConfig.Msg.POST_MESSAGE)
        if not result:
            if SetUpLib.wait_message_enter(SutConfig.Msg.PAGE_MAIN, 30):
                assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_data(PwdLib.PW.DEFAULT_PW)
                if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
                    logging.info('密码删除')
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
        elif result == [True, True]:
            assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data(PwdLib.PW.DEFAULT_PW)
            if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS, 5):
                logging.info('密码删除')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
        else:
            logging.info("SetUpLib: Boot to setup main page successfully")

    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15, save=True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 30):
        logging.info('输入密码时按ESC没有跳过密码启动')
    else:
        return
    assert _go_to_setup(is_del=False)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.del_admin(admin, True)
    return True


# 密码删除测试，删除管理员密码，用户密码也被删除测试
def password_security_024():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user, True)
    assert _go_to_setup(admin, is_del=False)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.del_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user, False, expect=PwdLib.pw_user_only)
    return True


# 密码删除测试，删除用户密码，只删除用户密码
def password_security_025():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user, True)
    assert _go_to_setup(admin, is_del=False)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.del_user(user, True)
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    assert PwdLib.check_psw_post(user, PwdLib.pw_invalid)
    logging.info('删除用户密码，用户密码无法进入setup')
    assert PwdLib.check_psw_post(admin, SutConfig.Msg.PAGE_MAIN, 100)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.del_admin(admin, True)
    return True


def password_security_026():
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admin_list = [PwdLib.gen_pw(digit=9, upper=0, lower=0, symbol=0),
                  PwdLib.gen_pw(digit=8, upper=0, lower=0, symbol=0),
                  PwdLib.gen_pw(digit=0, upper=0, lower=19, symbol=0),
                  PwdLib.gen_pw(digit=0, upper=0, lower=20, symbol=0),
                  PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2),
                  PwdLib.gen_pw(digit=0, upper=5, lower=5, symbol=0),
                  PwdLib.gen_pw(digit=5, upper=0, lower=0, symbol=5),
                  PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2), ]
    user_list = [PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=9),
                 PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=8),
                 PwdLib.gen_pw(digit=0, upper=19, lower=0, symbol=0),
                 PwdLib.gen_pw(digit=0, upper=20, lower=0, symbol=0),
                 PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2),
                 PwdLib.gen_pw(digit=10, upper=0, lower=0, symbol=0),
                 PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=10),
                 PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2), ]

    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                            [SutConfig.Psw.SET_ADMIN_PSW, {SutConfig.Psw.CHECK_PSW: 'Enabled'},
                                             {SutConfig.Psw.PSW_COMPLEXITY: 'Disabled'}, {SutConfig.Psw.PSW_LEN: 8},
                                             {SutConfig.Psw.PSW_RETRY: 3}], 18, save=True)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin_list[0], False, expect=PwdLib.pw_len_dif)
    logging.info('设置字符长度为8，输入不符合字符长度密码失败')
    assert PwdLib.set_admin(admin_list[1], True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user_list[0], False, expect=PwdLib.pw_len_dif)
    logging.info('设置字符长度为8，输入不符合字符长度密码失败')
    assert PwdLib.set_user(admin_list[1], False, expect=PwdLib.pw_is_same)
    logging.info('用户密码管理员密码相同设置失败')
    assert PwdLib.set_user(user_list[1], True)
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    for i in range(0, 3):
        assert PwdLib.set_admin(admin, None, 'aaaaaaaa', PwdLib.pw_incorrect)
        logging.info(f'第{i + 1}次密码输错')
    assert PwdLib.set_admin(admin, None, 'aaaaaaaa', PwdLib.pw_lock)
    logging.info('第4次密码输错，屏幕锁定')
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Psw.PSW_LEN: 20}, {SutConfig.Psw.PSW_RETRY: 10}], 18,
                                            save=True)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin_list[2], False, expect=PwdLib.pw_len_dif)
    logging.info('设置字符长度为20，输入不符合字符长度密码失败')
    assert PwdLib.set_admin(admin_list[3], True)

    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user_list[2], False, expect=PwdLib.pw_len_dif)
    logging.info('设置字符长度为20，输入不符合字符长度密码失败')
    assert PwdLib.set_admin(admin_list[3], False, expect=PwdLib.pw_is_same)
    logging.info('用户密码管理员密码相同设置失败')
    assert PwdLib.set_user(user_list[3], True)
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    for i in range(0, 10):
        assert PwdLib.set_admin(admin, None, '1111111111', PwdLib.pw_incorrect)
        logging.info(f'第{i + 1}次密码输错')
    assert PwdLib.set_admin(admin, None, '111111111', PwdLib.pw_lock)
    logging.info('第11次密码输错，屏幕锁定')
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Psw.CHECK_PSW: 'Enabled'},
                                                       {SutConfig.Psw.PSW_COMPLEXITY: 'Enabled'},
                                                       {SutConfig.Psw.PSW_LEN: 10}, {SutConfig.Psw.PSW_RETRY: 5}], 18,
                                            save=True)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin_list[4], False, expect=PwdLib.pw_len_dif)
    logging.info('设置字符长度为10，输入不符合字符长度密码失败')
    assert PwdLib.set_admin(admin_list[5], False, expect=PwdLib.pw_simple)
    logging.info('密码复杂度打开，密码必须包含大小写字母，数字以及特殊符号')
    assert PwdLib.set_admin(admin_list[6], False, expect=PwdLib.pw_simple)
    assert PwdLib.set_admin(admin_list[7], True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(user_list[4], False, expect=PwdLib.pw_len_dif)
    logging.info('设置字符长度为10，输入不符合字符长度密码失败')
    assert PwdLib.set_user(user_list[5], False, expect=PwdLib.pw_simple)
    assert PwdLib.set_user(user_list[6], False, expect=PwdLib.pw_simple)
    logging.info('密码复杂度打开，密码必须包含大小写字母，数字以及特殊符号')
    assert PwdLib.set_user(user_list[7], True)
    for i in range(0, 5):
        assert PwdLib.set_user(user, None, '11111111', PwdLib.pw_incorrect)
        logging.info(f'第{i + 1}次密码输错')
    assert PwdLib.set_user(user, None, '111111111', PwdLib.pw_lock)
    logging.info('第6次用户密码输错，屏幕锁定')
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 200,
                                     SutConfig.Msg.POST_MESSAGE)
    for i in range(0, 5):
        assert PwdLib.check_psw_post('111111111', PwdLib.pw_invalid)
        logging.info(f'密码第{i + 1}次输错')
    assert PwdLib.check_psw_post('1234564564', PwdLib.pw_lock)
    logging.info('密码第6次输错，屏幕被锁定')
    assert _go_to_setup(is_del=False)
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    for i in range(0, 5):
        assert PwdLib.set_admin(admin, None, '1611111111', PwdLib.pw_incorrect)
        logging.info(f'第{i + 1}次密码输错')
    assert PwdLib.set_admin(admin, None, user_list[7], PwdLib.pw_lock)
    logging.info('第6次管理员密码输错，屏幕锁定')
    assert _go_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Psw.CHECK_PSW: 'Disabled'}], 18, save=True)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(new_admin, True)
    for i in range(0, SutConfig.Psw.TRY_COUNTS):
        assert PwdLib.set_admin(admin, None, '1611111111', PwdLib.pw_incorrect)
    assert PwdLib.set_admin(admin, None, '1111111111111', PwdLib.pw_lock), '密码检查开关关闭，重试次数没有恢复默认'
    assert _go_to_setup()
    SetUpLib.default_save()
    return True


# 管理员密码和用户密码不允许设置相同测试
def password_security_027():
    admin = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    assert _go_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
    assert PwdLib.set_admin(admin, True)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
    assert PwdLib.set_user(admin, False, expect=PwdLib.pw_is_same)
    logging.info('用户密码管理员密码相同设置失败')
    assert SetUpLib.locate_option(Key.UP, [SutConfig.Psw.SET_ADMIN_PSW], 3)
    assert PwdLib.del_admin(admin, True)
    return True
