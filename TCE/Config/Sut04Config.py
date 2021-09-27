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
    SLES = "sled-secureboot"
    Ubuntu = f"ubuntu.*?(?:{name_ruler})"


class Env:
    # Define test plan
    TESTCASE_CSV = "TCE\\AllTest.csv"

    # Report Setting
    PROJECT_NAME = "TCE"
    SUT_CONFIG = "Sut04"  # 4U-RAS-4-DIMM
    REPORT_TEMPLATE = "TCE\\Report\\template"
    RELEASE_BRANCH = "TCEV6_014"

    # Log settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\TCE\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # BIOS Serial setting
    BIOS_SERIAL = "com5"  # rdp hostname: desktop-go80pcl

    # BMC Configuration
    BMC_IP = '192.168.111.115'
    BMC_USER = 'Admin#'
    BMC_PASSWORD = 'Admin@9000'

    # OS Configuration
    OS_IP = '192.168.111.117'
    OS_IP_UBUNTU = '192.168.111.xxx'
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
    CPU_INFO = ['Processor ID\s+000606A6', 'Processor Frequency\s+2.200GHz']
    CPU_SKU = ['Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz',
               'Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz']
    DIMM_FREQ = 2933  # Mhz
    DIMM_INFO = ['DIMM000\(A\)\s+S0.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM010\(B\)\s+S0.CB.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM040\(E\)\s+S0.CE.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM050\(F\)\s+S0.CF.D0:2933MT/s Hynix DRx4 32GB RDIMM']
