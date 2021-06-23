# Author: arthur

import logging
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, BmcLib, PlatMisc
from Report import ReportGen
from Core import MiscLib, SshLib, SutInit
from ICX2P.Config import SutConfig

# Boot Device Related Test case, test case ID, TC151-199
'''
function module, do not call (only be used below)
'''

restored_cmds = ['ipmcset -d bootdevice -v 0\n', 'ipmcget -d bootdevice\n']
restored_rets = ['successfully', 'No override']


def boot_device(boot='UEFI Boot', os="SUSE Linux Enterprise\(LUN0\) RAID CARD",
                pxe='UEFI HTTPSv4: Intel Network - Port00 SLOT1'):
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
def enabled_disable_options(PXE_OPTION='IPv4 PXE'):
    result_list = []
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.verify_info(['DVD-ROM Drive', 'PXE', 'Others'], 7)
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)  # this case should be run before suse os is the first boot opt,
        if not MiscLib.ping_sut(SutConfig.OS_IP, 600):
            result_list.append('0')
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, ['PCH Configuration', 'PCH SATA Configuration'], 12, 'SATA Controller')
        SetUpLib.send_keys([Key.F6, Key.ESC])
        assert SetUpLib.enter_menu(Key.DOWN, ['PCH sSATA Configuration'], 7, 'sSATA Controller')
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        if not SetUpLib.wait_message(Msg.SUSE_GRUB, 120):
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
def boot_to_dvd(ssh, dvd_option, msg_install_start):
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert boot_device()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootDeviceType_002
# Precondition: 1、Legacy模式；2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
# OnStart: NA
# OnComplete: Setup Boot Page
def boot_device_type_002():
    tc = ('152', '[TC152]Legacy模式启动类型分类测试', '启动类型分类')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert boot_device('Legacy Boot', '\(Bus 33 Dev 00\)PCI RAID Adapter RAID CARD',
                           'IBA XE \(X550\) Slot 3100 v2434 Port 0 SLOT1')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootOrder_001
# Precondition: 1、BIOS默认值配置；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: SHELL
def boot_order_001():
    tc = ('153', '[TC153]UEFI Setup菜单启动顺序调整测试', '启动类型分类')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert enabled_disable_options()
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    if not PlatMisc.dvd_verify():
        result.log_skip()
        return
    try:
        assert boot_to_dvd(SutInit.Sut.BMC_SSH, "Virtual DVD-ROM VM", "Welcome to GRUB")
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert enabled_disable_options(PXE_OPTION='PXE Boot to LAN')
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    if not PlatMisc.dvd_verify():
        result.log_skip()
        return
    try:
        assert boot_to_dvd(SutInit.Sut.BMC_SSH, r"Virtual DVD-ROM VM 1\.1\.0", "Initializing gfx code")
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
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
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_options(Key.DOWN, [['SP Boot', '<Enabled>']], 12)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        assert SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.SUSE_GRUB, 60)  # check can not boot to SP
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_options(Key.DOWN, [['SP Boot', '<Disabled>']], 12)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        if SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.SUSE_GRUB, 60):
            raise AssertionError
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
