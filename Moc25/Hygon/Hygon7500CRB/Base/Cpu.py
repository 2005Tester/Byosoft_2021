#coding='utf-8'
import re
import time
import logging
from Hygon7500CRB.BaseLib import BmcLib,SetUpLib
from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig, Sut01Config
from Hygon7500CRB.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



#CPU信息
def cpu_information():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Msg.CPU_INFO, 7)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(1)
    cpu_core=re.findall(r'Number Of Processors *?(\d{1,2}) Core',data)
    cpu_thread = re.findall(r'Number Of Processors *?\d{1,2} Core\(s\) / (\d{1,2}) Thread', data)
    cpu_frequency=re.findall(r'CPU Speed *?(\d{4}).*?MHz',data)
    assert SetUpLib.boot_os_from_bm()
    while True:
        core_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Count'")
        if core_result:
            break
    linux_cpu_core=re.findall(r'Core Count: (\d{1,2})',core_result[0])
    if cpu_core[0]==linux_cpu_core[0]:
        logging.info('CPU核数验证成功')
    else:
        stylelog.fail('CPU核数验证失败,setup下CPU频率{0}，Linux下CPU频率{1}'.format(cpu_core,linux_cpu_core))
        count+=1
    while True:
        thread_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4|grep 'Thread Count'")
        if thread_result:
            break
    linux_cpu_thread=re.findall(r'Thread Count: (\d{2})',thread_result[0])
    if cpu_thread[0]==linux_cpu_thread[0]:
        logging.info('CPU线程数验证成功')
    else:
        stylelog.fail('CPU线程数验证失败,setup下CPU线程数{0}，Linux下CPU线程数{1}'.format(cpu_thread,linux_cpu_thread))
        count+=1
    while True:
        frequency_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4| grep 'Current Speed'")
        if frequency_result:
            break
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
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_STM_DISABLED,5)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Thread Count'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]

    thread_count_close=re.findall('Thread Count: ([0-9]+)',cmd_result)[0]

    logging.info('超线程关闭，系统Thread Count为{0}'.format(thread_count_close))
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Msg.CPU_INFO, 7)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    if SetUpLib.wait_message('Core\(s\) / {0} Thread'.format(thread_count_close),10):
        logging.info('超线程关闭，setup下Thread Count 与系统下一致')
    else:
        stylelog.fail('setup下Thread Count 与系统下不一致')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_STM_ENABLED,5)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Thread Count'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    thread_count_open=re.findall('Thread Count: ([0-9]+)',cmd_result)[0]
    logging.info('超线程打开，系统Thread Count为{0}'.format(thread_count_open))
    if int(thread_count_open)==int(thread_count_close)*2:
        logging.info('超线程打开,Thread Count数量是没有打开的2倍')
    else:
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Msg.CPU_INFO, 7)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Core\(s\) / {0} Thread'.format(thread_count_open),10):
        logging.info('超线程打开，setup下Thread Count 与系统下一致')
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
    else:
        stylelog.fail('setup下Thread Count 与系统下不一致')
        return
    return True



# CPU C-State
def cpu_cstate():
    cpu_speed=Sut01Config.Msg.CPU_FREQUENCY_CSTATE
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_CSTATE_ENABLED,20)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    try_counts = 10
    while try_counts:
        while True:
            output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
            if output:
                break
        speeds = []
        for i in output:
            if 'clock:' in i:
                speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
        if all(speed == cpu_speed[0] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('cstate打开，core 频率不是{0}'.format(cpu_speed[0]))
        return
    else:
        logging.info('cstate打开，core 频率为{0}'.format(cpu_speed[0]))
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_CSTATE_DISABLED,20)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    try_counts = 10
    while try_counts:
        while True:
            output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
            if output:
                break
        speeds = []
        for i in output:
            if 'clock:' in i:
                speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
        if all(speed == cpu_speed[1] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('cstate关闭，core 频率不是{0}'.format(cpu_speed[1]))
        return
    else:
        logging.info('cstate关闭，core 频率为{0}'.format(cpu_speed[1]))
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_CSTATE_AUTO,20)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
    return True



