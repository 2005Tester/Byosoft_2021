#coding='utf-8'
from abc import abstractstaticmethod
import datetime
from typing import Set
import requests
import re
import time
import subprocess
import logging
from Inspur7500.Base import HDDPassword
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from batf.Report import stylelog



def frb2_watchdog():
    count=0
    logging.info('FRB2 Watchdog禁用，POST测试..................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.CLOSE_FRB,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN,20):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()

    if status=='Stopped' and action=='No action' and times=='0':
        logging.info('FRB2定时器禁用，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器禁用，ipmitool与setup不一致,{0}{1}{2}'.format(status,action,times))
        count+=1
    logging.info('FRB2 Watchdog开启，POST测试..................................')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.OPEN_FRB1,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN,20):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()

    if status=='Started/Running' and action=='Hard Reset' and times=='600':
        logging.info('FRB2定时器启用，重启，10分钟，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器启用，重启，10分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.OPEN_FRB2,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN,20):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()

    if status=='Started/Running' and action=='Power Down' and times=='1800':
        logging.info('FRB2定时器启用，关闭电源，30分钟，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器启用，关闭电源，30分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.OPEN_FRB3,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN,20):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()
    if status=='Started/Running' and action=='Hard Reset' and times=='300':
        logging.info('FRB2定时器启用，重启，5分钟，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器启用，重启，5分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    logging.info('FRB2 Watchdog禁用，BIOS密码测试..................................')
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter('Admin@001')
    time.sleep(1)
    SetUpLib.send_data('Admin@001')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_SETUP_PSW_SUCCESS,3):
        logging.info('管理员密码设置成功')
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_key(Key.DEL)
    if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,10):
        assert SetUpLib.boot_with_hotkey(Key.DEL,SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT,300,SutConfig.Msg.POST_MESSAGE)
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    if status=='Stopped' and action=='No action' and times=='0':
        logging.info('设置BIOS密码后，POST界面自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('设置BIOS密码后，POST界面没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status,action,times))
        count+=1
    SetUpLib.send_data_enter('Admin@001')
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN,20):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Psw.LOC_ADMIN_PSW,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Admin@001')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Psw.DEL_SETUP_PSW_SUCCESS,3):
        logging.info('密码删除')
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    logging.info('FRB2 Watchdog禁用，硬盘密码测试..................................')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.LOC_HDD_PSW,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDDPassword.HDD_NAME_01],3,2):
        if not SetUpLib.locate_option(Key.UP,[HDDPassword.HDD_NAME_01],3,2):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.SET_HDD_PSW_OPTION],3,2):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Psw.SET_HDD_PSW_OPTION],3,2):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd12345')
    time.sleep(1)
    SetUpLib.send_data('hdd12345')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_HDD_PSW_SUCCESS,5):
        logging.info('硬盘密码设置成功')
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    BmcLib.enable_serial_normal()
    if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    if status=='Stopped' and action=='No action' and times=='0':
        logging.info('设置硬盘密码后，POST界面自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('设置硬盘密码后，POST界面没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status,action,times))
        count+=1
    SetUpLib.send_data('hdd12345')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.DEL)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN_CN):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Psw.LOC_HDD_PSW,16)
    if not SetUpLib.locate_option(Key.DOWN,[HDDPassword.HDD_NAME_01],5,2):
        if not SetUpLib.locate_option(Key.UP,[HDDPassword.HDD_NAME_01],5,2):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Psw.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd12345')
    if SetUpLib.wait_message_enter(SutConfig.Psw.SET_HDD_PSW_SUCCESS):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    if count==0:
        return True
    else:
        return



