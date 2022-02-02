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
    PROJECT_NAME = "InspurStorage"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "InspurStorage\\Report\\template"
    TESTCASE_CSV = "InspurStorage\\AllTest.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\InspurStorage\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com5"

    # BMC Configuration
    BMC_IP = '192.168.6.233'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.59'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@123'

    # Tool definition - Ver 1.8.18
    SMBIOS = "InspurStorage\\Tools\\smbios4u\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sda4"
    LINUX_USB_MOUNT = "/mnt/"
    SHELL_USB_PATH = "fs1:"
    USB_VOLUME = "USB:SanDisk \(P4\)"

    #BIOS flash command
    LINUX_FLASH_CMD = "./flash bfu"
    LINUX_SMBIOS_CMD="./flash dmi"
    LINUX_FLASH_DRIVER_PATH = "/root/"
    LINUX_BIOS_MOUNT_PATH = "/mnt/Storage/"
    SHELL_FLASH_CMD = " ByoShellFlash.efi bfu"
    DOS_FLASH_CMD = "byoflash bfu"
    UNSIGN_BIOS_FILE="bios.fd"
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE= "previous.bin"
    CONSTANT_BIOS_FILE="constant.bin"

    #OS Login
    ROOT_LOGIN='localhost login|bogon login'
    LOGIN_SUCCESS='root@localhost|root@bogon'



class Msg:
    POST_MESSAGE = 'Press Del to enter SETUP|Press F3 to enter Boot Menu|ress F12 to enter PXE boot'
    HOTKEY_PROMPT_DEL = POST_MESSAGE
    HOTKEY_PROMPT_F11 = 'Press F3 to enter Boot Menu'
    HOTKEY_PROMPT_F11_CN = POST_MESSAGE
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot,'
    HOTKEY_PROMPT_F12_CN = POST_MESSAGE

    # pages in bios configuration
    PAGE_MAIN = "CPU Info"
    PAGE_DEVICE = "PCIe Configuration"
    PAGE_ADVANCED = 'Hyper Thread'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Load Setup Defaults'
    PAGE_ALL = [PAGE_DEVICE,PAGE_MAIN,PAGE_ADVANCED,PAGE_SECURITY,PAGE_BOOT,PAGE_EXIT]

    QUIET_BOOT = 'Quiet Boot'
    NUMLOCK_STATE = 'Bootup NumLock State'
    INTERNAL_SHELL = 'Internal SHELL'
    PXE_IP_VER='Net Boot IP Version'
    SAVE_AND_EXIT='Save and Exit'


    # menus of boot page
    ENTER_BOOTMENU = "Startup Device Menu|ENTER to select boot device"
    SHELL='Internal EDK Shell'
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: SanDisk'
    PXE_PORT1 = "UEFI OnBoard 3: Port 1 - Intel\(R\) I350 Gigabit Backplane Connection PXE IPv4"
    PXE_PORT2 = "UEFI OnBoard 3: Port 1 - Intel\(R\) I350 Gigabit Backplane Connection PXE IPv6"
    LINUX_OS = 'UEFI NVME: WDC CL SN720 SDAQNTW-256G-2000'
    LINUX_OS_MSG = 'Kylin Linux Advanced Server'


    HDD_BOOT_NAME = 'Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    OTHER_BOOT_NAME = 'Others'


