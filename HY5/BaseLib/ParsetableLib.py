# -*- coding: utf-8 -*-
# !/bin/bash

"""
Script_: ParsetableLib.py

Description:
        Set the BIOS Variable options (Auto) - uni tool v0.0.3, supported by byo crew;
        For now, this script is only for the data analysis;
        If the DUT fails to boot properly due to the large number of variable Settings,
        y need to manually power down and update the BIOS firmware version to the latest
        # Author: arthur
        文件系统介绍：
        一级目录：
                 original_csv - 当前byo基线表中unitool工具支持设置de变量清单
        子程序函数介绍：
                 read_ed_option()   # 遍历当前Enable/Disable变量设置不同值
                 read_index_option()   # 遍历当前index变量设置不同值
                 read_other_option() # 遍历当前others变量设置不同值
                 主程序中def函数模块可根据需求注释或打开, 三大类独立可执行,
                 如用于初期BIOS选项验证, 一次修改100变量, 则注释子程序块,
                 单独变量遍历设置打开子程序块即可，默认为注释状态,
        python lib ENV: pandas and openpyxl modules should be installed before test,
"""

import os
import shutil
import logging

import pandas as pd
from collections import defaultdict
from HY5.Config import SutConfig

# python env imports
# try:
#     import pandas
# except ModuleNotFoundError as e:
#     print("Should install pandas")
#     import os
#     p = os.popen("pip install pandas")
#     print(p.read())
#     import pandas
# finally:
#     print("import pandas successfully")

# csv file定义
csv_file = '{0}.csv'.format(SutConfig.Env.PROJECT_NAME)
ed_csv_file = '{0}_ed.csv'.format(SutConfig.Env.PROJECT_NAME)
index_csv_file = '{0}_index.csv'.format(SutConfig.Env.PROJECT_NAME)
other_csv_file = '{0}_others.csv'.format(SutConfig.Env.PROJECT_NAME)
# 全局dict
ed_dict_base = defaultdict(list)
index_dict_base = defaultdict(list)
others_dict_base = defaultdict(list)
# ed options
ed_dict = {}
# index options
index_dict = {}
# other options
others_dict = {}
# defined value定义
code_str = 'utf-8-sig'
row_name = 'Value.1'
col_name = 'VariableName.1'
uni_name = 'UniTool Setting Support'
col_name_new = 'VariableName'
# boot type, key words
# boot_type = 'UefiOptimizedBootToggle'
ed_keys_word = 'Enable|Enabled|Disable|Disabled|Yes'
index_keys_word = 'Index|Use|VariableName'
# (issue) items should not be set;
'IODC'
'PciePhyTestMode'
'DfxSocketDevFuncHide[0]~[255]'

# current dir
cur_path = SutConfig.Env.LOG_DIR
csv_word = 'original_csv'
csv_path = cur_path + '\\' + csv_word


# Read byo bios setup excel file, then save the available data to csv file
def read_xls(file):
    try:
        data = pd.read_excel(file, pd.ExcelFile(file).sheet_names[0],
                             usecols="I, K:L", dtype=str)  # Read the excel
        temp_file = 'temp.csv'
        data_bk = data.to_csv(temp_file, index=False, encoding=code_str)  # To csv file
        data_bk = pd.read_csv(temp_file, encoding=code_str)
        data_bk = data_bk.dropna(axis=0, how='any')
        temp_data = data_bk.drop_duplicates(col_name, keep='last', inplace=False)
        temp_data.to_csv(csv_file, index=False, encoding=code_str)
        os.remove(temp_file)
        return True
    except Exception as e:
        logging.info(str(e))
        # sys.exit()
        return


# Read csv file, save the available items to csv files,
# named "ed - Enable/Disable, index - the item contains index value  and others - Non Enable/Disable"
def read_csv(self):
    try:
        df = pd.read_csv(self, encoding=code_str)
        # read csv
        feature_data_ed = df.iloc[:, 0:3][(df[df.T.index[2]] == 'Y') &
                                          (~df[df.T.index[1]].str.contains(SutConfig.SysCfg.TBD_items, case=True, na=False)) &
                                          (df[df.T.index[0]].str.contains(ed_keys_word, case=False, na=False))]
        print("ed variable:", len(feature_data_ed))
        # index
        feature_data_index = df.iloc[:, 0:3][(~df[df.T.index[1]].str.contains(SutConfig.SysCfg.TBD_items, case=True, na=False)) &
                                             (df[df.T.index[2]].str.contains(index_keys_word, case=False, na=False))]
        print("index variable:", len(feature_data_index))
        # others
        feature_data_others = df.iloc[:, 0:3][(df[df.T.index[2]] == 'Y') &
                                              (~df[df.T.index[1]].str.contains(SutConfig.SysCfg.TBD_items, case=True, na=False)) &
                                              (~df[df.T.index[0]].str.contains(ed_keys_word, case=False, na=False))]
        print("others variable:", len(feature_data_others))
        print("Total supported items:", len(feature_data_ed) + len(feature_data_index) + len(feature_data_others))
        # Move the csv files to a folder
        if os.path.isdir(csv_path):
            shutil.rmtree(csv_path)
        # re-create the folder
        os.mkdir(csv_path)
        feature_data_ed.to_csv(ed_csv_file, index=False, encoding=code_str)
        feature_data_index.to_csv(index_csv_file, index=False, encoding=code_str)
        feature_data_others.to_csv(other_csv_file, index=False, encoding=code_str)
        file_list = os.listdir()
        for i in file_list:
            if os.path.splitext(i)[1] == '.csv':
                try:
                    shutil.move(i, csv_path)
                except Exception as e:
                    print(str(e))

        return True
    except Exception as e:
        logging.debug(str(e))
        return


