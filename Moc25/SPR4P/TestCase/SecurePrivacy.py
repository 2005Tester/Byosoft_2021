from string import ascii_letters as letters

from SPR4P.Config import *
from SPR4P.BaseLib import *


####################################
# SecurePrivacy Test Case
# TC 3100-3111
####################################


@core.test_case(("3100", "[TC3100] Testcase_CheckPwdHistory_001", "历史密码配置选项检查"))
def Testcase_CheckPwdHistory_001():
    """
    Name:       历史密码配置选项检查
    Condition:  1、默认配置。
    Steps:      1、管理员进Setup菜单，检查历史密码选项设置范围及默认值，有结果A。
    Result:     A：设置范围5~10，默认为5。
    Remark:
    """
    value_out_of_range = [4, 11]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, Key.DOWN, 15, integer=True) == "5"
        for i in range(6, 11):
            SetUpLib.send_keys([Key.ENTER, str(i), Key.ENTER])
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        # 设置超出范围数值，使用重启后再进入验证
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, Key.DOWN, 15, integer=True) == "5"
        for j in value_out_of_range:
            SetUpLib.send_keys([Key.ENTER, str(j), Key.ENTER])
            assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, Key.DOWN, 15, integer=True) == "5"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("3101", "[TC3101] Testcase_CheckPwdHistory_002", "管理员设置历史密码测试"))
def Testcase_CheckPwdHistory_002():
    """
    Name:       管理员设置历史密码测试
    Condition:  1、已设置管理员密码a。
    Steps:      1、管理员进Setup菜单，设置历史密码次数为5，F10保存重启再次进Setup菜单检查是否生效，有结果A；
                2、依次修改管理员密码4次，此时历史密码5个，按时间顺序依次为abcde，进入Setup菜单，依次修改管理员密码为abcde，检查能否设置成功，有结果B；
                3、设置管理员密码f，此时历史密码6个，按时间顺序依次为abcdef，进入Setup菜单，依次修改管理员密码为abcdef，检查能否设置成功，有结果C。
    Result:     A：设置生效；
                B：设置失败，提示不能设置历史密码；
                C：a设置成功，bcdef均设置失败。
    Remark:     1、按时间顺序最近的5个不可设置。
    """
    # condition
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_d = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_e = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_f = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)

    try:
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "5", integer=True, save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result A
        assert SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, Key.DOWN, integer=True) == "5"
        # step 2
        for index, new_pw in enumerate([pw_b, pw_c, pw_d, pw_e]):
            logging.info(f"Set password: index [{letters[index+1]}]")
            assert PwdLib.set_admin_pw_and_verify(new_pw, PW.ADMIN)
        # result B
        for index, try_pw_1 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e]):
            logging.info(f"Set invalid password: index [{letters[index]}]")
            assert PwdLib.set_admin_password(try_pw_1, PW.ADMIN, result=False, save=False), '5 historical passwords should not be set success'
        # step 3
        logging.info(f"Set password: index [{letters[index + 1]}]")
        assert PwdLib.set_admin_pw_and_verify(pw_f, PW.ADMIN)
        # result C
        for index, try_pw_2 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Check password available: index [{letters[index]}]")
            result = True if try_pw_2 in [pw_a] else False
            assert PwdLib.set_admin_password(try_pw_2, PW.ADMIN, result=result, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("3102", "[TC3102] Testcase_CheckPwdHistory_003", "管理员设置历史密码遍历选项测试"))
def Testcase_CheckPwdHistory_003():
    """
    Name:       管理员设置历史密码遍历选项测试
    Condition:  1、已设置管理员密码a。
    Steps:      1、管理员进Setup菜单，设置历史密码次数为6，F10保存重启再次进Setup菜单检查是否生效，有结果A；
                2、依次修改管理员密码5次，此时历史密码6个，按时间顺序依次为abcdef，进入Setup菜单，依次修改管理员密码为abcdef，检查能否设置成功，有结果B；
                3、设置管理员密码g，此时历史密码6个，按时间顺序依次为abcdefg，进入Setup菜单，依次修改管理员密码为abcdefg，检查能否设置成功，有结果C；
                4、历史密码次数N遍历选项可选值，重复步骤1~3。
    Result:     A：设置生效；
                B：设置失败，提示不能设置历史密码；
                C：a设置成功，bcdefg均设置失败。
    Remark:     1、按时间顺序最近的N个不可设置。
    """

    def pw_record_test(n):
        try:
            pw_default = Msg.BIOS_PASSWORD
            pw_list = [pw_default] + [PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2) for pw in range(n)]
            # step 1
            assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, n, integer=True, save=True)
            assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
            # result A
            assert SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, Key.DOWN, integer=True) == f"{n}"
            # step 2
            for index, new_pw in enumerate(pw_list[1:n]):
                logging.info(f"Set password: index [{letters[index + 1]}]")
                assert PwdLib.set_admin_pw_and_verify(new_pw, PW.ADMIN)
            # result B
            for index, try_pw_1 in enumerate(pw_list[:n]):
                logging.info(f"Set invalid password: index [{letters[index]}]")
                assert PwdLib.set_admin_password(try_pw_1, PW.ADMIN, result=False, save=False), f'{n} historical passwords should not be set success'
            # step 3
            logging.info(f"Set password: index [{letters[index + 1]}]")
            assert PwdLib.set_admin_pw_and_verify(pw_list[n], PW.ADMIN)
            # result C
            for index, try_pw_2 in enumerate(pw_list):
                logging.info(f"Check password available: index [{letters[index]}]")
                result = True if try_pw_2 in [pw_list[0]] else False
                assert PwdLib.set_admin_password(try_pw_2, PW.ADMIN, result=result, save=False)
            return True
        except Exception as e:
            logging.error(e)
            core.capture_screen()
        finally:
            PwdLib.restore_admin_password()

    try:
        pw_rcd_range = [6, 10]  # 由于耗时比较长，暂时只测边缘值
        for set_n in pw_rcd_range:
            assert pw_record_test(set_n)

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("3103", "[TC3103] Testcase_CheckPwdHistory_004", "普通用户设置历史密码测试"))
def Testcase_CheckPwdHistory_004():
    """
    Name:       普通用户设置历史密码测试
    Condition:  1、已设置普通用户密码a。
    Steps:      1、管理员进Setup菜单，设置历史密码次数为5，F10保存重启普通用户进Setup菜单检查是否生效，有结果A；
                2、普通用户进Setup菜单依次修改自身密码4次，此时历史密码5个，按时间顺序依次为abcde，普通用户再次进入Setup菜单，依次修改自身密码为abcde，检查能否设置成功，有结果B；
                3、设置普通用户密码f，此时历史密码6个，按时间顺序依次为abcdef，普通用户进入Setup菜单，依次修改自身密码为abcdef，检查能否设置成功，有结果C。
    Result:     A：设置生效；
                B：设置失败，提示不能设置历史密码；
                C：a设置成功，bcdef均设置失败。
    Remark:     1、按时间顺序最近的5个不可设置。
    """
    pw_init = PwdLib.gen_pw(prefix="Admin@", upper=1, lower=1, symbol=1, digit=1)
    pw_a = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    pw_b = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    pw_c = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    pw_d = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    pw_e = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    pw_f = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    try:
        # condition
        assert PwdLib.init_user_password(pw_a, pw_init)
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "5", save=True, integer=True)  # 默认为5
        # result A
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        assert SetUpLib.check_grey_option({Msg.SAVE_PW_RCD_NUM: "5"}, refresh_keys=[Key.LEFT, Key.RIGHT], integer=True, span=1)
        # step 2
        for index, pw1 in enumerate([pw_b, pw_c, pw_d, pw_e]):
            logging.info(f"Set user password: index [{letters[index + 1]}]")
            assert PwdLib.set_user_pw_and_verify(pw1, PW.USER)
        # result B
        for index, pw2 in enumerate([pw_a, pw_b, pw_c ,pw_d, pw_e]):
            logging.info(f"Check password available: index [{letters[index]}]")
            assert PwdLib.set_user_password(new_pw=pw2, old_pw=PW.USER, result=False, save=False)
        # step 3
        assert PwdLib.set_user_pw_and_verify(pw_f, PW.USER)
        # result C
        for index, pw3 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Check password available: index [{letters[index]}]")
            result = True if pw3 in [pw_a] else False
            assert PwdLib.set_user_password(pw3, PW.USER, result=result, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        PwdLib.delele_user_pw()


@core.test_case(("3104", "[TC3104] Testcase_CheckPwdHistory_005", "管理员普通用户历史密码独立记录测试"))
def Testcase_CheckPwdHistory_005():
    """
    Name:       管理员普通用户历史密码独立记录测试
    Condition:  1、依次设置管理员密码abc，设置普通用户密码xyz。
    Steps:      1、管理员进Setup菜单，设置历史密码次数为5，保存重启进Setup菜单依次修改管理员密码为xyz，检查能否设置成功，有结果A；
                2、重启后普通用户进入Setup菜单，依次修改自身密码为abc，检查能否设置成功，有结果A;
                3、重启后管理员进入Setup菜单，依次修改自身密码为xyzabc，检查能否设置成功，有结果B;
                4、重启后普通用户进入Setup菜单，依次修改自身密码为abcxyz，检查能否设置成功，有结果B;
    Result:     A：设置生效（管理员与普通用户一致时无法成功）；
                B：按时间顺序最近的5个不可设置。
    Remark:     1、按时间顺序最近的N个不可设置。
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_c = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)

    pw_init = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_x = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_y = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_z = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)

    try:
        # condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        for index, admin_pw1 in enumerate([pw_b, pw_c]):  # admin:abc
            logging.info(f"Set admin password: index [{letters[index + 1]}]")
            assert PwdLib.set_admin_pw_and_verify(admin_pw1, PW.ADMIN)
        assert PwdLib.init_user_password(pw_x, pw_init)
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        for index, user_pw1 in enumerate([pw_y, pw_z]):  # user:xyz
            logging.info(f"Set user password: index [{'xyz'[index + 1]}]")
            assert PwdLib.set_user_pw_and_verify(user_pw1, PW.USER)
        # step 1
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_user=True)
        if SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, integer=True) != "5":
            assert BmcLib.force_reset()
            assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_user=True)
            assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "5", save=True, integer=True)
        # result A
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW, Key.DOWN)
        for index, admin_pw2 in enumerate([pw_x, pw_y, pw_z]):
            logging.info(f"Set admin password: index [{'xyz'[index]}]")
            if admin_pw2 in [PW.USER]:  # user:z
                assert PwdLib.set_admin_password(admin_pw2, PW.ADMIN, result=False, save=False)
            else:
                assert PwdLib.set_admin_pw_and_verify(admin_pw2, PW.ADMIN)  # admin:abcxy
        # step 2
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        # result A
        for index, user_pw2 in enumerate([pw_a, pw_b, pw_c]):
            logging.info(f"Set user password: index [{letters[index]}]")
            if user_pw2 in [PW.ADMIN]:  # admin:y
                assert PwdLib.set_user_password(user_pw2, PW.USER, result=False, save=False)
            else:
                assert PwdLib.set_user_pw_and_verify(user_pw2, PW.USER)  # user:xyzabc
        # step 3
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        # result B
        for index, admin_pw3 in enumerate([pw_x, pw_y, pw_z, pw_a, pw_b, pw_c]):  # admin:abcxy, user:b
            logging.info(f"Check admin password available: index [{'xyzabc'[index]}]")
            result = True if admin_pw3 in [pw_z] else False
            assert PwdLib.set_admin_password(admin_pw3, PW.ADMIN, result=result, save=False)
        # step 4
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        # result A
        for index, user_pw3 in enumerate([pw_a, pw_b, pw_c, pw_x, pw_y, pw_z]):  # user:xyzabc, admin:y
            logging.info(f"Check user password available: index [{'abcxyz'[index]}]")
            result = True if user_pw3 in [pw_x] else False
            assert PwdLib.set_user_password(user_pw3, PW.USER, result=result, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()
        PwdLib.restore_admin_password()


@core.test_case(("3105", "[TC3105] Testcase_CheckPwdHistory_006", "历史密码选项保存重启生效"))
def Testcase_CheckPwdHistory_006():
    """
    Name:       历史密码选项保存重启生效
    Condition:  1、依次设置管理员密码abcde。
    Steps:      1、管理员进Setup菜单，设置历史密码次数为5，保存重启进Setup菜单依次修改管理员密码为abcde，检查能否设置成功，有结果A；
                2、设置管理员密码f，此时历史密码6个，按时间顺序依次为abcdef，进入Setup菜单，依次修改管理员密码为abcdef，检查能否设置成功，有结果B;
                3、设置历史密码次数为6，设置后再依次修改管理员密码为abcdef，检查能否设置成功，有结果B;
                4、F10保存重启后再次进Setup菜单依次修改管理员密码为abcdef，检查能否设置成功，有结果A;
    Result:     A：设置失败，提示不能设置历史密码；
                B：a设置成功，bcdefg均设置失败。
    Remark:
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_d = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_e = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_f = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)

    def check_result_b():
        """Password won't be changed in this step"""
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW, Key.DOWN, 20)
        for index, try_pw_2 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Check password available: index [{letters[index]}]")
            result = True if try_pw_2 in [pw_a] else False
            assert PwdLib.set_admin_password(try_pw_2, PW.ADMIN, result=result, save=False)
        return True

    try:
        # condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        for index, new_pw in enumerate([pw_b, pw_c, pw_d, pw_e]):
            logging.info(f"Set password: index [{letters[index + 1]}]")
            assert PwdLib.set_admin_pw_and_verify(new_pw, PW.ADMIN)
        # step 1
        if SetUpLib.get_option_value(Msg.SAVE_PW_RCD_NUM, Key.DOWN, integer=True) != "5":
            assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "5", integer=True, save=True)
            assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result A
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW, Key.DOWN, 20)
        for index, try_pw_1 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e]):
            logging.info(f"Set invalid password: index [{letters[index]}]")
            assert PwdLib.set_admin_password(try_pw_1, PW.ADMIN, result=False, save=False), '5 historical passwords should not be set success'
        # step 2
        logging.info(f"Set password: index [{letters[index + 1]}]")
        assert PwdLib.set_admin_pw_and_verify(pw_f, PW.ADMIN)
        # result B
        assert check_result_b()
        # step 3
        assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "6", integer=True, save=False)
        # result B
        assert check_result_b()
        # step 4
        assert BmcLib.force_reset()  # don't save password of try in last step
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "6", integer=True, save=True)  # save config here
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        # result A
        for index, try_pw_1 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Set invalid password: index [{letters[index]}]")
            assert PwdLib.set_admin_password(try_pw_1, PW.ADMIN, result=False, save=False), '5 historical passwords should not be set success'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("3106", "[TC3106] Testcase_CheckPwdHistory_007", "历史密码选项变更测试"))
