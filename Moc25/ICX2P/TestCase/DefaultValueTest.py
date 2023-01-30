import logging
import time
import os
import csv
from ICX2P.Config import SutConfig
from ICX2P.BaseLib import SetUpLib, PlatMisc, BmcLib
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.Config.SutConfig import SysCfg
from batf.Report import ReportGen
from batf import MiscLib, core, SerialLib
from batf.SutInit import Sut
from ICX2P.TestCase import UpdateBIOS


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
            assert SetUpLib.enter_menu(Key.DOWN, [cpu_menu], 15, "Port 1A")
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
    tc = ('103', '[TC103] Verify Boot Fail Policy Information', 'Verify Boot Fail Policy is Boot Retry')
    result = ReportGen.LogHeaderResult(tc)
    boot_fail_policy_retry = ['<Boot Retry>']
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


# Testcase_NetworkMode_001检查网口模式选项存在Dedicated\Auto\shared-PCIE\Onboard OCP Shared四种模式，默认值为Dedicated
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_networkMode_001():
    tc = ('105', '[TC105] Verify BMC Network Mode Information', 'Verify BMC Network Mode ')
    result = ReportGen.LogHeaderResult(tc)
    path_bmc_cfg = ['BMC LAN Configuration']
    bmc_network_mode_dedicate = ['<Dedicated>']
    bmc_network_mode_value = 'DedicatedAutoShared\-PCIEOnboard OCP Shared'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BMC)
        assert SetUpLib.enter_menu(Key.DOWN, path_bmc_cfg, 20, '<Dedicated>')
        assert SetUpLib.locate_option(Key.DOWN, bmc_network_mode_dedicate, 20)
        logging.info("**Verify BMC Network Mode Address default value is Dedicated**")
        assert SetUpLib.verify_supported_values(bmc_network_mode_value)
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
    tc = ('106', '[TC106] 确认串口重定向默认打开，并且稳定', 'Verify BMC Network Mode ')
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
        result.log_fail()


# Testcase_ThermalPolicy_001
# Precondition: N/A
# OnStart: N/A
# Steps: '1、单板启动，进入Setup菜单，查看BMC设置界面是否存在BMC Thermal Policy选项（风扇调速），有结果A。
# ExceptedResult: A：存在选项，可以设置的模式有：Energy saving mode(节能模式)、Low noise mode(低噪声模式)、
# performance mode(高性能模式)、Custom mode(用户自定义模式)。
# OnCompleted: SetUp
def testcase_thermalPolicy_001():
    tc = ('107', '[TC107] 01 BIOS提供风扇调速策略选项测试', 'BIOS设置风扇调速策略')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BMC)
        assert SetUpLib.locate_option(Key.DOWN, ['BMC Smart Cooling', f"<.+>"], 12)
        assert SetUpLib.verify_supported_values('Energy Saving ModeLow Noise ModeHigh Performance ModeCustom Mode')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Testcase_WOL_001
# Precondition: N/A
# OnStart: N/A
# Steps: '1、上电启动进Setup菜单，查看WOL选项，有结果A。
# ExceptedResult: A：存在Wake on PME菜单选项，且默认Disabled，可配置修改。
# OnCompleted: SetUp
def testcase_wol_001():
    tc = ('108', '[TC108] 01 WOL选项默认值测试', '支持WOL功能设置')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.CPU_CONFIG)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 25, Msg.CDN)
        assert SetUpLib.locate_option(Key.UP, [Msg.WOL, f"<.+>"], 25)
        assert SetUpLib.verify_supported_values("Disabled")
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Testcase_LoadCustomDefaults_001&2&3&7 确认Setup菜单默认无Load Custom Defaults选项
# Author: OuYang
# Precondition:之前跑的case都与load custom default选项无关，且没有产生load custom default选项
# OnStart:
# OnComplete: SetUp
@core.test_case(('109', '[TC109] testcase_load_custom_defaults_001', '确认Setup菜单默认无Load Custom Defaults选项'))
def testcase_load_custom_defaults_001():
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert not SetUpLib.verify_info(Msg.LOAD_CUSTOM_DEFAULT, 8)
        logging.info("**Verify 默认无Load Custom Defaults选项**")
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail


# Testcase_SPD_001  01 内存SPD检测选项默认值测试
# Author: Lupeipei
@core.test_case(('110', '[TC110] 01 内存SPD检测选项默认值测试', '支持SPD可靠性'))
def testcase_spd_001():
    default_value = 'Disabled'
    options_value = ['Disabled', 'Enabled', ]
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


