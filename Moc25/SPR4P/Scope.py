from batf import var
from batf.TcExecutor import TestScope
from SPR4P.Config import SutConfig
from SPR4P.Config.PlatConfig import Msg
from SPR4P.TestCase import UpdateBIOS, Legacy
from SPR4P.BaseLib import SetUpLib, PlatMisc


# Supported type (case senstive): Release, Daily, Weekly
def scope(run_type, branch=SutConfig.Env.BRANCH_LATEST):
    var.set("run_type", run_type)
    csv_file = SutConfig.Env.TESTCASE_CSV
    if var.get("test_csv"):
        csv_file = var.get("test_csv")
    test_scope = TestScope(csv_file, run_type)
    if UpdateBIOS.update_bios(branch):
        if test_scope.os and SetUpLib.boot_os_from_bm():
            PlatMisc.set_rtc_time_linux(time_str=None)  # 测试开始之前, 将RTC时间与SUT时间同步
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
    release_branch = SutConfig.Env.BRANCH_RELEASE
    var.set('branch', release_branch)
    scope("Release", release_branch)


# Bascic check for csv test plan file
def check_csv():
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, "Daily")
    test_scope.check_csv()


def debug_scope():
    import SPR4P.TestCase as test
    test.Testcase_HelpInfo_005()

