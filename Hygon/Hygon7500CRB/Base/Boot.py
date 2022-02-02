#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import os
import time
import logging
import pyautogui
from Hygon7500CRB.Base import SetUpPassword, Cpu, PCIE,SetUp,HDDPassword,Smbios,PXE
from Hygon7500CRB.BaseLib import BmcLib,SetUpLib,SshLib
from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig, Sut01Config
from PIL import Image,ImageChops
from batf.Report import  stylelog
from batf.SutInit import Sut
from Hygon7500CRB.TestCase import SmbiosTest



def post_information():
    assert SetUpLib.boot_with_hotkey(Key.F2,SutConfig.Msg.SEL_LANG,120,SutConfig.Msg.POST_MESSAGE)
    logging.info('进入Setup成功')
    information = []
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.post_information_path,20)
    information = information + re.findall(r'BMC Firmware Revision + ([0-9]\.[0-9]{2})', SetUpLib.get_data(2))
    SetUpLib.locate_option(Key.DOWN, ['BMC Lan Configuration'], 11)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    information = information + re.findall(r'(192\.168\.[0-9]\.[0-9]{2,3})',SetUpLib.get_data(2))
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    SetUpLib.send_key(Key.LEFT)
    time.sleep(1)
    SetUpLib.send_key(Key.RIGHT)
    data = SetUpLib.get_data(2)
    information=information+re.findall(r'Release Version +([0-9.]+) ',data)
    information=information+re.findall(r'BIOS Build Time +([0-9/]+) ',data)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Msg.CPU_INFO,5)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    information.append(re.findall(r'Processor Type +(.*? Processor)',data)[0])
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Msg.MEM_INFO,5)
    data=SetUpLib.get_data(2)
    information=information + re.findall(r'Total Memory.*?([0-9]+ GB)',data)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.Boot.BOOT_TO_CPU0,4)
    data = SetUpLib.get_data(2)
    information.append(re.findall(r'[Manu]:(.*?), ', data)[0])
    information.append(re.findall(r'[PN]:(.*?), ', data)[0])
    SetUpLib.send_key(Key.ESC)
    BmcLib.init_sut()
    start_time = time.time()
    datas = []
    while True:
        data = SetUpLib.get_data(1)
        datas.append(data)
        if 'F2 to enter SETUP' in data:
            data = SetUpLib.get_data(1)
            datas.append(data)
            break
        now = time.time()
        spent_time = (now - start_time)
        if spent_time > 150:
            break
    data=''.join(datas)
    count=0
    for i in information:
        if i.replace(' ','') in data.replace(' ',''):

            logging.info('显示{0}'.format(i))
        else:
            count+=1
            stylelog.fail(i)
    if count!=0:
        return
    else:
        return True



#快捷启动
def quick_boot_hotkey():
    assert SetUpLib.boot_with_hotkey(Key.F2,SutConfig.Msg.SEL_LANG,120,SutConfig.Msg.POST_MESSAGE)
    logging.info('F2进入SetUp成功')
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.quick_boot_hotkey,5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    data = SetUpLib.get_data(1)
    name = re.findall('(Riser[A-Z]\_[0-9]\(J[0-9]{3} [0-9]X\))', data)[-1]
    name = re.sub(r'\(', '\(', name)
    name = re.sub(r'\)', '\)', name)
    assert SetUpLib.select_option_value(Key.DOWN,[name],Key.DOWN,'Enabled',30)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Boot.BOOT_Network_Boot,15)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_with_hotkey(Key.F7,SutConfig.Msg.ENTER_BOOTMENU_CN,120,SutConfig.Msg.POST_MESSAGE)
    logging.info('F7进入启动菜单成功')
    assert SetUpLib.boot_with_hotkey(Key.F12,'PXE',120,SutConfig.Msg.POST_MESSAGE)
    logging.info('F12进入PXE成功')
    return True



#截取屏幕，imgdir为截图存放的文件夹，picturename为图片的名称，不需要加'.jpg',返回图片的路径（没有'.jpg'）
def capture_screen(imgdir,picturename):
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
# def post_logo():
    # if not BmcLib.init_sut():
    #     logging.info("SetUpLib: Rebooting SUT Failed.")
    #     return
    # logging.info("SetUpLib: Booting to setup")
    # BmcLib.enable_serial_normal()
    # SetUpLib.wait_message('驱动加载中')
    # picture_path=capture_screen('Hygon/Tools/Pictures/Logo','logo')
    #
    # img = Image.open(picture_path+'.jpg')
    #
    # cropped = img.crop((400, 400, 1500, 650))
    # cropped.save(picture_path+"_cut.jpg")
    # logging.info('图片截取成功')
    # # img2 = Image.open('Hygon/Tools/Pictures/CorrectLogo/logo.jpg')
    # # cropped = img2.crop((300, 400, 1000, 550))
    # # cropped.save('Hygon/Tools/Pictures/CorrectLogo/logocut.jpg')
    # image1=Image.open(picture_path+"_cut.jpg")
    # image2=Image.open('Hygon/Tools/Pictures/CorrectLogo/logocut.jpg')
    # diff = ImageChops.difference(image1, image2)
    # if diff.getbbox()==None:
    #     logging.info('logo无变化')
    #     return True
    # else:
    #     logging.info('logo改变')