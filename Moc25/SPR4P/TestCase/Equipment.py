
from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Equipment Test Case
# TC 2600-2629
####################################


# @core.test_case(("2600", "[TC2600] Testcase_EquipmentMode_003", "Web升级不清除装备标志位"))
# def Testcase_EquipmentMode_003():
#     """
#     Name:       Web升级不清除装备标志位
#     Condition:  1、已升级装备BIOS版本软件包；
#                 2、装备包已上传至OS；
#                 3、开启全打印开关。
#                 4、使用装备BMC、BIOS版本。
#     Steps:      1、OS装备路径下执行装备脚本Equipment_config.sh，脚本执行完成后执行命令 echo $? 检查脚本执行情况，有结果A；
#                 2、Web升级装备版本，重启系统串口日志检查装备标志位是否被清零，能否进入装备模式，有结果B；
#     Result:     A：echo $？结果为0，脚本执行成功；
#                 B：EquipMentModeFlag值为1，能进入装备模式。
#     Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2601", "[TC2601] Testcase_EquipmentTools_001", "uniCfg定制BIOS变量"))
def Testcase_EquipmentTools_001():
    """
    Name:       uniCfg定制BIOS变量
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已获取支持装备定制的变量列表。
    Steps:      1、启动进OS，装备包路径下执行./uniCfg -r VariableName命令（可在支持变量列表中随机选取一变量），检查读取是否成功，对比变量列表检查变量值是否在可选范围内，有结果A;
                2、执行./uniCfg -w VariableName:Value命令写入可选范围内其他值，检查是否修改成功，有结果B；
                3、执行./uniCfg -r VariableName命令再次读取，检查修改是否生效，有结果C；
                4、重启进Setup菜单，检查选项定制是否生效，有结果D。
    Result:     A：读取变量成功，无异常报错，变量值在范围内；
                B：修改成功，无异常报错；
                C：读取成功，为写入值；
                D：选项定制生效。
    Remark:     1、已获取支持装备定制的Setup变量列表。
    """
    exclude_list = ["pcie", "redfish:", "setSecureErase"]  # 有些特殊选项不能随机修改

    def pick_a_variable(var_dict):
        v_name = random.choice(list(variables.keys()))
        v_info = variables[v_name]
        v_values = v_info["values"]
        if any(integar in v_values for integar in ["min", "max", "step"]):  # 选择非数值型的变量
            return pick_a_variable(var_dict)
        if not v_info["unicfg"]:  # 选择支持uniCfg修改的变量
            return pick_a_variable(var_dict)
        if any(ex in v_name.lower() for ex in exclude_list):  # PCIE有些选项为自适应,修改后可能会不一致
            return pick_a_variable(var_dict)
        v_list = list(hex(int(v, 16))[2:] for v in v_info["values"].values())
        return v_name, v_list

    try:
        variables = PlatMisc.baseline_to_dict()
        var_name, var_val = pick_a_variable(variables)
        logging.info(f"Test option: {var_name} -> {var_val}")
        assert SetUpLib.boot_to_default_os()
        var_read = Sut.UNITOOL.read(var_name)[var_name]
        assert var_read in var_val, f"Unitool read value not in baseline scope: bseline={var_val}"
        if var_read in var_val:
            var_val.remove(var_read)
        var_value_set = random.choice(var_val)
        assert Sut.UNITOOL.write(**{var_name: var_value_set}), f"Unitool write value fail"
        assert Sut.UNITOOL.check(**{var_name: var_value_set}), f"Unitool check value fail"
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**{var_name: var_value_set}), f"Unitool check value fail after reboot"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2602", "[TC2602] Testcase_EquipmentTools_003", "uniCfg不支持定制SecureBoot"))
def Testcase_EquipmentTools_003():
    """
    Name:       uniCfg不支持定制SecureBoot
    Condition:  1、BIOS默认配置；
                2、装备包已上传到OS（装备支持的OS）；
                3、已获取支持装备定制的变量列表。
    Steps:      1、启动进OS，装备包路径下执行./uniCfg -r SecureBoot查看默认值，得结果A；
                2、执行./uniCfg -w SecureBoot:1，完成之后再读一次变量，查看修改是否生效,得结果A。
    Result:     A：无法读写变量，提示报错。
    Remark:
    """
    secure_boot = {"SecureBoot": 1}
    secure_res = {"SecureBoot": None}
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.read(*secure_boot) == secure_res, 'Get value before writing, fail'
        assert not Sut.UNITOOL.write(**secure_boot), 'unitool write fail'
        assert Sut.UNITOOL.read(*secure_boot) == secure_res, 'Get value after writing, fail'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2604", "[TC2604] Testcase_EquipmentTools_006", "uniCfg恢复变量默认值"))
