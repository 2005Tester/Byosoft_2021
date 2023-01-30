# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

session = RedFishLib.Redfish()


def check_bios_version():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_MAIN)
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)
    version_setup = re.findall(r'Release Version +([0-9\.]+) ', data)[0]
    result = session.get_msg('/redfish/v1/Systems/1')
    if result["BiosVersion"] == version_setup:
        logging.info('BIOS版本号，SetUp下与RedFish一致')
    else:
        stylelog.fail(f'BIOS版本号，SetUp下与RedFish不一致，SetUp{version_setup},RedFish{result["BiosVersion"]}')
        return
    return True


def power_management():
    body = {
        "ResetType": "ForceOff"
    }
    status_url = '/redfish/v1/Systems/1'
    power_url = '/redfish/v1/Systems/1/Actions/ComputerSystem.Reset'
    logging.info('BMC 关机......................')
    BmcLib.power_off()
    time.sleep(10)
    if session.get_msg(status_url)['PowerState'] == 'Off':
        logging.info('关机状态，RedFish读取电源状态为Off')
    else:
        stylelog.info('关机状态，RedFish读取电源状态失败')
        return
    logging.info('BMC 开机..............................')
    BmcLib.power_on()
    time.sleep(10)
    if session.get_msg(status_url)['PowerState'] == 'On':
        logging.info('开机状态，RedFish读取电源状态为On')
    else:
        stylelog.info('开机状态，RedFish读取电源状态失败')
        return
    time.sleep(5)
    logging.info('RedFish 关机...........................')
    body['ResetType'] = 'ForceOff'
    session.post(power_url, body)
    time.sleep(10)
    if BmcLib.power_status() == "Chassis Power is off":
        logging.info('RedFish 关机，BMC 验证成功')
    else:
        stylelog.fail('RedFish 关机，BMC 验证失败')
        return
    time.sleep(5)
    logging.info('RedFish 开机................................')
    body['ResetType'] = 'On'
    session.post(power_url, body)
    time.sleep(10)
    if BmcLib.power_status() == "Chassis Power is on":
        logging.info('RedFish 开机，BMC 验证成功')
    else:
        stylelog.fail('RedFish 开机，BMC 验证失败')
        return
    time.sleep(5)
    return True


