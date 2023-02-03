#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import os
import csv
import re
import json
import datetime
import logging
import time
import glob
import numpy
import pandas
import difflib
from pathlib import Path
from typing import Union
from functools import wraps
from PIL import Image
from SPR4P.Config import SutConfig
from batf.Common.LogAnalyzer import LogAnalyzer
from SPR4P.Config.PlatConfig import Msg, Key, BiosCfg
from SPR4P.BaseLib import SetUpLib, BmcLib, BmcWeb
from batf.SutInit import Sut
from batf import SerialLib, SshLib, MiscLib, var, core

# LogAnalyzer
P = LogAnalyzer(SutConfig.Env.LOG_DIR)


def root_path() -> Path:
    """Get current project root path, return Path object"""
    root = Path(__file__).parent.parent
    return root


# used for rw test
def rw_everything(ssh, exp_res, mem_bar=None, cmd='mmr', str=' ', start=1, stop=3):
    """
    :str is split flag, default is ' ' - blank
    :start from list, default is 1
    :stop by list, default is 3
    :param exp_res is a excepted num list
    :param mem_bar should be printed in full debug message, e.g mem0_bar and mem1_bar address - list
    :param cmd is a parameter supported by rw tool, e.g mmr
    """
    if mem_bar is None:
        mem_bar = []

    org_list = []
    logging.info('Starting to rw the address...')
    for i in range(len(mem_bar)):
        res = SshLib.execute_command(ssh, r'cd {0};./rw {1} {2} | grep {2}'.format(SutConfig.Env.RW_PATH, cmd, mem_bar[i]))
        logging.debug(res)
        if len(res) == 0:
            logging.info('RW tool can not be found')
            break
        else:
            for j in res.split(str)[start:stop]:
                org_list.append(j)

    time.sleep(0.1)
    logging.debug(org_list)
    if exp_res != org_list:
        logging.info('Register verified - fail')
        return
    logging.info('Register verified - pass')
    return True


def cscripts_rw(cmd: str):
    """
    Read / Write Cscripts cmds

    Returns:    dict    -   cmd end with '.show()'
                hex     -   read register field name
                str     -   others / write

    raise:      Exception
    """
    logging.info(f"Run cscripts cmd: '{cmd}'")
    cd_path = f"cd {SutConfig.Env.CSCRIPTS_PATH}\n"
    cmd_open = "python3 startCscripts.py -a inband\n"
    rsp = SshLib.interaction(Sut.OS_SSH, [cd_path, cmd_open, f"{cmd}\n"], ["", ">>>", ""], timeout=60)
    if not rsp[0]:
        raise Exception("Open Cscripts and run cmd error")
    cmd_sub = re.sub("([()])", r"\\\1", cmd)  # parentheses handle
    rsp_str = re.sub(f"[\s\S]*{cmd_sub}.*|>>> ", "", rsp[1]).strip()
    if re.search("\.showsearch", cmd):
        reg_key_value = re.findall("([.\w]+) = ([.\w]+)", rsp_str)
        if not reg_key_value:
            raise Exception(f"Register pairs of key/value  not found: {rsp_str}")
        reg_kv_dict = {kv[0]: kv[1] for kv in reg_key_value}
        logging.info(reg_kv_dict)
        return reg_kv_dict
    if re.search("\.show", cmd):
        reg_key_value = re.findall("(\w+) : (\w+)", rsp_str)
        if not reg_key_value:
            raise Exception(f"Register pairs of key/value  not found: {rsp_str}")
        reg_kv_dict = {kv[1]: int(kv[0], 16) for kv in reg_key_value}
        logging.info(reg_kv_dict)
        return reg_kv_dict
    if rsp_str.isdigit():
        logging.info(f"{cmd} = {int(rsp_str)}")
        return int(rsp_str)
    if re.fullmatch("[0-9a-fA-FxX]*", rsp_str):
        logging.info(f"{cmd} = {int(rsp_str, 16)}")
        return int(rsp_str, 16)
    logging.debug(rsp_str)
    return rsp_str


def dc_cycle():
    if not SetUpLib.boot_to_setup():
        return
    if not BmcLib.force_power_cycle():
        return
    logging.info("Booting to setup")
    if not SetUpLib.continue_to_setup():
        return
    return True


