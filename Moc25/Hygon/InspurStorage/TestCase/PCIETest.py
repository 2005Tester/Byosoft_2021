import logging
import time
from InspurStorage.Config import SutConfig
from InspurStorage.Base import PCIE
from batf import core



'''
PCIE  case  编号:251~300
'''



@core.test_case(('251', '[TC251]PCIE Retrain','PCIE 链路协商重试'))
def pcie_retrain():
    try:
        assert PCIE.pcie_retrain()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('252', '[TC252]Pcie Resource Reservation','PCIE资源预留'))
def pcie_resource_reservation():
    try:
        assert PCIE.pcie_resource_reservation()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('253', '[TC253]Pcie Memory Enable','PCIE的Memory使能'))
def pcie_mem_enable():
    try:
        assert PCIE.pcie_mem_enable()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('254', '[TC254]SMI','SMI 机制'))
def smi():
    try:
        assert PCIE.smi()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('255', '[TC255]IO','PCIE Slot槽正确的分配IO资源'))
def io():
    if SutConfig.Pci.NAME == '2U':
        return core.Status.Skip
    try:
        assert PCIE.io()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('256', '[TC256]QAT','插入QAT 查看是否显示'))
def qat():
    try:
        assert PCIE.qat()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail