import random
import yaml
import pandas

from SPR4P.Config import *
from SPR4P.BaseLib import *
from SPR4P.Resource.PowerEfficiency import OptionPath

####################################
# PowerEfficiency Test Case
# TC 2500-2542
####################################


def _power_efficiency_setup_align():
    """将 变量名:整数值 转换为Setup界面的 选项名:选项值"""
    power_base = PlatMisc.root_path() / f"{Env.POWER_EFFICIENCY}"
    pd = pandas.read_csv(power_base, index_col=0, dtype=str)

    setup_name_value = {}
    base_data = PlatMisc.baseline_to_dict()

    def get_value_name_from_num(num, value_dict):
        num_int = int(num, 16) if "0x" in num else int(num, 10)
        for val_name, val_num in value_dict.items():
            if val_name in ["min", "max", "step"]:  # integer
                continue
            if int(val_num, 16) == num_int:
                return val_name
        return num

    for mode in pd.columns:
        setup_name_value[mode] = {}
        for variable in pd.index:
            value = pd.loc[variable, mode]
            if variable not in base_data:
                continue
            if pandas.isna(value):
                logging.warning(f"Value missing: {mode} -> {variable} = {value}")
                continue
            setup = base_data[variable]["setup"]
            setup = re.sub("([()\[\]])", r"\\\1", setup)  # 括号前加斜线
            values = base_data[variable]["values"]
            value = get_value_name_from_num(value, values)
            setup_name_value[mode][setup] = value
    return setup_name_value


class _PowerEfficiencyTest:
    def __init__(self, base: pandas.DataFrame, config=None):
        self.base = base
        self.report = pandas.DataFrame()
        self.fails = {}
        self.reg_fails = {}
        self.config = config
        self.config_data = None

    def check_options_by_unicfg(self, mode_name: str):
        self.report[mode_name] = self.base[mode_name]
        attr_read = Sut.UNITOOL.read(*self.base.index)
        mode_result = {}
        for attr_name, read_value in attr_read.items():
            if read_value is None:
                logging.error(f"Fail to read unicfg value: {mode_name}.{attr_name}")
                self.fails[mode_name][attr_name] = read_value
                continue
            expect_value = str(self.base.loc[attr_name, mode_name])
            expect_value_int = int(expect_value, 16) if ("0x" in expect_value) else int(expect_value, 10)
            read_value_int = int(read_value, 16)  # uniCfg返回值为16进制
            read_value_report = hex(read_value_int) if ("0x" in expect_value) else read_value_int  # 如果csv为16进制,则报告也显示为16进制
            if expect_value_int != read_value_int:
                mode_result[attr_name] = read_value_report
                if mode_name in self.fails:
                    self.fails[mode_name][attr_name] = read_value_report
                else:
                    self.fails[mode_name] = {attr_name: read_value_report}
            else:
                mode_result[attr_name] = "pass"
        self.report[f"{mode_name}_check"] = pandas.Series(mode_result)
        return mode_result

    def load_yml(self) -> dict:
        if not os.path.exists(self.config):
            raise FileExistsError("Dynamic power saving config file not exist")
        with open(self.config, "r", encoding="utf-8") as yf:
            self.config_data = yaml.safe_load(yf)
            return self.config_data

    def check_register_in_os(self, mode_name):
        if self.config_data is None:
            self.load_yml()
        for attr_name, reg_info in self.config_data.items():
            method = reg_info[0]
            if method == "msr":
                if not self.check_msr_bit_in_os(mode_name, attr_name, reg_info):
                    if mode_name in self.reg_fails:
                        self.reg_fails[mode_name].append(attr_name)
                    else:
                        self.reg_fails[mode_name] = [attr_name]
            elif method == "cscripts":
                if not self.check_cscript_reg_bit_in_os(mode_name, attr_name, reg_info):
                    if mode_name in self.reg_fails:
                        self.reg_fails[mode_name].append(attr_name)
                    else:
                        self.reg_fails[mode_name] = [attr_name]
        return not self.reg_fails

    def check_reg_match_with_base(self, attr_name: str, val_dict: dict, reg_value: int, expect_num: str):
        """
        通过寄存器值,返回预期对应的uniCfg变量的整数值
        :param attr_name: 选项的变量名
        :param val_dict: yml配置中的值的名称和预期寄存器值的对应关系  Enable: 1
        :param reg_value: 读到的寄存器值, 0/1/2
        :param expect_num: 预期uniCfg读到的变量值, 0/3/7
        :return:
        """
        if not hasattr(self, "setup_base"):
            self.setup_base = PlatMisc.baseline_to_dict()
        values = self.setup_base[attr_name]["values"]
        values_vk = {int(v, 16): k for k, v in values.items()}  # {1: "Enable"}
        expect_i = int(expect_num, 16) if expect_num.startswith("0x") else int(expect_num)
        if expect_i not in values_vk:
            logging.error(f"Expect unicfg value not defined in setup baseline: {expect_num}")
            return False
        val_expect_name = values_vk[expect_i]
        for _name, _val in val_dict.items():
            if val_expect_name.lower() != _name.lower():
                continue
            if _val == reg_value:
                logging.info(f"[PASS]: [{attr_name}] expect=[{val_expect_name}], register={reg_value}")
                return True
            else:
                logging.error(f"[FAIL]: [{attr_name}] expect=[{val_expect_name}], register={reg_value}")
                return False
        logging.error(f"expect value name missing in config: {val_expect_name}")

    def check_msr_bit_in_os(self, mode_name, attr_name, reg_info):
        logging.info("=" * 60)
        addr = reg_info[1]
        bit = str(reg_info[2])
        attr_kv = reg_info[3]
        expect_value = str(self.base.loc[attr_name, mode_name])
        msr_value = SshLib.execute_command(Sut.OS_SSH, f"cd /root/rw;./rw rdmsr {addr}").strip()
        if "-" in bit:
            bit_range = re.findall("(\d+)-(\d+)", bit)[0]
            msr_bit_val = PlatMisc.read_hex_bit(f"0x{msr_value}", int(bit_range[1]), int(bit_range[0]))
            logging.info(f"{mode_name}.{attr_name} -> msr({addr})={msr_value}, bit[{bit}]={msr_bit_val}")
            return self.check_reg_match_with_base(attr_name, attr_kv, msr_bit_val, expect_value)
        else:
            msr_bit_val = PlatMisc.read_hex_bit(f"0x{msr_value}", int(bit))
            logging.info(f"{mode_name}.{attr_name} -> msr({addr})={msr_value}, bit[{bit}]={msr_bit_val}")
            return self.check_reg_match_with_base(attr_name, attr_kv, msr_bit_val, expect_value)

    def check_cscript_reg_bit_in_os(self, mode_name, attr_name, reg_info):
        logging.info("=" * 60)
        addr = reg_info[1]
        bit = reg_info[2]
        attr_kv = reg_info[3]
        relation_ship = reg_info[4]
        expect_value = str(self.base.loc[attr_name, mode_name])
        reg = PlatMisc.cscripts_rw(addr)
        values_all = list(reg.values())
        relation_map = any(val == hex(1) for val in values_all) if (relation_ship == "any") else all(val == hex(1) for val in values_all)
        reg_val_int = 1 if relation_map else 0
        logging.info(f"{mode_name}.{attr_name} -> {addr} [{bit}]={reg_val_int}")
        return self.check_reg_match_with_base(attr_name, attr_kv, reg_val_int, expect_value)

    def result_summary(self, report_name):
        report_path = PlatMisc.current_test_dir()
        report_file = os.path.join(report_path, report_name)
        stylelog.success(f"Detail test report saved at {report_file}")
        self.report.to_excel(report_file)
        # show test result in test log
        result = False if (self.fails or self.reg_fails) else True
        logging.info(f"Test result: {result}")
        for _mode, _attr in self.reg_fails.items():
            stylelog.fail(f"Register fail: [{_mode}] -> {_attr}")
        for mode, attr_kv in self.fails.items():
            for att_k, att_v in attr_kv.items():
                stylelog.fail(f"UniCfg fail: [{mode}] -> {att_k}={att_v}")
        return result


# @core.test_case(("2500", "[TC2500] Testcase_HpcMode_001", "HPC模式菜单联动检查"))
# def Testcase_HpcMode_001():
#     """
#     Name:       HPC模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为HPC，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2501", "[TC2501] Testcase_GeneralComputingMode_001", "General Computing模式菜单联动检查"))
# def Testcase_GeneralComputingMode_001():
#     """
#     Name:       General Computing模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为General Computing，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2502", "[TC2502] Testcase_IoThroughputMode_001", "I/OThroughput模式菜单联动检查"))
# def Testcase_IoThroughputMode_001():
#     """
#     Name:       I/OThroughput模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为I/OThroughput，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2503", "[TC2503] Testcase_MemoryThroughputMode_001", "MemoryThroughput模式菜单联动检查"))
# def Testcase_MemoryThroughputMode_001():
#     """
#     Name:       MemoryThroughput模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为MemoryThroughput，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2504", "[TC2504] Testcase_ServerSideJavaMode_001", "Server Side Java模式菜单联动检查"))
# def Testcase_ServerSideJavaMode_001():
#     """
#     Name:       Server Side Java模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Server Side Java，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2505", "[TC2505] Testcase_EnergySavingMode_001", "Energy Saving模式菜单联动检查"))
# def Testcase_EnergySavingMode_001():
#     """
#     Name:       Energy Saving模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Energy Saving，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2506", "[TC2506] Testcase_NfvMode_001", "NFV模式菜单联动检查"))
# def Testcase_NfvMode_001():
#     """
#     Name:       NFV模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为NFV，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2507", "[TC2507] Testcase_CustomMode_001", "Custom模式菜单联动检查"))
# def Testcase_CustomMode_001():
#     """
#     Name:       Custom模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下切换能效场景为非Custom后再设置为Custom模式，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2508", "[TC2508] Testcase_CustomMode_002", "默认模式菜单联动检查"))
# def Testcase_CustomMode_002():
#     """
#     Name:       默认模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线；
#                 2、默认配置。
#     Steps:      1、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线Custom模式一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2509", "[TC2509] Testcase_BenchMark_001", "能效菜单选择开关检查"))
# def Testcase_BenchMark_001():
#     """
#     Name:       能效菜单选择开关检查
#     Condition:  1、默认配置；
#                 2、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下检查是否提供能效选择开关，可选值及默认值，有结果A；
#                 2、随机选择一种能效场景，保存重启进Setup菜单，检查联动是否符合预期，有结果B；
#                 3、检查联动选项中DEMT与Static Turbo两个选项是否互斥，有结果C；
#                 4、检查联动选项CKE Power Down使能状态，有结果D；
#     Result:     A：提供能效选择开关，支持13个可选值（见备注），默认为Custom；
#                 B：菜单联动与基线一致；
#                 C：此两个选项无同时Enabled的场景（可以同时Disabled）；
#                 D：除Efficiency、Energy Saving两种模式为Enabled，其余模式均Disabled。
#     Remark:     【选项名称与值对应关系】
#                 0：Custom
#                 1：Efficiency
#                 2：Performance
#                 3：Load Balance
#                 4：High Ras
#                 5：HPC
#                 6：General Computing
#                 7：Low Latency
#                 8：Server Side Java
#                 9：Memory Throughput
#                 10：I/O Throughput
#                 11：Energy Saving
#                 12：NFV
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2510", "[TC2510] Testcase_BenchMark_002", "Efficiency模式菜单联动检查"))
# def Testcase_BenchMark_002():
#     """
#     Name:       Efficiency模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Efficiency，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A；
#                 3、检查联动选项中Pstates与DEMT两个选项是否均Enabled，有结果B；
#                 4、检查联动选项CKE Power Down使能状态，有结果C；
#     Result:     A：菜单联动与基线一致；
#                 B：Pstates、DEMT均为Enabled；
#                 C：CKE Power Down为Enabled。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2511", "[TC2511] Testcase_BenchMark_003", "Efficiency模式频率调节"))
# def Testcase_BenchMark_003():
#     """
#     Name:       Efficiency模式频率调节
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Efficiency，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A；
#                 3、检查联动选项中Pstates与DEMT两个选项是否均Enabled，有结果B；
#                 4、检查联动选项CKE Power Down使能状态，有结果C；
#     Result:     A：菜单联动与基线一致；
#                 B：Pstates、DEMT均为Enabled；
#                 C：CKE Power Down为Enabled。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2512", "[TC2512] Testcase_BenchMark_004", "Efficiency模式能效测试"))
# def Testcase_BenchMark_004():
#     """
#     Name:       Efficiency模式能效测试
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Efficiency，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A；
#                 3、检查联动选项中Pstates与DEMT两个选项是否均Enabled，有结果B；
#                 4、检查联动选项CKE Power Down使能状态，有结果C；
#     Result:     A：菜单联动与基线一致；
#                 B：Pstates、DEMT均为Enabled；
#                 C：CKE Power Down为Enabled。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2513", "[TC2513] Testcase_BenchMark_005", "Performance模式菜单联动检查"))
# def Testcase_BenchMark_005():
#     """
#     Name:       Performance模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Performance，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2514", "[TC2514] Testcase_BenchMark_006", "Load Balance模式菜单联动检查"))
# def Testcase_BenchMark_006():
#     """
#     Name:       Load Balance模式菜单联动检查
#     Condition:  1、已获取能效联动菜单基线。
#     Steps:      1、启动进Setup菜单，电源管理界面下设置能效场景为Load Balance，保存退出；
#                 2、启动进Setup菜单，检查能效联动是否符合预期，有结果A。
#     Result:     A：菜单联动与基线一致。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2515", "[TC2515] Testcase_BenchMark_008", "Efficiency场景长时间测试"))
# def Testcase_BenchMark_008():
#     """
#     Name:       Efficiency场景长时间测试
#     Condition:
#     Steps:      1、按键进入Setup菜单，选择Performance Profile->PowerEfficiency场景，反复复位3次，有结果A。
#     Result:     A：系统运行正常。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2516", "[TC2516] Testcase_BenchMark_010", "Performance场景长时间测试"))
# def Testcase_BenchMark_010():
#     """
#     Name:       Performance场景长时间测试
#     Condition:
#     Steps:      1、按键进入Setup菜单，选择Performance Profile->Performance场景，反复复位3次，有结果A。
#     Result:     A：系统运行正常。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2517", "[TC2517] Testcase_BenchMark_012", "Load Balance场景长时间测试"))
# def Testcase_BenchMark_012():
#     """
#     Name:       Load Balance场景长时间测试
#     Condition:
#     Steps:      1、按键进入Setup菜单，选择Performance Profile->Load Balance场景，反复复位3次，有结果A。
#     Result:     A：系统运行正常。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2518", "[TC2518] Testcase_VRD_003", "其他Benchmark场景下电流负偏配置检查"))
# def Testcase_VRD_003():
#     """
#     Name:       其他Benchmark场景下电流负偏配置检查
#     Condition:  1、使用165W以上的CPU
#     Steps:      1、单板上电，进入BIOS Setup 菜单，选择除Linpack外的其他场景；
#                 2、进入OS，使用uniCfg 工具，查看CurrentUnderReport值是否为0，有结果A；
#                 3、遍历所有非Linpack场景。
#     Result:     A：非Linpack场景，CurrentUndeReport值都是0。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2521", "[TC2521] Testcase_DEMT_001", "DEMT菜单测试"))
def Testcase_DEMT_001():
    """
    Name:       DEMT菜单测试
    Condition:
    Steps:      1、单板正常上电，进入Setup菜单，查看DEMT菜单状态，有结果A。
    Result:     A：提供DEMT开关，默认Disabled。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG, key=Key.UP)
        assert SetUpLib.get_option_value(Msg.DEMT) == Msg.DISABLE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail





# @core.test_case(("2522", "[TC2522] Testcase_DEMT_002", "打开DEMT功能测试"))
# def Testcase_DEMT_002():
#     """
#     Name:       打开DEMT功能测试
#     Condition:  已安装Windows并上传RW/PTU1.4及以上工具
#     Steps:      1、单板正常上电，进入Setup菜单，使能DEMT；
#                 2、进入Windows，使用PTU工具给CPU加压，加压过程中使用RW工具观察0x84（CPU占用率）和0x85（当前P状态）调节情况，有结果A。
#     Result:     A：动态调频正常，CPU能处于低频率高占用率，具体参考各CPU频率和占用率对应表。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2523", "[TC2523] Testcase_DEMT_003", "关闭DEMT功能测试"))
# def Testcase_DEMT_003():
#     """
#     Name:       关闭DEMT功能测试
#     Condition:  已安装Windows并上传RW/PTU1.4及以上工具
#     Steps:      1、单板正常上电，进入Setup菜单，关闭DEMT；
#                 2、进入Windows，使用PTU工具给CPU加压，加压过程中使用RW工具观察0x84（CPU占用率）和0x85（当前P状态）调节情况，有结果A。
#     Result:     A：关闭DEMT后不再支持动态调频，0x84、0x85为0。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2524", "[TC2524] Testcase_StaticTurbo_001", "静态Turbo设置菜单检查"))
def Testcase_StaticTurbo_001():
    """
    Name:       静态Turbo设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，Socket界面下查看是否提供Static Turbo设置菜单，可选值及默认值，有结果A。
    Result:     A：提供静态Turbo控制开关，Auto、Manual、Disable可选，默认Disabled。
    Remark:
    """
    values = ["Auto", "Manual", Msg.DISABLE]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.STATIC_TURBO), values)
        assert SetUpLib.get_option_value(Msg.STATIC_TURBO) == Msg.DISABLE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("2525", "[TC2525] Testcase_StaticTurbo_002", "静态Turbo为Auto时功能测试"))
# def Testcase_StaticTurbo_002():
#     """
#     Name:       静态Turbo为Auto时功能测试
#     Condition:  1、已知CPU的标准频率a和Turbo频率b。
#     Steps:      1、启动进Setup菜单，Socket界面下设置Static Turbo为Auto，设置频率c∈[a，b]，F10保存重启；
#                 2、启动进OS，查看CPU运行频率，有结果A；
#                 3、给CPU加压，查看CPU运行频率，有结果A.
#     Result:     A：实际频率在cb之间动态调整。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2526", "[TC2526] Testcase_StaticTurbo_003", "静态Turbo为Manual时功能测试"))
# def Testcase_StaticTurbo_003():
#     """
#     Name:       静态Turbo为Manual时功能测试
#     Condition:  1、已知CPU的标准频率a和Turbo频率b。
#     Steps:      1、启动进Setup菜单，Socket界面下设置Static Turbo为Manual，设置频率c∈[a，b]，F10保存重启；
#                 2、启动进OS，查看CPU运行频率，有结果A；
#                 3、给CPU加压，查看CPU运行频率，有结果A.
#     Result:     A：实际频率为c。
#     Remark:     1、Manual场景下，因压力模型不一致，若超过TDP，频率还是会降低；
#                 2、TDP：热设计功耗。
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2527", "[TC2527] Testcase_StaticTurbo_004", "静态Turbo为Disable时功能测试"))
# def Testcase_StaticTurbo_004():
#     """
#     Name:       静态Turbo为Disable时功能测试
#     Condition:  1、已知CPU的标准频率a和Turbo频率b、最低频率c；
#     Steps:      1、启动进Setup菜单，Socket界面下设置Static Turbo为Disabled，F10保存重启；
#                 2、启动进OS，查看CPU运行频率，有结果A；
#                 3、给CPU加压，查看CPU运行频率，有结果B.
#     Result:     A：不加压时运行在最低频率c；
#                 B：加压时运行在Turbo频率b。
#     Remark:     1、默认开启Turbo Mode，加压时跑Turbo频率。
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2528", "[TC2528] Testcase_StaticTurbo_005", "静态Turbo频率异常值设置"))
# def Testcase_StaticTurbo_005():
#     """
#     Name:       静态Turbo频率异常值设置
#     Condition:  1、已知CPU的标准频率a和Turbo频率b。
#     Steps:      1、启动进Setup菜单，Socket界面下设置Static Turbo为Manual，设置频率c<a，F10保存重启进OS，查看CPU运行频率，有结果A；
#                 2、启动进Setup菜单，Socket界面下设置Static Turbo频率c>b，F10保存重启进OS，查看CPU运行频率，有结果A；
#     Result:     A：实际频率为a；
#                 B：实际频率为b。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2529", "[TC2529] Testcase_StaticTurbo_006", "能效场景下设置静态Turbo测试"))
# def Testcase_StaticTurbo_006():
#     """
#     Name:       能效场景下设置静态Turbo测试
#     Condition:  1、已知CPU的标准频率a和Turbo频率b。
#     Steps:      1、启动进Setup菜单，Socket界面下设置能效场景为非Custom模式，同时设置静态Turbo为Manual，设置频率c∈[a，b]，F10保存重启；
#                 2、启动进OS，查看CPU运行频率，有结果A；
#                 3、遍历所有可设置的能效模式，重复执行步骤1~2。
#     Result:     A：实际运行为对应能效场景下频率。
#     Remark:
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2530", "[TC2530] Testcase_HWP_001", "BIOS提供HWP菜单选项测试"))
def Testcase_HWP_001():
    """
    Name:       BIOS提供HWP菜单选项测试
    Condition:
    Steps:      1、上电启动进Setup菜单，检查HWP选项及默认值与可选值，结果A；
                2、遍历设置HWP可选值，保存退出，检查启动情况，结果B。
    Result:     A：存在HWP选项且默认Disable，可选Disable、Native Mode、OOB Mode、Native Mode without Legacy Support四个选项。
                B：启动BIOS和OS正常，无异常复位/挂死等现象。
    Remark:     Advanced->Socket Configuration->Advanced Power Mgmt. Configuration->Hardware PM State Control
    """
    values = [Msg.DISABLE, "Native Mode", "Out of Band Mode", "Native Mode with No Legacy Support"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG)
        assert SetUpLib.enter_menu(Msg.HW_P_STATE)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.HWP), values)
        assert SetUpLib.get_option_value(Msg.HWP) == Msg.DISABLE
        for value in values:
            assert SetUpLib.set_option_value(Msg.HWP, value, save=True)
            assert MiscLib.ping_sut(Env.OS_IP, Env.BOOT_DELAY)
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG, key=Key.UP)
            assert SetUpLib.enter_menu(Msg.HW_P_STATE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("2531", "[TC2531] Testcase_HWP_002", "Idle状态下HWP不同模式功能验证"))
# def Testcase_HWP_002():
#     """
#     Name:       Idle状态下HWP不同模式功能验证
#     Condition:
#     Steps:      1、上电启动进Setup菜单，设置HWP选项为Native，保存退出；
#                 2、启动进OS，静置5分钟以上，观察CPU频率及功耗情况，有结果A；
#                 3、遍历设置HWP可选值，保存退出，重复步骤2。
#     Result:     A：1）、Native 模式下， CPU可以跑到最低频，同时功耗可以维持在最低；
#                    2）、Diabled情况下，HWP 不参与调节频率及功耗，CPU频率维持最低频率；
#                    3）、OOB需要带外配置，频率不随负载变化，一直维持在带外设置的频率。
#     Remark:     1、Advanced->Socket Configuration->Advanced Power Mgmt. Configuration->Hardware PM State Control
#                 2、static turbo联动OOB选项，可通过设置static turbo频率观察OOB
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2532", "[TC2532] Testcase_HWP_003", "满载状态下HWP不同模式功能验证"))
# def Testcase_HWP_003():
#     """
#     Name:       满载状态下HWP不同模式功能验证
#     Condition:
#     Steps:      1、上电启动进setup菜单，设置HWP选项为Native，保存退出；
#                 2、启动进OS，使用ptu工具加压，观察CPU频率及功耗情况，有结果A；
#                 3、遍历设置HWP可选值，保存退出，重复步骤2。
#     Result:     A：1）、Native 模式下，根据ptu设置的负载， CPU可以跑到最高频，同时功耗可以维持在最高；
#                    2）、Diabled情况下，HWP 不参与调节频率及功耗，CPU频率维持在最高频率；
#                    3）、OOB需要带外配置，频率不随负载变化，一直维持在带外设置的频率。
#     Remark:     1、Advanced->Socket Configuration->Advanced Power Mgmt. Configuration->Hardware PM State Control
#                 2、static turbo联动OOB选项，可通过设置static turbo频率观察OOB
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2533", "[TC2533] Testcase_Ufs_001", "UFS设置菜单检查"))
def Testcase_Ufs_001():
    """
    Name:       UFS设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，P状态配置界面下检查是否存在UFS设置菜单，有结果A。
    Result:     A：存在UFS菜单选项，Enabled，Disabled_Max，Disabled_Min三个可选项；默认Enabled。
    Remark:
    """
    values = ["Enabled", "Disabled_Max", "Disabled_Min"]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG)
        assert SetUpLib.enter_menu(Msg.CPU_ADV_PM_TUN)
        assert SetUpLib.get_option_value(Msg.UFS, key=Key.UP) == Msg.ENABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.UFS, key=Key.UP), values)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("2534", "[TC2534] Testcase_Ufs_002", "UFS功能测试_Enabled"))
