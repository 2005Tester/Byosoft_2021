import logging
import re
import os
import csv
from Core import SerialLib, MiscLib, SshLib
from Core.SutInit import Sut
from ICX2P.BaseLib import SetUpLib, BmcLib, PlatMisc
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from Report import ReportGen


# Test case ID: TC630-TC650

##########################################
#           PCIe Test Cases              #
##########################################

# Author: WangQingshan
# MMIOL资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_mmiol():
    tc = ('630', '[TC630] Testcase_PCIeResource_001', 'MMIOL资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    cpu_rsc_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        stk0 = rsc_data[1][5].split(" - ")[0]
        stk1 = rsc_data[2][5].split(" - ")[0]
        assert stk0, "MMIOL Base not found"
        size_serial = hex(int(stk1, 16) - int(stk0, 16))
        assert size_serial, "MMIOL Size not found"
        logging.info(f"MMIOL_BASE: {stk0.lower()}")
        logging.info(f"MMIOL_SIZE: {size_serial}")
        logging.info("MMIOL Resource Test Pass")
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()


# Author: WangQingshan
# MMIOH资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_mmioh():
    tc = ('631', '[TC631] Testcase_PCIeResource_002', 'MMIOH资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    MMIOH = "MMIO High Base"
    MMIOH_size = "MMIO High Granularity Size"
    cpu_rsc_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, "Common RefCode Configuration"], 10, "MMIO High Base")
        MMIOH_value = SetUpLib.get_option_value([MMIOH, "<.+>"], Key.DOWN, 8)
        MMIOH_size = SetUpLib.get_option_value([MMIOH_size, "<.+>"], Key.DOWN, 8)
        base_scale = 40 if MMIOH_value[-1] == "T" else 30  # T / G
        base_setup = hex(int(MMIOH_value[:-1]) * (1 << base_scale))
        size_setup = hex(int(MMIOH_size[:-1]) * (1 << 30))  # G
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        stk0 = rsc_data[1][6].split(" - ")[0].replace(" ", "")
        stk1 = rsc_data[2][6].split(" - ")[0].replace(" ", "")
        size_serial = hex(int(stk1, 16) - int(stk0, 16))
        logging.info(f"MMIOH_BASE: setup={base_setup} | serial print={stk0.lower()}")
        logging.info(f"MMIOH_SIZE: setup={size_setup} | serial print={size_serial}")
        assert int(stk0, 16) == int(base_setup, 16), "MMIO High Base Mis-Match"
        assert int(size_serial, 16) == int(size_setup, 16), "MMIO High Size Mis-Match"
        logging.info("MMIOH Resource Test Pass")
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()


# Author: WangQingshan
# BIOS提供MMIOH资源调整选项测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_mmioh_menu():
    tc = ('632', '[TC632] Testcase_PCIeResource_003', 'BIOS提供MMIOH资源调整选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    base_default = "13T"
    size_default = "64G"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, "Common RefCode Configuration"], 10, "MMIO High Base")
        base_value = SetUpLib.get_option_value(["MMIO High Base", "<.+>"], Key.DOWN, 8)
        size_value = SetUpLib.get_option_value(["MMIO High Granularity Size", "<.+>"], Key.DOWN, 8)
        logging.info(f"Get MMIOH Base = {base_value}")
        logging.info(f"Get MMIOH Size = {size_value}")
        assert base_value == base_default, f'Expected MMIOH Base default is "{base_default}", actually is "{base_value}"'
        assert size_value == size_default, f'Expected MMIOH Size default is "{size_default}", actually is "{size_value}"'
        result.log_pass()
    except Exception as e:
        logging.info(e)
        result.log_fail()


