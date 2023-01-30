import logging
import random
import string
import time

from batf import var, SerialLib, MiscLib
from batf.SutInit import Sut

from SPR4P.BaseLib import SetUpLib, BmcLib, PlatMisc, Update, BmcWeb
from SPR4P.Config.PlatConfig import Msg, Key
from SPR4P.Config import SutConfig

# password prompt message in security page
pw_enter_old = 'Please type in your password'
pw_enter_new = 'Please type in your new password'
pw_cfm_new = 'Please confirm your new password'
pw_change_saved = 'Changes have been saved after press'
pw_invalid = 'Invalid Password'
pw_is_history = 'Password can not be the same as the'
pw_be_diff = 'The new password should be different'
pw_user_del_cfm = 'After the user password is deleted,common users cannot log in'
pw_short = "Password too short"
pw_simple = "Password too simple"
pw_simple_confirm = "Enabling simple password poses security risks"
pw_lock = "Enter incorrect password 3 times"
pw_not_same = "Passwords are not the same"
pw_admin_del_cfm = "Deleting passwords might have security problem. Are you sure"
pw_is_weak = "The password fails the dictionary check"
pw_input_weak = "Please type in your data"
pw_weak_short = "Please Input 8~16 Character Weak Password"
pw_weak_del = "Are you sure to clear this weak password"
pw_weak_not_exist_del = "Input weak password isn't in Weak Password List"
pw_weak_exist = 'Weak password same with "Default String list"'
pw_weak_same = "Weak password same with Weak Password list"
pw_weak_full = "Weak password buffer full, erase one"
pw_is_expire = "The current password is expiration"

# password prompt message for init password
pw_is_default = 'The current password is the default'

# BMC security log: password change
sec_admin_success = "Security,BIOS,BMC Change Supervisor password successfully"
sec_user_success = "Security,BIOS,BMC Change User password successfully"
sec_old_wrong = "Security,BIOS,BMC update password failed.Old password is wrong"
sec_old_invalid = "Security,BIOS,Old password is not valid"
sec_new_short = "Security,BIOS,New password is too short"
sec_new_long = "Security,BIOS,New password is too long"
sec_new_simple = "Security,BIOS,New password complexity invalid"
sec_new_weak = "Security,BIOS,The password fails the dictionary check"
sec_new_invalid = "Security,BIOS,New password is not valid"
sec_is_history = "Security,BIOS,New password is the same to recent one"
sec_two_more_diff = "Security,BIOS,New password should have two or more different char with old password"
sec_invalid_char = "Security,BIOS,BMC update password failed.Password contain invalid character"
# BMC security log: password expire
sec_admin_expire = "Security,BIOS,Administer password has expired"
sec_user_expire = "Security,BIOS,User password has expired"
# BMC security log: weak pw change from BIOS setup
sec_add_weak = "Security,BIOS,User(Administrator),Weak Password Change success"
sec_del_weak = "Security,BIOS,User(Administrator),Weak Password Delete success"
sec_reset_weak = "Security,BIOS,Default weak password is loaded"
# BMC security log: login/logout
sec_user_front_login = "Security,BIOS,User(User) Frontpage login success"
sec_user_setup_login = "Security,BIOS,User(User) Setup Utility login success"
sec_user_setup_logout = "Security,BIOS,User(User) Setup Utility logout success"
sec_admin_front_login = "Security,BIOS,User(Administrator) Frontpage login success"
sec_admin_setup_login = "Security,BIOS,User(Administrator) Setup Utility login success"
sec_admin_setup_logout = "Security,BIOS,User(Administrator) Setup Utility logout success"
sec_check_fail = "Security,BIOS,Check Password error"
# BMC security log: password change from BIOS setup
sec_admin_set_user_pass = "Security,BIOS,User(Administrator),Set User password success"
sec_admin_set_user_fail = "Security,BIOS,User(Administrator),Set User password fail"
sec_admin_change_user_pass = "Security,BIOS,User(Administrator),Change User password success"
sec_admin_clear_user = "Security,BIOS,User(Administrator),Clear User password success"
sec_user_change_pass = "Security,BIOS,User(User),Change User password success"
sec_user_change_fail = "Security,BIOS,User(User),Change User password fail"
sec_user_check_fail = "Security,BIOS,Check User Password error"
sec_del_admin = "Security,BIOS,User(Administrator),Clear Administrator password success"