# def Testcase_Ufs_002():
#     """
#     Name:       UFS功能测试_Enabled
#     Condition:  1、PTU、RW工具已上传OS；
#                 2、已知CPU的Ucore频率范围[a,b]；
#                 3、设置UFS选项为Enabled。
#     Steps:      1、启动进OS，空闲状态下，PTU工具查看Uncore频率值，RW工具读取MSR 0x621寄存器值，有结果A；
#                 2、加压情况下，PTU工具查看Uncore频率值，RW工具读取MSR 0x621寄存器值，有结果B；
#     Result:     A：PTU查看Uncore频率为a*100，0x621结果为a；
#                 B：PTU查看Uncore频率为b*100，0x621结果为b。
#     Remark:
#                 1、./rw rdmsr 0x620获取规格频率范围（如读取结果为0C18，则最小值为0C，最大值为18）
#                 2、./rw rdmsr 0x621获取实际频率（取低2bit值）
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2535", "[TC2535] Testcase_Ufs_003", "UFS功能测试_Disaled_Min"))
# def Testcase_Ufs_003():
#     """
#     Name:       UFS功能测试_Disaled_Min
#     Condition:  1、PTU、RW工具已上传OS；
#                 2、已知CPU的Ucore频率范围[a,b]；
#                 3、设置UFS选项为Disaled_Min。
#     Steps:      1、启动进OS，空闲状态下，PTU工具查看Uncore频率值，RW工具读取MSR 0x621寄存器值，有结果A；
#                 2、加压情况下，PTU工具查看Uncore频率值，RW工具读取MSR 0x621寄存器值，有结果A；
#     Result:     A：PTU查看Uncore频率为a*100，0x621结果为a。
#     Remark:
#                 1、./rw rdmsr 0x620获取规格频率范围（如读取结果为0C18，则最小值为0C，最大值为18）
#                 2、./rw rdmsr 0x621获取实际频率（取低2bit值）
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2536", "[TC2536] Testcase_Ufs_004", "UFS功能测试_Disaled_Max"))
# def Testcase_Ufs_004():
#     """
#     Name:       UFS功能测试_Disaled_Max
#     Condition:  1、PTU、RW工具已上传OS；
#                 2、已知CPU的Ucore频率范围[a,b]；
#                 3、设置UFS选项为Disaled_Max。
#     Steps:      1、启动进OS，空闲状态下，PTU工具查看Uncore频率值，RW工具读取MSR 0x621寄存器值，有结果A；
#                 2、加压情况下，PTU工具查看Uncore频率值，RW工具读取MSR 0x621寄存器值，有结果A；
#     Result:     A：PTU查看Uncore频率为b*100，0x621结果为b。
#     Remark:
#                 1、./rw rdmsr 0x620获取规格频率范围（如读取结果为0C18，则最小值为0C，最大值为18）
#                 2、./rw rdmsr 0x621获取实际频率（取低2bit值）
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("2540", "[TC2540] Testcase_RrqIrq_004", "RRQ选项合法值校验"))
def Testcase_RrqIrq_004():
    """
    Name:       RRQ选项合法值校验
    Condition:  1、Local or Remote Threshold设置为Manual。
    Steps:      1、启动进Setup菜单，Uncore界面下检查RRQ Threshold选项Help信息有效值范围，有结果A；
                2、随机输入a∈[1,31]，检查能否设置成功，有结果B；
                3、输入a∉[1,31]，检查能否设置成功，有结果C。
    Result:     A：RRQ Threshold有效范围为[1,31]，31表示关闭；
                B：a设置成功；
                C：a值无法设置成功。
    Remark:     1、仅支持十进制输入。
                此选项已经隐藏，通过uniCfg工具验证
    """
    try:
        assert SetUpLib.boot_to_default_os()
        for n in range(0, 33):
            set_n = hex(n)[2:]
            result = Sut.UNITOOL.write(**{Attr.RRQ_THLD_V: set_n})
            if 1 <= n <= 31:
                assert result, "result should be true"
            else:
                assert not result, "result should be false"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2541", "[TC2541] Testcase_RrqIrq_005", "Manual模式时RRQ设置测试"))
