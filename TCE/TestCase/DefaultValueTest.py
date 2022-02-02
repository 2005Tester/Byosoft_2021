import logging
import time

from TCE.BaseLib import SetUpLib, PlatMisc, BmcLib
from TCE.Config.PlatConfig import Key, Msg
from TCE.Config.SutConfig import SysCfg
from batf.Report import ReportGen
from batf import core, MiscLib
from batf.SutInit import Sut
from TCE.Config import SutConfig


# Test case ID: TC100-150

##########################################
#        UNCORE Test Cases               #
##########################################

# Testcase_RRQIRQ_001
def rrqirq():
    tc = ('101', '[TC101] Testcase_RRQIRQ_001', 'Setup菜单RRQ和IRQ选项默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_GENERAL, 20, 'Uncore Status')
        logging.info("Find option and verify default value.")
        assert SetUpLib.locate_option(Key.DOWN, ["Local/Remote Threshold", f"<.+>"], 20)
        logging.info("Verify supported values.")
        values = 'DisabledAutoLowMediumHighManual'
        assert SetUpLib.verify_supported_values(values)
        logging.info("Verify default value of RRQ and IRQ when set to manual.")
        assert SetUpLib.set_option_value("Local/Remote Threshold", 'Manual')
        manual_opts = [["IRQ Threshold", "\[7\]"], ["RRQ Threshold", "\[7\]"]]
        assert SetUpLib.verify_options(Key.DOWN, manual_opts, 12)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# 检查默认状态PCIE_Root_Port带宽分配是否正确（不包括插入不同Rise/Slimline/NVME,带宽可变的root port)
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_port_bandwidth_check():
    tc = ('102', '[TC102] Testcase_PCIeInit_001', 'PCIe带宽默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 15, Msg.IIO_CONFIG)
        for cpu in range(SysCfg.CPU_CNT):  # loop cpu
            cpu_menu = f"CPU {cpu + 1} Configuration"
            assert SetUpLib.enter_menu(Key.DOWN, [cpu_menu], 15, "PCIe Completion Timeout")
            for port, bwidth in SysCfg.PCIE_MAP[cpu].items():  # loop root port
                port_menu = f"Port {port.upper()}"
                assert SetUpLib.enter_menu(Key.DOWN, [port_menu], 15, "PCIe Port")
                assert SetUpLib.verify_info([rf"PCIe Port Link Max\s+Max Width {bwidth.lower()}"],
                                            25), f"Socket{cpu}：port {port} = {bwidth} fail"
                logging.info(f"Socket{cpu}：port {port} = {bwidth} pass")
                SetUpLib.send_key(Key.ESC)
            SetUpLib.send_key(Key.ESC)
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        result.log_fail(capture=True)


# Testcase_Boot_Fail_Policy_001, 检查Boot Fail Policy默认为Boot Retry,且选项值为Boot Retry/Cold Boot/None
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_boot_fail_policy_001():
    tc = ('103', '[TC103] Verify Boot Fail Policy Information', 'Verify Boot Fail Policy is Cold Boot')
    result = ReportGen.LogHeaderResult(tc)
    boot_fail_policy_retry = ['<Cold Boot>']
    boot_fail_policy_value = 'Boot RetryCold BootNone'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, boot_fail_policy_retry, 20)
        assert SetUpLib.verify_supported_values(boot_fail_policy_value)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Testcase_Com_Resource_001确认存在串口资源选项Select Base I/O Address且默认值为3F8
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_com_resource_001():
    tc = ('104', '[TC104] Verify COM Information', 'Verify Select Base I/O Address default value is 3F8')
    result = ReportGen.LogHeaderResult(tc)
    path_misc_cfg = ['Miscellaneous Configuration']
    select_base_io = ['<3F8>\s+Select Base I/O Address']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, path_misc_cfg, 20, 'Select Base I/O Address')
        logging.info("**Verify Select Base I/O Address default value is 3F8**")
        assert SetUpLib.verify_info(select_base_io, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Testcase_Serial_001 && Testcase_Serial_002 BIOS串口重定向选项默认打开，串口稳定停留在Setup下不会发送ESC
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_serial_001():
    tc = ('106', '[TC106] 确认串口重定向默认打开，并且稳定', 'Verify iBMC Network Mode ')
    result = ReportGen.LogHeaderResult(tc)
    path_console_redirection = ['Console Redirection Configuration']
    console_redirection_value = ['<Enabled>\s + Console Redirection']
    flow_control = ['<None>\s + Flow Control']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, path_console_redirection, 20, 'Console Redirection')
        logging.info("**Verify Console Redirection default value is Enabled**")
        assert SetUpLib.verify_info(console_redirection_value, 20)
        time.sleep(20)
        assert SetUpLib.verify_info(flow_control, 20)
        logging.info("**Verify Console Redirection is stable**")
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Testcase_ThermalPolicy_001
# Precondition: N/A
# OnStart: N/A
# Steps: '1、单板启动，进入Setup菜单，查看BMC设置界面是否存在iBMC Thermal Policy选项（风扇调速），有结果A。
# ExceptedResult: A：存在选项，可以设置的模式有：Energy saving mode(节能模式)、Low noise mode(低噪声模式)、
# performance mode(高性能模式)、Custom mode(用户自定义模式)。
# OnCompleted: SetUp
def testcase_thermalPolicy_001():
    tc = ('107', '[TC107] 01 BIOS提供风扇调速策略选项测试', 'BIOS设置风扇调速策略')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BMC)
        assert SetUpLib.locate_option(Key.DOWN, ['iBMC Smart Cooling', f"<.+>"], 12)
        assert SetUpLib.verify_supported_values('Energy Saving ModeLow Noise ModeHigh Performance ModeCustom Mode')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Testcase_LoadCustomDefaults_001&2&3&7 确认Setup菜单默认无Load Custom Defaults选项
# Author: OuYang
# Precondition:之前跑的case都与load custom default选项无关，且没有产生load custom default选项
# OnStart:
# OnComplete: SetUp
def testcase_load_custom_defaults_001():
    tc = ('109', '[TC109] 确认Setup菜单默认无Load Custom Defaults选项', 'Verify Load Custom Defaults ')
    result = ReportGen.LogHeaderResult(tc)
    boot_retry = '<Boot Retry>'
    boot_cold = '<Cold Boot>'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert not SetUpLib.verify_info(Msg.LOAD_CUSTOM_DEFAULT, 7)
        logging.info("**Verify 默认无Load Custom Defaults选项**")
        assert SetUpLib.boot_suse_from_bm()
        assert PlatMisc.unitool_command('w BootFailPolicy:1', Sut.OS_SSH)
        assert PlatMisc.unitool_command('setCustomDefault', Sut.OS_SSH)
        logging.info("**使用unitool工具Load Custom Defaults选项，确认load Custom Default和F9功能的BIOS选项正确**")
        assert SetUpLib.load_custom_default()
        assert SetUpLib.continue_to_page(boot_retry)
        assert SetUpLib.locate_option(Key.DOWN, [boot_retry], 20)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, [boot_cold], 20)
        logging.info("**确认清楚CMOS之后，Load Custom Default项显示正常**")
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.verify_info(Msg.LOAD_CUSTOM_DEFAULT, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Testcase_SPD_001  01 内存SPD检测选项默认值测试
# Author: Lupeipei
@core.test_case(('110', '[TC110] 01 内存SPD检测选项默认值测试', '支持SPD可靠性'))
def testcase_spd_001():
    default_value = Msg.DISABLED
    options_value = [Msg.DISABLED, Msg.ENABLED, ]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 20, Msg.SPD_CRC)
        assert SetUpLib.get_option_value([Msg.SPD_CRC, "<.+>"], Key.DOWN, 10) == default_value
        logging.info("SPD CRC Check 默认值是Disabled")
        assert SetUpLib.get_all_values(Msg.SPD_CRC, Key.DOWN, 10) == options_value
        logging.info("SPD CRC Check 选项是：Enabled，Disabled")
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)


# Testcase_LoadDefault_005  05 Load Defaults选项功能测试
# Author: Lupeipei
@core.test_case(('113', '[TC113] 05 Load Defaults选项功能测试', '支持恢复Setup默认值'))
def testcase_loaddefault_005():
    try:
        default_value = [Msg.DISABLED, 'Dynamic Mode', Msg.ENABLED]
        options_value = [Msg.ENABLED, 'Static 2X Mode', Msg.DISABLED]
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 20, Msg.SPD_CRC)
        assert SetUpLib.set_option_value(Msg.SPD_CRC, options_value[0], save=False)
        assert SetUpLib.set_option_value(Msg.MEM2X_REFRESH, options_value[1], save=False)
        assert SetUpLib.set_option_value(Msg.ATTEMPT_FAST_BOOT, options_value[2], save=False)
        logging.info("修改SPD CRC Check, Attempt Fast Boot 和 Refresh Options 成功")
        assert SetUpLib.back_to_setup_toppage()
        assert Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [Msg.PAGE_SAVE], 10)
        assert SetUpLib.locate_option(Key.DOWN, ['Load Defaults'], 10)
        SetUpLib.send_keys([Key.ENTER, Key.Y])
        time.sleep(3)
        assert Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 10)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 20, Msg.SPD_CRC)
        assert SetUpLib.get_option_value([Msg.SPD_CRC, "<.+>"], Key.DOWN, 10) == default_value[0]
        assert SetUpLib.get_option_value([Msg.MEM2X_REFRESH, "<.+>"], Key.DOWN, 10) == default_value[1]
        assert SetUpLib.get_option_value([Msg.ATTEMPT_FAST_BOOT, "<.+>"], Key.UP, 10) == default_value[2]
        logging.info("修改的BIOS配置项都恢复默认值")
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)


# Testcase_LoadCustomDefaults_002&3&7 确认Setup菜单默认无Load Custom Defaults选项
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
@core.test_case(('111', '[TC111] testcase_load_custom_defaults_002', 'UEFI模式验证Load Custom Defaults选项功能正常'))
def load_custom_defaults_verify():
    boot_retry = ['Boot Fail Policy', '<Boot Retry>']
    boot_cold = ['Boot Fail Policy', '<Cold Boot>']
    boot_val = {'BootFailPolicy': 1}
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config(boot_val)
        assert PlatMisc.unitool_command('setCustomDefault', Sut.OS_SSH)
        logging.info("**UEFI模式Load Custom Defaults功能选项设置**")
        assert SetUpLib.boot_to_page(boot_retry[1])
        assert SetUpLib.locate_option(Key.DOWN, boot_retry, 20), "boot_cold list num ={}".format(len(boot_retry))
        assert SetUpLib.set_option_value(boot_retry[0], 'None', save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Key.DOWN, ['Load Custom Defaults'], 20)
        SetUpLib.send_keys(Key.ENTER_SAVE_RESET)
        assert SetUpLib.continue_to_page(boot_retry[1])
        assert SetUpLib.verify_info(boot_retry, 20), "boot_cold list num ={}".format(len(boot_retry))
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_info(boot_cold, 20), "boot_retry list num={}".format(len(boot_cold))
        logging.info("**确认清楚CMOS之后，Load Custom Default项显示正常**")
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.verify_info(['Load Custom Defaults'], 8)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
