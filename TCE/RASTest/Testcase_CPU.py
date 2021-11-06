# -*- encoding=utf8 -*-

"""
RAS(CPU)需求
"""

msocket = Loc.msocket
imc = Loc.imc
channel = Loc.channel
ch = Loc.ch

usocket = Loc.usocket
uport = Loc.upi_port

psocket = Loc.psocket
pport = Loc.pcie_port

# 01 Viral Mode默认使能测试
@bios_setting("Viral")
def Testcase_CPURAS_001():
    excmd(Cmd.viral_check, _halt=True)

# 02 Viral Mode注入PCIe UCE错误测试
@bios_setting("Viral")
def Testcase_CPURAS_002():
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.comp_timeout_severity)
    inj_pcie(errType="uce")
    excmd(Cmd.iio_viral_show.format(psocket), _halt=False)
    excmd(Cmd.viral_state_pcie.format(psocket), _halt=False, delay=Delay.caterr)

# 03 Viral Mode注入UPI UCE错误测试
@bios_setting("Viral")
def Testcase_CPURAS_003():
    excmd(Cmd.upi_top)
    inj_upi(num_crcs=0)
    excmd(Cmd.iio_viral_show.format(usocket), _halt=False)
    excmd(Cmd.viral_state_upi.format(usocket), _halt=False)

# 08 Memory Error Injection
@bios_setting("WrCRC")
def Testcase_CPURAS_008():
    inj_cap()
    inj_mem()
    excmd(Cmd.inj_wcrc.format(msocket, imc, channel))

# 09 Core Error Injection
@bios_setting("Default")
def Testcase_CPURAS_009():
    print("""
    ========================================================
    请参考以下测试CASE:
    Testcase_FDM_IERR_MCERR_005     3-Strike Timeout
    Testcase_FDM_IERR_MCERR_001     IERR
    Testcase_FDM_IERR_MCERR_006     MCERR
    ========================================================
    """
    )

# 10 UPI Error Injection
@bios_setting("Default")
def Testcase_CPURAS_010():
    inj_upi(port=0, num_crcs=1)
    Testcase_CPURAS_018()
    inj_upi(num_crcs=0)

# 11 PCIe Error Injection
@bios_setting("Default")
def Testcase_CPURAS_011():
    inj_pcie(socket=0, port=0, errType="ce")
    inj_pcie(errType="ce")
    inj_pcie(errType="uce")

# 12 LMCE功能测试
@bios_setting("Default")
def Testcase_CPURAS_012():
    if os_ssh.open_shell():
        os_ssh.install_driver()
        check_info("./unitool -r LmceEn", sys._getframe().f_code.co_name)
    print("msr(0x179)={:0>64b}".format(excmd("msr(0x179)")))
    print("msr(0x4D0)={:0>64b}".format(excmd("msr(0x4d0)")))

# 13 单lane瞬态错误（单bit错误），LLR成功
@bios_setting("Default")
def Testcase_CPURAS_013():
    excmd(Cmd.inj_upi.format(usocket, uport, 1, repr("random")), _halt=True, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)

# 14 单lane瞬态错误（单bit错误），LLR失败（kti{0|1|2}_lcl[11:8]寄存器配置max_num_retry），发起物理层重新初始化成功
@bios_setting("Default")
def Testcase_CPURAS_014():
    excmd(Cmd.upi_rxeinj, _halt=True, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)

# 15 多lane瞬态错误（多bit错误），LLR成功
@bios_setting("Default")
def Testcase_CPURAS_015():
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)

# 16 多lane瞬态错误（多bit错误），LLR失败（配置在kti{0|1|2}_lcl[11:8]寄存器配置max_num_retry），发起物理层重新初始化成功
@bios_setting("Default")
def Testcase_CPURAS_016():
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 0, repr("random")), _halt=True, _go=False)
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 1, repr("random")), _halt=False, _go=False)
    excmd(Cmd.upi_rxeinj, _halt=False, _go=False)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)

# 17 单bit或多bit错误，LLR失败，物理层重新初始化失败（kti{0|1|2}_lcl[13:12]寄存器配置max_num_phy_reinit），
@bios_setting("Default")
def Testcase_CPURAS_017():
    inj_upi(num_crcs=0)
    excmd(Cmd.kti_mc_st, _halt=False, _go=False)

# 18 UPI全带宽，PH_TDC [7:0]范围单lane或多lane故障
@bios_setting("Default")
def Testcase_CPURAS_018():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 1, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)

# 19 UPI全带宽，PH_TDC [19:12]范围单lane或多lane故障
@bios_setting("Default")
def Testcase_CPURAS_019():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 1, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)

# 20 UPI全带宽，PH_RDC [7:0]范围单lane或多lane故障
@bios_setting("Default")
def Testcase_CPURAS_020():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 0, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)

# 21 UPI全带宽，PH_RDC [19:12]范围单lane或多lane故障
@bios_setting("Default")
def Testcase_CPURAS_021():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)

# 22 16bit CRC UPI链路保护测试
@bios_setting("Default")
def Testcase_CPURAS_022():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)
