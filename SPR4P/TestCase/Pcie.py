import csv
import logging

from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Pcie Test Case
# TC 1300-1353
####################################


def _get_pcie_resource_region(uefi=True, reset=True):
    """从串口读取PCIE RootPort和Device的BDF，然后进OS，检查Endpoint的资源分配"""
    bdf_info = PlatMisc.get_pcie_bdf(reset)
    if bdf_info:
        resource_region = {}
        assert SetUpLib.boot_to_default_os(reset=False, uefi=uefi)
        for root_port, end_point in bdf_info.items():
            for end_bdf in end_point:
                sut_ssh = Sut.OS_SSH if uefi else Sut.OS_LEGACY_SSH
                is_endpoint = SshLib.execute_command(sut_ssh, f"lspci -s {end_bdf} -vvv |grep Endpoint")
                if is_endpoint:
                    region = SshLib.execute_command(sut_ssh, f"lspci -s {end_bdf} -vvv |grep size=")
                    resource_region[end_bdf] = region
        for bdf, reg in resource_region.items():
            logging.info(f"Device {bdf} region: {reg}")
        return resource_region
    else:
        logging.warning("No pcie device found")


def _pcie_iio_port_test(option, option_exist=True, value_read=None, value_set=None, value_list=None):
    """检查每一个 IIO Root Port下的选项，支持检查可选值，默认值，和设置值（不保存）"""
    for cpu in range(Sys.CPU_CNT):
        socket_option = f"Socket {cpu + 1} Configuration"
        assert SetUpLib.enter_menu(socket_option, key=Key.UP)
        cpu_ports = SetUpLib.get_all_options()
        for cpu_port in cpu_ports:
            if not re.search("Port \w{2}", cpu_port):
                continue
            assert SetUpLib.enter_menu(cpu_port, key=Key.UP)
            if option_exist:
                option_found = False
                if value_list:
                    assert MiscLib.same_values(SetUpLib.get_all_values(option), value_list)
                    option_found = True
                if value_read:
                    assert SetUpLib.get_option_value(option) == value_read, f"ASPM Value != {value_read}"
                    option_found = True
                if value_set:
                    assert SetUpLib.set_option_value(option, value_set)
                    option_found = True
                if not option_found:
                    port_options = SetUpLib.get_all_options()
                    assert option in port_options, f"CPU{cpu} PORT {cpu_port} option not found: {option}"
            else:
                port_options = SetUpLib.get_all_options()
                assert option not in port_options, f"CPU{cpu} PORT {cpu_port} option found: {option}"
            SetUpLib.send_keys([Key.ESC], delay=2)
        SetUpLib.send_keys([Key.ESC], delay=2)
    return True


def _aspm_root_port_os_check(aspm_value, reset=True):
    """从串口读取PCIE RootPort和Device的BDF，然后进OS，检查RootPort的ASPM状态"""
    aspm_dict = {Msg.VAL_ASPM[0]: "ASPM not supported", Msg.VAL_ASPM[2]: "ASPM L1"}
    bdf_info = PlatMisc.get_pcie_bdf(reset)
    assert SetUpLib.boot_to_default_os(reset=False, uefi=True)
    for root_port, end_point in bdf_info.items():
        is_endpoint = SshLib.execute_command(Sut.OS_SSH, f'lspci -s {root_port} -vvv |grep "Root Port"')
        if is_endpoint:
            pcie_dev_info = SshLib.execute_command(Sut.OS_SSH, f"lspci -s {root_port} -vvv |grep -i LnkCap: -A1")
            logging.info(f"ASPM Setting={aspm_value}, OS ASPM Status={aspm_dict.get(aspm_value)}")
            assert aspm_dict.get(aspm_value) in pcie_dev_info, f"PCIE root port aspm mismatch"
            logging.info(f"PCIE root port aspm match")
    return True


def _sriov_bar_resource_check():
    """Check SRIOV BARs in Linux"""
    bdf_info = PlatMisc.get_pcie_bdf(reset=True)
    assert SetUpLib.boot_to_default_os(reset=False, uefi=True)
    bars_dict = {}
    for root_port, end_point in bdf_info.items():
        for end_bdf in end_point:
            is_endpoint = SshLib.execute_command(Sut.OS_SSH, f'lspci -s {end_bdf} -vvv |grep "Endpoint"')
            if is_endpoint:
                sriov_cap = SshLib.execute_command(Sut.OS_SSH, f'lspci -s {end_bdf} -vvv |grep "SR-IOV"')
                if not sriov_cap:
                    continue
                logging.info(f"PCIE device support SR-IOV: {end_bdf}")
                caps = SshLib.execute_command(Sut.OS_SSH, f'lspci -s {end_bdf} -vvv')
                caps_list = caps.split("Capabilities:")
                for cap in caps_list:
                    if "SR-IOV" in cap:
                        bar_list = re.findall("Region \d+:.+", cap)
                        if bar_list:
                            bars_dict[end_bdf] = bar_list
    for dev, bar in bars_dict.items():
        logging.info(f"SR-IOV BARs: {dev}: {bar}")
    return bars_dict


def _mem_size(addr: str):
    int16 = int(addr, 16)
    if int16 <= 64 * 2**10:  # 64K = IO Space
        return -1
    addr_bin = bin(int16)
    addr_bit = len(addr_bin[2:])
    if addr_bit > 32:
        return 64
    return 32


def _lspci_range(bdf, uefi=True):
    ssh = Sut.OS_SSH if uefi else Sut.OS_LEGACY_SSH
    lspci = SshLib.execute_command(ssh, f"lspci -s {bdf} -vvv |grep size=")
    lspci_list = set()
    for pci_line in lspci.splitlines():
        base_size = re.findall("(?:Memory|Expansion ROM) at ([0-9a-f]+) .* \[size=(\d+)(K|M|G)]", pci_line)
        if base_size:
            base, size, unit = base_size[0]
            mem_start = int(base, 16)
            unit_int = 2 ** 10 if unit == "K" else (2 ** 20 if unit == "M" else 2 ** 30)
            mem_end = mem_start + int(size) * unit_int - 1
            lspci_list.add(f"{hex(mem_start)[2:]}-{hex(mem_end)[2:]}")
    for _bdf in lspci_list:
        logging.info(f"[lspci] {bdf}: {_bdf}")
    return lspci_list


def _iomem_range(bdf, uefi=True):
    ssh = Sut.OS_SSH if uefi else Sut.OS_LEGACY_SSH
    iomem = SshLib.execute_command(ssh, f"cat /proc/iomem |grep {bdf}")
    iomem_list = set()
    for io_line in iomem.splitlines():
        mem_range = re.findall("({0}-{0})".format("[0-9a-fA-F]+"), io_line)
        if mem_range:
            iomem_list.add(mem_range[0])
    for _bdf in iomem_list:
        logging.info(f"[iomem] {bdf}: {_bdf}")
    return iomem_list


def _post_mem_range(bdf, log):
    post_range = set()
    bus, dev, func = re.split(":|\.", bdf.upper())
    bdf_find = re.findall(f"Base = 0x([0-9a-fA-F]+).*Length = 0x([0-9a-fA-F]+).*Owner = PCI \[{bus:0>2}\|{dev:0>2}\|{func:0>2}:", log)
    if bdf_find:
        for post_mem in bdf_find:
            base, size = post_mem
            if _mem_size(base) == -1:
                continue
            mem_start = int(base, 16)
            mem_end = mem_start + int(size, 16) - 1
            post_range.add(f"{hex(mem_start)[2:]}-{hex(mem_end)[2:]}")
    for _bdf in post_range:
        logging.info(f"[post resource map] {bdf}: {_bdf}")
    return post_range


@core.test_case(("1300", "[TC1300] Testcase_PcieInit_001", "PCIe带宽默认值测试"))
def Testcase_PcieInit_001():
    """
    Name:       PCIe带宽默认值测试
    Condition:  1、单板不插Riser卡。
    Steps:      1、启动进Setup菜单，IIO界面查看各Root Port的带宽分配是否与软硬件接口文档描述一致，有结果A；
                2、对比软硬件接口文档，检查菜单是否隐藏未使用的Root Port，有结果B。
    Result:     A：带宽默认配置与软硬件接口文档一致；
                B：未使用的RootPort均已隐藏。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        for cpu in range(SutConfig.Sys.CPU_CNT):  # loop cpu
            cpu_menu = f"Socket {cpu + 1} Configuration"
            assert SetUpLib.enter_menu([cpu_menu], Key.DOWN)
            options = SetUpLib.get_all_options()
            for port in options:  # loop root port
                if not port:
                    continue
                root_port = re.findall("Port (\w+)", port)
                if root_port:
                    assert SetUpLib.enter_menu(port, key=Key.UP)
                    band_width = Env.PCIE_MAP[cpu].get(root_port[0].lower()).lower()
                    assert SetUpLib.get_option_value("PCIe Port Link Max Width", integer=None) == f"Max Width {band_width}"
                SetUpLib.send_key(Key.ESC, delay=1)
            SetUpLib.send_key(Key.ESC, delay=1)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1302", "[TC1302] Testcase_PcieResource_001", "BUS资源分配初始值检查"))
def Testcase_PcieResource_001():
    """
    Name:       BUS资源分配初始值检查
    Condition:  1、已提供资源分配方案；
                2、单板接PCIe外设尽量少。
    Steps:      1、单板上电启动，检查串口打印各Socket Stack下BUS资源分配大小（搜“CPU Resource Allocation”），有结果A。
    Result:     A：BUS资源按方案文档进行分配。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档。
    """
    cpu_rsc_file = os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv")
    stack_valid = ["Stk00", "Stk01", "Stk02", "Stk03", "Stk04", "Stk05", "Stk08", "Stk09", "Stk10", "Stk11", "Ubox"]
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        if not MiscLib.ping_sut(Env.OS_IP, Env.BOOT_DELAY):
            assert SetUpLib.boot_to_default_os()
        for i in range(len(rsc_data)):
            line_num = i + 1
            if line_num >= len(rsc_data):
                continue
            if not rsc_data[line_num]:
                continue
            if rsc_data[line_num][0] not in stack_valid:
                continue
            stk_n_bus = rsc_data[line_num][3].split(" - ")[0][2:]
            logging.info(f"Stack{i} BUS: {stk_n_bus}")
            assert SshLib.execute_command(Sut.OS_SSH, f"lspci |grep -i {stk_n_bus}:"), f"Stack BUS not found: {stk_n_bus}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1303", "[TC1303] Testcase_PcieResource_002", "IO资源分配初始值检查"))
def Testcase_PcieResource_002():
    """
    Name:       IO资源分配初始值检查
    Condition:  1、已提供资源分配方案；
                2、单板接PCIe外设尽量少。
    Steps:      1、单板上电启动，检查串口打印各Socket Stack下IO资源分配大小（搜“CPU Resource Allocation”），有结果A。
    Result:     A：IO资源按方案文档进行分配。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档。
    """
    cpu_rsc_file = os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv")
    stack_valid = ["Stk00", "Stk01", "Stk02", "Stk03", "Stk04", "Stk05", "Stk08", "Stk09", "Stk10", "Stk11", "Ubox"]
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        for i in range(6):
            line_num = i + 1
            if line_num >= len(rsc_data):
                continue
            if not rsc_data[line_num]:
                continue
            if rsc_data[line_num][0] not in stack_valid:
                continue
            stk_n_io = rsc_data[line_num][4]
            logging.info(f"Stack{i} IO: {stk_n_io}")
            assert stk_n_io.split(" - ")[0] != "0xFFFF", f"Stack{i} IO Invalid: {stk_n_io}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1304", "[TC1304] Testcase_PcieResource_003", "IOApic资源分配初始值检查"))
def Testcase_PcieResource_003():
    """
    Name:       IOApic资源分配初始值检查
    Condition:  1、已提供资源分配方案；
                2、单板接PCIe外设尽量少。
    Steps:      1、单板上电启动，检查串口打印各Socket Stack下IOApic资源分配大小（搜“CPU Resource Allocation”），有结果A。
    Result:     A：IOApic资源按方案文档进行分配。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档。
    """
    base_default = "32T"  # 4P
    size_default = "256G" # 4P
    if SutConfig.Env.MAX_CPU_CNT == 2:
        base_default = "13T"  # 2P
        size_default = "64G"  # 2P 默认64G

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL, Key.DOWN)
        base_value = SetUpLib.get_option_value(Msg.MMIOH_BASE, Key.DOWN)
        size_value = SetUpLib.get_option_value(Msg.MMIOH_SIZE, Key.DOWN)
        logging.info(f"Get MMIO Base = {base_value}")
        logging.info(f"Get MMIO Size = {size_value}")
        assert base_value == base_default, f'Expected MMIO Base default is "{base_default}", actually is "{base_value}"'
        assert size_value == size_default, f'Expected MMIO Size default is "{size_default}", actually is "{size_value}"'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1305", "[TC1305] Testcase_PcieResource_004", "MMIOL资源分配初始值检查"))
def Testcase_PcieResource_004():
    """
    Name:       MMIOL资源分配初始值检查
    Condition:  1、已提供资源分配方案；
                2、单板接PCIe外设尽量少。
    Steps:      1、单板上电启动，检查串口打印各Socket Stack下MMIOL资源分配大小（搜“CPU Resource Allocation”关键字），有结果A。
    Result:     A：MMIOL资源按方案文档进行分配。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档。
    """
    cpu_rsc_file = os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv")
    try:
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        stk0 = rsc_data[1][6].split(" - ")[0]
        stk1 = rsc_data[2][6].split(" - ")[0]
        assert stk0, "MMIOL Base not found"
        size_serial = hex(int(stk1, 16) - int(stk0, 16))
        assert size_serial, "MMIOL Size not found"
        logging.info(f"MMIOL_BASE: {stk0.lower()}")
        logging.info(f"MMIOL_SIZE: {size_serial}")
        logging.info("MMIOL Resource Test Pass")
        return core.Status.Pass
    except Exception as e:
        logging.info(e)
        return core.Status.Fail


@core.test_case(("1306", "[TC1306] Testcase_PcieResource_005", "MMIOH资源分配初始值检查"))
def Testcase_PcieResource_005():
    """
    Name:       MMIOH资源分配初始值检查
    Condition:  1、已提供资源分配方案；
                2、单板接PCIe外设尽量少。
    Steps:      1、单板上电启动，检查串口打印各Socket Stack下MMIOH资源分配大小（搜“CPU Resource Allocation”关键字），有结果A。
    Result:     A：MMIOH资源按方案文档进行分配。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档。
    """
    cpu_rsc_file = os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv")
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL, Key.DOWN)
        MMIO_value = SetUpLib.get_option_value(Msg.MMIOH_BASE, Key.DOWN)
        MMIO_size = SetUpLib.get_option_value(Msg.MMIOH_SIZE, Key.DOWN)
        base_scale = 40 if MMIO_value[-1] == "T" else 30  # T / G
        base_setup = hex(int(MMIO_value[:-1]) * (1 << base_scale))
        size_setup = hex(int(MMIO_size[:-1]) * (1 << 30))  # G
        if not os.path.exists(cpu_rsc_file):
            cpu_rsc_file = PlatMisc.dump_cpu_resource()
            assert cpu_rsc_file, "invalid CPU Resource Allocation Table"
        with open(cpu_rsc_file, "r") as rsc_file:
            rsc_data = list(csv.reader(rsc_file))
        stk0 = rsc_data[1][7].split(" - ")[0].replace(" ", "")
        stk1 = rsc_data[2][7].split(" - ")[0].replace(" ", "")
        size_serial = hex(int(stk1, 16) - int(stk0, 16))
        logging.info(f"MMIO_BASE: setup={base_setup} | serial print={stk0.lower()}")
        logging.info(f"MMIO_SIZE: setup={size_setup} | serial print={size_serial}")
        assert int(stk0, 16) == int(base_setup, 16), "MMIO High Base Mis-Match"
        assert int(size_serial, 16) == int(size_setup, 16), "MMIO High Size Mis-Match"
        logging.info("MMIO Resource Test Pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case("1307", None, "PCI 64bit 资源分配设置菜单检查")
def Testcase_PcieResource_006():
    """
    Name:       PCI 64bit 资源分配设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，IIO页面下检查是否有PCI 64-bit Resource Allocation选项，可选值及默认值，有结果A；
                2、关闭PCI 64-bit Resource Allocation选项，F10保存重启进Setup菜单，检查选项设置是否生效，有结果B。
    Result:     A：提供PCI 64-bit Resource Allocation选项，Enabled、Disabled可选，默认Enabled；
                B：选项设置生效，为Disabled；
    Remark:     1、若接有PCIe卡，当PCIe需要64Bit资源时会自动使能此选项。
    """
    try:
        options = [Msg.ENABLE, Msg.DISABLE]
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.PCI_64_RSC_ALLOC), options)
        assert SetUpLib.get_option_value(Msg.PCI_64_RSC_ALLOC) == Msg.ENABLE
        assert SetUpLib.set_option_value(Msg.PCI_64_RSC_ALLOC, Msg.DISABLE, save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert SetUpLib.get_option_value(Msg.PCI_64_RSC_ALLOC) in options
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1309", "[TC1309] Testcase_PcieResource_008", "MMIOH基地址设置菜单检查"))
def Testcase_PcieResource_008():
    """
    Name:       MMIOH基地址设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，IIO界面下检查是否提供MMIO High Base设置菜单，可选值及默认值，有结果A。
    Result:     A：提供MMIO High Base选项，有512G、1T、2T、3.5T、4T、13T、16T、24T、32T、40T、56T等11档可选，2P服务器默认13T，4P服务器默认56T。
    Remark:
    """
    mmio_high_base = ['56T', '40T', '32T', '24T', '16T', '13T', '4T', '3.5T', '2T', '1T', '512G']
    if Sys.CPU_CNT > 2:
        mmio_high_base.remove("56T")
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.MMIO_HIGHT_BASE), mmio_high_base)
        assert SetUpLib.get_option_value(Msg.MMIO_HIGHT_BASE) == Env.MMIOH_BASE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1310", "[TC1310] Testcase_PcieResource_009", "MMIOH颗粒度设置菜单检查"))
def Testcase_PcieResource_009():
    """
    Name:       MMIOH颗粒度设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，IIO界面下检查是否提供MMIO High Granularity Size设置菜单，可选值及默认值，有结果A。
    Result:     A：提供MMIO High Granularity Size选项，有1G、4G、16G、64G、256G、1024G等6档可选，默认64G。
    Remark:
    """
    mmio_high_size = ['1G', '4G', '16G', '64G', '256G', '1024G']
    if Sys.CPU_CNT > 2:
        mmio_high_size.remove("1024G")
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.MMIO_HIGHT_SIZE), mmio_high_size)
        assert SetUpLib.get_option_value(Msg.MMIO_HIGHT_SIZE) == Env.MMIOH_SIZE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1311", "[TC1311] Testcase_PcieResource_010", "MMIOH资源调整功能测试"))
def Testcase_PcieResource_010():
    """
    Name:       MMIOH资源调整功能测试
    Condition:
    Steps:      1、启动进Setup菜单，IIO界面下随机设置MMIOH基地址与颗粒度选项，F10保存退出；
                2、检查串口MMIOH资源分配（搜“CPU Resource Allocation”关键字）基地址与颗粒是否与设置保持一致，有结果A；
                3、检查启动是否异常，能否顺利进入OS，有结果B；
    Result:     A：MMIOH Base与Size分配与设置的一致；
                B：启动无异常，能顺利进入OS。
    Remark:     1、MMIOH资源人为改变，有可能导致资源不足而复位；
                2、不支持的组合需在选项设置Help信息下增加备注。
    """
    unsupport = [['3.5T', '1024G'], ['512G', '1024G'], ["56T", "1024G"]]  # [BASE, SIZE]
    if SutConfig.Sys.CPU_CNT == 4:
        unsupport += [["56T", "256G"], ["40T", "1024G"], ["32T", "1024G"]]

    def set_mmioh_and_verify(base_value: str, size_value: str):
        unsup_key = [k for k, v in unsupport]
        unsup_val = [v for k, v in unsupport]
        if (base_value in unsup_key) and (size_value == unsup_val):
            logging.warning(f"Not Supported: Base={base_value}, Size={size_value}")
            return True
        try:
            logging.info(f"Satrt to test: Base={base_value}, Size={size_value}")
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL, Key.DOWN)
            assert SetUpLib.set_option_value(Msg.MMIOH_BASE, base_value)
            if size_value not in SetUpLib.get_all_values(Msg.MMIOH_SIZE):
                logging.info(f"MMIOH Base={base_value} not support Size: {size_value}")
                return True
            assert SetUpLib.set_option_value(Msg.MMIOH_SIZE, size_value)
            SetUpLib.send_keys(Key.SAVE_RESET)

            base_scale = 40 if base_value.endswith("T") else 30  # T / G
            size_scale = 40 if size_value.endswith("T") else 30  # T / G

            base_setup = hex(int(eval(base_value[:-1]) * (1 << base_scale)))
            size_setup = hex(int(eval(size_value[:-1]) * (1 << size_scale)))

            resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 60, 120)
            if not resource:
                return
            data_search = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SutConfig.Sys.CPU_CNT)])
            rsc_table = re.search(data_search, resource)
            if not rsc_table:
                return
            lines = rsc_table.group().split("\n")
            result = []
            for line in lines:
                result.append(list(map(lambda x: x.strip(), line.split("|"))))

            stk0 = result[1][7].split(" - ")[0].replace(" ", "")
            stk1 = result[2][7].split(" - ")[0].replace(" ", "")
            size_serial = hex(int(stk1, 16) - int(stk0, 16))
            logging.info(f"MMIO_BASE: setup={base_setup} | serial print={stk0.lower()}")
            logging.info(f"MMIO_SIZE: setup={size_setup} | serial print={size_serial}")
            base_match = int(stk0, 16) == int(base_setup, 16)
            size_match = int(size_serial, 16) == int(size_setup, 16)
            # assert SetUpLib.wait_boot_msgs(Msg.BIOS_BOOT_COMPLETE)
            if not base_match:
                logging.warning("MMIO High Base mis-Match")
            if not size_match:
                logging.warning("MMIO High Size mis-Match")
            assert base_match or size_match, "Both Base and Size mis-match with BIOS config"
            logging.info(f"Test Pass: Base={base_value}, Size={size_value}")
            return True
        except Exception as e:
            logging.error(e)
            return False
        finally:
            BmcLib.clear_cmos()

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL, Key.DOWN)
        base_values = SetUpLib.get_all_values(Msg.MMIOH_BASE)
        size_values = SetUpLib.get_all_values(Msg.MMIOH_SIZE)
        fails = []
        for base_val in base_values:
            for size_val in size_values:
                if not set_mmioh_and_verify(base_val, size_val):
                    fail_info = f"Base:{base_val} | Size: {size_val}"
                    fails.append(fail_info)
        assert not fails, f"Fails Information => {fails}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1312", "[TC1312] Testcase_PcieResource_012", "Legacy IO资源设置菜单检查"))
def Testcase_PcieResource_012():
    """
    Name:       Legacy IO资源设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，IIO界面下检查是否有Legacy IO资源设置菜单，可选值及默认值，有结果A；
                2、对比软硬件接口文档，检查菜单是否隐藏未使用的IIO Stack，有结果B。
    Result:     A：提供IIO Stack x控制开关，其中x与具体Stack对应，Enabled、Disabled可选，默认均Enabled；
                B：未使用的IIO Stack均已隐藏。
    Remark:     1、V7目前仅使用Stack0~Stack5，Stack0为DMI，Stack1~Stack5与Port1~Port5对应，对应关系参考接口文档；
                2、选项具体位置：IIO Configuration->IIO Stack IO Resource Configuration
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_STACK, Key.DOWN)
        options = SetUpLib.get_all_options()
        iio_stack_list = []
        for stk in range(5):
            iio_option = f"IIO Stack {stk+1}"
            iio_stack_list.append(iio_option)
            assert SetUpLib.get_option_value(iio_option) == Msg.ENABLE
            assert MiscLib.same_values(SetUpLib.get_all_values(iio_option), [Msg.ENABLE, Msg.DISABLE])
            assert iio_option in options, f"{iio_option} not in {options}"
        assert MiscLib.same_values(list(options.keys()), iio_stack_list)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1314", "[TC1314] Testcase_PcieResourceUefi_007", "【UEFI】PCIe设备资源一致性测试"))