def _load_custom_defaults_verify(boottype):
    boot_retry = ['Boot Fail Policy', '<Boot Retry>']
    boot_cold = ['Boot Fail Policy', '<Cold Boot>']
    boot_val = {'BootFailPolicy': 2}
    try:
        if boottype == 'uefi':
            assert SetUpLib.boot_suse_from_bm()
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
            assert Sut.UNITOOL.set_config(boot_val)
            assert PlatMisc.unitool_command('setCustomDefault', Sut.OS_SSH)
            logging.info("**UEFI模式Load Custom Defaults功能选项设置**")
        elif boottype == 'legacy':
            assert SetUpLib.boot_to_bootmanager()
            assert SetUpLib.enter_menu(Key.DOWN, [SysCfg.LEGACY_OS], 10, Msg.LINUX_GRUB)
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, 300)
            assert Sut.UNITOOL_LEGACY_OS.set_config(boot_val)
            assert PlatMisc.unitool_command('setCustomDefault', Sut.OS_LEGACY_SSH)
            logging.info("**Legacy模式Load Custom Defaults功能选项设置**")
        else:
            logging.error("**Unsupported Boot type **")
            return False
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, boot_cold, 20), "boot_cold list num ={}".format(len(boot_cold))
        assert SetUpLib.set_option_value(boot_retry[0], 'None', save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Key.DOWN, ['Load Custom Defaults'], 10), '** Load Custom default not found' 
        SetUpLib.send_keys(Key.ENTER_SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_info(boot_cold, 20), "boot_cold list num ={}".format(len(boot_cold))
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_info(boot_retry, 20), "boot_retry list num={}".format(len(boot_retry))
        logging.info("**确认清楚CMOS之后，Load Custom Default项显示正常**")
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.verify_info(['Load Custom Defaults'], 8)
        return True
    except Exception as e:
        logging.error(e)
        return False


# Testcase_LoadCustomDefaults_002&3&7 确认Setup菜单默认无Load Custom Defaults选项
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
@core.test_case(('111', '[TC111] testcase_load_custom_defaults_002', 'UEFI模式验证Load Custom Defaults选项功能正常'))
def testcase_load_custom_defaults_002():
    try:
        assert _load_custom_defaults_verify('uefi')
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        logging.info("还原测试环境")
        BmcLib.clear_cmos()


# Testcase_LoadCustomDefaults_002&3&7 确认Setup菜单默认无Load Custom Defaults选项  ## 此case 只能放在scope最后
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
@core.test_case(('112', '[TC112] testcase_load_custom_defaults_003', 'Legacy模式验证Load Custom Defaults选项功能正常'))
def testcase_load_custom_defaults_003():
    try:
        assert _load_custom_defaults_verify('legacy')
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)
        BmcLib.set_boot_mode("Legacy", once=False)


# Testcase_LoadDefault_005  05 Load Defaults选项功能测试
# Author: Lupeipei
@core.test_case(('113', '[TC113] 05 Load Defaults选项功能测试', '支持恢复Setup默认值'))
def testcase_loaddefault_005():
    try:
        default_value = ['Disabled', 'Dynamic Mode', 'Enabled']
        options_value = ['Enabled', 'Static 2X Mode', 'Disabled']
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 20, Msg.SPD_CRC)
        assert SetUpLib.set_option_value(Msg.SPD_CRC, options_value[0], save=False)
        assert SetUpLib.set_option_value(Msg.MEM2X_REFRESH, options_value[1], save=False)
        assert SetUpLib.set_option_value(Msg.ATTEMPT_FAST_BOOT, options_value[2], save=False)
        logging.info("修改SPD CRC Check, Attempt Fast Boot 和 Refresh Options 成功")
        assert SetUpLib.back_to_setup_toppage()
        assert Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [Msg.PAGE_SAVE], 10)
        assert SetUpLib.locate_option(Key.DOWN, ['Load Factory Defaults'], 10)
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


