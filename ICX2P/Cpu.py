from ICX2P import SutConfig
from ICX2P.SutConfig import Key, Msg
from ICX2P.BaseLib import PowerLib, icx2pAPI, SetUpLib
from Report import ReportGen


# Cpu Related Test case, test case ID, 2xx

# Testcase_CPU_COMPA_015, 016 - TBD
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Uncore status page
def upi_link_status(serial, ssh):
    tc = ('026', '[TC026]UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_UNCORE_STATUS, 10, 'Uncore Status'):
        result.log_fail()
        return

    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.upi_state, 4):
        result.log_fail()
        return
    result.log_pass()
    return True
