import importlib
import logging
import time
import re
import os
from ByoTool.Config import SutConfig
from batf.TcExecutor import TestScope


class ReportGenerator:
    def __init__(self, template, log, report):
        self.template = template
        self.log = log
        self.report = report
        self.all_log = self.load_test_log()  # 所有log列表
        self.tcresult = {}  # 每个case具体内容{'TC401': ['[TC401]Post Information', 'Post Information Test', 'Pass', ['00:04:04'], [[25, 158]]]}
        self.status = {}
        self.start_end_time = {}  # 每个case开始时间结束时间{'TC401': [['2022-10-29 08:48:52'], ['2022-10-29 08:52:56']]}
        self.start_end_log = {}  # 每个caselog开始行数，结束行数{'TC401': [[25], [157]]}
        self.testReport = {'testVersion': 'NA', 'testConfig': 'NA', 'testProject': 'NA'}
        self.pass_num = 0
        self.fail_num = 0
        self.skip_num = 0
        self.msg_pattern = '(?:\[.+\(\s*\d+\)])'
        self.pattern = '(?:\s---|:)'

    def load_test_log(self):
        all_log = []
        with open(self.log, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line and line != '\n':
                    if re.search('<img src=', line) or re.search('<span', line):
                        pass
                    else:
                        line = line.replace('<', '&lt;')
                    all_log.append(line)
        return all_log

    @staticmethod
    def convert_time(time_str):
        time_arr = time.strptime(time_str, r"%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(time_arr))
        return ts

    def get_result(self, all_log):
        for index, line in enumerate(all_log):
            if re.search('&lt;TC\d+>&lt;Tittle>', line):
                tcname = re.findall("&lt;(TC\d+)>&lt;Tittle>(.+):Start", line)
                if tcname:
                    tcname = tcname[0]
                    self.tcresult[tcname[0]] = [tcname[1]]
            if re.search('&lt;TC\d+>&lt;Description>', line):
                description = re.findall("&lt;(TC\d+)>&lt;Description>(.+)", line)
                if description:
                    description = description[0]
                    self.tcresult[description[0]].append(description[1])
            if re.search("&lt;TC\d+>&lt;Result>.+:.+", line):
                status = re.findall("&lt;(TC\d+)>&lt;Result>.+:(.+)", line)[0]
                if status[0] not in self.status.keys():
                    self.status[status[0]] = []
                self.status[status[0]].append(status[1])
            if re.search(f'INFO{self.pattern} &lt;TC\d+>&lt;Tittle>.+:Start', line):
                start_time = re.findall(
                    f'(\d+-\d+-\d+\s\d+:\d+:\d+) {self.msg_pattern}*\s*INFO{self.pattern} &lt;(TC\d+)>&lt;Tittle>.+:Start',
                    line)
                if start_time:
                    start_time = start_time[0]
                    if start_time[1] not in self.start_end_time.keys():
                        self.start_end_time[start_time[1]] = [[], []]
                    self.start_end_time[start_time[1]][0].append(start_time[0])
            if re.search("&lt;TC\d+>&lt;Result>", line):
                end_time = re.findall(
                    f"(\d+-\d+-\d+\s\d+:\d+:\d+) {self.msg_pattern}*\s*INFO{self.pattern}\s&lt;(TC\d+)>", line)
                if end_time:
                    end_time = end_time[0]
                    self.start_end_time[end_time[1]][1].append(end_time[0])
            if re.search("&lt;TC\d+>&lt;Tittle>.+:Start", line):
                tc = re.findall('&lt;(TC\d+)>', line)[0]
                if tc not in self.start_end_log.keys():
                    self.start_end_log[tc] = [[], []]
                self.start_end_log[tc][0].append(index)
            if re.search("&lt;(TC\d+)>&lt;Result>.+:.+", line):
                tc = re.findall('&lt;(TC\d+)>', line)[0]
                self.start_end_log[tc][1].append(index)
            if re.search("Byosoft Automation Test Framework Version|Commit:", line):
                version = re.findall("Byosoft Automation Test Framework Version ([\d.]+)", line)
                if version:
                    self.testReport['testVersion'] = version[0]
            if re.search("SUT Configuration:", line):
                sut_config = re.findall("SUT Configuration:(.+)", line)[0]
                self.testReport['testConfig'] = sut_config
            if re.search("Test Project:", line):
                proj = re.findall("Test Project:(.+)", line)[0]
                self.testReport['testProject'] = proj
            if re.search(r"&lt;TC\d+>&lt;Result>.+:Pass", line):
                self.pass_num += 1
            if re.search(r"&lt;TC\d+>&lt;Result>.+:Fail", line):
                self.fail_num += 1
            if re.search(r"&lt;TC\d+>&lt;Result>.+:Skip", line):
                self.skip_num += 1

    def get_status(self):
        for key, value in self.status.items():
            self.tcresult[key].append(value)

    # 每个case花费时间
    def get_spent_time(self):
        for key, value in self.start_end_time.items():
            duration_list = []
            for index in range(len(value[0])):
                if value[1] and value[1][index]:
                    duration = self.convert_time(value[1][index]) - self.convert_time(value[0][index])
                    m, s = divmod(duration, 60)
                    h, m = divmod(m, 60)
                    duration = "%02d:%02d:%02d" % (h, m, s)
                else:
                    duration = '00:00:00'
                duration_list.append(duration)
            self.tcresult[key].append(duration_list)

    # 每个case开始，结束位置索引
    def get_log(self):
        for key, value in self.start_end_log.items():
            log_list = []
            for index in range(len(value[0])):
                if value[1] and value[1][index]:
                    log_list.append([value[0][index], value[1][index] + 1])
                else:
                    log_list.append([value[0][index], value[0][index] + 1])
            self.tcresult[key].append(log_list)

    def get_total_time(self):
        start_time = re.findall(
            f"(\d+-\d+-\d+\s\d+:\d+:\d+)\s{self.msg_pattern}*\s*(?:INFO|DEBUG|ERROR){self.pattern}\sByosoft Automation",
            self.all_log[0])[0]
        end_time = re.findall(f"(\d+-\d+-\d+\s\d+:\d+:\d+)\s{self.msg_pattern}*\s*(?:INFO|DEBUG|ERROR){self.pattern}\s",
                              self.all_log[-1])[0]
        total_time = self.convert_time(end_time) - self.convert_time(start_time)
        m, s = divmod(total_time, 60)
        h, m = divmod(m, 60)
        total_time = "%02d:%02d:%02d" % (h, m, s)
        return start_time, total_time

    def get_alltcresult(self):
        alltcresult = []
        for key, value in self.tcresult.items():
            if len(value) == 5 and len(value[2]) == len(value[3]):
                for index in range(len(value[3])):
                    testresult = {}
                    testresult['tcName'] = value[0]
                    testresult['description'] = value[1]
                    testresult['spendTime'] = value[3][index]
                    testresult['status'] = value[2][index]
                    testresult['log'] = self.all_log[value[4][index][0]:value[4][index][1]]
                    alltcresult.append(testresult)
        try:
            alltcresult.sort(key=lambda x: re.findall('\d+-\d+-\d+ \d+:\d+:\d+', x['log'][0])[0])
        except:
            pass
        return alltcresult

    def get_testReport(self):
        alltcresult = self.get_alltcresult()
        total_time = self.get_total_time()
        self.testReport['testResult'] = alltcresult
        self.testReport['testAll'] = len(alltcresult)
        self.testReport['testPass'] = self.pass_num
        self.testReport['testFail'] = self.fail_num
        self.testReport['testSkip'] = self.skip_num
        self.testReport['beginTime'] = total_time[0]
        self.testReport['totalTime'] = total_time[1]

    def write_to_html(self):
        self.get_result(self.all_log)
        self.get_status()
        self.get_spent_time()
        self.get_log()
        self.get_testReport()

        old = "ResultDict"
        new = str(self.testReport)
        dst = self.report

        with open(self.template, 'r', encoding='utf-8') as f:
            content = f.read()
            data = content.replace(old, new)
            with open(dst, 'w', encoding='utf-8') as new:
                new.write(data)


def gen_report():
    template = SutConfig.Env.REPORT_TEMPLATE
    log_dir = SutConfig.Env.LOG_DIR
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"),
                             os.path.join(log_dir, "Testreport.html"))
    report.write_to_html()


class TestcaseScope(TestScope):
    def __init__(self, csv_file, execution_type):
        super().__init__(csv_file, execution_type)

    def _check_case(self, file_name, func_name):
        module_path = '{0}\\TestCase\\'.format(self.project) + file_name + '.py'
        if file_name and os.path.exists(module_path):
            with open(module_path, 'r', encoding='utf-8') as py:
                if re.search(f'def\s+{func_name.split("(")[0]}', py.read()):
                    return True
                else:
                    logging.error("Check fail: {0}.{1}".format(file_name, func_name))
        else:
            logging.error("Check fail: {0}.{1}".format(file_name, func_name))

    def run_test(self, category):
        TC_GROUP = ['default', 'os', 'legacy', 'equip', 'fulldebug']
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
                    parameter_dict = {}
                    for i in para.split(','):
                        key, value = i.split('=')
                        key = key.strip()
                        value = value.strip()
                        if key.strip() and value.strip():
                            if re.search('"', value) or re.search("'", value):
                                value = value.replace("'", '').replace('"', '')
                            else:
                                if all(m in '0123456789' for m in value):
                                    value = int(value)
                            parameter_dict[key.strip()] = value
                    func(**parameter_dict)
            except Exception as e:
                logging.error("Failed to execute test case: {0}.{1}".format(module, case))
                logging.error(e)
            try:
                gen_report()
            except Exception as e:
                logging.error('Failed to create report')
                logging.error(e)
