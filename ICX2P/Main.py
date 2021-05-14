from Common import Unitool
from Core import SutInit
from Core.SutInit import Sut
from ICX2P import UpdateBIOS, biosTest, DefaultValueTest, Os, Release, Legacy, CpuInit01, MemInit02, PchInit03, \
    PcieInit04, Io05, Smbios09, Security22
from ICX2P.Config import SutConfig


# init SUT
SutInit.SutInit("ICX2P")
ser = Sut.BIOS_COM
ssh_os = Sut.OS_SSH

# init unitool
unitool = Unitool.SshUnitool(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD, SutConfig.UNI_PATH, True)


# Test scope for non-equipment build
def TestScope():
    biosTest.post_test(ser)
    biosTest.PM()
    biosTest.usbTest()
    CpuInit01.cpu_mem_info()
    biosTest.press_f2()
    CpuInit01.static_turbo_default()
    CpuInit01.ufs_default_value()
    DefaultValueTest.rrqirq()
    biosTest.dram_rapl_option_check()
    biosTest.securityBoot()
    biosTest.vtd()
    biosTest.cnd_default_enable()
    CpuInit01.upi_link_status()
    CpuInit01.cpu_cores_active_enable_1(ssh_os)
    CpuInit01.cpu_cores_active_enable_middle(ssh_os)
    CpuInit01.cpu_cores_active_enable_max(ssh_os)
    CpuInit01.cpu_cores_disable_sys_normally(ssh_os)
    CpuInit01.cores_customized_by_unitool(ssh_os)
    if Os.boot_to_suse():
        Smbios09.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Security22.Pwd_test(ser)
    MemInit02.dimm_power_mgt_01()
    MemInit02.dimm_power_mgt_02()
    MemInit02.dimm_power_mgt_04()
    MemInit02.dimm_power_mgt_05()
    MemInit02.dimm_power_mgt_07()
    Release.me_version_status()
    biosTest.loadDefault()
    MemInit02.Testcase_MemMargin_001()
    PchInit03.usb_default_enable_check()
    PchInit03.post_gpio_error_check()
    DefaultValueTest.pcie_port_bandwidth_check()
    biosTest.Testcase_SerialPrint_001()
    biosTest.Testcase_SerialPrint_003()
    PcieInit04.Testcase_PCIeResource_001()
    PcieInit04.Testcase_PCIeResource_002()
    PcieInit04.Testcase_PCIeResource_003()
    PcieInit04.Testcase_PCIeResource_005()
    biosTest.Testcase_PowerEfficiency_001(unitool)
    if Legacy.enable_legacy_boot():
        Legacy.disable_legacy_boot()


# Test scope for euipment mode image
def EquipScope():
    Release.equip_mode_version_check()
    Os.boot_to_suse_mfg()
    Smbios09.smbios_type128(unitool)
    MemInit02.Testcase_MemoryCompa_009(unitool)


# Define test scope for daily test
def DailyTest():
    UpdateBIOS.update_bios('master')
    TestScope()
    if UpdateBIOS.update_bios_mfg('master'):
        EquipScope()


def ReleaseTest():
    UpdateBIOS.update_bios('2288V6_011')
    TestScope()
    if UpdateBIOS.update_bios_mfg('2288V6_011'):
        EquipScope()


def Debug():
    UpdateBIOS.update_bios('master')
    CpuInit01.cpu_mem_info()
    MemInit02.Testcase_MemoryCompa_001()
    MemInit02.Testcase_MemoryCompa_006(ser, ssh_os)
    Io05.Testcase_SystemInfo_001(ser)
    Io05.Testcase_SystemInfo_002(ser)
    Io05.Testcase_SystemInfo_003(ser)
    biosTest.Testcase_PowerEfficiency_001(unitool)
