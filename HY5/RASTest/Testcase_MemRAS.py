# -*- encoding=utf8 -*-


class GetMem:  # auto detect a dimm slot for mem error inject
    def __init__(self):
        self.slot = check_mem_pop()[0]
        self.socket = self.slot[0]
        self.imc = self.slot[1]
        self.channel = self.slot[2] if (self.slot[1] == 0) else self.slot[2] + 3
        self.dimm = self.slot[3]

    def check_adddc_status(self):
        itp_halt()
        read_register("ras.adddc_status_check({},{})".format(self.socket, self.imc), echo=True)
        itp_go()

    def check_dimminfo(self):
        read_register("mc.dimminfo()", echo=True)


class ADDDC(GetMem):
    def __init__(self):
        super(ADDDC, self).__init__()
        self.CONFIG = type(self).__name__

    def Testcase_MemRAS_010(self):
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=2, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank=3)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_011(self):
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_012(self):
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, bank=3)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_013(self):
        mem_err(count=3, socket=self.socket, channel=self.channel, dimm=self.dimm)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_014(self):
        self.Testcase_MemRAS_013()
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=2, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank=2)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_015(self):
        self.Testcase_MemRAS_013()
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=2, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank=3)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_016(self):
        self.Testcase_MemRAS_013()
        mem_err(count=3, socket=self.socket, channel=self.channel, dimm=self.dimm, bank=1)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_017(self):
        self.Testcase_MemRAS_013()
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1, bank=2)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=1, bank=3)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_018(self):
        self.Testcase_MemRAS_013()
        mem_err(count=3, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=2, bank=2)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_019(self):
        self.Testcase_MemRAS_013()
        buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy()
        mem_err(count=3, socket=self.socket, channel=self.channel, dimm=self.dimm, rank=buddy_rank,
                bank_group=buddy_bank_group, bank=buddy_bank)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_020(self):
        self.Testcase_MemRAS_018()
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank=3)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=4, bank=3)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=5, bank=3)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_021(self):
        self.Testcase_MemRAS_018()
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank_group=3, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank_group=3, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=4, bank_group=3, bank=2)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_022(self):
        self.Testcase_MemRAS_016()
        buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy()
        if vls_size == 1:
            mem_err(count=3, socket=self.socket, channel=self.channel, dimm=self.dimm, rank=buddy_rank)
            check_sparing_status()
            self.check_adddc_status()

    def Testcase_MemRAS_023(self):
        self.Testcase_MemRAS_018()
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=3, bank_group=3, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=4, bank_group=3, bank=1)
        mem_err(count=1, socket=self.socket, channel=self.channel, dimm=self.dimm, dev=5, bank_group=3, bank=1)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_024(self):
        self.Testcase_MemRAS_018()
        buddy_rank, buddy_bank_group, buddy_bank, vls_size = get_buddy()
        mem_err(count=3, socket=self.socket, channel=self.channel, dimm=self.dimm, rank=buddy_rank,
                bank_group=buddy_bank_group, bank=buddy_bank)
        check_sparing_status()
        self.check_adddc_status()

    def Testcase_MemRAS_025(self):
        self.Testcase_MemRAS_021()


class RankSparing1(GetMem):
    def __init__(self):
        super(RankSparing1, self).__init__()
        self.CONFIG = type(self).__name__

    def Testcase_MemRAS_026(self):
        self.check_dimminfo()
        mem_err(count=3, dev=3, socket=self.socket, channel=self.channel, dimm=1, rank=0, bank_group=1, bank=0)
        check_sparing_status(True)
        read_register("sv.socket0.uncore0.imc{}_sparing_patrol_status.show()".format(self.imc), echo=True)
        self.check_dimminfo()


class RankSparing2(GetMem):
    def __init__(self):
        super(RankSparing2, self).__init__()
        self.CONFIG = type(self).__name__

    def Testcase_MemRAS_027(self):
        self.check_dimminfo()
        mem_err(count=3, addr=0x8000)
        check_sparing_status(True)
        read_register("sv.socket0.uncore0.imc{}_sparing_patrol_status.show()".format(self.imc), echo=True)
        self.check_dimminfo()
        mem_err(count=3, addr=0x8000)
        check_sparing_status(True)
        read_register("sv.socket0.uncore0.imc{}_sparing_patrol_status.show()".format(self.imc), echo=True)
        self.check_dimminfo()


ADDDC = ADDDC()
RankSparing1 = RankSparing1()
RankSparing2 = RankSparing2()
