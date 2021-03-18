from Report import ReportGen
from ICX2P.BaseLib import Update 


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


def update_bios_mfg(serial, dst, branch):
    tc = ('019', '装备模式: Update BIOS', 'Update BIOS 装备模式')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not Update.get_test_image(dst, branch, 'EQU-build'):
        result.log_fail()
        return
    if not Update.update_specific_img(dst, serial):
        result.log_fail()
        return
    result.log_pass()
    return True
