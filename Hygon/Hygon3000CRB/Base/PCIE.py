#coding='utf-8'
import datetime
from typing import Set
import requests
import re
import time
import logging
from Hygon3000CRB.BaseLib import BmcLib,SetUpLib
from Hygon3000CRB.Config.PlatConfig import Key
from Hygon3000CRB.Config import SutConfig,Sut01Config
from Hygon3000CRB.BaseLib import SshLib
from batf.SutInit import Sut
from batf.Report import stylelog



def pcie_max_payload():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.PCIE.SET_PAYLOAD_128B,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 128:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("RAID卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 128 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为128B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为128B失败')
                    return
            else:
                logging.info("RAID卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")
    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 128:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("网卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 128 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为128B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为128B失败')
                    return
            else:
                logging.info("网卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        stylelog.fail("BDF无效")
        return
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 128:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("SAS卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 128 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为128B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为128B失败')
                    return
            else:
                logging.info("SAS卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_PAYLOAD_256B,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 256:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("RAID卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 256 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为256B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为256B失败')
                    return
            else:
                logging.info("RAID卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 256:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("网卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 256 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为256B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为256B失败')
                    return
            else:
                logging.info("网卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        stylelog.fail("BDF无效")
        return
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 256:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("SAS卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 256 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为256B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为256B失败')
                    return
            else:
                logging.info("SAS卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_PAYLOAD_512B,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 512:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("RAID卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 512 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为512B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为512B失败')
                    return
            else:
                logging.info("RAID卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 512:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("网卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 512 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为512B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为512B失败')
                    return
            else:
                logging.info("网卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        stylelog.fail("BDF无效")
        return

    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
            cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
            if int(cmd_result1) >= 512:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("SAS卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                if 'MaxPayload 512 bytes' in cmd_result2:
                    logging.info('修改PCIE最大负载为512B成功')
                else:
                    stylelog.fail('修改PCIE最大负载为512B失败')
                    return
            else:
                logging.info("SAS卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_PAYLOAD_AUTO,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    return True



# 最大读需求大小
def pcie_max_Readload():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_READ_REQUEST_128B,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("RAID卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 128 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为128B成功')
            else:
                stylelog.fail('修改最大读需求大小为128B失败')
                return
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

# SAS卡测试
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("SAS卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 128 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为128B成功')
            else:
                stylelog.fail('修改最大读需求大小为128B失败')
                return

    else:
        logging.warning("SAS卡不存在，跳过RAID卡测试")

# 网卡测试
    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:

            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("网卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 128 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为128B成功')
            else:
                stylelog.fail('修改最大读需求大小为128B失败')
                return

    else:
        logging.warning("网卡不存在，跳过RAID卡测试")
    # 256B
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_READ_REQUEST_256B,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:

            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("RAID卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 256 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为256B成功')
            else:
                stylelog.fail('修改最大读需求大小为256B失败')
                return

    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

        # SAS卡测试
        logging.info('SAS卡测试..............................................')
        while True:
            cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
            if cmd_result:
                break
        cmd_result = cmd_result[0]
        BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
        logging.info("所有SAS卡的BDF为：{0}".format(BDF))
        if BDF:
            for i in BDF:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH,"lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("SAS卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
                if 'MaxReadReq 256 bytes' in cmd_result2:
                    logging.info('修改最大读需求大小为256B成功')
                else:
                    stylelog.fail('修改最大读需求大小为256B失败')
                    return
        else:
            logging.warning("SAS卡不存在，跳过RAID卡测试")

        # 网卡测试
        logging.info('网卡测试..............................................')
        while True:
            cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
            if cmd_result:
                break
        cmd_result = cmd_result[0]
        BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
        logging.info("所有网卡的BDF为：{0}".format(BDF))
        if BDF:
            for i in BDF:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("网卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
                if 'MaxReadReq 256 bytes' in cmd_result2:
                    logging.info('修改最大读需求大小为256B成功')
                else:
                    stylelog.fail('修改最大读需求大小为256B失败')
                    return
        else:
            logging.warning("网卡不存在，跳过RAID卡测试")

    # 512B
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_READ_REQUEST_512B,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("RAID卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 512 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为512B成功')
            else:
                stylelog.fail('修改最大读需求大小为512B失败')
                return
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

    # SAS卡测试
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH,"lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("SAS卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 512 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为512B成功')
            else:
                stylelog.fail('修改最大读需求大小为512B失败')
                return
    else:
        logging.warning("SAS卡不存在，跳过RAID卡测试")

    # 网卡测试
    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                if cmd_result2:
                    break
            cmd_result2 = cmd_result2[0]
            logging.info("网卡 {0} 实际支持的MaxReadReq为：{1}".format(i, cmd_result2))
            if 'MaxReadReq 512 bytes' in cmd_result2:
                logging.info('修改最大读需求大小为512B成功')
            else:
                stylelog.fail('修改最大读需求大小为512B失败')
                return
    else:
        logging.warning("网卡不存在，跳过RAID卡测试")
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_READ_REQUEST_AUTO,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(6)
    return True



def pcie_aspm():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_ASPM_L1,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1" in cmd_result1 or "ASPM L1" in cmd_result1 and "ASPM L0s" not in cmd_result1:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("RAID卡 {0} 实际ASPM结果为：{1}".format(i, cmd_result2))
                if 'ASPM L1 Enabled' in cmd_result2:
                    logging.info('修改PCIE ASPM为L1成功')
                elif 'ASPM Disabled' in cmd_result2:
                    stylelog.fail('修改PCIE ASPM为L1失败,PCIE ASPM 是关闭的')
                    return
                else:
                    stylelog.fail('命令返回结果为{0}'.format(cmd_result2))
                    return
            else:
                logging.warning("RAID卡 {0} 不支持 ASPM L1，跳过测试".format(i))
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

# 网卡测试
    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1" in cmd_result1 or "ASPM L1" in cmd_result1 and "ASPM L0s" not in cmd_result1:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("网卡 {0} 实际ASPM结果为：{1}".format(i, cmd_result2))
                if 'ASPM L1 Enabled' in cmd_result2:
                    logging.info('修改PCIE ASPM为L1成功')
                elif 'ASPM Disabled' in cmd_result2:
                    stylelog.fail('修改PCIE ASPM为L1失败,PCIE ASPM 是关闭的')
                    return
                else:
                    stylelog.fail('命令返回结果为{0}'.format(cmd_result2))
                    return
            else:
                logging.warning("网卡 {0} 不支持 ASPM L1，跳过测试".format(i))
    else:
        stylelog.fail('BDF为空')
        return

# SAS测试
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1" in cmd_result1 or "ASPM L1" in cmd_result1 and "ASPM L0s" not in cmd_result1:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("SAS卡 {0} 实际ASPM结果为：{1}".format(i, cmd_result2))
                if 'ASPM L1 Enabled' in cmd_result2:
                    logging.info('修改PCIE ASPM为L1成功')
                elif 'ASPM Disabled' in cmd_result2:
                    stylelog.fail('修改PCIE ASPM为L1失败,PCIE ASPM 是关闭的')
                    return
                else:
                    stylelog.fail('命令返回结果为{0}'.format(cmd_result2))
                    return
            else:
                logging.warning("SAS卡 {0} 不支持 ASPM L1，跳过测试".format(i))
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")

# PCIE活动状态电源管理：关闭
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_ASPM_DISABLED,6)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1" in cmd_result1 or "ASPM L1" in cmd_result1 and "ASPM L0s" not in cmd_result1:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("RAID卡 {0} 实际ASPM结果为：{1}".format(i, cmd_result2))
                if 'ASPM Disabled' in cmd_result2:
                    logging.info('修改PCIE ASPM为关闭成功')
                elif 'ASPM L1 Enabled' in cmd_result2:
                    stylelog.fail('修改PCIE ASPM为关闭失败，PCIE ASPM是L1')
                    return
                else:
                    stylelog.fail('命令返回结果为{0}'.format(cmd_result2))
                    return
            else:
                logging.warning("RAID卡 {0} 不支持 ASPM L1，跳过测试".format(i))
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

# 网卡测试
    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1" in cmd_result1 or "ASPM L1" in cmd_result1 and "ASPM L0s" not in cmd_result1:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("网卡 {0} 实际ASPM结果为：{1}".format(i, cmd_result2))
                if 'ASPM Disabled' in cmd_result2:
                    logging.info('修改PCIE ASPM为关闭成功')
                elif 'ASPM L1 Enabled' in cmd_result2:
                    stylelog.fail('修改PCIE ASPM为关闭失败，PCIE ASPM是L1')
                    return
                else:
                    stylelog.fail('命令返回结果为{0}'.format(cmd_result2))
                    return
            else:
                logging.warning("网卡 {0} 不支持 ASPM L1，跳过测试".format(i))
    else:
        stylelog.fail('BDF为空')
        return

# SAS测试
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1" in cmd_result1 or "ASPM L1" in cmd_result1 and "ASPM L0s" not in cmd_result1:
                while True:
                    cmd_result2 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
                    if cmd_result2:
                        break
                cmd_result2 = cmd_result2[0]
                logging.info("SAS卡 {0} 实际ASPM结果为：{1}".format(i, cmd_result2))
                if 'ASPM Disabled' in cmd_result2:
                    logging.info('修改PCIE ASPM为关闭成功')
                elif 'ASPM L1 Enabled' in cmd_result2:
                    stylelog.fail('修改PCIE ASPM为关闭失败，PCIE ASPM是L1')
                    return
                else:
                    stylelog.fail('命令返回结果为{0}'.format(cmd_result2))
                    return
            else:
                logging.warning("SAS卡 {0} 不支持 ASPM L1，跳过测试".format(i))
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")
    return True



# 4GB以上空间解码
def Above_4G_Decoding():
    count_enable = 0
    count_disable = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_4G_DECODING_ENABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证网卡的BDF为：{0}'.format(i))
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.info('4GB以上空间解码打开成功，网卡的BDF为{0}'.format(i))
                count_enable += 1
            else:
                logging.info('网卡的4GB以上空间解码可能不支持，需手动确认')
                logging.error('失败网卡的BDF为{0}'.format(i))
                count_disable += 1
    else:
        logging.info('网卡不存在，跳过网卡测试')

    # raid
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI | awk '{print $1}'")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证RAID卡的BDF为：{0}'.format(i))
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.info('4GB以上空间解码打开成功，RAID卡的BDF为{0}'.format(i))
                count_enable += 1
            else:
                logging.info('RAID卡的4GB以上空间解码可能不支持，需手动确认')
                logging.error('失败RAID卡的BDF为{0}'.format(i))
                count_disable += 1
    else:
        logging.info('RAID卡不存在，跳过RAID卡测试')

    # SAS
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS | awk '{print $1}'")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证SAS卡的BDF为：{0}'.format(i))
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.info('4GB以上空间解码打开成功，SAS卡的BDF为{0}'.format(i))
                count_enable += 1
            else:
                logging.info('4GB以上空间解码可能不支持，需手动确认')
                logging.error('失败SAS的BDF为{0}'.format(BDF))
                count_disable += 1
    else:
        logging.info('SAS卡不存在，跳过SAS卡测试')
    logging.info("支持above 4G的BDF共有{0}".format(count_enable))
    logging.info("不支持above 4G的BDF共有{0}".format(count_disable))

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_4G_DECODING_DISABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    assert SetUpLib.boot_os_from_bm()

    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证网卡的BDF为：{0}'.format(i))
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.error('4GB以上空间解码关闭失败')
                logging.info('关闭失败网卡的BDF为{0}'.format(i))
                return
            else:
                logging.info('4GB以上空间解码关闭成功')
    else:
        logging.info('网卡不存在，跳过网卡测试')

    # raid
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI | awk '{print $1}'")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证RAID卡的BDF为：{0}'.format(i))
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            # print(cmd_result2)
            if cmd_result2 > 8:
                logging.error('4GB以上空间解码关闭失败')
                logging.info('关闭失败RAID卡的BDF为{0}'.format(i))
                return
            else:
                logging.info('4GB以上空间解码关闭成功')
    else:
        logging.info('RAID卡不存在，跳过RAID卡测试')

    # SAS
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS | awk '{print $1}'")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证SAS卡的BDF为：{0}'.format(i))
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.error('4GB以上空间解码关闭失败')
                logging.info('关闭失败SAS卡的BDF为{0}'.format(i))
                return
            else:
                logging.info('4GB以上空间解码关闭成功')
    else:
        logging.info('SAS卡不存在，跳过SAS卡测试')

    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.PCIE.SET_4G_DECODING_ENABLED,6)
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(2)
    if count_enable >= 1:
        return True



def pcie_device_link_status():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN,Sut01Config.PCIE.BOOT_PCIE_CONFIG,8)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_os_from_bm()
    count = 0
    logging.info('RAID卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep LSI")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            support = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result)
            logging.info("{0} 的最大支持带宽为：{1}".format(i, support))
            time.sleep(2)
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkSta".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            actual = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result1)
            logging.info("{0} 的实际带宽为：    {1}".format(i, actual))
            if support == actual:
                logging.info('{0}最大支持与实际相符'.format(i))
            else:
                stylelog.fail('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
                count += 1
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")

    logging.info('网卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep Eth")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    for i in BDF:
        while True:
            cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            if cmd_result:
                break
        cmd_result = cmd_result[0]
        support = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result)
        logging.info("{0} 的最大支持带宽为：{1}".format(i, support))
        time.sleep(2)
        while True:
            cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkSta".format(i))
            if cmd_result1:
                break
        cmd_result1 = cmd_result1[0]
        actual = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result1)
        logging.info("{0} 的实际带宽为：    {1}".format(i, actual))
        if support == actual:
            logging.info('{0}最大支持与实际相符'.format(i))
        else:
            stylelog.fail('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
            count += 1
    logging.info('SAS卡测试..............................................')
    while True:
        cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci | grep SAS")
        if cmd_result:
            break
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            while True:
                cmd_result = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                if cmd_result:
                    break
            cmd_result = cmd_result[0]
            support = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result)
            logging.info("{0} 的最大支持带宽为：{1}".format(i, support))
            time.sleep(2)
            while True:
                cmd_result1 = SshLib.execute_command(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkSta".format(i))
                if cmd_result1:
                    break
            cmd_result1 = cmd_result1[0]
            actual = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result1)
            logging.info("{0} 的实际带宽为：    {1}".format(i, actual))
            if support == actual:
                logging.info('{0}最大支持与实际相符'.format(i))
            else:
                stylelog.fail('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
                count += 1
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")
    if count == 0:
        return True
    else:
        return