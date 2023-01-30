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
    PROJECT_NAME = "Inspur7500"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "Inspur7500\\Report\\template"

    TESTCASE_CSV = "Inspur7500\\AllTest1.csv"
    RELEASE_BRANCH = "Hygon_016"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\Nvwa\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com5"

    # BMC Configuration
    BMC_IP = '192.168.6.72'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # Legacy OS Configuration
    OS_IP_LEGACY = '192.168.6.241'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    # OS Configuration
    OS_IP = '192.168.6.241'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    # Tool definition - Ver 1.8.18
    IPMITOOL = "Inspur7500\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER,
                                                                                                  BMC_PASSWORD)
    SMBIOS = "Inspur7500\\Tools\\smbiosnvwa\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sda4"
    LINUX_USB_MOUNT = "/mnt/"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs5:"
    USB_VOLUME = "USB:SanDisk \(P4\)"

    # BIOS flash command
    BIOS_FILE = 'BIOS'

    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)
    WINDOWS_FLASH_CMD = "ByoWinFlash.exe bfu"

    DOS_FLASH_CMD = "byoflash bfu"
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE = "previous.bin"
    CONSTANT_BIOS_FILE = "constant.bin"
    OTHERS_BIOS_FILE = 'others.bin'
    UNSIGNED_BIOS_FILE = 'unsigned.bin'

    # Change boot order related cmd with raw method
    UEFI_PXE_ONCE = "{0} raw 0x00 0x08 0x05 0xA0 0x04 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_SETUP_ONCE = "{0} raw 0x00 0x08 0x05 0xA0 0x18 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_HDD_ONCE = "{0} raw 0x00 0x08 0x05 0xA0 0x08 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_ODD_ONCE = "{0} raw 0x00 0x08 0x05 0xA0 0x20 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_USB_ONCE = "{0} raw 0x00 0x08 0x05 0xA0 0x3C 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_NONE_ONCE = "{0} raw 0x00 0x08 0x05 0xA0 0x00 0x00 0x00 0x00".format(IPMITOOL)

    UEFI_PXE_ALWAYS = "{0} raw 0x00 0x08 0x05 0xE0 0x04 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_SETUP_ALWAYS = "{0} raw 0x00 0x08 0x05 0xE0 0x18 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_HDD_ALWAYS = "{0} raw 0x00 0x08 0x05 0xE0 0x08 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_ODD_ALWAYS = "{0} raw 0x00 0x08 0x05 0xE0 0x20 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_USB_ALWAYS = "{0} raw 0x00 0x08 0x05 0xE0 0x3C 0x00 0x00 0x00".format(IPMITOOL)
    UEFI_NONE_ALWAYS = "{0} raw 0x00 0x08 0x05 0xE0 0x00 0x00 0x00 0x00".format(IPMITOOL)

    LEGACY_PXE_ONCE = "{0} raw 0x00 0x08 0x05 0x80 0x04 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_SETUP_ONCE = "{0} raw 0x00 0x08 0x05 0x80 0x18 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_HDD_ONCE = "{0} raw 0x00 0x08 0x05 0x80 0x08 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_ODD_ONCE = "{0} raw 0x00 0x08 0x05 0x80 0x20 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_USB_ONCE = "{0} raw 0x00 0x08 0x05 0x80 0x3C 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_NONE_ONCE = "{0} raw 0x00 0x08 0x05 0x80 0x00 0x00 0x00 0x00".format(IPMITOOL)

    LEGACY_PXE_ALWAYS = "{0} raw 0x00 0x08 0x05 0xC0 0x04 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_SETUP_ALWAYS = "{0} raw 0x00 0x08 0x05 0xC0 0x18 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_HDD_ALWAYS = "{0} raw 0x00 0x08 0x05 0xC0 0x08 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_ODD_ALWAYS = "{0} raw 0x00 0x08 0x05 0xC0 0x20 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_USB_ALWAYS = "{0} raw 0x00 0x08 0x05 0xC0 0x3C 0x00 0x00 0x00".format(IPMITOOL)
    LEGACY_NONE_ALWAYS = "{0} raw 0x00 0x08 0x05 0xC0 0x00 0x00 0x00 0x00".format(IPMITOOL)

    PXE_ONCE_COMMON = "{0} chassis bootdev pxe".format(IPMITOOL)
    SETUP_ONCE_COMMON = "{0} chassis bootdev bios".format(IPMITOOL)
    HDD_ONCE_COMMON = "{0} chassis bootdev disk".format(IPMITOOL)
    ODD_ONCE_COMMON = "{0} chassis bootdev cdrom".format(IPMITOOL)
    USB_ONCE_COMMON = "{0} chassis bootdev floppy".format(IPMITOOL)

    PXE_ALWAYS_COMMON = "{0} chassis bootdev pxe options=persistent".format(IPMITOOL)
    SETUP_ALWAYS_COMMON = "{0} chassis bootdev bios options=persistent".format(IPMITOOL)
    HDD_ALWAYS_COMMON = "{0} chassis bootdev disk options=persistent".format(IPMITOOL)
    ODD_ALWAYS_COMMON = "{0} chassis bootdev cdrom options=persistent".format(IPMITOOL)
    USB_ALWAYS_COMMON = "{0} chassis bootdev floppy options=persistent".format(IPMITOOL)

    # Load Default
    LOAD_DEFAULT = "{0} raw 0x3e 0x61 0x01".format(IPMITOOL)

    # Check or clear boot flag
    BOOT_FLAG_GET = "{0} raw 0x00 0x09 0x05 0x00 0x00".format(IPMITOOL)
    BOOT_FLAG_CLEAR = "{0} raw 0x00 0x08 0x05 0x00 0x00 0x00 0x00 0x00".format(IPMITOOL)

    # OEM命令
    SET_BIOS_SERIAL = 'raw 0x3e 0xc4 0x01'  # 切换BIOS串口
    GET_OPTION = 'raw 0x3e 0xc2'  # OEM命令获取
    CHANGE_OPTION = 'raw 0x3e 0xc3 0x01'  # OEM修改


class Msg:
    POST_MESSAGE = 'Del to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot'
    HOTKEY_PROMPT_DEL = 'Del to enter SETUP'
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu'
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot'

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

    # Menus of boot page
    ENTER_BOOTMENU = "Startup Device Menu|ENTER to select boot device"
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: SanDisk'
    SHELL = "Internal EDK Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    LEGACY_HDD_BOOT_NAME = "SATA3\-1: Samsung SSD 870 EVO 250GB|UEFI SATA3\-1: Samsung SSD 870 EVO 250GB"  # Legacy系统盘在Legacy,UEFI模式下启动名
    UEFI_HDD_BOOT_NAME = 'CentOS Linux\(SATA3\-0: SanDisk SDSSDH3 500G\)|SATA3\-0: SanDisk SDSSDH3 500G'  # UEFI系统盘在Legacy,UEFI模式下启动名
    LINUX_OS = 'CentOS Linux\(SATA3\-0: SanDisk SDSSDH3 500G\)|SATA3\-1: Samsung SSD 870 EVO 250GB'  # UEFI系统盘在UEFI模式启动名，Legacy系统盘在Legacy模式下启动名


class Boot:
    SERVICE_CONFIG = [Msg.PAGE_ADVANCED, Msg.SERVER_CONFIG]
    LOC_USB = [Msg.PAGE_ADVANCED, Msg.USB_CONFIG]
    LOC_HDD = [Msg.PAGE_BOOT, Msg.HDD_BOOT_NAME]
    CPU_INFO = [Msg.CPU_INFO]
    MEM_INFO = [Msg.MEM_INFO]

    ONBOARD_ETH = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]
    PXE = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]

    # Boot order
    BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.USB_BOOT_NAME, Msg.PXE_BOOT_NAME,
                           Msg.ODD_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.USB_BOOT_NAME, Msg.PXE_BOOT_NAME,
                             Msg.ODD_BOOT_NAME]


