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

# Report Setting
REPORT_TEMPLATE = r"{0}\Report\template_HY5".format(os.getcwd())

# Environment settings
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_DIR = 'c:\\daily\\HY5\\{0}'.format(timestamp)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
SMBIOS_DIR = 'c:\\daily\\SMBIOS'
# if not os.path.exists(SMBIOS_DIR):   # if run SMBIOS related test cases, this line should not be annotated,
#     os.makedirs(SMBIOS_DIR)
SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')
BINARY_DIR = '\\\\172.16.0.73\\HY5_Binary'
HPM_DIR = '\\\\byodiskstation1\\PublicRW\\QA\\HY5 HPM'
INI_DIR = '\\\\byodiskstation1\\PublicRW\\QA\\AT Tools'
SHAR_DIR = '\\\\byodiskstation1\\PublicRW\\QA\\AT Report\\Haiyan5\\{0}'.format(timestamp)
# if not os.path.exists(SHAR_DIR):
#     os.makedirs(SHAR_DIR)

# Serial Port Configuration
BIOS_SERIAL = "com3"

# BMC Configuration
BMC_IP = '192.168.2.100'
BMC_USER = 'Administrator'
BMC_PASSWORD = 'Admin@9000'
PORT = 22

# BIOS Configuration
BIOS_USER = 'Admin@9000'
BIOS_PASSWORD = 'Admin@9000'

# OS Configuration
OS_IP = '192.168.100.91'
OS_USER = 'root'
OS_PASSWORD = 'byosoft@123'


# Key mapping
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

# pat
pat = '[(\d+);\d+H[\w\s\d<>\[\]&-]'

# unitool, chipsec path
unitool_path = r'/root/flashtool/Linux_17.10/'
chipsc_path = r'/home/byo/chipsec_merge/'

# defined the msg info
msg = 'Press Del go to Setup Utility'
press_f2 = 'Press F2'
msg1 = 'Press F11 go to BootManager'
msg2 = 'Press F12 go to PXE boot'
msg3 = 'Press F6 go to SP boot'
msg4 = 'BIOS Configuration'
msg5 = 'USB Mouse\s+1'
msg6 = 'USB Keyboard\s+1'
msg7 = 'USB Mass Storage\s+2'
pwd_info = 'The current password is the default password.Please update password!'
default_pwd = 'Admin@9000'

# BIOS Setup options,
# level 1
PXE_option = 'UEFI HTTPSv4: Network - Port00 SLOT1'
option = 'PCH Configuration'
option2 = 'CPU Configuration'
OS = 'P0-ubuntu - HDD 0'
SUSE = 'P0-SUSE Linux Enterprise - HDD 0'
pwd_item = 'Manage Supervisor Password'
pwd_item1 = 'Simple Password'

# level 2
option3 = 'Processor Configuration'
option5 = 'Memory Topology'
option1 = 'USB Configuration'
option6 = 'Advanced Power Mgmt. Configuration'
option7 = 'Miscellaneous Configuration'
option8 = 'CPU P State Control'
option9 = 'Uncore Configuration'
option10 = 'Virtualization Configuration'

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
upi_state = ['Current UPI Link Speed\s+Fast', 'Current UPI Link Frequency\s+10\.4\s+GT\/s']

# CPU, DIMM info
CPU_info = ['Processor ID\s+0005065B', 'Processor Frequency\s+2.500GHz', 'Microcode Revision\s+0700001F']
DIMM_info = ['DIMM000\s+S0.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM', 'DIMM100\s+S1.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM']

# set by arthur, a common key order
key2default = [Key.F9, Key.Y, Key.F10, Key.Y]
key2Setup = [Key.RIGHT, Key.RIGHT, Key.DOWN, Key.ENTER]
key2OS = [Key.RIGHT, Key.ENTER, Key.UP]
key2pwd = [Key.RIGHT, Key.RIGHT, Key.RIGHT]
key2TPM = [Key.RIGHT, Key.RIGHT, Key.RIGHT, Key.RIGHT]

new_pwd_9 = 'Admin@9001'
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