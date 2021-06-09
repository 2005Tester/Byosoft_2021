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
from Core import var
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


EXEC_TYPE = ['Release', 'Daily', 'Weekly']
TC_GROUP = ['default', 'os', 'legacy', 'equip', 'fulldebug']


class TestScope:
    def __init__(self, csv_file, execution_type):
        if execution_type not in EXEC_TYPE:
            logging.error("Wrong parameter, supported execution type: {0}".format(EXEC_TYPE))
            return
        self.project = var.get('project')
        self.csv_file = csv_file
        self.execution_type = execution_type
        self.default = []
        self.legacy = []
        self.os = []
        self.equip = []
        self.fulldebug = []
        self.all_tc = []  # all the test cases loaded from csv file
        self.tc_to_run = []  # test cases pass check
        self.csv_errs = []
        self._read_csv2dict()
        self._filter_invalid_Case()
        self._get_test_cases()

    def _read_csv2dict(self):
        with open(self.csv_file, 'r') as f:
            tcs = csv.DictReader(f)
            for row in tcs:
                if row['Name'] == '':
                    pass
                else:
                    self.all_tc.append(row)

    def _check_case(self, file_name, func_name):
        module_path = '{0}\\TestCase\\'.format(self.project) + file_name + '.py'
        if file_name and os.path.exists(module_path):
            # todo add test function check
            return True
        else:
            logging.error("Check fail: {0}.{1}".format(file_name, func_name))

    def _filter_invalid_Case(self):
        logging.info("Check and remove invalid test cases...")
        invalid_case = 0
        for tc in self.all_tc:
            try:
                module, case = tuple(tc['Name'].split('.'))
                if self._check_case(module, case):
                    self.tc_to_run.append(tc)
                else:
                    logging.info("TC:{0},  Module: {1} doesn't exist".format(tc, module))
                    self.csv_errs.append("TC:{0},  Module: {1} doesn't exist".format(tc, module))
                    invalid_case += 1
            except Exception as e:
                if tc['Name'] == '':
                    pass
                else:
                    logging.error("Invalid test case: {0}".format(tc))
                    logging.error(e)
                    self.csv_errs.append("Invalid test case: {0}".format(tc))
                    invalid_case += 1
        logging.info("{0} invalid test case found.".format(invalid_case))

    # Check whether all the test cases are valid
    def check_csv(self):
        logging.info("Start checking {0}".format(self.csv_file))
        if self.all_tc is None:
            logging.error("Error, read csv file failed")
            return
        self._check_duplicate()  # check duplicate test cases
        if self.csv_errs:
            logging.info("[Failed]Checking csv file, {0} errors found:".format(len(self.csv_errs)))
            for err in self.csv_errs:
                logging.error(err)
        else:
            logging.info("[Pass]Checking csv file done")

    # check whether there are duplicate test cases in csv file.
    def _check_duplicate(self):
        logging.info("Checking duplicate test cases...")
        temp_list = []
        for tc in self.all_tc:
            if tc['Name'] in temp_list:
                logging.error("Duplicate test case found: {0}".format(tc))
                self.csv_errs.append("Duplicated test case: {0}".format(tc))
            else:
                temp_list.append(tc['Name'])

    def _get_test_cases(self):
        logging.info("Get test cases to be executed.")
        if self.tc_to_run is None:
            logging.error("Test case list is empty")
            return
        for row in self.tc_to_run:
            if row[self.execution_type]:
                if row['Group'] == 'os':
                    self.os.append(row['Name'])
                elif row['Group'] == 'legacy':
                    self.legacy.append(row['Name'])
                elif row['Group'] == 'equip':
                    self.equip.append(row['Name'])
                elif row['Group'] == 'fulldebug':
                    self.fulldebug.append(row['Name'])
                else:
                    self.default.append(row['Name'])
        logging.info("Default: {0}".format(len(self.default)))
        logging.info("Equip: {0}".format(len(self.equip)))
        logging.info("Legacy: {0}".format(len(self.legacy)))
        logging.info("OS: {0}".format(len(self.os)))
        logging.info("Full Debug: {0}".format(len(self.fulldebug)))
        logging.info("Total Test cases: {0}".format(len(self.default) + len(self.legacy) + len(self.os) + len(self.equip)))

    # fetch and run valid test cases defined in csv file
    def run_test(self, category):
        if category not in TC_GROUP:
            logging.error("Wrong parameter, supported category: {0}".format(TC_GROUP))

        scope = {
            TC_GROUP[0]: self.default,
            TC_GROUP[1]: self.os,
            TC_GROUP[2]: self.legacy,
            TC_GROUP[3]: self.equip,
            TC_GROUP[4]: self.fulldebug
        }
        testcases = scope[category]
        for tc in testcases:
            module, case = tc.split('.')
            casename, para = case.split('(')
            para = para.replace(')', '')
            try:
                mde = importlib.import_module(name='.TestCase.{0}'.format(module), package='{0}'.format(self.project))
                func = getattr(mde, casename)
                if para == '':
                    func()
                else:
                    pass
            except Exception as e:
                logging.error("Faile to execute test case: {0}.{1}".format(module, case))
                logging.error(e)
