# -*- encoding=utf8 -*-
from D2000.BaseLib import SetUpLib, SshLib, BmcLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from batf.SutInit import Sut
import time, logging, re
from batf import core
from batf.Report import stylelog
import datetime, string, random

HISTORY = set()


def gen_pw(digit=0, upper=0, lower=0, symbol=0, total=0, prefix="", suffix=""):
    """密码生成器，按规则生成密码，并且避免使用旧密码，防止Case之间互相影响"""
    digit_strs = string.digits  # 数字
    lower_strs = string.ascii_lowercase.replace("x", "")  # 小写字母
    upper_strs = string.ascii_uppercase  # 大写字母
    letter_strs = string.ascii_letters.replace("x", "")  # 大小写字母
    symbol_strs = string.punctuation  # 特殊字符加空格

    prefix_len = len(prefix) if prefix else 0
    suffix_len = len(suffix) if suffix else 0
    sum_len = digit + upper + lower + symbol + prefix_len + suffix_len
    random_len = total - sum_len
    if total and (sum_len > total):
        raise TypeError(f"Expected password length:{sum_len} > total length:{total}")

    digit_choice = "".join(random.choices(digit_strs, k=digit)) if digit > 0 else ""
    upper_choice = "".join(random.choices(upper_strs, k=upper)) if upper > 0 else ""
    lower_choice = "".join(random.choices(lower_strs, k=lower)) if lower > 0 else ""
    symbol_choice = "".join(random.choices(symbol_strs, k=symbol)) if symbol > 0 else ""
    random_scope = "".join([digit_strs, letter_strs, symbol_strs])
    random_choice = "".join(random.choices(random_scope, k=random_len)) if random_len > 0 else ""

    didit_info = f"[digit:{digit}]" if digit else ""
    upper_info = f"[upper:{upper}]" if upper else ""
    lower_info = f"[lower:{lower}]" if lower else ""
    symbol_info = f"[symbol:{symbol}]" if symbol else ""
    random_info = f"[random:{random_len}]" if random_len > 0 else ""

    pw_gen = [digit_choice, upper_choice, lower_choice, symbol_choice, random_choice]
    random.shuffle(pw_gen)
    pw_gen = "".join(pw_gen)
    password = f"{prefix}{pw_gen}{suffix}"

    if password in HISTORY:
        return gen_pw(digit, upper, lower, symbol, total, prefix, suffix)

    pw_info = f'{prefix}{didit_info}{upper_info}{lower_info}{symbol_info}{random_info}{suffix}'
    logging.info(f"Password Type: {pw_info} -> {password}")
    HISTORY.add(password)
    return password


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


def set_admin(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 5):
        logging.info('管理员密码设置成功')
    else:
        stylelog.fail('管理员密码设置失败')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Psw.ADMIN_PSW_STATUS, 3):
        logging.info('设置管理员密码后,显示管理员密码已安装')
    else:
        stylelog.fail('设置管理员密码后,没有显示管理员密码已安装')
        return
    return True


def set_user(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    if SetUpLib.wait_message(SutConfig.Tool.SET_PSW_SUC_MSG, 5):
        logging.info('用户密码设置成功')
    else:
        stylelog.fail('用户密码设置失败')
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Psw.USER_PSW_STATUS, 3):
        logging.info('设置用户密码后,显示用户密码已安装')
    else:
        stylelog.fail('设置用户密码后,没有显示用户密码已安装')
        return
    return True


def del_admin(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Psw.DEL_PSW_SUC_MSG, 5):
        logging.info('管理员密码删除成功')
    else:
        stylelog.fail('管理员密码删除失败')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    return True


def del_user(password):
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(password)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Psw.DEL_PSW_SUC_MSG, 5):
        logging.info('用户密码删除成功')
    else:
        stylelog.fail('用户密码删除失败')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
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
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_USER, 3):
        logging.info('登陆类型显示用户')
    else:
        stylelog.fail('登陆类型不是用户')
        count += 1
    if SetUpLib.check_grey_out_option(SutConfig.Psw.GREY_OPTION, SutConfig.Psw.GREY_OPTION_PATH, True):
        logging.info('用户密码登录，选项灰显')
    else:
        stylelog.fail('用户密码登录，选项不是灰显')
        count += 1
    if count == 0:
        return True
    else:
        return False


def updated_bios_setup():
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Upd.UPDATE_BIOS_LATEST, 40, 'Confirmation', timeout=15)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Upd.SETUP_MSG, 300):
        logging.info('BIOS 刷新成功')
    time.sleep(100)
    return True


@core.test_case(('4001', '[TC4001]检查管理员密码为大写字母加小写字母加数字加特殊字符', '检查管理员密码为大写字母加小写字母加数字加特殊字符'))
def setup_psw_4001():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:

        assert SetUpLib.boot_to_setup()

        if set_admin(admin) == True:
            if go_to_setup(password=admin) == [True, True]:
                logging.info('输入管理员密码成功进入SetUp')
            else:
                stylelog.fail('进入SetUp失败')
                return
        else:
            stylelog.fail('管理员密码设置失败')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
            logging.info('登陆类型显示管理员')
            assert del_admin(password=admin)
            sign = True
            return True
        else:
            stylelog.fail('登陆类型不是管理员')
            assert del_admin(password=admin)
            sign = True
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                del_admin(password=admin)


