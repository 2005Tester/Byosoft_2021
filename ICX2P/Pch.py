import os
import re
import logging
from Report import ReportGen
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.Config.SutConfig import SysCfg
from ICX2P.BaseLib import SetUpLib, icx2pAPI, PowerLib
from Core import SerialLib


# Test case ID: TC600-TC620

##########################################
#           PCH Test Cases          #
##########################################


# POST阶段检查串口log是否有打印GPIO错误
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def post_gpio_error_check(serial, ssh_bmc):
    tc = ('600', '[TC600] Testcase_GPIO_002', '02 BIOS启动阶段GPIO初始化测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        assert icx2pAPI.debug_message(ssh_bmc, enable=True), "debug message enable fail"
        assert PowerLib.force_power_cycle(ssh_bmc), "force_power_cycle fail"
        assert SerialLib.is_msg_present(serial, msg=Msg.BIOS_BOOT_COMPLETE, delay=600), "boot up fail"
        assert os.path.isfile(SutConfig.SERIAL_LOG), "Invalid serial log"
        with open(SutConfig.SERIAL_LOG) as ser_log:
            ser_data = ser_log.read()
        assert (Msg.GPIO_ERR not in ser_data), "Found GPIO Error, test failed"
        logging.info(f"No '{Msg.GPIO_ERR}' found in serial log, test pass")
        assert icx2pAPI.debug_message(ssh_bmc, enable=False), "debug message disable fail"
        assert PowerLib.force_power_cycle(ssh_bmc), "force_power_cycle fail"
        assert SerialLib.is_msg_present(serial, msg=Msg.BIOS_BOOT_COMPLETE), "boot up fail"
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        result.log_fail()


# 检查确认USB每个分组下面的Port默认为Enable
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def usb_default_enable_check(serial, ssh_bmc):
    tc = ('601', '[TC601] Testcase_USB_Port_001', '01 Setup菜单默认打开USB Port选项测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    rear_usb = rf"Rear USB Control(?:\s+<Enabled>\s+USB Physical Port\d+){{{SysCfg.REAR_USB_CNT}}}"
    buildin_usb = rf"Built-in USB Control(?:\s+<Enabled>\s+USB Physical Port\d+){{{SysCfg.BUILDIN_USB_CNT}}}"
    key_words = f"{rear_usb}.+{buildin_usb}"
    try:
        assert SetUpLib.boot_to_page(ssh_bmc, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_USB_CFG, 6, "USB")
        if SetUpLib.verify_info([rear_usb, buildin_usb], 10):
            result.log_pass()  # return pass if verify_info match
            return True
        assert os.path.isfile(SutConfig.SERIAL_LOG), "Invalid serial log"
        logging.info(f"Check local serial log: {SutConfig.SERIAL_LOG}")
        with open(SutConfig.SERIAL_LOG) as ser_log:  # check serial log in case of no enough temporary read buffer
            ser_data = ser_log.read()
        assert re.search(key_words, ser_data), "USB strings not match, test fail"
        logging.info("USB key words found in local serial log, test pass")
        result.log_pass()
        return True
    except AssertionError as e:
        logging.info(e)
        result.log_fail()