class Che:
    #生产商信息检查
    LOC_SYS_SUM=['CPU Info','System Summary']
    PRODUCT_MSG=['Inspur', 'Byosoft', 'Xuanwu4U']

    #BIOS信息检查
    BIOS_MSG=['Byosoft ByoCore BIOS V1.0', '3.00.34', '01/10/2022 13:13']

    #内存信息检查
    LOC_MEM_INFO=['Memory Info']
    SILK=['A0','B0','C0','C1','D0','D1','E0','F0','G0','G1','H0','H1']

    #CPu信息检查
    LOC_CPU_INFO=['CPU Info']
    CPU_MSG=['Hygon C86 7265 24-core Processor', 'CPU 0', 'CPU 1', '0x900F11', '2200 MHz', '24 Cores', '24 Thread', '0x80901047', '2304KB', '12MB', '64MB']

    #板载网卡，NVME信息检查
    MAC_ADDRESS=['00-A0-C9-00-00-00', '00-A0-C9-00-00-01', 'B4-05-5D-C5-49-A5', 'B4-05-5D-C5-49-A4']
    NVME_MSG=['WDC CL SN720 SDAQNTW-256G-2000 SN:21031L800168 Size:256.0GB']
    LOC_LAN=['PCIe Configuration','Lan Configuration']
    LOC_NVME=['PCIe Configuration','NVME Device']
    SET_INFO=['Hyper Thread',{'Debug Mode':'Information'}]

    # 日志打印级别
    DEBUG_VALUES=['Debug','Information','Warning','Critical','Disable']
    DEBUG_NAME='Debug Mode'

    #smbus频率
    SMBUS=['FED80ED0: 00 00 00 00 00 00 00 00-1C 00 00 00 1C 00 00 00','FED80EE0: 1C 00 00 00 1C 00 00 00-1C 00 00 00 1C 00 00 00','FED80EF0: 00 00 00 00 00 00 00 00-00 00 00 00 FF FF FF FF']

    #NTB资源预留
    NTB=[{2:4},{5:8},{6:4}]

    #BDS
    SET_DEBUG=['Hyper Thread',{'Debug Mode':'Debug'}]
    SET_WARNING=['Hyper Thread',{'Debug Mode':'Warning'}]

    #Level Clear
    DEBUG_OPTION_VALUE = ['Debug', 'Warning', 'Critical', 'Disable','Information']
    WRONG_MSG='DirectBootCallback|QuestionId :0x\d+'



class Boot:
    LOC_BOOT_USB=['Load Setup Defaults',Msg.USB_UEFI]
    LOC_BOOT_OS=['Load Setup Defaults',Msg.LINUX_OS]
    LOC_BOOT_PXE=['Load Setup Defaults',Msg.PXE_PORT1]
    LOC_BOOT_PXE_IPv6 = ['Load Setup Defaults', Msg.PXE_PORT2]
    SET_PXE_ALL=['User Wait Time', {'Network Boot': 'Enabled'},{'Net Boot IP Version':'All'}]
    PXE = ['User Wait Time', {'Network Boot': 'Enabled'},{'Net Boot IP Version':'IPv4'}]
    IPV4_MSG='Start PXE over IPv4'
    IPV6_MSG='Start PXE over IPv6'
    # Boot order
    ORDER = [Msg.USB_UEFI, Msg.LINUX_OS, Msg.PXE_PORT1, Msg.PXE_PORT2]  # 启动顺序
    #Change Boot order
    CHANGE_ORDER=[Msg.PXE_PORT1,Msg.PXE_PORT2,Msg.LINUX_OS,Msg.USB_UEFI]#改变后启动顺序

class Cpu:
    #CPU信息
    CPU_INFO=['CPU Info']

    #CPU超线程
    CLOSE_HYPER_THREADING=['Hyper Thread',{'Hyper Thread':'Disabled'}]
    OPEN_HYPER_THREADING = ['Hyper Thread',{'Hyper Thread':'Enabled'}]

    #CPU C-State
    CPU_FREQUENCY_CSTATE=['3.00','2.50']#海光工具检测，C-State打开、关闭状态下的CPU频率
    OPEN_CSTATE=['Hyper Thread',{'CPU C-State Control':'Enabled'}]
    CLOSE_CSTATE = ['Hyper Thread',{'CPU C-State Control':'Disabled'}]

    #CPU P-State
    CPU_FREQUENCY_PSTATE=['2.20','1.60','1.20']#海光工具检测，P0、P1、P2CPU频率
    OPEN_PSTATE=['Hyper Thread',{'CPU P-State Control':'Enabled'}]
    CLOSE_PSTATE=['Hyper Thread',{'CPU P-State Control':'Disabled'}]

    #CPU NUMA
    OPEN_NUMA=['Hyper Thread',{'Hyper Thread':'Enabled'},{'NUMA Nodes':'Enabled'}]
    CLOSE_NUMA=['Hyper Thread',{'Hyper Thread':'Enabled'},{'NUMA Nodes':'Disabled'}]

    #CPU CPB
    CPU_FREQUENCY_CPB='2.20'#海光工具检测,超频关闭，打开下CPU频率
    CLOSE_CPB=['Hyper Thread',{'CPU P-State Control':'Disabled'},{'CPU C-State Control':'Disabled'},{'Core Performance Boost':'Disabled'}]
    OPEN_CPB=['Hyper Thread',{'Core Performance Boost':'Auto|Enabled'}]



