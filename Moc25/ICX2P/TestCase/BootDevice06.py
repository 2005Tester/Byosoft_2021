# Author: arthur

import logging
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, PlatMisc, BmcLib
from batf.Report import ReportGen
from batf import MiscLib, SshLib, SutInit, core, SerialLib
from ICX2P.Config import SutConfig
from batf.SutInit import Sut
from ICX2P.TestCase import UpdateBIOS
from batf.Common.LogAnalyzer import LogAnalyzer

# Boot Device Related Test case, test case ID, TC151-199
'''
function module, do not call (only be used below)
'''

restored_cmds = ['ipmcset -d bootdevice -v 0\n', 'ipmcget -d bootdevice\n']
restored_rets = ['successfully', 'No override']


def _boot_device(boot='UEFI Boot', os=Msg.MENU_HDD_BOOT,
                 pxe=SutConfig.SysCfg.PXE_UEFI):
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.verify_info(['DVD-ROM Drive', 'PXE', 'Others'], 7)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.DOWN, [boot, 'HDD Device'], 7, os)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.DOWN, [boot, 'PXE Device'], 7, pxe)
        return True
    except AssertionError:
        return False


# only used to test boot_order 01 08
def _enabled_disable_options(PXE_OPTION='IPv4 PXE'):
    result_list = []
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.verify_info(['DVD-ROM Drive', 'PXE', 'Others'], 7)
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)  # this case should be run before suse os is the first boot opt,
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 600):
            result_list.append('0')
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, ['PCH Configuration', 'PCH SATA Configuration'], 12, 'SATA Controller')
        SetUpLib.send_keys([Key.F6, Key.ESC])
        assert SetUpLib.enter_menu(Key.DOWN, ['PCH sSATA Configuration'], 7, 'sSATA Controller')
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        if not SetUpLib.wait_message(Msg.LINUX_GRUB, 120):
            result_list.append('1')
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, ['PCH Configuration', 'USB Configuration'], 12, 'USB Mouse')
        assert SetUpLib.locate_option(Key.DOWN, ['USB Physical Port1'], 7)
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.locate_option(Key.DOWN, ['USB Physical Port2'], 7)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        if not SetUpLib.wait_message('NBP file downloaded successfully', 120):
            result_list.append('2')
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, [PXE_OPTION], 7)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        if not SetUpLib.wait_message('Shell', 120):
            result_list.append('3')
        logging.debug(result_list)
        # check the result,
        if len(result_list) == 0:
            return True
    except AssertionError:
        return False


# Force dvd boot when PXE set to 1st option in BMC
def _boot_to_dvd(ssh, dvd_option, msg_install_start):
    logging.info("Set PXE as first boot option from BMC.")
    cmds = ['ipmcset -d bootdevice -v 1\n', 'ipmcget -d bootdevice\n']
    rets = ['successfully', 'Force PXE']
    try:
        assert SshLib.interaction(ssh, cmds, rets, timeout=15)
        logging.info("Boot from DVD Boot via boot manager.")
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.enter_menu(Key.DOWN, [dvd_option], 12, msg_install_start)
        return True
    except AssertionError:
        return False


##########################################
#          Boot Device Test Cases        #
##########################################


# Author: arthur
# Testcase Num: Testcase_BootDeviceType_001
# Precondition: 1、UEFI模式；2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
# OnStart: NA
# OnComplete: Setup Boot Page
def boot_device_type_001():
    tc = ('151', '[TC151]UEFI模式启动类型分类测试', '启动类型分类')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _boot_device()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootDeviceType_002
# Precondition: 1、Legacy模式；2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
# OnStart: NA
# OnComplete: Setup Boot Page
def boot_device_type_002():
    tc = ('152', '[TC152]Legacy模式启动类型分类测试', '启动类型分类')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _boot_device('Legacy Boot', SutConfig.SysCfg.LEGACY_OS, SutConfig.SysCfg.PXE_LEGACY)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootOrder_001
# Precondition: 1、BIOS默认值配置；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: SHELL
def boot_order_001():
    tc = ('153', '[TC153]UEFI Setup菜单启动顺序调整测试', '启动类型分类')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _enabled_disable_options()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Testcase Num: Testcase_BootOrder_002 008
