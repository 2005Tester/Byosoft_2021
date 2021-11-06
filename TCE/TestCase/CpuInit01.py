import logging
import re
from batf import SerialLib, SshLib, MiscLib, core
from batf.SutInit import Sut
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import BiosCfg, Key, Msg
from TCE.BaseLib import SetUpLib, BmcLib
from batf.Report import ReportGen, stylelog


# Cpu Related Test case, test case ID, TC200-299

##########################################
#              CPU Test Cases            #
##########################################
# function Module : acpidump验证X2APIC
def acpidump():
    local_list = []
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
    SshLib.execute_command(Sut.OS_SSH, r'rm *.dat *.out *.dsl')  # 清理
    SshLib.execute_command(Sut.OS_SSH, r'acpidump -o ACPI.out')  # 导出acpi列表
    logging.info("get ACPI.out")
    SshLib.execute_command(Sut.OS_SSH, r'acpixtract -a ACPI.out')  # 获取ACPI.dat文件
    logging.info("get ACPI.dat")

    SshLib.execute_command(Sut.OS_SSH, r'iasl -d apic.dat')  # 解析acpi.dat文件[0]
    logging.info("analysis apic.dat")
    Local_APIC = SshLib.execute_command(Sut.OS_SSH, r'cat apic.dsl')
    local_list.append(Local_APIC)

    SshLib.execute_command(Sut.OS_SSH, r'iasl -d slit.dat')  # 解析slit.dat文件[1]
    logging.info("analysis slit.dat")
    Local_slit = SshLib.execute_command(Sut.OS_SSH, r'cat slit.dsl')
    local_list.append(Local_slit)

    SshLib.execute_command(Sut.OS_SSH, r'iasl -d dsdt.dat')  # 解析dsdt.dat文件[2]
    logging.info("analysis dsdt.dat")
    Local_dsdt = SshLib.execute_command(Sut.OS_SSH, r'cat dsdt.dsl')
    local_list.append(Local_dsdt)

    SshLib.execute_command(Sut.OS_SSH, r'iasl -d srat.dat')  # 解析srat.dat文件[3]
    logging.info("analysis srat.dat")
    Local_srat = SshLib.execute_command(Sut.OS_SSH, r'cat srat.dsl')
    local_list.append(Local_srat)

    return local_list


# function Module : 使用unitool还原bios setting
def reset_cpu_setting(cmd_var):
    logging.info("Reseting CPU settings.")
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 60):
        SetUpLib.boot_suse_from_bm()
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 300):
            return
    if not Sut.UNITOOL.write(**cmd_var):
        logging.info('unitool write_in fail')
        return
    logging.info("unitool.write_in pass")
    if not Sut.UNITOOL.check(**cmd_var):
        logging.info('check unitool_write fail')
        return
    logging.info('Modify bios setting to default setting by unipwd tool, Pass')
    return True