def os_watchdog():
    count=0
    logging.info('OS Watchdog启用测试..................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.OPEN_OS_WDOG1,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    if status=='Started/Running' and action=='Power Down' and times=='600':
        logging.info('系统定时器启用，关闭电源，10分钟，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器启用，关闭电源，10分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_OS_WDOG2, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')

    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    if status=='Started/Running' and action=='Hard Reset' and times=='1800':
        logging.info('系统定时器启用，重启，30分钟，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器启用，重启，30分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_OS_WDOG3, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')

    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    if status=='Started/Running' and action=='Hard Reset' and times=='300':
        logging.info('系统定时器启用，重启，5分钟，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器启用，重启，5分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    
    assert SetUpLib.boot_to_setup()
    logging.info('OS Watchdog禁用测试..................................')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.CLOSE_OS_WDOG, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    arg='{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
  
    status=re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)',stdoutput)[0]
    action=re.findall(r'Watchdog Timer Actions: +(.*) \(',stdoutput)[0]
    times=re.findall(r'Initial Countdown: +(.*?) sec',stdoutput)[0]
    if status=='Stopped' and action=='No action' and times=='0':
        logging.info('系统定时器禁用，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器禁用，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status,action,times))
        count+=1
    if count==0:
        return True
    else:
        return



def power_loss():
    count=0
    logging.info('Setup修改，BMC验证.....................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.SET_POWER_LOSS1,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    arg='{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)',stdoutput)[0]
    if status=='always-on':
        logging.info('setup下修改电源丢失策略为上电，BMC为上电，一致')
    else:
        stylelog.fail('setup下修改电源丢失策略为上电，BMC为{0}，一致'.format(status))
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.SET_POWER_LOSS2,18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    arg='{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)',stdoutput)[0]
    if status=='previous':
        logging.info('setup下修改电源丢失策略为上次状态，BMC为上次状态，一致')
    else:
        stylelog.fail('setup下修改电源丢失策略为上次状态，BMC为{0}，一致'.format(status))
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.SET_POWER_LOSS3, 18)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    arg='{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    status=re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)',stdoutput)[0]

    if status=='always-off':
        logging.info('setup下修改电源丢失策略为保持关闭，BMC为保持关闭，一致')
    else:
        stylelog.fail('setup下修改电源丢失策略为保持关闭，BMC为{0}，一致'.format(status))
        count+=1
    logging.info('BMC修改，SetUp验证.....................................')
    arg='{0} chassis policy always-on'.format(SutConfig.Env.IPMITOOL)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC修改电源策略为上电')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_SERVICE,18)
    data=SetUpLib.get_data(3)
    if re.search(r'{0} *Restore AC Power Loss'.format(SutConfig.Ipm.POWER_LOSS_VALUE[0]), data):
        logging.info('BMC修改电源策略为上电，Setup下为上电，一致')
    else:
        stylelog.fail('BMC修改电源策略为上电，Setup下为{0}，不一致'.format(re.findall(r'Mgmt *<(.+)> *Restore AC Power Loss',data)))
        count+=1
    arg='{0} chassis policy previous'.format(SutConfig.Env.IPMITOOL)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC修改电源策略为上次状态')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_SERVICE,18)
    data=SetUpLib.get_data(3)

    if re.search(r'{0} *Restore AC Power Loss'.format(SutConfig.Ipm.POWER_LOSS_VALUE[1]), data):
        logging.info('BMC修改电源策略为上次状态，Setup下为上次状态，一致')
    else:
        stylelog.fail('BMC修改电源策略为上次状态，Setup下为{0}，不一致'.format(re.findall(r'Mgmt *<(.+)> *Restore AC Power Loss',data)))
        count+=1
    arg='{0} chassis policy always-off'.format(SutConfig.Env.IPMITOOL)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC修改电源策略为保持关闭')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_SERVICE,18)
    data=SetUpLib.get_data(3)
    if re.search(r'{0} *Restore AC Power Loss'.format(SutConfig.Ipm.POWER_LOSS_VALUE[2]), data):
        logging.info('BMC修改电源策略为保持关闭，Setup下为保持关闭，一致')
    else:
        stylelog.fail('BMC修改电源策略为上次保持关闭，Setup下为{0}，不一致'.format(re.findall(r'Mgmt *<(.+)> *Restore AC Power Loss',data)))
        count+=1
    if count==0:
        return True
    else:
        return 



