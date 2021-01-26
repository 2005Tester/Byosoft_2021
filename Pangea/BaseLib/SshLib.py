from ICX2P import SutConfig
import logging

# Run one command return the result, no \n reqired for command
def execute_command(ssh, command):
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.execute_command(command)
    else:
        logging.info("SshLib: login failed.")
        return

# Run several commands through ssh in a row, and check return of all the commnads
# commands: list of commands, need to add \n for each command
# rets: return value of each command defined in above parameter
def interaction(ssh, commands, rets):
    if ssh.login(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD):
        return ssh.interaction(commands, rets)
    else:
        logging.info("SshLib: login failed.")
        return

