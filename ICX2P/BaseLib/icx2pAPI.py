#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import datetime
import logging
import subprocess
import time
from Core import SerialLib
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import PowerLib, SetUpLib


def dump_smbios(ssh, cmd='dmidecode'):
    if ssh.login():
        logging.info("Dumping smbios table...")
        return ssh.dump_info(cmd, SutConfig.LOG_DIR)


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
            # try:
            #     updatebios.update_specific_img(config.BIOS, serial)
            #     time.sleep(300)
            #     start_time = time.time()
            # except Exception as e:
            #     print(e)


# clear CMOS on BMC side
def clearCMOS(ssh):
    logging.info("Clear CMOS")
    cmd_clearcoms = 'ipmcset -d clearcmos\n'
    ret_clearcmos = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_clearcoms, cmd_confirm]
    rets = [ret_clearcmos, ret_confirm]
    if PowerLib.is_power_off():
        pass
    else:
        if PowerLib.power_off():
            time.sleep(30)  # wait for 30s due to if in OS
            pass

    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: clear CMOS failed")
        return


# OS - capture time,
def osTime(ssh):
    t1 = ''
    if ssh.login():
        logging.info("Capture time...")
        res = ssh.execute_command(r'hwclock --show')
        t = res.decode()
        t0 = t.split('.')[0]
        t1 = datetime.datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
        time.sleep(1)
    ssh.execute_command('reboot')
    return t1


# used for rw test
def rw_everything(ssh, exp_res, mem_bar, cmd='mmr', str=' ', start=1, stop=3):
    """
    :str is split flag, default is ' ' - blank
    :start from list, default is 1
    :stop by list, default is 3
    :param exp_res is a excepted num list
    :param mem_bar should be printed in full debug message, e.g mem0_bar and mem1_bar address - list
    :param cmd is a parameter supported by rw tool, e.g mmr
    """
    time.sleep(5)
    org_list = []
    if ssh.login():
        logging.info('Start to rw the address...')
        for i in mem_bar:
            res = ssh.execute_command(r'cd {0};./rw {1} {2} | grep {2}'.format(SutConfig.RW_PATH, cmd, i, i))
            logging.debug(res)
            for j in res.split(str)[start:stop]:
                org_list.append(j)
        time.sleep(1)
    logging.debug(list(set(org_list)))
    if exp_res != list(set(org_list)):
        logging.info('Register verified - fail')
        return False
    logging.info('Register verified - pass')
    return True


# def to BIOS Setup - System Time page
def toSysTime(serial):
    if not toBIOSnp(serial):
        return
    serial.send_keys_with_delay(SutConfig.key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    return True


def toBIOSConf(serial):
    serial.send_keys_with_delay(SutConfig.key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    return True


# to BIOS with power action, for restore test Env,
def toBIOS(serial, ssh, pwd=SutConfig.BIOS_PASSWORD):
    if not PowerLib.force_reset():
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.waitString(Msg.HOTKEY_PROMPT_DEL, timeout=600):
        return
    serial.send_keys(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString(SutConfig.press_f2, timeout=60):
        return
    serial.send_data(pwd)
    time.sleep(0.2)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    # if serial.waitString(SutConfig.pwd_info):
    #     serial.send_data(chr(0x0D))  # Send Enter
    # else:
    #     # 新密码输入没有提示信息，无需按两次回车键
    #     logging.info('The default pwd may be modified before, ignore it and try the new pwd next step')
    #     serial.send_keys_with_delay([Key.RIGHT, Key.LEFT])
    #     pass
    if not serial.waitString('Continue', timeout=60):
        return
    logging.info("Booting to setup successfully")
    return True


# to BIOS without power action
def toBIOSnp(serial, pwd=SutConfig.BIOS_PASSWORD):
    logging.info("HaiYan5 Common Test Lib: boot to setup")
    if not serial.waitString(Msg.HOTKEY_PROMPT_DEL, timeout=600):  # set to 600 开启全打印，启动时间较长
        return
    serial.send_keys(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString(SutConfig.press_f2, timeout=60):  # 考虑全打印
        return
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    # if serial.waitString(SutConfig.pwd_info):
    #     serial.send_data(chr(0x0D))  # Send Enter
    # else:
    #     # 新密码输入没有提示信息，无需按两次回车键
    #     logging.info('The default pwd may be modified before, ignore it and try the new pwd next step')
    #     serial.send_keys_with_delay([Key.RIGHT, Key.LEFT])
    #     pass
    # if not serial.waitString('Continue', timeout=60):  # 考虑全打印，延长至1分钟
    #     return
    logging.info("Booting to setup successfully")
    return True


def dcCycle():
    if not SetUpLib.boot_to_setup():
        return
    if not PowerLib.force_power_cycle():
        return
    logging.info("Booting to setup")
    if not SetUpLib.continue_to_setup():
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


def pressDelnp(serial):
    if not serial.waitString(Msg.HOTKEY_PROMPT_DEL, timeout=300):
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString(SutConfig.press_f2, timeout=60):
        return
    return True


def reset_default(serial):
    logging.info("Reset BIOS to dafault by F9")
    if not SetUpLib.boot_to_bios_config():
        return
    SerialLib.send_keys_with_delay(serial, Key.RESET_DEFAULT)
    if not SerialLib.is_msg_present(serial, Msg.BIOS_BOOT_COMPLETE):
        logging.info("Reset dafault by F9:Fail")
        return
    logging.info("Reset dafault by F9:Pass")
    return True


# open/close debug message with bmc cmd
def debug_message(ssh_bmc, enable=True):
    value = 1 if enable else 2
    cmd1 = f"ipmcset -t maintenance -d biosprint -v {value}\n"
    rtn1 = 'Do you want to continue'
    cmd2 = 'Y\n'
    rtn2 = 'successfully'
    if not ssh_bmc.login():
        return
    if not enable:
        logging.info("[Serial Debug Message] -> Disabled")
        return ssh_bmc.interaction([cmd1], [rtn2])
    logging.info("[Serial Debug Message] -> Enabled")
    return ssh_bmc.interaction([cmd1, cmd2], [rtn1, rtn2])