def Testcase_EquipmentTools_006():
    """
    Name:       uniCfg恢复变量默认值
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已获取支持装备定制的变量列表。
    Steps:      1、启动进OS，装备包路径下执行./uniCfg -w VariableName:Value命令写入非默认值，检查是否成功，有结果A；
                2、重启进入Setup菜单，检查修改是否生效，有结果B；
                3、进入OS执行./uniCfg -c命令恢复默认，重启后进Setup菜单检查选项值，有结果C；
    Result:     A：修改成功，无异常报错；
                B：修改生效；
                C：选项已恢复默认值。
    Remark:     1、uniCfg -c执行后必须重启后才能进行菜单定制化，否则会导致系统异常。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        default = Sut.UNITOOL.read(*BiosCfg.HPM_KEEP)

        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)

        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)

        assert PlatMisc.uni_command("-c")
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**default)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2605", "[TC2605] Testcase_EquipmentTools_007", "uniCfg定制Logo"))
def Testcase_EquipmentTools_007():
    """
    Name:       uniCfg定制Logo
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、定制Logo已上传OS装备包路径。
    Steps:      1、启动进OS，装备包路径下执行./uniCfg -getlogo LogoFile命令，读取产品Logo，检查是否成功，检查读取的Logo与启动时是否一致，有结果A；
                2、执行./uniCfg -setlogo LogoFile命令，定制产品Logo，检查是否成功，有结果B；
                3、重启系统，检查启动过程中显示是否为定制Logo，有结果C。
    Result:     A：读取成功，与启动Logo一致；
                B：定制成功，无异常报错；
                C：显示为定制Logo。
    Remark:     1、设置的logo文件名可以更改，但文件必须是bmp格式，160*160(宽*高)，8位索引色，图片最大56KB。
    """
    try:
        origin_logo = PlatMisc.save_logo(path=Env.LOG_DIR, name="origin_logo")
        assert origin_logo, "fail to get origin_logo"

        assert SetUpLib.boot_to_default_os(reset=False)
        backup_logo = "logo_backup.bmp"
        assert PlatMisc.uni_command(f"-getlogo {backup_logo}")  # backup logo
        assert PlatMisc.unilogo_update(name="CustomLogo.bmp")

        modify_logo = PlatMisc.save_logo(path=Env.LOG_DIR, name="modify_logo")
        assert modify_logo, "fail to get modify_logo"
        assert not MiscLib.compare_images(modify_logo, origin_logo), "Modify logo should be different with origin logo"

        assert SetUpLib.boot_to_default_os(reset=False)
        assert PlatMisc.uni_command(f"-setlogo {backup_logo}")  # restore logo

        restore_logo = PlatMisc.save_logo(path=Env.LOG_DIR, name="restore_logo")
        assert restore_logo, "fail to get restore_logo"
        assert MiscLib.compare_images(restore_logo, origin_logo), "Restore logo should be same with origin logo"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PlatMisc.unilogo_update(name="Logo.bmp")


@core.test_case(("2606", "[TC2606] Testcase_EquipmentTools_008", "uniCfg定制Logo长时间测试"))
def Testcase_EquipmentTools_008():
    """
    Name:       uniCfg定制Logo长时间测试
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、定制Logo已上传OS。
    Steps:      1、启动进OS，装备包路径下执行./uniCfg -setlogo LogoFile命令，定制产品Logo，检查是否成功，有结果A；
                2、重启系统检查启动过程中显示是否为定制Logo，有结果B；
                3、重复步骤2多次。
    Result:     A：定制成功，无异常报错；
                B：显示为定制Logo。
    Remark:     1、设置的logo文件名可以更改，但文件必须是bmp格式，160*160(宽*高)，8位索引色，图片最大56KB。
    """
    origin_logo = PlatMisc.save_logo(path=SutConfig.Env.LOG_DIR, name="origin_logo")
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.unilogo_update(name="CustomLogo.bmp")
        # 重复3次,重启并检查logo修改结果
        for i in range(1, 4):
            modify_logo = PlatMisc.save_logo(path=SutConfig.Env.LOG_DIR, name="modify_logo")
            assert modify_logo
            assert not MiscLib.compare_images(modify_logo, origin_logo), "Modify logo should be different with origin logo"
            logging.info(f"No.{i} reset pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        PlatMisc.unilogo_update(name="Logo.bmp")


@core.test_case(("2607", "[TC2607] Testcase_EquipmentTools_009", "uniPwd定制合法密码"))
def Testcase_EquipmentTools_009():
    """
    Name:       uniPwd定制合法密码
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码a。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码为符合要求密码b，检查密码是否修改成功，有结果A；
                2、重启系统使用密码b登录Setup菜单，检查登录情况，有结果B。
    Result:     A：密码修改成功；
                B：登录成功。
    Remark:     1、uniPwd设置密码不检查弱口令字典和历史密码。
    """
    try:
        pw_equ = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2, symbol=2)
        assert SetUpLib.boot_to_default_os()
        assert PwdLib.set_admin_pw_by_unipwd(pw_equ, Msg.BIOS_PASSWORD)
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, password=pw_equ)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2608", "[TC2608] Testcase_EquipmentTools_010", "uniPwd多次定制合法密码测试"))
def Testcase_EquipmentTools_010():
    """
    Name:       uniPwd多次定制合法密码测试
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码a。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码为符合要求密码，检查密码是否修改成功，有结果A；
                2、多次定制符合要求的新密码，检查能否定制成功，有结果A；
                2、重启系统使用最终密码登录Setup菜单，检查登录情况，有结果B。
    Result:     A：密码修改成功；
                B：登录成功。
    Remark:     1、uniPwd设置密码不检查弱口令字典和历史密码。
    """
    try:
        pw_list = [PwdLib.gen_pw(prefix="Admin@", digit=i, upper=2, lower=2, symbol=1) for i in range(5)]
        assert SetUpLib.boot_to_default_os()
        for pw_i in pw_list:
            assert PwdLib.set_admin_pw_by_unipwd(pw_i, PW.ADMIN)
            assert PlatMisc.unipwd_tool(new_pw=pw_i, cmd="check")
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, password=pw_list[-1])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2609", "[TC2609] Testcase_EquipmentTools_011", "uniPwd定制新密码长度检查"))
def Testcase_EquipmentTools_011():
    """
    Name:       uniPwd定制新密码长度检查
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码长度小于8或大于16；
                2、检查密码是否修改成功，有结果A。
    Result:     A：密码修改失败，提示长度不符合要求。
    Remark:
    """
    try:
        pw_equ_7 = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PW.MIN - 1)
        pw_equ_17 = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=2, total=PW.MAX + 1)
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert not PwdLib.set_admin_pw_by_unipwd(pw_equ_7, PW.ADMIN), f'长度小于{PW.MIN}'
        assert not PwdLib.set_admin_pw_by_unipwd(pw_equ_17, PW.ADMIN), f'长度大于{PW.MAX}'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2610", "[TC2610] Testcase_EquipmentTools_012", "uniPwd定制新密码复杂度检查"))
def Testcase_EquipmentTools_012():
    """
    Name:       uniPwd定制新密码复杂度检查
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码长度满足要求[8,16]，复杂度不满足要求；
                2、检查密码是否修改成功，有结果A。
    Result:     A：密码修改失败，提示复杂度不符合要求。
    Remark:     1、口令必须包含如下至少两种字符的组合（特殊字符必须）：
                    －至少一个小写字母；
                    －至少一个大写字母；
                    －至少一个数字；
                    －至少一个特殊字符：`~!@#$%^&*()-_=+\|[{}];:'",<.>/?和空格。
    """
    try:
        pw_equ_7 = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, total=PW.MIN - 1)
        pw_equ_8 = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=1, total=PW.MIN)
        pw_equ_11 = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=1, total=PW.MIN + 3)
        pw_equ_16 = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=1, total=PW.MAX)
        pw_equ_17 = PwdLib.gen_pw(digit=2, upper=2, lower=2, symbol=1, total=PW.MAX + 1)

        assert SetUpLib.boot_to_default_os()
        assert not PwdLib.set_admin_pw_by_unipwd(pw_equ_7, PW.ADMIN), f'长度小于{PW.MIN}'
        assert not PwdLib.set_admin_pw_by_unipwd(pw_equ_17, PW.ADMIN), f'长度大于{PW.MAX}'

        assert PwdLib.set_admin_pw_by_unipwd(pw_equ_8, PW.ADMIN)
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, password=pw_equ_8)

        assert SetUpLib.boot_to_default_os()
        assert PwdLib.set_admin_pw_by_unipwd(pw_equ_11, PW.ADMIN)
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, password=pw_equ_11)

        assert SetUpLib.boot_to_default_os()
        assert PwdLib.set_admin_pw_by_unipwd(pw_equ_16, PW.ADMIN)
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, password=pw_equ_16)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2611", "[TC2611] Testcase_EquipmentTools_013", "uniPwd定制新密码为弱口令字典密码"))
def Testcase_EquipmentTools_013():
    """
    Name:       uniPwd定制新密码为弱口令字典密码
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码为弱口令字典中的密码a，检查密码是否修改成功，有结果A；
                2、重启系统使用密码a登录Setup菜单，检查登录情况，有结果B。
    Result:     A：密码修改成功；
                B：登录成功。
    Remark:     1、uniPwd设置密码不检查弱口令字典和历史密码。
    """
    try:
        pw_equ = PwdLib.pick_a_weak_password()
        assert SetUpLib.boot_to_default_os()
        assert PwdLib.set_admin_pw_by_unipwd(pw_equ, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2612", "[TC2612] Testcase_EquipmentTools_014", "uniPwd定制新密码为历史密码"))
def Testcase_EquipmentTools_014():
    """
    Name:       uniPwd定制新密码为历史密码
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码a，且存在历史密码b。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码为历史密码b，检查密码是否修改成功，有结果A；
                2、重启系统使用密码b登录Setup菜单，检查登录情况，有结果B。
    Result:     A：密码修改成功；
                B：登录成功。
    Remark:     1、uniPwd设置密码不检查弱口令字典和历史密码。
    """
    try:
        pw_a = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(pw_a, PW.ADMIN, result=True, save=True)  # generate history password

        assert SetUpLib.boot_to_default_os(reset=False)
        assert PwdLib.set_admin_pw_by_unipwd(Msg.BIOS_PASSWORD, PW.ADMIN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2613", "[TC2613] Testcase_EquipmentTools_015", "uniPwd定制密码时旧密码错误"))
def Testcase_EquipmentTools_015():
    """
    Name:       uniPwd定制密码时旧密码错误
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -set NewPwd OldPwd命令定制Setup认证密码，新密码满足要求，输入错误的旧密码；
                2、检查密码是否修改成功，有结果A。
    Result:     A：密码修改失败，提示密码错误。
    Remark:
    """
    try:
        pw_equ = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2, symbol=1)
        pw_old = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2)

        assert SetUpLib.boot_to_default_os()
        assert not PwdLib.set_admin_pw_by_unipwd(pw_equ, pw_old), '预期密码修改失败'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2614", "[TC2614] Testcase_EquipmentTools_016", "uniPwd定制简易密码"))
def Testcase_EquipmentTools_016():
    """
    Name:       uniPwd定制简易密码
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -sets NewPwd OldPwd命令定制Setup认证密码，新密码长度满足要求[8,16]，复杂度不满足要求，检查密码是否修改成功，有结果A；
                2、重启系统使用设置密码登录Setup菜单，检查登录情况，有结果B。
    Result:     A：密码修改成功；
                B：登录成功。
    Remark:
    """
    try:
        pw_equ = PwdLib.gen_pw(digit=PW.MIN)
        assert SetUpLib.boot_to_default_os()
        assert PwdLib.set_admin_pw_by_unipwd(pw_equ, PW.ADMIN, simple=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("2615", "[TC2615] Testcase_EquipmentTools_017", "uniPwd检查密码"))
def Testcase_EquipmentTools_017():
    """
    Name:       uniPwd检查密码
    Condition:  1、装备包已上传到OS（装备支持的OS）；
                2、已设置管理员密码a。
    Steps:      1、启动进OS，装备包路径下执行./uniPwd -check Pwd命令时输入正确的密码，检查是否正确，有结果A；
                2、输入错误的密码，检查是否正确，有结果B；
                3、执行./uniPwd -set NewPwd OldPwd命令设置新密码b，设置后再执行./uniPwd -check Pwd时输入密码a检查是否正确，有结果B；
                4、输入密码b检查是否正确，有结果A；
    Result:     A：密码检查正确；
                B：密码检查错误；
    Remark:
    """
    try:
        pw_equ = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=2, lower=2, symbol=1)
        assert SetUpLib.boot_to_default_os()

        assert PlatMisc.unipwd_tool(Msg.BIOS_PASSWORD, cmd='check')
        assert not PlatMisc.unipwd_tool(pw_equ, cmd='check'), '默认密码检查错误'

        assert PwdLib.set_admin_pw_by_unipwd(pw_equ, PW.ADMIN)

        assert not PlatMisc.unipwd_tool(Msg.BIOS_PASSWORD, cmd='check'), '旧密码检查错误'
        assert PlatMisc.unipwd_tool(pw_equ, cmd='check'), '新密码检查错误'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


# @core.test_case(("2616", "[TC2616] Testcase_EquipmentTools_025", "装备脚本定制BIOS测试"))
# def Testcase_EquipmentTools_025():
#     """
#     Name:       装备脚本定制BIOS测试
#     Condition:  1、装备包已上传到OS（装备支持的OS）；
#                 2、定制Logo已上传OS装备包路径，假定为test.bmp；
#                 3、使用装备BMC、BIOS版本。
#     Steps:      1、启动进OS，装备路径下创建配置文件customset.ini，文件内容格式如：
#                 BootOrder 1023  
#                 @uniPassword Admin123456!
#                 @uniLogoFile test.bmp
#                 保存后执行./common_config.sh脚本，检查执行情况，有结果A；
#                 2、执行./common_verify.sh脚本，检查校验情况，有结果B；
#                 3、重启在启动过程查看Logo是否定制成功，登录Setup菜单检查密码和变量是否定制成功，有结果C；
#     Result:     A：脚本执行成功，提示变量、Logo、密码均定制成功；
#                 B：脚本执行成功，提示变量、Logo、密码均校验成功；
#                 C：变量、Logo、密码均与定制一致。
#     Remark:     1、定制变量即自行选择；
#                 2、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2617", "[TC2617] Testcase_EquipmentTools_028", "装备脚本开启VMD"))
# def Testcase_EquipmentTools_028():
#     """
#     Name:       装备脚本开启VMD
#     Condition:  1、装备包已上传到OS（装备支持的OS）；
#                 2、使用装备BMC、BIOS版本。
#     Steps:      1、启动进OS，装备路径下执行./intel_VMD_Open.sh命令定制VMD选项，检查执行情况，有结果A；
#                 2、重启后进入Setup菜单，检查VMD是否已打开，有结果B；
#                 3、进OS后通过uniCfg再次检查VMD选项情况，有结果C。
#     Result:     A：脚本运行成功，VMD开启，且系统自动重启；
#                 B：VMD已开启；
#                 C：VMD已关闭。
#     Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2618", "[TC2618] Testcase_EquipmentTools_029", "装备脚本Margin测试"))
# def Testcase_EquipmentTools_029():
#     """
#     Name:       装备脚本Margin测试
#     Condition:  1、装备包已上传到OS（装备支持的OS）；
#                 2、使用装备BMC、BIOS版本。
#     Steps:      1、启动进OS，执行./memtest_config.sh使能装备标志位
#                 2、OS下执行以下几条命令后冷复位单板做Margin测试（V5单板）
#                 ./uniCfg -w EnableBiosSsaRMTonFCB:1 
#                 ./uniCfg -w RankMargin:0 
#                 ./uniCfg -w EnableBiosSsaRMT:1 
#                 ./uniCfg -w BiosSsaPerBitMargining:1 
#                 ./uniCfg -w BiosSsaDebugMessages:5 
#                 ./uniCfg -w SysDbgLevel:1
#                 3、保存一份串口日志，启动进OS，使用rw工具读取type128中Margin结果内存地址，对比内存中的Margin结果和串口打印的Margin结果中打印*的地方，有结果A。
#                 具体操作步骤：
#                 1）进入OS，敲dmidecode -t 128，获取第二个word32的值为00 60 2B 6E（该地址为小端模式）
#                 2）读取上面地址中内容 ./rw mmr 6E2B6000 2000 ，查看6E2B6510开始的一段非0值（十六进制）
#                 3）串口打印中搜索rank margin（十进制）
#                 4）将2）和3）中的值进行对比，有结果A
#                 
#     Result:     A：Margin测试结果正确。
#     Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2619", "[TC2619] Testcase_EquipmentModeCe_001", "装备模式下，触发MEM CE错误测试"))
# def Testcase_EquipmentModeCe_001():
#     """
#     Name:       装备模式下，触发MEM CE错误测试
#     Condition:  1、使用装备BMC、BIOS版本。
#     Steps:      1、启动进OS，设置装备标志，reboot；
#                 2、启动进OS，飞线注入ce错误，观察OS dmesg信息及FDM日志，有结果A。
#     Result:     A：OS运行正常，dmesg和FDM记录ce错误。
#     Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2620", "[TC2620] Testcase_EquipmentModeCe_002", "装备模式下，触发PCIE CE错误测试"))
# def Testcase_EquipmentModeCe_002():
#     """
#     Name:       装备模式下，触发PCIE CE错误测试
#     Condition:  1、使用装备BMC、BIOS版本。
#     Steps:      1、启动进OS，设置装备标志，reboot；
#                 2、启动进OS，ITP工具注入PCIE ce故障，观察OS运行情况及FDM日志，有结果A。
#     Result:     A：OS运行正常，dmesg和FDM记录ce错误。
#     Remark:     1、ITP工具PCIE ce故障注入错误，命令如下：
#                   halt()
#                   ei.resetInjcetorLockCheck()    ei.injectPcieError(0,0,errType="ce")
#                   ITP.go()
#                 2、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2621", "[TC2621] Testcase_EquipmentModeCe_003", "装备模式下，触发QPI CE错误测试"))
# def Testcase_EquipmentModeCe_003():
#     """
#     Name:       装备模式下，触发QPI CE错误测试
#     Condition:  1、使用装备BMC、BIOS版本。
#     Steps:      1、启动进OS，设置装备标志，reboot；
#                 2、启动进OS，ITP工具注入QPI ce故障，观察OS运行情况及FDM日志，有结果A。
#     Result:     A：OS运行正常，dmesg和FDM记录ce错误。
#     Remark:     1、ITP工具QPI ce故障注入错误，命令如下：
#                   halt()
#                   ei.resetInjcetorLockCheck()
#                   ei.injectQpiError(0,0,1)
#                   ITP.go()
#                 2、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2622", "[TC2622] Testcase_FtPxeBoot_001", "FT模式标志位检查"))
def Testcase_FtPxeBoot_001():
    """
    Name:       FT模式标志位检查
    Condition:  1、使用装备BMC、BIOS版本；
                2、BMC设置装备标志位；
                3、开启全打印。
    Steps:      1、启动进OS，检查串口打印信息是否进入装备Ft模式，有结果A；
                2、BMC关闭装备标志位，重启进OS，检查串口打印信息是否进入装备Ft模式，有结果B。
    Result:     A：系统进FT模式，串口打印 [FTModeDxe] FTModeDxeEntry；
                B：系统不进入FT模式，串口无 [FTModeDxe] FTModeDxeEntry打印；
    Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
                2、进入FT模式命令：
                maint_debug_cli
                setprop DftStatus.FTModeFlag 1
                3、测试完成后需退出FT模式，命令如下：
                maint_debug_cli
                setprop DftStatus.FTModeFlag 0
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.uni_command(f"-w {Attr.EQUIP_FLAG}:1")
        assert BmcLib.debug_message(enable=True), "debug message enable fail"
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.EQUIP_FLAG.format(1), timeout=Env.BOOT_FULL_DBG)

        assert MiscLib.ping_sut(Env.OS_IP, timeout=Env.BOOT_FULL_DBG)
        assert PlatMisc.uni_command(f"-w {Attr.EQUIP_FLAG}:0")
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.EQUIP_FLAG.format(0), timeout=Env.BOOT_FULL_DBG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        BmcLib.debug_message(enable=False)


# @core.test_case(("2623", "[TC2623] Testcase_FtPxeBoot_002", "FT模式不改变四大类启动顺序"))
# def Testcase_FtPxeBoot_002():
#     """
#     Name:       FT模式不改变四大类启动顺序
#     Condition:  1、使用装备BMC、BIOS版本；
#                 2、存在四大类启动项。
#     Steps:      1、启动进Setup菜单，Boot界面修改四大类启动顺序，假设为a，F10保存重启进BootManager，检查修改是否生效，有结果A；
#                 2、BMC设置装备标志位，启动进BootManager，检查启动顺序，有结果B。
#     Result:     A：启动顺序设置生效；
#                 B：四大类启动顺序不变，依然为a。
#     Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#                 2、进入FT模式命令：
#                 maint_debug_cli
#                 setprop DftStatus.FTModeFlag 1
#                 3、测试完成后需退出FT模式，命令如下：
#                 maint_debug_cli
#                 setprop DftStatus.FTModeFlag 0
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2624", "[TC2624] Testcase_FtPxeBoot_007", "装备模式启动测试"))
def Testcase_FtPxeBoot_007():
    """
    Name:       装备模式启动测试
    Condition:  1、使用装备BMC、BIOS版本；
                2、BMC已设置装备标志位。
    Steps:      1、启动进OS，检测启动过程有无反复重启、挂死、黑屏等异常现象，有结果A；
                2、OS下静置5min后再次操作，检查是否正常，有结果B；
                3、重复步骤1-2 3次。
    Result:     A：单板能正常启动，无反复重启、挂死、黑屏等异常现象；
                B：静置后OS下操作正常。
    Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
                2、进入FT模式命令：
                maint_debug_cli
                setprop DftStatus.FTModeFlag 1
                3、测试完成后需退出FT模式，命令如下：
                maint_debug_cli
                setprop DftStatus.FTModeFlag 0
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.uni_command(f"-w {Attr.EQUIP_FLAG}:1")
        BmcLib.force_reset()
        assert MiscLib.ping_sut(Env.OS_IP, Env.BOOT_DELAY)

        for times in range(2):
            time.sleep(300)
            assert SetUpLib.boot_to_default_os()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2625", "[TC2625] Testcase_FtPxeBoot_008", "装备模式热键操作"))
def Testcase_FtPxeBoot_008():
    """
    Name:       装备模式热键操作
    Condition:  1、使用装备BMC、BIOS版本；
                2、BMC已设置装备标志位。
    Steps:      1、启动至热键界面，按Del键，检查能否正常进入FrontPage，有结果A；
                2、重启至热键界面，按F11，检查能否正常进入BootManager界面，有结果B；
                3、遍历所有支持的热键，检查是否符合预期，有结果C。
    Result:     A：能正常进入Frontpage界面，无挂死现象；
                B：能正常进入BootManager，无挂死现象；
                C：所有热键符合预期，无挂死现象。
    Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
                2、进入FT模式命令：
                maint_debug_cli
                setprop DftStatus.FTModeFlag 1
                3、测试完成后需退出FT模式，命令如下：
                maint_debug_cli
                setprop DftStatus.FTModeFlag 0
    """
    keys_info = [[Key.DEL, Msg.HOME_PAGE],
                  [Key.F6, Msg.F6_CONFIRM_UEFI],
                  [Key.F11, Msg.BOOT_MANAGER],
                  [Key.F12, SutConfig.Sys.PXE_UEFI_MSG]]
    try:
        for key in keys_info:
            assert SetUpLib.boot_to_default_os()
            assert PlatMisc.uni_command(f"-w {Attr.EQUIP_FLAG}:1")
            assert SolLib.boot_with_hotkey(key=key[0], confirm=key[1])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("2626", "[TC2626] Testcase_FtPxeBoot_009", "装备模式下板卡识别"))
# def Testcase_FtPxeBoot_009():
#     """
#     Name:       装备模式下板卡识别
#     Condition:  1、使用装备BMC、BIOS版本；
#                 2、BMC已设置装备标志位。
#     Steps:      1、启动进Setup菜单，IIO界面检测网卡对应port，link状态及带宽是否正确，有结果A；
#                 2、BMC WEB界面查看板卡信息（厂家、型号、资源归属、所在slot号等）是否正确，有结果B；
#                 3、启动进OS，执行"lspci -tv"命令检查设备是否识别，有结果C。
#     Result:     A：板卡对应Port link在位，带宽与实际一致；
#                 B：板卡信息正确，资源归属、slot号与实际一致；
#                 C：板卡设备能正常识别。
#     Remark:     1、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#                 2、进入FT模式命令：
#                 maint_debug_cli
#                 setprop DftStatus.FTModeFlag 1
#                 3、测试完成后需退出FT模式，命令如下：
#                 maint_debug_cli
#                 setprop DftStatus.FTModeFlag 0
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2627", "[TC2627] Testcase_MemoryBomId_002", "内存BOM ID上报BMC测试"))
# def Testcase_MemoryBomId_002():
#     """
#     Name:       内存BOM ID上报BMC测试
#     Condition:  1、内存已写入BOM ID；
#                 2、使用装备BMC、BIOS版本。
#     Steps:      1、查看BMC Web界面内存信息，与SMBIOS Type17中的内存信息进行对比，有结果A。
#     Result:     A：BMC Web正确显示内存BOM ID。
#     Remark:     1、内存BOM ID对应Type17 Assert Tag字段后8个字节；
#                 2、BIOS版本格式a.b.c，其中a为2表示上网版本，1表示装备版本；BMC版本格式a.b.c.d，其中d为奇数表示上网版本，偶数表示装备版本；
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2628", "[TC2628] Testcase_Vddio_001", "内存VDDIO电压设置菜单检查"))
def Testcase_Vddio_001():
    """
    Name:       内存VDDIO电压设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，检查Advanced-> Socket Configuration-> Memory Configuration -> Memory Training -> Memory Voltage目录是否已隐藏，有结果A；
                2、检查菜单其他页面是否有VDDIO可设置选项，有结果A。
    Result:     A：内存VDDIO电压设置菜单已隐藏。
    Remark:
    """
    mem_vol = "Memory Voltage"
    path_list = [Msg.PATH_UNCORE_GENERAL, Msg.PATH_UNCORE_STATUS, Msg.PATH_PSTATE_CTL, Msg.PATH_ADV_PM_CFG,
                 Msg.PATH_PER_CPU_INFO, Msg.PATH_PRO_CFG, Msg.PATH_PRO_COMM, Msg.PATH_IIO_CONFIG,
                 Msg.PATH_MEN_INFO, Msg.PATH_MEM_POWER_ADV, Msg.PATH_CSTATE_CTL, Msg.PATH_PCSC_CTL,
                 Msg.PATH_VIRTUAL_VTD, Msg.PATH_IIO_STACK]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG)
        assert not SetUpLib.locate_option(mem_vol)
        for path_page in path_list:
            assert SetUpLib.back_to_setup_toppage()
            assert SetUpLib.enter_menu(path_page)
            assert not SetUpLib.locate_option(mem_vol)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2629", "[TC2629] Testcase_Vddio_002", "装备工具调节内存电压测试"))
def Testcase_Vddio_002():
    """
    Name:       装备工具调节内存电压测试
    Condition:  1、装备工具已上传OS。
    Steps:      1、启动进OS，装备路径下使用"./uniCfg -r Vdd"命令读取默认电压值，有结果A；
                2、设置内存电压a∈[1.045,1.155]，命令为"./uniCfg -w Vdd:a"，重启系统串口打印查看内存电压是否正确，有结果B；
    Result:     A：默认电压1.145；
                B：电压设置生效，数值为a；
    Remark:     1、Vdd调节范围：1.045~1.155，默认值1.145，调整步经0.005；
                2、串口搜索关键字“DDR Vdd”；
                3、注意进制转换，uniCfg设置值为16进制。
    """
    Vdd_def = {"Vdd": '479'}                                  # 479(16) = 1145(10), 默认电压
    vdd_set = {"Vdd": '450'}                                  # 450(16) = 1104(10), 修改电压
    try:
        assert SetUpLib.boot_to_default_os()
        res = Sut.UNITOOL.read(*vdd_set)
        assert res == Vdd_def, "unitool read fail"
        assert Sut.UNITOOL.write(**vdd_set), "unitool write fail"
        BmcLib.force_reset()
        ser_log = SerialLib.cut_log(Sut.BIOS_COM, "START_DIMMINFO_SYSTEM_TABLE", "STOP_DIMMINFO_SYSTEM_TABLE",
                                    SutConfig.Env.BOOT_DELAY, SutConfig.Env.BOOT_DELAY)
        assert "DDR Vdd" and "1.104V" in ser_log, "Serial port not found DDR_Vdd"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2630", "[TC2630] 装备模式:启动阶段串口日志检查 ", "启动阶段串口日志检查"))
def Testcase_Vddio_003():
    try:
        assert PlatMisc.no_error_at_post()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("2631", "[TC2631] 装备模式:BIOS资源分配 ", "装备模式:BIOS资源分配"))
# def Testcase_Vddio_004():
#     try:
#         assert BmcLib.debug_message(enable=True)
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.debug_message(enable=False)
#         BmcLib.clear_cmos()
