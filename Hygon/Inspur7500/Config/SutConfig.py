#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation

# -*- encoding=utf8 -*-
import importlib
import re

from batf import var
import os
import datetime
from Inspur7500.Config import PutiConfig as SutCfgMde

# SutCfgMde = importlib.import_module(var.get('SutCfg'), var.get('project'))


exec("SutCfgMde = importlib.import_module(var.get('SutCfg'), var.get('project'))")


class _Env:
    REPORT_TEMPLATE = "Inspur7500\\Report\\template"

    # 生成日志文件
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = os.path.join(SutCfgMde.Env.LOG, timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    RELEASE_BRANCH = "Hygon_017"

    BMC_SERIAL_USER = 'root'
    BMC_SERIAL_PASSWORD = '0penBmc'

    # Ipmi工具存放路径
    IPMITOOL = "Inspur7500\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(SutCfgMde.Env.BMC_IP,
                                                                                                  SutCfgMde.Env.BMC_USER,
                                                                                                  SutCfgMde.Env.BMC_PASSWORD)
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

    LINUX_USB_MOUNT = "/mnt/"
    WINDOWS_FLASH_CMD = "ByoWinFlash.exe bfu"
    DOS_FLASH_CMD = "byoflash bfu"
    LATEST_BIOS_FILE = "latest.bin"
    PREVIOUS_BIOS_FILE = "previous.bin"
    CONSTANT_BIOS_FILE = "constant.bin"
    OTHERS_BIOS_FILE = 'others.bin'
    UNSIGNED_BIOS_FILE = 'unsigned.bin'


class Env(SutCfgMde.Env,_Env):
    pass


class _Msg:
    POST_MESSAGE = 'DEL to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot'
    HOTKEY_PROMPT_DEL = 'DEL to enter SETUP'
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu'
    HOTKEY_PROMPT_F12 = 'Press F12 to PXE boot|Press F12 to enter PXE boot'

    ENTER_BOOTMENU = "Startup Device Menu|ENTER to select boot device"
    ENTER_SETUP = "Enter Setup"
    SHELL = "Internal EDK Shell"


class Msg(SutCfgMde.Msg,_Msg):
    pass


