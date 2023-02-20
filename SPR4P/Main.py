import os
from batf import var
from batf.SutInit import Sut
from SPR4P import Collecter
from SPR4P.BaseLib import BmcLib
from SPR4P.Config.PlatConfig import Msg


if os.path.exists("SPR4P\ScopeLocal.py"):
    from SPR4P import ScopeLocal as TestScope
else:
    from SPR4P import Scope as TestScope


def global_config():
    """Workaround for project specific config"""
    Sut.BIOS_COM.set_password(Msg.BIOS_PASSWORD, Msg.PW_PROMPT)
    BmcLib.set_boot_dev(dev=None, once=False)
    BmcLib.debug_message(enable=False)
    Sut.UNITOOL.set_tool_name("uniCfg")
    Sut.UNITOOL_LEGACY_OS.set_tool_name("uniCfg")
    var.set("run_type", "Debug")


# Define test scope for daily test
def DailyTest():
    global_config()
    Collecter.collect_testcase()
    TestScope.daily_scope()


def WeeklyTest():
    global_config()
    Collecter.collect_testcase()
    TestScope.weekly_scope()


def ReleaseTest():
    global_config()
    Collecter.collect_testcase()
    TestScope.release_scope()


def Debug():
    global_config()
    TestScope.debug_scope()


def CheckCsv():
    TestScope.check_csv()
