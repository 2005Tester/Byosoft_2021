# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
PXE  case  编号:201~250
'''


@core.test_case(('201', '[TC201]PXE Option Rom', 'PXE网络引导'))
def pxe_option_rom(oem=False):
    """
    Name:   PXE网络引导

    Steps:  1.SetUp下关闭PXE网络引导
            2.查看启动菜单是否出现PXE启动项
            3.SetUp下打开PXE网络引导
            4.查看启动菜单是否出现PXE启动项

    Result: 2.启动菜单没有PXE启动项
            4.启动菜单有PXE启动项
    """
    try:
        assert PXE.pxe_option_rom(oem)
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('202', '[TC202]PXE BOOT', 'PXE启动IPv4和IPv6'))
def pxe_boot(oem=False):
    """
    Name:   PXE启动

    Steps:  1.SetUp设置IP版本为IPv4
            2.F12是否进入Ipv4网络启动
            3.SetUp设置IP版本为IPv6
            4.F12是否进入Ipv6网络启动
            5.SetUp设置Legacy模式
            6.F12是否进入Legacy网络启动

    Result: 2.F12进入Ipv4网络启动
            4.F12进入Ipv6网络启动
            6.F12进入Legacy网络启动
    """
    try:

        assert PXE.pxe_boot(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('203', '[TC203]PXE Retry', '网络启动重试'))
def pxe_retry(oem=False):
    """
    Name:   网络启动重试

    Steps:  1.SetUp下关闭网络启动重试
            2.F12进入网络启动
            3.SetUp下打开网络启动重试
            4.F12进入网络启动

    Result: 2.网络启动失败后，不进行重试
            4.网络启动失败后不断进行重试
    """
    try:
        assert PXE.pxe_retry(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('204', '[TC204]Net Boot IP Version', '网络引导IP版本'))
def pxe_protocol(oem=False):
    """
    Name:   网络引导IP版本

    Steps:  1.SetUp设置网络引导IP版本为Ipv4和Ipv6
            2.查看启动菜单
            3.SetUp设置网络引导IP版本为Ipv4
            4.查看启动菜单
            5.SetUp设置网络引导IP版本为Ipv6
            6.查看启动菜单

    Result: 2.启动菜单中有Ipv4和Ipv6的启动项
            4.启动菜单只有Ipv4的启动项
            6.启动菜单只有Ipv6的启动项
    """
    try:
        assert PXE.pxe_protocol(oem)
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('205', '[TC205]PXE Network', 'PXE启动网卡'))
def pxe_network():
    """
    Name:   PXE启动网卡

    Steps:  1.SetUp下启动网卡选择板载网卡
            2.查看启动菜单
            3.SetUp下启动网卡选择外插网卡
            4.查看启动菜单
            5.SetUp下启动网卡选择Null
            6.查看启动菜单

    Result: 2.启动菜单只有板载网卡的启动项
            4.启动菜单只有外插网卡的启动项
            6.启动菜单有板载网卡和外插网卡的启动项
    """
    try:
        assert PXE.pxe_network()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('206', '[TC206]PXE BOOT Priority', 'PXE启动优先级'))
def pxe_boot_priority(oem=False):
    """
    Name:   PXE启动优先级

    Steps:  1.SetUp下设置板载优先
            2.查看启动菜单
            3.SetUp下设置外插优先
            4.查看启动菜单

    Result: 2.启动项中板载优先
            4.启动项中外插优先
    """

    try:
        assert PXE.pxe_boot_priority(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('207', '[TC207]Legacy PXE Retry', 'Legacy模式网络启动重试'))
def pxe_retry_legacy(oem=False):
    """
    Name:   Legacy模式网络启动重试

    Steps:  1.SetUp设置Legacy模式，网络启动重试关闭
            2.F12进入网络启动
            3.SetUp打开网络启动重试
            4.F12进入网络启动

    Result: 2.网络启动失败后不在重试
            4.网络启动失败后不断进行重试
    """
    try:
        assert PXE.pxe_retry_legacy(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('208', '[TC208]Highest Boot Priority Device', '高启动优先设备'))
def higest_boot_priority():
    try:
        return PXE.higest_boot_priority()
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
