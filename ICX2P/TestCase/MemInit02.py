# this script just for dimm related test func

import logging
import numpy, re
from Core.SutInit import Sut
from Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.SutConfig import SysCfg
from ICX2P.Config.PlatConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib, PlatMisc, BmcLib
from Core import SerialLib, SshLib, MiscLib

# Test case ID: TC700-750

##########################################
#            Release Test Cases          #
##########################################

'''
function module, only used below
'''

# defined cscripts command
cscripts_cmd_cke = 'sv.socket0.uncore.memss.mc1.ch0.cke_ll0.show()'
cscripts_cmd_refresh = 'sv.socket0.uncore.memss.mc1.ch0.dimm_temp_th_0.show()'

# go to memory frequency page
def navigate_to_mem_fre():
    try:
        assert SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 6)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 12, Msg.MEM_FRE)
        return True
    except AssertionError:
        logging.info("navigate_to_mem_fre: Fail")


# go to cke power down page
def navigate_to_cke():
    try:
        assert SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 6)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.CKE)
        return True
    except AssertionError:
        logging.info("navigate_to_cke: Fail")


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS Setup
# 03 支持内存电源管理配置
def dimm_power_mgt_01():
    tc = ('700', '[TC700]Testcase_MemPower_001', 'BIOS默认关闭DDR4内存的LP-ASR模式测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert (SetUpLib.boot_to_page(Msg.PAGE_INFO))
        if SetUpLib.verify_info(['CPU Number\s+2'], 7):
            assert navigate_to_mem_fre(), 'navigate to mem freq page -> fail'
            assert (SetUpLib.verify_options(Key.DOWN, [[Msg.MEM2X_REFRESH, '<Dynamic Mode>']], 7))
        elif SetUpLib.verify_info(['CPU Number\s+4'], 7):
            assert navigate_to_mem_fre(), 'navigate to mem freq page -> fail'
            assert (SetUpLib.verify_options(Key.DOWN, [[Msg.MEM2X_REFRESH, '<Static 2X Mode>']], 7))
        else:
            logging.info('Unsupported CPU Number...')
            raise AssertionError
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS Setup
def dimm_power_mgt_02():
    tc = ('701', '[TC701]Testcase_MemPower_002&3', 'BIOS默认关闭CKE Power Down&Setup菜单提供内存自刷新和CKE Power Down选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert (SetUpLib.boot_to_page(Msg.PAGE_INFO))
        assert navigate_to_mem_fre(), 'navigate to mem freq page -> fail'
        SetUpLib.send_key(Key.ESC)
        assert (SetUpLib.enter_menu(Key.DOWN, [Msg.ADV_POWER_MGF_CONFIG, Msg.MEM_POWER_THER_CONFIG,
                                               Msg.MEM_POWER_ADV], 12, Msg.CKE))
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_04():
    tc = ('702', '[TC702]Testcase_MemPower_004', '打开DDR4内存的LP-ASR模式功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert SetUpLib.verify_options(Key.DOWN, [[Msg.LPASR_MODE, '<Auto SR>']], 7)
        assert SetUpLib.boot_option_from_bm(Msg.BOOT_OPTION_SUSE, Msg.BIOS_BOOT_COMPLETE)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_05():
    tc = ('703', '[TC703]Testcase_MemPower_005', '打开CKE Power down功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        assert SetUpLib.continue_to_page(Msg.PAGE_INFO)
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7)
        assert SetUpLib.boot_option_from_bm(Msg.BOOT_OPTION_SUSE, Msg.BIOS_BOOT_COMPLETE)
        assert (MiscLib.ping_sut(SutConfig.OS_IP, 600))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS Setup
def dimm_power_mgt_07():
    tc = ('704', '[TC704]Testcase_MemPower_007', '内存省电模式选项互斥测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert (SetUpLib.boot_to_page(Msg.PAGE_INFO))
        assert navigate_to_cke(), 'navigate to mem cke power page -> fail'
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert (SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>'], ['PPD', '<Enabled>']], 7))
        assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Enabled>']], 3))
        if SetUpLib.verify_options(Key.DOWN, [['PPD', '<Enabled>']], 3):
            raise AssertionError
        else:
            result.log_pass()  # the expected result here's that the option can not be found.
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_010():
    tc = ('705', '[TC705]Testcase_MemPower_010', '内存省电模式使能PPD时寄存器状态测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    exp_list = ['0x00000001:ddrt_cke_en(24:24)', '0x00000001:ppd_en(09:09)', '0x00000000:apd_en(08:08)', '0x0000000d:cke_idle_timer(07:00)']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.MEM_POWER_ADV)
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.MEM_POWER_ADV)
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
        assert SetUpLib.boot_option_from_bm(Msg.BOOT_OPTION_SUSE, Msg.BIOS_BOOT_COMPLETE)
        assert (PlatMisc.cscripts_inband_register(cscripts_cmd_cke, exp_list))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_011():
    tc = ('706', '[TC706]Testcase_MemPower_011', '内存省电模式使能APD时寄存器状态测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    exp_list = ['0x00000001:ddrt_cke_en(24:24)', '0x00000000:ppd_en(09:09)', '0x00000001:apd_en(08:08)', '0x0000000d:cke_idle_timer(07:00)']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.MEM_POWER_ADV)
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert (SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>'], ['PPD', '<Enabled>']], 7))
        assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Enabled>']], 3))
        # the expected result here's that the option can not be found.
        if SetUpLib.verify_options(Key.DOWN, [['PPD', '<Enabled>']], 3):
            raise AssertionError
        else:
            SetUpLib.send_keys(Key.SAVE_RESET)
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.MEM_POWER_ADV)
            assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
            assert (SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
            assert (SetUpLib.verify_options(Key.DOWN, [['APD', '<Enabled>']], 3))
            assert SetUpLib.boot_option_from_bm(Msg.BOOT_OPTION_SUSE, Msg.BIOS_BOOT_COMPLETE)
            assert (PlatMisc.cscripts_inband_register(cscripts_cmd_cke, exp_list))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def dimm_power_mgt_012():
    tc = ('707', '[TC707]Testcase_MemPower_012', '内存省电模式使能时更改定时器选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    exp_list = ['0x00000001:ddrt_cke_en(24:24)', '0x00000001:ppd_en(09:09)', '0x00000000:apd_en(08:08)', '0x000000ad:cke_idle_timer(07:00)']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.MEM_POWER_ADV)
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        SetUpLib.send_key(Key.F5)
        assert (SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert (SetUpLib.verify_options(Key.DOWN, [['CKE Idle Timer', '\[20\]']], 7))
        SetUpLib.send_key(Key.ENTER)  # Send Enter
        SetUpLib.send_data_enter('255')  # set 255
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.MEM_POWER_ADV)
        assert (SetUpLib.verify_options(Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
        assert (SetUpLib.enter_menu(Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
        assert (SetUpLib.verify_options(Key.DOWN, [['CKE Idle Timer', '\[255\]']], 7))
        assert (SetUpLib.boot_suse_from_bm())
        assert (PlatMisc.cscripts_inband_register(cscripts_cmd_cke, exp_list))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# 检查并打开RMT菜单,重启查看串口是否正常打印RMT数据
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def rmt_menu_test():
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
        key_str = SerialLib.cut_log(Sut.BIOS_COM, SERIAL_RMT_FLAG[0], "Lane Margin", 20, 600)
        logging.debug(key_str)
        assert (SERIAL_RMT_FLAG[0] in key_str)
        assert (SERIAL_RMT_FLAG[1] in key_str)
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
def memory_compa_001():
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
def memory_compa_006(n=1):
    tc = ('710', '[TC710] Testcase_MemoryCompa_006', '06 内存容量一致性测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    for i in range(n):
        res_lst = []
        try:
            assert BmcLib.force_reset()
            meminfo = SerialLib.cut_log(Sut.BIOS_COM, "Total Memory :", "", 3, 300)
            mem_mb = re.search("Total Memory : (\d+)MB", meminfo)
            assert mem_mb, "Search total memory size from serial failed"
            mem_size_ser = int(mem_mb.group(1))
            assert SetUpLib.continue_to_page('BIOS Revision')
            assert SetUpLib.verify_info([f'Total Memory\s+{mem_size_ser} MB'], 20), "dimm_size_verify -> fail"
            assert SetUpLib.back_to_front_page("Boot Manager")
            SetUpLib.send_key(Key.ENTER)
            assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 5, Msg.BIOS_BOOT_COMPLETE)
            assert MiscLib.ping_sut(SutConfig.OS_IP, 200)
            res = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep -i e820')
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
            logging.debug(int(mem_size))
            assert int(mem_size) == mem_size_ser//1024, 'dimm_size_diff_fail'
            result.log_pass()
        except AssertionError as e:
            logging.error(e)
            result.log_fail(capture=True)


# 01 设置动态内存刷新模式功能测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def mem_refresh_001():
    tc = ('711', '[TC711] Testcase_MemRefresh_001', '01 设置动态内存刷新模式功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    exp_list = ['0x00000000:temp_thrt_hyst(26:24)', '0x00000064:temp_hi(23:16)', '0x0000005f:temp_mid(15:08)', '0x00000055:temp_lo(07:00)']
    try:
        assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), "boot_to_page -> fail"
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.MEMORY_CONFIG], 10, Msg.MEM_FRE), "enter_menu -> fail"
        assert SetUpLib.locate_option(Key.DOWN, [Msg.MEM2X_REFRESH, '<Dynamic Mode>'], 10), "locate_option -> fail"
        assert SetUpLib.boot_option_from_bm(Msg.BOOT_OPTION_SUSE, Msg.BIOS_BOOT_COMPLETE)
        assert (PlatMisc.cscripts_inband_register(cscripts_cmd_refresh, exp_list))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# 02 设置静态2X内存刷新模式功能测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def mem_refresh_002():
    tc = ('712', '[TC712] Testcase_MemRefresh_002', '02 设置静态2X内存刷新模式功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    exp_list = ['0x00000000:temp_thrt_hyst(26:24)', '0x00000064:temp_hi(23:16)', '0x0000005f:temp_mid(15:08)', '0x00000000:temp_lo(07:00)']
    try:
        assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), "boot_to_page -> fail"
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.MEMORY_CONFIG], 10, Msg.MEM_FRE), "enter_menu -> fail"
        assert SetUpLib.locate_option(Key.DOWN, [Msg.MEM2X_REFRESH, '<Dynamic Mode>'], 10), "locate_option -> fail"
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y])
        assert SetUpLib.continue_to_boot_suse_from_bm(), "boot_to_os -> fail"
        assert (PlatMisc.cscripts_inband_register(cscripts_cmd_refresh, exp_list))
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# 装备模式下打开RMT并检查串口RMT数据是否正常打印
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def rmt_equip_test():
    tc = ('713', '[TC713]Testcase_MemoryCompa_009', '装备模式内存Margin功能测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
        assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        assert Sut.UNITOOL.set_config(BiosCfg.MFG_RMT), "Change setup by unitool failed."
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
def set_mem_freq_001_006(n=1):
    tc = ('714', '[TC714] Testcase_SetMemFreq_001_006', '01-06 内存频率选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    freq_values = ["Auto", "2666", "2933", "3200"]

    def ddr_boot_freq():
        try:
            dimm_info = SerialLib.cut_log(Sut.BIOS_COM, "START_DIMMINFO_SYSTEM_TABLE", "STOP_DIMMINFO_SYSTEM_TABLE", 20, 300)
            assert dimm_info, "Invalid Dimm info table"
            ddr_freq = re.search("DDR Freq.*?DDR4-(\d+)", dimm_info)
            assert ddr_freq, "Current DDR Freq not found"
            ddr_freq_default = ddr_freq.group(1)
            logging.info("**Current DDR frequency is: {} MHz".format(ddr_freq_default))
            return ddr_freq_default
        except Exception as e:
            logging.error(e)

    try:
        for r in range(n):
            assert BmcLib.force_reset()
            default_freq = ddr_boot_freq()
            assert default_freq
            logging.info("**Check whether supported frequency values are correct.")
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 10, "PPR Type")
            freq_support = SetUpLib.get_all_values("Memory Frequency", Key.DOWN, 5)
            assert MiscLib.same_values(freq_support, freq_values)
            logging.info("**Supported frequency values verified.")
            for freq in ["2666", "3200"]:
                logging.info("**Set memory frequenct to: {0}".format(freq))
                assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
                assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 10, "PPR Type")
                assert SetUpLib.set_option_value("Memory Frequency", freq, save=True)
                logging.info("**Verifying current memory frequency.")
                boot_freq = ddr_boot_freq()
                assert boot_freq
                if freq == "2666":
                    assert boot_freq == freq, f"Set Memory Frequency to {freq} but check boot log mismatch"
                if freq == "3200":
                    assert boot_freq == default_freq, f"Current DDR Freq: {boot_freq} not match with default memory frequency"
                logging.info(f"Check memory freuency match with {freq} Mhz")
                assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# 01 MTRR最大内存地址范围测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def mtrr_max_range():
    tc = ('715', '[TC715] Testcase_MTRR_002', '01 MTRR最大内存地址范围测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_suse_from_bm(), "boot_to_os -> fail"
        res = SshLib.execute_command(Sut.OS_SSH, 'cat /proc/mtrr')
        assert res
        mem_size = re.findall(r"\d+\.?\d*", res.split('=')[2])
        for i in mem_size:
            if int(i) / 1024 == SysCfg.DIMM_SIZE * 2:
                logging.info('MTRR MAX DIMM SIZE Pass')
        result.log_pass()
    except AssertionError:
        logging.info('MTRR MAX DIMM SIZE Fail')
        result.log_fail(capture=True)


# 02 MTRR Fixed ranges测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: SUSE OS
def mtrr_fixed_range():
    tc = ('716', '[TC716] Testcase_MTRR_002', '02 MTRR Fixed ranges测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    flag = []
    try:
        assert BmcLib.force_reset(), 'reset_system -> fail'
        assert not SetUpLib.wait_message('0xa0300', 60), 'find 0xa0300 string'
        assert SetUpLib.boot_option_from_bm(Msg.BOOT_OPTION_SUSE, Msg.BIOS_BOOT_COMPLETE)
        res = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep MTRR')
        assert res
        if 'MTRR fixed ranges enabled' in res:
            logging.info('MTRR fixed ranges enabled')
        else:
            logging.info('MTRR fixed ranges not enabled')
            status = 1
            flag.append(status)
        res_1 = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep A0000')
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
