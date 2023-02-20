import glob
import logging
import random
from copy import deepcopy

from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# BiosSetup Test Case
# TC 1600-1693
####################################


usb_list = [f'USB MassStorage\s+{SutConfig.Sys.USB_STORAGE}']
bmc_supper_value = [Msg.DISABLE, Msg.ENABLE]
bmc_wd_type = [Msg.BMC_WDT_POST, Msg.BMC_WDT_OS]
bmc_wd_action = [Msg.BMC_WDT_ACTION_POST, Msg.BMC_WDT_ACTION_OS]
bmc_wd_timeout = [Msg.BMC_WDT_TIMEOUT_POST, Msg.BMC_WDT_TIMEOUT_OS]
bmc_act_after = Msg.VAL_BMC_WDT_ACT[-1]


def _get_attr_dict(options=Msg.CUSTOM_OPTIONS) -> dict:
    attr = {}
    for att in options:
        attr.update(att[-1])
    return attr


def _clear_custom_default(uefi=True):
    os_ip = Env.OS_IP if uefi else Env.OS_IP_LEGACY
    if not MiscLib.ping_sut(os_ip, 5):
        if not SetUpLib.boot_to_default_os(uefi=uefi):
            return
    return PlatMisc.uni_command("-c", uefi=uefi)


@core.test_case(("1600", "[TC1600] Testcase_LoadDefault_001", "BMC恢复菜单默认值测试"))
def Testcase_LoadDefault_001():
    """
    Name:       BMC恢复菜单默认值测试
    Condition:
    Steps:      1、启动进Setup菜单，修改部分非BMC相关配置项（尽可能每个界面均有修改选项，特别是BootType、串口重定向界面下的选项，看门狗等），F10保存重启再次进Setup菜单检查是否生效，有结果A；
                2、BMC恢复默认后重启再次进Setup菜单，检查修改选项是否恢复默认值，有结果B。
    Result:     A：选项修改生效；
                B：选项已恢复默认值。
    Remark:     1、具体拉低GPIO命令参考BMC命令定义
                2、恢复默认不影响从BMC获取的相关配置（如IPV4/IPV6，双因素认证，SSH配置，调速策略等）、密码、TPM显示（版本信息），保持当前配置不变。
    """
    try:
        # Set
        assert SetUpLib.boot_to_bios_config()
        for op in Msg.PICK_OPTIONS:
            page, path, option, set_value, default = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(option, set_value, save=False)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # Check
        assert SetUpLib.continue_to_bios_config()
        for op in Msg.PICK_OPTIONS:
            page, path, option, set_value, default = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(option) == set_value
        # BMC Load Default
        BmcLib.clear_cmos()
        # Verify
        assert SetUpLib.boot_to_bios_config()
        for op in Msg.PICK_OPTIONS:
            page, path, option, set_value, default = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(option) == default
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1601", "[TC1601] Testcase_LoadDefault_002", "BMC恢复默认值后修改配置测试"))
def Testcase_LoadDefault_002():
    """
    Name:       BMC恢复默认值后修改配置测试
    Condition:  1、BMC恢复默认值。
    Steps:      1、启动进Setup菜单，随机修改部分配置项，F10保存重启再次进Setup菜单，查看配置项修改是否生效，有结果A。
    Result:     A：配置项修改成功。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, str(int(SutConfig.Sys.CPU_CORES / 2)), save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, str(int(SutConfig.Sys.CPU_CORES / 2))]], Key.DOWN, 5)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1602", "[TC1602] Testcase_LoadDefault_003", "F9恢复菜单默认值测试"))
def Testcase_LoadDefault_003():
    """
    Name:       F9恢复菜单默认值测试
    Condition:
    Steps:      1、启动进Setup菜单，修改部分非BMC相关配置项（尽可能每个界面均有修改选项，特别是BootType、串口重定向界面下的选项，看门狗等）；
                ，F10保存重启再次进Setup菜单检查是否生效，有结果A；
                2、F9恢复默认后F10保存重启再次进Setup菜单，检查修改选项是否恢复默认值，有结果B。
    Result:     A：选项修改生效；
                B：选项已恢复默认值。
    Remark:     1、恢复默认不影响从BMC获取的相关配置（如IPV4/IPV6，双因素认证，SSH配置，调速策略等）、密码、TPM显示（版本信息），保持当前配置不变。
    """
    flow_con = [Msg.FLOW_CTL, '<None>']
    flow_rts = [Msg.FLOW_CTL, '<RTS/CTS>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], Key.DOWN, 20, flow_con[0])
        assert SetUpLib.set_option_value(flow_con[0], 'RTS/CTS', Key.DOWN, save=False)  # 修改串口界面中的参数
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option([Msg.PAGE_BOOT], Key.RIGHT, 10)
        assert SetUpLib.set_option_value(Msg.USB_BOOT, Msg.DISABLE, Key.DOWN, save=True)  # 修改Boot界面参数保存并重启
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)                         # 进Setup菜单检查修改是否生效
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], Key.DOWN, 20, flow_con[0])
        assert SetUpLib.verify_options([flow_rts], Key.DOWN, 16)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option([Msg.PAGE_BOOT], Key.RIGHT, 10)
        assert SetUpLib.verify_options([[Msg.USB_BOOT, Msg.DISABLE]], Key.DOWN, 16)
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, Key.RESET_DEFAULT)             # F9 恢复默认并验证
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], Key.DOWN, 20, flow_con[0])
        assert SetUpLib.verify_options([flow_con], Key.DOWN, 16)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.locate_option([Msg.PAGE_BOOT], Key.RIGHT, 10)
        assert SetUpLib.verify_options([[Msg.USB_BOOT, Msg.ENABLE]], Key.DOWN, 16)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1603", "[TC1603] Testcase_LoadDefault_004", "F9恢复默认值后修改配置测试"))
def Testcase_LoadDefault_004():
    """
    Name:       F9恢复默认值后修改配置测试
    Condition:
    Steps:      1、启动进Setup菜单，F9恢复默认后检查各页面与F9之前是否一致，是否有新开放菜单、选项值变更等现象，有结果A；
                2、随机修改部分配置项，F10保存重启再次进Setup菜单，查看配置项修改是否生效，有结果B。
    Result:     A：F9前后一致，无新开放菜单、选项值变更等现象；
                B：配置项修改成功。
    Remark:
    """
    page_flag = [Msg.PAGE_ADVANCED, Msg.PAGE_SECURITY, Msg.PAGE_BOOT, Msg.PAGE_SAVE]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        for flag in page_flag:
            assert SetUpLib.switch_to_page(flag)
            _temp_log_bef = SetUpLib.get_all_options().keys()
            logging.debug(f"{flag}_bef = {_temp_log_bef}")
            assert SetUpLib.load_default_in_setup()
            _temp_log_aft = SetUpLib.get_all_options().keys()
            logging.debug(f"{flag}_aft = {_temp_log_aft}")
            assert _temp_log_aft == _temp_log_bef, "setup menu changed after load default"# F9恢复默认后检查各页面与F9之前一致
        assert SetUpLib.switch_to_page(Msg.PAGE_ADVANCED)           # 修改部分配置项
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, confirm_msg=Msg.ACT_CPU_CORES)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, str(int(SutConfig.Sys.CPU_CORES / 2)), save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)                         # 验证修改配置项
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, confirm_msg=Msg.ACT_CPU_CORES)
        assert SetUpLib.verify_options(options=[[Msg.ACT_CPU_CORES, str(int(SutConfig.Sys.CPU_CORES / 2))]])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1604", "[TC1604] Testcase_LoadDefault_005", "恢复默认不影响管理员密码"))
def Testcase_LoadDefault_005():
    """
    Name:       恢复默认不影响管理员密码
    Condition:  1、已设置管理员密码。
    Steps:      1、管理员登录Setup菜单，F9恢复默认后F10保存重启检查登录Setup菜单时是否需要验证密码，管理员密码能否登录Setup菜单，有结果A；
                2、BMC恢复默认后重启检查登录Setup菜单时是否需要验证密码，管理员密码能否登录Setup菜单，有结果A；
    Result:     A：管理员密码登录Setup菜单成功；
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, Key.RESET_DEFAULT)  # F9恢复默认后F10保存重启
        assert SetUpLib.continue_to_page(Msg.PAGE_INFO)
        assert BmcLib.clear_cmos()   # BMC恢复默认
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1605", "[TC1605] Testcase_LoadDefault_006", "恢复默认不影响普通用户密码"))
def Testcase_LoadDefault_006():
    """
    Name:       恢复默认不影响普通用户密码
    Condition:  1、已设置普通用户密码。
    Steps:      1、管理员登录Setup菜单，F9恢复默认后F10保存重启检查登录Setup菜单时是否需要验证密码，普通用户密码能否登录Setup菜单，有结果A；
                2、BMC恢复默认后重启检查登录Setup菜单时是否需要验证密码，普通用户密码能否登录Setup菜单，有结果A；
    Result:     A：普通用户密码登录Setup菜单成功；
    Remark:
    """
    pw_init = PwdLib.gen_pw(prefix="Admin@", upper=1, lower=1, symbol=1, digit=1)
    pw_a = PwdLib.gen_pw(total=10, upper=1, lower=1, symbol=1, digit=1)
    try:
        # condition
        assert PwdLib.init_user_password(pw_a, pw_init)
        logging.debug(f"pw_a = {pw_a}")
        # set 1
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, Key.RESET_DEFAULT)     # F9恢复默认后F10保存重启
        # result A
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)         # 管理员正常登录
        assert BmcLib.force_reset()
        assert SetUpLib.continue_to_pw_prompt()          # 普通用户 正常登录
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE), f'{Msg.HOME_PAGE} not found'
        # set 2
        BmcLib.clear_cmos()     # BMC恢复默认后重启
        # result A
        assert BmcLib.force_reset()
        assert SetUpLib.continue_to_pw_prompt()          # 普通用户 正常登录
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE), f'{Msg.HOME_PAGE} not found'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.delele_user_pw()


@core.test_case(("1606", "[TC1606] Testcase_LoadDefault_007", "恢复默认不影响BMC相关配置"))
def Testcase_LoadDefault_007():
    """
    Name:       恢复默认不影响BMC相关配置
    Condition:
    Steps:      1、启动进Setup菜单，修改IPV4/IPV6、风扇调速、上电策略、SSH服务、双因素等相关配置，F10保存重启再次进Setup菜单检查是否生效，有结果A；
                2、F9恢复默认后F10保存重启再次进Setup菜单，检查修改选项是否恢复默认值，有结果B。
                3、BMC恢复默认后重启再次进Setup菜单，检查修改选项是否恢复默认值，有结果B。
    Result:     A：选项修改生效；
                B：修改选项未恢复默认值。
    Remark:
    """
    set_power_policy = "Last State"
    set_bmc_fan = "Custom Mode"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.set_option_value(Msg.POWER_POLICY, set_power_policy)
        assert SetUpLib.set_option_value(Msg.BMC_FAN_MODE, set_bmc_fan, save=True)   # 修改风扇模式,F10保存重启

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.verify_options(options=[[Msg.POWER_POLICY, set_power_policy]])        # 选项修改生效
        assert SetUpLib.verify_options(options=[[Msg.BMC_FAN_MODE, set_bmc_fan]])
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, Key.RESET_DEFAULT)             # F9恢复默认后F10保存重启

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.verify_options(options=[[Msg.POWER_POLICY, set_power_policy]])        # 修改选项未恢复默认值
        assert SetUpLib.verify_options(options=[[Msg.BMC_FAN_MODE, set_bmc_fan]])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        SetUpLib.set_option_value(Msg.BMC_FAN_MODE, "Energy Saving Mode")
        SetUpLib.set_option_value(Msg.POWER_POLICY, "Power On", save=True)
        SetUpLib.wait_msg(Msg.LOGO_SHOW)


@core.test_case(("1607", "[TC1607] Testcase_LoadDefault_008", "恢复默认不影响RTC时间"))
def Testcase_LoadDefault_008():
    """
    Name:       恢复默认不影响RTC时间
    Condition:
    Steps:      1、启动进Setup菜单，修改TRC时间，F10保存重启再次进Setup菜单检查是否生效，有结果A；
                2、F9恢复默认后F10保存重启再次进Setup菜单，检查RTC时间是否恢复默认值，有结果B。
                3、BMC恢复默认后重启再次进Setup菜单，检查RTC时间是否恢复默认值，有结果B。
    Result:     A：RTC时间修改生效；
                B：修改选项未恢复默认值。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        time_a = BmcLib.get_bmc_datetime()
        set_time = MiscLib.date_time_delta(time_a, minutes=30)
        assert PlatMisc.set_rtc_time_linux(set_time)

        assert SetUpLib.boot_to_bios_config()
        time_b = BmcLib.get_bmc_datetime()
        assert MiscLib.time_str_offset(time_a, time_b) > 30 * 60

        assert BmcLib.clear_cmos()
        assert SetUpLib.boot_to_bios_config()
        time_b = BmcLib.get_bmc_datetime()
        assert MiscLib.time_str_offset(time_a, time_b) > 30 * 60
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PlatMisc.set_rtc_time_linux(time_str=None)


@core.test_case(("1608", "[TC1608] Testcase_LoadDefault_009", "恢复默认不影响安全启动"))
def Testcase_LoadDefault_009():
    """
    Name:       恢复默认不影响安全启动
    Condition:  1、UEFI模式。
    Steps:      1、启动进Secureboot界面，开启安全启动选项，F10保存重启再次进Secureboot界面检查是否生效，有结果A；
                2、F9恢复默认后F10保存重启再次进Secureboot界面，检查安全启动是否恢复默认值，有结果B。
                3、BMC恢复默认后重启再次进Secureboot界面，检查安全启动是否恢复默认值，有结果B。
    Result:     A：选项修改生效；
                B：修改选项未恢复默认值。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Msg.SECURE_RESTORE)
        SetUpLib.send_keys([Key.ENTER, Key.Y], delay=3)
        assert SetUpLib.get_option_value(Msg.SECURE_STATE, integer=None) == Msg.ENABLE

        SetUpLib.send_key(Key.ESC, delay=1)
        assert SetUpLib.move_to_bios_config()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_setup()
        assert SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.get_option_value(Msg.SECURE_STATE, integer=None) == Msg.ENABLE

        SetUpLib.send_key(Key.ESC, delay=1)
        assert SetUpLib.move_to_bios_config()
        assert SetUpLib.load_default_in_setup(save=True)
        assert SetUpLib.continue_to_setup()
        assert SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.get_option_value(Msg.SECURE_STATE, integer=None) == Msg.ENABLE

        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.get_option_value(Msg.SECURE_STATE, integer=None) == Msg.ENABLE
        assert SetUpLib.locate_option(Msg.SECURE_ERASE)
        SetUpLib.send_keys([Key.ENTER, Key.Y], delay=3)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        for i in range(3):  # 恢复安全启动设置到默认状态
            if not SetUpLib.boot_to_setup():
                continue
            SetUpLib.locate_front_page_icon(Msg.SECURE_BOOT)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.get_option_value(Msg.SECURE_STATE, integer=None) == Msg.DISABLE:
                break
            SetUpLib.locate_option(Msg.SECURE_ERASE)
            SetUpLib.send_keys([Key.ENTER, Key.Y], delay=3)
            SetUpLib.send_keys(Key.SAVE_RESET)


