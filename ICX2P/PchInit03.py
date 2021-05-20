import os
import re
import logging
from Core import var
from Core.SutInit import Sut
from Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.Config.SutConfig import SysCfg
from ICX2P.BaseLib import SetUpLib, PlatMisc, BmcLib
from Core import SerialLib


# Test case ID: TC600-TC620

##########################################
#           PCH Test Cases          #
##########################################


# POST阶段检查串口log是否有打印GPIO错误
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def post_gpio_error_check():
    tc = ('600', '[TC600] Testcase_GPIO_002', '02 BIOS启动阶段GPIO初始化测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert BmcLib.debug_message(enable=True), "debug message enable fail"
        assert BmcLib.force_power_cycle(), "force_power_cycle fail"
        assert SerialLib.is_msg_present(Sut.BIOS_COM, msg=Msg.BIOS_BOOT_COMPLETE, delay=600), "boot up fail"
        assert os.path.isfile(var.get('serial_log')), "Invalid serial log"
        with open(var.get('serial_log'), 'r') as ser_log:
            ser_data = ser_log.read()
        assert (Msg.GPIO_ERR not in ser_data), "Found GPIO Error, test failed"
        logging.info(f"No '{Msg.GPIO_ERR}' found in serial log, test pass")
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        result.log_fail()
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# 检查确认USB每个分组下面的Port默认为Enable
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def usb_default_enable_check():
    tc = ('601', '[TC601] Testcase_USB_Port_001', '01 Setup菜单默认打开USB Port选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    rear_usb = rf"Rear USB Control(?:\s+<Enabled>\s+USB Physical Port\d+){{{SysCfg.REAR_USB_CNT}}}"
    buildin_usb = rf"Built-in USB Control(?:\s+<Enabled>\s+USB Physical Port\d+){{{SysCfg.BUILDIN_USB_CNT}}}"
    key_words = f"{rear_usb}.+{buildin_usb}"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_USB_CFG, 6, "USB")
        if SetUpLib.verify_info([rear_usb, buildin_usb], 10):
            result.log_pass()  # return pass if verify_info match
            return True
        assert os.path.isfile(var.get('serial_log')), "Invalid serial log"
        logging.info(f"Check local serial log: {var.get('serial_log')}")
        with open(var.get('serial_log'), 'r') as ser_log:  # check serial log in case of no enough temporary read buffer
            ser_data = ser_log.read()
        assert re.search(key_words, ser_data), "USB strings not match, test fail"
        logging.info("USB key words found in local serial log, test pass")
        result.log_pass()
        return True
    except AssertionError as e:
        logging.info(e)
        result.log_fail()


# Testcase_SATA_Hot_Plug_001 检查SATA与sSATA的所有Port中的Hot Plug选项都为Enable
# Precondition:
# OnStart:
# OnComplete: SetUp
def hot_plug_sata():
    tc = ('602', 'Verify SATA/sSATA Information', 'Verify Hot Plug Enable')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    PATH_SATA_CFG = ['PCH Configuration', 'PCH Configuration']
    PATH_sSATA_CFG = ['PCH Configuration', 'PCH sSATA Configuration']
    Hot_Plug_Info = ['<Disabled>\s+Hot Plug']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, PATH_SATA_CFG, 20, 'PCH SATA Configuration')
        logging.info("**Verify SATA Hot Plug Information**")
        assert not SetUpLib.verify_info(Hot_Plug_Info, 20)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, PATH_sSATA_CFG, 20, 'PCH SATA Configuration')
        logging.info("**Verify sSATA Hot Plug Information**")
        assert not SetUpLib.verify_info(Hot_Plug_Info, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)

# Testcase_Spin_Up_001使用unitool确认SataSpinUp的默认值为Enable
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: Os
def testcase_spin_up_001(unitool):
    tc = ('603', 'Verify SataSpinUp GetVariable value is 1', 'Verify value is 1')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_suse_from_bm()
        assert PlatMisc.ping_sut()
        assert unitool.check(SataSpinUp=1)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)