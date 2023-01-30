# -*- encoding=utf8 -*-
from CommonTest.RASTest.SPR.TestLoader import *
from CommonTest.RASTest.SPR.Testcase_FDM import *


"""
RAS(CPU)需求
"""

def _check_kti_mscod(code: int, socket=Loc.usocket, port=Loc.upi_port):
    assert excmd(f"sv.socket{socket}.uncore.upi.upi{port}.bios_kti_err_st.mscod_code"
                 ) == code, "[Assert] Check Mscod_Code Failed"
    return True


def _inject_mca_error(err_type):
    try:
        excmd(Cmd.smm_en_break.format(1), _halt=True, _go=True)
        inj_mem(count=1, addr=0x1_1234_5000, errType=err_type)
        excmd(Cmd.smm_ex_break.format(1), _halt=True, _go=True)
        timer(120)
        excmd(Cmd.emca_dump)
    finally:
        excmd(Cmd.smm_en_break.format(0), _halt=True, _go=False)
        excmd(Cmd.smm_ex_break.format(0), _halt=False, _go=True)


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
@check_result()
def Testcase_CpuRas_MCA_002():
    """CDC模式配置与查询"""
    MCG_CAP = excmd(Cmd.MCG_CAP, _halt=True, _go=False)
    MCG_CONTAIN = excmd(Cmd.MCG_CONTAIN, _halt=False, _go=True)
    assert hex_bit(MCG_CAP, 24) == 1, "[Assert] MCG_CAP bit 24 != 1"  # MCG_SER_P
    assert hex_bit(MCG_CONTAIN, 0) == 1, "[Assert] MCG_CONTAIN bit 0 != 1"  # POISON_EN


@bios_setting()
@check_result()
def Testcase_CpuRas_MCA_003():
    """CMCI中断配置与查询"""
    def _set_bios(config: dict):
        if not ping_sut():
            force_power_cycle()
            assert ping_sut()
        os_ssh.set_config(config)
        force_power_cycle()
        ping_sut()

    MCG_CAP = excmd(Cmd.MCG_CAP, _halt=True, _go=False)
    MC0_CTL2 = excmd(Cmd.MC0_CTL2, _halt=False, _go=True)
    assert hex_bit(MCG_CAP, 10) == 1, "[Assert] MCG_CAP bit 10 != 1"  # MCP_CMCI_P
    assert hex_bit(MC0_CTL2, 30) == 1, "[Assert] MC0_CTL2 bit 30 != 1"  # CORRECTED_ERR_EN

    _set_bios(Bios.FDM_Disable)
    MCG_CAP_dis = excmd(Cmd.MCG_CAP, _halt=True, _go=False)
    MC0_CTL2_dis = excmd(Cmd.MC0_CTL2, _halt=False, _go=True)
    assert hex_bit(MCG_CAP_dis, 10) == 0, "[Assert] MCG_CAP_dis bit 10 != 0"  # MCP_CMCI_P
    assert hex_bit(MC0_CTL2_dis, 14, 0) == 0, "[Assert] MC0_CTL2_dis bit 14:0 != 0"  # CORRECTED_ERR_THRSH

    _set_bios(Bios.CMCI_Thld)
    MC0_CTL2_set = excmd(Cmd.MC0_CTL2, _halt=True, _go=True)
    assert hex_bit(MC0_CTL2_set, 14, 0) == list(Bios.CMCI_Thld.values())[0], "[Assert] MC0_CTL2_set bit 14:0 != 0x3fff"


@bios_setting()
@check_result()
def Testcase_CpuRas_MCA_004():
    """eMCA配置与查询"""
    shell_cmd("./unitool -r EmcaEn")
    assert os_ssh.read("EmcaEn").get("EmcaEn") == "1"


@bios_setting()
def Testcase_CpuRas_MCA_005():
    """MC Bank数查询"""
    MCG_CAP = excmd(Cmd.MCG_CAP)

    for _msr in range(0x400, 0x454, 1):
        print("MSR {} = {}".format(hex(_msr), hex(excmd(f"msr({hex(_msr)})") )))

    for _msr in range(0x474, 0x47f, 1):
        print("MSR {} = {}".format(hex(_msr), hex(excmd(f"msr({hex(_msr)})") )))

    assert hex_bit(MCG_CAP, 7, 0) == 23, "[Assert] MC Banks count != 23"


@bios_setting("ADDDC")
@check_result("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=1)
def Testcase_CpuRas_MCA_009():
    shell_cmd("dmesg -C")
    inj_mem(count=1, errType="ce")
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


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


# @bios_setting()
# def Testcase_CpuRas_ErrorInjectSupport_002c():
#     """Memory Error Injection"""
#     excmd(Cmd.inj_wcrc.format(Loc.msocket, Loc.imc, Loc.channel, Loc.sub_ch))


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
def Testcase_CpuRas_ErrorInjectSupport_005():
    """Correctable Error Reporting"""
    shell_cmd("dmesg -C")
    excmd(Cmd.dimminfo)
    excmd(Cmd.emca_config)
    _inject_mca_error(err_type="ce")
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)



@bios_setting()
def Testcase_CpuRas_ErrorInjectSupport_006():
    """Uncorrectable Error Reporting"""
    excmd(Cmd.dimminfo)
    excmd(Cmd.emca_config)
    _inject_mca_error(err_type="uce")


@bios_setting()
@check_result()
def Testcase_CpuRas_LocalMCE_001():
    """LMCE功能测试"""
    shell_cmd("./unitool -r LmceEn", save_path=getframe().f_code.co_name)
    MCG_CAP = excmd(Cmd.MCG_CAP)
    MCG_EXT_CTL = excmd(Cmd.MCG_EXT_CTL)
    cprint("msr(0x179)={:0>64b}".format(MCG_CAP))
    cprint("msr(0x4D0)={:0>64b}".format(MCG_EXT_CTL))
    assert hex_bit(MCG_CAP, 27) == 1, "[Assert] MCG_CAP bit 27 != 1"
    assert hex_bit(MCG_EXT_CTL, 0) == 1, "[Assert] MCG_EXT_CTL bit 0 != 1"


def Testcase_CpuRas_LocalMCE_002():
    """Local MCE"""
    Testcase_FDM_IERR_MCERR_002()


@bios_setting()
def Testcase_CpuRas_UPILinkRetry_001():
    """QPI Link Level Retry测试"""
    inj_upi(count=5, delay=20)
    inj_pcie(count=6, errType="ce", delay=20)
    timer(smi_dis)
    inj_upi(count=5, delay=20)
    inj_pcie(count=6, errType="ce", delay=20)
    timer(smi_dis)
    inj_upi(count=5, delay=20)
    inj_pcie(count=6, errType="ce", delay=20)
    timer(smi_dis)
    inj_upi(count=1, port=0)
    inj_pcie(count=1, socket=0, port=0, errType="ce")


@bios_setting()
def Testcase_CpuRas_UPILinkRetry_002():
    """UPI Link Level Retry"""
    shell_cmd("dmesg -C")
    inj_upi(count=1, num_crcs=100)
    excmd(Cmd.dump_upi_err)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


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
    _check_kti_mscod(code=0x31)  # follow V6 test result


@bios_setting()
def Testcase_CpuRas_UPDynamicLink_007():
    """多lane瞬态错误（多bit错误），LLR成功"""
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(Loc.usocket, Loc.upi_port, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)
    _check_kti_mscod(code=0x30)


@bios_setting("UpiLane")
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

