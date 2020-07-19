# -*- encoding=utf8 -*-
import paramiko
import time
import re
import ctypes

STATUS_FAIL = 0
STATUS_PASS = 1
SUT = "192.168.2.100"
USERNAME = "Administrator"
PW = "Admin@9000"



STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
 
FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01  # text color contains blue.
FOREGROUND_GREEN = 0x02  # text color contains green.
FOREGROUND_RED = 0x04  # text color contains red.
FOREGROUND_INTENSITY = 0x08  # text color is intensified.
 
BACKGROUND_BLUE = 0x10  # background color contains blue.
BACKGROUND_GREEN = 0x20  # background color contains green.
BACKGROUND_RED = 0x40  # background color contains red.
BACKGROUND_INTENSITY = 0x80  # background color is intensified.

class PrintColor:
    ''''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    for information on Windows APIs.'''
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
 
    def set_cmd_color(self, color, handle=std_out_handle):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool
 
    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
 
    def print_red_text(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
 
    def print_green_text(self, print_text):
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
 
    def print_blue_text(self, print_text):
        self.set_cmd_color(FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
 
    def print_red_text_with_blue_bg(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_BLUE | BACKGROUND_INTENSITY)
        print(print_text)
        self.reset_color()


prt = PrintColor()

def print_rawmsg(msg):
    prt.print_red_text('*'*50)
    prt.print_red_text(msg)
    prt.print_red_text('*'*50)


def upload_bios(src): #src: temp image directory, tmp/rp001.bin or tmp/bios.hpm 
     # Upload BIOS image (.bin. .hpm) to SUT
    bin_file = 'rp001.bin'
    hpm_file = 'bios.hpm'
    transport = paramiko.Transport(SUT, 22)
    transport.banner_timeout = 180  # Increase timeout value to fix connection issue
    transport.connect(username=USERNAME, password=PW)
    sftp = paramiko.SFTPClient.from_transport(transport)
    res = sftp.listdir()
    #print(res)  
    for item in res:
        if re.search(".bin",item):
            print("Deleting old .bin image...")
            sftp.remove(item)
        elif re.search(".hpm",item):
            print("Deleting old .hpm image...")
            sftp.remove(item)
    if re.search('.bin', src):
        try:
            res = sftp.put(src, bin_file)
        except OSError:
            print("Skip due to SSH connection error.")
            transport.close()
            return False
        if re.search("67108864", str(res)):
            print("BIOS image (bin) uploaded to iBMC SFTP.")
            transport.close()
            prt.print_green_text("Upload bios to iBMC: PASS")
            return True
        else:
            print("Failed to upload BIOS image to iBMC SFTP.")
            print_rawmsg(res)
            transport.close()
            return False
    elif re.search('.hpm', src):
        try:
            res = sftp.put(src, hpm_file)
        except OSError:
            print("Skip due to SSH connection error.")
            transport.close()
            return False
        if re.search("rw", str(res)):
            print("HPM image uploaded to iBMC SFTP.")
            transport.close()
            prt.print_green_text("Upload bios to iBMC: PASS")
            return False
        else:
            print("Failed to upload hpm image to iBMC SFTP.")
            print_rawmsg(res)
            transport.close()
            return False
    else:
        print("Invalid image type, please check source file...")
        transport.close()
        return False

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
        print_rawmsg(res)
        print("HPM Uploaded successfully, will perform upgrade on next reset")
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
        s.connect(SUT,22,USERNAME, PW, banner_timeout=180)
    except Exception as e:
        print("Error in connecting SUT...")
        return STATUS_FAIL

    op=s.invoke_shell()
    
    def send_cmd(cmd):
        op.send(cmd)
        time.sleep(5)
        res=op.recv(1024)
        return(res)

    res = send_cmd(cmd_shutdown)  #shutdown SUT
    if re.search("Do you want to continue", res.decode('utf-8')):
        print("Shutdown command sent to SUT successfully")
        res = send_cmd(cmd_confirm) #confirm shutdown
        if re.search("Control fru0 forced power off successfully", res.decode('utf-8')):
            print("Shutdown successfully")
            res = send_cmd(cmd_maint_mode)
            if re.search("Debug Shell", res.decode('utf-8')):
                print("iBMC enter maintenance debug mode")
                res = send_cmd(cmd_upgrade_mode) #attach upgrade mode
                if re.search("Success", res.decode('utf-8')):
                    print("iBMC attach upgrade successfullly")
                    start_time = time.time()
                    res = send_cmd(cmd_load) #Load bios to SUT   
                    #print(res.decode('utf-8'))               
                    while (re.search("load bios succefully",res.decode('utf-8'))==None):
                        print("Checking Status...")
                        res=op.recv(1024)
                        print(res.decode('utf-8'))
                        now = time.time()
                        if ((now - start_time)>300):
                            print("Porgraming Flash Device Timeout!!!")
                            op.close()
                            s.close()
                            return STATUS_FAIL
                    if re.search("load bios succefully",res.decode('utf-8')):
                            op.close()
                            s.close()
                            prt.print_green_text("Load bios to iBMC: PASS")
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
    s.connect(SUT,22,USERNAME, PW, banner_timeout=150)
    op=s.invoke_shell()
    def send_cmd(cmd):
        op.send(cmd)
        time.sleep(5)
        res=op.recv(1024)
        return(res)

    res = send_cmd(cmd_power_on)
    if re.search("Do you want to continue", res.decode('utf-8')):
        print("Power on command sent to SUT.")
        res = send_cmd(cmd_confirm) #confirm power on
        if re.search("Control fru0 power on successfully", res.decode('utf-8')):
            print("Power on successfully.")
            send_cmd(cmd_fan_manual_mode) #tune fan speed
            send_cmd(cmd_fan_40)
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
        Print("Upload BIOS image failed")
    if not program_flash():
        print("Program flash failed")
    poweron_sut()
     
