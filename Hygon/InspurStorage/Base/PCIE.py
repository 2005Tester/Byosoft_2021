#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import time
import logging
from InspurStorage.BaseLib import BmcLib,SetUpLib
from InspurStorage.Config.PlatConfig import Key
from InspurStorage.Config import SutConfig
from InspurStorage.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



#PCIE链路协商重试
def _pcie_retrain_4u():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pci.SET_INFO,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    datas=''
    start=time.time()
    while True:
        end=time.time()
        datas=datas+SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE,datas):
            break
        if (end-start)>200:
            break
    if re.search('Offset *= *0x6[A-Z],Data *8[03], *Status *= *[a-zA-Z]+',datas) and not re.search('Offset *= *0x6[A-Z],Data *03, *Status *= *[a-zA-Z]+',datas):
        logging.info('PCIE 链路协商重试验证成功')
        return True
    else:
        stylelog.fail('PCIE 链路协商重试验证失败,{}'.format(re.findall('Offset *= *0x6[A-Z],Data *\d{2}, *Status *= *[a-zA-Z]+',datas)))
        return



def _pcie_retrain_2u():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.SET_INFO, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    datas = ''
    start = time.time()
    while True:
        end = time.time()
        datas = datas + SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas):
            break
        if (end - start) > 200:
            break
    if re.search('Offset *= *0x1[0-9],Data *= *0x0+, *Status *= *Success+', datas):
        logging.info('PCIE 链路协商重试验证成功')
        return True
    else:
        stylelog.fail(
            'PCIE 链路协商重试验证失败,{}'.format(re.findall('Offset *= *0x1[0-9],Data*= *0x[0-9]+, *Status *= *[a-zA-Z]+', datas)))
        return



def pcie_retrain():
    name = SutConfig.Pci.NAME
    if name == '2U':
        assert _pcie_retrain_2u()
        return True
    elif name == '4U':
        assert _pcie_retrain_4u()
        return True
    else:
        stylelog.fail(name)
        return



