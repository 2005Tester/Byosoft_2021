#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

import os
import logging
import logging.config
import argparse
from Common import LogConfig
from Report.ReportGen import ReportGenerator


class CliParse:
    def __init__(self):
        my_parser = argparse.ArgumentParser()
        my_parser.add_argument("ProjectName", help="Supported projects: ICX2P, Pangea")
        my_parser.add_argument("ExecutionType", help="Supported Execution Type: daily, release, debug, loop")
        my_parser.add_argument("-p", "--post", action="store_true", help="Opional: Post test resul to web portl")
        args = my_parser.parse_args()
        self.project = args.ProjectName
        self.execution_type = args.ExecutionType
        if args.post:
            self.post = args.post
        else:
            self.post = None

    def get_project(self):
        return self.project

    def get_execution_type(self):
        return self.execution_type

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
        logging.info("Test Project: {0}".format(self.config.PROJECT_NAME))
        logging.info("SUT Configuration: {0}".format(self.config.SUT_CONFIG))
        return log_dir

    def gen_report(self, log_dir):
        template = self.config.REPORT_TEMPLATE
        report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
        report.write_to_html()
        if self.post:
            print("Posting result to database.")
            report.post_result()

    def run(self):
        if self.execution_type not in ["daily", "release", "debug"]:
            print("Option: \"{0}\" not supported".format(self.execution_type))
            return
        logdir = self.init_log()
        if self.execution_type == "daily":
            print(self.config.PROJECT_NAME)
            self.script.DailyTest()
        elif self.execution_type == "release":
            print(self.config.PROJECT_NAME)
            self.script.ReleaseTest()
        elif self.execution_type == "debug":
            print(self.config.PROJECT_NAME)
            self.script.Debug()
        self.gen_report(logdir)
