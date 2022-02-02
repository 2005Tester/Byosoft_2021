"""
此配置只有测试RAS/FDM时才会用到
首次使用脚本请确认配置
"""

# 【首次测试请确认配置】
# Unitool的路径
UNI_PATH = "/root/flashtool/unitool"

# 【首次测试请确认配置】
# 系统配置信息
OS_IP = "192.168.120.17"
OS_USER = "root"
OS_PW = "root"

# 【首次测试请确认配置】
# BMC配置信息
BMC_IP = "192.168.111.16"
BMC_USER = "Administrator"
BMC_PW = "Admin@9001"

# 【首次测试请确认配置】
# "startCscripts.py" 文件的路径
Cscript_Path = r"D:\Tools\Cscripts\ICX"

# 串口
COM = "COM3"

# Boot到系统的标志字符串
OS_FLAG = "Ubuntu 20.04 LTS"

# 打开DebugMessage后重启系统 超时时间
BOOT_TIMEOUT = 900

# 测试Case关键字
TestcaseFunc = "Testcase_"
TestcaseFile = "Testcase_"

# Delay时间
class Delay:
    mem = 20
    bank_vls = 120
    rank_vls = 240
    rank_sparing = 320
    caterr = 720
    mem_uce = 180


# SMI风暴抑制
smi_dis = 610  # SMI抑制时间
smi_thld = 3  # SMI抑制次数


# 【首次测试请确认配置】
class Sys:
    """
    系统配置
    """
    # CPU
    CPUs = [0, 1, 2, 3]
    UPIs = [0, 1, 2]

    # Memory
    MCs = [0, 1, 2, 3]
    CHs = [0, 1]
    SUB_CHs = [0,1]
    DIMMs = [0, 1]
    Ranks = [0, 1]
    MaxRank = 4  # 固定值

    # PCIE Root Port
    ROOT0 = ["dmi"]
    ROOT1 = []
    ROOT2 = []
    ROOT3 = []

    # port_map
    PORT_MAP = {
        0: ["dmi", "dmi"],
        1: ["0a", "pxp0.pcieg5.port0"],
        2: ["0b", "pxp0.pcieg4.port3"],
        3: ["0c", "pxp0.pcieg5.port1"],
        4: ["0d", "pxp0.pcieg4.port2"],
        5: ["0e", "pxp0.pcieg5.port2"],
        6: ["0f", "pxp0.pcieg4.port1"],
        7: ["0g", "pxp0.pcieg5.port3"],
        8: ["0h", "pxp0.pcieg4.port0"],
        9: ["1a", "pxp1.pcieg5.port0"],
        10: ["1b", "pxp1.pcieg4.port3"],
        11: ["1c", "pxp1.pcieg5.port1"],
        12: ["1d", "pxp1.pcieg4.port2"],
        13: ["1e", "pxp1.pcieg5.port2"],
        14: ["1f", "pxp1.pcieg4.port1"],
        15: ["1g", "pxp1.pcieg5.port3"],
        16: ["1h", "pxp1.pcieg4.port0"],
        17: ["2a", "pxp2.pcieg5.port0"],
        18: ["2b", "pxp2.pcieg4.port3"],
        19: ["2c", "pxp2.pcieg5.port1"],
        20: ["2d", "pxp2.pcieg4.port2"],
        21: ["2e", "pxp2.pcieg5.port2"],
        22: ["2f", "pxp2.pcieg4.port1"],
        23: ["2g", "pxp2.pcieg5.port3"],
        24: ["2h", "pxp2.pcieg4.port0"],
        25: ["3a", "pxp3.pcieg5.port0"],
        26: ["3b", "pxp3.pcieg4.port3"],
        27: ["3c", "pxp3.pcieg5.port1"],
        28: ["3d", "pxp3.pcieg4.port2"],
        29: ["3e", "pxp3.pcieg5.port2"],
        30: ["3f", "pxp3.pcieg4.port1"],
        31: ["3g", "pxp3.pcieg5.port3"],
        32: ["3h", "pxp3.pcieg4.port0"],
        33: ["4a", "pxp4.pcieg5.port0"],
        34: ["4b", "pxp4.pcieg4.port3"],
        35: ["4c", "pxp4.pcieg5.port1"],
        36: ["4d", "pxp4.pcieg4.port2"],
        37: ["4e", "pxp4.pcieg5.port2"],
        38: ["4f", "pxp4.pcieg4.port1"],
        39: ["4g", "pxp4.pcieg5.port3"],
        40: ["4h", "pxp4.pcieg4.port0"],
        41: ["5a", "pxp5.pcieg5.port0"],
        42: ["5b", "pxp5.pcieg4.port3"],
        43: ["5c", "pxp5.pcieg5.port1"],
        44: ["5d", "pxp5.pcieg4.port2"],
        45: ["5e", "pxp5.pcieg5.port2"],
    }


