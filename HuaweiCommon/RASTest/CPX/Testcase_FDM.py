# -*- encoding=utf8 -*-
# from HY5.RASTest.RasConfig import *
# from HY5.RASTest.TestLoader import *


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

# 01 内存注入可纠正故障风暴抑制功能测试
@bios_setting("Default")
def Testcase_FDM_SMI_001():
    inj_mem(count=12, errType="ce")

# 02 PCIE non-fatal错误循环注入
@bios_setting("Default")
def Testcase_FDM_SMI_002():
    for i in range(smi_thld):
        inj_pcie(count=12,  errType="uce")
        timer(smi_dis)
    inj_pcie(count=1, errType="uce")

# 03 SMI风暴抑制功能测试
@bios_setting("Default")
def Testcase_FDM_SMI_003():
    inj_pcie(count=12, socket=psocket, port=pcie_port, errType="ce")

# 04 SMI风暴永久抑制功能
@bios_setting("Default")
def Testcase_FDM_SMI_004():
    for i in range(smi_thld):
        inj_pcie(count=12, errType="ce")
        timer(smi_dis)
    inj_pcie(count=1, errType="ce")

# 05 MCERR发生之后需要收集UCNA MCA
@bios_setting("Default")
def Testcase_FDM_SMI_005():
    inj_mem(count=12, errType="ce")
    timer(65)
    inj_mem(count=1, errType="uce")

# 06 永久风暴抑制后发生MCERR时收集UCNA MCA
@bios_setting("Default")
def Testcase_FDM_SMI_006():
    for i in range(smi_thld):
        inj_mem(count=12, errType="ce")
        timer(smi_dis)
    inj_mem(count=1, errType="uce")

# 07 可纠正错误风暴抑制SMI NO不能为0
@bios_setting("Default")
def Testcase_FDM_SMI_007():
    n = 9
    for i in range(int(255 / n) + 1):
        inj_pcie(count=n, errType="ce", delay=1)
        timer(70)


# 支持CE错误对OS屏蔽
@bios_setting("Default")
def Testcase_FDM_OS_CE_001():
    tc = sys._getframe().f_code.co_name
    halt()
    itp.msr(0x52)
    go()
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_mem(count=1, errType="ce")
    check_info("dmesg", tc, "dmesg_mem_ce")
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")
    check_info("dmesg", tc, "dmesg_pcie_ce")
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(socket=0, port=0, errType="ce")
    check_info("dmesg", tc, "dmesg_dmi_ce")
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(socket=psocket, port=pcie_port, errType="uce")
    check_info("dmesg", tc, "dmesg_pcie_uce")
    os_ssh.close_shell()


#  支持PCIE Non-fatal错误上报
@bios_setting("Default")
def Testcase_FDM_PcieNonFatal_001():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(count=3, socket=0, port=0, errType="uce")
    inj_pcie(count=3, errType="uce")
    check_info("dmesg", sys._getframe().f_code.co_name, "dmesg")
    os_ssh.close_shell()


# 01 不可纠正巡检错误降级
@bios_setting("Default")
def Testcase_FDM_PatrolScrub_001():
    if os_ssh.open_shell():
        os_ssh.exec_cmds(["dmesg -C\n"])
        cmd = 'socket={}, channel={}, dimm={}, rank={}, errType="uce", PatrolConsume=True'.format(msocket, ch, dimm, rank)
        excmd(Cmd.ei_dev.format(1, 2, 3, 4), _halt=False, _go=False)
        excmd(Cmd.inj_mem.format(cmd), delay=Delay.mem)
        excmd(Cmd.dump_mem_err, _halt=False)
        check_info("dmesg", sys._getframe().f_code.co_name, "dmesg")
        os_ssh.close_shell()


# 01 同一个SMI中断中上报的信息SMI Number编号要保持一致
@bios_setting("Default")
def Testcase_FDM_SMI_CollectInfo_001():
    inj_pcie(socket=psocket, port=pcie_port, errType="ce")


# 01 注入CPU IERR测试
@bios_setting("IERR_Debug")
def Testcase_FDM_PostErrReport_001():
    excmd(Cmd.inj_ierr.format(0), delay=Delay.caterr)
    force_power_cycle(bmc_ssh)
    time.sleep(30)
    ping_sut(BOOT_TIMEOUT*4)

# 02 注入内存UCE错误测试
@bios_setting("DebugMsg")
def Testcase_FDM_PostErrReport_002():
    inj_mem(count=1, errType="uce")
    force_power_cycle(bmc_ssh)
    time.sleep(30)
    ping_sut(BOOT_TIMEOUT * 4)