# Precondition: 1、BIOS默认值配置/UEFI or Legacy模式；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: DVD
def boot_order_002():
    tc = ('154', '[TC154]02 08【UEFI Legacy模式】启动顺序优先级_Setup菜单和BMC设置', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    n_fail = 0
    try:
        logging.info("** Change boot order: Others->PXE->DVD-ROM Drive->Hard Disk Drive")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.locate_option(Key.DOWN, ['Others'], 7)
        SetUpLib.send_keys([Key.F6 * 3])
        assert SetUpLib.locate_option(Key.DOWN, ['PXE'], 7)
        SetUpLib.send_keys([Key.F6 * 2])
        assert SetUpLib.locate_option(Key.DOWN, ['DVD-ROM Drive'], 7)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        if not SetUpLib.wait_message('Shell', 120):
            logging.info("Boot to others failed.")
            n_fail += 1
        logging.info("** Change boot order: PXE->Others->DVD-ROM Drive->Hard Disk Drive")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.locate_option(Key.DOWN, ['PXE'], 7)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        if not SetUpLib.wait_message('NBP file downloaded successfully', 120):
            logging.info("** Boot to PXE failed")
            n_fail += 1
        logging.info("** Change boot order: DVD-ROM Drive->PXE->Others->Hard Disk Drive")
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.locate_option(Key.DOWN, ['DVD-ROM Drive'], 7)
        SetUpLib.send_keys([Key.F6 * 2, Key.F10, Key.Y])
        if not SetUpLib.wait_message('Install SUSE 15.2', 120):
            logging.info("** Failed to boot to DVD-ROM")
            n_fail += 1
        assert n_fail
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Testcase Num: Testcase_BootOrder_003
# Precondition: 1、UEFI模式；2、Setup菜单启动顺序保持默认设置。
# OnStart: NA
# OnComplete: PXE
def boot_order_003():
    tc = ('155', '[TC155]03 【UEFI模式】启动顺序优先级_Setup菜单和BMC设置', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    cmds = ['ipmcset -d bootdevice -v 1\n', 'ipmcget -d bootdevice\n']
    rets = ['successfully', 'Force PXE']
    try:
        assert SshLib.interaction(SutInit.Sut.BMC_SSH, cmds, rets, timeout=15)
        assert BmcLib.force_reset()
        assert SetUpLib.wait_message('NBP file downloaded successfully')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        SshLib.interaction(SutInit.Sut.BMC_SSH, restored_cmds, restored_rets, timeout=15)


# Testcase Num: Testcase_BootOrder_004
# Precondition: 1、BIOS默认值配置；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: DVD
def boot_order_004():
    tc = ('156', '[TC156]04【UEFI模式】启动顺序优先级_Setup菜单和BMC设置', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    if not PlatMisc.dvd_verify():
        result.log_skip()
        return
    try:
        assert _boot_to_dvd(SutInit.Sut.BMC_SSH, "Virtual DVD-ROM VM", Msg.LINUX_GRUB)
        result.log_pass()
        SshLib.interaction(SutInit.Sut.BMC_SSH, restored_cmds, restored_rets, timeout=15)
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootOrder_005 011
# Precondition: 1、UEFI or Legacy模式；2、Setup菜单启动顺序保持默认设置。
# OnStart: NA
# OnComplete: PXE
def boot_order_005():
    tc = ('157', '[TC157]05 11【UEFI Legacy模式】启动顺序优先级_Setup菜单和BMC设置', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    cmds = ['ipmcset -d bootdevice -v 5\n', 'ipmcget -d bootdevice\n']
    rets = ['successfully', 'Force boot from default CD/DVD']
    try:
        assert SshLib.interaction(SutInit.Sut.BMC_SSH, cmds, rets, timeout=15)
        assert SetUpLib.boot_with_hotkey(Key.F12, 'NBP file downloaded successfully', 120)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        SshLib.interaction(SutInit.Sut.BMC_SSH, restored_cmds, restored_rets, timeout=15)


# Testcase Num: Testcase_BootOrder_007
# Precondition: 1、BIOS Legacy模式；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: SHELL
def boot_order_007():
    tc = ('158', '[TC158]07 【Legacy模式】默认启动顺序测试', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _enabled_disable_options(PXE_OPTION='PXE Boot to LAN')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Testcase Num: Testcase_BootOrder_010
# Precondition: 1、Legacy；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: DVD
def boot_order_010():
    tc = ('159', '[TC159]10 [Legacy模式] 启动顺序优先级_BMC设置和F11热键', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    if not PlatMisc.dvd_verify():
        result.log_skip()
        return
    try:
        assert _boot_to_dvd(SutInit.Sut.BMC_SSH, r"Virtual DVD-ROM VM 1\.1\.0", "Initializing gfx code")
        result.log_pass()
        SshLib.interaction(SutInit.Sut.BMC_SSH, restored_cmds, restored_rets, timeout=20)
        return True
    except AssertionError:
        result.log_fail(capture=True)


# 09 支持SP启动
# Testcase Num: Testcase_SP_Boot_001
# Precondition: 'SP开关为初始状态
# OnStart: NA
# OnComplete: SP
def sp_boot_001():
    tc = ('160', '[TC160]01 SP开关默认状态测试', '支持SP启动')
    result = ReportGen.LogHeaderResult(tc)
    try:
        # assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_options(Key.DOWN, [['SP Boot', '<Enabled>']], 12)
        SetUpLib.send_keys([Key.F6, Key.F9, Key.Y])
        assert SetUpLib.verify_options(Key.DOWN, [['SP Boot', '<Enabled>']], 20)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_SP_Boot_002
# Precondition: 'SP已部署；
# OnStart: NA
# OnComplete: SP
def sp_boot_002():
    tc = ('161', '[TC161]02 SP开关功能测试', '支持SP启动')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_options(Key.DOWN, [['SP Boot', '<Enabled>']], 12)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        assert SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.LINUX_GRUB, 60)  # check can not boot to SP
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_options(Key.DOWN, [['SP Boot', '<Disabled>']], 12)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        if SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.LINUX_GRUB, 60):
            raise AssertionError
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


#testcase_httpsboot_001()
@core.test_case(('162', '[TC162]01 新增HTTPS Boot使能设置项', '支持Https Boot'))
def testcase_httpboot_001():
    options_value = ["Disabled", "HTTPS:IPv4", "HTTPS:IPv6", "HTTPS:IPv4/IPv6"]
    default_value = "HTTPS:IPv4"
    try:
        assert SetUpLib.boot_to_page('Boot Options')
        assert SetUpLib.get_option_value(["HTTPS Boot Capability", "<.+>"], Key.UP, 10) == default_value
        assert SetUpLib.get_all_values('HTTPS Boot Capability', Key.UP, 15) == options_value
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)


#testcase_httpsboot_002
# Author: Lupeipei
@core.test_case(('163', '[TC163]02 带外修改HTTPS Boot使能设置项', '支持Https Boot'))
def testcase_httpboot_002():
    try:
        assert BmcLib.force_reset()
        bios_options_value = ["HTTPS:IPv6", "HTTPS:IPv4/IPv6", "Disabled"]
        unitool_options_value = [{'NetworkHttpsProtocol': 1}, {'NetworkHttpsProtocol': 2}, {'NetworkHttpsProtocol': 4}]
        for i in range(3):
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
            assert Sut.UNITOOL.set_config(unitool_options_value[i])
            assert SetUpLib.boot_to_page('Boot Options')
            assert SetUpLib.get_option_value(["HTTPS Boot Capability", "<.+>"], Key.UP, 10) == bios_options_value[i]
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
    finally:
        BmcLib.clear_cmos()


# Testcase_PxeCfg_001 PXE开关菜单默认值测试
# Author: Lupeipei
# 遍历UEFI、Legacy模式: 1、进入Setup菜单Boot页面，查看PXE开关可设置及默认值，有结果A
# A：存在PXE总开关，默认打开；UEFI模式存在PXE Boot Capability配置选项，可选Disabled、UEFI:IPv4、UEFI:IPv6、UEFI:IPv4/IPv6，默认UEFI:IPv4；UEFI模式存IPv4单独配置选项，默认打开；
# Legacy模式不存在PXE Boot Capability、IPv4/IPv6配置选项。
@core.test_case(("164", "[TC164] 01 PXE开关菜单默认值测试", "支持PXE开关控制"))
def testcase_pxecfg_001():
    options_value = ["Disabled", "UEFI:IPv4", "UEFI:IPv6", "UEFI:IPv4/IPv6"]
    default_value = "UEFI:IPv4"
    try:
        assert SetUpLib.boot_to_page('Boot Options')
        assert SetUpLib.get_option_value([Msg.PXE_BOOT_CAPABILITY, "<.+>"], Key.UP, 10) == default_value
        assert SetUpLib.get_all_values(Msg.PXE_BOOT_CAPABILITY, Key.UP, 15) == options_value
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, "Legacy Boot", save=True)
        assert SetUpLib.continue_to_bios_config()
        assert Sut.BIOS_COM.locate_setup_option(Key.LEFT, ['Boot Options'], 10)
        assert SetUpLib.verify_info([Msg.PXE_BOOT_CAPABILITY], 10) is None
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)


# Testcase_PxeCfg_002 02 PXE总开关功能测试
# Author: Lupeipei
# 遍历UEFI、Legacy模式：1、进入Setup菜单Boot页面，关闭PXE总开关，有结果A；2、保存重启后，进入Boot Manager查看是否有PXE启动项，有结果B。
# A：PXE总开关关闭后，UEFI模式PXE Boot Capability、IPv4、IPv6菜单无法配置配置；B：无PXE启动项。
@core.test_case(("165", "[TC165] 02 PXE总开关功能测试", "支持PXE开关控制"))
def testcase_pxecfg_002():
    try:
        assert SetUpLib.boot_to_page('Boot Options')
        assert SetUpLib.set_option_value(Msg.PXE_BOOT_CAPABILITY, 'Disabled', save=True)
        assert SetUpLib.continue_to_bootmanager()
        assert SerialLib.is_msg_not_present(Sut.BIOS_COM, 'UEFI PXEv4', 'UEFI HTTPSv4')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)

