import random
from string import ascii_letters as letters

from SPR4P.Config import *
from SPR4P.BaseLib import *


####################################
# Security Test Case
# TC 2300-2426
####################################


@core.test_case(("2300", "[TC2300] Testcase_TPM_002", "BIOS Setup菜单提供TPM相关信息测试"))
@mark_skip_if(not Sys.TPM, reason="TPM not installed")
def Testcase_TPM_002():
    """
    Name:       BIOS Setup菜单提供TPM相关信息测试
    Condition:  单板已插TPM卡
    Steps:      1、启动进入BIOS Setup菜单，在Security界面查看TPM在位、类型、版本、自检、使能状态等信息，有结果A；
                2、配置TPM选项，有结果B。
    Result:     A：TPM在位、类型、版本、自检状态、使能状态正确；
                B：选项可正常配置。
    Remark:
    """
    tpm = SutConfig.Sys.TPM
    tpm_values = ["No Action", "TPM2 ClearControl(NO) + Clear", "TPM2 PCR_Allocate(Algorithm IDs)", "TPM2 ChangeEPS", "TCG2 LogAllDigests"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.TPM_DEV, integer=None) == f"{tpm['Protocol']} {tpm['Version']}", "tpm protocol"
        assert SetUpLib.get_option_value(Msg.TPM_ACTIVE, integer=None) == f"SHA256, SM3_256", "tpm active"
        assert SetUpLib.get_option_value(Msg.TPM_SUPPORT, integer=None) == f"{', '.join(tpm['HashAlgo'])}", "tpm support"
        assert SetUpLib.get_option_value(Msg.TPM2_OPERATE) == tpm_values[0], "tpm default"
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.TPM2_OPERATE), tpm_values), "tpm values"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("2301", "[TC2301] Testcase_TPM_005", "BIOS默认打开TPM功能测试"))
@mark_skip_if(not Sys.TPM, reason="TPM not installed")
def Testcase_TPM_005():
    """
    Name:       BIOS默认打开TPM功能测试
    Condition:  单板已插TPM卡
    Steps:      1、单板上电进Setup，按F9恢复默认配置，查看TPM功能选项是否默认打开，有结果A；
                2、遍历兼容性规格内的TPM型号，重复步骤1。
    Result:     A：TPM功能选项默认打开。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.TPM_ACTIVE, integer=None) == f"SHA256, SM3_256", "tpm active"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("2302", "[TC2302] Testcase_TPM_007", "BMC查询TPM启动时使能状态信息测试"))
@mark_skip_if(not Sys.TPM, reason="TPM not installed")
def Testcase_TPM_007():
    """
    Name:       BMC查询TPM启动时使能状态信息测试
    Condition:  单板已插TPM卡
    Steps:      1、TPM功能active时，BMC下查询TPM状态信息，有结果A；
                2、Setup菜单下将TPM功能inactive，BMC下查询TPM状态信息，有结果A；
                3、遍历兼容性规格内的TPM型号。
    Result:
                A：BMC下正确查询到TPM状态信息。
    Remark:
    """
    try:
        tpm = BmcWeb.BMC_WEB.get_tpm_info()
        fail_items = {}
        for k, v in SutConfig.Sys.TPM.items():
            if (k in tpm) and (tpm.get(k) != v):
                logging.error(f"TPM {k} mismatch with config: {v}")
                fail_items[k] = v
        assert not fail_items, f"TPM info mismatch with config"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2303", "[TC2303] Testcase_TPM_008", "BMC查询TPM在位信息测试"))
def Testcase_TPM_008():
    """
    Name:       BMC查询TPM在位信息测试
    Condition:  单板已插TPM卡
    Steps:      1、BMC Web下查询TPM芯片是否在位，有结果A；
                2、BMC命令行执行ipmcget -d v查询TPM芯片是否在位，有结果A；
                3、拿掉TPM芯片，BMC Web下查询TPM是否在位，有结果B；
                4、BMC命令行执行ipmcget -d v查询TPM芯片是否在位，有结果B；
                5、遍历兼容性规格内的TPM型号。
    Result:     A：TPM插上时BMC下查询到TPM在位；
                B：TPM拿下时BMC下查询到TPM不在位。
    Remark:
    """
    try:
        if not SutConfig.Sys.TPM:
            assert not BmcWeb.BMC_WEB.get_tpm_info()
            assert not BmcLib.get_tpm_info()
        else:
            assert BmcWeb.BMC_WEB.get_tpm_info()
            assert BmcLib.get_tpm_info()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2304", "[TC2304] Testcase_TPM_009", "TPM加密算法测试"))
@mark_skip_if(not Sys.TPM, reason="TPM not installed")
def Testcase_TPM_009():
    """
    Name:       TPM加密算法测试
    Condition:  单板已插TPM卡
    Steps:      1、进入Setup Security菜单；
                2、菜单中查询支持的加密算法，有结果A。
    Result:     A：TPM2.0采用SHA1和SHA256两种算法；
                TPM1.2只支持SHA1。（芯片本身不支持复杂的算法）
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.TPM_ACTIVE, integer=None) == f"SHA256, SM3_256", "tpm active"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("2305", "[TC2305] Testcase_TPM_015", "BIOS上报TCM信息到BMC测试"))
# def Testcase_TPM_015():
#     """
#     Name:       BIOS上报TCM信息到BMC测试
#     Condition:  单板已插TCM卡
#     Steps:      1、单板上电启动，BMC Web界面查看TCM型号、协议版本、FW版本、自检结果等信息，有结果A。
#     Result:     A：Web界面显示型号为TCM，其他信息均为NA。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2306", "[TC2306] Testcase_TPM_016", "BIOS初始化TCM芯片测试"))
# def Testcase_TPM_016():
#     """
#     Name:       BIOS初始化TCM芯片测试
#     Condition:  单板已插TCM卡
#     Steps:      1、单板上电启动；
#                 2、Setup菜单里查看TCM芯片信息，有结果A。
#     Result:     A：Setup菜单里显示TCM芯片在位，TCM相关信息正确。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2307", "[TC2307] Testcase_SecurityBoot_001", "Legacy模式隐藏Secure Boot界面"))
def Testcase_SecurityBoot_001():
    """
    Name:       Legacy模式隐藏Secure Boot界面
    Condition:  1、Legacy模式。
    Steps:      1、启动进Front page界面，查看是否存在Secure Boot相关菜单，有结果A。
    Result:     A：无Secure Boot菜单。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
        assert BmcLib.set_boot_mode("Legacy", once=True)
        assert SetUpLib.boot_to_setup()
        assert not SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.set_boot_mode("uefi", once=False)


@core.test_case(("2308", "[TC2308] Testcase_BiosPasswordSecurity_002", "设置密码长度测试_密码长度小于最少字符数(8)"))
def Testcase_BiosPasswordSecurity_002():
    """
    Name:       设置密码长度测试_密码长度小于最少字符数(8)
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码长度小于最少字符数要求（8），如长度为5；
                3、检查密码修改是否成功，有结果A。
    Result:     A：提示不满足复杂度要求，修改失败。
    Remark:
    """
    pw_a = PwdLib.gen_pw(total=PW.MIN - 1, digit=1, upper=1, lower=1, symbol=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_short)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2309", "[TC2309] Testcase_BiosPasswordSecurity_003", "设置密码长度测试_密码长度等于最少字符数(8)"))
def Testcase_BiosPasswordSecurity_003():
    """
    Name:       设置密码长度测试_密码长度等于最少字符数(8)
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码长度等于最少字符数要求（8），满足其他复杂度要求；
                3、检查密码修改是否成功，有结果A。
    Result:     A：满足复杂度要求，修改成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(total=PW.MIN, digit=1, upper=1, lower=1, symbol=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_pw_and_verify(pw_a, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2310", "[TC2310] Testcase_BiosPasswordSecurity_004", "设置密码长度测试_密码长度大于最少字符数(8)"))
def Testcase_BiosPasswordSecurity_004():
    """
    Name:       设置密码长度测试_密码长度大于最少字符数(8)
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码长度大于最少字符数要求（8），如长度为9，满足其他复杂度要求；
                3、检查密码修改是否成功，有结果A。
    Result:     A：满足复杂度要求，修改成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(total=PW.MIN + 1, digit=1, upper=1, lower=1, symbol=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_pw_and_verify(pw_a, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2311", "[TC2311] Testcase_BiosPasswordSecurity_005", "设置密码长度测试_密码长度等于最大字符数"))
def Testcase_BiosPasswordSecurity_005():
    """
    Name:       设置密码长度测试_密码长度等于最大字符数
    Condition:  1、已明确方案设计最大密码字符数要求，假定长度为a；
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码长度等于最大字符数要求a，满足其他复杂度要求；
                3、检查密码修改是否成功，有结果A。
    Result:     A：满足复杂度要求，修改成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(total=PW.MAX, digit=1, upper=1, lower=1, symbol=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_pw_and_verify(pw_a, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2312", "[TC2312] Testcase_BiosPasswordSecurity_006", "设置密码长度测试_密码长度大于最大字符数"))
def Testcase_BiosPasswordSecurity_006():
    """
    Name:       设置密码长度测试_密码长度大于最大字符数
    Condition:  1、已明确方案设计最大密码字符数要求，假定长度为a；
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码长度超出最大字符数要求a，满足其他复杂度要求；
                3、检查密码修改是否成功，有结果A。
    Result:     A：不支持输入超过a个字符。
    Remark:
    """
    pw_a = PwdLib.gen_pw(total=PW.MAX + 1, digit=1, upper=1, lower=1, symbol=1)
    valid_pw = pw_a[:PW.MAX]

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=True, save=True)
        assert PwdLib.check_pw_length_and_hidden(pw_a, length=PW.MAX)
        assert PwdLib.continue_to_setup_with_pw(valid_pw)
        PwdLib.update_current_pw(valid_pw)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2313", "[TC2313] Testcase_BiosPasswordSecurity_007", "设置密码字符类型测试_1种字符类型密码"))
def Testcase_BiosPasswordSecurity_007():
    """
    Name:       设置密码字符类型测试_1种字符类型密码
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码为1种字符类型，尝试各种组合（共4种组合）；
                3、检查密码修改是否成功，有结果A。
    Result:     A：提示不满足复杂度要求，修改失败。
    Remark:     1、密码必须包含大写字母、小写字母、数字、特殊字符四种中至少三种字符的组合（其中特殊字符必须）
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN)
    pw_b = PwdLib.gen_pw(upper=PW.MIN)
    pw_c = PwdLib.gen_pw(lower=PW.MIN)
    pw_d = PwdLib.gen_pw(symbol=PW.MIN)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for index, pw in enumerate([pw_a, pw_b, pw_c, pw_d]):
            logging.info(f"Check admin password available: index [{letters[index]}]")
            assert PwdLib.set_admin_password(pw, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_simple)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2314", "[TC2314] Testcase_BiosPasswordSecurity_008", "设置密码字符类型测试_2种字符类型密码"))
def Testcase_BiosPasswordSecurity_008():
    """
    Name:       设置密码字符类型测试_2种字符类型密码
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码为2种字符类型，尝试各种组合（共6种组合）；
                3、检查密码修改是否成功，有结果A。
    Result:     A：提示不满足复杂度要求，修改失败。
    Remark:     1、密码必须包含大写字母、小写字母、数字、特殊字符四种中至少三种字符的组合（其中特殊字符必须）
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN - 3, upper=3)
    pw_b = PwdLib.gen_pw(digit=PW.MIN - 3, lower=3)
    pw_c = PwdLib.gen_pw(digit=PW.MIN - 3, symbol=3)
    pw_d = PwdLib.gen_pw(upper=PW.MIN - 3, lower=3)
    pw_e = PwdLib.gen_pw(upper=PW.MIN - 3, symbol=3)
    pw_f = PwdLib.gen_pw(lower=PW.MIN - 3, symbol=3)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for index, pw in enumerate([pw_a, pw_b, pw_c, pw_d, pw_e, pw_f]):
            logging.info(f"Check admin password available: index [{letters[index]}]")
            assert PwdLib.set_admin_password(pw, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_simple)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2315", "[TC2315] Testcase_BiosPasswordSecurity_009", "设置密码字符类型测试_3种字符类型密码"))
def Testcase_BiosPasswordSecurity_009():
    """
    Name:       设置密码字符类型测试_3种字符类型密码
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码为3种字符类型，尝试各种组合（共4种组合）；
                3、检查密码修改是否成功，有结果A。
    Result:     A：密码复杂度要求密码需要在大写字母、小写字母、数字中任选两种，且必须加特殊字符；满足此要求的组合能修改成功，不满足此要求的组合不能设置成功。
    Remark:     1、密码必须包含大写字母、小写字母、数字、特殊字符四种中至少三种字符的组合（其中特殊字符必须）
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN - 3, upper=2, lower=1)
    pw_b = PwdLib.gen_pw(digit=PW.MIN - 3, upper=2, symbol=1)
    pw_c = PwdLib.gen_pw(digit=PW.MIN - 3, lower=2, symbol=1)
    pw_d = PwdLib.gen_pw(upper=PW.MIN - 3, lower=2, symbol=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for index, pw in enumerate([pw_a, pw_b, pw_c, pw_d]):
            logging.info(f"Check admin password available: index [{letters[index]}]")
            result, expect = (False, PwdLib.pw_simple) if pw in [pw_a] else (True, PwdLib.pw_change_saved)
            if result:
                assert PwdLib.set_admin_pw_and_verify(pw, PW.ADMIN)
            else:
                assert PwdLib.set_admin_password(pw, PW.ADMIN, result=result, save=False, expect=expect)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2316", "[TC2316] Testcase_BiosPasswordSecurity_010", "设置密码字符类型测试_4种字符类型密码"))
def Testcase_BiosPasswordSecurity_010():
    """
    Name:       设置密码字符类型测试_4种字符类型密码
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码为4种字符类型，尝试各种组合（共1种组合）；
                3、检查密码修改是否成功，有结果A。
    Result:     A：满足复杂度要求，修改成功。
    Remark:     1、密码必须包含大写字母、小写字母、数字、特殊字符四种中至少三种字符的组合（其中特殊字符必须）
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN - 4, upper=2, lower=1, symbol=1)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for index, pw in enumerate([pw_a]):
            logging.info(f"Check admin password available: index [{letters[index]}]")
            assert PwdLib.set_admin_pw_and_verify(pw, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2317", "[TC2317] Testcase_BiosPasswordSecurity_011", "设置密码字符类型测试_特殊字符遍历"))
def Testcase_BiosPasswordSecurity_011():
    """
    Name:       设置密码字符类型测试_特殊字符遍历
    Condition:
    Steps:      1、启动进Setup菜单，设置修改密码；
                2、新密码包含的特殊字符遍历所有特殊字符；
                3、检查密码修改是否成功，有结果A。
    Result:     A：只支持Help信息列举的特殊字符，其他特殊字符不支持输入
    Remark:     1、支持特殊字符如下：
                `~!@#$%^&*()-_=+\|[{}];:'",<.>/?  和空格
    """
    pw_prefix = PwdLib.gen_pw(upper=1, lower=4)
    pw_suffix = PwdLib.gen_pw(digit=PW.MIN - 7)
    pw_list = [PwdLib.gen_pw(prefix=rf"{pw_prefix}{_chr * 2}", suffix=pw_suffix) for _chr in PW.SYMBOL]  # 密码需要2位不同

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for index, pw in enumerate(pw_list):
            logging.info(f"Check admin password available: index [{index}]")
            assert PwdLib.set_admin_password(pw, PW.ADMIN, result=True, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2318", "[TC2318] Testcase_BiosPasswordSecurity_013", "输入错误密码次数测试_输入错误密码次数小于阈值(3)"))
def Testcase_BiosPasswordSecurity_013():
    """
    Name:       输入错误密码次数测试_输入错误密码次数小于阈值(3)
    Condition:
    Steps:      1、启动进Setup菜单前，输入错误的密码次数不超过阈值；
                2、检查是否出现报错提示，并可以再次输入，有结果A。
    Result:     A：提示报错，并可以再次输入。
    Remark:
    """
    invalid_pw = 2
    pw_list = [PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2) for _ in range(invalid_pw)]

    try:
        assert SetUpLib.boot_to_pw_prompt()
        for pw in pw_list:
            SetUpLib.send_data_enter(pw)
            assert SetUpLib.wait_msg(PwdLib.pw_invalid)
            SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.PW_PROMPT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2319", "[TC2319] Testcase_BiosPasswordSecurity_014", "输入错误密码次数测试_阈值(3)内连续输入错误密码后输入正确密码"))
def Testcase_BiosPasswordSecurity_014():
    """
    Name:       输入错误密码次数测试_阈值(3)内连续输入错误密码后输入正确密码
    Condition:
    Steps:      1、启动进Setup菜单前，输入错误的密码次数不超过阈值；
                2、最后输入正确的密码；
                3、检查是否可以登录setup菜单，有结果A。
    Result:     A：输入错误密码提示报错，输入正确密码可以登录。
    Remark:
    """
    invalid_pw = 2
    pw_list = [PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2) for _ in range(invalid_pw)]

    try:
        assert SetUpLib.boot_to_pw_prompt()
        for pw in pw_list:
            SetUpLib.send_data_enter(pw)
            assert SetUpLib.wait_msg(PwdLib.pw_invalid)
            SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.PW_PROMPT)
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2320", "[TC2320] Testcase_BiosPasswordSecurity_015", "输入错误密码次数测试_输入错误密码次数超出阈值(3)"))
def Testcase_BiosPasswordSecurity_015():
    """
    Name:       输入错误密码次数测试_输入错误密码次数超出阈值(3)
    Condition:
    Steps:      1、启动进Setup菜单前，输入错误的密码次数超过阈值；
                2、检查是否可以继续输入，界面是否出现报错提示，有结果A。
    Result:     A：无法继续输入，锁定输入界面，提示报错、并提示复位。
    Remark:     1、超过3次输入失败会锁定并提示复位。
    """
    invalid_pw = 3
    pw_list = [PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2) for _ in range(invalid_pw)]

    try:
        assert SetUpLib.boot_to_pw_prompt()
        for pw in pw_list:
            SetUpLib.send_data_enter(pw)
            assert SetUpLib.wait_msg(PwdLib.pw_invalid)
            SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(PwdLib.pw_lock)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2321", "[TC2321] Testcase_BiosPasswordSecurity_016", "输入错误密码次数测试_超出阈值(3)不影响下一次登录"))
