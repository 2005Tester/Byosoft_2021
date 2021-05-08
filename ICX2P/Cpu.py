import logging
from Core import SerialLib, SshLib
from Core.SutInit import Sut
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import icx2pAPI, SetUpLib, BmcLib
from Report import ReportGen


# Cpu Related Test case, test case ID, TC200-299

##########################################
#              CPU Test Cases            #
##########################################


# function Module : 使用unitool修改Cpu_core
def set_cpu_by_unitool(ssh_os, cmd_set):
    SshLib.execute_command(ssh_os, r'cd {0};insmod ufudev.ko'.format(SutConfig.UNI_PATH))
    res = SshLib.execute_command(ssh_os, cmd_set)
    logging.info(res)
    if len(res) == 0:
        logging.info('blank, maybe the ko module failed')
        return False
    elif 'error' in res:
        logging.info("Modify BIOS_Setting :Fail")
        return False
    else:
        logging.info('Rebooting the SUT...')
        SshLib.execute_command(ssh_os, 'reboot')
    logging.info("Modify BIOS_Setting :Pass")
    return True


# function Module : 还原设Cpu_core
def reset_cpu_setting(ssh_os):
    cmd = r'cd {0};./unitool -w ActiveCpuCores:0'.format(SutConfig.UNI_PATH)
    logging.info("Modify cpu setting to default setting by unipwd tool")
    if not BmcLib.force_reset():
        logging.info('power off-on fail')
        return False
    if not icx2pAPI.ping_sut():
        logging.info('boot linux-suse fail')
        return False
    if not set_cpu_by_unitool(ssh_os, cmd):
        logging.info('set_cpu_by_unitool fail')
        return False
    return True