def Testcase_RrqIrq_005():
    """
    Name:       Manual模式时RRQ设置测试
    Condition:  1、Local or Remote Threshold设置为Manual。
    Steps:      1、启动进Setup菜单，Uncore界面下设置RRQ Threshold选项值为31，F10保存重启；
                2、启动进OS，执行"lspci -s 7f:1d.1 -xxxx"命令查看420字节[4:0]bit数值，有结果A；
                3、启动进Setup菜单，随机设置RRQ Threshold选项值a∈[1,31)，F10保存重启；
                4、启动进OS，执行"lspci -s 7f:1d.1 -xxxx"命令查看420字节[4:0]bit数值，有结果A；
    Result:     A：RRQ Thresholds寄存器[4:0]数值为0x1F，表示关闭;
                B：RRQ Thresholds寄存器[4:0]数值转换为十进制为a。
    Remark:     # 原测试步骤有变更，当前平台修改选项为 "RRQ Count Threshold"
    """
    cmd_read = "lspci -s 7f:1d.1 -xxxx |grep 420:"

    def set_rrq_and_verify(thld):
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL)
        assert SetUpLib.set_option_value(Msg.RRQ_THLD, f"{thld}", save=True, integer=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_UNCORE_GENERAL)
        assert SetUpLib.get_option_value(Msg.RRQ_THLD, integer=True) == f"{thld}"
        assert SetUpLib.back_to_front_page(highlight=Msg.HOME_PAGE)
        SetUpLib.send_key(Key.ENTER)
        assert MiscLib.ping_sut(Env.OS_IP, timeout=Env.BOOT_DELAY)
        read_str1 = SshLib.execute_command(Sut.OS_SSH, cmd_read, print_result=True)
        assert read_str1, f"invalid data: {cmd_read}"
        byte_4_0 = "".join(re.findall("420: ([0-9a-fA-F]+)", read_str1))
        assert PlatMisc.read_hex_bit(int(byte_4_0, 16), 4, 0) == thld, f"lspci reg420[4:0] != {thld}"
        return True

    try:
        assert set_rrq_and_verify(thld=31)

        random_rrq = random.choice(range(1, 31))
        logging.info(f"Test RRQ = {random_rrq}")
        assert set_rrq_and_verify(thld=random_rrq)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2542", "[TC2542] Testcase_DramRapl_001", "菜单项DRAM RAPL选单检查"))