def Testcase_BiosPasswordSecurity_016():
    """
    Name:       输入错误密码次数测试_超出阈值(3)不影响下一次登录
    Condition:
    Steps:      1、启动进Setup菜单前，输入错误的密码次数超过阈值；
                2、系统热复位，再次尝试输入正确密码；
                3、检查是否可以正确登录，有结果A。
    Result:     A：不影响下一次登录，正确密码可以登录。
    Remark:     1、超过3次输入失败会锁定并提示复位。
    """
    invalid_pw = 3
    pw_list = [PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2) for _ in range(invalid_pw)]

    try:
        assert SetUpLib.boot_to_pw_prompt()
        for pw in pw_list:
            SetUpLib.send_data_enter(pw)
            assert SetUpLib.wait_msg(PwdLib.pw_invalid)
            SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(PwdLib.pw_lock)
        BmcLib.force_reset()
        assert SetUpLib.boot_to_setup()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2322", "[TC2322] Testcase_BiosPasswordSecurity_019", "用户修改密码_输入正确旧密码"))
def Testcase_BiosPasswordSecurity_019():
    """
    Name:       用户修改密码_输入正确旧密码
    Condition:
    Steps:      1、启动进Setup菜单，修改密码；
                2、检查是否需要验证旧密码；
                3、输入正确的旧密码，有结果A。
    Result:     A：旧密码正确才能修改密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=True, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2323", "[TC2323] Testcase_BiosPasswordSecurity_020", "用户修改密码_输入错误旧密码"))
def Testcase_BiosPasswordSecurity_020():
    """
    Name:       用户修改密码_输入错误旧密码
    Condition:
    Steps:      1、启动进Setup菜单，修改密码；
                2、检查是否需要验证旧密码；
                3、输入错误的旧密码，有结果A。
    Result:     A：旧密码错误，不能修改密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(PwdLib.pw_enter_old, 10)
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid, 10)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2324", "[TC2324] Testcase_BiosPasswordSecurity_021", "用户修改密码_新密码需要二次确认"))
def Testcase_BiosPasswordSecurity_021():
    """
    Name:       用户修改密码_新密码需要二次确认
    Condition:
    Steps:      1、启动进Setup菜单，修改密码；
                2、输入正确旧密码，输入复杂度符合要求的新密码；
                3、检查是否需要确认新密码，有结果A。
    Result:     A：新密码需要再次输入确认。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=True, save=False, confirm_pw=pw_a)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2325", "[TC2325] Testcase_BiosPasswordSecurity_022", "用户修改密码_新密码确认失败"))
def Testcase_BiosPasswordSecurity_022():
    """
    Name:       用户修改密码_新密码确认失败
    Condition:
    Steps:      1、启动进Setup菜单，修改密码；
                2、输入正确旧密码，输入复杂度符合要求的新密码；
                3、确认新密码时输入错误新密码；
                4、检查是否修改成功，有结果A。
    Result:     A：提示新密码确认失败，修改失败。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=False, save=False, confirm_pw=pw_b,
                                         expect=PwdLib.pw_not_same)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2326", "[TC2326] Testcase_BiosPasswordSecurity_023", "用户修改密码_新密码确认成功"))
def Testcase_BiosPasswordSecurity_023():
    """
    Name:       用户修改密码_新密码确认成功
    Condition:
    Steps:      1、启动进Setup菜单，修改密码；
                2、输入正确旧密码，输入复杂度符合要求的新密码；
                3、确认新密码时输入正确新密码；
                4、检查是否修改成功，有结果A。
    Result:     A：提示新密码修改成功，保存重启生效。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_a, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2327", "[TC2327] Testcase_BiosPasswordSecurity_024", "登录失败模糊提示信息测试"))
def Testcase_BiosPasswordSecurity_024():
    """
    Name:       登录失败模糊提示信息测试
    Condition:
    Steps:      1、启动进Setup菜单前，输入错误的密码，尝试多种场景（长度不满足、字符组合不满足）；
                2、检查登录失败提示信息是否准确，有结果A。
    Result:     A：提示密码错误，登录失败，无详细登录失败原因。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=1, total=PW.MIN - 1)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=1, total=PW.MAX + 1)
    pw_c = PwdLib.gen_pw(digit=4, upper=2, lower=2, total=PW.MIN)
    pw_d = PwdLib.gen_pw(digit=8, total=PW.MIN)

    try:
        for pw in [[pw_a, pw_b], [pw_c, pw_d]]:  # 错误密码达到3次会锁定
            assert SetUpLib.boot_to_pw_prompt()
            SetUpLib.send_data_enter(pw[0])
            assert SetUpLib.wait_msg(PwdLib.pw_invalid, 10)
            SetUpLib.send_data_enter(pw[1])
            assert SetUpLib.wait_msg(PwdLib.pw_invalid, 10)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2328", "[TC2328] Testcase_BiosPasswordSecurity_025", "禁止提供自动登录功能测试"))
def Testcase_BiosPasswordSecurity_025():
    """
    Name:       禁止提供自动登录功能测试
    Condition:
    Steps:      1、启动进Setup菜单前，输入正确的密码，检查登录界面是否提供“自动登录/记住我”功能，有结果A。
    Result:     A：登录成功，无“自动登录/记住我”功能。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data(Msg.BIOS_PASSWORD)
        assert not SetUpLib.wait_boot_msgs(["[Ss]ave", "[Aa]uto", "[Rr]ecord"], timeout=5)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2329", "[TC2329] Testcase_BiosPasswordSecurity_026", "PowerOnPassword设置"))
def Testcase_BiosPasswordSecurity_026():
    """
    Name:       PowerOnPassword设置
    Condition:
    Steps:      1、启动进Setup菜单，使能Power On Password，F10保存重启；
                2、检查进入OS前是否要密码验证，管理员密码能否登录进入OS，有结果A。
    Result:     A：需要密码验证，管理员密码能够登录进入OS。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.POWER_ON_PW, Msg.ENABLE, save=True)
        assert SetUpLib.wait_msg(Msg.PW_PROMPT, timeout=SutConfig.Env.BOOT_DELAY)
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2330", "[TC2330] Testcase_A2SecurityModel1_002", "串口登录Setup需要密码认证测试"))
def Testcase_A2SecurityModel1_002():
    """
    Name:       串口登录Setup需要密码认证测试
    Condition:  1、默认配置
    Steps:      1、启动过程中串口按热键进入Setup菜单前，检查是否需要密码认证，有结果A；
                2、输入正确密码，检查是否正常登陆，有结果B；
    Result:     A：需要输入密码才可以登录；
                B：登陆Setup成功。
    Remark:     1、需要遍历KVM、串口、SOL、USB（VGA接显示器、配USB按键）等机制进入Setup菜单是否需要输入密码。
    """
    try:
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2331", "[TC2331] Testcase_SensitiveInfoCheck_001", "串口日志禁止显示密码"))
def Testcase_SensitiveInfoCheck_001():
    """
    Name:       串口日志禁止显示密码
    Condition:
    Steps:      1、启动进OS，检查串口日志中是否包含登录密码信息，有结果A；
                2、开启全打印，启动进OS，再次检查串口日志中是否包含登录密码信息，有结果A。
    Result:     A：不包含密码信息。
    Remark:
    """
    try:
        assert BmcLib.force_reset()
        ser_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.LINUX_GRUB, SutConfig.Env.BOOT_DELAY,
                                    SutConfig.Env.BOOT_DELAY)
        assert Msg.BIOS_PASSWORD not in ser_log, "BIOS password is found in normal serial log"
        assert BmcLib.debug_message(True)
        assert BmcLib.force_reset()
        ser_debug = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.LINUX_GRUB, SutConfig.Env.BOOT_DELAY,
                                      SutConfig.Env.BOOT_DELAY)
        assert Msg.BIOS_PASSWORD not in ser_debug, "BIOS password is found in full serial log"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.debug_message(False)
        BmcLib.clear_cmos()


@core.test_case(("2332", "[TC2332] Testcase_SensitiveInfoCheck_002", "登录界面禁止明文显示密码"))
def Testcase_SensitiveInfoCheck_002():
    """
    Name:       登录界面禁止明文显示密码
    Condition:
    Steps:      1、单板启动登录Setup菜单前，输入正确密码，检查登录是否明文显示密码，有结果A。
    Result:     A：没有明文显示密码，不显示或用*代替。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PwdLib.check_pw_length_and_hidden(Msg.BIOS_PASSWORD, len(Msg.BIOS_PASSWORD))
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2333", "[TC2333] Testcase_HttpsBoot_001", "Https Boot设置菜单检查"))
def Testcase_HttpsBoot_001():
    """
    Name:       Https Boot设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，Boot界面查看是否提供Https Boot设置菜单，可选值及默认值，有结果A。
    Result:     A：提供Https Boot设置菜单，Disabled、IPv4、IPv6、IPv4/IPv6四项可选，默认IPv4。
    Remark:
    """
    https_boot_values = ["Disabled", "HTTPS:IPv4", "HTTPS:IPv6", "HTTPS:IPv4/IPv6"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        get_values = SetUpLib.get_all_values(Msg.HTTPS_BOOT)
        assert get_values
        assert MiscLib.same_values(https_boot_values, get_values)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("2334", "[TC2334] Testcase_Chipsec_001", "chipsec扫描测试"))  # Chipsec目前测试Fail
# def Testcase_Chipsec_001():
#     """
#     Name:       chipsec扫描测试
#     Condition:  
#     Steps:      1、开展chipsec扫描，有结果A。
#     Result:     A：版本通过chipsec扫描且无告警（如告警无法清除需提供合理解释）。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2335", "[TC2335] Testcase_UserPassWord_001", "管理员添加普通用户密码"))
def Testcase_UserPassWord_001():
    """
    Name:       管理员添加普通用户密码
    Condition:
    Steps:      1、管理员登录Setup菜单，检查添加普通用户密码时是否需要校验旧密码，有结果A；
                2、设置普通用户的密码不符合Help信息要求，检查能否设置成功，有结果B；
                3、设置普通用户的密码符合Help信息要求，检查能否设置成功，有结果C；
                4、F10保存重启后通过设置的普通用户密码登录Setup菜单，检查能否成功登录，有结果D。
    Result:     A：管理员设置普通用户密码不需要校验旧密码；
                B：密码不符合复杂度要求，设置失败，提示错误；
                C：密码设置成功；
                D：普通用户密码登录成功并要求修改默认密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=4, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, symbol=2, lower=PW.MIN-6)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_USR_PW)
        assert PwdLib.set_user_password(pw_a, old_pw=None, result=False, save=False)
        assert PwdLib.set_user_password(pw_b, old_pw=None, result=True, save=True)
        assert PwdLib.continue_to_setup_with_pw(pw_b, default=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2336", "[TC2336] Testcase_UserPassWord_002", "管理员删除普通用户密码"))
def Testcase_UserPassWord_002():
    """
    Name:       管理员删除普通用户密码
    Condition:  1、已设置普通用户密码，假定为a；
                2、删除普通用户密码开关已开启。
    Steps:      1、管理员登录Setup菜单，检查删除普通用户密码时是否需要密码验证，有结果A；
                2、删除普通用户密码，F10保存重启后通过密码a登录Setup菜单，检查能否登录成功，有结果B；
    Result:     A：管理员删除普通用户密码不需要密码校验；
                B：登录Setup失败。
    Remark:
    """
    pw_init = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)

    try:
        assert PwdLib.init_user_password(pw_a, pw_init)
        assert PwdLib.delele_user_pw()
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2337", "[TC2337] Testcase_UserPassWord_003", "管理员修改普通用户密码"))
def Testcase_UserPassWord_003():
    """
    Name:       管理员修改普通用户密码
    Condition:  1、已设置普通用户密码，假定为a。
    Steps:      1、管理员登录Setup菜单，检查修改普通用户密码时是否需要校验旧密码，有结果A；
                2、修改普通用户密码为b，F10保存重启通过普通用户密码a登录Setup菜单，检查能否成功登录，有结果B;
                3、通过普通用户密码b登录Setup菜单，检查能否成功登录，有结果C;
    Result:     A：管理员设置普通用户密码不需要校验旧密码；
                B：密码a登录失败；
                C：密码b登录成功。
    Remark:
    """
    pw_init = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)

    try:
        assert PwdLib.init_user_password(pw_a, pw_init)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_b, old_pw=PW.USER, save=True, result=True)
        assert SetUpLib.continue_to_pw_prompt()
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.PW_PROMPT)
        SetUpLib.send_data_enter(pw_b)
        assert SetUpLib.wait_boot_msgs(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2338", "[TC2338] Testcase_UserPassWord_004", "普通用户修改自身密码_复杂度检验"))
def Testcase_UserPassWord_004():
    """
    Name:       普通用户修改自身密码_复杂度检验
    Condition:  1、已设置普通用户密码。
    Steps:      1、普通用户登录Setup菜单，检查修改自身密码时是否需要校验旧密码，有结果A；
                2、修改密码不符合Help信息要求，检查能否设置成功，有结果B；
                3、修改密码符合Help信息提示要求，检查能否设置成功，有结果C；
                4、F10保存重启后通过修改后的普通用户密码登录Setup菜单，检查能否成功登录，有结果D。
    Result:
                A：普通用户修改自身密码需要校验旧密码；
                B：密码不符合复杂度要求，设置失败，提示错误；
                C：密码设置成功；
                D：普通用户密码登录成功。
    Remark:
    """
    pw_init = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_invalid1 = PwdLib.gen_pw(digit=4, upper=2, lower=2)
    pw_invalid2 = PwdLib.gen_pw(digit=4, upper=1, lower=1, symbol=PW.MIN - 7)

    try:
        assert PwdLib.init_user_password(pw_a, pw_init)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True)
        for pw in [pw_invalid1, pw_invalid2]:
            assert PwdLib.set_user_password(new_pw=pw, old_pw=PW.USER, result=False, save=False)
        assert PwdLib.set_user_pw_and_verify(pw_b, PW.USER)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2339", "[TC2339] Testcase_UserPassWord_005", "普通用户修改自身密码_与管理员密码一致"))
def Testcase_UserPassWord_005():
    """
    Name:       普通用户修改自身密码_与管理员密码一致
    Condition:  1、已设置管理员及普通用户密码。
    Steps:      1、管理员登录Setup菜单，设置普通用户密码与管理员密码一致，检查能否设置成功，有结果A；
                2、管理员设置管理员密码与普通用的密码一致，检查能否设置成功，有结果A；
                3、普通用户登录Setup菜单，修改自身密码跟管理员密码一致，检查能否设置成功，有结果A。
    Result:     A：设置失败，提示错误；
    Remark:
    """
    pw_init = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)

    try:
        assert PwdLib.init_user_password(pw_a, pw_init)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_user=True)
        assert PwdLib.set_user_password(PW.ADMIN, old_pw=None, result=False, save=False, expect=PwdLib.pw_invalid)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(PW.USER, old_pw=PW.ADMIN, result=False, save=False, expect=PwdLib.pw_invalid)
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        assert PwdLib.set_user_password(PW.ADMIN, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2340", "[TC2340] Testcase_UserPassWord_006", "修改密码BMC安全日志记录"))
def Testcase_UserPassWord_006():
    """
    Name:       修改密码BMC安全日志记录
    Condition:
    Steps:      1、管理员登录Setup菜单，设置普通用户的密码a，检查BMC Web是否存在安全日志记录，有结果A；
                2、管理员登录Setup菜单，修改普通用户的密码为错误密码，检查BMC Web是否存在安全日志记录，有结果B；
                3、管理员登录Setup菜单，修改普通用户的密码b，检查BMC Web是否存在安全日志记录，有结果C；
                4、普通用户使用密码b登录Setup菜单，修改自身密码为错误密码，检查BMC Web是否存在安全日志记录，有结果D；
                5、普通用户使用密码b登录Setup菜单，修改自身密码c，检查BMC Web是否存在安全日志记录，有结果E；
                6、管理员登录Setup菜单，清除普通用户的密码，检查BMC Web是否存在安全日志记录，有结果F。
    Result:     A：存在管理员创建用户密码记录；
                B：存在管理员修改密码失败记录；
                C：存在管理员修改用户密码记录；
                D：存在普通用户修改密码失败记录；
                E：存在普通用户修改用户密码记录；
                F：存在管理员清除用户密码记录。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_c = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    pw_short = PwdLib.gen_pw(digit=4, upper=2, symbol=1)
    pw_simple = PwdLib.gen_pw(digit=4, upper=2, lower=2)

    admin_set_user_pass = PwdLib.sec_admin_set_user_pass
    admin_set_user_fail = PwdLib.sec_admin_set_user_fail
    admin_change_user_pass = PwdLib.sec_admin_change_user_pass
    admin_clear_user = PwdLib.sec_admin_clear_user

    user_change_pass = PwdLib.sec_user_change_pass
    user_change_fail = PwdLib.sec_user_change_fail
    user_check_fail = PwdLib.sec_user_check_fail

    try:
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        time_now = BmcLib.get_bmc_datetime()
        assert PwdLib.set_user_pw_save_wo_exit(pw_a, old_pw=None)
        # result A
        assert PlatMisc.bmc_log_exist(admin_set_user_pass, time_now, security=True), "admin_set_user_pass"
        # step 2
        for try_pw1 in [
            [pw_short, pw_short],
            [pw_simple, pw_simple],
            [pw_short, pw_simple]
        ]:
            time_now = BmcLib.get_bmc_datetime()
            assert PwdLib.set_user_password(try_pw1[0], old_pw=None, result=False, save=False, confirm_pw=try_pw1[1])
            # result B
            assert PlatMisc.bmc_log_exist(admin_set_user_fail, time_now, security=True), "admin_ser_user_fail"
        # step 3
        time_now = BmcLib.get_bmc_datetime()
        assert PwdLib.set_user_pw_save_wo_exit(pw_b, old_pw=None)
        # result C
        assert PlatMisc.bmc_log_exist(admin_change_user_pass, time_now, security=True), "admin_change_user_pass"
        # step 4
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True, default=True)
        for try_pw2 in [
            [pw_short, pw_short],
            [pw_simple, pw_simple],
            [pw_short, pw_simple]
        ]:
            time_now = BmcLib.get_bmc_datetime()
            assert PwdLib.set_user_password(try_pw2[0], old_pw=PW.USER, result=False, save=False, confirm_pw=try_pw2[1])
            # result D
            assert PlatMisc.bmc_log_exist(user_change_fail, time_now, security=True), "user_change_fail"
        # step 4+ (input invalid old user pw)
        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.locate_option(Msg.SET_USR_PW)
        assert PwdLib.set_user_password(new_pw=None, old_pw=PW.ADMIN, result=None, save=False)  # 无效的用户密码
        # result D+ (input invalid old user pw)
        assert PlatMisc.bmc_log_exist(user_check_fail, time_now, security=True), "user_check_fail"
        # step 5
        time_now = BmcLib.get_bmc_datetime()
        assert PwdLib.set_user_password(pw_c, old_pw=PW.USER, result=True, save=True)
        # result E
        assert PlatMisc.bmc_log_exist(user_change_pass, time_now, security=True), "user_change_pass"
        # step 6
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_user=True)
        time_now = BmcLib.get_bmc_datetime()
        assert PwdLib.delele_user_pw()
        # result E
        assert PlatMisc.bmc_log_exist(admin_clear_user, time_now, security=True), "admin_clear_user"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2341", "[TC2341] Testcase_UserPassWord_007", "PowerOnPassword使能后普通用户登录OS"))