class Psw:
    # Password related messages
    SET_SETUP_PSW_SUCCESS_ADM = 'Administrator Password *Installed'
    SET_SETUP_PSW_SUCCESS_USE = 'User Password *Installed'
    DEL_SETUP_PSW_SUCCESS_ADM = 'Administrator Password *Uninstalled'
    DEL_SETUP_PSW_SUCCESS_USE = 'User Password *Uninstalled'
    SET_ADMIN_PSW = 'Set Administrator Password'
    SET_USER_PSW = 'Set User Password'
    OPEN_USE_CHANGE=[{'User Password Changeable by User':'Enabled'}]
    CLOSE_USE_CHANGE = [{'User Password Changeable by User': 'Disabled'}]
    CLEAR_USE_PSW='Clear User Password'
    LOGIN_TYPE_ADM='User Login Type *Administrator'
    LOGIN_TYPE_USE = 'User Login Type *User'
    NEW_OLD_PSW_DIFF = 'Passwords are not the same'
    PSW_LEN_DIFF = 'Character length is not equal'
    LOGIN_SETUP_PSW_PROMPT = 'System Security'
    PSW_LOCK='The password was mistyped three times. Press the Enter will restart.'
    CHARACTERS_LENGTH_NOT_ENOUGH = 'Please enter enough characters'
    CHARACTERS_TYPE_NOT_ENOUGH = 'Warning|Passwords need to contain upper and lower case letters'
    LOGIN_SETUP_PSW_FAIL = 'Invalid Password'
    PSW_ERROR_LOCK = 'The password is incorrect and the screen is locked'
    PSW_CHECK_ERROR = 'Incorrect password'
    USER_NOT_DEL_PSW = 'User Rights Cannot Delete Password'
    PSW_EXPIRE = 'Password expired'
    PSW_SET_STATUS = 'Installed'
    PWS_NOT_SET_STATUS = 'Not Installed'
    USER_ADMIN_PSW_SAME = 'Password Rule Error'
    POWER_ON_PSW_OPTION = 'Power-on Password'
    PSW_EXPIRY_DATE = 'Password Valid Days'
    LOC_USER_PSW=[SET_ADMIN_PSW,SET_USER_PSW]
    LOC_ADMIN_PSW = [SET_ADMIN_PSW]



class Pci:
    NAME='4U'
    # PCIE链路协商重试
    SET_INFO = ['Hyper Thread', {'Debug Mode': 'Information'}]

    # PCIE资源预留
    OPEN_SLOT = ['PCIe Configuration', 'PCIe Configuration', {'Slot3': 'Enabled'}, {'Slot4': 'Enabled'},
                 {'Slot5': 'Enabled'}, {'Slot6': 'Enabled'}]
    BDFS = ['0d:00.0', '0d:01.0', 'ae:01.2', 'ae:01.1', 'd5:01.2', 'd5:01.1', '0d:02.0', '0d:03.0', '64:00.0',
            '64:01.0', '64:02.0', '64:03.0']
    SLOT = '8'  # x16规格插在的Slot口，如果插在Slot1，Slot2两个口，SLOT='2';如果插在Slot3，Slot4两个口，SLOT='4'...

    # SMI
    BDFS_SMI = ['0d:00.0', '0d:01.0', 'ae:01.2', 'ae:01.1', 'd5:01.2', 'd5:01.1', '0d:02.0', '0d:03.0', '64:00.0',
            '64:01.0', '64:02.0', '64:03.0']
    ALL_SLOTS = ['3', '4', '5', '6']

    # PCIE的Memory使能
    LOC_PCIE_DEVICE = ['PCIe Configuration', 'PCI Device Info']

    #IO
    IO_SLOT=['1','3']#外接网卡82599ES插在的Slot口