#PCIE资源预留
def _pcie_resource_reservation_4u():
    bdfs=SutConfig.Pci.BDFS
    slot=SutConfig.Pci.SLOT
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Pci.OPEN_SLOT,18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)

    bdfs_spe=[]
    data = SetUpLib.execute_command('lspci -tv')
    spec = re.findall(
        '\[(?:0e-13|14-30|31-36|37-53|65-6a|6b-87|88-8d|8e-aa|af-cb|cc-d1|d6-f2|f3-f8)\][0-9a-z]+\.[0-9a-z]+\-\[[0-9a-z]+-[0-9a-z]+\][0-9a-z]+\.[0-9a-z]+.*\[([0-9a-z]+)-[0-9a-z]+\][0-9a-z]+\.[0-9a-z]+\-\[[0-9a-z]+\]\-\-',
        data)
    if spec!=[]:
        spec=spec[0]
        for i in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11',
                  '12', '13', '14', '15', '16', '17', '18']:
            bdfs_spe.append(spec + ':' + i + '.' + '0')
    else:
        logging.info('没有接JBOF')
    bdfs1=['0d:00.0','0d:01.0']
    bdfs2=['ae:01.2','ae:01.1']
    bdfs3=['d5:01.2','d5:01.1']
    bdfs4=['0d:02.0','0d:03.0']
    bdfs5=['64:00.0','64:01.0']
    bdfs6=['64:02.0','64:03.0']
    for bdf in bdfs1:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if slot == '2':
            if bdf ==bdfs1[1]:
                if re.search('Memory behind bridge:.*\[size=201M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL为201MB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL不是201MB'.format(bdf))
                    count += 1
                if re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                    count += 1
            if bdf==bdfs1[0]:
                if not re.search('Memory behind bridge:.*\[size=(?:48|201)M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL验证失败'.format(bdf))
                    count += 1
                if not re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0},x16MMIOH预留资源验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},x16MMIOH预留资源验证失败'.format(bdf))
                    count += 1
        else:
            if re.search('Memory behind bridge:.*\[size=48M\]', datas):
                logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
            else:
                stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=1G\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                count+=1
    for bdf in bdfs2:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if slot == '4':
            if bdf ==bdfs2[1]:
                if re.search('Memory behind bridge:.*\[size=201M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL为201MB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL不是201MB'.format(bdf))
                    count += 1
                if re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                    count += 1
            if bdf==bdfs2[0]:
                if datas=='':
                    pass
                else:
                    stylelog.fail('BDF:{},验证失败'.format(bdf))
                    count+=1
        else:
            if re.search('Memory behind bridge:.*\[size=48M\]', datas):
                logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
            else:
                stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=1G\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                count+=1
    for bdf in bdfs3:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if slot == '6':
            if bdf ==bdfs3[1]:
                if re.search('Memory behind bridge:.*\[size=201M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL为201MB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL不是201MB'.format(bdf))
                    count += 1
            if bdf==bdfs3[0]:
                if datas=='':
                    pass
                else:
                    stylelog.fail('BDF:{},验证失败'.format(bdf))
                    count+=1
        else:
            if re.search('Memory behind bridge:.*\[size=48M\]', datas):
                logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
            else:
                stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=1G\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                count+=1
    for bdf in bdfs4:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if slot == '8':
            if bdf ==bdfs4[1]:
                if re.search('Memory behind bridge:.*\[size=201M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL为201MB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL不是201MB'.format(bdf))
                    count += 1
                if re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                    count += 1
            if bdf==bdfs4[0]:
                if not re.search('Memory behind bridge:.*\[size=(?:48|201)M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL验证失败'.format(bdf))
                    count += 1
                if not re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0},x16MMIOH预留资源验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},x16MMIOH预留资源验证失败'.format(bdf))
                    count += 1
        else:
            if re.search('Memory behind bridge:.*\[size=48M\]', datas):
                logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
            else:
                stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=1G\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                count+=1
    for bdf in bdfs5:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if slot == '10':
            if bdf ==bdfs5[1]:
                if re.search('Memory behind bridge:.*\[size=201M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL为201MB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL不是201MB'.format(bdf))
                    count += 1
                if re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                    count += 1
            if bdf==bdfs5[0]:
                if not re.search('Memory behind bridge:.*\[size=(?:48|201)M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL验证失败'.format(bdf))
                    count += 1
                if not re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0},x16MMIOH预留资源验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},x16MMIOH预留资源验证失败'.format(bdf))
                    count += 1
        else:
            if re.search('Memory behind bridge:.*\[size=48M\]', datas):
                logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
            else:
                stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=1G\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                count+=1

    for bdf in bdfs6:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if slot == '12':
            if bdf ==bdfs6[1]:
                if re.search('Memory behind bridge:.*\[size=201M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL为201MB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL不是201MB'.format(bdf))
                    count += 1
                if re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
                else:
                    stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                    count += 1
            if bdf==bdfs6[0]:
                if not re.search('Memory behind bridge:.*\[size=(?:48|201)M\]', datas):
                    logging.info('BDF:{0},X16的slot资源预留MMIOL验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},X16的slot资源预留MMIOL验证失败'.format(bdf))
                    count += 1
                if not re.search('Prefetchable memory behind bridge:.*\[size=1G\]', datas):
                    logging.info('BDF:{0},x16MMIOH预留资源验证成功'.format(bdf))
                else:
                    stylelog.fail('BDF:{0},x16MMIOH预留资源验证失败'.format(bdf))
                    count += 1
        else:
            if re.search('Memory behind bridge:.*\[size=48M\]', datas):
                logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
            else:
                stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=1G\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为1GB'.format(bdf))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是1GB'.format(bdf))
                count+=1
    if bdfs_spe!=[]:
        for bus in bdfs_spe:
            time.sleep(1)
            datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bus))
            if re.search('Memory behind bridge:.*\[size=8M\]', datas):
                logging.info('BDF:{0}slot资源预留MMIOL为8MB'.format(bus))
            else:
                stylelog.fail('BDF:{0}slot资源预留MMIOL不是8MB'.format(bus))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=4M\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为4M'.format(bus))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是4M'.format(bus))
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def _pcie_resource_reservation_2u():
    bdfs = SutConfig.Pci.BDFS
    slots = SutConfig.Pci.SLOT
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_SLOT, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    bdfs_spe = []
    data = SetUpLib.execute_command('lspci -tv')
    spec = re.findall(
        '\[(?:0e-1b|1c-29|3e-5a|5b-77|8d-a9|ae-bb|d3-ef)\][0-9a-z]+\.[0-9a-z]+\-\[[0-9a-z]+-[0-9a-z]+\][0-9a-z]+\.[0-9a-z]+.*\[([0-9a-z]+)-[0-9a-z]+\][0-9a-z]+\.[0-9a-z]+\-\[[0-9a-z]+\]\-\-',
        data)
    if spec!=[]:
        spec=spec[0]
        for i in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11',
                  '12', '13', '14', '15', '16', '17', '18']:
            bdfs_spe.append(spec + ':' + i + '.' + '0')
    else:
        logging.info('没有接JBOF')
    bdf1=[]
    for slot in slots:
        bdf1.append(bdfs[int(slot)-1])
    for i in bdf1:
        bdfs.remove(i)
    bdf2=bdfs
    logging.info(bdf1)
    logging.info(bdf2)
    for bdf in bdf1:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if re.search('Memory behind bridge:.*\[size=208M\]', datas):
            logging.info('BDF:{0},X8的slot资源预留MMIOL为208MB'.format(bdf))
        else:
            stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是208MB'.format(bdf))
            count += 1
        if re.search('Prefetchable memory behind bridge:.*\[size=104M\]', datas):
            logging.info('BDF:{0}MMIOH预留资源为104M'.format(bdf))
        else:
            stylelog.fail('BDF:{0}MMIOH预留资源不是104M'.format(bdf))
            count += 1
    for bdf in bdf2:
        time.sleep(1)
        datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        if re.search('Memory behind bridge:.*\[size=48M\]', datas):
            logging.info('BDF:{0},X8的slot资源预留MMIOL为48MB'.format(bdf))
        else:
            stylelog.fail('BDF:{0},X8的slot资源预留MMIOL不是48MB'.format(bdf))
            count += 1
        if re.search('Prefetchable memory behind bridge:.*\[size=100M\]', datas):
            logging.info('BDF:{0}MMIOH预留资源为100M'.format(bdf))
        else:
            stylelog.fail('BDF:{0}MMIOH预留资源不是100M'.format(bdf))
            count += 1
    if bdfs_spe!=[]:
        for bus in bdfs_spe:
            time.sleep(1)
            datas = SetUpLib.execute_command('lspci -xxvvs {}'.format(bus))
            if re.search('Memory behind bridge:.*\[size=8M\]', datas):
                logging.info('BDF:{0}slot资源预留MMIOL为8MB'.format(bus))
            else:
                stylelog.fail('BDF:{0}slot资源预留MMIOL不是8MB'.format(bus))
                count+=1
            if re.search('Prefetchable memory behind bridge:.*\[size=4M\]',datas):
                logging.info('BDF:{0}MMIOH预留资源为4M'.format(bus))
            else:
                stylelog.fail('BDF:{0}MMIOH预留资源不是4M'.format(bus))
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def pcie_resource_reservation():
    name = SutConfig.Pci.NAME
    if name == '2U':
        assert _pcie_resource_reservation_2u()
        return True
    elif name == '4U':
        assert _pcie_resource_reservation_4u()
        return True
    else:
        stylelog.fail(name)
        return



