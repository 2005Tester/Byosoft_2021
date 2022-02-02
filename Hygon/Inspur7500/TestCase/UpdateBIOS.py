import logging
import time
import re
from batf.Report import ReportGen
from Inspur7500.BaseLib import  SetUpLib, BmcLib
from Inspur7500.Base import Update
from Inspur7500.Config import SutConfig
from batf import core



'''
UpdateBIOS  Case  编号：001~100
'''



@core.test_case(('021', '[TC021]Upgrade BIOS in Setup Update model normal', 'Setup保留升级BIOS'))
def setup_upgrade_normal(bios_mode='latest',change_part='all'):

    try:
        assert Update.setup_upgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

    
    
@core.test_case(('022', '[TC022]Upgrade BIOS in Setup Update model all', 'Setup全刷升级BIOS'))
def setup_upgrade_all(bios_mode='latest',change_part='three'):

    try:
        assert Update.setup_upgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('023', '[TC023]Downgrade BIOS in Setup Update model normal', 'Setup保留降级BIOS'))
def setup_downgrade_normal(bios_mode='previous',change_part='all'):

    try:
        assert Update.setup_downgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('024', '[TC024]Downgrade BIOS in Setup Update model all', 'Setup全刷降级BIOS'))
def setup_downgrade_all(bios_mode='previous',change_part='one'):

    try:
        assert Update.setup_downgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('025', '[TC025]Keep BIOS in Setup Update model normal', 'Setup保留平刷BIOS'))
def setup_keep_normal(bios_mode='latest',change_part='all'):

    try:
        assert Update.setup_keep_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('026', '[TC026]Keep BIOS in Setup Update model all', 'Setup全刷平刷BIOS'))
def setup_keep_all(bios_mode='latest',change_part='two'):

    try:
        assert Update.setup_keep_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('031', '[TC031]Upgrade BIOS in DOS Update model normal', 'DOS保留升级BIOS'))
def dos_upgrade_normal(bios_mode='latest',change_part='one'):

    try:
        assert Update.dos_upgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('032', '[TC032]Upgrade BIOS in DOS Update model all', 'DOS全刷升级BIOS'))
def dos_upgrade_all(bios_mode='latest',change_part='one'):

    try:
        assert Update.dos_upgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('033', '[TC033]Downgrade BIOS in DOS Update model normal', 'DOSq保留降级BIOS'))
def dos_downgrade_normal(bios_mode='previous',change_part='two'):

    try:
        assert Update.dos_downgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('034', '[TC034]Downgrade BIOS in DOS Update model all', 'DOS全刷降级BIOS'))
def dos_downgrade_all(bios_mode='previous',change_part='two'):

    try:
        assert Update.dos_downgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('035', '[TC035]Keep BIOS in DOS Update model normal', 'DOS保留平刷BIOS'))
def dos_keep_normal(bios_mode='latest',change_part='three'):

    try:
        assert Update.dos_keep_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('036', '[TC036]Keep BIOS in DOS Update model all', 'DOS全刷平刷BIOS'))
def dos_keep_all(bios_mode='latest',change_part='three'):

    try:
        assert Update.dos_keep_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('041', '[TC041]Upgrade BIOS in Shell Update model normal', 'SHELL保留升级BIOS'))
def shell_upgrade_normal(bios_mode='latest',change_part='two'):

    try:
        assert Update.shell_upgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('042', '[TC042]Upgrade BIOS in Shell Update model all', 'SHELL全刷升级BIOS'))
def shell_upgrade_all(bios_mode='latest',change_part='two'):

    try:
        assert Update.shell_upgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('043', '[TC043]Downgrade BIOS in Shell Update model normal', 'SHELL保留降级BIOS'))
def shell_downgrade_normal(bios_mode='previous',change_part='three'):

    try:
        assert Update.shell_downgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('044', '[TC044]Downgrade BIOS in Shell Update model all', 'SHELL全刷降级BIOS'))
def shell_downgrade_all(bios_mode='previous',change_part='three'):

    try:
        assert Update.shell_downgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('045', '[TC045]Keep BIOS in Shell Update model normal', 'SHELL保留平刷BIOS'))
def shell_keep_normal(bios_mode='latest',change_part='one'):

    try:
        assert Update.shell_keep_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('046', '[TC046]Keep BIOS in Shell Update model all', 'SHELL全刷平刷BIOS'))
def shell_keep_all(bios_mode='latest',change_part='one'):

    try:
        assert Update.shell_keep_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('051', '[TC051]Upgrade BIOS in Linux Update model normal', 'Linux保留升级BIOS'))
