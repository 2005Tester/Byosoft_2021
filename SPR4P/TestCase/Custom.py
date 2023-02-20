import json
from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Custom Test Case
# TC 2000-2020
####################################


def _bios_restore(logo=False, password=False, custom=False):
    BmcLib.clear_cmos()
    if BmcLib.get_fw_version().BIOS != PlatMisc.config_ver().BiosVer:
        return Update.flash_bios_bin_and_init()

    if not MiscLib.ping_sut(Env.OS_IP, 10):
        if not SetUpLib.boot_to_default_os():
            return False
    logo_restore = PlatMisc.unilogo_update(PlatMisc.config_ver().LogoSrc) if logo else True
    pw_restore = PwdLib.restore_admin_password() if password else True
    custom = PlatMisc.uni_command("-c") if custom else True
    return logo_restore and pw_restore and custom


@core.test_case(("2000", "[TC2000] Testcase_UpgradeNoChange_001", "升级配置不丢失"))
def Testcase_UpgradeNoChange_001():
    """
    Name:       升级配置不丢失
    Condition:  1、已知待升级版本b。
    Steps:      1、启动进Setup菜单，随机修改部分选项，F10保存重启再次进Setup菜单检查修改是否生效，有结果A；
                2、使用Redfish收集一份CurrentValue值，假定为x；
                3、BMC Web升级b版本后启动进OS，再次Redfish收集一份CurrentValue值，假定为y；
                4、对比xy两份CurrentValue值，检查是否存在差异，有结果B。
    Result:     A：选项修改生效；
                B：xy保持一致（不一致需确定合理性）。
    Remark:
    """
    try:
        hpm_file = PlatMisc.get_latest_hpm_bios()

        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert SetUpLib.boot_to_default_os()
        log_path = PlatMisc.current_test_dir()
        current_value_a = Sut.BMC_RFISH.current_dump(dump_json=True, path=log_path, name=f"CurrentValue_a.json")

        assert Update.update_bios_hpm(hpm_file)
        assert SetUpLib.boot_to_default_os(reset=False)
        current_value_b = Sut.BMC_RFISH.current_dump(dump_json=True, path=log_path, name=f"CurrentValue_b.json")
        assert current_value_a == current_value_b, "CurrentValue_a != CurrentValue_b"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _bios_restore()


@core.test_case(("2001", "[TC2001] Testcase_UpgradeNoChange_002", "默认Logo升级不丢失"))
def Testcase_UpgradeNoChange_002():
    """
    Name:       默认Logo升级不丢失
    Condition:  1、已知待升级版本b。
    Steps:      1、上电启动，检查当前版本Logo，假定为x；
                2、BMC Web升级b版本后启动进OS，检查版本Logo，假定为y；
                3、对比xy是否一致，有结果A。
    Result:     A：xy保持一致。
    Remark:
    """
    try:
        hpm_file = PlatMisc.get_latest_hpm_bios()
        default_logo = PlatMisc.save_logo(path=PlatMisc.current_test_dir())
        assert Update.update_bios_hpm(hpm_file)
        custom_logo = PlatMisc.save_logo(path=PlatMisc.current_test_dir())
        assert MiscLib.compare_images(default_logo, custom_logo)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _bios_restore()


@core.test_case(("2002", "[TC2002] Testcase_UpgradeNoChange_003", "定制Logo升级不丢失"))
def Testcase_UpgradeNoChange_003():
    """
    Name:       定制Logo升级不丢失
    Condition:  1、已知待升级版本b；
                2、装备工具已定制Logo。
    Steps:      1、上电启动，检查当前版本Logo是否为定制Logo，有结果A；
                2、BMC Web升级b版本后启动，检查版本Logo是否为定制Logo，有结果A。
    Result:     A：为装备定制Logo。
    Remark:
    """
    try:
        hpm_file = PlatMisc.get_latest_hpm_bios()

        assert SetUpLib.boot_to_default_os(delay=10)
        custom_logo = PlatMisc.root_path() / "Resource/Logo/CustomLogo.bmp"
        assert PlatMisc.unilogo_update(custom_logo)

        assert Update.update_bios_hpm(hpm_file)
        custom_post_logo = PlatMisc.save_logo(path=PlatMisc.current_test_dir())
        assert MiscLib.images_similar(custom_post_logo, str(custom_logo))
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _bios_restore(logo=True)