def Testcase_PcieResourceUefi_007():
    """
    Name:       【UEFI】PCIe设备资源一致性测试
    Condition:  1、UEFI模式；
                2、接PCIe设备。
    Steps:      1、 启动进OS，执行"lspci -s bus:dev:func  -vvv"命令查看设备配置空间，记录PCIe设备各资源信息(包括基地址、大小)，假定为a；
                2、 多次重启对比设备各资源信息是否发生变化，有结果A。
    Result:     A：设备各资源信息不发生变化，依然为a。
    Remark:
    """
    try:
        resource_a = _get_pcie_resource_region()
        for i in range(3):
            resource_b = _get_pcie_resource_region()
            assert resource_b == resource_a, "PCIe resource mismatch"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1316", "[TC1316] Testcase_PcieResourceUefi_009", "【UEFI】单CPU资源分配测试"))
@mark_skip_if(Sys.CPU_CNT != 1, reason="CPU counts not match with testcase specification")
def Testcase_PcieResourceUefi_009():
    """
    Name:       【UEFI】单CPU资源分配测试
    Condition:  1、UEFI模式；
                2、接单CPU；
                3、接PCIe设备。
    Steps:      1、单板上电启动，检查能否正常进入OS，有结果A；
                2、执行"lspci -s bus:dev:func  -vvv"命令检查配置空间资源分配是否正常，有结果D。
    Result:     A：能正常进入OS，无挂死、反复重启等异常现象。
                B：设备各资源分配正常。
    Remark:
    """
    try:
        assert _get_pcie_resource_region()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1317", "[TC1317] Testcase_PcieResourceLegacy_007", "【Legacy】PCIe设备资源一致性测试"))
