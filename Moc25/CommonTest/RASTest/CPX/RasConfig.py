"""
此配置只有测试RAS/FDM时才会用到
首次使用脚本请确认配置
"""

# 【首次测试请确认配置】
# Unitool的路径
UNI_PATH = "/root/flashtool/unitool"

# 【首次测试请确认配置】
# 系统配置信息
OS_IP = "192.168.2.150"
OS_USER = "root"
OS_PW = "root"

# 【首次测试请确认配置】
# BMC配置信息
BMC_IP = "192.168.2.102"
BMC_USER = "Administrator"
BMC_PW = "Admin@9001"

# 【首次测试请确认配置】
# "startCscripts.py" 文件的路径
Cscript_Path = r"D:\Tools\Cscripts\CPX"

# 串口
COM = "COM4"

# Boot到系统的标志字符串
OS_FLAG = "Ubuntu 20.04 LTS"

# 打开DebugMessage后重启系统 超时时间
BOOT_TIMEOUT = 900

# 测试Case关键字
TC_ID = "Testcase"


# Delay时间
class Delay:
    mem = 20
    bank_vls = 40
    rank_vls = 320
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
    UPIs = [0, 1, 2, 3, 4, 5]

    # Memory
    MCs = [0, 1]
    CHs = [0, 1, 2]
    DIMMs = [0, 1]
    Ranks = [0, 1]
    MaxRank = 4  # 固定值

    # PCIE Root Port
    ROOT0 = ["dmi", "1a", "2a", "2c", "3a"]
    ROOT1 = ["1a", "1c", "2a", "3a", "3c"]

    # pcie port_map
    PORT_MAP = {
        0: ["dmi", "dmi"],
        1: ["1a", "b1d00f0"],
        2: ["1b", "b1d01f0"],
        3: ["1c", "b1d02f0"],
        4: ["1d", "b1d03f0"],
        5: ["2a", "b2d00f0"],
        6: ["2b", "b2d01f0"],
        7: ["2c", "b2d02f0"],
        8: ["2d", "b2d03f0"],
        9: ["3a", "b4d00f0"],
        10: ["3b", "b4d01f0"],
        11: ["3c", "b4d02f0"],
        12: ["3d", "b4d03f0"],
    }

    # viral_iio 的bdf端口
    Viral_BDF = [
        "b0d05f2",
        "b1d05f2",
        "b2d05f2",
        "b4d05f2",
    ]


