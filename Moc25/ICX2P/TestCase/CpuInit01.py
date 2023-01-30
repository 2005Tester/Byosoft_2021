import logging
import re
import time

from batf import SerialLib, SshLib, MiscLib, core
from batf.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import BiosCfg, Key, Msg
from ICX2P.BaseLib import SetUpLib, BmcLib
from batf.Report import ReportGen, stylelog

lowest_frequency = 800  # Mhz
min_cpu_base = int(SutConfig.SysCfg.CPU_BASE * 1000) - int(SutConfig.SysCfg.CPU_BASE * 1000 * 0.1)
max_cpu_base = int(SutConfig.SysCfg.CPU_BASE * 1000) + int(SutConfig.SysCfg.CPU_BASE * 1000 * 0.1)

# Cpu Related Test case, test case ID, TC200-299

##########################################
#              CPU Test Cases            #
##########################################
# function Module : acpidump验证X2APIC
def _acpidump():
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
def _reset_cpu_setting(cmd_var):
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
def _cpu_cores_active_enable(num):
    res_lst = []  # restore the res result
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.set_option_value('Active Processor Cores', '{0}'.format(num), save=True)
        stylelog.info("Core counts changed to {0}, save and reboot.".format(num))
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        stylelog.info("Verify Memory Information")
        assert SetUpLib.verify_info(SutConfig.SysCfg.DIMM_INFO, 20)
        assert SetUpLib.boot_suse_from_bm()
        # 每个CPU下只有num个core。
        res = SshLib.execute_command(Sut.OS_SSH, r'lscpu | grep "per socket"')
        res1 = res.replace('\n', '').split(':')[-1].strip()
        assert int(res1) == num, ("**Core Enable error = {}".format(res1))
        # 在smbios4中检查：Core数量为总数，Core Enable为num，线程数为Enabled核数的两倍 #
        res2 = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | egrep -m 3 "Core Count|Core Enabled|Thread Count"')
        Core_Count = res2.splitlines()[0].split(':')[-1].strip()
        Core_Enabled = res2.splitlines()[1].split(':')[-1].strip()
        Thread_Count = res2.splitlines()[2].split(':')[-1].strip()
        res_lst.extend([Core_Count, Core_Enabled, Thread_Count])
        assert [str(SutConfig.SysCfg.CPU_CORES), str(num), str(num * 2)] == res_lst,\
            '**Core or Thread err:{0}**'.format(res_lst)
        logging.info('All check pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


# stress tools， 配置参看 “Byo AT测试开发进度表- TC229”
def _cpu_stress_tool(command1, command2, succe_flag, ssh_type=Sut.OS_SSH):
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
    get_cpu = SshLib.execute_command(ssh_type, f"{command1} & {command2}")
    if succe_flag not in get_cpu:
        logging.debug('** check linux_command ')
        return
    return get_cpu


def _cpu_to_c6(command1, flag_c6):
    try:
        # 空载时,CPU进入到C6
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_c6 = SshLib.execute_command(Sut.OS_SSH, command1)
        logging.debug(cpu_c6)
        assert cpu_c6 is not None and flag_c6 in cpu_c6, '** linux_OS command --> fail'
        pkg_6 = []  # cpu 整体状态，根据cpu个数显示
        cpu_6 = []  # cpu_core 状态，根据每个cpu_core数量显示
        for i in cpu_c6.split('\n')[2:-1]:
            if len(i.split()) == 3:
                cpu_6.append(i)
            if len(i.split()) == 4:
                pkg_6.append(i)
        pkg_flag = 0
        cpu_core = 0
        for k in pkg_6:
            if k[3] == 0:
                logging.debug('** No. {0}_cpu, C6 = {1}'.format(k.split()[0], k.split()[3]))
                pkg_flag += 1
        for j in cpu_6:
            if j[2] == 0:
                logging.debug('** No. {0}_cpu_{1} core, C6 = {2}'.format(j.split()[0], j.split()[1], j.split()[2]))
                cpu_core += 1
        assert pkg_flag == 0 and cpu_core == 0, "**cpu空载时，进入C6 --> fail"
        logging.info('空载时 C6 --- pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


def _cpu_to_c0(command1, command2, succ_flag):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_c0 = _cpu_stress_tool(command1, command2, succ_flag)
        logging.debug(cpu_c0)
        assert cpu_c0 is not None, '** linux_OS command --> fail'
        assert float(cpu_c0.split('\n')[2].strip()) > 45, '**加载时进入C0 --> fail'
        logging.info('加压后 C0 --- pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


def _cpu_to_c1(command1, flag_c1):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_c1 = SshLib.execute_command(Sut.OS_SSH, command1)
        res_c1 = float(cpu_c1.split('\n')[2].strip())
        logging.debug(cpu_c1)
        assert cpu_c1 is not None and flag_c1 in cpu_c1, '** linux_OS command --> fail'
        assert res_c1 > 90, f'**空闲时进入C1 --> fail,cpu_c1 = {res_c1}'
        logging.info('空闲时 C1 --- pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


# Testcase_CPU_COMPA_015, 016 - TBD
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Uncore status page
def upi_link_status():
    tc = ('200', '[TC200]UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc)
    if SutConfig.SysCfg.CPU_CNT < 2:
        logging.info("UPI must be tested on 2-way or more system")
        result.log_skip()
        return
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_STATUS, 22, 'Uncore Status'):
        result.log_fail()
        return
    if not SetUpLib.verify_info(SutConfig.SysCfg.upi_state, 4):
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
        result.log_fail()


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
        result.log_fail()


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
        result.log_fail()


# Verify CPU Active Processor Cores information
# Precondition: unitool
# OnStart: NA
# OnComplete: suse Page
def cpu_cores_active_enable_1():
    tc = ('205', '[TC205] Testcase_CoreDisable_002', 'Enable 1 CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _cpu_cores_active_enable(1)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


def cpu_cores_active_enable_middle():
    tc = ('206', '[TC206] Testcase_CoreDisable_003', 'Enable middle-num CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _cpu_cores_active_enable(14)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


def cpu_cores_active_enable_max():
    tc = ('207', '[TC207] Testcase_CoreDisable_004', 'Enable max-1 CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert _cpu_cores_active_enable(27)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


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
        SetUpLib.send_keys([Key.F6] * 28)
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
        return True
    except AssertionError:
        logging.info("异常还原")
        result.log_fail()
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
def _numa_disabled_verify():  # 进入 Numa page，设置 Numa 为 Disabled,到 suse中验证
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


def _numa_enabled_verify():  # 进入 Numa page，设置 Numa 为 Enabled，到 suse中验证
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
        assert _numa_disabled_verify()
        nodes_dis = SshLib.execute_command(Sut.OS_SSH, Num_cmd).split('nodes')[0].split(':')[1]
        if int(nodes_dis) == 1:
            logging.info('numa_disabled pass')
        else:
            logging.info('numa_disabled fail')
            result.log_fail()
            return
        assert _numa_enabled_verify()
        nodes_enab = SshLib.execute_command(Sut.OS_SSH, Num_cmd).split('nodes')[0].split(':')[1]
        if int(nodes_enab) == 2:
            logging.info('numa_enabled pass')
        else:
            logging.info('numa_enabled fail')
            result.log_fail()
            return
        logging.info("正常还原")
        result.log_pass()
        return True
    except AssertionError:
        logging.info("异常还原")
        result.log_fail()
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
        stylelog.info("Suse_OS Boot Successful")
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
                        logging.info('外部CPU距离-fail')
                        result.log_fail()
                        return
            else:
                logging.info("内部CPU距离-fail")
                result.log_fail()
                return
        result.log_pass()
        return True
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
        assert _numa_disabled_verify()
        while n < 5:  # 系统反复复位，暂定4次
            res = SshLib.execute_command(Sut.OS_SSH, r'date')
            logging.info("system reboot pass, system-Time is : {} ".format(res))
            assert BmcLib.force_reset()
            n = n + 1
        # 还原系统设置
        logging.info("正常还原")
        result.log_pass()
        return True
    except AssertionError:
        logging.info("异常还原")
        result.log_fail()
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
                    continue
        logging.info('not found "bist",pass ')
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: Fubaolin
# CPU Hyper-Threading 特性测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_03():
    tc = ('214', '[TC214] Testcase_CPU_COMPA_003', 'CPU Hyper-Threading 特性测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert BmcLib.force_reset()
        # HT-enabled查看物理CPU中core数量
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "cpu cores"| uniq')
        assert res
        Core_Count = int(res.split(':')[1].replace(' ', '').strip('\n'))
        logging.info("**HT-enabled, Core_Count = {}".format(Core_Count))
        # 查看逻辑CPU的个数
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "processor"| wc -l')
        assert res
        Logical_CPU = int(res.strip('\n'))
        logging.info("**HT-enabled, Core_Enabled = {}".format(Logical_CPU))
        if Core_Count == SutConfig.SysCfg.CPU_CORES and Logical_CPU == SutConfig.SysCfg.CPU_CNT*SutConfig.SysCfg.CPU_CORES*2:
            logging.info("**HT-enabled,Core_Count pass, Logical_CPU pass**")
        else:
            logging.info("**HT-enabled, Core eorro**")
            result.log_fail()
            return
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, ["Hyper-Threading \[ALL\]", f"<.+>"], 5)
        assert SetUpLib.verify_supported_values("Enabled")
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y])
        time.sleep(120)
        # HT-disabled 查看物理CPU中core数量
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "cpu cores"| uniq')
        assert res
        Core_Count = int(res.split(':')[1].replace(' ', '').strip('\n'))
        logging.info("**HT-disabled, Core_Count = {}**".format(Core_Count))
        # 查看逻辑CPU的个数
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /proc/cpuinfo| grep "processor"| wc -l')
        assert res
        Logical_CPU = int(res.strip('\n'))
        logging.info("**HT-disabled, Core_Enabled = {}**".format(Logical_CPU))
        if Core_Count == SutConfig.SysCfg.CPU_CORES and Logical_CPU == SutConfig.SysCfg.CPU_CNT*SutConfig.SysCfg.CPU_CORES:
            logging.info("**HT-disabled,Core_Count pass, Logical_CPU pass**")
        else:
            logging.info(f"**HT-disabled, Core_Count={Core_Count}, Logical_CPU={Logical_CPU}**")
            return
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, ["Hyper-Threading \[ALL\]", f"<.+>"], 5)
        assert SetUpLib.verify_supported_values("Disabled")
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        logging.info("异常还原")
        result.log_fail()
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
    mic_rev = 'Microcode Revision\s+0D000331'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info([mic_rev], 10)
        assert BmcLib.force_reset()
        # OS中 查看CPU微码
        res = SshLib.execute_command(Sut.OS_SSH, r'cat /sys/devices/system/cpu/cpu0/microcode/version')
        assert '0x' in res, "command return err"
        mic_ver = res.strip('\n').replace('0x', '0', 1)
        assert mic_ver == mic_rev.split('+')[1].lower(), "res is blank, check it"
        logging.info("The microcode-version in OS is the same as that in BIOS")
        result.log_pass()
        return True
    except Exception as err:
        logging.error(err)
        result.log_fail()


# Author: Fubaolin
# CPU信息显示测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_06():
    tc = ('217', '[TC217] Testcase_CPU_COMPA_006', 'CPU信息显示测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info(SutConfig.SysCfg.CPU_INFO, 20)
        assert BmcLib.force_reset()
        # 在smbios4中检查：cpu型号，频率，个数
        res = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Version:" ')
        assert res, "Get invalid data of dmidecode -t4"
        os_cpu_list = re.findall(SutConfig.SysCfg.CPU_FULL_NAME, res)
        assert os_cpu_list, "**OS check CPU type or frequency mismatch"
        logging.info("**OS check CPU type and frequency success")
        assert len(os_cpu_list) == SutConfig.SysCfg.CPU_CNT, "OS CPU count mismatch"
        logging.info("**OS check CPU count success")
        result.log_pass()
        return True
    except Exception as e:
        logging.error(e)
        result.log_fail()


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
        acpi_list_bf= _acpidump()

        apic_n = acpi_list_bf[0].split(date_1)[0].count(data_2)
        srat_n = acpi_list_bf[3].split(date_1)[0].count(data_3)
        logging.info("当前实际核数：{0}, {1}".format(apic_n, srat_n))
        assert apic_n == SutConfig.SysCfg.CPU_CNT*56, '在apic文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在apic文件中，X2APIC个数与当前CPU总线程数一致')
        assert srat_n == SutConfig.SysCfg.CPU_CNT*56, '在srat文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在srat文件中，X2APIC个数与当前CPU总线程数一致')

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, ht_bef, 20)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        acpi_list_af = _acpidump()

        apic_m = acpi_list_af[0].split(date_1)[0].count(data_2)
        srat_m = acpi_list_af[3].split(date_1)[0].count(data_3)
        logging.info("当前实际核数：{0}, {1}".format(apic_m, srat_m))
        assert apic_m == SutConfig.SysCfg.CPU_CNT*28, '在apic文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.info('在apic文件中，X2APIC个数与当前CPU总线程数一致')
        assert srat_m == SutConfig.SysCfg.CPU_CNT*28, '在srat文件中，X2APIC个数与当前CPU总线程数不一致，需要检查'
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
@core.test_case(('227', '[TC227] cpu_compa_024', 'OS下X2APIC开关状态测试'))
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


# Author: Fubaolin
# 支持时钟展频设置
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_SpreadSpectrum_001():
    tc = ('218', '[TC218] Testcase_SpreadSpectrum_001', 'BIOS支持时钟展频设置测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_MISC_CONFIG, 20, 'Spread Spectrum')
        assert SetUpLib.verify_supported_values("Disabled")
        # boot to suse,use unitool  verify_info
        assert SetUpLib.boot_suse_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.open_shell()
        assert Sut.UNITOOL.check(**BiosCfg.Spread_Spectrum_bef)
        assert Sut.UNITOOL.write(**BiosCfg.Spread_Spectrum_aft)
        assert Sut.UNITOOL.check(**BiosCfg.Spread_Spectrum_aft)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# 支持APIC中CPU核数上报
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_ApicReport():
    tc = ('219', '[TC219] Testcase_ApicReport_001,002,003', '支持APIC中CPU总线程数和核数上报')
    result = ReportGen.LogHeaderResult(tc, SutConfig.Env.LOG_DIR)
    Extended_APIC = ['Extended APIC', '<Disabled>']
    Extended_APIC2 = ['Extended APIC', '<Enabled>']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PRO_CFG, 20, Msg.EXTENDED_APIC)
        assert SetUpLib.locate_option(Key.DOWN, Extended_APIC, 20)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)
        Local_Apic_ID = _acpidump()[0].split('Raw Table Data')[0].count('Processor Local x2APIC')
        assert Local_Apic_ID == SutConfig.SysCfg.CPU_CNT*56, '在apic文件中，Local x2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.debug("当前实际核数：{}".format(Local_Apic_ID))
        logging.info('在apic文件中，Local x2APIC个数与当前CPU总线程数一致')

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PRO_CFG, 20, Msg.EXTENDED_APIC)
        assert SetUpLib.locate_option(Key.DOWN, Extended_APIC2, 20)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        Local_Apic = _acpidump()[0].split('Raw Table Data')[0].count('Processor Local APIC')
        assert Local_Apic_ID == SutConfig.SysCfg.CPU_CNT*56, '在apic文件中，Local x2APIC个数与当前CPU总线程数不一致，需要检查'
        logging.debug("当前实际核数：{}".format(Local_Apic))
        logging.info('在apic文件中，Local APIC个数与当前CPU总线程数一致')

        SshLib.execute_command(Sut.OS_SSH, r'rm *.dat *.out *.dsl')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# function Module  for cpu_compa_011:
