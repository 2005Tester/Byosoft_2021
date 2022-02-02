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
    PROJECT_NAME = "Hygon7500CRB"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "Hygon7500CRB\\Report\\template"

    TESTCASE_CSV = "Hygon7500CRB\\AllTest.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\Hygon7500CRB\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com3"

    # BMC Configuration
    BMC_IP = '192.168.6.94'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.174'
    OS_USER = 'root'
    OS_PASSWORD = 'byosoft@1'

    # Tool definition - Ver 1.8.18
    IPMITOOL = "Hygon7500CRB\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER, BMC_PASSWORD)
    SMBIOS = "Hygon7500CRB\\Tools\\smbios7000\\"

    # BIOS Firmware URL and local path
    BIOS_URL = "http://192.168.6.20/backup/Inspur_Hygon_HG5000_Normal_nvwa"
    NONE_COMMON_BIOS = ["_ali_"]
    BIOS_SIZE = "16777216"
    BIOS_TOOL_PATH = "Hygon7500CRB\\Tools\\ipmitool\\"
    LATEST_BIN_PATH = os.path.join(BIOS_TOOL_PATH, "latest.bin")
    PREVIOUS_BIN_PATH = os.path.join(BIOS_TOOL_PATH, "previous.bin")
    LATEST_ZIP_PATH = os.path.join(BIOS_TOOL_PATH, "latest.zip")
    PREVIOUS_ZIP_PATH = os.path.join(BIOS_TOOL_PATH, "previous.zip")
    LATEST_UNZIP_PATH = os.path.join(BIOS_TOOL_PATH, "latest")
    PREVIOUS_UNZIP_PATH = os.path.join(BIOS_TOOL_PATH, "previous")
    BMC_UPDATE_TOOL = "wsl ./Hygon7500CRB/Tools/ipmitool/loquat -d BIOS -i redfish -f"
    BIOS_UPDATE_LATEST = "{0} Hygon7500CRB/Tools/ipmitool/latest.bin -h {1} -u {2} -p {3}".format(BMC_UPDATE_TOOL, BMC_IP, BMC_USER, BMC_PASSWORD)
    BIOS_UPDATE_PREVIOUS = "{0} Hygon7500CRB/Tools/ipmitool/previous.bin -h {1} -u {2} -p {3}".format(BMC_UPDATE_TOOL, BMC_IP, BMC_USER, BMC_PASSWORD)


 
    # BIOS remote path
    #LINUX_OS_PATH = "/boot/efi/"
    LINUX_USB_DEVICE = "/dev/sda4"
    LINUX_USB_MOUNT = "/mnt/"
    #WINDOWS_OS_PATH = "C:\\Users\\Administrator\\"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs0:"



    #BIOS flash command
    LINUX_FLASH_CMD = "./flash bfu"
    LINUX_FLASH_DRIVER_PATH = "/root/"
    LINUX_BIOS_MOUNT_PATH = "/mnt/BIOS/"
    WINDOWS_FLASH_CMD = "ByoWinFlash.exe bfu"
    SHELL_FLASH_CMD = "ByoShellFlash.efi bfu"
    DOS_FLASH_CMD = "byoflash bfu"
    LATEST_BIOS = "latest.bin"
    PREVIOUS_BIOS = "previous.bin"
    CONSTANT_BIOS="constant.bin"



    # CPU, DIMM info
    CPU_info = ['Processor ID\s+000606A6', 'Processor Frequency\s+2.000GHz']
    DIMM_info = ['DIMM020\(C\)\s+S0.CC.D0:2933MT/s Hynix DRx4 32GB RDIMM']



    #change CPU fan speed related cmd
    FAN_MANUAL = "{0} raw 0x3e 0x2b 0xcc 0xcb 0x00 0x00 0xff ".format(IPMITOOL)
    FAN_SPEED_20 = FAN_MANUAL + "0x14 0x14 0x14 0x14 0x14 0x14 0x14 0x14"
    FAN_SPEED_25 = FAN_MANUAL + "0x19 0x19 0x19 0x19 0x19 0x19 0x19 0x19"
    FAN_SPEED_30 = FAN_MANUAL + "0x1E 0x1E 0x1E 0x1E 0x1E 0x1E 0x1E 0x1E"
    FAN_SPEED_40 = FAN_MANUAL + "0x28 0x28 0x28 0x28 0x28 0x28 0x28 0x28"
    FAN_SPEED_50 = FAN_MANUAL + "0x32 0x32 0x32 0x32 0x32 0x32 0x32 0x32"
    FAN_AUTO = "{0} raw 0x3e 0x2b 0xcc 0xcb 0x00 0x01 0xff 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00".format(IPMITOOL)

    #change boot order related cmd with raw method
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

    #Check or clear boot flag
    BOOT_FLAG_GET = "{0} raw 0x00 0x09 0x05 0x00 0x00".format(IPMITOOL)
    BOOT_FLAG_CLEAR = "{0} raw 0x00 0x08 0x05 0x00 0x00 0x00 0x00 0x00".format(IPMITOOL)

    #BMC control or check related command
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
    POST_MESSAGE = 'enter SETUP'
    HOTKEY_PROMPT_DEL = 'F2 to enter SETUP,'
    HOTKEY_PROMPT_DEL_CN = POST_MESSAGE
    HOTKEY_PROMPT_F11 = 'Press F7 to enter Boot Menu,'
    HOTKEY_PROMPT_F11_CN = POST_MESSAGE
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot,'
    HOTKEY_PROMPT_F12_CN = POST_MESSAGE

    # pages in bios configuration
    PAGE_MAIN = "CPU Info"
    PAGE_APPLIANCES = 'PCIE Configuration'
    PAGE_ADVANCED = 'Sys Debug Mode'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Load Setup Defaults'

    PAGE_ALL = [PAGE_MAIN,PAGE_APPLIANCES,PAGE_ADVANCED,PAGE_SECURITY,PAGE_BOOT,PAGE_EXIT]


    # main
    CPU_INFO = 'CPU Info'
    MEM_INFO = 'Memory Info'
    DATE_TIME = 'System Date and Time'
    SYS_SUMMARY = 'System Summary'
    PSP = 'PSP Firmware Uersions'
    SEL_LANG = 'Select Language'


    # Device
    PCIE_CONFIG = 'PCIE Configuration'
    VIDEO_CONFIG = 'Video Configuration'
    SATA_CONFIG = 'SATA Configuration'
    SATA_INFO = 'SATA Information'
    NVME_DEVICE = 'NVME Device'
    USB_CONFIG = 'USB Configuration'
    PCI_DEVICE = 'PCI Device Info'


    # Advanced
    ABOVE_4G_DECODING = 'Above 4G Decoding'
    PCIE_MAX_PAYLOAD = 'PCIE Max Payload Size'
    PCIE_MAX_READ = 'PCIE Max Read Request Size'
    ASPM_SUPPORT = 'ASPM Support'

    SMT_MODE = 'SMT Mode'
    SVM_CONTROL = 'SVM Control'
    P_STATE = 'P-State Control'
    SR_IOV = 'SR-IOV Support'

    NUMA = 'NUMA'

    RAS_PCIE_CE = 'RAS PCIE CE'
    RAS_CE_SMI = 'RAS CE Smi Threshoid'
    APEI_EINJ_CPU_CE_SUPPORT = 'APEI EINJ CPU CE Support'

    CONSOLE_REDIRECTION = 'Console Redirection'
    SERVER_CONFIG = 'Server Configuration'
    WAKE_FROM_RTC = 'Wake from RTC'
    SATA_PCIE_Switch = 'SATA/PCIE Switch'
    HYGON_CBS = 'Hygon CBS'
    UEFI_HII_CONFIG = 'UEFI HII Configuration'


    # Security
    SET_ADMIN_PSW = 'Set Administrator Password'
    SET_USER_PSW = 'Set User Password'
    PSW_VALID_DAYS = 'Set Password Valid Days'
    POWER_ON_PSW = 'Power-on Password'

    TPM_SEL_CN = 'TPM Select'
    TCG2_CONFIG = 'TCG2 Configuration'
    HDD_PSW_CN = 'HDD Password'
    TCM_CONFIG = 'TCM Configuration'
    SECURE_BOOT = 'Secure Boot'
    HDD_BIND = 'HDD Bind'

    # Password related messages
    SET_SETUP_PSW_SUCCESS = 'Password Setting Successfully'
    DEL_SETUP_PSW_SUCCESS = 'Password deleted succeeded'

    # Boot
    NUMLOCK_STATE = 'Bootup NumLock State'
    BOOT_OPTION_FILTER = 'Boot option filter'
    INTERNAL_SHELL = 'Internal Shell'
    NETWORK_BOOT = 'Network Boot'
    PXE_RETRY = 'PXE Retry'
    PXE_IP_VER_CN = 'Net Boot IP Version'
    HTTP_BOOT = 'Http Boot'

    PCI_ROM_PRIORITY = 'PCI ROM Priority'

    # UEFI BOOT Order
    HDD_BOOT_NAME = 'Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive'
    USB_BOOT_CD_NAME = 'USB CD/DVD ROM Drive'
    OTHER_BOOT_NAME = 'Others'

    # Legacy BOOT Order
    HDD_BOOT_NAME_CN = 'Hard Drive'
    PXE_BOOT_NAME_CN = 'Network Adapter'
    ODD_BOOT_NAME_CN = 'CD/DVD ROM Drive'
    USB_BOOT_NAME_CN = 'USB Flash Drive/USB Hard Disk'
    USB_BOOT_CD_NAME_CN = 'USB CD/DVD ROM Drive'
    OTHER_BOOT_NAME_CN = 'Others'


    # EXIT
    LOAD_SETUP_DEFAUITS = 'Load Setup Defauits'
    SAVE_EXIT = 'Save and Exit'

    SHUTDOWN = 'Shutdown System'
    REBOOT = 'Reboot System'

    BIOS_UPDATE = 'BIOS Update'
    BOOT_MANAGER = 'Boot Manager'




