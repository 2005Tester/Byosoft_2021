#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-


#UTF-8键位
class Key:
    ADD = '\x2B'  # +
    SUBTRACT = '\x2D'  # -
    ENTER = '\x0D'
    DEL = '\x7F'
    F1 = '\x1b1'
    F7 = '\x1b7'
    F9 = '\x1b9'
    F10 = '\x1b0'
    F11 = '\x1b!'
    F12 = '\x1b@'
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    LEFT = '\x1b[D'
    RIGHT ='\x1b[C'
    Y = 'Y'
    N = 'N'
    CONTROL = '\ue009'
    DISCARD_CHANGES = ['N']
    RESET_DEFAULT = [F9, Y]
    SAVE_RESET = [F10, Y]
    CONTROL_F11 = [CONTROL, F11]
    CONTROL_Q = [chr(0x11)]
    PAGE_UP = '\x1b?'
    PAGE_DOWN = '\x1b/'

#VT100键位
class VT100_Key:
    ADD = '\x2B'  # +
    SUBTRACT = '\x2D'  # -
    ENTER = '\x0D'
    DEL = '\x7F'
    F1 = '\x1bOP'
    F7 = '\x1bOq'
    F9 = '\x1bOp'
    F10 = '\x1bOM'
    F11 = '\x1bOZ'
    F12 = '\x1bO['
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    LEFT = '\x1b[D'
    RIGHT = '\x1b[C'
    Y = 'Y'
    N = 'N'
    CONTROL = '\ue009'
    DISCARD_CHANGES = ['N']
    RESET_DEFAULT = [F9, Y]
    SAVE_RESET = [F10, Y]
    CONTROL_F11 = [CONTROL, F11]
    CONTROL_Q = [chr(0x11)]
    PAGE_UP = '\x1b[?'
    PAGE_DOWN = '\x1b[/'


class Puti:
    # Pages in bios configuration
    PAGE_MAIN = "BIOS Info"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Save Changes'
    PAGE_ALL = [PAGE_MAIN, PAGE_ADVANCED, PAGE_SECURITY, PAGE_BOOT, PAGE_EXIT]

    # Menus of main page
    CPU_INFO = 'CPU Info'
    MEM_INFO = 'Memory Info'
    DATE_TIME = 'System Date and Time'
    PCIE_INFO = 'PCIE Info'
    SEL_LANG = 'Select Language'

    # Menus of Advanced
    TERMINAL_TYPE = 'Terminal Type'
    LAN_CONFIG = 'Lan Configuration'
    VIDEO_CONFIG = 'Video Configuration'
    SATA_CONFIG = 'SATA Configuration'
    USB_CONFIG = 'USB Configuration'
    VIRTUALIZATION = 'Virtualization'
    MISC_CONFIG = 'Misc Configuration'
    SERVER_CONFIG = 'Server Configuration'
    ERROR_MANAG = 'Error Management'
    HYGON_CBS = 'Hygon CBS'
    HDD_BIND = 'HDD Bind'
    UEFI_HII = 'UEFI HII Configuration'

    # Menus of Security
    SET_USER_PSW = 'Set User Password'
    PSW_LOCK_TIME = 'Password Lock Time'
    PSW_VALID_DAYS = 'Password Valid Days'
    CUSTOM_PSW_CHECK = 'Custom Password Check '
    PSW_COMPLEXITY = 'Password Complexity'
    PSW_LEN = 'Password Length'
    PSW_RETRY = 'Password Retry'
    TPM_SEL = 'TPM Select'
    SECURE_BOOT = 'Secure Boot'
    HDD_PSW = 'Hdd Password'

    # Menus of Boot
    QUIET_BOOT = 'Quiet Boot'
    NUMLOCK_STATE = 'Bootup NumLock State'
    LEGACY_OPTION_ROM = 'OPTION ROM Message'
    BOOT_MODE = 'Boot Mode'
    INTERNAL_SHELL = 'Internal SHELL'
    PXE_OPTION_ROM = 'PXE Option Rom'
    PXE_NETWORK = 'Select a Network to PXE'
    PXE_RETRY = 'PXE Boot Options Retry'
    PXE_IP_VER = 'Net Boot IP Version'
    PXE_BOOT_PRIOROTY = 'PXE Boot Priority'
    HDD_BOOT_NAME = 'Internal Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    OTHER_BOOT_NAME = 'Others'

    # Menus of Exit
    SAVE_AND_EXIT = 'Save and Exit'
    EXIT_NO_SAVE = 'Discard Changes and Exit'
    LOAD_DEFAULTS = 'Load Setup Defaults'
    BIOS_UPDATE_PARAMETERS = 'BIOS Update Parameters'
    BIOS_UPDATE = 'BIOS Update'
    SHUTDOWN_SYSTEM = 'Shutdown System'
    REBOOT_SYSTEM = 'Reboot System'

    # Special option
    AC = 'Restore AC Power Loss'
    REAR_USB = 'Rear USB port Configuration'
    FRONT_USB = 'Front USB port Configuration'
    PCI_MAX = 'PCIe Max Payload Size'
    PCI_ASPM = 'PCIe ASPM'


