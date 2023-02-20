import os
import re
import time
import logging
from copy import deepcopy
from pathlib import Path
from batf.SutInit import Sut
from batf import SshLib, MiscLib
from SPR4P.Config import SutConfig


def is_power_state(state, retry=1):
    """Confirm current power state is "off" or "on" """
    logging.debug("Check power status...")
    cmd = 'ipmcget -d powerstate'
    state = state.lower()
    support = ["on", "off"]
    if state not in support:
        logging.error(f"state '{state}' not in support list: {support}")
        return False
    for i in range(retry):
        result = SshLib.execute_command(Sut.BMC_SSH, cmd)
        if state.capitalize() in result:
            logging.debug(f'Current power state is {state}')
            return True
        else:
            support_copy = deepcopy(support)
            support_copy.remove(state)
            logging.debug(f'Current power state is {"".join(support_copy)}')
            time.sleep(1)


# power on SUT by BMC command
def power_on():
    logging.info("[BmcLib.power_on]Power on system.")
    cmd_reset = 'ipmcset -d powerstate -v 1\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]

    if is_power_state("on"):
        logging.info("Power status is already on.")
        return True

    for i in range(3):
        SshLib.interaction(Sut.BMC_SSH, cmds, rets, timeout=15, delay=1)
        if is_power_state("on", retry=5):
            return True
    logging.error("BMC power on failed")
    return False


# power off sut by BMC command
def power_off():
    logging.info("[BmcLib.power_off]Power off system - force")
    cmd_reset = 'ipmcset -d powerstate -v 2\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]

    if is_power_state("off"):
        logging.info("Power status is already off.")
        return True

    for i in range(3):
        SshLib.interaction(Sut.BMC_SSH, cmds, rets, timeout=15, delay=1)
        if is_power_state("off", retry=5):
            return True
    logging.error("BMC power off failed")
    return False


def force_system_reset():
    logging.info("[BmcLib] BMC force system reset.")
    cmd_reset = 'ipmcset -d frucontrol -v 0\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if Sut.BMC_SSH.login():
        return Sut.BMC_SSH.interaction(cmds, rets, timeout=30, delay=1)
    else:
        logging.error("BMC force system reset failed")
        return


# Force power cycle by BMC command
def force_power_cycle():
    logging.info("[BmcLib] BMC force power cycle.")
    cmd_powercycle = 'ipmcset -d frucontrol -v 2\n'
    ret_powercycle = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_powercycle, cmd_confirm]
    rets = [ret_powercycle, ret_confirm]
    if is_power_state("off"):
        power_on()
    if Sut.BMC_SSH.login():
        return Sut.BMC_SSH.interaction(cmds, rets, timeout=30, delay=1)
    else:
        logging.error("HY5 Common TC: force power cycle failed")
        return


# Force reset SUT by BMC command
def force_reset():
    logging.info("BMC Force Reset.")
    if is_power_state("on"):
        return force_power_cycle()  # work around to avoid the know issue of V7: Warm reboot IERR
    return power_on()


# clear CMOS by BMC command
def clear_cmos():
    logging.info("Clear CMOS to restore enviroment.")
    cmd_clearcoms = 'ipmcset -d clearcmos\n'
    ret_clearcmos = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_clearcoms, cmd_confirm]
    rets = [ret_clearcmos, ret_confirm]
    if not SshLib.interaction(Sut.BMC_SSH, cmds, rets, timeout=30):
        logging.error("Clear CMOS failed")
        return
    logging.debug("Clear CMOS done")
    return True


# open/close debug message with bmc cmd
def debug_message(enable=True):
    """注意：开启后无法通过clear CMOS关闭，需要重新调用此函数关闭"""
    msg = "Enable" if enable else "Disable"
    value = 1 if enable else 2
    logging.info(f"Set serial debug message to: {msg}")
    cmd1 = f"ipmcset -t maintenance -d biosprint -v {value}\n"
    rtn1 = 'Do you want to continue'
    cmd2 = 'Y\n'
    rtn2 = 'success'
    if not Sut.BMC_SSH.login():
        return
    if not enable:
        logging.info("[Serial Debug Message] -> Disabled")
        return Sut.BMC_SSH.interaction([cmd1], [rtn2], timeout=30)
    logging.info("[Serial Debug Message] -> Enabled")
    return Sut.BMC_SSH.interaction([cmd1, cmd2], [rtn1, rtn2], timeout=30)


def set_boot_dev(dev=None, once=True):
    support = {None: 0, "PXE": 1, "HD": 2, "CD": 5, "BIOS": 6, "USB": "0xF"}
    if dev not in support:
        logging.error(f"Boot Device '{dev}' not in support list: {list(support.keys())}")
        return False
    duration = "once" if once else "permanent"
    set_cmd = f"ipmcset -d bootdevice -v {support[dev]} {duration}"
    return SshLib.interaction(Sut.BMC_SSH, [set_cmd], ["success"], timeout=30)


