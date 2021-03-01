# -*- encoding=utf8 -*-
import re
import time
import subprocess
from Common.ssh import SshConnection


class SerialUnitool(object):
    """
    通过串口重定向的方式Boot到OS
    需要事先修改Linux Grub参数 "console=tty0 console=ttyS0,115200n8"
    使用unitool工具修改BIOS选项
    """

    def __init__(self, ser, os_usr, os_pw, uni_path, os_flag):
        self.serial = ser
        self.user = os_usr
        self.pw = os_pw
        self.upath = uni_path
        self.flag = os_flag

    def send_cmds(self, cmds, feedback=None):
        result = True
        res = []
        for index, cmd in enumerate(cmds):
            self.serial.session.flushOutput()
            self.serial.session.flushInput()
            self.serial.send_data(cmd)
            output_lines = [r.decode() for r in self.serial.session.readlines()]
            output_str = "".join(output_lines)

            try:
                if feedback and (feedback[index] in output_str):
                    result = result & True
                else:
                    result = result & False
            except:
                result = False
                pass
            res.append((cmd, result, output_str))
        return res

    def is_login(self):
        try:
            if self.send_cmds([self.user + "\n", self.pw + "\n", "pwd\n"], ["", "", "/root"])[0][1]:
                return True
        except Exception as e:
            print(e)
            print("Error: Not Boot to OS or Username/Password Wrong !")

    # 一个或多个BIOS {变量名：变量值}
    def write(self, **kwargs):
        result = True
        if self.is_login():
            self.send_cmds(["cd {}\n".format(self.upath), "insmod ufudev.ko\n"])
            for key, value in kwargs.items():
                try:
                    if self.send_cmds(["./unitool -w {}:{}\n".format(key, value)], ["success!"])[0][1]:
                        print("Set {} = {}".format(key, value))
                        result = result & True
                    else:
                        print("Set {} = {} fail".format(key, value))
                        result = result & False
                except:
                    result = False
            return result

    # 一个或多个BIOS 变量名
    def read(self, *args):
        result = {}
        if self.is_login():
            self.send_cmds(["cd {}\n".format(self.upath), "insmod ufudev.ko\n"])
            for key in args:
                rd_cmd = "./unitool -r {}\n".format(key)
                send_read = self.send_cmds([rd_cmd], ["success!"])[0]
                if send_read[1]:
                    try:
                        read_value = re.findall(r"GetVariable value:([0-9a-zA-Z]*)", send_read[2])[0]
                        print("Read {}={}".format(key, read_value))
                        result[key] = read_value
                    except:
                        result[key] = None
                        pass
                else:
                    print("Read {} fail".format(key))
                    result[key] = None
        return result

    # 一个或多个BIOS {变量名：变量值}
    def check(self, **kwargs):
        result = True
        for key, value in kwargs.items():
            get_data = self.read(key).get(key)
            if str(get_data) == str(value):
                # print("Check {}: {} pass!".format(key, value))
                result = result & True
            else:
                # print("Check {}: {} fail!".format(key, value))
                result = result & False
        return result

    # 先检查选项是否符合，不符合则修改选项，注意：重启后设置才能生效
    def set_config(self, cfg_dict):
        if self.check(**cfg_dict):
            return "check_pass"
        if self.write(**cfg_dict):
            return "set_pass"


class SshUnitool(SshConnection):
    """
    通过系统ssh网络连接的方式
    使用unitool修改BIOS选项
    """

    def __init__(self, os_ip, os_usr, os_pw, uni_path):
        self.ip = os_ip
        self.user = os_usr
        self.pw = os_pw
        self.upath = uni_path
        self.shell = None
        super(SshUnitool, self).__init__(self.ip, self.user, self.pw)

    def sut_online(self):
        ping_try = subprocess.Popen(("ping -n 3 -w 10 {}".format(self.ip)), stdout=subprocess.PIPE)
        result = ping_try.stdout.read().decode("gbk")
        if "TTL=" in result:
            return True

    def open_shell(self):
        if not self.sut_online():
            print("SUT {} is offline, please check os network".format(self.ip))
            return False
        if self.login():
            self.shell = self.ssh_client.invoke_shell()
            return True

    def close_shell(self):
        self.ssh_client.close()

    def recv_data(self, buffer=1024, timeout=10):
        all_data = []
        start_time = time.time()
        while not self.shell.recv_ready():
            if time.time() - start_time > timeout:
                print("ssh receive data timeout")
                break
            time.sleep(0.5)
        while self.shell.recv_ready():
            all_data.append(self.shell.recv(buffer).decode("utf-8"))
            time.sleep(0.01)
            if time.time() - start_time > timeout:
                print("ssh receive data timeout")
                break
        return "".join(all_data)

    def exec_cmds(self, cmd_list, feedback=None, timeout=10):
        result = True
        retn = []
        for index, cmd in enumerate(cmd_list):
            self.shell.sendall(cmd)
            time.sleep(0.2)
            data = self.recv_data(buffer=10240, timeout=timeout)
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

    def env_set(self):
        self.exec_cmds(["cd {}\n".format(self.upath), "insmod ufudev.ko\n"])

    # 传入参数一个或多个，格式为 { "AttributeName1"：Value1, "AttributeName2"：Value2 }
    def write(self, **kwargs):
        if not self.open_shell():
            print("OS shell can't be opened")
            return
        self.env_set()
        result = True
        for key, value in kwargs.items():
            send_write = self.exec_cmds(["./unitool -w {}:{}\n".format(key, value)], ["success!"])
            if send_write:
                try:
                    if not send_write[0][1]:
                        print("-- [Set] {}={} fail".format(key, value))
                        result = result & False
                        continue
                    print("-- [Set] {}={}".format(key, value))
                    result = result & True
                except:
                    result = False
        return result

    #  传入参数一个或多个，格式为 ["AttributeName1", "AttributeName2"]，返回读到值的字典
    def read(self, *args):
        result = {}
        if not self.open_shell():
            print("OS shell can't be opened")
            return
        self.env_set()
        for key in args:
            send_read = self.exec_cmds(["./unitool -r {}\n".format(key)])
            if send_read:
                try:
                    read_val = re.findall(r"GetVariable value:([0-9a-zA-Z]*)", send_read[0][2])
                    read_value = read_val[0] if read_val else None
                    print("-- [Read] {}={}".format(key, read_value))
                    result[key] = read_value
                except:
                    result[key] = None
                    pass
            else:
                print("-- [Read] {} fail".format(key))
                result[key] = None
        return result

    # 检查选项是否为期望值，格式为字典，符合预期返回True，不符合预期返回False
    def check(self, **kwargs):
        result = True
        for key, value in kwargs.items():
            get_data = self.read(key)[key]
            result = (result & True) if (str(get_data) == str(value)) else (result & False)
        result_flag = "Pass" if result else "Fail"
        print('-- [Check] Config {}！'.format(result_flag))
        return result

    # 先检查选项是否符合，不符合则修改选项，注意：重启后设置才能生效
    def set_config(self, cfg_dict):
        if self.check(**cfg_dict):
            self.close_shell()
            return "check_pass"
        if self.write(**cfg_dict):
            self.close_shell()
            return "set_pass"
