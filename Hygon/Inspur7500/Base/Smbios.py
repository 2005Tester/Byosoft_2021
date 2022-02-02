import datetime
import re
import os
import time
import shutil
import difflib
import logging
import pyautogui
from bs4 import BeautifulSoup
from serial.win32 import SetupComm
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from Inspur7500.BaseLib import SshLib
from batf.SutInit import Sut



def get_smbios():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT_CN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Msg.BOOT_MODE_CN], 6, "UEFI")
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(4)
    assert SetUpLib.boot_os_from_bm()
    types=[0,1,2,3,4,7,8,9,11,13,16,17,19,20,38,39,41,127]
    shutil.rmtree('Inspur7500/Tools/SMBIOS')
    os.mkdir('Inspur7500/Tools/SMBIOS')
    SshLib.execute_command_limit(Sut.OS_SSH,'rm -rf SMBIOS;mkdir SMBIOS')
    while True:
        for type in types:
            type_file='type'+str(type)+'.txt'
            SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t {0} > SMBIOS/{1}".format(type, type_file))
            type_file_linux='SMBIOS/'+type_file
            SshLib.sftp_download_file(Sut.OS_SFTP,type_file_linux,'Inspur7500/Tools/SMBIOS/{0}'.format(type_file))
            for root, dirs, files in os.walk('Inspur7500/Tools/SMBIOS'):
                if len(files)==len(types):
                    return True

     
    
def get_bios_date():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN_CN)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    version=re.findall(r'Release Version +([0-9\.]+) ',data)
    date=re.findall(r'BIOS Build Time +([0-9\-]+) ',data)
    return version,date



def check_diff(log1, log2):
    logging.info("Comparing {0} and {1}".format(log1, log2))
    try:
        with open(log1, 'r') as f:
            content_log1 = f.read().splitlines()
        with open(log2, 'r') as f:
            content_log2 = f.read().splitlines()
    except FileNotFoundError:
        logging.error("Please check whether log file exists.")
        return True
    d = difflib.Differ()
    diffs = list(d.compare(content_log1, content_log2))
    res = []
    for diff in diffs:
        if not re.search("^\s", diff):
            res.append(diff)
    return res