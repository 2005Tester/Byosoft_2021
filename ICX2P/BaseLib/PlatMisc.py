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
import datetime
import logging
import time
from PIL import Image
from ICX2P.Config import SutConfig
from ICX2P.Config.PlatConfig import Msg, Key
from ICX2P.BaseLib import BmcLib, SetUpLib
from Core.SutInit import Sut
from Core import SerialLib, SshLib


# OS - capture time,
def osTime(ssh):
    t1 = ''
    if ssh.login():
        logging.info("Capture time...")
        res = ssh.execute_command(r'hwclock --show')
        t = res.decode()
        t0 = t.split('.')[0]
        t1 = datetime.datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
        time.sleep(1)
    ssh.execute_command('reboot')
    return t1


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
        res = SshLib.execute_command(ssh, r'cd {0};./rw {1} {2} | grep {2}'.format(SutConfig.RW_PATH, cmd, mem_bar[i]))
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


# used for read register data, e,g cke power down and mem refresh mode
# sv.socket0.uncore.memss.mc0.ch0.cke_ll0.show
def cscripts_inband_register(cmd, exp_list, stop=-6):
    """
    :param cmd is a standard cscripts command,
            e.g sv.socket0.uncore.memss.mc0.ch0.cke_ll0.show()
    :param exp_list is a excepted data list,
            e.g ['0x00000000:ddrt_cke_en(24:24)', '0x00000000:ppd_en(09:09)']
    :stop from list index, default is -4
    """
    try:
        logging.info('Opening cscripts inband...')
        res_list = []
        cmds = ['cd {0}\n'.format(SutConfig.CSCRIPTS_PATH), 'pwd\n', './openCscripts.sh\n', '{0}\n'.format(cmd)]
        rets = ['', '{0}'.format(SutConfig.CSCRIPTS_PATH), 'Socket 0', '{0}'.format((exp_list[-1].split(':', 1)[0]).strip())]
        res = SshLib.interaction(Sut.OS_SSH, cmds, rets, timeout=15)[1]
        data = res.split('\r\n')[stop:]
        for i in range(len(data)):
            for j in data[i].split('--'):
                if '0x' in j:
                    res_list.append(j.replace(" ", ""))  # strip()
        time.sleep(0.01)
        logging.debug(res_list)
        if exp_list != res_list:
            logging.info('Data compared -> fail')
            return
        logging.info('Data compared -> pass')
        return True
    except Exception as err:
        logging.info('exp_list should be a non-empty list, not other types - {0}'.format(err))


def dcCycle():
    if not SetUpLib.boot_to_setup():
        return
    if not BmcLib.force_power_cycle():
        return
    logging.info("Booting to setup")
    if not SetUpLib.continue_to_setup():
        return
    return True


def last_release(current_branch, step=1):
    current_ver = int(current_branch[-3:])
    last_ver = "{:03}".format(current_ver - step)
    last_branch = Msg.RELEASE_BRANCH.format(last_ver)
    return last_branch


# sub function for dump cpu resource allocation table
def dump_cpu_resource():
    if not BmcLib.force_reset():
        return
    resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 10, 120)
    if not resource:
        return
    data_search = r"[\s\S]*".join([rf"CPU{n}[\s\S]*Ubox.+" for n in range(SutConfig.SysCfg.CPU_CNT)])
    rsc_table = re.search(data_search, resource)
    if not rsc_table:
        return
    lines = rsc_table.group().split("\n")
    result = []
    for line in lines:
        result.append(list(map(lambda x: x.strip(), line.split("|"))))
    csv_file = os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv")
    with open(os.path.join(SutConfig.LOG_DIR, "cpu_resource.csv"), "w", newline="") as rsc:
        csv_writer = csv.writer(rsc)
        csv_writer.writerows(result)
    return csv_file


# match all similar named options of one page
def match_options(key, patten, try_cnt=10):
    name_patten = re.compile(patten)
    SerialLib.clean_buffer(Sut.BIOS_COM)
    tmp_data = ""
    for i in range(try_cnt):
        SetUpLib.send_keys([key])
        tmp_data += SerialLib.recv_data(Sut.BIOS_COM, 1024)
    search_result = name_patten.findall(tmp_data)
    if not search_result:
        logging.info(f"No any options matched for '{patten}'")
        return
    menu_list = list(set(search_result))
    menu_list.sort(reverse=False)
    for port in menu_list:
        logging.info(f"Option '{port}' matched")
    return menu_list


# Check whether DVD-ROM exists in boot manager
def dvd_verify():
    logging.info("** Verify DVD exists ")
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Key.DOWN, ['[UEFILegacy] Boot'], 23, 'HDD Device')   # , 'DVD-ROM Drive  -page'   ,
        assert SetUpLib.verify_info(['DVD-ROM Device'], 4)
        logging.info(" DVD-ROM device found.")
        return True
    except AssertionError:
        logging.info("DVD-ROM device not found.")


