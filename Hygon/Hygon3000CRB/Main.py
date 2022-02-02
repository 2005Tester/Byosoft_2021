import os
if os.path.exists("Hygon3000CRB\ScopeLocal.py"):
    from Hygon3000CRB import ScopeLocal as TestScope
else:
    from Hygon3000CRB import Scope as TestScope


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
                