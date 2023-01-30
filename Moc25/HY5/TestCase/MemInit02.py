# this script just for dimm related test func

import logging
from batf.SutInit import Sut
from batf.Report import ReportGen
from HY5.Config.PlatConfig import Key, Msg
from HY5.BaseLib import SetUpLib, BmcLib
from batf import SerialLib, SshLib, MiscLib, core

# Test case ID: TC700-750

##########################################
#            Release Test Cases          #
##########################################

'''
function module, only used below
'''


# go to memory frequency page
def navigate_to_mem_fre():
    try:
        assert SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 6)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 12, Msg.MEM_FRE)
        return True
    except AssertionError:
        logging.info("navigate_to_mem_fre: Fail")


# go to cke power down page
def navigate_to_cke():
    try:
        assert SetUpLib.locate_option(Key.RIGHT, [Msg.PAGE_ADVANCED], 6)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_POWER_ADV, 12, Msg.CKE)
        return True
    except AssertionError:
        logging.info("navigate_to_cke: Fail")


# 检查并打开RMT菜单,重启查看串口是否正常打印RMT数据
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def rmt_menu_test():
    tc = ('600', '[TC600] Testcase_MemMargin_001', '01 内存margin测试菜单选项测试')
    result = ReportGen.LogHeaderResult(tc)

    BSSA_MENU = "BSSA Configuration Menu"
    BSSA_RMT = "BSSA Rank Margin Tool"
    BSSA_RMT_FAST = "BSSA RMT on Fast Cold Boot"
    SERIAL_RMT_FLAG = ["START_BSSA_RMT", "Ctl+"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED), "boot_to_page -> fail"
        logging.info("Press Enter")
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_CONFIG, BSSA_MENU], 15, BSSA_RMT), "enter_menu >> fail"
        # BSSA Rank Margin Tool: Enable
        assert SetUpLib.locate_option(Key.DOWN, [BSSA_RMT, "<Disabled>"], 15), "locate_option >> fail"
        logging.info("Press F6")
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.verify_options(Key.DOWN, [[BSSA_RMT, "<Enabled>"]], 15), "verify_options >> fail"
        logging.info(f"{BSSA_RMT} -> Enabled")
        # BSSA RMT on Fast Cold Boot: Enable
        assert SetUpLib.locate_option(Key.DOWN, [BSSA_RMT_FAST, "<Disabled>"], 15), "locate_option >> fail"
        logging.info("Press F6")
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.verify_options(Key.DOWN, [[BSSA_RMT_FAST, "<Enabled>"]], 15), "verify_options >> fail"
        logging.info(f"{BSSA_RMT_FAST} -> Enabled")
        # Serial Debug Message: Enable
        assert BmcLib.debug_message(enable=True), "bmc_debug_message >> fail"
        SetUpLib.send_keys(Key.SAVE_RESET, 2)
        key_str = SerialLib.cut_log(Sut.BIOS_COM, SERIAL_RMT_FLAG[0], "Lane Margin", 20, 1200)  # full dimm population delay
        logging.debug(key_str)
        assert (SERIAL_RMT_FLAG[0] in key_str)
        assert (SERIAL_RMT_FLAG[1] in key_str)
        result.log_pass()
    except AssertionError as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()
