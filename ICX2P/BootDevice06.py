from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib
from Report import ReportGen
from Core import MiscLib
from ICX2P.Config import SutConfig


# Boot Device Related Test case, test case ID, TC151-199
'''
function module, do not call (only be used below)
'''


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
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