def oem():

    count=0
    logging.info('获取BIOS默认设置.............................')
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(5)
    subprocess.Popen(args=SutConfig.Env.UEFI_SETUP_ONCE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC 修改SETUP启动一次')
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(150)
    arg='{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    result=stdoutput.decode('gbk').strip()
    if result==SutConfig.Ipm.OEM_DEFAULT_VALUE:
        logging.info('ipmitool返回结果一致,返回结果为{0}'.format(result))
    else:
        stylelog.fail('ipmitool返回结果不一致，返回结果为{0}'.format(result))
        count+=1
    logging.info('修改BIOS设置.............................')
    arg='{0} raw 0x3e 0xc3 0x01 0x02 0x31 0x04 0x32 0x04 0x15 0x13 0x56 0x5a 0x18 0x0a 0x00 0x09'.format(SutConfig.Env.IPMITOOL)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Run {0}'.format(arg))
    subprocess.Popen(args=SutConfig.Env.UEFI_SETUP_ONCE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC 修改SETUP启动一次')
    BmcLib.init_sut()
    time.sleep(150)
    arg='{0} raw 0x3e 0xc2'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    result=stdoutput.decode('gbk').strip()
    if result=='00 02 31 04 32 04 15 13 56 5a 18 0a 00 09':
        logging.info('ipmitool返回结果一致,返回结果为{0}'.format(result))
    else:
        stylelog.fail('ipmitool返回结果不一致，返回结果为{0}'.format(result))
        count+=1

    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    logging.info('语言=英语')
    time.sleep(1)
    assert SetUpLib.enter_menu(Key.DOWN,SutConfig.Ipm.LOC_CONSOLE,5)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    if 'Console Redirection' in data:
        if re.search('<Enabled> *Console Redirection',data):
            logging.info('串口重定向=开启')
        else:
            stylelog.fail('串口重定向修改失败，串口重定向:{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Console Redirection',data)))
            count+=1
    else:
        logging.info('没有串口重定向这个选项，不验证')
    if 'Serial Port Baudrate' in data:
        if re.search('<115200> *Serial Port Baudrate', data):
            logging.info('串口波特率=115200')
        else:
            stylelog.fail('串口波特率修改失败，串口波特率:{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Serial Port Baudrate', data)))
            count += 1
    else:
        logging.info('没有串口波特率这个选项，不验证')
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_LAN,10)
    data=SetUpLib.get_data(2)
    if 'Onboard Ethernet Controller' in data:
        if re.search('<Enabled> *Onboard Ethernet Controller',data):
            logging.info('板载网卡控制=打开')
        else:
            stylelog.fail('板载网卡控制修改失败，板载网卡控制：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Onboard Ethernet Controller',data)))
            count+=1
    else:
        logging.info('没有板载网卡控制这个选项，不验证')
    if 'Wake On Lan' in data:
        if re.search('<Disabled> *Wake On Lan',data):
            logging.info('网络唤醒=关闭')
        else:
            stylelog.fail('网络唤醒修改失败，网络唤醒：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Wake On Lan',data)))
            count+=1
    else:
        logging.info('没有网络唤醒这个选项，不验证')

    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_VIDEO,10)
    data=SetUpLib.get_data(2)
    if 'Primary Graphics Adapter' in data:
        if re.search('<IGD> *Primary Graphics Adapter',data):
            logging.info('优先显示控制器=板载显卡')
        else:
            stylelog.fail('优先显示控制器修改失败，优先显示控制器：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Primary Graphics Adapter',data)))
            count+=1
    else:
        logging.info('没有优先显示控制器这个选项，不验证')



    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_USB,10)
    data=SetUpLib.get_data(2)
    if 'USB Mass Storage Support' in data:
        if re.search('<Disabled> *USB Mass Storage Support',data):
            logging.info('USB存储设备支持=关闭')
        else:
            stylelog.fail('USB存储设备支持修改失败，USB存储设备支持：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *USB Mass Storage Support',data)))
            count+=1
    else:
        logging.info('没有USB存储设备支持这个选项，不验证')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_USB_PORT,3)
    data=SetUpLib.get_data(2)
    if 'Rear USB port Configuration' in data:
        if re.search('<Disabled> *Rear USB port Configuration',data):
            logging.info('后置USB端口配置=关闭')
        else:
            stylelog.fail('后置USB端口配置修改失败，后置USB端口配置：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Rear USB port Configuration',data)))
            count+=1
    else:
        logging.info('没有后置USB端口配置这个选项，不验证')

    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_VIRTU,10)
    data=SetUpLib.get_data(2)
    if 'IOMMU' in data:
        if re.search('<Disabled> *IOMMU',data):
            logging.info('IOMMU=禁用')
        else:
            stylelog.fail('IOMMU修改失败，IOMMU：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *IOMMU',data)))
            count+=1
    else:
        logging.info('没有IOMMU这个选项，不验证')
    if 'SVM' in data:
        if re.search('<Disabled> *SVM',data):
            logging.info('SVM=禁用')
        else:
            stylelog.fail('SVM修改失败，SVM：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *SVM',data)))
            count+=1
    else:
        logging.info('没有SVM这个选项，不验证')
    if 'SR-IOV Support' in data:
        if re.search('<Disabled> *SR\-IOV Support',data):
            logging.info('SR-IOV支持=关闭')
        else:
            stylelog.fail('SR-IOV支持修改失败，SR-IOV支持：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *SR\-IOV Support',data)))
            count+=1
    else:
        logging.info('没有SR-IOV支持这个选项，不验证')
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_MISC,10)
    data=SetUpLib.get_data(2)
    if 'SPI BIOS Lock' in data:
        if re.search('<Enabled> *SPI BIOS Lock',data):
            logging.info('SPI BIOS锁=打开')
        else:
            stylelog.fail('SPI BIOS锁修改失败，SPI BIOS锁：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *SPI BIOS Lock',data)))
            count+=1
    else:
        logging.info('没有SPI BIOS锁这个选项，不验证')
    if 'PCIE Max Payload Size' in data:
        if re.search('<512B> *PCIE Max Payload Size',data):
            logging.info('PCIE最大负载=512B')
        else:
            stylelog.fail('PCIE最大负载修改失败，PCIE最大负载：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *PCIE Max Payload Size',data)))
            count+=1
    else:
        logging.info('没有PCIE最大负载这个选项，不验证')
    if 'PCIE ASPM' in data:
        if re.search('<L1> *PCIE ASPM',data):
            logging.info('PCIE活动状态电源管理=L1')
        else:
            stylelog.fail('PCIE活动状态电源管理修改失败，PCIE活动状态电源管理：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *PCIE ASPM',data)))
            count+=1
    else:
        logging.info('没有PCIE活动状态电源管理这个选项，不验证')
    if 'Hyper Threading Technology' in data:
        if re.search('<Disabled> *Hyper Threading Technology',data):
            logging.info('超线程技术=关闭')
        else:
            stylelog.fail('超线程技术修改失败，超线程技术：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Hyper Threading Technology',data)))
            count+=1
    else:
        logging.info('没有超线程技术这个选项，不验证')
    if 'ENERGY_PERF_BIAS_CFG mode' in data:
        if re.search('<User Defined> *ENERGY_PERF_BIAS_CFG mode',data):
            logging.info('性能模式=用户自定义')
        else:
            stylelog.fail('性能模式修改失败，性能模式：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *ENERGY_PERF_BIAS_CFG mode',data)))
            count+=1
    else:
        logging.info('没有性能模式这个选项，不验证')
    if 'CPU P-State Control' in data:
        if re.search('<P0\+P1\+P2> *CPU P\-State Control',data):
            logging.info('CPU P-State控制=P0+P1+P2')
        else:
            stylelog.fail('CPU P-State控制修改失败，CPU P-State控制：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *CPU P\-State Control',data)))
            count+=1
    else:
        logging.info('没有CPU P-State控制这个选项，不验证')
    if 'CPU C-State Control' in data:
        if re.search('<Enabled> *CPU C\-State Control',data):
            logging.info('CPU C-State控制=打开')
        else:
            stylelog.fail('CPU C-State控制修改失败，CPU C-State控制：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *CPU C\-State Control',data)))
            count+=1
    else:
        logging.info('没有CPU C-State控制这个选项，不验证')
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_ERR,10)
    data=SetUpLib.get_data(2)
    if 'Platform First Error Handling' in data:
        if re.search('<Disabled> *Platform First Error Handling',data):
            logging.info('错误管理=关闭')
        else:
            stylelog.fail('错误管理修改失败，错误管理：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Platform First Error Handling',data)))
            count+=1
    else:
        logging.info('没有错误管理这个选项，不验证')
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.OPEN_ERR,3)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)
    if 'MCA Error Threshold Count' in data:
        if re.search('<10> *MCA Error Threshold Count',data):
            logging.info('MCA错误数量控制=10')
        else:
            if re.search('<1500> *MCA Error Threshold Count',data):
                logging.info('MCA错误数量控制=1500')
            else:
                stylelog.fail('MCA错误数量控制修改失败，MCA错误数量控制：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *MCA Error Threshold Count',data)))
                count+=1
    else:
        logging.info('没有MCA错误数量控制这个选项，不验证')
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_HYGON,10)
    data=SetUpLib.get_data(2)
    if 'Core Performance Boost' in data:
        if re.search('<Disabled> *Core Performance Boost', data):
            logging.info('核心性能提升=禁用')
        else:
            stylelog.fail('核心性能提升修改失败，核心性能提升：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Core Performance Boost', data)))
            count += 1
    else:
        logging.info('没有核心性能提升这个选项，不验证')
    if 'NUMA' in data:
        if re.search('<Channel> *NUMA', data):
            logging.info('NUMA=通道')
        else:
            stylelog.fail('NUMA修改失败，NUMA：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *NUMA', data)))
            count += 1
    else:
        logging.info('没有NUMA这个选项，不验证')
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY_CN)
    SetUpLib.send_key(Key.RIGHT)
    data=SetUpLib.get_data(2)

    if 'User Wait Time' in data:
        if re.search('\[10\] *User Wait Time', data):
            logging.info('用户等待时间=[10]')
        else:
            stylelog.fail('用户等待时间修改失败，用户等待时间：{0}'.format(re.findall('\[(\w[\w -/]*[\w\)])\] *User Wait Time', data)))
            count += 1
    else:
        logging.info('没有用户等待时间这个选项，不验证')
    if 'Quiet Boot' in data:
        if re.search('<Enabled> *Quiet Boot', data):
            logging.info('安静启动=打开')
        else:
            stylelog.fail('安静启动修改失败，安静启动：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Quiet Boot', data)))
            count += 1
    else:
        logging.info('没有安静启动这个选项，不验证')
    if 'Bootup NumLock State' in data:
        if re.search('<Off> *Bootup NumLock State', data):
            logging.info('数字锁定键开机状态=关闭')
        else:
            stylelog.fail('数字锁定键开机状态修改失败，安静启动：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Bootup NumLock State', data)))
            count += 1
    else:
        logging.info('没有数字锁定键开机状态这个选项，不验证')
    if 'Boot Mode' in data:
        if re.search('<UEFI> *Boot Mode', data):
            logging.info('启动模式=UEFI')
        else:
            stylelog.fail('启动模式修改失败，安静启动：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Boot Mode', data)))
            count += 1
    else:
        logging.info('没有启动模式这个选项，不验证')
    if 'Internal SHELL' in data:
        if re.search('<Enabled> *Internal SHELL', data):
            logging.info('内置SHELL=打开')
        else:
            stylelog.fail('内置SHELL修改失败，内置SHELL：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Internal SHELL', data)))
            count += 1
    else:
        logging.info('没有内置SHELL这个选项，不验证')
    if 'PXE Boot Options Retry' in data:
        if re.search('<Disabled> *PXE Boot Options Retry', data):
            logging.info('网络启动重试=关闭')
        else:
            stylelog.fail('网络启动重试修改失败，网络启动重试：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *PXE Boot Options Retry', data)))
            count += 1
    else:
        logging.info('没有网络启动重试这个选项，不验证')
    if 'Net Boot IP Version' in data:
        if re.search('<IPv6> *Net Boot IP Version', data):
            logging.info('网络引导IP版本=IPv6')
        else:
            stylelog.fail('网络引导IP版本修改失败，网络引导IP版本：{0}'.format(re.findall('<(\w[\w -/]*[\w\)])> *Net Boot IP Version', data)))
            count += 1
    else:
        logging.info('没有网络引导IP版本这个选项，不验证')
    if re.search('UEFI Boot Order.*USB Flash Drive/USB Hard Disk.*USB CD/DVD ROM Drive.*Network Adapter.*Internal Hard Drive.*Others',data):
        logging.info('启动顺序为：U盘->光驱->网络->硬盘->其他')
    else:
        stylelog.fail('启动顺序修改失败，启动顺序为{0}'.format(re.findall('UEFI Boot Order(.*)Legacy Boot Order',data)[0].replace('►','').replace(' ','')))
        count+=1
    time.sleep(2)
    SetUpLib.send_keys(Key.RESET_DEFAULT)
    time.sleep(5)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)

    if count==0:
        return True
    else:
        return



