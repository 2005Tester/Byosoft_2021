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
from ByoTool.Config.PlatConfig import Key


class Env:
    # Report Setting
    PROJECT_NAME = "ByoTool"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "ByoTool\\Report\\template"

    TESTCASE_CSV = "ByoTool\\ToolTest.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\ByoTool\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com3"

    # BMC Configuration
    BMC_IP = '192.168.6.199'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.43'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    OS_IP_LEGACY = '192.168.6.43'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    # Tool definition - Ver 1.8.18
    IPMITOOL = "Inspur7500\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER,
                                                                                                  BMC_PASSWORD)
    SMBIOS = "Inspur7500\\Tools\\smbiosyangjian\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sdd4"
    LINUX_USB_MOUNT = "/mnt/"
    LINUX_USB_NAME = 'DataTraveler'
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs4:"
    USB_VOLUME = "USB:Kingston DataTraveler 2.0 \(P4\)"

    # BIOS flash command
    BIOS_FILE = 'Yangjian'
    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)
    WINDOWS_FLASH_CMD = "ByoWinFlash.exe bfu"
    DOS_FLASH_CMD = "byoflash bfu"
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE = "previous.bin"
    CONSTANT_BIOS_FILE = "constant.bin"
    OTHERS_BIOS_FILE = 'others.bin'
    UNSIGNED_BIOS_FILE = 'unsigned.bin'

    MACHINE_TYPE = 'Server'  # 测试机器的类型,服务器(支持Ipmi):'Server',桌面机:'Desktop'
    OEM_SUPPORT = True  # 是否支持通过OEM命令修改SetUp选项值


class Msg:
    SETUP_KEY = Key.DEL  # POST界面进入SetUp按键
    BOOTMENU_KEY = Key.F11  # POST界面进入启动菜单按键

    POST_MESSAGE = 'DEL to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot'
    HOTKEY_PROMPT_DEL = 'DEL to enter SETUP'
    HOTKEY_PROMPT_F11 = ' Press F11 to enter Boot Menu'
    HOTKEY_PROMPT_F12 = 'Press F12 to PXE boot'
    SETUP_MESSAGE = "Build Info"  # 进入SetUp确认信息
    # Pages in bios configuration
    PAGE_MAIN = "Build Info"
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
    OS_MSG = 'Kylin|Tencent|UOS'
    LEGACY_OS = "SATA1-7: WDC WD5000LPCX-22VHAT0|UEFI SATA1-7: WDC WD5000LPCX-22VHAT0"
    LEGACY_OS_MSG = 'UOS'
    # UOS_OS = 'UOS\(UEFI SATA1\-4: INTEL SSDSCKKB960G8\)'
    UEFI_OS = 'UOS\(UEFI SATA1\-6: SanDisk Z400S\)|UEFI SATA1\-6: SanDisk Z400S'
    UEFI_OS_MSG = 'UOS'
    LINUX_OS = 'UOS\(UEFI SATA1\-6: SanDisk Z400S\)|SATA1-7: WDC WD5000LPCX-22VHAT0'
    LINUX_OS_MSG = 'UOS'


