import logging
from ICX2P.Config import SutConfig
from ICX2P.BaseLib import SetUpLib, BmcLib, PlatMisc
from Core import MiscLib
from Report import ReportGen

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
def boot_to_legacy_os():
    tc = ('502', '[TC502] Boot to legacy OS', 'Boot to legacy OS and check dmesg info')
    result = ReportGen.LogHeaderResult(tc)
    err_ignore = ["XFS .*?: Metadata (?:I/O|CRC) error", "ERST.*? support is initialized", "regulatory.(?:0|db)"]
    try:
        assert BmcLib.force_reset()
        if not SetUpLib.wait_message('Start of legacy boot', 600):
            assert SetUpLib.enable_legacy_boot()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, 600)
        assert not PlatMisc.get_dmesg_keywords(["error", "fail"], err_ignore)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
