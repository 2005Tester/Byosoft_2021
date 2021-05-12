import logging
import time
from Core.SutInit import Sut
from Core import SshLib


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
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if Sut.BMC_SSH.login():
        return Sut.BMC_SSH.interaction(cmds, rets)
    else:
        logging.error("Power on failed")
        return


# power off sut by BMC command
def power_off():
    logging.info("[BmcLib.power_off]Power off system - force")
    cmd_reset = 'ipmcset -d powerstate -v 2\n'
    ret_reset = 'Do you want to continue'
    cmd_confirm = 'Y\n'
    ret_confirm = 'successfully'
    cmds = [cmd_reset, cmd_confirm]
    rets = [ret_reset, ret_confirm]
    if Sut.BMC_SSH.login():
        return Sut.BMC_SSH.interaction(cmds, rets)
    else:
        logging.error("Power off failed")
        return


# Force reset SUT by BMC command
def force_reset():
    if is_power_off():
        if power_on():
            return True
    else:
        cmd_reset = 'ipmcset -d frucontrol -v 0\n'
        ret_reset = 'Do you want to continue'
        cmd_confirm = 'Y\n'
        ret_confirm = 'successfully'
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
    ret_confirm = 'successfully'
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
    if is_power_off():
        pass
    else:
        if power_off():
            time.sleep(30)  # wait for 30s due to if in OS
            pass

    if Sut.BMC_SSH.login():
        return Sut.BMC_SSH.interaction(cmds, rets)
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
    cmd_shutdown = 'ipmcset -d powerstate -v 2\n'
    ret_shutdown = 'Do you want to continue'
    cmd_maint_mode = 'maint_debug_cli\n'
    ret_maint_mode = 'Debug Shell'
    cmd_confirm = 'Y\n'
    ret_confirm = 'Control fru0 forced power off successfully'
    cmd_upgrade_mode = 'attach upgrade\n'
    ret_upgrade_mode = 'Success'
    cmd_load = 'load_bios_bin /tmp/rp001.bin\n'
    ret_load = 'load bios succefully'
    cmds = [cmd_shutdown, cmd_confirm, cmd_maint_mode, cmd_upgrade_mode, cmd_load]
    rets = [ret_shutdown, ret_confirm, ret_maint_mode, ret_upgrade_mode, ret_load]
    return SshLib.interaction(Sut.BMC_SSH, cmds, rets)