@core.test_case(("166", "[TC166] 02 PXE总开关功能测试", "支持PXE开关控制"))
def legacy_testcase_pxecfg_002():
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SerialLib.is_msg_not_present(Sut.BIOS_COM, 'PXEv4', SutConfig.SysCfg.PXE_LEGACY)
        #
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)


# Testcase_BootModeSet_001 '01 BMC、BIOS同时设置启动模式测试 支持BMC界面配置启动类型
# Author: Lupeipei
# 1、BIOS停留在Setup菜单界面下，此时BMC下设置启动模式为UEFI，BIOS Setup设置启动模式为Legacy，F10保存重启；
# 2、进入Setup菜单，查看BIOS启动模式，登录BMC Web查看启动模式，有结果A；
# 3、BIOS Setup设置启动模式为UEFI，保存退出；
# 4、进入Setup菜单，查看BIOS启动模式，登录BMC Web查看启动模式，有结果B。
# A：启动模式为Legacy；B：启动模式为UEFI。
@core.test_case(("167", "[TC167]01 BMC、BIOS同时设置启动模式测试", "支持BMC界面配置启动类型"))
def testcase_bootmodeset_001():
    try:
        assert SetUpLib.boot_to_page(Msg.BOOT_OPTIONS)
        assert BmcLib.is_uefi_boot()
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, "Legacy Boot", save=True)
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert BmcLib.is_uefi_boot() is None
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'Legacy Boot'
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, "UEFI Boot", save=True)
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert BmcLib.is_uefi_boot()
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'UEFI Boot'
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)