# 【首次测试请确认配置】
class Loc:
    """
    默认注错位置
    """
    # 内存位置
    msocket = 0
    imc = 0
    channel = 0
    sub_ch = 1
    dimm = 0

    rank = 1
    bg = 3  # bank_group 位置不用改
    ba = 3  # bank 位置不用改

    # 系统channel转换
    ch = (imc * len(Sys.CHs)) + channel

    # 内存UCE 4G以上地址
    mem_uce_addr = 0x100000000

    # mirror 地址
    full_mirr_addr = 0x100000040
    arm_mirr_addr = 0x100000040
    arm_non_mirr_addr = 0xA00000000

    # UPI
    usocket = 0
    upi_port = 1

    # PCIe
    psocket = 1
    pcie_port = 1

    # PCie设备信息
    pcie_os_bdf = "98:00.0"
    pcie_root_bdf = "97:02:00"
    pcie_dev_name = "PCIe Card3"

    # DCPMM
    dsocket = 0
    dmc = 0
    dchannel = 0
    ddimm = 0
    drank = 1


# Cscripts 命令
class Cmd:
    # 注错命令
    inj_mem = 'ei.injectMemError({})'
    inj_pcie = "ei.injectPcieError(socket={}, port={}, errType={})"
    inj_cap = "ei.injectCMDParity(socket={}, mc={}, channel={}, sub_ch={})"#
    inj_wcrc = "ei.injectWriteCRC(socket={}, mc={}, ch={}, sub_ch={})"#
    inj_upi = "ei.injectUpiError(socket={}, port={}, num_crcs={}, laneNum={})"
    inj_upi_failover = "ei.injUpiDataLinkFailover(socket={}, port={}, direction={}, dataLanes={}, portreset=1)"#
    inj_3s = "ei.injectThreeStrike({})"#
    inj_ierr = "ei.injectIERR({})"
    inj_mcer = "ei.injectMCERR()"
    ei_dev = "ei.memDevs(dev0={}, dev0msk=0x{}, dev1={}, dev1msk=0x{})"
    ei_reset = "ei.resetInjectorLockCheck(0)"
    sa2da = "ei.sa2da_table({},{})"

    # 查询命令
    msr = "itp.msr({}, {})"
    dimminfo = "mc.dimminfo()"
    pcie_top = "pcie.topology()"
    pcie_map = "pcie.port_map()"
    upi_top = "upi.topology()"
    dump_mem_err = "error.check_mem_errors()"
    dump_upi_err = "error.check_upi_errors()"
    dump_pcie_err = "error.check_pcie_errors()"

    # ras 模块
    adddc_check = "ras.adddc_status_check(socket={}, mc={}, channel={})"#
    viral_check = "ras.viral_config_check()"
    viral_err = "ras.viral_error_check()"
    retry_rd = "ras.retry_rd_log_decode(socket={},mc={},channel={})"#

    # sv 命令
    dimm_pop = "sv.socket{}.uncore.memss.mc{}.ch{}.dimmmtr_{}.dimm_pop"
    upi_rxeinj = "sv.sockets.uncore.upi.upi{}.ktirxeinjctl0=0xcacb2143".format(Loc.upi_port)
    kti_mc_st = "sv.socket{}.uncore.upi.upi{}.bios_kti_err_st.show()".format(Loc.usocket, Loc.upi_port)
    s_clm = "sv.sockets.uncore.showsearch('s_clm','f')"
    iio_viral_show = 'sv.socket{}.uncore.showsearch("iio_viral","f")'
    viral_state_pcie = "sv.socket{}.uncore.m2iosfs.viral_cfg.show()"#
    viral_state_upi = "sv.sockets.uncore.upi.upis.ktiviral.show()"
    mem_mode = "sv.socket{}.uncore.memss.m2mem{}.mode.show()"
    alertsignal = "sv.socket{}.uncore.memss.mc{}.ch{}.alertsignal.show()".format(
        Loc.msocket, Loc.imc, Loc.channel)
    correrrorstatus = "sv.socket{}.uncore.memss.mc{}.ch{}.correrrorstatus.show()".format(
        Loc.msocket, Loc.imc, Loc.channel)
    sparing_patrol_status = "sv.socket{}.uncore.memss.mc{}.ch{}.sparing_patrol_status.show()"
    adddc_sparing = "sv.socket{}.uncore.memss.mc{}.ch{}.sparing_control.adddc_sparing".format(
        Loc.msocket, Loc.imc, Loc.channel)
    set_temp_th = "sv.socket{}.uncore.memss.mc{}.ch{}.dimm_temp_th_{}.{}=0x0"
    show_field_reg = "sv.sockets.uncore.showsearch({!r},'f')"
    show_reg = "sv.sockets.uncore.showsearch({!r})"
    core_count = "len(sv.socket0.cpu.cores)"#
    pcls_cfg = "sv.socket{}.uncore.memss.mc{}.ch{}.pcls_{}_cfg_data_info.show()"

    buddy_rank = "sv.socket{}.uncore.memss.mc{}.ch{}.adddc_region{}_control.nonfailed_cs"
    buddy_bg = "sv.socket{}.uncore.memss.mc{}.ch{}.adddc_region{}_control.nonfailed_bg"
    buddy_bank = "sv.socket{}.uncore.memss.mc{}.ch{}.adddc_region{}_control.nonfailed_ba"
    region_size = "sv.socket{}.uncore.memss.mc{}.ch{}.adddc_region{}_control.region_size"

    pcie_present = "sv.socket{}.uncore.pi5.{}.cfg.linksts.dllla"#
    comp_timeout_severity = "sv.socket{}.uncore.pi5.{}.cfg.erruncsev.ctes=1".format(
        Loc.psocket, Sys.PORT_MAP[Loc.pcie_port][1])#


