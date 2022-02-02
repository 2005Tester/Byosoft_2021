import os
if os.path.exists("HY5\ScopeLocal.py"):
    from HY5 import ScopeLocal as TestScope
else:
    from HY5 import Scope as TestScope


# Define test scope for daily test
def DailyTest():
    TestScope.daily_scope()


def WeeklyTest():
    TestScope.weekly_scope()


def ReleaseTest():
    TestScope.release_scope()


def Debug():
    TestScope.debug_scope()


def CheckCsv():
    TestScope.check_csv()
