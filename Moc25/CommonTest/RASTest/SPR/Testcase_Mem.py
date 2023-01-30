# -*- encoding=utf8 -*-
from CommonTest.RASTest.SPR.TestLoader import *

"""
RAS(内存)需求
"""
_DIMM_LOC = f"{Loc.msocket} {Loc.ch} {Loc.dimm} {Loc.rank + Loc.sub_ch * (len(Sys.SUB_CHs))}"


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


def _check_mem_err_count(socket=Loc.msocket, mc=Loc.imc, ch=Loc.channel, count=1):
    assert excmd(f"sv.socket{socket}.uncore.memss.mc{mc}.ch{ch}.imc0_mc_status_shadow.cor_err_cnt"
                 ) == count, "[Assert] Check mem correct error count failed"
    return True


def _trigger_vls(level="bank"):
    if level not in ("rank", "bank"):
        cprint(f"Invalid VLS level: {level}")
        return False
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, delay=Delay.mem_ov)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    if level=="bank":
        return _check_vls(level)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=1, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    if level == "rank":
        return _check_vls(level)


@bios_setting("FullMirror")
def Testcase_MemRas_MirrorMode_001():
    """Mirror模式功能测试"""
    _check_mirror_mode()


@bios_setting("FullMirror")
@check_result("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1)
def Testcase_MemRas_MirrorMode_002():
    """Mirror模式下注入可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    inj_mem(count=1, errType="ce", addr=Loc.full_mirr_addr)


@bios_setting("FullMirror")
@check_result("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1, mscode="0X0101", options={"Mci_Misc": "Bit\(62\)MirrorCorrErr"})
def Testcase_MemRas_MirrorMode_003():
    """Primary通道注入不可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    inj_mem(count=1, errType="uce", addr=Loc.full_mirr_addr)
    excmd(Cmd.retry_rd.format(Loc.msocket, Loc.imc, Loc.ch))
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorcorrerr": 1})


@bios_setting("FullMirror")
@check_result("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1, mscode="0X0101", options={"Mci_Misc": "Bit\(62\)MirrorCorrErr"})
def Testcase_MemRas_MirrorMode_004():
    """Primary通道注入不可纠正错误，Secondary通道注入可纠正错误"""
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
@check_result("fdm_mem_uce", only=False, err_type=["UCNA"], sysaddr=Loc.full_mirr_addr)
def Testcase_MemRas_MirrorMode_005():
    """两个通道都注入不可纠正错误"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_uce"'.format(hex(Loc.full_mirr_addr))), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x304})


@bios_setting("FullMirror")
@check_result("fdm_mem_ce", sysaddr=Loc.full_mirr_addr, count=1, mscode="0X0101",
              options={"Mci_Misc": "Bit\(63\)MirrorFailover"})
def Testcase_MemRas_MirrorMode_006():
    """Mirror Failover"""
    _check_mirror_mode()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x314})


"""
UEFI ARM Mirror 功能测试
"""


@bios_setting("ArmMirror")
@check_result()
def Testcase_MemRas_UEFIARMMirror_001():
    """菜单设置ARM Mirror"""
    _check_mirror_mode()
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mode.mirrorddr4": 1})


@bios_setting("ArmMirror")
@check_result("fdm_mem_ce", sysaddr=Loc.arm_mirr_addr, count=1, mscode="0X0101",
              options={"Mci_Misc": "Bit\(62\)MirrorCorrErr"})
def Testcase_MemRas_UEFIARMMirror_002():
    """镜像地址范围内UCE错误"""
    _check_mirror_mode()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(hex(Loc.arm_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorcorrerr": 1,
                f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x30c})


@bios_setting("ArmMirror")
@check_result("fdm_mem_ce", sysaddr=Loc.arm_mirr_addr, count=1, mscode="0X0101",
              options={"Mci_Misc": "Bit\(63\)MirrorFailover"})
def Testcase_MemRas_UEFIARMMirror_003():
    """镜像地址范围内Mirror Failover"""
    _check_mirror_mode()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(hex(Loc.arm_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.mirrorfailover": 1,
                f"sv.socket{Loc.msocket}.uncore.memss.m2mem{Loc.imc}.mci_misc_shadow.errortype": 0x314})


@bios_setting("ArmMirror")
@check_result("fdm_mem_uce", only=False, err_type=["UCNA"], sysaddr=Loc.arm_non_mirr_addr, options={"MSCODE": "0X00A0"})
def Testcase_MemRas_UEFIARMMirror_004():
    """非镜像地址范围UCE错误"""
    _check_mirror_mode()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(hex(Loc.arm_non_mirr_addr))), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.mc{Loc.imc}.ch{Loc.channel}.imc{Loc.imc}_mc_status_shadow.uc": 1})


@bios_setting()
@check_result("fdm_mem_ce", mscode="0X0200", mcacode="0X00B0", options={"Module": f".+IMC {Loc.imc} Chan {Loc.channel}"})
def Testcase_MemRas_CA_ParityError_002():
    """Transient C/A Parity Error"""
    inj_cap()
    excmd(Cmd.alertsignal)
    assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.mc{Loc.imc}.ch{Loc.channel}.alertsignal.seen":1})

"""
X4 ADDDC/ADDDC+1 测试
"""
@bios_setting("ADDDC")
def Testcase_MemRas_ADDDC_001():
    """Lockstep模式功能测试"""
    excmd(Cmd.dimminfo)
    _trigger_vls("bank")
    excmd(Cmd.dimminfo)



@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} 0 1"],
              [f"{_DIMM_LOC} {Loc.bg} 1 2"],
              [f"{_DIMM_LOC} {Loc.bg} 2 3"])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} 0 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 1 2", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 3", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_002():
    """1st Strike同rank，不同bank，不同dev注入CE错误"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=0, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2, delay=Delay.mem_ov)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 0"],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1"],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 2"])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 0", 1, ""],
              [f"{_DIMM_LOC} {Loc.ba} 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 2", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_003():
    """1st Strike同rank，同bank，不同dev注入CE错误"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=0, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, delay=Delay.mem_ov)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} 0 1"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1"],
              [f"{_DIMM_LOC} {Loc.bg} 2 1"])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} 0 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 1", 1, "DDDC sparing"])
def Testcase_MemRas_ADDDC_004():
    """1st Strike同rank，不同bank，同dev注入CE错误"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=0, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=2, delay=Delay.mem_ov)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False, [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3])
@check_result("maint_mem_ce", [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"])
def Testcase_MemRas_ADDDC_005():
    """1st Strike同rank，同bank，同dev注入CE错误"""
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, delay=Delay.mem_ov)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 2 1"],
              [f"{_DIMM_LOC} {Loc.bg} 2 2"],
              [f"{_DIMM_LOC} {Loc.bg} 2 3"])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 2 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 2", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 3", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_006():
    """2nd Strike同rank，同bank，不同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=2, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=2, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 1 1"],
              [f"{_DIMM_LOC} {Loc.bg} 1 2"],
              [f"{_DIMM_LOC} {Loc.bg} 2 3"])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 1 2", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 3", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_007():
    """2nd Strike同rank，任意bank，不同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3, "DDDC sparing"])