#  function Module, TC205,TC206,TC207 调用
def cpu_cores_active_enable(ssh_os, num, set_n):
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
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
        assert SetUpLib.boot_with_hotkey(Key.F11, "Boot Manager Menu", 300)
        assert SetUpLib.enter_menu(Key.DOWN, ["SUSE Linux Enterprise\(LUN0\)"], 20, "Welcome to GRUB")
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, 170)
        logging.info("Suse_OS Boot Successful")
        ### 每个CPU下只有num个core。
        res1 = SshLib.execute_command(ssh_os, r'lscpu | grep " per socket" ').replace('\n', '').split(':')[-1].strip()
        if int(res1) == num:
            logging.info("**Core Enable pass**")
        else:
            logging.info("**Core Enable eorro**")
            return False
        # 在smbios4中检查：Core数量为总数，Core Enable为num，线程数为Enabled核数的两倍 #
        smbios4_Core_Count = SshLib.execute_command(ssh_os, r'dmidecode -t 4 | grep "Core Count" ').replace('\n', '').split(':')[-1].strip()
        logging.info("**Core_Count = {}**".format(smbios4_Core_Count))
        smbios4_Core_Enabled = SshLib.execute_command(ssh_os, r'dmidecode -t 4 | grep "Core Enabled" ').replace('\n', '').split(':')[-1].strip()
        logging.info("**Core_Enabled = {}**".format(smbios4_Core_Enabled))
        smbios4_Thread_Count = SshLib.execute_command(ssh_os, r'dmidecode -t 4 | grep "Thread Count" ').replace('\n', '').split(':')[-1].strip()
        logging.info("**Thread_Count = {}**".format(smbios4_Thread_Count))
        if smbios4_Core_Count == '28' and smbios4_Core_Enabled == str(num) and smbios4_Thread_Count == str(num*2):
            logging.info("**Core_Count pass, Core_Enabled pass,Thread_Count pass")
        else:
            logging.info("**Core eorro**")
            return False
        # 使用 unitool 还原 'Active Processor Cores', '<All>' #
        logging.info("正常还原")
        assert reset_cpu_setting(ssh_os)
        return True
    except AssertionError:
        logging.info("异常还原")
        reset_cpu_setting(ssh_os)
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
def cpu_cores_active_enable_1(ssh_os):
    tc = ('205', '[205]Testcase_CoreDisable_002', 'Enable 1 CPU core test')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    num = 1
    set_n = 28
    try:
        assert cpu_cores_active_enable(ssh_os, num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


def cpu_cores_active_enable_middle(ssh_os):
    tc = ('206', '[206]Testcase_CoreDisable_003', 'Enable middle-num CPU core test')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    num = 14
    set_n = 14
    try:
        assert cpu_cores_active_enable(ssh_os, num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


def cpu_cores_active_enable_max(ssh_os):
    tc = ('207', '[207]Testcase_CoreDisable_004', 'Enable max-1 CPU core test')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    num = 27
    set_n = 1
    try:
        assert cpu_cores_active_enable(ssh_os, num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU disable Processor Cores,the system runs normally
# Precondition: unitool
# OnStart: NA
# OnComplete: suse Page
def cpu_cores_disable_sys_normally(ssh_os):
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
        while n < 5:  #系统反复复位，暂定4次
            # boot suse #
            assert SetUpLib.continue_to_bootmanager()
            assert SetUpLib.enter_menu(Key.DOWN, ["SUSE Linux Enterprise\(LUN0\)"], 20, "Welcome to GRUB")
            assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, 200)
            logging.info("Suse_OS Boot Successful")
            res = SshLib.execute_command(ssh_os, r'date')
            logging.info("system reboot pass, system-Time is : {} ".format(res))
            assert BmcLib.force_reset()
            n = n+1
        # 还原系统设置
        logging.info("正常还原")
        assert reset_cpu_setting(ssh_os)
        result.log_pass()
    except AssertionError:
        logging.info("异常还原")
        reset_cpu_setting(ssh_os)
        result.log_fail(capture=True)


# Unitool to modify the number of CPU cores,in bios and OS Verify CPU Cores
# Precondition: Unitool
# OnStart: NA
# OnComplete: suse Page
def cores_customized_by_unitool(ssh_os):
    tc = ('209', '[TC209] CoreDisable_007', 'Unitool to modify the number of CPU cores,in bios and OS Verify CPU Cores')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    ACT_CPU_CORES = ['Active Processor Cores', '<20>']
    cmd_set_20 = r'cd {0};./unitool -w ActiveCpuCores:20'.format(SutConfig.UNI_PATH)
    cmd_checkin = r'lscpu | grep " per socket" '
    try:
        assert SetUpLib.boot_with_hotkey(Key.F11, "Boot Manager Menu", 300)
        assert SetUpLib.enter_menu(Key.DOWN, ["SUSE Linux Enterprise\(LUN0\)"], 20, "Welcome to GRUB")
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE, 170)
        logging.info("Suse_OS Boot Successful")
        assert set_cpu_by_unitool(ssh_os, cmd_set_20)
        # 进入Bios ，验证 unitool修改是否成功
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.verify_info(ACT_CPU_CORES, 20)
        logging.info("bios setting checkin")
        # 进入 OS，验证 unitool修改是否成功
        assert BmcLib.force_reset()
        assert icx2pAPI.ping_sut()
        SshLib.execute_command(ssh_os, r'cd {0};insmod ufudev.ko'.format(SutConfig.UNI_PATH))
        res = SshLib.execute_command(ssh_os, cmd_checkin).replace('\n', '').split(':')[-1].strip()
        logging.info(res)
        if int(res) == 20:
            logging.info('checkin cpu_core - pass')
        else:
            logging.info('checkin cpu_core - fail')
            return
        # 还原系统设置
        logging.info("正常还原")
        assert reset_cpu_setting(ssh_os)
        result.log_pass()
    except AssertionError:
        logging.info("异常还原")
        reset_cpu_setting(ssh_os)
        result.log_fail(capture=True)