def Testcase_UserPassWord_007():
    """
    Name:       PowerOnPassword使能后普通用户登录OS
    Condition:
    Steps:      1、管理员登录Setup菜单，使能Power On Password，F10保存重启；
                2、检查OS引导时是否弹出密码输入框，普通用户密码能否登录进入OS，有结果A。
    Result:     A：弹出密码输入框，通过普通用户密码能够登录进入OS。
    Remark:
    """
    pw_i = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_user_pw_save_wo_exit(pw_i, old_pw=None)
        assert SetUpLib.set_option_value(Msg.POWER_ON_PW, Msg.ENABLE, save=True)
        assert SetUpLib.wait_boot_msgs(Msg.PW_PROMPT)
        SetUpLib.send_data_enter(PW.USER)
        assert SetUpLib.wait_msg(PwdLib.pw_is_default, 5)
        SetUpLib.send_key(Key.ENTER)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 120)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2342", "[TC2342] Testcase_UserPassWord_008", "设置普通用户密码为简易密码"))
def Testcase_UserPassWord_008():
    """
    Name:       设置普通用户密码为简易密码
    Condition:
    Steps:      1、管理员登录Setup菜单，使能Simple Password，设置普通用户密码为简易密码a，检查能否设置成功；F10保存重启后，检查能否通过简易密码a登录Setup菜单，有结果A；
                2、普通用户登录Setup菜单，修改密码为简易密码b，检查能否修改成功；F10保存重启后，检查能否通过简易密码b登录Setup菜单，有结果A；
                3、管理员登录Setup菜单，关闭Simple Password，F10保存重启，检查能否通过简易密码b登录Setup菜单，有结果B；
                4、修改普通用户密码为简易密码c，检查能否设置成功，修改普通用户密码为复杂密码d，检查能否设置成功，有结果C；
                5、F10保存重启后检查能否通过复杂密码d登录Setup菜单，有结果B。
    Result:     A：简易密码设置成功，能够通过简易密码登录；
                B：登录成功；
                C：设置简易密码c失败，设置复杂密码d成功；
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN)
    pw_b = PwdLib.gen_pw(digit=PW.MIN)
    pw_c = PwdLib.gen_pw(digit=PW.MIN)
    pw_d = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm, 15)
        SetUpLib.send_key(Key.ENTER)
        # step 2 + result A
        assert PwdLib.init_user_password(pw_b, pw_a)
        # result A
        assert PwdLib.continue_to_setup_with_pw(pw_b)
        # step 3
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.DISABLE, save=True)
        # result B
        assert PwdLib.continue_to_setup_with_pw(pw_b, to_user=True)
        assert PwdLib.set_user_password(pw_c, PW.USER, result=False, save=False, expect=PwdLib.pw_simple)
        assert PwdLib.set_user_password(pw_d, PW.USER, result=True, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2343", "[TC2343] Testcase_UserPassWord_009", "登入登出Setup时BMC安全日志记录"))
def Testcase_UserPassWord_009():
    """
    Name:       登入登出Setup时BMC安全日志记录
    Condition:  1、已设置管理员及普通用户密码。
    Steps:      1、普通用户登录Setup菜单之后退出进入系统，检查BMC安全日志中是否存在日志记录，身份是否区分，有结果A；
                2、管理员登录Setup菜单之后退出进入系统，检查BMC安全日志中是否存在日志记录，身份是否区分，有结果B；
                3、密码输入失败时，检查BMC安全日志是否做身份区分，有结果C。
    Result:     A：BMC安全日志登入登出记录完整且为普通用户身份；
                B：BMC安全日志登入登出记录完整且为管理员身份；
                C：无身份区分，显示check password error。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)

    user_front_login = PwdLib.sec_user_front_login
    user_setup_login = PwdLib.sec_user_setup_login
    user_setup_logout = PwdLib.sec_user_setup_logout

    admin_front_login = PwdLib.sec_admin_front_login
    admin_setup_login = PwdLib.sec_admin_setup_login
    admin_setup_logout = PwdLib.sec_admin_setup_logout

    check_fail = PwdLib.sec_check_fail

    try:
        # condition
        assert PwdLib.admin_set_user_pw_default(pw_a)
        # step 1 + result C
        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(pw_b)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        SetUpLib.send_key(Key.ENTER)
        assert PlatMisc.bmc_log_exist(check_fail, time_now, security=True), "check_fail user"
        # step 1 + result A
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.USER)
        assert SetUpLib.wait_msg(PwdLib.pw_is_default)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(user_front_login, time_now, security=True), "user_front_login"

        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.move_to_bios_config()
        assert PlatMisc.bmc_log_exist(user_setup_login, time_now, security=True), "user_setup_login"

        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.back_to_front_page()
        assert PlatMisc.bmc_log_exist(user_setup_logout, time_now, security=True), "user_setup_logout exit"

        assert SetUpLib.move_to_bios_config()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_msg(Msg.CPU_RSC_ALLOC)
        assert PlatMisc.bmc_log_exist(user_setup_logout, time_now, security=True), "user_setup_logout reboot"

        # step 2 + result C
        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(pw_b)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        SetUpLib.send_key(Key.ENTER)
        assert PlatMisc.bmc_log_exist(check_fail, time_now, security=True), "check_fail admin"

        # step 2 + result B
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.ADMIN)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(admin_front_login, time_now, security=True), "admin_front_login"

        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.move_to_bios_config()
        assert PlatMisc.bmc_log_exist(admin_setup_login, time_now, security=True), "admin_setup_login"

        time_now = BmcLib.get_bmc_datetime()
        assert SetUpLib.back_to_front_page()
        assert PlatMisc.bmc_log_exist(admin_setup_logout, time_now, security=True), "admin_setup_logout exit"

        assert SetUpLib.move_to_bios_config()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_msg(Msg.CPU_RSC_ALLOC)
        assert PlatMisc.bmc_log_exist(admin_setup_logout, time_now, security=True), "admin_logout reboot"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


# @core.test_case(("2344", "[TC2344] Testcase_UserPassWord_012", "普通用户热键响应_串口方式"))
# def Testcase_UserPassWord_012():
#     """
#     Name:       普通用户热键响应_串口方式
#     Condition:  
#     Steps:      1、单板上电在热键位置通过串口遍历所有热键，按下后输入普通用户密码，检查能否成功登入相应热键界面，有结果A；
#                 2、串口按热键登录FrontPage后检查FrontPage界面显示情况，有结果B；
#                 3、普通用户登录进入Setup之后，通过串口遍历所有热键切换，检查响应是否正常，有结果C。
#     Result:     A：除Del能够登录进入外，F11、F12、F6均登录失败，提示密码错误；
#                 B：FrontPage界面只存在进Setup和Continue两个选项；
#                 C：F5和F6无法修改选项值，F9已被禁用，其余热键均正常响应。
#     Remark:     1、遍历所有热键包括Del、F6、F11、F12；
#                 2、Setup内部热键包括F1、ESC、方向键、F5、F6、Enter、F9、F10；
#                 3、普通用户时Setup菜单除修改密码“Set User Password ”、保存并退出"Save Changes & Exit"外所有选项置灰，所以F5、F6无法修改；
#                 4、KVM跟串口响应热键处理方式不同。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2345", "[TC2345] Testcase_UserPassWord_013", "普通用户无权限修改菜单选项"))
# def Testcase_UserPassWord_013():
#     """
#     Name:       普通用户无权限修改菜单选项
#     Condition:  
#     Steps:      1、管理员登录Setup菜单，遍历所有界面，检查是否存在异常，是否有正常选项被置灰、隐藏，是否有开放多余选项，有结果A；
#                 2、普通用户登录Setup菜单，遍历所有界面，检查是否存在可设置选项，是否有开放多余选项，是否有正常选项被隐藏，有结果B。
#     Result:     A：Setup菜单正常，无正常选项被置灰、隐藏，没有开放多余选项；
#                 B：无正常选项被隐藏，没有开放多余选项，除Set User Password、Save Changes & Exit两个选项外，其余选项均不可设置。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2346", "[TC2346] Testcase_UserPassWord_014", "普通用户屏蔽F9功能"))
def Testcase_UserPassWord_014():
    """
    Name:       普通用户屏蔽F9功能
    Condition:
    Steps:      1、管理员登录Setup菜单，修改Setup的选项与默认值不一致，覆盖盖Advanced、boot、power、secure界面下的变量，F10保存重启；
                2、普通用户登录Setup菜单，串口和KVM按F9，检查响应情况，有结果A；
                3、重启系统，管理员登录Setup菜单，串口和KVM按F9，检查响应情况，有结果B。
    Result:     A：串口和KVM按F9无反应，不会响应F9功能；
                B：串口和KVM按F9均响应，设置的选项恢复默认值。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    options = [[Msg.PAGE_ADVANCED, Msg.PATH_MEM_CONFIG, Msg.MEM_TURBO],
               [Msg.PAGE_BOOT, None, Msg.USB_BOOT],
               [Msg.PAGE_SECURITY, None, Msg.POWER_ON_PW]]
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN)
        value_choice = {}
        value_default = {}
        for _, op in enumerate(options):
            page, path, option = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            values = SetUpLib.get_all_values(option)
            default = SetUpLib.get_option_value(option)
            values.remove(default)
            value_choice[option] = random.choice(values)
            value_default[option] = default
            assert SetUpLib.set_option_value(option, value_choice[option])
            assert SetUpLib.back_to_setup_toppage()

        SetUpLib.send_key(Key.F9)
        assert SetUpLib.wait_msg(Msg.LOAD_DEFAULT_PROMPT, 10)
        SetUpLib.send_key(Key.ENTER)

        for _, op in enumerate(options):
            page, path, option = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            current = SetUpLib.get_option_value(option)
            assert current == value_default[option]
            assert SetUpLib.back_to_setup_toppage()
        SetUpLib.send_keys(Key.SAVE_RESET)

        assert PwdLib.continue_to_setup_with_pw(PW.USER, default=True)
        SetUpLib.send_key(Key.F9)
        assert not SetUpLib.wait_msg(Msg.LOAD_DEFAULT_PROMPT, 10)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2347", "[TC2347] Testcase_UserPassWord_015", "普通用户F10功能测试"))
def Testcase_UserPassWord_015():
    """
    Name:       普通用户F10功能测试
    Condition:
    Steps:      1、普通用户登录Setup菜单，修改自身密码a，按F10之后检查响应情况，用密码a登录Setup菜单，检查能否登录成功，有结果A；
                2、再次修改自身密码b，Exit界面执行"Save Changes & Exit"检查响应情况，用密码b登录Setup菜单，检查能否登录成功，有结果B。
    Result:     A：正常响应F10，成功登录Setup；
                B：正常响应"Save Changes & Exit"，成功登录Setup。
    Remark:
    """
    pw_init = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        # step 1 + result A
        assert PwdLib.init_user_password(pw_a, pw_init)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_b, PW.USER, result=True, save=False)
        assert SetUpLib.save_with_exit()
        assert PwdLib.continue_to_setup_with_pw(pw_b)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2348", "[TC2348] Testcase_UserPassWord_016", "用户切换配置不变更"))
def Testcase_UserPassWord_016():
    """
    Name:       用户切换配置不变更
    Condition:
    Steps:      1、管理员登录Setup菜单，F9恢复默认配置，F10后通过Redfish收集一份CurrentValue值a；
                2、普通用户登录Setup菜单，F10后通过Redfish收集一份CurrentValue值b，对比ab两份配置，检查是否存在差异，有结果A；
    Result:     A：用户切换配置保持不变。
    Remark:     1、确保普通用户置灰所有选项不会影响选项的配置；
                2、F9不影响选项配置（目前普通用户F9不响应）。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        # step 1
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_setup()
        json_a = Sut.BMC_RFISH.current_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Admin_F9_F10.json")
        assert json_a, "Invalid CurrentValue: admin"
        # step 2
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, default=True)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_setup()
        json_b = Sut.BMC_RFISH.current_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="User_F9_F10.json")
        assert json_b, "Invalid CurrentValue: user"
        # result A
        assert json_a == json_b, "Admin CurrentValue mismatch with user after F10 pressed"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2349", "[TC2349] Testcase_UserPassWord_017", "用户切换配置不变更_联动菜单"))
