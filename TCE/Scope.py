from Core.TcExecutor import TestScope
from TCE.Config import SutConfig
from TCE.TestCase import UpdateBIOS, Os
from TCE.BaseLib import PlatMisc


# Supported type (case senstive): Release, Daily, Weekly
def scope(type, branch='master'):
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, type)
    if UpdateBIOS.update_bios(branch):
        if test_scope.os and Os.boot_to_suse():
            test_scope.run_test('os')
        test_scope.run_test('default')
        test_scope.run_test('fulldebug')

    if test_scope.equip and UpdateBIOS.update_bios_mfg(branch):
        test_scope.run_test('equip')


# Define test scope for daily test
def daily_scope():
    # init sut,
    assert PlatMisc.init_tce_sut(), 'bmc ssh -> failed'
    scope("Daily")


# Bascic check for csv test plan file
def check_csv():
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, "Daily")
    test_scope.check_csv()


def debug_scope():
    UpdateBIOS.update_bios('master')
