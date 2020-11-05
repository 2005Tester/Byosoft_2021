#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

import re
import logging
import time
from Common import ssh
from Common import SutSerial
from Moc25 import Moc25TcLib
from Moc25 import Moc25Config


# Verify BIOS version get from BMC is correct
def report_bios_ver_bmc(ssh):
    logging.info("<TC008><Tittle>Verify BIOS Version from BMC:Start")
    logging.info("<TC008><Description>检查BIOS上报给BMC的版本信息是否正确")
    cmd = "ipmitool alioem version"
    if not ssh.login(Moc25Config.BMC_IP, Moc25Config.BMC_USER, Moc25Config.BMC_PASSWORD):
        logging.info("<TC008><Result>Verify BIOS Version from BMC:Fail")
        return
    logging.info("Dumping version info from BMC...")
    res = ssh.execute_command(cmd)
    if not re.search(Moc25Config.BIOS_VERSION, res):
        logging.info("<TC008><Result>Verify BIOS Version from BMC:Fail")
        return
    logging.info("<TC008><Result>Verify BIOS Version from BMC:Pass")
    return True


# IPMI 引导测试 PXE
def ipmi_set_boot_pxe(serial, ssh):
    logging.info("<TC009><Tittle>IPMI引导测试-PXE:Start")
    logging.info("<TC009><Description>使用IPMI命令设置BIOS从PXE启动")
    cmd = ["ipmitool chassis bootdev pxe\n"]
    ret = ["Set Boot Device to pxe"]

    logging.info("Login BMC via SSH...")
    if not ssh.login(Moc25Config.BMC_IP, Moc25Config.BMC_USER, Moc25Config.BMC_PASSWORD):
        logging.info("<TC009><Result>IPMI引导测试-PXE:Fail")
        return
    if not ssh.interaction(cmd, ret):
        logging.info("SSH command execution fail")
        logging.info("<TC009><Result>IPMI引导测试-PXE:Fail")
        return
    time.sleep(150)
    if not Moc25TcLib.force_reset2(serial):
        logging.info("<TC009><Result>IPMI引导测试-PXE:Fail")
        return

    if not serial.is_msg_present_general("Boot from native PXE LAN"):
        logging.info("<TC009><Result>IPMI引导测试-PXE:Fail")
        return
    logging.info("<TC009><Result>IPMI引导测试-PXE:Pass")
    return True


    # IPMI 引导测试 Setup
def ipmi_set_boot_bios(serial, ssh):
    logging.info("<TC010><Tittle>IPMI引导测试-BIOS:Start")
    logging.info("<TC010><Description>使用IPMI命令设置启动到BIOS设置界面")
    cmd = ["ipmitool chassis bootdev bios\n"]
    ret = ["Set Boot Device to bios"]

    logging.info("Sending BMC command...")
    if not ssh.login(Moc25Config.BMC_IP, Moc25Config.BMC_USER, Moc25Config.BMC_PASSWORD):
        logging.info("<TC010><Result>IPMI引导测试-BIOS:Fail")
        return
    if not ssh.interaction(cmd, ret):
        logging.info("SSH command execution fail")
        logging.info("<TC010><Result>IPMI引导测试-BIOS:Fail")
        return
    time.sleep(150)
    if not Moc25TcLib.force_reset(serial):
        logging.info("<TC010><Result>IPMI引导测试-BIOS:Fail")
        return

    if not serial.is_msg_present_general("Byosoft ByoCore"):
        logging.info("<TC010><Result>IPMI引导测试-BIOS:Fail")
        return
    logging.info("<TC010><Result>IPMI引导测试-BIOS:Pass")
    return True