
from Common import SutSerial
from Common import ssh
from ICX2P import UpdateBIOS, SutConfig, biosTest, DefaultValueTest, Os, Release


# init seril
ser = SutSerial.SutControl(SutConfig.BIOS_SERIAL, 115200, 0.5, SutConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)


# Define test scope for daily test
def DailyTest():
    UpdateBIOS.update_bios(ser, SutConfig.LOG_DIR)
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
    Os.boot_to_suse(ser, ssh_bmc)


def ReleaseTest():
    print("Run release test for ICX 2P.")
    Release.me_version_status(ser, ssh_bmc)


def Debug():
    print("Run debug test for ICX 2P.")
