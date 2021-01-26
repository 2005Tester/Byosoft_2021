import os
from Common import Misc
from Pangea.BaseLib import SshLib
from Pangea import SutConfig

##########################################
####        UNCORE Test Cases        #####
####        Testcase ID: 2xx         #####
##########################################


# tests case to check whetehr result of lspci -tv is different after bios update 
# Precondition: Network is connected, OS can be accessed via ssh
# On Start: in OS
# On Complate: in OS
def pci_resource(ssh):
    tc = ('200', 'PCIE Resource Test 01', 'check whetehr lspci -tv result is different after bios update')
    result = Misc.LogHeaderResult(tc)
    lkg_log = os.path.join(SutConfig.LKG_LOG_DIR, "lspci_tv.log")
    if not SshLib.check_diff(ssh, "lspci -tv", lkg_log):
        result.log_fail()
        return
    result.log_pass()
    return True
