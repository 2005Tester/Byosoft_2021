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

    TESTCASE_CSV = "Inspur7500\\AllTest.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\Puti\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com4"

    # BMC Configuration
    BMC_IP = '192.168.6.62'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.59'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2021'

    # Tool definition - Ver 1.8.18
    IPMITOOL = "Inspur7500\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER, BMC_PASSWORD)
    SMBIOS = "Inspur7500\\Tools\\smbiosputi\\"

    # BIOS Firmware URL and local path
    BIOS_URL = "http://192.168.6.20/backup/Inspur_Hygon_HG5000_Normal_nvwa"
    NONE_COMMON_BIOS = ["_ali_"]
    BIOS_SIZE = "16777216"
    BIOS_TOOL_PATH = "Inspur7500\\Tools\\ipmitool\\"
    LATEST_BIN_PATH = os.path.join(BIOS_TOOL_PATH, "latest.bin")
    PREVIOUS_BIN_PATH = os.path.join(BIOS_TOOL_PATH, "previous.bin")
    LATEST_ZIP_PATH = os.path.join(BIOS_TOOL_PATH, "latest.zip")
    PREVIOUS_ZIP_PATH = os.path.join(BIOS_TOOL_PATH, "previous.zip")
    LATEST_UNZIP_PATH = os.path.join(BIOS_TOOL_PATH, "latest")
    PREVIOUS_UNZIP_PATH = os.path.join(BIOS_TOOL_PATH, "previous")
    BMC_UPDATE_TOOL = "wsl ./Inspur7500/Tools/ipmitool/loquat -d BIOS -i redfish -f"
    BIOS_UPDATE_LATEST = "{0} Inspur7500/Tools/ipmitool/latest.bin -h {1} -u {2} -p {3}".format(BMC_UPDATE_TOOL, BMC_IP, BMC_USER, BMC_PASSWORD)
    BIOS_UPDATE_PREVIOUS = "{0} Inspur7500/Tools/ipmitool/previous.bin -h {1} -u {2} -p {3}".format(BMC_UPDATE_TOOL, BMC_IP, BMC_USER, BMC_PASSWORD)

    # BIOS remote path
    # LINUX_OS_PATH = "/boot/efi/"
    LINUX_USB_DEVICE = "/dev/sdc4"
    LINUX_USB_MOUNT = "/mnt/"
    # WINDOWS_OS_PATH = "C:\\Users\\Administrator\\"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs4:"
    USB_VOLUME = "USB:SanDisk \(P4\)"
    
    # BIOS flash command
    LINUX_FLASH_CMD = "./flash bfu"
    LINUX_FLASH_DRIVER_PATH = "/root/"
    LINUX_BIOS_MOUNT_PATH = "/mnt/BIOS/"
    WINDOWS_FLASH_CMD = "ByoWinFlash.exe bfu"
    SHELL_FLASH_CMD = "ByoShellFlash.efi bfu"
    DOS_FLASH_CMD = "byoflash bfu"
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE= "previous.bin"
    CONSTANT_BIOS_FILE="constant.bin"

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

    PXE_ONCE_COMMON ="{0} chassis bootdev pxe".format(IPMITOOL)
    SETUP_ONCE_COMMON ="{0} chassis bootdev bios".format(IPMITOOL)
    HDD_ONCE_COMMON ="{0} chassis bootdev disk".format(IPMITOOL)
    ODD_ONCE_COMMON ="{0} chassis bootdev cdrom".format(IPMITOOL)
    USB_ONCE_COMMON ="{0} chassis bootdev floppy".format(IPMITOOL)

    PXE_ALWAYS_COMMON ="{0} chassis bootdev pxe options=persistent".format(IPMITOOL)
    SETUP_ALWAYS_COMMON ="{0} chassis bootdev bios options=persistent".format(IPMITOOL)
    HDD_ALWAYS_COMMON ="{0} chassis bootdev disk options=persistent".format(IPMITOOL)
    ODD_ALWAYS_COMMON ="{0} chassis bootdev cdrom options=persistent".format(IPMITOOL)
    USB_ALWAYS_COMMON ="{0} chassis bootdev floppy options=persistent".format(IPMITOOL)

    # Check or clear boot flag
    BOOT_FLAG_GET = "{0} raw 0x00 0x09 0x05 0x00 0x00".format(IPMITOOL)
    BOOT_FLAG_CLEAR = "{0} raw 0x00 0x08 0x05 0x00 0x00 0x00 0x00 0x00".format(IPMITOOL)

    # BMC control or check related command
    BMC_RESET = "{0} mc reset cold".format(IPMITOOL)
    BMC_GUID = "{0} mc guid".format(IPMITOOL)
    BMC_INFO = "{0} mc info".format(IPMITOOL)
    BMC_WATCHDOG = "{0} mc watchdog get".format(IPMITOOL)
    BMC_SELFTEST = "{0} mc selftest".format(IPMITOOL)
    FRU_PRINT = "{0} fru print".format(IPMITOOL)
    CPU_TEMP = "{0} sdr | findstr CPU[01]_Core_Temp".format(IPMITOOL)
    FAN_SPEED = "{0} sdr | findstr FAN[12345678]_Speed".format(IPMITOOL)



class SysCfg:
    CPU_CNT = 2  # cpu socket count
    REAR_USB_CNT = 2
    BUILDIN_USB_CNT = 1
    DIMM_SIZE = 96  # /GB

    PCIE_MAP = [
        {  # cpu0
            "0a": "x16",  # ocp
            "1a": "x8",  # slot1
            "1c": "x8",  # build-in raid
            "2a": "x16",  # slot2
            "3a": "x16"  # slot7
        },
        {  # cpu1
            "0a": "x16",  # slot3
            "1a": "x16",  # slot4
            # "2a": "x8",  # Slimline3
            # "2c": "x8",  # Slimline4
        }]

    # CPU, DIMM info
    CPU_info = ['Processor ID\s+000606A6', 'Processor Frequency\s+2.000GHz']
    DIMM_info = ['DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM',
                 'DIMM160\(G\)\s+S1.CG.D0:2933MT/s Hynix DRx4 32GB RDIMM']