@core.test_case(('4002', '[TC4002]检查管理员密码长度为最小值', '检查管理员密码长度为最小值'))
def setup_psw_4002():
    admin = gen_pw(digit=2, upper=2, lower=2, symbol=2, total=8)
    sign = False
    try:
        assert SetUpLib.boot_to_setup()
        if set_admin(admin) == True:
            if go_to_setup(password=admin) == [True, True]:
                logging.info('输入管理员密码成功进入SetUp')
            else:
                stylelog.fail('进入SetUp失败')
                return
        else:
            stylelog.fail('管理员密码设置失败')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
            logging.info('登陆类型显示管理员')
            assert del_admin(password=admin)
            sign = True
            return True
        else:
            stylelog.fail('登陆类型不是管理员')
            assert del_admin(password=admin)
            sign = True
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                del_admin(password=admin)


@core.test_case(('4003', '[TC4003]检查管理员密码长度为最大值', '检查管理员密码长度为最大值'))
def setup_psw_4003():
    admin = gen_pw(digit=5, upper=5, lower=5, symbol=5, total=20)
    sign = False
    try:
        assert SetUpLib.boot_to_setup()

        if set_admin(admin) == True:
            if go_to_setup(password=admin) == [True, True]:
                logging.info('输入管理员密码成功进入SetUp')
            else:
                stylelog.fail('进入SetUp失败')
                return
        else:
            stylelog.fail('管理员密码设置失败')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
            logging.info('登陆类型显示管理员')
            assert del_admin(password=admin)
            sign = True
            return True
        else:
            stylelog.fail('登陆类型不是管理员')
            assert del_admin(password=admin)
            sign = True
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                del_admin(password=admin)


@core.test_case(('4004', '[TC4004]检查管理员密码输错测试', '检查管理员密码输错测试'))
def setup_psw_4004():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    limit_time = 2
    sign = False
    try:

        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin), '设置管理员密码失败'
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        for i in range(0, limit_time):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('12345678')
            if SetUpLib.wait_message(SutConfig.Psw.ERROR_PSW_MSG, 3):
                logging.info(f'SetUp下，第{i + 1}次输错密码，提示密码错误')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)

            else:
                stylelog.fail(f'SetUp下，第{i + 1}次输错密码，没有提示密码错误')
                count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('12345678')
        if SetUpLib.wait_message(SutConfig.Psw.LOCK_MSG, 3):
            logging.info(f'SetUp下，第{limit_time + 1}次输错密码，BIOS锁住')
        else:
            stylelog.fail(f'SetUp下，第{limit_time + 1}次输错密码，BIOS没有锁住')
            count += 1
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('设置密码，进入SetUp没有要求输入密码')
            return

        for i in range(0, limit_time):
            time.sleep(1)
            SetUpLib.send_data_enter('12345678')
            if SetUpLib.wait_message(SutConfig.Psw.INVALID_PSW_MSG, 3):
                logging.info(f'进入SetUp时，第{i + 1}次输错密码，提示密码错误')
                time.sleep(1)

            else:
                stylelog.fail(f'进入SetUp时，第{i + 1}次输错密码，没有提示密码错误')
                count += 1
        time.sleep(1)
        SetUpLib.send_data_enter('12345678')
        if SetUpLib.wait_message(SutConfig.Psw.LOCK_MSG, 3):
            logging.info(f'进入SetUp时，第{limit_time + 1}次输错密码，BIOS锁住')
        else:
            stylelog.fail(f'进入SetUp时，第{limit_time + 1}次输错密码，BIOS没有锁住')
            count += 1
        assert go_to_setup(password=admin)
        assert del_admin(password=admin)
        sign = True
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                del_admin(password=admin)


@core.test_case(('4005', '[TC4005]检查修改管理员密码测试', '检查修改管理员密码测试'))
def setup_psw_4005():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    change_admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:

        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin), '设置管理员密码失败'
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        time.sleep(1)
        SetUpLib.send_data_enter(change_admin)
        time.sleep(1)
        SetUpLib.send_data_enter(change_admin)
        if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 5):
            logging.info('管理员密码修改成功')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('管理员密码修改失败')
            assert go_to_setup(password=admin)
            assert del_admin(password=admin)
            sign = True
            return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('设置密码，进入SetUp没有要求输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if SetUpLib.wait_message(SutConfig.Psw.INVALID_PSW_MSG, 3):
            logging.info('修改管理员密码后，输入修改前的管理员密码，提示密码错误')
            time.sleep(1)
        else:
            stylelog.fail('修改管理员密码后，输入修改前的管理员密码，没有提示密码错误')
            assert go_to_setup(password=admin)
            assert del_admin(password=admin)
            sign = True
            return
        SetUpLib.send_data_enter(change_admin)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 60):
            logging.info('修改管理员密码后，输入修改后的管理员密码，成功进入SetUp')
        else:
            stylelog.fail('修改管理员密码后，输入修改后的管理员密码，没有进入SetUp')
            return
        assert del_admin(password=change_admin)
        sign = True
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=change_admin):
                del_admin(password=change_admin)


@core.test_case(('4006', '[TC4006]检查修改管理员为前5次测试', '检查修改管理员为前5次测试'))
def setup_psw_4006():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    admins = [gen_pw(digit=2, upper=3, lower=3, symbol=2), gen_pw(digit=2, upper=3, lower=3, symbol=2),
              gen_pw(digit=2, upper=3, lower=3, symbol=2), gen_pw(digit=2, upper=3, lower=3, symbol=2),
              gen_pw(digit=2, upper=3, lower=3, symbol=2)]
    sign = False
    try:

        assert SetUpLib.boot_to_setup()
        assert set_admin(admin)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        for index in range(0, len(admins)):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if index == 0:
                SetUpLib.send_data_enter(admin)
            else:
                SetUpLib.send_data_enter(admins[index - 1])
            time.sleep(1)
            SetUpLib.send_data_enter(admins[index])
            time.sleep(1)
            SetUpLib.send_data_enter(admins[index])
            if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 3):
                logging.info(f'第{index + 1}次修改管理员密码成功')
            else:
                stylelog.fail(f'第{index + 1}次修改管理员密码失败')
                if index == 0:

                    assert go_to_setup(password=admin)
                    assert del_admin(password=admin)
                    sign = True
                else:

                    assert go_to_setup(password=admins[index - 1])
                    assert del_admin(password=admins[index - 1])
                    sign = True
                return
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admins[-1])
        time.sleep(1)
        SetUpLib.send_data_enter(admins[0])
        time.sleep(1)
        SetUpLib.send_data_enter(admins[0])
        if SetUpLib.wait_message(SutConfig.Psw.PSW_FIVE_TIMES, 3):
            logging.info('修改密码为前五次的密码，提示密码不能与前五次密码相同')
        else:
            stylelog.fail('修改密码为前五次的密码，没有提示密码不能与前五次密码相同')
            assert go_to_setup(password=admins[0])
            assert del_admin(password=admins[0])
            sign = True
            return
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admins[-1])
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 3):
            logging.info('修改密码为第一次设置的密码，修改成功')
        else:
            stylelog.fail('修改密码为第一次设置的密码，修改失败')
            assert go_to_setup(password=admins[-1])
            assert del_admin(password=admins[-1])
            sign = True
            return
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert del_admin(password=admin)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                del_admin(admin)


@core.test_case(('4007', '[TC4007]检查用户密码为大写字母加小写字母加数字加特殊字符', '检查用户密码为大写字母加小写字母加数字加特殊字符'))
def setup_psw_4007():
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:

        assert SetUpLib.boot_to_setup()
        if set_user(user) == True:
            if go_to_setup(password=user) == [True, True]:
                logging.info('输入用户密码成功进入SetUp')
            else:
                stylelog.fail('进入SetUp失败')
                return
        else:
            stylelog.fail('用户密码设置失败')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
            logging.info('只设置用户密码,登陆类型显示管理员')
            assert del_user(password=user)
            sign = True
            return True
        else:
            stylelog.fail('登陆类型不是管理员')
            assert del_user(password=user)
            sign = True
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=user):
                del_user(password=user)


@core.test_case(('4008', '[TC4008]检查用户密码长度为最小值', '检查用户密码长度为最小值'))
def setup_psw_4008():
    user = gen_pw(digit=2, upper=2, lower=2, symbol=2, total=8)
    sign = False
    try:

        assert SetUpLib.boot_to_setup()
        if set_user(user) == True:
            if go_to_setup(password=user) == [True, True]:
                logging.info('输入用户密码成功进入SetUp')
            else:
                stylelog.fail('进入SetUp失败')
                return
        else:
            stylelog.fail('用户密码设置失败')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
            logging.info('只设置用户密码,登陆类型显示管理员')
            assert del_user(password=user)
            sign = True
            return True
        else:
            stylelog.fail('登陆类型不是管理员')
            assert del_user(password=user)
            sign = True
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=user):
                del_user(password=user)


@core.test_case(('4009', '[TC4009]检查用户密码长度为最大值', '检查用户密码长度为最大值'))
def setup_psw_4009():
    user = gen_pw(digit=5, upper=5, lower=5, symbol=5, total=20)
    sign = False
    try:

        assert SetUpLib.boot_to_setup()
        if set_user(user) == True:
            if go_to_setup(password=user) == [True, True]:
                logging.info('输入用户密码成功进入SetUp')
            else:
                stylelog.fail('进入SetUp失败')
                return

        else:
            stylelog.fail('用户密码设置失败')
            return
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        if SetUpLib.wait_message(SutConfig.Psw.LOGIN_TYPE_ADMIN, 3):
            logging.info('只设置用户密码,登陆类型显示管理员')
            assert del_user(password=user)
            sign = True
            return True
        else:
            stylelog.fail('登陆类型不是管理员')
            assert del_user(password=user)
            sign = True
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=user):
                del_user(password=user)


@core.test_case(('4010', '[TC4010]检查用户密码输错测试', '检查用户密码输错测试'))
def setup_psw_4010():
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    limit_time = 2
    sign = False
    try:

        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_user(user), '设置用户密码失败'
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        for i in range(0, limit_time):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('12345678')
            if SetUpLib.wait_message(SutConfig.Psw.ERROR_PSW_MSG, 3):
                logging.info(f'SetUp下，第{i + 1}次输错密码，提示密码错误')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)

            else:
                stylelog.fail(f'SetUp下，第{i + 1}次输错密码，没有提示密码错误')
                count += 1
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('12345678')
        if SetUpLib.wait_message(SutConfig.Psw.LOCK_MSG, 3):
            logging.info(f'SetUp下，第{limit_time + 1}次输错密码，BIOS锁住')
        else:
            stylelog.fail(f'SetUp下，第{limit_time + 1}次输错密码，BIOS没有锁住')
            count += 1
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('设置密码，进入SetUp没有要求输入密码')
            return

        for i in range(0, limit_time):
            time.sleep(1)
            SetUpLib.send_data_enter('12345678')
            if SetUpLib.wait_message(SutConfig.Psw.INVALID_PSW_MSG, 3):
                logging.info(f'进入SetUp时，第{i + 1}次输错密码，提示密码错误')
                time.sleep(1)

            else:
                stylelog.fail(f'进入SetUp时，第{i + 1}次输错密码，没有提示密码错误')
                count += 1
        time.sleep(1)
        SetUpLib.send_data_enter('12345678')
        if SetUpLib.wait_message(SutConfig.Psw.LOCK_MSG, 3):
            logging.info(f'进入SetUp时，第{limit_time + 1}次输错密码，BIOS锁住')
        else:
            stylelog.fail(f'进入SetUp时，第{limit_time + 1}次输错密码，BIOS没有锁住')
            count += 1
        assert go_to_setup(password=user)
        assert del_user(password=user)
        sign = True
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=user):
                del_user(password=user)


@core.test_case(('4011', '[TC4011]检查修改用户密码测试', '检查修改用户密码测试'))
def setup_psw_4011():
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    change_user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:

        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_user(user), '设置用户密码失败'
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        time.sleep(1)
        SetUpLib.send_data_enter(change_user)
        time.sleep(1)
        SetUpLib.send_data_enter(change_user)
        if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 5):
            logging.info('用户密码修改成功')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('用户密码修改失败')
            assert go_to_setup(password=user)
            assert del_user(password=user)
            sign = True
            return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('设置密码，进入SetUp没有要求输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if SetUpLib.wait_message(SutConfig.Psw.INVALID_PSW_MSG, 3):
            logging.info('修改用户密码后，输入修改前的用户密码，提示密码错误')
            time.sleep(1)
        else:
            stylelog.fail('修改用户密码后，输入修改前的用户密码，没有提示密码错误')
            assert go_to_setup(password=user)
            assert del_user(password=user)
            sign = True
            return
        SetUpLib.send_data_enter(change_user)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 60):
            logging.info('修改用户密码后，输入修改后的用户密码，成功进入SetUp')
        else:
            stylelog.fail('修改用户密码后，输入修改后的用户密码，没有进入SetUp')
            return
        assert del_user(password=change_user)
        sign = True
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=change_user):
                del_user(password=change_user)


@core.test_case(('4012', '[TC4012]检查修改用户为前5次测试', '检查修改用户为前5次测试'))
def setup_psw_4012():
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    users = [gen_pw(digit=2, upper=3, lower=3, symbol=2), gen_pw(digit=2, upper=3, lower=3, symbol=2),
             gen_pw(digit=2, upper=3, lower=3, symbol=2), gen_pw(digit=2, upper=3, lower=3, symbol=2),
             gen_pw(digit=2, upper=3, lower=3, symbol=2)]
    sign = False
    try:

        assert SetUpLib.boot_to_setup()
        assert set_user(user)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        for index in range(0, len(users)):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if index == 0:
                SetUpLib.send_data_enter(user)
            else:
                SetUpLib.send_data_enter(users[index - 1])
            time.sleep(1)
            SetUpLib.send_data_enter(users[index])
            time.sleep(1)
            SetUpLib.send_data_enter(users[index])
            if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 3):
                logging.info(f'第{index + 1}次修改用户密码成功')
            else:
                stylelog.fail(f'第{index + 1}次修改用户密码失败')
                if index == 0:
                    assert go_to_setup(password=user)
                    assert del_user(password=user)
                    sign = True
                else:
                    assert go_to_setup(password=users[index - 1])
                    assert del_user(password=users[index - 1])
                    sign = True
                return
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(users[-1])
        time.sleep(1)
        SetUpLib.send_data_enter(users[0])
        time.sleep(1)
        SetUpLib.send_data_enter(users[0])
        if SetUpLib.wait_message(SutConfig.Psw.PSW_FIVE_TIMES, 3):
            logging.info('修改密码为前五次的密码，提示密码不能与前五次密码相同')
        else:
            stylelog.fail('修改密码为前五次的密码，没有提示密码不能与前五次密码相同')
            assert go_to_setup(password=users[0])
            assert del_user(password=users[0])
            sign = True
            return
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(users[-1])
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 3):
            logging.info('修改密码为第一次设置的密码，修改成功')
        else:
            stylelog.fail('修改密码为第一次设置的密码，修改失败')
            assert go_to_setup(password=users[-1])
            assert del_user(password=users[-1])
            sign = True
            return
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        assert del_user(password=user)
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=user):
                del_user(user)


@core.test_case(('4013', '[TC4013]管理员密码负面测试', '管理员密码负面测试'))
def setup_psw_4013():
    low_length = [gen_pw(digit=1, upper=1, lower=1, symbol=1, total=5), '']
    error_type = [gen_pw(digit=8, upper=0, lower=0, symbol=0, total=8),  # 只有数字
                  gen_pw(digit=0, upper=8, lower=0, symbol=0, total=8),  # 只有大写字母
                  gen_pw(digit=0, upper=0, lower=8, symbol=0, total=8),  # 只有小写字母
                  gen_pw(digit=0, upper=0, lower=0, symbol=8, total=8),  # 只有特殊字符
                  gen_pw(digit=4, upper=4, lower=0, symbol=0, total=8),  # 数字加大写字母
                  gen_pw(digit=4, upper=0, lower=4, symbol=0, total=8),  # 数字加小写字母
                  gen_pw(digit=4, upper=0, lower=0, symbol=4, total=8),  # 数字加特殊字符
                  gen_pw(digit=0, upper=4, lower=4, symbol=0, total=8),  # 大写字母加小写字母
                  gen_pw(digit=0, upper=4, lower=0, symbol=4, total=8),  # 大写字母加特殊字符
                  gen_pw(digit=0, upper=0, lower=4, symbol=4, total=8),  # 小写字母加特殊字符
                  gen_pw(digit=3, upper=3, lower=2, symbol=0, total=8),  # 数字加大写字母加小写字母
                  gen_pw(digit=2, upper=3, lower=0, symbol=3, total=8),  # 数字加大写字母加特殊字符
                  gen_pw(digit=3, upper=0, lower=2, symbol=3, total=8),  # 数字加小写字母加特殊字符
                  gen_pw(digit=0, upper=2, lower=3, symbol=3, total=8)]  # 大写字母加小写字母加特殊字符
    confirm_psw = [gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='Admin@'),
                   gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='aDMIN@')]
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        for i in low_length:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(i)
            if SetUpLib.wait_message(SutConfig.Psw.CHARACTERS_LENGTH_NOT_ENOUGH, 3):
                logging.info(f'管理员密码{i}，提示长度不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
            else:
                stylelog.fail(f'管理员密码{i},没有提示长度不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ESC)
                count += 1
        time.sleep(1)
        for i in error_type:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(i)
            time.sleep(1)
            SetUpLib.send_data_enter(i)
            if SetUpLib.wait_message(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 3):
                logging.info(f'管理员密码{i}，提示类型不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
            else:
                stylelog.fail(f'管理员密码{i}，没有提示类型不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                del_admin(i)
                count += 1
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Psw.CHARACTERS_LENGTH_NOT_ENOUGH, 3):
            logging.info('确认密码输入空值，提示信息请输入足够的字符')
        else:
            stylelog.fail('确认密码输入空值，没有提示请输入足够的字符')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[1])
        if SetUpLib.wait_message(SutConfig.Psw.PSW_NOT_SAME, 3):
            logging.info('两次密码输入不一致，提示密码不同')
        else:
            stylelog.fail('两次密码输入不一致，没有提示密码不同')
            count += 1
        time.sleep(1)
        assert set_admin(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[1])
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        if SetUpLib.wait_message(SutConfig.Psw.PSW_NOT_SAME, 3):
            logging.info('修改密码时，两次密码不一致，提示密码不同')
        else:
            stylelog.fail('修改密码时，两次密码不一致，没有提示密码不同')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            del_admin(confirm_psw[1])
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert del_admin(confirm_psw[0])
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4014', '[TC4014]用户密码负面测试', '用户密码负面测试'))
def setup_psw_4014():
    low_length = [gen_pw(digit=1, upper=1, lower=1, symbol=1, total=5), '']
    error_type = [gen_pw(digit=8, upper=0, lower=0, symbol=0, total=8),  # 只有数字
                  gen_pw(digit=0, upper=8, lower=0, symbol=0, total=8),  # 只有大写字母
                  gen_pw(digit=0, upper=0, lower=8, symbol=0, total=8),  # 只有小写字母
                  gen_pw(digit=0, upper=0, lower=0, symbol=8, total=8),  # 只有特殊字符
                  gen_pw(digit=4, upper=4, lower=0, symbol=0, total=8),  # 数字加大写字母
                  gen_pw(digit=4, upper=0, lower=4, symbol=0, total=8),  # 数字加小写字母
                  gen_pw(digit=4, upper=0, lower=0, symbol=4, total=8),  # 数字加特殊字符
                  gen_pw(digit=0, upper=4, lower=4, symbol=0, total=8),  # 大写字母加小写字母
                  gen_pw(digit=0, upper=4, lower=0, symbol=4, total=8),  # 大写字母加特殊字符
                  gen_pw(digit=0, upper=0, lower=4, symbol=4, total=8),  # 小写字母加特殊字符
                  gen_pw(digit=3, upper=3, lower=2, symbol=0, total=8),  # 数字加大写字母加小写字母
                  gen_pw(digit=2, upper=3, lower=0, symbol=3, total=8),  # 数字加大写字母加特殊字符
                  gen_pw(digit=3, upper=0, lower=2, symbol=3, total=8),  # 数字加小写字母加特殊字符
                  gen_pw(digit=0, upper=2, lower=3, symbol=3, total=8)]  # 大写字母加小写字母加特殊字符
    confirm_psw = [gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='Users@'),
                   gen_pw(digit=2, upper=0, lower=0, symbol=0, total=8, prefix='uSERS@')]
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_USER_PSW, 18)
        for i in low_length:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(i)
            if SetUpLib.wait_message(SutConfig.Psw.CHARACTERS_LENGTH_NOT_ENOUGH, 3):
                logging.info(f'用户密码{i}，提示长度不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
            else:
                stylelog.fail(f'用户密码{i},没有提示长度不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ESC)
                count += 1
        time.sleep(1)
        for i in error_type:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter(i)
            time.sleep(1)
            SetUpLib.send_data_enter(i)
            if SetUpLib.wait_message(SutConfig.Psw.CHARACTERS_TYPE_NOT_ENOUGH, 3):
                logging.info(f'用户密码{i}，提示类型不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
            else:
                stylelog.fail(f'用户密码{i}，没有提示类型不符')
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                del_user(i)
                count += 1
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Psw.CHARACTERS_LENGTH_NOT_ENOUGH, 3):
            logging.info('确认密码输入空值，提示信息请输入足够的字符')
        else:
            stylelog.fail('确认密码输入空值，没有提示请输入足够的字符')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[1])
        if SetUpLib.wait_message(SutConfig.Psw.PSW_NOT_SAME, 3):
            logging.info('两次密码输入不一致，提示密码不同')
        else:
            stylelog.fail('两次密码输入不一致，没有提示密码不同')

            count += 1
        time.sleep(1)
        assert set_user(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[1])
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_psw[0])
        if SetUpLib.wait_message(SutConfig.Psw.PSW_NOT_SAME, 3):
            logging.info('修改密码时，两次密码不一致，提示密码不同')
        else:
            stylelog.fail('修改密码时，两次密码不一致，没有提示密码不同')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            del_user(confirm_psw[1])
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        assert del_user(confirm_psw[0])
        if count == 0:
            sign = True
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4015', '[TC4015]同时设置管理员用户密码测试', '同时设置管理员用户密码测试'))
def setup_psw_4015():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    password = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        logging.info('管理员密码,用户密码不同测试')
        assert SetUpLib.boot_to_setup()
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


@core.test_case(('4016', '[TC4016]同时设置管理员用户密码,管理员密码登录,修改管理员,用户密码测试', '同时设置管理员用户密码,管理员密码登录,修改管理员,用户密码测试'))
def setup_psw_4016():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    changed_admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    changed_user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert go_to_setup(password=admin)
        if is_admin() != True:
            count += 1
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        time.sleep(1)
        SetUpLib.send_data_enter(changed_admin)
        time.sleep(1)
        SetUpLib.send_data_enter(changed_admin)
        if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 5):
            logging.info('管理员密码修该成功')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('管理员密码修改失败')
            del_admin(admin)
            del_user(user)
            return
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Tool.SET_USER_PSW, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        time.sleep(1)
        SetUpLib.send_data_enter(changed_user)
        time.sleep(1)
        SetUpLib.send_data_enter(changed_user)
        if SetUpLib.wait_message(SutConfig.Tool.SET_PSW_SUC_MSG, 5):
            logging.info('用户密码修改成功')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('用户密码修改失败')
            del_admin(changed_admin)
            del_user(user)
            return
        if go_to_setup(password=changed_user) == [True, True]:
            logging.info('修改后的用户密码成功进入SetUp')
        else:
            stylelog.fail('修改后的用户密码进入SetUp失败')
            return
        if go_to_setup(password=changed_admin) == [True, True]:
            logging.info('修改后的管理员密码成功进入SetUp')
        else:
            stylelog.fail('修改后的管理员密码进入SetUp失败')
            return
        assert del_admin(changed_admin)
        assert del_user(changed_user)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4017', '[TC4017]同时设置管理员用户密码,用户密码登录,修改用户密码测试', '同时设置管理员用户密码,用户密码登录,修改管理员,用户密码测试'))
def setup_psw_4017():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    changed_user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert go_to_setup(password=user)
        if is_user() != True:
            count += 1
        assert SetUpLib.boot_to_page('Set User Password')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        time.sleep(1)
        SetUpLib.send_data_enter(changed_user)
        time.sleep(1)
        SetUpLib.send_data_enter(changed_user)
        if SetUpLib.wait_message(SutConfig.Psw.SET_PSW_SUC_MSG, 5):
            logging.info('用户密码修该成功')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail('用户密码修改失败')
            go_to_setup(password=user)
            del_admin(admin)
            del_user(user)
            return
        if go_to_setup(password=changed_user) == [True, True]:
            logging.info('修改后的用户密码成功进入SetUp')
        else:
            stylelog.fail('修改后的用户密码进入SetUp失败')
            return
        if go_to_setup(password=admin) == [True, True]:
            logging.info('管理员密码成功进入SetUp')
        else:
            stylelog.fail('管理员密码进入SetUp失败')
            return
        assert del_admin(admin)
        assert del_user(changed_user)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('4018', '[TC4018]同时设置管理员用户密码,F9不会清除密码,刷新BIOS后,清除密码', '同时设置管理员用户密码,F9不会清除密码,刷新BIOS后,清除密码'))
def setup_psw_4018():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if go_to_setup(password=user) == [True, True]:
            logging.info('F9后，用户密码依然存在')
        if go_to_setup(password=admin) == [True, True]:
            logging.info('F9后，管理员密码依然存在')
        assert updated_bios_setup()
        if go_to_setup(password=admin) == True:
            logging.info('刷新BIOS后密码被清除')
            return True
        else:
            stylelog.fail('刷新BIOS后密码没有被清除')
            del_admin(admin)
            del_user(user)
            return

    except Exception as e:
        go_to_setup(password=admin)
        del_admin(admin)
        del_user(user)
        logging.error(e)
        return core.Status.Fail


def change_date_days(days):
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.DATE_TIME], 6)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data = re.findall(r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})\]', SetUpLib.get_data(2, readline=False))
    if not data:
        stylelog.fail("时间抓取失败")
        return
    data = data[0]
    day = data[1]
    month = data[0]
    year = data[2]
    now = datetime.date(int(year), int(month), int(day))
    delta = datetime.timedelta(days)
    n_date = now + delta
    n_year = n_date.strftime('%Y')
    n_month = n_date.strftime('%m')
    n_day = n_date.strftime('%d')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter(n_month)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter(n_day)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter(n_year)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    data = re.findall(r'\[([0-9]{2})/ +System Date.*([0-9]{2})/([0-9]{4})\]', SetUpLib.get_data(2, readline=False))
    if not data:
        stylelog.fail('时间抓取失败')
        return

    if data[0][0] == n_month and data[0][1] == n_day and data[0][2] == n_year:
        time.sleep(1)
        logging.info('日期修改成功')
    else:
        stylelog.fail('日期修改失败')
        return


