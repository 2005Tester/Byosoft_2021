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
import difflib


class LogAnalyzer:
    def __init__(self, log_dir):
        self.log_dir = log_dir
    #    self.config = config

    @staticmethod
    def load_log(log):
        log_list = []
        if os.path.exists(log):
            with open(log, 'r') as f:
                log_list = f.readlines()
        else:
            logging.info("{0} doesn't exist".format(log))
        return log_list

    # Check difference of two log files
    @staticmethod
    def check_diff(log1, log2):
        logging.info("Comparing {0} and {1}".format(log1, log2))
        try:
            with open(log1, 'r') as f:
                content_log1 = f.read().splitlines()
            with open(log2, 'r') as f:
                content_log2 = f.read().splitlines()
        except FileNotFoundError:
            logging.error("Please check whether log file exists.")
            return True
        d = difflib.Differ()
        diffs = list(d.compare(content_log1, content_log2))
        res = []
        for diff in diffs:
            if not re.search("^\s", diff):
                res.append(diff)
        return res

    def check_bios_log(self):
        ast = 0
        exception = 0
        error = 0
        bios_log = os.path.join(self.log_dir, "serial.log")
        data = self.load_log(bios_log)
        for line in data:
            if re.search("_assert", line, re.IGNORECASE):
                logging.info("Assert found in line {0}".format(data.index(line)+1))
                # logging.info(line)
                ast +=1
            if re.search("X64 Exception", line, re.IGNORECASE):
                logging.info("Exception found in line {0}".format(data.index(line)+1))
                # logging.info(line)
                exception +=1
        if ast == 0:
            logging.info("No assert found in serial log.")
        if exception == 0:
            logging.info("No exception found in serial log.")

        if (ast + exception + error) == 0:    
            return True

    def check_cpuinfo(self, cores):
        cpuinfo_log = os.path.join(self.log_dir, "cpuinfo.log")
        with open(cpuinfo_log, 'r') as f:
            data = f.read()
        corenumbers = re.findall("cpu cores\s+:\s+(\d+)", data)
        for num in corenumbers:
            if num == str(cores):
                pass
            else:
                logging.info("Core count is incorrect")
                return 
        logging.info("Core count is correct")
        return True


    # Check difference of two log files.
    # Return list of diffs,  return True if log_expected or log_actual not found
    @staticmethod
    def check_diff(log_expected, log_actual):
        logging.info("Comparing {0} and {1}".format(log_expected, log_actual))
        try:
            with open(log_expected, 'r') as f:
                content_expected = f.read().splitlines()
            with open(log_actual, 'r') as f:
                content_actual = f.read().splitlines()
        except FileNotFoundError:
            logging.error("Please check whether log file exists.")
            return True
        d = difflib.Differ()
        diffs = list(d.compare(content_expected, content_actual))
        res = []
        for diff in diffs:
            if not re.search("^\s", diff):
                res.append(diff)
        return res


    # Send a command via ssh, dump the result to current test log directory and diff with expected_log 
    # return Ture if no diff found
    def dump_and_verify(self, ssh, command, expected_log):
        if not ssh.login():
            return
        actual_log = ssh.dump_info(command, self.log_dir)
        diffs = LogAnalyzer.check_diff(expected_log, actual_log)
        if not isinstance(diffs, list):
            return
        if diffs:
            for diff in diffs:
                logging.info(diff)
            return
        logging.info("No difference found")
        return True