# Testcase_BootModeSet_002 '02 BMC设置启动模式测试 支持BMC界面配置启动类型
# Author: Lupeipei
# 1、BMC设置BIOS启动模式为UEFI模式；
# 2、单板复位3次，观察是否UEFI模式启动，有结果A；
# 3、BMC设置BIOS启动模式为Legacy模式；
# 4、单板复位3次，观察是否Legacy模式启动，结果B
# A：启动模式为UEFI；B：启动模式为Legacy。
@core.test_case(("168", "[TC168]02 BMC设置启动模式测试", "支持BMC界面配置启动类型"))
def testcase_bootmodeset_002():
    try:
        assert BmcLib.is_uefi_boot()
        assert SetUpLib.boot_to_page(Msg.BOOT_OPTIONS)
        for i in range(3):
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)
            assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'UEFI Boot'
        assert BmcLib.set_boot_mode("Legacy", once=True)
        for i in range(3):
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)
            assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'Legacy Boot'
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)


#Testcase_BootModeSet_003 03 BMC Web设置BIOS启动模式_Forced System Reset 支持BMC界面配置启动类型
# Author: Lupeipei
# 1、BMC Web设置启动模式为Legacy模式，保存；
# 2、KVM执行强制复位系统（Forced System Reset），检查BIOS启动阶段的启动模式，有结果A；
# 3、BMC Web设置启动模式为UEFI模式，保存；
# 4、KVM执行强制复位系统（Forced System Reset），检查BIOS启动阶段的启动模式，有结果B。
# A：正确切换Legacy启动模式；B：正确切换UEFI启动模式。
@core.test_case(("169", "[TC169]03 BMC Web设置BIOS启动模式_Forced System Reset", "支持BMC界面配置启动类型"))
def testcase_bootmodeset_003():
    try:
        assert BmcLib.set_boot_mode("Legacy", once=True)
        assert BmcLib.force_reset()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'Legacy Boot'
        assert BmcLib.set_boot_mode("UEFI", once=True)
        assert BmcLib.force_reset()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'UEFI Boot'
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)


