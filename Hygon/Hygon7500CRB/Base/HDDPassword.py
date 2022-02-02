#coding='utf-8'
import datetime
from typing import Set
import re
import time
import logging
from Hygon7500CRB.BaseLib import BmcLib, SetUpLib
from Hygon7500CRB.Config.PlatConfig import Key
from Hygon7500CRB.Config import SutConfig, Sut01Config
from batf.SutInit import Sut
from batf.Report import stylelog



#硬盘顺序与设置硬盘密码时的顺序对应,每个硬盘系统对应
HDD_NAME_01=Sut01Config.Msg.HDD_PASSWORD_NAME_01
HDD_NAME_01_OS=SutConfig.Msg.HDD_NAME_01_OS
HDD_NAME_02=SutConfig.Msg.HDD_PASSWORD_NAME_02
HDD_NAME_02_OS=SutConfig.Msg.HDD_NAME_02_OS
# HDD_NAME_03=SutConfig.Msg.HDD_PASSWORD_NAME_03



def del_hdd_password(password):
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.F2, Sut01Config.Msg.SEL_LANG, 150, Sut01Config.Msg.HOTKEY_PROMPT_DEL_CN):
        time.sleep(2)
        SetUpLib.send_data(password)
        time.sleep(1)
        if SetUpLib.wait_message_enter(Sut01Config.Msg.POST_MESSAGE):
            SetUpLib.send_key(Key.F2)
        else:
            return
        if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG,30):
            logging.info('进入setup')
        else:
            return
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
        try_counts=3
        while try_counts:
            time.sleep(3)
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            if SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],4):
                break
            else:
                time.sleep(1)
                SetUpLib.send_key(Key.ESC)
                time.sleep(2)
                SetUpLib.send_key(Key.DOWN)
                try_counts-=1
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_data(password)
        time.sleep(1)
        if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
            logging.info('密码删除')
        else:
            return
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.ESC)
        time.sleep(2)
        SetUpLib.send_key(Key.RIGHT)
        time.sleep(1)
        return True
    else:
        logging.info("SetUpLib: Boot to setup main page successfully")
        return True



