#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
from Inspur7500.Config.PlatConfig import Puti


class Env:
    # 测试报告设置
    PROJECT_NAME = "Inspur7500"
    SUT_CONFIG = "SUT1-Half-DIMM"

    # 测试文件
    TESTCASE_CSV = "Inspur7500\\AllTest1.csv"

    # Environment settings
    LOG = 'e:\\daily\\Puti'

    # 串口号
    BIOS_SERIAL = "com3"

    # BMC 配置
    BMC_IP = '192.168.6.76'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.119'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    OS_IP_LEGACY = '192.168.6.119'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    SMBIOS = "Inspur7500\\Tools\\smbiosputi\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sda4"  # LinuxU盘盘符
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs1:"
    USB_VOLUME = "USB:SanDisk \(P4\)"  # SetUp刷新BIOSU盘名

    # BIOS flash command
    BIOS_FILE = 'BIOS'  # U盘存放BIOS文件和刷新工具的文件夹名
    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)

    # OEM命令
    SET_BIOS_SERIAL = 'raw 0x3e 0xc4 0x01'  # 切换BIOS串口
    GET_OPTION = 'raw 0x3e 0xc2'  # OEM命令获取
    CHANGE_OPTION = 'raw 0x3e 0xc3 0x01'  # OEM修改


class Msg(Puti):
    # Menus of boot page
    USB_UEFI = 'UEFI USB: SanDisk'
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    LEGACY_HDD_BOOT_NAME = "UEFI NVME\(PCI2-0-0\): Samsung SSD 980 250GB|NVME\(PCI2-0-0\): Samsung SSD 980 250GB"  # Legacy系统盘在Legacy,UEFI模式下启动名
    UEFI_HDD_BOOT_NAME = 'kos\(SATA3-1: Samsung SSD 870 EVO 250GB\)|SATA3-1: Samsung SSD 870 EVO 250GB'  # UEFI系统盘在Legacy,UEFI模式下启动名
    LINUX_OS = 'kos\(SATA3-1: Samsung SSD 870 EVO 250GB\)'  # UEFI系统盘在UEFI模式启动名，Legacy系统盘在Legacy模式下启动名


class Boot:
    # Boot order
    BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.ODD_BOOT_NAME, Msg.PXE_BOOT_NAME,
                           Msg.USB_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.ODD_BOOT_NAME, Msg.PXE_BOOT_NAME,
                             Msg.USB_BOOT_NAME]


class Cpu:
    # CPU频率
    CPU_FREQUENCY = ['1200', '1600', '2000']  # SetUp下可以设定的CPU频率

    # CPU P-State
    CPU_FREQUENCY_PSTATE = ['2.50', '1.60', '1.20']  # 海光工具检测，P0、P1、P2CPU频率

    # CPU 降核
    CPU_DOWNCORE_CORE = ['8', '8', '12', '16', '16', '24']  # CPU降核
    DOWNCORE_VALUES = ['TWO (1 + 1)', 'TWO (2 + 0)', 'THREE (3 + 0)', 'FOUR (2 + 2)', 'FOUR (4 + 0)', 'SIX (3 + 3)']

    # CPU NUMA
    NUMA_VALUES = ['Socket', 'None', 'Channel', 'Die', 'Auto']
    CPU_NUMA_ONE = ['1', '4', '4', '1', '4']  # NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO = ['1', '8', '8', '2', '8']  # NUMA双路CPU分别对应插槽、没有、通道、裸片、自动

    # CPU CPB
    CPU_FREQUENCY_CPB = ['2.00', '3.00']  # 海光工具检测,超频关闭，打开下CPU频率

    # CPU Performance
    VALUE_CPU_SPEED = ['1.20', '1.60', '2.00', '2.50']  # 每个值对应的CPU频率


class Psw:
    TRY_COUNTS = 3  # 输错密码重试次数,3代表输错3次后，第4次输错会被锁定

    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = 'SATA3-1: Samsung SSD 870 EVO 250GB'
    HDD_PASSWORD_NAME_02 = 'NVME\(PCI2-0-0): Samsung SSD 980 250GB'
    HDD_NAME_01_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_NAME_02_OS = Msg.LEGACY_HDD_BOOT_NAME


class Pxe:
    # PXE 重试
    PXE_RETRY_MSG = 'timeout'

    # LegacyPXE 重试
    PXE_RETRY_MSG_LEGACY = 'WangXun\(R\) *PXE *\(PCI01:00.0\)'

    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun(R) (B4-05-5D-8E-91-B2)"
    PXE_NET_ADDON = "Intel X550 Eth (B4-05-5D-16-7C-2E)"

    # PXE启动项(IPv4)
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun\(R\) PXE IPv4"
    PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d - Intel X550 Eth PXE IPv4'


