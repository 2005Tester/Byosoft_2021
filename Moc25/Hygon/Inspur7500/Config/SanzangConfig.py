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
from Inspur7500.Config.PlatConfig import Key


class Env:
    # Report Setting
    PROJECT_NAME = "Inspur7500"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "Inspur7500\\Report\\template"

    TESTCASE_CSV = "Inspur7500\\AllTest2.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\Sanzang\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com6"

    # BMC Configuration
    BMC_IP = '192.168.6.32'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.230'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    OS_IP_LEGACY = '192.168.6.230'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    # Tool definition - Ver 1.8.18
    IPMITOOL = "Inspur7500\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER,
                                                                                                  BMC_PASSWORD)
    SMBIOS = "Inspur7500\\Tools\\smbiossanzang\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sdd4"
    LINUX_USB_MOUNT = "/mnt/"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs3:"
    USB_VOLUME = "USB:Kingston DataTraveler 2.0 \(P4\)"

    # BIOS flash command
    BIOS_FILE = 'Sanzang'
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
    POST_MESSAGE = 'DEL to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot'
    HOTKEY_PROMPT_DEL = 'DEL to enter SETUP'
    HOTKEY_PROMPT_F11 = ' Press F11 to enter Boot Menu'
    HOTKEY_PROMPT_F12 = 'Press F12 to PXE boot'

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

    # Menus of boot page
    ENTER_BOOTMENU = "Startup Device Menu|ENTER to select boot device"
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: Kingston DataTraveler 2.0'
    SHELL = "Internal EDK Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun Gigabit Server Adapter WX1860NCSI PXE IPv4|UEFI Onboard: Port 0 - WangXun Gigabit Server Adapter WX1860NCSI-2 PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun Gigabit Server Adapter WX1860NCSI PXE IPv4|UEFI Onboard: Port 1 - WangXun Gigabit Server Adapter WX1860NCSI-2 PXE IPv4"
    LEGACY_HDD_BOOT_NAME = "SATA1-7: Samsung SSD 870 EVO 250GB|UEFI SATA1-7: Samsung SSD 870 EVO 250GB"  # Legacy系统盘在Legacy,UEFI模式下启动名
    UEFI_HDD_BOOT_NAME = 'UOS\(UEFI SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C\)|UEFI SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C'  # UEFI系统盘在Legacy,UEFI模式下启动名
    LINUX_OS = 'UOS\(UEFI SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C\)|NVME\(PCI1-0-0\): Samsung SSD 980 250GB'  # UEFI系统盘在UEFI模式启动名，Legacy系统盘在Legacy模式下启动名


class Boot:
    SERVICE_CONFIG = [Msg.PAGE_ADVANCED, Msg.SERVER_CONFIG]
    LOC_USB = [Msg.PAGE_ADVANCED, Msg.USB_CONFIG]
    LOC_HDD = [Msg.PAGE_BOOT, Msg.HDD_BOOT_NAME]
    CPU_INFO = [Msg.CPU_INFO]
    MEM_INFO = [Msg.MEM_INFO]
    ONBOARD_ETH = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]
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
    CPU_FREQUENCY = ['1200', '1600', '2000']  # SetUp下可以设定的CPU频率
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
    CPU_FREQUENCY_PSTATE = ['2.50', '1.60', '1.20']  # 海光工具检测，P0、P1、P2 CPU频率
    SET_PSTATE_P0 = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                     {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Disabled'},
                     {'Set CPU Speed': '{0} MHz'.format(CPU_FREQUENCY[-1])}]
    SET_PSTATE_P0P1 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1'}]
    SET_PSTATE_P0P1P2 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1+P2'}]
    SET_HIGH = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'Performance'}]

    # CPU 降核
    CPU_DOWNCORE_CORE = ['8', '8', '12', '16', '16', '24']  # CPU降核
    DOWNCORE_VALUES = ['TWO (1 + 1)', 'TWO (2 + 0)', 'THREE (3 + 0)', 'FOUR (2 + 2)', 'FOUR (4 + 0)', 'SIX (3 + 3)']
    LOC_DOWNCORE = ['Console Redirection', 'Hygon CBS']
    DOWNCORE_NAME = 'Downcore control'
    SET_DOWNCORE_AUTO = ['Console Redirection', 'Hygon CBS', {'Downcore control': 'Auto'}]

    # CPU AES
    CLOSE_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Disabled'}]
    OPEN_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Enabled'}]

    # CPU NUMA
    NUMA_VALUES = ['Socket', 'None', 'Channel', 'Die', 'Auto']
    CPU_NUMA_ONE = ['1', '4', '4', '1', '4']  # NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO = ['1', '8', '8', '2', '8']  # NUMA双路CPU分别对应插槽、没有、通道、裸片、自动
    LOC_NUMA = ['Console Redirection', 'Hygon CBS']
    NUMA_NAME = 'NUMA'

    # CPU CPB
    CPU_FREQUENCY_CPB = ['2.00', '3.00']  # 海光工具检测,超频关闭，打开下CPU频率
    CLOSE_CPB = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                 {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Enabled'},
                 {'Set CPU Speed': '{0} MHz'.format(CPU_FREQUENCY[-1])}, 'Console Redirection', 'Hygon CBS',
                 {'Core Performance Boost': 'Disabled'}]
    OPEN_CPB = ['Console Redirection', 'Hygon CBS', {'Core Performance Boost': 'Auto|Enabled'}]
    LOC_CPU_SPEED = ['Console Redirection', 'Misc Configuration']

    LOC_PERFORMANCE = ['Console Redirection', 'Misc Configuration']
    PERFORMANCE_NAME = 'ENERGY_PERF_BIAS_CFG mode'
    PERFORMANCE_VALUE_NAME = ['Energy', 'Energy Balance', 'Performance Balance', 'Performance']  # 支持修改的值
    VALUE_CPU_SPEED = ['1.20', '1.60', '2.00', '2.50']  # 每个值对应的CPU频率
    LOC_CPB = ['Console Redirection', 'Hygon CBS']
    CPB_NAME = 'Core Performance Boost'

    # SMEE控制
    OPEN_SMEE = ['Console Redirection', 'Hygon CBS', {'SMEE Control': 'Enabled'}]
    CLOSE_SMEE = ['Console Redirection', 'Hygon CBS', {'SMEE Control': 'Disabled'}]
    SMEE_MSG = 'Secure Memory Encryption \(SME\) active'


class Psw:
    PAGE_ALL = ['BIOS Info', 'Console Redirection', 'Set User Password', 'Shutdown System']  # 用户密码登录，SetUp页面名

    TRY_COUNTS = 3  # 输错密码重试次数,3代表输错3次后，第4次输错会被锁定

    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = 'NVME\(PCI1-0-0\): Samsung SSD 980 250GB \(TCG-OPAL\)'
    HDD_PASSWORD_NAME_02 = 'SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C'
    HDD_NAME_01_OS = 'Windows Boot Manager\(UEFI NVME\(PCI1-0-0\): Samsung SSD 980 250GB\)'
    HDD_NAME_02_OS = 'UOS\(UEFI SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C\)'

    HASH_NAME = 'Set HddPassword Hash Type'
    HASH_TYPE = ['SHA-256 Hash', 'SM3 Hash']
    ENABLE_HDD_NAME = 'Enable NVMe Admin Password|Enable HDD User Password'
    ERASE_NAME = 'Security Erase NVMe Data|Security Erase HDD Data'
    DISABLE_PSW_NAME = 'Disable HDD Password|Disable NVMe Password'
    CHANGE_ADMIN_NAME = 'Change NVMe Admin Password|Change HDD Master Password'
    CHANGE_USER_NAME = 'Change HDD User Password|Change NVMe User Password'
    HDD_PSW_STATUS_INSTALLED = 'Set hard disk password:Installed'
    HDD_PSW_STATUS_NOT_INSTALLED = 'Set hard disk password:Not Installed'
    HDD_LOCK_MSG = "The hard drive's security state cannot be changed"
    POST_HDD_MSG = 'Enter HDD Password'

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
    PWS_NOT_SET_STATUS = 'Not Installed|Uninstalled'
    POWER_ON_PSW_OPTION = 'Power-on Password'
    PSW_EXPIRY_DATE = 'Password Valid Days'
    HDD_PSW_OPTION = 'HDD Password'
    SET_HDD_PSW_OPTION = 'Enable HDD Password|Enable HDD User Password'
    DEL_HDD_PSW_OPTION = 'Disable HDD Password|Disable HDD User Password'
    LOGIN_HDD_PSW_PROMPT = 'Enter HDD Password'
    HDD_LOCK_STATUS = 'security state cannot be changed'
    SET_HDD_HASH_TYPE1 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SHA-256 Hash'}]
    SET_HDD_HASH_TYPE2 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SM3 Hash'}]
    LOC_HDD_PSW = [SET_ADMIN_PSW, HDD_PSW_OPTION]
    LOC_USER_PSW = [SET_ADMIN_PSW, SET_USER_PSW]
    LOC_ADMIN_PSW = [SET_ADMIN_PSW]
    LOC_LOCK_OPTION = [SET_ADMIN_PSW, PSW_LOCK_OPTION]
    SET_TIME_WEEK = [{'Password Valid Days': '7 Days'}]
    SET_TIME_MONTH = [{'Password Valid Days': '30 Days'}]
    SET_TIME_ALWAYS = [{'Password Valid Days': 'Indefinite'}]


class Ipm:
    # Frb2_watchdog
    CLOSE_FRB = ['Console Redirection', 'Server Management', {'FRB2 Watchdog Timer': 'Disabled'}]
    OPEN_FRB1 = ['Console Redirection', 'Server Management', {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '10minutes|10 minutes'}]
    OPEN_FRB2 = ['Console Redirection', 'Server Management', {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Power Off'}, {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_FRB3 = ['Console Redirection', 'Server Management', {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '5minutes|5 minutes'}]

    # OS watchdog
    OPEN_OS_WDOG1 = ['Console Redirection', 'Server Management', {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Power Off'}, {'OS Watchdog Timer Timeout': '10minutes|10 minutes'}]
    OPEN_OS_WDOG2 = ['Console Redirection', 'Server Management', {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_OS_WDOG3 = ['Console Redirection', 'Server Management', {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '5minutes|5 minutes'}]
    CLOSE_OS_WDOG = ['Console Redirection', 'Server Management', {'OS Boot Watchdog Timer': 'Disabled'}]

    # Power Loss
    SET_POWER_LOSS1 = ['Console Redirection', 'Server Management', {'Restore AC power loss': 'Power On'}]
    SET_POWER_LOSS2 = ['Console Redirection', 'Server Management', {'Restore AC power loss': 'Last State'}]
    SET_POWER_LOSS3 = ['Console Redirection', 'Server Management', {'Restore AC power loss': 'Stay Off'}]
    LOC_SERVICE = ['Console Redirection', 'Server Management']
    POWER_LOSS_OPTION = 'Restore AC power loss'
    POWER_LOSS_VALUE = ['<Power On>', '<Last State>', '<Stay Off>']

    # OEM
    OPTION_VALUE = {'HyperThread': [1, {'Enabled': ['0', '1'], 'Disabled': ['0', '0']}],
                    'SR-IOV': [1, {'Enabled': ['1', '0'], 'Disabled': ['1', '1']}],
                    'VMX': [1, {'Enabled': ['2', '1'], 'Disabled': ['2', '0']}],
                    'IOMMU': [1, {'Enabled': ['3,4', '01'], 'Disabled': ['3,4', '00'], 'Auto': ['3,4', '10']}],
                    'RDSEED': [1, {'Enabled': ['5', '1'], 'Disabled': ['5', '0']}],
                    'PXEPriority': [1, {'Disabled': ['6,7', '00'], 'Onboard': ['6,7', '01'], 'Addon': ['6,7', '10']}],

                    'NUMA': [2, {'None': ['0,2', '000'], 'Channel': ['0,2', '001'], 'Die': ['0,2', '010'],
                                 'Socket': ['0,2', '011'],
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
                                     {'2000MHz': ['4,5', '00'], '1600MHz': ['4,5', '01'], '1200MHz': ['4,5', '10']}],

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
            'RearUSB': 'RearUSBPortConfiguration', 'FrontUSB': 'FrontUSBPortConfiguration',
            'USBStorage': 'USBMassStorageSupport', 'MaxPayload': 'PCIEMaxPayloadSize', 'ASPM': 'PCIEASPM',
            'Property': 'ENERGY_PERF_BIAS_CFGmode', 'CPUP-State': 'CPUP-StateControl',
            'CPUC-State': 'CPUC-StateControl', 'CPUFrequency': 'SetCPUSpeed', 'QuietBoot': 'QuietBoot',
            'NumLock': 'BootupNumLockState', 'OptionRom': 'OPTIONROMMessage', 'UEFIShell': 'InternalSHELL',
            'NetworkStack': 'UEFINetworkStack', 'PXERetry': 'PXEBootOptionsRetry', 'WaitTime': 'UserWaitTime',
            'FRB2': 'FRB2WatchdogTimer', 'AES': 'AES'}
    # oem命令修改的SetUp选项
    CHANGE_OPTION_VALUE1 = ['HyperThread:Disabled', 'SR-IOV:Disabled', 'VMX:Disabled', 'IOMMU:Disabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:None', 'Turbo:Disabled', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:Ipv6',
                            'PFEH:Disabled', 'MCACount:0', 'OnLan:Disabled', 'WakeOnLan:Disabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:512B',
                            'ASPM:L1', 'Perfmode:Performance', 'CPUP-State:P0', 'CPUC-State:Disabled',
                            'NumLock:Off', 'OptionRom:Enabled', 'UEFIShell:Enabled',
                            'NetworkStack:Enabled', 'PXERetry:Disabled', 'WaitTime:14', 'First:PXE', 'Second:HDD',
                            'Third:ODD', 'Fourth:USB', 'Fifth:Others', 'FRB2:Disabled', 'AES:Disabled']

    CHANGE_OPTION_VALUE2 = ['HyperThread:Enabled', 'SR-IOV:Enabled', 'VMX:Enabled', 'IOMMU:Enabled', 'RDSEED:Disabled',
                            'PXEPriority:Addon', 'NUMA:Channel', 'Turbo:Auto', 'PXE:Enabled', 'SPILock:Disabled',
                            'HideBootLogo:Disabled', 'BootMode:Legacy', 'IPVersion:Ipv4', 'PFEH:Enabled', 'MCACount:10',
                            'OnLan:Enabled', 'WakeOnLan:Enabled', 'Graphic:PCIE', 'RearUSB:Enabled', 'FrontUSB:Enabled',
                            'USBStorage:Enabled', 'MaxPayload:128B', 'ASPM:Disabled', 'Perfmode:PerfBalance',
                            'CPUP-State:P0', 'NumLock:On', 'OptionRom:Disabled', 'UEFIShell:Disabled',
                            'NetworkStack:Disabled', 'PXERetry:Enabled',
                            'WaitTime:25', 'First:USB', 'Second:ODD', 'Third:PXE', 'Fourth:HDD', 'Fifth:Others',
                            'FRB2:Enabled', 'AES:Disabled']

    CHANGE_OPTION_VALUE3 = ['HyperThread:Disabled', 'SR-IOV:Disabled', 'VMX:Disabled', 'IOMMU:Disabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:Die', 'Turbo:Disabled', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:All',
                            'PFEH:Disabled', 'MCACount:0', 'OnLan:Disabled', 'WakeOnLan:Disabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:256B',
                            'ASPM:L1', 'Perfmode:EnergyBalance', 'CPUP-State:P0+P1', 'NumLock:Off', 'OptionRom:Enabled',
                            'UEFIShell:Enabled',
                            'NetworkStack:Disabled', 'PXERetry:Disabled', 'WaitTime:14', 'First:ODD', 'Second:PXE',
                            'Third:HDD', 'Fourth:USB', 'Fifth:Others', 'FRB2:Disabled', 'AES:Enabled']

    CHANGE_OPTION_VALUE4 = ['HyperThread:Enabled', 'SR-IOV:Enabled', 'VMX:Enabled', 'IOMMU:Enabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:Die', 'Turbo:Disabled', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:All',
                            'PFEH:Disabled', 'MCACount:0', 'OnLan:Disabled', 'WakeOnLan:Enabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:Auto',
                            'ASPM:L1', 'Perfmode:Energy', 'CPUP-State:P0+P1+P2', 'NumLock:Off', 'OptionRom:Enabled',
                            'UEFIShell:Enabled', 'NetworkStack:Disabled', 'PXERetry:Disabled', 'WaitTime:131',
                            'First:USB', 'Second:HDD', 'Third:ODD', 'Fourth:PXE', 'Fifth:Others', 'FRB2:Enabled',
                            'AES:Enabled']

    CHANGE_OPTION_VALUE5 = ['HyperThread:Disabled', 'SR-IOV:Disabled', 'VMX:Disabled', 'IOMMU:Disabled',
                            'RDSEED:Enabled', 'PXEPriority:Onboard', 'NUMA:None', 'Turbo:Disabled', 'PXE:Enabled',
                            'SPILock:Enabled', 'HideBootLogo:Enabled', 'BootMode:UEFI', 'IPVersion:Ipv6',
                            'PFEH:Disabled', 'MCACount:0', 'OnLan:Disabled', 'WakeOnLan:Disabled', 'Graphic:IGD',
                            'RearUSB:Disabled', 'FrontUSB:Disabled', 'USBStorage:Disabled', 'MaxPayload:512B',
                            'ASPM:L1', 'Perfmode:UserDefined', 'CPUP-State:P0+P1', 'CPUC-State:Enabled',
                            'CPUFrequency:1200MHz', 'NumLock:Off', 'OptionRom:Enabled', 'UEFIShell:Enabled',
                            'NetworkStack:Enabled', 'PXERetry:Disabled', 'WaitTime:32', 'First:PXE', 'Second:HDD',
                            'Third:ODD', 'Fourth:USB', 'Fifth:Others', 'FRB2:Enabled', 'AES:Disabled']
    CHANGE_OPTION_VALUE = [CHANGE_OPTION_VALUE1, CHANGE_OPTION_VALUE2, CHANGE_OPTION_VALUE3, CHANGE_OPTION_VALUE4,
                           CHANGE_OPTION_VALUE5]

    # BMC USRE
    ADD_USER = 'Add User'
    DEL_USER = 'Delete User'
    CHANGE_USER = 'Change User'
    USER_NAME = 'User Name'
    USER_PSW = 'User Password'
    CNANGE_USER_PSW = 'Change user Password'
    USER_PRIVILEGE = 'Privilege'
    CALLBACK = 'Callback'
    USER = 'User'
    OPERATOR = 'Operator'
    ADMIN = 'Administrator'
    NO_ACCESS = 'No Access'
    USER_STATE = 'User Status '
    DISABLE = 'Disabled'
    ENABLE = 'Enabled'
    USER_NAME_NOT_MATCH = 'Contains at least 5 characters|Please enter enough characters'
    USER_NAME_EXITS = 'Username does not conform to specifications or already exists'
    ERROR_PSW = 'Wrong Password'
    DEL_USER_SUCCESS = 'Delete user success'
    SET_PSW_SUCCESS = 'Setting Successfully|Password Set Successfully'
    LOC_USER_CONF = ['Console Redirection', 'Server Management', 'BMC User Configuration']

    # IPMITOOL 启动
    OS_MSG = 'Kylin|Tencent|CentOS|UOS|Windows'
    UEFI_PXE_MSG = 'Checking Media Presence...'
    LEGACY_PXE_MSG = 'PXE initialising devices...|PXEinitialisingdevices...'
    BOTH_PXE_MSG = 'PXE initialising devices...|Checking Media Presence...|PXEinitialisingdevices...'
    UEFI_USB_MSG = 'UEFI Interactive Shell'
    LEGACY_USB_MSG = 'Start booting from USB device|StartbootingfromUSBdevice'
    BOTH_USB_MSG = 'Start booting from USB device|UEFI Interactive Shell|StartbootingfromUSBdevice'

    OPEN_LAN = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]
    OPEN_PXE = [{'PXE Option Rom': 'Enabled'}]
    BOOT_MODE_UEFI = [{'Boot Mode': 'UEFI'}]
    BOOT_MODE_LEGACY = [{'Boot Mode': 'Legacy'}]
    OPEN_SHELL = [{'Internal SHELL': 'Enabled'}]

    # 板载SOL
    CLOSE_SOL = ['Console Redirection', 'Server Management', {'SOL for Baseboard Mgmt': 'Disabled'}]
    OPEN_SOL = ['Console Redirection', 'Server Management', {'SOL for Baseboard Mgmt': 'Enabled'}]

    # BMC系统日志
    LOC_SYS_LOG = ['Console Redirection', 'Server Management', 'BMC system event log']

    # FRU
    LOC_FRU = ['Console Redirection', 'Server Management', 'FRU Information']
    CLEAR_FRU = ['Console Redirection', 'Server Management', 'Clear System Event Log']


class Pci:
    OPEN_LAN = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]

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
    CLOSE_PXE = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                 'User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]

    # PXE 启动
    SET_IPV4 = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'}, {'Net Boot IP Version': 'IPv4'}]
    SET_IPV6 = ['User Wait Time', {'Net Boot IP Version': 'IPv6'}]
    SET_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}, {'PXE Option Rom': 'Enabled'}]
    SET_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}]

    # PXE 重试
    CLOSE_PXE_RETRY = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                       {'PXE Boot Options Retry': 'Disabled'},
                       {'Net Boot IP Version': 'IPv4'}]
    OPEN_PXE_RETRY = ['User Wait Time', {'PXE Boot Options Retry': 'Enabled'}]
    PXE_RETRY_MSG = 'UEFI Onboard: Port 1 \- WangXun Gigabit Server Adapter WX1860NCSI\-2 HTTP IPv4'

    # LegacyPXE 重试
    CLOSE_PXE_RETRY_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}, {'PXE Option Rom': 'Enabled'},
                              {'PXE Boot Options Retry': 'Disabled'}]
    OPEN_PXE_RETRY_LEGACY = ['User Wait Time', {'PXE Boot Options Retry': 'Enabled'}]
    PXE_RETRY_MSG_LEGACY = 'WangXun\(R\) *PXE *\(PCI02:00.0\)|WangXun\(R\) *PXE *\(PCI01:00.0\)'

    # PXE IP 版本
    SET_IPV4_6 = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                  'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                  {'Net Boot IP Version': 'IPv4 and IPv6'}]

    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun Gigabit Server Adapter WX1860NCSI (02-02-03-04-05-06)"
    PXE_NET_ADDON = "Intel(R) Ethernet Converged Network Adapter X710 (40-A6-B7-1B-72-E4)"
    # PXE_NET_ADDON = "Inspur(R) Ethernet Controller X550 (B4-05-5D-16-7C-2E)"
    # PXE_NET_ADDON = 'Intel(R) Ethernet Controller 10 Gigabit X540-AT2 (E8-61-1F-29-D8-85)'

    # PXE启动项(IPv4)
    # PXE_PORT_ADDON =  'UEFI Slot \d+: Port \d+ - Intel\(R\) Ethernet Controller 10 Gigabit (?:X540-AT2|X540-AT2-2) (?:PXE|HTTP) IPv4'
    # PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d+ - Inspur\(R\) Ethernet Controller (?:X550|X550-2) (?:PXE|HTTP) IPv4'
    PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d+ - Intel\(R\) Ethernet Converged Network Adapter (?:X710|X710-2) (?:PXE|HTTP) IPv4'
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun Gigabit Server Adapter (?:WX1860NCSI|WX1860NCSI-2) (?:PXE|HTTP) IPv4"
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

    # Higest Boot Priority
    HIGHEST_DEVICE = 'UEFI Slot \d+: Port \d+ - Intel\(R\) Ethernet Converged Network Adapter (?:X710|X710-2) (?:PXE|HTTP) IPv4'
    OPEN_HIGHEST_DEVICE = ['User Wait Time',{'Highest Boot Priority Device':'Enabled'}]
    CLOSE_HIGHEST_DEVICE = ['User Wait Time',{'Highest Boot Priority Device':'Disabled'}]


