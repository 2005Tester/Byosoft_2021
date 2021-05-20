import logging
import subprocess
import time

from Hygon.Config import SutConfig


# run command in windows,
def interaction(cmd, exp, timeout=5):
    logging.info("Run command: {0}".format(cmd))
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        if exp in stdoutput.decode('gbk'):
            logging.info("{0}".format(exp))
            break

        if time_spent > timeout:
            logging.error("Command run timeout - %s seconds, unable to find the expected result." % time_spent)
            return
    logging.debug(stdoutput.decode('gbk'))
    return True


# updated by arthur,
def is_power_on():
    logging.info("Check power status...")
    ret_cmd = '{0} chassis power status'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power is on')


def is_power_off():
    logging.info("Check power status...")
    ret_cmd = '{0} chassis power status'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power is off')


def power_off():
    logging.info("Starting to power off the SUT.")
    ret_cmd = '{0} chassis power off'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Down/Off')


def power_on():
    logging.info("Starting to power on the SUT.")
    ret_cmd = '{0} chassis power on'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Up/On')


def init_sut():
    logging.info("Init SUT power status to on...")
    try:
        if not is_power_on():
            logging.info("Chassis power is off.")
            raise AssertionError
        logging.info("Current power status is on, a power cycle operation is required.")
        assert power_cycle(), 'power cycle -> fail'
        return True
    except AssertionError:
        return power_on()


def power_reset():
    logging.info("Starting to power reset the SUT.")
    ret_cmd = '{0} chassis power reset'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Reset')


def power_cycle():
    logging.info("Starting to power cycle the SUT.")
    ret_cmd = '{0} chassis power cycle'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, 'Chassis Power Control: Cycle')


def set_language_to_eng():
    logging.info("Starting to set the default language to english.")
    ret_cmd = '{0} raw raw 0x3e 0xc3 0x01 0x0d 0 0x02 0x20 0x34 0x15 0x13 0x77 0x07 0x09 0x05 0 0x66'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, "")


def enable_console_direction():
    logging.info("Starting to enable console direction.")
    ret_cmd = '{0} raw raw 0x3e 0xc3 0x01 0x0d 0 0x02 0x20 0x34 0x15 0x12 0x77 0x07 0x09 0x05 0 0x66'.format(SutConfig.IPMITOOL)
    return interaction(ret_cmd, "")
