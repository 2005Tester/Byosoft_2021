# -*- encoding=utf8 -*-

import json
import logging
import os
import re
import time

import redfish
from redfish.rest.v1 import InvalidCredentialsError, RetriesExhaustedError


class Redfish(object):
    SYSTEM = "/redfish/v1/Systems/1"
    CHASSIS = "/redfish/v1/Chassis/1"
    MANAGER = "/redfish/v1/Managers/1"
    BIOS_CURRENT = rf"{SYSTEM}/Bios"
    BIOS_SETTING = rf"{SYSTEM}/Bios/Settings"
    BIOS_RESET = rf"{SYSTEM}/Bios/Actions/Bios.ResetBios"
    REGISTRY_PATH = r"/redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v{}_{}_{}.json"

    def __init__(self, bmc_ip, user, pw):
        self.host = f"https://{bmc_ip}"
        self.user = user
        self.pw = pw
        self.session = redfish.redfish_client(base_url=self.host, username=self.user, password=self.pw, timeout=5, max_retry=5)

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
        return True

    # 获取registry.json文件的版本号与路径
    def get_reg_path(self):
        if not self.login():
            return
        data = self.session.get(self.BIOS_CURRENT)
        if data.status != 200:
            return
        reg_ver = re.findall(r"BiosAttributeRegistry.(\d+).(\d+).(\d+)", data.dict.get("AttributeRegistry"))[0]
        self.logout()
        return self.REGISTRY_PATH.format(reg_ver[0], reg_ver[1], reg_ver[2])

    # 获取E-Tag
    def get_etag(self, path):
        e_tag = self.session.get(self.SYSTEM).getheader(name="ETag")
        if not e_tag:
            time.sleep(5)
            self.get_etag(path)
        return {"If-Match": e_tag}

    def get_info(self, path: str):
        """ GET data from path, return Dict """
        try:
            assert self.login()
            get_data = self.session.get(path).dict
            assert self.logout()
            return get_data
        except Exception as e:
            logging.error(e)
            return {}

    def patch_data(self, path: str, data: dict):
        """ PATCH data to path, return status/body """
        class PatchStatus:
            status = None
            result = None
            body = None
        # try:
        assert self.login()
        get_data = self.session.patch(path=path, body=data, headers=self.get_etag(path))
        PatchStatus.status = get_data.status
        PatchStatus.body = get_data.dict
        PatchStatus.result = True if (get_data.status == 200) else False
        assert self.logout()
        return PatchStatus
        # except Exception as e:
        #     logging.error(e)
        #     return {}

    # 获取attribute的当前值,同时更新self.current
    def read_bios_option(self, *args):
        """
        Input:  *[key1, key2] or "key1", "key2"
        Output: {key1: value1, key2: value2}
        """
        result = {}
        try:
            assert self.login()
            all_data = self.session.get(self.BIOS_CURRENT).dict
            for key in args:
                result[key] = all_data.get("Attributes").get(key)
            self.logout()
            return result
        except Exception as e:
            logging.error(e)
            return {}

    # 输入选项和取值，PATCH后LOG打印结果
    def set_bios_option(self, **kwargs):
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
        patch = self.session.patch(path=self.BIOS_SETTING, body=body, headers=self.get_etag(self.BIOS_SETTING))
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
    def check_bios_option(self, **kwargs):
        """
        Input:  **{key1: value1, key2: value2} or key1=value1, key2=value2
        Output: True / False
        """
        if not self.login():
            return
        data = self.session.get(self.BIOS_CURRENT)
        fail_cnt = 0
        if data.status == 200:
            self.current = data.dict.get("Attributes")
            for key, value in kwargs.items():
                if self.current.get(key) != value:
                    fail_cnt += 1
            self.logout()
            return fail_cnt == 0

    # 通过POST请求恢复默认
    def bios_load_default(self):
        """ Load Default with POST operation, unable to change UEFI/Legacy """
        if not self.login():
            return
        response = self.session.post(path=self.BIOS_RESET, body={})
        if response.status == 200:
            logging.info("BIOS load default successful!")
            self.logout()
            return True

    # Dump CurrentValue, 变量保存到self.current, dump=True则将 currentvalue 保存为本地json文件
    def current_dump(self, dump_json=False, path=".", name="CurrentValue.json"):
        if not self.login():
            return
        data = self.session.get(self.BIOS_CURRENT)
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
        data = self.session.get(self.get_reg_path())
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
        try:
            return self.registry["RegistryEntries"]["Attributes"]
        except:
            return self.registry_dump()["RegistryEntries"]["Attributes"]

    def Menus(self):
        try:
            return self.registry["RegistryEntries"]["Menus"]
        except:
            return self.registry_dump()["RegistryEntries"]["Menus"]

    def Dependencies(self):
        try:
            return self.registry["RegistryEntries"]["Dependencies"]
        except:
            return self.registry_dump()["RegistryEntries"]["Dependencies"]