# 标记Release测试状态，避免重复测试
class ReleaseTest:
    new_bios = None
    old_bios = None
    downgrade_tested = None
    registry_old = None
    registry_new = None
    hot_key_uefi = None
    hot_key_legacy = None
    pxe_boot_uefi = None
    pxe_boot_legacy = None


def read_bmc_dump_log(package_path, sub_path):
    log_path = os.path.join(package_path, sub_path)
    if not os.path.isfile(log_path):
        return
    with open(log_path) as log:
        return log.read()


# 检查dmesg信息种是否存在某个关键字，返回相应行组成的列表
# 比如检查 error, fail, 则 keywords = ["error", "fail]
def get_dmesg_keywords(keywords: list, ignore_list=None):
    ignore_list = [] if not ignore_list else list(ignore_list)
    err_lines = []
    for words in keywords:
        logging.info(f'Check is there any "{words}" in dmesg')
        dmesg_err = SshLib.execute_command(Sut.OS_SSH, f"dmesg |grep -i {words})")
        if not dmesg_err:
            logging.info(f'Check dmesg of "{words}" pass')
            continue
        for line in dmesg_err.splitlines():
            if any(re.search(ignore, line, re.I) for ignore in ignore_list):
                continue
            err_lines.append(err_lines)
            logging.info(f"Unexpected dmesg info: {line}")
    return err_lines


# cmd support: set / clear / check / sets / checks
# cmd support align with unipwd helping message
def unipwd_tool(cmd="set", password=""):
    cmd_support = ["set", "clear", "check", "sets", "checks"]
    password = "" if cmd == "clear" else password
    cd_path = f"cd {SutConfig.UNI_PATH}"
    ins_mod = f"insmod ufudev.ko"
    pwd_exec = f"./unipwd -{cmd} {password}"
    rtn_pass = f"{cmd} password success"
    try:
        assert cmd in cmd_support, f"{cmd} not in support list {cmd_support}"
        rtn = SshLib.execute_command(Sut.OS_SSH, f"{cd_path};{ins_mod};{pwd_exec}")
        assert rtn_pass in rtn.lower(), f"Unipwd {cmd} password failed"
        logging.info(f"Unipwd {cmd} password success")
        return True
    except Exception as e:
        logging.error(e)


# update logo with unilogo tool in linux
# 若path参数为空，则默认刷\Tools\Logo里的logo文件
def unilogo_update(name, path=""):
    cd_path = f"cd {SutConfig.UNI_PATH}"
    ins_mod = f"insmod ufudev.ko"
    logo_flash = f"./unilogo -logo ./{name}"
    rtn_pass = f"Update Logo.+success"
    try:
        if not path:
            logging.info(f"Update the logo in ..Tools/Logo/{name}")
            path = os.path.join(os.path.dirname(__file__), r"..\Tools\Logo")
            assert name in os.listdir(path), f"Logo name {name} not exist in directory: Tools/Logo"  # 检查name文件是否存在
        assert SshLib.sftp_upload_file(Sut.OS_SFTP, f"{path}/{name}", f"{SutConfig.UNI_PATH}/{name}", ret_msg="")
        rtn = SshLib.execute_command(Sut.OS_SSH, f"{cd_path};{ins_mod};{logo_flash}")
        assert rtn, f"execute_command for flash logo error: {rtn}"
        assert re.search(rtn_pass, rtn.lower(), re.I), f"Unilogo update logo failed:\n{rtn}"
        logging.info(f"Unilogo update logo success")
        return True
    except Exception as e:
        logging.error(e)


# 保存logo图片, 默认格式为bmp
def save_logo(path=SutConfig.LOG_DIR, name="logo", logo_loc=(88, 160, 248, 320)):
    now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    try:
        assert BmcLib.force_reset()
        SerialLib.clean_buffer(Sut.BIOS_COM)
        assert SerialLib.is_msg_present(Sut.BIOS_COM, Msg.LOGO_SHOW, 120)
        img_file = BmcLib.capture_kvm_screen(SutConfig.LOG_DIR, f"Screen_{now}")
        img_open = Image.open(img_file)  # 打开图片
        cut_logo = img_open.crop(logo_loc)  # logo裁剪
        cut_logo = cut_logo.convert("P", palette=Image.ADAPTIVE, colors=256)
        save_img = os.path.join(path, f"{name}.bmp")
        cut_logo.save(save_img, format="bmp", bits=8, quality=95)  # 保存裁剪部分
        assert os.path.isfile(save_img)
        logging.info(f"Save logo success: {save_img}")
        return save_img
    except Exception as e:
        logging.error(e)
