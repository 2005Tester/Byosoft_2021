import requests
import json
import paramiko
import time
import re
import os
import copy
import subprocess
import datetime
import random
from collections import OrderedDict
from sys import argv
import logger
import updatebios

sut = '192.168.2.100'
port = '22'
username = 'Administrator'
password = 'Admin@9000'

BIOS = "HY5V016_candidate1.bin"
REGISTRY_FILE = ".\\baseline\\registry.json"
GET_URL = "https://192.168.2.100/redfish/v1/Systems/1/Bios/"
PATCH_URL = "https://192.168.2.100/redfish/v1/Systems/1/Bios/Settings/"

INIT_STATUS = {"Completed": [],"Passed": [],"Error": [],"Failed": []}

PING_CMD = 'ping 192.168.100.178'
LOG_FILE = "testlog.txt"

help_msg = """
Usage: 
python redfish.py [xxx.json] --Patch and verify all the setup options defined in xxx.json
python redfish.py [directoryname] --Find all the json files in specified directory, and run all the tests in those json files
python redfish.py [checkregistry] --check whether registry.json and setup baseline is aligned
python redfish.py [init]     --cleanup teststatus
"""

log = logger.Logger(LOG_FILE, level = "info")

requests.packages.urllib3.disable_warnings()

def load_testcase(testcase_file):
    with open (testcase_file, 'r') as f:
        payloads = json.load(f,object_pairs_hook=OrderedDict)
        if not isinstance(payloads,dict):
            payloads = json.loads(payloads,object_pairs_hook=OrderedDict)
        return(payloads)


def load_test_status(testcase_file):
    status_file = testcase_file + ".status"
    if not os.path.exists(status_file):
        with open(status_file,'w') as f:
            json.dump(INIT_STATUS, f, indent=1)
        
    with open(status_file,'r') as f:
        status = json.load(f)
    log.logger.info("Complted: " + str(len(status["Completed"])))
    log.logger.info("Error: " + str(len(status["Error"])))
    log.logger.info("Passed: " + str(len(status["Passed"])))
    log.logger.info("Failed: " + str(len(status["Failed"])))
    log.logger.info("Load test status from %s" %status_file)
    return status

def update_test_status(test_status,status_file):
    with open(status_file,'w') as f:
        json.dump(test_status, f, indent=1)


