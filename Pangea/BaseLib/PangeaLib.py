#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import subprocess
import time

from Pangea import SutConfig
from Pangea.BaseLib import PowerLib
from Pangea.SutConfig import Key, Msg


def ping_sut():
    logging.info("Test the connection...")
    ping_cmd = 'ping {0}'.format(SutConfig.OS_IP)
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        if 'TTL=' in stdoutput.decode('gbk'):
            print("SUT is online now")
            return True
        if time_spent > 600:
            print("Lost SUT for %s seconds, check the ip connection" % time_spent)
            return False


# to BIOS with power action,
def toBIOS(serial, ssh):
    if not PowerLib.reboot_system(ssh):
        return
    logging.info("Booting to setup")
    if not serial.waitString(Msg.HOTKEY_PROMPT_F2, timeout=600):
        return
    serial.send_keys(Key.F2)
    logging.info("Hot Key sent")
    if not serial.waitString('System Information', timeout=60):
        return
    logging.info("Booting to setup successfully")
    return True


# to BIOS without power action,
def toBIOSnp(serial):
    logging.info("Booting to setup")
    if not serial.waitString(Msg.HOTKEY_PROMPT_F2, timeout=600):
        return
    serial.send_keys(Key.F2)
    logging.info("Hot Key sent")
    if not serial.waitString('System Information', timeout=60):
        return
    logging.info("Booting to setup successfully")
    return True


def reset_default(serial, ssh):
    logging.info("Reset BIOS to default by F9")
    if not toBIOS(serial, ssh):
        return
    time.sleep(1)
    serial.send_keys(Key.F9)
    time.sleep(0.1)
    serial.send_data(Key.Y)
    time.sleep(20)
    serial.send_keys(Key.F10)
    time.sleep(0.1)
    serial.send_data(Key.Y)
    if not serial.waitString(Msg.BIOS_BOOT_COMPLETE, timeout=300):
        logging.info("Reset default by F9:Fail")
        return
    logging.info("Reset default by F9:Pass")
    return True
