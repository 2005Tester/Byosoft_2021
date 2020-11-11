#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import os
import datetime


# Report Setting
REPORT_TEMPLATE = "C:\\autotest\\Report\\template_HY5"

# Environment settings
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_DIR = 'c:\\daily\\HY5\\{0}'.format(timestamp)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')
BINARY_DIR = '\\\\172.16.0.73\\HY5_Binary'

# Serial Port Configuration
BIOS_SERIAL = "com3"

# BMC Configuration
BMC_IP = '192.168.2.100'
BMC_USER = 'Administrator'
BMC_PASSWORD = 'Admin@9000'
PORT = 22

# BIOS Configuration
BIOS_USER = 'Admin@9000'
BIOS_PASSWORD = 'Admin@9000'

# OS Configuration
OS_IP = '192.168.100.132'
OS_USER = 'root'
OS_PASSWORD = 'byo@123'


# Key mapping
class Key:
    ENTER = [chr(0x0D)]
    DEL = [chr(0x7F)]
    F6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
    F9 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x30), chr(0x7e)]
    F10 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x31), chr(0x7e)]
    F11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
    ESC = '\33' + ' '
    F12 = '\33' + '[24~'
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]