def check_cpu_frequency():
    count = 0
    wrong_msg = []
    url = '/redfish/v1/Systems/1/Processors?$expand=.'
    cpu_speed = SutConfig.Cpu.CPU_FREQUENCY
    assert SetUpLib.boot_to_setup()
    for speed in cpu_speed:
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(2)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.SET_FREQUENCY, 15)
        time.sleep(2)
        assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Cpu.SET_CPU_SPEED_NAME], 5, '{0} MHz'.format(speed))
        time.sleep(3)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        time.sleep(5)
        cpu_info = session.get_msg(url)
        if cpu_info:
            if all(i['Oem']['Public']['FrequencyMHz'] == int(speed) for i in cpu_info['Members']):
                logging.info(f'SetUp 下修改CPU频率为{speed}MHz,RedFish验证通过')
            else:
                stylelog.fail(
                    f"SetUp 下修改CPU频率为{speed}MHz,RedFish验证失败，RedFish：{cpu_info['Members'][0]['Oem']['Public']['FrequencyMHz']}")
                wrong_msg.append(
                    f"SetUp 下修改CPU频率为{speed}MHz,RedFish验证失败，RedFish：{cpu_info['Members'][0]['Oem']['Public']['FrequencyMHz']}")
                count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def check_cpu_core_thread():
    count = 0
    wrong_msg = []
    url = '/redfish/v1/Systems/1/Processors?$expand=.'
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CLOSE_HYPER_THREADING, 10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CPU_INFO, 5)
    data = SetUpLib.get_data(3)
    l1_setup = re.findall('L1 Cache Size +(\d+)', data)[0]
    l2_setup = re.findall('L2 Cache Size +(\d+)', data)[0]
    l3_setup = re.findall('L3 Cache Size +(\d+)', data)[0]
    thread_count_close = re.findall('CPU Thread Count +(\d+)', data)[0]
    core_count = re.findall('CPU Core Count +(\d+)', data)[0]
    cpu_info = session.get_msg(url)
    if cpu_info['Members'][0]['Oem']['Public']['L1CacheKiB'] == int(l1_setup):
        logging.info('RedFish读取的L1与SetUp一致')
    else:
        if cpu_info['Members'][0]['Oem']['Public']['L1CacheKiB'] == int(l1_setup) * 1024:
            logging.info('RedFish读取的L1与SetUp一致')
        else:
            stylelog.fail(
                f"RedFish读取的L1与SetUp不一致，SetUp{l1_setup},RedFish{cpu_info['Members'][0]['Oem']['Public']['L1CacheKiB']}")
            count += 1

    if cpu_info['Members'][0]['Oem']['Public']['L2CacheKiB'] == int(l2_setup):
        logging.info('RedFish读取的L1与SetUp一致')
    else:
        if cpu_info['Members'][0]['Oem']['Public']['L2CacheKiB'] == int(l2_setup) * 1024:
            logging.info('RedFish读取的L2与SetUp一致')
        else:
            stylelog.fail(
                f"RedFish读取的L2与SetUp不一致，SetUp{l2_setup},RedFish{cpu_info['Members'][0]['Oem']['Public']['L2CacheKiB']}")
            count += 1

    if cpu_info['Members'][0]['Oem']['Public']['L3CacheKiB'] == int(l3_setup):
        logging.info('RedFish读取的L1与SetUp一致')
    else:
        if cpu_info['Members'][0]['Oem']['Public']['L3CacheKiB'] == int(l3_setup) * 1024:
            logging.info('RedFish读取的L3与SetUp一致')
        else:
            stylelog.fail(
                f"RedFish读取的L3与SetUp不一致，SetUp{l3_setup},RedFish{cpu_info['Members'][0]['Oem']['Public']['L3CacheKiB']}")
            count += 1
    if cpu_info['Members'][0]['TotalCores'] == int(core_count):
        logging.info('RedFish读取的Core Count与SetUp一致')
    else:
        stylelog.fail(
            f"RedFish读取的Core Count与SetUp不一致，SetUp：{core_count},RedFish:{cpu_info['Members'][0]['TotalCores']}")
        count += 1
        wrong_msg.append(
            f"RedFish读取的Core Count与SetUp不一致，SetUp：{core_count},RedFish:{cpu_info['Members'][0]['TotalCores']}")
    if all(i['TotalThreads'] == int(thread_count_close) for i in cpu_info['Members']):
        logging.info('超线程关闭，setup下Thread Count 与RedFish读取的值一致')
    else:
        stylelog.fail(
            f"setup下Thread Count 与RedFish不一致,SetUp:{thread_count_close},RedFish:{cpu_info['Members'][0]['TotalThreads']}")
        count += 1
        wrong_msg.append(
            f"setup下Thread Count 与RedFish不一致,SetUp:{thread_count_close},RedFish:{cpu_info['Members'][0]['TotalThreads']}")
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.OPEN_HYPER_THREADING, 10)
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    thread_count_open = str(int(thread_count_close) * 2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Cpu.CPU_INFO, 5)
    if SetUpLib.wait_message('CPU Thread Count +{0}'.format(thread_count_open), 10, readline=True):
        logging.info('超线程打开，setup下Thread Count 变为2倍')
    else:
        stylelog.fail('超线程打开，setup下Thread Count 没有变为2倍')
        count += 1
        wrong_msg.append('超线程打开，setup下Thread Count 没有变为2倍')
    cpu_info = session.get_msg(url)
    if all(i['TotalThreads'] == int(thread_count_open) for i in cpu_info['Members']):
        logging.info('超线程打开，RedFish读取的值变为2倍')
    else:
        stylelog.fail(
            f"超线程打开，RedFish读取的值没有变为2倍,RedFish:{cpu_info['Members'][0]['TotalThreads']}")
        count += 1
        wrong_msg.append(
            f"超线程打开，RedFish读取的值没有变为2倍,RedFish:{cpu_info['Members'][0]['TotalThreads']}")
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def rfh_change_hyper_thread():
    url = '/redfish/v1/Systems/1/Processors?$expand=.'
    data_close = {
        "Attributes":
            {"ProcessorHyperThreading": "Disabled"
             }
    }
    data_open = {
        "Attributes": {"ProcessorHyperThreading": "Enabled"
                       }
    }

    result = session.change_bios_value(data_close)
    if result.status == 200:
        logging.info('RedFish修改选项成功')
    else:
        stylelog.fail('RedFish修改选项失败')
        return
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    cpu_info = session.get_msg(url)
    close_thread = cpu_info['Members'][0]['TotalThreads']
    result = session.change_bios_value(data_open)
    if result.status == 200:
        logging.info('RedFish修改选项成功')
    else:
        stylelog.fail('RedFish修改选项失败')
        return
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    cpu_info = session.get_msg(url)
    open_thread = cpu_info['Members'][0]['TotalThreads']
    logging.info(f'超线程打开：{open_thread}')
    logging.info(f'超线程关闭：{close_thread}')
    if open_thread == close_thread * 2:
        logging.info('RedFish 打开，关闭超线程验证成功')
        return True
    else:
        stylelog.fail('RedFish 打开，关闭超线程验证失败')
        return


def check_mem():
    assert SetUpLib.boot_os_from_bm()
    dict = {'DIMM001': 'DIMMA1',
            'DIMM003': 'DIMMB1',
            'DIMM005': 'DIMMC1',
            'DIMM007': 'DIMMD1',
            'DIMM009': 'DIMME1',
            'DIMM011': 'DIMMF1',
            'DIMM013': 'DIMMG1',
            'DIMM015': 'DIMMH1'}
    count = 0
    wrong_msg = []
    mem_dict_redfish = {}
    mem_msg_redfish = session.get_msg('/redfish/v1/Systems/1/Memory?$expand=.')
    for i in mem_msg_redfish['Members']:
        mem_dict_redfish[i["DeviceLocator"]] = [str(i['CapacityMiB'])[:2], i['Manufacturer'], i['MemoryDeviceType'],
                                                str(i['OperatingSpeedMhz']), i['PartNumber'], i['SerialNumber']]

    result = SshLib.execute_command_limit(Sut.OS_SSH, 'dmidecode -t 17')[0]
    for i in result.split('Memory Device'):
        for j in dict.keys():
            if dict[j] in i:
                list = []
                list += re.findall('Size: (\d{2})', i)
                list += re.findall('Manufacturer: ([\w ]+)', i)
                list += re.findall('Type: ([\w ]+)', i)
                list += re.findall('[^ ]Speed: (\d+)', i)
                list += re.findall('Part Number: ([\w -]+)', i)
                list += re.findall('Serial Number: ([\w ]+)', i)
                if list == mem_dict_redfish[j]:
                    logging.info(f'内存{dict[j]},系统下与RedFish一致')
                    logging.info(list)
                else:
                    stylelog.fail(f'内存{dict[j]},系统下与RedFish不一致,系统{list},RedFish{mem_dict_redfish[j]}')
                    count += 1
                    wrong_msg.append(f'内存{dict[j]},系统下与RedFish不一致,系统{list},RedFish{mem_dict_redfish[j]}')
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def check_hdd():
    count = 0
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sup.LOC_SATA, 10)
    data = SetUpLib.get_data(2)
    if 'M.2 Driver 1' not in data:
        try_counts = 100
        while try_counts:
            SetUpLib.send_key(Key.DOWN)
            data = SetUpLib.get_data(1)
            if 'M.2 Driver 1' in data:
                break
            try_counts -= 1
    result = session.get_msg('/redfish/v1/Chassis/1/Drives?$expand=.')
    for i in result["Members"]:
        logging.info(f"硬盘{i['@odata.id']}信息检查")
        if str(i["CapableSpeedGbs"]) in data:
            logging.info('硬盘速度验证通过')
        else:
            stylelog.fail('硬盘速度验证失败')
            count += 1
        if f'{str(int(i["CapacityBytes"] / 1073741824))}GB' in data or f'{str(int(i["CapacityBytes"] / 1099511627776))}TB' in data:
            logging.info('硬盘容量验证通过')
        else:
            stylelog.fail('硬盘容量验证失败')
            count += 1
        if i["Manufacturer"] in data:
            logging.info('硬盘厂商验证通过')
        else:
            stylelog.fail('硬盘厂商验证失败')
            count += 1
        if i["MediaType"] in data:
            logging.info('硬盘类型验证通过')
        else:
            stylelog.fail('硬盘类型验证失败')
            count += 1
        if i['Model'].replace(' ', '') in data.replace(' ', ''):
            logging.info('硬盘Model验证通过')
        else:
            stylelog.fail('硬盘Model验证失败')
            count += 1
        if i['Revision'] in data:
            logging.info('硬盘Revision验证通过')
        else:
            stylelog.fail('硬盘Revision验证失败')
            count += 1
    if count == 0:
        return True
    else:
        return


def check_network():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.PXE_NETWORK], 10)
    value_list = SetUpLib.get_value_list()
    value_list.remove('NULL')
    url = '/redfish/v1/Chassis/1/NetworkAdapters'
    msg = session.get_msg(url)
    if msg["Members@odata.count"] == len(value_list):
        logging.info('Redfish读取网卡数量与SetUp一致')
        return True
    else:
        stylelog.fail(f'Redfishi读取网卡数量与SetUp不一致，SetUp：{len(value_list)}，RedFish：{msg["Members@odata.count"]}')
        return


def check_pcie():
    os_slot = []
    assert SetUpLib.boot_os_from_bm()
    result = SshLib.execute_command_limit(Sut.OS_SSH, 'dmidecode -t 9')[0].replace('\n', '').replace('\r', '').split(
        'System Slot Information')
    for i in result:
        if re.search('In Use', i):
            os_slot += re.findall('ID: (\d+)', i)
    url = '/redfish/v1/Chassis/1/PCIeDevices?$expand=.'
    msg = session.get_msg(url)
    redfish_slot = []
    for i in msg["Members"]:
        redfish_slot.append(str(i["Oem"]["Public"]["SlotNumber"]))
    if os_slot:
        if all(slot in redfish_slot for slot in os_slot):
            logging.info('PCIE设备Slot号Redfish与OS下一致')
        else:
            stylelog.fail('PCIE设备Slot号Redfish与OS不一致')
            stylelog.fail(f'OS{os_slot}')
            stylelog.fail(f'RedFish{redfish_slot}')
            return
    else:
        logging.info('没有PCIE设备')
        return


def redfish_change_value():
    dict = {
        'BootType': ['UEFIBoot', 'LegacyBoot'],
        'IPVersion': [['Enabled', 'Disabled'], ['Disabled', 'Enabled'], ['Enabled', 'Enabled']],
        'Bootorder': [['HardDiskDrive', 'PXE', 'USBHardDisk', 'USBDVDROMDrive'],
                      ['HardDiskDrive', 'PXE', 'USBDVDROMDrive', 'USBHardDisk'],
                      ['HardDiskDrive', 'USBHardDisk', 'PXE', 'USBDVDROMDrive'],
                      ['HardDiskDrive', 'USBHardDisk', 'USBDVDROMDrive', 'PXE'],
                      ['HardDiskDrive', 'USBDVDROMDrive', 'PXE', 'USBHardDisk'],
                      ['HardDiskDrive', 'USBDVDROMDrive', 'USBHardDisk', 'PXE'],
                      ['PXE', 'HardDiskDrive', 'USBHardDisk', 'USBDVDROMDrive'],
                      ['PXE', 'HardDiskDrive', 'USBDVDROMDrive', 'USBHardDisk'],
                      ['PXE', 'USBHardDisk', 'HardDiskDrive', 'USBDVDROMDrive'],
                      ['PXE', 'USBHardDisk', 'USBDVDROMDrive', 'HardDiskDrive'],
                      ['PXE', 'USBDVDROMDrive', 'HardDiskDrive', 'USBHardDisk'],
                      ['PXE', 'USBDVDROMDrive', 'USBHardDisk', 'HardDiskDrive'],
                      ['USBHardDisk', 'HardDiskDrive', 'PXE', 'USBDVDROMDrive'],
                      ['USBHardDisk', 'HardDiskDrive', 'USBDVDROMDrive', 'PXE'],
                      ['USBHardDisk', 'PXE', 'HardDiskDrive', 'USBDVDROMDrive'],
                      ['USBHardDisk', 'PXE', 'USBDVDROMDrive', 'HardDiskDrive'],
                      ['USBHardDisk', 'USBDVDROMDrive', 'HardDiskDrive', 'PXE'],
                      ['USBHardDisk', 'USBDVDROMDrive', 'PXE', 'HardDiskDrive'],
                      ['USBDVDROMDrive', 'HardDiskDrive', 'PXE', 'USBHardDisk'],
                      ['USBDVDROMDrive', 'HardDiskDrive', 'USBHardDisk', 'PXE'],
                      ['USBDVDROMDrive', 'PXE', 'USBHardDisk', 'HardDiskDrive'],
                      ['USBDVDROMDrive', 'PXE', 'HardDiskDrive', 'USBHardDisk'],
                      ['USBDVDROMDrive', 'USBHardDisk', 'PXE', 'HardDiskDrive'],
                      ['USBDVDROMDrive', 'USBHardDisk', 'HardDiskDrive', 'PXE']],
        'ProcessorHyperThreading': ['Enabled', 'Disabled']
    }
    currect_value = session.get_current_vlaue()
    logging.info(f'当前BIOS值{currect_value}')
    change_value = currect_value
    order = [currect_value['BootTypeOrder0'], currect_value['BootTypeOrder1'], currect_value['BootTypeOrder2'],
             currect_value['BootTypeOrder3']]
    ipversion = [currect_value['IPv4PXESupport'], currect_value['IPv6PXESupport']]
    order_values = dict['Bootorder']
    order_values.remove(order)
    change_order = random.choice(order_values)
    change_value['BootTypeOrder0'] = change_order[0]
    change_value['BootTypeOrder1'] = change_order[1]
    change_value['BootTypeOrder2'] = change_order[2]
    change_value['BootTypeOrder3'] = change_order[3]
    ip_values = dict['IPVersion']
    ip_values.remove(ipversion)
    change_ip = random.choice(ip_values)
    change_value['IPv4PXESupport'] = change_ip[0]
    change_value['IPv6PXESupport'] = change_ip[1]
    for key, value in currect_value.items():
        if key in dict.keys():
            values = dict[key]
            values.remove(value)
            change_value[key] = random.choice(values)
    logging.info(f'修改BIOS值{change_value}')
    result = session.change_bios_value({"Attributes": change_value})
    if result.result == True:
        logging.info('RedFish修改BIOS选项')
    assert SetUpLib.boot_to_setup()
    time.sleep(5)
    changed_value = session.get_current_vlaue()
    if changed_value == change_value:
        logging.info('RedFish 修改BIOS 选项验证成功')
        return True
    else:
        stylelog.fail('RedFish 修改BIOS 选项验证失败')
        stylelog.fail(f'修改的{change_value}')
        stylelog.fail(f'修改后{changed_value}')
        return