class Cpu:
    MONITOR_TOOL = 'monitor_0.1.8'
    PSTATE_TOOL = 'pstate-set.sh'
    CSTATE_TOOL = 'SMUToolSuite'
    # CPU信息
    CPU_INFO = [Msg.PAGE_MAIN, Msg.CPU_INFO]

    # CPU频率
    CPU_FREQUENCY = ['1600', '2000', '2500']  # SetUp下可以设定的CPU频率
    SET_CPU_SPEED_NAME = 'Set CPU Speed'
    SET_FREQUENCY = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                     {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Disabled'}]
    SET_FREQUENCY_HIGH = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'Performance'}]

    # CPU超线程
    CLOSE_HYPER_THREADING = ['Console Redirection', 'Misc Configuration', {'Hyper Threading Technology': 'Disabled'}]
    OPEN_HYPER_THREADING = ['Console Redirection', 'Misc Configuration', {'Hyper Threading Technology': 'Enabled'}]

    # CPU C-State
    OPEN_CSTATE = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                   {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Enabled'},
                   {'Set CPU Speed': '{0} MHz'.format(CPU_FREQUENCY[-1])}]
    CLOSE_CSTATE = ['Console Redirection', 'Misc Configuration', {'CPU C-State Control': 'Disabled'}]

    # CPU P-State
    CPU_FREQUENCY_PSTATE = ['2.50', '2.00', '1.60']  # 海光工具检测，P0、P1、P2CPU频率
    SET_PSTATE_P0 = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                     {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Disabled'},
                     {'Set CPU Speed': '{0} MHz'.format(CPU_FREQUENCY[-1])}]
    SET_PSTATE_P0P1 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1'}]
    SET_PSTATE_P0P1P2 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1+P2'}]
    SET_HIGH = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'Performance'}]

    # CPU 降核
    CPU_DOWNCORE_CORE = ['4', '4', '6', '8', '8', '12']  # CPU降核
    DOWNCORE_VALUES = ['TWO (1 + 1)', 'TWO (2 + 0)', 'THREE (3 + 0)', 'FOUR (2 + 2)', 'FOUR (4 + 0)', 'SIX (3 + 3)']
    LOC_DOWNCORE = ['Console Redirection', 'Hygon CBS']
    DOWNCORE_NAME = 'Downcore control'
    SET_DOWNCORE_AUTO = ['Console Redirection', 'Hygon CBS', {'Downcore control': 'Auto'}]

    # CPU AES
    CLOSE_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Disabled'}]
    OPEN_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Enabled'}]

    # CPU NUMA
    NUMA_VALUES = ['None', 'Channel', 'Die', 'Auto']
    CPU_NUMA_ONE = ['2', '2', '1', '2']  # NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO = ['4', '4', '2', '4']  # NUMA双路CPU分别对应插槽、没有、通道、裸片、自动
    LOC_NUMA = ['Console Redirection', 'Hygon CBS']
    NUMA_NAME = 'NUMA'

    # CPU CPB
    CPU_FREQUENCY_CPB = ['2.50', '3.00']  # 海光工具检测,超频关闭，打开下CPU频率
    CLOSE_CPB = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                 {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Enabled'},
                 {'Set CPU Speed': '{0} MHz'.format(CPU_FREQUENCY[-1])}, 'Console Redirection', 'Hygon CBS',
                 {'Core Performance Boost': 'Disabled'}]
    OPEN_CPB = ['Console Redirection', 'Hygon CBS', {'Core Performance Boost': 'Auto|Enabled'}]
    LOC_CPU_SPEED = ['Console Redirection', 'Misc Configuration']

    # CPU Performance
    LOC_PERFORMANCE = ['Console Redirection', 'Misc Configuration']
    PERFORMANCE_NAME = 'ENERGY_PERF_BIAS_CFG mode'
    PERFORMANCE_VALUE_NAME = ['Energy', 'Energy Balance', 'Performance Balance', 'Performance']  # 支持修改的值
    VALUE_CPU_SPEED = ['1.60', '2.00', '2.50', '3.00']  # 每个值对应的CPU频率
    LOC_CPB = ['Console Redirection', 'Hygon CBS']
    CPB_NAME = 'Core Performance Boost'

    # SMEE控制
    OPEN_SMEE = ['Console Redirection', 'Hygon CBS', {'SMEE Control': 'Enabled'}]
    CLOSE_SMEE = ['Console Redirection', 'Hygon CBS', {'SMEE Control': 'Disabled'}]
    SMEE_MSG = 'Secure Memory Encryption \(SME\) active'


class Psw:
    PAGE_ALL = ['BIOS Info', 'Console Redirection', 'Set User Password', 'Shutdown System']  # 用户密码登录，SetUp页面名
    TRY_COUNTS = 2  # 输错密码重试次数,2代表输错2次后，第3次输错会被锁定

    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = "SATA3\-0: SanDisk SDSSDH3 500G"
    HDD_PASSWORD_NAME_02 = "SATA3\-1: Samsung SSD 870 EVO 250GB"
    HDD_NAME_01_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_NAME_02_OS = Msg.LEGACY_HDD_BOOT_NAME

    # Password related messages
    SET_SETUP_PSW_SUCCESS = 'Password Setting Successfully'
    DEL_SETUP_PSW_SUCCESS = 'Password deleted succeeded'
    SET_ADMIN_PSW = 'Set Administrator Password'
    SET_USER_PSW = 'Set User Password'
    CHECK_PSW = 'Custom Password Check '
    PSW_COMPLEXITY = 'Password Complexity'
    PSW_LEN = 'Password Length'
    PSW_RETRY = 'Password Retry'
    LOGIN_SETUP_PSW_PROMPT = 'System Security'
    PSW_LOCK_OPTION = 'Password Lock Time'
    PSW_EXPIRE = 'Password expired'
    PSW_SET_STATUS = 'Installed'
    PWS_NOT_SET_STATUS = 'Not Installed'
    POWER_ON_PSW_OPTION = 'Power-on Password'
    PSW_EXPIRY_DATE = 'Set Password Valid Days'

    HDD_PSW_OPTION = 'Hdd Password'
    SET_HDD_PSW_OPTION = 'Enable Hdd Password'
    DEL_HDD_PSW_OPTION = 'Disable Hdd Password'
    LOGIN_HDD_PSW_PROMPT = 'Enter Hdd Password'
    HDD_LOCK_STATUS = 'security state cannot be changed'
    SET_HDD_HASH_TYPE1 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SHA-256 Hash'}]
    SET_HDD_HASH_TYPE2 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SM3 Hash'}]
    LOC_HDD_PSW = [SET_ADMIN_PSW, HDD_PSW_OPTION]
    LOC_USER_PSW = [SET_ADMIN_PSW, SET_USER_PSW]
    LOC_ADMIN_PSW = [SET_ADMIN_PSW]
    LOC_LOCK_OPTION = [SET_ADMIN_PSW, PSW_LOCK_OPTION]
    SET_TIME_WEEK = [{'Set Password Valid Days': '7 Days'}]
    SET_TIME_MONTH = [{'Set Password Valid Days': '30 Days'}]
    SET_TIME_ALWAYS = [{'Set Password Valid Days': 'Indefinite'}]


class Ipm:
    # Frb2_watchdog
    CLOSE_FRB = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Disabled'}]
    OPEN_FRB1 = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '10minutes|10 minutes'}]
    OPEN_FRB2 = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Power Off'}, {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_FRB3 = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '5minutes|5 minutes'}]

    # OS watchdog
    OPEN_OS_WDOG1 = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Power Off'}, {'OS Watchdog Timer Timeout': '10minutes|10 minutes'}]
    OPEN_OS_WDOG2 = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_OS_WDOG3 = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '5minutes|5 minutes'}]
    CLOSE_OS_WDOG = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Disabled'}]

    # Power Loss
    SET_POWER_LOSS1 = ['Console Redirection', 'Server Configuration', {'Restore AC Power Loss': 'Power On'}]
    SET_POWER_LOSS2 = ['Console Redirection', 'Server Configuration', {'Restore AC Power Loss': 'Last State'}]
    SET_POWER_LOSS3 = ['Console Redirection', 'Server Configuration', {'Restore AC Power Loss': 'Always Off'}]
    LOC_SERVICE = ['Console Redirection', 'Server Configuration']
    POWER_LOSS_OPTION = 'Restore AC Power Loss'
    POWER_LOSS_VALUE = ['<Power On>', '<Last State>', '<Always Off>']

    # oem自定义命令支持修改的BIOS设置项
    OPTION_VALUE = {'HyperThread': [1, {'Enabled': ['0', '1'], 'Disabled': ['0', '0']}],
                    'SR-IOV': [1, {'Enabled': ['1', '0'], 'Disabled': ['1', '1']}],
                    'VMX': [1, {'Enabled': ['2', '1'], 'Disabled': ['2', '0']}],
                    'IOMMU': [1, {'Enabled': ['3,4', '01'], 'Disabled': ['3,4', '00'], 'Auto': ['3,4', '10']}],
                    'RDSEED': [1, {'Enabled': ['5', '1'], 'Disabled': ['5', '0']}],
                    'PXEPriority': [1, {'Disabled': ['6,7', '00'], 'Onboard': ['6,7', '01'], 'Addon': ['6,7', '10']}],

                    'NUMA': [2, {'None': ['0,2', '000'], 'Channel': ['0,2', '001'], 'Die': ['0,2', '010'],
                                 'Auto': ['0,2', '100']}],
                    'Turbo': [2, {'Auto': ['3', '1'], 'Disabled': ['3', '0']}],
                    'PXE': [2, {'Enabled': ['4', '1'], 'Disabled': ['4', '0']}],
                    'SPILock': [2, {'Enabled': ['5', '1'], 'Disabled': ['5', '0']}],
                    'HideBootLogo': [2, {'Enabled': ['6', '1'], 'Disabled': ['6', '0']}],

                    'BootMode': [3, {'UEFI': ['0', '0'], 'Legacy': ['0', '1']}],
                    'IPVersion': [3, {'IPv4': ['1,2', '01'], 'IPv6': ['1,2', '10'], 'All': ['1,2', '11'],
                                      'Disabled': ['1,2', '00']}],
                    'PerfMode': [3, {'UserDefined': ['3,5', '000'], 'Performance': ['3,5', '001'],
                                     'PerformanceBalance': ['3,5', '010'], 'EnergyBalance': ['3,5', '011'],
                                     'Energy': ['3,5', '100']}],
                    'FRB2': [3, {'Disabled': ['6', '0'], 'Enabled': ['6', '1']}],
                    'AES': [3, {'Disabled': ['7', '1'], 'Enabled': ['7', '0']}],

                    'First': [4, {'HDD': ['0,3', '0000'], 'USB': ['0,3', '0010'], 'ODD': ['0,3', '0011'],
                                  'PXE': ['0,3', '0100'], 'Others': ['0,3', '0101']}],
                    'Second': [4, {'HDD': ['4,7', '0000'], 'USB': ['4,7', '0010'], 'ODD': ['4,7', '0011'],
                                   'PXE': ['4,7', '0100'], 'Others': ['4,7', '0101']}],

                    'Third': [5, {'HDD': ['0,3', '0000'], 'USB': ['0,3', '0010'], 'ODD': ['0,3', '0011'],
                                  'PXE': ['0,3', '0100'], 'Others': ['0,3', '0101']}],
                    'Fourth': [5, {'HDD': ['4,7', '0000'], 'USB': ['4,7', '0010'], 'ODD': ['4,7', '0011'],
                                   'PXE': ['4,7', '0100'], 'Others': ['4,7', '0101']}],

                    'Fifth': [6, {'HDD': ['0,3', '0000'], 'USB': ['0,3', '0010'], 'ODD': ['0,3', '0011'],
                                  'PXE': ['0,3', '0100'], 'Others': ['0,3', '0101']}],

                    'Language': [7, {'Chinese': ['0', '0'], 'English': ['0', '1']}],
                    'Console': [7, {'Enabled': ['1', '1'], 'Disabled': ['1', '0']}],
                    'Baudrate': [7, {'9600': ['2,4', '000'], '19200': ['2,4', '001'], '38400': ['2,4', '010'],
                                     '57600': ['2,4', '011'], '115200': ['2,4', '100']}],
                    'SMEE': [7, {'Enabled': ['5', '1'], 'Disabled': ['5', '0']}],

                    'PFEH': [8, {'Enabled': ['0', '1'], 'Disabled': ['0', '0']}],
                    # 'MCACount': [8,
                    #              {'0': ['1,3', '000'], '1': ['1,3', '001'], '5': ['1,3', '010'], '10': ['1,3', '011'],
                    #               '100': ['1,3', '100'], '1000': ['1,3', '101'], '2000': ['1,3', '110']}],
                    'MCACount': [8, {'0': ['1,3', '000'], '1': ['1,3', '001'], '10': ['1,3', '010'],
                                     '4095': ['1,3', '011'], '100': ['1,3', '100'], '1000': ['1,3', '101'],
                                     '2000': ['1,3', '110']}],
                    'OnLan': [8, {'Enabled': ['4', '1'], 'Disabled': ['4', '0']}],
                    'WakeOnLan': [8, {'Enabled': ['5', '1'], 'Disabled': ['5', '0']}],
                    'Graphic': [8, {'PCIE': ['6', '0'], 'IGD': ['6', '1']}],

                    'RearUSB': [9, {'Enabled': ['0', '1'], 'Disabled': ['0', '0']}],
                    'FrontUSB': [9, {'Enabled': ['1', '1'], 'Disabled': ['1', '0']}],
                    'USBStorage': [9, {'Enabled': ['2', '1'], 'Disabled': ['2', '0']}],
                    'MaxPayload': [9, {'Auto': ['3,4', '00'], '128B': ['3,4', '01'], '256B': ['3,4', '10'],
                                       '512B': ['3,4', '11']}],
                    'ASPM': [9, {'L1': ['5,6', '10'], 'Disabled': ['5,6', '00']}],

                    'Property': [10, {'UserDefined': ['0', '0'], 'Performance': ['0', '1']}],
                    'CPUP-State': [10, {'P0+P1+P2': ['1,2', '00'], 'P0+P1': ['1,2', '01'], 'P0': ['1,2', '10']}],
                    'CPUC-State': [10, {'Enabled': ['3', '1'], 'Disabled': ['3', '0']}],
                    'CPUFrequency': [10,
                                     {'2500MHz': ['4,5', '00'], '2000MHz': ['4,5', '01'], '1600MHz': ['4,5', '10']}],

                    'QuietBoot': [13, {'Enabled': ['0', '1'], 'Disabled': ['0', '0']}],
                    'NumLock': [13, {'On': ['1', '1'], 'Off': ['1', '0']}],
                    'OptionRom': [13, {'Enabled': ['2', '1'], 'Disabled': ['2', '0']}],
                    'UEFIShell': [13, {'Enabled': ['3', '1'], 'Disabled': ['3', '0']}],
                    'NetworkStack': [13, {'Enabled': ['4', '1'], 'Disabled': ['4', '0']}],
                    'PXERetry': [13, {'Enabled': ['5', '1'], 'Disabled': ['5', '0']}]
                    }
    DICT = {'HyperThread': 'HyperThreadingTechnology', 'SR-IOV': 'SR-IOVSupport', 'VMX': 'SVM', 'IOMMU': 'IOMMU',
            'RDSEED': 'RDSEEDandRDRANDControl', 'PXEPriority': 'PXEBootPriority', 'NUMA': 'NUMA',
            'Turbo': 'CorePerformanceBoost', 'PXE': 'PXEOptionRom', 'SPILock': 'SPIBIOSLock',
            'HideBootLogo': 'HideBootLogo', 'BootMode': 'BootMode', 'PerfMode': 'ENERGY_PERF_BIAS_CFGmode',
            'Language': 'SelectLanguage', 'Console': 'ConsoleRedirection', 'Baudrate': 'SerialPortBaudrate',
            'SMEE': 'SMEEControl', 'PFEH': 'PlatformFirstErrorHandling', 'MCACount': 'MCAErrorThresholdCount',
            'OnLan': 'OnboardEthernetController', 'WakeOnLan': 'WakeOnLan', 'Graphic': 'PrimaryGraphicsAdapter',
            'RearUSB': 'RearUSBportConfiguration', 'FrontUSB': 'FrontUSBportConfiguration',
            'USBStorage': 'USBMassStorageSupport', 'MaxPayload': 'PCIEMaxPayloadSize', 'ASPM': 'PCIEASPM',
            'Property': 'ENERGY_PERF_BIAS_CFGmode', 'CPUP-State': 'CPUP-StateControl',
            'CPUC-State': 'CPUC-StateControl', 'CPUFrequency': 'SetCPUSpeed', 'QuietBoot': 'QuietBoot',
            'NumLock': 'BootupNumLockState', 'OptionRom': 'OPTIONROMMessage', 'UEFIShell': 'InternalSHELL',
            'NetworkStack': 'UEFINetworkStack', 'PXERetry': 'PXEBootOptionsRetry', 'WaitTime': 'UserWaitTime',
            'FRB2': 'FRB2WatchdogTimer', 'AES': 'AES'}

    # oem命令修改的SetUp选项
    CHANGE_OPTION_VALUE1 = ['HyperThread:Disabled', 'SR-IOV:Disabled', 'VMX:Disabled', 'IOMMU:Disabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:None', 'Turbo:Auto', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:Legacy', 'IPVersion:Ipv6',
                            'PFEH:Disabled', 'MCACount:0', 'OnLan:Disabled', 'WakeOnLan:Disabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:512B',
                            'ASPM:L1', 'PerfMode:Performance', 'CPUP-State:P0', 'NumLock:Off', 'OptionRom:Disabled',
                            'UEFIShell:Enabled',
                            'NetworkStack:Enabled', 'PXERetry:Disabled', 'WaitTime:14', 'First:USB', 'Second:PXE',
                            'Third:ODD', 'Fourth:HDD', 'Fifth:Others', 'FRB2:Disabled', 'AES:Disabled']

    CHANGE_OPTION_VALUE2 = ['HyperThread:Enabled', 'SR-IOV:Enabled', 'VMX:Enabled', 'IOMMU:Enabled', 'RDSEED:Disabled',
                            'PXEPriority:Addon', 'NUMA:Channel', 'Turbo:Disabled', 'PXE:Enabled', 'SPILock:Disabled',
                            'HideBootLogo:Disabled', 'BootMode:UEFI', 'IPVersion:Ipv4', 'PFEH:Enabled', 'MCACount:10',
                            'OnLan:Enabled', 'WakeOnLan:Enabled', 'Graphic:PCIE', 'RearUSB:Enabled', 'FrontUSB:Enabled',
                            'USBStorage:Enabled', 'MaxPayload:128B', 'ASPM:Disabled', 'PerfMode:PerfBalance',
                            'CPUP-State:P0',
                            'CPUC-State:Disabled', 'NumLock:On', 'OptionRom:Disabled', 'UEFIShell:Disabled',
                            'NetworkStack:Disabled',
                            'PXERetry:Enabled', 'WaitTime:25', 'First:PXE', 'Second:Others', 'Third:ODD', 'Fourth:USB',
                            'Fifth:HDD', 'FRB2:Enabled', 'AES:Disabled']

    CHANGE_OPTION_VALUE3 = ['HyperThread:Disabled', 'SR-IOV:Disabled', 'VMX:Disabled', 'IOMMU:Disabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:Die', 'Turbo:Disabled', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:All',
                            'PFEH:Disabled', 'MCACount:100', 'OnLan:Disabled', 'WakeOnLan:Disabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:256B',
                            'ASPM:L1', 'Perfmode:EnergyBalance', 'CPUP-State:P0+P1', 'NumLock:Off', 'OptionRom:Enabled',
                            'UEFIShell:Enabled',
                            'NetworkStack:Disabled', 'PXERetry:Disabled', 'WaitTime:14', 'First:ODD', 'Second:PXE',
                            'Third:HDD', 'Fourth:USB', 'Fifth:Others', 'FRB2:Disabled', 'AES:Enabled']

    CHANGE_OPTION_VALUE4 = ['HyperThread:Enabled', 'SR-IOV:Enabled', 'VMX:Enabled', 'IOMMU:Enabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:Die', 'Turbo:Disabled', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:All',
                            'PFEH:Disabled', 'MCACount:1000', 'OnLan:Disabled', 'WakeOnLan:Enabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:Auto',
                            'ASPM:L1', 'Perfmode:Energy', 'CPUP-State:P0+P1+P2', 'NumLock:Off', 'OptionRom:Enabled',
                            'UEFIShell:Enabled',
                            'NetworkStack:Disabled', 'PXERetry:Disabled', 'WaitTime:131', 'First:USB', 'Second:HDD',
                            'Third:ODD', 'Fourth:PXE', 'Fifth:Others', 'SMEE:Enabled', 'FRB2:Enabled']

    CHANGE_OPTION_VALUE5 = ['HyperThread:Disabled', 'SR-IOV:Disabled', 'VMX:Disabled', 'IOMMU:Disabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:Auto', 'Turbo:Auto', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:Ipv6',
                            'PFEH:Disabled', 'MCACount:2000', 'OnLan:Disabled', 'WakeOnLan:Disabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:512B',
                            'ASPM:L1', 'Perfmode:UserDefined', 'CPUP-State:P0', 'CPUC-State:Enabled',
                            'CPUFrequency:2000MHz', 'NumLock:Off', 'OptionRom:Enabled', 'UEFIShell:Enabled',
                            'NetworkStack:Enabled', 'PXERetry:Disabled', 'WaitTime:32', 'First:PXE', 'Second:HDD',
                            'Third:ODD', 'Fourth:USB', 'Fifth:Others', 'SMEE:Disabled', 'FRB2:Disabled']
    CHANGE_OPTION_VALUE = [CHANGE_OPTION_VALUE1, CHANGE_OPTION_VALUE2, CHANGE_OPTION_VALUE3, CHANGE_OPTION_VALUE4,
                           CHANGE_OPTION_VALUE5]

    # BMC USRE
    ADD_USER = 'Add User'
    DEL_USER = 'Delete User'
    CHANGE_USER = 'Change User'
    USER_NAME = 'User Name'
    USER_PSW = 'User Password'
    CNANGE_USER_PSW = 'Change User Password|Change user Password'
    USER_PRIVILEGE = 'Privilege'
    CALLBACK = 'Callback'
    USER = 'User'
    OPERATOR = 'Operator'
    ADMIN = 'Administrator'
    NO_ACCESS = 'No Access'
    USER_STATE = 'User Status '
    DISABLE = 'Disabled'
    ENABLE = 'Enabled'
    USER_NAME_NOT_MATCH = 'Username is a string of 5 to 16 letters|Username only support the first character must be a letter'
    USER_NAME_EXITS = 'Username does not conform to specifications or already exists'
    ERROR_PSW = 'Wrong Password'
    DEL_USER_SUCCESS = 'Delete user success'
    SET_PSW_SUCCESS = 'Setting Successfully'
    LOC_USER_CONF = ['Console Redirection', 'Server Configuration', 'BMC User Configuration']

    # IPMITOOL 启动
    OS_MSG = 'Kylin|Tencent|CentOS|UOS|Windows'
    UEFI_PXE_MSG = 'Checking media present...'
    LEGACY_PXE_MSG = 'PXE initialising devices...|PXEinitialisingdevices...'
    BOTH_PXE_MSG = 'PXE initialising devices...|Checking media present...|PXEinitialisingdevices...'
    UEFI_USB_MSG = 'UEFI Interactive Shell'
    LEGACY_USB_MSG = 'Start booting from USB device|StartbootingfromUSBdevice'
    BOTH_USB_MSG = 'Start booting from USB device|UEFI Interactive Shell|StartbootingfromUSBdevice'

    OPEN_LAN = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]
    OPEN_PXE = [{'PXE Option Rom': 'Enabled'}]
    BOOT_MODE_UEFI = [{'Boot Mode': 'UEFI'}]
    BOOT_MODE_LEGACY = [{'Boot Mode': 'Legacy'}]
    OPEN_SHELL = [{'Internal SHELL': 'Enabled'}]

    # 板载SOL
    CLOSE_SOL = ['Console Redirection', 'Server Configuration', {'SOL for Baseboard Mgmt': 'Disabled'}]
    OPEN_SOL = ['Console Redirection', 'Server Configuration', {'SOL for Baseboard Mgmt': 'Enabled'}]

    # BMC系统日志
    LOC_SYS_LOG = ['Console Redirection', 'Server Configuration', 'BMC system log']

    # FRU
    LOC_FRU = ['Console Redirection', 'Server Configuration', 'FRU Information']
    CLEAR_FRU = ['Console Redirection', 'Server Configuration', 'Clear System Event Log']