#  function Module, TC205,TC206,TC207 调用
def cpu_cores_active_enable(num, set_n):
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, ACT_CPU_CORES, 20)
        SetUpLib.send_keys([Key.F6] * set_n)
        stylelog.info("Core counts changed to {0}, save and reboot.".format(set_n))
        SetUpLib.send_keys([Key.F10, Key.Y], 5)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        SetUpLib.send_keys([Key.ENTER])
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        stylelog.info("Verify Memory Information")
        assert SetUpLib.verify_info(SutConfig.SysCfg.DIMM_INFO, 20)
        assert SetUpLib.boot_suse_from_bm()
        # 每个CPU下只有num个core。
        res = SshLib.execute_command(Sut.OS_SSH, r'lscpu | grep "per socket" ')
        res1 = res.replace('\n', '').split(':')[-1].strip()
        assert int(res1) == num, ("**Core Enable error = {}".fotmat(res1))
        # 在smbios4中检查：Core数量为总数，Core Enable为num，线程数为Enabled核数的两倍 #
        res2 = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | egrep -m 3 "Core Count|Core Enabled|Thread Count"')
        Core_Count = res2.splitlines()[0].split(':')[-1].strip()
        Core_Enabled = res2.splitlines()[1].split(':')[-1].strip()
        Thread_Count = res2.splitlines()[2].split(':')[-1].strip()
        assert Core_Count == '28' and Core_Enabled == str(num) and Thread_Count == str(num * 2), \
            '**Core or Thread eorro:{},{},{}**'.format(Core_Count, Core_Enabled, Thread_Count)
        logging.info('All check pass')
        return True
    except AssertionError:
        return False


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
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PER_CPU_INFO, 20, 'BSP Revision')
        logging.info("**Verify CPU Information**")
        assert SetUpLib.verify_info(SutConfig.SysCfg.CPU_INFO, 20)
        SetUpLib.send_keys([Key.ESC, Key.ESC])
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        logging.info("**Verify Memory Information**")
        assert SetUpLib.verify_info(SutConfig.SysCfg.DIMM_INFO, 20)
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
    result = ReportGen.LogHeaderResult(tc)
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    list_info = ['All', '27', '26', '25', '24', '23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                 '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
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
    result = ReportGen.LogHeaderResult(tc)
    num = 1
    set_n = 31
    try:
        assert cpu_cores_active_enable(num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_cpu_setting(BiosCfg.ActiveCpuCores_Default)


def cpu_cores_active_enable_middle():
    tc = ('206', '[TC206] Testcase_CoreDisable_003', 'Enable middle-num CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    num = 18
    set_n = 14
    try:
        assert cpu_cores_active_enable(num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_cpu_setting(BiosCfg.ActiveCpuCores_Default)


def cpu_cores_active_enable_max():
    tc = ('207', '[TC207] Testcase_CoreDisable_004', 'Enable max-1 CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    num = 31
    set_n = 1
    try:
        assert cpu_cores_active_enable(num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_cpu_setting(BiosCfg.ActiveCpuCores_Default)


# Verify CPU disable Processor Cores,the system runs normally
# Precondition: unitool
# OnStart: NA
# OnComplete: suse Page
def cpu_cores_disable_sys_normally():
    tc = ('208', '[TC208] CoreDisable_005', 'After disable the CPU core, the system runs normally')
    result = ReportGen.LogHeaderResult(tc)
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    n = 1
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, ACT_CPU_CORES, 20)
        SetUpLib.send_keys([Key.F6] * 31)
        logging.info("**Active Processor Cores**")
        SetUpLib.send_keys([Key.F10, Key.Y], 5)
        logging.info("**reboot**")
        while n < 5:  # 系统反复复位，暂定4次
            # boot suse #
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
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


# Unitool to modify the number of CPU cores,in bios and OS Verify CPU Cores
# Precondition: Unitool
# OnStart: NA
# OnComplete: suse Page
def cores_customized_by_unitool():
    tc = ('209', '[TC209] CoreDisable_007', 'Unitool to modify the number of CPU cores,in bios and OS Verify CPU Cores')
    result = ReportGen.LogHeaderResult(tc)
    ACT_CPU_CORES = ['Active Processor Cores', '<20>']
    try:
        assert SetUpLib.boot_suse_from_bm()
        stylelog.info("Suse_OS Boot Successful")
        MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.write(ActiveCpuCores=20)
        SshLib.execute_command(Sut.OS_SSH, r'reboot')
        # 进入Bios ，验证 unitool修改是否成功
        stylelog.info("Verify processor counts in Setup.")
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(ACT_CPU_CORES, 20)
        stylelog.success("bios setting verified")
        # 进入 OS，验证 unitool修改是否成功
        assert SetUpLib.boot_suse_from_bm()
        res = SshLib.execute_command(Sut.OS_SSH, r'lscpu | grep " per socket" ').replace('\n', '').split(':')[
            -1].strip()
        assert res
        if int(res) == 20:
            stylelog.success('Verify cpu cores - pass')
        else:
            logging.debug(res)
            stylelog.fail('Verify cpu cores - fail')
            result.log_fail()
            return
        # 还原系统设置
        stylelog.success("正常还原")
        result.log_pass()
        return True
    except AssertionError:
        stylelog.fail("异常还原")
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# modify the numa disable/enable,in OS Verification
# Precondition: suse
# OnStart: NA
# OnComplete: suse Page


# function Module
def numa_disabled_verify():  # 进入 Numa page，设置 Numa 为 Disabled,到 suse中验证
    numa_bef = ['NUMA', '<Enabled>']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        return False
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_COMM, 20, Msg.NUMA):
        return False
    if not SetUpLib.locate_option(Key.DOWN, numa_bef, 20):
        return False
    SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 600):
        return False
    return True


def numa_enabled_verify():  # 进入 Numa page，设置 Numa 为 Enabled，到 suse中验证
    numa_aft = ['NUMA', '<Disabled>']
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        return False
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_COMM, 20, Msg.NUMA):
        return False
    if not SetUpLib.locate_option(Key.DOWN, numa_aft, 20):
        return False
    SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 600):
        return False
    return True


# Author: Fubaolin
# 内存NUMA特性设置测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def numa_01():
    tc = ('210', '[TC210] Testcase_NUMA_001', '内存NUMA特性设置测试')
    result = ReportGen.LogHeaderResult(tc)
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
            logging.debug(nodes_enab)
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
    result = ReportGen.LogHeaderResult(tc)
    Num_cmd = r'numactl -H'
    try:
        assert SetUpLib.boot_suse_from_bm()
        logging.info("Suse_OS Boot Successful")
        numa_h = SshLib.execute_command(Sut.OS_SSH, Num_cmd)
        assert numa_h
        numa_n = int(numa_h.split("nodes")[0].split(":")[1].replace(' ', ''))  # 获取CPU数量
        i = 0
        for i in range(numa_n):
            numa_var = list(numa_h.split("node   0   1")[1].split(r'{}:'.format(i))[1].splitlines()[0].replace('  ',
                                                                                                               ' ').strip().split(
                ' '))
            # logging.info(numa_var)
            if numa_var[i] == '10':  # CPU自己与自己距离为‘10’
                logging.info("内部CPU距离正常")
                numa_var.pop(i)
                for j in range(numa_n - 1):
                    if numa_var[j] == '20':  # CPU与其他cpu 距离为‘20’
                        logging.info("外部CPU距离正常")
                    else:
                        logging.debug(numa_var[j])
                        logging.info('外部CPU距离-fail')
                        return result.log_fail(capture=True)
            else:
                logging.debug(numa_var[i])
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
    result = ReportGen.LogHeaderResult(tc)
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
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_suse_from_bm()
        stylelog.info("Suse_OS Boot Successful")
        fail_dir = SutConfig.Env.LOG_DIR + r'\TC213.log'
        with open(fail_dir, 'r+', encoding='utf-8') as f:
            line_text = f.readlines()
            for str in line_text:
                if 'bist' in str:
                    logging.info('found "bist", fail')
                    result.log_fail()
                    return
                else:
                    logging.info('not found "bist",pass ')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Author: Fubaolin
# CPU Hyper-Threading 特性测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_03():
    tc = ('214', '[TC214] Testcase_CPU_COMPA_003', 'CPU Hyper-Threading 特性测试')
    result = ReportGen.LogHeaderResult(tc)
    ht_bef = ["Hyper-Threading \[ALL\]", "<Enabled>"]
    ht_aft = ["Hyper-Threading \[ALL\]", "<Disabled>"]
    try:
        assert BmcLib.force_reset()
        # HT-enabled查看物理CPU中core数量
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "cpu cores"| uniq')
        assert res
        Core_Count = res.split(':')[1].replace(' ', '').strip('\n')
        logging.info("**Core_Count = {}".format(Core_Count))
        # 查看逻辑CPU的个数
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "processor"| wc -l')
        assert res
        Logical_CPU = res.strip('\n')
        logging.info("**Core_Enabled = {}".format(Logical_CPU))
        if Core_Count == '32' and Logical_CPU == '128':
            logging.info("**Core_Count pass, Logical_CPU pass**")
        else:
            logging.debug(Core_Count, Logical_CPU)
            logging.info("**Core eorro**")
            return False
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(ht_bef, 2)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        # HT-disabled 查看物理CPU中core数量
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "cpu cores"| uniq')
        assert res
        Core_Count = res.split(':')[1].replace(' ', '').strip('\n')
        logging.info("**Core_Count = {}**".format(Core_Count))
        # 查看逻辑CPU的个数
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "processor"| wc -l')
        assert res
        Logical_CPU = res.strip('\n')
        logging.info("**Core_Enabled = {}**".format(Logical_CPU))
        if Core_Count == '32' and Logical_CPU == '64':
            logging.info("**Core_Count pass, Logical_CPU pass**")
        else:
            logging.debug(Core_Count, Logical_CPU)
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
    result = ReportGen.LogHeaderResult(tc)
    mic_version = ['Microcode Revision\s+0D0002A0\s+|\s+0D0002A0']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info(mic_version, 6)
        assert BmcLib.force_reset()
        # OS中 查看CPU微码
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /sys/devices/system/cpu/cpu0/microcode/version')
        assert res
        mic_ver = res.strip('\n')
        logging.info("**mic_ver = {}**".format(mic_ver))
        if mic_ver == '0xd0002a0':
            logging.info("The microcode-version in OS is the same as that in BIOS")
        else:
            logging.debug(mic_ver)
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
    result = ReportGen.LogHeaderResult(tc)
    pro_fre = ['Processor Frequency\s+2.200GHz+|\s+2.200GHz']
    pro_ver = ['Processor 1 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz',
               'Processor 2 Version \s+Intel\(R\) Xeon\(R\) Gold 6 \s+338N CPU @ 2.20GHz']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info(pro_fre, 20)
        assert SetUpLib.verify_info(pro_ver, 20)
        assert BmcLib.force_reset()
        # 在smbios4中检查：cpu型号，频率，个数
        res = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Version:" ')
        assert res
        cpu_version = res.replace('\n', '').split(':')[-1].strip()
        if cpu_version == 'Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz':
            logging.info('cpu_version is ok')
        else:
            logging.debug(cpu_version)
            logging.info('Different, please check')
            return result.log_fail(capture=True)
        cpu_num = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Socket Designation:" ')
        assert cpu_num
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


# Author: Fubaolin
# X2APIC选项测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_017():
    tc = ('215', '[TC215] Testcase_CPU_COMPA_017', 'X2APIC选项测试')
    result = ReportGen.LogHeaderResult(tc)
    Extended_APIC = ['Extended APIC', '<Disabled>']
    ht_bef = ["Hyper-Threading \[ALL\]", "<Enabled>"]
    date_1 = 'Raw Table Data'
    data_2 = 'Processor x2Apic ID'
    data_3 = 'Processor Local APIC/SAPIC Affinity'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PRO_CFG, 20, Msg.EXTENDED_APIC)
        assert SetUpLib.locate_option(Key.DOWN, Extended_APIC, 20)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)
        acpi_list_bf = acpidump()

        apic_n = acpi_list_bf[0].split(date_1)[0].count(data_2)
        srat_n = acpi_list_bf[3].split(date_1)[0].count(data_3)
        logging.info("当前实际核数：{0}, {1}".format(apic_n, srat_n))
        assert apic_n == 128, '在apic文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在apic文件中，X2APIC个数与当前CPU总线程数一致')
        assert srat_n == 128, '在srat文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在srat文件中，X2APIC个数与当前CPU总线程数一致')

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, ht_bef, 20)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        acpi_list_af = acpidump()

        apic_m = acpi_list_af[0].split(date_1)[0].count(data_2)
        srat_m = acpi_list_af[3].split(date_1)[0].count(data_3)
        logging.info("当前实际核数：{0}, {1}".format(apic_m, srat_m))
        assert apic_m == 64, '在apic文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在apic文件中，X2APIC个数与当前CPU总线程数一致')
        assert srat_m == 64, '在srat文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在srat文件中，X2APIC个数与当前CPU总线程数一致')

        SshLib.execute_command(Sut.OS_SSH, r'rm *.dat *.out *.dsl')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()
      
      
