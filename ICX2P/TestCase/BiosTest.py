#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import re
import time
import os
import csv
from batf import core, SerialLib, MiscLib, SshLib
from batf.SutInit import Sut
from ICX2P.Config.SutConfig import SysCfg
from ICX2P.Config.PlatConfig import Msg, Key, BiosCfg
from ICX2P.Config import SutConfig
from ICX2P.BaseLib import PlatMisc, SetUpLib, ParsetableLib, BmcLib
from ICX2P.BaseLib.PlatMisc import ReleaseTest
from batf.Report import ReportGen, stylelog
from batf.Common.LogAnalyzer import LogAnalyzer
from ICX2P.TestCase import UpdateBIOS

P = LogAnalyzer(SutConfig.Env.LOG_DIR)
baseline = PlatMisc.root_path() / "ICX2P/Tools/SetupBase/2288服务器setup菜单基线.xlsx"


# POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
def post_test():  # POST: POST Log(TBD) and Information Check
    tc = ('002', '[TC002]POST Information Test', 'POST Information Test')
    result = ReportGen.LogHeaderResult(tc)
    msg_list = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F6]
    capture_start = "STOP_DIMMINFO_SYSTEM_TABLE"
    capture_end = "Press F6 go to SP boot"
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, 60, 120)
        assert MiscLib.verify_msgs_in_log(msg_list, log_cut)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# PM: Warm reset n times, Cold reset n times and AC (TBD)
def warm_reboot(count=5):
    tc = ('003', f'[TC003]Warm reset {count} times', f'Warm reset {count} times test')
    result = ReportGen.LogHeaderResult(tc)
    reboot_fail = 0
    try:
        assert BmcLib.enable_fdmlog_dump()
        tc_dir = os.path.join(SutConfig.Env.LOG_DIR, f"TC{tc[0]}")  # check fdmlog
        dump_dir_b = BmcLib.bmc_dumpinfo(tc_dir, "dump_before", uncom=True)
        fdmlog_b = PlatMisc.read_bmc_dump_log(dump_dir_b, "dump_info/LogDump/fdm_log")
        bmc_event_b = BmcLib.bmc_warning_check().message  # check bmc warning
        assert SetUpLib.boot_to_bios_config()
        logging.info("Warm reset loops: {0}".format(count))
        for i in range(count):  # warm reboot
            logging.info("Warm reset cycle: {0}".format(i + 1))
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)
            logging.debug("Ctrl + Alt + Del key sent")
            if not SetUpLib.continue_to_setup():
                reboot_fail += 1
        dump_dir_a = BmcLib.bmc_dumpinfo(tc_dir, "dump_after", uncom=True)  # check fdmlog
        fdmlog_a = PlatMisc.read_bmc_dump_log(dump_dir_a, "dump_info/LogDump/fdm_log")
        bmc_event_a = BmcLib.bmc_warning_check().message  # check bmc warning
        assert fdmlog_b == fdmlog_a, f"New fdmlog recorded after {count} times warm reset"
        assert bmc_event_b == bmc_event_a, f"New bmc enevts detected after {count} times warm reset"
        assert not reboot_fail, f"Warm reset fail times: {reboot_fail}"
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# DC cycle n times
def cold_reboot(count=5):
    tc = ('004', f'[TC004]Cold reset {count} times', f'Cold reset {count} times test')
    result = ReportGen.LogHeaderResult(tc)
    reboot_fail = 0
    try:
        assert BmcLib.enable_fdmlog_dump()
        tc_dir = os.path.join(SutConfig.Env.LOG_DIR, f"TC{tc[0]}")  # check fdmlog
        dump_dir_b = BmcLib.bmc_dumpinfo(tc_dir, "dump_before", uncom=True)
        fdmlog_b = PlatMisc.read_bmc_dump_log(dump_dir_b, "dump_info/LogDump/fdm_log")
        bmc_event_b = BmcLib.bmc_warning_check().message  # check bmc warning
        assert SetUpLib.boot_to_bios_config()
        logging.info("Cold reset loops: {0}".format(count))
        for j in range(count):  # cold reboot
            logging.info("DC reset cycle: {0}".format(j + 1))
            if not PlatMisc.dcCycle():
                reboot_fail += 1
        dump_dir_a = BmcLib.bmc_dumpinfo(tc_dir, "dump_after", uncom=True)  # check fdmlog
        fdmlog_a = PlatMisc.read_bmc_dump_log(dump_dir_a, "dump_info/LogDump/fdm_log")
        bmc_event_a = BmcLib.bmc_warning_check().message  # check bmc warning
        assert fdmlog_b == fdmlog_a, f"New fdmlog recorded after {count} times cold reset"
        assert bmc_event_b == bmc_event_a, f"New bmc enevts detected after {count} times cold reset"
        assert not reboot_fail, f"Cold reset fail times: {reboot_fail}"
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# PXE Test
@core.test_case(('005', '[TC005] PXE Hotkey Test', 'PXE HotKey Test'))
def pxe_test(n=1):
    for i in range(n):
        if not SetUpLib.boot_with_hotkey(Key.F12, 'F12 is pressed. Go to PXE boot', 180):
            core.capture_screen()
            return
    ReleaseTest.pxe_boot_uefi = True
    return core.Status.Pass


# USB Test
# Precondition: No USB key installed
# OnStart: NA
# OnComplete: USB Configuration Page
def usb_test():
    tc = ('006', '[TC006]USB Test', 'USB Test')
    result = ReportGen.LogHeaderResult(tc)
    msg_list = ['USB Mouse\s+1', 'USB Keyboard\s+1', f'USB Mass Storage\s+{SutConfig.SysCfg.USB_DISK}']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail(capture=True)
        return
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_USB_CFG, 10, 'USB'):
        result.log_fail(capture=True)
        return
    if not SetUpLib.verify_info(msg_list, 7):
        result.log_fail(capture=True)
        return
    core.capture_screen()
    result.log_pass()
    return True


# press F2
def press_f2():
    tc = ('009', '[TC009]Setup菜单用户输入界面按F2切换键盘制式', '支持热键配置')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOTKEY_PROMPT_DEL, 300)
        SetUpLib.send_key(Key.DEL)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, "Press F2", 60)
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'fr-FR')
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'ja-JP')
        SetUpLib.send_key(Key.F2)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'en-US')
        logging.info("Send password...")
        SetUpLib.send_data(Msg.BIOS_PASSWORD)
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'Continue', 30)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Setup: Load default and setting saving - AT test cases below,
def load_default():
    tc = ('011', '[TC011] Load default and setting saving Test', 'BIOS Load default Test')
    result = ReportGen.LogHeaderResult(tc)
    pxe_boot = ["PXE Boot Capability", "<UEFI:IPv4>"]
    boot_fail_policy = ["Boot Fail Policy", "<Boot Retry>"]
    pxe_boot_2 = ["PXE Boot Capability", "<UEFI:IPv6>"]
    boot_fail_policy_2 = ["Boot Fail Policy", "<Cold Boot>"]
    default_options = [boot_fail_policy, pxe_boot]
    changed_options = [boot_fail_policy_2, pxe_boot_2]
    if not SetUpLib.boot_to_page(Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return

    # change option boot fail policy from "Boot Retry" to "Cold Boot"
    logging.info("***change option boot fail policy from Boot Retry to Cold Boot")
    if not SetUpLib.locate_option(Key.DOWN, boot_fail_policy, 15):
        result.log_fail(capture=True)
        return
    SetUpLib.send_key(Key.F5)

    # change pxe option from IPV4 to IPV6
    logging.info("***change pxe option from IPV4 to IPV6")
    if not SetUpLib.locate_option(Key.DOWN, pxe_boot, 15):
        result.log_fail(capture=True)
        return

    logging.info("***Save and reset.")
    SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)

    # Verify modified options
    if not SetUpLib.boot_to_page(Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return
    result.capture_screen()
    if not SetUpLib.verify_options(Key.DOWN, changed_options, 15):
        result.log_fail(capture=True)
        return
    logging.info("***Modified options are verified.")

    logging.info("***Reset defaul by hotkey")
    SetUpLib.send_keys(Key.RESET_DEFAULT, 2)

    # Verify whether options are reset to default
    logging.info("***Verify whether options are reset to default")
    if not SetUpLib.continue_to_page(Msg.PAGE_BOOT):
        result.log_fail(capture=True)
        return
    if not SetUpLib.verify_options(Key.DOWN, default_options, 15):
        result.log_fail(capture=True)
        return

    result.log_pass()
    return True


# Testcase_DRAM_RAPL_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup DRAM RAPL page
def dram_rapl_option_check():
    tc = ('015', '[TC015]Testcase_DRAM_RAPL_001, 菜单项DRAM RAPL选单检查', '支持DRAM RAPL设置')
    result = ReportGen.LogHeaderResult(tc)
    dram_rapl = [['DRAM RAPL', '<Enabled>']]
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_DRAM_RAPL, 20, Msg.DRAM_RAPL_CONFIG):
        result.log_fail()
        return

    if not SetUpLib.verify_options(Key.DOWN, dram_rapl, 4):
        result.log_fail()
        return
    logging.info("**DRAM rapl default value verified.")
    SetUpLib.send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, r'DisabledEnabled', 10):
        result.log_fail()
        return
    logging.info("**DRAM rapl supported values verified.")
    result.log_pass()
    return True


