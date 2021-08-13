import logging
import re
import os
import csv
from Core import SerialLib, MiscLib, SshLib
from Core.SutInit import Sut
from TCE.BaseLib import SetUpLib, BmcLib, PlatMisc
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Key, Msg
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
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
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
def pcie_resource_ioapic():
    tc = ('636', '[TC636] Testcase_PCIeResource_009', 'IOApic资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
    pcie_bdf = r"PCIE LINK STATUS:\s+(.+):\s+Link up as"

    def get_lspci_info():
        try:
            assert BmcLib.force_reset()
            pcie_slot = SerialLib.cut_log(Sut.BIOS_COM, "PCIE LINK STATUS:", Msg.BIOS_BOOT_COMPLETE, 60, 200)
            assert pcie_slot, "Invalid PCIE LINK STATUS"
            bdf_list = re.findall(pcie_bdf, pcie_slot)
            assert bdf_list, "No PCIe Device Detected, test skipped"
            logging.info(f"Found PCie Device: {bdf_list}")
            assert SetUpLib.boot_suse_from_bm([Msg.UBUNTU], Msg.BIOS_BOOT_COMPLETE)
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
        assert lspci_info, "Invalid lspci info"
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
# Setup菜单提供ASPM选项测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def aspm_menu_default():
    tc = ('639', '[TC639] Testcase_ASPM_001', 'Setup菜单提供ASPM选项测试')
    result = ReportGen.LogHeaderResult(tc)

    aspm_values = ["Disabled", "Per individual port", "L1 Only"]
    aspm_default = "Disabled"

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 15, "Network CDN")
        assert SetUpLib.locate_option(Key.DOWN, [Msg.ASPM_GLOBAL, f"<{aspm_default}>"], 15)  # 验证默认值
        assert SetUpLib.get_all_values(Msg.ASPM_GLOBAL, Key.UP, 10) == aspm_values  # 验证可选值
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# ASPM总开关测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def aspm_global_disable_l1only():
    tc = ('640', '[TC640] Testcase_ASPM_002', 'ASPM总开关测试')
    result = ReportGen.LogHeaderResult(tc)
    aspm_lnkcap_flag = {"Disabled": "not supported", "L1 Only": "L1"}
    save_value = "Disabled"  # ASPM Global默认值

    def aspm_status_check(status):  # 修改global菜单为Disabled/L1 Only，遍历检查IIO与OS pci info
        nonlocal save_value
        try:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 15, "Network CDN")
            assert SetUpLib.get_option_value([Msg.ASPM_GLOBAL, "<.+>"], Key.UP, 10) == save_value  # 检查默认值
            assert SetUpLib.set_option_value(Msg.ASPM_GLOBAL, status, key=Key.UP)
            save_value = status
            assert SetUpLib.back_to_setup_toppage()
            assert SetUpLib.enter_menu(Key.UP, Msg.PATH_IIO_CONFIG, 15, Msg.IIO_CONFIG)
            for cpu in range(SutConfig.SysCfg.CPU_CNT):  # CPU遍历
                cpu_menu = f"CPU {cpu + 1} Configuration"
                assert SetUpLib.enter_menu(Key.DOWN, [cpu_menu], 15, "PCIe Completion Timeout")
                root_ports = PlatMisc.match_options(Key.DOWN, "(Port (?:DMI|[0-4][A-D]))", 10)
                for port in root_ports:  # Root Port遍历
                    assert SetUpLib.enter_menu(Key.DOWN, [port], 10, "Link Speed")
                    assert not SetUpLib.locate_option(Key.UP, [Msg.ASPM_ROOT_PORT, "<.+>"],
                                                      10), f'"{Msg.ASPM_ROOT_PORT}" should be hidden'
                    logging.info(f'Verify pass: "{Msg.ASPM_ROOT_PORT}" is hidden')
                    SetUpLib.send_keys([Key.ESC])
                SetUpLib.send_keys([Key.ESC])
            SetUpLib.send_keys([Key.F10, Key.Y])  # 检查完毕保存设置重启进OS检查状态
            assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
            assert MiscLib.ping_sut(SutConfig.OS_IP, 300)
            rtn_data = SshLib.execute_command(Sut.OS_SSH, 'lspci |grep "PCI bridge"')  # 进入系统检查 Root Port ASPM 状态
            os_ports_bdf = re.findall("([0-9a-f]{2}:0[2-5].0)", rtn_data)
            assert os_ports_bdf, "Failed to find root ports BDF"
            for os_port in os_ports_bdf:
                port_rtn = SshLib.execute_command(Sut.OS_SSH, f"lspci -s {os_port} -vvv |grep LnkCap")
                assert port_rtn, f"Get invalid bdf： {os_port}"
                assert re.search(f"ASPM.*{aspm_lnkcap_flag.get(save_value)}", port_rtn), \
                    f"{os_port} ASPM status fail:\n{port_rtn}"
                logging.info(f"Verify pass: root port {os_port} ASPM = {save_value}")
            return True
        except Exception as e0:
            logging.error(e0)

    # main test process
    try:
        assert aspm_status_check("Disabled")  # Global默认状态
        assert aspm_status_check("L1 Only")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: WangQingshan
