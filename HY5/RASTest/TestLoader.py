# -*- encoding=utf8 -*-

import os
import sys
import threading
import time

import serial.tools.list_ports as list_ports

# Non cscript function import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))))
import Common.ssh as ssh
import Common.SutSerial as Serial
from HY5.Hy5TcLib import bmc_dump, force_power_cycle
from HY5.Hy5Config import *
import HY5.RASTest.Unitool as Unitool


def detect_serial_ports():
    port_list = list(list_ports.comports())
    if len(port_list) == 1:
        return list(port_list[0])[0]
    elif len(port_list) <= 0:
        print("No serial port found!")
    else:
        port_number = 0
        for port in port_list:
            print(port, port_number)
            port_number += 1
        p = int(input("Please choose serial port: "))
        return list(port_list[p])[0]


def load_scripts(file_name="Testcase"):
    dir = os.path.dirname(sys.argv[0])
    tc_list = [i for i in os.listdir(dir) if file_name in i]
    for t in tc_list:
        with open(os.path.join(dir, t), "rb") as f:
            exec(f.read(), globals())


def run(func_tc_name):
    now = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
    config, tc_name = func_tc_name.split(".")
    cwd = os.path.join(os.getcwd(), tc_name + "_" + now)
    log_file = os.path.join(cwd, "cscript_{}_{}.log".format(tc_name, now))
    serial_log = cwd + "/serial_log.log"
    os_flag = "Ubuntu 20.04 LTS"
    os.mkdir(cwd)
    log(log_file)
    print("Start {} Test:".format(tc_name))

    error_log = Serial.SutControl(detect_serial_ports(), 115200, 0.5, log=serial_log)
    bmc = ssh.SshConnection()
    try:
        unitool = Unitool.SerialUnitool(ser=error_log)
        unitool.set_config("DFX")
        unitool.set_config(config)
        ser0 = threading.Thread(target=error_log.capture_data)
        ser0.setDaemon(True)
        ser0.start()

        bmc.login(BMC_IP, BMC_USER, BMC_PASSWORD)
        print("BMC login success!")
        if bmc.interaction(["maint_debug_cli\n", "attach diag\n", "dump_state 1\n", "bye\n"],
                           ["%", "Success", "Success", "Byebye"]):  # Enable FDM LOG
            print("FDM Log Enabled!")
        else:
            print("FDM Log Enable Failed!")

        exec(func_tc_name + "()")

        if bmc_dump(bmc, cwd, tc_name):
            print("Reset and wait SUT boot to OS... ")
            force_power_cycle(bmc)
        error_log.close_session()

        boot_log = Serial.SutControl(detect_serial_ports(), 115200, 0.5, log=serial_log)
        if boot_log.is_msg_present_general(os_flag):
            print("=" * 30, "Boot to OS successfully!", "=" * 30)
            boot_log.close_session()
            return True
        nolog()

    except Exception as e:
        print(e)
        error_log.close_session()
        force_power_cycle(bmc)
        bmc.close_session()
        print("{} Test Error !".format(tc_name))
        nolog()
        except_log = Serial.SutControl(detect_serial_ports(), 115200, 0.5, log=serial_log)
        if except_log.is_msg_present_general(os_flag):
            except_log.close_session()
        pass


def run_all_case(*args):
    func_list = args
    for func in func_list:
        tc_list = [t for t in eval("dir({})".format(func)) if "Testcase" in t]
        # config = eval("{}.CONFIG".format(func))
        for tc in tc_list:
            # print(func + "." + tc)
            run(func + "." + tc)


load_scripts("Testcase")
run_all_case("ADDDC", "RankSparing1", "RankSparing2", "SmiStorm")
