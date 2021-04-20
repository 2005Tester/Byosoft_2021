from ICX2P import SutConfig
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import PowerLib, icx2pAPI, SetUpLib
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
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'Disabled_MaxDisabled_Min'):
        result.log_fail()
        return
    result.log_pass()
    return True