@core.test_case(("1609", "[TC1609] Testcase_LoadDefault_011", "恢复默认不影响TPM信息显示"))
@mark_skip_if(not Sys.TPM, reason="TPM not installed")
def Testcase_LoadDefault_011():
    """
    Name:       恢复默认不影响TPM信息显示
    Condition:  1、单板接TPM卡。
    Steps:      1、启动进Setup菜单，检查TPM在位状态、版本信息是否正确，有结果A；
                2、F9恢复默认后F10保存重启再次进Setup菜单，检查TPM信息是否恢复默认值，有结果B。
                3、BMC恢复默认后重启再次进Setup菜单，检查TPM信息是否恢复默认值，有结果B。
    Result:     A：TPM在位，版本信息正确；
                B：TPM信息未恢复默认值。
    Remark:
    """
    tpm = SutConfig.Sys.TPM
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.TPM_DEV, integer=None) == f"{tpm['Protocol']} {tpm['Version']}", "default protocol"
        assert SetUpLib.get_option_value(Msg.TPM_ACTIVE, integer=None) == f"SHA256, SM3_256", "default active"

        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.TPM_DEV, integer=None) == f"{tpm['Protocol']} {tpm['Version']}", "setup default protocol"
        assert SetUpLib.get_option_value(Msg.TPM_ACTIVE, integer=None) == f"SHA256, SM3_256", "setup default  active"

        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.TPM_DEV, integer=None) == f"{tpm['Protocol']} {tpm['Version']}", "bmc default protocol"
        assert SetUpLib.get_option_value(Msg.TPM_ACTIVE, integer=None) == f"SHA256, SM3_256", "bmc default active"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


@core.test_case(("1610", "[TC1610] Testcase_LoadDefault_013", "Load Defaults选项功能测试"))
def Testcase_LoadDefault_013():
    """
    Name:       Load Defaults选项功能测试
    Condition:
    Steps:      1、启动进Setup菜单，随机修改部分配置项，使之与系统默认配置值不一样；
                2、选择Load Defaults选项，查看修改的配置项是否恢复默认值，有结果A。
    Result:     A：修改的配置项都恢复默认值。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, confirm_msg=Msg.ACT_CPU_CORES)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, str(int(SutConfig.Sys.CPU_CORES / 2)), save=False)
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, [Key.RESET_DEFAULT])

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)                         # 验证修改配置项,恢复默认值
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, confirm_msg=Msg.ACT_CPU_CORES)
        assert SetUpLib.verify_options(options=[[Msg.ACT_CPU_CORES, "All"]])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1611", "[TC1611] Testcase_LoadDefault_014", "F9操作响应时间测试"))
def Testcase_LoadDefault_014():
    """
    Name:       F9操作响应时间测试
    Condition:
    Steps:      1、启动进Setup菜单，修改部分选项，F9恢复默认，检查F9弹框时间及选项恢复时间是否合理，有结果A。
    Result:     A：反应时间3s以内，符合要求。
    Remark:     1、反应时间过长需要优化。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG)
        default = SetUpLib.get_option_value(Msg.POWER_EFFICIENCY)
        values = SetUpLib.get_all_values(Msg.POWER_EFFICIENCY)
        choose_val = random.choice(values)
        assert SetUpLib.set_option_value(Msg.POWER_EFFICIENCY, choose_val)
        assert SetUpLib.load_default_in_setup()
        assert SetUpLib.wait_msg(f"{Msg.POWER_EFFICIENCY}\s+<{default}>", timeout=3), "F9 response over 3s"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1612", "[TC1612] Testcase_LoadDefault_015", "全擦升级后F9操作测试"))
def Testcase_LoadDefault_015():
    """
    Name:       全擦升级后F9操作测试
    Condition:  1、全擦BIOS版本。
    Steps:      1、首次启动进Setup菜单，F9恢复默认后，F10保存重启，检查F9、F10响应时间是否合理，有结果A；
                2、进入Setup菜单查看选项是否为默认值，有结果B。
    Result:     A：F9、F10响应时间合理；
                B：选项均为默认值。
    Remark:
    """
    try:
        img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image(Env.BRANCH_LATEST)
        assert Update.update_bios_bin(img)
        PwdLib.update_current_pw(pw_admin=Msg.BIOS_PW_DEFAULT)

        BmcLib.force_reset()
        assert PwdLib.continue_to_setup_with_pw(current_pw=Msg.BIOS_PW_DEFAULT, default=True)
        assert SetUpLib.switch_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL)
        options_a = SetUpLib.get_all_options()
        assert SetUpLib.load_default_in_setup(save=True)

        assert PwdLib.continue_to_setup_with_pw(current_pw=Msg.BIOS_PW_DEFAULT, default=True)
        assert SetUpLib.switch_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL)
        options_b = SetUpLib.get_all_options()
        assert options_a == options_b, "Options changed after load default in setup"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()
        SetUpLib.move_option_in_bootmanager(Msg.BOOT_OPTION_OS, 6)


@core.test_case(("1613", "[TC1613] Testcase_LoadDefault_016", "F9前后CPU资源分配对比测试"))
def Testcase_LoadDefault_016():
    """
    Name:       F9前后CPU资源分配对比测试
    Condition:
    Steps:      1、启动进Setup菜单，串口收集一份资源分配表a；
                2、菜单下F9恢复默认后F10保存重启，串口再收集一份资源分配表b；
                3、对比ab两份资源分配表，有结果A。
    Result:     A：ab对比一致（有差异需确认合理性）。
    Remark:
    """
    try:
        assert BmcLib.force_reset()
        resource_bef = SerialLib.cut_log(Sut.BIOS_COM, Msg.CPU_RSC_ALLOC, Msg.START_DIMM, SutConfig.Env.BOOT_DELAY,
                                         SutConfig.Env.BOOT_DELAY)
        assert resource_bef
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, [Key.RESET_DEFAULT])       # F9恢复默认后F10保存重启
        resource_aft = SerialLib.cut_log(Sut.BIOS_COM, Msg.CPU_RSC_ALLOC, Msg.START_DIMM, SutConfig.Env.BOOT_DELAY,
                                         SutConfig.Env.BOOT_DELAY)
        assert resource_aft
        assert resource_bef in resource_aft
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1614", "[TC1614] Testcase_LoadDefault_017", "Clearcmos与F9后选项对比测试"))
def Testcase_LoadDefault_017():
    """
    Name:       Clearcmos与F9后选项对比测试
    Condition:
    Steps:      1、BMC恢复默认后启动进Setup菜单，此时Redfish收集一份CurrentValue值a；
                2、Setup菜单中按F9恢复默认，F10保存重启进入OS后，再次收集一份CurrentValue值b；
                3、对比ab是否存在差异，有结果A。
    Result:     A：ab对比一致（有差异需确认合理性）。
    Remark:
    """
    try:
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        bef_data = Sut.BMC_RFISH.Attributes()
        assert bef_data
        SetUpLib.send_keys(Key.RESET_DEFAULT, delay=3)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        aft_data = Sut.BMC_RFISH.Attributes()
        assert aft_data
        assert bef_data == aft_data, "Clearcmos_Radfish Not equal to F9_Radfish "
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1615", "[TC1615] Testcase_LoadDefault_018", "BMC与BIOS共同控制选项一致性测试"))
def Testcase_LoadDefault_018():
    """
    Name:       BMC与BIOS共同控制选项一致性测试
    Condition:  1、已梳理公共选项列表如BMC相关配置、BootType等。
    Steps:      1、启动进Setup菜单，修改相关选项，保存重启再次进入Setup菜单，检查选择值与BMC Web显示值是否一致，有结果A；
                2、BMC Web修改选项，保存后重启单板进入Setup菜单检查修改是否生效，有结果A；
                3、拉低GPIO或F9恢复默认值，保存重启进入Setup菜单检查选项是否与BMC Web保持一致，有结果B。
    Result:     A：能修改生效，Setup菜单与BMC保持一致；
                B：Setup菜单与BMC保持一致，BMC相关配置不恢复默认值（看门狗除外），其余恢复默认值。
    Remark:     1、遵循后设置后生效原则；
                # 根据最新规则, 恢复默认时, BootType会自动切换到UEFI模式
    """
    try:
        # Step 1
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.set_option_value(Msg.POWER_POLICY, Msg.VAL_POWER_OFF)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.switch_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, Msg.LEGACY_BOOT, save=True)

        assert SetUpLib.wait_boot_msgs(Msg.BIOS_BOOT_COMPLETE)
        assert BMC_WEB.get_power_policy() == 0
        assert BMC_WEB.get_boot_info().mode == Msg.LEGACY

        # Step 2
        assert BMC_WEB.set_power_policy(mode=1)
        assert BMC_WEB.set_boot_overwrite(once=False, mode=Msg.UEFI)

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        power_policy_b = SetUpLib.get_option_value(Msg.POWER_POLICY, key=Key.UP)
        assert power_policy_b == Msg.VAL_POWER_ON
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.switch_to_page(Msg.PAGE_BOOT)
        boot_type_b = SetUpLib.get_option_value(Msg.BOOT_TYPE)
        assert boot_type_b == Msg.UEFI_BOOT

        # Step 3
        assert SetUpLib.load_default_in_setup(save=True)

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.get_option_value(Msg.POWER_POLICY, key=Key.UP) == Msg.VAL_POWER_ON  # 恢复默认时Power Policy保持不变
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.switch_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.get_option_value(Msg.BOOT_TYPE) == boot_type_b  # 恢复默认时BootType会切换到默认UEFI模式
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        BMC_WEB.set_power_policy(mode=1)


@core.test_case(("1617", "[TC1617] Testcase_GraphDisplay_014", "Quiet Boot默认关闭测试"))
def Testcase_GraphDisplay_014():
    """
    Name:       Quiet Boot默认关闭测试
    Condition:
    Steps:      1、启动进入Setup菜单Boot界面，检查是否存在Quiet Boot选项，OS下通过uniCfg工具读取选项默认值情况，有结果A；
                2、修改此选项，F10保存重启后再次进入OS检查是否生效，有结果B;
    Result:     A：setup菜单未提供Quiet Boot选项，OS读到选项默认关闭；
                B：修改生效；
    Remark:
    """
    try:
        quiet_boot = "Quiet Boot"
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert quiet_boot not in SetUpLib.get_all_options()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1618", "[TC1618] Testcase_DiffDefaultValue_002", "Setup菜单F9后默认值检查"))
def Testcase_DiffDefaultValue_002():
    """
    Name:       Setup菜单F9后默认值检查
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、进入Setup菜单修改部分选项（涉及共用默认值和不同默认值项）保存重启进入Setup菜单检查修改选项是否生效，有结果A；
                2、F9恢复默认值后F10保存重启进入Setup菜单检查是否恢复默认值，有结果B；
                3、遍历所有包含不同默认值的单板。
    Result:     A：修改均已生效；
                B：恢复为默认值，包括公共选项和差异化选项。
    Remark:
    """
    try:
        # Set
        assert SetUpLib.boot_to_bios_config()
        for op in Msg.PICK_OPTIONS:
            page, path, option, set_value, default = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(option, set_value, save=False)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # Check
        assert SetUpLib.continue_to_bios_config()
        for op in Msg.PICK_OPTIONS:
            page, path, option, set_value, default = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(option) == set_value
        # Setup F9 Load Default
        assert SetUpLib.load_default_in_setup(save=True)
        # Verify
        assert SetUpLib.continue_to_bios_config()
        for op in Msg.PICK_OPTIONS:
            page, path, option, set_value, default = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(option) == default
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1619", "[TC1619] Testcase_DiffDefaultValue_003", "Redfish检查单板差异化选项默认值"))
def Testcase_DiffDefaultValue_003():
    """
    Name:       Redfish检查单板差异化选项默认值
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、通过postman工具获取单板CurrentValue、Registry中的"DefaultValue"，有结果A；
                2、遍历所有包含不同默认值的单板。
    Result:     A：CurrentValue、Registry中的"DefaultValue"属性值与开发提供的差异化文档一致。
    Remark:     CurrentValue 位置： https://192.168.28.xxx/redfish/v1/Systems/1/Bios
                Registry文件位置：
                https://192.168.28.136/redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v1_4_3.jso
    """
    try:
        baseline = PlatMisc.baseline_to_dict(dump_file=os.path.join(Env.LOG_DIR, "base.json"))
        registry = Sut.BMC_RFISH.registry_dump(dump_json=True, path=Env.LOG_DIR)
        current = Sut.BMC_RFISH.current_dump(dump_json=True, path=Env.LOG_DIR)

        # V7中一些特殊处理的选项: DisplayName, Baseline_Value, Registry_Value
        current_special = {"Language": ["English", "en-US"]}
        registry_special = {"Power Performance Tuning": ["OS Controls EPB", None]}

        def get_base_default_from_display(display_name, base_dict):
            for base_k, base_v in base_dict.items():
                if base_v["setup"] == display_name:
                    return base_v["default"]
            logging.warning(f"Attributes not defined in baseline: {display_name}")

        def get_display_name_from_registry(curr_name, reg_dict):
            attr_list = reg_dict["RegistryEntries"]["Attributes"]
            for attr in attr_list:
                if attr["AttributeName"] == curr_name:
                    return attr["DisplayName"]
            logging.warning(f"Current AttributeName not found in registry: {curr_name}")

        def current_value_check(current_dict, base_dict, reg_dict):
            fails = 0
            for current_name, current_value in current_dict.items():
                curr_display_name = get_display_name_from_registry(current_name, reg_dict)
                if curr_display_name in current_special:
                    base_default = current_special[curr_display_name][1]
                else:
                    base_default = get_base_default_from_display(curr_display_name, base_dict)
                if base_default:
                    if str(base_default) == str(current_value):
                        continue
                    elif base_default.startswith("0x") and (int(base_default, 16) == current_value):
                        continue
                    logging.error(f"Current default mismatch [{curr_display_name}]: baseline={base_default}, current={current_value}")
                    fails += 1
            return fails == 0

        def registry_default_check(registry_dict, base_dict):
            attributes_list = registry_dict["RegistryEntries"]["Attributes"]
            fails = 0
            for attr in attributes_list:
                attr_default = attr["DefaultValue"]
                display_name = attr["DisplayName"]
                if display_name in registry_special:
                    base_default = registry_special[display_name][1]
                else:
                    base_default = get_base_default_from_display(display_name, base_dict)
                if base_default:
                    if str(base_default) == str(attr_default):
                        continue
                    elif base_default.startswith("0x") and (int(base_default, 16) == attr_default):
                        continue
                    logging.error(f"Registry default mismatch [{display_name}]: baseline={base_default}, registry={attr_default}")
                    fails += 1
            return fails == 0

        assert current_value_check(current, baseline, registry), "current value check fail"
        assert registry_default_check(registry, baseline), "registry default check fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1620", "[TC1620] Testcase_DiffDefaultValue_004", "定制化默认值后单板默认值检查"))
