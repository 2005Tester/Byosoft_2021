# -*- encoding=utf8 -*-
import re
import os
import logging


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


    def check_bios_log(self):
        ast = 0
        exception = 0
        error = 0
        bios_log = os.path.join(self.log_dir, "serial.log")
        data = self.load_log(bios_log)
        for line in data:
            if re.search("assert", line):
                logging.info("Assert found in line {0}".format(data.index(line)+1))
                logging.info(line)
                ast +=1
            if re.search("Exception", line):
                logging.info("Exception found in line {0}".format(data.index(line)+1))
                logging.info(line)
                exception +=1
        if ast == 0:
            logging.info("No assert found in serial log.")
        if exception == 0:
            logging.info("No exception found in serial log.")
    
        if (ast + exception + error) == 0:    
            return True


    def check_errors(self):
        pass

    def check_smbios(self):
        passed_test = 0
        smbios_log = os.path.join(self.log_dir, "dmidecode.log")
        data = self.load_log(smbios_log)
        for line in data:
            if re.search("UUID: E1C5D866-0018-83C3-B211-D21D464C6424", line):
                logging.info("UUID checked: {0}".format(line))
                passed_test +=1

            if re.search("Product Name: 2488H V6", line):
                logging.info("Product Name checked: {0}".format(line))
                passed_test +=1
            
        if passed_test == 2:
            return True






if __name__ == "__main__":
    loganalyze = LogAnalyzer(r"C:\daily\autolog\2020-09-21_17-55-47-overnight")
    loganalyze.check_bios_log()
