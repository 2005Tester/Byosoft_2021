from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Cpu Test Case
# TC 1000-1048
####################################


NUMA_CMD = r'numactl -H'


#  function Module
def _numa_disabled_verify():  # 进入 Numa page，设置 Numa 为 Disabled,到 OS中验证
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_COMM, Key.DOWN, 20, confirm_msg=Msg.NUMA)
        assert SetUpLib.set_option_value(Msg.NUMA, Msg.DISABLE, Key.UP, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return True
    except AssertionError:
        return False


def _numa_enabled_verify():  # 进入 Numa page，设置 Numa 为 Enabled，到 OS中验证
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_COMM, Key.DOWN, 20, confirm_msg=Msg.NUMA)
        assert SetUpLib.set_option_value(Msg.NUMA, Msg.ENABLE, Key.UP, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return True
    except AssertionError:
        return False


def _disable_x2apic():
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN)
    assert SetUpLib.set_option_value(Msg.EXTENDED_APIC, Msg.DISABLE, save=False)
    assert SetUpLib.back_to_setup_toppage()
    return True


def _cpu_cores_active_enable(num):
    res_lst = []  # restore the res result
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        if num == SutConfig.Sys.CPU_CORES:
            num = 'All'
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, '{0}'.format(num), save=True)
        logging.info("Core counts changed to {0}, save and reboot.".format(num))
        assert SetUpLib.continue_to_os_from_bm()
        # 每个CPU下只有num个core。
        res = SshLib.execute_command(Sut.OS_SSH, r'lscpu | grep "per socket"')
        res1 = res.replace('\n', '').split(':')[-1].strip()
        if num == 'All':
            num = SutConfig.Sys.CPU_CORES
        assert int(res1) == num, ("**Core Enable error = {}".format(res1))
        # 在smbios4中检查：Core数量为总数，Core Enable为num，线程数为Core核数的两倍 #
        res2 = SshLib.execute_command(Sut.OS_SSH, r'dmidecode -t 4 | egrep -m 3 "Core Count|Core Enabled|Thread Count"')
        Core_Count = res2.splitlines()[0].split(':')[-1].strip()
        Core_Enabled = res2.splitlines()[1].split(':')[-1].strip()
        Thread_Count = res2.splitlines()[2].split(':')[-1].strip()
        res_lst.extend([Core_Count, Core_Enabled, Thread_Count])
        assert [str(SutConfig.Sys.CPU_CORES), str(num), str(SutConfig.Sys.CPU_CORES * 2)] == res_lst, \
            '**Core or Thread err:{0}**'.format(res_lst)
        logging.info('All check pass')
        return True
    except Exception as e:
        logging.error(e)
        return False


def _check_acpi_dsl_result(tmp_data):
    acpi_id = 'Processor x2Apic ID : '
    apic_ids = []
    try:
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        _acpi_date = PlatMisc.get_acpi_table_linux('apic').split('Raw Table Data')[0]
        assert _acpi_date, "dump ACPI-apic table failed"
        for line in _acpi_date.splitlines():
            id_find = re.findall(f'{acpi_id}([0-9a-fA-F]+)', line)
            if id_find:
                apic_ids.append(id_find[0])
                if len(apic_ids) > 2 and (int(apic_ids[-1], 16) != 1):  # 物理核ID在前,虚拟核ID在后
                    assert int(apic_ids[-1], 16) > int(apic_ids[-2], 16), f"ID没有顺序排列: {apic_ids[-1]} < {apic_ids[-2]}" # id正确，顺序排列
        assert len(set(apic_ids)) == len(apic_ids), f"APIC ID有重复: {apic_ids}"  # 没有重复
        if tmp_data == Msg.ENABLE:              # “Local APIC”个数与当前CPU总线程数一致
            assert len(apic_ids) == SutConfig.Sys.CPU_CNT * SutConfig.Sys.CPU_CORES * 2, \
                '**Local_APIC Enable num = {}, pls checkin.'.format(len(apic_ids))
        if tmp_data == Msg.DISABLE:             # “Local APIC”个数与当前CPU核数一致
            assert len(apic_ids) == SutConfig.Sys.CPU_CNT * SutConfig.Sys.CPU_CORES, \
                '**Local_APIC Disable num = {}, pls checkin.'.format(len(apic_ids))
        return True
    except Exception as e:
        logging.info(e)
        return False


@core.test_case(("1000", "[TC1000] Testcase_CpuInitUefi_001", "【UEFI】满配CPU启动测试"))
def Testcase_CpuInitUefi_001():
    """
    Name:       【UEFI】满配CPU启动测试
    Condition:  1、满配CPU。
    Steps:      1、单板上电启动，检查能否正常进入OS，串口是否存在异常打印，有结果A；
                2、进入Setup菜单检查CPU、UPI信息是否正常，有结果B；
                3、进入OS下执行lscpu检查CPU数量及信息是否正确，有结果C。
    Result:     A：能正常启动进OS，无挂死反复重启现象，串口无异常打印；
                B：Setup菜单CPU及UPI信息正常；
                B：OS下CPU数量为实际安装个数，信息准确。
    Remark:
    """
    mem_size_keyword = "Total online memory"
    cpu_type_keyword = "Model name"
    cpu_count_keyword = "Socket"
    try:
        for i in range(1):  # default - 1 loop, should be modified based on test case.
            assert PlatMisc.no_error_at_post()
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PER_CPU_INFO)
        assert SetUpLib.verify_options(SutConfig.Sys.CPU_INFO, integer=None)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_STATUS, Key.DOWN, 20, Msg.UNCORE_STATUS)
        assert SetUpLib.verify_info(SutConfig.Sys.UPI_STATE, 7)
        assert SetUpLib.boot_to_default_os()
        cpu_name_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "^{cpu_type_keyword}"')
        cpu_count_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        mem_size_cmd = SshLib.execute_command(Sut.OS_SSH, f'lsmem |grep "{mem_size_keyword}"')
        assert cpu_name_cmd, f"[{cpu_type_keyword}] not found in lscpu"
        assert cpu_count_cmd, f"[{cpu_count_keyword}] not found in lscpu"
        assert mem_size_cmd, f"[{mem_size_keyword}] not found in lsmem"
        cpu_type = "".join(re.findall(f"{cpu_type_keyword}.*:\s*(.+)", cpu_name_cmd))
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        mem_size = "".join(re.findall(f"{mem_size_keyword}.*:\s*(.+)G", mem_size_cmd))
        check_cpu_os = (SutConfig.Sys.CPU_FULL_NAME == cpu_type)
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_mem_os = (int(mem_size) == SutConfig.Sys.MEM_SIZE)
        assert check_mem_os, f"Check MEM Size fail in OS: {mem_size}"
        assert check_cpu_os, f"Check CPU Name fail in OS: {cpu_type}"
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1001", "[TC1001] Testcase_CpuInitLegacy_001", "【Legacy】满配CPU启动测试"))
@mark_legacy_test
def Testcase_CpuInitLegacy_001():
    """
    Name:       【Legacy】满配CPU启动测试
    Condition:  1、满配CPU。
    Steps:      1、单板上电启动，检查能否正常进入OS，串口是否存在异常打印，有结果A；
                2、进入Setup菜单检查CPU、UPI信息是否正常，有结果B；
                3、进入OS下执行lscpu检查CPU数量及信息是否正确，有结果C。
    Result:     A：能正常启动进OS，无挂死反复重启现象，串口无异常打印；
                B：Setup菜单CPU及UPI信息正常；
                B：OS下CPU数量为实际安装个数，信息准确。
    Remark:
    """
    mem_size_keyword = "Total online memory"
    cpu_type_keyword = "Model name"
    cpu_count_keyword = "Socket"
    try:
        for i in range(1):  # default - 1 loop, should be modified based on test case.
            assert PlatMisc.no_error_at_post()
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PER_CPU_INFO)
        assert SetUpLib.verify_options(SutConfig.Sys.CPU_INFO, integer=None)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_STATUS, Key.DOWN, 20, Msg.UNCORE_STATUS)
        assert SetUpLib.verify_info(SutConfig.Sys.UPI_STATE, 7)
        assert SetUpLib.boot_to_default_os(uefi=False)
        cpu_name_cmd = SshLib.execute_command(Sut.OS_LEGACY_SSH, f'lscpu |grep "^{cpu_type_keyword}"')
        cpu_count_cmd = SshLib.execute_command(Sut.OS_LEGACY_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        mem_size_cmd = SshLib.execute_command(Sut.OS_LEGACY_SSH, f'lsmem |grep "{mem_size_keyword}"')
        assert cpu_name_cmd, f"[{cpu_type_keyword}] not found in lscpu"
        assert cpu_count_cmd, f"[{cpu_count_keyword}] not found in lscpu"
        assert mem_size_cmd, f"[{mem_size_keyword}] not found in lsmem"
        cpu_type = "".join(re.findall(f"{cpu_type_keyword}.*:\s*(.+)", cpu_name_cmd))
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        mem_size = "".join(re.findall(f"{mem_size_keyword}.*:\s*(.+)G", mem_size_cmd))
        check_cpu_os = (SutConfig.Sys.CPU_FULL_NAME == cpu_type)
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_mem_os = (int(mem_size) == SutConfig.Sys.MEM_SIZE)
        assert check_mem_os, f"Check MEM Size fail in OS: {mem_size}"
        assert check_cpu_os, f"Check CPU Name fail in OS: {cpu_type}"
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1002", "[TC1002] Testcase_CoreDisable_001", "关核设置菜单检查"))
def Testcase_CoreDisable_001():
    """
    Name:       关核设置菜单检查
    Condition:  1、已安装Linux系统；
                2、CPU满配。
    Steps:      1、启动进Setup菜单，Processor界面检查是否提供核数设置选项，默认值及可选值，有结果A；
                2、随机设置CPU核数为N，F10保存重启进OS，执行"lscpu"命令查看CPU信息，有结果B；
    Result:     A：提供核数使能开关，范围0~MAX（根据CPU型号自动调整范围）可选，默认为0（选项显示为All）；
                B：CPU数量与实际一致，每个CPU下N个Core。
    Remark:
    """
    cpu_count_keyword = "Socket"
    cpu_core_keywd = "Core"
    exp_val = []
    set_core = Sys.CPU_CORES // 2
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, "<All>"]], Key.DOWN, 7)  # check the default val
        for i in range(1, int(f"{SutConfig.Sys.CPU_CORES}")):
            exp_val.append('{0}'.format(i))
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.ACT_CPU_CORES), exp_val + ['All']), "core check failed"
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{set_core}", save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        cpu_count_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        cpu_core_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_core_keywd}"')
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        cpu_core = "".join(re.findall(f"{cpu_core_keywd}.*:\s*(.+)", cpu_core_cmd))
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_cpu_core = (int(cpu_core) == int(set_core))
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"
        assert check_cpu_core, f"Check CPU Core fail in OS: {cpu_core}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1003", "[TC1003] Testcase_CoreDisable_002", "CPU使能1个核测试"))
