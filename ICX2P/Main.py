from Common import SutSerial, Unitool, ssh
from Core import SutInit
from Core.SutInit import Sut
from ICX2P import UpdateBIOS, biosTest, DefaultValueTest, Os, Release, Smbios, Pwd, Legacy, DIMM, Cpu, Pch, Hotkey
from ICX2P.Config import SutConfig


# init SUT
SutInit.SutInit("ICX2P")
ser = Sut.BIOS_COM
ssh_bmc = Sut.BMC_SSH
ssh_os = Sut.OS_SSH
sftp_bmc = Sut.BMC_SFTP

# init unitool
unitool = Unitool.SshUnitool(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD, SutConfig.UNI_PATH)


# Test scope for non-equipment build
def TestScope():
    biosTest.POST_Test(ser)
    biosTest.PM(ser)
    biosTest.usbTest(ser, ssh_bmc)
    Cpu.cpu_mem_info(ser)
    biosTest.pressF2(ser)
    Cpu.static_turbo_default(ser)
    Cpu.ufs_default_value(ser)
    DefaultValueTest.rrqirq(ser)
    biosTest.dram_rapl_option_check(ser, ssh_bmc)
    biosTest.securityBoot(ser)
    biosTest.vtd(ser)
    biosTest.cnd_default_enable(ser, ssh_bmc)
    Cpu.upi_link_status(ser)
    Cpu.cpu_cores_active_enable_1(ser, ssh_bmc, ssh_os)
    Cpu.cpu_cores_active_enable_middle(ser, ssh_bmc, ssh_os)
    Cpu.cpu_cores_active_enable_max(ser, ssh_bmc, ssh_os)
    if Os.boot_to_suse(ser):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.Pwd_test(ser, ssh_bmc, ssh_os)
    DIMM.DPM.dimm_power_mgt_01(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_02(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_04(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_05(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_07(ser, ssh_bmc)
    Release.me_version_status(ser)
    biosTest.loadDefault(ser, ssh_bmc)
    biosTest.vtd(ser)
    DIMM.Testcase_MemMargin_001(ser, ssh_bmc)
    Pch.usb_default_enable_check(ser)
    Pch.post_gpio_error_check(ser, ssh_bmc)
    if Legacy.enable_legacy_boot():
        Legacy.disable_legacy_boot()


# Test scope for euipment mode image
def EquipScope():
    Release.equip_mode_version_check()
    Os.boot_to_suse_mfg(ser)
    Smbios.smbios_type128(ser, ssh_os, ssh_bmc, unitool)


# Define test scope for daily test
def DailyTest():
    UpdateBIOS.update_bios(ser, ssh_bmc, sftp_bmc, 'master')
    TestScope()
    if UpdateBIOS.update_bios_mfg(ser, ssh_bmc, sftp_bmc, 'master'):
        EquipScope()


def ReleaseTest():
    UpdateBIOS.update_bios(ser, ssh_bmc, sftp_bmc, '2288V6_010')
    TestScope()
    if UpdateBIOS.update_bios_mfg(ser, ssh_bmc, sftp_bmc, '2288V6_010'):
        EquipScope()


def Debug():
    Cpu.cpu_mem_info(ser, ssh_bmc)
    DIMM.Testcase_MemoryCompa_001(ser)
    DIMM.Testcase_MemoryCompa_006(ser, ssh_bmc, ssh_os)
    Hotkey.Testcase_SystemInfo_001(ser)
    Hotkey.Testcase_SystemInfo_002(ser)
    Hotkey.Testcase_SystemInfo_003(ser)
    Smbios.smbios_type128(ser, ssh_os, ssh_bmc, unitool)
    DIMM.Testcase_MemoryCompa_009(ser, ssh_bmc, unitool)
    biosTest.Testcase_SerialPrint_001(ser, ssh_bmc)
    biosTest.Testcase_SerialPrint_002(ser)
