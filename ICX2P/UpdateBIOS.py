from Report import ReportGen
from ICX2P.BaseLib import Update, SetUpLib
from ICX2P import SutConfig, Pwd


def update_bios(serial, ssh_bmc, sftp_bmc, branch):
    tc = ('001', 'Update BIOS', 'Update BIOS')
    result = ReportGen.LogHeaderResult(tc, serial)
    img = Update.get_test_image(SutConfig.LOG_DIR, branch, 'debug-build')
    if not Update.update_bios(serial, ssh_bmc, sftp_bmc, img):
        result.log_fail()
        return
    if not Pwd.update_default_password(serial, ssh_bmc):
        result.log_fail(capture=True)
        return
    if not SetUpLib.move_boot_option_up(serial, ssh_bmc, SutConfig.Msg.BOOT_OPTION_OS, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


def update_bios_mfg(serial, ssh_bmc, sftp_bmc, branch):
    tc = ('019', '装备模式: Update BIOS', 'Update BIOS 装备模式')
    result = ReportGen.LogHeaderResult(tc, serial)
    img = Update.get_test_image(SutConfig.LOG_DIR, branch, 'EQU-build')
    if not Update.update_bios(serial, ssh_bmc, sftp_bmc, img):
        result.log_fail()
        return
    if not Pwd.update_default_password(serial, ssh_bmc):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True