class Sup:
    # Interface_information
    NECESSARY_MSG = ['BIOS Vendor', 'BIOS Core Version', 'Mother Board Info', 'CPU Info', 'Memory Info',
                     'System Date and Time',
                     'PCIE Info', 'USB Configuration', 'Console Redirection', 'Set Administrator Password',
                     'Set User Password',
                     'HDD Password', 'User Wait Time',
                     'PXE Option Rom', 'Boot Order', 'Save and Exit', 'Load Setup Defaults', 'BIOS Update Parameters',
                     'Shutdown System', 'Reboot System']

    # Onboard Lan Configuration
    CLOSE_LAN = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Disabled'},
                 'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                 {'Net Boot IP Version': 'IPv4'}]
    LOC_PCI_INFO = [Msg.PAGE_MAIN, 'PCIE Info', 'PCI Device Info']
    OPEN_LAN = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]

    # 网络唤醒
    MAC_ADDRESS = '02-02-03-04-05-06|02-02-03-04-05-07'
    CLOSE_WAKE_ONLINE = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                         {'Wake On Lan': 'Disabled'}]
    OPEN_WAKE_ONLINE = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                        {'Wake On Lan': 'Enabled'}]

    # USB 存储设备支持
    CLOSE_USB_STORAGE = ['User Wait Time', {'Boot Mode': 'UEFI'}, 'Console Redirection', 'USB Configuration',
                         {'USB Mass Storage Support': 'Disabled'}, 'USB Port Configuration',
                         {'Rear USB Port Configuration': 'Enabled'}, {'Front USB Port Configuration': 'Enabled'}]
    OPEN_USB_STORAGE = ['Console Redirection', 'USB Configuration', {'USB Mass Storage Support': 'Enabled'}]

    # USB 端口配置
    OPEN_USB_PORT_BOTH = ['Console Redirection', 'USB Configuration', {'USB Mass Storage Support': 'Enabled'},
                          'USB Port Configuration', {'Rear USB Port Configuration': 'Enabled'},
                          {'Front USB Port Configuration': 'Enabled'}]
    LOC_USB_INFO = ['Console Redirection', 'USB Configuration']
    OPEN_USB_PORT_FRONT = [{'Rear USB Port Configuration': 'Disabled'}, {'Front USB Port Configuration': 'Enabled'}]
    OPEN_USB_PORT_BEHIND = [{'Rear USB Port Configuration': 'Enabled'}, {'Front USB Port Configuration': 'Disabled'}]
    CLOSE_USB_PORT_BOTH = [{'Rear USB Port Configuration': 'Disabled'}, {'Front USB Port Configuration': 'Disabled'}]
    OPEN_USB_PORT_ALL = [{'Rear USB Port Configuration': 'Enabled'}, {'Front USB Port Configuration': 'Enabled'}]
    CLOSE_USB_PORT_FRONT = [{'Front USB Port Configuration': 'Disabled'}]
    OPEN_USB_PORT_FRONT_ONLY = [{'Front USB Port Configuration': 'Enabled'}]
    CLOSE_USB_PORT_BEHIND = [{'Rear USB Port Configuration': 'Disabled'}]
    OPEN_USB_PORT_BEHIND_ONLY = [{'Rear USB Port Configuration': 'Enabled'}]

    # HDD Bind
    HDD_BIND_NAME_1 = 'B6D0F2 SAMSUNG MZ7L3480HCHQ- S6KLNE0RA02530'
    HDD_BIND_NAME_2 = 'B6D0F2 Samsung SSD 870 EVO 2 S6PFNX0T330003J'
    HDD_BIND_NAME_1_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_BIND_NAME_2_OS = Msg.LEGACY_HDD_BOOT_NAME
    HDD_BIND_PROMPT = 'Hdd has been changed'  ################################################
    HDD_BIND1 = ['Console Redirection', 'HDD Bind', {'HDD Bind': HDD_BIND_NAME_1}]
    HDD_BIND2 = ['Console Redirection', 'HDD Bind', {'HDD Bind': HDD_BIND_NAME_2}]
    HDD_BIND3 = ['Console Redirection', 'HDD Bind', {'HDD Bind': 'Unbind'}]

    # Secure Boot
    LOC_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot']
    OPEN_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot', {'Secure Boot Default Key Provision': 'Auto'},
                        'User Wait Time', {'Boot Mode': 'UEFI'},
                        {'Internal SHELL': 'Enabled'}]
    CLOSE_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot', {'Secure Boot Default Key Provision': 'Manual'},
                         'Attempt Secure Boot']
    SECURE_MSG = 'Command Error Status: Security Violation'
    BACKUP_CMD = 'ByoFlash.efi -bu backup.bin'
    # Quiet Boot
    OPEN_QUIET_BOOT = ['User Wait Time', {'Quiet Boot': 'Enabled'}]
    CLOSE_QUIET_BOOT = [{'Quiet Boot': 'Disabled'}]

    # SPI BIOS 锁住
    OPEN_SPI = ['User Wait Time', {'Internal SHELL': 'Enabled'}, 'Console Redirection', 'Misc Configuration',
                {'SPI BIOS Lock': 'Enabled'}]
    CLOSE_SPI = ['User Wait Time', {'Internal SHELL': 'Enabled'}, 'Console Redirection', 'Misc Configuration',
                 {'SPI BIOS Lock': 'Disabled'}]
    SPI_LOCK_MSG = 'SPI BIOS is Locked in Setup|It is locked|Flash is locked'
    # 虚拟化
    IOMMU_DISABLED_INFO = 'AMD IOMMUv2 functionality not available on this system'
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'
    SVM_DISABLED_INFO = 'kvm: disabled by bios|kvm: no hardware support'
    OS_TYPE = 'UnionTech OS'

    # IOMMU
    CLOSE_IOMMU = ['Console Redirection', 'Virtualization Configuration', {'IOMMU': 'Disabled'}]
    OPEN_IOMMU = ['Console Redirection', 'Virtualization Configuration', {'IOMMU': 'Enabled'}]

    # SVM
    CLOSE_SVM = ['Console Redirection', 'Virtualization Configuration', {'SVM': 'Disabled'}]
    OPEN_SVM = ['Console Redirection', 'Virtualization Configuration', {'SVM': 'Enabled'}]

    # SR-IOV
    CLOSE_SR = ['Console Redirection', 'Virtualization Configuration', {'SR-IOV Support': 'Disabled'}]
    OPEN_SR = ['Console Redirection', 'Virtualization Configuration', {'SR-IOV Support': 'Enabled'}]

    # 内存频率
    MEMORY_SPEED = ['667', '800', '1067', '1200', '1333']  # SetUp下可以设置的内存频率
    LOC_HYGON = ['Console Redirection', 'Hygon CBS', {'Allow setting memory frequency': 'Enabled'}]
    MEMORY_SPEED_NAME = 'Memory Clock Speed'
    LOC_MEM = [Msg.PAGE_MAIN, 'Memory Info']

    # Load Setup Defaults
    CLOSE_VIRTU = ['Console Redirection', 'Virtualization Configuration', {'IOMMU': 'Disabled'}, {'SVM': 'Disabled'},
                   {'SR-IOV Support': 'Disabled'}]
    OPEN_VIRTU = [{'IOMMU': 'Enabled'}, {'SVM': 'Enabled'}, {'SR-IOV Support': 'Enabled'}]
    LOC_VIRTU = ['Console Redirection', 'Virtualization Configuration']
    LOC_SAV_EXI = [Msg.PAGE_EXIT, 'Save and Exit']
    LOC_NO_SAV_EXI = [Msg.PAGE_EXIT, 'Discard Changes and Exit']
    VIRTUALIZATION_DEFAULT = ['Enabled', 'Enabled', 'Enabled']

    # 全刷后检查默认值
    SET_UPDATE_ALL = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Full Update'}]
    UPDATE_BIOS_PATH = [Msg.PAGE_EXIT, Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE),
                        Env.LATEST_BIOS_FILE]
    CHANGE_OPTION_VALUE = ['Console Redirection', 'Virtualization Configuration', {'IOMMU': 'Disabled'},
                           {'SVM': 'Disabled'}, {'SR-IOV Support': 'Disabled'}, 'User Wait Time',
                           {'Internal SHELL': 'Enabled'}]
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
    POST_MSG = "Press F12 to clear this computer's TPM"
    LOC_TCG2 = ['Set Administrator Password', 'TCG2 Configuration']
    CLOSE_TPM = ['Set Administrator Password', {'TPM Select': 'Disabled|Disable'}]

    # TPM Plus
    CLOSE_TPM_STATE = ['Set Administrator Password', 'TCG2 Configuration', {'TPM State': 'Disabled'}]
    OPEN_TPM_STATE = ['Set Administrator Password', 'TCG2 Configuration', {'TPM State': 'Enabled'}]
    TPM_LIST = ['Platform Hierarchy', 'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization']
    REV_NAME = 'Attempt Rev of TPM2 ACPI Table'
    PPI_NAME = 'Attempt PPI Version'
    PCR_BANK_MSG = 'New PCRBanks is 0x\d+. \('
    CHANGE_TPM_VALUE = ['TPM2 PCR_Allocate(Algorithm IDs)', 'TPM2 ChangeEPS']
    ESC_MSG = 'Press ESC to reject this change'

    # Boot Logo
    HIDE_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Enabled'}]
    SHOW_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Disabled'}]
    LOGO_PATH = './Inspur7500/Tools/Pictures/Logo'
    MANUFACTOURER = 'Inspur'

    # 联动关系
    BOOT_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}]
    UEFI_HII = 'UEFI HII Configuration'
    BOOT_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}]
    OPEN_SECURE = ['Set Administrator Password', 'Secure Boot', {'Secure Boot Default Key Provision': 'Auto'}]
    CLOSE_SECURE_MSG = '<Manual> *Secure Boot Default Key Provision'
    CLOSE_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]
    CLOSE_PXE_STACK = ['User Wait Time', {'UEFI Network Stack': 'Disabled'}]
    LOC_UEFI_HII = ['Console Redirection', 'UEFI HII Configuration']

    # Option Rom
    OPEN_OPTION_ROM = ['Console Redirection', 'Onboard Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},
                       'User Wait Time', {'Boot Mode': 'Legacy'}, {'OPTION ROM Message': 'Enabled'}]
    CLOSE_OPTION_ROM = ['User Wait Time', {'OPTION ROM Message': 'Disabled'}]
    ONBOARD_MSG = 'WangXun\(R\) *PXE'
    ASMEDIA_MSG = 'WangXun\(R\) *PXE'

    # TPCM
    OPEN_TPCM = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'}, {'Hygon TPCM': 'Enabled'}]
    CLOSE_TPCM = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'},
                  {'Hygon TPCM': 'Disabled'}]
    CLOSE_DEBUG = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Disabled'}]
    TPCM_MSG = 'TpcmVerifyRaw:Success'