# 【首次测试请确认配置】
class Loc:
    """
    默认注错位置
    """
    # 内存位置
    msocket = 0
    imc = 0
    channel = 0
    dimm = 1

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
    psocket = 0
    pcie_port = 7

    # OS下PCie设备分配的Bus:Dev.Func
    pcie_dev_BDF = "26:00.0"

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
    inj_cap = "ei.injectCAParity(socket={}, channel={})"
    inj_wcrc = "ei.injectWriteCRC(socket={}, ch={})"
    inj_upi = "ei.injectUpiError(socket={}, port={}, num_crcs={}, laneNum={})"
    inj_upi_failover = "ei.injUpiDataLinkFailover(socket={}, port={}, direction={}, dataLanes={}, portreset=1)"
    inj_3s = "ei.injectThreeStrike({})"
    inj_ierr = "ei.injectIERR({})"
    inj_mcer = "ei.injectMCERR()"
    ei_dev = "ei.memDevs(dev0={}, dev0msk=0x{}, dev1={}, dev1msk=0x{})"
    ei_reset = "ei.resetInjectorLockCheck(0)"
    sa2da = "ei.sa2da_table({},{})"

    # 查询命令
    read_msr = "itp.msr({}, {})"
    dimminfo = "mc.dimminfo()"
    pcie_top = "pcie.topology()"
    pcie_map = "pcie.port_map()"
    upi_top = "upi.topology()"
    dump_mem_err = "error.dumpMemErrors()"
    dump_upi_err = "error.dumpUpiErrors()"

    # ras 模块
    adddc_check = "ras.adddc_status_check(socket={}, mc={})"
    viral_check = "ras.viral_config_check()"
    viral_err = "ras.viral_error_check()"
    retry_rd = "ras.retry_rd_log_decode(socket={},channel={})"

    # sv 命令
    dimm_pop = "sv.socket{}.uncore0.imc{}_c{}_dimmmtr_{}.dimm_pop"
    upi_rxeinj = "sv.sockets.uncore0.kti{}_rxeinjctl0=0xcacb2143".format(Loc.upi_port)
    kti_mc_st = "sv.socket{}.uncore0.kti{}_bios_err_st.show()".format(Loc.usocket, Loc.upi_port)
    s_clm = "sv.sockets.uncore0.showsearch('s_clm','f')"
    iio_viral_show = 'sv.socket{}.uncore0.showsearch("iio_viral","f")'
    viral_state_pcie = "sv.socket{}.uncore0.iio_viral_b0d05f2.show()"
    viral_state_upi = "sv.socket{}.uncore0.kti{}_viral.show()"
    mem_mode = "sv.socket{}.uncore0.imc{}_m2mem_mode.show()"
    alertsignal = "sv.socket{}.uncore0.imc{}_c{}_alertsignal.show()".format(Loc.msocket, Loc.imc, Loc.channel)
    correrrorstatus = "sv.socket{}.uncore0.imc{}_c{}_correrrorstatus.show()".format(Loc.msocket, Loc.imc,
                                                                                         Loc.channel)
    sparing_patrol_status = "sv.socket{}.uncore0.imc{}_sparing_patrol_status.show()"
    adddc_sparing = "sv.socket{}.uncore0.imc{}_sparing_control.adddc_sparing".format(Loc.msocket, Loc.imc)
    set_temp_lo = "sv.socket{}.uncore0.imc{}_c{}_dimm_temp_th_{}.temp_lo=0x0".format(Loc.msocket, Loc.imc,
                                                                                          Loc.channel, Loc.dimm)
    set_temp_mid = "sv.socket{}.uncore0.imc{}_c{}_dimm_temp_th_{}.temp_mid=0x0".format(Loc.msocket, Loc.imc,
                                                                                            Loc.channel, Loc.dimm)
    show_field_reg = "sv.sockets.uncore0.showsearch({!r},'f')"
    show_reg = "sv.sockets.uncore0.showsearch({!r})"
    core_count = "len(sv.socket0.cores)"

    buddy_rank = "sv.socket{}.uncore0.imc{}_c{}_adddc_region{}_control.nonfailed_cs"
    buddy_bg = "sv.socket{}.uncore0.imc{}_c{}_adddc_region{}_control.nonfailed_bg"
    buddy_bank = "sv.socket{}.uncore0.imc{}_c{}_adddc_region{}_control.nonfailed_ba"
    region_size = "sv.socket{}.uncore0.imc{}_c{}_adddc_region{}_control.region_size"

    pcie_present = "sv.socket{}.uncore0.pxp_{}_lnksts.data_link_layer_link_active"
    comp_timeout_severity = "sv.socket{}.uncore0.pxp_{}_uncerrsev.completion_time_out_severity=1".format(Loc.psocket,
                                                                                     Sys.PORT_MAP[Loc.pcie_port][1])


