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
PROJECT_NAME = "2288V6"
SUT_CONFIG = "SUT1-Full-DIMM"
REPORT_TEMPLATE = "ICX2P\\Report\\template"

# Environment settings
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_DIR = 'c:\\daily\\ICX2P\\{0}'.format(timestamp)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
SMBIOS_DIR = 'c:\\daily\\SMBIOS'
# if not os.path.exists(SMBIOS_DIR):
#     os.makedirs(SMBIOS_DIR)
SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')

HPM_DIR = ''
INI_DIR = ''
SHAR_DIR = '\\\\byodiskstation1\\PublicRW\\QA\\AT Report\\2288V6\\{0}'.format(timestamp)

# Serial Port Configuration
BIOS_SERIAL = "com3"

# BMC Configuration
BMC_IP = '192.168.2.102'
BMC_USER = 'Administrator'
BMC_PASSWORD = 'Admin@9001'
PORT = 22

# BIOS Configuration
BIOS_USER = 'Admin@9001'
BIOS_PASSWORD = 'Admin@9000'

# OS Configuration
OS_IP = '192.168.3.200'
OS_USER = 'root'
OS_PASSWORD = '1'


# Tool definition
UNI_PATH = "/root/flashtool/unitool"


# BIOS Firmware Directory, Must manual copy image files to the directory before test
BIOS_PATH = r"\\ByoDiskStation1\PublicRW\QA\Firmware\2288V6\BIOS"

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
    RESET_DEFAULT = [F9, Y, F10, Y]


# Messages to identify a spcific boot option, page, menu or system status 
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
    PAGE_BOOT = '<[UEFILegacy]{4,6}Boot>'
    PAGE_SAVE = 'Save Changes and Exit'

    # menus of CPU configuration
    CPU_CONFIG = 'CPU Configuration'
    PROCESSOR_CONFIG = 'Processor Configuration'
    UNCORE_CONFIG = 'Uncore Configuration'
    UNCORE_GENERAL = 'Uncore General Configuration'

    # menus of PCH configuration
    PCH_CONFIG = 'PCH CONFIGURATION'
    NETWORK_CONFIG = 'Network Configuration'

    # path of setup menus
    PATH_UNCORE_GENERAL = [CPU_CONFIG, UNCORE_CONFIG, UNCORE_GENERAL]

    # Menu in Boot page
    MENU_BOOT_ORDER = 'UEFI Boot'
    MENU_HDD_BOOT = 'HDD Device'
    BOOT_OPTION_SUSE = ["SUSE Linux Enterprise\(LUN0\)"]

    # Firmware version info
    ME_VERSION = '0F:4.4.4.53'


# BIOS configuration to be set by unitool
class BiosCfg:
    MFG_RMT = {
        "EquipMentModeFlag": 1,
        "EnableBiosSsaRMT": 1,
        "EnableBiosSsaRMTonFCB": 1,
        "serialDebugMsgLvl": 2
    }

    EQUIP_FLAG = {
        "EquipmentModeFlag": 1
    }

    # HPM Upgrade/Downgrade keep BIOS Setting unchanged setting
    HPM_KEEP = {
        "UsbBoot": 0,
        "WakeOnLanSupport": 1,
        "AcpiApicPolicy": 0,
        "FDMSupport": 0,
        "SataPort": 0,
        "sSataPort": 0,
        "PerformanceTuningMode": 0,
        "VTdSupport": 0,
        "DFXEnable": 1,
        "ActiveCpuCores": 4,
        "ProcessorHyperThreadingDisable": 1,
        "UFSDisable": 1,
        "ProcessorEistEnable": 0,
        "C6Enable": 1,
        "IrqThreshold": 0,
        "EnableBiosSsaRMT": 1,
        "pprType": 0,
        "SvrMngmntFrb2Enable": 1,
    }

# pat
pat = '[(\d+);\d+H[\w\s\d<>\[\]&-]'



# defined the msg info
press_f2 = 'Press F2'
msg5 = 'USB Mouse\s+1'
msg6 = 'USB Keyboard\s+1'
msg7 = 'USB Mass Storage\s+0'
pwd_info = 'The current password is the default password.Please update password!'
default_pwd = 'Admin@9000'

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
option3 = 'Processor Configuration'
option5 = 'Memory Topology'
option1 = 'USB Configuration'
option6 = 'Advanced Power Mgmt. Configuration'
option7 = 'Miscellaneous Configuration'
option8 = 'CPU P State Control'
option9 = 'Uncore Configuration'
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
dram = ['<Enabled>\s+DRAM RAPL']
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
key2Setup = [Key.RIGHT, Key.RIGHT, Key.DOWN, Key.ENTER]
key2OS = [Key.RIGHT, Key.ENTER]
key2pwd = [Key.RIGHT, Key.RIGHT, Key.RIGHT]

# WA
w2key = [Key.RIGHT, Key.UP]