class _Boot:
    SERVICE_CONFIG = [Msg.PAGE_ADVANCED, Msg.SERVER_CONFIG]
    LOC_USB = [Msg.PAGE_ADVANCED, Msg.USB_CONFIG]
    LOC_HDD = [Msg.PAGE_BOOT, Msg.HDD_BOOT_NAME]
    CPU_INFO = [Msg.CPU_INFO]
    MEM_INFO = [Msg.MEM_INFO]
    ONBOARD_ETH = [Msg.PAGE_ADVANCED, Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'}]
    PXE = [Msg.PAGE_BOOT, {'PXE Option Rom': 'Enabled'}]


class Boot(SutCfgMde.Boot,_Boot):
    pass


class _Cpu:
    MONITOR_TOOL = 'monitor_0.1.8'
    PSTATE_TOOL = 'pstate-set.sh'
    CSTATE_TOOL = 'SMUToolSuite'
    # CPU信息
    CPU_INFO = [Msg.PAGE_MAIN, Msg.CPU_INFO]

    # CPU频率
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
                   {'Set CPU Speed': '{0} MHz'.format(SutCfgMde.Cpu.CPU_FREQUENCY[-1])}]
    CLOSE_CSTATE = ['Console Redirection', 'Misc Configuration', {'CPU C-State Control': 'Disabled'}]

    # CPU P-State
    SET_PSTATE_P0 = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                     {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Disabled'},
                     {'Set CPU Speed': '{0} MHz'.format(SutCfgMde.Cpu.CPU_FREQUENCY[-1])}]
    SET_PSTATE_P0P1 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1'}]
    SET_PSTATE_P0P1P2 = ['Console Redirection', 'Misc Configuration', {'CPU P-State Control': 'P0+P1+P2'}]
    SET_HIGH = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'Performance'}]

    # CPU 降核
    LOC_DOWNCORE = ['Console Redirection', 'Hygon CBS']
    DOWNCORE_NAME = 'Downcore control'
    SET_DOWNCORE_AUTO = ['Console Redirection', 'Hygon CBS', {'Downcore control': 'Auto'}]

    # CPU AES
    CLOSE_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Disabled'}]
    OPEN_AES = ['Console Redirection', 'Misc Configuration', {'AES': 'Enabled'}]

    # NUMA
    LOC_NUMA = ['Console Redirection', 'Hygon CBS']
    NUMA_NAME = 'NUMA'

    CLOSE_CPB = ['Console Redirection', 'Misc Configuration', {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'},
                 {'CPU P-State Control': 'P0'}, {'CPU C-State Control': 'Enabled'},
                 {'Set CPU Speed': '{0} MHz'.format(SutCfgMde.Cpu.CPU_FREQUENCY[-1])}, 'Console Redirection',
                 'Hygon CBS',
                 {'Core Performance Boost': 'Disabled'}]
    OPEN_CPB = ['Console Redirection', 'Hygon CBS', {'Core Performance Boost': 'Auto|Enabled'}]
    LOC_CPU_SPEED = ['Console Redirection', 'Misc Configuration']

    # CPU Performance
    LOC_PERFORMANCE = ['Console Redirection', 'Misc Configuration']
    PERFORMANCE_NAME = 'ENERGY_PERF_BIAS_CFG mode'
    PERFORMANCE_VALUE_NAME = ['Energy', 'Energy Balance', 'Performance Balance', 'Performance']  # 支持修改的值
    LOC_CPB = ['Console Redirection', 'Hygon CBS']
    CPB_NAME = 'Core Performance Boost'

    # SMEE控制
    OPEN_SMEE = ['Console Redirection', 'Hygon CBS', {'SMEE Control': 'Enabled'}]
    CLOSE_SMEE = ['Console Redirection', 'Hygon CBS', {'SMEE Control': 'Disabled'}]
    SMEE_MSG = 'Secure Memory Encryption \(SME\) active'


class Cpu(SutCfgMde.Cpu,_Cpu):
    pass


class _Psw:
    PAGE_ALL = [Msg.PAGE_MAIN, 'Console Redirection', 'Set User Password', 'Shutdown System']  # 用户密码登录，SetUp页面名

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
    PSW_EXPIRY_DATE = 'Password Valid Days|Set Password Valid Days'
    HDD_PSW_OPTION = Msg.HDD_PSW
    SET_HDD_PSW_OPTION = 'Enable (?:HDD|Hdd) Password|Enable HDD User Password'
    DEL_HDD_PSW_OPTION = 'Disable (?:HDD|Hdd) Password|Disable HDD User Password'
    LOGIN_HDD_PSW_PROMPT = 'Enter (?:HDD|Hdd) Password'
    HDD_LOCK_STATUS = 'security state cannot be changed'
    SET_HDD_HASH_TYPE1 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SHA-256 Hash'}]
    SET_HDD_HASH_TYPE2 = [SET_ADMIN_PSW, HDD_PSW_OPTION, {'Set HddPassword Hash Type': 'SM3 Hash'}]
    LOC_HDD_PSW = [SET_ADMIN_PSW, HDD_PSW_OPTION]
    LOC_USER_PSW = [SET_ADMIN_PSW, SET_USER_PSW]
    LOC_ADMIN_PSW = [SET_ADMIN_PSW]
    LOC_LOCK_OPTION = [SET_ADMIN_PSW, PSW_LOCK_OPTION]
    SET_TIME_WEEK = [{PSW_EXPIRY_DATE: '7 Days'}]
    SET_TIME_MONTH = [{PSW_EXPIRY_DATE: '30 Days'}]
    SET_TIME_ALWAYS = [{PSW_EXPIRY_DATE: 'Indefinite'}]


class Psw(SutCfgMde.Psw,_Psw):
    pass


class Ipm:
    # Frb2_watchdog
    CLOSE_FRB = ['Console Redirection', Msg.SERVER_CONFIG, {'FRB2 Watchdog Timer': 'Disabled'}]
    OPEN_FRB1 = ['Console Redirection', Msg.SERVER_CONFIG, {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '10minutes|10 minutes'}]
    OPEN_FRB2 = ['Console Redirection', Msg.SERVER_CONFIG, {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Power Off'}, {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_FRB3 = ['Console Redirection', Msg.SERVER_CONFIG, {'FRB2 Watchdog Timer': 'Enabled'},
                 {'FRB2 Watchdog Timer Policy': 'Reset'}, {'FRB2 Watchdog Timer Timeout': '5minutes|5 minutes'}]

    # OS watchdog
    OPEN_OS_WDOG1 = ['Console Redirection', Msg.SERVER_CONFIG, {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Power Off'}, {'OS Watchdog Timer Timeout': '10minutes|10 minutes'}]
    OPEN_OS_WDOG2 = ['Console Redirection', Msg.SERVER_CONFIG, {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '30minutes|30 minutes'}]
    OPEN_OS_WDOG3 = ['Console Redirection', Msg.SERVER_CONFIG, {'OS Boot Watchdog Timer': 'Enabled'},
                     {'OS Watchdog Timer Policy': 'Reset'}, {'OS Watchdog Timer Timeout': '5minutes|5 minutes'}]
    CLOSE_OS_WDOG = ['Console Redirection', Msg.SERVER_CONFIG, {'OS Boot Watchdog Timer': 'Disabled'}]

    # Power Loss
    SET_POWER_LOSS1 = ['Console Redirection', Msg.SERVER_CONFIG,
                       {Msg.AC: 'Power On'}]
    SET_POWER_LOSS2 = ['Console Redirection', Msg.SERVER_CONFIG,
                       {Msg.AC: 'Last State'}]
    SET_POWER_LOSS3 = ['Console Redirection', Msg.SERVER_CONFIG,
                       {Msg.AC: 'Stay Off|Always Off'}]
    LOC_SERVICE = ['Console Redirection', Msg.SERVER_CONFIG]
    POWER_LOSS_OPTION = Msg.AC
    POWER_LOSS_VALUE = ['<Power On>', '<Last State>', '<Stay Off>|<Always Off>']

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
                    "TermType": [7, {"VT100": ["6,7", "00"], "VT100+": ["6,7", "01"], "UTF-8": ["6,7", "10"],
                                     "Linux": ["6,7", "11"]}],

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
                                     {f'{Cpu.CPU_FREQUENCY[-1]}MHz': ['4,5', '00'],
                                      f'{Cpu.CPU_FREQUENCY[1]}MHz': ['4,5', '01'],
                                      f'{Cpu.CPU_FREQUENCY[0]}MHz': ['4,5', '10']}],

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
            'RearUSB': 'RearUSBPortConfiguration', 'FrontUSB': Msg.FRONT_USB.replace(' ', ''),
            'USBStorage': 'USBMassStorageSupport', 'MaxPayload': Msg.PCI_MAX.replace(' ', ''),
            'ASPM': Msg.PCI_ASPM.replace(' ', ''),
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
                            'USBStorage:Enabled', 'MaxPayload:128B', 'ASPM:Disabled', 'Perfmode:PerformanceBalance',
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
                            f'CPUFrequency:{Cpu.CPU_FREQUENCY[0]}MHz', 'NumLock:Off', 'OptionRom:Enabled',
                            'UEFIShell:Enabled',
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
    CNANGE_USER_PSW = 'Change User Password|Change user Password'
    USER_PRIVILEGE = 'Privilege'
    CALLBACK = 'Callback'
    USER = 'User'
    OPERATOR = 'Operator'
    ADMIN = 'Administrator'
    NO_ACCESS = 'No Access'
    USER_STATE = 'User Status '
    DISABLE = 'Disabled'
    ENABLE = 'Enabled'
    USER_NAME_NOT_MATCH = 'Contains at least 5 characters|Please enter enough characters|Username is a string of 5 to 16 letters|Username only support the first character must be a letter'
    USER_NAME_EXITS = 'Username does not conform to specifications or already exists'
    ERROR_PSW = 'Wrong Password'
    DEL_USER_SUCCESS = 'Delete user success'
    SET_PSW_SUCCESS = 'Setting Successfully|Password Set Successfully'
    LOC_USER_CONF = ['Console Redirection', Msg.SERVER_CONFIG, 'BMC User Configuration']

    # IPMITOOL 启动
    OS_MSG = 'Kylin|Tencent|CentOS|UOS|Windows|kos'
    UEFI_PXE_MSG = 'Checking Media Presence...|Checking media present...'
    LEGACY_PXE_MSG = 'PXE initialising devices...|PXEinitialisingdevices...'
    BOTH_PXE_MSG = 'PXE initialising devices...|Checking Media Presence...|PXEinitialisingdevices...|Checking media present...'
    UEFI_USB_MSG = 'UEFI Interactive Shell'
    LEGACY_USB_MSG = 'Start booting from USB device|StartbootingfromUSBdevice'
    BOTH_USB_MSG = 'Start booting from USB device|UEFI Interactive Shell|StartbootingfromUSBdevice'

    OPEN_LAN = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'}]
    OPEN_PXE = [{'PXE Option Rom': 'Enabled'}]
    BOOT_MODE_UEFI = [{'Boot Mode': 'UEFI'}]
    BOOT_MODE_LEGACY = [{'Boot Mode': 'Legacy'}]
    OPEN_SHELL = [{'Internal SHELL': 'Enabled'}]

    # 板载SOL
    CLOSE_SOL = ['Console Redirection', Msg.SERVER_CONFIG, {'SOL for Baseboard Mgmt': 'Disabled'}]
    OPEN_SOL = ['Console Redirection', Msg.SERVER_CONFIG, {'SOL for Baseboard Mgmt': 'Enabled'}]

    # BMC系统日志
    LOC_SYS_LOG = ['Console Redirection', Msg.SERVER_CONFIG, 'BMC system log|BMC system event log']

    # FRU
    LOC_FRU = ['Console Redirection', Msg.SERVER_CONFIG, 'FRU Information']
    CLEAR_FRU = ['Console Redirection', Msg.SERVER_CONFIG, 'Clear System Event Log']

    # SOL Terminal
    FRAME_MSG = ['Are you sure Exit','General Help','Are you sure load defaults','Save configuration changes and exit|Save Configuration Changes and Exit now']
    TER_VT100_PLUS = ['Console Redirection','Console Redirection',{'Terminal Type':'VT100+'}]
    TER_VT100 = ['Console Redirection','Console Redirection',{'Terminal Type':'VT100'}]

class Pci:
    OPEN_LAN = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'}]

    # PCIE最大负载
    LOC_PCIE = ['Console Redirection', 'Misc Configuration']
    PCIE_MAX_NAME = Msg.PCI_MAX
    PCIE_MAX_VALUE = ['128B', '256B', '512B', 'Auto']

    # PCIE活动状态电源管理
    OPEN_ASPM = ['Console Redirection', 'Misc Configuration', {Msg.PCI_ASPM: 'L1|Enabled'}]
    CLOSE_ASPM = ['Console Redirection', 'Misc Configuration', {Msg.PCI_ASPM: 'Disabled'}]

    # 4GB以上空间解码
    OPEN_ABOVE = ['Console Redirection', 'Misc Configuration', {'Above 4G Decoding': 'Enabled'}]
    CLOSE_ABOVE = ['Console Redirection', 'Misc Configuration', {'Above 4G Decoding': 'Disabled'}]


class _Pxe:
    IPV4_MSG = 'Start PXE over IPv4'
    IPV6_MSG = 'Start PXE over IPv6'

    # PXE Option Rom
    CLOSE_PXE = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                 'User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]

    # PXE 启动
    SET_IPV4 = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'}, {'Net Boot IP Version': 'IPv4'}]
    SET_IPV6 = ['User Wait Time', {'Net Boot IP Version': 'IPv6'}]
    SET_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}, {'PXE Option Rom': 'Enabled'}]
    SET_UEFI = ['User Wait Time', {'Boot Mode': 'UEFI'}]

    # PXE 重试
    CLOSE_PXE_RETRY = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                       {'PXE Boot Options Retry': 'Disabled'},
                       {'Net Boot IP Version': 'IPv4'}]
    OPEN_PXE_RETRY = ['User Wait Time', {'PXE Boot Options Retry': 'Enabled'}]

    # LegacyPXE 重试
    CLOSE_PXE_RETRY_LEGACY = ['User Wait Time', {'Boot Mode': 'Legacy'}, {'PXE Option Rom': 'Enabled'},
                              {'PXE Boot Options Retry': 'Disabled'}]
    OPEN_PXE_RETRY_LEGACY = ['User Wait Time', {'PXE Boot Options Retry': 'Enabled'}]

    # PXE IP 版本
    SET_IPV4_6 = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                  'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                  {'Net Boot IP Version': 'IPv4 and IPv6'}]
    SET_ONBOARD = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                   {'Select a Network to PXE': SutCfgMde.Pxe.PXE_NET_ONBOARD}, {'Net Boot IP Version': 'IPv4'}]
    SET_ADDON = ['User Wait Time', {'Select a Network to PXE': SutCfgMde.Pxe.PXE_NET_ADDON}]
    SET_NONE = ['User Wait Time', {'Select a Network to PXE': 'NULL'}]

    # PXE Boot Priority
    SET_ONBOARD_PRI = ['User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                       {'Select a Network to PXE': 'NULL'}, {'Net Boot IP Version': 'IPv4'},
                       {'PXE Boot Priority': 'Onboard First'}]
    SET_ADDON_PRI = ['User Wait Time', {'PXE Boot Priority': 'Addon First'}]
    SET_ADDON_NONE = ['User Wait Time', {'PXE Boot Priority': 'Disabled'}]


class Pxe(SutCfgMde.Pxe,_Pxe):
    pass


class _Sup:
    # Interface_information
    NECESSARY_MSG = ['BIOS Vendor', 'BIOS Core Version', 'Mother Board Info', 'CPU Info', 'Memory Info',
                     'System Date and Time',
                     'PCIE Info', 'USB Configuration', 'Console Redirection', 'Set Administrator Password',
                     'Set User Password',
                     'HDD Password', 'User Wait Time',
                     'PXE Option Rom', 'Boot Order', 'Save and Exit', 'Load Setup Defaults', 'BIOS Update Parameters',
                     'Shutdown System', 'Reboot System']

    # Onboard Lan Configuration
    CLOSE_LAN = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Disabled'},
                 'User Wait Time', {'Boot Mode': 'UEFI'}, {'PXE Option Rom': 'Enabled'},
                 {'Net Boot IP Version': 'IPv4'}]
    LOC_PCI_INFO = [Msg.PAGE_MAIN, 'PCIE Info', 'PCI Device Info']
    OPEN_LAN = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'}]

    # 网络唤醒
    CLOSE_WAKE_ONLINE = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                         {'Wake On Lan': 'Disabled'}]
    OPEN_WAKE_ONLINE = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                        {'Wake On Lan': 'Enabled'}]

    # USB 存储设备支持
    CLOSE_USB_STORAGE = ['User Wait Time', {'Boot Mode': 'UEFI'}, 'Console Redirection', 'USB Configuration',
                         {'USB Mass Storage Support': 'Disabled'}, 'USB Port Configuration',
                         {Msg.REAR_USB: 'Enabled'}, {Msg.FRONT_USB: 'Enabled'}]
    OPEN_USB_STORAGE = ['Console Redirection', 'USB Configuration', {'USB Mass Storage Support': 'Enabled'}]

    # USB 端口配置
    OPEN_USB_PORT_BOTH = ['Console Redirection', 'USB Configuration', {'USB Mass Storage Support': 'Enabled'},
                          'USB Port Configuration', {Msg.REAR_USB: 'Enabled'},
                          {Msg.FRONT_USB: 'Enabled'}]
    LOC_USB_INFO = ['Console Redirection', 'USB Configuration']
    OPEN_USB_PORT_FRONT = [{Msg.REAR_USB: 'Disabled'}, {Msg.FRONT_USB: 'Enabled'}]
    OPEN_USB_PORT_BEHIND = [{Msg.REAR_USB: 'Enabled'}, {Msg.FRONT_USB: 'Disabled'}]
    CLOSE_USB_PORT_BOTH = [{Msg.REAR_USB: 'Disabled'}, {Msg.FRONT_USB: 'Disabled'}]
    OPEN_USB_PORT_ALL = [{Msg.REAR_USB: 'Enabled'}, {Msg.FRONT_USB: 'Enabled'}]
    CLOSE_USB_PORT_FRONT = [{Msg.FRONT_USB: 'Disabled'}]
    OPEN_USB_PORT_FRONT_ONLY = [{Msg.FRONT_USB: 'Enabled'}]
    CLOSE_USB_PORT_BEHIND = [{Msg.REAR_USB: 'Disabled'}]
    OPEN_USB_PORT_BEHIND_ONLY = [{Msg.REAR_USB: 'Enabled'}]

    # HDD Bind
    HDD_BIND1 = ['Console Redirection', 'HDD Bind', {'HDD Bind': SutCfgMde.Sup.HDD_BIND_NAME_1}]
    HDD_BIND2 = ['Console Redirection', 'HDD Bind', {'HDD Bind': SutCfgMde.Sup.HDD_BIND_NAME_2}]
    HDD_BIND3 = ['Console Redirection', 'HDD Bind', {'HDD Bind': 'Unbind'}]

    # Secure Boot
    LOC_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot']
    OPEN_SECURE_BOOT = [{'Secure Boot': 'Enabled'}, 'User Wait Time', {'Boot Mode': 'UEFI'},
                        {'Internal SHELL': 'Enabled'}]
    CLOSE_SECURE_BOOT = ['Set Administrator Password', 'Secure Boot', 'Reset to Factory Mode']
    SECURE_MSG = 'Command Error Status: Security Violation'
    BACKUP_CMD = 'ByoShellFlash.efi bfu -bu backup.bin'

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
    CLOSE_IOMMU = ['Console Redirection', Msg.VIRTUALIZATION, {'IOMMU': 'Disabled'}]
    OPEN_IOMMU = ['Console Redirection', Msg.VIRTUALIZATION, {'IOMMU': 'Enabled'}]

    # SVM
    CLOSE_SVM = ['Console Redirection', Msg.VIRTUALIZATION, {'SVM': 'Disabled'}]
    OPEN_SVM = ['Console Redirection', Msg.VIRTUALIZATION, {'SVM': 'Enabled'}]

    # SR-IOV
    CLOSE_SR = ['Console Redirection', Msg.VIRTUALIZATION, {'SR-IOV Support': 'Disabled'}]
    OPEN_SR = ['Console Redirection', Msg.VIRTUALIZATION, {'SR-IOV Support': 'Enabled'}]

    # 内存频率
    LOC_HYGON = ['Console Redirection', 'Hygon CBS', {'Allow setting memory frequency': 'Enabled'}]
    MEMORY_SPEED_NAME = 'Memory Clock Speed'
    LOC_MEM = [Msg.PAGE_MAIN, 'Memory Info']

    # Load Setup Defaults
    CLOSE_VIRTU = ['Console Redirection', Msg.VIRTUALIZATION, {'IOMMU': 'Disabled'}, {'SVM': 'Disabled'},
                   {'SR-IOV Support': 'Disabled'}]
    OPEN_VIRTU = [{'IOMMU': 'Enabled'}, {'SVM': 'Enabled'}, {'SR-IOV Support': 'Enabled'}]
    LOC_VIRTU = ['Console Redirection', Msg.VIRTUALIZATION]
    LOC_SAV_EXI = [Msg.PAGE_EXIT, 'Save and Exit']
    LOC_NO_SAV_EXI = [Msg.PAGE_EXIT, 'Discard Changes and Exit']

    VIRTUALIZATION_DEFAULT = re.findall('<([^<]+)>(?:IOMMU|SVM|SR-IOVSupport)',
                                        ''.join(SutCfgMde.Upd.DEFAULT_OPTION_VALUE))

    # 全刷后检查默认值
    SET_UPDATE_ALL = [Msg.PAGE_EXIT, {'BIOS Update Parameters': 'Full Update'}]
    UPDATE_BIOS_PATH = [Msg.PAGE_EXIT, Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE),
                        Env.LATEST_BIOS_FILE]
    CHANGE_OPTION_VALUE = ['Console Redirection', Msg.VIRTUALIZATION, {'IOMMU': 'Disabled'},
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
    POST_MSG = "Press F12 to clear this computer's TPM|Press F12 to clear the TPM"
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
    CLOSE_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Disabled'}]
    OPEN_PXE_OPTION = ['User Wait Time', {'PXE Option Rom': 'Enabled'}]
    CLOSE_PXE_STACK = ['User Wait Time', {'UEFI Network Stack': 'Disabled'}]
    LOC_UEFI_HII = ['Console Redirection', 'UEFI HII Configuration']

    # Option Rom
    OPEN_OPTION_ROM = ['Console Redirection', Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                       'User Wait Time', {'Boot Mode': 'Legacy'}, {'OPTION ROM Message': 'Enabled'}]
    CLOSE_OPTION_ROM = ['User Wait Time', {'OPTION ROM Message': 'Disabled'}]
    ONBOARD_MSG = 'WangXun\(R\) *PXE'

    # TPCM
    OPEN_TPCM = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'}, {'Hygon TPCM': 'Enabled'}]
    CLOSE_TPCM = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Debug'},
                  {'Hygon TPCM': 'Disabled'}]
    CLOSE_DEBUG = ['Console Redirection', 'Misc Configuration', {'Debug Print Level': 'Disabled'}]
    TPCM_MSG = 'TpcmVerifyRaw:Success'


class Sup(SutCfgMde.Sup,_Sup):
    pass


class _Upd:
    # 获取BIOS选项值
    REMOVE_OPTIONS = ['BMC system log', 'UEFI HII Configuration', 'BMC system event log',
                      'Key Management', 'System Date and Time']  # 读取选项时不进入的菜单

    # 修改BIOS选项
    CHANGE_PART1 = [Msg.PAGE_MAIN, 'PCIE Info', {'MCIO0_CPU1 as SATA': 'Enabled '}, {'MCIO2_CPU1 as SATA': 'Enabled'},
                    'Console Redirection',
                    Msg.LAN_CONFIG, {'Onboard Ethernet Controller': 'Enabled'},
                    {'Wake On Lan': 'Disabled'},
                    'Console Redirection', 'Video Configuration', {'Primary Graphics Adapter': 'IGD'},
                    'Console Redirection', Msg.VIRTUALIZATION, {'IOMMU': 'Enabled'}, {'SVM': 'Disabled'},
                    {'SR-IOV Support': 'Disabled'},
                    'Console Redirection', 'Misc Configuration', {'Above 4G Decoding': 'Disabled'},
                    {'MMIO High Limit': '4TB'}, {'Hide Boot Logo': 'Enabled'}, {Msg.PCI_MAX: '512B'},
                    {Msg.PCI_ASPM: 'L1'}, {'AES': 'Disabled'}, {'Hyper Threading Technology': 'Disabled'},
                    {'ENERGY_PERF_BIAS_CFG mode': 'User Defined'}, {'CPU P-State Control': 'P0+P1'},
                    {'CPU C-State Control': 'Enabled'}, {'Set CPU Speed': '1600 MHz'}, {'FCH SSC': 'Enabled'}]
    CHANGE_PART2 = ['Console Redirection', Msg.SERVER_CONFIG, {'FRB2 Watchdog Timer': 'Enabled'},
                    {'FRB2 Watchdog Timer Policy': 'Power Off'},
                    {'FRB2 Watchdog Timer Timeout': '30minutes|30 minutes'}, {'OS Boot Watchdog Timer': 'Enabled'},
                    {'SOL for Baseboard Mgmt': 'Enabled'}, {Msg.AC: 'Stay Off'},
                    'Console Redirection', Msg.SERVER_CONFIG, 'BMC Lan Configuration', {'NCSI': 'Disabled'},
                    'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                    {'MCA Error Threshold Count': '100'}, {'Leaky Bucket Time': 10}, {'Leaky Bucket Count': 20},
                    {'Pcie CE Threshold': 5}, {'CPU CE Threshold': 200},
                    'Console Redirection', 'Hygon CBS', {'Allow setting memory frequency': 'Enabled'},
                    {'Memory Clock Speed': '1333MHz'}, {'Downcore control': 'SIX (3 + 3)'},
                    {'Core Performance Boost': 'Disabled'}, {'SMEE Control': 'Disabled'},
                    {'Chipselect Interleaving': 'Disabled'}, {'Channel interleaving': 'Enabled'}, {'NUMA': 'None'},
                    {'Memory interleaving size': '512 Bytes'}, {'Redirect scrubber control': 'Enabled'},
                    {'Determinism Slider': 'Power'}, {'RDSEED and RDRAND Control': 'Auto'},
                    {'DRAM scrub time': '48 hours|48hours'},
                    {'cTDP Control': 'Manual'}, {'Efficiency Optimized Mode': 'Auto'}, {'Bank Interleaving': 'Auto'},
                    'Console Redirection', 'Hygon CBS', 'Cache Prefetcher settings',
                    {'L1 Stream HW Prefetcher': 'Enable'}, {'L2 Stream HW Prefetcher': 'Enable'},
                    'Console Redirection', 'Hygon CBS', 'NBIO Common Options', {'NBIO RAS Control': 'Disabled'},
                    {'ACS Enable': 'Disabled'},
                    'Console Redirection', {'Memory error behavior': 'Shutdown System'}]
    CHANGE_PART3_1 = ['Set Administrator Password', 'Password Lock Time']
    CHANGE_PART3_2 = ['User Wait Time', {'User Wait Time': 10},
                      {'Bootup NumLock State': 'Off'}, {'Internal SHELL': 'Enabled'}, {'PXE Option Rom': 'Disabled'},
                      {'PXE Boot Options Retry': 'Enabled'},
                      {'Net Boot IP Version': 'IPv6'}, {'PXE Boot Priority': 'Onboard First'}]
    SET_TIME_ALWAYS = [{'Password Valid Days': 'Indefinite'}]

    PASSWORD_MSG = 'Please input (?:admin )*password'
    START_UPDATE_MSG = 'Update BIOS|Reading Bios|Reading File'

    WRONG_PSW_MSG = '(?:Password|password) is invalid|Check password failed|password is invalid'

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
    SHELL_MSG_NOR = "End.....................Successed!|BIOS has been updated"
    SHELL_MSG_ALL = "Update ALL..................Successed!|BIOS has been updated"

    LINUX_MSG_NOR = "End.....................Successed!|Flash update successfully"
    LINUX_MSG_ALL = "Update ALL..................Successed!|Flash update successfully"

    WINDOWS_FLASH_TOOL = Env.WINDOWS_FLASH_CMD
    WINDOWS_MSG_NOR = "End.....................Successed!"
    WINDOWS_MSG_ALL = "Update ALL..................Successed!"

    SETUP_OTHERS = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.OTHERS_BIOS_FILE]
    SETUP_UNSIGNED = [Msg.BIOS_UPDATE, Env.USB_VOLUME, '<{}>'.format(Env.BIOS_FILE), Env.UNSIGNED_BIOS_FILE]

    UPDATE_OTHERS_MSG_SETUP = 'File Sign Match Fail|File Not Match'
    UPDATE_UNSIGNED_MSG_SETUP = 'File Sign Match Fail|BIOS Verify Sign Fail'
    UPDATE_OTHERS_MSG_LINUX = 'please check BIOS ID information|BIOSID is not matched'
    UPDATE_UNSIGNED_MSG_LINUX = 'Sign Verify.*failed|Sign Verify.*Failed'
    UPDATE_OTHERS_MSG_SHELL = 'BiosCheck Fail|BIOSID is not matched'
    UPDATE_UNSIGNED_MSG_SHELL = 'BiosCheck Fail|Sign Verify.*Failed'


class Upd(SutCfgMde.Upd,_Upd):
    pass


class Rfs:
    CURRECT_VALUE = 'Inspur7500\\Tools\\currectvalue.json'
    CHANGE_OPTIONS_FILE = 'Inspur7500\\Tools\\changevalue.json'
    REGISTRY_FILE = 'Inspur7500\\Tools\\registry.json'
    DEPENDENCE_FILE = 'Inspur7500\\Tools\\dependence.json'
    REGISTRY_FILE_PATH = 'Inspur7500\\Tools\\'
    BIOS_PATH_LATEST = 'Inspur7500\\Tools\\BIOS\\latest.bin'
    BIOS_PATH_PREVIOUS = 'Inspur7500\\Tools\\BIOS\\previous.bin'


class Tool:
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


class _Ras:
    CLOSE_PFEH = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Disabled'}]
    SET_MEM_THRESHOLD_10 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 0}]
    SET_MEM_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                           {'MCA Error Threshold Count': '1'}]
    SET_MEM_THRESHOLD_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                           {'MCA Error Threshold Count': '0'}]
    SET_MEM_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                             {'MCA Error Threshold Count': '4095'}, {'Leaky Bucket Time': 0}]
    OPEN_PFEH = ['Console Redirection', Msg.SERVER_CONFIG, {'OS Boot Watchdog Timer': 'Disabled'},
                 'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'}]
    SET_LEAKY_BUCKET_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                          {'MCA Error Threshold Count': '10'}, {'Leaky Bucket Time': 0}]
    SET_PCIE_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'(?:PCIe|Pcie|PCIE) CE Threshold': 1}]
    SET_PCIE_THRESHOLD_2 = ['Console Redirection', Msg.VIRTUALIZATION, {'IOMMU': 'Enabled'},
                            'Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'(?:PCIe|Pcie|PCIE) CE Threshold': 2}]
    SET_PCIE_THRESHOLD_0 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'(?:PCIe|Pcie|PCIE) CE Threshold': 0}]
    SET_CPU_THRESHOLD_1 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                           {'CPU CE Threshold': 1}]

    SET_CPU_THRESHOLD_10 = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                            {'CPU CE Threshold': 10}]
    SET_CPU_THRESHOLD_MAX = ['Console Redirection', 'Error Management', {'Platform First Error Handling': 'Enabled'},
                             {'CPU CE Threshold': 4095}]


class Ras(SutCfgMde.Ras,_Ras):
    pass
