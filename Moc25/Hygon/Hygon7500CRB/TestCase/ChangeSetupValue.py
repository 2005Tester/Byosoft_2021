import logging
import time

from batf.Report import ReportGen
from Hygon7500CRB.BaseLib import SetUpLib

from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig

def change_update_mode(mode="normal"):
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_EXIT_CN)
        if mode == "normal":
            assert SetUpLib.select_option_value(Key.DOWN, [SutConfig.Msg.BIOS_UPDATE_MODE_CN], Key.DOWN, "保留配置", 6)
        else:
            assert SetUpLib.select_option_value(Key.DOWN, [SutConfig.Msg.BIOS_UPDATE_MODE_CN], Key.DOWN, "完全刷新", 6)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        logging.info("Change update mode successed.")
        return True
    except AssertionError as e:
        logging.error(e)
        logging.info("Change update mode failed.")
        return

def change_cpu_frequency(frequency="2500"):
    try:
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED_CN)
        assert SetUpLib.enter_menu(Key.DOWN, [SutConfig.Msg.MISC_CONFIG_CN], 10, SutConfig.Msg.PERFORMANCE_CN)
        assert SetUpLib.select_option_value(Key.DOWN, [SutConfig.Msg.PERFORMANCE_CN], Key.DOWN, "用户自定义", 5)
        assert SetUpLib.select_option_value(Key.DOWN, [SutConfig.Msg.CPU_FREQUENCY_CN], Key.DOWN, "{0} MHz".format(frequency), 5)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        logging.info("Change CPU frequency to {0} MHz successed.".format(frequency))
        return True
    except AssertionError as e:
        logging.error(e)
        logging.info("Change CPU frequency to {0} MHz failed.".format(frequency))
        return


        