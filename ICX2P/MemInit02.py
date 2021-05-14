# this script just for dimm related test func

import logging
import unittest
import numpy, re
from Core.SutInit import Sut
from Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.SutConfig import SysCfg
from ICX2P.Config.PlatConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib, icx2pAPI, BmcLib
from Core import SerialLib, SshLib
from ICX2P import Os


# Test case ID: TC700-750

##########################################
#            Release Test Cases          #
##########################################

# go to memory frequency page
def navigate_to_mem_fre():
    assert(SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 6))
    assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.MEMORY_CONFIG], 12, Msg.MEM_FRE))

# go to cke power down page
def navigate_to_cke():
    assert(SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 6))
    assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.ADV_POWER_MGF_CONFIG,
                                                   Msg.MEM_POWER_THER_CONFIG, Msg.MEM_POWER_ADV], 12, Msg.CKE))

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS Setup
# 03 支持内存电源管理配置
def dimm_power_mgt_01():
    tc = ('700', 'Testcase_MemPower_001', 'BIOS默认关闭DDR4内存的LP-ASR模式测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(SetUpLib.boot_to_page(Msg.PAGE_INFO))
        if SetUpLib.verify_info(['CPU Number\s+2'], 7):
            assert navigate_to_mem_fre(), 'navigate to mem freq page -> fail'
            assert(SetUpLib.verify_options(Key.DOWN, [[Msg.MEM2X_REFRESH, '<Disabled>']], 7))
        elif SetUpLib.verify_info(['CPU Number\s+4'], 7):
            assert navigate_to_mem_fre(), 'navigate to mem freq page -> fail'
            assert(SetUpLib.verify_options(Key.DOWN, [[Msg.MEM2X_REFRESH, '<Extended>']], 7))
        else:
            logging.info('Unsupported CPU Number...')
            raise AssertionError
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        return False

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS Setup
def dimm_power_mgt_02():
    tc = ('701', 'Testcase_MemPower_002&3', 'BIOS默认关闭CKE Power Down&Setup菜单提供内存自刷新和CKE Power Down选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(SetUpLib.boot_to_page(Msg.PAGE_INFO))
        assert navigate_to_mem_fre(), 'navigate to mem freq page -> fail'
        SetUpLib.send_key(Key.ESC)
        assert(SetUpLib.enter_menu(Key.DOWN, [Msg.ADV_POWER_MGF_CONFIG, Msg.MEM_POWER_THER_CONFIG,
                                                       Msg.MEM_POWER_ADV], 12, Msg.CKE))
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        return False

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_04():
    tc = ('702', 'Testcase_MemPower_004', '打开DDR4内存的LP-ASR模式功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(SetUpLib.boot_to_page(Msg.PAGE_INFO))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.LPASR_MODE, '<Auto SR>']], 7))
        assert(SetUpLib.boot_to_bootmanager())
        assert(SetUpLib.enter_menu(Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        return False

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_05():
    tc = ('703', 'Testcase_MemPower_005', '打开CKE Power down功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(SetUpLib.boot_to_page(Msg.PAGE_INFO))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        assert(SetUpLib.continue_to_page(Msg.PAGE_INFO))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
        assert(SetUpLib.boot_to_bootmanager())
        assert(SetUpLib.enter_menu(Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
        assert(icx2pAPI.ping_sut())
        SetUpLib.reset_default()
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        SetUpLib.reset_default()
        return False

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS Setup
def dimm_power_mgt_07():
    tc = ('704', '[TC704]Testcase_MemPower_007', '内存省电模式选项互斥测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(SetUpLib.boot_to_page(Msg.PAGE_INFO))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>'], ['PPD', '<Enabled>']], 7))
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Enabled>']], 3))
        assertFalse(SetUpLib.verify_options(Key.DOWN, [['PPD', '<Enabled>']], 3))
    except AssertionError as err:
        result.log_fail(capture=True)
        SetUpLib.reset_default()
        return False
    SetUpLib.reset_default()
    result.log_pass()

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_010(serial, ssh_os, ssh_bmc):
    tc = ('705', 'Testcase_MemPower_010', '内存省电模式使能PPD时寄存器状态测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(icx2pAPI.toBIOS(serial, ssh_bmc))
        assert(icx2pAPI.toBIOSConf(serial))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        assert(icx2pAPI.toBIOSnp(serial))
        assert(icx2pAPI.toBIOSConf(serial))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
        assert(SetUpLib.boot_to_bootmanager())
        assert(SetUpLib.enter_menu(Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
        assert(icx2pAPI.ping_sut())
        assert(icx2pAPI.rw_everything(ssh_os, SutConfig.CKE_POWER_DOWN, ['c61218a0', 'fb9a18a4']))
        SetUpLib.reset_default()
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        SetUpLib.reset_default()
        return False

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_011(serial, ssh_os, ssh_bmc):
    tc = ('706', 'Testcase_MemPower_011', '内存省电模式使能APD时寄存器状态测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(icx2pAPI.toBIOS(serial, ssh_bmc))
        assert(icx2pAPI.toBIOSConf(serial))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>'], ['PPD', '<Enabled>']], 7))
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Enabled>']], 3))
        assertFalse(SetUpLib.verify_options(Key.DOWN, [['PPD', '<Enabled>']], 3))
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert(icx2pAPI.toBIOSnp(serial))
        assert(icx2pAPI.toBIOSConf(serial))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
        assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert(SetUpLib.verify_options(Key.DOWN, [['APD', '<Enabled>']], 3))
        assert(SetUpLib.boot_to_bootmanager())
        assert(SetUpLib.enter_menu(Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
        assert(icx2pAPI.ping_sut())
        assert(icx2pAPI.rw_everything(ssh_os, ['1100', '010f'], ['c61218a0']))
        SetUpLib.reset_default()
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        SetUpLib.reset_default()
        return False

# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_012(serial, ssh_os, ssh_bmc):
    tc = ('707', 'Testcase_MemPower_012', '内存省电模式使能时更改定时器选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert(icx2pAPI.toBIOS(serial, ssh_bmc))
        assert(icx2pAPI.toBIOSConf(serial))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert(SetUpLib.verify_options(Key.DOWN, [['CKE Idle Timer', '\[20\]']], 7))
        SetUpLib.send_key(Key.ENTER)  # Send Enter
        SetUpLib.send_data_enter('255')  # set 255
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert(icx2pAPI.toBIOSnp(serial))
        assert(icx2pAPI.toBIOSConf(serial))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert(SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
        assert(SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert(SetUpLib.verify_options(Key.DOWN, [['CKE Idle Timer', '\[255\]']], 7))
        assert(SetUpLib.boot_to_bootmanager())
        assert(SetUpLib.enter_menu(Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
        assert(icx2pAPI.ping_sut())
        assert(icx2pAPI.rw_everything(ssh_os, ['1100', '02bf'], ['c61218a0']))
        SetUpLib.reset_default()
        result.log_pass()
    except AssertionError as err:
        result.log_fail(capture=True)
        SetUpLib.reset_default()
        return False

# 检查并打开RMT菜单,重启查看串口是否正常打印RMT数据
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_MemMargin_001():
    tc = ('708', '[TC708] Testcase_MemMargin_001', '01 内存margin测试菜单选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)

    BSSA_MENU = "BSSA Configuration Menu"
    BSSA_RMT = "BSSA Rank Margin Tool"
    BSSA_RMT_FAST = "BSSA RMT on Fast Cold Boot"
    SERIAL_RMT_FLAG = ["START_BSSA_RMT", "Ctl+"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED), "boot_to_page -> fail"
        logging.info("Press Enter")
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_CONFIG, BSSA_MENU], 15, BSSA_RMT), "enter_menu >> fail"
        # BSSA Rank Margin Tool: Enable
        assert SetUpLib.locate_option(Key.DOWN, [BSSA_RMT, "<Disabled>"], 15), "locate_option >> fail"
        logging.info("Press F6")
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.verify_options(Key.DOWN, [[BSSA_RMT, "<Enabled>"]], 15), "verify_options >> fail"
        logging.info(f"{BSSA_RMT} -> Enabled")
        # BSSA RMT on Fast Cold Boot: Enable
        assert SetUpLib.locate_option(Key.DOWN, [BSSA_RMT_FAST, "<Disabled>"], 15), "locate_option >> fail"
        logging.info("Press F6")
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.verify_options(Key.DOWN, [[BSSA_RMT_FAST, "<Enabled>"]], 15), "verify_options >> fail"
        logging.info(f"{BSSA_RMT_FAST} -> Enabled")
        # Serial Debug Message: Enable
        assert BmcLib.debug_message(enable=True), "bmc_debug_message >> fail"
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.wait_strings(SERIAL_RMT_FLAG, 600), "waitStrings >> fail"
        result.log_pass()
    except AssertionError as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# 01 内存初始化测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS SETUP
def Testcase_MemoryCompa_001():
    tc = ('709', '[TC709] Testcase_MemoryCompa_001', '01 内存初始化测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED), "boot_to_page -> fail"
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.MEMORY_TOP], 15,
                                   'DIMM000\(A\)'), "enter_menu >> fail"
        assert SetUpLib.verify_info(SutConfig.DIMM_info, 20)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 06 内存容量一致性测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def Testcase_MemoryCompa_006(serial, ssh_os, n=1):
    tc = ('710', '[TC710] Testcase_MemoryCompa_006', '06 内存容量一致性测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    res_lst = []
    for i in range(n):
        try:
            assert SetUpLib.boot_to_page('BIOS Revision'), "boot_to_page -> fail"
            assert SetUpLib.verify_info('Total Memory\s+65536 MB', 20), "dimm_size_verify -> fail"
            assert Os.boot_to_suse(serial), "boot_to_os -> fail"
            assert icx2pAPI.ping_sut(), "ping_os_ip-> fail"
            res = SshLib.execute_command(ssh_os, 'dmesg | grep -i e820')
            for j in res.split('\n'):
                if 'BIOS-e820' in j and 'ACPI' not in j:
                    for k in j.split(' '):
                        if '-' and '0x' in k.strip(']'):
                            for m in k.strip(']').split('-'):
                                res_lst.append(int(m, 16))
            base_adr = res_lst[0:100:2]  # store mem start addr
            for j1 in range(len(res_lst)):
                for k1 in res_lst:
                    if k1 in base_adr:
                        res_lst.remove(k1)
            stop_adr = res_lst  # restore the res_lst - mem stop addr
            base_array = numpy.array(base_adr)
            stop_array = numpy.array(stop_adr)
            e820 = numpy.matrix.tolist(stop_array - base_array)
            mem_size = sum(e820) / 1024 / 1024 / 1024
            assert int(mem_size) == SysCfg.DIMM_SIZE, 'dimm_size_diff_fail'
            result.log_pass()
        except AssertionError:
            result.log_fail(capture=True)


# 01 设置动态内存刷新模式功能测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def Testcase_MemRefresh_001(serial, ssh_os):
    tc = ('711', '[TC711] Testcase_MemRefresh_001', '01 设置动态内存刷新模式功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), "boot_to_page -> fail"
        assert SetUpLib.locate_option(Key.DOWN, [Msg.MEM2X_REFRESH, '<Disabled>'], 10), "locate_option -> fail"
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        assert Os.boot_to_suse(serial), "boot_to_os -> fail"
        assert icx2pAPI.ping_sut(), "ping_os_ip-> fail"
        assert icx2pAPI.rw_everything(ssh_os, ['005f', '5a55'], ['c99224e0', 'fb9224e0'])
        assert SetUpLib.reset_default()
        result.log_pass()
    except AssertionError:
        assert SetUpLib.reset_default()
        result.log_fail(capture=True)


# 02 设置静态2X内存刷新模式功能测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def Testcase_MemRefresh_002(serial, ssh_os):
    tc = ('712', '[TC712] Testcase_MemRefresh_001', '02 设置静态2X内存刷新模式功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), "boot_to_page -> fail"
        assert SetUpLib.enter_menu(Key.DOWN, Msg.MEMORY_CONFIG, 10, Msg.MEM_FRE), "enter_menu -> fail"
        assert SetUpLib.locate_option(Key.DOWN, [Msg.MEM2X_REFRESH, '<Disabled>'], 10), "locate_option -> fail"
        SetUpLib.send_keys([Key.F6 * 3, Key.F10, Key.Y])
        assert Os.boot_to_suse(serial), "boot_to_os -> fail"
        assert icx2pAPI.ping_sut(), "ping_os_ip-> fail"
        assert icx2pAPI.rw_everything(ssh_os, ['005f', '5a55'], ['c99224e0', 'fb9224e0'])
        assert SetUpLib.reset_default()
        result.log_pass()
    except AssertionError:
        assert SetUpLib.reset_default()
        result.log_fail(capture=True)


# 装备模式下打开RMT并检查串口RMT数据是否正常打印
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def Testcase_MemoryCompa_009(unitool):
    tc = ('713', '[TC713]Testcase_MemoryCompa_009', '装备模式内存Margin功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    logging.info("Change setup option to enable RMT")
    try:
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
        assert icx2pAPI.ping_sut()
        assert unitool.set_config(BiosCfg.MFG_RMT), "Change setup by unitool failed."
        logging.info("Reboot SUT to Linux")
        assert BmcLib.force_reset()
        ser_rmt_data = SerialLib.cut_log(Sut.BIOS_COM, "START_BSSA_RMT", "STOP_BSSA_RMT", 15, 600)
        assert ("Ctl+" in ser_rmt_data), "Invalid RMT data"
        BmcLib.clear_cmos()
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        BmcLib.clear_cmos()
        result.log_fail()


# 01 内存频率选项默认值测试/02 2666内存频率设置测试/03 2933内存频率设置测试/04 2933内存频率设置长时间测试/05 3200内存频率设置测试
# 06 3200内存频率设置长时间测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def navegate_to_mem_fre_option(serial, n=1):  # used to set mem freq test
    assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), "boot_to_page -> fail"
    assert SetUpLib.enter_menu(Key.DOWN, Msg.MEMORY_CONFIG, 10, Msg.MEM_FRE), "enter_menu -> fail"
    assert SetUpLib.locate_option(Key.DOWN, [Msg.MEM_FRE, 'Auto'], 10), "locate_option -> fail"
    SetUpLib.send_keys([Key.F6 * n, Key.F10, Key.Y])
    assert Os.boot_to_suse(serial), "boot_to_os -> fail"
    assert icx2pAPI.ping_sut(), "ping_os_ip-> fail"
    assert SetUpLib.reset_default()


def Testcase_SetMemFreq_001_006(serial, n=1):
    tc = ('714', '[TC714] Testcase_SetMemFreq_001_006', '01-06 内存频率选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page('BIOS Revision'), "boot_to_page -> fail"
        if SetUpLib.verify_info('System Memory Speed\s+2666 MT\/s', 20):
            logging.info('DIMM FRE is 2666 MT/s')
            assert navegate_to_mem_fre_option(serial), '2666-dimm_2666_mem_freq_test -> fail'
        elif SetUpLib.verify_info('System Memory Speed\s+2933 MT\/s', 20):
            logging.info('DIMM FRE is 2933 MT/s')
            assert navegate_to_mem_fre_option(serial), '2933-dimm_2666_mem_freq_test -> fail'
            assert navegate_to_mem_fre_option(serial, 2), '2933-dimm_2933_mem_freq_test -> fail'
        elif SetUpLib.verify_info('System Memory Speed\s+3200 MT\/s', 20):
            logging.info('DIMM FRE is 3200 MT/s')
            for i in range(n):
                assert navegate_to_mem_fre_option(serial), '3200-dimm_2666_mem_freq_test -> fail'
                assert navegate_to_mem_fre_option(serial, 2), '3200-dimm_2933_mem_freq_test -> fail'
                assert navegate_to_mem_fre_option(serial, 3), '3200-dimm_3200_mem_freq_test -> fail'
        else:
            logging.info('Not supported this dimm type')
        result.log_pass()
    except AssertionError:
        assert SetUpLib.reset_default()
        result.log_fail(capture=True)


# 01 MTRR最大内存地址范围测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def Testcase_MTRR_001(ssh_os):
    tc = ('715', '[TC715] Testcase_MTRR_002', '01 MTRR最大内存地址范围测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        # assert Os.boot_to_suse(serial, ssh_bmc), "boot_to_os -> fail"
        assert icx2pAPI.ping_sut(), "ping_os_ip-> fail"
        res = SshLib.execute_command(ssh_os, 'cat /proc/mtrr')
        mem_size = re.findall(r"\d+\.?\d*", res.split('=')[2])
        for i in mem_size:
            if int(i)/1024 == SysCfg.DIMM_SIZE * 2:
                logging.info('MTRR MAX DIMM SIZE Pass')
        result.log_pass()
    except AssertionError:
        logging.info('MTRR MAX DIMM SIZE Fail')
        result.log_fail(capture=True)


# 02 MTRR Fixed ranges测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def Testcase_MTRR_002(serial, ssh_os):
    tc = ('716', '[TC716] Testcase_MTRR_002', '02 MTRR Fixed ranges测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    flag = []
    try:
        assert BmcLib.force_reset(), 'reset_system -> fail'
        assert not SetUpLib.wait_message('0xa0300', 60), 'find 0xa0300 string'
        assert Os.boot_to_suse(serial), "boot_to_os -> fail"
        assert icx2pAPI.ping_sut(), "ping_os_ip-> fail"
        res = SshLib.execute_command(ssh_os, 'dmesg | grep MTRR')
        if 'MTRR fixed ranges enabled' in res:
            logging.info('MTRR fixed ranges enabled')
        else:
            logging.info('MTRR fixed ranges not enabled')
            status = 1
            flag.append(status)
        res_1 = SshLib.execute_command(ssh_os, 'dmesg | grep A0000')
        if 'A0000-FFFFF uncachable' in res_1:
            logging.info('MTRR fixed ranges enabled')
        else:
            logging.info('MTRR fixed ranges not enabled')
            status = 2
            flag.append(status)
        assert len(flag) == 0, 'MTRR_fixed_ranges_test -> fail'
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