class Pci:
    OPEN_LAN = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]

    # PCIE最大负载
    LOC_PCIE = ['Console Redirection', 'Misc Configuration']
    PCIE_MAX_NAME = 'PCIE Max Payload Size'
    PCIE_MAX_VALUE = ['128B', '256B', '512B', 'Auto']

    # PCIE活动状态电源管理
    OPEN_ASPM = ['Console Redirection', 'Misc Configuration', {'PCIE ASPM': 'L1|Enabled'}]
    CLOSE_ASPM = ['Console Redirection', 'Misc Configuration', {'PCIE ASPM': 'Disabled'}]

    # 4GB以上空间解码
    OPEN_ABOVE = ['Console Redirection', 'Misc Configuration', {'Above 4G Decoding': 'Enabled'}]
    CLOSE_ABOVE = ['Console Redirection', 'Misc Configuration', {'Above 4G Decoding': 'Disabled'}]


class Pxe:
    IPV4_MSG = 'Start PXE over IPv4'
    IPV6_MSG = 'Start PXE over IPv6'

    # PXE Option Rom
    CLOSE_PXE = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                 'User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]

    # PXE 启动
    SET_IPV4 = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'}, {'Net Boot IP Version': 'IPv4'}]
    SET_IPV6 = ['User Wait Time', {'Net Boot IP Version': 'IPv6'}]
    SET_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}, {'PXE Option Rom': 'Enabled'}]
    SET_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}]

    # PXE 重试
    CLOSE_PXE_RETRY = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                       {'PXE Boot Options Retry': 'Disabled'}, {'Net Boot IP Version': 'IPv4'}]
    OPEN_PXE_RETRY = ['User Wait Time', {'PXE Boot Options Retry': 'Enabled'}]
    PXE_RETRY_MSG = 'timeout'

    # LegacyPXE 重试
    CLOSE_PXE_RETRY_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}, {'PXE Option Rom': 'Enabled'},
                              {'PXE Boot Options Retry': 'Disabled'}]
    OPEN_PXE_RETRY_LEGACY = ['User Wait Time', {'PXE Boot Options Retry': 'Enabled'}]
    PXE_RETRY_MSG_LEGACY = 'WangXun\(R\) *PXE *\(PCI01:00.0\)'

    # PXE IP 版本
    SET_IPV4_6 = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                  'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                  {'Net Boot IP Version': 'IPv4 and IPv6'}]

    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun(R) (B4-05-5D-4F-6B-D2)"
    # PXE_NET_ADDON = "Intel E10I2-X540-US (E8-61-1F-29-D8-85)"
    # PXE_NET_ADDON = "Intel PRO-1000-DESTOP (00-1B-21-11-78-CB)"
    PXE_NET_ADDON = "Intel I350-AM2 Eth (80-61-5F-04-BE-1D)"
    # PXE_NET_ADDON = "Intel X710 10GbE (40-A6-B7-45-00-B0)"

    # PXE启动项(IPv4)
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun\(R\) PXE IPv4"
    # PXE_PORT_ADDON = 'UEFI Slot 0: Port \d - Intel PRO-1000-DESTOP PXE IPv4'
    PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d - Intel I350-AM2 Eth PXE IPv4'
    # PXE_PORT_ADDON = 'UEFI Slot 2: Port \d - Intel\(R\) X710 10GbE PXE IPv4'
    SET_ONBOARD = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                   {'Select a Network to PXE': PXE_NET_ONBOARD}, {'Net Boot IP Version': 'IPv4'}]
    SET_ADDON = ['User Wait Time', {'Select a Network to PXE': PXE_NET_ADDON}]
    SET_NONE = ['User Wait Time', {'Select a Network to PXE': 'NULL'}]

    # PXE Boot Priority
    SET_ONBOARD_PRI = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                       {'Select a Network to PXE': 'NULL'}, {'Net Boot IP Version': 'IPv4'},
                       {'PXE Boot Priority': 'Onboard First'}]
    SET_ADDON_PRI = ['User Wait Time', {'PXE Boot Priority': 'Addon First'}]
    SET_ADDON_NONE = ['User Wait Time', {'PXE Boot Priority': 'Disabled'}]