def Testcase_CoreDisable_002():
    """
    Name:       CPU使能1个核测试
    Condition:  1、已安装Linux系统；
                2、CPU满配。
    Steps:      1、启动进Setup菜单，Processor界面设置CPU核数为1，F10保存重启；
                2、启动进OS，执行"lscpu"命令查看CPU信息，有结果B；
    Result:     A：CPU数量与实际一致，每个CPU下1个Core。
    Remark:
    """
    cpu_count_keyword = "Socket"
    cpu_core_keywd = "Core"
    set_core = 1
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{set_core}", save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG + [Msg.MEM_TOP], Key.UP, 15, Msg.MEM_TOP)
        assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO, 30)
        assert SetUpLib.boot_to_default_os()
        cpu_count_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        cpu_core_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_core_keywd}"')
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        cpu_core = "".join(re.findall(f"{cpu_core_keywd}.*:\s*(.+)", cpu_core_cmd))
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_cpu_core = (int(cpu_core) == int(set_core))
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"
        assert check_cpu_core, f"Check CPU Core fail in OS: {cpu_core}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1004", "[TC1004] Testcase_CoreDisable_003", "CPU使能MAX-1个核测试"))
def Testcase_CoreDisable_003():
    """
    Name:       CPU使能MAX-1个核测试
    Condition:  1、已安装Linux系统；
                2、CPU满配。
    Steps:      1、启动进Setup菜单，Processor界面设置CPU核数为MAX-1，F10保存重启；
                2、启动进OS，执行"lscpu"命令查看CPU信息，有结果B；
    Result:     A：CPU数量与实际一致，每个CPU下MAX-1个Core。
    Remark:
    """
    cpu_count_keyword = "Socket"
    cpu_core_keywd = "Core"
    set_core = Sys.CPU_CORES - 1
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{set_core}", save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG + [Msg.MEM_TOP], Key.UP, 15, Msg.MEM_TOP)
        assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO, 30)
        assert SetUpLib.boot_to_default_os()
        cpu_count_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        cpu_core_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_core_keywd}"')
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        cpu_core = "".join(re.findall(f"{cpu_core_keywd}.*:\s*(.+)", cpu_core_cmd))
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_cpu_core = (int(cpu_core) == int(set_core))
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"
        assert check_cpu_core, f"Check CPU Core fail in OS: {cpu_core}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1005", "[TC1005] Testcase_CoreDisable_004", "关核后系统稳定性测试"))
def Testcase_CoreDisable_004():
    """
    Name:       关核后系统稳定性测试
    Condition:  1、已安装Linux系统；
                2、CPU满配。
    Steps:      1、启动进Setup菜单，Processor界面随机设置CPU核数为N，F10保存重启；
                2、启动进OS，执行"lscpu"命令查看CPU信息，有结果A；
                3、反复复位5次，检查系统运行情况，有结果B。
    Result:     A：CPU数量与实际一致，每个CPU下N个Core；
                B：能正常进入OS，无异常现象。
    Remark:
    """
    cpu_count_keyword = "Socket"
    cpu_core_keywd = "Core"
    set_core = Sys.CPU_CORES // 2
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{set_core}", save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG + [Msg.MEM_TOP], Key.UP, 15, Msg.MEM_TOP)
        assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO, 30)
        assert SetUpLib.boot_to_default_os()
        cpu_count_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        cpu_core_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_core_keywd}"')
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        cpu_core = "".join(re.findall(f"{cpu_core_keywd}.*:\s*(.+)", cpu_core_cmd))
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_cpu_core = (int(cpu_core) == int(set_core))
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"
        assert check_cpu_core, f"Check CPU Core fail in OS: {cpu_core}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1006", "[TC1006] Testcase_CoreDisable_005", "隔核要求从bitmap高位进行隔离"))
def Testcase_CoreDisable_005():
    """
    Name:       隔核要求从bitmap高位进行隔离
    Condition:  1、已安装Linux系统；
                2、CPU满配；
                3、开启全打印。
    Steps:      1、启动进Setup菜单，串口检查bitmap置1位数与CPU核数是否一致，有结果A；
                2、Processor界面设置CPU核数为N（随机），F10保存重启，串口检查bitmap置1位数与CPU设置核数是否一致，置0位数是否从高位隔离，有结果B；
    Result:     A：bitmap置1位数为CPU支持最大核数MAX；
                B：bitmap置1位数为N；且置0位数MAX-N从高位依次隔离。
    Remark:     1、串口搜索关键字“resolvedCoresMask”，转换为二进制后置1位数即为使能CPU核数；
    """
    set_core = Sys.CPU_CORES // 2
    key_wd = []
    res_wd = []  # used to store the test result,
    end_str = "CPU Feature Early Config completed! Reset Requested: 0"

    # do not call,
    def check_bitmap(cpu_cores):
        ser_log = SerialLib.cut_log(Sut.BIOS_COM, "BIOS Log @", end_str, 300, 300)
        for line in ser_log.split('\n'):
            for i in SutConfig.Sys.CPU_POP:
                if re.search(f"S{i}_0 ResolvedCoresMask", line):
                    key_wd.append(line.replace(" ", ""))

        # check the original cpu bit value,
        key_wd_aft = sorted(list(set(key_wd)), key=key_wd.index)  # restore the order,
        for j in key_wd_aft[:int(len(key_wd_aft) / 2)]:
            cpu_id = j.strip().split('=')[0]
            cpu_val = j.strip().split('=')[1]
            # check the modified cpu bit value,
            for k in key_wd_aft[int(len(key_wd_aft) / 2):]:
                if k.strip().split('=')[0] == cpu_id:
                    if not cpu_val.endswith(k.strip().split('=')[1].lstrip('0')) and \
                            bin(int(cpu_val, 16)).count("1") == cpu_cores:
                        res_wd.append(j)
        # check the final result,
        if res_wd:
            logging.debug(res_wd)
            return False
        return True

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MISC_CONFIG, Key.DOWN, 20, Msg.MISC_CONFIG)
        assert SetUpLib.set_option_value(Msg.SYS_DEBUG_LEVEL, Msg.ENABLE, save=True)
        assert check_bitmap(SutConfig.Sys.CPU_CORES), '隔核未按要求从bitmap高位进行隔离'
        assert SetUpLib.boot_to_page_full_debug(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{set_core}", save=True)
        assert check_bitmap(set_core), f'{set_core}核未按要求从bitmap高位进行隔离'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1007", "[TC1007] Testcase_CoreDisable_008", "uniCfg定制CPU核数测试"))
def Testcase_CoreDisable_008():
    """
    Name:       uniCfg定制CPU核数测试
    Condition:  1、已安装Linux系统；
                2、CPU满配；
                3、uniCfg工具已上传OS。
    Steps:      1、启动进OS，执行uniCfg -R ProcessorActiveCore 查看当前使能的CPU核数；
                2、执行uniCfg -W ProcessorActiveCore:n （n为范围内任意值），reboot复位，进Setup菜单Processor界面，检查CPU核数使能值，有结果A；
                3、按ESC退出Setup菜单，启动进OS，执行lscpu，有结果B。
    Result:     A：CPU使能核数显示为n；
                B：每个CPU下显示n个核数。
    Remark:
    """
    cpu_core_keywd = "Core"
    core_aft = int(f'{list(BiosCfg.ACTIVE_CPU_CORE.values())[0]}', 16)
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.ACTIVE_CPU_CORE)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, f'{core_aft}']], Key.DOWN, 7)
        assert SetUpLib.boot_to_default_os()
        cpu_core_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_core_keywd}"')
        cpu_core = "".join(re.findall(f"{cpu_core_keywd}.*:\s*(.+)", cpu_core_cmd))
        check_cpu_core = (int(cpu_core) == core_aft)
        assert check_cpu_core, f"Check CPU Core fail in OS: {cpu_core}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1008", "[TC1008] Testcase_CoreDisable_009", "BIOS上报CPU核数到register.json文件正确性测试"))
def Testcase_CoreDisable_009():
    """
    Name:       BIOS上报CPU核数到register.json文件正确性测试
    Condition:  1、Postman工具已正确安装。
    Steps:      1、使用Postman工具获取BIOS上报的register.json文件；
                2、检查ProcessorActiveCore的Type、DisplayName、DefaultValue字段，有结果A。
    Result:     A：Type:"Enumeration"
                DisplayName:"Active Processor Cores"
                DefaultValue:All
                此预期结果视实际情况而定。
    Remark:     register.json文件具体Get路径参考：https://192.168.3.55/redfish/v1/RegistryStore/AttributeRegistries/en/BiosAttributeRegistry.v1_4_3.json。
    """
    active_core = False
    try:
        Sut.BMC_RFISH.registry_dump(True, path=SutConfig.Env.LOG_DIR, name="registry_009.json")  # 获取registry数据
        for n in Sut.BMC_RFISH.Attributes():
            if n.get("AttributeName") == list(BiosCfg.ACTIVE_CPU_CORE.keys())[0]:
                active_core = True
                assert n.get("DefaultValue") == "All" and n.get("Type") == "Enumeration", \
                    'error value or type, check the registry.json file'
        assert active_core, 'Can not find the right AttributeName'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1009", "[TC1009] Testcase_CoreDisable_010", "redfish带外使能1个CPU核数测试"))
