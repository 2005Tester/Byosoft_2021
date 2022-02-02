#coding='utf-8'
import re
import time
import logging
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from Inspur7500.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



#CPU信息
def cpu_information():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    data=SetUpLib.get_data(1)
    cpu_core=re.findall(r'CPU Core Count *?(\d{2})',data)
    cpu_thread=re.findall(r'CPU Thread Count *?(\d{2})',data)
    cpu_frequency=re.findall(r'CPU Frequency *?(\d{4}).*?MHz',data)
    assert SetUpLib.boot_os_from_bm()

    core_result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4|grep 'Core Count'")

    linux_cpu_core=re.findall(r'Core Count: (\d{2})',core_result[0])
    if cpu_core[0]==linux_cpu_core[0]:
        logging.info('CPU核数验证成功')
    else:
        stylelog.fail('CPU核数验证失败,setup下CPU频率{0}，Linux下CPU频率{1}'.format(cpu_core,linux_cpu_core))
        count+=1
    thread_result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4|grep 'Thread Count'")
    linux_cpu_thread=re.findall(r'Thread Count: (\d{2})',thread_result[0])
    if cpu_thread[0]==linux_cpu_thread[0]:
        logging.info('CPU线程数验证成功')
    else:
        stylelog.fail('CPU线程数验证失败,setup下CPU线程数{0}，Linux下CPU线程数{1}'.format(cpu_thread,linux_cpu_thread))
        count+=1

    frequency_result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4| grep 'Current Speed'")

    linux_cpu_frequency=re.findall(r'Current Speed: (\d{4}) MHz',frequency_result[0])
    if cpu_frequency[0]==linux_cpu_frequency[0]:
        logging.info('CPU频率验证成功')
    else:
        stylelog.fail('CPU频率验证失败，setup下CPU频率{0}，Linux下CPU频率{1}'.format(cpu_frequency,linux_cpu_frequency))
        count+=1
    if count==0:
        return True
    else:
        return



#CPU频率
def cpu_frequency():
    speed=SutConfig.Cpu.CPU_FREQUENCY
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_FREQUENCY1,15)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info('修改CPU频率为{0}MHz'.format(speed[0]))
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4| grep 'Current Speed'")

    linux_cpu_frequency=re.findall(r'Current Speed: (\d{4}) MHz',result[0])
    if linux_cpu_frequency[0]==speed[0]:
        logging.info('linux下CPU频率为{0}MHz'.format(speed[0]))
    else:
        stylelog.fail('Linux下CPU频率不是{0}MHz，为{1}'.format(speed[0],linux_cpu_frequency[0]))
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    cpu_frequency=re.findall(r'CPU Frequency *?(\d{4}).*?MHz',SetUpLib.get_data(1))
    if cpu_frequency[0]==speed[0]:
        logging.info('Setup下CPU频率为{0}MHz'.format(speed[0]))
    else:
        stylelog.fail('Setup下CPU频率不是{0}MHz，为{1}'.format(speed[0],cpu_frequency[0]))
        return
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_FREQUENCY2,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info('修改CPU频率为{0}MHz'.format(speed[1]))
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4|grep 'Current Speed'")
    linux_cpu_frequency=re.findall(r'Current Speed: (\d{4}) MHz',result[0])
    if linux_cpu_frequency[0]==speed[1]:
        logging.info('Linux下CPU频率为{0}MHz'.format(speed[1]))
    else:
        stylelog.fail('Linux下CPU频率不是{0}MHz，为{1}'.format(speed[1],linux_cpu_frequency[0]))
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    cpu_frequency=re.findall(r'CPU Frequency *?(\d{4}).*?MHz',SetUpLib.get_data(1))
    if cpu_frequency[0]==speed[1]:
        logging.info('Setup下CPU频率为{0}Mhz'.format(speed[1]))
    else:
        stylelog.fail('Setup下CPU频率不是{0}Mhz，为{1}'.format(speed[1],cpu_frequency[0]))
        return
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.SET_FREQUENCY3, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    logging.info('修改频率为{0}MHz'.format(speed[2]))
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4|grep 'Current Speed'")

    linux_cpu_frequency=re.findall(r'Current Speed: (\d{4}) MHz',result[0])
    if linux_cpu_frequency[0]==speed[2]:
        logging.info('Linux下CPU频率为{0}Mhz'.format(speed[2]))
    else:
        stylelog.fail('Linux下CPU频率不是{0}Mhz，为{1}'.format(speed[2],cpu_frequency[0]))
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    cpu_frequency=re.findall(r'CPU Frequency *?(\d{4}).*?MHz',SetUpLib.get_data(1))
    if cpu_frequency[0]==speed[2]:
        logging.info('Setup下CPU频率为{0}Mhz'.format(speed[2]))
    else:
        stylelog.fail('Setup下CPU频率不是{0}Mhz，为{1}'.format(speed[2],cpu_frequency[0]))
        return
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.SET_FREQUENCY4, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#CPU超线程
def cpu_hyper_threading():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_HYPER_THREADING,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    cmd_result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4 | grep 'Thread Count'")

    cmd_result=cmd_result[0]
    thread_count_close=re.findall('Thread Count: ([0-9]+)',cmd_result)[0]
    logging.info('超线程关闭，系统Thread Count为{0}'.format(thread_count_close))
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    if SetUpLib.wait_message('CPU Thread Count +{0}'.format(thread_count_close),10,readline=True):
        logging.info('超线程关闭，setup下Thread Count 与系统下一致')
    else:
        stylelog.fail('setup下Thread Count 与系统下不一致')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_HYPER_THREADING,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    cmd_result=SshLib.execute_command_limit(Sut.OS_SSH,"dmidecode -t 4 | grep 'Thread Count'")

    cmd_result=cmd_result[0]
    thread_count_open=re.findall('Thread Count: ([0-9]+)',cmd_result)[0]
    logging.info('超线程打开，系统Thread Count为{0}'.format(thread_count_open))
    if int(thread_count_open)==int(thread_count_close)*2:
        logging.info('超线程打开,Thread Count数量是没有打开的2倍')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CPU_INFO, 5)
    if SetUpLib.wait_message('CPU Thread Count +{0}'.format(thread_count_open),10,readline=True):
        logging.info('超线程打开，setup下Thread Count 与系统下一致')
    else:
        stylelog.fail('setup下Thread Count 与系统下不一致')
        return
    return True



