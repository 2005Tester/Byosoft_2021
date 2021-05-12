import re
import logging
import os
import time
from Common.LogAnalyzer import LogAnalyzer


# Run one command from ssh (e.g. dmidecode) return the result, no \n reqired for command
def execute_command(ssh, command):
    if ssh.login():
        return ssh.execute_command(command)
    else:
        logging.info("SshLib: login failed.")
        return


# Run several commands through ssh in a row, and check return of all the commands
# commands: list of commands, need to add \n for each command
# rets: return value of each command defined in above parameter
def interaction(ssh, commands, rets):
    if ssh.login():
        return ssh.interaction(commands, rets)
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
def sftp_upload_file(sftp, src_file, dst_file, ret_msg=None):
    if sftp.login():
        logging.info("Uploading: {0}".format(src_file))
        sftp.upload_file(src_file, dst_file, ret_msg)
        sftp.close_session()
        return True
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


def interaction_time_limit(ssh, cmd_list, rtn_list="", timeout=180, buffer=1024, echo=False):
    """
    SSH interaction run cmd list and check feedback
    :param ssh:         ssh instance
    :param cmd_list:    one or more cmd list
    :param rtn_list:    one or more expected string
    :param timeout:     cmd timeout
    :param echo:        show each cmd run result if True
    :param buffer:      receive buffer
    :return: True:      rtn_list match cmd_list
             False:     rtn_list mis-match cmd_list
             None:      rtn_list is not provided
    """
    cmd_list = list(cmd_list)
    rtn_list = list(rtn_list)
    if ssh.login():
        status = True
        shell = ssh.ssh_client.invoke_shell()
        for index, cmd in enumerate(cmd_list):
            retry = False
            logging.info('Sending: {0}'.format(cmd.strip("\n")))
            shell.send(cmd)
            time.sleep(4)
            res = shell.recv(1024)
            if not rtn_list:
                status = None
                continue
            start_time = time.time()
            while not (rtn_list[index] in res.decode('utf-8')):
                if shell.recv_ready():
                    res = shell.recv(buffer)
                if echo:
                    print(res.decode('utf-8'))
                if (time.time() - start_time) > timeout and (not retry):   # retry once if feedback timeout
                    shell.send(cmd)
                    time.sleep(4)
                    res = shell.recv(buffer)
                    retry = True
                    continue
                if (time.time() - start_time) > timeout*2 and retry:
                    status = False
                    logging.error("Run command {0} [timeout]".format(cmd.strip("\n")))
                    return status
            logging.info("Run command [successful]")
        shell.close()
        ssh.close_session()
        return status
