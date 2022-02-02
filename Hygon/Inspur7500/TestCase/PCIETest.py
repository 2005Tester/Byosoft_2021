import logging
import time
from batf.Report import ReportGen
from Inspur7500.Base import PCIE
from batf import core



'''
PCIE  case  编号:251~300
'''



@core.test_case(('251','[TC251]PCIE Max Payload','PCIE最大负载'))
def pcie_max_payload():

    try:
        assert PCIE.pcie_max_payload()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('252','[TC252]PCIE ASPM','PCIE ASPM'))
def pcie_aspm():

    try:
        assert PCIE.pcie_aspm()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('253','[TC253]PCIE Device Link Status','PCIE Device Link Status'))
def pcie_device_link_status():

    try:
        assert PCIE.pcie_device_link_status()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('254','[TC254]Above 4GB Decoding','4GB以上空间解码'))
def above_4gb():

    try:
        assert PCIE.above_4gb()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail