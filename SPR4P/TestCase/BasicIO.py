from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# BasicIO Test Case
# TC 1400-1449
####################################


def _log_time(log_n):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY) #考虑全打印
        logging.info("Suse_OS Boot Successful")
        SERIAL_LOG = os.path.join(SutConfig.Env.LOG_DIR, 'TC{}.log'.format(log_n))
        with open(SERIAL_LOG, 'r', encoding="utf-8") as _log:
            ser_log = _log.read()
        s_cont = 0
        for str_check in SutConfig.Sys.OEM_LOG_SUT + Msg.OEM_LOG_COMMON:
            if not re.search(str_check, ser_log):
                s_cont += 1
                logging.info('**{} -- not found**'.format(str_check))
        return s_cont == 0
    except AssertionError as e:
        logging.error(e)
        return False


def _bt_log_time():
    assert BmcLib.force_reset()
    if not BmcLib.read_bt_data('92 14 E3 00 05 10 01'):
        core.capture_screen()
        return False
    return True


def _get_time_from_serial():
    logging.info("Get datetime from serial")
    assert BmcLib.force_reset()
    ser_time_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.POST_START, 5, SutConfig.Env.BOOT_DELAY)
    assert ser_time_log, "Invalid serial log"
    time_str = "".join(re.findall(f"{Msg.POST_START} (.+?) <<<", ser_time_log))
    time_serial_int = int(time.mktime(time.strptime(time_str, '%Y.%m.%d %H:%M:%S')))
    logging.info(f"Serial Date Time: {time_str}")
    return time_serial_int


def _get_time_from_bmc():
    logging.info("Get datetime from bmc ssh")
    cmd_time = ['ipmcget -d time']
    res_t = ['']
    read_bmc = SshLib.interaction(Sut.BMC_SSH, cmd_time, res_t)
    assert read_bmc, "Invalid bmc data"
    read_bmc = read_bmc[1]
    date_time_found = re.findall("(\d{4}-\d{1,2}-\d{1,2}).*?(\d{2}:\d{1,2}:\d{1,2})", read_bmc)
    assert date_time_found, "Datetime string not found"
    bmc_date, bmc_time = date_time_found[0]
    bmc_date_time = f"{bmc_date} {bmc_time}"
    bmc_utc = "".join(re.findall("UTC([-+\d]*)", read_bmc))
    logging.info(f"BMC Date Time: {bmc_date_time} UTC{bmc_utc}")
    bmc_date_time_int = int(time.mktime(time.strptime(bmc_date_time, '%Y-%m-%d %H:%M:%S')))
    utc_offset_int = -(int(bmc_utc) * 60 * 60 if bmc_utc else 0)
    bmc_time_int = bmc_date_time_int + utc_offset_int
    return bmc_time_int


@core.test_case(("1400", "[TC1400] Testcase_SystemInfoUefi_002", "【UEFI】热键提示信息正确显示_KVM"))
def Testcase_SystemInfoUefi_002():
    """
    Name:       【UEFI】热键提示信息正确显示_KVM
    Condition:  1、UEFI模式。
    Steps:      1、上电启动至第一屏，查看热键显示是否齐全，有结果A；
                2、KVM逐个按下热键，查看按键后屏幕提示是否准确，响应按键动作是否与预设一致，有结果B。
    Result:     A：热键提示信息显示齐全，包含DEL/F11/F12/F6；
                B：按键后高亮显示：XX is Pressed.Go to..的提示信息，热键响应与预设动作一致。
    Remark:
    """
    try:
        default_logo = str(PlatMisc.root_path() / "Resource/Logo/Key.bmp")
        key_logo = PlatMisc.save_logo(name="TC1400_hotkey", prompt=Msg.HOTKEY_PROMPT_DEL, cursor=Msg.CURSOR_HOTKEY)
        assert MiscLib.compare_images(default_logo, key_logo)
        keys = {"DEL": [Key.DEL, Msg.DEL_PRESSED],
                "F11": [Key.F11, Msg.F11_PRESSED],
                "F12": [Key.F12, Msg.F12_PRESSED],
                "F6": [Key.F6, Msg.F6_PRESSED]}
        for key_name, key in keys.items():
            assert SetUpLib.boot_with_hotkey(key[0], key[1]), f"{key_name} boot fail"
            save_path = os.path.join(Env.LOG_DIR, var.get("current_test"))
            hotkey_image = PlatMisc.screen_crop(Msg.CURSOR_HOTKEY, name=f"TC1400_{key_name}", path=save_path)
            hotkey_resource = str(PlatMisc.root_path() / f"Resource/Logo/{key_name}.bmp")
            assert MiscLib.compare_images(hotkey_image, hotkey_resource)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1401", "[TC1401] Testcase_SystemInfoUefi_003", "【UEFI】热键提示信息正确显示_串口"))
def Testcase_SystemInfoUefi_003():
    """
    Name:       【UEFI】热键提示信息正确显示_串口
    Condition:  1、UEFI模式。
    Steps:      1、上电启动至第一屏，查看热键显示是否齐全，有结果A；
                2、串口逐个按下热键，查看按键后串口提示是否准确，响应按键动作是否与预设一致，有结果B。
    Result:     A：热键提示信息显示齐全，包含DEL/F11/F12/F6；
                B：按键后显示：XX is Pressed.Go to..的提示信息，热键响应与预设动作一致。
    Remark:
    """
    try:
        keys = {"DEL": [Key.DEL, Msg.DEL_PRESSED],
                "F11": [Key.F11, Msg.F11_PRESSED],
                "F12": [Key.F12, Msg.F12_PRESSED],
                "F6": [Key.F6, Msg.F6_PRESSED]}
        for key_name, key in keys.items():
            assert SetUpLib.boot_with_hotkey(key[0], key[1]), f"{key_name} boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1403", "[TC1403] Testcase_SystemInfoLegacy_003", "【Legacy】热键提示信息正确显示_串口"))
