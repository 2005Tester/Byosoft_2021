import logging
from Core import SerialLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import icx2pAPI, SetUpLib
from Report import ReportGen


# Cpu Related Test case, test case ID, TC200-299

##########################################
#              CPU Test Cases            #
##########################################

# Testcase_CPU_COMPA_015, 016 - TBD
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Uncore status page
def upi_link_status(serial, ssh):
    tc = ('200', '[TC200]UPI link链路检测测试', 'CPU兼容性测试')
    result = ReportGen.LogHeaderResult(tc, serial)

    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_UNCORE_STATUS, 22, 'Uncore Status'):
        result.log_fail()
        return

    if not icx2pAPI.verify_setup_options_down(serial, SutConfig.upi_state, 4):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_UFS_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup P-State control page
def ufs_default_value(serial, ssh):
    tc = ('201', '[TC201]Testcase_UFS_001', 'UFS默认值测试')
    result = ReportGen.LogHeaderResult(tc, serial)

    if not SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED):
        result.log_fail()
        return

    if not SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_PSTATE_CTL, 20, Msg.CPU_P_STATE):
        result.log_fail()
        return

    if not icx2pAPI.verify_setup_options_up(serial, SutConfig.ufs, 4):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ESC, Key.ENTER])
    if not SetUpLib.locate_option(serial, Key.DOWN, ["UFS", "<Enabled>"], 12):
        result.log_fail()
        return
    SerialLib.send_key(serial, Key.ENTER)
    if not SerialLib.is_msg_present(serial, r'Disabled_MaxDisabled_Min', 10):
        result.log_fail()
        return
    result.log_pass()
    return True


