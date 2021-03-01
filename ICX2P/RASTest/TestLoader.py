import sys
import os
import time
import win32api
import shutil
import subprocess
# import serial.tools.list_ports as list_ports
from functools import wraps

local_path = os.path.dirname(sys.argv[0])
sys.path.append(os.path.abspath(os.path.join(local_path, "../..")))
from ICX2P.RASTest.RasConfig import *
import Common.Unitool as Setup
import Common.ssh as ssh

global ei, sv, mc, ras, log, nolog, itp, logcustom
globals()["FLAG"] = None
globals()["CurrentConfig"] = None

os_ssh = Setup.SshUnitool(OS_IP, OS_USER, OS_PW, UNI_PATH)
bmc = ssh.SshConnection(BMC_IP, BMC_USER, BMC_PW)

"""
注错函数
"""


def excmd(cmd, echo=True, halt=True, go=True, delay=0):
    result = None
    exc_list = ["=", "show(", "showsearch("]
    if "sv" in cmd:
        sv.refresh()
    if "ei.inj" in cmd:
        logcustom('>>> ei.resetInjectorLockCheck()', "icyan")
        ei.resetInjectorLockCheck()
    if halt:
        itp.halt()
    if echo:
        logcustom('>>> {}'.format(cmd), "icyan", "magenta")
    if any(ex in cmd for ex in exc_list):
        exec(cmd, globals())
    else:
        result = eval(cmd, globals())
    if go:
        itp.go()
    if (delay > 0) and isinstance(delay, int):
        timer(delay)
    return result


def inj_mem(count=1, dev=1, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, rank=Loc.rank, bank_group=Loc.bg, bank=Loc.ba, errType="ce", addr=None, delay=Delay.mem):
    if errType == "uce":
        excmd(Cmd.ei_dev.format(dev, 2, 3, 4))
    if errType == "ce":
        excmd(Cmd.ei_dev.format(dev, 2, 3, 0))
    if addr:
        argvs = "addr={}, errType={}".format(hex(addr), repr(errType))
        for i in range(count):
            excmd(Cmd.inj_mem.format(argvs), delay=delay)
        return
    for i in range(count):
        argvs = "socket={}, channel={}, dimm={}, rank={}, bank_group={}, bank={}, errType={}".format(socket, channel, dimm, rank, bank_group, bank, repr(errType))
        excmd(Cmd.inj_mem.format(argvs), delay=delay)


def inj_pcie(count=1, socket=Loc.psocket, port=Loc.pcie_port, errType="ce", delay=3):
    for i in range(count):
        excmd(Cmd.inj_pcie.format(socket, repr(port), repr(errType)), delay=delay)


def inj_upi(count=1, socket=Loc.usocket, port=Loc.upi_port, num_crcs=1, laneNum='random', delay=3):
    if num_crcs == 0:
        excmd(Cmd.inj_upi.format(socket, port, num_crcs, repr(laneNum), delay=Delay.caterr))
        return
    for i in range(count):
        excmd(Cmd.inj_upi.format(socket, port, num_crcs, repr(laneNum)), delay=delay)


def inj_cap(count=1, socket=Loc.msocket, channel=Loc.ch, delay=3):
    for i in range(count):
        excmd(Cmd.inj_cap.format(socket, channel), delay=delay)


def inj_3s(socket=0, delay=Delay.caterr):
    win32api.keybd_event(89, 0, 0, 0)  # 键入 y
    win32api.keybd_event(13, 0, 0, 0)  # 键入 Enter
    excmd(Cmd.inj_3s.format(socket), delay=delay)


