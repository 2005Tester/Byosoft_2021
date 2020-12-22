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
from ICX2P import UpdateBIOS, IcxConfig
from Report.ReportGen import ReportGenerator



# Init log setting
log_dir = IcxConfig.LOG_DIR
log_format = LogConfig.gen_config(log_dir)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)


# init seril
ser = SutSerial.SutControl(IcxConfig.BIOS_SERIAL, 115200, 0.5, IcxConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection()

# Generate html test report
def gen_report():
    template = IcxConfig.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.write_to_html()

    
# for debug purpose
def debug_run():
    pass


# Define test scope here
def run_test():
    UpdateBIOS.update_bios(ser, log_dir)
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

