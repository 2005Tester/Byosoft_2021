import logging
import subprocess
import time
from D2000.Config import SutConfig
import re
from multidict import CIMultiDict


# run command in windows,
def interaction(cmd, exp, timeout=10):
    logging.info("Run command: {0}".format(cmd))
    start_time = time.time()
    while True:
        # 主要用来执行shell命令，args是待执行的命令，shell为True是就执行shell命令。当args为列表（列表第一项通常是要执行程序的路径，后面是要执行的命令），
        # shell为false时，表示在列表第一项的程序下执行命令。
        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()  # 输出的是程序的标准输出和标准错误
        now = time.time()
        time_spent = (now - start_time)
        if exp in stdoutput.decode('gbk'):
            logging.info("{0}".format(exp))
            break
        if time_spent > timeout:
            logging.error("Command run timeout - %s seconds, unable to find the expected result." % time_spent)
            break
            # return
    logging.debug(stdoutput.decode('gbk'))
    return True


def ping_sut(delay=200):
    logging.info("Test network connection...")
    ping_cmd = 'ping {0}'.format(SutConfig.Env.OS_IP)
    start_time = time.time()
    while True:
        now_1 = time.time()
        p = subprocess.Popen(args=ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while p.poll() is None:
            line = p.stdout.readline().decode('gbk')
            if 'TTL=' in line:
                logging.info("SUT is online.")
                return True
            if time.time() - now_1 > 1:
                break
        now = time.time()
        time_spent = (now - start_time)
        if time_spent > delay:
            logging.error("Lost SUT for %s seconds, check the ip connection" % time_spent)
            return False


# updated by arthur,
def is_power_on():
    logging.info("Check power status...")
    ret_cmd = '{0} chassis power status'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power is on')


def is_power_off():
    logging.info("Check power status...")
    ret_cmd = '{0} chassis power status'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power is off')


# check power status
def power_status():
    logging.info("Check power status...")
    time.sleep(5)
    ret_cmd = '{0} chassis power status'.format(SutConfig.Env.IPMITOOL)
    logging.info("Run command: {0}".format(ret_cmd))
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        sut_status1 = "Chassis Power is off"
        sut_status2 = "Chassis Power is on"
        if sut_status1 in stdoutput.decode('gbk'):
            logging.info("{0}".format(sut_status1))
            return sut_status1
        if sut_status2 in stdoutput.decode('gbk'):
            logging.info("{0}".format(sut_status2))
            return sut_status2
        if time_spent > 10:
            logging.error("Command run timeout - %s seconds, unable to find the power status." % time_spent)
            return


def power_off():
    logging.info("Starting to power off the SUT.")
    ret_cmd = '{0} chassis power off'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Down/Off')


def power_on():
    logging.info("Starting to power on the SUT.")
    ret_cmd = '{0} chassis power on'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Up/On')


def init_sut():
    logging.info("Init SUT power status to on...")
    try:
        if power_status() == "Chassis Power is off":
            logging.info("SUT is off, now power on")
            assert power_on(), "Power on failed."
            return True
        else:
            logging.info("SUT is on, now cycle it.")
            assert power_cycle(), "Power cycle failed."
            return True
    except AssertionError:
        return


def power_reset():
    logging.info("Starting to power reset the SUT.")
    ret_cmd = '{0} chassis power reset'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Reset')


def power_cycle():
    logging.info("Starting to power cycle the SUT.")
    ret_cmd = '{0} chassis power cycle'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Cycle')


def set_console_to_bios():
    logging.info("Set Console output to BIOS.")
    ret_cmd = '{0} raw 0x3e 0xc4 0x01'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, "")


# Enable Console
def enable_console_direction():
    ret_cmd = '{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    cmd = stdoutput.decode('gbk')
    cmd = re.findall('[0-9a-zA-Z]{2}', cmd)
    if int(cmd[-1], 16) & 1 == 1:
        cmd[-1] = hex(int(cmd[-1], 16) - 1)[2:]
    logging.info("Enable console direction.")
    cmd_console = hex(int('{:08b}'.format(int(cmd[7], 16))[:3] + '10011', 2))[2:]
    ret_cmd = '{0} raw 0x3e 0xc3 0x01 0x{1} 0x{2} 0x{3} 0x{4} 0x{5} 0x{6} 0x{7} 0x{8} 0x{9} 0x{10} 0x{11} 0x{12} 0x{13}'.format(
        SutConfig.Env.IPMITOOL, cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6], cmd_console, cmd[8], cmd[9], cmd[10],
        cmd[11],
        cmd[12], cmd[13])
    return interaction(ret_cmd, "")


# Check whether Console is enabled or not
def check_serial_status():
    set_console_to_bios()
    logging.info("Check Serial status.")
    ret_cmd = '{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    logging.info("Run command: {0}".format(ret_cmd))
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        cmd = stdoutput.decode('gbk')
        now = time.time()
        time_spent = (now - start_time)
        if '{:08b}'.format(int(cmd[22:24], 16))[-5:] != '10011':
            # if cmd[22:24] != '13':
            logging.info("Checked BIOS value is:{0}".format(cmd))
            logging.info("Serial is disabled.")
            return re.findall('[0-9a-zA-Z]{2}', cmd)
        cmd = re.findall('[0-9a-zA-Z]{2}', cmd)
        if int(cmd[-1], 16) & 1 == 1:
            logging.info("Checked BIOS value is:{0}".format(cmd))
            logging.info("Quiet Boot is enabled.")
            return cmd
        if time_spent > 5:
            logging.error("Command run timeout - %s seconds, unable to find the expected result." % time_spent)
            return "enabled"
        logging.info("Checked BIOS value is:{0}".format(stdoutput.decode('gbk')))
        logging.info("Serial is enabled.")
        return "enabled"


