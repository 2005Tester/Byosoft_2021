# -*- encoding=utf8 -*-
import paramiko
import datetime
import time
import re
import common
from common import ssh

STATUS_FAIL = 0
STATUS_PASS = 1
SUT = "192.168.2.100"
USERNAME = "Administrator"
PW = "Admin@9000"


def print_rawmsg(msg):
    common.prt.print_red_text('*'*50)
    common.prt.print_red_text(msg)
    common.prt.print_red_text('*'*50)


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
            common.prt.print_green_text("Upload bios to iBMC: PASS")
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
            common.prt.print_green_text("Upload bios to iBMC: PASS")
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
    s.connect(SUT,22,USERNAME, PW)
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
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    cmd_maint_mode = 'maint_debug_cli\n' 
    cmd_confirm = 'Y\n'
    cmd_upgrade_mode = 'attach upgrade\n'
    cmd_load = 'load_bios_bin /tmp/rp001.bin\n'
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(SUT, 22, USERNAME, PW)
    except Exception as e:
        print("Error in connecting SUT...")
        return STATUS_FAIL

    op = s.invoke_shell()
    res = ssh.send_command(cmd_shutdown, op)  # shutdown SUT
    if re.search("Do you want to continue", res.decode('utf-8')):
        print("Shutdown command sent to SUT successfully")
        res = ssh.send_command(cmd_confirm, op)  # confirm shutdown
        if re.search("Control fru0 forced power off successfully", res.decode('utf-8')):
            print("Shutdown successfully")
            res = ssh.send_command(cmd_maint_mode, op)
            if re.search("Debug Shell", res.decode('utf-8')):
                print("iBMC enter maintenance debug mode")
                res = ssh.send_command(cmd_upgrade_mode, op)  # attach upgrade mode
                if re.search("Success", res.decode('utf-8')):
                    print("iBMC attach upgrade successfullly")
                    start_time = time.time()
                    res = ssh.send_command(cmd_load)  # Load bios to SUT
                    # print(res.decode('utf-8'))
                    while re.search("load bios succefully",res.decode('utf-8')) == None:
                        print("Checking Status...")
                        res = op.recv(1024)
                        print(res.decode('utf-8'))
                        now = time.time()
                        if ((now - start_time)>600):
                            print("Porgraming Flash Device Timeout!!!")
                            op.close()
                            s.close()
                            return STATUS_FAIL
                    if re.search("load bios succefully",res.decode('utf-8')):
                            op.close()
                            s.close()
                            common.prt.print_green_text("Load bios to iBMC: PASS")
                            return STATUS_PASS         
                else:
                    print("iBMC Failed to attach upgrade")
                    print_rawmsg(res.decode('utf-8'))
                    op.close()
                    s.close()
                    return STATUS_FAIL             
            else:
                print("Failed to enter iBMC Enter Maintenance Debug Mode")
                print_rawmsg(res.decode('utf-8'))
                op.close()
                s.close()
                return STATUS_FAIL 
        else:
            print("Failed to shutdown SUT")
            print_rawmsg(res.decode('utf-8'))
            op.close()
            s.close()
            return STATUS_FAIL 
    else:
        print("Failed to Send Shutdown Command Sent to SUT")
        print_rawmsg(res.decode('utf-8'))
        op.close()
        s.close()
        return STATUS_FAIL 


def poweron_sut():
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    cmd_confirm = 'Y\n'

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(SUT,22,USERNAME, PW)
    op=s.invoke_shell()

    res = ssh.send_command(cmd_power_on, op)
    if re.search("Do you want to continue", res.decode('utf-8')):
        print("Power on command sent to SUT.")
        res = ssh.send_command(cmd_confirm, op) #confirm power on
        if re.search("Control fru0 power on successfully", res.decode('utf-8')):
            print("Power on successfully.")
            ssh.send_command(cmd_fan_manual_mode, op) #tune fan speed
            ssh.send_command(cmd_fan_40, op)
            common.prt.print_green_text("Power On SUT: PASS")
            return STATUS_PASS
        else:
            print("Failed to power on SUT.")
            print_rawmsg(res.decode('utf-8'))
            return STATUS_FAIL

    op.close()
    s.close()

if __name__ =='__main__':
    upload_bios()
    program_flash()
#    test()