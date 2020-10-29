#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import time
import subprocess
import logging
import re
from Moc25 import updatebios
from Moc25 import Moc25Config


def dump_smbios(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping smbios table...")
        return ssh.dump_info('dmidecode', Moc25Config.LOG_DIR)


def lspci(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping pci info...")
        return ssh.dump_info('lspci', Moc25Config.LOG_DIR)


def dmesg(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping dmesg...")
        return ssh.dump_info('dmesg', Moc25Config.LOG_DIR)


def cpuinfo(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping cpuinfo...")
        return ssh.dump_info('cat /proc/cpuinfo', Moc25Config.LOG_DIR)

# Check whether cpu core count is equal to "num" in OS
def verify_cpucore_count(ssh, num):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Checking cpu core count...")
        cpuinfo = ssh.execute_command('cat /proc/cpuinfo | grep "cpu cores" | uniq')
        logging.debug(cpuinfo)
        if re.search(str(num), cpuinfo):
            logging.info("Core count is correct")
            return True
        else:
            logging.info("Core count is not correct.")
            return


def dc_cycling(ssh, serial, n):
    for i in range(n):
        try:
            logging.info("Test cycle: {0}".format(i))
            force_power_cycle(ssh)
            serial.is_boot_success()
        except Exception as e:
            logging.error(e)


def force_power_cycle(ssh):
    pass


def force_reset(ssh):
    logging.info("Force system reset.")
    return True
    """
    cmd_reset = 'ipmitool chassis power reset\n'
    ret_reset = 'Command not supported in present state'
    cmds = [cmd_reset]
    rets = [ret_reset]
    if ssh.login(Moc25Config.BMC_IP, Moc25Config.BMC_USER, Moc25Config.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("Moc25 Common TC: force system reset failed")
        return
    """


def rebootsut(ssh):
    cmd_shutdown = 'ipmcset -d powerstate -v 2\n'
    ret_shutdown = 'Do you want to continue'
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    ret_power_on = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm_off = 'Control fru0 forced power off successfully'
    ret_confirm_on = 'Control fru0 power on successfully'
    cmds = [cmd_shutdown, cmd_confirm, cmd_power_on, cmd_confirm]
    rets = [ret_shutdown, ret_confirm_off, ret_power_on, ret_confirm_on]
    if ssh.login(Moc25Config.BMC_IP, Moc25Config.BMC_USER, Moc25Config.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("Moc25 Common TC: reboot sut failed")
        return


def boot_AliOS(serial, ssh):
    logging.info("<TC001><Tittle>Boot to AliOS:Start")
    logging.info("<TC001><Description>Boot to AliOS")
    if not force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    if not serial.is_msg_present_general('Alibaba Group Enterprise Linux Server release 7.2', 120):
        logging.info("<TC001><Result>Boot to AliOS:Fail")
        return
    logging.info("<TC001><Result>Boot to AliOS:Pass")
    return True