# sub function for dump cpu resource allocation table
def dump_cpu_resource():
    if not BmcLib.force_reset():
        return
    resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 10, 120)
    if not resource:
        return
    data_search = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SutConfig.Sys.CPU_CNT)])
    rsc_table = re.search(data_search, resource)
    if not rsc_table:
        return
    lines = rsc_table.group().split("\n")
    result = []
    for line in lines:
        result.append(list(map(lambda x: x.strip(), line.split("|"))))
    csv_file = os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv")
    with open(os.path.join(SutConfig.Env.LOG_DIR, "cpu_resource.csv"), "w", newline="") as rsc:
        csv_writer = csv.writer(rsc)
        csv_writer.writerows(result)
    return csv_file


# Check whether DVD-ROM exists in boot manager
def dvd_verify():
    logging.info("** Verify DVD exists ")
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(['[UEFILegacy] Boot'], Key.DOWN, 23)  # , 'DVD-ROM Drive  -page'   ,
        assert SetUpLib.verify_info([Msg.MENU_DVD_BOOT], 4)
        logging.info(" DVD-ROM device found.")
        return True
    except AssertionError:
        logging.info("DVD-ROM device not found.")


def read_bmc_dump_log(package_path, sub_path):
    log_path = os.path.join(package_path, sub_path)
    if not os.path.isfile(log_path):
        logging.warning(f"file not exists in {log_path}")
        return
    with open(log_path) as log:
        return log.read()


# 检查dmesg信息种是否存在某个关键字，返回相应行组成的列表
# 比如检查 error, fail, 则 keywords = ["error", "fail]
def check_dmesg(keywords: list, ignore_list=None):
    ignore_list = [] if not ignore_list else list(ignore_list)
    err_lines = []
    for words in keywords:
        logging.info(f'Check is there any "{words}" in dmesg')
        dmesg_err = SshLib.execute_command(Sut.OS_SSH, f"dmesg |grep -i {words}")
        if not dmesg_err:
            logging.info(f'Check dmesg of "{words}" pass')
            continue
        for line in dmesg_err.splitlines():
            if any(re.search(ignore, line, re.I) for ignore in ignore_list):
                continue
            err_lines.append(err_lines)
            logging.warning(f"Unexpected dmesg: {line}")
    if not err_lines:
        logging.error(f"{len(err_lines)} dmesg error are recorded")
    return err_lines


def unipwd_tool(new_pw="", old_pw="", cmd="set") -> bool:
    """
    :param new_pw: uniPwd param1
    :param old_pw: uniPwd param2
    :param cmd: uniPwd Command, support: set / clear / check / sets / checks (align with unipwd helping message)
    :return: True / None
    """
    cmd_support = ["set", "clear", "check", "sets", "checks"]
    new_pw = "" if cmd == "clear" else new_pw
    cd_path = f"cd {SutConfig.Env.UNI_PATH}"
    if new_pw:
        new_pw = MiscLib.regex_unescape(new_pw, "\\$`\'\"")  # linux shell escape character handle
    if old_pw:
        old_pw = MiscLib.regex_unescape(old_pw, "\\$`\'\"")  # linux shell escape character handle
    param0 = f'"{new_pw}"'
    param1 = f' "{old_pw}"' if old_pw else ''
    pwd_exec = f'./uniPwd -{cmd} {param0}{param1}'
    rtn_pass = f"success"
    try:
        assert cmd in cmd_support, f"{cmd} not in support list {cmd_support}"
        rtn = SshLib.execute_command(Sut.OS_SSH, f"{cd_path};{pwd_exec}")
        assert rtn, f"Return nothing after execute cmd: {pwd_exec}"
        assert rtn_pass in rtn.lower(), f"Unipwd {cmd} password failed"
        logging.info(f"Unipwd {cmd} password success")
        return True
    except Exception as e:
        logging.error(e)


