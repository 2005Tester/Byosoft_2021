import logging
import time
from batf.Report import ReportGen
from Hygon3000CRB.Base import PCIE
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



@core.test_case(('254','[TC254]PCIE Max Readload','PCIE Max Readload'))
def pcie_max_Readload():
    try:
        assert PCIE.pcie_max_Readload()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('255','[TC255]Above 4G Decoding','Above 4G Decoding'))
def Above_4G_Decoding():
    try:
        assert PCIE.Above_4G_Decoding()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail