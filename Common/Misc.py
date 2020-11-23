#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-

import logging


# tc: tuple of test case basic information, 0:id, 1:tittle, 2:description
class LogHeaderResult:
    # write test case info to serial log and test log
    def __init__(self, tc, serial=None):
        self.tc = tc
        self.msg_start = '<TC{0}><Tittle>{1}:Start'.format(tc[0], tc[1])
        self.msg_description = '<TC{0}><Description>{1}'.format(tc[0], tc[2])
        self.msg_fail = '<TC{0}><Result>{1}:Fail'.format(tc[0], tc[1])
        self.msg_pass = '<TC{0}><Result>{1}:Pass'.format(tc[0], tc[1])
        self.msg_skip = '<TC{0}><Result>{1}:Skip'.format(tc[0], tc[1])
        if serial:
            self.msg_serial = 'TC{0} {1}\n'.format(tc[0], tc[1])
            serial.write_msg(self.msg_serial)
        logging.info(self.msg_start)
        logging.info(self.msg_description)

    def log_pass(self):
        logging.info(self.msg_pass)

    def log_fail(self):
        logging.info(self.msg_fail)

    def log_skip(self):
        logging.info(self.msg_skip)