class PW:
    MIN = 8                                             # 密码最小长度
    MAX = 16                                            # 密码最大长度
    WEAK_CNT = 100                                      # 自定义弱密码个数
    SYMBOL = string.punctuation + " "                   # 密码支持的特殊字符

    ADMIN = Msg.BIOS_PASSWORD                           # 当前管理员密码
    USER = None                                         # 当前用户密码
    HISTORY = {Msg.BIOS_PASSWORD, Msg.BIOS_PW_DEFAULT}  # 历史密码
    WEAK_PW = [                                         # 弱密码列表
        "Work@7*24",
        'Visit@7*24"',
        "Visit@7*24",
        "Update@7*24",
        "Password@123",
        "Password",
        "Pass456$",
        "Admin_1243",
        "Admin_1234#",
        "Admin_1234",
        "Admin_123",
        "Admin_12#",
        "Admin_01",
        "Admin@storage",
        "Admin@revive",
        "Admin@9000",
        "Admin@7*24",
        "Admin@7*2",
        "Admin@1234",
        "Admin@123",
        "Admin23@#",
        "Admin1@BCM",
        "Admin123!",
        "Admin!123",
        "Access@7*24"]


def gen_pw(digit=0, upper=0, lower=0, symbol=0, total: int = None, prefix: str = "", suffix: str = ""):
    """密码生成器，按规则生成密码，并且避免使用旧密码，防止Case之间互相影响"""
    if total == 0:
        logging.info('Password Type: [Empty] -> ""')
        return ""

    digit_strs = string.digits
    lower_strs = string.ascii_lowercase
    upper_strs = string.ascii_uppercase
    letter_strs = string.ascii_letters
    symbol_strs = PW.SYMBOL

    lower_strs = lower_strs.replace("x", "")  # workaround for 'x' missing if send data too fast(known issue)
    letter_strs = letter_strs.replace("x", "")  # workaround for 'x' missing if send data too fast(known issue)

    digit = 0 if digit < 0 else digit
    upper = 0 if upper < 0 else upper
    lower = 0 if lower < 0 else lower
    symbol = 0 if symbol < 0 else symbol

    prefix_len = len(prefix) if prefix else 0
    suffix_len = len(suffix) if suffix else 0
    sum_len = digit + upper + lower + symbol + prefix_len + suffix_len
    random_len = total - sum_len if total else 0
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

    if (password in PW.HISTORY) or (password in PW.WEAK_PW) or password.startswith(" ") or password.endswith(" "):
        return gen_pw(digit, upper, lower, symbol, total, prefix, suffix)

    pw_info = f'{prefix}{didit_info}{upper_info}{lower_info}{symbol_info}{random_info}{suffix}'
    logging.info(f"Password Type: {pw_info} -> {password}")
    PW.HISTORY.add(password)
    return password


def pw_is_valid(pw, simple=False):
    if len(pw) < 8:
        logging.info(f"Password length < {PW.MIN}: {pw}")
        return False
    if len(pw) > 16:
        logging.info(f"Password length > {PW.MAX}: {pw}")
        return False
    if simple:  # 简单密码只检查长度, 忽略类型检查
        logging.info(f"Simple password is valid")
        return True
    type_found = set()
    for s in pw:
        if s in string.ascii_uppercase:
            type_found.add("upper")
        elif s in string.ascii_lowercase:
            type_found.add("lower")
        elif s in string.digits:
            type_found.add("digit")
        elif s in string.punctuation + " ":
            type_found.add("symbol")
    symbol_req = "symbol" in type_found
    type_req = len(type_found) >= 3
    if not symbol_req:
        logging.info(f"Symbol not in pw: {pw}")
    elif not type_req:
        logging.info(f"At least 3 types of upper/lower/digit/symbol: {pw}")
    return symbol_req and type_req  # 合法密码至少有3种字符组合,并且至少有一个特殊字符


