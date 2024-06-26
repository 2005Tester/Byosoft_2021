#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
from HY5.Config import SutConfig

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
    DISCARD_CHANGES = ['N']
    RESET_DEFAULT = [F9, Y, F10, Y]
    SAVE_RESET = [F10, Y]
    ENTER_SAVE_RESET = [ENTER, Y, F10, Y]


# OS Boot Option Keywords
class BootOS:
    name_ruler = r"RAID CARD|HDD\s*\d+|NVME\s*\d+|SLOT\s*\d+"
    SLES = f"SUSE Linux Enterprise.*?(?:{name_ruler})"
    Ubuntu = f"ubuntu.*?(?:{name_ruler})"
    CentOS = f"CentOS Linux.*?(?:{name_ruler})"
    Windows = f"Windows Boot Manager.*?(?:{name_ruler})"
    VMware = f"VMware ESXi.*?(?:{name_ruler})"


# Messages to identify a specific boot option, page, menu or system status
class Msg:
    BIOS_PW_DEFAULT = "Admin@9000"
    BIOS_PASSWORD = 'Admin@9009'

    HOTKEY_PROMPT_DEL = 'Press Del go to Setup Utility'
    HOTKEY_PROMPT_F11 = 'Press F11 go to BootManager'
    HOTKEY_PROMPT_F12 = 'Press F12 go to PXE boot'
    HOTKEY_PROMPT_F6 = 'Press F6 go to SP boot'

    PW_PROMPT = 'Enter Current Password'
    PW_UPATE_PROMPT = 'The current password is the default password.Please update password!'

    # Home screen with 6 icons
    HOME_PAGE = '/Continue/'
    SECURE_BOOT = 'Administer Secure Boot'
    BIOS_BOOT_COMPLETE = 'BIOS boot completed'

    # pages in bios configuration
    PAGE_INFO = "BIOS Revision"
    PAGE_ADVANCED = 'CPU Configuration'
    PAGE_BMC = 'iBMC version'
    PAGE_SECURITY = 'TPM Device'
    PAGE_BOOT = '<UEFI Boot>'
    PAGE_SAVE = 'Save Changes and Exit'

    # menus of CPU configuration
    CPU_CONFIG = 'CPU Configuration'
    COMMON_REF_CONFIG = 'Common RefCode Configuration'
    PROCESSOR_CONFIG = 'Processor Configuration'
    UNCORE_CONFIG = 'Uncore Configuration'
    UNCORE_GENERAL = 'Uncore General Configuration'
    MEMORY_CONFIG = 'Memory Configuration'
    MEMORY_TOP = 'Memory Topology'
    MEMORY_RAS_CFG = "Memory RAS Configuration"
    ADV_POWER_MGF_CONFIG = 'Advanced Power Mgmt. Configuration'
    MEM_FRE = 'Memory Frequency'
    MEM2X_REFRESH = 'Refresh Options'
    PFM_PRO = 'Performance Profile'
    CPU_P_STATE = 'CPU P State Control'
    CPU_C_STATE = 'CPU C State Control'
    PKG_C_STATE_CONTROL = 'Package C State Control'
    PER_CPU = 'Per-CPU Information'
    MEM_POWER_THER_CONFIG = 'Memory Power & Thermal Configuration'
    DRAM_RAPL_CONFIG = 'DRAM RAPL Configuration'
    MEM_POWER_ADV = 'Memory Power Savings Advanced Options'
    CKE = 'CKE Power Down'
    APD = 'APD'
    PPD = 'PPD'
    LPASR_MODE = 'LPASR Mode'
    CKE_FEATURE = 'CKE Feature'
    CKE_IDLE_TIMER = 'CKE Idle Timer'
    UNCORE_STATUS = 'Uncore Status'
    ACT_CPU_CORES = 'Active Processor Cores'
    IIO_CONFIG = "IIO Configuration"
    NUMA = "NUMA"
    ASPM_ROOT_PORT = "PCIe ASPM Support"
    EXTENDED_APIC = "Extended APIC"
    SYS_EVENT_LOG = "System Event Log"
    SPD_CRC = "SPD CRC Check"
    ATTEMPT_FAST_BOOT = "Attempt Fast Boot"
    IBMC_WDT_CONFIGURATION = 'iBMC WDT Configuration'

    # menus of PCH configuration
    PCH_CONFIG = 'PCH Configuration'
    NETWORK_CONFIG = 'Network Configuration'
    USB_CONFIG = 'USB Configuration'

    # Console Configuration Menu
    Console_CONFIG = 'Console Redirection Configuration'
    Console_REDIR = 'Console Redirection'
    SPCR = 'SPCR'
    BAUD_RATE = 'Baud Rate'

    # Misc Configuration Menu
    MISC_CONFIG = 'Miscellaneous Configuration'
    CDN = 'Network CDN'
    ASPM_GLOBAL = r"PCIe ASPM Support \(Global\)"

    # menus of Password configuration
    MGT_SPV_PWD = 'Manage Supervisor Password'
    SP_PWD = 'Simple Password'

    # Menus of Virtualization Configuration page
    VIRTUAL_CFG = "Virtualization Configuration"
    VIRTUAL_VTD = "Intel\(R\) VT for Directed I/O \(VT-d\)"
    SRIOV_GLOBAL = "PCIe SR-IOV"
    SRIOV_IIO = r"CPU (\d) Port (DMI|[0-4][A-D]) SR-IOV Support"

    # path of setup menus
    PATH_UNCORE_GENERAL = [CPU_CONFIG, UNCORE_CONFIG, UNCORE_GENERAL]
    PATH_UNCORE_STATUS = [CPU_CONFIG, UNCORE_CONFIG, UNCORE_GENERAL, UNCORE_STATUS]
    PATH_DRAM_RAPL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, MEM_POWER_THER_CONFIG, DRAM_RAPL_CONFIG]
    PATH_PSTATE_CTL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, CPU_P_STATE]
    PATH_USB_CFG = [PCH_CONFIG, USB_CONFIG]
    PATH_ADV_PM_CFG = [CPU_CONFIG, ADV_POWER_MGF_CONFIG]
    PATH_PER_CPU_INFO = [CPU_CONFIG, PROCESSOR_CONFIG, PER_CPU]
    PATH_PRO_CFG = [CPU_CONFIG, PROCESSOR_CONFIG]
    PATH_PRO_COMM = [CPU_CONFIG, COMMON_REF_CONFIG]
    PATH_IIO_CONFIG = [CPU_CONFIG, IIO_CONFIG]
    PATH_MEM_CONFIG = [CPU_CONFIG, MEMORY_CONFIG]
    PATH_MEM_POWER_ADV = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, MEM_POWER_THER_CONFIG, MEM_POWER_ADV]
    PATH_MISC_CONFIG = [MISC_CONFIG]
    PATH_CSTATE_CTL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, CPU_C_STATE]
    PATH_PCSC_CTL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, PKG_C_STATE_CONTROL]
    PATH_VIRTUAL_VTD = [VIRTUAL_CFG, VIRTUAL_VTD]
    PATH_WDT_CONFIG = [PAGE_BMC, IBMC_WDT_CONFIGURATION]

    # Menu in Boot page
    MENU_BOOT_ORDER = 'UEFI Boot'
    MENU_HDD_BOOT = 'HDD Device'
    BOOT_OPTION_SUSE = [BootOS.SLES]
    BOOT_OPTION_OS = [BootOS.SLES]
    PXE_OPT = 'UEFI HTTPSv4: Network - Port00 SLOT1'
    UBUNTU = BootOS.Ubuntu
    SUSE_GRUB = 'Welcome to GRUB'
    PXE_BOOT_CAPABILITY = 'PXE Boot Capability'
    BOOT_TYPE = 'Boot Type'
    BOOT_OPTIONS = 'Boot Options'

    # Menus in Exit
    SAVE_WO_RESET = "Save Changes Without Exiting"
    LOAD_CUSTOM_DEFAULT = ['Load Custom Defaults']



    # Firmware version info
    ME_VERSION = '0F:4.4.4.35'
    RC_VERSION = '0F:4.4.4.35'
    BIOS_REVISION = '0.80'
    BIOS_DATE = '07/16/2021'
    iBMC_VERSION = '3.01.16.02'
    CPU_TYPE = 'Cooper Lake'
    TOTAL_MEMORY = '{0}MB'.format(SutConfig.SysCfg.DIMM_SIZE * 1024)

    # POST GPIO ERROR Keywords print in serial log
    GPIO_ERR = "GPIO ERROR"

    # Release Branch Name
    RELEASE_BRANCH = "HY5_{}"

    # show logo flag
    LOGO_SHOW = "BootType :"

    # 精简打印，华为要求 LogTime_check_list
    LogTime_common = [
    'BootType',
    'RC Version',
    'BIOS Revision',
    'BIOS Date',
    'iBMC Version',
    'R_PCH_TCO2_STS = 0x0',
    'The Box has NOT been opened.',
    'EFI1711 V1.00.05',
    'Press Del go to Setup Utility',
    'Press F11 go to BootManager',
    'Press F12 go to PXE boot',
    'Press F6 go to SP boot',
    'BGRT BmpToGop Unsupported',
    'BIOS boot completed.']

