import os


class Spr5885HV7:
    PROJECT_NAME = "5885H V7"  # 项目名称 (batf)

    # Define test plan
    TESTCASE_CSV = "SPR4P\\AllTest.csv"
    if os.path.exists("SPR4P\\AllTestLocal.csv"):
        TESTCASE_CSV = "SPR4P\\AllTestLocal.csv"

    # Hardware Version
    PCH_VERSION = r'EBG PCH B1 - EBG A0/A1/B0/B1 SKU'

    # Latest Branch Firmware Version
    BMC_VER = '3.06.02.02'
    ME_VER_LATEST = '18:6.0.4.25'           # [master]
    RC_VER_LATEST = '1.1.1.020F'            # [master]
    MICRO_CODE_LATEST = 'AB000161'          # [master]
    BIOS_VER_LATEST = '2.00.28'             # [master]
    BIOS_DATE_LATEST = '12/21/2022'         # [master]

    # Release Branch Firmware Version
    ME_VER_RELEASE = ME_VER_LATEST          # [Release]
    RC_VER_RELEASE = RC_VER_LATEST          # [Release]
    MICRO_CODE_RELEASE = MICRO_CODE_LATEST  # [Release]
    BIOS_VER_RELEASE = BIOS_VER_LATEST      # [Release]
    BIOS_DATE_RELEASE = BIOS_DATE_LATEST    # [Release]

    # Git Branch Name
    BRANCH_LATEST = "master"
    BRANCH_RELEASE = "5885HV7_028"          # [Release]
    BRANCH_OLD = "5885HV7_027"              # [Release]

    # 满配CPU Socket数量
    MAX_CPU_CNT = 4

    # HPM BIOS存放路径 (Release测试需要刷入HPM BIOS时，需要将HPM BIOS存放到指定路径中)
    BIOS_PATH = rf"\\192.168.113.26\PublicRW\QA\Firmware\5885HV7\BIOS"

    BIOS_BIN_NAME = "5885HV7"  # 从Git下载的压缩包里，.bin的文件名标志

    HOTKEY_RETRY = 2  # 热键retry次数(有些时候按键一次无法生效)

    AC_CMD = "regwrite 0x391 0x80"

    POWER_EFFICIENCY = "Resource/PowerEfficiency/5885HV7_PowerEfficiency.csv"

    # PCIE ROOT PORT: Max Support BandWidth
    PCIE_MAP = [
        {   # socket 0
            "1a": "x16",  # ocp
            "3a": "x8",   # slot4
            "3e": "x8",   # slot5
        },
        {   # socket 1
            "1a": "x8",   # slot6
        }]

    MMIOH_BASE = "32T"
    MMIOH_SIZE = "256G"


class Spr2288HV7:
    PROJECT_NAME = "2288 V7"  # 项目名称 (batf)

    # Define test plan
    TESTCASE_CSV = "SPR4P\\AllTest.csv"
    if os.path.exists("SPR4P\\AllTestLocal.csv"):
        TESTCASE_CSV = "SPR4P\\AllTestLocal.csv"

    # Hardware Version
    PCH_VERSION = r'EBG PCH B1 - EBG A0/A1/B0/B1 SKU'

    # Latest Branch Firmware Version
    BMC_VER = '3.06.02.05'
    ME_VER_LATEST = Spr5885HV7.ME_VER_LATEST            # [master]
    RC_VER_LATEST = Spr5885HV7.RC_VER_LATEST            # [master]
    MICRO_CODE_LATEST = Spr5885HV7.MICRO_CODE_LATEST    # [master]
    BIOS_VER_LATEST = Spr5885HV7.BIOS_VER_LATEST        # [master]
    BIOS_DATE_LATEST = Spr5885HV7.BIOS_DATE_LATEST      # [master]

    # Release Branch Firmware Version
    ME_VER_RELEASE = "18:6.0.4.25"          # [Release]
    RC_VER_RELEASE = "1.1.1.016B"           # [Release]
    MICRO_CODE_RELEASE = "AB0000C0"         # [Release]
    BIOS_VER_RELEASE = "2.00.19"            # [Release]
    BIOS_DATE_RELEASE = "01/07/2023"        # [Release]

    # Git Branch Name
    BRANCH_LATEST = "master"
    BRANCH_RELEASE = "2288HV7_019"          # [Release]
    BRANCH_OLD = "2288HV7_018"              # [Release]

    # 满配CPU Socket数量
    MAX_CPU_CNT = 2

    # HPM BIOS存放路径 (Release测试需要刷入HPM BIOS时，需要将HPM BIOS存放到指定路径中)
    BIOS_PATH = rf"\\192.168.113.26\PublicRW\QA\Firmware\2288HV7\BIOS"

    BIOS_BIN_NAME = "2288V7"  # 从Git下载的压缩包里，.bin的文件名标志

    HOTKEY_RETRY = 3  # 热键retry次数(有时候按键一次无法生效)

    AC_CMD = "regwrite 0x96 2"

    POWER_EFFICIENCY = "Resource/PowerEfficiency/2288V7_PowerEfficiency.csv"

    # PCIE ROOT PORT: Max Support BandWidth
    PCIE_MAP = [
        {   # socket 0
            "1a": "x16",  # ocp
            "2a": "x16",  # slot4
            "3a": "x16",  # slot5
            "5a": "x8",
        },
        {   # socket 1
            "1a": "x16",  # slot6
            "2a": "x16",
            "3a": "x4",
            "3c": "x4",
            "3e": "x4",
            "3g": "x4",
        }]

    MMIOH_BASE = "13T"
    MMIOH_SIZE = "64G"

