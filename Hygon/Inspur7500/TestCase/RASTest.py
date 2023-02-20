# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
RAS  case  编号:1001~1050
'''


def get_eth_bdf():
    onboard_bdf = {}
    result = SshLib.execute_command_limit(Sut.OS_SSH, 'lspci | grep -i eth')[0]
    for i in result.split('\n'):
        if re.search('wangxun|8088', i, re.I):
            onboard_bdf[re.findall('(\w{2}:\w{2}.\w+) ', i)[0][:6]] = []
            break

    bdfs = re.findall('(\w{2}:\w{2}.\w+) ', result)
    for key in list(onboard_bdf.keys()):
        onboard_bdf[key] = [i for i in bdfs if key in i]
    bdfs = [i for i in bdfs if list(onboard_bdf.keys())[0][:6] not in i]
    add_bdfs = {}
    for i in bdfs:
        if i[:5] not in add_bdfs.keys():
            add_bdfs[i[:5]] = []
    for key in list(add_bdfs.keys()):
        add_bdfs[key] = [i for i in bdfs if key in i]
    return onboard_bdf, add_bdfs


def get_sel_num(output, msg):
    sel = []
    for i in output.split('\n'):
        if re.search(msg, i):
            num = re.findall(' *([0-9a-z]+) \| \w+/\w+/\w+', i)[0]
            sel.append(str(int(f'0x{num}', 16)))
    return sel


def get_bdf(sel):
    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel get {sel}')
    event_data = re.findall('Event Data .*: (\w+)', output)[0]
    data2 = event_data[2:4]
    data3 = event_data[4:6]
    bus = data2
    device = int('{:08b}'.format(int(data3, 16))[0:-3], 2)
    device = '{:02d}'.format(device)
    function = int('{:08b}'.format(int(data3, 16))[-3:], 2)
    return f'{bus}:{device}.{function}'


def get_data3(sel):
    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel get {sel}')
    event_data = re.findall('Event Data.*: (\w+)', output)[0]
    data3 = event_data[4:6] if event_data[4:6] else ''
    return data3


def is_bdf_support_acs(bdf):
    result = SshLib.execute_command_limit(Sut.OS_SSH, f'lspci -xxvvs {bdf} | grep "Access Control Services"')[0]
    if result != '':
        return True
    else:
        return False


@core.test_case(('1001', '[TC1001]内存各类型错误上报BMC', '内存各类型错误上报BMC'))
def mem_ras_001(oem=False):
    """
    Name:   内存各类型错误上报BMC

    Steps:  1.SetUp下内存错误数量设为10
            2.系统下单比特注入10次，查看BCM上报结果，
            3.内核打印错误后，'reboot'命令重启，查看BMC上报情况
            4.系统下多比特注入10次，查看BMC上报结果，
            5.单比特注入2次，查看BMC上报结果
            6.多比特注入2次，查看BMC上报结果
            7.重新启动到系统，UCE注入，查看BMC上报结果
            8.SetUp下内存错误数量设为1
            9.系统下单比特注入1次，3次，查看BMC上报结果
            10.系统下多比特注入1次，2次，查看BMC上报结果
            11.SetUp下内存错误数量设为0
            12.系统下UCE注入，查看BMC上报结果

    Result: 2.BMC上报一次
            3.BMC不上报
            4.BMC上报一次
            5/6.BMC不上报
            7.BMC上报'不可纠正错误'
            9.BMC上报1次，3次
            10.BMC上报1次，2次
            12.BMC上报'不可纠正错误'
    """
    try:
        count = 0
        wrong_msg = []
        logging.info(f"{'-' * 25}错误数量为10测试{'-' * 25}")
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_10, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        if re.search('CPU Not Authed', SshLib.execute_command_limit(Sut.OS_SSH, './HygonSecureAuthTool -c')[0], re.I):
            SshLib.execute_command_limit(Sut.OS_SSH, './HygonSecureAuthTool -u -d AuthSToken')

        # 单比特注入.....................................
        logging.info('单比特注入....................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 10')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info('错误数量设置为10,单比特注入10次，BMC上报一次')
        else:
            stylelog.fail('错误数量设置为10,单比特注入10次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为10,单比特注入10次，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        time.sleep(1)
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        start = time.time()
        while True:
            if SshLib.execute_command_limit(Sut.OS_SSH, "dmesg | grep -i 'Memory Controller'")[0] != '':
                break
            time.sleep(2)
            now = time.time()
            if now - start > 400:
                break
        time.sleep(2)
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0:
            logging.info('错误数量设置为10,单比特注入10次，重启后，BMC没有上报')
        else:
            stylelog.fail('错误数量设置为10,单比特注入10次，重启后，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为10,单比特注入10次，重启的后，BMC上报')
            wrong_msg.append(output)
            count += 1
        # 多比特注入............................................
        logging.info('多比特注入........................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 10')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info('错误数量设置为10,多比特注入10次，BMC上报一次')
        else:
            stylelog.fail('错误数量设置为10,多比特注入10次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为10,多比特注入10次，BMC上报有误')
            wrong_msg.append(output)
            count += 1

        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 2')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0:
            logging.info('错误数量设置为10,单比特注入2次，BMC没有上报')
        else:
            stylelog.fail('错误数量设置为10,单比特注入2次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为10,单比特注入2次，BMC上报')
            wrong_msg.append(output)
            count += 1
        time.sleep(1)
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 2')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0:
            logging.info('错误数量设置为10,多比特注入2次，BMC没有上报')
        else:
            stylelog.fail('错误数量设置为10,多比特注入2次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为10,单比特注入2次，BMC上报')
            wrong_msg.append(output)
            count += 1

        # UCE注入....................................................
        logging.info('UCE注入..............................')
        assert SetUpLib.boot_os_from_bm()
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 8 ./inject_mem.sh 1 0x2ff00 2 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable ECC') != 0:
            logging.info('错误数量设置为10,UCE注入，BMC上报')
        else:
            stylelog.fail('错误数量设置为10,UCE注入，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为10,UCE注入，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        logging.info(f"{'-' * 25}错误数量为1测试{'-' * 25}")
        if oem is True:
            BmcLib.change_bios_value(['PFEH:Enabled','MCACount:1'])
        else:
            assert SetUpLib.boot_to_setup()
            time.sleep(2)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_1, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        # 单比特注入......................................................
        logging.info('单比特注入....................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info('错误数量设置为1,单比特注入1次，BMC上报一次')
        else:
            stylelog.fail('错误数量设置为1,单比特注入1次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为1,单比特注入1次，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        time.sleep(1)
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 3')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 3:
            logging.info('错误数量设置为1,单比特注入3次，BMC上报3次')
        else:
            stylelog.fail('错误数量设置为1,单比特注入3次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为1,单比特注入3次，BMC上报有误')
            wrong_msg.append(output)
            count += 1

        # 多比特注入......................................................
        logging.info('多比特注入....................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info('错误数量设置为1,多比特注入1次，BMC上报一次')
        else:
            stylelog.fail('错误数量设置为1,多比特注入1次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为1,多比特注入1次，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        time.sleep(1)
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 2')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 2:
            logging.info('错误数量设置为1,多比特注入2次，BMC上报2次')
        else:
            stylelog.fail('错误数量设置为1,多比特注入2次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为1,多比特注入2次，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        # 错误数量设置为0，UCE注入上报测试
        if oem is True:
            BmcLib.change_bios_value(['PFEH:Enabled','MCACount:0'])
        else:
            assert SetUpLib.boot_to_setup()
            time.sleep(1)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_0, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        logging.info('UCE注入..............................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 8 ./inject_mem.sh 1 0x4ff00 2 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable ECC') != 0:
            logging.info('错误数量设置为0,UCE注入，BMC上报')
        else:
            stylelog.fail('错误数量设置为0,UCE注入，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为0,UCE注入，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1002', '[TC1002]内存可纠正错误不上报BMC', '内存可纠正错误不上报BMC'))
def mem_ras_002(oem=False):
    """
    Name:   内存可纠正错误不上报BMC

    Steps:  1.SetUp下内存错误数量设为0
            2.系统下单比特注入5次，查看BMC上报结果
            3.系统下多比特注入5次，查看BMC上报结果
            4.系统下重启后，查看BMC上报结果

    Result: 2/3/4:  BMC不上报
    """
    try:
        count = 0
        wrong_msg = []
        if oem is True:
            BmcLib.change_bios_value(['PFEH:Enabled','MCACount:0'])
        else:
            assert SetUpLib.boot_to_setup()
            time.sleep(1)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_0, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        logging.info('单比特注入...........................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 5')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('错误数量设置为0,单比特注入5次，没有上报')
        else:
            stylelog.fail('错误数量设置为0,单比特注入5次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为0,单比特注入5次，BMC上报')
            wrong_msg.append(output)
            count += 1
        logging.info('多比特注入...........................')
        time.sleep(1)
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 5')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('错误数量设置为0,多比特注入5次，没有上报')
        else:
            stylelog.fail('错误数量设置为0,多比特注入5次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为0,多比特注入5次，BMC上报')
            wrong_msg.append(output)
            count += 1
        time.sleep(1)
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0:
            logging.info('错误数量设置为0,注错重启后，没有上报')
        else:
            stylelog.fail('错误数量设置为0,注错重启后，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('错误数量设置为0,注错重启后，BMC上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1003', '[TC1003]内存各类型错误不上报BMC', '内存各类型错误不上报BMC'))
def mem_ras_003(oem=False):
    """
    Name:   内存各类型错误不上报BMC

    Steps:  1.SetUp下设置内存错误数量为1，关闭错误管理
            2.系统下单比特注入2次，查看BMC上报结果
            3.系统下多比特注入2次，查看BMC上报结果
            4.系统下UCE注入，查看BMC上报结果

    Result: 2/3/4.BMC不上报
    """
    try:
        count = 0
        wrong_msg = []
        if oem is True:
            BmcLib.change_bios_value(['PFEH:Disabled','MCACount:1'])
        else:
            assert SetUpLib.boot_to_setup()
            time.sleep(1)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_1, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.CLOSE_PFEH, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        logging.info('单比特注入...........................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 2')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭,单比特注入2次，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭,单比特注入2次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭,单比特注入2次，BMC上报')
            wrong_msg.append(output)
            count += 1
        logging.info('多比特注入...........................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 3')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭,多比特注入3次，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭,多比特注入3次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭,多比特注入3次，BMC上报')
            wrong_msg.append(output)
            count += 1
        logging.info('UCE注入..............................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 8 ./inject_mem.sh 1 0x2ff00 2 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭,UCE注入，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭,UCE注入，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭,UCE注入，BMC上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1004', '[TC1004]内存关闭PFEH，错误错误数量设为0测试', '内存关闭PFEH，错误错误数量设为0测试'))
def mem_ras_004(oem=False):
    """
    Name:   错误数量设为0，关闭错误管理

    Steps:  1.SetUp内存错误数量设为0，关闭错误管理
            2.系统下单比特注入2次，多比特注入3次，UCE注入，查看BMC上报结果
            3.系统下重启后，查看BMC上报结果

    Result: 2/3.BMC不上报

    """
    try:
        count = 0
        wrong_msg = []
        if oem is True:
            BmcLib.change_bios_value(['PFEH:Disabled','MCACount:0'])
        else:
            assert SetUpLib.boot_to_setup()
            time.sleep(1)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_0, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.CLOSE_PFEH, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        logging.info('单比特注入...........................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 2')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭，错误数量设为0,单比特注入2次，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭，错误数量设为0,单比特注入2次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭，错误数量设为0,单比特注入2次，BMC上报')
            wrong_msg.append(output)
            count += 1
        logging.info('多比特注入...........................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 3')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭，错误数量设为0,多比特注入3次，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭，错误数量设为0,多比特注入3次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭，错误数量设为0,多比特注入3次，BMC上报')
            wrong_msg.append(output)
            count += 1
        logging.info('UCE注入..............................')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, 'timeout 8 ./inject_mem.sh 1 0x2ff00 2 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable ECC') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭，错误数量设为0,UCE注入，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭，错误数量设为0,UCE注入，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭，错误数量设为0,UCE注入，BMC上报')
            wrong_msg.append(output)
            count += 1
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable ECC') == 0 and output.count('Correctable ECC') == 0:
            logging.info('PFEH关闭，错误数量设为0,注入后重启，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭，错误数量设为0,注入后重启，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭，错误数量设为0,注入后重启，BMC上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1005', '[TC1005]内存漏斗测试', '内存漏斗测试'))
def mem_ras_005():
    """
    Name:   内存漏斗测试

    Steps:  1.SetUp下设置内存错误数量为10，漏斗时间为1分钟，漏斗数量为5
            2.进入系统注错10次(初始时间为注错10次后的时间)
            3.等待30秒,注错10次,查看BMC上报结果(初始时间更新为注错10次后的时间,与step2的初始时间相差了大约30+10*5=80秒,80秒小于2分钟,期望结果会上报)
            4.等待80秒,注错5次后,接着再注错5次,查看BMC上报结果(初始时间更新为第二个5次注完的时间,与step3的初始时间相差了大约80+5*5+5*5=130秒,130秒大于2分钟,期望结果不会上报)
            5.SetUp下设置内存错误数量为10，漏斗时间为2分钟，漏斗数量为12
            6.进入系统注错10次(初始时间为注错10次后的时间)
            7.等待30秒,注错10次,查看BMC上报结果(初始时间更新为注错10次后的时间,与step6的初始时间相差了大约30+10*5=80秒,80秒小于2分钟,期望结果会上报)
            8.等待80秒,注错5次后,接着再注错5次,查看BMC上报结果(初始时间更新为第二个5次注完的时间,与step7的初始时间相差了大约80+5*5+5*5=130秒,130秒大于2分钟,期望结果不会上报)
            9.SetUp下设置内存错误数量为100，漏斗时间为5分钟，漏斗数量为50
            10.进入系统注错100次(初始时间为注错100次后的时间)
            11.等待0秒,注错100次,查看BMC上报结果(初始时间更新为注错100次后的时间,与step10的初始时间相差了大约0+100*5=500秒,500秒小于10分钟,期望结果会上报)
            12.等待110秒,注错50次后,接着再注错50次,查看BMC上报结果(初始时间更新为第二个50次注完的时间,与step10的初始时间相差了大约110+50*5+50*5=610秒,610秒大于10分钟,期望结果不会上报)

    Result: 3.BMC上报
            4.BMC不上报
            7.BMC上报
            8.BMC不上报
            11.BMC上报
            12.BMC不上报
    """
    try:
        def get_sleep_time(mca_count=10, leaky_time=2, leaky_count=5, spent_time=60, over_time=True):
            minute = mca_count // leaky_count if mca_count % leaky_count == 0 else mca_count // leaky_count + 1
            second = minute * leaky_time  # 临界值,超过该值会触发漏斗机制
            spent_time = int(spent_time)  # 注错所花费的时间
            if over_time:
                sleep_time = second - spent_time + mca_count + 10
                sleep_time = sleep_time if sleep_time > 0 else 0
            else:
                if spent_time > leaky_time:
                    sleep_time = 0
                else:
                    sleep_time = second - spent_time - 30 if second - spent_time > 30 else 0
            return sleep_time, second

        wrong_msg = []
        count = 0
        change_list = [SutConfig.Ras.SET_LEAKY_BUCKET_1, SutConfig.Ras.SET_LEAKY_BUCKET_2,
                       SutConfig.Ras.SET_LEAKY_BUCKET_3]
        for index, change_option in enumerate(change_list):
            mca_count = int(list(change_option[0].values())[0])  # 例如:10
            leaky_time = list(change_option[1].values())[0]  # 例如:1
            leaky_count = list(change_option[2].values())[0]  # 例如:5
            logging.info(f'-----------内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}测试---------------------')
            assert SetUpLib.boot_to_setup()
            time.sleep(1)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.OPEN_PFEH, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, change_option, 18, save=True)
            assert SetUpLib.boot_os_from_bm()
            logging.info(f'注错{mca_count}次')
            now = time.time()
            SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_mem.sh 1 0x3ff00 1 {mca_count}')
            start = time.time()
            spent_time = int(start - now)  # 注错10次花费的时间
            logging.info('初始时间更新')
            origin_time = start  # 进入系统，注错10次后的时间为初始时间
            logging.info(f'等待{get_sleep_time(mca_count, leaky_time, leaky_count, spent_time, False)[0]}秒')
            time.sleep(get_sleep_time(mca_count, leaky_time, leaky_count, spent_time, False)[0])
            BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
            SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_mem.sh 1 0x3ff00 1 {mca_count}')
            end = time.time()  # 再次注错10次后的时间，此时初始时间更新为当前时间
            logging.info('初始时间更新')
            origin_time = end  # 注错10次后，初始时间更新
            ce_time = get_sleep_time(mca_count, leaky_time, leaky_count, spent_time, False)[1]  # 触发机制的临界时间 120s
            if end - start < ce_time:  # 两次初始时间更新的时间差,差值在两分钟之内,会上报BMC

                time.sleep(5)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('Correctable ECC') == 1:
                    logging.info(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差小于{int(ce_time)}秒，BMC上报')
                else:
                    stylelog.fail(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差小于{int(ce_time)}秒，BMC没有上报')
                    stylelog.fail(output)
                    wrong_msg.append(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差小于{int(ce_time)}秒，BMC没有上报')
                    wrong_msg.append(output)
                    count += 1
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
            else:  # 两次初始时间更新的时间差,差值大于两分钟,不会上报BMC
                time.sleep(5)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
                    logging.info(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差大于{int(ce_time)}秒，BMC没有上报')
                else:
                    stylelog.fail(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差大于{int(ce_time)}秒，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差大于{int(ce_time)}秒，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
            logging.info(f'等待{get_sleep_time(mca_count, leaky_time, leaky_count, spent_time, True)[0]}秒')
            time.sleep(get_sleep_time(mca_count, leaky_time, leaky_count, spent_time, True)[0])
            SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_mem.sh 1 0x3ff00 1 {int(mca_count / 2)}')
            time.sleep(2)
            SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_mem.sh 1 0x3ff00 1 {math.ceil(mca_count / 2)}')
            end = time.time()
            logging.info('初始时间更新')
            if end - origin_time > ce_time:  # 两次初始时间更新的时间差,差值大于两分钟,不会上报BMC
                time.sleep(5)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('Correctable ECC') == 0 and len(output.split('\n')) == 2:
                    logging.info(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差大于{int(ce_time)}秒，BMC没有上报')
                else:
                    stylelog.fail(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差大于{int(ce_time)}秒，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差大于{int(ce_time)}秒，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
            else:
                time.sleep(5)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('Correctable ECC') == 1:
                    logging.info(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差小于{int(ce_time)}秒，BMC上报')
                else:
                    stylelog.fail(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差小于{int(ce_time)}秒，BMC没有上报')
                    stylelog.fail(output)
                    wrong_msg.append(
                        f'内存错误数量:{mca_count},漏斗时间:{leaky_time},漏斗数量:{leaky_count}，时间差小于{int(ce_time)}秒，BMC没有上报')
                    wrong_msg.append(output)
                    count += 1
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')

        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1006', '[TC1006]内存漏斗设为0测试', '内存漏斗设为0测试'))
def mem_ras_006():
    """
        Name:   内存漏斗设为0测试

        Steps:  1.SetUp下设置内存错误数量为10，漏斗时间为1，漏斗数量为5,再将漏斗时间设为0
                2.进入系统,注错10次，查看BMC上报结果
                3.等待2分钟后注错10次，查看BMC上报结果


        Result: 2/3.BMC上报一次
        """
    try:
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.OPEN_PFEH, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_LEAKY_BUCKET_1, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_LEAKY_BUCKET_0, 18, save=True)
        assert SetUpLib.boot_os_from_bm()
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 10')
        time.sleep(5)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info('漏斗数量设为0,注错10次，BMC上报1次')
        else:
            stylelog.fail('漏斗数量设为0,注错10次，BMC没有上报')
            return
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        time.sleep(120)
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 1 10')
        time.sleep(5)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info('漏斗数量设为0,2分钟后注错10次，BMC上报1次')
        else:
            stylelog.fail('漏斗数量设为0,2分钟后注错10次，BMC没有上报')
            return
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1007', '[TC1007]内存持续注入测试', '内存持续注入测试'))
def mem_ras_007():
    """
    Name:   内存持续注入测试

    Steps:  1.SetUp设置内存错误数量为10
            2.系统下对指定内存持续注入错误
            3.查看BMC是否上报，内存丝印是否上报准确

    Result: 3.BMC上报且丝印正确

    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_10, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        du_list = []
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        type = 'old' if SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh -h | grep "5 parameter"')[
            0] else 'new'
        S_cmd = './DramErrorInjector_v1.6 -S' if type == 'old' else './DramErrorInjector -S'
        data = SshLib.execute_command_limit(Sut.OS_SSH, f'{S_cmd}')[0]
        time.sleep(2)
        for i in re.findall('Die : (\w+) \| UMC : (\w+) \x1B\[0;32m\[Detected\]\x1B\[0m', data):
            du_list.append(i[0] + ' ' + i[1])
        all_mem_list = \
            SshLib.execute_command_limit(Sut.OS_SSH, "dmidecode -t 17 | grep -i 'Total Width'")[
                0].splitlines()
        if type == 'new':
            for key, value in SutConfig.Ras.RAS_DICT.items():
                if value[0][0:3] in du_list:
                    BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                    die, umc, dimm = value[0].split(' ')
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_mem.sh 1 {die} {umc} {int(dimm) + 1} 0 10')
                    time.sleep(5)
                    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                    sel = get_sel_num(output, 'Correctable ECC')
                    if sel:
                        event_data = get_data3(random.choice(sel))
                        if re.search('Unknown', all_mem_list[value[1]]):
                            all_event_data = []
                            for m, n in SutConfig.Ras.RAS_DICT.items():
                                if n[0][0:3] == value[0][0:3]:
                                    all_event_data.append(m)
                            if event_data in all_event_data:
                                logging.info(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC上报,且内存丝印上报正确')
                            else:
                                stylelog.fail(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC上报,内存丝印上报错误')
                                wrong_msg.append(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC上报,内存丝印上报错误')
                                count += 1
                        else:
                            if event_data == key:
                                logging.info(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC上报,且内存丝印上报正确')
                            else:
                                stylelog.fail(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC上报,内存丝印上报错误')
                                wrong_msg.append(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC上报,内存丝印上报错误')
                                count += 1
                    else:
                        stylelog.fail(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC没有上报')
                        stylelog.fail(output)
                        wrong_msg.append(f'内存持续注入die:{die},umc:{umc},dimm:{dimm},BMC没有上报')
                        wrong_msg.append(output)
                        count += 1
                    time.sleep(2)
                    if value[1] % 2 != 0:
                        assert SetUpLib.boot_os_from_bm()
        else:
            for key, value in SutConfig.Ras.RAS_DICT.items():
                if value[0][0:3] in du_list and value[1] % 2 != 0:
                    die, umc, dimm = value[0].split(' ')
                    BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                    SshLib.execute_command_limit(Sut.OS_SSH,
                                                 f'timeout 20 ./inject_mem.sh 1 {die} {umc} 0 1')
                    time.sleep(5)
                    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                    sel = get_sel_num(output, 'Correctable ECC')
                    if sel:
                        if get_data3(random.choice(sel)) == key:
                            logging.info(f'内存持续注入die:{die},umc:{umc},BMC上报,且内存丝印上报正确')
                        else:
                            stylelog.fail(f'内存持续注入die:{die},umc:{umc},BMC上报,内存丝印上报错误')
                            count += 1
                    else:
                        stylelog.fail(f'内存持续注入die:{die},umc:{umc},BMC没有上报')
                        stylelog.fail(output)
                        wrong_msg.append(f'内存持续注入die:{die},umc:{umc},BMC没有上报')
                        wrong_msg.append(output)
                        count += 1
                    time.sleep(2)
                    assert SetUpLib.boot_os_from_bm()
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1008', '[TC1008]内存错误数量设为最大值测试', '内存错误数量设为最大值测试'))
def mem_ras_008():
    """
    Name:   内存错误数量最大值测试

    Steps:  1.SetUp内存错误数量设为最大值，漏斗时间设为最大值
            2.系统下注错4090次，查看BMC上报结果
            3.在注错5次，查看BMC上报结果
            4.在注错5次，查看BMC上报结果

    Result: 2.BMC不上报
            3/4.BMC上报一次
    """
    try:
        max_count = 4095
        count = 0
        logging.info(f"{'-' * 25}错误数量为最大值{max_count}测试{'-' * 25}")
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_MEM_THRESHOLD_MAX, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        for i in range(0, (max_count - 5) // 10):
            logging.info(f'第{i * 10}次注入')
            SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 10')
            time.sleep(2)
        if (max_count - 5) % 10 != 0:
            SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_mem.sh 1 0x3ff00 0 {(max_count - 5) % 10}')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 0:
            logging.info(f'错误数量设为{max_count},注错{max_count - 5}次后，没有上报错误')
        else:
            stylelog.fail(f'错误数量设为{max_count},注错{max_count - 5}次后，BMC上报错误')
            stylelog.fail(output)
            count += 1
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 5')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info(output)
            logging.info(f'错误数量设置为{max_count},单比特注入{max_count}次，BMC上报一次')
        else:
            stylelog.fail(f'错误数量设置为{max_count},单比特注入{max_count}次，BMC上报有误')
            stylelog.fail(output)
            count += 1
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_mem.sh 1 0x3ff00 0 5')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable ECC') == 1:
            logging.info(output)
            logging.info(f'错误数量设为{max_count},注错{max_count + 5}次后，上报一次错误')
        else:
            stylelog.fail(f'错误数量设置为{max_count},单比特注入{max_count + 5}次，BMC上报有误')
            stylelog.fail(output)
            count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1011', '[TC1011]PCIE各类型错误上报BMC', 'PCIE各类型错误上报BMC'))
def pcie_ras_001():
    """
    Name:   PCIE各类型错误上报BMC

    Steps:  遍历板载网卡和外插网卡
            1.SetUp下设置PCIE阈值为2
            2.系统下lcrc_tx注入2次，查看BMC上报结果
            3.系统下lcrc_rx注入2次，查看BMC上报结果
            4.系统下ecrc_tx注入，查看BMC上报结果
            5.系统下ecrc_rx注入，查看BMC上报结果
            6.系统下acs_fatal注入，查看BMC上报结果
            7.系统下acs_nofatal注入，查看BMC上报结果
            8.SetUp下设置PCIE阈值为0
            9.系统下ecrc_tx注入，查看BMC上报结果
            10.系统下ecrc_rx注入，查看BMC上报结果
            11.系统下acs_fatal注入，查看BMC上报结果
            12.系统下acs_nofatal注入，查看BMC上报结果
            13.SetUp下设置PCIE阈值为1
            14.系统下lcrc_tx注入1次，查看BMC上报结果
            15.系统下lcrc_rx注入1次，查看BMC上报结果

    Result: 2.BMC上报2次且BDF号正确
            3.BMC上报1次且BDF号正确
            4/5/6.BMC上报且BDF号正确，机器重启
            7.BMC上报且BDF号正确
            9/10/11.BMC上报且BDF号正确，机器重启
            12.BMC上报且BDF号正确
            14.BMC上报2次且BDF号正确
            15.BMC上报1次且BDF号正确

    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_2, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        onboard_bdf, add_bdfs = get_eth_bdf()
        if onboard_bdf == {} and add_bdfs == {}:
            stylelog.fail('板载网卡，外插网卡都没识别到')
            return
        if onboard_bdf:
            logging.info('板载网卡注错测试...................')
            onboard_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in onboard_bdf.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        onboard_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = onboard_bdf[m]
                        break
            for key, value in onboard_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1 * len(value):
                    logging.info('PCIE CE阈值为2,lcrc_tx注入2次，BMC上报2次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        bdfs = []
                        for i in sel:
                            bdf = get_bdf(i)
                            bdfs.append(bdf)
                        if sorted(bdfs) == sorted(value) or all(i in value for i in bdfs):
                            logging.info(f'BDF:{bdfs},上报正确')
                        else:
                            stylelog.fail(f'BDF:{bdfs},上报有误')
                            wrong_msg.append(f'BDF:{bdfs},上报有误')
                            count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,lcrc_tx注入2次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,lcrc_tx注入2次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1:
                    logging.info('PCIE CE阈值为2,lcrc_rx注入2次，BMC上报1次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,lcrc_rx注入2次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,lcrc_rx注入2次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为2,ecrc_tx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if bdf in value:
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,ecrc_tx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,ecrc_tx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为2,ecrc_rx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,ecrc_rx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,ecrc_rx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_fatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                sign = is_bdf_support_acs(value[0])
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为2,acs_fatal注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为2,acs_fatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为2,acs_fatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0:
                    logging.info('PCIE CE阈值为2,acs_nofatal注入，BMC上报')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为2,acs_nofatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为2,acs_nofatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_to_setup()
                time.sleep(1)
                SetUpLib.send_keys(Key.CONTROL_F11)
                assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_0, 18,save=True)
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为0,ecrc_tx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if bdf in value:
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为0,ecrc_tx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,ecrc_tx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为0,ecrc_rx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为0,ecrc_rx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,ecrc_rx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_fatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:

                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为0,acs_fatal注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为0,acs_fatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为0,acs_fatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0:
                    logging.info('PCIE CE阈值为0,acs_nofatal注入，BMC上报')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为0,acs_nofatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为0,acs_nofatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
        if add_bdfs:
            logging.info('外插网卡注错测试')
            assert SetUpLib.boot_to_setup()
            time.sleep(1)
            SetUpLib.send_keys(Key.CONTROL_F11)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_2, 18,save=True)
            assert SetUpLib.boot_os_from_bm()
            add_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in add_bdfs.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        add_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = add_bdfs[m]
                        break
            for key, value in add_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1 * len(value):
                    logging.info('PCIE CE阈值为2,lcrc_tx注入2次，BMC上报2次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        bdfs = []
                        for i in sel:
                            bdf = get_bdf(i)
                            bdfs.append(bdf)
                        if sorted(bdfs) == sorted(value) or all(i in value for i in bdfs):
                            logging.info(f'BDF:{bdfs},上报正确')
                        else:
                            stylelog.fail(f'BDF:{bdfs},上报有误')
                            wrong_msg.append(f'BDF:{bdfs},上报有误')
                            count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,lcrc_tx注入2次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,lcrc_tx注入2次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1:
                    logging.info('PCIE CE阈值为2,lcrc_rx注入2次，BMC上报1次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,lcrc_rx注入2次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,lcrc_rx注入2次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为2,ecrc_tx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if bdf in value:
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,ecrc_tx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,ecrc_tx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为2,ecrc_rx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为2,ecrc_rx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为2,ecrc_rx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                sign = is_bdf_support_acs(value[0])
                logging.info('acs_fatal注入............................')

                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为2,acs_fatal注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为2,acs_fatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为2,acs_fatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0:
                    logging.info('PCIE CE阈值为2,acs_nofatal注入，BMC上报')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为2,acs_nofatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为2,acs_nofatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_to_setup()
                time.sleep(1)
                SetUpLib.send_keys(Key.CONTROL_F11)
                assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_0, 18,save=True)
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为0,ecrc_tx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if bdf in value:
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为0,ecrc_tx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,ecrc_tx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为0,ecrc_rx注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为0,ecrc_rx注入，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,ecrc_rx注入，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_fatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0 and re.search('System Restart', output):
                    logging.info('PCIE CE阈值为0,acs_fatal注入，BMC上报，且重启')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为0,acs_fatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为0,acs_fatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:

                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 1 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') != 0:
                    logging.info('PCIE CE阈值为0,acs_nofatal注入，BMC上报')
                    sel = get_sel_num(output, 'PCI SERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PCIE CE阈值为0,acs_nofatal注入，BMC上报有误')
                        stylelog.fail(output)
                        wrong_msg.append('PCIE CE阈值为0,acs_nofatal注入，BMC上报有误')
                        wrong_msg.append(output)
                        count += 1
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_1, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        onboard_bdf, add_bdfs = get_eth_bdf()
        if onboard_bdf == {} and add_bdfs == {}:
            stylelog.fail('板载网卡，外插网卡都没识别到')
            return
        if onboard_bdf:
            logging.info('板载网卡注错测试...................')
            onboard_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in onboard_bdf.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        onboard_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = onboard_bdf[m]
                        break
            for key, value in onboard_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 1 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1 * len(value):
                    logging.info('PCIE CE阈值为1,lcrc_tx注入1次，BMC上报2次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        bdfs = []
                        for i in sel:
                            bdf = get_bdf(i)
                            bdfs.append(bdf)
                        if sorted(bdfs) == sorted(value) or all(i in value for i in bdfs):
                            logging.info(f'BDF:{bdfs},上报正确')
                        else:
                            stylelog.fail(f'BDF:{bdfs},上报有误')
                            wrong_msg.append(f'BDF:{bdfs},上报有误')
                            count += 1
                else:
                    stylelog.fail('PCIE CE阈值为1,lcrc_tx注入1次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为1,lcrc_tx注入1次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 1 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1:
                    logging.info('PCIE CE阈值为1,lcrc_rx注入1次，BMC上报1次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为1,lcrc_rx注入1次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为1,lcrc_rx注入1次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
        if add_bdfs:
            logging.info('外插网卡注错测试')
            add_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in add_bdfs.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        add_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = add_bdfs[m]
                        break
            for key, value in add_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 1 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1 * len(value):
                    logging.info('PCIE CE阈值为1,lcrc_tx注入1次，BMC上报1次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        bdfs = []
                        for i in sel:
                            bdf = get_bdf(i)
                            bdfs.append(bdf)
                        if sorted(bdfs) == sorted(value) or all(i in value for i in bdfs):
                            logging.info(f'BDF:{bdfs},上报正确')
                        else:
                            stylelog.fail(f'BDF:{bdfs},上报有误')
                            wrong_msg.append(f'BDF:{bdfs},上报有误')
                            count += 1
                else:
                    stylelog.fail('PCIE CE阈值为1,lcrc_tx注入1次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为1,lcrc_tx注入1次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 1 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1:
                    logging.info('PCIE CE阈值为1,lcrc_rx注入1次，BMC上报1次')
                    sel = get_sel_num(output, 'PCI PERR')
                    if sel:
                        for i in sel:
                            bdf = get_bdf(i)
                            if re.search(bdf, key, re.I):
                                logging.info(f'BDF:{bdf},上报正确')
                            else:
                                stylelog.fail(f'BDF:{bdf},上报有误')
                                wrong_msg.append(f'BDF:{bdf},上报有误')
                                count += 1
                else:
                    stylelog.fail('PCIE CE阈值为1,lcrc_rx注入1次，BMC上报有误')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为1,lcrc_rx注入1次，BMC上报有误')
                    wrong_msg.append(output)
                    count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1012', '[TC1012]PCIE可纠正错误不上报BMC', 'PCIE可纠正错误不上报BMC'))
def pcie_ras_002():
    """
    Name:   PCIE可纠正错误不上报BMC

    Steps:  遍历板载网卡和外插网卡
            1.SetUp下设置PCIE阈值为0
            2.系统下lcrc_tx注入2次，查看BMC上报结果
            3.系统下lcrc_rx注入2次，查看BMC上报结果
            4.系统下重启，查看BMC上报结果

    Result: 2/3/4.BMC不上报

    """

    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_0, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        onboard_bdf, add_bdfs = get_eth_bdf()
        if onboard_bdf == {} and add_bdfs == {}:
            stylelog.fail('板载网卡，外插网卡都没识别到')
            return
        if onboard_bdf:
            logging.info('板载网卡注错测试...................')
            onboard_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in onboard_bdf.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        onboard_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = onboard_bdf[m]
                        break
            for key, value in onboard_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PCIE CE阈值为0,lcrc_tx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PCIE CE阈值为0,lcrc_tx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,lcrc_tx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PCIE CE阈值为0,lcrc_rx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PCIE CE阈值为0,lcrc_rx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,lcrc_rx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
        if add_bdfs:
            logging.info('外插网卡注错测试')
            add_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in add_bdfs.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        add_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = add_bdfs[m]
                        break
            for key, value in add_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PCIE CE阈值为0,lcrc_tx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PCIE CE阈值为0,lcrc_tx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,lcrc_tx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PCIE CE阈值为0,lcrc_rx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PCIE CE阈值为0,lcrc_rx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PCIE CE阈值为0,lcrc_rx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
        time.sleep(1)
        SshLib.execute_command_limit(Sut.OS_SSH, 'reboot')
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('PCI PERR') == 0:
            logging.info('PCIE CE阈值为0,注错后重启，BMC没有上报')
        else:
            stylelog.fail('PCIE CE阈值为0,注错后重启，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PCIE CE阈值为0,注错后重启，BMC上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1013', '[TC1013]PCIE各类型错误不上报BMC', 'PCIE各类型错误不上报BMC'))
def pcie_ras_003(oem=False):
    """
    Name:   PCIE各类型错误不上报BMC

    Steps:  遍历板载网卡和外插网卡
            1.SetUp下设置PCIE阈值为2，关闭 错误管理
            2.系统下lcrc_tx注入2次，查看BMC上报结果
            3.系统下lcrc_rx注入2次，查看BMC上报结果
            4.系统下ecrc_tx注入，查看BMC上报结果
            5.系统下ecrc_rx注入，查看BMC上报结果
            6.系统下acs_fatal注入，查看BMC上报结果
            7.系统下acs_nofatal注入，查看BMC上报结果

    Result: 2/3/4/5/6/7.BMC没有上报,机器不重启

    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(1)
        if oem is True:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_2, 18,save=True)
            BmcLib.change_bios_value(['PFEH:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_2, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.CLOSE_PFEH, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        onboard_bdf, add_bdfs = get_eth_bdf()
        if onboard_bdf == {} and add_bdfs == {}:
            stylelog.fail('板载网卡，外插网卡都没识别到')
            return
        if onboard_bdf:
            logging.info('板载网卡注错测试...................')
            onboard_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in onboard_bdf.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        onboard_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = onboard_bdf[m]
                        break
            for key, value in onboard_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('关闭PFEH,lcrc_tx注入2次，BMC没有上报')
                else:
                    stylelog.fail('关闭PFEH,lcrc_tx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,lcrc_tx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('关闭PFEH,lcrc_rx注入2次，BMC没有上报')
                else:
                    stylelog.fail('关闭PFEH,lcrc_rx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,lcrc_rx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('关闭PFEH,ecrc_tx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('关闭PFEH,ecrc_tx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,ecrc_tx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('关闭PFEH,ecrc_rx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('关闭PFEH,ecrc_rx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,ecrc_rx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_fatal注入............................')
                sign = is_bdf_support_acs(value[0])
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:

                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('关闭PFEH,acs_fatal注入，BMC没有上报，没有重启')
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('关闭PFEH,acs_fatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('关闭PFEH,acs_fatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:

                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('关闭PFEH,acs_nofatal注入，BMC没有上报')
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('关闭PFEH,acs_nofatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('关闭PFEH,acs_nofatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
        if add_bdfs:
            logging.info('外插网卡注错测试')
            add_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in add_bdfs.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        add_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = add_bdfs[m]
            for key, value in add_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('关闭PFEH,lcrc_tx注入2次，BMC没有上报')
                else:
                    stylelog.fail('关闭PFEH,lcrc_tx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,lcrc_tx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('关闭PFEH,lcrc_rx注入2次，BMC没有上报')
                else:
                    stylelog.fail('关闭PFEH,lcrc_rx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,lcrc_rx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('关闭PFEH,ecrc_tx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('关闭PFEH,ecrc_tx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,ecrc_tx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('关闭PFEH,ecrc_rx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('关闭PFEH,ecrc_rx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('关闭PFEH,ecrc_rx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_fatal注入............................')
                sign = is_bdf_support_acs(value[0])

                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('关闭PFEH,acs_fatal注入，BMC没有上报，没有重启')
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('关闭PFEH,acs_fatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('关闭PFEH,acs_fatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
                assert SetUpLib.boot_os_from_bm()
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('关闭PFEH,acs_nofatal注入，BMC没有上报')
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('关闭PFEH,acs_nofatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('关闭PFEH,acs_nofatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1

        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1014', '[TC1014]PCIE关闭PFEH，错误错误数量设为0测试', 'PCIE关闭PFEH，错误错误数量设为0测试'))
def pcie_ras_004(oem=False):
    """
    Name:   CPIE阈值设为0，关闭错误管理

    Steps:  遍历板载网卡和外插网卡
            1.SetUp下设置PCIE阈值为0，关闭错误管理
            2.系统下lcrc_tx注入2次，查看BMC上报结果
            3.系统下lcrc_rx注入2次，查看BMC上报结果
            4.系统下ecrc_tx注入，查看BMC上报结果
            5.系统下ecrc_rx注入，查看BMC上报结果
            6.系统下acs_fatal注入，查看BMC上报结果
            7.系统下acs_nofatal注入，查看BMC上报结果

    Result: 2/3/4/5/6/7.BMC没有上报,机器不重启
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        time.sleep(1)
        if oem is True:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_0, 18,save=True)
            BmcLib.change_bios_value(['PFEH:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_0, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.CLOSE_PFEH, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        onboard_bdf, add_bdfs = get_eth_bdf()
        if onboard_bdf == {} and add_bdfs == {}:
            stylelog.fail('板载网卡，外插网卡都没识别到')
            return
        if onboard_bdf:
            logging.info('板载网卡注错测试...................')
            onboard_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in onboard_bdf.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        onboard_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = onboard_bdf[m]
                        break
            for key, value in onboard_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PFEH关闭，错误数量设为0,lcrc_tx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,lcrc_tx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,lcrc_tx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PFEH关闭，错误数量设为0,lcrc_rx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,lcrc_rx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,lcrc_rx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('PFEH关闭，错误数量设为0,ecrc_tx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,ecrc_tx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,ecrc_tx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                time.sleep(1)
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1

                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('PFEH关闭，错误数量设为0,ecrc_rx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,ecrc_rx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,ecrc_rx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1

                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('acs_fatal注入............................')
                sign = is_bdf_support_acs(value[0])
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:

                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('PFEH关闭，错误数量设为0,acs_fatal注入，BMC没有上报，没有重启')
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PFEH关闭，错误数量设为0,acs_fatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('PFEH关闭，错误数量设为0,acs_fatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:

                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PFEH关闭，错误数量设为0,acs_nofatal注入，BMC没有上报')
                else:
                    if sign == False:
                        logging.info(f'{onboard_bdf}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PFEH关闭，错误数量设为0,acs_nofatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('PFEH关闭，错误数量设为0,acs_nofatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
        if add_bdfs:
            logging.info('外插网卡注错测试')
            add_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in add_bdfs.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        add_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = add_bdfs[m]
            for key, value in add_arg.items():
                logging.info('lcrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_tx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PFEH关闭，错误数量设为0,lcrc_tx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,lcrc_tx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,lcrc_tx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 2 1')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PFEH关闭，错误数量设为0,lcrc_rx注入2次，BMC没有上报')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,lcrc_rx注入2次，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,lcrc_rx注入2次，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_tx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_tx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('PFEH关闭，错误数量设为0,ecrc_tx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,ecrc_tx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,ecrc_tx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('ecrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh ecrc_rx {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('PFEH关闭，错误数量设为0,ecrc_rx注入，BMC没有上报，没有重启')
                else:
                    stylelog.fail('PFEH关闭，错误数量设为0,ecrc_rx注入，BMC上报')
                    stylelog.fail(output)
                    wrong_msg.append('PFEH关闭，错误数量设为0,ecrc_rx注入，BMC上报')
                    wrong_msg.append(output)
                    count += 1
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('acs_fatal注入............................')
                sign = is_bdf_support_acs(value[0])

                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_fatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and not re.search('System Restart', output):
                    logging.info('PFEH关闭，错误数量设为0,acs_fatal注入，BMC没有上报，没有重启')
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PFEH关闭，错误数量设为0,acs_fatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('PFEH关闭，错误数量设为0,acs_fatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
                logging.info('acs_nofatal注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh acs_nonfatal {key} 1 2 1', 5)
                except:
                    pass
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and len(output.split('\n')) == 2:
                    logging.info('PFEH关闭，错误数量设为0,acs_nofatal注入，BMC没有上报')
                else:
                    if sign == False:
                        logging.info(f'{value[0]}不支持acs服务，需手动验证')
                    else:
                        stylelog.fail('PFEH关闭，错误数量设为0,acs_nofatal注入，BMC上报')
                        stylelog.fail(output)
                        wrong_msg.append('PFEH关闭，错误数量设为0,acs_nofatal注入，BMC上报')
                        wrong_msg.append(output)
                        count += 1
                try:
                    SshLib.execute_command_limit(Sut.OS_SSH, 'reboot', 5)
                except:
                    pass

                if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                      SutConfig.Msg.POST_MESSAGE):
                    logging.info('重启失败，后续测试结果可能不准确')
                    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                     SutConfig.Msg.POST_MESSAGE)
                if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
                    return
                if not BmcLib.ping_sut():
                    return
                time.sleep(20)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI SERR') == 0 and output.count('PCI PERR') == 0:
                    logging.info('注错后重启，BMC没有上报错误')
                else:
                    stylelog.fail('注错后重启，BMC上报错误')
                    stylelog.fail(output)
                    wrong_msg.append('注错后重启，BMC上报错误')
                    wrong_msg.append(output)
                    count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1015', '[TC1015]PCIE错误数量最大值测试', 'PCIE错误数量最大值测试'))
def pcie_ras_005():
    """
    Name:   PCIE错误数量最大值测试

    Steps:  1.SetUp下设置PCIE阈值为最大值
            2.系统下lcrc_rx注错9990,查看BMC上报结果
            3.系统下再注错10次,查看BMC上报结果
            4.系统下在注错10次，查看BMC上报结果

    Result: 2.BMC没有上报
            3/4.BMC上报一次
    """

    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_PCIE_THRESHOLD_MAX, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        onboard_bdf, add_bdfs = get_eth_bdf()
        if onboard_bdf == {} and add_bdfs == {}:
            stylelog.fail('板载网卡，外插网卡都没识别到')
            return
        if onboard_bdf:
            logging.info('板载网卡注错测试...................')
            onboard_arg = {}
            result = SshLib.execute_command_limit(Sut.OS_SSH, './rastest gpp')[0].split('\n')
            for m in onboard_bdf.keys():
                for i in range(0, len(result)):
                    if re.search(m, result[i]):
                        onboard_arg[re.findall('(\w+:\w+.\w+)', result[i - 1])[0]] = onboard_bdf[m]
                        break
            for key, value in onboard_arg.items():
                logging.info('lcrc_rx注入............................')
                BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                for n in range(1, 1000):
                    logging.info(f'第{n * 10}次注入')
                    SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 10 1')
                    time.sleep(1)
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 0:
                    logging.info(f'PCIE CE阈值为最大值,lcrc_rx注入9990次，BMC没有上报')
                    logging.info(output)
                else:
                    BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
                    stylelog.fail(f'PCIE CE阈值为最大值,lcrc_rx注入9990次，BMC上报')
                    stylelog.fail(output)
                    count += 1
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 10 1')
                logging.info(f'第10000次注入')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1:
                    logging.info(f'PCIE CE阈值为最大值,lcrc_rx注入10000次，BMC上报1次')
                    logging.info(output)
                else:
                    stylelog.fail(f'PCIE CE阈值为最大值,lcrc_rx注入10000次，BMC上报有误')
                    stylelog.fail(output)
                    count += 1
                SshLib.execute_command_limit(Sut.OS_SSH, f'./inject_pcie.sh lcrc_rx {key} 1 10 1')
                logging.info(f'第10010次注入')
                time.sleep(10)
                output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
                if output.count('PCI PERR') == 1:
                    logging.info(f'PCIE CE阈值为最大值,lcrc_rx注入10010次，BMC上报1次')
                    logging.info(output)
                else:
                    stylelog.fail(f'PCIE CE阈值为最大值,lcrc_rx注入10010次，BMC上报有误')
                    stylelog.fail(output)
                    count += 1
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1021', '[TC1021]CPU各类型错误上报BMC', 'CPU各类型错误上报BMC'))
def cpu_ras_001():
    """
    Name:   CPU各类型错误上报BMC

    Steps:  1.SetUp下设置CPU阈值为10
            2.系统下可纠正错误注入9次，查看BMC上报结果
            3.系统下可纠正错误注入10次，查看BMC上报结果
            4.系统下fatal注入，查看BMC上报结果
            5.系统下nonfatal注入，查看BMC上报结果

    Result: 2.BMC不上报
            3.BMC上报一次
            4/5.BMC上报
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_CPU_THRESHOLD_10, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        logging.info('可纠正错误注入')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 1 9 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable machine check error') == 0 and len(output.split('\n')) == 2:
            logging.info('CPU错误数量设置为10,可纠正错误注入9次，BMC没有上报')
        else:
            stylelog.fail('CPU错误数量设置为10,可纠正错误注入9次，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('CPU错误数量设置为10,可纠正错误注入9次，BMC上报')
            wrong_msg.append(output)
            count += 1
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 1 1 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable machine check error') == 1:
            logging.info('CPU错误数量设置为10,可纠正错误注入10次，BMC上报一次')
        else:
            stylelog.fail('CPU错误数量设置为10,可纠正错误注入10次，BMC上报有误')
            stylelog.fail(output)
            wrong_msg.append('CPU错误数量设置为10,可纠正错误注入10次，BMC上报有误')
            wrong_msg.append(output)
            count += 1
        logging.info('不可纠正错误注入')
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        try:
            SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 2 1 1', 5)
        except:
            pass
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable machine check exception') != 0:
            logging.info('CPU错误数量设置为10,注入不可纠正错误nonfatal，BMC上报')
        else:
            stylelog.fail('CPU错误数量设置为10,注入不可纠正错误nonfatal，BMC没有上报')
            stylelog.fail(output)
            wrong_msg.append('CPU错误数量设置为10,注入不可纠正错误nonfatal，BMC没有上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        try:
            SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 4 1 1', 5)
        except:
            pass
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable machine check exception') != 0:
            logging.info('CPU错误数量设置为10,注入不可纠正错误fatal，BMC上报')
        else:
            stylelog.fail('CPU错误数量设置为10,注入不可纠正错误fatal，BMC没有上报')
            stylelog.fail(output)
            wrong_msg.append('CPU错误数量设置为10,注入不可纠正错误fatal，BMC没有上报')
            wrong_msg.append(output)
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1022', '[TC1022]CPU各类型错误不上报BMC', 'CPU各类型错误不上报BMC'))
def cpu_ras_002(oem=False):
    """
    Name:   CPU各类型错误不上报BMC

    Steps:  1.SetUp下设置CPU阈值为1，关闭错误管理
            2.系统下注入可纠正错误，查看BMC上报结果
            3.系统下fatal注入，查看BMC上报结果
            4.系统下nonfatal注入，查看BMC上报结果

    Result: 2/3/4.BMC不上报

    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        if oem is True:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_CPU_THRESHOLD_1, 18,save=True)
            BmcLib.change_bios_value(['PFEH:Disabled'])
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_CPU_THRESHOLD_1, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.CLOSE_PFEH, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 1 10 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable machine check error') == 0 and len(output.split('\n')) == 2:
            logging.info('PFEH关闭,注入可纠正错误，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭,注入可纠正错误，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭,注入可纠正错误，BMC上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        try:
            SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 2 1 1', 5)
        except:
            pass
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable machine check exception') == 0:
            logging.info('PFEH关闭,注入不可纠正错误nonfatal，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭,注入不可纠正错误nonfatal，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭,注入不可纠正错误nonfatal，BMC上报')
            wrong_msg.append(output)
            count += 1
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        try:
            SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 4 1 1', 5)
        except:
            pass
        if not SetUpLib.boot_with_hotkey_only(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE):
            logging.info('重启失败，后续测试结果可能不准确')
            assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 200, SutConfig.Msg.POST_MESSAGE)
        if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.LINUX_OS, 30, ''):
            return
        if not BmcLib.ping_sut():
            return
        time.sleep(20)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Uncorrectable machine check exception') == 0:
            logging.info('PFEH关闭,注入不可纠正错误fatal，BMC没有上报')
        else:
            stylelog.fail('PFEH关闭,注入不可纠正错误fatal，BMC上报')
            stylelog.fail(output)
            wrong_msg.append('PFEH关闭,注入不可纠正错误fatal，BMC上报')
            wrong_msg.append(output)
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('1023', '[TC1023]CPU错误数量最大值测试', 'CPU错误数量最大值测试'))
def cpu_ras_003():
    """
    Name:   CPU错误数量最大值测试

    Steps:  1.SetUp下设置CPU阈值为最大值
            2.系统下注错4094次，查看BMC上报结果
            3.系统下再注错1次，查看BMC上报结果

    Result: 2.BMC没有上报
            3.BMC上报一次
    """
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.CONTROL_F11)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ras.SET_CPU_THRESHOLD_MAX, 18,save=True)
        assert SetUpLib.boot_os_from_bm()
        BmcLib.interaction(f'{SutConfig.Env.IPMITOOL} sel clear', 'Clearing SEL')
        for i in range(0, 409):
            SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 1 10 1')
            time.sleep(1)
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 1 4 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable machine check error') == 0 and len(output.split('\n')) == 2:
            logging.info('CPU错误数量设为4095，注错4094次后，BMC没有上报错误')
        else:
            stylelog.fail('CPU错误数量设为4095，注错4094次后，BMC上报错误')
            stylelog.fail(output)
            wrong_msg.append('CPU错误数量设为4095，注错4094次后，BMC上报错误')
            wrong_msg.append(output)
            count += 1
        SshLib.execute_command_limit(Sut.OS_SSH, './inject_cpu.sh 1 1 1')
        time.sleep(10)
        output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sel list')
        if output.count('Correctable machine check error') == 1:
            logging.info('CPU错误数量设为4095，注错4095次后，BMC上报一次')
        else:
            stylelog.fail('CPU错误数量设为4095，注错4095次后，BMC没有上报错误')
            stylelog.fail(output)
            wrong_msg.append('CPU错误数量设为4095，注错4095次后，BMC没有上报错误')
            wrong_msg.append(output)
            count += 1
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