class Sup:
    NECESSARY_MSG = ['BIOS Vendor', 'BIOS Core Version', 'Mother Board Info', 'CPU Info', 'Memory Info',
                     'System Date and Time',
                     'PCIE Info', 'USB Configuration', 'Console Redirection', 'Set Administrator Password',
                     'Set User Password', 'Hdd Password', 'User Wait Time',
                     'PXE Option Rom', 'Boot Order', 'Save and Exit', 'Load Setup Defaults', 'BIOS Update Parameters',
                     'Shutdown System', 'Reboot System']

    # Lan Configuration
    CLOSE_LAN = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Disabled'},
                 'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                 {'Net Boot IP Version': 'IPv4'}]
    LOC_PCI_INFO = [Msg.PAGE_MAIN, 'PCIE Info', 'PCI Device Info']
    OPEN_LAN = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]

    # 网络唤醒
    MAC_ADDRESS = 'B4-05-5D-4F-6B-D3|B4-05-5D-4F-6B-D4'
    CLOSE_WAKE_ONLINE = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                         {'Wake On Lan': 'Disabled'}]
    OPEN_WAKE_ONLINE = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                        {'Wake On Lan': 'Enabled'}]

    # USB 存储设备支持
    CLOSE_USB_STORAGE = ['User Wait Time', {'Boot Mode': 'UEFI'}, 'Console Redirection', 'USB Configuration',
                         {'USB Mass Storage Support': 'Disabled'}, 'USB Port Configuration',
                         {'Rear USB port Configuration': 'Enabled'}, {'Front USB port Configuration': 'Enabled'}]
    OPEN_USB_STORAGE = ['Console Redirection', 'USB Configuration', {'USB Mass Storage Support': 'Enabled'}]

    # USB 端口配置
    OPEN_USB_PORT_BOTH = ['Console Redirection', 'USB Configuration', {'USB Mass Storage Support': 'Enabled'},
                          'USB Port Configuration', {'Rear USB port Configuration': 'Enabled'},
                          {'Front USB port Configuration': 'Enabled'}]
    LOC_USB_INFO = ['Console Redirection', 'USB Configuration']
    OPEN_USB_PORT_FRONT = [{'Rear USB port Configuration': 'Disabled'}, {'Front USB port Configuration': 'Enabled'}]
    OPEN_USB_PORT_BEHIND = [{'Rear USB port Configuration': 'Enabled'}, {'Front USB port Configuration': 'Disabled'}]
    CLOSE_USB_PORT_BOTH = [{'Rear USB port Configuration': 'Disabled'}, {'Front USB port Configuration': 'Disabled'}]
    OPEN_USB_PORT_ALL = [{'Rear USB port Configuration': 'Enabled'}, {'Front USB port Configuration': 'Enabled'}]
    CLOSE_USB_PORT_FRONT = [{'Front USB port Configuration': 'Disabled'}]
    OPEN_USB_PORT_FRONT_ONLY = [{'Front USB port Configuration': 'Enabled'}]
    CLOSE_USB_PORT_BEHIND = [{'Rear USB port Configuration': 'Disabled'}]
    OPEN_USB_PORT_BEHIND_ONLY = [{'Rear USB port Configuration': 'Enabled'}]

    # 硬盘绑定使用
    HDD_BIND_NAME_1 = 'B4D0F0 SanDisk SDSSDH3 500G 2149LC475012'
    HDD_BIND_NAME_2 = 'B4D0F0 Samsung SSD 870 EVO 250GB S6PFNX0T330000P'
    HDD_BIND_NAME_1_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_BIND_NAME_2_OS = Msg.LEGACY_HDD_BOOT_NAME
    HDD_BIND_PROMPT = 'No binded Hdd boot will be ignored'  ################################################
    HDD_BIND1 = ['Console Redirection', 'HDD Bind', {'HDD Bind': HDD_BIND_NAME_1}]
    HDD_BIND2 = ['Console Redirection', 'HDD Bind', {'HDD Bind': HDD_BIND_NAME_2}]
    HDD_BIND3 = ['Console Redirection', 'HDD Bind', {'HDD Bind': 'No Binded'}]

    # Secure Boot
    LOC_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot']
    OPEN_SECURE_BOOT = [{'Secure Boot': 'Enabled'}, 'User Wait Time', {'Boot Mode': 'UEFI'},
                        {'Internal SHELL': 'Enabled'}]
    CLOSE_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot', 'Reset to Factory Mode']
    SECURE_MSG = 'Command Error Status: Security Violation'
    BACKUP_CMD = 'ByoShellFlash.efi bfu -bu backup.bin'
    # Quiet Boot
    OPEN_QUIET_BOOT = ['User Wait Time', {'Quiet Boot': 'Enabled'}]
    CLOSE_QUIET_BOOT = [{'Quiet Boot': 'Disabled'}]

    # SPI BIOS 锁住
    OPEN_SPI = ['User Wait Time', {'Internal SHELL': 'Enabled'}, 'Console Redirection', 'Misc Configuration',
                {'SPI BIOS Lock': 'Enabled'}]
    CLOSE_SPI = ['User Wait Time', {'Internal SHELL': 'Enabled'}, 'Console Redirection', 'Misc Configuration',
                 {'SPI BIOS Lock': 'Disabled'}]

    SPI_LOCK_MSG = 'SPI BIOS is Locked in Setup'
    # 虚拟化
    IOMMU_DISABLED_INFO = 'AMD IOMMUv2 functionality not available on this system'
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'
    SVM_DISABLED_INFO = 'kvm: disabled by bios|kvm: no hardware support'
    OS_TYPE = 'UnionTech OS'

    # IOMMU
    CLOSE_IOMMU = ['Console Redirection', 'Virtualization', {'IOMMU': 'Disabled'}]
    OPEN_IOMMU = ['Console Redirection', 'Virtualization', {'IOMMU': 'Enabled'}]

    # SVM
    CLOSE_SVM = ['Console Redirection', 'Virtualization', {'SVM': 'Disabled'}]
    OPEN_SVM = ['Console Redirection', 'Virtualization', {'SVM': 'Enabled'}]

    # SR-IOV
    CLOSE_SR = ['Console Redirection', 'Virtualization', {'SR-IOV Support': 'Disabled'}]
    OPEN_SR = ['Console Redirection', 'Virtualization', {'SR-IOV Support': 'Enabled'}]

    # 内存频率
    MEMORY_SPEED = ['667', '800', '1067', '1200', '1333']  # SetUp下可以设置的内存频率
    LOC_HYGON = ['Console Redirection', 'Hygon CBS', {'Allow setting memory frequency': 'Enabled'}]
    MEMORY_SPEED_NAME = 'Memory Clock Speed'
    LOC_MEM = [Msg.PAGE_MAIN, 'Memory Info']

    # Load Setup Defaults
    CLOSE_VIRTU = ['Console Redirection', 'Virtualization', {'IOMMU': 'Disabled'}, {'SVM': 'Disabled'},
                   {'SR-IOV Support': 'Disabled'}]
    OPEN_VIRTU = [{'IOMMU': 'Enabled'}, {'SVM': 'Enabled'}, {'SR-IOV Support': 'Enabled'}]
    LOC_VIRTU = ['Console Redirection', 'Virtualization']
    LOC_SAV_EXI = [Msg.PAGE_EXIT, 'Save and Exit']
    LOC_NO_SAV_EXI = [Msg.PAGE_EXIT, 'Discard Changes and Exit']
    VIRTUALIZATION_DEFAULT = ['Enabled', 'Enabled', 'Enabled']  # common
    # VIRTUALIZATION_DEFAULT=['Auto', 'Enabled', 'Enabled'] #baidu

    # 全刷后检查默认值
    SET_UPDATE_ALL = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Full Update'}]
    UPDATE_BIOS_PATH = [Msg.PAGE_EXIT, Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE),
                        Env.LATEST_BIOS_FILE]
    CHANGE_OPTION_VALUE = ['Console Redirection', 'Virtualization', {'IOMMU': 'Disabled'}, {'SVM': 'Disabled'},
                           {'SR-IOV Support': 'Disabled'}, 'User Wait Time', {'Internal SHELL': 'Enabled'}]
    # SATA控制器(Sata配置页面,控制器A,B所连接的硬盘)
    SATA_R_A = '\['  # 控制器A所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    SATA_R_B = '\['  # 控制器B所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    LOC_SATA = ['Console Redirection', 'SATA Configuration']
    OPEN_SATA = ['Console Redirection', 'SATA Configuration', 'Sata Controller Configuration',
                 {'Asmedia Controller 1061R_A': 'Enabled'}, {'Asmedia Controller 1061R_B': 'Enabled'}]
    CLOSE_SATA_A = ['Sata Controller Configuration', {'Asmedia Controller 1061R_A': 'Disabled'},
                    {'Asmedia Controller 1061R_B': 'Enabled'}]
    CLOSE_SATA_B = ['Sata Controller Configuration', {'Asmedia Controller 1061R_A': 'Enabled'},
                    {'Asmedia Controller 1061R_B': 'Disabled'}]
    CLOSE_SATA = ['Sata Controller Configuration', {'Asmedia Controller 1061R_A': 'Disabled'},
                  {'Asmedia Controller 1061R_B': 'Disabled'}]

    # TPM
    SET_DTPM = ['Set Administrator Password', {'TPM Select': 'DTPM'}]
    SET_FTPM = ['Set Administrator Password', {'TPM Select': 'FTPM'}]
    DTPM_MSG = 'TPM 2.0'
    FTPM_MSG = '156'
    DTPM_OS_MSG = 'NTZ0751:00: 2.0 TPM'
    FTPM_OS_MSG = 'Inspur7500|Hygon'
    CHANGE_TPM2 = ['Set Administrator Password', 'TCG2 Configuration',
                   {'TPM2 Operation': 'TPM2 ClearControl(NO) + Clear'}]
    POST_MSG = 'Press F12 to clear the TPM'
    LOC_TCG2 = ['Set Administrator Password', 'TCG2 Configuration']
    CLOSE_TPM = ['Set Administrator Password', {'TPM Select': 'Disable'}]

    # Boot Logo
    HIDE_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Enabled'}]
    SHOW_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Disabled'}]
    LOGO_PATH = './Inspur7500/Tools/Pictures/Logo'
    MANUFACTOURER = 'Inspur'

    # 联动关系
    BOOT_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}]
    UEFI_HII = 'UEFI HII Configuration'
    BOOT_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}]
    OPEN_SECURE = [{'Secure Boot': 'Enabled'}]
    CLOSE_SECURE_MSG = '<Disabled> *Secure Boot'
    CLOSE_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]
    CLOSE_PXE_STACK = ['User Wait Time', {'UEFI Network Stack': 'Disabled'}]
    LOC_UEFI_HII = ['Console Redirection', 'UEFI HII Configuration']

    # Option Rom
    OPEN_OPTION_ROM = ['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                       'User Wait Time', {'Boot Mode': 'Legacy'}, {'OPTION ROM Message': 'Enabled'}]
    CLOSE_OPTION_ROM = ['User Wait Time', {'OPTION ROM Message': 'Disabled'}]
    ONBOARD_MSG = 'WangXun\(R\)PXE|WangXun\(R\) PXE'
    ASMEDIA_MSG = 'AsmediaTechnologies|Asmedia Technologies'

    # TPCM
    OPEN_TPCM = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'}, {'Hygon TPCM': 'Enabled'}]
    CLOSE_TPCM = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'},
                  {'Hygon TPCM': 'Disabled'}]
    CLOSE_DEBUG = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Disabled'}]
    TPCM_MSG = 'TpcmVerifyRaw:Success'


