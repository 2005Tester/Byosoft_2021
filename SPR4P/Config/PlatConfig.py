#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
from SPR4P.Config import SutConfig


# Key mapping
class Key:
    ENTER = '\x0d'
    DEL = '\x7f'
    ESC = '\x1b '
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    RIGHT = '\x1b[C'
    LEFT = '\x1b[D'
    F2 = '\x1b[12~'
    F5 = '\x1b[15~'
    F6 = '\x1b[17~'
    F9 = '\x1b[20~'
    F10 = '\x1b[21~'
    F11 = '\x1b[23~'
    F12 = '\x1b[24~'
    CTRL_ALT_DELETE = '\x1bR\x1br\x1bR'
    Y = 'Y'
    F = "F"
    C = "C"
    DISCARD_CHANGES = 'N'
    RESET_DEFAULT = [F9, F, F10, Y]
    SAVE_RESET = [F10, Y]
    ENTER_SAVE_RESET = [ENTER, Y, F10, Y]


# OS Boot Option Keywords
class BootOS:
    SLES = ".*SUSE Linux Enterprise.*"
    SLED = ".*sled-secureboot.*"
    UBUNTU = ".*ubuntu.*"
    CENTOS = ".*CentOS Linux.*"
    WINDOWS = ".*Windows Boot Manager.*"
    VMWARE = ".*VMware ESXi.*"
    RHEL = ".*Red Hat Enterprise Linux.*"


class Attr:
    """BIOS Setup Attributes Names Define"""
    RRQ = "RrqThreshold"
    IRQ = "ObsoleteIrqThreshold"
    RRQ_THLD_V = "RrqThresholdvalue"
    DRAM_RAPL = "DramRaplPwrLimitLockCsr"
    ACPI_APIC = "AcpiApicReport"
    CPU_CORES = "ActiveCpuCores"
    BOOT_OVERRITE = 'BootOverride'
    BOOT_FAIL_POLICY = 'BootFailPolicy'
    SIMPLE_PW = "Authority"
    EQUIP_FLAG = "EquipMentModeFlag"
    RMT = "EnableRMT"
    SYS_DBG_LEVEL = "SysDbgLevel"
    MEM_DBG_LEVEL = "serialDebugMsgLvl"
    RAS_LOG_LEVEL = "RasLogLevel"
    ADDDC_EN = "ADDDCEn"
    PPR_TYPE = "pprType"
    USB_BOOT = "UsbBoot"
    CDN = "CdnSupport"
    FDM = "FDMSupport"
    CR_POST = "CRAfterPost"
    KTI_L0P = "KtiLinkL0pEn"
    SYS_ERR_EN = "SystemErrorEn"
    WHEA_EN = "WheaSupportEn"
    EIST = "ProcessorEistEnable"
    HT_EN = "ProcessorHyperThreadingDisable"
    C6 = "C6Enable"
    WDT_POST = "POSTBootWDTimerTimeout"
    BOOT_TYPE = "UefiOptimizedBootToggle"
    PXE_EN = "SlotPxeEnable"
    HW_PREFETCHER = "MlcStreamerPrefetcherEnable"

    # BMC配置相关
    BMC_WDT_POST = "SvrMngmntFrb2Enable"
    BMC_WDT_OS = "OSBootWDTimer"
    BMC_IP = "BMCIPVMode"
    BMC_IPV4 = "NicIpv4.Source"
    BMC_IPV6 = "NicIpv6.Source"
    BMC_2FACTOR = "Twofactors"
    BMC_THERMAl = "ThermalPolicy"
    BMC_FAN_SPEED = "FanSpeed[0]"
    BMC_SSH = "BMCSSH"
    BMC_POWER = "PowerRestorePolicy"
    BMC_NET_MODE = "NetworkMode"
    BMC_VLAN = "BMCVlan"
    BMC_NCSI = "NcsiPciePortSelect"


