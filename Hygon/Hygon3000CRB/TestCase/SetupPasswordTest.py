import logging
import time
from batf.Report import ReportGen
from batf.SutInit import Sut
from Hygon3000CRB.Base import SetUpPassword,HDDPassword
from Hygon3000CRB.BaseLib import BmcLib
from batf import core



'''
SetUpPassword  case  编号：701~800               
'''



# @core.test_case(('701', '[TC701]Password Security 001', '设置密码测试，未设置管理员密码直接设置用户密码，设置失败测试'))
# def password_security_001():
#     try:
#         assert SetUpPassword.password_security_001()
#         return core.Status.Pass
#
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail



@core.test_case(('701', '[TC701]Password Security 001', '设置密码长度测试，密码长度小于最少字符数，修改失败测试'))
def password_security_001():
    try:
        assert SetUpPassword.password_security_001()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('702', '[TC702]Password Security 002', '设置密码长度测试，密码长度等于最少字符数，修改成功测试'))
def password_security_002():
    try:
        assert SetUpPassword.password_security_002()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('703', '[TC703]Password Security 003', '设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试'))
def password_security_003():
    try:
        assert SetUpPassword.password_security_003()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('704', '[TC704]Password Security 004', '设置密码长度测试，密码长度最大字符数，修改成功测试'))
def password_security_004():
    try:
        assert SetUpPassword.password_security_004()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('705', '[TC705]Password Security 005', '设置密码长度测试，密码长度超出最大字符数，修改失败测试'))
def password_security_005():
    try:
        assert SetUpPassword.password_security_005()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('706', '[TC706]Password Security 006', '设置密码字符类型测试，只有1种字符类型密码测试'))
def password_security_006():
    try:
        assert SetUpPassword.password_security_006()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('707', '[TC707]Password Security 007', '设置密码字符类型测试，2种字符类型密码测试'))
def password_security_007():
    try:
        assert SetUpPassword.password_security_007()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('708', '[TC708]Password Security 008', '设置密码字符类型测试，3种字符类型密码测试'))
def password_security_008():
    try:
        assert SetUpPassword.password_security_008()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('709', '[TC709]Password Security 009', '设置密码字符类型测试，4种字符类型密码测试'))
def password_security_009():
    try:
        assert SetUpPassword.password_security_009()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('710', '[TC710]Password Security 010', '输入错误密码3次内，提示报错，并可以再次输入测试；输错3次后不允许在输入密码测试；输入错误密码超出阈值测试'))
def password_security_010():
    try:
        assert SetUpPassword.password_security_010()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('711', '[TC711]Password Security 011', '输入错误密码次数测试，阈值内连续输入错误密码后输入正确密码测试'))
def password_security_011():
    try:
        assert SetUpPassword.password_security_011()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('712', '[TC712]Password Security 012', '输入错误密码次数测试，超出阈值锁定输入界面，重启后不影响下一次登录'))
def password_security_012():
    try:
        assert SetUpPassword.password_security_012()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail



# @core.test_case(('714', '[TC714]Password Security 014', '输入错误密码等待时间测试，超出阈值锁定时间测试,锁定时间结束，输入正确密码可以进入'))
# def password_security_014():
#     try:
#         assert SetUpPassword.password_security_014()
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail



@core.test_case(('713', '[TC713]Password Security 013', '输入用户密码进入setup测试，进入setup可以删除用户密码'))
def password_security_013():
    try:
        assert SetUpPassword.password_security_013()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('714', '[TC714]Password Security 014', '输入用户密码进入setup测试，进入setup可以修改用户密码'))
def password_security_014():
    try:
        assert SetUpPassword.password_security_014()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('715', '[TC715]Password Security 015', '密码不能明文显示，任意密码用*代替字符测试'))
def password_security_015():
    try:
        assert SetUpPassword.password_security_015()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('716', '[TC716]Password Security 016', '密码修改验证旧密码测试，输入错误旧密码，不能修改密码'))
def password_security_016():
    try:
        assert SetUpPassword.password_security_016()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('717', '[TC717]Password Security 017', '密码修改验证新密码测试，新密码确认时，输入错误新密码，修改失败测试'))
def password_security_017():
    try:
        assert SetUpPassword.password_security_017()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('718', '[TC718]Password Security 018', '历史密码5次范围内重复修改无效，超过5次后可以修改为5次前的密码测试'))
def password_security_018():
    try:
        assert SetUpPassword.password_security_018()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('719', '[TC719]Password Security 019', '开机密码测试，打开开机密码，进入系统需要输入开机密码测试'))
def password_security_019():
    try:
        assert SetUpPassword.password_security_019()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('720','[TC720]Password Security 020','密码有效期测试'))
def password_security_020():
    try:
        assert SetUpPassword.password_security_020()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('721','[TC721]Password Security 021','输入密码时按ESC测试'))
def password_security_021():
    try:
        assert SetUpPassword.password_security_021()
        return core.Status.Pass
    except Exception as e:
        SetUpPassword.del_password('Admin@21', 'Users@21')
        logging.error(e)
        return core.Status.Fail