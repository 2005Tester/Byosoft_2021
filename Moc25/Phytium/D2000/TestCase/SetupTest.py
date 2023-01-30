# coding='utf-8'
import re
import time
import logging
from D2000.BaseLib import BmcLib, SetUpLib, SshLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from D2000.TestCase import UpdateTest
from batf import core
from batf.SutInit import Sut
from batf.Report import stylelog


@core.test_case(('101', '[TC101]板载网卡配置', '板载网卡配置'))
def onboard_lan():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_ONBOARD_LAN, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            datas = SetUpLib.get_data(30, SutConfig.Msg.BOOTMENU_KEY)
        else:
            logging.info('没有开机')
            return
        if any(re.search(i, datas) for i in
               [SutConfig.Msg.PXE_PORT1, SutConfig.Msg.HTTP_PORT1, SutConfig.Msg.PXE_PORT2, SutConfig.Msg.HTTP_PORT2]):
            stylelog.fail('关闭板载网卡启动菜单仍出现PXE启动项')
            return True
        else:
            logging.info('关闭板载网卡,启动菜单没有PXE启动项')

        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 20, SutConfig.Msg.SETUP_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_ONBOARD_LAN, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            datas = SetUpLib.get_data(30, SutConfig.Msg.BOOTMENU_KEY)
        else:
            logging.info('没有开机')
            return
        if all(re.search(i, datas) for i in
               [SutConfig.Msg.PXE_PORT1, SutConfig.Msg.HTTP_PORT1, SutConfig.Msg.PXE_PORT2, SutConfig.Msg.HTTP_PORT2]):
            logging.info('打开板载网卡,启动菜单出现PXE启动项')
        else:
            stylelog.fail('打开板载网卡启动菜单没有出现PXE启动项')
            return
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('102', '[TC102]SR-IOV', 'SR-IOV'))
def sriov():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_SR, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)

        assert SetUpLib.boot_os_from_bm()
        result = SshLib.execute_command_limit(Sut.OS_SSH, 'ifconfig | grep flags')
        buss = re.findall('(\w+:\w+.\w+) ', SshLib.execute_command_limit(Sut.OS_SSH, 'lspci | grep Eth')[0])
        bus = []
        if buss == []:
            logging.info('没有网卡设备跳过测试')
            return core.Status.Pass
        ethname_list = re.findall('(.*?): flags', result[0])
        if not ethname_list:
            stylelog.fail('没有找到ethname')
            return
        for i in SutConfig.Sup.REMOVE_ETHNAME:
            ethname_list.remove(i)

        for i in ethname_list:
            result1 = SshLib.execute_command_limit(Sut.OS_SSH, f'cat /sys/class/net/{i}/device/sriov_totalvfs')
            if result1[1] or result1[0] == '0':
                logging.info(f'{i}不支持SR-IOV')
                bus.append(buss[ethname_list.index(i)])
            else:
                SshLib.execute_command_limit(Sut.OS_SSH,
                                             f'echo 2 > /sys/class/net/{i}/device/sriov_numvfs')

        cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
        buslist = []
        for i in buss:
            if i not in bus:
                buslist.append(i)
        if cmd_result1[0].count('Virtual Function') == 0:
            logging.info('SR-IOV 关闭，系统下正常显示')
        else:
            stylelog.fail('SR-IOV 关闭，系统下异常')
            wrong_msg.append('SR-IOV 关闭，系统下异常')
            count += 1
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SR, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_os_from_bm()
        result = SshLib.execute_command_limit(Sut.OS_SSH, 'ifconfig | grep flags')
        buss = re.findall('(\w+:\w+.\w+) ', SshLib.execute_command_limit(Sut.OS_SSH, 'lspci | grep Eth')[0])
        bus = []
        if buss == []:
            logging.info('没有网卡设备跳过测试')
            return core.Status.Pass
        ethname_list = re.findall('(.*?): flags', result[0])
        if not ethname_list:
            stylelog.fail('没有找到ethname')
            return
        for i in SutConfig.Sup.REMOVE_ETHNAME:
            ethname_list.remove(i)

        for i in ethname_list:
            result1 = SshLib.execute_command_limit(Sut.OS_SSH, f'cat /sys/class/net/{i}/device/sriov_totalvfs')
            if result1[1] or result1[0] == '0':
                logging.info(f'{i}不支持SR-IOV')
                bus.append(buss[ethname_list.index(i)])
            else:
                SshLib.execute_command_limit(Sut.OS_SSH,
                                             f'echo 2 > /sys/class/net/{i}/device/sriov_numvfs')

        cmd_result1 = SshLib.execute_command_limit(Sut.OS_SSH, "lspci | grep Eth")
        buslist = []
        for i in buss:
            if i not in bus:
                buslist.append(i)
        print(buslist)
        if cmd_result1[0].count('Virtual Function') == len(buslist) * 2:
            logging.info('SR-IOV 打开，系统下正常显示')
        else:
            stylelog.fail('SR-IOV 打开，系统下异常')
            wrong_msg.append('SR-IOV 打开，系统下异常')
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


