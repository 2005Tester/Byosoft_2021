# -*- encoding=utf8 -*-
import paramiko
import time
import re


def send_command(command, op):
    op.send(command)
    time.sleep(5)
    ret = op.recv(1024)
    return ret


