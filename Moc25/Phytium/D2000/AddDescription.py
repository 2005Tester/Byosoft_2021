import csv
import re

from pathlib import Path

fun_nam_dict = {}

test_case_list = []

case_name_list = []

for pyfile in Path('TestCase').iterdir():
    if not pyfile.stem.startswith('_'):
        test_case_list.append(pyfile.stem)
        with open(pyfile, 'r', encoding='utf-8') as f:
            data = f.read()
            for i in re.findall("\n@\s*core.test_case\s*\(.+?\ndef (\w+\().*?\)", data):
                case_name_list.append(pyfile.stem + '.' + i + ')')
            tc = re.findall("\n@\s*core.test_case\s*\(.+?\[.+\].+,\s*'(.+)'\s*\)\)\ndef (\w+\().*?\)", data)
            for i in tc:
                fun_nam_dict[i[1]] = i[0]

print(test_case_list)


def add_description(csv_path):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        for i in case_lines:
            for key, value in fun_nam_dict.items():
                if key in i[0]:
                    if len(i) == 5:
                        i.append(value)
                    elif len(i) >= 5:
                        i[5] = value
        fcsv.seek(0)
        csv_w = csv.writer(fcsv)
        if header[-1] != 'Description':
            header.append('Description')
        csv_w.writerows([header] + case_lines)
    fcsv.close()


def del_description(csv_path):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        for i in case_lines:
            if len(i) == 6:
                i.pop(-1)
    fcsv.close()
    with open(csv_path, "w+", encoding='utf-8', newline="") as fcsv:
        fcsv.seek(0)
        csv_w = csv.writer(fcsv)
        while True:
            if header[-1] == 'Description':
                header = header[0:-1]
            else:
                break
        csv_w.writerows([header] + case_lines)
    fcsv.close()


def set_all_weekly_yes(csv_path):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        for i in case_lines:
            if i:
                if i[4] != 'Yes':
                    i[4] = 'Yes'
        fcsv.seek(0)
        csv_w = csv.writer(fcsv)
        csv_w.writerows([header] + case_lines)
    fcsv.close()


# 删除所有的Yes
def del_all_yes(csv_path):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        for i in case_lines:
            if i:
                i[2] = ''
                i[3] = ''
                i[4] = ''
    fcsv.close()
    with open(csv_path, "w+", encoding='utf-8', newline="") as fcsv:
        fcsv.seek(0)
        csv_w = csv.writer(fcsv)
        csv_w.writerows([header] + case_lines)
    fcsv.close()


def set_module_yes(csv_path, change_list, type_name):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        for i in case_lines:
            if i:
                if i[0].split('.')[0] in change_list:
                    if type(type_name) == list:
                        for j in type_name:
                            if j.lower() == 'release':
                                i[2] = 'Yes'
                            elif j.lower() == 'daily':
                                i[3] = 'Yes'
                            elif j.lower() == 'weekly':
                                i[4] = 'Yes'
                    else:
                        if type_name.lower() == 'release':
                            i[2] = 'Yes'
                        elif type_name.lower() == 'daily':
                            i[3] = 'Yes'
                        elif type_name.lower() == 'weekly':
                            i[4] = 'Yes'
    fcsv.close()
    with open(csv_path, "w+", encoding='utf-8', newline="") as fcsv:
        fcsv.seek(0)
        csv_w = csv.writer(fcsv)
        csv_w.writerows([header] + case_lines)
    fcsv.close()


def del_spe_case(csv_path, ignore_list):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        ignore = []
        for i in ignore_list:
            if type(i) == list:
                ignore += i
            elif type(i) == str:
                ignore.append(i)

        for i in case_lines:
            if i:
                if i[0] in ignore:
                    i[2] = ''
                    i[3] = ''
                    i[4] = ''
        fcsv.close()
        with open(csv_path, "w+", encoding='utf-8', newline="") as fcsv:
            fcsv.seek(0)
            csv_w = csv.writer(fcsv)
            csv_w.writerows([header] + case_lines)
        fcsv.close()


def check_testcase_in_csv(csv_path, add=False):
    with open(csv_path, "r+", encoding='utf-8', newline="") as fcsv:
        case_list = list(csv.reader(fcsv))
        header = case_list[0]
        case_lines = case_list[1:]
        csv_case_list = [i[0] for i in case_lines if i]
        add_case = []
        for i in case_name_list:
            if i not in csv_case_list:
                add_case.append(i)
        if add == True:
            for i in add_case:
                case_lines.append([i, '', '', '', ''])
        else:
            for i in add_case:
                print(i)
        fcsv.close()
        with open(csv_path, "w+", encoding='utf-8', newline="") as fcsv:
            fcsv.seek(0)
            csv_w = csv.writer(fcsv)
            csv_w.writerows([header] + case_lines)
        fcsv.close()


if __name__ == '__main__':

    # 文件编码格式必须为'utf-8'
    # add_description('AllTest.csv')  # 添加case描述

    # del_description('AllTest.csv')#删除已添加的case描述

    # del_all_yes('AllTest.csv')#删除所有的Yes

    # set_all_weekly_yes('AllTest.csv')  # weekly设置所有case为Yes

    change_list = ['BootTest', 'ByoCfgTest', 'ByoDmiTest', 'FlashTest', 'PCIETest', 'SecureBootTest', 'SetupPswTest',
                   'SetUpTest', 'SmbiosTest', 'UpdateTest']
    # set_module_yes('AllTest.csv', change_list, ['release', 'daily', 'weekly'])  # 根据TestCase文件夹下测试模块,添加Yes

    # check_testcase_in_csv('AllTest.csv', add=False)  # 检查csv文件中是否包含所有的testcase
