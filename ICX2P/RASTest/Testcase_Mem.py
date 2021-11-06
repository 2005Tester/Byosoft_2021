# -*- encoding=utf8 -*-

"""
内存相关的所有测试项目
"""

msocket = Loc.msocket
imc = Loc.imc
channel = Loc.channel
ch = Loc.ch
dimm = Loc.dimm
rank = Loc.rank


"""
FullMirror 功能测试
"""

# 测试前检查确认没有错误
def _pre_test_check():
    itp.halt()
    excmd(Cmd.dump_mem_err)
    excmd(Cmd.mem_mode.format(msocket, imc))
    excmd((Cmd.dimminfo))
    itp.go()

# 检查是否触发ADDDC及是否正确组成VLS
def _vls_check(vls):
    assert int(excmd(Cmd.adddc_sparing, echo=False))==1, "[Assert] No ADDDC Sparing"
    if vls.lower() == "bank":
        assert int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, 0), echo=False)) == 0, "[Assert] No Bank-VLS"
        return
    if vls.lower() == "rank":
        assert int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, 0), echo=False)) == 1, "[Assert] No Rank-VLS"
        return

# 01 Mirror模式下注入可纠正错误
@bios_setting("FullMirror")
def Testcase_MemRAS_001():
    _pre_test_check()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    inj_mem(count=1, errType="ce", addr=Loc.full_mirr_addr)

# 02 Primary通道注入不可纠正错误
@bios_setting("FullMirror")
def Testcase_MemRAS_002():
    _pre_test_check()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    inj_mem(count=1, errType="uce", addr=Loc.full_mirr_addr)
    excmd(Cmd.retry_rd.format(msocket, ch))

# 03 Primary通道注入不可纠正错误，Secondary通道注入可纠正错误
@bios_setting("FullMirror")
def Testcase_MemRAS_003():
    _pre_test_check()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 0))
    excmd(Cmd.inj_mem.format('addr={},errType="ce",immInject=False,immConsume=False,Inj2ndCh=True'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce",immInject=True,immConsume=True,Inj2ndCh=False'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

# 04 两个通道都注入不可纠正错误
@bios_setting("FullMirror")
def Testcase_MemRAS_004():
    _pre_test_check()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_uce"'.format(hex(Loc.full_mirr_addr))), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)

# 05 Mirror Failover
@bios_setting("FullMirror")
def Testcase_MemRAS_005():
    _pre_test_check()
    excmd(Cmd.sa2da.format(hex(Loc.full_mirr_addr), hex(Loc.full_mirr_addr + 0x10)))
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(hex(Loc.full_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)


"""
ArmMirror 功能测试
"""

# 06 菜单设置ARM Mirror
@bios_setting("ArmMirror")
def Testcase_MemRAS_006():
    _pre_test_check()

# 07 镜像地址范围内UCE错误
@bios_setting("ArmMirror")
def Testcase_MemRAS_007():
    _pre_test_check()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(hex(Loc.arm_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

# 08 镜像地址范围内持续UCE
@bios_setting("ArmMirror")
def Testcase_MemRAS_008():
    _pre_test_check()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="mirror_failover"'.format(hex(Loc.arm_mirr_addr))))
    excmd(Cmd.dump_mem_err, _halt=False)

# 09 非镜像地址范围UCE错误
@bios_setting("ArmMirror")
def Testcase_MemRAS_009():
    _pre_test_check()
    excmd(Cmd.ei_dev.format(1, 2, 3, 4))
    excmd(Cmd.inj_mem.format('addr={},errType="uce"'.format(hex(Loc.arm_non_mirr_addr))), delay=Delay.mem_uce)
    excmd(Cmd.dump_mem_err, _halt=False)


"""
ADDDC 功能测试
"""

# 10 1st Strike同rank，不同bank，不同dev注入CE错误
@bios_setting("ADDDC")
def Testcase_MemRAS_010():
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1, bank=0)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=2, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank=2)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 11 1st Strike同rank，同bank，不同dev注入CE错误
@bios_setting("ADDDC")
def Testcase_MemRAS_011():
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=0)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=2)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 12 1st Strike同rank，不同bank，同dev注入CE错误
@bios_setting("ADDDC")
def Testcase_MemRAS_012():
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, bank=0)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, bank=2)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))
    _vls_check("bank")