def Testcase_CoreDisable_010():
    """
    Name:       redfish带外使能1个CPU核数测试
    Condition:  1、Postman工具已正确安装。
    Steps:      1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":1，有结果A；
                2、重启进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
    Result:     A：命令下发正常，无报错；
                B：CPU使能核数显示为1。
    Remark:     具体PATCH的路径参考：https://192.168.3.55/redfish/v1/Systems/Bios/Settings。
    """
    try:
        assert Sut.BMC_RFISH.set_bios_option(**{Attr.CPU_CORES: '1'}).result, 'Error: PATCH Fail'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, '<1>']], Key.DOWN, 7)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1010", "[TC1010] Testcase_CoreDisable_011", "redfish带外使能CPU核数最大值测试"))
def Testcase_CoreDisable_011():
    """
    Name:       redfish带外使能CPU核数最大值测试
    Condition:  1、Postman工具已正确安装
    Steps:      1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":n（n为当前CPU支持的最大核数），有结果A；
                2、重启进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
    Result:     A：命令下发正常，无报错；
                B：CPU使能核数显示为ALL，系统启动正常，无挂死反复复位现象。
    Remark:     具体PATCH的路径参考：https://192.168.3.55/redfish/v1/Systems/Bios/Settings。
    """
    try:
        assert Sut.BMC_RFISH.set_bios_option(**{Attr.CPU_CORES: f'{SutConfig.Sys.CPU_CORES}'}).result, 'Error: PATCH Fail'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, f'<All>']], Key.DOWN, 7)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1011", "[TC1011] Testcase_CoreDisable_012", "redfish带外使能CPU核数超过最大值测试"))
def Testcase_CoreDisable_012():
    """
    Name:       redfish带外使能CPU核数超过最大值测试
    Condition:  1、Postman工具已正确安装
    Steps:      1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":n（n为超过当前CPU支持的最大核数），有结果A；
                2、重启进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
    Result:     A：下发失败；
                B：CPU使能核数显示为ALL。
    Remark:     具体PATCH的路径参考：https://192.168.3.55/redfish/v1/Systems/Bios/Settings。
    """
    try:
        assert not Sut.BMC_RFISH.set_bios_option(**{Attr.CPU_CORES: f'{SutConfig.Sys.MAX_CORES_PLAT+1}'}).result, 'Expect PATCH fail, actually PATCH success'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, '<All>']], Key.DOWN, 7)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1012", "[TC1012] Testcase_CoreDisable_013", "redfish带外使能CPU核数为0测试"))
def Testcase_CoreDisable_013():
    """
    Name:       redfish带外使能CPU核数为0测试
    Condition:  1、Postman工具已正确安装
    Steps:      1、使用Postman工具带外设置CPU使能核数，命令格式"ProcessorActiveCore":0，有结果A；
                2、重启X86进入Setup菜单Processor界面，检查CPU使能核数选项显示，有结果B。
    Result:     A：命令下发失败，报错；
                B：CPU使能核数显示为ALL。
    Remark:     具体PATCH的路径参考：https://192.168.3.55/redfish/v1/Systems/Bios/Settings。
    """
    try:
        assert not Sut.BMC_RFISH.set_bios_option(**{Attr.CPU_CORES: '0'}).result, 'Error: PATCH Fail'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_options([[Msg.ACT_CPU_CORES, '<All>']], Key.DOWN, 7)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1013", "[TC1013] Testcase_Numa_001", "NUMA设置菜单检查"))
def Testcase_Numa_001():
    """
    Name:       NUMA设置菜单检查
    Condition:
    Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下检查NUMA选项默认值及可选值，有结果A。
    Result:     A：提供菜单开关，选项值为：Enable，Disable。默认为Enable；
    Remark:     1、不同产品选项可能存在差异，若非预期结果需找开发确认
    """
    try:
        numa_default = {Msg.NUMA: Msg.ENABLE}
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_COMM)
        if Sys.CPU_CNT <= 2:
            assert SetUpLib.get_option_value(Msg.NUMA, Key.UP, 10) == Msg.ENABLE
            assert MiscLib.same_values(SetUpLib.get_all_values(Msg.NUMA, Key.UP, 4), [Msg.ENABLE, Msg.DISABLE])
        else:
            assert SetUpLib.check_grey_option(numa_default)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1014", "[TC1014] Testcase_Numa_002", "满配CPU时NUMA节点个数测试"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="NUMA只支持2P系统")
def Testcase_Numa_002():
    """
    Name:       满配CPU时NUMA节点个数测试
    Condition:  1、满配CPU且各物理CPU均已配置内存；
                2、已经安装Linux系统。
    Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置关闭NUMA，保存重启；
                2、进入OS通过numactl -H命令查看内存控制器的个数，有结果A；
                3、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置打开NUMA；
                4、进入OS通过numactl -H命令查看内存控制器的个数，有结果B。
    Result:     A：查看到的内存控制器为一个；
                B：查看实际内存控制器个数应为当前服务器物理CPU个数。
    Remark:     1、Suse系统自带Numactl命令，Redhat/CentOS系统需要手动安装Package（yun install numa*）
                2、Suse15版本Numa特性可能存在问题（内核版本原因）
    """
    try:
        assert _numa_disabled_verify()
        nodes_dis = SshLib.execute_command(Sut.OS_SSH, NUMA_CMD).split('nodes')[0].split(':')[1]
        n = 0
        if int(nodes_dis) == 1:
            logging.info('numa set disabled,nodes = {}, pass'.format(int(nodes_dis)))
        else:
            n += 1
            logging.info('numa set disabled,nodes = {}, fail'.format(int(nodes_dis)))
        assert _numa_enabled_verify()
        nodes_ena = SshLib.execute_command(Sut.OS_SSH, NUMA_CMD).split('nodes')[0].split(':')[1]
        if int(nodes_ena) == int(SutConfig.Sys.CPU_CNT):
            logging.info('numa set enabled,nodes = {}, pass'.format(int(nodes_ena)))
        else:
            n += 1
            logging.info('numa set enabled,nodes = {}, fail'.format(int(nodes_ena)))
        assert n == 0
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1015", "[TC1015] Testcase_Numa_003", "满配CPU时NUMA节点间距测试"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="NUMA只支持2P系统")
def Testcase_Numa_003():
    """
    Name:       满配CPU时NUMA节点间距测试
    Condition:  1、满配CPU且各物理CPU均已配置内存；
                2、已经安装Linux系统。
    Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置关闭NUMA，保存重启；
                2、进入OS通过numactl -H命令查看各节点间距，有结果A；
                3、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置打开NUMA；
                4、进入OS通过numactl -H命令查看各节点间距，有结果B。
    Result:     A：仅一个节点，间距唯一。
                B：各节点间距符合硬件结构（如4P，node0到3的距离与到1、2的不同）。
    Remark:     1、节点间距离参考硬件结构。
    """
    n = 0
    try:
        assert _numa_disabled_verify()    # NUMA-disabled 仅一个节点，间距唯一
        nodes_dis = SshLib.execute_command(Sut.OS_SSH, NUMA_CMD).split('node')[-1].split(':')[1]
        if int(nodes_dis) == 10:
            logging.info("NUMA-disabled,Node internal distance - pass")
        else:
            n += 1
            logging.info('NUMA-disabled, nodes = {}, fail'.format(int(nodes_dis)))
        assert _numa_enabled_verify()
        numa_h = SshLib.execute_command(Sut.OS_SSH, NUMA_CMD)
        numa_n = int(numa_h.split('nodes')[0].split(":")[1].replace(' ', ''))  # NUMA-Enabled 获取节点数量
        i = 0
        for i in range(numa_n):
            numa_var = list(numa_h.split("node")[-1].split(r'{}:'.format(i))[1].splitlines()[0].replace('  ', ' ')
                            .strip().split(' '))
            if numa_var[i] == '10':  # 同节点内部间距=10
                logging.info("{} Node internal distance - pass".format(i))
                numa_var.pop(i)
                for j in range(numa_n - 1):
                    if numa_var[j] == '21':  # 不同节点距离=21
                        logging.info("{} Node external distance - pass".format(i))
                    else:
                        n += 1
                        logging.info('{} Node external distance - fail'.format(i))
                        return
            else:
                n += 1
                logging.info("{} Node internal distance - fail".format(i))
                return
        assert n == 0
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1016", "[TC1016] Testcase_Numa_004", "满配CPU时SLIT表正确上报测试"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="NUMA只支持2P系统")
def Testcase_Numa_004():
    """
    Name:       满配CPU时SLIT表正确上报测试
    Condition:  1、满配CPU；
                2、已经安装Linux系统。
    Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置开启NUMA，保存重启；
                2、进入OS通过工具dump并分离ACPI表，检查SLIT表上报是否正确，有结果A。
                3、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置关闭NUMA，保存重启；
                4、进入OS通过工具dump并分离ACPI表，检查SLIT表上报是否正确，有结果A。
    Result:     A：Numa开启时上报SLIT表，且表中记录的各节点间距符合硬件结构；
                B：Numa关闭时不上报SLIT表。
    Remark:     1、dump并分离ACPI表方法见“支持ACPI”需求用例步骤
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_COMM, Key.DOWN, 20, Msg.NUMA)
        assert SetUpLib.verify_info([Msg.NUMA], 2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_os_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        acpi_data = PlatMisc.get_acpi_table_linux("slit")
        node_num = len(re.findall('Locality+\s+\d+\s:', acpi_data))
        for i in range(node_num):
            numa_var_16 = acpi_data.split('Raw Table Data')[0].split('Locality   {} : '.format(i))[1].split('\n')[0].split(' ')
            if int(numa_var_16[i], 16) == 10:   #16进制字符转换成10进制，同节点内部间距=10
                logging.info("{} Node internal distance - pass".format(i))
                numa_other = list(set(numa_var_16)-{numa_var_16[i]})    #获取不同节点间距的数据
                for _other in numa_other:
                    if int(_other, 16) == 21:       #16进制字符转换成10进制，不同节点内部间距=21
                        logging.info("{} Node external distance - pass".format(i))
                    else:
                        logging.info('{} Node external distance - fail'.format(i))
                        return
            else:
                logging.info("{} Node internal distance - fail".format(i))
                return
        assert _numa_disabled_verify(), 'numa set disabled fail'      #numa关闭后，要求 不上报SLIT表
        acpi_data = PlatMisc.get_acpi_table_linux("slit")
        assert not acpi_data, 'slit_file exist, fail'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1017", "[TC1017] Testcase_Numa_005", "满配CPU时SRAT表正确上报测试"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="NUMA只支持2P系统")
def Testcase_Numa_005():
    """
    Name:       满配CPU时SRAT表正确上报测试
    Condition:  1、满配CPU；
                2、已经安装Linux系统。
    Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置开启NUMA，保存重启；
                2、进入OS通过工具dump并分离ACPI表，检查SRAT表上报是否正确，有结果A。
                3、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置关闭NUMA，保存重启；
                4、进入OS通过工具dump并分离ACPI表，检查SRAT表上报是否正确，有结果A。
    Result:     A：Numa开启时上报SRAT表，且表中记录的APIC ID与内存地址分配正确；
                B：Numa关闭时不上报SRAT表。
    Remark:     1、dump并分离ACPI表方法见“支持ACPI”需求用例步骤
    """
    apic_list = []
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_COMM, Key.DOWN, 20, Msg.NUMA)
        assert SetUpLib.verify_options([[Msg.NUMA, Msg.ENABLE]], Key.UP, 5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert SetUpLib.continue_to_os_from_bm()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 800)
        acpi_data = PlatMisc.get_acpi_table_linux("srat")
        _apic_list = re.findall('Apic ID\s:\s0{6}\w\w', acpi_data)
        for i in _apic_list:
            apic_str = re.split(':\s0{6}', i)[1]
            apic_list.append(apic_str)
        for i in range(len(apic_list)):
            for j in range(i + 1, len(apic_list)):
                assert apic_list[i] is not apic_list[j], 'a = {}, b = {}'.format(apic_list[i], apic_list[j])
        assert _numa_disabled_verify()      #numa关闭后，要求 不上报srat表
        acpi_data = PlatMisc.get_acpi_table_linux("srat")
        assert not acpi_data, 'srat_file exist, fail'
        logging.info('numa_disabled, srat.dsl is none')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1018", "[TC1018] Testcase_Numa_006", "NUMA关闭时内存1DPC长时间测试"))
@mark_skip_if(Sys.CPU_CNT == 4, reason="Setup option NUMA is grey out in 4s system")
def Testcase_Numa_006():
    """
    Name:       NUMA关闭时内存1DPC长时间测试
    Condition:  1、满配CPU且各内存配置为1DPC；
                2、已经安装Linux系统。
    Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置关闭NUMA，保存重启；
                2、检查BIOS启动和OS引导情况，有结果A；
                3、OS下反复复位，检查运行是否正常，有结果A。
    Result:     A：NUMA关闭不影响正常启动，串口日志无新增报错。
    Remark:     1、8P单板：8P/6P/2P单系统形态NUMA菜单被隐藏，默认开启，无法修改，1458形态以及8P/6P/4P双系统形态NUMA菜单开放且可修改.；
                2、支持NUMA特性，可开关，默认开启（基线需求描述，AR.SR.SF-00000602.001.004）。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_COMM, Key.DOWN, 20, Msg.NUMA)
        assert SetUpLib.verify_options([[Msg.NUMA, Msg.ENABLE]], Key.UP, 7)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.NUMA, Key.UP, 4), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.set_option_value(Msg.NUMA, Msg.DISABLE, save=True)
        for i in range(3):  # default - 3 loops, should be modified based on test case.
            assert PlatMisc.no_error_at_post()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1019", "[TC1019] Testcase_Numa_007", "1P模式时NUMA特性测试"))
