# -*- encoding=utf8 -*-
import os
import datetime

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

#Report Setting
REPORT_TEMPLATE = "C:\\autotest\\Report\\template_Moc"

# Enviroment settigs
LOG_DIR = 'c:\\daily\\Moc25\\{0}'.format(timestamp)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')
BINARY_DIR = '\\\\172.16.0.73\\Ali_Moc\\Moc25'

# BMC Configuration
BMC_IP = '192.168.2.100'
BMC_USER = 'root'
BMC_PASSWORD = 'root'
PORT = 22

# BIOS Configuration
BIOS_USER = 'Admin'
BIOS_PASSWORD = 'Admin'

# OS Configuration
OS_IP = '192.168.100.112'
OS_USER = 'root'
OS_PASSWORD = 'alibaba1688'



