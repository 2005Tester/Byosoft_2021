# -*- encoding=utf8 -*-
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
HddPassword  case 编号:801~900
'''


@core.test_case(('801', '[TC801]HDD Password Security 001','设置硬盘密码长度小于最少字符数，大于最大字符，设置密码时两次输入不一致，只有数字，只有字母，只有特殊符号，数字和特殊符号，字母和特殊符号设置失败测试'))
def hdd_password_001():
    """
    Name:  硬盘密码负面测试

    Steps:  1.设置硬盘密码长度小于最少字符数，满足复杂度要求
            2.设置硬盘密码长度大于最大字符数，满足复杂度要求
            3.设置密码时确认密码与输入密码不一致
            4.设置硬盘密码长度符合要求，只有数字
            5.设置硬盘密码长度符合要求，只有字母
            6.设置硬盘密码长度符合要求，只有特殊符号
            7.设置硬盘密码长度符合要求，数字和特殊符号
            8.设置硬盘密码长度符合要求，字母和特殊符号

    Result: 1/2/3/4/5/6/7/8 设置不成功
    """
    try:
        assert HDDPassword.hdd_password_001()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('802', '[TC802]HDD Password Security 002', '设置硬盘密码长度等于最小字符数，复杂度最小，设置成功测试'))
def hdd_password_002():
    """
    Name:   设置硬盘密码长度最小，复杂度最小

    Steps:  1.设置硬盘密码长度最小，复杂度最小
            2.关机，开机，输入硬盘密码进入SetUp
            3.删除硬盘密码

    Result: 1.硬盘密码设置成功
            2.输入硬盘密码成功进入SetUp
    """
    try:
        assert HDDPassword.hdd_password_002()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('803', '[TC803]HDD Password Security 003', '设置硬盘密码长度等于最小字符数，复杂度最大，设置成功测试'))
def hdd_password_003():
    """
    Name:   设置密码长度最小，复杂度最大

    Steps:  1.设置硬盘密码长度最小，复杂度最大
            2.关机，开机，输入硬盘密码进入SetUp
            3.删除硬盘密码

    Result: 1.硬盘密码设置成功
            2.输入硬盘密码成功进入SetUp
    """
    try:
        assert HDDPassword.hdd_password_003()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('804', '[TC804]HDD Password Security 004', '设置硬盘密码长度大于最小字符数，小于最大字符数，设置成功测试'))
def hdd_password_004():
    """
    Name:   设置硬盘密码长度大于最小字符，小于最大字符

    Steps:  1.设置硬盘密码长度大于最小字符数,小于最大字符数
            2.关机，开机输入硬盘密码进入SetUp
            3.删除硬盘密码

    Result: 1.硬盘密码设置成功
            2.输入硬盘密码成功进入SetUp
    """
    try:
        assert HDDPassword.hdd_password_004()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('805', '[TC805]HDD Password Security 005', '设置硬盘密码长度等于最大字符数，复杂度最小，设置成功测试'))
def hdd_password_005():
    """
    Name:   设置硬盘密码长度等于最大字符，复杂度最小

    Steps:  1.设置硬盘密码长度等于最大字符，复杂度最小
            2.关机，开机输入硬盘密码进入SetUp
            3.删除硬盘密码
    Result: 1.硬盘密码设置成功
            2.输入硬盘密码成功进入SetUp
    """
    try:
        assert HDDPassword.hdd_password_005()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('806', '[TC806]HDD Password Security 006', '设置硬盘密码长度等于最大字符数，复杂度最大，设置成功测试'))
def hdd_password_006():
    """
    Name:   设置硬盘密码长度等于最大字符，复杂度最大

    Steps:  1.设置硬盘密码长度等于最大字符，复杂度最大
            2.关机，开机输入硬盘密码进入SetUp
            3.删除硬盘密码
    Result: 1.硬盘密码设置成功
            2.输入硬盘密码成功进入SetUp
    """
    try:
        assert HDDPassword.hdd_password_006()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('807', '[TC807]HDD Password Security 007', '禁用硬盘密码测试'))
def hdd_password_007():
    """
    Name:   禁用硬盘密码

    Steps:  1.设置硬盘密码
            2.禁用硬盘密码输入错误的硬盘密码
            3.禁用硬盘密码输入正确的硬盘密码

    Result: 2.硬盘密码禁用失败
            3.硬盘密码禁用成功

    """
    try:
        assert HDDPassword.hdd_password_007()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('808', '[TC808]HDD Password Security 008', '修改硬盘密码测试，修改为最小长度，最小复杂度，修改成功测试'))
def hdd_password_008():
    """
    Name:   修改硬盘密码最小长度，最小复杂度

    Steps:  1.设置硬盘密码
            2.修改硬盘密码为最小长度，最小复杂度
            3.关机，开机POST校验硬盘密码输入修改前的密码
            4.输入修改后的硬盘密码
            5.禁用硬盘密码输入修改前的硬盘密码
            6.禁用硬盘密码输入修改后的硬盘密码

    Result: 2.硬盘密码修改成功
            3.提示硬盘密码错误
            4.硬盘密码校验成功
            5.禁用硬盘密码失败
            6.禁用硬盘密码成功

    """
    try:
        assert HDDPassword.hdd_password_008()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('809', '[TC809]HDD Password Security 009', '修改硬盘密码测试，修改为最大长度，最大复杂度，修改成功测试'))
def hdd_password_009():
    """
    Name:   修改硬盘密码最大长度，最大复杂度

    Steps:  1.设置硬盘密码
            2.修改硬盘密码为最大长度，最大复杂度
            3.关机，开机POST校验硬盘密码输入修改前的密码
            4.输入修改后的硬盘密码
            5.禁用硬盘密码输入修改前的硬盘密码
            6.禁用硬盘密码输入修改后的硬盘密码

    Result: 2.硬盘密码修改成功
            3.提示硬盘密码错误
            4.硬盘密码校验成功
            5.禁用硬盘密码失败
            6.禁用硬盘密码成功
    """
    try:
        assert HDDPassword.hdd_password_009()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('810', '[TC810]HDD Password Security 010', '修改硬盘密码测试，修改为符合长度要求，不符合复杂度要求；符合复杂度要求，不符合长度要求；新密码和确认密码不同，修改失败测试'))
def hdd_password_010():
    """
    Name:   修改硬盘密码负面测试

    Steps:  1.设置硬盘密码
            2.修改硬盘密码为符合长度要求，不符合复杂度要求
            3.修改硬盘密码为符合复杂度要求，不符合长度要求
            4.修改硬盘密码时，新密码与确认密码不同
            5.禁用硬盘密码

    Result: 2/3/4.修改失败

    """
    try:
        assert HDDPassword.hdd_password_010()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('811', '[TC811]HDD Password Security 011', '设置硬盘密码进入系统测试'))
def hdd_password_011():
    """
    Name:   设置硬盘密码进入系统

    Steps:  1.设置硬盘密码
            2.关机，开机POST输入正确的硬盘密码，启动菜单进入该硬盘
            3.重复步骤2

    Result: 2/3.启动菜单有该硬盘启动项，成功进入该硬盘的系统
    """
    try:
        assert HDDPassword.hdd_password_011()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('812', '[TC812]HDD Password Security 012', '硬盘密码输错测试'))
def hdd_password_012():
    """
    Name:   硬盘密码输错测试

    Steps:  1.设置硬盘密码
            2.关机，开机POST阶段输错硬盘密码三次，检查启动菜单是否有该硬盘启动项,SetUp下该硬盘的状态
            3.关机，开机POST阶段输错密码两次，第三次输入正确的密码，进入SetUp删除硬盘密码

    Result: 2.启动菜单没有该硬盘的启动项，SetUp下该硬盘锁住
            3.成功进入SetUp，硬盘密码删除成功
    """
    try:
        assert HDDPassword.hdd_password_012()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('813', '[TC813]HDD Password Security 013', '修改硬盘密码，输入错误密码3次，硬盘锁定'))
def hdd_password_013():
    """
    Name:   修改硬盘密码，输错密码三次

    Steps:  1.设置硬盘密码
            2.修改硬盘密码，输错旧密码三次
            3.删除硬盘密码

    Result: 2.输错密码三次，提示密码被锁住

    """
    try:
        assert HDDPassword.hdd_password_013()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('814', '[TC814]HDD Password Security 014', '硬盘密码输入时按ESC测试'))
def hdd_password_014():
    """
    Name:   硬盘密码输入时按ESC

    Steps:  1.设置硬盘密码
            2.关机，开机POST阶段按ESC跳过硬盘密码，检查启动菜单，SetUp下硬盘状态
            3.关机，开机输入正确硬盘密码进入SetUp，删除硬盘密码

    Result: 2.启动菜单没有该硬盘启动项，SetUp下硬盘被锁住
            3.输入正确密码成功进入SetUp
    """
    try:
        assert HDDPassword.hdd_password_014()

        return core.Status.Pass
    except Exception as e:

        logging.error(e)
        return core.Status.Fail


@core.test_case(('815', '[TC815]HDD Password Security 015', '多硬盘密码测试'))
def hdd_password_015():
    """
    Name:   多硬盘密码

    Steps:  1.设置两个硬盘的硬盘密码
            2.关机，开机POST校验第一块硬盘时输入第二个硬盘的密码
            3.输入第一个硬盘的密码
            4.校验第二个硬盘时输入第一个硬盘的密码
            5.输入第二个硬盘的密码
            6.进入SetUp删除两个硬盘的密码

    Result: 2.密码校验失败
            3.密码校验成功
            4.密码校验失败
            5.密码校验成功
    """
    try:
        assert HDDPassword.hdd_password_015()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('816', '[TC816]HDD Password Security 016', '多硬盘密码输错测试'))
def hdd_password_016():
    """
    Name:   多硬盘密码输错

    Steps:  1.设置两个硬盘的硬盘密码
            2.POST阶段第一个硬盘密码输错三次，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            3.POST阶段第一个硬盘输入正确密码，第二个硬盘密码输错三次，检查启动菜单，SetUp下硬盘状态
            4.POST阶段两个硬盘密码都输错三次，检查启动菜单，SetUp下硬盘状态
            5.删除两个硬盘密码

    Result: 2.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            3.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            4.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
    """
    try:
        assert HDDPassword.hdd_password_016()
        return core.Status.Pass
    except Exception as e:
        BmcLib.power_off()
        logging.error(e)
        return core.Status.Fail


@core.test_case(('817', '[TC817]HDD Password Security 017', '多硬盘密码输入时按ESC测试'))
def hdd_password_017():
    """
    Name:   多硬盘密码输入时按ESC

    Steps:  1.两个硬盘设置硬盘密码
            2.POST阶段ESC跳过第一个硬盘密码，第二个硬盘输入正确密码，检查启动菜单，SetUp下硬盘状态
            3.POST阶段第一个硬盘输入正确密码，ESC跳过第二个硬盘密码，检查启动菜单，SetUp下硬盘状态
            4.POST阶段两个硬盘都ESC跳过密码，检查启动菜单，SetUp下硬盘状态
            5.删除两块硬盘密码

    Result: 2.启动菜单没有第一块硬盘信息，有第二块硬盘信息，SetUp下第一块硬盘锁住，第二块硬盘没有锁住
            3.启动菜单没有第二块硬盘信息，有第一块硬盘信息，SetUp下第二块硬盘锁住，第一块硬盘没有锁住
            4.启动菜单没有两块硬盘信息，SetUp下两块硬盘都锁住
    """
    try:
        assert HDDPassword.hdd_password_017()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('818', '[TC818]HDD Password Security 018', '多硬盘密码进入系统测试'))
def hdd_password_018():
    """
    Name:   多硬盘密码进入系统

    Steps:  1.设置两个硬盘的硬盘密码
            2.第一个硬盘密码输错三次，第二个硬盘输入正确密码，启动菜单进入第二个硬盘系统(第一次)
            3.第一个硬盘输入正确密码，第二个硬盘密码输错三次，启动菜单进入第一个硬盘系统(第一次)
            4.两个硬盘都输入正确密码，启动菜单进入第一个硬盘系统(第二次)
            5.两个硬盘都输入正确密码，启动菜单进入第二个硬盘系统(第二次)
            6.删除两个硬盘密码

    Result: 2.启动菜单只有第二个硬盘启动项，成功进入第二个硬盘系统
            3.启动菜单只有第一个硬盘启动项，成功进入第一个硬盘系统
            4.启动菜单有两个硬盘启动项，成功进入第一个硬盘系统
            5.启动菜单有两个硬盘启动项，成功进入第二个硬盘系统
    """
    try:
        assert HDDPassword.hdd_password_018()
        return core.Status.Pass
    except Exception as e:
        logging.info('Error...........................................')
        time.sleep(3)
        HDDPassword._boot_to_setup_two()
        BmcLib.power_off()
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail


@core.test_case(('819', '[TC819]Change HddPassword Hash Type', '设置硬盘密码哈希算法'))
def set_hash_type(type='type1'):
    """
    Name:   设置硬盘密码哈希算法

    Steps:  1.进入Setup设置指定的硬盘密码哈希算法

    Result: 1.哈希算法设置成功
    """
    try:
        assert HDDPassword.set_hash_type(type)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
