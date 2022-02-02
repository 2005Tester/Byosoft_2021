import logging
from SPR4P.Config import SutConfig
from SPR4P.BaseLib import SetUpLib, PlatMisc, BmcLib
from batf import MiscLib, SerialLib, core
from batf.Report import ReportGen
from batf.SutInit import Sut
from SPR4P.Config.PlatConfig import Key, Msg
from SPR4P.TestCase import UpdateBIOS

# Test case ID: TC500-520

##########################################
#            Legacy Test Cases           #
##########################################


@core.test_case(('500', '[TC500] Enable Legacy Boot', 'Enable Legacy Boot.'))
def enable_legacy_boot():
    try:
        assert SetUpLib.enable_legacy_boot()
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


@core.test_case(('501', '[TC501] Disable Legacy Boot', 'Disable Legacy Boot.'))
def disable_legacy_boot():
    try:
        assert SetUpLib.disable_legacy_boot()
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


# 启动到Legacy OS并检查dmesg没有错误
# Precondition: 依赖 enable_legacy_boot()
# OnStart: Legacy Mode
# OnComplete: NA
@core.test_case(('502', '[TC502] Boot to legacy OS', 'Boot to legacy OS and check dmesg info'))
def boot_to_legacy_os():
    err_ignore = ["XFS .*?: Metadata (?:I/O|CRC) error", "ERST.*? support is initialized", "regulatory.(?:0|db)"]
    try:
        assert BmcLib.force_reset()
        if not SetUpLib.wait_message('Start of legacy boot', 600):
            assert SetUpLib.enable_legacy_boot()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, 600)
        assert not PlatMisc.get_dmesg_keywords(["error", "fail"], err_ignore)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
