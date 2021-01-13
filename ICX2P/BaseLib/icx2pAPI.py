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

import Common.ssh as SSH
from Common.ssh import sftp
from ICX2P import SutConfig
from ICX2P.SutConfig import Key
from ICX2P.BaseLib import Update

# sftp, ssh(instantiation)
s = sftp(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD)
h = SSH.SshConnection()


def dump_smbios(ssh, cmd='dmidecode'):
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
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


# update by arthur,
def is_power_off(ssh):
    logging.info("Check power status...")
    cmd_on = 'ipmcget -d powerstate\n'
    ret_confirm = 'Off'
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        ret = ssh.execute_command_interaction(cmd_on)
        if ret_confirm in ret.decode():
            logging.info('Current power state is Off')
            return True
        else:
            logging.info('Current power state is On')
            return


def power_on(ssh):
    logging.info("Power on system.")
    cmd_reset = 'ipmcset -d powerstate -v 1\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: Power on failed")
        return


def power_off(ssh):
    logging.info("Power off system - force")
    cmd_reset = 'ipmcset -d powerstate -v 2\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: Power off failed")
        return


def force_reset(ssh):
    if is_power_off(ssh):
        if power_on(ssh):
            return True
    else:
        cmd_reset = 'ipmcset -d frucontrol -v 0\n'
        ret_reset = 'Do you want to continue'
        cmd_confirm = 'Y\n'
        ret_confirm = 'successfully'
        cmds = [cmd_reset, cmd_confirm]
        rets = [ret_reset, ret_confirm]
        if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
            return ssh.interaction(cmds, rets)
        else:
            logging.error("HY5 Common TC: force system reset failed")
            return


def force_power_cycle(ssh):
    logging.info("Force power cycle.")
    cmd_powercycle = 'ipmcset -d frucontrol -v 2\n'
    ret_powercycle = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_powercycle, cmd_confirm]
    rets = [ret_powercycle, ret_confirm]
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: force powercycle failed")
        return


# clear CMOS on BMC side
def clearCMOS(ssh):
    logging.info("Clear CMOS")
    cmd_clearcoms = 'ipmcset -d clearcmos\n'
    ret_clearcmos = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_clearcoms, cmd_confirm]
    rets = [ret_clearcmos, ret_confirm]
    if is_power_off(ssh):
        pass
    else:
        if power_off(ssh):
            time.sleep(30)  # wait for 30s due to if in OS
            pass

    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: clear CMOS failed")
        return


# scp the ini file to OS...
def sftpFile(ssh):
    s.login()
    # a = s.sftp.listdir(SutConfig.unitool_path)
    # print(a)
    b = '{0}\\AT\\unitool.ini'.format(SutConfig.HPM_DIR)  # the level 2 folder name must be app, {0} - unitool path
    s.sftp.put(b, r'{0}/app/1.ini'.format(SutConfig.unitool_path), confirm=True)
    s.sftp.close()
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        logging.info("unitool...")
        ssh.execute_command(r'cd {0}/kernel;insmod ufudev.ko'.format(SutConfig.unitool_path))
        res = ssh.execute_command(r'cd {0}/app;./unitool -rf 1.ini | grep error'.format(SutConfig.unitool_path))
        if 'error' in res:
            logging.debug(res)
            return
        else:
            # ssh.execute_command(r'cd {0}/app;cp unicfg.ini 1_bef.ini'.format(SutConfig.unitool_path))
            res1 = ssh.execute_command(r'cd {0}/app;./unitool -wf 1.ini | grep error'.format(SutConfig.unitool_path))
            if 'error' in res1:
                logging.debug(res1)
                return
    h.close_session()
    return True


# cmp the diff files,
def cmpFile(ssh):
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        logging.info("cmp the config ini file...")
        res = ssh.execute_command(r'cd {0}/app;./unitool -rf 1.ini | grep error'.format(SutConfig.unitool_path))
        if 'error' in res:
            logging.debug(res)
            return
        else:
            res1 = ssh.execute_command(r'cd {0}/app;diff -b 1.ini unicfg.ini'.format(SutConfig.unitool_path))
            if len(res1) != 0:
                logging.debug(res1)
                return
    h.close_session()
    return True


# chipsec_test,
def chipsecMerge(ssh):
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        logging.info("chipsec Test...")
        res = ssh.execute_command(r'cd {0};python chipsec_main.py | grep -i failed'.format(SutConfig.chipsc_path))
        # print(res.decode())
        if 'FAILED:' in res:
            logging.debug(res)
            return
    h.close_session()
    return True


# OS - capture time,
def osTime(ssh):
    t1 = ''
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        logging.info("Capture time...")
        res = ssh.execute_command(r'hwclock --show')
        t = res.decode()
        t0 = t.split('.')[0]
        t1 = datetime.datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
        time.sleep(1)
    ssh.execute_command('reboot')
    h.close_session()
    return t1


