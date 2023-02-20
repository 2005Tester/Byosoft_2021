# -*- encoding=utf8 -*-
import logging
import subprocess
import time
from Inspur7500.BaseLib import SetUpLib
from Inspur7500.Config import SutConfig, Key
import re
from multidict import CIMultiDict
import paramiko

# 每次开机强制更改的选项
force_option = ['Console:Enabled', 'Baudrate:115200', 'Language:English', 'TermType:UTF-8', 'QuietBoot:Disabled']


# run command in windows
def interaction(cmd, exp, timeout=10):
    logging.debug("Run command: {0}".format(cmd))
    start_time = time.time()
    while True:
        # 主要用来执行shell命令，args是待执行的命令，shell为True是就执行shell命令。当args为列表（列表第一项通常是要执行程序的路径，后面是要执行的命令），
        # shell为false时，表示在列表第一项的程序下执行命令。
        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()  # 输出的是程序的标准输出和标准错误
        now = time.time()
        time_spent = (now - start_time)
        if exp in stdoutput.decode('gbk'):
            logging.debug("{0}".format(exp))
            break
        if time_spent > timeout:
            logging.error("Command run timeout - %s seconds, unable to find the expected result." % time_spent)
            break
            # return
    logging.debug(stdoutput.decode('gbk'))
    return True


def output(cmd):
    """执行cmd命令并返回结果"""
    logging.info("Run command: {0}".format(cmd))
    try:
        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()  # 输出的是程序的标准输出和标准错误
        if stdoutput != b'':
            logging.debug(stdoutput.decode('gbk'))
            return stdoutput.decode('gbk')
        elif erroutput != b'':
            logging.debug(erroutput.decode('gbk'))
            return erroutput.decode('gbk')
        else:
            return ''
    except:
        return ''


def ping_sut(delay=200):
    """检查IP是否可以Ping通"""
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
        # if ssh_login():
        #     logging.info("SUT is online.")
        #     return True
        now = time.time()
        time_spent = (now - start_time)
        if time_spent > delay:
            logging.error("Lost SUT for %s seconds, check the ip connection" % time_spent)
            return False


def is_power_on():
    """判断是否开机状态"""
    logging.info("Check power status...")
    ret_cmd = '{0} chassis power status'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power is on')


def is_power_off():
    """判断是否关机状态"""
    logging.info("Check power status...")
    ret_cmd = '{0} chassis power status'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power is off')


# check power status
def power_status():
    """检查当前机器状态(关机或开机)"""
    logging.debug("Check power status...")
    time.sleep(5)
    ret_cmd = '{0} chassis power status'.format(SutConfig.Env.IPMITOOL)
    logging.debug("Run command: {0}".format(ret_cmd))
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
    """关机"""
    logging.debug("Starting to power off the SUT.")
    ret_cmd = '{0} chassis power off'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Down/Off')


def power_on():
    """开机"""
    logging.debug("Starting to power on the SUT.")
    ret_cmd = '{0} chassis power on'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Up/On')


def init_sut():
    """初始化机器(关机状态:开机,开机状态:关机开机)"""
    activate_bmc()
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
    """重启"""
    logging.debug("Starting to power reset the SUT.")
    ret_cmd = '{0} chassis power reset'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Reset')