#启动菜单
    # menus of boot page
    # ENTER_BOOTMENU_CN = "设备启动菜单"
    ENTER_BOOTMENU_CN = "Startup Device Menu"
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: Kingston'
    SHELL = "Internal EDK Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Intel Ethernet Server Adapter I350-T2 PXE IPv4"
    PXE_PORT2 = "UEFI Intel Ethernet Server Adapter I350-T2-2 PXE IPv4"
    OS_MSG = 'Kylin|Tencent|CentOS'
    CENT_OS_Legacy = 'SATA1\-4: ST1000DM010\-2EP102'
    CENTOS_OS = 'CentOS Linux\(MegaRAID Controller Drive 0 Logical Channel Pun 6\)'
    CENTOS_OS_MSG = 'CentOS'
    KYLIN_OS = "UOS\(UEFI SATA1-6: ST1000DM010\-2EP102\)"
   
    KYLIN_OS_MSG = 'UOS'
    UOS_OS = 'Kylin Linux Desktop\(UEFI NVME: Samsung SSD 980 PRO 250GB\)'
    UOS_OS_MSG = 'Kylin'
    HTTP_NAME1 = 'UEFI Intel\(R\) Ethernet Server Adapter I350-T2-2 HTTP IPv4'
    HTTP_NAME2 = 'UEFI Intel\(R\) Ethernet Server Adapter I350-T2-2 HTTP IPv6'
    HTTP_IPV4_MSG = 'Start HTTP Boot over IPv4'
    HTTP_IPV6_MSG = 'Start HTTP Boot over IPv6'
    PXE_IPV4_MSG = 'Start PXE over IPv4'
    PXE_IPV6_MSG = 'Start PXE over IPv6'
    PXE_IPV4_MSG_ERROR = 'No valid offer received'



    LINUX_OS = KYLIN_OS
    LINUX_OS_MSG = KYLIN_OS_MSG
    WINDOWS_OS = KYLIN_OS
    WINDOWS_OS_MSG = KYLIN_OS_MSG


    # path of setup menus