# Testcase_LoadDefault_006 06 F9恢复Setup菜单默认配置测试 和 07 F9恢复BIOS和OS看门狗测
# Author: Lupeipei
# testcase_loaddefault_006 和 testcase_loaddefault_007 合并成一个case
@core.test_case(('114', '[TC114] 06 F9恢复Setup菜单默认配置测试 和 07 F9恢复BIOS和OS看门狗测试', '支持恢复Setup默认值'))
def testcase_loaddefault_006_007():
    try:
        default_value = ['Disabled', 'Dynamic Mode', 'Enabled', '115200']
        options_value = ['Enabled', 'Static 2X Mode', 'Disabled', '9600']
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 20, Msg.SPD_CRC)
        assert SetUpLib.set_option_value(Msg.SPD_CRC, options_value[0], save=False)
        assert SetUpLib.set_option_value(Msg.MEM2X_REFRESH, options_value[1], save=False)
        assert SetUpLib.set_option_value(Msg.ATTEMPT_FAST_BOOT, options_value[2], save=False)
        logging.info("修改SPD CRC Check, Attempt Fast Boot 和 Refresh Options 成功")
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.Console_CONFIG], 20, Msg.Console_REDIR)
        assert SetUpLib.set_option_value(Msg.BAUD_RATE, options_value[3], save=False)
        assert SetUpLib.set_option_value(Msg.SPCR, options_value[2], save=False)
        logging.info("修改Console Redirection, Baud Rate 和 SPCR 成功")
        assert SetUpLib.back_to_setup_toppage()
        assert Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [Msg.PAGE_BMC], 10)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_WDT_CONFIG, 20, 'BMC WDT Support For POST')
        assert SetUpLib.set_option_value("BMC WDT Support For POST", options_value[0], save=False)
        assert SetUpLib.set_option_value("BMC WDT Support For OS", options_value[0], save=False)
        logging.info("修改BMC WDT Support For POST和BMC WDT Support For OS 成功")
        SetUpLib.send_keys([Key.F9, Key.F])
        time.sleep(3)
        assert SetUpLib.get_option_value(['BMC WDT Support For POST', "<.+>"], Key.UP, 10) == default_value[0]
        assert SetUpLib.get_option_value(['BMC WDT Support For OS', "<.+>"], Key.UP, 10) == default_value[0]
        assert SetUpLib.back_to_setup_toppage()
        assert Sut.BIOS_COM.locate_setup_option(Key.LEFT, [Msg.PAGE_ADVANCED], 10)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.Console_CONFIG], 20, Msg.Console_REDIR)
        # assert SetUpLib.get_option_value([Msg.Console_REDIR, "<.+>"], Key.UP, 10) == default_value[0]
        assert SetUpLib.get_option_value([Msg.BAUD_RATE, "<.+>"], Key.UP, 10) == default_value[3]
        assert SetUpLib.get_option_value([Msg.SPCR, "<.+>"], Key.UP, 10) == default_value[2]
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 20, Msg.SPD_CRC)
        assert SetUpLib.get_option_value([Msg.SPD_CRC, "<.+>"], Key.DOWN, 10) == default_value[0]
        assert SetUpLib.get_option_value([Msg.MEM2X_REFRESH, "<.+>"], Key.DOWN, 10) == default_value[1]
        assert SetUpLib.get_option_value([Msg.ATTEMPT_FAST_BOOT, "<.+>"], Key.UP, 10) == default_value[2]
        logging.info("修改的BIOS配置项都恢复默认值")
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)


# Author: Fubaolin
# Testcase_Serial_003, 串口重定向选项功能测试
# Precondition: Legacy模式
# OnStart:
# OnComplete: NA
@core.test_case(('115', '[TC115]Testcase_Serial_003', '串口重定向选项功能测试'))
def testcase_serial_003():
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End, 60, 120)
        assert MiscLib.verify_msgs_in_log([SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End], log_cut)
        logging.info("**Verify_pass,Serial port redirection option feature enabled**")
        # 关闭串口重定向
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.Console_CONFIG], 20, Msg.Console_REDIR)
        assert SetUpLib.set_option_value(Msg.Console_REDIR, 'Disabled', save=True)
        log_cut_2 = SerialLib.cut_log(Sut.BIOS_COM, 'CPU Resource Allocation', Msg.BIOS_BOOT_COMPLETE, 60, 120)
        assert not MiscLib.verify_msgs_in_log([SutConfig.SysCfg.Option_Rom_Start, SutConfig.SysCfg.Option_Rom_End], log_cut_2)
        logging.info("**Verify_pass, Serial port redirection option feature Disabled**")
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
    finally:
        logging.info("还原测试环境")
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)
        BmcLib.set_boot_mode("Legacy", once=False)


# Author: Fubaolin
# Testcase_LoadDefault_012, F9恢复默认值后，CPU资源分配测试
# Precondition: N/A
# OnStart: N/A
# Steps: 1、Setup菜单下按F9恢复默认，F10保存退出；
# 2、查看启动串口日志中CPU资源的分配情况，有结果A。
# A：CPU资源分配正确。
@core.test_case(('116', '[TC116]Testcase_LoadDefault_012', 'F9恢复默认值后CPU资源分配测试'))
def testcase_loaddefault_012():
    cpu_rsc_ls = ['Stk00', 'Stk01', 'Stk02', 'Stk03', 'Stk04', 'Stk05', 'Rsvd', 'Ubox']
    cpu_rsc = ['CPU0']
    i = 0
    error_flag = 0
    try:
        cpu_rsc_file = os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv")
        if not os.path.exists(cpu_rsc_file):
            assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = csv.reader(rsc_file)
            cpu_rsc_list = [row[0] for row in rsc_data]
            for _cpu_rsc_num in cpu_rsc_list:
                if _cpu_rsc_num == '':
                    i += 1
                    cpu_rsc.append(f'CPU{i}')
                    assert SutConfig.SysCfg.CPU_CNT == len(cpu_rsc)
                    logging.info('**Match CPU_num pass')
        for j in cpu_rsc:
            _cpu_rsc_s = [j] + cpu_rsc_ls
            if not set(_cpu_rsc_s).issubset(set(cpu_rsc_list)):
                logging.info('invalid CPU Resource not in cvs')
                error_flag += 1
        assert error_flag == 0
        logging.info('**All date in Table')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail

