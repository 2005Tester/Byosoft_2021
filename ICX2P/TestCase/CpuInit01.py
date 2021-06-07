import logging
from Core import SerialLib, SshLib, MiscLib
from Core.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import SetUpLib, BmcLib
from Report import ReportGen


# Cpu Related Test case, test case ID, TC200-299

##########################################
#              CPU Test Cases            #
##########################################


# function Module : 使用unitool还原bios setting
def reset_cpu_setting(cmd_var):
    cmd = eval("dict(%s)" % cmd_var.replace(":", "="))
    if not BmcLib.force_reset():
        logging.info('power off-on fail')
        return False
    if not MiscLib.ping_sut(SutConfig.OS_IP, 300):
        logging.info('boot linux-suse fail')
        return False
    if not Sut.UNITOOL.write(**cmd):
        logging.info('unitool write_in fail')
        return False
    logging.info("unitool.write_in pass")
    if not Sut.UNITOOL.check(**cmd):
        logging.info('check unitool_write fail')
        return False
    logging.info('Modify bios setting to default setting by unipwd tool, Pass')
    return True


#  function Module, TC205,TC206,TC207 调用
def cpu_cores_active_enable(num, set_n):
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    cmd_var = 'ActiveCpuCores:0'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.locate_option(Key.DOWN, ACT_CPU_CORES, 20)
        SetUpLib.send_keys([Key.F6]*set_n)
        logging.info("**Active Processor Cores**")
        SetUpLib.send_keys([Key.F10, Key.Y], 5)
        logging.info("**reboot**")
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        # assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        SetUpLib.send_keys(Key.ENTER)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        logging.info("**Verify Memory Information**")
        assert SetUpLib.verify_info(SutConfig.DIMM_info, 20)
        # boot suse #
        assert BmcLib.force_reset()
        # 每个CPU下只有num个core。
        res1 = SshLib.execute_command(Sut.OS_SSH, r'lscpu | grep " per socket" ').replace('\n', '').split(':')[-1].strip()
        assert res1
        if int(res1) == num:
            logging.info("**Core Enable pass**")
        else:
            logging.info("**Core Enable eorro**")
            return False
        # 在smbios4中检查：Core数量为总数，Core Enable为num，线程数为Enabled核数的两倍 #
        smbios4_Core_Count = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Core Count" ').replace('\n', '').split(':')[-1].strip()
        logging.info("**Core_Count = {}**".format(smbios4_Core_Count))
        smbios4_Core_Enabled = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Core Enabled" ').replace('\n', '').split(':')[-1].strip()
        logging.info("**Core_Enabled = {}**".format(smbios4_Core_Enabled))
        smbios4_Thread_Count = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Thread Count" ').replace('\n', '').split(':')[-1].strip()
        logging.info("**Thread_Count = {}**".format(smbios4_Thread_Count))
        if smbios4_Core_Count == '28' and smbios4_Core_Enabled == str(num) and smbios4_Thread_Count == str(num*2):
            logging.info("**Core_Count pass, Core_Enabled pass,Thread_Count pass")
        else:
            logging.info("**Core eorro**")
            return False
        # 使用 unitool 还原 'Active Processor Cores', '<All>' #
        logging.info("正常还原")
        return True
    except AssertionError:
        logging.info("异常还原")
    finally:
        reset_cpu_setting(cmd_var)

# Testcase_CPU_COMPA_015, 016 - TBD
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Uncore status page
def upi_link_status():
    tc = ('200', '[TC200]UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc)
    upi_state = ['Current UPI Link Speed\s+Fast', 'Current UPI Link Frequency\s+11\.2\s+GT\/s']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_STATUS, 22, 'Uncore Status'):
        result.log_fail()
        return

    if not SetUpLib.verify_info(upi_state, 4):
        result.log_fail()
        return
    logging.info("**UPI Link speed and frequency verified.")
    result.log_pass()
    return True


# Testcase_UFS_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup P-State control page
def ufs_default_value():
    tc = ('201', '[TC201]Testcase_UFS_001', 'UFS默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    ufs = ['UFS', '<Enabled>']

    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE):
        result.log_fail()
        return

    if not SetUpLib.verify_options(Key.DOWN, [ufs], 4):
        result.log_fail()
        return
    SetUpLib.send_keys([Key.ESC, Key.ENTER])
    if not SetUpLib.locate_option(Key.DOWN, ["UFS", "<Enabled>"], 12):
        result.log_fail()
        return
    logging.info("**UFS default value verified.")
    SetUpLib.send_key(Key.ENTER)
    if not SerialLib.is_msg_present(Sut.BIOS_COM, r'Disabled_MaxDisabled_Min', 10):
        result.log_fail()
        return
    logging.info("**UFS Supported values verified.")
    result.log_pass()
    return True


# Testcase_Static_Turbo_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Advanced power management page
def static_turbo_default():
    tc = ('202', '[TC202]Testcase_Static_Turbo_001', '静态Turbo默认值测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    static_turbo_default = ['Static Turbo', '<Disabled>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_ADV_PM_CFG, 20, Msg.ADV_POWER_MGF_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, static_turbo_default, 10)
        SetUpLib.send_key(Key.ENTER)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, r'AutoManualDisabled')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU and DIMM information
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Memory Topology Page
def cpu_mem_info():
    tc = ('203', '[TC203]CPU Memory Information', 'Verify CPU and Memory Information')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PER_CPU_INFO, 20, 'BSP Revision')
        logging.info("**Verify CPU Information**")
        assert SetUpLib.verify_info(SutConfig.CPU_info, 20)
        SetUpLib.send_keys([Key.ESC, Key.ESC])
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        logging.info("**Verify Memory Information**")
        assert SetUpLib.verify_info(SutConfig.DIMM_info, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU Active Processor Cores information
# Precondition: NA
# OnStart: NA
# OnComplete: Processor Configuration Page
def cpu_cores_active():
    tc = ('204', '[204]Testcase_CoreDisable_001', 'CPU Active Processor Cores information')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    list_info = ['All', '27', '26', '25', '24', '23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.locate_option(Key.DOWN, ACT_CPU_CORES, 20)
        SetUpLib.send_key(Key.ENTER)
        logging.info("**Active Processor Cores**")
        assert SetUpLib.verify_info(list_info, 28)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU Active Processor Cores information
# Precondition: unitool
# OnStart: NA
# OnComplete: suse Page
def cpu_cores_active_enable_1():
    tc = ('205', '[TC205] Testcase_CoreDisable_002', 'Enable 1 CPU core test')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    num = 1
    set_n = 28
    try:
        assert cpu_cores_active_enable(num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


def cpu_cores_active_enable_middle():
    tc = ('206', '[TC206] Testcase_CoreDisable_003', 'Enable middle-num CPU core test')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    num = 14
    set_n = 14
    try:
        assert cpu_cores_active_enable(num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


def cpu_cores_active_enable_max():
    tc = ('207', '[TC207] Testcase_CoreDisable_004', 'Enable max-1 CPU core test')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    num = 27
    set_n = 1
    try:
        assert cpu_cores_active_enable(num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU disable Processor Cores,the system runs normally
# Precondition: unitool
# OnStart: NA
# OnComplete: suse Page
def cpu_cores_disable_sys_normally():
    tc = ('208', '[TC208] CoreDisable_005', 'After disable the CPU core, the system runs normally')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    n = 1
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.locate_option(Key.DOWN, ACT_CPU_CORES, 20)
        SetUpLib.send_keys([Key.F6]*28)
        logging.info("**Active Processor Cores**")
        SetUpLib.send_keys([Key.F10, Key.Y], 5)
        logging.info("**reboot**")
        while n < 5:  # 系统反复复位，暂定4次
            # boot suse #
            assert MiscLib.ping_sut(SutConfig.OS_IP, 600)
            res = SshLib.execute_command(Sut.OS_SSH, r'date')
            logging.info("system reboot pass, system-Time is : {} ".format(res))
            assert BmcLib.force_reset()
            n = n+1
        # 还原系统设置
        logging.info("正常还原")
        result.log_pass()
    except AssertionError:
        logging.info("异常还原")
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Unitool to modify the number of CPU cores,in bios and OS Verify CPU Cores
# Precondition: Unitool
# OnStart: NA
# OnComplete: suse Page
def cores_customized_by_unitool():
    tc = ('209', '[TC209] CoreDisable_007', 'Unitool to modify the number of CPU cores,in bios and OS Verify CPU Cores')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    ACT_CPU_CORES = ['Active Processor Cores', '<20>']
    try:
        assert SetUpLib.boot_with_hotkey(Key.F11, "Boot Manager Menu", 300)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, "Welcome to GRUB")
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, 170)
        logging.info("Suse_OS Boot Successful")
        MiscLib.ping_sut(SutConfig.OS_IP, 600)
        assert Sut.UNITOOL.write(ActiveCpuCores=20)
        SshLib.execute_command(Sut.OS_SSH, r'reboot')
        # 进入Bios ，验证 unitool修改是否成功
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.verify_info(ACT_CPU_CORES, 20)
        logging.info("bios setting checkin")
        # 进入 OS，验证 unitool修改是否成功
        assert BmcLib.force_reset()
        res = SshLib.execute_command(Sut.OS_SSH, r'lscpu | grep " per socket" ').replace('\n', '').split(':')[-1].strip()
        assert res
        if int(res) == 20:
            logging.info('checkin cpu_core - pass')
        else:
            logging.info('checkin cpu_core - fail')
            return
        # 还原系统设置
        logging.info("正常还原")
        result.log_pass()
    except AssertionError:
        logging.info("异常还原")
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()

# modify the numa disable/enable,in OS Verification
# Precondition: suse
# OnStart: NA
# OnComplete: suse Page


# function Module
def numa_disabled_verify(): # 进入 Numa page，设置 Numa 为 Disabled,到 suse中验证
    numa_bef = ['NUMA', '<Enabled>']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        return False
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_COMM, 20, Msg.NUMA):
        return False
    if not SetUpLib.locate_option(Key.DOWN, numa_bef, 20):
        return False
    SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
    if not MiscLib.ping_sut(SutConfig.OS_IP, 600):
        return False
    return True


def numa_enabled_verify(): # 进入 Numa page，设置 Numa 为 Enabled，到 suse中验证
    numa_aft = ['NUMA', '<Disabled>']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        return False
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_COMM, 20, Msg.NUMA):
        return False
    if not SetUpLib.locate_option(Key.DOWN, numa_aft, 20):
        return False
    SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)
    if not MiscLib.ping_sut(SutConfig.OS_IP, 600):
        return False
    return True


# Author: Fubaolin
# 内存NUMA特性设置测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def numa_01():
    tc = ('210', '[TC210] Testcase_NUMA_001', '内存NUMA特性设置测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    Num_cmd = r'numactl --hardware'
    try:
        assert numa_disabled_verify()
        nodes_dis = SshLib.execute_command(Sut.OS_SSH, Num_cmd).split('nodes')[0].split(':')[1]
        if int(nodes_dis) == 1:
            logging.info('numa_disabled pass')
        else:
            logging.info('numa_disabled fail')
            return result.log_fail(capture=True)
        assert numa_enabled_verify()
        nodes_enab = SshLib.execute_command(Sut.OS_SSH, Num_cmd).split('nodes')[0].split(':')[1]
        if int(nodes_enab) == 2:
            logging.info('numa_enabled pass')
        else:
            logging.info('numa_enabled fail')
            return result.log_fail(capture=True)
        logging.info("正常还原")
        result.log_pass()
    except AssertionError:
        logging.info("异常还原")
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# NUMA Distance距离与硬件结构匹配测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def numa_02():
    tc = ('211', '[TC211] Testcase_NUMA_002', 'NUMA Distance距离与硬件结构匹配测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    Num_cmd = r'numactl -H'
    try:
        assert SetUpLib.boot_with_hotkey(Key.F11, "Boot Manager Menu", 300)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, "Welcome to GRUB")
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, 170)
        logging.info("Suse_OS Boot Successful")
        numa_h = SshLib.execute_command(Sut.OS_SSH, Num_cmd)
        numa_n =int(numa_h.split("nodes")[0].split(":")[1].replace(' ', '')) #获取CPU数量
        i = 0
        for i in range(numa_n):
            numa_var = list(numa_h.split("node   0   1")[1].split(r'{}:'.format(i))[1].splitlines()[0].replace('  ', ' '). strip().split(' '))
            # logging.info(numa_var)
            if numa_var[i] == '10': #  CPU自己与自己距离为‘10’
                logging.info("内部CPU距离正常")
                numa_var.pop(i)
                for j in range(numa_n-1):
                    if numa_var[j] =='20': # CPU与其他cpu 距离为‘20’
                        logging.info("外部CPU距离正常")
                    else:
                        logging.info('外部CPU距离-fail')
                        return result.log_fail(capture=True)
            else:
                logging.info("内部CPU距离-fail")
                return result.log_fail(capture=True)
        result.log_pass()
    except AssertionError:
        result.log_fail()


# Author: Fubaolin
# 关闭NUMA内存条1DPC反复复位测试
# Precondition: linux-OS,Unitool,
# OnStart: NA
# OnComplete: NA
def numa_03():
    tc = ('212', '[TC212] Testcase_NUMA_003', '关闭NUMA内存条1DPC反复复位测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    n = 1
    try:
        assert numa_disabled_verify()
        while n < 5:  # 系统反复复位，暂定4次
            res = SshLib.execute_command(Sut.OS_SSH, r'date')
            logging.info("system reboot pass, system-Time is : {} ".format(res))
            assert BmcLib.force_reset()
            n = n + 1
        # 还原系统设置
        logging.info("正常还原")
        result.log_pass()
    except AssertionError:
        logging.info("异常还原")
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# CPU BIST自检结果测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_02():
    tc = ('213', '[TC213] Testcase_CPU_COMPA_002', 'CPU BIST自检結果测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_with_hotkey(Key.F11, "Boot Manager Menu", 300)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, "Welcome to GRUB")
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, 170)
        logging.info("Suse_OS Boot Successful")
        fail_dir = SutConfig.LOG_DIR + r'\TC213.log'
        with open(fail_dir, 'r+',  encoding='utf-8') as f:
            line_text = f.readlines()
            for str in line_text:
                if 'bist' in str:
                    logging.info('found "bist", fail')
                    return result.log_fail(capture=True)
                else:
                    logging.info('not found "bist",pass ')
        result.log_pass()
    except AssertionError:
        result.log_fail()


# Author: Fubaolin
# CPU Hyper-Threading 特性测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_03():
    tc = ('214', '[TC214] Testcase_CPU_COMPA_003', 'CPU Hyper-Threading 特性测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    ht_bef = ["Hyper-Threading \[ALL\]", "<Enabled>"]
    ht_aft = ["Hyper-Threading \[ALL\]", "<Disabled>"]
    try:
        assert BmcLib.force_reset()
        # HT-enabled查看物理CPU中core数量
        Core_Count = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "cpu cores"| uniq').split(':')[1].replace(' ', '').strip('\n')
        logging.info("**Core_Count = {}".format(Core_Count))
        # 查看逻辑CPU的个数
        Logical_CPU = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "processor"| wc -l').strip('\n')
        logging.info("**Core_Enabled = {}".format(Logical_CPU))
        if Core_Count == '28' and Logical_CPU == '112':
            logging.info("**Core_Count pass, Logical_CPU pass**")
        else:
            logging.info("**Core eorro**")
            return False
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(ht_bef, 2)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        # HT-disabled 查看物理CPU中core数量
        Core_Count = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "cpu cores"| uniq').split(':')[1].replace(' ', '').strip('\n')
        logging.info("**Core_Count = {}**".format(Core_Count))
        # 查看逻辑CPU的个数
        Logical_CPU = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "processor"| wc -l').strip('\n')
        logging.info("**Core_Enabled = {}**".format(Logical_CPU))
        if Core_Count == '28' and Logical_CPU == '56':
            logging.info("**Core_Count pass, Logical_CPU pass**")
        else:
            logging.info("**Core eorro**")
            return False
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(ht_aft, 2)
        result.log_pass()
        return True
    except AssertionError:
        logging.info("异常还原")
        result.log_fail(capture=True)
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# CPU微码测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_05():
    tc = ('216', '[TC216] Testcase_CPU_COMPA_005', 'CPU微码测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    mic_version = ['Microcode Revision\s+0D0002A0\s+|\s+0D0002A0']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info(mic_version, 6)
        assert BmcLib.force_reset()
        # OS中 查看CPU微码
        mic_ver = SshLib.execute_command(Sut.OS_SSH, r'cat /sys/devices/system/cpu/cpu0/microcode/version').strip('\n')
        logging.info("**mic_ver = {}**".format(mic_ver))
        if mic_ver == '0xd0002a0':
            logging.info("The microcode-version in OS is the same as that in BIOS")
        else:
            logging.info("Different, please check")
            return result.log_fail(capture=True)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Author: Fubaolin
# CPU信息显示测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_06():
    tc = ('217', '[TC217] Testcase_CPU_COMPA_006', 'CPU信息显示测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    pro_fre = ['Processor Frequency\s+2.000GHz+|\s+2.000GHz']
    pro_ver = ['Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+330 CPU @ 2.00GHz',
               'Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+330 CPU @ 2.00GHz']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info(pro_fre, 20)
        assert SetUpLib.verify_info(pro_ver, 20)
        assert BmcLib.force_reset()
        # 在smbios4中检查：cpu型号，频率，个数
        cpu_version = \
        SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Version:" ').replace('\n', '').split(':')[-1].strip()
        if cpu_version == 'Intel(R) Xeon(R) Gold 6330 CPU @ 2.00GHz':
            logging.info('cpu_version is ok')
        else:
            logging.info('Different, please check')
            return result.log_fail(capture=True)
        cpu_num = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Socket Designation:" ')
        if 'CPU01' in cpu_num:
            if 'CPU02' in cpu_num:
                logging.info('cpu_num is ok')
            else:
                logging.info('cpu02 no found,please check')
                return result.log_fail(capture=True)
        else:
            logging.info('cpu01 no found,please check')
            return result.log_fail(capture=True)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


