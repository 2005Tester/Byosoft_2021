from Common import SutSerial, Unitool, ssh
from ICX2P import UpdateBIOS, SutConfig, biosTest, DefaultValueTest, Os, Release, Smbios, Pwd, Legacy, DIMM, Cpu


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
    biosTest.ProcessorDIMM(ser, ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    Cpu.static_turbo_default(ser, ssh_bmc)
    Cpu.ufs_default_value(ser, ssh_bmc)
    DefaultValueTest.rrqirq(ser, ssh_bmc)
    biosTest.dram_rapl_option_check(ser, ssh_bmc)
    biosTest.securityBoot(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    biosTest.cnd_default_enable(ser, ssh_bmc)
    Cpu.upi_link_status(ser, ssh_bmc)
    if Os.boot_to_suse(ser, ssh_bmc):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.simplePWDTest(ser, ssh_bmc)
    Pwd.Simple_password_validity(ser, ssh_bmc)
    Pwd.Simple_password_disenable(ser, ssh_bmc)
    Pwd.Simple_password_save_enable(ser, ssh_bmc)
    Pwd.Simple_password_save_disable(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_002(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_003(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_004(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_005_019_021(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_006(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_007(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_008(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_009(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_010(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_011_012_014(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_013(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_015(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_016(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_020(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_022(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_01(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_07(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_08(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_09(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_01(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_02(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_04(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_05(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_07(ser, ssh_bmc)
    Release.me_version_status(ser, ssh_bmc)
    biosTest.loadDefault(ser, ssh_bmc)
    if Legacy.enable_legacy_boot(ser, ssh_bmc):
        Legacy.disable_legacy_boot(ser, ssh_bmc)


# Test scope for euipment mode image
def EquipScope():
    Os.move_suse_to_first(ser, ssh_bmc)
    Release.equip_mode_version_check(ser, ssh_bmc)
    Os.boot_to_suse_mfg(ser, ssh_bmc)


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
    print("Run debug test for ICX 2P.")
    # biosTest.loadDefault(ser, ssh_bmc)
    Release.hpm_upgrade_test(ser, ssh_bmc, sftp_bmc, unitool)
    Release.hpm_downgrade_test(ser, ssh_bmc, sftp_bmc, unitool)
