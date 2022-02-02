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
def cpu_cores_active_enable(num):
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
        assert ['32', str(num), str(num * 2)] == res_lst, '**Core or Thread err:{0}**'.format(res_lst)
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
    ufs = ['UFS', Msg.ENABLED_VAL]

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
    static_turbo_default = ['Static Turbo', Msg.DISABLED_VAL]
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
    try:
        assert cpu_cores_active_enable(1)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_cpu_setting(BiosCfg.ActiveCpuCores_Default)


def cpu_cores_active_enable_middle():
    tc = ('206', '[TC206] Testcase_CoreDisable_003', 'Enable middle-num CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert cpu_cores_active_enable(16)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)
    finally:
        reset_cpu_setting(BiosCfg.ActiveCpuCores_Default)


def cpu_cores_active_enable_max():
    tc = ('207', '[TC207] Testcase_CoreDisable_004', 'Enable max-1 CPU core test')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert cpu_cores_active_enable(31)
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
    numa_bef = ['NUMA', Msg.ENABLED_VAL]
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
    numa_aft = ['NUMA', Msg.DISABLED_VAL]
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
                    continue
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
    mic_rev = 'Microcode Revision\s+0D000311'
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
    # pro_fre = [SutConfig.SysCfg.CPU_INFO[2]]
    # pro_ver = SutConfig.SysCfg.CPU_INFO[-2:]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PER_CPU_INFO, 20, Msg.PER_CPU)
        assert SetUpLib.verify_info(SutConfig.SysCfg.CPU_INFO, 20)
        assert BmcLib.force_reset()
        # 在smbios4中检查：cpu型号，频率，个数
        res = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Version:"')
        assert 'CPU' in res, 'res return err'
        cpu_version = res.replace('\n', '').split(':')[-1].strip()
        assert cpu_version == 'Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz', 'cpu_version test failed'
        cpu_num = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | grep "Socket Designation:"')
        assert 'CPU01' and 'CPU02' in cpu_num, 'cpu num test failed'
        result.log_pass()
        return True
    except Exception as err:
        logging.error(err)
        result.log_fail()


# Author: Fubaolin
# X2APIC选项测试
# Precondition: linux-OS
# OnStart: NA
# OnComplete: NA
def cpu_compa_017():
    tc = ('215', '[TC215] Testcase_CPU_COMPA_017', 'X2APIC选项测试')
    result = ReportGen.LogHeaderResult(tc)
    Extended_APIC = ['Extended APIC', Msg.DISABLED_VAL]
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
@core.test_case(('227', '[TC227] cpu_compa_024', 'OS下X2APIC开关状态测试'))
def cpu_compa_024():
    Extended_APIC = ['Extended APIC', Msg.DISABLED_VAL]
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
        assert SetUpLib.set_option_value('Extended APIC', Msg.ENABLED, save=True)
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
    return set_core_redfish(tc, 31, 200)


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
    return set_core_redfish(tc, 44, 400)


# 1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":0，有结果A；
def testcase_coreDisable_012():
    tc = ('226', '[TC226] 12 redfish带外使能CPU核数为0测试', '支持CPU关核')
    return set_core_redfish(tc, 0, 400)


# cpu锁频测试,
std_freq = int(eval('{0} * 1000'.format(SutConfig.SysCfg.CPU_FREQ)))  # 标准频率


def cpu_stress_tool(command1, command2, succe_flag):
    assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
    get_cpu = SshLib.execute_command(Sut.OS_SSH, f"{command1} & {command2}")
    if succe_flag not in get_cpu:
        logging.debug('** check linux_command ')
        return
    return get_cpu


def cpu_to_c6(command1, flag_c6):
    try:
        # 空载时,CPU进入到C6
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_c6 = SshLib.execute_command(Sut.OS_SSH, command1)
        assert cpu_c6 is not None and flag_c6 in cpu_c6, '** linux_OS command --> fail'
        logging.debug(cpu_c6)
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


def cpu_to_c0(command1, command2, succ_flag):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_c0 = cpu_stress_tool(command1, command2, succ_flag)
        assert cpu_c0 is not None, '** linux_OS command --> fail'
        logging.debug(cpu_c0)
        assert float(cpu_c0.split('\n')[2].strip()) > 45, '**加载时进入C0 --> fail'
        logging.info('加压后 C0 --- pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


def cpu_to_c1(command1, flag_c1):
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_c1 = SshLib.execute_command(Sut.OS_SSH, command1)
        assert cpu_c1 is not None and flag_c1 in cpu_c1, '** linux_OS command --> fail'
        logging.debug(cpu_c1)
        assert float(cpu_c1.split('\n')[2].strip()) > 95, '**空闲时进入C1 --> fail'
        logging.info('空闲时 C1 --- pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


# Precondition:linux-OS, stress tools install
# OnStart:
# 1、进入Setup关闭EIST(P-State)，关闭C-State（默认关闭），F10保存重启；
# 2、进入系统，查看CPU核的运行频率，有结果A；
# 3、使用Stress工具对所有CPU加压，检查所有CPU核运行频率，有结果A。
# A：所有核运行在标称频率。
@core.test_case(('229', '[TC229] Testcase_CPU_COMPA_004', 'CPU锁频测试'))
def Cpu_Lock_Frequency():
    stress_command = "stress --cpu {0} --timeout 20".format(SutConfig.SysCfg.CPU_CORE)
    get_cpu_para = "timeout 10 turbostat| awk -F' ' '{print $1,$2,$7}'"
    succe_flag = "successful run completed"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value('SpeedStep \(Pstates\)', Msg.DISABLED), '**close EIST(P-State)--> fail'
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_CSTATE_CTL, 20, Msg.CPU_C_STATE)
        assert SetUpLib.set_option_value('MONITOR\/MWAIT', Msg.ENABLED, save=True), '**Enabled MONITOR--> fail'
        assert SetUpLib.verify_info(['C\-State OS Indicator', Msg.DISABLED_VAL], 10), '**C-State check--> fail'
        cpu_fre = cpu_stress_tool(stress_command, get_cpu_para, succe_flag)
        assert cpu_fre is not None, '**check stress_tool in linux_OS and path'
        logging.debug(cpu_fre)
        sta_flg = 0
        for i in cpu_fre.split('\n')[3:-2]:
            if int(i.split()[2]) != int(eval('{0} * 1000'.format(SutConfig.SysCfg.CPU_FREQ))):
                logging.debug(
                    '** No. {0}_cpu_{1} core, frequency = {2}'.format(i.split()[0], i.split()[1], i.split()[2]))
                sta_flg += 1
        assert sta_flg == 0, '**Get frequency after pressurize--check fail'
        logging.info("**Get frequency after pressurize--check pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# EIST特性测试
# Precondition:linux-OS, stress tools install
# OnStart:
# Steps:
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
    get_cpu_para = "sleep 40s;timeout 10 turbostat -q| awk -F' ' '{print $1,$2,$6}'"
    pressure = int((SutConfig.SysCfg.CPU_CNT*SutConfig.SysCfg.CPU_CORE)*0.5-1)  # core序号，从0起始
    # 加压的核数，cpu数量 乘 每个cpu的核数 乘 0.5
    pressure_num = int((SutConfig.SysCfg.CPU_CNT*SutConfig.SysCfg.CPU_CORE)*0.5)
    # 给序号0~{（cpu数量x核数）1/2-1}的[（cpu数量x核数）1/2 ]个核加压
    stress_command = "taskset -c 0-{} stress -c {} --timeout 60".format(pressure, pressure_num)
    succe_flag = 'Bzy_MHz'
    standard_frequency = 2200   # 标准频率
    lowest_frequency = 800  # 最低频率
    fail_count = 0
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value('Turbo Mode', Msg.DISABLED, save=True), '**Disabled turbo_mode--> fail'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_fre_min = SshLib.execute_command(Sut.OS_SSH, get_cpu_para)
        logging.debug(cpu_fre_min)
        assert succe_flag in cpu_fre_min.split('\n')[0], "获取Cpu频率 --> fail"
        assert int(cpu_fre_min.split('\n')[1].split()[2]) < int(standard_frequency*0.5), "**空闲状态cpu频率 --> fail"
        cpu_fre = cpu_stress_tool(stress_command, get_cpu_para, succe_flag)
        assert cpu_fre is not None, '**check stress_tool in linux_OS and path'
        logging.debug(cpu_fre)
        num = int((len(cpu_fre.split('\n')[3:-2]))/2)   # 全部核数对半分成2份（加压，未加压）
        cpu_1 = cpu_fre.split('\n')[3:num+3]  # 加压核ist
        cpu_2 = cpu_fre.split('\n')[num+3:-2]  # 未加压核list
        for i in cpu_1:  # 获取加压的核（总核数前一半）频率
            if not standard_frequency-100 < int(i.split()[2]) < standard_frequency+100:   # 加压的核，频率>标准频率
                logging.warning("**加压的核运行在标称频率, {0} core实际读取频率 = {1}".format(i.split()[1], i.split()[2]))
                fail_count += 1
        for j in cpu_2:  # 获取未加压的核（总核数后一半）频率
            if not lowest_frequency-100 < int(j.split()[2]) <= standard_frequency:   # 未加压的核，频率<=标准频率
                logging.warning("**未加压核运行在最低频率, {0} core实际读取频率 = {1}".format(j.split()[1], j.split()[2]))
                fail_count += 1
        # disabled eist func,
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value('SpeedStep \(Pstates\)', Msg.DISABLED, save=True), '**Disabled eist--> fail'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        SshLib.execute_command(Sut.OS_SSH, f"cpupower frequency-set -g ondemand")  # 关闭OS自动调频功能避免OS能效策略影响
        cpu_fre_min = SshLib.execute_command(Sut.OS_SSH, get_cpu_para)
        logging.debug(cpu_fre_min)
        assert succe_flag in cpu_fre_min.split('\n')[0], "获取Cpu频率 --> fail"
        assert int(cpu_fre_min.split('\n')[1].split()[2]) < standard_frequency+100, "**空闲状态cpu频率 --> fail"
        cpu_fre_2 = cpu_stress_tool(stress_command, get_cpu_para, succe_flag)
        assert cpu_fre_2 is not None, '**check stress_tool in linux_OS and path'
        logging.debug(cpu_fre)
        cpu_3 = cpu_fre_2.split('\n')[3:num+3]  # 加压核ist
        cpu_4 = cpu_fre_2.split('\n')[num + 3:-2]  # 未加压核list
        for k in cpu_3:  # 获取加压的核（总核数前一半）频率
            if not standard_frequency+100 > int(k.split()[2]) > standard_frequency-100:   # 加压的核，频率在标准频率附近振荡
                logging.warning("**加压的核，频率在标准频率附近振荡, {0} core实际读取频率 = {1}".format(k.split()[1], k.split()[2]))
                fail_count += 1
        for m in cpu_4:  # 获取未加压的核（总核数后一半）频率
            if not standard_frequency+100 > int(m.split()[2]) > standard_frequency-100:   # 未加压的核，频率在标准频率附近振荡
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
