# -*- encoding=utf8 -*-
import re
import time
import logging
from D2000.BaseLib import SetUpLib, SshLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from batf.Report import stylelog
from batf import core
from batf.SutInit import Sut


@core.test_case(('201', '[TC201]PCIE ASPM', 'PCIE 活动状态电源管理'))
def pcie_aspm():
    ALL_CHANGED_ASPM = SutConfig.Pci.ALL_CHANGED_ASPM
    ASPM_MSG = SutConfig.Pci.ASPM_MSG
    try:
        count = 0
        wrong_msg = []
        for index in range(len(ALL_CHANGED_ASPM)):
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN, ALL_CHANGED_ASPM[index], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(2)
            assert SetUpLib.boot_os_from_bm()
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci")
            cmd_result = cmd_result[0]
            BDF = re.findall(r'[\w]{2}:[\w]{2}\.[\w]', cmd_result)
            BDF = list(set(BDF) - set(SutConfig.Pci.EXCEPT_BDF))
            if BDF:
                for i in BDF:
                    cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                               "lspci -vvv -s {0} | grep -w LnkCap".format(i))
                    cmd_result1 = cmd_result1[0]
                    if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                        cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                                   "lspci -vvv -s {0} | grep -w LnkCtl".format(i))

                        cmd_result2 = cmd_result2[0]
                        if ASPM_MSG[index] == 'Disabled':
                            if f'ASPM {ASPM_MSG[index]}' in cmd_result2:
                                logging.info(f'修改PCIE ASPM为{ASPM_MSG[index]}成功')
                            else:
                                stylelog.fail(f'{i},修改PCIE ASPM为{ASPM_MSG[index]}失败,命令返回结果为{cmd_result2}')
                                wrong_msg.append(f'{i},修改PCIE ASPM为{ASPM_MSG[index]}失败,命令返回结果为{cmd_result2}')
                                count += 1
                        else:
                            if f'ASPM {ASPM_MSG[index]} Enabled' in cmd_result2:
                                logging.info(f'修改PCIE ASPM为{ASPM_MSG[index]}成功')
                            else:
                                stylelog.fail(f'{i},修改PCIE ASPM为{ASPM_MSG[index]}失败,命令返回结果为{cmd_result2}')
                                wrong_msg.append(f'{i},修改PCIE ASPM为{ASPM_MSG[index]}失败,命令返回结果为{cmd_result2}')
                                count += 1
            else:
                logging.info('没有PCIE设备，跳过测试')
                return core.Status.Skip

        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('202', '[TC202]PCIE Max Payload Size', 'PCIE最大负载'))
def pcie_max_payload():
    try:
        count = 0
        assert SetUpLib.boot_os_from_bm()
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci")[0]
        BDF = re.findall(r'[\w]{2}:[\w]{2}\.[\w]', cmd_result)
        BDF = list(set(BDF) - set(SutConfig.Pci.EXCEPT_BDF))
        if BDF:
            for i in BDF:
                cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                           "lspci -vvv -s {0} | grep DevCap[^0-9]".format(i))
                cmd_result1 = cmd_result1[0]
                cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)
                if cmd_result1:
                    logging.info(f"{i} 最大支持的MaxPayload为：{cmd_result1[0]}")
                    if int(cmd_result1[0]) >= 128:
                        cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                                   "lspci -vvv -s {0} | grep MaxReadReq".format(i))

                        cmd_result2 = cmd_result2[0]

                        if 'MaxPayload 128 bytes' in cmd_result2:
                            logging.info('PCIE最大负载为128B验证成功')
                        else:
                            stylelog.fail('PCIE最大负载为128B验证失败')
                            stylelog.fail("RAID卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                            count += 1
                    else:
                        logging.info(f"{0} 最大支持的MaxPayload不满足测试要求，跳过测试")
                else:
                    logging.info(f'{i}不支持MaxPayload，跳过测试')
        else:
            logging.info('没有PCIE设备,跳过测试')
            return core.Status.Fail
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('203', '[TC203]PCIE Max Read Request Size', 'PCIE最大读需求大小'))
def pcie_max_read():
    ALL_MAX_READ = SutConfig.Pci.ALL_MAX_READ
    MAX_READ_MSG = SutConfig.Pci.MAX_READ_MSG
    try:
        count = 0
        wrong_msg = []
        for index in range(len(ALL_MAX_READ)):
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN, ALL_MAX_READ[index], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(2)
            assert SetUpLib.boot_os_from_bm()
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci")[0]
            BDF = re.findall(r'[\w]{2}:[\w]{2}\.[\w]', cmd_result)
            BDF = list(set(BDF) - set(SutConfig.Pci.EXCEPT_BDF))
            if BDF:
                for i in BDF:
                    cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                               "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    cmd_result2 = cmd_result2[0]
                    if f'MaxReadReq {MAX_READ_MSG[index]} bytes' in cmd_result2:
                        logging.info(f'修改PCIE最大读需求为{MAX_READ_MSG[index]}B成功')
                    else:
                        stylelog.fail(f'修改PCIE最大读需求为{MAX_READ_MSG[index]}B失败')
                        stylelog.fail(f" {i} 实际支持的MaxReadReq为：{cmd_result2}")
                        wrong_msg.append(f'修改PCIE最大读需求为{MAX_READ_MSG[index]}B失败')
                        wrong_msg.append(f" {i} 实际支持的MaxReadReq为：{cmd_result2}")
                        count += 1
            else:
                logging.info('PCIE设备不存在,跳过测试')
                return core.Status.Skip
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return


    except Exception as e:
        logging.error(e)
        return core.Status.Fail
