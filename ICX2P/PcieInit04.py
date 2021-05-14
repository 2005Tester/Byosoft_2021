import logging
import re
from Core import SerialLib
from Core.SutInit import Sut
from ICX2P.BaseLib import SetUpLib, BmcLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from Report import ReportGen


# Test case ID: TC630-TC650

##########################################
#           PCIe Test Cases              #
##########################################

# MMIOL资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_PCIeResource_001():
    tc = ('630', '[TC630] Testcase_PCIeResource_001', 'MMIOL资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        assert BmcLib.force_reset()
        resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 10, 120, 3)
        assert resource, "invalid CPU Resource Allocation Table"
        cpu0_stk0 = r"CPU0[\S\s]+?(Stk00[\S\s]+?)(Stk01.+)"
        data = re.search(cpu0_stk0, resource)
        assert data, "Invalid Resource Data"
        stk0 = data.group(1).split(" | ")[5].split(" - ")[0]
        stk1 = data.group(2).split(" | ")[5].split(" - ")[0]
        assert stk0, "MMIOL Base not found"
        size_serial = hex(int(stk1, 16) - int(stk0, 16))
        assert size_serial, "MMIOL Size not found"
        logging.info(f"MMIOL_BASE: {stk0.lower()}")
        logging.info(f"MMIOL_SIZE: {size_serial}")
        logging.info("MMIOL Resource Test Pass")
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()


# MMIOH资源分配静态表测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_PCIeResource_002():
    tc = ('631', '[TC631] Testcase_PCIeResource_002', 'MMIOH资源分配静态表测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    MMIOH = "MMIO High Base"
    MMIOH_size = "MMIO High Granularity Size"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, "Common RefCode Configuration"], 10, "MMIO High Base")
        MMIOH_value = SetUpLib.get_option_value([MMIOH, "<.+>"], Key.DOWN, 8)
        MMIOH_size = SetUpLib.get_option_value([MMIOH_size, "<.+>"], Key.DOWN, 8)
        base_scale = 40 if MMIOH_value[-1] == "T" else 30  # T / G
        base_setup = hex(int(MMIOH_value[:-1]) * (1 << base_scale))
        size_setup = hex(int(MMIOH_size[:-1]) * (1 << 30))  # G
        assert BmcLib.force_reset()
        resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 10, 120, 3)
        assert resource, "invalid CPU Resource Allocation Table"
        cpu0_stk0 = r"CPU0[\S\s]+?(Stk00[\S\s]+?)(Stk01.+)"
        data = re.search(cpu0_stk0, resource)
        assert data, "Invalid Resource Data"
        stk0 = data.group(1).split(" | ")[6].split(" - ")[0].replace(" ", "")
        stk1 = data.group(2).split(" | ")[6].split(" - ")[0].replace(" ", "")
        size_serial = hex(int(stk1, 16) - int(stk0, 16))
        logging.info(f"MMIOH_BASE: setup={base_setup} | serial print={stk0.lower()}")
        logging.info(f"MMIOH_SIZE: setup={size_setup} | serial print={size_serial}")
        assert int(stk0, 16) == int(base_setup, 16), "MMIO High Base Mis-Match"
        assert int(size_serial, 16) == int(size_setup, 16), "MMIO High Size Mis-Match"
        logging.info("MMIOH Resource Test Pass")
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()


# BIOS提供MMIOH资源调整选项测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_PCIeResource_003():
    tc = ('632', '[TC632] Testcase_PCIeResource_003', 'BIOS提供MMIOH资源调整选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    base_default = "13T"
    size_default = "64G"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG, "Common RefCode Configuration"], 10, "MMIO High Base")
        base_value = SetUpLib.get_option_value(["MMIO High Base", "<.+>"], Key.DOWN, 8)
        size_value = SetUpLib.get_option_value(["MMIO High Granularity Size", "<.+>"], Key.DOWN, 8)
        logging.info(f"Get MMIOH Base = {base_value}")
        logging.info(f"Get MMIOH Size = {size_value}")
        assert base_value == base_default, f'Expected MMIOH Base default is "{base_default}", actually is "{base_value}"'
        assert size_value == size_default, f'Expected MMIOH Size default is "{size_default}", actually is "{size_value}"'
        result.log_pass()
    except Exception as e:
        logging.info(e)
        result.log_fail()


# BIOS提供PCIe 64bit decode选项测试
# Precondition: BIOS默认密码
# OnStart: NA
# OnComplete: NA
def Testcase_PCIeResource_005():
    tc = ('633', '[TC633] Testcase_PCIeResource_005', 'BIOS提供PCIe 64bit decode选项测试')
    result = ReportGen.LogHeaderResult(tc, SutConfig.LOG_DIR)
    try:
        # Set Config
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
        assert SetUpLib.locate_option(Key.DOWN, ["PCI 64-Bit Resource Allocation", "<Enabled>"], 16
                                      ), "Check default value failed"
        logging.info('Check "PCI 64-Bit Resource Allocation" default = <Enabled> pass')
        SetUpLib.send_key(Key.F6)
        assert SetUpLib.verify_options(Key.DOWN, [["PCI 64-Bit Resource Allocation", "<Disabled>"]], 16)
        SetUpLib.send_keys(Key.SAVE_RESET)
        # Check Config
        re_allocate = SerialLib.cut_log(Sut.BIOS_COM,
                                        "Resource allocation Failed. Enabling 64bit MMIO allocation and resetting the system",
                                        "START_SOCKET_0_DIMMINFO_TABLE", 10, 120, 5)
        # 未触发资源不足正常 Disable
        if not re_allocate:
            assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
            assert SetUpLib.verify_options(Key.DOWN, [["PCI 64-Bit Resource Allocation", "<Disabled>"]], 16)
            logging.info('Check "PCI 64-Bit Resource Allocation" change to <Disabled> pass')
            result.log_pass()
            return True
        # 触发资源不足会强制分配4G以上，且选项强制 Enable
        assert re.search(r"CPU0[\S\s]+?(Stk00[\S\s]+?)(Stk01.+)", re_allocate), "Enabling 64bit MMIO allocation Failed"
        logging.info("Resource allocation Failed. Enabling 64bit MMIO allocation and resetting the system.")
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
        assert SetUpLib.verify_options(Key.DOWN, [["PCI 64-Bit Resource Allocation", "<Enabled>"]], 16)
        logging.info('Check "PCI 64-Bit Resource Allocation" force restore to <Enabled> pass')
        result.log_pass()
        return True
    except Exception as e:
        logging.info(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()