@mark_legacy_test
def Testcase_SystemInfoLegacy_003():
    """
    Name:       【Legacy】热键提示信息正确显示_串口
    Condition:  1、Legacy模式。
    Steps:      1、上电启动至第一屏，查看热键显示是否齐全，有结果A；
                2、串口逐个按下热键，查看按键后串口提示是否准确，响应按键动作是否与预设一致，有结果B。
    Result:     A：热键提示信息显示齐全，包含DEL/F11/F12/F6；
                B：按键后显示：XX is Pressed.Go to..的提示信息，热键响应与预设动作一致。
    Remark:
    """
    try:
        keys = {"DEL": [Key.DEL, Msg.DEL_PRESSED],
                "F11": [Key.F11, Msg.F11_PRESSED],
                "F12": [Key.F12, Msg.F12_PRESSED],
                "F6": [Key.F6, Msg.F6_PRESSED]}
        for key_name, key in keys.items():
            assert SetUpLib.boot_with_hotkey(key[0], key[1]), f"{key_name} boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1404", "[TC1404] Testcase_HotKey_001", "Setup菜单F1/F5/F6/F9/F10常用热键测试"))
def Testcase_HotKey_001():
    """
    Name:       Setup菜单F1/F5/F6/F9/F10常用热键测试
    Condition:
    Steps:      1、上电启动，进入Front page、Setup菜单，验证F1/F5/F6/F9/F10热键功能是否正常，有结果A。
    Result:     A：菜单热键功能正常。
    Remark:     F1热键不在需求范围内，具体热键以实际为准
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.CONSOLE_CONFIG)
        logging.info("Test hotkey: F2")
        SetUpLib.send_key(Key.F2)
        assert SetUpLib.wait_msg(Msg.KEYBOARD_FR), "Hotkey test fail: F2"

        assert SetUpLib.locate_option(Msg.CONSOLE_REDIR)
        logging.info("Test hotkey: F6")
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.locate_option([Msg.CONSOLE_REDIR, Msg.DISABLE]), "Hotkey test fail: F6"

        logging.info("Test hotkey: F5")
        SetUpLib.send_key(Key.F5)
        assert SetUpLib.locate_option([Msg.CONSOLE_REDIR, Msg.ENABLE]), "Hotkey test fail: F5"

        logging.info("Test hotkey: F9")
        assert SetUpLib.load_default_in_setup()

        logging.info("Test hotkey: F10")
        SetUpLib.send_key(Key.F10)
        assert SetUpLib.wait_msg(Msg.SAVE_EXIT_PROMPT), "Hotkey test fail: F10"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1405", "[TC1405] Testcase_HotKey_002", "Setup菜单登录密码界面按F2切换键盘制式"))
def Testcase_HotKey_002():
    """
    Name:       Setup菜单登录密码界面按F2切换键盘制式
    Condition:
    Steps:      1、上电启动，BIOS启动过程中热键提示信息；
                2、按DEL键，提示输入登录密码；
                3、按F2，检查键盘制式是否在美式、日式、法式正常切换，有结果A。
    Result:     A：正常切换键盘制式，包括法式、日式和美式键盘。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.KEYBOARD_SWAP, password=None)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.KEYBOARD_FR)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.KEYBOARD_JP)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.KEYBOARD_US)
        logging.info("Send password...")
        SetUpLib.send_data(Msg.BIOS_PASSWORD)
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOME_PAGE, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1406", "[TC1406] Testcase_HotKey_003", "Setup菜单用户输入界面按F2切换键盘制式"))
def Testcase_HotKey_003():
    """
    Name:       Setup菜单用户输入界面按F2切换键盘制式
    Condition:
    Steps:      1、上电启动，BIOS启动过程中热键提示信息；
                2、按DEL键，进入Setup菜单，检查菜单用户输入界面，如：修改密码界面、设置BMC IP界面等；
                3、按F2，检查键盘制式是否在美式、日式、法式正常切换，有结果A。
    Result:     A：正常切换键盘制式，包括法式、日式和美式键盘。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_SECURITY)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.KEYBOARD_FR)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.KEYBOARD_JP)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.KEYBOARD_US)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1407", "[TC1407] Testcase_HotKey_004", "BIOS启动阶段SOL热键显示测试"))
def Testcase_HotKey_004():
    """
    Name:       BIOS启动阶段SOL热键显示测试
    Condition:  1、通过BMC SOL登录x86（"ipmcset -t sol -d activate -v 1 0"）
    Steps:      1、上电启动，检查SOL界面显示的热键信息是否正确，有结果A。
    Result:     A：SOL正确显示热键信息，包括DEL、F6、F11、F12。
    Remark:
    """
    try:
        assert BmcLib.force_reset()
        assert BmcLib.read_sol_data([Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F11,
                                    Msg.HOTKEY_PROMPT_DEL], SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1408", "[TC1408] Testcase_HotKey_005", "SOL界面按DEL热键进入Frontpage菜单测试"))
def Testcase_HotKey_005():
    """
    Name:       SOL界面按DEL热键进入Frontpage菜单测试
    Condition:  1、通过BMC SOL登录x86（"ipmcset -t sol -d activate -v 1 0"）
    Steps:      1、上电启动，启动过程中，SOL界面按DEL键，检查是否进入Frontpage菜单，有结果A。
    Result:     A：正常进入Frontpage菜单。
    Remark:
    """
    try:
        assert SolLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1409", "[TC1409] Testcase_HotKey_006", "SOL界面按F6热键进入SP启动测试"))
def Testcase_HotKey_006():
    """
    Name:       SOL界面按F6热键进入SP启动测试
    Condition:  1、通过BMC SOL登录x86（"ipmcset -t sol -d activate -v 1 0"）
    Steps:      1、上电启动，启动过程中，SOL界面按F6键，检查是否从SP启动，有结果A。
    Result:     A：从SP正常启动。
    Remark:
    """
    try:
        assert SolLib.boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_UEFI)
        assert PlatMisc.is_sp_boot_success()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1410", "[TC1410] Testcase_HotKey_007", "SOL界面按F11热键进入Bootmanage菜单测试"))
def Testcase_HotKey_007():
    """
    Name:       SOL界面按F11热键进入Bootmanage菜单测试
    Condition:  1、通过BMC SOL登录x86（"ipmcset -t sol -d activate -v 1 0"）
    Steps:      1、上电启动，启动过程中，SOL界面按F11键，检查是否进入Bootmanage菜单，有结果A。
    Result:     A：正常进入Bootmanage菜单。
    Remark:
    """
    try:
        assert SolLib.boot_with_hotkey(Key.F11, Msg.BOOT_MANAGER)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1411", "[TC1411] Testcase_HotKey_008", "SOL界面按F12热键进入PXE启动测试"))
def Testcase_HotKey_008():
    """
    Name:       SOL界面按F12热键进入PXE启动测试
    Condition:  1、通过BMC SOL登录x86（"ipmcset -t sol -d activate -v 1 0"）
    Steps:      1、上电启动，启动过程中，SOL界面按F12热键，检查是否从PXE启动，有结果A。
    Result:     A：优先从PXE启动。
    Remark:
    """
    try:
        assert SolLib.boot_with_hotkey(Key.F12, SutConfig.Sys.PXE_UEFI_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1412", "[TC1412] Testcase_HotKey_009", "SOL界面按DEL热键进入Frontpage菜单按ESC退出测试"))
def Testcase_HotKey_009():
    """
    Name:       SOL界面按DEL热键进入Frontpage菜单按ESC退出测试
    Condition:  1、通过BMC SOL登录x86（"ipmcset -t sol -d activate -v 1 0"）
    Steps:      1、上电启动，启动过程中，SOL界面按DEL键进入Frontpage菜单，进入Frontpage页面下任一子菜单；
                2、按ESC键退出菜单，检查是否正常退出，有结果A。
    Result:     A：正常退出到Frontpage菜单。
    Remark:
    """
    try:
        assert SolLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE, close=False)
        assert SolLib.locate_front_page_icon(Msg.BOOT_MANAGER)
        assert SolLib.send_key(Key.ENTER)
        assert SolLib.locate_option(Msg.BOOT_OPTION_OS)
        assert SolLib.send_key(Key.ESC)
        assert SolLib.locate_front_page_icon(Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        SolLib.close_sol()


@core.test_case(("1413", "[TC1413] Testcase_HotKeyUefi_001", "【UEFI】BIOS启动阶段KVM热键显示测试"))
def Testcase_HotKeyUefi_001():
    """
    Name:       【UEFI】BIOS启动阶段KVM热键显示测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，检查KVM界面显示的热键信息是否正确，有结果A。
    Result:     A：KVM正确显示热键信息，包括DEL、F6、F11、F12。
    Remark:
    """
    try:
        default_logo = os.path.join(PlatMisc.root_path(), "Resource/Logo/Key.bmp")
        logging.info(f"Default logo: {default_logo}")
        key_logo = PlatMisc.save_logo(name="key_logo", prompt=Msg.HOTKEY_SHOW, cursor=Msg.CURSOR_HOTKEY)
        if not key_logo:
            logging.info("Post logo can't be captured, please confirm the KVM is open as share mode, not private mode")
            raise AssertionError
        assert MiscLib.compare_images(default_logo, key_logo)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1414", "[TC1414] Testcase_HotKeyUefi_002", "【UEFI】BIOS启动阶段串口热键显示测试"))
def Testcase_HotKeyUefi_002():
    """
    Name:       【UEFI】BIOS启动阶段串口热键显示测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，检查串口打印的热键信息是否正确，有结果A。
    Result:     A：串口正确打印热键信息，包括DEL、F6、F11、F12。
    Remark:
    """
    capture_start = Msg.POST_START
    capture_end = Msg.BIOS_BOOT_COMPLETE
    hot_key_list = [Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_DEL]
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, SutConfig.Env.BOOT_DELAY,
                                    SutConfig.Env.BOOT_DELAY)
        for hot_key in hot_key_list:
            assert hot_key in log_cut, f"no found: {hot_key}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1415", "[TC1415] Testcase_HotKeyUefi_003", "【UEFI】按DEL热键进入Frontpage菜单测试"))
def Testcase_HotKeyUefi_003():
    """
    Name:       【UEFI】按DEL热键进入Frontpage菜单测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，启动过程中按DEL键，检查是否进入Frontpage菜单，有结果A。
    Result:     A：正常进入Frontpage菜单。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1416", "[TC1416] Testcase_HotKeyUefi_004", "【UEFI】按DEL热键进入Frontpage菜单长时间测试"))
