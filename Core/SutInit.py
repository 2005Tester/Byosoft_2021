import importlib
import logging
from Common import SutSerial
from Common import ssh


class SutInit:
    def __init__(self, project):
        config = importlib.import_module('.SutConfig', package=project)
        self.sut = config.Sut
        self.serial_log = config.SERIAL_LOG
        logging.info("Initilizing SUT Connection...")
        self.bios_serial = self.init_bios_serial()
        if not self.bios_serial:
            logging.info("Failed to initilize BIOS serial port")

        self.bmc_serial = self.init_bmc_serial()
        if not self.bmc_serial:
            logging.info("Failed to initilize BMC serial port")

        self.bmc_ssh = self.init_bmc_ssh()
        if not self.bmc_ssh:
            logging.info("Failed to initilize BMC ssh connection")

        self.os_ssh = self.init_os_ssh()
        if not self.os_ssh:
            logging.info("Failed to initilize OS ssh connection")

        self.bmc_sftp = self.init_bmc_sftp()
        if not self.bmc_sftp:
            logging.info("Failed to initilize BMC SFTP connection")

        self.os_sftp = self.init_os_sftp()
        if not self.os_sftp:
            logging.info("Failed to initilize OS SFTP connection")

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

    def init_bmc_sftp(self):
        try:
            ip = self.sut.BMC_IP
            user = self.sut.BMC_USER
            password = self.sut.BMC_PASSWORD
            bmc_sftp = ssh.sftp(ip, user, password)
            return bmc_sftp
        except AttributeError:
            print("BMC IP not configured, skip initlize BMC SFTP interface")

    def init_os_sftp(self):
        try:
            ip = self.sut.OS_IP
            user = self.sut.OS_USER
            password = self.sut.OS_PASSWORD
            os_sftp = ssh.sftp(ip, user, password)
            return os_sftp
        except AttributeError:
            print("OS IP not configured, skip initilize OS SFTP interface")  
