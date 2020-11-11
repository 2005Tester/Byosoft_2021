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

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


# BIOS Information
BIOS_VERSION = '2.0.ID.AL.E.005.01'
BMC_VERSION = '5.34'

# Report Setting
REPORT_TEMPLATE = "Report\\template_Moc"

# Environment settings
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


# Email report settings
MAIL_SERVER = ''
MAIL_FROM = 'ci@byosoft.com.cn'
MAIL_PW = ''
MAIL_TO = 'gaojie@byosoft.com.cn,ci@byosoft.com.cn,yq268009@alibaba-inc.com'
MAIL_TEMPLATE = 'Report\\email_template_Moc'