def _cpu_compa_pc6():
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
    SshLib.execute_command(Sut.OS_SSH, r'timeout 15s turbostat --show Pkg%pc6 > tc220.txt')
    res = SshLib.execute_command(Sut.OS_SSH, r'cat tc220.txt').replace('Pkg%pc6/n', '')
    if '0.00' not in res:
        logging.info('**set C6 --- Pkg%pc6 test pass')
        return True
    else:
        logging.info('**set C6 ---Pkg%pc6 test  fail')
        return False


# Author: Fubaolin
# Package C-state特性测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_011():
    tc = ('220', '[TC220] Testcase_CPU_COMPA_011', 'Package C-state特性测试')
    result = ReportGen.LogHeaderResult(tc)
    MONI_MWAIT_DIS = ['MONITOR\/MWAIT', '<Disabled>']
    CPU_C6_RPT_DIS = ['CPU C6 Report', '<Disabled>']
    EHS_C1E_DIS = ['Enhanced Halt State \(C1E\)', '<Disabled>']
    EHS_C1E_ENABLE = ['Enhanced Halt State \(C1E\)', '<Enabled>']
    try:
        # 前置条件
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.locate_option(Key.DOWN, MONI_MWAIT_DIS, 10)
        SetUpLib.send_key(Key.F5)
        assert SetUpLib.locate_option(Key.DOWN, CPU_C6_RPT_DIS, 10)
        SetUpLib.send_key(Key.F5)

        # 设置 C1E=Enable,Package C State Control=Auto， 进os验证 PC6状态
        assert SetUpLib.locate_option(Key.DOWN, EHS_C1E_DIS, 5)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)
        logging.info('第1次验证pc6状态 ')
        assert _cpu_compa_pc6(), "**C1E=Enable,Package_C_State =Auto fail"

        # 设置 C1E=Enable,Package C State Control=c6， 进os验证 PC6状态
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PCSC_CTL, 20, Msg.PKG_C_STATE_CONTROL)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        logging.info('第2次验证pc6状态 ')
        assert _cpu_compa_pc6(), "**C1E=Enable,Package_C_State =C6 fail"

        # 设置 C1E=Disable,Package_C_State_Control=C6 进os验证 PC6状态
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.locate_option(Key.DOWN, EHS_C1E_ENABLE, 5)
        SetUpLib.send_keys([Key.F6, Key.F10, Key.Y], 3)
        logging.info('第3次验证pc6状态 ')
        assert _cpu_compa_pc6(), "**C1E=Disable,Package_C_State =C6 fail"

        # 设置 C1E=Disable, package C State =Auto ,进os验证 PC6状态
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PCSC_CTL, 20, Msg.PKG_C_STATE_CONTROL)
        SetUpLib.send_keys([Key.F5, Key.F10, Key.Y], 3)
        logging.info('第4次验证pc6状态 ')
        assert _cpu_compa_pc6(), "**C1E=Disable,Package_C_State =Auto fail"
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
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
def _set_core_redfish(tc, set_data, exp_data):  # this def used to set cpu cores via redfish,
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
        BmcLib.force_reset()
        assert SetUpLib.continue_to_page(Msg.CPU_CONFIG)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, Msg.PROCESSOR_CONFIG], 12, Msg.PER_CPU)
        # 根据平台实际cpu核数，设定 set_data 数值
        if set_data == 0 or set_data >29:
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


