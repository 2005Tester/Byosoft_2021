import logging
import random
import string
import time
from ByoTool.BaseLib import SetUpLib, BmcLib
from ByoTool.Config.PlatConfig import Key



pw_enter_old = 'Please type in your password'
pw_enter_new = 'Please type in your new password'
pw_cfm_new = 'Please confirm your new password'
pw_set_suc = 'Password Setting Successfully'
pw_incorrect = 'Incorrect Password|Incorrect password'
pw_limit = 'Fatal Error... System Halted'
pw_expire='Password expired'
pw_is_history='Password has been used by the latest 5 times'
pw_is_same = 'Password Rule Error'
pw_be_diff = 'The new password should be different'
pw_short = "Please enter enough characters"
pw_simple = "Passwords need to contain upper and lower case letters|Passwords can contain upper and lower case letters"
pw_not_same = "Passwords are not the same"
pw_del_suc = "Password deleted succeeded"
pw_invalid='Invalid Password'
pw_limit_post = 'Fatal Error... System Halted'



class PW:
    MIN = 8
    MAX = 20

    ADMIN = None
    USER = None

    HISTORY = set()


class HDD_PW:
    MIN = 8
    MAX = 20

    ADMIN = None
    USER = None
    ADMIN_ANOTHER = None



def gen_pw(digit=0, upper=0, lower=0, symbol=0, total=None, prefix="", suffix=""):
    """密码生成器，按规则生成密码，并且避免使用旧密码，防止Case之间互相影响"""
    if total == 0:
        logging.info('Password Type: [Empty] -> ""')
        return ""

    digit_strs = string.digits  # 数字
    lower_strs = string.ascii_lowercase.replace("x", "")  # 小写字母
    upper_strs = string.ascii_uppercase  # 大写字母
    letter_strs = string.ascii_letters.replace("x", "")  # 大小写字母
    symbol_strs = string.punctuation  # 特殊字符加空格

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

    if password in PW.HISTORY:
        return gen_pw(digit, upper, lower, symbol, total, prefix, suffix)

    pw_info = f'{prefix}{didit_info}{upper_info}{lower_info}{symbol_info}{random_info}{suffix}'
    logging.info(f"Password Type: {pw_info} -> {password}")
    PW.HISTORY.add(password)
    return password