# 09 支持DWR特性
@bios_setting("DebugMsg")
def Testcase_FDM_DWR_002():
    inj_3s(socket=0)
    force_power_cycle(bmc_ssh)
    time.sleep(30)
    ping_sut()
    excmd(Cmd.inj_ierr.format(0), delay=Delay.caterr)
    force_power_cycle(bmc_ssh)
    time.sleep(30)
    ping_sut()

# 01 PCIe单次CE错误UR屏蔽测试
@bios_setting("Default")
def Testcase_FDM_IIOUR_001():
    inj_pcie(count=1, errType="ce")
    os_ssh.open_shell()
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)

# 02 PCIe多次CE错误UR屏蔽测试
@bios_setting("Default")
def Testcase_FDM_IIOUR_002():
    inj_pcie(count=3, errType="ce")
    os_ssh.open_shell()
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)

# 03 PCIe单次UCE故障UR屏蔽测试
@bios_setting("Default")
def Testcase_FDM_IIOUR_003():
    inj_pcie(count=1, errType="uce")
    os_ssh.open_shell()
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)

# 04 PCIe多次UCE故障UR屏蔽测试
@bios_setting("Default")
def Testcase_FDM_IIOUR_004():
    inj_pcie(count=3, errType="uce")
    os_ssh.open_shell()
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)

# 05 PCIe 两个port同时注入CE错误
@bios_setting("Default")
def Testcase_FDM_IIOUR_005():
    inj_pcie(count=1, socket=0, port=0, errType="ce")
    inj_pcie(count=1, errType="ce")
    os_ssh.open_shell()
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)


# 01 ITP工具注入内存CE故障
@bios_setting("Default")
def Testcase_FDM_CE_001():
    inj_mem(count=1, errType="ce")

# 02 ITP工具注入内存CE故障-槽位遍历
@bios_setting("Dafault")
def Testcase_FDM_CE_002():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    for socket in Sys.CPUs:
        for mc in Sys.MCs:
            for chan in Sys.CHs:
                ch = (mc * len(Sys.CHs)) + chan
                inj_mem(socket=socket, channel=ch, dimm=0, rank=1, errType="ce")
    check_info("dmesg", sys._getframe().f_code.co_name, "dmesg")
    os_ssh.close_shell()

# 03 ITP工具注入PCIe CE故障
@bios_setting("Default")
def Testcase_FDM_CE_003():
    inj_pcie(count=1, errType="ce")

# 06 ITP工具注入UPI CE故障
@bios_setting("Default")
def Testcase_FDM_CE_006():
    inj_upi(count=1, num_crcs=1)

# 07 ITP工具注入UPI CE故障-CPU、UPI Port口遍历
@bios_setting("Default")
def Testcase_FDM_CE_007():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    for usocket in Sys.CPUs:
        for uport in Sys.UPIs:
            inj_upi(socket=usocket, port=uport, num_crcs=1)
    check_info("dmesg", sys._getframe().f_code.co_name)
    os_ssh.close_shell()


# 01 ITP工具注入PCIE UCE故障
@bios_setting("Default")
def Testcase_FDM_UCE_001():
    inj_pcie(count=1, errType="uce")

# 02 ITP工具注入内存UCE故障
@bios_setting("Default")
def Testcase_FDM_UCE_002():
    inj_mem(count=1, errType="uce")

# 03 ITP工具注入UPI UCE故障
@bios_setting("Default")
def Testcase_FDM_UCE_003():
    inj_upi(count=1, num_crcs=0)


# 01 ITP工具注入CPU IERR故障
@bios_setting("IERR")
def Testcase_FDM_IERR_MCERR_001():  # IERR CPU槽位遍历
    core_count = excmd(Cmd.core_count)
    v_points = len(sv.sockets)*core_count*2
    for vp in range(0, v_points, core_count*2+1):
        excmd(Cmd.inj_ierr.format(vp), delay=Delay.caterr)
        force_power_cycle(bmc_ssh)
        time.sleep(30)
        ping_sut()

# 02 MEI卡内存多颗粒多bit故障注入
@bios_setting("Default")
def Testcase_FDM_IERR_MCERR_002():
    excmd(Cmd.ei_dev.format(1, 2, 3, "f"))  # 注入多bit错误
    argvs = 'socket={}, channel={}, dimm={}, rank={}, errType="uce"'.format(msocket, ch, dimm, rank)
    excmd(Cmd.inj_mem.format(argvs), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)

# 04 ITP工具CPU 3-strick故障注入
@bios_setting("Default")
def Testcase_FDM_IERR_MCERR_004():
    inj_3s(socket=1)
    force_power_cycle(bmc_ssh)
    time.sleep(30)
    ping_sut()

