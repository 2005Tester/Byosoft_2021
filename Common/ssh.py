# -*- encoding=utf8 -*-
import paramiko
import logging
import time
import re
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
import sys
import os


class sftp():
    def __init__(self, host_ip, username, password):
        self.host_ip = host_ip
        self.username = username
        self.password = password

    def login(self):
        try:
            self.transport = paramiko.Transport(self.host_ip, 22)
            self.transport.banner_timeout = 120
            self.transport.connect(username = self.username, password = self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except:
            logging.error("sftp_login: {0}".format(e))

    def ls_dir(self):
        return self.sftp.listdir()


class SshConnection():
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()
 
    def login(self, host_ip, username, password):
        try:
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(host_ip, port=22, username=username, password=password)
        except AuthenticationException:
            print('Incorrect Username or Password.')
            return
        except NoValidConnectionsError:
            print('Connection timeout...')
            return
        except:
            print("Unexpected Error:", sys.exc_info()[0])
            return
        return True
    
    def execute_command(self, command, log_dir):
        log = os.path.join(log_dir, ''.join((command, '.log')))
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        res = stdout.read().decode()
        print(res)
        with open(log, 'w') as f:
            f.write(res)

    def execute_command_interaction(self, cmd, op):
        op.send(cmd)
        time.sleep(4)
        ret = op.recv(1024)
        return ret

    def interaction(self, cmds, strs):
        op = self.ssh_client.invoke_shell()
        for i in range(0, len(cmds)):
            res = self.execute_command_interaction(cmds[i], op)
            logging.info('Sending command: {0}'.format(cmds[i]))
            # print(res.decode('utf-8'))
            start_time = time.time()
            while not re.search(strs[i], res.decode('utf-8')):
                logging.info("Checking Status...")
                res = op.recv(1024)
                # print(res.decode('utf-8'))
                logging.info(res.decode('utf-8'))
                now = time.time()
                if re.search(strs[i], res.decode('utf-8')):
                    print("Any chnace to reach here ?")
                    break
                if (now - start_time) > 600:
                    logging.error("Run command {0} timeout.".format(cmds[i]))
                    return
        op.close()
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
        return status

    def close_session(self):
        self.ssh_client.close()


def send_command(command, op):
    op.send(command)
    time.sleep(5)
    ret = op.recv(1024)
    return ret


def call_commands(cmds, strs, op):
    for i in range(0, len(cmds)):
        res = send_command(cmds[i], op)  # confirm shutdown
        if not re.search(strs[i], res.decode('utf-8')):
            print('Command: %s failed to execute.' % cmds[i])
            return False
        print('Sending command: %s' % cmds[i])
    return True