# 遍历Root Port ASPM开关测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def aspm_per_port_loop():
    tc = ('641', '[TC641] Testcase_ASPM_003 / Testcase_ASPM_004', 'Root Port ASPM开关测试 / 遍历Root Port ASPM开关测试')
    result = ReportGen.LogHeaderResult(tc)
    iio_aspm_values = ["L1 Only", "Disabled"]
    aspm_lnkcap_flag = {"Disabled": "not supported", "L1 Only": "L1"}
    save_value = "Disabled"  # ASPM per port 默认值

    def iio_aspm_check(value):  # 修改Global为PerPort，遍历修改IIO并检查状态与OS pci info
        nonlocal save_value
        try:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.UP, Msg.PATH_IIO_CONFIG, 15, Msg.IIO_CONFIG)
            for cpu in range(SutConfig.SysCfg.CPU_CNT):  # CPU遍历
                cpu_menu = f"CPU {cpu + 1} Configuration"
                assert SetUpLib.enter_menu(Key.DOWN, [cpu_menu], 15, "PCIe Completion Timeout")
                root_ports = PlatMisc.match_options(Key.DOWN, "(Port (?:DMI|[0-4][A-D]))", 10)  # 动态获取Root Port
                for port in root_ports:  # Root Port遍历
                    assert SetUpLib.enter_menu(Key.DOWN, [port], 10, "Link Speed")
                    assert SetUpLib.get_option_value([Msg.ASPM_ROOT_PORT, "<.+>"], Key.UP, 10) == save_value  # 默认值检查
                    assert SetUpLib.get_all_values(Msg.ASPM_ROOT_PORT, Key.UP, 10) == iio_aspm_values
                    assert SetUpLib.set_option_value(Msg.ASPM_ROOT_PORT, value, key=Key.UP, loc_cnt=8)
                    SetUpLib.send_keys([Key.ESC])
                SetUpLib.send_keys([Key.ESC])
            SetUpLib.send_keys(Key.SAVE_RESET)  # per port 遍历修改完成，保存设置重启进OS检查状态
            save_value = value
            assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
            assert MiscLib.ping_sut(SutConfig.OS_IP, 300)
            rtn_data = SshLib.execute_command(Sut.OS_SSH, 'lspci |grep "PCI bridge"')  # 进入系统检查 Root Port ASPM 状态
            os_ports_bdf = re.findall("([0-9a-f]{2}:0[2-5].0)", rtn_data)
            assert os_ports_bdf, "Failed to find root ports BDF"
            for os_port in os_ports_bdf:
                port_rtn = SshLib.execute_command(Sut.OS_SSH, f"lspci -s {os_port} -vvv |grep LnkCap")
                assert port_rtn, f"Get invalid lspci info： {os_port}"
                assert re.search(f"ASPM.*{aspm_lnkcap_flag.get(save_value)}",
                                 port_rtn), f"{os_port} ASPM status fail:\n{port_rtn}"
                logging.info(f"Verify pass: root port {os_port} ASPM = {save_value}")
            return True
        except Exception as e0:
            logging.error(e0)

    # main test process
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MISC_CONFIG], 15, "Network CDN")
        assert SetUpLib.locate_option(Key.UP, [Msg.ASPM_GLOBAL, "<.+>"], 10)
        assert SetUpLib.set_option_value(Msg.ASPM_GLOBAL, "Per individual port", key=Key.UP, save=True)
        for value in iio_aspm_values:
            assert iio_aspm_check(value)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: WangQingshan
