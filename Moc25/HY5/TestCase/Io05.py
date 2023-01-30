# this script just for hotkey related function test
import logging
import os
import re
from HY5.Config import SutConfig
from HY5.Config.PlatConfig import Key, Msg
from HY5.BaseLib import SetUpLib, BmcLib
from batf import SerialLib, MiscLib, core
from batf.SutInit import Sut

# Test case ID: TC800-850

'''
function module, do not call, only used below,
'''


def check_info():
    FW_VER = BmcLib.firmware_version_check()
    check_list = [Msg.RC_VERSION, Msg.BIOS_REVISION, Msg.BIOS_DATE, FW_VER.BMC, SutConfig.Env.BMC_IP, Msg.CPU_TYPE,
                  Msg.TOTAL_MEMORY, Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F11,
                  Msg.HOTKEY_PROMPT_F12]
    capture_start = "STOP_DIMMINFO_SYSTEM_TABLE"
    capture_end = "Press F6 go to SP boot"
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, 120, 150)
        assert MiscLib.verify_msgs_in_log(check_list, log_cut)
        return True
    except AssertionError:
        return False


def hotkey_press():
    flag_sendkey = Msg.HOTKEY_PROMPT_DEL
    failures = 0
    del_pressed = 'Del is pressed. Go to Setup Utility'
    f11_pressed = 'F11 is pressed. Go to BootManager'
    f12_pressed = 'F12 is pressed. Go to PXE boot'
    f6_pressed = 'F6 is pressed. Go to SP boot'

    key_msg = [
        (Key.DEL, del_pressed),
        (Key.F11, f11_pressed),
        (Key.F12, f12_pressed),
        (Key.F6, f6_pressed)
    ]

    for check_item in key_msg:
        logging.info('**Testing: {0}'.format(check_item[1]))
        try:
            BmcLib.force_reset()
            assert SetUpLib.wait_message(flag_sendkey, 180)
            SetUpLib.send_key(check_item[0])
            assert SetUpLib.wait_message(check_item[1])
            logging.info('**Test pass.')
        except AssertionError:
            failures += 1
            logging.info('**Test fail.')

    if failures == 0:
        return True
    else:
        logging.info("{0} test failed".format(failures))
        return False


def log_Time(log_n):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600) #考虑全打印
        logging.info("Suse_OS Boot Successful")
        SERIAL_LOG = os.path.join(SutConfig.Env.LOG_DIR, 'TC{}.log'.format(log_n))
        res = [x.strip() for x in open(SERIAL_LOG, 'r').readlines() if x.strip() != '']
        s_cont = 0
        for s_str in SutConfig.Env.LogTime_Dedicated + Msg.LogTime_common:
            logging.info('check ： {}'.format(s_str))
            if not s_str in str(res):
                if not re.search(r"\d+",s_str):
                    s_cont = s_cont + 1
                    logging.info('**{} -- no found**'.format(s_str))
                    return False
        if s_cont == 0:
            logging.info('All check pass')
            return True
    except AssertionError as e:
        logging.error(e)
        return False


def bt_logTime(timeout = 60):
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('DB 07 00 05 10 01', timeout):
        core.capture_screen()
        return False
    return True

##########################################
#            Release Test Cases          #
##########################################


# Author: Fubaolin
# Testcase_LogTime_001, 003 串口日志打印
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
@core.test_case(('800', '[TC800] 串口日志打印测试01_03', '【UEFI模式】支持BIOS启动开始和结束信息打印及上报'))
def Testcase_LogTime_01_03():
    try:
        assert SetUpLib.boot_suse_from_bm()
        assert log_Time('800')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        return core.Status.Fail


