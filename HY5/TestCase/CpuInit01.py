import logging
from batf import SerialLib, SshLib, MiscLib, core
from batf.SutInit import Sut
from HY5.Config import SutConfig
from HY5.Config.PlatConfig import Key, Msg
from HY5.BaseLib import SetUpLib
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


# Testcase_CPU_COMPA_015, 016 - TBD
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Uncore status page
def upi_link_status():
    tc = ('200', '[TC200]UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc)
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