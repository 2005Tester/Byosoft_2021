#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import time
import subprocess
import logging
import re
from Report import ReportGen
from Moc25 import SutConfig
from Moc25.SutConfig import Msg, Sut


CTRL_ALT_DELETE = '\33R\33r\33R'
ENTER = [chr(0x0D)]


def dump_acpi(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping acpi table...")
        return ssh.dump_info('acpidump', Moc25Config.LOG_DIR)

def dump_smbios(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping smbios table...")
        return ssh.dump_info('dmidecode', Moc25Config.LOG_DIR)


def lspci(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping pci info...")
        return ssh.dump_info('lspci -vv', Moc25Config.LOG_DIR, "lspci.log")


def dmesg(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping dmesg...")
        return ssh.dump_info('dmesg', Moc25Config.LOG_DIR)


def cpuinfo(ssh):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Dumping cpuinfo...")
        return ssh.dump_info('cat /proc/cpuinfo', Moc25Config.LOG_DIR)

# Check whether cpu core count is equal to "num" in OS
def verify_cpucore_count(ssh, num):
    if ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Checking cpu core count...")
        cpuinfo = ssh.execute_command('cat /proc/cpuinfo | grep "cpu cores" | uniq')
        logging.debug(cpuinfo)
        if re.search(str(num), cpuinfo):
            logging.info("Core count is correct")
            return True
        else:
            logging.info("Core count is not correct.")
            return


# Power cycle by IPMI command from serial port
def power_cycle_ipmi_serial(serial):
    logging.info("Sending CTRL+ALT+DEL to reboot SUT")
#    serial.send_data("ipmitool chassis bootdev disk\n")
    serial.send_data("ipmitool chassis power cycle\n")
    if not serial.is_msg_present_general("Chassis Power Control: Cycle", 10):
        logging.info("Power cycle Command fail.")
        return
    logging.info("Power cycle command successful.")
    return True


# Warm reset
def warm_reset(serial):
    logging.info("Sending CTRL+ALT+DEL to reboot SUT")
    serial.send_data(CTRL_ALT_DELETE)
    if serial.is_msg_present_general(Msg.BOOT_MSG, 60):
        logging.info("Reboot by CTRL+ALT+DEL successfully")
        return True
    logging.info("Try login os and reboot by command")
    if not reset_in_os(serial):
        logging.info("failed to reboot by command")
        return 
    return True   

def login_os(serial):
    serial.send_keys(ENTER*3)
    if serial.is_msg_present_general("localhost.localdomain", 10):
        logging.info("Logining successful")
        return True
    serial.send_data(Sut.OS_USER + "\n")  
    if not serial.is_msg_present_general("Password", 10):
        logging.info("Login fail, no password prompt")
        return
    serial.send_data(Sut.OS_PASSWORD + "\n")  
    if not serial.is_msg_present_general("localhost.localdomain", 10): 
        logging.info("Failed to login")
        return
    logging.info("Logining successful")
    return True


def continue_boot_and_login_os(serial):
    logging.info("Continue boot and login OS")
    if not serial.is_msg_present_general(Msg.OS_MSG, 180):
        return
    if not login_os(serial):
        return
    return True    

def reset_in_os(serial):
    serial.send_keys(ENTER*3)
    if not serial.is_msg_present_general("localhost login:", 15):
        serial.send_data("shutdown -r now\n")
        logging.info("Reboot command sent")
        if serial.is_msg_present_general(Msg.BOOT_MSG, 60):
            return True
    
    serial.send_data(Sut.OS_USER + "\n")  
    if not serial.is_msg_present_general("Password", 10):
        return

    serial.send_data(Sut.OS_PASSWORD + "\n")  
    if not serial.is_msg_present_general("localhost.localdomain", 10):  
        return

    serial.send_data("shutdown -r now\n")
    logging.info("Reboot command sent") 
    if not serial.is_msg_present_general(Msg.BOOT_MSG, 60):
        return
    
    logging.info("shutdown command sent successfully")
    return True


# Send IPMI command via SSH
def ipmi_command_ssh(ssh, cmds, rets):
    logging.info("Sending IPMI command...")
    if not ssh.login(Moc25Config.BMC_IP, Moc25Config.BMC_USER, Moc25Config.BMC_PASSWORD):
        return
    if not ssh.interaction(cmds, rets):
        logging.info("IPMI command execution fail")
        ssh.close_session()
        return
    ssh.close_session()
    logging.info("IPMI command executed successfully")
    return True


# Send IPMI command via BMC serial port
def ipmi_command_com(serial, cmd, ret):
    logging.info("Sending IPMI command from COM port...")
    serial.send_data(cmd)
    if not serial.is_msg_present_general(ret):
        return
    logging.info("IPMI command executed successfully")
    return True


# force power cycle by ipmi command 
def force_power_cycle_ipmi(ssh):
    logging.info("Force power cycle by ipmi command.")
    cmd = ['ipmitool chassis power cycle\n']
    ret = ['Chassis Power Control: Cycle']
    if not ipmi_command_ssh(ssh, cmd, ret):
        logging.info("Power cycle command failed.")
        return
    logging.info("Power cycle command sent.")
    return True
    
#Force power cycle is warm reset fails
def force_reset(serial, ssh=None):
    if warm_reset(serial):
        return True
    logging.info("Warmreset fail, force power cycle")
    try:
        if force_power_cycle_ipmi(ssh):
            return True
    except AttributeError:
        logging.info("Attribute Error.")
        return
    logging.info("Force reset fail.")
    return
        
# Precondition: In OS and logged in
def read_msr(serial, msr):
    logging.info("Reading MSR: {}".format(msr))
    res = serial.run_command("rdmsr -c -0 {0} \n".format(msr))
    reg_value = re.findall(r"0x\w{16}", res)[0]
    if re.search("command not found", res):
        logging.error("Command not found, please install rdmsr tool")
        return
    else:
        logging.info("Value of MSR {0}: {1}".format(msr, reg_value))
        return reg_value
