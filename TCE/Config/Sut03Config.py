#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import os
import datetime


# OS Boot Option Keywords
class BootOS:
    name_ruler = r"RAID CARD|HDD\s*\d+|NVME\s*\d+|SLOT\s*\d+"
    SLES = f"sled-secureboot.*?(?:{name_ruler})"
    Ubuntu = f"ubuntu.*?(?:{name_ruler})"


class Env:
    # URL of test result database api to generate test report
    REPORT_URL = 'http://192.168.113.234/api/v1/report'

    # Define test plan
    TESTCASE_CSV = "TCE\\AllTestLocal.csv"

    # Report Setting
    PROJECT_NAME = "TCE"
    SUT_CONFIG = "Sut03"  # 4U-Full-DIMM
    REPORT_TEMPLATE = "TCE\\Report\\template"
    RELEASE_BRANCH = "TCEV6_022"
    PREVIOUS_BRANCH = 'TCEV6_021'

    # Log settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\TCE_{0}\\{1}'.format(SUT_CONFIG, timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # BIOS Serial setting
    BIOS_SERIAL = "com10"  # rdp hostname: desktop-ft2tm75

    # BMC Configuration
    BMC_IP = '192.168.111.113'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9000'

    # OS Configuration
    OS_IP = '192.168.111.116'
    OS_IP_UBUNTU = '192.168.111.21'
    OS_USER = 'root'
    OS_PASSWORD = '1'

    # Tool definition
    UNI_PATH = "/root/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/cscripts'
    CHIPSEC_PATH = "/root/chipsec"

    # BIOS hpm img Directory, Must manual copy image files to the directory before test
    BIOS_PATH_2U = r"\\ByoDiskStation1\PublicRW\QA\Firmware\TCE\2U"
    BIOS_PATH_4U = r"\\ByoDiskStation1\PublicRW\QA\Firmware\TCE\4U"

    # Redfish configuration
    REDFISH_API = {
        "SYSTEM": "/redfish/v1/Systems/Blade1",
        "CHASSIS": "/redfish/v1/Chassis/Blade1",
        "MANAGER": "/redfish/v1/Managers/Blade1"
    }


# The SUT physical system configuration
class SysCfg:
    CPU_CNT = 2  # cpu socket count
    CPU_CORE = 32  # cpu core count
    DIMM_SIZE = 128  # /GB
    USB_Storage = 0  # usb disk inserted

    PCIE_MAP = [
        {  # cpu0
            "dmi": "x4",  # PCH_DMI[3:0]
            "0a": "x16",  # RISER4-slot1 2
            "1a": "x16",  # RISER4-slot5
            "2a": "x16",  # RISER2-slot6
            # "3a": "x8",  # NC
            "3c": "x4",  # CX4
            "3d": "x4",  # I350
        },
        {  # cpu1
            "0a": "x16",  # CX5/CX6
            "1a": "x4",  # NVME0
            "1b": "x4",  # NVME1
            "1c": "x8",  # Riser1-slot8
            "2a": "x16",  # Riser1-slot7
            # "3a": "x16",  # NC
        }]

    # CPU, DIMM info
    CPU_TYPE = "6338N"
    CPU_FREQ = "2.2"
    CPU_INFO = [
        'Processor BSP Revision\s+606A6 \- ICX D2',
        'Processor ID\s+000606A6',
        'Processor Frequency\s+2.200GHz',
        'Microcode Revision\s+0D000311',
        'Processor Voltage\s+1.6V',
        'Active Cores/Total Cores\s+32/32',
        'Active Threads\s+64',
        'L1 Cache RAM\(Per Core\)\s+80KB',
        'L2 Cache RAM\(Per Core\)\s+1280KB',
        'L3 Cache RAM\(Per Package\)\s+49152KB',
        "Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6\s+338N CPU @ 2.20GHz",
        "Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6\s+338N CPU @ 2.20GHz"
    ]
    CPU_SKU = ['Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz',
               'Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz']
    DIMM_FREQ = 2933  # Mhz
    DIMM_INFO = ['DIMM010\(B\)\s+S0.CB.D0:2933MT/s Hynix DRx4 32GB RDIMM']

    # PPD, PAD, TIMER and DIMM TH_0 registers - read by cscripts
    cke_ll0_ppd = ['0x00000001:ddrt_cke_en(24:24)', '0x00000001:ppd_en(09:09)', '0x00000000:apd_en(08:08)',
                   '0x0000000f:cke_idle_timer(07:00)']
    cke_ll0_apd = ['0x00000001:ddrt_cke_en(24:24)', '0x00000000:ppd_en(09:09)', '0x00000001:apd_en(08:08)',
                   '0x0000000f:cke_idle_timer(07:00)']
    cke_ll0_timer = ['0x00000001:ddrt_cke_en(24:24)', '0x00000001:ppd_en(09:09)', '0x00000000:apd_en(08:08)',
                     '0x000000bf:cke_idle_timer(07:00)']

    dimm_th0_default = ['0x00000000:temp_thrt_hyst(26:24)', '0x00000064:temp_hi(23:16)', '0x0000005f:temp_mid(15:08)',
                        '0x00000055:temp_lo(07:00)']
    dimm_th0_2X = ['0x00000000:temp_thrt_hyst(26:24)', '0x00000064:temp_hi(23:16)', '0x0000005f:temp_mid(15:08)',
                   '0x00000000:temp_lo(07:00)']

    device_order = ['eth4', 'eth15', 'eth5', 'eth14', 'eth12', 'eth13', 'eth10', 'eth11', 'eth6', 'eth7', 'eth8', 'eth9']

    # hidden items list, 目前以下选项已与byo开发团队确认, 暂不建议设置, 可根据不同平台BIOS设计优化, 单独修改或手动设置验证
    TBD_items = 'IODC|PciePhyTestMode|ConfigIOU|DdrFreqLimit|DfxSocketDevFuncHide|' \
                'AllowMixedPowerOnCpuRatio|mrcRepeatTest|LegacyRmt|EccEnable|ValidationBreakpointType|' \
                'dfxHighAddressStartBitPosition|MmcfgBase|MmcfgSize|MemTestLoops|MemChannelEnable|' \
                'DdrMemoryType|UefiOptimizedBootToggle|RmtOnAdvancedTraining|DfxB2PMailboxCmdEnMask|' \
                'memFlows|memFlowsExt|memFlowsExt2|memFlowsExt3|DfxRstCplBitsEn|' \
                'EnablePkgCCriteriaKti[1]|UefiOcpPxe|LegacyOcpPxe|PcieAerEcrcEn'

    Unitool_Backup_Name = [
        'Backup name:SetupBackup Restore variable Success size:0x325',
        'Backup name:PchSetupBackup Restore variable Success size:0x420',
        'Backup name:MeRcConfigurationBackup Restore variable Success size:0x55',
        'Backup name:SocketIioConfigBackup Restore variable Success size:0x20BA',
        'Backup name:SocketCommonRcConfigBackup Restore variable Success size:0x3B',
        'Backup name:SocketMpLinkConfigBackup Restore variable Success size:0xAD',
        'Backup name:SocketMemoryConfigBackup Restore variable Success size:0x3EA',
        'Backup name:SocketPowerManagementConfigBackup Restore variable Success size:0x1D6',
        'Backup name:SocketProcessorCoreConfigBackup Restore variable Success size:0x14E',
        'Backup name:MemBootHealthConfigBackup Restore variable Success size:0x13',
        'Backup name:BootClassOrderBackup Restore variable Success size:0x4',
        'Backup name:SetupBackup Restore variable Success size:0x18',
    ]