# 13 1st Strike同rank，同bank，同dev注入CE错误
@bios_setting("ADDDC")
def Testcase_MemRAS_013():
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm)
    timer(Delay.bank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))
    _vls_check("bank")

# 14 2nd Strike同rank，同bank，不同dev
@bios_setting("ADDDC")
def Testcase_MemRAS_014():
    Testcase_MemRAS_013()
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1, bank=2)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=2, bank=2)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 15 2nd Strike同rank，任意bank，不同dev
@bios_setting("ADDDC")
def Testcase_MemRAS_015():
    Testcase_MemRAS_013()
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=2, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 16 2nd Strike同rank，不同bank，同dev
@bios_setting("ADDDC")
def Testcase_MemRAS_016():
    Testcase_MemRAS_013()
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))
    _vls_check("rank")

# 17 2nd Strike同rank，不同bank，同dev（3次CE分布不同bank）
@bios_setting("ADDDC")
def Testcase_MemRAS_017():
    Testcase_MemRAS_013()
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1, bank=0)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=1, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))
    _vls_check("rank")

# 18 2nd Strike同rank，不同bank，不同dev
@bios_setting("ADDDC")
def Testcase_MemRAS_018():
    Testcase_MemRAS_013()
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm, dev=2, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))
    _vls_check("bank")

# 19 2nd Strike Bank VLS的buddy Bank注入3次CE错误
@bios_setting("ADDDC")
def Testcase_MemRAS_019():
    Testcase_MemRAS_013()
    dimm0, buddy_rank, buddy_bg, buddy_ba, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm0, rank=buddy_rank, bank_group=buddy_bg, bank=buddy_ba)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))
    _vls_check("bank")

# 20 3rd Strike 同rank，不同dev
@bios_setting("ADDDC")
def Testcase_MemRAS_020():
    Testcase_MemRAS_016()
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank=2)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=4, bank=2)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=5, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 21 3rd Strike 同rank，任意bank，任意dev
@bios_setting("ADDDC")
def Testcase_MemRAS_021():
    Testcase_MemRAS_016()
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank_group=3, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank_group=3, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=4, bank_group=3, bank=2)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 22 3rd Strike故障rank的buddy rank上
@bios_setting("ADDDC")
def Testcase_MemRAS_022():
    Testcase_MemRAS_016()
    dimm0, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm0, rank=buddy_rank)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 23 3rd Strike与1、2在同一rank，但都不是相同dev
@bios_setting("ADDDC")
def Testcase_MemRAS_023():
    Testcase_MemRAS_016()
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=3, bank_group=3, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=4, bank_group=3, bank=1)
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, dev=5, bank_group=3, bank=1)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 24 3rd Strike与1、2在不同rank，且是1或2的buddy
@bios_setting("ADDDC")
def Testcase_MemRAS_024():
    Testcase_MemRAS_018()
    dimm0, buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy(region=0)
    inj_mem(count=3, socket=msocket, channel=ch, dimm=dimm0, rank=buddy_rank, bank_group=buddy_bank_group, bank=buddy_bank)
    timer(Delay.rank_vls)
    excmd(Cmd.adddc_check.format(msocket, imc))

# 25 3rd Strike同rank，任意bank，任意dev
def Testcase_MemRAS_025():
    Testcase_MemRAS_021()

# 28 PPR功能测试
@bios_setting("PPR")
def Testcase_MemRAS_028():
    inj_mem(count=1, socket=msocket, channel=ch, dimm=dimm, rank=1, errType="ce")
    force_power_cycle(bmc)
    time.sleep(30)
    ping_sut()

