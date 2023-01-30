# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
SetUpPassword  case  编号:701~800               
'''


@core.test_case(('701', '[TC701]Password Security 001', '设置密码测试，未设置管理员密码直接设置用户密码，设置失败测试'))
def password_security_001():
    """
    Name:   直接设置用户密码

    Steps:  1.不设置管理员密码直接设置用户密码

    Result: 1.设置失败
    """
    try:
        assert SetUpPassword.password_security_001()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('702', '[TC702]Password Security 002', '设置密码长度测试，密码长度小于最少字符数，修改失败测试'))
def password_security_002():
    """
    Name:   设置密码长度小于最少字符

    Steps:  1.设置管理员密码长度小于最少字符
            2.设置符合长度，复杂度的管理员密码
            3.设置用户密码长度小于最少字符

    Result: 1.设置失败
            2.设置成功
            3.设置失败
    """
    try:
        assert SetUpPassword.password_security_002()
        return core.Status.Pass


    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('703', '[TC703]Password Security 003', '设置密码长度测试，密码长度等于最少字符数，修改成功测试'))
def password_security_003():
    """
    Name:   设置密码长度等于最少字符

    Steps:  1.设置管理员密码长度等于最少字符
            2.设置用户密码长度等于最少字符
            3.重启输入正确的管理员密码进入Setup
            4.删除密码
    Result: 1.管理员密码设置成功
            2.用户密码设置成功
            3.成功进入SetUp
    """
    try:
        assert SetUpPassword.password_security_003()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('704', '[TC704]Password Security 004', '设置密码长度测试，密码长度大于最少字符数，小于最大字符数，修改成功测试'))
def password_security_004():
    """
    Name:   设置密码长度大于最少字符小于最大字符

    Steps:  1.设置管理员密码长度大于最少字符小于最大字符
            2.设置用户密码长度大于最少字符小于最大字符
            3.重启输入正确的管理员密码进入Setup
            4.删除密码

    Result: 1.密码设置成功
            2.密码设置成功
            3.成功进入SetUp

    """
    try:
        assert SetUpPassword.password_security_004()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('705', '[TC705]Password Security 005', '设置密码长度测试，密码长度最大字符数，修改成功测试'))
def password_security_005():
    """
    Name:   设置密码长度最大字符

    Steps:  1.设置管理员密码长度最大字符
            2.设置用户密码长度最大字符
            3.重启输入正确的管理员密码进入Setup
            4.删除密码

    Result: 1.密码设置成功
            2.密码设置成功
            3.成功进入SetUp
    """
    try:
        assert SetUpPassword.password_security_005()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('706', '[TC706]Password Security 006', '设置密码长度测试，密码长度超出最大字符数，修改失败测试'))
def password_security_006():
    """
    Name:   设置密码长度大于最大字符

    Steps:  1.设置管理员密码长度大于最大字符
            2.设置用户密码长度大于最大字符
            3.重启输入最大字符长度的管理员密码
            4.删除密码

    Result: 1.超过最大长度的密码输不进去
            2.超过最大长度的密码输不进去
            3.成功进入SetUp

    """
    try:
        assert SetUpPassword.password_security_006()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('707', '[TC707]Password Security 007', '设置密码字符类型测试，只有1种字符类型密码测试'))
def password_security_007():
    """
    Name:   设置密码只有一种字符类型

    Steps:  1.设置管理员密码只有数字，只有大写字母，只有小写字母，只有特殊字符
            2.设置用户密码只有数字，只有大写字母，只有小写字母，只有特殊字符

    Result: 1/2.设置不成功
    """
    try:
        assert SetUpPassword.password_security_007()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('708', '[TC708]Password Security 008', '设置密码字符类型测试，2种字符类型密码测试'))
def password_security_008():
    """
    Name:   设置密码2种字符类型

    Steps:  1.设置管理员密码数字加大写字母，数字加小写字母，数字加特殊字符，大写字母加小写字母，大写字母加特殊字符，小写字母加特殊字符
            2.设置用户密码数字加大写字母，数字加小写字母，数字加特殊字符，大写字母加小写字母，大写字母加特殊字符，小写字母加特殊字符

    Result: 1.设置不成功
            2.设置不成功
    """
    try:
        assert SetUpPassword.password_security_008()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('709', '[TC709]Password Security 009', '设置密码字符类型测试，3种字符类型密码测试'))
def password_security_009():
    """
    Name:   设置密码3种字符类型

    Steps:  1.设置管理员密码数字加大写字母加小写字母，数字加大写字母加特殊字符，数字加小写字母加特殊字符，大写字母加小写字每加特殊字符
            2.设置用户密码数字加大写字母加小写字母，数字加大写字母加特殊字符，数字加小写字母加特殊字符，大写字母加小写字每加特殊字符

    Result: 1.设置不成功
            2.设置不成功
    """
    try:
        assert SetUpPassword.password_security_009()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('710', '[TC710]Password Security 010', '设置密码字符类型测试，4种字符类型密码测试'))
def password_security_010():
    """
    Name:   设置密码4种字符类型

    Steps:  1.设置管理员密码数字加大写字母加小写字母加特殊字符
            2.设置用户密码数字加大写字母加小写字母加特殊字符
            3.删除密码

    Result: 1/2.密码设置成功
    """
    try:
        assert SetUpPassword.password_security_010()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('711', '[TC711]Password Security 011', '输入错误密码3次内，提示报错，并可以再次输入测试；输错3次后不允许在输入密码测试；输入错误密码超出阈值测试'))
def password_security_011():
    """
    Name:   输错密码

    Steps:  1.设置管理员密码
            2.重启，POST校验密码输错密码三次

    Result: 2.输错密码三次，提示锁定，不允许输入密码
    """
    try:
        assert SetUpPassword.password_security_011()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('712', '[TC712]Password Security 012', '输入错误密码次数测试，阈值内连续输入错误密码后输入正确密码测试'))
def password_security_012():
    """
    Name:   输错密码两次后输入正确密码

    Steps:  1.POST校验密码输错两次密码后输入正确密码

    Result: 2.密码正确成功进入SetUp
    """
    try:
        assert SetUpPassword.password_security_012()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('713', '[TC713]Password Security 013', '输入错误密码次数测试，超出阈值锁定输入界面，重启后不影响下一次登录'))
def password_security_013():
    """
    Name:   输错密码3次后，不影响下次登录

    Steps:  1.POST校验密码输错3次
            2.重启输入正确密码

    Result: 1.提示锁住
            2.成功进入SetUp
    """
    try:
        assert SetUpPassword.password_security_013()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('714', '[TC714]Password Security 014', '输入错误密码等待时间测试，超出阈值锁定时间测试,锁定时间结束，输入正确密码可以进入'))
def password_security_014():
    """
    Name:   密码锁定时间

    Steps:  1.设置密码锁定时间60s
            2.SetUp下输错密码三次
            3.锁定时间结束
            4.POST校验密码输错三次
            5.锁定时间结束输入正确密码
            6.设置密码锁定时间180s
            7.POST校验密码输错三次
            8.锁定时间结束输入正确密码
            9.SetUp下输错密码三次
            10.删除密码

    Result: 2.提示锁定60s
            3.锁定时间结束可以继续输入密码
            4.提示锁定60s
            5.锁定时间结束输入正确密码成功进入SetUp
            7.提示锁定180s
            8.成功进入SetUp
            9.提示锁定180s
    """

    try:
        assert SetUpPassword.password_security_014()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('715', '[TC715]Password Security 015', '输入用户密码进入setup测试，进入setup不可以删除用户密码'))
def password_security_015():
    """
    Name:   用户密码登录

    Steps:  1.设置管理员，用户密码
            2.用户密码登录SetUp

    Result: 2.登录类型为用户，不能修改选项，不能删除用户密码
    """
    try:
        assert SetUpPassword.password_security_015()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('716', '[TC716]Password Security 016', '输入用户密码进入setup测试，进入setup可以修改用户密码'))
def password_security_016():
    """
    Name:   用户密码登录修改用户密码

    Steps:  1.用户密码登录SetUp，修改用户密码

    Result: 1.用户密码修改成功
    """
    try:
        assert SetUpPassword.password_security_016()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('717', '[TC717]Password Security 017', '密码不能明文显示，任意密码用*代替字符测试'))
def password_security_017():
    """
    Name:   输入的密码不能明文显示

    Steps:  1.POST校验密码输入的密码，显示*
    """

    try:
        assert SetUpPassword.password_security_017()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('718', '[TC718]Password Security 018', '密码修改验证旧密码测试，输入错误旧密码，不能修改密码'))
def password_security_018():
    """
    Name:   修改密码输入错误的旧密码

    Steps:  1.修改管理员密码时输入错误的旧密码

    Result: 1.密码校验失败
    """
    try:
        assert SetUpPassword.password_security_018()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('719', '[TC719]Password Security 019', '密码修改验证新密码测试，新密码确认时，输入错误新密码，修改失败测试'))
def password_security_019():
    """
    Name    修改密码时新密码与确认密码不一致

    Steps:  1.修改管理员密码，新密码确认密码输入不一致
            2.修改用户密码，新密码确认密码输入不一致
            3.删除密码
    Result: 1/2.修改失败

    """
    try:
        assert SetUpPassword.password_security_019()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('720', '[TC720]Password Security 020', '历史密码5次范围内重复修改无效，超过5次后可以修改为5次前的密码测试'))
def password_security_020():
    """
    Name:   历史密码5次无法设置

    Steps:  1.依次修改管理员密码为a,b,c,d,e
            2.修改管理员密码为a
            3.修改管理员密码为f
            4.修改管理员密码为a
            5.依次修改用户密码为a,b,c,d,e
            6.修改用户密码为a
            7.修改用户密码为f
            8.修改用户密码为a
            9.删除密码

    Result: 2.修改失败，提示与前5次密码相同
            4.修改成功
            6.修改失败，提示与前5次密码相同
            8.修改成功

    """
    try:
        assert SetUpPassword.password_security_020()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('721', '[TC721]Password Security 021', '开机密码测试，打开开机密码，进入系统需要输入开机密码测试'))
def password_security_021():
    """
    Name:   开机密码

    Steps:  1.设置管理员密码，用户密码，打开开机密码
            2.输入管理员密码进入启动菜单，进入系统
            3.输入用户密码进入启动菜单，进入系统
            4.关闭开机密码
    Result: 2/3.成功进入系统
            4.进入系统不需要输入密码
    """
    try:
        assert SetUpPassword.password_security_021()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('722', '[TC722]Password Security 022', '密码有效期测试'))
def password_security_022():
    """
    Name:   密码有效期

    Steps:  1.设置管理员，用户密码，设置密码有效期7天,开机密码打开
            2.修改日期6天23时50分后
            3.分别检查POST阶段，SetUp下用户密码，管理员密码是否过期
            4.修改日期7天1分后
            5.分别检查自行启动，POST阶段，SetUp下用户密码，管理员密码是否过期
            6.设置密码有效期30天
            7.修改日期29天23时50分后
            8.分别检查POST阶段，SetUp下用户密码，管理员密码是否过期
            9.修改日期30天1分后
            10.分别检查自行启动，POST阶段，SetUp下用户密码，管理员密码是否过期
            11.设置密码有效期为无限期
            12.修改日期为最小日期，最大日期
            13.SetUp下检查管理员，用户密码是否过期

    Result: 3.管理员，用户密码都没有过期
            5.管理员，用户密码都过期
            8.管理员，用户密码都没有过期
            10.管理员，用户密码都过期
            13.管理员，用户密码都没有过期

    """
    try:
        assert SetUpPassword.password_security_022()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('723', '[TC723]Password Security 023', '输入密码时按ESC测试'))
def password_security_023():
    """
    Name:   输入密码按ESC

    Steps:  1.设置管理员密码
            2.POST阶段校验密码时按ESC

    Result: 2.没有跳过密码
    """
    try:
        assert SetUpPassword.password_security_023()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('724', '[TC724]Password Security 024', '密码删除测试，删除管理员密码，用户密码也被删除测试'))
def password_security_024():
    """
    Name:   删除管理员密码，用户密码同时被删除

    Steps:  1.设置管理员用户密码
            2.删除管理员密码

    Result: 2.管理员用户密码都被删除
    """
    try:
        assert SetUpPassword.password_security_024()

        return core.Status.Pass
    except Exception as e:

        logging.error(e)
        return core.Status.Fail


@core.test_case(('725', '[TC725]Password Security 025', '密码删除测试，删除用户密码，只删除用户密码测试'))
def password_security_025():
    """
    Name:   删除用户密码

    Steps:  1.设置管理员用户密码
            2.删除用户密码
            3.POST校验密码输入用户密码
            4.删除密码

    Result: 2.只有用户密码被删除
            3.提示密码错误


    """
    try:
        assert SetUpPassword.password_security_025()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('726', '[TC726]Password Security 026', '密码检查'))
def password_security_026():
    """
    Name:   密码检查

    Steps:  1.SetUp下打开密码检查，关闭密码复杂度，设置密码长度为8，重试次数为3
            2.设置不符合密码长度的管理员，用户密码
            3.管理员密码，用户密码设置相同测试
            4.输错密码3次
            5.设置密码长度为20，重试次数为10
            6.设置不符合密码长度的管理员，用户密码
            7.管理员密码，用户密码设置相同测试
            8.输错密码10次
            9.打开密码复杂度，设置密码长度10，重试次数5
            10.设置不符合密码长度的管理员用户名密码
            11.设置不符合复杂度要求的管理员用户密码
            12.输错密码5次
            13.删除密码

    Result: 2/3/6/7/10/11.密码设置失败
            4/8/12.提示密码锁住
    """
    try:
        assert SetUpPassword.password_security_026()
        return core.Status.Pass
    except Exception as e:
        from Inspur7500.BaseLib import SetUpLib
        SetUpPassword._go_to_setup()
        SetUpLib.default_save()
        logging.error(e)
        return core.Status.Fail


@core.test_case(('727', '[TC727]Password Security 027', '管理员密码和用户密码不允许设置相同测试'))
def password_security_027():
    """
    Name:   管理员用户密码设置相同

    Steps:  1.设置管理员密码
            2.设置用户密码和管理员密码相同

    Result: 2.设置失败
    """
    try:
        assert SetUpPassword.password_security_027()
        BmcLib.power_off()
        time.sleep(5)
        return core.Status.Pass
    except Exception as e:
        BmcLib.power_off()
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail
