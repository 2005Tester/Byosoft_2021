#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import re
import time
import logging


class ReportGenerator:
    def __init__(self, template, log, report):
        self.template = template
        self.log = log
        self.report = report
    # load test log to list
    def load_test_log(self):
        log_lines = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                log_lines.append(line)
        return log_lines

    # Convert time string from log to timestamp
    @staticmethod
    def convert_time(time_str):
        time_arr = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(time_arr))
        return ts

    # get ids of executed test cases
    def get_tcids(self):
        tc_ids = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("<TC\d+><Tittle>.+:Start", line):
                    tc_ids.append(re.findall("(TC\d+)", line))
        return tc_ids

    # get test duration for a single test case by tese case if
    def get_tc_duration(self, id):
        duration = 0
        for line in self.load_test_log():
            if re.search("<{0}><Tittle>.+:Start".format(id), line):
                start_time = re.findall("(.+)\sINFO.+:Start", line)[0]
            if re.search("<{0}><Result>.+:.+".format(id), line):
                end_time = re.findall("(.+)\sINFO.+", line)[0]
        try:
            duration = self.convert_time(end_time) - self.convert_time(start_time)
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            duration = "%02d:%02d:%02d" %(h, m, s)
        except UnboundLocalError:
            logging.debug("get_tc_duration: failed to get start or end time, <{0}><Tittle>.+:Start or <{0}><Result>.+:.+ not found".format(id))
        return duration

    # get start time and total time spent in a test cycle
    def get_total_time(self):
        testlog = self.load_test_log()
        start_time = re.findall("(.+)\sINFO.+", testlog[0])[0]
        end_time = re.findall("(.+)\sINFO.+", testlog[-1])[0]
        total_time = self.convert_time(end_time) - self.convert_time(start_time)
        m, s = divmod(total_time, 60)
        h, m = divmod(m, 60)
        total_time = "%02d:%02d:%02d" %(h, m, s)
        return start_time, total_time

    # get test result by test case id
    def get_status(self, tcid):
        status = "NA"
        for line in self.load_test_log():
            if re.search("<{0}><Result>.+:.+".format(tcid), line):
                status = re.findall("<{0}><Result>.+:(.+)".format(tcid), line)[0]
        return status

    # get test log for a single test case by test case id
    def get_tc_log(self, tcid):
        log = []
        all_log = self.load_test_log()
        for line in all_log:
            if re.search("<{0}><Tittle>.+:Start".format(tcid), line):
                start_index = all_log.index(line)
            if re.search("<{0}><Result>.+:.+".format(tcid), line):
                end_index = all_log.index(line)
        try: 
            for i in range(start_index, end_index+1):
                log.append(all_log[i])  
        except UnboundLocalError:
            logging.debug("get_tc_log: failed to get index, <{0}><Tittle>.+:Start or <{0}><Result>.+:.+ not found".format(tcid))
        return log


    # get testcase description
    def get_des(self, tcid):
        des = "NA"
        for line in self.load_test_log():
            if re.search("<{0}><Description>.+".format(tcid), line):
                des = re.findall("<{0}><Description>(.+)".format(tcid), line)[0]
        return des


    # get number of pass, fail, skip test cases
    def get_result_count(self):
        pass_num = 0
        fail_num = 0
        skip_num = 0

        for line in self.load_test_log():
            if re.search("<TC\d+><Result>.+:Pass", line):
                pass_num +=1
            if re.search("<TC\d+><Result>.+:Fail", line):
                fail_num +=1
            if re.search("<TC\d+><Result>.+:Skip", line):
                skip_num +=1
        return pass_num, fail_num, skip_num

    # get code verion of test image
    def get_code_version(self):
        version = "NA"
        for line in self.load_test_log():
            if re.search("Latest Version is:", line):
                version = re.findall("Latest Version is: (\d+)", line)
        return version

    # collect and update test case result
    def collect_test_result(self):
        testReport = {}
        alltcResult = []
        tcResult = {}
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("<TC\d+><Tittle>.+:Start", line):
                    id = re.findall("(TC\d+)", line)[0]
                    tcResult['tcName'] = re.findall("<TC\d+><Tittle>(.+):Start", line)[0]
                    tcResult['description'] = self.get_des(id)
                    tcResult['spendTime'] = self.get_tc_duration(id)
                    tcResult['status'] = self.get_status(id)
                    tcResult['log'] = self.get_tc_log(id)
                    # tcResult['log'] = []
                    # print(tcResult)
                    alltcResult.append(tcResult.copy())
        testReport['testResult'] = alltcResult
        testReport['testVersion'] = self.get_code_version()
        testReport['testAll'] = len(alltcResult)
        testReport['testPass'] = self.get_result_count()[0]
        testReport['testFail'] = self.get_result_count()[1]
        testReport['testSkip'] = self.get_result_count()[2]
        testReport['beginTime'] = self.get_total_time()[0]
        testReport['totalTime'] = self.get_total_time()[1]
        return testReport

    # write test result dict to html report
    def write_to_html(self):
        old = "ResultDict"
        new = str(self.collect_test_result())
        dst = self.report

        with open(self.template, 'r', encoding='utf-8') as f:
            content = f.read()
            data = content.replace(old, new)
            with open(dst, 'w', encoding='utf-8') as new:
                new.write(data)