def del_hdd_password_two():
    logging.info("SetUpLib: Boot to setup main page")
    if not BmcLib.init_sut():
        stylelog.fail("SetUpLib: Rebooting SUT Failed.")
        return
    logging.info("SetUpLib: Booting to setup")
    logging.info("Waiting for Hotkey message found...")
    if not SetUpLib.boot_with_hotkey_only(Key.F2, SutConfig.Msg.SEL_LANG, 150, SutConfig.Msg.HOTKEY_PROMPT_DEL_CN):
        SetUpLib.send_data('hdd123@1')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(4)
        if re.search(Sut01Config.Msg.LOGIN_HDD_PSW_PROMPT, data):
            SetUpLib.send_data('hdd123@22')
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
                logging.info('两个硬盘')
                hdd_count = 'two'
                SetUpLib.send_key(Key.F2)
        elif re.search(SutConfig.Msg.LOGIN_HDD_PSW_FAIL, data):
            SetUpLib.send_key(Key.ENTER)
            time.sleep(1)
            SetUpLib.send_data('hdd123@22')
            if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT, 5):
                SetUpLib.send_data('hdd123@1')
                time.sleep(1)
                if SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
                    logging.info('两个硬盘')
                    hdd_count = 'two'
                    SetUpLib.send_key(Key.F2)
            else:
                if SetUpLib.wait_message('CPU Info', 60):
                    logging.info('只有一个硬盘密码')
                    hdd_count = 'one'
                    password = 'hdd123@22'
                    SetUpLib.send_key(Key.F2)
        else:
            if SetUpLib.wait_message('CPU Info', 60):
                logging.info('只有一个硬盘密码')
                hdd_count = 'one'
                password = 'hdd123@1'
                SetUpLib.send_key(Key.F2)
        if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG, 30):
            logging.info('进入setup')
        else:
            return
        if hdd_count == 'two':
            count = 0
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
            time.sleep(3)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.locate_option(Key.DOWN, [Sut01Config.Msg.DEL_HDD_PSW_OPTION], 4):
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_data('hdd123@1')
                time.sleep(1)
                if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                    logging.info('第一个硬盘密码删除')
                    count += 1
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                else:
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(2)
                    SetUpLib.send_data('hdd123@22')
                    time.sleep(1)
                    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                        logging.info('第一个硬盘密码删除')
                        count += 1
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                    else:
                        return
            time.sleep(2)
            SetUpLib.send_key(Key.ESC)
            time.sleep(2)
            SetUpLib.send_key(Key.DOWN)
            time.sleep(2)
            SetUpLib.send_key(Key.ENTER)
            if SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.DEL_HDD_PSW_OPTION], 4):
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_data('hdd123@22')
                time.sleep(1)
                if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                    logging.info('第二个硬盘密码删除')
                    count += 1
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                else:
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(2)
                    SetUpLib.send_data('hdd123@1')
                    time.sleep(1)
                    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                        logging.info('第二个硬盘密码删除')
                        count += 1
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                    else:
                        return
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            if count == 2:
                time.sleep(2)
                SetUpLib.send_key(Key.ESC)
                time.sleep(2)
                SetUpLib.send_key(Key.RIGHT)
                time.sleep(1)
                return True
            else:
                time.sleep(2)
                SetUpLib.send_key(Key.DOWN)
                time.sleep(2)
                SetUpLib.send_key(Key.ENTER)
                if SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.DEL_HDD_PSW_OPTION], 4):
                    SetUpLib.send_key(Key.ENTER)
                    time.sleep(1)
                    SetUpLib.send_data('hdd123@22')
                    time.sleep(1)
                    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                        logging.info('第二个硬盘密码删除')
                        count += 1
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                    else:
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(2)
                        SetUpLib.send_data('hdd123@1')
                        time.sleep(1)
                        if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                            logging.info('第二个硬盘密码删除')
                            count += 1
                            time.sleep(1)
                            SetUpLib.send_key(Key.ENTER)
                        else:
                            return
                time.sleep(1)
                SetUpLib.send_key(Key.ESC)
                if count == 2:
                    time.sleep(2)
                    SetUpLib.send_key(Key.ESC)
                    time.sleep(2)
                    SetUpLib.send_key(Key.RIGHT)
                    time.sleep(1)
                    return True
                else:
                    return
        else:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
            try_counts = 3
            while try_counts:
                time.sleep(3)
                SetUpLib.send_key(Key.ENTER)
                if SetUpLib.locate_option(Key.DOWN, [SutConfig.Msg.DEL_HDD_PSW_OPTION], 3):
                    break
                else:
                    time.sleep(1)
                    SetUpLib.send_key(Key.ESC)
                    time.sleep(2)
                    SetUpLib.send_key(Key.DOWN)
                    try_counts -= 1
            SetUpLib.send_key(Key.ENTER)
            time.sleep(2)
            SetUpLib.send_data('hdd123@1')
            time.sleep(1)
            if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
                logging.info('硬盘密码删除')
                SetUpLib.send_key(Key.ENTER)
            else:
                return
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.ESC)
            time.sleep(1)
            SetUpLib.send_key(Key.RIGHT)
            time.sleep(1)
            return True
    else:
        logging.info("SetUpLib: Boot to setup main page successfully")
        return True



