import logging
import time
from TCE.Config import SutConfig
from TCE.BaseLib import SetUpLib, PlatMisc, BmcLib
from TCE.Config.PlatConfig import Key, Msg
from TCE.Config.SutConfig import SysCfg
from batf.Report import ReportGen


# Test case ID: TC100-150

##########################################
####        UNCORE Test Cases        #####    
##########################################

# Testcase_RRQIRQ_001
def rrqirq():
    tc = ('101', '[TC101] Testcase_RRQIRQ_001', 'Setup菜单RRQ和IRQ选项默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    msg = 'Uncore Status'
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_GENERAL, 20, msg):
        result.log_fail()
        return

    logging.info("Find option and verify default value.")
    if not SetUpLib.locate_option(Key.DOWN, ["Local/Remote Threshold", "<Auto>"], 20):
        result.log_fail()
        return

    logging.info("Verify supported values.")
    values = 'DisabledAutoLowMediumHighManual'
    if not SetUpLib.verify_supported_values(values):
        result.log_fail()
        return
    logging.info("Verify default value of RRQ and IRQ when set to manual.")
    SetUpLib.send_keys([Key.F5, Key.F5, Key.F5, Key.F5])
    manual_opts = [["IRQ Threshold", "\[7\]"], ["RRQ Threshold", "\[7\]"]]
    if not SetUpLib.verify_options(Key.DOWN, manual_opts, 12):
        result.log_fail()
        return

    result.log_pass()
    return True


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
    boot_fail_policy_retry = ['<Boot Retry>']
    boot_fail_policy_cold = ['<Cold Boot>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert not SetUpLib.verify_info(Msg.LOAD_CUSTOM_DEFAULT, 20)
        logging.info("**Verify 默认无Load Custom Defaults选项**")
        assert SetUpLib.boot_suse_from_bm()
        assert PlatMisc.unitool_command('w BootFailPolicy:1')
        assert PlatMisc.unitool_command('setCustomDefault')
        logging.info("**使用unitool工具Load Custom Defaults选项，确认load Custom Default和F9功能的BIOS选项正确**")
        assert SetUpLib.load_custom_default()
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, boot_fail_policy_retry, 20)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, boot_fail_policy_cold, 20)
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