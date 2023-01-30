# -*- encoding=utf8 -*-
from ByoTool.Config import *
from ByoTool.BaseLib import *


def go_to_setup(key=SutConfig.Msg.SETUP_KEY, pw_prompt=SutConfig.Tool.POST_PSW_MSG, password=None, is_del=True):
    if password is None:
        password = PwdLib.PW.ADMIN if PwdLib.PW.ADMIN else PwdLib.PW.USER
        password = '' if not password else password
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
            if is_del:
                if PwdLib.PW.ADMIN:
                    del_admin(PwdLib.PW.ADMIN)
                if PwdLib.PW.USER:
                    del_user(PwdLib.PW.USER)
            logging.info("SetUpLib: Boot to setup main page successfully,with password")
            return [True, True]
        elif result == True:
            logging.info("SetUpLib: Boot to setup main page successfully")
            return True
        else:
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 10):
                if is_del:
                    if PwdLib.PW.ADMIN:
                        del_admin(PwdLib.PW.ADMIN)
                    if PwdLib.PW.USER:
                        del_user(PwdLib.PW.USER)
                    SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15)
            else:
                SetUpLib.reboot()
                try_counts -= 1
    logging.info("SetUpLib: Boot to setup main page Failed")
    return


def set_admin(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
    assert PwdLib.set_admin(password, True)
    return True


def set_user(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    assert PwdLib.set_user(password, True)
    return True


def del_admin(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
    assert PwdLib.del_admin(password, True)
    return True


def del_user(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
    assert PwdLib.del_user(password, True)
    return True


def is_admin():
    count = 0
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
        logging.info('登陆类型显示管理员')
    else:
        stylelog.fail('登陆类型不是管理员')
        count += 1
    for i in SutConfig.Msg.PAGE_ALL:
        if not SetUpLib.boot_to_page(i):
            count += 1
    if count == 0:
        return True
    else:
        return False


def is_user():
    count = 0
    # assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_USER, 3):
        logging.info('登陆类型显示用户')
    else:
        stylelog.fail('登陆类型不是用户')
        count += 1
    if count == 0:
        return True
    else:
        return False


def updated_bios_setup():
    pass
    # assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.UPDATE_BIOS_LATEST, 40, 'Confirmation', timeout=15)
    # time.sleep(2)
    # SetUpLib.send_key(Key.ENTER)
    # if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
    #     logging.info('BIOS 刷新成功')
    # time.sleep(100)
    # return True


@core.test_case(('4001', '[TC4001]检查管理员密码为大写字母加小写字母加数字', '检查管理员密码为大写字母加小写字母加数字'))
def setup_psw_4001():
    """
    Name:   检查管理员密码为大写字母加小写字母加数字

    Steps:  1.SetUp设置管理员密码为大写字母加小写字母加数字
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """

    admin = PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=0)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4002', '[TC4002]检查管理员密码为大写字母加小写字母加特殊字符', '检查管理员密码为大写字母加小写字母加特殊字符'))
def setup_psw_4002():
    """
    Name:   检查管理员密码为大写字母加小写字母加特殊字符

    Steps:  1.SetUp设置管理员密码为大写字母加小写字母加特殊字符
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """
    admin = PwdLib.gen_pw(digit=0, upper=3, lower=3, symbol=2)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4003', '[TC4003]检查管理员密码为大写字母加数字加特殊字符', '检查管理员密码为大写字母加数字加特殊字符'))
def setup_psw_4003():
    """
    Name:   检查管理员密码为大写字母加数字加特殊字符

    Steps:  1.SetUp设置管理员密码为大写字母加数字加特殊字符
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """

    admin = PwdLib.gen_pw(digit=2, upper=3, lower=0, symbol=3)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4004', '[TC4004]检查管理员密码为小写字母加数字加特殊字符', '检查管理员密码为小写字母加数字加特殊字符'))
def setup_psw_4004():
    """
    Name:   检查管理员密码为小写字母加数字加特殊字符

    Steps:  1.SetUp设置管理员密码为小写字母加数字加特殊字符
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """
    admin = PwdLib.gen_pw(digit=3, upper=0, lower=3, symbol=2)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4005', '[TC4005]检查管理员密码为大写字母加小写字母加数字加特殊字符', '检查管理员密码为大写字母加小写字母加数字加特殊字符'))
def setup_psw_4005():
    """
    Name:   检查管理员密码为大写字母加小写字母加数字加特殊字符

    Steps:  1.SetUp设置管理员密码为大写字母加小写字母加数字加特殊字符
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """
    admin = PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4006', '[TC4006]检查管理员密码长度为最小值', '检查管理员密码长度为最小值'))
def setup_psw_4006():
    """
    Name:   检查管理员密码长度为最小值

    Steps:  1.SetUp设置管理员密码长度为最小值
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """
    admin = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.PW.MIN)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4007', '[TC4007]检查管理员密码长度为最大值', '检查管理员密码长度为最大值'))
def setup_psw_4007():
    """
    Name:   检查管理员密码长度为最大值

    Steps:  1.SetUp设置管理员密码长度为最大值
            2.进入SetUp
            3.删除管理员密码

    Result: 1.管理员密码设置成功
            2.要求输入密码，输入管理员密码成功进入SetUp
            3.管理员密码删除成功
    """
    admin = PwdLib.gen_pw(digit=5, upper=5, lower=5, symbol=5, total=PwdLib.PW.MAX)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert go_to_setup(password=admin, is_del=False) == [True, True], '进入SetUp失败'
        assert is_admin()
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4008', '[TC4008]检查管理员密码输错测试', '检查管理员密码输错测试'))
def setup_psw_4008():
    """
    Name:   检查管理员密码输错测试

    Steps:  1.SetUp设置管理员密码
            2.SetUp下修改密码输入错误的密码，错误次数达到上限
            3.进入SetUp输入错误密码，错误次数达到上限

    Result: 1.管理员密码设置成功
            2/3.输错密码提示密码错误，错误次数达到上限提示被锁住
    """
    admin = PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2)
    new_admin = PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2)
    limit_time = 2
    try:
        assert go_to_setup()
        assert set_admin(admin), '设置管理员密码失败'
        for i in range(0, limit_time):
            assert PwdLib.set_admin(new_admin, None, '12345678', PwdLib.pw_incorrect)
        assert PwdLib.set_admin(new_admin, None, '12345678', PwdLib.pw_limit)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE), '设置密码，进入SetUp没有要求输入密码'
        for i in range(0, limit_time):
            assert PwdLib.check_psw_post('12345678', PwdLib.pw_invalid)
        assert PwdLib.check_psw_post('123456789', PwdLib.pw_limit_post)
        assert go_to_setup(password=admin, is_del=False)
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4009', '[TC4009]检查修改管理员密码测试', '检查修改管理员密码测试'))
def setup_psw_4009():
    """
    Name:   检查修改管理员密码测试

    Steps:  1.SetUp下设置管理员密码
            2.修改管理员密码
            3.使用修改后的密码进入SetUp

    Result: 1.管理员密码设置成功
            2.管理员密码修改成功
            3.输入修改前的密码提示密码错误，输入修改后的密码成功进入SetUp
    """
    admin = PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2)
    change_admin = PwdLib.gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        assert go_to_setup()
        assert set_admin(admin), '设置管理员密码失败'
        assert PwdLib.set_admin(change_admin, True, admin)
        assert PwdLib.set_admin(admin, None, admin, PwdLib.pw_incorrect)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE), '设置密码，进入SetUp没有要求输入密码'
        assert PwdLib.check_psw_post(admin, PwdLib.pw_invalid), '修改管理员密码后，输入修改前的管理员密码，没有提示密码错误'
        assert PwdLib.check_psw_post(change_admin, SutConfig.Msg.SETUP_MESSAGE, 60)
        assert del_admin(password=change_admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4010', '[TC4010]检查修改管理员为前5次测试', '检查修改管理员为前5次测试'))
def setup_psw_4010():
    """
    Name:   检查修改管理员为前5次测试

    Steps:  1.SetUp下设置管理员密码
            2.依次修改管理员密码为a,b,c,d,e
            3.修改管理员密码为a
            4.修改管理员密码为第一次设置的密码

    Result: 1.管理员密码设置成功
            2.管理员密码修改成功
            3.修改失败，提示与前5次密码相同
            4.修改成功
    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    admins = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3), PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
              PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3), PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
              PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    try:
        assert go_to_setup()
        assert set_admin(admin)
        for index in range(0, len(admins)):
            if index == 0:
                assert PwdLib.set_admin(admins[index], True, admin)
            else:
                assert PwdLib.set_admin(admins[index], True, admins[index - 1])
        assert PwdLib.set_admin(admins[0], False, admins[-1], PwdLib.pw_is_history), '修改密码为前五次的密码，没有提示密码不能与前五次密码相同'
        assert PwdLib.set_admin(admin, True, admins[-1]), '修改密码为第一次设置的密码，修改失败'
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4011', '[TC4011]检查用户密码为大写字母加小写字母加数字', '检查用户密码为大写字母加小写字母加数字'))
def setup_psw_4011():
    """

    Name:   检查用户密码为大写字母加小写字母加数字

    Steps:  1.SetUp设置用户密码为大写字母加小写字母加数字
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=0)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4012', '[TC4012]检查用户密码为大写字母加小写字母加特殊字符', '检查用户密码为大写字母加小写字母加特殊字符'))
def setup_psw_4012():
    """

    Name:   检查用户密码为大写字母加小写字母加特殊字符

    Steps:  1.SetUp设置用户密码为大写字母加小写字母加特殊字符
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=0, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4013', '[TC4013]检查用户密码为大写字母加数字加特殊字符', '检查用户密码为大写字母加数字加特殊字符'))
def setup_psw_4013():
    """

    Name:   检查用户密码为大写字母加数字加特殊字符

    Steps:  1.SetUp设置用户密码为大写字母加数字加特殊字符
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=0, symbol=3)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4014', '[TC4014]检查用户密码为小写字母加数字加特殊字符', '检查用户密码为小写字母加数字加特殊字符'))
def setup_psw_4014():
    """

    Name:   检查用户密码为小写字母加数字加特殊字符

    Steps:  1.SetUp设置用户密码为小写字母加数字加特殊字符
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=3, upper=0, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4015', '[TC4015]检查用户密码为大写字母加小写字母加数字加特殊字符', '检查用户密码为大写字母加小写字母加数字加特殊字符'))
def setup_psw_4015():
    """

    Name:   检查用户密码为大写字母加小写字母加数字加特殊字符

    Steps:  1.SetUp设置用户密码为大写字母加小写字母加数字加特殊字符
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4016', '[TC4016]检查用户密码长度为最小值', '检查用户密码长度为最小值'))
def setup_psw_4016():
    """

    Name:   检查用户密码长度为最小值

    Steps:  1.SetUp设置用户密码长度为最小值
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PwdLib.PW.MIN)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4017', '[TC4017]检查用户密码长度为最大值', '检查用户密码长度为最大值'))
def setup_psw_4017():
    """

    Name:   检查用户密码长度为最大值

    Steps:  1.SetUp设置用户密码长度为最大值
            2.进入SetUp
            3.删除用户密码

    Result: 1.用户密码设置成功
            2.要求输入密码，输入用户密码成功进入SetUp
            3.用户密码删除成功
    """
    user = PwdLib.gen_pw(digit=5, upper=5, lower=5, symbol=5, total=PwdLib.PW.MAX)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert is_admin()
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4018', '[TC4018]检查用户密码输错测试', '检查用户密码输错测试'))
def setup_psw_4018():
    """

    Name:   检查用户密码输错测试

    Steps:  1.SetUp设置用户密码
            2.SetUp下修改密码输入错误的密码，错误次数达到上限
            3.进入SetUp输入错误密码，错误次数达到上限

    Result: 1.用户密码设置成功
            2/3.输错密码提示密码错误，错误次数达到上限提示被锁住
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    limit_time = 2
    try:
        assert go_to_setup()
        assert set_user(user), '设置用户密码失败'
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        for i in range(0, limit_time):
            assert PwdLib.set_user(new_user, None, '123456789', PwdLib.pw_incorrect)
        assert PwdLib.set_user(new_user, None, '123456789', PwdLib.pw_limit)

        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        for i in range(0, limit_time):
            assert PwdLib.check_psw_post('123456789', PwdLib.pw_invalid)
        assert PwdLib.check_psw_post('123456789', PwdLib.pw_limit_post)
        assert go_to_setup(password=user, is_del=False)
        assert del_user(password=user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4019', '[TC4019]检查修改用户密码测试', '检查修改用户密码测试'))
def setup_psw_4019():
    """

    Name:   检查修改用户密码测试

    Steps:  1.SetUp下设置用户密码
            2.修改用户密码
            3.使用修改后的密码进入SetUp

    Result: 1.用户密码设置成功
            2.用户密码修改成功
            3.输入修改前的密码提示密码错误，输入修改后的密码成功进入SetUp
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    change_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_user(user), '设置用户密码失败'
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        assert PwdLib.set_admin(change_user, True, user)
        assert PwdLib.set_user(user, None, user, PwdLib.pw_incorrect)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, PwdLib.pw_invalid)
        assert PwdLib.check_psw_post(change_user, SutConfig.Msg.SETUP_MESSAGE, 60)
        assert del_user(password=change_user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4020', '[TC4020]检查修改用户为前5次测试', '检查修改用户为前5次测试'))
def setup_psw_4020():
    """

    Name:   检查修改用户为前5次测试

    Steps:  1.SetUp下设置用户密码
            2.依次修改用户密码为a,b,c,d,e
            3.修改用户密码为a
            4.修改用户密码为第一次设置的密码

    Result: 1.用户密码设置成功
            2.用户密码修改成功
            3.修改失败，提示与前5次密码相同
            4.修改成功
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    users = [PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3), PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
             PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3), PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3),
             PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)]
    try:
        assert go_to_setup()
        assert set_user(user)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        for index in range(0, len(users)):
            if index == 0:
                assert PwdLib.set_user(users[index], True, user)
            else:
                assert PwdLib.set_user(users[index], True, users[index - 1])
        assert PwdLib.set_user(users[0], False, users[-1], PwdLib.pw_is_history), '修改密码为前五次的密码，没有提示密码不能与前五次密码相同'
        assert PwdLib.set_user(user, True, users[-1]), '修改密码为第一次设置的密码，修改失败'
        assert del_user(password=user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4021', '[TC4021]管理员密码负面测试', '管理员密码负面测试'))
def setup_psw_4021():
    """
    Name:   管理员密码负面测试

    Steps:  1.检查设置管理员密码长度小于最小长度
            2.检查设置管理员密码不满足复杂度要求
            3.检查设置管理员密码新密码确认密码输入不同

    Result: 1/2/3.密码设置失败
    """
    low_length = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=5), '']
    error_type = [PwdLib.gen_pw(digit=6, upper=0, lower=0, symbol=0, total=6),  # 只有数字
                  PwdLib.gen_pw(digit=0, upper=6, lower=0, symbol=0, total=6),  # 只有大写字母
                  PwdLib.gen_pw(digit=0, upper=0, lower=6, symbol=0, total=6),  # 只有小写字母
                  PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=6, total=6),  # 只有特殊字符
                  PwdLib.gen_pw(digit=3, upper=3, lower=0, symbol=0, total=6),  # 数字加大写字母
                  PwdLib.gen_pw(digit=3, upper=0, lower=3, symbol=0, total=6),  # 数字加小写字母
                  PwdLib.gen_pw(digit=3, upper=0, lower=0, symbol=3, total=6),  # 数字加特殊字符
                  PwdLib.gen_pw(digit=0, upper=3, lower=3, symbol=0, total=6),  # 大写字母加小写字母
                  PwdLib.gen_pw(digit=0, upper=3, lower=0, symbol=3, total=6),  # 大写字母加特殊字符
                  PwdLib.gen_pw(digit=0, upper=0, lower=3, symbol=3, total=6),  # 小写字母加特殊字符
                  ]
    confirm_psw = [PwdLib.gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='Admin@'),
                   PwdLib.gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='aDMIN@')]

    try:
        assert go_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        for i in low_length:
            assert PwdLib.set_admin(i, False, expect=PwdLib.pw_short)
        for i in error_type:
            assert PwdLib.set_admin(i, False, expect=PwdLib.pw_simple)
        # assert PwdLib.set_admin(confirm_psw[0], False, expect=PwdLib.pw_not_same, confirm_pw='')
        assert PwdLib.set_admin(confirm_psw[0], False, expect=PwdLib.pw_not_same, confirm_pw=confirm_psw[1])
        assert PwdLib.set_admin(confirm_psw[0], True)
        assert PwdLib.set_admin(confirm_psw[1], False, confirm_psw[0], PwdLib.pw_not_same, confirm_psw[0])
        assert del_admin(confirm_psw[0])
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4022', '[TC4022]用户密码负面测试', '用户密码负面测试'))
def setup_psw_4022():
    """
    Name:   用户密码负面测试

    Steps:  1.检查设置用户密码长度小于最小长度
            2.检查设置用户密码不满足复杂度要求
            3.检查设置用户密码新密码确认密码输入不同

    Result: 1/2/3.密码设置失败
    """

    low_length = [PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=5), '']
    error_type = [PwdLib.gen_pw(digit=6, upper=0, lower=0, symbol=0, total=6),  # 只有数字
                  PwdLib.gen_pw(digit=0, upper=6, lower=0, symbol=0, total=6),  # 只有大写字母
                  PwdLib.gen_pw(digit=0, upper=0, lower=6, symbol=0, total=6),  # 只有小写字母
                  PwdLib.gen_pw(digit=0, upper=0, lower=0, symbol=6, total=6),  # 只有特殊字符
                  PwdLib.gen_pw(digit=3, upper=3, lower=0, symbol=0, total=6),  # 数字加大写字母
                  PwdLib.gen_pw(digit=3, upper=0, lower=3, symbol=0, total=6),  # 数字加小写字母
                  PwdLib.gen_pw(digit=3, upper=0, lower=0, symbol=3, total=6),  # 数字加特殊字符
                  PwdLib.gen_pw(digit=0, upper=3, lower=3, symbol=0, total=6),  # 大写字母加小写字母
                  PwdLib.gen_pw(digit=0, upper=3, lower=0, symbol=3, total=6),  # 大写字母加特殊字符
                  PwdLib.gen_pw(digit=0, upper=0, lower=3, symbol=3, total=6),  # 小写字母加特殊字符
                  ]
    confirm_psw = [PwdLib.gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='Users@'),
                   PwdLib.gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='uSERS@')]
    try:
        assert go_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        for i in low_length:
            assert PwdLib.set_user(i, False, expect=PwdLib.pw_short)
        for i in error_type:
            assert PwdLib.set_user(i, False, expect=PwdLib.pw_simple)
        # assert PwdLib.set_user(confirm_psw[0], False, expect=PwdLib.pw_short, confirm_pw='')
        assert PwdLib.set_user(confirm_psw[0], False, expect=PwdLib.pw_not_same, confirm_pw=confirm_psw[1])
        assert PwdLib.set_user(confirm_psw[0], True)
        assert PwdLib.set_user(confirm_psw[1], False, confirm_psw[0], PwdLib.pw_not_same, confirm_psw[0])
        assert del_user(confirm_psw[0])
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4023', '[TC4023]同时设置管理员用户密码测试', '同时设置管理员用户密码测试'))
def setup_psw_4023():
    """
    Name:   同时设置管理员用户密码测试

    Steps:  1.管理员，用户密码设置不同
            2.管理员，用户密码设置相同

    Result: 1/2.管理员，用户密码设置成功
    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    password = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        logging.info('管理员密码,用户密码不同测试')
        assert go_to_setup()
        assert set_admin(admin), '管理员密码设置失败'
        assert set_user(user), '用户密码设置失败'
        logging.info('管理员,用户密码设置不同验证成功')
        assert del_admin(admin)
        assert del_user(user)
        assert set_admin(password)
        assert set_user(password)
        logging.info('管理员,用户密码设置相同验证成功')
        assert del_admin(password)
        assert del_user(password)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4024', '[TC4024]同时设置管理员用户密码,管理员密码登录,修改管理员,用户密码测试', '同时设置管理员用户密码,管理员密码登录,修改管理员,用户密码测试'))
def setup_psw_4024():
    """
    Name:   同时设置管理员用户密码,管理员密码登录,修改管理员,用户密码测试

    Steps:  1.设置管理员，用户密码
            2.管理员密码登录SetUp,检查权限，修改管理员密码，修改用户密码
            3.使用修改后的管理员，用户密码登录SetUp

    Result: 1.管理员，用户密码设置成功
            2.权限为管理员，修改管理员，用户密码成功
            3.修改后的管理员，用户密码成功登录SetUp
    """

    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    changed_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    changed_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert go_to_setup(password=admin, is_del=False)
        assert is_admin()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        assert PwdLib.set_admin(changed_admin, True, admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
        assert PwdLib.set_user(changed_user, True, user)
        assert go_to_setup(password=changed_user, is_del=False) == [True, True], '修改后的用户密码进入SetUp失败'
        assert go_to_setup(password=changed_admin, is_del=False) == [True, True], '修改后的管理员密码进入SetUp失败'
        assert del_admin(changed_admin)
        assert del_user(changed_user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4025', '[TC4025]同时设置管理员用户密码,用户密码登录,修改用户密码测试', '同时设置管理员用户密码,用户密码登录,修改管理员,用户密码测试'))
def setup_psw_4025():
    """
    Name:   同时设置管理员用户密码,用户密码登录,修改管理员,用户密码测试

    Steps:  1.设置管理员，用户密码
            2.用户密码登录SetUp,检查权限，修改管理员，用户密码
            3.使用修改后的用户密码登录SetUp

    Result: 1.管理员，用户密码修改成功
            2.权限为用户，不能修改管理员密码，可以修改用户密码
            3.修改后的用户密码成功登录SetUp

    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    changed_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:

        assert go_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert go_to_setup(password=user, is_del=False)
        assert is_user()
        assert SetUpLib.boot_to_page('Set User Password')
        assert PwdLib.set_user(changed_user, True, user)
        assert go_to_setup(password=changed_user, is_del=False) == [True, True]
        assert go_to_setup(password=admin, is_del=False) == [True, True]
        assert del_admin(admin)
        assert del_user(changed_user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4026', '[TC4026]同时设置管理员用户密码,F9不会清除密码,刷新BIOS后,清除密码', '同时设置管理员用户密码,F9不会清除密码,刷新BIOS后,清除密码'))
def setup_psw_4026():
    """
    Name:   同时设置管理员用户密码,F9不会清除密码,刷新BIOS后,清除密码

    Steps:  1.设置管理员，用户密码
            2.F9恢复默认值
            3.刷新BIOS

    Result: 1.管理员，用户密码设置成功
            2.管理员，用户密码没有被清除
            3.管理员，用户密码被清除
    """

    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert go_to_setup(password=user, is_del=False) == [True, True]
        assert go_to_setup(password=admin, is_del=False) == [True, True]
        assert updated_bios_setup()
        assert go_to_setup(password=admin, is_del=False) == True
        PwdLib.PW.ADMIN = None
        PwdLib.PW.USER = None
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4027', '[TC4027]设置管理员密码,开机密码测试', '设置管理员密码,开机密码测试'))
def setup_psw_4027():
    """
    Name:   设置管理员密码,开机密码测试

    Steps:  1.设置管理员密码，打开开机密码
            2.检查进入系统是否需要输入密码
            3.检查进入启动菜单是否需要输入密码

    Result: 2.需要输入密码
            3.需要输入密码
    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.OPEN_POWER_ON_PSW, 18, save=True)
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        assert PwdLib.check_psw_post(admin, '')
        assert BmcLib.ping_sut(150), '进入系统失败'
        SetUpLib.reboot()
        logging.info('系统下重启')
        assert SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200), '开机密码打开，进入系统不需要输入密码'
        assert PwdLib.check_psw_post(admin, '')
        assert BmcLib.ping_sut(150), '进入系统失败'
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '进入SetUp失败'
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 30)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CLOSE_POWER_ON_PSW, 18, save=True)
        assert BmcLib.ping_sut(), '关闭开机密码，进入系统仍需输入密码'
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '关闭开机密码，启动菜单进入Setup无需输入密码'
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 30), '进入SetUp失败'
        assert del_admin(admin)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4028', '[TC4028]设置用户密码,开机密码测试', '设置用户密码,开机密码测试'))
def setup_psw_4028():
    """
    Name:   设置用户密码,开机密码测试

    Steps:  1.设置用户密码，打开开机密码
            2.检查进入系统是否需要输入密码
            3.检查进入启动菜单是否需要输入密码

    Result: 2.需要输入密码
            3.需要输入密码
    """

    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.OPEN_POWER_ON_PSW, 18, save=True)
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        assert PwdLib.check_psw_post(user, '')
        assert BmcLib.ping_sut(150), '进入系统失败'
        SetUpLib.reboot()
        logging.info('系统下重启')
        assert SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200), '开机密码打开，进入系统不需要输入密码'
        assert PwdLib.check_psw_post(user, '')
        assert BmcLib.ping_sut(150), '进入系统失败'
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        assert PwdLib.check_psw_post(user, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '进入SetUp失败'
        assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 30)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CLOSE_POWER_ON_PSW, 18, save=True)
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '关闭开机密码，启动菜单进入Setup无需输入密码'
        assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 30), '进入SetUp失败'
        assert del_user(user)
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4029', '[TC4029]同时设置管理员,用户密码,开机密码测试', '同时设置管理员,用户密码,开机密码测试'))
def setup_psw_4029():
    """
    Name:   同时设置管理员,用户密码,开机密码测试

    Steps:  1.设置管理员，用户密码，打开开机密码
            2.检查进入系统是否需要输入密码，管理员，用户密码进入系统
            3.检查进入启动菜单是否需要输入密码，管理员密码，用户密码进入启动菜单

    Result: 2.需要输入密码，管理员，用户密码成功进入系统
            3.需要输入密码，管理员密码，用户密码成功进入启动菜单
    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.OPEN_POWER_ON_PSW, 18, save=True)
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        assert PwdLib.check_psw_post(admin, '')
        assert BmcLib.ping_sut(150), '管理员密码,进入系统失败'
        SetUpLib.reboot()
        logging.info('系统下重启')
        assert SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200)
        assert PwdLib.check_psw_post(user, '')
        assert BmcLib.ping_sut(150), '用户密码进入系统失败'
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        assert PwdLib.check_psw_post(user, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '启动菜单进入SetUp不需要输入密码'
        assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 30)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.ENTER_BOOTMENU, 30)
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '启动菜单进入SetUp不需要输入密码'
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 30)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CLOSE_POWER_ON_PSW, 18, save=True)
        assert BmcLib.ping_sut(), '关闭开机密码，进入系统仍需输入密码'
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, '')
        assert BmcLib.ping_sut()
        time.sleep(15)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '关闭开机密码，启动菜单进入Setup无需输入密码'
        assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 30), '进入SetUp失败'
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE), '关闭开机密码,进入启动菜单仍需输入密码'
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30,
                                           SutConfig.Tool.POST_PSW_MSG), '关闭开机密码，启动菜单进入Setup无需输入密码'
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 30)
        assert del_admin(admin)
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


