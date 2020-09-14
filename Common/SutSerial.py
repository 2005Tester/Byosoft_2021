# -*- encoding=utf8 -*-
import serial
import time
import re
import logging


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

    def open_session(self):
        self.session.open()

    def close_session(self):
        self.session.close()

    def send_data(self, data):
        self.session.write(data.encode())

    def send_keys(self, keys):
        for char in keys:
            self.send_data(char)

    def receive_data(self, size):
        self.session.read(size)

    @ staticmethod
    def is_timeout(t_start, timeout):
        now = time.time()
        spent_time = (now - t_start)
        if spent_time > timeout:
            logging.info("Check message in serial output time out.")
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
            logging.info("Found message: \"{0}\"".format(msg))
            return True

    @staticmethod
    def cleanup_data(data):
        pat1 = '[\x00-\x1F]\[\d+;\d+[mH]*'
        pat2 = '[\x00-\x1F]\[\d+[mJ]'
        data = re.sub(pat1, '', data)
        data = re.sub(pat2, '', data)
        # print(data)
        return data

    def is_boot_success(self):
        start_time = time.time()
        logging.debug("check_boot_success: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if self.find_msg("BIOS boot completed.", data):
                        return True
            except Exception as e:
                logging.error("check_boot_success:{0}".format(e))
                break
            if self.is_timeout(start_time, 600):
                logging.debug("is_boot_success: timeout")
                break
    
    def is_msg_present(self, msg):
        start_time = time.time()
        logging.debug("is_msg_present: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if self.find_msg(msg, data):
                        return True
                    #else:
                    #    keys = [chr(0x1b), chr(0x5b), chr(0x42), chr(0x1b), chr(0x5b), chr(0x41)]
                    #    self.send_keys(keys)
            except Exception as e:
                logging.error("is_msg_present:{0}".format(e))
                break
            if self.is_timeout(start_time, 300):
                logging.debug("is_msg_present: timeout")
                break
    
    # boot with hotkey pressed, and check whether boot is successful
    def boot_with_hotkey(self, key, msg, timeout):
        start_time = time.time()
        logging.info("Receiving data from SUT...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    data = self.cleanup_data(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if self.find_msg("Press Del go to Setup Utility", data):
                        self.send_keys(key)
                        logging.info("Hot Key sent")
                    if self.find_msg("Press F2", data):
                        self.send_data("Admin@9000")
                        self.send_data(chr(0x0D))  # Send Enter
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")
                    if self.find_msg(msg, data):
                        return True
            except Exception as e:
                logging.error(e)
                logging.info("Please check whether COM port is in use.")
                break

            if self.is_timeout(start_time, timeout):
                break
        return True

    def hotkey_del(self):
        key_del = [chr(0x7F)]
        msg = "Boot From File"
        return self.boot_with_hotkey(key_del, msg, 300)

    def hotkey_f6(self):
        key_f6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
        msg = "BIOS boot completed."
        return self.boot_with_hotkey(key_f6, msg, 300)

    def hotkey_f11(self):
        key_f11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
        msg = "Boot Manager Menu"
        return self.boot_with_hotkey(key_f11, msg, 300)

    def hotkey_f12(self):
        key_f12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]
        msg = "none"
        return self.boot_with_hotkey(key_f12, msg, 300)
