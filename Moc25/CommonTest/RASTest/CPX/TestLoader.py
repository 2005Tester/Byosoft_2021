# -*- encoding=utf8 -*-

import re
import sys
import os
import time
import shutil
import subprocess
from functools import wraps
from io import StringIO

local_path = os.path.dirname(sys.argv[0])
sys.path.append(os.path.abspath(os.path.join(local_path, "../..")))
from CommonTest.RASTest.CPX.RasConfig import *
from CommonTest.CommLib.BmcWebRequest import BmcWeb
import platforms.CPX.cpxmc.cpxAddressTranslator as Tran
import batf.Common.Unitool as Setup
from batf.Common import ssh

global ei, sv, mc, ras, log, nolog, itp, logcustom
globals()["FLAG"] = None
globals()["CurrentConfig"] = None

os_ssh = Setup.SshUnitool(OS_IP, OS_USER, OS_PW, UNI_PATH)
bmc_ssh = ssh.SshConnection(BMC_IP, BMC_USER, BMC_PW)
bmc_web = BmcWeb(BMC_IP, BMC_USER, BMC_PW)

"""
注错函数
"""


def excmd(cmd, echo=True, delay=0, _halt=True, _go=True):
    result = ""
    exc_list = ["=", "show(", "showsearch("]  # 不能用eval()的命令
    if "ei.inj" in cmd:
        logcustom('>>> ei.resetInjectorLockCheck()', "icyan")
        ei.resetInjectorLockCheck()
    if _halt:
        while not itp.ishalted():
            itp.halt()
    if echo:
        logcustom('>>> {}'.format(cmd), "icyan", "magenta")
    if any(ex in cmd for ex in exc_list):
        exec(cmd, globals())
    else:
        result = repr(eval(cmd, globals()))
    if _go:
        while itp.ishalted():
            itp.go()
    if delay:
        timer(delay)
    if result.startswith("0x"):
        result = int(result, 16)
    elif result.isdigit():
        result = int(result)
    if echo:
        if isinstance(result, int):
            print(f">>> {hex(result)}")
        elif result.strip() not in ["", "None", "True", "False"]:
            print(f'>>> {result}')
    return result


def dram_addr_trans(socket, mc, ch, dimm, rank, bank_group, bank, row, column, mem_type="ddr4"):
    trans = Tran.TranslationInfo()
    trans.invalidateAddrMap()
    trans.clear()
    trans.socket_id = socket
    trans.mc_id = mc
    trans.channel = ch
    trans.dimm = dimm
    trans.phys_rank = rank
    trans.chip_id = 0
    trans.bank_group = bank_group
    trans.bank = bank
    trans.row = row
    trans.column = column
    Tran.dramAddressToCoreAddress(trans, 2)
    result_addr = trans.subAddrDict.get("ddr").core_addr
    if result_addr == -1:
        logcustom("Dram Adddress Translate Error", "ired")
        return
    return int(result_addr)


#  Inject Mem CE/UCE, count为注错次数
def inj_mem(count=1, dev=1, dev0msk=0x2, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, rank=Loc.rank, bank_group=Loc.bg, bank=Loc.ba, errType="ce", addr=None, delay=Delay.mem):
    dev1msk = 0
    if errType == "uce":
        delay = Delay.mem_uce  # 内存UCE注错后等待3分钟
        dev1msk = 0x4
    dev0msk = hex(dev0msk).strip("0x") if isinstance(dev0msk, int) and dev0msk > 10 else dev0msk
    excmd(Cmd.ei_dev.format(repr(dev), repr(dev0msk), 3, repr(dev1msk)))
    if addr:
        argvs = "addr={}, errType={}".format(hex(addr), repr(errType))
        for i in range(count):
            excmd(Cmd.inj_mem.format(argvs), delay=delay)
        return
    for i in range(count):
        argvs = "socket={}, channel={}, dimm={}, rank={}, bank_group={}, bank={}, errType={}".format(socket, channel, dimm, rank, bank_group, bank, repr(errType))
        excmd(Cmd.inj_mem.format(argvs), delay=delay)