# Program BIOS flash by BMC command
def program_flash():
    # Program flash procedure: power off->maint mode->attach upgrade ->load bin
    logging.info("[BmcLib.program_flash]Programing flash...")
    cmd_maint_mode = 'maint_debug_cli\n'
    ret_maint_mode = 'Debug Shell'
    cmd_upgrade_mode = 'attach upgrade\n'
    ret_upgrade_mode = 'Success'
    cmd_load = 'load_bios_bin /tmp/rp001.bin\n'
    ret_load = 'load bios succefully'
    cmds = [cmd_maint_mode, cmd_upgrade_mode, cmd_load]
    rets = [ret_maint_mode, ret_upgrade_mode, ret_load]
    if power_off():
        return SshLib.interaction(Sut.BMC_SSH, cmds, rets)


# BMC一键收集
# uncom=True: uncompress the file, return path="path/name" | uncom=False: return file="path/name.tar.gz"
def bmc_dumpinfo(path, name="dump", uncom=False):
    cmd_diag = "ipmcget -d diaginfo"
    SshLib.sftp_remove_file(Sut.BMC_SFTP, ".bin")
    logging.info("Start BMC dump, Please wait...")
    res = SshLib.execute_command(Sut.BMC_SSH, cmd_diag)
    if "successful" not in res:
        logging.info("BMC Dump get error")
        logging.debug(res)
        return
    logging.info(f"Dump finished, Copy to folder: {path}")
    if not os.path.exists(path):
        os.makedirs(path)
    tar_file = os.path.join(path, f"{name}.tar.gz")
    if not SshLib.sftp_download_file(Sut.BMC_SFTP, "/tmp/dump_info.tar.gz", tar_file):
        return
    logging.info("BMC dumpinfo successfully")
    if not uncom:
        return tar_file
    logging.info(f"Uncompress file: {tar_file}")
    return MiscLib.uncompress_targz(tar_file, path)


# 检查当前状态BMC web是否有告警
def bmc_warning_check(ignore: list = None):
    class Result:
        status = None
        message = None
    cmd = "ipmcget -d healthevents"
    res = SshLib.execute_command(Sut.BMC_SSH, cmd)
    if not res:
        logging.error(f'Run cmd "{cmd}" error')
        return
    Result.message = res
    if "System in health state" in res:
        logging.info("[BMC Warning Check] Current system in health state")
        Result.status = True
        return Result

    logging.info("[BMC Warning Check] Alarms/Events detected")
    Result.status = False
    if ignore:
        err_found = []
        for warn_line in res.splitlines()[1:]:
            warn_msg = warn_line.split('|')[-1].strip()
            if any(re.search(ig_msg, warn_msg) for ig_msg in ignore):
                logging.debug(f'Warning ignored: "{warn_msg}"')
                continue
            err_found.append(warn_msg)
        for err in err_found:
            logging.error(f'Warning message: "{err}"')
        if err_found:
            logging.error(f"{len(err_found)} bmc warning messages found")
            Result.status = False
        else:
            Result.status = True
    return Result


# 从BMC读取当前固件版本信息, 返回版本信息为字符串格式
def get_fw_version():
    class BmcInfo:
        BIOS = None
        BMC = None
        CPLD = None
        PRODUCT = None
    cmd = "ipmcget -d v"
    info = SshLib.execute_command(Sut.BMC_SSH, cmd)
    if not info:
        logging.error(f'Cmd "{cmd}" return nothing')
        return
    bios_ver = "".join(re.findall("\nActive\s+BIOS\s+Version:\s+.*?\)([.\d]+)", info))
    BmcInfo.BIOS = bios_ver
    bmc_ver = "".join(re.findall("\nActive\s+iBMC\s+Version:\s+.*?\)([.\d]+)", info))
    BmcInfo.BMC = bmc_ver
    cpld_ver = "".join(re.findall("\nCPLD\s+Version:\s+.*?\)([.\d]+)", info))
    BmcInfo.CPLD = cpld_ver
    product_name = "".join(re.findall("\nProduct\s+Name:\s+.*?(\d+\s+\w+)", info))
    BmcInfo.PRODUCT = product_name
    return BmcInfo


# Enable fdmlog
def enable_fdmlog_dump():
    dump_cmd = ["maint_debug_cli\n", "attach diag\n", "dump_state 6\n"]
    dump_rtn = ["Shell", "Success", "Success"]
    return SshLib.interaction(Sut.BMC_SSH, dump_cmd, dump_rtn, 10)


# 抓取当前KVM屏幕图像，并保存到本地
def capture_kvm_screen(path, name):
    save_screen = SshLib.interaction(Sut.BMC_SSH, ["ipmcset -d printscreen\n"], ["successfully"], 15)
    if not save_screen:
        logging.info("please confirm the KVM is open as share mode, not private mode")
        return
    save_path = "".join(re.findall("Download print screen image to (.+) successfully.", save_screen[1]))
    img_file = os.path.join(path, f"{name}.jpeg")
    if SshLib.sftp_download_file(Sut.BMC_SFTP, save_path, img_file):
        logging.info(f"Dump current kvm screen success, save image {img_file}")
        return img_file


# Set fan mode by bmc
def set_fan_level():
    logging.info("[BmcLib] Set fan mode.")
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    ret_fan_manual_mode = 'Set fan mode successfully'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    ret_fan_40 = 'Set fan level successfully'
    cmds = [cmd_fan_manual_mode, cmd_fan_40]
    rets = [ret_fan_manual_mode, ret_fan_40]
    return SshLib.interaction(Sut.BMC_SSH, cmds, rets, timeout=30)


# Check whether current boot type is UEFI via BMC redfish
def is_uefi_boot():
    logging.info("[BmcLib] Check if current boot as UEFI mode.")
    try:
        boot_type = Sut.BMC_RFISH.get_info(Sut.BMC_RFISH.SYSTEM)["Boot"]["BootSourceOverrideMode"]
        logging.info(f"Current boot type: {boot_type}")
        if boot_type == "UEFI":
            return True
    except Exception as e:
        logging.error(e)


# Set boot type to UEFI/Legacy via redfish, default set once
def set_boot_mode(mode, once=True):
    logging.info("[BmcLib] Set boot type with redfish.")
    mode_list = {"uefi": "UEFI", "legacy": "Legacy"}
    mode = mode.lower()
    try:
        assert mode in mode_list, f"Give invalid boot type, Only '{mode_list}' allowed"
        overwrite_en = "Once" if once else "Continuous"
        patch_body = {"Boot": {"BootSourceOverrideEnabled": overwrite_en,"BootSourceOverrideMode": mode_list[mode]}}
        patch = Sut.BMC_RFISH.patch_data(path=Sut.BMC_RFISH.SYSTEM, data=patch_body)
        if patch.result:
            logging.info(f"BMC set boot type success to '{mode_list[mode]}' for {overwrite_en}")
            return True
        logging.error(f"BMC set boot type failed")
    except Exception as e:
        logging.error(e)


def is_legacy_boot():
    get_mode = Sut.BMC_RFISH.get_info(path=Sut.BMC_RFISH.SYSTEM)
    if get_mode:
        if get_mode["Boot"]["BootSourceOverrideMode"].lower() == "legacy":
            logging.info("Current boot mode is legacy")
            return True
        else:
            logging.info("Current boot mode is UEFI")
            return False


def open_bt_channel():
    """Open bt channel for continuous reading data from bt channel, return ssh_shell instance"""
    logging.info("Opening bt channel...")
    cmd1 = 'maint_debug_cli\n'
    cmd2 = 'attach ipmi\n'
    cmd3 = 'trace ch=bt\n'
    cmds = [cmd1, cmd2, cmd3]
    res = ['%', '%', '']
    if not Sut.BMC_SSH.login():
        return
    bt_shell = Sut.BMC_SSH.ssh_client.invoke_shell()
    for index, cmd in enumerate(cmds):
        bt_shell.send(cmd)
        time.sleep(2)
        rsp = bt_shell.recv(1024).decode('utf-8')
        if res[index] not in rsp:
            logging.error(f"Run cmd fail: {cmd}")
            return
    logging.info("Open bt channel success")
    return bt_shell


# Check bmc bt test_data, better call it before power or capture action, better use reboot in OS
def read_bt_data(key_str, timeout=SutConfig.Env.BOOT_DELAY, login=True, logout=True, shell=None):
    """key_str: the test_data you wanna to grab from bt channel, should be a list"""
    # check input data, key_str[0]: e.g 58 c6 must be 1st param from list
    assert isinstance(key_str, list), 'input should be a list'
    logging.info("Reading data from bt channel...")
    if login:
        shell = open_bt_channel()
    time_start = time.time()
    buffer = ""
    res_flg = []  # store the temp result,
    while True:
        if shell.recv_ready():
            temp = shell.recv(1024).decode('utf-8')
            last2_buffer = f"{buffer}{temp}"
            buffer = temp
            if len(key_str) == 1:
                if (i in last2_buffer for i in key_str):
                    logging.info(f"All msg found in bt channel: {key_str}")
                    break
            else:
                for j in key_str[1:]:
                    if re.findall(r'.*{0}.*{1}'.format(key_str[0], j), last2_buffer, re.I):
                        logging.debug(f'Msg found...{j}')
                        res_flg.append(j)

                if res_flg == key_str[1:]:
                    logging.info(f"All msg found in bt channel: {res_flg}")
                    break
        if time.time() - time_start > timeout:
            logging.info(f"Msg not found in bt channel within {timeout}s: {list(set(key_str[1:]) - set(res_flg))}")
            if logout:
                logging.info("Close the bt channel.")
                Sut.BMC_SSH.close_session()
            return False
    Sut.BMC_SSH.close_session()
    logging.info("Close the bt channel.")
    return True