def set_password(new_pw, old_pw, result, save, expect=None, confirm_pw=None):
    """
    result为True, 预期设置成功
    result为False, 预期设置失败
    result为None, 预期旧密码输入错误
    expect: 预期的消息弹窗(第一行)
    """
    confirm_pw = new_pw if not confirm_pw else confirm_pw
    try:
        SetUpLib.send_key(Key.ENTER)
        if old_pw:
            assert SetUpLib.wait_msg(pw_enter_old, 10), '{} not found'.format(pw_enter_old)
            SetUpLib.send_data_enter(old_pw)
            if result is None:
                old_wrong = pw_invalid if not expect else expect
                assert SetUpLib.wait_msg(old_wrong)
                logging.info("Password input is invalid")
                SetUpLib.send_key(Key.ENTER)
                return True
        assert SetUpLib.wait_msg(pw_enter_new, 15), '{} not found'.format(pw_enter_new)
        SetUpLib.send_data_enter(new_pw)
        assert SetUpLib.wait_msg(pw_cfm_new, 15), '{} not found'.format(pw_cfm_new)
        SetUpLib.send_data_enter(confirm_pw)

        if result:
            assert SetUpLib.wait_msg(pw_change_saved, 15), '{} not found'.format(pw_change_saved)
            logging.info(f"Password can be set success: {new_pw}")
            SetUpLib.send_keys([Key.ENTER])
        else:
            fail_reason = f"{pw_is_history}|{pw_be_diff}|{pw_short}|{pw_invalid}|{pw_simple}|{pw_not_same}"
            expect = expect if expect else fail_reason
            assert SetUpLib.wait_msg(expect), f'Msg not found: "{expect}"'
            SetUpLib.send_keys([Key.ENTER])
            logging.info(f"Password can not be set: {new_pw}(invalid)")

        if save:
            SetUpLib.send_keys([Key.F10], delay=1)
            SetUpLib.send_key(Key.Y)
            assert SetUpLib.wait_msg(Msg.CPU_RSC_ALLOC, 300)
        if result and save:
            logging.info("Password changed: {0} => {1}".format(old_pw, new_pw))
        return True
    except Exception as e:
        logging.error(e)


def update_current_pw(pw_admin: str = None, pw_user: str = None):
    if isinstance(pw_admin, str):
        valid_pw_admin = pw_admin[:PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current Admin Password -> {valid_pw_admin}")
        PW.ADMIN = valid_pw_admin
    if isinstance(pw_user, str):
        valid_pw_user = pw_user[:PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current User Password -> {valid_pw_user}")
        PW.USER = valid_pw_user


def continue_to_setup_with_pw(current_pw, invalid_pw=None, to_admin=None, to_user=None, default=False):
    """不重启，继续启动到setup，用指定密码登录，同时可验证非法密码或默认密码"""
    try:
        logging.info("Verifying password...")
        assert SetUpLib.continue_to_pw_prompt()

        if invalid_pw:
            logging.info(f"Password should not be [old]: {invalid_pw}")
            SetUpLib.send_data_enter(invalid_pw)
            assert SetUpLib.wait_msg(pw_invalid)
            SetUpLib.send_keys([Key.ENTER])

        logging.info(f"Password should be [new]: {current_pw}")
        SetUpLib.send_data_enter(current_pw)
        if default:
            assert SetUpLib.wait_msg(pw_is_default, 15)
            SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert SetUpLib.move_to_bios_config()

        if to_admin:
            assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.locate_option(Msg.SET_ADMIN_PW, Key.DOWN, 20)
            return True
        elif to_user:
            assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.locate_option(Msg.SET_USR_PW, Key.DOWN, 20)
            return True
        return True
    except Exception as e:
        logging.error(e)


def check_pw_length_and_hidden(pw, length):
    """检查输入密码长度,并确认密码是否隐藏"""
    ser_log = PlatMisc.get_current_serial_log()
    pw_show = "*" * length
    assert f' {pw_show} ' in ser_log, f'"{pw_show}" not found in serial log'
    assert pw not in ser_log, f"Warning: password '{Msg.BIOS_PASSWORD}' found in serial log"
    logging.info("Password length match and input string is hidden")
    return True


# ###########################管理员密码################################
def set_admin_password(new_pw, old_pw, result, save, expect=None, confirm_pw=None):
    """输入管理员密码"""
    assert set_password(new_pw, old_pw, result, save, expect, confirm_pw)
    if save and result:
        update_current_pw(pw_admin=new_pw)
    return True


def set_admin_pw_and_verify(new, old):
    """设置密码并重启验证"""
    assert SetUpLib.locate_option(Msg.SET_ADMIN_PW, Key.DOWN, 20)
    assert set_admin_password(new, old, result=True, save=True)
    assert continue_to_setup_with_pw(new, old, to_admin=True)
    return True


def delete_admin_pw(save=True):
    """删除管理员密码"""
    assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
    assert SetUpLib.set_option_value(Msg.DEL_PW_SUPPORT, Msg.ENABLE)
    if SetUpLib.wait_msg(pw_admin_del_cfm, 15):
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Msg.DEL_ADMIN_PW)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.wait_msg(Msg.PRESS_ENTER_PROMPT, 15)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.wait_msg(pw_enter_old)
    SetUpLib.send_data_enter(PW.ADMIN)
    assert SetUpLib.wait_msg(pw_change_saved)
    SetUpLib.send_key(Key.ENTER)
    if save:
        assert SetUpLib.save_without_exit()
        update_current_pw(pw_admin="")
        assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY, Key.LEFT)
    return True


