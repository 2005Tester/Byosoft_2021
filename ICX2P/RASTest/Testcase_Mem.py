# -*- encoding=utf8 -*-

"""
内存相关的所有测试项目
"""

socket = Loc.msocket
imc = Loc.imc
channel = Loc.channel
ch = Loc.ch
dimm = Loc.dimm


"""
FullMirror 功能测试
"""


def _pre_test_check():
    halt()
    excmd(Cmd.dump_mem_err)
    excmd(Cmd.mem_mode.format(socket, imc))
    excmd((Cmd.dimminfo))
    go()


def _vls_check(vls):
    assert int(excmd(Cmd.adddc_sparing, echo=False))==1, "No ADDDC Sparing Assert"
    if vls.lower() == "bank":
        assert int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, 0), echo=False)) == 0, "No Bank-VLS Assert"
        return
    if vls.lower() == "rank":
        assert int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, 0), echo=False)) == 1, "No Rank-VLS Assert"
        return


@bios_setting("FullMirror")
def Testcase_MemRAS_001():
    _pre_test_check()
    excmd(Cmd.sa2da.format(Loc.full_mirr_addr, hex(int(Loc.full_mirr_addr, 16) + 16)))
    inj_mem(count=1, errType="ce", addr=Loc.full_mirr_addr)
    excmd(Cmd.dump_mem_err)


@bios_setting("FullMirror")
def Testcase_MemRAS_002():
    _pre_test_check()
    excmd(Cmd.sa2da.format(Loc.full_mirr_addr, hex(int(Loc.full_mirr_addr, 16) + 16)))
    inj_mem(count=1, errType="uce", addr=Loc.full_mirr_addr)
    excmd(Cmd.dump_mem_err)
    excmd(Cmd.retry_rd.format(socket, ch))


@bios_setting("FullMirror")
def Testcase_MemRAS_003():
    _pre_test_check()
    excmd(Cmd.sa2da.format(Loc.full_mirr_addr, hex(int(Loc.full_mirr_addr, 16) + 16)))
    excmd(Cmd.inj_mem.format('addr={},errType="ce",immInject=False,immConsume=False,Inj2ndCh=True'.format(Loc.full_mirr_addr)))
    excmd(Cmd.inj_mem.format('addr={},errType=”uce”,immInject=True,immConsume=True,Inj2ndCh=False'.format(Loc.full_mirr_addr)))
    excmd(Cmd.dump_mem_err)


@bios_setting("FullMirror")
def Testcase_MemRAS_004():
    _pre_test_check()
    excmd(Cmd.sa2da.format(Loc.full_mirr_addr, hex(int(Loc.full_mirr_addr, 16) + 16)))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_uce"'.format(Loc.full_mirr_addr)))
    excmd(Cmd.dump_mem_err)


@bios_setting("FullMirror")
def Testcase_MemRAS_005():
    _pre_test_check()
    excmd(Cmd.sa2da.format(Loc.full_mirr_addr, hex(int(Loc.full_mirr_addr, 16) + 16)))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(Loc.full_mirr_addr)))
    excmd(Cmd.dump_mem_err)


"""
ArmMirror 功能测试
"""

@bios_setting("ArmMirror")
def Testcase_MemRAS_006():
    _pre_test_check()


@bios_setting("ArmMirror")
def Testcase_MemRAS_007():
    _pre_test_check()
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(Loc.arm_mirr_addr)))
    excmd(Cmd.dump_mem_err)


@bios_setting("ArmMirror")
def Testcase_MemRAS_008():
    _pre_test_check()
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(Loc.arm_mirr_addr)))
    excmd(Cmd.dump_mem_err)


@bios_setting("ArmMirror")
def Testcase_MemRAS_009():
    _pre_test_check()
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(Loc.arm_non_mirr_addr)))
    excmd(Cmd.dump_mem_err)


"""
ADDDC 功能测试
"""

@bios_setting("ADDDC")
def Testcase_MemRAS_010():
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=2, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank=3)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_011():
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_012():
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, bank=3)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))
    _vls_check("bank")

@bios_setting("ADDDC")
def Testcase_MemRAS_013():
    inj_mem(count=3, socket=socket, channel=ch, dimm=dimm)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))
    _vls_check("bank")


@bios_setting("ADDDC")
def Testcase_MemRAS_014():
    Testcase_MemRAS_013()
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=2, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_015():
    Testcase_MemRAS_013()
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=2, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank=3)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_016():
    Testcase_MemRAS_013()
    inj_mem(count=3, socket=socket, channel=ch, dimm=dimm, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))
    _vls_check("rank")


@bios_setting("ADDDC")
def Testcase_MemRAS_017():
    Testcase_MemRAS_013()
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1, bank=2)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=1, bank=3)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))
    _vls_check("rank")


@bios_setting("ADDDC")
def Testcase_MemRAS_018():
    Testcase_MemRAS_013()
    inj_mem(count=3, socket=socket, channel=ch, dimm=dimm, dev=2, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))
    _vls_check("bank")


@bios_setting("ADDDC")
def Testcase_MemRAS_019():
    Testcase_MemRAS_013()
    dimm0, buddy_rank, buddy_bg, buddy_ba, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=socket, channel=ch, dimm=dimm0, rank=buddy_rank, bank_group=buddy_bg, bank=buddy_ba)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))
    _vls_check("bank")


@bios_setting("ADDDC")
def Testcase_MemRAS_020():
    Testcase_MemRAS_018()
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank=3)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=4, bank=3)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=5, bank=3)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_021():
    Testcase_MemRAS_018()
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank_group=3, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank_group=3, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=4, bank_group=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_022():
    Testcase_MemRAS_016()
    dimm0, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=socket, channel=ch, dimm=dimm0, rank=buddy_rank)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_023():
    Testcase_MemRAS_018()
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=3, bank_group=3, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=4, bank_group=3, bank=1)
    inj_mem(count=1, socket=socket, channel=ch, dimm=dimm, dev=5, bank_group=3, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


@bios_setting("ADDDC")
def Testcase_MemRAS_024():
    Testcase_MemRAS_018()
    dimm0, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=socket, channel=ch, dimm=dimm0, rank=buddy_rank, bank_group=buddy_bank_group, bank=buddy_bank)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(socket, imc))


def Testcase_MemRAS_025():
    Testcase_MemRAS_021()


@bios_setting("Default")
def Testcase_MemRAS_029():
    inj_cap()
    excmd(Cmd.alertsignal)


def Testcase_MemRAS_032():
    Testcase_FDM_Other_004()


@bios_setting("Default")
def Testcase_MemRAS_033():
    excmd(Cmd.dimminfo)


@bios_setting("Default")
def Testcase_MemRAS_034():
    if os_ssh.open_shell():
        os_ssh.env_set()
        check_info("./unitool –r ScrambleEn", sys._getframe().f_code.co_name, logname="os.log")


@bios_setting("WrCRC")
def Testcase_MemRAS_035():
    excmd(Cmd.correrrorstatus)
    excmd(Cmd.alertsignal)
    excmd(Cmd.inj_wcrc.format(socket, imc, channel))
    excmd(Cmd.alertsignal)