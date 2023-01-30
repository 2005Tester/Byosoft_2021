# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
PCIE  case  编号:251~300
'''


@core.test_case(('251', '[TC251]PCIE Max Payload', 'PCIE最大负载'))
def pcie_max_payload(oem=False):
    """
    Name:   PCIE最大负载

    Steps:  遍历所有的选项值
            1.SetUp下设置PCIE最大负载为指定值
            2.进入系统查看网卡，RAID卡，SAS卡的PCIE Max Payload

    Result: 2.系统下网卡，RAID卡，SAS卡的PCIE Max Payload为设置的值
    """
    try:
        assert PCIE.pcie_max_payload(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('252', '[TC252]PCIE ASPM', 'PCIE ASPM'))
def pcie_aspm(oem=False):
    """
    Name:   PCIE ASPM

    Steps:  1.SetUp下打开ASPM
            2.进入系统查看网卡，RAID卡，SAS卡的ASPM
            3.SetUp下关闭ASPM
            4.进入系统查看网卡，RAID卡，SAS卡的ASPM

    Result: 2.系统下网卡，RAID卡，SAS卡的ASPM为L1
            4.系统下网卡，RAID卡，SAS卡的ASPM为Disabled
    """
    try:
        assert PCIE.pcie_aspm(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('253', '[TC253]PCIE Device Link Status', 'PCIE Device Link Status'))
def pcie_device_link_status():
    """
    Name:   PCIE Device Link Status

    Steps:  1.进入系统查看网卡，RAID卡，SAS卡最大支持带宽与实际带宽是否相符

    Result: 1.看网卡，RAID卡，SAS卡最大支持带宽与实际带宽相符
    """
    try:
        assert PCIE.pcie_device_link_status()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('254', '[TC254]Above 4GB Decoding', '4GB以上空间解码'))
def above_4gb():
    """
    Name:   4GB以上空间解码

    Steps:  1.SetUp下打开4GB以上空间解码
            2.系统下查看网卡，RAID卡，SAS卡是否打开
            3.SetUp下关闭4GB以上空间解码
            4.系统下查看网卡，RAID卡，SAS卡是否关闭

    Result: 2.系统下查看网卡，RAID卡，SAS卡打开
            4.系统下查看网卡，RAID卡，SAS卡关闭

    """
    try:
        assert PCIE.above_4gb()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
