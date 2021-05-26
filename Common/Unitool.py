# -*- encoding=utf8 -*-
import re
import logging
import time
import subprocess
from Common.ssh import SshConnection


def cprint(str_msg, log=False):
    if log:
        logging.info(str_msg)
    else:
        print(str_msg)


class SshUnitool(SshConnection):
    """
    通过系统ssh网络连接的方式使用unitool修改/读取/检查BIOS选项
    修改完配置后需要重启机器才能生效
    默认参数：
        os_ip:      ssh ip地址
        os_user:    ssh 登录用户名
        os_pw:      ssh 登录密码
        uni_path:   unitool放在OS下的路径，需要将unitool文件和 ufudev.ko放在同一个文件夹
        log_debug:  False: print的方式打印关键信息
                    True： logging的方式打印关键信息
    """

    def __init__(self, os_ip, os_usr, os_pw, uni_path, loginfo=False):
        self.ip = os_ip
        self.user = os_usr
        self.pw = os_pw
        self.upath = uni_path
        self.shell = None
        self.ins_driver = False
        self.loginfo = loginfo
        super(SshUnitool, self).__init__(self.ip, self.user, self.pw)

    def sut_online(self):
        ping_try = subprocess.Popen(("ping {}".format(self.ip)), stdout=subprocess.PIPE)
        result = ping_try.stdout.read().decode("gbk")
        if "TTL=" in result:
            return True

    def link_active(self):
        trans_open = self.ssh_client.get_transport() if self.ssh_client else None
        link_status = trans_open and trans_open.is_active()
        if not link_status:
            self.ins_driver = False
        return link_status

    def open_shell(self):
        if not self.sut_online():
            cprint("SUT {} is offline, please check os network".format(self.ip), self.loginfo)
            return False
        if self.link_active():  # 避免重复登录
            # self.shell = self.ssh_client.invoke_shell()
            return True
        if self.login():
            self.shell = self.ssh_client.invoke_shell()
            self.ins_driver = False
            return True

    def close_shell(self):
        self.ins_driver = False
        self.shell.close()
        self.ssh_client.close()

    def install_driver(self):
        if not self.ins_driver:
            self.exec_cmds([f"cd {self.upath}\n", "insmod ufudev.ko\n"])
            self.ins_driver = True

    def recv_data(self, buffer=1024, timeout=10):
        all_data = []
        start_time = time.time()
        while not self.shell.recv_ready():
            if time.time() - start_time > timeout:
                cprint("ssh receive data timeout", self.loginfo)
                break
            time.sleep(0.1)
        while self.shell.recv_ready():
            all_data.append(self.shell.recv(buffer).decode("utf-8"))
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                cprint("ssh receive data timeout", self.loginfo)
                break
        return "".join(all_data)

    def exec_cmds(self, cmd_list, feedback=None, timeout=10):
        result = True
        retn = []
        cmd_list = [cmd_list] if isinstance(cmd_list, str) else cmd_list
        for index, cmd in enumerate(cmd_list):
            if not cmd.endswith("\n"):  # except handle
                cmd = f"{cmd}\n"
            self.shell.sendall(cmd)
            time.sleep(0.5)
            data = self.recv_data(buffer=1024, timeout=timeout)
            try:
                if feedback and (feedback[index] in data):
                    result = result & True
                else:
                    result = result & False
            except:
                result = False
                pass
            retn.append((cmd, result, data))
        return retn

    # 传入参数示例: **{"AttributeName1"：Value1, "AttributeName2"：Value2} 或者 AttributeName1=Value1,AttributeName2=Value2
    # 返回设置值的状态: 全部都设置成功返回True; 任意一个设置失败返回False
    def write(self, **kwargs):
        if not self.open_shell():
            cprint("OS shell can't be opened", self.loginfo)
            return
        self.install_driver()
        fail_cnt = 0
        for key, value in kwargs.items():
            send_write = self.exec_cmds(["./unitool -w {}:{}\n".format(key, value)], ["success!"])
            if send_write:
                try:
                    if not send_write[0][1]:
                        cprint("-- [Set] {}={} fail".format(key, value), self.loginfo)
                        fail_cnt += 1
                        continue
                    cprint("-- [Set] {}={}".format(key, value), self.loginfo)
                except:
                    fail_cnt += 1
        self.close_shell()
        return fail_cnt == 0

    # 传入参数示例: *["AttributeName1", "AttributeName2"] 或者 "AttributeName1", "AttributeName2"
    # 返回当前值的字典: {"AttributeName1"：Value1, "AttributeName2"：Value2}
    def read(self, *args):
        result = {}
        if not self.open_shell():
            cprint("OS shell can't be opened", self.loginfo)
            return
        self.install_driver()
        for key in args:
            send_read = self.exec_cmds(["./unitool -r {}\n".format(key)])
            if send_read:
                try:
                    read_val = re.findall(r"GetVariable value:([0-9a-zA-Z]*)", send_read[0][2])
                    read_value = read_val[0] if read_val else None
                    cprint("-- [Read] {}={}".format(key, read_value), self.loginfo)
                    result[key] = read_value
                except:
                    result[key] = None
                    pass
            else:
                cprint("-- [Read] {} fail".format(key), self.loginfo)
                result[key] = None
        self.close_shell()
        return result

    # 传入参数示例: **{"AttributeName1"：Value1, "AttributeName2"：Value2} 或者 AttributeName1=Value1,AttributeName2=Value2
    # 读到的值符合预期: 全部符合预期返回True; 任意一个不符合预期: 返回False
    def check(self, **kwargs):
        fail_cnt = 0
        for key, value in kwargs.items():
            get_data = self.read(key)[key]
            fail_cnt = fail_cnt+1 if (str(get_data) != str(value)) else fail_cnt
        result_flag = "Match" if fail_cnt else "Mismatch"
        cprint('-- [Check] Config {}'.format(result_flag), self.loginfo)
        self.close_shell()
        return fail_cnt == 0

    # 先检查选项是否符合，不符合则修改选项，注意：重启后设置才能生效
    def set_config(self, cfg_dict):
        if self.check(**cfg_dict):
            return "check_pass"
        if self.write(**cfg_dict):
            return "set_pass"
