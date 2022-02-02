# this script just for hotkey related function test
import logging
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


def _check_info():
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


def _hotkey_press():
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


def _log_Time(log_n):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600) #考虑全打印
        logging.info("Suse_OS Boot Successful")
        SERIAL_LOG = os.path.join(SutConfig.Env.LOG_DIR, 'TC{}.log'.format(log_n))
        with open(SERIAL_LOG , 'r', encoding="utf-8") as _log:
            ser_log = _log.read()
        s_cont = 0
        for str_check in SutConfig.SysCfg.OEM_LOG_SUT + Msg.OEM_LOG_COMMON:
            if not re.search(str_check, ser_log):
                s_cont += 1
                logging.info('**{} -- not found**'.format(str_check))
        return s_cont == 0
    except AssertionError as e:
        logging.error(e)
        return False


def _bt_logTime(timeout = 60):
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('14 E3 00 05 10 01', timeout):
        core.capture_screen()
        return False
    return True

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
        assert _check_info()
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
        assert _check_info()
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
        assert _hotkey_press()
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
        assert _hotkey_press()
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
        assert _log_Time('804')
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
        assert _log_Time('805')
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
    try:
        assert _bt_logTime(60)
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail


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
        assert BmcLib.read_bt_data('14 E3 00 05 10 01', 10) is None  # excepted_result - can not find the data
    logging.info('3 times force reset at post done,')
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('14 E3 00 05 10 01', 100):
        core.capture_screen()
        return core.Status.Fail
    return core.Status.Pass


# Testcase_ReportSMBIOSToBMC_001
# Precondition: 1、BMC BT通道打开；# 2、可正常启动进入OS。
# OnStart: 'UEFI'模式
# Steps:
# '1、BIOS正常启动；
#  2、检查BIOS启动阶段，BT通道中上报SMBIOS情况(关键字：14 E3 00 05 10)，有结果A。
#  A：BT通道中正确上报SMBIOS信息。
# OnCompleted: OS
@core.test_case(('809', '[TC809] 01 SMBIOS信息上报BMC测试', 'SMBIOS信息上报BMC'))
def report_smbios_toBMC_001():
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('14 E3 00 05 10', 100):
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


# Author: Fubaolin
# Testcase_LogTime_006
# Precondition: 1、BMC BT通道打开；# 2、可正常启动进入OS。
# OnStart: 'Legacy'模式
# Steps:
# '1、BIOS正常启动进入OS，查看BT通道打印，有结果A。
#  A：启动过程中不会上报结束标志，启动完成后仅上报一次结束标志，进入OS时不会重复上报。
# OnCompleted: OS
@core.test_case(('812', '[TC812] 06 【Legacy模式】BIOS正常启动结束标志上报', 'BIOS上报启动完成标记给BMC'))
def Legacy_Testcase_LogTime_006():
    try:
        # assert SetUpLib.enable_legacy_boot()   #Scope_group下，条件已满足
        assert _bt_logTime(300)
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail


# Testcase_FDM_PostErrReport_004
# Precondition: 开启BT通道。
# OnStart: UEFI模式
# Step:
# 1、BIOS正常启动；
# 2、BMC BT通道信息中查找"DB 07 00 17 01"字段；
# 3、与启动日志中的CPU Stack bus信息对比，有结果A。
# Expt_result:
# A：正确上报CPU Stack bus信息。 01：ParaSel ；39：信息大小； 02：CPU个数； 00：Segment 后面6个字节为stack号：00 xx xx xx xx xx
# OnCompleted: OS
@core.test_case(('813', '[TC813]04 FDM上报CPU Stack的BUS分配', '支持Post阶段故障信息搜集上报'))
def fdm_PostErrReport_004(start=18, end=31, flg='00'):
    """
    start: msg start index num,
    end: msg end index num,
    flg: 6个字节为stack号, 切片字符串
    """
    stk_bus = []
    bt_data_bus = []
    key_str = '14 E3 00 17 01 39 0{0}'.format(str(SutConfig.SysCfg.CPU_CNT))  # 01：ParaSel ；39：信息大小； 0{0}：CPU个数
    try:
        assert BmcLib.force_reset()
        cpu_log = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 100,
                                    120)
        assert cpu_log is not None, 'serial -> no data output'
        for i in cpu_log.split('\n'):
            if 'Stk' in i:
                for j in i.split():
                    if '0x' in j:
                        if len(j) == 4:  # get the stk bus addr,
                            stk_bus.append(j.replace('0x', ''))
        # read the bt data,
        assert BmcLib.force_reset()
        # 01：ParaSel ；39：信息大小； 02：CPU个数
        res = BmcLib.read_bt_data(key_str, 100)
        assert res, 'bt -> no data output'
        for i_str in res[1].split('\n'):
            if key_str in i_str:
                # assume index 18 to 31 is sku bus num, depends on bmc bt data format.
                for j_str in i_str.split()[start:end]:
                    bt_data_bus.append(j_str)
        # 6个字节为stack号
        del_item = [key for key, x in enumerate(bt_data_bus) if x == flg]  # 00 string
        final_lst = [bt_data_bus[k] for k in range(0, len(bt_data_bus), 1) if k not in del_item[1:len(del_item)]]
        assert stk_bus[0::2] == final_lst, 'skt bus failed - {0}'.format(list(set(stk_bus[0::2]) - set(final_lst)))
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail


# Testcase_FDM_PostErrReport_005
# Precondition: 开启BT通道。
# OnStart: UEFI模式
# Step:
# 1、BIOS正常启动；
# 2、BMC BT通道信息中查找"DB 07 00 17 03"字段；
# 3、检查上报的CPU型号是否正确，有结果A。
# Expt_result:
# A：上报信息中可以查询到03 01 06，表示上报CPU类型正确。
# OnCompleted: OS
@core.test_case(('814', '[TC814]05 FDM上报CPU型号', '支持Post阶段故障信息搜集上报'))
def fdm_PostErrReport_005():
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('14 E3 00 17 03 01 06', 100):
        return core.Status.Fail
    return core.Status.Pass


# Testcase_FDM_PostErrReport_006
# Precondition: 开启BT通道。
# OnStart: UEFI模式
# Step:
# 1、BIOS正常启动；
# 2、BMC BT通道信息中查找"DB 07 00 17 02"字段；
# 3、OS下通过uniCfg工具查询变量状态，检查上报状态是否正确，有结果A。
# Expt_result:
# A：FDMSupport：01  EmcaCsmiEn：02   IoMcaEn：00   ViralEn：00    PoisonEn：01  EmcaMsmiEn：02。
# OnCompleted: OS
@core.test_case(('815', '[TC815]06 FDM上报Setup配置信息', '支持Post阶段故障信息搜集上报'))
def fdm_PostErrReport_006():
    try:
        assert BmcLib.force_reset()
        assert BmcLib.read_bt_data("14 E3 00 17 02 08 01 02 00 00 01 02", 100)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 150)
        assert Sut.UNITOOL.check(**{"FDMSupport": 1, "EmcaCsmiEn": 2, "IoMcaEn": 0, "ViralEn": 0, "PoisonEn": 1,
                                    "EmcaMsmiEn": 2})
        return core.Status.Pass
    except AssertionError:
        core.capture_screen()
        return core.Status.Fail


# Testcase_FDM_PostErrReport_007
# Precondition: 开启BT通道。
# OnStart: UEFI模式
# Step:
# 1、BIOS正常启动；
# 2、BMC BT通道信息中查找"DB 07 00 17 09"字段；
# 3、打开全打印，检查CPU Thread ID信息上报是否正确，有结果A。
# Expt_result:
# A：正确上报CPU Thread ID信息。
# OnCompleted: OS
@core.test_case(('816', '[TC816]07 FDM上报Thread ID信息', '支持Post阶段故障信息搜集上报'))
def fdm_PostErrReport_007():
    # should confirmed with dev,
    tread1_str = "14 E3 00 17 0B 23 00 20 01 " \
                 "00 02 04 06 08 0A 0E 10 12 14 16 18 1A 1C 22 24 26 28 2A 2C 2E 30 34 36 38 3A 3C 3E 40 44 46"
    # tread2_str = "14 E3 00 17 0B 23 01 20 01 " \
    #              "00 02 04 06 08 0A 0E 10 12 14 16 18 1A 1C 22 24 26 28 2A 2C 2E 30 34 36 38 3A 3C 3E 40 44 46"
    assert BmcLib.force_reset()
    # exp_str = "{0}|{1}".format(tread1_str, tread2_str)   # 可修改，默认读CPU0
    if BmcLib.read_bt_data(tread1_str, 100):
        return core.Status.Pass
    else:
        core.capture_screen()
        return core.Status.Fail


# Testcase_FDM_PostErrReport_008
# Precondition: 开启BT通道。
# OnStart: UEFI模式
# Step:
# 1、BIOS正常启动；
# 2、BMC BT通道信息中查找"DB 07 00 17 04"字段；
# 3、检查MCA寄存器信息上报是否正确，有结果A。
# Expt_result:
# A：正确上报MSR 0x178 、0x179、0x17F和0x35。
# OnCompleted: OS
@core.test_case(('817', '[TC817]08 FDM上报MCA寄存器', '支持Post阶段故障信息搜集上报'))
def fdm_PostErrReport_008():
    # should confirmed with dev,
    msr_str = "14 E3 00 17 04 28 78 01 01 00 00 00 00 00 00 00 79 01 1C 0C 00 0F 00 00 00 00 " \
              "7F 01 00 00 00 00 00 00 00 00 35 00 40 00 20 00 00 00 00 00 00"
    try:
        assert BmcLib.force_reset()
        assert BmcLib.read_bt_data(msr_str, 100)
        return core.Status.Pass
    except AssertionError:
        core.capture_screen()
        return core.Status.Fail


