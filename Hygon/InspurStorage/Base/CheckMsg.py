#coding='utf-8'
import re
import os
import time
import subprocess
import logging
import pyautogui
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Base import Update,Boot
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from InspurStorage.BaseLib import SshLib
from batf.SutInit import Sut
from PIL import Image,ImageChops
from batf.Report import stylelog



def product_msg():
    msg = SutConfig.Che.PRODUCT_MSG
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.LOC_SYS_SUM,10)
    list=re.findall('System Manufacturer *([a-zA-Z]+)  ',SetUpLib.get_data(2))
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_DEVICE)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    data=SetUpLib.get_data(2)
    list=list+re.findall('BIOS Vendor *([a-zA-Z]+)  ',data)
    list = list + re.findall('Mother Board Info *([0-9a-zA-Z]+)  ', data)
    if list==msg:
        logging.info('生产制造信息检查通过')
        return True
    else:
        stylelog.fail('生产制造信息不符,{}'.format(list))
        return



def bios_msg():
    msg=SutConfig.Che.BIOS_MSG
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_DEVICE)
    time.sleep(1)
    SetUpLib.send_key(Key.LEFT)
    data = SetUpLib.get_data(2)
    list=[re.findall('BIOS Version *([0-9a-zA-Z\. ]+) +Release Version',data)[0].strip()]
    list = list + re.findall('Release Version *([0-9\.]+)  ', data)
    list = list + re.findall(' BIOS Build Time *(\d+/\d+/\d+ \d+:\d+)  ', data)
    if list==msg:
        logging.info('BIOS信息检查通过')
        return True
    else:
        stylelog.fail('BIOS信息不符,{}'.format(list))
        return



def memory_msg():
    count=0
    silks=SutConfig.Che.SILK
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.LOC_MEM_INFO,5)
    data=SetUpLib.get_data(2)
    total_mem=re.findall('Total Memory *(\d+) GB',data)[0]
    mem_frequency=re.findall('Memory Frequency *(\d+) MT/s',data)[0]
    list1 = []
    try_counts = 15
    while try_counts:
        SetUpLib.send_key(Key.DOWN)
        data = SetUpLib.get_data(1)
        list1 = list1 + re.findall(
            'DIMM[A-Z]\d *Manu:[a-zA-Z ]+, *PN:[0-9A-Z\-]+, *Size:\d+GB, *[0-9A-Zx]+, *Type:[A-Z]+, *ECC:Yes, *SN:[0-9A-Za-z]+',
            data)
        if 'CPU 1' in data:
            break
        try_counts -= 1
    mem_cpu0 = list(set(list1))
    mem_cpu0.sort(key=list1.index)
    try_counts = 15
    while try_counts:
        SetUpLib.send_key(Key.DOWN)
        if re.search('\│\│ *CPU 1', SetUpLib.get_data(1)):
            SetUpLib.send_key(Key.UP)
            time.sleep(1)
            SetUpLib.close_session()
            time.sleep(1)
            SetUpLib.open_session()
            break
        try_counts -= 1
    list2 = []
    try_counts = 15
    while try_counts:
        SetUpLib.send_key(Key.DOWN)
        data = SetUpLib.get_data(1)
        list2 = list2 + re.findall(
            'DIMM[A-Z]\d *Manu:[a-zA-Z ]+, *PN:[0-9A-Z\-]+, *Size:\d+GB, *[0-9A-Zx]+, *Type:[A-Z]+, *ECC:Yes, *SN:[0-9A-Za-z]+',
            data)
        if 'DIMMH1' in data:
            break
        try_counts -= 1
    mem_cpu1 = list(set(list2))
    mem_cpu1.sort(key=list2.index)
    mem_setup_cpu0=mem_cpu0
    mem_setup_cpu1 = mem_cpu1
    mem_setup = mem_setup_cpu0 + mem_setup_cpu1
    logging.info(mem_setup)
    logging.info('收集Log信息')
    time.sleep(1)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(1)
    datas = ''
    start = time.time()
    while True:
        end = time.time()
        data = SetUpLib.get_data(1)
        if 'Memory Info' in data:
            datas = datas + data
            datas = datas + SetUpLib.get_data(1)
            break
        if (end - start) > 200:
            break
    datas = datas.replace('\n', '').replace('\r', '')
    mem_log_cpu0 = re.findall(
        'Mem\[CPU0_[A-Z]\d[A-Z]*\d*:Training Success\] *Speed:\d+\(\d+\) *Manu:[a-zA-Z ]+, *PN:[0-9A-Z\-]+, *Size:\d+GB, *[0-9A-Zx]+, *Type:[A-Z]+, *ECC:Yes, *SN:[0-9A-Za-z]{8}',
        datas)
    mem_log_cpu1 = re.findall(
        'Mem\[CPU1_[A-Z]\d[A-Z]*\d*:Training Success\] *Speed:\d+\(\d+\) *Manu:[a-zA-Z ]+, *PN:[0-9A-Z\-]+, *Size:\d+GB, *[0-9A-Zx]+, *Type:[A-Z]+, *ECC:Yes, *SN:[0-9A-Za-z]{8}',
        datas)
    mem_log=mem_log_cpu0+mem_log_cpu1
    logging.info(mem_log)
    if  len(mem_setup)==len(mem_log)==int(total_mem)/32:
        logging.info('SetUp下内存数量与log中一致')
    else:
        stylelog.fail('SetUp下内存数量与log中不一致，setup{0},log{1},setup{2}'.format(len(mem_setup),len(mem_log),str(int(total_mem)/32)))
        return
    if mem_log_cpu0!=[]:
        for i in mem_log_cpu0:
            silk=re.findall(
        'Mem\[CPU0_([A-Z]\d[A-Z]*\d*):Training Success\] *Speed:\d+\(\d+\) *Manu:[a-zA-Z ]+, *PN:[0-9A-Z\-]+, *Size:\d+GB, *[0-9A-Zx]+, *Type:[A-Z]+, *ECC:Yes, *SN:[0-9A-Za-z]{8}',
        i)[0]
            if silk in silks:
                logging.info('丝印{}验证成功'.format(silk))
            else:
                stylelog.fail('丝印{}验证失败'.format(silk))
                count+=1
    if mem_log_cpu1!=[]:
        for i in mem_log_cpu1:
            silk=re.findall(
        'Mem\[CPU1_([A-Z]\d[A-Z]*\d*):Training Success\] *Speed:\d+\(\d+\) *Manu:[a-zA-Z ]+, *PN:[0-9A-Z\-]+, *Size:\d+GB, *[0-9A-Zx]+, *Type:[A-Z]+, *ECC:Yes, *SN:[0-9A-Za-z]{8}',
        i)[0]
            if silk in silks:
                logging.info('丝印{}验证成功'.format(silk))
            else:
                stylelog.fail('丝印{}验证失败'.format(silk))
                count+=1
    for i in mem_log:
        if re.findall('Speed:\d+\((\d+)\)',i)[0]==mem_frequency:
            logging.info('内存频率验证成功')
        else:
            stylelog.fail('内存频率验证失败,setup{0},log{1}'.format(mem_frequency,re.findall('Speed:\d+\((\d+)\)',i)[0]))
            count+=1
    for i in mem_setup:
        if re.findall('Manu:.*SN:[0-9A-Z]{8}',i)[0].replace(' ','')==re.findall('Manu:.*SN:[0-9A-Z]{8}',mem_log[mem_setup.index(i)])[0].replace(' ',''):
            logging.info('setup内存信息与log中一致')
        else:
            stylelog.fail('setup内存信息与log中不一致,setup{0},log{1}'.format(i,mem_log[mem_setup.index(i)]))
            count+=1
    if count==0:
        return True
    else:
        return



