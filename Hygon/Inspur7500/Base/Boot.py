# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *


def post_information():
    assert SetUpLib.boot_to_setup()
    information = []
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.LOC_USB, 10)
    data = SetUpLib.get_data(2, cleanup=False)
    if not re.findall('USB device list :(.*)USB Port', data):
        stylelog.fail('USB数据收集失败')
        return
    data = re.findall('USB device list :(.*)USB Port', data)[0]
    for i in re.findall('(?:\x1b\[\d+;\d+H){1}(\w[\w -:/]*[\w\)+])', data):
        if 'Mouse' in i:
            information = information + re.findall('USB *Mouse(.*)', i.strip())
        if 'Keyboard' in i:
            information = information + re.findall('USB *Keyboard(.*)', i.strip())
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.SERVICE_CONFIG, 10)
    information = information + re.findall(r'BMC Firmware Revision +([0-9\.]*) ', SetUpLib.get_data(2))
    assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Boot.LOC_HDD, 18)
    time.sleep(2)
    for i in SetUpLib.get_value_list():
        print(i)
        if re.search('\(UEFI', i):
            information.append(i)
    # information=information+SetUpLib.get_value_list()
    assert SetUpLib.back_to_setup_toppage()
    assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_ADVANCED)
    SetUpLib.send_key(Key.LEFT)
    information = information + re.findall(r'Onboard LAN[0|1] MAC Address +([A-Z0-9\-]+) ', SetUpLib.get_data(2))
    SetUpLib.send_key(Key.ENTER)
    data = SetUpLib.get_data(2)
    information = information + re.findall(r'Release Version +([0-9\.]+) ', data)
    information = information + re.findall(r'BIOS Build Time +([0-9\-]+) ', data)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.CPU_INFO, 5)
    data = SetUpLib.get_data(2)
    information = information + re.findall(r'CPU (?:Version|Mode|Model) +([0-9a-zA-Z \-]+?Processor) +', data)
    information = information + re.findall(r'CPU Frequency.*?([0-9]{4} MHz) +', data)
    SetUpLib.send_key(Key.ESC)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.MEM_INFO, 5)
    data = SetUpLib.get_data(2)
    information = information + re.findall(r'Manu:(.*?),', data)
    information = information + re.findall(r'Type:(.*?),', data)
    information = information + re.findall(r'Memory [a-zA-Z]* *Frequency.*?([0-9]{4} MHz)', data)
    information = information + re.findall(r'Total Memory.*?([0-9]+ GB)', data)
    information = information + re.findall(r'Total Memory Count.*?([0-9]{1,2})', data)
    SetUpLib.send_key(Key.ESC)
    BmcLib.init_sut()
    BmcLib.enable_serial_normal()
    start_time = time.time()
    datas = []
    while time.time() - start_time < 200:
        datas.append(SetUpLib.get_data(1))
        if re.search(SutConfig.Msg.POST_MESSAGE,''.join(datas)):
            datas.append(SetUpLib.get_data(2))
            break
    data = ''.join(datas)
    count = 0
    for i in information:
        if i.replace(' ', '') in data.replace(' ', ''):
            logging.info('显示{0}'.format(i))
        elif re.sub(' [ a-zA-Z0-9]+\(.*\):*', '', i).replace(' ', '') in data.replace(' ', ''):
            logging.info('显示{0}'.format(re.sub(' [ a-zA-Z0-9]+\(.*\):*', '', i)))
        elif re.sub('SATA\d{1,2}-\d{1,2}: ', '', re.sub('\(', ': ', i, 1)[:-1]).strip().replace(' ',
                                                                                                '') in data.replace(' ',
                                                                                                                    ''):
            logging.info('显示{0}'.format(i))
        else:
            count += 1
            stylelog.fail(i)
    if count != 0:
        return
    else:
        return True


