#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-

import json
import logging
import random
import re
import pandas as pd

from copy import deepcopy
from RedFish.commlibs.commtools import to_excel, reboot_sut
from Common.RedfishLib import Redfish
from RedFish.config import bmc_ip, bmc_user, bmc_pw, TEST_RESULT_DIR

"""
【测试配置】
1. 配置 config 文件
    -   bmc_ip
    -   bmc_user
    -   bmc_pw
    -   COM
2. 进入到Redfish文件夹，运行命令 RedFishTest.py depmain 开始测试
3. 测试完成后Excel报告保存在 config.REPORT_DIR 路径中

【测试流程】
1. Dump Registry文件
2. 以MapFrom列表为索引，整理出每个MapFrom条件，关联的下级MapTo菜单，作为一行
3. 去掉所有的反向关联条件（Hidden=False)
4. 遍历DataFrame的每一行，并尝试PATCH MapFrom 列表
    a.  每次遍历前先通过POST恢复默认
    b.  每次遍历都去检查此菜单是否有多级联动导致不能直接修改的情况，如果有，则让此条件和上级菜单（选择一个可修改的值）一起PATCH
5. 修改完成后重启
6. 重启后检查 MapFrom 的值有没有修改成功
7. 然后检查每一个MapTo的条件，查看是否满足
    a.  CurrentValue的情况：    Value为PATCH的值则认为 pass
    b.  Hidden/ReadOnly=True的情况:    尝试PATCH并PATCH失败则认为 pass
    c.  其他情况:   尝试PATCH并PATCH成功则认为 pass
8.  生成Excel报告
    PASS:   -  MapFrom PATCH成功
            -  重启后检查MapFrom的值符合要求
            -  重启后检查MapTo的值或者属性符合要求
    FAIL:   -  任意一项为Fail
"""


class DepenTest(Redfish):
    def __init__(self, ssh_bmc, serial):
        super(DepenTest, self).__init__(bmc_ip, bmc_user, bmc_pw)
        self.ssh = ssh_bmc
        self.serial = serial
        self.atts_pd = pd.DataFrame()
        self.map_from_pd = pd.DataFrame()
        self.depens = self.Dependencies()
        self.mapto_link = self.mapto_info()
        self.registry_dump(dump_json=True, path=TEST_RESULT_DIR)

    def attributes_info(self, dump: bool = False):
        """ 以AttributeName为索引返回 DataFrame，可选择生成Excel文件用于手动检查 """
        atts = self.Attributes()
        for index, att in enumerate(atts):
            if atts[index].get("Value"):
                atts[index]["Value"] = [val["ValueName"] for val in att["Value"]]
        self.atts_pd = pd.DataFrame(atts).set_index("AttributeName")
        if dump:
            to_excel(self.atts_pd, "AttributesName_所有信息")
        return self.atts_pd

    def depenfor_info(self, dump: bool = False):
        """ 以DependencyFor为索引返回 DataFrame，可选择生成Excel文件用于手动检查 """
        depen_pd = pd.DataFrame(self.depens).set_index("DependencyFor")
        depen_pd["Dependency"] = depen_pd["Dependency"].apply(lambda x: json.dumps(x, indent=4))
        if dump:
            to_excel(depen_pd, "DependencyFor_检索信息")
        return depen_pd

    def mapto_info(self, dump: bool = False):
        """ 以MapToAttribute为索引返回 DataFrame，可选择生成Excel文件用于手动检查 """
        depen_dic = {}
        depen_link = {}  # used for map link in self.mapped_as_unchanged()
        for depen in self.depens:
            map_to_name = depen["Dependency"]["MapToAttribute"]
            for d in depen["Dependency"]["MapFrom"]:
                mt_property = depen["Dependency"]["MapToProperty"]
                mt_value = depen["Dependency"]["MapToValue"]
                mf_name = d["MapFromAttribute"]
                mf_value = d["MapFromValue"]
                if not depen_dic.get(map_to_name):
                    depen_dic[map_to_name] = [depen]
                else:
                    depen_dic[map_to_name].append(depen)
                if (mt_property == "Hidden" or mt_property == "ReadOnly") and mt_value:
                    if not depen_link.get(map_to_name):
                        depen_link.setdefault(map_to_name, {})
                    if not depen_link[map_to_name].get(mf_name):
                        depen_link[map_to_name].setdefault(mf_name, [])
                    depen_link[map_to_name][mf_name].append(mf_value)
        map_to_pd = pd.DataFrame.from_dict(depen_dic, orient="index").applymap(lambda x: json.dumps(x, indent=4))
        if dump:
            to_excel(map_to_pd, "MapToAttribute_检索信息")
        return depen_link

    def mapfrom_info(self, dump: bool = False):
        """ 以MapFrom为索引返回 DataFrame，可选择生成Excel文件用于手动检查 """
        map_from_dic = {}
        deps = deepcopy(self.depens)
        for depen in deps:
            mapf = str(depen["Dependency"]["MapFrom"])  # "[{},{}]"
            depen["Dependency"].pop("MapFrom")
            mapt = depen["Dependency"]  # {}
            if not (mapf in map_from_dic):
                map_from_dic[mapf] = [mapt]  # [{}]
            else:
                map_from_dic[mapf].append(mapt)  # # [{},{}]
        self.map_from_pd = pd.DataFrame.from_dict(map_from_dic, orient="index").reset_index()
        mf_depen_relation = self.map_from_pd
        mf_depen_relation["index"] = mf_depen_relation["index"].apply(eval)
        mf_depen_relation = mf_depen_relation.applymap(lambda x: json.dumps(x, indent=4))
        if dump:
            to_excel(mf_depen_relation, "MapFrom_MapTo_联动关系")
        return self.map_from_pd

    def drop_hidden_false(self, dump: bool = False):
        """ 去除所有 Hidden=false的反向关系 """
        hid_false = re.compile(r"MapToProperty.+Hidden.+MapToValue.+False")
        for column_index, column_data in self.map_from_pd.iteritems():
            for row_index, row_data in column_data.iteritems():
                if hid_false.search(str(row_data)) or (str(row_data) == "None"):
                    self.map_from_pd.loc[row_index, column_index] = None
        self.map_from_pd.dropna(subset=[n for n in range(0, len(self.map_from_pd.columns) - 1)], how="all",
                                inplace=True)
        # self.map_from_pd["index"] = self.map_from_pd["index"].apply(eval)
        self.map_from_pd.reset_index(inplace=True, drop=True)
        mf_hidden_false = self.map_from_pd.applymap(lambda x: json.dumps(x, indent=4))
        if dump:
            to_excel(mf_hidden_false, "MapFrom_去除反向联动信息")
        return self.map_from_pd

    def mapped_as_unchanged(self, mapfrom: list):
        """ 检查选项是否会被关联并且不允许修改 (Hidden=True/ReadOnly=True) """
        result_mapto = True
        for index, mf in enumerate(mapfrom):
            mf_name = mapfrom[index]["MapFromAttribute"]
            for mk in self.mapto_link.keys():
                if mf_name == mk:
                    result_mapto = result_mapto & False
        return not result_mapto

    @staticmethod
    def gen_patch_data(map_from: list):
        """
        生成PATCH的字典
            1. Only one item just return       {key1:value1}
            2. One more items
                MapTerms = AND return all       {key1:value1, key2:value2, ...}
                MapTerms = OR return 1st one    {key1:value1}
        """
        option = {}
        for index, mf in enumerate(map_from):
            mf_key = map_from[index]["MapFromAttribute"]
            mf_value = map_from[index]["MapFromValue"]
            option[mf_key] = mf_value
            if len(map_from) == 1:
                return option
            if map_from[index]["MapTerms"] == "OR":
                return option
        return option

    def not_the_value(self, mf_key, mf_value, mt_key):
        vals = deepcopy(self.atts_pd.loc[mf_key, "Value"])
        mt_link = deepcopy(self.mapto_link[mt_key][mf_key])
        if mf_value in vals:
            vals.remove(mf_value)  # 去掉MapFrom的值
        if len(vals) == 1:
            return random.choice(vals)
        for mk in mt_link:
            if mk in vals:
                vals.remove(mk)  # 去掉被关联且不能改的值
        return random.choice(vals)

    @staticmethod
    def mf_key_value(mapfrom: list):
        """ 根据MapFrom生成字典 {MapFromAttribute：MapFromValue} """
        mf_dic = {}
        for mf in mapfrom:
            mf_dic.update({mf["MapFromAttribute"]: mf["MapFromValue"]})
        return mf_dic

    def gen_data_w_top(self, mapfrom: list):
        """ 当发现 MapFromAttribute 被联动时，找到上级联动一起修改 """
        mf_dic = self.mf_key_value(mapfrom)
        depens = deepcopy(self.depens)
        for depen in depens:
            mapto_name = depen["Dependency"]["MapToAttribute"]
            if mapto_name not in mf_dic.keys():
                continue
            mapto_property = depen["Dependency"]["MapToProperty"]
            mapto_value = depen["Dependency"]["MapToValue"]
            if not ((mapto_property == "Hidden" or mapto_property == "ReadOnly") and mapto_value):
                continue
            for mf in depen["Dependency"]["MapFrom"]:
                key = mf["MapFromAttribute"]
                if key in mf_dic.keys():  # 避免PATHC Value被覆盖修改
                    continue
                value = self.not_the_value(key, mapto_value, mapto_name)
                kv = {key: value}
                if mf["MapTerms"] == "OR":  # OR的只选择一个
                    mf_dic.update(kv)
                    break
                mf_dic.update(kv)  # AND的选择所有
        return mf_dic

    def check_mapto(self, mapfrom: list):
        """ PATCH完成后重启，检查所有的MapTo的联动条件是否满足 """
        # pandas DataFrame filter doesn't support list types, use column IndexStr instead
        mf_info = {mf["MapFromAttribute"]: mf["MapFromValue"] for mf in mapfrom}
        mapto_row = self.map_from_pd[self.map_from_pd["IndexStr"].values == json.dumps(mapfrom, indent=4)].iloc[0]
        result = True
        for mi, mt in mapto_row.items():
            if not isinstance(mi, int):
                continue
            if not mt:
                continue
            map_key = mt.get("MapToAttribute")
            map_property = mt.get("MapToProperty")
            map_value = mt.get("MapToValue")
            # json transfer data as str, redfish may get value as int
            if isinstance(map_value, str):
                map_value = int(map_value) if map_value.isdigit() else map_value
            # Check Value Equal MapTo
            if map_property == "CurrentValue":
                if not self.check(**{map_key: map_value}):
                    result = result & False
                    logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <fail>")
                    continue
                logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <pass>")
                continue
            # Hidden/ReadOnly map_key can't be changed
            patch_try = self.patch_radom(map_key)
            if patch_try.result is None:
                continue
            if (map_property == "Hidden" or map_property == "ReadOnly") and map_value:
                if patch_try.result:
                    result = result & False  # Hidden/ReadOnly should patch fail
                    logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <fail>")
                    logging.info(rf"Status: {patch_try.status}")
                    continue
                logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <pass>")
                continue
            # is map_key be mapped bt other item as Hidden/ReadOnly ?
            if self.mapto_link.get(map_key):
                for kmf, vmf in mf_info.items():
                    if vmf in self.mapto_link[map_key].get(kmf):
                        if patch_try.result:
                            result = result & False
                            logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <fail>")
                            logging.info(rf"Message: {patch_try.body}")
                            continue
                        logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <pass>")
                    else:
                        if not patch_try.result:
                            result = result & False
                            logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <fail>")
                            logging.info(rf"Message: {patch_try.body}")
                            continue
                        logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <pass>")
                continue
            # Others Patch pass
            if not patch_try.result:
                result = result & False
                logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <fail>")
                logging.info(rf"Message: {patch_try.body}")
                continue
            logging.info(rf"[CHECK] MapTO: {map_key}: {map_property} -> {map_value} <pass>")
        return result

    def patch_radom(self, key: str):
        """ 随机选择一个有效Value去PATCH，用于重启后检查是否能修改，判断是否隐藏或只读 """
        attpd = self.atts_pd
        if key not in attpd.index:
            logging.info(rf"[{key}] not in AttributeName list, <skipped>")
            return {"result": None}
        att_series = attpd.loc[key]
        default = att_series["DefaultValue"]
        if att_series["Type"] == "Enumeration":
            vale = deepcopy(att_series["Value"])
            if default in vale:
                vale.remove(default)
            value = random.choice(vale)
            return self.write(**{key: value})
        if att_series["Type"] == "Integer":
            low = int(att_series["LowerBound"])
            up = int(att_series["UpperBound"] + 1)
            scrlar = int(att_series["ScalarIncrement"])
            scrlar = 1 if (scrlar == 0) else scrlar
            iter_range = list(range(low, up, scrlar))
            iter_range.remove(default)
            ival = random.choice(iter_range)
            return self.write(**{key: ival})

    def gen_report(self):
        """ 生成最终结果 """
        self.map_from_pd["Summary"] = self.map_from_pd.apply(
            lambda x:
            "Pass" if (
                              x.CheckStatus == "pass" and x.PatchStatus == "pass" and x.CheckMapTo == "pass")  else
            ("Fail" if (
                    x.CheckStatus == "fail" or x.PatchStatus == "fail" or x.CheckMapTo == "fail") else
             None), axis=1)
        self.map_from_pd.drop(labels="IndexStr", axis=1, inplace=True)
        self.map_from_pd["index"] = self.map_from_pd["index"].apply(json.dumps).apply(eval)
        self.map_from_pd["index"] = self.map_from_pd["index"].apply(lambda x: json.dumps(x, indent=4))
        to_excel(self.map_from_pd, "DepMainSummary")

    def run_test(self):
        # 初始化整理数据
        self.depenfor_info(dump=True)
        self.mapto_info(dump=True)
        self.attributes_info(dump=True)
        self.mapfrom_info(dump=True)
        self.drop_hidden_false(dump=True)
        pdlist = self.map_from_pd.columns.tolist()
        pdlist = pdlist[:1] + ["IndexStr", "PATCH", "IsMapped", "PatchStatus", "CheckStatus", "CheckMapTo",
                               "Summary"] + pdlist[1:]
        self.map_from_pd = self.map_from_pd.reindex(columns=pdlist)
        self.map_from_pd["IndexStr"] = self.map_from_pd["index"].apply(lambda x: json.dumps(x, indent=4))

        # 遍历测试
        for row, mf_item in self.map_from_pd["index"].iteritems():
            try:
                logging.info("==========================================================")

                # Load Default and Reboot
                self.load_default()
                if not reboot_sut(ssh_bmc=self.ssh, serial=self.serial):
                    logging.info("Boot up failed")
                    continue
                logging.info("Boot up successfully")

                # print test title
                key_value = self.gen_patch_data(mf_item)
                logging.info("Start test {}".format(key_value))

                # PATCH items of mapped as unchanged
                if self.mapped_as_unchanged(mf_item):
                    logging.info(r"Items is mapped as Hidden or ReadOnly, try patch with top-level")
                    # 多级联动的情况，将主菜单和子菜单一起修改，主菜单要改为 非 Hidden / ReadOnly
                    self.map_from_pd.loc[row, "IsMapped"] = "yes"
                    key_value = self.gen_data_w_top(mf_item)
                    self.map_from_pd.loc[row, "PATCH"] = json.dumps(key_value, indent=4)
                    patch_result = self.write(**key_value)
                    if not patch_result.result:
                        logging.info(r"[PATCH] {} <fail>".format(key_value))
                        logging.info(f"Status: {patch_result.status}")
                        logging.info(rf"Message: {patch_result.body}")
                        self.map_from_pd.loc[row, "PatchStatus"] = "fail"
                        continue
                    logging.info(r"[PATCH] {} <pass>".format(key_value))
                    logging.info(rf"Status: {patch_result.status}")
                    self.map_from_pd.loc[row, "PatchStatus"] = "pass"
                else:
                    # Normal PATCH
                    self.map_from_pd.loc[row, "PATCH"] = json.dumps(key_value, indent=4)
                    patch_result = self.write(**key_value)
                    if not patch_result.result:
                        logging.info(r"[PATCH] {} <fail>".format(key_value))
                        logging.info(rf"Error Message: {patch_result.body}")
                        self.map_from_pd.loc[row, "PatchStatus"] = "fail"
                        continue
                    logging.info(r"[PATCH] {} <pass>".format(key_value))
                    self.map_from_pd.loc[row, "PatchStatus"] = "pass"

                # REBOOT
                if not reboot_sut(ssh_bmc=self.ssh, serial=self.serial):
                    logging.info("Boot up failed")
                    continue
                logging.info("Boot up successfully")

                # CHECK MapFrom
                if not self.check(**key_value):
                    logging.info(r"[CHECK] >>> MapFrom: {} <fail>".format(key_value))
                    self.map_from_pd.loc[row, "CheckStatus"] = "fail"
                    continue
                logging.info(r"[CHECK] >>> MapFrom: {} <pass>".format(key_value))
                self.map_from_pd.loc[row, "CheckStatus"] = "pass"

                # CHECK MapTo
                if not self.check_mapto(mf_item):
                    self.map_from_pd.loc[row, "CheckMapTo"] = "fail"
                    logging.info(r"[CHECK] >>> MapTo Result: <fail>")
                    continue
                self.map_from_pd.loc[row, "CheckMapTo"] = "pass"
                logging.info(r"[CHECK] >>> MapTo Result: <pass>")

                # Force to UEFI if 'BootType' is set to 'LegacyBoot' (this attribute can't be load default with post)
                if ('BootType', 'LegacyBoot') in key_value.items():
                    assert self.write(BootType='UEFIBoot').result
                    assert reboot_sut(self.ssh, self.serial)

            except Exception as e:
                logging.info(e)
                continue

        # Result Summary
        self.gen_report()