@core.test_case(('102', '[TC102]User Wait Time', '用户等待时间'))
def user_wait_time():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_BOOT_ORDER_USB, 18)
        time.sleep(1)
        for i in range(0, 7):
            SetUpLib.send_key(Key.ADD)
            time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_USER_TIME_10, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(1)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            logging.info('进入POST界面')
            start = time.time()
        else:
            return
        if SetUpLib.wait_message(SutConfig.Msg.SHELL_MSG):
            logging.info('进入Shell')
            end = time.time()
        else:
            return
        spent_time = end - start
        if 9 <= spent_time <= 11:
            logging.info('设置用户等待时间为10秒验证成功')
        else:
            stylelog.fail(f'设置用户等待时间10秒,验证失败,实际时间为{spent_time}秒')
            wrong_msg.append(f'设置用户等待时间10秒,验证失败,实际时间为{spent_time}秒')
            count += 1
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_USER_TIME_MAX, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            logging.info('进入POST界面')
        if not SetUpLib.wait_message(SutConfig.Msg.SHELL_MSG, 30):
            logging.info('设置用户等待时间为65535,POST界面一直等待')
        else:
            stylelog.fail('设置用户等待时间为65535,POST界面没有一直等待')
            wrong_msg.append('设置用户等待时间为65535,POST界面没有一直等待')
            count += 1
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_USER_TIME_MIN, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(1)
        start = time.time()
        datas = ''
        while True:
            data = SetUpLib.get_data(1)
            datas += data
            if re.search(SutConfig.Msg.SHELL_MSG, data):
                break
            if time.time() - start > 150:
                break
        if not re.search(SutConfig.Msg.POST_MESSAGE, datas):
            logging.info(f'设置用户等待时间为0秒,不显示{SutConfig.Msg.POST_MESSAGE}')
        else:
            stylelog.fail(f'设置用户等待时间为0秒,仍显示{SutConfig.Msg.POST_MESSAGE}')
            wrong_msg.append(f'设置用户等待时间为0秒,仍显示{SutConfig.Msg.POST_MESSAGE}')
            count += 1

        time.sleep(10)
        SetUpLib.send_data_enter('exit 0')
        if SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 10):
            logging.info('进入SetUp')
        else:
            return
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        return True
    except Exception as e:
        SetUpLib.reboot()
        if SetUpLib.wait_message(SutConfig.Msg.SHELL_MSG):
            SetUpLib.send_data_enter('exit 0')
        time.sleep(10)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(10)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        logging.error(e)
        return core.Status.Fail


@core.test_case(('103', '[TC103]PXE Retry', '网络启动重试'))
def pxe_retry():
    try:
        retry_counts = 3
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PXE_RETRY, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Sup.PXE_MSG, 200, SutConfig.Msg.POST_MESSAGE)
        counts = 0
        while True:
            if SetUpLib.wait_message(SutConfig.Sup.PXE_RETRY_MSG, 300):
                counts += 1
                logging.info('第{0}次网络重试'.format(counts))
            else:
                return
            if counts == retry_counts:
                break
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PXE_RETRY, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Sup.PXE_MSG, 200, SutConfig.Msg.POST_MESSAGE)
        time.sleep(100)
        if BmcLib.ping_sut():
            logging.info('网络启动重试关闭，启动失败后，不再重新尝试，直接进入系统')
        else:
            return
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('104', '[TC104]Network Boot', '网络引导'))
def net_boot():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_NET, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(1)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            datas = SetUpLib.get_data(30, SutConfig.Msg.BOOTMENU_KEY)
        else:
            logging.info('没有开机')
            return
        if not re.search('PXE|HTTP', datas):
            logging.info('关闭网络引导，启动菜单没有PXE启动项')
        else:
            stylelog.fail('关闭网络引导，启动菜单仍出现PXE启动项')
            wrong_msg.append('关闭网络引导，启动菜单仍出现PXE启动项')
            count += 1
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_NET, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(1)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            datas = SetUpLib.get_data(30, SutConfig.Msg.BOOTMENU_KEY)
        else:
            logging.info('没有开机')
            return
        if all(re.search(i, datas) for i in
               [SutConfig.Msg.PXE_PORT1, SutConfig.Msg.HTTP_PORT1, SutConfig.Msg.PXE_PORT2, SutConfig.Msg.HTTP_PORT2]):
            logging.info('打开网络引导,启动菜单出现PXE启动项')
        else:
            stylelog.fail('打开网络引导,启动菜单没有出现PXE启动项')
            wrong_msg.append('打开网络引导,启动菜单没有出现PXE启动项')
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