@mark_legacy_test
def Testcase_PcieResourceLegacy_007():
    """
    Name:       【Legacy】PCIe设备资源一致性测试
    Condition:  1、Legacy模式；
                2、接PCIe设备。
    Steps:      1、 启动进OS，执行"lspci -s bus:dev:func  -vvv"命令查看设备配置空间，记录PCIe设备各资源信息(包括基地址、大小)，假定为a；
                2、 多次重启对比设备各资源信息是否发生变化，有结果A。
    Result:     A：设备各资源信息不发生变化，依然为a。
    Remark:
    """
    try:
        resource_a = _get_pcie_resource_region(uefi=False)
        for i in range(3):
            resource_b = _get_pcie_resource_region(uefi=False)
            assert resource_b == resource_a, "PCIe resource mismatch"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1319", "[TC1319] Testcase_PcieResourceLegacy_009", "【Legacy】单CPU资源分配测试"))
@mark_skip_if(Sys.CPU_CNT != 1, reason="CPU counts not match with testcase specification")
@mark_legacy_test
def Testcase_PcieResourceLegacy_009():
    """
    Name:       【Legacy】单CPU资源分配测试
    Condition:  1、Legacy模式；
                2、接单CPU；
                3、接PCIe设备。
    Steps:      1、单板上电启动，检查能否正常进入OS，有结果A；
                2、执行"lspci -s bus:dev:func  -vvv"命令检查配置空间资源分配是否正常，有结果D。
    Result:     A：能正常进入OS，无挂死、反复重启等异常现象。
                B：设备各资源分配正常。
    Remark:
    """
    try:
        assert _get_pcie_resource_region(uefi=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1320", "[TC1320] Testcase_Aspm_001", "ASPM设置菜单检查"))
def Testcase_Aspm_001():
    """
    Name:       ASPM设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，检查PCIe ASPM总开关默认状态，有结果A；
                2、检查IIO及PCH PCIe菜单下每个具体Root Port下是否存在ASPM选项，有结果B。
    Result:     A：存在PCIe ASPM总开关，可选Disable，Per Port，L1 only，默认Disable；
                B：每个Root Port下的ASPM选项均被隐藏。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PERI_CONFIG)
        assert SetUpLib.get_option_value(Msg.ASPM_GLOBAL) == Msg.DISABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.ASPM_GLOBAL), Msg.VAL_ASPM)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert _pcie_iio_port_test(Msg.ASPM_ROOT_PORT, option_exist=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1321", "[TC1321] Testcase_Aspm_002", "ASPM总开关测试"))
def Testcase_Aspm_002():
    """
    Name:       ASPM总开关测试
    Condition:
    Steps:      1、启动进Setup菜单，设置PCIe ASPM总开关为L1 Only，检查IIO及PCH PCIe菜单下每个具体Root Port下的ASPM选项值，有结果A；
                2、保存重启进OS，lspci -vvv -s bus:dev:func查询对应Root Port下的PCIe设备配置空间，检查ASPM状态，有结果B。
                3、重启进Setup菜单，设置PCIe ASPM总开关为Disabled，检查IIO及PCH PCIe菜单下每个具体Root Port下的ASPM选项值，有结果A；
                4、重启进OS，lspci -vvv -s bus:dev:func查询对应Root Port下的PCIe设备配置空间，检查ASPM状态，有结果C；
    Result:     A：每个Root Port下的ASPM选项均被隐藏；
                B：ASPM显示为L1 Only；
                C：ASPM显示为Disable。
    Remark:     1、如果设备不支持L1 Only，OS下ASPM仍会显示Disabled。
    """
    try:
        aspm_val_l1only = Msg.VAL_ASPM[2]
        aspm_val_disable = Msg.VAL_ASPM[0]

        def aspm_l1only_disable_test(aspm_value):
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PERI_CONFIG)
            assert SetUpLib.set_option_value(Msg.ASPM_GLOBAL, aspm_value)
            assert SetUpLib.back_to_setup_toppage()
            assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
            assert _pcie_iio_port_test(Msg.ASPM_ROOT_PORT, option_exist=False)
            SetUpLib.send_keys(Key.SAVE_RESET)
            assert _aspm_root_port_os_check(aspm_value, reset=False)
            return True

        assert aspm_l1only_disable_test(aspm_value=aspm_val_l1only)
        assert aspm_l1only_disable_test(aspm_value=aspm_val_disable)

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1322", "[TC1322] Testcase_Aspm_003", "Root Port ASPM开关测试"))
def Testcase_Aspm_003():
    """
    Name:       Root Port ASPM开关测试
    Condition:  1、ASPM总开关设置为Per Port
    Steps:      1、启动进Setup菜单，检查IIO及PCH PCIe下各Root Port的ASPM选项，有结果A；
                2、修改Root Port的ASPM开关为L1 Only，F10保存重启进OS，lspci -vvv -s bus:dev:func查询对应Root Port下的PCIe设备配置空间，检查ASPM状态，有结果B；
                3、重启进Setup菜单，修改Root Port的ASPM开关为Disable，F10保存重启进OS，lspci -vvv -s bus:dev:func查询对应Root Port下的PCIe设备配置空间，检查ASPM状态，有结果C；
    Result:     A：存在ASPM选项，可选Disable，L1 Only，默认Disable；
                B：ASPM显示为L1 Only；
                C：ASPM显示为Disable。
    Remark:     1、如果设备不支持L1 Only，OS下ASPM仍会显示Disabled。
    """
    try:
        aspm_val_disable = Msg.VAL_ASPM[0]
        aspm_val_port = Msg.VAL_ASPM[1]
        aspm_val_l1only = Msg.VAL_ASPM[2]

        def aspm_per_port_test(aspm_read, aspm_set):
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PERI_CONFIG)
            assert SetUpLib.set_option_value(Msg.ASPM_GLOBAL, aspm_val_port)
            assert SetUpLib.back_to_setup_toppage()
            assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
            assert _pcie_iio_port_test(Msg.ASPM_ROOT_PORT, value_read=aspm_read,
                                       value_set=aspm_set, value_list=[aspm_val_disable, aspm_val_l1only])
            SetUpLib.send_keys(Key.SAVE_RESET)
            assert _aspm_root_port_os_check(aspm_set, reset=False)
            return True

        assert aspm_per_port_test(aspm_val_disable, aspm_val_l1only)
        assert aspm_per_port_test(aspm_val_l1only, aspm_val_disable)

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1323", "[TC1323] Testcase_Sriov_001", "SRIOV设置菜单检查"))
def Testcase_Sriov_001():
    """
    Name:       SRIOV设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，Peripheral Configuration界面下查看是否存在SR-IOV设置菜单，可选值及默认值，有结果A；
                2、设置SR-IOV为Enabled或Disabled，检查菜单联动，有结果B；
                3、设置SR-IOV为Per IIO Port，检查菜单联动，有结果C。
    Result:     A：存在SR-IOV总开关，可选Per IIO Port，Enable，Disable，默认Enable；
                B：Enabled或Disabled时不联动菜单；
                C：开放每个Port单独设置开关，Enabled、Disabled可选。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_SRIOV)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.SRIOV_GLOBAL, key=Key.UP), Msg.VAL_SRIOV)
        assert SetUpLib.get_option_value(Msg.SRIOV_GLOBAL, key=Key.UP) == Msg.ENABLE
        for option in SetUpLib.get_all_options():
            assert not re.search(Msg.SRIOV_PORT, option)

        assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, Msg.DISABLE, key=Key.UP)
        for option in SetUpLib.get_all_options():
            assert not re.search(Msg.SRIOV_PORT, option)

        assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, Msg.VAL_SRIOV[2], key=Key.UP)
        all_options = SetUpLib.get_all_options()
        rootport_cnt = 0
        for option, value in all_options.items():
            if not re.search(Msg.SRIOV_PORT, option):
                continue
            assert MiscLib.same_values(SetUpLib.get_all_values(option), [Msg.DISABLE, Msg.ENABLE])
            rootport_cnt += 1
        assert rootport_cnt, "No Root Port Found"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1324", "[TC1324] Testcase_Sriov_002", "SRIOV总开关测试"))
