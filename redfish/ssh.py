# -*- encoding=utf8 -*-
import paramiko
import time
import re

class TestOverSsh:
    def __init__(self):
        self._transport = None
        self._channel = None

    def transport_connect(self,info):
        self._transport = paramiko.Transport((info[0], int(info[1])))  
        self._transport.start_client()
        self._transport.auth_password(info[2], info[3])
        self._channel = self._transport.open_session()
        self._channel.settimeout(7200)
        self._channel.get_pty()
        self._channel.invoke_shell()
        return self._transport,self._channel
    
    def transport_disconnect(self):
        if self._channel:
            self._channel.close()
        if self._transport:
            self._transport.close()

    def send(self,cmd,channel):
        commod = cmd
        cmd += '\r'
        p = re.compile(r']#')
        result = ''
        channel.send(cmd)
        while True:
            time.sleep(0.2)
            ret = channel.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            print(ret)
            if p.search(ret):
                break
        return result


    def sendMiddle(self,cmd,channel):
        commod = cmd
        cmd += '\r'
        channel.send(cmd)
        time.sleep(0.5)
        ret = channel.recv(65535)
        ret = ret.decode('utf-8')
        print(ret)
        return ret

class SshConnection:
    def __init__(self):
        self.session = None


    def newsession(self, info):
        self.session = paramiko.SSHClient()
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.session.connect(info[0], info[1], info[2], info[3])
            op = self.session.invoke_shell()
        except Exception as e:
            print(e)
        return op
        

    def interact(self, cmd_list):
        p = re.compile(r']#')
        for i in cmd:
            print("Sending command: %s" %(i))
            self.newsession.send(i+'\n')
            while True:
                #ready = op.receive
                time.sleep(0.2)
                res=op.recv(65536).decode('utf-8')
                print(res)
                if p.search(res):
                    break


def interact(host, port, username, password, cmd):
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(host,22,username, password)
    except Exception as e:
        print(e)
        print("Error in connecting SUT...")
        return 0
    op=s.invoke_shell()
    p = re.compile(r']#')
    for i in cmd:
        print("Sending command: %s" %(i))
        op.send(i+'\n')
        while True:
            time.sleep(0.2)
            res=op.recv(65536).decode('utf-8')
            print(res)
            if p.search(res):
                break
    op.close
    s.close


if __name__ == "__main__":
 
    sut = '192.168.34.5'
    port = '22'
    username = 'root'
    password = 'P@44w0rd321'
    cmd = ['yum update']
#    interact(sut, port, username, password, cmd)


    info = [sut, port,username,password]
    connect = SshConnection()
    connect.newsession(info)
    connect.interact(cmd)
#    transport = TestOverSsh()
#    channel = transport.transport_connect(info)[1]
#    transport.send('yum update',channel)
    
    #transport.send('dmesg',channel)
    #str1 = transport.sendMiddle('scp root@ip:/home/version/or.sh  /home/version',channel)

    #if ('Are you sure you want to continue connecting (yes/no)' in str1):
    #    transport.sendMiddle('yes',channel)
    #str1 = transport.sendMiddle('passwd',channel)
    #if('Permission denied, please try again'  in  str1):
    #str1 = transport.sendMiddle('passwd',channel)
    #transport.send('ls -l', channel)
