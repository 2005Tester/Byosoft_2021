from Core import SutInit
from Core import var
from Core.TcExecutor import TestScope
from ICX2P.Config import SutConfig
from ICX2P.TestCase import UpdateBIOS, BiosTest, Os, Legacy, CpuInit01, BootDevice06

# init SUT
SutInit.SutInit("ICX2P")


# Supported type (case senstive): Release, Daily, Weekly
def scope(type, branch='master'):
    test_scope = TestScope(SutConfig.TESTCASE_CSV, type)
    if UpdateBIOS.update_bios(branch):
        if test_scope.os and Os.boot_to_suse():
            test_scope.run_test('os')
        test_scope.run_test('default')
        test_scope.run_test('fulldebug')

    if test_scope.legacy and Legacy.enable_legacy_boot():
        test_scope.run_test('legacy')
        Legacy.disable_legacy_boot()

    if test_scope.equip and UpdateBIOS.update_bios_mfg(branch):
        test_scope.run_test('equip')


# Define test scope for daily test
def daily_scope():
    scope("Daily")


# Entry for weekly test
def weekly_scope():
    scope("Weekly")


def release_scope():
    """Release Basic Function Test"""
    release_branch = "2288V6_012"
    var.set('branch', release_branch)
    scope("Release", release_branch)


# Bascic check for csv test plan file
def check_csv():
    test_scope = TestScope(SutConfig.TESTCASE_CSV, "Daily")
    test_scope.check_csv()


def debug_scope():
    UpdateBIOS.update_bios('master')
    CpuInit01.cpu_mem_info()
    BiosTest.power_efficiency_mode_loop()
    BootDevice06.boot_order_001()
    BootDevice06.boot_order_003()
    BootDevice06.boot_order_004()
    BootDevice06.boot_order_005()