class Psw:
    HDD_PSW1 = [['hdd@12345', 'hdd@11111'],  # 两次密码不一致
                ['hdd@001', 'hdd@12345678901234567890'],  # 长度不符合密码要求
                ['12345678901234567890', 'abcdefgh', '~`"!@#$%', '\:;<,>.?', '?/ @#$%^', "1'^&*()_",
                 'a-+={[}]']]  # 复杂度不符合密码要求
    HDD_PSW2 = ['hdd@1234']
    HDD_PSW3 = ['Hd1~`!@#']
    HDD_PSW4 = ['h1$%^&*()_-+={[}]|"']
    HDD_PSW5 = ['hdd@1234567890123456']
    HDD_PSW6 = ["Hdd123456 :;'\<,>.?/"]
    HDD_PSW7 = ['hdd@12345']
    HDD_PSW8 = ['hdd@12345', 'hdd@11111']
    HDD_PSW9 = ['hdd@12345', 'Hdd1234567890!@#$%^&']
    HDD_PSW10 = ['hdd@12345', '12345678', 'hdd@123']
    HDD_PSW11 = ['hdd@12345']
    HDD_PSW12 = ['hdd@12345']
    HDD_PSW13 = ['hdd@12345']
    HDD_PSW14 = ['hdd@12345']
    HDD_PSW15 = ['hdd@12345', 'hdd@123456']
    HDD_PSW16 = ['hdd@12345', 'hdd@123456']
    HDD_PSW17 = ['hdd@12345', 'hdd@123456']
    HDD_PSW18 = ['hdd@12345', 'hdd@123456']
    HDD_PSW19 = ['hdd@12345']

    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = 'SATA1\-6: SanDisk Z400S'
    HDD_PASSWORD_NAME_02 = 'SATA1-7: WDC WD5000LPCX-22VHAT0'
    # HDD_PASSWORD_NAME_03 = 'NVME\(PCI2\-0\-0\): SAMSUNG MZVLW256HEHP\-000L7'
    HDD_NAME_01_OS = [Msg.UEFI_OS, Msg.UEFI_OS_MSG]
    HDD_NAME_02_OS = [Msg.LEGACY_OS, Msg.LEGACY_OS_MSG]

    # Password related messages
    SET_SETUP_PSW_SUCCESS = 'Password Setting Successfully'
    DEL_SETUP_PSW_SUCCESS = 'Password deleted succeeded'
    SET_ADMIN_PSW = 'Set Administrator Password'
    SET_USER_PSW = 'Set User Password'
    CHECK_PSW = 'Custom Password Check '
    PSW_COMPLEXITY = 'Password Complexity'
    PSW_LEN = 'Password Length'
    PSW_RETRY = 'Password Retry'

    ONLY_SET_USER_PSW = 'Please set Administrator Password first'
    CHARACTERS_LENGTH_NOT_ENOUGH = 'Please enter enough characters'
    CHARACTERS_TYPE_NOT_ENOUGH = 'Warning|Passwords need to contain upper and lower case letters'
    LOGIN_SETUP_PSW_PROMPT = 'System Security'
    LOGIN_SETUP_PSW_FAIL = 'Invalid Password'
    PSW_ERROR_LOCK = 'The password is incorrect and the screen is locked'
    PSW_LOCK_OPTION = 'Password Lock Time'
    PSW_CHECK_ERROR = 'Incorrect password'
    PSW_LOCK_60S = 'Please Reset or Wait 60 seconds|The password is incorrect and the screen is locked'
    PSW_LOCK_180S = 'Please Reset or Wait 180 seconds|The password is incorrect and the screen is locked'
    USER_NOT_DEL_PSW = 'User Rights Cannot Delete Password'
    NEW_OLD_PSW_DIFF = 'Passwords are not the same'
    PREVIOUS_5_PSW_SAME = 'Password has been used by the latest 5 times'
    PSW_EXPIRE = 'Password expired'
    PSW_SET_STATUS = 'Installed'
    PWS_NOT_SET_STATUS = 'Not Installed|Uninstalled'
    USER_ADMIN_PSW_SAME = 'Password Rule Error'
    POWER_ON_PSW_OPTION = 'Power-on Password'
    PSW_EXPIRY_DATE = 'Password Valid Days'
    PSW_LEN_DIFF = 'Character length is not equal'

    HDD_PSW_OPTION = 'HDD Password'
    SET_HDD_PSW_OPTION = 'Enable HDD Password|Enable HDD User Password'
    DEL_HDD_PSW_OPTION = 'Disable HDD Password|Disable HDD User Password'
    HDD_CHARACTERS_LENGTH_NOT_ENOUGH = 'Invalid Password Length'
    HDD_CHARACTERS_TYPE_NOT_ENOUGH = 'Invalid Password Charater Type|Password complexity is invalid'
    SET_HDD_PSW_SUCCESS = 'Changes have been saved|Password have been cleared'
    DEL_HDD_PSW_SUCCESS = 'Password have been cleared'
    LOGIN_HDD_PSW_PROMPT = 'Enter HDD Password'
    LOGIN_HDD_PSW_FAIL = 'Incorrect password'
    DEL_HDD_PSW_ERROR = 'Invalid Password'
    HDD_NEW_OLD_PSW_DIFF = 'Passwords are not the same'
    HDD_LOCK_PROMPT = 'Please restart and enter the correct password to unlock the locked HDD|Please power off then power on, enter the correct password to'
    HDD_LOCK_SETUP = 'The number of password attempts has reached the limit. System will shutdown'
    HDD_LOCK_STATUS = 'security state cannot be changed'
    HDD_ESC_LOCK_PROMPT = 'Drive is still locked|operation failed'
    HDD_NOW_PSW = 'Enter Current Password'

    SET_HDD_HASH_TYPE1 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SHA-256 Hash'}]
    SET_HDD_HASH_TYPE2 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SM3 Hash'}]
    LOC_HDD_PSW = [SET_ADMIN_PSW, HDD_PSW_OPTION]
    LOC_USER_PSW = [SET_ADMIN_PSW, SET_USER_PSW]
    LOC_ADMIN_PSW = [SET_ADMIN_PSW]
    LOC_LOCK_OPTION = [SET_ADMIN_PSW, PSW_LOCK_OPTION]
    SET_TIME_WEEK = [{'Password Valid Days': '7 Days'}]
    SET_TIME_MONTH = [{'Password Valid Days': '30 Days'}]
    SET_TIME_ALWAYS = [{'Password Valid Days': 'Indefinite'}]


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

    # 读取SetUp值时进入选项的路径,依次进入各主页面下的各级子菜单，'ESC'代表按ESC键
    OPTION_PATH = ['Build Info', 'PCIE Info', 'ESC', 'Console Redirection', 'Lan Configuration', 'ESC',
                   'Video Configuration', 'ESC', 'SATA Configuration',
                   'ESC', 'USB Configuration', 'USB Port Configuration', 'ESC', 'ESC', 'Virtualization', 'ESC',
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

    #########ByoDmi工具
    SMBIOS_PATH_LINUX = "ByoTool\\Tools\\ByoDmi_Smbios\\LINUX\\"
    SMBIOS_PATH_WINDOWS = "ByoTool\\Tools\\ByoDmi_Smbios\\WINDOWS\\"
    SMBIOS_PATH_SHELL = "ByoTool\\Tools\\ByoDmi_Smbios\\SHELL\\"
    BYODMI_SMBIOS_CHANGE = {
        '1 0 4': 'oem104',
        '1 0 5': 'oem105',
        '1 0 6': 'oem106',
        '1 0 7': 'oem107',
        '1 0 8': 'ac 00 ba 00 00 00 00 00 00 00 00 00 00 00 12 00',
        '2 0 4': 'oem204',
        '2 0 5': 'oem205',
        '2 0 6': 'oem206',
        '2 0 7': 'oem207',
        '2 0 8': 'oem208',
        '2 0 10': 'oem2010',
        '3 0 4': 'oem304',
        '3 0 6': 'oem306',
        '3 0 7': 'oem307',
        '3 0 8': 'oem308',
    }

    SHELL_BYODMI_VERSION_CMD = 'ByoDmi.efi -v'
    SHELL_BYODMI_VERSION_CONFIRM_MSG = 'ByoDmi.efi version'
    SHELL_BYODMI_HELP_CMD = 'ByoDmi.efi -h'
    SHELL_BYODMI_HELP_CONFIRM_MSG = 'help message'
    SHELL_BYODMI_TYPE_CMD = 'ByoDmi.efi -type'
    SHELL_BYODMI_VIEW_CMD = 'ByoDmi.efi -view'
    SHELL_BYODMI_VIEWALL_CMD = 'ByoDmi.efi -viewall'
    SHELL_BYODMI_LOCK_CMD = 'ByoDmi.efi -lock'
    SHELL_BYODMI_LOCK_MSG = 'Lock success'
    SHELL_BYODMI_LOCK_RUN_MSG = 'It is locked'
    SHELL_BYODMI_UNLOCK_CMD = 'ByoDmi.efi -unlock'
    SHELL_BYODMI_UNLOCK_MSG = 'Unlock success'

    LINUX_BYODMI_VERSION_CMD = './ByoDmi -v'
    LINUX_BYODMI_VERSION_CONFIRM_MSG = 'ByoDmi Version:'
    LINUX_BYODMI_HELP_CMD = './ByoDmi -h'
    LINUX_BYODMI_HELP_CONFIRM_MSG = 'help message'
    LINUX_BYODMI_TYPE_CMD = './ByoDmi -type'
    LINUX_BYODMI_VIEW_CMD = './ByoDmi -view'
    LINUX_BYODMI_VIEWALL_CMD = './ByoDmi -viewall'

    LINUX_BYODMI_LOCK_CMD = './ByoDmi -lock'
    LINUX_BYODMI_LOCK_MSG = 'Lock Success'
    LINUX_BYODMI_LOCK_RUN_MSG = 'It is locked'
    LINUX_BYODMI_UNLOCK_CMD = './ByoDmi -unlock'
    LINUX_BYODMI_UNLOCK_MSG = 'Unlock Success'

    WINDOWS_BYODMI_VERSION_CMD = 'ByoDmi.exe -v'
    WINDOWS_BYODMI_VERSION_CONFIRM_MSG = 'ByoDmi.exe Version:'
    WINDOWS_BYODMI_HELP_CMD = 'ByoDmi.exe -h'
    WINDOWS_BYODMI_HELP_CONFIRM_MSG = 'help message'
    WINDOWS_BYODMI_TYPE_CMD = 'ByoDmi.exe -type'
    WINDOWS_BYODMI_VIEW_CMD = 'ByoDmi.exe -view'
    WINDOWS_BYODMI_VIEWALL_CMD = 'ByoDmi.exe -viewall'
    WINDOWS_BYODMI_LOCK_CMD = 'ByoDmi.exe -lock'
    WINDOWS_BYODMI_LOCK_MSG = 'Lock Success'
    WINDOWS_BYODMI_LOCK_RUN_MSG = 'It is locked'
    WINDOWS_BYODMI_UNLOCK_CMD = 'ByoDmi.exe -unlock'
    WINDOWS_BYODMI_UNLOCK_MSG = 'Unlock Success'

    #########ByoCfg工具
    REMOVE_OPTIONS = ['Custom Password Check', 'Quiet Boot', 'Boot Mode', 'SPI BIOS Lock']
    BOOT_NAME_DICT_UEFI = {'HDD': 'Internal Hard Drive',
                           'USB_DISK': 'USB Flash Drive/USB Hard Disk',
                           'PXE': 'Network Adapter',
                           'USB_ODD': 'USB CD/DVD ROM Drive',
                           'OTHERS': 'Others',
                           }

    BOOT_NAME_DICT_LEGACY = {'HDD': 'Internal Hard Drive',
                             'USB_DISK': 'USB Flash Drive/USB Hard Disk',
                             'PXE': 'Network Adapter',
                             'USB_ODD': 'USB CD/DVD ROM Drive',

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
    SHELL_BYOCFG_ERR_MSG = 'Usage'

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
