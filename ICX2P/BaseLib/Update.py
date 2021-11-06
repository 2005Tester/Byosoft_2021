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
from batf.SutInit import Sut
from batf import SshLib, SerialLib, Ci
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Msg
from ICX2P.BaseLib import SetUpLib, BmcLib


# Obtain the path of latest bios image from Gitlab artifacts
def get_test_image(dst, branch, job):
    gitlab_icx = Ci.Gitlab(31, 'PbLqm_njsnGxCQBtHoMG')
    test_image = gitlab_icx.download_latest_image(branch, dst, ".bin", job)
    logging.info("Image for test: {0}".format(test_image))
    return(test_image)


# Upload BIOS image to SUT BMC
def upload_bios(src):
    # Upload BIOS image (.bin. .hpm) to SUT
    bin_file = 'rp001.bin'
    hpm_file = 'bios.hpm'
    transport = paramiko.Transport(SutConfig.Env.BMC_IP, 22)
    transport.banner_timeout = 90  # Increase timeout value to fix connection issue
    transport.connect(username=SutConfig.Env.BMC_USER, password=SutConfig.Env.BMC_PASSWORD)
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


def hpm_update(hpm_name="bios.hpm"):
    cmd = 'ipmcset -d upgrade -v /tmp/{}\n'.format(hpm_name)
    rtn = 'successfully'
    BmcLib.power_off()
    logging.info('Start to flash hpm image')
    if SshLib.interaction(Sut.BMC_SSH, [cmd], [rtn], timeout=600):
        logging.info("HPM BIOS flash successfully")
        return True


def update_specific_img(bios):
    if not upload_bios(bios):
        logging.info("Upload BIOS image failed")
        return
    if not BmcLib.program_flash():
        logging.info("Program flash failed")
        return
    if not BmcLib.power_on():
        logging.error("power on sut fail")
        return
    if not SetUpLib.wait_message(Msg.BIOS_BOOT_COMPLETE):
        return
    if not SetUpLib.update_default_password():
        return
    time.sleep(15)
    return True


def update_bios(bios_img):
    target_bin = "/tmp/rp001.bin"
    logging.info("Remove existing BIOS image from BMC")
    SshLib.sftp_remove_file(Sut.BMC_SFTP, target_bin)
    if not SshLib.sftp_upload_file(Sut.BMC_SFTP, bios_img, target_bin, '67108864'):
        return
    if not BmcLib.program_flash():
        return
#    if not BmcLib.power_on():
#        return
#    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
#        return
    logging.info("BIOS update successfully.")
    logging.info("BIOS Imgae: {0}".format(bios_img))
    return True


# flash hpm bios from a specific directory
def flash_local_hpm(img_file):
    SshLib.sftp_remove_file(Sut.BMC_SFTP, ".bin", "/tmp")
    SshLib.sftp_remove_file(Sut.BMC_SFTP, ".hpm", "/tmp")
    SshLib.sftp_remove_file(Sut.BMC_SFTP, ".tar.gz", "/tmp")
    if not os.path.isfile(img_file):
        logging.info("Invalid hpm file, please double check")
        return
    hpm_path, hpm_name = os.path.split(img_file)
    if not SshLib.sftp_upload_file(sftp=Sut.BMC_SFTP, src_file=img_file, dst_file=r"/tmp/"+hpm_name, ret_msg="rw"):
        return
    if not hpm_update(hpm_name):
        return
    if not BmcLib.power_on():
        return
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.HOTKEY_PROMPT_DEL, delay=600):
        return
    logging.info("HPM BIOS update successfully.")
    logging.info("HPM image: {0}".format(img_file))
    return True
