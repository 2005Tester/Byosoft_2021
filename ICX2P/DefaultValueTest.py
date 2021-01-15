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
    tc = ('101', 'Testcase_RRQIRQ_001 Setup菜单RRQ和IRQ选项默认值测试', '支持RRQ&IRQ设置')
    result = Misc.LogHeaderResult(tc, serial)

    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED, serial, ssh):
        result.log_fail()
        return
    msg = 'Uncore Status'
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_GENERAL, 20, msg, serial):
        result.log_fail()
        return

    if not SetUpLib.locate_option(Key.DOWN, ["Local/Remote Threshold", "Auto"], 20, serial):
        result.log_fail()
        return

    values = 'DisabledAutoLowMediumHighManual'
    if not SetUpLib.verify_supported_values(values, serial):
        result.log_fail()
        return
    result.log_pass()
    return True

"""        
#    if not icx2pAPI.toBIOS(serial, ssh):
#        result.log_fail()
#        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option9, timeout=30):
        result.log_fail()
        return
    serial.send_data(chr(0x0D))
    if not serial.find_setup_option(Key.DOWN, SutConfig.option12, 3):
        result.log_fail()
        return
    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.local_remote, 12):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pat, 'Local/Remote Threshold', timeout=60):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.DOWN, r'DisabledAutoLowMediumHigh'):
        result.log_fail()
        return
    # not supported with current release bios, comfired with BIOS dev, TBD
    # serial.send_keys(Key.ESC)
    # serial.send_keys_with_delay([Key.F5, Key.F5, Key.F5, Key.F5])
    # if not icx2pAPI.verify_setup_options_down(serial, ['\[7\]\s+IRQ Threshold', '\[7\]\s+RRQ Threshold'], 12):
    #     result.log_fail()
    #     return
    # serial.send_keys(Key.ESC)
    # serial.send_keys(Key.ENTER)
    # if not serial.to_highlight_option(Key.DOWN, SutConfig.pat, 'IRQ Threshold', timeout=60):
    #     result.log_fail()
    #     return
    # serial.send_keys(Key.ENTER)
    # serial.send_data('10')
    # serial.send_keys_with_delay([Key.ENTER, Key.DOWN, Key.ENTER])
    # serial.send_data('20')
    # serial.send_keys(Key.ENTER)
    # serial.send_keys(Key.F10 + Key.Y)
    # if not icx2pAPI.toBIOSnp(serial):
    #     result.log_fail()
    #     return
    # if not icx2pAPI.toBIOSConf(serial):
    #     result.log_fail()
    #     return
    # serial.send_keys_with_delay(SutConfig.w2key)
    # if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
    #     result.log_fail()
    #     return
    # serial.send_keys(Key.ENTER)
    # if not serial.to_highlight_option(Key.DOWN, SutConfig.option9, timeout=30):
    #     result.log_fail()
    #     return
    # serial.send_keys(Key.ENTER)
    # if not serial.find_setup_option(Key.DOWN, SutConfig.option12, 3):
    #     result.log_fail()
    #     return
    # if not icx2pAPI.verify_setup_options_down(serial, ['\[10\]\s+IRQ Threshold', '\[20\]\s+RRQ Threshold'], 12):
    #     result.log_fail()
    #     return
    result.log_pass()
    return True

"""   