# Testcase_BootModeSet_004 '04 BMC Web设置BIOS启动模式_Forced Power Cycle 支持BMC界面配置启动类型
# Author: Lupeipei
# 1、BMC Web设置启动模式为Legacy模式，保存；
# 2、KVM强制Power Cycle系统，检查BIOS启动阶段的启动模式，有结果A。
# 3、BMC Web系统启动项菜单下，设置启动模式为"UEFI模式"，保存；
# 4、KVM强制Power Cycle系统，检查BIOS启动阶段的启动模式，有结果B。
# A：正确切换Legacy启动模式；B：正确切换UEFI启动模式。
@core.test_case(("170", "[TC170]04 BMC Web设置BIOS启动模式_Forced Power Cycle", "支持BMC界面配置启动类型"))
def testcase_bootmodeset_004():
    try:
        assert BmcLib.set_boot_mode("Legacy", once=True)
        assert BmcLib.force_power_cycle()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'Legacy Boot'
        assert BmcLib.set_boot_mode("UEFI", once=True)
        assert BmcLib.force_power_cycle()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'UEFI Boot'
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)


# Testcase_BootModeSet_005 05 BMC Web设置BIOS启动模式_Power On Cycle 支持BMC界面配置启动类型
# Author: Lupeipei
# 1、BMC Web设置启动模式为Legacy模式，保存；
# 2、KVM强制Power Off/Power On系统，检查BIOS启动阶段的启动模式，有结果A；
# 3、BMC Web设置启动模式为UEFI模式，保存；
# 4、强制Power Off/Power On系统，检查BIOS启动阶段的启动模式，有结果B。
# A：正确切换Legacy启动模式；B：正确切换UEFI启动模式。
@core.test_case(("171", "[TC171]05 BMC Web设置BIOS启动模式_Power On", "支持BMC界面配置启动类型"))
def testcase_bootmodeset_005():
    try:
        assert BmcLib.set_boot_mode("Legacy", once=True)
        assert BmcLib.power_off()
        assert BmcLib.power_on()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'Legacy Boot'
        assert BmcLib.set_boot_mode("UEFI", once=True)
        assert BmcLib.power_off()
        assert BmcLib.power_on()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'UEFI Boot'
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)


# Testcase_BootModeSet_006 06 BMC设置启动模式后通过Setup菜单恢复 支持BMC界面配置启动类型
# Author: Lupeipei
# 1、BMC Web设置启动模式为Legacy模式，重启X86，进入BIOS Setup菜单查看BIOS启动模式，有结果A；
# 2、BIOS Setup设置启动模式为UEFI，保存退出；
# 3、重新进入Setup菜单，查看BIOS启动模式，登录BMC web查看启动模式，有结果B。
# A：正确切换Legacy启动模式；B：正确切换UEFI启动模式。
@core.test_case(("172", "[TC172]06 BMC设置启动模式后通过Setup菜单恢复", "支持BMC界面配置启动类型"))
def testcase_bootmodeset_006():
    try:
        assert BmcLib.set_boot_mode("Legacy", once=True)
        assert BmcLib.force_reset()
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'Legacy Boot'
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, "UEFI Boot", save=True)
        assert SetUpLib.continue_to_page(Msg.BOOT_OPTIONS)
        assert SetUpLib.get_option_value([Msg.BOOT_TYPE, "<.+>"], Key.UP, 10) == 'UEFI Boot'
        assert BmcLib.is_uefi_boot()
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)