def Testcase_HotKeyUefi_004():
    """
    Name:       【UEFI】按DEL热键进入Frontpage菜单长时间测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，启动过程中按DEL键，检查是否进入Frontpage菜单，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：正常进入Frontpage菜单。
    Remark:
    """
    try:
        i = 0
        while i < 3:
            assert SetUpLib.boot_to_page(Msg.PAGE_INFO), f" {i}th time boot set_up page fail"
            i += 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1417", "[TC1417] Testcase_HotKeyUefi_005", "【UEFI】按F6热键进入SP启动测试"))
def Testcase_HotKeyUefi_005():
    """
    Name:       【UEFI】按F6热键进入SP启动测试
    Condition:  1、UEFI模式；
                2、SP已部署。
    Steps:      1、上电启动，启动过程中按F6键，检查是否从SP启动，有结果A。
    Result:     A：从SP正常启动。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.F6, msg=Msg.F6_CONFIRM_UEFI), "Check Hot key failed: F6 "
        assert PlatMisc.is_sp_boot_success()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1418", "[TC1418] Testcase_HotKeyUefi_006", "【UEFI】按F6热键进入SP启动长时间测试"))
def Testcase_HotKeyUefi_006():
    """
    Name:       【UEFI】按F6热键进入SP启动长时间测试
    Condition:  1、UEFI模式；
                2、SP已部署。
    Steps:      1、上电启动，启动过程中按F6键，检查是否从SP启动，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：从SP正常启动。
    Remark:
    """
    try:
        i = 0
        while i < 3:
            assert SetUpLib.boot_with_hotkey(Key.F6, msg=Msg.F6_CONFIRM_UEFI), f"{i}th times F6_hotkey fail"
            assert PlatMisc.is_sp_boot_success()
            i += 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1419", "[TC1419] Testcase_HotKeyUefi_007", "【UEFI】按F11热键进入Bootmanage菜单测试"))
def Testcase_HotKeyUefi_007():
    """
    Name:       【UEFI】按F11热键进入Bootmanage菜单测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，启动过程中按F11键，检查是否进入Bootmanage菜单，有结果A。
    Result:     A：正常进入Bootmanage菜单。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.F11, msg="Boot Manager Menu"), "Check Hot key failed: F11 "
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1420", "[TC1420] Testcase_HotKeyUefi_008", "【UEFI】按F11热键进入Bootmanage菜单长时间测试"))
def Testcase_HotKeyUefi_008():
    """
    Name:       【UEFI】按F11热键进入Bootmanage菜单长时间测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，启动过程中按F11键，检查是否进入Bootmanage菜单，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：正常进入Bootmanage菜单。
    Remark:
    """
    try:
        i = 0
        while i < 3:
            assert SetUpLib.boot_with_hotkey(Key.F11, msg="Boot Manager Menu"), f"{i}th time F11_hotkey fail"
            i += 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1421", "[TC1421] Testcase_HotKeyUefi_009", "【UEFI】按F12热键进入PXE启动测试"))
def Testcase_HotKeyUefi_009():
    """
    Name:       【UEFI】按F12热键进入PXE启动测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，启动过程中按F12热键，检查是否从PXE启动，有结果A。
    Result:     A：优先从PXE启动。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.F12, msg="Booting EFI Network for IPv4"), "Check Hot key failed: F12 "
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1422", "[TC1422] Testcase_HotKeyUefi_010", "【UEFI】按F12热键进入PXE启动长时间测试"))
def Testcase_HotKeyUefi_010():
    """
    Name:       【UEFI】按F12热键进入PXE启动长时间测试
    Condition:  1、UEFI模式。
    Steps:      1、上电启动，启动过程中按F12热键，检查是否从PXE启动，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：优先从PXE启动。
    Remark:
    """
    try:
        for i in range(3):
            assert SetUpLib.boot_with_hotkey(Key.F12, msg="Booting EFI Network for IPv4"), f"{i}th time F12 hotkey fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1423", "[TC1423] Testcase_HotKeyLegacy_001", "【Legacy】BIOS启动阶段KVM热键显示测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_001():
    """
    Name:       【Legacy】BIOS启动阶段KVM热键显示测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，检查KVM界面显示的热键信息是否正确，有结果A。
    Result:     A：KVM正确显示热键信息，包括DEL、F6、F11、F12。
    Remark:
    """
    try:
        default_logo = os.path.join(PlatMisc.root_path(), "Resource/Logo/Key.bmp")
        logging.info(f"Default logo: {default_logo}")
        key_logo = PlatMisc.save_logo(name="key_logo", prompt=Msg.HOTKEY_SHOW, cursor=Msg.CURSOR_HOTKEY)
        if not key_logo:
            logging.info("Post logo can't be captured, please confirm the KVM is open as share mode, not private mode")
            raise AssertionError
        assert MiscLib.compare_images(default_logo, key_logo)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1424", "[TC1424] Testcase_HotKeyLegacy_002", "【Legacy】BIOS启动阶段串口热键显示测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_002():
    """
    Name:       【Legacy】BIOS启动阶段串口热键显示测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，检查串口打印的热键信息是否正确，有结果A。
    Result:     A：串口正确打印热键信息，包括DEL、F6、F11、F12。
    Remark:
    """
    capture_start = Msg.POST_START
    capture_end = Msg.BIOS_BOOT_COMPLETE
    hot_key_list = [Msg.HOTKEY_PROMPT_F6, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_DEL]
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, SutConfig.Env.BOOT_DELAY,
                                    SutConfig.Env.BOOT_DELAY)
        for hot_key in hot_key_list:
            assert hot_key in log_cut, f"no found: {hot_key}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1425", "[TC1425] Testcase_HotKeyLegacy_003", "【Legacy】按DEL热键进入Frontpage菜单测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_003():
    """
    Name:       【Legacy】按DEL热键进入Frontpage菜单测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，启动过程中按DEL键，检查是否进入Frontpage菜单，有结果A。
    Result:     A：正常进入Frontpage菜单。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1426", "[TC1426] Testcase_HotKeyLegacy_004", "【Legacy】按DEL热键进入Frontpage菜单长时间测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_004():
    """
    Name:       【Legacy】按DEL热键进入Frontpage菜单长时间测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，启动过程中按DEL键，检查是否进入Frontpage菜单，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：正常进入Frontpage菜单。
    Remark:
    """
    try:
        for i in range(1, 4):
            assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE), f"No.{i} Legacy boot to Frontpage fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1427", "[TC1427] Testcase_HotKeyLegacy_005", "【Legacy】按F6热键进入SP启动测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_005():
    """
    Name:       【Legacy】按F6热键进入SP启动测试
    Condition:  1、Legacy模式；
                2、SP已部署。
    Steps:      1、上电启动，启动过程中按F6键，检查是否从SP启动，有结果A。
    Result:     A：从SP正常启动。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_LEGACY), f"Legacy, from SP boot fail"
        assert PlatMisc.is_sp_boot_success()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1428", "[TC1428] Testcase_HotKeyLegacy_006", "【Legacy】按F6热键进入SP启动长时间测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_006():
    """
    Name:       【Legacy】按F6热键进入SP启动长时间测试
    Condition:  1、Legacy模式；
                2、SP已部署。
    Steps:      1、上电启动，启动过程中按F6键，检查是否从SP启动，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：从SP正常启动。
    Remark:
    """
    try:
        for i in range(1, 4):
            assert SetUpLib.boot_with_hotkey(Key.F6, msg=Msg.F6_CONFIRM_LEGACY), f"Legacy,No.{i} from SP boot fail"
            assert PlatMisc.is_sp_boot_success()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1429", "[TC1429] Testcase_HotKeyLegacy_007", "【Legacy】按F11热键进入Bootmanage菜单测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_007():
    """
    Name:       【Legacy】按F11热键进入Bootmanage菜单测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，启动过程中按F11键，检查是否进入Bootmanage菜单，有结果A。
    Result:     A：正常进入Bootmanage菜单。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.F11, Msg.F11_CONFIRM), f"Legacy, boot to Bootmanage fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1430", "[TC1430] Testcase_HotKeyLegacy_008", "【Legacy】按F11热键进入Bootmanage菜单长时间测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_008():
    """
    Name:       【Legacy】按F11热键进入Bootmanage菜单长时间测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，启动过程中按F11键，检查是否进入Bootmanage菜单，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：正常进入Bootmanage菜单。
    Remark:
    """
    try:
        for i in range(1, 4):
            assert SetUpLib.boot_with_hotkey(Key.F11, Msg.F11_CONFIRM), f"Legacy, No.{i} boot to Bootmanage fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1431", "[TC1431] Testcase_HotKeyLegacy_009", "【Legacy】按F12热键进入PXE启动测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_009():
    """
    Name:       【Legacy】按F12热键进入PXE启动测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，启动过程中按F12热键，检查是否从PXE启动，有结果A。
    Result:     A：优先从PXE启动。
    Remark:
    """
    try:
        assert SetUpLib.boot_with_hotkey(Key.F12, Sys.PXE_LEGACY_MSG), "Check Hot key failed: F12 "
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1432", "[TC1432] Testcase_HotKeyLegacy_010", "【Legacy】按F12热键进入PXE启动长时间测试"))
@mark_legacy_test
def Testcase_HotKeyLegacy_010():
    """
    Name:       【Legacy】按F12热键进入PXE启动长时间测试
    Condition:  1、Legacy模式。
    Steps:      1、上电启动，启动过程中按F12热键，检查是否从PXE启动，有结果A；
                2、重复执行步骤1 3次，有结果A。
    Result:     A：优先从PXE启动。
    Remark:
    """
    try:
        for i in range(1, 4):
            assert SetUpLib.boot_with_hotkey(Key.F12, Sys.PXE_LEGACY_MSG), f"Legacy, No.{i} from PXE boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1433", "[TC1433] Testcase_SerialPrint_001", "启动关键信息打印"))