def bmc_user():
    count=0
    logging.info('SetUp端.....................................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_USER_CONF,18)
    logging.info('Setup下新增bmc用户时，输入不符合要求的用户名，提示失败..........................')
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.ADD_USER],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.ADD_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    passwords=['a123','1234a','a123@']
    for password in passwords:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_data(password)
        time.sleep(2)
        if SetUpLib.wait_message_enter(SutConfig.Ipm.USER_NAME_NOT_MATCH,3):
            logging.info('用户名不符合规范')
        else:
            return
        SetUpLib.send_key(Key.ENTER)
    logging.info('Setup下新增bmc用户时，输入存在的用户名，提示失败.....................')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('Root_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_1',10):
        logging.info('用户名设置Root_1成功')
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.DEL_USER], 5):
            assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.DEL_USER], 5)
        SetUpLib.send_key(Key.ENTER)
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
            assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data('Root_1')
        time.sleep(1)
        if SetUpLib.wait_message_enter('Root_1',8):
            pass
        else:
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data('Root@root11')
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Ipm.DEL_USER_SUCCESS):
            logging.info('删除用户成功')
            SetUpLib.send_key(Key.ENTER)
        else:
            return
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.ADD_USER], 5):
            assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.ADD_USER], 5)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_data('Root_1')
        time.sleep(1)
        if SetUpLib.wait_message_enter('Root_1', 10):
            logging.info('用户名设置Root_1成功')
        else:
            return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Root@root1')
    time.sleep(1)
    SetUpLib.send_data('Root@root1')
    if SetUpLib.wait_message_enter(SutConfig.Ipm.SET_PSW_SUCCESS,3):
        logging.info('用户密码设置成功')

    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root_1')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Ipm.USER_NAME_EXITS,10):
        logging.info('新增bmc用户时，输入存在的用户名，提示失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    for i in stdoutput.split('\\n'):
        if 'Root_1' in i:
            userid=i.split(' ')[0]
    if 'Root_1' in stdoutput:
        logging.info(' Setup下新增bmc用户后，ipmitool user list中有该用户')
    else:
        stylelog.fail(' Setup下新增bmc用户后，ipmitool user list中没有该用户')
        count+=1
    logging.info('Setup下Changer User...........................')
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_1',10):
        logging.info('输入用户名Root_1')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root00')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ERROR_PSW,10):
        logging.info('修改密码，输入错误密码，提示失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW,10):
        logging.info('修改密码，输入正确密码后，用户密码，变为修改用户密码')
    else:
        return


    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CNANGE_USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Root@root11')
    time.sleep(1)
    SetUpLib.send_data('Root@root11')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.SET_PSW_SUCCESS,10):
        logging.info('修改密码为Root@root11成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    arg='{0} user test {1} 20 Root@root11'.format(SutConfig.Env.IPMITOOL, userid)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    if re.search('Success',stdoutput):
        logging.info('Ipmitool下密码更改成功')
    else:
        stylelog.fail('Ipmitool下密码更改失败,提示{0}'.format(stdoutput))
        count+=1
    
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_1',10):
        logging.info('输入用户名Root_1')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root11')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW,10):
        pass
    else:
        return
    
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Ipm.USER_PRIVILEGE],6,SutConfig.Ipm.CALLBACK)
    time.sleep(3)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    for i in stdoutput.split('\\n'):
        if 'Root_1' in i:
            if 'CALLBACK' in i:
                logging.info('SetUp下更改权限为回叫，ipmitool返回CALLBACK')
            else:
                stylelog.fail('SetUp下更改权限为回叫，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count+=1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Ipm.USER_PRIVILEGE],6,SutConfig.Ipm.USER)
    time.sleep(3)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    for i in stdoutput.split('\\n'):
        if 'Root_1' in i:
            if 'USER' in i:
                logging.info('SetUp下更改权限为用户，ipmitool返回USER')
            else:
                stylelog.fail('SetUp下更改权限为用户，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count+=1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Ipm.USER_PRIVILEGE],6,SutConfig.Ipm.OPERATOR)
    time.sleep(3)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    for i in stdoutput.split('\\n'):
        if 'Root_1' in i:
            if 'OPERATOR' in i:
                logging.info('SetUp下更改权限为操作人，ipmitool返回OPERATOR')
            else:
                stylelog.fail('SetUp下更改权限为操作人，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count+=1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Ipm.USER_PRIVILEGE],7,SutConfig.Ipm.ADMIN)
    time.sleep(3)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    for i in stdoutput.split('\\n'):
        if 'Root_1' in i:
            if 'ADMINISTRATOR' in i:
                logging.info('SetUp下更改权限为管理员，ipmitool返回ADMINISTRATOR')
            else:
                stylelog.fail('SetUp下更改权限为管理员，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count+=1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Ipm.USER_PRIVILEGE],6,SutConfig.Ipm.NO_ACCESS)
    time.sleep(3)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    for i in stdoutput.split('\\n'):
        if 'Root_1' in i:
            if 'NO ACCESS' in i:
                logging.info('SetUp下更改权限为无法访问，ipmitool返回NO ACCESS')
            else:
                stylelog.fail('SetUp下更改权限为无法访问，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count+=1
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.DEL_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.DEL_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_1',10):
        pass
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root11')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DEL_USER_SUCCESS,10):
        logging.info('setup下删除用户成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(3)
    arg='{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput=str(stdoutput).replace("'",'')
    if 'Root_1' not in stdoutput:
        logging.info('setup下删除用户，ipmitool没有返回用户')
    else:
        stylelog.fail('setup下删除用户，ipmitool仍返回用户')
        count+=1
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    # userid=str(int(userid)+1)
    logging.info('BMC端.....................................................')
    logging.info('BMC增加用户.....................................................')
    arg='{0} user set name {1} Root_2'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户名，Run {0}'.format(arg))
    time.sleep(3)
    arg='{0} user set password {1} Root@root2 20'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置密码，Run {0}'.format(arg))
    time.sleep(3)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW,10):
        logging.info('BMC新建用户，SetUp下认证成功')

    else:
        logging.info('BMC新建用户，SetUp下认证失败')

        return
    time.sleep(3)
    logging.info('BMC更改用户状态.....................................................')
    arg='{0} user enable {1}'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户状态为enable，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ENABLE,10):
        logging.info('BMC修改用户状态为enabled，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为enabled，SetUp下认证失败')
        count+=1   
    time.sleep(2)
    arg='{0} user disable {1}'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户状态为disable，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DISABLE,10):
        logging.info('BMC修改用户状态为disabled，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为disabled，SetUp下认证失败')
        count+=1   
    time.sleep(2)
    logging.info('BMC更改用户密码.....................................................')
    arg='{0} user set password {1} Root@root22 20'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC修改用户密码为Root@root22，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ERROR_PSW,10):
        logging.info('BMC修改用户密码为Root@root22，输入原密码Root@root2显示密码错误')
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW,10):
        logging.info('BMC修改用户密码为Root@root22，SetUp下验证成功')
        time.sleep(2)
    else:
        return
    logging.info('BMC更改用户权限....................................................................')
    arg='{0} user priv {1} 0x1 1'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为Callback，Run {0}'.format(arg))
    time.sleep(3)
    arg = '{0} user priv {1} 0x1 8'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为Callback，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CALLBACK,10):
        logging.info('BMC修改用户权限为Callback，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为Callback，SetUp下认证失败')
        count+=1   
    time.sleep(2)


    arg='{0} user priv {1} 0x2 1'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为User，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0x2 8'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为User，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.USER,10):
        logging.info('BMC修改用户权限为User，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为User，SetUp下认证失败')
        count+=1   
    time.sleep(2)

    
    arg='{0} user priv {1} 0x3 1'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为Operator，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0x3 8'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为Operator，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    # else:
    #     return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.OPERATOR,10):
        logging.info('BMC修改用户权限为Operator，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为Operator，SetUp下认证失败')
        count+=1   
    time.sleep(2)



    arg='{0} user priv {1} 0x4 '.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为Administrator，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0x4 8'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为Administrator，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ADMIN,10):
        logging.info('BMC修改用户权限为Administrator，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为Administrator，SetUp下认证失败')
        count+=1   
    time.sleep(2)

    
    arg='{0} user priv {1} 0xF 1'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为No Access，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0xF 8'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC设置用户权限为No Access，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.CHANGE_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.CHANGE_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
 
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2',10):
        logging.info('输入用户名Root_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.NO_ACCESS,10):
        logging.info('BMC修改用户权限为No Access，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为No Access，SetUp下认证失败')
        count+=1   
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('BMC更改用户密码.....................................................')
    arg = '{0} user set password {1} Root@root3 20'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC修改用户密码为Root@root3，Run {0}'.format(arg))
    time.sleep(3)
    time.sleep(2)
    logging.info('BMC更改用户密码.....................................................')
    arg = '{0} user set password {1} Root@root33 20'.format(SutConfig.Env.IPMITOOL, userid)
    subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('BMC修改用户密码为Root@root33，Run {0}'.format(arg))
    time.sleep(5)
    if not SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.DEL_USER],5):
        assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.DEL_USER],5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_NAME],5):
        assert SetUpLib.locate_option(Key.UP,[SutConfig.Ipm.USER_NAME],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Root_2'):
        pass
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Ipm.USER_PSW],5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Root@root33')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DEL_USER_SUCCESS,10):
        logging.info('删除用户成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if count==0:
        return True
    else:
        return



def sol():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.CLOSE_SOL,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    try:
        arg = '{0} sol activate'.format(SutConfig.Env.IPMITOOL)
        p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate(timeout=2)
    except:

        stylelog.fail('SetUp下关闭板载SOL功能，BMC仍可以激活SOL')
        return
    if 'Info: SOL payload disabled' in erroutput.decode('gbk'):
        logging.info('SetUp下关闭板载SOL功能，BMC无法激活SOL')
    else:
        logging.info(erroutput.decode('gbk'))
        stylelog.fail('SetUp下关闭板载SOL功能，BMC仍可以激活SOL')
        return
    BmcLib.set_console_to_bios()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SOL, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    try:
        arg = '{0} sol activate'.format(SutConfig.Env.IPMITOOL)
        p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate(timeout=2)
        logging.info(erroutput.decode('gbk'))
        stylelog.fail('SetUp下打开板载SOL功能,Bmc不能激活SOL')
        return
    except:
        arg = '{0} sol activate'.format(SutConfig.Env.IPMITOOL)
        p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate(timeout=2)
        if 'payload already active on another session' in erroutput.decode('gbk'):
            logging.info('SetUp下打开板载SOL功能,Bmc可以激活SOL')
        else:
            logging.info(erroutput.decode('gbk'))
            stylelog.fail('SetUp下打开板载SOL功能,Bmc不能激活SOL')
            return
    try:
        arg = '{0} sol deactivate'.format(SutConfig.Env.IPMITOOL)
        p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate(timeout=2)
        if erroutput.decode('gbk')=='':
            logging.info('Bmc关闭SOL')
        else:
            logging.info(erroutput.decode('gbk'))
            stylelog.fail('Bmc没有关闭SOL')
            return
    except:
        stylelog.fail('Bmc没有关闭SOL')
        return
    time.sleep(2)
    BmcLib.set_console_to_bios()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.CLOSE_SOL, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    return True



def bmc_system_log():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_SYS_LOG,18)
    logging.info('SetUp下收集BMC系统日志')
    start_time=time.time()
    while True:
        data = SetUpLib.get_data(1)
        end_time=time.time()
        if 'Total Entries' in data:
            break
        if end_time-start_time >150:
            break
    logging.info('SetUp下收集BMC系统日志完成')
    setup_log=re.findall('\d{4}/\d+/\d+ \d+:\d+:\d+',data)
    logging.info('Bmc下收集BMC系统日志')
    arg = '{0} sel list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    bmc=re.findall('\d+/\d+/\d+ \| \d+:\d+:\d+',stdoutput.decode('gbk'))[::-1][:len(setup_log)]
    logging.info('Bmc下收集BMC系统日志完成')
    bmc_log=[]
    for i in bmc:
        i=i.replace('| ','')
        year=re.findall('/(\d{4})',i)[0]
        i=re.sub('/\d{4}','',i)

        i=year+'/'+i
        i = re.sub(' 0', ' ', i)
        i=re.sub('/0', '/', i)
        bmc_log.append(i)
    logging.info('SetUp系统日志:{}'.format(setup_log))
    logging.info(' BMC 系统日志:{}'.format(bmc_log))
    if bmc_log==setup_log:
        logging.info('SetUp下系统日志与BMC下系统日志一致')

    else:
        stylelog.fail('SetUp下系统日志与BMC下系统日志不一致')
        return
    logging.info('清除系统日志')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.CLEAR_FRU,18)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_SYS_LOG, 18)
    logging.info('SetUp下收集BMC系统日志')
    start_time = time.time()
    while True:
        data = SetUpLib.get_data(1)
        end_time = time.time()
        if 'Total Entries' in data:
            break
        if end_time - start_time > 150:
            break
    logging.info('SetUp下收集BMC系统日志完成')
    setup_log_clear = re.findall('\d{4}/\d+/\d+ \d+:\d+:\d+', data)
    logging.info('Bmc下收集BMC系统日志')
    arg = '{0} sel list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    bmc_clear = re.findall('\d+/\d+/\d+ \| \d+:\d+:\d+', stdoutput.decode('gbk'))[::-1][:len(setup_log_clear)]
    logging.info('Bmc下收集BMC系统日志完成')
    bmc_log_clear= []
    for i in bmc_clear:
        i = i.replace('| ', '')
        year = re.findall('/(\d{4})', i)[0]
        i = re.sub('/\d{4}', '', i)
        i = year + '/' + i
        i = re.sub(' 0', ' ', i)
        i = re.sub('/0', '/', i)
        bmc_log_clear.append(i)
    logging.info('SetUp系统日志:{}'.format(setup_log_clear))
    logging.info(' BMC 系统日志:{}'.format(setup_log_clear))
    if setup_log_clear==setup_log_clear:
        logging.info('清除系统日志后，SetUp下和BMC下返回结果一致')
        if len(setup_log_clear)==1:
            logging.info('清除系统日志后，系统日志只有一条')
            return True
        else:
            logging.info('清除系统日志后，系统日志不止一条')
            return
    else:
        stylelog.fail('清除系统日志后，SetUp下和BMC下返回结果不一致')
        return



