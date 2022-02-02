from TCE.BaseLib import Update, SetUpLib
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Msg
from batf import core, var
import logging
import os


@core.test_case(('001', '[TC001]Update BIOS', 'Update BIOS BIN img file via BMC'))
def update_bios(branch, flag='non_mfg'):
    try:
        # changed global IMG, IMG_MFG
        non_mfg_img = Update.get_test_image(SutConfig.Env.LOG_DIR, branch, 'debug-build')
        var.set("non_mfg_img", non_mfg_img)
        mfg_img = Update.get_test_image(SutConfig.Env.LOG_DIR, branch, 'EQU-build')
        var.set("mfg_img", mfg_img)
        if flag == 'non_mfg':
            logging.info('TC001 - update non-mfg bios')
            assert Update.update_bios(non_mfg_img)
        elif flag == 'mfg':
            logging.info('TC019 - update mfg bios')
            Update.update_bios(mfg_img)
        else:
            logging.info('Unknown bios type, break and exit')
            raise Exception

        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail


# used for restore env, cautious - less call, default is non-mfg version
def update_bios_local(flag='non_mfg'):
    var.set('serial_log', os.path.join(SutConfig.Env.LOG_DIR, 'update_bios_local.log'))
    try:
        local_img = var.get("non_mfg_img")
        local_mfg_img = var.get("mfg_img")
        logging.info('Restore Env, update bios locally,')
        if flag == 'non_mfg':
            assert Update.update_bios(local_img)
        elif flag == 'mfg':
            assert Update.update_bios(local_mfg_img)
        else:
            logging.info('Unknown bios type')
            raise Exception
        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5)
        logging.info('Update bios locally successfully,')
        return True
    except Exception as err:
        logging.error(err)
        logging.info('Update bios locally -> failed,')
        return False
