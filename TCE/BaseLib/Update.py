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
from Core.SutInit import Sut
from Core import SshLib
from Common import ssh, GitLab
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Msg
from TCE.BaseLib import SetUpLib, BmcLib


# Obtain the path of latest bios image from Gitlab artifacts
def get_test_image(dst, branch, job):
    gitlab_icx = GitLab.Gitlab(31, 'PbLqm_njsnGxCQBtHoMG')
    res = BmcLib.get_productname()
    if res == ['4U']:
        test_image_4u = gitlab_icx.download_latest_image(branch, dst, "WTCEAV+\d+\_byo", job)
        logging.info("Image for test: {0}".format(test_image_4u))
        return (test_image_4u)
    elif res == ['2U']:
        test_image_2u = gitlab_icx.download_latest_image(branch, dst, "WTCEBV+\d+\_byo", job)
        logging.info("Image for test: {0}".format(test_image_2u))
        return (test_image_2u)
    else:
        logging.info('Unsupported product, break the bios flash.')
        return False


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


def poweron_sut():
    logging.info("Power on Sut.")
    sshconn = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    ret_power_on = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'Control fru0 power on successfully'
    cmds = [cmd_power_on, cmd_confirm]
    rets = [ret_power_on, ret_confirm]

    if sshconn.login():
        return sshconn.interaction(cmds, rets)


def update_specific_img(bios):
    if not upload_bios(bios):
        logging.info("Upload BIOS image failed")
        return
    if not BmcLib.program_flash():
        logging.info("Program flash failed")
        return
    if not poweron_sut():
        logging.error("power on sut fail")
        return
    if not SetUpLib.wait_message(Msg.BIOS_BOOT_COMPLETE):
        return
    if not SetUpLib.update_default_password():
        return
    time.sleep(15)
    return True


def update_bios(bios_img):
    target_bin = "./rp001.bin"
    logging.info("Remove existing BIOS image from BMC")
    SshLib.sftp_remove_file(Sut.BMC_SFTP, ".bin")
    if not SshLib.sftp_upload_file(Sut.BMC_SFTP, bios_img, target_bin, '67108864'):
        return
    if not BmcLib.program_flash():
        return
    logging.info("BIOS update successfully.")
    logging.info("BIOS Imgae: {0}".format(bios_img))
    return True
