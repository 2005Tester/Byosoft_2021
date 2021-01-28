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
BMC_IP = '192.168.2.102'
BMC_USER = 'Administrator'
BMC_PASSWORD = 'Admin@9001'
PORT = 22

# BIOS Auth Configuration
BIOS_USER = 'Admin@9001'
BIOS_PASSWORD = 'Admin@9000'

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
    F2 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x32), chr(0x7e)]
    F5 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x35), chr(0x7e)]
    F6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
    F9 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x30), chr(0x7e)]
    F10 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x31), chr(0x7e)]
    F11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
    F12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]


####################################################################################
#     Messages to identify a spcific boot option, page, menu or system status      #
####################################################################################
class Msg:
    HOTKEY_PROMPT_DEL = 'Press Del go to Setup Utility'
    HOTKEY_PROMPT_F11 = 'Press F11 go to BootManager'
    HOTKEY_PROMPT_F12 = 'Press F12 go to PXE boot'
    HOTKEY_PROMPT_F6 = 'Press F6 go to SP boot'

    PW_PROMPT = 'Enter Current Password'

    # Home screen with 6 icons
    HOME_PAGE = 'Continue'
    BIOS_BOOT_COMPLETE = 'BIOS boot completed'

    # pages in bios configuration
    PAGE_ADVANCED = 'CPU Configuration'
    PAGE_BMC = 'Additional System Information'
    PAGE_SECURITY = 'TPM Device'
    PAGE_BOOT = '<UEFI Boot Type>'
    PAGE_SAVE = 'Save Changes and Exit'

    # menus of CPU configuration
    CPU_CONFIG = 'CPU Configuration'
    PROCESSOR_CONFIG = 'Processor Configuration'
    UNCORE_CONFIG = 'Uncore Configuration'
    UNCORE_GENERAL = 'Uncore General Configuration'

    # menus of PCH configuration
    PCH_CONFIG = 'PCH CONFIGURATION'
    NETWORK_CONFIG = 'Network Configuration'

    # patch of setup menus
    PATH_UNCORE_GENERAL = [CPU_CONFIG, UNCORE_CONFIG, UNCORE_GENERAL]