class Upd:
    PASSWORDS = ['Adminbios@1', 'Usersbios@1']  # 刷BIOS前设置的密码
    BMC_LINK_OPTION = ['<Disabled>SOLforBaseboardMgmt', '<Enabled>SOLforBaseboardMgmt', '<AlwaysOff>RestoreACPowerLoss',
                       '<LastState>RestoreACPowerLoss', '<PowerOn>RestoreACPowerLoss']
    DEFAULT_OPTION_VALUE = ['<Continuetostart>Memoryerrorbehavior', '<30Days>SetPasswordValidDays',
                            '<Disabled>Power-onPassword', '[100]PasswordLockTime', '<Disable>TPMSelect',
                            '[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
                            '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
                            '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion',
                            '<Disabled>PXEBootPriority', '<FullUpdate>BIOSUpdateParameters', '<English>SelectLanguage',
                            '<Disabled>Slot1ForRetimerCard', '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan',
                            '<ALL>PrimaryGraphicsAdapter', '<Enabled>USBMassStorageSupport', '<Enabled>IOMMU',
                            '<Enabled>SVM', '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<64TB>MMIOHighLimit',
                            '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize',
                            '<Disabled>PCIEASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
                            '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode',
                            '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
                            '<Disabled>SOLforBaseboardMgmt', '<LastState>RestoreACPowerLoss',
                            '<Enabled>PlatformFirstErrorHandling', '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime',
                            '[60]LeakyBucketCount', '<Enabled>ClearmemoryCEthresholdinevery', '[10000]PCIECEThreshold',
                            '[4095]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol',
                            '<Auto>EfficiencyOptimizedMode', '<Auto>BankInterleaving', '<Disabled>SMEEControl',
                            '<Enabled>ChipselectInterleaving', '<Auto>ChannelInterleaving', '<Auto>NUMA',
                            '<Auto>MemoryInterleavingSize', '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider',
                            '<Auto>DRAMscrubtime', '<Disabled>RDSEEDandRDRANDControl', '<NoBinded>HDDBind',
                            '<Enabled>RearUSBportConfiguration', '<Enabled>FrontUSBportConfiguration',
                            '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl',
                            '<Auto>ACSEnable']  # common
    # DEFAULT_OPTION_VALUE=['<Continuetostart>Memoryerrorbehavior', '[100]PasswordLockTime', '<30Days>SetPasswordValidDays', '<Disabled>Power-onPassword', '<Disable>TPMSelect', '[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode', '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE', '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion', '<AddonFirst>PXEBootPriority', '<FullUpdate>BIOSUpdateParameters', '<English>SelectLanguage', '<Disabled>Slot1ForRetimerCard', '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan', '<PCIE>PrimaryGraphicsAdapter','<Enabled>USBMassStorageSupport', '<Auto>IOMMU', '<Enabled>SVM', '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<64TB>MMIOHighLimit', '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize','<Disabled>PCIEASPM', '<Disabled>AES', '<Enabled>HyperThreadingTechnology', '<120>MemoryCEStormThreshold','<1200>MemoryCEAccumulationThreshold','<Disabled>DebugPrintLevel','<Performance>ENERGY_PERF_BIAS_CFGmode', '<P0>CPUP-StateControl', '<Disabled>CPUC-StateControl', '<Enabled>FRB2WatchdogTimer', '<Reset>FRB2WatchdogTimerPolicy', '<10minutes>FRB2WatchdogTimerTimeout', '<Disabled>OSBootWatchdogTimer', '<Enabled>SOLforBaseboardMgmt', '<PowerOn>RestoreACPowerLoss', '<Enabled>PlatformFirstErrorHandling', '<4095>MCAErrorThresholdCount', '<Auto>MemoryClockSpeed','<Enabled>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Enabled>CorePerformanceBoost', '<Disabled>EfficiencyOptimizedMode','<Enabled>BankInterleaving','<Auto>cTDPControl','<Disabled>SMEEControl', '<Auto>ChipselectInterleaving', '<Enabled>ChannelInterleaving', '<Channel>MemoryInterleaving', '<Auto>MemoryInterleavingSize', '<Auto>Redirectscrubbercontrol', '<Performance>DeterminismSlider','<Auto>DRAMscrubtime', '<Disabled>RDSEEDandRDRANDControl','<NoBinded>HDDBind', '<Enabled>RearUSBportConfiguration', '<Enabled>FrontUSBportConfiguration', '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable'] #baidu

    # 获取BIOS选项值
    REMOVE_OPTIONS = ['BMC system log', 'UEFI HII Configuration', 'BMC system event log',
                      'Key Management']  # 读取选项时不进入的菜单

    # 修改BIOS选项
    CHANGE_PART1 = [Msg.PAGE_MAIN, 'PCIE Info', {'Slot1 For Retimer Card': 'Enabled'}, 'Console Redirection',
                    'Lan Configuration',
                    {'Onboard Ethernet Controller': 'Enabled'}, {'Wake On Lan': 'Disabled'}, 'Console Redirection',
                    'Video Configuration', {'Primary Graphics Adapter': 'IGD'}, 'Console Redirection', 'Virtualization',
                    {'IOMMU': 'Disabled'}, {'SVM': 'Disabled'}, {'SR-IOV Support': 'Disabled'}, 'Console Redirection',
                    'Misc Configuration', {'Above 4G Decoding': 'Disabled'},
                    {'MMIO High Limit': '32TB'}, {'Hide Boot Logo': 'Enabled'}, {'PCIE Max Payload Size': '512B'},
                    {'PCIE ASPM': 'L1'}, {'AES': 'Enabled'}, {'Hyper Threading Technology': 'Disabled'},
                    {'Debug Print Level': 'Debug'},
                    {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'}, {'CPU P-State Control': 'P0+P1'},
                    {'CPU C-State Control': 'Enabled'}, 'Set Administrator Password', {'TPM Select': 'FTPM'}]

    CHANGE_PART2 = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Enabled'},
                    {'FRB2 Watchdog Timer Policy': 'Power Off'},
                    {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}, {'OS Boot Watchdog Timer': 'Enabled'},
                    {'SOL for Baseboard Mgmt': 'Enabled'}, {'Restore AC Power Loss': 'Always Off'},
                    'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                    {'MCA Error Threshold Count': '100'}, {'Leaky Bucket Time': 10}, {'Leaky Bucket Count': 20},
                    {'Clear memory CE threshold in every': 'Disabled'}, {'PCIE CE Threshold': 5},
                    {'CPU CE Threshold': 200}, 'Console Redirection', 'Hygon CBS', {'Memory Clock Speed': '1333MHz'},
                    {'Downcore control': 'SIX (3 + 3)'}, {'Core Performance Boost': 'Disabled'},
                    {'Efficiency Optimized Mode': 'Disabled'}, {'Bank Interleaving': 'Disabled'},
                    {'SMEE Control': 'Disabled'},
                    {'Chipselect Interleaving': 'Disabled'}, {'Channel Interleaving': 'Enabled'}, {'NUMA': 'None'},
                    {'Memory Interleaving Size': '512 Bytes'}, {'Redirect scrubber control': 'Enabled'},
                    {'Determinism Slider': 'Power'},
                    {'DRAM scrub time': '48 hours|48hours'}, {'RDSEED and RDRAND Control': 'Enabled'},
                    'Console Redirection', 'Hygon CBS', 'Cache Prefetcher settings',
                    {'L1 Stream HW Prefetcher': 'Enable'}, {'L2 Stream HW Prefetcher': 'Enable'}, 'Console Redirection',
                    'Hygon CBS', 'NBIO Common Options',
                    {'NBIO RAS Control': 'Disabled'}, {'ACS Enable': 'Disabled'}, 'Console Redirection',
                    {'Memory error behavior': 'Shutdown System'}]

    CHANGE_PART3_1 = ['Set Administrator Password', 'Password Lock Time']
    CHANGE_PART3_2 = ['User Wait Time', {'User Wait Time': 10}, {'Bootup NumLock State': 'Off'},
                      {'Internal SHELL': 'Enabled'}, {'PXE Option Rom': 'Disabled'}]
    SET_TIME_ALWAYS = [{'Set Password Valid Days': 'Indefinite'}]

    PASSWORD_MSG = 'Please input (?:admin )*password'
    START_UPDATE_MSG = 'Reading Bios|Reading File'

    SET_UPDATE_NOR = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Reserved Configuration'}]
    SET_UPDATE_ALL = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Full Update'}]
    SETUP_LATEST = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.LATEST_BIOS_FILE]
    SETUP_PREVIOUS = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.PREVIOUS_BIOS_FILE]
    SETUP_CONSTANT = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.CONSTANT_BIOS_FILE]
    SETUP_MSG = 'Flash is updated successfully!'

    SET_DOS = [Msg.PAGE_BOOT, {'Boot Mode': 'Legacy'}]
    DOS_FLASH_TOOL = Env.DOS_FLASH_CMD
    ENT_DOS_MSG = 'Start booting from USB device...|StartbootingfromUSBdevice...'
    DOS_FLASH_CMD_LATEST_ALL = 'byoflash bfu -all latest.bin'
    DOS_FLASH_CMD_PREVIOUS_ALL = 'byoflash bfu -all previous.bin'
    DOS_FLASH_CMD_CONSTANT_ALL = 'byoflash bfu -all constant.bin'
    DOS_FLASH_CMD_LATEST = 'byoflash bfu latest.bin'
    DOS_FLASH_CMD_PREVIOUS = 'byoflash bfu previous.bin'
    DOS_FLASH_CMD_CONSTANT = 'byoflash bfu constant.bin'
    DOS_MSG_NOR = "End.....................Successed!"
    DOS_MSG_ALL = "Update ALL..................Successed!"

    OPEN_SHELL = [Msg.PAGE_BOOT, {'Boot Mode': 'UEFI'}, {'Internal SHELL': 'Enabled'}]
    SHELL_FLASH_CMD_LATEST_ALL = 'ByoShellFlash.efi bfu -all latest.bin'
    SHELL_FLASH_CMD_PREVIOUS_ALL = 'ByoShellFlash.efi bfu -all previous.bin'
    SHELL_FLASH_CMD_CONSTANT_ALL = 'ByoShellFlash.efi bfu -all constant.bin'
    SHELL_FLASH_CMD_LATEST = 'ByoShellFlash.efi bfu latest.bin'
    SHELL_FLASH_CMD_PREVIOUS = 'ByoShellFlash.efi bfu previous.bin'
    SHELL_FLASH_CMD_CONSTANT = 'ByoShellFlash.efi bfu constant.bin'
    SHELL_MSG_NOR = "End.....................Successed!|BIOS has been updated"
    SHELL_MSG_ALL = "Update ALL..................Successed!|BIOS has been updated"

    LINUX_FLASH_CMD_LATEST_ALL = f'./flash bfu -all {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./flash bfu -all {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_FLASH_CMD_CONSTANT_ALL = f'./flash bfu -all {Env.LINUX_BIOS_MOUNT_PATH}constant.bin'
    LINUX_FLASH_CMD_LATEST = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_FLASH_CMD_CONSTANT = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}constant.bin'
    LINUX_MSG_NOR = "End.....................Successed!|BIOS has been updated"
    LINUX_MSG_ALL = "Update ALL..................Successed!|BIOS has been updated"

    WINDOWS_FLASH_TOOL = Env.WINDOWS_FLASH_CMD
    WINDOWS_MSG_NOR = "End.....................Successed!"
    WINDOWS_MSG_ALL = "Update ALL..................Successed!"

    SETUP_OTHERS = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.OTHERS_BIOS_FILE]
    SETUP_UNSIGNED = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.UNSIGNED_BIOS_FILE]
    SHELL_FLASH_CMD_OTHERS = 'ByoShellFlash.efi bfu others.bin'
    SHELL_FLASH_CMD_UNSIGNED = 'ByoShellFlash.efi bfu unsigned.bin'
    LINUX_FLASH_CMD_OTHERS = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'
    UPDATE_OTHERS_MSG_SETUP = 'File Not Match'
    UPDATE_UNSIGNED_MSG_SETUP = 'BIOS Verify Sign Fail'
    UPDATE_OTHERS_MSG_LINUX = 'BIOSID is not matched'
    UPDATE_UNSIGNED_MSG_LINUX = 'Sign Verify.*Failed'
    UPDATE_OTHERS_MSG_SHELL = 'BIOSID is not matched'
    UPDATE_UNSIGNED_MSG_SHELL = 'Sign Verify.*Failed'


