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


def power_on(ssh):
    logging.info("Power on system...")
    cmd_reset = 'cliset -d cpldreg -v 0xe8 0\n'
    cmd_reset_1 = 'cliset-dc pld bit-v0xe7 0 0\n'
    cmd_reset_2 = 'cliset-dc pld bit-vOxe7 0 1\n'
    ret_confirm = 'ok'
    cmds = [cmd_reset, cmd_reset_1, cmd_reset_2]
    rets = [ret_confirm, ret_confirm, ret_confirm]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("PANGEA Common Lib: system power on failed")
        return


def power_off(ssh):
    logging.info("Power off system...")
    cmd = 'TMOUT=0'
    cmd_reset = 'cliset -d cpldreg -v 0xe8 0\n'
    cmd_reset_1 = 'cliset-dc pld bit-v0xe7 1 0\n'
    cmd_reset_2 = 'cliset-dc pld bit-vOxe7 1 1\n'
    ret_confirm = 'ok'
    cmds = [cmd, cmd_reset, cmd_reset_1, cmd_reset_2]
    rets = ['', ret_confirm, ret_confirm, ret_confirm]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("PANGEA Common Lib: system power off failed")
        return


def power_cycle(ssh):
    logging.info("Start to power cycle the system...")
    if not power_off(ssh):
        return
    else:
        time.sleep(5)
        if not power_on(ssh):
            logging.error("PANGEA Common Lib: system power cycle failed")
            return

    return True


def reboot_system(ssh):
    logging.info("Start to reboot the system...")
    cmd_reset = 'cliset -d rebootsystem -v 0\n'
    ret_cmd_reset = 'Have you read danger alert message carefully?'
    cmd_confirm1 = 'y\r'
    ret_cmd_confirm1 = 'Are you sure you really want to perform the operation?'
    cmd_confirm2 = 'y\r'
    ret_cmd_confirm2 = 'Input your password:'
    pw = 'Huawei12#$\r'
    ret_pw = 'Soft Reboot System successfully'
    cmds = [cmd_reset, cmd_confirm1, cmd_confirm2, pw]
    rets = [ret_cmd_reset, ret_cmd_confirm1, ret_cmd_confirm2, ret_pw]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("PANGEA Common Lib: system reset failed")
        return


def hard_reset(ssh):
    logging.info("Start to power cycle the system...")
    cmd_reset = 'cliset -d rebootsystem -v 1\n'
    ret_cmd_reset = 'Have you read danger alert message carefully?'
    cmd_confirm1 = 'y\r'
    ret_cmd_confirm1 = 'Are you sure you really want to perform the operation?'
    cmd_confirm2 = 'y\r'
    ret_cmd_confirm2 = 'Input your password:'
    pw = 'Huawei12#$\r'
    ret_pw = 'Soft Reboot System successfully'
    cmds = [cmd_reset, cmd_confirm1, cmd_confirm2, pw]
    rets = [ret_cmd_reset, ret_cmd_confirm1, ret_cmd_confirm2, ret_pw]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("PANGEA Common Lib: system cycle failed")
        return
