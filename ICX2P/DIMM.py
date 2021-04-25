# this script just for dimm related test func

import logging
import unittest

from ICX2P import SutConfig
from Report import ReportGen
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, icx2pAPI, PowerLib

# Test case ID: TC700-750

##########################################
#            Release Test Cases          #
##########################################

# 03 支持内存电源管理配置
class dimm_memPower(unittest.TestCase):
    # go to memory frequency page
    def navigate_to_mem_fre(self, serial):
        self.assertTrue(SetUpLib.locate_option(serial, Key.RIGHT, [Msg.PAGE_ADVANCED], 6))
        self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CPU_CONFIG], 12, Msg.PROCESSOR_CONFIG))
        self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEMORY_CONFIG], 12, Msg.MEM_FRE))

    # go to cke power down page
    def navigate_to_cke(self, serial):
        self.assertTrue(SetUpLib.locate_option(serial, Key.RIGHT, [Msg.PAGE_ADVANCED], 6))
        self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CPU_CONFIG], 12, Msg.PROCESSOR_CONFIG))
        self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.ADV_POWER_MGF_CONFIG], 12, Msg.PFM_PRO))
        self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEM_POWER_THER_CONFIG], 12, Msg.DRAM_RAPL_CONFIG))
        self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEM_POWER_ADV], 12, Msg.CKE))

    def dimm_power_mgt_01(self, serial, ssh):
        tc = ('700', 'Testcase_MemPower_001', 'BIOS默认关闭DDR4内存的LP-ASR模式测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            if SetUpLib.verify_info(serial, ['CPU Number\s+2'], 7):
                dimm_memPower.navigate_to_mem_fre(self, serial)
                self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.MEM2X_REFRESH, '<Disabled>']], 7))
            elif SetUpLib.verify_info(serial, ['CPU Number\s+4'], 7):
                dimm_memPower.navigate_to_mem_fre(self, serial)
                self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.MEM2X_REFRESH, '<Extended>']], 7))
            else:
                logging.info('Unsupported CPU Number...')
                raise AssertionError
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def dimm_power_mgt_02(self, serial, ssh):
        tc = ('701', 'Testcase_MemPower_002&3', 'BIOS默认关闭CKE Power Down&Setup菜单提供内存自刷新和CKE Power Down选项测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_mem_fre(self, serial)
            serial.send_keys(Key.ESC)
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.ADV_POWER_MGF_CONFIG], 12, Msg.PFM_PRO))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEM_POWER_THER_CONFIG], 12, Msg.DRAM_RAPL_CONFIG))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEM_POWER_ADV], 12, Msg.CKE))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def dimm_power_mgt_04(self, serial, ssh):
        tc = ('702', 'Testcase_MemPower_004', '打开DDR4内存的LP-ASR模式功能测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.LPASR_MODE, '<Auto SR>']], 7))
            self.assertTrue(SetUpLib.boot_to_bootmanager(serial, ssh))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def dimm_power_mgt_05(self, serial, ssh):
        tc = ('703', 'Testcase_MemPower_005', '打开CKE Power down功能测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
            serial.send_keys_with_delay([Key.F5, Key.F10, Key.Y])
            self.assertTrue(icx2pAPI.toBIOSnp(serial))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
            self.assertTrue(SetUpLib.boot_to_bootmanager(serial, ssh))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
            self.assertTrue(icx2pAPI.ping_sut())
        except AssertionError as err:
            result.log_fail(capture=True)
            return False
        result.log_pass()

    def dimm_power_mgt_07(self, serial, ssh):
        tc = ('704', 'Testcase_MemPower_007', '内存省电模式选项互斥测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
            serial.send_keys(Key.F5)
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Disabled>'], ['PPD', '<Enabled>']], 7))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Disabled>']], 7))
            serial.send_keys(Key.F5)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Enabled>']], 3))
            self.assertFalse(SetUpLib.verify_options(serial, Key.DOWN, [['PPD', '<Enabled>']], 3))
        except AssertionError as err:
            result.log_fail(capture=True)
            icx2pAPI.reset_default(serial, ssh)
            return False
        icx2pAPI.reset_default(serial, ssh)
        result.log_pass()

    def dimm_power_mgt_010(self, serial, ssh_os, ssh_bmc):
        tc = ('705', 'Testcase_MemPower_010', '内存省电模式使能PPD时寄存器状态测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh_bmc))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
            serial.send_keys_with_delay([Key.F5, Key.F10, Key.Y])
            self.assertTrue(icx2pAPI.toBIOSnp(serial))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
            self.assertTrue(SetUpLib.boot_to_bootmanager(serial, ssh_bmc))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
            self.assertTrue(icx2pAPI.ping_sut())
            self.assertTrue(icx2pAPI.rw_everything(ssh_os, SutConfig.CKE_POWER_DOWN, ['c61218a0', 'fb9a18a4']))
        except AssertionError as err:
            result.log_fail(capture=True)
            icx2pAPI.reset_default(serial, ssh_bmc)
            return False
        icx2pAPI.reset_default(serial, ssh_bmc)
        result.log_pass()

    def dimm_power_mgt_011(self, serial, ssh_os, ssh_bmc):
        tc = ('706', 'Testcase_MemPower_011', '内存省电模式使能APD时寄存器状态测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh_bmc))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
            serial.send_keys(Key.F5)
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Disabled>'], ['PPD', '<Enabled>']], 7))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Disabled>']], 7))
            serial.send_keys(Key.F5)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Enabled>']], 3))
            self.assertFalse(SetUpLib.verify_options(serial, Key.DOWN, [['PPD', '<Enabled>']], 3))
            serial.send_keys_with_delay([Key.F10, Key.Y])
            self.assertTrue(icx2pAPI.toBIOSnp(serial))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['APD', '<Enabled>']], 3))
            self.assertTrue(SetUpLib.boot_to_bootmanager(serial, ssh_bmc))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
            self.assertTrue(icx2pAPI.ping_sut())
            self.assertTrue(icx2pAPI.rw_everything(ssh_os, ['c61218a0: 010f 1100 010f 1100 010f 1100 010f 1100 '], ['c61218a0']))
        except AssertionError as err:
            result.log_fail(capture=True)
            icx2pAPI.reset_default(serial, ssh_bmc)
            return False
        icx2pAPI.reset_default(serial, ssh_bmc)
        result.log_pass()

    def dimm_power_mgt_012(self, serial, ssh_os, ssh_bmc):
        tc = ('707', 'Testcase_MemPower_012', '内存省电模式使能时更改定时器选项测试')
        result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
        try:
            self.assertTrue(icx2pAPI.toBIOS(serial, ssh_bmc))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Disabled>']], 7))
            serial.send_keys(Key.F5)
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['CKE Idle Timer', '\[20\]']], 7))
            serial.send_data(chr(0x0D))  # Send Enter
            serial.send_data('255')  # set 255
            serial.send_data(chr(0x0D))  # Send Enter
            serial.send_keys_with_delay([Key.F10, Key.Y])
            self.assertTrue(icx2pAPI.toBIOSnp(serial))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CKE_FEATURE], 12, Msg.CKE_IDLE_TIMER))
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [['CKE Idle Timer', '\[255\]']], 7))
            self.assertTrue(SetUpLib.boot_to_bootmanager(serial, ssh_bmc))
            self.assertTrue(SetUpLib.enter_menu(serial, Key.DOWN, Msg.suse_linux, 12, Msg.suse_linux_msg))
            self.assertTrue(icx2pAPI.ping_sut())
            self.assertTrue(icx2pAPI.rw_everything(ssh_os, ['c61218a0: 02bf 1100 02bf 1100 02bf 1100 02bf 1100 '], ['c61218a0']))
        except AssertionError as err:
            result.log_fail(capture=True)
            icx2pAPI.reset_default(serial, ssh_bmc)
            return False
        icx2pAPI.reset_default(serial, ssh_bmc)
        result.log_pass()


