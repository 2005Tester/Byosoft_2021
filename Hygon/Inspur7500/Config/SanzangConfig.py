#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
from Inspur7500.Config.PlatConfig import Sanzang


class Env:
    # 测试报告设置
    PROJECT_NAME = "Inspur7500"
    SUT_CONFIG = "SUT1-Half-DIMM"

    # 测试文件
    TESTCASE_CSV = "Inspur7500\\AllTest2.csv"

    # 日志路径
    LOG = 'e:\\daily\\Sanzang'

    # 串口号
    BIOS_SERIAL = "com6"

    # BMC 配置
    BMC_IP = '192.168.6.68'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # 系统 配置
    OS_IP = '192.168.6.122'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    # Legacy 系统配置
    OS_IP_LEGACY = '192.168.6.122'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    # Smbios 路径
    SMBIOS = "Inspur7500\\Tools\\smbiossanzang\\"

    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sdd4"
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs3:"
    USB_VOLUME = "USB:Kingston DataTraveler 2.0 \(P4\)"

    # U盘存放BIOS文件，刷新工具的文件夹名称
    BIOS_FILE = 'Sanzang'
    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)

    # OEM命令
    SET_BIOS_SERIAL = 'raw 0x3e 0xc4 0x01'  # 切换BIOS串口
    GET_OPTION = 'raw 0x3e 0xc2'  # OEM命令获取
    CHANGE_OPTION = 'raw 0x3e 0xc3 0x01'  # OEM修改


class Msg(Sanzang):
    # Menus of boot page
    USB_UEFI = 'UEFI USB: Kingston DataTraveler 2.0'
    DOS = "USB: Kingston DataTraveler 2.0"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun Gigabit Server Adapter WX1860NCSI PXE IPv4|UEFI Onboard: Port 0 - WangXun Gigabit Server Adapter WX1860NCSI-2 PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun Gigabit Server Adapter WX1860NCSI PXE IPv4|UEFI Onboard: Port 1 - WangXun Gigabit Server Adapter WX1860NCSI-2 PXE IPv4"
    LEGACY_HDD_BOOT_NAME = "SATA1-6: Samsung SSD 870 EVO 250GB|UEFI SATA1-6: Samsung SSD 870 EVO 250GB"
    UEFI_HDD_BOOT_NAME = 'kos\(UEFI SATA1-7: SAMSUNG MZ7L3480HCHQ-00B7C\)|SATA1-7: SAMSUNG MZ7L3480HCHQ-00B7C'
    # LINUX_OS = 'UOS\(UEFI SATA1-7: SAMSUNG MZ7L3480HCHQ-00B7C\)|SATA1-6: Samsung SSD 870 EVO 250GB'
    LINUX_OS = 'kos\(UEFI SATA1-7: SAMSUNG MZ7L3480HCHQ-00B7C\)|SATA1-6: Samsung SSD 870 EVO 250GB'


class Boot:
    # Boot order
    BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.USB_BOOT_NAME, Msg.PXE_BOOT_NAME,
                           Msg.ODD_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.USB_BOOT_NAME, Msg.PXE_BOOT_NAME,
                             Msg.ODD_BOOT_NAME]

    # Tencent
    # BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.ODD_BOOT_NAME,
    #                        Msg.USB_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    # BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.ODD_BOOT_NAME,
    #                          Msg.USB_BOOT_NAME, Msg.OTHER_BOOT_NAME]

    # Baidu
    # BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.USB_BOOT_NAME,
    #                        Msg.ODD_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    # BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.USB_BOOT_NAME,
    #                          Msg.ODD_BOOT_NAME]

    # PingAn
    # BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.USB_BOOT_NAME,
    #                        Msg.ODD_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    # BOOT_NAME_LIST_LEGACY = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.USB_BOOT_NAME,
    #                          Msg.ODD_BOOT_NAME]


class Cpu:
    # CPU频率
    CPU_FREQUENCY = ['1600', '2000', '2700']  # SetUp下可以设定的CPU频率

    # CPU P-State
    CPU_FREQUENCY_PSTATE = ['2.90', '2.00', '1.60']  # 海光工具检测，P0、P1、P2 CPU频率

    # CPU 降核
    # CPU_DOWNCORE_CORE = ['8', '8', '12', '16', '16', '24']  # CPU降核
    CPU_DOWNCORE_CORE = ['8', '16', '24']
    # DOWNCORE_VALUES = ['TWO (1 + 1)', 'TWO (2 + 0)', 'THREE (3 + 0)', 'FOUR (2 + 2)', 'FOUR (4 + 0)', 'SIX (3 + 3)']
    DOWNCORE_VALUES = ['TWO (1 + 1)', 'FOUR (4 + 0)', 'SIX (3 + 3)']

    # CPU NUMA
    NUMA_VALUES = ['Socket', 'None', 'Channel', 'Die', 'Auto']
    CPU_NUMA_ONE = ['1', '4', '4', '1', '4']  # NUMA单路CPU分别对应插槽、没有、通道、裸片、自动
    CPU_NUMA_TWO = ['1', '8', '8', '2', '8']  # NUMA双路CPU分别对应插槽、没有、通道、裸片、自动

    # CPU CPB
    CPU_FREQUENCY_CPB = ['2.70', '2.90']  # 海光工具检测,超频关闭，打开下CPU频率

    # CPU Performance
    VALUE_CPU_SPEED = ['1.60', '2.00', '2.70', '2.90']  # 每个值对应的CPU频率


class Psw:
    TRY_COUNTS = 3  # 输错密码重试次数,3代表输错3次后，第4次输错会被锁定

    # 硬盘名及对应的系统
    HDD_PASSWORD_NAME_01 = 'SATA1-6: Samsung SSD 870 EVO 250GB'
    HDD_PASSWORD_NAME_02 = 'SATA1-7: SAMSUNG MZ7L3480HCHQ-00B7C'
    # HDD_PASSWORD_NAME_03 = 'NVME\(PCI2\-0\-0\): SAMSUNG MZVLW256HEHP\-000L7'
    HDD_NAME_01_OS = 'UEFI SATA1-6: Samsung SSD 870 EVO 250GB'
    HDD_NAME_02_OS = 'kos\(UEFI SATA1-7: SAMSUNG MZ7L3480HCHQ-00B7C\)'


class Pxe:
    # PXE 重试
    PXE_RETRY_MSG = 'UEFI Onboard: Port 1 \- WangXun Gigabit Server Adapter WX1860NCSI\-2 HTTP IPv4'

    # LegacyPXE 重试
    PXE_RETRY_MSG_LEGACY = 'WangXun\(R\) *PXE *\(PCI02:00.0\)|WangXun\(R\) *PXE *\(PCI01:00.0\)'

    # PXE启动网卡
    PXE_NET_ONBOARD = "WangXun Gigabit Server Adapter WX1860NCSI (02-02-03-04-05-06)"
    # PXE_NET_ADDON = "Intel(R) Ethernet Converged Network Adapter X710 (40-A6-B7-1B-72-E4)"
    # PXE_NET_ADDON = "Inspur(R) Ethernet Controller X550 (B4-05-5D-16-7C-2E)"
    PXE_NET_ADDON = "Inspur(R) Ethernet Controller E810-XXV for SFP (EF-BE-AD-DE-EF-BE)"
    # PXE_NET_ADDON = 'Intel(R) Ethernet Controller 10 Gigabit X540-AT2 (E8-61-1F-29-D8-85)'

    # PXE启动项(IPv4)
    PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d+ - Inspur\(R\) Ethernet Controller E810-XXV for (?:SFP|SFP-2) (?:PXE|HTTP) IPv4'
    # PXE_PORT_ADDON =  'UEFI Slot \d+: Port \d+ - Intel\(R\) Ethernet Controller 10 Gigabit (?:X540-AT2|X540-AT2-2) (?:PXE|HTTP) IPv4'
    # PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d+ - Inspur\(R\) Ethernet Controller (?:X550|X550-2) (?:PXE|HTTP) IPv4'
    # PXE_PORT_ADDON = 'UEFI Slot \d+: Port \d+ - Intel\(R\) Ethernet Converged Network Adapter (?:X710|X710-2) (?:PXE|HTTP) IPv4'
    PXE_PORT_ONBOARD = "UEFI Onboard: Port \d - WangXun Gigabit Server Adapter (?:WX1860NCSI|WX1860NCSI-2) (?:PXE|HTTP) IPv4"

    # Higest Boot Priority
    HIGHEST_DEVICE = 'UEFI Slot \d+: Port \d+ - Intel\(R\) Ethernet Converged Network Adapter (?:X710|X710-2) (?:PXE|HTTP) IPv4'
    OPEN_HIGHEST_DEVICE = ['User Wait Time', {'Highest Boot Priority Device': 'Enabled'}]
    CLOSE_HIGHEST_DEVICE = ['User Wait Time', {'Highest Boot Priority Device': 'Disabled'}]


class Sup:
    # 网络唤醒
    MAC_ADDRESS = '02-02-03-04-05-06|02-02-03-04-05-07'

    # HDD Bind
    HDD_BIND_NAME_1 = 'B6D0F2 Samsung SSD 870 EVO 2 S6PFNX0T330003J'
    HDD_BIND_NAME_2 = 'B6D0F2 SAMSUNG MZ7L3480HCHQ- S6KLNE0RA02530'
    HDD_BIND_NAME_1_OS = Msg.LEGACY_HDD_BOOT_NAME
    HDD_BIND_NAME_2_OS = Msg.UEFI_HDD_BOOT_NAME
    HDD_BIND_PROMPT = 'Hdd has been changed'  ################################################

    # 内存频率
    MEMORY_SPEED = ['667', '800', '1067', '1200', '1333']  # SetUp下可以设置的内存频率

    # 联动关系
    OPEN_SECURE = ['Set Administrator Password', 'Secure Boot', {'Secure Boot Default Key Provision': 'Auto'}]
    CLOSE_SECURE_MSG = '<Manual> *Secure Boot Default Key Provision'

    # Option Rom
    ASMEDIA_MSG = 'WangXun\(R\) *PXE'


class Upd:
    PASSWORDS = ['Admin@1116', 'Users@1116']

    BMC_LINK_OPTION = ['<Disabled>SOLforBaseboardMgmt', '<Enabled>SOLforBaseboardMgmt', '<StayOff>RestoreACpowerloss',
                       '<LastState>RestoreACpowerloss', '<PowerOn>RestoreACpowerloss']

    # 通用默认值
    STANDARD = [  # 主菜单
        ['<English>SelectLanguage', '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA'],
        #  高级菜单
        ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '<Enabled>ConsoleRedirection',
         '<115200>SerialPortBaudrate', '<8DataBits>SerialDataBits', '<Noparity>SerialParityType', '<1>SerialStopBits',
         '<VT-UTF8>TerminalType', '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan',
         '<PCIE>PrimaryGraphicsAdapter', '<Enabled>USBMassStorageSupport', '<Enabled>RearUSBPortConfiguration',
         '<Enabled>FrontUSBPortConfiguration', '<Disabled>IOMMU', '<Enabled>SVM', '<Enabled>SR-IOVSupport',
         '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit', '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock',
         '<Auto>PCIEMaxPayloadSize', '<Disabled>PCIEASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
         '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode', '<Disabled>FCHSSC',
         '<Disabled>HygonTPCM', '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
         '<Disabled>SOLforBaseboardMgmt', '<LastState>RestoreACpowerloss', '<Enabled>SelComponents',
         '<NoClear>AllowClearBMCSystemEventLog', '<Disabled>SelStatusCode', '<Enabled>NCSI', '<Dynamic>IPv4Source',
         '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<Dynamic>IPv4Source', '<Enabled>IPv6',
         '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<NoAccess>Privilege', '<Disabled>UserStatus',
         '<NoAccess>Privilege', '<Disabled>UserStatus', '<Enabled>PlatformFirstErrorHandling',
         '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount', '[10000]PcieCEThreshold',
         '[4095]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
         '<Enabled>ChipselectInterleaving', '<Auto>Channelinterleaving', '<Auto>NUMA', '<Auto>Memoryinterleavingsize',
         '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider', '<Disabled>RDSEEDandRDRANDControl',
         '<Auto>DRAMscrubtime', '<Auto>cTDPControl', '<Auto>EfficiencyOptimizedMode', '<Auto>BankInterleaving',
         '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable',
         '<Unbind>HDDBind'],
        #  安全菜单
        ['[100]PasswordLockTime', '<30Days>PasswordValidDays', '<Disabled>Power-onPassword',
         '<Enabled>CustomPasswordCheck', '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
         '<DTPM>TPMSelect', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot', '<Enter>RestoreFactoryKeys',
         '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode', '<Enter>EnterDeployedMode',
         # '<Enabled>PHRandomization', '<1.3>AttemptPPIVersion', '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy',
         # '[0]TPM2OperationParameter', '<Rev4>AttemptRevofTPM2ACPITable', '<NoAction>TPM2Operation', '<Enabled>PlatformHierarchy',
         # '<Enabled>TPMState'
         ],
        #  启动菜单
        ['[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
         '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
         '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion', '<Disabled>PXEBootPriority'],
        #  退出菜单
        ['<FullUpdate>BIOSUpdateParameters']]

    # 百度默认值
    BAIDU = [  # 主菜单
        ['<English>SelectLanguage', '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA'],
        # 高级菜单
        ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '<Enabled>ConsoleRedirection',
         '<8DataBits>SerialDataBits', '<Noparity>SerialParityType', '<1>SerialStopBits', '<VT-UTF8>TerminalType',
         '<Disabled>OnboardEthernetController', '<PCIE>PrimaryGraphicsAdapter', '<Enabled>OnboardSATAController',
         '<Enabled>USBMassStorageSupport', '<Enabled>RearUSBPortConfiguration', '<Enabled>FrontUSBPortConfiguration',
         '<Auto>IOMMU', '<Enabled>SVM', '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit',
         '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize', '<Disabled>PCIEASPM',
         '<Enabled>AES', '<Enabled>HyperThreadingTechnology', '<120>MemoryCEStormThreshold',
         '<1200>MemoryCEAccumulationThreshold', '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode',
         '<Disabled>FCHSSC', '<Disabled>HygonTPCM', '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
         '<Disabled>SOLforBaseboardMgmt', '<PowerOn>RestoreACpowerloss', '<Enabled>SelComponents',
         '<NoClear>AllowClearBMCSystemEventLog', '<Disabled>SelStatusCode', '<Enabled>NCSI', '<Dynamic>IPv4Source',
         '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<Dynamic>IPv4Source', '<Enabled>IPv6',
         '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<NoAccess>Privilege', '<Disabled>UserStatus',
         '<NoAccess>Privilege', '<Disabled>UserStatus', '<Enabled>PlatformFirstErrorHandling',
         '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount', '<2000>PcieCEThreshold',
         '[4095]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
         '<Auto>ChipselectInterleaving', '<Enabled>Channelinterleaving', '<Channel>MemoryInterleaving',
         '<Auto>Memoryinterleavingsize', '<Auto>Redirectscrubbercontrol', '<Performance>DeterminismSlider',
         '<Disabled>RDSEEDandRDRANDControl', '<Auto>DRAMscrubtime', '<Auto>cTDPControl',
         '<Disabled>EfficiencyOptimizedMode', '<Enabled>BankInterleaving', '<Auto>L1StreamHWPrefetcher',
         '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable', '<Unbind>HDDBind'],
        # 安全菜单
        ['[100]PasswordLockTime', '<30Days>PasswordValidDays', '<Disabled>Power-onPassword',
         '<Enabled>CustomPasswordCheck', '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
         '<DTPM>TPMSelect', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot', '<Enter>RestoreFactoryKeys',
         '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode', '<Enter>EnterDeployedMode',
         # '<Enabled>PHRandomization', '<1.3>AttemptPPIVersion', '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy',
         # '[0]TPM2OperationParameter', '<Rev4>AttemptRevofTPM2ACPITable', '<NoAction>TPM2Operation', '<Enabled>PlatformHierarchy',
         # '<Enabled>TPMState'
         ],
        # 启动菜单
        ['[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
         '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
         '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion', '<Disabled>HighestBootPriorityDevice'],
        # 退出菜单
        ['<FullUpdate>BIOSUpdateParameters']]

    # 腾讯默认值
    TENCENT = [  # 主菜单
        ['<English>SelectLanguage', '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA'],
        # 高级菜单
        ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '<Enabled>ConsoleRedirection',
         '<115200>SerialPortBaudrate', '<8DataBits>SerialDataBits', '<Noparity>SerialParityType', '<1>SerialStopBits',
         '<VT-UTF8>TerminalType', '<Disabled>OnboardEthernetController', '<PCIE>PrimaryGraphicsAdapter',
         '<Enabled>USBMassStorageSupport', '<Enabled>RearUSBPortConfiguration', '<Enabled>FrontUSBPortConfiguration',
         '<Enabled>IOMMU', '<Enabled>SVM', '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit',
         '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize', '<Disabled>PCIEASPM',
         '<Enabled>AES', '<Enabled>HyperThreadingTechnology', '<Disabled>DebugPrintLevel',
         '<Performance>ENERGY_PERF_BIAS_CFGmode', '<Disabled>FCHSSC', '<Disabled>HygonTPCM',
         '<Enabled>FRB2WatchdogTimer', '<Reset>FRB2WatchdogTimerPolicy', '<6minutes>FRB2WatchdogTimerTimeout',
         '<Disabled>OSBootWatchdogTimer', '<Disabled>SOLforBaseboardMgmt', '<StayOff>RestoreACpowerloss',
         '<Enabled>SelComponents', '<NoClear>AllowClearBMCSystemEventLog', '<Disabled>SelStatusCode', '<Enabled>NCSI',
         '<Dynamic>IPv4Source', '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<Dynamic>IPv4Source',
         '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<NoAccess>Privilege', '<Disabled>UserStatus',
         '<NoAccess>Privilege', '<Disabled>UserStatus', '<Enabled>PlatformFirstErrorHandling',
         '<2000>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount', '[10000]PcieCEThreshold',
         '[4095]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
         '<Enabled>ChipselectInterleaving', '<Auto>Channelinterleaving', '<Channel>NUMA',
         '<Auto>Memoryinterleavingsize', '<Auto>Redirectscrubbercontrol', '<Performance>DeterminismSlider',
         '<Disabled>RDSEEDandRDRANDControl', '<Auto>DRAMscrubtime', '<Auto>cTDPControl',
         '<Auto>EfficiencyOptimizedMode', '<Enabled>BankInterleaving', '<Auto>L1StreamHWPrefetcher',
         '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable', '<Unbind>HDDBind'],
        # 安全菜单
        ['[100]PasswordLockTime', '<30Days>PasswordValidDays', '<Disabled>Power-onPassword',
         '<Enabled>CustomPasswordCheck', '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
         '<Disable>TPMSelect', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot',
         '<Enter>RestoreFactoryKeys', '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode',
         '<Enter>EnterDeployedMode',
         # '<Enabled>PHRandomization', '<1.3>AttemptPPIVersion', '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy',
         # '[0]TPM2OperationParameter', '<Rev4>AttemptRevofTPM2ACPITable', '<NoAction>TPM2Operation', '<Enabled>PlatformHierarchy',
         # '<Enabled>TPMState'
         ],
        # 启动菜单
        ['[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
         '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
         '<Enabled>PXEBootOptionsRetry', '<IPv4>NetBootIPVersion'],
        # 退出菜单
        ['<FullUpdate>BIOSUpdateParameters']]

    # 平安默认值
    PINGAN = [  # 主菜单
        ['<English>SelectLanguage', '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA'],
        # 高级菜单
        ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '<Enabled>ConsoleRedirection',
         '<115200>SerialPortBaudrate', '<8DataBits>SerialDataBits', '<Noparity>SerialParityType',
         '<1>SerialStopBits', '<VT-UTF8>TerminalType', '<Disabled>OnboardEthernetController',
         '<PCIE>PrimaryGraphicsAdapter', '<Enabled>USBMassStorageSupport', '<Enabled>RearUSBPortConfiguration',
         '<Enabled>FrontUSBPortConfiguration', '<Disabled>IOMMU', '<Enabled>SVM', '<Enabled>SR-IOVSupport',
         '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit', '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock',
         '<Auto>PCIEMaxPayloadSize', '<Disabled>PCIEASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
         '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode', '<Disabled>FCHSSC',
         '<Disabled>HygonTPCM', '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
         '<Enabled>SOLforBaseboardMgmt', '<LastState>RestoreACpowerloss', '<Enabled>SelComponents',
         '<NoClear>AllowClearBMCSystemEventLog', '<Disabled>SelStatusCode', '<Disabled>NCSI',
         '<Dynamic>IPv4Source', '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength',
         '<NoAccess>Privilege', '<Disabled>UserStatus', '<NoAccess>Privilege', '<Disabled>UserStatus',
         '<Enabled>PlatformFirstErrorHandling', '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime',
         '[60]LeakyBucketCount', '[10000]PcieCEThreshold', '[4095]CPUCEThreshold',
         '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
         '<Enabled>ChipselectInterleaving', '<Auto>Channelinterleaving', '<Auto>NUMA',
         '<Auto>Memoryinterleavingsize', '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider',
         '<Disabled>RDSEEDandRDRANDControl', '<Auto>DRAMscrubtime', '<Auto>cTDPControl',
         '<Auto>EfficiencyOptimizedMode', '<Auto>BankInterleaving', '<Auto>L1StreamHWPrefetcher',
         '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable', '<Unbind>HDDBind'],
        # 安全菜单
        ['[100]PasswordLockTime', '<30Days>PasswordValidDays', '<Disabled>Power-onPassword',
         '<Enabled>CustomPasswordCheck', '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
         '<Disable>TPMSelect', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot',
         '<Enter>RestoreFactoryKeys', '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode',
         '<Enter>EnterDeployedMode',
         # '<Enabled>PHRandomization', '<1.3>AttemptPPIVersion', '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy',
         # '[0]TPM2OperationParameter', '<Rev4>AttemptRevofTPM2ACPITable', '<NoAction>TPM2Operation', '<Enabled>PlatformHierarchy',
         # '<Enabled>TPMState'
         ],
        # 启动菜单
        ['[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState',
         '<UEFI>BootMode', '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
         '<Enabled>PXEBootOptionsRetry', '<IPv4>NetBootIPVersion'],
        # 退出菜单
        ['<FullUpdate>BIOSUpdateParameters']]

    ALI = [  # 主菜单
        ['<English>SelectLanguage', '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA'],
        # 高级菜单
        ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '<Enabled>ConsoleRedirection',
         '<115200>SerialPortBaudrate', '<8DataBits>SerialDataBits', '<Noparity>SerialParityType', '<1>SerialStopBits',
         '<VT-UTF8>TerminalType', '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan',
         '<PCIE>PrimaryGraphicsAdapter', '<Enabled>OnboardSATAController', '<Enabled>USBMassStorageSupport',
         '<Enabled>RearUSBPortConfiguration', '<Enabled>FrontUSBPortConfiguration', '<Disabled>IOMMU', '<Enabled>SVM',
         '<Enabled>SR-IOVSupport', '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit', '<Disabled>HideBootLogo',
         '<Disabled>SPIBIOSLock', '<Auto>PCIEMaxPayloadSize', '<Disabled>PCIEASPM', '<Enabled>AES',
         '<Enabled>HyperThreadingTechnology', '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode',
         '<Disabled>FCHSSC', '<Disabled>HygonTPCM', '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
         '<Disabled>SOLforBaseboardMgmt', '<LastState>RestoreACpowerloss', '<Enabled>SelComponents',
         '<NoClear>AllowClearBMCSystemEventLog', '<Disabled>SelStatusCode', '<Disabled>NCSI', '<Dynamic>IPv4Source',
         '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<NoAccess>Privilege', '<Disabled>UserStatus',
         '<NoAccess>Privilege', '<Disabled>UserStatus', '<Enabled>PlatformFirstErrorHandling',
         '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount', '[10000]PcieCEThreshold',
         '[4095]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
         '<Enabled>ChipselectInterleaving', '<Auto>Channelinterleaving', '<Auto>NUMA', '<Auto>Memoryinterleavingsize',
         '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider', '<Disabled>RDSEEDandRDRANDControl',
         '<Auto>DRAMscrubtime', '<Auto>cTDPControl', '<Auto>EfficiencyOptimizedMode', '<Auto>BankInterleaving',
         '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable',
         '<Unbind>HDDBind'],
        # 安全菜单
        ['[100]PasswordLockTime', '<30Days>PasswordValidDays', '<Disabled>Power-onPassword',
         '<Enabled>CustomPasswordCheck', '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
         '<DTPM>TPMSelect', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot', '<Enter>RestoreFactoryKeys',
         '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode', '<Enter>EnterDeployedMode',
         # '<Enabled>PHRandomization', '<1.3>AttemptPPIVersion', '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy',
         # '[0]TPM2OperationParameter', '<Rev4>AttemptRevofTPM2ACPITable', '<NoAction>TPM2Operation', '<Enabled>PlatformHierarchy',
         # '<Enabled>TPMState'
         ],
        # 启动菜单
        ['[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
         '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
         '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion', '<Disabled>PXEBootPriority'],
        # 退出菜单
        ['<FullUpdate>BIOSUpdateParameters']]

    JD = [  # 主菜单
        ['<English>SelectLanguage', '<Disabled>MCIO0_CPU1asSATA', '<Disabled>MCIO2_CPU1asSATA'],
        # 高级菜单
        ['<0>Silkscreenstartnumber', '<Continuetostart>Memoryerrorbehavior', '<Enabled>ConsoleRedirection',
         '<115200>SerialPortBaudrate', '<8DataBits>SerialDataBits', '<Noparity>SerialParityType', '<1>SerialStopBits',
         '<None>FlowControl', '<VT-UTF8>TerminalType', '<Enabled>OnboardEthernetController', '<Enabled>WakeOnLan',
         '<PCIE>PrimaryGraphicsAdapter', '<Enabled>USBMassStorageSupport', '<Enabled>RearUSBPortConfiguration',
         '<Enabled>FrontUSBPortConfiguration', '<Enabled>IOMMU', '<Enabled>SVM', '<Enabled>SR-IOVSupport',
         '<Enabled>Above4GDecoding', '<8TB>MMIOHighLimit', '<Disabled>HideBootLogo', '<Disabled>SPIBIOSLock',
         '<Auto>PCIEMaxPayloadSize', '<Disabled>PCIEASPM', '<Enabled>AES', '<Enabled>HyperThreadingTechnology',
         '<Disabled>DebugPrintLevel', '<Performance>ENERGY_PERF_BIAS_CFGmode', '<Disabled>FCHSSC',
         '<Disabled>HygonTPCM', '<Disabled>FRB2WatchdogTimer', '<Disabled>OSBootWatchdogTimer',
         '<Enabled>SOLforBaseboardMgmt', '<LastState>RestoreACpowerloss', '<Enabled>SelComponents',
         '<NoClear>AllowClearBMCSystemEventLog', '<Disabled>SelStatusCode', '<Enabled>NCSI', '<Dynamic>IPv4Source',
         '<Enabled>IPv6', '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<Dynamic>IPv4Source', '<Enabled>IPv6',
         '<Dynamic>IPv6Source', '[0]IPv6PrefixLength', '<NoAccess>Privilege', '<Disabled>UserStatus',
         '<NoAccess>Privilege', '<Disabled>UserStatus', '<Enabled>PlatformFirstErrorHandling',
         '<4095>MCAErrorThresholdCount', '[1]LeakyBucketTime', '[60]LeakyBucketCount', '[10000]PcieCEThreshold',
         '[4095]CPUCEThreshold', '<Auto>Allowsettingmemoryfrequency', '<Auto>Downcorecontrol', '<Disabled>SMEEControl',
         '<Auto>ChipselectInterleaving', '<Enabled>Channelinterleaving', '<Auto>NUMA', '<Auto>Memoryinterleavingsize',
         '<Auto>Redirectscrubbercontrol', '<Auto>DeterminismSlider', '<Disabled>RDSEEDandRDRANDControl',
         '<Auto>DRAMscrubtime', '<Auto>cTDPControl', '<Auto>EfficiencyOptimizedMode', '<Enabled>BankInterleaving',
         '<Auto>L1StreamHWPrefetcher', '<Auto>L2StreamHWPrefetcher', '<Auto>NBIORASControl', '<Auto>ACSEnable',
         '<Unbind>HDDBind'],
        # 安全菜单
        ['[100]PasswordLockTime', '<30Days>PasswordValidDays', '<Disabled>Power-onPassword',
         '<Enabled>CustomPasswordCheck', '<Enabled>PasswordComplexity', '[10]PasswordLength', '[6]PasswordRetry',
         '<DTPM>TPMSelect', '<SHA-256Hash>SetHddPasswordHashType', '<Disabled>SecureBoot', '<Enter>RestoreFactoryKeys',
         '<Enter>ResetPlatformtoSetupMode', '<Enter>EnterAuditMode', '<Enter>EnterDeployedMode',
         # '<Enabled>PHRandomization', '<1.3>AttemptPPIVersion', '<Enabled>StorageHierarchy', '<Enabled>EndorsementHierarchy',
         # '[0]TPM2OperationParameter', '<Rev4>AttemptRevofTPM2ACPITable', '<NoAction>TPM2Operation', '<Enabled>PlatformHierarchy',
         # '<Enabled>TPMState'
         ],
        # 启动菜单
        ['[5]UserWaitTime', '<Disabled>QuietBoot', '<On>BootupNumLockState', '<UEFI>BootMode',
         '<Disabled>InternalSHELL', '<Enabled>PXEOptionRom', '<NULL>SelectaNetworktoPXE',
         '<Enabled>PXEBootOptionsRetry', '<IPv4andIPv6>NetBootIPVersion', '<Disabled>PXEBootPriority'],
        # 退出菜单
        ['<FullUpdate>BIOSUpdateParameters']]

    DEFAULT_OPTION_VALUE = sum(JD, [])

    SHELL_FLASH_CMD_LATEST_ALL = 'ByoFlash.efi -bfu latest.bin -all'
    SHELL_FLASH_CMD_PREVIOUS_ALL = 'ByoFlash.efi -bfu previous.bin -all'
    SHELL_FLASH_CMD_CONSTANT_ALL = 'ByoFlash.efi -bfu constant.bin -all'
    SHELL_FLASH_CMD_LATEST = 'ByoFlash.efi -bfu latest.bin'
    SHELL_FLASH_CMD_PREVIOUS = 'ByoFlash.efi -bfu previous.bin'
    SHELL_FLASH_CMD_CONSTANT = 'ByoFlash.efi -bfu constant.bin'

    LINUX_FLASH_CMD_LATEST_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -all'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin -all'
    LINUX_FLASH_CMD_CONSTANT_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}constant.bin -all'
    LINUX_FLASH_CMD_LATEST = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_FLASH_CMD_CONSTANT = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}constant.bin'

    SHELL_FLASH_CMD_OTHERS = 'ByoFlash.efi -bfu others.bin'
    SHELL_FLASH_CMD_UNSIGNED = 'ByoFlash.efi -bfu unsigned.bin'
    LINUX_FLASH_CMD_OTHERS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'


