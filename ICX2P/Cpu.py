import logging
from Core import SerialLib
from ICX2P import SutConfig
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import icx2pAPI, SetUpLib
from Report import ReportGen


# Cpu Related Test case, test case ID, TC200-299

##########################################
#              CPU Test Cases            #
##########################################

# Testcase_CPU_COMPA_015, 016 - TBD
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Uncore status page
def upi_link_status(serial, ssh):
    tc = ('200', '[TC200]UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc, serial)

    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_UNCORE_STATUS, 22, 'Uncore Status'):
        result.log_fail()
        return

    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.upi_state, 4):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_UFS_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup P-State control page
def ufs_default_value(serial, ssh):
    tc = ('201', '[TC201]Testcase_UFS_001', 'UFS默认值测试')
    result = ReportGen.LogHeaderResult(tc, serial)

    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE):
        result.log_fail()
        return

    if not icx2pAPI.verify_setup_options_up(serial, SutConfig.ufs, 4):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ESC, Key.ENTER])
    if not SetUpLib.locate_option(serial, Key.DOWN, ["UFS", "<Enabled>"], 12):
        result.log_fail()
        return
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, r'Disabled_MaxDisabled_Min', 10):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_Static_Turbo_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Advanced power management page
def static_turbo_default(serial, ssh):
    tc = ('202', '[202]Testcase_Static_Turbo_001', '静态Turbo默认值测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    static_turbo_default = ['Static Turbo', '<Disabled>']
    try:
        assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_ADV_PM_CFG, 20, Msg.ADV_POWER_MGF_CONFIG)
        assert SetUpLib.locate_option(serial, Key.DOWN, static_turbo_default, 10)
        SerialLib.send_key(serial, Key.ENTER)
        assert SerialLib.is_msg_present(serial, r'AutoManualDisabled')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU and DIMM information
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Memory Topology Page
def cpu_mem_info(serial, ssh):
    tc = ('203', '[203]CPU Memory Information', 'Verify CPU and Memory Information')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_PER_CPU_INFO, 20, 'BSP Revision')
        logging.info("**Verify CPU Information**")
        assert SetUpLib.verify_info(serial, SutConfig.CPU_info, 20)
        SerialLib.send_keys_with_delay(serial, [Key.ESC, Key.ESC])
        assert SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        logging.info("**Verify Memory Information**")
        assert SetUpLib.verify_info(serial, SutConfig.DIMM_info, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)