class Sup:
    # 网络唤醒
    MAC_ADDRESS = 'B4-05-5D-8E-91-B2|B4-05-5D-8E-91-B3'

    # HDD Bind
    HDD_BIND_NAME_1 = 'B4D0F0 WDC WD5000LPCX-22VHAT0 WD-WXL1A8668TU6'
    HDD_BIND_NAME_2 = 'B5D0F0 INTEL SSDSCKKB960G8 PHYH90840080960L'
    HDD_BIND_NAME_1_OS = Msg.LEGACY_HDD_BOOT_NAME
    HDD_BIND_NAME_2_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_BIND_PROMPT = 'No binded Hdd boot will be ignored'  ################################################

    # 内存频率
    MEMORY_SPEED = ['667', '800', '1067', '1200', '1333']  # SetUp下可以设置的内存频率

    # Boot Logo
    HIDE_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Enabled'}]
    SHOW_BOOT_LOGO = ['Console Redirection', 'Misc Configuration', {'Hide Boot Logo': 'Disabled'}]
    LOGO_PATH = './Inspur7500/Tools/Pictures/Logo'
    MANUFACTOURER = 'Inspur'

    # 联动关系
    OPEN_SECURE = [{'Secure Boot': 'Enabled'}]
    CLOSE_SECURE_MSG = '<Disabled> *Secure Boot'

    # Option Rom
    ASMEDIA_MSG = 'AsmediaTechnologies|Asmedia Technologies'


class Upd:
    PASSWORDS = ['Admin@1111', 'Users@1111']

    # BMC 相关选项
    BMC_LINK_OPTION = ['<Disabled>SOLforBaseboardMgmt', '<Enabled>SOLforBaseboardMgmt', '<StayOff>RestoreACPowerLoss',
                       '<LastState>RestoreACPowerLoss', '<PowerOn>RestoreACPowerLoss']

    # 默认值
    DEFAULT_OPTION_VALUE = ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '[100]PasswordLockTime',
                            '<30Days>PasswordValidDays', '<Disabled>Power-onPassword', '<Enabled>CustomPasswordCheck',
                            '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
                            '<Disabled>TPMSelect', '[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState',
                            '<UEFI>BootMode', '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom',
                            '<NULL>SelectaNetworktoPXE', '<Enabled>PXEBootOptionsRetry',
                            '<IPv4andIPv6>NetBootIPVersion', '<Disabled>PXEBootPriority',
                            '<FullUpdate>BIOSUpdateParameters', '<English>SelectLanguage',
                            '<DefaultConfiguration>NativePCIeConfiguration', '<Disabled>SLIM1_CPU0asSATA',
                            '<Disabled>SLIM3_CPU1asSATA', '<Disabled>SLIM5_CPU1asSATA',
                            '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan', '<PCIE>PrimaryGraphicsAdapter',
                            '<Enabled>USBMassStorageSupport', '<Enabled>IOMMU', '<Enabled>SVM',
                            '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit',
                            '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIeMaxPayloadSize',
                            '<Disabled>PCIeASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
                            '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode',
                            '<Disabled>PCIeResizableBAR', '<Disabled>FCHSSC', '<Disabled>FRB2WatchdogTimer',
                            '<Disabled>OSBootWatchdogTimer', '<Disabled>SOLforBaseboardMgmt',
                            '<LastState>RestoreACPowerLoss', '<Enabled>PlatformFirstErrorHandling',
                            '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount',
                            '<Enabled>ClearmemoryCEthresholdinevery', '[10000]PCIeCEThreshold', '[4095]CPUCEThreshold',
                            '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
                            '<Enabled>ChipselectInterleaving', '<Auto>ChannelInterleaving', '<Auto>NUMA',
                            '<Auto>MemoryInterleavingsize', '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider',
                            '<Disabled>RDSEEDandRDRANDControl', '<Auto>DRAMscrubtime', '<Auto>EfficiencyOptimizedMode',
                            '<Auto>BankInterleaving', '<NoBinded>HDDBind', '<Enabled>RearUSBportConfiguration',
                            '<Enabled>FrontUSBportConfiguration', '<Auto>L1StreamHWPrefetcher',
                            '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable',
                            '<Enabled>ConsoleRedirection', '<115200>SerialPortBaudrate', '<VT-UTF8>TerminalType',
                            '<8>SerialDataBits', '<None>SerialParity', '<1>SerialStopBits',
                            '<Enabled>AsmediaController1061R_A', '<Enabled>AsmediaController1061R_B',
                            '<Disabled>HygonTPCM', '<Enabled>NCSI', '<Static>IPv4Source', '<Enabled>IPv6',
                            '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<Dynamic>IPv4Source',
                            '<Administrator>Privilege', '<Disabled>UserStatus', '<Disabled>SecureBoot']

    DOS_FLASH_CMD_LATEST_ALL = 'byoflash bfu -all latest.bin'
    DOS_FLASH_CMD_PREVIOUS_ALL = 'byoflash bfu -all previous.bin'
    DOS_FLASH_CMD_CONSTANT_ALL = 'byoflash bfu -all constant.bin'
    DOS_FLASH_CMD_LATEST = 'byoflash bfu latest.bin'
    DOS_FLASH_CMD_PREVIOUS = 'byoflash bfu previous.bin'
    DOS_FLASH_CMD_CONSTANT = 'byoflash bfu constant.bin'

    SHELL_FLASH_CMD_LATEST_ALL = 'ByoShellFlash.efi bfu -all latest.bin'
    SHELL_FLASH_CMD_PREVIOUS_ALL = 'ByoShellFlash.efi bfu -all previous.bin'
    SHELL_FLASH_CMD_CONSTANT_ALL = 'ByoShellFlash.efi bfu -all constant.bin'
    SHELL_FLASH_CMD_LATEST = 'ByoShellFlash.efi bfu latest.bin'
    SHELL_FLASH_CMD_PREVIOUS = 'ByoShellFlash.efi bfu previous.bin'
    SHELL_FLASH_CMD_CONSTANT = 'ByoShellFlash.efi bfu constant.bin'

    LINUX_FLASH_CMD_LATEST_ALL = f'./flash bfu -all {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./flash bfu -all {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_FLASH_CMD_CONSTANT_ALL = f'./flash bfu -all {Env.LINUX_BIOS_MOUNT_PATH}constant.bin'
    LINUX_FLASH_CMD_LATEST = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_FLASH_CMD_CONSTANT = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}constant.bin'

    SHELL_FLASH_CMD_OTHERS = 'ByoShellFlash.efi bfu others.bin'
    SHELL_FLASH_CMD_UNSIGNED = 'ByoShellFlash.efi bfu unsigned.bin'
    LINUX_FLASH_CMD_OTHERS = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./flash bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'