# 29 Transient C/A Parity Error
@bios_setting("Default")
def Testcase_MemRAS_029():
    inj_cap()
    excmd(Cmd.alertsignal)

# 32 Patrol Scrubbing
@bios_setting("Default")
def Testcase_MemRAS_032():
    if os_ssh.open_shell():
        os_ssh.exec_cmds(["dmesg -C\n"])
        cmd = 'socket={}, channel={}, dimm={}, rank=0, errType="ce", PatrolConsume=True'.format(msocket, ch, dimm)
        excmd(Cmd.ei_dev.format(1, 2, 3, 0))
        excmd(Cmd.inj_mem.format(cmd))
        excmd(Cmd.dump_mem_err, _halt=False)
        check_info("dmesg", sys._getframe().f_code.co_name)
        os_ssh.close_shell()

# 33 Demand Scrub
@bios_setting("Default")
def Testcase_MemRAS_033():
    excmd(Cmd.dimminfo)

# 34 Data Scrambling
@bios_setting("Default")
def Testcase_MemRAS_034():
    if os_ssh.open_shell():
        os_ssh.install_driver()
        check_info("./unitool -r ScrambleEn", sys._getframe().f_code.co_name)
        os_ssh.close_shell()

# 35 DDR4 Write Data CRC Protection
@bios_setting("WrCRC")
def Testcase_MemRAS_035():
    excmd(Cmd.correrrorstatus)
    excmd(Cmd.alertsignal)
    excmd(Cmd.inj_wcrc.format(msocket, imc, channel))
    excmd(Cmd.alertsignal)

# 37 内存Memory Thermal Throttling测试
@bios_setting("WrCRC")
def Testcase_MemRAS_037():
    excmd(Cmd.show_field_reg.format("temp_hi"))
    excmd(Cmd.show_field_reg.format("temp_mid"))
    excmd(Cmd.show_field_reg.format("temp_lo"))
    excmd(Cmd.show_field_reg.format("dimm_temp"))
    excmd(Cmd.set_temp_lo)
    excmd(Cmd.set_temp_mid)

# 38.单Bit内存错误PCLS测试
@bios_setting("Pcls")
def Testcase_MemRAS_038():
    excmd(Cmd.pcls_cfg.format(msocket, imc, channel, 0))
    inj_mem(count=1, errType="ce")
    excmd(Cmd.pcls_cfg.format(msocket, imc, channel, 0))
    excmd(Cmd.show_pcls.format(msocket, imc, channel))

# 39. 单个通道注满16个PCLS Entry测试
@bios_setting("Pcls")
def Testcase_MemRAS_039():
    for rank in range(0, 2):
        for bg in range(0, 4):
            for ba in range(0, 2):
                inj_mem(socket=msocket, channel=ch, dimm=dimm, rank=rank, bank_group=bg, bank=ba, errType="ce")
                timer(20)
    excmd(Cmd.show_pcls.format(msocket, imc, channel))
    excmd(Cmd.adddc_check.format(msocket, imc))
    inj_mem(count=3, bank_group=1, bank=3, errType="ce")
    excmd(Cmd.adddc_check.format(msocket, imc))

# 40. 多Bit内存错误不触发PCLS测试
@bios_setting("Pcls")
def Testcase_MemRAS_040():
    excmd(Cmd.ei_dev.format(1, "f", 3, 0))  # 多Bit错误注入
    argvs = "socket={}, channel={}, dimm={}, rank={}, bank_group={}, bank={}, errType='ce', showErrorRegs=True".format(msocket, ch, dimm, rank, 3, 3)
    for i in range(3):
        excmd(Cmd.inj_mem.format(argvs), delay=Delay.mem)
    excmd(Cmd.adddc_check.format(msocket, imc))
    excmd(Cmd.pcls_cfg.format(msocket, imc, channel, 0))
    excmd(Cmd.show_pcls.format(msocket, imc, channel))
