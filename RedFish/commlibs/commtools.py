# -*- encoding=utf8 -*-
import os
import time
import logging
import subprocess
import pandas
import RedFish.config as config


def loginfo(preinfo=None, postinfo=None):
    def func_decorator(func):
        def func_wrapper(*args, **kwargs):
            if isinstance(preinfo, str):
                logging.info(repr(preinfo))
            rtn = func(*args, **kwargs)
            if isinstance(postinfo, str):
                logging.info(repr(postinfo))
            return rtn
        return func_wrapper
    return func_decorator


def reboot_to_os(ssh_bmc, timeout=600):
    cmd_off = 'ipmcset -d powerstate -v 2\n'
    cmd_on = 'ipmcset -d powerstate -v 1\n'
    ret_ensure = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    if not ssh_bmc.login():
        logging.info("BMC login fail")
        return
    logging.info('Reboot SUT...')
    if not ssh_bmc.interaction([cmd_off, cmd_confirm, cmd_on, cmd_confirm], [ret_ensure, ret_confirm, ret_ensure, ret_confirm]):
        logging.info("Reboot SUT Failed")
        return
    logging.info("Reboot SUT successful, wait sut online...")
    ssh_bmc.close_session()
    time.sleep(30)
    return True if ping_sut(timeout=timeout) else False


def reboot_to_setup(ssh_bmc, serial, msg="Press Del go to Setup Utility", timeout=300):
    cmd_off = 'ipmcset -d powerstate -v 2\n'
    cmd_on = 'ipmcset -d powerstate -v 1\n'
    ret_ensure = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    if not ssh_bmc.login():
        logging.info("BMC login fail")
        return
    logging.info('Reboot SUT...')
    if not ssh_bmc.interaction([cmd_off, cmd_confirm, cmd_on, cmd_confirm], [ret_ensure, ret_confirm, ret_ensure, ret_confirm]):
        logging.info("Reboot SUT Failed")
        return
    logging.info("Reboot SUT successful, wait sut boot to setup...")
    ssh_bmc.close_session()
    if serial.waitString(msg=msg, timeout=timeout):
        return True


def ping_sut(ip=config.os_ip, timeout=180):
    logging.info("Ping OS IP Address: {} ...".format(ip))
    ping_cmd = 'ping {0}'.format(config.os_ip)
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        if 'TTL=' in stdoutput.decode('gbk'):
            logging.info("SUT is Online Now !")
            return True
        if time_spent > timeout:
            logging.info("Lost SUT for {} seconds, please check the OS ip".format(time_spent))
            return False


# 支持列表，字典和DataFrame转成excel文件
def to_excel(data, name="", path=os.path.abspath(config.REPORT_DIR)):
    if not os.path.exists(path):
        os.makedirs(path)
    now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    path_name = os.path.join(path, rf"{name} {now}.xlsx")
    if isinstance(data, list):
        pandas.Series(data).to_excel(path_name)
    elif isinstance(data, dict):
        pandas.DataFrame.from_dict(data, orient='index').to_excel(path_name)
    elif isinstance(data, pandas.DataFrame):
        data.to_excel(path_name)
    logging.info("Create excel {} successful!".format(path_name))
