import logging
import os
from Pangea import SutConfig
from Common.LogAnalyzer import LogAnalyzer


# Run one command from ssh (e.g. dmidecode) return the result, no \n reqired for command
def execute_command(ssh, command):
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.execute_command(command)
    else:
        logging.info("SshLib: login failed.")
        return

# Run several commands through ssh in a row, and check return of all the commnads
# commands: list of commands, need to add \n for each command
# rets: return value of each command defined in above parameter
def interaction(ssh, commands, rets):
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.interaction(commands, rets)
    else:
        logging.info("SshLib: login failed.")
        return


# Run one command from ssh (e.g. dmidecode) output result to a log file
def dump_info(ssh, command, log_name=None):
    if ssh.login(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD):
        log_dir = SutConfig.LOG_DIR
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


