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
from Core import SerialLib, MiscLib
from Core.SutInit import Sut
from TCE.Config.SutConfig import SysCfg
from TCE.Config.PlatConfig import Msg, Key
from TCE.Config import SutConfig
from TCE.BaseLib import BmcLib, PlatMisc, SetUpLib
from Report import ReportGen
from Common.LogAnalyzer import LogAnalyzer

P = LogAnalyzer(SutConfig.LOG_DIR)


# POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
def post_test():  # POST: POST Log(TBD) and Information Check
    tc = ('002', '[TC002]POST Information Test', 'POST Information Test')
    result = ReportGen.LogHeaderResult(tc)
    msg_list = [Msg.HOTKEY_PROMPT_DEL, Msg.HOTKEY_PROMPT_F11, Msg.HOTKEY_PROMPT_F12, Msg.HOTKEY_PROMPT_F6]
    capture_start = "STOP_DIMMINFO_SYSTEM_TABLE"
    capture_end = "Press F6 go to SP boot"
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, 100, 150)
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
        tc_dir = os.path.join(SutConfig.LOG_DIR, f"TC{tc[0]}")  # check fdmlog
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
        tc_dir = os.path.join(SutConfig.LOG_DIR, f"TC{tc[0]}")  # check fdmlog
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
def pxe_test(n=1):
    tc = ('005', '[TC005] PXE Hotkey Test', 'PXE HotKey Test')
    result = ReportGen.LogHeaderResult(tc)
    for i in range(n):
        if not SetUpLib.boot_with_hotkey(Key.F12, 'NBP file downloaded successfully', 180):
            result.log_fail()
            return
    result.log_pass()
    ReleaseTestStatus.pxe_boot_uefi = True
    return True


# USB Test
# Precondition: No USB key installed
# OnStart: NA
# OnComplete: USB Configuration Page
def usb_test():
    tc = ('006', '[TC006]USB Test', 'USB Test')
    result = ReportGen.LogHeaderResult(tc)
    msg_list = ['USB Mouse\s+1', 'USB Keyboard\s+1', f'USB Mass Storage\s+{SutConfig.SysCfg.USB_Storage}']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail(capture=True)
        return

    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_USB_CFG, 10, 'USB'):
        result.log_fail(capture=True)
        return

    if not SetUpLib.verify_info(msg_list, 7):
        result.log_fail()
        return
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
        SetUpLib.send_data(SutConfig.BIOS_PASSWORD)
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'Continue', 30)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


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
def vtd():
    tc = ('025', '[TC025] Testcase_VTD_002', '关闭VT-d功能启动测试')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    vt_d_menu = ["Virtualization Configuration", "Intel\(R\) VT for Directed I/O \(VT-d\)"]
    if not SetUpLib.enter_menu(Key.DOWN, vt_d_menu, 20, "Directed"):
        logging.info("Failed to vir config")
        result.log_fail()
        return
    opt_vt = ["Intel\(R\) VT for Directed I/O", "<Enabled>"]
    if not SetUpLib.locate_option(Key.DOWN, opt_vt, 4):
        result.log_fail()
        return
    logging.info("Diasble VT-d")
    SetUpLib.send_key(Key.F5)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, "Disabled"):
        logging.info("VT-d option is not disaled.")
        result.log_fail()
        return
    logging.info("Save and reboot")
    SetUpLib.send_keys([Key.F10, Key.Y])
    assert SetUpLib.continue_to_boot_suse_from_bm()
    logging.info("Verify OS boot with VT-D disabled.")
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
        logging.info("OS boot failed")
        result.log_fail()
        return

    result.log_pass()
    return True


# 检查串口log关键信息打印，包括 CPU资源分配 / BIOS版本信息 / PCIE LINK STATUS
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def serial_print_keywords():
    tc = ('026', '[TC026]Testcase_SerialPrint_001', '启动关键信息打印测试')
    result = ReportGen.LogHeaderResult(tc)
    cpu_resource = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SysCfg.CPU_CNT)])
    bios_ver = r"BIOS Revision :\s+\d.\d+"
    pcie_lnk = r"PCIE LINK STATUS:"

    def check_process(timeout):
        # CPU Resource Allocation
        cpu_log = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 100,
                                    timeout)
        key_string1 = re.search(cpu_resource, cpu_log)
        assert key_string1, "CPU Resource Allocation not found"
        logging.info("CPU Resource Allocation check pass")
        # BIOS Revision
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
        SetUpLib.send_keys(Key.CTRL_ALT_DELETE)
        assert check_process(timeout=300)
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
        SetUpLib.send_keys(Key.SAVE_RESET)  # bmc reset 4s delay may cause serial output missed the beginning part
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


# 依据能效菜单基线文件(TCE/Tools/PowerEfficiency/TCE_PowerEfficiency.csv)验证所有能效场景，其关联选项是否配置正确
# Precondition: 配置好unitool
# OnStart: Boot to linux
# OnComplete: NA
def power_efficiency_mode_loop():
    tc = ('028', '[TC028]Testcase_PowerEfficiency_001', 'PowerEfficiency场景配置测试')
    result = ReportGen.LogHeaderResult(tc)
    baseline = os.path.join(os.path.dirname(__file__), r"..\Tools\PowerEfficiency\TCE_PowerEfficiency.csv")
    if not os.path.exists(baseline):
        logging.error("Baseline file not found.")
        result.log_skip()
        return
    with open(baseline, "r", encoding="utf-8-sig") as file:
        data = list(csv.reader(file))
    option = "Performance Profile"
    # list order must follow the bios menu sequence
    value_list = ["Custom", "Efficiency", "Performance", "Load Balance", "High RAS", "HPC", "General Computing",
                  "Low Latency", "Server Side Java", "Memory Throughput", "I/O Throughput", "Energy Saving", "NFV"]
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
            SetUpLib.send_key(Key.UP)
            time.sleep(2)
            assert SetUpLib.set_option_value(option, to_mode, Key.DOWN, 10, save=True)
            assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
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
        report_path = os.path.join(SutConfig.LOG_DIR, f"TC{tc[0]}")
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        report_file = os.path.join(report_path, "power_efficiency_test_report.csv")
        logging.info(f"Detail test report saved at {report_file}")
        with open(report_file, "w", newline="") as report:
            report_writer = csv.writer(report)
            report_writer.writerows(data)
        # show test result in test log
        warning_fail_modes = [mode for mode in healthy_state if healthy_state.get(mode) != origin_event]
        test_result = False if failed_items else True
        logging.info(f"Test result: {test_result}")
        for mode, attr_kv in failed_items.items():
            for att_k, att_v in attr_kv.items():
                logging.info(f"{mode}={att_k}, Read Value={att_v} failed")
        for warn_mode in warning_fail_modes:
            logging.info(f'[Warning] Power efficiency = {warn_mode}: BMC warning detected')
        # Result summary
        assert (not failed_items) and (not warning_fail_modes)
        result.log_pass()
    except Exception as e:
        logging.info(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()
