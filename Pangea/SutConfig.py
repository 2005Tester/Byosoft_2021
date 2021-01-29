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

###################################################
#     Test Execution and SUT Global Settings      #
###################################################
# Report and logging Settings
PROJECT_NAME = "Pangea"
SUT_CONFIG = "NVME-SH"
BOARD_TYPE = "NVME2P"
REPORT_TEMPLATE = "Pangea\\Report\\template"
# timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_DIR = 'c:\\daily\\Pangea\\{0}'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')

# Serial Port Configuration
BIOS_SERIAL = "com3"

# BMC Network Configuration
BMC_IP = '172.30.129.102'
BMC_USER = 'root'
BMC_PASSWORD = 'Huawei12#$'
PORT = 22

# OS Network Configuration
OS_IP = '192.168.100.48'
OS_USER = 'byosoft'
OS_PASSWORD = 'byosoft@123'

# Some test cases may depends on below settings
LKG_LOG_DIR = "Pangea\\Lkg"


##########################################
#               Key Mapping              #
##########################################
class Key:
    ENTER = [chr(0x0D)]
    DEL = [chr(0x7F)]
    F2 = '\33' + '2'
    # F2 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x32), chr(0x7e)]
    # F5 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x35), chr(0x7e)]
    # F6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
    F7 = '\33' + '7'
    F9 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x30), chr(0x7e)]
    F10 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x31), chr(0x7e)]
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]


# Common key order
key2default = [Key.F9, Key.Y, Key.F10, Key.Y]


####################################################################################
#     Messages to identify a specific boot option, page, menu or system status      #
####################################################################################
class Msg:
    HOTKEY_PROMPT = 'Press [Enter] to directly boot'
    HOTKEY_PROMPT_F2 = 'Press [F2]    to enter setup and select boot options'
    HOTKEY_PROMPT_F7 = 'Press [F7]    to show boot menu options'

    # Home screen with 6 icons
    HOME_PAGE = 'System Information'
    BIOS_BOOT_COMPLETE = 'BIOS startup is complete'

    # pages in BIOS configuration
    PAGE_ADVANCED = 'Advanced'
    PAGE_SECURITY = 'Security'
    PAGE_BOOT = 'Boot'
    PAGE_SAVE = 'Exit'

    # menus of CPU configuration
    CPU_MENU = 'All Cpu Information'
    CPU_CONFIG = 'Socket Configuration'
    PROCESSOR_CONFIG = 'Processor Configuration'
    MEMORY_CONFIG = 'Memory Configuration'
    MEMORY_TOPOLOGY = 'Memory Topology'

    # menus of Boot page
    Boot_MENU = 'Boot'
    Boot_OPTION = 'Boot Options'
    Boot_MANAGER = 'Boot Manager'
    PXE_PORT = 'UEFI PXEv4 (MAC:B8E3B18B06C9)\-Port1 Mgmt'
    OS_PORT = 'Euler Linux Boot'