# update logo with unilogo tool in linux
# 若path参数为空，则默认刷\Tools\Logo里的logo文件
def unilogo_update(name, path=""):
    cd_path = f"cd {SutConfig.Env.UNI_PATH}"
    logo_flash = f"./uniCfg -setlogo ./{name}"
    rtn_pass = f"Update Logo.+success"
    try:
        if not path:
            path = root_path() / "Resource/Logo"
            logging.info(f"Update the logo: {path}/{name}")
            assert name in os.listdir(path), f"Logo name {name} not exist in directory: Tools/Logo"  # 检查name文件是否存在
        assert SshLib.sftp_upload_file(Sut.OS_SFTP, f"{path}/{name}", f"{SutConfig.Env.UNI_PATH}/{name}", ret_msg="")
        rtn = SshLib.execute_command(Sut.OS_SSH, f"{cd_path};{logo_flash}")
        assert rtn, f"execute_command for flash logo error: {rtn}"
        assert re.search(rtn_pass, rtn.lower(), re.I), f"Unilogo update logo failed:\n{rtn}"
        logging.info(f"Unilogo update logo success")
        return True
    except Exception as e:
        logging.error(e)


def screen_crop(cursor, path=SutConfig.Env.LOG_DIR, name=None):
    now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    name = f"Screen_{now}" if not name else name
    if not os.path.exists(path):
        os.makedirs(path)
    img_file = BmcLib.capture_kvm_screen(path, name=name)
    img_open = Image.open(img_file)  # 打开图片
    cut_logo = img_open.crop(cursor)  # logo裁剪
    cut_logo = cut_logo.convert("P", palette=Image.ADAPTIVE, colors=256)
    save_img = os.path.join(path, f"{name}.bmp")
    cut_logo.save(save_img, format="bmp", bits=8, quality=100)  # 保存裁剪部分
    if not os.path.isfile(save_img):
        raise FileExistsError("Crop screen image fail")
    return save_img


# 保存logo图片, 默认格式为bmp
def save_logo(path=SutConfig.Env.LOG_DIR, name="logo", prompt=Msg.LOGO_SHOW, cursor=Msg.CURSOR_LOGO):
    try:
        assert BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(prompt, SutConfig.Env.BOOT_DELAY)
        save_img = screen_crop(cursor=cursor, path=path, name=name)
        logging.info(f"Save logo success: {save_img}")
        return save_img
    except Exception as e:
        logging.error(e)


# unitool 無參數 如 -b -c -setCustomDefault, 及ini脚本
def uni_command(cmd, uefi=True):
    cd_path = f"cd {SutConfig.Env.UNI_PATH}"
    tool_name = "uniCfg"
    rsp_pass = "success"
    rsp_fail = "error"
    ssh_ins = Sut.OS_SSH if uefi else Sut.OS_LEGACY_SSH
    try:
        if "getlogo" in cmd:
            logo_file = cmd.split()[1]
            SshLib.execute_command(ssh_ins, f"{cd_path};rm -rf {logo_file}")
        rsp = SshLib.execute_command(ssh_ins, f"{cd_path};./{tool_name} {cmd}", print_result=True)  # 默认Sut.OS_SSH 为uefi模式下os
        assert MiscLib.msg_contain(rsp.lower(), rsp_pass, excepts=rsp_fail), f"[{tool_name}] '{cmd}' failed"
        return True
    except Exception as e:
        logging.error(e)
        return


def get_acpi_table_linux(table_name: Union[str, list], path="~/acpi_dump", uefi=True):
    """
    str:    if only one table specificed, return str of specific acpi table,
            if multi table specificed, return dict like: {table1: "xxx", table2: "xxx"}
    -1:     acpi table not exist
    None:   error
    """
    sut_os_ssh = Sut.OS_SSH if uefi else Sut.OS_LEGACY_SSH
    if "Usage" not in SshLib.execute_command(sut_os_ssh, "acpidump -h"):
        logging.warning("'acpidump' tool not installed in current os")
        return
    if isinstance(table_name, str):
        table_name = [table_name.lower()]
    cmd_dump = "acpidump -o AcpiTable.out"
    cmd_xtract = "acpixtract -a AcpiTable.out"
    clean_path = "rm -f *.out *.dat *.dsl"
    SshLib.execute_command(sut_os_ssh, f"mkdir {path};cd {path};{clean_path};{cmd_dump};{cmd_xtract}")
    tables_dat = SshLib.execute_command(sut_os_ssh, f"cd {path};ls")
    logging.debug(f"{tables_dat}")
    all_tables = {}
    for table in table_name:
        if f"{table}.dat" in tables_dat:
            cmd_decode = f"iasl -d {table}.dat"
            logging.info(f"ACPI table found: {table}")
            SshLib.execute_command(sut_os_ssh, f"cd {path};{cmd_decode}")
            table_content = SshLib.execute_command(sut_os_ssh, f"cd {path};cat {table}.dsl")
            all_tables[table] = table_content
        else:
            logging.warning(f"ACPI table not exist: {table}")
    if len(table_name) == 1:
        return all_tables.get(table_name[0])
    return all_tables


def smbios_to_dict(smbios: str):
    """
    transfer smbios to dict, support one or more SMBIOS data
    {   "type17":
            [
                {"Handle Name":"Memory Device", "Size": 64G, "Rank": xxx},
                {"Handle Name":"Memory Device", "Size": 64G, "Rank": xxx},
            ]
    }
    """
    sm_split = re.findall("\nHandle \w+, DMI type (\d+).+?\n([\w ]*)\n([\S\s]+?)(?=\nHandle \w+, DMI type|$)", smbios)
    if not sm_split:
        logging.error("Invalid SMBIOS data")
        return
    smbios_all = {}
    for sm in sm_split:
        type_n = sm[0].strip()
        name = sm[1].strip()
        data = sm[2].strip()
        data = re.sub("\t+", "", data)
        data_find = re.findall("(.+?):( .+|\n[\S\s]+)", data)
        handle = {"Handle Name": name}
        data_dict = {k[0].strip(): k[1].strip() for k in data_find}
        handle.update(data_dict)
        type_title = f"type{type_n}"
        if type_title not in smbios_all:
            smbios_all[type_title] = []
        if not smbios_all[type_title]:
            smbios_all[type_title] = [handle]
        else:
            smbios_all[type_title].append(handle)
    return smbios_all


def smbios_dump_compare(ssh, type_n):
    sample_log_file = SutConfig.Env.Smbios_PATH + 'type{0}.txt'.format(type_n)
    if not Path(sample_log_file).exists():
        raise OSError(f"SMBIOS sample log not exist: {sample_log_file}")
    with open(sample_log_file, "r", encoding="utf-8") as log:
        sample_log_str = log.read()

    read_log_file = os.path.join(var.get('log_dir'), f"smbios_type{type_n}.txt")
    read_log_str = SshLib.execute_command(ssh, f"dmidecode -t {type_n}")
    with open(read_log_file, "w", encoding="utf-8") as log:
        log.write(read_log_str)  # 如果没有模板日志，则将当前SMBIOS保存到本地

    read_dict = smbios_to_dict(read_log_str)
    template_dict = smbios_to_dict(sample_log_str)
    if read_dict != template_dict:
        logging.debug(f"Read SMBIOS data: {json.dumps(read_dict, indent=4)}")
        logging.debug(f"Sample Log data: {json.dumps(template_dict, indent=4)}")
        difference = P.check_diff(read_log_file, sample_log_file)
        for diff in difference:
            logging.warning(diff)
        return False
    logging.info(f"Check SMBIOS type{type_n} pass")
    return True


def no_error_at_post(boot_time=SutConfig.Env.BOOT_DELAY, reboot=True):
    try:
        if reboot:
            assert BmcLib.force_reset()
        SerialLib.clean_buffer(Sut.BIOS_COM)
        ser_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.BIOS_BOOT_COMPLETE, boot_time, boot_time)
        assert Msg.BIOS_BOOT_COMPLETE in ser_log
        return MiscLib.msg_exclude(ser_log, Msg.SERIAL_WORDS, Msg.SERIAL_IGNORE)
    except Exception:
        return False


def dimm_per_channel():
    """Check current config is 1DPC or 2DPC"""
    dimm_pop = SutConfig.Sys.DIMM_POP
    dimm_info = {}
    for slot in dimm_pop:
        socket, channel, dimm = slot
        if socket not in dimm_info:
            dimm_info[socket] = {}
        if channel not in dimm_info[socket]:
            dimm_info[socket][channel] = []
        if dimm not in dimm_info[socket][channel]:
            dimm_info[socket][channel].append(dimm)
    dpc_n = []
    for _socket, _channel in dimm_info.items():
        for _ch, _dimm in _channel.items():
            dpc_n.append(len(_dimm))
    return min(dpc_n)