# def Testcase_Numa_007():
#     """
#     Name:       1P模式时NUMA特性测试
#     Condition:  1、只保留主CPU；
#                 2、已经安装Linux系统。
#     Steps:      1、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置关闭NUMA，保存重启；
#                 2、进入OS通过numactl -H命令查看内存控制器的个数，有结果A；
#                 3、单板上电进入BIOS Setup菜单，在“Socket Configuration”界面下设置打开NUMA；
#                 4、进入OS通过numactl -H命令查看内存控制器的个数，有结果A。
#     Result:     A：查看到的内存控制器为一个；
#     Remark:     1、Suse系统自带Numactl命令，Redhat/CentOS系统需要手动安装Package（yun install numa*）
#                 2、Suse15版本Numa特性可能存在问题（内核版本原因）
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1020", "[TC1020] Testcase_Vtd_001", "VT-d设置菜单检查"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="4P系统VT-d菜单置灰")
def Testcase_Vtd_001():
    """
    Name:       VT-d设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，Socket Configuration页面下找到VT-d选项，查看其可选值及默认值，有结果A；
    Result:     A：Enabled、Disabled可选，默认为Enabled。
    Remark:     VTD在ExtendAPIC开启时, 会置灰无法选择
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert _disable_x2apic()
        assert SetUpLib.enter_menu(Msg.PATH_VIRTUAL_VTD, Key.DOWN)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.VTD), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.get_option_value(Msg.VTD, Key.DOWN, 15) == Msg.ENABLE
        assert SetUpLib.set_option_value(Msg.VTD, Msg.DISABLE, save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_VIRTUAL_VTD, Key.DOWN)
        assert SetUpLib.get_option_value(Msg.VTD, Key.DOWN, 15) == Msg.DISABLE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1021", "[TC1021] Testcase_Vtd_002", "VT-d菜单联动检查"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="4P系统VT-d菜单置灰")
def Testcase_Vtd_002():
    """
    Name:       VT-d菜单联动检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，关闭VT-d选项，F10保存重启再次进Setup菜单查看Extended APIC和其它关联选项状态，有结果A；
                2、开启VT-d选项，F10保存重启再次进Setup菜单查看Extended APIC和其它关联选项状态，有结果B；
                3、修改Extended APIC和其它关联选项为非默认值，F10保存重启再次进Setup菜单查看修改是否生效，有结果C。
    Result:     A：X2APIC和其它关联选项不可设置（隐藏或置灰）；
                B：X2APIC和其它关联选项恢复可设置状态；
                C：选项修改生效。
    Remark:     关闭VT-d选项，如果需要F10保存， 在2P机器上需要先关闭 Extended APIC。
    """
    vtd_option = [Msg.DISABLE, Msg.ENABLE]
    grey_option = [Msg.DMA_CON_OP_FLAG, Msg.INTERRUPT_REMAPPING, Msg.SATC_SUPPORT, Msg.RHSA_SUPPORT]

    def _back_vtd_page():
        try:
            assert SetUpLib.back_to_setup_toppage()
            assert SetUpLib.enter_menu(Msg.PATH_VIRTUAL_VTD)
            return True
        except Exception as e:
            logging.error(e)
            return False
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.set_option_value(Msg.EXTENDED_APIC, Msg.DISABLE, save=False)
        assert _back_vtd_page()
        for opt in vtd_option:
            assert SetUpLib.set_option_value(Msg.VTD, opt, save=True)
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
            if opt == Msg.DISABLE:
                assert not SetUpLib.locate_option(Msg.EXTENDED_APIC)                # 选项被隐藏
                assert _back_vtd_page()
                assert SetUpLib.check_grey_option(grey_option)                      # 选项被置灰
        # set 2
            if opt == Msg.ENABLE:
                assert SetUpLib.locate_option(Msg.EXTENDED_APIC)                    # 选项可设置
                assert _back_vtd_page()
                for op in grey_option:
                    assert SetUpLib.locate_option(op)                               # 选项可设置
        # set 3
        assert SetUpLib.set_option_value(Msg.RHSA_SUPPORT, Msg.DISABLE)
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.set_option_value(Msg.EXTENDED_APIC, Msg.DISABLE, save=True)
        # 验证 set3
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.verify_options([[Msg.EXTENDED_APIC, Msg.DISABLE]])
        assert _back_vtd_page()
        assert SetUpLib.verify_options([[Msg.RHSA_SUPPORT, Msg.DISABLE]])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1022", "[TC1022] Testcase_Vtd_004", "关闭VT-d启动测试"))
@mark_skip_if(Sys.CPU_CNT == 4, reason="Setup option VT-d is grey out in 4s system")
def Testcase_Vtd_004():
    """
    Name:       关闭VT-d启动测试
    Condition:  1、VT-d选项已关闭。
    Steps:      1、上电启动，检查能否正常进入系统，有结果A；
                2、检查串口日志，是否存在异常信息打印，有结果B。
    Result:     A：能正常启动进系统；
                B：串口无异常打印信息。
    Remark:     VTD在ExtendAPIC开启时, 会置灰无法选择
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert _disable_x2apic()
        assert SetUpLib.enter_menu(Msg.PATH_VIRTUAL_VTD, Key.DOWN)
        assert SetUpLib.set_option_value(Msg.VTD, Msg.DISABLE, save=True)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1023", "[TC1023] Testcase_Vtd_005", "DMAR表正确上报"))
@mark_skip_if(Sys.CPU_CNT == 4, reason="VTD Can not be disable success in 4S platform")
def Testcase_Vtd_005():
    """
    Name:       DMAR表正确上报
    Condition:
    Steps:      1、启动进Setup菜单，关闭VT-d选项，F10保存重启进入OS；
                2、使用dump工具分离ACPI表，检查DMAR表上报情况，有结果A。
                3、启动进Setup菜单，开启VT-d选项，F10保存重启进入OS；
                4、使用dump工具分离ACPI表，检查DMAR表上报情况，有结果B。
    Result:     A：关闭时不上报DMAR表。
                B：开启时上报DMAR表，且表中结构体DRHD、RMRR、ATSR、RHSA信息正确；
    Remark:     VTD在ExtendAPIC开启时, 会置灰无法选择
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert _disable_x2apic()
        assert SetUpLib.enter_menu(Msg.PATH_VIRTUAL_VTD, Key.DOWN)
        assert SetUpLib.set_option_value(Msg.VTD, Msg.ENABLE, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        acpi_dmar = PlatMisc.get_acpi_table_linux('dmar')
        assert acpi_dmar, "dmar table should be exists when numa is enable"
        # 表中结构体DRHD、RMRR、ATSR、RHSA信息正确 -- 无判定条件
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert _disable_x2apic()
        assert SetUpLib.enter_menu(Msg.PATH_VIRTUAL_VTD, Key.DOWN)
        assert SetUpLib.set_option_value(Msg.VTD, Msg.DISABLE, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        acpi_dmar = PlatMisc.get_acpi_table_linux('dmar')
        assert not acpi_dmar, 'dmar_file exist, fail'
        logging.info('vtd_disabled, dmar.dsl is none')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1024", "[TC1024] Testcase_CpuCompa_001", "BIOS关闭逻辑核功能测试"))
def Testcase_CpuCompa_001():
    """
    Name:       BIOS关闭逻辑核功能测试
    Condition:
    Steps:      1、进入Setup菜单,在Socket界面下使能1个核,F10后进OS用lscpu命令查看cpu核数信息，有结果A；
                2、执行dmidecode -t 4查看cpu使能的核数信息，有结果A；
                3、使能CPU核数遍历1、最大值、中间值，重复步骤1~2。
    Result:     A：CPU总核数不变，总线程数是总核数的两倍，使能的核数为与Setup菜单中设置的一致。
    Remark:
    """
    try:
        assert _cpu_cores_active_enable(1)      #使能CPU核数遍历1
        BmcLib.clear_cmos()
        assert _cpu_cores_active_enable(int(SutConfig.Sys.CPU_CORES / 2))      #使能CPU核数遍历中间值
        BmcLib.clear_cmos()
        assert _cpu_cores_active_enable(SutConfig.Sys.CPU_CORES)     #使能CPU核数遍历最大值
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1025", "[TC1025] Testcase_CpuCompa_002", "CPU BIST自检结果"))
def Testcase_CpuCompa_002():
    """
    Name:       CPU BIST自检结果
    Condition:
    Steps:      1、单板正常启动进OS，收集串口日志检查启动过程中是否存在CPU BIST报错，有结果A。
    Result:     A：无CPU BIST报错，无Error打印。
    Remark:     1、搜索“BIST”关键字即可
    """
    cat_end = Msg.LINUX_GRUB
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, cat_end, SutConfig.Env.BOOT_DELAY, SutConfig.Env.BOOT_DELAY)
        assert 'bist' not in log_cut, 'In serial_log found "bist", failed '
        logging.info('Not found "bist",pass ')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1026", "[TC1026] Testcase_CpuCompa_003", "CPU HT特性测试"))
def Testcase_CpuCompa_003():
    """
    Name:       CPU HT特性测试
    Condition:
    Steps:      1、进入BIOS Setup，检查HT模式设置，有结果A；
                2、进入系统，查看逻辑CPU的个数是否为物理CPU核数*2，有结果B；
                3、重启，进入BIOS Setup，设置关闭HT，F10后进入BIOS Setup，检查HT模式设置，有结果C；
                4、进入系统，查看逻辑CPU的个数是否为物理CPU核数，有结果D；
                5、重启进入BIOS Setup，F9恢复默认值，有结果E；
                6、保存重启，重复步骤2。
    Result:     A：CPU支持HT时，BIOS默认使能HT，CPU不支持HT时HT菜单隐藏；
                B：CPU支持HT且使能，逻辑CPU个数为物理CPU核数*2，CPU不支持HT时，逻辑CPU个数为物理CPU核数；
                C：HT为Disabled状态；
                D：CPU关闭HT逻辑CPU个数为物理CPU核数；
                E：HT恢复默认使能，CPU不支持HT时HT菜单依然隐藏。
    Remark:     1、CPU若不支持HT，则会隐藏Hyper-Threading选项。
    """
    def _set_lp_option(lp_option):
        try:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
            assert SetUpLib.set_option_value(Msg.EN_LP, lp_option, save=True)
            return True
        except AssertionError as e:
            logging.info(e)
            return False

    def _verify_logical_core(lp_option):
        cat_cmd = r'cat /proc/cpuinfo| grep "processor"| wc -l'
        try:
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
            _Logical_CPU = SshLib.execute_command(Sut.OS_SSH, cat_cmd)  # 查看逻辑CPU的个数
            assert _Logical_CPU
            Logical_CPU = int(_Logical_CPU.strip('\n'))
            logging.info("**Set LP_Enable,Core_Enabled = {}".format(Logical_CPU))
            if lp_option == Msg.VAL_LP_EN:
                assert Logical_CPU == SutConfig.Sys.CPU_CNT * SutConfig.Sys.CPU_CORES * 2, "**Core eorro**"
            if lp_option == Msg.VAL_LP_DIS:
                assert Logical_CPU == SutConfig.Sys.CPU_CNT * SutConfig.Sys.CPU_CORES, "**Core eorro**"
            return True
        except Exception as e:
            logging.error(e)
            return False
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)  # LP-enabled
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_options([[Msg.EN_LP, Msg.VAL_LP_EN]], Key.DOWN, 5), 'verify_LP_Enabled fail'
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _verify_logical_core(Msg.ENABLE)

        assert _set_lp_option(Msg.VAL_LP_DIS)      # LP-disabled
        assert _verify_logical_core(Msg.DISABLE)

        assert _set_lp_option(Msg.VAL_LP_EN)       # LP-enabled
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_options([[Msg.EN_LP, Msg.VAL_LP_EN]], Key.DOWN, 5)
        logging.info('All option_verify pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1027", "[TC1027] Testcase_CpuCompa_004", "CPU锁频测试"))
def Testcase_CpuCompa_004():
    """
    Name:       CPU锁频测试
    Condition:
    Steps:      1、进入Setup关闭EIST(P-State)，关闭C-State（默认关闭），F10保存重启；
                2、进入系统，查看CPU核的运行频率，有结果A；
                3、使用Stress工具对所有CPU加压，检查所有CPU核运行频率，有结果A。
    Result:     A：所有核运行在标称频率。
    Remark:     使用turbostat工具查看频率：./turbostate
    """
    res_val = []
    stress_command = f"stress --cpu {SutConfig.Sys.CPU_CORES} --timeout 20"
    get_cpu_cmd = "timeout 10 turbostat| awk -F' ' '{print $1,$2,$7}'"
    cmd_flag = "successful run completed"

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PSTATE_CTL, Key.UP, 20, Msg.CPU_P_STATE)
        assert SetUpLib.set_option_value(Msg.SPEED_STEP_EIST, Msg.DISABLE, save=True), '关闭EIST(P-State)失败'
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        get_cpu = SshLib.execute_command(Sut.OS_SSH, f"{stress_command} & {get_cpu_cmd}")
        assert re.search(cmd_flag, get_cpu), f'{get_cpu}'
        for i in get_cpu.split('\n')[3:-2]:
            base_spec = int(SutConfig.Sys.CPU_BASE * 1000)
            read_val = int(i.split()[2])
            if not MiscLib.value_close(base_spec, read_val, 5):
                res_val.append(f"{i.split()[0], i.split()[1], i.split()[2]}")
        assert len(res_val) == 0, f'{res_val}'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1028", "[TC1028] Testcase_CpuCompa_005", "CPU微码测试"))
def Testcase_CpuCompa_005():
    """
    Name:       CPU微码测试
    Condition:
    Steps:      1、进入BIOS Setup，Socket界面查看CPU微码版本，有结果A；
                2、进入系统，执行：cat /sys/devices/system/cpu/cpu0/microcode/version查看微码版本是否与步骤1一致，有结果B。
    Result:     A：微码版本显示正确；
                B：OS下查询微码版本和BIOS查询一致。
    Remark:     1、微码版本确认，如没有问题单跟踪修改，默认保持和上一个BIOS版本中的微码一致。
    """
    microcode_bios = f'{Msg.MICRO_CODE}\s+{PlatMisc.match_config_version().MicroCode}'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PER_CPU_INFO, Key.UP, 20, Msg.PROC_INFO)
        assert SetUpLib.verify_info([microcode_bios], 10)
        # OS中 查看CPU微码
        assert SetUpLib.boot_to_default_os()
        _res = SshLib.execute_command(Sut.OS_SSH, r'cat /sys/devices/system/cpu/cpu0/microcode/version')
        assert '0x' in _res, "command return error"
        microcode_os = _res.strip('\n').replace('0x', '', 1)
        assert microcode_os == PlatMisc.match_config_version().MicroCode.lower(), "Microcode in os doesn't match with BIOS setup"
        logging.info("The microcode_version in OS is the same as that in BIOS")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1029", "[TC1029] Testcase_CpuCompa_006", "CPU信息显示测试"))
def Testcase_CpuCompa_006():
    """
    Name:       CPU信息显示测试
    Condition:
    Steps:      1、启动进Setup菜单，查看CPU型号、频率、个数等信息是否正确，有结果A；
                2、启动进OS，dmidecode -t 4查看SMBIOS信息是否正确，有结果A；
                3、Web界面查看CPU信息上报是否正确，有结果A。
    Result:     A：CPU信息与实际一致。
    Remark:     1、Intel官网查询CPU信息：https://ark.intel.com/content/www/us/en/ark.html。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PER_CPU_INFO)
        assert SetUpLib.verify_options(SutConfig.Sys.CPU_INFO, integer=None)

        assert SetUpLib.boot_to_default_os()
        assert PlatMisc.smbios_dump_compare(Sut.OS_SSH, type_n=4), "SMBIOS type4 check failed"

        proc_info_web = BmcWeb.BMC_WEB.processor_info()
        assert proc_info_web, "Fail to get processor info from web"
        for proc in proc_info_web:
            assert SutConfig.Sys.CPU_FULL_NAME == proc, f"{proc} != {SutConfig.Sys.CPU_FULL_NAME}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1030", "[TC1030] Testcase_CpuCompa_009", "Local APIC特性测试"))
