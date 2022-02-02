# -*- encoding=utf8 -*-
from HuaweiCommon.RASTest.SPR.TestLoader import *

"""
RAS(CPU)需求
"""

def _check_kti_mscod(code: int, socket=Loc.usocket, port=Loc.upi_port):
    assert excmd(f"sv.socket{socket}.uncore.upi.upi{port}.bios_kti_err_st.mscod_code"
                 ) == code, "[Assert] Check Mscod_Code Failed"
    return True


@bios_setting("Viral")
def Testcase_CpuRas_ViralMode_001():
    """Viral Mode默认使能测试"""
    excmd(Cmd.viral_check, _halt=True)


@bios_setting("Viral")
def Testcase_CpuRas_ViralMode_002():
    """Viral Mode注入PCIe UCE错误测试"""
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.comp_timeout_severity)
    inj_pcie(errType="uce")
    excmd(Cmd.iio_viral_show.format(Loc.psocket), _halt=False)
    excmd(Cmd.viral_state_pcie.format(Loc.psocket), _halt=False, delay=Delay.caterr)


@bios_setting("Viral")
def Testcase_CpuRas_ViralMode_003():
    """Viral Mode注入UPI UCE错误测试"""
    excmd(Cmd.upi_top)
    inj_upi(num_crcs=0)
    excmd(Cmd.iio_viral_show.format(Loc.usocket), _halt=False)
    excmd(Cmd.viral_state_upi.format(Loc.usocket), _halt=False)


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_001():
    """PCIe Uncorrectable Error"""
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    inj_pcie(errType="uce")


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_002a():
    """Memory Error Injection"""
    inj_cap()


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_002b():
    """Memory Error Injection"""
    inj_mem()


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_002c():
    """Memory Error Injection"""
    excmd(Cmd.inj_wcrc.format(Loc.msocket, Loc.imc, Loc.channel, Loc.sub_ch))


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_003a():
    """Core Error Injection"""
    inj_3s()


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_003b():
    """Core Error Injection"""
    excmd(Cmd.inj_mcer, delay=Delay.caterr)


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_003c():
    """Core Error Injection"""
    excmd(Cmd.inj_ierr.format(0), delay=Delay.caterr)


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_004a():
    """UPI Error Injection"""
    inj_upi(num_crcs=1)


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_004b():
    """UPI Error Injection"""
    inj_upi(num_crcs=0)


@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_004c():
    """UPI Error Injection"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 1, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting()
def Testcase_CpuRas_LocalMCE_001():
    """LMCE功能测试"""
    shell_cmd("./unitool -r LmceEn", save_path=getframe().f_code.co_name)
    cprint("msr(0x179)={:0>64b}".format(excmd("msr(0x179)")))
    cprint("msr(0x4D0)={:0>64b}".format(excmd("msr(0x4d0)")))


@bios_setting()
def Testcase_CpuRas_UPILinkRetry_001():
    """QPI Link Level Retry测试"""
    inj_upi(count=5, delay=20)
    inj_pcie(count=6, errType="ce", delay=20)
    timer(smi_dis)
    inj_upi(count=5, delay=20)
    inj_pcie(count=6, errType="ce", delay=20)
    timer(smi_dis)
    inj_upi(count=1, delay=20)
    inj_pcie(count=1, errType="ce", delay=20)
    inj_upi(count=1, port=0)


@bios_setting()
def Testcase_CpuRas_UPILinkRetry_002():
    """UPI Link Level Retry"""
    inj_upi(count=1, num_crcs=100)
    excmd(Cmd.dump_upi_err)


@bios_setting("UpiFailover")
def Testcase_CpuRas_UPDynamicLink_001():
    """UPI全带宽，PH_TDC [7:0]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 1, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CpuRas_UPDynamicLink_002():
    """UPI全带宽，PH_TDC [19:12]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 1, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CpuRas_UPDynamicLink_003():
    """UPI全带宽，PH_RDC [7:0]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 0, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("UpiFailover")
def Testcase_CpuRas_UPDynamicLink_004():
    """UPI全带宽，PH_RDC [19:12]范围单lane或多lane故障"""
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(Loc.usocket, Loc.upi_port, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting()
def Testcase_CpuRas_UPDynamicLink_005():
    """单lane瞬态错误（单bit错误），LLR成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 1, repr("random")), _halt=True, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)
    _check_kti_mscod(code=0x30)



@bios_setting()
def Testcase_CpuRas_UPDynamicLink_006():
    """单lane瞬态错误（单bit错误），LLR失败（kti{0|1|2}_lcl[11:8]寄存器配置max_num_retry），发起物理层重新初始化成功"""
    excmd(Cmd.upi_rxeinj, _halt=True, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)
    _check_kti_mscod(code=0x31)


@bios_setting()
def Testcase_CpuRas_UPDynamicLink_007():
    """多lane瞬态错误（多bit错误），LLR成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)
    _check_kti_mscod(code=0x30)


@bios_setting()
def Testcase_CpuRas_UPDynamicLink_008():
    """多lane瞬态错误（多bit错误），LLR失败（配置在kti{0|1|2}_lcl[11:8]寄存器配置max_num_retry），发起物理层重新初始化成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.upi_rxeinj, _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)
    _check_kti_mscod(code=0x31)


@bios_setting()
def Testcase_CpuRas_UPDynamicLink_009():
    """单bit或多bit错误，LLR失败，物理层重新初始化失败（kti{0|1|2}_lcl[13:12]寄存器配置max_num_phy_reinit)"""
    inj_upi(num_crcs=0)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)