##########################################
#     Pcie Resource Table for TC201      #
##########################################
# PCIE Resource for NVME2P board
ROOT_PORT_17 = ("00:1b.0", ["Memory behind bridge: 9e400000-a03fffff [size=32M]", "Prefetchable memory behind bridge: 0000200f7ae00000-0000200fbadfffff [size=1G]"])
ROOT_PORT_18 = ("00:1b.1", ["Memory behind bridge: 9c400000-9e3fffff [size=32M]", "Prefetchable memory behind bridge: 0000200fbae00000-0000200ffadfffff [size=1G]"])
ROOT_PORT_19 = ("00:1b.2", ["Memory behind bridge: 94000000-9bffffff [size=128M]", "Prefetchable memory behind bridge: 0000200ffae00000-0000200ffedfffff [size=64M]"])
ROOT_PORT_20 = ("00:1b.3", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: [disabled]"])
ROOT_PORT_13 = ("00:1d.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: [disabled]"])
ROOT_PORT_15 = ("00:1d.6", ["Memory behind bridge: 9c000000-9c3fffff [size=4M]", "Prefetchable memory behind bridge: 0000200ffee00000-0000200fffdfffff [size=16M]"])
DEV_16_04_0 = ("16:04.0", ["Memory behind bridge: a4800000-a87fffff [size=64M]", "Prefetchable memory behind bridge: 0000201fbff00000-0000201fffefffff [size=1G]"])
DEV_30_02_0 = ("30:02.0", ["Memory behind bridge: adc00000-b1bfffff [size=64M]", "Prefetchable memory behind bridge: 0000202f7ff00000-0000202fbfefffff [size=1G]"])
DEV_30_04_0 = ("30:04.0", ["Memory behind bridge: a9c00000-adbfffff [size=64M]", "Prefetchable memory behind bridge: 0000202fbff00000-0000202fffefffff [size=1G]"])
DEV_4A_02_0 = ("4a:02.0", ["Memory behind bridge: bc400000-c03fffff [size=64M]", "Prefetchable memory behind bridge: 0000203fbfc00000-0000203fffbfffff [size=1G]"])
DEV_4A_04_0 = ("4a:04.0", ["Memory behind bridge: b4400000-bc3fffff [size=128M]", "Prefetchable memory behind bridge: 0000203f7fc00000-0000203fbfbfffff [size=1G]"])
DEV_57_00_0 = ("57:00.0", ["Memory behind bridge: b4400000-b73fffff [size=48M]", "Prefetchable memory behind bridge: 0000203f80000000-0000203f8bffffff [size=192M]"])
DEV_58_00_0 = ("58:00.0", ["Memory behind bridge: b7000000-b73fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f8b000000-0000203f8bffffff [size=16M]"])
DEV_58_01_0 = ("58:01.0", ["Memory behind bridge: b6c00000-b6ffffff [size=4M]", "Prefetchable memory behind bridge: 0000203f8a000000-0000203f8affffff [size=16M]"])
DEV_58_02_0 = ("58:02.0", ["Memory behind bridge: b6800000-b6bfffff [size=4M]", "Prefetchable memory behind bridge: 0000203f89000000-0000203f89ffffff [size=16M]"])
DEV_58_03_0 = ("58:03.0", ["Memory behind bridge: b6400000-b67fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f88000000-0000203f88ffffff [size=16M]"])
DEV_58_04_0 = ("58:04.0", ["Memory behind bridge: b6000000-b63fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f87000000-0000203f87ffffff [size=16M]"])
DEV_58_05_0 = ("58:05.0", ["Memory behind bridge: b5c00000-b5ffffff [size=4M]", "Prefetchable memory behind bridge: 0000203f86000000-0000203f86ffffff [size=16M]"])
DEV_58_06_0 = ("58:06.0", ["Memory behind bridge: b5800000-b5bfffff [size=4M]", "Prefetchable memory behind bridge: 0000203f85000000-0000203f85ffffff [size=16M]"])
DEV_58_07_0 = ("58:07.0", ["Memory behind bridge: b5400000-b57fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f84000000-0000203f84ffffff [size=16M]"])
DEV_58_08_0 = ("58:08.0", ["Memory behind bridge: b5000000-b53fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f83000000-0000203f83ffffff [size=16M]"])
DEV_58_09_0 = ("58:09.0", ["Memory behind bridge: b4c00000-b4ffffff [size=4M]", "Prefetchable memory behind bridge: 0000203f82000000-0000203f82ffffff [size=16M]"])
DEV_58_0A_0 = ("58:0a.0", ["Memory behind bridge: b4800000-b4bfffff [size=4M]", "Prefetchable memory behind bridge: 0000203f81000000-0000203f81ffffff [size=16M]"])
DEV_58_0B_0 = ("58:0b.0", ["Memory behind bridge: b4400000-b47fffff [size=4M]", "Prefetchable memory behind bridge: 0000203f80000000-0000203f80ffffff [size=16M]"])
DEV_74_02_0 = ("74:02.0", ["Memory behind bridge: c6800000-c87fffff [size=32M]", "Prefetchable memory behind bridge: 0000204fbe000000-0000204ffdffffff [size=1G]"])
DEV_97_02_0 = ("97:02.0", ["Memory behind bridge: cac00000-cacfffff [size=1M]", "Prefetchable memory behind bridge: [disabled]"])
DEV_98_00_0 = ("98:00.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: [disabled]"])
DEV_9F_02_0 = ("9f:02.0", ["Memory behind bridge: df000000-e2ffffff [size=64M]", "Prefetchable memory behind bridge: 0000207f7ff00000-0000207fbfefffff [size=1G]"])
DEV_9F_04_0 = ("9f:04.0", ["Memory behind bridge: dd000000-deffffff [size=32M]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fffefffff [size=1G]"])
DEV_AC_00_0 = ("ac:00.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fc02fffff [size=4M]"])
DEV_AD_00_0 = ("ad:00.0", ["Memory behind bridge: [disabled]", "Prefetchable memory behind bridge: 0000207fbff00000-0000207fc02fffff [size=4M]"])
DEV_B3_02_0 = ("b3:02.0", ["Memory behind bridge: e5000000-e8ffffff [size=64M]", "Prefetchable memory behind bridge: 0000208fbff00000-0000208fffefffff [size=1G]"])
DEV_C5_02_0 = ("c5:02.0", ["Memory behind bridge: f2400000-fa3fffff [size=128M]", "Prefetchable memory behind bridge: 0000209f7fc00000-0000209fbfbfffff [size=1G]"])
DEV_C6_00_0 = ("c6:00.0", ["Memory behind bridge: f2400000-f53fffff [size=48M]", "Prefetchable memory behind bridge: 0000209f80000000-0000209f8bffffff [size=192M]"])
DEV_C7_00_0 = ("c7:00.0", ["Memory behind bridge: f5000000-f53fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f8b000000-0000209f8bffffff [size=16M]"])
DEV_C7_01_0 = ("c7:01.0", ["Memory behind bridge: f4c00000-f4ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f8a000000-0000209f8affffff [size=16M]"])
DEV_C7_02_0 = ("c7:02.0", ["Memory behind bridge: f4800000-f4bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f89000000-0000209f89ffffff [size=16M]"])
DEV_C7_03_0 = ("c7:03.0", ["Memory behind bridge: f4400000-f47fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f88000000-0000209f88ffffff [size=16M]"])
DEV_C7_04_0 = ("c7:04.0", ["Memory behind bridge: f4000000-f43fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f87000000-0000209f87ffffff [size=16M]"])
DEV_C7_05_0 = ("c7:05.0", ["Memory behind bridge: f3c00000-f3ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f86000000-0000209f86ffffff [size=16M]"])
DEV_C7_06_0 = ("c7:06.0", ["Memory behind bridge: f3800000-f3bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f85000000-0000209f85ffffff [size=16M]"])
DEV_C7_07_0 = ("c7:07.0", ["Memory behind bridge: f3400000-f37fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f84000000-0000209f84ffffff [size=16M]"])
DEV_C7_08_0 = ("c7:08.0", ["Memory behind bridge: f3000000-f33fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f83000000-0000209f83ffffff [size=16M]"])
DEV_C7_09_0 = ("c7:09.0", ["Memory behind bridge: f2c00000-f2ffffff [size=4M]", "Prefetchable memory behind bridge: 0000209f82000000-0000209f82ffffff [size=16M]"])
DEV_C7_0A_0 = ("c7:0a.0", ["Memory behind bridge: f2800000-f2bfffff [size=4M]", "Prefetchable memory behind bridge: 0000209f81000000-0000209f81ffffff [size=16M]"])
DEV_C7_0B_0 = ("c7:0b.0", ["Memory behind bridge: f2400000-f27fffff [size=4M]", "Prefetchable memory behind bridge: 0000209f80000000-0000209f80ffffff [size=16M]"])
DEV_C5_04_0 = ("c5:04.0", ["Memory behind bridge: ea400000-f23fffff [size=128M]", "Prefetchable memory behind bridge: 0000209fbfc00000-0000209fffbfffff [size=1G]"])
DEV_DE_00_0 = ("de:00.0", ["Memory behind bridge: ea400000-ed3fffff [size=48M]", "Prefetchable memory behind bridge: 0000209fc0000000-0000209fcbffffff [size=192M]"])
DEV_DF_00_0 = ("df:00.0", ["Memory behind bridge: ed000000-ed3fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fcb000000-0000209fcbffffff [size=16M]"])
DEV_DF_01_0 = ("df:01.0", ["Memory behind bridge: ecc00000-ecffffff [size=4M]", "Prefetchable memory behind bridge: 0000209fca000000-0000209fcaffffff [size=16M]"])
DEV_DF_02_0 = ("df:02.0", ["Memory behind bridge: ec800000-ecbfffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc9000000-0000209fc9ffffff [size=16M]"])
DEV_DF_03_0 = ("df:03.0", ["Memory behind bridge: ec400000-ec7fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc8000000-0000209fc8ffffff [size=16M]"])
DEV_DF_04_0 = ("df:04.0", ["Memory behind bridge: ec000000-ec3fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc7000000-0000209fc7ffffff [size=16M]"])
DEV_DF_05_0 = ("df:05.0", ["Memory behind bridge: ebc00000-ebffffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc6000000-0000209fc6ffffff [size=16M]"])
DEV_DF_06_0 = ("df:06.0", ["Memory behind bridge: eb800000-ebbfffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc5000000-0000209fc5ffffff [size=16M]"])
DEV_DF_07_0 = ("df:07.0", ["Memory behind bridge: eb400000-eb7fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc4000000-0000209fc4ffffff [size=16M]"])
DEV_DF_08_0 = ("df:08.0", ["Memory behind bridge: eb000000-eb3fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc3000000-0000209fc3ffffff [size=16M]"])
DEV_DF_09_0 = ("df:09.0", ["Memory behind bridge: eac00000-eaffffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc2000000-0000209fc2ffffff [size=16M]"])
DEV_DF_0A_0 = ("df:0a.0", ["Memory behind bridge: ea800000-eabfffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc1000000-0000209fc1ffffff [size=16M]"])
DEV_DF_0B_0 = ("df:0b.0", ["Memory behind bridge: ea400000-ea7fffff [size=4M]", "Prefetchable memory behind bridge: 0000209fc0000000-0000209fc0ffffff [size=16M]"])

