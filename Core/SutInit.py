import importlib
import logging
from Common import SutSerial
from Common import ssh
from Common import Unitool
from Common import RedfishLib
from Core import var


class Sut:
    BIOS_COM = None
    BMC_COM = None
    BMC_SSH = None
    BMC_SFTP = None
    BMC_RFISH = None
    OS_SSH = None
    OS_SFTP = None
    UNITOOL = None


class SutInit:
    def __init__(self, project):
        config = importlib.import_module('.Config.SutConfig', package=project)
        self.sut = config
        var.set('log_dir', config.LOG_DIR)
        logging.info("Initilizing SUT Connection...")

        Sut.BIOS_COM = self.init_bios_serial()
        if not Sut.BIOS_COM:
            logging.info("Failed to initilize BIOS serial port")

        Sut.BMC_COM = self.init_bmc_serial()
        if not Sut.BMC_COM:
            logging.info("Failed to initilize BMC serial port")

        Sut.BMC_SSH = self.init_bmc_ssh()
        if not Sut.BMC_SSH:
            logging.info("Failed to initilize BMC ssh connection")

        Sut.OS_SSH = self.init_os_ssh()
        if not Sut.OS_SSH:
            logging.info("Failed to initilize OS ssh connection")

        Sut.BMC_SFTP = self.init_bmc_sftp()
        if not Sut.BMC_SFTP:
            logging.info("Failed to initilize BMC SFTP connection")

        Sut.BMC_RFISH = self.init_bmc_redfish()
        if not Sut.BMC_RFISH:
            logging.info("Failed to initilize BMC Redfish connection")

        Sut.OS_SFTP = self.init_os_sftp()
        if not Sut.OS_SFTP:
            logging.info("Failed to initilize OS SFTP connection")

        Sut.UNITOOL = self.init_unitool()
        if not Sut.UNITOOL:
            logging.info("Failed to initilize unitool")

    def init_bios_serial(self):
        try:
            com_port = self.sut.BIOS_SERIAL
            bios_serial = SutSerial.SutControl(com_port, 115200, 0.5)
            return bios_serial
        except AttributeError:
            logging.error("BIOS Serial port not configured, skip initlize BIOS serial interface")

    def init_bmc_serial(self):
        try:
            com_port = self.sut.BMC_SERIAL
            bmc_serial = SutSerial.SutControl(com_port, 115200, 0.5)
            return bmc_serial
        except AttributeError:
            logging.error("BMC Serial port not configured, skip initlize BMC serial interface")

    def init_bmc_ssh(self):
        try:
            ip = self.sut.BMC_IP
            user = self.sut.BMC_USER
            password = self.sut.BMC_PASSWORD
            bmc_ssh = ssh.SshConnection(ip, user, password)
            return bmc_ssh
        except AttributeError:
            logging.error("BMC IP not configured, skip initlize BMC Ssh interface")

    def init_os_ssh(self):
        try:
            ip = self.sut.OS_IP
            user = self.sut.OS_USER
            password = self.sut.OS_PASSWORD
            os_ssh = ssh.SshConnection(ip, user, password)
            return os_ssh
        except AttributeError:
            logging.error("OS IP not configured, skip initilize OS Ssh interface")

    def init_bmc_sftp(self):
        try:
            ip = self.sut.BMC_IP
            user = self.sut.BMC_USER
            password = self.sut.BMC_PASSWORD
            bmc_sftp = ssh.sftp(ip, user, password)
            return bmc_sftp
        except AttributeError:
            logging.error("BMC IP not configured, skip initlize BMC SFTP interface")

    def init_bmc_redfish(self):
        try:
            ip = self.sut.BMC_IP
            user = self.sut.BMC_USER
            password = self.sut.BMC_PASSWORD
            bmc_redfish = RedfishLib.Redfish(ip, user, password)
            return bmc_redfish
        except AttributeError:
            logging.error("BMC IP not configured, skip initlize BMC SFTP interface")

    def init_os_sftp(self):
        try:
            ip = self.sut.OS_IP
            user = self.sut.OS_USER
            password = self.sut.OS_PASSWORD
            os_sftp = ssh.sftp(ip, user, password)
            return os_sftp
        except AttributeError:
            logging.error("OS IP not configured, skip initilize OS SFTP interface")  

    def init_unitool(self):
        try:
            ip = self.sut.OS_IP
            user = self.sut.OS_USER
            password = self.sut.OS_PASSWORD
            tool_path = self.sut.UNI_PATH
            unitool = Unitool.SshUnitool(ip, user, password, tool_path, True)
            return unitool
        except Exception as e:
            logging.error("Failed to init unitool")
            logging.error(e)