##########################################
#     Pcie Resource Table for TC201      #
##########################################
# PCIE Resource for NVME2P board
N2_00_1B_0 = ("00:1b.0", ["Memory behind bridge: 9e400000-a03fffff [size=32M]", "Prefetchable memory behind bridge: 0000200f7ae00000-0000200fbadfffff [size=1G]"])
N2_00_1B_1 = ("00:1b.1", ["Memory behind bridge: 9c400000-9e3fffff [size=32M]", "Prefetchable memory behind bridge: 0000200fbae00000-0000200ffadfffff [size=1G]"])
N2_00_1B_2 = ("00:1b.2", ["Memory behind bridge: 94000000-9bffffff [size=128M]", "Prefetchable memory behind bridge: 0000200ffae00000-0000200ffedfffff [size=64M]"])
N2_00_1B_3 = ("00:1b.3", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: [disabled]"])
N2_00_1D_0 = ("00:1d.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: [disabled]"])
N2_00_1D_6 = ("00:1d.6", ["Memory behind bridge: 9c000000-9c3fffff [size=4M]", "Prefetchable memory behind bridge: 0000200ffee00000-0000200fffdfffff [size=16M]"])
N2_16_04_0 = ("16:04.0", ["Memory behind bridge: a4800000-a87fffff [size=64M]", "Prefetchable memory behind bridge: 0000201fbff00000-0000201fffefffff [size=1G]"])
N2_30_02_0 = ("30:02.0", ["Memory behind bridge: adc00000-b1bfffff [size=64M]", "Prefetchable memory behind bridge: 0000202f7ff00000-0000202fbfefffff [size=1G]"])
N2_30_04_0 = ("30:04.0", ["Memory behind bridge: a9c00000-adbfffff [size=64M]", "Prefetchable memory behind bridge: 0000202fbff00000-0000202fffefffff [size=1G]"])
N2_4A_02_0 = ("4a:02.0", ["Memory behind bridge: bc400000-c03fffff [size=64M]", "Prefetchable memory behind bridge: 0000203fbfc00000-0000203fffbfffff [size=1G]"])
N2_4A_04_0 = ("4a:04.0", ["Memory behind bridge: b4400000-bc3fffff [size=128M]", "Prefetchable memory behind bridge: 0000203f7fc00000-0000203fbfbfffff [size=1G]"])
N2_57_00_0 = ("57:00.0", ["Memory behind bridge: b4400000-b73fffff [size=48M]", "Prefetchable memory behind bridge: 0000203f80000000-0000203f8bffffff [size=192M]"])
N2_58_00_0 = ("58:00.0", ["Memory behind bridge: b7000000-b73fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f8b000000-0000203f8bffffff [size=16M]"])
N2_58_01_0 = ("58:01.0", ["Memory behind bridge: b6c00000-b6ffffff [size=4M]", "Prefetchable memory behind bridge: 0000203f8a000000-0000203f8affffff [size=16M]"])
N2_58_02_0 = ("58:02.0", ["Memory behind bridge: b6800000-b6bfffff [size=4M]", "Prefetchable memory behind bridge: 0000203f89000000-0000203f89ffffff [size=16M]"])
N2_58_03_0 = ("58:03.0", ["Memory behind bridge: b6400000-b67fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f88000000-0000203f88ffffff [size=16M]"])
N2_58_04_0 = ("58:04.0", ["Memory behind bridge: b6000000-b63fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f87000000-0000203f87ffffff [size=16M]"])
N2_58_05_0 = ("58:05.0", ["Memory behind bridge: b5c00000-b5ffffff [size=4M]", "Prefetchable memory behind bridge: 0000203f86000000-0000203f86ffffff [size=16M]"])
N2_58_06_0 = ("58:06.0", ["Memory behind bridge: b5800000-b5bfffff [size=4M]", "Prefetchable memory behind bridge: 0000203f85000000-0000203f85ffffff [size=16M]"])
N2_58_07_0 = ("58:07.0", ["Memory behind bridge: b5400000-b57fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f84000000-0000203f84ffffff [size=16M]"])
N2_58_08_0 = ("58:08.0", ["Memory behind bridge: b5000000-b53fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f83000000-0000203f83ffffff [size=16M]"])
N2_58_09_0 = ("58:09.0", ["Memory behind bridge: b4c00000-b4ffffff [size=4M]", "Prefetchable memory behind bridge: 0000203f82000000-0000203f82ffffff [size=16M]"])
N2_58_0A_0 = ("58:0a.0", ["Memory behind bridge: b4800000-b4bfffff [size=4M]", "Prefetchable memory behind bridge: 0000203f81000000-0000203f81ffffff [size=16M]"])
N2_58_0B_0 = ("58:0b.0", ["Memory behind bridge: b4400000-b47fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f80000000-0000203f80ffffff [size=16M]"])
N2_74_02_0 = ("74:02.0", ["Memory behind bridge: c6800000-c87fffff [size=32M]", "Prefetchable memory behind bridge: 0000204fbe000000-0000204ffdffffff [size=1G]"])
N2_97_02_0 = ("97:02.0", ["Memory behind bridge: cac00000-cacfffff [size=1M]", "Prefetchable memory behind bridge: [disabled]"])
N2_98_00_0 = ("98:00.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: [disabled]"])
N2_9F_02_0 = ("9f:02.0", ["Memory behind bridge: df000000-e2ffffff [size=64M]", "Prefetchable memory behind bridge: 0000207f7ff00000-0000207fbfefffff [size=1G]"])
N2_9F_04_0 = ("9f:04.0", ["Memory behind bridge: dd000000-deffffff [size=32M]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fffefffff [size=1G]"])
N2_AC_00_0 = ("ac:00.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fc02fffff [size=4M]"])
N2_AD_00_0 = ("ad:00.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fc02fffff [size=4M]"])
N2_B3_02_0 = ("b3:02.0", ["Memory behind bridge: e5000000-e8ffffff [size=64M]", "Prefetchable memory behind bridge: 0000208fbff00000-0000208fffefffff [size=1G]"])
N2_C5_02_0 = ("c5:02.0", ["Memory behind bridge: f2400000-fa3fffff [size=128M]", "Prefetchable memory behind bridge: 0000209f7fc00000-0000209fbfbfffff [size=1G]"])
N2_C6_00_0 = ("c6:00.0", ["Memory behind bridge: f2400000-f53fffff [size=48M]", "Prefetchable memory behind bridge: 0000209f80000000-0000209f8bffffff [size=192M]"])
N2_C7_00_0 = ("c7:00.0", ["Memory behind bridge: f5000000-f53fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f8b000000-0000209f8bffffff [size=16M]"])
N2_C7_01_0 = ("c7:01.0", ["Memory behind bridge: f4c00000-f4ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f8a000000-0000209f8affffff [size=16M]"])
N2_C7_02_0 = ("c7:02.0", ["Memory behind bridge: f4800000-f4bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f89000000-0000209f89ffffff [size=16M]"])
N2_C7_03_0 = ("c7:03.0", ["Memory behind bridge: f4400000-f47fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f88000000-0000209f88ffffff [size=16M]"])
N2_C7_04_0 = ("c7:04.0", ["Memory behind bridge: f4000000-f43fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f87000000-0000209f87ffffff [size=16M]"])
N2_C7_05_0 = ("c7:05.0", ["Memory behind bridge: f3c00000-f3ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f86000000-0000209f86ffffff [size=16M]"])
N2_C7_06_0 = ("c7:06.0", ["Memory behind bridge: f3800000-f3bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f85000000-0000209f85ffffff [size=16M]"])
N2_C7_07_0 = ("c7:07.0", ["Memory behind bridge: f3400000-f37fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f84000000-0000209f84ffffff [size=16M]"])
N2_C7_08_0 = ("c7:08.0", ["Memory behind bridge: f3000000-f33fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f83000000-0000209f83ffffff [size=16M]"])
N2_C7_09_0 = ("c7:09.0", ["Memory behind bridge: f2c00000-f2ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f82000000-0000209f82ffffff [size=16M]"])
N2_C7_0A_0 = ("c7:0a.0", ["Memory behind bridge: f2800000-f2bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f81000000-0000209f81ffffff [size=16M]"])
N2_C7_0B_0 = ("c7:0b.0", ["Memory behind bridge: f2400000-f27fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f80000000-0000209f80ffffff [size=16M]"])
N2_C5_04_0 = ("c5:04.0", ["Memory behind bridge: ea400000-f23fffff [size=128M]", "Prefetchable memory behind bridge: 0000209fbfc00000-0000209fffbfffff [size=1G]"])
N2_DE_00_0 = ("de:00.0", ["Memory behind bridge: ea400000-ed3fffff [size=48M]", "Prefetchable memory behind bridge: 0000209fc0000000-0000209fcbffffff [size=192M]"])
N2_DF_00_0 = ("df:00.0", ["Memory behind bridge: ed000000-ed3fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fcb000000-0000209fcbffffff [size=16M]"])
N2_DF_01_0 = ("df:01.0", ["Memory behind bridge: ecc00000-ecffffff [size=4M]", "Prefetchable memory behind bridge: 0000209fca000000-0000209fcaffffff [size=16M]"])
N2_DF_02_0 = ("df:02.0", ["Memory behind bridge: ec800000-ecbfffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc9000000-0000209fc9ffffff [size=16M]"])
N2_DF_03_0 = ("df:03.0", ["Memory behind bridge: ec400000-ec7fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc8000000-0000209fc8ffffff [size=16M]"])
N2_DF_04_0 = ("df:04.0", ["Memory behind bridge: ec000000-ec3fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc7000000-0000209fc7ffffff [size=16M]"])
N2_DF_05_0 = ("df:05.0", ["Memory behind bridge: ebc00000-ebffffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc6000000-0000209fc6ffffff [size=16M]"])
N2_DF_06_0 = ("df:06.0", ["Memory behind bridge: eb800000-ebbfffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc5000000-0000209fc5ffffff [size=16M]"])
N2_DF_07_0 = ("df:07.0", ["Memory behind bridge: eb400000-eb7fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc4000000-0000209fc4ffffff [size=16M]"])
N2_DF_08_0 = ("df:08.0", ["Memory behind bridge: eb000000-eb3fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc3000000-0000209fc3ffffff [size=16M]"])
N2_DF_09_0 = ("df:09.0", ["Memory behind bridge: eac00000-eaffffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc2000000-0000209fc2ffffff [size=16M]"])
N2_DF_0A_0 = ("df:0a.0", ["Memory behind bridge: ea800000-eabfffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc1000000-0000209fc1ffffff [size=16M]"])
N2_DF_0B_0 = ("df:0b.0", ["Memory behind bridge: ea400000-ea7fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc0000000-0000209fc0ffffff [size=16M]"])