def Testcase_Sriov_002():
    """
    Name:       SRIOV总开关测试
    Condition:  1、接支持SR-IOV的PCIe设备，假定为Porta；
                2、已安装规格内OS。
    Steps:      1、启动进Setup菜单，SR-IOV总开关设置为Disabled，保存重启进OS，lspci -vvv -s bus:dev:func查询对应PCIe设备是否有预留BAR资源，有结果A。
                2、重启进Setup菜单，SR-IOV总开关设置Enabled，保存重启进OS，lspci -vvv -s bus:dev:func查询对应PCIe设备是否有预留BAR资源，有结果B；
    Result:     A：正常预留BAR资源（关闭后，OS还是可通过上层驱动自行打开）；
                B：正常预留BAR资源。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_SRIOV)
        assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, Msg.DISABLE, save=True)
        assert SetUpLib.boot_to_default_os(reset=False)
        if not _sriov_bar_resource_check():
            logging.warning("No SR-IOV BARs found, maybe no PCIE device support SR-IOV, skip the test")
            return core.Status.Skip

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_SRIOV)
        assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, Msg.ENABLE, save=True)
        assert SetUpLib.boot_to_default_os(reset=False)
        assert _sriov_bar_resource_check()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1325", "[TC1325] Testcase_Sriov_003", "Per IIO SR-IOV开关测试"))
def Testcase_Sriov_003():
    """
    Name:       Per IIO SR-IOV开关测试
    Condition:  1、接支持SR-IOV的PCIe设备，假定为Porta；
                2、已安装规格内OS；
                3、SR-IOV总开关设置为Per IIO Port。
    Steps:      1、启动进Setup菜单，设置对应Port的SR-IOV开关为Disable，保存退出；
                3、重启进OS，lspci -vvv -s bus:dev:func查询对应PCIe设备是否有预留BAR资源，有结果A；
                4、重启进Setup菜单，设置对应Port的SR-IOV开关为Enable，保存退出；
                5、重启进OS，lspci -vvv -s bus:dev:func查询对应PCIe设备是否有预留BAR资源，有结果B。
    Result:     A：正常预留BAR资源（关闭后，OS还是可通过上层驱动自行打开）；
                B：正常预留BAR资源。
    Remark:
    """
    try:
        val_sriov_port = Msg.VAL_SRIOV[2]

        def set_per_port_sriov(value):
            all_options = SetUpLib.get_all_options()
            rootport_cnt = 0
            for option in all_options:
                if not re.search(Msg.SRIOV_PORT, option):
                    continue
                assert SetUpLib.set_option_value(option, value, key=Key.UP)
                rootport_cnt += 1
            assert rootport_cnt, "No Root Port Found"
            SetUpLib.send_keys(Key.SAVE_RESET)
            return True

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_SRIOV)
        assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, val_sriov_port)
        assert set_per_port_sriov(Msg.DISABLE)
        assert SetUpLib.boot_to_default_os(reset=False)
        if not _sriov_bar_resource_check():
            logging.warning("No SR-IOV BARs found, skip the test")
            return core.Status.Skip

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_SRIOV)
        assert set_per_port_sriov(Msg.ENABLE)
        assert SetUpLib.boot_to_default_os(reset=False)
        assert _sriov_bar_resource_check()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1326", "[TC1326] Testcase_Sriov_006", "SR-IOV开启/关闭均不预留BUS号测试"))
def Testcase_Sriov_006():
    """
    Name:       SR-IOV开启/关闭均不预留BUS号测试
    Condition:  1、接支持SR-IOV的PCIe设备，假定为Porta；
                2、已安装规格内OS。
    Steps:      1、启动进Setup菜单，设置SR-IOV开关为Disable，保存退出；
                2、重启进OS，lspci -tv查询对应PCIe设备是否有预留BUS号资源，有结果A；
                3、重启进Setup菜单，设置SR-IOV开关为Enable，保存退出；
                4、重启进OS，lspci -tv查询对应PCIe设备是否有预留BUS资源，有结果A。
    Result:     A：开启和关闭SR-IOV，PCIe设备均不预留BUS资源。
    Remark:
    """
    try:
        def sriov_bus_rsv_test(value):
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_SRIOV)
            assert SetUpLib.set_option_value(Msg.SRIOV_GLOBAL, value, save=True)
            if not _sriov_bar_resource_check():
                logging.warning("No SR-IOV device found, skip the test")
                return -1
            lspci_tv = SshLib.execute_command(Sut.OS_SSH, "lspci -tv")
            bus_reserved = []
            for line in lspci_tv.splitlines():
                ports = re.findall("\[[0-9a-fA-F-]+]", line)
                if ports:
                    end_port = ports[-1]
                    if "-" in end_port:  # 有预留BUS资源时,BUS显示为某个范围
                        logging.warning(line)
                        bus_reserved.append(line)
            if bus_reserved:
                for index, bus in enumerate(bus_reserved):
                    if "X550" in bus:
                        logging.info("[Ignore] Intel X550 have reserved bus")
                        bus_reserved.remove(bus)
            assert not bus_reserved, "SR-IOV reserved bus found"
            return True

        sriov_disable = sriov_bus_rsv_test(Msg.DISABLE)
        if sriov_disable == -1:  # No pcie device support SR-IOV
            return core.Status.Skip

        assert sriov_disable
        assert sriov_bus_rsv_test(Msg.ENABLE)

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1327", "[TC1327] Testcase_PciePortItem_001", "Setup菜单提供CPU RootPort端口开关测试"))
def Testcase_PciePortItem_001():
    """
    Name:       Setup菜单提供CPU RootPort端口开关测试
    Condition:
    Steps:      1、启动进Setup菜单，检查Socket Configuration->IIO界面是否存在rootport端口开关选项，有结果A；
    Result:     A：每个rootport均提供开关可设置。选项为Enable和Disable, Auto。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert _pcie_iio_port_test(Msg.PCIE_PORT, value_list=[Msg.ENABLE, Msg.DISABLE, Msg.Auto])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1328", "[TC1328] Testcase_PciePortItem_002", "打开关闭CPU RootPort端口开关测试"))
def Testcase_PciePortItem_002():
    """
    Name:       打开关闭CPU RootPort端口开关测试
    Condition:  1、单板每个CPU下外插PCIe板卡
    Steps:      1、进Setup菜单IIO界面，关闭Socket0下的Rootport，保存退出；
                2、启动进OS，lspci命令查看Socket0 Rootport下的设备在位情况，有结果A；
                3、重启进Setup菜单IIO界面，打开Socket0下的Rootport，保存退出；
                4、启动进OS，lspci命令查看Socket0 Rootport下的设备在位情况，有结果B；
                5、遍历每个Socket，重复步骤1~4。
    Result:     A：无PCIe设备；
                B：有PCIe设备。
    Remark:     rootport对应的slot参考软硬件接口文档
    """
    try:
        # Disable
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert _pcie_iio_port_test(Msg.PCIE_PORT, value_set=Msg.DISABLE)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert not _get_pcie_resource_region(reset=False)
        # Enable
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert _pcie_iio_port_test(Msg.PCIE_PORT, value_set=Msg.ENABLE)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _get_pcie_resource_region(reset=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1329", "[TC1329] Testcase_DisplayMode_001", "显卡选择设置菜单检查"))
def Testcase_DisplayMode_001():
    """
    Name:       显卡选择设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，检查是否提供显卡选择开关，默认值是否正确，有结果A。
    Result:     A：提供显卡选择开关，选项为外接显卡或板载显卡输出，默认为板载显卡输出。
    Remark:
    """
    video_mode = ['On Board Graphics', 'Plug-in Graphics']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.VIDEO_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.DISPLAY_MODE), video_mode)
        assert SetUpLib.get_option_value(Msg.DISPLAY_MODE) == video_mode[0]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1330", "[TC1330] Testcase_SlotPxeCfgUefi_001", "【UEFI】外接网卡PXE开关默认状态"))