# Setup菜单提供SRIOV选项测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def sriov_global_menu():
    tc = ('642', '[TC642] Testcase_SRIOV_001', 'Setup菜单提供SRIOV选项测试')
    result = ReportGen.LogHeaderResult(tc)
    sriov_vals = ["Disabled", "Enabled", "Per IIO Port"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, [Msg.VIRTUAL_CFG], 5, Msg.VIRTUAL_CFG)
        assert SetUpLib.get_option_value([Msg.SRIOV_GLOBAL, "<.+>"], Key.UP, 3) == "Enabled"  # 默认值检查
        assert SetUpLib.get_all_values(Msg.SRIOV_GLOBAL, Key.DOWN, 5) == sriov_vals  # 可选值检查
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# SRIOV总开关测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def sriov_enable_disable():
    tc = ('643', '[TC643] Testcase_SRIOV_002', 'SRIOV总开关测试')
    result = ReportGen.LogHeaderResult(tc)

    def sriov_status_check(status):
        try:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.UP, [Msg.VIRTUAL_CFG], 5, Msg.VIRTUAL_CFG)
            assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, status, Key.UP, 4, save=True)
            pcie_bdf = SerialLib.cut_log(Sut.BIOS_COM, "PCIE LINK STATUS:", Msg.BIOS_BOOT_COMPLETE, 20, 200)
            assert pcie_bdf, "Invalid PCIE LINK STATUS"
            bdf_list = re.findall("PCIE LINK STATUS: ([0-9a-fA-F]+:[0-4]+\.[0-9a-fA-F])", pcie_bdf)
            assert bdf_list, "Invalid BDF"
            logging.info(f"PCIE Bus: {bdf_list}")
            assert SetUpLib.boot_suse_from_bm([Msg.UBUNTU], Msg.BIOS_BOOT_COMPLETE)
            assert MiscLib.ping_sut(SutConfig.OS_IP, 300)
            sriov_sup_port = {}
            for port in bdf_list:
                port_info = SshLib.execute_command(Sut.OS_SSH, f"lspci -s {port} -vvv")
                if "SR-IOV" in port_info:
                    logging.info(f"{port} support SR-IOV, start to check BAR resource")
                    sriov_sup_port[port] = port_info
                    sriov_info = re.findall("\(SR-IOV\)([\S\s]*)VF Migration:", port_info)
                    assert sriov_info, "Find SRIOV detail information failed"
                    bars = re.findall("(Region \d): Memory at (\w+)", sriov_info[0])
                    assert bars, f"Find SR-IOV bar resource failed"
                    for bar in bars:
                        region_addr = int(bar[1], 16)
                        assert region_addr != 0, f"SR-IOV resource allocate fail: {port} {bar}, this is OS related, please double check in other OS"
                    logging.info(f"Verify {port} SR-IOV pass: {bars}")
            if not sriov_sup_port:
                return 0
            return True
        except Exception as e0:
            logging.error(e0)

    try:
        sriov_en_check = sriov_status_check("Enabled")
        if sriov_en_check == 0:
            logging.info("No PCIE devices support SR-IOV, test skipped")
            result.log_skip()
            return
        assert sriov_en_check
        sriov_dis_check = sriov_status_check("Disabled")
        assert sriov_dis_check
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: WangQingshan
# 遍历Root Port SR-IOV开关测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def sriov_per_port_loop():
    tc = ('644', '[TC644] Testcase_SRIOV_003 / Testcase_SRIOV_005', '遍历Root Port SR-IOV开关测试')
    result = ReportGen.LogHeaderResult(tc)

    def sriov_per_port_switch(value):
        try:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.UP, [Msg.VIRTUAL_CFG], 5, Msg.VIRTUAL_CFG)
            port_list = PlatMisc.match_options(Key.DOWN, r"(CPU \d Port (?:DMI|[0-4][A-D]) SR-IOV Support)", 15)
            for port in port_list:
                assert SetUpLib.set_option_value(port, value, save=False)
            SetUpLib.send_keys(Key.SAVE_RESET)
            link_sts = SerialLib.cut_log(Sut.BIOS_COM, "PCIE LINK STATUS:.+", Msg.BIOS_BOOT_COMPLETE, 30, 300)
            assert link_sts, "Invalid PCIE LINK STATUS"
            bdf_list = re.findall("PCIE LINK STATUS: ([0-9a-fA-F]+:[0-4]+\.[0-9a-fA-F])", link_sts)
            assert bdf_list, "Invalid BDF"
            logging.info(f"PCIE Bus: {bdf_list}")
            assert SetUpLib.boot_suse_from_bm([Msg.UBUNTU], Msg.BIOS_BOOT_COMPLETE)
            MiscLib.ping_sut(SutConfig.OS_IP, 300)
            sriov_sup_port = {}
            for port in bdf_list:
                port_info = SshLib.execute_command(Sut.OS_SSH, f"lspci -s {port} -vvv")
                if "SR-IOV" in port_info:
                    logging.info(f"{port} support SR-IOV, start to check BAR resource")
                    sriov_sup_port[port] = port_info
                    sriov_info = re.findall("\(SR-IOV\)([\S\s]*)VF Migration:", port_info)
                    assert sriov_info, "Find SRIOV detail information failed"
                    bars = re.findall("(Region \d): Memory at (\w+)", sriov_info[0])
                    assert bars, f"Find SR-IOV bar resource failed"
                    for bar in bars:
                        region_addr = int(bar[1], 16)
                        assert region_addr != 0, f"SR-IOV resource allocate fail: {port} {bar}, this is OS related, please double check in other OS"
                    logging.info(f"Verify {port} SR-IOV pass: {bars}")
            if not sriov_sup_port:
                return 0
            return True
        except Exception as e0:
            logging.error(e0)

    # main test process
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, [Msg.VIRTUAL_CFG], 5, Msg.VIRTUAL_CFG)
        assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, "Per IIO Port", save=True)
        sriov_per_port = sriov_per_port_switch("Disabled")
        if sriov_per_port == 0:
            logging.info("No PCIE devices support SR-IOV, test skipped")
            result.log_skip()
            return
        assert sriov_per_port
        assert sriov_per_port_switch("Enabled")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: WangQingshan
# Setup菜单提供CPU RootPort端口开关测试
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def root_port_switch_menu():
    tc = ('645', '[TC645] Testcase_PCIePortItem_001', 'Setup菜单提供CPU RootPort端口开关测试')
    result = ReportGen.LogHeaderResult(tc)
    switch_option = "PCIe Port"
    switch_value = ["Auto", "Disabled", "Enabled"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_IIO_CONFIG, 15, Msg.IIO_CONFIG)
        for cpu in range(SutConfig.SysCfg.CPU_CNT):  # CPU遍历
            cpu_menu = f"CPU {cpu + 1} Configuration"
            assert SetUpLib.enter_menu(Key.DOWN, [cpu_menu], 15, "PCIe Completion Timeout")
            root_ports = PlatMisc.match_options(Key.DOWN, "(Port (?:[0-4][A-D]))", 10)
            for port in root_ports:  # Root Port遍历
                assert SetUpLib.enter_menu(Key.DOWN, [port], 10, "PCIe Port")
                SetUpLib.send_key(Key.DOWN)
                assert SetUpLib.get_all_values(switch_option, Key.UP, 15) == switch_value
                SetUpLib.send_keys([Key.ESC])
            SetUpLib.send_keys([Key.ESC])
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