# Testcase_Static_Turbo_001
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Advanced power management page
def static_turbo_default(serial, ssh):
    tc = ('202', '[TC202]Testcase_Static_Turbo_001', '静态Turbo默认值测试')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    static_turbo_default = ['Static Turbo', '<Disabled>']
    try:
        assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_ADV_PM_CFG, 20, Msg.ADV_POWER_MGF_CONFIG)
        assert SetUpLib.locate_option(serial, Key.DOWN, static_turbo_default, 10)
        SerialLib.send_key(serial, Key.ENTER)
        assert SerialLib.is_msg_present(serial, r'AutoManualDisabled')
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU and DIMM information
# Precondition: NA
# OnStart: NA
# OnComplete: Setup Memory Topology Page
def cpu_mem_info(serial, ssh):
    tc = ('203', '[TC203]CPU Memory Information', 'Verify CPU and Memory Information')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(serial, Key.DOWN, Msg.PATH_PER_CPU_INFO, 20, 'BSP Revision')
        logging.info("**Verify CPU Information**")
        assert SetUpLib.verify_info(serial, SutConfig.CPU_info, 20)
        SerialLib.send_keys_with_delay(serial, [Key.ESC, Key.ESC])
        assert SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        logging.info("**Verify Memory Information**")
        assert SetUpLib.verify_info(serial, SutConfig.DIMM_info, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU Active Processor Cores information
# Precondition: NA
# OnStart: NA
# OnComplete: Processor Configuration Page
def cpu_cores_active(serial, ssh):
    tc = ('204', '[204]Testcase_CoreDisable_001', 'CPU Active Processor Cores information')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    list_info = ['All', '27', '26', '25', '24', '23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    try:
        assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(serial, ssh, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.locate_option(serial, Key.DOWN, ACT_CPU_CORES, 20)
        SerialLib.send_key(serial, Key.ENTER)
        logging.info("**Active Processor Cores**")
        assert icx2pAPI.verify_setup_options_up(serial, list_info, 28)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)


# Verify CPU Active Processor Cores information
# Precondition: NA
# OnStart: NA
# OnComplete: suse Page

#  function Module
def cpu_cores_active_enable(serial, ssh, ssh_os,num, set_n):
    ACT_CPU_CORES = ['Active Processor Cores', '<All>']
    try:
        assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(serial, ssh, Msg.PATH_PRO_CFG, 20, Msg.ACT_CPU_CORES)
        assert SetUpLib.locate_option(serial, Key.DOWN, ACT_CPU_CORES, 20)
        SerialLib.send_keys_with_delay(serial, [Key.F6]*set_n)
        logging.info("**Active Processor Cores**")
        SerialLib.send_keys_with_delay(serial, [Key.F10, Key.Y], 5)
        logging.info("**reboot**")
        assert SetUpLib.continue_to_page(serial, Msg.PAGE_ADVANCED)
        # assert SetUpLib.boot_to_page(serial, ssh, Msg.PAGE_ADVANCED)
        SerialLib.send_keys_with_delay(serial, Key.ENTER)
        assert SetUpLib.enter_menu(serial, Key.DOWN, [Msg.MEMORY_TOP], 20, 'DIMM000')
        logging.info("**Verify Memory Information**")
        assert SetUpLib.verify_info(serial, SutConfig.DIMM_info, 20)
        ### boot suse
        assert SetUpLib.boot_with_hotkey(serial, ssh, Key.F11, "Boot Manager Menu", 300)
        assert SetUpLib.enter_menu(serial, Key.DOWN, ["SUSE Linux Enterprise\(LUN0\)"], 20, "Welcome to GRUB")
        assert SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE, 170)
        logging.info("Suse_OS Boot Successful")
        ### 每个CPU下只有num个core。
        res1 = SshLib.execute_command(ssh_os, r'lscpu | grep " per socket" ').replace('\n', '').split(':')[-1].strip()
        print("res1 = ", res1)
        if int(res1) == num:
            logging.info("**Core Enable pass**")
        else:
            logging.info("**Core Enable eorro**")
            return False
        ### 在smbios4中检查：Core数量为总数，Core Enable为num，线程数为Enabled核数的两倍
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
        ###使用 unitool 还原 'Active Processor Cores', '<All>'
        logging.info("**restore parameters**")
        SshLib.execute_command(ssh_os, r'cd {0};insmod ufudev.ko'.format(SutConfig.UNI_PATH))
        res = SshLib.execute_command(ssh_os,
                                     r'cd {0};./unitool -w ActiveCpuCores:0'.format(SutConfig.UNI_PATH))
        logging.info(res)
        if len(res) == 0:
            logging.info('blank, maybe the ko module failed')
            return
        elif 'error' in res:
            logging.info("Modify BIOS PWD:Fail")
            return
        return True
    except AssertionError:
        logging.info("Test failed, restore parameters")
        SshLib.execute_command(ssh_os, r'cd {0};insmod ufudev.ko'.format(SutConfig.UNI_PATH))
        SshLib.execute_command(ssh_os,
                                     r'cd {0};./unitool -w ActiveCpuCores:0'.format(SutConfig.UNI_PATH))
        return False


def cpu_cores_active_enable_1(serial, ssh, ssh_os):
    tc = ('205', '[205]Testcase_CoreDisable_002', 'Enable 1 CPU core test')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        num = 1
        set_n = 28
        assert cpu_cores_active_enable(serial, ssh, ssh_os, num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


def cpu_cores_active_enable_middle(serial, ssh, ssh_os):
    tc = ('206', '[206]Testcase_CoreDisable_003', 'Enable middle-num CPU core test')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        num = 14
        set_n = 14
        assert cpu_cores_active_enable(serial, ssh, ssh_os, num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)


def cpu_cores_active_enable_max(serial, ssh, ssh_os):
    tc = ('207', '[207]Testcase_CoreDisable_004', 'Enable max-1 CPU core test')
    result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)
    try:
        num = 27
        set_n = 1
        assert cpu_cores_active_enable(serial, ssh, ssh_os, num, set_n)
        result.log_pass()
    except AssertionError:
        result.log_fail(capture=True)