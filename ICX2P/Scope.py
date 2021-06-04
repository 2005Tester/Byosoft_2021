from Common import Unitool
from Core import SutInit
from Core.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.TestCase import UpdateBIOS, BiosTest, DefaultValueTest, Os, Release, Legacy, CpuInit01, MemInit02, PchInit03, \
    PcieInit04, Io05, Smbios09, Security22, BootDevice06

# init SUT
SutInit.SutInit("ICX2P")

# init unitool
unitool = Unitool.SshUnitool(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD, SutConfig.UNI_PATH, True)


# Test scope for non-equipment build
def full_scope():
    BiosTest.post_test()
    BiosTest.power_cycling()
    BiosTest.usb_test()
    CpuInit01.cpu_mem_info()
    BiosTest.press_f2()
    CpuInit01.static_turbo_default()
    CpuInit01.ufs_default_value()
    DefaultValueTest.rrqirq()
    BiosTest.dram_rapl_option_check()
    BiosTest.security_boot()
    BiosTest.vtd()
    BiosTest.cnd_default_enable()
    CpuInit01.upi_link_status()
    CpuInit01.cpu_cores_active_enable_1(unitool)
    CpuInit01.cpu_cores_active_enable_middle(unitool)
    CpuInit01.cpu_cores_active_enable_max(unitool)
    CpuInit01.cpu_cores_disable_sys_normally(unitool)
    CpuInit01.cores_customized_by_unitool(unitool)
    CpuInit01.numa_01(unitool)
    CpuInit01.numa_02()
    CpuInit01.numa_03(unitool)
    CpuInit01.cpu_compa_02()
    CpuInit01.cpu_compa_03()
    CpuInit01.cpu_compa_05()
    if Os.boot_to_suse():
        Smbios09.smbios_test_all()
        Release.equip_mode_flag_check(unitool)
    Security22.pwd_test_all()
    MemInit02.dimm_power_mgt_01()
    MemInit02.dimm_power_mgt_02()
    MemInit02.dimm_power_mgt_04()
    MemInit02.dimm_power_mgt_05()
    MemInit02.dimm_power_mgt_07()
    MemInit02.memory_compa_001()
    MemInit02.memory_compa_006()
    MemInit02.dimm_power_mgt_010()
    MemInit02.dimm_power_mgt_011()
    MemInit02.dimm_power_mgt_012()
    MemInit02.mem_refresh_001()
    MemInit02.mem_refresh_002()
    MemInit02.set_mem_freq_001_006()
    MemInit02.mtrr_max_range()
    MemInit02.mtrr_fixed_range()
    Io05.system_info_001()
    Io05.system_info_003()
    Release.me_version_status()
    BiosTest.load_default()
    MemInit02.rmt_menu_test()
    PchInit03.usb_default_enable_check()
    PchInit03.post_gpio_error_check()
    DefaultValueTest.pcie_port_bandwidth_check()
    BiosTest.serial_print_keywords()
    BiosTest.serial_print_error_check()
    PcieInit04.pcie_resource_mmiol()
    PcieInit04.pcie_resource_mmioh()
    PcieInit04.pcie_resource_mmioh_menu()
    PcieInit04.pcie_resource_64b()
    PcieInit04.pcie_resource_bus()
    PcieInit04.pcie_resource_legacyio()
    PcieInit04.pcie_resource_ioapic()
    PcieInit04.pcie_resource_lspci_uefi()
    PcieInit04.aspm_global_disable_l1only()
    PcieInit04.aspm_per_port_loop()
    BiosTest.power_efficiency_mode_loop(unitool)
    BootDevice06.boot_device_type_001()
    BootDevice06.boot_order_002()
    BootDevice06.boot_order_004(Sut.BMC_SSH)
    if Legacy.enable_legacy_boot():
        BootDevice06.boot_device_type_002()
        Io05.system_info_002()
        # Io05.system_info_004()
        PcieInit04.pcie_resource_lspci_legacy()
        BootDevice06.boot_order_012(Sut.BMC_SSH)
        Legacy.disable_legacy_boot()


# Test scope for equipment mode image
def equip_scope():
    Release.equip_mode_version_check()
    Os.boot_to_suse_mfg()
    Smbios09.smbios_type128(unitool)
    MemInit02.rmt_equip_test(unitool)


class ReleaseBasic:
    def __init__(self, release_branch):
        self.branch = release_branch

    def normal_scope(self):  # Non-Equip BIOS Test Scope
        if UpdateBIOS.update_bios(self.branch):
            BiosTest.post_test()
            BiosTest.power_cycling()
            Release.check_bmc_warning()
            Release.me_version_status()
            BiosTest.pxe_test()
            BiosTest.load_default()
            BiosTest.security_boot()
            if Os.boot_to_suse():
                Smbios09.smbios_test_all()
            Release.registry_check(self.branch)
            Release.compare_fdm_log(self.branch)
            # Release.hpm_upgrade_test(unitool, self.branch)  # need get release hpm bios from huawei
            Release.hpm_downgrade_test(unitool, self.branch)

    def equip_scope(self):
        if UpdateBIOS.update_bios_mfg(self.branch):
            Release.equip_mode_version_check()
            Smbios09.smbios_type128(unitool)
            if Os.boot_to_suse():
                Release.equip_mode_flag_check(unitool)


# Define test scope for daily test
def daily_scope():
    UpdateBIOS.update_bios('master')
    full_scope()
    if UpdateBIOS.update_bios_mfg('master'):
        equip_scope()


def release_scope():
    """Release Basic Function Test"""
    release_branch = "2288V6_012"
    release_basic = ReleaseBasic(release_branch)
    release_basic.normal_scope()
    release_basic.equip_scope()


def debug_scope():
    UpdateBIOS.update_bios('master')
    CpuInit01.cpu_mem_info()
    BiosTest.power_efficiency_mode_loop(unitool)
    BootDevice06.boot_order_001()
    BootDevice06.boot_order_003(Sut.BMC_SSH)
    BootDevice06.boot_order_004(Sut.BMC_SSH)
    BootDevice06.boot_order_005(Sut.BMC_SSH)