class Ras:
    SET_LEAKY_BUCKET_1 = [{'MCA Error Threshold Count': '1'}, {'Leaky Bucket Time': 35}, {'Leaky Bucket Count': 2}]
    SET_LEAKY_BUCKET_2 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 75}, {'Leaky Bucket Count': 15}]
    SET_LEAKY_BUCKET_3 = [{'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 7}, {'Leaky Bucket Count': 1}]

    SET_PCIE_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                              {'Pcie CE Threshold': 10000}]

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
        '1c': ['2 0 0', 14],  # CPU0_H0
        '1d': ['2 0 1', 15],  # CPU0_H1
        '18': ['2 1 0', 12],  # CPU0_G0
        '19': ['2 1 1', 13],  # CPU0_G1
        '10': ['3 0 0', 8],  # CPU0_E0
        '11': ['3 0 1', 9],  # CPU0_E1
        '14': ['3 1 0', 10],  # CPU0_F0
        '15': ['3 1 1', 11],  # CPU0_F1
        '2c': ['4 0 0', 22],  # CPU1_D0
        '2d': ['4 0 1', 23],  # CPU1_D1
        '28': ['4 1 0', 20],  # CPU1_C0
        '29': ['4 1 1', 21],  # CPU1_C1
        '20': ['5 0 0', 16],  # CPU1_A0
        '21': ['5 0 1', 17],  # CPU1_A1
        '24': ['5 1 0', 18],  # CPU1_B0
        '25': ['5 1 1', 19],  # CPU1_B1
        '3c': ['6 0 0', 30],  # CPU1_H0
        '3d': ['6 0 1', 31],  # CPU1_H1
        '38': ['6 1 0', 28],  # CPU1_G0
        '39': ['6 1 1', 29],  # CPU1_G1
        '30': ['7 0 0', 24],  # CPU1_E0
        '31': ['7 0 1', 25],  # CPU1_E1
        '34': ['7 1 0', 26],  # CPU1_F0
        '35': ['7 1 1', 27],  # CPU1_F1
    }
