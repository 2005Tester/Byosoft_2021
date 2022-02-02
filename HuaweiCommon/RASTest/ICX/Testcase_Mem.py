# -*- encoding=utf8 -*-
from HuaweiCommon.RASTest.ICX.RasConfig import *
from HuaweiCommon.RASTest.ICX.TestLoader import *

"""
内存相关的所有测试项目
"""

"""
FullMirror 功能测试
"""


def _check_mirror_mode():
    """测试前检查确认没有错误"""
    itp.halt()
    excmd(Cmd.dump_mem_err)
    excmd(Cmd.mem_mode.format(Loc.msocket, Loc.imc))
    excmd(Cmd.dimminfo)
    itp.go()
    excmd(Cmd.mem_mode.format(Loc.msocket, Loc.imc))


def _check_vls(vls):
    """检查是否触发ADDDC及是否正确组成VLS"""
    assert int(excmd(Cmd.adddc_sparing, echo=False))==1, "[Assert] No ADDDC Sparing"
    if vls.lower() == "bank":
        assert int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, 0), echo=False)) == 0, "[Assert] No Bank-VLS"
        return True
    if vls.lower() == "rank":
        assert int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, 0), echo=False)) == 1, "[Assert] No Rank-VLS"
        return True


def _trigger_vls(level="bank"):
    if level not in ("rank", "bank"):
        print(f"Invalid VLS level: {level}")
        return False
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    if level=="bank":
        return _check_vls(level)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    if level == "rank":
        return _check_vls(level)


