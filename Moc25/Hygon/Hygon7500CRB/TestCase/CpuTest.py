import logging
import time
from batf.Report import ReportGen

from Hygon7500CRB.Config.PlatConfig import Key, Msg
from Hygon7500CRB.BaseLib import BmcLib,SetUpLib
from Hygon7500CRB.Base import Cpu
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


@core.test_case(('305', '[TC305]CPU CPB', 'CPU 超频'))
def cpu_cpb():
    try:
        assert Cpu.cpu_cpb()

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail




@core.test_case(('306','[TC306]CPU Downcore Control','CPU Downcore Control'))
def cpu_downcore_control():

    try:
        assert Cpu.cpu_downcore_control()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail




@core.test_case(('307','[TC307]CPU NUMA','CPU NUMA'))
def cpu_numa():

    try:
        assert Cpu.cpu_numa()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail




# @core.test_case(('308','[TC308]CPU AES','CPU AES'))
# def cpu_aes():
#     try:
#         assert Cpu.cpu_aes()
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#
#




# @core.test_case(('302', '[TC302]CPU Frequency', 'CPU频率'))
# def cpu_frequency():
#     try:
#         assert Cpu.cpu_frequency()
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
