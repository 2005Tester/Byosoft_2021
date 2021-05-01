from Common import SutSerial, Unitool, ssh
from ICX2P import UpdateBIOS, biosTest, DefaultValueTest, Os, Release, Smbios, Pwd, Legacy, DIMM, Cpu, Pch, Hotkey
from ICX2P.Config import SutConfig


# init seril
ser = SutSerial.SutControl(SutConfig.BIOS_SERIAL, 115200, 0.5, SutConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)
sftp_bmc = ssh.sftp(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)

# init ssh os interface
ssh_os = ssh.SshConnection(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD)
unitool = Unitool.SshUnitool(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD, SutConfig.UNI_PATH)


# Test scope for non-equipment build
def TestScope():
    biosTest.POST_Test(ser, ssh_bmc)
    biosTest.PM(ser, ssh_bmc)
    biosTest.usbTest(ser, ssh_bmc)
    Cpu.cpu_mem_info(ser, ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    Cpu.static_turbo_default(ser, ssh_bmc)
    Cpu.ufs_default_value(ser, ssh_bmc)
    DefaultValueTest.rrqirq(ser, ssh_bmc)
    biosTest.dram_rapl_option_check(ser, ssh_bmc)
    biosTest.securityBoot(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    biosTest.cnd_default_enable(ser, ssh_bmc)
    Cpu.upi_link_status(ser, ssh_bmc)
    Cpu.cpu_cores_active_enable_1(ser, ssh_bmc, ssh_os)
    Cpu.cpu_cores_active_enable_middle(ser, ssh_bmc, ssh_os)
    Cpu.cpu_cores_active_enable_max(ser, ssh_bmc, ssh_os)
    if Os.boot_to_suse(ser, ssh_bmc):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.Pwd_test(ser, ssh_bmc, ssh_os)
    DIMM.DPM.dimm_power_mgt_01(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_02(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_04(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_05(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_07(ser, ssh_bmc)
    Release.me_version_status(ser, ssh_bmc)
    biosTest.loadDefault(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    DIMM.Testcase_MemMargin_001(ser, ssh_bmc)
    Pch.usb_default_enable_check(ser, ssh_bmc)
    Pch.post_gpio_error_check(ser, ssh_bmc)
    if Legacy.enable_legacy_boot(ser, ssh_bmc):
        Legacy.disable_legacy_boot(ser, ssh_bmc)


# Test scope for euipment mode image
def EquipScope():
    Release.equip_mode_version_check(ser, ssh_bmc)
    Os.boot_to_suse_mfg(ser, ssh_bmc)
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
    DIMM.Testcase_MemoryCompa_001(ser, ssh_bmc)
    DIMM.Testcase_MemoryCompa_006(ser, ssh_bmc, ssh_os)
    Hotkey.Testcase_SystemInfo_001(ser, ssh_bmc)
    Hotkey.Testcase_SystemInfo_002(ser, ssh_bmc)
    Hotkey.Testcase_SystemInfo_003(ser, ssh_bmc)
    Smbios.smbios_type128(ser, ssh_os, ssh_bmc, unitool)
    DIMM.Testcase_MemoryCompa_009(ser, ssh_bmc, unitool)
    biosTest.Testcase_SerialPrint_001(ser, ssh_bmc)
    biosTest.Testcase_SerialPrint_002(ser, ssh_bmc)