def Testcase_SerialPrint_001():
    """
    Name:       启动关键信息打印
    Condition:
    Steps:      1、启动进OS，检查关键信息串口打印是否完整，有结果A；
    Result:     A：
                1、串口打印启动资源信息表、BIOS版本信息、PCIE link状态等信息；
                2、串口打印ME状态寄存器信息；
                3、打印PCIE设备的关键信息，包括root BDF、设备类型、槽位号、linkcap、linkstatus、device BDF、device VID、device DID；
    Remark:     1、具体关键信息参考OEM Level信息定义；
                2、PCIE设备的关键信息需接PCIE卡；
    """
    cpu_resource = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SutConfig.Sys.CPU_CNT)])
    bios_ver = Msg.PAGE_INFO
    pcie_lnk = str(SutConfig.Sys.PCIE_INFO)

    def check_process(timeout):
        # CPU Resource Allocation
        cpu_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.CPU_RSC_ALLOC, Msg.START_DIMM, timeout, timeout)
        key_string1 = re.search(cpu_resource, cpu_log)
        assert key_string1, "CPU Resource Allocation not found"
        logging.info("CPU Resource Allocation check pass")
        # BIOS Revision
        ver_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.LOGO_SHOW, "BMC FW Version :", timeout, timeout)
        key_string2 = re.search(bios_ver, ver_log)
        assert key_string2, "BIOS Revision not found"
        logging.info("BIOS Revision check pass")
        # PCIE LINK STATUS
        pcie_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.HOTKEY_PROMPT_DEL, Msg.BIOS_BOOT_COMPLETE, timeout, timeout)
        key_string3 = re.search(pcie_lnk, pcie_log)
        assert key_string3, "[Assert]: PCIE LINK STATUS not found, Confirm whether PCIE device exist"
        logging.info("PCIE LINK STATUS check pass")
        return True

    try:
        # Open serial debug message
        assert BmcLib.debug_message(True)
        assert BmcLib.force_reset()
        assert check_process(timeout=SutConfig.Env.BOOT_FULL_DBG)

        # Close serial debug message
        assert BmcLib.debug_message(False)
        assert BmcLib.force_reset()
        assert check_process(timeout=SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


@core.test_case(("1435", "[TC1435] Testcase_LogTime_001", "首条串口日志打印当前时间测试"))
def Testcase_LogTime_001():
    """
    Name:       首条串口日志打印当前时间测试
    Condition:
    Steps:      1、系统复位，查看串口日志是否有当前时间的打印信息，有结果A。
    Result:     A：第一条打印启动时间（时间与RTC时间一致）
                "=~=~=~=~=~=~=~=~=~=~= BIOS Log @ %d.%d.%d %d:%d:%d =~=~=~=~=~=~=~=~=~=~=\n"。
    Remark:
    """
    try:
        time_serial = _get_time_from_serial()
        time_bmc = _get_time_from_bmc()
        time_offset = time_bmc - time_serial
        assert 0 <= time_offset < 5, f'Serial time: {time_serial}, Bmc time: {time_bmc}, Offset: {time_offset}s'
        logging.info(f"Datetime Offset: {time_offset}s")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1436", "[TC1436] Testcase_LogTime_002", "打开debug开关时首条串口日志打印当前时间测试"))
def Testcase_LogTime_002():
    """
    Name:       打开debug开关时首条串口日志打印当前时间测试
    Condition:
    Steps:      1、系统复位，查看串口日志是否有当前时间的打印信息，有结果A。
    Result:     A：第一条打印启动时间（时间与RTC时间一致）
                "=~=~=~=~=~=~=~=~=~=~= BIOS Log @ %d.%d.%d %d:%d:%d =~=~=~=~=~=~=~=~=~=~=\n"。
    Remark:
    """
    try:
        assert BmcLib.debug_message(True)
        time_serial = _get_time_from_serial()
        time_bmc = _get_time_from_bmc()
        time_offset = time_bmc - time_serial
        assert 0 <= time_offset < 5, f'Serial time: {time_serial}, Bmc time: {time_bmc}, Offset: {time_offset}s'
        logging.info(f"Datetime Offset: {time_offset}s")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.debug_message(False)
        BmcLib.clear_cmos()


@core.test_case(("1437", "[TC1437] Testcase_LogTime_003", "串口日志打印BIOS启动结束信息"))
def Testcase_LogTime_003():
    """
    Name:       串口日志打印BIOS启动结束信息
    Condition:
    Steps:      1、系统复位，查看串口日志是否打印BIOS启动结束信息，有结果A。
    Result:     A：串口打印BIOS启动结束信息，如BIOS startup is complete @ %d.%d.%d %d:%d:%d。
    Remark:
    """
    try:
        assert BmcLib.force_reset()
        log_cat = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.BIOS_BOOT_COMPLETE,
                                    SutConfig.Env.BOOT_DELAY, SutConfig.Env.BOOT_DELAY)
        assert MiscLib.verify_msgs_in_log([Msg.POST_START, Msg.BIOS_BOOT_COMPLETE], log_cat)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1438", "[TC1438] Testcase_LogTimeUefi_001", "【UEFI】正常启动结束标志上报"))
