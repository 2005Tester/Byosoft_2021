from batf import var, SshLib, SutInit
from batf.TcExecutor import TestScope
from SPR4P.Config import SutConfig
from SPR4P.TestCase import UpdateBIOS, Os, Legacy


# Supported type (case senstive): Release, Daily, Weekly
def scope(type, branch='master'):
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, type)
    # set boot option to none,
    SshLib.execute_command(SutInit.Sut.BMC_SSH, 'ipmcset -d bootdevice -v 0 permanent')
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
    release_branch = SutConfig.Env.RELEASE_BRANCH
    var.set('branch', release_branch)
    scope("Release", release_branch)


# Bascic check for csv test plan file
def check_csv():
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, "Daily")
    test_scope.check_csv()


def debug_scope():
    from SPR4P.TestCase import VariableLoop, RedfishTest
    VariableLoop.test_variable_loop()
    RedfishTest.redfish_default_value_test()
    RedfishTest.redfish_post_load_default_test()
    RedfishTest.redfish_non_dependency_test()
    RedfishTest.redfish_dependency_test()
