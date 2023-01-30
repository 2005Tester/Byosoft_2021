# -*- encoding=utf8 -*-
import os
import requests
import json, redfish
from redfish.rest.v1 import InvalidCredentialsError, RetriesExhaustedError
import logging, time, re
import importlib
from batf import var
import random
from collections import OrderedDict
from Inspur7500.BaseLib import BmcLib


class Redfish:
    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        self.config = importlib.import_module('.Config.SutConfig', package=var.get('project'))
        self.ip = self.config.Env.BMC_IP
        self.user = self.config.Env.BMC_USER
        self.psw = self.config.Env.BMC_PASSWORD
        self.GET_URL = "https://{}/redfish/v1/Systems/1/Bios/".format(self.ip)
        self.BIOS_URL = "https://{}/redfish/v1/Systems/1/Bios/Settings".format(self.ip)
        self.POST_RUL = "https://{}/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios".format(self.ip)
        self.SESSION_URL = "https://{}/redfish/v1/SessionService/Sessions".format(self.ip)
        self.headers = {
            'If-Match': 'W/"584db857"',
            'X-Auth-Token': 'TdeOYHzgr2egh475MVxw',
            'Content-Type': 'application/json',
        }

    # 获取token
    def get_token(self):
        headers_session = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data_session = {
            "UserName": self.user,
            "Password": self.psw
        }
        data_session = json.dumps(data_session)
        response = requests.request("POST", self.SESSION_URL, headers=headers_session, data=data_session, verify=False)
        token = response.headers['X-Auth-Token']
        response.close()
        if token:
            print(token)
            return token

    # 登录RedFish
    def login(self):
        response = requests.request("GET", self.SESSION_URL, headers=self.headers, verify=False)
        if response.status_code == 200:
            return True
        else:
            logging.info('登陆出错，重新生成token')
            token = self.get_token()
            response.close()
            if token:
                self.headers['X-Auth-Token'] = token
                try_counts = 3
                while try_counts:
                    if requests.request("GET", self.SESSION_URL, headers=self.headers, verify=False).status_code == 200:
                        return True
                    else:
                        logging.info('使用新的token登陆出错，5秒后重试')
                        time.sleep(5)
                        try_counts -= 1
            else:
                logging.info(f'使用新的token尝试登录3次后，仍出错')
                return

    # 删除会话
    def del_session(self):
        if self.login():
            response = requests.request("GET", self.SESSION_URL, headers=self.headers, verify=False)
            print(response.text)
            for i in re.findall(r'"@odata.id": "(/redfish/v1/SessionService/Sessions/\w+)"', response.text):
                url = f'https://{self.ip}{i}'
                response = requests.request("DELETE", url, headers=self.headers, verify=False)
                print(response.text)
                response.close()
                time.sleep(2)
        else:
            return

    def get_current_vlaue(self):
        if self.login():
            response = requests.request('GET', self.BIOS_URL, headers=self.headers, verify=False)
            dict = json.loads(response.text)
            if "Attributes" in dict.keys():
                return dict["Attributes"]
            else:
                return dict
        else:
            return

    def get_etag(self, url):
        if not self.login():
            return
        result = requests.request('GET', url, headers=self.headers, verify=False).headers
        if 'ETag' in dict(result).keys():
            e_tag = result["Etag"]
        else:
            e_tag = 'W/"584db857"'
        return e_tag

    def change_bios_value(self, input):
        if self.login():
            class PatchStatus:
                status = None
                body = None
                result = None

            currect = self.get_current_vlaue()
            if "Attributes" in dict(input).keys():
                for key, value in input["Attributes"].items():
                    currect[key] = value
                data = {
                    "Attributes": currect
                }
            else:
                for key, value in input.items():
                    currect[key] = value
                data = input

            self.headers['If-Match'] = self.get_etag(self.BIOS_URL)
            data = json.dumps(data)
            logging.debug(data)
            response = requests.request('PATCH', self.BIOS_URL, headers=self.headers, data=data, verify=False)
            PatchStatus.status = response.status_code
            PatchStatus.result = True if (response.status_code == 200) else False
            if response.status_code == 200:
                logging.info('RedFish change option,value successfully')
                msg = json.loads(response.text)
            else:
                msg = json.loads(response.text)
            response.close()
            PatchStatus.body = msg
            return PatchStatus
        else:
            return

    # input {key,value}
    # output:True  all input in msg
    #       diff  a dict{} difference in msg
    def check_value(self, input):
        if self.login():
            fail_count = 0
            diff = {}
            response = requests.request('GET', self.BIOS_URL, headers=self.headers, verify=False)
            if response.status_code == 200:
                dict = json.loads(response.text)["Attributes"]
                for key, value in input.items():
                    if key in dict.keys():
                        if dict[key] != value:
                            fail_count += 1
                            diff[key] = dict[key]
                    else:
                        logging.info(f'{key} not in BIOS options,please check.')
                        fail_count += 1
            response.close()
            if fail_count == 0:
                return True
            else:
                return diff
        else:
            return

    def get_msg(self, url):
        data = ''
        if self.login():
            url = f"https://{self.ip}{url}"
            response = requests.request('GET', url, headers=self.headers, verify=False)
            response.close()
            if response.status_code in [200, 201, 202]:
                dict = json.loads(response.text)
                data = dict
                return data
        else:
            return

    def post(self, url, input):
        url = f"https://{self.ip}{url}"
        if self.login():
            class PatchStatus:
                status = None
                body = None
                result = None

            input = json.dumps(input)
            response = requests.request('POST', url, headers=self.headers, data=input, verify=False)
            PatchStatus.status = response.status_code
            PatchStatus.result = True if (response.status_code in [200, 201, 202]) else False
            if response.status_code in [200, 201, 202]:
                logging.info('RedFish Post successfully')
                msg = json.loads(response.text)
            else:
                msg = json.loads(response.text)
            response.close()
            PatchStatus.body = msg
            return PatchStatus
        else:
            return

    def patch(self, url, input):
        if self.login():
            url = f"https://{self.ip}{url}"

            class PatchStatus:
                status = None
                body = None
                result = None

            self.headers['If-Match'] = self.get_etag(url)
            input = json.dumps(input)
            response = requests.request('PATCH', url, headers=self.headers, data=input, verify=False)
            PatchStatus.status = response.status_code
            PatchStatus.result = True if (response.status_code in [200, 201, 202]) else False
            if response.status_code in [200, 201, 202]:
                logging.info('RedFish patch successfully')
                msg = json.loads(response.text)
            else:
                msg = json.loads(response.text)
            response.close()
            PatchStatus.body = msg
            return PatchStatus
        else:
            return

    def update_bios(self, mode, path):
        if BmcLib.power_status() == 'Chassis Power is off':
            logging.info('Power is off ,start to update bios')
        else:
            BmcLib.power_off()
            time.sleep(10)
        url_exit = f'https://{self.ip}/redfish/v1/UpdateService/FirmwareInventory/BIOS/Actions/Oem/Byosoft.Firmware.ExitUpdateMode'
        if not self.login():
            return
        logging.info('Start to upload BIOS file...')
        url_upload = f'https://{self.ip}/redfish/v1/UpdateService/FirmwareInventory/BIOS/Actions/Oem/Byosoft.Firmware.Upload'
        with open(path, 'rb') as f:
            response = requests.request("POST", url=url_upload, data=f, headers=self.headers, verify=False)
        if response.status_code in [200, 201, 202]:
            logging.info('Upload BIOS file successfully...')
        else:
            logging.debug(response.text)
            logging.error('Upload BIOS file fail...')
            requests.request("POST", url=url_exit, headers=self.headers, verify=False)
            return
        time.sleep(2)
        logging.info('Start to prepare for target update...')
        url_prepare = f'https://{self.ip}/redfish/v1/UpdateService/FirmwareInventory/BIOS/Actions/Oem/Byosoft.Firmware.EnterUpdateMode'
        response = requests.request("POST", url=url_prepare, headers=self.headers, verify=False)
        if response.status_code in [200, 201, 202]:
            logging.info('Enter Update Mode Successfully')
        else:
            logging.debug(response.text)
            logging.error('Enter Update Mode Fail')
            requests.request("POST", url=url_exit, headers=self.headers, verify=False)
            return
        time.sleep(2)
        logging.info('Select Update Mode(Full Update or Reserved Configuration)')
        url_mode = f'https://{self.ip}/redfish/v1/UpdateService/FirmwareInventory/BIOS/Actions/Oem/Byosoft.Firmware.Update'
        if mode == 'all':
            data = {"PreserveCfg": False}
        elif mode == 'normal':
            data = {"PreserveCfg": True}
        else:
            logging.info('Update Mode Error,Update BIOS by Full Update')
            data = {"PreserveCfg": False}
        data = json.dumps(data)
        response = requests.request("POST", url=url_mode, headers=self.headers, verify=False, data=data)
        if response.status_code in [200, 201, 202]:
            logging.info(f'Select Update Mode {mode} Sueeceefully')
        else:
            logging.debug(response.text)
            logging.error(f'Select Update Mode {mode} Fail')
            requests.request("POST", url=url_exit, headers=self.headers, verify=False)
            return
        logging.info('Start Update BIOS')
        url_state = f'https://{self.ip}/redfish/v1/UpdateService/FirmwareInventory/BIOS'
        start = time.time()
        while True:
            response = requests.request("GET", url=url_state, headers=self.headers, verify=False)
            dict = json.loads(response.text)
            percent = dict["Oem"]["Byosoft"]["UpdatePercentage"]
            logging.info(f'PERCENTAGE = {percent}%')
            if percent == 100:
                break
            now = time.time()
            if now - start > 300:
                break
            time.sleep(1)
        logging.info('Update BIOS Successfully')
        time.sleep(5)
        response = requests.request("POST", url=url_exit, headers=self.headers, verify=False)
        if response.status_code in [200, 201, 202]:
            logging.info('Exit Update Menu')
        else:
            logging.debug(response.text)
            logging.error(f'Fail to Exit Update Menu')
            return
        return True

    # Dump Registry,  dump=True则将 registry 保存为本地json文件
    def registry_dump(self, dump_json=False, path=".", name="registry.json"):
        if not self.login():
            return
        data = self.get_msg('/redfish/v1/Registries/BiosAttributeRegistry')
        if data:
            if dump_json:
                json_file = os.path.join(os.path.abspath(path), name)
                with open(json_file, "w") as f:
                    json.dump(data, f, indent=4)
                    logging.info("{} dump pass".format(json_file))
            return data
        logging.info("Error: response code")

    # 加载registry文件，返回字典
    def load_registry_file(self):
        with open(self.config.Rfs.REGISTRY_FILE, 'r') as fp:
            registry = json.load(fp)
        return registry

    # 读取registry.json中所有AttributeName, 返回varnames list
    def get_all_varnames(self):
        varnames = []
        registry = self.load_registry_file()
        for item in registry["RegistryEntries"]["Attributes"]:
            varnames.append(item["AttributeName"])
        return varnames

    def get_varnames(self, path):
        varnames = []
        with open(path, 'r') as fp:
            registry = json.load(fp)
        if "RegistryEntries" in registry.keys():
            for item in registry["RegistryEntries"]["Attributes"]:
                varnames.append(item["AttributeName"])
        elif "Attributes" in registry.keys():
            for item in registry["Attributes"]:
                varnames.append(item["AttributeName"])
        else:
            varnames = list(registry.keys())
        return varnames

    def supported_value(self, varname):
        all_varnames = self.get_all_varnames()
        registry = self.load_registry_file()
        if varname in all_varnames:
            if self.get_key_value_registry(varname, "Type") == "Enumeration":
                for item in registry["RegistryEntries"]["Attributes"]:  # Attributes list中的每个选项的详细信息
                    if item["AttributeName"] == varname:
                        return [val["ValueName"] for val in item["Value"]]  # val为描述所有支持的value的dict
            elif self.get_key_value_registry(varname, "Type") == 'Integer':
                scalar = self.get_key_value_registry(varname, "ScalarIncrement")
                scalar = scalar if scalar else 1
                lower = self.get_key_value_registry(varname, "LowerBound")
                upper = self.get_key_value_registry(varname, "UpperBound")
                values = list(range(int(lower), int(upper) + 1, int(scalar)))
                return values
        else:
            print(varname + " is not supported.")

    # 从 json 文件加载所有的选项, 返回payloads字典
    def load(self, tc_file):
        with open(tc_file, 'r') as f:
            payloads = json.load(f, object_pairs_hook=OrderedDict)
            if not isinstance(payloads, dict):
                payloads = json.loads(payloads, object_pairs_hook=OrderedDict)
            return payloads

    # 返回特定选项的特定key的value
    def get_key_value_registry(self, key, value):
        registry = self.load_registry_file()
        for item in registry["RegistryEntries"]["Attributes"]:  # Attributes list中的每个选项的详细信息
            if item["AttributeName"] == key:
                if value in item.keys():
                    return item[value]
                else:
                    return None

    # 去除测试文件中所有有依赖的选项
    def remove_dependence(self, tc_file):
        dependece = self.load(self.config.Rfs.DEPENDENCE_FILE)
        testscope = self.load(tc_file)
        for i in list(testscope.keys()):
            if i in dependece.keys():
                del testscope[i]
        with open(tc_file, 'w') as fp:
            json.dump(testscope, fp, indent=1)

    # 改变testcase 文件中选项的值为非默认（随机）
    def change_value_random(self, tc_file):
        testscope = self.load(tc_file)
        for key in testscope:
            values = self.supported_value(key)
            if values:
                if len(values) == 1:
                    pass
                else:
                    values.remove(testscope[key])
                    desired_value = random.choice(values)
                    testscope[key] = desired_value
        with open(tc_file, 'w') as fp:
            json.dump(testscope, fp, indent=1)

    # 为测试文件中需要依赖的选项，添加依赖选项
    def add_dependence(self, tc_file):
        dependence = self.load(self.config.Rfs.DEPENDENCE_FILE)
        testscope = self.load(tc_file)
        for i in list(testscope.keys()):
            if i in dependence.keys():
                for m, n in dependence[i].items():
                    testscope[m] = n
        with open(tc_file, 'w') as fp:
            json.dump(testscope, fp, indent=1)

    # 遍历registry.json, 返回所有选项所支持的value
    def gen_payload_list(self, path=''):
        payload_list = []
        if path:
            all_options = self.get_varnames(path)
        else:
            all_options = self.get_all_varnames()
        # dep_options = get_varnames_dep()[0]
        # non_dep_options = list(set(all_options)-set(dep_options))
        for option in all_options:
            values = self.supported_value(option)
            for value in values:
                payload = {option: value}
                payload_list.append(payload)
        return payload_list

    # 遍历registry.json, 返回所有选项的随机值
    def gen_payload_list_random_value(self, path=''):
        payload_list = []
        if path:
            all_options = self.get_varnames(path)
        else:
            all_options = self.get_all_varnames()
        for option in all_options:
            if len(self.supported_value(option)) == 1:
                value = self.supported_value(option)[0]
            else:
                value = random.choice(self.supported_value(option))
            payload = {option: value}
            payload_list.append(payload)
        return payload_list

    # 通过registry.json检查testcase json文件里面的setup option的值是否合法
    def verify_testcase(self, testcase_file, remove=False):
        testscope = self.load(testcase_file)
        all_varnames = self.get_all_varnames()
        for setupoption in list(testscope.keys()):
            if setupoption in all_varnames:
                if self.get_key_value_registry(setupoption, "Type") == "Enumeration":
                    if not testscope[setupoption] in self.supported_value(setupoption):
                        print(setupoption + ":Value is invalid.")
                        print("Supported values: ")
                        print(self.supported_value(setupoption))
                        print('-' * 30)
                        if remove:
                            del testscope[setupoption]
                elif self.get_key_value_registry(setupoption, "Type") == "Integer":
                    scalar = self.get_key_value_registry(setupoption, "ScalarIncrement")
                    scalar = scalar if scalar else 1
                    lower = self.get_key_value_registry(setupoption, "LowerBound")
                    upper = self.get_key_value_registry(setupoption, "UpperBound")
                    if testscope[setupoption] not in list(range(int(lower), int(upper) + 1, int(scalar))):
                        print(setupoption + ":Value is invalid.")
                        print(f"Supported values: ({str(lower)},{str(upper)})")
                        print('-' * 30)
                        if remove:
                            del testscope[setupoption]
                if self.get_key_value_registry(setupoption, "GrayOut") == True:
                    print(setupoption + " is GrayOut")
                    if remove:
                        del testscope[setupoption]
            else:
                print(setupoption + " is invalid")
                print('-' * 30)
                if remove:
                    del testscope[setupoption]
        if remove:
            with open(testcase_file, 'w') as fp:
                json.dump(testscope, fp, indent=1)

    # 下载当前option，value到本地
    def dump_currect_value(self, path):
        if not self.login():
            return
        data = self.get_current_vlaue()

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