def is_hid_setup(data, count=0):
    if count == 0:
        if re.search('USB\s*Mouse\s*:\s*|USB\s*Keyboard\s*:\s*', data):
            return True
        else:
            return False
    else:
        if len(re.findall('USB\s*Mouse\s*:\s*|USB\s*Keyboard\s*:\s*', data)) == count:
            return True
        else:
            return False


def is_mass_sotrage_setup(data, count=0):
    if count == 0:
        if re.search('USB\s*Storage\s*:\s*', data):
            return True
        else:
            return False
    else:
        if len(re.findall('USB\s*Storage\s*:\s*', data)) == count:
            return True
        else:
            return False


def is_others_setup(data, count=0):
    if count == 0:
        if re.search('USB\s*Others\s*:\s*', data):
            return True
        else:
            return False
    else:
        if len(re.findall('USB\s*Others\s*:\s*', data)) == count:
            return True
        else:
            return False


def is_mass_storage_setup_bootmenu(count=0):
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_BOOT_MANAGER, 18)
    data = SetUpLib.get_data(2)
    if count == 0:
        if re.search('UEFI USB:', data):
            return True
        else:
            return False
    else:
        if len(re.findall('UEFI USB:', data)) == count:
            return True
        else:
            return False


def is_mass_storage_bootmenu(data, count=0):
    if count == 0:
        if re.search('UEFI USB:', data):
            return True
        else:
            return False
    else:
        if len(re.findall('UEFI USB:', data)) == count:
            return True
        else:
            return False


def is_mass_storage_shell(count=0):
    SetUpLib.send_data_enter('map -r')
    data = SetUpLib.get_data(3)
    fs = list(set(re.findall('(FS\d+:).*:\r\n\s*.*/USB.*\r\n', data, re.I)))

    if count == 0:
        if fs:
            return True
        else:
            return False
    else:
        if len(fs) == count:
            return True
        else:
            return False


def is_read_only():
    sign = True
    SetUpLib.send_data_enter('map -r')
    data = SetUpLib.get_data(3)
    fs = re.findall('(FS\d+:).*:\r\n\s*.*/USB.*\r\n', data, re.I)
    if fs:
        for i in fs:
            SetUpLib.send_data_enter(i)
            time.sleep(1)
            SetUpLib.send_data_enter('edit')
            result = SetUpLib.get_data(2, readline=False)
            if re.search('UEFI EDIT', result):
                time.sleep(1)
                SetUpLib.send_key(Key.CONTROL_Q)
                time.sleep(1)

            elif re.search('edit: Access Denied', result):
                time.sleep(1)
                sign = False
            elif re.search('edit: Invalid File Name', result):
                time.sleep(1)

            else:
                assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 200,
                                                 SutConfig.Msg.POST_MESSAGE)
                SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 18, SutConfig.Msg.SHELL_MSG)
                time.sleep(10)
        SetUpLib.send_data_enter('exit')
        time.sleep(1)

        if sign == False:
            return True
        else:
            return False
    else:
        return False


