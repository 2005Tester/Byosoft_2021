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
    PROJECT_NAME = "Hygon3000CRB"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "Hygon3000CRB\\Report\\template"
    TESTCASE_CSV = "Hygon3000CRB\\AllTest.csv"
    RELEASE_BRANCH = "Hygon_016"
    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\Hygon3000CRB\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com3"

    # BMC Configuration
    BMC_IP = '192.168.6.203'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.151'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2021'

    # Tool definition - Ver 1.8.18
    IPMITOOL = "Hygon3000CRB\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER, BMC_PASSWORD)
    SMBIOS = "Hygon3000CRB\\Tools\\smbios5000\\"

    # BIOS Firmware URL and local path
    BIOS_URL = "http://192.168.6.20/backup/Inspur_Hygon_HG5000_Normal_nvwa"
    NONE_COMMON_BIOS = ["_ali_"]
    BIOS_SIZE = "16777216"
    BIOS_TOOL_PATH = "Hygon3000CRB\\Tools\\ipmitool\\"
    LATEST_BIN_PATH = os.path.join(BIOS_TOOL_PATH, "latest.bin")
    PREVIOUS_BIN_PATH = os.path.join(BIOS_TOOL_PATH, "previous.bin")
    LATEST_ZIP_PATH = os.path.join(BIOS_TOOL_PATH, "latest.zip")
    PREVIOUS_ZIP_PATH = os.path.join(BIOS_TOOL_PATH, "previous.zip")
    LATEST_UNZIP_PATH = os.path.join(BIOS_TOOL_PATH, "latest")
    PREVIOUS_UNZIP_PATH = os.path.join(BIOS_TOOL_PATH, "previous")
    BMC_UPDATE_TOOL = "wsl ./Hygon3000CRB/Tools/ipmitool/loquat -d BIOS -i redfish -f"
    BIOS_UPDATE_LATEST = "{0} Hygon3000CRB/Tools/ipmitool/latest.bin -h {1} -u {2} -p {3}".format(BMC_UPDATE_TOOL, BMC_IP, BMC_USER, BMC_PASSWORD)
    BIOS_UPDATE_PREVIOUS = "{0} Hygon3000CRB/Tools/ipmitool/previous.bin -h {1} -u {2} -p {3}".format(BMC_UPDATE_TOOL, BMC_IP, BMC_USER, BMC_PASSWORD)

    # BIOS remote path
    #LINUX_OS_PATH = "/boot/efi/"
    LINUX_USB_DEVICE = "/dev/sdc4"
    LINUX_USB_MOUNT = "/mnt/"
    #WINDOWS_OS_PATH = "C:\\Users\\Administrator\\"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs7:"

    #BIOS flash command
    LINUX_FLASH_CMD = "./flash bfu"
    LINUX_FLASH_DRIVER_PATH = "/root/"
    LINUX_BIOS_MOUNT_PATH = "/mnt/BIOS/"
    WINDOWS_FLASH_CMD = "ByoWinFlash.exe bfu"
    SHELL_FLASH_CMD = "ByoShellFlash.efi bfu"
    DOS_FLASH_CMD = "byoflash bfu"


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

    #change boot order related cmd with normal method

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
    POST_MESSAGE = '进入固件配置'
    HOTKEY_PROMPT_DEL = 'Del to enter SETUP,'
    HOTKEY_PROMPT_DEL_CN = POST_MESSAGE
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu,'
    HOTKEY_PROMPT_F11_CN = POST_MESSAGE
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot,'
    HOTKEY_PROMPT_F12_CN = POST_MESSAGE

    # pages in bios configuration
    PAGE_MAIN = "Building Info"
    PAGE_MAIN_CN = "编译信息"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_ADVANCED_CN = '串口重定向'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_SECURITY_CN = '设置管理员密码'
    PAGE_BOOT = 'User Wait Time'
    PAGE_BOOT_CN = '用户等待时间'
    PAGE_EXIT = 'Save Changes'
    PAGE_EXIT_CN = '保存修改'

    # menus of main page
    CPU_INFO_CN = '处理器信息'

    # menus of USB configuration
    USB_CONFIG_CN = 'USB配置'
    USB_PORT_CONFIG_CN = 'USB端口配置'

    # menus of Misc configuration
    MISC_CONFIG_CN = 'Misc设置'
    PERFORMANCE_CN = '性能模式'
    CPU_FREQUENCY_CN = '设定CPU频率'

    # menus of update bios
    BIOS_UPDATE_CN = "BIOS固件更新"
    BIOS_UPDATE = "BIOS Update"
    HDD_VOLUME = "SATA:INTEL SSDSCKKB960G8 \(P1\)"
    USB_VOLUME = "USB:SanDisk \(P4\)"

    # 刷新BIOS的文件名
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE = "previous.bin"
    CONSTANT_BIOS_FILE = "constant.bin"

    # menus of boot page
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    ENTER_SETUP = "Enter Setup"

    ENTER_BOOTMENU_CN = "设备启动菜单"
    USB_UEFI = 'UEFI USB: SanDisk'
    CENT_OS_Legacy = 'SATA1\-4: ST1000DM010\-2EP102'
    CENTOS_OS = 'CentOS Linux\(MegaRAID Controller Drive 0 Logical Channel Pun 6\)'
    CENTOS_OS_MSG = 'CentOS'
    KYLIN_OS = 'Kylin Linux Advanced Server\(SATA2-0: INTEL SSDSCKKB960G8\)'
    KYLIN_OS_MSG = "Kylin"
    UOS_OS = 'UOS\(SATA1\-0: TOSHIBA DT01ACA100\)'
    UOS_OS_MSG = "UOS"
    LINUX_OS = KYLIN_OS
    LINUX_OS_MSG = KYLIN_OS_MSG
    WINDOWS_OS = "Windows Boot Manager\(SATA1\-6: TOSHIBA DT01ACA100\)"
    WINDOWS_OS_MSG = "Windows"

    INTERNAL_SHELL_CN = "内置SHELL"
    SHELL = "Internal EDK Shell"
    BOOT_MODE_CN = "启动模式"
    BOOT_MODE = "Boot Mode"
    DOS = "USB: SanDisk"
    BIOS_UPDATE_MODE_CN = "BIOS固件更新参数"
    BIOS_UPDATE_MODE = "BIOS Update Parameters"

    # path of setup menus
    PATH_USB_CFG_CN = [USB_CONFIG_CN, USB_PORT_CONFIG_CN]
    PATH_LATEST_BIOS_UPDATE_CN = [BIOS_UPDATE_CN, USB_VOLUME, LATEST_BIOS_FILE]
    PATH_PREVIOUS_BIOS_UPDATE_CN = [BIOS_UPDATE_CN, USB_VOLUME, PREVIOUS_BIOS_FILE]
    PATH_PERFORMANCE_CN = [MISC_CONFIG_CN, PERFORMANCE_CN]

# CPU related messages
    CPU_FREQUENCY = ['1600', '2000', '2500']  # SetUp下可以设定的CPU频率
    CPU_FREQUENCY_CSTATE = ['3.00', '2.50']  # 海光工具检测，C-State打开、关闭状态下的CPU频率
    CPU_FREQUENCY_PSTATE = ['2.50', '2.00', '1.60']  # 海光工具检测，P0、P1、P2CPU频率
    CPU_FREQUENCY_CPB = ['2.50', '3.00']  # 海光工具检测,超频关闭，打开下CPU频率
    CPU_DOWNCORE_CORE = ['4', '4', '6', '8', '8', '12']#CPU降核
    CPU_NUMA_ONE = ['2', '2', '1', '2']  # NUMA单路CPU分别对应没有、通道、裸片、自动
    CPU_NUMA_TWO = ['4', '4', '2', '4']  # NUMA双路CPU分别对应没有、通道、裸片、自动

 # HDDPassword related messages
    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = "SATA1\-0: TOSHIBA DT01ACA100"
    HDD_PASSWORD_NAME_02 = "SATA2\-0: INTEL SSDSCKKB960G8"
    # HDD_PASSWORD_NAME_02 = "SATA1-0: WDC WD10EZEX-08WN4A0"
    HDD_NAME_01_OS = [LINUX_OS, LINUX_OS_MSG]
    HDD_NAME_02_OS = [KYLIN_OS, KYLIN_OS_MSG]

# IpmBoot related messages
    # IPMITOOL 启动
    IPMITOOL_HDD_BOOT_NAME = '内置硬盘驱动器'
    IPMITOOL_PXE_BOOT_NAME = '内置网络设备'
    IPMITOOL_ODD_BOOT_NAME = 'USB CD/DVD光驱'
    IPMITOOL_USB_BOOT_NAME = 'USB闪存驱动器/USB 硬盘'
    IPMITOOL_OTHER_BOOT_NAME = '其它'

# Ipmitool related messages
    # OEM命令获取和修改Setup选项
    OEM_DEFAULT_VALUE = '00 09 1c 02 20 34 15 10 37 07 05 05 00 26'



