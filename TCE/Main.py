import os

if os.path.exists("TCE\ScopeLocal.py"):
    from TCE import ScopeLocal as TestScope
else:
    from TCE import Scope as TestScope


# Define test scope for daily test
def DailyTest():
    TestScope.daily_scope()


def WeeklyTest():
    TestScope.weekly_scope()


def Debug():
    TestScope.debug_scope()


def CheckCsv():
    TestScope.check_csv()
