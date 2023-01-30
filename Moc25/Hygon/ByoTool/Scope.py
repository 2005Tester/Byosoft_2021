from batf import var

from ByoTool.BaseLib.Report import TestcaseScope
from ByoTool.Config import SutConfig


# Supported type (case senstive): Release, Daily, Weekly
def scope(run_type):
    var.set("run_type", run_type)
    csv_file = var.get('test_csv') if var.get('test_csv') else SutConfig.Env.TESTCASE_CSV
    test_scope = TestcaseScope(csv_file, run_type)
    test_scope.run_test('default')


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