# 检查CDN开关默认值
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Miscellaneous Configuration page
def cnd_default_enable():
    tc = ('017', '[TC017]检查CDN开关默认值', '支持网口CDN特性开关')
    result = ReportGen.LogHeaderResult(tc)
    cdn_status = ['Network CDN', '<Enabled>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 20, 'Miscellaneous')
        assert SetUpLib.verify_options(Key.DOWN, [cdn_status], 12)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Testcase_SecurityBoot_001
def security_boot():
    tc = ('023', '[TC023] Secure Boot默认值', 'Secure Boot默认值')
    result = ReportGen.LogHeaderResult(tc)
    keys_secure_boot = [Key.RIGHT, Key.DOWN, Key.ENTER]
    secureboot_disable = ['Current Secure Boot State\s+Disabled']
    if not SetUpLib.boot_to_setup():
        result.log_fail(capture=True)
        return
    logging.info("Enter secure boot configuration.")
    SetUpLib.send_keys(keys_secure_boot)
    logging.info("Checking secure boot status")
    if not SetUpLib.verify_info(secureboot_disable, 5):
        result.log_fail(capture=True)
        return
    logging.info("**Secure boot default status verified.")
    result.log_pass()
    return True


# Testcase_VTD_002
@core.test_case(('025', '[TC025] Testcase_VTD_002', '关闭VT-d功能启动测试'))
def testcase_vtd_002():
    vt_d_menu = ["Virtualization Configuration", "Intel\(R\) VT for Directed I/O \(VT-d\)"]
    opt_vt = ["Intel\(R\) VT for Directed I/O", "<Enabled>"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, vt_d_menu, 20, "Directed")
        assert SetUpLib.locate_option(Key.DOWN, opt_vt, 4)
        assert SetUpLib.set_option_value('Intel\(R\) VT for Directed I/O', 'Disabled', save=True)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
    finally:
        BmcLib.clear_cmos()


# Testcase_VTD_003
def testcase_vtd_003():
    tc = ('029', '[TC029] Testcase_VID_003', 'VI-d菜单联动测试')
    result = ReportGen.LogHeaderResult(tc)
    opt_vt_enable = ["Intel\(R\) VT for Directed I/O", "<Enabled>"]

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_VIRTUAL_VTD, 20, Msg.VIRTUAL_VTD)
        assert SetUpLib.verify_info(['Interrupt Remapping'],4)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(['Extended APIC'], 10)
        logging.info("VTD enable Interrupt Remapping and Extended APIC can set")
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_VIRTUAL_VTD, 20, Msg.VIRTUAL_VTD)
        assert SetUpLib.locate_option(Key.DOWN, opt_vt_enable, 4)
        assert SetUpLib.set_option_value('Intel\(R\) VT for Directed I/O', 'Disabled', Key.DOWN, 10, True)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(['Extended APIC'], 10) is None
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_VIRTUAL_VTD, 20, Msg.VIRTUAL_VTD)
        assert SetUpLib.verify_info(['Interrupt Remapping'], 4) is None
        result.log_pass()
        return True
    except AssertionError as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# 检查串口log关键信息打印，包括 CPU资源分配 / BIOS版本信息 / PCIE LINK STATUS
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def serial_print_keywords():
    tc = ('026', '[TC026]Testcase_SerialPrint_001', '启动关键信息打印测试')
    result = ReportGen.LogHeaderResult(tc)
    cpu_resource = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SysCfg.CPU_CNT)])
    bios_ver = r"BIOS Version :\s+\d.\d+"
    pcie_lnk = r"PCIE LINK STATUS:"

    def check_process(timeout):
        # CPU Resource Allocation
        cpu_log = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 100,
                                    timeout)
        key_string1 = re.search(cpu_resource, cpu_log)
        assert key_string1, "CPU Resource Allocation not found"
        logging.info("CPU Resource Allocation check pass")
        # BIOS Version
        ver_log = SerialLib.cut_log(Sut.BIOS_COM, "BootType :", "BIOS Date :", 100, timeout)
        key_string2 = re.search(bios_ver, ver_log)
        assert key_string2, "BIOS Revision not found"
        logging.info("BIOS Revision check pass")
        # PCIE LINK STATUS
        pcie_log = SerialLib.cut_log(Sut.BIOS_COM, "Press Del go to Setup Utility", "BIOS boot completed", 100, timeout)
        key_string3 = re.search(pcie_lnk, pcie_log)
        assert key_string3, "[Assert]: PCIE LINK STATUS not found, Confirm whether PCIE device exist"
        logging.info("PCIE LINK STATUS check pass")
        return True

    try:
        # Open serial debug message
        assert BmcLib.debug_message(True)
        assert BmcLib.force_reset()
        assert check_process(timeout=600)
        # Close serial debug message
        assert BmcLib.debug_message(False)
        assert SetUpLib.boot_to_bios_config()
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert check_process(timeout=200)
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        result.log_fail()
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# 检查串口log打印没有任何错误信息：由于DebugMessage有太多干扰项，系统发生故障时默认打印级别就会打印，因此直接默认模式检查
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def serial_print_error_check():
    tc = ('027', '[TC027]Testcase_SerialPrint_003', 'BIOS启动阶段串口报错检查')
    result = ReportGen.LogHeaderResult(tc)
    error_msg = ["error", "fail", "assert", "exception"]
    ignore_list = ["IdFromBmc Fail,Status: Device Error"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        SetUpLib.send_keys(Key.SAVE_RESET, 2)  # bmc reset 4s delay may cause serial output missed the beginning part
        ser_log = SerialLib.cut_log(Sut.BIOS_COM, "BIOS Log @", Msg.BIOS_BOOT_COMPLETE, 120, 120)
        assert MiscLib.verify_msgs_in_log(["BIOS Log @", Msg.BIOS_BOOT_COMPLETE], ser_log)
        for line in ser_log.split("\n"):
            for err in error_msg:
                if not re.search(err, line, re.I):  # 检查错误信息， 忽略大小写
                    continue
                for ig in ignore_list:
                    assert re.search(ig, line), f"[Assert]: {line}"  # 排除例外
                    logging.debug(f"[Ignore]: {line}")
        result.log_pass()
        return True
    except AssertionError as e:
        logging.info(e)
        result.log_fail()


# 依据能效菜单基线文件(ICX2P/Tools/PowerEfficiency/2288V6_PowerEfficiency.csv)验证所有能效场景，其关联选项是否配置正确
# Precondition: 配置好unitool
# OnStart: Boot to linux
# OnComplete: NA
def power_efficiency_mode_loop():
    tc = ('028', '[TC028]Testcase_PowerEfficiency_001', 'PowerEfficiency场景配置测试')
    result = ReportGen.LogHeaderResult(tc)
    baseline = os.path.join(os.path.dirname(__file__), r"..\Tools\PowerEfficiency\2288V6_PowerEfficiency.csv")
    if not os.path.exists(baseline):
        logging.error("Baseline file not found.")
        result.log_skip()
        return
    with open(baseline, "r", encoding="utf-8-sig") as file:
        data = list(csv.reader(file))
    option = "Performance Profile"
    failed_items = {}
    healthy_state = {}
    try:
        origin_event = BmcLib.bmc_warning_check().message  # get bmc health state before test
        for col_index, to_mode in enumerate(data[0][1:]):
            # Set power efficiency mode
            result_index = data[0].index(to_mode) + 1
            data[0].insert(result_index, f"{to_mode}_check")
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_ADV_PM_CFG, 15, "Performance Profile")
            SetUpLib.send_keys([Key.UP])
            assert SetUpLib.set_option_value(option, to_mode, Key.DOWN, 10, save=True)
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
            # Check each mode BMC warning info
            healthy_state[to_mode] = BmcLib.bmc_warning_check().message
            # Check each Attribute's value
            name_list = [row_data[0] for row_data in data[1:]]
            read_res = Sut.UNITOOL.read(*name_list)
            for row_index, attr_name in enumerate(data[1:]):
                key = attr_name[0]
                value = attr_name[data[0].index(f"{to_mode}_check") - 1]
                value = str(int(value, 16)) if ("0x" in value) else value
                read_val = read_res.get(key) if read_res else None
                if read_val != value:
                    if failed_items.get(to_mode):
                        failed_items[to_mode][key] = read_val
                    else:
                        failed_items[to_mode] = {key: read_val}
                    data[row_index + 1].insert(result_index, read_val)
                    continue
                data[row_index + 1].insert(result_index, "pass")
        # Gen test report csv file
        report_path = os.path.join(SutConfig.Env.LOG_DIR, f"TC{tc[0]}")
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        report_file = os.path.join(report_path, "power_efficiency_test_report.csv")
        stylelog.info(f"Detail test report saved at {report_file}")
        with open(report_file, "w", newline="") as report:
            report_writer = csv.writer(report)
            report_writer.writerows(data)
        # show test result in test log
        warning_fail_modes = [mode for mode in healthy_state if healthy_state.get(mode) != origin_event]
        test_result = False if failed_items else True
        logging.info(f"Test result: {test_result}")
        for mode, attr_kv in failed_items.items():
            for att_k, att_v in attr_kv.items():
                stylelog.fail(f"{mode}={att_k}, Read Value={att_v} failed")
        for warn_mode in warning_fail_modes:
            stylelog.warning(f'[Warning] Power efficiency = {warn_mode}: BMC warning detected')
        # Result summary
        assert (not failed_items) and (not warning_fail_modes)
        result.log_pass()
    except Exception as e:
        logging.info(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# used to save the unitool test result,
def _write_txt(option, data):
    report_file = os.path.join(SutConfig.Env.LOG_DIR, "{0}_{1}_result.txt".format(SutConfig.Env.PROJECT_NAME, option))
    with open(report_file, "a+", newline="") as report:
        report.write(data)


# BYO unitool AT test coverd,
def _auto_set_setup(option, maxvalue):
    """
    baseline: setup base line excel
    option: 3 values - ed, index, other, matched with the setup baseline excel, a word string,
    maxvalue: the setup has the max values, e.g OnDieThermalThrottling, refer to csv file (path: LOG_DIR),
    """
    try:
        if not os.path.exists(baseline):
            logging.error("baseline file not found.")
            return
        assert ParsetableLib.build(baseline), 'failed to generate csv file'
        if option == 'ed':
            init_dict = ParsetableLib.read_ed_option()
        elif option == 'index':
            init_dict = ParsetableLib.read_index_option()
        elif option == 'other':
            init_dict = ParsetableLib.read_other_option()
        else:
            logging.info('Unknown Setup option, exit.')
            return
        logging.info('Start to check {0} setup options'.format(option))
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        init_temp = Sut.UNITOOL.read(*(init_dict.keys()))
        check_list = []
        while init_dict[maxvalue]:  # 对应value属性值最多的key
            diff_dict = ParsetableLib.cmp(init_dict, init_temp)
            for key, value in diff_dict.items():
                if not Sut.UNITOOL.write(**{key: value}):  # key:value
                    check_list.append('set failed option:{0}'.format(key))
                    break  # set next one option
                SshLib.execute_command(Sut.OS_SSH, 'reboot')
                time.sleep(60)  # the delay time depends on the SUT CONFIG
                logging.info('Reboot the system...')
                if MiscLib.ping_sut(SutConfig.Env.OS_IP, 300) and \
                        SshLib.interaction(Sut.OS_SSH, ['ls\n'], ['{0}'.format(SutConfig.Env.UNI_PATH.split('/')[2])]):
                    logging.info('Boot to OS Successfully,')
                    _write_txt(option, '{0}={1} - Pass\n'.format(key, value))
                else:
                    check_list.append('test failed option:{0}'.format(key))
                    core.capture_screen(SutConfig.Env.LOG_DIR, key)
                    _write_txt(option, '{0}={1} - Fail\n'.format(key, value))
                    logging.info('Clear CMOS, contionue...')
                    BmcLib.clear_cmos()
                    BmcLib.force_reset()
                    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 300) and not \
                            SshLib.interaction(Sut.OS_SSH, ['ls\n'], ['{0}'.format(SutConfig.Env.UNI_PATH.split('/')[2])]):
                        logging.debug('debug result - {0}'.format(check_list))
                        logging.info('Exit the loop test, check the network and SUT status,')
                        return

        # check the final result, if run all options
        if len(check_list) != 0:
            logging.debug('final result - {0}'.format(check_list))
            logging.info('set {0} setup options loop test -> failed'.format(option))
            return False

        return True
    except Exception as err:
        logging.debug('the value none exist: {0}, move the key to TBD_items'.format(err))
    finally:
        logging.info('Restore the test Env,')
        BmcLib.clear_cmos()


def auto_set_ed():
    tc = ('007', '[TC007]AUTO_TEST_SETUP_ED_VALUE', '遍历设置ENABLE/DISABLE SETUP选项值')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _auto_set_setup('ed', 'OnDieThermalThrottling')
    except AssertionError:
        result.log_fail()
        return
    result.log_pass()
    return True


def auto_set_index():
    tc = ('008', '[TC008]AUTO_TEST_SETUP_INDEX_VALUE', '遍历设置INDEX SETUP选项值')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _auto_set_setup('index', 'RstPcieStorageRemapPort')
    except AssertionError:
        result.log_fail()
        return
    result.log_pass()
    return True


def auto_set_other():
    tc = ('010', '[TC010]AUTO_TEST_SETUP_OTHER_VALUE', '遍历设置OTHER SETUP选项值')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _auto_set_setup('other', 'RstPcieStorageRemapPort[1]')
    except AssertionError:
        result.log_fail()
        return
    result.log_pass()
    return True


# '07 SETUP设置需求, arthur
# 02 支持恢复Setup默认值
# Testcase_LoadDefault_001
# Precondition: 配置好unitool
# OnStart: Boot to linux
# Step: 'UEFI/Legacy模式：
# 1、BIOS启动进入Setup菜单，修改保存非BMC IPMI相关配置项；
# 2、BMC侧输入“ipmcset -d clearcmos”命令；
# 3、X86侧热复位，再次进入菜单，检查BIOS启动是否正常，选项是否恢复默认值，有结果A。
# Expected_Result: A：BIOS启动正常，Setup菜单恢复默认值。
# OnComplete: PowerOff
# set default def, used for tc032
def _set_loadDefault(set_value, os_ip, uni_type=Sut.UNITOOL, ssh_type=Sut.OS_SSH):
    try:
        assert MiscLib.ping_sut(os_ip, 300)
        assert SshLib.interaction(ssh_type, ['ls\n'], ['{0}'.format(SutConfig.Env.UNI_PATH.split('/')[2])])
        res = uni_type.read(*set_value)
        assert uni_type.write(**set_value)
        assert BmcLib.force_reset()
        time.sleep(60)  # the delay time depends on the SUT CONFIG
        logging.info('Reboot the system...')
        # 当前AT平台默认一个legacy系统，如多个系统需替换从boot manger启动指定legacy系统函数
        if MiscLib.ping_sut(os_ip, 300) and SshLib.interaction(ssh_type, ['ls\n'], ['{0}'.format(SutConfig.Env.UNI_PATH.split('/')[2])]):
            assert res != set_value
        BmcLib.clear_cmos()
        assert SetUpLib.boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        res1 = Sut.UNITOOL.read(*set_value)   # read 2nd time,
        assert res == res1, 'setup options restored failed'
        return True
    except Exception as e:
        logging.error(e)
        return


