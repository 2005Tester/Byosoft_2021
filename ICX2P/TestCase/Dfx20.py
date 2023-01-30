import logging
import time

from batf import MiscLib, SshLib, SutInit, core
from batf.Report import ReportGen
from ICX2P.BaseLib import SetUpLib, BmcLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg


# Test case ID: TC071-TC090 - arthur

##########################################
#         DFX Test Cases                 #
##########################################


# common cnd test steps,
def _cnd_test_step(value):
    dev_list = []  # verify the order of dev in OS
    assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), 'failed to Setup'
    assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 20, Msg.CDN), 'failed to navigate to CDN'
    assert SetUpLib.set_option_value(Msg.CDN, value, save=True), 'set value ->failed'
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600), 'failed to ping os'
    res = SshLib.execute_command(SutInit.Sut.OS_SSH, 'dmidecode -t 41')
    if value == "Enabled":
        assert 'Ethernet' in res, 'not found network device - {0}'.format(logging.debug(res))
    else:
        assert 'Ethernet' not in res, 'found network device- {0}'.format(logging.debug(res))
    res1 = SshLib.execute_command(SutInit.Sut.OS_SSH, 'ip addr')
    for i in str(res1).split(':'):
        if len(i) <= 5 and 'eth' in i:
            dev_list.append(i.strip(' '))
    logging.debug(dev_list)
    assert SutConfig.Env.OS_IP in res1 \
           and dev_list.sort() == SutConfig.SysCfg.ETH_OS.sort(), 'check network device order failed'

    return True


# 01 支持网口CDN特性开关, arthur
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: POWER OFF
def cnd_support_test01():
    tc = ('071', '[TC071] Testcase_CDN_Support_001&002', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _cnd_test_step('Disabled')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


def cnd_support_test02():
    tc = ('072', '[TC072] Testcase_CDN_Support_004&005', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _cnd_test_step('Enabled')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


def vgaErr_to_bmc():
    tc = ('073', '[TC073] Testcase_VgaErrReportToBMC_002', '02 VGA正常不上报BMC')
    result = ReportGen.LogHeaderResult(tc)
    assert SetUpLib.boot_to_setup()
    res = BmcLib.bmc_warning_check().message
    if 'VGA' in res:
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def testcase_spcr_001():
    tc = ('074', '[TC074] Testcase_Spcr_001', '01 Setup菜单提供OS串口重定向选项测试')
    result = ReportGen.LogHeaderResult(tc)
    assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), 'failed to Setup'
    assert SetUpLib.enter_menu(Key.DOWN, [Msg.Console_CONFIG], 20, Msg.Console_REDIR), 'failed to navigate to CDN'
    if not SetUpLib.locate_option(Key.UP, [Msg.SPCR, "<Enabled>"], 12):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


# Testcase_ACPI_001
# Precondition: N/A
# OnStart: 'UEFI'模式
# Steps:
# 1、OS下使用acpidump工具导出ACPI表信息acpidump > acpi.out；
# 2、分离各表格数据，会生成多个数据文件，使用命令acpixtract -a acpi.out；
# 3、反汇编FACP表，使用命令iasl -d facp.dat，然后使用cat命令查看FACP表项信息，有结果A。
# Result:
# A：关闭平台时钟：Use Platform Timer为0。
# OnCompleted: OS
@core.test_case(('075', '[TC075] 01 ACPI规范测试_FACP表', '支持ACPI'))
def testcase_ACPI_001():
    try:
        cmds = ["acpidump > acpi.out\n", "acpixtract -a acpi.out\n", "iasl -d facp.dat\n"]
        rets = ["", "", ""]
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert SshLib.interaction(SutInit.Sut.OS_SSH, cmds, rets), f"cmd fail"
        res_facp = SshLib.execute_command(SutInit.Sut.OS_SSH, "cat facp.dsl | grep 'Use Platform Timer'\n")
        assert res_facp, "Pls checkin SshLib.execute_command"
        assert '0' in res_facp, '{}'.format(res_facp)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        SshLib.execute_command(SutInit.Sut.OS_SSH, "rm -rf *.out *.dat *.dsl")


# Testcase_ACPI_002
# Precondition: N/A
# OnStart: 'UEFI'模式
# Steps:
# 1、OS下使用acpidump工具导出ACPI表信息acpidump > acpi.out；
# 2、分离各表格数据，会生成多个数据文件，使用命令acpixtract -a acpi.out；
# 3、反汇编DSDT表，使用命令iasl -d dsdt.dat，然后使用cat命令查看DSDT表项信息，有结果A。
# Result:
# A：DSDT表信息正确，ACPI6.1版本。
# OnCompleted: OS
@core.test_case(('076', '[TC076] 02 ACPI规范测试_DSDT表', '支持ACPI'))
def testcase_ACPI_002():
    try:
        cmds = ["acpidump > acpi.out\n", "acpixtract -a acpi.out\n", "iasl -d dsdt.dat\n"]
        rets = [" ", " ", " "]
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert SshLib.interaction(SutInit.Sut.OS_SSH, cmds, rets)
        res = SshLib.execute_command(SutInit.Sut.OS_SSH, "cat dsdt.dsl | grep 'Disassembly of dsdt.dat'")
        assert '2020' or '2021' in res, '{}'.format(res)   # last acpi ver is 6.4,
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        SshLib.execute_command(SutInit.Sut.OS_SSH, "rm -rf *.out *.dat *.dsl")


# Testcase_DEMT_001
# Precondition: N/A
# OnStart: 'UEFI'模式
# Steps:
# 1、单板正常上电，进入Setup菜单，查看DEMT菜单状态，有结果A。
# Result:
# A：提供DEMT开关，默认Disabled。
# OnCompleted: OS
@core.test_case(('077', '[TC077] 01 DEMT菜单测试', '支持动态节能（DEMT）'))
def testcase_DEMT_001():
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.locate_option(Key.DOWN, ["DEMT", "<Disabled>"], 12), 'check the default setting,'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
