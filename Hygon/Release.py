from Hygon.Config.PlatConfig import Msg, Key
from Hygon.BaseLib import SetUpLib
from Hygon.Config import SutConfig
from Report import ReportGen


# Test case ID: 1xx

##########################################
#            Release Test Cases          #
##########################################


def check_usb_info():
    tc = ('100', 'Verify USB INFO', 'Check usb device info')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_setup(), 'boot to setup -> fail'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED_CN), 'boot to page -> fail'
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_USB_CFG_CN, 12, '后置USB端口配置'), 'enter menu -> fail'
        assert SetUpLib.verify_options(Key.DOWN, [['前置USB端口配置', '<打开>']], 4), 'verify options -> fail'
        assert SetUpLib.locate_option(Key.UP, ['后置USB端口配置', '<打开>'], 4), 'locate option -> fail'
        assert SetUpLib.verify_supported_values('打开 关闭'), 'verify values -> fail'
        # assert SetUpLib.get_option_value(['后置USB端口配置', '<打开>'], Key.UP, 4), 'get option value -> fail'
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    # finally:
    #     pass
