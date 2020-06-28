import re
import json
import common


def update_result(data, id, log):  #data = TestRunInfo, id: test case id, result: pass/fail/skip, read from log, time: test execution time, read from log, log: path of overall log
    result = 'Skip'
    spend_time = '0s'

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
    data["testResult"][id]["log"].clear()
    data["testResult"][id]["log"].append(log)
    data["testResult"][id]["spendTime"] = spend_time




def update_overview(data):
#    test_all = 7
    test_pass = 0
    test_fail = 0
    test_skip = 0
    if not common.VER_TESTED:
        test_name = "NA"
    else:
        test_name = common.VER_TESTED[-1]
    data["totalTime"] = 0

    # update overall pass/fail number
    for tc in data["testResult"]:
        if tc["status"] == "Pass":
            test_pass+=1
        elif tc["status"] == "Fail":  
            test_fail+=1
        elif tc["status"] == "Skip":
            test_skip+=1     

    # update total_time
    for tc in data["testResult"]:
        t = float(tc['spendTime'][:-1])
        data["totalTime"] = data["totalTime"] + t

#    data["testAll"] = test_all
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