PCI_NVME_2P = [N2_00_1B_0, N2_00_1B_1, N2_00_1B_2, N2_00_1B_3, N2_00_1D_0, N2_00_1D_6, N2_16_04_0, N2_30_02_0, N2_30_04_0, N2_4A_02_0, N2_4A_04_0, N2_57_00_0,
               N2_58_00_0, N2_58_01_0, N2_58_02_0, N2_58_03_0, N2_58_04_0, N2_58_05_0, N2_58_06_0, N2_58_07_0, N2_58_08_0, N2_58_09_0, N2_58_0A_0, N2_58_0B_0,
               N2_74_02_0, N2_97_02_0, N2_98_00_0, N2_9F_02_0, N2_9F_04_0, N2_AC_00_0, N2_AD_00_0, N2_B3_02_0, N2_C5_02_0, N2_C6_00_0, N2_C7_00_0, N2_C7_01_0,
               N2_C7_02_0, N2_C7_03_0, N2_C7_04_0, N2_C7_05_0, N2_C7_06_0, N2_C7_07_0, N2_C7_08_0, N2_C7_09_0, N2_C7_0A_0, N2_C7_0B_0, N2_C5_04_0, N2_DE_00_0,
               N2_DF_00_0, N2_DF_01_0, N2_DF_02_0, N2_DF_03_0, N2_DF_04_0, N2_DF_05_0, N2_DF_06_0, N2_DF_07_0, N2_DF_08_0, N2_DF_09_0, N2_DF_0A_0, N2_DF_0B_0]

