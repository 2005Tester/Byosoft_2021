#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import os
import time
import importlib
from batf import var


SutCfgMde = importlib.import_module(var.get('SutCfg'), var.get('project'))


_Env = SutCfgMde.Env
_SysCfg = SutCfgMde.SysCfg


class Env(_Env):
    # Report Setting
    PROJECT_NAME = "2288V6"  # 项目名称 (batf)
    REPORT_TEMPLATE = "ICX2P\\Report\\template"
    if not hasattr(_Env, "SUT_CONFIG"):
        SUT_CONFIG = f"{PROJECT_NAME}-SUT"  # SUT缺省名称 (batf)

    # URL of test result database api to generate test report
    REPORT_URL = 'http://192.168.113.234/api/v1/report'

    # Define test plan
    TESTCASE_CSV = "ICX2P\\AllTest.csv"
    if os.path.exists("ICX2P\\AllTestLocal.csv"):
        TESTCASE_CSV = "ICX2P\\AllTestLocal.csv"

    # Create Log path
    _timestamp = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
    LOG_DIR = os.path.join(_Env.LOG_DIR, _timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # BIOS branch for master test
    LATEST_BRANCH = "master"

    # BIOS Vcs branch for release test
    RELEASE_BRANCH = "2288V6_057"
    PREVIOUS_BRANCH = "2288V6_056"

    # Redfish configuration
    REDFISH_API = {
        "SYSTEM": "/redfish/v1/Systems/1",
        "CHASSIS": "/redfish/v1/Chassis/1",
        "MANAGER": "/redfish/v1/Managers/1",
    }

    # HPM BIOS存放路径 (Release测试需要刷入HPM BIOS时，需要将HPM BIOS存放到指定路径中)
    BIOS_PATH = r"\\ByoDiskStation1\PublicRW\QA\Firmware\2288V6\BIOS"

    # 全打印开启后，检查的关键字
    oem_list_Example = ['OemId', 'OemTableId', 'OemRevision',   'Oem POSTCODE=/<^\d{2}$/>']

    # 可以忽略的BMC告警信息
    BMC_WARN_IG = ['Failed RAID array detected.', 'SSL certificate is about to expire or has expired.',
                   'The SAS or PCIe cable to front disk backplane PORTA is incorrectly connected.',
                   'The SAS or PCIe cable to front disk backplane is incorrectly connected.',
                   'The SAS or PCIe cable to front disk backplane PORTB is incorrectly connected.']


class SysCfg(_SysCfg):
    # 以下信息根据配置自动生成，一般无需修改
    ##################################################################################################################
    CPU_CNT = len(_SysCfg.CPU_POP)                          # CPU 数量
    DIMM_CNT = len(_SysCfg.DIMM_POP)                        # DIMM 数量
    MEM_FREQ = min(_SysCfg.CPU_M_FREQ, _SysCfg.DIMM_FREQ)   # 内存实际运行速率，取CPU和DIMM支持的最小值
    MEM_SIZE = _SysCfg.DIMM_SIZE * DIMM_CNT                 # 系统安装的全部内存容量(GB)

    # 内存位置 (用于Cscript读寄存器)
    MEM_SOCKET = _SysCfg.DIMM_POP[0][0]                             # Memory Present: Socket
    MEM_MC = int(int(_SysCfg.DIMM_POP[0][1]) / SutCfgMde.CPU.CHs)   # Memory Present: Memory Controller
    MEM_CH = int(_SysCfg.DIMM_POP[0][1]) % SutCfgMde.CPU.CHs        # Memory Present: Memory Channel
    MEM_SLOT = _SysCfg.DIMM_POP[0][2]                               # Memory Present: Memory Slot

    # Example:　["DIMM: Hynix", "32GB", "RDIMM", "2933"]
    MEM_POST_INFO = [f'DIMM: {_SysCfg.DIMM_VENDOR}',
                     f'{_SysCfg.DIMM_SIZE}GB',
                     f'{_SysCfg.DIMM_TYPE}',
                     f'{_SysCfg.DIMM_FREQ}',
                     ]

    # Example:　Intel\(R\) Xeon\(R\) Gold 6330 CPU @ 2.00GHz
    CPU_FULL_NAME = "{0} {1} {2} CPU @ {3:.1f}0GHz".format(
        SutCfgMde.CPU.Name, '\s*'.join(SutCfgMde.CPU.Level), '\s*'.join(_SysCfg.CPU_TYPE), _SysCfg.CPU_BASE)

    # BIOS Setup　Processor Info页面详细信息
    PROC_LIST = []
    for n in range(CPU_CNT):
        PROC_LIST.append(f"Processor {n + 1} Version\s+{CPU_FULL_NAME}")

    CPU_INFO = [f'Processor BSP Revision\s+{_SysCfg.CPU_ID} \- {_SysCfg.CPU_CODE} {_SysCfg.CPU_STEP}',
                f'Processor ID\s+000{_SysCfg.CPU_ID}',
                f'Processor Frequency\s+{_SysCfg.CPU_BASE:.1f}00GHz',
                f'Processor Voltage\s+{SutCfgMde.CPU.Voltage}',
                f'Active Cores/Total Cores\s+{_SysCfg.CPU_CORES}/{_SysCfg.CPU_CORES}',
                f'Active Threads\s+{_SysCfg.CPU_CORES * 2}',
                f'L1 Cache RAM\(Per Core\)\s+{_SysCfg.CPU_L1}KB',
                f'L2 Cache RAM\(Per Core\)\s+{_SysCfg.CPU_L2}KB',
                f'L3 Cache RAM\(Per Package\)\s+{_SysCfg.CPU_L3}KB',
                ] + PROC_LIST

    # Example:　[DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM, ...]
    DIMM_INFO = []
    for dimm in _SysCfg.DIMM_POP:
        DIMM_INFO.append(
            f"DIMM{dimm}\({'ABCDEFGH'[int(dimm[1])]}\)\s+S{dimm[0]}.C{'ABCDEFGH'[int(dimm[1])]}.D{dimm[2]}:"
            f"{_SysCfg.DIMM_FREQ}MT/s {_SysCfg.DIMM_VENDOR} {_SysCfg.DIMM_RANK_BW} {_SysCfg.DIMM_SIZE}GB {_SysCfg.DIMM_TYPE}")

    # Example:　[PCIE LINK STATUS: 31:00.1: Link up as x8 Gen3",...]
    PCIE_INFO = []
    for _bdf, _peinfo in _SysCfg.PCIE_POP.items():
        PCIE_INFO.append(f"PCIE LINK STATUS: {_bdf}: Link up as {_peinfo['BandWidth']} {_peinfo['Speed']}")
    ##################################################################################################################


    # PCIE ROOT PORT: Max Support BandWidth
    PCIE_MAP = [{
            "0a": "x16",  # ocp
            "1a": "x8",  # slot1
            "1c": "x8",  # build-in raid
            "2a": "x16",  # slot2
            "3a": "x16",  # slot7
        },
        {
            "0a": "x16",  # slot3
            "1a": "x16",  # slot4
            # "2a": "x8",  # Slimline3
            # "2c": "x8",  # Slimline4
        }
    ]

    # Upi Status
    upi_state = ['Current UPI Link Speed\s+Fast', 'Current UPI Link Frequency\s+11\.2\s+GT\/s']

    # defined cscripts command
    cscripts_cmd_cke = f'sv.socket{MEM_SOCKET}.uncore.memss.mc{MEM_MC}.ch{MEM_CH}.cke_ll0.show()'
    cscripts_cmd_refresh = f'sv.socket{MEM_SOCKET}.uncore.memss.mc{MEM_MC}.ch{MEM_CH}.dimm_temp_th_{MEM_SLOT}.show()'

    # hidden items list, 目前以下选项已与byo开发团队确认, 暂不建议设置, 可根据不同平台BIOS设计优化, 单独修改或手动设置验证
    TBD_items = 'IODC|PciePhyTestMode|ConfigIOU|DdrFreqLimit|DfxSocketDevFuncHide|' \
                'AllowMixedPowerOnCpuRatio|mrcRepeatTest|LegacyRmt|EccEnable|ValidationBreakpointType|' \
                'dfxHighAddressStartBitPosition|MmcfgBase|MmcfgSize|MemTestLoops|MemChannelEnable|' \
                'DdrMemoryType|UefiOptimizedBootToggle|RmtOnAdvancedTraining|DfxB2PMailboxCmdEnMask|' \
                'memFlows|memFlowsExt|memFlowsExt2|memFlowsExt3|DfxRstCplBitsEn|' \
                'EnablePkgCCriteriaKti[1]|UefiOcpPxe|LegacyOcpPxe|PcieAerEcrcEn'

    Backup_Name = ['Setup', 'PchSetup', 'MeRcConfiguration', 'SocketIioConfig', 'SocketIioConfig',
                   'SocketCommonRcConfig', 'SocketMemoryConfig', 'SocketPowerManagementConfig',
                   'SocketProcessorCoreConfig', 'MemBootHealthConfig', 'BootClassOrder']
    Unitool_Backup_Name = []
    for bak_name in Backup_Name:
        Unitool_Backup_Name.append(f'Backup name:{bak_name}Backup Restore variable Success size:0x[0-9a-fA-F]+')

    # 精简打印，华为要求 LogTime_check_list
    OEM_LOG_SUT = [
        'START_SOCKET_\d_DIMMINFO_TABLE',
        'START_DIMMINFO_SYSTEM_TABLE',
        f'BMC IP : {_Env.BMC_IP}',
        f'CPU type : {_SysCfg.CPU_CODE_L}',
        f'Total Memory : {MEM_SIZE * 1024}MB',
    ] + PCIE_INFO