# cpu_compa_024
# Author: Lupeipei
@core.test_case(('227', '[227] cpu_compa_024', 'OS下X2APIC开关状态测试'))
def cpu_compa_024():
    Extended_APIC = ['Extended APIC', '<Disabled>']
    try:
        # Extended APIC BIOS选项默认是Disabled
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PRO_CFG, 20, Msg.EXTENDED_APIC)
        assert SetUpLib.verify_options(Key.DOWN, [Extended_APIC], 16)
        assert SetUpLib.boot_suse_from_bm()
        res = SshLib.execute_command(Sut.OS_SSH, r'dmesg | grep -i x2apic').replace('\n','')
        assert re.search("DMAR-IR: x2apic is disabled", res)
        # Extended APIC BIOS选项设置为Enabled
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PRO_CFG, 20, Msg.EXTENDED_APIC)
        assert SetUpLib.locate_option(Key.DOWN, Extended_APIC, 20)
        assert SetUpLib.set_option_value('Extended APIC', 'Enabled', save=True)
        assert SetUpLib.continue_to_boot_suse_from_bm()
        res = SshLib.execute_command(Sut.OS_SSH, r'dmesg | grep -i x2apic').replace('\n', '')
        assert re.search("x2apic: enabled by BIOS", res)
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
    finally:
        BmcLib.clear_cmos()


