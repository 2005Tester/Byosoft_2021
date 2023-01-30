from batf import var
from batf.TcExecutor import TestScope
from Hygon7500CRB.Config import SutConfig
from Hygon7500CRB.TestCase import UpdateBIOS,Legacy
import os

# Supported type (case senstive): Release, Daily, Weekly
def scope(type, branch='master'):
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, type)
    test_scope.run_test('default')


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
    from Hygon7500CRB.TestCase import UpdateBIOS, SmbiosTest,IpmitoolTest,SetupPasswordTest,CpuTest,PXETest,SmbiosTest,SetUpTest,BootTest,PCIETest,HddPasswordTest
    