def Testcase_CpuCompa_009():
    """
    Name:       Local APIC特性测试
    Condition:
    Steps:      1、进入Setup菜单Socket界面下开启超线程，F10进入OS通过Dump工具Dump出apic.dsl表；
                2、查看表中“Local APIC”的个数是否与当前CPU总线程数一致，依序排列，且与APIC id一一对应，没有重复，有结果A；
                3、进入BIOS Setup选单界面，关闭超线程，F10进入OS通过Dump工具再次Dump出apic.dsl表；
                4、查看表中“Local APIC”的个数是否与当前CPU核数一致，依序排列，且与APIC id一一对应，没有重复，有结果B。
    Result:     A：“Local APIC”个数与当前CPU总线程数一致，id正确，顺序排列，没有重复；
                B：“Local APIC”个数与当前CPU核数一致，id正确，顺序排列，没有重复。
    Remark:     1、Dump工具路径：\\10.186.48.184\bios测试组工作基线\01 IT服务器项目组\01 V5服务器\LOG-uniBIOS Purley V100R008C20\测试工具；
                2、Dump命令三部曲：
                ./acpidump > acpi.dat
                ./acpixtract -a acpi.dat
                ./iasl -d apic.dat；
                3、查看“Local APIC”的个数：cat apic.dsl |grep -i "Local APIC ID"。
                4、8P Local APIC与Local APIC有区别
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)  # LP-enabled
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_options([[Msg.EN_LP, Msg.VAL_LP_EN]], Key.DOWN, 5), 'verify_LP_Enabled fail'
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _check_acpi_dsl_result(Msg.ENABLE)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)     # LP-disabled
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.set_option_value(Msg.EN_LP, Msg.VAL_LP_DIS)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _check_acpi_dsl_result(Msg.DISABLE)
        logging.info("All Local_APIC feature pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1031", "[TC1031] Testcase_CpuCompa_010", "内存NUMA特性设置测试"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="NUMA只支持2P系统")
def Testcase_CpuCompa_010():
    """
    Name:       内存NUMA特性设置测试
    Condition:  1、各物理CPU均已配置内存；
                2、已经安装Linux系统。
    Steps:      1、进入BIOS Setup 选单界面，在“Advanced”菜单下设置关闭NUMA；
                2、进入OS查看内存控制器的个数： numactl  --hardware，有结果A；
                3、进入BIOS Setup 选单界面，在“Advanced”菜单下设置打开NUMA；
                4、进入OS查看内存控制器的个数：numactl  --hardware，有结果B。
    Result:     1、关闭NUMA时，查看到的内存控制器为一个；
                2、打开NUMA时，查看实际内存控制器个数应为当前服务器物理CPU个数。
    Remark:     1、测试Numa时确保每个CPU下都存在内存条。
    """
    Num_cmd = r'numactl --hardware'
    try:
        assert _numa_disabled_verify()
        nodes_dis = SshLib.execute_command(Sut.OS_SSH, Num_cmd).split('nodes')[0].split(':')[1]
        assert int(nodes_dis) == 1, 'numa_disabled fail'
        assert _numa_enabled_verify()
        nodes_enab = SshLib.execute_command(Sut.OS_SSH, Num_cmd).split('nodes')[0].split(':')[1]
        assert int(nodes_enab) == SutConfig.Sys.CPU_CNT, 'numa_enabled fail'
        logging.info("All numa feature pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1032", "[TC1032] Testcase_CpuCompa_017", "X2APIC选项测试"))
def Testcase_CpuCompa_017():
    """
    Name:       X2APIC选项测试
    Condition:  1、使能X2Apic选项。
    Steps:      1、进入Setup菜单Socket界面下开启超线程，F10进入OS通过Dump工具Dump出apic.dsl表；
                2、查看表中“Local APIC”的个数是否与当前CPU总线程数一致，依序排列，且与APIC id一一对应，没有重复，有结果A；
                3、进入BIOS Setup选单界面，关闭超线程，F10进入OS通过Dump工具再次Dump出apic.dsl表；
                4、查看表中“Local APIC”的个数是否与当前CPU核数一致，依序排列，且与APIC id一一对应，没有重复，有结果B。
    Result:     A：“X2APIC”个数与当前CPU总线程数一致,id正确，没有重复；
                B：“X2APIC”个数与当前CPU总核数一致,id正确，没有重复。
    Remark:     1、C20更改为同Local APIC一致，因此查看是搜索关键字“Local APIC ID”即可；
                2、Dump工具路径：\\10.186.48.184\bios测试组工作基线\01 IT服务器项目组\01 V5服务器\LOG-uniBIOS Purley V100R008C20\测试工具；
                3、Dump命令三部曲：
                ./acpidump > acpi.dat
                ./acpixtract -a acpi.dat
                ./iasl -d apic.dat；
                4、查看“Local APIC”的个数：cat apic.dsl |grep -i "Local APIC ID"。
                5、8P Local APIC与Local APIC有区别
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)  # LP-enabled
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_options([[Msg.EN_LP, Msg.VAL_LP_EN]], Key.DOWN, 5), 'verify_LP_Enabled fail'
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _check_acpi_dsl_result(Msg.ENABLE)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)     # LP-disabled
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.set_option_value(Msg.EN_LP, Msg.VAL_LP_DIS)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _check_acpi_dsl_result(Msg.DISABLE)
        logging.info("All X2APIC feature pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1033", "[TC1033] Testcase_CpuCompa_019", "内存满配信息显示"))
def Testcase_CpuCompa_019():
    """
    Name:       内存满配信息显示
    Condition:  1、单板满插内存。
    Steps:      1、单板启动检查MRC阶段内存拓扑表，内存型号、容量、厂家、位宽等信息，有结果A；
                2、启动按DEL进Setup菜单，进入Memory界面，查看内存槽位、型号、容量、厂家、位宽等信息，有结果A；
                3、Web界面查看内存槽位、型号、容量、厂家、位宽等信息，有结果A。
    Result:     A：内存信息正确。
    Remark:     1、步骤1需开启全打印，相关信息在全打印日志中搜索关键字“MRC”。
    """
    capture_start = Msg.CPU_RSC_ALLOC
    capture_end = "STOP_DIMMINFO_SYSTEM_TABLE"
    try:
        assert BmcLib.force_reset()
        log_cut = SerialLib.cut_log(Sut.BIOS_COM, capture_start, capture_end, 60, 100)
        assert MiscLib.verify_msgs_in_log(SutConfig.Sys.MEM_POST_INFO, log_cut)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEN_INFO, Key.DOWN, 30, 'DIMM000')
        assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO, 64)
        logging.info("All Dimm_info pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1034", "[TC1034] Testcase_CpuCompa_024", "OS下X2APIC开关状态测试"))
@mark_skip_if(Sys.CPU_CNT > 2, reason="4P系统下,X2APIC选项置灰无法更改")
def Testcase_CpuCompa_024():
    """
    Name:       OS下X2APIC开关状态测试
    Condition:  1、单板满插CPU。
    Steps:      1、进入Setup菜单开启X2APIC，F10保存重启，进入OS通过dmesg |grep -i x2apic查询，有结果A；
                2、重启进入Setup菜单关闭X2APIC，F10保存重启，进入OS通过dmesg |grep -i x2apic查询，有结果A。
    Result:     A：OS查询结果与Setup菜单设置保持一致。
    Remark:
    """
    x2apic_cmd = "dmesg | grep -i 'x2apic'"
    try:
        # enabled by default on 4P,
        assert SetUpLib.boot_to_default_os()
        assert re.search(Msg.ENABLE, SshLib.execute_command(Sut.OS_SSH, x2apic_cmd), re.I), 'can not find str enabled'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.EXTENDED_APIC, Msg.DISABLE, loc_cnt=20, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert re.search(Msg.DISABLE, SshLib.execute_command(Sut.OS_SSH, x2apic_cmd), re.I), 'can not find str disabled'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1035", "[TC1035] Testcase_CpuCompa_025", "关核后CPU HT特性测试"))