# Testcase_SP_Boot_011 SP安全启动测试
# Author: ouyang
# 前提：1、SP已部署；
# 2、SP开关已打开；
# 3、BIOS UEFI模式
# 4、安全启动已打开。
# 预期结果：'1、进入OS（如Redhat7.3），通过"grep 'Root CA' /proc/keys"指令，查看已加载的安全证书；
# 2、通过指令系统启动时按F6正常从SP启动。
@core.test_case(("173", "[TC173] SP安全启动测试", "证书正常加载，SP boot正常"))
def testcase_sp_boot_011():
    P = LogAnalyzer(SutConfig.Env.LOG_DIR)
    expted_log = 'ICX2P\\Tools\\SafetyCertificate\\Keys.txt'.format()
    keys_secure_boot = [Key.RIGHT, Key.DOWN, Key.ENTER]
    try:
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys(keys_secure_boot)
        assert SetUpLib.enter_menu(Key.DOWN, ["Secure Boot Factory Options"], 20, 'Secure Boot Factory Options')
        assert SetUpLib.locate_option(Key.DOWN, ["Restore Secure Boot to Factory Settings"], 4)
        SetUpLib.send_keys(Key.ENTER_SAVE_RESET)
        assert SetUpLib.continue_to_bootmanager()
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.UBUNTU], 10, Msg.BIOS_BOOT_COMPLETE)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 50)
        SshLib.execute_command(Sut.OS_SSH, r'cat /proc/keys | grep -i "Root CA" | cut -c 9- > key.log')
        assert P.dump_and_verify(Sut.OS_SSH, "cat key.log".format(), expted_log)
        logging.info("还原Secure Boot默认值")
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys(keys_secure_boot)
        assert SetUpLib.enter_menu(Key.DOWN, ["Secure Boot Factory Options"], 20, 'Secure Boot Factory Options')
        assert SetUpLib.locate_option(Key.DOWN, ["Erase all Secure Boot Settings"], 4)
        SetUpLib.send_keys(Key.ENTER_SAVE_RESET)
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail

# Testcase_SP_Boot_017  密码为空时，SP启动登录密码测试
# Author: ouyang
# 前提：'1、'1、SP开关打开；
# 2、系统密码为空。
# 预期结果：'1、系统启动时，按F6选择从SP启动，未弹出登录框。
@core.test_case(("174", "[TC174] 密码为空时，SP启动登录密码测试", "SP登录情况正常"))
def testcase_sp_boot_017():
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        assert SetUpLib.set_option_value(["Delete Password Support"], "Enabled")
        if SetUpLib.wait_message('Deleting passwords', 20):
            SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Key.UP, ["Delete Supervisor Password"], 20)
        SetUpLib.send_key(Key.ENTER*2)
        assert (SetUpLib.wait_message('Please type in your password'))
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        SetUpLib.send_key(Key.ENTER)
        logging.info("Delete Password")
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_message(Msg.HOTKEY_PROMPT_F6)
        SetUpLib.send_key(Key.F6)
        logging.info("SP Boot")
        assert SetUpLib.wait_message(Msg.BIOS_BOOT_COMPLETE)
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        logging.info("Restore Password Admin@9009")
        BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert PlatMisc.unipwd_tool("set", 'Admin@9009'), 'unitool_set failed'


# Testcase_NVMeSlotInfo_001
# 前提：单板搭配不同硬盘背板接上NVMe盘
# 1、单板启动，进入Setup菜单，查看NVMe盘信息显示（包含厂商、槽位丝印号、序列号），有结果A；
# 2、遍历所有的NVMe插盘组合。
# 预期结果：A：Setup菜单显示NVMe盘信息：厂商信息正确，槽位信息与单板实际的丝印号相符，序列号与NVMe实际一致。
@core.test_case(("175", "[TC175]01 NVMe丝印信息Setup菜单菜单显示", "支持NVMe盘的丝印信息显示"))
def testcase_NVMeSlotInfo_001():
    key_str = 'NVMe Information'
    hdd_str = ["NVMe1+\s+HUAWEI+\s+HWE52P431T6M002N+\s+032WEUFSK3001185+\s"]  # confirm with dev before defined,
    fail_cnt = 0
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [key_str], 12, key_str)
        for i in range(0, len(hdd_str)):
            if not SetUpLib.wait_message(hdd_str[i], 6):
                fail_cnt += 1
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail

# Testcase_SecurityBoot_003
# Author: ouyang
# 1、在Administer Secure Boot菜单中，更改Erase all Secure Boot setting为Enable。
# 2、按F10保存退出。
# 3、进入Administer Secure Boot菜单确认擦除功能是否正常，有结果A。
# 4、Administer Secure Boot菜单中，更改Restore all Secure Booting setting为Enable。
# 5、按F10保存退出。
# 6、进入Administer Secure Boot菜单确认所有选项是否都恢复出厂设置，有结果B。
# 预期结果：A：PK/KEK/DB/DBX options选项下签名列表被删除；
# B：PK/KEK/DB/DBX options选项下签名列表加载。
@core.test_case(("176", "[TC176]Secure Boot菜单项测试", "支持Secure Boot"))
def testcase_securityBoot_003():
    keys_secure_boot = [Key.RIGHT, Key.DOWN, Key.ENTER]
    KEK_PATH = ["KEK Options", "Delete KEK"]
    DB_PATH = ["DB Options", "Delete Signature"]
    DBX_PATH = ["DBX Options", "Delete Signature", "Signature List, Entry-1"]
    def secure_mode(type):
        SBFO = "Secure Boot Factory Options"
        PK_PATH = ["Custom Secure Boot Options", "PK Options"]
        try:
            assert SetUpLib.enter_menu(Key.DOWN, [SBFO], 20, SBFO)
            if type == 'Restore':
                assert SetUpLib.locate_option(Key.DOWN, ["Restore Secure Boot to Factory Settings"], 4)
            elif type == 'Erase':
                assert SetUpLib.locate_option(Key.DOWN, ["Erase all Secure Boot Settings"], 4)
            else:
                logging.error("unsupport secure mode")
            SetUpLib.send_keys(Key.ENTER_SAVE_RESET)
            assert SetUpLib.continue_to_setup()
            SetUpLib.send_keys(keys_secure_boot)
            assert SetUpLib.set_option_value(["Secure Boot Mode"], "Custom Mode")
            assert SetUpLib.enter_menu(Key.DOWN, PK_PATH, 20, 'Delete PK')
            return True
        except Exception as e:
            logging.error("change secure boot mode fail{0}".format(e))
            return False
    try:
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys(keys_secure_boot)
        assert secure_mode('Restore')
        assert SetUpLib.verify_info(['Delete Pk'], 4)
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.enter_menu(Key.DOWN, KEK_PATH, 20, 'Delete KEK')
        assert SetUpLib.verify_info(['Microsoft Corporation KEK CA'], 4)
        SetUpLib.send_key(Key.ESC*2)
        assert SetUpLib.enter_menu(Key.DOWN, DB_PATH, 20, 'Delete Signature')
        assert SetUpLib.verify_info(['Huawei Root CA'], 4)
        SetUpLib.send_key(Key.ESC*2)
        assert SetUpLib.enter_menu(Key.DOWN, DBX_PATH, 20, 'Signature List, Entry-1')
        SetUpLib.send_key(Key.ESC*4)
        secure_mode('Erase')
        assert SetUpLib.verify_info(['Enroll PK'], 4)
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.enter_menu(Key.DOWN, KEK_PATH, 20, 'Delete KEK')
        assert not SetUpLib.verify_info(['Microsoft Corporation KEK CA'], 4)
        SetUpLib.send_key(Key.ESC*2)
        assert SetUpLib.enter_menu(Key.DOWN, DB_PATH, 20, 'Delete Signature')
        assert not SetUpLib.verify_info(['Huawei Root CA'], 4)
        SetUpLib.send_key(Key.ESC*2)
        assert not SetUpLib.enter_menu(Key.DOWN, DBX_PATH, 20, 'Signature List, Entry-1')
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