class Nvwa:
    # Pages in bios configuration
    PAGE_MAIN = "Building Info"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Save Changes'
    PAGE_ALL = [PAGE_MAIN, PAGE_ADVANCED, PAGE_SECURITY, PAGE_BOOT, PAGE_EXIT]

    # Menus of main page
    CPU_INFO = 'CPU Info'
    MEM_INFO = 'Memory Info'
    DATE_TIME = 'System Date and Time'
    PCIE_INFO = 'PCIE Info'
    SEL_LANG = 'Select Language'

    # Menus of Advanced
    TERMINAL_TYPE = 'Terminal Type'
    LAN_CONFIG = 'Lan Configuration'
    VIDEO_CONFIG = 'Video Configuration'
    SATA_CONFIG = 'SATA Configuration'
    USB_CONFIG = 'USB Configuration'

    VIRTUALIZATION = 'Virtualization'
    MISC_CONFIG = 'Misc Configuration'
    SERVER_CONFIG = 'Server Configuration'
    ERROR_MANAG = 'Error Management'
    HYGON_CBS = 'Hygon CBS'
    HDD_BIND = 'HDD Bind'
    UEFI_HII = 'UEFI HII Configuration'

    # Menus of Security
    SET_USER_PSW = 'Set User Password'
    PSW_LOCK_TIME = 'Password Lock Time'
    PSW_VALID_DAYS = 'Set Password Valid Days'
    CUSTOM_PSW_CHECK = 'Custom Password Check'
    PSW_COMPLEXITY = 'Password Complexity'
    PSW_LEN = 'Password Length'
    PSW_RETRY = 'Password Retry'
    TPM_SEL = 'TPM Select'
    SECURE_BOOT = 'Secure Boot'
    HDD_PSW = 'Hdd Password'

    # Menus of Boot
    QUIET_BOOT = 'Quiet Boot'
    NUMLOCK_STATE = 'Bootup NumLock State'
    LEGACY_OPTION_ROM = 'OPTION ROM Message'
    BOOT_MODE = 'Boot Mode'
    INTERNAL_SHELL = 'Internal SHELL'
    PXE_OPTION_ROM = 'PXE Option Rom'
    PXE_NETWORK = 'Select a Network to PXE'
    PXE_RETRY = 'PXE Boot Options Retry'
    PXE_IP_VER = 'Net Boot IP Version'
    PXE_BOOT_PRIOROTY = 'PXE Boot Priority'
    HDD_BOOT_NAME = 'Internal Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    OTHER_BOOT_NAME = 'Others'

    # Menus of Exit
    SAVE_AND_EXIT = 'Save and Exit'
    EXIT_NO_SAVE = 'Discard Changes and Exit'
    LOAD_DEFAULTS = 'Load Setup Defaults'
    BIOS_UPDATE_PARAMETERS = 'BIOS Update Parameters'
    BIOS_UPDATE = 'BIOS Update'
    SHUTDOWN_SYSTEM = 'Shutdown System'
    REBOOT_SYSTEM = 'Reboot System'

    # Special option
    AC = 'Restore AC Power Loss'
    REAR_USB = 'Rear USB port Configuration'
    FRONT_USB = 'Front USB port Configuration'
    PCI_MAX = 'PCIE Max Payload Size'
    PCI_ASPM = 'PCIE ASPM'


class Sanzang:
    # Pages in bios configuration
    PAGE_MAIN = "Build Info"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Save Changes'

    PAGE_ALL = [PAGE_MAIN, PAGE_ADVANCED, PAGE_SECURITY, PAGE_BOOT, PAGE_EXIT]
    SETUP_MESSAGE = PAGE_MAIN  # 进入SetUp确认信息
    # Menus of main page
    CPU_INFO = 'CPU Info'
    MEM_INFO = 'Memory Info'
    DATE_TIME = 'System Date and Time'
    PCIE_INFO = 'PCIE Info'
    SEL_LANG = 'Select Language'

    # Menus of Advanced
    TERMINAL_TYPE = 'Terminal Type'
    LAN_CONFIG = 'Onboard Lan Configuration'
    VIDEO_CONFIG = 'Video Configuration'
    SATA_CONFIG = 'SATA Configuration'
    USB_CONFIG = 'USB Configuration'
    VIRTUALIZATION = 'Virtualization Configuration'
    MISC_CONFIG = 'Misc Configuration'
    SERVER_CONFIG = 'Server Management'
    ERROR_MANAG = 'Error Management'
    HYGON_CBS = 'Hygon CBS'
    HDD_BIND = 'HDD Bind'
    UEFI_HII = 'UEFI HII Configuration'

    # Menus of Security
    SET_USER_PSW = 'Set User Password'
    PSW_LOCK_TIME = 'Password Lock Time'
    PSW_VALID_DAYS = 'Password Valid Days'
    CUSTOM_PSW_CHECK = 'Custom Password Check '
    PSW_COMPLEXITY = 'Password Complexity'
    PSW_LEN = 'Password Length'
    PSW_RETRY = 'Password Retry'
    TPM_SEL = 'TPM Select'
    SECURE_BOOT = 'Secure Boot'
    HDD_PSW = 'HDD Password'

    # Menus of Boot
    QUIET_BOOT = 'Quiet Boot'
    NUMLOCK_STATE = 'Bootup NumLock State'
    LEGACY_OPTION_ROM = 'OPTION ROM Message'
    BOOT_MODE = 'Boot Mode'
    INTERNAL_SHELL = 'Internal SHELL'
    PXE_OPTION_ROM = 'PXE Option Rom'
    PXE_NETWORK = 'Select a Network to PXE'
    PXE_RETRY = 'PXE Boot Options Retry'
    PXE_IP_VER = 'Net Boot IP Version'
    PXE_BOOT_PRIOROTY = 'PXE Boot Priority'
    HDD_BOOT_NAME = 'Internal Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    OTHER_BOOT_NAME = 'Others'

    # Menus of Exit
    SAVE_AND_EXIT = 'Save and Exit'
    EXIT_NO_SAVE = 'Discard Changes and Exit'
    LOAD_DEFAULTS = 'Load Setup Defaults'
    BIOS_UPDATE_PARAMETERS = 'BIOS Update Parameters'
    BIOS_UPDATE = 'BIOS Update'
    SHUTDOWN_SYSTEM = 'Shutdown System'
    REBOOT_SYSTEM = 'Reboot System'

    # Special option
    AC = 'Restore AC power loss'
    REAR_USB = 'Rear USB Port Configuration'
    FRONT_USB = 'Front USB Port Configuration'
    PCI_MAX = 'PCIE Max Payload Size'
    PCI_ASPM = 'PCIE ASPM'


class Yangjian:
    # Pages in bios configuration
    PAGE_MAIN = "Build Info"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Save Changes'

    PAGE_ALL = [PAGE_MAIN, PAGE_ADVANCED, PAGE_SECURITY, PAGE_BOOT, PAGE_EXIT]
    SETUP_MESSAGE = PAGE_MAIN  # 进入SetUp确认信息
    # Menus of main page
    CPU_INFO = 'CPU Info'
    MEM_INFO = 'Memory Info'
    DATE_TIME = 'System Date and Time'
    PCIE_INFO = 'PCIE Info'
    SEL_LANG = 'Select Language'

    # Menus of Advanced
    TERMINAL_TYPE = 'Terminal Type'
    LAN_CONFIG = 'Onboard Lan Configuration'
    VIDEO_CONFIG = 'Video Configuration'
    SATA_CONFIG = 'SATA Configuration'
    USB_CONFIG = 'USB Configuration'

    VIRTUALIZATION = 'Virtualization Configuration'
    MISC_CONFIG = 'Misc Configuration'
    SERVER_CONFIG = 'Server Management'
    ERROR_MANAG = 'Error Management'
    HYGON_CBS = 'Hygon CBS'
    HDD_BIND = 'HDD Bind'
    UEFI_HII = 'UEFI HII Configuration'

    # Menus of Security
    SET_USER_PSW = 'Set User Password'
    PSW_LOCK_TIME = 'Password Lock Time'
    PSW_VALID_DAYS = 'Password Valid Days'
    CUSTOM_PSW_CHECK = 'Custom Password Check '
    PSW_COMPLEXITY = 'Password Complexity'
    PSW_LEN = 'Password Length'
    PSW_RETRY = 'Password Retry'
    TPM_SEL = 'TPM Select'
    SECURE_BOOT = 'Secure Boot'
    HDD_PSW = 'HDD Password'

    # Menus of Boot
    QUIET_BOOT = 'Quiet Boot'
    NUMLOCK_STATE = 'Bootup NumLock State'
    LEGACY_OPTION_ROM = 'OPTION ROM Message'
    BOOT_MODE = 'Boot Mode'
    INTERNAL_SHELL = 'Internal SHELL'
    PXE_OPTION_ROM = 'PXE Option Rom'
    PXE_NETWORK = 'Select a Network to PXE'
    PXE_RETRY = 'PXE Boot Options Retry'
    PXE_IP_VER = 'Net Boot IP Version'
    PXE_BOOT_PRIOROTY = 'PXE Boot Priority'
    HDD_BOOT_NAME = 'Internal Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    OTHER_BOOT_NAME = 'Others'

    # Menus of Exit
    SAVE_AND_EXIT = 'Save and Exit'
    EXIT_NO_SAVE = 'Discard Changes and Exit'
    LOAD_DEFAULTS = 'Load Setup Defaults'
    BIOS_UPDATE_PARAMETERS = 'BIOS Update Parameters'
    BIOS_UPDATE = 'BIOS Update'
    SHUTDOWN_SYSTEM = 'Shutdown System'
    REBOOT_SYSTEM = 'Reboot System'

    # Special option
    AC = 'Restore AC Power Loss'
    REAR_USB = 'Rear USB Port Configuration'
    FRONT_USB = 'Front USB Port Configuration'
    PCI_MAX = 'PCIE Max Payload Size'
    PCI_ASPM = 'PCIE ASPM'
