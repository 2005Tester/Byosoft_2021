# -*- encoding=utf8 -*-
from CommonTest.RASTest.ICX.RasConfig import *
from CommonTest.RASTest.ICX.TestLoader import *


@bios_setting("Default")
def Testcase_EDMA_001():
    """01 通过EDMA上报FDM信息"""
    bmc_web.blackbox_switch(True)
    inj_mem(count=1, errType="ce")


@bios_setting("Default")
def Testcase_EDMA_002():
    """02 通过EDMA一次上报多条FDM信息"""
    bmc_web.blackbox_switch(True)
    itp.halt()
    _inject_a = f"socket={Loc.msocket}, channel={Loc.ch}, dimm={Loc.dimm}, rank={Loc.rank}, bank_group=1, bank=1, errType='ce'"
    excmd(Cmd.inj_mem.format(_inject_a), delay=Delay.mem, _halt=False, _go=False)
    _inject_b = f"socket={Loc.msocket}, channel={Loc.ch}, dimm={Loc.dimm}, rank={Loc.rank}, bank_group=2, bank=2, errType='ce'"
    excmd(Cmd.inj_mem.format(_inject_b), delay=Delay.mem, _halt=False, _go=False)
    _inject_c = f"socket={Loc.msocket}, channel={Loc.ch}, dimm={Loc.dimm}, rank={Loc.rank}, bank_group=3, bank=2, errType='ce'"
    excmd(Cmd.inj_mem.format(_inject_c), delay=Delay.mem, _halt=False, _go=False)
    itp.go()


@bios_setting("Default")
def Testcase_EDMA_003():
    """03 通过EDMA上报FDM信息_故障类型覆盖"""
    bmc_web.blackbox_switch(True)
    inj_pcie(count=1, errType="ce")
    inj_pcie(count=1, errType="uce")
    inj_mem(count=1, errType="ce")
    inj_cap(count=1)


@bios_setting("Default")
def Testcase_EDMA_004():
    """03 通过EDMA上报FDM信息_故障类型覆盖"""
    bmc_web.blackbox_switch(False)
    inj_mem(count=1, errType="ce")


@msp_enable
@bios_setting("Default")
def Testcase_GPIOMulti_002():
    """02 GPIO复用功能_风暴抑制测试"""
    inj_mem(count=11, errType="ce")
    timer(smi_dis)
    inj_mem(count=1, errType="ce")


@msp_enable
@bios_setting("Default")
def Testcase_GPIOMulti_003():
    """03 GPIO复用功能_风暴抑制时触发硬隔离测试"""
    inj_mem(count=11, errType="ce")
    timer(smi_dis)
    inj_mem_rc(count=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, row=0x6000, column=0x500)


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_002():
    """02 BMC GPIO SMI触发RAS_ADDDC测试"""
    inj_mem_rc(count=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("PPR")
def Testcase_GPIORAS_003():
    """03 BMC GPIO SMI触发RAS_PPR测试"""
    inj_mem_rc(count=1, row=0x6000, column=0x500)
    inj_mem_rc(count=1, row=0x6000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_004():
    """04 硬隔离_一行地址触发Row Fault"""
    inj_mem_rc(count=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_005():
    """05 硬隔离_多行地址触发Row Fault"""
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=2, row=0x5000, column=0x600)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=2, row=0x5000, column=0x600)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_006():
    """06 硬隔离_一列地址触发Col Fault"""
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_007():
    """07 硬隔离_多列地址触发Col Fault"""
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=2, row=0x6000, column=0x500)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=2, row=0x6000, column=0x500)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=1, bank_group=1, bank=1, row=0x6000, column=0x500)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_008():
    """08 硬隔离_Bank内不同行列触发Bank隔离"""
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_009():
    """09 硬隔离_Dev内故障Bank达到3个，触发Dev隔离"""
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=1, row=0x6000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0=0, bank_group=1, bank=2, row=0x6000, column=0x600)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_010():
    """10 同颗粒单burst多DQ故障"""
    inj_mem_rc(count=1, dev0msk=0xf, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0xf, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    inj_mem_rc(count=1, dev0msk=0xf, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0xf, bank_group=1, bank=2, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0msk=0xf, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0xf, bank_group=1, bank=1, row=0x6000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_011():
    """11 同颗粒不同burst单DQ"""
    inj_mem_rc(count=1, dev0msk=0x10000001, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0x10000001, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    inj_mem_rc(count=1, dev0msk=0x10001001, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0x10001001, bank_group=1, bank=2, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0msk=0x10001001, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0x10001001, bank_group=1, bank=1, row=0x6000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_GPIORAS_012():
    """12 同颗粒不同burst多DQ"""
    inj_mem_rc(count=1, dev0msk=0xf000000f, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0xf000000f, bank_group=1, bank=1, row=0x5000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    inj_mem_rc(count=1, dev0msk=0xf000f00f, bank_group=1, bank=2, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0xf000f00f, bank_group=1, bank=2, row=0x6000, column=0x500)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))

    force_power_cycle()
    timer(30)
    ping_sut()

    inj_mem_rc(count=1, dev0msk=0xf000f00f, bank_group=1, bank=1, row=0x5000, column=0x500)
    inj_mem_rc(count=1, dev0msk=0xf000f00f, bank_group=1, bank=1, row=0x6000, column=0x600)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("ADDDC")
def Testcase_PageOffline_001():
    """01 内存PageOffline功能测试"""
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_mem(count=2, bank_group=1, bank=1, errType="ce")
    check_info("dmesg", Testcase_PageOffline_001.__name__)
    os_ssh.close_shell()


@msp_enable
@bios_setting("ADDDC")
def Testcase_PageOffline_002():
    """02 内存PageOffline功能_多个page地址测试"""
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_mem(count=2, bank_group=1, bank=1, errType="ce")
    check_info("dmesg", Testcase_PageOffline_002.__name__)
    inj_mem(count=2, bank_group=2, bank=2, errType="ce")
    check_info("dmesg", Testcase_PageOffline_002.__name__)
    os_ssh.close_shell()


@msp_enable
@bios_setting("ADDDC")
def Testcase_MSP_New_001():
    """1.同device4各bank各注入一次CE"""
    inj_mem(count=1, bank_group=1, bank=0, errType="ce")
    inj_mem(count=1, bank_group=1, bank=1, errType="ce")
    inj_mem(count=1, bank_group=1, bank=2, errType="ce")
    inj_mem(count=1, bank_group=1, bank=3, errType="ce")
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@msp_enable
@bios_setting("Default")
def Testcase_MSP_New_002():
    """1.同device4各bank各注入一次CE"""
    for i in range(smi_thld):
        inj_mem(count=12, errType="ce")
        timer(smi_dis)
    inj_mem(count=1, errType="ce")