class Ras:
    SET_LEAKY_BUCKET_1 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 39}, {'Leaky Bucket Count': 4}]
    SET_LEAKY_BUCKET_2 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 132}, {'Leaky Bucket Count': 15}]
    SET_LEAKY_BUCKET_3 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 26}, {'Leaky Bucket Count': 3}]
    SET_PCIE_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                              {'PCIe CE Threshold': 10000}]
    RAS_DICT = {
        #   'eventdata' : ['die umc dimm',内存位置]
        '0c': ['0 0 0',6],  # CPU0_D0
        '0d': ['0 0 1',7],  # CPU0_D1
        '08': ['0 1 0',4],  # CPU0_C0
        '09': ['0 1 1',5],  # CPU0_C1
        '00': ['1 0 0',0],  # CPU0_A0
        '01': ['1 0 1',1],  # CPU0_A1
        '04': ['1 1 0',2],  # CPU0_B0
        '05': ['1 1 1',3],  # CPU0_B1
        '1c': ['2 0 0',14],  # CPU0_H0
        '1d': ['2 0 1',15],  # CPU0_H1
        '18': ['2 1 0',12],  # CPU0_G0
        '19': ['2 1 1',13],  # CPU0_G1
        '10': ['3 0 0',8],  # CPU0_E0
        '11': ['3 0 1',9],  # CPU0_E1
        '14': ['3 1 0',10],  # CPU0_F0
        '15': ['3 1 1',11],  # CPU0_F1
        '2c': ['4 0 0',22],  # CPU1_D0
        '2d': ['4 0 1',23],  # CPU1_D1
        '28': ['4 1 0',20],  # CPU1_C0
        '29': ['4 1 1',21],  # CPU1_C1
        '20': ['5 0 0',16],  # CPU1_A0
        '21': ['5 0 1',17],  # CPU1_A1
        '24': ['5 1 0',18],  # CPU1_B0
        '25': ['5 1 1',19],  # CPU1_B1
        '3c': ['6 0 0',30],  # CPU1_H0
        '3d': ['6 0 1',31],  # CPU1_H1
        '38': ['6 1 0',28],  # CPU1_G0
        '39': ['6 1 1',29],  # CPU1_G1
        '30': ['7 0 0',24],  # CPU1_E0
        '31': ['7 0 1',25],  # CPU1_E1
        '34': ['7 1 0',26],  # CPU1_F0
        '35': ['7 1 1',27],  # CPU1_F1
    }
