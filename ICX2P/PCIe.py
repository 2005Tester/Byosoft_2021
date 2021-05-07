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
