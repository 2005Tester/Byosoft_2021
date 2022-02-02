from HuaweiCommon.RASTest.SPR.TestLoader import *


@bios_setting()
def Testcase_PcieRas_ErrorReport_001a():
    """Corrected Error测试"""
    shell_cmd("dmesg -C")
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.dump_pcie_err)
    inj_pcie(count=1, socket=Loc.psocket, port=0, errType="ce")  # DMI
    excmd(Cmd.dump_pcie_err)


@bios_setting()
def Testcase_PcieRas_ErrorReport_001b():
    """Corrected Error测试"""
    shell_cmd("dmesg -C")
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.dump_pcie_err)
    inj_pcie(count=1, socket=Loc.psocket, port=Loc.pcie_port, errType="ce")
    excmd(Cmd.dump_pcie_err)


@bios_setting()
def Testcase_PcieRas_ErrorReport_002():
    """Uncorrectable Error测试"""
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.dump_pcie_err)
    inj_pcie(count=1, socket=Loc.psocket, port=Loc.pcie_port, errType="uce")
    excmd(Cmd.dump_pcie_err)


@bios_setting()
def Testcase_PcieRas_ErrorReport_003():
    """non-fatal error Error测试"""
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.dump_pcie_err)
    inj_pcie(count=1, socket=Loc.psocket, port=0, errType="uce")  # DMI
    excmd(Cmd.dump_pcie_err)


@bios_setting()
def Testcase_PcieRas_IIOErrorReport_001a():
    """IIO Local Group Error Reporting"""
    Testcase_PcieRas_ErrorReport_001b()


@bios_setting()
def Testcase_PcieRas_IIOErrorReport_001b():
    """IIO Local Group Error Reporting"""
    Testcase_PcieRas_ErrorReport_002()