@bios_setting("FullMirror")
@check_dump("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1)
def Testcase_MemRAS_001():
    """01 Mirror模式下注入可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    inj_mem(count=1, errType="ce", addr=Loc.full_mirr_addr)


@bios_setting("FullMirror")
@check_dump("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1, mscode="0X0101", options={"Mci_Misc": "Bit\(62\)MirrorCorrErr"})
def Testcase_MemRAS_002():
    """02 Primary通道注入不可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    inj_mem(count=1, errType="uce", addr=Loc.full_mirr_addr)
    excmd(Cmd.retry_rd.format(Loc.msocket, Loc.ch))

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorcorrerr": 1})


@bios_setting("FullMirror")
@check_dump("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1, mscode="0X0101", options={"Mci_Misc": "Bit\(62\)MirrorCorrErr"})
def Testcase_MemRAS_003():
    """03 Primary通道注入不可纠正错误，Secondary通道注入可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 0))
    excmd(Cmd.inj_mem.format(
        'addr={},errType="ce",immInject=False,immConsume=False,Inj2ndCh=True'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format(
        'addr={},errType="uce",immInject=True,immConsume=True,Inj2ndCh=False'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorcorrerr": 1,
                f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x30c})


@bios_setting("FullMirror")
@check_dump("fdm_mem_uce", only=False, err_type=["UCNA"], sysaddr=Loc.full_mirr_addr)
def Testcase_MemRAS_004():
    """04 两个通道都注入不可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_uce"'.format(hex(Loc.full_mirr_addr))), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x304})


@bios_setting("FullMirror")
@check_dump("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1, mscode="0X0101",
            options={"Mci_Misc": "Bit\(63\)MirrorFailover"})
def Testcase_MemRAS_005():
    """05 Mirror Failover"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x314})


"""
ArmMirror 功能测试
"""


@bios_setting("ArmMirror")
@check_dump()
def Testcase_MemRAS_006():
    """06 菜单设置ARM Mirror"""
    _check_mirror_mode()

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mode.mirrorddr4": 1})


@bios_setting("ArmMirror")
@check_dump("fdm_mem_ce", sysaddr=Loc.arm_mirr_addr, count=1, mscode="0X0101",
            options={"Mci_Misc": "Bit\(62\)MirrorCorrErr"})
def Testcase_MemRAS_007():
    """07 镜像地址范围内UCE错误"""
    _check_mirror_mode()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(hex(Loc.arm_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorcorrerr": 1,
                f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x30c})


@bios_setting("ArmMirror")
@check_dump("fdm_mem_ce", sysaddr=Loc.arm_mirr_addr, count=1, mscode="0X0101",
            options={"Mci_Misc": "Bit\(63\)MirrorFailover"})
def Testcase_MemRAS_008():
    """08 镜像地址范围内持续UCE"""
    _check_mirror_mode()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(hex(Loc.arm_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorcorrerr": 1,
                f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x314})


@bios_setting("ArmMirror")
@check_dump("fdm_mem_uce", only=False, err_type=["UCNA"], sysaddr=Loc.arm_non_mirr_addr, options={"MSCODE": "0X00A0"})
def Testcase_MemRAS_009():
    """09 非镜像地址范围UCE错误"""
    _check_mirror_mode()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(hex(Loc.arm_non_mirr_addr))), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)

    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.mc{Loc.imc}.ch{Loc.channel}.imc{Loc.imc}_mc_status_shadow.uc": 1})


"""
ADDDC 功能测试
"""


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 0 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 2"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3"])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 0 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 2", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_010():
    """10 1st Strike同rank，不同bank，不同dev注入CE错误"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=0)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 0"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 2"])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 0", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 2", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_011():
    """11 1st Strike同rank，同bank，不同dev注入CE错误"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=0)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 0 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1"])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 0 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1", 1, "DDDC sparing"])
def Testcase_MemRAS_012():
    """12 1st Strike同rank，不同bank，同dev注入CE错误"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=0)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=2)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False, [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3])
@check_dump("maint_mem_ce", [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"])
def Testcase_MemRAS_013():
    """13 1st Strike同rank，同bank，同dev注入CE错误"""
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3"])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_014():
    """14 2nd Strike同rank，同bank，不同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=2)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=2)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3"])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 2", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_015():
    """15 2nd Strike同rank，任意bank，不同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3, "DDDC sparing"])
def Testcase_MemRAS_016():
    """16 2nd Strike同rank，不同bank，同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("rank")


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 0 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1"])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 0 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 1", 1, "DDDC sparing"])
def Testcase_MemRAS_017():
    """17 2nd Strike同rank，不同bank，同dev（3次CE分布不同bank）"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=0)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("rank")


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2", 3])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2", 3, "DDDC sparing"])
def Testcase_MemRAS_018():
    """18 2nd Strike同rank，不同bank，不同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2", 3])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 2", 3, "DDDC sparing"])
def Testcase_MemRAS_019():
    """19 2nd Strike Bank VLS的buddy Bank注入3次CE错误"""
    _trigger_vls(level="bank")
    dimm0, buddy_rank, buddy_bg, buddy_ba, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=dimm0, rank=buddy_rank, bank_group=buddy_bg,
            bank=buddy_ba)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3", 1],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 4", 1],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 5", 1])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 3", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 4", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 2 5", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_020():
    """20 3rd Strike 同rank，不同dev"""
    _trigger_vls("rank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, bank=2)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=5, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 3", 1],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 3", 1],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 2 4", 1])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 3", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 3", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 2 4", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_021():
    """21 3rd Strike 同rank，任意bank，任意dev"""
    _trigger_vls("rank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank_group=2, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank_group=2, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, bank_group=2, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_022():
    """22 3rd Strike故障rank的buddy rank上"""
    _trigger_vls("rank")
    dimm0, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=dimm0, rank=buddy_rank)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
@check_dump("fdm_memce_array", False,
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 3", 1],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 4", 1],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 2 5", 1])
@check_dump("maint_mem_ce",
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} {Loc.bg} 1 1", 3, "DDDC sparing"],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 3", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 1 4", 1, ""],
            [f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank} 2 2 5", 1, "Memory_CE_Bucket"])
def Testcase_MemRAS_023():
    """23 3rd Strike与1、2在同一rank，但都不是相同dev"""
    _trigger_vls("rank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank_group=2, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, bank_group=2, bank=1)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=5, bank_group=2, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_024():
    """24 3rd Strike与1、2在不同rank，且是1或2的buddy"""
    _trigger_vls(level="bank")
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    _check_vls("bank")

    dimm0, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=dimm0, rank=buddy_rank, bank_group=buddy_bank_group, bank=buddy_bank)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


def Testcase_MemRAS_025():
    """25 3rd Strike同rank，任意bank，任意dev"""
    Testcase_MemRAS_021()


@bios_setting("PPR")
@check_dump("maint_mem_ppr", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm)
def Testcase_MemRAS_028():
    """28 PPR功能测试"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, rank=1, errType="ce")
    force_power_cycle()
    time.sleep(30)
    ping_sut()


