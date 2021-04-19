import logging
from ICX2P import SutConfig
from ICX2P.SutConfig import Key, Msg, BiosCfg
from ICX2P.BaseLib import SetUpLib
from Report import ReportGen

# Test case ID: TC500-520

##########################################
#            Legacy Test Cases           #
##########################################


def enable_legacy_boot(serial, ssh):
    tc = ('500', 'Enable Legacy Boot', 'Enable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)
    if not SetUpLib.enable_legacy_boot(serial, ssh):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def disable_legacy_boot(serial, ssh):
    tc = ('501', 'Disable Legacy Boot', 'Disable Legacy Boot.')
    result = ReportGen.LogHeaderResult(tc, imgdir=SutConfig.LOG_DIR)
    if not SetUpLib.disable_legacy_boot(serial, ssh):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
