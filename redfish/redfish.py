import requests
import json
import time
import os
import datetime
import random
from sys import argv
import logger
import updatebios
import config
import sut
import testcase

log = logger.Logger(config.LOG_FILE, level="info")
requests.packages.urllib3.disable_warnings()


def load_test_status(testcase_file):
    status_file = testcase_file + ".status"
    if not os.path.exists(status_file):
        with open(status_file, 'w') as f:
            json.dump(config.INIT_STATUS, f, indent=1)
        
    with open(status_file,'r') as f:
        status = json.load(f)
    log.logger.info("Complted: " + str(len(status["Completed"])))
    log.logger.info("Error: " + str(len(status["Error"])))
    log.logger.info("Passed: " + str(len(status["Passed"])))
    log.logger.info("Failed: " + str(len(status["Failed"])))
    log.logger.info("Load test status from %s" % status_file)
    return status


def update_test_status(test_status, status_file):
    with open(status_file, 'w') as f:
        json.dump(test_status, f, indent=1)


# 遍历registry.json, 找到所有无联动关系的选项所支持的value
def gen_payload_list():
    payload_list = []
    all_options = testcase.get_all_varnames()
    dep_options = testcase.get_varnames_dep()
    non_dep_options = list(set(all_options)-set(dep_options))
    for option in non_dep_options:
        values = testcase.supported_value(option)
        for value in values:
            payload = {"Attributes": {option: value}}
            payload_list.append(payload)
    return payload_list


def registry_file_value_test():
    log.logger.info("-"*60)
    log.logger.info("Testing all supported values for non dependency options")
    errors = []
    payloads = gen_payload_list()
    for payload in payloads:
        key = list(payload["Attributes"].keys())[0]
        value = payload["Attributes"][key]
        log.logger.info("%s : %s" %(str(key), str(value)))
        payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" % (key, value)
        res = sut.patch_single_payload(payload, config.PATCH_URL).decode('utf-8')
        res = json.loads(res)
        if 'error' in res:
            errors.append(payload)
            log.logger.info("_"*60)
            log.logger.info(payload)
            log.logger.info(res['error'])
            log.logger.info("_"*60)
    log.logger.info("Errors: %d" % len(errors))
           

