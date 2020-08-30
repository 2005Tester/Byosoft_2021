# -*- encoding=utf8 -*-
import paramiko
import time
import re
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
import sys
import os

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
        time.sleep(2)
        ret = op.recv(1024)
        return ret

    def interaction(self, cmds, strs):
        op = self.ssh_client.invoke_shell()
        for i in range(0, len(cmds)):
            res = self.execute_command_interaction(cmds[i], op)
            print('Sending command: %s' % cmds[i])
            #print(res.decode('utf-8'))
            """    
            if not re.search(strs[i], res.decode('utf-8')):
                print('Command: %s failed to execute.' % cmds[i])
                return
        return True
            """
            start_time = time.time()
            while not re.search(strs[i], res.decode('utf-8')):
                print("Checking Status...")
                res = op.recv(1024)
                print(res.decode('utf-8'))
                now = time.time()
                if re.search(strs[i], res.decode('utf-8')):
                    print("Command %s executed successfully" %(cmds[i]))
                    status = True
                if (now - start_time) > 600:
                    print("Run command %s timeout." %(cmds[i]))
                    status = False
                    break
        op.close()
        status = True
        return status

    def is_command_success(self, cmd, expected_result):
        op = self.ssh_client.invoke_shell()
        start_time = time.time()
        print("Sending command: %s" % cmd)
        #res = self.execute_command_interaction(cmd, op)
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

