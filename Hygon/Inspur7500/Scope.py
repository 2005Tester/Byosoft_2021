from batf import var
from Inspur7500.Config import SutConfig
from Inspur7500.TestCase import Legacy, HddPasswordTest
from Inspur7500.BaseLib.Report import TestcaseScope
from Inspur7500.BaseLib import Report


# Supported type (case senstive): Release, Daily, Weekly
def scope(run_type):
    var.set("run_type", run_type)
    csv_file = var.get('test_csv') if var.get('test_csv') else SutConfig.Env.TESTCASE_CSV
    test_scope = TestcaseScope(csv_file, run_type)
    test_scope.run_test('default')
    if test_scope.legacy and Legacy.enable_legacy_boot():
        test_scope.run_test('legacy')
        Legacy.disable_legacy_boot()
        Report.gen_report()
    if test_scope.equip:
        HddPasswordTest.set_hash_type('type1')
        test_scope.run_test('equip')
        HddPasswordTest.set_hash_type('type2')
        test_scope.run_test('equip')


# Define test scope for daily test
def daily_scope():
    scope("Daily")


# Entry for weekly test
def weekly_scope():
    scope("Weekly")


def release_scope():
    scope("Release")


# Bascic check for csv test plan file
def check_csv():
    test_scope = TestcaseScope(SutConfig.Env.TESTCASE_CSV, "Daily")
    test_scope.check_csv()


def debug_scope():
    pass