def Testcase_MemRas_ADDDC_008():
    """2nd Strike同rank，不同bank，同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, bank=1, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("rank")


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 0 1"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1"],
              [f"{_DIMM_LOC} {Loc.bg} 2 1"])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 0 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 1", 1, "DDDC sparing"])
def Testcase_MemRas_ADDDC_009():
    """2nd Strike同rank，不同bank，同dev（3次CE分布不同bank）"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=0, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=1, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("rank")


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 2 2", 3])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 2 2", 3, "DDDC sparing"])
def Testcase_MemRas_ADDDC_010():
    """2nd Strike同rank，不同bank，不同dev"""
    _trigger_vls(level="bank")
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("bank")


@bios_setting("ADDDC")
def Testcase_MemRas_ADDDC_011():
    """2nd Strike Bank VLS的buddy Bank注入3次CE错误"""
    _trigger_vls(level="bank")
    dimm0, sub_ch, buddy_rank, buddy_bg, buddy_ba, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=dimm0, sub_ch=sub_ch, rank=buddy_rank, bank_group=buddy_bg,
            bank=buddy_ba, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("bank")


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 2 3", 1],
              [f"{_DIMM_LOC} {Loc.bg} 2 4", 1],
              [f"{_DIMM_LOC} {Loc.bg} 2 5", 1])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 2 3", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 4", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} 2 5", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_012():
    """3rd Strike 同rank，不同dev"""
    _trigger_vls("rank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank=2, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, bank=2, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=5, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3],
              [f"{_DIMM_LOC} 2 1 3", 1],
              [f"{_DIMM_LOC} 2 1 3", 1],
              [f"{_DIMM_LOC} 2 2 4", 1])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} 2 1 3", 1, ""],
              [f"{_DIMM_LOC} 2 1 3", 1, ""],
              [f"{_DIMM_LOC} 2 2 4", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_013():
    """3rd Strike 同rank，任意bank，任意dev"""
    _trigger_vls("rank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank_group=2, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank_group=2, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, bank_group=2, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
def Testcase_MemRas_ADDDC_014():
    """3rd Strike故障rank的buddy rank上"""
    _trigger_vls("rank")
    dimm0, sub_ch, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=dimm0, sub_ch=sub_ch, rank=buddy_rank, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3],
              [f"{_DIMM_LOC} 2 1 3", 1],
              [f"{_DIMM_LOC} 2 1 4", 1],
              [f"{_DIMM_LOC} 2 2 5", 1])
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} 1 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} 2 1 3", 1, ""],
              [f"{_DIMM_LOC} 2 1 4", 1, ""],
              [f"{_DIMM_LOC} 2 2 5", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_015():
    """3rd Strike与1、2在同一rank，但都不是相同dev"""
    _trigger_vls("rank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=3, bank_group=2, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, bank_group=2, bank=1, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=5, bank_group=2, bank=1, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


@bios_setting("ADDDC")
def Testcase_MemRas_ADDDC_016():
    """3rd Strike与1、2在不同rank，且是1或2的buddy"""
    _trigger_vls(level="bank")
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=2, bank=2, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    _check_vls("bank")

    dimm0, sub_ch, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=Loc.msocket, channel=Loc.ch, dimm=dimm0, sub_ch=sub_ch, rank=buddy_rank,
            bank_group=buddy_bank_group, bank=buddy_bank, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))