def Testcase_UserPassWord_017():
    """
    Name:       用户切换配置不变更_联动菜单
    Condition:
    Steps:      1、管理员登录Setup菜单，修改部分联动关系选项如BenchMark、EnergyPolicy等，F10后通过Redfish收集一份CurrentValue值a；
                2、普通用户登录Setup菜单，F10后通过Redfish收集一份CurrentValue值b，对比a、b两份配置，检查是否存在差异，有结果A；
                3、普通用户登录Setup菜单，按F9后再按F10，通过Redfish收集一份CurrentValue值c，对比a、b、c三份配置，检查是否存在差异，有结果A；
    Result:     A：用户切换配置保持不变。
    Remark:     1、确保普通用户置灰所有选项不会影响选项的配置；
                2、F9不影响选项配置（目前普通用户F9不响应）。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CPU_CONFIG, Msg.ADV_POWER_MGF_CONFIG])
        assert SetUpLib.set_option_value(Msg.POWER_EFFICIENCY, "HPC", save=True)
        assert SetUpLib.continue_to_setup()
        json_a = Sut.BMC_RFISH.current_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Admin_set_F10_a.json")
        assert json_a, "json_a invalid"
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, default=True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_setup()
        json_b = Sut.BMC_RFISH.current_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="User_F10_a.json")
        assert json_b, "json_b invalid"
        assert json_a == json_b, "Admin CurrentValue mismatch with user after change value and F10 pressed"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2350", "[TC2350] Testcase_UserPassWord_018", "恢复默认配置无法恢复用户密码"))
def Testcase_UserPassWord_018():
    """
    Name:       恢复默认配置无法恢复用户密码
    Condition:  1、已设置普通用户密码，假定为a。
    Steps:      1、管理员登录Setup菜单，F9恢复默认，F10保存重启后检查能否通过普通用户密码a登录Setup菜单，有结果A；
                2、普通用户密码a登录Setup菜单后修改自身密码为b，F10保存重启后检查能否通过普通用户密码b登录Setup菜单，，有结果B；
                3、BMC拉GPIO恢复默认值，重启系统后检查能否通过密码a登录Setup菜单，能否通过密码b登录Setup菜单，有结果C。
    Result:     A：能够通过密码a登录；
                B：能够通过密码b登录；
                C：密码a无法登录，密码b能够登录。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True, default=True)
        assert PwdLib.set_user_pw_and_verify(pw_b, PW.USER)
        assert BmcLib.clear_cmos()
        assert BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(current_pw=pw_b, invalid_pw=pw_a)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


# @core.test_case(("2351", "[TC2351] Testcase_UserPassWord_019", "恢复装备定制化无法恢复用户密码"))
# def Testcase_UserPassWord_019():
#     """
#     Name:       恢复装备定制化无法恢复用户密码
#     Condition:  1、已设置普通用户密码，假定为a。
#     Steps:      1、OS下通过uniCfg工具（uniCfg -w xxxx:x）修改部分选项并通过命令（uniCfg SaveCustomdefualt ）保存为客户定制化默认值，重启系统；
#                 2、管理员登录Setup菜单，修改定制化选项为非定制化值，修改普通用户密码为b，保存重启，普通用户登录Setup菜单，检查LoadCustomDefault选项是否存在，能否恢复定制化选项值，有结果A；
#                 3、管理员登录Setup菜单，检查LoadCustomDefault选项是否存在，能否恢复定制化选项值，有结果B；
#                 4、重启系统后检查能否通过密码a登录Setup菜单，能否通过密码b登录Setup菜单，有结果C。
#     Result:     A：LoadCustomDefault选项存在，无法恢复定制化选项值；
#                 B：LoadCustomDefault选项存在，能恢复定制化选项值；
#                 C：密码a无法登录，密码b能够登录。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2352", "[TC2352] Testcase_UserPassWord_020", "升级普通用户密码保持不变"))
def Testcase_UserPassWord_020():
    """
    Name:       升级普通用户密码保持不变
    Condition:  1、已设置普通用户密码，假定为a。
    Steps:      1、Web升级BIOS版本后上电检查能否通过密码a登录Setup菜单，有结果A；
                2、修改普通用户密码b，F10保存重启后检查能否通过密码b登录Setup菜单，有结果B；
                4、Web升级BIOS版本后上电检查能否通过密码b登录Setup菜单，有结果B。
    Result:     A：能够通过密码a登录；
                B：能够通过密码b登录。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_init = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
    try:
        hpm_img = PlatMisc.get_latest_hpm_bios()
        assert PwdLib.init_user_password(pw_a, pw_init)
        assert Update.update_bios_hpm(hpm_img)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True)
        assert PwdLib.set_user_pw_and_verify(pw_b, PW.USER)
        assert Update.update_bios_hpm(hpm_img)
        assert PwdLib.continue_to_setup_with_pw(pw_b, to_user=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        if Update.flash_bios_bin_and_init(img):
            PwdLib.update_current_pw(pw_admin=Msg.BIOS_PASSWORD)
            PwdLib.update_current_pw(pw_user="")


@core.test_case(("2353", "[TC2353] Testcase_WeakKeyList_001", "弱口令字典默认清单检查"))
def Testcase_WeakKeyList_001():
    """
    Name:       弱口令字典默认清单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，检查弱口令清单，对比清单列表与代码定义是否一致，有结果A；
    Result:     A：弱口令清单内容与数量与代码定义一致。
    Remark:     1、弱口令清单合理性由SE保证
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        weak_pw_list = PwdLib.get_default_weak_pw_list()
        assert set(weak_pw_list) == set(PW.WEAK_PW), "Weak password get from setup mismatch with config"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("2354", "[TC2354] Testcase_WeakKeyList_002", "管理员弱口令检查功能测试"))
def Testcase_WeakKeyList_002():
    """
    Name:       管理员弱口令检查功能测试
    Condition:  1、全擦升级
    Steps:      1、启动进Setup菜单，创建管理员密码为弱口令字典密码，检查能否成功，有结果A；
                2、创建管理员密码为符合密码复杂度要求密码a，检查能否成功，有结果B；
                3、重启进Setup菜单，修改管理员密码为弱口令字典密码，检查能否成功，有结果A；
                4、修改管理员密码为符合密码复杂度要求密码b，检查能否成功，有结果B；
    Result:     A：设置失败，提示不能设置弱口令密码；
                B：设置成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

    try:
        # condition
        assert PwdLib.delete_admin_pw()
        # step 1
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for try_pw1 in PW.WEAK_PW:
            # result A
            assert PwdLib.set_admin_password(try_pw1, old_pw=None, result=False, save=False, expect=PwdLib.pw_is_weak)
        # step 2 + result B
        assert PwdLib.set_admin_pw_and_verify(pw_a, old=None)
        # step 2 + result A
        for try_pw2 in PW.WEAK_PW:
            # result A
            assert PwdLib.set_admin_password(try_pw2, old_pw=PW.ADMIN, result=False, save=False,
                                             expect=PwdLib.pw_is_weak)
        assert PwdLib.set_admin_pw_and_verify(pw_b, old=PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2355", "[TC2355] Testcase_WeakKeyList_003", "普通用户弱口令检查功能测试"))
def Testcase_WeakKeyList_003():
    """
    Name:       普通用户弱口令检查功能测试
    Condition:  1、全擦升级
    Steps:      1、启动进Setup菜单，创建普通用户密码为弱口令字典密码，检查能否成功，有结果A；
                2、创建普通用户密码为符合密码复杂度要求密码a，检查能否成功，有结果B；
                3、重启管理员进Setup菜单，修改普通用户密码为弱口令字典密码，检查能否成功，有结果A；
                4、修改普通用户密码为符合密码复杂度要求密码b，检查能否成功，有结果B；
                5、重启普通用户进Setup菜单，修改普通用户密码为弱口令字典密码，检查能否成功，有结果A；
                6、修改普通用户密码为符合密码复杂度要求密码c，检查能否成功，有结果B；
    Result:     A：设置失败，提示不能设置弱口令密码；
                B：设置成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        # step 1
        assert SetUpLib.locate_option(Msg.SET_USR_PW)
        for try_pw1 in PW.WEAK_PW:
            # result A
            assert PwdLib.set_user_password(try_pw1, old_pw=None, result=False, save=False, expect=PwdLib.pw_is_weak)
        # step 2 + result B
        assert PwdLib.admin_set_user_pw_default(pw_a)
        # step 3 + result A
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_user=True)
        for try_pw2 in PW.WEAK_PW:
            assert PwdLib.set_user_password(try_pw2, old_pw=None, result=False, save=False, expect=PwdLib.pw_is_weak)
        # step 4 + result B
        assert PwdLib.set_user_password(pw_b, None, result=True, save=True)
        # step 5 + result A
        assert PwdLib.continue_to_setup_with_pw(pw_b, to_user=True, default=True)
        for try_pw2 in PW.WEAK_PW:
            assert PwdLib.set_user_password(try_pw2, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_is_weak)
        # step 6 + result B
        assert PwdLib.set_user_pw_and_verify(pw_c, old=PW.USER)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2356", "[TC2356] Testcase_WeakKeyList_004", "添加弱口令测试"))
def Testcase_WeakKeyList_004():
    """
    Name:       添加弱口令测试
    Condition:
    Steps:      1、启动进Setup菜单，添加长度为[8,16]不满足密码复杂度要求口令，检查能否成功，有结果A；
                2、添加长度为[8,16]满足密码复杂度要求口令，检查能否成功，有结果A；
                3、添加长度小于8满足密码复杂度要求口令，检查能否成功，有结果B；
                4、添加长度大于16满足密码复杂度要求口令，检查能否成功，有结果C；
                5、F10保存重启进入Setup菜单修改管理员密码为刚添加的弱口令密码，检查能否成功，有结果D。
    Result:     A：添加成功，显示所有弱口令清单；
                B：添加失败，提示不满足长度要求；
                C：最大支持16字符，超过之后无法输入；
                D：修改失败，提示不能设置弱口令密码。
    Remark:     1、弱口令不检查口令复杂度，只检查密码长度。
    """
    pw_1 = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN - 4)
    pw_2 = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    pw_3 = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN - 5)
    pw_4 = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MAX - 3)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        for try_pw in [pw_1, pw_2, pw_3, pw_4]:
            result = False if try_pw in [pw_3] else True
            expect_pw = try_pw[:PW.MAX]
            assert PwdLib.add_weak_pw_and_verify(try_pw, result, confirm_pw=expect_pw, expect=PwdLib.pw_weak_short)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2357", "[TC2357] Testcase_WeakKeyList_005", "添加重复弱口令测试"))
def Testcase_WeakKeyList_005():
    """
    Name:       添加重复弱口令测试
    Condition:
    Steps:      1、启动进Setup菜单，添加弱口令清单中已有的弱口令a，检查能否成功，有结果A；
                2、F10保存重启进入Setup菜单修改管理员密码为弱口令密码a，检查能否成功，有结果B。
    Result:     A：添加失败，提示弱口令已在列表中；【需求变更】 添加重复的弱密码，会提示删除弱密码
                B：修改失败，提示不能修改为弱口令密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN - 4)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=False, expect=PwdLib.pw_weak_same)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_is_weak)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2358", "[TC2358] Testcase_WeakKeyList_006", "添加当前密码为弱口令测试"))
def Testcase_WeakKeyList_006():
    """
    Name:       添加当前密码为弱口令测试
    Condition:  1、已设置管理员密码。
    Steps:      1、启动进Setup菜单，添加当前管理员密码为弱口令，检查能否成功，有结果A；
                2、F10保存重启后使用当前密码登录Setup菜单，检查能否登录，有结果B。
    Result:     A：添加成功，显示所有弱口令清单；
                B：登录成功。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(PW.ADMIN, result=True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2359", "[TC2359] Testcase_WeakKeyList_007", "添加弱口令立即生效"))
def Testcase_WeakKeyList_007():
    """
    Name:       添加弱口令立即生效
    Condition:
    Steps:      1、启动进Setup菜单，添加长度为[8,16]满足密码复杂度要求口令a，检查能否成功，有结果A；
                2、菜单修改管理员密码为刚添加的弱口令密码a，检查能否成功，有结果B。；
                3、F10保存重启进入Setup菜单修改管理员密码为刚添加的弱口令密码，检查能否成功，有结果B。
    Result:     A：添加成功，显示所有弱口令清单；
                B：修改失败，提示不能修改为弱口令密码。
    Remark:     1、添加弱口令立即生效。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN - 4)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_is_weak)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2360", "[TC2360] Testcase_WeakKeyList_008", "弱口令数目限制测试"))
def Testcase_WeakKeyList_008():
    """
    Name:       弱口令数目限制测试
    Condition:  1、已明确弱口令字典支持最大弱口令数量a。
    Steps:      1、启动进Setup菜单，反复添加弱口令，检查能否成功，有结果A；
                2、F10保存重启进入Setup菜单修改管理员密码为新增加的弱口令密码，检查能否成功，有结果B。
    Result:     A：添加成功，显示所有弱口令清单，达到最大数目a后无法继续添加；
                B：修改失败，提示不能修改为弱口令密码。
    Remark:
    """
    weak_list = [PwdLib.gen_pw(total=PW.MIN) for _ in range(PW.WEAK_CNT + 1)]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        for index, pw in enumerate(weak_list):
            logging.info(f"Weak password index: [{index}]")
            if index in range(PW.WEAK_CNT):  # 0 - 99
                assert PwdLib.add_weak_pw_and_verify(pw, result=True)
            else:  # >= 100
                assert PwdLib.add_weak_pw_and_verify(pw, result=False, expect=PwdLib.pw_weak_full)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2361", "[TC2361] Testcase_WeakKeyList_009", "删除默认清单弱口令测试"))
def Testcase_WeakKeyList_009():
    """
    Name:       删除默认清单弱口令测试
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，删除默认弱口令清单中的弱口令a，检查能否成功，有结果A；
                2、F10保存重启后进入Setup检查口令a是否在弱口令列表显示，有结果B；
                3、修改管理员用户密码为a，检查能否成功，有结果C；
    Result:     A：删除成功；
                B：已删除的弱口令不再显示在弱口令列表中；
                C：口令a满足复杂度要求，则修改成功；不满足复杂度要求，修改失败。
    Remark:
    """
    try:
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        # result A
        choose_weak_pw = PwdLib.del_default_weak_pw_and_verify()
        # step 2
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], Key.UP)
        # result B
        all_weak_pw = SetUpLib.get_all_options(span=1)
        assert choose_weak_pw not in all_weak_pw, f"Weak pw found in list after delete and save: {choose_weak_pw}"
        # step 3
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        # result C
        set_result = PwdLib.pw_is_valid(choose_weak_pw)
        assert PwdLib.set_admin_password(choose_weak_pw, PW.ADMIN, result=set_result, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2362", "[TC2362] Testcase_WeakKeyList_010", "删除新增弱口令测试"))
def Testcase_WeakKeyList_010():
    """
    Name:       删除新增弱口令测试
    Condition:  1、已新增弱口令a。
    Steps:      1、启动进Setup菜单，删除新增弱口令a，检查能否成功，有结果A；
                2、F10保存重启后进入Setup检查口令a是否在弱口令列表显示，有结果B；
                3、修改管理员用户密码为a，检查能否成功，有结果C；
    Result:     A：删除成功；
                B：已删除的弱口令不再显示在弱口令列表中；
                C：口令a满足复杂度要求，则修改成功；不满足复杂度要求，修改失败。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        # condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # step 1
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result A
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.delete_weak_pw(pw_a)
        # step 2
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result B
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        page_options = SetUpLib.get_all_options(span=1)
        assert page_options
        assert pw_a not in page_options, "Weak pw is found after deleted"
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        set_result = PwdLib.pw_is_valid(pw_a)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=set_result, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2363", "[TC2363] Testcase_WeakKeyList_011", "删除弱口令立即生效"))
def Testcase_WeakKeyList_011():
    """
    Name:       删除弱口令立即生效
    Condition:
    Steps:      1、启动进Setup菜单，删除弱口令清单中的弱口令a，修改管理员密码为a，检查能否成功，有结果A。
    Result:     A：口令a满足复杂度要求，则修改成功；不满足复杂度要求，修改失败。
    Remark:     1、删除弱口令立即生效。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        choose_weak_pw = PwdLib.del_default_weak_pw_and_verify()
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        set_result = PwdLib.pw_is_valid(choose_weak_pw)
        if set_result:
            assert PwdLib.set_admin_pw_and_verify(choose_weak_pw, PW.ADMIN)
        else:
            assert PwdLib.set_admin_password(choose_weak_pw, PW.ADMIN, result=False, save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2364", "[TC2364] Testcase_WeakKeyList_012", "重置弱口令字典测试"))
def Testcase_WeakKeyList_012():
    """
    Name:       重置弱口令字典测试
    Condition:
    Steps:      1、启动进Setup菜单，添加长度为[8,16]的口令a，删除弱口令字典原有弱口令b；
                2、F10保存重启进入Setup菜单检查弱口令列表中口令a，b是否存在，有结果A；
                3、F9恢复默认后保存重启进入Setup菜单检查弱口令列表中口令a，b是否存在，弱口令列表是否恢复默认，有结果B。
    Result:     A：a存在，b不存在；
                B：a不存在，b存在，弱口令列表恢复默认。
    Remark:     1、F9/Clearcmos/Load Default/Load Custom Default均可重置弱口令字典。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        assert SetUpLib.back_to_setup_toppage()
        weak_b = PwdLib.del_default_weak_pw_and_verify()
        # step 2
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], Key.UP)
        # result A
        secure_options = SetUpLib.get_all_options(span=1)
        assert secure_options
        assert pw_a in secure_options, f"Add weak pw not found in weak list: {pw_a}"
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], Key.UP)
        default_options = SetUpLib.get_all_options(span=1)
        assert default_options
        assert weak_b not in default_options, f"Default weak pw found after delete and save: {weak_b}"
        # step 3
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result B
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], Key.UP)
        secure_options = SetUpLib.get_all_options(span=1)
        assert secure_options
        assert pw_a not in secure_options, f"Add weak pw found after load default: {pw_a}"
        assert SetUpLib.back_to_setup_toppage()
        default_options = PwdLib.get_default_weak_pw_list()
        assert default_options
        assert weak_b in default_options, f"Default weak pw not found after load default: {weak_b}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2365", "[TC2365] Testcase_WeakKeyList_013", "重置弱口令字典立即生效"))
