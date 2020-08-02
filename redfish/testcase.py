# -*- encoding=utf8 -*-
import json
import os
import re
import random
from collections import OrderedDict
import config


# 从 json 文件加载所有的选项, 返回payloads字典
def load(tc_file):
    with open(tc_file, 'r') as f:
        payloads = json.load(f, object_pairs_hook=OrderedDict)
        if not isinstance(payloads, dict):
            payloads = json.loads(payloads, object_pairs_hook=OrderedDict)
        return payloads


# 改变testcase 文件中选项的值为非默认（随机）
def change_value(tc_file):
    testscope = load(tc_file)
    for key in testscope:
        values = supported_value(key)
        if len(values) == 1:
            pass
        else:
            values.remove(testscope[key])
            desired_value = random.choice(values)
            testscope[key] = desired_value
        with open(tc_file, 'w') as fp:
            json.dump(testscope, fp, indent=1)


# 读取registry.json，返回registry字典
def load_registry_file():
    with open(config.REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    return registry

def get_hidden_options():
    hidden_options = []
    registry = load_registry_file()
    for item in registry["RegistryEntries"]["Attributes"]:
        if item["Hidden"] == True:
            hidden_options.append(item["AttributeName"])
    return hidden_options


# 获取setup的menpath
def get_setup_path(setupname):
    registry = load_registry_file()
    for var in registry["RegistryEntries"]["Attributes"]:
        if var["AttributeName"] == setupname:
            return var["MenuPath"]


# 读取registry.json中所有AttributeName, 返回varnames list
def get_all_varnames():
    varnames = []
    registry = load_registry_file()
    for item in registry["RegistryEntries"]["Attributes"]:
        varnames.append(item["AttributeName"])
    return varnames


# 从Dependencies 描述里面获取所有有依赖关系的setup选项
def get_varnames_dep():
    varnames_dep = []
    dependency_for = []
    registry = load_registry_file()
    dep_list = registry["RegistryEntries"]["Dependencies"]
    for item in dep_list:
        if item["Dependency"]["MapToAttribute"] not in varnames_dep:
            varnames_dep.append(item["Dependency"]["MapToAttribute"])
        if item["DependencyFor"] not in varnames_dep:
            varnames_dep.append(item["DependencyFor"])
        if item["DependencyFor"] not in dependency_for:
            dependency_for.append(item["DependencyFor"])
    return varnames_dep, dependency_for


# 遍历registry.json, 找到所有无联动关系的选项所支持的value
def gen_payload_list():
    payload_list = []
    all_options = get_all_varnames()
    # dep_options = get_varnames_dep()[0]
    # non_dep_options = list(set(all_options)-set(dep_options))
    for option in all_options:
        values = supported_value(option)
        for value in values:
            payload = {"Attributes": {option: value}}
            payload_list.append(payload)
    return payload_list


# 从HIDDEN_LIST(setup基线文档)中获取所有隐藏的setup选项
def get_hidden_list():
    exclude = ['', 'NA', '\n']
    hidden_lst = []
    with open(config.HIDDEN_LIST, 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if line not in exclude:
                hidden_lst.append(line)
    return hidden_lst


# 从BIOS code base 获取hfr和vrf文件
def get_file_list():
    hfr_vfr_list = []
    for root, directory, files in os.walk(config.BIOS_CODE):
        for filename in files:
            name, suf = os.path.splitext(filename)
            if suf in ['.hfr', '.vfr']:
                hfr_vfr_list.append(os.path.join(root, filename))
    return hfr_vfr_list


# 在VFR和HFR文件中查找给定setup选项, 返回该选项属于哪一类，比如'SOCKET_MEMORY_CONFIGURATION'
def match_setup(setup, file):
    with open(file, "r", encoding='utf-8') as f:
        buf = f.read()
        pat = re.compile(r"=\s+(.+).%s,.*redfish" % setup)
        ret = pat.findall(buf)
    return ret


# 获取所有HFR, VFR中该setup的路径，返回列表
def get_setup_category(setup):
    setup_categories = []
    file_list = get_file_list()
    for hfr_vfr in file_list:
        match = match_setup(setup, hfr_vfr)
        if match:
            for itm in match:
                if itm not in setup_categories:
                    setup_categories.append(itm)
    return setup_categories


# 给定varname，获取registry里面所有支持的值，返回列表
def supported_value(varname):
    all_varnames = get_all_varnames()
    registry = load_registry_file()
    if varname in all_varnames:
        for item in registry["RegistryEntries"]["Attributes"]:  # Attributes list中的每个选项的详细信息
            if item["AttributeName"] == varname:
                try:
                    return [val["ValueName"] for val in item["Value"]]  # val为描述所有支持的value的dict
                except Exception as e:
                    return ["Value is Null"]
    else:
        print(varname + " is not supported.")


# 通过registry.json检查testcase json文件里面的setup option的值是否合法
def verify_testcase(testcase_file):
    with open(testcase_file, 'r') as fp:
        testscope = json.loads(json.load(fp))
        # testscope = json.load(fp)
    for setupoption in testscope["Attributes"]:
        try:
            if not testscope["Attributes"][setupoption] in supported_value(setupoption):
                print(setupoption + ":Value is invalid.")
                print("Supported values: ")
                print(supported_value(setupoption))
        except Exception as e:
            print(e)


def gen_all_tc():
    dep_for = get_varnames_dep()[1]   # 获取所有依赖关系的父选项（DependencyFor）
    allcase = load(config.CURR_SET_JSON)
    alloptions = list(allcase.keys())
    for key in alloptions:
        if key in dep_for:
            allcase.pop(key)
    tc_file = os.path.join(config.TEST_RESULT_DIR, "all.json")
    with open(tc_file, "w") as fp:
        json.dump(allcase, fp, indent=1)
    change_value(tc_file)
    return tc_file

def get_error_details(error_msg):
    msgs = []
    msg_ext_info = error_msg['error']['@Message.ExtendedInfo']
    for i, msg in enumerate(msg_ext_info):
        msgs.append(msg['Message'])
    return msgs