def Testcase_MemRas_ADDDC_017():
    """3rd Strike同rank，任意bank，任意dev"""
    Testcase_MemRas_ADDDC_013()


@bios_setting("ADDDC")
@check_result("fdm_memce_array", False,
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 4", 1],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 5", 1],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 6", 1],

              )
@check_result("maint_mem_ce",
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 1", 3, "DDDC sparing"],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 4", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 5", 1, ""],
              [f"{_DIMM_LOC} {Loc.bg} {Loc.ba} 6", 1, "Memory_CE_Bucket"])
def Testcase_MemRas_ADDDC_018():
    """ADDDC+1功能测试"""
    _trigger_vls(level="bank")
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=4, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=5, delay=Delay.mem_ov)
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=6, delay=Delay.mem_ov)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(Loc.msocket, Loc.imc, Loc.ch))
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, dev=7, delay=Delay.mem_ov)


@bios_setting("PPR")
@check_result("fdm_mem_ce", socket=Loc.msocket, channel=Loc.channel, dimm=Loc.dimm, count=1)
def Testcase_MemRas_PPR_001():
    """Post Package Repair (PPR)"""
    inj_mem(count=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, errType="ce")
    force_power_cycle()
    time.sleep(30)
    ping_sut()


@bios_setting("PatrolScrub")
@check_result("fdm_mem_ce", socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, mscode="0X0008", mcacode="0X00C0")
def Testcase_MemRas_Scrubbing_001():
    """Patrol Scrubbing"""
    shell_cmd("dmesg -C")
    cmd = f'socket={Loc.msocket}, channel={Loc.ch}, sub_channel={Loc.sub_ch}, dimm={Loc.dimm}, rank=0, errType="ce", PatrolConsume=True'
    excmd(Cmd.ei_dev.format(1, 2, 3, 0))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting()