def baseline_to_dict(dump_file=None, var_key=True, value_to_index=True):
    """
    Transfer Baseline Excel to dict
    var_key:  If True, return dict with "variable name" as the key
              If False, return dict with "setup name" as the key
    value_to_dict:  If True, return "values" like: { "Enabled": "0x1", "Disabled": "0x0" }
                    If False, return "values" like: { "0x1": "Enable", "0x0": "Disabled" }
    :return:
                {
                "Variable Name1": {
                                "setup": "SetupOption Name1"
                                "values": { "Enabled": "0x1", "Disabled": "0x0" },
                                "default":"Enabled",
                                "unicfg": True,
                                "redfish": False
                                }

                }
    """

    base_file = root_path() / "Resource/SetupBase/5885HV7_Setup_Baseline.xlsx"
    logging.info(f"Baseline file: {base_file}")
    head_variable = "项目名"
    head_value = "英文选择项Value"
    head_default = "英文选择项"
    head_setup = "英文菜单项"
    head_unitool = "UniCfg"
    head_redfish = "Redfish"
    sheet_name = "V7 Setup基线"

    base_dict = {}
    pd = pandas.read_excel(base_file, sheet_name=sheet_name, dtype=str)
    pd = pd.fillna("")

    def values_dict_from_name(value: str, name_to_index=True):
        value_pairs = value.splitlines()
        value_dict = {}
        for values in value_pairs:
            val_split = values.split(":", maxsplit=1)
            if not any(v.startswith("0x") for v in val_split):
                val_split = values.rsplit(":", maxsplit=1)
            if len(val_split) != 2:
                continue
            val_name, val_num = val_split[0].strip(), val_split[1].strip()
            if "0x" in val_name:
                val_name, val_num = val_num, val_name
            if name_to_index:
                value_dict[val_name] = val_num
            else:
                value_dict[val_num] = val_name
        return value_dict

    def get_default_value(value="Enabled*\nDisabled"):
        return "".join(re.findall("(\S.*)\*", value)).strip()

    for row in pd.index:
        var_name = pd.loc[row, head_variable]
        if not var_name.strip():
            continue
        if var_name in base_dict:
            continue
        if len(var_name.splitlines()) > 1:
            var_name = var_name.splitlines()[0]
        var_values = pd.loc[row, head_value]
        var_default = pd.loc[row, head_default]
        var_setup = pd.loc[row, head_setup]
        var_unicfg = pd.loc[row, head_unitool]
        var_redfish = pd.loc[row, head_redfish]

        var_values = values_dict_from_name(var_values, name_to_index=value_to_index)
        var_default = get_default_value(var_default)
        var_setup = str(var_setup).strip()
        var_unicfg = True if str(var_unicfg).strip() == "Y" else False
        var_redfish = True if str(var_redfish).strip() == "Y" else False
        if var_key:
            base_dict[var_name] = {"setup": var_setup,
                                   "values": var_values,
                                   "default": var_default,
                                   "unicfg": var_unicfg,
                                   "redfish": var_redfish}
        else:
            base_dict[var_setup] = {"variable": var_name,
                                   "values": var_values,
                                   "default": var_default,
                                   "unicfg": var_unicfg,
                                   "redfish": var_redfish}
    if dump_file:
        with open(dump_file, "w", encoding="utf-8") as f:
            json.dump(base_dict, f, indent=4)

    return base_dict


def get_current_serial_log() -> str:
    current_log = var.get('serial_log')
    logging.info("Read serial log of current test")
    with open(current_log, "r", encoding="utf-8") as _log:
        return _log.read()


def set_rtc_time_linux(time_str=None, time_format="%Y-%m-%d %H:%M:%S"):
    """在Linux系统下设置RTC时间, 如果time_str=None, 则将HOST时间和SUT时间同步"""
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 10):
        if not SetUpLib.boot_to_default_os():
            return
    if time_str:
        try:
            time_is_valid = time.strptime(time_str, time_format)
        except Exception as e:
            logging.error(f"[{e}] Time str should follow the format: {time_format}")
            return
    else:
        time_str = datetime.datetime.now().strftime(time_format)
    logging.info(f"Setting RTC time to: {time_str} UTC+8")
    cmd_utc_set = 'timedatectl set-timezone "Asia/Shanghai"'
    cmd_time_set = f'date -s "{time_str}"'
    if not SshLib.interaction(Sut.OS_SSH, [cmd_utc_set, cmd_time_set, "hwclock -w", "clock -w"], ["", "", "", ""], timeout=15, delay=1):
        return
    # Check Date Time Result
    time_read = SshLib.execute_command(Sut.OS_SSH, f'date "+{time_format}"').strip()
    rtc_read = SshLib.execute_command(Sut.OS_SSH, "hwclock -r").strip()
    date_find = "".join(re.findall("\d{4}[/-]\d{1,2}[/-]\d{1,2}", rtc_read))
    time_find = "".join(re.findall("\d{1,2}:\d{1,2}:\d{1,2}", rtc_read))
    date_split = re.split("/|-", date_find)
    rtc_time_str = f"{'-'.join(date_split)} {time_find}"
    time_offset = MiscLib.time_str_offset(time_read, rtc_time_str)
    if 0 <= time_offset <= 10:
        logging.info("Linux set RTC time success")
        return True
    logging.error(f"Linux set RTC time fail: [{time_offset}] {time_read} -> {rtc_read} ")


