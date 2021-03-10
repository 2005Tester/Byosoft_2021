import logging
from ICX2P.SutConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib
from Report import ReportGen

# Test case ID: 4xx

##########################################
#            Legacy Test Cases           #
##########################################


def enable_legacy_boot(serial, ssh):
    tc = ('400', 'Enable Legacy Boot', 'Enable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.enable_legacy_boot(serial, ssh):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def disable_legacy_boot(serial, ssh):
    tc = ('401', 'Disable Legacy Boot', 'Disable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.disable_legacy_boot(serial, ssh):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
