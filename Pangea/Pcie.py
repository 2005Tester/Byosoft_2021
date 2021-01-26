import os
import logging
from Common import Misc
from Pangea.BaseLib import SshLib
from Pangea import SutConfig

##########################################
####        PCIE Test Cases          #####
####        Testcase ID: 2xx         #####
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
    logging.info("Check resource allocation for root port 1")
    root_port1 = ["Memory behind bridge: 9b800000-9b9fffff", "Prefetchable memory behind bridge: 0000000098000000-0000000099ffffff"]
    if not SshLib.verify_info(ssh, "OS", "lspci -s 00:1c.0 -vv", root_port1):
        result.log_fail()
        return
    logging.info("Resource allocation for root port 1 verified")
    result.log_pass()
    return True