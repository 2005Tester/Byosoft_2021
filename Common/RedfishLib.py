# -*- encoding=utf8 -*-

import json
import logging
import os
import re
import time

import redfish
from redfish.rest.v1 import InvalidCredentialsError, RetriesExhaustedError


class Redfish(object):
    CURRENT_PATH = r"/redfish/v1/Systems/1/Bios"
    REGISTRY_PATH = r"/redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v{}_{}_{}.json"
    PATCH_PATH = r"/redfish/v1/Systems/1/Bios/Settings"
    POST_PATH = r"/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"

    def __init__(self, bmc_ip, user, pw):
        self.host = f"https://{bmc_ip}"
        self.user = user
        self.pw = pw
        self.current = None
        self.registry = None
        self.current_json = None
        self.registry_json = None
        self.session = redfish.redfish_client(base_url=self.host, username=self.user, password=self.pw, timeout=5, max_retry=5)
        self.reg_match()

    def login(self):
        try:
            self.session.login(auth="basic")
            logging.info("Redfish login successfully")
        except InvalidCredentialsError:
            logging.error("[InvalidCredentialsError]：login retry after 10s")
            time.sleep(10)
            self.login()
        except RetriesExhaustedError:
            logging.error("[RetriesExhaustedError]：login retry after 10s")
            time.sleep(10)
            self.login()
        except Exception as e:
            logging.error(e)
            return
        return True

    def logout(self):
        self.session.logout()

    # 获取registry文件的版本号
    def reg_match(self):
        if not self.login():
            return
        data = self.session.get(self.CURRENT_PATH)
        if data.status != 200:
            return
        reg_ver = re.findall(r"BiosAttributeRegistry.(\d+).(\d+).(\d+)", data.dict.get("AttributeRegistry"))[0]
        self.REGISTRY_PATH = self.REGISTRY_PATH.format(reg_ver[0], reg_ver[1], reg_ver[2])
        self.logout()

    # 获取E-Tag
    def get_etag(self):
        e_tag = self.session.get(self.PATCH_PATH).getheader(name="ETag")
        if not e_tag:
            time.sleep(5)
            self.get_etag()
        return {"If-Match": e_tag}

    # 获取attribute的当前值,同时更新self.current
    def read(self, *args):
        """
        Input:  *[key1, key2] or "key1", "key2"
        Output: {key1: value1, key2: value2}
        """
        result = {}
        if not self.login():
            return result
        data = self.session.get(self.CURRENT_PATH)
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            for key in args:
                result[key] = self.current.get(key)
            self.logout()
            return result

    # 输入选项和取值，PATCH后LOG打印结果
    def write(self, **kwargs):
        """
        Input:  **{"key1": value1, "key2": value2} or key1=value1, key2=value2
        Output: {   status:     patch status code: int,
                    body:       Pass       ->   Attributes: {}
                                Fail       ->   Message: str
                    result:     True / False
                }
        """
        class PatchStatus:
            status = None
            body = None
            result = None
        if not self.login():
            return PatchStatus
        body = {"Attributes": kwargs}
        patch = self.session.patch(path=self.PATCH_PATH, body=body, headers=self.get_etag())
        time.sleep(0.5)
        result = True if (patch.status == 200) else False
        if patch.status == 200:
            msg = re.findall(r'("Attributes":\s*\{.+?\}),', patch.text)
        else:
            msg = re.findall(r'"Message":\s*"(.+?)",', patch.text)
        PatchStatus.status = patch.status
        PatchStatus.body = "".join(msg)
        PatchStatus.result = result
        self.logout()
        return PatchStatus

    # 检查选项key的值是否为value,同时更新self.current
    def check(self, **kwargs):
        """
        Input:  **{key1: value1, key2: value2} or key1=value1, key2=value2
        Output: True / False
        """
        if not self.login():
            return
        data = self.session.get(self.CURRENT_PATH)
        fail_cnt = 0
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            for key, value in kwargs.items():
                if self.current.get(key) != value:
                    fail_cnt += 1
            self.logout()
            return fail_cnt == 0

    # 通过POST请求恢复默认
    def load_default(self):
        """ Load Default with POST operation, unable to change UEFI/Legacy """
        if not self.login():
            return
        response = self.session.post(path=self.POST_PATH, body={})
        if response.status == 200:
            logging.info("BIOS load default successful!")
            self.logout()
            return True

    # Dump CurrentValue, 变量保存到self.current, dump=True则将 currentvalue 保存为本地json文件
    def current_dump(self, dump_json=False, path=".", name="CurrentValue.json"):
        if not self.login():
            return
        data = self.session.get(self.CURRENT_PATH)
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            if dump_json:
                json_file = os.path.join(os.path.abspath(path), name)
                with open(json_file, "w") as f:
                    json.dump(self.current, f, indent=4)
                    self.current_json = json_file
                    logging.info("{} dump pass".format(json_file))
            self.logout()
            return self.current
        logging.info("Error: response code: {}".format(data.status))

    # Dump Registry, 变量保存到self.registry, dump=True则将 registry 保存为本地json文件
    def registry_dump(self, dump_json=False, path=".", name="Registry.json"):
        if not self.login():
            return
        data = self.session.get(self.REGISTRY_PATH)
        if data.status == 200:
            self.registry = {k: v for k, v in data.dict.items() if
                             k in ["Language", "RegistryVersion", "RegistryEntries"]}
            if dump_json:
                json_file = os.path.join(os.path.abspath(path), name)
                with open(json_file, "w") as f:
                    json.dump(self.registry, f, indent=4)
                    self.registry_json = json_file
                    logging.info("{} dump pass".format(json_file))
            self.logout()
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
