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
    lkg_log = os.path.join(SutConfig.LKG_LOG_DIR, "lspci_tv.log")
    if not SshLib.check_diff(ssh, "OS", "lspci -tv", lkg_log):
        result.log_fail()
        return
    result.log_pass()
    return True


# tests case to check whetehr resource allocated for root ports are correct
# Precondition: Network is connected, OS can be accessed via ssh
# On Start: in OS
# On Complete: in OS
def pci_resource_root_port(ssh):
    tc = ('201', 'PCIE Resource Test 02', 'check whetehr resource allocated for root ports are correct')
    result = Misc.LogHeaderResult(tc)
    fail_cnt = 0
    ports = [SutConfig.ROOT_PORT_17, SutConfig.ROOT_PORT_18, SutConfig.ROOT_PORT_19, SutConfig.ROOT_PORT_15]
    for port in ports:
        logging.info("Check resource allocation for: {0}".format(port[0]))
        if not SshLib.verify_info(ssh, "OS", "lspci -s {0} -vv".format(port[0]), port[1]):
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