def Testcase_LogTimeUefi_001():
    """
    Name:       【UEFI】正常启动结束标志上报
    Condition:  1、UEFI模式；
                2、BMC BT通道打开；
                3、无可启动OS。
    Steps:      1、BIOS正常启动，查看BT通道打印，有结果A。
    Result:     A：启动过程中不会上报结束标志，启动完成后仅上报一次结束标志。
    Remark:     1、进入BT通道指令：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、结束标志关键字：
                92 DB 07 00 05 10 01
    """
    try:
        assert _bt_log_time()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1439", "[TC1439] Testcase_LogTimeUefi_003", "【UEFI】进入OS，启动结束标志上报"))
def Testcase_LogTimeUefi_003():
    """
    Name:       【UEFI】进入OS，启动结束标志上报
    Condition:  1、UEFI模式；
                2、BMC BT通道打开；
                3、有可启动的OS。
    Steps:      1、BIOS正常启动进OS，查看BT通道打印，有结果A。
    Result:     A：启动过程中不会上报结束标志，启动完成后仅上报一次结束标志，进入OS时不会重复上报。
    Remark:     1、进入BT通道指令：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、结束标志关键字：
                92 DB 07 00 05 10 01
    """
    try:
        assert _bt_log_time()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1440", "[TC1440] Testcase_LogTimeUefi_004", "【UEFI】PXE轮询时，启动结束标志上报"))