# BIOS configuration to be set by unitool
class BiosCfg:

    ActiveCpuCores_Default = {'ActiveCpuCores': 0}

    ActiveCpuCores_aft = {"ActiveCpuCores": 20}

    MFG_RMT = {
        "EquipMentModeFlag": 1,
        "EnableBiosSsaRMT": 1,
        "EnableBiosSsaRMTonFCB": 1,
        "serialDebugMsgLvl": 2
    }

    EQUIP_FLAG = {
        "EquipMentModeFlag": 1
    }
    
    XMPMODE = {
        "XMPMode": 0
    }

    # HPM Upgrade/Downgrade keep BIOS Setting unchanged setting
    HPM_KEEP = {
        "UsbBoot": 0,
        "WakeOnPME": 1,
        "AcpiApicPolicy": 0,
        "FDMSupport": 0,
        "SataPort": 0,
        "sSataPort": 0,
        "PerformanceTuningMode": 0,
        "VTdSupport": 0,
        "ADDDCEn": 1,
        "ActiveCpuCores": 4,
        "ProcessorHyperThreadingDisable": 1,
        "UFSDisable": 1,
        "ProcessorEistEnable": 0,
        "C6Enable": 1,
        "IrqThreshold": 0,
        "EnableBiosSsaRMT": 1,
        "pprType": 0,
        "BMCWDTEnable": 1,
    }

    Spread_Spectrum_bef = {
        "EnableClockSpreadSpec": 0
    }

    Spread_Spectrum_aft = {
        "EnableClockSpreadSpec": 1
    }