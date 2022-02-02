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


# Sut01: Host IP 192.168.111.93
class Env:
    # URL of test result database api to generate test report
    REPORT_URL = 'http://192.168.113.234/api/v1/report'

    # Define test plan
    TESTCASE_CSV = "SPR4P\\AllTest.csv"
    if os.path.exists("SPR4P\\AllTestLocal.csv"):
        TESTCASE_CSV = "SPR4P\\AllTestLocal.csv"

    # Report Setting
    PROJECT_NAME = "5885HV7"
    SUT_CONFIG = "SUT1-Full-DIMM"
    REPORT_TEMPLATE = "SPR4P\\Report\\template"
    RELEASE_BRANCH = "5885HV7_002"

    # Log settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\SPR4P_Sut01\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # BIOS Serial setting
    BIOS_SERIAL = "com4"

    # BMC Configuration
    BMC_IP = '192.168.120.6'
    BMC_USER = 'a'
    BMC_PASSWORD = 'a'

    # OS Configuration
    OS_IP_LEGACY = '192.168.111.195'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = '1'

    OS_IP = '192.168.111.69'
    OS_USER = 'root'
    OS_PASSWORD = 'byo@123'

    # Smbios Path
    Smbios_PATH = 'SPR4P\\Resource\\Smbios\\Sut01\\'
    # Tool definition
    UNI_PATH = "/root/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/Cscripts'
    CHIPSEC_PATH = "/root/chipsec"

    # Redfish configuration
    REDFISH_API = {
        "SYSTEM": "/redfish/v1/Systems/1",
        "CHASSIS": "/redfish/v1/Chassis/1",
        "MANAGER": "/redfish/v1/Managers/1"
    }

    # BIOS Firmware Directory, Must manual copy image files to the directory before test
    BIOS_PATH = r"\\ByoDiskStation1\PublicRW\QA\Firmware\5885HV7\BIOS"

    #全打印开启后，检查的关键字
    oem_list_Example = ['OemId', 'OemTableId', 'OemRevision',   'Oem POSTCODE=/<^\d{2}$/>']
    
    # 精简打印，华为要求 LogTime_check_list
    LogTime_Dedicated = [
        'iBMC IP : 192.168.111.192',
        'START_SOCKET_1_DIMMINFO_TABLE',
        'STOP_SOCKET_1_DIMMINFO_TABLE',
        'START_SOCKET_0_DIMMINFO_TABLE',
        'STOP_SOCKET_0_DIMMINFO_TABLE',
        'START_DIMMINFO_SYSTEM_TABLE',
        'STOP_DIMMINFO_SYSTEM_TABLE',
        'CPU type : Ice Lake',
        'Total Memory : 65536MB',
        "PCIE LINK STATUS: \\d+:\\d+.\\d+: Link up as x08 Gen\\d+!",
        "PCIE LINK STATUS: \\d+:\\d+.\\d+: Link up as x08 Gen\\d+!",
        "PCIE LINK STATUS: \\d+:\\d+.\\d+: Link up as x08 Gen\\d+!"]


    # 可以忽略的ibmc告警信息
    exclusion = ['Failed RAID array detected.']

# The SUT physical system configuration
class SysCfg:
    CPU_CNT = 2  # cpu socket count
    CPU_CORE_CNT = 28
    REAR_USB_CNT = 2
    BUILDIN_USB_CNT = 1
    DIMM_SIZE = 64  # /GB
    USB_Storage = 2  # usb disk inserted

    PCIE_MAP = [
        {  # cpu0
            "0a": "x16",  # ocp
            "1a": "x8",  # slot1
            "1c": "x8",  # build-in raid
            "2a": "x16",  # slot2
            "3a": "x16"  # slot7
        },
        {  # cpu1
            "0a": "x16",  # slot3
            "1a": "x16",  # slot4
            # "2a": "x8",  # Slimline3
            # "2c": "x8",  # Slimline4
        }]

    # CPU, DIMM info
    CPU_TYPE = "6330"
    CPU_FREQ = "2.0"
    CPU_INFO = [
        'Processor BSP Revision\s+606A6 \- ICX D1',
        'Processor ID\s+000606A6',
        'Processor Frequency\s+2.000GHz',
        'Microcode Revision\s+0D000311',
        'Processor Voltage\s+1.6V',
        'Active Cores/Total Cores\s+28/28',
        'Active Threads\s+56',
        'L1 Cache RAM\(Per Core\)\s+80KB',
        'L2 Cache RAM\(Per Core\)\s+1280KB',
        'L3 Cache RAM\(Per Package\)\s+43008KB',
        "Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6\s+330 CPU @ 2.00GHz",
        "Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6\s+330 CPU @ 2.00GHz"
    ]
    DIMM_FREQ = 2933  # Mhz
    DIMM_INFO = ['DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM160\(G\)\s+S1.CG.D0:2933MT/s Hynix DRx4 32GB RDIMM']
    # Upi Status
    upi_state = ['Current UPI Link Speed\s+Fast', 'Current UPI Link Frequency\s+11\.2\s+GT\/s']

    # defined cscripts command
    cscripts_cmd_cke = 'sv.socket0.uncore.memss.mc1.ch0.cke_ll0.show()'
    cscripts_cmd_refresh = 'sv.socket0.uncore.memss.mc1.ch0.dimm_temp_th_0.show()'
    # memory information
    memory_verify_list = ['DIMM: Hynix', 'DRAM: Hynix', '32GB\(\s+8Gbx4\s+DR', 'DDR4 RDIMM  R/C-B', '2933 21-21-21']

    # UEFI PXE
    Uefi_PXE = r'UEFI PXEv4:\([0-9A-Z\-]{17}\) - Port00 SLOT1'
    Legacy_Pxe_info = 'IBA XE'

    Option_Rom_Start = "Initializing Intel\(R\) Boot Agent XE v2.3.58"
    Option_Rom_End = "PXE 2.1 Build 092 \(WfM 2.0\)"
    # Boot Option Flag
    Legacy_OS = '\(Bus 33 Dev 00\)PCI RAID Adapter RAID CARD'
    Legacy_PXE = 'IBA XE Slot 3100 v2358 Port 0 SLOT1'

    # network dev list order in OS
    device_order = ['eth7', 'eth6']

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