def Testcase_WeakKeyList_013():
    """
    Name:       重置弱口令字典立即生效
    Condition:  1、已添加弱口令a，删除原有弱口令b。
    Steps:      1、F9恢复默认检查弱口令列表中口令a，b是否存在，弱口令列表是否恢复默认，有结果A；
                2、修改管理员密码为a，检查能否成功，有结果B；
                3、修改管理员密码为b，检查能否成功，有结果C；
                4、F10保存重启进入Setup菜单检查弱口令列表中口令a，b是否存在，弱口令列表是否恢复默认，有结果A。
    Result:     A：a不存在，b存在，弱口令列表恢复默认；
                B：修改成功；
                C：修改失败，提示不能修改为弱口令密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 6)
    try:
        # condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        assert SetUpLib.back_to_setup_toppage()
        weak_b = PwdLib.del_default_weak_pw_and_verify()
        # step 1 + result A
        assert SetUpLib.load_default_in_setup()
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        secure_options = SetUpLib.get_all_options(span=1)
        assert pw_a not in secure_options, f"custom add weak is found after load default: {pw_a}"
        assert SetUpLib.back_to_setup_toppage()
        default_list = PwdLib.get_default_weak_pw_list()
        assert weak_b in default_list, f"default weak pw is not found after delete and load default: {weak_b}"
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        # step 2 + result B
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=True, save=False)
        # step 3 + result C
        assert PwdLib.set_admin_password(weak_b, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_is_weak)
        # step 4 + result A
        SetUpLib.send_keys(Key.SAVE_RESET)
        PwdLib.update_current_pw(pw_admin=pw_a)
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        secure_options = SetUpLib.get_all_options(span=1)
        assert pw_a not in secure_options, f"custom add weak is found after load default: {pw_a}"
        assert SetUpLib.back_to_setup_toppage()
        default_list = PwdLib.get_default_weak_pw_list()
        assert weak_b in default_list, f"default weak pw is not found after delete and load default: {weak_b}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2366", "[TC2366] Testcase_WeakKeyList_014", "简易密码弱口令测试"))
def Testcase_WeakKeyList_014():
    """
    Name:       简易密码弱口令测试
    Condition:  1、已开启简易密码开关。
    Steps:      1、启动进Setup菜单，添加简易密码a为弱口令字典，修改管理员密码为a，有结果A；
                2、修改管理用户密码为非弱口令清单的简易密码，有结果B。
    Result:     A：修改失败，提示不能修改为弱口令密码；
                B：修改成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN)
    pw_b = PwdLib.gen_pw(digit=PW.MIN)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm, 15)
        SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=False, save=False, expect=PwdLib.pw_is_weak)
        assert PwdLib.set_admin_pw_and_verify(pw_b, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2367", "[TC2367] Testcase_WeakKeyList_016", "弱口令操作记录上报BMC"))
def Testcase_WeakKeyList_016():
    """
    Name:       弱口令操作记录上报BMC
    Condition:
    Steps:      1、启动进Setup菜单，添加口令到弱口令字典，F10保存重启检查BMC操作日志，有结果A；
                2、进Setup菜单，删除弱口令字典中口令，F10保存重启检查BMC操作日志，有结果B；
                3、进Setup菜单，重置弱口令字典，F10保存重启检查BMC操作日志，有结果C；
    Result:     A：存在添加弱口令的操作日志记录；
                B：存在删除弱口令的操作日志记录；
                C：存在重置弱口令的操作日志记录；
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, symbol=2, lower=PW.MIN - 6)
    add_weak = PwdLib.sec_add_weak
    del_weak = PwdLib.sec_del_weak
    reset_weak = PwdLib.sec_reset_weak
    try:
        # step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        bmc_time = BmcLib.get_bmc_datetime()
        assert PwdLib.add_weak_pw_and_verify(pw_a, result=True)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result A
        assert PlatMisc.bmc_log_exist(add_weak, bmc_time, security=True), "add weak not exist"
        # step 2
        bmc_time = BmcLib.get_bmc_datetime()
        assert SetUpLib.enter_menu([Msg.WEAK_PW_DICT], key=Key.UP)
        assert PwdLib.delete_weak_pw(pw_a)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result B
        assert PlatMisc.bmc_log_exist(del_weak, bmc_time, security=True), "del weak not exist"
        # step 3
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # result C
        assert PlatMisc.bmc_log_exist(reset_weak, bmc_time, security=True), "reset weak not exist"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2368", "[TC2368] Testcase_KeyValidityCheck_001", "密码有效期设置菜单测试"))
def Testcase_KeyValidityCheck_001():
    """
    Name:       密码有效期设置菜单测试
    Condition:
    Steps:      1、启动进Setup菜单，检查密码有效期设置菜单，有结果A。
    Result:     A：密码有效期设置菜单可设置，提供0天（表示不过期）、30天、60天、90天、180天、360天6种选择，默认180天。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.PW_EXPIRE_DATE) == Msg.VAL_PW_EXPIRE[0]  # index 0 is the default
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.PW_EXPIRE_DATE), Msg.VAL_PW_EXPIRE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("2369", "[TC2369] Testcase_KeyValidityCheck_002", "管理员密码有效期测试"))
def Testcase_KeyValidityCheck_002():
    """
    Name:       管理员密码有效期测试
    Condition:  1、已设置管理员密码为a，设置密码时RTC时间为b。
    Steps:      1、启动进Setup菜单，设置密码有效期为N天，RTC日期为b+N天；
                2、F10保存重启管理员登录Setup菜单，检查登录是否正常，有结果A；
                3、设置密码有效期为0天，F10保存重启管理员登录Setup菜单，检查登录是否正常，有结果B；
                4、N遍历30天、60天、90天、180天、360天，重复执行步骤1~3。
    Result:     A：正常登录，提示密码超期，建议修改；
                B：正常登录，不会提示密码超期。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)  # uniPwd修改密码不考虑有效期
    try:
        # step 4
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_a, PW.ADMIN)
        time_sut = BmcLib.get_bmc_datetime()
        for expire in Msg.VAL_PW_EXPIRE:
            # step 1 + step 2
            if expire.startswith("0"):
                continue
            assert SetUpLib.set_option_value(Msg.PW_EXPIRE_DATE, expire, save=True)
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
            day = "".join(re.findall("(\d+) ", expire))
            date_delta = MiscLib.date_time_delta(time_sut, days=int(day)+1)
            assert PlatMisc.set_rtc_time_linux(time_str=date_delta)
            BmcLib.force_reset()
            # result A
            assert SetUpLib.continue_to_pw_prompt()
            SetUpLib.send_data_enter(PW.ADMIN)
            assert SetUpLib.wait_msg(PwdLib.pw_is_expire, 30)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            # step 3
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.set_option_value(Msg.PW_EXPIRE_DATE, "0 day", save=True)
            assert SetUpLib.continue_to_pw_prompt()
            # result B
            SetUpLib.send_data_enter(PW.ADMIN)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2370", "[TC2370] Testcase_KeyValidityCheck_003", "普通用户密码有效期测试"))
def Testcase_KeyValidityCheck_003():
    """
    Name:       普通用户密码有效期测试
    Condition:  1、已设置普通用户密码为a（非默认密码），设置密码时RTC时间为b。
    Steps:      1、管理员登录Setup菜单，设置密码有效期为N天，RTC日期为b+N天；
                2、F10保存重启普通用户登录Setup菜单，检查登录是否正常，有结果A；
                3、重启系统管理员登录Setup菜单，设置密码有效期为0天，F10保存重启普通用户登录Setup菜单，检查登录是否正常，有结果B；
                4、N遍历30天、60天、90天、180天、360天，重复执行步骤1~3。
    Result:     A：正常登录，提示密码超期，建议修改；
                B：正常登录，不会提示密码超期。
    Remark:
    """
    pw_i = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.init_user_password(pw_a, pw_i)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        # step 4
        time_sut = BmcLib.get_bmc_datetime()
        for expire in Msg.VAL_PW_EXPIRE:
            # step 1 + step 2
            if expire.startswith("0"):
                continue
            assert SetUpLib.set_option_value(Msg.PW_EXPIRE_DATE, expire, save=True)
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
            day = "".join(re.findall("(\d+) ", expire))
            date_delta = MiscLib.date_time_delta(time_sut, days=int(day)+1)
            assert PlatMisc.set_rtc_time_linux(time_str=date_delta)
            # result A
            assert SetUpLib.boot_to_pw_prompt()
            SetUpLib.send_data_enter(PW.USER)
            assert SetUpLib.wait_msg(PwdLib.pw_is_expire, 30)
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            # step 3
            assert SetUpLib.boot_to_pw_prompt()
            SetUpLib.send_data_enter(PW.ADMIN)
            if SetUpLib.wait_msg(PwdLib.pw_is_expire, 1):
                SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.set_option_value(Msg.PW_EXPIRE_DATE, "0 day", save=True)
            assert SetUpLib.continue_to_pw_prompt()
            # result B
            SetUpLib.send_data_enter(PW.USER)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.get_bmc_datetime()
        PwdLib.delele_user_pw()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2371", "[TC2371] Testcase_KeyValidityCheck_004", "用户密码有效期独立判断"))
def Testcase_KeyValidityCheck_004():
    """
    Name:       用户密码有效期独立判断
    Condition:  1、已设置管理员、普通用户密码，且普通用户密码非默认密码。
    Steps:      1、通过修改密码前调整TRC时间的方式，设置管理员及普通用户密码，使得其中一个有效期 > 30天，另外一个有效期 < 30天；
                2、进入Setup菜单，设置密码有效期为：30天，F10保存重启；
                2、管理员或普通用户登录Setup菜单，有结果A。
    Result:     A：正常登录，仅当密码有效期 < 30天才会提示密码超期，> 30天不会提示密码超期。
    Remark:
    """
    pw_i = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        time_sut = BmcLib.get_bmc_datetime()
        date_delta = MiscLib.date_time_delta(time_sut, days=30)
        assert PlatMisc.set_rtc_time_linux(time_str=date_delta)   # user pw not expired, admin pw is expired
        assert PwdLib.init_user_password(pw_a, pw_i)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.PW_EXPIRE_DATE, Msg.VAL_PW_EXPIRE[2], save=True)  # 30 days
        assert SetUpLib.continue_to_pw_prompt()
        SetUpLib.send_data_enter(PW.ADMIN)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire, 30)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(PW.USER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2372", "[TC2372] Testcase_KeyValidityCheck_005", "默认密码不判断有效期"))
def Testcase_KeyValidityCheck_005():
    """
    Name:       默认密码不判断有效期
    Condition:  1、管理员已设置普通用户密码，设置密码时RTC时间为b。
    Steps:      1、管理员登录Setup菜单，设置密码有效期为N天，RTC日期为b+N天；
                2、F10保存重启普通用户登录Setup菜单，检查登录是否正常，有结果A；
                3、N遍历0天、30天、60天、90天、180天、360天，重复执行步骤1~2。
    Result:     A：正常登录，提示修改默认密码，不会提示密码超期。
    Remark:     1、管理员每次设置的普通用户密码即为普通用户的默认密码；
                2、管理员无默认密码。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        # step 3
        time_sut = BmcLib.get_bmc_datetime()
        for expire in Msg.VAL_PW_EXPIRE:
            # step 1
            day = "".join(re.findall("(\d+) ", expire))
            date_delta = MiscLib.date_time_delta(time_sut, days=int(day)+1)
            assert PlatMisc.set_rtc_time_linux(time_str=date_delta)
            assert SetUpLib.boot_to_pw_prompt()
            SetUpLib.send_data_enter(PW.ADMIN)
            if SetUpLib.wait_msg(PwdLib.pw_is_expire, 1):
                SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.set_option_value(Msg.PW_EXPIRE_DATE, expire, save=True)
            # step2 + result A
            assert PwdLib.continue_to_setup_with_pw(PW.USER, default=True)
            assert SetUpLib.boot_to_default_os()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2373", "[TC2373] Testcase_KeyValidityCheck_006", "密码超期上报BMC测试"))
