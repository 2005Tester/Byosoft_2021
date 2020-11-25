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
from HY5 import updatebios
from HY5 import Hy5Config
from RedFish import config
import Common.ssh as SSH
from Common import Misc


def dump_smbios(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping smbios table...")
        return ssh.dump_info('dmidecode', Hy5Config.LOG_DIR)


def lspci(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping pci info...")
        return ssh.dump_info('lspci', Hy5Config.LOG_DIR)


def dmesg(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping dmesg...")
        return ssh.dump_info('dmesg', Hy5Config.LOG_DIR)


def cpuinfo(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping cpuinfo...")
        return ssh.dump_info('cat /proc/cpuinfo', Hy5Config.LOG_DIR)


# Check whether cpu core count is equal to "num" in OS
def verify_cpucore_count(ssh, num):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
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


def boot_manager(serial, ssh):
    logging.info("HaiYan5 Common Test Lib: boot to boot manager")
    if not force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to boot manager")
    msg = "Boot Manager Menu"
    if not serial.boot_with_hotkey(Hy5Config.Key.F11, msg, 300):
        logging.info("Booting to boot manager failed.")
        return
    return True


def ping_sut():
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=config.PING_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        output = stdoutput.decode()
        now = time.time()
        time_spent = (now-start_time)
        if output.find("TTL=") >= 0:
            print("SUT is online now")
            return True
        if time_spent > 600:
            print("Lost SUT for %s seconds, refresh BIOS image" % time_spent)
            try:
                updatebios.update_specific_img(config.BIOS)
                time.sleep(300)
                start_time = time.time()
            except Exception as e:
                print(e)


# update by arthur,
def is_power_off(ssh):
    logging.info("Check power status...")
    cmd_on = 'ipmcget -d powerstate'
    ret_confirm = 'Off'
    if ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        ret = ssh.execute_command_interaction(cmd_on)
        # print(ret)
        if ret_confirm in ret.decode():
            return True
        else:
            return False


# updated by arthur,
def power_on(ssh):
    logging.info("Power on system.")
    cmd_reset = 'ipmcset -d powerstate -v 1\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: Power on failed")
        return


def force_reset(ssh):
    if is_power_off(ssh):
        print('Current power state is Off, power on first')  # updated by arthur,
        if power_on(ssh):
            return True
    else:
        logging.info("Current power state is On, force system reset.")  # updated by arthur,
        cmd_reset = 'ipmcset -d frucontrol -v 0\n'
        ret_reset = 'Do you want to continue'
        cmd_confirm = 'Y\n'
        ret_confirm = 'successfully'
        cmds = [cmd_reset, cmd_confirm]
        rets = [ret_reset, ret_confirm]
        if ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
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
    if ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: force powercycle failed")
        return


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
    if ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: reboot sut failed")
        return


def sp_boot(serial, ssh):
    tc = ('001', 'SP Boot by F6', 'SP Boot by Hotkkey')
    result = Misc.LogHeaderResult(tc, serial)
    if not force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("SP boot by F6: testing")
    msg = "BIOS boot completed."
    if not serial.boot_with_hotkey(Hy5Config.Key.F6, msg, 300):
        result.log_fail()
        return
    result.log_pass()
    return True


def boot_ubuntu(serial, ssh):
    tc = ('002', 'Boot to UEFI Ubuntu', 'Boot to UEFI Ubuntu 18.04')
    result = Misc.LogHeaderResult(tc, serial)
    key_down = [chr(0x1b), chr(0x5b), chr(0x42), chr(0x0D)]
    if not boot_manager(serial, ssh):
        return
    serial.send_keys(key_down)
    if not serial.is_msg_present('byosoft-2488H-V6 login'):
        result.log_fail()
        return
    result.log_pass()
    return True


def boot_windows(serial, ssh):
    tc = ('003', 'Boot to UEFI windows', 'Boot to UEFI Windows 2019')
    result = Misc.LogHeaderResult(tc, serial)
    if not force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    if not serial.is_msg_present('Computer is booting, SAC started and initialized'):
        result.log_fail()
        return
    result.log_pass()
    return True


def bmc_dump(ssh, path, name):
    cmd_diag = ["ipmcget -d diaginfo\n"]
    rtn_diag = ["successfully"]
    ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD)
    SFTP = SSH.sftp(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD)
    SFTP.login()
    files = SFTP.sftp.listdir("/tmp")
    bin_files = [b for b in files if ".bin" in b]
    if bin_files:
        for bi in bin_files:
            SFTP.sftp.remove(bi)
            print("Remove {}!".format(bi))
    print("Start BMC dump, Please wait...")
    if ssh.interaction(cmd_diag, rtn_diag):  # this function will default close session, re-open in next step
        print("Dump completed, Copy to {}".format(path))
        SFTP.sftp.get("/tmp/dump_info.tar.gz", "{}/{}_dump_info.tar.gz".format(path, name))
        print("Copy dump log completed!")
        SFTP.sftp.close()
        return True

        
# clear CMOS on BMC side
def clearCMOS(ssh):
    logging.info("Clear CMOS")
    cmd_clearcoms = 'ipmcset -d clearcmos\n'
    ret_clearcmos = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_clearcoms, cmd_confirm]
    rets = [ret_clearcmos, ret_confirm]
    if ssh.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: clear CMOS failed")
        return
