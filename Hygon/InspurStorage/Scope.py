from batf import var
from batf.TcExecutor import TestScope
from InspurStorage.Config import SutConfig
from InspurStorage.TestCase import UpdateBIOS
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
    scope("Release")



# Bascic check for csv test plan file
def check_csv():
    test_scope = TestScope(SutConfig.Env.TESTCASE_CSV, "Daily")
    test_scope.check_csv()



def debug_scope():
    pass
