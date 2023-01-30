#coding='utf-8'
import re
import time
import logging
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from InspurStorage.BaseLib import SshLib
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



#CPU超线程
def cpu_hyper_threading():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_HYPER_THREADING,3)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    cmd_result=SetUpLib.execute_command("dmidecode -t 4 | grep 'Thread Count'")
    thread_count_close=re.findall('Thread Count: ([0-9]+)',cmd_result)[0]
    logging.info('超线程关闭，系统Thread Count为{0}'.format(thread_count_close))
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CPU_INFO,5)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('CPU Thread Count +{0}'.format(thread_count_close),10,readline=True):
        logging.info('超线程关闭，setup下Thread Count 与系统下一致')
    else:
        stylelog.fail('setup下Thread Count 与系统下不一致')
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_HYPER_THREADING,10)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    cmd_result=SetUpLib.execute_command("dmidecode -t 4 | grep 'Thread Count'")
    thread_count_open=re.findall('Thread Count: ([0-9]+)',cmd_result)[0]
    logging.info('超线程打开，系统Thread Count为{0}'.format(thread_count_open))
    if int(thread_count_open)==int(thread_count_close)*2:
        logging.info('超线程打开,Thread Count数量是没有打开的2倍')
    else:
        return
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CPU_INFO, 5)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('CPU Thread Count +{0}'.format(thread_count_open),10,readline=True):
        logging.info('超线程打开，setup下Thread Count 与系统下一致')
    else:
        stylelog.fail('setup下Thread Count 与系统下不一致')
        return
    return True



# CPU C-State
def cpu_cstate():
    count = 0
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.OPEN_CSTATE, 18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    cc6open = []
    time.sleep(1)
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
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CLOSE_CSTATE, 18)
    time.sleep(1)
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
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count == 0:
        return True
    else:
        return



# CPU P-State
def cpu_pstate():
    count=0
    cpu_speed=SutConfig.Cpu.CPU_FREQUENCY_PSTATE
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.OPEN_CPB, 18)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_PSTATE,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    result0 = SetUpLib.execute_command('./pstate-set.sh -1 0')
    if result0 == '':
        logging.info('成功切换pstate为P0')
        time.sleep(2)
        output = SetUpLib.execute_command('timeout 5 ./monitor')
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+',i)
        if any(float(speed) >= float(cpu_speed[1]) for speed in speeds):
            logging.info('切换pstate为P0,频率为{}'.format(cpu_speed[0]))
        else:
            stylelog.fail('切换pstate为P0,频率不是{0},频率为{1}'.format(cpu_speed[0],speeds))
            count+=1
    else:
        stylelog.fail('切换pstate为P0失败')
        return
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    result1 = SetUpLib.execute_command('./pstate-set.sh -1 1')
    print(result1)
    if result1 == '':
        logging.info('成功切换pstate为P1')
        time.sleep(2)
        output = SetUpLib.execute_command('timeout 5 ./monitor')
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+',i)
        if any(float(speed) >= float(cpu_speed[2]) for speed in speeds) and all(float(speed) <= float(cpu_speed[1]) for speed in speeds):
            logging.info('切换pstate为P1,频率为{}'.format(cpu_speed[1]))

        else:
            stylelog.fail('切换pstate为P1,频率不是{0},频率为{1}'.format(cpu_speed[1], speeds))
            count += 1
    else:
        stylelog.fail('切换pstate为P1失败')
        return
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    result2 = SetUpLib.execute_command('./pstate-set.sh -1 2')
    if result2 == '':
        logging.info('成功切换pstate为P2')
        time.sleep(2)
        output = SetUpLib.execute_command('timeout 5 ./monitor')
        speeds = []
        for i in output.split('\n'):
            if 'clock:' in i:
                speeds += re.findall('\d.\d+',i)
        if all(float(speed) <= float(cpu_speed[2]) for speed in speeds):
            logging.info('切换pstate为P2,频率为{}'.format(cpu_speed[2]))

        else:
            stylelog.fail('切换pstate为P2,频率不是{0},频率为{1}'.format(cpu_speed[2], speeds))
            count += 1
    else:
        stylelog.fail('切换pstate为P2失败')
        return
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_PSTATE,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_os_from_bm()
    result0 = SetUpLib.execute_command('./pstate-set.sh -1 0')
    if re.search('No such file or directory|没有那个文件或目录',result0):
        logging.info('P-State关闭，无法切换pstate为P0')
    else:
        stylelog.fail('命令输出结果为{0}'.format(result0))
        count+=1
    result1 = SetUpLib.execute_command('./pstate-set.sh -1 1')
    if re.search('No such file or directory|没有那个文件或目录',result1):
        logging.info('P-State关闭，无法切换pstate为P1')
    else:
        stylelog.fail('命令输出结果为{0}'.format(result1))
        count+=1
    result2 = SetUpLib.execute_command('./pstate-set.sh -1 2')
    if re.search('No such file or directory|没有那个文件或目录',result2):
        logging.info('P-State关闭，无法切换pstate为P2')
    else:
        stylelog.fail('命令输出结果为{0}'.format(result2))
        count+=1
    output = SetUpLib.execute_command('timeout 5 ./monitor')
    speeds = []
    for i in output.split('\n'):
        if 'clock:' in i:
            speeds += re.findall('\d.\d+',i)
    if any(float(speed) >= float(cpu_speed[1]) for speed in speeds):
        logging.info('P-State 关闭,频率为p0')

    else:
        stylelog.fail('P-State 关闭,频率不是P0,频率为{}'.format(speeds))
        count += 1
    time.sleep(2)
    SetUpLib.send_data_enter('reboot')
    if count==0:
        return True
    else:
        return



