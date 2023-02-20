from SPR4P.Config import *
from SPR4P.BaseLib import *


####################################
# Dfx Test Case
# TC 3000-3010
####################################


@core.test_case(("3000", "[TC3000] Testcase_NetworkName_001", "CDN设置菜单检查"))
def Testcase_NetworkName_001():
    """
    Name:       CDN设置菜单检查
    Condition:  1、默认配置
    Steps:      1、启动进Setup菜单，Misc界面下查看是否提供CDN设置菜单，可选值及默认值，有结果A。
    Result:     A：提供CDN设置菜单，Enabled、Disabled可选，默认为Enabled。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MISC_CONFIG, Key.DOWN, 20, Msg.MISC_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.CDN), [Msg.ENABLE, Msg.DISABLE])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("3001", "[TC3001] Testcase_NetworkName_002", "CDN开启时板载网卡上报Type41"))
def Testcase_NetworkName_002():
    """
    Name:       CDN开启时板载网卡上报Type41
    Condition:  1、CDN已开启；
                2、满配OCP网卡
    Steps:      1、启动进OS，执行"dmidecode -t41"命令查看板载设备信息，有结果A。
    Result:     A：SATA、USB、Video、OCP等板载设备信息显示正确，设备类型、丝印、BDF准确无误；
    Remark:
    """
    try:
        # enabled by default on 4P,
        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.smbios_dump_compare(Sut.OS_SSH, 41)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("3002", "[TC3002] Testcase_NetworkName_003", "CDN关闭时板载网卡不上报Type41"))
@mark_skip_if(BMC_WEB.is_ocp_exist, reason="OCP not exist", value=False)
def Testcase_NetworkName_003():
    """
    Name:       CDN关闭时板载网卡不上报Type41
    Condition:  1、CDN已关闭；
                2、满配OCP网卡
    Steps:      1、启动进OS，执行"dmidecode -t41"命令查看板载设备信息，有结果A。
    Result:     A：SATA、USB、Video等板载设备信息显示正确，设备类型、丝印、BDF准确无误，无OCP网卡显示信息；
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MISC_CONFIG, Key.DOWN, 20, Msg.MISC_CONFIG)
        assert SetUpLib.set_option_value(Msg.CDN, Msg.DISABLE, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        type41_data = SshLib.execute_command(Sut.OS_SSH, "dmidecode -t 41")
        assert not re.search("OCP", type41_data, re.I), f"存在OCP网卡显示信息 - f{type41_data}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("3003", "[TC3003] Testcase_NetworkName_004", "CDN开关不影响Slot网卡上报Type9"))
def Testcase_NetworkName_004():
    """
    Name:       CDN开关不影响Slot网卡上报Type9
    Condition:  1、接Pcie网卡。
    Steps:      1、启动进Setup菜单，Misc界面下关闭CDN开关，F10保存退出；
                2、启动进OS，执行"dmidecode -t9"命令查看Slot设备信息，有结果A。
                3、启动进Setup菜单，Misc界面下开启CDN开关，F10保存退出；
                4、启动进OS，执行"dmidecode -t9"命令查看Slot设备信息，有结果A。
    Result:     A：Slot网卡设备信息显示正确，设备类型、丝印、在为状态、BDF等信息准确无误。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MISC_CONFIG, Key.DOWN, 20, Msg.MISC_CONFIG)
        assert SetUpLib.set_option_value(Msg.CDN, Msg.DISABLE, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert PlatMisc.smbios_dump_compare(Sut.OS_SSH, 9)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MISC_CONFIG, Key.DOWN, 20, Msg.MISC_CONFIG)
        assert SetUpLib.set_option_value(Msg.CDN, Msg.ENABLE, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert PlatMisc.smbios_dump_compare(Sut.OS_SSH, 9)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("3007", "[TC3007] Testcase_Spcr_001", "SPCR设置菜单检查"))
def Testcase_Spcr_001():
    """
    Name:       SPCR设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，ACPI配置界面下检查是否存在SPCR设置菜单，默认值及可选值，有结果A。
    Result:     A：存在OS串口重定向选项（SPCR），可选Enabled、Disabled，默认Enabled。
    Remark:     1、不同产品选项位置不同，以Setup菜单基线为准。
    """
    spcr_table = "ACPI Table or Features Control"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(spcr_table, Key.DOWN, 20, spcr_table)
        assert MiscLib.same_values(SetUpLib.get_all_values("SPCR Table Support", Key.UP), [Msg.ENABLE, Msg.DISABLE])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

