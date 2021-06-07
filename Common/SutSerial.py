#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import serial
import time
import re
import sys
import logging
from Core import var

ENTER = [chr(0x0D)]
UP = [chr(0x1b), chr(0x5b), chr(0x41)]
DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]

ES = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}"

SEP = "(?:\x1b\[\d+;\d+H){1}"  # value separator
HLP = "(?:\x1b\[\d+m){3}"  # value hightlight ending flag, last appeared valid
VALR = "(\w[\w -/]*\w)"  # bios value name ruler


class SutControl:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.data = ''
        try:
            self.session = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.session.is_open:
                logging.info("Serial port opened.")               
        except Exception as e:
            logging.error(e)
            logging.info("SutControl: init failed.")
            sys.exit()

    def open_session(self):
        self.session.open()

    def close_session(self):
        self.session.close()

    def send_data(self, data):
        self.session.write(data.encode())

    def send_keys(self, keys):
        for char in keys:
            self.send_data(char)

    # send multiple keys in a row with delay, keys = list
    def send_keys_with_delay(self, keys, delay=1):
        for key in keys:
            self.send_keys(key)
            time.sleep(delay)

    def receive_data(self, size):
        self.data = self.session.read(size).decode('utf-8', errors='ignore')
        return self.data

    @ staticmethod
    def is_timeout(t_start, timeout):
        now = time.time()
        spent_time = (now - t_start)
        if spent_time > timeout:
            # logging.info("Check message in serial output time out.")
            return True

    def write_data2log(self, data):
        with open(var.get('serial_log'), 'a', encoding='utf-8', errors='ignore') as f:
            f.write(data)

    def capture_data(self):
        logging.info("capture data from serial port")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    self.write_data2log(data)

            except Exception as e:
                logging.error(e)
                break

    @staticmethod
    def find_msg(msg, data):
        if re.search(msg, data):
            logging.debug("Found: \"{0}\"".format(msg))
            return True

    def cleanup_data(self, data, save=True):
        pat1 = "\x1B[@-_][0-?]*[ -/]*[@-~]"
        pat2 = "[-\+^]{3,}"
        pat3 = "/\s+\\\\"
        dic = {pat1: "", pat2: "", pat3: ""}
        for k, v in dic.items():
            data = re.compile(k).sub(v, data)
        if save:
            self.write_data2log(data)
        return data

    def is_boot_success(self):
        start_time = time.time()
        logging.debug("check_boot_success: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    if self.find_msg("Press F2", data):
                        self.send_data("Admin@9009")
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")
                    if self.find_msg("BIOS boot completed.", data):
                        return True
            except Exception as e:
                logging.error("check_boot_success:{0}".format(e))
                break
            if self.is_timeout(start_time, 600):
                logging.debug("is_boot_success: timeout")
                break

    def is_msg_present_general(self, msg, delay=150, pw_prompt=None, pw=None, cleanup=True):
        logging.debug("Waiting for:\"{0}\"".format(msg))
        start_time = time.time()
        logging.debug("is_msg_present_general: receiving data from serial port...")
        if self.find_msg(msg, self.data):
            return True
        else:
            while True:
                if self.session.in_waiting:
                    try:
                        self.data = self.session.read(1024).decode("utf-8", errors='ignore')
                        if cleanup:
                            self.data = self.cleanup_data(self.data)
                        else:
                            self.write_data2log(self.data)
                    except Exception as e:
                        logging.error(e)
                        logging.error("is_msg_present_general: error in reading serial data")         
                    if pw_prompt and self.find_msg(pw_prompt, self.data):
                        self.send_data(pw)
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")         
                    if self.find_msg(msg, self.data):
                        logging.debug("Message found.")
                        return True

                if self.is_timeout(start_time, delay):
                    if delay > 5:
                        logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
                    break

    # verify specified message (msg1) should not appeare in serial log, but msg2 should be present
    def is_msg_not_present(self, msg1, msg2):
        logging.info("Waiting for:\"{0}\" not \"{1}\"".format(msg2, msg1))
        start_time = time.time()
        logging.debug("is_msg_not_present: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    if self.find_msg("Press F2", data):
                        self.send_data("Admin@9009")
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")
                    if self.find_msg(msg1, data):
                        logging.info("String \"{0}\" should not occur in BIOS log.".format(msg1))
                        return
                    if self.find_msg(msg2, data):
                        return True
            except Exception as e:
                logging.error("is_msg_not_present:{0}".format(e))
                break
            if self.is_timeout(start_time, 300):
                logging.debug("is_msg_not_present: timeout")
                break

    # Find 1 string, waitString
    def waitString(self, msg, timeout=10, regex=False):
        """
        Read data from Console Redirection port, and wait specified string
        :param msg: String to be captured
        :param timeout: Timeout of wait duration
        :return: True, if get specified string from COM port
                 False, script has not capture specified string after timeout
        """
        t_start = time.time()
        f = open(var.get('serial_log'), 'a')
        # buffer_list = []
        logging.info("Waiting for string:\"{0}\"".format(msg))
        while True:
            try:
                buffer = b''
                count = self.session.inWaiting()
                if count > 0:
                    data = self.session.read(count)
                    if data == '':
                        break
                    # else:
                    #     buffer_list.append(data)
                    #     print(buffer_list)
                    if data != buffer:
                        f.write(data.decode())
                        if not regex:
                            if msg in data.decode():
                                logging.info("Find string:{0}".format(msg))
                                break
                        else:
                            if re.search(msg, data.decode(), re.M):
                                logging.debug("Find string:{0}".format(msg))
                                break

                time.sleep(0.01)
            except EOFError:
                pass

            now = time.time()
            spent_time = (now - t_start)
            if spent_time > timeout:
                logging.info("Can not find string(timeout):{0}".format(msg))
                return False
        f.close()
        return True

    # For e.g: post test, find more than 1 string, waitStrings
    def waitStrings(self, msg_list=None, timeout=5):
        """
        Read data from Console Redirection port, and wait more than 1 string
        :param msg_list: Multiple strings wait to be captured
        :param timeout: Timeout of wait duration
        :return: True, if all strings get from COM port
                 False, script has not captured all strings after timeout
        """
        if msg_list is None:
            msg_list = []

        tmp = []
        t_start = time.time()
        f = open(var.get('serial_log'), 'a')
        logging.info("Waiting for strings:\"{0}\"".format(msg_list))
        while True:
            try:
                buffer = b''
                count = self.session.inWaiting()
                if count > 0:
                    data = self.session.read(count)
                    if data == '':
                        break

                    if data != buffer:
                        f.write(data.decode())
                        for i in msg_list:
                            if i in data.decode():
                                tmp.append(i)

                time.sleep(0.01)
            except EOFError:
                pass
            if set(tmp) == set(msg_list):
                logging.info('Find strings:{0}'.format(list(set(tmp))))
                break

            now = time.time()
            spent_time = (now - t_start)
            if spent_time > timeout:
                logging.info("Can not find strings(timeout):{0}".format(list(set(msg_list) - set(tmp))))
                return False
        f.close()
        return True

    # boot with hotkey pressed, and check whether boot is successful
    def boot_with_hotkey(self, key, msg, timeout, hotkey_prompt="Press Del go to Setup Utility", pw_prompt="Press F2", password="Admin@9009"):
        start_time = time.time()
        logging.debug("boot_with_hotkey: Receiving data from SUT...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8", errors='ignore')
                    data = self.cleanup_data(data)
                    if self.find_msg(hotkey_prompt, data):
                        self.send_keys(key)
                        logging.info("Hot Key sent")
                    if self.find_msg(pw_prompt, data):
                        self.send_data(password)
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")
                    if self.find_msg(msg, data):
                        return True
            except Exception as e:
                logging.error(e)
                logging.debug("boot_with_hotkey: Please check whether COM port is in use.")
                break

            if self.is_timeout(start_time, timeout):
                break

    # Navigate in a setup page and verify whether multiple setup options are correct
    def navigate_and_verify(self, key, setup_options, try_counts):
        # for i in range(0, try_counts):
        while setup_options and try_counts:
            self.send_keys(key)
            try_counts -= 1
            time.sleep(2)
            for option in setup_options:
                if self.is_msg_present_general(option, 3):
                    setup_options.pop(setup_options.index(option))
        if len(setup_options) == 0:
            logging.info("All the setup options are verified")
            return True
        else:
            for option in setup_options:
                logging.info("{0} not verified".format(option))

    # Find a setup option and stop there, will not send "Enter" after option found
    # setupoption = ['name','value'] e.g. ['KTI Prefetch', 'Auto']
    # Patten1: Only option name is highlighted, name should be specified, value not required
    # Patten2: Only value is highlighted, both name and value need to be specified
    # Patten3: Both setup optin and value is highlighted, same process as patten1, but use [name + space + value]
    def locate_setup_option(self, key, setupoption, try_counts, delay=1):

        if len(setupoption) == 1:
            patten = setupoption[0] + ES

        elif len(setupoption) == 2:
            patten = ES + "{0}".format(setupoption[1]) + ES + "\s+" + ES + "\s+" + ES + "{0}".format(setupoption[0])

        else:
            logging.info("Incorrect format of parameter: setupoption, should be list")
            return
        logging.info("Locate option: {0}".format(setupoption))
        # self.receive_data(512)
        while try_counts:
            try_counts -= 1
            time.sleep(2)
            if self.is_msg_present_general(patten, delay, cleanup=False):
                logging.info("Option found: {0}".format(setupoption))
                try_counts = 0
                return True
            self.send_keys(key)
        logging.info("Option not found: {0}".format(setupoption))

    def locate_menu(self, key, menuname, try_counts):
        patten = menuname + ES
        # self.receive_data(512)
        while try_counts:
            time.sleep(2)
            if self.is_msg_present_general(patten, 1, cleanup=False):
                logging.info("Menu found: {0}".format(menuname))
                try_counts = 0
                return True
            self.send_keys(key)
            try_counts -= 1

    # Enter specifc setup menu by given path(list)
    def enter_menu(self, key, option_path, try_counts, confirm_msg, timeout=15):
        logging.info("Go to setup menu:{0}".format(option_path))
        for option in option_path:
            logging.info("Locate menu: {0}".format(option))
            if not self.locate_menu(key, option, try_counts):
                logging.info("Not Found: {0}".format(option))
                return
            self.send_keys(ENTER)
            time.sleep(2)
        if not self.is_msg_present_general(confirm_msg, timeout):
            logging.info("{0} not captured, may not enter corect menu")
            return
        logging.info("Enter menu: {0} successfully".format(option_path[-1]))
        return True

    # run command from serial port until spefified message occur
    def run_command(self, cmd, msg):
        logging.info("Sending command: {0}".format(cmd.strip("\n")))
        self.send_data(cmd)  
        logging.info("Receiving data...")
        data = self.session.read_until(expected=msg).decode('utf-8')
        data = self.cleanup_data(data)
        return data

    # navigate and get setup option value by name
    def get_option_value(self, option_patten, value_patten, key, try_counts):
        if not self.locate_setup_option(key, option_patten, try_counts):
            logging.info("Setup option not found.")
            return
        pat_value = re.compile(value_patten)
        res = pat_value.findall(self.data)
        if len(res) != 1:
            logging.info("Error: Multiple match found {0}".format(res))
            return
        else:
            logging.info("Value of option: {0} is {1}".format(option_patten[0], res[0]))
            return res[0]

    # cut a section of serial log
    def cut_log(self, start_str, end_str, duration=20, timeout=200):
        logging.info(f"Cut serial log from: '{start_str}' to '{end_str}'")
        data_cut = ""
        boot_log = ""
        cut_begain = 0
        patten_start = re.compile(start_str)
        patten_end = re.compile(end_str)
        start_time = time.time()
        while True:
            if self.session.in_waiting:
                tmp_line = self.session.readline().decode("utf-8", errors='ignore')  # readline to avoid keywords split
                cln_data = self.cleanup_data(tmp_line, save=False)
                boot_log += cln_data
                if patten_start.search(cln_data):  # start_str found
                    cut_begain = time.time()
                    logging.info(f"Start string found: {start_str}")
                if cut_begain:
                    if time.time() - cut_begain < duration:  # cache serial output
                        data_cut += cln_data
                    if patten_end.search(cln_data):  # cache last tmp_line
                        logging.info(f"End string found: {end_str}")
                        if not patten_end.search(data_cut):  # in case of first tmp_line contains start and end str
                            data_cut += cln_data
                        self.write_data2log(boot_log)
                        return data_cut
                    if time.time() - cut_begain > duration:  # duration timeout
                        logging.info(f"Start_str found but missing end_str: duration timeout {duration}s")
                        self.write_data2log(boot_log)
                        return data_cut
            if time.time() - start_time > timeout:  # nothing found, timeout limit
                logging.info(f"Nothing found, timeout exit for {timeout}s")
                self.write_data2log(boot_log)
                return data_cut

    # get one option all value list, need locate to the target option first
    def get_value_list(self):
        all_patten = re.compile(f"{SEP}{VALR}")
        self.session.flushInput()
        self.send_keys_with_delay(ENTER)
        tmpdata = self.receive_data(self.session.in_waiting)
        self.send_keys_with_delay(ENTER)
        val_list = all_patten.findall(tmpdata)
        if not val_list:
            logging.error("Fail to match values list")
            return
        logging.info("Current option values: {}".format(val_list))
        return val_list

    # locate to the target value, need locate to the target option first
    # value_str: the target value to highlight
    def locate_value(self, value_str):
        hl_patten = re.compile(f"{SEP}{VALR}{HLP}")  # hight patten
        val_list = self.get_value_list()
        if not val_list:
            return
        if value_str not in val_list:
            logging.error('"{}" not in value list'.format(value_str))
            return
        self.session.flushInput()
        self.send_keys_with_delay(ENTER)
        tmpdata = self.receive_data(self.session.in_waiting)
        hl_default = hl_patten.findall(tmpdata)
        if hl_default[-1] == value_str:
            logging.info('Current select option is "{}"'.format(value_str))
            return True
        offset = val_list.index(value_str)-val_list.index(hl_default[-1])
        press_key = DOWN if offset > 0 else UP
        key_cnt = abs(offset)
        for k in range(key_cnt):
            self.send_keys(press_key)
            time.sleep(1)
            tmpdata = self.receive_data(self.session.in_waiting)
        hl_current = hl_patten.findall(tmpdata)
        if not hl_current:
            logging.error("Fail to verify current select value after key pressed")
            return
        if hl_current[-1] == value_str:
            logging.info('Locate to value "{}" pass'.format(value_str))
            return True
        logging.error('Locate to value "{}" failed'.format(value_str))