class Sup:
    # BIOS默认参数
    DEFAULT_OPTIONS=['<Disabled>HyperThread', '<Disabled>CPUP-StateControl', '<Disabled>CPUC-StateControl', '<Disabled>SpreadSpectrum', '<Auto>CorePerformanceBoost', '<Enabled>NUMANodes', '<Enabled>IOMMU', '<Information>DebugMode', '<Disable>TPMSelect', '[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<Disabled>InternalSHELL', '<Enabled>NetworkBoot', '<IPv4>NetBootIPVersion', '<English>SelectLanguage', '<Disabled>Slot3', '<Disabled>Slot4', '<Disabled>Slot5', '<Disabled>Slot6', '<Enabled>USBMassStorageSupport', '<Enabled>CPU1USBPortEnable', '<Enabled>ConsoleRedirection', '<115200>SerialPortBaudrate', '<VT-UTF8>TerminalType', '<Enabled>PlatformFirstErrorHandling', '<1>MCAErrorThresholdCount']

    #串口重定向支持
    SET_VT100 = ['Hyper Thread', 'Console Redirection', {'Terminal Type': 'VT100'}]
    SET_UTF8=['Hyper Thread','Console Redirection',{'Terminal Type':'VT-UTF8'}]
    F1_MSG='General Help'
    ESC_MSG='Are you sure Exit'
    F9_MSG='Are you sure load defaults'
    F10_MSG='Save configuration changes and exit'

    #USB 存储设备支持
    CLOSE_USB_STORAGE=['PCIe Configuration','USB Configuration',{'USB Mass Storage Support':'Disabled'},{'CPU1 USB Port Enable':'Enabled'}]
    OPEN_USB_STORAGE=['PCIe Configuration','USB Configuration',{'USB Mass Storage Support':'Enabled'}]

    #USB端口配置
    LOC_USB_INFO=['PCIe Configuration','USB Configuration']
    CLOSE_USB_PORT=['PCIe Configuration','USB Configuration',{'USB Mass Storage Support':'Enabled'},{'CPU1 USB Port Enable':'Disabled'}]
    OPEN_USB_PORT = ['PCIe Configuration', 'USB Configuration',{'CPU1 USB Port Enable': 'Enabled'}]

    #Secure Boot
    SECURE_MSG='Invalid Signature detected. Check Secure Boot Policy in Setup.'
    LOC_SECURE_BOOT=['Set Administrator Password','Secure Boot','Restore Factory Keys']
    OPEN_SECURE_BOOT=[{'Secure Boot':'Enabled'},'User Wait Time',{'Internal SHELL':'Enabled'}]
    CLOSE_SECURE_BOOT=['Set Administrator Password','Secure Boot','Reset to Setup Mode']

    #Network Boot
    OPEN_NET_BOOT=['User Wait Time',{'Network Boot':'Enabled'}]
    CLOSE_NET_BOOT = ['User Wait Time',{'Network Boot':'Disabled'}]

    #SPI BIOS 锁住
    OPEN_SPI=['User Wait Time',{'Internal SHELL':'Enabled'},'Console Redirection','Misc Configuration',{'SPI BIOS Lock':'Enabled'}]
    CLOSE_SPI=['User Wait Time',{'Internal SHELL':'Enabled'},'Console Redirection','Misc Configuration',{'SPI BIOS Lock':'Disabled'}]

    #安静启动
    OPEN_QUIET_BOOT=['User Wait Time',{'Quiet Boot':'Enabled'}]
    CLOSE_QUIET_BOOT = ['User Wait Time', {'Quiet Boot': 'Disabled'}]

    # 虚拟化
    IOMMU_ENABLED_INFO = 'AMD-Vi: IOMMU performance counters supported'

    #IOMMU
    CLOSE_IOMMU=['Hyper Thread',{'IOMMU':'Disabled'}]
    OPEN_IOMMU=['Hyper Thread',{'IOMMU':'Enabled'}]

    #Load Setup Defaults
    CHANGED_VALUES=['<Enabled>HyperThread', '<Enabled>CPUP-StateControl', '<Enabled>CPUC-StateControl', '<Enabled>SpreadSpectrum', '<Disabled>CorePerformanceBoost', '<Disabled>NUMANodes', '<Disabled>IOMMU', '<Debug>DebugMode', '<Disable>TPMSelect', '[5]UserWaitTime', '<Disabled>QuietBoot', '<Off>BootupNumLockState', '<Enabled>InternalSHELL', '<Enabled>NetworkBoot', '<IPv6>NetBootIPVersion', '<English>SelectLanguage', '<Enabled>Slot3', '<Enabled>Slot4', '<Enabled>Slot5', '<Enabled>Slot6', '<Enabled>USBMassStorageSupport', '<Enabled>CPU1USBPortEnable', '<Enabled>ConsoleRedirection', '<115200>SerialPortBaudrate', '<VT-UTF8>TerminalType', '<Disabled>PlatformFirstErrorHandling', '<Disabled>PlatformPCIEAERReport']

    #reboot
    REBOOT_SYSYTEM=['Load Setup Defaults','Reboot System']

    #未签名BIOS
    UPDATE_UNSIGN_MSG='Verifying BIOS signature....Failed!'

    #TPM
    SET_FTPM = ['Set Administrator Password', {'TPM Select': 'FTPM'}]
    DTPM_OS_MSG='NTZ0751:00: 2.0 TPM'
    FTPM_OS_MSG = 'Hygon'
    CHANGE_TPM2=['Set Administrator Password','TCG2 Configuration',{'TPM2 Operation':'TPM2 ClearControl(NO) + Clear'}]
    POST_MSG='Press F12 to clear the TPM'
    LOC_TCG2=['Set Administrator Password','TCG2 Configuration']
    CLOSE_TPM=['Set Administrator Password', {'TPM Select': 'Disabled|Disable'}]

    #AER 控制
    CLOSE_ERR_MAN=['Hyper Thread','Error Management',{'Platform First Error Handling':'Disabled'}]
    LOC_ERR=['Hyper Thread','Error Management']

