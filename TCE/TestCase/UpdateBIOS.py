from batf.Report import ReportGen
from TCE.BaseLib import Update, SetUpLib
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Msg


def update_bios(branch):
    tc = ('001', '[TC001]Update BIOS', 'Update BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.LOG_DIR, branch, 'debug-build')
    # img = r"C:\Users\admin\Desktop\arthur\BIOS\WTCEAV004.bin"
    if not Update.update_bios(img):
        result.log_fail()
        return
    if not SetUpLib.update_default_password():
        result.log_fail(capture=True)
        return
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
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
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
