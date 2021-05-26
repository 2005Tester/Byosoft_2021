import os
if os.path.exists("ICX2P\ScopeLocal.py"):
    from ICX2P import ScopeLocal as TestScope
else:
    from ICX2P import Scope as TestScope


# Define test scope for daily test
def DailyTest():
    TestScope.daily_scope()


def ReleaseTest():
    TestScope.release_scope()


def Debug():
    TestScope.debug_scope()