# inst...
DPM = dimm_memPower()


# 检查并打开RMT菜单,重启查看串口是否正常打印RMT数据
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_MemMargin_001(serial, ssh_bmc):
    tc = ('708', '[TC708] Testcase_MemMargin_001', '01 内存margin测试菜单选项测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)

    BSSA_MENU = "BSSA Configuration Menu"
    BSSA_RMT = "BSSA Rank Margin Tool"
    BSSA_RMT_FAST = "BSSA RMT on Fast Cold Boot"
    SERIAL_RMT_FLAG = ["START_BSSA_RMT", "Ctl+"]
    try:
        assert SetUpLib.boot_to_page(serial, ssh_bmc, Msg.PAGE_ADVANCED), "boot_to_page -> fail"
        logging.info("Press Enter")
        serial.send_keys(Key.ENTER)
        assert SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEMORY_CONFIG, BSSA_MENU], 15, BSSA_RMT), "enter_menu >> fail"
        # BSSA Rank Margin Tool: Enable
        assert SetUpLib.locate_option(serial, Key.DOWN, [BSSA_RMT, "<Disabled>"], 15), "locate_option >> fail"
        logging.info("Press F6")
        serial.send_keys(Key.F6)
        assert SetUpLib.verify_options(serial, Key.DOWN, [[BSSA_RMT, "<Enabled>"]], 15), "verify_options >> fail"
        logging.info(f"{BSSA_RMT} -> Enabled")
        # BSSA RMT on Fast Cold Boot: Enable
        assert SetUpLib.locate_option(serial, Key.DOWN, [BSSA_RMT_FAST, "<Disabled>"], 15), "locate_option >> fail"
        logging.info("Press F6")
        serial.send_keys(Key.F6)
        assert SetUpLib.verify_options(serial, Key.DOWN, [[BSSA_RMT_FAST, "<Enabled>"]], 15), "verify_options >> fail"
        logging.info(f"{BSSA_RMT_FAST} -> Enabled")
        # Serial Debug Message: Enable
        assert icx2pAPI.debug_message(ssh_bmc, enable=True), "bmc_debug_message >> fail"
        serial.send_keys(Key.F10 + Key.Y)
        assert serial.waitStrings(SERIAL_RMT_FLAG, timeout=600), "waitStrings >> fail"
        # BIOS load default
        icx2pAPI.debug_message(ssh_bmc, enable=False)
        icx2pAPI.clearCMOS(ssh_bmc)
        PowerLib.force_power_cycle(ssh_bmc)
        serial.is_msg_present(Msg.HOTKEY_PROMPT_DEL)
        result.log_pass()
    except AssertionError as e:
        logging.error(e)
        icx2pAPI.debug_message(ssh_bmc, enable=False)
        icx2pAPI.clearCMOS(ssh_bmc)
        PowerLib.force_power_cycle(ssh_bmc)
        serial.is_msg_present(Msg.HOTKEY_PROMPT_DEL)
        result.log_fail()


# 01 内存初始化测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: BIOS SETUP
def Testcase_MemoryCompa_001(serial, ssh_bmc):
    tc = ('709', '[TC709] Testcase_MemoryCompa_001', '01 内存初始化测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(serial, ssh_bmc, Msg.PAGE_ADVANCED), "boot_to_page -> fail"
        assert SetUpLib.enter_menu(serial, Key.DOWN, [Msg.CPU_CONFIG, Msg.MEMORY_TOP], 15, 'DIMM000\(A\)'), "enter_menu >> fail"
        assert SetUpLib.verify_info(serial, SutConfig.DIMM_info, 20)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)

