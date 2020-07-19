# -*- encoding=utf8 -*-
import json
from collections import OrderedDict
import config


# 从 json 文件加载所有的选项, 返回payloads字典
def load(tc_file):
    with open(tc_file, 'r') as f:
        payloads = json.load(f, object_pairs_hook=OrderedDict)
        if not isinstance(payloads, dict):
            payloads = json.loads(payloads, object_pairs_hook=OrderedDict)
        return payloads


# 读取registry.json，返回registry字典
def load_registry_file():
    with open(config.REGISTRY_FILE, 'r') as fp:
        registry = json.load(fp)
    return registry


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
    registry = load_registry_file()
    dep_list = registry["RegistryEntries"]["Dependencies"]
    for item in dep_list:
        if item["Dependency"]["MapToAttribute"] not in varnames_dep:
            varnames_dep.append(item["Dependency"]["MapToAttribute"])
        elif item["DependencyFor"] not in varnames_dep:
            varnames_dep.append(item["DependencyFor"])
    return varnames_dep


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

