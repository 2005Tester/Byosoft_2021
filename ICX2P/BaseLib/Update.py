#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import paramiko
import time
import logging
import os
import re
from Common import ssh, Misc, GitLab
from ICX2P import SutConfig


# Obtain the path of latest bios image from Gitlab artifacts
def get_test_image(dst):
    gitlab_icx = GitLab.Gitlab(31, 'PbLqm_njsnGxCQBtHoMG')
    test_image = gitlab_icx.download_latest_image_master(dst, ".bin")
    logging.info("Image for test: {0}".format(test_image))
    return(test_image)   

# Upload BIOS image to SUT BMC
def upload_bios(src):
    # Upload BIOS image (.bin. .hpm) to SUT
    bin_file = 'rp001.bin'
    hpm_file = 'bios.hpm'
    transport = paramiko.Transport(SutConfig.BMC_IP, 22)
    transport.banner_timeout = 90  # Increase timeout value to fix connection issue
    transport.connect(username=SutConfig.BMC_USER, password=SutConfig.BMC_PASSWORD)
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
    output = os.path.join(src, 'output')
    for filename in os.listdir(output):
        if re.search('.bin', str(filename)):
            try:
                logging.info("Uploading image to BMC...")
                res = sftp.put(os.path.join(output, filename), bin_file)
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
        elif re.search('.hpm', str(filename)):
            try:
                res = sftp.put(os.path.join(output, filename), hpm_file)
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
            sftp.close()
            transport.close()
            return


def hpm_update():
    cmd_hpmupdate = 'ipmcset -d upgrade -v /tmp/bios.hpm\n'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(SutConfig.BMC_IP, 22, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)
    op = s.invoke_shell()
    op.send(cmd_hpmupdate)
    time.sleep(5)
    res = op.recv(1024)
    if re.search('successfully',res.decode('utf-8')):
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
    
    if sshconn.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
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

    if sshconn.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return sshconn.interaction(cmds, rets)
    

def update_specific_img(bios, serial):
    if not upload_bios(bios):
        logging.info("Upload BIOS image failed")
        return
    if not program_flash():
        logging.info("Program flash failed")
        return
    if not poweron_sut():
        logging.error("power on sut fail")
        return
    if not serial.is_boot_success():
        return
    time.sleep(15)
    return True


# Update BIOS to latest CI build
def update_bios_ci(serial):
    tc = ('000', 'Update BIOS by BMC', 'Outband BIOS update')
    result = Misc.LogHeaderResult(tc, serial)
    image = get_test_image(SutConfig.BINARY_DIR)
    if not image:
        result.log_skip()
        return
    if not update_specific_img(image, serial):
        result.log_fail()
        return
    result.log_pass()
    return True


if __name__ == '__main__':
    upload_bios()
    program_flash()
