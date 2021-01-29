import re
import logging
import os
from Pangea import SutConfig
from Common.LogAnalyzer import LogAnalyzer


# Run one command from ssh (e.g. dmidecode) return the result, no \n reqired for command
def execute_command(ssh, command):
    if ssh.login():
        return ssh.execute_command(command)
    else:
        logging.info("SshLib: login failed.")
        return


# Run several commands through ssh in a row, and check return of all the commnads
# commands: list of commands, need to add \n for each command
# rets: return value of each command defined in above parameter
def interaction(ssh, commands, rets):
    if ssh.login():
        return ssh.interaction(commands, rets)
    else:
        logging.info("SshLib: login failed.")
        return


# Run one command from ssh (e.g. dmidecode) output result to a log file
def dump_info(ssh, command, log_name=None):
    if ssh.login():
        log_dir = SutConfig.LOG_DIR
        return ssh.dump_info(command, log_dir, log_name)


# Check difference of a test log (obtaind from ssh) with a standard log
def check_diff(ssh, command, lkg):
    if not os.path.exists(lkg):
        logging.info("Log: {0} for comparision not found".format(lkg))
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


# sftp put by using SCPClient
def sftp_put_via_scp(ssh, src, dst, timeout):
    if not ssh.login():
        logging.error("SSH login failed")
        return
    return ssh.sftp_put_via_scp(src, dst, timeout)


# sftp put by using SCPClient
def sftp_get_via_scp(ssh, src, dst, timeout):
    if not ssh.login():
        logging.error("SSH login failed")
        return
    return ssh.sftp_get_via_scp(src, dst, timeout)