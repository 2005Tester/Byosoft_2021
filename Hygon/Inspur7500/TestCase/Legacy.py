# -*- encoding=utf8 -*-
from Inspur7500.BaseLib import SetUpLib, BmcLib
from batf.Report import ReportGen


# Test case ID: TC901-020

##########################################
#            Legacy Test Cases           #
##########################################


def enable_legacy_boot():
    tc = ('1', '[TC1] Enable Legacy Boot', 'Enable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.enable_legacy_boot():
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def disable_legacy_boot():
    tc = ('2', '[TC2] Disable Legacy Boot', 'Disable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.disable_legacy_boot():
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