def get_current_date():
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(3)
    date = re.findall(
        r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})]\s*\[(\d+):\s*System Time.*([0-9]{2}):\s*System Time.*([0-9]{2})\]',
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


def change_date_time(datetuple):
    year, month, day, hour, minute, second = datetuple
    for date in [month, day, year, hour, minute, '00']:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if date:
            time.sleep(1)
            SetUpLib.send_data(date)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        if date == year:
            SetUpLib.send_key(Key.DOWN)
            time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    SetUpLib.clean_buffer()
    SetUpLib.send_key(Key.ENTER)
    data = re.findall(r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})]\s*\[([0-9]{2}):\s*System Time.*([0-9]{2}):',
                      SetUpLib.get_data(3))
    if data:
        data = data[0]
        if data[0] == month and data[1] == day and data[2] == year and data[3] == hour and data[4] == minute:
            logging.info('日期修改成功')
        else:
            logging.info('日期可能修改失败')
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True


@core.test_case(('4030', '[TC4030]管理员密码有效期', '管理员密码有效期'))
def setup_psw_4030():
    """
    Name:  管理员密码有效期

    Steps:  1.设置管理员密码，修改密码有效期为7天
            2.验证7天内密码是否过期
            3.验证7天后密码是否过期
            4.修改密码有效期为30天
            5.验证30天内密码是否过期
            6.验证30天后密码是否过期
            7.修改密码有效期为永久有效
            8.验证最小时间，最大时间密码是否过期

    Result: 2.密码没有过期
            3.密码过期
            5.密码没有过期
            6.密码过期
            8.密码没有过期
    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        within_7day = [(6, 23, 50, 00)]  # 有效期7天，不过期;(6, 23, 50, 00)代表6天23小时50分钟0秒后
        out_7day = [(7, 00, 1, 00)]  # 有效期7天，过期;(7, 00, 1, 00)代表7天0小时1分钟0秒后
        within_30day = [(29, 23, 50, 00)]  # 有效期30天，不过期;(29, 23, 50, 00)代表29天23小时50分钟0秒后
        out_30day = [(30, 00, 1, 00)]  # 有效期30天，过期;(30, 00, 1, 00)代表30天0小时1分钟0秒后
        always_day = [('2099', '12', '31', '23', '59', '00'),
                      ('2022', '01', '01', '00', '00',
                       '00')]  # 有效期永久，不过期;(2099, 12, 31, 23, 59, 00)代表修改日期为2099年12月31日23时59分00秒
        assert go_to_setup()
        assert set_admin(admin)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_WEEK, 15)
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DATE_TIME], 6)
        current_date = get_current_date()
        for delay in within_7day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期7天,{strdelay}后密码过期'
            logging.info(f'设置密码有效期7天,{strdelay}后密码没有过期')
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为7天，{strdelay}后密码SetUp下过期'

        for delay in out_7day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            assert PwdLib.set_admin(new_admin, False, admin, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后setup下密码没有过期'

        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 15, save=True)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60)
        for delay in within_30day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期30天,{strdelay}后密码过期'
            logging.info(f'设置密码有效期30天,{strdelay}后密码没有过期')
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为30天，{strdelay}后密码SetUp下过期'

        for delay in out_30day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            assert PwdLib.set_admin(new_admin, False, admin, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后setup下密码没有过期'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15, save=True)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60)
        for date in always_day:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            change_date_time(date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE,
                                         60), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后后密码过期'.format(*tuple(date))
            logging.info('设置密码永久有效,时间{}年{}月{}日{}时{}分{}秒后密码没有过期'.format(*tuple(date)))
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后密码SetUp下过期'.format(
                *tuple(date))
        assert del_admin(admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4031', '[TC4031]用户密码有效期', '用户密码有效期'))
def setup_psw_4031():
    """
    Name:  用户密码有效期

    Steps:  1.设置用户密码，修改密码有效期为7天
            2.验证7天内密码是否过期
            3.验证7天后密码是否过期
            4.修改密码有效期为30天
            5.验证30天内密码是否过期
            6.验证30天后密码是否过期
            7.修改密码有效期为永久有效
            8.验证最小时间，最大时间密码是否过期

    Result: 2.密码没有过期
            3.密码过期
            5.密码没有过期
            6.密码过期
            8.密码没有过期
    """
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        within_7day = [(6, 23, 50, 00)]  # 有效期7天，不过期;(6, 23, 50, 00)代表6天23小时50分钟0秒后
        out_7day = [(7, 00, 1, 00)]  # 有效期7天，过期;(7, 00, 1, 00)代表7天0小时1分钟0秒后
        within_30day = [(29, 23, 50, 00)]  # 有效期30天，不过期;(29, 23, 50, 00)代表29天23小时50分钟0秒后
        out_30day = [(30, 00, 1, 00)]  # 有效期30天，过期;(30, 00, 1, 00)代表30天0小时1分钟0秒后
        always_day = [('2099', '12', '31', '23', '59', '00'),
                      ('2022', '01', '01', '00', '00',
                       '00')]  # 有效期永久，不过期;(2099, 12, 31, 23, 59, 00)代表修改日期为2099年12月31日23时59分00秒
        assert go_to_setup()
        assert set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_WEEK, 15)
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DATE_TIME], 6)
        current_date = get_current_date()
        for delay in within_7day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期7天,{strdelay}后密码过期'
            logging.info(f'设置密码有效期7天,{strdelay}后密码没有过期')
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为7天，{strdelay}后密码SetUp下过期'

        for delay in out_7day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
            assert PwdLib.set_admin(new_user, False, user, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后setup下密码没有过期'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 15, save=True)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 60)
        for delay in within_30day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期30天,{strdelay}后密码过期'
            logging.info(f'设置密码有效期30天,{strdelay}后密码没有过期')
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为30天，{strdelay}后密码SetUp下过期'

        for delay in out_30day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
            assert PwdLib.set_admin(new_user, False, user, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后setup下密码没有过期'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15, save=True)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 60)
        for date in always_day:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            change_date_time(date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE,
                                         60), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后后密码过期'.format(*tuple(date))
            logging.info('设置密码永久有效,时间{}年{}月{}日{}时{}分{}秒后密码没有过期'.format(*tuple(date)))
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后密码SetUp下过期'.format(
                *tuple(date))
        assert del_admin(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4032', '[TC4032]管理员，用户密码有效期', '管理员，用户密码有效期'))
def setup_psw_4032():
    """
    Name:  管理员，用户密码有效期

    Steps:  1.设置管理员，用户密码，修改密码有效期为7天
            2.验证7天内管理员，用户密码是否过期
            3.验证7天后管理员，用户密码是否过期
            4.修改密码有效期为30天
            5.验证30天内管理员，用户密码是否过期
            6.验证30天后管理员，用户密码是否过期
            7.修改密码有效期为永久有效
            8.验证最小时间，最大时间管理员，用户密码是否过期

    Result: 2.管理员，用户密码没有过期
            3.管理员，用户密码过期
            5.管理员，用户密码没有过期
            6.管理员，用户密码过期
            8.管理员，用户密码没有过期
    """
    admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_admin = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    new_user = PwdLib.gen_pw(digit=3, upper=3, lower=3, symbol=3)
    try:
        within_7day = [(6, 23, 50, 00)]  # 有效期7天，不过期;(6, 23, 50, 00)代表6天23小时50分钟0秒后
        out_7day = [(7, 00, 1, 00)]  # 有效期7天，过期;(7, 00, 1, 00)代表7天0小时1分钟0秒后
        within_30day = [(29, 23, 50, 00)]  # 有效期30天，不过期;(29, 23, 50, 00)代表29天23小时50分钟0秒后
        out_30day = [(30, 00, 1, 00)]  # 有效期30天，过期;(30, 00, 1, 00)代表30天0小时1分钟0秒后
        always_day = [('2099', '12', '31', '23', '59', '00'),
                      ('2022', '01', '01', '00', '00', '00')]
        # 有效期永久，不过期;(2099, 12, 31, 23, 59, 00)代表修改日期为2099年12月31日23时59分00秒
        assert go_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_WEEK, 15)
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DATE_TIME], 6)
        current_date = get_current_date()
        for delay in within_7day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期7天,{strdelay}后用户密码过期'
            logging.info(f'设置密码有效期7天,{strdelay}后密码没有过期')
            assert SetUpLib.boot_to_page('Set User Password')
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为7天，{strdelay}后用户密码SetUp下过期'
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期7天,{strdelay}后管理员密码过期'
            logging.info(f'设置密码有效期7天,{strdelay}后密码没有过期')
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为7天，{strdelay}后管理员密码SetUp下过期'
        for delay in out_7day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后用户密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.boot_to_page('Set User Password')
            assert PwdLib.set_user(new_user, False, user, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后setup下密码没有过期'
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后管理员密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            assert PwdLib.set_admin(new_admin, False, admin, PwdLib.pw_expire), f'设置密码有效期为7天，{strdelay}后setup下管理员密码没有过期'

        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 15, save=True)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60)
        for delay in within_30day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期30天,{strdelay}后用户密码过期'
            logging.info(f'设置密码有效期30天,{strdelay}后用户密码没有过期')
            assert SetUpLib.boot_to_page('Set User Password')
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为30天，{strdelay}后用户密码SetUp下过期'
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60), f'设置密码有效期30天,{strdelay}后管理员密码过期'
            logging.info(f'设置密码有效期30天,{strdelay}后管理员密码没有过期')
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), f'设置密码有效期为30天，{strdelay}后管理员密码SetUp下过期'
        for delay in out_30day:
            strdelay = '{}天{}小时{}分{}秒'.format(*delay)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            delay_date = get_delay_date(current_date, delay)
            change_date_time(delay_date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后用户密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.boot_to_page('Set User Password')
            assert PwdLib.set_user(new_user, False, user, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后setup下用户密码没有过期'
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后密码没有过期'
            assert SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            assert PwdLib.set_admin(new_admin, False, admin,
                                    PwdLib.pw_expire), f'设置密码有效期为30天，{strdelay}后setup下管理员密码没有过期'
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15, save=True)
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE)
        assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE, 60)
        for date in always_day:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [SutConfig.Msg.PAGE_MAIN, SutConfig.Psw.DATE_TIME], 6)
            change_date_time(date)
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(user, SutConfig.Msg.SETUP_MESSAGE,
                                         60), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后用户密码过期'.format(*tuple(date))
            logging.info('设置密码永久有效,时间{}年{}月{}日{}时{}分{}秒后用户密码没有过期'.format(*tuple(date)))
            assert SetUpLib.boot_to_page('Set User Password')
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(user)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后用户密码SetUp下过期'.format(
                *tuple(date))
            assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                             SutConfig.Msg.POST_MESSAGE)
            assert PwdLib.check_psw_post(admin, SutConfig.Msg.SETUP_MESSAGE,
                                         60), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后后管理员密码过期'.format(*tuple(date))
            logging.info('设置密码永久有效,时间{}年{}月{}日{}时{}分{}秒后管理员密码没有过期'.format(*tuple(date)))
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(admin)
            assert not SetUpLib.wait_message(PwdLib.pw_expire, 3), '设置密码永久有效，时间{}年{}月{}日{}时{}分{}秒后管理员密码SetUp下过期'.format(
                *tuple(date))
        assert del_admin(admin)
        assert del_user(user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