def Testcase_LogTimeUefi_004():
    """
    Name:       【UEFI】PXE轮询时，启动结束标志上报
    Condition:  1、UEFI模式；
                2、BMC BT通道打开；
                3、有PXE启动项，PXE服务器未部署。
    Steps:      1、BIOS正常启动进入PXE轮询，查看BT通道打印，有结果A。
    Result:     A：轮询过程中仅上报一次结束标志。
    Remark:     1、进入BT通道指令：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、结束标志关键字：
                92 DB 07 00 05 10 01
    """
    flag = '92 14 E3 00 05 10 01'
    try:
        assert BmcLib.force_reset()
        assert SetUpLib.wait_msg(Msg.HOTKEY_PROMPT_DEL, SutConfig.Env.BOOT_DELAY)
        SetUpLib.send_key(Key.F12)
        msg_found = False
        login = False
        # 结束标志出现的时机不确定，有时候在输入密码之前，有时候在输入密码之后
        bt_ch = BmcLib.open_bt_channel()
        start_time = time.time()
        while time.time() - start_time < 120:
            timeout = 2 if not login else 60
            if BmcLib.read_bt_data(flag, timeout=timeout, login=False, logout=False, shell=bt_ch):
                msg_found = True
                break
            if (not login) and SetUpLib.wait_msg(Msg.PW_PROMPT, timeout=2):
                SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
                login = True

        assert msg_found, f"Msg not found in bt channel within 120s: {flag}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1441", "[TC1441] Testcase_LogTimeLegacy_001", "【Legacy】正常启动进OS结束标志上报"))
@mark_legacy_test
def Testcase_LogTimeLegacy_001():
    """
    Name:       【Legacy】正常启动进OS结束标志上报
    Condition:  1、Legacy模式；
                2、BMC BT通道打开；
                3、可正常启动进OS。
    Steps:      1、BIOS正常启动进OS，查看BT通道打印，有结果A。
    Result:     A：启动过程中不会上报结束标志，仅进入OS时上报一次结束标志。
    Remark:     1、进入BT通道指令：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、结束标志关键字：
                92 DB 07 00 05 10 01
    """
    try:
        assert _bt_log_time()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1442", "[TC1442] Testcase_LogTimeLegacy_003", "【Legacy】进入OS，启动结束标志上报"))
@mark_legacy_test
def Testcase_LogTimeLegacy_003():
    """
    Name:       【Legacy】进入OS，启动结束标志上报
    Condition:  1、Legacy模式；
                2、BMC BT通道打开；
                3、有可启动的OS。
    Steps:      1、BIOS正常启动进OS，查看BT通道打印，有结果A。
    Result:     A：启动过程中不会上报结束标志，启动完成后仅上报一次结束标志，进入OS时不会重复上报。
    Remark:     1、进入BT通道指令：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、结束标志关键字：
                92 DB 07 00 05 10 01
    """
    try:
        assert _bt_log_time()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1443", "[TC1443] Testcase_LogTimeLegacy_004", "【Legacy】PXE轮询时，启动结束标志上报"))
@mark_legacy_test
def Testcase_LogTimeLegacy_004():
    """
    Name:       【Legacy】PXE轮询时，启动结束标志上报
    Condition:  1、Legacy模式；
                2、BMC BT通道打开；
                3、有PXE启动项，PXE服务器未部署。
    Steps:      1、BIOS正常启动进入PXE轮询，查看BT通道打印，有结果A。
    Result:     A：轮询过程中仅上报一次结束标志。
    Remark:     1、进入BT通道指令：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、结束标志关键字：
                92 DB 07 00 05 10 01
    """
    flag = '92 14 E3 00 05 10 01'
    try:
        assert BmcLib.force_reset()
        assert SetUpLib.wait_msg(Msg.HOTKEY_PROMPT_DEL, SutConfig.Env.BOOT_DELAY)
        SetUpLib.send_key(Key.F12)
        msg_found = False
        login = False
        # 结束标志出现的时机不确定，有时候在输入密码之前，有时候在输入密码之后
        bt_ch = BmcLib.open_bt_channel()
        start_time = time.time()
        while time.time() - start_time < 120:
            timeout = 2 if not login else 60
            if BmcLib.read_bt_data(flag, timeout=timeout, login=False, logout=False, shell=bt_ch):
                msg_found = True
                break
            if (not login) and SetUpLib.wait_msg(Msg.PW_PROMPT, timeout=2):
                SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
                login = True
        assert msg_found, f"Msg not found in bt channel within 120s: {flag}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1444", "[TC1444] Testcase_SerialRedirect_001", "串口重定向设置菜单检查"))
def Testcase_SerialRedirect_001():
    """
    Name:       串口重定向设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，检查是否提供串口重定向选项开关，默认值及可选值，有结果A；
                2、打开关闭串口重定向选项时，检查菜单联动情况，有结果B；
    Result:     A：提供串口重定向选项，打开、关闭可选，默认打开；
                B：关闭选项时，串口参数隐藏无法设置；打开选项时，串口参数可设置。
    Remark:
    """
    name_option = [[Msg.FLOW_CTL, '<None>'], ['Baud Rate', '<115200>'], ['Terminal Type', '<VT\_100>'],
                   ['Parity', '<None>'], ['Data Bits', '<8 Bits>'], ['Stop Bits', '<1 Bit>']]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], confirm_msg=Msg.CONSOLE_REDIR)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.CONSOLE_REDIR), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.verify_options(options=[[Msg.CONSOLE_REDIR, Msg.ENABLE]])
        assert SetUpLib.set_option_value(Msg.CONSOLE_REDIR, Msg.DISABLE, save=False)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG])
        assert SetUpLib.get_option_value(Msg.CONSOLE_REDIR, try_counts=1) == Msg.DISABLE
        for _na_op in name_option:
            assert not SetUpLib.locate_option(setupoption=_na_op, try_counts=5), f"{_na_op} is found"  # 关闭选项时，串口参数隐藏无法设置
        assert SetUpLib.load_default_in_setup()
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG])
        assert SetUpLib.get_option_value(Msg.CONSOLE_REDIR, Key.UP, 5) == Msg.ENABLE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1445", "[TC1445] Testcase_SerialRedirect_002", "串口重定向参数修改测试"))
