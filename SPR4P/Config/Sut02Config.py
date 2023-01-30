#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
from SPR4P.Resource.Material.CPU import QYFR as CPU
from SPR4P.Resource.Material.DIMM import Samsung_16G_1Rx8_4800 as DIMM
from SPR4P.Resource.Material.External import HDDBP8 as HDDBP
from SPR4P.Config.ProjConfig import Spr5885HV7 as PROJ


class Env(PROJ):
    """Environment Configuration"""

    # Report Setting
    SUT_CONFIG = "SUT2-32-DIMM"  # SUT名称 (batf)

    # Log settings
    LOG_DIR = 'c:\\daily\\SPR4P_Sut02'

    # BIOS Serial setting
    BIOS_SERIAL = "com5"

    # BMC Configuration
    BMC_IP = '192.168.120.9'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9001'

    # UEFI OS
    OS_IP = '192.168.111.201'
    OS_USER = 'root'
    OS_PASSWORD = 'root'

    # Legacy OS
    OS_IP_LEGACY = '192.168.111.195'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = '1'

    # 系统开机时间(s)
    BOOT_DELAY = 10 * 60
    BOOT_FULL_DBG = 20 * 60
    BOOT_RMT = 2 * 60 * 60

    # Smbios Path
    Smbios_PATH = 'SPR4P\\Resource\\Smbios\\Sut02\\'

    # OS Tools Path
    UNI_PATH = "/root/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/Cscripts'
    CHIPSEC_PATH = "/root/chipsec"


# SUT Physical Components Config
class Sys:
    # CPU型号
    CPU_TYPE: str = CPU.Type                 # CPU Production Name (Xeon)
    CPU_CODE: str = CPU.Code                 # CPU Code Name (SPR)
    CPU_CODE_L: str = CPU.CodeLong           # CPU Long Code Name (Sapphire Rapids)
    CPU_BASE: int = CPU.BaseFreq             # CPU Base Frequency [GHz] (1.9)
    CPU_TURBO: int = CPU.TurboFreq           # CPU Turbo Frequency [Ghz] (2.8)
    CPU_CORES: int = CPU.Cores               # CPU Physical Cores (56)
    CPU_STEP: str = CPU.Stepping             # CPU Stepping (D0)
    CPU_L1: int = CPU.L1_Cache               # CPU L1 Cache per package [KB]
    CPU_L2: int = CPU.L2_Cache               # CPU L2 Cache per package [KB]
    CPU_L3: int = CPU.L3_Cache               # CPU L3 Cache per package [KB]
    CPU_M_FREQ: int = CPU.Max_MemFreq_2DPC   # CPU Max Supported DDR Frequency [MHz] (4800)
    CPU_TDP: int = CPU.TDP                   # CPU Thermal Design Power(W)
    CPU_ID: str = CPU.CPUID                  # CPU ProcessorID

    # DIMM型号
    DIMM_SIZE: int = DIMM.Size               # 单根内存条容量 [GB] (32)
    DIMM_VENDOR: str = DIMM.Vendor           # DIMM条 厂商 (Samsung)
    DIMM_FREQ: int = DIMM.Freq               # 内存频率 [MHz] (3200)
    DIMM_RANK_CNT: int = DIMM.RankCnt        # Rank Count (2)
    DIMM_DRAM_BW: int = DIMM.DRAM_BW         # 内存颗粒位宽 [bit] (4)
    DIMM_RANK_TYPE: str = DIMM.RankType      # Rank & BitWidth (DRx4)
    DIMM_BW: int = DIMM.DIMM_BW              # 内存条位宽 [bit] (80)
    DIMM_TYPE: str = DIMM.Type               # DIMM Type (RDIMM)

    # CPU安装位置
    CPU_POP = [0, 1]

    # DIMM 安装位置 ("{socket}{channel}{dimm}")
    DIMM_POP = ["000", "001", "010", "011", "020", "021", "030", "031", "040", "041", "050", "051", "060", "061", "070", "071"]

    PCIE_INFO = """
+----------------------------------------------------------------------+
| RootPortSBDF  |Type&ID|  LINKCAP |LINKSTS|  DeviceSBDF |   Vid|   Did|
|---------------+-------+----------+-------+-------------+------+------|
|  00:97:01:00  |SLOT 06|0x00425882| 0x1082| 00:98:00:00 |0x8086|0x1563|
|---------------+-------+----------+-------+-------------+------+------|
|  00:97:01:00  |SLOT 06|0x00425882| 0x1082| 00:98:00:01 |0x8086|0x1563|
+----------------------------------------------------------------------+
"""

    # USB Info
    USB_PORT_REAR = 2               # USB Rear Ports
    USB_PORT_FRONT = 2              # USB Front Ports
    USB_PORT_BUILDIN = 1            # USB Build-in Ports

    USB_STORAGE = 0                 # USB Storage Devices
    USB_MOUSE = 1
    USB_KEYBOARD = 1

    # PXE Info
    PXE_UEFI_DEV = r'UEFI PXEv4:.* - Port01'
    PXE_UEFI_MSG = "Install CentOS"
    PXE_LEGACY_DEV = 'IBA XE Slot 3100 v2358 Port 0 SLOT1'
    PXE_LEGACY_MSG = "Booting EFI Network for IPv4"

    # HTTPS Info
    HTTP4_UEFI_DEV = r'UEFI HTTPSv4:.* - SLOT2 Port02'
    HTTP4_UEFI_MSG = r'Shell>'
    HTTP6_UEFI_DEV = r'UEFI HTTPSv6:.* - SLOT2 Port02'
    HTTP6_UEFI_MSG = r'Shell>'

    # Legacy OptionROM Info
    Option_Rom_Start = "Initializing Intel\(R\) Boot Agent XE v2.3.58"
    Option_Rom_End = "PXE 2.1 Build 092 \(WfM 2.0\)"

    # Boot Option Flag
    OS_UEFI = "RHEL"                                            # UEFI OS名称 (PlatConfig.BootOS中定义的OS名称)
    OS_LEGACY = '\(Bus 33 Dev 00\)PCI RAID Adapter RAID CARD'   # Legacy OS
    BOOT_DVD = 'Virtual DVD-ROM VM'                             # DVD Boot Option
    BOOT_USB = ""                                               # USB Boot Option

    # Network dev list in OS
    ETH_OS = ['eth7', 'eth6']

    # 背板属性定义
    HDDBP_controller = HDDBP.Controller
    HDDBP_port = HDDBP.Ports

    # HTTPS 加载证书路径
    PATH_CERT = ["TLS Certificate Manager", "CA Manager", "Import Certificate", "Enroll Cert Using File",
                 "NO VOLUME LABEL.*GPT.*", "<EFI>", "<redhat>"]
    PATH_CERT_OS = "/boot/efi/EFI/redhat/root.crt"

    TPM = None

    NETWORK_PORT = 2  # 全部网口数量

    OCP_PORT = 0