def cpu_numa():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_NUMA,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    SetUpLib.execute_command('cd ACPI/')
    time.sleep(1)
    SetUpLib.execute_command('./acpidump > acpi.dat')
    time.sleep(1)
    SetUpLib.execute_command('./acpixtract -a acpi.dat')
    time.sleep(1)
    SetUpLib.execute_command('./iasl -d apic.dat')
    time.sleep(1)
    result = SetUpLib.execute_command('cat apic.dsl')
    result = re.findall('Local Apic ID : ([0-9A-Za-z]{2})', result)[1:4]
    if any(int(i, 16) & 1 == 1 for i in result):
        logging.info(result)
        logging.info('NUMA 关闭,Local Apic ID 顺序排列')
    else:
        stylelog.fail('NUMA 关闭,Local Apic ID 不是顺序排列，是{}'.format(result))
        SetUpLib.send_data_enter('reboot')
        return
    SetUpLib.send_data_enter('reboot')
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_NUMA,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    SetUpLib.execute_command('cd ACPI/')
    time.sleep(1)
    SetUpLib.execute_command('./acpidump > acpi.dat')
    time.sleep(1)
    SetUpLib.execute_command('./acpixtract -a acpi.dat')
    time.sleep(1)
    SetUpLib.execute_command('./iasl -d apic.dat')
    time.sleep(1)
    result=SetUpLib.execute_command('cat apic.dsl')
    result=re.findall('Local Apic ID : ([0-9A-Za-z]{2})',result)[1:4]
    if all(int(i, 16) & 1 == 0 for i in result):
        logging.info(result)
        logging.info('打开NUMA，Local Apic ID 偶数排列')
    else:
        stylelog.fail('打开NUMA，Local Apic ID 不是偶数排列,是{}'.format(result))
        SetUpLib.send_data_enter('reboot')
        return
    SetUpLib.send_data_enter('reboot')
    time.sleep(3)
    return True



#CPU超频
def cpu_cpb():
    cpu_speed=SutConfig.Cpu.CPU_FREQUENCY_CPB
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.CLOSE_CPB,18)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    assert SetUpLib.boot_os_from_bm()
    output = SetUpLib.execute_command('timeout 5 ./monitor')
    speeds = []
    for i in output.split('\n'):
        if 'clock:' in i:
            speeds += re.findall('\d.\d+',i)
    if all(float(speed) <= float(cpu_speed) for speed in speeds):
        logging.info('CPU超频关闭 频率都小于{0}'.format(cpu_speed))
    else:
        stylelog.fail('CPU超频关闭 频率超过{0},是{1}'.format(cpu_speed, speeds))
        return

    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    assert SetUpLib.boot_to_setup()
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.OPEN_CPB,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    output = SetUpLib.execute_command('timeout 5 ./monitor')
    speeds = []
    for i in output.split('\n'):
        if 'clock:' in i:
            speeds += re.findall('\d.\d+',i)
    if any(float(speed) >= float(cpu_speed) for speed in speeds):
        logging.info('CPU超频打开 频率超过{0}'.format(cpu_speed))
    else:
        stylelog.fail('CPU超频打开 频率都小于{0}'.format(cpu_speed))
        return
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    return True