# PXE related messages
    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun(R) (B4-05-5D-4F-6B-D2)"
    PXE_NET_ADDON = "Intel E10I2-X540-US (E8-61-1F-29-D8-85)"
    # PXE_NET_ADDON = "Intel PRO\-1000\-DESTOP \(00\-1B\-21\-11\-78\-CB\)"

    # PXE启动项(IPv4)
    PXE_PORT_ADDON = 'UEFI Slot 0: Port \d - Intel E10I2-X540-US PXE IPv4'
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun\(R\) PXE IPv4"

# SetUp related messages
    # 网络唤醒使用
    MAC_ADDRESS = 'B4-05-5D-4F-6B-D3'
    # 硬盘绑定使用
    HDD_BIND_NAME_1 = 'B7D0F2 TOSHIBA DT01ACA100 37FHTDWNS'
    HDD_BIND_NAME_2 = 'B5D0F0 INTEL SSDSCKKB960G8 BTYH019101JK960L'
    HDD_BIND_NAME_1_OS = [LINUX_OS, LINUX_OS_MSG]
    HDD_BIND_NAME_2_OS = [KYLIN_OS, KYLIN_OS_MSG]
    HDD_BIND_PROMPT = '硬盘引导违规'
    # 虚拟化
    IOMMU_DISABLED_INFO = 'AMD IOMMUv2 functionality not available on this system'
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'
    SVM_DISABLED_INFO = 'kvm: disabled by bios'
    OS_TYPE = 'UnionTech OS'
    # 内存频率
    MEMORY_SPEED = ['667', '800', '1067', '1200', '1333']  # SetUp下可以设置的内存频率
    # IOMMU,SVM,SR-IOV默认值
    VIRTUALIZATION_DEFAULT = ['启用', '禁用', '打开']

    # Sata控制器(Sata配置页面,控制器A,B所连接的硬盘)
    SATA_R_A = '\['  # 控制器A所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    SATA_R_B = '\['  # 控制器B所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动









    # Setup密码相关信息
    SET_SETUP_PSW_SUCCESS = '密码设置成功|密码设成功'
    DEL_SETUP_PSW_SUCCESS = '密码删成功|密码删除成功'
    SET_ADMIN_PSW = '设置管理员密码'
    SET_USER_PSW = '设置用户密码'
    ONLY_SET_USER_PSW = '请先设置管理员密码'
    CHARACTERS_LENGTH_NOT_ENOUGH = '请输入足够的字符'
    CHARACTERS_TYPE_NOT_ENOUGH = '警告'
    LOGIN_SETUP_PSW_PROMPT = '系统安全'
    LOGIN_SETUP_PSW_FAIL = '密码错误'
    PSW_ERROR_LOCK = '密码错误，屏幕锁定'
    PSW_LOCK_OPTION = '密码锁定时间'
    PSW_CHECK_ERROR = '密码检查失败'
    PSW_LOCK_60S = '密码错误，屏幕锁定，请等待60秒'
    PSW_LOCK_180S = '密码错误，屏幕锁定，请等待180秒'
    USER_NOT_DEL_PSW = '用户权限不能删除密码'
    NEW_OLD_PSW_DIFF = '密码不同'
    PREVIOUS_5_PSW_SAME = '修改后的密码不能与前五次密码相同！'
    PSW_EXPIRE = '密码已经过期'
    PSW_SET_STATUS = '已安装'
    PWS_NOT_SET_STATUS = '未设定'
    USER_ADMIN_PSW_SAME = '不符合密码安全'
    POWER_ON_PSW_OPTION = '开机密码'
    PSW_EXPIRY_DATE = '设置密码有效期'

    # 硬盘密码相关信息
    HDD_PSW_OPTION = '硬盘密码'
    SET_HDD_PSW_OPTION = '启用硬盘密码'
    DEL_HDD_PSW_OPTION = '禁用硬盘密码'
    HDD_CHARACTERS_LENGTH_NOT_ENOUGH = '密码长度无效'
    HDD_CHARACTERS_TYPE_NOT_ENOUGH = '密码字符类型无效'
    HDD_PSW_NOT_SAME = '密码不符，两次输入的密码必须相同'
    SET_HDD_PSW_SUCCESS = '密码修改已保存'
    LOGIN_HDD_PSW_PROMPT = '输入Hdd密码'
    LOGIN_HDD_PSW_FAIL = '密码错误'
    DEL_HDD_PSW_ERROR = '密码无效'
    HDD_NEW_OLD_PSW_DIFF = '密码不符，两次输入的密码必须相同'
    HDD_LOCK_PROMPT = '请重启并输入正确的密码才可以解开锁住的硬盘'
    HDD_LOCK_STATUS = '无法更改驱动器的安全状态'
    HDD_ESC_LOCK_PROMPT = '密码输入已取消，驱动器仍处于锁定状态'



