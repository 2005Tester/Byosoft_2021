import pandas as pd
import logging
import re
from random import choice
from RedFish.commlibs.commtools import reboot_sut, to_excel
from Common.RedfishLib import Redfish
from RedFish import config
from copy import deepcopy


class NonDepTest(Redfish):
    def __init__(self, ssh_bmc, ser):
        super(NonDepTest, self).__init__(config.bmc_ip, config.bmc_user, config.bmc_pw)
        self.bmc = ssh_bmc
        self.ser = ser
        self.registry_dump(dump_json=True, path=config.TEST_RESULT_DIR)

    def attributes_data(self):
        atts = self.Attributes()
        for index, att in enumerate(atts):
            if atts[index].get("Value"):
                atts[index]["Value"] = [val["ValueName"] for val in att["Value"]]
        self.att_pd = pd.DataFrame(atts).set_index("AttributeName")
        logging.info(f"Current Registry.json contains {len(self.att_pd.index)} attributes names")

    def get_non_default_value(self, key):
        default_value = self.att_pd.loc[key, "DefaultValue"]
        if default_value is None:  # 没有默认值的情况
            logging.info(f"[Warning] DefaultValue: {key} = {default_value}")
            return
        if self.att_pd.loc[key, "Type"] == "Enumeration":  # 枚举型值
            values = deepcopy(self.att_pd.loc[key, "Value"])
            if len(values) < 2:
                logging.info(f"[Warning] Only One Value: {key} = {values}")
                return
            values.remove(default_value)
            return choice(values)
        if self.att_pd.loc[key, "Type"] == "Integer":  # 整数型值
            scalar = deepcopy(self.att_pd.loc[key, "ScalarIncrement"])
            scalar = scalar if scalar else 1
            lower = deepcopy(self.att_pd.loc[key, "LowerBound"])
            upper = deepcopy(self.att_pd.loc[key, "UpperBound"])
            values = list(range(int(lower), int(upper) + 1, int(scalar)))
            values.remove(default_value)
            return int(choice(values))

    def gen_patch_key_value(self):
        self.patch_key_value = {}
        for att in self.att_pd.index:
            value = self.get_non_default_value(att)
            if value is not None:
                self.patch_key_value[att] = value
        self.patch_key_value.update(self.boot_order_key_value())  # Boot Order取值需要特殊处理

    def report_init(self):
        self.result = pd.DataFrame.from_dict(self.patch_key_value, orient="index")  # 整理报告格式
        self.result.rename(columns={0: "patch_value"}, inplace=True)
        pdlist = self.result.columns.tolist()
        col_list = ["default_value", "patch_status", "check_status", "summary", "message"]
        col_list = col_list[:1] + pdlist + col_list[1:]
        self.result = self.result.reindex(columns=col_list)

    def drop_been_mapped(self):
        """ CurrentValue / Hidden=True / ReadOnly=True """
        dep_data = self.Dependencies()
        self.been_mapto = {}
        for dep in dep_data:
            mapfrom = {mf["MapFromAttribute"]: mf["MapFromValue"] for mf in dep["Dependency"]["MapFrom"]}
            for mf_key, mf_value in mapfrom.items():
                try:
                    if self.att_pd.loc[mf_key, "DefaultValue"] != mf_value:  # 有联动关系但默认情况不关联的视为非关联项，可直接修改
                        continue
                except Exception as e:
                    logging.error(f"{e} missing in attributes list")
            mapto_name = dep["Dependency"]["MapToAttribute"]
            mapto_property = dep["Dependency"]["MapToProperty"]
            mapto_value = dep["Dependency"]["MapToValue"]
            if (mapto_property == "CurrentValue") or ((mapto_property in ["Hidden", "ReadOnly"]) and mapto_value):
                if (mapto_name not in self.been_mapto) and (mapto_name in self.patch_key_value.keys()):
                    self.been_mapto[mapto_name] = self.patch_key_value.get(mapto_name)
        for name in self.been_mapto:
            self.patch_key_value.pop(name)

    def boot_type_load_default(self):  # boot type无法load_default
        name = "BootType"
        default = self.att_pd.loc[name, "DefaultValue"]
        logging.info(f"BootType load default to \"{default}\"")
        if self.set_bios_option(**{name: default}).result:
            logging.info("BootType load default successfully")

    def try_patch_all(self):
        except_list = config.BootInvolved.MemPop + config.BootInvolved.Exclusive + config.BootInvolved.ReadOnly
        for i in except_list:
            self.patch_key_value.pop(i)

        for k in self.att_pd.index:
            if k not in self.patch_key_value.keys():
                logging.debug(f"Items {k} will be test in single patch")
                continue
            default_value = self.att_pd.loc[k, "DefaultValue"]
            self.result.loc[k, "default_value"] = default_value
        logging.info(f"Try Patch {len(self.patch_key_value)} items that without dependency")

        while True:
            write = self.set_bios_option(**self.patch_key_value)
            logging.info(f"PATCH Status: {write.status}")
            logging.info(f"PATCH Message: {write.body}")
            if write.result:
                for key, value in self.patch_key_value.items():
                    if isinstance(value, int):
                        logging.debug(f'\"{key}\":{value},')
                    else:
                        logging.debug(f'\"{key}\":\"{value}\",')
                    self.result.loc[key, "patch_status"] = "pass"
                break
            fail_att = re.search(r"Attributes/(\S+?)\s", write.body)
            if fail_att:
                fail_att = fail_att.group(1)
            else:
                logging.info(f"[Error] Attributes not found: {write.body}")
                continue
            logging.info(f"PATCH Failed: remove \"{fail_att}\" and retry...")
            self.result.loc[fail_att, "patch_status"] = f"{write.body}"
            if self.patch_key_value.get(fail_att):
                self.patch_key_value.pop(fail_att)
            logging.info(f"Remain {len(self.patch_key_value)} items in testing...")

    def narrow_down_fail_items(self):
        """ 批量修改失败时，10个1组筛选出是哪部分选项导致无法修改成功 """
        all_keys = list(self.test_fail_key_value.keys())
        for index in range(len(all_keys)//10+1):
            logging.info("================================================")
            self.bios_load_default()
            reboot_sut(self.bmc, self.ser)
            test_keys = all_keys[0:10] if len(all_keys)>10 else all_keys
            test_kv = {k: self.test_fail_key_value[k] for k in test_keys}
            patch = self.set_bios_option(**test_kv)
            logging.info(f"[NarrowDown]: PATCH {patch.body}")
            if patch.result:
                for key in test_kv:
                    self.result.loc[key, "patch_status"] = "pass"
                reboot_sut(self.bmc, self.ser)
            if self.check_bios_option(**test_kv):
                logging.info("[NarrowDown]: pass")
                for key in test_kv:
                    self.result.loc[key, "check_status"] = "pass"
                    self.test_fail_key_value.pop(key)
            else:
                logging.info("[NarrowDown]: fail")
            for tk in test_keys:
                all_keys.remove(tk)

    def boot_order_key_value(self):
        boot_order_name = "BootTypeOrder"
        boot_order_menus = [att for att in self.att_pd.index if boot_order_name in att]
        boot_order_values = self.att_pd.loc[f"{boot_order_name}0", "Value"]
        order_key_value = {}
        for order in boot_order_menus:
            choose_value = choice(boot_order_values)
            order_key_value[order] = choose_value
            boot_order_values.remove(choose_value)
        return order_key_value

    def exclude_items_key_value(self):
        exclude_kv = {}
        for boot_os in config.BootInvolved.BootOS:
            exclude_kv[boot_os] = self.get_non_default_value(boot_os)
        return exclude_kv

    def single_patch_test(self):
        self.been_mapto.update(self.test_fail_key_value)  # fail的选项单独测试一遍
        self.been_mapto.update(self.exclude_items_key_value())  #排除的选项放在最后测试
        logging.info(f"{len(self.been_mapto)} items excluded, try test one by one...")
        excluded_items = deepcopy(self.been_mapto)
        for key, value in excluded_items.items():
            if key not in self.been_mapto:
                continue
            logging.info("============================================================")
            index_option = re.findall(r"(\w+)\[(\d+)]", key)
            patch_kv = {key: value}
            if index_option:  # 带索引的选项统一修改，减少重启次数
                index_name = index_option[0][0]
                if key in self.been_mapto.keys():
                    ifound = re.findall(rf"({index_name})\[(\d+)]", "".join(self.been_mapto.keys()))
                    for ikv in ifound:
                        ikey = f"{ikv[0]}[{ikv[1]}]"
                        patch_kv[ikey] = value
                        self.been_mapto.pop(ikey)
                else:
                    continue
            boot_order = re.findall(f"BootTypeOrder", key)
            if boot_order:  # BootOrder需要4个选项一起修改
                if key in self.been_mapto.keys():
                    patch_kv = self.boot_order_key_value()
                    for jkv in patch_kv:
                        self.been_mapto.pop(jkv)
                else:
                    continue
            logging.info(f"Testing: {patch_kv}")
            self.result.loc[key, "default_value"] = self.att_pd.loc[key, "DefaultValue"]
            self.bios_load_default()
            reboot_sut(self.bmc, self.ser)
            patch = self.set_bios_option(**patch_kv)
            if patch.result:
                logging.info(f"[PATCH] {patch.body} successfully")
                reboot_sut(self.bmc, self.ser)
                check_value = self.read_bios_option(*patch_kv.keys())
                for check_name in patch_kv.keys():
                    self.result.loc[check_name, "patch_status"] = "pass"
                    if check_value.get(check_name) == value:
                        self.result.loc[check_name, "check_status"] = "pass"
                        logging.info(f"[Check] {check_name} = {value} <pass>")
                    else:
                        logging.info(f"[Check] {check_name} = {value} <fail> -> {check_value.get(check_name)}")
                        self.result.loc[check_name, "check_status"] = "fail"
                continue
            logging.info(f"PATCH Status: {patch.status}")
            logging.info(f"PATCH Message: {patch.body}")
            for pf_name in patch_kv.keys():
                self.result.loc[pf_name, "patch_status"] = "fail"
                self.result.loc[pf_name, "message"] = patch.body

    def gen_report(self, name):
        self.result["summary"] = self.result.apply(
            lambda x:
            "Pass" if (
                    x.patch_status == "pass" and x.check_status == "pass") else
            ("Fail" if (
                    x.patch_status == "fail" or x.check_status == "fail") else
             None), axis=1)
        to_excel(self.result, name)

    def run_test(self):
        self.bios_load_default()  # 测试前先恢复默认
        reboot_sut(self.bmc, self.ser)
        self.attributes_data()  # 获取所有变量信息
        self.gen_patch_key_value()  # 生成非默认值数据表
        self.report_init()
        self.drop_been_mapped()  # 去掉默认情况就存在联动关系的选项
        self.try_patch_all()  # 先尝试批量修改
        reboot_sut(self.bmc, self.ser)
        data = self.read_bios_option(*self.patch_key_value.keys())
        self.test_fail_key_value = {}
        for key, value in self.patch_key_value.items():  # 检查批量修改的结果
            if data.get(key) != value:
                self.test_fail_key_value[key] = value
                self.result.loc[key, "check_status"] = "fail"
                logging.info(rf"[Failed] {key} | patch=<{value}>; read=<{data.get(key)}>")
                continue
            self.result.loc[key, "check_status"] = "pass"
        self.gen_report("非联动测试结果批量修改")  # 批量修改结果生成报告
        self.boot_type_load_default()  # 恢复 BootType为UEFI（因为POST无法恢复）
        self.bios_load_default()
        reboot_sut(self.bmc, self.ser)
        self.narrow_down_fail_items()  # 测试Fail的10个1组，尝试PATCH，并更新测试结果数据表
        self.single_patch_test()  # 剩下的Fail选项 + 非默认情况下有联动关系的单独测试， 每次PATCH一项并重启，更新测试结果数据表
        # 测完恢复默认
        self.bios_load_default()
        reboot_sut(self.bmc, self.ser)
        # 生成测试报告
        self.gen_report("非联动测试结果汇总")
