from Report import ReportGen
from Pangea.BaseLib import Update


def update_bios(serial, dst, ssh):
    tc = ('001', 'Update BIOS', 'Update BIOS + Parallel Flash')
    result = ReportGen.LogHeaderResult(tc, serial)
    if not Update.get_test_image(dst):
        result.log_fail()
        return
    if not Update.update_specific_img(serial, dst, ssh):
        result.log_fail()
        return
    result.log_pass()
    return True
