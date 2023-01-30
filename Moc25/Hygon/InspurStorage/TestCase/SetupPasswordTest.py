import logging
import time
from batf.Report import ReportGen
from batf.SutInit import Sut
from InspurStorage.Base import SetUpPassword
from InspurStorage.BaseLib import BmcLib
from batf import core



'''
SetUpPassword  case  编号：701~800               
'''



@core.test_case(('701', '[TC701]Password Security 001', '设置密码测试，未设置管理员密码直接设置用户密码，可以设置测试'))
def password_security_001():
    try:
        assert SetUpPassword.password_security_001()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('702', '[TC702]Password Security 002', '设置密码长度测试，密码长度小于最少字符数，修改失败测试'))
def password_security_002():
    try:
        assert SetUpPassword.password_security_002()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('703', '[TC703]Password Security 003', '设置密码长度测试，密码长度等于最少字符数，修改成功测试'))
def password_security_003():
    try:
        assert SetUpPassword.password_security_003()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('704', '[TC704]Password Security 004', '设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试'))
def password_security_004():
    try:
        assert SetUpPassword.password_security_004()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('705', '[TC705]Password Security 005', '设置密码长度测试，密码长度最大字符数，修改成功测试'))
def password_security_005():
    try:
        assert SetUpPassword.password_security_005()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('706', '[TC706]Password Security 006', '设置密码长度测试，密码长度超出最大字符数，修改失败测试'))
def password_security_006():
    try:
        assert SetUpPassword.password_security_006()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('707', '[TC707]Password Security 007', '密码不一致测试'))
def password_security_007():
    try:
        assert SetUpPassword.password_security_007()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('708', '[TC708]Password Security 008', '密码输错测试'))
def password_security_008():
    try:
        assert SetUpPassword.password_security_008()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('709', '[TC709]Password Security 009', '用户更改密码测试'))
def password_security_009():
    try:
        assert SetUpPassword.password_security_009()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('710', '[TC710]Password Security 010', '管理员，用户密码进入系统测试'))
def password_security_010():
    try:
        assert SetUpPassword.password_security_010()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('711', '[TC711]Password Security 011', '清除用户密码'))
def password_security_011():
    try:
        assert SetUpPassword.password_security_011()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

