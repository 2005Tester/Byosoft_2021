# -*- encoding=utf8 -*-

# memory
msocket = Loc.msocket
imc = Loc.imc
channel = Loc.channel
ch = Loc.ch
dimm = Loc.dimm
rank = Loc.rank

# pcie
psocket = Loc.psocket
pcie_port = Loc.pcie_port

# upi
usocket = Loc.usocket
upi_port = Loc.upi_port



# 支持SMI中断风暴屏蔽
@bios_setting("General")
def Testcase_FDM_SMI_001():
    inj_mem(count=12, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")


@bios_setting("General")
def Testcase_FDM_SMI_002():
    for i in range(smi_thld):
        inj_pcie(count=11, socket=psocket, port=pcie_port, errType="uce")
        timer(smi_dis)
    inj_pcie(socket=psocket, port=pcie_port, errType="uce")


@bios_setting("General")
def Testcase_FDM_SMI_003():
    inj_pcie(count=11, socket=psocket, port=pcie_port, errType="ce")


@bios_setting("General")
def Testcase_FDM_SMI_004():
    for i in range(smi_thld):
        inj_pcie(count=11, socket=psocket, port=pcie_port, errType="ce")
        timer(smi_dis)
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")


@bios_setting("General")
def Testcase_FDM_SMI_005():
    inj_mem(count=11, dev=1, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")
    timer(65)
    inj_mem(dev=5, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="uce")


@bios_setting("General")
def Testcase_FDM_SMI_006():
    for i in range(smi_thld):
        inj_mem(count=11, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")
        timer(smi_dis)
    inj_mem(dev=5, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="uce")


@bios_setting("General")
def Testcase_FDM_SMI_007():
    for i in range(int(255 / 10) + 1):
        inj_pcie(count=10, socket=psocket, port=pcie_port, errType="ce", delay=1)
        timer(61)


# 支持CE错误对OS屏蔽
@bios_setting("Default")
def Testcase_FDM_OS_CE_001():
    tc = sys._getframe().f_code.co_name
    halt()
    itp.msr(0x52)
    go()
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")
    check_info("dmesg", tc, "dmesg_mem_ce.log")
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")
    check_info("dmesg", tc, "dmesg_pcie_ce.log")
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(socket=0, port=0, errType="ce")
    check_info("dmesg", tc, "dmesg_dmi_ce.log")
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(socket=psocket, port=pcie_port, errType="uce")
    check_info("dmesg", tc, "dmesg_pcie_uce.log")
    os_ssh.close_shell()


#  支持PCIE Non-fatal错误上报
@bios_setting("General")
def Testcase_FDM_PcieNonFatal_001():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(count=3, socket=psocket, port=pcie_port, errType="uce")
    check_info("dmesg", sys._getframe().f_code.co_name, "dmesg.log")
    os_ssh.close_shell()


# 支持不可纠正巡检错误降级设置
@bios_setting("General")
def Testcase_FDM_PatrolScrub_001():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    cmd = 'socket={}, channel={}, dimm={}, rank=0, errType="uce", PatrolConsume=True'.format(msocket, ch, dimm)
    excmd(Cmd.inj_mem.format(cmd), delay=Dalay.mem)
    excmd(Cmd.dump_mem_err, halt=False, go=False)
    check_info("dmesg", sys._getframe().f_code.co_name, "dmesg.log")
    os_ssh.close_shell()


# 支持SMI（CSMI，AER）中断触发的故障寄存器信息搜集上报
@bios_setting("General")
def Testcase_FDM_SMI_CollectInfo_001():
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")


# 支持PCIE UR错误屏蔽
@bios_setting("General")
def Testcase_FDM_IIOUR_001():
    os_ssh.open_shell()
    inj_pcie(count=1, socket=psocket, port=pcie_port, errType="ce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)


@bios_setting("General")
def Testcase_FDM_IIOUR_002():
    os_ssh.open_shell()
    inj_pcie(count=3, socket=psocket, port=pcie_port, errType="ce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)


@bios_setting("General")
def Testcase_FDM_IIOUR_003():
    os_ssh.open_shell()
    inj_pcie(count=1, socket=psocket, port=pcie_port, errType="uce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)


@bios_setting("General")
def Testcase_FDM_IIOUR_004():
    os_ssh.open_shell()
    inj_pcie(count=3, socket=psocket, port=pcie_port, errType="uce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)


@bios_setting("Default")
def Testcase_FDM_IIOUR_005():
    os_ssh.open_shell()
    inj_pcie(count=1, socket=psocket, port=0, errType="ce")
    inj_pcie(count=1, socket=psocket, port=pcie_port, errType="ce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)


# CE故障注入测试
@bios_setting("Default")
def Testcase_FDM_CE_001():
    inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")


@bios_setting("Default")
def Testcase_FDM_CE_003():
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")


@bios_setting("Default")
def Testcase_FDM_CE_006():
    inj_upi(socket=usocket, port=upi_port, num_crcs=1)


@bios_setting("Default")
def Testcase_FDM_CE_007():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    for usocket in Sys.CPUs:
        for uport in Sys.UPIs:
            inj_upi(socket=usocket, port=uport, num_crcs=1)
    check_info("dmesg", sys._getframe().f_code.co_name)
    os_ssh.close_shell()


# UCE故障注入测试
@bios_setting("General")
def Testcase_FDM_UCE_001():
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")


@bios_setting("General")
def Testcase_FDM_UCE_002():
    inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=0, errType="uce")


@bios_setting("General")
def Testcase_FDM_UCE_003():
    inj_upi(socket=usocket, port=upi_port, num_crcs=0)


# IERR和MCERR
@bios_setting("General")
def Testcase_FDM_IERR_MCERR_001():
    inj_3s(socket=0)


@bios_setting("General")
def Testcase_FDM_IERR_MCERR_002():
    excmd(Cmd.ei_dev.format(1, 2, 3, "f"))
    argvs = 'socket={}, channel={}, dimm={}, rank={}, errType="uce"'.format(msocket, ch, dimm, rank)
    excmd(Cmd.inj_mem.format(argvs), delay=Delay.mem)


@bios_setting("General")
def Testcase_FDM_IERR_MCERR_004():
    inj_3s(socket=1)


@bios_setting("General")
def Testcase_FDM_IERR_MCERR_005():
    inj_3s(socket=0)


@bios_setting("General")
def Testcase_FDM_IERR_MCERR_006():
    excmd(Cmd.inj_mcer, echo=True, delay=Delay.caterr)


@bios_setting("General")
def Testcase_FDM_IERR_MCERR_007():
    Testcase_FDM_UCE_002()


@bios_setting("Legacy")
def Testcase_FDM_IERR_MCERR_008():
    inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=0, errType="uce")


# 内存RAS模式相关
@bios_setting("ADDDC")
def Testcase_FDM_MEM_RAS_001():
    Testcase_MemRAS_013()
    inj_mem(dev=5, socket=msocket, channel=ch, dimm=dimm, rank=0, bank_group=2, bank=2, errType="ce")


@bios_setting("ADDDC")
def Testcase_FDM_MEM_RAS_002():
    Testcase_MemRAS_013()
    inj_mem(dev=5, socket=msocket, channel=ch, dimm=dimm, rank=0, bank_group=2, bank=2, errType="uce")



@bios_setting("FullMirror")
def Testcase_FDM_MEM_RAS_003():
    inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")


@bios_setting("FullMirror")
def Testcase_FDM_MEM_RAS_004():
    inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=0, errType="uce")


def Testcase_FDM_MEM_RAS_007():
    Testcase_MemRAS_021()


def Testcase_FDM_MEM_RAS_008():
    Testcase_MemRAS_021()


def Testcase_FDM_MEM_RAS_009():
    Testcase_MemRAS_013()


@bios_setting("ADDDC")
def Testcase_FDM_MEM_RAS_010():
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce", delay=5)
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce", delay=30)


def Testcase_FDM_MEM_RAS_011():
    Testcase_MemRAS_021()


# 其他
@bios_setting("Default")
def Testcase_FDM_Other_001():
    print("Current Socket Number: {}".format(len(sv.sockets)))
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="ce")


@bios_setting("Default")
def Testcase_FDM_Other_002():
    print("Current Socket Number: {}".format(len(sv.sockets)))
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, rank=0, errType="uce")


@bios_setting("Default")
def Testcase_FDM_Other_004():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    cmd = 'socket={}, channel={}, dimm={}, rank=0, errType="ce", PatrolConsume=True'.format(msocket, ch, dimm)
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, halt=False, go=False)
    check_info("dmesg", sys._getframe().f_code.co_name)
    os_ssh.close_shell()


@bios_setting("Default")
def Testcase_FDM_Other_005():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    cmd = 'socket={}, channel={}, dimm={}, rank=0, errType="uce", PatrolConsume=True'.format(msocket, ch, dimm)
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, halt=False, go=False)
    check_info("dmesg", sys._getframe().f_code.co_name)
    os_ssh.close_shell()


@bios_setting("Default")
def Testcase_FDM_Other_008():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(count=1, socket=psocket, port=0, errType="ce")
    inj_pcie(count=1, socket=psocket, port=pcie_port, errType="ce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)
    check_info("dmesg", sys._getframe().f_code.co_name, "dmesg.log")
    os_ssh.close_shell()














