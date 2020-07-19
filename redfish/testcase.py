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

