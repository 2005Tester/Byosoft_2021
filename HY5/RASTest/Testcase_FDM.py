# -*- encoding=utf8 -*-


class SmiStorm:
    def __init__(self):
        self.CONFIG = type(self).__name__

    def Testcase_FDM_SMI_002(self):
        ports = check_pcie_presence()
        for port in ports:
            for i in range(3):
                pcie_err(count=11, socket_port=port, errType="uce")
                timer(610)
            pcie_err(count=1, socket_port=port, errType="uce")

    def Testcase_FDM_SMI_003(self):
        port = check_pcie_presence()[0]
        pcie_err(count=11, socket_port=port, errType="ce")

    def Testcase_FDM_SMI_004(self):
        ports = check_pcie_presence()
        for port in ports:
            for i in range(4):
                pcie_err(count=11, socket_port=port, errType="ce")
                timer(610)
            pcie_err(count=1, socket_port=port, errType="ce")

    def Testcase_FDM_SMI_005(self):
        slot = check_mem_pop()[0]
        channel = slot[2] if (slot[1] == 0) else slot[2] + 3
        mem_err(count=11, dev=1, socket=slot[0], channel=channel, dimm=slot[3], rank=0, errType="ce")
        timer(65)
        mem_err(count=1, dev=3, socket=slot[0], channel=channel, dimm=slot[3], rank=0, errType="uce")

    def Testcase_FDM_SMI_006(self):
        slot = check_mem_pop()[0]
        channel = slot[2]
        if slot[1]:
            channel = channel + 3
        for i in range(3):
            mem_err(count=11, socket=slot[0], channel=channel, dimm=slot[3], rank=0, errType="ce")
            timer(610)
        mem_err(count=1, socket=slot[0], channel=channel, dimm=slot[3], rank=0, errType="uce")

    def Testcase_FDM_SMI_007(self):
        port = check_pcie_presence()[0]
        pcie_err(count=255, socket_port=port, errType="ce")


SmiStorm = SmiStorm()
