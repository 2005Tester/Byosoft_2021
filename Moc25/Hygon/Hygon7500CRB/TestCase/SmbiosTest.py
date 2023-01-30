import logging
import time
from batf.Report import ReportGen
from batf.SutInit import Sut
from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig
from Hygon7500CRB.BaseLib import BmcLib,SetUpLib
from Hygon7500CRB.Base import Smbios

import re


'''
Smbios  Case  编号：101~200


'''





def get_smbios():
    tc=('101', '[TC101]get SMBIOS Message', 'get SMBIOS Message')
    result=ReportGen.LogHeaderResult(tc)
    try:
        assert Smbios.get_smbios()
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail(capture=True)
        return


def smbios():
    
    tc=('102','[TC102]SMBIOS Type 0','检查 SMBIOS Type 0')
    result=ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page('PCIE Configuration')
        SetUpLib.send_key(Key.LEFT)
        data=SetUpLib.get_data(2)
        version_setup=re.findall(r'Release Version +([0-9\.]+) ',data)
        date_setup=re.findall(r'BIOS Build Time +([0-9\/]+) ',data)
        with open('Hygon/Tools/SMBIOS/type0.txt', 'r') as f:
            content_log1 = f.read()
            version_type0=re.findall(r'Version: ([0-9\.]+)', content_log1)
            date_type0=re.findall(r'Release Date: ([0-9\/]+)', content_log1)
            if version_setup==version_type0 and date_setup==date_type0:
                logging.info('type 0 BIOS版本，日期与setup显示一致')
                result.log_pass()
            else:
                logging.info('type 0显示BIOS版本：{0}，setup下BIOS版本：{1},type 0显示BIOS发布日期：{2}，setup下BIOS发布日期：{3}'.format(version_type0,version_setup,date_type0,date_setup))
                result.log_fail()
    except Exception as e:
        logging.error(e)
        result.log_fail(capture=True)

    
    
    types=[1,2,3,4,7,9,11,13,16,17,19,38,39,41,127]
    count=1
    for i in types:
        tc=('{0}'.format(str(count+102)),'[TC{0}]SMBIOS Type {1}'.format(str(count+102),i),'检查 SMBIOS Type {0}'.format(i))
        result = ReportGen.LogHeaderResult(tc)
        try:
            differs=Smbios.check_diff('{0}type{1}.txt'.format(SutConfig.Env.SMBIOS,str(i)),'Hygon/Tools/SMBIOS/type{0}.txt'.format(str(i)))
            if len(differs)==0:
                result.log_pass()
            else:
                for differ in differs:
                    logging.info(differ)
                result.log_fail()
                    
                    

        except Exception as e:
            logging.error(e)
            result.log_fail(capture=True)
            return
        count+=1


