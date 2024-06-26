#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
from ICX2P.Tools.Material.CPU import Icx6330 as CPU


class Env:
    """Environment Configuration"""

    # Report Setting
    SUT_CONFIG = "SUT1-Full-DIMM"  # SUT名称 (batf)

    # Log settings
    LOG_DIR = 'c:\\daily\\ICX2P_Sut01'

    # BIOS Serial setting
    BIOS_SERIAL = "com5"

    # BMC Configuration
    BMC_IP = '192.168.111.192'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9001'

    # UEFI OS
    OS_IP = '192.168.111.194'
    OS_USER = 'root'
    OS_PASSWORD = '1'

    # UEFI OS名称：PlatConfig.BootOS中定义的OS名称
    OS_NAME = "SLES"

    # Legacy OS
    OS_IP_LEGACY = '192.168.111.195'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = '1'

    # 系统开机时间(s)
    BOOT_DELAY = 300

    # Smbios Path
    Smbios_PATH = 'ICX2P\\Tools\\Smbios\\Sut01\\'

    # OS Tools Path
    UNI_PATH = "/root/flashtool/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/Cscripts'
    CHIPSEC_PATH = "/root/chipsec"


# SUT Physical Components Config
class SysCfg:
    # CPU型号
    CPU_TYPE: str = CPU.Type            # CPU Production Name
    CPU_CODE: str = CPU.Code            # CPU Code Name
    CPU_CODE_L: str = CPU.CodeLong      # CPU Long Code Name
    CPU_BASE: int = CPU.BaseFreq        # CPU Base Frequency
    CPU_TURBO: int = CPU.TurboFreq      # CPU Turbo Frequency
    CPU_CORES: int = CPU.Cores          # CPU Physical Cores
    CPU_STEP: str = CPU.Stepping        # CPU Stepping
    CPU_L1: int = CPU.L1_Cache          # CPU L1 Cache(KB)
    CPU_L2: int = CPU.L2_Cache          # CPU L2 Cache(KB)
    CPU_L3: int = CPU.L3_Cache          # CPU L3 Cache(KB)
    CPU_M_FREQ: int = CPU.Max_Mem_Freq  # CPU Max Supported DDR Frequency(MHz)
    CPU_TDP: int = CPU.TDP              # CPU Thermal Design Power(W)
    CPU_ID: str = CPU.CPUID             # CPU ProcessorID

    # DIMM型号
    DIMM_SIZE = 32                      # 单根内存条容量
    DIMM_VENDOR = "Hynix"               # DIMM条 厂商
    DIMM_FREQ = 2933                    # MHz
    DIMM_RANK_BW = "DRx4"               # Rank & BandWidth
    DIMM_TYPE = "RDIMM"                 # DIMM Type

    # CPU安装位置
    CPU_POP = [0, 1]

    # DIMM 安装位置 ("{socket}{channel}{dimm}")
    DIMM_POP = ["020", "160"]

    # PCIE 设备安装位置  "Bus:Dev.Fun": {"BandWidth": "x**", "Speed": "Gen*"}
    PCIE_POP = {"31:00.0": {"BandWidth": "x08", "Speed": "Gen2"},
                "31:00.1": {"BandWidth": "x08", "Speed": "Gen2"},
                "33:00.0": {"BandWidth": "x08", "Speed": "Gen3"},
                }

    # USB Info
    USB_REAR = 2  # Rear USB Ports
    USB_BUILD_IN = 1  # Build-in USB Ports
    USB_DISK = 2  # USB Disk Inserted

    # PXE Info
    PXE_UEFI = r'UEFI PXEv4:\([0-9A-Z\-]{17}\) - Port00 SLOT1'
    PXE_LEGACY = 'IBA XE Slot 3100 v2358 Port 0 SLOT1'

    # Legacy OptionROM Info
    Option_Rom_Start = "Initializing Intel\(R\) Boot Agent XE v2.3.58"
    Option_Rom_End = "PXE 2.1 Build 092 \(WfM 2.0\)"

    # Boot Option Flag
    LEGACY_OS = '\(Bus 33 Dev 00\)PCI RAID Adapter RAID CARD'

    # network dev list order in OS
    ETH_OS = ['eth7', 'eth6']
