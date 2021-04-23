import os
import logging
from ICX2P import SutConfig
from Report import ReportGen
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, icx2pAPI, PowerLib, SerialLib


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
