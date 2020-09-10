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

    def receive_data(self, size):
        self.session.read(size)

    def is_timeout(self, t_start, timeout):
        now = time.time()
        spent_time = (now - t_start)
        if spent_time > timeout:
            logging.info("Time out, probably boot fail.")
            return True

    def capture_data(self):
        logging.info("capture data from serial port")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    with open(self.log, 'a') as f:
                        f.write(data)
            except Exception as e:
                logging.error(e)
                break

    def is_boot_success(self):
        start_time = time.time()
        logging.info("check_boot_success: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if re.search("BIOS boot completed.", data):
                        logging.info("check_boot_success: pass")
                        return True
            except Exception as e:
                logging.error("check_boot_success:{0}".format(e))
                break
            now = time.time()
            spent_time = (now - start_time)
            if spent_time > 600:
                logging.info("check_boot_success: timeout")
                break
    
    def is_msg_present(self, msg):
        start_time = time.time()
        logging.info("is_msg_present: receiving data from serial port...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    # data.replace(r'[\x00-\x1F]\[\d\d;\d\dH', '')
                    # print(data)
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if re.search(msg, data):
                        logging.debug("is_msg_present: found:{0}".format(msg))
                        return True
            except Exception as e:
                logging.error("is_msg_present:{0}".format(e))
                break
            now = time.time()
            spent_time = (now - start_time)
            if spent_time > 90:
                keys = [chr(0x1b), chr(0x5b), chr(0x42), chr(0x1b), chr(0x5b), chr(0x41)]
                for char in keys:
                    serial.send_data(char)
            if spent_time > 300:
                logging.error("is_msg_present: timeout")
                break
    
    # boot with hotkey pressed, and check whether boot is successful
    def boot_with_hotkey(self, key, msg, timeout):
        start_time = time.time()
        logging.info("Receiving data from SUT...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    with open(self.log, 'a') as f:
                        f.write(data)
                    if re.search("Press Del go to Setup Utility", data):
                        for char in key:
                            self.send_data(char)
                        logging.info("Hot Key sent")
                    if re.search("Press F2", data):
                        self.send_data("Admin@9000")
                        self.send_data(chr(0x0D))  # Send Enter
                        self.send_data(chr(0x0D))  # Send Enter
                        logging.info("Send password...")
                    if re.search(msg, data):
                        logging.info("BIOS Boot Successful.")
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