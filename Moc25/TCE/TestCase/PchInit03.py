import os
import re
import logging
from batf import var
from batf.SutInit import Sut
from batf.Report import ReportGen
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Key, Msg
from TCE.Config.SutConfig import SysCfg
from TCE.BaseLib import SetUpLib, BmcLib
from batf import SerialLib, MiscLib


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
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert BmcLib.debug_message(enable=True), "debug message enable fail"
        assert BmcLib.force_reset()
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


# Testcase_SATA_Hot_Plug_001 检查SATA与sSATA的所有Port中的Hot Plug选项都为Enable
# Precondition:
# OnStart:
# OnComplete: SetUp
def hot_plug_sata():
    tc = ('602', '[TC602] Verify SATA/sSATA Information', 'Verify Hot Plug Enable')
    result = ReportGen.LogHeaderResult(tc)
    PATH_SATA_CFG = ['PCH Configuration', 'PCH SATA Configuration']
    Hot_Plug_Info = ['<Disabled>\s+Hot Plug']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, PATH_SATA_CFG, 20, 'PCH SATA Configuration')
        logging.info("**Verify SATA Hot Plug Information**")
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
def testcase_spin_up_001():
    tc = ('603', '[TC603] Verify SataSpinUp GetVariable value is 1', 'Verify value is 1')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(SataSpinUp=1)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)
