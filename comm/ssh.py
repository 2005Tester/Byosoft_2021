# -*- encoding=utf8 -*-
import paramiko
import time
import re


def send_command(command, op):
    op.send(command)
    time.sleep(5)
    ret = op.recv(1024)
    return ret


def call_commands(cmds, strs, op, s):
    for i in range(0, len(cmds)):
        res = ssh.send_command(cmd[i], op)  # confirm shutdown
        if not re.search(strs[i], res.decode('utf-8')):
            op.close()
            s.close()
            print('%s failed to execute.' % cmd[i])
            return False
        print('%s executed successfully.' % cmd[i])
    op.close()
    s.close()
    return True

