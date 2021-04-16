# -*- encoding=utf8 -*-

import json
import logging
import os
import re
import time

import redfish

import RedFish.config as config


class RedFish(object):
    CURRENT_PATH = r"/redfish/v1/Systems/1/Bios"
    REGISTRY_PATH = r"/redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v{}_{}_{}.json"
    PATCH_PATH = r"/redfish/v1/Systems/1/Bios/Settings"
    POST_PATH = r"/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"

    def __init__(self, ip=config.bmc_ip, user=config.bmc_user, pw=config.bmc_pw):
        self.ip = ip
        self.user = user
        self.pw = pw
        self.session = None
        self.current = None
        self.registry = None
        self.current_json = None
        self.registry_json = None
        self.login()
        self.current_dump()
        self.registry_dump()

    def login(self):
        host = "https://{}".format(self.ip)
        self.session = redfish.redfish_client(base_url=host, username=self.user, password=self.pw)
        try:
            self.session.login(auth="basic")
            logging.info("Redfish login successful")
            self.reg_match()
            return True
        except Exception as e:
            logging.info(f"Redfish login error：{e}")
            return False

    def logout(self):
        self.session.logout()

    # 获取registry文件的版本号
    def reg_match(self):
        data = self.session.get(self.CURRENT_PATH)
        if data.status != 200:
            return
        reg_ver = re.findall(r"BiosAttributeRegistry.(\d+).(\d+).(\d+)", data.dict.get("AttributeRegistry"))[0]
        self.REGISTRY_PATH = self.REGISTRY_PATH.format(reg_ver[0], reg_ver[1], reg_ver[2])

    # 获取E-Tag
    def get_etag(self):
        e_tag = self.session.get(self.PATCH_PATH).getheader(name="ETag")
        return {'If-Match': e_tag}

    # 获取attribute的当前值,同时更新self.current
    def read(self, *args):
        """
        Input:  [key1, key2]
        Output: {key1: value1, key2: value2}
        """
        data = self.session.get(self.CURRENT_PATH)
        result = {}
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            for key in args:
                result[key] = self.current.get(key)
            return result

    # 输入选项和取值，PATCH后LOG打印结果
    def write(self, **kwargs):
        """
        Input:  {key1: value1, key2: value2}
        Output: {   "status":   patch status code: int,
                    "body":     Pass       ->   Attributes: {}
                                Fail       ->   Message: str
                    "result":   True / False}
        """
        body = {"Attributes": kwargs}
        patch = self.session.patch(path=self.PATCH_PATH, body=body, headers=self.get_etag())
        time.sleep(0.5)
        result = True if (patch.status == 200) else False
        msg = re.findall(r'("Attributes":\s*\{.+?\}),', patch.text) if result else re.findall(r'"Message":\s*"(.+?"),',
                                                                                              patch.text)
        return {"status": patch.status, "body": "".join(msg), "result": result}

    # 检查选项key的值是否为value,同时更新self.current
    def check(self, **kwargs):
        """
        Input:  {key1: value1, key2: value2}
        Output: True / False
        """
        data = self.session.get(self.CURRENT_PATH)
        result = True
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            for key, value in kwargs.items():
                if self.current.get(key) != value:
                    result = result & False
            return result

    # 通过POST请求恢复默认
    def load_default(self):
        """ Load Default with POST operation, unable to change UEFI/Legacy """
        response = self.session.post(path=self.POST_PATH, body={})
        if response.status == 200:
            logging.info("BIOS load default successful!")
            return True

    # Dump CurrentValue, 变量保存到self.current, 可选择是否保存到本地 .json文件, 默认路径为config.TEST_RESULT_DIR
    def current_dump(self, dump_name=None):
        data = self.session.get(self.CURRENT_PATH)
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            if dump_name:
                self.current_json = os.path.join(config.TEST_RESULT_DIR, dump_name)
                with open(self.current_json, "w") as f:
                    json.dump(self.current, f, indent=4)
                    logging.info("{}/{} dump pass".format(config.TEST_RESULT_DIR, dump_name))
            return self.current
        logging.info("Error: response code: {}".format(data.status))

    # Dump Registry, 变量保存到self.registry, 可选择是否保存到本地 .json文件, 默认路径为config.TEST_RESULT_DIR
    def registry_dump(self, dump_name=None):
        data = self.session.get(self.REGISTRY_PATH)
        if data.status == 200:
            self.registry = {k: v for k, v in data.dict.items() if
                             k in ["Language", "RegistryVersion", "RegistryEntries"]}
            if dump_name:
                self.registry_json = os.path.join(config.TEST_RESULT_DIR, dump_name)
                with open(self.registry_json, "w") as f:
                    json.dump(self.registry, f, indent=4)
                    logging.info("{}/{} dump pass".format(config.TEST_RESULT_DIR, dump_name))
            return self.registry
        logging.info("Error: response code: {}".format(data.status))

    def Attributes(self):
        if not self.registry:
            self.registry_dump()
        return self.registry["RegistryEntries"]["Attributes"]

    def Menus(self):
        if not self.registry:
            self.registry_dump()
        return self.registry["RegistryEntries"]["Menus"]

    def Dependencies(self):
        if not self.registry:
            self.registry_dump()
        return self.registry["RegistryEntries"]["Dependencies"]

    def AttributeName_list(self):
        return [n.get("AttributeName") for n in self.Attributes()]

    def DependencyFor_list(self):
        return list(set([d.get("DependencyFor") for d in self.Dependencies()]))