#CPU related messages
    CPU_FREQUENCY = ['1200', '1600', '2000']#SetUp下可以设定的CPU频率
    CPU_FREQUENCY_CSTATE=['3.00','2.50']#海光工具检测，C-State打开、关闭状态下的CPU频率
    CPU_FREQUENCY_PSTATE=['2.50', '1.60', '1.20']

    CPU_FREQUENCY_CPB=['2.00','3.00']#海光工具检测,超频关闭，打开下CPU频率
    CPU_DOWNCORE_CORE=['8','8','12','16','16','24']#CPU降核

    CPU_NUMA_ONE=['1','4','4','1','4']#NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO=['1','8','8','2','8']#NUMA双路CPU分别对应插槽、没有、通道、裸片、自动

#HDDPassword related messages
    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = 'SATA1-5: ST1000DM010-2EP102'
    HDD_PASSWORD_NAME_02 = 'SATA1-4: ST1000DM010-2EP102'
    # HDD_PASSWORD_NAME_03 = 'NVME\(PCI2\-0\-0\): SAMSUNG MZVLW256HEHP\-000L7'
    HDD_NAME_01_OS = [KYLIN_OS, KYLIN_OS_MSG]
    HDD_NAME_02_OS = [UOS_OS, UOS_OS_MSG]