def loadDefault_001_uefi():
    tc = ('012', '[TC012]01 BMC Clearcmos恢复菜单默认值测试', '支持恢复Setup默认值')
    result = ReportGen.LogHeaderResult(tc)
    set_value = {'CoreDisableMask': '10', 'IotEn': '1', 'CompletionTimeoutGlobal': '0'}  # 可根据平台设计增减设置变量
    try:
        assert BmcLib.force_reset()
        assert _set_loadDefault(set_value, SutConfig.Env.OS_IP)
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


def loadDefault_001_legacy():
    tc = ('013', '[TC013]01 BMC Clearcmos恢复菜单默认值测试 LEGACY MODE', '支持恢复Setup默认值')
    result = ReportGen.LogHeaderResult(tc)
    set_value = {'CoreDisableMask': '10', 'IotEn': '1', 'CompletionTimeoutGlobal': '0'}  # 可根据平台设计增减设置变量
    try:
        assert BmcLib.force_reset()
        assert _set_loadDefault(set_value, SutConfig.Env.OS_IP_LEGACY, Sut.UNITOOL_LEGACY_OS, Sut.OS_LEGACY_SSH)  # legacy mode
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        logging.info("还原测试环境")
        BmcLib.clear_cmos()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_OS, 5):
            UpdateBIOS.update_bios(SutConfig.Env.LATEST_BRANCH)
        BmcLib.set_boot_mode("Legacy", once=False)


