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

    def read_csv2dict(self):
        with open(self.csv_file, 'r') as f:
            tcs = csv.DictReader(f)
            for row in tcs:
                self.all_tc.append(row)

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
                if module and os.path.exists('ICX2P\\TestCase\\' + module + '.py'):
                    # to do: add check for function definition
                    self.tc_to_run.append(tc)
                else:
                    logging.info("TC:{0},  Module: {1} doesn't exist".format(tc, module))
            except Exception:
                if tc['Name'] == '':
                    pass
                else:
                    logging.error("Invalid test case: {0}".format(tc))
        logging.info("checking csv file done.")

    # do do
    def check_duplicate():
        pass

    # to do
    def check_module_importd():
        pass

    def get_test_cases(self):
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
        print("Default:", len(self.default))
        print("Equip:", len(self.equip))
        print("Legacy:", len(self.legacy))
        print("OS:", len(self.os))
        print("Total Test case number: {0}".format(len(self.default) + len(self.legacy) + len(self.os) + len(self.equip)))