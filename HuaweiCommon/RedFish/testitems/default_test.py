import logging

import pandas
import re
from HuaweiCommon.RedFish.commlibs.commtools import read_default_values, option_value_index_map, reboot_to_os
from batf.Common.RedfishLib import Redfish
from HuaweiCommon.RedFish import config as cfg
from copy import deepcopy


"""
Redfish默认值测试
1， unitool读取默认值
2， redfish读registry的默认值
3， 比较二者是否一样
4， 修改几个值
5， 重启检查是否改成功
6， redfish POST恢复默认
7， 重启检查是否全部恢复默认

"""


def redfish_default_value_test(ssh_bmc, unitool):
    rfish = Redfish(cfg.bmc_ip, cfg.bmc_user, cfg.bmc_pw)
    var_data = rfish.Attributes()
    for index, att in enumerate(var_data):
        if var_data[index].get("Value"):
            var_data[index]["Value"] = [val["ValueName"] for val in att["Value"]]
    var_pd = pandas.DataFrame(var_data).set_index("AttributeName")
    var_list = [n.get("AttributeName") for n in rfish.Attributes()]
    reboot_to_os(ssh_bmc)
    val_map = option_value_index_map(base_xlsx=cfg.baseline_xlsx)
    val_idx = read_default_values(unitool, var_list)
    default_value = {}
    for var_name in var_list:
        uni_name = "".join(re.findall("(.*?)\[", var_name)) if ("[0]" in var_name) else var_name
        if var_pd.loc[var_name, "Type"] == "Enumeration":
            key_valid = val_map.get(uni_name)
            if isinstance(key_valid, dict):
                rfish_default = str(var_pd.loc[var_name, "DefaultValue"])
                uni_rd_val = val_idx.get(uni_name)
                uni_read_default = key_valid.get(uni_rd_val)
                default_value[uni_name] = uni_read_default
                if uni_read_default != rfish_default:
                    logging.info(f'[{var_name}] Default: registry="{rfish_default}" | read="{uni_read_default}" | dic -> {key_valid} | {uni_rd_val} | {uni_read_default}"')
        if var_pd.loc[var_name, "Type"] == "Integer":
            default_value[uni_name] = val_idx.get(uni_name)


def rfish_post_load_default_test(ssh_bmc, unitool):
    pick_setup = {
        "UsbBoot": 0,
        "WakeOnPME": 1,
        "AcpiApicPolicy": 0,
        "FDMSupport": 0,
        "SataPort": 0,
        "sSataPort": 0,
        "PerformanceTuningMode": 0,
        "VTdSupport": 0,
        "ADDDCEn": 1,
        "ActiveCpuCores": 4,
        "ProcessorHyperThreadingDisable": 1,
        "UFSDisable": 1,
        "ProcessorEistEnable": 0,
        "C6Enable": 1,
        "IrqThreshold": 0,
        "EnableBiosSsaRMT": 1,
        "pprType": 0,
        "BMCWDTEnable": 1,
    }
    reboot_to_os(ssh_bmc)
    pick_setup_default = deepcopy(pick_setup)
    val_default = unitool.read(*pick_setup)  # read default
    for option in pick_setup:
        pick_setup_default[option] = val_default.get(option)
    unitool.write(**pick_setup)  # config modify
    reboot_to_os(ssh_bmc)
    val_modify = unitool.read(*pick_setup)  # check modify
    for option in pick_setup:
        if val_modify.get(option) != str(pick_setup.get(option)):
            logging.info(f"{option} set config failed")
    rfish = Redfish(cfg.bmc_ip, cfg.bmc_user, cfg.bmc_pw)
    rfish.bios_load_default()
    reboot_to_os(ssh_bmc)
    val_after_post = unitool.read(*pick_setup)
    for option in pick_setup_default:
        if val_after_post.get(option) != pick_setup_default.get(option):
            logging.info(f"{option} don't load default after post performed")