def set_admin_pw_by_unipwd(new_pw, old_pw="", simple=False):
    """通过uniPwd工具设置管理员密码，如果能设置成功，则更新管理员密码"""
    cmd = "sets" if simple else "set"
    if PlatMisc.unipwd_tool(new_pw, old_pw, cmd=cmd):
        update_current_pw(pw_admin=new_pw)
        return True


def restore_admin_password():
    """恢复默认管理员密码"""
    try:
        BmcLib.clear_cmos()
        if PW.ADMIN == Msg.BIOS_PASSWORD:  # 如果全局密码未变更,则不需要恢复
            return True

        logging.info(f'Reset password to "{Msg.BIOS_PASSWORD}" by unipwd tool')
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 5):
            assert SetUpLib.boot_to_default_os()
        if not PlatMisc.unipwd_tool(new_pw=Msg.BIOS_PASSWORD, cmd="check"):
            assert set_admin_pw_by_unipwd(Msg.BIOS_PASSWORD, old_pw=PW.ADMIN)
        return True
    except Exception:
        if Update.flash_bios_bin_and_init(var.get("biosimage")):
            update_current_pw(pw_admin=Msg.BIOS_PASSWORD)
            return True


# ###########################用户密码################################
def set_user_password(new_pw, old_pw, result, save, expect=None, confirm_pw=None):
    """输入用户密码"""
    assert set_password(new_pw, old_pw, result, save, expect, confirm_pw)
    if save and result:
        update_current_pw(pw_user=new_pw)
    return True


def set_user_pw_and_verify(new, old):
    """设置密码并重启验证"""
    assert SetUpLib.locate_option(Msg.SET_USR_PW, Key.DOWN, 20)
    assert set_user_password(new, old, result=True, save=True)
    assert continue_to_setup_with_pw(new, old, to_user=True)
    return True


def set_user_pw_save_wo_exit(new_pw, old_pw):
    """设置用户密码，保存不退出"""
    assert SetUpLib.locate_option(Msg.SET_USR_PW)
    assert set_password(new_pw, old_pw, result=True, save=False)
    assert SetUpLib.save_without_exit()
    update_current_pw(pw_user=new_pw)
    assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
    assert SetUpLib.locate_option(Msg.SET_USR_PW)
    return True


def init_user_password(new_pw, default):
    """管理员设置默认的用户密码后，用户第一次进入时，需要再改一次用户密码，改为非默认的用户密码"""
    if not SetUpLib.locate_option(Msg.SET_USR_PW, Key.DOWN, 15):
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_USR_PW, Key.DOWN, 15)
    assert set_user_password(new_pw=default, old_pw=None, result=True, save=True)
    logging.info("Update user pw to non default...")
    assert continue_to_setup_with_pw(default, to_user=True, default=True)
    assert set_password(new_pw, default, result=True, save=True)
    assert SetUpLib.wait_boot_msgs(Msg.LOGO_SHOW)
    update_current_pw(pw_user=new_pw)
    return True


def admin_set_user_pw_default(user_pw, to_user=None, login=None):
    """管理员设置用户默认密码"""
    assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
    assert SetUpLib.locate_option(Msg.SET_USR_PW)
    assert set_user_password(new_pw=user_pw, old_pw=None, save=True, result=True)
    if login and (not to_user):
        assert continue_to_setup_with_pw(user_pw, default=True)
        return True
    if to_user:
        assert continue_to_setup_with_pw(user_pw, default=True)
        assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_USR_PW, Key.DOWN, 15)
        return True
    return True


