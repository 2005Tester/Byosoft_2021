# -*- encoding=utf8 -*-
import paramiko
import datetime
import time
import re
from Common import ssh
from Common import PrintColor
#from Common import Logger
#import logging

#logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s')

STATUS_FAIL = 0
STATUS_PASS = 1
SUT = "192.168.2.100"
USERNAME = "Administrator"
PW = "Admin@9000"

prt = PrintColor.PrintColor()

sshconn = ssh.SshConnection()

def print_rawmsg(msg):
    prt.print_red_text('*'*50)
    prt.print_red_text(msg)
    prt.print_red_text('*'*50)


def upload_bios(src):
    # Upload BIOS image (.bin. .hpm) to SUT
    bin_file = 'rp001.bin'
    hpm_file = 'bios.hpm'
    transport = paramiko.Transport(SUT, 22)
    transport.banner_timeout = 30  # Increase timeout value to fix connection issue
    transport.connect(username=USERNAME, password=PW)
    sftp = paramiko.SFTPClient.from_transport(transport)
    res = sftp.listdir()
    # print(res)
    for item in res:
        if re.search(".bin", item):
            print("Deleting old .bin image...")
            sftp.remove(item)
        elif re.search(".hpm", item):
            print("Deleting old .hpm image...")
            sftp.remove(item)
    if re.search('.bin', src):
        try:
            res = sftp.put(src, bin_file)
        except OSError:
            print("Skip due to SSH connection error.")
            return STATUS_FAIL
        if re.search("67108864", str(res)):
            print("BIOS image (bin) uploaded to iBMC SFTP.")
            transport.close()
            prt.print_green_text("Upload bios to iBMC: PASS")
            return STATUS_PASS
        else:
            print("Failed to upload BIOS image to iBMC SFTP.")
            print_rawmsg(res)
            transport.close()
            return STATUS_FAIL
    elif re.search('.hpm', src):
        try:
            res = sftp.put(src, hpm_file)
        except OSError:
            print("Skip due to SSH connection error.")
            return STATUS_FAIL
        if re.search("rw", str(res)):
            print("HPM image uploaded to iBMC SFTP.")
            transport.close()
            prt.print_green_text("Upload bios to iBMC: PASS")
            return STATUS_PASS
        else:
            print("Failed to upload hpm image to iBMC SFTP.")
            print_rawmsg(res)
            transport.close()
            return STATUS_FAIL
    else:
        print("Invalid image type, please check source file...")
        return STATUS_FAIL


def hpm_update():
    cmd_hpmupdate = 'ipmcset -d upgrade -v /tmp/bios.hpm\n'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(SUT,22,USERNAME,PW)
    op=s.invoke_shell()
    op.send(cmd_hpmupdate)
    time.sleep(5)
    res=op.recv(1024)
    if re.search('successfully',res.decode('utf-8')):
        # print_rawmsg(res)
        print("HPM Uploaded successfully, upgrade on next reboot")
        op.close()
        s.close()
        return STATUS_PASS  
    else:
        print("Failed to perform HPM upgrade")
        print_rawmsg(res)
        op.close()
        s.close()
        return STATUS_FAIL  


def program_flash():
    # Program flash procedure: power off->maint mode->attach upgrade ->load bin
    cmd_shutdown = 'ipmcset -d powerstate -v 2\n'
    ret_shutdown = 'Do you want to continue'
    cmd_maint_mode = 'maint_debug_cli\n'
    ret_maint_mode = 'Debug Shell'
    cmd_confirm = 'Y\n'
    ret_confirm = 'Control fru0 forced power off successfully'
    cmd_upgrade_mode = 'attach upgrade\n'
    ret_upgrade_mode = 'Success'
    cmd_load = 'load_bios_bin /tmp/rp001.bin\n'
    cmds = [cmd_shutdown, cmd_confirm, cmd_maint_mode, cmd_upgrade_mode, cmd_load]
    rets = [ret_shutdown, ret_confirm, ret_maint_mode, ret_upgrade_mode, "load bios succefully"]
    
    if sshconn.login(SUT, USERNAME, PW):
        return(sshconn.interaction(cmds, rets))
        
    #    if sshconn.is_command_success(cmd_load, "load bios succefully"):
    #        return True

    """    
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(SUT, 22, USERNAME, PW)
    except Exception as e:
        print("Error in connecting SUT...")
        return False

    op = s.invoke_shell()
    if not ssh.call_commands(cmds, rets, op):
        op.close()
        s.close()
        return False
    res = ssh.send_command(cmd_load, op)  # Load bios to SUT
    print(res.decode('utf-8'))
    print("Sending command: %s" % cmd_load)
    start_time = time.time()
    while not re.search("load bios succefully", res.decode('utf-8')):
        print("Checking Status...")
        res = op.recv(1024)
        print(res.decode('utf-8'))
        now = time.time()
        if (now - start_time) > 60:
            print("Porgraming Flash Device Timeout!!!")
            status = False
        if re.search("load bios succefully", res.decode('utf-8')):
            prt.print_green_text("Load bios to iBMC: PASS")
            status = True
    return status
    """
   
  
def poweron_sut():
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    cmd_confirm = 'Y\n'

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(SUT, 22, USERNAME, PW)
    op = s.invoke_shell()
    res = ssh.send_command(cmd_power_on, op)
    if re.search("Do you want to continue", res.decode('utf-8')):
        print("Power on command sent to SUT.")
        res = ssh.send_command(cmd_confirm, op) # confirm power on
        if re.search("Control fru0 power on successfully", res.decode('utf-8')):
            print("Power on successfully.")
            ssh.send_command(cmd_fan_manual_mode, op) # tune fan speed
            ssh.send_command(cmd_fan_40, op)
            prt.print_green_text("Power On SUT: PASS")
            return STATUS_PASS
        else:
            print("Failed to power on SUT.")
            print_rawmsg(res.decode('utf-8'))
            return STATUS_FAIL

    op.close()
    s.close()


def perform_update(bios):
    if not upload_bios(bios):
        print("Upload BIOS image failed")
    if not program_flash():
        print("Program flash failed")
    poweron_sut()

if __name__ == '__main__':
    upload_bios()
    program_flash()
