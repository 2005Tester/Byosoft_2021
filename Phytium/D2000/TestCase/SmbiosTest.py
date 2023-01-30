# coding='utf-8'
import re
import os
import time
import logging
import shutil, difflib
from D2000.BaseLib import BmcLib, SetUpLib, SshLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from batf.Report import stylelog
from batf import core
from batf.SutInit import Sut


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


@core.test_case(('401', '[TC401]Check Smbios', '对比SMBIOS信息'))
def get_smbios():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_os_from_bm()
        types = [0, 1, 2, 3, 4, 7, 8, 9, 11, 13, 16, 17, 19, 20, 38, 39, 41, 127]
        shutil.rmtree('D2000/Tools/SMBIOS')
        os.mkdir('D2000/Tools/SMBIOS')
        SshLib.execute_command_limit(Sut.OS_SSH, 'rm -rf SMBIOS;mkdir SMBIOS')
        for type in types:
            type_file = 'type' + str(type) + '.txt'
            SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t {0} > SMBIOS/{1}".format(type, type_file))
            type_file_linux = 'SMBIOS/' + type_file
            SshLib.sftp_download_file(Sut.OS_SFTP, type_file_linux, 'D2000/Tools/SMBIOS/{0}'.format(type_file))
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        data = SetUpLib.get_data(2)
        version_setup = re.findall(r'Release Version +([0-9\.]+) ', data)
        date_setup = re.findall(r'BIOS Build Time +([0-9\-/]+) ', data)
        with open('D2000/Tools/SMBIOS/type0.txt', 'r') as f:
            content_log1 = f.read()
            version_type0 = re.findall(r'Version: ([0-9\.]+)', content_log1)
            date_type0 = re.findall(r'Release Date: ([0-9\-/]+)', content_log1)
            if version_setup == version_type0 and date_setup == date_type0:
                logging.info('type 0 BIOS版本，日期与setup显示一致')
            else:
                stylelog.fail(
                    'type 0显示BIOS版本：{0}，setup下BIOS版本：{1},type 0显示BIOS发布日期：{2}，setup下BIOS发布日期：{3}'.format(version_type0,
                                                                                                         version_setup,
                                                                                                         date_type0,
                                                                                                         date_setup))
                wrong_msg.append(
                    'type 0显示BIOS版本：{0}，setup下BIOS版本：{1},type 0显示BIOS发布日期：{2}，setup下BIOS发布日期：{3}'.format(version_type0,
                                                                                                         version_setup,
                                                                                                         date_type0,
                                                                                                         date_setup))
                count += 1
        types = [1, 2, 3, 4, 7, 8, 9, 11, 13, 16, 17, 19, 20, 38, 39, 41, 127]
        for i in types:
            differs = check_diff('{0}type{1}.txt'.format(SutConfig.Env.SMBIOS, str(i)),
                                 'D2000/Tools/SMBIOS/type{0}.txt'.format(str(i)))
            if len(differs) == 0:
                pass
            else:
                for differ in differs:
                    logging.info(differ)
                count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
