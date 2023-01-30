# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *


def pcie_max_payload(oem):
    for value in SutConfig.Pci.PCIE_MAX_VALUE[:-1]:
        if oem is True:
            BmcLib.change_bios_value([f'MaxPayload:{value}', 'OnLan:Enabled'])
        else:
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_LAN, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN,
                                                    SutConfig.Pci.LOC_PCIE + [{SutConfig.Pci.PCIE_MAX_NAME: value}], 18,
                                                    save=True)
        assert SetUpLib.boot_os_from_bm()
        speed = re.findall('(\d+)B', value)[0] if re.findall('(\d+)B', value) else '128'

        logging.info('RAID卡测试..............................................')
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep LSI")
        cmd_result = cmd_result[0]
        BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
        logging.info("所有RAID卡的BDF为：{0}".format(BDF))
        if BDF != []:
            for i in BDF:
                cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                           "lspci -vvv -s {0} | grep DevCap[^0-9]".format(i))
                cmd_result1 = cmd_result1[0]
                logging.info("RAID卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
                cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
                if int(cmd_result1) >= int(speed):

                    cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                               "lspci -vvv -s {0} | grep MaxReadReq".format(i))

                    cmd_result2 = cmd_result2[0]
                    logging.info("RAID卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                    if f'MaxPayload {speed} bytes' in cmd_result2:
                        logging.info(f'修改PCIE最大负载为{speed}B成功')
                    else:
                        stylelog.fail(f'修改PCIE最大负载为{speed}B失败')
                        return
                else:
                    logging.info("RAID卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
        else:
            logging.warning("RAID卡不存在，跳过RAID卡测试")
        logging.info('网卡测试..............................................')
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
        cmd_result = cmd_result[0]
        BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
        logging.info("所有网卡的BDF为：{0}".format(BDF))
        if BDF != []:
            for i in BDF:
                cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                           "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                cmd_result1 = cmd_result1[0]
                logging.info("网卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
                cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
                if int(cmd_result1) >= int(speed):
                    cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                               "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    cmd_result2 = cmd_result2[0]
                    logging.info("网卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                    if f'MaxPayload {speed} bytes' in cmd_result2:
                        logging.info(f'修改PCIE最大负载为{speed}B成功')
                    else:
                        stylelog.fail(f'修改PCIE最大负载为{speed}B失败')
                        return
                else:
                    logging.info("网卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
        else:
            stylelog.fail("BDF无效")
            return
        logging.info('SAS卡测试..............................................')
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep SAS")
        cmd_result = cmd_result[0]
        BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
        logging.info("所有SAS卡的BDF为：{0}".format(BDF))
        if BDF != []:
            for i in BDF:
                cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                           "lspci -vvv -s {0} | grep -I DevCap[^0-9]".format(i))
                cmd_result1 = cmd_result1[0]
                logging.info("SAS卡 {0} 最大支持的MaxPayload为：{1}".format(i, cmd_result1))
                cmd_result1 = re.findall('MaxPayload ([0-9]+) bytes', cmd_result1)[0]
                if int(cmd_result1) >= int(speed):
                    cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH,
                                                               "lspci -vvv -s {0} | grep MaxReadReq".format(i))
                    cmd_result2 = cmd_result2[0]
                    logging.info("SAS卡 {0} 实际支持的MaxPayload为：{1}".format(i, cmd_result2))
                    if f'MaxPayload {speed} bytes' in cmd_result2:
                        logging.info(f'修改PCIE最大负载为{speed}B成功')
                    else:
                        stylelog.fail(f'修改PCIE最大负载为{speed}B失败')
                        return
                else:
                    logging.info("SAS卡 {0} 最大支持的MaxPayload不满足测试要求，跳过测试".format(i))
        else:
            logging.warning("SAS卡不存在，跳过SAS卡测试")
    if oem is True:
        BmcLib.change_bios_value([f'MaxPayload:{SutConfig.Pci.PCIE_MAX_VALUE[-1]}'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.LOC_PCIE + [
            {SutConfig.Pci.PCIE_MAX_NAME: SutConfig.Pci.PCIE_MAX_VALUE[-1]}], 18, save=True)
    return True


def pcie_aspm(oem):
    if oem is True:
        BmcLib.change_bios_value(['ASPM:L1', 'OnLan:Enabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_LAN, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_ASPM, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep LSI")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
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
    logging.info('网卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
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
    logging.info('SAS卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep SAS")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
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
    if oem is True:
        BmcLib.change_bios_value(['ASPM:Disabled'])
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.CLOSE_ASPM, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    logging.info('RAID卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep LSI")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result1 = cmd_result1[0]
            logging.info("RAID卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
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
    logging.info('网卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result1 = cmd_result1[0]
            logging.info("网卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
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
    logging.info('SAS卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep SAS")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result1 = cmd_result1[0]
            logging.info("SAS卡 {0} 支持ASPM L1能力为：{1}".format(i, cmd_result1))
            if "ASPM L0s L1," in cmd_result1 or "ASPM L1," in cmd_result1 and "ASPM L0s," not in cmd_result1:
                cmd_result2 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCtl".format(i))
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


def pcie_device_link_status():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_LAN, 10, save=True)
    assert SetUpLib.boot_os_from_bm()
    count = 0
    wrong_msg = []
    logging.info('RAID卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep LSI")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有RAID卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result = cmd_result[0]
            support = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result)
            logging.info("{0} 的最大支持带宽为：{1}".format(i, support))
            time.sleep(2)
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkSta".format(i))
            cmd_result1 = cmd_result1[0]
            actual = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result1)
            logging.info("{0} 的实际带宽为：    {1}".format(i, actual))
            if support == actual:
                logging.info('{0}最大支持与实际相符'.format(i))
            else:
                stylelog.fail('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
                wrong_msg.append('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
                count += 1
    else:
        logging.warning("RAID卡不存在，跳过RAID卡测试")
    logging.info('网卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有网卡的BDF为：{0}".format(BDF))
    for i in BDF:
        cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
        cmd_result = cmd_result[0]
        support = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result)
        logging.info("{0} 的最大支持带宽为：{1}".format(i, support))
        time.sleep(2)
        cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkSta".format(i))
        cmd_result1 = cmd_result1[0]
        actual = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result1)
        logging.info("{0} 的实际带宽为：    {1}".format(i, actual))
        if support == actual:
            logging.info('{0}最大支持与实际相符'.format(i))
        else:
            stylelog.fail('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
            wrong_msg.append('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
            count += 1
    logging.info('SAS卡测试..............................................')
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep SAS")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    logging.info("所有SAS卡的BDF为：{0}".format(BDF))
    if BDF:
        for i in BDF:
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkCap".format(i))
            cmd_result = cmd_result[0]
            support = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result)
            logging.info("{0} 的最大支持带宽为：{1}".format(i, support))
            time.sleep(2)
            cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep -w LnkSta".format(i))
            cmd_result1 = cmd_result1[0]
            actual = re.findall(r'(Speed .*/s).*(Width x[0-9])', cmd_result1)
            logging.info("{0} 的实际带宽为：    {1}".format(i, actual))
            if support == actual:
                logging.info('{0}最大支持与实际相符'.format(i))
            else:
                stylelog.fail('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
                wrong_msg.append('{0}最大支持与实际不符，最大支持{1}，实际{2}'.format(i, support, actual))
                count += 1
    else:
        logging.warning("SAS卡不存在，跳过SAS卡测试")
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def above_4gb():
    count_enable = 0
    count_disable = 0
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.OPEN_ABOVE, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth | grep -v Wangxun | awk '{print $1}'")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证网卡的BDF为：{0}'.format(i))
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.info('4GB以上空间解码打开成功，网卡的BDF为{0}'.format(i))
                count_enable += 1
            else:
                logging.info('网卡的4GB以上空间解码可能不支持，需手动确认')
                stylelog.fail('失败网卡的BDF为{0}'.format(i))
                count_disable += 1
    else:
        logging.info('网卡不存在，跳过网卡测试')
    # raid
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep LSI | awk '{print $1}'")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证RAID卡的BDF为：{0}'.format(i))
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.info('4GB以上空间解码打开成功，RAID卡的BDF为{0}'.format(i))
                count_enable += 1
            else:
                logging.info('RAID卡的4GB以上空间解码可能不支持，需手动确认')
                stylelog.fail('失败RAID卡的BDF为{0}'.format(i))
                count_disable += 1
    else:
        logging.info('RAID卡不存在，跳过RAID卡测试')
    # SAS
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep SAS | awk '{print $1}'")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证SAS卡的BDF为：{0}'.format(i))
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                logging.info('4GB以上空间解码打开成功，SAS卡的BDF为{0}'.format(i))
                count_enable += 1
            else:
                logging.info('4GB以上空间解码可能不支持，需手动确认')
                stylelog.fail('失败SAS的BDF为{0}'.format(BDF))
                count_disable += 1
    else:
        logging.info('SAS卡不存在，跳过SAS卡测试')
    logging.info("支持above 4G的BDF共有{0}".format(count_enable))
    logging.info("不支持above 4G的BDF共有{0}".format(count_disable))
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.CLOSE_ABOVE, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth | grep -v Wangxun | awk '{print $1}'")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证网卡的BDF为：{0}'.format(i))
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                stylelog.fail('4GB以上空间解码关闭失败')
                logging.info('关闭失败网卡的BDF为{0}'.format(i))
                return
            else:
                logging.info('4GB以上空间解码关闭成功')
    else:
        logging.info('网卡不存在，跳过网卡测试')
    # raid
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep LSI | awk '{print $1}'")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证RAID卡的BDF为：{0}'.format(i))
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            # print(cmd_result2)
            if cmd_result2 > 8:
                stylelog.fail('4GB以上空间解码关闭失败')
                logging.info('关闭失败RAID卡的BDF为{0}'.format(i))
                return
            else:
                logging.info('4GB以上空间解码关闭成功')
    else:
        logging.info('RAID卡不存在，跳过RAID卡测试')
    # SAS
    cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep SAS | awk '{print $1}'")
    cmd_result = cmd_result[0]
    BDF = re.findall(r'[0-9]{2}:[0-9]{2}\.[0-9]', cmd_result)
    if BDF:
        for i in BDF:
            logging.info('当前验证SAS卡的BDF为：{0}'.format(i))
            cmd_result = SshLib.execute_command_limit(Sut.OS_SSH, "lspci -vvv -s {0} | grep 'Region.*\['".format(i))
            cmd_result = cmd_result[0]
            cmd_result1 = re.findall(r'Memory at ([a-z0-9]+)', cmd_result)
            logging.info('Memory at {0}'.format(cmd_result1))
            cmd_result2 = len(cmd_result1[0])
            if cmd_result2 > 8:
                stylelog.fail('4GB以上空间解码关闭失败')
                logging.info('关闭失败SAS卡的BDF为{0}'.format(i))
                return
            else:
                logging.info('4GB以上空间解码关闭成功')
    else:
        logging.info('SAS卡不存在，跳过SAS卡测试')
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pci.CLOSE_ABOVE, 18, save=True)
    if count_enable >= 1:
        return True
    else:
        stylelog.fail('没有设备支持')
        return
