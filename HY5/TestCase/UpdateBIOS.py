from batf.Report import ReportGen
from batf import var
from HY5.BaseLib import Update, SetUpLib
from HY5.Config import SutConfig
from HY5.Config.PlatConfig import Msg
import logging
import os


def update_bios():
    tc = ('001', '[TC001]Update BIOS', 'Update BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.BIOS_DIR, type="Non-Mfg")
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

def downgrade_bios():
    tc = ('002', '[TC002]downgrade BIOS', 'downgrade BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_previous_test_image(SutConfig.Env.BIOS_DIR)
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


def parallel_bios():
    tc = ('003', '[TC003]parallel Update BIOS', 'parallel Update BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.BIOS_DIR, type="Non-Mfg")
    var.set("biosimage", img)
    if not Update.update_bios(img):
        result.log_fail()
        return
    logging.info("还原测试版本")
    if not Update.update_bios(img):
        result.log_fail()
        return
    logging.info("平刷测试版本")
    if not SetUpLib.update_default_password():
        result.log_fail(capture=True)
        return
    SetUpLib.disable_legacy_boot()
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True

def update_bios_mfg():
    tc = ('004', '[TC004]Update Mfg BIOS', 'Update Mfg BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.BIOS_DIR, type="Mfg")
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