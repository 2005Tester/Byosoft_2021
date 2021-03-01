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


@bios_setting("Viral")
def Testcase_CPURAS_001():
    excmd(Cmd.viral_check, halt=True)


@bios_setting("Viral")
def Testcase_CPURAS_002():
    excmd(Cmd.pcie_top)
    excmd(Cmd.pcie_map)
    excmd(Cmd.comp_timeout_severity)
    inj_pcie(errType="uce")
    excmd(Cmd.iio_viral_show.format(psocket), halt=False)
    excmd(Cmd.viral_state.format(psocket), halt=False)


@bios_setting("Viral")
def Testcase_CPURAS_003():
    excmd(Cmd.upi_top)
    inj_upi(num_crcs=0)
    excmd(Cmd.iio_viral_show.format(usocket), halt=False)
    excmd(Cmd.viral_state.format(usocket), halt=False)


@bios_setting("WrCRC")
def Testcase_CPURAS_008():
    inj_cap()
    inj_mem()
    excmd(Cmd.inj_wcrc.format(msocket, imc, channel))


@bios_setting("Default")
def Testcase_CPURAS_009():
    inj_3s()
    excmd(Cmd.inj_mcer, delay=Delay.caterr)
    excmd(Cmd.inj_ierr, delay=Delay.caterr)


@bios_setting("Default")
def Testcase_CPURAS_010():
    inj_upi(num_crcs=1)
    inj_upi(num_crcs=0)


@bios_setting("Default")
def Testcase_CPURAS_011():
    inj_pcie(errType="ce")
    inj_pcie(errType="ce", port=0)
    inj_pcie(errType="uce")


@bios_setting("Default")
def Testcase_CPURAS_012():
    if os_ssh.open_shell():
        os_ssh.env_set()
        check_info("./unitool –r LmceEn", sys._getframe().f_code.co_name, logname="os.log")


@bios_setting("Default")
def Testcase_CPURAS_013():
    excmd(Cmd.inj_upi.format(usocket, uport, 1, repr("random")), halt=True, go=False)
    excmd(Cmd.kti_mc_st, halt=False, go=False)


@bios_setting("Default")
def Testcase_CPURAS_014():
    excmd(Cmd.upi_rxeinj, halt=True, go=False)
    excmd(Cmd.kti_mc_st, halt=False, go=False)


@bios_setting("Default")
def Testcase_CPURAS_015():
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 0, repr("random")), halt=True, go=False)
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 1, repr("random")), halt=False, go=False)
    excmd(Cmd.kti_mc_st, halt=False, go=False)


@bios_setting("Default")
def Testcase_CPURAS_016():
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 0, repr("random")), halt=True, go=False)
    excmd(Cmd.inj_upi.format(usocket, uport, 2, 1, repr("random")), halt=False, go=False)
    excmd(Cmd.upi_rxeinj, halt=False, go=False)
    excmd(Cmd.kti_mc_st, halt=False, go=False)


@bios_setting("Default")
def Testcase_CPURAS_017():
    inj_upi(num_crcs=0)
    excmd(Cmd.kti_mc_st, halt=False, go=False)


@bios_setting("Default")
def Testcase_CPURAS_018():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 1, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("Default")
def Testcase_CPURAS_019():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 1, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("Default")
def Testcase_CPURAS_020():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 0, hex(0x2)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("Default")
def Testcase_CPURAS_021():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)


@bios_setting("Default")
def Testcase_CPURAS_022():
    excmd(Cmd.upi_top)
    excmd(Cmd.inj_upi_failover.format(usocket, uport, 0, hex(0x2000)))
    excmd(Cmd.s_clm)
    excmd(Cmd.upi_top)
