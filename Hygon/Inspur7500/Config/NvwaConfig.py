#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
from Inspur7500.Config.PlatConfig import Nvwa


class Env:
    # 测试报告设置
    PROJECT_NAME = "Inspur7500"
    SUT_CONFIG = "SUT1-Half-DIMM"

    # 测试文件
    TESTCASE_CSV = "Inspur7500\\AllTest1.csv"

    # Environment settings
    LOG = 'c:\\daily\\Nvwa'

    # 串口号
    BIOS_SERIAL = "com5"

    # BMC 配置
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

    SMBIOS = "Inspur7500\\Tools\\smbiosnvwa\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sda4"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs5:"
    USB_VOLUME = "USB:SanDisk \(P4\)"

    # BIOS flash command
    BIOS_FILE = 'BIOS'
    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)

    # OEM命令
    SET_BIOS_SERIAL = 'raw 0x3e 0xc4 0x01'  # 切换BIOS串口
    GET_OPTION = 'raw 0x3e 0xc2'  # OEM命令获取
    CHANGE_OPTION = 'raw 0x3e 0xc3 0x01'  # OEM修改


class Msg(Nvwa):
    # Menus of boot page
    USB_UEFI = 'UEFI USB: SanDisk'
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    LEGACY_HDD_BOOT_NAME = "SATA3\-1: Samsung SSD 870 EVO 250GB|UEFI SATA3\-1: Samsung SSD 870 EVO 250GB"  # Legacy系统盘在Legacy,UEFI模式下启动名
    UEFI_HDD_BOOT_NAME = 'CentOS Linux\(SATA3\-0: SanDisk SDSSDH3 500G\)|SATA3\-0: SanDisk SDSSDH3 500G'  # UEFI系统盘在Legacy,UEFI模式下启动名
    LINUX_OS = 'CentOS Linux\(SATA3\-0: SanDisk SDSSDH3 500G\)|SATA3\-1: Samsung SSD 870 EVO 250GB'  # UEFI系统盘在UEFI模式启动名，Legacy系统盘在Legacy模式下启动名


class Boot:
    # Boot order
    BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.USB_BOOT_NAME, Msg.PXE_BOOT_NAME,
                           Msg.ODD_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.USB_BOOT_NAME, Msg.PXE_BOOT_NAME,
                             Msg.ODD_BOOT_NAME]


class Cpu:
    # CPU频率
    CPU_FREQUENCY = ['1600', '2000', '2500']  # SetUp下可以设定的CPU频率

    # CPU P-State
    CPU_FREQUENCY_PSTATE = ['2.50', '2.00', '1.60']  # 海光工具检测，P0、P1、P2CPU频率

    # CPU 降核
    CPU_DOWNCORE_CORE = ['4', '4', '6', '8', '8', '12']  # CPU降核
    DOWNCORE_VALUES = ['TWO (1 + 1)', 'TWO (2 + 0)', 'THREE (3 + 0)', 'FOUR (2 + 2)', 'FOUR (4 + 0)', 'SIX (3 + 3)']

    # CPU NUMA
    NUMA_VALUES = ['None', 'Channel', 'Die', 'Auto']
    CPU_NUMA_ONE = ['2', '2', '1', '2']  # NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO = ['4', '4', '2', '4']  # NUMA双路CPU分别对应插槽、没有、通道、裸片、自动

    # CPU CPB
    CPU_FREQUENCY_CPB = ['2.50', '3.00']  # 海光工具检测,超频关闭，打开下CPU频率

    # CPU Performance
    VALUE_CPU_SPEED = ['1.60', '2.00', '2.50', '3.00']  # 每个值对应的CPU频率


class Psw:
    TRY_COUNTS = 2  # 输错密码重试次数,2代表输错2次后，第3次输错会被锁定

    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = "SATA3\-0: SanDisk SDSSDH3 500G"
    HDD_PASSWORD_NAME_02 = "SATA3\-1: Samsung SSD 870 EVO 250GB"
    HDD_NAME_01_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_NAME_02_OS = Msg.LEGACY_HDD_BOOT_NAME


class Pxe:
    # PXE 重试
    PXE_RETRY_MSG = 'timeout'

    # LegacyPXE 重试
    PXE_RETRY_MSG_LEGACY = 'WangXun\(R\) *PXE *\(PCI01:00.0\)'

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


class Sup:
    # 网络唤醒
    MAC_ADDRESS = 'B4-05-5D-4F-6B-D3|B4-05-5D-4F-6B-D4'

    # 硬盘绑定使用
    HDD_BIND_NAME_1 = 'B4D0F0 SanDisk SDSSDH3 500G 2149LC475012'
    HDD_BIND_NAME_2 = 'B4D0F0 Samsung SSD 870 EVO 250GB S6PFNX0T330000P'
    HDD_BIND_NAME_1_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_BIND_NAME_2_OS = Msg.LEGACY_HDD_BOOT_NAME
    HDD_BIND_PROMPT = 'No binded Hdd boot will be ignored'  ################################################

    # 内存频率
    MEMORY_SPEED = ['667', '800', '1067', '1200', '1333']  # SetUp下可以设置的内存频率

    # 联动关系
    OPEN_SECURE = [{'Secure Boot': 'Enabled'}]
    CLOSE_SECURE_MSG = '<Disabled> *Secure Boot'

    # Option Rom
    ASMEDIA_MSG = 'AsmediaTechnologies|Asmedia Technologies'


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
                              {'PCIE CE Threshold': 10000}]
    RAS_DICT = {
        #   'eventdata' : ['die umc dimm',内存位置]
        '0c': ['0 0 0', 6],  # CPU0_D0
        '0d': ['0 0 1', 7],  # CPU0_D1
        '08': ['0 1 0', 4],  # CPU0_C0
        '09': ['0 1 1', 5],  # CPU0_C1
        '00': ['1 0 0', 0],  # CPU0_A0
        '01': ['1 0 1', 1],  # CPU0_A1
        '04': ['1 1 0', 2],  # CPU0_B0
        '05': ['1 1 1', 3],  # CPU0_B1
        '2c': ['2 0 0', 14],  # CPU1_D0
        '2d': ['2 0 1', 15],  # CPU1_D1
        '28': ['2 1 0', 12],  # CPU1_C0
        '29': ['2 1 1', 13],  # CPU1_C1
        '20': ['3 0 0', 8],  # CPU1_A0
        '21': ['3 0 1', 9],  # CPU1_A1
        '24': ['3 1 0', 10],  # CPU1_B0
        '25': ['3 1 1', 11],  # CPU1_B1
    }
