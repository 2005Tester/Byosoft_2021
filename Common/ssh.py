#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import paramiko
import logging
import time
import re
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
import sys
import os
from scp import SCPClient
import scp


class sftp:
    def __init__(self, host_ip, username, password):
        self.host_ip = host_ip
        self.username = username
        self.password = password

    def login(self):
        logging.debug("Try sftp login.")
        try:
            self.transport = paramiko.Transport(self.host_ip, 22)
            self.transport.banner_timeout = 120
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except:
            logging.error("sftp_login: {0}".format(e))
            return
        logging.info("SFTP login successfully")
        return True

    def ls_dir(self, dir='.'):
        return self.sftp.listdir(dir)

    # remove file which matches file_re
    def remove_file(self, file_re, dir='.'):
        files = self.ls_dir(dir)
        for file in files:
            if re.search(file_re, file):
                logging.info("Removing: {0}".format(file))
                self.sftp.remove(file)

    # upload a file to sftp,ret_msg is used to verify result, can use file size 
    def upload_file(self, src_file, dst_file, ret_msg=None):
        status = 0
        try:
            logging.info("Uploading file to sftp")
            res = self.sftp.put(src_file, dst_file)
        except OSError:
            logging.error("Skip due to SSH connection error.")
            return
        if re.search(ret_msg, str(res)):
            logging.info("File uploaded to SFTP successfully.")
            status = 1
        else:
            logging.info("Failed to upload file to SFTP.")
            logging.info(res)
        self.close_session()
        return status

    def close_session(self):
        self.sftp.close()
        self.transport.close()


class SshConnection:
    def __init__(self, host_ip, usernmae, password):
        self.host_ip = host_ip
        self.username = usernmae
        self.password = password
        self.ssh_client = paramiko.SSHClient()

    def login(self):
        logging.debug("SSH login: {0}".format(self.host_ip))
        try:
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.host_ip, port=22, username=self.username, password=self.password)
        except AuthenticationException:
            logging.error('Error in ssh connection: Incorrect Username or Password.')
            return
        except NoValidConnectionsError:
            logging.error('Error: NoValidConnectionsError, retry after 60 seconds.')
            time.sleep(60)
            self.login()
        except TimeoutError:
            logging.info("Timeout..., retry aftre 15 seconds.")
            time.sleep(60)
            self.login()
        except ConnectionAbortedError:
            logging.info('ConnectionAbortedError, retry after 60 seconds.')
            time.sleep(60)
            self.login()
        except:
            logging.error("Error in ssh connection:", sys.exc_info()[0])
            return
        return True

    # execute command on SUT
    def execute_command(self, command):
        logging.debug("Sending: {0}".format(command))
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        res = stdout.read().decode()
        return res

    # dumm information to a log file
    def dump_info(self, command, log_dir, log_name=None):
        if log_name:
            file_name = log_name.replace(' ','_').replace('-','').replace('\\','_') +'.txt'
        else:
            file_name = command.replace(' ','_').replace('-','').replace('\\','_') + '.txt'
        log = os.path.join(log_dir, file_name)
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        res = stdout.read().decode()
        with open(log, 'w') as f:
            f.write(res)
        return log

    def execute_command_interaction(self, cmd):
        op = self.ssh_client.invoke_shell()
        op.send(cmd)
        time.sleep(4)
        ret = op.recv(1024)
        op.close()
        self.ssh_client.close()
        return ret

    # send commands one by one through ssh in interactive mode    
    def interaction(self, cmds, strs):
        op = self.ssh_client.invoke_shell()
        for i in range(0, len(cmds)):
            logging.debug('Sending: {0}'.format(cmds[i].strip("\n")))
            op.send(cmds[i])
            time.sleep(4)
            res = op.recv(1024)
            start_time = time.time()
            while not re.search(strs[i], res.decode('utf-8')):
                if op.recv_ready():
                    logging.info("Checking command status...")
                    res = op.recv(1024)
                    logging.info(res.decode('utf-8'))
                now = time.time()
                if re.search(strs[i], res.decode('utf-8')):
                    # Will reach here if command returns result after a while
                    break
                if (now - start_time) > 300:
                    logging.error("Run command: {0} timeout.".format(cmds[i].strip("\n")))
                    return
        #    logging.info('Command successful.')
        op.close()
        self.ssh_client.close()
        status = True
        return status

    def is_command_success(self, cmd, expected_result):
        op = self.ssh_client.invoke_shell()
        start_time = time.time()
        print("Sending command: %s" % cmd)
        # res = self.execute_command_interaction(cmd, op)
        op.send(cmd)
        time.sleep(5)
        res = op.recv(1024)
        print(res.decode('utf-8'))
        while not re.search(expected_result, res.decode('utf-8')):
            print("Checking Status...")
            res = op.recv(1024)
            print(res.decode('utf-8'))
            now = time.time()
            print(now)
            if re.search(expected_result, res.decode('utf-8')):
                print("Command %s executed successfully" %(cmd))
                status = True
            if (now - start_time) > 360:
                print("Run command %s timeout." %(cmd))
                status = False
                break
        op.close()
        self.ssh_client.close()
        return status

    # On some platform paramiko sftp not work, use SCPClien
    def sftp_put_via_scp(self, src, dst, timeout):
        scpclient = SCPClient(self.ssh_client.get_transport(), socket_timeout=timeout)
        try:
            scpclient.put(src, dst)
        except FileNotFoundError as e:
            logging.info("Error in uploading file: {0}".format(e))
            scpclient.close()
            return
        scpclient.close()
        return True

    def sftp_get_via_scp(self, src, dst, timeout):
        scpclient = SCPClient(self.ssh_client.get_transport(), socket_timeout=timeout)
        try:
            scpclient.get(src, dst)
        except scp.SCPException as e:
            logging.info("Error in downloading file: {0}".format(e))
            scpclient.close()
            return
        scpclient.close()
        return True

    def close_session(self):
        self.ssh_client.close()
