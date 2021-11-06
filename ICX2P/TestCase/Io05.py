# this script just for hotkey related function test
import logging, time
import os
import re

from batf.Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, BmcLib

from batf import SerialLib, MiscLib, core
from batf.SutInit import Sut

# Test case ID: TC800-850

'''
function module, do not call, only used below,
'''


def check_info():
    FW_VER = BmcLib.firmware_version_check()
    check_list = [Msg.RC_VERSION, Msg.BIOS_REVISION, Msg.BIOS_DATE, FW_VER.BMC, SutConfig.Env.BMC_IP, Msg.CPU_TYPE,
                  Msg.TOTAL_MEMORY, Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F11,
                  Msg.HOTKEY_PROMPT_F12]
    capture_start = "STOP_DIMMINFO_SYSTEM_TABLE"
    capture_end = "Press F6 go to SP boot"
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, 120, 150)
        assert MiscLib.verify_msgs_in_log(check_list, log_cut)
        return True
    except AssertionError:
        return False


def hotkey_press():
    flag_sendkey = Msg.HOTKEY_PROMPT_DEL
    failures = 0
    del_pressed = 'Del is pressed. Go to Setup Utility'
    f11_pressed = 'F11 is pressed. Go to BootManager'
    f12_pressed = 'F12 is pressed. Go to PXE boot'
    f6_pressed = 'F6 is pressed. Go to SP boot'

    key_msg = [
        (Key.DEL, del_pressed),
        (Key.F11, f11_pressed),
        (Key.F12, f12_pressed),
        (Key.F6, f6_pressed)
    ]

    for check_item in key_msg:
        logging.info('**Testing: {0}'.format(check_item[1]))
        try:
            BmcLib.force_reset()
            assert SetUpLib.wait_message(flag_sendkey, 180)
            SetUpLib.send_key(check_item[0])
            assert SetUpLib.wait_message(check_item[1])
            logging.info('**Test pass.')
        except AssertionError:
            failures += 1
            logging.info('**Test fail.')

    if failures == 0:
        return True
    else:
        logging.info("{0} test failed".format(failures))
        return False


def log_Time(log_n):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600) #考虑全打印
        logging.info("Suse_OS Boot Successful")
        SERIAL_LOG = os.path.join(SutConfig.Env.LOG_DIR, 'TC{}.log'.format(log_n))
        res = [x.strip() for x in open(SERIAL_LOG , 'r').readlines() if x.strip() != '']
        s_cont = 0
        for s_str in SutConfig.Env.LogTime_Dedicated + Msg.LogTime_common:
            logging.info('check ： {}'.format(s_str))
            if not s_str in str(res):
                if not re.search(r"\d+",s_str):
                    s_cont = s_cont + 1
                    logging.info('**{} -- no found**'.format(s_str))
                    return False
        if s_cont == 0:
            logging.info('All check pass')
            return True
    except AssertionError as e:
        logging.error(e)
        return False


##########################################
#            Release Test Cases          #
##########################################


