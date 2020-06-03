import re
import json
import common


def update_result(data, id, log):  #data = TestRunInfo, id: test case id, result: pass/fail/skip, read from log, time: test execution time, read from log, log: path of overall log
    result = 'Skip'
    spend_time = '0ms'

    with open (log,'r', encoding = 'utf-8') as f:
        for line in f.readlines():
            s = re.findall('[0-9]+\.[0-9]+s', line)
            if s:
                spend_time = s[0]
            if re.search('OK', line):
                result = 'Pass'
            elif re.search('FAILED', line):
                result = 'Fail' 


    data["testResult"][id]["status"] = result
    data["testResult"][id]["log"].append(log)
    data["testResult"][id]["spendTime"] = spend_time




def update_overview(data):
    test_all = 6
    test_pass = 0
    test_fail = 0
    test_skip = 0
    total_time = 0
    test_name = common.VER_TESTED[-1]

    for testrun in data["testResult"]:
        if testrun["status"] == "Pass":
            test_pass+=1
        elif testrun["status"] == "Fail":  
            test_fail+=1
        elif testrun["status"] == "Skip":
            test_skip+=1     

    data["testAll"] = test_all
    data["testFail"] = test_fail
    data["testSkip"] = test_skip
    data["testPass"] = test_pass
    data["testName"] = test_name

    with open('tmp\\result.json','w') as f:
        json.dump(common.TestRunInfo, f)

def gen_html(template, dst):
    old = "ResultDict"
    new = str(common.TestRunInfo)

    with open (template, 'r', encoding = 'utf-8') as f:
        content = f.read()
        report = content.replace(old, new)
        with open (dst, 'w', encoding = 'utf-8') as new:
            new.write(report)