def Testcase_KeyValidityCheck_006():
    """
    Name:       密码超期上报BMC测试
    Condition:  1、已设置管理员、普通用户密码，且普通用户密码非默认密码。
    Steps:      1、管理员用户登录Setup菜单，设置密码有效期及RTC时间，使管理员密码超过有效期，F10保存重启管理员登录Setup菜单，查看BMC安全日志，有结果A；
                1、管理员用户登录Setup菜单，设置普通用户密码及RTC时间，使普通用户密码超过有效期，F10保存重启普通用户登录Setup菜单，查看BMC操作日志，有结果A。
    Result:     A：BMC日志记录管理员密码过期告警；
                B：BMC日志记录普通用户密码过期告警；
    Remark:
    """
    pw_i = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    admin_expire = PwdLib.sec_admin_expire
    user_expire = PwdLib.sec_user_expire
    try:
        assert PwdLib.init_user_password(pw_a, pw_i)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        time_sut = BmcLib.get_bmc_datetime()
        expire_default_int = int("".join(re.findall(r"\d+", Msg.VAL_PW_EXPIRE[0])))
        date_delta = MiscLib.date_time_delta(time_sut, days=expire_default_int)
        assert PlatMisc.set_rtc_time_linux(time_str=date_delta)

        assert SetUpLib.boot_to_pw_prompt()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.ADMIN)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(admin_expire, time_now, security=True)

        assert SetUpLib.boot_to_pw_prompt()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.USER)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(user_expire, time_now, security=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2431", "[TC2431] Testcase_KeyValidityCheck_007", "redfish密码超期上报BMC测试"))
def Testcase_KeyValidityCheck_007():
    """
    Name:       redfish密码超期上报BMC测试
    Condition:  1、已设置管理员、普通用户密码，且普通用户密码非默认密码。
    Steps:      1、管理员用户登录Setup菜单，设置密码有效期及RTC时间，使管理员密码超过有效期，F10保存重启管理员登录Setup菜单，查看BMC安全日志，有结果A；
                1、管理员用户登录Setup菜单，设置普通用户密码及RTC时间，使普通用户密码超过有效期，F10保存重启普通用户登录Setup菜单，查看BMC操作日志，有结果A。
    Result:     A：BMC日志记录管理员密码过期告警；
                B：BMC日志记录普通用户密码过期告警；
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    user_change = PwdLib.sec_user_success
    admin_expire = PwdLib.sec_admin_expire
    user_expire = PwdLib.sec_user_expire
    try:
        assert PwdLib.change_pw_by_redfish("user", pw_a, old_pw='', result=True, sec_log=user_change)
        assert SetUpLib.boot_to_default_os()
        time_sut = BmcLib.get_bmc_datetime()
        expire_default_int = int("".join(re.findall(r"\d+", Msg.VAL_PW_EXPIRE[0])))
        date_delta = MiscLib.date_time_delta(time_sut, days=expire_default_int)
        assert PlatMisc.set_rtc_time_linux(time_str=date_delta)

        assert SetUpLib.boot_to_pw_prompt()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.ADMIN)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(admin_expire, time_now, security=True)

        assert SetUpLib.boot_to_pw_prompt()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.USER)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(user_expire, time_now, security=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2432", "[TC2432] Testcase_KeyValidityCheck_008", "uniPwd密码超期上报BMC测试"))
def Testcase_KeyValidityCheck_008():
    """
    Name:       uniPwd密码超期上报BMC测试
    Condition:  1、已设置管理员、普通用户密码，且普通用户密码非默认密码。
    Steps:      1、管理员用户登录Setup菜单，设置密码有效期及RTC时间，使管理员密码超过有效期，F10保存重启管理员登录Setup菜单，查看BMC安全日志，有结果A；
                1、管理员用户登录Setup菜单，设置普通用户密码及RTC时间，使普通用户密码超过有效期，F10保存重启普通用户登录Setup菜单，查看BMC操作日志，有结果A。
    Result:     A：BMC日志记录管理员密码过期告警；
                B：BMC日志记录普通用户密码过期告警；
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    user_change = PwdLib.sec_user_success
    admin_expire = PwdLib.sec_admin_expire
    user_expire = PwdLib.sec_user_expire
    try:
        assert PwdLib.change_pw_by_redfish("user", pw_b, old_pw='', result=True, sec_log=user_change)
        assert SetUpLib.boot_to_default_os()
        assert PwdLib.set_admin_pw_by_unipwd(pw_a, PW.ADMIN)
        time_sut = BmcLib.get_bmc_datetime()
        expire_default_int = int("".join(re.findall(r"\d+", Msg.VAL_PW_EXPIRE[0])))
        date_delta = MiscLib.date_time_delta(time_sut, days=expire_default_int)
        assert PlatMisc.set_rtc_time_linux(time_str=date_delta)

        assert SetUpLib.boot_to_pw_prompt()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(admin_expire, time_now, security=True)

        assert SetUpLib.boot_to_pw_prompt()
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.send_data_enter(PW.USER)
        assert SetUpLib.wait_msg(PwdLib.pw_is_expire)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(user_expire, time_now, security=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()
        PwdLib.delele_user_pw()
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("2374", "[TC2374] Testcase_BmcSetBiosRootPwd_001", "设置管理员密码功能测试"))
def Testcase_BmcSetBiosRootPwd_001():
    """
    Name:       设置管理员密码功能测试
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码（密码复杂度符合要求），检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置成功；
                C：新密码登录成功。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    admin_change = PwdLib.sec_admin_success
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=True, sec_log=admin_change)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2375", "[TC2375] Testcase_BmcSetBiosRootPwd_002", "设置管理员密码时旧密码错误"))
def Testcase_BmcSetBiosRootPwd_002():
    """
    Name:       设置管理员密码时旧密码错误
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，输入错误的旧密码，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（旧密码错误）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    old_wrong = PwdLib.sec_old_wrong
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, pw_b, result=False, sec_log=old_wrong)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2376", "[TC2376] Testcase_BmcSetBiosRootPwd_003", "设置管理员密码时旧密码为空"))
def Testcase_BmcSetBiosRootPwd_003():
    """
    Name:       设置管理员密码时旧密码为空
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，输入旧密码为空，新密码复杂度符合要求，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（密码错误）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(total=0)
    old_invalid = PwdLib.sec_old_invalid
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, pw_b, result=False, sec_log=old_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2377", "[TC2377] Testcase_BmcSetBiosRootPwd_004", "设置管理员密码为空测试"))
def Testcase_BmcSetBiosRootPwd_004():
    """
    Name:       设置管理员密码为空测试
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码为空，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（新密码无效）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(total=0)
    new_invalid = PwdLib.sec_admin_success  # 需求变更，新密码为空时，删除密码
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=True, sec_log=new_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2378", "[TC2378] Testcase_BmcSetBiosRootPwd_005", "设置管理员密码长度不符合要求"))
def Testcase_BmcSetBiosRootPwd_005():
    """
    Name:       设置管理员密码长度不符合要求
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码长度不满足要求（小于8或大于16），检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（新密码太短或太长）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN-7)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MAX-5)
    new_short = PwdLib.sec_new_short
    new_long = PwdLib.sec_new_long
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=False, sec_log=new_short)
        assert PwdLib.change_pw_by_redfish("admin", pw_b, PW.ADMIN, result=False, sec_log=new_long)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2379", "[TC2379] Testcase_BmcSetBiosRootPwd_006", "设置管理员密码复杂度不满足要求"))
def Testcase_BmcSetBiosRootPwd_006():
    """
    Name:       设置管理员密码复杂度不满足要求
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码复杂度不满足要求并下发，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（新密码太简单）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功；
                3、密码复杂度要求：
                必须包含如下至少三种字符的组合（其中特殊字符必须）:
                      －至少一个小写字母；
                      －至少一个大写字母；
                      －至少一个数字；
                      －至少一个特殊字符：`~!@#$%^&*()-_=+\|[{}];:'",<.>/?  和空格
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN-4)
    new_simple = PwdLib.sec_new_simple
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=False, sec_log=new_simple)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2380", "[TC2380] Testcase_BmcSetBiosRootPwd_007", "设置管理员密码为弱口令字典密码"))
def Testcase_BmcSetBiosRootPwd_007():
    """
    Name:       设置管理员密码为弱口令字典密码
    Condition:  1、Postman工具已安装；
                2、已知弱口令字典集合H。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码a∈H，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（新密码属于弱口令）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.pick_a_weak_password()
    new_weak = PwdLib.sec_new_weak
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=False, sec_log=new_weak)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2381", "[TC2381] Testcase_BmcSetBiosRootPwd_008", "设置管理员密码为历史密码"))
def Testcase_BmcSetBiosRootPwd_008():
    """
    Name:       设置管理员密码为历史密码
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码为历史密码，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（新密码不能与历史密码相同）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, symbol=2, lower=PW.MIN - 6)
    is_history = PwdLib.sec_is_history
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=True)
        assert PwdLib.change_pw_by_redfish("admin", Msg.BIOS_PASSWORD, PW.ADMIN, result=False, sec_log=is_history)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2382", "[TC2382] Testcase_BmcSetBiosRootPwd_009", "设置管理员密码与旧密码相似"))
def Testcase_BmcSetBiosRootPwd_009():
    """
    Name:       设置管理员密码与旧密码相似
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码与旧密码仅一个字符差异（字符顺序一致），检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（新旧密码至少2个字符不同）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix=Msg.BIOS_PASSWORD[:-1], total=len(Msg.BIOS_PASSWORD))
    two_more_diff = PwdLib.sec_two_more_diff
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=False, sec_log=two_more_diff)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2383", "[TC2383] Testcase_BmcSetBiosRootPwd_010", "设置管理员密码包含非法字符"))
def Testcase_BmcSetBiosRootPwd_010():
    """
    Name:       设置管理员密码包含非法字符
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码，设置新密码包含非法字符，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（密码不能包含非法字符）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功；
                3、特殊字符除了`~!@#$%^&*()-_=+\|[{}];:'",<.>/? 和空格之外均为非法字符
    """
    pw_a = PwdLib.gen_pw(prefix=Msg.BIOS_PASSWORD[:-1], suffix="。")
    invalid_char = PwdLib.sec_invalid_char
    try:
        assert PwdLib.change_pw_by_redfish("admin", pw_a, PW.ADMIN, result=False, sec_log=invalid_char)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2384", "[TC2384] Testcase_BmcSetBiosRootPwd_011", "设置管理员密码与用户密码一致"))
def Testcase_BmcSetBiosRootPwd_011():
    """
    Name:       设置管理员密码与用户密码一致
    Condition:  1、Postman工具已安装；
                2、已知用户密码为a。
    Steps:      1、通过Redfish修改BIOS管理员密码为a，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置失败（密码无效）；
                C：新密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_i = PwdLib.gen_pw(digit=2, upper=2, symbol=2, lower=PW.MIN-6)
    pw_a = PwdLib.gen_pw(digit=2, upper=2, symbol=2, lower=PW.MIN-6)
    user_admin_same = PwdLib.sec_new_invalid
    try:
        assert PwdLib.init_user_password(pw_a, pw_i)
        assert PwdLib.change_pw_by_redfish("admin", PW.USER, PW.ADMIN, result=False, login=True, sec_log=user_admin_same)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()
        PwdLib.delele_user_pw()


@core.test_case(("2385", "[TC2385] Testcase_BmcSetBiosRootPwd_012", "FirstLogin时设置管理员密码"))
def Testcase_BmcSetBiosRootPwd_012():
    """
    Name:       FirstLogin时设置管理员密码
    Condition:  1、全擦升级后下电；
                2、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS管理员密码（旧密码为空，新密码复杂度符合要求），检查下发是否成功，有结果A；
                2、上电单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS管理员密码设置成功；
                C：新密码登录成功。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "Supervisor",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(digit=2, upper=2, symbol=2, lower=PW.MIN - 6)
    pw_default = Msg.BIOS_PW_DEFAULT
    admin_success = PwdLib.sec_admin_success
    try:
        img = var.get("biosimage")
        if not img:
            img = Update.get_test_image(SutConfig.Env.BRANCH_LATEST)
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        assert PwdLib.change_pw_by_redfish("admin", pw_a, pw_default, result=True, login=True, sec_log=admin_success)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2386", "[TC2386] Testcase_BmcSetBiosUserPwd_001", "设置用户密码功能测试"))
def Testcase_BmcSetBiosUserPwd_001():
    """
    Name:       设置用户密码功能测试
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，旧密码为a，新密码复杂度符合要求，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置成功；
                C：新用户密码登录成功（默认普通用户密码会提示强制修改密码）。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    user_success = PwdLib.sec_user_success
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=True, sec_log=user_success, login=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2387", "[TC2387] Testcase_BmcSetBiosUserPwd_002", "设置用户密码时旧密码错误"))
def Testcase_BmcSetBiosUserPwd_002():
    """
    Name:       设置用户密码时旧密码错误
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，输入错误的旧密码，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（旧密码错误）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    old_wrong = PwdLib.sec_old_wrong
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, pw_c, result=False, sec_log=old_wrong)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2388", "[TC2388] Testcase_BmcSetBiosUserPwd_003", "设置用户密码时旧密码为空"))
def Testcase_BmcSetBiosUserPwd_003():
    """
    Name:       设置用户密码时旧密码为空
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，输入旧密码为空，新密码复杂度符合要求，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（密码错误）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(total=0)
    old_invalid = PwdLib.sec_old_invalid
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, pw_c, result=False, sec_log=old_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2389", "[TC2389] Testcase_BmcSetBiosUserPwd_004", "设置用户密码为空测试"))
def Testcase_BmcSetBiosUserPwd_004():
    """
    Name:       设置用户密码为空测试
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码为空，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（新密码无效）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(total=0)
    user_del_success = PwdLib.sec_user_success
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=False, sec_log=user_del_success, login=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2390", "[TC2390] Testcase_BmcSetBiosUserPwd_005", "设置用户密码长度不符合要求"))
def Testcase_BmcSetBiosUserPwd_005():
    """
    Name:       设置用户密码长度不符合要求
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码长度不满足要求（小于8或大于16），检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（新密码太短或太长）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 7)
    pw_c = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MAX - 5)
    new_short = PwdLib.sec_new_short
    new_long = PwdLib.sec_new_long
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=False, sec_log=new_short)
        assert PwdLib.change_pw_by_redfish("user", pw_c, PW.USER, result=False, sec_log=new_long)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2391", "[TC2391] Testcase_BmcSetBiosUserPwd_006", "设置用户密码复杂度不满足要求"))
def Testcase_BmcSetBiosUserPwd_006():
    """
    Name:       设置用户密码复杂度不满足要求
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码复杂度不满足要求并下发，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（新密码太简单）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功；
                3、密码复杂度要求：
                必须包含如下至少三种字符的组合（其中特殊字符必须）:
                      －至少一个小写字母；
                      －至少一个大写字母；
                      －至少一个数字；
                      －至少一个特殊字符：`~!@#$%^&*()-_=+\|[{}];:'",<.>/?  和空格
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN - 4)
    new_simple = PwdLib.sec_new_simple
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=False, sec_log=new_simple)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2392", "[TC2392] Testcase_BmcSetBiosUserPwd_007", "设置用户密码为弱口令字典密码"))
def Testcase_BmcSetBiosUserPwd_007():
    """
    Name:       设置用户密码为弱口令字典密码
    Condition:  1、Postman工具已安装；
                2、已知弱口令字典集合H；
                3、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码a∈H，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（新密码属于弱口令）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.pick_a_weak_password()
    new_weak = PwdLib.sec_new_weak
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=False, sec_log=new_weak)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2393", "[TC2393] Testcase_BmcSetBiosUserPwd_008", "设置用户密码为历史密码"))
def Testcase_BmcSetBiosUserPwd_008():
    """
    Name:       设置用户密码为历史密码
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码为历史密码，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（新密码不能与历史密码相同）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    is_history = PwdLib.sec_is_history
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=True)
        assert PwdLib.change_pw_by_redfish("user", pw_a, PW.USER, result=False, sec_log=is_history)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2394", "[TC2394] Testcase_BmcSetBiosUserPwd_009", "设置用户密码与旧密码相似"))
def Testcase_BmcSetBiosUserPwd_009():
    """
    Name:       设置用户密码与旧密码相似
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码与旧密码仅一个字符差异（字符顺序一致），检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（新旧密码至少2个字符不同）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix=pw_a[:-1], total=len(pw_a))
    two_more_diff = PwdLib.sec_two_more_diff
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=False, sec_log=two_more_diff)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2395", "[TC2395] Testcase_BmcSetBiosUserPwd_010", "设置用户密码包含非法字符"))
def Testcase_BmcSetBiosUserPwd_010():
    """
    Name:       设置用户密码包含非法字符
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a。
    Steps:      1、通过Redfish修改BIOS用户密码，设置新密码包含非法字符，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（密码不能包含非法字符）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功；
                3、特殊字符除了`~!@#$%^&*()-_=+\|[{}];:'",<.>/? 和空格之外均为非法字符
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix=pw_a[:-1], suffix="。")
    invalid_char = PwdLib.sec_invalid_char
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", pw_b, PW.USER, result=False, sec_log=invalid_char)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2396", "[TC2396] Testcase_BmcSetBiosUserPwd_011", "设置用户密码与管理员密码一致"))
def Testcase_BmcSetBiosUserPwd_011():
    """
    Name:       设置用户密码与管理员密码一致
    Condition:  1、Postman工具已安装；
                2、已创建用户密码a；
                3、已知管理员密码为b。
    Steps:      1、通过Redfish修改BIOS用户密码旧密码为a，新密码为b，检查下发是否成功，有结果A；
                2、重启单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置失败（密码无效）；
                C：新用户密码登录失败。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    user_admin_same = PwdLib.sec_new_invalid
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a)
        assert PwdLib.change_pw_by_redfish("user", PW.ADMIN, PW.USER, result=False, login=True, sec_log=user_admin_same)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()
        PwdLib.delele_user_pw()


@core.test_case(("2397", "[TC2397] Testcase_BmcSetBiosUserPwd_012", "无用户时设置用户密码"))
def Testcase_BmcSetBiosUserPwd_012():
    """
    Name:       无用户时设置用户密码
    Condition:  1、全擦升级后下电；
                2、Postman工具已安装。
    Steps:      1、通过Redfish修改BIOS用户密码（旧密码为空，新密码复杂度符合要求），检查下发是否成功，有结果A；
                2、上电单板，BMC Web观察安全日志记录，有结果B；
                3、按热键进FrontPage，使用新用户密码登录，检查登录情况，有结果C。
    Result:     A：设置密码下发成功；
                B：Web记录BIOS用户密码设置成功；
                C：新用户密码登录成功。
    Remark:     1、Redfish设置接口：: https://192.168.2.100/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword
                 Post数据:
                 {
                 "PasswordName": "User",
                 "OldPassword": "Admin@9000",
                 "NewPassword": "Admin@4321"
                }
                2、redfish不做密码检查，格式符合要求均能设置成功。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(total=0)
    user_success = PwdLib.sec_user_success
    try:
        assert PwdLib.change_pw_by_redfish("user", pw_a, pw_b, result=True, login=True, sec_log=user_success)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2398", "[TC2398] Testcase_ForceChangeDefaultPwd_001", "管理员无默认密码测试"))
def Testcase_ForceChangeDefaultPwd_001():
    """
    Name:       管理员无默认密码测试
    Condition:  1、全擦BIOS版本
    Steps:      1、启动时按热键登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、设置密码后登录Setup菜单重启，使用设置密码再次登录Setup菜单，检查登录前是否要求强制修改密码，有结果B。
    Result:     A：初次登录无密码，且要求设置密码；(需求变更, 初次登录有默认密码,并且提示修改)
                B：不要求强制修改。
    Remark:
    """
    bios_img = var.get("biosimage")
    if not bios_img:
        bios_img = Update.get_test_image(SutConfig.Env.BRANCH_LATEST)
    try:
        assert Update.flash_bios_bin_and_init(bios_img)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        if BmcLib.get_fw_version().BIOS != SutConfig.Env.BIOS_VER_LATEST:
            Update.flash_bios_bin_and_init(bios_img)


@core.test_case(("2399", "[TC2399] Testcase_ForceChangeDefaultPwd_002", "普通用户强制修改默认密码"))
def Testcase_ForceChangeDefaultPwd_002():
    """
    Name:       普通用户强制修改默认密码
    Condition:  1、管理员已设置普通用户密码a。
    Steps:      1、普通用户使用密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、修改密码为b后登录Setup菜单，重启后再次使用密码a登录Setup菜单，检查是否登录成功，有结果B;
                3、使用密码b登录Setup菜单，检查登录前是否提示修改密码，有结果C；
    Result:     A：提示默认密码，要求修改密码；
                B：密码错误，无法登录Setup；
                C：登录成功，无修改密码提示。
    Remark:     1、登录前修改密码立即生效，无需保存。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, to_user=True)
        assert PwdLib.set_user_pw_and_verify(pw_b, pw_a)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2400", "[TC2400] Testcase_ForceChangeDefaultPwd_003", "强制修改密码时重启测试"))
def Testcase_ForceChangeDefaultPwd_003():
    """
    Name:       强制修改密码时重启测试
    Condition:  1、管理员已设置普通用户密码a。
    Steps:      1、普通用户使用密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、修改密码未完成时重启系统，再次使用密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
    Result:     A：提示默认密码，要求修改密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_b, pw_a, result=True, save=False)
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(pw_a, pw_b, default=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2401", "[TC2401] Testcase_ForceChangeDefaultPwd_004", "强制修改密码复杂度检查"))
def Testcase_ForceChangeDefaultPwd_004():
    """
    Name:       强制修改密码复杂度检查
    Condition:  1、管理员已设置普通用户密码a。
    Steps:      1、普通用户使用密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、修改为不符合密码复杂度密码b，检查修改是否成功，能否登录Setup菜单，有结果B；
                3、修改为符合密码复杂度密码c，检查修改是否成功，能否登录Setup菜单，有结果B；
    Result:     A：提示默认密码，要求修改密码；
                B：修改失败，无法登录Setup；
                C：修改成功，能登录Setup。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(digit=2, upper=2, lower=PW.MIN - 4)
    pw_c = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_b, pw_a, result=False, save=True, expect=PwdLib.pw_simple)
        assert PwdLib.continue_to_setup_with_pw(pw_a, pw_b, to_user=True, default=True)
        assert PwdLib.set_user_pw_and_verify(pw_c, PW.USER)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2402", "[TC2402] Testcase_ForceChangeDefaultPwd_005", "强制修改密码遍历热键测试"))