#设置硬盘密码长度小于最少字符数，大于最大字符，设置密码时两次输入不一致，
#只有数字，只有字母，只有特殊符号，数字和特殊符号，字母和特殊符号设置失败测试
def hdd_password_001(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    logging.info('硬盘密码长度小于最少字符数测试,符合复杂度........')
    
    time.sleep(1)
    SetUpLib.send_data_enter('hdd00@1')
    time.sleep(1)
    SetUpLib.send_data('hdd00@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_LENGTH_NOT_ENOUGH, 10):
        logging.info('长度小于最少字符数，硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    logging.info('设置密码时两次输入不一致测试..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(2)
    SetUpLib.send_data('hdd11111')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_NEW_OLD_PSW_DIFF, 10):
        logging.info('设置密码时两次输入不一致,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    logging.info('硬盘密码只有数字测试，符合最大长度..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data_enter('12345678901234567890123456789012')
    time.sleep(2)
    SetUpLib.send_data('12345678901234567890123456789012')
    if SetUpLib.wait_message_enter(Sut01Config.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 10):
        logging.info('设置密码只有数字,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    logging.info('硬盘密码只有字母测试，符合最小长度..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('abcdefgh')
    time.sleep(2)
    SetUpLib.send_data('abcdefgh')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 10):
        logging.info('设置密码只有字母,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    logging.info('硬盘密码只有特殊字符测试..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('!!!!!!!!')
    time.sleep(2)
    SetUpLib.send_data('!!!!!!!!')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 10):
        logging.info('设置密码只有特殊字符,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    logging.info('硬盘密码数字和特殊字符测试..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('12345!!!')
    time.sleep(2)
    SetUpLib.send_data('12345!!!')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 10):
        logging.info('设置密码数字和特殊字符,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    logging.info('硬盘密码字母和特殊字符测试..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('abcde!!!')
    time.sleep(2)
    SetUpLib.send_data('abcde!!!')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 10):
        logging.info('设置密码字母和特殊字符,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    logging.info('硬盘密码字母和数字测试..........')
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd12345')
    time.sleep(2)
    SetUpLib.send_data('hdd12345')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 10):
        logging.info('设置密码字母和数字,硬盘密码设置失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    return True



#设置硬盘密码长度等于最小字符数，设置成功测试（测试用密码'hdd123@1'）
def hdd_password_002(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert SetUpLib.boot_to_setup()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    logging.info('硬盘密码长度最小，复杂度最小测试..............')
    
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    time.sleep(5)
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd111@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入错误密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        logging.info('输入错误密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True
    


#设置硬盘密码长度等于最小字符数，最大复杂度，设置成功测试
def hdd_password_003(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    logging.info('硬盘密码长度最小，复杂度最大测试..............')
    time.sleep(1)
    SetUpLib.send_data_enter('Hdd1234@')
    time.sleep(1)    
    SetUpLib.send_data('Hdd1234@')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd111@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入错误密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入错误密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('Hdd1234@')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('Hdd1234@')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#设置硬盘密码长度大于最小字符数，小于最大字符数，设置成功测试（测试用密码'hdd123@22789'）
def hdd_password_004(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('Hdd1234@')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    logging.info('硬盘密码大于最小字符数，小于最大字符数测试..............')
   
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@22789')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@22789')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码大于最小字符数，小于最大字符数成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd111@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入错误密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入错误密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22789')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@22789')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#设置硬盘密码长度等于最大字符数，复杂度最小，设置成功测试(测试用密码'hdd123@2278901234567')
def hdd_password_005(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@22789')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    logging.info('硬盘密码等于长度最大，复杂度最小测试..............')
    
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@2278901234567890123456789')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@2278901234567890123456789')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd111@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入错误密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入错误密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@2278901234567890123456789')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@2278901234567890123456789')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#设置硬盘密码长度等于最大字符数，复杂度最大，设置成功测试(测试用密码'hdd123@227890!@#$%^&')
def hdd_password_006(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@2278901234567890123456789')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    logging.info('硬盘密码等于长度最大，复杂度最大测试..............')
    
    time.sleep(2)
    SetUpLib.send_data_enter('hdd123@227890123456789012!@#$%^&')
    time.sleep(2)
    SetUpLib.send_data('hdd123@227890123456789012!@#$%^&')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd111@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入错误密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入错误密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@227890123456789012!@#$%^&')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@227890123456789012!@#$%^&')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#禁用硬盘密码测试
def hdd_password_007(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@227890123456789012!@#$%^&')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('hdd1111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_HDD_PSW_ERROR,5):
        logging.info('禁用密码时输入错误的密码，提示密码无效')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('禁用密码时输入错误的密码没有提示密码无效')
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('禁用密码时输入正确的密码，成功禁用密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return True
    else:
        logging.info('禁用密码时输入正确的密码，没有成功禁用密码')
        return



#修改硬盘密码测试，修改为最小长度，最小复杂度，修改成功测试
def hdd_password_008(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Enter Current Password',3):
        time.sleep(1)
        SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data_enter('hdd111@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd111@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('修改硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入修改前的密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入修改前的密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入修改后的密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_HDD_PSW_ERROR,5):
        logging.info('输入修改前的密码无效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#修改硬盘密码测试，修改为最大长度，最大复杂度，修改成功测试
def hdd_password_009(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd111@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Enter Current Password',3):
        time.sleep(1)
        SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@227890123456789012!@#$%^&')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@227890123456789012!@#$%^&')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('修改硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入修改前的密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入修改前的密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@227890123456789012!@#$%^&')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入修改后的密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.DEL_HDD_PSW_ERROR,5):
        logging.info('输入修改前的密码无效')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(2)
    SetUpLib.send_data('hdd123@227890123456789012!@#$%^&')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#修改硬盘密码测试，修改为符合长度要求，不符合复杂度要求；符合复杂度要求，不符合长度要求；新密码和确认密码不同，修改失败测试
def hdd_password_010(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
    elif hddorder==2:
        hddname=HDD_NAME_02
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@227890123456789012!@#$%^&')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    logging.info('修改硬盘密码为符合长度要求，不符合复杂度要求测试..................')
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Enter Current Password',3):
        time.sleep(1)
        SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data_enter('hdd12345')
    time.sleep(1)    
    SetUpLib.send_data('hdd12345')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_TYPE_NOT_ENOUGH, 5):
        logging.info('修改硬盘密码为符合长度要求，不符合复杂度要求失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    logging.info('修改硬盘密码为符合复杂度要求，不符合长度要求测试..................')
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Enter Current Password', 3):
        time.sleep(1)
        SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_CHARACTERS_LENGTH_NOT_ENOUGH, 5):
        logging.info('修改硬盘密码为符合复杂度要求，不符合长度要求失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    logging.info('修改硬盘密码新密码和确认密码不同，修改失败测试..................')
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Enter Current Password', 3):
        time.sleep(1)
        SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data_enter('hdd111@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_NEW_OLD_PSW_DIFF, 5):
        logging.info('修改硬盘密码新密码和确认密码不同，修改失败')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message('Enter Current Password', 3):
        time.sleep(1)
        SetUpLib.send_data_enter('hdd123@1')
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#设置硬盘密码进入系统测试
def hdd_password_011(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
        hddos=HDD_NAME_01_OS
    elif hddorder==2:
        hddname=HDD_NAME_02
        hddos=HDD_NAME_02_OS
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F7)
    else:
        stylelog.fail('输入正确密码，没有进入')
        return
    if SetUpLib.wait_message(Sut01Config.Msg.ENTER_BOOTMENU_CN):
        logging.info('进入启动菜单')
    else:
        stylelog.fail('没有进入启动菜单')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,hddos[0],20,'')
    if BmcLib.ping_sut():
        logging.info('第一次成功进入系统')
    else:
        stylelog.fail('第一次没有进入系统')
        return
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F7)
    else:
        stylelog.fail('输入正确密码，没有进入')
        return
    if SetUpLib.wait_message(SutConfig.Msg.ENTER_BOOTMENU_CN,10):
        logging.info('进入启动菜单')
    else:
        stylelog.fail('没有进入启动菜单')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,hddos[0],20,'')
    if BmcLib.ping_sut():
        logging.info('第二次成功进入系统')
    else:
        stylelog.fail('第二次没有进入系统')
        return
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(3)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#硬盘密码输错测试
def hdd_password_012(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
        hddos=HDD_NAME_01_OS
    elif hddorder==2:
        hddname=HDD_NAME_02
        hddos=HDD_NAME_02_OS
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(hddos[0]).findall(data):
        logging.info('密码输错三次，启动项中没有硬盘')
    else:
        stylelog.fail('密码输错三次，启动项仍有硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5):
        logging.info('输错三次硬盘密码进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('第三次输入正确密码，成功进入')
        time.sleep(1)
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#硬盘密码输入时按ESC测试
def hdd_password_013(hddorder):
    if hddorder==1:
        hddname=HDD_NAME_01
        hddos=HDD_NAME_01_OS
    elif hddorder==2:
        hddname=HDD_NAME_02
        hddos=HDD_NAME_02_OS
    # elif hddorder==3:
    #     hddname=HDD_NAME_03
    else:
        stylelog.fail('hddorder有误')
        return
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_key(Key.ESC)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_ESC_LOCK_PROMPT,5):
        logging.info('输入密码时按ESC提示驱动器仍处于锁定状态')
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(hddos[0]).findall(data):
        logging.info('输入密码时按ESC，启动项中没有硬盘')
    else:
        stylelog.fail('输入密码时按ESC，启动项仍有硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,2):
        logging.info('输入密码时按ESC进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        time.sleep(1)
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[hddname],3):
        if not SetUpLib.locate_option(Key.UP,[hddname],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#多硬盘密码测试
def hdd_password_014():
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password('hdd123@1')
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@22')
    time.sleep(1)    
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入其它硬盘密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入其他硬盘密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(HDD_NAME_02):
        logging.info('输入第一个硬盘密码，成功进入第一个硬盘，要求输入第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('输入其它硬盘密码，提示密码错误')
        SetUpLib.send_key(Key.ENTER)
    else:
        stylelog.fail('输入其他硬盘密码，没有提示密码错误')
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        time.sleep(1)
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#多硬盘密码输错测试
def hdd_password_015():
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password_two()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@22')
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
#第一个硬盘密码输错测试
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    logging.info('第一个硬盘密码输错测试.............................................................')
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if SetUpLib.wait_message(HDD_NAME_02):
        logging.info('第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘密码输错三次，启动项中没有该硬盘')
    else:
        stylelog.fail('第一个硬盘密码输错三次，启动项仍有硬盘')
        return
    if re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第二个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第一个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(3)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.DEL_HDD_PSW_OPTION,5,readline=True):
        logging.info('第二个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
#第二个硬盘密码输错测试
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    logging.info('第二个硬盘密码输错测试.......................................................')
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(HDD_NAME_02,10):
        logging.info('第二个硬盘密码')
    else:
        return
    time.sleep(1)

    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘密码输错三次，启动项中没有该硬盘')
    else:
        stylelog.fail('第二个硬盘密码输错三次，启动项仍有硬盘')
        return
    if re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第一个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第二个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.DEL_HDD_PSW_OPTION,5):
        logging.info('第一个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
#两个硬盘密码输错测试
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    logging.info('两个硬盘密码输错测试.......................................................')
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错')
        time.sleep(1)
    else:
        return
    if SetUpLib.wait_message_enter(HDD_NAME_02,10):
        logging.info('第二个硬盘')
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘密码输错三次，启动项中没有该硬盘')
    else:
        stylelog.fail('第一个硬盘密码输错三次，启动项中仍有该硬盘')
        return
    if not re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘密码输错三次，启动项中没有该硬盘')
    else:
        stylelog.fail('第二个硬盘密码输错三次，启动项中仍有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第一个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第二个硬盘输错密码三次进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(HDD_NAME_02):
        logging.info('第三次输入第一个硬盘密码，成功进入第一个硬盘，要求输入第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[Sut01Config.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True



#多硬盘密码输入时按ESC测试
def hdd_password_016():
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password_two()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@22')
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
#第一个硬盘密码输入时按ESC测试
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    logging.info('第一个硬盘密码输入时按ESC测试.............................................................')
    SetUpLib.send_key(Key.ESC)
    if SetUpLib.wait_message(Sut01Config.Msg.HDD_ESC_LOCK_PROMPT,10):
        logging.info('第一个硬盘密码输入时按ESC，提示驱动器处于锁定状态')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(HDD_NAME_02):
        logging.info('第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘密码输入时按ESC，启动项中没有该硬盘')
    else:
        stylelog.fail('第一个硬盘密码输入时按ESC，启动项仍有硬盘')
        return
    if re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第二个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第一个硬盘输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(Sut01Config.Msg.DEL_HDD_PSW_OPTION,5,readline=True):
        logging.info('第二个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
#第二个硬盘密码输入时按ESC测试
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    logging.info('第二个硬盘密码输入时按ESC测试.......................................................')
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(HDD_NAME_02,10):
        logging.info('第二个硬盘密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_ESC_LOCK_PROMPT,10):
        logging.info('第二个硬盘输入时按ESC提示驱动器处于锁定状态')
        SetUpLib.send_key(Key.ENTER)
    else:
        return

    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘密码输入时按ESC，启动项中没有该硬盘')
    else:
        stylelog.fail('第二个硬盘密码输入时按ESC，启动项仍有硬盘')
        return
    if re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第一个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第二个硬盘输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(Sut01Config.Msg.DEL_HDD_PSW_OPTION,5,readline=True):
        logging.info('第一个硬盘输入正确密码进入setup，可以设置该硬盘的硬盘密码')
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
#两个硬盘密码输入时按ESC测试
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    logging.info('两个硬盘密码输入按ESC测试.......................................................')
    
    SetUpLib.send_key(Key.ESC)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_ESC_LOCK_PROMPT,10):
        logging.info('第一个硬盘输入时按ESC，提示驱动器处于锁定状态')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if SetUpLib.wait_message(HDD_NAME_02,10):
        logging.info('第二个硬盘')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_ESC_LOCK_PROMPT,10):
        logging.info('第二个硬盘密码输入时按ESC提示驱动器处于锁定状态')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if  SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘密码输入时按ESC，启动项中没有该硬盘')
    else:
        stylelog.fail('第一个硬盘密码输入时按ESC，启动项中仍有该硬盘')
        return
    if not re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘密码输入时按ESC，启动项中没有该硬盘')
    else:
        stylelog.fail('第二个硬盘密码输入时按ESC，启动项中仍有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,'Enter Setup',20,SutConfig.Msg.SEL_LANG)
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第一个硬盘密码输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if SetUpLib.wait_message(SutConfig.Msg.HDD_LOCK_STATUS,5,readline=True):
        logging.info('第二个硬盘密码输入时按ESC进入setup，无法设置该硬盘的硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(5)
    BmcLib.power_on()
    if not SetUpLib.wait_message(HDD_NAME_01):
        BmcLib.init_sut()
        assert SetUpLib.wait_message(HDD_NAME_01)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(HDD_NAME_02):
        logging.info('输入第一个硬盘密码，成功进入第一个硬盘，要求输入第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True

    

#多硬盘密码进入系统测试
def hdd_password_017():
    BmcLib.power_off()
    time.sleep(5)
    assert del_hdd_password_two()
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@1')
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_key(Key.ESC)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    if not SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
        if not SetUpLib.locate_option(Key.UP,[SutConfig.Msg.SET_HDD_PSW_OPTION],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data_enter('hdd123@22')
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS, 5):
        logging.info('设置硬盘密码成功')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_keys(Key.SAVE_RESET)
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(8)
    BmcLib.power_on()
    time.sleep(5)
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        time.sleep(5)
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错,第一个硬盘密码输错三次，硬盘被锁定')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        logging.info('第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if not re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘密码输错三次，启动项中没有该硬盘')
    else:
        stylelog.fail('第一个硬盘密码输错三次，启动项仍有硬盘')
        return
    if re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第二个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,HDD_NAME_02_OS[0],20,'')
    logging.info('第二个硬盘第一次成功进入系统')
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(8)
    BmcLib.power_on()
    time.sleep(5)
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        time.sleep(5)
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        logging.info('第一个硬盘正确输入密码成功')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd111@1')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第一次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd222@2')
    time.sleep(1)
    if SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_FAIL,10):
        logging.info('密码第二次输错')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    time.sleep(1)
    SetUpLib.send_data('hdd333@3')
    if SetUpLib.wait_message_enter(SutConfig.Msg.HDD_LOCK_PROMPT,10):
        logging.info('密码第三次输错,第二个硬盘密码输错三次，硬盘被锁定')
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    else:
        return
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    if not re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘密码输错三次，启动项中没有该硬盘')
    else:
        stylelog.fail('第二个硬盘密码输错三次，启动项仍有硬盘')
        return
    if re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第一个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,HDD_NAME_01_OS[0],20,'')
    logging.info('第一个硬盘第一次成功进入系统')
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(8)
    BmcLib.power_on()
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        time.sleep(5)
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        logging.info('第一个硬盘正确输入密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    logging.info('第二个硬盘密码输入正确的密码')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if  re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第一个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    if re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第二个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,HDD_NAME_01_OS[0],20,'')
    if BmcLib.ping_sut():
        logging.info('第一个硬盘第二次成功进入系统')
    else:
        stylelog.fail('第一个硬盘第二次没有进入系统')
        return
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(8)
    BmcLib.power_on()
    time.sleep(5)
    if not SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        time.sleep(5)
        assert SetUpLib.wait_message(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        logging.info('第一个硬盘正确输入密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    logging.info('第二个硬盘密码输入正确的密码')
    time.sleep(1)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        data=SetUpLib.get_data(10,Key.F7)
    else:
        return
    if  re.compile(HDD_NAME_01_OS[0]).findall(data):
        logging.info('第一个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第一个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    if re.compile(HDD_NAME_02_OS[0]).findall(data):
        logging.info('第二个硬盘输入正确的密码，启动项中有该硬盘')
    else:
        stylelog.fail('第二个硬盘输入正确的密码，启动项中没有该硬盘')
        return
    assert SetUpLib.select_boot_option(Key.DOWN,HDD_NAME_02_OS[0],20,'')
    if BmcLib.ping_sut():
        logging.info('第二个硬盘第二次成功进入系统')
    else:
        stylelog.fail('第二个硬盘第二次没有进入系统')
        return
    time.sleep(5)
    BmcLib.power_off()
    time.sleep(8)
    BmcLib.power_on()
    if not SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        BmcLib.init_sut()
        time.sleep(5)
        assert SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT)
    time.sleep(2)
    SetUpLib.send_data('hdd123@1')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.LOGIN_HDD_PSW_PROMPT):
        logging.info('输入第一个硬盘密码，成功进入第一个硬盘，要求输入第二个硬盘密码')
    else:
        return
    time.sleep(2)
    SetUpLib.send_data('hdd123@22')
    time.sleep(2)
    if  SetUpLib.wait_message_enter(SutConfig.Msg.POST_MESSAGE):
        logging.info('输入正确密码，成功进入')
        SetUpLib.send_key(Key.F2)
    else:
        return
    if SetUpLib.wait_message(SutConfig.Msg.SEL_LANG):
        logging.info('进入setup')
    else:
        return
    assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.HDDPassword.SET_HDDPASSWORD,10)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_01],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_01],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@1')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_key(Key.ESC)
    time.sleep(1)
    if not SetUpLib.locate_option(Key.DOWN,[HDD_NAME_02],3):
        if not SetUpLib.locate_option(Key.UP,[HDD_NAME_02],3):
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
        else:
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
    else:
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
    assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Msg.DEL_HDD_PSW_OPTION],3)
    SetUpLib.send_key(Key.ENTER)
    time.sleep(1)
    SetUpLib.send_data('hdd123@22')
    if SetUpLib.wait_message_enter(SutConfig.Msg.SET_HDD_PSW_SUCCESS,5):
        logging.info('删除密码')
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
    else:
        return
    SetUpLib.send_keys(Key.SAVE_RESET)
    return True