@mark_skip_if(not Sys.PXE_UEFI_DEV, reason="No add-in network card in config")
def Testcase_SlotPxeCfgUefi_001():
    """
    Name:       【UEFI】外接网卡PXE开关默认状态
    Condition:  1、UEFI模式；
                2、单板满配Riser及PCIe网卡。
    Steps:      1、启动进Setup菜单，PXE Configuration界面下查看是否存在Slot PXE选项，可选值及默认值，有结果A；
                2、Boot界面下查看是否存在外接网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，查看是否有外接网卡的PXE启动项，有结果B。
    Result:     A：存在Slot PXE选项；Enabled、Disabled可选，默认Enabled，且新增CPU n First Slot Port m的控制开关均Enabled（n为CPU数量，m为First Slot所接网卡的网卡数量）；
                B：有外接网卡的PXE启动项。
    Remark:     1、First Slot未接网卡时，不显示响应的PXE控制开关。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.SLOT_PXE), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.get_option_value(Msg.SLOT_PXE) == Msg.ENABLE

        all_options = SetUpLib.get_all_options()
        for option in all_options:
            if re.search(Msg.SLOT_PXE_FIRST, option):
                assert SetUpLib.get_option_value(option) == Msg.ENABLE

        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1331", "[TC1331] Testcase_SlotPxeCfgUefi_002", "【UEFI】Slot PXE关闭时PXE功能验证"))
@mark_skip_if(not Sys.PXE_UEFI_DEV, reason="No add-in network card in config")
def Testcase_SlotPxeCfgUefi_002():
    """
    Name:       【UEFI】Slot PXE关闭时PXE功能验证
    Condition:  1、UEFI模式；
                2、单板满配Riser及PCIe网卡。
    Steps:      1、启动进Setup菜单，关闭Slot PXE开关，F10保存重启进入Setup菜单PXE Configuration界面下查看，有结果A；
                2、Boot界面下查看是否存在外接网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，查看是否有外接网卡的PXE启动项，有结果B。
    Result:     A：Slot PXE关闭，且隐藏所有First Slot Port网口开关；
                B：无外接网卡的PXE启动项。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert SetUpLib.set_option_value(Msg.SLOT_PXE, Msg.DISABLE)
        options = SetUpLib.get_all_options()
        assert not any(re.search(Msg.SLOT_PXE_FIRST, op) for op in options)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.UEFI)
        if SetUpLib.enter_menu(Msg.MENU_PXE_BOOT):
            assert not SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER, delay=2)
        assert not SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1332", "[TC1332] Testcase_SlotPxeCfgUefi_003", "【UEFI】Slot PXE开启时PXE功能验证"))
@mark_skip_if(not Sys.PXE_UEFI_DEV, reason="No add-in network card in config")
def Testcase_SlotPxeCfgUefi_003():
    """
    Name:       【UEFI】Slot PXE开启时PXE功能验证
    Condition:  1、UEFI模式；
                2、单板满配Riser及PCIe网卡；
                3、PXE服务器已部署。
    Steps:      1、启动进Setup菜单，开启Slot PXE开关，F10保存重启进入Setup菜单PXE Configuration界面下查看，有结果A；
                2、Boot界面下查看是否存在外接网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，选择从外接网卡的PXE启动，查看启动情况，有结果C。
    Result:     A：Slot PXE开启，且新增CPU n First Slot Port m的控制开关均Enabled（n为CPU数量，m为First Slot所接网卡的网卡数量）；
                B：显示所有网卡PXE启动项；
                C：PXE启动成功。
    Remark:     1、First Slot未接网卡时，不显示响应的PXE控制开关。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert SetUpLib.set_option_value(Msg.SLOT_PXE, Msg.ENABLE, save=True)

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        all_options = SetUpLib.get_all_options()
        for option in all_options:
            if re.search(Msg.SLOT_PXE_FIRST, option):
                assert SetUpLib.get_option_value(option) == Msg.ENABLE

        assert SetUpLib.switch_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.UEFI)
        if SetUpLib.enter_menu(Msg.MENU_PXE_BOOT):
            assert SetUpLib.locate_option(Msg.SLOT_PXE_PORT)

        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER, delay=2)
        assert SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        assert SetUpLib.locate_option(Sys.PXE_UEFI_DEV)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Sys.PXE_UEFI_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case("1333", "[TC1333] Testcase_SlotPxeCfgLegacy_001", "【Legacy】外接网卡PXE开关默认状态")
@mark_skip_if(not Sys.PXE_LEGACY_DEV, reason="No add-in network card in config")
@mark_legacy_test
def Testcase_SlotPxeCfgLegacy_001():
    """
    Name:       【Legacy】外接网卡PXE开关默认状态
    Condition:  1、Legacy模式；
                2、单板满配Riser及PCIe网卡。
    Steps:      1、启动进Setup菜单，PXE Configuration界面下查看是否存在Slot PXE选项，可选值及默认值，有结果A；
                2、Boot界面下查看是否存在外接网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，查看是否有外接网卡的PXE启动项，有结果B。
    Result:     A：存在Slot PXE选项；Enabled、Disabled可选，默认Enabled，且新增CPU n First Slot Port m的控制开关均Enabled（n为CPU数量，m为First Slot所接网卡的网卡数量）；
                B：有外接网卡的PXE启动项。
    Remark:     1、First Slot未接网卡时，不显示响应的PXE控制开关。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.SLOT_PXE), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.get_option_value(Msg.SLOT_PXE) == Msg.ENABLE

        all_options = SetUpLib.get_all_options()
        for option in all_options:
            if re.search(Msg.SLOT_PXE_FIRST, option):
                assert SetUpLib.get_option_value(option) == Msg.ENABLE

        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case("1334", "[TC1334] Testcase_SlotPxeCfgLegacy_002", "【Legacy】Slot PXE关闭时PXE功能验证")