@check_result()
def Testcase_MemRas_Scrubbing_002():
    """Demand Scrub"""
    excmd(Cmd.dimminfo)
    assert_reg({Cmd.demand_scrub_dis.format(Loc.msocket, Loc.imc):0})


@bios_setting()
def Testcase_MemRas_Scrubbing_003():
    """Demand scrub功能测试-ce error"""
    excmd(Cmd.dimminfo)
    addr = 0x20000
    dram_addr = core_addr_trans(addr)
    assert_reg({Cmd.demand_scrub_dis.format(dram_addr.socket, dram_addr.imc):0})
    shell_cmd("dmesg -C")
    excmd(Cmd.dump_mem_err)
    cmd = f"addr={hex(addr)},immInject=True,immConsume=False,oneInjection=True,haltFirst=True,checkEInjLock=True,showInjectors=True"
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err)
    excmd("mem(0x20000, 4)")
    excmd(Cmd.dump_mem_err)
    _check_mem_err_count(socket=dram_addr.socket, mc=dram_addr.imc, ch=dram_addr.ch, count=1)
    excmd("ei.resetInjectorLockCheck()")
    excmd("mem(0x20000, 4)")
    _check_mem_err_count(socket=dram_addr.socket, mc=dram_addr.imc, ch=dram_addr.ch, count=1)


# @bios_setting()  #
# def Testcase_MemRas_Scrubbing_004():
#     """Demand scrub去功能测试"""
#     excmd(Cmd.dimminfo)
#     addr = 0x20000
#     dram_addr = core_addr_trans(addr)
#     demand_scrub_dis = f"sv.socket{dram_addr.socket}.uncore.memss.m2mem{dram_addr.imc}.defeatures0.demandscrubwrdis"
#     excmd(demand_scrub_dis+"=1")
#     assert_reg({f"sv.socket{dram_addr.socket}.uncore.memss.m2mem{dram_addr.imc}.defeatures0.demandscrubwrdis":1})
#     shell_cmd("dmesg -C")
#     excmd(Cmd.dump_mem_err)
#     cmd = f"addr={hex(addr)},immInject=True,immConsume=False,oneInjection=True,haltFirst=True,checkEInjLock=True,showInjectors=True"
#     excmd(Cmd.inj_mem.format(cmd))
#     excmd(Cmd.dump_mem_err)
#     excmd("mem(0x20000, 4)")
#     excmd(Cmd.dump_mem_err)
#     _check_mem_err_count(socket=dram_addr.socket, mc=dram_addr.imc, ch=dram_addr.ch, count=2)
#     excmd("ei.resetInjectorLockCheck()")
#     excmd("mem(0x20000, 4)")
#     _check_mem_err_count(socket=dram_addr.socket, mc=dram_addr.imc, ch=dram_addr.ch, count=4)


@bios_setting("PatrolScrub")
@check_result("fdm_mem_ce", sysaddr=0x1000_0000, count=1, mscode="0X0008", mcacode="0X00C0")
def Testcase_MemRas_Scrubbing_005():
    """Patrol scrub功能测试-ce error"""
    addr = 0x1000_0000
    shell_cmd("dmesg -C")
    cmd = f'addr={hex(addr)}, errType="ce", PatrolConsume=True'
    dram_addr = core_addr_trans(addr)
    excmd(Cmd.ei_dev.format(1, 2, 3, 0))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)
    _check_mem_err_count(socket=dram_addr.socket, mc=dram_addr.imc, ch=dram_addr.ch, count=1)


@bios_setting("PatrolScrub")
def Testcase_MemRas_Scrubbing_006():
    """Patrol scrub功能测试-uce error"""
    addr = 0x1000_0000
    shell_cmd("dmesg -C")
    cmd = f'addr={hex(addr)}, errType="uce", PatrolConsume=True'
    dram_addr = core_addr_trans(addr)
    excmd(Cmd.ei_dev.format(1, 2, 3, 2))
    excmd(Cmd.inj_mem.format(cmd))
    excmd(Cmd.dump_mem_err, _halt=False)
    shell_cmd("dmesg", save_path=getframe().f_code.co_name)


