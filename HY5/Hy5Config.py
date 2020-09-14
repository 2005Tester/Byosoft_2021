# -*- encoding=utf8 -*-
import os
import datetime

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


# Enviroment settigs
LOG_DIR = 'c:\\daily\\autolog\\{0}'.format(timestamp)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')
BINARY_DIR = '\\\\172.16.0.73\\HY5_Binary'

# BMC Configuration
BMC_IP = '192.168.2.100'
BMC_USER = 'Administrator'
BMC_PASSWORD = 'Admin@9000'
PORT = 22

# BIOS Configuration
BIOS_USER = 'Admin@9000'
BIOS_PASSWORD = 'Admin@9000'

# OS Configuration
OS_IP = '192.168.100.64'
OS_USER = 'root'
OS_PASSWORD = 'byo@123'


# Key mapping
ENTER = [chr(0x0D)]
DEL = [chr(0x7F)]
F2 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x32), chr(0x7e)]
F5 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x35), chr(0x7e)]
F6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
F9 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x30), chr(0x7e)]
F10 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x31), chr(0x7e)]
F11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
F12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]
UP = [chr(0x1b), chr(0x5b), chr(0x41)]
DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
Y = [chr(0x59)]