class Msg:
    POST_MESSAGE_EN="Del to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot"
    POST_MESSAGE = 'Del to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot'
    HOTKEY_PROMPT_DEL = 'Del to enter SETUP,'
    HOTKEY_PROMPT_DEL_CN = POST_MESSAGE
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu,'
    HOTKEY_PROMPT_F11_CN = POST_MESSAGE
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot,'
    HOTKEY_PROMPT_F12_CN = POST_MESSAGE

    # Pages in bios configuration
    PAGE_MAIN = "BIOS Info"
    PAGE_MAIN_CN = "BIOS Info"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_ADVANCED_CN = 'Console Redirection'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_SECURITY_CN = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_BOOT_CN = 'User Wait Time'
    PAGE_EXIT = 'Save Changes'
    PAGE_EXIT_CN = 'Save Changes'

    PAGE_ALL = [PAGE_MAIN_CN,PAGE_ADVANCED_CN,PAGE_SECURITY_CN,PAGE_BOOT_CN,PAGE_EXIT_CN]

    # Menus of main page
    CPU_INFO_CN = 'CPU Info'
    MEM_INFO_CN='Memory Info'
    DATE_TIME_CN='System Date and Time'
    PCIE_INFO_CN='PCIE Info'
    SEL_LANG_CN='Select Language'
    SEL_LANG='Select Language'
    
    # Menus of Advanced
    TERMINAL_TYPE='Terminal Type'
    LAN_CONFIG_CN='Lan Configuration'
    VIDEO_CONFIG_CN='Video Configuration'
    SATA_CONFIG_CN='SATA Configuration'
    USB_CONFIG_CN = 'USB Configuration'

    VIRTUALIZATION_CN='Virtualization'
    MISC_CONFIG_CN='Misc Configuration'
    SERVER_CONFIG_CN='Server Configuration'
    ERROR_MANAG_CN='Error Management'
    HYGON_CBS_CN='Hygon CBS'
    HDD_BIND_CN='HDD Bind'
    UEFI_HII_CN='UEFI HII Configuration'

    # Menus of Security
    SET_USER_PSW_CN='Set User Password'
    PSW_LOCK_TIME_CN='Password Lock Time'
    PSW_VALID_DAYS_CN='Password Valid Days'
    CUSTOM_PSW_CHECK_CN='Custom Password Check'
    PSW_COMPLEXITY_CN='Password Complexity'
    PSW_LEN_CN='Password Length'
    PSW_RETRY_CN='Password Retry'
    TPM_SEL_CN='TPM Select'
    SECURE_BOOT_CN='Secure Boot'
    HDD_PSW_CN='HDD Password'

    # Menus of Boot
    QUIET_BOOT_CN='Quiet Boot'
    NUMLOCK_STATE_CN='Bootup NumLock State'
    LEGACY_OPTION_ROM_CN='OPTION ROM Message'
    BOOT_MODE_CN='Boot Mode'
    INTERNAL_SHELL_CN='Internal SHELL'
    PXE_OPTION_ROM_CN='PXE Option Rom'
    PXE_NETWORK_CN='Select a Network to PXE'
    PXE_RETRY_CN='PXE Boot Options Retry'
    PXE_IP_VER_CN='Net Boot IP Version'
    PXE_BOOT_PRIOROTY='PXE Boot Priority'
    HDD_BOOT_NAME = 'Internal Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    OTHER_BOOT_NAME = 'Others'

    # Menus of Exit
    SAVE_AND_EXIT_CN='Save and Exit'
    EXIT_NO_SAVE_CN='Discard Changes and Exit'
    LOAD_DEFAULTS_CN='Load Setup Defaults'
    BIOS_UPDATE_PARAMETERS_CN='BIOS Update Parameters'
    BIOS_UPDATE_CN='BIOS Update'
    SHUTDOWN_SYSTEM_CN='Shutdown System'
    REBOOT_SYSTEM_CN='Reboot System'

    # Menus of boot page
    ENTER_BOOTMENU_CN = "Startup Device Menu|ENTER to select boot device"
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: SanDisk'
    SHELL = "Internal EDK Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    OS_MSG = 'Kylin|Tencent|CentOS'
    CENT_OS_Legacy = 'SATA1\-4: ST1000DM010\-2EP102'
    CENTOS_OS = 'CentOS Linux\(MegaRAID Controller Drive 0 Logical Channel Pun 6\)'
    CENTOS_OS_MSG = 'CentOS'
    KYLIN_OS = "Kylin Linux Advanced Server\(SATA3-0: WDC WD10EZEX-08WN4A0\)"
    KYLIN_OS_MSG = 'Kylin'
    UOS_OS = 'UOS\(SATA3\-1: SanDisk SDSSDH3 500G\)'
    UOS_OS_MSG = 'UOS'
    LINUX_OS = UOS_OS
    LINUX_OS_MSG = UOS_OS_MSG
    WINDOWS_OS = KYLIN_OS
    WINDOWS_OS_MSG = KYLIN_OS_MSG



