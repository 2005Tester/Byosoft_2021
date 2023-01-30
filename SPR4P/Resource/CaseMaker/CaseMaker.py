import os
import re
import sys
import shutil
import pandas


ExcelHeader = {
    "module": "Feature_Name",
    "number": "Testcase_Number",
    "name": "Testcase_Name",
    "condition": "Testcase_Pretreatment Condition",
    "step": "Testcase_Test Steps",
    "result": "Testcase_Expected Result",
    "remark": "Testcase_Remark",
    "auto": "Auto",
    }


ModuleName = {
    "初始化CPU需求": "Cpu",
    "初始化内存需求": "Memory",
    "PCH初始化需求": "Pch",
    "PCIe初始化需求": "Pcie",
    "输入输出需求": "BasicIO",
    "启动设备支持需求": "BootDevice",
    "SETUP设置需求": "BiosSetup",
    "BMC通信需求": "Bmc",
    "SMBIOS需求": "Smbios",
    "单板设计相关需求": "BoardDesign",
    # "Intel DCPMM支持需求": "DCPMM",
    "服务器定制化需求": "Custom",
    "第三方组件管理需求": "ThirdParty",
    "启动操作系统需求": "BootOS",
    # "Intel DCPMM RAS": "DcpmmRAS",
    # "RAS（CPU）需求": "CpuRAS",
    # "RAS（内存）需求": "MemoryRAS",
    # "RAS（PCIE）需求": "PcieRAS",
    "ACPI标准规范需求": "Acpi",
    "安全类规格需求": "Security",
    "能效需求": "PowerEfficiency",
    "装备需求": "Equipment",
    # "FDM需求": "FDM",
    # "资料需求": "Resource",
    "支持产品实现single build要求": "SingleBuild",
    "BIOS支持公有云": "PublicCloud",
    "X86 V7服务器需求": "X86V7",
    "DFX需求": "Dfx",
    "安全及隐私保护6.0要求": "Privacy",
    # "版本发布例行": "ReleaseRoutine",
    }


ModuleHeader = """
import os
import re
import time
import logging

from batf import var, core, SshLib, MiscLib, SerialLib
from batf.SutInit import Sut
from SPR4P.Config import SutConfig
from SPR4P.Config.PlatConfig import Key, Msg, BiosCfg
from SPR4P.BaseLib import SetUpLib, PlatMisc, BmcLib, BmcWeb, Update

####################################
# {py_name} Test Case
# TC {module_start}-{module_end}
####################################

"""


TestCase = """
# @core.test_case(("{id_num}", "[TC{id_num}] {tc_num}", "{tc_name}"))
# def {tc_num}():
#     \"\"\"
#     Name:       {tc_name}
#     Condition:  {tc_cond}
#     Steps:      {tc_step}
#     Result:     {tc_result}
#     Remark:     {tc_remark}
#     \"\"\"
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()

"""


def create_folder(file):
    """清理原来的文件夹和文件，重新生成"""
    file_name = os.path.splitext(os.path.split(file)[1])[0]
    if os.path.exists(f"./{file_name}"):
        shutil.rmtree(f"./{file_name}")
    os.makedirs(f"./{file_name}")
    return file_name


def load_excel(tc_file):
    """加载Excel文件，并筛选ExcelHeader定义的列"""
    tc: pandas.DataFrame = pandas.read_excel(tc_file, sheet_name=0, header=0)
    tc = tc[list(ExcelHeader.values())]
    tc = tc.fillna("")
    return tc


def get_modules(pd, index_name, pattern="【(.+)】"):
    """根据FeatureName索引，以及索引的正则，让同一类Feature放在同一个py文件中"""
    modules = {}
    last_mod = None
    for row, mod in pd[index_name].items():
        if pandas.isna(mod):
            continue
        flag_found = "".join(re.findall(pattern, mod))
        if flag_found:
            if last_mod:
                modules[last_mod].append(row - 1)
            modules[flag_found] = [row]
            last_mod = flag_found
    modules[last_mod].append(len(pd[index_name]) - 1)
    return modules


def doc_align(lines):
    """Tesecase 说明信息对齐"""
    if isinstance(lines, str):
        return re.sub("\n", "\n# " + " " * 16, lines)
    return lines


def module_id_range_start(id_end):
    """每个py文件的ID从整百开始"""
    if id_end % 100 == 0:
        return id_end
    return (id_end + 100) // 100 * 100


def create_testcase(pd, report_dir):
    """创建测试用例文件, 包括导入包和ID范围，以及所有的测试用例函数"""
    index_module = ExcelHeader["module"]
    index_num = ExcelHeader["number"]
    index_name = ExcelHeader["name"]
    index_cond = ExcelHeader["condition"]
    index_step = ExcelHeader["step"]
    index_result = ExcelHeader["result"]
    index_remark = ExcelHeader["remark"]

    id_num = 1000  # Test ID start
    modules = get_modules(pd, index_name=index_module)

    for mod_name, mod_range in modules.items():
        py_name = ModuleName.get(mod_name)
        if not py_name:
            continue
        module_start = module_id_range_start(id_num)
        id_num = module_start
        py_file = os.path.join(f"./{report_dir}/{py_name}.py")

        for tc_row, tc_num in pd[index_num].items():
            if pandas.isna(tc_num):
                continue
            if tc_row < mod_range[0]:
                continue
            if tc_row > mod_range[1]:
                break
            is_auto = pd.loc[tc_row, ExcelHeader["auto"]]
            if pandas.isna(is_auto) or (not bool(is_auto)):
                continue

            # Create test module header
            if not os.path.exists(py_file):
                with open(py_file, "w", newline="\n", encoding="utf-8") as mod_py:
                    mod_py.write(ModuleHeader.format(py_name=py_name, module_start=module_start, module_end=module_start))

            # Create testcase method
            with open(py_file, "a", newline="\n", encoding="utf-8") as mod_py:
                tc_name = doc_align(pd.loc[tc_row, index_name])
                tc_name_find = re.findall(f"\d+\s*(.+)", tc_name)
                tc_name = tc_name_find[0] if tc_name_find else tc_name
                tc_cond = doc_align(pd.loc[tc_row, index_cond])
                tc_step = doc_align(pd.loc[tc_row, index_step])
                tc_result = doc_align(pd.loc[tc_row, index_result])
                tc_remark = doc_align(pd.loc[tc_row, index_remark])
                mod_py.write(TestCase.format(id_num=id_num, tc_num=tc_num, tc_name=tc_name, tc_cond=tc_cond,
                                             tc_step=tc_step, tc_result=tc_result, tc_remark=tc_remark))
            id_num += 1
        # Update test module range
        if os.path.exists(py_file):
            with open(py_file, "r+", newline="\n", encoding="utf-8") as py_file:
                py_read = py_file.read()
                py_file.seek(0)
                update_tc_range = re.sub(f"# TC {module_start}-{module_start}",
                                         f"# TC {module_start}-{id_num-1}", py_read)
                py_file.write(update_tc_range)

        print(f"Create Testcase: {py_name}: [{module_start}-{id_num-1}]")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("请输入测试用例文件路径!")
        sys.exit(0)

    excel_file = sys.argv[1]
    if not os.path.exists(excel_file):
        print("文件未找到!")
        sys.exit(0)

    pd = load_excel(excel_file)
    report_name = create_folder(excel_file)
    create_testcase(pd, report_name)