def inj_mem_rc(count=1, dev0=1, dev0msk=0x2, socket=Loc.msocket, channel=Loc.ch, dimm=Loc.dimm, rank=Loc.rank, bank_group=0, bank=0, row=0, column=0, delay=Delay.mem):
    """inject mem error to specific row columns"""
    mc = channel // len(Sys.CHs)
    ch = channel % len(Sys.CHs)
    addr_tran = dram_addr_trans(socket, mc, ch, dimm, rank, bank_group, bank, row, column)
    excmd('ei.sa2da_table({}, {})'.format(hex(addr_tran), hex(addr_tran + 0x100)), echo=True)
    inj_mem(count=count, dev=dev0, dev0msk=dev0msk, addr=addr_tran, errType="ce", delay=delay)


#  Inject PCIE CE/UCE, count为注错次数
def inj_pcie(count=1, socket=Loc.psocket, port=Loc.pcie_port, errType="ce", delay=3):
    for i in range(count):
        excmd(Cmd.inj_pcie.format(socket, repr(port), repr(errType)), delay=delay)


#  Inject UPI CE/UCE, count为注错次数
def inj_upi(count=1, socket=Loc.usocket, port=Loc.upi_port, num_crcs=1, laneNum='random', delay=3):
    if num_crcs==0:
        excmd(Cmd.inj_upi.format(socket, port, num_crcs, repr(laneNum)), delay=Delay.caterr)
        return
    for i in range(count):
        excmd(Cmd.inj_upi.format(socket, port, num_crcs, repr(laneNum)), delay=delay)


#  Inject Mem CMD/Address Parity Error，count为注错次数
def inj_cap(count=1, socket=Loc.msocket, channel=Loc.ch, delay=3):
    for i in range(count):
        excmd(Cmd.inj_cap.format(socket, channel), delay=delay)


#  Inject ThreeStrike Timeout Error
def inj_3s(socket=0, delay=Delay.caterr):
    cmd = Cmd.inj_3s.format(socket)
    logcustom('>>> ei.resetInjectorLockCheck()', "icyan")
    ei.resetInjectorLockCheck()
    logcustom('>>> {}'.format(cmd), "icyan", "magenta")  # 命令显示打印
    stdin = sys.stdin  # 重定向sys.stdio
    sys.stdin = StringIO("y")  # 输入确认键 "y"
    exec(cmd)
    sys.stdin = stdin  # 恢复sys.stdio
    timer(delay)