def bmc_log_exist(logs, from_time, operate=None, running=None, security=None, all_logs=None):
    """检查在某个时间点之后，预期的安全日志是否存在, 支持单条或多条的检查"""
    logs = [logs] if isinstance(logs, str) else logs
    if not all_logs:
        all_logs = BmcWeb.BMC_WEB.get_ibmc_log(from_time=from_time, operate=operate, running=running, security=security)
    log_miss = set(logs)
    for line in all_logs:
        index, date, log_str = line
        if from_time and MiscLib.time_str_offset(from_time, date) <= 0:
            continue
        for log in logs:
            if (log in log_str) or re.search(log, log_str):
                logging.info(f"BMC log found after [{from_time}]: {log}")
                log_miss.remove(log)
            if not log_miss:
                return True
    logging.info(f"BMC log not found after [{from_time}]: {log_miss}")
    return False


def linux_tool_ready(os_path, local_path, uefi=True):
    """检查Linux工具是否准备好，如果不存在，则上传到OS并且加权限，需要启动到Linux OS"""
    tool = Path(os_path)
    tool_name = tool.name
    tool_path = tool.parent.as_posix()
    ssh_ins = Sut.OS_SSH if uefi else Sut.OS_LEGACY_SSH
    sftp_ins = Sut.OS_SFTP if uefi else Sut.OS_LEGACY_SFTP
    if tool_name in SshLib.execute_command(ssh_ins, f"ls {tool_path} |grep {tool_name}"):
        return True
    local_tool = root_path() / f"{local_path}"
    if not SshLib.sftp_upload_file(sftp_ins, str(local_tool), f"{tool_path}/{tool_name}", ret_msg=""):
        return
    SshLib.execute_command(ssh_ins, f"chmod 777 {tool_path}/{tool_name}")
    return True


def get_latest_hpm_bios():
    branch_list = glob.glob(os.path.join(SutConfig.Env.BIOS_PATH, "*"))
    ver_latest = 0
    branch_latest = ""
    for branch in branch_list:
        ver_str = branch[-3:]
        if not ver_str.isdigit():
            continue
        branch_ver = int(ver_str)
        if branch_ver >= ver_latest:
            ver_latest = branch_ver
            branch_latest = branch
    latest_hpm = glob.glob(os.path.join(SutConfig.Env.BIOS_PATH, branch_latest, "*.hpm"))
    if latest_hpm:
        return latest_hpm[0]
    else:
        raise FileNotFoundError(f"Hpm files not found in path: {branch_latest}")


def is_sp_boot_success(timeout=300):
    logging.info("Waiting SP boot complete...")
    start_time = time.time()
    sp_flag = root_path() / "Resource/Images/sp_flag.bmp"
    while time.time() - start_time <= timeout:
        tmp = screen_crop((0, 0, 200, 30), name="sp_boot", path=os.path.join(SutConfig.Env.LOG_DIR, var.get('current_test')))
        if MiscLib.images_similar(tmp, str(sp_flag)):
            return True
        time.sleep(15)
    logging.info("SP boot failed")
    core.capture_screen()


def read_hex_bit(hex_val: Union[int, str], high: int, low: int = None):
    """将一个数值转换为二进制后，返回其中一位或多位的值"""
    if isinstance(hex_val, str) and hex_val.startswith("0x"):
        hex_val = int(hex_val, 16)
    high_mask = (1 << high + 1) - 1
    temp_val = hex_val & high_mask
    if low is None:
        return temp_val >> high
    return temp_val >> low


