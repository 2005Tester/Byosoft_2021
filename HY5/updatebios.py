# -*- encoding=utf8 -*-
import paramiko
import datetime
import time
import logging
import os
import re
from pathlib import Path
from Common import ssh
from HY5 import daily
from HY5 import Hy5Config


# Obtain the path of latest bios image from CI build backup directory
def get_test_image(path):
    if os.path.exists(path):
        versions = os.listdir(path)
        versions.sort(reverse=True)
        latest_version = versions[1]
        logging.info("Latest Version is: {0}".format(latest_version))
        if latest_version in daily.VER_TESTED:
            logging.info("{0} has been tested".format(latest_version))
            return
    else:
        logging.error("BIOS image directroy can't be accessed, please check VPN connection.")
        return

    current_image_dir = os.path.join(path, latest_version)
    p = Path(current_image_dir)   # remote image dir of current version
    rp001_image = []
    for b in p.rglob('HY5*_byo.bin'):
        rp001_image.append(b)
    if not rp001_image:
        logging.info("Image for {0} not found, please check whether build is finished.".format(latest_version))
        return
    else:
        logging.info("BIOS image for test: %s" %(rp001_image[0]))
        return rp001_image[0]


def upload_bios(src):
    # Upload BIOS image (.bin. .hpm) to SUT
    bin_file = 'rp001.bin'
    hpm_file = 'bios.hpm'
    transport = paramiko.Transport(Hy5Config.BMC_IP, 22)
    transport.banner_timeout = 90  # Increase timeout value to fix connection issue
    transport.connect(username=Hy5Config.BMC_USER, password=Hy5Config.BMC_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    res = sftp.listdir()
    # print(res)
    for item in res:
        if re.search(".bin", item):
            logging.info("Deleting old .bin image...")
            sftp.remove(item)
        elif re.search(".hpm", item):
            logging.info("Deleting old .hpm image...")
            sftp.remove(item)
    if re.search('.bin', str(src)):
        try:
            logging.info("Uploading image to BMC...")
            res = sftp.put(src, bin_file)
        except OSError:
            logging.error("Skip due to SSH connection error.")
            return
        if re.search("67108864", str(res)):
            logging.info("BIOS image (bin) uploaded to iBMC SFTP.")
            sftp.close()
            transport.close()
            return True
        else:
            print("Failed to upload BIOS image to iBMC SFTP.")
            print(res)
            sftp.close()
            transport.close()
            return
    elif re.search('.hpm', str(src)):
        try:
            res = sftp.put(src, hpm_file)
        except OSError:
            print("Skip due to SSH connection error.")
            return
        if re.search("rw", str(res)):
            print("HPM image uploaded to iBMC SFTP.")
            sftp.close()
            transport.close()
            return True
        else:
            print("Failed to upload hpm image to iBMC SFTP.")
            print(res)
            sftp.close()
            transport.close()
            return
    else:
        print("Invalid image type, please check source file...")
        return


def hpm_update():
    cmd_hpmupdate = 'ipmcset -d upgrade -v /tmp/bios.hpm\n'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(Hy5Config.BMC_IP, 22, Hy5Config.BMC_USER, Hy5Config.BMC_PW)
    op = s.invoke_shell()
    op.send(cmd_hpmupdate)
    time.sleep(5)
    res = op.recv(1024)
    if re.search('successfully',res.decode('utf-8')):
        # print_rawmsg(res)
        print("HPM Uploaded successfully, upgrade on next reboot")
        op.close()
        s.close()
        return True
    else:
        print("Failed to perform HPM upgrade")
        print(res)
        op.close()
        s.close()
        return  


def program_flash():
    sshconn = ssh.SshConnection()
    # Program flash procedure: power off->maint mode->attach upgrade ->load bin
    cmd_shutdown = 'ipmcset -d powerstate -v 2\n'
    ret_shutdown = 'Do you want to continue'
    cmd_maint_mode = 'maint_debug_cli\n'
    ret_maint_mode = 'Debug Shell'
    cmd_confirm = 'Y\n'
    ret_confirm = 'Control fru0 forced power off successfully'
    cmd_upgrade_mode = 'attach upgrade\n'
    ret_upgrade_mode = 'Success'
    cmd_load = 'load_bios_bin /tmp/rp001.bin\n'
    ret_load = 'load bios succefully'
    cmds = [cmd_shutdown, cmd_confirm, cmd_maint_mode, cmd_upgrade_mode, cmd_load]
    rets = [ret_shutdown, ret_confirm, ret_maint_mode, ret_upgrade_mode, ret_load]
    
    if sshconn.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        return sshconn.interaction(cmds, rets)
        
  
def poweron_sut():
    sshconn = ssh.SshConnection()
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    ret_power_on = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'Control fru0 power on successfully'
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    ret_fan_manual_mode = 'Set fan mode successfully'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    ret_fan_40 = 'Set fan level successfully'
    cmds = [cmd_power_on, cmd_confirm, cmd_fan_manual_mode, cmd_fan_40]
    rets = [ret_power_on, ret_confirm, ret_fan_manual_mode, ret_fan_40]

    if sshconn.login(Hy5Config.BMC_IP, Hy5Config.BMC_USER, Hy5Config.BMC_PASSWORD):
        return sshconn.interaction(cmds, rets)
    

def update_specific_img(bios, serial):
    if not upload_bios(bios):
        print("Upload BIOS image failed")
        return
    if not program_flash():
        print("Program flash failed")
        return
    if not poweron_sut():
        logging.error("power on sut fail")
        return
    if not serial.is_boot_success():
        return
    return True


# Update BIOS to latest CI build
def update_bios_ci(serial):
    image = get_test_image(Hy5Config.BINARY_DIR)
    update_specific_img(image, serial)


if __name__ == '__main__':
    upload_bios()
    program_flash()
