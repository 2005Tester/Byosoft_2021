#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import re
import os
import logging
from Common.LogAnalyzer import LogAnalyzer
from Moc25 import Moc25Config


# Test case for log analysis
def check_log(log_dir):
    log = LogAnalyzer(log_dir)
    logging.info("<TC900><Tittle>Check BIOS Log:Start")
    logging.info("<TC900><Description>Check whether there are asserts or exception in test")
    if log.check_bios_log():
        logging.info("<TC900><Result>Check BIOS Log:Pass")
    else:
        logging.info("<TC900><Result>Check BIOS Log:Fail")


# check post information
def check_post_information(log_dir):
    logging.info("<TC901><Tittle>Check Post Information:Start")
    logging.info("<TC901><Description>Verify Whether Information in post screen is correct")
    log = os.path.join(log_dir, 'serial.log')
    fail_cnt = 0
    if os.path.exists(log):
        with open(log, 'r') as f:
            data = f.read()
        if not re.search(Moc25Config.BIOS_VERSION, data):
            logging.info("BIOS version is not correct.")
            fail_cnt +=1
        if not re.search(Moc25Config.BMC_VERSION, data):
            logging.info("BMC version is not correct.")
            fail_cnt +=1
        if not re.search("CPU Information: Intel\(R\) Genuine processor", data):
            logging.info("CPU information is not correct.")
            fail_cnt +=1
        if not re.search("Total Memory Size: 4 GiB, 1 Pics, Current Speed: 2400 MHz", data):
            logging.info("Memory information is not correct.")
            fail_cnt +=1
    if fail_cnt > 0:
        logging.info("<TC901><Result>Check Post Information:Fail")
        return
    else:
        logging.info("<TC901><Result>Check Post Information:Pass")
        return True
