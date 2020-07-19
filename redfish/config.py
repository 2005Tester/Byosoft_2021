# -*- encoding=utf8 -*-

sut = '192.168.2.100'
port = '22'
username = 'Administrator'
password = 'Admin@9000'

BIOS = "HY5V016_candidate1.bin"
REGISTRY_FILE = ".\\baseline\\registry.json"
GET_URL = "https://192.168.2.100/redfish/v1/Systems/1/Bios/"
PATCH_URL = "https://192.168.2.100/redfish/v1/Systems/1/Bios/Settings/"

INIT_STATUS = {"Completed": [], "Passed": [], "Error": [], "Failed": []}

PING_CMD = 'ping 192.168.100.178'
LOG_FILE = "testlog.txt"

help_msg = """
Usage: 
python redfish.py [xxx.json] --Patch and verify all the setup options defined in xxx.json
python redfish.py [directoryname] --Find all the json files in specified directory, and run all the tests in those json files
python redfish.py [checkregistry] --check whether registry.json and setup baseline is aligned
python redfish.py [init]     --cleanup teststatus
"""