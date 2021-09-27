import logging
from TCE.Config import SutConfig
from TCE.BaseLib import SetUpLib
from TCE.Config.PlatConfig import Key, Msg
from TCE.Config.SutConfig import SysCfg
from Report import ReportGen


# Test case ID: TC100-150

##########################################
####        UNCORE Test Cases        #####    
##########################################

# Testcase_RRQIRQ_001
def rrqirq():
    tc = ('101', '[TC101] Testcase_RRQIRQ_001', 'Setup菜单RRQ和IRQ选项默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    msg = 'Uncore Status'
    if not SetUpLib.enter_menu(Key.DOWN, Msg.PATH_UNCORE_GENERAL, 20, msg):
        result.log_fail()
        return

    logging.info("Find option and verify default value.")
    if not SetUpLib.locate_option(Key.DOWN, ["Local/Remote Threshold", "<Auto>"], 20):
        result.log_fail()
        return

    logging.info("Verify supported values.")
    values = 'DisabledAutoLowMediumHighManual'
    if not SetUpLib.verify_supported_values(values):
        result.log_fail()
        return
    logging.info("Verify default value of RRQ and IRQ when set to manual.")
    SetUpLib.send_keys([Key.F5, Key.F5, Key.F5, Key.F5])
    manual_opts = [["IRQ Threshold", "\[7\]"],["RRQ Threshold", "\[7\]"]]
    if not SetUpLib.verify_options(Key.DOWN, manual_opts, 12):
        result.log_fail()
        return

    result.log_pass()
    return True


# 检查默认状态PCIE_Root_Port带宽分配是否正确（不包括插入不同Rise/Slimline/NVME,带宽可变的root port)
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def pcie_port_bandwidth_check():
    tc = ('102', '[TC102] Testcase_PCIeInit_001', 'PCIe带宽默认值测试')
    result = ReportGen.LogHeaderResult(tc)
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 15, Msg.IIO_CONFIG)
        for cpu in range(SysCfg.CPU_CNT):  # loop cpu
            cpu_menu = f"CPU {cpu + 1} Configuration"
            assert SetUpLib.enter_menu(Key.DOWN, [cpu_menu], 15, "PCIe Completion Timeout")
            for port, bwidth in SysCfg.PCIE_MAP[cpu].items():  # loop root port
                port_menu = f"Port {port.upper()}"
                assert SetUpLib.enter_menu(Key.DOWN, [port_menu], 15, "PCIe Port")
                assert SetUpLib.verify_info([rf"PCIe Port Link Max\s+Max Width {bwidth.lower()}"], 25), f"Socket{cpu}：port {port} = {bwidth} fail"
                logging.info(f"Socket{cpu}：port {port} = {bwidth} pass")
                SetUpLib.send_key(Key.ESC)
            SetUpLib.send_key(Key.ESC)
        result.log_pass()
    except AssertionError as e:
        logging.info(e)
        result.log_fail(capture=True)

# Testcase_Boot_Fail_Policy_001, 检查Boot Fail Policy默认为Boot Retry,且选项值为Boot Retry/Cold Boot/None
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_boot_fail_policy_001():
    tc = ('103', 'Verify Boot Fail Policy Information', 'Verify Boot Fail Policy is Boot Retry')
    result = ReportGen.LogHeaderResult(tc)
    Boot_Fail_Policy_Retry = ['<Boot Retry>']
    Boot_Fail_Policy_Value = 'Boot RetryCold BootNone'
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Key.DOWN, Boot_Fail_Policy_Retry, 20)
        assert SetUpLib.verify_supported_values(Boot_Fail_Policy_Value)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)

# Testcase_Com_Resource_001确认存在串口资源选项Select Base I/O Address且默认值为3F8
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_com_resource_001():
    tc = ('104', 'Verify COM Information', 'Verify Boot Fail Policy is Boot Retry')
    result = ReportGen.LogHeaderResult(tc)
    PATH_MISC_CFG = ['Miscellaneous Configuration']
    Select_Base_IO = ['<3F8>\s+Select Base I/O Address']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, PATH_MISC_CFG, 20, 'Select Base I/O Address')
        logging.info("**Verify Select Base I/O Address default value is 3F8**")
        assert SetUpLib.verify_info(Select_Base_IO, 20)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)

# Testcase_NetworkMode_001检查网口模式选项存在Dedicated\Auto\shared-PCIE\Onboard OCP Shared四种模式，默认值为Dedicated
# Author: OuYang
# Precondition:
# OnStart:
# OnComplete: SetUp
def testcase_NetworkMode_001():
    tc = ('105', 'Verify iBMC Network Mode Information', 'Verify iBMC Network Mode ')
    result = ReportGen.LogHeaderResult(tc)
    PAGE_SERVER_MGMT = 'iBMC version'
    PATH_IBMC_CFG = ['iBMC LAN Configuration']
    iBMC_Network_Mode_Dedicate =['<Dedicated>']
    iBMC_Network_Mode_Value = 'DedicatedAutoShared\-PCIEOnboard OCP Shared'
    try:
        assert SetUpLib.boot_to_page(PAGE_SERVER_MGMT)
        assert SetUpLib.enter_menu(Key.DOWN, PATH_IBMC_CFG, 20, '<Dedicated>')
        assert SetUpLib.locate_option(Key.DOWN, iBMC_Network_Mode_Dedicate, 20)
        logging.info("**Verify iBMC Network Mode Address default value is Dedicated**")
        assert SetUpLib.verify_supported_values(iBMC_Network_Mode_Value)
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail(capture=True)