# 不同RAS功能的BIOS设置
class Bios:
    DFX = {
        "DFXEnable": 1,
        # "DfxDisableBiosDone": 1,
        "LockChipset": 0,
        "DirectoryModeEn": 0,
        "RasLogLevel": 3,
    }

    ADDDC = {
        "ADDDCEn": 1,
        "PlusOneEn": 1,
        "spareErrTh": 1,
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
class TestList:
    # 按测试Case分类
    FDM = [
        "Testcase_FDM_SMI_001",
        "Testcase_FDM_SMI_002",
        "Testcase_FDM_SMI_003",
        "Testcase_FDM_SMI_004",
        "Testcase_FDM_SMI_005",
        "Testcase_FDM_SMI_006",
        "Testcase_FDM_SMI_007",

        "Testcase_FDM_OS_CE_001",

        "Testcase_FDM_PcieNonFatal_001",

        "Testcase_FDM_PatrolScrub_001",

        "Testcase_FDM_SMI_CollectInfo_001",

        "Testcase_FDM_PostErrReport_001",
        "Testcase_FDM_PostErrReport_002",

        "Testcase_FDM_IIOUR_001",
        "Testcase_FDM_IIOUR_002",
        "Testcase_FDM_IIOUR_003",
        "Testcase_FDM_IIOUR_004",
        "Testcase_FDM_IIOUR_005",

        "Testcase_FDM_CE_001",
        # "Testcase_FDM_CE_002",  # 需要内存满配才能测试
        "Testcase_FDM_CE_003",
        "Testcase_FDM_CE_006",
        "Testcase_FDM_CE_007",

        "Testcase_FDM_UCE_001",
        "Testcase_FDM_UCE_002",
        "Testcase_FDM_UCE_003",

        "Testcase_FDM_IERR_MCERR_001",
        "Testcase_FDM_IERR_MCERR_002",
        "Testcase_FDM_IERR_MCERR_004",
        "Testcase_FDM_IERR_MCERR_005",
        "Testcase_FDM_IERR_MCERR_006",
        "Testcase_FDM_IERR_MCERR_007",
        "Testcase_FDM_IERR_MCERR_008",

        "Testcase_FDM_MEM_RAS_001",
        "Testcase_FDM_MEM_RAS_002",
        "Testcase_FDM_MEM_RAS_003",
        "Testcase_FDM_MEM_RAS_004",
        "Testcase_FDM_MEM_RAS_007",  # ICX没有SDDC功能
        "Testcase_FDM_MEM_RAS_008",
        "Testcase_FDM_MEM_RAS_009",
        "Testcase_FDM_MEM_RAS_010",
        "Testcase_FDM_MEM_RAS_011",
        "Testcase_FDM_MEM_RAS_013",

        "Testcase_FDM_Other_001",
        "Testcase_FDM_Other_002",
        "Testcase_FDM_Other_004",
        "Testcase_FDM_Other_005",
        "Testcase_FDM_Other_008",
    ]

    MEM = [
        "Testcase_MemRAS_001",
        "Testcase_MemRAS_002",
        "Testcase_MemRAS_003",
        "Testcase_MemRAS_004",
        "Testcase_MemRAS_005",
        "Testcase_MemRAS_006",
        "Testcase_MemRAS_007",
        "Testcase_MemRAS_008",
        "Testcase_MemRAS_009",

        "Testcase_MemRAS_010",
        "Testcase_MemRAS_011",
        "Testcase_MemRAS_012",
        "Testcase_MemRAS_013",
        "Testcase_MemRAS_014",
        "Testcase_MemRAS_015",
        "Testcase_MemRAS_016",
        "Testcase_MemRAS_017",
        "Testcase_MemRAS_018",
        "Testcase_MemRAS_019",
        "Testcase_MemRAS_020",
        "Testcase_MemRAS_021",
        "Testcase_MemRAS_022",
        "Testcase_MemRAS_023",
        "Testcase_MemRAS_024",
        "Testcase_MemRAS_025",

        "Testcase_MemRAS_028",
        "Testcase_MemRAS_029",
        "Testcase_MemRAS_032",
        "Testcase_MemRAS_033",
        "Testcase_MemRAS_034",
        "Testcase_MemRAS_035",
        "Testcase_MemRAS_037",
    ]

    CPU = [
        "Testcase_CPURAS_001",
        "Testcase_CPURAS_002",
        "Testcase_CPURAS_003",
        "Testcase_CPURAS_008",
        "Testcase_CPURAS_009",
        "Testcase_CPURAS_010",
        "Testcase_CPURAS_011",
        "Testcase_CPURAS_012",
        "Testcase_CPURAS_013",
        "Testcase_CPURAS_014",
        "Testcase_CPURAS_015",
        "Testcase_CPURAS_016",
        "Testcase_CPURAS_017",
        "Testcase_CPURAS_018",
        "Testcase_CPURAS_019",
        "Testcase_CPURAS_020",
        "Testcase_CPURAS_021",
        "Testcase_CPURAS_022",
    ]

    # RAS功能集合
    ADDDC = [
        "Testcase_MemRAS_010",
        "Testcase_MemRAS_011",
        "Testcase_MemRAS_012",
        "Testcase_MemRAS_013",
        "Testcase_MemRAS_014",
        "Testcase_MemRAS_015",
        "Testcase_MemRAS_016",
        "Testcase_MemRAS_017",
        "Testcase_MemRAS_018",
        "Testcase_MemRAS_019",
        "Testcase_MemRAS_020",
        "Testcase_MemRAS_021",
        "Testcase_MemRAS_022",
        "Testcase_MemRAS_023",
        "Testcase_MemRAS_024",
        "Testcase_MemRAS_025",
    ]

    Mirror = [
        "Testcase_MemRAS_001",
        "Testcase_MemRAS_002",
        "Testcase_MemRAS_003",
        "Testcase_MemRAS_004",
        "Testcase_MemRAS_005",
        "Testcase_MemRAS_006",
        "Testcase_MemRAS_007",
        "Testcase_MemRAS_008",
        "Testcase_MemRAS_009",
    ]

    MSP = [
        "Testcase_EDMA_001",
        "Testcase_EDMA_002",
        "Testcase_EDMA_003",
        "Testcase_EDMA_004",
        "Testcase_GPIOMulti_002",
        "Testcase_GPIOMulti_003",
        "Testcase_GPIORAS_002",
        "Testcase_GPIORAS_003",
        "Testcase_GPIORAS_004",
    ]

    # 【可在此处添加需要自定义的测试集合】
    Custom = [

    ]