PCI_NVME_2P = [ROOT_PORT_17, ROOT_PORT_18, ROOT_PORT_19, ROOT_PORT_20, ROOT_PORT_13, ROOT_PORT_15,
               DEV_16_04_0, DEV_30_02_0, DEV_30_04_0, DEV_4A_02_0, DEV_4A_04_0, DEV_57_00_0,
               DEV_58_00_0, DEV_58_01_0, DEV_58_02_0, DEV_58_03_0, DEV_58_04_0, DEV_58_05_0,
               DEV_58_06_0, DEV_58_07_0, DEV_58_08_0, DEV_58_09_0, DEV_58_0A_0, DEV_58_0B_0,
               DEV_74_02_0, DEV_97_02_0, DEV_98_00_0, DEV_9F_02_0, DEV_9F_04_0, DEV_AC_00_0,
               DEV_AD_00_0, DEV_B3_02_0, DEV_C5_02_0, DEV_C6_00_0, DEV_C7_00_0, DEV_C7_01_0,
               DEV_C7_02_0, DEV_C7_03_0, DEV_C7_04_0, DEV_C7_05_0, DEV_C7_06_0, DEV_C7_07_0,
               DEV_C7_08_0, DEV_C7_09_0, DEV_C7_0A_0, DEV_C7_0B_0, DEV_C5_04_0, DEV_DE_00_0,
               DEV_DF_00_0, DEV_DF_01_0, DEV_DF_02_0, DEV_DF_03_0, DEV_DF_04_0, DEV_DF_05_0,
               DEV_DF_06_0, DEV_DF_07_0, DEV_DF_08_0, DEV_DF_09_0, DEV_DF_0A_0, DEV_DF_0B_0]




