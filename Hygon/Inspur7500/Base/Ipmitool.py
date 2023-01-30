# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *


def frb2_watchdog(oem):
    password = 'Admin@' + str(random.randint(1, 100)) + str(random.randint(1, 100))
    arg = '{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    count = 0
    wrong_msg = []
    logging.info('FRB2 Watchdog禁用，POST测试..................................')
    if oem is True:
        BmcLib.change_bios_value(['FRB2:Disabled'])
        BmcLib.init_sut()
    else:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.CLOSE_FRB, 18, save=True)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.boot_with_hotkey_only(Key.DEL,SutConfig.Msg.PAGE_MAIN,50):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('FRB2定时器禁用，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器禁用，ipmitool与setup不一致,{0}{1}{2}'.format(status, action, times))
        wrong_msg.append('FRB2定时器禁用，ipmitool与setup不一致,{0}{1}{2}'.format(status, action, times))
        count += 1
    logging.info('FRB2 Watchdog开启，POST测试..................................')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_FRB1, 18, save=True)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 50):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()

    if status == 'Started/Running' and action == 'Hard Reset' and times == '600':
        logging.info('FRB2定时器启用，重启，10分钟，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器启用，重启，10分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('FRB2定时器启用，重启，10分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_FRB2, 18, save=True)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 50):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()
    if status == 'Started/Running' and action == 'Power Down' and times == '1800':
        logging.info('FRB2定时器启用，关闭电源，30分钟，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器启用，关闭电源，30分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('FRB2定时器启用，关闭电源，30分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_FRB3, 18, save=True)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    SetUpLib.send_key(Key.DEL)
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 50):
        logging.info('进入setup')
    else:
        assert SetUpLib.boot_to_setup()
    if status == 'Started/Running' and action == 'Hard Reset' and times == '300':
        logging.info('FRB2定时器启用，重启，5分钟，ipmitool与setup一致')
    else:
        stylelog.fail('FRB2定时器启用，重启，5分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('FRB2定时器启用，重启，5分钟，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1
    logging.info('FRB2 Watchdog禁用，F12网络启动测试..................................')
    assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Ipm.BOTH_PXE_MSG, 300, SutConfig.Msg.HOTKEY_PROMPT_F12)
    time.sleep(2)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('F12进入网络启动，自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('F12进入网络启动，没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('F12进入网络启动，没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        count += 1
    logging.info('FRB2 Watchdog禁用，IPM命令修改 PXE UEFI 启动一次..................................')
    BmcLib.output(SutConfig.Env.UEFI_PXE_ONCE)
    logging.info('IPMITOOL 修改UEFI PXE启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.UEFI_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改UEFI PXE启动一次，成功启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改UEFI PXE启动一次，没有启动到PXE')
            return
    else:
        return
    time.sleep(2)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('IPM UEFI PXE 启动，自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('IPM UEFI PXE 启动，没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('IPM UEFI PXE 启动，没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        count += 1
    logging.info('FRB2 Watchdog禁用，IPM命令修改 PXE Legacy 启动一次..................................')
    BmcLib.output(SutConfig.Env.LEGACY_PXE_ONCE)
    logging.info('IPMITOOL 修改Legacy PXE启动一次')
    time.sleep(2)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        if SetUpLib.wait_message(SutConfig.Ipm.LEGACY_PXE_MSG, 50, readline=False):
            logging.info('IPMITOOL 修改Legacy PXE启动一次，成功启动到PXE')
        else:
            stylelog.fail('IPMITOOL 修改Legacy PXE启动一次，没有启动到PXE')
            return
    else:
        return
    time.sleep(2)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('IPM Legacy PXE 启动，自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('IPM Legacy PXE 启动，没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('IPM Legacy PXE 启动，没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        count += 1
    SetUpPassword._go_to_setup(is_del=True)
    logging.info('FRB2 Watchdog禁用，BIOS密码测试..................................')
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 5)
    assert PwdLib.set_admin(password, True)
    SetUpLib.send_keys(Key.SAVE_RESET)
    if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
    SetUpLib.send_key(Key.DEL)
    if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 50):
        assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, 300, SutConfig.Msg.POST_MESSAGE)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('设置BIOS密码后，POST界面自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('设置BIOS密码后，POST界面没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('设置BIOS密码后，POST界面没有自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        count += 1
    SetUpLib.send_data_enter(password)
    if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 30):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Psw.LOC_ADMIN_PSW, 18)
    assert PwdLib.del_admin(password, True)
    BmcLib.power_cycle()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    logging.info('FRB2 Watchdog禁用，硬盘密码测试..................................')
    assert SetUpLib.locate_menu(Key.DOWN,
                                SutConfig.Psw.LOC_HDD_PSW + [HDDPassword.HDD_NAME_01, SutConfig.Psw.SET_HDD_PSW_OPTION],
                                10)
    assert PwdLib.set_hdd_admin('hdd@12345', True)
    BmcLib.init_sut()
    if not SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        BmcLib.enable_serial_normal()
        assert SetUpLib.wait_message(SutConfig.Psw.LOGIN_HDD_PSW_PROMPT)
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('设置硬盘密码后，硬盘密码输入界面自动禁用FRB2 Watchdog')
    else:
        stylelog.fail('设置硬盘密码后，硬盘密码输入界面自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('设置硬盘密码后，硬盘密码输入界面自动禁用FRB2 Watchdog,{0},{1},{2}'.format(status, action, times))
        count += 1
    assert PwdLib.check_psw_post('hdd@12345', '')
    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        stdoutput = BmcLib.output(arg)
        status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
        action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
        times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
        if status == 'Started/Running' and action == 'Hard Reset' and times == '300':
            logging.info('输入硬盘密码后,FRB2定时器启用，重启，5分钟，')
        else:
            stylelog.fail('输入硬盘密码后,FRB2定时器没有启用，{},{},{}'.format(status, action, times))
            wrong_msg.append('输入硬盘密码后,FRB2定时器没有启用，{},{},{}'.format(status, action, times))
            count += 1
        SetUpLib.send_key(Key.DEL)
    else:
        return
    if SetUpLib.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 50):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.locate_menu(Key.DOWN,
                                SutConfig.Psw.LOC_HDD_PSW + [HDDPassword.HDD_NAME_01, SutConfig.Psw.DEL_HDD_PSW_OPTION],
                                16)
    assert PwdLib.del_hdd_psw('hdd@12345', True)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def os_watchdog():
    count = 0
    wrong_msg = []
    arg = '{0} mc watchdog get'.format(SutConfig.Env.IPMITOOL)
    logging.info('OS Watchdog启用测试..................................')
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_OS_WDOG1, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Started/Running' and action == 'Power Down' and times == '600':
        logging.info('系统定时器启用，关闭电源，10分钟，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器启用，关闭电源，10分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('系统定时器启用，关闭电源，10分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1

    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_OS_WDOG2, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Started/Running' and action == 'Hard Reset' and times == '1800':
        logging.info('系统定时器启用，重启，30分钟，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器启用，重启，30分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('系统定时器启用，重启，30分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1
    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_OS_WDOG3, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Started/Running' and action == 'Hard Reset' and times == '300':
        logging.info('系统定时器启用，重启，5分钟，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器启用，重启，5分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('系统定时器启用，重启，5分钟，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1

    assert SetUpLib.boot_to_setup()
    time.sleep(1)
    SetUpLib.send_keys(Key.CONTROL_F11)
    time.sleep(2)
    logging.info('OS Watchdog禁用测试..................................')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.CLOSE_OS_WDOG, 18, save=True)
    assert SetUpLib.boot_os_from_bm()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Watchdog Timer Is: +([a-zA-Z/]+)', stdoutput)[0]
    action = re.findall(r'Watchdog Timer Actions: +(.*) \(', stdoutput)[0]
    times = re.findall(r'Initial Countdown: +(.*?) sec', stdoutput)[0]
    if status == 'Stopped' and action == 'No action' and times == '0':
        logging.info('系统定时器禁用，进入系统后，ipmitool与setup一致')
    else:
        stylelog.fail('系统定时器禁用，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        wrong_msg.append('系统定时器禁用，进入系统后，ipmitool与setup不一致,{0},{1},{2}'.format(status, action, times))
        count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def power_loss():
    count = 0
    wrong_msg = []
    arg = '{0} chassis  status | findstr "Restore Policy"'.format(SutConfig.Env.IPMITOOL)
    logging.info('Setup修改，BMC验证.....................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.SET_POWER_LOSS1, 18, save=True)
    assert SetUpLib.boot_to_setup()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
    if status == 'always-on':
        logging.info('setup下修改电源丢失策略为上电，BMC为上电，一致')
    else:
        stylelog.fail('setup下修改电源丢失策略为上电，BMC为{0}，不一致'.format(status))
        wrong_msg.append('setup下修改电源丢失策略为上电，BMC为{0}，不一致'.format(status))
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.SET_POWER_LOSS2, 18, save=True)
    assert SetUpLib.boot_to_setup()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]
    if status == 'previous':
        logging.info('setup下修改电源丢失策略为上次状态，BMC为上次状态，一致')
    else:
        stylelog.fail('setup下修改电源丢失策略为上次状态，BMC为{0}，一致'.format(status))
        wrong_msg.append('setup下修改电源丢失策略为上次状态，BMC为{0}，一致'.format(status))
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.SET_POWER_LOSS3, 18, save=True)
    assert SetUpLib.boot_to_setup()
    stdoutput = BmcLib.output(arg)
    status = re.findall(r'Power Restore Policy : ([a-zA-Z\-]+)', stdoutput)[0]

    if status == 'always-off':
        logging.info('setup下修改电源丢失策略为保持关闭，BMC为保持关闭，一致')
    else:
        stylelog.fail('setup下修改电源丢失策略为保持关闭，BMC为{0}，一致'.format(status))
        wrong_msg.append('setup下修改电源丢失策略为保持关闭，BMC为{0}，一致'.format(status))
        count += 1
    logging.info('BMC修改，SetUp验证.....................................')
    BmcLib.output('{0} chassis policy always-on'.format(SutConfig.Env.IPMITOOL))
    logging.info('BMC修改电源策略为上电')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_SERVICE, 18)
    data = SetUpLib.get_data(3)
    if re.search(r'{0} *{1}'.format(SutConfig.Ipm.POWER_LOSS_VALUE[0], SutConfig.Ipm.POWER_LOSS_OPTION), data):
        logging.info('BMC修改电源策略为上电，Setup下为上电，一致')
    else:
        stylelog.fail('BMC修改电源策略为上电，Setup下为{0}，不一致'.format(
            re.findall(r'Mgmt *<(.+)> *{}'.format(SutConfig.Ipm.POWER_LOSS_OPTION), data)))
        wrong_msg.append('BMC修改电源策略为上电，Setup下为{0}，不一致'.format(
            re.findall(r'Mgmt *<(.+)> *{}'.format(SutConfig.Ipm.POWER_LOSS_OPTION), data)))
        count += 1
    BmcLib.output('{0} chassis policy previous'.format(SutConfig.Env.IPMITOOL))
    logging.info('BMC修改电源策略为上次状态')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_SERVICE, 18)
    data = SetUpLib.get_data(3)

    if re.search(r'{0} *{1}'.format(SutConfig.Ipm.POWER_LOSS_VALUE[1], SutConfig.Ipm.POWER_LOSS_OPTION), data):
        logging.info('BMC修改电源策略为上次状态，Setup下为上次状态，一致')
    else:
        stylelog.fail('BMC修改电源策略为上次状态，Setup下为{0}，不一致'.format(
            re.findall(r'Mgmt *<(.+)> *{}'.format(SutConfig.Ipm.POWER_LOSS_OPTION), data)))
        wrong_msg.append('BMC修改电源策略为上次状态，Setup下为{0}，不一致'.format(
            re.findall(r'Mgmt *<(.+)> *{}'.format(SutConfig.Ipm.POWER_LOSS_OPTION), data)))
        count += 1
    BmcLib.output('{0} chassis policy always-off'.format(SutConfig.Env.IPMITOOL))
    logging.info('BMC修改电源策略为保持关闭')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_SERVICE, 18)
    data = SetUpLib.get_data(3)
    if re.search(r'{0} *{1}'.format(SutConfig.Ipm.POWER_LOSS_VALUE[2], SutConfig.Ipm.POWER_LOSS_OPTION), data):
        logging.info('BMC修改电源策略为保持关闭，Setup下为保持关闭，一致')
    else:
        stylelog.fail('BMC修改电源策略为上次保持关闭，Setup下为{0}，不一致'.format(
            re.findall(r'Mgmt *<(.+)> *{}'.format(SutConfig.Ipm.POWER_LOSS_OPTION), data)))
        wrong_msg.append('BMC修改电源策略为上次保持关闭，Setup下为{0}，不一致'.format(
            re.findall(r'Mgmt *<(.+)> *{}'.format(SutConfig.Ipm.POWER_LOSS_OPTION), data)))
        count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def oem():
    count = 0
    wrong_msg = []
    change_option = SutConfig.Ipm.CHANGE_OPTION_VALUE
    assert SetUpLib.boot_to_setup()
    for i in change_option:
        change_cmd = BmcLib.change_bios_value(i)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        arg = '{0} {1}'.format(SutConfig.Env.IPMITOOL,SutConfig.Env.GET_OPTION)
        stdoutput = BmcLib.output(arg)
        result = re.findall('\w+', stdoutput.strip())
        if result == change_cmd:
            logging.info('修改BIOS设置后，IPMITOOL返回结果与修改一致')
            logging.info(f'修改值{result}')
        else:
            stylelog.fail(f"修改BIOS设置后，IPMITOOL返回结果:{result}")
            stylelog.fail(f"修改BIOS设置后，实 际 修 改 结果:{change_cmd}")
            wrong_msg.append(f"修改BIOS设置后，IPMITOOL返回结果:{result}")
            wrong_msg.append(f"修改BIOS设置后，实 际 修 改 结果:{change_cmd}")
            count += 1
    SetUpLib.default_save()
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def bmc_user():
    user_name_list = [PwdLib.gen_pw(prefix='Root_', digit=1, upper=1, lower=2),
                      PwdLib.gen_pw(prefix='Root_', digit=1, upper=1, lower=2),
                      PwdLib.gen_pw(prefix='Root_', digit=1, upper=1, lower=2),
                      ]
    user_pwd_list = [PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     PwdLib.gen_pw(digit=4, upper=3, lower=3, symbol=0, suffix='@'),
                     ]
    count = 0
    wrong_msg = []
    logging.info('SetUp端.....................................................')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_USER_CONF, 18)
    logging.info('Setup下新增bmc用户时，输入不符合要求的用户名，提示失败..........................')
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.ADD_USER], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.ADD_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    passwords = ['a123', '1234a', 'a123@']
    for password in passwords:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_data(password)
        time.sleep(2)
        if SetUpLib.wait_message_enter(SutConfig.Ipm.USER_NAME_NOT_MATCH, 3):
            logging.info('用户名不符合规范')
        else:
            return
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    logging.info('Setup下新增bmc用户时，输入存在的用户名，提示失败.....................')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data(user_name_list[0])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[0], 20):
        logging.info(f'用户名设置{user_name_list[0]}成功')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user_pwd_list[0])
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[0])
    if SetUpLib.wait_message_enter(SutConfig.Ipm.SET_PSW_SUCCESS, 3):
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
    SetUpLib.send_data(user_name_list[0])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.USER_NAME_EXITS, 15):
        logging.info('新增bmc用户时，输入存在的用户名，提示失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    for i in stdoutput.splitlines():
        if user_name_list[0] in i:
            userid = i.split(' ')[0]
    if user_name_list[0] in stdoutput:
        logging.info(' Setup下新增bmc用户后，ipmitool user list中有该用户')
    else:
        stylelog.fail(' Setup下新增bmc用户后，ipmitool user list中没有该用户')
        wrong_msg.append(' Setup下新增bmc用户后，ipmitool user list中没有该用户')
        count += 1
    logging.info('Setup下Changer User...........................')
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_name_list[0])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[0], 15):
        logging.info(f'输入用户名{user_name_list[0]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('123456789')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ERROR_PSW, 20):
        logging.info('修改密码，输入错误密码，提示失败')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[0])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW, 20):
        logging.info('修改密码，输入正确密码后，用户密码，变为修改用户密码')
    else:
        return

    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CNANGE_USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user_pwd_list[1])
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[1])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.SET_PSW_SUCCESS, 20):
        logging.info(f'修改密码为{user_pwd_list[1]}成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        return

    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    arg = '{0} user test {1} 20 {2}'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[1])
    arg1 = '{0} user test {1} 16 {2}'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[1])
    stdoutput = BmcLib.output(arg)
    if re.search('Success', stdoutput):
        logging.info('Ipmitool下密码更改成功')
    else:
        time.sleep(1)
        stdoutput = BmcLib.output(arg1)
        if re.search('Success', stdoutput):
            logging.info('Ipmitool下密码更改成功')
        else:
            stylelog.fail('Ipmitool下密码更改失败,提示{0}'.format(stdoutput))
            wrong_msg.append('Ipmitool下密码更改失败,提示{0}'.format(stdoutput))
            count += 1

    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_name_list[0])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[0], 20):
        logging.info(f'输入用户名{user_name_list[0]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[1])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW, 20):
        pass
    else:
        return

    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.CALLBACK)
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    for i in stdoutput.splitlines():
        if user_name_list[0] in i:
            if 'CALLBACK' in i:
                logging.info('SetUp下更改权限为回叫，ipmitool返回CALLBACK')
            else:
                stylelog.fail('SetUp下更改权限为回叫，ipmitool返回{0}'.format(i.split(' ')[-1]))
                wrong_msg.append('SetUp下更改权限为回叫，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.USER)
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    for i in stdoutput.splitlines():
        if user_name_list[0] in i:
            if 'USER' in i:
                logging.info('SetUp下更改权限为用户，ipmitool返回USER')
            else:
                stylelog.fail('SetUp下更改权限为用户，ipmitool返回{0}'.format(i.split(' ')[-1]))
                wrong_msg.append('SetUp下更改权限为用户，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.OPERATOR)
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    for i in stdoutput.splitlines():
        if user_name_list[0] in i:
            if 'OPERATOR' in i:
                logging.info('SetUp下更改权限为操作人，ipmitool返回OPERATOR')
            else:
                stylelog.fail('SetUp下更改权限为操作人，ipmitool返回{0}'.format(i.split(' ')[-1]))
                wrong_msg.append('SetUp下更改权限为操作人，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 7, SutConfig.Ipm.ADMIN)
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    for i in stdoutput.splitlines():
        if user_name_list[0] in i:
            if 'ADMINISTRATOR' in i:
                logging.info('SetUp下更改权限为管理员，ipmitool返回ADMINISTRATOR')
            else:
                stylelog.fail('SetUp下更改权限为管理员，ipmitool返回{0}'.format(i.split(' ')[-1]))
                wrong_msg.append('SetUp下更改权限为管理员，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.UP)
    time.sleep(1)
    SetUpLib.send_key(Key.DOWN)
    assert SetUpLib.change_option_value(Key.DOWN, [SutConfig.Ipm.USER_PRIVILEGE], 6, SutConfig.Ipm.NO_ACCESS)
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    for i in stdoutput.splitlines():
        if user_name_list[0] in i:
            if 'NO ACCESS' in i:
                logging.info('SetUp下更改权限为无法访问，ipmitool返回NO ACCESS')
            else:
                stylelog.fail('SetUp下更改权限为无法访问，ipmitool返回{0}'.format(i.split(' ')[-1]))
                wrong_msg.append('SetUp下更改权限为无法访问，ipmitool返回{0}'.format(i.split(' ')[-1]))
                count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.DEL_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.DEL_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_name_list[0])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[0], 20):
        pass
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[1])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DEL_USER_SUCCESS, 20):
        logging.info('setup下删除用户成功')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(3)
    arg = '{0} user list'.format(SutConfig.Env.IPMITOOL)
    stdoutput = BmcLib.output(arg)
    if user_name_list[0] not in stdoutput:
        logging.info('setup下删除用户，ipmitool没有返回用户')
    else:
        stylelog.fail('setup下删除用户，ipmitool仍返回用户')
        wrong_msg.append('setup下删除用户，ipmitool仍返回用户')
        count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)

    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.ADD_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.ADD_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data(user_name_list[1])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[1], 20):
        logging.info(f'用户名设置{user_name_list[1]}成功')

    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user_pwd_list[2])
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[2])
    if SetUpLib.wait_message_enter(SutConfig.Ipm.SET_PSW_SUCCESS, 3):
        logging.info('用户密码设置成功')
        time.sleep(1)
    else:
        return
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_name_list[1])
    time.sleep(2)
    if SetUpLib.wait_message_enter(user_name_list[1], 20):
        logging.info(f'输入用户名{user_name_list[1]}')
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    time.sleep(1)
    for i in range(0, 4):
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('123456789')
        if SetUpLib.wait_message(SutConfig.Ipm.ERROR_PSW, 5):
            logging.info(f'第{i + 1}次输错密码')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail(f'第{i + 1}次输错密码没有提示密码错误')
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            count += 1
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user_pwd_list[2])
    if not SetUpLib.wait_message(SutConfig.Ipm.ERROR_PSW, 5):
        logging.info(f'第5次输入正确密码，没有提示密码错误')
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter(user_name_list[1])
        if SetUpLib.wait_message(user_name_list[1], 20):
            logging.info(f'输入用户名{user_name_list[1]}')
        else:
            return
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
        time.sleep(1)
    else:
        stylelog.fail(f'第5次输入正确密码提示密码错误')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)

    for i in range(1, 6):
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('123456789')
        if SetUpLib.wait_message(SutConfig.Ipm.ERROR_PSW, 5):
            logging.info(f'输错密码{i}次')
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
        else:
            stylelog.fail(f'输错密码{i}次,没有提示密码错误')
            count += 1
            time.sleep(1)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter(user_pwd_list[2])
    if SetUpLib.wait_message(SutConfig.Ipm.ERROR_PSW, 5):
        logging.info('输错密码5次后，输入正确密码仍提示密码错误')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
    else:
        stylelog.fail('输错密码5次后，输入正确密码没有密码错误')
        count += 1
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)

    userid = str(int(userid) + 1)
    logging.info('BMC端.....................................................')
    logging.info('BMC增加用户.....................................................')
    arg = '{0} user set name {1} {2}'.format(SutConfig.Env.IPMITOOL, userid, user_name_list[2])
    BmcLib.output(arg)
    logging.info('BMC设置用户名，Run {0}'.format(arg))
    time.sleep(3)
    arg = '{0} user set password {1} {2} 20'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[3])
    BmcLib.output(arg)
    logging.info('BMC设置密码，Run {0}'.format(arg))
    time.sleep(3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[3])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW, 20):
        logging.info('BMC新建用户，SetUp下认证成功')

    else:
        logging.info('BMC新建用户，SetUp下认证失败')

        return
    time.sleep(3)
    logging.info('BMC更改用户状态.....................................................')
    arg = '{0} user enable {1}'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户状态为enable，Run {0}'.format(arg))
    time.sleep(15)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[3])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ENABLE, 20):
        logging.info('BMC修改用户状态为enabled，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为enabled，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为enabled，SetUp下认证失败')
        count += 1
    time.sleep(2)
    arg = '{0} user disable {1}'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户状态为disable，Run {0}'.format(arg))
    time.sleep(15)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[3])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DISABLE, 20):
        logging.info('BMC修改用户状态为disabled，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为disabled，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为disabled，SetUp下认证失败')
        count += 1
    time.sleep(2)
    logging.info('BMC更改用户密码.....................................................')
    arg = '{0} user set password {1} {2} 20'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[4])
    BmcLib.output(arg)
    logging.info('BMC修改用户密码为{1}，Run {0}'.format(arg, user_pwd_list[4]))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[3])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ERROR_PSW, 20):
        logging.info(f'BMC修改用户密码为{user_pwd_list[4]}，输入原密码{user_pwd_list[3]}显示密码错误')
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[4])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CNANGE_USER_PSW, 20):
        logging.info(f'BMC修改用户密码为{user_pwd_list[4]}，SetUp下验证成功')
        time.sleep(2)
    else:
        return
    logging.info('BMC更改用户权限....................................................................')
    arg = '{0} user priv {1} 0x1 1'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为Callback，Run {0}'.format(arg))
    time.sleep(3)
    arg = '{0} user priv {1} 0x1 8'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为Callback，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[4])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.CALLBACK, 20):
        logging.info('BMC修改用户权限为Callback，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为Callback，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为Callback，SetUp下认证失败')
        count += 1
    time.sleep(2)

    arg = '{0} user priv {1} 0x2 1'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为User，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0x2 8'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为User，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[4])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.USER, 20):
        logging.info('BMC修改用户权限为User，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为User，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为User，SetUp下认证失败')
        count += 1
    time.sleep(2)

    arg = '{0} user priv {1} 0x3 1'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为Operator，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0x3 8'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为Operator，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    # else:
    #     return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[4])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.OPERATOR, 20):
        logging.info('BMC修改用户权限为Operator，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为Operator，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为Operator，SetUp下认证失败')
        count += 1
    time.sleep(2)

    arg = '{0} user priv {1} 0x4 1'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为Administrator，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0x4 8'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为Administrator，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[4])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.ADMIN, 20):
        logging.info('BMC修改用户权限为Administrator，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为Administrator，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为Administrator，SetUp下认证失败')
        count += 1
    time.sleep(2)

    arg = '{0} user priv {1} 0xF 1'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为No Access，Run {0}'.format(arg))
    time.sleep(5)
    arg = '{0} user priv {1} 0xF 8'.format(SutConfig.Env.IPMITOOL, userid)
    BmcLib.output(arg)
    logging.info('BMC设置用户权限为No Access，Run {0}'.format(arg))
    time.sleep(5)
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.CHANGE_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.CHANGE_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)

    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2], 20):
        logging.info(f'输入用户名{user_name_list[2]}')
    else:
        return
    time.sleep(2)
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[4])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.NO_ACCESS, 20):
        logging.info('BMC修改用户权限为No Access，SetUp下认证成功')
    else:
        stylelog.fail('BMC修改用户状态为No Access，SetUp下认证失败')
        wrong_msg.append('BMC修改用户状态为No Access，SetUp下认证失败')
        count += 1
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    time.sleep(2)
    logging.info('BMC更改用户密码.....................................................')
    arg = '{0} user set password {1} {2} 20'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[5])
    BmcLib.output(arg)
    logging.info('BMC修改用户密码为{1}，Run {0}'.format(arg, user_pwd_list[5]))
    time.sleep(3)
    time.sleep(2)
    logging.info('BMC更改用户密码.....................................................')
    arg = '{0} user set password {1} {2} 20'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[6])
    BmcLib.output(arg)
    logging.info('BMC修改用户密码为{1}，Run {0}'.format(arg, user_pwd_list[6]))
    time.sleep(5)
    logging.info('BMC更改用户密码.....................................................')
    arg = '{0} user set password {1} {2} 20'.format(SutConfig.Env.IPMITOOL, userid, user_pwd_list[7])
    BmcLib.output(arg)
    logging.info('BMC修改用户密码为{1}，Run {0}'.format(arg, user_pwd_list[7]))
    time.sleep(5)
    if not SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.DEL_USER], 5):
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.DEL_USER], 5)
    SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_NAME], 5):
        assert SetUpLib.locate_option(Key.UP, [SutConfig.Ipm.USER_NAME], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_name_list[2])
    time.sleep(1)
    if SetUpLib.wait_message_enter(user_name_list[2]):
        pass
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Ipm.USER_PSW], 5)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data(user_pwd_list[7])
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Ipm.DEL_USER_SUCCESS, 20):
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


