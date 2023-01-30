import os
import datetime
from D2000.Config.PlatConfig import Key


class Env:
    # Report Setting
    PROJECT_NAME = "D2000"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "D2000\\Report\\template"

    TESTCASE_CSV = "D2000\\AllTest.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\D2000\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com3"

    # BMC Configuration
    BMC_IP = '192.168.6.63'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.174'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    OS_IP_LEGACY = '192.168.6.174'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    IPMITOOL = "ByoTool\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER,
                                                                                               BMC_PASSWORD)
    SMBIOS = "D2000\\Tools\\smbiosd2000\\"
    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sda4"  # LinuxU盘盘符
    LINUX_USB_MOUNT = "/mnt/"
    LINUX_USB_NAME = 'Cruzer Force'  # Linux下'fdisk -l'中U盘名称
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs8:"
    USB_VOLUME = "USB:SanDisk \(P4\)"  # SetUp刷新BIOSU盘名

    BIOS_FILE = 'D2000'  # U盘存放BIOS文件和刷新工具的文件夹名
    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)

    MACHINE_TYPE = 'Desktop'  # 测试机器的类型,服务器(支持Ipmi):'Server',桌面机:'Desktop'
    OEM_SUPPORT = False  # 是否支持通过OEM命令修改SetUp选项值


class Msg:
    SETUP_KEY = Key.F2  # POST界面进入SetUp按键
    BOOTMENU_KEY = Key.F7  # POST界面进入启动菜单按键

    POST_MESSAGE = 'Press \[F2\] to enter'
    # POST_MESSAGE ='Del to enter SETUP|Press F11 to enter Boot Menu|Press F12 to enter PXE boot'
    PAGE_MAIN = "CPU Info"
    PAGE_DEVICE = 'Onboard LAN Configuration'
    PAGE_ADVANCED = 'PEU0\[0:7\] slot enable'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'Bootup NumLock State'
    PAGE_EXIT = 'Save and Exit'

    HDD_BOOT_NAME = 'Hard Drive'
    PXE_BOOT_NAME = 'Network Adapter'
    ODD_BOOT_NAME = 'CD/DVD ROM Drive'
    USB_BOOT_NAME = 'USB Flash Drive/USB Hard Disk'
    USBODD_BOOT_NAME = 'USB CD/DVD ROM Drive'
    OTHER_BOOT_NAME = 'Others'

    PAGE_ALL = [PAGE_MAIN, PAGE_DEVICE, PAGE_ADVANCED, PAGE_SECURITY, PAGE_BOOT, PAGE_EXIT]
    SETUP_MESSAGE = 'Select Language'  # 进入SetUp确认信息
    ENTER_BOOTMENU = "Please select boot device"  # 进入启动菜单确认信息
    SHELL_MSG = 'UEFI Interactive Shell'
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: SanDisk'
    SHELL = "UEFI Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI PXEv4 \(MAC:78E58C8C3D8A\)"
    HTTP_PORT1 = "UEFI HTTPv4 \(MAC:78E58C8C3D8A\)"
    PXE_PORT2 = "UEFI PXEv4 \(MAC:1C4FBF586746\)"
    HTTP_PORT2 = "UEFI HTTPv4 \(MAC:1C4FBF586746\)"
    OS_MSG = 'Kylin|Tencent|CentOS|UOS'
    LEGACY_OS = "SATA3-1: WDC WD5000LPCX-22VHAT0|UEFI SATA3-1: WDC WD5000LPCX-22VHAT0"  # Legacy系统盘在Legacy,UEFI模式下启动名
    LEGACY_OS_MSG = 'Kylin'
    UEFI_OS = 'Kylin Linux Advanced Server\(SATA3-1: SAMSUNG MZ7LH480HAHQ-00005\)|SATA3-1: SAMSUNG MZ7LH480HAHQ-00005'  # UEFI系统盘在Legacy,UEFI模式下启动名
    UEFI_OS_MSG = 'Kylin'
    LINUX_OS = 'UOS\(UEFI NVME\(PCIF-0-0\): Samsung SSD 980 250G...'  # UEFI系统盘在UEFI模式启动名，Legacy系统盘在Legacy模式下启动名
    # LINUX_OS = 'UOS\(UEFI SATA3-2: SAMSUNG MZ7L3480HCHQ-00B7C\)'
    LINUX_OS_MSG = 'UOS'
    WINDOWS_OS = 'UEFI SATA 2: WDC WD10EZEX-08WN4A0\(Windows Boot Manager\)'
    WINDOWS_OS_MSG = ''


class Boot:
    LOC_CPU = ['CPU Info']
    LOC_MEM = ['CPU Info', 'Memory Info']
    LOC_USB = ['Onboard LAN Configuration', 'USB Port Configuration']
    LOC_HDD = ['Bootup NumLock State', 'Change Boot order', 'Hard Drive']
    LOC_SATA = ['Onboard LAN Configuration', 'SATA Device Info']
    LOC_NVME = ['Onboard LAN Configuration', 'NVME Device Info']
    BOOT_NAME_LIST_UEFI = [Msg.HDD_BOOT_NAME, Msg.PXE_BOOT_NAME, Msg.ODD_BOOT_NAME,
                           Msg.USB_BOOT_NAME, Msg.USBODD_BOOT_NAME, Msg.OTHER_BOOT_NAME]
    OPEN_LAN = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'},
                'Bootup NumLock State', {'Network Boot': 'Enabled'}]
    LOC_BOOT_ORDER = ['Bootup NumLock State', 'Change Boot order']
    LOC_BOOT_MANAGER = ['Bootup NumLock State', 'Boot Manager']


class Sup:
    CLOSE_ONBOARD_LAN = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Disabled'},
                         'Bootup NumLock State', {'Network Boot': 'Enabled'}]
    OPEN_ONBOARD_LAN = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'}]

    # SR-IOV
    REMOVE_ETHNAME = ['enaphyt4i0', 'enaphyt4i1', 'lo']
    CLOSE_SR = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'}, 'PEU0\[0:7\] slot enable',
                {'SR-IOV Support': 'Disabled'}]
    OPEN_SR = ['PEU0\[0:7\] slot enable', {'SR-IOV Support': 'Enabled'}]

    # 内存频率
    MEM_SPEED_NAME = 'Set Memory Frequency'
    LOC_MEM_SPEED = ['CPU Info', 'Memory Info']

    # 系统日期和时间
    LOC_DATE_TIME = ['CPU Info', 'System Date and Time']

    # 用户等待时间
    OPEN_SHELL = ['Bootup NumLock State', {'Internal SHELL': 'Enabled'}]

    LOC_BOOT_ORDER_USB = ['Bootup NumLock State', 'Change Boot order', 'Others']
    SET_USER_TIME_10 = ['Bootup NumLock State', {'User Wait Time': 10}]
    SET_USER_TIME_MAX = ['Bootup NumLock State', {'User Wait Time': 65535}]
    SET_USER_TIME_MIN = ['Bootup NumLock State', {'User Wait Time': 0}]

    # 网络启动重试
    OPEN_PXE_RETRY = ['Bootup NumLock State', {'Network Boot': 'Enabled'}, {'PXE Boot Options Retry': 'Enabled'}]
    CLOSE_PXE_RETRY = ['Bootup NumLock State', {'PXE Boot Options Retry': 'Disabled'}]
    PXE_MSG = 'UEFI PXEv4 \(MAC:78E58C8C3D8A\)'
    PXE_RETRY_MSG = 'UEFI HTTPv4 \(MAC:1C4FBF586746\)'

    # 网络引导
    CLOSE_NET = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'}, 'Bootup NumLock State',
                 {'Network Boot': 'Disabled'}]
    OPEN_NET = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'}, 'Bootup NumLock State',
                {'Network Boot': 'Enabled'}]

    # USB端口测试
    # Hub插在的USB端口名称(用于TC108,所有设备都接在Hub上)
    USB_PORT_OPTION_NAME = 'USB Port1 Configuration\(USB2.0 Up\)'

    # 所有的USB设备,按照格式自行添加,连接USB设备类型与数量一致(用于TC105,TC106)
    PORT_DEVICE_DICT = {0: 'Mass Storage',
                        1: 'HID',
                        2: 'HID'
                        }
    LOC_BOOT_MANAGER = ['Bootup NumLock State', 'Boot Manager']
    USB_PORT_GLOBAL_VALUES = ['AUTO', 'HID', 'HID & Mass Storage', 'HID & Mass Storage Read Only', 'HID & Others',
                              'HID & Others & Mass Storage Read Only']
    USB_PORT_VALUES = ['AUTO', 'HID', 'HID & Mass Storage', 'HID & Mass Storage Read Only', 'HID & Others',
                       'HID & Others & Mass Storage Read Only', 'Mass Storage', 'Mass Storage Read Only',
                       'Others & Mass Storage', 'Others & Mass Storage Read Only', 'Others', 'None']
    SET_GLOBAL_USB_PORT = ['Onboard LAN Configuration', 'USB Port Configuration',
                           {'USB Port Global Configuration': 'AUTO'}]
    LOC_USB_PORT = ['Onboard LAN Configuration', 'USB Port Configuration']
    USB_PORT_GLOBAL_OPTION_NAME = 'USB Port Global Configuration'
    ALL_USB_PORT_OPTION_NAME = ['USB Port1 Configuration\(USB2.0 Up\)', 'USB Port2 Configuration\(USB2.0 Down\)',
                                'USB Port3 Configuration\(USB3.0 Up\)', 'USB Port4 Configuration\(USB3.0 Down\)']

    # 板载SATA槽开关
    LOC_SATA_INFO = ['Onboard LAN Configuration', 'SATA Device Info']
    OPEN_ONBOARD_SATA = ['PEU0\[0:7\] slot enable', {'Onboard SATA slot enable': 'Enabled'}]
    CLOSE_ONBOARD_SATA = ['PEU0\[0:7\] slot enable', {'Onboard SATA slot enable': 'Disabled'}]

    # NVME槽开关
    LOC_NVME_INFO = ['Onboard LAN Configuration', 'NVME Device Info']
    OPEN_NVME = ['PEU0\[0:7\] slot enable', {'PEU0\[8:11\]\(NVME\) slot enable': 'Enabled'}]
    CLOSE_NVME = ['PEU0\[0:7\] slot enable', {'PEU0\[8:11\]\(NVME\) slot enable': 'Disabled'}]

    # PEU0[0:7]
    LOC_PCIE_INFO = ['Onboard LAN Configuration', 'PCIE Device Info']
    OPEN_PUE0_07 = ['PEU0\[0:7\] slot enable', {'PEU0\[0:7\] slot enable': 'Enabled'}]
    CLOSE_PUE0_07 = ['PEU0\[0:7\] slot enable', {'PEU0\[0:7\] slot enable': 'Disabled'}]

    # 板载USB槽开关
    OPEN_USB_SLOT = ['PEU0\[0:7\] slot enable', {'Onboard USB slot enable': 'Enabled'}]
    CLOSE_USB_SLOT = ['PEU0\[0:7\] slot enable', {'Onboard USB slot enable': 'Disabled'}]

    # PEU1[0:7]
    OPEN_PUE1_07 = ['PEU0\[0:7\] slot enable', {'PEU1\[0:7\] slot enable': 'Enabled'}]
    CLOSE_PUE1_07 = ['PEU0\[0:7\] slot enable', {'PEU1\[0:7\] slot enable': 'Disabled'}]

    # PEU1[8:15]
    OPEN_PUE1_815 = ['PEU0\[0:7\] slot enable', {'PEU1\[8:15\] slot enable': 'Enabled'}]
    CLOSE_PUE1_815 = ['PEU0\[0:7\] slot enable', {'PEU1\[8:15\] slot enable': 'Disabled'}]

    # 硬盘绑定
    BIND_MSG = 'Hdd has been changed'
    LOC_HDD_BIND = ['Set Administrator Password', 'HDD Bind']
    SET_HDD_UNBIND = ['Set Administrator Password', 'HDD Bind', {'HDD Bind': 'Unbind'}]

    # Load Default
    LOAD_DEFAULT = ['Save and Exit', 'Load Setup Defaults']

    # Boot Watchdog
    SET_WATCHDOG_1 = ['PEU0\[0:7\] slot enable', {'Boot Watchdog': 'Enabled'}, {'Watchdog Timer Timeout': '1 minute'}]
    SET_USER_TIME_65 = ['Bootup NumLock State', {'User Wait Time': 65}]
    SET_WATCHDOG_3 = ['PEU0\[0:7\] slot enable', {'Boot Watchdog': 'Enabled'}, {'Watchdog Timer Timeout': '3 minute'}]
    SET_USER_TIME_185 = ['Bootup NumLock State', {'User Wait Time': 185}]
    SET_WATCHDOG_5 = ['PEU0\[0:7\] slot enable', {'Boot Watchdog': 'Enabled'}, {'Watchdog Timer Timeout': '5 minute'}]
    SET_USER_TIME_305 = ['Bootup NumLock State', {'User Wait Time': 305}]

    # 保存修改
    CHANGE_OPTIONS = ['CPU Info', 'Memory Info', {'Set Memory Frequency': '2400MHz'}, 'Onboard LAN Configuration',
                      'SATA Device Info', {'S.M.A.R.T Check': 'Disabled'}, 'PEU0\[0:7\] slot enable',
                      {'PBF Debug Level': 'Second Level'},
                      {'Boot Watchdog': 'Enabled'}, {'ASPM Support': 'L1'}, 'Bootup NumLock State',
                      {'Bootup NumLock State': 'Off'}, {'User Wait Time': 15}, {'Network Boot': 'Enabled'},
                      {'PXE Boot Options Retry': 'Enabled'}]
    CHANGE_OPTION_NAME = ['<Enabled>OnboardLANConfiguration', '<Enabled>PEU0[0:7]slotenable',
                          '<Enabled>PEU0[8:11](NVME)slotenable', '<Enabled>OnboardSATAslotenable',
                          '<Enabled>PEU1[0:7]slotenable', '<Enabled>PEU1[8:15]slotenable',
                          '<Enabled>OnboardUSBslotenable', '<Enabled>ConsoleRedirection', '<COM0>SerialPortSelect',
                          '<115200>SerialPortBaudrate', '<VT100+>TerminalType', '<SecondLevel>PBFDebugLevel',
                          '<Enabled>BootWatchdog', '<3minute>WatchdogTimerTimeout', '<L1>ASPMSupport',
                          '<128B>PCIEMaxPayloadSize', '<512B>PCIEMaxReadRequestSize', '<Enabled>SR-IOVSupport',
                          '<SHA-256Hash>SetPasswordEncryptionAlgorithm', '<Off>BootupNumLockState', '[15]UserWaitTime',
                          '<Enabled>NetworkBoot', '<Enabled>PXEBootOptionsRetry', '<Enabled>InternalSHELL',
                          '<English>SelectLanguage', '<2400MHz>SetMemoryFrequency', '<Disabled>S.M.A.R.TCheck',
                          '<AUTO>USBPortGlobalConfiguration', '<AUTO>USBPort1Configuration(USB2.0Up)',
                          '<AUTO>USBPort2Configuration(USB2.0Down)', '<AUTO>USBPort3Configuration(USB3.0Up)',
                          '<AUTO>USBPort4Configuration(USB3.0Down)', '<Enable>USBEnable', '<Enable>SATAEnable',
                          '<No>SataPort1Used', '<Disable>SataPort1Enable', '<Yes>SataPort2Used',
                          '<Enable>SataPort2Enable', '<No>SataPort3Used', '<Disable>SataPort3Enable',
                          '<Yes>SataPort4Used', '<Enable>SataPort4Enable', '<Enable>PcieX2Dn4Enable',
                          '<Enable>PcieX2Dn5Enable', '<Enable>PcieX1Dn6Enable', '<Enable>PcieX1Dn7Enable',
                          '<Enable>PcieX1Dn8Enable', '<Enable>PcieX1Dn9Enable']

    LOC_SAVE_CHANGE = ['Save and Exit']


class Pci:
    EXCEPT_BDF=['0e:02.7','0f:00.0']
    # PCIE ASPM
    ASPM_L0S = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'}, 'PEU0\[0:7\] slot enable',
                {'ASPM Support': 'L0s'}]
    ASPM_L1 = ['PEU0\[0:7\] slot enable', {'ASPM Support': 'L1'}]
    ASPM_L0S_L1 = ['PEU0\[0:7\] slot enable', {'ASPM Support': 'L0s&L1'}]
    ASPM_CLOSE = ['PEU0\[0:7\] slot enable', {'ASPM Support': 'Disabled'}]
    ALL_CHANGED_ASPM = [ASPM_L0S, ASPM_L1, ASPM_L0S_L1, ASPM_CLOSE]
    ASPM_MSG = ['L0s', 'L1', 'L0s L1', 'Disabled']

    # PCIE 最大读需求
    MAX_READ_256 = ['Onboard LAN Configuration', {'Onboard LAN Configuration': 'Enabled'}, 'PEU0\[0:7\] slot enable',
                    {'PCIE Max Read Request Size': '256B'}]
    MAX_READ_512 = ['PEU0\[0:7\] slot enable', {'PCIE Max Read Request Size': '512B'}]
    ALL_MAX_READ = [MAX_READ_256, MAX_READ_512]
    MAX_READ_MSG = ['256', '512']


