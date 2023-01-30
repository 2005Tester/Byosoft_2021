from SPR4P.Config import *
from SPR4P.BaseLib import *


@core.test_case(('001', '[TC001]Update BIOS', 'Update BIOS'))
def update_bios(branch=SutConfig.Env.BRANCH_LATEST):
    img = Update.get_test_image(branch)
    var.set("biosimage", img)
    if not Update.flash_bios_bin_and_init(img):
        return core.Status.Fail
    return core.Status.Pass


@core.test_case(('019', '[TC019]装备模式: Update BIOS', 'Update BIOS 装备模式'))
def update_bios_mfg(branch=SutConfig.Env.BRANCH_LATEST):
    img = Update.get_test_image(branch, 'equip')
    if not Update.flash_bios_bin_and_init(img):
        return core.Status.Fail
    return core.Status.Pass