@mark_skip_if(not Sys.PXE_LEGACY_DEV, reason="No add-in network card in config")
@mark_legacy_test
def Testcase_SlotPxeCfgLegacy_002():
    """
    Name:       【Legacy】Slot PXE关闭时PXE功能验证
    Condition:  1、Legacy模式；
                2、单板满配Riser及PCIe网卡。
    Steps:      1、启动进Setup菜单，关闭Slot PXE开关，F10保存重启进入Setup菜单PXE Configuration界面下查看，有结果A；
                2、Boot界面下查看是否存在外接网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，查看是否有外接网卡的PXE启动项，有结果B。
    Result:     A：Slot PXE关闭，且隐藏所有First Slot Port网口开关；
                B：无外接网卡的PXE启动项。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert SetUpLib.set_option_value(Msg.SLOT_PXE, Msg.DISABLE)
        options = SetUpLib.get_all_options()
        assert not any(re.search(Msg.SLOT_PXE_FIRST, op) for op in options)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.LEGACY)
        if SetUpLib.enter_menu(Msg.MENU_PXE_BOOT):
            assert not SetUpLib.locate_option(Msg.SLOT_PXE_PORT)

        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER, delay=2)
        assert not SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case("1335", "[TC1335] Testcase_SlotPxeCfgLegacy_003", "【Legacy】Slot PXE开启时PXE功能验证")
@mark_skip_if(not Sys.PXE_LEGACY_DEV, reason="No add-in network card in config")
@mark_legacy_test
def Testcase_SlotPxeCfgLegacy_003():
    """
    Name:       【Legacy】Slot PXE开启时PXE功能验证
    Condition:  1、Legacy模式；
                2、单板满配Riser及PCIe网卡；
                3、PXE服务器已部署。
    Steps:      1、启动进Setup菜单，开启Slot PXE开关，F10保存重启进入Setup菜单PXE Configuration界面下查看，有结果A；
                2、Boot界面下查看是否存在外接网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，选择从外接网卡的PXE启动，查看启动情况，有结果C。
    Result:     A：Slot PXE开启，且新增CPU n First Slot Port m的控制开关均Enabled（n为CPU数量，m为First Slot所接网卡的网卡数量）；
                B：显示所有网卡PXE启动项；
                C：PXE启动成功。
    Remark:     1、First Slot未接网卡时，不显示响应的PXE控制开关。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        assert SetUpLib.set_option_value(Msg.SLOT_PXE, Msg.ENABLE, save=True)

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        all_options = SetUpLib.get_all_options()
        for option in all_options:
            if re.search(Msg.SLOT_PXE_FIRST, option):
                assert SetUpLib.get_option_value(option) == Msg.ENABLE

        assert SetUpLib.switch_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.LEGACY)
        if SetUpLib.enter_menu(Msg.MENU_PXE_BOOT):
            assert SetUpLib.locate_option(Msg.SLOT_PXE_PORT)

        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER, delay=2)
        assert SetUpLib.locate_option(Msg.SLOT_PXE_PORT)
        assert SetUpLib.locate_option(Sys.PXE_LEGACY_DEV)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(Sys.PXE_LEGACY_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1336", "[TC1336] Testcase_OcpPxeCfgUefi_001", "【UEFI】OCP网卡PXE开关默认状态"))
@mark_skip_if(BMC_WEB.is_ocp_exist, value=False)
def Testcase_OcpPxeCfgUefi_001():
    """
    Name:       【UEFI】OCP网卡PXE开关默认状态
    Condition:  UEFI模式
    Steps:      1、启动进Setup菜单，PXE Configuration界面下查看是否存在OCP PXE选项，可选值及默认值，有结果A；
                2、Boot界面下查看是否存在OCP网卡的PXE启动项，有结果B；
                3、进入Boot Manager菜单，查看是否有OCP网卡的PXE启动项，有结果B。
    Result:     A：存在OCP PXE选项，显示数量与实际网口一致，Enabled、Disabled可选，默认均Enabled，
                B：所有OCP网口均有PXE启动项。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PXE_CONFIG)
        ocp_pxe_cnt = 0
        options = SetUpLib.get_all_options()
        for op in options:
            if not re.search(Msg.OCP_PXE, op):
                continue
            ocp_pxe_cnt += 1
            assert SetUpLib.get_option_value(op) == Msg.ENABLE
            assert MiscLib.same_values(SetUpLib.get_all_values(op), [Msg.ENABLE, Msg.DISABLE])
        assert ocp_pxe_cnt == Sys.OCP_PORT, "OCP网口数量与配置不一致"
        assert SetUpLib.back_to_front_page(highlight=Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER, delay=2)
        assert SetUpLib.locate_option(Msg.OCP_PXE_BOOT, order=ocp_pxe_cnt)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("1338", "[TC1338] Testcase_Vroc_001", "NVMe配置场景带宽自适应"))
# def Testcase_Vroc_001():
#     """
#     Name:       NVMe配置场景带宽自适应
#     Condition:  1、获取软硬件接口文档；
#                 2、NVMe硬盘背板正确连接。
#     Steps:      1、启动进Setup菜单， IIO界面下查看CPU各Port口的带宽分配，有结果A；
#     Result:     A：带宽分配与软硬件接口文档一致，根据硬盘背板类型动态分配。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1339", "[TC1339] Testcase_Vroc_002", "NVMe自动识别测试"))
# def Testcase_Vroc_002():
#     """
#     Name:       NVMe自动识别测试
#     Condition:  1、UEFI模式；
#                 2、OS已安装。
#     Steps:      1、插入NVMe硬盘，启动进Setup菜单IIO界面下NVMe是否正常识别，带宽分配是否正确，有结果A；
#                 2、进OS执行“lspci -tv”命令查看NVMe硬盘是否在位，有结果B；
#                 3、拔出NVMe硬盘，启动进Setup菜单IIO界面下NVMe是否正常识别，带宽分配是否正确，有结果C；
#                 4、进OS执行“lspci -tv”命令查看NVMe硬盘是否在位，有结果D；
#     Result:     A：NVMe正常识别，带宽X4，速率Gen3；
#                 B：NVMe在位，型号、BDF正确；
#                 C：NVMe无法识别；
#                 D：NVMe不在位。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1340", "[TC1340] Testcase_Vroc_003", "NVMe信息上报BMC"))
# def Testcase_Vroc_003():
#     """
#     Name:       NVMe信息上报BMC
#     Condition:  1、UEFI模式；
#                 2、NVMe硬盘在位；
#                 3、BMC BT通道已打开；
#                 4、已安装OS。
#     Steps:      1、启动进OS，BMC BT通道查看NVMe上报BDF信息是否正确，有结果A；
#                 2、BMC Web界面查看NVMe硬盘信息显示是否正确，有结果B。
#     Result:     A：BT上报BDF信息正确；
#                 B：BMC显示内容正确。
#     Remark:     1、BT通道搜索关键字“58 C8”;
#                 2、BMC Web界面关注NVMe硬盘容量、厂家、型号、序列号、资源归属等信息。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1341", "[TC1341] Testcase_Vroc_004", "NVMe正确显示Type9信息"))
# def Testcase_Vroc_004():
#     """
#     Name:       NVMe正确显示Type9信息
#     Condition:  1、UEFI模式；
#                 2、NVMe硬盘在位。
#     Steps:      1、启动进OS，执行“dmidecode -t9”命令查看NVMe槽位号与实际丝印是否一致，带宽、速率等信息显示是否正确，有结果A。
#     Result:     A：槽位号显示为HDDx，与实际丝印号一致，带宽、速率显示正确，Current Usage显示为inuse，不在位则显示Avaliable。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1342", "[TC1342] Testcase_Vroc_005", "VMD开关默认状态"))
def Testcase_Vroc_005():
    """
    Name:       VMD开关默认状态
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，IIO界面下查看是否有VMD开关，可选值及默认值，有结果A；
                2、切换启动模式为Legacy，F10保存重启进Setup菜单，查看VMD开关状态，有结果B。
    Result:     A：提供VMD开关，Enabled、Disabled可选，默认Disabled；
                B：VMD开关被隐藏。
    Remark:     Legacy模式当前暂不隐藏VMD开关
    """
    try:
        def check_vmd():
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG + [Msg.VMD_MENU])
            assert SetUpLib.get_option_value(Msg.VMD_CONFIG) == Msg.DISABLE
            assert MiscLib.same_values(SetUpLib.get_all_values(Msg.VMD_CONFIG), [Msg.ENABLE, Msg.DISABLE])
            return True
        assert check_vmd()
        assert BMC_WEB.set_boot_overwrite(mode="legacy", once=False)
        assert check_vmd()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        assert BMC_WEB.set_boot_overwrite(mode="uefi", once=False)


# @core.test_case(("1343", "[TC1343] Testcase_Vroc_006", "打开VMD开关测试"))
# def Testcase_Vroc_006():
#     """
#     Name:       打开VMD开关测试
#     Condition:  1、UEFI模式；
#                 2、开启VMD开关。
#     Steps:      1、启动进Setup菜单，IIO界面查看VMD开关状态，有结果A；
#                 2、BMC Web界面查看是否有VMD开关操作日志，有结果B；
#                 3、进入DeviceManage HII界面，查看是否有VROC功能选项，有结果C；
#                 4、OS下执行“mdadm --detail-platform”命令，查看是否存在I/O Controller控制器，有结果D；
#                 5、OS下执行“lspci -tv”命令，查看是否存在大于10000的设备，有结果E。
#     Result:     A：VMD开关为Enabled；
#                 B：操作日志显示VMD开关打开；
#                 C：有VROC功能选项；
#                 D：存在I/O Controller控制器；
#                 E：存在大于10000的设备。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1344", "[TC1344] Testcase_Vroc_007", "关闭VMD开关测试"))
# def Testcase_Vroc_007():
#     """
#     Name:       关闭VMD开关测试
#     Condition:  1、UEFI模式；
#                 2、关闭VMD开关。
#     Steps:      1、启动进Setup菜单，IIO界面查看VMD开关状态，有结果A；
#                 2、BMC Web界面查看是否有VMD开关操作日志，有结果B；
#                 3、进入DeviceManage HII界面，查看是否有VROC功能选项，有结果C；
#                 4、OS下执行“mdadm --detail-platform”命令，查看是否存在I/O Controller控制器，有结果D；
#                 5、OS下执行“lspci -tv”命令，查看是否存在大于10000的设备，有结果E。
#     Result:     A：VMD开关为Disabled；
#                 B：操作日志显示VMD开关关闭；
#                 C：不存在VROC选项；
#                 D：不存在I/O Controller控制器；
#                 E：不存在大于10000的设备。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1346", "[TC1346] Testcase_RegisterCheck_002", "设备速率查询"))
@mark_skip_if(not Sys.PCIE_SLOT, reason="PCIE SLOT info is not config")
def Testcase_RegisterCheck_002():
    """
    Name:       设备速率查询
    Condition:  1、被测板卡已连接；
                2、已安装Linux系统。
    Steps:      1、启动进OS，查询对应板卡BDF号，假定为bus:dev.func；
                2、输入命令“lspci -vvv -s bus:dev.func”查询板卡配置寄存器中LnkCap字段的Speed及Width数值是否与板卡规格一致，有结果A；
                3、查询板卡配置寄存器中LnkSta字段的Speed及Width数值，检查是否与LnkCap字段一致，有结果B；
    Result:     A：与板卡规格一致；
                B：与LnkCap字段值一致。
    Remark:
    """
    try:
        if not MiscLib.ping_sut(Env.OS_IP, 10):
            assert SetUpLib.boot_to_default_os()
        fails = 0
        for bdf, dev in Sys.PCIE_SLOT.items():
            dev_info = f"{bdf}: {dev.Width} {dev.Speed}"
            logging.info(dev_info)
            lnkcap = f"LnkCap:.*Speed {dev.Speed}.*Width {dev.Width}.*"
            lnksta = f"LnkSta:.*Speed {dev.Speed}.*Width {dev.Width}.*"
            lspci_vvv = SshLib.execute_command(Sut.OS_SSH, f"lspci -s {bdf} -vvv")
            if not re.search(lnkcap, lspci_vvv):
                logging.error(f"LnkCap fail: {dev_info}\n{lnkcap}\n{lspci_vvv}")
                fails += 1
            if not re.search(lnksta, lspci_vvv):
                logging.error(f"LnkSta fail: {dev_info}\n{lnksta}\n{lspci_vvv}")
                fails += 1
        assert fails == 0
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1347", "[TC1347] Testcase_ResourceAllocationUefi_001", "【UEFI】MMIO资源检查"))
def Testcase_ResourceAllocationUefi_001():
    """
    Name:       【UEFI】MMIO资源检查
    Condition:  1、UEFI模式；
                2、被测网卡满配Slot；
                3、开启全打印。
    Steps:      1、启动进OS，查询被测板卡BDF号，假定为bus:dev.func；
                2、输入命令"lspci -vvv -s bus:dev.func"，查询板卡MMIO资源分配，假定为a；
                3、输入"cat /proc/iomem"查询被测板卡mem资源分配，假定为b；
                4、启动日志中搜索"Resource Map"对应BDF的资源分配，假定为c；
                5、对比abc的基地址及分配大小是否一致，有结果A；
                6、检查每个Slot下的被测板卡，重复步骤1~5。
    Result:     A：基地址及分配大小保持一致。
    Remark:     1、MMIO资源包括MMIOL和MMIOH，可能不止一段，每段均要保持一致；
                2、系统下32-bit、Expansion ROM对应串口Mem32数据，64-bit对应串口PMem64数据。
    """
    lspci_range_dict = {}
    iomem_range_dict = {}
    post_mem_dict = {}

    try:
        assert BmcLib.debug_message(enable=True)
        post_log = SetUpLib.get_post_log(timeout=Env.BOOT_FULL_DBG)
        assert MiscLib.ping_sut(Env.OS_IP, Env.BOOT_DELAY)
        for bdf in Sys.PCIE_SLOT:
            lspci_range_dict[bdf] = _lspci_range(bdf)
            iomem_range_dict[bdf] = _iomem_range(bdf)
            post_mem_dict[bdf] = _post_mem_range(bdf, post_log)
        for bdf, mem_info in post_mem_dict.items():
            assert lspci_range_dict[bdf].issubset(mem_info), f"{bdf}: lspci mismatch with post resource map"
            assert iomem_range_dict[bdf].issubset(mem_info), f"{bdf}: iomem mismatch with post resource map"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# @core.test_case(("1348", "[TC1348] Testcase_ResourceAllocationUefi_002", "【UEFI】Port IO资源检查"))