@core.test_case(("2003", "[TC2003] Testcase_UpgradeNoChange_004", "密码升级不丢失"))
def Testcase_UpgradeNoChange_004():
    """
    Name:       密码升级不丢失
    Condition:  1、已知待升级版本b。
    Steps:      1、启动进Setup菜单，修改密码为x，F10保存重启使用x密码登录Setup菜单，检查是否成功，有结果A；
                2、BMC Web升级b版本后启动，用x密码登录Setup菜单，检查是否成功，有结果A；
    Result:     A：密码x登录成功。
    Remark:
    """
    try:
        pw_x = PwdLib.gen_pw(prefix="Admin@", digit=2, upper=PW.MAX - 8)
        hpm_file = PlatMisc.get_latest_hpm_bios()
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert PwdLib.set_admin_pw_and_verify(pw_x, PW.ADMIN)
        assert Update.update_bios_hpm(hpm_file)
        assert PwdLib.continue_to_setup_with_pw(pw_x)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _bios_restore(password=True)


@core.test_case(("2004", "[TC2004] Testcase_UpgradeNoChange_005", "定制菜单升级不丢失"))
def Testcase_UpgradeNoChange_005():
    """
    Name:       定制菜单升级不丢失
    Condition:  1、已知待升级版本b；
                2、装备工具已定制Setup菜单。
    Steps:      1、BMC Web升级b版本，启动进Setup菜单，按"Load Custom Default"，检查定制化菜单是否正常加载，有结果A。
    Result:     A：定制化菜单正常加载，选项值与定制一致。
    Remark:
    """
    try:
        set_options = BiosCfg.HPM_KEEP
        hpm_file = PlatMisc.get_latest_hpm_bios()
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**set_options)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        assert Update.update_bios_hpm(hpm_file)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        assert SetUpLib.back_to_front_page()
        SetUpLib.send_key(Key.ENTER)
        assert MiscLib.ping_sut(Env.OS_IP, 300)
        assert Sut.UNITOOL.check(**set_options)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _bios_restore(custom=True)


@core.test_case(("2007", "[TC2007] Testcase_Redfish_001", "升级后未启动时带外设置变量值"))
def Testcase_Redfish_001():
    """
    Name:       升级后未启动时带外设置变量值
    Condition:  1、Postman工具已安装。
    Steps:      1、下电升级BIOS，升级完成后仍保持下电状态；
                2、通过Redfish修改部分Setup变量并下发；
                3、启动进Setup菜单，检查变量修改是否生效，有结果A。
    Result:     A：Redfish修改生效。
    Remark:     1、Redfish设置接口：
                https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
                192.168.X.XXX为BMC IP地址；
                2、支持Redfish修改变量参考Setup菜单基线；
                3、通过PATCH操作进行带外设置。
    """
    try:
        hpm_file = PlatMisc.get_latest_hpm_bios()
        assert Update.update_bios_hpm(hpm_file, power_on=False)
        set_options = Sut.BMC_RFISH.set_bios_option(**RedfishCfg.HPM_KEEP)
        assert set_options.result, f"Set BIOS failed: [{set_options.status}]{set_options.body}"
        logging.info(f"Set BIOS configuration success:\n{json.dumps(RedfishCfg.HPM_KEEP, indent=4)}")
        assert SetUpLib.boot_to_setup()
        assert Sut.BMC_RFISH.check_bios_option(**RedfishCfg.HPM_KEEP), \
            f"Check BIOS failed: {json.dumps(Sut.BMC_RFISH.read_bios_option(*RedfishCfg.HPM_KEEP), indent=4)}"
        logging.info(f"Check BIOS configuration success")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _bios_restore()


@core.test_case(("2008", "[TC2008] Testcase_Redfish_002", "带外设置基本选项"))
def Testcase_Redfish_002():
    """
    Name:       带外设置基本选项
    Condition:  1、Postman工具已安装；
                2、随机选择部分基本变量，假定为a。
    Steps:      1、通过Redfish修改变量a并下发，检查下发情况，有结果A；
                2、启动进Setup菜单，检查变量a设置是否生效，有结果B。
    Result:     A：下发成功；
                B：变量a设置生效。
    Remark:     1、Redfish设置接口：
                https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
                192.168.X.XXX为BMC IP地址；
                2、支持Redfish修改变量参考Setup菜单基线；
                3、通过PATCH操作进行带外设置。
    """
    try:
        assert Sut.BMC_RFISH.set_bios_option(**{Attr.CPU_CORES: f'{int(SutConfig.Sys.CPU_CORES/2)}'}).result, 'Error: PATCH Fail'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, f'{int(SutConfig.Sys.CPU_CORES/2)}']])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2009", "[TC2009] Testcase_Redfish_003", "Redfish和Setup同时修改变量值"))