def Testcase_DiffDefaultValue_004():
    """
    Name:       定制化默认值后单板默认值检查
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、OS下通过uniCfg工具（uniCfg -w xxxx:x）修改部分选项（涉及共用默认值和不同默认值项）并通过命令（uniCfg SaveCustomDefault）保存为客户定制化默认值；
                2、重启进入Setup菜单检查定制选项是否生效，有结果A；
                3、F9后检查是否恢复为默认值，有结果B；
                4、遍历所有涉及不同默认值的单板。
    Result:     A：修改均已生效；
                B：恢复为默认值，包括公共选项和差异化选项。
    Remark:
    """
    try:
        # PAGE, PATH, OPTION, AttributeName, SetValue
        pick_options = [[Msg.PAGE_ADVANCED, Msg.PATH_MEM_RAS, Msg.ADDDC_SP, Attr.ADDDC_EN, 0],
                        [Msg.PAGE_ADVANCED, Msg.PATH_UNCORE_GENERAL, Msg.UPI_L0P_EN, Attr.KTI_L0P, 0],
                        [Msg.PAGE_BOOT, [], Msg.BOOT_FAIL_POLICY, Attr.BOOT_FAIL_POLICY, 2]]
        baseline = PlatMisc.baseline_to_dict()

        def get_display_value_from_index(base_dict, attr_name, index):
            attr_info = base_dict[attr_name]
            attr_values = attr_info["values"]
            for v_name, v_index in attr_values.items():
                if int(str(v_index), 16) == int(str(index), 16):
                    return v_name
            raise IndexError(f"Attribute index not found in baseline: {attr_name} -> {index}")

        assert SetUpLib.boot_to_default_os()
        set_ops = {_op[3]: _op[-1] for _op in pick_options}
        assert Sut.UNITOOL.write(**set_ops)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        for op in pick_options:
            page, path, option, attr, set_v = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            display_value = get_display_value_from_index(baseline, attr, set_v)
            assert SetUpLib.get_option_value(option) == display_value

        assert SetUpLib.load_default_in_setup()
        for op in pick_options:
            page, path, option, attr, set_v = op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            default_value = baseline[attr]["default"]
            assert SetUpLib.get_option_value(option) == default_value
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1621", "[TC1621] Testcase_DiffDefaultValue_005", "uniCfg恢复默认后默认值检查"))
def Testcase_DiffDefaultValue_005():
    """
    Name:       uniCfg恢复默认后默认值检查
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、OS下通过uniCfg工具（uniCfg -w xxxx:x）修改部分选项（涉及共用默认值和不同默认值项）保存重启进入Setup菜单检查修改选项是否生效，有结果A；
                2、进入OS 使用uniCfg工具（uniCfg -c)清除配置，重启后进入Setup菜单，检查是否恢复默认值，有结果B；
                4、遍历所有涉及不同默认值的单板。
    Result:     A：修改均已生效；
                B：恢复为默认值，包括公共选项和差异化选项。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        default = Sut.UNITOOL.read(*BiosCfg.HPM_KEEP)
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)

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


@core.test_case(("1622", "[TC1622] Testcase_DiffDefaultValue_007", "全擦升级后默认值检查"))
def Testcase_DiffDefaultValue_007():
    """
    Name:       全擦升级后默认值检查
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、进入Setup菜单修改部分选项（涉及共用默认值和不同默认值项）保存重启进入Setup菜单检查修改选项是否生效，有结果A；
                2、BMC全擦升级后上电进入Setup菜单，检查是否恢复默认值，有结果B；
                4、遍历所有涉及不同默认值的单板。
    Result:     A：修改均已生效；
                B：恢复为默认值，包括公共选项和差异化选项。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        default = Sut.UNITOOL.read(*BiosCfg.HPM_KEEP)
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.flash_bios_bin_and_init()
        SetUpLib.send_key(Key.ENTER)
        assert MiscLib.ping_sut(Env.OS_IP, 500)
        assert Sut.UNITOOL.check(**default)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1623", "[TC1623] Testcase_DiffDefaultValue_008", "BMC Web升级后默认值检查"))
def Testcase_DiffDefaultValue_008():
    """
    Name:       BMC Web升级后默认值检查
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、进入Setup菜单修改部分选项（涉及共用默认值和不同默认值项）保存重启进入Setup菜单检查修改选项是否生效，有结果A；
                2、BMC Web升级BIOS版本后上电进入Setup菜单，检查是否恢复默认值，有结果B；
                3、F9恢复默认值后F10保存重启进入Setup菜单检查是否恢复默认值，有结果C；
                4、遍历所有包含不同默认值的单板。
    Result:     A：修改均已生效；
                B：升级后配置保持不变，不会恢复为默认值，包括公共选项和差异化选项。
                C：恢复为默认值，包括公共选项和差异化选项。
    Remark:
    """
    try:
        hpm_file = PlatMisc.get_latest_hpm_bios()
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.update_bios_hpm(hpm_file)
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        Update.flash_bios_bin_and_init()


@core.test_case(("1624", "[TC1624] Testcase_DiffDefaultValue_009", "Redfish下恢复默认值后默认值检查"))
def Testcase_DiffDefaultValue_009():
    """
    Name:       Redfish下恢复默认值后默认值检查
    Condition:  1、开发提供单板差异化默认值列表
    Steps:      1、Redfish下，使用postman工具修改部分选项（涉及共用默认值和不同默认值项），下发命令后重启进入Setup菜单检查修改选项是否生效，有结果A；
                2、Redfish下使用Patch方法下发指令恢复默认值后重启进入Setup菜单，检查是否恢复默认值，有结果B；
                4、遍历所有涉及不同默认值的单板。
    Result:     A：修改均已生效；
                B：恢复为默认值，包括公共选项和差异化选项。
    Remark:
    """
    try:
        redfish_options = {}
        baseline = PlatMisc.baseline_to_dict()
        for op_k, op_v in BiosCfg.HPM_KEEP.items():
            if op_k not in baseline:
                continue
            values = baseline[op_k]["values"]
            for key, val in values.items():
                if int(val, 16) == op_v:
                    redfish_options[op_k] = key
                    break

        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.LOGO_SHOW)
        logging.info(f"Options for test: {redfish_options}")
        assert redfish_options, "Invalid redfish options"
        default = Sut.BMC_RFISH.read_bios_option(*redfish_options)
        logging.info(f"Default options: {default}")

        set_option = Sut.BMC_RFISH.set_bios_option(**redfish_options)
        if not set_option.result:
            for _opk, _opv in deepcopy(redfish_options).items():
                if _opk in set_option.body:
                    redfish_options.pop(_opk)  # remove dependency items
            assert Sut.BMC_RFISH.set_bios_option(**redfish_options).result, "redfish retry set option fail"
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.BIOS_BOOT_COMPLETE)
        assert Sut.BMC_RFISH.check_bios_option(**redfish_options), f"redfish check option fail"

        assert Sut.BMC_RFISH.bios_load_default()
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.BIOS_BOOT_COMPLETE)
        assert Sut.BMC_RFISH.check_bios_option(**default), f"redfish check load default fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1625", "[TC1625] Testcase_LoadCustomDefaults_001", "Setup默认无“Load Custom Defaults”选项"))