def delele_user_pw():
    """恢复默认状态,删除用户密码"""
    try:
        BmcLib.clear_cmos()
        if not PW.USER:
            return True
        if not SetUpLib.locate_option(Msg.DEL_USER_PW, try_counts=15):
            assert BmcLib.force_reset()
            assert SetUpLib.continue_to_pw_prompt()
            SetUpLib.send_data_enter(PW.ADMIN)
            if SetUpLib.wait_msg(pw_is_expire, 1):
                SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            assert SetUpLib.move_to_bios_config()
            assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.set_option_value(Msg.DEL_PW_SUPPORT, Msg.ENABLE)
            if SetUpLib.wait_msg(pw_admin_del_cfm, 15):
                SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.locate_option(Msg.DEL_USER_PW, Key.DOWN, 15)
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, pw_user_del_cfm, 10), f'{pw_user_del_cfm} not found'
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, pw_change_saved, 10), f'{pw_change_saved} not found'
        SetUpLib.send_key(Key.ENTER, delay=1)
        assert SetUpLib.load_default_in_setup()
        assert SetUpLib.save_without_exit()
        PW.USER = None
        return True
    except Exception as e:
        logging.error(e)


# ###########################弱密码################################
def pick_a_weak_password():
    """在弱密码字典中随机挑选一个符合密码要求的弱密码"""
    pw = random.choice(PW.WEAK_PW)
    if not pw_is_valid(pw):
        return pick_a_weak_password()
    logging.info(f"Pick the weak password: {pw}")
    return pw


def get_default_weak_pw_list() -> list:
    """获取弱密码列表"""
    try:
        assert SetUpLib.enter_menu(Msg.WEAK_PW_DICT, Key.UP)
        weak_pw = SetUpLib.get_all_options(key=Key.UP, counts=PW.WEAK_CNT + len(PW.WEAK_PW), span=1)
        assert weak_pw, "Fail to get weak password list"
        weak_pw_list = [key for key, val in weak_pw.items() if not val]
        return weak_pw_list
    except Exception as e:
        logging.error(e)
        return []


def add_weak_pw_and_verify(input_pw, result, confirm_pw=None, expect=None):
    """添加弱密码列表,并检查结果 (result为False才会有提示信息)"""
    confirm_pw = input_pw if (not confirm_pw) else confirm_pw
    confirm_pw = MiscLib.regex_unescape(confirm_pw)
    expect = f"{pw_weak_short}|{pw_weak_exist}" if (not expect) else expect
    assert SetUpLib.locate_option(Msg.ADD_WEAK_PW, Key.DOWN)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.wait_msg(pw_input_weak)
    SetUpLib.send_data_enter(input_pw)
    if not result:
        logging.info("Weak password input should be invalid")
        assert SetUpLib.wait_msg(expect)
        SetUpLib.send_key(Key.ENTER)
        return True

    for i in range(10):  # Work Around for BIOS slow response after too much weak password added
        if Msg.ADD_WEAK_PW in Sut.BIOS_COM.receive_data(2048):
            break
        time.sleep(1)

    SerialLib.clean_buffer(Sut.BIOS_COM)
    assert SetUpLib.locate_option(confirm_pw, Key.UP, exact=True, try_counts=PW.WEAK_CNT+len(PW.WEAK_PW)), f"Weak password not found in weak list after set: {input_pw}"
    logging.info("Weak password input success")
    return True


def delete_weak_pw(weak_pws, span=1):
    """
    删除指定的弱密码. 如果不指定,则删除所有的弱密码
    起始位置：Security页面
    结束位置: Security页面
    """
    logging.info("Try to delete all the custom add pws in weak list")
    weak_list = [weak_pws] if isinstance(weak_pws, str) else weak_pws
    if not SetUpLib.locate_option(Msg.DEL_WEAK_PW, Key.DOWN, try_counts=15):
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu(Msg.WEAK_PW_DICT, key=Key.UP)
        assert SetUpLib.locate_option(Msg.DEL_WEAK_PW, Key.DOWN)
    delete_success = set()
    for pw in weak_list:
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(pw_input_weak)
        SetUpLib.send_data_enter(pw)
        if SetUpLib.wait_msg(pw_weak_del, timeout=10):
            SetUpLib.send_key(Key.ENTER)
            logging.info(f"Weak password : {pw} delete")
        if SetUpLib.wait_msg(pw_weak_not_exist_del, timeout=10):
            SetUpLib.send_key(Key.ENTER)
            logging.info(f"Weak password : {pw} isn't in Weak Password List")

        for k in range(PW.WEAK_CNT + len(PW.WEAK_PW)):
            SetUpLib.send_key(Key.UP)
            serial_data = Sut.BIOS_COM.read_full_buffer()
            current = Sut.BIOS_COM.option(serial_data, span=span)
            if current.name == Msg.DEL_WEAK_PW:
                logging.info(f"Weak password delete success: {pw}")
                delete_success.add(pw)
                break
            if current.name in weak_list:
                logging.info(f"Weak password remain exists after delete: {pw}")
                return False
    if delete_success == set(weak_list):
        return True


