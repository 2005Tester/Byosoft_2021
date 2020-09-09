# -*- encoding=utf8 -*-
import time
import subprocess
import logging
from HY5 import updatebios
from HY5 import Hy5Config
from RedFish import config


def dump_smbios(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping smbios table...")
        return ssh.execute_command('dmidecode', Hy5Config.LOG_DIR)


def lspci(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping pci info...")
        return ssh.execute_command('lspci', Hy5Config.LOG_DIR)


def dmesg(ssh):
    if ssh.login(Hy5Config.OS_IP, Hy5Config.OS_USER, Hy5Config.OS_PASSWORD):
        logging.info("Dumping dmesg...")
        return ssh.execute_command('dmesg', Hy5Config.LOG_DIR)


def dc_cycling(ssh, serial, n):
    for i in range(n):
        try:
            logging.info("Test cycle: {0}".format(i))
            force_power_cycle(ssh)
            serial.is_boot_success()
        except Exception as e:
            logging.error(e)


def check_log():
    pass


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
    logging.info("SP boot by F6: testing")
    if not serial.hotkey_f6():
        logging.info("TC-SP Boot by F6: Fail.")
        return
    logging.info("TC-SP Boot by F6: Pass")
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
            return True
        if time_spent > 600:
            print("Lost SUT for %s seconds, refresh BIOS image" % time_spent)
            try:
                updatebios.update_specific_img(config.BIOS)
                time.sleep(300)
                start_time = time.time()
            except Exception as e:
                print(e)


def force_reset(ssh):
    logging.info("Force system reset.")
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


def boot_ubuntu(serial, ssh):
    key_down = [chr(0x1b), chr(0x5b), chr(0x42)]
    if not boot_manager(serial, ssh):
        return
    for char in key_down:
        serial.send_data(char)
    serial.send_data(chr(0x0D))
    if not serial.is_msg_present('byosoft-2488H-V6 login'):
        logging.info("TC-Boot to UEFI Ubuntu: Fail")
        return
    logging.info("TC-Boot to UEFI Ubuntu: Pass")
    return True


def boot_windows(serial, ssh):
    if not rebootsut(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    if not serial.is_msg_present('Computer is booting, SAC started and initialized'):
        logging.info("TC-Boot to UEFI windows: Fail")
        return
    logging.info("TC-Boot to UEFI windows: Pass")
    return True