# 02 支持恢复Setup默认值
# Testcase_LoadDefault_002
# Precondition: 配置好unitool
# OnStart: Boot to linux
# Step: 'UEFI模式：
# '1、BIOS启动进入Setup菜单，修改菜单登录密码，保存退出；
# 2、BMC侧输入“ipmcset -d clearcmos”命令；
# 3、X86侧热复位，再次进入菜单，检查菜单登录密码是否恢复成默认值，有结果A。
# Expected_Result: A：菜单登录密码没有恢复默认值。
# OnComplete: PowerOff
def testcase_loadDefault_002():
    tc = ('014', '[TC014]02 BMC Clearcmos不恢复BIOS密码测试', '支持恢复Setup默认值')
    result = ReportGen.LogHeaderResult(tc)
    try:
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_setup()
        result.log_pass()  # 期望密码不被恢复
        return True
    except AssertionError:
        result.log_fail()


# Testcase_MemorySequence_001 01 内存时序参数设置测试 支持内存时序调整
# Author: Lupeipei
# 1、单板上电，进入到Setup菜单，查看是否存在设置调整内存时序参数的菜单，有结果A；
# 2、退出Setup，启动到OS下，使用uniCfg工具读取内存时序参数，查看默认参数是否正确，有结果B；
# 3、使用uniCfg工具修改内存时序参数变量为Enabled，重启进入OS，再次读取参数值，有结果C
# A：Setup菜单隐藏调整内存时序参数选项；B：参数默认为Disabled；C：读取参数为Enabled。
@core.test_case(("016", "[TC016] 01 内存时序参数设置测试", "支持内存时序调整"))
def testcase_memorysequence_001():
    CHANG_XMPMODE = {"XMPMode": 1}
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MEM_CONFIG, 10, Msg.SPD_CRC)
        assert SetUpLib.verify_info(['Memory Timings Override'], 10) is None
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert SetUpLib.continue_to_boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        res = Sut.UNITOOL.read(*BiosCfg.XMPMODE)
        assert res.get(list(BiosCfg.XMPMODE.keys())[0]) == '0'
        logging.info("XMPMode default value 0")
        assert Sut.UNITOOL.set_config(CHANG_XMPMODE)
        assert SetUpLib.boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        res1 = Sut.UNITOOL.read(*CHANG_XMPMODE)
        assert res1.get(list(CHANG_XMPMODE.keys())[0]) == '1'
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)


