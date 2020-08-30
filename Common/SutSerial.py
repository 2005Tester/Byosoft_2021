import serial
import time
import re
from Common import SutSsh

#logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s')

class SutControl(): 
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.session = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if (self.session.is_open):
                Ret = True
        except Exception as e:
            print(e)

    def open_sesion(self):
        self.session.open()

    def close_session(self):
        self.session.close()

    def send_data(self, data):
        self.session.write(data.encode())

    def receive_data(self, size):
        self.session.read(size)

    def is_timeout(self, t_start, timeout):
        now = time.time()
        spent_time =(now - t_start)
        if spent_time > timeout:
            print("Time out, probably boot fail.")
            return True

    def check_boot_success(self):
        start_time = time.time()
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    with open('serial.log', 'a') as f:
                        f.write(data)
                    if re.search("BIOS boot completed.", data):
                        print("check_boot_success: BIOS Boot Successful.")
                        self.close_session()
                        return
            except Exception as e:
                print(e)
            now = time.time()
            spent_time =(now - start_time)
            if spent_time > 600:
                print("check_boot_success: Time out, probably boot fail.")
                self.close_session()
                break

    def send_key(sef, key):
        for char in key:
            self.send_data(char)

    def send_hotkey(self, key, msg, timeout):
        start_time = time.time()
        print("Receiving data from SUT...")
        while True:
            try:
                if self.session.in_waiting:
                    data = self.session.read(256).decode("utf-8")
                    with open('serial.log', 'a') as f:
                        f.write(data)
                    if re.search("Press Del go to Setup Utility", data):
                        for char in key:
                            self.send_data(char)
                        print("Hot Key sent")
                    if re.search("Press F2", data):
                        self.send_data("Admin@9000")
                        self.send_data(chr(0x0D))  # Send Enter
                        self.send_data(chr(0x0D))  # Send Enter
                        print("Send password...")
                    if re.search(msg, data):
                        print("BIOS Boot Successful.")
                        return True
            except Exception as e:
                print(e)
                print("Please check whether COM port is in use.")
                break

            if self.is_timeout(start_time, timeout):
                break



    def hotkey_del(self):
        key_del = [chr(0x7F)]
        msg = "none"
        self.send_hotkey(key_del, msg, 300)

    def hotkey_F6(self):
        key_f6 = [chr(0x1b),chr(0x5b),chr(0x31),chr(0x37),chr(0x7e)]
        msg = "BIOS boot completed."
        self.send_hotkey(key_f6, msg, 300)

    def hotkey_F11(self):
        key_f11 = [chr(0x1b),chr(0x5b),chr(0x32),chr(0x33),chr(0x7e)]
        msg = "Boot Manager Menu"
        self.send_hotkey(key_f11, msg, 300)    

    def hotkey_F12(self):
        key_f12 = [chr(0x1b),chr(0x5b),chr(0x32),chr(0x34),chr(0x7e)]
        msg = "none"
        self.send_hotkey(key_f12, msg, 300)