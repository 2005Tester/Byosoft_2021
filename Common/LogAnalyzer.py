#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import re
import os
import logging
import difflib


class LogAnalyzer:
    def __init__(self, log_dir):
        self.log_dir = log_dir
    #    self.config = config

    @staticmethod
    def load_log(log):
        log_list = []
        if os.path.exists(log):
            with open(log, 'r') as f:
                log_list = f.readlines()
        else:
            logging.info("{0} doesn't exist".format(log))
        return log_list

    # Check difference of two log files
    @staticmethod
    def check_diff(log1, log2):
        logging.info("Comparing {0} and {1}".format(log1, log2))
        try:
            with open(log1, 'r') as f:
                content_log1 = f.read().splitlines()
            with open(log2, 'r') as f:
                content_log2 = f.read().splitlines()
        except FileNotFoundError:
            logging.error("Please check whether log file exists.")
            return True
        d = difflib.Differ()
        diffs = list(d.compare(content_log1, content_log2))
        res = []
        for diff in diffs:
            if not re.search("^\s", diff):
                res.append(diff)
        return res

    def check_bios_log(self):
        ast = 0
        exception = 0
        error = 0
        bios_log = os.path.join(self.log_dir, "serial.log")
        data = self.load_log(bios_log)
        for line in data:
            if re.search("_assert", line, re.IGNORECASE):
                logging.info("Assert found in line {0}".format(data.index(line)+1))
                # logging.info(line)
                ast +=1
            if re.search("X64 Exception", line, re.IGNORECASE):
                logging.info("Exception found in line {0}".format(data.index(line)+1))
                # logging.info(line)
                exception +=1
        if ast == 0:
            logging.info("No assert found in serial log.")
        if exception == 0:
            logging.info("No exception found in serial log.")
    
        if (ast + exception + error) == 0:    
            return True

    def check_cpuinfo(self, cores):
        cpuinfo_log = os.path.join(self.log_dir, "cpuinfo.log")
        with open(cpuinfo_log, 'r') as f:
            data = f.read()
        corenumbers = re.findall("cpu cores\s+:\s+(\d+)", data)
        for num in corenumbers:
            if num == str(cores):
                pass
            else:
                logging.info("Core count is incorrect")
                return 
        logging.info("Core count is correct")
        return True

    # API to check SMBIOS,
    def check_smbios(self, target_path, template_path):
        target_file = ''
        template_file = ''
        num = []
        for file in os.listdir(target_path):
            if 'dmidecode' in os.path.splitext(file)[0]:
                target_file = os.path.join(target_path, file)
                num = re.findall(r"\d+", os.path.splitext(file)[0])

        # write the diff data to files
        result_file = 'diff-{0}.log'.format(''.join(num))

        for file1 in os.listdir(template_path):
            if 'config' in os.path.splitext(file1)[0]:
                template_file = os.path.join(template_path, file1)
            elif 'dmidecode' in os.path.splitext(file1)[0]:
                template_file = os.path.join(template_path, file1)

        try:
            target_list = self.getData(target_file)
            origin_list = self.getData(template_file)
            diff_file = open(os.path.join(target_path, result_file), 'w')
        except Exception:
            logging.info("No file found in log.")
            return

        # break if the type date is none,
        if len(target_list) == 1:
            logging.info('No type date found in template file')
            return False

        diff_list = [[]]
        if 'dmidecode' in template_file.split(os.sep)[-1].split('.')[0]:
            for i in range(1, len(target_list)):
                for j in range(1, len(origin_list)):
                    if target_list[i][0] == origin_list[j][0]:
                        # print('find the type data, start to compare...')
                        for k in range(1, len(target_list[i])):
                            if target_list[i][k] in origin_list[j]:
                                pass
                            else:
                                diff_list.append(target_list[i][k])
                                logging.info('The diff data - {0}{1}'.format(target_list[i][0], target_list[i][k]))
                                diff_data = target_list[i][0], target_list[i][k]
                                diff_file.writelines(diff_data)
                    else:
                        pass
        elif 'config' in template_file.split(os.sep)[-1].split('.')[0]:
            for i in range(1, len(target_list)):
                for j in range(1, len(origin_list)):
                    if target_list[i][0] == origin_list[j][0]:
                        # print('find the type data, start to compare...')
                        for n in range(2, len(target_list[i])):
                            var_name = target_list[i][n].split(':')[0].strip()
                            for m in range(1, len(origin_list[j])):
                                var_name_tmp = origin_list[j][m].split('=')[0]
                                if var_name == var_name_tmp:
                                    var_value = target_list[i][n].split(':')[1].strip()
                                    var_value_tmp = origin_list[j][m].split('=')[1].strip()
                                    if var_value != var_value_tmp:
                                        diff_list.append(target_list[i][n])
                                        logging.info(
                                            'The diff data - {0}{1}'.format(target_list[i][0], target_list[i][n]))
                                        diff_data = target_list[i][0], target_list[i][n]
                                        diff_file.writelines(diff_data)
                                    else:
                                        pass
                                else:
                                    pass
                    else:
                        pass
        else:
            logging.info('The file can not be parsed, check the origin data')
            return False

        diff_list = [j for j in diff_list if j != []]
        diff_file.close()
        # if empty list, no diff data - pass
        if len(diff_list):
            return False
        else:
            return True

    # parse the smbios log file to list,
    def getData(self, file):
        f = open(file, 'r')
        data = f.readlines()
        lists = [[]]
        index = 0
        for i in data:
            if i == '\n':
                index += 1
                lists.append([])
            else:
                lists[index].append(i)
        f.close()
        lists = [j for j in lists if j != []]  # remove the []
        return lists

    # test API
    def smbiosCheck(self, command, target_path, template_path):
        """
        :param command: smbios command, e.g: dmidecode -t xx
        :param template_path: e.g: Hy5Config.SMBIOS_DIR
        :param target_path: e.g: Hy5Config.LOG_DIR
        for different platform, the ini file is a standard defined smbios table file.
                        dmidecode.log is for stress or find the diff after the smbios table is completed on BIOS side.
        :return: True - Data matched, False - find diff data
        """
        if self.check_smbios(target_path, template_path):
            logging.info('Pass:{0}'.format(command))
        else:
            logging.info('Fail:{0}'.format(command))
        # print(target_path)
        with open(os.path.join(target_path, 'test.log'), 'r') as f:
            for line in f.readlines():
                if 'Fail:' in line:
                    print('TYPE DATA Check:Failed')
                    return False

        return True