def ping_sut():
    cmd_update_bios = r'python C:\UpdateTool\updatebios.py ' + BIOS
    start_time = time.time()
    while True:        
        p = subprocess.Popen(args=PING_CMD,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (stdoutput,erroutput) = p.communicate() 
        output = stdoutput.decode()
        now = time.time()
        time_spent = (now-start_time)
        if output.find("TTL=") >=0:
            print("SUT is online now")
            break
        if time_spent >900:
            print("Lost SUT for %s seconds, refresh BIOS image" %(time_spent))
            try:
                updatebios.perform_update(BIOS)
                time.sleep(300)
                start_time = time.time()
            except Exception as e:
                print(e)

def get_all_supported_options():
    all_options = []
    with open (REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    for item in registry["RegistryEntries"]["Attributes"]:
        all_options.append(item["AttributeName"])
    return all_options

def test_registry_file(baseline):
    exclude = ['','NA','\n']
    baseline_lst = []
    with open (baseline, 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if not line in exclude:
                baseline_lst.append(line)
    #print (baseline_lst)
    registry_lst = get_all_supported_options()
    
    for option in baseline_lst:
        if not option in registry_lst:
            log.logger.info(option + ": missed in registry.json.")
    for option in registry_lst:
        if not option in baseline_lst:
            log.logger.info(option + ": not listed in setup baseline xlsx.")


def gen_dep_tc():
    dependency_options = {}
    multi_dep = []
    # 生成有依赖关系的dict
    with open (REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    dep_list = registry["RegistryEntries"]["Dependencies"]
    for item in dep_list:
        for i in item["Dependency"]["MapFrom"]:
            if i["MapFromAttribute"] not in dependency_options:
                dependency_options[(i["MapFromAttribute"])]=[]
    # 把有依赖的选项写入列表
    for key in dependency_options:
        for dep in dep_list:
            if (dep["DependencyFor"] == key) and (dep["Dependency"]["MapToAttribute"] not in dependency_options[key]):
                dependency_options[key].append(dep["Dependency"]["MapToAttribute"])
    print(dependency_options)

    #检查是否有多层依赖.
    for key in dependency_options:
        for opt in dependency_options[key]:
            if (opt in dependency_options) and (opt not in multi_dep):
                multi_dep.append(opt)
    
    # 生成有依赖关系的test case, 导出到tc_dependency.json    
    for key in dependency_options:
        tc_dep = {} 
        tc_dep["Attributes"] = {}
        file_name = 'tc_dep_' + key + '.json'
        tc_dep["Attributes"][key] = ""
        for opt in dependency_options[key]:
            tc_dep["Attributes"][opt] = ""
            with open (file_name, 'w') as f:
                json.dump(tc_dep, f, indent=1)
    print(multi_dep)

def gen_nondep_tc(testcase_file):
    dependency_options = []
    with open (REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    dep_list = registry["RegistryEntries"]["Dependencies"]
    for item in dep_list:
        if item["Dependency"]["MapToAttribute"] not in dependency_options:
            dependency_options.append(item["Dependency"]["MapToAttribute"])
        elif item["DependencyFor"] not in dependency_options:
            dependency_options.append(item["DependencyFor"])
    #print(dependency_options)
    with open (testcase_file, "r") as fp:
        allcase = json.load(fp)
    alloptions = list(allcase["Attributes"].keys())
    for key in alloptions:
        if key in dependency_options:
            allcase["Attributes"].pop(key)
            print("remove: " + key)
    tc_file = testcase_file.split(".")[0] + "remove_dep.json"
    with open (tc_file,"w") as fp:
        json.dump(allcase, fp, indent=1)
    return tc_file


def change_value(testcase_file):
    with open (testcase_file, 'r') as fp:
        testscope = json.load(fp)
    for key in testscope["Attributes"]:
        values = supported_value(key)
        if len(values) == 1:
            pass
        else:
            values.remove(testscope["Attributes"][key])
            desired_value = random.choice(values)
            testscope["Attributes"][key] = desired_value
        with open ("changes.json", 'w') as fp:
            json.dump(testscope, fp, indent=1)
   

def get_setup_path(setupname):
    with open (REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    for item in registry["RegistryEntries"]["Attributes"]:
        if item["AttributeName"] == setupname:
            return(item["MenuPath"])

# 通过registry.json检查testcase json文件里面的setup option的值是否合法
def verify_testcase(testcase_file):
    with open (testcase_file, 'r') as fp:
        testscope = json.loads(json.load(fp))
        #testscope = json.load(fp)
    for setupoption in testscope["Attributes"]:
    #    print(supported_value(setupoption))
        try:
            if not testscope["Attributes"][setupoption] in supported_value(setupoption):
                print(setupoption + ":Value is invalid.")
                print("Supported values: " )
                print(supported_value(setupoption))
        except Exception as e:
            print(e)


# 获取registry里面每个setup option支持的值
def supported_value(setupname):
    supported_setup = []
    with open (REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    for item in registry["RegistryEntries"]["Attributes"]:
        supported_setup.append(item["AttributeName"])
    if setupname in supported_setup:
        for item in registry["RegistryEntries"]["Attributes"]:
            if item["AttributeName"] == setupname:
                try:
                    return [i["ValueName"] for i in item["Value"]]
                except Exception as e:
                #    print(e)
                #    print(setupname)
                    return (["Value is Null"])
    else:
        print(setupname + " is not supported.")

    
# 发送GET request 获取当前setup选项的值
def get(url):
    headers = {
    'If-Match': 'W/"492eb2b8"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify = False)
    #result = response.text.encode('utf8')
    result = response.text
    response.close()
    #print(result)
    #with open ('result.json', 'w') as fp:
    #    json.dump(result, fp)
    return result

# 发送PATCH request 设置 testcase里面的值 
def patch(testcase_file, url):
    with open(testcase_file,'r') as fp:
        payload = json.load(fp)
    #payload = "{\r\n    \"Attributes\": {\r\n     \"RdtCatOpportunisticTuning\": \"Tuned 0x600\" \r\n    }\r\n}"
    headers = {
    'If-Match': 'W/"584db857"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify = False)
    Etag = response.headers['ETag']
    headers['If-Match'] = Etag

    response = requests.request("PATCH", url, headers=headers, data = payload, verify = False)
    response.close()
    return response.text.encode('utf8')

def patch_one_option(payload, url):
    headers = {
    'If-Match': 'W/"584db857"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify = False)
    Etag = response.headers['ETag']
    headers['If-Match'] = Etag

    response = requests.request("PATCH", url, headers=headers, data = payload, verify = False)
    response.close()
    return response.text.encode('utf8')

# 比较testcase里面的预期值和实际get到的值
def compare(testcase_file, result):
    failures = []
    passed = []
    with open (testcase_file, 'r') as fp:
        testscope = json.load(fp)
        testscope = json.loads(testscope)
    for key in testscope["Attributes"]:
        if not testscope["Attributes"][key] == result["Attributes"][key]:
            print(key + " : Failed")
            print(get_setup_path(key))
            failures.append(key)
        else:
            print(key + " : Pass")
            print(get_setup_path(key))
            passed.append(key)
    print('-'*60)
    print("Passed Setup options: %d" %(len(passed)) )
    print("Failed Setup options: %d" %(len(failures)) )
    print(failures)

def compare_one(payload, result):
    tc = json.loads(payload)
    for key in tc["Attributes"]:
        if not tc["Attributes"][key] == result["Attributes"][key]:
            log.logger.info(key + " : Failed")
            tc_result = "Failed"
        else:
            log.logger.info(key + " : Pass")
            tc_result = "Passed"
    log.logger.info('-'*60)
    return tc_result

def rebootsut():
    cmd_shutdown = 'ipmcset -d powerstate -v 2\n'
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    cmd_confirm = 'Y\n'
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(sut,port,username, password, banner_timeout=150)
    except Exception as e:
        print("Error in connecting SUT...")
        time.sleep(300)
        rebootsut()
        return

    op=s.invoke_shell()
    
    def send_cmd(cmd):
        op.send(cmd)
        time.sleep(5)
        res=op.recv(1024)
        return(res)

    res = send_cmd(cmd_shutdown)  #shutdown SUT
    if re.search("Do you want to continue", res.decode('utf-8')):
        res = send_cmd(cmd_confirm) #confirm shutdown
        if re.search("Control fru0 forced power off successfully", res.decode('utf-8')):
            print("Shutdown command sent to SUT.")
            time.sleep(10)
            res = send_cmd(cmd_power_on)
            if re.search("Do you want to continue", res.decode('utf-8')):
                res = send_cmd(cmd_confirm) #confirm power on
                if re.search("Control fru0 power on successfully", res.decode('utf-8')):
                    print("Power on command sent to SUT.")
                    send_cmd(cmd_fan_manual_mode) #tune fan speed
                    send_cmd(cmd_fan_40)
                    print("Booting SUT...")
                    #os.system('pause')
                    time.sleep(30)
                    ping_sut()
    op.close()
    s.close()
    return
                    

def run_test(test_Case_file):

    # Precheck: 比较test case 和 当前值, 打印改变的选项.
    current_value = json.loads(get(GET_URL))
    compare(test_Case_file,current_value)
    os.system('pause')
    # patch request 设置 test case中的值
    res = patch(test_Case_file,PATCH_URL).decode('utf-8')
    res = json.loads(res)
    if 'error' in res:
        print(res['error'])
    else:
        print("Patch Successfully")

        rebootsut()
        result = get(GET_URL)
        result = json.loads(result)
        compare(test_Case_file,result)

def run_test_one_by_one(payload):
    current_all = json.loads(get(GET_URL))
    test_item = json.loads(payload)
    try:
        for key in test_item["Attributes"]:
            log.logger.info(key + " default value: " + str(current_all["Attributes"][key]))
            log.logger.info("Path: " + get_setup_path(key))
    except Exception as e:
        log.logger.error(e)
        log.logger.error("-"*60)
        tc_result = "Error"
        return tc_result

    res = patch_one_option(payload,PATCH_URL).decode('utf-8')
    res = json.loads(res)
    if 'error' in res:
        log.logger.info(res['error'])
        tc_result = "Error"
        log.logger.info('-'*60)
    else:
        log.logger.info("Patch Successfully")
        rebootsut()
        result = json.loads(get(GET_URL))
        tc_result = compare_one(payload,result)
    return tc_result

def auto_test(testcase_file):
    tc_executed = 0
    log.logger.info("*"*60)
    log.logger.info("Start test with %s" %(testcase_file))
    log.logger.info("*"*60)
    test_status = load_test_status(testcase_file)
    payloads = load_testcase(testcase_file)
    for key in payloads["Attributes"]:
        if not key in test_status["Completed"]:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #print(timestamp)
            payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" %(key, payloads["Attributes"][key])
            log.logger.info(key + " Value to set: " + str(payloads["Attributes"][key]))
            tc_result = run_test_one_by_one(payload)
            test_status["Completed"].append(key)
            if tc_result == "Error":
                test_status["Error"].append(key)
            if tc_result == "Passed":
                test_status["Passed"].append(key)
            if tc_result == "Failed":
                test_status["Failed"].append(key)
            update_test_status(test_status, (testcase_file + '.status'))
            tc_executed +=1
    if tc_executed == 0:
        log.logger.info("Test for %s is already done." %(testcase_file))
        return True

def auto_test_dir(dir):
    tc_file_list = os.listdir(dir)
    for tc_file in tc_file_list:
        if tc_file.split(".")[-1] == 'json':
            iscomplete = auto_test(os.path.join(dir,tc_file))
            log.logger.info("Test completed for %s" % tc_file)
            log.logger.info("#"*60)
            if not iscomplete:
                updatebios.perform_update(BIOS)
                log.logger.info("Rebooting SUT, test will continue in 5 minutes")
                time.sleep(500)
        else:
            print("%s is not a json file, skip test" %tc_file)

if __name__ == "__main__":

    if len(argv)==2:
        if argv[1] == "clenup":
            log.logger.info("Function Not ready yet, INTENTION IS TO clenup status and log file")
        elif argv[1] == "gendeptc":
            log.logger.info("generating dependency test case")
            gen_dep_tc()
        elif argv[1] == "gennondeptc":
            log.logger.info("generating non-dependency test case")
            change_value(gen_nondep_tc("7972.json"))
        elif argv[1] == "checkregistry":
            log.logger.info("Testing registry file...")
            test_registry_file("baseline_0716_1400.txt")
        elif os.path.isfile(argv[1]):
            log.logger.info("Run test for %s" % argv[1])
            auto_test(argv[1])
        elif os.path.isdir(argv[1]):
            log.logger.info("Run multiple files in directory %s" % argv[1])
            auto_test_dir(argv[1])
        else:
            print(help_msg)
    else:
        print(help_msg)

#    verify_testcase("V15_Default_all.json")
#    res = patch("tc_debug.json",PATCH_URL).decode('utf-8')
#    print(res)
#    run_test(".\\hang1\\1sthalf.json")
#    auto_test(".\\dep\\tc_dep_PciePortDisable_10.json")
#    ping_sut()
#    change_value(".\\gen_case\\remove_dep.json")


#    change_value("remove_dep.json")
    
#    res = patch("V15_Default_Dis2En.json",PATCH_URL).decode('utf-8')
#    print(res)





   
