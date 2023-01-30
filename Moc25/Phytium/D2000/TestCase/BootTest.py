# -*- encoding=utf8 -*-
import re, random
import time
import logging
from D2000.BaseLib import SetUpLib
from D2000.Config.PlatConfig import Key
from D2000.Config import SutConfig
from batf.Report import stylelog
from batf import core


@core.test_case(('001', '[TC001]POST信息检查', 'POST信息检查'))
def post_information():
    try:
        count = 0
        information = []
        assert SetUpLib.boot_to_setup()
        time.sleep(1)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        SetUpLib.send_key(Key.LEFT)
        data = SetUpLib.get_data(2)
        information += re.findall('Release Version\s*([0-9\.]+)', data)
        information += re.findall('BIOS Build Time\s*([0-9/]+)', data)
        information += re.findall('MAC address \d* *([0-9A-Z\-]+)', data)
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Boot.LOC_CPU, 10)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        information += re.findall('CPU Vendor\s*(\w+)', data)
        information += re.findall('CPU Type\s*([\w/]+)', data)
        information += re.findall('CPU frequency\s*(\w+ MHz)', data)
        information += re.findall('CPU Core count\s*(\d+)', data)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_MEM, 10)
        data = SetUpLib.get_data(2)
        information += re.findall('Module/Dram Manufacturer\s*([\w/]+)', data)
        information += re.findall('Size\s*(\w+ GB)', data)
        information += re.findall('Form Factor\s*(\w+)', data)
        information += re.findall('Total Memory size \(GB\)\s*(\d+GB)', data)
        information += re.findall('<(\d+MHz)>\s*Set Memory Frequency', data)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_USB, 10)
        data = SetUpLib.get_data(2, cleanup=False)
        if not re.findall('USB device list : (.*)', data):
            stylelog.fail('USB数据收集失败')
            return
        data = re.findall('USB device list : (.*)', data)[0]
        for i in re.findall('(?:\x1b\[\d+;\d+H){1}(\w[\w -:/]*[\w\)+])', data):
            if 'Mouse' in i:
                information = information + re.findall('USB *Mouse : (.*)', i.strip())
            if 'Keyboard' in i:
                information = information + re.findall('USB *Keyboard : (.*)', i.strip())
            if 'Storage' in i:
                information = information + re.findall('USB *Storage : (.*)', i.strip())
            if 'Others' in i:
                information = information + re.findall('USB *Others : (.*)', i.strip())
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.LOC_SATA_INFO, 18)
        data = SetUpLib.get_data(2, cleanup=False)
        for i in re.findall('(?:\x1b\[\d+;\d+H){1}SATA Drive \d\s+(?:\x1b\[\d+;\d+H){1}([\s\w\-\(\)]+)', data):
            if 'None' not in i:
                information.append(i.strip())
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_NVME, 18)
        data = SetUpLib.get_data(2)
        information += re.findall('([\s\w]+)SN:', data)
        SetUpLib.reboot()
        start_time = time.time()
        datas = ''
        while True:
            data = SetUpLib.get_data(1)
            datas += data
            if re.search(SutConfig.Msg.POST_MESSAGE, data):
                break
            now = time.time()
            spent_time = (now - start_time)
            if spent_time > 100:
                break
        data = ''.join(datas)
        print(information)
        for i in information:
            if i.replace(' ', '') in data.replace(' ', ''):
                logging.info('显示{0}'.format(i.strip()))
            else:
                if re.findall(': *(.+)\)', i):
                    if re.findall(': *(.+)\)', i)[0].replace(' ', '') in data.replace(' ', ''):
                        logging.info("显示{}".format(re.findall(': *(.+)\)', i)[0]))
                    else:
                        count += 1
                        stylelog.fail(i)
                else:
                    count += 1
                    stylelog.fail(i)
        if count != 0:
            return
        else:
            return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('002', '[TC002]快捷启动', '快捷启动'))