# Testcase_S3_001
# Precondition: linux-OS,unitool 部分OS kernel版本可能主动开启S3/S4功能，建议使用kernel 4.9或者以前内核测试
# OnStart: 'UEFI'模式
# Steps:
# '1、进入OS下，执行cat /sys/power/state查询，有结果A；
#  2、执行命令echo mem > /sys/power/state，尝试进入S3，有结果B。
# 'A：查询结果没有显示mem字符串；
#  B：执行命令后报错，无法进入S3。
# OnCompleted: OS
def testcase_s3_001():
    tc = ('221', '[TC221] 01 S3关闭测试', '不支持S3启动')
    result = ReportGen.LogHeaderResult(tc)
    assert BmcLib.force_reset()
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
    if 'mem' in SshLib.execute_command(Sut.OS_SSH, 'cat /sys/power/state'):
        logging.info('部分OS kernel版本可能主动开启S3/S4功能，建议使用kernel 4.9或者以前内核测试')
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_CoreDisable_008
# Precondition: register.json文件具体Get路径参考：
# /redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v5_1_5.json
# OnStart: 'UEFI'模式
# Steps:
# '1、使用Postman工具获取BIOS上报的register.json文件；
#  2、检查ProcessorActiveCore的Type、DisplayName、DefaultValue字段，有结果A。
# A：Type:"Enumeration"
# DisplayName:"Active Processor Cores"
# DefaultValue:All
# 此预期结果示实际情况而定。
# OnCompleted: OS
def testcase_coreDisable_008():
    tc = ('222', '[TC222] 08 BIOS上报CPU核数到register.json文件正确性测试', '支持CPU关核')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        # verify data based on the platform,
        data = {
            'AttributeName': 'ActiveCpuCores',
            'Type': 'Enumeration',
            'DisplayName': 'Active Processor Cores',
            'DefaultValue': 'All',
        }
        reg_path = Sut.BMC_RFISH.get_reg_path()
        res = Sut.BMC_RFISH.get_info(reg_path)['RegistryEntries']['Attributes']
        for i in res:
            if i['AttributeName'] == "ActiveCpuCores":
                cmp_res = [j for j in tuple(data.items()) if j not in tuple(i.items())]
                logging.debug("The diff data is".format(cmp_res))
                assert cmp_res == [], 'result cmp failed,'
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()