def Testcase_LoadCustomDefaults_001():
    """
    Name:       Setup默认无“Load Custom Defaults”选项
    Condition:  1、未进行过定制化操作，或者BIOS进行全擦升级。
    Steps:      1、启动进入Setup菜单，检查是否存在“Load Custom Defaults”选项，有结果A。
    Result:     A：无 “Load Custom Defaults”菜单。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert not SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1626", "[TC1626] Testcase_LoadCustomDefaults_002", "BMC恢复默认不清除Load Custom Default选项"))
def Testcase_LoadCustomDefaults_002():
    """
    Name:       BMC恢复默认不清除Load Custom Default选项
    Condition:  1、已生成定制化菜单。
    Steps:      1、BMC命令行使用命令拉低GPIO管脚恢复默认值；
                2、单板重启进入菜单，检查"Load Custom Default"选项是否正常显示，有结果A。
                3、F9后F10保存重启再次进入Setup菜单检查"Load Custom Default"选项是否正常显示，有结果A。
    Result:     A：正常显示"Load Custom Default"选项。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.ADDDC_DIS)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)

        assert BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)

        assert SetUpLib.load_default_in_setup(save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1627", "[TC1627] Testcase_LoadCustomDefaults_003", "uniCfg清除Load Custom Default选项"))
def Testcase_LoadCustomDefaults_003():
    """
    Name:       uniCfg清除Load Custom Default选项
    Condition:
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，是否生成“Load Custom Defaults”菜单，有结果A；
                3、进入OS执行uniCfg -c命令后再次重启进入Setup菜单，检查定制选项值和“Load Custom Defaults”菜单，有结果B；
    Result:     A：定制选项值均已生效，存在 “Load Custom Defaults”选项；
                B：定制选项已恢复默认值，不存在 “Load Custom Defaults”选项；
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.ADDDC_DIS)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)

        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.uni_command("-c")
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert not SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1628", "[TC1628] Testcase_LoadCustomDefaults_004", "Web升级不清除Load Custom Default选项"))
def Testcase_LoadCustomDefaults_004():
    """
    Name:       Web升级不清除Load Custom Default选项
    Condition:
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，是否生成“Load Custom Defaults”菜单，有结果A；
                3、Web升级BIOS版本后再次重启进入Setup菜单，检查定制选项值和“Load Custom Defaults”菜单，有结果B；
    Result:     A：正常显示"Load Custom Default"选项。
    Remark:
    """
    try:
        new_hpm_file = PlatMisc.get_latest_hpm_bios()

        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)

        assert Update.update_bios_hpm(new_hpm_file)
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        assert SetUpLib.back_to_front_page()
        SetUpLib.send_key(Key.ENTER)
        assert MiscLib.ping_sut(Env.OS_IP, Env.BOOT_DELAY)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        Update.flash_bios_bin_and_init()


@core.test_case(("1629", "[TC1629] Testcase_LoadCustomDefaults_005", "BMC相关选项不支持定制测试"))
def Testcase_LoadCustomDefaults_005():
    """
    Name:       BMC相关选项不支持定制测试
    Condition:
    Steps:      1、OS下使用uniCfg工具定制BMC相关配置（比如看门狗、Ipv4、Ipv6、网口模式、风扇调速、上电策略、SSH服务等)，检查能否定制成功，有结果A；
                2、重启进入Setup菜单检查选项是否变更，有结果B；
    Result:     A：定制失败，提示报错；
                B：选项保持不变。
    Remark:     1、不支持选项见Setup菜单基线列表
    """
    try:
        baseline = PlatMisc.baseline_to_dict(dump_file="file.json")
        bmc_cfg = [v for k, v in Attr.__dict__.items() if k.startswith("BMC_")]
        unsupported = {}
        for _bmc_var in bmc_cfg:
            if baseline[_bmc_var]["unicfg"]:
                continue  # 从基线列表中挑选出不支持uniCfg的BMC相关变量
            logging.info(f"BMC variable not support uniCfg: {_bmc_var}")
            values = baseline[_bmc_var]["values"].values()
            choice_val = random.choice(list(values))
            unsupported[_bmc_var] = choice_val

        assert SetUpLib.boot_to_default_os()
        read_var = Sut.UNITOOL.read(*unsupported)
        read_pass = []
        for key_r, val_r in read_var.items():
            if not (val_r is None):
                logging.error(f"BMC variable should not read success: {key_r}")
                read_pass.append(key_r)

        write_pass = []
        for key_w, val_w in unsupported.items():
            if Sut.UNITOOL.write(**{key_w: val_w}):
                logging.error(f"BMC variable should not write success: {key_w}")
                write_pass.append(key_w)
        assert (not read_pass) and (not write_pass), f"read success: {read_pass}\nwrite success: {write_pass}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1630", "[TC1630] Testcase_LoadCustomDefaultUefi_001", "【UEFI】定制化恢复功能测试"))
def Testcase_LoadCustomDefaultUefi_001():
    """
    Name:       【UEFI】定制化恢复功能测试
    Condition:  1、UEFI模式。
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，是否生成“Load Custom Defaults”菜单，有结果A；
                3、Setup中更改定制化选项为非定制化值，F10保存重启，再次进入Setup菜单检查选项值是否改为非定制化值，有结果B；
                4、点击“Load Custom Defaults”，检查定制化选项是否恢复定制化值，有结果C。
    Result:     A：定制选项值均已生效，存在 “Load Custom Defaults”选项；
                B：设置生效，均为非定制化值；
                C：均恢复为定制化值。
    Remark:     1、./uniCfg -wf xxx.ini文件方式可定制多个变量；
    """
    try:
        bios_option = _get_attr_dict()
        # step 1
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**bios_option)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        # step 2
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        # result A
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        # step 3
        for set_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = set_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # result B
        assert SetUpLib.continue_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == change_val
        # step 4
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result C
        for set_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = set_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1631", "[TC1631] Testcase_LoadCustomDefaultUefi_002", "【UEFI】定制化恢复前修改部分菜单测试"))
def Testcase_LoadCustomDefaultUefi_002():
    """
    Name:       【UEFI】定制化恢复前修改部分菜单测试
    Condition:  1、UEFI模式；
                2、Setup菜单修改部分选项为非默认值，且已生效，假设此选项集合为a，修改成非默认值b，集合a的选项默认值为c。
    Steps:      1、OS下使用uniCfg工具定制任意选项，假定为集合d（a，d可存在交集)，定制值为e，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，有结果A；
                3、Setup中更改定制化选项集合d为非e，更改集合a选项值为非b，F10保存重启，再次进入Setup菜单检查集合a，d选项值修改是否生效，有结果B；
                4、点击“Load Custom Defaults”，检查集合a，d选项值恢复状态，有结果C。
    Result:     A：定制选项均已生效，为e（a,d交集选项值为e，非b）；
                B：a，d集合选项均设置生效；
                C：集合a恢复为b，集合d恢复为e（a,d交集选项值为e）
    Remark:     1、./uniCfg -wf xxx.ini文件方式可定制多个变量；
                2、Load Custom Defaults恢复至./uniCfg SaveCustomDefault前所有变量值的状态。
    """
    setup_option = Msg.CUSTOM_OPTIONS[:-1]
    os_option = Msg.CUSTOM_OPTIONS[1:]
    os_attr = _get_attr_dict(options=os_option)

    try:
        # condition 2
        assert SetUpLib.boot_to_bios_config()
        for set_op in setup_option:
            page, path, op_name, custom_val, change_val, attr_dict = set_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, custom_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # step 1
        assert SetUpLib.boot_to_default_os(reset=False)
        assert Sut.UNITOOL.write(**os_attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        # step 2 + step 3
        assert SetUpLib.boot_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
            assert SetUpLib.set_option_value(op_name, value=change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # result B
        assert SetUpLib.continue_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == change_val
        # step 4
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result C
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1632", "[TC1632] Testcase_LoadCustomDefaultUefi_003", "【UEFI】定制化恢复后修改菜单值测试"))
def Testcase_LoadCustomDefaultUefi_003():
    """
    Name:       【UEFI】定制化恢复后修改菜单值测试
    Condition:  1、UEFI模式；
                2、默认配置。
    Steps:      1、OS下使用uniCfg工具定制任意选项，假定为集合d，定制值为e，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，有结果A；
                3、Setup中更改定制化选项集合d为非e，更改其他一些非集合b的选项，假定为集合a（a，d可存在交集）选项值为非默认值，假定为b，F10保存重启，再次进入Setup菜单检查集合a，d选项值修改是否生效，有结果B；
                4、点击“Load Custom Defaults”，检查集合a，d选项值恢复状态，有结果C。
    Result:     A：定制选项均已生效，为e；
                B：a，d集合选项均设置生效；
                C：集合a恢复为默认值，集合d恢复为e（a,d交集选项值为e）
    Remark:     1、./uniCfg -wf xxx.ini文件方式可定制多个变量；
                2、Load Custom Defaults恢复至./uniCfg SaveCustomDefault前所有变量值的状态。
    """
    setup_option = Msg.CUSTOM_OPTIONS[:-1]
    os_option = Msg.CUSTOM_OPTIONS[1:]
    os_attr = _get_attr_dict(options=os_option)

    try:
        # step 1
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**os_attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        # step 2 + step 3
        assert SetUpLib.boot_to_bios_config()
        for os_op in os_option:  # 集合d
            page, path, op_name, custom_val, change_val, attr_dict = os_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
            assert SetUpLib.set_option_value(op_name, value=change_val)
        for setup_op in setup_option:  # 集合a
            page, path, op_name, custom_val, change_val, attr_dict = setup_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, value=change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # result B
        assert SetUpLib.continue_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == change_val
        # step 4
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result C
        for os_check in os_option:
            page, path, op_name, custom_val, change_val, attr_dict = os_check
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val  # 集合d恢复为e
        baseline = PlatMisc.baseline_to_dict(var_key=False)
        for setup_check in setup_option:
            page, path, op_name, custom_val, change_val, attr_dict = setup_check
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            if setup_check in os_option:  # 交集
                assert SetUpLib.get_option_value(op_name) == custom_val
            else:
                assert baseline[op_name]["default"] == SetUpLib.get_option_value(op_name)  # 集合a恢复为默认值
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1633", "[TC1633] Testcase_LoadCustomDefaultUefi_004", "【UEFI】定制化恢复后F9恢复BIOS默认值"))
def Testcase_LoadCustomDefaultUefi_004():
    """
    Name:       【UEFI】定制化恢复后F9恢复BIOS默认值
    Condition:  1、UEFI模式。
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)（最后一步需要执行./uniCfg SaveCustomDefault）；
                2、重启进入Setup菜单，更改定制化选项为非定制化值，F10保存重启；
                3、再次进入Setup菜单，点击“Load Custom Defaults”，检查定制化选项是否恢复定制化值，有结果A。
                4、恢复定制化默认值之后，在Setup菜单下使用F9恢复BIOS默认值，检查恢复项目，有结果B。
    Result:
                A：选项均恢复为定制化值；
                B：F9之后，恢复到BIOS默认值。
    Remark:
    """
    try:
        attr = _get_attr_dict()
        # step 1
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        # step 2
        assert SetUpLib.boot_to_bios_config()
        for setup_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = setup_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, value=change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # step 3
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        # step 4
        baseline = PlatMisc.baseline_to_dict(var_key=False)
        assert SetUpLib.load_default_in_setup()
        for setup_check in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = setup_check
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert baseline[op_name]["default"] == SetUpLib.get_option_value(op_name)  # 集合a恢复为默认值
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1634", "[TC1634] Testcase_LoadCustomDefaultUefi_005", "【UEFI】装备模式下定制化操作测试"))
def Testcase_LoadCustomDefaultUefi_005():
    """
    Name:       【UEFI】装备模式下定制化操作测试
    Condition:  1、UEFI模式；
                2、OS下设置装备模式。
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，是否生成“Load Custom Defaults”菜单，有结果A；
                3、Setup中更改定制化选项为非定制化值，F10保存重启，再次进入Setup菜单点击“Load Custom Defaults”，检查定制化选项是否恢复定制化值，有结果B。
    Result:     A：定制选项值均已生效，存在 “Load Custom Defaults”选项；
                B：均恢复为定制化值。
    Remark:
    """
    try:
        attr = _get_attr_dict()
        # condition 2
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**{Attr.EQUIP_FLAG: 1})
        # step 1
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT)
        # step 2
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
            # step 3
            assert SetUpLib.set_option_value(op_name, change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result B
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default()


@core.test_case(("1635", "[TC1635] Testcase_LoadCustomDefaultLegacy_001", "【Legacy】定制化恢复功能测试"))
@mark_legacy_test
def Testcase_LoadCustomDefaultLegacy_001():
    """
    Name:       【Legacy】定制化恢复功能测试
    Condition:  1、Legacy模式。
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，是否生成“Load Custom Defaults”菜单，有结果A；
                3、Setup中更改定制化选项为非定制化值，F10保存重启，再次进入Setup菜单检查选项值是否改为非定制化值，有结果B；
                4、点击“Load Custom Defaults”，检查定制化选项是否恢复定制化值，有结果C。
    Result:     A：定制选项值均已生效，存在 “Load Custom Defaults”选项；
                B：设置生效，均为非定制化值；
                C：均恢复为定制化值。
    Remark:     1、./uniCfg -wf xxx.ini文件方式可定制多个变量；
    """
    try:
        bios_option = _get_attr_dict()
        # step 1
        assert SetUpLib.boot_to_default_os(uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.write(**bios_option)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT, uefi=False)
        # step 2
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        # result A
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        # step 3
        for set_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = set_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # result B
        assert SetUpLib.continue_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == change_val
        # step 4
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result C
        for set_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = set_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default(uefi=False)


@core.test_case(("1636", "[TC1636] Testcase_LoadCustomDefaultLegacy_002", "【Legacy】定制化恢复前修改部分菜单测试"))
@mark_legacy_test
def Testcase_LoadCustomDefaultLegacy_002():
    """
    Name:       【Legacy】定制化恢复前修改部分菜单测试
    Condition:  1、Legacy模式；
                2、Setup菜单修改部分选项为非默认值，且已生效，假设此选项集合为a，修改成非默认值b，集合a的选项默认值为c。
    Steps:      1、OS下使用uniCfg工具定制任意选项，假定为集合d（a，d可存在交集)，定制值为e，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，有结果A；
                3、Setup中更改定制化选项集合d为非e，更改集合a选项值为非b，F10保存重启，再次进入Setup菜单检查集合a，d选项值修改是否生效，有结果B；
                4、点击“Load Custom Defaults”，检查集合a，d选项值恢复状态，有结果C。
    Result:     A：定制选项均已生效，为e（a,d交集选项值为e，非b）；
                B：a，d集合选项均设置生效；
                C：集合a恢复为b，集合d恢复为e（a,d交集选项值为e）
    Remark:     1、./uniCfg -wf xxx.ini文件方式可定制多个变量；
                2、Load Custom Defaults恢复至./uniCfg SaveCustomDefault前所有变量值的状态。
    """
    setup_option = Msg.CUSTOM_OPTIONS[:-1]
    os_option = Msg.CUSTOM_OPTIONS[1:]
    os_attr = _get_attr_dict(options=os_option)

    try:
        # condition 2
        assert SetUpLib.boot_to_bios_config()
        for set_op in setup_option:
            page, path, op_name, custom_val, change_val, attr_dict = set_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, custom_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # step 1
        assert SetUpLib.boot_to_default_os(reset=False, uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.write(**os_attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT, uefi=False)
        # step 2 + step 3
        assert SetUpLib.boot_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
            assert SetUpLib.set_option_value(op_name, value=change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # result B
        assert SetUpLib.continue_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == change_val
        # step 4
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result C
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default(uefi=False)


@core.test_case(("1637", "[TC1637] Testcase_LoadCustomDefaultLegacy_003", "【Legacy】定制化恢复后修改菜单值测试"))
@mark_legacy_test
def Testcase_LoadCustomDefaultLegacy_003():
    """
    Name:       【Legacy】定制化恢复后修改菜单值测试
    Condition:  1、Legacy模式；
                2、默认配置。
    Steps:      1、OS下使用uniCfg工具定制任意选项，假定为集合d，定制值为e，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，有结果A；
                3、Setup中更改定制化选项集合d为非e，更改其他一些非集合b的选项，假定为集合a（a，d可存在交集）选项值为非默认值，假定为b，F10保存重启，再次进入Setup菜单检查集合a，d选项值修改是否生效，有结果B；
                4、点击“Load Custom Defaults”，检查集合a，d选项值恢复状态，有结果C。
    Result:     A：定制选项均已生效，为e；
                B：a，d集合选项均设置生效；
                C：集合a恢复为默认值，集合d恢复为e（a,d交集选项值为e）
    Remark:     1、./uniCfg -wf xxx.ini文件方式可定制多个变量；
                2、Load Custom Defaults恢复至./uniCfg SaveCustomDefault前所有变量值的状态。
    """
    setup_option = Msg.CUSTOM_OPTIONS[:-1]
    os_option = Msg.CUSTOM_OPTIONS[1:]
    os_attr = _get_attr_dict(options=os_option)

    try:
        # step 1
        assert SetUpLib.boot_to_default_os(uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.write(**os_attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT, uefi=False)
        # step 2 + step 3
        assert SetUpLib.boot_to_bios_config()
        for os_op in os_option:  # 集合d
            page, path, op_name, custom_val, change_val, attr_dict = os_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
            assert SetUpLib.set_option_value(op_name, value=change_val)
        for setup_op in setup_option:  # 集合a
            page, path, op_name, custom_val, change_val, attr_dict = setup_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, value=change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # result B
        assert SetUpLib.continue_to_bios_config()
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == change_val
        # step 4
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result C
        for os_check in os_option:
            page, path, op_name, custom_val, change_val, attr_dict = os_check
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val  # 集合d恢复为e
        baseline = PlatMisc.baseline_to_dict(var_key=False)
        for setup_check in setup_option:
            page, path, op_name, custom_val, change_val, attr_dict = setup_check
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            if setup_check in os_option:  # 交集
                assert SetUpLib.get_option_value(op_name) == custom_val
            else:
                assert baseline[op_name]["default"] == SetUpLib.get_option_value(op_name)  # 集合a恢复为默认值
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default(uefi=False)


@core.test_case(("1638", "[TC1638] Testcase_LoadCustomDefaultLegacy_004", "【Legacy】定制化恢复后F9恢复BIOS默认值"))
@mark_legacy_test
def Testcase_LoadCustomDefaultLegacy_004():
    """
    Name:       【Legacy】定制化恢复后F9恢复BIOS默认值
    Condition:  1、Legacy模式。
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)（最后一步需要执行./uniCfg SaveCustomDefault）；
                2、重启进入Setup菜单，更改定制化选项为非定制化值，F10保存重启；
                3、再次进入Setup菜单，点击“Load Custom Defaults”，检查定制化选项是否恢复定制化值，有结果A。
                4、恢复定制化默认值之后，在Setup菜单下使用F9恢复BIOS默认值，检查恢复项目，有结果B。
    Result:
                A：选项均恢复为定制化值；
                B：F9之后，恢复到BIOS默认值。
    Remark:
    """
    try:
        attr = _get_attr_dict()
        # step 1
        assert SetUpLib.boot_to_default_os(uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.write(**attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT, uefi=False)
        # step 2
        assert SetUpLib.boot_to_bios_config()
        for setup_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = setup_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.set_option_value(op_name, value=change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # step 3
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        # step 4
        baseline = PlatMisc.baseline_to_dict(var_key=False)
        assert SetUpLib.load_default_in_setup()
        for setup_check in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = setup_check
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert baseline[op_name]["default"] == SetUpLib.get_option_value(op_name)  # 集合a恢复为默认值
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default(uefi=False)


@core.test_case(("1639", "[TC1639] Testcase_LoadCustomDefaultLegacy_005", "【Legacy】装备模式下定制化操作测试"))
@mark_legacy_test
def Testcase_LoadCustomDefaultLegacy_005():
    """
    Name:       【Legacy】装备模式下定制化操作测试
    Condition:  1、Legacy模式；
                2、OS下设置装备模式。
    Steps:      1、OS下使用uniCfg工具定制任意选项（比如启动项设置，启动类型，PXE设置，CPU配置…)，定制成功后执行./uniCfg SaveCustomDefault；
                2、重启进入Setup菜单，检查定制选项值是否生效，是否生成“Load Custom Defaults”菜单，有结果A；
                3、Setup中更改定制化选项为非定制化值，F10保存重启，再次进入Setup菜单点击“Load Custom Defaults”，检查定制化选项是否恢复定制化值，有结果B。
    Result:     A：定制选项值均已生效，存在 “Load Custom Defaults”选项；
                B：均恢复为定制化值。
    Remark:
    """
    try:
        attr = _get_attr_dict()
        # condition 2
        assert SetUpLib.boot_to_default_os(uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.write(**{Attr.EQUIP_FLAG: 1})
        # step 1
        assert SetUpLib.boot_to_default_os(uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.write(**attr)
        assert PlatMisc.uni_command(Msg.UNI_SAVE_CUSTOM_DEFAULT, uefi=False)
        # step 2
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
            # step 3
            assert SetUpLib.set_option_value(op_name, change_val)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Msg.LOAD_CUSTOM_DEFAULT)
        SetUpLib.send_keys([Key.ENTER, Key.ENTER], delay=3)
        # result B
        for check_op in Msg.CUSTOM_OPTIONS:
            page, path, op_name, custom_val, change_val, attr_dict = check_op
            assert SetUpLib.switch_to_page(page)
            if path:
                assert SetUpLib.enter_menu(path)
            assert SetUpLib.get_option_value(op_name) == custom_val
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _clear_custom_default(uefi=False)


# @core.test_case(("1640", "[TC1640] Testcase_NVMeSlotInfoUefi_001", "NVMe丝印信息显示"))
# def Testcase_NVMeSlotInfoUefi_001():
#     """
#     Name:       NVMe丝印信息显示
#     Condition:  1、UEFI模式；
#                 2、接NVMe背板且有NVMe盘。
#     Steps:      1、启动进Setup菜单，NVMe界面下查看NVMe信息显示是否正确（包含但不限于厂商、丝印号、序列号），有结果A。
#     Result:     A：NVMe显示信息与实际一致。
#     Remark:     1、丝印信息与实际接的位置相对应。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1641", "[TC1641] Testcase_NVMeSlotInfoLegacy_001", "【Legacy】传统模式NVMe信息显示"))
# def Testcase_NVMeSlotInfoLegacy_001():
#     """
#     Name:       【Legacy】传统模式NVMe信息显示
#     Condition:  1、Legacy模式；
#                 2、接NVMe背板且有NVMe盘。
#     Steps:      1、启动进Setup菜单，NVMe界面下查看NVMe信息是否显示，有结果A；
#     Result:     A：NVMe显示信息与实际一致。
#     Remark:     1、丝印信息与实际接的位置相对应。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1642", "[TC1642] Testcase_CpuDisplay_001", "满配CPU时Setup菜单CPU信息显示测试"))
def Testcase_CpuDisplay_001():
    """
    Name:       满配CPU时Setup菜单CPU信息显示测试
    Condition:  1、满配CPU。
    Steps:      1、启动进入Setup菜单Processor Configuration界面，查看CPU信息显示是否正确，有结果A。
    Result:     A：CPU stepping、Processor ID、频率、微码、标称电压、L1\L2\L3 Cache、CPU型号、CPU标称核数、TDP、Thread均显示正确，不显示多余CPU信息。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PER_CPU_INFO)
        assert SetUpLib.verify_options(SutConfig.Sys.CPU_INFO, integer=None)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1644", "[TC1644] Testcase_CpuDisplay_004", "关核后Setup菜单CPU信息显示测试"))
def Testcase_CpuDisplay_004():
    """
    Name:       关核后Setup菜单CPU信息显示测试
    Condition:
    Steps:      1、启动进入Setup菜单关闭CPU部分核，F10保存重启后进入Setup菜单Processor Configuration界面，查看CPU信息显示是否正确，有结果A。
    Result:     A：CPU stepping、Processor ID、频率、微码、标称电压、L1\L2\L3 Cache、CPU型号、CPU标称核数、TDP、Thread均显示正确，CPU标称核数不受关核影响，显示标称核数。
    Remark:
    """
    set_core = SutConfig.Sys.CPU_CORES // 2
    core_close_info = deepcopy(SutConfig.Sys.CPU_INFO)
    core_close_info['Active Cores / Total Cores'] = f'{set_core}/{SutConfig.Sys.CPU_CORES}'
    core_close_info['Active Threads'] = f'{set_core * 2}'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{set_core}", save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PER_CPU_INFO)
        assert SetUpLib.verify_options(core_close_info, integer=None)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1645", "[TC1645] Testcase_MemoryDisplay_001", "Setup菜单内存信息显示测试"))
def Testcase_MemoryDisplay_001():
    """
    Name:       Setup菜单内存信息显示测试
    Condition:
    Steps:      1、启动进Setup菜单Memory Topology界面，查看内存信息显示是否正确，有结果A；
    Result:     A：信息显示完整，无多余槽位显示。
    Remark:     显示内存拓扑信息如下：
                1、在位信息（按照服务器丝印规范填写）
                2、容量
                3、厂家
                4、DIMM类型，比如LRDIMM，RDIMM，intel DCPMM
                5、频率：规格频率
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEN_INFO, Key.UP)
        assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1646", "[TC1646] Testcase_MemoryDisplay_002", "Setup菜单内存信息显示长时间测试"))