def redfish_change_bmc_user():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_USER_CONF, 18)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.ADD_USER], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.ADD_USER], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_1', 20):
        logging.info('用户名设置Root_1成功')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('Redfish@1')
    time.sleep(1)
    SetUpLib.send_data('Redfish@1')
    if SetUpLib.wait_message_enter(SutConfig.Ipm.SET_PSW_SUCCESS, 3):
        logging.info('用户密码设置成功')
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    for i in stdoutput.splitlines():
        if 'Redfish_1' in i:
            userid = i.split(' ')[0]
    if 'Redfish_1' in stdoutput:
        logging.info(' Setup下新增bmc用户后，ipmitool user list中有该用户')
    else:
        stylelog.fail(' Setup下新增bmc用户后，ipmitool user list中没有该用户')
        wrong_msg.append(' Setup下新增bmc用户后，ipmitool user list中没有该用户')
        count += 1
    url = f'/redfish/v1/AccountService/Accounts/{userid}'
    logging.info('SetUp修改用户权限，RedFish验证')
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_1', 20):
        logging.info('输入用户名Redfish_1')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW, 20):
        pass
    else:
        return
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.CALLBACK)
    time.sleep(3)
    result = session.get_msg(url)
    if result['RoleId'] == 'Callback':
        logging.info('SetUp下更改权限为回叫，RedFish返回CALLBACK')
    else:
        stylelog.fail('SetUp下更改权限为回叫，RedFish返回{0}'.format(result['RoleId']))
        wrong_msg.append('SetUp下更改权限为回叫，RedFish返回{0}'.format(result['RoleId']))
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.USER)
    time.sleep(3)

    result = session.get_msg(url)
    if result['RoleId'] == 'User':
        logging.info('SetUp下更改权限为用户，RedFish返回User')
    else:
        stylelog.fail('SetUp下更改权限为用户，RedFish返回{0}'.format(result['RoleId']))
        wrong_msg.append('SetUp下更改权限为用户，RedFish返回{0}'.format(result['RoleId']))
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.OPERATOR)
    time.sleep(3)
    result = session.get_msg(url)
    if result['RoleId'] == 'Operator':
        logging.info('SetUp下更改权限为操作人，RedFish返回Operator')
    else:
        stylelog.fail('SetUp下更改权限为操作人，RedFish返回{0}'.format(result['RoleId']))
        wrong_msg.append('SetUp下更改权限为操作人，RedFish返回{0}'.format(result['RoleId']))
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 7, SutConfig.Ipm.ADMIN)
    time.sleep(3)
    result = session.get_msg(url)
    if result['RoleId'] == 'Administrator':
        logging.info('SetUp下更改权限为管理员，RedFish返回Administrator')
    else:
        stylelog.fail('SetUp下更改权限为管理员，RedFish返回{0}'.format(result['RoleId']))
        wrong_msg.append('SetUp下更改权限为管理员，RedFish返回{0}'.format(result['RoleId']))
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.NO_ACCESS)
    time.sleep(3)
    result = session.get_msg(url)
    if result['RoleId'] == 'NoAccess':
        logging.info('SetUp下更改权限为无法访问，RedFish返回NoAccess')
    else:
        stylelog.fail('SetUp下更改权限为无法访问，RedFish返回{0}'.format(result['RoleId']))
        wrong_msg.append('SetUp下更改权限为无法访问，RedFish返回{0}'.format(result['RoleId']))
        count += 1
    logging.info('SetUp修改用户状态，RedFish验证')
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_STATE], 6, SutConfig.Ipm.DISABLE)
    time.sleep(3)
    result = session.get_msg(url)
    if result["Enabled"] == False:
        logging.info('SetUp下更改状态为Disable，RedFish返回Disable')
    else:
        stylelog.fail('SetUp下更改状态为Disable，RedFish返回{0}'.format(str(result["Enabled"])))
        wrong_msg.append('SetUp下更改状态为Disable，RedFish返回{0}'.format(str(result["Enabled"])))
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_STATE], 6, SutConfig.Ipm.ENABLE)
    time.sleep(3)
    result = session.get_msg(url)
    if result["Enabled"] == True:
        logging.info('SetUp下更改状态为Enable，RedFish返回Enable')
    else:
        stylelog.fail('SetUp下更改状态为Enable，RedFish返回{0}'.format(str(result["Enabled"])))
        wrong_msg.append('SetUp下更改状态为Enable，RedFish返回{0}'.format(str(result["Enabled"])))
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    logging.info('RedFish修改BMC用户账号，密码.......................................')
    path_data = {
        "UserName": 'Redfish_2',
        "Password": 'Redfish@2',
        "RoleId": 'Administrator',
        "Enabled": True,
    }
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
        return
    time.sleep(2)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_1')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Invalid User', 15):
        logging.info('RedFish修改账号，输入之前的账号提示错误')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('RedFish修改账号成功')
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ADMIN, 15):
        logging.info('RedFish修改密码，验证成功')
    else:
        stylelog.fail('RedFish修改密码，验证失败')
        wrong_msg.append('RedFish修改密码，验证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(3)
    logging.info('RedFish 修改用户权限为Operator.....................................')
    path_data['RoleId'] = 'Operator'
    path_data['Password'] = 'Redfish@3'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@3')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.OPERATOR, 15):
        logging.info('RedFish修改用户权限为OPERATOR，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为OPERATOR，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为OPERATOR，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('RedFish 修改用户权限为User.....................................')
    path_data['RoleId'] = 'User'
    path_data['Password'] = 'Redfish@4'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@4')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.USER, 15):
        logging.info('RedFish修改用户权限为USER，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为USER，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为USER，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('RedFish 修改用户权限为NoAccess.....................................')
    path_data['RoleId'] = 'NoAccess'
    path_data['Password'] = 'Redfish@5'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@5')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.NO_ACCESS, 15):
        logging.info('RedFish修改用户权限为NO_ACCESS，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为NO_ACCESS，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为NO_ACCESS，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('RedFish 修改用户权限为Callback.....................................')
    path_data['RoleId'] = 'Callback'
    path_data['Password'] = 'Redfish@6'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@6')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CALLBACK, 15):
        logging.info('RedFish修改用户权限为Callback，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为Callback，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为Callback，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('RedFish 修改用户权限为Administrator.....................................')
    path_data['RoleId'] = 'Administrator'
    path_data['Password'] = 'Redfish@7'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@7')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ADMIN, 15):
        logging.info('RedFish修改用户权限为ADMIN，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为ADMIN，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为ADMIN，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('RedFish 修改用户状态为Enabled.....................................')
    path_data['Enabled'] = True
    path_data['Password'] = 'Redfish@8'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@8')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ENABLE, 15):
        logging.info('RedFish修改用户状态为Enabled，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为Enabled，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为Enabled，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)

    logging.info('RedFish 修改用户状态为Disabled.....................................')
    path_data['Enabled'] = False
    path_data['Password'] = 'Redfish@9'
    if session.patch(url, path_data).result != True:
        stylelog.fail('RedFish 修改失败')
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2', 15):
        logging.info('输入用户名Redfish_2')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@9')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DISABLE, 15):
        logging.info('RedFish修改用户状态为Disabled，SetUp下认证成功')
    else:
        stylelog.fail('RedFish修改用户状态为Disabled，SetUp下认证失败')
        wrong_msg.append('RedFish修改用户状态为Disabled，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.DEL_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.DEL_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish_2')
    time.sleep(1)
    if SetUpLib.wait_message_enter('Redfish_2'):
        pass
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Redfish@9')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DEL_USER_SUCCESS, 15):
        logging.info('删除用户成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def redfish_upgrade_bios_normal(bios_mode, change_part):
    count = 0
    if change_part.lower() == 'all':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        assert Update._change_options_value_part2()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        Update._go_to_setup()
        assert Update._change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        Update._go_to_setup()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    time.sleep(5)
    assert Update._go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    time.sleep(2)
    BmcLib.power_off()
    time.sleep(10)
    if bios_mode.lower() == 'latest':
        assert session.update_bios('normal', SutConfig.Rfs.BIOS_PATH_LATEST)
    elif bios_mode.lower() == 'previous':
        assert session.update_bios('normal', SutConfig.Rfs.BIOS_PATH_PREVIOUS)
    else:
        stylelog.fail('bios_mode有误')
        return
    logging.info('BIOS 更新成功')
    time.sleep(10)
    if Update._go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1
    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        time.sleep(1)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LOCK_OPTION], 5)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('100')
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 18)
        if SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5):
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            time.sleep(1)
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5, 'Enabled')
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.PSW_COMPLEXITY], 5, 'Enabled')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LEN], 5)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('10')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_RETRY], 3)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('6')
        time.sleep(1)
    time.sleep(5)
    #
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.clean_buffer()
    logging.info('刷新后的选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in updated_options]))
    logging.info('刷新前的选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in changed_options]))
    if updated_options == changed_options:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        for i in changed_options:
            if i not in updated_options:
                logging.info('刷新前的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return


def redfish_upgrade_bios_all(bios_mode, change_part):
    count = 0
    num = 0
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    if change_part.lower() == 'all':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        assert Update._change_options_value_part2()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        Update._go_to_setup()
        assert Update._change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        Update._go_to_setup()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(10)
    if bios_mode.lower() == 'latest':
        assert session.update_bios('all', SutConfig.Rfs.BIOS_PATH_LATEST)
    elif bios_mode.lower() == 'previous':
        assert session.update_bios('all', SutConfig.Rfs.BIOS_PATH_PREVIOUS)
    else:
        stylelog.fail('bios_mode有误')
        return
    logging.info('BIOS 更新成功')
    time.sleep(10)
    BmcLib.init_sut()
    time.sleep(200)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if Update._go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        time.sleep(1)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LOCK_OPTION], 5)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('100')
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 18)
        if SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5):
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            time.sleep(1)
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5, 'Enabled')
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.PSW_COMPLEXITY], 5, 'Enabled')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LEN], 5)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('10')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_RETRY], 3)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('6')
        time.sleep(1)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.clean_buffer()
    logging.info('刷新后选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in updated_options]))
    logging.info('默认的选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in default_options]))
    if status == 'always-off' and '<{0}>{1}'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', ''),
            SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>{1}'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', ''),
            SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>{1}'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', ''),
            SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search(
                                                                                    f"{SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')}",
                                                                                    i)]))
        num += 1
    updated_options = [i for i in updated_options if
                       not re.search(f"{SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')}", i)]
    default_options = [i for i in default_options if
                       not re.search(f"{SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')}", i)]

    if updated_options == default_options:
        logging.info('SetUp下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i.replace('<', '[').replace('>', ']')))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return


def redfish_downgrade_bios_normal(bios_mode, change_part):
    count = 0
    if change_part.lower() == 'all':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        assert Update._change_options_value_part2()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        Update._go_to_setup()
        assert Update._change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        Update._go_to_setup()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    time.sleep(5)
    assert Update._go_to_setup()
    changed_options = SetUpLib.get_all_option_value()
    time.sleep(2)
    BmcLib.power_off()
    time.sleep(10)
    if bios_mode.lower() == 'latest':
        assert session.update_bios('normal', SutConfig.Rfs.BIOS_PATH_LATEST)
    elif bios_mode.lower() == 'previous':
        assert session.update_bios('normal', SutConfig.Rfs.BIOS_PATH_PREVIOUS)
    else:
        stylelog.fail('bios_mode有误')
        return
    logging.info('BIOS 更新成功')
    time.sleep(10)
    if Update._go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1
    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        time.sleep(1)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LOCK_OPTION], 5)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('100')
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 18)
        if SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5):
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            time.sleep(1)
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5, 'Enabled')
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.PSW_COMPLEXITY], 5, 'Enabled')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LEN], 5)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('10')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_RETRY], 3)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('6')
        time.sleep(1)
    time.sleep(5)
    #
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.clean_buffer()
    logging.info('刷新后的选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in updated_options]))
    logging.info('刷新前的选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in changed_options]))
    if updated_options == changed_options:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置没有改变')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            return True
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下保留配置刷新，刷新BIOS后配置改变,改变的配置如下')
        for i in updated_options:
            if i not in changed_options:
                logging.info('刷新后的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        for i in changed_options:
            if i not in updated_options:
                logging.info('刷新前的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return


def redfish_downgrade_bios_all(bios_mode, change_part):
    count = 0
    num = 0
    default_options = SutConfig.Upd.DEFAULT_OPTION_VALUE
    if change_part.lower() == 'all':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        assert Update._change_options_value_part2()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'one':
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'two':
        Update._go_to_setup()
        assert Update._change_options_value_part2()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    elif change_part.lower() == 'three':
        Update._go_to_setup()
        assert Update._change_options_value_part3()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    else:
        logging.info('change_part输入有误,默认改变第一部分')
        Update._go_to_setup()
        assert Update._change_options_value_part1()
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(10)
    if bios_mode.lower() == 'latest':
        assert session.update_bios('all', SutConfig.Rfs.BIOS_PATH_LATEST)
    elif bios_mode.lower() == 'previous':
        assert session.update_bios('all', SutConfig.Rfs.BIOS_PATH_PREVIOUS)
    else:
        stylelog.fail('bios_mode有误')
        return
    logging.info('BIOS 更新成功')
    time.sleep(10)
    BmcLib.init_sut()
    time.sleep(200)
    BmcLib.enable_serial_only()
    time.sleep(5)
    if Update._go_to_setup():
        logging.info('刷新BIOS后管理员密码依然存在')
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Msg.PAGE_SECURITY, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        data = SetUpLib.get_data(2)
        if re.search('User Password *Installed', data):
            logging.info('刷新BIOS后用户密码依然存在')
        else:
            stylelog.fail('刷新BIOS后用户密码不存在')
            count += 1

    else:
        stylelog.fail('刷新BIOS后管理员密码不存在')
        count += 1
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    stdoutput = str(stdoutput).replace("'", '')
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
    updated_options = SetUpLib.get_all_option_value()
    if '[60]PasswordLockTime' in updated_options:
        assert SetUpLib.back_to_setup_toppage()
        assert SetUpLib.boot_to_page(SutConfig.Psw.SET_ADMIN_PSW)
        time.sleep(1)
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LOCK_OPTION], 5)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('100')
        time.sleep(1)
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Psw.SET_TIME_MONTH, 18)
        if SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5):
            time.sleep(1)
            SetUpLib.send_key(Key.UP)
            time.sleep(1)
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.CHECK_PSW], 5, 'Enabled')
            SetUpLib.change_option_value(Key.DOWN, [SutConfig.Psw.PSW_COMPLEXITY], 5, 'Enabled')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_LEN], 5)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('10')
            SetUpLib.locate_option(Key.DOWN, [SutConfig.Psw.PSW_RETRY], 3)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data_enter('6')
        time.sleep(1)
    time.sleep(4)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(3)
    BmcLib.enable_serial_only()
    SetUpLib.clean_buffer()
    logging.info('刷新后选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in updated_options]))
    logging.info('默认的选项值{0}'.format([i.replace('<', '[').replace('>', ']') for i in default_options]))
    if status == 'always-off' and '<{0}>{1}'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[0].replace(' ', ''),
            SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'previous' and '<{0}>{1}'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[1].replace(' ', ''),
            SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    elif status == 'always-on' and '<{0}>{1}'.format(
            SutConfig.Upd.POWER_LOSS_VALUES[2].replace(' ', ''),
            SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')) in updated_options:
        logging.info('刷新BIOS后，电源丢失策略与BMC保持一致')
    else:
        stylelog.fail('刷新BIOS后，电源丢失策略和BMC不一致,BMC：{0}，SetUp：{1}'.format(status, [i for i in updated_options if
                                                                                re.search(
                                                                                    f"{SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')}",
                                                                                    i)]))
        num += 1
    updated_options = [i for i in updated_options if
                       not re.search(f"{SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')}", i)]
    default_options = [i for i in default_options if
                       not re.search(f"{SutConfig.Upd.POWER_LOSS_OPTION.replace(' ', '')}", i)]

    if updated_options == default_options:
        logging.info('SetUp下完全刷新，刷新BIOS后选项变为默认值')
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
                return True
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
                return
        else:
            stylelog.fail('刷新BIOS后密码不存在')
            return
    else:
        logging.info('SetUp下完全刷新，刷新BIOS后选项没有变为默认值，改变的配置如下')
        for i in updated_options:
            if i not in default_options:
                logging.info('刷新后选项{0}'.format(i.replace('<', '[').replace('>', ']')))

        for i in default_options:
            if i not in updated_options:
                logging.info('默认的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
        if count == 0:
            logging.info('刷新BIOS后密码依然存在')
            if num == 0:
                logging.info('刷新BIOS后电源丢失策略与BMC一致')
            else:
                stylelog.fail('刷新BIOS后电源丢失策略与BMC不一致')
        else:
            stylelog.fail('刷新BIOS后密码不存在')
        return


def redfish_change_setup_verify():
    count = 0
    path = 'Hygon7500CRB\\Tools\\1.json'
    testscope = session.load(path)
    num = []
    for key in testscope:
        values = session.supported_value(key)
        if not isinstance(values[0], int):
            num.append(len(values))
    for i in range(0, max(num)):
        for key in testscope:
            values = session.supported_value(key)
            if isinstance(values[0], int):
                desired_value = random.choice(values)
                testscope[key] = desired_value
            else:
                if i < len(values):
                    testscope[key] = values[i]
                else:
                    testscope[key] = random.choice(values)
        # print(testscope)
        with open(path, 'w') as fp:
            json.dump(testscope, fp, indent=1)
        time.sleep(1)
        session.add_dependence(path)
        time.sleep(1)
        session.verify_testcase(path, remove=True)
        time.sleep(1)
        result = session.change_bios_value(session.load(path))
        if result.status == 200:
            logging.info('RedFish修改option，value成功')
        else:
            stylelog.fail('RedFish修改option，value失败')
            count += 1
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        setup_option = SetUpLib.get_all_option_value()
        changed_option = session.load(path)
        logging.debug(changed_option)
        logging.debug(setup_option)
        for key, value in changed_option.items():
            if any(re.search(f"(?:<|\[){str(value).replace(' ', '')}(?:>|\]){key.replace(' ', '')}", i) for i in
                   setup_option):
                logging.debug(f'RedFish修改{key}<{value}>,SetUp验证通过')

            else:
                stylelog.fail((f'RedFish修改{key}<{value}>,SetUp验证失败'))
                count += 1
    if count == 0:
        return True
    else:
        return


def setup_change_redfish_verify():
    count = 0
    for i in SutConfig.Rfs.CHANGE_OPTIONS:
        logging.info('-' * 30)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, i, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(10)
        assert SetUpLib.boot_to_setup()
        redfish_option = session.get_current_vlaue()
        logging.debug(redfish_option)
        logging.debug(i)
        for option in i:
            if isinstance(option, dict):
                if list(option.keys())[0].replace('\\', '') in redfish_option.keys():
                    if redfish_option[list(option.keys())[0]] == list(option.values())[0]:
                        logging.debug(f"SetUp修改{list(option.keys())[0]}<{list(option.values())[0]}>,RedFish验证成功")
                    else:
                        stylelog.fail(f"SetUp修改{list(option.keys())[0]}<{list(option.values())[0]}>,RedFish验证失败")
                        count += 1
                else:
                    stylelog.fail(
                        f"SetUp修改{list(option.keys())[0]}<{list(option.values())[0]}>,RedFish没有{list(option.keys())[0]}")
                    count += 1
    if count == 0:
        return True
    else:
        return
