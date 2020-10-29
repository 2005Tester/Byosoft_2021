#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import paramiko
import datetime
import time
import logging
import os
import re
from pathlib import Path
from Common import ssh
from Moc25 import Moc25Config


# Obtain the path of latest bios image from CI build backup directory
def get_test_image(path):
    if os.path.exists(path):
        dirs = os.listdir(path)
        versions = sorted(dirs,key=lambda x: os.path.getmtime(os.path.join(path, x)))
        #print(versions)
        latest_version = versions[-1]
        logging.info("Latest Version is: {0}".format(latest_version))
    else:
        logging.error("BIOS image directroy can't be accessed, please check VPN connection.")
        return

    current_image_dir = os.path.join(path, latest_version)
    p = Path(current_image_dir)   # remote image dir of current version
    test_image = []
    for b in p.rglob('*_32MB.bin'):
        test_image.append(b)
    if not test_image:
        logging.info("Image for {0} not found, please check whether build is finished.".format(latest_version))
        return
    else:
        logging.info("BIOS image for test: %s" %(test_image[0]))
        return test_image[0]


def upload_bios(src):
    pass



def program_flash():
    pass

        
  
def poweron_sut():
    pass


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
    logging.info("<TC000><Tittle>Update BIOS by BMC:Start")
    logging.info("<TC000><Description>Outband BIOS update")
    image = get_test_image(Moc25Config.BINARY_DIR)
    if not image:
        logging.info("<TC000><Result>Update BIOS by BMC:Skip")
        return
    if not update_specific_img(image, serial):
        logging.info("<TC000><Result>Update BIOS by BMC:Fail")
        return
    logging.info("<TC000><Result>Update BIOS by BMC:Pass")
    return True


if __name__ == '__main__':
    get_test_image(Moc25Config.BINARY_DIR)

