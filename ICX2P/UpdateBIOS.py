from Report import ReportGen
from ICX2P.BaseLib import Update 
from ICX2P import SutConfig


def update_bios(serial, dst, branch):
    tc = ('001', 'Update BIOS', 'Update BIOS')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not Update.get_test_image(dst, branch, 'debug-build'):
        result.log_fail()
        return
    if not Update.update_specific_img(dst, serial):
        result.log_fail()
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
    result.log_pass()
    return True