@core.test_case(('4019', '[TC4019]同时设置管理员用户密码,密码有效期测试', '同时设置管理员用户密码,密码有效期测试'))
def setup_psw_4019():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:
        assert go_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_WEEK, 15)
        change_date_days(days=6)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)

        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(2)
        SetUpLib.send_data(user)
        time.sleep(2)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('设置密码有效期为7天，6天后用户密码没有失效')
        else:
            return
        # assert SetUpLib.boot_to_page('Set User Password')
        # SetUpLib.send_key(Key.ENTER)
        # time.sleep(1)
        # SetUpLib.send_data(user)
        # time.sleep(2)
        # if not SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        #     logging.info('设置密码有效期为7天，6天后用户密码SetUp下没有失效')
        # else:
        #     stylelog.fail('设置密码有效期为7天，6天后用户密码SetUp下失效')
        #     return

        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(2)
        SetUpLib.send_data(admin)
        time.sleep(2)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('设置密码有效期为7天，6天后管理员密码没有失效')
        else:
            return

        change_date_days(days=1)
        SetUpLib.send_key(Key.ESC)
        # assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Psw.SET_ADMIN_PSW,18)
        # time.sleep(1)
        # SetUpLib.send_key(Key.ENTER)
        # time.sleep(2)
        # SetUpLib.send_data(admin)
        # if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        #     logging.info('设置密码有效期为7天，7天后setup下管理员密码失效')
        #     time.sleep(1)
        #     SetUpLib.send_key(Key.ENTER)
        # else:
        #     stylelog.fail('设置密码有效期为7天，7天后setup下管理员密码没有失效')
        #     return
        # time.sleep(1)
        # SetUpLib.send_key(Key.ESC)
        # time.sleep(2)
        # assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 3)
        # time.sleep(1)
        # SetUpLib.send_key(Key.ENTER)
        # time.sleep(2)
        # SetUpLib.send_data(user)
        # time.sleep(1)
        # if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        #     logging.info('设置密码有效期为7天，7天后setup下用户密码失效')
        #     time.sleep(1)
        #     SetUpLib.send_key(Key.ENTER)
        # else:
        #     stylelog.fail('设置密码有效期为7天，7天后setup下用户密码没有失效')
        #     return
        # time.sleep(1)
        # SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)

        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
            logging.info('设置密码有效期为7天，7天后进入setup提示用户密码失效')
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('设置密码有效期为7天，7天后进入setup没有提示用户密码失效')
            return

        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('进入setup')
        else:
            return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
            logging.info('设置密码有效期为7天，7天后进入setup提示管理员密码失效')
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('设置密码有效期为7天，7天后进入setup没有提示管理员密码失效')
            return

        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('进入setup')
        else:
            return
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 15)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert go_to_setup(password=admin)
        change_date_days(22)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('设置密码有效期为30天，29天后用户密码没有失效')
        else:
            return
        # assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Psw.SET_USER_PSW,18)
        # SetUpLib.send_key(Key.ENTER)
        # time.sleep(1)
        # SetUpLib.send_data(user)
        # time.sleep(1)
        # if not SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        #     logging.info('设置密码有效期为30天，29天后用户密码SetUp下没有失效')
        # else:
        #     return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('设置密码有效期为30天，29天后管理员密码没有失效')
        else:
            return
        change_date_days(1)
        SetUpLib.send_key(Key.ESC)
        # assert SetUpLib.locate_menu(Key.DOWN,SutConfig.Psw.SET_ADMIN_PSW,18)
        # SetUpLib.send_key(Key.ENTER)
        # time.sleep(2)
        # SetUpLib.send_data(admin)
        # if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        #     logging.info('设置密码有效期为30天，30天后setup下管理员密码失效')
        #     time.sleep(1)
        #     SetUpLib.send_key(Key.ENTER)
        # else:
        #     stylelog.fail('设置密码有效期为30天，30天后setup下管理员密码没有失效')
        #     return
        # time.sleep(1)
        # SetUpLib.send_key(Key.ESC)
        # time.sleep(2)
        # assert SetUpLib.locate_menu(Key.DOWN, [SutConfig.Psw.SET_USER_PSW], 18)
        # SetUpLib.send_key(Key.ENTER)
        # time.sleep(2)
        # SetUpLib.send_data(user)
        # if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
        #     logging.info('设置密码有效期为30天，30天后setup下用户密码失效')
        #     time.sleep(1)
        #     SetUpLib.send_key(Key.ENTER)
        # else:
        #     stylelog.fail('设置密码有效期为30天，30天后setup下用户密码没有失效')
        #     return
        # time.sleep(1)
        # SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)

        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
            logging.info('设置密码有效期为30天，30天后进入setup提示用户密码失效')
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('设置密码有效期为30天，30天后进入setup没有提示用户密码失效')
            return
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('进入setup')
        else:
            return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        if SetUpLib.wait_message_enter(SutConfig.Psw.PSW_EXPIRE, 5):
            logging.info('设置密码有效期为30天，30天后进入setup提示管理员密码失效')
            SetUpLib.send_key(Key.ENTER)
        else:
            stylelog.fail('设置密码有效期为30天，30天后进入setup没有提示管理员密码失效')
            return
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('进入setup')
        else:
            return
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.SET_ADMIN_PSW, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_ALWAYS, 15)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('设置密码有效期为无限期，30天后用户密码没有失效')
        else:
            return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Tool.POST_PSW_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SETUP_MESSAGE, 100):
            logging.info('设置密码有效期为无限期，30天后管理员密码没有失效')
        else:
            return
        assert del_admin(admin)
        assert del_user(user)
        sign = True
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                if del_admin(admin):
                    del_user(user)