class Rfs:
    CURRECT_VALUE = 'Inspur7500\\Tools\\currectvalue.json'
    CHANGE_OPTIONS_FILE = 'Inspur7500\\Tools\\changevalue.json'
    REGISTRY_FILE = 'Inspur7500\\Tools\\registry.json'
    DEPENDENCE_FILE = 'Inspur7500\\Tools\\dependence.json'
    REGISTRY_FILE_PATH = 'Inspur7500\\Tools\\'
    BIOS_PATH_LATEST = 'Inspur7500\\Tools\\BIOS\\latest.bin'
    BIOS_PATH_PREVIOUS = 'Inspur7500\\Tools\\BIOS\\previous.bin'
    PASSWORDS = ['Admin@1122', 'Users@1122']


class Tool:
    pass


class Sec:
    pass


class Ras:
    CLOSE_PFEH = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Disabled'}]
    SET_MEM_THRESHOLD_10 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 1440}]
    SET_MEM_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                           {'MCA Error Threshold Count': '1'}]
    SET_MEM_THRESHOLD_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                           {'MCA Error Threshold Count': '0'}]
    SET_MEM_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                             {'MCA Error Threshold Count': '4095'}, {'Leaky Bucket Time': 1440}]
    SET_DEBUG = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'}]
    OPEN_PFEH = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Disabled'},
                 'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'}]
    SET_LEAKY_BUCKET_1 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 39}, {'Leaky Bucket Count': 4}]
    SET_LEAKY_BUCKET_2 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 132}, {'Leaky Bucket Count': 15}]
    SET_LEAKY_BUCKET_3 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 26}, {'Leaky Bucket Count': 3}]
    SET_LEAKY_BUCKET_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                          {'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 0}]
    SET_PCIE_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'PCIE CE Threshold': 1}]
    SET_PCIE_THRESHOLD_2 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'PCIE CE Threshold': 2}]
    SET_PCIE_THRESHOLD_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'PCIE CE Threshold': 0}]
    SET_PCIE_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                              {'PCIE CE Threshold': 10000}]
    SET_CPU_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                           {'CPU CE Threshold': 1}]
    SET_CPU_THRESHOLD_10 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'CPU CE Threshold': 10}]
    SET_CPU_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                             {'CPU CE Threshold': 4095}]
    RAS_DICT = {
        #   eventdata  du
        '0d': '00',  # CPU0_D1
        '09': '01',  # CPU0_C1
        '01': '10',  # CPU0_A1
        '05': '11',  # CPU0_B1
        '2d': '20',  # CPU1_D1
        '29': '21',  # CPU1_C1
        '21': '30',  # CPU1_A1
        '25': '31',  # CPU1_B1

    }
