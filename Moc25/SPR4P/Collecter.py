import os
import re
import sys
import csv
import logging
from pathlib import Path
import importlib

module_ignore = [
    "__init__",
    "Os",
    "Legacy",
    "UpdateBIOS",
    "RedfishTest",
    "VariableLoop",
]


def get_proj_dir():
    """依据 "Collecter.py" 的相对路径获取项目文件"""
    proj_dir = Path(__file__).parent
    if proj_dir.exists():
        return proj_dir
    logging.error(f"Project directory not exixts: {proj_dir}")
    exit()


def get_case_dir(proj_dir: Path):
    """获取项目文件夹下的测试用例 "TestCase" 路径"""
    testcase_dir = proj_dir / "TestCase"
    if testcase_dir.exists():
        return testcase_dir
    logging.error(f"TestCase directory not exists: {testcase_dir}")
    exit()


def get_case_files(testcase_dir: Path):
    """读取项目文件夹下的所有测试用例 ".py" 文件"""
    case_modules = []
    py_names = []
    for pyfile in testcase_dir.iterdir():
        if pyfile.stem.startswith("_"):
            continue
        if pyfile.stem not in module_ignore:
            case_modules.append(pyfile)
            py_names.append(pyfile.stem)
    logging.info(f"Collecting testcase function.")
    for pyname in py_names:
        logging.debug(f"  -- {pyname}.py")
    return case_modules


def get_csv_file():
    """读取项目文件夹下的 "AllTest.csv" 文件"""
    csv_file = get_proj_dir() / "AllTest.csv"
    if csv_file.exists():
        return csv_file
    logging.error(f"{csv_file} is not exists")
    exit()


def read_csv_list():
    """读取项目文件夹下的csv文件中已有的测试列表"""
    csv_file = get_csv_file()
    with open(csv_file, "r", encoding="utf-8") as fcsv:
        test_list = list(csv.reader(fcsv))
        header = test_list[0]
        body = test_list[1:]
        exist_case = []
        for line in body:
            if not line:
                continue
            exist_case.append(line[0])
        return exist_case


def get_test_func_from_py(case_files):
    """从每个py文件中收集以 "@core.test_case"装饰器 装饰的用例函数"""
    case_flag = "\n@\s*core.test_case\s*\(.+?\n(?:@.*\n)*def (\w+)\(.*?\)"
    test_cases = []
    for pyfile in case_files:
        with open(pyfile, "r", encoding="utf-8") as py:
            data = py.read()
            tc = re.findall(case_flag, data)
            if not tc:
                continue
            for t in tc:
                test_cases.append(f"{pyfile.stem}.{t}()")
    return test_cases


def add_test_scope(func_list, group=None, release=None, daily=True, weekly=True):
    """新发现的用例在加入列表时，默认为 "daily" / "weekly" """
    test_func_scope = []
    if group and group not in ["os", "equip", "fulldebug", "legacy"]:
        logging.error(f"Invalid group type: {group}")
    group = group if group else ""
    release = "Yes" if release else ""
    daily = "Yes" if daily else ""
    weekly = "Yes" if weekly else ""
    csv_list = read_csv_list()
    for func in func_list:
        if func in csv_list:
            continue
        test_func_scope.append([func, group, release, daily, weekly])
    return test_func_scope


def name_match(str_a, str_b):
    """按命名相似度匹配最相似的函数名，放在一起"""
    len_a = len(str_a)
    len_b = len(str_b)
    min_len = min(len_a, len_b)
    while min_len:
        if str_a[0:min_len] == str_b[0:min_len]:
            return str_a[0:min_len]
        min_len -= 1


def remove_csv_error_list():
    """检查CSV文件,,如果定义的函数名在代码中没有找到,则删除此行"""
    prj_dir = get_proj_dir()
    prj_stem = prj_dir.stem
    tc_dir = get_case_dir(prj_dir)
    tc_stem = tc_dir.stem
    csv_file = get_csv_file()

    with open(csv_file, "r", encoding="utf-8") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]

    for index, line in enumerate(case_lines):
        if not line:
            continue
        func_name = line[0]
        func_find = re.findall("(\w+)\.(\w+)\(", func_name)
        if not func_find:
            logging.error(f"CSV line error: [{index+1}] {func_name}")
        module, func = func_find[0]
        try:
            mod_imp = importlib.import_module(f".{module}", package=f"{prj_stem}.{tc_stem}")
        except Exception as e:
            case_lines.pop(index)
            logging.error(f"Remove testcase [{module}.{func} ({index+1})]: {e}")
            continue
        if not hasattr(mod_imp, func):
            case_lines.pop(index)
            logging.error(f"Remove testcase [{module}.{func} ({index+1})]: function not found")

    with open(csv_file, "w", encoding="utf-8", newline="") as fcsv:
        csv_w = csv.writer(fcsv)
        csv_w.writerows([header] + case_lines)


def add_csv_new_list(new_funcs):
    """将新发现的测试用例加入csv文件中，csv中已经有的用例列表保持不变"""
    csv_file = get_csv_file()
    with open(csv_file, "r+", encoding="utf-8", newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        insert_dict = {}

        for new_line in new_funcs:
            new_name = new_line[0]
            name_match_index = 0
            insert_row = -1
            for index, line in enumerate(case_lines):
                if not line:
                    continue
                func_name = line[0]
                name_matched = name_match(new_name, func_name)
                if name_matched:
                    name_match_tmp = len(name_matched)
                    if name_match_tmp >= name_match_index:
                        name_match_index = name_match_tmp
                        insert_row = index + 1

            while insert_row in insert_dict:
                if insert_row >= 0:  # 已经有的模块全部放到一起
                    insert_row += 1
                else:
                    insert_row -= 1  # 新发现的模块，自动放到文件末尾，同一模块中的放在一起

            insert_dict[insert_row] = new_line

        for row, func_line in insert_dict.items():
            logging.info(f"Add {func_line} to row: {row+1 if row>0 else row}")
            case_lines.insert(row, func_line)

        fcsv.seek(0)
        csv_w = csv.writer(fcsv)
        csv_w.writerows([header] + case_lines)


def collect_testcase():
    root = get_proj_dir()
    path = get_case_dir(root)
    pyfiles = get_case_files(path)
    funcs = get_test_func_from_py(pyfiles)
    new_cases = add_test_scope(funcs)
    remove_csv_error_list()
    add_csv_new_list(new_cases)


def gen_test_scope(key_words: list):
    """根据N个关键字自动生成测试列表，生成列表的daily列为Yes"""
    print(f"根据关键字生成daily测试列表: {key_words}")
    test_scope = []
    csv_file = get_csv_file()
    with open(csv_file) as f:
        csv_load = csv.reader(f)
        for index, line in enumerate(list(csv_load)):
            if index == 0:
                test_scope.append(line)
                continue
            for k in key_words:
                if k.lower() in line[0].lower():
                    line_add_daily = line[:3] + ["Yes"] + line[4:]
                    test_scope.append(line_add_daily)
                    break
    gen_csv = f"{'_'.join(key_words)}.csv"
    with open(gen_csv, "w", newline="\n") as fw:
        csv_write = csv.writer(fw)
        csv_write.writerows(test_scope)
    if os.path.exists(gen_csv):
        print(f"共有{len(test_scope)}个测试用例")
        print(f"生成测试CSV文件: {gen_csv}")


if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        gen_test_scope(args)
    else:
        collect_testcase()
