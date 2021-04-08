# this script just for dimm related test func

import logging
import unittest

from ICX2P import SutConfig
from Report import ReportGen
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, icx2pAPI


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
            if SetUpLib.verify_info(serial, Key.DOWN, ['CPU Number\s+2'], 7):
                dimm_memPower.navigate_to_mem_fre(self, serial)
                self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.MEM2X_REFRESH, '<Disabled>']], 7))
            elif SetUpLib.verify_info(serial, Key.UP, ['CPU Number\s+4'], 7):
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
            serial.send_keys(Key.CTRL_ALT_DELETE)
            self.assertTrue(icx2pAPI.ping_sut())
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
            self.assertTrue(icx2pAPI.toBIOSnp(serial, ssh))
            self.assertTrue(icx2pAPI.toBIOSConf(serial))
            dimm_memPower.navigate_to_cke(self, serial)
            self.assertTrue(SetUpLib.verify_options(serial, Key.DOWN, [[Msg.CKE, '<Enabled>']], 7))
            serial.send_keys(Key.CTRL_ALT_DELETE)
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
            return False
        result.log_pass()


# inst...
DPM = dimm_memPower()