def Testcase_CpuCompa_025():
    """
    Name:       关核后CPU HT特性测试
    Condition:  1、已安装Linux系统；
                2、CPU满配;
                3、设置CPU核数为N（随机）。
    Steps:      1、启动进Setup菜单，Processor界面设置HT选项为Disabled，F10保存重启；
                2、启动进OS，执行"lscpu"命令查看CPU信息，有结果A；
                3、启动进Setup菜单，Processor界面设置HT选项为Enabled，F10保存重启；
                4、启动进OS，执行"lscpu"命令查看CPU信息，有结果B；
    Result:     A：每个核的线程数为1；
                B：每个核的线程数为2。
    Remark:     1、CPU不支持HT特性时隐藏此选项。
    """
    ex_cmd = "lscpu | grep 'Thread'"
    try:
        # enabled by default on 4P,
        assert SetUpLib.boot_to_default_os()
        assert re.search("2", SshLib.execute_command(Sut.OS_SSH, ex_cmd), re.I), '每个核的线程数不为2'
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.EN_LP, Msg.VAL_LP_DIS, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert re.search("1", SshLib.execute_command(Sut.OS_SSH, ex_cmd), re.I), '每个核的线程数不为1'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1036", "[TC1036] Testcase_CpuCompa_026", "关核后CPU锁频测试"))
# def Testcase_CpuCompa_026():
#     """
#     Name:       关核后CPU锁频测试
#     Condition:  1、已安装Linux系统；
#                 2、CPU满配;
#                 3、设置CPU核数为N（随机）。
#     Steps:      1、启动进Setup菜单，P状态界面设置EIST(P-State)选项为Disabled，F10保存重启；
#                 2、启动进OS，空闲和加压状态下检查CPU运行频率，有结果A；
#                 3、启动进Setup菜单，P状态界面设置EIST(P-State)选项为Enabled，F10保存重启；
#                 4、启动进OS，空闲和加压状态下检查CPU运行频率，有结果B；
#     Result:     A：空闲、加压状态下所有核均运行在标称频率；
#                 B：空闲状态下所有核均运行在最小频率；加压状态下所有核均运行在Turbo频率。
#     Remark:
#     """
#     res_val_a = []  # 用于存Result A结果集合
#     res_val_b = []  # 用于存Result B结果集合
#     stress_command = f"stress --cpu {SutConfig.Sys.CPU_CORES} --timeout 20"
#     get_cpu_cmd = "timeout 10 turbostat| awk -F' ' '{print $1,$2,$7}'"
#     cmd_flag = "successful run completed"
#
#     # do not call,
#     def _check_freq_res(res_list, cpu_status, freq):
#         assert re.search(cmd_flag, cpu_status), f'{cpu_status}'
#         for i in cpu_status.split('\n')[3:-2]:
#             if int(i.split()[2]) != int(freq):
#                 res_list.append(f"{i.split()[0], i.split()[1], i.split()[2]}")
#         if len(res_list) != 0:
#             return False, res_list
#         return True
#
#     try:
#         # enabled by default on 4P,
#         assert BmcLib.force_reset()
#         assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
#         # based on linux os,
#         SshLib.execute_command(Sut.OS_SSH, "cpupower -c all frequency-set -g ondemand")
#         # free status,
#         cpu_free = SshLib.execute_command(Sut.OS_SSH, f"{get_cpu_cmd}")
#         if not _check_freq_res(res_val_b, cpu_free, 800):
#             logging.debug(_check_freq_res(res_val_b, cpu_free, 800)[1])
#             logging.warning('空闲状态下部分核未运行在最小频率, 继续测试中')
#         # busy status,
#         cpu_busy = SshLib.execute_command(Sut.OS_SSH, f"{stress_command} & {get_cpu_cmd}")
#         if not _check_freq_res(res_val_b, cpu_busy, SutConfig.Sys.CPU_TURBO * 1000):
#             logging.debug(_check_freq_res(res_val_b, cpu_busy, SutConfig.Sys.CPU_TURBO * 1000)[1])
#             logging.warning('加压状态下部分核未运行在Turbo频率, 继续测试中')
#         # disabled turbo mode for next test step,
#         assert Sut.UNITOOL.write(**{"TurboMode": 0})
#         assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
#         assert SetUpLib.enter_menu(Key.UP, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE)
#         assert SetUpLib.set_option_value(Msg.SPEED_STEP_EIST, Msg.DISABLE, save=True), '关闭EIST(P-State)失败'
#         assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
#         SshLib.execute_command(Sut.OS_SSH, "cpupower -c all frequency-set -g ondemand")
#         # free status,
#         cpu_free = SshLib.execute_command(Sut.OS_SSH, f"{get_cpu_cmd}")
#         if not _check_freq_res(res_val_b, cpu_free, SutConfig.Sys.CPU_BASE * 1000):
#             logging.debug(_check_freq_res(res_val_b, cpu_free, 800)[1])
#             logging.warning('空闲状态下部分核未运行在最小频率, 继续测试中')
#         # busy status,
#         cpu_busy = SshLib.execute_command(Sut.OS_SSH, f"{stress_command} & {get_cpu_cmd}")
#         assert _check_freq_res(res_val_b, cpu_busy, SutConfig.Sys.CPU_BASE * 1000), \
#             '加压状态下部分核未运行在Turbo频率, {0}'.format(res_val_a)
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1037", "[TC1037] Testcase_CpuCompa_029", "关核后Local APIC特性测试"))
def Testcase_CpuCompa_029():
    """
    Name:       关核后Local APIC特性测试
    Condition:  1、CPU核数当前为X（X为随机值）
    Steps:      1、进入Setup菜单Socket界面下开启超线程，F10进入OS通过Dump工具Dump出apic.dsl表；
                2、查看表中“Local APIC”的个数是否与当前CPU总线程数一致，依序排列，且与APIC id一一对应，没有重复，有结果A；
                3、进入BIOS Setup选单界面，关闭超线程，F10进入OS通过Dump工具再次Dump出apic.dsl表；
                4、查看表中“Local APIC”的个数是否与当前CPU核数一致，依序排列，且与APIC id一一对应，没有重复，有结果B。
    Result:     A：“Local APIC”个数与当前CPU总线程数一致，id正确，顺序排列，没有重复；
                B：“Local APIC”个数与当前CPU核数一致，id正确，顺序排列，没有重复。
    Remark:     1、Dump工具路径：\\10.186.48.184\bios测试组工作基线\01 IT服务器项目组\01 V5服务器\LOG-uniBIOS Purley V100R008C20\测试工具；
                2、Dump命令三部曲：
                ./acpidump > acpi.dat
                ./acpixtract -a acpi.dat
                ./iasl -d apic.dat；
                3、查看“Local APIC”的个数：cat apic.dsl |grep -i "Local APIC ID"。
    """
    id_list = []
    id_res = []  # used to store the results,

    def _check_id_cores(cpu_thread):
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        apic_num = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_num == cpu_thread, f"Threads in apic: {apic_num}, expected: {cpu_thread}"
        # check the pyh cores,
        for line in apic_table.split("\n"):
            if re.findall("Processor x2Apic ID", line):
                id_list.append(line.split(":")[1])
        for i in id_list[:int(len(id_list) / 2)]:
            if int(i, 16) % 2 != 0:
                id_res.append(i)
        # check the non-phy cores,
        for j in id_list[int(len(id_list) / 2):]:
            if int(j, 16) % 2 == 0:
                id_res.append(j)
        if len(id_res) != 0:
            return False, id_res
        return True

    try:
        # enabled by default on 4P,
        assert BmcLib.force_reset()
        cpu_threads = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT * 2
        assert _check_id_cores(cpu_threads), \
            "X2APIC个数与当前CPU总线程数测试异常, {0}".format(_check_id_cores(cpu_threads)[1])
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.EN_LP, Msg.VAL_LP_DIS, save=True)
        cpu_threads_aft = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT
        assert _check_id_cores(cpu_threads_aft), \
            "X2APIC个数与当前CPU总核数测试异常, {0]".format(_check_id_cores(cpu_threads_aft)[1])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1038", "[TC1038] Testcase_CpuCompa_033", "关核后X2APIC选项测试"))
def Testcase_CpuCompa_033():
    """
    Name:       关核后X2APIC选项测试
    Condition:  1、进入BIOS Setup，将Extended apic选项设置成enable。
                2、CPU核数当前为X（X为随机值）
    Steps:      1、进入Setup菜单Socket界面下开启超线程，F10进入OS通过Dump工具Dump出apic.dsl表；
                2、查看表中“Local APIC”的个数是否与当前CPU总线程数一致，依序排列，且与APIC id一一对应，没有重复，有结果A；
                3、进入BIOS Setup选单界面，关闭超线程，F10进入OS通过Dump工具再次Dump出apic.dsl表；
                4、查看表中“Local APIC”的个数是否与当前CPU核数一致，依序排列，且与APIC id一一对应，没有重复，有结果B。
    Result:     A：“X2APIC”个数与当前CPU总线程数一致,id正确，没有重复；
                B：“X2APIC”个数与当前CPU总核数一致,id正确，没有重复。
    Remark:     1、C20更改为同Local APIC一致，因此查看是搜索关键字“Local APIC ID”即可；
                2、Dump工具路径：\\10.186.48.184\bios测试组工作基线\01 IT服务器项目组\01 V5服务器\LOG-uniBIOS Purley V100R008C20\测试工具；
                3、Dump命令三部曲：
                ./acpidump > acpi.dat
                ./acpixtract -a acpi.dat
                ./iasl -d apic.dat；
                4、查看“Local APIC”的个数：cat apic.dsl |grep -i "Local APIC ID"。
    """
    id_list = []
    id_res = []  # used to store the results,

    def _check_id_cores(cpu_thread):
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        apic_num = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_num == cpu_thread, f"Threads in apic: {apic_num}, expected: {cpu_thread}"
        # check the pyh cores,
        for line in apic_table.split("\n"):
            if re.findall("Processor x2Apic ID", line):
                id_list.append(line.split(":")[1])
        for i in id_list[:int(len(id_list) / 2)]:
            if int(i, 16) % 2 != 0:
                id_res.append(i)
        # check the non-phy cores,
        for j in id_list[int(len(id_list) / 2):]:
            if int(j, 16) % 2 == 0:
                id_res.append(j)
        if len(id_res) != 0:
            return False, id_res
        return True

    try:
        # enabled by default on 4P,
        assert BmcLib.force_reset()
        cpu_threads = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT * 2
        assert _check_id_cores(cpu_threads), \
            "X2APIC个数与当前CPU总线程数测试异常, {0}".format(_check_id_cores(cpu_threads)[1])
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG, Key.DOWN, 20, Msg.PROC_INFO)
        assert SetUpLib.set_option_value(Msg.EN_LP, Msg.VAL_LP_DIS, save=True)
        cpu_threads_aft = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT
        assert _check_id_cores(cpu_threads_aft), \
            "X2APIC个数与当前CPU总核数测试异常, {0]".format(_check_id_cores(cpu_threads_aft)[1])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1039", "[TC1039] Testcase_SpreadSpectrum_001", "时钟展频设置菜单检查"))