class Boot:
    SERVICE_CONFIG=[Msg.PAGE_ADVANCED_CN,Msg.SERVER_CONFIG_CN]
    LOC_USB=[Msg.PAGE_ADVANCED_CN,Msg.USB_CONFIG_CN]
    LOC_HDD=[Msg.PAGE_BOOT,Msg.HDD_BOOT_NAME]
    CPU_INFO=[Msg.CPU_INFO_CN]
    MEM_INFO=[Msg.MEM_INFO_CN]

    ONBOARD_ETH=['Console Redirection','Lan Configuration',{'Onboard Ethernet Controller':'Enabled'}]
    PXE=['User Wait Time', {'PXE Option Rom': 'Enabled'}]



class Cpu:
    # CPU信息
    CPU_INFO=[Msg.PAGE_MAIN_CN,Msg.CPU_INFO_CN]
    
    # CPU频率
    CPU_FREQUENCY=['1200', '1600', '2000']#SetUp下可以设定的CPU频率
    SET_FREQUENCY1=['Console Redirection','Misc Configuration',{'ENERGY_PERF_BIAS_CFG mode':'User Defined'},{'CPU P-State Control':'P0'},{'CPU C-State Control':'Disabled'},{'Set CPU Speed':'{0} MHz'.format(CPU_FREQUENCY[0])}]
    SET_FREQUENCY2=['Console Redirection','Misc Configuration',{'Set CPU Speed':'{0} MHz'.format(CPU_FREQUENCY[1])}]
    SET_FREQUENCY3 = ['Console Redirection', 'Misc Configuration', {'Set CPU Speed': '{0} MHz'.format(CPU_FREQUENCY[2])}]
    SET_FREQUENCY4 = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'Performance'}]
    
    # CPU超线程
    CLOSE_HYPER_THREADING=['Console Redirection','Misc Configuration',{'Hyper Threading Technology':'Disabled'}]
    OPEN_HYPER_THREADING = ['Console Redirection', 'Misc Configuration', {'Hyper Threading Technology': 'Enabled'}]
    
    # CPU C-State
    CPU_FREQUENCY_CSTATE=['3.00','2.50']#海光工具检测，C-State打开、关闭状态下的CPU频率
    OPEN_CSTATE=['Console Redirection','Misc Configuration',{'ENERGY_PERF_BIAS_CFG mode':'User Defined'},{'CPU P-State Control':'P0'},{'CPU C-State Control':'Enabled'},{'Set CPU Speed':'{0} MHz'.format(CPU_FREQUENCY[-1])}]
    CLOSE_CSTATE = ['Console Redirection', 'Misc Configuration',  {'CPU C-State Control': 'Disabled'}]
    
    # CPU P-State
    CPU_FREQUENCY_PSTATE=['2.50','1.60','1.20']#海光工具检测，P0、P1、P2CPU频率
    SET_PSTATE_P0=['Console Redirection','Misc Configuration',{'ENERGY_PERF_BIAS_CFG mode':'User Defined'},{'CPU P-State Control':'P0'},{'CPU C-State Control':'Disabled'},{'Set CPU Speed':'{0} MHz'.format(CPU_FREQUENCY[-1])}]
    SET_PSTATE_P0P1 = ['Console Redirection', 'Misc Configuration',  {'CPU P-State Control': 'P0+P1'}]
    SET_PSTATE_P0P1P2 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1+P2'}]
    SET_HIGH=['Console Redirection','Misc Configuration',{'ENERGY_PERF_BIAS_CFG mode':'Performance'}]
    
    # CPU 降核
    CPU_DOWNCORE_CORE=['8','8','12','16','16','24']#CPU降核
    DOWNCORE_VALUES=['TWO (1 + 1)','TWO (2 + 0)','THREE (3 + 0)','FOUR (2 + 2)','FOUR (4 + 0)','SIX (3 + 3)']
    LOC_DOWNCORE=['Console Redirection','Hygon CBS']
    DOWNCORE_NAME='Downcore control'
    SET_DOWNCORE_AUTO = ['Console Redirection', 'Hygon CBS', {'Downcore control': 'Auto'}]
    
    # CPU AES
    CLOSE_AES=['Console Redirection','Misc Configuration',{'AES':'Disabled'}]
    OPEN_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Enabled'}]
    
    # CPU NUMA
    NUMA_VALUES = ['Socket', 'None', 'Channel', 'Die', 'Auto']
    CPU_NUMA_ONE = ['1', '4', '4', '1', '4']  # NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO = ['1', '8', '8', '2', '8']  # NUMA双路CPU分别对应插槽、没有、通道、裸片、自动
    LOC_NUMA=['Console Redirection','Hygon CBS']
    NUMA_NAME='NUMA'
    
    # CPU CPB
    CPU_FREQUENCY_CPB=['2.00','2.50']#海光工具检测,超频关闭，打开下CPU频率
    CLOSE_CPB=['Console Redirection','Misc Configuration',{'ENERGY_PERF_BIAS_CFG mode':'User Defined'},{'CPU P-State Control':'P0'},{'CPU C-State Control':'Disabled'},{'Set CPU Speed':'{0} MHz'.format(CPU_FREQUENCY[-1])},'Console Redirection','Hygon CBS',{'Core Performance Boost':'Disabled'}]
    OPEN_CPB=['Console Redirection','Hygon CBS',{'Core Performance Boost':'Auto|Enabled'}]