def Testcase_ForceChangeDefaultPwd_005():
    """
    Name:       强制修改密码遍历热键测试
    Condition:  1、管理员已设置普通用户密码a。
    Steps:      1、启动按Del热键使用普通用户密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、重启按F6热键使用普通用户密码a进行SP启动，检查登录前是否提示修改密码，有结果A；
                3、重启按F11热键使用普通用户密码a登录BootManager，检查登录前是否提示修改密码，有结果A；
                4、启动按F12热键使用普通用户密码a进行PXE启动，检查登录前是否提示修改密码，有结果A；
    Result:     A：提示默认密码，要求修改密码；
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, login=True)
        for key, hotkey in {"Del": Key.DEL, "F6": Key.F6, "F11": Key.F11, "F12": Key.F12}.items():
            assert SetUpLib.boot_to_pw_prompt(hotkey), f"{key} test failed"
            SetUpLib.send_data_enter(pw_a)
            assert SetUpLib.wait_msg(f"{PwdLib.pw_is_default}|Please Enter Supervisor Password")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2403", "[TC2403] Testcase_ForceChangeDefaultPwd_006", "管理员多次修改普通用户密码"))
def Testcase_ForceChangeDefaultPwd_006():
    """
    Name:       管理员多次修改普通用户密码
    Condition:
    Steps:      1、管理员进Setup菜单，设置普通用户密码a，F10保存重启后使用密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、重启后管理员进Setup菜单，设置普通用户密码b，F10保存重启后使用密码b登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                3、重启后管理员进Setup菜单，设置普通用户密码c，F10保存重启后使用密码c登录Setup菜单，检查登录前是否提示修改密码，有结果A；
    Result:     A：提示默认密码，要求修改密码；
    Remark:     1、管理员设置普通用户密码即为普通用户默认密码。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        for pw in [pw_a, pw_b, pw_c]:
            assert PwdLib.admin_set_user_pw_default(pw, login=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2404", "[TC2404] Testcase_ForceChangeDefaultPwd_007", "强制修改密码日志上报"))
def Testcase_ForceChangeDefaultPwd_007():
    """
    Name:       强制修改密码日志上报
    Condition:  1、管理员已设置普通用户密码a。
    Steps:      1、普通用户使用密码a登录Setup菜单，检查登录前是否提示修改密码，有结果A；
                2、修改密码失败时，检查BMC是否有安全日志记录，有结果B；
                3、修改密码成功时，检查BMC是否有安全日志记录，有结果B；
    Result:     A：提示默认密码，要求修改密码；
                B：有安全日志记录。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, to_user=True)
        sut_time = BmcLib.get_bmc_datetime()
        assert PwdLib.set_user_password(PW.ADMIN, PW.USER, result=False, save=False, expect=PwdLib.pw_invalid)
        assert PlatMisc.bmc_log_exist(PwdLib.sec_user_change_fail, sut_time, security=True)
        sut_time = BmcLib.get_bmc_datetime()
        assert PwdLib.set_user_password(pw_b, PW.USER, result=True, save=True)
        assert PlatMisc.bmc_log_exist(PwdLib.sec_user_change_pass, sut_time, security=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2405", "[TC2405] Testcase_FirstLogin_003", "首次登陆失败时BMC恢复默认测试"))
def Testcase_FirstLogin_003():
    """
    Name:       首次登陆失败时BMC恢复默认测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动按热键登录Setup菜单，检查登录时是否需要设置密码，有结果A；
                2、设置新密码失败后BMC执行恢复默认命令，重启系统再次登录Setup菜单，检查登录时是否需要设置密码，有结果A。
    Result:     A：空密码登录，要求设置新密码。  # 需求变更,有默认密码
    Remark:     1、不支持删除密码，空密码只存在首次登陆场景；
                2、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    pw_a = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(Msg.BIOS_PW_DEFAULT, to_admin=True, default=True)
        assert PwdLib.set_admin_password(pw_a, Msg.BIOS_PW_DEFAULT, result=False, save=False)
        BmcLib.clear_cmos()
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(Msg.BIOS_PW_DEFAULT, to_admin=True, default=True)
        assert PwdLib.set_admin_pw_and_verify(Msg.BIOS_PASSWORD, Msg.BIOS_PW_DEFAULT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2406", "[TC2406] Testcase_FirstLogin_004", "首次启动不需要设置密码"))
def Testcase_FirstLogin_004():
    """
    Name:       首次启动不需要设置密码
    Condition:  1、全擦升级BIOS。
    Steps:      1、启动进OS，检查过程中是否需要设置密码，有结果A；
                2、重启系统，按热键进Setup菜单，检查登录时是否需要设置密码，有结果B。
    Result:     A：启动进OS，过程中不需要设置密码；
                B：空密码登录，要求设置新密码。  # 需求变更,有默认密码
    Remark:     1、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.boot_to_default_os()
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(Msg.BIOS_PW_DEFAULT, to_admin=True, default=True)
        assert PwdLib.set_admin_pw_and_verify(Msg.BIOS_PASSWORD, Msg.BIOS_PW_DEFAULT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2407", "[TC2407] Testcase_FirstLogin_005", "uniCfg恢复默认后登陆测试"))
def Testcase_FirstLogin_005():
    """
    Name:       uniCfg恢复默认后登陆测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）；
                2、装备包已上传至OS；
    Steps:      1、启动进OS，装备路径下执行./uniCfg -c命令恢复默认；
                2、重启系统，按热键进Setup菜单，检查登录时是否需要设置密码，有结果B。
    Result:     A：空密码登录，要求设置新密码。   # 需求变更,有默认密码
    Remark:     1、不支持删除密码，空密码只存在首次登陆场景；
                2、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.uni_command("-c")
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(Msg.BIOS_PW_DEFAULT, to_admin=True, default=True)
        assert PwdLib.set_admin_pw_and_verify(Msg.BIOS_PASSWORD, Msg.BIOS_PW_DEFAULT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2408", "[TC2408] Testcase_FirstLogin_006", "空密码上报BMC测试"))
def Testcase_FirstLogin_006():
    """
    Name:       空密码上报BMC测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动进OS，检查BMC Web界面是否有安全日志记录，有结果A；
                2、重启系统，按热键进Setup菜单，检查登录时BMC Web界面是否有安全日志记录，有结果B；
    Result:     A：存在系统无密码的安全日志记录；
                B：无安全日志记录。
    Remark:     1、不支持删除密码，空密码只存在首次登陆场景；
                2、仅空密码启动会上报日志，按热键走First login流程，不上报日志。
                3、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    try:
        assert PwdLib.delete_admin_pw(save=False)
        sut_time = BmcLib.get_bmc_datetime()
        assert SetUpLib.save_without_exit()
        PwdLib.update_current_pw(pw_admin="")
        assert PlatMisc.bmc_log_exist(PwdLib.sec_del_admin, sut_time, security=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2409", "[TC2409] Testcase_FirstLogin_007", "首次登陆要求设置密码遍历热键"))
def Testcase_FirstLogin_007():
    """
    Name:       首次登陆要求设置密码遍历热键
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动按Del热键登录Setup菜单，检查登录时是否需要设置密码，有结果A；
                2、重启按F6热键进行SP启动，检查登录时是否需要设置密码，有结果A；
                3、重启按F11热键登录BootManager，检查登录时是否需要设置密码，有结果A；
                4、启动按F12热键进行PXE启动，检查登录时是否需要设置密码，有结果A；
    Result:     A：空密码登录，要求设置新密码。  # 需求变更,全刷升级后有默认密码
    Remark:     1、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        for key, hotkey in {"Del": Key.DEL, "F6": Key.F6, "F11": Key.F11, "F12": Key.F12}.items():
            assert SetUpLib.boot_to_pw_prompt(hotkey), f"{key} test failed"
            SetUpLib.send_data_enter(Msg.BIOS_PW_DEFAULT)
            assert SetUpLib.wait_msg(PwdLib.pw_is_default, 10)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2410", "[TC2410] Testcase_FirstLogin_008", "首次登陆设置密码多次失败测试"))
def Testcase_FirstLogin_008():
    """
    Name:       首次登陆设置密码多次失败测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动按热键登录Setup菜单，检查登录时是否需要设置密码，有结果A；
                2、设置复杂度不满足要求的密码，检查能否设置成功，有结果B；
                3、设置复杂度不满足要求的密码，尝试三次以上，检查界面是否被锁定，有结果C；
    Result:     A：空密码登录，要求设置新密码；
                B：设置密码失败；
                C：界面不会锁定，一直提示设置新密码。
    Remark:     1、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    # 需求变更,更改测试步骤为: 删除管理员密码后,添加新管理员密码时,输入非法密码超过3次,预期仍然可以正常输入
    pw_a = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    pw_d = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.delete_admin_pw()
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for pw in [pw_a, pw_b, pw_c, pw_d]:
            assert PwdLib.set_admin_password(new_pw=pw, old_pw=None, result=False, save=False, expect=PwdLib.pw_simple)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2411", "[TC2411] Testcase_FirstLogin_009", "首次登陆失败后再次重启登陆测试"))
def Testcase_FirstLogin_009():
    """
    Name:       首次登陆失败后再次重启登陆测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动按热键登录Setup菜单，检查登录时是否需要设置密码，有结果A；
                2、设置复杂度不满足要求的密码失败后，重启系统再次登录Setup菜单，检查登录时是否需要设置密码，有结果A。
    Result:     A：空密码登录，要求设置新密码。
    Remark:     1、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid, 10)
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.wait_msg(PwdLib.pw_is_default, 10)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2412", "[TC2412] Testcase_FirstLogin_010", "首次登陆失败后Web升级测试"))
def Testcase_FirstLogin_010():
    """
    Name:       首次登陆失败后Web升级测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动按热键登录Setup菜单，检查登录时是否需要设置密码，有结果A；
                2、下电Web升级BIOS版本，升级完成后上电再次登录Setup菜单，检查登录时是否需要设置密码，有结果A。
    Result:     A：空密码登录，要求设置新密码。
    Remark:     1、设置新密码成功后会清除首次启动标志。此用例执行完后可先不设置密码，方便之后用例测试，否则需要全擦升级。
    """
    img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
    try:
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.wait_msg(PwdLib.pw_is_default, 10)
        hpm_img = PlatMisc.get_latest_hpm_bios()
        assert Update.update_bios_hpm(hpm_img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.continue_to_pw_prompt()
        SetUpLib.send_data_enter(Msg.BIOS_PW_DEFAULT)
        assert SetUpLib.wait_msg(PwdLib.pw_is_default, 10)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        if Update.flash_bios_bin_and_init(img):
            PwdLib.update_current_pw(pw_admin=Msg.BIOS_PASSWORD)


@core.test_case(("2413", "[TC2413] Testcase_FirstLogin_011", "首次登录设置新密码成功测试 "))
def Testcase_FirstLogin_011():
    """
    Name:       首次登录设置新密码成功测试
    Condition:  1、全擦升级BIOS（若首次启动未设置密码，则不需全擦升级）。
    Steps:      1、启动按热键登录Setup菜单，检查登录时是否需要设置密码，有结果A；
                2、设置复杂度满足要求的密码a，检查能否设置成功，有结果B；
                3、重启系统，按热键登录Setup菜单，检查登录时是否需要设置密码，使用密码a登录，检查是否成功，有结果C。
    Result:     A：空密码登录，要求设置新密码；
                B：设置密码成功，进入Setup菜单；
                C：不需要设置新密码，密码a登录成功。
    Remark:     1、设置新密码成功后会清除首次启动标志。
    """
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
        assert Update.flash_bios_bin_and_init(img)
        assert SetUpLib.boot_to_setup()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2414", "[TC2414] Testcase_ChangePassWord_001", "管理员修改自身密码需要验证旧密码"))
def Testcase_ChangePassWord_001():
    """
    Name:       管理员修改自身密码需要验证旧密码
    Condition:  1、已设置管理员密码a。
    Steps:      1、管理员登录Setup菜单，修改自身密码，检查修改前是否需要校验旧密码，有结果A；
                2、修改新密码为b，F10保存重启使用密码b登录Setup菜单，检查登录情况，有结果B。
    Result:     A：设置新密码前需要输入旧密码；
                B：密码b登录成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_a, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2415", "[TC2415] Testcase_ChangePassWord_002", "管理员修改普通用户密码不需要验证旧密码"))
def Testcase_ChangePassWord_002():
    """
    Name:       管理员修改普通用户密码不需要验证旧密码
    Condition:  1、已设置普通用户密码a。
    Steps:      1、管理员登录Setup菜单，修改普通用户密码，检查修改前是否需要校验旧密码，有结果A；
    Result:     A：直接设置新密码，不需要验证旧密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, login=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2416", "[TC2416] Testcase_ChangePassWord_003", "管理员修改普通用户密码为普通用户默认密码"))
def Testcase_ChangePassWord_003():
    """
    Name:       管理员修改普通用户密码为普通用户默认密码
    Condition:  1、已设置管理员密码a。
    Steps:      1、管理员登录Setup菜单，设置普通用户密码为b，F10保存重启普通用户登录Setup菜单，登录后检查是否有默认密码提示，有结果A；
                2、重启后管理员登录Setup菜单，设置普通用户密码为c，F10保存重启普通用户登录Setup菜单，登录后检查是否有默认密码提示，有结果A；
    Result:     A：登录后提示为默认密码，强制修改密码。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, login=True)
        assert PwdLib.admin_set_user_pw_default(pw_b, login=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2417", "[TC2417] Testcase_ChangePassWord_004", "管理员旧密码验证失败模糊提示"))
def Testcase_ChangePassWord_004():
    """
    Name:       管理员旧密码验证失败模糊提示
    Condition:  1、已设置管理员密码a，且存在历史密码b。
    Steps:      1、管理员登录Setup菜单，修改自身密码时旧密码输入复杂度不满足要求的密码，设置满足要求的新密码，检查错误提示，有结果A；
                2、旧密码输入长度不满足要求的密码，设置满足要求的新密码，检查错误提示，有结果A；
                3、旧密码输入弱口令字典密码，设置满足要求的新密码，检查错误提示，有结果A；
                4、重启后管理员登录Setup菜单，修改自身密码时旧密码输入历史密码b，设置满足要求的新密码，检查错误提示，有结果A；
    Result:     A：提示无效密码。
    Remark:     1、三次错误后锁定，无法再输入，需重启。
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_simple = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    pw_short = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN-7)
    pw_weak = random.choice(PW.WEAK_PW)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_b, pw_a)
        assert PwdLib.set_admin_password(pw_c, old_pw=pw_simple, result=None, save=False, expect=PwdLib.pw_invalid)
        assert PwdLib.set_admin_password(pw_c, old_pw=pw_short, result=None, save=False, expect=PwdLib.pw_invalid)
        assert PwdLib.set_admin_password(pw_c, old_pw=pw_weak, result=None, save=False, expect=PwdLib.pw_lock)
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.ADMIN, to_admin=True)
        assert PwdLib.set_admin_password(pw_c, old_pw=pw_weak, result=None, save=False, expect=PwdLib.pw_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2418", "[TC2418] Testcase_ChangePassWord_005", "管理员新密码设置失败明确提示"))
def Testcase_ChangePassWord_005():
    """
    Name:       管理员新密码设置失败明确提示
    Condition:  1、已设置管理员密码a，且存在历史密码b。
    Steps:      1、管理员登录Setup菜单，修改自身密码时输入正确的旧密码a，设置复杂度不满足要求的新密码，检查错误提示，有结果A；
                2、输入正确的旧密码a，设置长度不满足要求的新密码，检查错误提示，有结果B；
                3、输入正确的旧密码a，设置弱口令字典密码为新密码，检查错误提示，有结果C；
                4、重启后管理员登录Setup菜单，修改自身密码时输入正确的旧密码a，设置新密码为历史密码b，检查错误提示，有结果D；
                5、输入正确的旧密码a，同时设置新密码为a，检查错误提示，有结果E；
    Result:     A：提示密码复杂度不满足要求；
                B：提示密码长度不满足要求；
                C：提示无法设置弱口令字典密码；
                D：提示无法设置历史密码；
                E：提示新旧密码至少2个字符不一致。
    Remark:     1、三次错误后锁定，无法再输入，需重启。
    """
    pw_a = Msg.BIOS_PASSWORD
    pw_b = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_simple = PwdLib.gen_pw(prefix="Admin", digit=2, upper=2, lower=2)
    pw_short = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 7)
    pw_weak = random.choice(PW.WEAK_PW)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_b, old=pw_a)
        assert PwdLib.set_admin_password(pw_simple, old_pw=PW.ADMIN, result=False, save=False, expect=PwdLib.pw_simple)
        assert PwdLib.set_admin_password(pw_short, old_pw=PW.ADMIN, result=False, save=False, expect=PwdLib.pw_short)
        assert PwdLib.set_admin_password(pw_weak, old_pw=PW.ADMIN, result=False, save=False, expect=PwdLib.pw_is_weak)
        assert PwdLib.set_admin_password(pw_a, old_pw=PW.ADMIN, result=False, save=False, expect=PwdLib.pw_is_history)
        assert PwdLib.set_admin_password(PW.ADMIN, old_pw=PW.ADMIN, result=False, save=False, expect=PwdLib.pw_be_diff)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2419", "[TC2419] Testcase_ChangePassWord_006", "普通用户修改自身密码需要验证旧密码"))