def sol():
    count = 0
    wrong_msg = []
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.CLOSE_SOL, 18, save=True)
    assert SetUpLib.boot_to_setup()
    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sol info 1')
    if output:
        if any(re.search('Enabled\s*: false', i) for i in output.splitlines()):
            logging.info('SetUp下关闭sol,Ipmi返回结果为禁用')
        else:
            stylelog.fail(f'SetUp下关闭sol,Ipmi返回结果不是禁用,{output}')
            wrong_msg.append(f'SetUp下关闭sol,Ipmi返回结果不是禁用,{output}')
            count += 1
    BmcLib.output(f'{SutConfig.Env.IPMITOOL} sol set enabled true 1')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SOL[:-1], 18)
    if not SetUpLib.verify_info(
            [f'<{list(SutConfig.Ipm.OPEN_SOL[-1].values())[0]}>\s*{list(SutConfig.Ipm.OPEN_SOL[-1].keys())[0]}'], 10):
        stylelog.fail('Ipmi启用sol，SetUp下仍是禁用')
        wrong_msg.append('Ipmi启用sol，SetUp下仍是禁用')
        count += 1
    BmcLib.output(f'{SutConfig.Env.IPMITOOL} sol set enabled false 1')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SOL[:-1], 18)
    if not SetUpLib.verify_info(
            [f'<{list(SutConfig.Ipm.CLOSE_SOL[-1].values())[0]}>\s*{list(SutConfig.Ipm.CLOSE_SOL[-1].keys())[0]}'], 10):
        stylelog.fail('Ipmi禁用sol，SetUp下是启用')
        wrong_msg.append('Ipmi禁用sol，SetUp下是启用')
        count += 1
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.OPEN_SOL, 18, save=True)
    assert SetUpLib.boot_to_setup()
    output = BmcLib.output(f'{SutConfig.Env.IPMITOOL} sol info 1')
    if output:
        if any(re.search('Enabled\s*: true', i) for i in output.splitlines()):
            logging.info('SetUp下打开sol,Ipmi返回结果为启用')
        else:
            stylelog.fail(f'SetUp下打开sol,Ipmi返回结果不是启用,{output}')
            wrong_msg.append(f'SetUp下打开sol,Ipmi返回结果不是启用,{output}')
            count += 1
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return