def del_default_weak_pw_and_verify():
    weak_default = get_default_weak_pw_list()
    weak_choice = random.choice(weak_default)
    assert SetUpLib.locate_option(Msg.DEL_WEAK_PW)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.wait_msg(pw_input_weak)
    SetUpLib.send_data_enter(weak_choice)
    if SetUpLib.wait_msg(pw_weak_del, timeout=10):
        SetUpLib.send_key(Key.ENTER)
        assert weak_choice not in SetUpLib.get_all_options(counts=PW.WEAK_CNT + len(PW.WEAK_PW), span=1), "Weak Password found after delete"
        logging.info(f"Weak password delete success: {weak_choice}")
        return weak_choice
    if SetUpLib.wait_msg(pw_weak_not_exist_del, timeout=10):
        SetUpLib.send_key(Key.ENTER)
        logging.info(f"Password not in weak list: {weak_choice}")


def change_pw_by_redfish(pw_type, new_pw, old_pw, result, sec_log=None, login=None):
    """
    通过Redfish设置BIOS密码，并检查BMC安全日志是否有相应记录
    :param pw_type: 密码类型 admin / user
    :param new_pw: 新密码, 若删除密码则为 ""
    :param old_pw: 旧密码, 若新添加则为 ""
    :param result: 预期的redfish修改结果, 如果密码合法为True, 密码不合法为False
    :param sec_log: 预期的需要出现的安全日志,支持1条或多条,多条时为列表
    :param login: 新密码如果可以登录成功,则login为True
    :return: True/False
    """
    def update_password():
        if pw_type == "admin":
            update_current_pw(pw_admin=new_pw)
        elif pw_type == "user":
            update_current_pw(pw_user=new_pw)

    type_support = {"user": "UserPassword", "admin": "Supervisor"}
    pw_type = pw_type.lower()
    login = result if (login is None) else login
    assert pw_type in type_support, f"Unsupported password type: {pw_type}"
    pw_path = f"/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword"
    msg = "User" if pw_type == "user" else "Supervisor"
    success = f"Security,BIOS,BMC Change {msg} password successfully"
    pw_body = {"PasswordName": type_support[pw_type], "OldPassword": old_pw, "NewPassword": new_pw}

    sut_time = BmcLib.get_bmc_datetime()
    assert Sut.BMC_RFISH.post_data(path=pw_path, data=pw_body).result, "BMC change password post failed"
    BmcLib.force_reset()
    assert SetUpLib.wait_boot_msgs(Msg.HOTKEY_PROMPT_DEL)
    # 通过读取安全日志确认是否修改成功
    security_logs = BmcWeb.BMC_WEB.get_ibmc_log(from_time=sut_time, security=True)
    log_success = PlatMisc.bmc_log_exist(success, sut_time, security=True, all_logs=security_logs)
    if result and log_success:
        update_password()
    # 新密码为空若能修改成功,则删除密码
    if log_success and (not new_pw) and (pw_type == "admin"):
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE)
        update_password()
        if sec_log == success:
            assert log_success, f"BMC security log not found: {sec_log}"
        elif sec_log:
            assert PlatMisc.bmc_log_exist(sec_log, sut_time, security=True, all_logs=security_logs)
        return True
    # 密码为非空时,登录Setup检查结果
    assert SetUpLib.boot_to_pw_prompt()
    SetUpLib.send_data_enter(new_pw)
    if login:  # 可以登录Setup
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        update_password()
    else:  # 登录Setup失败
        assert SetUpLib.wait_msg(pw_invalid)
    if sec_log == success:
        assert log_success, f"BMC security log not found: {sec_log}"
    elif sec_log:
        assert PlatMisc.bmc_log_exist(sec_log, sut_time, all_logs=security_logs)  # 检查日志
    return True


def force_login_try(pw_wrong, pw_right=None):
    for i in range(3):
        if i < 2:
            SetUpLib.send_data_enter(pw_wrong)
            assert SetUpLib.wait_msg(pw_invalid, 10)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(Msg.PW_PROMPT, 10)
            continue
        if pw_right:
            SetUpLib.send_data_enter(pw_right)
            return True
        else:
            SetUpLib.send_data_enter(pw_wrong)
            assert SetUpLib.wait_msg(pw_invalid, 10)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(pw_lock, 10)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(pw_lock, 10)
            return True