def power_cycle():
    """关机开机"""
    logging.debug("Starting to power cycle the SUT.")
    ret_cmd = '{0} chassis power cycle'.format(SutConfig.Env.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Cycle')


def set_console_to_bios():
    """切换BIOS串口"""
    logging.debug("Set Console output to BIOS.")
    ret_cmd = '{0} {1}'.format(SutConfig.Env.IPMITOOL, SutConfig.Env.SET_BIOS_SERIAL)
    return interaction(ret_cmd, "")


def check_serial_status():
    """检查当前串口状态，语言，安静启动"""
    activate_bmc()
    set_console_to_bios()
    logging.info("Check Serial status.")
    ret_cmd = '{0} {1}'.format(SutConfig.Env.IPMITOOL, SutConfig.Env.GET_OPTION)
    start_time = time.time()
    while True:
        stdout = output(ret_cmd).strip('\n')
        cmd = re.findall('\w+', stdout)
        if len(cmd) == 14:
            option_value = get_oem_option(cmd)
            if any(option_value.get(i.split(':')[0]) != i.split(':')[1] for i in force_option):
                logging.info("Checked BIOS value is:{0}".format(stdout))
                logging.info("Serial is disabled.")
                return cmd
            else:
                logging.info("Checked BIOS value is:{0}".format(stdout))
                logging.info("Serial is enabled.")
                return "enabled"
        if (time.time() - start_time) > 5:
            logging.error("Command run timeout 5 seconds, unable to find the expected result.")
            return "enabled"
        time.sleep(1)


# Enable Console and Shell
def enable_serial_normal():
    """强制打开串口，关闭安全启动，修改语言英文"""
    try_counts = 3
    while try_counts:
        logging.info("Delay 5s to check serial status.")
        time.sleep(5)
        cmd = check_serial_status()
        if cmd != "enabled":
            cmd = get_cmd_change(cmd, force_option)
            logging.info("Enable console direction.")
            ret_cmd = '{} {} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{}'.format(
                SutConfig.Env.IPMITOOL, SutConfig.Env.CHANGE_OPTION, *tuple(cmd[1:]))
            interaction(ret_cmd, "")
            init_sut()
            try_counts -= 1
        else:
            logging.info("Direct to boot.")
            return True


def enable_serial_only():
    set_console_to_bios()
    ret_cmd = '{0} {1}'.format(SutConfig.Env.IPMITOOL, SutConfig.Env.GET_OPTION)
    p = subprocess.Popen(args=ret_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    cmd = stdoutput.decode('gbk')
    if '{:08b}'.format(int(cmd[22:24], 16))[-5:] != '10011' or '{:08b}'.format(int(cmd[22:24], 16))[:2] != '10':
        # if cmd[22: 24] != '13':
        cmd = re.findall('[0-9a-zA-Z]{2}', cmd)
        time.sleep(1)
        set_console_to_bios()
        # cmd_console = hex(int('{:08b}'.format(int(cmd[7], 16))[:3] + '10011', 2))[2:]
        cmd_console = hex(int('10' + '{:08b}'.format(int(cmd[7], 16))[2] + '10011', 2))[2:]
        ret_cmd = '{0} {14} 0x{1} 0x{2} 0x{3} 0x{4} 0x{5} 0x{6} 0x{7} 0x{8} 0x{9} 0x{10} 0x{11} 0x{12} 0x{13}'.format(
            SutConfig.Env.IPMITOOL, cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6], cmd_console, cmd[8], cmd[9],
            cmd[10], cmd[11],
            cmd[12], cmd[13], SutConfig.Env.CHANGE_OPTION)
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


def get_cmd_change(current_cmd, change):
    """传入当前选项对应的oem和要改变的选项值，返回改变后的oem"""
    option_value1 = SutConfig.Ipm.OPTION_VALUE
    option_value = CIMultiDict()
    for k1, v1 in option_value1.items():
        dict = CIMultiDict()
        for k2, v2 in v1[1].items():
            dict[k2] = v2
        option_value[k1] = [v1[0], dict]
    for i in change:
        option = i.split(':')[0]
        value = i.split(':')[1]
        if option.lower() == 'waittime':
            current_cmd[12] = '{:0{width}x}'.format(int(value), width=4)[:2]
            current_cmd[11] = '{:0{width}x}'.format(int(value), width=4)[-2:]
        else:
            a = current_cmd[option_value[option][0]]  # 16进制数字
            b = '{:08b}'.format(int(a, 16))[::-1]  # 十六进制转8位二进制数字的倒序
            index_start = int(option_value[option][1][value][0].split(',')[0])  # 要替换的起始序号
            if len(option_value[option][1][value][0].split(',')) > 1:
                index_end = int(option_value[option][1][value][0].split(',')[1]) + 1  # 要替换的结束序号
            else:
                index_end = index_start + 1

            b = b[:index_start] + option_value[option][1][value][1][::-1] + b[index_end:]  # 替换为需要修改的值
            b = b[::-1]  # 变回原来的顺序
            current_cmd[option_value[option][0]] = '0' + hex(int(b, 2))[2:] if len(hex(int(b, 2))[2:]) == 1 else hex(
                int(b, 2))[2:]
    return current_cmd


def get_oem_option(oem):
    """传入oem，返回对应的选项值"""
    oem_option_value = {}
    for k, v in SutConfig.Ipm.OPTION_VALUE.items():
        binary = f'{int(oem[v[0]], 16):08b}'[::-1]  # 转为2进制并倒序
        index = [i[0] for i in v[1].values()][0].split(',')
        index_start = int(index[0])  # ['3,4','3,4','3,4']
        index_end = int(index[1]) if len(index) > 1 else index_start
        for m, n in v[1].items():
            if n[1] == binary[index_start:index_end + 1][::-1]:
                value = m
                oem_option_value[k] = value
    return oem_option_value


def change_bios_value(input):
    """通过OEM命令修改BIOS选项"""
    change_option = force_option + input if check_serial_status() != 'enabled' else input
    logging.info(f'Change BIOS value => {",".join(input)}')
    get_cmd = '{0} {1}'.format(SutConfig.Env.IPMITOOL, SutConfig.Env.GET_OPTION)
    hexadecimal = output(get_cmd)
    cmd = re.findall('\w+', hexadecimal)
    cmd_change = get_cmd_change(cmd, change_option)
    ret_cmd_change = '{} {} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{} 0x{}'.format(
        SutConfig.Env.IPMITOOL, SutConfig.Env.CHANGE_OPTION, *tuple(cmd_change[1:]))
    try_counts = 3
    while try_counts:
        interaction(ret_cmd_change, "")
        init_sut()
        logging.info("Delay 5s to check bios value.")
        time.sleep(5)
        changed_cmd = output(get_cmd)
        logging.info("Checked BIOS value is:{0}".format(changed_cmd))
        if re.findall('\w+', changed_cmd) == cmd_change:
            break
        try_counts -= 1
    return cmd_change


def get_boot_mode():
    ret_cmd = '{0} {1}'.format(SutConfig.Env.IPMITOOL, SutConfig.Env.GET_OPTION)
    hexadecimal = output(ret_cmd)
    cmd = re.findall('\w+', hexadecimal)
    if int(cmd[3], 16) & 1 == 1:
        return 'Legacy'
    else:
        return 'UEFI'


def is_bmc_activate(delay=10, bmc_ip=None):
    """判断当前BMC是否可用"""
    if bmc_ip is not None:
        cmd = f'{SutConfig.Env.IPMITOOL.replace(SutConfig.Env.BMC_IP, bmc_ip)} chassis power status'
    else:
        cmd = f'{SutConfig.Env.IPMITOOL} chassis power status'
    start_time = time.time()
    while time.time() - start_time < delay:
        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start = time.time()
        error = False
        while p.poll() is None:
            now = time.time()
            if now - start > 2:
                error = True
                break
        if error:
            p.kill()
        else:
            return True
        time.sleep(1)


def activate_bmc():
    """如果BMC不可用，等待BMC重启完成，更新BMC IP"""
    if not is_bmc_activate():
        logging.info('BMC may restart')
        start = time.time()
        while time.time() - start < 300:
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.wait_message('login:', 3):
                break
        SetUpLib.send_data_enter(SutConfig.Env.BMC_SERIAL_USER)
        assert SetUpLib.wait_message('Password:', 10)
        time.sleep(2)
        SetUpLib.send_data_enter(SutConfig.Env.BMC_SERIAL_PASSWORD)
        assert SetUpLib.wait_message(SutConfig.Env.BMC_SERIAL_USER, 20)
        SetUpLib.send_data_enter('ifconfig')
        bmc_ip = re.findall('inet addr:(192.\d+.\d+.\d+)', SetUpLib.get_data(5))
        if not bmc_ip:
            return
        bmc_ip = bmc_ip[0]
        time.sleep(20)
        if not is_bmc_activate(30, bmc_ip):
            return
        if bmc_ip != SutConfig.Env.BMC_IP:
            SutConfig.Env.IPMITOOL = SutConfig.Env.IPMITOOL.replace(SutConfig.Env.BMC_IP, bmc_ip)
            SutConfig.Env.BMC_IP = bmc_ip
        logging.info('BMC reboot ends.')
        return True