# CPU P-State
def cpu_pstate():
    cpu_speed=Sut01Config.Msg.CPU_FREQUENCY_PSTATE
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_PSTATE_DISABLED,10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()
    while True:
        result0 = SshLib.execute_command(Sut.OS_SSH, './pstate-set.sh -1 0')
        if result0:
            break
    if re.search('No such file or directory|没有那个文件或目录',result0[1]):
        logging.info('P-State关闭，无法切换pstate为P0')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result0[0], result0[1]))
        return
    while True:
        result1 = SshLib.execute_command(Sut.OS_SSH, './pstate-set.sh -1 1')
        if result1:
            break
    if re.search('No such file or directory|没有那个文件或目录',result1[1]):
        logging.info('P-State关闭，无法切换pstate为P1')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result1[0], result1[1]))
        return
    while True:
        result2 = SshLib.execute_command(Sut.OS_SSH, './pstate-set.sh -1 2')
        if result2:
            break
    if re.search('No such file or directory|没有那个文件或目录',result2[1]):
        logging.info('P-State关闭，无法切换pstate为P2')
    else:
        stylelog.fail('命令输出结果为{0}，{1}'.format(result2[0], result2[1]))
        return
    try_counts = 10
    while try_counts:
        while True:
            output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
            if output:
                break
        speeds = []
        for i in output:
            if 'clock:' in i:
                speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
        if any(speed == cpu_speed[0] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('高性能模式下core 频率不是{0}'.format(cpu_speed[0]))
        return
    else:
        logging.info('高性能模式下core 频率为{0}'.format(cpu_speed[0]))

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_PSTATE_ENABLED,10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    assert SetUpLib.boot_os_from_bm()
    while True:
        result0 = SshLib.execute_command(Sut.OS_SSH, './pstate-set.sh -1 0')
        if result0:
            break
    if len(result0[0]) == 0 and len(result0[1]) == 0:
        logging.info('成功切换pstate为P0')
        time.sleep(2)
        try_counts = 10
        while try_counts:
            while True:
                output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
                if output:
                    break
            speeds = []
            for i in output:
                if 'clock:' in i:
                    speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
            if all(speed == cpu_speed[0] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('P0下core 频率不是{0}'.format(cpu_speed[0]))
            return
        else:
            logging.info('P0下core 频率为{0}'.format(cpu_speed[0]))

    else:
        stylelog.fail('切换pstate为P0失败')
        return
    while True:
        result1 = SshLib.execute_command(Sut.OS_SSH, './pstate-set.sh -1 1')
        if result1:
            break
    if len(result1[0]) == 0 and len(result1[1]) == 0:
        logging.info('成功切换pstate为P1')
        time.sleep(2)
        try_counts = 10
        while try_counts:
            while True:
                output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
                break
            speeds = []
            for i in output:
                if 'clock:' in i:
                    speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
            if all(speed == cpu_speed[1] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('切换pstate为P1 频率不是{0}'.format(cpu_speed[1]))
            return
        else:
            logging.info('切换pstate为P1 频率为{0}'.format(cpu_speed[1]))
    else:
        stylelog.fail('切换pstate为P1失败')
        return
    while True:
        result2 = SshLib.execute_command(Sut.OS_SSH, './pstate-set.sh -1 2')
        if result2:
            break
    if len(result2[0]) == 0 and len(result2[1]) == 0:
        logging.info('成功切换pstate为P2')
        time.sleep(2)
        try_counts = 10
        while try_counts:
            while True:
                output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
                break
            speeds = []
            for i in output:
                if 'clock:' in i:
                    speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
            if all(speed == cpu_speed[2] for speed in speeds):
                break
            else:
                try_counts -= 1
        if try_counts == 0:
            stylelog.fail('切换pstate为P2 频率不是{0}'.format(cpu_speed[2]))
            return
        else:
            logging.info('切换pstate为P2 频率为{0}'.format(cpu_speed[2]))
    else:
        stylelog.fail('切换pstate为P2失败')
        return
    return True



#CPU降核
def cpu_downcore_control():
    core=Sut01Config.Msg.CPU_DOWNCORE_CORE
    count=0
    assert SetUpLib.boot_to_setup()
    logging.info('1+1组合测试...........................................................')
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.HYGON_CBS],20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN,['Downcore control'],Key.UP,'TWO \(1 \+ 1\)',9)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Enabled'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    core_enabled=re.findall(r'Core Enabled: +([0-9]+)',cmd_result)
    for i in core_enabled:
        if i==core[0]:
            logging.info('修改核心数量为1+1，Core Enabled 为{0}'.format(core[0]))
        else:
            stylelog.fail('修改核心数量为1+1，Core Enabled 不是{0}，而是{1}'.format(core[0],i))
            count+=1
    assert SetUpLib.boot_to_setup()
    logging.info('2+0组合测试...........................................................')
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HYGON_CBS], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN, ['Downcore control'], Key.DOWN, 'TWO \(2 \+ 0\)', 9)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Enabled'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    core_enabled=re.findall(r'Core Enabled: +([0-9]+)',cmd_result)
    for i in core_enabled:
        if i==core[1]:
            logging.info('修改核心数量为2+0，Core Enabled 为{0}'.format(core[1]))
        else:
            stylelog.fail('修改核心数量为2+0，Core Enabled 不是{0}，而是{1}'.format(core[1],i))
            count+=1
    assert SetUpLib.boot_to_setup()
    logging.info('3+0组合测试...........................................................')
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HYGON_CBS], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN, ['Downcore control'], Key.DOWN, 'THREE \(3 \+ 0\)', 9)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Enabled'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    core_enabled=re.findall(r'Core Enabled: +([0-9]+)',cmd_result)
    for i in core_enabled:
        if i==core[2]:
            logging.info('修改核心数量为3+0，Core Enabled 为{0}'.format(core[2]))
        else:
            stylelog.fail('修改核心数量为3+0，Core Enabled 不是{0}，而是{1}'.format(core[2],i))
            count+=1
    assert SetUpLib.boot_to_setup()
    logging.info('2+2组合测试...........................................................')
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HYGON_CBS], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN, ['Downcore control'], Key.DOWN, 'FOUR \(2 \+ 2\)', 9)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Enabled'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    core_enabled=re.findall(r'Core Enabled: +([0-9]+)',cmd_result)
    for i in core_enabled:
        if i==core[3]:
            logging.info('修改核心数量为2+2，Core Enabled 为{0}'.format(core[3]))
        else:
            stylelog.fail('修改核心数量为2+2，Core Enabled 不是{0}，而是{1}'.format(core[3],i))
            count+=1
    assert SetUpLib.boot_to_setup()
    logging.info('4+0组合测试...........................................................')
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HYGON_CBS], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN, ['Downcore control'], Key.DOWN, 'FOUR \(4 \+ 0\)', 9)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Enabled'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    core_enabled=re.findall(r'Core Enabled: +([0-9]+)',cmd_result)
    for i in core_enabled:
        if i==core[4]:
            logging.info('修改核心数量为4+0，Core Enabled 为{0}'.format(core[4]))
        else:
            stylelog.fail('修改核心数量为4+0，Core Enabled 不是{0}，而是{1}'.format(core[4],i))
            count+=1
    assert SetUpLib.boot_to_setup()
    logging.info('3+3组合测试...........................................................')
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HYGON_CBS], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN, ['Downcore control'], Key.DOWN, 'SIX \(3 \+ 3\)', 9)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result=SshLib.execute_command(Sut.OS_SSH,"dmidecode -t 4 | grep 'Core Enabled'")
        if cmd_result:
            break
    cmd_result=cmd_result[0]
    core_enabled=re.findall(r'Core Enabled: +([0-9]+)',cmd_result)
    for i in core_enabled:
        if i==core[5]:
            logging.info('修改核心数量为3+3，Core Enabled 为{0}'.format(core[5]))
        else:
            stylelog.fail('修改核心数量为3+3，Core Enabled 不是{0}，而是{1}'.format(core[5],i))
            count+=1
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(Sut01Config.Msg.PAGE_ADVANCED)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.HYGON_CBS], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Moksha Common Options'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Core/Thread Enablement'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN, ['Agree'], 20)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.select_option_value(Key.DOWN, ['Downcore control'], Key.DOWN, 'Auto', 9)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    if count==0:
        return True
    else:
        return