def quick_boot_hotkey():
    try:
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.SETUP_KEY, SutConfig.Msg.SETUP_MESSAGE, 150,
                                         SutConfig.Msg.POST_MESSAGE)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.OPEN_LAN, 18)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        logging.info('进入SetUp成功')
        assert SetUpLib.boot_with_hotkey(SutConfig.Msg.BOOTMENU_KEY, SutConfig.Msg.ENTER_BOOTMENU, 150,
                                         SutConfig.Msg.POST_MESSAGE)
        logging.info('进入启动菜单成功')
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Sup.PXE_MSG, 150, SutConfig.Msg.POST_MESSAGE)
        logging.info('进入网络启动成功')
        return True
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('003', '[TC003]Boot Order', '启动顺序'))
def boot_order():
    try:
        count = 0
        wrong_msg = []
        logging.info('UEFI模式启动顺序测试')
        BOOT_NAME_LIST_UEFI = SutConfig.Boot.BOOT_NAME_LIST_UEFI
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.OPEN_SHELL, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.OPEN_LAN, 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(2)
        assert SetUpLib.boot_to_setup()
        for index, name in enumerate(BOOT_NAME_LIST_UEFI):
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Boot.LOC_BOOT_ORDER, 18)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2, cleanup=False)
            option_list = re.findall('► (.*?) *(?:\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}', data)
            assert SetUpLib.locate_option(Key.DOWN, [name], 18)
            for i in range(0, 5):
                time.sleep(1)
                SetUpLib.send_key(Key.ADD)
            time.sleep(1)
            new_boot_name_list = BOOT_NAME_LIST_UEFI[0:index + 1][::-1] + BOOT_NAME_LIST_UEFI[index + 1:]
            order_name = []
            SetUpLib.send_key(Key.UP)
            SetUpLib.clean_buffer()
            for option in new_boot_name_list:
                if option in option_list:
                    if not SetUpLib.locate_option(Key.DOWN, [option], 7):
                        assert SetUpLib.locate_option(Key.UP, [option], 6)
                    value = SetUpLib.get_value_list()
                    if len(value) > 1:
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(1)
                        for j in range(2):
                            num = random.choice([i for i in range(0, len(value))])
                            for i in range(0, num):
                                SetUpLib.send_key(Key.DOWN)
                                time.sleep(1)
                            for i in range(0, num):
                                SetUpLib.send_key(Key.ADD)
                                time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        SetUpLib.clean_buffer()
                        order_name += SetUpLib.get_value_list()
                        time.sleep(1)
                    else:
                        order_name += value
                    time.sleep(1)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(2)
            data = SetUpLib.boot_to_boot_menu(True)
            changed_order_name = ''
            for order in order_name:
                if len(order) > 45:
                    changed_order_name += order[:45] + '...'
                else:
                    changed_order_name += order
            if changed_order_name in data.replace(SutConfig.Msg.ENTER_SETUP, ''):
                logging.info(f"修改启动顺序为:{''.join(order_name)},启动菜单验证成功")
            else:
                stylelog.fail(f"修改启动顺序为{''.join(order_name)},启动菜单验证失败")
                stylelog.fail(data)
                wrong_msg.append(f"修改启动顺序为{''.join(order_name)},启动菜单验证失败")
                stylelog.fail(data)
                count += 1
            assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)

            changed_order = ''
            for i in new_boot_name_list:
                changed_order += ' *►* *' + i + ' *'
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_BOOT_ORDER, 18)

            data = SetUpLib.get_data(3)
            if re.search(changed_order, data):
                logging.info(f'修改启动顺序为{new_boot_name_list},SetUp下验证成功')
            else:
                stylelog.fail(f'修改启动顺序为{new_boot_name_list},SetUp下验证失败')
                wrong_msg.append(f'修改启动顺序为{new_boot_name_list},SetUp下验证失败')
                count += 1
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_BOOT_MANAGER, 18)
            data = SetUpLib.get_data(2)
            if ''.join(order_name).replace(' ', '') in data.replace(' ', ''):
                logging.info(f"修改启动顺序为:{''.join(order_name)},启动管理器验证成功")

            else:
                stylelog.fail(f"修改启动顺序为:{''.join(order_name)},启动管理器验证失败")
                stylelog.fail(data)
                wrong_msg.append(f"修改启动顺序为{''.join(order_name)},启动管理器验证失败")
                stylelog.fail(data)
                count += 1
        time.sleep(1)
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        time.sleep(15)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