def pcie_mem_enable():
    count=0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_SLOT, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    bdf=re.findall('[0-9a-z]+:[0-9a-z]+\.[0-9a-z]+',SetUpLib.execute_command('lspci | grep Eth'))
    for i in bdf:
        time.sleep(1)
        result=SetUpLib.execute_command('lspci -xxvvs {} | grep Region'.format(i))
        if result!='':
            if re.search('Disable',result):
                stylelog.fail('{},内存使能验证失败'.format(i))
                stylelog.fail(result)
                count+=1
            else:
                logging.info('{},内存使能验证成功'.format(i))
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count==0:
        return True
    else:
        return



def smi():
    bdfs = SutConfig.Pci.BDFS_SMI
    nums = SutConfig.Pci.ALL_SLOTS

    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_SLOT, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    data = SetUpLib.execute_command("lspci | grep 'PCIE GPP Bridge'")
    bdf1 = re.findall('([0-9A-Za-z]{2}:[0-9A-Za-z]{2}\.[0-9A-Za-z]+) PCI bridge', data)
    time.sleep(1)
    a = []
    for num in nums:
        bdf1.extend([bdfs[int(num) - 1]])
    for num in nums:
        a.append(bdfs[int(num) - 1])
    for i in a:
        bdfs.remove(i)
    bdf2 = bdfs
    print(bdf1)
    print(bdf2)
    for bdf in bdf2:
        time.sleep(1)
        result = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
        control = re.findall('Control:.*', result)
        bridgectl = re.findall('BridgeCtl:.*', result)
        devctl = re.findall('DevCtl:.*', result)
        if re.search('SERR\-', control[0]) and re.search('SERR\-', bridgectl[0]) and re.search(
                'CorrErr\- NonFatalErr\- FatalErr\-', devctl[0]):
            logging.info('PCIE设备{}资源配置信息验证成功'.format(bdf))
        else:
            stylelog.fail('PCIE设备{}资源配置信息验证失败'.format(bdf))
            stylelog.fail('{0},{1},{2}'.format(control, bridgectl, devctl))
            count += 1
    for bdf in bdf1:
        if bdf not in bdf2:
            time.sleep(1)
            result = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))
            if result != '':
                control = re.findall('Control:.*', result)
                bridgectl = re.findall('BridgeCtl:.*', result)
                devctl = re.findall('DevCtl:.*', result)
                if re.search('SERR\+', control[0]) and re.search('SERR\+', bridgectl[0]) and re.search(
                        'CorrErr\+ NonFatalErr\+ FatalErr\+', devctl[0]):
                    logging.info('PCIE设备{}资源配置信息验证成功'.format(bdf))
                else:
                    stylelog.fail('PCIE设备{}资源配置信息验证失败'.format(bdf))
                    stylelog.fail('{0},{1},{2}'.format(control, bridgectl, devctl))
                    count += 1
            else:
                logging.info('BDF:{}结果为空.'.format(bdf))
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(2)
    if count == 0:
        return True
    else:
        return