# 不同RAS功能的BIOS设置
class Bios:
    DFX = {
        "DFXEnable": 1,
        "DfxDisableBiosDone": 1,
        "LockChipset": 0,
        "DirectoryModeEn": 0,
        "RasLogLevel": 3,
    }

    ADDDC = {
        "ADDDCEn": 1,
        "spareErrTh": 1,
        "PclsEn": 0,
    }

    FullMirror = {
        "MirrorMode": 1,
        "PartialMirrorUefi": 0,
        "PclsEn": 0,
        "ADDDCEn": 0,
        "spareErrTh": 6000,
    }

    ArmMirror = {
        "MirrorMode": 0,
        "PartialMirrorUefi": 1,
        "PartialMirrorUefiPercent": 3000,
        "PclsEn": 0,
        "ADDDCEn": 0,
        "spareErrTh": 6000,
    }

    Legacy = {
        "PoisonEn": 0,
    }

    PatrolScrub = {
        "PatrolScrub": 1,
        "PatrolScrubDuration": 1,
    }

    WrCRC = {
        "WrCRC": 1,
        "ADDDCEn": 0,
    }

    Viral = {
        "ViralEn": 1,
    }

    Pcls = {
        "PclsEn": 1,
        "ADDDCEn": 1,
        "spareErrTh": 1,
    }

    UpiFailover = {
        "KtiLinkL0pEn": 0,
        "KtiLinkL1En": 0
    }

    IERR = {
        "EmcaMsmiEn": 0,
        "ShutdownSuppression": 1,
    }

    PPR = {
        "pprType": 1,
        "pprErrInjTest": 1,
        "spareErrTh": 1,
    }

    IERR_Debug = {
        "EmcaMsmiEn": 0,
        "ShutdownSuppression": 1,
        "serialDebugMsgLvl": 2,
    }

    DebugMsg = {
        "serialDebugMsgLvl": 2,
        "RasLogLevel": 3,
    }


# 测试Case集合，可单独自定义，用 "-f" 参数测试自定义Testcase集合
class TestCase:
    CPU = []
    MEM = []
    PCIE = []
    FDM = []

    ADDDC = []
    MIRROR = []

    # 【可在此处添加需要自定义的测试集合】
    Custom = []
