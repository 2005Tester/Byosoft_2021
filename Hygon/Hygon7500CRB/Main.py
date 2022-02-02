import os
if os.path.exists("Hygon\ScopeLocal.py"):
    from Hygon7500CRB import ScopeLocal as TestScope
else:
    from Hygon7500CRB import Scope as TestScope


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
                