def bmc_system_log():
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_SYS_LOG, 18)
    logging.info('SetUp下收集BMC系统日志')
    start_time = time.time()
    while True:
        data = SetUpLib.get_data(1,limit_time=True)
        end_time = time.time()
        if 'Total Entries' in data:
            break
        if end_time - start_time > 300:
            break
    logging.info('SetUp下收集BMC系统日志完成')
    setup = re.findall('\d{4}/\d+/\d+ \d+:\d+:\d+', data)
    setup_log = []
    for i in setup:
        if re.search('/\d/', i):
            i = i[:5] + '0' + i[5:]
        if re.search('/\d ', i):
            i = i[:8] + '0' + i[8:]
        if re.search(' \d:', i):
            i = i[:11] + '0' + i[11:]
        setup_log.append(i)
    logging.info('Bmc下收集BMC系统日志')
    arg = '{0} sel list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    bmc = re.findall('\d+/\d+/\d+ \| \d+:\d+:\d+', stdoutput.decode('gbk'))[::-1][:len(setup_log)]
    logging.info('Bmc下收集BMC系统日志完成')
    bmc_log = []
    for i in bmc:
        i = i.replace('| ', '')
        year = re.findall('/(\d{4})', i)[0]
        i = re.sub('/\d{4}', '', i)
        i = year + '/' + i
        bmc_log.append(i)
    logging.info('SetUp系统日志:{}'.format(setup_log))
    logging.info(' BMC 系统日志:{}'.format(bmc_log))
    if bmc_log == setup_log:
        logging.info('SetUp下系统日志与BMC下系统日志一致')

    else:
        stylelog.fail('SetUp下系统日志与BMC下系统日志不一致')
        return
    logging.info('清除系统日志')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.CLEAR_FRU, 18)
    time.sleep(2)
    SetUpLib.send_key(Key.Y)
    time.sleep(10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_SYS_LOG, 18)
    logging.info('SetUp下收集BMC系统日志')
    start_time = time.time()
    while True:
        data = SetUpLib.get_data(1,limit_time=True)
        end_time = time.time()
        if 'Total Entries' in data:
            break
        if end_time - start_time > 300:
            break
    logging.info('SetUp下收集BMC系统日志完成')
    setup_clear = re.findall('\d{4}/\d+/\d+ \d+:\d+:\d+', data)
    setup_log_clear = []
    for i in setup_clear:
        if re.search('/\d/', i):
            i = i[:5] + '0' + i[5:]
        if re.search('/\d ', i):
            i = i[:8] + '0' + i[8:]
        setup_log_clear.append(i)
    logging.info('Bmc下收集BMC系统日志')
    arg = '{0} sel list'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    bmc_clear = re.findall('\d+/\d+/\d+ \| \d+:\d+:\d+', stdoutput.decode('gbk'))[::-1][:len(setup_log_clear)]
    logging.info('Bmc下收集BMC系统日志完成')
    bmc_log_clear = []
    for i in bmc_clear:
        i = i.replace('| ', '')
        year = re.findall('/(\d{4})', i)[0]
        i = re.sub('/\d{4}', '', i)
        i = year + '/' + i
        bmc_log_clear.append(i)
    logging.info('SetUp系统日志:{}'.format(setup_log_clear))
    logging.info(' BMC 系统日志:{}'.format(setup_log_clear))
    if setup_log_clear == setup_log_clear:
        logging.info('清除系统日志后，SetUp下和BMC下返回结果一致')
        if len(setup_log_clear) == 1:
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
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Ipm.LOC_FRU, 18)
    setup_fru = []
    data = SetUpLib.get_data(2)
    data = re.findall('(Chassis Part Number.*)', data)[0]
    for i in re.findall('[A-Z]\w+ *\w+ *\w+[a-z] {2,}[0-9A-Za-z\-]+   ', data):
        setup_fru = setup_fru + re.findall('  ([0-9A-Za-z].*)', i.strip())
    setup_fru = setup_fru + [
        re.findall('System UUID *([a-zA-z\-0-9]+ {0,1}[a-zA-z\-0-9]+)   ', data)[0].replace(' ', '').lower()]
    bmc_fru = []
    arg = '{0} fru print'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    data = stdoutput.decode('gbk')
    bmc_fru = re.findall('Chassis Part Number *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Chassis Serial *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Board Mfg *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Board Product *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Board Serial *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Board Part Number *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Manufacturer *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Name *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Part Number *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Version *: ([0-9A-Za-z\-]+)', data)[:1]
    bmc_fru = bmc_fru + re.findall('Product Serial *: ([0-9A-Za-z\-]+)', data)[:1]
    arg = '{0} mc guid'.format(SutConfig.Env.IPMITOOL)
    p = subprocess.Popen(args=arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    bmc_fru = bmc_fru + [re.findall('System GUID *: ([0-9A-Za-z\-]+)', stdoutput.decode('gbk'))[0].lower()]

    if setup_fru == bmc_fru:
        logging.info('FRU信息验证通过')
        logging.info('SetUp下FRU:{}'.format(setup_fru))
        logging.info(' BMC 下FRU:{}'.format(bmc_fru))
        return True
    else:
        del bmc_fru[-4]
        if setup_fru == bmc_fru:
            logging.info('FRU信息验证通过')
            logging.info('SetUp下FRU:{}'.format(setup_fru))
            logging.info(' BMC 下FRU:{}'.format(bmc_fru))
            return True
        else:
            stylelog.fail('FRU信息验证不通过')
            logging.info('SetUp下FRU:{}'.format(setup_fru))
            logging.info(' BMC 下FRU:{}'.format(bmc_fru))
            return