def Testcase_MemoryDisplay_002():
    """
    Name:       Setup菜单内存信息显示长时间测试
    Condition:
    Steps:      1、启动进Setup菜单Memory Topology界面，查看内存信息显示是否正确，有结果A；
                2、重复步骤1 5次。
    Result:     A：信息显示完整，无多余槽位显示。
    Remark:     显示内存拓扑信息如下：
                1、在位信息（按照服务器丝印规范填写）
                2、容量
                3、厂家
                4、DIMM类型，比如LRDIMM，RDIMM，intel DCPMM
                5、频率：规格频率
    """
    try:
        for i in range(0, 6):
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_MEN_INFO, Key.UP)
            assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO), f'No.{i} verify_men_info, fail'
            i += 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1647", "[TC1647] Testcase_MemoryDisplay_005", "满配内存Setup菜单信息显示测试"))
# def Testcase_MemoryDisplay_005():
#     """
#     Name:       满配内存Setup菜单信息显示测试
#     Condition:  1、满配内存条。
#     Steps:      1、启动进入Setup菜单Memory Topology界面，查看内存信息显示是否正确，有结果A。
#     Result:     A：信息显示完整。
#     Remark:     显示内存拓扑信息如下：
#                 1、在位信息（按照服务器丝印规范填写）
#                 2、容量
#                 3、厂家
#                 4、DIMM类型，比如LRDIMM，RDIMM，intel DCPMM
#                 5、频率：规格频率
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1648", "[TC1648] Testcase_UsbCount_001", "Setup菜单USB键盘鼠标数量显示测试"))
def Testcase_UsbCount_001():
    """
    Name:       Setup菜单USB键盘鼠标数量显示测试
    Condition:
    Steps:      1、启动进Setup菜单，查看USB键盘鼠标数量，有结果A；
                2、外插USB键盘和鼠标，重启进Setup菜单，查看USB键盘鼠标数量，有结果B。
    Result:     A：USB键盘和鼠标数量与实际一致（默认存在一个KVM键盘和鼠标）；
                B：USB键盘和鼠标数量各加1。
    Remark: 开启KVM后,USB键盘和鼠标数量都是1, 默认测试环境不开启KVM
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_USB_CFG)
        assert SetUpLib.get_option_value(Msg.USB_MOUSE, integer=None) == str(SutConfig.Sys.USB_MOUSE)
        assert SetUpLib.get_option_value(Msg.USB_KEYBOARD, integer=None) == str(SutConfig.Sys.USB_KEYBOARD)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1649", "[TC1649] Testcase_UsbCount_002", "Setup菜单USB存储设备数量显示测试"))
def Testcase_UsbCount_002():
    """
    Name:       Setup菜单USB存储设备数量显示测试
    Condition:
    Steps:      1、启动进Setup菜单，查看USB存储设备数量，有结果A；
                2、插入1个U盘，重启进Setup菜单，查看USB存储设备数量，有结果B。
    Result:     A：USB存储设备与实际一致，不外插USB存储设备时为0；
                B：USB存储设备数量加1。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_USB_CFG)
        assert int(SetUpLib.get_option_value(Msg.USB_STORAGE, integer=None)) == SutConfig.Sys.USB_STORAGE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1650", "[TC1650] Testcase_UsbCount_004", "SP设备不作为USB设备数量统计"))
def Testcase_UsbCount_004():
    """
    Name:       SP设备不作为USB设备数量统计
    Condition:
    Steps:      1、启动进Setup菜单，关闭SP启动，F10保存重启再次进Setup菜单查看USB设备数量，有结果A；
                2、启动进Setup菜单，打开SP启动，F10保存重启再次进Setup菜单查看USB设备数量，有结果A；
    Result:     A：USB设备数量显示与实际一致，SP开启或关闭，USB设备数量保持不变。
    Remark:
    """
    def verify_set(set_value):
        try:
            assert SetUpLib.set_option_value(Msg.SP_BOOT, set_value, save=True)  # 关闭/开启 Boot界面SP参数保存并重启)
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_USB_CFG)
            assert SetUpLib.verify_info(usb_list)
            return True
        except Exception as e:
            logging.error(e)
            return False
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert verify_set(Msg.DISABLE)
        assert SetUpLib.switch_to_page(Msg.PAGE_BOOT)
        assert verify_set(Msg.ENABLE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1651", "[TC1651] Testcase_MainDisplay_001", "Main菜单正确显示信息测试"))
def Testcase_MainDisplay_001():
    """
    Name:       Main菜单正确显示信息测试
    Condition:
    Steps:      1、启动l进Setup菜单，查看Main菜单信息是否显示齐全并与实际一致（版本号、编译时间、产品名称、序列号、CPU型号、CPU数量、内存频率、内存容量、CPU TDP信息），有结果A。
    Result:     A：版本号、编译时间、产品名称、序列号、CPU型号、CPU数量、内存频率（运行频率）、内存容量、CPU TDP等信息与实际一致。
    Remark:     1、内存频率需要参照不同CPU支持的运行频率。
    """
    main_dict = {Msg.PAGE_INFO: SutConfig.Env.BIOS_VER_LATEST,
                 'Release Date': SutConfig.Env.BIOS_DATE_LATEST,
                 'Product Name': SutConfig.Env.PROJECT_NAME,
                 'System Number': 'To be filled by O.E.M.',
                 'Processor Type': SutConfig.Sys.CPU_FULL_NAME,
                 'Node Number': SutConfig.Sys.CPU_CNT,
                 'Processor Core Count': SutConfig.Sys.CPU_CORES,
                 'TDP': SutConfig.Sys.CPU_TDP,
                 'Total Memory': SutConfig.Sys.MEM_SIZE * 1024,
                 'System Memory Speed': SutConfig.Sys.MEM_FREQ}
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        main_info = SetUpLib.get_main_info(Key.DOWN)
        assert main_info, "Fail to get info in mani page"
        for key, value in main_dict.items():
            assert key in main_info, f"Option {key} not found"
            assert str(value) in main_info[key], f"'{key}' value mismatch, expect={value}, actually={main_info[key]}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1653", "[TC1653] Testcase_MainDisplay_004", "修改内存频率时Main菜单显示"))
def Testcase_MainDisplay_004():
    """
    Name:       修改内存频率时Main菜单显示
    Condition:  1、假设默认运行频率为X（X=MIN(当前内存频率，CPU支持最大频率））。
    Steps:      1、启动进Setuo菜单，修改内存频率为Y（Y<X），F10保存重启再次进Setup菜单检查Main菜单下内存频率，有结果A；
                2、修改内存频率为Y（Y>X），F10保存重启再次进Setup菜单检查Main菜单下内存频率，有结果B；
                2、F9恢复内存频率默认设置Auto，F10保存重启再次进入Setup菜单检查Main菜单下内存频率，有结果B。
    Result:     A：内存频率为Y；
                B：内存频率为X。
    Remark:     1、CPU支持频率参考Intel官网：https://ark.intel.com/content/www/us/en/ark.html
    """
    cut_stat = 'START_DIMMINFO_SYSTEM_TABLE'
    cut_end = 'STOP_DIMMINFO_SYSTEM_TABLE'

    def set_mem_freq_and_verify(set_value: int):
        expect_freq = str(min(set_value, SutConfig.Sys.MEM_FREQ))
        assert SetUpLib.set_option_value(Msg.MEM_FREQ, str(set_value), save=True)
        log_cut_min = SerialLib.cut_log(Sut.BIOS_COM, cut_stat, cut_end, 30, SutConfig.Env.BOOT_DELAY)
        assert re.search(expect_freq, log_cut_min), f'Verify MEM freq in serial log fail: {set_value}'
        assert SetUpLib.continue_to_page(Msg.PAGE_INFO)
        main_info_set = SetUpLib.get_main_info()
        assert main_info_set
        assert expect_freq in main_info_set.get(Msg.SYS_MEM_SPEED), "Check mem freq fail in setup: min"
        assert SetUpLib.switch_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG)
        return True

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG)
        val_default = SetUpLib.get_option_value(Msg.MEM_FREQ)
        val_all = SetUpLib.get_all_values(Msg.MEM_FREQ)
        set_freq_list = [val for val in val_all if val.isdigit() and (val != val_default)]  # 排除掉非数字和默认项
        min_freq = min(list(map(int, set_freq_list)))        # 获取 可选最小项
        max_freq = max(list(map(int, set_freq_list)))        # 获取 可选最大项

        if min_freq < SutConfig.Sys.MEM_FREQ:
            assert set_mem_freq_and_verify(min_freq)
        if max_freq > SutConfig.Sys.MEM_FREQ:
            assert set_mem_freq_and_verify(min_freq)

        logging.info("Reset default...")
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        main_info_auto = SetUpLib.get_main_info()
        assert main_info_auto
        assert str(SutConfig.Sys.MEM_FREQ) in main_info_auto.get(Msg.SYS_MEM_SPEED), "Check mem freq fail in setup: auto"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1654", "[TC1654] Testcase_MainDisplay_005", "修改序列号时Main菜单显示"))