class Psw:
    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = 'SATA3\-0: WDC WD10EZEX-08WN4A0'
    HDD_PASSWORD_NAME_02 = 'SATA3\-1: SanDisk SDSSDH3 500G'
    # HDD_PASSWORD_NAME_03 = 'NVME\(PCI2\-0\-0\): SAMSUNG MZVLW256HEHP\-000L7'
    HDD_NAME_01_OS = [Msg.KYLIN_OS, Msg.KYLIN_OS_MSG]
    HDD_NAME_02_OS = [Msg.UOS_OS, Msg.UOS_OS_MSG]

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
    PSW_LOCK_60S = 'Please Reset or Wait 60 seconds'
    PSW_LOCK_180S = 'Please Reset or Wait 180 seconds'
    USER_NOT_DEL_PSW = 'User Rights Cannot Delete Password'
    NEW_OLD_PSW_DIFF = 'Passwords are not the same'
    PREVIOUS_5_PSW_SAME = 'Password has been used by the latest 5 times'
    PSW_EXPIRE = 'Password expired'
    PSW_SET_STATUS = 'Installed'
    PWS_NOT_SET_STATUS = 'Not Installed'
    USER_ADMIN_PSW_SAME = 'Password Rule Error'
    POWER_ON_PSW_OPTION = 'Power-on Password'
    PSW_EXPIRY_DATE = 'Password Valid Days'
    PSW_LEN_DIFF='Character length is not equal'

    HDD_PSW_OPTION = 'Hdd Password'
    SET_HDD_PSW_OPTION = 'Enable Hdd Password'
    DEL_HDD_PSW_OPTION = 'Disable Hdd Password'
    HDD_CHARACTERS_LENGTH_NOT_ENOUGH = 'Invalid Password Length'
    HDD_CHARACTERS_TYPE_NOT_ENOUGH = 'Invalid Password Charater Type'
    SET_HDD_PSW_SUCCESS = 'Changes have been saved'
    LOGIN_HDD_PSW_PROMPT = 'Enter Hdd Password'
    LOGIN_HDD_PSW_FAIL = 'Incorrect password'
    DEL_HDD_PSW_ERROR = 'Invalid Password'
    HDD_NEW_OLD_PSW_DIFF = 'Passwords are not the same'
    HDD_LOCK_PROMPT = 'Please restart and enter the correct password to unlock the locked HDD'
    HDD_LOCK_STATUS = 'security state cannot be changed'
    HDD_ESC_LOCK_PROMPT = 'Drive is still locked'
    HDD_NOW_PSW='Enter Current Password'

    LOC_HDD_PSW=[SET_ADMIN_PSW,HDD_PSW_OPTION]
    LOC_USER_PSW=[SET_ADMIN_PSW,SET_USER_PSW]
    LOC_ADMIN_PSW = [SET_ADMIN_PSW]
    LOC_LOCK_OPTION=[SET_ADMIN_PSW,PSW_LOCK_OPTION]
    SET_TIME_WEEK=[{'Password Valid Days':'7 Days'}]
    SET_TIME_MONTH = [{'Password Valid Days': '30 Days'}]
    SET_TIME_ALWAYS = [{'Password Valid Days': 'Indefinite'}]



class Ipm:
    # Frb2_watchdog
    CLOSE_FRB=['Console Redirection','Server Configuration',{'FRB2 Watchdog Timer':'Disabled'}]
    OPEN_FRB1=['Console Redirection','Server Configuration',{'FRB2 Watchdog Timer':'Enabled'},{'FRB2 Watchdog Timer Policy':'Reset'},{'FRB2 Watchdog Timer Timeout':'10minutes|10 minutes'}]
    OPEN_FRB2 = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Enabled'}, {'FRB2 Watchdog Timer Policy': 'Power Off'}, {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_FRB3 = ['Console Redirection', 'Server Configuration', {'FRB2 Watchdog Timer': 'Enabled'}, {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '5minutes|5 minutes'}]
    
    # OS watchdog
    OPEN_OS_WDOG1=['Console Redirection', 'Server Configuration',{'OS Boot Watchdog Timer':'Enabled'},{'OS Watchdog Timer Policy':'Power Off'},{'OS Watchdog Timer Timeout':'10minutes|10 minutes'}]
    OPEN_OS_WDOG2 = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Enabled'}, {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_OS_WDOG3 = ['Console Redirection', 'Server Configuration', {'OS Boot Watchdog Timer': 'Enabled'}, {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '5minutes|5 minutes'}]
    CLOSE_OS_WDOG=['Console Redirection','Server Configuration',{'OS Boot Watchdog Timer':'Disabled'}]
    
    # Power Loss
    SET_POWER_LOSS1=['Console Redirection','Server Configuration',{'Restore AC Power Loss':'Power On'}]
    SET_POWER_LOSS2 = ['Console Redirection', 'Server Configuration', {'Restore AC Power Loss': 'Last State'}]
    SET_POWER_LOSS3 = ['Console Redirection', 'Server Configuration', {'Restore AC Power Loss': 'Stay Off'}]
    LOC_SERVICE=['Console Redirection', 'Server Configuration']
    POWER_LOSS_VALUE = ['<Power On>', '<Last State>', '<Stay Off>']
    
    # OEM
    OEM_DEFAULT_VALUE = '00 09 1c 06 20 34 15 10 37 07 05 05 00 36'
    LOC_CONSOLE=['Console Redirection']
    LOC_LAN=['Lan Configuration']
    LOC_VIDEO=['Video Configuration']
    LOC_USB=['USB Configuration']
    LOC_USB_PORT=['USB Port Configuration']
    LOC_VIRTU=['Virtualization']
    LOC_MISC=['Misc Configuration']
    LOC_ERR=['Error Management']
    OPEN_ERR=[{'Platform First Error Handling':'Enabled'}]
    LOC_HYGON=['Hygon CBS']
    
    # BMC USRE
    ADD_USER='Add User'
    DEL_USER='Delete User'
    CHANGE_USER='Change User'
    USER_NAME='User Name'
    USER_PSW='User Password'
    CNANGE_USER_PSW='Change User Password'
    USER_PRIVILEGE='Privilege'
    CALLBACK='Callback'
    USER='User'
    OPERATOR='Operator'
    ADMIN='Administrator'
    NO_ACCESS='No Access'
    USER_STATE='User Status'
    DISABLE='Disabled'
    ENABLE='Enabled'
    USER_NAME_NOT_MATCH='Username is a string of 5 to 16 letters|Username only support the first character must be a letter'
    USER_NAME_EXITS='Username does not conform to specifications or already exists'
    ERROR_PSW='Wrong Password'
    DEL_USER_SUCCESS='Delete user success'
    SET_PSW_SUCCESS='Setting Successfully'
    LOC_USER_CONF=['Console Redirection','Server Configuration','BMC User Configuration']

    # IPMITOOL 启动
    IPMITOOL_HDD_BOOT_NAME = 'Internal Hard Drive'
    IPMITOOL_PXE_BOOT_NAME = 'Network Adapter'
    IPMITOOL_ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    IPMITOOL_USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    IPMITOOL_OTHER_BOOT_NAME = 'Others'
    OS_MSG='Kylin|UOS'
    UEFI_PXE_MSG='Checking media present...'
    LEGACY_PXE_MSG='PXE initialising devices...|PXEinitialisingdevices...'
    BOTH_PXE_MSG='PXE initialising devices...|Checking media present...|PXEinitialisingdevices...'
    UEFI_USB_MSG='UEFI Interactive Shell'
    LEGACY_USB_MSG='Start booting from USB device|StartbootingfromUSBdevice'
    BOTH_USB_MSG='Start booting from USB device|UEFI Interactive Shell|StartbootingfromUSBdevice'

    OPEN_LAN=['Console Redirection','Lan Configuration',{'Onboard Ethernet Controller':'Enabled'}]
    OPEN_PXE=[{'PXE Option Rom':'Enabled'}]
    BOOT_MODE_UEFI=[{'Boot Mode':'UEFI'}]
    BOOT_MODE_LEGACY = [{'Boot Mode': 'Legacy'}]
    OPEN_SHELL=[{'Internal SHELL':'Enabled'}]
    
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
    SET_PCIE_MAX1=['Console Redirection','Misc Configuration',{'PCIE Max Payload Size':'128B'}]
    SET_PCIE_MAX2 = ['Console Redirection', 'Misc Configuration', {'PCIE Max Payload Size': '256B'}]
    SET_PCIE_MAX3 = ['Console Redirection', 'Misc Configuration', {'PCIE Max Payload Size': '512B'}]
    SET_PCIE_MAX4 = ['Console Redirection', 'Misc Configuration', {'PCIE Max Payload Size': 'Auto'}]
    
    # PCIE活动状态电源管理
    OPEN_ASPM=['Console Redirection', 'Misc Configuration',{'PCIE ASPM':'L1|Enabled'}]
    CLOSE_ASPM = ['Console Redirection', 'Misc Configuration', {'PCIE ASPM': 'Disabled'}]
    
    # 4GB以上空间解码
    OPEN_ABOVE=['Console Redirection','Misc Configuration',{'Above 4G Decoding':'Enabled'}]
    CLOSE_ABOVE=['Console Redirection','Misc Configuration',{'Above 4G Decoding':'Disabled'}]