# Testcase_SP_Boot_010 redfish change SP boot
# Author: OuYang
# Precondition:Postman工具已安装
# 1、Redfish带外关闭SP Boot选项；
# 2、重启X86进Setup菜单，检查SP Boot选项状态，与设置值一致；
# 3、Redfish带外打开SP Boot选项；
# 4、重启X86进Setup菜单，检查SP Boot选项状态，与设置值一致；
# OnStart:
# OnComplete: SetUp
@core.test_case(('228', '[TC228] redfish change SP boot', 'verify redfish change SP boot success'))
def testcase_sp_boot_010():
    logging.info("[BmcLib] Set SP boot with redfish.")
    SP_OPTION_REDFISH = ['Disabled', 'Enabled']
    try:
        for i in range(2):
            assert BmcLib.force_reset()
            assert Sut.BMC_RFISH.set_bios_option(
                **{'SPBoot': SP_OPTION_REDFISH[i]}).status == 200, 'status != ok, result is False'
            logging.info("redfish设置SP boot为 '{0}' 成功".format(SP_OPTION_REDFISH[i]))
            assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
            assert SetUpLib.get_option_value(["SP Boot", "<.+>"], Key.UP, 10) == SP_OPTION_REDFISH[i]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)


def testcase_coreDisable_009():
    tc = ('223', '[TC223] 09 redfish带外使能1个CPU核数测试', '支持CPU关核')
    return _set_core_redfish(tc, 1, 200)


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
    return _set_core_redfish(tc, 27, 200)


