# -*- encoding=utf8 -*-
import re
import logging
import os
import time
from batf.Common.LogAnalyzer import LogAnalyzer
import paramiko
from Inspur7500.Config import SutConfig


# Run one command from ssh (e.g. dmidecode) return the result, no \n reqired for command
def execute_command(ssh, command, decoding='', delay=600):
    if ssh.login():
        logging.info("Sending: {0}".format(command))
        stdin, stdout, stderr = ssh.ssh_client.exec_command(command, timeout=delay)
        if decoding:
            res = stdout.read().decode(decoding)
            err = stderr.read().decode(decoding)
        else:
            res = stdout.read().decode()
            err = stderr.read().decode()
        ssh.close_session()
        return res, err
    else:
        logging.info("SshLib: login failed.")
        return


def execute_command_limit(ssh, command, delay=290, decoding=''):
    start_time = time.time()
    while True:
        try:
            cmd_result = execute_command(ssh, command, decoding, delay=delay)
        except:
            logging.info(f"{delay} didn't find result")
            cmd_result = ''
        end_time = time.time()
        spent_time = end_time - start_time
        if cmd_result:
            break
        if spent_time > delay:
            break
    logging.debug(cmd_result)
    return cmd_result


def invoke_shell(ssh, command, timeout=5):
    if ssh.login():
        logging.info("Sending: {0}".format(command))
        op = ssh.ssh_client.invoke_shell(width=160, height=80)
        if not re.search('\n', command):
            command = command + '\n'
        op.sendall(command)
        time.sleep(timeout)
        return op.recv(1024)
    else:
        logging.info("SshLib: login failed.")
        return


def execute_command_interaction(ssh, command):
    if ssh.login():
        return ssh.execute_command_interaction(command)
    else:
        logging.info("SshLib: login failed.")
        return


# Run several commands through ssh in a row, and check return of all the commands
# commands: list of commands, need to add \n for each command
# rets: return value of each command defined in above parameter
def interaction(ssh, commands, rets, timeout=300):
    if ssh.login():
        return ssh.interaction(commands, rets, timeout)
    else:
        logging.info("SshLib: login failed.")
        return


# Run one command from ssh (e.g. dmidecode) output result to a log file
def dump_info(ssh, command, log_dir, log_name=None):
    if ssh.login():
        return ssh.dump_info(command, log_dir, log_name)


# Check difference of a test log (obtaind from ssh) with a standard log
def check_diff(ssh, command, lkg):
    if not os.path.exists(lkg):
        logging.info("Last known good log for comparision doesn't exist")
        return
    logging.info("Dumping log for: {0}".format(command))
    current_log = dump_info(ssh, command)
    diffs = LogAnalyzer.check_diff(lkg, current_log)
    if diffs:
        for diff in diffs:
            logging.info(diff)
        return
    logging.info("No diffs found between curren and last known good logs")
    return True


# Check whether spefified infomation exists in the result of a command in os, e.g. lspci, dmidecode
def verify_info(ssh, command, infos):
    res = execute_command(ssh, command)
    failures = 0
    for info in infos:
        if not re.search(info, res):
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


# remove a file from sftp, file name matches file_re
# if dir is not specified, use root directory
def sftp_remove_file(sftp, file_re, dir='.'):
    if sftp.login():
        sftp.remove_file(file_re, dir)
        sftp.close_session()
        return True
    else:
        logging.info("SFTP login fail.")


# upload a file to sftp,ret_msg is used to verify result, can use file size
def sftp_upload_file(sftp, src_file, dst_file, ret_msg=''):
    if sftp.login():
        logging.info("Uploading: {0}".format(src_file))
        result = sftp.upload_file(src_file, dst_file, ret_msg)
        sftp.close_session()
        if result == 1:
            return True
        else:
            return
    else:
        logging.info("SFTP login fail.")


# download a file from sftp to local, ret_msg is used to verify result, can use file size
def sftp_download_file(sftp, src_file, dst_file):
    if sftp.login():
        logging.info("Downloading: {0}".format(src_file))
        return sftp.download_file(src_file, dst_file)
    else:
        logging.info("SFTP login fail.")


# list files and directories from a sftp directory
def sftp_lsdir(sftp, dir='.'):
    if sftp.login():
        logging.info("Fetching directory info...")
        lsdir = sftp.ls_dir(dir)
        sftp.close_session()
        return lsdir
    else:
        logging.info("SFTP login fail.")


def reboot(command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(SutConfig.Env.OS_IP, port=22, username=SutConfig.Env.OS_USER, password=SutConfig.Env.OS_PASSWORD)
    ssh_client.exec_command(command)
    ssh_client.close()
