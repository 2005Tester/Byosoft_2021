from HuaweiCommon.RASTest.SPR.Testcase_Mem import *


@bios_setting()
@check_dump("smi_storm", [1])
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=11)
def Testcase_SmiStorm_001():
    """内存注入可纠正故障风暴抑制功能测试"""
    inj_mem(count=12, errType="ce")


@bios_setting()
@check_dump("smi_storm", [1, 2, 3])
@check_dump("fdm_pcie_uce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=33)
def Testcase_SmiStorm_002():
    """PCIE non-fatal错误循环注入"""
    for i in range(smi_thld):
        inj_pcie(count=12, errType="uce")
        timer(smi_dis)
    inj_pcie(count=1, errType="uce")


@bios_setting()
@check_dump("smi_storm", [1])
@check_dump("fdm_pcie_ce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=11)
def Testcase_SmiStorm_003():
    """SMI风暴抑制功能测试"""
    inj_pcie(count=12, socket=Loc.psocket, port=Loc.pcie_port, errType="ce")


@bios_setting()
@check_dump("smi_storm", [1, 2, 3])
@check_dump("fdm_pcie_ce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=33)
def Testcase_SmiStorm_004():
    """SMI风暴永久抑制功能"""
    for i in range(smi_thld):
        inj_pcie(count=12, errType="ce")
        timer(smi_dis)
    inj_pcie(count=1, errType="ce")


@bios_setting()
@check_dump("smi_storm", [1])
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=11)
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_SmiStorm_005():
    """MCERR发生之后需要收集UCNA MCA"""
    inj_mem(count=12, errType="ce")
    timer(65)
    inj_mem(count=1, errType="uce")


@bios_setting()
@check_dump("smi_storm", [1, 2, 3])
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=33)
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_SmiStorm_006():
    """永久风暴抑制后发生MCERR时收集UCNA MCA"""
    for i in range(smi_thld):
        inj_mem(count=12, errType="ce")
        timer(smi_dis)
    inj_mem(count=1, errType="uce")


@bios_setting()
def Testcase_SmiStorm_007():
    """可纠正错误风暴抑制SMI NO不能为0"""
    n = 9
    for i in range(int(255 / n) + 1):
        inj_pcie(count=n, errType="ce", delay=1)
        timer(70)


@bios_setting()
def Testcase_OSMaskCeError_001():
    """检查MCA寄存器"""
    msr_52 = excmd(Cmd.msr.format("0x52", None))
    bit0 = bit(hex(msr_52), 0)
    bit1 = bit(hex(msr_52), 1)
    assert (bit0 == 1) and (bit1 == 1)


@bios_setting()
def Testcase_OSMaskCeError_002():
    """CE错误对OS屏蔽"""
    shell_cmd("dmesg -C")
    inj_mem(count=1)
    shell_cmd("dmesg", save_name=getframe().f_code.co_name)


@bios_setting()
def Testcase_OSMaskCeError_003():
    """PCIE CE错误对OS屏蔽"""
    shell_cmd("dmesg -C")
    inj_pcie(count=1)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


def Testcase_OSMaskCeError_004():
    """UCNA 错误对OS屏蔽"""
    Testcase_OSMaskCeError_002()


@bios_setting()
def Testcase_PcieNonFatal_001a():
    """PCIE non-fatal错误上报"""
    shell_cmd("dmesg -C")
    inj_pcie(count=3, socket=0, port=0, errType="uce")  # DMI
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting()
def Testcase_PcieNonFatal_001b():
    """PCIE non-fatal错误上报"""
    shell_cmd("dmesg -C")
    inj_pcie(count=3, errType="uce")
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting("PatrolScrub")
def Testcase_UceDowngrade_001():
    """支持不可纠正巡检错误降级设置"""
    shell_cmd("dmesg -C")
    cmd = 'socket={}, channel={}, dimm={}, rank={}, errType="uce", PatrolConsume=True'.format(
        Loc.msocket, Loc.ch, Loc.dimm, Loc.rank)
    excmd(Cmd.ei_dev.format(1, 2, 3, 4), _halt=False, _go=False)
    excmd(Cmd.inj_mem.format(cmd), delay=Delay.mem)
    excmd(Cmd.dump_mem_err, _halt=False)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting()
def Testcase_SmiCollectInfo_001():
    """同一个SMI中断中上报的信息SMI Number编号要保持一致"""
    inj_pcie(count=1)


@bios_setting("IERR")
def Testcase_PostErrReport_001():
    """注入CPU IERR测试"""
    excmd(Cmd.inj_ierr.format(0), delay=Delay.caterr)
    force_power_cycle()
    time.sleep(30)
    ping_sut(BOOT_TIMEOUT * 4)


@bios_setting()
def Testcase_PostErrReport_002():
    """注入内存UCE错误测试"""
    inj_mem(count=1, errType="uce")
    force_power_cycle()
    time.sleep(30)
    ping_sut(BOOT_TIMEOUT * 4)


@bios_setting("DebugMsg")
def Testcase_Dwr_002():
    """09 支持DWR特性"""
    inj_3s(socket=0)
    force_power_cycle()
    time.sleep(30)
    ping_sut()


@bios_setting()
@check_dump(error="fdm_pcie_ce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=1)
def Testcase_PcieUrErrorMask_001():
    """PCIe单次CE错误UR屏蔽测试"""
    inj_pcie(count=1, errType="ce")
    shell_cmd("lspci -s {} -vvv".format(Loc.pcie_os_bdf), save_path=getframe().f_code.co_name)


@bios_setting()
@check_dump(error="fdm_pcie_ce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=3)
def Testcase_PcieUrErrorMask_002():
    """PCIe多次CE错误UR屏蔽测试"""
    inj_pcie(count=3, errType="ce")
    shell_cmd("lspci -s {} -vvv".format(Loc.pcie_os_bdf), save_path=getframe().f_code.co_name)


@bios_setting()
@check_dump(error="fdm_pcie_uce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=1)
def Testcase_PcieUrErrorMask_003():
    """PCIe单次UCE故障UR屏蔽测试"""
    inj_pcie(count=1, errType="uce")
    shell_cmd("lspci -s {} -vvv".format(Loc.pcie_os_bdf), save_path=getframe().f_code.co_name)


@bios_setting()
@check_dump(error="fdm_pcie_uce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=3)
def Testcase_PcieUrErrorMask_004():
    """PCIe多次UCE故障UR屏蔽测试"""
    inj_pcie(count=3, errType="uce")
    shell_cmd("lspci -s {} -vvv".format(Loc.pcie_os_bdf), save_path=getframe().f_code.co_name)


@bios_setting()
def Testcase_PcieUrErrorMask_005():
    """PCIe 两个port同时注入CE错误"""
    inj_pcie(count=1, socket=0, port=0, errType="ce")
    inj_pcie(count=1, errType="ce")
    shell_cmd("lspci -s {} -vvv".format(Loc.pcie_os_bdf), save_path=getframe().f_code.co_name)


@bios_setting()
@check_dump(error="fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=1)
def Testcase_CeError_001():
    """ITP工具注入内存CE故障"""
    inj_mem(count=1, errType="ce")


@mark_skip(reason="内存槽位遍历需要满配内存测试")
@bios_setting("Dafault")
def Testcase_CeError_002():
    """ITP工具注入内存CE故障-槽位遍历"""
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    for socket in Sys.CPUs:
        for mc in Sys.MCs:
            for chan in Sys.CHs:
                ch = (mc * len(Sys.CHs)) + chan
                inj_mem(socket=socket, channel=ch, dimm=0, rank=1, errType="ce")
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)
    os_ssh.close_shell()


@bios_setting()
@check_dump(error="fdm_pcie_ce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=1)
def Testcase_CeError_003():
    """ITP工具注入PCIe CE故障"""
    inj_pcie(count=1, errType="ce")


@bios_setting()
@check_dump(error="fdm_upi_ce", socket=Loc.usocket, port=Loc.upi_port, crc=1, count=1)
def Testcase_CeError_006():
    """ITP工具注入UPI CE故障"""
    inj_upi(count=1, num_crcs=1)


@bios_setting()
def Testcase_CeError_007():
    """ITP工具注入UPI CE故障-CPU、UPI Port口遍历"""
    os_ssh.open_shell()
    os_ssh.exec_cmds(["dmesg -C\n"])
    for usocket in Sys.CPUs:
        for uport in Sys.UPIs:
            inj_upi(socket=usocket, port=uport, num_crcs=1)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)
    os_ssh.close_shell()


@bios_setting()
@check_dump(error="fdm_pcie_uce", socket=Loc.psocket, port=Loc.pcie_root_bdf, device=Loc.pcie_dev_name, count=1)
def Testcase_UceError_001():
    """ITP工具注入PCIE UCE故障"""
    inj_pcie(count=1, errType="uce")


@bios_setting()
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_UceError_002():
    """ITP工具注入内存UCE故障"""
    inj_mem(count=1, errType="uce")


@bios_setting()
@check_dump("fdm_upi_uce", socket=Loc.msocket, port=Loc.upi_port)
@check_dump("current_event", "Critical system error", "CPU\d UPI Link--\d.+CPU\d QPI/UPI link failed", "CPU\d UPI Link--\d.+CPU\d QPI/UPI link failed")
def Testcase_UceError_003():
    """ITP工具注入UPI UCE故障"""
    inj_upi(count=1, num_crcs=0)


@bios_setting("IERR")
@check_dump("fdm_ierr")
def Testcase_FDM_IERR_MCERR_001():  # IERR CPU槽位遍历
    """ITP工具注入CPU IERR故障"""
    core_count = int(excmd(Cmd.core_count))
    v_points = len(sv.sockets) * core_count * 2
    for vp in range(0, v_points, core_count * 2 + 1):
        excmd(Cmd.inj_ierr.format(vp), delay=Delay.caterr)
        force_power_cycle()
        time.sleep(30)
        ping_sut()


@bios_setting()
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_FDM_IERR_MCERR_002():
    """MEI卡内存多颗粒多bit故障注入"""
    excmd(Cmd.ei_dev.format(1, 2, 3, "f"))  # 注入多bit错误
    argvs = 'socket={}, channel={}, dimm={}, rank={}, errType="uce"'.format(
        Loc.msocket, Loc.ch, Loc.dimm, Loc.rank)
    excmd(Cmd.inj_mem.format(argvs), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)


@bios_setting()
@check_dump("fdm_3strike_timeout")
def Testcase_FDM_IERR_MCERR_004():
    """ITP工具CPU 3-strick故障注入"""
    inj_3s(socket=1)
    force_power_cycle()
    time.sleep(30)
    ping_sut()


@bios_setting()
@check_dump("fdm_3strike_timeout")
def Testcase_FDM_IERR_MCERR_005():
    """ITP注入3 Strike Timeout错误测试"""
    inj_3s(socket=0)
    force_power_cycle()
    time.sleep(30)
    ping_sut()


@bios_setting()
@check_dump("fdm_mcerr")
def Testcase_FDM_IERR_MCERR_006():
    """ITP工具注入CPU MCERR故障"""
    excmd(Cmd.inj_mcer, echo=True, delay=Delay.caterr)


def Testcase_FDM_IERR_MCERR_007():
    """ITP工具CDC内存Uce 故障注入"""
    Testcase_UceError_002()


@bios_setting("Legacy")
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_FDM_IERR_MCERR_008():
    """08 ITP工具legacy内存Uce故障注入"""
    inj_mem(count=1, errType="uce")


@bios_setting("ADDDC")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=4)
def Testcase_FDM_MEM_RAS_001():
    """Lockstep模式下地址解析测试_CE"""
    Testcase_MemRas_ADDDC_005()
    inj_mem(count=1, dev=5, errType="ce")


@bios_setting("ADDDC")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=3)
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_FDM_MEM_RAS_002():
    """Lockstep模式下地址解析测试_UCE"""
    Testcase_MemRas_ADDDC_005()
    inj_mem(count=1, dev=5, errType="uce")


@bios_setting("FullMirror")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=1)
def Testcase_FDM_MEM_RAS_003():
    """Mirror模式下地址解析测试_CE"""
    excmd(Cmd.dimminfo)
    inj_mem(count=1, errType="ce")


@bios_setting("FullMirror")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=1)
def Testcase_FDM_MEM_RAS_004():
    """Mirror模式下地址解析测试_UCE"""
    excmd(Cmd.dimminfo)
    inj_mem(count=1, errType="uce")


def Testcase_FDM_MEM_RAS_007():
    """SDDC功能测试"""
    Testcase_MemRas_ADDDC_013()


def Testcase_FDM_MEM_RAS_008():
    """触发RAS特性后日志记录测试"""
    Testcase_MemRas_ADDDC_013()


def Testcase_FDM_MEM_RAS_009():
    """故障隔离复判测试"""
    Testcase_MemRas_ADDDC_005()


@bios_setting("ADDDC")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=4)
def Testcase_FDM_MEM_RAS_010():
    """内存CE_overflow时间间隔测试"""
    inj_mem(count=1, errType="ce", delay=5)
    inj_mem(count=3, errType="ce", delay=30)


