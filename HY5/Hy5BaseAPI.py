#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import time

from HY5.Hy5Config import Key
from HY5 import updatebios, Hy5Config, Hy5TcLib


# def to BIOS Setup - System Time page
def toSysTime(serial):
    if not toBIOSnp(serial):
        return
    serial.send_keys_with_delay(Hy5Config.key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    return True


def toBIOSConf(serial):
    serial.send_keys_with_delay(Hy5Config.key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    return True


# to BIOS with power action, for restore test Env,
def toBIOS(serial, ssh, pwd='Admin@9000'):
    if not Hy5TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.waitString(Hy5Config.msg, timeout=600):
        return
    serial.send_keys(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString(Hy5Config.press_f2, timeout=60):
        return
    serial.send_data(pwd)
    time.sleep(0.2)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if serial.waitString(Hy5Config.pwd_info):
        serial.send_data(chr(0x0D))  # Send Enter
    else:
        # 新密码输入没有提示信息，无需按两次回车键
        logging.info('The default pwd may be modified before, ignore it and try the new pwd next step')
        serial.send_keys_with_delay([Key.RIGHT, Key.LEFT])
        pass
    if not serial.waitString('Continue', timeout=60):
        return
    logging.info("Booting to setup successfully")
    return True


# to BIOS without power action
def toBIOSnp(serial, pwd='Admin@9000'):
    logging.info("HaiYan5 Common Test Lib: boot to setup")
    if not serial.waitString(Hy5Config.msg, timeout=600):  # set to 600 开启全打印，启动时间较长
        return
    serial.send_keys(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString(Hy5Config.press_f2, timeout=60):  # 考虑全打印
        return
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if serial.waitString(Hy5Config.pwd_info):
        serial.send_data(chr(0x0D))  # Send Enter
    else:
        # 新密码输入没有提示信息，无需按两次回车键
        logging.info('The default pwd may be modified before, ignore it and try the new pwd next step')
        serial.send_keys_with_delay([Key.RIGHT, Key.LEFT])
        pass
    if not serial.waitString('Continue', timeout=60):  # 考虑全打印，延长至1分钟
        return
    logging.info("Booting to setup successfully")
    return True


def dcCycle(serial, ssh):
    if not toBIOS(serial, ssh):
        return
    if not Hy5TcLib.force_power_cycle(ssh):
        return
    logging.info("Booting to setup")
    if not toBIOSnp(serial):
        return

    return True


# for load default test
def verify_setup_options_up(serial, setup_options, try_count):
    if serial.navigate_and_verify(Key.UP, setup_options, try_count):
        return True
    if serial.navigate_and_verify(Key.DOWN, setup_options, try_count):
        return True


def verify_setup_options_down(serial, setup_options, try_count):
    if serial.navigate_and_verify(Key.DOWN, setup_options, try_count):
        return True
    if serial.navigate_and_verify(Key.UP, setup_options, try_count):
        return True


# updated by arthur, press Delete - common def, not test cases
def pressDel(serial, ssh):
    if not Hy5TcLib.force_reset(ssh):
        return
    if not serial.waitString(Hy5Config.msg, timeout=300):
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString(Hy5Config.press_f2, timeout=60):
        return
    return True


def pressDelnp(serial):
    if not serial.waitString(Hy5Config.msg, timeout=300):
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString(Hy5Config.press_f2, timeout=60):
        return
    return True


def pressF12(serial, ssh):
    if not Hy5TcLib.force_reset(ssh):
        return
    if not serial.waitString(Hy5Config.msg2, timeout=300):
        return
    serial.send_keys(Key.F12)
    if not serial.waitString(Hy5Config.press_f2, timeout=60):
        return
    serial.send_data(Hy5Config.default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info):
        return

    serial.send_data(chr(0x0D))  # Send Enter
    return True


# enhanced pwdVerification4 def,
def enterPWD(serial, pwd):
    serial.send_keys(Key.CTRL_ALT_DELETE)
    if not toBIOSnp(serial, pwd):
        return
    if not toBIOSConf(serial):
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pwd_item):
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=15):
        return
    return True


# set pwd common def function, only for set PWD, do not call it for other cases
# pwd1 - previous password, pwd2 - new password
def setPWD(serial, ssh, pwd1, pwd2):
    if not toBIOS(serial, ssh, Hy5Config.new_pwd_9):
        return
    if not toBIOSConf(serial):
        return
    serial.send_keys_with_delay(Hy5Config.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.pwd_item):
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    time.sleep(1)
    if not serial.waitString(Hy5Config.pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_4, timeout=30):
        return
    time.sleep(1)
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    return True


# set password with no power action first
def setPWDnp(serial, pwd1, pwd2):
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_4, timeout=30):
        return
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    return True


# set password with no power action first
def setPWDwithoutF10(serial, pwd1, pwd2):
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(Hy5Config.pwd_info_4, timeout=30):
        return
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.CTRL_ALT_DELETE)
    return True


def restore_env(serial):
    image = updatebios.get_test_image(Hy5Config.BINARY_DIR)
    if not image:
        logging.info("Update BIOS by BMC:Skip")
        return
    if not updatebios.update_specific_img(image, serial):
        return

    return True