def update_current_pw(pw_admin: str = None, pw_user: str = None, hdd_pw_admin: str = None, hdd_pw_user: str = None,
                      hdd_pw_admin_another: str = None):
    if isinstance(pw_admin, str):
        valid_pw_admin = pw_admin[:PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current Admin Password -> {valid_pw_admin}")
        PW.ADMIN = valid_pw_admin
    if isinstance(pw_user, str):
        valid_pw_user = pw_user[:PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current User Password -> {valid_pw_user}")
        PW.USER = valid_pw_user
    if isinstance(hdd_pw_admin, str):
        valid_hdd_pw_admin = hdd_pw_admin[:HDD_PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current HDD Admin Password -> {valid_hdd_pw_admin}")
        HDD_PW.ADMIN = valid_hdd_pw_admin
    if isinstance(hdd_pw_user, str):
        valid_hdd_pw_user = hdd_pw_user[:HDD_PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current HDD User Password -> {valid_hdd_pw_user}")
        HDD_PW.USER = valid_hdd_pw_user
    if isinstance(hdd_pw_admin_another, str):
        valid_hdd_pw_admin_another = hdd_pw_admin_another[:HDD_PW.MAX]  # 密码超过最大长度后会输不进去,只有前16位可以正常修改成功
        logging.info(f"Current HDD Admin Password -> {valid_hdd_pw_admin_another}")
        HDD_PW.ADMIN_ANOTHER = valid_hdd_pw_admin_another

def set_password(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    """
    result为True, 预期设置成功
    result为False, 预期设置失败
    result为None, 预期旧密码输入错误
    expect: 预期的消息弹窗(第一行)
    """
    confirm_pw = new_pw if confirm_pw == None else confirm_pw
    try:
        SetUpLib.send_key(Key.ENTER)
        if old_pw:
            assert SetUpLib.wait_message(pw_enter_old, 5), '{} not found'.format(pw_enter_old)
            SetUpLib.send_data_enter(old_pw)
            if result is None:
                expect = expect if expect else pw_incorrect
                assert SetUpLib.wait_message(expect, 5), f'{expect} not found'
                logging.info("Password input is invalid")
                SetUpLib.send_key(Key.ENTER)
                return True
            if expect == pw_expire:
                assert SetUpLib.wait_message(expect, 5),f'{expect} not found'
                logging.info('Password expired')
                SetUpLib.send_keys([Key.ENTER,Key.ESC])
                return True
        assert SetUpLib.wait_message(pw_enter_new, 5), '{} not found'.format(pw_enter_new)
        SetUpLib.send_data_enter(new_pw)
        if expect == pw_short:
            assert SetUpLib.wait_message(pw_short), f'{pw_short} not found'
            SetUpLib.send_key(Key.ENTER)
            return True
        assert SetUpLib.wait_message(pw_cfm_new, 5), '{} not found'.format(pw_cfm_new)
        SetUpLib.send_data_enter(confirm_pw)
        if result:
            assert SetUpLib.wait_message(pw_set_suc, 15), '{} not found'.format(pw_set_suc)
            logging.info(f"Password can be set success: {new_pw}")
            SetUpLib.send_keys([Key.ENTER])
        else:
            expect = expect if expect else f"{pw_is_same}|{pw_be_diff}|{pw_short}|{pw_invalid}|{pw_simple}|{pw_not_same}"
            assert SetUpLib.wait_message(expect), f'Msg not found: "{pw_is_same}" or "{pw_be_diff}"'
            SetUpLib.send_keys([Key.ENTER])
            logging.info(f"Password can not be set: {new_pw}(invalid)")
        if result:
            logging.info("Password changed: {0} => {1}".format(old_pw, new_pw))
        return True
    except Exception as e:
        logging.error(e)



def set_admin(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    assert set_password(new_pw, result, old_pw, expect, confirm_pw)
    time.sleep(1)
    if result:
        update_current_pw(pw_admin=new_pw)
    return True


def set_user(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    assert set_password(new_pw, result, old_pw, expect, confirm_pw)
    time.sleep(1)
    if result:
        update_current_pw(pw_user=new_pw)
    return True


def del_psw(pw, result, expect=None):
    try:
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(pw_enter_old, 5), '{} not found'.format(pw_enter_old)
        SetUpLib.send_data_enter(pw)
        if result:
            assert SetUpLib.wait_message(pw_enter_new, 5), '{} not found'.format(pw_enter_new)
            SetUpLib.send_keys([Key.ENTER,Key.ENTER])
            assert SetUpLib.wait_message(pw_del_suc, 5), '{} not found'.format(pw_del_suc)
            logging.info(f"Password delete success: {pw}")
            SetUpLib.send_keys([Key.ENTER])
        else:
            expect = expect if expect else f"{pw_invalid}"
            assert SetUpLib.wait_message(expect, 5), f'Msg not found:{expect}'
            SetUpLib.send_keys([Key.ENTER])
            logging.info(f"Password can not be deleted: {pw}(invalid)")
        if result:

            logging.info("Password changed: {0} => {1}".format(pw, 'None'))
        return True
    except Exception as e:
        logging.error(e)


def del_admin(pw, result, expect=None):
    assert del_psw(pw,result,expect)
    time.sleep(1)
    if result:
        PW.ADMIN = None
    return True


def del_user(pw, result, expect=None):
    assert del_psw(pw,result,expect)
    time.sleep(1)
    if result:
        PW.USER = None
    return True


hdd_pw_enter_old = 'Enter Current Password'  # 修改密码要求输入当前密码提示信息
hdd_pw_invalid = 'Invalid Password'  # SetUp输错密码提示信息
hdd_pw_enter_new = 'Enter New Password'  # 设置密码时提示信息
hdd_pw_set_suc = 'Changes have been saved'  # 密码设置成功提示信息
hdd_pw_short = 'Invalid Password Length'  # 小于最小长度提示信息
hdd_pw_long = 'Invalid Password Length'  # 大于最大长度提示信息
hdd_pw_not_same = 'Passwords are not the same'  # 新密码与确认密码输入不一致提示信息
hdd_pw_simple = 'Password complexity is invalid|Invalid Password Charater Type'  # 不满足复杂度要求提示信息
hdd_pw_enter_psw = 'Enter current HDD (?:Admin )*Password|Enter Hdd Password User Password'  # 删除密码要求输入当前密码提示信息
hdd_pw_del_suc = 'Password have been cleared|Changes have been saved'  # SetUp删除硬盘密码提示信息
hdd_pw_limit = 'The number of password attempts has reached the limit'  # SetUp输错密码三次提示信息
hdd_pw_incorrect = 'Incorrect password'  # POST输错密码提示信息
hdd_pw_limit_post = 'The number of incorrect password entries has reached the upper limit.|Please restart and enter the correct password to unlock the locked HDD'  # POST输错密码三次提示信息
hdd_pw_escape = 'Password input cancelled, Drive is still locked'  # POST ESC跳过密码提示信息
hdd_pw_frozen = 'Device is frozen or locked'

def set_hdd_password(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    """
        result为True, 预期设置成功
        result为False, 预期设置失败
        result为None, 预期旧密码输入错误
        expect: 预期的消息弹窗(第一行)
        """
    confirm_pw = new_pw if confirm_pw == None else confirm_pw
    try:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        if old_pw:
            assert SetUpLib.wait_message(hdd_pw_enter_old, 5), '{} not found'.format(hdd_pw_enter_old)
            SetUpLib.send_data_enter(old_pw)
            if result is None:
                expect = expect if expect else hdd_pw_invalid
                assert SetUpLib.wait_message(expect, 5)
                logging.info("Password input is invalid")
                SetUpLib.send_key(Key.ENTER)
                return True
        else:
            assert SetUpLib.wait_message(hdd_pw_enter_new, 5), '{} not found'.format(hdd_pw_enter_new)
        SetUpLib.send_data_enter(new_pw)
        time.sleep(1)
        SetUpLib.send_data_enter(confirm_pw)
        if result:
            assert SetUpLib.wait_message(hdd_pw_set_suc, 5), '{} not found'.format(hdd_pw_set_suc)
            logging.info(f"Password can be set success: {new_pw}")
            SetUpLib.send_keys([Key.ENTER])
        else:
            expect = expect if expect else f"{hdd_pw_long}|{hdd_pw_short}|{hdd_pw_invalid}|{hdd_pw_simple}|{hdd_pw_not_same}"
            assert SetUpLib.wait_message(expect, 5), f'Msg not found:{expect}'
            SetUpLib.send_keys([Key.ENTER])
            logging.info(f"Password can not be set: {new_pw}(invalid)")
        if result:
            logging.info("Password changed: {0} => {1}".format(old_pw, new_pw))
        return True
    except Exception as e:
        logging.error(e)


def set_hdd_admin(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    assert set_hdd_password(new_pw, result, old_pw, expect, confirm_pw)
    time.sleep(1)
    if result:
        update_current_pw(hdd_pw_admin=new_pw)
    return True


def set_hdd_admin_another(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    assert set_hdd_password(new_pw, result, old_pw, expect, confirm_pw)
    time.sleep(1)
    if result:
        update_current_pw(hdd_pw_admin_another=new_pw)
    return True


def set_hdd_user(new_pw, result, old_pw=None, expect=None, confirm_pw=None):
    assert set_hdd_password(new_pw, result, old_pw, expect, confirm_pw)
    time.sleep(1)
    if result:
        update_current_pw(hdd_pw_user=new_pw)
    return True


def del_hdd_psw(hdd_pw, result, expect=None):
    try:
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_message(hdd_pw_enter_psw, 5), '{} not found'.format(hdd_pw_enter_psw)
        SetUpLib.send_data_enter(hdd_pw)
        if result:
            assert SetUpLib.wait_message(hdd_pw_del_suc, 5), '{} not found'.format(hdd_pw_del_suc)
            logging.info(f"Password delete success: {hdd_pw}")
            SetUpLib.send_keys([Key.ENTER])
        else:
            expect = expect if expect else f"{hdd_pw_invalid}"
            assert SetUpLib.wait_message(expect, 5), f'Msg not found:{expect}'
            SetUpLib.send_keys([Key.ENTER])
            logging.info(f"Password can not be deleted: {hdd_pw}(invalid)")
        if result:
            HDD_PW.ADMIN = None if hdd_pw == HDD_PW.ADMIN else HDD_PW.ADMIN
            HDD_PW.ADMIN_ANOTHER = None if hdd_pw == HDD_PW.ADMIN_ANOTHER else HDD_PW.ADMIN_ANOTHER
            logging.info("Password changed: {0} => {1}".format(hdd_pw, 'None'))
        time.sleep(1)
        return True
    except Exception as e:
        logging.error(e)


def check_psw_post(pw=None, expect=None, timeout=10, key=None):
    try:
        if key:
            SetUpLib.send_key(key)
        else:
            SetUpLib.send_data_enter(pw)
        expect = expect if expect != None else f'{hdd_pw_incorrect}|{pw_invalid}'
        assert SetUpLib.wait_message(expect, timeout), f'Msg not found:{expect}'
        if expect in [hdd_pw_incorrect, hdd_pw_limit_post, hdd_pw_escape,pw_limit_post,pw_expire]:
            SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        return True
    except Exception as e:
        logging.error(e)
