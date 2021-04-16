# -*- encoding=utf8 -*-

import sys
import os
import logging
import pandas
import time

sys.path.append(os.path.abspath(r"../../"))
from Common.ssh import SshConnection
from RedFish import config
from RedFish.commlibs.redfishlibs import RedFish
from RedFish.commlibs.commtools import reboot_to_setup


"""
【测试配置】
1. 配置 config 文件
    -   bmc_ip
    -   bmc_user
    -   bmc_pw
    -   COM
    -   os_ip
    -   os_user
    -   os_pw
    -   unitool_path
    -   AppExcel
2. AppExcel变量名那一列的名字需要修改为 AttributeName
3. 进入到Redfish文件夹，运行命令 RedFishTest.py power 开始测试
4. 测试完成后Excel报告保存在 config.REPORT_DIR 路径中

【测试步骤】
1. 按照能效菜单的Excel表格遍历修改能效菜单模式
2. 重启进OS后，使用Unitool检查所有相关选项的值，确认是否与预期相同，相同则PASS，不相同则返回实际当前值
4. Excel表格遍历完成后生成测试报告，以Excel格式保存
"""


def app_test(bmc, serial):
    """能效菜单测试,遍历检查每个能效菜单，其相关的选项Value是否正确"""

    # HY5和2288V6的菜单名不一样
    app_name_list = ["ApplicationProfile", "BenchMarkSelection"]

    os_ssh = SshConnection(config.os_ip, config.os_user, config.os_pw)
    pd = pandas.read_excel(config.AppExcel, sheet_name=0, index_col="AttributeName")
    rfish = RedFish(config.bmc_ip, config.bmc_user, config.bmc_pw)
    rfish.registry_dump("registry.json")  # 获取registry数据
    names = rfish.AttributeName_list()
    app_name = "".join([app for app in app_name_list if app in names])

    for ap in pd:
        logging.info("===============================================")
        logging.info('[Set] {} = "{}"'.format(app_name, ap))
        pd[ap + "_Check"] = ""

        # PATCH AppProfile选项
        if rfish.write(**{app_name: ap}) != 200:
            logging.info('Error: {} = {} PATCH Fail!'.format(app_name, repr(ap)))
            continue
        logging.info('{} = {} PATCH Pass!'.format(app_name, repr(ap)))

        # 重启后确认能效菜单是否为预期，并保存一份json文件
        reboot_to_setup(bmc, serial)
        if not rfish.check(**{app_name: ap}):
            logging.info('Current AppValue is "{}"'.format(rfish.read(app_name)))
            logging.info('Redfish Check: {} = {}  Fail'.format(app_name, repr(ap)))
            continue
        rfish.current_dump("{}.json".format(ap.replace("/", "")))
        logging.info('Redfish Check: {} = {}  Pass!'.format(app_name, repr(ap)))

        # 进入OS，unitool检查子选项的值
        if not os_ssh.login():
            continue
        os_ssh.ssh_client.exec_command(r'cd {};insmod ufudev.ko'.format(config.unitool_path))
        logging.info("Unitool driver installed")
        time.sleep(3)  # 进OS后等待3秒确保Unitool Driver加载完成

        for sub in pd[ap].index:
            result, get_val = unitool_check(os_ssh, sub, pd.loc[sub, ap])
            if not result:
                pd.loc[sub, ap + "_Check"] = get_val
                logging.info("[Check] {} = {} | fail ====-> {}".format(sub, pd.loc[sub, ap], get_val))
                continue
            pd.loc[sub, ap + "_Check"] = "pass"
            logging.info("[Check] {} = {} | pass".format(sub, get_val))
        pd = pd.sort_index(axis=1)
        pd.to_excel("{}_Test_Result.xlsx".format(app_name))


def unitool_check(ssh, option, value):
    value = int(str(value), 16) if "0x" in str(value) else int(value)
    stdin, stdout, stderr = ssh.ssh_client.exec_command(r'cd {};./unitool -r {} |grep value'.format(config.unitool_path, option))
    rcv_data = stdout.read().decode("utf-8").split(":")
    if len(rcv_data) != 2:
        return False, rcv_data
    get_value = int(rcv_data[1])
    return (get_value == value), get_value