def fru():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Ipm.LOC_FRU,18)
    setup_fru=[]
    data=SetUpLib.get_data(2)
    data=re.findall('(Chassis Part Number.*)',data)[0]
    for i in re.findall('[A-Z]\w+ *\w+ *\w+[a-z] {2,}[0-9A-Za-z\-]+   ',data):
        setup_fru=setup_fru+re.findall('  ([0-9A-Za-z].*)',i.strip())
    setup_fru=setup_fru+[re.findall('System UUID *([a-zA-z\-0-9]+ {0,1}[a-zA-z\-0-9]+)   ',data)[0].replace(' ','').lower()]
    bmc_fru=[]
    arg = '{0} fru print'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    data=stdoutput.decode('gbk')
    bmc_fru=re.findall('Chassis Part Number *: ([0-9A-Za-z\-]+)',data)
    bmc_fru = bmc_fru+re.findall('Chassis Serial *: ([0-9A-Za-z\-]+)', data)
    bmc_fru = bmc_fru+re.findall('Board Mfg *: ([0-9A-Za-z\-]+)', data)
    bmc_fru = bmc_fru + re.findall('Board Product *: ([0-9A-Za-z\-]+)', data)
    bmc_fru = bmc_fru + re.findall('Board Serial *: ([0-9A-Za-z\-]+)', data)
    bmc_fru = bmc_fru + re.findall('Board Part Number *: ([0-9A-Za-z\-]+)', data)
    bmc_fru = bmc_fru + re.findall('Product Manufacturer *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Name *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Version *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Serial *: ([0-9A-Za-z\-]+)', data)[:1]
    arg = '{0} mc guid'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    bmc_fru = bmc_fru + [re.findall('System GUID *: ([0-9A-Za-z\-]+)',stdoutput.decode('gbk'))[0].lower()]
    logging.info('SetUp下FRU:{}'.format(setup_fru))
    logging.info(' BMC 下FRU:{}'.format(bmc_fru))
    if setup_fru==bmc_fru:
        logging.info('FRU信息验证通过')
        return True
    else:
        stylelog.fail('FRU信息验证不通过')
        return