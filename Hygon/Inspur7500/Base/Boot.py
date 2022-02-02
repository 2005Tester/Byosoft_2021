#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import os
import time
import logging
import pyautogui
from Inspur7500.Base import Update
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.Config import SutConfig
from PIL import Image,ImageChops
from batf.Report import  stylelog
import subprocess
from batf import core



def post_information():
    assert SetUpLib.boot_to_setup()
    information=[]
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_USB, 10)
    data = SetUpLib.get_data(2)
    data = re.findall('USB device list :(.*)USB Port', data)[0]
    for i in re.split('USB Front Port\d:|USB Back Port\d:', data):
        if 'Mouse' in i:
            information=information+re.findall('USB *Mouse(.*)', i.strip())
        if 'Keyboard' in i:
            information = information + re.findall('USB *Keyboard(.*)', i.strip())
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.SERVICE_CONFIG,10)
    information=information+re.findall(r'BMC Firmware Revision +([0-9\.]*) ',SetUpLib.get_data(2))
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.LOC_HDD,18)
    data=re.findall('([a-zA-Z ]+\([^\(|\)]+\(*[^\(|\)]+\)*[^\(|\)]+\))',SetUpLib.get_data(2))
    for i in data:
        i = re.sub('\(', ': ', i, 1)
        i = i[:-1]
        i=re.sub('SATA\d{1,2}-\d{1,2}: ','',i)
        information=information+[i.strip()]
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED_CN)
    SetUpLib.send_key(Key.LEFT)
    information=information+re.findall(r'Onboard LAN[0|1] MAC Address +([A-Z0-9\-]+) ',SetUpLib.get_data(2))
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    information=information+re.findall(r'Release Version +([0-9\.]+) ',data)
    information=information+re.findall(r'BIOS Build Time +([0-9\-]+) ',data)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.CPU_INFO,5)
    data=SetUpLib.get_data(2)
    information=information+re.findall(r'CPU Version +([0-9a-zA-Z \-]+Processor) +',data)
    information=information+re.findall(r'CPU Frequency.*?([0-9]{4} MHz) +',data)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.MEM_INFO,5)
    data=SetUpLib.get_data(2)
    information=information+re.findall(r'Manu:(.*?),',data)
    information = information + re.findall(r'Type:(.*?),', data)
    information=information+re.findall(r'Memory [a-zA-Z]* *Frequency.*?([0-9]{4} MHz)',data)
    information=information+re.findall(r'Total Memory.*?([0-9]+ GB)',data)
    information = information + re.findall(r'Total Memory Count.*?([0-9]{1,2})', data)
    SetUpLib.send_key(Key.ESC)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if 'Press Key in 0 seconds' in data:
            break
        now = time.time()
        spent_time = (now - start_time)
        if spent_time > 200:
            break


    data=''.join(datas)
    count=0
    for i in information:
        if i.replace(' ','') in data.replace(' ',''):

            logging.info('显示{0}'.format(i))
        else:
            if re.sub(' [ a-zA-Z0-9]+\(.*\):*','',i).replace(' ','') in data.replace(' ',''):
                logging.info('显示{0}'.format(re.sub(' [ a-zA-Z0-9]+\(.*\):*','',i)))
            else:
                count+=1
                stylelog.fail(i)
    if count!=0:
        return
    else:
        return True



#快捷启动
def quick_boot_hotkey():
    assert SetUpLib.boot_with_hotkey(Key.DEL,SutConfig.Msg.PAGE_MAIN_CN,150,SutConfig.Msg.POST_MESSAGE)
    logging.info('DEL进入SetUp成功')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.ONBOARD_ETH,10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.PXE, 10)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F11,SutConfig.Msg.ENTER_BOOTMENU_CN,150,SutConfig.Msg.POST_MESSAGE)
    logging.info('F11进入启动菜单成功')
    assert SetUpLib.boot_with_hotkey(Key.F12,'PXE',150,SutConfig.Msg.POST_MESSAGE)
    logging.info('F12进入PXE成功')
    return True



#截取屏幕，imgdir为截图存放的文件夹，picturename为图片的名称，不需要加'.jpg',返回图片的路径（没有'.jpg'）
def _capture_screen(imgdir,picturename):
    filename = picturename + ".jpg"
    if os.path.exists(imgdir):
        file_path = os.path.join(imgdir, filename)
    else:
        os.mkdir(imgdir)
        file_path = os.path.join(imgdir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    try:
        screen = pyautogui.screenshot()
        screen.save(file_path)
        logging.info("Screen captured: {0}".format(filename))
        return os.path.join(imgdir,picturename)
    except Exception as e:
        logging.info("Failed to capture screen.")
        logging.error(e)



#Post页面Logo检查
def post_logo():
    if not BmcLib.init_sut():
        logging.info("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    BmcLib.enable_serial_normal()
    SetUpLib.wait_message('驱动加载中')
    picture_path=_capture_screen('Inspur7500/Tools/Pictures/Logo','logo')

    img = Image.open(picture_path+'.jpg')
    
    cropped = img.crop((400, 400, 1500, 650))
    cropped.save(picture_path+"_cut.jpg")
    logging.info('图片截取成功')
    # img2 = Image.open('Inspur7500/Tools/Pictures/CorrectLogo/logo.jpg')
    # cropped = img2.crop((300, 400, 1000, 550))
    # cropped.save('Inspur7500/Tools/Pictures/CorrectLogo/logocut.jpg')
    image1=Image.open(picture_path+"_cut.jpg")
    image2=Image.open('Inspur7500/Tools/Pictures/CorrectLogo/logocut.jpg')
    diff = ImageChops.difference(image1, image2)
    if diff.getbbox()==None:
        logging.info('logo无变化')
        return True
    else:
        logging.info('logo改变')