#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging.config
import os
from sys import argv

from Common import ssh
from Common import SutSerial
from Common import LogConfig
from HY5 import SetUp
from HY5 import Hy5Config, Hy5BasicFunc
from Report.ReportGen import ReportGenerator

# Init log setting
log_dir = Hy5Config.LOG_DIR
shar_dir = Hy5Config.SHAR_DIR
log_format = LogConfig.gen_config(log_dir)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)

# init serial,
ser = SutSerial.SutControl("com3", 115200, 0.5, Hy5Config.SERIAL_LOG)
# init ssh
sshins = ssh.SshConnection()


def gen_report():
    template = Hy5Config.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    # shar_report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(shar_dir, "report.html"))
    report.collect_test_result()
    # shar_report.collect_test_result()
    report.write_to_html()
    # shar_report.write_to_html()
    shutil.copytree(log_dir, shar_dir, ignore=None)  # if local debug, this line should be annotated


def test_run():
    Hy5BasicFunc.hy5BasicTest(ser, sshins)
    SetUp.biosSetupTest(ser, sshins)
    gen_report()


if __name__ == "__main__":
    if argv[1] == "hy5":
        test_run()

    # elif argv[1] == "loop":
    #     cycle = 1
    #     while True:
    #         logging.info("-" * 50 + "\n" + " " * 45 + "Test Cycle:{0}".format(cycle))
    #         logging.info("-" * 50)
    #         test_run()
    #         cycle += 1
