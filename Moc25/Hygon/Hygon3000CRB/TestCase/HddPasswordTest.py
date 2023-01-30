#coding='utf-8'
import logging
import time
from batf.Report import ReportGen
from Hygon3000CRB.Base import SetUpPassword,HDDPassword
from Hygon3000CRB.BaseLib import BmcLib
from batf import core



'''
HddPassword  case 编号：801~900
'''



@core.test_case(('801', '[TC801]HDD Password Security 001','设置硬盘密码长度小于最少字符数，大于最大字符，设置密码时两次输入不一致，只有数字，只有字母，只有特殊符号，数字和特殊符号，字母和特殊符号设置失败测试'))
def hdd_password_001(hddorder=1):
    try:
        BmcLib.power_off()
        time.sleep(10)
        assert HDDPassword.hdd_password_001(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('802', '[TC802]HDD Password Security 002', '设置硬盘密码长度等于最小字符数，复杂度最小，设置成功测试'))
def hdd_password_002(hddorder=1):
    try:
        assert HDDPassword.hdd_password_002(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('803', '[TC803]HDD Password Security 003', '设置硬盘密码长度等于最小字符数，复杂度最大，设置成功测试'))
def hdd_password_003(hddorder=1):
    try:
        assert HDDPassword.hdd_password_003(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('804', '[TC804]HDD Password Security 004', '设置硬盘密码长度大于最小字符数，小于最大字符数，设置成功测试'))
def hdd_password_004(hddorder=1):
    try:
        assert HDDPassword.hdd_password_004(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('805', '[TC805]HDD Password Security 005', '设置硬盘密码长度等于最大字符数，复杂度最小，设置成功测试'))
def hdd_password_005(hddorder=1):
    try:
        assert HDDPassword.hdd_password_005(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('806', '[TC806]HDD Password Security 006', '设置硬盘密码长度等于最大字符数，复杂度最大，设置成功测试'))
def hdd_password_006(hddorder=1):
    try:
        assert HDDPassword.hdd_password_006(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('807', '[TC807]HDD Password Security 007', '禁用硬盘密码测试'))
def hdd_password_007(hddorder=1):
    try:
        assert HDDPassword.hdd_password_007(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('808', '[TC808]HDD Password Security 008', '修改硬盘密码测试，修改为最小长度，最小复杂度，修改成功测试'))
def hdd_password_008(hddorder=1):
    try:
        assert HDDPassword.hdd_password_008(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('809', '[TC809]HDD Password Security 009', '修改硬盘密码测试，修改为最大长度，最大复杂度，修改成功测试'))
def hdd_password_009(hddorder=1):
    try:
        assert HDDPassword.hdd_password_009(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('810', '[TC810]HDD Password Security 010', '修改硬盘密码测试，修改为符合长度要求，不符合复杂度要求；符合复杂度要求，不符合长度要求；新密码和确认密码不同，修改失败测试'))
def hdd_password_010(hddorder=1):
    try:
        assert HDDPassword.hdd_password_010(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('811', '[TC811]HDD Password Security 011', '设置硬盘密码进入系统测试'))
def hdd_password_011(hddorder=1):
    try:
        assert HDDPassword.hdd_password_011(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('812', '[TC812]HDD Password Security 012', '硬盘密码输错测试'))
def hdd_password_012(hddorder=1):
    try:
        assert HDDPassword.hdd_password_012(hddorder)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('813', '[TC813]HDD Password Security 013', '硬盘密码输入时按ESC测试'))
def hdd_password_013(hddorder=1):
    try:
        assert HDDPassword.hdd_password_013(hddorder)
        BmcLib.power_off()
        time.sleep(5)
        return core.Status.Pass
    except Exception as e:
        BmcLib.power_off()
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('814', '[TC814]HDD Password Security 014', '多硬盘密码测试'))
def hdd_password_014():
    try:
        assert HDDPassword.hdd_password_014()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('815', '[TC815]HDD Password Security 015', '多硬盘密码输错测试'))
def hdd_password_015():
    try:
        assert HDDPassword.hdd_password_015()
        BmcLib.power_off()
        return core.Status.Pass
    except Exception as e:
        BmcLib.power_off()
        logging.error(e)
        return core.Status.Fail



@core.test_case(('816', '[TC816]HDD Password Security 016', '多硬盘密码输入时按ESC测试'))
def hdd_password_016():
    try:
        assert HDDPassword.hdd_password_016()
        time.sleep(3)
        BmcLib.power_off()
        time.sleep(5)
        return core.Status.Pass
    except Exception as e:
        time.sleep(3)
        BmcLib.power_off()
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('817', '[TC817]HDD Password Security 017', '多硬盘密码进入系统测试'))
def hdd_password_017():
    try:
        assert HDDPassword.hdd_password_017()
        time.sleep(3)
        BmcLib.power_off()
        time.sleep(5)
        return core.Status.Pass
    except Exception as e:
        time.sleep(3)
        HDDPassword.del_hdd_password_two()
        BmcLib.power_off()
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail