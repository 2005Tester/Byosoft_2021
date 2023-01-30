import os
import datetime
from ByoTool.Config.PlatConfig import Key


class Env:
    # Report Setting
    PROJECT_NAME = "ByoTool"
    SUT_CONFIG = "SUT1-Half-DIMM"
    REPORT_TEMPLATE = "ByoTool\\Report\\template"

    TESTCASE_CSV = "ByoTool\\ToolTest.csv"
    RELEASE_BRANCH = "Hygon_017"

    # Environment settings
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\ByoTool\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Serial Port Configuration
    BIOS_SERIAL = "com7"

    # BMC Configuration
    BMC_IP = '192.168.6.124'
    BMC_USER = 'admin'
    BMC_PASSWORD = 'admin'

    # OS Configuration
    OS_IP = '192.168.6.110'
    OS_USER = 'root'
    OS_PASSWORD = 'Byosoft@2022'

    OS_IP_LEGACY = '192.168.6.110'
    OS_USER_LEGACY = 'root'
    OS_PASSWORD_LEGACY = 'Byosoft@2022'

    IPMITOOL = "ByoTool\\Tools\\ipmitool\\ipmitool.exe -I lanplus -H {0} -U {1} -P {2}".format(BMC_IP, BMC_USER,
                                                                                               BMC_PASSWORD)
    # BIOS remote path
    LINUX_USB_DEVICE = "/dev/sdb4"  # LinuxU盘盘符
    LINUX_USB_MOUNT = "/mnt/"
    LINUX_USB_NAME = 'Cruzer Force'  # Linux下'fdisk -l'中U盘名称
    WINDOWS_USB_PATH = "D:\\"
    SHELL_USB_PATH = "fs3:"
    USB_VOLUME = "USB:SanDisk \(P4\)"  # SetUp刷新BIOSU盘名

    BIOS_FILE = 'CRB7000'  # U盘存放BIOS文件和刷新工具的文件夹名
    LINUX_BIOS_MOUNT_PATH = "/mnt/{}/".format(BIOS_FILE)

    MACHINE_TYPE = 'Server'  # 测试机器的类型,服务器(支持Ipmi):'Server',桌面机:'Desktop'
    OEM_SUPPORT = False  # 是否支持通过OEM命令修改SetUp选项值


class Msg:
    SETUP_KEY = Key.F2  # POST界面进入SetUp按键
    BOOTMENU_KEY = Key.F7  # POST界面进入启动菜单按键
    POST_MESSAGE = 'Press F2 to'
    PAGE_MAIN = "CPU Info"
    PAGE_APPLIANCES = 'PCIE Configuration'
    PAGE_ADVANCED = 'Sys Debug Mode'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Load Setup Defaults'
    PAGE_ALL = [PAGE_MAIN, PAGE_APPLIANCES, PAGE_ADVANCED, PAGE_SECURITY, PAGE_BOOT, PAGE_EXIT]
    SETUP_MESSAGE = 'Select Language'  # 进入SetUp确认信息

    ENTER_BOOTMENU = "Startup Device Menu|ENTER to select boot device"  # 进入启动菜单确认信息
    ENTER_SETUP = "Enter Setup"
    USB_UEFI = 'UEFI USB: SanDisk'
    SHELL = "Internal EDK Shell"
    DOS = "USB: SanDisk"
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    OS_MSG = 'Kylin|Tencent|CentOS|UOS'
    LEGACY_OS = "SATA3-1: WDC WD5000LPCX-22VHAT0|UEFI SATA3-1: WDC WD5000LPCX-22VHAT0"  # Legacy系统盘在Legacy,UEFI模式下启动名
    LEGACY_OS_MSG = 'Kylin'
    UEFI_OS = 'Kylin Linux Advanced Server\(SATA3-1: SAMSUNG MZ7LH480HAHQ-00005\)|SATA3-1: SAMSUNG MZ7LH480HAHQ-00005'  # UEFI系统盘在Legacy,UEFI模式下启动名
    UEFI_OS_MSG = 'Kylin'
    LINUX_OS = 'UOS\(UEFI SATA5-2: INTEL SSDSCKKB960G8\)'  # UEFI系统盘在UEFI模式启动名，Legacy系统盘在Legacy模式下启动名
    # LINUX_OS = 'UOS\(UEFI SATA3-2: SAMSUNG MZ7L3480HCHQ-00B7C\)'
    LINUX_OS_MSG = 'UOS'
    WINDOWS_OS = 'Windows Boot Manager\(UEFI SATA1-6: WDC WD10EZEX-08WN4A0\)'
    WINDOWS_OS_MSG = ''


class Pxe:
    UEFI_USB_MSG = 'UEFI Interactive Shell'#进入U盘Shell确认信息
    LEGACY_USB_MSG = 'MS-DOS'#进入U盘DOS确认信息

    PXE_START_MSG = 'UEFI Intel\(R\) I350 Gigabit Network Connection PXE IPv4'#UEFI模式，PXE一个循环中开始的标志(一般为PXE第一个启动项名称)
    PXE_END_MSG = 'UEFI Intel\(R\) I350 Gigabit Network Connection-2 PXE IPv4'#UEFI模式，PXE一个循环中结束的标志(一般为PXE最后一个启动项名称)
    PXE_BOOT_NAME1 = 'UEFI Intel\(R\) I350 Gigabit Network Connection PXE IPv4'#PXE第一个启动项名称
    PXE_BOOT_NAME2 = 'UEFI Intel\(R\) I350 Gigabit Network Connection-2 PXE IPv4'#PXE最后一个启动项名称

    LOC_PXE = ['User Wait Time','Network Adapter']
    LOC_USB=['User Wait Time','USB Flash Drive/USB Hard Disk|USB Flash Drive']
    LOC_BOOT_MANAGER = ['Load Setup Defaults','Boot Manager']
    BOOT_MANAGER_MSG='Boot Manager Menu'
    SET_UEFI = ['User Wait Time',{'Boot option filter':'UEFI Only'},{'Network Boot':'Enabled'},{'Net Boot IP Version':'IPv4'},{'Http Boot':'Disabled'}]
    SET_PXE_0 = ['User Wait Time',{'PXE Retry':0}]
    SET_PXE_N = ['User Wait Time', {'PXE Retry': 8}]
    SET_PXE_MAX = ['User Wait Time', {'PXE Retry': 255}]

    LEGACY_PXE_START_MSG = '\x0cIntel\(R\)BootAgentGEv1.5.88'#Legacy模式，PXE一个循环中开始的标志
    LEGACY_PXE_BOOT_NAME1 = 'NET: IBA GE Slot 1100 v1588'#Legacy模式，PXE第一个启动项名称
    LEGACY_PXE_BOOT_NAME2 = 'NET: IBA GE Slot 1101 v1588'#Legacy模式，PXE最后一个启动项名称

    SET_LEGACY = ['User Wait Time',{'Boot option filter':'Legacy Only'},{'Network Boot':'Enabled'}]



class Psw:
    HDD_NAME1 = 'NVME\(PCI1-0-0\): Samsung SSD 980 250GB \(TCG-OPAL\)'
    HDD_BOOT_NAME1 = 'UEFI NVME\(PCI1-0-0\): Samsung SSD 980 250GB'
    HDD_NAME2 = 'SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C'
    HDD_BOOT_NAME2 = 'UOS\(UEFI SATA1-6: SAMSUNG MZ7L3480HCHQ-00B7C\)'
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

    SET_ADMIN_PSW = ['Set Administrator Password']  # SetUp下设置管理员密码的路径
    SET_USER_PSW = ['Set Administrator Password', 'Set User Password']  # SetUp下设置用户密码的路径
    SET_PSW_SUC_MSG = 'Password Setting Successfully'  # 密码设置成功的提示信息
    ADMIN_PSW_STATUS = 'Administrator Password *Installed'
    USER_PSW_STATUS = 'User Password *Installed'
    LOGIN_TYPE_ADMIN = 'User Login Type *Administrator'
    LOGIN_TYPE_USER = 'User Login Type *User'
    ERROR_PSW_MSG = 'Incorrect password'
    INVALID_PSW_MSG = 'Invalid Password'
    LOCK_MSG = ''
    DEL_PSW_SUC_MSG = 'Password deleted succeeded'  # 密码删除成功的提示信息
    PSW_FIVE_TIMES = 'Password has been used by the latest 5 times'
    CHARACTERS_LENGTH_NOT_ENOUGH = 'Please enter enough characters'
    CHARACTERS_TYPE_NOT_ENOUGH = 'Passwords can contain upper and lower case letters'
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

    LOC_BOOT_MANAGER = ['Load Setup Defaults', 'Boot Manager']
    BOOT_MANAGER_MSG = 'Boot Manager Menu'

class Tool:
    POST_PSW_MSG = 'System Security'  # 设置SetUp密码后,进入SetUp要求输入密码的提示信息

    # 修改的SMBIOS内容,可以在'{}'中间按照格式自定义添加
    SMBIOS_CHANGE = {'1 0 5': 'oem105',
                     '1 0 6': 'oem106',
                     }
    # 默认的SMBIOS内容,需要和修改的SMBIOS内容对应
    SMBIOS_DEFAULT = {'1 0 5': '62DB32',
                      '1 0 6': 'V1.0',

                      }

    SET_ADMIN_PSW = ['Set Administrator Password']  # SetUp下设置管理员密码的路径
    SET_USER_PSW = ['Set Administrator Password', 'Set User Password']  # SetUp下设置用户密码的路径
    SET_PSW_SUC_MSG = 'Password Setting Successfully'  # 密码设置成功的提示信息
    DEL_PSW_SUC_MSG = 'Password deleted succeeded'  # 密码删除成功的提示信息

    # 读取SetUp值时进入选项的路径,依次进入各主页面下的各级子菜单，'ESC'代表按ESC键
    OPTION_PATH = ['PCIE Configuration', 'PCIE Configuration', 'ESC', 'Video Configuration', 'ESC',
                   'SATA Configuration', 'ESC', 'NVME Device',
                   'ESC', 'USB Configuration', 'ESC', 'Sys Debug Mode', 'Wake from RTC', 'ESC', 'SATA/PCIE Switch',
                   'ESC']
    # OPTION_PATH=['Console Redirection','Onboard Lan Configuration','ESC','Video Configuration','ESC','USB Configuration','USB Port Configuration','ESC','ESC','Virtualization Configuration','ESC','Misc Configuration','ESC','Server Management']
    # 改变的SetUp选项
    CHANGE_OPTIONS = ['PCIE Configuration', 'PCIE Configuration', {'PCIE Wake': 'Disabled'}, 'PCIE Configuration',
                      'Video Configuration', {'Primary Graphics Adapter': 'IGD'}, 'Sys Debug Mode',
                      {'Above 4G Decoding': 'Disabled'}, 'User Wait Time', {'User Wait Time': 10}]
    # BIOS默认值
    DEFAULT_OPTION_VALUE = ['<Disabled>SysDebugMode', '<Enabled>Above4GDecoding', '<Enabled>SMTMode',
                            '<Enabled>SVMControl', '<Enabled>P-StateControl', '<Enabled>SR-IOVSupport', '<Enabled>NUMA',
                            '[0]LeakyBucketMinites', '[1]PcieCEThreshold', '[4096]CPUCEThreshold',
                            '<Enabled>APEIEINJCPUCESupport', '[5]RASCESmiThreshold', '<Disabled>TPMSelect',
                            '<Disabled>HygonTPCM', '[5]UserWaitTime', '<On>BootupNumLockState',
                            '<UEFIOnly>Bootoptionfilter', '<Enabled>InternalShell', '<Enabled>NetworkBoot',
                            '[0]PXERetry', '<IPv4>NetBootIPVersion', '<Disabled>HttpBoot', '<English>SelectLanguage',
                            '<Enabled>PCIEWake', '<Auto>PCIEMaxPayloadSize', '<Auto>PCIEMaxReadRequestSize',
                            '<Disabled>ASPMSupport', '<Enabled>ASM1061', '<Enabled>M.2(J511X)', '<Enabled>M.2(J521X)',
                            '<Enabled>RaidSlot(J488X)', '<Enabled>Slimline1_1(J1354X)', '<Enabled>Slimline1_2(J1354X)',
                            '<Enabled>OCP(J388X)', '<Enabled>RiserA_1(J1308X)', '<Enabled>RiserA_2(J1304X)',
                            '<Enabled>RiserA_3(J1304X)', '<Enabled>slimline2_1(J414X)', '<Enabled>slimline2_2(J414X)',
                            '<Enabled>RiserA_5(J1304X)', '<Enabled>RiserA_6(J1304X)', '<Enabled>Slimline4_1(J444X)',
                            '<Enabled>Slimline4_2(J444X)', '<Enabled>RiserB_1(J1334X)', '<Enabled>RiserB_2(J1334X)',
                            '<Enabled>RiserB_3(J1334X)', '<Enabled>RiserB_4(J1334X)', '<Enabled>RiserB_5(J1334X)',
                            '<Enabled>RiserB_6(J1334X)', '<Enabled>RiserB_7(J1334X)', '<Enabled>RiserB_8(J1334X)',
                            '<ALL>PrimaryGraphicsAdapter', '[16]SATAdevicedetectdelay', '<Enabled>S.M.A.R.TCheck',
                            '<Enabled>SATAController1', '<Enabled>SATAPort1', '<Enabled>SATAPort2',
                            '<Enabled>SATAPort3', '<Enabled>SATAPort4', '<Enabled>SATAPort5', '<Enabled>SATAPort6',
                            '<Enabled>SATAPort7', '<Enabled>SATAPort8', '<Enabled>SATAController2',
                            '<Enabled>SATAPort1', '<Enabled>SATAPort2', '<Enabled>SATAPort3', '<Enabled>SATAPort4',
                            '<Enabled>SATAPort5', '<Enabled>SATAPort6', '<Enabled>SATAPort7', '<Enabled>SATAPort8',
                            '<Enabled>SATAController3', '<Enabled>SATAPort1', '<Enabled>SATAPort2',
                            '<Enabled>SATAPort3', '<Enabled>SATAPort4', '<Enabled>SATAPort5', '<Enabled>SATAPort6',
                            '<Enabled>SATAPort7', '[100]USBwaitportstablestall', '<Enabled>USBMassStorageSupport',
                            '<Enabled>USBPort0', '<Enabled>USBPort1', '<Enabled>USBPort2', '<Enabled>USBPort3',
                            '[100]USBwaitportstablestall', '<Enabled>USBMassStorageSupport', '<Enabled>USBPort0',
                            '<Enabled>USBPort1', '<Enabled>USBPort2', '<Enabled>USBPort3', '<Disabled>Sunday',
                            '<Disabled>Monday', '<Disabled>Tuesday', '<Disabled>Wednesday', '<Disabled>Thursday',
                            '<Disabled>Friday', '<Disabled>Saturday', '<SATA>J112', '<SATA>J43']

    TOOL_PASSWORD_MSG = 'Please input (?:admin |poweron )*password|Please Enter Admin Password'  # 设置管理员密码后，刷新BIOS要求输入密码的提示信息
    WRONG_PSW_MSG = '(?:Password|password) is invalid|Check password failed|password is invalid'  # 工具刷新BIOS输入错误密码的提示信息
    BMC_LINK_OPTION = ['<Disabled>SOLforBaseboardMgmt', '<Enabled>SOLforBaseboardMgmt', '<StayOff>RestoreACPowerloss',
                       '<LastState>RestoreACPowerloss', '<PowerOn>RestoreACPowerloss']

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
    SHELL_LOCK_STATUS_MSG = 'It is locked|Flash Locked'
    SHELL_UNLOCK_STATUS_MSG = 'It is unLocked|Flash UnLocked|Flash unLocked'
    SHELL_LOCK_FAIL_MSG = 'Lock failed|Lock flash failed'
    SHELL_UNLOCK_FAIL_MSG = 'Unlock failed|Unlock flash failed'
    SHELL_LOCK_STATUS_CMD = 'ByoFlash.efi -locksts'
    SHELL_LOCK_BIOS_MSG = 'Lock success|Flash Locked'
    SHELL_UNLOCK_BIOS_MSG = 'Unlock success|Flash UnLocked'
    SHELL_LOCK_BIOS_UPDATE_MSG = 'It is locked|Flash is locked'
    SHELL_CLEAN_PSW_CMD = 'ByoFlash.efi -rstpwd'
    SHELL_CLEAN_PSW_MSG = 'ResetPassword success'
    SHELL_FLASH_CMD_OTHERS = 'ByoFlash.efi -bfu others.bin'
    SHELL_FLASH_CMD_UNSIGNED = 'ByoFlash.efi -bfu unsigned.bin'
    SHELL_UPDATE_OTHERS_MSG = 'BiosCheck Fail'
    SHELL_UPDATE_UNSIGNED_MSG = 'BiosCheck Fail'
    SHELL_EMPTY_CMD = 'ByoFlash.efi latest.bin'
    SHELL_ERROR_CMD = 'ByoFlash.efi -aaaa latest.bin'
    SHELL_INPUT_ERR_MSG = 'Input Error|Not support parameter'

    LINUX_TOOL_VERSION_CMD = './ByoFlash -v'
    LINUX_TOOL_VERSION_CONFIRM_MSG = 'Version|Byosoft Flash Utility'
    LINUX_TOOL_HELP_CMD = './ByoFlash -h'
    LINUX_TOOL_HELP_CONFIRM_MSG = 'Usage'
    LINUX_FLASH_CMD_LATEST_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -all'
    LINUX_FLASH_CMD_PREVIOUS_ALL = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin -all'
    LINUX_FLASH_CMD_LATEST = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_FLASH_CMD_PREVIOUS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_MSG_NOR = "Flash update successfully"
    LINUX_MSG_ALL = "Flash update successfully"
    LINUX_BACKUP_CMD = f'./ByoFlash -bu backup.bin'
    LINUX_BACKUP_SUC_MSG = 'Backup BIOS image Done'
    LINUX_UPDATE_BACKUP_CMD = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}latest.bin -bu backup.bin'
    LINUX_RESVNVM_CMD_LATEST = f'./ByoFlash -resvnvm {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_RESVNVM_CMD_PREVIOUS = f'./ByoFlash -resvnvm {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_RESVSMBIOS_CMD_LATEST = f'./ByoFlash -resvsmbios {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_RESVSMBIOS_CMD_PREVIOUS = f'./ByoFlash -resvsmbios {Env.LINUX_BIOS_MOUNT_PATH}previous.bin'
    LINUX_UPDATE_OA3_CMD = f'./ByoFlash -OA3 {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_LOCK_BIOS_UPDATE_CMD = f'./ByoFlash -lock'
    LINUX_UNLOCK_BIOS_UPDATE_CMD = f'./ByoFlash -unlock'
    LINUX_LOCK_BIOS_MSG = 'Flash Locked'
    LINUX_UNLOCK_BIOS_MSG = 'Flash UnLocked'
    LINUX_LOCK_FAIL_MSG = 'Lock flash failed'
    LINUX_UNLOCK_FAIL_MSG = 'Unlock flash failed'
    LINUX_LOCK_STATUS_CMD = f'./ByoFlash -locksts'
    LINUX_LOCK_STATUS_MSG = 'Flash Locked'
    LINUX_UNLOCK_STATUS_MSG = 'Flash unLocked'
    LINUX_LOCK_BIOS_UPDATE_MSG = 'Flash is locked, please unlock first'
    LINUX_CLEAN_PSW_CMD = './ByoFlash -rstpwd'
    LINUX_CLEAN_PSW_MSG = ''
    LINUX_FLASH_CMD_OTHERS = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}others.bin'
    LINUX_FLASH_CMD_UNSIGNED = f'./ByoFlash -bfu {Env.LINUX_BIOS_MOUNT_PATH}unsigned.bin'
    LINUX_UPDATE_OTHERS_MSG = 'please check BIOS ID information'
    LINUX_UPDATE_UNSIGNED_MSG = 'Sign Verify .* failed'
    LINUX_EMPTY_CMD = f'./ByoFlash {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_ERROR_CMD = f'./ByoFlash -aaaa {Env.LINUX_BIOS_MOUNT_PATH}latest.bin'
    LINUX_INPUT_ERR_MSG = 'Usage|Not support parameter'

    WINDOWS_TOOL_VERSION_CMD = 'ByoFlash.exe -v'
    WINDOWS_TOOL_VERSION_CONFIRM_MSG = 'Byosoft Flash Utility'
    WINDOWS_TOOL_HELP_CMD = 'ByoFlash.exe -h'
    WINDOWS_TOOL_HELP_CONFIRM_MSG = 'Usage'
    WINDOWS_FLASH_CMD_LATEST_ALL = f'ByoFlash.exe -bfu latest.bin -all'
    WINDOWS_FLASH_CMD_PREVIOUS_ALL = f'ByoFlash.exe -bfu previous.bin -all'
    WINDOWS_FLASH_CMD_LATEST = f'ByoFlash.exe -bfu latest.bin'
    WINDOWS_FLASH_CMD_PREVIOUS = f'ByoFlash.exe -bfu previous.bin'
    WINDOWS_MSG_NOR = "Flash update successfully"
    WINDOWS_MSG_ALL = "Flash update successfully"
    WINDOWS_BACKUP_CMD = f'ByoFlash.exe -bu backup.bin'
    WINDOWS_BACKUP_SUC_MSG = 'Status Success'
    WINDOWS_UPDATE_BACKUP_CMD = f'ByoFlash.exe -bfu latest.bin -bu backup.bin'
    WINDOWS_RESVNVM_CMD_LATEST = f'ByoFlash.exe -resvnvm latest.bin'
    WINDOWS_RESVNVM_CMD_PREVIOUS = f'ByoFlash.exe -resvnvm previous.bin'
    WINDOWS_RESVSMBIOS_CMD_LATEST = f'ByoFlash.exe -resvsmbios latest.bin'
    WINDOWS_RESVSMBIOS_CMD_PREVIOUS = f'ByoFlash.exe -resvsmbios previous.bin'
    WINDOWS_UPDATE_OA3_CMD = f'ByoFlash.exe -OA3 latest.bin'
    WINDOWS_LOCK_BIOS_UPDATE_CMD = f'ByoFlash.exe -lock'
    WINDOWS_UNLOCK_BIOS_UPDATE_CMD = f'ByoFlash.exe -unlock'
    WINDOWS_LOCK_BIOS_MSG = 'Flash Locked'
    WINDOWS_UNLOCK_BIOS_MSG = 'Flash UnLocked'
    WINDOWS_LOCK_FAIL_MSG = 'Lock flash failed'
    WINDOWS_UNLOCK_FAIL_MSG = 'Unlock flash failed'
    WINDOWS_LOCK_STATUS_CMD = f'ByoFlash.exe -locksts'
    WINDOWS_LOCK_STATUS_MSG = 'Flash Locked'
    WINDOWS_UNLOCK_STATUS_MSG = 'Flash unLocked'
    WINDOWS_LOCK_BIOS_UPDATE_MSG = 'Flash is locked, please unlock first'
    WINDOWS_CLEAN_PSW_CMD = 'ByoFlash.exe -rstpwd'
    WINDOWS_CLEAN_PSW_MSG = ''
    WINDOWS_FLASH_CMD_OTHERS = f'ByoFlash.exe -bfu others.bin'
    WINDOWS_FLASH_CMD_UNSIGNED = f'ByoFlash.exe -bfu unsigned.bin'
    WINDOWS_UPDATE_OTHERS_MSG = 'please check BIOS ID information'
    WINDOWS_UPDATE_UNSIGNED_MSG = 'Sign Verify .* failed'
    WINDOWS_EMPTY_CMD = f'ByoFlash.exe latest.bin'
    WINDOWS_ERROR_CMD = f'ByoFlash.exe -aaaa latest.bin'
    WINDOWS_INPUT_ERR_MSG = 'Not support parameter|Error command'

    #########ByoDmi工具
    SMBIOS_PATH_LINUX = "ByoTool\\Tools\\ByoDmi_Smbios\\LINUX\\"
    SMBIOS_PATH_WINDOWS = "ByoTool\\Tools\\ByoDmi_Smbios\\WINDOWS\\"
    SMBIOS_PATH_SHELL = "ByoTool\\Tools\\ByoDmi_Smbios\\SHELL\\"
    BYODMI_SMBIOS_CHANGE = {
        '1 0 4': 'oem104',
        '1 0 5': 'oem105',
        '1 0 6': 'oem106',
        '1 0 7': 'oem107',
        '1 0 8': '11 22 33 44 55 66 77 88 99 00 11 22 33 44 bb 66',
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
    SHELL_BYODMI_HELP_CONFIRM_MSG = 'help message|Utility'
    SHELL_BYODMI_TYPE_CMD = 'ByoDmi.efi -type'
    SHELL_BYODMI_VIEW_CMD = 'ByoDmi.efi -view'
    SHELL_BYODMI_VIEWALL_CMD = 'ByoDmi.efi -viewall'
    SHELL_BYODMI_LOCK_CMD = 'ByoDmi.efi -lock'
    SHELL_BYODMI_LOCK_MSG = 'Lock success|Flash Locked'
    SHELL_BYODMI_LOCK_RUN_MSG = 'It is locked|Flash is locked'
    SHELL_BYODMI_UNLOCK_CMD = 'ByoDmi.efi -unlock'
    SHELL_BYODMI_UNLOCK_MSG = 'Unlock success|Flash UnLocked'

    LINUX_BYODMI_VERSION_CMD = './ByoDmi -v'
    LINUX_BYODMI_VERSION_CONFIRM_MSG = 'ByoDmi Version:'
    LINUX_BYODMI_HELP_CMD = './ByoDmi -h'
    LINUX_BYODMI_HELP_CONFIRM_MSG = 'help message|Utility'
    LINUX_BYODMI_TYPE_CMD = './ByoDmi -type'
    LINUX_BYODMI_VIEW_CMD = './ByoDmi -view'
    LINUX_BYODMI_VIEWALL_CMD = './ByoDmi -viewall'

    LINUX_BYODMI_LOCK_CMD = './ByoDmi -lock'
    LINUX_BYODMI_LOCK_MSG = 'Lock Success|Flash Locked'
    LINUX_BYODMI_LOCK_RUN_MSG = 'It is locked|Flash is locked'
    LINUX_BYODMI_UNLOCK_CMD = './ByoDmi -unlock'
    LINUX_BYODMI_UNLOCK_MSG = 'Unlock Success|Flash UnLocked'

    WINDOWS_BYODMI_VERSION_CMD = 'ByoDmi.exe -v'
    WINDOWS_BYODMI_VERSION_CONFIRM_MSG = 'ByoDmi.exe Version:'
    WINDOWS_BYODMI_HELP_CMD = 'ByoDmi.exe -h'
    WINDOWS_BYODMI_HELP_CONFIRM_MSG = 'help message|Utility'
    WINDOWS_BYODMI_TYPE_CMD = 'ByoDmi.exe -type'
    WINDOWS_BYODMI_VIEW_CMD = 'ByoDmi.exe -view'
    WINDOWS_BYODMI_VIEWALL_CMD = 'ByoDmi.exe -viewall'
    WINDOWS_BYODMI_LOCK_CMD = 'ByoDmi.exe -lock'
    WINDOWS_BYODMI_LOCK_MSG = 'Lock Success|Flash Locked'
    WINDOWS_BYODMI_LOCK_RUN_MSG = 'It is locked|Flash is locked'
    WINDOWS_BYODMI_UNLOCK_CMD = 'ByoDmi.exe -unlock'
    WINDOWS_BYODMI_UNLOCK_MSG = 'Unlock Success|Flash UnLocked'

    #########ByoCfg工具
    REMOVE_OPTIONS = ['Custom Password Check', 'Quiet Boot', 'Boot Mode', 'SPI BIOS Lock']
    BOOT_NAME_DICT_UEFI = {'HDD': 'Hard Drive',
                           'USB_DISK': 'USB Flash Drive',
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

    SET_UEFI = ['User Wait Time', {'Boot option filter': 'UEFI Only'}, {'Internal Shell': 'Enabled'}]
    SET_LEGACY = ['User Wait Time', {'Boot option filter': 'Legacy Only'}]

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
    LINUX_BYOCFG_ERR_MSG = 'Usage|Failed'

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
    WINDOWS_BYOCFG_ERR_MSG = 'Usage|Failed'


class Sec:
    SET_DTPM = ['Set Administrator Password', {'TPM Select': 'DTPM(SPI)'}]
    SET_FTPM = ['Set Administrator Password', {'TPM Select': 'FTPM'}]
    LOC_TCG2 = ['Set Administrator Password', 'TCG2 Configuration']
    CLOSE_TPM = ['Set Administrator Password', {'TPM Select': 'Disabled|Disable'}]
    CLOSE_TPM_STATE = ['Set Administrator Password', 'TCG2 Configuration', {'TPM State': 'Disabled'}]
    OPEN_TPM_STATE = ['Set Administrator Password', 'TCG2 Configuration', {'TPM State': 'Enabled'}]
    TPM_LIST = ['Platform Hierarchy', 'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization']
    REV_NAME = 'Attempt Rev of TPM2 ACPI Table'
    PPI_NAME = 'Attempt PPI Version'
    PCR_BANK_MSG = 'New PCRBanks is 0x\d+. \('
    CHANGE_TPM_VALUE = ['TPM2 PCR_Allocate(Algorithm IDs)', 'TPM2 ChangeEPS']
    ESC_MSG = 'Press ESC to reject this change'

    OPEN_INTERNAL_SHELL = ['User Wait Time', {'Internal Shell': 'Enabled'}]
    SECURE_BOOT_PATH = ['Set Administrator Password', 'Secure Boot']
    OPEN_SECURE_BOOT = [{'Secure Boot': 'Enabled'}]
    CLOSE_SECURE_BOOT = [{'Secure Boot': 'Disabled'}]
    OPEN_CSM = ['User Wait Time', {'Boot option filter': 'Legacy Only'}]
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
    DEL_KEY_MSG = 'Are you sure you want to delete|to delete'
    GUID_NAME = 'Signature GUID'
    ERROR_CHARACTERS = 'Please enter in the correct format'
    LOW_CHARACTERS = 'Please enter enough characters'


class Upd:
    SET_UPDATE_ALL = ['Load Setup Defaults', {
        'BIOS Update Parameters': 'Full Update'}]

    UPDATE_BIOS_LATEST = ['Load Setup Defaults', 'BIOS Update',
                          Env.USB_VOLUME, f'<{Env.BIOS_FILE}>', 'latest.bin']

    SETUP_MSG = 'Flash is updated successfully'
