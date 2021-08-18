import importlib
import logging
import json
import sys
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


class ProjectInit:
    def __init__(self, cliparser):
        self.cli = cliparser
        self.prjcfg_file = 'ProjectConfig.json'
        with open(self.prjcfg_file, 'r') as f:
            self.project_list = json.load(f)

    def load_project(self):
        if not self.project_list:
            print("ProjectConfig.json not successfully loaded, exit test.")
            sys.exit(0)
        # get list of supported projects configured in json file.
        supported_prjs = [prj['ProjectName'] for prj in self.project_list]
        supported_prjs_dict = {item.lower(): item for item in supported_prjs}
        prj_lower = self.cli.get_project()
        sut_lower = self.cli.get_sutname()

        if prj_lower in list(supported_prjs_dict.keys()):
            project_name = supported_prjs_dict[prj_lower]
        else:
            print("Project not found, please double check ProjectConfig.json.")
            sys.exit(0)

        # Get config module file for specified SUT
        for prj in self.project_list:
            if prj['ProjectName'] == project_name:
                resources = prj['Resources']
                supported_suts = list(prj['ConfigMapping'].keys())
                supported_suts_dict = {item.lower(): item for item in supported_suts}
                if sut_lower in list(supported_suts_dict.keys()):
                    sutcfg = prj['ConfigMapping'][supported_suts_dict[sut_lower]]
                else:
                    print("Sut:{0} not found, please double check ProjectConfig.json.".format(sut_lower))
                    sys.exit(0)
        sutcfg_module = '.Config.' + sutcfg

        var.set('SutCfg', sutcfg_module)
        var.set('project', project_name)
        # import sut config module and main script for test run
        cfg = importlib.import_module(sutcfg_module, package=project_name)
        script = importlib.import_module('.Main', package=project_name)
        return cfg, script, resources


class SutInit:
    def __init__(self, project, resources):
        config = importlib.import_module('.Config.SutConfig', package=project)
        self.sut = config.Env
        self.resources = resources
        var.set('log_dir', config.Env.LOG_DIR)
        logging.info("Initilizing SUT Connection...")

        if 'BIOS_COM' in self.resources:
            Sut.BIOS_COM = self.init_bios_serial()
            if not Sut.BIOS_COM:
                logging.info("Failed to initilize BIOS serial port")

        if 'BMC_COM' in self.resources:
            Sut.BMC_COM = self.init_bmc_serial()
            if not Sut.BMC_COM:
                logging.info("Failed to initilize BMC serial port")

        if 'BMC_SSH' in self.resources:
            Sut.BMC_SSH = self.init_bmc_ssh()
            if not Sut.BMC_SSH:
                logging.info("Failed to initilize BMC ssh connection")

        if 'OS_SSH' in self.resources:
            Sut.OS_SSH = self.init_os_ssh()
            if not Sut.OS_SSH:
                logging.info("Failed to initilize OS ssh connection")

        if 'BMC_SFTP' in self.resources:
            Sut.BMC_SFTP = self.init_bmc_sftp()
            if not Sut.BMC_SFTP:
                logging.info("Failed to initilize BMC SFTP connection")

        if 'BMC_RFISH' in self.resources:
            Sut.BMC_RFISH = self.init_bmc_redfish()
            if not Sut.BMC_RFISH:
                logging.info("Failed to initilize BMC Redfish connection")

        if 'OS_SFTP' in self.resources:
            Sut.OS_SFTP = self.init_os_sftp()
            if not Sut.OS_SFTP:
                logging.info("Failed to initilize OS SFTP connection")

        if 'UNITOOL' in self.resources:
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
        except Exception as e:
            logging.error(e)
            logging.error("BMC IP not configured, skip initlize BMC Redfish interface")

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