def get_pcie_bdf(reset=True):
    if reset:
        BmcLib.force_reset()
    SerialLib.clean_buffer(Sut.BIOS_COM)
    post_log = SerialLib.cut_log(Sut.BIOS_COM, "RootPortSBDF", "\+-{50,}\+", SutConfig.Env.BOOT_DELAY, SutConfig.Env.BOOT_DELAY)
    bdf_info = {}
    for line in post_log.splitlines():
        bus_dev_func = re.findall("\w{2}:(\w{2}:\w{2}:\w{2})", line)
        if not bus_dev_func:
            continue
        root_port, end_point = bus_dev_func
        root_bus, root_dev, root_func = root_port.split(":")
        end_bus, end_dev, end_func = end_point.split(":")
        root_bdf = f"{root_bus}:{root_dev}.{root_func}"
        end_bdf = f"{end_bus}:{end_dev}.{end_func}"
        if root_bdf in bdf_info:
            bdf_info[root_bdf].append(end_bdf)
        else:
            bdf_info[root_bdf] = [end_bdf]
    logging.info(f"System PCIE BDF: {bdf_info}")
    return bdf_info


def current_test_dir() -> Path:
    current_path = Path(SutConfig.Env.LOG_DIR) / var.get("current_test")
    if not os.path.exists(current_path):
        os.makedirs(current_path)
    return current_path


def mark_legacy_test(func):
    """装饰器，测试前切换到Legacy模式，测试完成后恢复到UEFI"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            BmcLib.force_reset()
            SetUpLib.wait_boot_msgs(Msg.HOTKEY_PROMPT_DEL)  # workaround for clear CMOS will cause boot type setting fail
            assert BmcWeb.BMC_WEB.set_boot_overwrite(mode="legacy", once=False)
            return func(*args, **kwargs)
        except Exception:
            return core.Status.Fail
        finally:
            BmcWeb.BMC_WEB.set_boot_overwrite(mode="uefi", once=False)
    return wrapper


def mark_skip_if(condition, reason=None, equal=True, value=None):
    """
    装饰器，当condition条件为True时，跳过测试;
    如果condition为函数实例, 并且函数(返回值)满足equal(是否等于)和value(预期值)的条件, 则跳过测试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_skip = False
            value_check = bool(value) if (value in [True, False, None]) else value
            if callable(condition):
                if equal and (condition() == value_check):
                    is_skip = True
                elif (not equal) and (condition() != value_check):
                    is_skip = True
            elif condition:
                is_skip = True

            if is_skip:
                if reason:
                    logging.warning(f"[TestSkip] Reason: {reason}")
                return core.Status.Skip
            return func(*args, **kwargs)
        return wrapper
    return decorator


def compare_file(path1, path2):
    """
        Compare the differences line by line for two object
        Parameters
        ----------
        path1:        file path
        path2:        file path 

        Returns
        -------
        list            if two object have any difference, return list of different strings
                        if two object have no difference, return empty list
        """
    if not os.path.exists(path1) or not os.path.exists(path2):
        logging.error(f"{path1} or {path2} is not exist")
        return
    difference = P.check_diff(path1, path2)
    return difference


def del_lines_from_file(contents, path):
    """删除以contents中字符串开头的行"""
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        for line in lines:
            if line != "\n":
                if line.strip().split()[0] not in contents:
                    f.write(line)
            else:
                f.write(line)


def match_config_version():
    """根据run_type的不同,自动切换版本 (解决多个项目共用代码问题)"""
    class Ver:
        ME = SutConfig.Env.ME_VER_LATEST
        RC = SutConfig.Env.RC_VER_LATEST
        MicroCode = SutConfig.Env.MICRO_CODE_LATEST
        BiosVer = SutConfig.Env.BIOS_VER_LATEST
        BiosDate = SutConfig.Env.BIOS_DATE_LATEST

    if var.get("run_type").lower() == "release":
        Ver.ME = SutConfig.Env.ME_VER_RELEASE
        Ver.RC = SutConfig.Env.RC_VER_RELEASE
        Ver.MicroCode = SutConfig.Env.MICRO_CODE_RELEASE
        Ver.BiosVer = SutConfig.Env.BIOS_VER_RELEASE
        Ver.BiosDate = SutConfig.Env.BIOS_DATE_RELEASE
    return Ver