class Upd:
    PASSWORDS = ['Admin@9999', 'Users@9999']

    BMC_LINK_OPTION = ['<Disabled>SOLforBaseboardMgmt', '<Enabled>SOLforBaseboardMgmt', '<StayOff>RestoreACpowerloss',
                       '<LastState>RestoreACpowerloss', '<PowerOn>RestoreACpowerloss']
    DEFAULT_OPTION_VALUE = ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '[100]PasswordLockTime',
                            '<30Days>PasswordValidDays', '<Disabled>Power-onPassword', '<Enabled>CustomPasswordCheck',
                            '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry', '<DTPM>TPMSelect',
                            '[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
                            '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
                            '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion',
                            '<Disabled>PXEBootPriority', '<FullUpdate>BIOSUpdateParameters', '<English>SelectLanguage',
                            '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA',
                            '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan', '<PCIE>PrimaryGraphicsAdapter',
                            '<Enabled>USBMassStorageSupport', '<Enabled>IOMMU', '<Enabled>SVM',
                            '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit',
                            '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize',
                            '<Disabled>PCIEASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
                            '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode', '<Disabled>FCHSSC',
                            '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
                            '<Disabled>SOLforBaseboardMgmt', '<LastState>RestoreACpowerloss',
                            '<Disabled>PlatformFirstErrorHandling', '<Auto>Allowsettingmemoryfrequency',
                            '<Auto>Downcorecontrol', '<Disabled>SMEEControl', '<Enabled>ChipselectInterleaving',
                            '<Auto>Channelinterleaving', '<Auto>NUMA', '<Auto>Memoryinterleavingsize',
                            '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider',
                            '<Disabled>RDSEEDandRDRANDControl', '<Auto>DRAMscrubtime', '<Auto>cTDPControl',
                            '<Auto>EfficiencyOptimizedMode', '<Auto>BankInterleaving', '<Unbind>HDDBind',
                            '<Enabled>RearUSBPortConfiguration', '<Enabled>FrontUSBPortConfiguration',
                            '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl',
                            '<Auto>ACSEnable', '<Enabled>ConsoleRedirection', '<115200>SerialPortBaudrate',
                            '<8DataBits>SerialDataBits', '<Noparity>SerialParityType', '<1>SerialStopBits',
                            '<VT-UTF8>TerminalType', '<Enabled>NCSI', '<Dynamic>IPv4Source', '<Enabled>IPv6',
                            '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<Dynamic>IPv4Source', '<Enabled>IPv6',
                            '<Dynamic>IPv6Source',
                            '[0]IPv6PrefixLength', '<NoAccess>Privilege', '<Disabled>UserStatus', '<NoAccess>Privilege',
                            '<Disabled>UserStatus', '<Enabled>TPMState', '<Enabled>PlatformHierarchy',
                            '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy', '<Enabled>PHRandomization',
                            '<Rev4>AttemptRevofTPM2ACPITable', '<1.3>AttemptPPIVersion', '<NoAction>TPM2Operation',
                            '[0]TPM2OperationParameter', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot',
                            '<Enter>RestoreFactoryKeys', '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode',
                            '<Enter>EnterDeployedMode'
                            ]
    # 获取BIOS选项值
    REMOVE_OPTIONS = ['BMC system log', 'UEFI HII Configuration', 'BMC system event log',
                      'Key Management']  # 读取选项时不进入的菜单

    # 修改BIOS选项
    CHANGE_PART1 = [Msg.PAGE_MAIN, 'PCIE Info', {'MCIO2_CPU1 as SATA': 'Enabled'}, 'Console Redirection',
                    'Onboard Lan Configuration',
                    {'Onboard Ethernet Controller': 'Enabled'}, {'Wake On Lan': 'Disabled'}, 'Console Redirection',
                    'Virtualization Configuration', {'IOMMU': 'Disabled'}, {'SVM': 'Disabled'},
                    {'SR-IOV Support': 'Disabled'}, 'Console Redirection', 'Misc Configuration',
                    {'Above 4G Decoding': 'Disabled'},
                    {'MMIO High Limit': '4TB'}, {'Hide Boot Logo': 'Enabled'}, {'PCIE Max Payload Size': '512B'},
                    {'PCIE ASPM': 'L1'}, {'AES': 'Disabled'}, {'Hyper Threading Technology': 'Disabled'},
                    {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'}, {'CPU P-State Control': 'P0+P1'},
                    {'CPU C-State Control': 'Enabled'}]
    CHANGE_PART2 = ['Console Redirection', 'Server Management', {'FRB2 Watchdog Timer': 'Enabled'},
                    {'FRB2 Watchdog Timer Policy': 'Power Off'},
                    {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}, {'OS Boot Watchdog Timer': 'Enabled'},
                    {'SOL for Baseboard Mgmt': 'Enabled'}, {'Restore AC power loss': 'Stay Off'}, 'Console Redirection',
                    'Error Management', {'Platform First Error Handling': 'Enabled'},
                    {'MCA Error Threshold Count': '100'},
                    {'Leaky Bucket Time': 10}, {'Leaky Bucket Count': 20},
                    {'Clear memory CE threshold in every 24 hours': 'Disabled'},
                    {'Pcie CE Threshold': 5}, {'CPU CE Threshold': 200}, 'Console Redirection', 'Hygon CBS',
                    {'Allow setting memory frequency': 'Enabled'},
                    {'Memory Clock Speed': '1333MHz'}, {'Downcore control': 'SIX (3 + 3)'},
                    {'Core Performance Boost': 'Disabled'}, {'SMEE Control': 'Disabled'},
                    {'Chipselect Interleaving': 'Disabled'}, {'Channel interleaving': 'Enabled'}, {'NUMA': 'None'},
                    {'Memory interleaving size': '512 Bytes'}, {'Redirect scrubber control': 'Enabled'},
                    {'Determinism Slider': 'Power'},
                    {'RDSEED and RDRAND Control': 'Auto'}, {'DRAM scrub time': '48 hours|48hours'},
                    {'cTDP Control': 'Manual'}, {'Efficiency Optimized Mode': 'Auto'}, {'Bank Interleaving': 'Auto'},
                    'Console Redirection', 'Hygon CBS', 'Cache Prefetcher settings',
                    {'L1 Stream HW Prefetcher': 'Enable'}, {'L2 Stream HW Prefetcher': 'Enable'},
                    'Console Redirection', 'Hygon CBS', 'NBIO Common Options',
                    {'NBIO RAS Control': 'Disabled'}, {'ACS Enable': 'Disabled'}, 'Console Redirection',
                    {'Memory error behavior': 'Shutdown System'}]
    CHANGE_PART3_1 = ['Set Administrator Password', 'Password Lock Time']
    CHANGE_PART3_2 = ['User Wait Time', {'User Wait Time': 10},
                      {'Bootup NumLock State': 'Off'}, {'Internal SHELL': 'Enabled'}, {'PXE Option Rom': 'Disabled'}]
    SET_TIME_ALWAYS = [{'Password Valid Days': 'Indefinite'}]

    PASSWORD_MSG = 'Please input (?:admin )*password'
    START_UPDATE_MSG = 'Update BIOS'

    SET_UPDATE_NOR = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Reserved Configuration'}]
    SET_UPDATE_ALL = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Full Update'}]
    SETUP_LATEST = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.LATEST_BIOS_FILE]
    SETUP_PREVIOUS = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.PREVIOUS_BIOS_FILE]
    SETUP_CONSTANT = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.CONSTANT_BIOS_FILE]
    SETUP_MSG = 'Flash is updated successfully!'

    SET_DOS = [Msg.PAGE_BOOT, {'Boot Mode': 'Legacy'}]
    DOS_FLASH_TOOL = Env.DOS_FLASH_CMD
    ENT_DOS_MSG = 'Start booting from USB device...|StartbootingfromUSBdevice...'
    DOS_MSG_NOR = "End.....................Successed!|> "
    DOS_MSG_ALL = "Update ALL..................Successed!| C:\\\{}>".format(Env.BIOS_FILE)

    OPEN_SHELL = [Msg.PAGE_BOOT, {'Boot Mode': 'UEFI'}, {'Internal SHELL': 'Enabled'}]
    SHELL_FLASH_CMD_LATEST_ALL = 'ByoFlash.efi -bfu latest.bin -all'
    SHELL_FLASH_CMD_PREVIOUS_ALL = 'ByoFlash.efi -bfu previous.bin -all'
    SHELL_FLASH_CMD_CONSTANT_ALL = 'ByoFlash.efi -bfu constant.bin -all'
    SHELL_FLASH_CMD_LATEST = 'ByoFlash.efi -bfu latest.bin'
    SHELL_FLASH_CMD_PREVIOUS = 'ByoFlash.efi -bfu previous.bin'
    SHELL_FLASH_CMD_CONSTANT = 'ByoFlash.efi -bfu constant.bin'
    SHELL_MSG_NOR = "End.....................Successed!|BIOS has been updated"
    SHELL_MSG_ALL = "Update ALL..................Successed!|BIOS has been updated"

    LINUX_FLASH_CMD_LATEST_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -all'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin -all'
    LINUX_FLASH_CMD_CONSTANT_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}constant.bin -all'
    LINUX_FLASH_CMD_LATEST = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_FLASH_CMD_CONSTANT = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}constant.bin'
    LINUX_MSG_NOR = "End.....................Successed!|Flash update successfully"
    LINUX_MSG_ALL = "Update ALL..................Successed!|Flash update successfully"

    WINDOWS_FLASH_TOOL = Env.WINDOWS_FLASH_CMD
    WINDOWS_MSG_NOR = "End.....................Successed!"
    WINDOWS_MSG_ALL = "Update ALL..................Successed!"

    SETUP_OTHERS = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.OTHERS_BIOS_FILE]
    SETUP_UNSIGNED = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.UNSIGNED_BIOS_FILE]
    SHELL_FLASH_CMD_OTHERS = 'ByoFlash.efi -bfu others.bin'
    SHELL_FLASH_CMD_UNSIGNED = 'ByoFlash.efi -bfu unsigned.bin'
    LINUX_FLASH_CMD_OTHERS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'
    UPDATE_OTHERS_MSG_SETUP = 'File Sign Match Fail'
    UPDATE_UNSIGNED_MSG_SETUP = 'File Sign Match Fail'
    UPDATE_OTHERS_MSG_LINUX = 'please check BIOS ID information'
    UPDATE_UNSIGNED_MSG_LINUX = 'Sign Verify .* failed'
    UPDATE_OTHERS_MSG_SHELL = 'BiosCheck Fail'
    UPDATE_UNSIGNED_MSG_SHELL = 'BiosCheck Fail'


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
    SETUP_KEY = Key.DEL  # POST界面进入SetUp按键
    BOOTMENU_KEY = Key.F11  # POST界面进入启动菜单按键
    POST_PSW_MSG = 'System Security'  # 设置SetUp密码后,进入SetUp要求输入密码的提示信息

    # 修改的SMBIOS内容,可以在'{}'中间按照格式自定义添加
    SMBIOS_CHANGE = {'1 0 5': 'oem105',
                     '1 0 6': 'oem106',
                     }
    # 默认的SMBIOS内容,需要和修改的SMBIOS内容对应
    SMBIOS_DEFAULT = {'1 0 5': 'CS5260H2',
                      '1 0 6': 'V1',

                      }

    SET_ADMIN_PSW = ['Set Administrator Password']  # SetUp下设置管理员密码的路径
    SET_USER_PSW = ['Set Administrator Password', 'Set User Password']  # SetUp下设置用户密码的路径
    SET_PSW_SUC_MSG = 'Password Setting Successfully'  # 密码设置成功的提示信息
    DEL_PSW_SUC_MSG = 'Password deleted succeeded'  # 密码删除成功的提示信息

    MACHINE_TYPE = 'Server'  # 测试机器的类型,服务器(支持Ipmi):'Server',桌面机:'Desktop'

    # 读取SetUp值时进入选项的路径,依次进入各主页面下的各级子菜单，'ESC'代表按ESC键
    OPTION_PATH = ['Build Info', 'PCIE Info', 'ESC', 'Console Redirection', 'Lan Configuration', 'ESC',
                   'Video Configuration', 'ESC', 'SATA Configuration', 'Sata Controller Configuration', 'ESC'
                                                                                                        'ESC',
                   'USB Configuration', 'USB Port Configuration', 'ESC', 'ESC', 'Virtualization', 'ESC',
                   'Misc Configuration', 'ESC', 'Server Management', 'ESC', 'Error Management', 'ESC',
                   'Hygon CBS', 'ESC', 'HDD Bind', 'ESC']
    # OPTION_PATH=['Console Redirection','Onboard Lan Configuration','ESC','Video Configuration','ESC','USB Configuration','USB Port Configuration','ESC','ESC','Virtualization Configuration','ESC','Misc Configuration','ESC','Server Management']
    # 改变的SetUp选项
    CHANGE_OPTIONS = [Msg.PAGE_MAIN, 'PCIE Info', {'MCIO2_CPU1 as SATA': 'Enabled'},
                      'Console Redirection', 'Onboard Lan Configuration',
                      {'Onboard Ethernet Controller': 'Enabled'}, {'Wake On Lan': 'Disabled'},
                      'Console Redirection', 'Virtualization Configuration', {'IOMMU': 'Disabled'},
                      {'SVM': 'Disabled'}, {'SR-IOV Support': 'Disabled'}, 'Console Redirection',
                      'Misc Configuration', {'Above 4G Decoding': 'Disabled'},
                      {'MMIO High Limit': '4TB'}, {'Hide Boot Logo': 'Enabled'},
                      {'PCIE Max Payload Size': '512B'}, {'PCIE ASPM': 'L1'},
                      {'AES': 'Disabled'}, {'Hyper Threading Technology': 'Disabled'},
                      {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                      {'CPU P-State Control': 'P0+P1'}, {'CPU C-State Control': 'Enabled'}]
    # BIOS默认值
    DEFAULT_OPTION_VALUE = ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '[100]PasswordLockTime',
                            '<30Days>PasswordValidDays', '<Disabled>Power-onPassword', '<Enabled>CustomPasswordCheck',
                            '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry', '<DTPM>TPMSelect',
                            '[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
                            '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
                            '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion',
                            '<Disabled>PXEBootPriority', '<FullUpdate>BIOSUpdateParameters', '<English>SelectLanguage',
                            '<DefaultConfiguration>NativePCIeConfiguration', '<Disabled>MCIO2_CPU1asSATA',
                            '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan', '<PCIE>PrimaryGraphicsAdapter',
                            '<Enabled>USBMassStorageSupport', '<Enabled>IOMMU', '<Enabled>SVM',
                            '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit',
                            '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize',
                            '<Disabled>PCIEASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
                            '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode',
                            '<P0>CPUP-StateControl', '<Disabled>CPUC-StateControl', '<Disabled>FRB2WatchdogTimer',
                            '<Disabled>OSBootWatchdogTimer', '<Disabled>SOLforBaseboardMgmt',
                            '<LastState>RestoreACpowerloss', '<Enabled>PlatformFirstErrorHandling',
                            '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount',
                            '<Disabled>ClearmemoryCEthresholdinevery24hours', '<Enabled>RASPCIECE',
                            '[1]PcieCEThreshold', '[4096]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency',
                            '<Auto>Downcorecontrol', '<Auto>CorePerformanceBoost', '<Disabled>SMEEControl',
                            '<Enabled>ChipselectInterleaving', '<Auto>Channelinterleaving', '<Auto>NUMA',
                            '<Auto>Memoryinterleavingsize', '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider',
                            '<Disabled>RDSEEDandRDRANDControl', '<Auto>DRAMscrubtime', '<Auto>cTDPControl',
                            '<Auto>EfficiencyOptimizedMode', '<Auto>BankInterleaving', '<Unbind>HDDBind',
                            '<Enabled>RearUSBPortConfiguration', '<Enabled>FrontUSBPortConfiguration',
                            '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl',
                            '<Auto>ACSEnable']

    TOOL_PASSWORD_MSG = 'Please input (?:admin |poweron )*password|Please Enter Admin Password'  # 设置管理员密码后，刷新BIOS要求输入密码的提示信息
    WRONG_PSW_MSG = '(?:Password|password) is invalid|Check password failed|password is invalid'  # 工具刷新BIOS输入错误密码的提示信息
    POWER_LOSS_VALUES = ['Stay Off', 'Last State', 'Power On']
    POWER_LOSS_OPTION = 'Restore AC Power Loss'
    SHELL_TOOL_VERSION_CMD = 'ByoFlash.efi -v'
    SHELL_TOOL_VERSION_CONFIRM_MSG = 'Version'
    SHELL_TOOL_HELP_CMD = 'ByoFlash.efi -h'
    SHELL_TOOL_HELP_CONFIRM_MSG = 'Usage'
    SHELL_FLASH_CMD_LATEST_ALL = 'ByoFlash.efi -bfu latest.bin -all'
    SHELL_FLASH_CMD_PREVIOUS_ALL = 'ByoFlash.efi -bfu previous.bin -all'
    SHELL_FLASH_CMD_LATEST = 'ByoFlash.efi -bfu latest.bin'
    SHELL_FLASH_CMD_PREVIOUS = 'ByoFlash.efi -bfu previous.bin'
    SHELL_MSG_NOR = "BIOS has been updated"
    SHELL_MSG_ALL = "BIOS has been updated"
    SHELL_BACKUP_CMD = 'ByoFlash.efi -bu backup.bin'
    SHELL_BACKUP_SUC_MSG = 'Backup success'
    SHELL_UPDATE_BACKUP_CMD = 'ByoFlash.efi -bfu latest.bin -bu backup.bin'
    SHELL_RESVNVM_CMD_LATEST = 'ByoFlash.efi -resvnvm latest.bin'
    SHELL_RESVNVM_CMD_PREVIOUS = 'ByoFlash.efi -resvnvm previous.bin'
    SHELL_RESVSMBIOS_CMD_LATEST = 'ByoFlash.efi -resvsmbios latest.bin'
    SHELL_RESVSMBIOS_CMD_PREVIOUS = 'ByoFlash.efi -resvsmbios previous.bin'
    SHELL_UPDATE_OA3_CMD = 'ByoFlash.efi -OA3 latest.bin'
    SHELL_LOCK_BIOS_UPDATE_CMD = 'ByoFlash.efi -lock'
    SHELL_UNLOCK_BIOS_UPDATE_CMD = 'ByoFlash.efi -unlock'
    SHELL_LOCK_STATUS_MSG = 'It is locked'
    SHELL_UNLOCK_STATUS_MSG = 'It is unLocked'
    SHELL_LOCK_FAIL_MSG = 'Lock failed'
    SHELL_UNLOCK_FAIL_MSG = 'Unlock failed'
    SHELL_LOCK_STATUS_CMD = 'ByoFlash.efi -locksts'
    SHELL_LOCK_BIOS_MSG = 'Lock success'
    SHELL_UNLOCK_BIOS_MSG = 'Unlock success'
    SHELL_LOCK_BIOS_UPDATE_MSG = 'It is locked'
    SHELL_CLEAN_PSW_CMD = 'ByoFlash.efi -rstpwd'
    SHELL_CLEAN_PSW_MSG = 'ResetPassword success'
    SHELL_FLASH_CMD_OTHERS = 'ByoFlash.efi -bfu others.bin'
    SHELL_FLASH_CMD_UNSIGNED = 'ByoFlash.efi -bfu unsigned.bin'
    SHELL_UPDATE_OTHERS_MSG = 'BiosCheck Fail'
    SHELL_UPDATE_UNSIGNED_MSG = 'BiosCheck Fail'
    SHELL_EMPTY_CMD = 'ByoFlash.efi latest.bin'
    SHELL_ERROR_CMD = 'ByoFlash.efi -aaaa latest.bin'
    SHELL_INPUT_ERR_MSG = 'Input Error'

    LINUX_TOOL_VERSION_CMD = './ByoFlash -v'
    LINUX_TOOL_VERSION_CONFIRM_MSG = 'Version|Byosoft Flash Utility'
    LINUX_TOOL_HELP_CMD = './ByoFlash -h'
    LINUX_TOOL_HELP_CONFIRM_MSG = 'Usage'
    LINUX_FLASH_CMD_LATEST_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -all'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin -all'
    LINUX_FLASH_CMD_LATEST = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_MSG_NOR = "Flash update successfully"
    LINUX_MSG_ALL = "Flash update successfully"
    LINUX_BACKUP_CMD = f'./ByoFlash -bu backup.bin'
    LINUX_BACKUP_SUC_MSG = 'Backup BIOS image Done'
    LINUX_UPDATE_BACKUP_CMD = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -bu backup.bin'
    LINUX_RESVNVM_CMD_LATEST = f'./ByoFlash -resvnvm {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_RESVNVM_CMD_PREVIOUS = f'./ByoFlash -resvnvm {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_RESVSMBIOS_CMD_LATEST = f'./ByoFlash -resvsmbios {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_RESVSMBIOS_CMD_PREVIOUS = f'./ByoFlash -resvsmbios {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_UPDATE_OA3_CMD = f'./ByoFlash -OA3 {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_LOCK_BIOS_UPDATE_CMD = f'./ByoFlash -lock'
    LINUX_UNLOCK_BIOS_UPDATE_CMD = f'./ByoFlash -unlock'
    LINUX_LOCK_BIOS_MSG = 'Flash Locked'
    LINUX_UNLOCK_BIOS_MSG = 'Flash UnLocked'
    LINUX_LOCK_FAIL_MSG = 'Lock flash failed'
    LINUX_UNLOCK_FAIL_MSG = 'Unlock flash failed'
    LINUX_LOCK_STATUS_CMD = f'./ByoFlash -locksts'
    LINUX_LOCK_STATUS_MSG = 'Flash Locked'
    LINUX_UNLOCK_STATUS_MSG = 'Flash unLocked'
    LINUX_LOCK_BIOS_UPDATE_MSG = 'Flash is locked, please unlock first'
    LINUX_CLEAN_PSW_CMD = './ByoFlash -rstpwd'
    LINUX_CLEAN_PSW_MSG = ''
    LINUX_FLASH_CMD_OTHERS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'
    LINUX_UPDATE_OTHERS_MSG = 'please check BIOS ID information'
    LINUX_UPDATE_UNSIGNED_MSG = 'Sign Verify .* failed'
    LINUX_EMPTY_CMD = f'./ByoFlash {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_ERROR_CMD = f'./ByoFlash -aaaa {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_INPUT_ERR_MSG = 'Usage'

    WINDOWS_TOOL_VERSION_CMD = 'ByoFlash.exe -v'
    WINDOWS_TOOL_VERSION_CONFIRM_MSG = 'Byosoft Flash Utility'
    WINDOWS_TOOL_HELP_CMD = 'ByoFlash.exe -h'
    WINDOWS_TOOL_HELP_CONFIRM_MSG = 'Usage'
    WINDOWS_FLASH_CMD_LATEST_ALL = f'ByoFlash.exe -bfu latest.bin -all'
    WINDOWS_FLASH_CMD_PREVIOUS_ALL = f'ByoFlash.exe -bfu previous.bin -all'
    WINDOWS_FLASH_CMD_LATEST = f'ByoFlash.exe -bfu latest.bin'
    WINDOWS_FLASH_CMD_PREVIOUS = f'ByoFlash.exe -bfu previous.bin'
    WINDOWS_MSG_NOR = "Flash update successfully"
    WINDOWS_MSG_ALL = "Flash update successfully"
    WINDOWS_BACKUP_CMD = f'ByoFlash.exe -bu backup.bin'
    WINDOWS_BACKUP_SUC_MSG = 'Status Success'
    WINDOWS_UPDATE_BACKUP_CMD = f'ByoFlash.exe -bfu latest.bin -bu backup.bin'
    WINDOWS_RESVNVM_CMD_LATEST = f'ByoFlash.exe -resvnvm latest.bin'
    WINDOWS_RESVNVM_CMD_PREVIOUS = f'ByoFlash.exe -resvnvm previous.bin'
    WINDOWS_RESVSMBIOS_CMD_LATEST = f'ByoFlash.exe -resvsmbios latest.bin'
    WINDOWS_RESVSMBIOS_CMD_PREVIOUS = f'ByoFlash.exe -resvsmbios previous.bin'
    WINDOWS_UPDATE_OA3_CMD = f'ByoFlash.exe -OA3 latest.bin'
    WINDOWS_LOCK_BIOS_UPDATE_CMD = f'ByoFlash.exe -lock'
    WINDOWS_UNLOCK_BIOS_UPDATE_CMD = f'ByoFlash.exe -unlock'
    WINDOWS_LOCK_BIOS_MSG = 'Flash Locked'
    WINDOWS_UNLOCK_BIOS_MSG = 'Flash UnLocked'
    WINDOWS_LOCK_FAIL_MSG = 'Lock flash failed'
    WINDOWS_UNLOCK_FAIL_MSG = 'Unlock flash failed'
    WINDOWS_LOCK_STATUS_CMD = f'ByoFlash.exe -locksts'
    WINDOWS_LOCK_STATUS_MSG = 'Flash Locked'
    WINDOWS_UNLOCK_STATUS_MSG = 'Flash unLocked'
    WINDOWS_LOCK_BIOS_UPDATE_MSG = 'Flash is locked, please unlock first'
    WINDOWS_CLEAN_PSW_CMD = 'ByoFlash.exe -rstpwd'
    WINDOWS_CLEAN_PSW_MSG = ''
    WINDOWS_FLASH_CMD_OTHERS = f'ByoFlash.exe -bfu others.bin'
    WINDOWS_FLASH_CMD_UNSIGNED = f'ByoFlash.exe -bfu unsigned.bin'
    WINDOWS_UPDATE_OTHERS_MSG = 'please check BIOS ID information'
    WINDOWS_UPDATE_UNSIGNED_MSG = 'Sign Verify .* failed'
    WINDOWS_EMPTY_CMD = f'ByoFlash.exe latest.bin'
    WINDOWS_ERROR_CMD = f'ByoFlash.exe -aaaa latest.bin'
    WINDOWS_INPUT_ERR_MSG = 'Not support parameter|Error command'

    #########ByoCfg工具
    REMOVE_OPTIONS = ['Custom Password Check', 'Quiet Boot', 'Boot Mode', 'SPI BIOS Lock']
    BOOT_NAME_DICT_UEFI = {'HDD': Msg.HDD_BOOT_NAME,
                           'USB_DISK': Msg.USB_BOOT_NAME,
                           'PXE': Msg.PXE_BOOT_NAME,
                           'USB_ODD': Msg.ODD_BOOT_NAME,
                           'OTHERS': Msg.OTHER_BOOT_NAME,
                           }

    BOOT_NAME_DICT_LEGACY = {'HDD': Msg.HDD_BOOT_NAME,
                             'USB_DISK': Msg.USB_BOOT_NAME,
                             'PXE': Msg.PXE_BOOT_NAME,
                             'USB_ODD': Msg.ODD_BOOT_NAME,

                             }

    SET_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'Internal SHELL': 'Enabled'}]
    SET_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}]

    SHELL_BYOCFG_VERSION_CMD = 'ByoCfg.efi -v'
    SHELL_BYOCFG_VERSION_CONFIRM_MSG = 'Byosoft ByoCfg Utility'
    SHELL_BYOCFG_HELP_CMD = 'ByoCfg.efi -h'
    SHELL_BYOCFG_HELP_CONFIRM_MSG = 'Usage'
    SHELL_BYOCFG_DUMP = 'ByoCfg.efi -dump'
    SHELL_BYOCFG_WF = 'ByoCfg.efi -wf'
    SHELL_BYOCFG_W = 'ByoCfg.efi -w'
    SHELL_BYOCFG_R = 'ByoCfg.efi -r'
    SHELL_BYOCFG_SET_DEFAULT = 'ByoCfg.efi -setdefault'
    SHELL_BYOCFG_LOCK = 'ByoCfg.efi -lock'
    SHELL_BYOCFG_LOCK_MSG = 'Lock success'
    SHELL_BYOCFG_UNLOCK = 'ByoCfg.efi -unlock'
    SHELL_BYOCFG_UNLOCK_MSG = 'Unlock success'
    SHELL_BYOCFG_UNLOCK_RUN_MSG = 'It is locked'
    SHELL_BYOCFG_ERROR_CMD = 'ByoCfg.efi -aaaa'
    SHELL_BYOCFG_ERR_MSG = 'Usage|failed'

    LINUX_BYOCFG_VERSION_CMD = './ByoCfg -v'
    LINUX_BYOCFG_VERSION_CONFIRM_MSG = 'Byosoft ByoCfg Utility'
    LINUX_BYOCFG_HELP_CMD = './ByoCfg -h'
    LINUX_BYOCFG_HELP_CONFIRM_MSG = 'Usage'
    LINUX_BYOCFG_DUMP = './ByoCfg -dump'
    LINUX_BYOCFG_WF = './ByoCfg -wf'
    LINUX_BYOCFG_W = './ByoCfg -w'
    LINUX_BYOCFG_R = './ByoCfg -r'
    LINUX_BYOCFG_SET_DEFAULT = './ByoCfg -setdefault'
    LINUX_BYOCFG_LOCK = './ByoCfg -lock'
    LINUX_BYOCFG_LOCK_MSG = 'Flash Locked'
    LINUX_BYOCFG_UNLOCK = './ByoCfg -unlock'
    LINUX_BYOCFG_UNLOCK_MSG = 'Flash UnLocked'
    LINUX_BYOCFG_UNLOCK_RUN_MSG = 'Flash is locked, please unlock first'

    LINUX_BYOCFG_ERROR_CMD = './ByoCfg -aaaa'
    LINUX_BYOCFG_ERR_MSG = 'Usage'

    WINDOWS_BYOCFG_VERSION_CMD = 'ByoCfg.exe -v'
    WINDOWS_BYOCFG_VERSION_CONFIRM_MSG = 'Byosoft ByoCfg Utility'
    WINDOWS_BYOCFG_HELP_CMD = 'ByoCfg.exe -h'
    WINDOWS_BYOCFG_HELP_CONFIRM_MSG = 'Usage'
    WINDOWS_BYOCFG_DUMP = 'ByoCfg.exe -dump'
    WINDOWS_BYOCFG_WF = 'ByoCfg.exe -wf'
    WINDOWS_BYOCFG_W = 'ByoCfg.exe -w'
    WINDOWS_BYOCFG_R = 'ByoCfg.exe -r'
    WINDOWS_BYOCFG_SET_DEFAULT = 'ByoCfg.exe -setdefault'
    WINDOWS_BYOCFG_LOCK = 'ByoCfg.exe -lock'
    WINDOWS_BYOCFG_LOCK_MSG = 'Flash Locked'
    WINDOWS_BYOCFG_UNLOCK = 'ByoCfg.exe -unlock'
    WINDOWS_BYOCFG_UNLOCK_MSG = 'Flash UnLocked'
    WINDOWS_BYOCFG_UNLOCK_RUN_MSG = 'Flash is locked, please unlock first'

    WINDOWS_BYOCFG_ERROR_CMD = 'ByoCfg.exe -aaaa'
    WINDOWS_BYOCFG_ERR_MSG = 'Usage'