@bios_setting()
@check_result()
def Testcase_MemRas_Scrambling_001():
    """Data Scrambling"""
    shell_cmd("./unitool -r ScrambleEn", save_path=getframe().f_code.co_name)
    assert int(os_ssh.read("ScrambleEn").get("ScrambleEn")) == 1


@bios_setting()
@check_result()
def Testcase_MemRas_Scrambling_002():
    """Data Scrambling测试"""
    excmd(Cmd.scramble_cfg+".show()")
    scramb_cfg = excmd(Cmd.scramble_cfg, echo=False)
    assert hex_bit(scramb_cfg, 0) == 1
    assert hex_bit(scramb_cfg, 1) == 1
    assert hex_bit(scramb_cfg, 2) == 1


# @bios_setting("WrCRC")
# @check_dump("fdm_mem_ce", mscode="0X0200", mcacode="0X00B0", options={"Module": f".+IMC {Loc.imc} Chan {Loc.channel}"})
# def Testcase_MemRas_WriteProtection_001():
#     """DDR4 Write Data CRC Protection"""
#     excmd(Cmd.correrrorstatus)
#     excmd(Cmd.alertsignal)
#     excmd(Cmd.inj_wcrc.format(Loc.msocket, Loc.imc, Loc.channel, Loc.sub_ch))
#     excmd(Cmd.alertsignal)
#     assert_reg({f"sv.socket{Loc.msocket}.uncore.memss.mc{Loc.imc}.ch{Loc.channel}.alertsignal.seen": 1})


def Testcase_MemRas_WriteProtection_002():
    """DDR4 Memory CMD/ADDR Parity Check and Retry测试"""
    cprint("Testcase duplicated with 'Testcase_MemRas_CA_ParityError_002'")
    # Testcase_MemRas_CA_ParityError_002()


# def Testcase_MemRas_WriteProtection_003():
#     """DDR4 Memory CMD/ADDR Parity Check and Retry测试"""
#     Testcase_MemRas_WriteProtection_001()


@bios_setting()
def Testcase_MemRas_ThermalThrottling_001():
    """Memory Thermal Throttling阈值为low时，内存只触发X2刷新不降带宽"""
    excmd(Cmd.show_field_reg.format("temp_hi"))
    excmd(Cmd.show_field_reg.format("temp_mid"))
    excmd(Cmd.show_field_reg.format("temp_lo"))
    excmd(Cmd.show_field_reg.format("dimm_temp"))
    excmd(Cmd.set_temp_th.format(Loc.msocket, Loc.imc, Loc.ch, Loc.dimm, "temp_lo"))


@bios_setting()
def Testcase_MemRas_ThermalThrottling_002():
    """Memory Thermal Throttling阈值为middle时，内存降50%带宽"""
    excmd(Cmd.show_field_reg.format("temp_hi"))
    excmd(Cmd.show_field_reg.format("temp_mid"))
    excmd(Cmd.show_field_reg.format("temp_lo"))
    excmd(Cmd.show_field_reg.format("dimm_temp"))
    excmd(Cmd.set_temp_th.format(Loc.msocket, Loc.imc, Loc.ch, Loc.dimm, "temp_lo"))
    excmd(Cmd.set_temp_th.format(Loc.msocket, Loc.imc, Loc.ch, Loc.dimm, "temp_mid"))


@bios_setting()
def Testcase_MemRas_ThermalThrottling_003():
    """Memory Thermal Throttling阈值为High时，内存降95%带宽"""
    excmd(Cmd.show_field_reg.format("temp_hi"))
    excmd(Cmd.show_field_reg.format("temp_mid"))
    excmd(Cmd.show_field_reg.format("temp_lo"))
    excmd(Cmd.show_field_reg.format("dimm_temp"))
    excmd(Cmd.set_temp_th.format(Loc.msocket, Loc.imc, Loc.ch, Loc.dimm, "temp_lo"))
    excmd(Cmd.set_temp_th.format(Loc.msocket, Loc.imc, Loc.ch, Loc.dimm, "temp_mid"))
    excmd(Cmd.set_temp_th.format(Loc.msocket, Loc.imc, Loc.ch, Loc.dimm, "temp_hi"))


