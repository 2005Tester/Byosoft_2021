from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, BmcLib
from Report import ReportGen
from Core import MiscLib, SshLib
from ICX2P.Config import SutConfig


# Boot Device Related Test case, test case ID, TC151-199
'''
function module, do not call (only be used below)
'''

restored_cmds = ['ipmcset -d bootdevice -v 0\n', 'ipmcget -d bootdevice\n']
restored_rets = ['successfully', 'No override']


def boot_device(boot='UEFI Boot', os="SUSE Linux Enterprise\(LUN0\) RAID CARD", pxe='UEFI HTTPSv4: Intel Network - Port00 SLOT1'):
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
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert boot_device('Legacy Boot', '\(Bus 33 Dev 00\)PCI RAID Adapter RAID CARD', 'IBA XE \(X550\) Slot 3100 v2434 Port 0 SLOT1')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootOrder_001
# Precondition: 1、BIOS默认值配置；2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
# OnStart: NA
# OnComplete: SUSE OS
def boot_order_001():
    tc = ('153', '[TC153]UEFI Setup菜单启动顺序调整测试', '启动类型分类')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['Boot Type Order'], 12, 'Hard Disk Drive')
        assert SetUpLib.verify_info(['DVD-ROM Drive', 'PXE', 'Others'], 7)
        assert SetUpLib.boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Testcase Num: Testcase_BootOrder_003
# Precondition: 1、UEFI模式；2、Setup菜单启动顺序保持默认设置。
# OnStart: NA
# OnComplete: PXE
def boot_order_003(ssh):
    tc = ('154', '[TC154]03【UEFI模式】启动顺序优先级_Setup菜单和BMC设置', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    cmds = ['ipmcget -d bootdevice\n', 'ipmcset -d bootdevice -v 1\n', 'ipmcget -d bootdevice\n']
    rets = ['No override', 'successfully', 'Force PXE']
    try:
        assert SshLib.interaction(ssh, cmds, rets, timeout=15)
        assert BmcLib.force_reset()
        assert SetUpLib.wait_message('NBP file downloaded successfully')
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        assert SshLib.interaction(ssh, restored_cmds, restored_rets, timeout=15)


# Testcase Num: Testcase_BootOrder_004
# Precondition: 1、UEFI模式；2、Setup菜单启动顺序保持默认设置。
# OnStart: NA
# OnComplete: PXE
def boot_order_004(ssh):
    tc = ('155', '[TC155]05【UEFI模式】启动顺序优先级_Setup菜单和BMC设置', '支持启动顺序设置')
    result = ReportGen.LogHeaderResult(tc)
    cmds = ['ipmcget -d bootdevice\n', 'ipmcset -d bootdevice -v 5\n', 'ipmcget -d bootdevice\n']
    rets = ['No override', 'successfully', 'Force boot from default CD/DVD']
    try:
        assert SshLib.interaction(ssh, cmds, rets, timeout=15)
        assert SetUpLib.boot_with_hotkey(Key.F12, 'NBP file downloaded successfully', 120)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        assert SshLib.interaction(ssh, restored_cmds, restored_rets, timeout=15)
