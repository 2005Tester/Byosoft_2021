# -*- encoding=utf8 -*-
from CommonTest.RASTest.ICX.RasConfig import *
from CommonTest.RASTest.ICX.TestLoader import *
from CommonTest.RASTest.ICX.Testcase_FDM import *

"""
RAS(CPU)需求
"""


@bios_setting("Viral")
def Testcase_CPURAS_001():
    """01 Viral Mode默认使能测试"""
    excmd(Cmd.viral_check, _halt=True)


@bios_setting("Viral")
def Testcase_CPURAS_002():
    """02 Viral Mode注入PCIe UCE错误测试"""
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.comp_timeout_severity)
    inj_pcie(errType="uce")
    excmd(Cmd.iio_viral_show.format(Loc.psocket), _halt=False)
    excmd(Cmd.viral_state_pcie.format(Loc.psocket), _halt=False, delay=Delay.caterr)


@bios_setting("Viral")
def Testcase_CPURAS_003():
    """03 Viral Mode注入UPI UCE错误测试"""
    excmd(Cmd.upi_top)
    inj_upi(num_crcs=0)
    excmd(Cmd.iio_viral_show.format(Loc.usocket), _halt=False)
    excmd(Cmd.viral_state_upi.format(Loc.usocket), _halt=False)


@bios_setting("WrCRC")
def Testcase_CPURAS_008():
    """08 Memory Error Injection"""
    inj_cap()
    inj_mem()
    excmd(Cmd.inj_wcrc.format(Loc.msocket, Loc.imc, Loc.channel))


@bios_setting("Default")
def Testcase_CPURAS_009_a():
    """09 Core Error Injection: 3-Strike Timeout"""
    Testcase_FDM_IERR_MCERR_005()


@bios_setting("Default")
def Testcase_CPURAS_009_b():
    """09 Core Error Injection: IERR"""
    Testcase_FDM_IERR_MCERR_001()


@bios_setting("Default")
def Testcase_CPURAS_009_b():
    """09 Core Error Injection: MCERR"""
    Testcase_FDM_IERR_MCERR_006()


@bios_setting("Default")
def Testcase_CPURAS_010_a():
    """10 UPI Error Injection"""
    inj_upi(port=0, num_crcs=1)


@bios_setting("Default")
def Testcase_CPURAS_010_b():
    """10 UPI Error Injection"""
    Testcase_CPURAS_018()


@bios_setting("Default")
def Testcase_CPURAS_010_b():
    """10 UPI Error Injection"""
    inj_upi(num_crcs=0)


@bios_setting("Default")
def Testcase_CPURAS_011():
    """11 PCIe Error Injection"""
    inj_pcie(socket=0, port=0, errType="ce")
    inj_pcie(errType="ce")
    inj_pcie(errType="uce")


@bios_setting("Default")
def Testcase_CPURAS_012():
    """12 LMCE功能测试"""
    if os_ssh.open_shell():
        os_ssh.install_driver()
        check_info("./unitool -r LmceEn", Testcase_CPURAS_012.__name__)
    print("msr(0x179)={:0>64b}".format(excmd("msr(0x179)")))
    print("msr(0x4D0)={:0>64b}".format(excmd("msr(0x4d0)")))


@bios_setting("Default")
def Testcase_CPURAS_013():
    """13 单lane瞬态错误（单bit错误），LLR成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 1, repr("random")), _halt=True, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)


@bios_setting("Default")
def Testcase_CPURAS_014():
    """14 单lane瞬态错误（单bit错误），LLR失败（kti{0|1|2}_lcl[11:8]寄存器配置max_num_retry），发起物理层重新初始化成功"""
    excmd(Cmd.upi_rxeinj, _halt=True, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)


@bios_setting("Default")
def Testcase_CPURAS_015():
    """15 多lane瞬态错误（多bit错误），LLR成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)


@bios_setting("Default")
def Testcase_CPURAS_016():
    """16 多lane瞬态错误（多bit错误），LLR失败（配置在kti{0|1|2}_lcl[11:8]寄存器配置max_num_retry），发起物理层重新初始化成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.upi_rxeinj, _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)


@bios_setting("Default")
def Testcase_CPURAS_017():
    """17 单bit或多bit错误，LLR失败，物理层重新初始化失败（kti{0|1|2}_lcl[13:12]寄存器配置max_num_phy_reinit)"""
    inj_upi(num_crcs=0)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)


@bios_setting("UpiFailover")
def Testcase_CPURAS_018():
    """18 UPI全带宽，PH_TDC [7:0]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 1, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CPURAS_019():
    """19 UPI全带宽，PH_TDC [19:12]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 1, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CPURAS_020():
    """20 UPI全带宽，PH_RDC [7:0]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 0, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CPURAS_021():
    """21 UPI全带宽，PH_RDC [19:12]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CPURAS_022():
    """22 16bit CRC UPI链路保护测试"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)
