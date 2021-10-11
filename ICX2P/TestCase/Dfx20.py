import logging

from Core import MiscLib, SshLib, SutInit
from Report import ReportGen
from ICX2P.BaseLib import SetUpLib, BmcLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg


# Test case ID: TC071-TC090 - arthur

##########################################
#         DFX Test Cases                 #
##########################################


# common cnd test steps,
def cnd_test_step(value, key):
    dev_list = []  # verify the order of dev in OS
    assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), 'failed to Setup'
    assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 20, Msg.CDN), 'failed to navigate to CDN'
    assert SetUpLib.set_option_value(Msg.CDN, value, key, save=True), 'set value ->failed'
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300), 'failed to ping os'
    res = SshLib.execute_command(SutInit.Sut.OS_SSH, 'dmidecode -t 41')
    if value == "Enabled":
        assert 'Ethernet' in res, 'not found network device - {0}'.format(logging.debug(res))
    else:
        assert 'Ethernet' not in res, 'found network device- {0}'.format(logging.debug(res))
    res1 = SshLib.execute_command(SutInit.Sut.OS_SSH, 'ip addr')
    for i in str(res1).split(':'):
        if len(i) <= 5 and 'eth' in i:
            dev_list.append(i.strip(' '))
    logging.debug(dev_list)
    assert SutConfig.Env.OS_IP in res1 \
           and dev_list == SutConfig.SysCfg.device_order, 'check network device order failed'

    return True


# 01 支持网口CDN特性开关, arthur
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: POWER OFF
def cnd_support_test01():
    tc = ('071', '[TC071] Testcase_CDN_Support_001&002', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert cnd_test_step('Disabled', Key.DOWN)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


def cnd_support_test02():
    tc = ('072', '[TC072] Testcase_CDN_Support_004&005', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert cnd_test_step('Enabled', Key.UP)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


def vgaErr_to_bmc():
    tc = ('073', '[TC073] Testcase_VgaErrReportToBMC_002', '02 VGA正常不上报BMC')
    result = ReportGen.LogHeaderResult(tc)
    assert SetUpLib.boot_to_setup()
    res = BmcLib.bmc_warning_check().message
    if 'VGA' in res:
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def testcase_spcr_001():
    tc = ('074', '[TC074] Testcase_Spcr_001', '01 Setup菜单提供OS串口重定向选项测试')
    result = ReportGen.LogHeaderResult(tc)
    assert SetUpLib.boot_to_page(Msg.CPU_CONFIG), 'failed to Setup'
    assert SetUpLib.enter_menu(Key.DOWN, [Msg.Console_CONFIG], 20, Msg.Console_REDIR), 'failed to navigate to CDN'
    if not SetUpLib.locate_option(Key.UP, [Msg.SPCR, "<Enabled>"], 12):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