# PCIE resource table for SAS2P board
S2_00_1B_0 = ("00:1b.0", ["Memory behind bridge: 9e800000-a07fffff [size=32M]", "Prefetchable memory behind bridge: 0000200f79e00000-0000200fb9dfffff [size=1G]"])
S2_00_1B_1 = ("00:1b.1", ["Memory behind bridge: 9c800000-9e7fffff [size=32M]", "Prefetchable memory behind bridge: 0000200fb9e00000-0000200ff9dfffff [size=1G]"])
S2_00_1B_2 = ("00:1b.2", ["Memory behind bridge: 94000000-9bffffff [size=128M]", "Prefetchable memory behind bridge: 0000200ff9e00000-0000200ffddfffff [size=64M]"])
S2_00_1B_3 = ("00:1b.3", ["Memory behind bridge: 90000000-901fffff [size=2M]", "Prefetchable memory behind bridge: 0000200000000000-00002000001fffff [size=2M]"])
S2_00_1D_0 = ("00:1d.0", ["Memory behind bridge: 9c400000-9c7fffff [size=4M]", "Prefetchable memory behind bridge: 0000200ffde00000-0000200ffedfffff [size=16M]"])
S2_00_1D_6 = ("00:1d.6", ["Memory behind bridge: 9c000000-9c3fffff [size=4M]", "Prefetchable memory behind bridge: 0000200ffee00000-0000200fffdfffff [size=16M]"])
S2_16_04_0 = ("16:04.0", ["Memory behind bridge: a4800000-a87fffff [size=64M]", "Prefetchable memory behind bridge: 0000201fbff00000-0000201fffefffff [size=1G]"])
S2_30_02_0 = ("30:02.0", ["Memory behind bridge: adc00000-b1bfffff [size=64M]", "Prefetchable memory behind bridge: 0000202f7ff00000-0000202fbfefffff [size=1G]"])
S2_30_04_0 = ("30:04.0", ["Memory behind bridge: a9c00000-adbfffff [size=64M]", "Prefetchable memory behind bridge: 0000202fbff00000-0000202fffefffff [size=1G]"])
S2_4A_02_0 = ("4a:02.0", ["Memory behind bridge: bc400000-c03fffff [size=64M]", "Prefetchable memory behind bridge: 0000203f7ff00000-0000203fbfefffff [size=1G]"])
S2_4A_04_0 = ("4a:04.0", ["Memory behind bridge: b4400000-bc3fffff [size=128M]", "Prefetchable memory behind bridge: 0000203fbff00000-0000203fffefffff [size=1G]"])
# S2_57_00_0 = ("57:00.0", ["", ""]) No MEM Info
# S2_58_00_0 = ("58:00.0", ["", ""]) Not Exist
# S2_58_01_0 = ("58:01.0", ["", ""])
# S2_58_02_0 = ("58:02.0", ["", ""])
# S2_58_03_0 = ("58:03.0", ["", ""])
# S2_58_04_0 = ("58:04.0", ["", ""])
# S2_58_05_0 = ("58:05.0", ["", ""])
# S2_58_06_0 = ("58:06.0", ["", ""])
# S2_58_07_0 = ("58:07.0", ["", ""])
# S2_58_08_0 = ("58:08.0", ["", ""])
# S2_58_09_0 = ("58:09.0", ["", ""])
# S2_58_0A_0 = ("58:0a.0", ["", ""])
# S2_58_0B_0 = ("58:0b.0", ["", ""])
S2_74_02_0 = ("74:02.0", ["Memory behind bridge: c6800000-c87fffff [size=32M]", "Prefetchable memory behind bridge: 0000204fbe000000-0000204ffdffffff [size=1G]"])
S2_97_02_0 = ("97:02.0", ["Memory behind bridge: cac00000-cacfffff [size=1M]", "Prefetchable memory behind bridge: 0000206000000000-00002060001fffff [size=2M]"])
S2_98_00_0 = ("98:00.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_9F_02_0 = ("9f:02.0", ["Memory behind bridge: e1000000-e2ffffff [size=32M]", "Prefetchable memory behind bridge: 0000207f7ff00000-0000207fbfefffff [size=1G]"])
S2_9F_04_0 = ("9f:04.0", ["Memory behind bridge: dd000000-e0ffffff [size=64M]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fffefffff [size=1G]"])
# S2_AC_00_0 = ("ac:00.0", ["", ""]) Not Exist
# S2_AD_00_0 = ("ad:00.0", ["", ""]) Not Exist
S2_B3_02_0 = ("b3:02.0", ["Memory behind bridge: e5000000-e8ffffff [size=64M]", "Prefetchable memory behind bridge: 0000208fbff00000-0000208fffefffff [size=1G]"])
S2_C5_02_0 = ("c5:02.0", ["Memory behind bridge: f2400000-fa3fffff [size=128M]", "Prefetchable memory behind bridge: 0000209f7fc00000-0000209fbfbfffff [size=1G]"])
S2_C6_00_0 = ("c6:00.0", ["Memory behind bridge: f2400000-f33fffff [size=16M]", "Prefetchable memory behind bridge: 0000209f80000000-0000209f83ffffff [size=64M]"])
S2_C7_00_0 = ("c7:00.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_01_0 = ("c7:01.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_02_0 = ("c7:02.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_03_0 = ("c7:03.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_04_0 = ("c7:04.0", ["Memory behind bridge: f3000000-f33fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f83000000-0000209f83ffffff [size=16M]"])
S2_C7_05_0 = ("c7:05.0", ["Memory behind bridge: f2c00000-f2ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f82000000-0000209f82ffffff [size=16M]"])
S2_C7_06_0 = ("c7:06.0", ["Memory behind bridge: f2800000-f2bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f81000000-0000209f81ffffff [size=16M]"])
S2_C7_07_0 = ("c7:07.0", ["Memory behind bridge: f2400000-f27fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f80000000-0000209f80ffffff [size=16M]"])
S2_C7_08_0 = ("c7:08.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_09_0 = ("c7:09.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_0A_0 = ("c7:0a.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C7_0B_0 = ("c7:0b.0", ["Memory behind bridge: None", "Prefetchable memory behind bridge: None"])
S2_C5_04_0 = ("c5:04.0", ["Memory behind bridge: ea400000-f23fffff [size=128M]", "Prefetchable memory behind bridge: 0000209fbfc00000-0000209fffbfffff [size=1G]"])
# S2_DE_00_0 = ("de:00.0", ["", ""])
# S2_DF_00_0 = ("df:00.0", ["", ""])
# S2_DF_01_0 = ("df:01.0", ["", ""])
# S2_DF_02_0 = ("df:02.0", ["", ""])
# S2_DF_03_0 = ("df:03.0", ["", ""])
# S2_DF_04_0 = ("df:04.0", ["", ""])
# S2_DF_05_0 = ("df:05.0", ["", ""])
# S2_DF_06_0 = ("df:06.0", ["", ""])
# S2_DF_07_0 = ("df:07.0", ["", ""])
# S2_DF_08_0 = ("df:08.0", ["", ""])
# S2_DF_09_0 = ("df:09.0", ["", ""])
# S2_DF_0A_0 = ("df:0a.0", ["", ""])
# S2_DF_0B_0 = ("df:0b.0", ["", ""])

PCI_SAS_2P = [S2_00_1B_0, S2_00_1B_1, S2_00_1B_2, S2_00_1B_3, S2_00_1D_0, S2_00_1D_6, S2_16_04_0, S2_30_02_0, S2_30_04_0, S2_4A_02_0, S2_4A_04_0, S2_74_02_0,
              S2_97_02_0, S2_98_00_0, S2_9F_02_0, S2_9F_04_0, S2_B3_02_0, S2_C5_02_0, S2_C6_00_0, S2_C7_00_0, S2_C7_01_0, S2_C7_02_0, S2_C7_03_0, S2_C7_04_0,
              S2_C7_05_0, S2_C7_06_0, S2_C7_07_0, S2_C7_08_0, S2_C7_09_0, S2_C7_0A_0, S2_C7_0B_0, S2_C5_04_0]