class Upd:
    PASSWORDS = ['Admin@001', 'Users@001']
    UPDATE_BIOS_LATEST = ['Save and Exit', 'BIOS Update', Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', 'latest.bin']
    UPDATE_BIOS_PREVIOUS = ['Save and Exit', 'BIOS Update', Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', 'previous.bin']
    SETUP_MSG = 'Flash is updated successfully!'
    UPDATE_BIOS_UNSIGN = ['Save and Exit', 'BIOS Update', Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', 'unsigned.bin']
    UPDATE_BIOS_OTHERS = ['Save and Exit', 'BIOS Update', Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', 'others.bin']
    UPDATE_UNSIGN_MSG = 'File Not Match'
    UPDATE_OTHERS_MSG = 'File Not Match'


class Psw:
    SET_ADMIN_PSW = ['Set Administrator Password']  # SetUp下设置管理员密码的路径
    SET_USER_PSW = ['Set Administrator Password', 'Set User Password']  # SetUp下设置用户密码的路径
    SET_PSW_SUC_MSG = 'Password Setting Successfully'  # 密码设置成功的提示信息
    ADMIN_PSW_STATUS = 'Administrator Password *Installed'
    USER_PSW_STATUS = 'User Password *Installed'
    LOGIN_TYPE_ADMIN = 'User Login Type *Admin'
    LOGIN_TYPE_USER = 'User Login Type *User'
    ERROR_PSW_MSG = 'Incorrect password'
    INVALID_PSW_MSG = 'Invalid Password'
    LOCK_MSG = ''
    DEL_PSW_SUC_MSG = 'Password deleted succeeded'  # 密码删除成功的提示信息
    PSW_FIVE_TIMES = 'Password has been used by the latest 5 times'
    CHARACTERS_LENGTH_NOT_ENOUGH = 'Please enter enough characters'
    CHARACTERS_TYPE_NOT_ENOUGH = 'Passwords need to contain upper and lower case letters'
    PSW_NOT_SAME = 'Passwords are not the same'
    DATE_TIME = 'System Date and Time'
    SET_TIME_WEEK = [{'Set Password Valid Days': '7 Days'}]
    SET_TIME_MONTH = [{'Set Password Valid Days': '30 Days'}]
    SET_TIME_ALWAYS = [{'Set Password Valid Days': 'Forever'}]
    PSW_EXPIRE = 'Password expired'
    OPEN_POWER_ON_PSW = ['Set Administrator Password', {'Power-on Password': 'Enabled'}]
    CLOSE_POWER_ON_PSW = ['Set Administrator Password', {'Power-on Password': 'Disabled'}]
    POWER_ON_MSG = 'System Security: Power-On Password Required'
    SET_ENC_ALG = 'Set Password Encryption Algorithm'

    PAGE_ALL = ['CPU Info', 'SATA Device Info', 'Hardware Health Monitor', 'Set User Password',
                'Change Boot order', 'Save and Exit']  # 用户密码登录SetUp时各级菜单名
    GREY_OPTION = ['Select Language', 'Set Memory Frequency', 'Onboard LAN Configuration', 'S.M.A.R.T Check',
                   'USB Port Global Configuration', 'USB Port1 Configuration\(USB2.0 Up\)',
                   'USB Port2 Configuration\(USB2.0 Down\)', 'USB Port3 Configuration\(USB3.0 Up\)',
                   'USB Port4 Configuration\(USB3.0 Down\)', 'PEU0\[0:7\] slot enable',
                   'PEU0\[8:11\]\(NVME\) slot enable', 'Onboard SATA slot enable', 'PEU1\[0:7\] slot enable',
                   'PEU1\[8:15\] slot enable', 'Onboard USB slot enable', 'Console Redirection', 'Serial Port Select',
                   'Serial Port Baudrate', 'Terminal Type', 'PBF Debug Level', 'Boot Watchdog', 'ASPM Support',
                   'PCIE Max Payload Size', 'PCIE Max Read Request Size', 'SR-IOV Support',
                   'Set Administrator Password', 'Set Password Valid Days', 'Set Password Encryption Algorithm',
                   'TCM Configuration', 'TCG2 Configuration', 'HDD Password', 'Secure Boot', 'HDD Bind',
                   'Bootup NumLock State', 'User Wait Time', 'Network Boot', 'PXE Boot Options Retry', 'Internal SHELL',
                   'Load Setup Defaults', 'BIOS Update', 'X100 firmware Update', 'Shutdown System', 'Reboot System']
    GREY_OPTION_PATH = ['CPU Info', 'Memory Info', 'ESC', 'System Date and Time', 'SATA Device Info',
                        'SATA Device Info', 'ESC', 'USB Port Configuration', 'ESC']


class Tool:
    POST_PSW_MSG = 'System Security'  # 设置SetUp密码后,进入SetUp要求输入密码的提示信息

    # 修改的SMBIOS内容,可以在'{}'中间按照格式自定义添加
    SMBIOS_CHANGE = {'1 0 5': 'oem105',
                     '1 0 6': 'oem106',
                     }
    # 默认的SMBIOS内容,需要和修改的SMBIOS内容对应
    SMBIOS_DEFAULT = {'1 0 5': 'D2000',
                      '1 0 6': 'V1000'

                      }

    SET_ADMIN_PSW = ['Set Administrator Password']  # SetUp下设置管理员密码的路径
    SET_USER_PSW = ['Set Administrator Password', 'Set User Password']  # SetUp下设置用户密码的路径
    SET_PSW_SUC_MSG = 'Password Setting Successfully'  # 密码设置成功的提示信息
    DEL_PSW_SUC_MSG = 'Password deleted succeeded'  # 密码删除成功的提示信息

    # 读取SetUp值时进入选项的路径,依次进入各主页面下的各级子菜单，'ESC'代表按ESC键
    OPTION_PATH = ['CPU Info', 'Memory Info', 'ESC', 'Onboard LAN Configuration', 'SATA Device Info', 'ESC',
                   'USB Port Configuration', 'ESC', 'X100 Config', 'ESC']
    # 改变的SetUp选项
    CHANGE_OPTIONS = ['CPU Info', 'Memory Info', {'Set Memory Frequency': '2400MHz'}, 'Onboard LAN Configuration',
                      'SATA Device Info', {'S.M.A.R.T Check': 'Disabled'}, 'PEU0\[0:7\] slot enable',
                      {'PBF Debug Level': 'Second Level'},
                      {'Boot Watchdog': 'Enabled'}, {'ASPM Support': 'L1'}, 'Bootup NumLock State',
                      {'Bootup NumLock State': 'Off'}, {'User Wait Time': 15}, {'Network Boot': 'Enabled'},
                      {'PXE Boot Options Retry': 'Enabled'}]
    # BIOS默认值
    DEFAULT_OPTION_VALUE = ['<Enabled>OnboardLANConfiguration', '<Enabled>PEU0[0:7]slotenable',
                            '<Enabled>PEU0[8:11](NVME)slotenable', '<Enabled>OnboardSATAslotenable',
                            '<Enabled>PEU1[0:7]slotenable', '<Enabled>PEU1[8:15]slotenable',
                            '<Enabled>OnboardUSBslotenable', '<Enabled>ConsoleRedirection', '<COM0>SerialPortSelect',
                            '<115200>SerialPortBaudrate', '<VT100+>TerminalType', '<Fulllog>PBFDebugLevel',
                            '<Disabled>BootWatchdog', '<Disabled>ASPMSupport', '<128B>PCIEMaxPayloadSize',
                            '<512B>PCIEMaxReadRequestSize', '<Enabled>SR-IOVSupport',
                            '<SHA-256Hash>SetPasswordEncryptionAlgorithm', '<On>BootupNumLockState', '[5]UserWaitTime',
                            '<Disabled>NetworkBoot', '<Disabled>PXEBootOptionsRetry', '<Enabled>InternalSHELL',
                            '<English>SelectLanguage', '<2666MHz>SetMemoryFrequency', '<Enabled>S.M.A.R.TCheck',
                            '<AUTO>USBPortGlobalConfiguration', '<AUTO>USBPort1Configuration(USB2.0Up)',
                            '<AUTO>USBPort2Configuration(USB2.0Down)', '<AUTO>USBPort3Configuration(USB3.0Up)',
                            '<AUTO>USBPort4Configuration(USB3.0Down)', '<Enable>USBEnable', '<Enable>SATAEnable',
                            '<No>SataPort1Used', '<Disable>SataPort1Enable', '<Yes>SataPort2Used',
                            '<Enable>SataPort2Enable', '<No>SataPort3Used', '<Disable>SataPort3Enable',
                            '<Yes>SataPort4Used', '<Enable>SataPort4Enable', '<Enable>PcieX2Dn4Enable',
                            '<Enable>PcieX2Dn5Enable', '<Enable>PcieX1Dn6Enable', '<Enable>PcieX1Dn7Enable',
                            '<Enable>PcieX1Dn8Enable', '<Enable>PcieX1Dn9Enable']
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
    SHELL_INPUT_ERR_MSG = 'Usage'

    LINUX_TOOL_VERSION_CMD = './ByoFlash -v'
    LINUX_TOOL_VERSION_CONFIRM_MSG = 'ByoFlash version:'
    LINUX_TOOL_HELP_CMD = './ByoFlash -h'
    LINUX_TOOL_HELP_CONFIRM_MSG = 'Options:'
    LINUX_FLASH_CMD_LATEST_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -all'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin -all'
    LINUX_FLASH_CMD_LATEST = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_MSG_NOR = "BIOS has been updated|Update network region .* Success"
    LINUX_MSG_ALL = "BIOS has been updated|Update network region .* Success"
    LINUX_BACKUP_CMD = f'./ByoFlash -bu backup.bin'
    LINUX_BACKUP_SUC_MSG = 'Backup Bios .* Success'
    LINUX_UPDATE_BACKUP_CMD = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -bu backup.bin'
    LINUX_RESVNVM_CMD_LATEST = f'./ByoFlash -resvnvm {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_RESVNVM_CMD_PREVIOUS = f'./ByoFlash -resvnvm {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_RESVSMBIOS_CMD_LATEST = f'./ByoFlash -resvsmbios {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_RESVSMBIOS_CMD_PREVIOUS = f'./ByoFlash -resvsmbios {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_UPDATE_OA3_CMD = f'./ByoFlash -OA3 {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_LOCK_BIOS_UPDATE_CMD = f'./ByoFlash -lock'
    LINUX_UNLOCK_BIOS_UPDATE_CMD = f'./ByoFlash -unlock'
    LINUX_LOCK_BIOS_MSG = 'Lock Success'
    LINUX_UNLOCK_BIOS_MSG = 'Unlock Success'
    LINUX_LOCK_FAIL_MSG = 'Lock failed'
    LINUX_UNLOCK_FAIL_MSG = 'Unlock failed'
    LINUX_LOCK_STATUS_CMD = './ByoFlash -locksts'
    LINUX_LOCK_STATUS_MSG = 'It is locked'
    LINUX_UNLOCK_STATUS_MSG = 'It is unLocked'
    LINUX_LOCK_BIOS_UPDATE_MSG = 'It is locked'
    LINUX_CLEAN_PSW_CMD = './ByoFlash -rstpwd'
    LINUX_CLEAN_PSW_MSG = 'ResetPassword success'
    LINUX_FLASH_CMD_OTHERS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'
    LINUX_UPDATE_OTHERS_MSG = 'please check BIOS ID information'
    LINUX_UPDATE_UNSIGNED_MSG = 'Sign Verify .* failed'
    LINUX_EMPTY_CMD = f'./ByoFlash {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_ERROR_CMD = f'./ByoFlash -aaaa {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_INPUT_ERR_MSG = 'Options'

    #########ByoDmi工具
    SMBIOS_PATH_LINUX = "ByoTool\\Tools\\ByoDmi_Smbios\\LINUX\\"
    SMBIOS_PATH_WINDOWS = "ByoTool\\Tools\\ByoDmi_Smbios\\WINDOWS\\"
    SMBIOS_PATH_SHELL = "ByoTool\\Tools\\ByoDmi_Smbios\\SHELL\\"
    BYODMI_SMBIOS_CHANGE = {
        '1 0 4': 'oem104',
        '1 0 5': 'oem105',
        '1 0 6': 'oem106',
        '1 0 7': 'oem107',
        '1 0 8': '11 22 33 44 55 66 77 88 99 00 11 22 33 44 55 aa',
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

    #########ByoCfg工具
    REMOVE_OPTIONS = ['Custom Password Check', 'Quiet Boot', 'Boot Mode', 'SPI BIOS Lock', 'Console Redirection',
                      'Serial Port Select', 'Serial Port Baudrate', 'Terminal Type']
    BOOT_NAME_DICT_UEFI = {'HDD': 'Hard Drive',
                           'USB_DISK': 'USB Flash Drive/USB Hard Disk',
                           'PXE': 'Network Adapter',
                           'USB_ODD': 'USB CD/DVD ROM Drive',
                           'OTHERS': 'Others',
                           'ODD': 'CD/DVD ROM Drive'
                           }

    BOOT_NAME_DICT_LEGACY = {'HDD': 'Hard Drive',
                             'USB_DISK': 'USB Flash Drive/USB Hard Disk',
                             'PXE': 'Network Adapter',
                             'USB_ODD': 'USB CD/DVD ROM Drive',
                             'OTHERS': 'Others',
                             'ODD': 'CD/DVD ROM Drive'
                             }

    SET_UEFI = ['Bootup NumLock State', {'Network Boot': 'Enabled'}, {'Internal SHELL': 'Enabled'}, ]
    SET_LEGACY = ['Bootup NumLock State', {'Boot option filter': 'Legacy Only'}]

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
    LINUX_BYOCFG_LOCK_MSG = 'Lock Success'
    LINUX_BYOCFG_UNLOCK = './ByoCfg -unlock'
    LINUX_BYOCFG_UNLOCK_MSG = 'Unlock Success'
    LINUX_BYOCFG_UNLOCK_RUN_MSG = 'It is locked,use -unlock to unlock'

    LINUX_BYOCFG_ERROR_CMD = './ByoCfg -aaaa'
    LINUX_BYOCFG_ERR_MSG = 'Input paramter not support'


class Sec:
    OPEN_INTERNAL_SHELL = ['Bootup NumLock State', {'Internal SHELL': 'Enabled'}]
    SECURE_BOOT_PATH = ['Set Administrator Password', 'Secure Boot']
    OPEN_SECURE_BOOT = [{'Secure Boot': 'Enabled'}]
    CLOSE_SECURE_BOOT = [{'Secure Boot': 'Disabled'}]
    OPEN_CSM = ['Bootup NumLock State', {'Boot option filter': 'Legacy Only'}]
    CSM_CLOSE_MSG = '<UEFI Only> *Boot option filter'

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
    DEL_KEY_MSG = 'Are you sure you want to delete'