def test_registry_file(baseline):
    log.logger.info("Test case 1: compare registery.json with %s" % baseline)
    exclude = ['', 'NA', '\n']
    baseline_lst = []
    with open(baseline, 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if line not in exclude:
                baseline_lst.append(line)
    registry_lst = testcase.get_all_varnames()
    for option in baseline_lst:
        if option not in registry_lst:
            log.logger.info(option + ": missed in registry.json.")
    for option in registry_lst:
        if option not in baseline_lst:
            log.logger.info(option + ": not listed in setup baseline xlsx.")
    log.logger.info("-"*60)
    log.logger.info("Test case 2: Check whetehr all items in dependencies are also in attributes")
    reg = testcase.load_registry_file()
    dep_list = reg["RegistryEntries"]["Dependencies"]
    map_from_list = []
    map_to_list = []
    for dep in dep_list:
        map_to = dep["Dependency"]["MapToAttribute"]
        if map_to not in map_to_list:
            map_to_list.append(dep["Dependency"]["MapToAttribute"])
    log.logger.info("Checking MapToAttribute list...")
    for setup in map_to_list:
        if setup not in registry_lst:
            log.logger.info("[MapToAttribute]: %s is not supported by redfish" % setup)

    for dep in dep_list:
        for i in range(0, len(dep["Dependency"]["MapFrom"])):
            map_from = dep["Dependency"]["MapFrom"][i]["MapFromAttribute"]
            if map_from not in map_from_list:
                map_from_list.append(dep["Dependency"]["MapFrom"][i]["MapFromAttribute"])
    log.logger.info("Checking map from list...")
    for setup in map_from_list:
        if setup not in registry_lst:
            log.logger.info("[MapFromAttribute]: %s is not supported by redfish" % setup)


def gen_dep_tc():
    log.logger.info("-"*60)
    log.logger.info("Generateing dependency test cases...")
    dependency_options = {}
    multi_dep = []
    # 生成有依赖关系的dict
    registry = testcase.load_registry_file()
    dep_list = registry["RegistryEntries"]["Dependencies"]
    for item in dep_list:
        for i in item["Dependency"]["MapFrom"]:
            if i["MapFromAttribute"] not in dependency_options:
                dependency_options[(i["MapFromAttribute"])] = []
    # 把有依赖的选项写入列表
    for key in dependency_options:
        for dep in dep_list:
            if (dep["DependencyFor"] == key) and (dep["Dependency"]["MapToAttribute"] not in dependency_options[key]):
                dependency_options[key].append(dep["Dependency"]["MapToAttribute"])
    # log.logger.info(dependency_options)
    with open("dep_overview.json", "w") as f:
        json.dump(dependency_options, f, indent=1)

    # 检查是否有多层依赖.
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
            with open(file_name, 'w') as f:
                json.dump(tc_dep, f, indent=1)
    log.logger.info(multi_dep)
    log.logger.info("-"*60)


def gen_nondep_tc(testcase_file):
    dependency_options = testcase.get_varnames_dep()
    with open(testcase_file, "r") as fp:
        allcase = json.load(fp)
    alloptions = list(allcase["Attributes"].keys())
    for key in alloptions:
        if key in dependency_options:
            allcase["Attributes"].pop(key)
            print("remove: " + key)
    tc_file = testcase_file.split(".")[0] + "remove_dep.json"
    with open(tc_file, "w") as fp:
        json.dump(allcase, fp, indent=1)
    return tc_file


def change_value(testcase_file):
    with open(testcase_file, 'r') as fp:
        testscope = json.load(fp)
    for key in testscope["Attributes"]:
        values = testcase.supported_value(key)
        if len(values) == 1:
            pass
        else:
            values.remove(testscope["Attributes"][key])
            desired_value = random.choice(values)
            testscope["Attributes"][key] = desired_value
        with open(testcase_file, 'w') as fp:
            json.dump(testscope, fp, indent=1)
   

def get_setup_path(setupname):
    registry = testcase.load_registry_file()
    for item in registry["RegistryEntries"]["Attributes"]:
        if item["AttributeName"] == setupname:
            return item["MenuPath"]


# 通过registry.json检查testcase json文件里面的setup option的值是否合法
def verify_testcase(testcase_file):
    with open(testcase_file, 'r') as fp:
        testscope = json.loads(json.load(fp))
        # testscope = json.load(fp)
    for setupoption in testscope["Attributes"]:
        try:
            if not testscope["Attributes"][setupoption] in testcase.supported_value(setupoption):
                print(setupoption + ":Value is invalid.")
                print("Supported values: ")
                print(testcase.supported_value(setupoption))
        except Exception as e:
            print(e)


# 比较testcase里面的预期值和实际get到的值
def compare(testcase_file, result):
    failures = []
    passed = []
    with open(testcase_file, 'r') as fp:
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
    print("Passed Setup options: %d" % (len(passed)))
    print("Failed Setup options: %d" % (len(failures)))
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


def run_test(test_case_file):
    # Precheck: 比较test case 和 当前值, 打印改变的选项.
    current_value = json.loads(sut.get(config.GET_URL))
    compare(test_case_file, current_value)
    os.system('pause')
    # patch request 设置 test case中的值
    res = sut.patch_tc_file(test_case_file, config.PATCH_URL).decode('utf-8')
    res = json.loads(res)
    if 'error' in res:
        print(res['error'])
    else:
        print("Patch Successfully")

        sut.rebootsut()
        result = sut.get(config.GET_URL)
        result = json.loads(result)
        compare(test_case_file, result)


def run_test_one_by_one(payload):
    current_all = json.loads(sut.get(config.GET_URL))
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

    res = sut.patch_single_payload(payload, config.PATCH_URL).decode('utf-8')
    res = json.loads(res)
    if 'error' in res:
        log.logger.info(res['error'])
        tc_result = "Error"
        log.logger.info('-'*60)
    else:
        log.logger.info("Patch Successfully")
        sut.rebootsut()
        try:
            result = json.loads(sut.get(config.GET_URL))
            tc_result = compare_one(payload, result)
        except Exception as e:
            log.logger.error(e)
            tc_result = "Error"
    return tc_result


def auto_test(testcase_file):
    tc_executed = 0
    log.logger.info("*"*60)
    log.logger.info("Start test with %s" % testcase_file)
    log.logger.info("*"*60)
    test_status = load_test_status(testcase_file)
    payloads = testcase.load(testcase_file)
    for key in payloads["Attributes"]:
        if key not in test_status["Completed"]:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(payloads["Attributes"][key], int):
                payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": %d \r\n    }\r\n}" % (key, payloads["Attributes"][key])
            else:
                payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" % (key, payloads["Attributes"][key])
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
            tc_executed += 1
    if tc_executed == 0:
        log.logger.info("Test for %s is already done." % testcase_file)
        return True


def auto_test_dir(tc_dir):
    tc_file_list = os.listdir(tc_dir)
    for tc_file in tc_file_list:
        if tc_file.split(".")[-1] == 'json':
            iscomplete = auto_test(os.path.join(tc_dir, tc_file))
            log.logger.info("Test completed for %s" % tc_file)
            log.logger.info("#"*60)
            if not iscomplete:
                updatebios.perform_update(config.BIOS)
                log.logger.info("Rebooting SUT, test will continue in 5 minutes")
                time.sleep(500)
        else:
            print("%s is not a json file, skip test" % tc_file)


if __name__ == "__main__":
    if len(argv) == 2:
        if argv[1] == "clenup":
            log.logger.info("Function Not ready yet, INTENTION IS TO clenup status and log file")
        elif argv[1] == "gen-dep-tc":
            log.logger.info("generating dependency test case")
            gen_dep_tc()
        elif argv[1] == "valuetest":
            registry_file_value_test()

        elif argv[1] == "gen-non-dep-tc":
            log.logger.info("generating non-dependency test case")
            change_value(gen_nondep_tc("7998.json"))
        elif argv[1] == "checkregistry":
            log.logger.info("Testing registry file...")
            test_registry_file(".\\baseline\\baseline_0716_1400.txt")
        elif os.path.isfile(argv[1]):
            log.logger.info("Run test for %s" % argv[1])
            auto_test(argv[1])
        elif os.path.isdir(argv[1]):
            log.logger.info("Run multiple files in directory %s" % argv[1])
            auto_test_dir(argv[1])
        else:
            print(config.help_msg)
    else:
        print(config.help_msg)