# pat
pat = '[(\d+);\d+H[\w\s\d<>\[\]&-]'

# unitool, chipsec path
unitool_path = r'/root/flashtool/Linux_17.10/'
chipsc_path = r'/home/byo/chipsec_merge/'

# defined the msg info
press_f2 = 'Press F2'
msg5 = 'USB Mouse\s+1'
msg6 = 'USB Keyboard\s+1'
msg7 = 'USB Mass Storage\s+0'
pwd_info = 'The current password is the default password.Please update password!'
default_pwd = 'Admin@9001'

# BIOS Setup options,
# level 1
PXE_option = 'UEFI HTTPSv4: Network - Port00 SLOT1'
option = 'PCH Configuration'
option2 = 'CPU Configuration'
OS = 'P0-ubuntu - HDD 0'
# SUSE = 'P0-SUSE Linux Enterprise - HDD 0'
SUSE = 'SUSE Linux Enterprise\(LUN0\)'
pwd_item = 'Manage Supervisor Password'
pwd_item1 = 'Simple Password'

# level 2

VIRTUALIZATION_CONFIG = 'Virtualization Configuration'

# level 3
option4 = 'Per-CPU Information'
option11 = 'Memory Power & Thermal Configuration'
option12 = 'Uncore General Configuration'

# level 4
option14 = 'Uncore Status'