class Pxe:
    IPV4_MSG='Start PXE over IPv4'
    IPV6_MSG='Start PXE over IPv6'
    
    # PXE Option Rom
    CLOSE_PXE=['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},'User Wait Time',{'PXE Option Rom':'Disabled'}]
    OPEN_PXE = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]
    
    # PXE 启动
    SET_IPV4=['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},'User Wait Time',{'Boot Mode':'UEFI'},{'PXE Option Rom':'Enabled'},{'Net Boot IP Version':'IPv4'}]
    SET_IPV6=['User Wait Time',{'Net Boot IP Version':'IPv6'}]
    SET_LEGACY=['User Wait Time',{'Boot Mode':'Legacy'},{'PXE Option Rom':'Enabled'}]
    
    # PXE 重试
    CLOSE_PXE_RETRY=['User Wait Time',{'Boot Mode':'UEFI'},{'PXE Option Rom':'Enabled'},{'PXE Boot Options Retry':'Disabled'},{'Net Boot IP Version':'IPv4'}]
    OPEN_PXE_RETRY=['User Wait Time',{'PXE Boot Options Retry':'Enabled'}]
    
    # PXE IP 版本
    SET_IPV4_6=['Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},'User Wait Time',{'Boot Mode':'UEFI'},{'PXE Option Rom':'Enabled'},{'Net Boot IP Version':'IPv4 and IPv6'}]
    
    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun(R) (B4-05-5D-8E-91-B2)"
    PXE_NET_ADDON = "Intel PRO-1000-DESTOP (00-1B-21-11-78-CB)"
    
    # PXE启动项(IPv4)
    PXE_PORT_ADDON = 'UEFI Slot 32: Port \d - Intel E10I2-X540-US PXE IPv4'
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun\(R\) PXE IPv4"
    SET_ONBOARD=['User Wait Time',{'Boot Mode':'UEFI'},{'PXE Option Rom':'Enabled'},{'Select a Network to PXE':PXE_NET_ONBOARD},{'Net Boot IP Version':'IPv4'}]
    SET_ADDON=['User Wait Time',{'Select a Network to PXE':PXE_NET_ADDON}]
    SET_NONE = ['User Wait Time', {'Select a Network to PXE':'NULL'}]
    
    # PXE Boot Priority
    SET_ONBOARD_PRI=['User Wait Time',{'Boot Mode':'UEFI'},{'PXE Option Rom':'Enabled'},{'Select a Network to PXE':'NULL'},{'Net Boot IP Version':'IPv4'},{'PXE Boot Priority':'Onboard First'}]
    SET_ADDON_PRI=['User Wait Time',{'PXE Boot Priority':'Addon First'}]
    SET_ADDON_NONE = ['User Wait Time', {'PXE Boot Priority': 'Disabled'}]



class Sup:
    # Lan Configuration
    CLOSE_LAN=['Console Redirection','Lan Configuration', {'Onboard Ethernet Controller': 'Disabled'},'User Wait Time',{'Boot Mode':'UEFI'},{'PXE Option Rom':'Enabled'},{'Net Boot IP Version':'IPv4'}]
    LOC_PCI_INFO=[Msg.PAGE_MAIN_CN,'PCIE Info','PCI Device Info']
    OPEN_LAN=['Console Redirection','Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}]
    
    # 网络唤醒
    MAC_ADDRESS = 'B4-05-5D-8E-91-B2'
    CLOSE_WAKE_ONLINE=['Console Redirection','Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},{'Wake On Lan':'Disabled'}]
    OPEN_WAKE_ONLINE=['Console Redirection','Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'},{'Wake On Lan':'Enabled'}]
    
    # USB 存储设备支持
    CLOSE_USB_STORAGE=['User Wait Time',{'Boot Mode':'UEFI'},'Console Redirection','USB Configuration',{'USB Mass Storage Support':'Disabled'},'USB Port Configuration',{'Rear USB port Configuration':'Enabled'},{'Front USB port Configuration':'Enabled'}]
    OPEN_USB_STORAGE=['Console Redirection','USB Configuration',{'USB Mass Storage Support':'Enabled'}]
    
    # USB 端口配置
    OPEN_USB_PORT_BOTH=['Console Redirection','USB Configuration',{'USB Mass Storage Support':'Enabled'},'USB Port Configuration',{'Rear USB port Configuration':'Enabled'},{'Front USB port Configuration':'Enabled'}]
    LOC_USB_INFO=['Console Redirection','USB Configuration']
    OPEN_USB_PORT_FRONT=[{'Rear USB port Configuration':'Disabled'},{'Front USB port Configuration':'Enabled'}]
    OPEN_USB_PORT_BEHIND = [ {'Rear USB port Configuration': 'Enabled'},{'Front USB port Configuration': 'Disabled'}]
    CLOSE_USB_PORT_BOTH=[{'Rear USB port Configuration': 'Disabled'},{'Front USB port Configuration': 'Disabled'}]
    OPEN_USB_PORT_ALL=[{'Rear USB port Configuration': 'Enabled'},{'Front USB port Configuration': 'Enabled'}]
    CLOSE_USB_PORT_FRONT=[{'Front USB port Configuration': 'Disabled'}]
    OPEN_USB_PORT_FRONT_ONLY = [{'Front USB port Configuration': 'Enabled'}]
    CLOSE_USB_PORT_BEHIND = [{'Rear USB port Configuration': 'Disabled'}]
    OPEN_USB_PORT_BEHIND_ONLY = [{'Rear USB port Configuration': 'Enabled'}]
    
    # HDD Bind
    HDD_BIND_NAME_1 = 'B4D0F0 WDC WD10EZEX-08WN4A0 WD-WCC6Y3KRDTNP'
    HDD_BIND_NAME_2 = 'B4D0F0 SanDisk SDSSDH3 500G 2104DG444004'
    HDD_BIND_NAME_1_OS = [Msg.KYLIN_OS, Msg.KYLIN_OS_MSG]
    HDD_BIND_NAME_2_OS = [Msg.UOS_OS, Msg.UOS_OS_MSG]
    HDD_BIND_PROMPT = 'No binded Hdd boot will be ignored'################################################
    HDD_BIND1=['Console Redirection','HDD Bind',{'HDD Bind':HDD_BIND_NAME_1}]
    HDD_BIND2 = ['Console Redirection', 'HDD Bind', {'HDD Bind': HDD_BIND_NAME_2}]
    HDD_BIND3 = ['Console Redirection', 'HDD Bind', {'HDD Bind':'No Binded'}]
    
    # Secure Boot
    LOC_SECURE_BOOT=['Set Administrator Password','Secure Boot']
    OPEN_SECURE_BOOT=[{'Secure Boot':'Enabled'},'User Wait Time',{'Boot Mode':'UEFI'},{'Internal SHELL':'Enabled'}]
    CLOSE_SECURE_BOOT=['Set Administrator Password','Secure Boot','Reset to Factory Mode']
    
    # Quiet Boot
    OPEN_QUIET_BOOT=['User Wait Time',{'Quiet Boot':'Enabled'}]
    CLOSE_QUIET_BOOT = [{'Quiet Boot': 'Disabled'}]
    
    # SPI BIOS 锁住
    OPEN_SPI=['User Wait Time',{'Internal SHELL':'Enabled'},'Console Redirection','Misc Configuration',{'SPI BIOS Lock':'Enabled'}]
    CLOSE_SPI=['User Wait Time',{'Internal SHELL':'Enabled'},'Console Redirection','Misc Configuration',{'SPI BIOS Lock':'Disabled'}]
    
    # 虚拟化
    IOMMU_DISABLED_INFO = 'AMD IOMMUv2 functionality not available on this system'
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'
    SVM_DISABLED_INFO = 'kvm: disabled by bios'
    OS_TYPE = 'UnionTech OS'
    ETHERNET_NAME="eno1"
    
    # IOMMU
    CLOSE_IOMMU=['Console Redirection','Virtualization',{'IOMMU':'Disabled'}]
    OPEN_IOMMU=['Console Redirection','Virtualization',{'IOMMU':'Enabled'}]
    
    # SVM
    CLOSE_SVM = ['Console Redirection', 'Virtualization', {'SVM': 'Disabled'}]
    OPEN_SVM = ['Console Redirection', 'Virtualization', {'SVM': 'Enabled'}]
    
    # SR-IOV
    CLOSE_SR=['Console Redirection', 'Virtualization', {'SR-IOV Support': 'Disabled'}]
    OPEN_SR = ['Console Redirection', 'Virtualization', {'SR-IOV Support': 'Enabled'}]
    
    # 内存频率
    MEMORY_SPEED=['667', '800', '1067', '1200', '1333']#SetUp下可以设置的内存频率
    LOC_HYGON=['Console Redirection','Hygon CBS']
    MEMORY_SPEED_NAME='Memory Clock Speed'
    LOC_MEM=[Msg.PAGE_MAIN_CN,'Memory Info']
    
    # Load Setup Defaults
    CLOSE_VIRTU=['Console Redirection','Virtualization', {'IOMMU':'Disabled'},{'SVM':'Disabled'},{'SR-IOV Support':'Disabled'}]
    OPEN_VIRTU = [{'IOMMU': 'Enabled'}, {'SVM': 'Enabled'}, {'SR-IOV Support': 'Enabled'}]
    LOC_VIRTU=['Console Redirection','Virtualization']
    LOC_SAV_EXI=[Msg.PAGE_EXIT_CN,'Save and Exit']
    LOC_NO_SAV_EXI=[Msg.PAGE_EXIT_CN,'Discard Changes and Exit']
    VIRTUALIZATION_DEFAULT=['Enabled', 'Disabled', 'Enabled']
    
    # 全刷后检查默认值
    SET_UPDATE_ALL=[Msg.PAGE_EXIT_CN,{'BIOS Update Parameters':'Full Update'}]
    UPDATE_BIOS_PATH=[Msg.PAGE_EXIT_CN,Msg.BIOS_UPDATE_CN,Env.USB_VOLUME,'<BIOS>',Env.LATEST_BIOS_FILE]

    # SATA控制器(Sata配置页面,控制器A,B所连接的硬盘)
    SATA_R_A = '\['  # 控制器A所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    SATA_R_B = '\['  # 控制器B所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    LOC_SATA=['Console Redirection','SATA Configuration']
    OPEN_SATA=['Console Redirection','SATA Configuration','Sata Controller Configuration',{'Asmedia Controller 1061R_A':'Enabled'},{'Asmedia Controller 1061R_B':'Enabled'}]
    CLOSE_SATA_A=['Sata Controller Configuration',{'Asmedia Controller 1061R_A':'Disabled'},{'Asmedia Controller 1061R_B':'Enabled'}]
    CLOSE_SATA_B = ['Sata Controller Configuration', {'Asmedia Controller 1061R_A': 'Enabled'}, {'Asmedia Controller 1061R_B': 'Disabled'}]
    CLOSE_SATA=['Sata Controller Configuration', {'Asmedia Controller 1061R_A': 'Disabled'}, {'Asmedia Controller 1061R_B': 'Disabled'}]
    
    # TPM
    SET_DTPM=['Set Administrator Password',{'TPM Select':'DTPM'}]
    SET_FTPM = ['Set Administrator Password', {'TPM Select': 'FTPM'}]
    DTPM_MSG='TPM 2.0'
    FTPM_MSG = '156'
    DTPM_OS_MSG='NTZ0751:00: 2.0 TPM'
    FTPM_OS_MSG = 'Inspur7500'
    CHANGE_TPM2=['Set Administrator Password','TCG2 Configuration',{'TPM2 Operation':'TPM2 ClearControl(NO) + Clear'}]
    POST_MSG='Press F12 to clear the TPM'
    LOC_TCG2=['Set Administrator Password','TCG2 Configuration']
    CLOSE_TPM=['Set Administrator Password', {'TPM Select': 'Disabled'}]
    
    # Boot Logo
    HIDE_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Enabled'}]
    SHOW_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Disabled'}]
    LOGO_PATH = 'Hygon/Tools/Pictures/CorrectLogo/logo.png'
    MANUFACTOURER = 'Inspur'
    
    # 联动关系
    BOOT_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}]
    UEFI_HII = 'UEFI HII Configuration'
    BOOT_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}]
    CLOSE_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]
    CLOSE_PXE_STACK = ['User Wait Time', {'UEFI Network Stack': 'Disabled'}]
    LOC_UEFI_HII = ['Console Redirection', 'UEFI HII Configuration']
    
    # Option Rom
    OPEN_OPTION_ROM = 'Console Redirection', 'Lan Configuration', {'Onboard Ethernet Controller': 'Enabled'}, [
        'User Wait Time', {'Boot Mode': 'Legacy'}, {'OPTION ROM Message': 'Enabled'}]
    CLOSE_OPTION_ROM = ['User Wait Time', {'OPTION ROM Message': 'Disabled'}]
    ONBOARD_MSG = 'WangXun\(R\)PXE'
    ASMEDIA_MSG = 'AsmediaTechnologies'
    
    
    
