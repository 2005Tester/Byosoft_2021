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
from Moc25 import updatebios
from Moc25 import Moc25Config
from Moc25 import Moc25TcLib
from Moc25 import LogCheck
from Moc25 import SetUp
from Report.ReportGen import ReportGenerator
from Report import SendReport


# Init log setting
log_dir = Moc25Config.LOG_DIR
log_format = LogConfig.gen_config(log_dir)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)


# init seril
ser = SutSerial.SutControl("com5", 115200, 0.5, Moc25Config.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection()




def gen_report():
    template = Moc25Config.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.write_to_html()
    #mail_report = report.gen_email_report(Moc25Config.MAIL_TEMPLATE)
    #mail = SendReport.EmailReport(Moc25Config.MAIL_SERVER, Moc25Config.MAIL_FROM, Moc25Config.MAIL_TO, Moc25Config.MAIL_PW)
    #mail.send_mail(mail_report, os.path.join(log_dir, "report.html"))
    

def debug_run():
    log_dir = "C:\\daily\\Moc25\\2020-10-27_17-43-30"
    template = Moc25Config.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    mail_report = report.gen_email_report(Moc25Config.MAIL_TEMPLATE)
    mail = SendReport.EmailReport(Moc25Config.MAIL_SERVER, Moc25Config.MAIL_FROM, Moc25Config.MAIL_TO, Moc25Config.MAIL_PW)
    mail.send_mail(mail_report, os.path.join(log_dir, "report.html"))
    with open('mail.html', 'w') as f:
        f.write(mail_report)


def run_test():
    #updatebios.get_test_image(Moc25Config.BINARY_DIR)
    #SetUp.check_bios_version(ser, ssh_bmc)
    #Moc25TcLib.boot_AliOS(ser, ssh_bmc)
    #SetUp.check_me_status(ser, ssh_bmc)
    SetUp.boot_uefi_shell(ser, ssh_bmc)
    #SetUp.check_cpu_info(ser, ssh_bmc)
    #SetUp.pxe_boot(ser, ssh_bmc)
    LogCheck.check_log(log_dir)
    LogCheck.check_post_information(log_dir)
    gen_report()


if __name__ == '__main__':
    if len(argv) == 1:
        run_test()

    elif argv[1] == "loop":
        cycle = 1
        while True:
            logging.info("-"*50 + "\n" + " "*45 + "Test Cycle:{0}".format(cycle))
            logging.info("-"*50)
            run_test()
            cycle +=1
    elif argv[1] == "debug":
        debug_run()