# Messages to identify a specific boot option, page, menu or system status
class Msg:
    # Password
    BIOS_PW_DEFAULT = "Admin@9000"
    BIOS_PASSWORD = 'Admin@9999'

    # Hotkey Flag
    HOTKEY_SHOW = "ME Version"
    HOTKEY_PROMPT_DEL = 'Press Del go to Front Page'
    HOTKEY_PROMPT_F11 = 'Press F11 go to Boot Manager'
    HOTKEY_PROMPT_F12 = 'Press F12 go to PXE boot'
    HOTKEY_PROMPT_F6 = 'Press F6 go to SP boot'

    # Hotkey Pressed
    F6_PRESSED = 'F6 is pressed, go to SP boot.'
    F12_PRESSED = 'F12 is pressed, go to PXE boot.'
    F11_PRESSED = 'F11 is pressed, go to Boot Manager.'
    DEL_PRESSED = 'Del is pressed, go to Front Page'

    # Hotkey Confirm
    DEL_CONFIRM = "Enter Current Password"
    F11_CONFIRM = "Boot Manager Menu"
    F12_CONFIRM = "Booting EFI Network for IPv4"
    F6_CONFIRM_UEFI = "SmmInstallProtocolInterface: 296EB418"
    F6_CONFIRM_LEGACY = "SYSLINUX.*EDD"

    # Serial Prompt Message
    PW_PROMPT = 'Enter Current Password'
    PW_ENTER_NEW = 'Enter New Password'
    PRESS_ENTER_PROMPT = 'Press <Enter> to continue'
    BIOS_BOOT_COMPLETE = 'BIOS Startup is completed'
    RMT_START = "START_RMT_N\d"
    RMT_END = "Lane Margin"
    POST_START = "BIOS Log @"
    CPU_RSC_ALLOC = "CPU Resource Allocation"
    START_DIMM = "START_SOCKET_\d_DIMMINFO_TABLE"
    LOAD_DEFAULT_PROMPT = "Load default configuration"
    SAVE_EXIT_PROMPT = "Save configuration changes"
    START_LEGACY_BOOT = "Start of legacy boot"
    SECURE_RESTORE_PROMPT = "Press 'Y' to Restore Secure Boot"
    KEYBOARD_SWAP = "Press F2"

    # Front Page
    HOME_PAGE = '/ Continue /'  # serial full debug message contains keyword "Continue"
    BOOT_MANAGER = 'Boot Manager'
    SECURE_BOOT = 'Administer Secure Boot'
    SETUP_ICON = "(Setup|BIOS) Utility"

    # Setup Page Flag
    PAGE_INFO = "BIOS Version"
    PAGE_ADVANCED = 'Platform Information'
    PAGE_SECURITY = 'TPM Device'
    PAGE_BOOT = 'Boot Type'
    PAGE_SAVE = 'Save Changes & Exit'

    # Main Page Information
    SYS_MEM_SPEED = "System Memory Speed"

    # Advanced
    VIDEO_CONFIG = "Video Configuration"
    CPU_CONFIG = 'Socket Configuration'
    BMC_CONFIG = 'BMC Configuration'
    ME_CONFIG = 'ME Configuration'
    SYS_EVENT_LOG = "System Event Log"
    PCH_CONFIG = 'PCH-IO Configuration'
    CONSOLE_CONFIG = 'Console Redirection Configuration'
    MISC_CONFIG = 'Misc Configuration'
    PERI_CONFIG = 'Peripheral Configuration'
    PXE_CONFIG = 'PXE Configuration'

    # Video Configuration
    DISPLAY_MODE = "Display Mode"

    # Socket Configuration
    PROCESSOR_CONFIG = 'Processor Configuration'
    COMMON_REF_CONFIG = 'Common RefCode Configuration'
    UNCORE_CONFIG = 'Uncore Configuration'
    MEMORY_CONFIG = 'Memory Configuration'
    IIO_CONFIG = "IIO Configuration"
    ADV_POWER_MGF_CONFIG = 'Advanced Power Management Configuration'
    PCIE_PORT_MAX_PAYLOAD_SIZE = 'PCIe Port Max Payload Size'

    # Processor Configuration
    PROC_INFO = "Processor Information"
    EN_LP = "Enable LP \[Global\]"
    APIC_REPORT_CFG = "APIC number in MADT"
    EXTENDED_APIC = "Extended APIC"
    ACT_CPU_CORES = 'Active Processor Cores'
    HW_PREFETCHER = "Hardware Prefetcher"

    # Processor Information
    MICRO_CODE = 'Microcode Revision'

    # Uncore Configuration
    UNCORE_GENERAL = 'Uncore General Configuration'
    MMIO_HIGHT_BASE = "MMIO High Base"
    MMIO_HIGHT_SIZE = "MMIO High Granularity Size"
    RRQ_THLD = "Rrq Count Threshold"
    UPI_L0P_EN = "Link L0p Enable"

    # Uncore General Configuration
    UNCORE_STATUS = 'Uncore Status'
    MMIOH_BASE = "MMIO High Base"
    MMIOH_SIZE = "MMIO High Granularity Size"

    # Memory Configuration
    MEM_TOP = 'Memory Topology'
    MEM_RAS_CFG = "Memory RAS Configuration"
    MEM_FREQ = 'Memory Frequency'
    MEM_REFRESH = 'Refresh Options'
    MEM_TURBO = "Memory Turbo"
    SPD_CRC = "SPD CRC Check"
    ATTEMPT_FAST_BOOT = "Attempt Fast Boot"
    BSSA_CFG = "BSSA Configuration Menu"

    # PXE Configuration
    SLOT_PXE = "Slot PXE Control"
    OCP_PXE = "FLEX IO \d Port \d"

    # Memory RAS Configuratioin
    MIRROR_MODE = "Mirror Mode"
    ADDDC_SP = "ADDDC Sparing"

    # Advanced Power Management Configuration
    HW_P_STATE = 'Hardware PM State Control'
    CPU_ADV_PM_TUN = 'CPU Advanced PM Tuning'
    POWER_EFFICIENCY = 'Performance Profile'
    CPU_P_STATE = 'CPU P-State Control'
    CPU_C_STATE = 'CPU C-State Control'
    PKG_C_STATE_CONTROL = 'Package C-State Control'
    MEM_POWER_THER_CONFIG = 'Memory Power & Thermal Configuration'
    SPEED_STEP_EIST = 'SpeedStep \(Pstates\)'
    MWAIT = "Enable Monitor MWAIT"
    C6_REPORT = "CPU C6 report"
    C1E = "Enhanced Halt State \(C1E\)"
    C1E_OS = "C1E OS Indicator"
    C6_OS = "C6 OS Indicator"
    DEMT = "DEMT"
    STATIC_TURBO = "Static Turbo"
    HWP = "Hardware P-State"
    UFS = "Uncore Freq Scaling"

    # Memory Power & Thermal Configuration
    MEM_POWER_ADV = 'Memory Power Savings Advanced Options'

    # Memory Power Savings Advanced Options
    CKE = 'CKE Power Down'
    CKE_FEATURE = 'CKE Feature'
    CKE_IDLE_TIMER = 'CKE Idle Timer'
    PPD = 'PPD'

    # BSSA Configuration Menu
    RMT = "Rank Margin Tool"

    # Common RefCode Configuration
    NUMA = "NUMA"

    # BMC Configuration
    BMC_WDT_CONFIGURATION = 'BMC Configuration'
    BMC_WDT_POST = "BMC WDT Support For POST"
    BMC_WDT_ACTION_POST = "BMC WDT Action For POST"
    BMC_WDT_TIMEOUT_POST = "BMC WDT Time Out For POST"
    BMC_WDT_OS = "BMC WDT Support For OS"
    BMC_WDT_ACTION_OS = "BMC WDT Action For OS"
    BMC_WDT_TIMEOUT_OS = "BMC WDT Time Out For OS"
    BMC_NET_MODE = "BMC Network Mode"
    BMC_SERVICE = "BMC Service"
    BMC_SMART_COOLING = "BMC Smart Cooling"
    LOAD_BMC_DEFAULT = "Load BMC Default"
    POWER_POLICY = "Resume On AC Power Loss"
    BMC_FAN_MODE = "BMC Smart Cooling"

    # PCH-IO configuration
    NETWORK_CONFIG = 'Network Configuration'
    USB_CONFIG = 'USB Configuration'
    USB_MOUSE = 'USB Mouse'
    USB_KEYBOARD = 'USB Keyboard'
    USB_STORAGE = 'USB MassStorage'

    # Console Redirection Configuration
    CONSOLE_REDIR = 'Console Redirection'
    FLOW_CTL = "Flow Control"
    SPCR = 'SPCR'
    BAUD_RATE = 'Baud Rate'

    # Misc Configuration
    CDN = 'CDN Support'
    ASPM_GLOBAL = r"PCIe ASPM Support \(Global\)"
    SYS_DEBUG_LEVEL = "System Debug Level"
    WAKE_ON_LAN = "Wake on PME"
    SIO_1711 = "SIO 1711"
    BASE_IO_ADDRESS = "Base I/O Address"
    MEM_PRINT_LEVEL = "Memory Print Level"

    # System Event Log
    RAS_LOG_LEVEL = "RAS Log Level"

    # Security
    SIMPLE_PW = 'Simple Password'
    POWER_ON_PW = "Power-On Password"
    SAVE_PW_RCD_NUM = "Saved password record numbers"
    DEL_PW_SUPPORT = "Delete Password Support"
    SET_ADMIN_PW = ["Set Supervisor Password"]  # option without a value
    DEL_ADMIN_PW = ['Delete Supervisor Password']  # option without a value
    SET_USR_PW = ["Set User Password"]  # option without a value
    DEL_USER_PW = ['Delete User Password']  # option without a value
    ADD_WEAK_PW = "Add Weak Password"
    WEAK_PW_DICT = "Weak Password Dictionary"
    DEL_WEAK_PW = "Remove Weak Password"
    TLS_AUTH_CONFIG = "TLS Auth Configuration"
    PW_EXPIRE_DATE = "Password Expiration Date"
    TPM_DEV = "TPM Device"
    TPM_ACTIVE = "TPM2 Active PCR Hash Algorithm"
    TPM_SUPPORT = "TPM2 Hardware Supported Hash Algorithm"
    TPM2_OPERATE = "TPM2 Operation"

    # IIO Configuration
    VTD_MENU = "Intel\(R\) Virtualization for Directed I/O \(VT-d\)"
    VTD = "Intel\(R\) VT for Directed I/O \(VT-d\)"
    PCI_64_RSC_ALLOC = "PCI 64-Bit Resource Allocation"
    IIO_STK_RSC_CONFIG = "IIO Stack IO Resource Configuration"
    PCIE_PORT = "PCIe Port"
    VMD_MENU = "Intel\(R\) VMD technology"

    # SR-IOV Setup Settings
    SRIOV_MENU = "SR-IOV Setup Settings"
    SRIOV_GLOBAL = "PCIe SR-IOV"
    SRIOV_PORT = r"CPU\d Port (?:DMI|[0-9A-F]{2})"

    # VT-d Configuration
    OPT_OUT_MITIGATION = "Opt-Out Illegal MSI Mitigation"
    DMA_CON_OP_FLAG = "DMA Control Opt-In Flag"
    INTERRUPT_REMAPPING = "Interrupt Remapping"
    SATC_SUPPORT = "SATC Support"
    RHSA_SUPPORT = "RHSA Support"

    # Intel(R) VMD technology
    VMD_CONFIG = "Intel\(R\) VMD Config"

    # PCIE Root Port
    ASPM_ROOT_PORT = "PCIe ASPM Support"

    # Boot
    MENU_BOOT_ORDER = 'UEFI'
    PXE_BOOT_CAPABILITY = 'PXE Boot Capability'
    PXE_RETRY_COUNT = "PXE Retry Count"
    PXE_TIMEOUT_CONTROL = "PXE Timeout Control"
    BOOT_TYPE = 'Boot Type'
    BOOT_FAIL_POLICY = 'Boot Fail Policy'
    BOOT_OPTIONS = 'Boot Options'
    UEFI = "UEFI"
    LEGACY = "Legacy"
    UEFI_BOOT = "UEFIBoot"
    LEGACY_BOOT = "LegacyBoot"
    USB_BOOT = "USB Boot"
    SP_BOOT = "SP Boot"
    HTTPS_BOOT = "HTTPS Boot Capability"
    BOOT_OVERRIDE = "Boot Override"
    BOOT_SEQUENCE = "Boot Sequence"

    # UEFI Boot
    MENU_HDD_BOOT = 'Hard Disk Drive'
    MENU_DVD_BOOT = "DVD-ROM Drive"
    MENU_PXE_BOOT = "PXE"
    MENU_OTHERS_BOOT = "Others"

    # Boot Manager
    BOOT_OPTION_SUSE = [BootOS.SLES]
    BOOT_OPTION_RED = [BootOS.RHEL]
    BOOT_OPTION_OS = [getattr(BootOS, SutConfig.Sys.OS_UEFI.upper())]
    UBUNTU = BootOS.UBUNTU
    LINUX_GRUB = "[Pp]ress '\w' to"
    SLOT_PXE_PORT = ".*XE.*SLOT.*Port.*"
    SLOT_PXE_FIRST = "CPU \d+ First Slot Port \d+"
    OCP_PXE_BOOT = ".*PXE.*FLEXIO.*Port.*"

    # Secure Boot
    SECURE_STATE = "Secure Boot State"
    SECURE_MODE = "Secure Boot Mode"
    SECURE_RESTORE = "Restore Secure Boot to Factory Settings"
    SECURE_ERASE = "Erase all Secure Boot Settings"

    # General Values
    ENABLE = "Enabled"
    DISABLE = "Disabled"
    Auto = "Auto"
    FULL_MIRROR = "Full Mirror Mode"
    VAL_CKE_IDLE = "20"
    VAL_TTY0 = "3F8"        # tty0
    VAL_TTY1 = "2F8"        # tty1
    # Value: Resume On AC Power Loss
    VAL_POWER_ON = "Power On"
    VAL_POWER_LAST = "Last State"
    VAL_POWER_OFF = "Power Off"
    # Values List (index 0 is the default value)
    VAL_MEM_REF = ["Static 2x Mode", "Dynamic Mode"]
    VAL_MEM_FREQ = ["Auto", "3200", "3600", "4000", "4400", "4800"]
    VAL_PW_EXPIRE = ["180 days", "0 day", "30 days", "60 days", "90 days", "360 days"]
    VAL_LP_EN = "ALL LPs"
    VAL_LP_DIS = "Single LP"
    # HTTPS Boot Capability
    VAL_HTTPS_CAP = ["Disabled", "HTTPS:IPv4", "HTTPS:IPv6", "HTTPS:IPv4/IPv6"]
    # PXE Boot Capability
    VAL_PXE_CAP = ["Disabled", "UEFI:IPv4", "UEFI:IPv6", "UEFI:IPv4/IPv6"]
    VAL_ASPM = [DISABLE, "Per individual port", "L1 Only"]
    VAL_SRIOV = [ENABLE, DISABLE, "Per IIO Port"]
    VAL_PXE_TIMEOUT_CONTROL = [DISABLE, "1", "2", "3", "4"]
    # BMC WDT Action For OS
    VAL_BMC_WDT_ACT = ["HardReset", "NoAction", "PowerDown", "PowerCycle"]

    # Exit
    SAVE_WO_RESET = "Save Changes Without Exiting"
    SAVE_W_RESET = "Save Changes & Exit"
    LOAD_CUSTOM_DEFAULT = 'Load Custom Defaults'

    # PATH of Setup Menus
    PATH_UNCORE_GENERAL = [CPU_CONFIG, UNCORE_CONFIG, UNCORE_GENERAL]
    PATH_UNCORE_STATUS = [CPU_CONFIG, UNCORE_CONFIG, UNCORE_GENERAL, UNCORE_STATUS]
    PATH_PSTATE_CTL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, CPU_P_STATE]
    PATH_USB_CFG = [PCH_CONFIG, USB_CONFIG]
    PATH_ADV_PM_CFG = [CPU_CONFIG, ADV_POWER_MGF_CONFIG]
    PATH_PER_CPU_INFO = [CPU_CONFIG, PROCESSOR_CONFIG, PROC_INFO]
    PATH_PRO_CFG = [CPU_CONFIG, PROCESSOR_CONFIG]
    PATH_PRO_COMM = [CPU_CONFIG, COMMON_REF_CONFIG]
    PATH_IIO_CONFIG = [CPU_CONFIG, IIO_CONFIG]
    PATH_MEM_CONFIG = [CPU_CONFIG, MEMORY_CONFIG]
    PATH_MEM_RAS = PATH_MEM_CONFIG + [MEM_RAS_CFG]
    PATH_MEN_INFO = [CPU_CONFIG, MEMORY_CONFIG, MEM_TOP]
    PATH_MEM_POWER_ADV = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, MEM_POWER_THER_CONFIG, MEM_POWER_ADV]
    PATH_MISC_CONFIG = [MISC_CONFIG]
    PATH_CSTATE_CTL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, CPU_C_STATE]
    PATH_PCSC_CTL = [CPU_CONFIG, ADV_POWER_MGF_CONFIG, PKG_C_STATE_CONTROL]
    PATH_VIRTUAL_VTD = [CPU_CONFIG, IIO_CONFIG, VTD_MENU]
    PATH_WDT_CONFIG = [BMC_CONFIG, BMC_WDT_CONFIGURATION]
    PATH_PERI_CONFIG = [PERI_CONFIG, SIO_1711]
    PATH_IIO_STACK = [CPU_CONFIG, IIO_CONFIG, IIO_STK_RSC_CONFIG]
    PATH_SRIOV = [PERI_CONFIG, SRIOV_MENU]

    # Keyboard Type
    KEYBOARD_FR = "fr-FR"
    KEYBOARD_JP = "ja-JP"
    KEYBOARD_US = "en-US"

    # Logo Show Flag in serial log
    LOGO_SHOW = "BootType"

    # Pick options for Load Default TEST
    PICK_OPTIONS = [  # [PAGE, PATH, OptionName, SetValue, DefaultValue]
        [PAGE_BOOT, [], BOOT_TYPE, LEGACY_BOOT, UEFI_BOOT],
        [PAGE_ADVANCED, PATH_MEM_CONFIG, MEM_TURBO, ENABLE, DISABLE],
        [PAGE_ADVANCED, [CONSOLE_CONFIG], FLOW_CTL, "RTS/CTS", "None"],
        [PAGE_ADVANCED, PATH_WDT_CONFIG, BMC_WDT_POST, ENABLE, DISABLE]
    ]

    # Pick options for load custom default  test
    CUSTOM_OPTIONS = [  # page, path, option_name, custom_value, change_value, custom_var_dict
        [PAGE_ADVANCED, PATH_PRO_CFG, HW_PREFETCHER, DISABLE, ENABLE, {Attr.HW_PREFETCHER: 0}],
        [PAGE_BOOT, None, USB_BOOT, DISABLE, ENABLE, {Attr.USB_BOOT: 0}],
        [PAGE_ADVANCED, [PXE_CONFIG], SLOT_PXE, DISABLE, ENABLE, {Attr.PXE_EN: 0}]]

    # 精简打印，华为要求 LogTime_check_list
    OEM_LOG_COMMON = [
        'BootType',
        'RC Version',
        'BIOS Version',
        'Release Date',
        'BMC FW Version',
        'R_PCH_TCO2_STS = 0x0',
        'The Box has NOT been opened.',
        'E(?:FI1711 V1.00.0)?5',
        HOTKEY_PROMPT_DEL,
        HOTKEY_PROMPT_F11,
        HOTKEY_PROMPT_F12,
        HOTKEY_PROMPT_F6,
        # 'BGRT BmpToGop Unsupported',
        BIOS_BOOT_COMPLETE]

    # GPIO ERROR keyword in serial POST log
    GPIO_ERR = "GPIO ERROR"
    EQUIP_FLAG = "Get EquipmentEnableFlag Variable {}\(Success\)"

    # serial log - error key word and ignored str list defined group,
    SERIAL_WORDS = ["error", "fail", "assert", "exception"]
    SERIAL_IGNORE = [
        "IpmiLibReportSlotInfoToBMC Fail,Status: 0x7, RecvData = 0xD6",  # BMC版本适配异常
        "Error: GetSgxPrmrrData \(Unsupported\)",
        ]

    # dmesg info
    DMESG_WORDS = ["error", "fail", "warn"]
    DMESG_IGNORE = ["ERST: Error Record Serialization Table \(ERST\) support is initialized.",
                    "4xxx",  # 2288V7 RHEL8.6 Report QAT error
                    "BAR 13: failed to assign \[io  size 0x1000\]"
                    ]

    CURSOR_LOGO = (64, 160, 224, 320)
    CURSOR_HOTKEY = (0, 0, 300, 80)

    UNI_SAVE_CUSTOM_DEFAULT = "SaveCustomDefault"
    UNI_LOAD_CUSTOM_DEFAULT = "LoadCustomDefault"