def Testcase_FDM_MEM_RAS_011():
    """内存CE错误触发CE_Bucket"""
    Testcase_MemRas_ADDDC_013()


def Testcase_FDM_MEM_RAS_013():
    """内存CE阈值和漏桶值测试"""
    shell_cmd("./unitool -r spareErrTh", save_path=getframe().f_code.co_name)


@bios_setting()
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, count=1)
def Testcase_FDM_Other_001():
    """不同CPU数量配置时，注入内存CE故障"""
    cprint("Current Socket Number: {}".format(len(sv.sockets)))
    inj_mem(count=1, errType="ce")


@bios_setting()
@check_dump("fdm_mem_uce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_FDM_Other_002():
    """不同CPU数量配置时，注入内存UCE故障"""
    cprint("Current Socket Number: {}".format(len(sv.sockets)))
    inj_mem(count=1, errType="uce")


@bios_setting()
def Testcase_FDM_Other_004():
    """内存CE Patrol Scrub故障注入"""
    shell_cmd("dmesg -C")
    cmd = 'socket={}, channel={}, dimm={}, rank={}, errType="ce", PatrolConsume=True'.format(
        Loc.msocket, Loc.ch, Loc.dimm, Loc.rank)
    excmd(Cmd.ei_dev.format(1, 2, 3, 0))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting()
def Testcase_FDM_Other_005():
    """内存UCE Patrol Scrub故障注入"""
    shell_cmd("dmesg -C")
    cmd = 'socket={}, channel={}, dimm={}, rank={}, errType="uce", PatrolConsume=True'.format(
        Loc.msocket, Loc.ch, Loc.dimm, Loc.rank)
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting()
@check_dump("fdm_pcie_ce", count=2)
def Testcase_FDM_Other_008():
    """两个PCIe Port同时注入CE错误"""
    shell_cmd("dmesg -C")
    inj_pcie(count=1, socket=0, port=0, errType="ce")
    inj_pcie(count=1, errType="ce")
    shell_cmd("lspci -s {} -vvv".format(Loc.pcie_os_bdf), save_path=getframe().f_code.co_name)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)