def Testcase_SerialRedirect_002():
    """
    Name:       串口重定向参数修改测试
    Condition:
    Steps:      1、启动进Setup菜单，打开串口重定向开关，修改串口部分参数，F10保存重启再次进入Setup菜单检查是否生效，有结果A；
                2、F9恢复默认后再F10保存重启，再次进入Setup菜单检查参数是否恢复默认，有结果B；
    Result:     A：参数修改生效；
                B：参数恢复默认。
    Remark:
    """
    flow_con = [Msg.FLOW_CTL, '<None>']
    flow_rts = [Msg.FLOW_CTL, '<RTS/CTS>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], Key.DOWN, 20, flow_con[0])
        assert SetUpLib.set_option_value(flow_con[0], 'RTS/CTS', Key.DOWN, save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], Key.DOWN, 20, flow_con[0])
        assert SetUpLib.verify_options([flow_rts], Key.DOWN, 16)
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, Key.RESET_DEFAULT)     # 参数恢复默认
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], Key.DOWN, 20, flow_con[0])
        assert SetUpLib.verify_options([flow_con], Key.DOWN, 16)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1446", "[TC1446] Testcase_SerialRedirect_003", "默认关闭AutoRefresh测试"))
def Testcase_SerialRedirect_003():
    """
    Name:       默认关闭AutoRefresh测试
    Condition:  1、串口已连接。
    Steps:      1、启动进Setup菜单，检查串口界面是否自动发送ESC键，有结果A。
                2、进入Setup菜单串口重定向界面检查AutoRefresh选项是否默认关闭，有结果B；
    Result:     A：串口停留在Setup界面不会自动发送ESC键；
                B：AutoRefresh选项默认关闭。
    Remark:     1、AutoRefresh选项默认关闭且隐藏，验证功能无问题即可。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG])
        time.sleep(5)
        assert SetUpLib.locate_option(Msg.FLOW_CTL)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1447", "[TC1447] Testcase_SerialRedirectUefi_001", "【UEFI】串口进入Setup菜单无乱码测试"))
def Testcase_SerialRedirectUefi_001():
    """
    Name:       【UEFI】串口进入Setup菜单无乱码测试
    Condition:  1、UEFI模式。
    Steps:      1、启动进Setup菜单，检查串口打印是否出现乱码，有结果A；
    Result:     A：串口打印无乱码，关键字能正常抓取；
    Remark:     1、通过自动化跟踪
    """
    page_flag = [Msg.PAGE_ADVANCED, Msg.PAGE_SECURITY, Msg.PAGE_BOOT, Msg.PAGE_SAVE, Msg.PAGE_INFO]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        for _pa_fl in page_flag:
            SerialLib.send_key(Sut.BIOS_COM, Key.RIGHT)
            assert SetUpLib.wait_msg(_pa_fl), f'{_pa_fl} no found'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1448", "[TC1448] Testcase_SerialRedirectLegacy_001", "【Legacy】串口进入Setup菜单无乱码测试"))
@mark_legacy_test
def Testcase_SerialRedirectLegacy_001():
    """
    Name:       【Legacy】串口进入Setup菜单无乱码测试
    Condition:  1、Legacy模式。
    Steps:      1、启动进Setup菜单，检查串口打印是否出现乱码，有结果A；
    Result:     A：串口打印无乱码，关键字能正常抓取；
    Remark:     1、通过自动化跟踪
    """
    page_flag = [Msg.PAGE_ADVANCED, Msg.PAGE_SECURITY, Msg.PAGE_BOOT, Msg.PAGE_SAVE, Msg.PAGE_INFO]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_INFO)
        for _pa_fl in page_flag:
            SerialLib.send_key(Sut.BIOS_COM, Key.RIGHT)
            assert SetUpLib.wait_msg(_pa_fl), f'{_pa_fl} no found'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1449", "[TC1449] Testcase_SerialRedirectLegacy_002", "【Legacy】串口重定向选项功能测试"))
@mark_legacy_test
def Testcase_SerialRedirectLegacy_002():
    """
    Name:       【Legacy】串口重定向选项功能测试
    Condition:  1、Legacy模式。
    Steps:      1、启动进Setup菜单，使能串口重定向，F10保存重启检查串口信息POST阶段是否有SOL Oprom加载，有结果A；
                2、重启进Setup菜单，关闭串口重定向，F10保存重启检查串口信息POST阶段是否有SOL Oprom加载，有结果B；
    Result:     A：加载SOL的Oprom，通过串口按热键能进入Setup菜单；
                B：不加载SOL的Oprom，通过串口无法按热键进入Setup菜单。
    Remark:
    """
    conred_value = [Msg.ENABLE, Msg.DISABLE]
    try:
        for op in conred_value:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu([Msg.CONSOLE_CONFIG], confirm_msg=Msg.CONSOLE_REDIR)
            if op == Msg.ENABLE:
                assert SetUpLib.verify_options(options=[[Msg.CONSOLE_REDIR, Msg.ENABLE]])
                assert SolLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE)
            else:
                assert SetUpLib.set_option_value(Msg.CONSOLE_REDIR, Msg.DISABLE, save=True)
                assert SolLib.boot_with_hotkey(Key.DEL, Msg.BIOS_BOOT_COMPLETE, reboot=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