# 05 ITP注入3 Strike Timeout错误测试
@bios_setting("Default")
def Testcase_FDM_IERR_MCERR_005():
    inj_3s(socket=0)
    force_power_cycle(bmc_ssh)
    time.sleep(30)
    ping_sut()

# 06 ITP工具注入CPU MCERR故障
@bios_setting("Default")
def Testcase_FDM_IERR_MCERR_006():
    excmd(Cmd.inj_mcer, echo=True, delay=Delay.caterr)

# 07 ITP工具CDC内存Uce 故障注入
def Testcase_FDM_IERR_MCERR_007():
    Testcase_FDM_UCE_002()

# 08 ITP工具legacy内存Uce故障注入
@bios_setting("Legacy")
def Testcase_FDM_IERR_MCERR_008():
    inj_mem(count=1, errType="uce")


# 01 Lockstep模式下地址解析测试_CE
@bios_setting("ADDDC")
def Testcase_FDM_MEM_RAS_001():
    Testcase_MemRAS_013()
    inj_mem(count=1, dev=5, errType="ce")

# 02 Lockstep模式下地址解析测试_UCE
@bios_setting("ADDDC")
def Testcase_FDM_MEM_RAS_002():
    Testcase_MemRAS_013()
    inj_mem(count=1, dev=5, errType="uce")

# 03 Mirror模式下地址解析测试_CE
@bios_setting("FullMirror")
def Testcase_FDM_MEM_RAS_003():
    excmd((Cmd.dimminfo))
    inj_mem(count=1, errType="ce")

# 04 Mirror模式下地址解析测试_UCE
@bios_setting("FullMirror")
def Testcase_FDM_MEM_RAS_004():
    excmd((Cmd.dimminfo))
    inj_mem(count=1, errType="uce")

# 07 SDDC功能测试
def Testcase_FDM_MEM_RAS_007():
    Testcase_MemRAS_021()

# 08 触发RAS特性后日志记录测试
def Testcase_FDM_MEM_RAS_008():
    Testcase_MemRAS_021()

# 09 故障隔离复判测试
def Testcase_FDM_MEM_RAS_009():
    Testcase_MemRAS_013()

# 10 内存CE_overflow时间间隔测试
@bios_setting("ADDDC")
def Testcase_FDM_MEM_RAS_010():
    inj_mem(count=1, errType="ce", delay=5)
    inj_mem(count=3, errType="ce", delay=30)

# 11 内存CE错误触发CE_Bucket
def Testcase_FDM_MEM_RAS_011():
    Testcase_MemRAS_021()

# 13 内存CE阈值和漏桶值测试
@bios_setting("Default")
def Testcase_FDM_MEM_RAS_013():
    if os_ssh.open_shell():
        os_ssh.install_driver()
        check_info("./unitool -r spareErrTh", sys._getframe().f_code.co_name)
        os_ssh.close_shell()


# 01 不同CPU数量配置时，注入内存CE故障
@bios_setting("Default")
def Testcase_FDM_Other_001():
    print("Current Socket Number: {}".format(len(sv.sockets)))
    inj_mem(count=1, errType="ce")

# 02 不同CPU数量配置时，注入内存UCE故障
@bios_setting("Default")
def Testcase_FDM_Other_002():
    print("Current Socket Number: {}".format(len(sv.sockets)))
    inj_mem(count=1, errType="uce")

# 04 内存CE Patrol Scrub故障注入
@bios_setting("Default")
def Testcase_FDM_Other_004():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    cmd = 'socket={}, channel={}, dimm={}, rank={}, errType="ce", PatrolConsume=True'.format(msocket, ch, dimm, rank)
    excmd(Cmd.ei_dev.format(1, 2, 3, 0))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    check_info("dmesg", sys._getframe().f_code.co_name)
    os_ssh.close_shell()

# 05 内存UCE Patrol Scrub故障注入
@bios_setting("Default")
def Testcase_FDM_Other_005():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    cmd = 'socket={}, channel={}, dimm={}, rank={}, errType="uce", PatrolConsume=True'.format(msocket, ch, dimm, rank)
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    check_info("dmesg", sys._getframe().f_code.co_name)
    os_ssh.close_shell()

# 08 两个PCIe Port同时注入CE错误
@bios_setting("Default")
def Testcase_FDM_Other_008():
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    inj_pcie(count=1, socket=0, port=0, errType="ce")
    inj_pcie(count=1, errType="ce")
    check_info("lspci -s {} -vvv".format(Loc.pcie_dev_BDF), sys._getframe().f_code.co_name)
    check_info("dmesg", sys._getframe().f_code.co_name, "dmesg")
    os_ssh.close_shell()















