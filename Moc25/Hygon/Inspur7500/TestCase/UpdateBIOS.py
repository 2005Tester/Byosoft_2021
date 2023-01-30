# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
UpdateBIOS  Case  编号:001~100
'''


@core.test_case(('021', '[TC021]Upgrade BIOS in Setup Update model normal', 'Setup保留升级BIOS'))
def setup_upgrade_normal(bios_mode='latest', change_part='all'):
    """
    Name:   Setup保留升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Setup保留升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.setup_upgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('022', '[TC022]Upgrade BIOS in Setup Update model all', 'Setup全刷升级BIOS'))
def setup_upgrade_all(bios_mode='latest', change_part='three'):
    """
    Name:   Setup全刷升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Setup全刷升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.setup_upgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('023', '[TC023]Downgrade BIOS in Setup Update model normal', 'Setup保留降级BIOS'))
def setup_downgrade_normal(bios_mode='previous', change_part='all'):
    """
    Name:   Setup保留降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Setup保留降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.setup_downgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('024', '[TC024]Downgrade BIOS in Setup Update model all', 'Setup全刷降级BIOS'))
def setup_downgrade_all(bios_mode='previous', change_part='all'):
    """
    Name:   Setup全刷降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Setup全刷降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.setup_downgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('031', '[TC031]Upgrade BIOS in DOS Update model normal', 'DOS保留升级BIOS'))
def dos_upgrade_normal(bios_mode='latest', change_part='all'):
    """
    Name:   DOS保留升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.DOS保留升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.dos_upgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('032', '[TC032]Upgrade BIOS in DOS Update model all', 'DOS全刷升级BIOS'))
def dos_upgrade_all(bios_mode='latest', change_part='all'):
    """
    Name:   DOS全刷升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.DOS全刷升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.dos_upgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('033', '[TC033]Downgrade BIOS in DOS Update model normal', 'DOS保留降级BIOS'))
def dos_downgrade_normal(bios_mode='previous', change_part='all'):
    """
    Name:   DOS保留降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.DOS保留降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.dos_downgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('034', '[TC034]Downgrade BIOS in DOS Update model all', 'DOS全刷降级BIOS'))
def dos_downgrade_all(bios_mode='previous', change_part='all'):
    """
    Name:   DOS全刷降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.DOS全刷降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.dos_downgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('041', '[TC041]Upgrade BIOS in Shell Update model normal', 'SHELL保留升级BIOS'))
def shell_upgrade_normal(bios_mode='latest', change_part='all'):
    """
    Name:   Shell保留升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Shell保留升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.shell_upgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('042', '[TC042]Upgrade BIOS in Shell Update model all', 'SHELL全刷升级BIOS'))
def shell_upgrade_all(bios_mode='latest', change_part='all'):
    """
    Name:   Shell全刷升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Shell全刷升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.shell_upgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('043', '[TC043]Downgrade BIOS in Shell Update model normal', 'SHELL保留降级BIOS'))
def shell_downgrade_normal(bios_mode='previous', change_part='all'):
    """
    Name:   Shell保留降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Shell保留降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.shell_downgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('044', '[TC044]Downgrade BIOS in Shell Update model all', 'SHELL全刷降级BIOS'))
def shell_downgrade_all(bios_mode='previous', change_part='all'):
    """
    Name:   Shell全刷降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Shell全刷降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.shell_downgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('051', '[TC051]Upgrade BIOS in Linux Update model normal', 'Linux保留升级BIOS'))
def linux_upgrade_normal(bios_mode='latest', change_part='all'):
    """
    Name:   Linux保留升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Linux保留升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.linux_upgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('052', '[TC052]Upgrade BIOS in Linux Update model all', 'Linux全刷升级BIOS'))
def linux_upgrade_all(bios_mode='latest', change_part='all'):
    """
    Name:   Linux全刷升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Linux全刷升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.linux_upgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('053', '[TC053]Downgrade BIOS in Linux Update model normal', 'Linux保留降级BIOS'))
def linux_downgrade_normal(bios_mode='previous', change_part='all'):
    """
    Name:   Linux保留降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Linux保留降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.linux_downgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('054', '[TC054]Downgrade BIOS in Linux Update model all', 'Linux全刷降级BIOS'))
def linux_downgrade_all(bios_mode='previous', change_part='all'):
    """
    Name:   Linux全刷降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Linux全刷降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.linux_downgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('061', '[TC061]Upgrade BIOS in Windows Update model normal', 'Windows保留升级BIOS'))
def windows_upgrade_normal(bios_mode='latest', change_part='all'):
    """
    Name:   Windows保留升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Windows保留升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.windows_upgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('062', '[TC062]Upgrade BIOS in Windows Update model all', 'Windows全刷升级BIOS'))
def windows_upgrade_all(bios_mode='latest', change_part='all'):
    """
    Name:   Windows全刷升级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Windows全刷升级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.windows_upgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('063', '[TC063]Downgrade BIOS in Windows Update model normal', 'Windows保留降级BIOS'))
def windows_downgrade_normal(bios_mode='previous', change_part='all'):
    """
    Name:   Windows保留降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Windows保留降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与修改的值相同

    """
    try:
        assert Update.windows_downgrade_normal(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('064', '[TC064]Downgrade BIOS in Windows Update model all', 'Windows全刷降级BIOS'))
def windows_downgrade_all(bios_mode='previous', change_part='all'):
    """
    Name:   Windows全刷降级BIOS
    Condition:  设置管理员用户密码

    Steps:  1.修改SetUp选项
            2.Windows全刷降级BIOS
            3.检查刷新BIOS后密码是否存在，刷新后的选项

    Result: 3.管理员用户密码保留，刷新后的值与默认值相同

    """
    try:
        assert Update.windows_downgrade_all(bios_mode, change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('071', '[TC071]Set Password', '刷新BIOS前设置密码'))
def set_password():
    """
    Name:   刷新BIOS前设置密码

    Steps:  1.SetUp下设置管理员密码，用户密码
            2.设置密码有效期，密码锁定时间

    Result: 1/2.设置成功
    """
    try:
        assert Update.set_password()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('072', '[TC072]Delete Password', '刷新BIOS后删除密码'))
def del_password():
    """
    Name:   刷新BIOS后删除密码

    Steps:  1.SetUp下删除管理员密码，用户密码

    Result: 1.密码删除成功
    """
    try:
        assert Update.del_password()
        time.sleep(3)
        return core.Status.Pass
    except Exception as e:
        time.sleep(3)
        logging.error(e)
        return core.Status.Fail


@core.test_case(('081', '[TC081]Update BIOS in Setup Update model normal', 'SetUp保留刷新BIOS'))
def update_bios_setup_normal(bios_mode):
    """
    Name:   SetUp保留刷新BIOS

    Steps:  1.SetUp保留刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_setup_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('082', '[TC082]Update BIOS in Setup Update model all', 'SetUp全刷刷新BIOS'))
def update_bios_setup_all(bios_mode):
    """
    Name:   SetUp全刷刷新BIOS

    Steps:  1.SetUp全刷刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_setup_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('083', '[TC083]Update BIOS in DOS Update model normal', 'DOS保留刷新BIOS'))
def update_bios_dos_normal(bios_mode):
    """
    Name:   DOS保留刷新BIOS

    Steps:  1.DOS保留刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_dos_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('084', '[TC084]Update BIOS in DOS Update model all', 'DOS全刷刷新BIOS'))
def update_bios_dos_all(bios_mode):
    """
    Name:   DOS全刷刷新BIOS

    Steps:  1.DOS全刷刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_dos_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('085', '[TC085]Update BIOS in Shell Update model normal', 'SHELL保留刷新BIOS'))
def update_bios_shell_normal(bios_mode):
    """
    Name:   SHELL保留刷新BIOS

    Steps:  1.SHELL保留刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_shell_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('086', '[TC086]Update BIOS in Shell Update model all', 'SHELL全刷刷新BIOS'))
def update_bios_shell_all(bios_mode):
    """
    Name:   SHELL全刷刷新BIOS

    Steps:  1.SHELL全刷刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_shell_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('087', '[TC087]Update BIOS in Linux Update model normal', 'Linux保留刷新BIOS'))
def update_bios_linux_normal(bios_mode):
    """
    Name:   Linux保留刷新BIOS

    Steps:  1.Linux保留刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_linux_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('088', '[TC088]Update BIOS in Linux Update model all', 'Linux全刷刷新BIOS'))
def update_bios_linux_all(bios_mode):
    """
    Name:   Linux全刷刷新BIOS

    Steps:  1.Linux全刷刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_linux_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('089', '[TC089]Update BIOS in Windows Update model normal', 'Windows保留刷新BIOS'))
def update_bios_windows_normal(bios_mode):
    """
    Name:   Windows保留刷新BIOS

    Steps:  1.Windows保留刷新BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_windows_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('090', '[TC090]Update BIOS in Windows Update model all', 'Windows全刷刷新BIOS'))
def update_bios_windows_all(bios_mode):
    """
    Name:   Windows全刷刷新BIOS

    Steps:  1.Windows下全刷BIOS

    Result: 1.BIOS刷新成功
    """
    try:
        assert Update.update_bios_windows_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('091', '[TC091]Update Wrong BIOS(unsign,other)', '更新未签名，其他平台BIOS，更新失败测试'))
def update_wrong_bios():
    """
    Name:   更新未签名，其他平台BIOS，更新失败测试

    Steps:  1.SetUp下更新其他平台BIOS,未签名BIOS
            2.Shell下更新其他平台BIOS,未签名BIOS
            3.Linux下更新其他平台BIOS,未签名BIOS

    Result: 1/2/3.更新失败且提示信息正确
    """
    try:
        assert Update.update_wrong_bios()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