# Testcase_CoreDisable_011
# Precondition: register.json文件具体Get路径参考：'1、Postman工具已正确安装
# /redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v5_1_5.json
# OnStart: 'UEFI'模式
# Steps:
# '1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":n（n为超过当前CPU支持的最大核数），有结果A；
#  2、重启X86进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
#  A：n<=28时命令下发正常，无报错；n>28时报错，下发失败。 max is 28,
#  B：CPU使能核数显示为ALL。
# OnCompleted: SETUP
def testcase_coreDisable_011():
    tc = ('225', '[TC225] 11 redfish带外使能CPU核数超过最大值测试', '支持CPU关核')
    return _set_core_redfish(tc, 44, 400)


# 1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":0，有结果A；
def testcase_coreDisable_012():
    tc = ('226', '[TC226] 12 redfish带外使能CPU核数为0测试', '支持CPU关核')
    return _set_core_redfish(tc, 0, 400)


# Author: Fubaolin
# cpu锁频测试
# Precondition:linux-OS, stress tools install  
# OnStart:
# Set:
# 1、进入Setup关闭EIST(P-State)，关闭C-State（默认关闭），F10保存重启；
# 2、进入系统，查看CPU核的运行频率，有结果A；
# 3、使用Stress工具对所有CPU加压，检查所有CPU核运行频率，有结果A。
# A：所有核运行在标称频率。
@core.test_case(('229', '[TC229] Testcase_CPU_COMPA_004', 'CPU锁频测试'))
def Cpu_Lock_Frequency():
    speed_step = ['SpeedStep \(Pstates\)', '<Enabled>']
    MONI_MWAIT_DIS = ['MONITOR\/MWAIT', '<Disabled>']
    c_state = ['C\-State OS Indicator', '<Disabled>']
    stress_command = f"stress --cpu 56 --timeout 20"
    get_cpu_para = "timeout 10 turbostat| awk -F' ' '{print $1,$2,$7}'"
    succe_flag = "successful run completed"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.locate_option(Key.DOWN, speed_step, 10)
        assert SetUpLib.set_option_value(str(speed_step[0]),'Disabled', Key.DOWN), '**close EIST(P-State)--> fail'
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.locate_option(Key.DOWN, MONI_MWAIT_DIS, 10)
        assert SetUpLib.set_option_value(str(MONI_MWAIT_DIS[0]),'Enabled', Key.DOWN), '**Enabled MONITOR--> fail'
        assert SetUpLib.verify_info(c_state, 10), '**C-State check--> fail'
        SetUpLib.send_keys(Key.SAVE_RESET, 2)
        cpu_fre = _cpu_stress_tool(stress_command, get_cpu_para, succe_flag)
        assert cpu_fre is not None, '**check stress_tool in linux_OS and path'
        logging.debug(cpu_fre)
        sta_flg = 0
        for i in cpu_fre.split('\n')[3:-2]:
            if not min_cpu_base <= int(i.split()[2]) <= max_cpu_base:
                logging.debug('** No. {0}_cpu_{1} core, frequency = {2}'.format(i.split()[0], i.split()[1], i.split()[2]))
                sta_flg += 1
        assert sta_flg == 0, '**Get frequency after pressurize--check fail'
        logging.info("**Get frequency after pressurize--check pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

# Author: Fubaolin
# C-state特性测试
# Precondition:linux-OS, stress tools install
# OnStart:
# Set:
# 1、进入Setup菜单CPU C-State Control页面下查看MWAIT、C6 Report、C1E默认状态，有结果A；
# 2、Enable MWAIT、C6 Report后F10进入OS，空载时查看所有CPU核C状态；给所有CPU核加压后查看C状态，有结果B；
# 3、进入Setup菜单Disable MWAIT、C6 Report，F10保存重启；
# 4、进入OS，空载时查看所有CPU核C状态；给所有CPU核加压后查看C状态，有结果C；
# 5、进入Setup菜单Enable C1E，F10保存重启；
# 6、进入OS，空载时查看所有CPU核C状态；给所有CPU核加压后查看C状态，有结果C。
# A：MWAIT、C6 Report、C1E默认关闭；
# B：空闲时进入到C6，加压后进入到C0；
# C：空闲时进入到C1，加压后进入到C0。
@core.test_case(('230', '[TC230] Testcase_CPU_COMPA_007', 'C-state特性测试'))
def Cpu_c_State():
    moni_mwait_dis = ['MONITOR\/MWAIT', '<Disabled>']
    moni_mwait_Ena = ['MONITOR\/MWAIT', '<Enabled>']
    cpu_c6 = ['CPU C6 Report', '<Disabled>']
    cpu_c6_Ena = ['CPU C6 Report', '<Enabled>']
    c1e = ['Enhanced Halt State \(C1E\)', '<Disabled>']
    stress_command = f"stress --cpu 56 --timeout 60"
    get_cpu_c6 = "timeout 10 turbostat -q| awk -F' ' '{print $1,$2,$17,$21}'"
    get_cpu_c0 = "timeout 10 turbostat -q| awk -F' ' '{print $5}'"
    get_cpu_c1 = "timeout 10 turbostat -q| awk -F' ' '{print $10}'"
    flag_c6 = "Pkg%pc6" and "CPU%c6"
    flag_c0 = 'Busy%'
    flag_c1 = 'CPU%c1'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.locate_option(Key.UP, moni_mwait_dis, 10)
        assert SetUpLib.set_option_value(str(moni_mwait_dis[0]), 'Enabled', Key.DOWN), '**Enabled MONITOR--> fail'
        assert SetUpLib.locate_option(Key.DOWN, cpu_c6, 10)
        assert SetUpLib.set_option_value(str(cpu_c6[0]), 'Enabled', Key.DOWN), '**Enabled MONITOR--> fail'
        SetUpLib.send_keys(Key.SAVE_RESET, 2)
        # 空载时,CPU进入到C6
        assert _cpu_to_c6(get_cpu_c6, flag_c6)
        #加压后，cpu进入C0
        assert _cpu_to_c0(stress_command, get_cpu_c0, flag_c0)

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.locate_option(Key.UP, moni_mwait_Ena, 10)
        assert SetUpLib.set_option_value(str(moni_mwait_Ena[0]), 'Disabled', Key.DOWN), '**Disabled MONITOR--> fail'
        assert SetUpLib.locate_option(Key.DOWN, cpu_c6_Ena, 10)
        assert SetUpLib.set_option_value(str(cpu_c6_Ena[0]), 'Disabled', Key.DOWN), '**Disabled MONITOR--> fail'
        SetUpLib.send_keys(Key.SAVE_RESET, 2)
        # 空闲时进入到C1，
        assert _cpu_to_c1(get_cpu_c1, flag_c1)
        # 加压后进入到C0
        assert _cpu_to_c0(stress_command, get_cpu_c0, flag_c0)

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.locate_option(Key.DOWN, c1e, 10)
        assert SetUpLib.set_option_value(str(c1e[0]), 'Enabled', Key.DOWN), '**Enabled C1e--> fail'
        SetUpLib.send_keys(Key.SAVE_RESET, 2)
        # 空闲时进入到C1，
        assert _cpu_to_c1(get_cpu_c1, flag_c1)
        # 加压后进入到C0
        assert _cpu_to_c0(stress_command, get_cpu_c0, flag_c0)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# EIST特性测试
# Precondition:linux-OS, stress tools install
# OnStart:
# Set:
# 1、进入Setup，在CPU P-State Control界面Enable EIST(P-state)；
# 2、重启进入OS，空闲状态下查看CPU核的当前频率，有结果A；
# 3、使用stress工具给指定CPU加压，查看CPU运行频率，有结果B；
# 4、重启系统，进入Setup，关闭EIST功能，F10后进入OS。空闲状态下查看CPU核的当前频率，有结果C；
# 5、使用stress工具给指定CPU加压，查看CPU运行频率，有结果C。
# A：CPU核运行在最低频率；
# B：加压的核运行在标称频率，未加压核运行在最低频率；
# C：所有核均运行在标称频率。
@core.test_case(('231', '[TC231] Testcase_CPU_COMPA_012', 'EIST特性测试'))
def eist_features_test():
    get_cpu_para = "timeout 10 turbostat -q| awk -F' ' '{print $1,$2,$6}'"
    pressure = int((SutConfig.SysCfg.CPU_CNT*SutConfig.SysCfg.CPU_CORES)*0.5-1)  # core序号，从0起始
    # 加压的核数，cpu数量 乘 每个cpu的核数 乘 0.5
    pressure_num = int((SutConfig.SysCfg.CPU_CNT*SutConfig.SysCfg.CPU_CORES)*0.5)
    # 给序号0~{（cpu数量x核数）1/2-1}的[（cpu数量x核数）1/2 ]个核加压
    stress_command = "taskset -c 0-{} stress -c {} --timeout 80".format(pressure, pressure_num)
    succe_flag = 'Bzy_MHz'
    fail_count = 0
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value('Turbo Mode', 'Disabled', save=True), '**Disabled turbo_mode--> fail'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_fre_min = SshLib.execute_command(Sut.OS_SSH, "sleep 60s;{}".format(get_cpu_para))
        logging.debug(cpu_fre_min)
        assert succe_flag in cpu_fre_min.split('\n')[0], "获取Cpu频率 --> fail"
        assert int(cpu_fre_min.split('\n')[1].split()[2]) < int(SutConfig.SysCfg.CPU_BASE*1000), "**空闲状态cpu频率 --> fail"
        cpu_fre = _cpu_stress_tool(stress_command, "sleep 60s;{}".format(get_cpu_para), succe_flag)
        assert cpu_fre is not None, '**check stress_tool in linux_OS and path'
        logging.debug(cpu_fre)
        num = int((len(cpu_fre.split('\n')[3:-2]))/2)   # 全部核数对半分成2份（加压，未加压）
        cpu_1 = cpu_fre.split('\n')[3:num+3]  # 加压核ist
        cpu_2 = cpu_fre.split('\n')[num+3:-2]  # 未加压核list
        for i in cpu_1:  # 获取加压的核（总核数前一半）频率
            if not min_cpu_base < int(i.split()[2]) < max_cpu_base:   # 加压的核，频率>标准频率
                logging.warning("**加压的核运行在标称频率, {0} core实际读取频率 = {1}".format(i.split()[1], i.split()[2]))
                fail_count += 1
        assert fail_count == 0, 'fail count num -> {0}'.format(fail_count)
        for j in cpu_2:  # 获取未加压的核（总核数后一半）频率
            if not int(lowest_frequency)-int(SutConfig.SysCfg.CPU_BASE*1000*0.1) < \
                int(j.split()[2]) <= max_cpu_base:   # 未加压的核，频率<=标准频率
                logging.warning("**未加压核运行在最低频率, {0} core实际读取频率 = {1}".format(j.split()[1], j.split()[2]))
                fail_count += 1
        assert fail_count == 0, 'fail count num -> {0}'.format(fail_count)
        # disabled eist func,
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value('SpeedStep \(Pstates\)', 'Disabled', save=True), '**Disabled eist--> fail'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_fre_min = SshLib.execute_command(Sut.OS_SSH, "sleep 60s;{}".format(get_cpu_para))
        logging.debug(cpu_fre_min)
        assert succe_flag in cpu_fre_min.split('\n')[0], "获取Cpu频率 --> fail"
        assert int(cpu_fre_min.split('\n')[1].split()[2]) < int(SutConfig.SysCfg.CPU_BASE*1000)+\
               int(SutConfig.SysCfg.CPU_BASE*1000*0.1), "**空闲状态cpu频率 --> fail"
        cpu_fre_2 = _cpu_stress_tool(stress_command, "sleep 40s;{}".format(get_cpu_para), succe_flag)
        assert cpu_fre_2 is not None, '**check stress_tool in linux_OS and path'
        logging.debug(cpu_fre_2)
        cpu_3 = cpu_fre_2.split('\n')[3:num + 3]  # 加压核ist
        cpu_4 = cpu_fre_2.split('\n')[num + 3:-2]  # 未加压核list
        for k in cpu_3:  # 获取加压的核（总核数前一半）频率
            if not max_cpu_base> int(k.split()[2]) > min_cpu_base:   # 加压的核，频率在标准频率附近振荡
                logging.warning("**加压的核，频率在标准频率附近振荡, {0} core实际读取频率 = {1}".format(k.split()[1], k.split()[2]))
                fail_count += 1
        assert fail_count == 0, 'fail count num -> {0}'.format(fail_count)
        for m in cpu_4:  # 获取未加压的核（总核数后一半）频率
            if not max_cpu_base > int(m.split()[2]) > min_cpu_base:   # 未加压的核，频率在标准频率附近振荡
                logging.warning("**未加压的核，频率在标准频率附近振荡, {0} core实际读取频率 = {1}".format(m.split()[1], m.split()[2]))
                fail_count += 1
        # if failed, check the warning msg in test log,
        assert fail_count == 0, 'fail count num -> {0}'.format(fail_count)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# Turbo Mode特性测试
# Precondition:linux-OS, stress tools install
# OnStart:
# Set:
# 1、进入OS，使用stress工具给CPU某个核加压，使用turbostat工具查询CPU运行频率，有结果A；
# 2、覆盖CPU0和CPU1下多个核，重复步骤1；
# 3、重启进入Setup菜单，关闭TurboMode，保存退出；
# 4、重复步骤1-2，有结果B。
# A：CPU运行频率达到规格超频后的最大值；
# B：CPU运行频率达到规格标称值。
@core.test_case(('232', '[TC232] Testcase_CPU_COMPA_012', 'Turbo Mode特性测试'))
def turbo_mode_test():
    get_cpu_para = "sleep 40s;timeout 10 turbostat -q| awk -F' ' '{print $1,$2,$6}'"
    single_command = "taskset -c 10 stress -c 28 --timeout 60"
    more_command = "taskset -c 23-32 stress -c 28 --timeout 60" 
    succe_flag = 'Bzy_MHz'
    error_flag = 0
    min_cpu_turbo = int(SutConfig.SysCfg.CPU_TURBO * 1000) - int(SutConfig.SysCfg.CPU_BASE * 1000 * 0.1)
    max_cpu_turbo = int(SutConfig.SysCfg.CPU_TURBO * 1000) + int(SutConfig.SysCfg.CPU_BASE * 1000 * 0.1)
    min_cpu_base = int(SutConfig.SysCfg.CPU_BASE * 1000) - int(SutConfig.SysCfg.CPU_BASE * 1000 * 0.1)
    max_cpu_base = int(SutConfig.SysCfg.CPU_BASE * 1000) + int(SutConfig.SysCfg.CPU_BASE * 1000 * 0.1)
    try:
        # 默认 TurboMode_Enable
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        # 指定core 加压，并查询CPU运行频率
        cpu_fre_single = _cpu_stress_tool(single_command, get_cpu_para, succe_flag)
        assert cpu_fre_single is not None, '**check stress_tool in linux_OS command'
        logging.debug(cpu_fre_single)
        cpu_10 = cpu_fre_single.split('\n')[23:25]  # 获取指定No.10_core 加压频率
        for i in cpu_10:
            if not min_cpu_turbo < int(i.split()[2]) < max_cpu_turbo:   # "**单个core加压状态 cpu频率"
                error_flag += 1
        assert error_flag == 0, 'fail count num -> {}'.format(error_flag)
        # # 覆盖CPU0和CPU1下多个核
        cpu_fre_more = _cpu_stress_tool(more_command, get_cpu_para, succe_flag)
        assert cpu_fre_more is not None, '**check stress_tool in linux_OS command'
        logging.debug(cpu_fre_more)
        cpu_more = cpu_fre_more.split('\n')[49:69]  # 获取more_core 加压频率
        for j in cpu_more:
            if not min_cpu_turbo < int(j.split()[2]) < max_cpu_turbo:   # "**多个core加压状态 cpu频率"
                error_flag += 1
        assert error_flag == 0, 'fail count num -> {0}'.format(error_flag)
        # 修改 TurboMode_Disabled
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value('Turbo Mode', 'Disabled', save=True), '**Disabled eist--> fail'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        # 指定core 加压，并查询CPU运行频率
        cpu_fre_single_2 = _cpu_stress_tool(single_command, get_cpu_para, succe_flag)
        assert cpu_fre_single_2 is not None, '**check stress_tool in linux_OS command'
        logging.debug(cpu_fre_single_2)
        cpu_10_2 = cpu_fre_single_2.split('\n')[23:25]  # 获取指定No.10_core 加压频率
        for k in cpu_10_2:
            if not min_cpu_base < int(k.split()[2]) < max_cpu_base:   # "**单个core加压状态 cpu频率"
                error_flag += 1
        assert error_flag == 0, 'fail count num -> {0}'.format(error_flag)
        # 覆盖CPU0和CPU1下多个核
        cpu_fre_more_2 = _cpu_stress_tool(more_command, get_cpu_para, succe_flag)
        assert cpu_fre_more_2 is not None, '**check stress_tool in linux_OS command'
        logging.debug(cpu_fre_more_2)
        cpu_more_2 = cpu_fre_more_2.split('\n')[49:69]  # 获取more_core 加压频率
        for m in cpu_more_2:
            if not min_cpu_base < int(m.split()[2]) < max_cpu_base:   # "**多个core加压状态 cpu频率"
                error_flag += 1
        assert error_flag == 0, 'fail count num -> {0}'.format(error_flag)
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

# Testcase_BootFailPolicy_012 redfish change BootFailPolicy
# Author: OuYang
# Precondition:Postman工具已安装
# 1、通过Redfish获取BIOS的Current和Registry文件信息，有结果A；
# 2、带外配置Boot Fail Policy选项，重启系统，进入Setup菜单查看设置是否生效，有结果B。
# A：带外配置已添加新增菜单项；
# B：带外配置可以生效。
# OnStart:
# OnComplete: SetUp
@core.test_case(('233', '[TC233] redfish change BootFailPolicy', 'verify redfish change BootFailPolicy success'))
def testcase_BootFailPolicy_012():
    logging.info("[BmcLib] Set BootFailPolicy with redfish.")
    BOOT_FAIL_POLICY_REDFISH = ['None', 'Cold Boot', 'Boot Retry']
    try:
        for i in range(len(BOOT_FAIL_POLICY_REDFISH)):
            assert BmcLib.force_reset()
            assert Sut.BMC_RFISH.set_bios_option(
                **{'BootFailPolicy': BOOT_FAIL_POLICY_REDFISH[i]}).status == 200, 'status != ok, result is False'
            logging.info("redfish设置BootFailPolicy为 '{0}' 成功".format(BOOT_FAIL_POLICY_REDFISH[i]))
            assert SetUpLib.continue_to_page(Msg.PAGE_BOOT)
            logging.info(BOOT_FAIL_POLICY_REDFISH[i])
            assert SetUpLib.get_option_value(["Boot Fail Policy", "<.+>"], Key.DOWN, 15) == BOOT_FAIL_POLICY_REDFISH[i]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