def Testcase_ChangePassWord_006():
    """
    Name:       普通用户修改自身密码需要验证旧密码
    Condition:  1、已设置普通用户密码a。
    Steps:      1、普通用户登录Setup菜单，修改自身密码，检查修改前是否需要校验旧密码，有结果A；
                2、修改新密码为b，F10保存重启使用密码b登录Setup菜单，检查登录情况，有结果B。
    Result:     A：设置新密码前需要输入旧密码；
                B：密码b登录成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_b, PW.USER, result=True, save=True)
        assert PwdLib.continue_to_setup_with_pw(pw_b, to_user=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2420", "[TC2420] Testcase_ChangePassWord_007", "普通用户旧密码验证失败模糊提示"))
def Testcase_ChangePassWord_007():
    """
    Name:       普通用户旧密码验证失败模糊提示
    Condition:  1、已设置普通用户密码a。
    Steps:      1、普通用户登录Setup菜单，修改自身密码时旧密码输入复杂度不满足要求的密码，设置满足要求的新密码，检查错误提示，有结果A；
                2、旧密码输入长度不满足要求的密码，设置满足要求的新密码，检查错误提示，有结果A；
                3、旧密码输入弱口令字典密码，设置满足要求的新密码，检查错误提示，有结果A；
                4、重启后普通用户登录Setup菜单，修改自身密码时旧密码输入历史密码b，设置满足要求的新密码，检查错误提示，有结果A；
    Result:     A：提示无效密码。
    Remark:     1、三次错误后锁定，无法再输入，需重启。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_c = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_simple = PwdLib.gen_pw(prefix="User", digit=2, upper=2, lower=2)
    pw_short = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 7)
    pw_weak = random.choice(PW.WEAK_PW)
    try:
        assert PwdLib.init_user_password(pw_a, pw_b)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_c, old_pw=pw_simple, result=None, save=False, expect=PwdLib.pw_invalid)
        assert PwdLib.set_user_password(pw_c, old_pw=pw_short, result=None, save=False, expect=PwdLib.pw_invalid)
        assert PwdLib.set_user_password(pw_c, old_pw=pw_weak, result=None, save=False, expect=PwdLib.pw_lock)
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True)
        assert PwdLib.set_user_password(pw_c, old_pw=pw_b, result=None, save=False, expect=PwdLib.pw_invalid)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2421", "[TC2421] Testcase_ChangePassWord_008", "普通用户新密码设置失败明确提示"))
def Testcase_ChangePassWord_008():
    """
    Name:       普通用户新密码设置失败明确提示
    Condition:  1、已设置普通用户密码a。
    Steps:      1、普通用户登录Setup菜单，修改自身密码时输入正确的旧密码a，设置复杂度不满足要求的新密码，检查错误提示，有结果A；
                2、输入正确的旧密码a，设置长度不满足要求的新密码，检查错误提示，有结果B；
                3、输入正确的旧密码a，设置弱口令字典密码为新密码，检查错误提示，有结果C；
                4、重启后普通用户登录Setup菜单，修改自身密码时输入正确的旧密码a，设置新密码为历史密码b，检查错误提示，有结果D；
                5、输入正确的旧密码a，同时设置新密码为a，检查错误提示，有结果E；
    Result:     A：提示密码复杂度不满足要求；
                B：提示密码长度不满足要求；
                C：提示无法设置弱口令字典密码；
                D：提示无法设置历史密码;
                E：提示新旧密码至少2个字符不一致。
    Remark:     1、三次错误后锁定，无法再输入，需重启。
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_simple = PwdLib.gen_pw(prefix="User", digit=2, upper=2, lower=2)
    pw_short = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=PW.MIN - 7)
    pw_weak = random.choice(PW.WEAK_PW)
    try:
        assert PwdLib.init_user_password(pw_a, pw_b)
        assert PwdLib.continue_to_setup_with_pw(pw_a, to_user=True)
        assert PwdLib.set_user_password(pw_simple, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_simple)
        assert PwdLib.set_user_password(pw_short, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_short)
        assert PwdLib.set_user_password(pw_weak, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_is_weak)
        assert PwdLib.set_user_password(pw_b, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_is_history)
        assert PwdLib.set_user_password(PW.USER, old_pw=PW.USER, result=False, save=False, expect=PwdLib.pw_be_diff)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2422", "[TC2422] Testcase_BruteForce_001", "登录防爆力破解"))
def Testcase_BruteForce_001():
    """
    Name:       登录防爆力破解
    Condition:  1、已设置管理员密码。
    Steps:      1、启动按热键进Setup菜单，登录时输入三次错误密码，检查界面锁定情况，有结果A；
                2、重启后再次登录Setup菜单，登录时输入两次错误密码，第三次输入正确密码，检查是否登录成功，有结果B。
    Result:     A：登录界面被锁定，不响应任何按键操作；
                B：登录成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    try:
        assert SetUpLib.boot_to_pw_prompt()
        assert PwdLib.force_login_try(pw_wrong=pw_a)
        assert SetUpLib.boot_to_pw_prompt()
        assert PwdLib.force_login_try(pw_wrong=pw_a, pw_right=PW.ADMIN)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("2423", "[TC2423] Testcase_BruteForce_002", "登录防爆力破解遍历热键"))
def Testcase_BruteForce_002():
    """
    Name:       登录防爆力破解遍历热键
    Condition:  1、已设置管理员密码。
    Steps:      1、启动按Del热键登录Setup菜单，登录时输入三次错误密码，检查界面锁定情况，有结果A；
                2、重启按F6热键使进行SP启动，登录时输入三次错误密码，检查界面锁定情况，有结果A；
                3、重启按F11热键登录BootManager，登录时输入三次错误密码，检查界面锁定情况，有结果A；
                4、启动按F12热键进行PXE启动，登录时输入三次错误密码，检查界面锁定情况，有结果A；
    Result:     A：登录界面被锁定，不响应任何按键操作；
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    try:
        for key_name, hotkey in {"Del": Key.DEL, "F6": Key.F6, "F11": Key.F11, "F12": Key.F12}.items():
            assert SetUpLib.boot_to_pw_prompt(hotkey), f"{key_name} boot failed"
            assert PwdLib.force_login_try(pw_wrong=pw_a)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("2424", "[TC2424] Testcase_BruteForce_003", "PowerOnPassword防爆力破解"))
def Testcase_BruteForce_003():
    """
    Name:       PowerOnPassword防爆力破解
    Condition:  1、已设置管理员密码。
    Steps:      1、启动进Setup菜单，使能PowerOnPassword选项，F10保存重启；
                2、登录系统时输入三次错误密码，检查界面锁定情况，有结果A；
                3、重启后再登录时输入两次错误密码，第三次输入正确密码，检查是否登录成功，有结果B。
    Result:     A：登录界面被锁定，不响应任何按键操作；
                B：登录成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.POWER_ON_PW, Msg.ENABLE, save=True)
        assert SetUpLib.wait_boot_msgs(Msg.PW_PROMPT)
        assert PwdLib.force_login_try(pw_wrong=pw_a)
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.PW_PROMPT)
        assert PwdLib.force_login_try(pw_wrong=pw_a, pw_right=PW.ADMIN)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2425", "[TC2425] Testcase_BruteForce_004", "管理员修改自身密码防爆力破解"))
def Testcase_BruteForce_004():
    """
    Name:       管理员修改自身密码防爆力破解
    Condition:  1、已设置管理员密码a。
    Steps:      1、管理员登录Setup菜单，修改自身密码时输入错误的旧密码，设置符合要求的新密码，错误三次，检查界面锁定情况，有结果A；
                2、重启管理员登录Setup菜单，修改自身密码时输入错误的旧密码，设置符合要求的新密码，错误两次后第三次输入正确旧密码a，设置新密码b，检查密码设置是否成功，有结果B；
                3、F10保存重启使用密码b登录Setup菜单，检查登录情况，有结果C。
    Result:     A：登录界面被锁定，不响应任何按键操作；1
                B：密码设置成功，提示保存重启生效；
                C：登录成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    pw_wrong = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for i in range(3):
            if i < 2:
                assert PwdLib.set_admin_password(pw_a, old_pw=pw_wrong, result=None, save=False, expect=PwdLib.pw_invalid)
            else:
                assert PwdLib.set_admin_password(pw_a, old_pw=pw_wrong, result=None, save=False, expect=PwdLib.pw_lock)
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for i in range(3):
            if i < 2:
                assert PwdLib.set_admin_password(pw_a, old_pw=pw_wrong, result=None, save=False, expect=PwdLib.pw_invalid)
            else:
                assert PwdLib.set_admin_pw_and_verify(pw_a, old=PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2426", "[TC2426] Testcase_BruteForce_005", "普通用户修改自身密码防爆力破解"))
def Testcase_BruteForce_005():
    """
    Name:       普通用户修改自身密码防爆力破解
    Condition:  1、已设置普通用户密码a。
    Steps:      1、普通用户登录Setup菜单，修改自身密码时输入错误的旧密码，设置符合要求的新密码，错误三次，检查界面锁定情况，有结果A；
                2、重启普通用户登录Setup菜单，修改自身密码时输入错误的旧密码，设置符合要求的新密码，错误两次后第三次输入正确旧密码a，设置新密码b，检查密码设置是否成功，有结果B；
                3、F10保存重启使用密码b登录Setup菜单，检查登录情况，有结果C。
    Result:     A：登录界面被锁定，不响应任何按键操作；
                B：密码设置成功，提示保存重启生效；
                C：登录成功。
    Remark:
    """
    pw_a = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_b = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    pw_wrong = PwdLib.gen_pw(prefix="User@", digit=2, upper=2, lower=2)
    try:
        assert PwdLib.admin_set_user_pw_default(pw_a, to_user=True)
        for i in range(3):
            if i < 2:
                assert PwdLib.set_user_password(pw_b, old_pw=pw_wrong, result=None, save=False, expect=PwdLib.pw_invalid)
            else:
                assert PwdLib.set_user_password(pw_b, old_pw=pw_wrong, result=None, save=False, expect=PwdLib.pw_lock)
        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(PW.USER, to_user=True, default=True)
        for i in range(3):
            if i < 2:
                assert PwdLib.set_user_password(pw_b, old_pw=pw_wrong, result=None, save=False, expect=PwdLib.pw_invalid)
            else:
                assert PwdLib.set_user_pw_and_verify(pw_b, old=PW.USER)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("2427", "[TC2427] Testcase_HttpsBoot_004", "Https IPv4启动_长时间"))
def Testcase_HttpsBoot_004():
    """
    Name:       Https IPv4启动_长时间
    Condition:  1、Https Boot设置为IPv4；
                2、Https Boot IPv4服务已开启，网络连接正常。
                3、客户端需导入证书。
    Steps:      1、启动时按F12选择Https Boot，检查启动情况，有结果A；
                2、反复启动100次，检查启动情况，有结果A；
    Result:     A：每次均能正常进OS。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.linux_tool_ready(Sys.PATH_CERT_OS, "Resource/HttpsCert/root.crt")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.set_option_value(Msg.HTTPS_BOOT, Msg.VAL_HTTPS_CAP[1])
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Msg.PAGE_SECURITY, key=Key.LEFT)
        assert SetUpLib.enter_menu(SutConfig.Sys.PATH_CERT)
        assert SetUpLib.locate_option('root.crt'), f"can't find root.crt"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option('Commit Changes and Exit')
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_msg('There is already an identical signature in signature list.'):
            SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        i = 0
        while i < 100:
            assert SetUpLib.boot_to_bootmanager()
            assert SetUpLib.locate_option(SutConfig.Sys.HTTP4_UEFI_DEV, refresh=True), f"{i}th times find HTTPS Boot devices fail"
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(SutConfig.Sys.HTTP4_UEFI_MSG), f"{i}th times HTTPS Boot fail"
            i = i + 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2428", "[TC2428] Testcase_HttpsBoot_007", "Https IPv6启动_长时间"))
def Testcase_HttpsBoot_007():
    """
    Name:       Https IPv6启动_长时间
    Condition:  1、Https Boot设置为IPv6；
                2、Https Boot IPv6服务已开启，网络连接正常。
                3、客户端需导入证书。
    Steps:      1、启动时按F12选择Https Boot，检查启动情况，有结果A；
                2、反复启动100次，检查启动情况，有结果A；
    Result:     A：每次均能正常进OS。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.linux_tool_ready(Sys.PATH_CERT_OS, "Resource/HttpsCert/root.crt")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.set_option_value(Msg.HTTPS_BOOT, Msg.VAL_HTTPS_CAP[2])
        assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu(SutConfig.Sys.PATH_CERT)
        assert SetUpLib.locate_option('root.crt'), f"can't find root.crt"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option('Commit Changes and Exit')
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_msg('There is already an identical signature in signature list.'):
            SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        i = 0
        while i < 100:
            assert SetUpLib.boot_to_bootmanager()
            assert SetUpLib.locate_option(SutConfig.Sys.HTTP6_UEFI_DEV, refresh=True), f"{i}th times find HTTPS Boot devices fail"
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.wait_msg(SutConfig.Sys.HTTP6_UEFI_MSG), f"{i}th times HTTPS Boot fail"
            i = i + 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

@core.test_case(("2429", "[TC2429] Testcase_HttpsBoot_002", "Https IPv4启动"))
def Testcase_HttpsBoot_002():
    """
    Name:       Https IPv4启动
    Condition:  1、Https Boot设置为IPv4；
                2、Https Boot IPv4服务已开启，网络连接正常。
                3、客户端需导入证书。
    Steps:      1、启动进Bootmanager界面，查看网口启动项显示，有结果A；
                2、指定网口Https启动，检查启动情况，有结果B；
    Result:     A、每个网口均存在Https Boot IPv4启动项；
                B、正常启动进OS
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.linux_tool_ready(Sys.PATH_CERT_OS, "Resource/HttpsCert/root.crt")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.set_option_value(Msg.HTTPS_BOOT, Msg.VAL_HTTPS_CAP[1])
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Msg.PAGE_SECURITY, key=Key.LEFT)
        assert SetUpLib.enter_menu(SutConfig.Sys.PATH_CERT)
        assert SetUpLib.locate_option('root.crt'), f"can't find root.crt"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option('Commit Changes and Exit')
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_msg('There is already an identical signature in signature list.', timeout=15):
            SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.locate_option(r'UEFI HTTPSv4:', order=Sys.NETWORK_PORT, exact=False, refresh=True)
        assert SetUpLib.locate_option(SutConfig.Sys.HTTP4_UEFI_DEV, refresh=True), f" find HTTPS Boot devices fail"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.HTTP4_UEFI_MSG),  f" HTTPS Boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2430", "[TC2430] Testcase_HttpsBoot_005", "Https IPv6启动"))
def Testcase_HttpsBoot_005():
    """
    Name:       Https IPv6启动
    Condition:  1、Https Boot设置为IPv6；
                2、Https Boot IPv6服务已开启，网络连接正常。
                3、客户端需导入证书。
    Steps:      1、启动进Bootmanager界面，查看网口启动项显示，有结果A；
                2、指定网口Https启动，检查启动情况，有结果B；
    Result:     A、每个网口均存在Https Boot IPv6启动项。
                B、正常启动进OS
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.linux_tool_ready(Sys.PATH_CERT_OS, "Resource/HttpsCert/root.crt")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.set_option_value(Msg.HTTPS_BOOT, Msg.VAL_HTTPS_CAP[2])
        assert SetUpLib.switch_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.enter_menu(SutConfig.Sys.PATH_CERT)
        assert SetUpLib.locate_option('root.crt'), f"can't find root.crt"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option('Commit Changes and Exit')
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_msg('There is already an identical signature in signature list.', timeout=15):
            SetUpLib.send_key(Key.ENTER)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.locate_option(r'UEFI HTTPSv6:', order=Sys.NETWORK_PORT, exact=False, refresh=True)
        assert SetUpLib.locate_option(SutConfig.Sys.HTTP6_UEFI_DEV, refresh=True), f" find HTTPS Boot devices fail"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.HTTP6_UEFI_MSG), f" HTTPS Boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

