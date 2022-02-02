#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-


# Key mapping
class Key:
    ADD=[chr(0x2B)]#+
    SUBTRACT=[chr(0x2D)]#-
    ENTER = [chr(0x0D)]
    DEL = [chr(0x7F)]
    F2 = [chr(0x1b), chr(0x32)]
    F5 = [chr(0x1b),chr(0x35)]
    F6 = [chr(0x1b), chr(0x36)]
    F9 = [chr(0x1b), chr(0x39)]
    F10 = [chr(0x1b), chr(0x30)]
    F11 = [chr(0x1b), chr(0x21)]
    F12 = [chr(0x1b), chr(0x40)]
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]
    CONTROL = '\ue009'
    DISCARD_CHANGES = ['N']
    RESET_DEFAULT = [F9, Y]
    SAVE_RESET = [F10, Y]
    CONTROL_F11 = [CONTROL, F11]


# Messages to identify a specific boot option, page, menu or system status
class Msg:
    POST_MESSAGE = '进入固件配置|进入启动菜单|进入网络启动'
    HOTKEY_PROMPT_DEL = 'Del to enter SETUP,'
    HOTKEY_PROMPT_DEL_CN = POST_MESSAGE
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu,'
    HOTKEY_PROMPT_F11_CN = POST_MESSAGE
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot,'
    HOTKEY_PROMPT_F12_CN = POST_MESSAGE

    # pages in bios configuration
    PAGE_MAIN = "Building Info"
    PAGE_MAIN_CN = "固件信息"
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

    #刷新BIOS的文件名
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE = "previous.bin"
    CONSTANT_BIOS_FILE="constant.bin"


    # menus of boot page
    # ENTER_BOOTMENU_CN = "设备启动菜单"
    ENTER_BOOTMENU_CN = "设备启动菜单|按ENTER选择启动设备"
    ENTER_SETUP = "Enter Setup"
    USB_UEFI='UEFI USB: SanDisk'
    SHELL = "Internal EDK Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    OS_MSG='Kylin|Tencent|CentOS'
    CENT_OS_Legacy='SATA1\-4: ST1000DM010\-2EP102'
    CENTOS_OS='CentOS Linux\(MegaRAID Controller Drive 0 Logical Channel Pun 6\)'
    CENTOS_OS_MSG='CentOS'
    KYLIN_OS="Kylin Linux Advanced Server\(SATA3-0: WDC WD10EZEX-08WN4A0\)"
    KYLIN_OS_MSG='Kylin'
    UOS_OS='UOS\(SATA3\-1: SanDisk SDSSDH3 500G\)'
    UOS_OS_MSG='UOS'
    LINUX_OS = KYLIN_OS
    LINUX_OS_MSG = KYLIN_OS_MSG
    WINDOWS_OS = KYLIN_OS
    WINDOWS_OS_MSG = KYLIN_OS_MSG
    INTERNAL_SHELL_CN = "内置SHELL"
    BOOT_MODE_CN = "启动模式"
    BOOT_MODE = "Boot Mode"
    BIOS_UPDATE_MODE_CN = "BIOS固件更新参数"
    BIOS_UPDATE_MODE = "BIOS Update Parameters"

   # path of setup menus
    PATH_USB_CFG_CN = [USB_CONFIG_CN, USB_PORT_CONFIG_CN]
    PATH_LATEST_BIOS_UPDATE_CN = [BIOS_UPDATE_CN, USB_VOLUME, LATEST_BIOS_FILE]
    PATH_PREVIOUS_BIOS_UPDATE_CN = [BIOS_UPDATE_CN, USB_VOLUME, PREVIOUS_BIOS_FILE]
    PATH_PERFORMANCE_CN = [MISC_CONFIG_CN, PERFORMANCE_CN]

    # OS related messages
    IOMMU_DISABLED_INFO = 'AMD IOMMUv2 functionality not available on this system'
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'
    SVM_DISABLED_INFO = 'kvm: disabled by bios'
    OS_TYPE = 'UnionTech OS'


    #SATA控制器(Sata配置页面,控制器A,B所连接的硬盘)
    SATA_R_A='\['#控制器A所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动
    SATA_R_B='\['#控制器B所连接硬盘的名称(只需第一行，且开头第一个字符必须要有)，如果连接两个硬盘则只需要其中随机一个硬盘的名称即可,如果没有连接硬盘就保持原来的值不需要改动


    #PXE启动网卡
    PXE_NET_ONBOARD="WangXun(R) (B4-05-5D-8E-91-B2)"
    PXE_NET_ADDON="Intel PRO-1000-DESTOP (00-1B-21-11-78-CB)"

    #PXE启动项(IPv4)
    PXE_PORT_ADDON='UEFI Slot 32: Port \d - Intel E10I2-X540-US PXE IPv4'
    PXE_PORT_ONBOARD="UEFI Onboard: Port \d - WangXun\(R\) PXE IPv4"


    # 网络唤醒MAC地址
    MAC_ADDRESS = 'B4-05-5D-8E-91-B2'


    #OEM命令获取和修改Setup选项
    OEM_DEFAULT_VALUE='00 09 1c 06 20 34 15 10 37 07 05 05 00 36'

    #硬盘密码
    HDD_PASSWORD_NAME_01 = 'SATA3\-0: WDC WD10EZEX-08WN4A0'
    HDD_PASSWORD_NAME_02 = 'SATA3\-1: SanDisk SDSSDH3 500G'
    HDD_PASSWORD_NAME_03 = 'NVME\(PCI2\-0\-0\): SAMSUNG MZVLW256HEHP\-000L7'
    HDD_NAME_01_OS = [KYLIN_OS, KYLIN_OS_MSG]
    HDD_NAME_02_OS = [UOS_OS, UOS_OS_MSG]




    #硬盘绑定
    HDD_BIND_NAME_1 = 'B4D0F0 WDC WD10EZEX-08WN4A0 WD-WCC6Y3KRDTNP'
    HDD_BIND_NAME_2 = 'B4D0F0 SanDisk SDSSDH3 500G 2104DG444004'
    HDD_BIND_NAME_1_OS=[KYLIN_OS,KYLIN_OS_MSG]
    HDD_BIND_NAME_2_OS = [UOS_OS, UOS_OS_MSG]
    HDD_BIND_PROMPT='硬盘引导违规'


    # Password related messages
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
    PSW_LOCK_OPTION = '锁定时间'
    PSW_CHECK_ERROR = '密码检查失败|失败'
    PSW_LOCK_60S = '密码错误，屏幕锁定，请重启或者等待60秒|密码错误，屏幕锁定，请等待60秒'
    PSW_LOCK_180S = '密码错误，屏幕锁定，请重启或者等待180秒|密码错误，屏幕锁定，请等待180秒'
    USER_NOT_DEL_PSW = '用户权限不能删除密码'
    NEW_OLD_PSW_DIFF = '密码不同'
    PREVIOUS_5_PSW_SAME = '修改后的密码不能与前五次密码相同！'
    PSW_EXPIRE = '密码已经过期'
    PSW_SET_STATUS = '已安装'
    PWS_NOT_SET_STATUS = '未设定'
    USER_ADMIN_PSW_SAME = '不符合密码安全'
    POWER_ON_PSW_OPTION = '开机密码'
    PSW_EXPIRY_DATE = '有效期'

    HDD_PSW_OPTION = '硬盘密码'
    SET_HDD_PSW_OPTION = '启用硬盘密码'
    DEL_HDD_PSW_OPTION = '禁用硬盘密码'
    HDD_CHARACTERS_LENGTH_NOT_ENOUGH = '密码长度无效'
    HDD_CHARACTERS_TYPE_NOT_ENOUGH = '密码字符类型无效'
    SET_HDD_PSW_SUCCESS = '密码修改已保存'
    LOGIN_HDD_PSW_PROMPT = '输入Hdd密码'
    LOGIN_HDD_PSW_FAIL = '密码错误'
    DEL_HDD_PSW_ERROR = '密码无效'
    HDD_NEW_OLD_PSW_DIFF = '密码不符，两次输入的密码必须相同'
    HDD_LOCK_PROMPT = '请重启并输入正确的密码才可以解开锁住的硬盘'
    HDD_LOCK_STATUS = '无法更改驱动器的安全状态'
    HDD_ESC_LOCK_PROMPT = '密码输入已取消，驱动器仍处于锁定状态'

    # IPMITOOL 启动
    IPMITOOL_HDD_BOOT_NAME='内置硬盘驱动器'
    IPMITOOL_PXE_BOOT_NAME='内置网络设备'
    IPMITOOL_ODD_BOOT_NAME = 'USB CD/DVD光驱'
    IPMITOOL_USB_BOOT_NAME = 'USB闪存驱动器/USB硬盘'
    IPMITOOL_OTHER_BOOT_NAME = '其它'