def linux_upgrade_normal(bios_mode='latest',change_part='three'):

    try:
        assert Update.linux_upgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('052', '[TC052]Upgrade BIOS in Linux Update model all', 'Linux全刷升级BIOS'))
def linux_upgrade_all(bios_mode='latest',change_part='three'):

    try:
        assert Update.linux_upgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('053', '[TC053]Downgrade BIOS in Linux Update model normal', 'Linux保留降级BIOS'))
def linux_downgrade_normal(bios_mode='previous',change_part='one'):

    try:
        assert Update.linux_downgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('054', '[TC054]Downgrade BIOS in Linux Update model all', 'Linux全刷降级BIOS'))
def linux_downgrade_all(bios_mode='previous',change_part='one'):

    try:
        assert Update.linux_downgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('055', '[TC055]Keep BIOS in Linux Update model normal', 'Linux保留平刷BIOS'))
def linux_keep_normal(bios_mode='latest',change_part='two'):

    try:
        assert Update.linux_keep_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('056', '[TC056]Keep BIOS in Linux Update model all', 'Linux全刷平刷BIOS'))
def linux_keep_all(bios_mode='latest',change_part='two'):

    try:
        assert Update.linux_keep_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('061', '[TC061]Upgrade BIOS in Windows Update model normal', 'Windows保留升级BIOS'))
def windows_upgrade_normal(bios_mode='latest',change_part='all'):

    try:
        assert Update.windows_upgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('062', '[TC062]Upgrade BIOS in Windows Update model all', 'Windows全刷升级BIOS'))
def windows_upgrade_all(bios_mode='latest',change_part='all'):

    try:
        assert Update.windows_upgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('063', '[TC063]Downgrade BIOS in Windows Update model normal', 'Windows保留降级BIOS'))
def windows_downgrade_normal(bios_mode='previous',change_part='all'):

    try:
        assert Update.windows_downgrade_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('064', '[TC064]Downgrade BIOS in Windows Update model all', 'Windows全刷降级BIOS'))
def windows_downgrade_all(bios_mode='previous',change_part='all'):

    try:
        assert Update.windows_downgrade_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('065', '[TC065]Keep BIOS in Windows Update model normal', 'Windows保留平刷BIOS'))
def windows_keep_normal(bios_mode='latest',change_part='all'):

    try:
        assert Update.windows_keep_normal(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('066', '[TC066]Keep BIOS in Windows Update model all', 'Windows全刷平刷BIOS'))
def windows_keep_all(bios_mode='latest',change_part='all'):

    try:
        assert Update.windows_keep_all(bios_mode,change_part)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('071','[TC071]Set Password','刷新BIOS前设置密码'))
def set_password():

    try:
        assert Update.set_password()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('072','[TC072]Delete Password','刷新BIOS后删除密码'))
def del_password():

    try:
        assert Update.del_password()
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



@core.test_case(('081','[TC081]Update BIOS in Setup Update model normal','SetUp保留刷新BIOS'))
def update_bios_setup_normal(bios_mode):

    try:
        assert Update.update_bios_setup_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('082','[TC082]Update BIOS in Setup Update model all','SetUp全刷刷新BIOS'))
def update_bios_setup_all(bios_mode):

    try:
        assert Update.update_bios_setup_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('083','[TC083]Update BIOS in DOS Update model normal','DOS保留刷新BIOS'))
def update_bios_dos_normal(bios_mode):

    try:
        assert Update.update_bios_dos_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('084','[TC084]Update BIOS in DOS Update model all','DOS全刷刷新BIOS'))
def update_bios_dos_all(bios_mode):

    try:
        assert Update.update_bios_dos_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('085','[TC085]Update BIOS in Shell Update model normal','SHELL保留刷新BIOS'))
def update_bios_shell_normal(bios_mode):

    try:
        assert Update.update_bios_shell_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('086','[TC086]Update BIOS in Shell Update model all','SHELL全刷刷新BIOS'))
def update_bios_shell_all(bios_mode):

    try:
        assert Update.update_bios_shell_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('087','[TC087]Update BIOS in Linux Update model normal','Linux保留刷新BIOS'))
def update_bios_linux_normal(bios_mode):

    try:
        assert Update.update_bios_linux_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('088','[TC088]Update BIOS in Linux Update model all','Linux全刷刷新BIOS'))
def update_bios_linux_all(bios_mode):

    try:
        assert Update.update_bios_linux_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('089','[TC089]Update BIOS in Windows Update model normal','Windows保留刷新BIOS'))
def update_bios_windows_normal(bios_mode):

    try:
        assert Update.update_bios_windows_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('090','[TC090]Update BIOS in Windows Update model all','Windows全刷刷新BIOS'))
def update_bios_windows_all(bios_mode):

    try:
        assert Update.update_bios_windows_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
