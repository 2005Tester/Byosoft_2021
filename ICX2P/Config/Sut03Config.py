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
from ICX2P.Config.PlatConfig import Key

# Sut01: Host IP 192.168.111.15
class Env:
    # Define test plan
    TESTCASE_CSV = "ICX2P\\AllTest.csv"
    RELEASE_BRANCH = "2288V6_017"

    # Report Setting
    PROJECT_NAME = "2288V6"
    SUT_CONFIG = "SUT03"
    REPORT_TEMPLATE = "ICX2P\\Report\\template"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\ICX2P\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    HPM_DIR = ''
    INI_DIR = ''
    SHAR_DIR = '\\\\byodiskstation1\\PublicRW\\QA\\AT Report\\2288V6\\{0}'.format(timestamp)

    # Serial Port Configuration
    BIOS_SERIAL = "com5"

    # BMC Configuration
    BMC_IP = '192.168.111.16'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9001'
    PORT = 22

    # BIOS Configuration
    BIOS_PW_DEFAULT = "Admin@9000"
    BIOS_PASSWORD = 'Admin@9009'

    # OS Configuration
    OS_IP = '192.168.111.17'
    OS_USER = 'root'
    OS_PASSWORD = 'root'

    OS_IP_LEGACY = "192.168.111.17"

    # Tool definition
    UNI_PATH = "/root/flashtool/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/Cscripts'
    CHIPSEC_PATH = "/root/chipsec"

    # BIOS Firmware Directory, Must manual copy image files to the directory before test
    BIOS_PATH = r"\\ByoDiskStation1\PublicRW\QA\Firmware\2288V6\BIOS"


# The SUT physical system configuration
class SysCfg:
    CPU_CNT = 2  # cpu socket count
    REAR_USB_CNT = 2
    BUILDIN_USB_CNT = 1
    DIMM_SIZE = 96  # /GB
    USB_Storage = 0  # usb disk inserted

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
    CPU_TYPE = "6348"
    CPU_FREQ = "2.6"
    PRO_ID = "000606A6"
    CPU_info = [f'Processor ID\s+{PRO_ID}', f'Processor Frequency\s+(?:{CPU_FREQ}00GHz.*){CPU_CNT}']
    # CPU_SKU = ["Processor {0} Version \s+Intel\(R\) Xeon\(R\) Gold {1} CPU @ {2}0GHz"
    #            .format(cpu + 1, "\s*".join(CPU_TYPE), CPU_FREQ) for cpu in range(CPU_CNT)]

    DIMM_FREQ = 3200  # Mhz
    DIMM_info = [
        'DIMM000\(A\)\s+S0.CA.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM010\(B\)\s+S0.CB.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM020\(C\)\s+S0.CC.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM030\(D\)\s+S0.CD.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM040\(E\)\s+S0.CE.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM050\(F\)\s+S0.CF.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM060\(G\)\s+S0.CG.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM070\(H\)\s+S0.CH.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM100\(A\)\s+S1.CA.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM110\(B\)\s+S1.CB.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM120\(C\)\s+S1.CC.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM130\(D\)\s+S1.CD.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM140\(E\)\s+S1.CE.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM150\(F\)\s+S1.CF.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM160\(G\)\s+S1.CG.D0:3200MT/s Hynix DRx4 64GB RDIMM',
        'DIMM170\(H\)\s+S1.CH.D0:3200MT/s Hynix DRx4 64GB RDIMM',
    ]

    # Boot Option Flag
    Legacy_OS = 'P4-MG05ACA800E SATA- HDD 8'
    Legacy_PXE = 'IBA XE Slot 3101 v2358 Port 1 SLOT1'