# 01 【UEFI模式】POST启动第一屏显示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: OS (BIOS boot completed)
def system_info_001():
    tc = ('800', '[TC800] Testcase_SystemInfo_001', '01 【UEFI模式】POST启动第一屏显示信息测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert check_info()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 02 【Legacy模式】POST启动第一屏显示信息测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: OS (BIOS boot completed)
def system_info_002():
    tc = ('801', '[TC801] Testcase_SystemInfo_002', '02 【Legacy模式】POST启动第一屏显示信息测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert check_info()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 03 按热键后屏幕底部显示提示信息测试 UEFI
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SP SETUP
def system_info_003():
    tc = ('802', '[TC802] Testcase_SystemInfo_003', '03 按热键后屏幕底部显示提示信息测试 UEFI')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert hotkey_press()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 04 按热键后屏幕底部显示提示信息测试 legacy
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SP SETUP
def system_info_004():
    tc = ('803', '[TC803] Testcase_SystemInfo_004', '04 按热键后屏幕底部显示提示信息测试 legacy')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert hotkey_press()
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Author: Fubaolin
# Testcase_LogTime_001, 003 串口日志打印
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
@core.test_case(('804', '[TC804] 串口日志打印测试01_03', '【UEFI模式】支持BIOS启动开始和结束信息打印及上报'))
def Testcase_LogTime_01_03():
    try:
        assert SetUpLib.boot_suse_from_bm()
        assert log_Time('804')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail


# Author: Fubaolin
# Testcase_LogTime_001, 003 串口日志打印
# Precondition: linux-OS
# OnStart: fulldebug
# OnComplete: NA
@core.test_case(('805', '[TC805] 串口日志打印测试02', '【全打印开启】支持BIOS启动开始和结束信息打印及上报'))
def Testcase_LogTime_02():
    try:
        assert BmcLib.debug_message(enable=True), "debug message enable fail"  # 開啓全打印
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, delay=600), "boot up fail"
        assert log_Time('805')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail
    finally:    
        BmcLib.debug_message(False)  


# Testcase_PXERetry_001
# Precondition: 1、BIOS默认值配置。 只有Boot Retry使能，才可进行多次PXE retry。
# OnStart: 'UEFI'模式
# Steps:
# '1、启动进Boot菜单，查看是否存在PXE Retry Count菜单，有结果A；
#  2、Boot Fail Policy设置为Cold Boot或None，检查PXE Retry Count菜单，有结果B。
#  A：显示PXE Retry Count菜单，默认值为1；
#  B：PXE Retry Count菜单隐藏或置灰。
# OnCompleted: Setup
def testcase_pxeRetry_001():
    tc = ('806', '[TC806] 01 PXE Retry菜单设置测试', '支持PXE retry功能')
    result = ReportGen.LogHeaderResult(tc)
    assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
    try:
        assert SetUpLib.locate_option(Key.DOWN, ['Boot Fail Policy', '<Boot Retry>'], 7)
        assert SetUpLib.locate_option(Key.DOWN, ['PXE Retry Count', '\[1\]'], 7)
        assert SetUpLib.set_option_value('Boot Fail Policy', 'None')
        assert SetUpLib.locate_option(Key.DOWN, ['PXE Retry Count', '\[1\]'], 7) is None
        assert SetUpLib.set_option_value('Boot Fail Policy', 'Cold Boot')
        assert SetUpLib.locate_option(Key.DOWN, ['PXE Retry Count', '\[1\]'], 7) is None
        result.log_pass()  # 期望选项隐藏
        return True
    except AssertionError:
        result.log_fail()


# Testcase_LogTime_007
# Precondition: 1、BMC BT通道打开；# 2、可正常启动进入OS。
# OnStart: 'UEFI'模式
# Steps:
# '1、BIOS正常启动进入OS，查看BT通道打印，有结果A。
#  A：启动过程中不会上报结束标志，仅进入OS时上报一次结束标志。
# OnCompleted: OS
@core.test_case(('807', '[TC807] 07 【UEFI模式】BIOS正常启动进入OS结束标志上报', 'BIOS上报启动完成标记给BMC'))
def testcase_logTime_007():
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('DB 07 00 05 10 01', 60):
        core.capture_screen()
        return core.Status.Fail
    return core.Status.Pass


# Testcase_LogTime_008
# Precondition: 1、BMC BT通道打开；# 2、可正常启动进入OS。
# OnStart: 'UEFI'模式
# Steps:
# 1、BIOS启动，Post阶段通过KVM反复复位系统3次，查看BT通道打印，有结果A；
# 2、Post完成后进入OS，有结果B。
# A：启动过程中不会上报结束标志；
# B：仅进入OS时上报一次结束标志。
# OnCompleted: OS
@core.test_case(('808', '[TC808] 08 【UEFI模式】BIOS Post阶段反复复位后，启动结束标志上报', 'BIOS上报启动完成标记给BMC'))
def testcase_logTime_008():
    for i in range(3):
        assert BmcLib.force_reset()
        assert BmcLib.read_bt_data('DB 07 00 05 10 01', 10) is None  # excepted_result - can not find the data
    logging.info('3 times force reset at post done,')
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('DB 07 00 05 10 01', 100):
        core.capture_screen()
        return core.Status.Fail
    return core.Status.Pass


# Testcase_ReportSMBIOSToBMC_001
# Precondition: 1、BMC BT通道打开；# 2、可正常启动进入OS。
# OnStart: 'UEFI'模式
# Steps:
# '1、BIOS正常启动；
#  2、检查BIOS启动阶段，BT通道中上报SMBIOS情况(关键字：DB 07 00 04 00)，有结果A。
#  A：BT通道中正确上报SMBIOS信息。
# OnCompleted: OS
@core.test_case(('809', '[TC809] 01 SMBIOS信息上报BMC测试', 'SMBIOS信息上报BMC'))
def report_smbios_toBMC_001():
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('DB 07 00 04 00', 100):
        return core.Status.Fail
    return core.Status.Pass


# Testcase_PCIeBDFToBMC_001
# Precondition: 1、PCIe槽位安装PCIe卡；2、开启全打印；3、开启BT通道。
# OnStart: 'UEFI'模式
# Steps:
# '1、BIOS正常启动，检查串口打印中PCIe设备BDF上报信息，有结果A；
#  2、BMC Web侧检查PCIe设备所属CPU和Port信息是否正确，有结果B；  skip, TBD
#  3、BT通道搜索“C6 01 01”检查上报记录是否正确，有结果C。
#  A：串口正确打印上报的BDF信息；
#  B：Web界面显示信息正确；
#  C：BT通道上报BDF信息正确。
# OnCompleted: OS
@core.test_case(('810', '[TC810] 01 PCIe设备BDF信息上报BMC测试', 'PCIe设备BDF信息上报BMC'))
def pcie_bdf_toBMC_001():
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('C6 01 01', 100):
        return core.Status.Fail
    return core.Status.Pass


# Testcase_HotKey_002
# Precondition: SOL串口重定向已连接
# OnStart: 'UEFI'模式
# Steps:
# ''遍历UEFI和Legacy模式：
# 1、BIOS正常启动；
# 2、检查SOL界面显示的热键信息是否正确，有结果A。
# A：SOL正确显示热键信息，包括DEL、F6、F11、F12。
# OnCompleted: OS
@core.test_case(('811', '[TC811] 02 BIOS启动阶段SOL热键显示测试', '支持热键配置'))
def testcase_hotKey_002():
    assert BmcLib.force_reset()
    if not BmcLib.read_sol_data([Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F12], 60):
        core.capture_screen()
        return core.Status.Fail
    return core.Status.Pass