# Author: WangQingshan
# BIOS提供PCIe 64bit decode选项测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_64b():
    tc = ('633', '[TC633] Testcase_PCIeResource_005', 'BIOS提供PCIe 64bit decode选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        # Set Config
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
        assert SetUpLib.locate_option(Key.DOWN, ["PCI 64-Bit Resource Allocation", "<Enabled>"], 16
                                      ), "Check default value failed"
        logging.info('Check "PCI 64-Bit Resource Allocation" default = <Enabled> pass')
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.verify_options(Key.DOWN, [["PCI 64-Bit Resource Allocation", "<Disabled>"]], 16)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # Check Config
        re_allocate = SerialLib.cut_log(Sut.BIOS_COM,
                                        "Resource allocation Failed. Enabling 64bit MMIO allocation and resetting the system",
                                        "START_SOCKET_0_DIMMINFO_TABLE", 10, 120)
        # 未触发资源不足正常 Disable
        if not re_allocate:
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
            assert SetUpLib.verify_options(Key.DOWN, [["PCI 64-Bit Resource Allocation", "<Disabled>"]], 16)
            logging.info('Check "PCI 64-Bit Resource Allocation" change to <Disabled> pass')
            result.log_pass()
            return True
        # 触发资源不足会强制分配4G以上，且选项强制 Enable
        assert re.search(r"CPU0[\S\s]+?(Stk00[\S\s]+?)(Stk01.+)", re_allocate), "Enabling 64bit MMIO allocation Failed"
        logging.info("Resource allocation Failed. Enabling 64bit MMIO allocation and resetting the system.")
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
        assert SetUpLib.verify_options(Key.DOWN, [["PCI 64-Bit Resource Allocation", "<Enabled>"]], 16)
        logging.info('Check "PCI 64-Bit Resource Allocation" force restore to <Enabled> pass')
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: WangQingshan
# BUS资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_bus():
    tc = ('634', '[TC634] Testcase_PCIeResource_007', 'BUS资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    cpu_rsc_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        for i in rsc_data:
            if not i[0]:
                continue
            if i[0] != "Rsvd":
                assert i[2], "Invalid PCI Bus Allocation Data"
                logging.info(f"BUS Allocation: {i[0]:5} : {i[2]:5}")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# Legacy IO资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_legacyio():
    tc = ('635', '[TC635] Testcase_PCIeResource_008', 'Legacy IO资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    cpu_rsc_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        for i in rsc_data:
            if not i[0]:
                continue
            if i[0] != "Rsvd":
                assert i[3], "Invalid Legacy IO Allocation Data"
                logging.info(f"Legacy IO Allocation: {i[0]:5} : {i[3]:5}")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# Legacy IO资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_resource_ioapic():
    tc = ('636', '[TC636] Testcase_PCIeResource_009', 'IOApic资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    cpu_rsc_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        for i in rsc_data:
            if not i[0]:
                continue
            if i[0] != "Rsvd":
                assert i[4], "Invalid IOApic Allocation Data"
                logging.info(f"IOApic Allocation: {i[0]:5} : {i[4]:5}")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# 【UEFI模式】PCIe设备资源一致性测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def pcie_resource_lspci_uefi():
    tc = ('637', '[TC637] Testcase_PCIeResource_020', '【UEFI模式】PCIe设备资源一致性测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    pcie_bdf = r"PCIE LINK STATUS:\s+(.+):\s+Link up as"

    def get_lspci_info():
        try:
            assert BmcLib.force_reset()
            pcie_slot = SerialLib.cut_log(Sut.BIOS_COM, "PCIE LINK STATUS:", Msg.BIOS_BOOT_COMPLETE, 60, 200)
            assert pcie_slot, "Invalid PCIE LINK STATUS"
            bdf_list = re.findall(pcie_bdf, pcie_slot)
            assert bdf_list, "No PCIe Device Detected, test skipped"
            logging.info(f"Found PCie Device: {bdf_list}")
            assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
            lspci_info = []
            for bdf in bdf_list:
                pcie_cmd = f"lspci -s {bdf} -vvv"
                pci_info = SshLib.execute_command(Sut.OS_SSH, pcie_cmd)
                lspci_info.append(pci_info)
            return lspci_info
        except Exception as e0:
            logging.error(e0)
    # main test process
    try:
        lspci_info = get_lspci_info()
        reboot_cnt = 1
        for cnt in range(9):
            current_lspci = get_lspci_info()
            reboot_cnt += 1
            assert current_lspci == lspci_info, f"Reboot time {reboot_cnt}: lspci info compare fail\n" \
                                                f"Last:{lspci_info}\nCurrent:\n{current_lspci}"
            logging.info(f"Reboot time {reboot_cnt}: lspci info compare pass")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# 【Legacy模式】PCIe设备资源一致性测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def pcie_resource_lspci_legacy():
    tc = ('638', '[TC638] Testcase_PCIeResource_021', '【Legacy模式】PCIe设备资源一致性测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    pcie_bdf = r"PCIE LINK STATUS:\s+(.+):\s+Link up as"

    def get_lspci_info():
        try:
            assert BmcLib.force_reset()
            pcie_slot = SerialLib.cut_log(Sut.BIOS_COM, "PCIE LINK STATUS:", Msg.BIOS_BOOT_COMPLETE, 90, 300)
            assert pcie_slot, "Invalid PCIE LINK STATUS"
            bdf_list = re.findall(pcie_bdf, pcie_slot)
            assert bdf_list, "No PCIe Device Detected, test skipped"
            logging.info(f"Found PCie Device: {bdf_list}")
            assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
            lspci_info = []
            for bdf in bdf_list:
                pcie_cmd = f"lspci -s {bdf} -vvv"
                pci_info = SshLib.execute_command(Sut.OS_SSH, pcie_cmd)
                if not pci_info:
                    return
                lspci_info.append(pci_info)
            return lspci_info
        except Exception as e0:
            logging.error(e0)
    # main test process
    try:
        # assert SetUpLib.enable_legacy_boot()
        lspci_info = get_lspci_info()
        assert lspci_info, "Invalid lspci info data"
        reboot_cnt = 1
        for cnt in range(9):
            current_lspci = get_lspci_info()
            reboot_cnt += 1
            assert current_lspci == lspci_info, f"Reboot time {reboot_cnt}: lspci info compare fail\n" \
                                                f"Last lspci log:\n{lspci_info}\nCurrent lspci log:\n{current_lspci}"
            logging.info(f"Reboot time {reboot_cnt}: lspci info compare pass")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    # finally:
    #     SetUpLib.disable_legacy_boot()


# Author: WangQingshan
# Setup菜单提供ASPM选项测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def aspm_menu_default():
    tc = ('639', '[TC639] Testcase_ASPM_001', 'Setup菜单提供ASPM选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)

    aspm_global = r"PCIe ASPM Support \(Global\)"
    aspm_values = ["Disabled", "Per individual port", "L1 Only"]
    aspm_default = "Disabled"

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 15, "Network CDN")
        assert SetUpLib.locate_option(Key.DOWN, [aspm_global, f"<{aspm_default}>"], 15)  # 验证默认值
        assert SetUpLib.verify_supported_values("".join(aspm_values))  # 验证可选值
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