# CPU C-State
def cpu_cstate():
    count = 0
    cpu_speed = SutConfig.Cpu.CPU_FREQUENCY_CSTATE
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.OPEN_CSTATE, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.OPEN_CPB, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    cc6open = []
    SshLib.invoke_shell(Sut.OS_SSH, './SMUToolSuite > cstateopen.txt\n')
    time.sleep(1)
    cmd = SshLib.execute_command_limit(Sut.OS_SSH, 'cat cstateopen.txt')[0]
    for i in cmd.split('\r'):
        if re.search('core\d+', i):
            cc6open.append(re.findall('\d+.\d+', i)[-1])
    if cc6open != []:
        if any(i != '0.00' for i in cc6open):
            logging.info(cc6open)
            logging.info('C-State打开，cc6不为0')
        else:
            stylelog.fail('C-State打开，cc6仍为0')
            count += 1
    else:
        stylelog.fail('命令没有获取到结果')
        return
    time.sleep(1)
    SshLib.execute_command_limit(Sut.OS_SSH, 'rm -f cstateopen.txt')
    time.sleep(1)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CLOSE_CSTATE, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    cc6close = []
    SshLib.invoke_shell(Sut.OS_SSH, './SMUToolSuite > cstateclose.txt\n')
    time.sleep(1)
    cmd = SshLib.execute_command_limit(Sut.OS_SSH, 'cat cstateclose.txt')[0]
    for i in cmd.split('\r'):
        if re.search('core\d+', i):
            cc6close.append(re.findall('\d+.\d+', i)[-1])
    if cc6close != []:
        if all(i == '0.00' for i in cc6close):
            logging.info(cc6close)
            logging.info('C-State关闭，cc6全为0')
        else:
            stylelog.fail('C-State关闭，cc6仍不为0')
            count += 1
    else:
        stylelog.fail('命令没有获取到结果')
        return
    time.sleep(1)
    SshLib.execute_command_limit(Sut.OS_SSH, 'rm -f cstateclose.txt')
    time.sleep(1)
    if count == 0:
        return True
    else:
        return



