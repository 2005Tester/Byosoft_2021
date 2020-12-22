from Common import Misc
from ICX2P.BaseLib import Update 

def update_bios(serial, dst):
    tc = ('001', 'Update BIOS', 'Update BIOS')
    result = Misc.LogHeaderResult(tc, serial)
    if not Update.get_test_image(dst):
        result.log_fail()
    result.log_pass()
    return True