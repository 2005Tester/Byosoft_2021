#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
import logging.config
import os
from ICX2P import Pwd
from sys import argv
from Common import LogConfig
from Common import SutSerial
from Common import ssh
from ICX2P import UpdateBIOS, SutConfig, biosTest, DefaultValueTest, Cpu, Os
from Report.ReportGen import ReportGenerator
from ICX2P.BaseLib import SetUpLib

# init seril
ser = SutSerial.SutControl(SutConfig.BIOS_SERIAL, 115200, 0.5, SutConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)


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
    if len(argv)==2 and argv[1] == "daily":
        report.post_result()


# for debug purpose
def debug_run():
    log_dir = init_log()
    UpdateBIOS.update_bios(ser, log_dir)
#    DefaultValueTest.test(ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    gen_report(log_dir)


# Define test scope here
def run_test():
    log_dir = init_log()
    UpdateBIOS.update_bios(ser, log_dir)
    biosTest.POST_Test(ser, ssh_bmc)
    biosTest.PM(ser, ssh_bmc)
#    biosTest.pxeTest(ser, ssh_bmc)
#    biosTest.httpsTest(ser, ssh_bmc)
    biosTest.usbTest(ser, ssh_bmc)
    biosTest.ProcessorDIMM(ser, ssh_bmc)
#    biosTest.chipsecTest(ser, ssh_bmc)
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
#    biosTest.logTime(ser, ssh_bmc)
    Pwd.simplePWDTest(ser, ssh_bmc)
    Pwd.Simple_password_validity(ser, ssh_bmc)
    Pwd.Simple_password_disenable(ser, ssh_bmc)
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
