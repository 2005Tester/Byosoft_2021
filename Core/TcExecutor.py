#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

import os
import csv
import logging
import logging.config
import argparse
import importlib
from Common import LogConfig
from Report.ReportGen import ReportGenerator


class CliParse:
    def __init__(self):
        my_parser = argparse.ArgumentParser()
        my_parser.add_argument("ProjectName", help="Supported projects: ICX2P, Pangea, Hygon, TCE")
        my_parser.add_argument("ExecutionType", help="Supported Execution Type: daily, release, weekly, debug, checkcsv")
        my_parser.add_argument("-p", "--post", action="store_true", help="Opional: Post test resul to web portl")
        args = my_parser.parse_args()
        self.project = args.ProjectName
        self.execution_type = args.ExecutionType
        if args.post:
            self.post = args.post
        else:
            self.post = None

    def get_project(self):
        return self.project.lower()

    def get_execution_type(self):
        return self.execution_type.lower()

    def get_post(self):
        return self.post


class RunTest:
    def __init__(self, config, script, execution_type, post=None):
        self.config = config
        self.script = script
        self.execution_type = execution_type
        self.post = post

    def init_log(self):
        log_dir = self.config.LOG_DIR
        log_format = LogConfig.gen_config(log_dir)
        logging.config.dictConfig(log_format)
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        logging.info("Initializing test...")
        logging.info("Test Project: {0}".format(self.config.PROJECT_NAME))
        logging.info("SUT Configuration: {0}".format(self.config.SUT_CONFIG))
        return log_dir

    def gen_report(self, log_dir):
        logging.info("Generating report...")
        template = self.config.REPORT_TEMPLATE
        report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
        report.write_to_html()
        if self.post:
            print("Posting result to database.")
            report.post_result()

    def run(self):
        if self.execution_type not in ["daily", "release", "debug", "weekly", "checkcsv"]:
            print("Option: \"{0}\" not supported".format(self.execution_type))
            return
        logdir = self.init_log()
        if self.execution_type == "checkcsv":
            try:
                self.script.CheckCsv()
            except Exception as e:
                logging.error("Exception: {0}".format(e))
        if self.execution_type == "daily":
            try:
                self.script.DailyTest()
            except Exception as e:
                logging.error("Exception: {0}".format(e))
        if self.execution_type == "weekly":
            try:
                self.script.WeeklyTest()
            except Exception as e:
                logging.error("Exception: {0}".format(e))
        elif self.execution_type == "release":
            try:
                self.script.ReleaseTest()
            except Exception as e:
                logging.error("Exception: {0}".format(e))
        elif self.execution_type == "debug":
            try:
                self.script.Debug()
            except Exception as e:
                logging.error("Exception: {0}".format(e))
        self.gen_report(logdir)


class TestScope:
    def __init__(self, csv_file, execution_type):
        self.csv_file = csv_file
        self.execution_type = execution_type
        self.default = []
        self.legacy = []
        self.os = []
        self.equip = []
        self.all_tc = []  # all the test cases loaded from csv file
        self.tc_to_run = []  # test cases pass check
        self.check_csv()
        self.get_test_cases()

    def read_csv2dict(self):
        with open(self.csv_file, 'r') as f:
            tcs = csv.DictReader(f)
            for row in tcs:
                self.all_tc.append(row)

    def _check_case(self, file_name, func_name):
        module_path = 'ICX2P\\TestCase\\' + file_name + '.py'
        if file_name and os.path.exists(module_path):
            # todo add test function check
            return True
        else:
            logging.error("Check fail: {0}.{1}".format(file_name, func_name))

    # Check whether all the test cases are valid
    def check_csv(self):
        logging.info("Start checking {0}".format(self.csv_file))
        self.read_csv2dict()
        if self.all_tc is None:
            logging.error("Error, read csv file failed")
            return

        for tc in self.all_tc:
            try:
                module, case = tuple(tc['Name'].split('.'))
                if self._check_case(module, case):
                    self.tc_to_run.append(tc)
                else:
                    logging.info("TC:{0},  Module: {1} doesn't exist".format(tc, module))
            except Exception as e:
                if tc['Name'] == '':
                    pass
                else:
                    logging.error("Invalid test case: {0}".format(tc))
                    logging.error(e)
        logging.info("checking csv file done.")

    # do do
    def check_duplicate():
        pass

    def get_test_cases(self):
        logging.info("Get test cases to be executed.")
        for row in self.tc_to_run:
            if row[self.execution_type]:
                if row['Dependency'] == 'os':
                    self.os.append(row['Name'])
                elif row['Dependency'] == 'legacy':
                    self.legacy.append(row['Name'])
                elif row['Dependency'] == 'equip':
                    self.equip.append(row['Name'])
                else:
                    self.default.append(row['Name'])
        logging.info("Default: {0}".format(len(self.default)))
        logging.info("Equip: {0}".format(len(self.equip)))
        logging.info("Legacy: {0}".format(len(self.legacy)))
        logging.info("OS: {0}".format(len(self.os)))
        logging.info("Total Test cases: {0}".format(len(self.default) + len(self.legacy) + len(self.os) + len(self.equip)))

    def run_test(self, category):
        scope = {
            'os': self.os,
            'legacy': self.legacy,
            'equip': self.equip,
            'default': self.default
        }
        testcases = scope[category]
        for tc in testcases:
            module, case = tc.split('.')
            casename, para = case.split('(')
            para = para.replace(')', '')
            try:
                mde = importlib.import_module(name='.TestCase.{0}'.format(module), package='ICX2P')
                func = getattr(mde, casename)
                func(para)
            except Exception as e:
                logging.error("Faile to execute test case: {0}.{1}".format(module, case))
                logging.error(e)
