
from Common import SutSerial, Unitool, ssh
from ICX2P import UpdateBIOS, SutConfig, biosTest, DefaultValueTest, Os, Release, Smbios, Pwd, Legacy


# init seril
ser = SutSerial.SutControl(SutConfig.BIOS_SERIAL, 115200, 0.5, SutConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)

# init ssh os interface
ssh_os = ssh.SshConnection(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD)
unitool = Unitool.SshUnitool(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD, SutConfig.UNI_PATH)


# Define test scope for daily test
def DailyTest():
    UpdateBIOS.update_bios(ser, SutConfig.LOG_DIR, 'master')
    biosTest.POST_Test(ser, ssh_bmc)
    biosTest.PM(ser, ssh_bmc)
    biosTest.usbTest(ser, ssh_bmc)
    biosTest.ProcessorDIMM(ser, ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    biosTest.loadDefault(ser, ssh_bmc)
    biosTest.staticTurbo(ser, ssh_bmc)
    biosTest.ufs(ser, ssh_bmc)
    DefaultValueTest.rrqirq(ser, ssh_bmc)
    biosTest.dramRAPL(ser, ssh_bmc)
    biosTest.securityBoot(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    biosTest.cpuCOMPA(ser, ssh_bmc)
    if Os.boot_to_suse(ser, ssh_bmc):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.simplePWDTest(ser, ssh_bmc)
    Pwd.Simple_password_validity(ser, ssh_bmc)
    Pwd.Simple_password_disenable(ser, ssh_bmc)
    Pwd.Simple_password_save_enable(ser, ssh_bmc)
    Pwd.Simple_password_save_disable(ser, ssh_bmc)
    Release.me_version_status(ser, ssh_bmc)
    if UpdateBIOS.update_bios_mfg(ser, SutConfig.LOG_DIR, 'master'):
        Os.boot_to_suse_mfg(ser, ssh_bmc)


def ReleaseTest():
    UpdateBIOS.update_bios(ser, SutConfig.LOG_DIR, '2288V6_008')
    biosTest.POST_Test(ser, ssh_bmc)
    biosTest.PM(ser, ssh_bmc)
    biosTest.usbTest(ser, ssh_bmc)
    biosTest.ProcessorDIMM(ser, ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    biosTest.staticTurbo(ser, ssh_bmc)
    biosTest.ufs(ser, ssh_bmc)
    DefaultValueTest.rrqirq(ser, ssh_bmc)
    biosTest.dramRAPL(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    biosTest.cpuCOMPA(ser, ssh_bmc)
    if Os.boot_to_suse(ser, ssh_bmc):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.simplePWDTest(ser, ssh_bmc)
    Pwd.Simple_password_validity(ser, ssh_bmc)
    Pwd.Simple_password_disenable(ser, ssh_bmc)
    Pwd.Simple_password_save_enable(ser, ssh_bmc)
    Pwd.Simple_password_save_disable(ser, ssh_bmc)
    Release.me_version_status(ser, ssh_bmc)
    biosTest.loadDefault(ser, ssh_bmc)
    if UpdateBIOS.update_bios_mfg(ser, SutConfig.LOG_DIR, '2288V6_008'):
        Os.boot_to_suse_mfg(ser, ssh_bmc)
    if Legacy.enable_legacy_boot(ser, ssh_bmc):
        Legacy.disable_legacy_boot(ser, ssh_bmc)


def Debug():
    print("Run debug test for ICX 2P.")
    biosTest.loadDefault(ser, ssh_bmc)
