# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
CPU case 编号:301~400
'''


@core.test_case(('301', '[TC301]CPU Information', 'CPU 核数，线程数，频率'))
def cpu_information():
    """
    Name:   检查CPU核数，线程数，频率

    Steps:  1.启动到SetUp,抓取CPU Info下的CPU核数，线程数，频率
            2.启动到OS,对比type4中核数,线程数,频率与SetUp中是否一致

    Result: 2.一致
    """

    try:
        assert Cpu.cpu_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('302', '[TC302]CPU Frequency', 'CPU频率'))
def cpu_frequency(oem=False):
    """
    Name:   修改CPU频率

    Steps:  遍历所有的CPU频率
            1.进入SetUp，修改CPU频率
            2.进入OS，对比type4中CPU频率和修改的是否一致

    Result: 2.一致
    """
    try:
        assert Cpu.cpu_frequency(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('303', '[TC303]Hyper Threading test', 'CPU超线程'))
def cpu_hyper_threading(oem=False):
    """
    Name:   CPU超线程

    Steps:  1.进入SetUp，关闭超线程
            2.启动到SetUp，记录当前线程数，启动到OS，记录type4中线程数，检查两者是否相等
            3.进入SetUp，打开超线程
            4.重复步骤2
            5.检查打开超线程后的线程数是否是关闭的两倍

    Result: 2.相等
            4.相等
            5.检查打开超线程后的线程数是关闭的两倍
    """
    try:
        assert Cpu.cpu_hyper_threading(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('304', '[TC304]CPU C-State', 'CPU C-State'))
def cpu_cstate(oem=False):
    """
    Name:   CPU C-State

    Steps:  1.进入SetUp,打开C-State
            2.进入OS，运行工具'SMUToolSuite'，查看CC6的值
            3.进入SetUp,关闭C-State
            4.进入OS，运行工具'SMUToolSuite',查看CC6的值

    Result: 2.CC6的值不为0
            4.CC6的值全为0
    """
    try:
        assert Cpu.cpu_cstate(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('305', '[TC305]CPU P-State', 'CPU P-State'))
def cpu_pstate(oem=False):
    """
    Name:   CPU P-State

    Steps:  1.进入SetUp设置CPU P-State为P0
            2.进入OS，检查工具'pstate-set.sh'是否可以切换P0,P1,P2及各状态CPU的频率
            3.进入SetUp设置CPU P-State为P0+P1
            4.重复步骤2
            5.进入SetUp设置CPU P-State为P0+P1+P2
            6.重复步骤2

    Result: 2.不可以切换P0,P1,P2，CPU频率正确
            4.可以切换P0,P1，不可以切换P2，P0,P1下频率正确
            6.可以切换P0,P1,P2，且频率正确

    """

    try:
        assert Cpu.cpu_pstate(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('307', '[TC307]CPU Downcore Control', 'CPU Downcore Control'))
def cpu_downcore_control():
    """
    Name:   CPU 降核

    Steps:  遍历所有的核数
            1.进入SetUp，修改CPU核数
            2.进入OS，查看type4中是否为修改的核数

    Result: 2.type4中核数等于修改的核数

    """
    try:
        assert Cpu.cpu_downcore_control()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('308', '[TC308]CPU AES', 'CPU AES'))
def cpu_aes(oem=False):
    """
    Name:   CPU AES

    Steps:  1.SetUp关闭CPU AES
            2.进入OS，输入命令'lscpu | grep aes',检查是否有'aes'字样
            3.SetUp打开CPU AES
            4.重复步骤2

    Result: 2.没有'aes'字样
            4.有'aes'字样
    """
    try:
        assert Cpu.cpu_aes(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('310', '[TC310]CPU NUMA', 'CPU NUMA'))
def cpu_numa(oem=False):
    """
    Name:   CPU NUMA
    Condition:  满插内存

    Steps:  遍历所有选项
            1.进入SetUp修改NUMA值
            2.进入OS，输入命令'lscpu | grep NUMA'，检查NUMA节点是否正确

    Result: 2.选项对应的NUMA节点显示正确

    """
    try:
        assert Cpu.cpu_numa(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('311', '[TC311]CPU CPB', 'CPU 超频'))
def cpu_cpb(oem=False):
    """
    Name:   CPU 超频

    Steps:  遍历所有CPU频率
            1.SetUp设置CPU频率为指定值,关闭超频，进入OS检查CPU频率
            2.SetUp下打开超频，进入OS检查CPU频率

    Result  1.CPU频率为设定的值
            2.CPU频率为能达到的最大值

    """
    try:
        assert Cpu.cpu_cpb(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('312', '[TC312]CPU Performance', 'CPU 性能模式'))
def cpu_performance(oem=False):
    """
    Name:   CPU性能模式

    Steps:  遍历所有模式
            1.SetUp下设定指定的性能模式
            2.检查超频是否隐藏，OS下CPU频率是否为该模式对应的频率

    Result  2.超频自动隐藏，CPU频率正确
    """
    try:
        assert Cpu.cpu_performance(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('313', '[TC313]SMEE 控制', 'SMEE 控制'))
def smee(oem=False):
    """
    Name:   SMEE 控制

    Steps:  遍历所有模式
            1.SetUp下打开SMEE,系统下检查dmesg
            2.SetUp下关闭SMEE,系统下检查dmesg

    Result  1.系统下显示SME
            2.系统下不显示SME
    """
    try:
        assert Cpu.smee(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail