# -*- encoding=utf8 -*-

# SSH Configuration
sut = '192.168.2.100'
port = '22'
username = 'Administrator'
password = 'Admin@9000'
PING_CMD = 'ping 192.168.100.199'

EXELUDE_TEST = ['serialDebugMsgLvl', 'PowerOnPassword', 'MemChannelEnable[0]', 'MemChannelEnable[7]', 'PchUsbHsPort[8]']
BIOS = "C:\\UpdateTool\\HY5V017_candidate1.bin"
BIOS_CODE = "D:\\Code\\HY5\\Intel\\WhitleyRpPkg001"
REGISTRY_FILE = ".\\baseline\\registry.json"
HIDDEN_LIST = ".\\baseline\\hidden.txt"
CURR_SET_JSON = ".\\baseline\\current.json"

GET_URL = "https://192.168.2.100/redfish/v1/Systems/1/Bios/"
PATCH_URL = "https://192.168.2.100/redfish/v1/Systems/1/Bios/Settings/"

# log setting
TEST_RESULT_DIR = "C:\\redfishtest"
LOG_FILE = "C:\\redfishtest\\redfishtest.log"
INIT_STATUS = {"Completed": [], "Passed": [], "Error": [], "Failed": []}

help_msg = """
Usage: 
python redfish.py [xxx.json] --Patch and verify all the setup options defined in xxx.json
python redfish.py [directoryname] --Find all the json files in specified directory, and run all the tests in those json files
python redfish.py [checkregistry] --check whether registry.json and setup baseline is aligned
python redfish.py [init]     --cleanup teststatus
"""