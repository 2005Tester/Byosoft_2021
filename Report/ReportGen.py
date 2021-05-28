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
import time
import logging
import requests
import glob
import pyautogui
import logging.config
from Core.SutInit import Sut
from Core import var
from json2html import *


# tc: tuple of test case basic information, 0:id, 1:tittle, 2:description
class LogHeaderResult:
    # write test case info to serial log and test log
    def __init__(self, tc, imgdir=None):
        self.tc = tc
        self.serial = Sut.BIOS_COM
        self.imgdir = imgdir
        self.suffix = 1
        self.msg_start = '<TC{0}><Tittle>{1}:Start'.format(tc[0], tc[1])
        self.msg_description = '<TC{0}><Description>{1}'.format(tc[0], tc[2])
        self.msg_fail = '<TC{0}><Result>{1}:Fail'.format(tc[0], tc[1])
        self.msg_pass = '<TC{0}><Result>{1}:Pass'.format(tc[0], tc[1])
        self.msg_skip = '<TC{0}><Result>{1}:Skip'.format(tc[0], tc[1])
        var.set('current_test', 'TC{0}'.format(tc[0]))
        # write serial_log to global variable
        var.set('serial_log', os.path.join(var.get('log_dir'), 'TC{0}.log'.format(tc[0])))
        if imgdir:
            if not os.path.isdir(imgdir):
                os.makedirs(imgdir)
        if self.serial:
            self.msg_serial = '\n##### TC{0} {1} #####\n'.format(tc[0], tc[1])
            self.serial.write_data2log(self.msg_serial)
        logging.info(self.msg_start)
        logging.info(self.msg_description)

    def log_progress(self):
        logging.info("<Overall Status>:{0} Passed, {1} Failed, {2} Skiped".format(var.get('num_pass'), var.get('num_fail'), var.get('num_skip')))

    def log_pass(self):
        logging.info(self.msg_pass)
        var.increase('num_pass')
        self.log_progress()
        logging.info("-"*80)
        if self.serial:
            self.msg_serial = '\n##### TC{0} {1}: Pass #####\n'.format(self.tc[0], self.tc[1])
            self.serial.write_data2log(self.msg_serial)

    def log_fail(self, capture=None):
        if capture:
            self.capture_screen()
        logging.info(self.msg_fail)
        var.increase('num_fail')
        self.log_progress()
        logging.info("-"*80)
        if self.serial:
            self.msg_serial = '\n##### TC{0} {1}: Fail #####\n'.format(self.tc[0], self.tc[1])
            self.serial.write_data2log(self.msg_serial)

    def log_skip(self):
        logging.info(self.msg_skip)
        var.increase('num_skip')
        self.log_progress()
        logging.info("-"*80)
        if self.serial:
            self.msg_serial = '\n##### TC{0} {1}: Skip #####\n'.format(self.tc[0], self.tc[1])
            self.serial.write_data2log(self.msg_serial)

    def capture_screen(self):
        filename = 'TC' + self.tc[0] + '_' + str(self.suffix) + ".jpg"
        if self.imgdir:
            file_path = os.path.join(self.imgdir, filename)
        else:
            logging.error("Screen Capture Failed: Image path not set.")
            return
        if os.path.exists(file_path):
            self.suffix += 1
            filename = 'TC' + self.tc[0] + '_' + str(self.suffix) + ".jpg"
            file_path = os.path.join(self.imgdir, filename)
        try:
            screen = pyautogui.screenshot()
            screen.save(os.path.join(self.imgdir, file_path))
            logging.info("Screen captured: {0}".format(filename))
        except Exception as e:
            logging.info("Failed to capture screen.")
            logging.error(e)


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
        time_arr = time.strptime(time_str, r"%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(time_arr))
        return ts

    # get ids of executed test cases
    def get_tcids(self):
        tc_ids = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search(r"<TC\d+><Tittle>.+:Start", line):
                    tc_ids.append(re.findall(r"(TC\d+)", line))
        return tc_ids

    # get test duration for a single test case by tese case if
    def get_tc_duration(self, id):
        duration = 0
        for line in self.load_test_log():
            if re.search("<{0}><Tittle>.+:Start".format(id), line):
                if re.findall(r"(.+)\sINFO.+:Start", line):
                    start_time = re.findall(r"(.+)\sINFO.+:Start", line)[0]
                else:
                    start_time = "2000-01-01 00:00:01"
            if re.search("<{0}><Result>.+:.+".format(id), line):
                if re.findall(r"(.+)\s(?:INFO|DEBUG|ERROR).+", line):
                    end_time = re.findall(r"(.+)\sINFO.+", line)[0]
                else:
                    end_time = start_time
        try:
            duration = self.convert_time(end_time) - self.convert_time(start_time)
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            duration = "%02d:%02d:%02d" %(h, m, s)
        except UnboundLocalError:
            logging.debug("get_tc_duration: failed to get start or end time for test case {0}".format(id))
        return duration

    # get start time and total time spent in a test cycle
    def get_total_time(self):
        testlog = self.load_test_log()
        start_time = re.findall(r"(.+)\s(?:INFO|DEBUG|ERROR).+", testlog[0])[0]
        end_time = re.findall(r"(.+)\s(?:INFO|DEBUG|ERROR):", testlog[-1])[0]
        total_time = self.convert_time(end_time) - self.convert_time(start_time)
        m, s = divmod(total_time, 60)
        h, m = divmod(m, 60)
        total_time = "%02d:%02d:%02d" % (h, m, s)
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
        start_index = 0
        end_index = 0
        err_index = 0
        # print(tcid)
        for line in all_log:
            if re.search("<{0}><Tittle>.+:Start".format(tcid), line):
                start_index = all_log.index(line)
                # print("start:{0}".format(start_index))
            if re.search("<{0}><Result>.+:.+".format(tcid), line):
                end_index = all_log.index(line)
                # print("end:{0}".format(end_index))
            if re.search("ERROR: Exception:", line):
                err_index = all_log.index(line)
        if end_index == 0:
            end_index = err_index
        else:
            end_index = start_index + 1

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
            if re.search(r"<TC\d+><Result>.+:Pass", line):
                pass_num += 1
            if re.search(r"<TC\d+><Result>.+:Fail", line):
                fail_num += 1
            if re.search(r"<TC\d+><Result>.+:Skip", line):
                skip_num += 1
        return pass_num, fail_num, skip_num

    # get code verion of test image
    def get_code_version(self):
        version = "NA"
        for line in self.load_test_log():
            if re.search("Latest Code Version is:|Commit:", line):
                version = re.findall("Latest Code Version is: (\d+)", line)
                if not version:
                    version = re.findall("Commit: ([0-9a-z]{8})", line)
                    version = version[0]
        return version

    # get sut configuration info
    def get_sut_config(self):
        sut_config = "NA"
        for line in self.load_test_log():
            if re.search("SUT Configuration:", line):
                sut_config = re.findall("SUT Configuration:(.+)", line)
                sut_config = sut_config[0]
        return sut_config

    # get sut project info
    def get_proj_name(self):
        proj = "NA"
        for line in self.load_test_log():
            if re.search("Test Project:", line):
                proj = re.findall("Test Project:(.+)", line)
                proj = proj[0]
        return proj

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
        testReport['testConfig'] = self.get_sut_config()
        testReport['testProject'] = self.get_proj_name()
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

    # collect and update test case result for email
    def collect_test_result_email_format(self):
        testReport = {}
        alltcResult = []
        tcResult = {}
        testReport['Version'] = self.get_code_version()
        testReport['All'] = 0
        testReport['Pass'] = self.get_result_count()[0]
        testReport['Fail'] = self.get_result_count()[1]
        testReport['Skip'] = self.get_result_count()[2]
        testReport['Start Time'] = self.get_total_time()[0]
        testReport['Total Time'] = self.get_total_time()[1]
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("<TC\d+><Tittle>.+:Start", line):
                    id = re.findall("(TC\d+)", line)[0]
                    tcResult['Name'] = re.findall("<TC\d+><Tittle>(.+):Start", line)[0]
                    tcResult['Description'] = self.get_des(id)
                    tcResult['Duration'] = self.get_tc_duration(id)
                    tcResult['Result'] = self.get_status(id)
                    alltcResult.append(tcResult.copy())
        testReport['All'] = len(alltcResult)
        testReport['Result'] = alltcResult
        return testReport

    # convert json format (collect_test_result_email_format()) to html
    def gen_email_report(self, template):
        data_html = json2html.convert(self.collect_test_result_email_format())
        data_html = data_html.replace(r'<td>Pass</td>', r'<td><span class="text-navy">Pass</span></td>')
        data_html = data_html.replace(r'<td>Fail</td>', r'<td><span class="text-danger">Fail</span></td>')
        data_html = data_html.replace(r'<td>Skip</td>', r'<td><span class="text-warning">Skip</span></td>')
        old = "ResultDict"
        new = str(data_html)
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
            data = content.replace(old, new)
        return data

    # get list of files to be uploaded
    def get_upload_files(self):
        dir, fi = os.path.split(self.log)
        files = glob.glob(os.path.join(dir, '*.log'))    
        html_report = os.path.join(dir, 'report.html')
        files.append(html_report)
        files_for_upload = []
        for file in files:
            files_for_upload.append("('upload', ('serial.log', " + "open(" + file + ", 'rb')))")
        return files_for_upload

    # post test result to web
    def post_result(self):
        result = self.collect_test_result()

        dir, fi = os.path.split(self.log)
        report_files = [
            # ('upload', ('serial.log', open(os.path.join(dir, 'serial.log'), 'rb'))),
            ('upload', ('test.log', open(os.path.join(dir, 'test.log'), 'rb')))
        ]

        report_params = {'pro_name': result['testProject'], 'conf_name': result['testConfig'], 'ver_name': result['testVersion']}
        report_case = result['testResult']
        cell_list = []
        cell_desc_list = []
        cell_dura_list = []
        cell_res_list = []
        cell_log = []
        for i in range(len(report_case)):
            cell_list.append(report_case[i]['tcName'])
            cell_desc_list.append(report_case[i]['description'])
            cell_dura_list.append(report_case[i]['spendTime'])
            cell_res_list.append(report_case[i]['status'])
            cell_log.append(report_case[i]['log'])

        report_data = {
            "cell": cell_list,
            "cell_desc": cell_desc_list,
            "duration": cell_dura_list,
            "result": cell_res_list,
            "log": cell_log,
            "cell_all": result['testAll'],
            "cell_pass": result['testPass'],
            "cell_fail": result['testFail'],
            "cell_skip": result['testSkip'],
            "begin_time": result['beginTime'],
            "total_time": result['totalTime'],
        }

        resp = requests.post(url='http://192.168.100.162/api/v1/report',
                             params=report_params,
                             data=report_data,
                             files=report_files)
        print(resp)
        return resp
