import logging
import time
from batf.Report import ReportGen
from InspurStorage.Config.PlatConfig import Key, Msg
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Base import Cpu
from batf import core



'''
CPU case 编号:301~400
'''



@core.test_case(('301','[TC301]CPU Information','CPU 核数，线程数，频率'))
def cpu_information():
    try:
        assert Cpu.cpu_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('302','[TC302]Hyper Threading test','CPU超线程'))
def cpu_hyper_threading():
    try:
        assert Cpu.cpu_hyper_threading()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('303','[TC303]CPU C-State','CPU C-State'))
def cpu_cstate():
    try:
        assert Cpu.cpu_cstate()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('304','[TC304]CPU P-State','CPU P-State'))
def cpu_pstate():
    try:
        assert Cpu.cpu_pstate()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('305','[TC305]CPU NUMA','CPU NUMA'))
def cpu_numa():
    try:
        assert Cpu.cpu_numa()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('306','[TC306]CPU CPB','CPU 超频'))
def cpu_cpb():
    try:
        assert Cpu.cpu_cpb()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail