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
    # Report Setting
    PROJECT_NAME = "2288V6"
    SUT_CONFIG = "SUT1-Full-DIMM"
    REPORT_TEMPLATE = "ICX2P\\Report\\template"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\ICX2P\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com3"

    # BMC Configuration
    BMC_IP = '192.168.2.102'
    BMC_USER = 'Administrator'
    BMC_PASSWORD = 'Admin@9001'

    # BIOS Configuration
    BIOS_PW_DEFAULT = "Admin@9000"
    BIOS_PASSWORD = 'Admin@9009'

    # OS Configuration
    OS_IP = '192.168.3.200'
    OS_USER = 'root'
    OS_PASSWORD = '1'

    # Tool definition
    UNI_PATH = "/root/flashtool/unitool"
    RW_PATH = '/root/rw'

    # BIOS Firmware Directory, Must manual copy image files to the directory before test
    BIOS_PATH = r"\\ByoDiskStation1\PublicRW\QA\Firmware\2288V6\BIOS"


# The SUT physical system configuration
class SysCfg:
    CPU_CNT = 2  # cpu socket count
    REAR_USB_CNT = 2
    BUILDIN_USB_CNT = 1
    DIMM_SIZE = 96  # /GB

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
    CPU_info = ['Processor ID\s+000606A6', 'Processor Frequency\s+2.000GHz']
    DIMM_info = ['DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM160\(G\)\s+S1.CG.D0:2933MT/s Hynix DRx4 32GB RDIMM']