class Sec:
    OPEN_INTERNAL_SHELL = ['User Wait Time', {'Internal SHELL': 'Enabled'}]
    SECURE_BOOT_PATH = ['Set Administrator Password', 'Secure Boot']
    OPEN_SECURE_BOOT = [{'Secure Boot': 'Enabled'}]
    CLOSE_SECURE_BOOT = [{'Secure Boot': 'Disabled'}]
    OPEN_CSM = ['User Wait Time', {'Boot Mode': 'Legacy'}]
    CSM_CLOSE_MSG = '<UEFI> *Boot Mode'
    RESTORE_FACTORY = 'Restore Factory Keys'
    RESTORE_MSG = 'Restore Default Secure Boot Keys'
    RESET_SETUP_MODE = 'Reset Platform to Setup Mode'
    AUDIT_MODE = 'Enter Audit Mode'
    DEPLOYED_MODE = 'Enter Deployed Mode'
    KEY_MAN = 'Key Management'
    PK = 'PK Options'
    KEK = 'KEK Options'
    DB = 'DB Options'
    DBX = 'DBX Options'
    DBT = 'DBT Options'
    WARNING = 'Safe startup has been opened'
    BYOAUDIT_TOOL_PATH = 'SecureBoot'
    BYOAUDIT_TOOL_NAME = 'ByoAuditModeTest.efi'
    BYOAUDIT_VERIFY_MSG = 'ImageExeInfoTable->NumberOfImages:\d+'
    KEY_PATH = [Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', '<SecureBoot>', 'correct-key.der']
    ERROR_KEY_PATH = [Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', '<SecureBoot>', 'error-key.txt']
    ERROR_KEY_MSG = 'Unsupported file type'
    DEL_KEY_MSG = 'Are you sure you want to delete|to delete'
    GUID_NAME = 'Signature GUID'
    ERROR_CHARACTERS = 'Please enter in the correct format'
    LOW_CHARACTERS = 'Please enter enough characters'


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

    OPEN_PFEH = ['Console Redirection', 'Server Management', {'OS Boot Watchdog Timer': 'Disabled'},
                 'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'}]
    SET_LEAKY_BUCKET_1 = [{'MCA Error Threshold Count': '1'}, {'Leaky Bucket Time': 35}, {'Leaky Bucket Count': 2}]
    SET_LEAKY_BUCKET_2 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 75}, {'Leaky Bucket Count': 15}]
    SET_LEAKY_BUCKET_3 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 7}, {'Leaky Bucket Count': 1}]
    SET_LEAKY_BUCKET_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                          {'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 0}]

    SET_PCIE_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'Pcie CE Threshold': 1}]
    SET_PCIE_THRESHOLD_2 = ['Console Redirection', 'Virtualization Configuration', {'IOMMU': 'Enabled'},
                            'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'Pcie CE Threshold': 2}]
    SET_PCIE_THRESHOLD_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'Pcie CE Threshold': 0}]
    SET_PCIE_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                              {'Pcie CE Threshold': 10000}]
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
        '1d': '20',  # CPU0_H1
        '19': '21',  # CPU0_G1
        '11': '30',  # CPU0_E1
        '15': '31',  # CPU0_F1
        '2d': '40',  # CPU1_D1
        '29': '41',  # CPU1_C1
        '21': '50',  # CPU1_A1
        '25': '51',  # CPU1_B1
        '3d': '60',  # CPU1_H1
        '39': '61',  # CPU1_G1
        '31': '70',  # CPU1_E1
        '35': '71',  # CPU1_F1
    }
