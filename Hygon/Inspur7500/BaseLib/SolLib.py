import subprocess
import logging
import re
import time
from Inspur7500.BaseLib import PwdLib, BmcLib
from Inspur7500.Config import SutConfig
from Inspur7500.Config.PlatConfig import Key
from batf.SutInit import Sut


class SolTerm:
    def __init__(self):
        self.sol_session = None
        self.stdin = None
        self.stdout = None
        self.SEP = "(?:\x1b\[\d+;\d+H){1}"  # value separator
        self.HLP = "(?:\x1b\[\d+m){3}"  # value hightlight ending flag, last appeared valid
        self.VALR = "(\w[\w -:/]*[\w\)+]*)"  # bios value name ruler

    def is_sol_active(self):
        if self.sol_session and self.sol_session.poll() is None:
            return True

    def open_sol(self, cmd=f'{SutConfig.Env.IPMITOOL} sol activate'):
        if self.is_sol_active():
            return True
        else:
            try_counts = 3
            while try_counts:
                self.sol_session = subprocess.Popen(args=cmd, stdin=subprocess.PIPE,
                                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.stdin = self.sol_session.stdin
                self.stdout = self.sol_session.stdout
                time.sleep(1)
                data = self.get_data(2)
                if re.search('SOL payload disabled', data):
                    logging.info('SOL Disabled')
                    subprocess.Popen(args=f'{SutConfig.Env.IPMITOOL} sol set enabled true 1', stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(1)

                elif re.search('SOL payload already active on another session', data):
                    logging.info('SOL already active')
                    subprocess.Popen(args=f'{SutConfig.Env.IPMITOOL} sol deactivate', stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(1)

                else:
                    logging.info('Open SOL successfully')
                    time.sleep(1)
                    return True
                try_counts -= 1
            logging.info(f'Open SOL failed')
            return

    def close_sol(self):
        if self.sol_session and self.sol_session.poll() is None:
            self.sol_session.kill()

    # 缓存数据长度
    def in_waiting(self):
        self.stdout.seek(0, 2)
        inwaiting = self.stdout.tell()
        self.stdout.seek(0, 0)
        return inwaiting

    def clean_buffer(self):
        time.sleep(0.5)
        self.stdout.read(self.in_waiting())

    def send_key(self, key):
        if not self.is_sol_active():
            self.open_sol()
        for i in key:
            self.stdin.write(i.encode('utf-8'))
        self.stdin.flush()

    def send_keys(self, key, delay=1):
        for i in key:
            self.clean_buffer()
            self.send_key(i)
            time.sleep(delay)

    def send_data(self, data):
        if not self.is_sol_active():
            self.open_sol()

        self.stdin.write(data.encode('utf-8'))
        self.stdin.flush()

    def send_data_enter(self, data):
        self.send_data(data)
        time.sleep(2)
        self.send_key(Key.ENTER)

    def read_full_buffer(self, timeout=2):
        start_time = time.time()
        buffer = b''
        while time.time() - start_time < timeout:
            waiting_cout = self.in_waiting()
            if waiting_cout != 0:
                buffer += self.stdout.read(abs(waiting_cout))
        return buffer.decode(encoding='utf-8', errors='ignore')

    def get_data(self, delay=10, key=None, cleanup=True, scroll=False):
        keep_scroll = '(?:\x1b\[\d+;\d+H█\x1b\[\d+;\d+H░)|(?:\x1b\[\d+;\d+H\*\x1b\[\d+;\d+H\+)'
        if key is not None:
            self.send_key(key)
        data = self.read_full_buffer(delay)
        if scroll and re.search(f'{keep_scroll}', data):
            self.send_key(Key.PAGE_DOWN)
            data += self.read_full_buffer(delay)
        if cleanup:
            data = Sut.BIOS_COM.cleanup_data(data)
        else:
            Sut.BIOS_COM.write_data2log(data)
        return data

    def boot_with_hotkey_only(self, key, msg, timeout=250, hotkey_prompt="Press Del go to Setup Utilityasda",
                              pw_prompt=SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT, password=PwdLib.PW.DEFAULT_PW):
        setup_pw_msg = SutConfig.Psw.LOGIN_SETUP_PSW_PROMPT
        setup_pw = PwdLib.PW.DEFAULT_PW
        buffer = b''
        count = 0
        psw = False
        stop_sign = False
        start_time = time.time()
        logging.debug("boot_with_hotkey: Receiving data from SUT...")
        self.clean_buffer()
        while True:
            try:
                inwaiting_cout = self.in_waiting()
                if inwaiting_cout != 0:
                    # if count == 1 and not stop_sign:
                    #     time.sleep(0.1)
                    #     self.send_key(key)
                    data = self.stdout.read(inwaiting_cout)
                    buffer += data
                    all_data = Sut.BIOS_COM.cleanup_data(buffer.decode("utf-8", errors='ignore'), False)
                    Sut.BIOS_COM.cleanup_data(data.decode("utf-8", errors='ignore'))
                    if Sut.BIOS_COM.find_msg(hotkey_prompt, all_data):
                        time.sleep(1)
                        self.clean_buffer()
                        self.send_key(key)
                        if count == 0:
                            logging.info("Hot Key sent")
                        count = 1
                        buffer = b''
                    if Sut.BIOS_COM.find_msg(msg, all_data):
                        stop_sign = True
                        if psw == True:
                            return [True, True]
                        else:
                            return True
                    if not psw:
                        if Sut.BIOS_COM.find_msg(pw_prompt, all_data):
                            stop_sign = True
                            time.sleep(1)
                            self.send_data(f'{password}\x0d')
                            logging.info(f"Send password: {password}")
                            psw = True
                    if pw_prompt != setup_pw_msg:
                        if Sut.BIOS_COM.find_msg(setup_pw_msg, all_data):
                            stop_sign = True
                            time.sleep(1)
                            self.send_data(f'{setup_pw}\x0d')
                            logging.info(f"Send Setup password: {password}")

            except Exception as e:
                logging.error(e)
                logging.debug("boot_with_hotkey: Please check whether COM port is in use.")
                break

            if Sut.BIOS_COM.is_timeout(start_time, timeout):
                if count == 1:
                    logging.info('Hot Key sent,but did not find confirm msg')
                else:
                    logging.info('{0} not found'.format(hotkey_prompt))
                break

    def boot_with_hotkey(self, key, msg, timeout, hotkey_prompt):
        if not BmcLib.init_sut():
            return
        try_counts = 3
        while try_counts:
            self.open_sol()
            # BmcLib.enable_serial_normal()
            logging.info("Waiting for Hotkey message found...")
            if not self.boot_with_hotkey_only(key, msg, timeout, hotkey_prompt):
                BmcLib.power_cycle()
                try_counts -= 1
            else:
                logging.info("Boot with hotkey successfully.")
                return True

        logging.info("Boot with hotkey fail.")
        return

    def boot_to_setup(self):
        logging.info("SetUpLib: Boot to setup main page")
        if not BmcLib.init_sut():
            logging.info("SetUpLib: Rebooting SUT Failed.")
            return
        logging.info("SetUpLib: Booting to setup")
        try_counts = 3
        while try_counts:
            self.open_sol()
            # BmcLib.enable_serial_normal()
            logging.info("Waiting for Hotkey message found...")
            if not self.boot_with_hotkey_only(Key.DEL, SutConfig.Msg.PAGE_MAIN, 400, SutConfig.Msg.POST_MESSAGE):
                BmcLib.power_cycle()
                try_counts -= 1
            else:
                logging.info("SetUpLib: Boot to setup main page successfully")
                self.clean_buffer()
                return True
        logging.info("SetUpLib: Boot to setup main page Failed")
        return

    @staticmethod
    def option(strs, high_pat=(1, 37, 47), high_pat_end=(1, 30, 47)):
        high_pat = '\x1b\[{}m\x1b\[{}m\x1b\[{}m\x1b'.format(*high_pat)
        high_pat_end = '\x1b\[{}m\x1b\[{}m\x1b\[{}m'.format(*high_pat_end)

        class option:
            name = ''
            value = ''
            help = ''

        dict = {}
        op_va = re.findall(f'{high_pat}\[\d+;(\d+)H(.*?){high_pat_end}', strs)
        help_msg = ' '.join(re.findall(';\d*(?:73|91)H(.*?)\s*\x1b', strs))
        option.help = help_msg.strip()
        for op in op_va:
            dict[op[0]] = dict[op[0]] + ' ' + op[1] if op[0] in dict.keys() else op[1]
        option_value = list(dict.values())
        if option_value:
            option.name = option_value[0] if len(option_value) == 1 else option_value[1]
            option.value = option_value[0] if len(option_value) == 2 else ''
        return option

    @staticmethod
    def find_msg(msg, data, exact):
        if (not exact) and re.search(msg, data):
            return True
        if exact and re.search(f'{msg}$', data):
            return True

    def locate_option(self, key, setupoption, try_counts, delay=1, exact=True):
        data_before = ''
        name = setupoption[0]
        value = setupoption[1] if len(setupoption) == 2 else ''
        logging.info("Locate option: {0}".format(setupoption))
        data = self.get_data(delay + 1, cleanup=False)

        current = self.option(data)
        if self.find_msg(name, current.name, exact) and re.search(value, current.value):
            logging.info("Option found: {0}".format(setupoption))
            global help_msg
            help_msg = current.help
            return True
        else:
            self.send_key(key)
            while try_counts:
                data = self.get_data(delay, cleanup=False)
                if data == data_before and data != '':
                    break
                current = self.option(data)
                if self.find_msg(name, current.name, exact) and re.search(value, current.value):
                    logging.info("Option found: {0}".format(setupoption))
                    help_msg = current.help
                    return True
                data_before = data
                try_counts -= 1
                self.send_key(key)
            logging.info("Option not found: {0}".format(setupoption))

    def boot_to_page(self, page_name):
        logging.info("SetUpLib: Move to specified setup page")
        if page_name == SutConfig.Msg.PAGE_ALL[0]:
            ES = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,7}"
            patten = f'(?:\[0m\x1b\[34m\x1b\[47m\x1b\[\d+;\d+H{page_name}|{page_name}{ES})'
            try_counts = 12
            self.clean_buffer()
            self.send_key(Key.RIGHT)
            while try_counts:
                data = self.get_data(2, cleanup=False)
                if re.search(patten, data):
                    logging.info("Option found: {0}".format(page_name))
                    return True
                try_counts -= 1
                self.send_key(Key.RIGHT)
            logging.info("Option not found: {0}".format(page_name))
        else:
            if not self.locate_option(Key.RIGHT, [page_name], 12, 2):
                logging.info("SetUpLib: Specified setup page not found.")
                return
            logging.info("SetUpLib: Specified setup page found.")
            return True

    def wait_message(self, msg, delay=250, pw_prompt=None, pw=None, cleanup=True, readline=False):
        # return SerialLib.is_msg_present_clean(Sut.BIOS_COM,msg,delay,cleanup=cleanup)
        logging.debug("Waiting for:\"{0}\"".format(msg))
        start_time = time.time()
        buffer = b''
        clean_data = ''
        psw = False
        while True:
            time.sleep(0.1)
            in_waiting_count = self.in_waiting()
            if in_waiting_count != 0:
                try:
                    initial_data = self.stdout.read(in_waiting_count)
                    buffer += initial_data
                    data = buffer.decode("utf-8", errors='ignore')
                    if cleanup:
                        clean_data = Sut.BIOS_COM.cleanup_data(data, save=False)
                        Sut.BIOS_COM.cleanup_data(initial_data.decode("utf-8", errors='ignore'))
                    else:
                        Sut.BIOS_COM.write_data2log(initial_data.decode("utf-8", errors='ignore'))
                except Exception as e:
                    logging.error(e)
                    logging.error("is_msg_present_general: error in reading serial data")
                if cleanup:
                    if Sut.BIOS_COM.find_msg(msg, clean_data):
                        logging.debug("Message found.")
                        return True
                else:
                    if Sut.BIOS_COM.find_msg(msg, data):
                        logging.debug("Message found.")
                        return True
                if not psw:
                    if pw_prompt and Sut.BIOS_COM.find_msg(pw_prompt, data):
                        time.sleep(1)
                        self.send_data(f'{pw}\x0d')
                        logging.info("Send password...")
                        psw = True
            if Sut.BIOS_COM.is_timeout(start_time, delay):
                logging.info("is_msg_present_general: {0} not found after waiting {1} seconds".format(msg, delay))
                break

    def boot_to_boot_menu(self, data_save=False, reset=True, try_counts=2):
        self.open_sol()
        if try_counts > 0:
            scroll = '(?:\x1b\[\d+;\d+H█)|(?:\x1b\[\d+;\d+H\*)'
            logging.info("SetUpLib: Boot to boot menu")
            if reset:
                if not BmcLib.init_sut():
                    logging.info("SetUpLib: Rebooting SUT Failed.")
                    return
                # BmcLib.enable_serial_normal()
            if not self.wait_message(SutConfig.Msg.POST_MESSAGE):
                BmcLib.init_sut()
                # BmcLib.enable_serial_normal()
                assert self.wait_message(SutConfig.Msg.POST_MESSAGE)
            self.clean_buffer()
            logging.info("Hot Key sent")
            self.send_key(Key.F11)
            start = time.time()
            datas = ''
            while True:
                data = self.get_data(1, cleanup=False)
                datas += data
                if re.search(SutConfig.Msg.ENTER_BOOTMENU, Sut.BIOS_COM.cleanup_data(data)):
                    time.sleep(1)
                    if data_save:
                        datas += self.get_data(2, cleanup=False)
                        if re.search(scroll, datas):
                            self.clean_buffer()
                            self.send_key(Key.UP)
                            data1 = self.get_data(2, cleanup=False)
                            self.clean_buffer()
                            self.send_key(Key.DOWN)
                            data2 = self.get_data(2, cleanup=False)
                            split_data = re.findall('\x1b\[\d+;\d+H([^\x1b]+)\x1b\[1m', data2)[0] if re.findall(
                                '\x1b\[\d+;\d+H([^\x1b]+)\x1b\[1m', data2) else ''
                            datas = data2.split(split_data)[0] + split_data + data1.split(split_data)[-1]

                        logging.debug(Sut.BIOS_COM.cleanup_data(datas))
                        return Sut.BIOS_COM.cleanup_data(datas)
                    else:
                        logging.info("SetUpLib: Boot to boot menu successfully")
                        return True
                now = time.time()
                if now - start > 90:
                    break
            logging.info('Boot to bootmenu failed')
            if reset:
                return self.boot_to_boot_menu(data_save, reset, try_counts - 1)
            else:
                return self.boot_to_boot_menu(data_save, reset, 0)
        return ''

    def get_value_list(self):
        all_patten = re.compile(f"{self.SEP}{self.VALR}")
        high_patten = re.compile(f"{self.SEP}{self.VALR}{self.HLP}")
        self.send_key(Key.ENTER)
        tmpdata = self.get_data(1, cleanup=False)
        val_list = all_patten.findall(tmpdata)
        if re.search('▼', tmpdata):
            self.send_keys([Key.DOWN] * (len(val_list) - 1), 1)
            try_counts = 20
            while try_counts:
                time.sleep(1)
                self.send_key(Key.DOWN)
                data = self.get_data(1, cleanup=False)
                val_list += high_patten.findall(data)
                if not re.search('▼', data):
                    break
                try_counts -= 1
        self.send_keys(Key.ESC)
        if not val_list:
            logging.error("Fail to match values list")
            return
        logging.info("Current option values: {}".format(val_list))
        return val_list

    def locate_value(self, value_str):
        all_patten = re.compile(f"{self.SEP}{self.VALR}")
        self.send_key(Key.ENTER)
        tmpdata = self.get_data(1, cleanup=False)
        Sut.BIOS_COM.write_data2log(tmpdata)
        val_list = all_patten.findall(tmpdata)
        if not val_list:
            logging.error("Fail to match values list")
            return
        logging.info("Current option values: {}".format(val_list))
        hl_patten = re.compile(f"{self.SEP}{self.VALR}{self.HLP}")  # hight patten
        if '|' in value_str:
            if any(i in val_list for i in value_str.split('|')):
                for j in value_str.split('|'):
                    if j in val_list:
                        value_str = j
            else:
                logging.error('"{}" not in value list'.format(value_str))
                self.send_key(Key.ESC)
                return
        else:
            if value_str not in val_list:
                logging.error('"{}" not in value list'.format(value_str))
                self.send_key(Key.ESC)

        hl_default = hl_patten.findall(tmpdata)
        if hl_default[-1] == value_str:
            logging.info('Current select option is "{}"'.format(value_str))
            return True
        offset = val_list.index(value_str) - val_list.index(hl_default[-1])
        press_key = Key.DOWN if offset > 0 else Key.UP
        key_cnt = abs(offset)
        for k in range(key_cnt):
            self.send_key(press_key)
            time.sleep(1)
            tmpdata = self.stdout.read(self.in_waiting()).decode("utf-8", errors='ignore')

        hl_current = hl_patten.findall(tmpdata)
        if not hl_current:
            logging.error("Fail to verify current select value after key pressed")
            return
        if hl_current[-1] == value_str:
            logging.info('Locate to value "{}" pass'.format(value_str))
            return True
        logging.error('Locate to value "{}" failed'.format(value_str))

    def select_boot_option(self, key, optionname, try_counts, confirm_msg, first_option=None):
        counts = try_counts
        es = "(\x1B[@-_][0-?]*[ -/]*[@-~]){1,2}"
        patten = es + f'(?:{optionname})' + es + r"\x1B\[44m"
        patten_before = es + f'(?:{optionname})' + es + r"\x1B\[40m"
        round_sign = False
        while try_counts:
            data = self.get_data(1, cleanup=False)
            if re.search(patten, data):
                logging.info("Boot option found: {0}".format(optionname))
                self.send_key(Key.ENTER)
                if not self.boot_with_hotkey_only(Key.DEL, confirm_msg, 120):
                    logging.info("Boot to option: {0} Failed".format(optionname))
                    return
                logging.info("Boot to option: {0} successfully".format(optionname))
                return True
            elif re.search(patten_before, data):
                self.send_key(Key.UP)
                if self.wait_message(patten, 2, cleanup=False):
                    logging.info("Boot option found: {0}".format(optionname))
                    self.send_key(Key.ENTER)
                    if not self.boot_with_hotkey_only(Key.DEL, confirm_msg, 120):
                        logging.info("Boot to option: {0} Failed".format(optionname))
                        return
                    logging.info("Boot to option: {0} successfully".format(optionname))
                    return True
            if re.findall('\x1b\[\d+;\d+H(.*?)\x1b\[1m\x1b\[37m\x1b\[44m?', data) == first_option:
                round_sign = True
                logging.info("Boot to option: {0} Failed".format(optionname))
                return
            if try_counts == counts - 1 and first_option is None:
                first_option = re.findall('\x1b\[\d+;\d+H(.*?)\x1b\[1m\x1b\[37m\x1b\[44m?', data)
            self.send_key(key)
            try_counts -= 1
        if try_counts == 0 and round_sign is False:
            return self.select_boot_option(key, optionname, counts, confirm_msg, first_option)
        logging.info("Boot option NOT found: {0}".format(optionname))

    def change_option_value(self, key_optionname, optionname, try_counts, value_str, delay=1):
        if key_optionname == Key.DOWN:
            key = Key.UP
        elif key_optionname == Key.UP:
            key = Key.DOWN
        else:
            key = Key.DOWN
        if not self.locate_option(key_optionname, optionname, try_counts, delay):
            if not self.locate_option(key, optionname, try_counts + 1):
                time.sleep(0.5)
            else:
                time.sleep(0.5)
        else:
            time.sleep(1.5)
        if self.locate_value(value_str):
            time.sleep(0.5)
            self.send_key(Key.ENTER)
            time.sleep(0.5)
            return True
        else:
            logging.info("Value NOT found: {0}".format(value_str))

    def back_to_setup_toppage(self, msg='Setup Configuration|配置确认'):
        try:
            try_counts = 10
            while try_counts:
                logging.info('Navigating to top page,')
                self.send_key(Key.ESC)
                if self.wait_message(msg, delay=2):
                    time.sleep(0.5)
                    self.send_key(Key.DISCARD_CHANGES)
                    break
                try_counts -= 1
            logging.info("Current is top page,")
            time.sleep(0.5)
            return True
        except Exception as err:
            logging.debug(err)

    def enter_menu_change_value(self, key, option_path, try_counts, save=False):
        if type(option_path) == str:
            option_path = [option_path]
        for index, option in enumerate(option_path):
            if option in SutConfig.Msg.PAGE_ALL:
                if index > 0:
                    if len(option_path) > 1 and option_path[index - 1] == option:
                        if not self.locate_option(key, [option], 3):
                            if not self.locate_option(Key.UP, [option], 4):
                                time.sleep(0.5)
                            else:
                                time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                        self.send_key(Key.ENTER)
                    else:
                        assert self.back_to_setup_toppage()
                        assert self.boot_to_page(option)
                else:
                    assert self.back_to_setup_toppage()
                    assert self.boot_to_page(option)
            elif type(option) == dict:
                if isinstance(list(option.values())[0], int):
                    if list(option.keys())[0] == option_path[index - 1] and option_path[
                        index - 1] in SutConfig.Msg.PAGE_ALL:
                        time.sleep(0.5)
                        self.send_key(Key.ENTER)
                        time.sleep(1)
                        self.send_data_enter(str(list(option.values())[0]))
                        time.sleep(0.5)
                    else:
                        if not self.locate_option(key, list(option.keys()), try_counts):
                            if not self.locate_option(Key.UP, list(option.keys()), try_counts + 1):
                                time.sleep(0.5)
                            else:
                                time.sleep(0.5)
                                self.send_key(Key.ENTER)
                                time.sleep(1)
                                self.send_data_enter(str(list(option.values())[0]))
                                time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                            self.send_key(Key.ENTER)
                            time.sleep(1)
                            self.send_data_enter(str(list(option.values())[0]))
                            time.sleep(0.5)
                else:
                    if list(option.keys())[0] == option_path[index - 1] and option_path[
                        index - 1] in SutConfig.Msg.PAGE_ALL:
                        if self.locate_value(list(option.values())[0]):
                            time.sleep(0.5)
                            self.send_key(Key.ENTER)
                            time.sleep(0.5)
                        else:
                            logging.info("Value NOT found: {0}".format(list(option.values())[0]))
                    else:
                        assert self.change_option_value(key, list(option.keys()), try_counts, list(option.values())[0])
            else:
                if not self.locate_option(key, [option], try_counts):
                    if not self.locate_option(Key.UP, [option], try_counts + 1):
                        time.sleep(0.5)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                self.send_key(Key.ENTER)
        if save:
            time.sleep(1)
            self.send_keys(Key.SAVE_RESET)
            time.sleep(3)
        return True

    def get_shell_fs_num(self):
        self.send_data('Map')
        time.sleep(1)
        self.send_key(Key.ENTER)
        fs = []
        data = self.get_data(2).splitlines()
        for index in range(0, len(data)):
            if re.search('USB', data[index]):
                fs += re.findall('(FS\d+:) ', data[index - 1])
        if fs:
            num = ''
            for i in fs:
                self.send_data_enter(i)
                time.sleep(1)
                self.send_data_enter('ls')
                if SutConfig.Env.BIOS_FILE in self.get_data(3):
                    num = i
                    break
            return num
        else:
            return ''