# Enable Console and Shell after update BIOS
def enable_serial_after_update_bios():
    init_sut()
    logging.info("Delay 90s to let new BIOS boot once.")
    time.sleep(90)
    set_console_to_bios()
    enable_console_direction()
    power_reset()
    while True:
        logging.info("Delay 5s to check serial status.")
        time.sleep(5)
        if check_serial_status() == "disabled":
            logging.info("Delay 30s to enable serial again.")
            time.sleep(30)
            set_console_to_bios()
            enable_console_direction()
            power_reset()
        else:
            set_console_to_bios()
            logging.info("Enable Serial successed.")
            return True


# Enable Console and Shell
def enable_serial_normal():
    set_console_to_bios()
    while True:
        logging.info("Delay 5s to check serial status.")
        time.sleep(5)
        cmd = check_serial_status()
        if cmd != "enabled":
            set_console_to_bios()
            if int(cmd[-1], 16) & 1 == 1:
                cmd[-1] = hex(int(cmd[-1], 16) - 1)[2:]
            cmd_console = hex(int('{:08b}'.format(int(cmd[7], 16))[:3] + '10011', 2))[2:]
            logging.info("Enable console direction.")
            ret_cmd = '{0} raw 0x3e 0xc3 0x01 0x{1} 0x{2} 0x{3} 0x{4} 0x{5} 0x{6} 0x{7} 0x{8} 0x{9} 0x{10} 0x{11} 0x{12} 0x{13}'.format(
                SutConfig.Env.IPMITOOL, cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6], cmd_console, cmd[8], cmd[9],
                cmd[10],
                cmd[11],
                cmd[12], cmd[13])
            interaction(ret_cmd, "")
            init_sut()
        else:
            set_console_to_bios()
            logging.info("Direct to boot.")
            return True


def enable_serial_only():
    set_console_to_bios()
    ret_cmd = '{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    cmd = stdoutput.decode('gbk')
    if '{:08b}'.format(int(cmd[22:24], 16))[-5:] != '10011':
        # if cmd[22: 24] != '13':
        cmd = re.findall('[0-9a-zA-Z]{2}', cmd)
        time.sleep(1)
        set_console_to_bios()
        cmd_console = hex(int('{:08b}'.format(int(cmd[7], 16))[:3] + '10011', 2))[2:]
        ret_cmd = '{0} raw 0x3e 0xc3 0x01 0x{1} 0x{2} 0x{3} 0x{4} 0x{5} 0x{6} 0x{7} 0x{8} 0x{9} 0x{10} 0x{11} 0x{12} 0x{13}'.format(
            SutConfig.Env.IPMITOOL, cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6], cmd_console, cmd[8], cmd[9],
            cmd[10], cmd[11],
            cmd[12], cmd[13])
        logging.info('Run Command {0}'.format(ret_cmd))
        p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        time.sleep(3)
        power_reset()
        time.sleep(2)
        return True
    else:
        set_console_to_bios()
        logging.info('Serial is Enabled')
        return True


def change_bios_value(input):
    option_value1 = SutConfig.Ipm.OPTION_VALUE
    option_value = CIMultiDict()
    for k1, v1 in option_value1.items():
        dict = CIMultiDict()
        for k2, v2 in v1[1].items():
            dict[k2] = v2
        option_value[k1] = [v1[0], dict]
    ret_cmd = '{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    hexadecimal = stdoutput.decode('gbk')
    cmd = re.findall('\w+', hexadecimal)
    for i in input:
        option = i.split(':')[0]
        value = i.split(':')[1]
        if option.lower() == 'waittime':
            cmd[12] = '{:0{width}x}'.format(int(value), width=4)[:2]
            cmd[11] = '{:0{width}x}'.format(int(value), width=4)[-2:]
        else:
            a = cmd[option_value[option][0]]  # 16进制数字
            b = '{:08b}'.format(int(a, 16))[::-1]  # 十六进制转8位二进制数字的倒序
            index_start = int(option_value[option][1][value][0].split(',')[0])  # 要替换的起始序号
            if len(option_value[option][1][value][0].split(',')) > 1:
                index_end = int(option_value[option][1][value][0].split(',')[1]) + 1  # 要替换的结束序号
            else:
                index_end = index_start + 1

            b = b[:index_start] + option_value[option][1][value][1][::-1] + b[index_end:]  # 替换为需要修改的值
            b = b[::-1]  # 变回原来的顺序

            if len(hex(int(b, 2))[2:]) == 1:
                cmd[option_value[option][0]] = '0' + hex(int(b, 2))[2:]  # 转换为十六进制
            else:
                cmd[option_value[option][0]] = hex(int(b, 2))[2:]  # 转换为十六进制
        # print(cmd)
    ret_cmd_change = '{0} raw 0x3e 0xc3 0x01 0x{1} 0x{2} 0x{3} 0x{4} 0x{5} 0x{6} 0x{7} 0x{8} 0x{9} 0x{10} 0x{11} 0x{12} 0x{13}'.format(
        SutConfig.Env.IPMITOOL, cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6], cmd[7], cmd[8], cmd[9], cmd[10],
        cmd[11], cmd[12], cmd[13])
    assert interaction(ret_cmd_change, "")
    return cmd


def get_boot_mode():
    ret_cmd = '{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    hexadecimal = stdoutput.decode('gbk')
    cmd = re.findall('\w+', hexadecimal)
    if int(cmd[3], 16) & 1 == 1:
        return 'Legacy'
    else:
        return 'UEFI'