# 获取VLS Buddy的位置
def get_buddy(region=0):
    rank = int(excmd(Cmd.buddy_rank, echo=False))
    dimm = 0
    if rank >= Sys.MaxRank:
        dimm = 1
    bank_group = int(excmd(Cmd.buddy_bg.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    bank = int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    region_size = int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    return dimm, rank, bank_group, bank, region_size


# 延时提示
def timer(count, echo=True):
    if echo:
        logcustom('Wait {} seconds for process complete...'.format(count), "icyan")
    time.sleep(count)


# 单个串口自动检测端口，多个串口使用Config定义的默认端口
# def serial_port():
#     port_list = list(list_ports.comports())
#     if len(port_list) == 1:
#         return list(port_list[0])[0]
#     if len(port_list) <= 0:
#         logcustom("No serial port found!", "ired")
#         return
#     return COM


# 加载测试Case
def load_scripts(file_name="Testcase", path=local_path):
    """
    加载文件名为 "Testcase" 开头的脚本为全局变量
    """
    tc_list = [tc for tc in os.listdir(path) if file_name in tc]
    for t in tc_list:
        with open(os.path.join(local_path, t), "rb") as f:
            exec(f.read(), globals())


# 装饰器, 修改BIOS设置
def bios_setting(name):
    def setting_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            global CurrentConfig
            if name == CurrentConfig:
                return func(*args, **kwargs)
            logcustom("BIOS Load Default!", "icyan")  # 每次修改配置前先恢复默认
            if bmc.login():
                bmc.interaction(["ipmcset -d clearcmos\n", "Y\n"], ["continue", "successfully"])
                force_power_cycle(bmc_ssh=bmc)
                time.sleep(30)
                ping_sut()
                logcustom('Set BIOS config for "DFX"...', "icyan")
                os_ssh.set_config(Bios.DFX)
            if name == "Default":  # 如果输入参数为Default则通过BMC下命令LoadDefault
                force_power_cycle(bmc_ssh=bmc)
                time.sleep(30)
                ping_sut()
                CurrentConfig = name
                return func(*args, **kwargs)
            logcustom('Set BIOS Config to "{}"...'.format(name), "icyan")
            os_ssh.set_config(getattr(Bios, name))
            force_power_cycle(bmc_ssh=bmc)
            time.sleep(30)
            ping_sut()
            CurrentConfig = name
            return func(*args, **kwargs)
        return wrapped_function
    return setting_decorator


def force_power_cycle(bmc_ssh=bmc):
    logcustom("BMC Force Power Cycle...", "icyan")
    cmd_powercycle = 'ipmcset -d frucontrol -v 2\n'
    cmd_confirm = 'Y\n'
    rtn_powercycle = "Do you want to continue"
    rtn_confirm = "successfully."
    if bmc_ssh.login():
        return bmc_ssh.interaction([cmd_powercycle, cmd_confirm], [rtn_powercycle, rtn_confirm])


def ping_sut(timeout=BOOT_TIMEOUT):
    logcustom("Ping OS IP Address: {} ...".format(OS_IP), "icyan")
    ping_cmd = 'ping {0}'.format(OS_IP)
    start_time = time.time()
    reset_flag = 0
    while True:
        p = subprocess.Popen(args=ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        if 'TTL=' in stdoutput.decode('gbk'):
            logcustom("SUT is Online Now !", "igreen")
            return True
        if (time_spent > timeout) and (reset_flag == 0):
            logcustom("Lost SUT for {} seconds, force reset...".format(time_spent), "ired")
            force_power_cycle(bmc_ssh=bmc)
            bmc.close_session()
            reset_flag = 1
            continue
        if (time_spent > timeout*2) and (reset_flag == 1):
            logcustom("Lost SUT for {} seconds, please check the OS ip".format(time_spent), "ired")
            return False


# BMC一键收集
def bmc_dump(ssh, path, name):
    cmd_diag = "ipmcget -d diaginfo"
    ssh.login()
    sftp = ssh.ssh_client.open_sftp()
    files = sftp.listdir("/tmp")
    bin_files = [b for b in files if ".bin" in b]
    if bin_files:
        for bi in bin_files:
            sftp.remove(bi)
            logcustom("Remove {}!".format(bi), "icyan")
    logcustom("Start BMC dump, Please wait...", "icyan")
    if ssh.execute_command(cmd_diag):  # default close session, re-open in next step
        logcustom("Dump finished, Copy to folder:", "icyan")
        logcustom(path, "icyan")
        sftp.get("/tmp/dump_info.tar.gz", "{}/{} dump_info.tar.gz".format(path, name))
        logcustom("Copy dump log completed!", "igreen")
        ssh.close_session()
        return True


def check_info(cmd, testcase=None, logname="os.log"):
    rcv = os_ssh.exec_cmds(["{}\n".format(cmd)])[0][2]
    if testcase and logname:
        test_dir = os.path.join(os.path.join(os.getcwd(), FLAG), testcase)
        with open(os.path.join(test_dir, logname), "a") as tlog:
            tlog.write(rcv)
    return rcv


def run_one(tc_name, bmc):
    """
    输入参数格式为 RasFeature.Testcase
    一次运行一个Case， BIOS配置以RasFeature命名
    """
    global FLAG, CurrentConfig
    now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    cwd = os.path.join(os.path.join(os.getcwd(), FLAG), tc_name)
    log_file = os.path.join(cwd, "{} Cscripts_{}.log".format(tc_name, now))  # Cscript log
    if not os.path.exists(cwd):
        os.makedirs(cwd)
    log(log_file)
    logcustom("Start {} Test:".format(tc_name), "icyan")
    try:
        sv.refresh()
        exec("{}()".format(tc_name))  # 执行测试Case
        bmc_dump(bmc, cwd, tc_name)  # BMC一键收集
        force_power_cycle(bmc_ssh=bmc)
        time.sleep(30)
        ping_sut()
        nolog()
    except Exception as e:
        logcustom("[Exception]: {}".format(e), "ired")
        logcustom("{} Test Error !".format(tc_name), "ired")
        force_power_cycle(bmc_ssh=bmc)
        time.sleep(30)
        ping_sut()
        logcustom("Boot to OS successfully!", "igreen")
        nolog()
        fail_path = os.path.join(os.path.join(os.getcwd(), FLAG), "Test_Error")
        if not os.path.exists(fail_path):
            os.makedirs(fail_path)
        if os.path.exists(os.path.join(fail_path, tc_name)):
            shutil.rmtree(os.path.join(fail_path, tc_name))
        shutil.move(cwd, fail_path)
        pass


def start_test():
    """
    1. 直接指定Testcase
    2. 指定Func，测试所有相关Case
    """
    global FLAG
    if not os.path.isfile(os.path.join(local_path, "_temp")):
        logcustom('Please confirm the "_temp" file exist ！', "ired")
        return
    with open(os.path.join(local_path, "_temp"), "r") as item:
        lines = item.readlines()
        FLAG = lines[0].strip()
        feature = [fea.strip() for fea in lines[1:]]
    test_dir = os.path.join(os.getcwd(), FLAG)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    if bmc.login():
        logcustom("BMC Login Successful.", "igreen")
        bmc.interaction(["maint_debug_cli\n", "attach diag\n", "dump_state 1\n", "bye\n"], ["%", "Success", "Success", "Byebye"])
    logcustom("FDM Log Enabled Pass.", "igreen")
    ping_sut()
    for func in feature:
        # 单个Case测试
        if TC_ID in func:
            if func in os.listdir(test_dir):
                logcustom("Attention: [{}] is already tested, skipped.".format(func), "iyellow")
                continue
            ping_sut()
            run_one(func, bmc)
            continue

        # 按照TestList定义的集合测试
        tc_list = [tc for tc in getattr(TestList, func)]
        for case in tc_list:
            if case in os.listdir(test_dir):
                logcustom("Attention: [{}] is already tested, skipped.".format(case), "iyellow")
                continue
            ping_sut()
            run_one(case, bmc)


if __name__ == "__main__":
    load_scripts("Testcase")
    start_test()

