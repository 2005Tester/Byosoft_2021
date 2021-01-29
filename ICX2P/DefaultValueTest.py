import logging
from ICX2P.SutConfig import Key, Msg
from ICX2P import SutConfig
from ICX2P.BaseLib import icx2pAPI, SetUpLib
from Common import Misc


# Test case ID: 1xx

##########################################
####        UNCORE Test Cases        #####    
##########################################

# Testcase_RRQIRQ_001
def rrqirq(serial, ssh):
    tc = ('101', 'Testcase_RRQIRQ_001', 'Setup菜单RRQ和IRQ选项默认值测试')
    result = Misc.LogHeaderResult(tc, serial)
    if not SetUpLib.boot_to_page(serial, Msg.PAGE_ADVANCED, ssh):
        result.log_fail()
        return
    msg = 'Uncore Status'
    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_UNCORE_GENERAL, 20, msg):
        result.log_fail()
        return

    logging.info("Find option and verify default value.")
    if not SetUpLib.locate_option(serial, Key.DOWN, ["Local/Remote Threshold", "<Auto>"], 20):
        result.log_fail()
        return

    logging.info("Verify supported values.")
    values = 'DisabledAutoLowMediumHighManual'
    if not SetUpLib.verify_supported_values(serial, values):
        result.log_fail()
        return
    logging.info("Verify default value of RRQ and IRQ when set to manual.")
    SetUpLib.send_keys(serial, [Key.F5, Key.F5, Key.F5, Key.F5])
    manual_opts = [["IRQ Threshold", "\[7\]"],["RRQ Threshold", "\[7\]"]]
    if not SetUpLib.verify_options(serial, Key.DOWN, manual_opts, 12):
        result.log_fail()
        return

    result.log_pass()
    return True