# Grab bmc sol test_data, better call it before power action,
def read_sol_data(ver_lst, timeout=5):
    """
    verify_list: should be a str list to be verified,
    """
    logging.info("[BmcLib] Receiving bmc sol test_data...")
    sol_cmd = 'ipmcset -t sol -d activate -v 0 1\n'
    buff = ''
    assert isinstance(ver_lst, list), "Incorrect format of parameter: ver_lst, should be a list"

    tmp_lst = []
    try:
        if Sut.BMC_SSH.login():
            op = Sut.BMC_SSH.ssh_client.invoke_shell()
            logging.debug('Sending: {0}'.format(sol_cmd.strip("\n")))
            op.send(sol_cmd)
            time.sleep(1)
            start_time = time.time()
            res = op.recv(1024).decode('utf-8')
            while re.search('Connect SOL successfully', res):
                if op.recv_ready():
                    buff += op.recv(1024).decode('utf-8')
                    for i in ver_lst:
                        if re.search(i, buff):
                            tmp_lst.append(i)
                now = time.time()
                if set(tmp_lst) == set(ver_lst):
                    logging.info('Find strings:{0}'.format(list(set(tmp_lst))))
                    break
                # timeout default is 5s,
                if (now - start_time) > timeout:
                    logging.info('Grab sol test_data timeout, close the session')
                    logging.info("Can not find strings(timeout):{0}".format(list(set(ver_lst) - set(tmp_lst))))
                    op.close()
                    return
                # print(buff)
                time.sleep(0.1)
            return True
    except Exception as e:
        logging.error(e)
        return
    finally:
        Sut.BMC_SSH.ssh_client.close()


def get_bmc_datetime():
    cmd_time = 'ipmcget -d time'
    rsp_time = ""
    read_bmc = SshLib.interaction(Sut.BMC_SSH, [cmd_time], [rsp_time], timeout=30)
    assert read_bmc, "Invalid bmc data"
    read_bmc = read_bmc[1]
    date_time_found = re.findall("(\d{4}-\d{1,2}-\d{1,2}).*?(\d{2}:\d{1,2}:\d{1,2})", read_bmc)
    assert date_time_found, "Datetime string not found"
    bmc_date, bmc_time = date_time_found[0]
    bmc_date_time = f"{bmc_date} {bmc_time}"
    logging.info(f"Current BMC datetime: {bmc_date_time}")
    return bmc_date_time


def power_ac_cycle(ac_cmd):
    logging.info(f"Send AC Command from BMC: {ac_cmd}")
    cmd_maint_mode = 'maint_debug_cli\n'
    ret_maint_mode = 'Debug Shell'
    ret_ac = 'Success'
    ac_cmds = [cmd_maint_mode, ac_cmd]
    rets = [ret_maint_mode, ret_ac]
    return SshLib.interaction(Sut.BMC_SSH, ac_cmds, rets)


def get_tpm_info():
    sys_info =SshLib.execute_command(Sut.BMC_SSH, "ipmcget -d v")
    tpm_present = re.findall("Specification\s+Type:\s+(T[CP]M)", sys_info)
    if not tpm_present:
        logging.info("TPM/TCM not present")
        return {}
    logging.info("TPM/TCM is present")
    version = "".join(re.findall("Specification\s+Version:\s+(\S+)", sys_info))
    vendor = "".join(re.findall("Manufacturer\s+Name:\s+(\S+)", sys_info))
    logging.info(f"Vendor: {vendor}, Version: {version}")
    return {"Protocol": tpm_present, "Verson": version, "Vendor": vendor}


def ipmitool(cmd, response: str = "db 07 00"):
    root_path = Path(__file__).parent.parent
    ipmi_exe = root_path / "Resource/ipmitool/ipmitool.exe"
    cmd = f"{ipmi_exe} -I lanplus -H {SutConfig.Env.BMC_IP} -U {SutConfig.Env.BMC_USER} -P {SutConfig.Env.BMC_PASSWORD} {cmd}"
    exec_result = MiscLib.shell_cmd(cmd)
    if not response:
        logging.info(f"Ipmitool cmd executed without confirm")
        return exec_result.result
    output = exec_result.output
    if response not in output:
        logging.error(f"Expect response: {response}, actually={output}")
        return False
    else:
        logging.info(f"Ipmitool cmd executed success")
        return True