#PXE related messages
    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun(R) (B4-05-5D-8E-91-B2)"
    PXE_NET_ADDON = "Intel PRO-1000-DESTOP (00-1B-21-11-78-CB)"

    # PXE启动项(IPv4)
    PXE_PORT_ADDON = 'UEFI Slot 32: Port \d - Intel E10I2-X540-US PXE IPv4'
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun\(R\) PXE IPv4"

#SetUp related messages
    # 网络唤醒MAC地址
    MAC_ADDRESS = 'B4-05-5D-8E-91-B2'
    # 硬盘绑定
    # HDD_BIND_NAME_1 = 'Kylin Linux Advanced Server\(UEFI SATA1\-8: ST1000DM010-2EP102\)'
    HDD_BIND_NAME_1 ='UOS(UEFI SATA1-6: ST1000DM010-2EP102)'
    # HDD_BIND_NAME_1 = 'Kylin Linux Advanced Server'
    HDD_BIND_NAME_2 = 'Kylin Linux Desktop\(UEFI NVME: Samsung SSD 980 PRO 250GB\)'
    HDD_BIND_NAME_1_OS = [KYLIN_OS, KYLIN_OS_MSG]
    HDD_BIND_NAME_2_OS = [UOS_OS, UOS_OS_MSG]
    HDD_BIND_PROMPT = 'Hdd has been changed'
    # 虚拟化
    IOMMU_DISABLED_INFO = 'AMD IOMMUv2 functionality not available on this system'
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'
    SVM_DISABLED_INFO = 'kvm: disabled by bios'
    SRIOV_DISABLED_INFO = 'Unable to allocate interrupt, Error: -1'
    OS_TYPE = 'UnionTech OS'
    #内存频率
    MEMORY_SPEED=['667', '800', '933', '1067', '1200', '1333', '1467', '1600']#SetUp下可以设置的内存频率


    # SATA控制器(Sata配置页面,控制器A,B所连接的硬盘)
    SATA_R_A = '\['  # 控制器A所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    SATA_R_B = '\['  # 控制器B所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动



    CHARACTERS_LENGTH_NOT_ENOUGH = 'characters'
    CHARACTERS_TYPE_NOT_ENOUGH = 'Warning'
    LOGIN_SETUP_PSW_PROMPT = 'System Security'
    LOGIN_SETUP_PSW_FAIL = 'Invalid Password'
    PSW_ERROR_LOCK = 'Fatal Error... System Halted'
    PSW_CHECK_ERROR = 'Incorrect password'
    NEW_OLD_PSW_DIFF = 'Passwords are not the same|not the same'
    PREVIOUS_5_PSW_SAME = 'Password has been used by the latest 5 times|latest 5 times'
    PSW_EXPIRE = 'Password expired, Please change it as soon as possible|Password expired|as soon as possible'
    PSW_SET_STATUS = 'Installed'
    POWER_ON_PSW_OPTION = 'Power-on Password'
    PSW_EXPIRY_DATE = 'Set Password Valid Days'

    HDD_PSW_OPTION = 'HDD Password'
    SET_HDD_PSW_OPTION = 'Enable HDD Password'
    DEL_HDD_PSW_OPTION = 'Disable HDD Password'
    HDD_CHARACTERS_LENGTH_NOT_ENOUGH = 'Invalid Password Length'
    HDD_CHARACTERS_TYPE_NOT_ENOUGH = 'The password must contain at least one space or special character'
    SET_HDD_PSW_SUCCESS = 'Changes have been saved'
    LOGIN_HDD_PSW_PROMPT = 'Enter HDD Password'
    LOGIN_HDD_PSW_FAIL = 'Incorrect password'
    DEL_HDD_PSW_ERROR = 'Invalid Password'
    HDD_NEW_OLD_PSW_DIFF = 'Passwords are not the same'
    HDD_LOCK_PROMPT = "The number of incorrect password entries has reached the upper limit"
    HDD_LOCK_STATUS = "security state cannot be changed"
    HDD_ESC_LOCK_PROMPT = 'Password input cancelled'




class Boot:
    # Boot PATH
    post_information_path = [Msg.PAGE_ADVANCED,Msg.SERVER_CONFIG]
    BOOT_TO_CPU0 = ['CPU 0']
    quick_boot_hotkey= [Msg.PAGE_APPLIANCES]
    BOOT_Network_Boot = [Msg.PAGE_BOOT,{Msg.NETWORK_BOOT: 'Enabled'}]


class Cpu:
    SET_STM_DISABLED = [Msg.PAGE_ADVANCED,{Msg.SMT_MODE: 'Disabled'}]
    SET_STM_ENABLED = [Msg.PAGE_ADVANCED, {Msg.SMT_MODE: 'Enabled'}]
    SET_CSTATE_ENABLED = [Msg.PAGE_ADVANCED, {Msg.P_STATE: 'Enabled'},Msg.HYGON_CBS,'Moksha Common Options',{'Core Performance Boost': 'Auto'},{'Global C-state Control': 'Enabled'}]
    SET_CSTATE_DISABLED = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'Moksha Common Options', {'Global C-state Control': 'Disabled'}]
    SET_CSTATE_AUTO = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'Moksha Common Options', {'Global C-state Control': 'Auto'}]

    SET_PSTATE_DISABLED = [Msg.PAGE_ADVANCED, {Msg.P_STATE: 'Disabled'}]
    SET_PSTATE_ENABLED = [Msg.PAGE_ADVANCED, {Msg.P_STATE: 'Enabled'}]

    SET_CPB_DISABLED = [Msg.PAGE_ADVANCED, {Msg.P_STATE: 'Enabled'}, Msg.HYGON_CBS, 'Moksha Common Options', {'Core Performance Boost': 'Disabled'},{'Global C-state Control': 'Enabled'}]
    SET_CPB_AUTO = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'Moksha Common Options', {'Core Performance Boost': 'Auto'}]

    SET_NUMA_DISABLED = [Msg.PAGE_ADVANCED, {Msg.NUMA: 'Disabled'}]
    SET_NUMA_ENABLED = [Msg.PAGE_ADVANCED, {Msg.NUMA: 'Enabled'}]


class HDDPassword:
    # HDDPassword
    SET_HDDPASSWORD = [Msg.SET_ADMIN_PSW,Msg.HDD_PSW_OPTION]


class PCIE:
    SET_PAYLOAD_128B = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_PAYLOAD: '128B'}]
    SET_PAYLOAD_256B = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_PAYLOAD: '256B'}]
    SET_PAYLOAD_512B = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_PAYLOAD: '512B'}]
    SET_PAYLOAD_AUTO = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_PAYLOAD: 'Auto'}]

    SET_READ_REQUEST_128B = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_READ: '128B'}]
    SET_READ_REQUEST_256B = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_READ: '256B'}]
    SET_READ_REQUEST_512B = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_READ: '512B'}]
    SET_READ_REQUEST_AUTO = [Msg.PAGE_ADVANCED, {Msg.PCIE_MAX_READ: 'Auto'}]

    SET_ASPM_L1 = [Msg.PAGE_ADVANCED, {Msg.ASPM_SUPPORT: 'L1'}]
    SET_ASPM_DISABLED = [Msg.PAGE_ADVANCED, {Msg.ASPM_SUPPORT: 'Disabled'}]

    SET_4G_DECODING_ENABLED = [Msg.PAGE_ADVANCED, {Msg.ABOVE_4G_DECODING: 'Enabled'}]
    SET_4G_DECODING_DISABLED = [Msg.PAGE_ADVANCED, {Msg.ABOVE_4G_DECODING: 'Disabled'}]

    BOOT_PCIE_CONFIG = [Msg.PAGE_APPLIANCES]