# def Testcase_MainDisplay_005():
#     """
#     Name:       修改序列号时Main菜单显示
#     Condition:  1、假设默认序列号为X。
#     Steps:      1、通过Ipmi工具修改单板序列号为Y，上电进入Setup菜单检查Main菜单下序列号，有结果A；
#                 1、通过Ipmi工具恢复单板序列号为X，上电进入Setup菜单检查Main菜单下序列号，有结果B；
#     Result:     A：序列号为Y；
#                 B：序列号为X；
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


@core.test_case(("1657", "[TC1657] Testcase_HelpInfo_003", "Setup启动模式信息显示测试"))
def Testcase_HelpInfo_003():
    """
    Name:       Setup启动模式信息显示测试
    Condition:
    Steps:      1、启动进入Setup菜单，查看BootType启动类型分类显示，有结果A。
    Result:     A：启动模式分Legacy和UEFI，无Dual boot type。
    Remark:     1、Help信息也不显示
    """
    sup_val = ['UEFIBoot', 'LegacyBoot']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        type_list = SetUpLib.get_all_values(Msg.BOOT_TYPE)
        assert MiscLib.same_values(type_list, sup_val)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1659", "[TC1659] Testcase_HelpInfo_005", "菜单操作热键功能测试"))
def Testcase_HelpInfo_005():
    """
    Name:       菜单操作热键功能测试
    Condition:
    Steps:      1、启动进入Setup菜单，逐一按下操作热键(F1/F5/F6/F9/F10/ESC/ENTER/上下左右按键)，观察热键功能是否正确，有结果A。
    Result:     A：所有操作热键功能实现并且正确。
    Remark:     具体功能参照热键help信息
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.CONSOLE_CONFIG)
        logging.info("Test hotkey: F2")
        SetUpLib.send_key(Key.F2)
        assert SetUpLib.wait_msg(Msg.KEYBOARD_FR), "Hotkey test fail: F2"

        assert SetUpLib.locate_option(Msg.CONSOLE_REDIR)
        logging.info("Test hotkey: F6")
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.locate_option([Msg.CONSOLE_REDIR, Msg.DISABLE]), "Hotkey test fail: F6"

        logging.info("Test hotkey: F5")
        SetUpLib.send_key(Key.F5)
        assert SetUpLib.locate_option([Msg.CONSOLE_REDIR, Msg.ENABLE]), "Hotkey test fail: F5"

        logging.info("Test hotkey: F9")
        assert SetUpLib.load_default_in_setup()

        logging.info("Test hotkey: F10")
        SetUpLib.send_key(Key.F10)
        assert SetUpLib.wait_msg(Msg.SAVE_EXIT_PROMPT), "Hotkey test fail: F10"
        SetUpLib.send_key(Key.ESC, delay=1)

        logging.info("Test hotkey: Left")
        assert SetUpLib.switch_to_page(Msg.PAGE_SAVE, key=Key.LEFT)

        logging.info("Test hotkey: Right")
        assert SetUpLib.switch_to_page(Msg.PAGE_ADVANCED, key=Key.RIGHT)

        logging.info("Test hotkey: UP")
        assert SetUpLib.locate_option(Msg.MISC_CONFIG, key=Key.UP)

        logging.info("Test hotkey: DOWN")
        assert SetUpLib.locate_option(Msg.CPU_CONFIG, key=Key.DOWN)

        logging.info("Test hotkey: ENTER")
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Msg.PROCESSOR_CONFIG)

        logging.info("Test hotkey: ESC")
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.locate_option(Msg.MISC_CONFIG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1660", "[TC1660] Testcase_HelpInfoUefi_001", "【UEFI】PXE启动设备名称显示测试"))
def Testcase_HelpInfoUefi_001():
    """
    Name:       【UEFI】PXE启动设备名称显示测试
    Condition:  1、UEFI模式。
    Steps:      1、启动进入BootManager页面，检查PXE设备启动名称显示，有结果A；
                2、按键Esc退出，进入到Setup页面，查看PXE Configuration、Boot Sequence以及启动项分类选项，观察PXE设备名称显示是否正确，有结果A。
    Result:     A：启动项分类名称、启动设备名称及帮助信息显示为PXE，没有BEV字样出现。
    Remark:
    """
    def verify_pxe(refresh=False):
        try:
            boot_dict = SetUpLib.get_all_options(refresh=refresh)
            boot_list = list(map(str, boot_dict.keys()))
            for pxe_info in boot_list:
                if "PXE" in pxe_info:
                    assert "BEV" not in pxe_info, f"{pxe_info} found 'BEV', fail "
            return True
        except Exception as e:
            logging.error(e)
            return False
    try:
        assert SetUpLib.boot_to_bootmanager()               # BootManager_page 检查PXE设备启动名称显示
        assert verify_pxe(refresh=True)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)     # PXE_Configuration 检查PXE设备启动名称显示
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert verify_pxe()
        assert SetUpLib.back_to_setup_toppage()             # Boot_Type-->Boot Sequence 检查PXE设备启动名称显示
        assert SetUpLib.locate_option([Msg.PAGE_BOOT], Key.RIGHT, 10)
        assert SetUpLib.enter_menu(Msg.BOOT_SEQUENCE)
        assert verify_pxe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1661", "[TC1661] Testcase_HelpInfoUefi_002", "【UEFI】光驱设备分类名称显示测试"))
# def Testcase_HelpInfoUefi_002():
#     """
#     Name:       【UEFI】光驱设备分类名称显示测试
#     Condition:  1、UEFI模式。
#     Steps:      1、启动进入BootManager页面，检查光驱设备启动项分类名称显示，有结果A；
#                 2、按键Esc退出，进入到Setup页面，查看Boot Sequence，观察光驱启动项分类的名称显示是否正确，有结果A。
#     Result:     A：启动项分类的名称及帮助信息显示使用DVD-ROM替代CD/DVD-ROM的显示。
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


# @core.test_case(("1662", "[TC1662] Testcase_HelpInfoLegacy_001", "【Legacy】PXE启动设备名称显示测试"))
# def Testcase_HelpInfoLegacy_001():
#     """
#     Name:       【Legacy】PXE启动设备名称显示测试
#     Condition:  1、Legacy模式。
#     Steps:      1、启动进入BootManager页面，检查PXE设备启动名称显示，有结果A；
#                 2、按键Esc退出，进入到Setup页面，查看PXE Configuration、Boot Sequence以及启动项分类选项，观察PXE设备名称显示是否正确，有结果A。
#     Result:     A：启动项分类名称、启动设备名称及帮助信息显示为PXE，没有BEV字样出现。
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


# @core.test_case(("1663", "[TC1663] Testcase_HelpInfoLegacy_002", "【Legacy】光驱设备分类名称显示测试"))
# def Testcase_HelpInfoLegacy_002():
#     """
#     Name:       【Legacy】光驱设备分类名称显示测试
#     Condition:  1、Legacy模式。
#     Steps:      1、启动进入BootManager页面，检查光驱设备启动项分类名称显示，有结果A；
#                 2、按键Esc退出，进入到Setup页面，查看Boot Sequence，观察光驱启动项分类的名称显示是否正确，有结果A。
#     Result:     A：启动项分类的名称及帮助信息显示使用DVD-ROM替代CD/DVD-ROM的显示。
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