class Upd:
    PASSWORDS=['Adminbios@3','Usersbios@3']
    POWER_LOSS_VALUES=['Stay Off','Last State','Power On']
    
    # 获取BIOS选项值
    LOC_PCIE_INFO=[Msg.PAGE_MAIN_CN,'PCIE Info']
    LOC_CONSOLE=['Console Redirection']
    LOC_PART1=['Lan Configuration','Video Configuration','USB Configuration','Virtualization','Misc Configuration','Server Configuration','Error Management','Hygon CBS','HDD Bind']#Console Redirection菜单下所有需要进入获取值的选项

    LOC_USB_PORT=['Console Redirection','USB Configuration']
    LOC_PART2 =['USB Port Configuration']#Console Redirection->USB Configuration菜单下所有需要进入获取值的选项

    LOC_HYGON=['Console Redirection','Hygon CBS']
    LOC_PART3 =['Cache Prefetcher settings','NBIO Common Options']#Console Redirection->海光设置菜单下所有需要进入获取值的选项

    # 修改BIOS选项
    CHANGE_PART1=[Msg.PAGE_MAIN_CN,'PCIE Info',{'Puti Native Pcie Configuration':'Configuration 1'},{'SLIM1_CPU0 as SATA':'Enabled'},{'SLIM3_CPU1 as SATA':'Enabled'},{'SLIM5_CPU1 as SATA':'Enabled'},'Console Redirection','Lan Configuration',
                  {'Onboard Ethernet Controller':'Enabled'},{'Wake On Lan':'Disabled'},'Console Redirection','Virtualization',{'IOMMU':'Disabled'},{'SVM':'Disabled'},{'SR-IOV Support':'Disabled'},'Console Redirection','Misc Configuration',{'Above 4G Decoding':'Disabled'},
                  {'MMIO High Limit':'4TB'},{'Hide Boot Logo':'Enabled'},{'PCIE Max Payload Size':'512B'},{'PCIE ASPM':'L1'},{'AES':'Disabled'},{'Hyper Threading Technology':'Disabled'},{'Memory CE Storm Threshold':'Disabled'},{'Memory CE Accumulation Threshold':'Disabled'},{'Debug Print Level':'Debug'},
                  {'ENERGY_PERF_BIAS_CFG mode':'User Defined'},{'CPU P-State Control':'P0+P1'},{'CPU C-State Control':'Enabled'}]

    CHANGE_PART2=['Console Redirection','Server Configuration',{'FRB2 Watchdog Timer':'Enabled'},{'FRB2 Watchdog Timer Policy':'Power Off'},{'FRB2 Watchdog Timer Timeout':'30minutes|30 minutes'},{'OS Boot Watchdog Timer':'Enabled'},{'SOL for Baseboard Mgmt':'Enabled'},{'Restore AC Power Loss':'Stay Off'},'Console Redirection','Error Management',{'Platform First Error Handling':'Enabled'},{'MCA Error Threshold Count':'100'},'Console Redirection','Hygon CBS',{'Memory Clock Speed':'1333MHz'},{'Downcore control':'SIX (3 + 3)'},{'Core Performance Boost':'Disabled'},{'SMEE Control':'Disabled'},
                  {'Chipselect Interleaving':'Disabled'},{'Channel Interleaving':'Enabled'},{'NUMA':'None'},{'Memory Interleaving size':'512 Bytes'},{'Redirect scrubber control':'Enabled'},{'Determinism Slider':'Power'},
                  {'RDSEED and RDRAND Control':'Auto'},{'DRAM scrub time':'48 hours|48hours'},{'cTDP Control':'Manual'},{'Efficiency Optimized Mode':'Auto'},{'Bank Interleaving':'Auto'},'Console Redirection','Hygon CBS','Cache Prefetcher settings',{'L1 Stream HW Prefetcher':'Enabled'},{'L2 Stream HW Prefetcher':'Enabled'},'Console Redirection','Hygon CBS','NBIO Common Options',
                  {'NBIO RAS Control':'Disabled'},{'ACS Enable':'Disabled'},'Console Redirection',{'Memory error behavior':'Shutdown System'}]

    CHANGE_PART3_1=['Set Administrator Password','Password Lock Time']
    CHANGE_PART3_2 = ['Set Administrator Password', {'Password Valid Days':'Indefinite'},'User Wait Time',{'Bootup NumLock State':'Off'},{'Internal SHELL':'Enabled'},{'PXE Option Rom':'Disabled'}]
    SET_TIME_ALWAYS=[{'Password Valid Days':'Indefinite'}]
    SET_UPDATE_NOR=[Msg.PAGE_EXIT_CN,{'BIOS Update Parameters':'Reserved Configuration'}]
    SET_UPDATE_ALL = [Msg.PAGE_EXIT_CN, {'BIOS Update Parameters': 'Full Update'}]
    SETUP_LATEST=[Msg.BIOS_UPDATE_CN, Env.USB_VOLUME, '<BIOS>', Env.LATEST_BIOS_FILE]
    SETUP_PREVIOUS = [Msg.BIOS_UPDATE_CN, Env.USB_VOLUME, '<BIOS>', Env.PREVIOUS_BIOS_FILE]
    SETUP_CONSTANT = [Msg.BIOS_UPDATE_CN, Env.USB_VOLUME, '<BIOS>', Env.CONSTANT_BIOS_FILE]
    SETUP_MSG='Flash is updated successfully!'

    SET_DOS=[Msg.PAGE_BOOT_CN,{'Boot Mode':'Legacy'}]
    DOS_FLASH_TOOL=Env.DOS_FLASH_CMD
    ENT_DOS_MSG='Start booting from USB device...|StartbootingfromUSBdevice...'
    DOS_MSG_NOR="End.....................Successed!|> "
    DOS_MSG_ALL="Update ALL..................Successed!| C:\\\BIOS>"

    OPEN_SHELL=[Msg.PAGE_BOOT_CN,{'Boot Mode':'UEFI'},{'Internal SHELL':'Enabled'}]
    SHELL_FLASH_TOOL=Env.SHELL_FLASH_CMD
    SHELL_MSG_NOR="End.....................Successed!"
    SHELL_MSG_ALL="Update ALL..................Successed!"

    LINUX_MSG_NOR = "End.....................Successed!"
    LINUX_MSG_ALL = "Update ALL..................Successed!"

    WINDOWS_FLASH_TOOL=Env.WINDOWS_FLASH_CMD
    WINDOWS_MSG_NOR = "End.....................Successed!"
    WINDOWS_MSG_ALL = "Update ALL..................Successed!"