class BiosCfg:
    """BIOS Configuration to be Set by uniCfg Tool"""

    ACTIVE_CPU_CORE = {Attr.CPU_CORES: hex(SutConfig.Sys.CPU_CORES - 1)[2:]}

    RMT_EN = {
        Attr.RMT: 1,
        Attr.MEM_DBG_LEVEL: 1,
        Attr.SYS_DBG_LEVEL: 1
    }

    EQUIP_FLAG = {
        Attr.EQUIP_FLAG: 1
    }

    MFG_RMT = {
        **EQUIP_FLAG,
        **RMT_EN
    }

    HPM_KEEP = {  # HPM Upgrade/Downgrade keep BIOS Setting unchanged setting
        Attr.ADDDC_EN: 0,
        Attr.PPR_TYPE: 0,
        Attr.USB_BOOT: 0,
        Attr.CDN: 0,
        Attr.FDM: 0,
        Attr.CR_POST: 0,
        Attr.KTI_L0P: 0,
        Attr.SYS_ERR_EN: 0,
        Attr.WHEA_EN: 0,
        Attr.EIST: 0,
        Attr.HT_EN: 0,
        Attr.C6: 1,
        Attr.RMT: 1,
        Attr.CPU_CORES: 4,
        Attr.WDT_POST: 0xf,
    }

    ADDDC_DIS = {Attr.ADDDC_EN: 0}

    RAS_LOG_DIS = {Attr.RAS_LOG_LEVEL: 0}

    Boot_Override_def = {Attr.BOOT_OVERRITE: 0}

    Boot_Override_aft = {Attr.BOOT_OVERRITE: 8}

    Boot_Fail_Policy_def = {Attr.BOOT_FAIL_POLICY: 1}

    Boot_Fail_Policy_aft = {Attr.BOOT_FAIL_POLICY: 2}
