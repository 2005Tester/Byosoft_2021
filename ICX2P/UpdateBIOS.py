from Report import ReportGen
from ICX2P.BaseLib import Update 

def update_bios(serial, dst):
    tc = ('001', 'Update BIOS', 'Update BIOS')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not Update.get_test_image(dst):
        result.log_fail()
        return
    if not Update.update_specific_img(dst, serial):
        result.log_fail()
        return
    result.log_pass()
    return True