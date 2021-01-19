from ICX2P import SutConfig
from ICX2P.SutConfig import Key
from ICX2P.BaseLib import PowerLib, icx2pAPI, SetUpLib
from Common import Misc


# Cpu Related Test case, test case ID, 2xx

# Testcase_CoreDisable_001, 002, 003, 004, 005 and 007
def coreDisable(serial, ssh):
    tc = ('200', 'Setup菜单关核选项测试', '支持CPU关核')
    result = Misc.LogHeaderResult(tc, serial)
    if not icx2pAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option3):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_up(serial, ['<All>\s+Active Processor Cores'], 7):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pat, 'Active Processor Cores'):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.verify_option_value(Key.UP, r'1234567891011121314151617All', timeout=15):
        result.log_fail()
        return
    serial.send_keys(Key.ESC)
    serial.send_keys_with_delay([Key.F6, Key.F6])
    serial.send_keys(Key.F10 + Key.Y)
    if not icx2pAPI.toBIOSnp(serial):
        result.log_fail()
        return
    if not icx2pAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(SutConfig.w2key)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option2, timeout=60):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, SutConfig.option5):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not icx2pAPI.verify_setup_options_up(serial, SutConfig.DIMM_info, 20):
        result.log_fail()
        return
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not icx2pAPI.ping_sut():
        result.log_fail()
        return
#    if not icx2pAPI.chipsecMerge(ssh):
#        result.log_fail()
#        return
#    cmd = 'dmidecode -t 4'
#    path = SutConfig.LOG_DIR
#    icx2pAPI.dump_smbios(ssh, cmd)
#    if not P.smbiosCheck(cmd, path, SutConfig.SMBIOS_TEMPLATE):
#        result.log_fail()
#        return
    result.log_pass()
    return True