@core.test_case(('105', '[TC105]USB全局端口测试(不接USB Hub)', 'USB全局端口测试(不接USB Hub)'))
def usb_global_port():
    try:
        count = 0
        wrong_msg = []
        all_type = list(SutConfig.Sup.PORT_DEVICE_DICT.values())
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        for i in SutConfig.Sup.USB_PORT_GLOBAL_VALUES:
            if i == 'AUTO':
                values = 'HID & Mass Storage & Others'
            elif i == 'None':
                values = ''
            else:
                values = i
            value = ''
            for m in values.split(' & '):
                for n in all_type:
                    if n in m:
                        value += m
            print(value)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.USB_PORT_GLOBAL_OPTION_NAME: i}], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(2)
            data = SetUpLib.boot_to_boot_menu(True)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_bootmenu(data, count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_storage_bootmenu(data, count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，启动菜单不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 18, SutConfig.Msg.SHELL_MSG):
                assert SetUpLib.boot_to_shell()
            time.sleep(10)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_shell(count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    if re.search('Read Only', value, re.I):
                        if is_read_only():
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备只读')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            count += 1
                    else:
                        if is_read_only() == False:
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备可以读写')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不可以读写')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不可以读写')
                            count += 1
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_shell(count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，Shell不显示USB存储设备信息')
                    SetUpLib.send_data_enter('exit')
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 18, SutConfig.Msg.SETUP_MESSAGE):
                assert SetUpLib.boot_to_setup()
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_setup_bootmenu(count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_setup_bootmenu(count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    count += 1
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2)
            if re.search('HID', value, re.I):
                if is_hid_setup(data, count=all_type.count('HID')):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_hid_setup(data, count=all_type.count('HID')) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Mass Storage', value, re.I):
                if is_mass_sotrage_setup(data, count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_sotrage_setup(data, count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Others', value, re.I):
                if is_others_setup(data, count=all_type.count('Others')):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_others_setup(data, count=all_type.count('Others')) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    wrong_msg.append(data)
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


@core.test_case(('106', '[TC106]USB所有端口测试(不接USB Hub)', 'USB所有端口测试(不接USB Hub)'))
def usb_port():
    try:
        count = 0
        wrong_msg = []
        all_type = list(SutConfig.Sup.PORT_DEVICE_DICT.values())
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_GLOBAL_USB_PORT, 18)
        for i in SutConfig.Sup.USB_PORT_VALUES:
            if i == 'AUTO':
                values = 'HID & Mass Storage & Others'
            elif i == 'None':
                values = ''
            else:
                values = i
            value = ''
            for m in values.split(' & '):
                for n in all_type:
                    if n in m:
                        value += m
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            for option in SutConfig.Sup.ALL_USB_PORT_OPTION_NAME:
                assert SetUpLib.enter_menu_change_value(Key.DOWN, [{option: i}], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(1)
            data = SetUpLib.boot_to_boot_menu(True)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_bootmenu(data, count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_storage_bootmenu(data, count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，启动菜单不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 18, SutConfig.Msg.SHELL_MSG):
                assert SetUpLib.boot_to_shell()
            time.sleep(10)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_shell(count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    if re.search('Read Only', value, re.I):
                        if is_read_only():
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备只读')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            count += 1
                    else:
                        if is_read_only() == False:
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备可以读写')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不可以读写')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不可以读写')
                            count += 1
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_shell(count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，Shell不显示USB存储设备信息')
                    SetUpLib.send_data_enter('exit')
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 18, SutConfig.Msg.SETUP_MESSAGE):
                assert SetUpLib.boot_to_setup()
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_setup_bootmenu(count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_setup_bootmenu(count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    count += 1
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2)
            if re.search('HID', value, re.I):
                if is_hid_setup(data, count=all_type.count('HID')):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_hid_setup(data, count=all_type.count('HID')) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Mass Storage', value, re.I):
                if is_mass_sotrage_setup(data, count=all_type.count('Mass Storage')):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_sotrage_setup(data, count=all_type.count('Mass Storage')) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Others', value, re.I):
                if is_others_setup(data, count=all_type.count('Others')):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_others_setup(data, count=all_type.count('Others')) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    wrong_msg.append(data)
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


@core.test_case(('107', '[TC107]USB全局端口测试(接入USB Hub)', 'USB全局端口测试(接入USB Hub)'))
def usb_global_port_hub():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        for i in SutConfig.Sup.USB_PORT_GLOBAL_VALUES:
            if i == 'AUTO':
                value = 'HID & Mass Storage & Others'
            elif i == 'None':
                value = ''
            else:
                value = i
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.USB_PORT_GLOBAL_OPTION_NAME: i}], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(1)
            data = SetUpLib.boot_to_boot_menu(True)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_bootmenu(data):

                    logging.info(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_storage_bootmenu(data) == False:
                    logging.info(f'设置USB端口为{i}，启动菜单不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 18, SutConfig.Msg.SHELL_MSG):
                assert SetUpLib.boot_to_shell()
            time.sleep(10)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_shell():
                    logging.info(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    if re.search('Read Only', value, re.I):
                        if is_read_only():
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备只读')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            count += 1
                    else:
                        if is_read_only() == False:
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备可以读写')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不可以读写')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不可以读写')
                            count += 1
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_shell() == False:
                    logging.info(f'设置USB端口为{i}，Shell不显示USB存储设备信息')
                    SetUpLib.send_data_enter('exit')
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 18, SutConfig.Msg.SETUP_MESSAGE):
                assert SetUpLib.boot_to_setup()
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_setup_bootmenu():
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_setup_bootmenu() == False:
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    count += 1
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2)
            if re.search('HID', value, re.I):
                if is_hid_setup(data):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_hid_setup(data) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Mass Storage', value, re.I):
                if is_mass_sotrage_setup(data):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_sotrage_setup(data) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Others', value, re.I):
                if is_others_setup(data):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_others_setup(data) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    wrong_msg.append(data)
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


@core.test_case(('108', '[TC108]USB指定端口测试(接入USB Hub)', 'USB指定端口测试(接入USB Hub)'))
def usb_port_hub():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_GLOBAL_USB_PORT, 18)
        for i in SutConfig.Sup.USB_PORT_VALUES:
            if i == 'AUTO':
                value = 'HID & Mass Storage & Others'
            elif i == 'None':
                value = ''
            else:
                value = i
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sup.USB_PORT_OPTION_NAME: i}], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(1)
            data = SetUpLib.boot_to_boot_menu(True)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_bootmenu(data):
                    logging.info(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_storage_bootmenu(data) == False:
                    logging.info(f'设置USB端口为{i}，启动菜单不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，启动菜单显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.SHELL, 18, SutConfig.Msg.SHELL_MSG):
                assert SetUpLib.boot_to_shell()
            time.sleep(10)
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_shell():
                    logging.info(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    if re.search('Read Only', value, re.I):
                        if is_read_only():
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备只读')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不是只读')
                            count += 1
                    else:
                        if is_read_only() == False:
                            logging.info(f'设置USB端口为{i}，Shell下USB存储设备可以读写')
                        else:
                            stylelog.fail(f'设置USB端口为{i}，Shell下USB存储设备不能读写')
                            wrong_msg.append(f'设置USB端口为{i}，Shell下USB存储设备不能读写')
                            count += 1
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_shell() == False:
                    SetUpLib.send_data_enter('exit')
                    logging.info(f'设置USB端口为{i}，Shell不显示USB存储设备信息')
                else:
                    SetUpLib.send_data_enter('exit')
                    stylelog.fail(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，Shell显示USB存储设备信息')
                    count += 1
            if not SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 18, SutConfig.Msg.SETUP_MESSAGE):
                assert SetUpLib.boot_to_setup()
            if re.search('Mass Storage', value, re.I):
                if is_mass_storage_setup_bootmenu():
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器没有显示USB存储设备信息')
                    count += 1
            else:
                if is_mass_storage_setup_bootmenu() == False:
                    logging.info(f'设置USB端口为{i}，SetUp启动管理器不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    wrong_msg.append(f'设置USB端口为{i}，SetUp启动管理器显示USB存储设备信息')
                    count += 1
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2)
            if re.search('HID', value, re.I):
                if is_hid_setup(data):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_hid_setup(data) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示键鼠信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示键鼠信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Mass Storage', value, re.I):
                if is_mass_sotrage_setup(data):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_mass_sotrage_setup(data) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示USB存储设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示USB存储设备信息')
                    wrong_msg.append(data)
                    count += 1
            if re.search('Others', value, re.I):
                if is_others_setup(data):
                    logging.info(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表没有显示其他设备信息')
                    wrong_msg.append(data)
                    count += 1
            else:
                if is_others_setup(data) == False:
                    logging.info(f'设置USB端口为{i}，USB设备列表不显示其他设备信息')
                else:
                    stylelog.fail(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    stylelog.fail(data)
                    wrong_msg.append(f'设置USB端口为{i}，USB设备列表显示其他设备信息')
                    wrong_msg.append(data)
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


@core.test_case(('109', '[TC109]板载SATA槽开关', '板载SATA槽开关'))
def onboard_sata_slot():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_ONBOARD_SATA, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_SATA_INFO, 18)
        if SetUpLib.get_data(2).count('None') == 2:
            logging.info('板载SATA没有设备,跳过测试')
            return core.Status.Skip
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_ONBOARD_SATA, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_SATA_INFO, 18)
        data = SetUpLib.get_data(2)
        if data.count('None') == 2:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_ONBOARD_SATA, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            logging.info('关闭板载SATA,SATA设备列表中没有SATA设备')
            return True
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_ONBOARD_SATA, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            stylelog.fail('关闭板载SATA,SATA设备列表中仍有SATA设备')
            stylelog.fail(re.findall('SATA Drive \d.*?', data))
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('110', '[TC110]NVME槽开关', 'NVME槽开关'))
def nvme_slot():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_NVME, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_NVME_INFO, 18)
        if not re.search('SN:', SetUpLib.get_data(2)):
            logging.info('NVME槽没有设备,跳过测试')
            return core.Status.Skip
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_NVME, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_NVME_INFO, 18)
        data = SetUpLib.get_data(2)
        if not re.search('SN:', data):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_NVME, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            logging.info('关闭NVME槽,NVME设备列表没有设备')
            return True
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_NVME, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            stylelog.fail('关闭NVME槽,NVME设备列表仍有设备')
            stylelog.fail(data)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('111', '[TC111]PEU0[0:7]槽开关', 'PEU0[0:7]槽开关'))