#CPU超频
def cpu_cpb():
    cpu_speed=Sut01Config.Msg.CPU_FREQUENCY_CPB
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_CPB_DISABLED,20)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    try_counts = 10
    while try_counts:
        while True:
            output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
            if output:
                break
        speeds = []
        for i in output:
            if 'clock:' in i:
                speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
        if all(speed == cpu_speed[0] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('CPU超频关闭 频率不是{0}'.format(cpu_speed[0]))
        return
    else:
        logging.info('CPU超频关闭 频率为{0}'.format(cpu_speed[0]))
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_CPB_AUTO,20)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    try_counts = 10
    while try_counts:
        while True:
            output = SshLib.execute_command1(Sut.OS_SSH, './monitor_0.1.8', 32)
            if output:
                break
        speeds = []
        for i in output:
            if 'clock:' in i:
                speeds += i.replace('clock:        ', '').replace('  \n', '').split('   ')
        if all(speed == cpu_speed[1] for speed in speeds):
            break
        else:
            try_counts -= 1
    if try_counts == 0:
        stylelog.fail('CPU超频打开 频率不是{0}'.format(cpu_speed[1]))
        return
    else:
        logging.info('CPU超频打开 频率为{0}'.format(cpu_speed[1]))
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_CSTATE_DISABLED,20)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
    return True



def cpu_numa():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_NUMA_DISABLED,15)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        output = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep NUMA')
        if output:
            break
    output = output[0]
    if 'No NUMA configuration found' in output:
        logging.info('NUMA关闭成功')
    else:
        stylelog.fail('NUMA关闭失败')
        return
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Cpu.SET_NUMA_ENABLED,15)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    while True:
        output = SshLib.execute_command(Sut.OS_SSH, 'dmesg | grep NUMA')
        if output:
            break
    output = output[0]
    if 'No NUMA configuration found' not in output:
        logging.info('NUMA打开成功')
        return True
    else:
        stylelog.fail('NUMA打开失败')
        return