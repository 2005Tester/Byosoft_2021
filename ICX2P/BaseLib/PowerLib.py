import logging
from ICX2P import SutConfig


# update by arthur,
def is_power_off(ssh):
    logging.info("Check power status...")
    cmd_on = 'ipmcget -d powerstate\n'
    ret_confirm = 'Off'
    if ssh.login():
        ret = ssh.execute_command_interaction(cmd_on)
        if ret_confirm in ret.decode():
            logging.info('Current power state is Off')
            return True
        else:
            logging.info('Current power state is On')
            return


# power on SUT by BMC command
def power_on(ssh):
    logging.info("Power on system.")
    cmd_reset = 'ipmcset -d powerstate -v 1\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: Power on failed")
        return


# power off sut by BMC command
def power_off(ssh):
    logging.info("Power off system - force")
    cmd_reset = 'ipmcset -d powerstate -v 2\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("Power off failed")
        return


# Force reset SUT by BMC command
def force_reset(ssh):
    if is_power_off(ssh):
        if power_on(ssh):
            return True
    else:
        cmd_reset = 'ipmcset -d frucontrol -v 0\n'
        ret_reset = 'Do you want to continue'
        cmd_confirm = 'Y\n'
        ret_confirm = 'successfully'
        cmds = [cmd_reset, cmd_confirm]
        rets = [ret_reset, ret_confirm]
        if ssh.login():
            return ssh.interaction(cmds, rets)
        else:
            logging.error("Force system reset failed")
            return


# Force power cycle by BMC command
def force_power_cycle(ssh):
    logging.info("Force power cycle.")
    cmd_powercycle = 'ipmcset -d frucontrol -v 2\n'
    ret_powercycle = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_powercycle, cmd_confirm]
    rets = [ret_powercycle, ret_confirm]
    if ssh.login():
        return ssh.interaction(cmds, rets)
    else:
        logging.error("HY5 Common TC: force powercycle failed")
        return