def peu0_07_slot():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE0_07, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCIE_INFO, 18)
        if not re.search('1DB7', SetUpLib.get_data(2)):
            logging.info('PEU0[0:7]槽没有设备,跳过测试')
            return core.Status.Skip
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PUE0_07, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCIE_INFO, 18)
        data = SetUpLib.get_data(2)
        if not re.search('1DB7', data):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE0_07, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            logging.info('关闭PEU0[0:7]，PCIE设备列表不显示设备')
            return True
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE0_07, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            stylelog.fail('关闭PEU0[0:7]，PCIE设备列表仍显示设备')
            stylelog.fail(data)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('112', '[TC112]板载USB槽开关', '板载USB槽开关'))
def usb_slot():
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_USB_SLOT, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
        data = SetUpLib.get_data(2)
        all_usb_name = SutConfig.Sup.ALL_USB_PORT_OPTION_NAME
        all_usb_name.append(SutConfig.Sup.USB_PORT_GLOBAL_OPTION_NAME)
        if all(not re.search(i, data) for i in all_usb_name):
            logging.info('关闭板载USB槽，USB端口配置选项自动隐藏')
        else:
            stylelog.fail('关闭板载USB槽，USB端口配置选项没有自动隐藏')
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_USB_PORT, 18)
        data = SetUpLib.get_data(2)
        if all(not re.search(i, data) for i in all_usb_name):
            logging.info('关闭板载USB槽，USB端口配置选项自动隐藏')
        else:
            stylelog.fail('关闭板载USB槽，USB端口配置选项没有自动隐藏')
            count += 1
        if not re.search('USB', data.split('USB device list')[-1]):
            logging.info('关闭板载USB槽,USB设备列表不显示USB设备')
        else:
            stylelog.fail('关闭板载USB槽，USB设备列表仍显示USB设备')
            count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_USB_SLOT, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if count == 0:
            return True
        else:
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('113', '[TC113]PEU1[0:7]槽开关', 'PEU1[0:7]槽开关'))
def peu1_07_slot():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE1_07, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(1)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCIE_INFO, 18)
        data = SetUpLib.get_data(2)
        bdfs = re.findall('\w{2}\s{2}\w{2}\s{2}\w{2}', data)
        if not any(re.search('11  00', i) for i in bdfs):
            logging.info('PEU1[0:7]槽没有设备,跳过测试')
            return core.Status.Skip
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PUE1_07, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCIE_INFO, 18)
        data = SetUpLib.get_data(2)
        bdfs = re.findall('\w{2}\s{2}\w{2}\s{2}\w{2}', data)
        if not all(not re.search('11  00', i) for i in bdfs):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE1_07, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            logging.info('关闭PEU1[0:7]槽,PCIE设备列表不显示设备')
            return True
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE1_07, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            stylelog.fail('关闭PEU1[0:7]槽,PCIE设备列表仍显示设备')
            stylelog.fail(bdfs)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('114', '[TC114]PEU1[8:15]槽开关', 'PEU1[8:15]槽开关'))
