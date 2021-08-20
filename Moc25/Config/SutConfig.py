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


class Env:
    PROJECT_NAME = "Moc25"
    SUT_CONFIG = "Moc25-SUT1"

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    LOG_DIR = 'c:\\daily\\Moc25\\{0}'.format(timestamp)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    SERIAL_LOG = os.path.join(LOG_DIR, 'serial.log')

    BIOS_SERIAL = 'com9'

    # BMC Configuration
    BMC_SERIAL = 'com10'
    BMC_IP = '192.168.0.100'
    BMC_USER = 'root'
    BMC_PASSWORD = 'root'

    # OS Configuration
    OS_IP = '192.168.0.99'
    OS_USER = 'root'
    OS_PASSWORD = 'alibaba1688'

    # Report Setting
    REPORT_TEMPLATE = "Report\\template_Moc"


# BIOS Information
BIOS_VERSION = '2.0.ID.AL.E.006.03'
BMC_VERSION = '5.34'
CODE_VERSION = '7f4f4c18'
UUID = r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
VER_MICROCODE = 'FD000180'





# Environment settings


BINARY_DIR = '\\\\172.16.0.73\\Ali_Moc\\Moc25_ES1'




# BIOS Configuration
BIOS_USER = 'Admin'
BIOS_PASSWORD = 'Admin'

# Email report settings
MAIL_SERVER = 'mail.byosoft.com.cn'
MAIL_FROM = 'ci@byosoft.com.cn'
MAIL_PW = 'byosoft@ci123'
MAIL_TO = 'ci@byosoft.com.cn'
MAIL_CC = 'ci@byosoft.com.cn'
MAIL_TEMPLATE = 'Report\\email_template_Moc'


# Key mapping
class Key:
    ENTER = [chr(0x0D)]
    DEL = [chr(0x7F)]
    ESC = [chr(0x1B)]
    F2 = [chr(0x1b), chr(0x4f), chr(0x51)]
    F9 = [chr(0x1b), chr(0x4f), chr(0x58)]
    F10 = [chr(0x1b), chr(0x4f), chr(0x59)]
    F11 = [chr(0x1b), chr(0x4f), chr(0x5a)]
    F12 = [chr(0x1b), chr(0x4f), chr(0x5b)]
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]


# Messages to verify
class Msg:
    BOOT_MSG = 'SYSTEM SKU INFO'
    OS_MSG = 'localhost login:'

    HDD_BOOT_OPTION = "UEFI\s+AF2MA31DTDLT240A\s+0020281W6E3T"

    # Memory Info
    MEM_INFO_POST = "Total Memory Size: 8 GiB, Count: 1 Pics, Current Speed: 2933 MHz"
    MEM_TOPO_INFO = "Socket0.ChA.Dimm0:\s+2666MT/s\s+Hynix\s+SRx8\s+8GB\s+SODIMM"
    #MEM_TOPO_INFO = [r"Socket0.ChA.Dimm0:\s+2400MT/s\s+Kingston\s+SRx8\s+8GB\s+SODIMM",
    #                 r"Socket0.ChB.Dimm0:\s+2400MT/s\s+Kingston\s+SRx8\s+8GB\s+SODIMM"]
