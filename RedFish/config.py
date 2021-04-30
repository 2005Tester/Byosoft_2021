#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import os
import datetime

# SSH Configuration
bmc_ip = '192.168.2.100'
port = '22'
bmc_user = 'Administrator'
bmc_pw = 'Admin@9000'

COM = "COM7"

os_ip = '192.168.2.150'
os_user = "root"
os_pw = "root"
os_timeout = 1200
unitool_path = "/root/flashtool/unitool"

AppExcel = r".\baseline\PowerEfficiency_Baseline.xls"

REPORT_DIR = r".\report"

EXELUDE_TEST = ['serialDebugMsgLvl', 'PowerOnPassword', 'MemChannelEnable[1]', 'MemChannelEnable[6]', 'PchUsbHsPort[8]']
#EXELUDE_TEST = ['MemChannelEnable[1]']
BIOS = r"C:\Binary\2288V6\5148.bin"
BIOS_CODE = "D:\\Code\\HY5\\Intel\\WhitleyRpPkg001"
REGISTRY_FILE = ".\\baseline\\registry.json"
HIDDEN_LIST = ".\\baseline\\hidden.txt"
CURR_SET_JSON = ".\\baseline\\currentvalue.json"

# request settings to communicate with BMC
GET_URL = "https://{}/redfish/v1/Systems/1/Bios/".format(bmc_ip)
PATCH_URL = "https://{}/redfish/v1/Systems/1/Bios/Settings/".format(bmc_ip)
POST_RUL = "https://{}/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios".format(bmc_ip)

headers = {
    'If-Match': 'W/"584db857"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjphZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }


# log setting
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
TEST_RESULT_DIR = "C:\\redfishtest\\log"
if not os.path.exists(TEST_RESULT_DIR):
    os.makedirs(TEST_RESULT_DIR)
LOG_FILE = "C:\\redfishtest\\redfishtest_%s.log" % (timestamp)
SERIAL_LOG = "C:\\redfishtest\\log\\serial.log"
INIT_STATUS = {"Completed": [], "Passed": [], "Error": [], "Failed": []}

help_msg = """
Usage: 
python redfish.py [xxx.json] --Patch and verify all the setup options defined in xxx.json
python redfish.py [directoryname] --Find all the json files in specified directory, and run all the tests in those json files
python redfish.py [checkregistry] --check whether registry.json and setup baseline is aligned
python redfish.py [init]     --cleanup teststatus
"""

# list of options that is dependent by oters
INCLUDE_LIST = {
    "BootFailPolicy":"Boot Retry",
    "PcieCorErrLimitEn":"Enabled",
    "SvrMngmntFrb2Enable":"Enabled",
    "OSBootWDTimer":"Enabled",
    "MemBootHealthCheck":"Manual",
    "EnableBiosSsaRMT":"Enabled",
    "BiosSsaStepSizeOverride":"Enabled",
    "leakyBktTimeWindow":"Enabled",
    "StaticTurbo":"Manual",
    "PartialMirrorUefi":"Enabled",
    "NetworkProtocol":"UEFI:IPv4/IPv6",
    "PwrPerfTuning":"BIOS Controls EPB"
}

DEP_EXCLUDE_LIST = [

]

class RfishPrompt:
    wrong_value = "The value Enable for the property Attributes/{} is not in the list of acceptable values"
    hidden_error = "The property Attributes/{} cannot be modified because the value for the property Attributes/{} is {Disabled}"

