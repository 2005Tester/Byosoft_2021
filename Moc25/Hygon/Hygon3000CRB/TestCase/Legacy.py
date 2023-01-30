import logging
from Hygon3000CRB.BaseLib import SetUpLib, BmcLib
from batf import MiscLib
from batf.Report import ReportGen
# Test case ID: TC500-520



##########################################
#            Legacy Test Cases           #
##########################################



def enable_legacy_boot():
    tc = ('500', '[TC500] Enable Legacy Boot', 'Enable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.enable_legacy_boot():
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True



def disable_legacy_boot():
    tc = ('501', '[TC501] Disable Legacy Boot', 'Disable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.disable_legacy_boot():
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True



# Author: WangQingshan
# 启动到Legacy OS并检查dmesg没有错误
# Precondition: 依赖 enable_legacy_boot()
# OnStart: Legacy Mode
# OnComplete: NA