class PXE:
    SET_NETWORK_BOOT_DISABLED = [Msg.PAGE_BOOT,{Msg.NETWORK_BOOT: 'Disabled'}]
    SET_NETWORK_BOOT_ENABLED = [Msg.PAGE_BOOT, {Msg.NETWORK_BOOT: 'Enabled'}]

    SET_IP_VERSION_IPv4 = [Msg.PAGE_BOOT, {Msg.BOOT_OPTION_FILTER: 'UEFI Only'}, {Msg.NETWORK_BOOT: 'Enabled'}, {Msg.PXE_IP_VER_CN: 'IPv4'}]
    SET_IP_VERSION_IPv6 = [Msg.PAGE_BOOT, {Msg.PXE_IP_VER_CN: 'IPv6'}]

    PXE_LEGACY_BOOT = [Msg.PAGE_BOOT, {Msg.BOOT_OPTION_FILTER: 'Legacy Only'},{Msg.NETWORK_BOOT: 'Enabled'}]

    SET_PXE_RETRY_DISABLED = [Msg.PAGE_BOOT,{Msg.BOOT_OPTION_FILTER: 'UEFI Only'}, {Msg.NETWORK_BOOT: 'Enabled'}, {Msg.PXE_IP_VER_CN: 'IPv4'}, Msg.PXE_RETRY]
    SET_PXE_RETRY_ENABLED = [Msg.PAGE_BOOT, Msg.PXE_RETRY]

    PCIE_CONFIG = [Msg.PAGE_BOOT, {Msg.BOOT_OPTION_FILTER: 'UEFI Only'}, Msg.PAGE_APPLIANCES]
    SET_IP_VERSION_ALL = [Msg.PAGE_BOOT, {Msg.NETWORK_BOOT: 'Enabled'}, {Msg.PXE_IP_VER_CN: 'All'}]

    SET_HTTP_ENABLED1 = [Msg.PAGE_BOOT, {Msg.NETWORK_BOOT: 'Enabled'}, {Msg.PXE_IP_VER_CN: 'IPv4'},{Msg.HTTP_BOOT: 'Enabled'}]
    SET_HTTP_ENABLED2 = [Msg.PAGE_BOOT, {Msg.NETWORK_BOOT: 'Enabled'}, {Msg.PXE_IP_VER_CN: 'IPv6'}, {Msg.HTTP_BOOT: 'Enabled'}]
    SET_HTTP_DISABLED = [Msg.PAGE_BOOT, {Msg.HTTP_BOOT: 'Disabled'}]


class Setup:
    IN_MEMORY_INFO = [Msg.PAGE_MAIN, Msg.MEM_INFO]
    SET_ETH_CONTROLLER_DISABLED = [Msg.PAGE_APPLIANCES, {'OCP\(J38 8X\)': 'Disabled'}, Msg.PAGE_BOOT, {Msg.BOOT_OPTION_FILTER: 'UEFI Only'}, {Msg.NETWORK_BOOT: 'Enabled'}, {Msg.PXE_IP_VER_CN: 'IPv4'}]

    SET_USB_MASS_DISABLED = [Msg.PAGE_BOOT,{Msg.BOOT_OPTION_FILTER: 'UEFI Only'},Msg.PAGE_APPLIANCES,Msg.USB_CONFIG,{'USB Mass Storage Support': 'Disabled'},{'USB Port 0': 'Enabled'},{'USB Port 1': 'Enabled'},{'USB Port 2': 'Enabled'},{'USB Port 3': 'Enabled'}]
    SET_USB_MASS_ENABLED = [Msg.PAGE_APPLIANCES,Msg.USB_CONFIG,{'USB Mass Storage Support': 'Enabled'}]

    IN_USB_CONFIG = [Msg.PAGE_APPLIANCES, Msg.USB_CONFIG]
    SET_USB1_DISABLED = [{'USB Port 1': 'Disabled'}]
    SET_USB0_DISABLED = [{'USB Port 0': 'Disabled'}]
    SET_USB_ENABLED = [{'USB Port 0': 'Enabled'},{'USB Port 1': 'Enabled'}]

    SET_IOMMU_DISABLED = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'NBIO Common Options', 'NB Configuration', {'IOMMU': 'Disabled'}]
    SET_IOMMU_ENABLED = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'NBIO Common Options', 'NB Configuration', {'IOMMU': 'Enabled'}]
    SET_IOMMU_AUTO = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'NBIO Common Options', 'NB Configuration', {'IOMMU': 'Auto'}]

    HDD1_BIND = [Msg.PAGE_SECURITY, Msg.HDD_BIND, {Msg.HDD_BIND: Msg.HDD_BIND_NAME_1}]
    HDD2_BIND = [Msg.PAGE_SECURITY, Msg.HDD_BIND, {Msg.HDD_BIND: Msg.HDD_BIND_NAME_2}]
    HDD_UNBIND = [Msg.PAGE_SECURITY, Msg.HDD_BIND, {Msg.HDD_BIND: 'Unbind'}]

    SET_SECURE_BOOT_AUTO = [Msg.PAGE_BOOT, {Msg.BOOT_OPTION_FILTER: 'UEFI Only'}, {Msg.INTERNAL_SHELL: 'Enabled'}, Msg.PAGE_SECURITY, Msg.SECURE_BOOT, {'Secure Boot Default Key Provision': 'Auto'}]
    SET_SECURE_BOOT_MANUAL = [Msg.PAGE_SECURITY, Msg.SECURE_BOOT, {'Secure Boot Default Key Provision': 'Manual'}, 'Reset to Setup Mode']

    SET_USER_WAIT_TIME = [Msg.PAGE_BOOT]
    SET_BOOT_FILTER = [{Msg.BOOT_OPTION_FILTER: 'UEFI Only'}]

    SET_SVM_DISABLED = [Msg.PAGE_ADVANCED, {Msg.SVM_CONTROL: 'Disabled'}]
    SET_SVM_ENABLED = [Msg.PAGE_ADVANCED, {Msg.SVM_CONTROL: 'Enabled'}]

    SET_SR_IOV_DISABLED = [Msg.PAGE_ADVANCED, {Msg.SR_IOV: 'Disabled'}]
    SET_SR_IOV_ENABLED = [Msg.PAGE_ADVANCED, {Msg.SR_IOV: 'Enabled'}]

    SET_MEMORY_SPEED = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'UMC Common Options', 'DDR4 Common Options', 'DRAM Timing Configuration', 'I Accept', {'Allow setting memory frequency': 'Enabled'}]
    MEMORY_CLOCK_SPEED = 'Memory Clock Speed'
    SET_MEMORY_SPEED_AUTO = [Msg.PAGE_ADVANCED, Msg.HYGON_CBS, 'UMC Common Options', 'DDR4 Common Options', 'DRAM Timing Configuration', 'I Accept', {'Memory Clock Speed': 'Auto'}, {'Allow setting memory frequency': 'Auto'}]

    SAVE_CHANGE_ESC_DISABLED = [Msg.PAGE_ADVANCED, {Msg.SVM_CONTROL: 'Disabled'}, {Msg.P_STATE: 'Disabled'}, {Msg.SR_IOV: 'Disabled'}]
    SAVE_CHANGE_ENABLED = [Msg.PAGE_ADVANCED, {Msg.SVM_CONTROL: 'Enabled'}, {Msg.P_STATE: 'Enabled'}, {Msg.SR_IOV: 'Enabled'}]

    SAVE_CHANGE_EXIT_DISABLED = [Msg.PAGE_ADVANCED, {Msg.SVM_CONTROL: 'Disabled'}, {Msg.P_STATE: 'Disabled'}, {Msg.SR_IOV: 'Disabled'}, Msg.PAGE_EXIT, Msg.SAVE_EXIT]

    SYS_DEBUG_MODE = [Msg.PAGE_ADVANCED]

    IN_SATA_INFO = [Msg.PAGE_APPLIANCES, Msg.SATA_INFO]
    IN_SATA_CONFIG = [Msg.PAGE_APPLIANCES, Msg.SATA_CONFIG]

    SET_SATA_CONTROLLER1_DISABLED = [Msg.PAGE_APPLIANCES, Msg.SATA_CONFIG, {'SATA Controller 1': 'Disabled'}]
    SET_SATA_CONTROLLER1_ENABLED = [Msg.PAGE_APPLIANCES, Msg.SATA_CONFIG, {'SATA Controller 1': 'Enabled'}]

    SATA_PCIE_Switch_PCIE = [Msg.PAGE_ADVANCED, Msg.SATA_PCIE_Switch, {'J112': 'PCIE'}]
    SATA_PCIE_Switch_SATA = [Msg.PAGE_ADVANCED, Msg.SATA_PCIE_Switch, {'J112': 'SATA'}]


class PSW:
    SET_ADMIN_PSW = [Msg.SET_ADMIN_PSW]
    SET_USER_PSW = [Msg.SET_ADMIN_PSW, Msg.SET_USER_PSW]


class Smbios:
    SET_BOOT_MODE_UEFI = [Msg.PAGE_BOOT, {Msg.BOOT_OPTION_FILTER: "UEFI Only"}]
    CPU_INFO = [Msg.PAGE_MAIN]