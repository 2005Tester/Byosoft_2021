import logging
from HY5.BaseLib import SetUpLib
from HY5.Config.PlatConfig import Key, Msg
from batf.Report import ReportGen


# Test case ID: TC100-150

##########################################
#        UNCORE Test Cases               #
##########################################

# Testcase_RRQIRQ_001
def rrqirq():
    tc = ('300', '[TC300] Testcase_RRQIRQ_001', 'Setup菜单RRQ和IRQ选项默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_GENERAL, 20, 'Uncore Status')
        logging.info("Find option and verify default value.")
        assert SetUpLib.locate_option(Key.DOWN, ["Local/Remote Threshold", f"<.+>"], 20)
        logging.info("Verify supported values.")
        values = 'DisabledAutoLowMediumHighManual'
        assert SetUpLib.verify_supported_values(values)
        logging.info("Verify default value of RRQ and IRQ when set to manual.")
        assert SetUpLib.set_option_value("Local/Remote Threshold", 'Manual')
        manual_opts = [["IRQ Threshold", "\[7\]"], ["RRQ Threshold", "\[7\]"]]
        assert SetUpLib.verify_options(Key.DOWN, manual_opts, 12)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