def Testcase_CheckPwdHistory_007():
    """
    Name:       历史密码选项变更测试
    Condition:  1、依次设置管理员密码abcdef。
    Steps:      1、管理员进Setup菜单，设置历史密码次数为6，保存重启进Setup菜单依次修改管理员密码为abcdef，检查能否设置成功，有结果A；
                2、设置管理员密码g，此时历史密码6个，按时间顺序依次为abcdefg，进入Setup菜单，依次修改管理员密码为abcdefg，检查能否设置成功，有结果B;
                3、设置历史密码次数为5，F10保存重启后再次进Setup菜单依次修改管理员密码为abcdefg，检查能否设置成功，有结果A;
    Result:     A：设置失败，提示不能设置历史密码；
                B：a设置成功，bcdefg均设置失败;
                C：ab设置成功，cdefg均设置失败;
    Remark:
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_d = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_e = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_f = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)
    pw_g = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2)

    try:
        # condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        for index, new_pw in enumerate([pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Set password: index [{letters[index + 1]}]")
            assert PwdLib.set_admin_pw_and_verify(new_pw, PW.ADMIN)
        # step 1
        assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "6", integer=True, save=True)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        # result A
        for index, try_pw_1 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Set invalid password: index [{letters[index]}]")
            assert PwdLib.set_admin_password(try_pw_1, PW.ADMIN, result=False, save=False), '5 historical passwords ' \
                                                                                            'should not be set success'
        # step 2
        logging.info(f"Set password: index [{letters[index + 1]}]")
        assert PwdLib.set_admin_pw_and_verify(pw_g, PW.ADMIN)
        # result B
        for index, try_pw_2 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f, pw_g]):
            logging.info(f"Check password available: index [{letters[index]}]")
            result = True if try_pw_2 in [pw_a] else False
            assert PwdLib.set_admin_password(try_pw_2, PW.ADMIN, result=result, save=False)
        # step 3
        assert BmcLib.force_reset()  # don't save password of try in last step
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        assert SetUpLib.set_option_value(Msg.SAVE_PW_RCD_NUM, "5", integer=True, save=True)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        # result C
        for index, try_pw_3 in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f, pw_g]):
            logging.info(f"Check password available: index [{letters[index]}]")
            result = True if try_pw_3 in [pw_a, pw_b] else False
            assert PwdLib.set_admin_password(try_pw_3, PW.ADMIN, result=result, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("3107", "[TC3107] Testcase_CheckPwdDiff_001", "管理员新旧密码一个字符位不同"))
def Testcase_CheckPwdDiff_001():
    """
    Name:       管理员新旧密码一个字符位不同
    Condition:  1、已设置管理员密码，如Admin@9000
    Steps:      1、管理员进Setup菜单，将旧密码的一个字母大小写替换，设置为新密码如admin@9000，检查是否设置成功，有结果A；
                2、设置自身密码与旧密码一个字符位不一致，如Admin@8000，检查是否设置成功，有结果A；
    Result:     A：设置失败，提示不满足复杂度要求。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix=Msg.BIOS_PASSWORD[0].swapcase(), suffix=Msg.BIOS_PASSWORD[1:], total=len(Msg.BIOS_PASSWORD))
    pw_b = PwdLib.gen_pw(prefix=Msg.BIOS_PASSWORD[:-1], digit=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW, Key.DOWN, 20)
        for try_pw in [pw_a, pw_b]:
            assert PwdLib.set_admin_password(try_pw, PW.ADMIN, result=False, save=False)  # 设置失败，提示不满足复杂度要求。
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)  # 使用默认密码进setup
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("3108", "[TC3108] Testcase_CheckPwdDiff_002", "管理员新旧密码两个字符位不同"))
def Testcase_CheckPwdDiff_002():
    """
    Name:       管理员新旧密码两个字符位不同
    Condition:  1、已设置管理员密码，如Admin@9000
    Steps:      1、管理员进Setup菜单，将旧密码的非连续的两个字符位修改后设置为新密码如Bdmin@8000，检查是否设置成功，有结果A；
                2、将旧密码的连续的两个字符位修改后设置为新密码如Admin@9011，检查是否设置成功，有结果A；
    Result:     A：设置成功，提示保存重启生效。
    Remark:
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix=f"{pw_a[0].swapcase()}{pw_a[1]}{pw_a[2].swapcase()}{pw_a[3:]}", total=len(Msg.BIOS_PASSWORD))
    pw_c = PwdLib.gen_pw(prefix=pw_a[:-2], digit=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        for set_pw in [pw_b, pw_c]:
            assert PwdLib.set_admin_pw_and_verify(set_pw, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("3109", "[TC3109] Testcase_CheckPwdDiff_003", "普通用户新旧密码一个字符位不同"))
def Testcase_CheckPwdDiff_003():
    """
    Name:       普通用户新旧密码一个字符位不同
    Condition:  1、已设置普通用户密码，如Admin@9000
    Steps:      1、普通用户进Setup菜单，将旧密码的一个字母大小写替换，设置为新密码如admin@9000，检查是否设置成功，有结果A；
                2、设置自身密码与旧密码一个字符位不一致，如Admin@8000，检查是否设置成功，有结果A；
    Result:     A：设置失败，提示不满足复杂度要求。
    Remark:
    """
    pw_init = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_b = PwdLib.gen_pw(prefix=pw_a[0].swapcase(), suffix=pw_a[1:], total=len(pw_a))
    pw_c = PwdLib.gen_pw(prefix=pw_a[0:6], suffix=pw_a[7:], total=len(pw_a))

    try:
        # condition
        assert PwdLib.init_user_password(pw_a, pw_init)
        # step 1,2
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        # result A
        for index, user_pw1 in enumerate([pw_b, pw_c]):
            logging.info(f"Check admin password available: index [{'bc'[index]}]")
            assert PwdLib.set_admin_password(user_pw1, PW.USER, result=False, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("3110", "[TC3110] Testcase_CheckPwdDiff_004", "普通用户新旧密码两个字符位不同"))
def Testcase_CheckPwdDiff_004():
    """
    Name:       普通用户新旧密码两个字符位不同
    Condition:  1、已设置普通用户密码，如Admin@9000
    Steps:      1、普通用户进Setup菜单，将旧密码的非连续的两个字符位修改后设置为新密码如Bdmin@8000，检查是否设置成功，有结果A；
                2、将旧密码的连续的两个字符位修改后设置为新密码如Admin@9011，检查是否设置成功，有结果A；
    Result:     A：设置成功，提示保存重启生效。
    Remark:
    """
    pw_init = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, lower=2, upper=2)
    pw_b = PwdLib.gen_pw(prefix="admim@", suffix=pw_a[6:], total=len(pw_a))
    pw_c = PwdLib.gen_pw(prefix="Admin@", suffix=pw_a[8:], digit=1, total=len(pw_a))

    try:
        # condition
        assert PwdLib.init_user_password(pw_a, pw_init)
        # step 1,2
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        # result A
        for index, user_pw1 in enumerate([pw_b, pw_c]):
            logging.info(f"Check admin password available: index [{'bc'[index]}]")
            assert PwdLib.set_user_pw_and_verify(user_pw1, PW.USER)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("3111", "[TC3111] Testcase_CheckPwdDiff_005", "新旧密码字符相同位置不同"))
def Testcase_CheckPwdDiff_005():
    """
    Name:       新旧密码字符相同位置不同
    Condition:  1、已设置管理员密码，如Admin@9000
    Steps:      1、管理员进Setup菜单，将旧密码的字符顺序改变后设置为新密码如9000@Admin，检查是否设置成功，有结果A；
    Result:     A：设置成功，提示保存重启生效。
    Remark:
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix=f"{pw_a[6:]}{pw_a[5]}{pw_a[0:5]}", total=len(Msg.BIOS_PASSWORD))

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_b, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()