class Upd:
    SMBIOS_MSG='Update Smbios.............Successed!'
    PASSWORDS=['Adminbios@3','Usersbios@3']

    #获取BIOS选项值
    LOC_DEVICE=['PCIe Configuration']
    LOC_PART1=['PCIe Configuration','USB Configuration']#PCIe Configuration菜单下所有需要进入获取值的选项
    LOC_ADVANCED=['Hyper Thread']
    LOC_PART2 =['Console Redirection','Error Management']#Hyper Thread菜单下所有需要进入获取值的选项

    #修改BIOS选项
    CHANGE_PART=['PCIe Configuration','PCIe Configuration',{'Slot3':'Enabled'},{'Slot4':'Enabled'},{'Slot5':'Enabled'},{'Slot6':'Enabled'},Msg.PAGE_ADVANCED,{'Hyper Thread':'Enabled'},{'CPU P\-State Control':'Enabled'},{'CPU C-State Control':'Enabled'},{'SpreadSpectrum':'Enabled'},{'Core Performance Boost':'Disabled'},{'NUMA Nodes':'Disabled'},{'IOMMU':'Disabled'},{'Debug Mode':'Debug'},'Error Management',{'Platform First Error Handling':'Disabled'},'User Wait Time',{'Bootup NumLock State':'Off'},{'Internal SHELL':'Enabled'},{'Net Boot IP Version':'IPv6'}]
    LOC_USB=['Load Setup Defaults',Msg.USB_UEFI]
    LOC_OS=['Load Setup Defaults',Msg.LINUX_OS]
    SETUP_LATEST=['BIOS Update', Env.USB_VOLUME, '<Storage>', Env.LATEST_BIOS_FILE]
    SETUP_PREVIOUS = ['BIOS Update', Env.USB_VOLUME, '<Storage>', Env.PREVIOUS_BIOS_FILE]
    SETUP_CONSTANT = ['BIOS Update', Env.USB_VOLUME, '<Storage>', Env.CONSTANT_BIOS_FILE]
    SETUP_MSG='Flash is updated successfully!'
    SHELL_FLASH_TOOL=Env.SHELL_FLASH_CMD
    SHELL_MSG_NOR="End.....................Successed!"
    SHELL_MSG_ALL="Update ALL..................Successed!"
    LINUX_MSG_NOR = "End.....................Successed!"
    LINUX_MSG_ALL = "Update ALL..................Successed!"
    PRODUCT_NAME='Product Name: Xuanwu4U'


