# -*- encoding=utf8 -*-
import paramiko
import time
import re


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