# CPU P-State
def cpu_pstate():
    cpu_speed=SutConfig.Cpu.CPU_FREQUENCY_PSTATE
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_PSTATE_P0,18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_CPB,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    result0 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 0')

    if re.search('No such file or directory|没有那个文件或目录',result0[1]):
        logging.info('只打开P0，无法切换pstate为P0')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result0[0], result0[1]))
        return

    result1 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 1')

    if re.search('No such file or directory|没有那个文件或目录',result1[1]):
        logging.info('只打开P0，无法切换pstate为P1')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result1[0], result1[1]))
        return

    result2 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 2')

    if re.search('No such file or directory|没有那个文件或目录',result2[1]):
        logging.info('只打开P0，无法切换pstate为P2')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result2[0], result2[1]))
        return
    try_counts = 10
    while try_counts:

        output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+', i)
        if all(speed == cpu_speed[0] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts==0:
        stylelog.fail('P0下core 频率不是{0},是{1}'.format(cpu_speed[0],speeds))
        return
    else:
        logging.info('P0下core 频率为{0}'.format(cpu_speed[0]))
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_PSTATE_P0P1,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()
    result0 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 0')

    time.sleep(2)
    if len(result0[0]) == 0 and len(result0[1]) == 0:
        time.sleep(2)
        logging.info('成功切换pstate为P0')

        try_counts = 10
        while try_counts:

            output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
            speeds = []
            for i in output.split('\n'):
                if 'clock:' in i:
                    speeds += re.findall('\d.\d+', i)
            if all(speed == cpu_speed[0] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('P0下core 频率不是{0},是{1}'.format(cpu_speed[0],speeds))
            return
        else:
            logging.info('P0下core 频率为{0}'.format(cpu_speed[0]))
    else:
        stylelog.fail('切换pstate为P0失败')
        return

    result1 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 1')

    if len(result1[0]) == 0 and len(result1[1]) == 0:
        logging.info('成功切换pstate为P1')
        time.sleep(2)
        try_counts = 10
        while try_counts:

            output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
            speeds = []
            for i in output.split('\n'):
                if 'clock:' in i:
                    speeds += re.findall('\d.\d+', i)
            if all(speed == cpu_speed[1] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('切换pstate为P1 频率不是{0},是{1}'.format(cpu_speed[1],speeds))
            return
        else:
            logging.info('切换pstate为P1 频率为{0}'.format(cpu_speed[1]))
    else:
        stylelog.fail('切换pstate为P1失败')
        return


    result2 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 2')

    if 'aviliable pstate:' in result2[0]:
        logging.info('只打开P0+P1，无法切换pstate为P2')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result2[0], result2[1]))
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_PSTATE_P0P1P2,18)

    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()

    result0 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 0')

    if len(result0[0]) == 0 and len(result0[1]) == 0:
        logging.info('成功切换pstate为P0')
        time.sleep(2)
        try_counts = 10
        while try_counts:

            output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
            speeds = []
            for i in output.split('\n'):
                if 'clock:' in i:
                    speeds += re.findall('\d.\d+', i)
            if all(speed == cpu_speed[0] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('P0下core 频率不是{0},是{1}'.format(cpu_speed[0],speeds))
            return
        else:
            logging.info('P0下core 频率为{0}'.format(cpu_speed[0]))

    else:
        stylelog.fail('切换pstate为P0失败')
        return

    result1 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 1')

    if len(result1[0]) == 0 and len(result1[1]) == 0:
        logging.info('成功切换pstate为P1')
        time.sleep(2)
        try_counts = 10
        while try_counts:

            output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
            speeds = []
            for i in output.split('\n'):
                if 'clock:' in i:
                    speeds += re.findall('\d.\d+', i)
            if all(speed == cpu_speed[1] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('切换pstate为P1 频率不是{0},是{1}'.format(cpu_speed[1],speeds))
            return
        else:
            logging.info('切换pstate为P1 频率为{0}'.format(cpu_speed[1]))
    else:
        stylelog.fail('切换pstate为P1失败')
        return

    result2 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 2')

    if len(result2[0]) == 0 and len(result2[1]) == 0:
        logging.info('成功切换pstate为P2')
        time.sleep(2)
        try_counts = 10
        while try_counts:

            output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
            speeds = []
            for i in output.split('\n'):
                if 'clock:' in i:
                    speeds += re.findall('\d.\d+', i)
            if all(speed == cpu_speed[2] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('切换pstate为P2 频率不是{0},是{1}'.format(cpu_speed[2],speeds))
            return
        else:
            logging.info('切换pstate为P2 频率为{0}'.format(cpu_speed[2]))
    else:
        stylelog.fail('切换pstate为P2失败')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_HIGH,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()

    result0 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 0')

    if re.search('No such file or directory|没有那个文件或目录',result0[1]):
        logging.info('高性能模式下，无法切换pstate为P0')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result0[0], result0[1]))
        return

    result1 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 1')

    if re.search('No such file or directory|没有那个文件或目录',result1[1]):
        logging.info('高性能模式下，无法切换pstate为P1')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result1[0], result1[1]))
        return

    result2 = SshLib.execute_command_limit(Sut.OS_SSH, './pstate-set.sh -1 2')

    if re.search('No such file or directory|没有那个文件或目录',result2[1]):
        logging.info('高性能模式下，无法切换pstate为P2')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result2[0], result2[1]))
        return
    try_counts = 10
    while try_counts:

        output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+', i)
        if all(speed == cpu_speed[0] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('高性能模式下core 频率不是{0},是{1}'.format(cpu_speed[0],speeds))
        return
    else:
        logging.info('高性能模式下core 频率为{0}'.format(cpu_speed[0]))
    return True



#CPU降核
def cpu_downcore_control():
    core=SutConfig.Cpu.CPU_DOWNCORE_CORE
    values=SutConfig.Cpu.DOWNCORE_VALUES
    count=0
    for value in values:
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(2)
        logging.info('{0}组合测试...........................................................'.format(value))
        assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Cpu.LOC_DOWNCORE,18)
        time.sleep(1)
        assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Cpu.DOWNCORE_NAME], 18, '{0}'.format(value))
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        assert SetUpLib.boot_os_from_bm()

        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t 4 | grep 'Core Enabled'")

        cmd_result = cmd_result[0]
        core_enabled = re.findall(r'Core Enabled: +([0-9]+)', cmd_result)
        for i in core_enabled:
            if i == core[values.index(value)]:
                logging.info('修改核心数量为{0}，Core Enabled 为{1}'.format(value,core[values.index(value)]))
            else:
                stylelog.fail('修改核心数量为{0}，Core Enabled 不是{1}，而是{2}'.format(value,core[values.index(value)], i))
                count += 1
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.SET_DOWNCORE_AUTO, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count == 0:
        return True
    else:
        return



