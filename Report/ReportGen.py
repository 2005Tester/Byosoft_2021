# -*- encoding=utf8 -*-
import re
import time

class ReportGenerator:
    def __init__(self, log):
    #    self.result_template = result_template
    #    self.html_template = html_template
        self.log = log
    """        
        self.testResult = {
            "testResult":[]
            "testVersion":"0",
            "testAll":"0",
            "testPass":"0",
            "testFail":"0",
            "testSkip":"0",
            "beginTime":"0",
            "totalTime":"0"
            }
        self.tcResult = {
            "tcName": "", 
            "description": "Reset BIOS default by F9", 
            "spendTime": "0s", 
            "status": "", 
            "log": []
            } 
    """

    def convert_time(self, str):
        timArr = time.strptime(str, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(timeArr))

    def get_tcids(self):
        tc_ids = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("\[TC\d+\]\[.+]:Start", line):
                    tc_ids.append(re.findall("(TC\d+)", line))
        return tc_ids

    def get_spendtime(self):
        return "60s"


    def get_status(self, tcid):       
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("\[{0}\]\[.+\]:Pass".format(tcid), line):
                    return re.findall("\[{0}\]\[.+\]:(.+)".format(tcid), line)

    def get_log(self):
        return "log"

    def get_tcname(self, str):
        return re.findall("\[TC\d+\]\[(.+)\]:Start", str)[0]

    def get_des(self):
        return "description"

    def collect_test_result(self):
        alltcResult = []
        tcResult = {}
        tc_ids = []
        with open(self.log, 'r') as f:
            for line in f.readlines():
                if re.search("\[TC\d+\]\[.+]:Start", line):
                    id = re.findall("(TC\d+)", line)
                    tcResult['tcName'] = self.get_tcname(line)
                    tcResult['description'] = self.get_des()
                    tcResult['spendTime'] = self.get_spendtime()
                    tcResult['status'] = self.get_status(id)
                    tcResult['log'] = self.get_log()
                    alltcResult.append(tcResult)   
        print(alltcResult)
 

    def write_to_html(self):
        pass