def io():
    count=0
    slots=SutConfig.Pci.IO_SLOT
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_SLOT, 18)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    bdfs = ['0d:00.0','0d:01.0','ae:01.2','ae:01.1','d5:01.2','d5:01.1','0d:02.0','0d:03.0','64:00.0', '64:01.0','64:02.0', '64:03.0']
    data=[]
    for slot in slots:
        time.sleep(1)
        result=SetUpLib.execute_command('lspci -xxvvs {}'.format(bdfs[(int(slot)-1)]))
        if re.search('I/O behind bridge: [0-9a-z]+\-[0-9a-z]+ \[size=4K\]',result):
            logging.info('BDF:{}，插上网卡IO资源分配为4K'.format(bdfs[(int(slot)-1)]))
        else:
            stylelog.fail('BDF:{}，插上网卡IO资源分配不是4K'.format(bdfs[(int(slot)-1)]))
            count+=1
        data.append(bdfs[(int(slot)-1)])
    for i in data:
        bdfs.remove(i)

    for bdf in bdfs:
        time.sleep(1)
        result = SetUpLib.execute_command('lspci -xxvvs {}'.format(bdf))

        if re.search('I/O behind bridge: [0-9a-z]+\-[0-9a-z]+ \[empty\]',result) or re.search('I/O behind bridge: None',result):
            logging.info('BDF:{}没插网卡，IO资源分配为空'.format(bdf))
        else:
            stylelog.fail('BDF:{}没插网卡，IO资源分配不为空'.format(bdf))
            count+=1
    time.sleep(1)
    SetUpLib.send_data_enter('reboot')
    time.sleep(10)
    datas = ''
    start = time.time()
    while True:
        end = time.time()
        datas = datas + SetUpLib.get_data(1)
        if re.search(SutConfig.Msg.POST_MESSAGE, datas):
            break
        if (end - start) > 200:
            break
    log=re.findall('  IO\[\d\] [0-9A-Z]+ [0-9A-z]+',datas)

    if re.search('IO\[0\] 0 [0-9A-z]{4}',log[0]):
        pass
    else:
        count+=1
    if any(i in ['1','2','7','8'] for i in slots):
        if re.search('IO\[1\] [0-9A-z]{4} [0-9A-z]{4}',log[1]):
            logging.info('CPU0 Die1 有资源分配')
        else:
            stylelog.fail('CPU0 Die1 没有资源分配')
            count+=1
    if any(i in ['9','10','11','12'] for i in slots):
        if re.search('IO\[4\] [0-9A-z]{4} [0-9A-z]{4}',log[4]):
            logging.info('CPU1 Die0 有资源分配')
        else:
            stylelog.fail('CPU1 Die0 没有资源分配')
            count+=1
    if any(i in ['3','4'] for i in slots):
        if re.search('IO\[5\] [0-9A-z]{4} [0-9A-z]{4}',log[5]):
            logging.info('CPU1 Die1 有资源分配')
        else:
            stylelog.fail('CPU1 Die1 没有资源分配')
            count+=1
    if any(i in ['5','6'] for i in slots):
        if re.search('IO\[6\] [0-9A-z]{4} [0-9A-z]{4}',log[6]):
            logging.info('CPU1 Die2 有资源分配')
        else:
            stylelog.fail('CPU1 Die2 没有资源分配')
            count+=1
    if count==0:
        return True
    else:
        return



def qat():
    assert SetUpLib.boot_os_from_bm()
    time.sleep(1)
    result=SetUpLib.execute_command("lspci | grep -E  'QAT|QuickAssist'")
    if result != '':
        logging.info('QAT卡可以识别')
        time.sleep(1)
        SetUpLib.send_data_enter('reboot')
        return True
    else:
        stylelog.fail('没有识别到QAT卡，检查是否插入QAT卡')
        time.sleep(1)
        SetUpLib.send_data_enter('reboot')
        return