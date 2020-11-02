# -*- encoding=utf8 -*-
import json
import re
import sys

from HY5.Hy5Config import *


class SerialUnitool(object):
    def __init__(self, ser, usr=OS_USER, pw=OS_PASSWORD, path="/root/unitool", flag="Ubuntu 20.04 LTS"):
        self.serial = ser
        self.user = usr
        self.pw = pw
        self.unitool_path = path
        self.os_flag = flag
        self.cfg_file = os.path.join(os.path.dirname(sys.argv[0]), "BiosSetting.json")

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

    def is_login(self, user="root", pw="root"):
        try:
            if self.send_cmds([user + "\n", pw + "\n", "pwd\n"], ["", "", "/root"])[0][1]:
                return True
        except Exception as e:
            print(e)
            print("Error: Not Boot to OS or Username/Password Wrong !")

    def write(self, **kwargs):
        result = True
        if self.is_login(self.user, self.pw):
            self.send_cmds(["cd {}\n".format(self.unitool_path), "insmod ufudev.ko\n"])
            for key, value in kwargs.items():
                try:
                    if self.send_cmds(["./unitool -w {}:{}\n".format(key, value)], ["success!"])[0][1]:
                        print("Set {}:{} success!".format(key, value))
                        result = result & True
                    else:
                        print("Set {}:{} error!".format(key, value))
                        result = result & False
                except:
                    result = False
            return result

    def read(self, *args):
        result = {}
        if self.is_login(self.user, self.pw):
            a = self.send_cmds(["cd {}\n".format(self.unitool_path), "insmod ufudev.ko\n"])
            for key in args:
                rd_cmd = "./unitool -r {}\n".format(key)
                send_read = self.send_cmds([rd_cmd], ["success!"])[0]
                if send_read[1]:
                    try:
                        read_value = re.findall(r"GetVariable value:([0-9a-zA-Z]*)", send_read[2])[0]
                        print("Read {}:{} success!".format(key, read_value))
                        result[key] = read_value
                    except:
                        result[key] = None
                        pass
                else:
                    print("Read {} error!".format(key))
                    result[key] = None
        return result

    def check(self, **kwargs):
        result = True
        for key, value in kwargs.items():
            get_data = self.read(key)[key]
            if str(get_data) == str(value):
                # print("Check {}: {} success!".format(key, value))
                result = result & True
            else:
                # print("Check {}: {} failed!".format(key, value))
                result = result & False
        return result

    def set_config(self, config):
        with open(self.cfg_file, "r") as js:
            cfg = json.load(js)
        if self.check(**cfg[config]):
            print("Check {} config pass!".format(config))
            return True
        else:
            print("Set {} config...".format(config))
            result = self.write(**cfg[config])
            if result:
                print("Reboot to Save BIOS Setting!")
                self.send_cmds(["reboot\n"])
                if self.serial.is_msg_present(self.os_flag):
                    print("Boot to OS successfully!")
                    return True