@core.test_case(("1664", "[TC1664] Testcase_SimplePassword_001", "简易密码设置菜单检查"))
def Testcase_SimplePassword_001():
    """
    Name:       简易密码设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进入Setup菜单，检查简易密码开关默认值，有结果A；
                2、修改密码为简易密码（纯数字/字母/符号等），有结果B；
                3、按要求修改密码为复杂密码，有结果C；
                4、通过带外配置设置Simple Password，有结果D。
    Result:     A：Simple Password默认值为Disabled；
                B：修改失败，提示无效密码；
                C：修改成功，提示“Changes have been saved after press "Save and Exit"”；
                D: 带外配置生效，且BMC操作日志有1条修改记录。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=8)              # 纯数字
    pw_b = PwdLib.gen_pw(upper=8)              # 纯大写字母
    pw_c = PwdLib.gen_pw(lower=8)              # 纯小写字母
    pw_d = PwdLib.gen_pw(upper=4, lower=4)     # 纯大小写混合字母
    pw_e = PwdLib.gen_pw(symbol=8)             # 纯符号
    pw_f = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, prefix='Admi')
    pw_list = [pw_a, pw_b, pw_c, pw_d, pw_e]
    set_simple_pw = "Set Authority from [Disabled] to [Enabled] success"
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.SIMPLE_PW, Key.UP, 10) == Msg.DISABLE
        # set 2
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for sim_pw in pw_list:                  # 无效的用户密码
            assert PwdLib.set_admin_password(new_pw=sim_pw, old_pw=PW.ADMIN, result=False, expect=PwdLib.pw_simple, save=False)
        # set 3
        assert PwdLib.set_admin_password(new_pw=pw_f, old_pw=PW.ADMIN, result=True, expect=PwdLib.pw_change_saved, save=False)
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert PwdLib.set_admin_pw_by_unipwd(new_pw=pw_f, old_pw=Msg.BIOS_PASSWORD)
        assert PlatMisc.unipwd_tool(new_pw=pw_f, cmd="check")
        # set 4
        time_now = BmcLib.get_bmc_datetime()
        assert Sut.BMC_RFISH.set_bios_option(**{Attr.SIMPLE_PW: Msg.ENABLE}).result, 'Error: PATCH Fail'
        assert SetUpLib.boot_to_pw_prompt()
        assert PlatMisc.bmc_log_exist(set_simple_pw, time_now, operate=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1665", "[TC1665] Testcase_SimplePassword_002", "简易密码有效性检查"))
def Testcase_SimplePassword_002():
    """
    Name:       简易密码有效性检查
    Condition:  1、简易密码开关使能。
    Steps:      1、启动进入Setup菜单，修改密码为简易密码（纯数字/字母/符号等），长度不在8-16个字符范围内，检查设置情况，有结果A；
                2、修改密码为简易密码（纯数字/字母/符号等），长度在8-16个字符范围内，有结果B。
    Result:     A：修改失败，提示无效密码；
                B：修改成功，提示“Changes have been saved after press "Save and Exit"”。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=10)                 # 合法 纯数字
    pw_b = PwdLib.gen_pw(upper=10)                 # 合法 纯大写字母
    pw_c = PwdLib.gen_pw(lower=10)                 # 合法 纯小写字母
    pw_d = PwdLib.gen_pw(upper=5, lower=5)         # 合法 纯大小写混合字母
    pw_e = PwdLib.gen_pw(symbol=10)                # 合法 纯符号
    pw_a_7 = PwdLib.gen_pw(digit=7)                # 纯数字,小于8位
    pw_a_17 = PwdLib.gen_pw(digit=17)              # 纯数字,大于16位
    pw_b_7 = PwdLib.gen_pw(upper=7)                # 纯大写字母, 小于8位
    pw_b_17 = PwdLib.gen_pw(upper=17)              # 纯大写字母, 大于16位
    pw_c_7 = PwdLib.gen_pw(lower=7)                # 纯小写字母,小于8位
    pw_c_17 = PwdLib.gen_pw(lower=17)              # 纯小写字母,大于16位
    pw_d_7 = PwdLib.gen_pw(upper=4, lower=3)       # 纯大小写混合字母,小于8位
    pw_d_17 = PwdLib.gen_pw(upper=9, lower=8)      # 纯大小写混合字母,大于16位
    pw_e_7 = PwdLib.gen_pw(symbol=7)               # 纯符号,小于8位
    pw_e_17 = PwdLib.gen_pw(symbol=17)             # 纯符号,大于16位
    pw_normal = [pw_a, pw_b, pw_c, pw_d, pw_e]
    invalid_pw_short = [pw_a_7, pw_b_7, pw_c_7, pw_d_7, pw_e_7]
    invalid_pw_long = [pw_a_17, pw_b_17, pw_c_17, pw_d_17, pw_e_17]
    try:
        # Condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm)
        SetUpLib.send_keys([Key.ENTER, Key.SAVE_RESET])
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        # set 1
        for var_invalid in invalid_pw_short:                 # 无效的用户密码: "Password too short"
            assert PwdLib.set_admin_password(new_pw=var_invalid, old_pw=PW.ADMIN, result=False, expect=PwdLib.pw_short,
                                       save=False)
        for var_long in invalid_pw_long:                     # 大于16位的密码, 只有前16位有效
            assert PwdLib.set_admin_password(new_pw=var_long, old_pw=PW.ADMIN, result=True, expect=PwdLib.pw_change_saved,
                                       save=False)
        # set 2
        for var_nor in pw_normal:
            assert PwdLib.set_admin_password(new_pw=var_nor, old_pw=PW.ADMIN, result=True, expect=PwdLib.pw_change_saved,
                                       save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1666", "[TC1666] Testcase_SimplePassword_003", "设置简易密码后关闭简易密码开关"))
def Testcase_SimplePassword_003():
    """
    Name:       设置简易密码后关闭简易密码开关
    Condition:  1、简易密码设置已生效
    Steps:      1、启动进入Setup菜单，关闭简易密码开关，F10保存重启后通过简易密码登录Setup菜单，检查登录情况，有结果A；
                2、Setup菜单修改密码为简易密码（纯数字/字母/符号等），有结果B；
                3、按要求修改密码为复杂密码，有结果C。
    Result:     A：简易密码登录成功；
                B：修改失败，提示无效密码；
                C：修改成功，提示“Changes have been saved after press "Save and Exit"”。
    Remark:
    """
    pw_a = PwdLib.gen_pw(digit=10)              # 纯数字
    pw_b = PwdLib.gen_pw(upper=10)              # 纯大写字母
    pw_c = PwdLib.gen_pw(lower=10)              # 纯小写字母
    pw_d = PwdLib.gen_pw(upper=5, lower=5)      # 纯大小写混合字母
    pw_e = PwdLib.gen_pw(symbol=10)             # 纯符号
    pw_f = PwdLib.gen_pw(digit=1, upper=1, lower=1, symbol=1, prefix='Admin')
    pw_list = [pw_a, pw_b, pw_c, pw_d, pw_e]
    try:
        # Condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm)
        SetUpLib.send_keys([Key.ENTER, Key.SAVE_RESET])
        # set 1
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.DISABLE, save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.get_option_value(Msg.SIMPLE_PW, try_counts=10) == Msg.DISABLE
        # set 2
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for val in pw_list:
            assert PwdLib.set_admin_password(new_pw=val, old_pw=PW.ADMIN, result=False, expect=PwdLib.pw_simple,
                                       save=False)
        # set 3
        assert PwdLib.set_admin_password(new_pw=pw_f, old_pw=PW.ADMIN, result=True, expect=PwdLib.pw_change_saved,
                                   save=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1667", "[TC1667] Testcase_SimplePassword_004", "设置简易密码后保存生效"))
def Testcase_SimplePassword_004():
    """
    Name:       设置简易密码后保存生效
    Condition:  1、简易密码开关使能。
    Steps:      1、启动进入Setup菜单设置简易密码后，F10保存重启按Del重新登录Setup菜单，登录时输入设置简易密码之前的复杂密码，检查登录情况，有结果A；
                2、输入错误的简易密码（空密码、非法长度、其它值），检查登录情况，有结果A；
                3、输入正确的简易密码，检查登录情况，有结果B。
    Result:     A：登录失败，提示密码错误；
                B：登录成功。
    Remark:
    """
    pw_1 = PwdLib.gen_pw(digit=PW.MIN)                         # 设置的简单密码
    pw_a = PwdLib.gen_pw(total=0)                              # 空密码
    pw_b = PwdLib.gen_pw(symbol=2)                             # 小于8位(非法长度)
    pw_c = PwdLib.gen_pw(upper=4, lower=4)                     # 任意其他值
    pw_list = [pw_a, pw_b, pw_c]
    try:
        # Condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm)
        SetUpLib.send_keys([Key.ENTER, Key.SAVE_RESET])
        # set 1
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(new_pw=pw_1, old_pw=PW.ADMIN, result=True, expect=PwdLib.pw_change_saved, save=True)
        assert SetUpLib.continue_to_pw_prompt()
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        # set 2
        assert SetUpLib.boot_to_pw_prompt()
        for i in pw_list:
            SetUpLib.send_data_enter(i)
            assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        # set 3
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(pw_1)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1668", "[TC1668] Testcase_SimplePassword_005", "设置简易密码后不保存退出"))
def Testcase_SimplePassword_005():
    """
    Name:       设置简易密码后不保存退出
    Condition:  1、简易密码开关使能。
    Steps:      1、启动进入Setup菜单设置简易密码后，不保存退出，系统重启按Del重新登录Setup菜单，登录时输入错误的简易密码（空密码、非法长度、其它值），检查登录情况，有结果A；
                2、输入正确的简易密码，检查登录情况，有结果A；
                3、输入设置简易密码之前的复杂密码，检查登录情况，有结果B。
    Result:     A：登录失败，提示密码错误；
                B：登录成功。
    Remark:
    """
    pw_1 = PwdLib.gen_pw(digit=PW.MIN)          # 设置的简单密码
    pw_a = PwdLib.gen_pw(total=0)               # 空密码
    pw_b = PwdLib.gen_pw(symbol=7)              # 小于8位(非法长度)
    pw_c = PwdLib.gen_pw(upper=4, lower=4)      # 任意其他值
    pw_list = [pw_a, pw_b, pw_c, pw_1]
    try:
        # Condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm)
        SetUpLib.send_keys([Key.ENTER, Key.SAVE_RESET])
        # set 1-2
        assert SetUpLib.continue_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        assert PwdLib.set_admin_password(new_pw=pw_1, old_pw=PW.ADMIN, result=False, expect=PwdLib.pw_change_saved,
                                   save=False)
        assert SetUpLib.boot_to_pw_prompt()
        for i in pw_list:
            SetUpLib.send_data_enter(i)
            assert SetUpLib.wait_msg(PwdLib.pw_invalid)
        # set 3
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(PW.ADMIN)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1669", "[TC1669] Testcase_SimplePassword_006", "装备定制简易密码"))
def Testcase_SimplePassword_006():
    """
    Name:       装备定制简易密码
    Condition:  1、已安装装备支持的OS并上传装备工具。
    Steps:      1、启动进OS，使用uniPwd工具定制简单密码，检查设置是否成功，有结果A；
                2、重启系统，通过定制的简易密码登录Setup，检查能否登录成功，有结果B。
    Result:     A：uniPwd工具可以定制简单密码；
                B：简易密码登录成功。
    Remark:     1、./uniPwd -sets  new_pwd  old_pwd
    """
    pw_a = PwdLib.gen_pw(digit=PW.MIN)      # 简单密码
    try:
        # Condition
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm)
        SetUpLib.send_keys([Key.ENTER, Key.SAVE_RESET])
        # set 1
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert PwdLib.set_admin_pw_by_unipwd(new_pw=pw_a, old_pw=Msg.BIOS_PASSWORD)
        assert PlatMisc.unipwd_tool(new_pw=pw_a, cmd="check")
        # set 2
        assert SetUpLib.boot_to_pw_prompt()
        SetUpLib.send_data_enter(pw_a)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1670", "[TC1670] Testcase_SimplePassword_007", "简易密码开关立即生效"))
def Testcase_SimplePassword_007():
    """
    Name:       简易密码开关立即生效
    Condition:
    Steps:      1、启动进入Setup菜单，修改密码为简易密码（纯数字/字母/符号等），长度在8-16个字符范围内，有结果A；
                2、开启简易密码开关，再次修改密码为简易密码（纯数字/字母/符号等），长度在8-16个字符范围内，有结果B；
                3、保存重启后使用设置的简易密码登录Setup菜单，检查登录情况，有结果C。
    Result:     A：修改失败，提示无效密码；
                B：修改成功，提示“Changes have been saved after press "Save and Exit"”；
                C：登录成功。
    Remark:     1、简易密码开关开启后无需保存则可生效
    """
    pw_a = PwdLib.gen_pw(digit=10)                  # 纯数字
    pw_b = PwdLib.gen_pw(upper=10)                  # 纯大写字母
    pw_c = PwdLib.gen_pw(lower=10)                  # 纯小写字母
    pw_d = PwdLib.gen_pw(upper=5, lower=5)          # 纯大小写混合字母
    pw_e = PwdLib.gen_pw(symbol=10)                 # 纯符号
    pw_i = [pw_a, pw_b, pw_c, pw_d, pw_e]
    pw_j = [PW.ADMIN, pw_a, pw_b, pw_c, pw_d, pw_e]
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        for i in pw_i:
            assert PwdLib.set_admin_password(new_pw=i, old_pw=PW.ADMIN, result=False, expect=PwdLib.pw_simple, save=False)
        # set 2 - 3
        assert SetUpLib.set_option_value(Msg.SIMPLE_PW, Msg.ENABLE, save=False)
        assert SetUpLib.wait_msg(PwdLib.pw_simple_confirm)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        n = 0
        for j in pw_j[1:]:
            assert PwdLib.set_admin_password(new_pw=j, old_pw=pw_j[n], result=True, expect=PwdLib.pw_change_saved, save=True)
            n += 1
            assert SetUpLib.boot_to_pw_prompt()
            SetUpLib.send_data_enter(j)
            assert SetUpLib.wait_msg(Msg.HOME_PAGE)
            PwdLib.update_current_pw(pw_admin=j)
            assert SetUpLib.move_to_page(Msg.PAGE_SECURITY)
            assert SetUpLib.locate_option(Msg.SET_ADMIN_PW)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()


@core.test_case(("1674", "[TC1674] Testcase_LogLevel_004", "装备使能Margin Level日志级别测试"))
def Testcase_LogLevel_004():
    """
    Name:       装备使能Margin Level日志级别测试
    Condition:  1、装备脚本已归档OS。
    Steps:      1、启动进OS，执行./uniMem -w EquipmentModeFlag:1 使能标志位
                2、执行下述五条命令使能margin开关以及最大级别打印
                ./uniCfg -w EnableBiosSsaRMTonFCB:1
                ./uniCfg -w RankMargin:0
                ./uniCfg -w EnableBiosSsaRMT:1
                ./uniCfg -w BiosSsaPerBitMargining:1
                ./uniCfg -w BiosSsaDebugMessages:5
                ./uniCfg -w SysDbgLevel:1
                3、reboot使系统复位，检查bios阶段是否做Margin测试，有结果A。
    Result:     A：BIOS串口打印Margin测试过程。
    Remark:     1、串口日志可通过搜索START_BSSA_RMT观察
    """
    sing_flg = Msg.RMT_START
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert Sut.UNITOOL.set_config(BiosCfg.MFG_RMT), '**unitool_seting fail'
        assert BmcLib.force_reset()
        assert SetUpLib.wait_msg(sing_flg, SutConfig.Env.BOOT_RMT), "**Booting in Margin Level test fail"
        logging.info('Margin Level test pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


@core.test_case(("1675", "[TC1675] Testcase_SerialSelect_001", "串口资源选择设置菜单检查"))
def Testcase_SerialSelect_001():
    """
    Name:       串口资源选择设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，检查串口资源选择选项可选值及默认值，有结果A。
    Result:     A：提供串口资源选择开关，2F8、3F8可选，默认3F8。
    Remark:     1、3F8对应tty0(COM1)；
                2、2F8对应tty1(COM2)；
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PERI_CONFIG)
        assert SetUpLib.get_option_value(Msg.BASE_IO_ADDRESS, Key.UP, 10) == Msg.VAL_TTY0
        list_tty = SetUpLib.get_all_values(Msg.BASE_IO_ADDRESS)
        assert Msg.VAL_TTY0 in list_tty and Msg.VAL_TTY1 in list_tty
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1677", "[TC1677] Testcase_SerialSelect_003", "设置串口资源0x3F8输入输出长时间测试"))
def Testcase_SerialSelect_003():
    """
    Name:       设置串口资源0x3F8输入输出长时间测试
    Condition:  1、串口资源选择设置为3F8；
                2、OS配置文件已设置为tty0；
                3、串口已连接。
    Steps:      1、系统反复复位3次，检查串口输入输出是否正常，有结果A。
    Result:     A：串口输入输出正常。
    Remark:     1、3F8对应tty0(COM1)
                2、2F8对应tty1(COM2)
    """
    times = 4
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PERI_CONFIG)
        if SetUpLib.get_option_value(Msg.BASE_IO_ADDRESS) != Msg.VAL_TTY0:
            assert SetUpLib.set_option_value(Msg.BASE_IO_ADDRESS, Msg.VAL_TTY0, save=True)
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_PERI_CONFIG)
            assert SetUpLib.verify_options([Msg.BASE_IO_ADDRESS, Msg.VAL_TTY0])
        else:
            assert SetUpLib.get_option_value(Msg.BASE_IO_ADDRESS, Key.UP, 10) == Msg.VAL_TTY0
            list_tty = SetUpLib.get_all_values(Msg.BASE_IO_ADDRESS)
            assert Msg.VAL_TTY0 in list_tty and Msg.VAL_TTY1 in list_tty
        for i in range(1, times):
            assert BmcLib.force_reset()
            assert SetUpLib.wait_msg(Msg.CPU_RSC_ALLOC, SutConfig.Env.BOOT_DELAY)   # 检查串口输出否正常
            assert SetUpLib.wait_msg(Msg.START_DIMM, SutConfig.Env.BOOT_DELAY)
            logging.info(f"No.{i} run pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1679", "[TC1679] Testcase_SerialSelect_005", "设置串口资源0x2F8输入输出长时间测试"))
def Testcase_SerialSelect_005():
    """
    Name:       设置串口资源0x2F8输入输出长时间测试
    Condition:  1、串口资源选择设置为2F8；
                2、OS配置文件已设置为tty1；
                3、串口已连接。
    Steps:      1、系统反复复位3次，检查串口输入输出是否正常，有结果A。
    Result:     A：串口输入输出正常。
    Remark:     1、3F8对应tty0(COM1)
                2、2F8对应tty1(COM2)
    """
    times = 4
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PERI_CONFIG)
        if SetUpLib.get_option_value(Msg.BASE_IO_ADDRESS) != Msg.VAL_TTY1:
            assert SetUpLib.set_option_value(Msg.BASE_IO_ADDRESS, Msg.VAL_TTY1, save=True)
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_PERI_CONFIG)
            assert SetUpLib.verify_options([Msg.BASE_IO_ADDRESS, Msg.VAL_TTY1])
        else:
            assert SetUpLib.get_option_value(Msg.BASE_IO_ADDRESS, Key.UP, 10) == Msg.VAL_TTY1
        for i in range(1, times):
            assert BmcLib.force_reset()
            assert SetUpLib.wait_msg(Msg.CPU_RSC_ALLOC, SutConfig.Env.BOOT_DELAY)   # 检查串口输出否正常
            assert SetUpLib.wait_msg(Msg.START_DIMM, SutConfig.Env.BOOT_DELAY)
            logging.info(f"No.{i} run pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1680", "[TC1680] Testcase_WatchDog_001", "POST看门狗设置菜单检查"))
def Testcase_WatchDog_001():
    """
    Name:       POST看门狗设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，BMC界面下检查POST看门狗相关选项状态，可选值及默认值，有结果A；
                2、使能POST看门狗开关，检查超时时间、超时动作设置值，有结果B。
    Result:     A：看门狗开关Disabled、Enabled可选，默认Disabled；超时时间默认20min，置灰不可设置；
                超时动作默认Hard Reset，置灰不可设置；
                B：超时时间、超时动作可设置。
    Remark:     1、超时动作四项可选：NoAction、HardReset、PowerDown、PowerCycle
    """
    bmc_post_value = [Msg.DISABLE, Msg.ENABLE]
    bmc_timeout_post_default = '20'
    grey_option = [Msg.BMC_WDT_TIMEOUT_POST, Msg.BMC_WDT_ACTION_POST]
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.get_option_value(Msg.BMC_WDT_POST) == Msg.DISABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BMC_WDT_POST), bmc_post_value)
        assert SetUpLib.check_grey_option(grey_option)                                              # 置灰不可设置验证
        # set 2
        assert SetUpLib.set_option_value(Msg.BMC_WDT_POST, Msg.ENABLE, save=False)
        assert SetUpLib.get_option_value(Msg.BMC_WDT_ACTION_POST) == Msg.VAL_BMC_WDT_ACT[0]
        for act in Msg.VAL_BMC_WDT_ACT:
            assert SetUpLib.set_option_value(Msg.BMC_WDT_ACTION_POST, act, save=False)               # 超时动作可设置
        assert SetUpLib.get_option_value(Msg.BMC_WDT_TIMEOUT_POST, integer=True) == bmc_timeout_post_default
        for i in range(18, 26):                                                                     # help提示范围：18-25
            assert SetUpLib.set_option_value(Msg.BMC_WDT_TIMEOUT_POST, str(i), save=False, integer=True)  # 超时时间可设置
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1681", "[TC1681] Testcase_WatchDog_002", "POST看门狗超时时间合理性检查"))
def Testcase_WatchDog_002():
    """
    Name:       POST看门狗超时时间合理性检查
    Condition:  1、使能POST看门狗；
                2、已确定超时时间范围，假定为[a,b]。
    Steps:      1、启动进Setup菜单，BMC界面下遍历设置POST看门狗超时时间为[a，b]范围内，检查能否设置成功，有结果A；
                2、设置超时时间为[a，b]范围外值，检查能否设置成功，有结果B。
    Result:     A：范围内值设置成功；
                B：范围内值不支持设置；
    Remark:
    """
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.set_option_value(Msg.BMC_WDT_POST, Msg.ENABLE, save=False)
        # set 2
        for i in range(17, 27):                                                                     # help提示范围：18-25
            if i < 18 or i > 25:                                                                    # 超出范围的设置值
                assert not SetUpLib.set_option_value(Msg.BMC_WDT_TIMEOUT_POST, str(i))
            else:                                                                                   # 范围内的设置值
                assert SetUpLib.set_option_value(Msg.BMC_WDT_TIMEOUT_POST, str(i), integer=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1682", "[TC1682] Testcase_WatchDog_003", "OS看门狗设置菜单检查"))
def Testcase_WatchDog_003():
    """
    Name:       OS看门狗设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，BMC界面下检查OS看门狗相关选项状态，可选值及默认值，有结果A；
                2、使能OS看门狗开关，检查超时时间、超时动作设置值，有结果B。
    Result:     A：看门狗开关Disabled、Enabled可选，默认Disabled；超时时间默认5min，置灰不可设置；
                超时动作默认Hard Reset，置灰不可设置；
                B：超时时间、超时动作可设置。
    Remark:     1、超时动作四项可选：NoAction、HardReset、PowerDown、PowerCycle
    """
    bmc_os_value = [Msg.DISABLE, Msg.ENABLE]
    bmc_timeout_os_default = '5'
    grey_option = [Msg.BMC_WDT_ACTION_OS, Msg.BMC_WDT_TIMEOUT_OS]
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.get_option_value(Msg.BMC_WDT_OS) == Msg.DISABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BMC_WDT_OS), bmc_os_value)
        assert SetUpLib.check_grey_option(grey_option)
        # set 2
        assert SetUpLib.set_option_value(Msg.BMC_WDT_OS, Msg.ENABLE)
        assert SetUpLib.get_option_value(Msg.BMC_WDT_ACTION_OS) == Msg.VAL_BMC_WDT_ACT[0]
        for act in Msg.VAL_BMC_WDT_ACT:
            assert SetUpLib.set_option_value(Msg.BMC_WDT_ACTION_OS, act, save=False)               # 超时动作可设置
        assert SetUpLib.get_option_value(Msg.BMC_WDT_TIMEOUT_OS, integer=True) == bmc_timeout_os_default
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1683", "[TC1683] Testcase_WatchDog_004", "OS看门狗超时时间合理性检查"))
def Testcase_WatchDog_004():
    """
    Name:       OS看门狗超时时间合理性检查
    Condition:  1、使能OS看门狗；
                2、已确定超时时间范围，假定为[a,b]。
    Steps:      1、启动进Setup菜单，BMC界面下遍历设置OS看门狗超时时间为[a，b]范围内，检查能否设置成功，有结果A；
                2、设置超时时间为[a，b]范围外值，检查能否设置成功，有结果B。
    Result:     A：范围内值设置成功；
                B：范围内值不支持设置；
    Remark:
    """
    try:
        # Condition
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert SetUpLib.set_option_value(Msg.BMC_WDT_OS, Msg.ENABLE, save=False)
        # set 1-2
        for i in range(1, 10):                                                                    # help提示范围：2-8
            if i < 2 or i > 8:                                                                    # 超出范围的设置值
                assert not SetUpLib.set_option_value(Msg.BMC_WDT_TIMEOUT_OS, str(i))
            else:                                                                                 # 范围内的设置值
                assert SetUpLib.set_option_value(Msg.BMC_WDT_TIMEOUT_OS, str(i), integer=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()



def _bmc_enable(bmc_type):
    try:
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        for bmc_name in bmc_type:
            if SetUpLib.get_option_value(bmc_name) == Msg.DISABLE:
                assert SetUpLib.set_option_value(bmc_name, Msg.ENABLE, save=False)
        return True
    except Exception as e:
        logging.error(e)
        return False


def _bmc_action(bmc_action, act_after):
    try:
        for bmc_hl in bmc_action:  # 置灰的选项被改成可修改状态
            if not SetUpLib.check_grey_option(bmc_hl):
                assert SetUpLib.set_option_value(bmc_hl, act_after, save=False)
        return True
    except Exception as e:
        logging.error(e)
        return False


def _bmc_timeout(bmc_timeout, temp_timeout):
    try:
        for bmc_time in bmc_timeout:
            if not SetUpLib.check_grey_option(bmc_time):
                def_val = SetUpLib.get_option_value(bmc_time, integer=True)  # 修改的超时时间 = 默认时间 + temp_timeout
                assert SetUpLib.set_option_value(bmc_time, str(int(def_val) + int(temp_timeout)), integer=True)
        return True
    except Exception as e:
        logging.error(e)
        return False


def _bmc_verification(bmc_type, bmc_action, bmc_timeout):
    try:
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)  # 重启后验证修改值
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        for bmc_name_verily in bmc_type:
            assert SetUpLib.get_option_value(bmc_name_verily) == bmc_supper_value[1]
        for bmc_action_verily in bmc_action:
            assert SetUpLib.get_option_value(bmc_action_verily) == bmc_act_after
        for bmc_time_verily in bmc_timeout:
            if bmc_time_verily == bmc_timeout[0]:
                assert SetUpLib.get_option_value(bmc_time_verily, integer=True) == "23"
            if bmc_time_verily == bmc_timeout[1]:
                assert SetUpLib.get_option_value(bmc_time_verily, integer=True) == "8"
        return True
    except Exception as e:
        logging.error(e)
        return False


def _bmc_default_verification(bmc_type, bmc_grey):
    try:
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        for bmc_name_def in bmc_type:
            assert SetUpLib.get_option_value(bmc_name_def) == bmc_supper_value[0]
        assert SetUpLib.check_grey_option(bmc_grey)
        return True
    except Exception as e:
        logging.error(e)
        return False

@core.test_case(("1684", "[TC1684] Testcase_WatchDog_005", "F9恢复看门狗默认配置"))
def Testcase_WatchDog_005():
    """
    Name:       F9恢复看门狗默认配置
    Condition:
    Steps:      1、启动进setup菜单，BMC界面下修改POST、OS看门狗开关、超时时间、超时动作为非默认配置，F10保存重启后进入Setup菜单，检查是否生效，有结果A；
                2、F9恢复默认后F10再次进入Setup菜单，检查Post、OS看门狗状态，有结果B。
    Result:     A：Post、OS看门狗设置修改生效。
                B：Post、OS看门狗均处于Disable状态，超时时间、超时动作选项均置灰。
    Remark:
    """
    try:
        # set 1
        BmcLib.force_reset()
        assert _bmc_enable(bmc_wd_type)
        assert _bmc_action(bmc_wd_action, bmc_act_after)
        assert _bmc_timeout(bmc_wd_timeout, "3")
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _bmc_verification(bmc_wd_type, bmc_wd_action, bmc_wd_timeout)
        # set 2
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert _bmc_default_verification(bmc_wd_type, bmc_wd_action+bmc_wd_timeout)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1685", "[TC1685] Testcase_WatchDog_006", "Clearcmos恢复看门狗默认配置"))
def Testcase_WatchDog_006():
    """
    Name:       Clearcmos恢复看门狗默认配置
    Condition:
    Steps:      1、启动进setup菜单，BMC界面下修改POST、OS看门狗开关、超时时间、超时动作为非默认配置，F10保存重启后进入Setup菜单，检查是否生效，有结果A；
                2、BMC命令行执行Clearcmos命令，启动进入Setup菜单，检查Post、OS看门狗状态，有结果B。
    Result:     A：Post、OS看门狗设置修改生效。
                B：Post、OS看门狗均处于Disable状态，超时时间、超时动作选项均置灰。
    Remark:
    """
    try:
        # set 1
        BmcLib.force_reset()
        assert _bmc_enable(bmc_wd_type)
        assert _bmc_action(bmc_wd_action, bmc_act_after)
        assert _bmc_timeout(bmc_wd_timeout, "3")
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _bmc_verification(bmc_wd_type, bmc_wd_action, bmc_wd_timeout)
        # set 2
        BmcLib.clear_cmos()
        BmcLib.force_reset()
        assert _bmc_default_verification(bmc_wd_type, bmc_wd_action+bmc_wd_timeout)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1687", "[TC1687] Testcase_WatchDogUefi_004", "【UEFI】OS看门狗功能测试"))
def Testcase_WatchDogUefi_004():
    """
    Name:       【UEFI】OS看门狗功能测试
    Condition:  1、UEFI模式；
                2、使能OS看门狗；
                3、设置超时时间为a（范围内）；
                4、设置超时动作为b（范围内）；
                5、已安装OS系统。
    Steps:      1、启动进OS，检查是否触发看门狗，有结果A；
                2、BMC Web界面查看是否存在告警，有结果B；
                3、启动进Setup菜单，关闭OS看门狗，F10保存重启进入OS，检查是否触发看门狗，有结果C；
                4、BMC Web界面查看是否存在告警，有结果D；
    Result:     A：a时间后触发看门狗动作b；
                B：BMC Web存在OS看门狗超时动作b的告警；
                C：a时间后不触发看门狗；
                D：BMC Web无看门狗超时动作b的告警；
    Remark:
    """
    bmc_web_log = "Set watchdog timer use to (OS Load), action to (Power Down), " \
                 "timeout to (120) seconds, stop running successfully"
    try:
        # set 1
        BmcLib.force_reset()
        assert _bmc_enable([Msg.BMC_WDT_OS])
        assert _bmc_action([Msg.BMC_WDT_ACTION_OS], Msg.VAL_BMC_WDT_ACT[2])
        assert _bmc_timeout([Msg.BMC_WDT_TIMEOUT_OS], "-3")
        time_now_bef = BmcLib.get_bmc_datetime()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        time.sleep(150)                                                         # 验证 开启OS看门狗
        assert BmcLib.is_power_state("off"), f"OS_Close is fail"
        # set 2                                                                 # Web界面查看存在告警
        assert PlatMisc.bmc_log_exist(bmc_web_log, time_now_bef, operate=True)
        # set 3
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        if SetUpLib.get_option_value(Msg.BMC_WDT_OS) == bmc_supper_value[1]:
            assert SetUpLib.set_option_value(Msg.BMC_WDT_OS, Msg.DISABLE, save=True)
        time_now_aft = BmcLib.get_bmc_datetime()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        time.sleep(150)                                                         # 验证关闭OS看门狗
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        # set 4                                                                 # Web界面查看不存在告警
        assert not PlatMisc.bmc_log_exist(bmc_web_log, time_now_aft, operate=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1691", "[TC1691] Testcase_WatchDogLegacy_004", "【Legacy】OS看门狗功能测试"))
@mark_legacy_test
def Testcase_WatchDogLegacy_004():
    """
    Name:       【Legacy】OS看门狗功能测试
    Condition:  1、Legacy模式；
                2、使能OS看门狗；
                3、设置超时时间为a（范围内）；
                4、设置超时动作为b（范围内）；
                5、已安装OS系统。
    Steps:      1、启动进OS，检查是否触发看门狗，有结果A；
                2、BMC Web界面查看是否存在告警，有结果B；
                3、启动进Setup菜单，关闭OS看门狗，F10保存重启进入OS，检查是否触发看门狗，有结果C；
                4、BMC Web界面查看是否存在告警，有结果D；
    Result:     A：a时间后触发看门狗动作b；
                B：BMC Web存在OS看门狗超时动作b的告警；
                C：a时间后不触发看门狗；
                D：BMC Web无看门狗超时动作b的告警；
    Remark:
    """
    bmc_web_log = "Set watchdog timer use to (OS Load), action to (Power Down), " \
                 "timeout to (120) seconds, stop running successfully"
    try:
        # set 1
        BmcLib.force_reset()
        assert _bmc_enable([Msg.BMC_WDT_OS])
        assert _bmc_action([Msg.BMC_WDT_ACTION_OS], Msg.VAL_BMC_WDT_ACT[2])
        assert _bmc_timeout([Msg.BMC_WDT_TIMEOUT_OS], "-3")
        time_now_bef = BmcLib.get_bmc_datetime()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.boot_to_default_os(reset=False, uefi=False)
        time.sleep(150)                                                         # 验证 开启OS看门狗
        assert BmcLib.is_power_state("off"), f"OS_Close is fail"
        # set 2                                                                 # Web界面查看存在告警
        assert PlatMisc.bmc_log_exist(bmc_web_log, time_now_bef, operate=True)
        # set 3
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        if SetUpLib.get_option_value(Msg.BMC_WDT_OS) == bmc_supper_value[1]:
            assert SetUpLib.set_option_value(Msg.BMC_WDT_OS, Msg.DISABLE, save=True)
        time_now_aft = BmcLib.get_bmc_datetime()
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, SutConfig.Env.BOOT_DELAY)
        time.sleep(150)                                                         # 验证关闭OS看门狗
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, SutConfig.Env.BOOT_DELAY)
        # set 4                                                                 # Web界面查看不存在告警
        assert not PlatMisc.bmc_log_exist(bmc_web_log, time_now_aft, operate=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