# def Testcase_SpreadSpectrum_001():
#     """
#     Name:       时钟展频设置菜单检查
#     Condition:  
#     Steps:      1、启动进Setup菜单，PCH Configuration页面下检查是否存在External SSC - CK440选项，查看其可选值及默认值，有结果A；
#     Result:     A：存在时钟展频选项，SSC Off、SSC = -0.3%、SSC = -0.5%、Hardware可选，默认为Hardware。
#     Remark:     1、具体位置：Setup -> Advanced -> PCH-IO Configuration -> External SSC - CK440
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1040", "[TC1040] Testcase_SpreadSpectrum_002", "时钟展频功能测试"))
# def Testcase_SpreadSpectrum_002():
#     """
#     Name:       时钟展频功能测试
#     Condition:  1、开启全打印；
#     Steps:      1、启动进Setup菜单，PCH Configuration页面下设置时钟展频选项，保存重启；
#                 2、串口打印搜索“Clock Generator”查看Byte6数值是否与设置匹配，有结果A；
#                 3、遍历展频所有可选值，重复步骤1~2。
#     Result:     A：Byte6与设置选项匹配。
#     Remark:     1、具体位置：Setup -> Advanced -> PCH-IO Configuration -> External SSC - CK440；
#                 2、Byte6与设置值对应关系如下：
#                 0x04：SSC Off
#                 0x05：SSC = -0.3%
#                 0x07：SSC = -0.5%
#                 0x00：Hardware
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1041", "[TC1041] Testcase_ApicReport_001", "APIC上报策略设置菜单检查"))
def Testcase_ApicReport_001():
    """
    Name:       APIC上报策略设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，MISC界面下检查是否存在APIC上报测略设置选项，可选择及默认值，有结果A。
    Result:     A：存在APIC上报策略选择开关，ALL、Available可选，默认Available。
    Remark:     1、选项含义：
                Available----按照实际CPU核数上报；
                ALL----按照平台最大核数上报。
    """
    apic_path = [Msg.CPU_CONFIG, Msg.PROCESSOR_CONFIG]
    apic_values = ["Physical", "Maximum"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(apic_path, Key.DOWN, 20, 'Processor Information')
        assert SetUpLib.get_option_value(Msg.APIC_REPORT_CFG, Key.DOWN, 20) == apic_values[0]
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.APIC_REPORT_CFG), apic_values)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1042", "[TC1042] Testcase_ApicReport_002", "APIC上报策略为Available功能测试"))
def Testcase_ApicReport_002():
    """
    Name:       APIC上报策略为Available功能测试
    Condition:  1、设置APIC上报策略为Available；
                2、dump工具已上传OS。
    Steps:      1、启动进OS，使用acpidump工具导出ACPI总表，命令：./acpidump > acpi.out
                2、使用acpixtract工具分离总表生成多个ACPI表项，命令：./acpixtract -a acpi.out
                3、选择apic表项，使用iasl工具反汇编成dsl格式，命令：./iasl -d apic.dat
                4、使用cat命令查看apic表项中Local Apic ID个数，命令：cat apic.dsl |grep "Local Apic ID"，有结果A。
    Result:     A：Local Apic ID个数与当前CPU总线程数一致。
    Remark:     1、CPU总线程 = 当前CPU个数 *  当前CPU使能核数 * 当前CPU支持线程数；
                2、Local Apic ID最大到255个，超过则使用x2APIC。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT * 2
        apic_threads = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_threads == cpu_threads, f"Threads in apic: {apic_threads}, expect: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1043", "[TC1043] Testcase_ApicReport_003", "关核后APIC上报策略为Available功能测试"))
def Testcase_ApicReport_003():
    """
    Name:       关核后APIC上报策略为Available功能测试
    Condition:  1、设置APIC上报策略为Available；
                2、设置CPU核数为N（随机）；
                3、dump工具已上传OS。
    Steps:      1、启动进OS，使用acpidump工具导出ACPI总表，命令：./acpidump > acpi.out
                2、使用acpixtract工具分离总表生成多个ACPI表项，命令：./acpixtract -a acpi.out
                3、选择apic表项，使用iasl工具反汇编成dsl格式，命令：./iasl -d apic.dat
                4、使用cat命令查看apic表项中Local Apic ID个数，命令：cat apic.dsl |grep "Local Apic ID"，有结果A。
    Result:     A：Local Apic ID个数与当前CPU总线程数一致。
    Remark:     1、CPU总线程 = 当前CPU个数 *  当前CPU使能核数 * 当前CPU支持线程数；
                2、Local Apic ID最大到255个，超过则使用x2APIC。
    """
    try:
        # available by default on 4P,
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT * 2
        max_apic_report = len(re.findall("Processor Local x2APIC", apic_table))
        assert max_apic_report == cpu_threads, f"Threads in apic: {max_apic_report}, expect: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1044", "[TC1044] Testcase_ApicReport_004", "上报策略为Available且APIC个数超过255时上报测试"))
@mark_skip_if(Sys.CPU_CORES * Env.MAX_CPU_CNT * 2 < 255, reason="APIC个数未超过255")
def Testcase_ApicReport_004():
    """
    Name:       上报策略为Available且APIC个数超过255时上报测试
    Condition:  1、设置APIC上报策略为Available；
                2、设置CPU核数为N，使总APIC个数超过255；
                3、dump工具已上传OS。
    Steps:      1、启动进OS，使用acpidump工具导出ACPI总表，命令：./acpidump > acpi.out
                2、使用acpixtract工具分离总表生成多个ACPI表项，命令：./acpixtract -a acpi.out
                3、选择apic表项，使用iasl工具反汇编成dsl格式，命令：./iasl -d apic.dat
                4、使用cat命令查看apic表项中Local Apic ID与Local X2Apic ID个数，命令：cat apic.dsl |grep -E 'Local Apic ID | Local X2Apic ID'，有结果A。
    Result:     A：Local Apic ID、Local X2Apic ID个数之和与平台最大线程数一致。
    Remark:     1、CPU总线程 = 当前CPU个数 *  当前CPU使能核数 * 当前CPU支持线程数；
                2、Local Apic ID最大到255个，超过则使用x2APIC。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**{Attr.CPU_CORES: 0})
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = SutConfig.Sys.CPU_CORES * SutConfig.Sys.CPU_CNT * 2
        apic_report = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_report == cpu_threads, f"Threads in apic: {apic_report}, expected: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1045", "[TC1045] Testcase_ApicReport_005", "APIC上报策略为ALL功能测试"))
def Testcase_ApicReport_005():
    """
    Name:       APIC上报策略为ALL功能测试
    Condition:  1、设置APIC上报策略为ALL；
                2、dump工具已上传OS。
    Steps:      1、启动进OS，使用acpidump工具导出ACPI总表，命令：./acpidump > acpi.out
                2、使用acpixtract工具分离总表生成多个ACPI表项，命令：./acpixtract -a acpi.out
                3、选择apic表项，使用iasl工具反汇编成dsl格式，命令：./iasl -d apic.dat
                4、使用cat命令查看apic表项中Local Apic ID个数，命令：cat apic.dsl |grep "Local Apic ID"，有结果A。
    Result:     A：Local Apic ID个数与平台最大线程数一致。
    Remark:     1、平台最大线程数 = 产品支持最大CPU个数 * 平台支持CPU最大核数 * 平台CPU支持最大线程数；
                2、V7支持CPU最大核数为64核。
    """
    try:
        assert SetUpLib.boot_to_default_os(delay=10)
        assert Sut.UNITOOL.write(**{Attr.ACPI_APIC: 1})
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = SutConfig.Sys.MAX_CORES_PLAT * SutConfig.Env.MAX_CPU_CNT * 2
        apic_report = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_report == cpu_threads, f"Threads in apic: {apic_report}, expected: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1046", "[TC1046] Testcase_ApicReport_006", "关核后APIC上报策略为ALL功能测试"))
def Testcase_ApicReport_006():
    """
    Name:       关核后APIC上报策略为ALL功能测试
    Condition:  1、设置APIC上报策略为ALL；
                2、设置CPU核数为N（随机）；
                3、dump工具已上传OS。
    Steps:      1、启动进OS，使用acpidump工具导出ACPI总表，命令：./acpidump > acpi.out
                2、使用acpixtract工具分离总表生成多个ACPI表项，命令：./acpixtract -a acpi.out
                3、选择apic表项，使用iasl工具反汇编成dsl格式，命令：./iasl -d apic.dat
                4、使用cat命令查看apic表项中Local Apic ID个数，命令：cat apic.dsl |grep "Local Apic ID"，有结果A。
    Result:     A：Local Apic ID个数与平台最大线程数一致。
    Remark:     1、平台最大线程数 = 产品支持最大CPU个数 * 平台支持CPU最大核数 * 平台CPU支持最大线程数；
                2、V7支持CPU最大核数为64核。
    """
    try:
        assert SetUpLib.boot_to_default_os(delay=10)
        assert Sut.UNITOOL.write(**{Attr.ACPI_APIC: 1, Attr.CPU_CORES: 7})
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = SutConfig.Sys.MAX_CORES_PLAT * SutConfig.Env.MAX_CPU_CNT * 2
        apic_report = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_report == cpu_threads, f"Threads in apic: {apic_report}, expected: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1047", "[TC1047] Testcase_ApicReport_007", "上报策略为ALL且APIC个数超过255时上报测试"))
@mark_skip_if(Sys.MAX_CORES_PLAT * Env.MAX_CPU_CNT * 2 < 255, reason="APIC个数未超过255")
def Testcase_ApicReport_007():
    """
    Name:       上报策略为ALL且APIC个数超过255时上报测试
    Condition:  1、设置APIC上报策略为ALL；
                2、设置CPU核数为N，使总APIC个数超过255；
                3、dump工具已上传OS。
    Steps:      1、启动进OS，使用acpidump工具导出ACPI总表，命令：./acpidump > acpi.out
                2、使用acpixtract工具分离总表生成多个ACPI表项，命令：./acpixtract -a acpi.out
                3、选择apic表项，使用iasl工具反汇编成dsl格式，命令：./iasl -d apic.dat
                4、使用cat命令查看apic表项中Local Apic ID与Local X2Apic ID个数，命令：cat apic.dsl |grep -E 'Local Apic ID | Local X2Apic ID'，有结果A。
    Result:     A：Local Apic ID、Local X2Apic ID个数之和与平台最大线程数一致。
    Remark:     1、平台最大线程数 = 产品支持最大CPU个数 * 平台支持CPU最大核数 * 平台CPU支持最大线程数；
                2、V7支持CPU最大核数为64核。
                3、Local Apic ID最大到255个，超过则使用Local X2Apic ID。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**{Attr.ACPI_APIC: 1, **BiosCfg.ACTIVE_CPU_CORE})
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = SutConfig.Sys.MAX_CORES_PLAT * SutConfig.Env.MAX_CPU_CNT * 2
        apic_report = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_report == cpu_threads, f"Threads in apic: {apic_report}, expected: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1048", "[TC1048] Testcase_ApicReport_008", "修改CPU核数上报APIC表测试"))
def Testcase_ApicReport_008():
    """
    Name:       修改CPU核数上报APIC表测试
    Condition:  1、修改Active Processor core为任意值；
    Steps:      1、OS下使用acpidump工具导出ACPI表信息acpidump > acpi.out；
                2、分离各表格数据，会生成多个数据文件，使用命令acpixtract -a acpi.out；
                3、反汇编apic表，使用命令iasl -d apic.dat，然后使用cat命令查看apic表项信息，有结果A。
    Result:     A：APIC表“Local APIC”个数为平台最大支持核数。
    Remark:     1、Local Apic ID最大到255个，超过则使用Local X2Apic ID。
    """
    set_cores = int(list(BiosCfg.ACTIVE_CPU_CORE.values())[0], 16)
    try:
        assert SetUpLib.boot_to_default_os(delay=10)
        assert Sut.UNITOOL.write(**BiosCfg.ACTIVE_CPU_CORE)
        assert SetUpLib.boot_to_default_os()
        apic_table = PlatMisc.get_acpi_table_linux("apic")
        assert apic_table, "dump ACPI-apic table failed"
        cpu_threads = set_cores * SutConfig.Sys.CPU_CNT * 2
        apic_report = len(re.findall("Processor Local x2APIC", apic_table))
        assert apic_report == cpu_threads, f"Threads in apic: {apic_report}, expected: {cpu_threads}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

