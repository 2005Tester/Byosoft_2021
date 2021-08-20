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


class Env:
    # Define test plan
    TESTCASE_CSV = "TCE\\AllTest.csv"

    # Report Setting
    PROJECT_NAME = "TCE"
    SUT_CONFIG = "SUT1-2U-2-DIMM"
    REPORT_TEMPLATE = "TCE\\Report\\template"
    RELEASE_BRANCH = "TCE4UV6_009_TCE2UV6_006"

    # Log settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\TCE\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # BIOS Serial setting
    BIOS_SERIAL = "com4"  # rdp hostname: nuc3

    # BMC Configuration
    BMC_IP = '192.168.1.111'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9000'

    # OS Configuration
    OS_IP = '192.168.1.91'
    OS_USER = 'root'
    OS_PASSWORD = '1'

    # Tool definition
    UNI_PATH = "/root/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/cscripts'
    CHIPSEC_PATH = "/root/chipsec"

    # BIOS Firmware Directory, Must manual copy image files to the directory before test
    BIOS_PATH_2U = r"\\ByoDiskStation1\PublicRW\QA\Firmware\TCE\2U"
    BIOS_PATH_4U = r"\\ByoDiskStation1\PublicRW\QA\Firmware\TCE\4U"


# The SUT physical system configuration
class SysCfg:
    CPU_CNT = 2  # cpu socket count
    DIMM_SIZE = 64  # /GB
    USB_Storage = 0  # usb disk inserted

    PCIE_MAP = [
        {  # cpu0
            "dmi": "x4",  # GENZ 4C+(修改为Slimline)
            "0a": "x8",  # CX4 0
            "0c": "x8",  # Slimline X8连接器-卧式
            "1a": "x16",  # Riser 1-slot1
            "2a": "x4",  # NVME0
            "2b": "x4",  # NVME1
            "2c": "x4",  # CX4 1
            "2d": "x4",  # CX4 2
            "3a": "x8",  # Slimline X8连接器 单P场景RISER2应用
            "3c": "x8",  # NA/默认关闭
        },
        {  # cpu1
            # "0a": "x8",  # NA/默认关闭
            # "0c": "x8",  # NA/默认关闭
            "1a": "x8",  # NA/默认关闭
            "1c": "x8",  # 预留（BIOS默认关闭）
            "2a": "x16",  # Riser 2-slot2
            "3a": "x16",  # NA/默认关闭
        }]

    # CPU, DIMM info
    CPU_TYPE = "6338N"
    CPU_FREQ = "2.2"
    CPU_INFO = ['Processor ID\s+000606A6', 'Processor Frequency\s+2.200GHz']
    CPU_SKU = ['Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz',
               'Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz']
    DIMM_FREQ = 2933  # Mhz
    DIMM_INFO = ['DIMM000\(A\)\s+S0.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM100\(A\)\s+S1.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM']

    # PPD, PAD, TIMER and DIMM TH_0 registers - read by cscripts
    cke_ll0_ppd = ['0x00000001:ddrt_cke_en(24:24)', '0x00000001:ppd_en(09:09)', '0x00000000:apd_en(08:08)', '0x0000000f:cke_idle_timer(07:00)']
    cke_ll0_apd = ['0x00000001:ddrt_cke_en(24:24)', '0x00000000:ppd_en(09:09)', '0x00000001:apd_en(08:08)', '0x0000000f:cke_idle_timer(07:00)']
    cke_ll0_timer = ['0x00000001:ddrt_cke_en(24:24)', '0x00000001:ppd_en(09:09)', '0x00000000:apd_en(08:08)', '0x000000bf:cke_idle_timer(07:00)']

    dimm_th0_default = ['0x00000000:temp_thrt_hyst(26:24)', '0x00000064:temp_hi(23:16)', '0x0000005f:temp_mid(15:08)', '0x00000055:temp_lo(07:00)']
    dimm_th0_2X = ['0x00000000:temp_thrt_hyst(26:24)', '0x00000064:temp_hi(23:16)', '0x0000005f:temp_mid(15:08)', '0x00000000:temp_lo(07:00)']
