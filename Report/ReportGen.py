# -*- encoding=utf8 -*-
import re
import time

class ReportGenerator:
    def __init__(self, log, report):
    #    self.result_template = result_template
        self.report = report
        self.log = log


    def load_test_log(self):
        log_lines = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                log_lines.append(line)
        return log_lines


    def convert_time(self, str):
        time_arr = time.strptime(str, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(time_arr))
        return ts


    def get_tcids(self):
        tc_ids = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("\[TC\d+\]\[.+]:Start", line):
                    tc_ids.append(re.findall("(TC\d+)", line))
        return tc_ids


    def get_tc_duration(self, id):
        for line in self.load_test_log():
            if re.search("\[{0}\].+:Start".format(id), line):
                start_time = re.findall("(.+)\sINFO.+:Start", line)[0]
            if re.search("\[{0}\]\[.+\]:Pass|\[{0}\]\[.+\]:Fail|\[{0}\]\[.+\]:Skip".format(id), line):
                end_time = re.findall("(.+)\sINFO.+:[PFS]", line)[0]
        duration = self.convert_time(end_time) - self.convert_time(start_time)
        return duration


    def get_status(self, tcid):
        for line in self.load_test_log():
            if re.search("\[{0}\]\[.+\]:Pass|\[{0}\]\[.+\]:Fail|\[{0}\]\[.+\]:Skip".format(tcid), line):
                return re.findall("\[{0}\]\[.+\]:(.+)".format(tcid), line)[0]


    def get_tc_log(self, tcid):
        log = []
        all_log = self.load_test_log()
        for line in all_log:
            if re.search("\[{0}\]\[.+\]:Start".format(tcid), line):
                start_index = all_log.index(line)
            if re.search("\[{0}\]\[.+\]:Pass|\[{0}\]\[.+\]:Fail|\[{0}\]\[.+\]:Skip".format(tcid), line):
                end_index = all_log.index(line)
        for i in range(start_index, end_index+1):
            log.append(all_log[i])
            
        return log

    

    def get_tcname(self, str):
        return re.findall("\[TC\d+\]\[(.+)\]:Start", str)[0]


    def get_des(self):
        return "description"


    def get_result_count(self):
        pass_num = 0
        fail_num = 0
        skip_num = 0

        for line in self.load_test_log():
            if re.search("\[TC\d+\]\[.+\]:Pass", line):
                pass_num +=1
            if re.search("\[TC\d+\]\[.+\]:Fail", line):
                fail_num +=1
            if re.search("\[TC\d+\]\[.+\]:Skip", line):
                skip_num +=1
        return (pass_num, fail_num, skip_num)

        

    def collect_test_result(self):
        testReport = {}
        alltcResult = []
        tcResult = {}
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("\[TC\d+\]\[.+]:Start", line):
                    id = re.findall("(TC\d+)", line)[0]
                    tcResult['tcName'] = self.get_tcname(line)
                    tcResult['description'] = self.get_des()
                    tcResult['spendTime'] = self.get_tc_duration(id)
                    tcResult['status'] = self.get_status(id)
                    tcResult['log'] = self.get_tc_log(id)
                    alltcResult.append(tcResult.copy())
        testReport['testResult'] = alltcResult
        testReport['testVersion'] = "1234"
        testReport['testAll'] = len(alltcResult)
        testReport['testPass'] = self.get_result_count()[0]
        testReport['testFail'] = self.get_result_count()[1]
        testReport['testSkip'] = self.get_result_count()[2]
        testReport['beginTime'] = "begintime"
        testReport['totalTime'] = "10 min"
        return testReport


    def write_to_html(self):
        old = "ResultDict"
        new = str(self.collect_test_result())
        template = "C:\\autotest\\Report\\template_Moc"
        dst = self.report

        with open (template, 'r', encoding = 'utf-8') as f:
            content = f.read()
            data = content.replace(old, new)
            with open (dst, 'w', encoding = 'utf-8') as new:
                new.write(data)
