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
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Key, Msg
from ICX2P.BaseLib import BmcLib, SetUpLib


def ping_sut():
    logging.info("Test network connection...")
    ping_cmd = 'ping {0}'.format(SutConfig.OS_IP)
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        if 'TTL=' in stdoutput.decode('gbk'):
            logging.info("SUT is online.")
            return True
        if time_spent > 600:
            logging.error("Lost SUT for %s seconds, check the ip connection" % time_spent)
            return False
            # try:
            #     updatebios.update_specific_img(config.BIOS, serial)
            #     time.sleep(300)
            #     start_time = time.time()
            # except Exception as e:
            #     print(e)


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


def toBIOSConf(serial):
    serial.send_keys_with_delay(SutConfig.key2Setup)
    if not serial.waitString('System Time', timeout=60):
        return
    return True


def dcCycle():
    if not SetUpLib.boot_to_setup():
        return
    if not BmcLib.force_power_cycle():
        return
    logging.info("Booting to setup")
    if not SetUpLib.continue_to_setup():
        return
    return True


def last_release(current_branch, step=1):
    current_ver = int(current_branch[-3:])
    last_ver = "{:03}".format(current_ver - step)
    last_branch = Msg.RELEASE_BRANCH.format(last_ver)
    return last_branch
