#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
import logging.config
import os
from sys import argv
from Common import LogConfig
from Common import SutSerial
from Common import ssh
from Pangea import SutConfig, Pcie
from Report.ReportGen import ReportGenerator
from Pangea.BaseLib import SetUpLib
from Pangea import ReleaseTest, UpdateBIOS

# init seril
ser = SutSerial.SutControl(SutConfig.BIOS_SERIAL, 115200, 0.5, SutConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)
ssh_os = ssh.SshConnection(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD)


# Init log setting
def init_log():
    log_dir = SutConfig.LOG_DIR
    log_format = LogConfig.gen_config(log_dir)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.info("Test Project: {0}".format(SutConfig.PROJECT_NAME))
    logging.info("SUT Configuration: {0}".format(SutConfig.SUT_CONFIG))
    return log_dir


# Generate html test report
def gen_report(log_dir):
    template = SutConfig.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.write_to_html()
    if argv[1] and argv[1] == "daily":
        report.post_result()


# for debug purpose
def debug_run():
    log_dir = init_log()
    Pcie.pci_resource_tree_view(ssh_os)
    Pcie.pci_resource_root_port(ssh_os)
    Pcie.lspci_diff(ssh_os)
    gen_report(log_dir)


# Define test scope here
def run_test():
    log_dir = init_log()
    UpdateBIOS.update_bios(ser, log_dir, ssh_bmc)
    ReleaseTest.post_test(ser, ssh_bmc)
    ReleaseTest.warm_reboot_cycling(ser, ssh_bmc, 2)
    ReleaseTest.pxeTest(ser, ssh_bmc)
    ReleaseTest.processor_dimm_basic_info(ser, ssh_bmc)
    ReleaseTest.load_default_save_reset(ser, ssh_bmc)
    ReleaseTest.boot_eulerOS(ser, ssh_bmc)

    gen_report(log_dir)


if __name__ == '__main__':
    if len(argv) == 1 or argv[1] == "daily":
        run_test()

    elif argv[1] == "loop":
        cycle = 1
        while True:
            logging.info("-"*50 + "\n" + " "*45 + "Test Cycle:{0}".format(cycle))
            logging.info("-"*50)
            run_test()
            cycle += 1
    elif argv[1] == "debug":
        debug_run()

