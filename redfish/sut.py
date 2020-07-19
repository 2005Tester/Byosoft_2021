# -*- encoding=utf8 -*-
import re
import requests
import paramiko
import time
import subprocess
import json
import config
import updatebios


def ping_sut():
    cmd_update_bios = r'python C:\UpdateTool\updatebios.py ' + config.BIOS
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=config.PING_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        output = stdoutput.decode()
        now = time.time()
        time_spent = (now-start_time)
        if output.find("TTL=") >=0:
            print("SUT is online now")
            break
        if time_spent > 900:
            print("Lost SUT for %s seconds, refresh BIOS image" % time_spent)
            try:
                updatebios.perform_update(config.BIOS)
                time.sleep(300)
                start_time = time.time()
            except Exception as e:
                print(e)


def rebootsut():
    cmd_shutdown = 'ipmcset -d powerstate -v 2\n'
    cmd_power_on = 'ipmcset -d powerstate -v 1\n'
    cmd_confirm = 'Y\n'
    cmd_fan_manual_mode = 'ipmcset -d fanmode -v 1 0\n'
    cmd_fan_40 = 'ipmcset -d fanlevel -v 40\n'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(config.sut, config.port, config.username, config.password, banner_timeout=150)
    except Exception as e:
        print("Error in connecting SUT...")
        time.sleep(300)
        rebootsut()
        return

    op = s.invoke_shell()

    def send_cmd(cmd):
        op.send(cmd)
        time.sleep(5)
        ret = op.recv(1024)
        return ret

    res = send_cmd(cmd_shutdown)  # shutdown SUT
    if re.search("Do you want to continue", res.decode('utf-8')):
        res = send_cmd(cmd_confirm)  # confirm shutdown
        if re.search("Control fru0 forced power off successfully", res.decode('utf-8')):
            print("Shutdown command sent to SUT.")
            time.sleep(10)
            res = send_cmd(cmd_power_on)
            if re.search("Do you want to continue", res.decode('utf-8')):
                res = send_cmd(cmd_confirm)  # confirm power on
                if re.search("Control fru0 power on successfully", res.decode('utf-8')):
                    print("Power on command sent to SUT.")
                    send_cmd(cmd_fan_manual_mode)  # tune fan speed
                    send_cmd(cmd_fan_40)
                    print("Booting SUT...")
                    time.sleep(30)
                    ping_sut()
    op.close()
    s.close()
    return


def get(url):
    headers = {
    'If-Match': 'W/"492eb2b8"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, verify = False)
    result = response.text
    response.close()
    return result


# 发送PATCH request 设置 testcase里面的值
def patch_tc_file(testcase_file, url):
    with open(testcase_file,'r') as fp:
        payload = json.load(fp)
    headers = {
    'If-Match': 'W/"584db857"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    etag = response.headers['ETag']
    headers['If-Match'] = etag
    response = requests.request("PATCH", url, headers=headers, data=payload, verify=False)
    response.close()
    return response.text.encode('utf8')


def patch_signle_payload(payload, url):
    # Payload 格式: payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" %(key, value)
    #key = list(payload["Attributes"].keys())[0]
    #value = payload["Attributes"][key]
    #if isinstance(value, int):
    #    payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%d\" \r\n    }\r\n}" %(key, value)
    #else:
    #    payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" %(key, value)
    headers = {
    'If-Match': 'W/"584db857"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify=False)
    etag = response.headers['ETag']
    headers['If-Match'] = etag
    response = requests.request("PATCH", url, headers=headers, data=payload, verify=False)
    response.close()
    return response.text.encode('utf8')