def Testcase_DramRapl_001():
    """
    Name:       菜单项DRAM RAPL选单检查
    Condition:
    Steps:      1、进入Setup菜单，检查DRAM RAPL 菜单项，有结果A。
    Result:     A：存在DRAM RAPL菜单项，可选Disabled、Enabled， 默认值为Enabled。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**{Attr.DRAM_RAPL: 1})
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# Precondition: 配置好unitool, 准备好
# 依据能效菜单基线文件,验证所有能效场景，其关联选项是否配置正确
# Testcase_HpcMode_001
# Testcase_GeneralComputingMode_001
# Testcase_IoThroughputMode_001
# Testcase_MemoryThroughputMode_001
# Testcase_ServerSideJavaMode_001
# Testcase_EnergySavingMode_001
# Testcase_NfvMode_001
# Testcase_CustomMode_001
# Testcase_CustomMode_002
# Testcase_BenchMark_001
# Testcase_BenchMark_002
# Testcase_BenchMark_003
# Testcase_BenchMark_004
# Testcase_BenchMark_005
# Testcase_BenchMark_006
# Testcase_BenchMark_007
# Testcase_BenchMark_008
# Testcase_BenchMark_009
# Testcase_BenchMark_010
# Testcase_BenchMark_011
# Testcase_BenchMark_012
# Testcase_VRD_003
# Testcase_VRD_004
@core.test_case(('2543', '[TC2543] Testcase_BenchMark_001', '遍历能效场景模式并检查联动菜单'))
def power_efficiency_mode_loop():
    power_efficiency_csv = PlatMisc.root_path() / f"{Env.POWER_EFFICIENCY}"
    if not os.path.exists(power_efficiency_csv):
        logging.error(f"能效基线文件不存在: {power_efficiency_csv}")
        return core.Status.Skip

    power_base = pandas.read_csv(power_efficiency_csv, index_col=0)
    bmc_warning = {}

    try:
        bmc_event = BmcLib.bmc_warning_check().message  # get bmc health state before test
        test = _PowerEfficiencyTest(power_base)

        for mode_name in power_base:
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_ADV_PM_CFG)
            assert SetUpLib.set_option_value(Msg.POWER_EFFICIENCY, mode_name, save=True)
            assert SetUpLib.boot_to_default_os(reset=False, timeout=SutConfig.Env.BOOT_DELAY*2)
            test.check_options_by_unicfg(mode_name)

            warn_message = BmcLib.bmc_warning_check().message
            if warn_message != bmc_event:
                bmc_warning[mode_name] = BmcLib.bmc_warning_check().message

        for warn_mode in bmc_warning:
            stylelog.warning(f'[Warning] Power efficiency = {warn_mode} (BMC warning detected)')

        result = test.result_summary("power_efficiency_mode_loop.xlsx")
        assert result and (not bmc_warning)
        return core.Status.Pass
    except Exception as e:
        logging.info(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2544", "[2544] 在Setup下检查能效联动关系", "Setup界面遍历设置能效模式，并检查联动关系"))
def check_power_efficiency_in_setup():
    log_path = os.path.join(Env.LOG_DIR, var.get("current_test"))
    test_status = {}
    try:
        setup_mode_value = _power_efficiency_setup_align()
        path_options = OptionPath.MENU_OPTIONS
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        for mode, values_want in setup_mode_value.items():
            assert SetUpLib.back_to_setup_toppage()
            assert SetUpLib.enter_menu([Msg.CPU_CONFIG, Msg.ADV_POWER_MGF_CONFIG], Key.DOWN)
            assert SetUpLib.set_option_value(Msg.POWER_EFFICIENCY, mode)
            test_status[mode] = {}
            for path_option in path_options:
                path, options = path_option
                assert SetUpLib.back_to_setup_toppage()
                if not SetUpLib.enter_menu(path, Key.DOWN):
                    core.capture_screen(img_dir=log_path, img_file=f"{mode}_{path}")
                    continue
                for op in options:
                    if op not in values_want:
                        logging.error(f"Setup option '{op}' not found in baseline file")
                        continue
                    is_integer = True if op in OptionPath.integer else False
                    key = Key.UP if op in OptionPath.key_up else Key.DOWN
                    try_cnt = 5 if op in OptionPath.less_try else 35
                    try:
                        value_read = SetUpLib.get_option_value(op, key, try_counts=try_cnt, integer=is_integer)
                    except Exception:
                        core.capture_screen(img_dir=log_path, img_file=f"{mode}_{op}")
                        continue
                    result = "pass" if value_read == values_want.get(op) else value_read
                    test_status[mode][op] = result

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        core.capture_screen()
        return core.Status.Fail
    finally:
        df = pandas.DataFrame(test_status)
        df.to_csv(os.path.join(var.get('log_dir'), "setup_power_efficiency_result.csv"), na_rep="")
        BmcLib.clear_cmos()


@core.test_case(2545, description="动态能效功能遍历验证")
def Testcase_Dynamic_PowerEfficiency():
    """
    Name:       动态能效功能遍历验证
    Condition:
    Steps:      1、启动进OS, 登录BMC网页，在BIOS设置页面, 设置能效模式, 不重启, 检查联动菜单对应的MSR寄存器值, 有结果A。
                2、遍历设置能效模式, 不重启, 检查联动菜单对应的MSR寄存器值, 有结果A
    Result:     A：能效模式对应的联动菜单的寄存器值与动态能效表格匹配, 在不重启的情况下, 可以实时更新。
    Remark:     具体动态能效参考相关能效基线文件.
    """
    try:
        power_efficiency_csv = PlatMisc.root_path() / f"{Env.POWER_EFFICIENCY}"
        dynamic_config = PlatMisc.root_path() / "Resource/PowerEfficiency/dynamic_power_saving.yml"

        if not os.path.exists(power_efficiency_csv):
            logging.error(f"能效基线文件不存在: {power_efficiency_csv}")
            return core.Status.Skip

        power_base = pandas.read_csv(power_efficiency_csv, index_col=0)
        test = _PowerEfficiencyTest(power_base, config=dynamic_config)
        power_modes = list(power_base.columns)
        for mode_name in power_modes[1:] + [power_modes[0]]:
            assert SetUpLib.boot_to_default_os()
            assert BMC_WEB.set_dynamic_power_saving(mode_name)
            test.check_register_in_os(mode_name)
            assert SetUpLib.boot_to_default_os()
            test.check_options_by_unicfg(mode_name)

        assert test.result_summary("dynamic_power_saving_test_report.xlsx")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
