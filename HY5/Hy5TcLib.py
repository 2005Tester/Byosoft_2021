# -*- encoding=utf8 -*-
import time
import subprocess
import logging
from HY5 import updatebios
from HY5 import Hy5Config
from RedFish import config


def dc_cycling(ssh, serial, n):
    for i in range(n):
        try:
            logging.info("Test cycle: {0}".format(i))
            rebootsut(ssh)
            serial.is_boot_success()
        except Exception as e:
            logging.error(e)


def boot_manager(serial, ssh):
    logging.info("HaiYan5 Common Test Lib: boot to boot manager")
    logging.info("Rebooting SUT...")
    if not rebootsut(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to boot manager")
    if not serial.hotkey_f11():
        logging.info("Booting to boot manager failed.")
        return
    return True


def sp_boot(serial, ssh):
    logging.info("HaiYan5 Common Test Lib: sp_boot")
    logging.info("Rebooting SUT...")
    if not rebootsut(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to SP...")
    if not serial.hotkey_f6():
        logging.info("Booting to SP Failed.")
        return
    return True


def ping_sut():
    cmd_update_bios = r'python C:\UpdateTool\updatebios.py ' + config.BIOS
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=config.PING_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        output = stdoutput.decode()
        now = time.time()
        time_spent = (now-start_time)
        if output.find("TTL=") >= 0:
            print("SUT is online now")
            break
        if time_spent > 900:
            print("Lost SUT for %s seconds, refresh BIOS image" % time_spent)
            try:
                updatebios.update_specific_img(config.BIOS)
                time.sleep(300)
                start_time = time.time()
            except Exception as e:
                print(e)


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