@core.test_case(('4020', '[TC4020]设置管理员密码,开机密码测试', '设置管理员密码,开机密码测试'))
def setup_psw_4020():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:
        assert SetUpLib.boot_to_setup()
        set_admin(admin)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.OPEN_POWER_ON_PSW, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if BmcLib.ping_sut(150):
            logging.info('成功进入系统')
        else:
            stylelog.fail('进入系统失败')
            return
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        logging.info('系统下重启')
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if BmcLib.ping_sut(150):
            logging.info('成功进入系统')
        else:
            stylelog.fail('进入系统失败')
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('成功进入系统')
        else:
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('进入SetUp失败')
            return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE):
            logging.info('成功进入SetUp')
        else:
            return

        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CLOSE_POWER_ON_PSW, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if BmcLib.ping_sut():
            logging.info('关闭开机密码，进入系统无需输入密码')
        else:
            stylelog.fail('关闭开机密码，进入系统仍需输入密码')
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('成功进入系统')
        else:
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('关闭开机密码，启动菜单进入Setup无需输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 30):
            logging.info('开机密码关闭，启动菜单进入SetUp需要输入密码')
        else:
            stylelog.fail('进入SetUp失败')
            return
        assert del_admin(admin)
        sign = True
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                del_admin(admin)


@core.test_case(('4021', '[TC4021]设置用户密码,开机密码测试', '设置用户密码,开机密码测试'))
def setup_psw_4021():
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:
        assert SetUpLib.boot_to_setup()
        set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.OPEN_POWER_ON_PSW, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if BmcLib.ping_sut(150):
            logging.info('成功进入系统')
        else:
            stylelog.fail('进入系统失败')
            return
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        logging.info('系统下重启')
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if BmcLib.ping_sut(150):
            logging.info('成功进入系统')
        else:
            stylelog.fail('进入系统失败')
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('成功进入系统')
        else:
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('进入SetUp失败')
            return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE):
            logging.info('成功进入SetUp')
        else:
            return
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CLOSE_POWER_ON_PSW, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if BmcLib.ping_sut():
            logging.info('关闭开机密码，进入系统无需输入密码')
        else:
            stylelog.fail('关闭开机密码，进入系统仍需输入密码')
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('成功进入系统')
        else:
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('关闭开机密码，启动菜单进入Setup无需输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 30):
            logging.info('开机密码关闭，启动菜单进入SetUp需要输入密码')
        else:
            stylelog.fail('进入SetUp失败')
            return
        assert del_user(user)
        sign = True
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=user):
                del_user(user)


@core.test_case(('4022', '[TC4022]同时设置管理员,用户密码,开机密码测试', '同时设置管理员,用户密码,开机密码测试'))
def setup_psw_4022():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    sign = False
    try:
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin)
        assert set_user(user)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.OPEN_POWER_ON_PSW, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if BmcLib.ping_sut(150):
            logging.info('管理员密码,成功进入系统')
        else:
            stylelog.fail('管理员密码,进入系统失败')
            return
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        logging.info('系统下重启')
        if SetUpLib.wait_message(SutConfig.Psw.POWER_ON_MSG, 200):
            logging.info('开机密码打开，进入系统需要输入密码')
        else:
            if BmcLib.ping_sut(30):
                stylelog.fail('开机密码打开，进入系统不需要输入密码')
                return
            else:
                stylelog.fail('第一启动项可能不是系统，请手动确认')
                return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if BmcLib.ping_sut(150):
            logging.info('用户密码,成功进入系统')
        else:
            stylelog.fail('用户密码进入系统失败')
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('管理员密码成功进入系统')
        else:
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        logging.info('开机密码打开,进入启动菜单需要输入密码')
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('用户密码成功进入系统')
        else:
            return
        time.sleep(15)

        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('启动菜单进入SetUp不需要输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data_enter(user)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE):
            logging.info('用户密码成功进入SetUp')
        else:
            return

        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Psw.POWER_ON_MSG, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if not SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU, 30):
            return
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('启动菜单进入SetUp不需要输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data_enter(admin)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE):
            logging.info('管理员密码成功进入SetUp')
        else:
            return
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.CLOSE_POWER_ON_PSW, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if BmcLib.ping_sut():
            logging.info('关闭开机密码，进入系统无需输入密码')
        else:
            stylelog.fail('关闭开机密码，进入系统仍需输入密码')
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if BmcLib.ping_sut():
            logging.info('成功进入系统')
        else:
            return
        time.sleep(15)
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('关闭开机密码，启动菜单进入Setup无需输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data(user)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 30):
            logging.info('开机密码关闭，启动菜单进入SetUp需要输入密码')
        else:
            stylelog.fail('进入SetUp失败')
            return
        if not SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                         SutConfig.Msg.POST_MESSAGE):
            stylelog.fail('关闭开机密码,进入启动菜单仍需输入密码')
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Tool.POST_PSW_MSG):
            stylelog.fail('关闭开机密码，启动菜单进入Setup无需输入密码')
            return
        time.sleep(1)
        SetUpLib.send_data(admin)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 30):
            logging.info('开机密码关闭，启动菜单进入SetUp需要输入密码')
        else:
            stylelog.fail('进入SetUp失败')
            return
        assert del_admin(admin)
        assert del_user(user)
        sign = True
        return True

    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if sign == False:
            if go_to_setup(password=admin):
                if del_admin(admin):
                    del_user(user)


@core.test_case(('4023', '[TC4023]设置密码后，设置密码加密算法自动置灰测试', '设置密码后，设置密码加密算法自动置灰测试'))
def setup_psw_4023():
    admin = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    user = gen_pw(digit=2, upper=3, lower=3, symbol=2)
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert set_admin(admin)
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_ENC_ALG], 10):
            logging.info('设置管理员密码后，设置密码加密算法自动置灰')
        else:
            stylelog.fail('设置管理员密码后，设置密码加密算法没有置灰')
            count += 1
        assert del_admin(admin)
        assert set_user(user)
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.SET_ENC_ALG], 10):
            logging.info('设置用户密码后，设置密码加密算法自动置灰')
        else:
            stylelog.fail('设置用户密码后，设置密码加密算法没有置灰')
            count += 1
        assert del_user(user)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
