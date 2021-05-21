#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import os
import csv
import re
import datetime
import logging
import subprocess
import time
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Msg
from ICX2P.BaseLib import BmcLib, SetUpLib
from Core.SutInit import Sut
from Core import SerialLib, SshLib


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
def rw_everything(ssh, exp_res, mem_bar=None, cmd='mmr', str=' ', start=1, stop=3):
    """
    :str is split flag, default is ' ' - blank
    :start from list, default is 1
    :stop by list, default is 3
    :param exp_res is a excepted num list
    :param mem_bar should be printed in full debug message, e.g mem0_bar and mem1_bar address - list
    :param cmd is a parameter supported by rw tool, e.g mmr
    """
    if mem_bar is None:
        mem_bar = []

    org_list = []
    logging.info('Starting to rw the address...')
    for i in range(len(mem_bar)):
        res = SshLib.execute_command(ssh, r'cd {0};./rw {1} {2} | grep {2}'.format(SutConfig.RW_PATH, cmd, mem_bar[i]))
        logging.debug(res)
        if len(res) == 0:
            logging.info('RW tool can not be found')
            break
        else:
            for j in res.split(str)[start:stop]:
                org_list.append(j)

    time.sleep(0.1)
    logging.debug(org_list)
    if exp_res != org_list:
        logging.info('Register verified - fail')
        return
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


# sub function for dump cpu resource allocation table
def dump_cpu_resource():
    if not BmcLib.force_reset():
        return
    resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 10, 120, 3)
    if not resource:
        return
    data_search = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SutConfig.SysCfg.CPU_CNT)])
    rsc_table = re.search(data_search, resource)
    if not rsc_table:
        return
    lines = rsc_table.group().split("\n")
    result = []
    for line in lines:
        result.append(list(map(lambda x: x.strip(), line.split("|"))))
    csv_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    with open(os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv"), "w", newline="") as rsc:
        csv_writer = csv.writer(rsc)
        csv_writer.writerows(result)
    return csv_file