def cpu_msg():
    msg=SutConfig.Che.CPU_MSG
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Che.LOC_CPU_INFO, 5)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)

    list=[re.findall('CPU Type *(.*)Processor Socket',data)[0].strip()]
    list=list+re.findall('CPU \d',re.findall('Processor Socket(.*)CPU ID',data)[0])
    list=list+[re.findall('CPU ID *(.*?)\|',data)[0].strip()]
    list = list + [re.findall('CPU Speed *(.*?)\|', data)[0].strip()]
    list = list + [re.findall('CPU Core Count *(.*?)\|', data)[0].strip()]
    list = list + [re.findall('CPU Thread Count *(.*?)\|', data)[0].strip()]
    list = list + [re.findall('CPU MicroCode Patch Version *(.*?)\|', data)[0].strip()]
    list = list + [re.findall('L1 Cache Size *(.*?)\|', data)[0].strip()]
    list = list + [re.findall('L2 Cache Size *(.*?)\|', data)[0].strip()]
    list = list + [re.findall('L3 Cache Size *(.*?)\|', data)[0].strip()]
    if list==msg:
        logging.info('CPU信息检查通过')
        return True
    else:
        stylelog.fail('CPU信息不符,{}'.format(list))
        return



def lan_nvme_msg():
    mac=SutConfig.Che.MAC_ADDRESS
    nvme=SutConfig.Che.NVME_MSG
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.LOC_LAN,10)
    data=SetUpLib.get_data(2)
    result=re.findall('Onboard Lan\d MAC Address +([0-9A-Z]{2}\-[0-9A-Z]{2}\-[0-9A-Z]{2}\-[0-9A-Z]{2}\-[0-9A-Z]{2}\-[0-9A-Z]{2})',data)
    if result==mac:
        logging.info('板载网卡MAC地址检查通过')
    else:
        stylelog.fail('板载网卡MAC地址检查失败，实际MAC地址{}'.format(result))
        count+=1
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.LOC_NVME,10)
    data=SetUpLib.get_data(2)
    if all( i in data for i in nvme):
        logging.info('NVME 信息检查通过')
    else:
        stylelog.fail('NVME 信息检查失败')
        stylelog.fail(data.strip())
        count+=1
    if count==0:
        return True
    else:
        return



def memory_training():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Che.LOC_MEM_INFO, 5)
    data = SetUpLib.get_data(1)
    total_mem = re.findall('Total Memory *(\d+) GB', data)[0]
    time.sleep(1)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(1)
    datas = ''
    start=time.time()
    while True:
        end=time.time()
        data = SetUpLib.get_data(1)
        if 'Memory Info' in data:
            datas = datas + data
            datas = datas + SetUpLib.get_data(1)
            break
        if (end-start)>200:
            break
    success=len(re.findall('Training Success',datas))
    fail=len(re.findall('Training Failed',datas))
    if success == int(total_mem)/32 and fail in [24-int(total_mem)/32,12-int(total_mem)/32]:
        logging.info('内存Training结果显示正确')
        return True
    else:
        stylelog.fail('内存Training结果显示错误,training成功个数：{0}，training失败个数：{1}'.format(success,fail))
        return



def debug_mode():
    values=SutConfig.Che.DEBUG_VALUES
    log_length=[]
    assert SetUpLib.boot_to_setup()
    for value in values:
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
        assert SetUpLib.change_option_value(Key.DOWN,[SutConfig.Che.DEBUG_NAME],10,value)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        SetUpLib.close_session()
        time.sleep(2)
        SetUpLib.open_session()
        datas = ''
        start = time.time()
        while True:
            end = time.time()
            datas = datas+SetUpLib.get_data(1)
            if re.search(SutConfig.Msg.POST_MESSAGE,datas):
                SetUpLib.send_key(Key.DEL)
            if re.search(SutConfig.Msg.PAGE_MAIN,datas):
                break
            if (end - start) > 300:
                break

        log_length.append(len(datas.split(SutConfig.Msg.PAGE_MAIN)[0].split('\n')))
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.SET_INFO,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    if sorted(log_length,reverse=True)==log_length:
        logging.info('日志数量逐级减少')
        return True
    else:
        for value in values:
            stylelog.fail('{0}Log数量为{1}'.format(value,log_length[values.index(value)]))
        return