# Read enabled and disabled items
def read_ed_option():
    try:
        file1 = os.path.join(csv_path, ed_csv_file)
        # Iterate over the variable names
        df1 = pd.read_csv(file1, encoding=code_str)
        df1[col_name] = df1[col_name].str.split('~')
        variable = [' '.join([i.strip().replace('[0]', '') for i in j[0].strip().split('\t')]) for j in df1[col_name]]

        # Move the column 2;
        df1.drop(labels=[col_name], axis=1, inplace=True)
        df1.insert(0, col_name_new, variable)
        # re-save;
        df1.to_csv(file1, index=None, encoding=code_str)

        value1 = df1.loc[0, ["Value.1"]]
        value2 = value1.map(lambda x: x.split('\n')[2].split(':')[1])

        data = df1.loc[:, [col_name_new, row_name]]
        data[row_name] = data[row_name].str.split('\n')
        for i in range(len(data[col_name_new])):
            for j in range(len(data[row_name][i])):
                ed_dict_base[data[col_name_new][i]].append(data[row_name][i][j])

        # hex to int
        for key, value in ed_dict_base.items():
            for k in value:
                ed_value = k.split(':')
                # len 2
                if len(ed_value) == 2:
                    if ed_value[1].strip().isdigit():
                        ed_dict.setdefault(key, []).append(ed_value[1])
                    else:
                        # hex to int
                        try:
                            ed_value[1] = int(ed_value[1], 16)
                            ed_dict.setdefault(key, []).append(ed_value[1])
                        except Exception as e:
                            print(str(e))
                            print(key, ed_value[1])
                else:
                    # No ready, standby;
                    # print('No value detected;', key, ed_value)
                    pass
        return ed_dict
    except Exception as e:
        logging.debug(str(e))


# Read index items
def read_index_option():
    try:
        file1 = os.path.join(csv_path, index_csv_file)
        # Iterate over the variable names
        df2 = pd.read_csv(file1, encoding=code_str)
        df2[col_name] = df2[col_name].str.split('~')
        variable1 = [' '.join([i.strip().replace('[0]', '') for i in j[0].strip().split('\t')]) for j in df2[col_name]]

        # Move the column 2, remove the issue item - TBD
        df2.drop(labels=[col_name], axis=1, inplace=True)
        df2.insert(0, col_name_new, variable1)
        df2.to_csv(file1, index=None, encoding=code_str)

        data1 = df2.loc[:, [col_name_new, row_name]]

        data1[row_name] = data1[row_name].str.split('\n')
        for i in range(len(data1[col_name_new])):
            for j in range(len(data1[row_name][i])):
                index_dict_base[data1[col_name_new][i]].append(data1[row_name][i][j])

        # value hex to int
        for key, value in index_dict_base.items():
            for k in value:
                index_value = k.split(':')
                if len(index_value) == 2:
                    if index_value[1].strip().isdigit():
                        index_dict.setdefault(key, []).append(index_value[1])
                    else:
                        # hex to int
                        try:
                            index_value[1] = int(index_value[1], 16)
                            index_dict.setdefault(key, []).append(index_value[1])
                            # print(index_value[1])
                        except Exception as e:
                            print(str(e))
                            print(key, index_value[1])
                else:
                    # No ready, standby;
                    # print('No value detected;', key, index_value)
                    pass
        return index_dict
    except Exception as e:
        logging.debug(str(e))


# read others items
def read_other_option():
    try:
        file1 = os.path.join(csv_path, other_csv_file)
        # Iterate over the variable names
        df_others = pd.read_csv(file1, encoding=code_str)
        df_others[col_name] = df_others[col_name].str.split('~')
        variable2 = [' '.join([i.strip().replace('[0]', '') for i in j[0].strip().split('\t')]) for j in df_others[col_name]]
        df_others.drop(labels=[col_name], axis=1, inplace=True)
        df_others.insert(0, col_name_new, variable2)
        df_others.to_csv(file1, index=None, encoding=code_str)

        data2 = df_others.loc[:, [col_name_new, row_name]]
        data2[row_name] = data2[row_name].str.split('\n')
        # fill the na value
        fill_value = data2[row_name].fillna('Value:NA')
        length = data2[col_name_new].str.len()
        for i in range(len(length)):
            for j in range(len(fill_value[i])):
                others_dict_base[data2[col_name_new][i]].append(fill_value[i][j])
        # value hex to int
        for key, value in others_dict_base.items():
            for k in value:
                other_value = k.split(':')
                # len 2
                if len(other_value) == 2:
                    if other_value[1].strip().isdigit():
                        others_dict.setdefault(key, []).append(other_value[1])
                    else:
                        # hex to int
                        try:
                            other_value[1] = int(other_value[1], 16)
                            others_dict.setdefault(key, []).append(other_value[1])
                        except Exception as e:
                            print(str(e))
                            print(key, other_value[1])
                else:
                    # No ready, standby;
                    # print('No value detected;', key, other_value)
                    pass
        return others_dict
    except Exception as e:
        logging.debug(str(e))


# Compare/modify the data... ...整合出区别于当前BIOS默认值一套字典组合,
def cmp(dict1, dict2):
    for key in dict1:
        if dict2[key][0] in dict1[key]:
            dict1[key].remove(dict2[key][0])
    final_dict = {}
    for key in dict1:
        if dict1[key] is None:
            continue
        elif dict1[key] != []:  # list is not None
            final_dict[key] = dict1[key][0]
            dict1[key].pop(0)
    return final_dict


# Main build,
def build(target_file):
    logging.info("Starting auto-test, check the byo setup data,")
    assert read_xls(target_file)  # byo BIOS Setup base line excel
    logging.info("Save available data supported by unitool to csv files'")
    return read_csv(csv_file)
