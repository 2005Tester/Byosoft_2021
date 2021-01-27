import os
import logging
from Common import Misc
from Pangea.BaseLib import SshLib
from Pangea import SutConfig

##########################################
#        PCIE Test Cases                 #
#        Testcase ID: 2xx                #
##########################################


# tests case to check whetehr result of lspci -tv is different after bios update 
# Precondition: Network is connected, OS can be accessed via ssh
# On Start: in OS
# On Complete: in OS
def pci_resource_tree_view(ssh):
    tc = ('200', 'PCIE Resource Test 01', 'check whetehr lspci -tv result is different after bios update')
    result = Misc.LogHeaderResult(tc)
    if SutConfig.BOARD_TYPE == "NVME2P":
        lkg_log = os.path.join(SutConfig.LKG_LOG_DIR, "lspci_tv_nvme2p.log")
    elif SutConfig.BOARD_TYPE == "SAS2P":
        lkg_log = os.path.join(SutConfig.LKG_LOG_DIR, "lspci_tv_sas2p.log")
    else:
        logging.info("Board type defined in SutConfig is not valid.")
        result.log_skip()
        return
    if not SshLib.check_diff(ssh, "lspci -tv", lkg_log):
        result.log_fail()
        return
    result.log_pass()
    return True


# tests case to check whetehr result of lspci -vv is different after bios update
# Precondition: Network is connected, OS can be accessed via ssh
# On Start: in OS
# On Complete: in OS
def lspci_diff(ssh):
    tc = ('201', 'PCIE Resource Test 01', 'check whetehr lspci -vv result is different after bios update')
    result = Misc.LogHeaderResult(tc)
    if SutConfig.BOARD_TYPE == "NVME2P":
        lkg_log = os.path.join(SutConfig.LKG_LOG_DIR, "lspci_vv_nvme2p.log")
    elif SutConfig.BOARD_TYPE == "SAS2P":
        lkg_log = os.path.join(SutConfig.LKG_LOG_DIR, "lspci_vv_sas2p.log")
    else:
        logging.info("Board type defined in SutConfig is not valid.")
        result.log_skip()
        return
    if not SshLib.check_diff(ssh, "lspci -vv", lkg_log):
        result.log_fail()
        return
    result.log_pass()
    return True


# tests case to check whetehr resource allocated for root ports are correct
# Precondition: Network is connected, OS can be accessed via ssh
# On Start: in OS
# On Complete: in OS
def pci_resource_root_port(ssh):
    tc = ('202', 'PCIE Resource Test 03', 'check whetehr resource allocated for root ports are correct')
    result = Misc.LogHeaderResult(tc)
    fail_cnt = 0
    ports = SutConfig.PCI_NVME_2P
    for port in ports:
        logging.info("Check resource allocation for: {0}".format(port[0]))
        if not SshLib.verify_info(ssh, "lspci -s {0} -vv".format(port[0]), port[1]):
            fail_cnt += 1
        else:
            logging.info("Verified: {0}".format(port(0)))
    if fail_cnt == 0:
        logging.info("Resource allocation for all root port verified")
        result.log_pass()
        return True
    else:
        logging.info("{0} out of {1} test failed".format(fail_cnt, len(ports)))
        result.log_fail()
        return
