from batf.Report import ReportGen
from batf import var
from ICX2P.BaseLib import Update, SetUpLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Msg


def update_bios(branch):
    tc = ('001', '[TC001]Update BIOS', 'Update BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.LOG_DIR, branch, 'debug-build')
    var.set("biosimage", img)
    if not Update.update_bios(img):
        result.log_fail()
        return
    if not SetUpLib.update_default_password():
        result.log_fail(capture=True)
        return
    SetUpLib.disable_legacy_boot()
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def update_bios_mfg(branch):
    tc = ('019', '[TC019]装备模式: Update BIOS', 'Update BIOS 装备模式')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.LOG_DIR, branch, 'EQU-build')
    if not Update.update_bios(img):
        result.log_fail()
        return
    if not SetUpLib.update_default_password():
        result.log_fail(capture=True)
        return
    SetUpLib.disable_legacy_boot()
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