def peu1_815_slot():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE1_815, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(1)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCIE_INFO, 18)
        data = SetUpLib.get_data(2)
        bdfs = re.findall('\w{2}\s{2}\w{2}\s{2}\w{2}', data)
        if not any(re.search('12  00', i) for i in bdfs):
            logging.info('PEU1[8:15]槽没有设备,跳过测试')
            return core.Status.Skip
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CLOSE_PUE1_815, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_PCIE_INFO, 18)
        data = SetUpLib.get_data(2)
        bdfs = re.findall('\w{2}\s{2}\w{2}\s{2}\w{2}', data)
        if not all(not re.search('12  00', i) for i in bdfs):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE1_815, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            logging.info('关闭PEU1[8:15]槽,PCIE设备列表不显示设备')
            return True
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_PUE1_815, 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            stylelog.fail('关闭PEU1[8:15]槽,PCIE设备列表仍显示设备')
            stylelog.fail(bdfs)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('115', '[TC115]HDD Bind', '硬盘绑定'))
def hdd_bind():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_HDD_BIND, 18)
        SetUpLib.clean_buffer()
        all_value = SetUpLib.get_value_list()
        if len(all_value) < 3:
            logging.info('硬盘数量小于2块，跳过测试')
            return core.Status.Skip
        all_value = all_value[1:]
        for index, value in enumerate(all_value):
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_HDD_BIND + [{'HDD Bind': value}], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(2)
            assert SetUpLib.boot_to_boot_menu()
            for i in all_value[:index] + all_value[index + 1:]:
                if SetUpLib.select_boot_option(Key.DOWN, i.replace('(', '\(').replace(')', '\)'), 30,
                                               SutConfig.Sup.BIND_MSG):
                    logging.info(f'绑定硬盘{value}，启动菜单无法进入{i}')
                else:
                    stylelog.fail(f'绑定硬盘{value}，启动菜单仍可以进入{i}')
                    wrong_msg.append(f'绑定硬盘{value}，启动菜单仍可以进入{i}')
                    count += 1
                assert SetUpLib.boot_to_boot_menu()
            assert SetUpLib.select_boot_option(Key.DOWN, value, 30, '')
            if not SetUpLib.wait_message(SutConfig.Sup.BIND_MSG, 10):
                logging.info(f'绑定硬盘{value},启动菜单成功进入{value}')
            else:
                stylelog.fail(f'绑定硬盘{value},启动菜单无法进入{value}')
                wrong_msg.append(f'绑定硬盘{value},启动菜单无法进入{value}')
                count += 1
            time.sleep(20)
            assert SetUpLib.boot_to_setup()
            for i in all_value[:index] + all_value[index + 1:]:
                assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_BOOT_MANAGER, 18)
                assert SetUpLib.locate_option(Key.DOWN, [i.replace('(', '\(').replace(')', '\)')], 18)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                if SetUpLib.wait_message(SutConfig.Sup.BIND_MSG, 15):
                    logging.info(f'绑定硬盘{value}，启动管理器无法进入{i}')
                else:
                    stylelog.fail(f'绑定硬盘{value}，启动管理器仍可以进入{i}')
                    wrong_msg.append(f'绑定硬盘{value}，启动管理器仍可以进入{i}')
                    count += 1
                assert SetUpLib.boot_to_setup()
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_BOOT_MANAGER, 18)
            assert SetUpLib.locate_option(Key.DOWN, [value.replace('(', '\(').replace(')', '\)')], 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            if not SetUpLib.wait_message(SutConfig.Sup.BIND_MSG, 10):
                logging.info(f'绑定硬盘{value},启动管理器成功进入{value}')
            else:
                stylelog.fail(f'绑定硬盘{value},启动管理器无法进入{value}')
                wrong_msg.append(f'绑定硬盘{value},启动管理器无法进入{value}')
                count += 1
            time.sleep(20)
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_HDD_UNBIND, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('116', '[TC116]Boot Watchdog', '系统定时器'))
def boot_watchdog():
    try:

        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_BOOT_ORDER_USB, 18)
        time.sleep(1)
        for i in range(0, 7):
            SetUpLib.send_key(Key.ADD)
            time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_WATCHDOG_1, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_USER_TIME_65, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            SetUpLib.reboot()
            assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        time.sleep(63)
        SetUpLib.send_key(Key.ENTER)
        if not SetUpLib.wait_message(SutConfig.Msg.SHELL_MSG, 5):
            logging.info('设置系统定时器时间为1分钟,POST界面停留1分钟后重启')
        else:
            stylelog.fail('设置系统定时器时间为1分钟,POST界面停留1分钟后没有重启')
            wrong_msg.append('设置系统定时器时间为1分钟,POST界面停留1分钟后没有重启')
            count += 1
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_WATCHDOG_3, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_USER_TIME_185, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            SetUpLib.reboot()
            assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        time.sleep(3)
        if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 120):
            logging.info('设置系统定时器时间为3分钟，POST界面停留2分钟后没有重启')
            time.sleep(60)
            SetUpLib.send_key(Key.ENTER)
            if not SetUpLib.wait_message(SutConfig.Msg.SHELL_MSG, 5):
                logging.info('设置系统定时器时间为3分钟,POST界面停留3分钟后重启')
            else:
                stylelog.fail('设置系统定时器时间为3分钟,POST界面停留3分钟后没有重启')
                wrong_msg.append('设置系统定时器时间为3分钟,POST界面停留3分钟后没有重启')
                count += 1
        else:
            stylelog.fail('设置系统定时器时间为3分钟，POST界面停留2分钟后重启')
            wrong_msg.append('设置系统定时器时间为3分钟，POST界面停留2分钟后重启')
            count += 1
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_WATCHDOG_5, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.SET_USER_TIME_305, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            SetUpLib.reboot()
            assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        time.sleep(2)
        if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE, 180):
            logging.info('设置系统定时器时间为5分钟，POST界面停留3分钟后没有重启')
            time.sleep(120)
            SetUpLib.send_key(Key.ENTER)
            if not SetUpLib.wait_message(SutConfig.Msg.SHELL_MSG, 5):
                logging.info('设置系统定时器时间为5分钟,POST界面停留5分钟后重启')
            else:
                stylelog.fail('设置系统定时器时间为5分钟,POST界面停留5分钟后没有重启')
                wrong_msg.append('设置系统定时器时间为5分钟,POST界面停留5分钟后没有重启')
                count += 1
        else:
            stylelog.fail('设置系统定时器时间为5分钟，POST界面停留3分钟后重启')
            wrong_msg.append('设置系统定时器时间为5分钟，POST界面停留3分钟后重启')
            count += 1
        assert SetUpLib.boot_to_setup()
        time.sleep(2)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('117', '[TC117]F9 Load Default', 'F9下恢复默认值测试'))
