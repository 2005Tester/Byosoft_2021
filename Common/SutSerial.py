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

ENTER = [chr(0x0D)]
ES = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,5}"


class SutControl:
    def __init__(self, port, baudrate, timeout, log):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.log = log
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
        logging.info("key sent")

    # send multiple keys in a row with delay, keys = list
    def send_keys_with_delay(self, keys, delay=1):
        for key in keys:
            self.send_keys(key)
            time.sleep(delay)

    def receive_data(self, size):
        data = self.session.read(size).decode('utf-8')
        return data

    @ staticmethod
    def is_timeout(t_start, timeout):
        now = time.time()
        spent_time = (now - t_start)
        if spent_time > timeout:
            # logging.info("Check message in serial output time out.")
            return True

    def capture_data(self):
        logging.info("capture data from serial port")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
            except Exception as e:
                logging.error(e)
                break

    @staticmethod
    def find_msg(msg, data):
        if re.search(msg, data):
            logging.debug("Found: \"{0}\"".format(msg))
            return True

    def write_data2log(self, data):
        with open(self.log, 'a') as f:
            f.write(data)

    def cleanup_data(self, data):
        pat1 = "\x1B[@-_][0-?]*[ -/]*[@-~]"
        pat2 = "[-\+^]{3,}"
        pat3 = "/\s+\\\\"
        dic = {pat1: "", pat2: "", pat3: ""}
        for k, v in dic.items():
            data = re.compile(k).sub(v, data)
        with open(self.log, 'a') as f:
            f.write(data)

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
                        self.send_data("Admin@9000")
                        self.send_data(chr(0x0D))  # Send Enter
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
        while True:
            if self.session.in_waiting:
                try:
                    data = self.session.read(512).decode("utf-8")
                    if cleanup:
                        data = self.cleanup_data(data)
                    else:
                        self.write_data2log(data)
                except Exception as e:
                    logging.debug(e)
                    logging.debug("is_msg_present_general: error in reading serial data")
                    data = ''              
                if pw_prompt and self.find_msg(pw_prompt, data):
                    self.send_data(pw)
                    self.send_data(chr(0x0D))  # Send Enter
                    self.send_data(chr(0x0D))  # Send Enter
                    logging.info("Send password...")               
                if self.find_msg(msg, data):
                    return True

            if self.is_timeout(start_time, delay):
                if delay > 5:
                    logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
                break

    def is_msg_present(self, msg):
        logging.info("Waiting for:\"{0}\"".format(msg))
        start_time = time.time()
        logging.debug("is_msg_present: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if self.find_msg("Press F2", data):
                        self.send_data("Admin@9000")
                        self.send_data(chr(0x0D))  # Send Enter
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")
                    if self.find_msg(msg, data):
                        return True
                    # else:
                    #    keys = [chr(0x1b), chr(0x5b), chr(0x42), chr(0x1b), chr(0x5b), chr(0x41)]
                    #    self.send_keys(keys)
            except Exception as e:
                logging.error("is_msg_present:{0}".format(e))
                break
            if self.is_timeout(start_time, 300):
                logging.debug("is_msg_present: timeout")
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
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if self.find_msg("Press F2", data):
                        self.send_data("Admin@9000")
                        self.send_data(chr(0x0D))  # Send Enter
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

    # workaround: fix the captured string printed twice, (updated by arthur)
    def waitString(self, msg, timeout=10, regex=False):
        """
        Read data from Console Redirection port, and wait specified string
        :param msg: String to be captured
        :param timeout: Timeout of wait duration
        :return: True, if get specified string from COM port
                 False, script has not capture specified string after timeout
        """
        t_start = time.time()
        self.buffer = ""
        logging.info("Waiting for string:\"{0}\"".format(msg))
        logging.debug("wait_for_msg: receiving data from serial port...")
        while True:
            try:
                count = self.session.inWaiting()  # Serial port buffer data
                if count != 0:
                    rev = self.session.read(count).decode('utf-8')
                    self.buffer += rev
                    rev = self.cleanup_data(self.buffer)
                    if not regex:
                        if msg in rev:
                            logging.info("Find string:{0}".format(msg))
                            return True
                    else:
                        if re.search(msg, rev, re.M):
                            logging.debug("Find string:{0}".format(msg))
                            return True
                time.sleep(0.1)
            except Exception as e:
                logging.error("Error:{0}".format(e))
            now = time.time()
            spent_time = (now - t_start)
            if spent_time > timeout:
                logging.info("Can not find string(timeout):{0}".format(msg))
                return False

    # For e.g: post test, find more than 1 string, waitStrings
    def waitStrings(self, msg_list=None, timeout=10):
        """
        Read data from Console Redirection port, and wait more than 1 string
        :param msg_list: Multiple strings wait to be captured
        :param timeout: Timeout of wait duration
        :return: True, if all strings get from COM port
                 False, script has not captured all strings after timeout
        """
        if msg_list is None:
            msg_list = []
        t_start = time.time()
        tmp = []
        var = ''
        self.buffer = ""
        while True:
            try:
                count = self.session.inWaiting()  # Serial port buffer data
                if count != 0:
                    rev = self.session.read(count).decode()
                    self.buffer += rev
                    rev = self.cleanup_data(self.buffer)
                    for i in range(len(msg_list)):
                        if msg_list[i] not in rev:
                            var = msg_list[i]
                        else:
                            tmp.append(msg_list[i])

                time.sleep(0.1)
            except Exception as e:
                logging.error("Error:{0}".format(e))

            if tmp == msg_list:
                logging.info('Find strings:{0}'.format(tmp))
                return True

            now = time.time()
            spent_time = (now - t_start)
            if spent_time > timeout:
                logging.info("Can not find strings(timeout):{0}".format(var))
                return False

    # boot with hotkey pressed, and check whether boot is successful
    def boot_with_hotkey(self, key, msg, timeout, hotkey_prompt="Press Del go to Setup Utility", pw_prompt="Press F2", password="Admin@9000"):
        start_time = time.time()
        logging.debug("boot_with_hotkey: Receiving data from SUT...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if self.find_msg(hotkey_prompt, data):
                        self.send_keys(key)
                        logging.info("Hot Key sent")
                    if self.find_msg(pw_prompt, data):
                        self.send_data(password)
                        self.send_data(chr(0x0D))  # Send Enter
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
    # Patten1: Only setup option is highlighted, name should be specified, value not required
    # Patten2: Only value is highlighted, both name and value need to be specified
    # Patten3: Both setup optin and value is highlighted, same process as patten1, but use [name + space + value]
    def locate_setup_option(self, key, setupoption, try_counts, delay=1):

        if len(setupoption) == 1:
            patten = setupoption[0] + ES

        elif len(setupoption) == 2:
            patten = ES + "{0}".format(setupoption[1]) + ES + "\s+" + ES + "\s+" + ES + "{0}".format(setupoption[0])

        else:
            logging.info("Incorrect format of parameter: setupoption")
            return
        logging.info("Locating option: {0}".format(setupoption))
        self.receive_data(512)
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
        self.receive_data(512)
        while try_counts:
            try_counts -= 1
            time.sleep(2)
            if self.is_msg_present_general(patten, 1, cleanup=False):
                logging.info("Menu found: {0}".format(menuname))
                try_counts = 0
                return True
            self.send_keys(key)

    # Enter specifc setup menu by given path(list)
    def enter_menu(self, key, option_path, try_counts, confirm_msg, timeout=15):
        for option in option_path:
            logging.info("Locating menu: {0}".format(option))
            if not self.locate_menu(key, option, try_counts):
                logging.info("Not Found: {0}".format(option))
                return
            self.send_keys(ENTER)
        if not self.is_msg_present_general(confirm_msg, timeout):
            logging.info("{0} not captured, may not enter corect menu")
            return
        logging.info("Enter menu: {0} successfully".format(option_path[-1]))
        return True

    # Will be replaced by locate_setup_option()
    def find_setup_option(self, key, setupoption, try_counts):
        highlight = "\x1B\["
        self.receive_data(512)
        while try_counts:
            try_counts -= 1
            time.sleep(2)
            if self.is_msg_present_general(setupoption + highlight, 1, cleanup=False):
                logging.info("{0} found".format(setupoption))
                self.send_keys(ENTER)
                try_counts = 0
                return True
            self.send_keys(key)

    # issue: can not to the first item(WA: ENTER + UP, then can find the first option or item), to be enhanced, TBD
    # could be used to navigate to a option in boot manager page or a option in Setup,
    def to_highlight_option(self, key, msg, pat=None, timeout=15):
        """
        :param msg: the option to be highlighted,
                    (ps: if the option name is 'Intel(R) TXT', just input TXT' -- known issue, to be enhanced, TBD)
        :param pat: the re rule, need to be modified for different platform, eg. pat value from Hy5Config.py,
        :timeout: set the value based on the counts of option in the current page,
        :return: Data read from serial port,
        """
        if pat is None:
            pat1 = re.compile('{0}\x1B\W'.format(msg), re.M)
        else:
            pat1 = re.compile('{0}{1}\s*\x1B\W'.format(pat, msg), re.M)

        # flush serial buffer
        self.session.flush()
        time.sleep(1)

        s_time = time.time()  # set timeout flag
        while True:
            serial_data = ''
            if time.time() - s_time > timeout:
                print("to highlight option timeout")
                return False

            self.send_keys(key)

            # read serial log in 2 sec
            for i in range(0, 2):
                data = self.readLines()
                if data:
                    serial_data += data
                time.sleep(1)

            pat1_res = pat1.findall(serial_data)
            if not pat1_res:
                continue
            else:
                logging.debug('find the highlight option:{0}'.format(pat1_res))
                logging.info('Find the highlight option, wait for the next step,')
                # self.send_keys(ENTER)
                break

        return True

    # debug, to support to_highlight_option def,
    def readLines(self, limit=None):
        """
        :param limit: most limit bytes to be read,
        :return: Data read from serial port,
        """
        if limit is None:
            read = self.session.readline()
        else:
            read = self.session.readline(limit)
        return read.decode()

    # used to verified the option values,
    def verify_option_value(self, key, msg, timeout=5):
        """
        :param timeout: no need to set the timeout anymore, the data will be read in 5s,
        """
        # pat1
        pat1 = re.compile(msg)

        # flush serial buffer in 5 sec
        for i in range(0, 5):
            self.readLines()
            time.sleep(1)

        s_time = time.time()  # set timeout flag
        while True:
            serial_data = ''
            if time.time() - s_time > timeout:
                print("Find the option value timeout, failed to check the value")
                return False

            self.send_keys(key)

            # read serial log in 2 sec
            for i in range(0, 2):
                data = self.readLines()
                data = self.cleanup_data(data)
                if data:
                    serial_data += data
                time.sleep(1)

            pat1_res = pat1.findall(serial_data)
            if not pat1_res:
                continue
            else:
                logging.info('The option values are correct:{0}'.format(pat1_res))
                break

        return True

    # run command from serial port until spefified message occur
    def run_command(self, cmd, msg):
        logging.info("Sending command: {0}".format(cmd.strip("\n")))
        self.send_data(cmd)  
        logging.info("Receiving data...")
        data = self.session.read_until(expected=msg).decode('utf-8')
        data = self.cleanup_data(data)
        return data
