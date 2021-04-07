import importlib
from Common import SutSerial
from Common import ssh


class SutInit:
    def __init__(self, project):
        config = importlib.import_module('.SutConfig', package=project)
        self.sut = config.Sut
        self.serial_log = config.SERIAL_LOG
        self.bios_serial = self.init_bios_serial()
        if not self.bios_serial:
            print("Failed to initilize BIOS serial port")

        self.bmc_serial = self.init_bmc_serial()
        if not self.bmc_serial:
            print("Failed to initilize BMC serial port")

        self.bmc_ssh = self.init_bmc_ssh()
        if not self.bmc_ssh:
            print("Failed to initilize BMC ssh connection")

        self.os_ssh = self.init_os_ssh()
        if not self.os_ssh:
            print("Failed to initilize OS ssh connection")

    def init_bios_serial(self):
        try:
            com_port = self.sut.BIOS_SERIAL
            bios_serial = SutSerial.SutControl(com_port, 115200, 0.5, self.serial_log)
            return bios_serial
        except AttributeError:
            print("BIOS Serial port not configured, skip initlize BIOS serial interface")

    def init_bmc_serial(self):
        try:
            com_port = self.sut.BMC_SERIAL
            bmc_serial = SutSerial.SutControl(com_port, 115200, 0.5, self.serial_log)
            return bmc_serial
        except AttributeError:
            print("BMC Serial port not configured, skip initlize BMC serial interface")

    def init_bmc_ssh(self):
        try:
            ip = self.sut.BMC_IP
            user = self.sut.BMC_USER
            password = self.sut.BMC_PASSWORD
            bmc_ssh = ssh.SshConnection(ip, user, password)
            return bmc_ssh
        except AttributeError:
            print("BMC IP not configured, skip initlize BMC Ssh interface")

    def init_os_ssh(self):
        try:
            ip = self.sut.OS_IP
            user = self.sut.OS_USER
            password = self.sut.OS_PASSWORD
            os_ssh = ssh.SshConnection(ip, user, password)
            return os_ssh
        except AttributeError:
            print("OS IP not configured, skip initilize OS Ssh interface")

    def init_unitool(self):
        pass

    def ping_sut(self):
        pass