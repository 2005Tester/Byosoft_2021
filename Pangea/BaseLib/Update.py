#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import os
from Core import Ci
from Pangea.SutConfig import Msg
from Pangea.BaseLib import SshLib, PowerLib


# Obtain the path of latest bios image from Gitlab artifacts
def get_test_image(dst):
    gitlab_icx = Ci.Gitlab(41, 'zY5yGx4mXyVo-YC6rjYv')
    test_image = gitlab_icx.download_latest_image_master(dst, 'Pangea_')
    logging.info(test_image)
    return test_image


# Upload BIOS image to SUT BMC
def upload_bios(src, ssh):
    # Upload BIOS image (.bin) to SUT
    for filename in os.listdir(src):
        if '.bin' in filename:
            local_path = src + '\\' + filename
            try:
                if not SshLib.sftp_put_via_scp(ssh, local_path, r'/data/HwWhitleyPkg_DEBUG.bin', 30):
                    print("Can not find file" + local_path)
                    return
            except FileNotFoundError as e:
                print(e)

    print("Upload to bmc OS successfully")
    return True


def program_flash(ssh):
    logging.info('Start to program the flash...')
    cmd_1 = 'cat /proc/mtd\n'
    ret_1 = '04000000'
    cmd_2 = 'cd /data/\n'
    cmd_3 = 'chmod 777 *\n'
    cmd_4 = './bmcdfx coreMsg secfw get biosMuxStatus\n'
    ret_4 = 'success'
    cmd_5 = './bmcdfx coreMsg secfw set biosMuxStatus 1\n'
    cmd_6 = 'rmmod sfc0_drv\n'
    cmd_7 = 'insmod /opt/pme/lib/modules/ko/sfc0_drv.ko\n'
    cmd_8 = 'cat /proc/mtd\n'
    cmd_9 = './mtd_debug erase /dev/mtd0 0 0x2000000\n'
    ret_9 = 'Erased'
    cmd_10 = './mtd_debug write /dev/mtd0 0 0x2000000 /data/HwWhitleyPkg_DEBUG.bin\n'
    ret_10 = 'Copied'
    cmd_11 = './bmcdfx coreMsg secfw verify bios 0\n'
    cmd_12 = './bmcdfx coreMsg secfw set biosMuxStatus 0\n'
    cmds = [cmd_1, cmd_2, cmd_3, cmd_4, cmd_5, cmd_6, cmd_7, cmd_8, cmd_9, cmd_10, cmd_11, cmd_12]
    rets = [ret_1, '', '', ret_4, ret_4, '', '', ret_1, ret_9, ret_10, ret_4, ret_4]

    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.info('Program the flash - failed...')
        return


def update_specific_img(serial, bios, ssh):
    if not upload_bios(bios, ssh):
        logging.info("Upload BIOS image failed")
        return
    if not PowerLib.power_off(ssh):
        logging.error("power off sut fail")
        return
    if not program_flash(ssh):
        logging.info("Program flash failed")
        return
    if not PowerLib.power_on(ssh):
        logging.error("power on sut fail")
        return
    if not serial.waitString(Msg.BIOS_BOOT_COMPLETE, timeout=300):
        return
    return True
