#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.


from batf.SutInit import Sut
from Moc25.Config import SutConfig
from batf.Report import ReportGen
import logging
import re


def verify_info(info_list, data):
    failures = 0
    for info in info_list:
        if not re.search(info, data):
            failures += 1
            logging.info("Not verified: {0}".format(info))
        else:
            logging.info("Verified: {0}".format(info))
    if failures == 0:
        logging.info("All information verified.")
        return True
    else:
        logging.info("{0} items not verified.".format(failures))
        return


# Verify interface type is KCS
def verify_bmc_ch_init(sut):
    serial = sut.bios_serial
    tc = ('122', 'Verify BMC init Channel', 'Verify Whether BMC channel interface type is KCS')
    result = ReportGen.LogHeaderResult(tc, serial)

    serial.send_data("dmidecode -t 38\n")
    if not serial.is_msg_present_general("Interface Type: KCS", 10):
        result.log_fail()
        return
    result.log_pass()
    return True    


def type0():
    serial = Sut.BIOS_COM
    tc = ('120', 'SMBIOS Type 0', 'Verify info mation of SMBIOS type0 is correct')
    result = ReportGen.LogHeaderResult(tc)
    msgs = ["Vendor: Byosoft", "Version: {0}".format(SutConfig.BIOS_VERSION)]
    serial.send_data("dmidecode -t 0\n")
    if not serial.waitStrings(msgs):
        result.log_fail()
        return
    result.log_pass()
    return True


def type1():
    ssh = Sut.OS_SSH
    tc = ('121', 'SMBIOS Type 1', 'Verify information of SMBIOS type1 is correct')
    result = ReportGen.LogHeaderResult(tc)
    if not ssh.login():
        logging.info("SSH login fail")
        result.log_fail()
        return
    cmd_typ1 = 'dmidecode -t 1'
    res = ssh.execute_command(cmd_typ1)
    logging.info("Dump SMBIOS Type1 ...")
    msgs = ["Manufacturer: Huaqin", "Product Name: AliMoC-MD4-42-50G", "UUID: \w{8}-\w{4}-\w{4}-\w{4}-\w{12}"]
    if not verify_info(msgs, res):
        result.log_fail()
        return
    result.log_pass()
    return True
    

def type2(ssh):
    tc = ('123', 'SMBIOS Type 2', 'Verify information of SMBIOS type2 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    logging.info("Dump SMBIOS Type2 ...")
    cmd_typ2 = 'dmidecode -t 2'
    res = ssh.execute_command(cmd_typ2)
    Mfg_info =  "Manufacturer: Huaqin"
    prod_name = "Product Name: AS03MC01"
    ver = "Version: R1296-G0001-01"
    sn =  "Serial Number: G0011CLS00000000000"
    infos = [Mfg_info, prod_name, ver, sn]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True


def type3(ssh):
    tc = ('124', 'SMBIOS Type 3', 'Verify information of SMBIOS type3 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    logging.info("Dump SMBIOS Type2 ...")
    cmd_typ3 = 'dmidecode -t 3'
    res = ssh.execute_command(cmd_typ3)
    Mfg_info =  "Manufacturer: Huaqin"
    ver = "Version: U30"
    sn =  "Serial Number: F9011CSS00000000000"
    asset_tag = "Asset Tag: ALIBMSEVT00000010123456789012345"
    infos = [Mfg_info, ver, sn, asset_tag]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True

def type4(ssh):
    tc = ('125', 'SMBIOS Type 4', 'Verify information of SMBIOS type4 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    logging.info("Dump SMBIOS Type4 ...")
    cmd_typ3 = 'dmidecode -t 4'
    res = ssh.execute_command(cmd_typ3)
    skt_info =  "Socket Designation: CPU0"
    cpu_mfg = "Manufacturer: Intel\(R\) Corporation"
    mx_speed =  "Max Speed: 4000 MHz"
    core_cnt = "Core Count: 4"
    thread_cnt = "Thread Count: 8"
    infos = [skt_info, cpu_mfg, mx_speed, core_cnt, thread_cnt]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True

def type7(ssh):
    tc = ('126', 'SMBIOS Type 7', 'Verify information of SMBIOS type7 is correct')
    result = Misc.LogHeaderResult(tc)

def type9(ssh):
    tc = ('127', 'SMBIOS Type 9', 'Verify information of SMBIOS type9 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    cmd = 'dmidecode -t 9'
    res = ssh.execute_command(cmd)
    info1 = "Designation: J48 - Slot 6"
    info2 = "Type: x8 PCI Express 3 x8"
    info3 = "Current Usage: Available"
    info4 = "Length: Long"
    info5 = "ID: 1"
    infos = [info1, info2, info3, info4, info5]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True


def type11(ssh):
    tc = ('128', 'SMBIOS Type 11', 'Verify information of SMBIOS type11 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    cmd = 'dmidecode -t 11'
    res = ssh.execute_command(cmd)
    info1 = "String 1: AliOS Linux/HDD/PxeV4"
    info2 = "String 2: Controller 1 Port 0 AF2MA31DTDLT240A"
    infos = [info1, info2]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True


def type13(ssh):
    tc = ('129', 'SMBIOS Type 13', 'Verify information of SMBIOS type13 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    cmd = 'dmidecode -t 13'
    res = ssh.execute_command(cmd)
    info1 = "Language Description Format: Long"
    info2 = "Installable Languages: 1"
    info3 = "en\|US\|iso8859-1"
    info4 = "Currently Installed Language: en\|US\|iso8859-1"
    infos = [info1, info2, info3, info4]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True


def type16(ssh):
    tc = ('130', 'SMBIOS Type 16', 'Verify information of SMBIOS type16 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    cmd = 'dmidecode -t 16'
    res = ssh.execute_command(cmd)
    info1 = "Location: System Board Or Motherboard"
    info2 = "Use: System Memory"
    info3 = "Error Correction Type: Single-bit ECC"
    info4 = "Maximum Capacity: 192 GB"
    info5 = "Number Of Devices: 3"
    infos = [info1, info2, info3, info4, info5]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True

def type17(ssh):
    tc = ('131', 'SMBIOS Type 17', 'Verify information of SMBIOS type17 is correct')
    result = Misc.LogHeaderResult(tc)

def type19(ssh):
    tc = ('132', 'SMBIOS Type 19', 'Verify information of SMBIOS type19 is correct')
    result = Misc.LogHeaderResult(tc)

def type20(ssh):
    tc = ('133', 'SMBIOS Type 20', 'Verify information of SMBIOS type20 is correct')
    result = Misc.LogHeaderResult(tc)

def type38(ssh):
    tc = ('134', 'SMBIOS Type 38', 'Verify information of SMBIOS type38 is correct')
    result = Misc.LogHeaderResult(tc)
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("SSH login fail")
        result.log_fail()
        return
    cmd = 'dmidecode -t 38'
    res = ssh.execute_command(cmd)
    interface = "Interface Type: KCS"
    spec_ver = "Specification Version: 2.0"
    slav_addr = "I2C Slave Address: 0x10"
    bas_addr = "Base Address: 0x0000000000000CA2 \(I/O\)"
    infos = [interface, spec_ver, slav_addr, bas_addr]
    if not verify_info(infos, res):
        result.log_fail()
        return
    result.log_pass()
    return True