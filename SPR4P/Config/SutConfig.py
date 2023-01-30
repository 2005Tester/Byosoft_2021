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
from batf import var, MiscLib


from SPR4P.Config import Sut01Config as SutCfgMde

if not var.get('SutCfg'):
    var.set('SutCfg', ".Config.Sut01Config")
if not var.get('project'):
    var.set('project', "SPR4P")

exec("SutCfgMde = importlib.import_module(var.get('SutCfg'), var.get('project'))")  # SUT Overwrite


_Env = SutCfgMde.Env
_Sys = SutCfgMde.Sys


class Env(_Env):
    # Report Setting
    REPORT_TEMPLATE = "SPR4P\\Report\\template"

    if not hasattr(_Env, "PROJECT_NAME"):
        PROJECT_NAME = f"EagleStream"  # PROJECT_NAME缺省名称 (batf)
    if not hasattr(_Env, "SUT_CONFIG"):
        SUT_CONFIG = f"{PROJECT_NAME}-SUT"  # SUT缺省名称 (batf)

    # URL of test result database api to generate test report
    REPORT_URL = 'http://192.168.113.234/api/v1/report'

    # Create Log path
    _timestamp = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
    LOG_DIR = os.path.join(_Env.LOG_DIR, _timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Redfish configuration
    REDFISH_API = {
        "SYSTEM": "/redfish/v1/Systems/1",
        "CHASSIS": "/redfish/v1/Chassis/1",
        "MANAGER": "/redfish/v1/Managers/1",
    }

    # 全打印开启后，检查的关键字
    oem_list_Example = ['OemId', 'OemTableId', 'OemRevision',   'Oem POSTCODE=/<^\d{2}$/>']

    # 可以忽略的BMC告警信息
    BMC_WARN_IG = [
        'Failed to obtain data of the air inlet temperature.',
        'Failed to obtain data of the CPU.*core temperature',
        'Failed to obtain data of the DTS temperature for CPU',
        'Failed to obtain data of the memory.*temperature',
        '.* mounting ear is not present.',
        'The SAS or PCIe cable to front disk backplane.*is incorrectly connected.',
        'Difference between CPU.*temperature',
        'CPU.*temperature is too high and will be underclocked',
        'CPU.*core voltage .+ is lower than the undervoltage threshold', #SUT3
        'Lost fan redundancy' #SUT3
    ]


class Sys(_Sys):
    CPU_CNT = len(_Sys.CPU_POP)                                 # CPU 数量
    DIMM_CNT = len(_Sys.DIMM_POP)                               # DIMM 数量
    MEM_FREQ = min(_Sys.CPU_M_FREQ, _Sys.DIMM_FREQ)             # 内存实际运行速率，取CPU和DIMM支持的最小值
    MEM_SIZE = _Sys.DIMM_SIZE * DIMM_CNT                        # 系统安装的全部内存容量(GB)
    MAX_CORES_PLAT = 60                                         # 平台支持的最大CPU核数

    # 内存位置 (用于Cscript读寄存器)
    MEM_SOCKET = _Sys.DIMM_POP[0][0]                             # Memory Present: Socket
    MEM_MC = int(int(_Sys.DIMM_POP[0][1]) / SutCfgMde.CPU.CHs)   # Memory Present: Memory Controller
    MEM_CH = int(_Sys.DIMM_POP[0][1]) % SutCfgMde.CPU.CHs        # Memory Present: Memory Channel
    MEM_SLOT = _Sys.DIMM_POP[0][2]                               # Memory Present: Memory Slot

    # Example:　["DIMM: Hynix", "32GB", "RDIMM", "2933"]
    MEM_POST_INFO = [f'DIMM: {_Sys.DIMM_VENDOR}',
                     f'{_Sys.DIMM_SIZE}GB',
                     f'{_Sys.DIMM_TYPE}',
                     f'{_Sys.DIMM_FREQ}',
                     ]

    # Example: Intel(R) Xeon(R) Gold 6330
    # CPU_FULL_NAME = "Genuine Intel(R) CPU 0000%@"
    CPU_FULL_NAME = f"{SutCfgMde.CPU.Name} {SutCfgMde.CPU.Level} {_Sys.CPU_TYPE}"

    # Processor Info 页面详细信息
    CPU_INFO = {
        'Processor BSP Revision': f'{_Sys.CPU_ID} - {_Sys.CPU_CODE}-SP {_Sys.CPU_STEP}',
        'Processor ID': f'000{_Sys.CPU_ID}',
        'Processor Frequency': f'{_Sys.CPU_BASE:.1f}00GHz',
        'Processor Voltage': f'{SutCfgMde.CPU.Voltage}',
        'Active Cores / Total Cores': f'{_Sys.CPU_CORES}/{_Sys.CPU_CORES}',
        'Active Threads': f'{_Sys.CPU_CORES * 2}',
        'L1 Cache RAM\(Per Core\)': f'{_Sys.CPU_L1 // _Sys.CPU_CORES}KB',
        'L2 Cache RAM\(Per Core\)': f'{_Sys.CPU_L2 // _Sys.CPU_CORES}KB',
        'L3 Cache RAM\(Per Package\)': f'{_Sys.CPU_L3}KB'}

    PROCESSORS = {}
    for n in range(CPU_CNT):
        _proc_info = MiscLib.regex_unescape(f'{CPU_FULL_NAME[:23].strip()} {CPU_FULL_NAME[23:].strip()}', chrs="\(\)")
        PROCESSORS[f'Processor {n + 1} Version'] = _proc_info
    CPU_INFO.update(PROCESSORS)

    # Example:　[DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM, ...]
    DIMM_INFO = []
    for dimm in _Sys.DIMM_POP:
        DIMM_INFO.append(
            f"DIMM{dimm}\({'ABCDEFGH'[int(dimm[1])]}\)\s+S{dimm[0]}.C{'ABCDEFGH'[int(dimm[1])]}.D{dimm[2]}:"
            f"{_Sys.DIMM_FREQ}MT/s {_Sys.DIMM_VENDOR} {_Sys.DIMM_RANK_TYPE} {_Sys.DIMM_SIZE}GB {_Sys.DIMM_TYPE}")

    # Upi Status
    UPI_STATE = ['Current UPI Link Speed\s+Fast', f'Current UPI Link Frequency\s+{SutCfgMde.CPU.UpiSpeed:.1f} GT/s']

    # defined cscripts command
    CS_CKE = f'sv.socket{MEM_SOCKET}.uncore.memss.mc{MEM_MC}.ch{MEM_CH}.cke_ll0.show()'
    CS_TEMP_TH = f'sv.socket{MEM_SOCKET}.uncore.memss.mc{MEM_MC}.ch{MEM_CH}.dimm_temp_th_{MEM_SLOT}.show()'

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
        f'BMC IPv4 IP    : {_Env.BMC_IP}',
        'BMC IPv6 IP    : {0}:{0}:{0}:{0}:\s+{0}:{0}:{0}:{0}'.format(f"[0-9a-fA-F]{{4}}"),
        f'CPU type       : {_Sys.CPU_CODE_L}',
        f'Total Memory   : {MEM_SIZE}GB',
        _Sys.PCIE_INFO
    ]

