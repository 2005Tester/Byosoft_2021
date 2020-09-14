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



