#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import os
import logging
from batf.SutInit import Sut
from batf import SshLib, SerialLib, Ci, var
from SPR4P.Config import SutConfig
from SPR4P.Config.PlatConfig import Msg, Key
from SPR4P.BaseLib import SetUpLib, BmcLib


# Obtain the path of latest bios image from Gitlab artifacts
def get_test_image(branch, build_type="debug", path=SutConfig.Env.LOG_DIR):
    build_support = {"debug": "debug-build", "equip": "equ-build"}
    if build_type.lower() not in build_support:
        raise TypeError(f"Gitlab CI build type '{build_type}' not in support list: {build_support}")
    project_id = 58
    private_key = 'PbLqm_njsnGxCQBtHoMG'
    build = build_support[build_type.lower()]
    gitlab_spr = Ci.Gitlab(project_id, private_key)
    test_image = gitlab_spr.download_latest_image(branch, path, f"{SutConfig.Env.BIOS_BIN_NAME}.*.bin", build)
    logging.info("Image for test: {0}".format(test_image))
    return test_image


def upload_bios_image(src_file, dst_file='/tmp/rp001.bin'):
    if not os.path.isfile(src_file):
        logging.error(f"Invalid source file to upload: {src_file}")
        return
    file_size = os.path.getsize(src_file)
    try_counts = 0
    while try_counts < 3:
        SshLib.sftp_remove_file(Sut.BMC_SFTP, ".bin|.hpm|.tar.gz", dir="/tmp")
        if SshLib.sftp_upload_file(Sut.BMC_SFTP, src_file=src_file, dst_file=dst_file, ret_msg=f'{file_size}'):
            return True
        try_counts += 1
    logging.error(f"Upload bios image to bmc failed with {try_counts} times retry")


def update_bios_bin(bios_img):
    logging.info("Remove existing BIOS image from BMC")
    if not upload_bios_image(bios_img):
        return
    if not BmcLib.program_flash():
        return
    logging.info("BIOS update successfully.")
    logging.info("BIOS Imgae: {0}".format(bios_img))
    return True


def flash_hpm(hpm_name="bios.hpm"):
    cmd = 'ipmcset -d upgrade -v /tmp/{}'.format(hpm_name)
    rtn = 'successfully'
    if not BmcLib.power_off():
        return
    logging.info('Start to flash hpm image')
    if rtn in SshLib.execute_command(Sut.BMC_SSH, cmd, print_result=False):
        logging.info("HPM BIOS flash successfully")
        return True


# flash hpm bios from a specific directory
def update_bios_hpm(hpm_file):
    hpm_path, hpm_name = os.path.split(hpm_file)
    if not upload_bios_image(src_file=hpm_file, dst_file=f"/tmp/{hpm_name}"):
        return
    if not flash_hpm(hpm_name):
        return
    if not BmcLib.power_on():
        return
    if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.LOGO_SHOW, delay=900):
        return
    logging.info("HPM BIOS update successfully.")
    logging.info("HPM image: {0}".format(hpm_file))
    return True


def flash_bios_bin_and_init(img=None):
    if not img:
        img = var.get("biosimage") if var.get("biosimage") else get_test_image(SutConfig.Env.BRANCH_LATEST)
    if not update_bios_bin(img):
        return
    BmcLib.set_boot_mode("uefi", once=False)
    if not SetUpLib.update_default_password():
        return
    if not SetUpLib.move_option_in_bootmanager(Msg.BOOT_OPTION_OS, 6):
        return
    return True