def load_default():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.CHANGE_OPTIONS, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(8)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        options = UpdateTest.get_options_value()
        default_options = SutConfig.Tool.DEFAULT_OPTION_VALUE
        if options == default_options:
            logging.info('F9恢复默认值成功')
            return True
        else:
            stylelog.fail('F9恢复默认值失败')
            for i in options:
                if i not in default_options:
                    logging.info('恢复后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in default_options:
                if i not in options:
                    logging.info('默认的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('118', '[TC118]Load Default', 'SetUp下恢复默认值测试'))
def load_default():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Tool.CHANGE_OPTIONS, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOAD_DEFAULT, 18)
        time.sleep(2)
        SetUpLib.send_key(Key.Y)
        time.sleep(5)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        options = UpdateTest.get_options_value()
        default_options = SutConfig.Tool.DEFAULT_OPTION_VALUE
        if options == default_options:
            logging.info('SetUp下恢复默认值成功')
            return True
        else:
            stylelog.fail('SetUp下恢复默认值失败')
            for i in options:
                if i not in default_options:
                    logging.info('恢复后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in default_options:
                if i not in options:
                    logging.info('默认的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('119', '[TC119]Save Change ESC', '通过ESC保存修改'))
def save_change_esc():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_OPTIONS, 18)
        time.sleep(1)
        SetUpLib.back_to_setup_toppage()
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.send_key(Key.Y)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        options = UpdateTest.get_options_value()
        print(options)
        changed_options = SutConfig.Sup.CHANGE_OPTION_NAME
        if options == changed_options:
            logging.info('ESC 保存修改成功')
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return True
        else:
            stylelog.fail('ESC 保存修改失败')
            for i in options:
                if i not in changed_options:
                    logging.info('ESC后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in changed_options:
                if i not in options:
                    logging.info('修改的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('120', '[TC120]Save Change F10', '通过F10保存修改'))
def save_change_f10():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_OPTIONS, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        options = UpdateTest.get_options_value()
        changed_options = SutConfig.Sup.CHANGE_OPTION_NAME
        if options == changed_options:
            logging.info('F10保存修改成功')
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return True
        else:
            stylelog.fail('F10保存修改失败')
            for i in options:
                if i not in changed_options:
                    logging.info('F10后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in changed_options:
                if i not in options:
                    logging.info('修改的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('121', '[TC121]Save Change SetUp', '通过SetUp保存修改'))
def save_change_setup():
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.CHANGE_OPTIONS, 18)
        time.sleep(1)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_SAVE_CHANGE, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        options = UpdateTest.get_options_value()
        changed_options = SutConfig.Sup.CHANGE_OPTION_NAME
        if options == changed_options:
            logging.info('Setup保存修改成功')
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return True
        else:
            stylelog.fail('Setup保存修改失败')
            for i in options:
                if i not in changed_options:
                    logging.info('Setup后选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            for i in changed_options:
                if i not in options:
                    logging.info('修改的选项{0}'.format(i.replace('<', '[').replace('>', ']')))
            SetUpLib.send_keys(Key.RESET_DEFAULT)
            time.sleep(5)
            SetUpLib.send_keys(Key.SAVE_RESET)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('122', '[TC122]Memory Speed', '修改内存频率'))
def change_mem_frequency():
    try:
        count = 0
        wrong_msg = []
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sup.LOC_MEM_SPEED + [SutConfig.Sup.MEM_SPEED_NAME], 18)
        time.sleep(1)
        mem_speeds = SetUpLib.get_value_list()
        assert SetUpLib.boot_to_setup()
        for speed in mem_speeds:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_MEM_SPEED + [
                {SutConfig.Sup.MEM_SPEED_NAME: speed}], 18)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(2)
            start = time.time()
            datas = ''
            while True:
                data = SetUpLib.get_data(1)
                datas += data
                if re.search(SutConfig.Msg.POST_MESSAGE, data):
                    break
                now = time.time()
                if now - start > 150:
                    break
            if re.search(f'Memory Speed : {speed}', datas):
                logging.info(f'修改内存频率为{speed}成功')
            else:
                stylelog.fail(f'修改内存频率为{speed}失败,内存频率为{re.findall("Memory Speed : ([0-9]+MHz)", datas)}')
                wrong_msg.append(f'修改内存频率为{speed}失败,内存频率为{re.findall("Memory Speed : ([0-9]+MHz)", datas)}')
                count += 1
            time.sleep(1)
            SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
            if not SetUpLib.wait_message(SutConfig.Msg.SETUP_MESSAGE, 30):
                assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(8)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('122', '[TC122]System Date and Tiem', '系统日期和时间'))
def system_date_time():
    try:
        count = 0
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_DATE_TIME, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('12')
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ADD)
        if SetUpLib.wait_message('\[01/   System Date', 2):
            logging.info('月份1-12')
        else:
            stylelog.fail('月份不是1-12')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('31')
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ADD)
        if SetUpLib.wait_message('   01/   System Date', 2):
            logging.info('日，1-31')
        else:
            stylelog.fail('日，不是1-31')
            count += 1
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('2000')
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.SUBTRACT)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message('2000\]', ):
            logging.info('年最小值为2000')
        else:
            stylelog.fail('年最小值不是2000')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('2099')
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.ADD)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(1)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ENTER)
        if SetUpLib.wait_message('2099\]', ):
            logging.info('年最大值为2099')
        else:
            stylelog.fail('年最大值不是2099')
            count += 1
        time.sleep(1)
        SetUpLib.send_key(Key.DOWN)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('23')
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ADD)
        if SetUpLib.wait_message('\[00:   System Time', 2):
            logging.info('时，0-23')
        else:
            stylelog.fail('时,不是0-23')
            count += 1
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data_enter('59')
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        time.sleep(1)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ADD)
        if SetUpLib.wait_message('  00:\s*System Time', 2):
            logging.info('分,0-59')
        else:
            stylelog.fail('分,不是0-59')
            count += 1
        if count == 0:
            return True
        else:
            return



    except Exception as e:
        logging.error(e)
        return core.Status.Fail