def Testcase_Redfish_003():
    """
    Name:       Redfish和Setup同时修改变量值
    Condition:  1、Postman工具已安装。
    Steps:      1、启动进Setup菜单，通过Redfish修改部分Setup变量并下发，同时在Setup菜单修改相同选项为不同值，F10保存重启进Setup菜单，检查变量状态，有结果A；
                2、再次通过Redfish修改部分Setup变量并下发，同时在Setup菜单修改其他选项值，F10保存重启进Setup菜单，检查变量状态，有结果A；
    Result:     A：变量显示为Redfish下发值；
                B：Redfish下发变量显示为下发值，Setup修改的变量显示为Setup修改值。
    Remark:     1、Redfish设置接口：
                https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
                192.168.X.XXX为BMC IP地址；
                2、支持Redfish修改变量参考Setup菜单基线；
                3、通过PATCH操作进行带外设置。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert Sut.BMC_RFISH.set_bios_option(**{Attr.CPU_CORES: f'{int(SutConfig.Sys.CPU_CORES / 4)}'}).result, 'Error: PATCH Fail'
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f'{int(SutConfig.Sys.CPU_CORES / 2)}', save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, f'{int(SutConfig.Sys.CPU_CORES / 4)}']])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2010", "[TC2010] Testcase_Redfish_004", "带外设置联动关系选项_从项可设置"))
def Testcase_Redfish_004():
    """
    Name:       带外设置联动关系选项_从项可设置
    Condition:  1、Postman工具已安装；
                2、随机选择有联动关系，且从项可设置的变量，假定为a。
    Steps:      1、通过Redfish修改变量a及其主项并下发；
                2、启动进Setup菜单，检查变量a及主项修改是否生效，有结果A；
    Result:     A：主从项均设置生效。
    Remark:     1、Redfish设置接口：
                https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
                192.168.X.XXX为BMC IP地址；
                2、支持Redfish修改变量参考Setup菜单基线；
                3、通过PATCH操作进行带外设置。
    """
    try:
        choice_op = RedfishCfg.DEP_MAIN_SUB
        logging.info(f"Choice option for test: {choice_op}")
        set_op = Sut.BMC_RFISH.set_bios_option(**choice_op)
        assert set_op.result, f"Choice option set failed: [{set_op.status}] {set_op.body}"
        logging.info("Set BIOS config success")
        assert SetUpLib.boot_to_setup()
        assert Sut.BMC_RFISH.check_bios_option(**choice_op), f"Check option failed:\n{Sut.BMC_RFISH.read_bios_option(*choice_op)}"
        logging.info("Check BIOS config success")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("2011", "[TC2011] Testcase_Redfish_005", "带外设置联动关系从项_从项不可设置"))
# def Testcase_Redfish_005():
#     """
#     Name:       带外设置联动关系从项_从项不可设置
#     Condition:  1、Postman工具已安装；
#                 2、随机选择有联动关系，且从项不可设置的变量（置灰或隐藏），假定为a。
#     Steps:      1、通过Redfish修改变量a及其主项并下发；
#                 2、启动进Setup菜单，检查变量a及主项修改是否生效，有结果A；
#     Result:     A：Redfish下发失败，主从项均不生效。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2012", "[TC2012] Testcase_Redfish_006", "带外设置联动关系从项_从项互斥"))
# def Testcase_Redfish_006():
#     """
#     Name:       带外设置联动关系从项_从项互斥
#     Condition:  1、Postman工具已安装；
#                 2、随机选择有联动关系，且从项可设置的变量，假定主项a联动从项值为b。
#     Steps:      1、通过Redfish修改主项a，且设置从项值为c，并下发；
#                 2、启动进Setup菜单，检查主从项修改是否生效，有结果A；
#     Result:     A：Redfish下发成功，从项值为b非c。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2013", "[TC2013] Testcase_Redfish_007", "带外设置联动关系主项"))
# def Testcase_Redfish_007():
#     """
#     Name:       带外设置联动关系主项
#     Condition:  1、Postman工具已安装；
#                 2、随机选择有联动关系变量，假定主项a联动从项值为b。
#     Steps:      1、通过Redfish修改主项a并下发；
#                 2、启动进入Setup菜单，检查主从项变量值，有结果A；
#     Result:     A：主项设置成功，从项跟随主项的设置值进行变化。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2014", "[TC2014] Testcase_Redfish_008", "带外设置后Setup菜单再修改"))
# def Testcase_Redfish_008():
#     """
#     Name:       带外设置后Setup菜单再修改
#     Condition:  1、Postman工具已安装；
#                 2、随机选择部分变量，假定为a；
#     Steps:      1、通过Redfish修改选项a并下发；
#                 2、启动进Setup菜单，检查选项a设置是否生效，有结果A；
#                 3、Setup菜单再修改变量a为其它值，F10保存退出再次进 Setup菜单，检查选项a设置是否生效，有结果B。
#     Result:     A：变量a设置生效；
#                 B：变量a设置生效，为Setup修改后的值。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2015", "[TC2015] Testcase_Redfish_009", "带外设置变量全遍历"))
# def Testcase_Redfish_009():
#     """
#     Name:       带外设置变量全遍历
#     Condition:  1、Postman工具已安装；
#                 2、随机选择部分基本变量，假定为a。
#     Steps:      1、通过Redfish修改变量a并下发，检查下发情况，有结果A；
#                 2、启动进Setup菜单，检查变量a设置是否生效，有结果B；
#                 3、遍历Setup菜单基线所有变量，重复步骤1~2。
#     Result:     A：下发成功；
#                 B：变量a设置生效。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址；
#                 2、支持Redfish修改变量参考Setup菜单基线；
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2016", "[TC2016] Testcase_Redfish_010", "带外恢复Setup菜单默认值"))
# def Testcase_Redfish_010():
#     """
#     Name:       带外恢复Setup菜单默认值
#     Condition:  1、Postman工具已安装；
#     Steps:      1、启动进Setup菜单，F9恢复默认，F10保存重启再次进入Setup菜单，Redfish收集一份CurrentValue，假定为a；
#                 2、修改Setup菜单部分选项未为非默认值，F10保存重启后再次进入Setup菜单，检查修改是否生效，有结果A；
#                 3、Redfish下发恢复默认指令，重启进入Setup菜单，Redfish收集一份CurrentValue，假定为b；
#                 4、对比ab两份数据是否一致，有结果B。
#     Result:     A：变量修改生效；
#                 B：ab结果一致。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址；
#                 2、支持Redfish修改变量参考Setup菜单基线；
#                 3、通过POST操作恢复默认设置，通过GET操作获取带外配置值。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2017", "[TC2017] Testcase_Redfish_011", "带外设置变量无效值_枚举型"))
# def Testcase_Redfish_011():
#     """
#     Name:       带外设置变量无效值_枚举型
#     Condition:  1、Postman工具已安装；
#                 2、随机选择部分枚举型变量，假定为a；
#     Steps:      1、通过Redfish修改变量a设置值为无效值，检查下发情况，结果A；
#                 2、启动进Setup菜单，检查设置是否生效，有结果B；
#     Result:     A：下发失败，提示设置值无效；
#                 B：选项a设置未生效。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2018", "[TC2018] Testcase_Redfish_012", "带外设置变量无效值_输入型"))
# def Testcase_Redfish_012():
#     """
#     Name:       带外设置变量无效值_输入型
#     Condition:  1、Postman工具已安装；
#                 2、随机选择部分输入型变量，假定为a；
#     Steps:      1、通过Redfish修改变量a设置值为无效值，检查下发情况，结果A；
#                 2、启动进Setup菜单，检查设置是否生效，有结果B；
#     Result:     A：下发失败，提示设置值无效；
#                 B：选项a设置未生效。
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过PATCH操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2019", "[TC2019] Testcase_Redfish_013", "Currentvalue文件正确性检查"))
# def Testcase_Redfish_013():
#     """
#     Name:       Currentvalue文件正确性检查
#     Condition:  1、Postman工具已安装。
#     Steps:      1、通过Redfish获取一份currentvalue.json文件；
#                 2、检查currentvalue.json文件变量值与Setup显示是否一致，有结果A；
#                 3、检查currentvalue.json文件变量是否与Setup菜单基线一致，有结果B。
#     Result:     A：当前值与Setup菜单保持一致；
#                 B：变量与Setup基线保持一致；
#     Remark:     1、Redfish设置接口：
#                 https://192.168.X.XXX/redfish/v1/Systems/1/Bios/Settings
#                 192.168.X.XXX为BMC IP地址
#                 2、支持Redfish修改变量参考Setup菜单基线
#                 3、通过GET操作进行带外设置。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2020", "[TC2020] Testcase_MemorySequence_001", "内存时序设置菜单检查"))
def Testcase_MemorySequence_001():
    """
    Name:       内存时序设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，查看是否存在内存时序菜单，可选值及默认值，有结果A；
                2、使能内存时序总开关，检查内存参数是否可设置，有结果B；
                3、关闭内存时序总开关，检查内存参数是否可设置，有结果C；
    Result:     A：提供时序调整总开关，Enabled、Disabled可选，默认为Disabled；
                B：开启后提供时序参数调整选项，包括tREFI，tCAS，tRP，tRCD，tRAS，tWR，tRFC，tRRD，tRTP，tWTR，tFAW，tRC，tCWL等；
                C：关闭后隐藏所有序参数调整选项。
    Remark:     1、提供菜单，调整内存时序参数；（仅功能性能比拼使用，默认关闭隐藏）
                2、使能后功能不需要测试；
                3、具体参数的变量名称需要由开发提供。
    """
    valid_param = {'tCAS': 0, 'tRP': 0, 'tRCD': 0, 'tRAS': 0, 'tRC': 0}
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert Sut.UNITOOL.check(**valid_param)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    # finally:
    #     BmcLib.clear_cmos()