# Testcase_CoreDisable_009
# Precondition: register.json文件具体Get路径参考：'1、Postman工具已正确安装
# /redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v5_1_5.json
# OnStart: 'UEFI'模式
# Steps:
# 1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":1，有结果A；
# 2、重启X86进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
# A：命令下发正常，无报错；
# B：CPU使能核数显示为1。
# OnCompleted: SETUP
def set_core_redfish(tc, set_data, exp_data):  # this def used to set cpu cores via redfish,
    """
    tc - report flag
    set_data: based on platform, refer to setup base line,
    exp_data: 200 is ok, 400 or others - False, error
    """
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.BMC_RFISH.set_bios_option(
            **{'ActiveCpuCores': '{0}'.format(set_data)}).status == exp_data, 'status != ok, result is False'
        assert SetUpLib.boot_to_page(Msg.CPU_CONFIG)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.PROCESSOR_CONFIG], 12, Msg.PER_CPU)
        # 根据平台实际cpu核数，设定 set_data 数值
        if set_data == 0 or set_data > 33:
            assert SetUpLib.locate_option(Key.DOWN, ['Active Processor Cores', '<All>'], 12)
        else:
            assert SetUpLib.locate_option(Key.DOWN, ['Active Processor Cores', '<{0}>'.format(set_data)], 12)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
        return
    finally:
        BmcLib.clear_cmos()


def testcase_coreDisable_009():
    tc = ('223', '[TC223] 09 redfish带外使能1个CPU核数测试', '支持CPU关核')
    return set_core_redfish(tc, 1, 200)


# Testcase_CoreDisable_010
# Precondition: register.json文件具体Get路径参考：'1、Postman工具已正确安装
# /redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v5_1_5.json
# OnStart: 'UEFI'模式
# Steps:
# '1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":n（n为当前CPU支持的最大核数），有结果A；
#  2、重启X86进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
# A：命令下发正常，无报错；
# B：CPU使能核数显示为ALL，系统启动正常，无挂死反复复位现象。
# OnCompleted: SETUP
def testcase_coreDisable_010():
    tc = ('224', '[TC224] 10 redfish带外使能CPU核数最大值测试', '支持CPU关核')
    return set_core_redfish(tc, 32, 200)


# Testcase_CoreDisable_011
# Precondition: register.json文件具体Get路径参考：'1、Postman工具已正确安装
# /redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v5_1_5.json
# OnStart: 'UEFI'模式
# Steps:
# '1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":n（n为超过当前CPU支持的最大核数），有结果A；
#  2、重启X86进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
#  A：n<=28时命令下发正常，无报错；n>28时报错，下发失败。 max is 43,
#  B：CPU使能核数显示为ALL。
# OnCompleted: SETUP
def testcase_coreDisable_011():
    tc = ('225', '[TC225] 11 redfish带外使能CPU核数超过最大值测试', '支持CPU关核')
    return set_core_redfish(tc, 33, 400)


# 1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":0，有结果A；
def testcase_coreDisable_012():
    tc = ('226', '[TC226] 12 redfish带外使能CPU核数为0测试', '支持CPU关核')
    return set_core_redfish(tc, 0, 400)
