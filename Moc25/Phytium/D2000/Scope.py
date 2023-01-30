from D2000.BaseLib.Report import TestcaseScope
from D2000.Config import SutConfig


# Supported type (case senstive): Release, Daily, Weekly
def scope(type, branch='master'):
    test_scope = TestcaseScope(SutConfig.Env.TESTCASE_CSV, type)
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
