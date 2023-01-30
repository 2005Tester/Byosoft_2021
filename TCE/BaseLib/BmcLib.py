import os
import logging
import re
import time
from batf.SutInit import Sut
from batf import SshLib, MiscLib
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Key
from TCE.BaseLib import SetUpLib


# update by arthur,
def is_power_off():
    logging.info("Check power status...")
    cmd_on = 'ipmcget -d powerstate\n'
    ret_confirm = 'Off'
    if Sut.BMC_SSH.login():
        ret = Sut.BMC_SSH.execute_command_interaction(cmd_on)
        if ret_confirm in ret.decode():
            logging.info('Current power state is Off')
            return True
        else:
            logging.info('Current power state is On')
            return


# power on SUT by BMC command
def power_on():
    logging.info("[BmcLib.power_on]Power on system.")
    cmd_reset = 'ipmcset -d powerstate -v 1\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]

    try_count = 3
    while is_power_off() and (try_count > 0):
        if Sut.BMC_SSH.login():
            Sut.BMC_SSH.interaction(cmds, rets)
            time.sleep(5)
        if not is_power_off():
            return True
        try_count -= 1

    if is_power_off():
        logging.error("Power on failed")
        return
    else:
        logging.info("Power status is already on.")
        return True


# power off sut by BMC command
def power_off():
    logging.info("[BmcLib.power_off]Power off system - force")
    cmd_reset = 'ipmcset -d powerstate -v 2\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'success'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]

    try_count = 3
    while (not is_power_off()) and (try_count > 0):
        if Sut.BMC_SSH.login():
            Sut.BMC_SSH.interaction(cmds, rets)
            time.sleep(5)
        if is_power_off():
            return True
        try_count -= 1

    if not is_power_off():
        logging.error("Power off failed")
        return
    else:
        logging.info("Power status is already off.")
        return True


# Force reset SUT by BMC command
def force_reset():
    if is_power_off():
        if power_on():
            return True
        else:
            logging.error("[BmcLib] power_on return false.")
    else:
        logging.info("[BmcLib]Force reset")
        cmd_reset = 'ipmcset -d frucontrol -v 0\n'
        ret_reset = 'Do you want to continue'
        cmd_confirm = 'Y\n'
        ret_confirm = ''
        cmds = [cmd_reset, cmd_confirm]
        rets = [ret_reset, ret_confirm]
        if Sut.BMC_SSH.login():
            return Sut.BMC_SSH.interaction(cmds, rets)
        else:
            logging.error("Force system reset failed")
            return


# Force power cycle by BMC command
def force_power_cycle():
    logging.info("[BmcLib.force_power_cycle]Force power cycle.")
    cmd_powercycle = 'ipmcset -d frucontrol -v 2\n'
    ret_powercycle = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = ''
    cmds = [cmd_powercycle, cmd_confirm]
    rets = [ret_powercycle, ret_confirm]
    if Sut.BMC_SSH.login():
        return Sut.BMC_SSH.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: force powercycle failed")
        return


# clear CMOS by BMC command
def clear_cmos():
    logging.info("Clear CMOS to restore enviroment.")
    cmd_clearcoms = 'ipmcset -d clearcmos\n'
    ret_clearcmos = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = ''
    cmds = [cmd_clearcoms, cmd_confirm]
    rets = [ret_clearcmos, ret_confirm]
    sleep_cnt = 0
    if is_power_off():
        pass
    else:
        power_off()
        while sleep_cnt <= 10:
            if is_power_off():
                break
            else:
                time.sleep(3)
                sleep_cnt += 1
    if Sut.BMC_SSH.login():
        Sut.BMC_SSH.interaction(cmds, rets)
        logging.info("[BmcLib]clear cmos done")
        return
    else:
        logging.error("BmcLib: clear CMOS failed by BMC command")
        return


# open/close debug message with bmc cmd
def debug_message(enable=True):
    logging.info("[BmcLib.debug_message]Turn full log on off.")
    value = 1 if enable else 2
    cmd1 = f"ipmcset -t maintenance -d biosprint -v {value}\n"
    rtn1 = 'Do you want to continue'
    cmd2 = 'Y\n'
    rtn2 = 'successfully'
    if not Sut.BMC_SSH.login():
        return
    if not enable:
        logging.info("[Serial Debug Message] -> Disabled")
        return Sut.BMC_SSH.interaction([cmd1], [rtn2])
    logging.info("[Serial Debug Message] -> Enabled")
    return Sut.BMC_SSH.interaction([cmd1, cmd2], [rtn1, rtn2])


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
        return SshLib.interaction(Sut.BMC_SSH, cmds, rets, 400)