# def Testcase_ResourceAllocationUefi_002():
#     """
#     Name:       【UEFI】Port IO资源检查
#     Condition:  1、UEFI模式；
#                 2、被测网卡满配Slot；
#                 3、开启全打印。
#     Steps:      1、启动进OS，查询被测板卡BDF号，假定为bus:dev.func；
#                 2、输入命令"lspci -vvv -s bus:dev.func"，查询板卡Port IO资源分配，假定为a；
#                 3、输入"cat /proc/ioports"查询被测板卡Port IO资源分配，假定为b；
#                 4、启动日志中搜索"Resource Map"对应BDF的资源分配，假定为c；
#                 5、对比abc的基地址及分配大小是否一致，有结果A；
#                 6、检查每个Slot下的被测板卡，重复步骤1~5。
#     Result:     A：基地址及分配大小保持一致。
#     Remark:     1、系统下I/O ports对应串口Io16数据。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1349", "[TC1349] Testcase_ResourceAllocationUefi_003", "【UEFI】Legacy IO资源检查"))
# def Testcase_ResourceAllocationUefi_003():
#     """
#     Name:       【UEFI】Legacy IO资源检查
#     Condition:  1、UEFI模式；
#                 2、被测网卡满配Slot；
#                 3、开启全打印。
#     Steps:      1、启动进OS，查询被测板卡BDF号，假定为bus:dev.func；
#                 2、输入命令"lspci -vvv -s bus:dev.func"，查询板卡Legacy IO资源分配，假定为a；
#                 3、启动日志中搜索"Resource Map"对应BDF的资源分配，假定为b；
#                 4、对比abc的基地址及分配大小是否一致，有结果A；
#                 5、检查每个Slot下的被测板卡，重复步骤1~4。
#     Result:     A：基地址及分配大小保持一致。
#     Remark:     2、系统下Expansion ROM对应串口Mem32数据。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1350", "[TC1350] Testcase_ResourceAllocationLegacy_001", "【Legacy】MMIO资源检查"))
@mark_legacy_test
def Testcase_ResourceAllocationLegacy_001():
    """
    Name:       【Legacy】MMIO资源检查
    Condition:  1、Legacy模式；
                2、被测网卡满配Slot；
                3、开启全打印。
    Steps:      1、启动进OS，查询被测板卡BDF号，假定为bus:dev.func；
                2、输入命令"lspci -vvv -s bus:dev.func"，查询板卡MMIO资源分配，假定为a；
                3、输入"cat /proc/iomem"查询被测板卡mem资源分配，假定为b；
                4、启动日志中搜索"Resource Map"对应BDF的资源分配，假定为c；
                5、对比abc的基地址及分配大小是否一致，有结果A；
                6、检查每个Slot下的被测板卡，重复步骤1~5。
    Result:     A：基地址及分配大小保持一致。
    Remark:     1、MMIO资源包括MMIOL和MMIOH，可能不止一段，每段均要保持一致；
                2、系统下32-bit、Expansion ROM对应串口Mem32数据，64-bit对应串口PMem64数据。
    """
    lspci_range_dict = {}
    iomem_range_dict = {}
    post_mem_dict = {}

    try:
        assert BmcLib.debug_message(enable=True)
        post_log = SetUpLib.get_post_log(timeout=Env.BOOT_FULL_DBG)
        for bdf in Sys.PCIE_SLOT:
            lspci_range_dict[bdf] = _lspci_range(bdf, uefi=False)
            iomem_range_dict[bdf] = _iomem_range(bdf, uefi=False)
            post_mem_dict[bdf] = _post_mem_range(bdf, post_log)
        for bdf, mem_info in post_mem_dict.items():
            assert lspci_range_dict[bdf].issubset(mem_info), f"{bdf}: lspci mismatch with post resource map"
            assert iomem_range_dict[bdf].issubset(mem_info), f"{bdf}: iomem mismatch with post resource map"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# @core.test_case(("1351", "[TC1351] Testcase_ResourceAllocationLegacy_002", "【Legacy】Port IO资源检查"))
# def Testcase_ResourceAllocationLegacy_002():
#     """
#     Name:       【Legacy】Port IO资源检查
#     Condition:  1、Legacy模式；
#                 2、被测网卡满配Slot；
#                 3、开启全打印。
#     Steps:      1、启动进OS，查询被测板卡BDF号，假定为bus:dev.func；
#                 2、输入命令"lspci -vvv -s bus:dev.func"，查询板卡Port IO资源分配，假定为a；
#                 3、输入"cat /proc/ioports"查询被测板卡Port IO资源分配，假定为b；
#                 4、启动日志中搜索"Resource Map"对应BDF的资源分配，假定为c；
#                 5、对比abc的基地址及分配大小是否一致，有结果A；
#                 6、检查每个Slot下的被测板卡，重复步骤1~5。
#     Result:     A：基地址及分配大小保持一致。
#     Remark:     1、系统下I/O ports对应串口Io16数据。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1352", "[TC1352] Testcase_ResourceAllocationLegacy_003", "【Legacy】Legacy IO资源检查"))
# def Testcase_ResourceAllocationLegacy_003():
#     """
#     Name:       【Legacy】Legacy IO资源检查
#     Condition:  1、Legacy模式；
#                 2、被测网卡满配Slot；
#                 3、开启全打印。
#     Steps:      1、启动进OS，查询被测板卡BDF号，假定为bus:dev.func；
#                 2、输入命令"lspci -vvv -s bus:dev.func"，查询板卡Legacy IO资源分配，假定为a；
#                 3、启动日志中搜索"Resource Map"对应BDF的资源分配，假定为b；
#                 4、对比abc的基地址及分配大小是否一致，有结果A；
#                 5、检查每个Slot下的被测板卡，重复步骤1~4。
#     Result:     A：基地址及分配大小保持一致。
#     Remark:     2、系统下Expansion ROM对应串口Mem32数据。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1353", "[TC1353] Testcase_Maxpayload_001", "Maxpayload设置菜单检查"))
def Testcase_Maxpayload_001():
    """
    Name:       Maxpayload设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，IIO界面检查每个Port口是否提供Max Payload Size设置选项，可选值及默认值，有结果A。
    Result:     A：存在PCIe Port Max Payload Size选项，Auto、512B 、256B、128B可选，默认Auto。
    Remark:
    """
    payload_size = ['Auto', '512B', '256B', '128B']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_IIO_CONFIG)
        assert _pcie_iio_port_test(option=Msg.PCIE_PORT_MAX_PAYLOAD_SIZE, value_read=payload_size[0], value_list=payload_size)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