# 快捷启动
def quick_boot_hotkey():
    assert SetUpLib.boot_with_hotkey(Key.DEL, SutConfig.Msg.PAGE_MAIN, 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('DEL进入SetUp成功')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.ONBOARD_ETH, 10)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Boot.PXE, 10, save=True)
    assert SetUpLib.boot_with_hotkey(Key.F11, SutConfig.Msg.ENTER_BOOTMENU, 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('F11进入启动菜单成功')
    assert SetUpLib.boot_with_hotkey(Key.F12, 'PXE', 150, SutConfig.Msg.POST_MESSAGE)
    logging.info('F12进入PXE成功')
    return True


def boot_order(oem):
    count = 0
    wrong_msg = []
    BOOT_NAME_LIST_UEFI = SutConfig.Boot.BOOT_NAME_LIST_UEFI
    BOOT_NAME_LIST_LEGACY = SutConfig.Boot.BOOT_NAME_LIST_LEGACY
    logging.info('UEFI模式启动顺序测试')
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Upd.OPEN_SHELL, 18)
    for index, name in enumerate(BOOT_NAME_LIST_UEFI):
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
        data = SetUpLib.get_data(5, cleanup=False)
        option_list = re.findall('(?:►|>) (\w.+?) *(?:\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}', data)
        assert SetUpLib.locate_option(Key.DOWN, [name], 18)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        new_boot_name_list = BOOT_NAME_LIST_UEFI[0:index + 1][::-1] + BOOT_NAME_LIST_UEFI[index + 1:]
        order_name = []
        SetUpLib.send_key(Key.UP)
        SetUpLib.clean_buffer()
        for option in new_boot_name_list:
            if option in option_list:
                if not SetUpLib.locate_option(Key.DOWN, [option], 15):
                    assert SetUpLib.locate_option(Key.UP, [option], 16)
                value = SetUpLib.get_value_list()
                if len(value) > 1:
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    for j in range(2):
                        num = random.choice([i for i in range(0, len(value))])
                        SetUpLib.send_keys([Key.DOWN] * num)
                        SetUpLib.send_keys([Key.ADD] * num)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    SetUpLib.clean_buffer()
                    time.sleep(1)
                    order_name += SetUpLib.get_value_list()
                    time.sleep(1)
                else:
                    order_name += value
                time.sleep(1)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        data = SetUpLib.boot_to_boot_menu(True)
        if ''.join(order_name) in data:
            logging.info(f"修改启动顺序为:{''.join(order_name)},启动菜单验证成功")
        else:
            stylelog.fail(f"修改启动顺序为{''.join(order_name)},启动菜单验证失败")
            stylelog.fail(data)
            wrong_msg.append(f"修改启动顺序为{''.join(order_name)},启动菜单验证失败")
            stylelog.fail(data)
            count += 1
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        changed_order = ''
        for i in new_boot_name_list:
            changed_order += i + '.*'
        SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
        data = SetUpLib.get_data(5,scroll=True).split('Boot Order')[-2].replace('►','').replace('>','')
        if re.search(changed_order, data):
            logging.info(f'修改启动顺序为{new_boot_name_list},SetUp下验证成功')
        else:
            stylelog.fail(f'修改启动顺序为{new_boot_name_list},SetUp下验证失败')
            wrong_msg.append(f'修改启动顺序为{new_boot_name_list},SetUp下验证失败')
            count += 1
    logging.info('Legacy模式启动顺序测试')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Pxe.SET_LEGACY, 18, save=True)
    assert SetUpLib.boot_to_setup()
    for index, name in enumerate(BOOT_NAME_LIST_LEGACY):
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
        data = SetUpLib.get_data(5, cleanup=False)
        option_list = re.findall('(?:►|>) (.*?) *(?:\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}', data)
        assert SetUpLib.locate_option(Key.DOWN, [name], 18)
        SetUpLib.send_keys([Key.ADD] * 5)
        time.sleep(1)
        new_boot_name_list = BOOT_NAME_LIST_LEGACY[0:index + 1][::-1] + BOOT_NAME_LIST_LEGACY[index + 1:]
        order_name = []
        SetUpLib.send_key(Key.UP)
        SetUpLib.clean_buffer()
        for option in new_boot_name_list:
            if option in option_list:
                if not SetUpLib.locate_option(Key.DOWN, [option], 15):
                    assert SetUpLib.locate_option(Key.UP, [option], 16)
                value = SetUpLib.get_value_list()
                if len(value) > 1:
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    for j in range(2):
                        num = random.choice([i for i in range(0, len(value))])
                        SetUpLib.send_keys([Key.DOWN] * num)
                        SetUpLib.send_keys([Key.ADD] * num)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    SetUpLib.clean_buffer()
                    order_name += SetUpLib.get_value_list()
                else:
                    order_name += value
                time.sleep(2)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        data = SetUpLib.boot_to_boot_menu(True)
        if ''.join(order_name) in data:
            logging.info(f"修改启动顺序为:{''.join(order_name)},启动菜单验证成功")
        else:
            stylelog.fail(f"修改启动顺序为{''.join(order_name)},启动菜单验证失败")
            stylelog.fail(data)
            wrong_msg.append(f"修改启动顺序为{''.join(order_name)},启动菜单验证失败")
            stylelog.fail(data)
            count += 1
        assert SetUpLib.select_boot_option(Key.DOWN, SutConfig.Msg.ENTER_SETUP, 30, SutConfig.Msg.PAGE_MAIN)
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        changed_order = ''
        for i in new_boot_name_list:
            changed_order += i + '.*'
        SetUpLib.send_key(Key.RIGHT)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.LEFT)
        data = SetUpLib.get_data(5,scroll=True).split('Boot Order')[-1].replace('►','').replace('>','')
        if re.search(changed_order, data):
            logging.info(f'修改启动顺序为{new_boot_name_list},SetUp下验证成功')
        else:
            stylelog.fail(f'修改启动顺序为{new_boot_name_list},SetUp下验证失败')
            wrong_msg.append(f'修改启动顺序为{new_boot_name_list},SetUp下验证失败')
            count += 1
    SetUpLib.default_save()
    if oem is True:
        assert SetUpLib.boot_to_setup()
        changed_order_uefi_setup = ''
        changed_order_legacy_setup = ''
        boot_dict = {'HDD': SutConfig.Msg.HDD_BOOT_NAME, 'PXE': SutConfig.Msg.PXE_BOOT_NAME,
                     'USB': SutConfig.Msg.USB_BOOT_NAME, 'ODD': SutConfig.Msg.ODD_BOOT_NAME,
                     'Others': SutConfig.Msg.OTHER_BOOT_NAME}
        changed_order_uefi = list(set(boot_dict.keys()))
        changed_order_legacy = list(set(list(boot_dict.keys())[:-1]))
        BmcLib.change_bios_value(['BootMode:UEFI', f'First:{changed_order_uefi[0]}', f'Second:{changed_order_uefi[1]}',
                                  f'Third:{changed_order_uefi[2]}', f'Fourth:{changed_order_uefi[3]}',
                                  f'Fifth:{changed_order_uefi[4]}'])
        for i in changed_order_uefi:
            changed_order_uefi_setup += boot_dict[i] + '.*'
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        SetUpLib.send_keys([Key.RIGHT, Key.LEFT])
        data = SetUpLib.get_data(5,scroll=True).split('Boot Order')[-2].replace('►','').replace('>','')
        if re.search(changed_order_uefi_setup, data):
            logging.info(f'UEFI,OEM命令修改启动顺序为{changed_order_uefi},SetUp下验证成功')
        else:
            stylelog.fail(f'UEFI,OEM命令修改启动顺序为{changed_order_uefi},SetUp下验证失败')
            wrong_msg.append(f'UEFI,OEM命令修改启动顺序为{changed_order_uefi},SetUp下验证失败')
            count += 1

        BmcLib.change_bios_value(
            ['BootMode:Legacy', f'First:{changed_order_legacy[0]}', f'Second:{changed_order_legacy[1]}',
             f'Third:{changed_order_legacy[2]}', f'Fourth:{changed_order_legacy[3]}',
             'Fifth:Others'])
        for i in changed_order_legacy:
            changed_order_legacy_setup +=boot_dict[i] + '.*'
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_BOOT)
        SetUpLib.send_key(Key.RIGHT)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.LEFT)
        data = SetUpLib.get_data(5,scroll=True).split('Boot Order')[-1].replace('►','').replace('>','')
        if re.search(changed_order_legacy_setup, data):
            logging.info(f'Legacy,OEM命令修改启动顺序为{changed_order_legacy},SetUp下验证成功')
        else:
            stylelog.fail(f'Legacy,OEM命令修改启动顺序为{changed_order_legacy},SetUp下验证失败')
            wrong_msg.append(f'Legacy,OEM命令修改启动顺序为{changed_order_legacy},SetUp下验证失败')
            count += 1
        SetUpLib.default_save()
        time.sleep(15)
    if count == 0:
        return True
    else:
        for i in wrong_msg:
            stylelog.fail(i)
        return