@bios_setting("Default")
@check_dump("fdm_mem_ce", mscode="0X0200", mcacode="0X00B0", options={"Module": f".+IMC {Loc.imc} Chan {Loc.channel}"})
def Testcase_MemRAS_029():
    """29 Transient C/A Parity Error"""
    inj_cap()
    excmd(Cmd.alertsignal)


@bios_setting("Default")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, mscode="0X0008", mcacode="0X00C0")
def Testcase_MemRAS_032():
    """32 Patrol Scrubbing"""
    if os_ssh.open_shell():
        os_ssh.exec_cmds(["dmesg -C\n"])
        cmd = 'socket={}, channel={}, dimm={}, rank=0, errType="ce", PatrolConsume=True'.format(
            Loc.msocket, Loc.ch, Loc.dimm)
        excmd(Cmd.ei_dev.format(1, 2, 3, 0))
        excmd(Cmd.inj_mem.format(cmd))
        excmd(Cmd.dump_mem_err, _halt=False)
        check_info("dmesg", Testcase_MemRAS_032.__name__)
        os_ssh.close_shell()


@bios_setting("Default")
def Testcase_MemRAS_033():
    """33 Demand Scrub"""
    excmd(Cmd.dimminfo)


@bios_setting("Default")
def Testcase_MemRAS_034():
    """34 Data Scrambling"""
    if os_ssh.open_shell():
        os_ssh.install_driver()
        check_info("./unitool -r ScrambleEn", Testcase_MemRAS_034.__name__)
        os_ssh.close_shell()


@bios_setting("WrCRC")
@check_dump("fdm_mem_ce", mscode="0X0200", mcacode="0X00B0", options={"Module": f".+IMC {Loc.imc} Chan {Loc.channel}"})
def Testcase_MemRAS_035():
    """35 DDR4 Write Data CRC Protection"""
    excmd(Cmd.correrrorstatus)
    excmd(Cmd.alertsignal)
    excmd(Cmd.inj_wcrc.format(Loc.msocket, Loc.imc, Loc.channel))
    excmd(Cmd.alertsignal)


@bios_setting("WrCRC")
def Testcase_MemRAS_037():
    """37 内存Memory Thermal Throttling测试"""
    excmd(Cmd.show_field_reg.format("temp_hi"))
    excmd(Cmd.show_field_reg.format("temp_mid"))
    excmd(Cmd.show_field_reg.format("temp_lo"))
    excmd(Cmd.show_field_reg.format("dimm_temp"))
    excmd(Cmd.set_temp_lo)
    excmd(Cmd.set_temp_mid)


@bios_setting("Pcls")
@check_dump("fdm_mem_ce", socket=Loc.msocket, channel=Loc.channel, dimm=Loc.dimm, count=1)
def Testcase_MemRAS_038():
    """38.单Bit内存错误PCLS测试"""
    excmd(Cmd.pcls_cfg.format(Loc.msocket, Loc.imc, Loc.channel, 0))
    inj_mem(count=1, errType="ce")
    excmd(Cmd.pcls_cfg.format(Loc.msocket, Loc.imc, Loc.channel, 0))
    excmd(Cmd.show_pcls.format(Loc.msocket, Loc.imc, Loc.channel))


@bios_setting("Pcls")
def Testcase_MemRAS_039():
    """39. 单个通道注满16个PCLS Entry测试"""
    for rank in range(0, 2):
        for bg in range(0, 4):
            for ba in range(0, 2):
                inj_mem(socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, rank=rank, bank_group=bg, bank=ba, errType="ce")
                timer(20)
    excmd(Cmd.show_pcls.format(Loc.msocket, Loc.imc, Loc.channel))
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    inj_mem(count=3, bank_group=1, bank=3, errType="ce")
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))


@bios_setting("Pcls")
def Testcase_MemRAS_040():
    """40. 多Bit内存错误不触发PCLS测试"""
    excmd(Cmd.ei_dev.format(1, "f", 3, 0))  # 多Bit错误注入
    argvs = "socket={}, channel={}, dimm={}, rank={}, bank_group={}, bank={}, errType='ce', showErrorRegs=True".format(
        Loc.msocket, Loc.ch, Loc.dimm, Loc.rank, 3, 3)
    for i in range(3):
        excmd(Cmd.inj_mem.format(argvs), delay=Delay.mem)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc))
    excmd(Cmd.pcls_cfg.format(Loc.msocket, Loc.imc, Loc.channel, 0))
    excmd(Cmd.show_pcls.format(Loc.msocket, Loc.imc, Loc.channel))