# 获取VLS Buddy的位置
def get_buddy(region=0):
    rank = int(excmd(Cmd.buddy_rank.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    dimm = 1 if rank >= Sys.MaxRank else 0
    bank_group = int(excmd(Cmd.buddy_bg.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    bank = int(excmd(Cmd.buddy_bank.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    region_size = int(excmd(Cmd.region_size.format(Loc.msocket, Loc.imc, Loc.channel, region), echo=False))
    return dimm, rank, bank_group, bank, region_size


# 延时提示
def timer(count, echo=True):
    if echo:
        logcustom('Wait {} seconds for process complete...'.format(count), "icyan")
    time.sleep(count)


def load_scripts(keyword="Testcase", path=local_path):
    """
    加载测试Case
    :param keyword:     测试case标志 关键字
    :param path:        加载case的文件夹
    :return:            None
    """
    tc_list = [tc for tc in os.listdir(path) if keyword in tc]
    for t in tc_list:
        with open(os.path.join(local_path, t), "rb") as f:
            scripts = re.sub(pattern="from .* import .*", repl="", string=f.read().decode("utf-8"))
            exec(scripts.read(), globals())


# 装饰器, 修改BIOS设置
def bios_setting(name):
    def setting_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            global CurrentConfig
            if name == CurrentConfig:
                return func(*args, **kwargs)
            logcustom("BIOS Load Default!", "icyan")  # 每次修改配置前先恢复默认
            if bmc_ssh.login():
                bmc_ssh.interaction(["ipmcset -d clearcmos\n", "Y\n"], ["continue", "successfully"])
                force_power_cycle(bmc_ssh=bmc_ssh)
                time.sleep(30)
                ping_sut()
                logcustom('Set BIOS config for "DFX"...', "icyan")
                os_ssh.set_config(Bios.DFX)
            if name == "Default":  # 如果输入参数为Default则通过BMC下命令LoadDefault
                force_power_cycle(bmc_ssh=bmc_ssh)
                time.sleep(30)
                ping_sut()
                CurrentConfig = name
                return func(*args, **kwargs)
            logcustom('Set BIOS Config to "{}"...'.format(name), "icyan")
            os_ssh.set_config(getattr(Bios, name))
            force_power_cycle(bmc_ssh=bmc_ssh)
            time.sleep(30)
            ping_sut()
            CurrentConfig = name
            return func(*args, **kwargs)
        return wrapped_function
    return setting_decorator


def set_msp(enable: bool):
    en_cmd = ["raw 0x30 0x92 0xDB 0x07 0x00 0x42 0x01", "raw 0x30 0x92 0xDB 0x07 0x00 0x42 0x05"]
    dis_cmd = ["raw 0x30 0x92 0xDB 0x07 0x00 0x42 0x00", "raw 0x30 0x92 0xDB 0x07 0x00 0x42 0x04"]
    success_flag = "db 07 00"
    ipmi_tool = os.path.abspath(f"{os.path.dirname(sys.argv[0])}/../../Resource/ipmitool/ipmitool.exe")
    ipmicmd, flag = (en_cmd, "enable") if enable else (dis_cmd, "disable")
    failed = 0
    for icmd in ipmicmd:
        p = subprocess.Popen(args=f"{ipmi_tool} -I lanplus -H {BMC_IP} -U {BMC_USER} -P {BMC_PW} {icmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        if success_flag not in stdoutput.decode('gbk'):
            failed += 1
    if failed == 0:
        logcustom(f"ipmitool set msp to '{flag}' successfully", "igreen")
    else:
        logcustom(f"ipmitool set msp to '{flag}' failed: {stdoutput.decode('gbk')}", "ired")
    return failed==0


# 装饰器，ipmi修改msp配置, 测试前开启MSP，测试完成后关闭MSP
def msp_enable(func):
    def wrapper(*args, **kwargs):
        set_msp(enable=True)
        func_return = func(*args, **kwargs)
        set_msp(enable=False)
        return func_return
    return wrapper


def force_power_cycle(bmc_ssh=bmc_ssh):
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
            time.sleep(5)
            return True
        if (time_spent > timeout) and (reset_flag == 0):  # ping超时后重启一次
            logcustom("Lost SUT for {} seconds, force reset...".format(time_spent), "ired")
            force_power_cycle(bmc_ssh=bmc_ssh)
            bmc_ssh.close_session()
            reset_flag = 1
            continue
        if (time_spent > timeout*2) and (reset_flag == 1):
            logcustom("Lost SUT for {} seconds, please check the OS ip".format(time_spent), "ired")
            return False


def time_sync():
    """
    Linux系统和Host时间同步，保证Cscript注错时间和BMC的FDMLOG时间一致
    :return: None
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if os_ssh.open_shell():
        logcustom("OS TimeZone Sync: UTC+8", "iyellow")
        os_ssh.exec_cmds(["timedatectl set-timezone 'Asia/Shanghai'"])
        logcustom("OS DateTime Sync: {}".format(now), "iyellow")
        os_ssh.exec_cmds(["timedatectl set-time '{}'".format(now)])
        os_ssh.exec_cmds(["timedatectl set-local-rtc 1"])
        os_ssh.close_shell()


# BMC一键收集
def bmc_dump(ssh_bmc, path, name):
    """
    BMC一键收集
    :param ssh:     BMC SSH类实例
    :param path:    BMC Dump保存路径
    :param name:    BMC Dump保存文件名
    :return:        一键收集成功则返回True
    """
    cmd_diag = "ipmcget -d diaginfo"
    if not ssh_bmc.login(BMC_IP, BMC_USER, BMC_PW):
        logcustom("BMC login failed", "ired")
        return
    sftp = ssh_bmc.ssh_client.open_sftp()
    files = sftp.listdir("/tmp")
    old_files = [b for b in files if (".bin" in b) or (".tar.gz" in b)]
    if old_files:
        for old in old_files:
            try:
                sftp.remove(old)
                logcustom("Remove {}!".format(old), "icyan")
            except:
                logcustom("Unable to remove '{}'".format(old), "ired")
    logcustom("Start BMC dump, Please wait...", "icyan")
    if ssh_bmc.execute_command(cmd_diag):  # default close session, re-open in next step
        logcustom("Dump finished, Copy to folder:", "icyan")
        logcustom(path, "icyan")
        try:
            sftp.get("/tmp/dump_info.tar.gz", "{}/{} dump_info.tar.gz".format(path, name))
            logcustom("Copy dump log completed!", "igreen")
            sftp.remove("/tmp/dump_info.tar.gz")
        except Exception as e:
            logcustom(f"{e}", "ired")
            return
        finally:
            ssh_bmc.close_session()
        return True


def check_info(cmd, path=None, logname=""):
    """
    系统下输入命令，将结果保存到本地
    :param cmd:     linux命令
    :param path:    本地os_log保存路径
    :param logname: 本地os_log保存文件名
    :return:        执行命令后的打印字符串
    """
    rcv = os_ssh.exec_cmds(["{}\n".format(cmd)])[0][2]
    if path:
        test_dir = os.path.join(os.path.join(os.getcwd(), FLAG), path)
        with open(os.path.join(test_dir, logname+"_os.log"), "a") as tlog:
            tlog.write(rcv)
    return rcv


def run_one(tc_name, ssh_bmc):
    """
    :param tc_name: 测试case的名字
    :param ssh_bmc:     bmc ssh类实例
    :return:
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
        # sv.refresh()
        exec("{}()".format(tc_name))  # 执行测试Case
        bmc_dump(ssh_bmc, cwd, tc_name)  # BMC一键收集
        force_power_cycle(bmc_ssh=ssh_bmc)
        time.sleep(30)
        ping_sut()
        nolog()
    except Exception as e:
        logcustom("[Exception]: {}".format(e), "ired")
        logcustom("{} Test Error !".format(tc_name), "ired")
        force_power_cycle(bmc_ssh=ssh_bmc)
        time.sleep(30)
        ping_sut()
        logcustom("Boot to OS successfully!", "igreen")
        bmc_dump(ssh_bmc, cwd, tc_name)  # BMC一键收集
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

    if bmc_ssh.login():
        logcustom("BMC Login Successful.", "igreen")
        bmc_ssh.interaction(["maint_debug_cli\n", "attach diag\n", "dump_state 1\n", "bye\n"], ["%", "Success", "Success", "Byebye"])
    logcustom("FDM Log Enabled Pass.", "igreen")
    ping_sut()
    time_sync()
    for func in feature:
        # 单个Case测试
        if TC_ID in func:
            if func in os.listdir(test_dir):
                logcustom("Attention: [{}] is already tested, skipped.".format(func), "iyellow")
                continue
            ping_sut()
            run_one(func, bmc_ssh)
            continue

        # 按照TestList定义的集合测试
        tc_list = [tc for tc in getattr(TestList, func)]
        for case in tc_list:
            if case in os.listdir(test_dir):
                logcustom("Attention: [{}] is already tested, skipped.".format(case), "iyellow")
                continue
            ping_sut()
            run_one(case, bmc_ssh)


if __name__ == "__main__":
    load_scripts("Testcase")
    start_test()

