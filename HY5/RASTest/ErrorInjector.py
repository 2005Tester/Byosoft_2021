import time


def itp_halt():
    halt()
    while not itp.ishalted():
        time.sleep(1)
    return True


def itp_go():
    go()
    while itp.ishalted():
        time.sleep(1)
    return True


def write_cmd(cmd):
    itp_halt()
    ei.resetInjectorLockCheck()
    print(">>>", cmd)
    exec(cmd)
    itp_go()


def read_register(cmd, echo=False):
    if echo:
        print(">>>", cmd)
    # itp_halt()
    reg = eval(cmd)
    # itp_go()
    return reg


def check_pcie_presence():
    result = []
    port_map = ["b1d00f0", "b1d01f0", "b1d02f0", "b1d03f0", "b2d00f0", "b2d01f0", "b2d02f0", "b2d03f0", "b4d00f0",
                "b4d01f0", "b4d02f0", "b4d03f0"]
    for socket in range(len(sv.sockets)):
        for port in port_map:
            if read_register("sv.socket{}.uncore0.pxp_{}_lnksts.data_link_layer_link_active".format(socket, port)):
                result.append((socket, port))
    if result:
        return result
    else:
        print("No PCIE device detected, please check!")


def check_mem_pop():
    result = []
    for socket in range(len(sv.sockets)):
        for imc in range(2):
            for channel in range(3):
                for dimm in range(2):
                    if read_register(
                            "sv.socket{}.uncore0.imc{}_c{}_dimmmtr_{}.dimm_pop".format(socket, imc, channel, dimm)):
                        result.append((socket, imc, channel, dimm))
    return result


def mem_err(count=3, dev=0, addr=None, socket=0, channel=0, dimm=0, rank=0, bank_group=1, bank=0, errType="ce"):
    def corrcount():
        ce = int(read_register("sv.socket0.uncore0.imc0_m2mem_mci_status.corrcount"))
        return ce

    if addr:
        cmd = 'ei.injectMemError(addr=0x{:x}, errType="{}")'.format(addr, errType)
    else:
        cmd = 'ei.injectMemError(socket={},channel={},dimm={},rank={},sub_rank=0,bank_group={},bank={},' \
              'errType="{}")'.format(socket, channel, dimm, rank, bank_group, bank, errType)
    if errType == "ce":
        ce_count = corrcount()
        count = count + ce_count
        ei.memDevs(dev0=dev, dev1msk=0)
        while ce_count < count:
            ce_count = corrcount()
            write_cmd(cmd)
            if ce_count < corrcount():
                time.sleep(20)
                ce_count = corrcount()
    elif errType == "uce":
        ei.memDevs(dev1msk=4)
        write_cmd(cmd)


def pcie_err(socket_port, count=11, errType="ce"):
    cpu = socket_port[0]  # socket
    slot = socket_port[1]  # port
    for i in range(count):
        cmd = 'ei.injectPcieError(socket={}, port="{}", errType="{}")'.format(cpu, slot, errType)
        write_cmd(cmd)
        time.sleep(2)


def upi_ce(count=11):
    for i in range(count):
        cmd = 'ei.injectUpiError(socket=0, port=0, num_crcs=1)'
        write_cmd(cmd)
        time.sleep(2)


def cap_ce(count=11):
    for i in range(count):
        cmd = 'ei.injectCAParity(socket=0, channel=0, numErrors=1)'
        write_cmd(cmd)
        time.sleep(20)


def copy_in_progress():
    copy_in_progress = read_register("sv.socket0.uncore0.imc0_sparing_patrol_status.copy_in_progress")
    if copy_in_progress:
        print("copy_in_progress...")
    return copy_in_progress


def copy_complete():
    copy_complete = read_register("sv.socket0.uncore0.imc0_sparing_patrol_status.copy_complete")
    if copy_complete:
        print("copy_complete!")
    return copy_complete


def spare_enable():
    return read_register("sv.socket0.uncore0.imc0_sparing_control.spare_enable")


def check_sparing_status(wait_sparing=False):
    print("Check sparing status...")
    time.sleep(1)
    if wait_sparing:
        while not copy_in_progress():
            time.sleep(2)
        while not copy_complete():
            time.sleep(3)
    else:
        if not spare_enable():
            time.sleep(20)
            return
        while not copy_in_progress():
            time.sleep(2)
        while not copy_complete():
            time.sleep(2)


def get_buddy():
    rank = read_register("sv.socket0.uncore0.imc0_c0_adddc_region0_control.nonfailed_cs")
    bank_group = read_register("sv.socket0.uncore0.imc0_c0_adddc_region0_control.nonfailed_bg")
    bank = read_register("sv.socket0.uncore0.imc0_c0_adddc_region0_control.nonfailed_ba")
    region_size = read_register("sv.socket0.uncore0.imc0_c0_adddc_region0_control.region_size")
    return rank, bank_group, bank, region_size


def timer(counter=610):
    t = 1
    while t <= counter:
        print("\r", t, end="", flush=True)
        t += 1
        time.sleep(1)
    print("\n")
