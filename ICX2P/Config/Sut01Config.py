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
    # Define test plan
    TESTCASE_CSV = "ICX2P\\AllTest.csv"

    # Report Setting
    PROJECT_NAME = "2288V6"
    SUT_CONFIG = "SUT1-Full-DIMM"
    REPORT_TEMPLATE = "ICX2P\\Report\\template"
    RELEASE_BRANCH = "2288V6_016"

    # Log settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\ICX2P\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # BIOS Serial setting
    BIOS_SERIAL = "com3"

    # BMC Configuration
    BMC_IP = '192.168.111.192'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9001'

    # OS Configuration
    OS_IP_LEGACY = '192.168.111.195'
    OS_IP = '192.168.111.194'
    OS_USER = 'root'
    OS_PASSWORD = '1'

    # Tool definition
    UNI_PATH = "/root/flashtool/unitool"
    RW_PATH = '/root/rw'
    CSCRIPTS_PATH = '/root/Cscripts'
    CHIPSEC_PATH = "/root/chipsec"

    # BIOS Firmware Directory, Must manual copy image files to the directory before test
    BIOS_PATH = r"\\ByoDiskStation1\PublicRW\QA\Firmware\2288V6\BIOS"

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

# The SUT physical system configuration
class SysCfg:
    CPU_CNT = 2  # cpu socket count
    REAR_USB_CNT = 2
    BUILDIN_USB_CNT = 1
    DIMM_SIZE = 64  # /GB
    USB_Storage = 3  # usb disk inserted

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
        'Processor ID\s+000606A6', 
        'Processor Frequency\s+2.000GHz',
        "Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6\s+330 CPU @ 2.00GHz",
        "Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6\s+330 CPU @ 2.00GHz"
        ]
    DIMM_FREQ = 2933  # Mhz
    DIMM_INFO = ['DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM160\(G\)\s+S1.CG.D0:2933MT/s Hynix DRx4 32GB RDIMM']

    # Boot Option Flag
    Legacy_OS = '\(Bus 32 Dev 00\)PCI RAID Adapter RAID CARD'
    Legacy_PXE = 'IBA XE Slot 4B00 v2358 Port 0 SLOT2'