# Author: Fubaolin
# System Debug Level日志级别测试
# Precondition: NA
# OnStart: NA
# set:
# 1、单板上电启动，进入到Setup菜单，查看System Debug Level默认值是否正确，有结果A；
# 2、设置打印级别为debug打印，保存重启。观察串口日志打印信息，有结果B；
# 3、单板复位，进入到Setup界面，设置打印级别为Disabled，保存重启，观察串口日志打印信息，有结果C。
#   A：默认为Disabled；
#   B：系统开启debug信息打印；
#   C：除OEMlevel外的打印全部去除。
def _check_msg_in_log(list_info, duration, timeout):
    try:
        resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "BIOS boot completed.", duration, timeout)
        str_flag = 0
        for str_info in list_info:
            results = re.search(str_info, resource)
            if results:
                logging.info('checkin pass： {}'.format(str_info))
                str_flag = str_flag + 1
        assert str_flag != 0, "**checkin list_info fail"
        logging.info('check_msg_in_log pass')
        return True
    except Exception as e:
        logging.error(e)
        return False

@core.test_case(('018', '[TC018] Testcase_BugLevel_001', ' System Debug Level日志级别测试'))
def System_Debug_Level():
    debug_msg_disable = ['Serial Debug Message Level', '<Disabled>']
    debug_msg_enable = ['Serial Debug Message Level', '<Enabled>']
    full_debug_flg = 'START_MRC_RUN'
    try:
        # 开启全打印
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MISC_CONFIG, 20, str(debug_msg_disable[0]))
        assert SetUpLib.locate_option(Key.DOWN, debug_msg_disable, 10), '**debug_msg_disable not found'
        assert SetUpLib.set_option_value(str(debug_msg_enable[0]), 'Enabled', Key.DOWN, save=True), '**set debug_msg_level Enabled  -> failed'
        assert SetUpLib.wait_message(full_debug_flg, 300), "**Booting in full debug message level --> fail"
        assert _check_msg_in_log(SutConfig.SysCfg.OEM_LOG_SUT+Msg.OEM_LOG_COMMON, duration=320, timeout=350)
        logging.info("**full debug message pass")
        # 关闭全打印
        assert BmcLib.force_reset()
        assert SetUpLib.wait_message("BdsWait", 300)
        SetUpLib.send_key(Key.DEL)
        assert SetUpLib.wait_message(Msg.PW_PROMPT, 300)
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.move_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MISC_CONFIG, 20, str(debug_msg_enable[0]))
        assert SetUpLib.locate_option(Key.DOWN, debug_msg_enable, 10), '**debug_msg_enable not found'
        assert SetUpLib.set_option_value(str(debug_msg_disable[0]), 'Disabled', Key.DOWN, save=True), '**set debug_msg_level Disabled -> failed'
        assert _check_msg_in_log(SutConfig.SysCfg.OEM_LOG_SUT+Msg.OEM_LOG_COMMON, duration=120, timeout=200)
        assert not SetUpLib.wait_message(full_debug_flg)
        logging.info('debug_msg_level Disabled pass')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        BmcLib.debug_message(enable=False)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