# BMC一键收集
# uncom=True: uncompress the file, return path="path/name" | uncom=False: return file="path/name.tar.gz"
def bmc_dumpinfo(path, name="dump", uncom=False):
    cmd_diag = "ipmcget -d diaginfo\n"
    SshLib.sftp_remove_file(Sut.BMC_SFTP, ".bin")
    logging.info("Start BMC dump, Please wait...")
    res = SshLib.interaction(Sut.BMC_SSH, [cmd_diag], ['successfully'])[1]
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
def bmc_warning_check():
    class Result:
        status = None  #
        message = None

    cmd = "ipmcget -d healthevents"
    res = SshLib.execute_command(Sut.BMC_SSH, cmd)
    if not res:
        logging.error(f'Run cmd "{cmd}" error')
        return
    if "System in health state" in res:
        logging.info("[BMC Warning Check] Current system in health state")
        Result.status = True
    elif 'Low voltage of RTC battery on the mainboard' in res:
        logging.info("Low battery, check the CMOS, if not exist, pass - health state")
        Result.status = True
    else:
        logging.info("[BMC Warning Check] Alarms/Events detected")
        Result.status = False
        for line in res.split("\r\n"):
            logging.info(line)
    Result.message = res
    return Result


# Enable fdmlog
def enable_fdmlog_dump():
    dump_cmd = ["maint_debug_cli\n", "attach diag\n", "dump_state 1\n"]
    dump_rtn = ["Shell", "Success", "Success"]
    return SshLib.interaction(Sut.BMC_SSH, dump_cmd, dump_rtn, 10)


def get_productname():
    logging.info("Return product name to fetch the right bios...")
    cmd = ['ipmcget -d ver\n']
    ret = ['Mainboard']
    prd = []  # board id list
    data = SshLib.interaction(Sut.BMC_SSH, cmd, ret)[1]
    if '0x0055' in data:  # 4U board id
        prd.append('4U')
    elif '0x0056' in data:  # 2U board id
        prd.append('2U')
    else:
        print('No action.')
        return
    return prd


# Set fan mode by bmc
def set_fan_level():
    logging.info("[BmcLib] Set fan mode.")
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    ret_fan_manual_mode = 'Set fan mode successfully'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    ret_fan_40 = 'Set fan level successfully'
    cmds = [cmd_fan_manual_mode, cmd_fan_40]
    rets = [ret_fan_manual_mode, ret_fan_40]
    return SshLib.interaction(Sut.BMC_SSH, cmds, rets)


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


# Check bmc bt data, better call it before power or capture action, better use reboot in OS
def read_bt_data(key_str, timeout=5):
    """
    key_str: the data u wanna grab from bt channel,
    """
    logging.info("[BmcLib] Read bmc bt data...")
    bt_cmd = 'maint_debug_cli\n'
    ipmi_cmd = 'attach ipmi\n'
    trace_cmd = 'trace ch=bt\n'
    cmds = [bt_cmd, ipmi_cmd, trace_cmd]
    res = ''
    try:
        if Sut.BMC_SSH.login():
            op = Sut.BMC_SSH.ssh_client.invoke_shell()
            for i in range(0, len(cmds)):
                logging.debug('Sending: {0}'.format(cmds[i].strip("\n")))
                op.send(cmds[i])
                time.sleep(0.2)
                if cmds[i] == trace_cmd:
                    logging.info('BT data receiving and searching...')
                    start_time = time.time()
                    while True:
                        if op.recv_ready():
                            res = op.recv(1024).decode('utf-8')
                        now = time.time()
                        if re.findall(key_str, res):
                            logging.debug('Found the msg: {0}'.format(res))
                            break
                        # timeout default is 5s,
                        if (now - start_time) > timeout:
                            logging.info('Grab bt data timeout, close the session')
                            op.close()
                            raise Exception
                        # print(res)
                        time.sleep(0.1)
                else:
                    pass  # skip invalid data,
            op.close()
        return True, res
    except Exception as e:
        logging.error(e)
        return False
    finally:
        Sut.BMC_SSH.ssh_client.close()


# 抓取当前KVM屏幕图像，并保存到本地
def capture_kvm_screen(path, name):
    save_screen = SshLib.interaction(Sut.BMC_SSH, ["ipmcset -d printscreen\n"], ["successfully"], 15)
    if not save_screen:
        logging.info("BMC dump screen run command failed")
        return
    save_path = "".join(re.findall("Download print screen image to (.+) successfully.", save_screen[1]))
    img_file = os.path.join(path, f"{name}.jpeg")
    if SshLib.sftp_download_file(Sut.BMC_SFTP, save_path, img_file):
        logging.info(f"Dump current kvm screen success, save image {img_file}")
        return img_file


# 从BMC读取当前固件版本信息, 返回版本信息为字符串格式
def firmware_version_check():
    class BmcInfo:
        BIOS = None
        BMC = None
        CPLD = None
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
    return BmcInfo


# Grab bmc sol data, better call it before power action,
def read_sol_data(ver_lst, timeout=5):
    """
    verify_list: should be a str list to be verified,
    """
    logging.info("[BmcLib] Receiving bmc sol data...")
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
                    logging.info('Grab sol data timeout, close the session')
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