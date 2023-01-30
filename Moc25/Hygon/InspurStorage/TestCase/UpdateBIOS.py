import logging
import time
import re
from batf.Report import ReportGen
from InspurStorage.BaseLib import  SetUpLib, BmcLib
from InspurStorage.Base import Update
from InspurStorage.Config import SutConfig
from batf import core



'''
UpdateBIOS  Case  编号：001~100
'''



@core.test_case(('021', '[TC021]Upgrade BIOS in Setup Update model normal', 'Setup保留升级BIOS'))
def setup_upgrade(bios_mode='latest'):
    try:
        assert Update.setup_upgrade(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('023', '[TC023]Downgrade BIOS in Setup Update model normal', 'Setup保留降级BIOS'))
def setup_downgrade(bios_mode='previous'):
    try:
        assert Update.setup_downgrade(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('025', '[TC025]Keep BIOS in Setup Update model normal', 'Setup保留平刷BIOS'))
def setup_keep(bios_mode='latest'):
    try:
        assert Update.setup_keep(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('041', '[TC041]Upgrade BIOS in Shell Update model normal', 'SHELL保留升级BIOS'))
def shell_upgrade_normal(bios_mode='latest'):
    try:
        assert Update.shell_upgrade_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('042', '[TC042]Upgrade BIOS in Shell Update model all', 'SHELL全刷升级BIOS'))
def shell_upgrade_all(bios_mode='latest'):
    try:
        assert Update.shell_upgrade_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('043', '[TC043]Downgrade BIOS in Shell Update model normal', 'SHELL保留降级BIOS'))
def shell_downgrade_normal(bios_mode='previous'):
    try:
        assert Update.shell_downgrade_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('044', '[TC044]Downgrade BIOS in Shell Update model all', 'SHELL全刷降级BIOS'))
def shell_downgrade_all(bios_mode='previous'):
    try:
        assert Update.shell_downgrade_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('045', '[TC045]Keep BIOS in Shell Update model normal', 'SHELL保留平刷BIOS'))
def shell_keep_normal(bios_mode='latest'):
    try:
        assert Update.shell_keep_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('046', '[TC046]Keep BIOS in Shell Update model all', 'SHELL全刷平刷BIOS'))
def shell_keep_all(bios_mode='latest'):
    try:
        assert Update.shell_keep_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('051', '[TC051]Upgrade BIOS in Linux Update model normal', 'Linux保留升级BIOS'))
def linux_upgrade_normal(bios_mode='latest'):

    try:
        assert Update.linux_upgrade_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('052', '[TC052]Upgrade BIOS in Linux Update model all', 'Linux全刷升级BIOS'))
def linux_upgrade_all(bios_mode='latest'):
    try:
        assert Update.linux_upgrade_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('053', '[TC053]Downgrade BIOS in Linux Update model normal', 'Linux保留降级BIOS'))
def linux_downgrade_normal(bios_mode='previous'):
    try:
        assert Update.linux_downgrade_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('054', '[TC054]Downgrade BIOS in Linux Update model all', 'Linux全刷降级BIOS'))
def linux_downgrade_all(bios_mode='previous'):
    try:
        assert Update.linux_downgrade_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('055', '[TC055]Keep BIOS in Linux Update model normal', 'Linux保留平刷BIOS'))
def linux_keep_normal(bios_mode='latest'):
    try:
        assert Update.linux_keep_normal(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('056', '[TC056]Keep BIOS in Linux Update model all', 'Linux全刷平刷BIOS'))
def linux_keep_all(bios_mode='latest'):
    try:
        assert Update.linux_keep_all(bios_mode)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