#CPU AES
def cpu_aes():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_AES,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    cmd_result=SshLib.execute_command_limit(Sut.OS_SSH,"lscpu | grep aes")

    if len(cmd_result[0])==len(cmd_result[1])==0:
        logging.info('AES关闭，系统下不显示AES')
    else:
        stylelog.fail('AES关闭，系统下显示{0}{1}'.format(cmd_result[0],cmd_result[1]))
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.OPEN_AES, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()

    cmd_result=SshLib.execute_command_limit(Sut.OS_SSH,"lscpu | grep aes")

    cmd_result=cmd_result[0]
    if 'aes' in cmd_result:
        logging.info('AES打开，系统中有aes')
        return True
    else:
        stylelog.fail('AES打开，系统中没有aes')
        return



def cpu_numa():

    numa_valus=SutConfig.Cpu.NUMA_VALUES
    numa_cpu_one=SutConfig.Cpu.CPU_NUMA_ONE
    numa_cpu_two=SutConfig.Cpu.CPU_NUMA_TWO
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    data=SetUpLib.get_data(3)
    if re.findall(r'CPU Count +([0-9])',data)[0]=='1':
        logging.info('单路CPU')
        cpu_count=1
    elif re.findall(r'CPU Count +([0-9])',data)[0]=='2':
        logging.info('双路CPU')
        cpu_count=2
    else:
        stylelog.fail('没有找到CPU数量')
        return
    time.sleep(1)
    for value in numa_valus:
        logging.info('NUMA  {0}测试...........................................'.format(value))
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(2)
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Cpu.LOC_NUMA, 18)
        time.sleep(1)
        assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Cpu.NUMA_NAME],10,'{0}'.format(value))
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_os_from_bm()

        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lscpu | grep NUMA")

        cmd_result = cmd_result[0]
        numa = re.findall(r'NUMA.*([0-9]+)', cmd_result)[0]
        if cpu_count==1:
            if numa==numa_cpu_one[numa_valus.index(value)]:
                logging.info('单路CPU，修改NUMA为{0}，NUMA节点为{1}'.format(value,numa_cpu_one[numa_valus.index(value)]))
            else:
                stylelog.fail('单路CPU，修改NUMA为{0}，NUMA节点不是{1}，而是{2}'.format(value,numa_cpu_one[numa_valus.index(value)],numa))
                count+=1
        elif cpu_count==2:
            if numa==numa_cpu_two[numa_valus.index(value)]:
                logging.info('双路CPU，修改NUMA为{0}，NUMA节点为{1}'.format(value,numa_cpu_two[numa_valus.index(value)]))
            else:
                stylelog.fail('双路CPU，修改NUMA为{0}，NUMA节点不是{1}，而是{2}'.format(value,numa_cpu_two[numa_valus.index(value)],numa))
                count+=1
        if value!=numa_valus[-1]:
            assert SetUpLib.boot_to_setup()
    if count==0:
        return True
    else:
        return



#CPU超频
def cpu_cpb():
    cpu_speed=SutConfig.Cpu.CPU_FREQUENCY_CPB
    assert SetUpLib.boot_to_setup()
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_CPB,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_os_from_bm()
    try_counts = 10
    while try_counts:

        output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+', i)
        if all(speed == cpu_speed[0] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('CPU超频关闭 频率不是{0},是{1}'.format(cpu_speed[0],speeds))
        return
    else:
        logging.info('CPU超频关闭 频率为{0}'.format(cpu_speed[0]))
    assert SetUpLib.boot_to_setup()
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_CPB,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()
    try_counts = 10
    while try_counts:

        output = SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 5 ./monitor_0.1.8')[0]
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+', i)
        if all(speed == cpu_speed[1] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('CPU超频打开 频率不是{0},是{1}'.format(cpu_speed[1],speeds))
        return
    else:
        logging.info('CPU超频打开 频率为{0}'.format(cpu_speed[1]))
    return True