# BIOS items info,
static_turbo = ['<Disabled>\s+Static Turbo']
ufs = ['<Enabled>\s+UFS']
local_remote = ['Local/Remote Threshold\s+<Auto>']
dram = ['<Enabled>\s+DRAM RAPL']
simplePWD_info = ['<Disabled>\s+Simple Password']
secure_status = ['Current Secure Boot State\s+Disabled']
cnd_status = ['<Enabled>\s+Network CDN']

# TPM info
tpm_info = ['TPM Device\s+TPM 2.0', 'TPM2 Active PCR Hash\s+Algorithm+\s+SHA1\, SHA256',
            'TPM2 Hardware Supported Hash\s+Algorithm+\s+SHA1\, SHA256']

# UPI Status
upi_state = ['Current UPI Link Speed\s+Fast', 'Current UPI Link Frequency\s+11\.2\s+GT\/s']

# CPU, DIMM info
CPU_info = ['Processor ID\s+000606A6', 'Processor Frequency\s+2.000GHz']
DIMM_info = ['DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM', 
             'DIMM160\(G\)\s+S1.CG.D0:2933MT/s Hynix DRx4 32GB RDIMM']

# Common key order
key2default = [Key.F9, Key.Y, Key.F10, Key.Y]
key2Setup = [Key.RIGHT, Key.RIGHT, Key.DOWN, Key.ENTER]
key2OS = [Key.RIGHT, Key.ENTER]
key2pwd = [Key.RIGHT, Key.RIGHT, Key.RIGHT]
key2type = [Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.RIGHT]

# WA
w2key = [Key.RIGHT, Key.UP]

new_pwd_9 = 'Admin@9002'
new_pwd_8 = 'Admin@9!'
new_pwd_16 = 'Admin@9001Admin@90'
new_pwd_17 = 'Admin@9001Admin@900'
simple_pwd = '11111111'
weak_pwd = 'Huawei@CLOUD8!'
# 新密码为2种字符类型，尝试各种组合（共6种组合）
pwd_list1 = ['ADMIN123', 'admin123', 'admin###', 'ADMIN###', 'ADMINadm', '1234####']
# System will be locked after send wrong pwd 3 times
# 新密码为3种字符类型，尝试各种组合（共4种组合）
pwd_list2 = ['Administrator@', 'admin@123', 'Administrator1', 'ADMIN@123']
# common error msg
pwd_info_1 = 'Please type in your password'
pwd_info_2 = 'Please type in your new password'
pwd_info_3 = 'Please confirm your new password'
pwd_info_4 = 'Changes have been saved after press'
invalid_info = 'Invalid Password'
error_info = 'Enter incorrect password 3 times,System Locked'
enable_simple_pwd = 'Enabling simple password poses security risks'
simple_pwd_warning = 'The password fails the dictionary check - it is too simplistic/systematic'