# used for equipment test
def equipment(ssh):
    s.login()
    b = '{0}\\AT\\equipment.ini'.format(SutConfig.HPM_DIR)  # the level 2 folder name must be app, {0} - unitool path
    s.sftp.put(b, r'{0}/app/2.ini'.format(SutConfig.unitool_path), confirm=True)
    s.sftp.close()
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        logging.info("unitool...")
        ssh.execute_command(r'cd {0}/kernel;insmod ufudev.ko'.format(SutConfig.unitool_path))
        res = ssh.execute_command(r'cd {0}/app;./unitool -wf 2.ini | grep error'.format(SutConfig.unitool_path))
        if 'error' in res:
            logging.debug(res)
            return
    ssh.execute_command('reboot')
    h.close_session()
    return True


# used for unitool test
def unitool(ssh, data):
    time.sleep(5)
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        ssh.execute_command(r'cd {0}/kernel;insmod ufudev.ko'.format(SutConfig.unitool_path))
        logging.info('Start to set the value...')
        print(data)
        res = ssh.execute_command(r'cd {0}/app;./unitool -w {1} | grep error'.format(SutConfig.unitool_path, data))
        print(res)
        time.sleep(5)
        if 'error' in res:
            logging.debug(res)
            pass
    ssh.execute_command('reboot')
    h.close_session()
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
def toBIOS(serial, ssh, pwd='Admin@9000'):
    if not force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.waitString(SutConfig.msg, timeout=600):
        return
    serial.send_keys(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString(SutConfig.press_f2, timeout=60):
        return
    serial.send_data(pwd)
    time.sleep(0.2)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if serial.waitString(SutConfig.pwd_info):
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
    if not serial.waitString(SutConfig.msg, timeout=600):  # set to 600 开启全打印，启动时间较长
        return
    serial.send_keys(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString(SutConfig.press_f2, timeout=60):  # 考虑全打印
        return
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if serial.waitString(SutConfig.pwd_info):
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
    if not force_power_cycle(ssh):
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
    if not force_reset(ssh):
        return
    if not serial.waitString(SutConfig.msg, timeout=300):
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString(SutConfig.press_f2, timeout=60):
        return
    return True


def pressDelnp(serial):
    if not serial.waitString(SutConfig.msg, timeout=300):
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString(SutConfig.press_f2, timeout=60):
        return
    return True


def pressF12(serial, ssh):
    if not force_reset(ssh):
        return
    if not serial.waitString(SutConfig.msg2, timeout=300):
        return
    serial.send_keys(Key.F12)
    if not serial.waitString(SutConfig.press_f2, timeout=60):
        return
    serial.send_data(SutConfig.default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info):
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
    serial.send_keys_with_delay(SutConfig.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pwd_item):
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(SutConfig.pwd_info_1, timeout=15):
        return
    return True


# set pwd common def function, only for set PWD, do not call it for other cases
# pwd1 - previous password, pwd2 - new password
def setPWD(serial, ssh, pwd1, pwd2):
    if not toBIOS(serial, ssh, SutConfig.new_pwd_9):
        return
    if not toBIOSConf(serial):
        return
    serial.send_keys_with_delay(SutConfig.key2pwd)
    if not serial.to_highlight_option(Key.DOWN, SutConfig.pwd_item):
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString(SutConfig.pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    time.sleep(1)
    if not serial.waitString(SutConfig.pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_4, timeout=30):
        return
    time.sleep(1)
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    return True


# set password with no power action first
def setPWDnp(serial, pwd1, pwd2):
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_4, timeout=30):
        return
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.F10 + Key.Y)
    return True


# set password with no power action first
def setPWDwithoutF10(serial, pwd1, pwd2):
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_1, timeout=30):
        return
    serial.send_data(pwd1)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_2, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_3, timeout=30):
        return
    serial.send_data(pwd2)
    serial.send_data(chr(0x0D))
    if not serial.waitString(SutConfig.pwd_info_4, timeout=30):
        return
    serial.send_keys(Key.ENTER)
    time.sleep(1)
    serial.send_keys(Key.CTRL_ALT_DELETE)
    return True


def restore_env(serial, dst):
    if not Update.get_test_image(dst):
        return
    if not Update.update_specific_img(dst, serial):
        return
    return True


def reset_default(serial, ssh):
    logging.info("Reset BIOS to dafault by F9")
    keys = Key.F9 + Key.Y + Key.F10 + Key.Y
    if not toBIOS(serial, ssh):
        return
    if not toBIOSConf(serial):
        return
    # time.sleep(1)
    serial.send_keys(keys)
    if not serial.is_msg_present('BIOS boot completed.'):
        logging.info("Reset dafault by F9:Fail")
        return
    logging.info("Reset dafault by F9:Pass")
    return True