# Author: Fubaolin
# 装备模式System Debug Level日志级别测试
# Precondition: 装备模式
# OnStart: NA
# set:
# 1、单板启动进入到OS下，执行./uniCfg -r SysDbgLevel,查看默认值是否是Disabled，有结果A；
# 2、执行./uniCfg -w SysDbgLevel:1，使能打印级别，之后reboot复位，观察串口日志打印信息，有结果B；
# 3、进入os下，执行./uniCfg -w SysDbgLevel:0，关闭打印级别，之后reboot复位，观察串口日志打印信息，有结果C。
# A：默认为Disabled；
# B：系统开启debug信息打印；
# C：除OEMlevel外的打印全部去除。
@core.test_case(('020', '[TC020] Testcase_BugLevel_002', ' 装备使能System Debug Level级别测试'))
def Equipment_System_Debug_Level():
    ser_debug_def = {"serialDebugMsgLvl": 0}
    ser_debug_mod = {"serialDebugMsgLvl": 2}
    full_debug_flg = 'START_MRC_RUN'
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.check(**ser_debug_def), '**unitool_read ser_debug fail' 
        assert Sut.UNITOOL.set_config(ser_debug_mod), "**full_debug Enable set fail."      # full_debug Enable
        assert BmcLib.force_reset()
        assert SetUpLib.wait_message(full_debug_flg, 300), "**Booting in full debug message level --> fail"
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 500)
        assert Sut.UNITOOL.set_config(ser_debug_def), "**full_debug disable set fail."      # full_debug disable
        
        assert BmcLib.force_reset()
        assert _check_msg_in_log(SutConfig.SysCfg.OEM_LOG_SUT + Msg.OEM_LOG_COMMON, duration=120, timeout=200)
        SerialLib.clean_buffer(Sut.BIOS_COM)
        assert not SetUpLib.wait_message(full_debug_flg)
        logging.info('debug_msg_level Disabled pass')
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
        BmcLib.debug_message(enable=False)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