#支持初始化GPIO OK_REDUCE_PWR_R 为 OUTPUT，初始化为无效电平
def gpio():
    assert SetUpLib.boot_with_hotkey(Key.F3,SutConfig.Msg.ENTER_BOOTMENU,250,SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.USB_UEFI,12,'UEFI Interactive Shell')
    time.sleep(10)
    SetUpLib.send_data_enter('{0}'.format(SutConfig.Env.SHELL_USB_PATH))
    time.sleep(2)
    SetUpLib.send_data_enter('cd Storage')
    time.sleep(1)
    SetUpLib.send_data('App.efi -r 0 3 9')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    if re.findall('GPIO: *\d+ *\d+ *\d+ *\d+ *(\d+) ',data)[0]=='0':
        logging.info('GPIO显示Status为0')
        return True
    else:
        stylelog.fail('GPIO显示Status不是0,而是{}'.format(re.findall('GPIO: *\d+ *\d+ *\d+ *\d+ *(\d+) ',data)))
        return



#smbus频率默认配置为100KHZ
def smbus():
    smbus=SutConfig.Che.SMBUS
    assert SetUpLib.boot_with_hotkey(Key.F3, SutConfig.Msg.ENTER_BOOTMENU, 250, SutConfig.Msg.POST_MESSAGE)
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.USB_UEFI, 12, 'UEFI Interactive Shell')
    time.sleep(10)
    SetUpLib.send_data('mem fed80E00 100')
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    data=SetUpLib.get_data(2)
    if all(i in data for i in smbus):
        logging.info('smbus频率默认配置为100KHZ')
        return True
    else:
        stylelog.fail('smbus频率默认配置不是100KHZ')
        stylelog.fail(data)
        return



def _ntb_resource_reservation_4u():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.SET_INFO,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    datas=''
    start=time.time()
    while True:
        end=time.time()
        datas+=SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE,datas):
            break
        if end-start>200:
            break
    ntbs=[]
    total=re.findall('\+MMIO64 \(([0-9A-Z]+),[0-9A-Z]+',datas)
    other=re.findall('MMIO64\[\d+\] ([0-9A-Z]+) [0-9A-Z]+',datas)
    if len(total)!=len(other):
        return
    for i in range(0,len(total)):
        if total[i]!=other[i]:
            ntb=int(other[i][:-10],16)-int(total[i][:-10],16)
            ntbs.append({i:ntb})
    if ntbs==SutConfig.Che.NTB:
        logging.info('NTB资源预留验证成功')
        return True
    else:
        stylelog.fail('NTB资源预留验证失败,{}'.format(ntbs))
        return



def _ntb_resource_reservation_2u():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Che.SET_INFO, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    datas = ''
    start = time.time()
    while True:
        end = time.time()
        datas += SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas):
            break
        if end - start > 200:
            break
    total = re.findall('\+MMIO64 \(([0-9A-Z]+),[0-9A-Z]+', datas)

    if all(float(i[:-10])>1.5 for i in total):
        logging.info(total)
        logging.info('内存预留1.5T以上的MMIOH空间')
        return True
    else:
        stylelog.fail('内存预留MMIOH空间小于1.5T')
        stylelog.fail(total)
        return



def ntb_resource_reservation():
    name=SutConfig.Pci.NAME
    if name=='2U':
        assert _ntb_resource_reservation_2u()
        return True
    elif name=='4U':
        assert _ntb_resource_reservation_4u()
        return True
    else:
        stylelog.fail(name)
        return



def che_ras():
    SetUpLib.send_data_enter('reboot')
    time.sleep(1)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    datas = ''
    start = time.time()
    while True:
        end = time.time()
        datas += SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas):
            break
        if end - start > 200:
            break
    if re.search('\[RAS\]',datas):
        logging.info('RAS信息采集并记录到log')
        return True
    else:
        stylelog.fail('log中没有RAS信息')
        return



def che_postcode():
    SetUpLib.send_data_enter('reboot')
    time.sleep(1)
    SetUpLib.send_key(Key.CTRL_ALT_DELETE)
    time.sleep(1)
    SetUpLib.close_session()
    time.sleep(1)
    SetUpLib.open_session()
    datas = ''
    start = time.time()
    while True:
        end = time.time()
        datas += SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas):
            break
        if end - start > 200:
            break
    if re.search('POSTCODE', datas):
        logging.info('log中有POSTCODE信息')
        return True
    else:
        stylelog.fail('log中没有POSTCODE信息')
        return



def che_bds():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Che.SET_DEBUG,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    SetUpLib.close_session()
    time.sleep(2)
    SetUpLib.open_session()
    datas1 = ''
    start = time.time()
    while True:
        end = time.time()
        datas1 = datas1 + SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas1):
            SetUpLib.send_key(Key.F3)
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, datas1):
            break
        if (end - start) > 300:
            break
    if re.search('\[Bds\]Booting BootMenu',datas1):
        logging.info('日志打印级别Debug,Bds后有启动选项显示')
    else:
        stylelog.fail('日志打印级别Debug,Bds后没有启动选项显示')
        count+=1
    assert SetUpLib.select_boot_option(Key.DOWN,SutConfig.Msg.ENTER_SETUP,12,SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Che.SET_WARNING, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    SetUpLib.close_session()
    time.sleep(2)
    SetUpLib.open_session()
    datas2 = ''
    start = time.time()
    while True:
        end = time.time()
        datas2 = datas2 + SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas2):
            SetUpLib.send_key(Key.F3)
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, datas2):
            break
        if (end - start) > 300:
            break
    if re.search('\[Bds\]Booting BootMenu',datas2):
        logging.info('日志打印级别Warning,Bds后有启动选项显示')
    else:
        stylelog.fail('日志打印级别Warning,Bds后没有启动选项显示')
        count += 1
    assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 12, SutConfig.Msg.PAGE_MAIN)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Che.SET_INFO, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    SetUpLib.close_session()
    time.sleep(2)
    SetUpLib.open_session()
    datas3 = ''
    start = time.time()
    while True:
        end = time.time()
        datas3 = datas3 + SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas3):
            SetUpLib.send_key(Key.F3)
        if re.search(SutConfig.Msg.ENTER_BOOTMENU, datas3):
            break
        if (end - start) > 300:
            break
    if re.search('\[Bds\]Booting BootMenu', datas3):
        logging.info('日志打印级别Information,Bds后有启动选项显示')
    else:
        stylelog.fail('日志打印级别Information,Bds后没有启动选项显示')
        count += 1
    if count==0:
        return True
    else:
        return



def che_debug_mode_clear():
    count=0
    values=SutConfig.Che.DEBUG_OPTION_VALUE
    assert SetUpLib.boot_to_setup()
    for value in values:
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
        assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Che.DEBUG_NAME], 10, value)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        try_counts = 12
        data=''
        while try_counts:
            SetUpLib.close_session()  # 关闭连接
            time.sleep(0.5)
            SetUpLib.open_session()  # 打开连接
            time.sleep(0.5)
            data += SetUpLib.get_data(2, Key.RIGHT)
            if SutConfig.Msg.PAGE_MAIN in data:
                break
            try_counts -= 1
        print(data)
        if not re.search(SutConfig.Che.WRONG_MSG,data):
            logging.info('SetUp界面周围无其他信息展示')
        else:
            stylelog.fail('SetUp界面周围有其他信息')
            count+=1
    if count==0:
        return True
    else:
        return
