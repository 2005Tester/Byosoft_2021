import os
import re
import csv
import glob
import stat
import tarfile
import time
import datetime


class DumpFile:
    def __init__(self, tar_path: str, tar_name: str=None):
        self.file_path = tar_path
        self.file_name = tar_name

    def _get_tar_file(self) -> str:
        if self.file_name:
            return os.path.join(self.file_path, self.file_name)
        tar_file = glob.glob(os.path.join(self.file_path, "*.tar.gz"))
        if not tar_file:
            print(f"## No *.tar.gz files found in {self.file_path}")
            return ""
        if len(tar_file) > 1:
            print(f"## Multi *.tar.gz files found in {self.file_path}")
            self.file_name = input("Please Input the tar.gz file name:")
            return os.path.join(self.file_path, self.file_name)
        return tar_file[0]

    @staticmethod
    def _get_member_by_name(name, members):
        for member in members:
            tar_name = os.path.split(member.name)[1]
            if re.match(rf"{name}\.?", tar_name):
                yield member

    def _extract_by_names(self, tar_file:str, names=""):
        """
        Extract the specific name file from the tar.gz package

        Parameters
        ----------
        tar_file: str
            the tar.gz file to extract from
        names: str or list
            all file named as {name} will be extracted to the tar_file's directory, ingore the name suffix

        Returns
        -------
        None
        """
        if names:
            names = [names] if isinstance(names, str) else names
        tar_file_path = os.path.split(tar_file)[0]
        with tarfile.open(tar_file) as tar:
            try:
                if names:
                    for name in names:
                        tar.extractall(path=tar_file_path, members=self._get_member_by_name(name, tar.getmembers()))
                else:
                    tar.extractall(path=tar_file_path)
            except PermissionError as e:
                os.chmod(e.filename, stat.S_IWRITE)
                self._extract_by_names(tar_file, names)

    def get_logs(self, path: str, name: str) -> list:
        """
        Get all files name as {name} or {name}.tzr.gz after extract

        Parameters
        ----------
        path: str
            the relative path in tar.gz file
        name: str
            file name in the path

        Returns
        -------
        list
            all file names abs path
        """
        abs_path = os.path.join(self.file_path, path)
        self._extract_by_names(self._get_tar_file(), name)
        logs = [os.path.join(abs_path, f) for f in os.listdir(abs_path) if re.match(rf"{name}(?:\.tar\.gz)?$", f)]
        return logs

    def _merge_log(self, path, key_word, name_in_tar) -> str:
        """
        Merge two file like "xxx" and "xxx.tar.gz" in the path

        Parameters
        ----------
        path: str
            the relative path in tar.gz file
        key_word: str
            keywords of file name to be merged
        name_in_tar: str
            the file name in xxx.tar.gz to be extract and merge

        Returns
        -------
        str
            return merged file path+name if merge success, else return ""
        """
        fdm_logs = self.get_logs(path, key_word)
        fdm_logs.sort(reverse=True)
        log_merge = f"{self.file_path}/{path}/{key_word}_all"
        with open(log_merge, "w", newline="\n") as _merge:
            for log in fdm_logs:
                log_path = os.path.split(log)[0]
                if log.endswith("tar.gz"):
                    self._extract_by_names(log, name_in_tar)
                    with open(f"{log_path}/{name_in_tar}", "r", encoding="utf-8") as _tar:
                        _merge.writelines(_tar.readlines())
                    try:
                        os.remove(f"{log_path}/{name_in_tar}")
                    except Exception:
                        pass
                else:
                    with open(f"{log_path}/{key_word}", "r", encoding="utf-8") as _log:
                        _merge.writelines(_log.readlines())
        if os.path.exists(log_merge):
            return log_merge
        print(f"## Fail to merge log: {key_word} and {name_in_tar}")
        return ""

    @staticmethod
    def compare(expect, actually, name="") -> bool:
        if isinstance(expect, str):
            if expect.isdigit():
                expect = int(expect)
            elif expect.lower().startswith("0x"):
                expect = int(expect, 16)
        if isinstance(actually, str):
            if actually.isdigit():
                actually = int(expect)
            elif actually.lower().startswith("0x"):
                actually = int(expect, 16)
        result = (expect == actually)
        if not result:
            print(f"## Check {name} fail: Expect={expect}, Actually={actually}")
        return result

    @staticmethod
    def log_filter(flag: str, log_list: list) -> list:
        valid_log = []
        for _log in log_list:
            if re.search(flag, _log):
                valid_log.append(_log)
        print(f"## {len(valid_log)} new log record after error injection")
        return valid_log

    def get_fdm_log(self) -> str:
        """
        Ectract and merge the fdmlog

        Returns
        -------
        str
            merged fdmlog path+name
        """
        return self._merge_log(path="dump_info/LogDump", key_word="fdm_log", name_in_tar="diagnose_fdm_log")

    def get_maintenance_log(self) -> str:
        """
        Ectract and merge the maintenance log

        Returns
        -------
        str
            merged maintenance log path+name
        """
        return self._merge_log(path="dump_info/LogDump", key_word="maintenance_log", name_in_tar="md_so_maintenance_log")

    def get_history_sel(self):
        """
        Get history system event log

        Returns
        -------
        str or None
            if extract history sel success return the file path+name, else return None
        """
        sel_history_tar = self.get_logs("dump_info/AppDump/sensor_alarm", "sel.tar")
        if sel_history_tar:
            self._extract_by_names(sel_history_tar[0], "eo_sel.csv")
        sel_history_log = f"{self.file_path}/dump_info/AppDump/sensor_alarm/eo_sel.csv"
        if os.path.exists(sel_history_log):
            return sel_history_log

    def get_current_sel(self):
        """
        Get current system event log show in bmc web

        Returns
        -------
        str or None
            if extract current sel success return the file path+name, else return None
        """
        sel_current_log = self.get_logs("dump_info/AppDump/sensor_alarm", "current_event.txt")
        if sel_current_log:
            return sel_current_log[0]

    def get_serial_log(self):
        """
        Ectract the BIOS serial log

        Returns
        -------
        str or None
            if extract serial log success return the file path+name, else return None
        """
        serial_log_tar = self.get_logs("dump_info/OSDump", "systemcom.tar")
        if serial_log_tar:
            self._extract_by_names(serial_log_tar[0], "systemcom.dat")
        serial_log = f"{self.file_path}/dump_info/OSDump/systemcom.dat"
        if os.path.exists(serial_log):
            return serial_log

    @staticmethod
    def get_real_time(time_string, time_format):
        """
        Transform format time string to time object

        Parameters
        ----------
        time_string: str
            string to parse
        time_format: str
            standard time format link: %Y-%m-%d %H:%M:%S

        Returns
        -------
        datetime.datetime object

        """
        time_parser = time.strptime(time_string, time_format)
        return datetime.datetime(*time_parser[0:6])

    def time_offset(self, start: str, end: str, start_format: str="%Y%m%d_%H%M%S", end_format: str="%Y-%m-%d %H:%M:%S") -> int:
        """
        Get two time's offset in second

        Parameters
        ----------
        start: str
            start time string
        end: str
            end time string
        start_format: str
            start time's format
        end_format: str
            end time's format

        Returns
        -------
        int
            seconds of {end_time} - {start_time}
        """
        return (self.get_real_time(end, end_format) - self.get_real_time(start, start_format)).total_seconds()

    @staticmethod
    def log_split(logfile, spliter="\n\n") -> list:
        with open(logfile, "r") as log:
            log_data = log.read().strip()
            return re.split(spliter, log_data) if log_data else []

    def get_new_log(self, logfile:str, test_time:str, spliter:str="\n\n") -> str:
        """
        Get the log after test_time

        Parameters
        ----------
        logfile: str
            logfile to deal with
        test_time: str
            the start test time string, must follow the format "%Y%m%d_%H%M%S"
        spliter: str
            string to split the log

        Returns
        -------
        str
            the new log's path+name after test time
        """
        # parse old log
        new_log = ""
        log_block_list = self.log_split(logfile, spliter)
        for block in log_block_list:
            block_time = "".join(re.findall("(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", block))
            if not block_time:
                continue
            if self.time_offset(start=test_time, end=block_time) >= 0:
                new_log += f"{block}{spliter}"
        # save new log
        if not new_log:
            print(f"## No any new log found after test, time: {test_time}")
        _path, _name = os.path.split(logfile)
        valid_log_save = os.path.join(_path, f"{_name}_new")
        with open(valid_log_save, "w", newline="\n") as log_save:
            log_save.write(new_log)
        return valid_log_save

    @staticmethod
    def words_in_text(text:str, exact:bool=False, *args, **kwargs):
        """
        Check if some {string} or {key: value} in the text

        Parameters
        ----------
        text: str
            the text string for search
        exact: bool
            if exact is True:
                1. all {args} should be found
                2. all {key:value} should be match
            if exact is False:
                1. at least one {args} should be found
                2. at least one {key:value} should be match

        args: str or list
            one or more strings for check
        kwargs: dict
            one or more key: values for check,like XX=a, YY=b or **{XX:a, YY:b}

        Returns
        -------
        bool
            return True or False acording to {exact} setting and check result
        """

        _str_miss = []
        _fail_item = {}
        if args:
            for arg in args:
                if not re.search(arg, text):
                    _str_miss.append(arg)
                    continue
        if kwargs:
            for key, value in kwargs.items():
                if not re.search(rf"{key}:\s+{value}", text, re.I):
                    _fail_item[key] = value
        if exact:
            return (not _str_miss) and (not _fail_item)
        _args_check = len(_str_miss) < len(args) if args else True
        _kw_check = len(_fail_item) < len(kwargs) if kwargs else True
        return _args_check and _kw_check

    @staticmethod
    def fdmlog_parse(single_log: str) -> dict:
        """
        Pasrse one FDM log to dict object

        Parameters
        ----------
        single_log: str
            single fdm log to deal with

        Returns
        -------
        dict
            return the dict object of single fdm_log
        """
        parse_dict = {}
        key_value_item = re.split("\s{2,}|\n", single_log)
        for key_value in key_value_item:
            if ":" not in key_value:
                continue
            kv = [r for r in re.split("(.+?):\s*(.+)", key_value) if r]
            if len(kv) != 2:
                continue
            if kv[0] in parse_dict:
                parse_dict[kv[0]].append(kv[1])
            else:
                parse_dict[kv[0]] = [kv[1]]
        return parse_dict

    def get_cpu_info(self) -> list:
        """
        Get CPU information from bmc dump file

        Returns
        -------
        dict
            return the dict: {"sku": XXX, "cores": XXX, "threads": XXX, "sn": XXX}
            and fill in the specific item if it's found
        """
        cpu_info = self.get_logs(path="dump_info/AppDump/CpuMem", name="cpu_info")
        if not cpu_info:
            return []
        cpu_list = []
        info_dic = {"sku": "", "cores": "", "threads": "", "sn": ""}
        with open(cpu_info[0], "r", encoding="utf-8") as _cpu:
            _lines = _cpu.readlines()
            for _c in _lines[1:]:
                _info = re.split("\s?,\s?", _c)
                if _info[1] != "present":
                    continue
                info_dic["sku"] = _info[2]
                info_dic["cores"] = "".join(re.findall("(\d+) cores", _info[4]))
                info_dic["threads"] = "".join(re.findall("(\d+) threads", _info[5]))
                info_dic["sn"] = _info[-1].strip()
                cpu_list.append(info_dic)
        return cpu_list


class BmcStatus(DumpFile):
    def __init__(self, test_time, dump_path, file_name=None):
        super(BmcStatus, self).__init__(dump_path, file_name)
        self.test_time = test_time

    @staticmethod
    def _bit(hex_val: str, high: int, low: int=None):
        """
        Parse a HEX str's specific bit value

        Parameters
        ----------
        hex_val: str
            HEX str, like 0xEF80400F
        high: int
            high bit offset
        low: int
            low bit offset, if low is None, just get single bit with {high}

        Returns
        -------
        int
            if both high and low are set:
                return section value of bit {low ~ high}
            if only high is set:
                return single bit of {high}
        """

        str_bin = int(hex_val, 16)
        high_mask = (1 << high + 1) - 1
        temp_val = str_bin & high_mask
        if low is None:
            return temp_val >> high
        return temp_val >> low

    def fdm_ierr(self) -> bool:
        """
        1. Error Type: Uncorrected Error-Catastrophic/Fatal
        2. MCA_ERR_SRC_LOG: bit27 = 1

        Returns
        bool
         return True if read IERR error successfully, else False
        -------

        """

        err_type = "Uncorrected Error-Catastrophic/Fatal"
        ierr_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(ierr_log)
        print(f"## {len(log_split)} new error record found after IERR injection")
        fdm_ierr_log = False
        for _log in log_split:
            err_type_check = self.words_in_text(_log, False, err_type)
            if not err_type_check:
                continue
            mca_err_src_log = "".join(re.findall("MCA_ERR_SRC_LOG: (.+)", _log))
            ierr_internal = self._bit(mca_err_src_log, 27)
            if ierr_internal:
                ierr_cpu = "".join(re.findall("CPU: (\d)\(Socket", _log))
                print(f"## [IERR_INTERNAL] CPU{ierr_cpu} | MCA_ERR_SRC_LOG = {mca_err_src_log}")
            if err_type_check and ierr_internal:
                print("## [FDM_LOG] Get IERR log success")
                fdm_ierr_log = True
        return fdm_ierr_log

    def fdm_mcerr(self) -> bool:
        """
        1. Error Type: Uncorrected Error-Catastrophic/Fatal
        2. MCA_ERR_SRC_LOG: bit27 = 0 / bit20=1 or bit26=1

        Returns
        -------
        bool
            return True if read MCERR error successfully, else False
        """

        err_type = "Uncorrected Error-Catastrophic/Fatal"
        mcerr_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(mcerr_log)
        print(f"## {len(log_split)} new error record found after MCERR injection")
        fdm_mcerr_log = False
        for _log in log_split:
            err_type_check = self.words_in_text(_log, False, err_type)
            if not err_type_check:
                continue
            mca_err_src_log = "".join(re.findall("MCA_ERR_SRC_LOG: (.+)", _log))
            mcerr_cpu = "".join(re.findall("CPU: (\d)\(Socket", _log))
            ierr_internal = self._bit(mca_err_src_log, 27)
            mcerr_msmi = self._bit(mca_err_src_log, 20)
            mcerr_internal = self._bit(mca_err_src_log, 26)
            mcerr_assert = (not ierr_internal) and (mcerr_msmi or mcerr_internal)
            if mcerr_assert:
                print(f"## [MCERR] CPU{mcerr_cpu} | MCA_ERR_SRC_LOG = {mca_err_src_log}")
            if err_type_check and mcerr_assert:
                print("## [FDM_LOG] Get MCERR log success")
                fdm_mcerr_log = True
        return fdm_mcerr_log

    def current_event(self, *args) -> bool:
        """
        Check if one or more event asserted in current BMC SystemEventLog after test

        Parameters
        ----------
        args: str or list
            one or more event string expect to assert

        Returns
        -------
        bool
            return True if all expect current event found, else False
        """

        if not args:
            return
        cur_sel = self.get_current_sel()
        _event_found = []
        with open(cur_sel, "r") as cur:
            for line in cur.readlines()[1:]:
                line_split = re.split(r"\s+\|\s+", line.strip())
                _time, _sensor, _event = line_split[1], line_split[3], line_split[5]
                _time_format = re.sub(r"[a-zA-Z]+ ", "", _time)
                if self.time_offset(self.test_time, _time_format) < 0:
                    continue
                _time_event = f"{_time_format} | {_sensor} | {_event}"
                for arg in args:
                    if (_time_event not in _event_found) and re.search(arg, line):
                        print(f"## Current New Event: '{_time_event}'")
                        _event_found.append(arg)
                        break
        if set(_event_found) == set(args):
            return True

    def history_event(self, *args) -> bool:
        """
        Check if one or more event asserted in history BMC SystemEventLog after test

        Parameters
        ----------
        args: str or list
            one or more event string expect to assert

        Returns
        -------
        bool
            return True if all expect history event found, else False
        """

        if not args:
            return
        hist_sel_csv = self.get_history_sel()
        _event_found = []
        with open(hist_sel_csv, "r", encoding="utf-8") as sel_csv:
            sel_read = csv.reader(sel_csv)
            sel_event = list(sel_read)[1:]
            for line in sel_event:
                _time = line[4]
                _event = line[3]
                _status = line[5]
                if self.time_offset(self.test_time, _time) < 0:
                    continue
                _time_event = f"{_time} | {_event} | {_status}"
                for arg in args:
                    if (_time_event not in _event_found) and re.search(arg, line):
                        print(f"## History New Event: '{_time_event}'")
                        _event_found.append(arg)
                        break
        if set(_event_found) == set(args):
            return True

    def fdm_3strike_timeout(self) -> bool:
        """
        1. Error Type: Uncorrected Error-Catastrophic/Fatal
        2. MCACODE = 0X0400
        3. MSCODE = 0X0080

        Returns
        -------
        bool
            return True if 3-strike timeout error found, else False
        """

        err_type = "Uncorrected Error-Catastrophic/Fatal"
        is_diag_success = self.history_event("Critical system error.")
        _3s_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(_3s_log)
        print(f"## {len(log_split)} new error record found after 3-Strike Timeout injection")
        _3s_log_found = False
        _tor_time_out = 0
        for _log in log_split:
            err_type_check = self.words_in_text(_log, False, err_type)
            if not err_type_check:
                continue
            if self.words_in_text(_log, True, Collect="BMC", MCACODE="0X110A", MSCODE="0X000C", **{"First MCERR Source": "CHA \d+"}):  # TOR Time Out
                _tor_time_out += 1
                continue
            _3s_reg = self.words_in_text(_log, True, Collect="BIOS", MCACODE="0X0400", MSCODE="0X0080")  # DWR Trigger 3-Strike Timeout
            if not _3s_reg:
                continue
            _time = "".join(re.findall(r"Time: (\d+-\d+-\d+ \d+:\d+:\d+)", _log))
            _3s_cpu = "".join(re.findall(r"CPU: (\d)\(Socket", _log))
            print(f"## [3Strike-Timeout] CPU{_3s_cpu} Asserted at: {_time}")
            if err_type_check and _3s_reg:
                print("## [FDM_LOG] Get 3Strike-Timeout log success")
                _3s_log_found = True
        return bool(_tor_time_out) if is_diag_success else (_3s_log_found and _tor_time_out)

    def serial_dwr(self):
        pass

    def fdm_mem_ce(self, only=True, mscode="0X0080", mcacode="0X0090", options=None, **kwargs) -> bool:
        """
        1. Error Type: Corrected Error
        2. MCACODE = "0X0090" / MSCODE = "0X0080"
        3. Support Physical Address Check: socket / channel / dimm / rank / bankgroup / bank / column / row / device / count
        4. Support System Address Check: sysaddr

        Parameters
        ----------
        options: dict
            Additional options to be check
        mcacode: str
            MCACODE value in MCi_Misc Register
        mscode: str
            MSCODE value in MCi_Misc Register
        only: bool
            if only is true, only this type error log to be match, other will be filtered out
        kwargs: dict
            physical address to check
            Available key: socket / channel / dimm / rank / bankgroup / bank / column / row / device

        Returns
        -------
        bool
            return True if Memory CE found and all physical address match, else False
        """

        err_type = "Corrected Error"
        _memce_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(_memce_log, spliter="CORRECTION_DEBUG_DEV_VEC_2: 0X[a-fA-F0-9]+\n\n")
        mem_err_flag = "MCA M2M OR IMC REGISTER DUMP"
        valid_mem_log = self.log_filter(mem_err_flag, log_split) if only else log_split
        _memce_fail = []
        for _log in valid_mem_log:
            err_type_check = self.words_in_text(_log, False, err_type)
            if not err_type_check:
                continue
            _memce_code = self.words_in_text(_log, True, MCACODE=mcacode, MSCODE=mscode)
            if not _memce_code:
                continue
            if options and not self.words_in_text(_log, True, **options):
                _memce_fail.append(options)
            _retry_info = "".join(re.findall(r"Retry_Rd_Err_Address: (.+)", _log))
            print(f"## Memory CE found at address: {_retry_info}")
            _phy_addr = re.findall(r"\[DIMM(\d)(\d)(\d)\]\(.*CS(\d).*BankGroup (\d).+Bank (\d).+Column (\d).+Row (\d).+"
                                   r"Device (\w+)\).+SYSADDRESS: (.+)\)", _log)
            if not _phy_addr:
                print(f'## Match Retry_Rd_Err_Address fail: {_retry_info}')
                continue
            socket, channel, dimm, rank, bankgroup, bank, coulmn, row, device, sysaddr = _phy_addr[0]
            _addr_dic = {"socket": socket,
                         "channel": channel,
                         "dimm": dimm,
                         "rank": rank,
                         "bankgroup": bankgroup,
                         "bank": bank,
                         "column": coulmn,
                         "row": row,
                         "device": device,
                         "sysaddr": sysaddr,
                         "count": len(valid_mem_log) }
            for key, value in kwargs.items():
                if key not in _addr_dic:
                    print(f"## Incorrect parameter: {key}")
                    return
                if not self.compare(value, _addr_dic.get(key), name=key):
                    _memce_fail.append(key)
        return not _memce_fail

    def fdm_memce_array(self, only=True, *args) -> bool:
        """
        FDM Multi MEM CE Array check, in different phy address one by one

        Parameters
        ----------
        only: bool
            if only is true, only this type error log to be match, other will be filtered out
        args: list
            args list must follow the format: ["socket channel dimm rank bank_group=0 bank=0 device", counts]

        Returns
        -------
        bool
            return True if all the ce match the address and follow the right order, else False
        """
        _memce_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(_memce_log, spliter="CORRECTION_DEBUG_DEV_VEC_2: 0X[a-fA-F0-9]+\n\n")
        mem_err_flag = "MCA M2M OR IMC REGISTER DUMP"
        valid_mem_log = self.log_filter(mem_err_flag, log_split) if only else log_split
        _memce_fail = []

        error_list = []
        for arg in args:
            if len(arg) == 2:
                error_list += [arg[0]] * arg[1]
            elif len(arg) == 1:
                error_list += [arg[0]]
            else:
                print(f"## Incorrect Parameters: {arg}")
        if not self.compare(len(error_list), len(valid_mem_log), name="fdm mem ce count"):
            _memce_fail.append("count")
        check_items = ["socket", "channel", "dimm", "rank", "bank_group", "bank", "device"]
        for index, _addr in enumerate(error_list):
            addr = _addr.strip().split(" ")
            try:
                fdm_log = valid_mem_log[index]
                _retry_info = "".join(re.findall(r"Retry_Rd_Err_Address: (.+)", fdm_log))
                print(f"## Memory CE found at address: {_retry_info}")
                _phy_addr = re.findall(r"\[DIMM(\d)(\d)(\d)\]\(.*CS(\d).*BankGroup (\d).+Bank (\d).+"
                                       r"Column (\d).+Row (\d).+Device (\w+)\).+SYSADDRESS: (.+)\)", fdm_log)[0]
                # _socket, _channel, _dimm, _rank, _bank_group, _bank, _coulmn, _row, _device, _sysaddr = _phy_addr[0]
            except:
                _memce_fail.append(f"addr_{index}: {_addr}")
                continue
            if not _phy_addr:
                print(f'## Match Retry_Rd_Err_Address fail: {_retry_info}')
                continue
            for _index, _add in enumerate(addr):
                _name = check_items[_index]
                _index = 8 if _name == "device" else _index
                if not self.compare(_add, _phy_addr[_index], name=_name):
                    _memce_fail.append(f"addr_{index}: {_name}")
        if not _memce_fail:
            return True
        print(f"## Check mem ce array fail: {_memce_fail}")

    def fdm_mem_uce(self, only=True, err_type=("UCNA", "SRAR"), options=None, **kwargs) -> bool:
        """
        1. Error Type: ["Uncorrected Error-UCNA", "Uncorrected Error-SRAR"]
        2. UCNA: MCACODE = "0X0090", MSCODE = "0X00A0" / SRAR: MCACODE = "0X0134", MSCODE = "0X0010"
        3. Support Physical Address Check: socket / channel / dimm
        4. Support System Address Check: sysaddr

        Parameters
        ----------
        only: bool
            if only is true, only this type error log to be match, other will be filtered out
        err_type: list
            Memory UCE Error Type: UCNA / SRAR / SRAO
        options: dict
            Additional Options to be check
        kwargs: dict
            physical address to check
            Available key: socket / channel / dimm / sysaddr

        Returns
        -------
        bool
            return True if Memory UCE found and all physical address match, else False
        """
        mem_uce_flag = "Uncorrected Error"
        err_type = list(err_type) if not isinstance(err_type, list) else err_type
        err_type = [f"{mem_uce_flag}-{_type}" for _type in err_type]
        _memuce_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(_memuce_log)
        valid_uce_log = self.log_filter(mem_uce_flag, log_split) if only else log_split
        _memuce_fail = []
        for _log in valid_uce_log:
            etype = "".join(re.findall("Error Type:(.+)", _log.strip()))
            if etype not in err_type:
                print(f"## Unexpected error record: {etype}")
                return
            if options and not self.words_in_text(_log, True, etype, **options):
                print("## Unexpected error record in fdm_log")
                return
            _phy_addr = re.findall(r"Mci_Address: (.+)\[DIMM(\d)(\d)(\d)]", _log)
            sysaddr, socket, channel, dimm = _phy_addr[0]
            _addr_dic = {"socket": socket,
                         "channel": channel,
                         "dimm": dimm,
                         "sysaddr": sysaddr}
            for key, value in kwargs.items():
                if key not in _addr_dic:
                    print(f"## Incorrect parameter: {key}")
                    return
                if not self.compare(str(value), _addr_dic.get(key), name=key):
                    _memuce_fail.append(key)
        return not _memuce_fail

    def fdm_pcie_ce(self, socket: int = None, port: str = None, device: str = None, count: int = 0, only=True) -> bool:
        """
        1. Error Type: Corrected Error
        2. Error Code: ERR_COR Received
        3. DEVSTS: (Bit 0)Correctable Error Detected
        4. Support Check: socket / port / device

        Parameters
        ----------
        socket: int
            expect pcie ce socket number
        port: str
            expect pcie ce port number
        device
            expect pcie device name
        count: int
            pcie ce error count
        only: bool
            if only is true, only this type error log to be match, other will be filtered out

        Returns
        -------
        bool
            return True if pcie ce error fonud and all location check match, else False
        """

        err_type = [("Corrected Error", "Receiver Error"),
                    ("Corrected Error", "ERR_COR Received")]
        _pcie_ce_log = self.get_new_log(self.get_fdm_log(), self.test_time)
        log_split = self.log_split(_pcie_ce_log)
        pcie_log_flag = "IIO REPORTING ERROR|IIO IEH GLOBAL REGISTER DUMP"
        valid_pcie_log = self.log_filter(pcie_log_flag, log_split) if only else log_split
        _pcie_ce_fail = []
        if len(valid_pcie_log) != count*2:
            _pcie_ce_fail.append("count")
        for _log in valid_pcie_log:
            if re.search(f"Sub Module: PCIe_RootPort", _log):
                etype_ecode_all = []
                for line in _log.splitlines():
                    _type_code_find = re.findall(rf"Error Type: (.+\S)\s+Error Code: (.+\S)", line)
                    if _type_code_find:
                        etype_ecode_all.append(_type_code_find[0])
                for _etype_code in etype_ecode_all:
                    if _etype_code not in err_type:
                        print(f"## Unexpected error type or error code: {_etype_code}")
                        _pcie_ce_fail.append(_etype_code)
                etype_check = self.words_in_text(_log, True, DEVSTS="\(Bit 0\)Correctable Error Detected")
                if not etype_check:
                    print(f"## DEVSTS or SECSTS check fail")
                    _pcie_ce_fail.append(["DEVSTS", "SECSTS"])
                _port_device = re.findall(r"Root Port: \((.+)\)\[(.+)]", _log)
                if not _port_device:
                    print("## Root Port Information is missing")
                    return
                _rootport, _device = _port_device[0]
                if not (port is None):
                    if not self.compare(port.lower().replace("0x", ""), _rootport.lower().replace("0x", ""), name="cpu"):
                        _pcie_ce_fail.append("port")
                if not (device is None):
                    if not self.compare(device.lower(), _device.lower(), name="device"):
                        _pcie_ce_fail.append("device")
            if not (socket is None):
                _cpu = "".join(re.findall(r"CPU: (\d)", _log))
                if not self.compare(socket, _cpu, name="socket"):
                    _pcie_ce_fail.append("socket")
        if not _pcie_ce_fail:
            return True
        print(f"## PCIE CE FDM check fail: {_pcie_ce_fail}")

    def fdm_pcie_uce(self, socket: int = None, port: str = None, device: str = None, count: int = 0, only=True) -> bool:
        """
        1. Error Type: Non-Fatal Error
        2. Error Code: Non-fatal Error Messsage Received
        3. DEVSTS: (Bit 1)Non-Fatal Error Detected
        4. Support Check: socket / port / device

        Parameters
        ----------
        socket: int
            expect pcie ce socket number
        port: str
            expect pcie ce port number
        device
            expect pcie device name
        count: int
            pcie uce error count
        only: bool
            if only is true, only this type error log to be match, other will be filtered out

        Returns
        -------
        bool
            return True if pcie uce error fonud and all location check match, else False
        """

        err_type = [("First Non-Fatal Error", "Completion Timeout Status"),
                    ("Non-Fatal Error", "Non-fatal Error Messsage Received")]
        _pcie_uce_log = self.log_split(self.get_new_log(self.get_fdm_log(), self.test_time))
        pcie_log_flag = "IIO REPORTING ERROR|IIO IEH GLOBAL REGISTER DUMP"
        valid_pcie_log = self.log_filter(pcie_log_flag, _pcie_uce_log) if only else _pcie_uce_log
        _pcie_uce_fail = []
        if len(valid_pcie_log) != count*2:
            _pcie_uce_fail.append("count")
        for _log in valid_pcie_log:
            if re.search(f"Sub Module: PCIe_RootPort", _log):
                etype_ecode_all = []
                for line in _log.splitlines():
                    _type_code_find = re.findall(rf"Error Type: (.+\S)\s+Error Code: (.+\S)", line)
                    if _type_code_find:
                        etype_ecode_all.append(_type_code_find[0])
                for _etype_code in etype_ecode_all:
                    if _etype_code not in err_type:
                        print(f"## Unexpected error type or error code: \n{_etype_code}")
                        _pcie_uce_fail.append(_etype_code)
                etype_check = self.words_in_text(_log, True, DEVSTS="\(Bit 1\)Non-Fatal Error Detected")
                if not etype_check:
                    print(f"## DEVSTS or SECSTS check fail")
                    _pcie_uce_fail.append(["DEVSTS", "SECSTS"])
                _port_device = re.findall(r"Root Port: \((.+)\)\[(.+)]", _log)
                if not _port_device:
                    print("## Root Port Information is missing")
                    return
                _rootport, _device = _port_device[0]
                if not (port is None):
                    if not self.compare(port.lower().replace("0x", ""), _rootport.lower().replace("0x", ""), name="port"):
                        _pcie_uce_fail.append("port")
                if not (device is None):
                    if not self.compare(device.lower(), _device.lower(), name="device"):
                        _pcie_uce_fail.append("device")
            if not (socket is None):
                _cpu = "".join(re.findall(r"CPU: (\d)", _log))
                if not self.compare(socket, _cpu, name="socket"):
                    _pcie_uce_fail.append("socket")
        if not _pcie_uce_fail:
            return True
        print(f"## PCIE CE FDM check fail: {_pcie_uce_fail}")

    def fdm_upi_ce(self, socket: int = None, port: int = None, crc: int = None, count: int = None, only=True) -> bool:
        """
        1. Error Type: Corrected Error
        2. MSCODE: 0X0030
        4. Support Check: socket / port / count

        Parameters
        ----------
        socket: int
            upi error socket number
        port: int
            upi error port number
        crc: int
            upi error crc count number
        count: int
            upi error count number
        only: bool
            if only is true, only this type error log to be match, other will be filtered out

        Returns
        -------
        bool
            return True if UPI CE error found and all physical address match, else False
        """

        err_type = "Corrected Error"
        _upi_ce_log = self.log_split(self.get_new_log(self.get_fdm_log(), self.test_time))
        upi_error_flag = "MCA UPI REGISTER DUMP"
        valid_upi_log = self.log_filter(upi_error_flag, _upi_ce_log) if only else _upi_ce_log
        _upi_ce_fail = []
        if count and len(valid_upi_log) != count:
            _upi_ce_fail.append("count")
        for _log in valid_upi_log:
            _err_type = self.words_in_text(_log, True, f"Error Type:{err_type}", MSCODE="0X0030")
            if not _err_type:
                print("## Unexpected error record in fdmlog after UPI CE injectioin")
                return
            _cpu = "".join(re.findall("CPU: (\d)\(Socket", _log))
            _port = "".join(re.findall("Module: MCA Bank\d+\(Intel UPI (\d+)\)", _log))
            _crc = "".join(re.findall("CRC Error Count: (\d+)", _log))
            if not (socket is None):
                if not self.compare(socket, _cpu, name="socket"):
                    _upi_ce_fail.append("socket")
            if not (port is None):
                if not self.compare(port, _port, name="port"):
                    _upi_ce_fail.append("port")
            if not (crc is None):
                if not self.compare(crc, _crc, name="crc"):
                    _upi_ce_fail.append("crc")
        if not _upi_ce_fail:
            return True
        print(f"## Check UPI CE fail: {_upi_ce_fail}")

    def fdm_upi_uce(self, socket: int = None, port: int = None) -> bool:
        """
        1. Error Type:Uncorrected Error-Catastrophic/Fatal
        2. All Cores for the fail CPU:
            a. Core: {core}
            b. MSCODE: 0X000C
            c. First MCERR Source: UPI {port}
        3. All Cores for the non fail CPU:
            a. Core: {core}
            b. MSCODE: 0X000C
            c. First MCERR Source: Chassis_Punit_FSM
        4. Error Flag: Module=MCA Bank7(Intel UPI 1) / MSCODE="0X0010" / First MCERR Source=UPI 1
        5. Support Check: socket / port

        Parameters
        ----------
        socket: int
            upi uce socket number
        port: int
            upi uce port number

        Returns
        -------
        bool
            return True if UPI UCE found and all physical assress match, else False
        """

        err_type = "Uncorrected Error-Catastrophic/Fatal"
        _fail = []
        _cores = []
        _err_detect = 0

        _upi_uce_log = self.log_split(self.get_new_log(self.get_fdm_log(), self.test_time))
        print(f"## {len(_upi_uce_log)} errors are recorded after UPI UCE injection")
        _cpu_info = self.get_cpu_info()[0]

        for _log in _upi_uce_log:
            if self.words_in_text(_log, True, err_type, Module=f"MCA Bank\d+\(Intel UPI {port}\)",  # UPI UCE Flag
                                  MSCODE="0X0010", **{"First MCERR Source": f"UPI {port}"}):
                _err_detect += 1
        if not _err_detect:
            print("## No Valid FDM log found in fdmlog")
            return

        for _log in _upi_uce_log:
            if not self.words_in_text(_log, True, f"Error Type:\s?{err_type}"):
                continue
            detail = self.fdmlog_parse(_log)
            core = detail.get('Core')
            if detail.get("CPU")[0][0] == str(socket):  # upi error socket
                if not self.words_in_text(_log, True, **{"First MCERR Source":f"UPI {port}"}):
                    print('Check "First MCERR Source" failed')
                    _fail.append(f'First MCERR Source: core{core}')
                if self.words_in_text(_log, True, MSCODE="0X000C", Core="\d"):
                    _cores.append(core[0])
            elif not self.words_in_text(_log, True, **{"First MCERR Source":f"Chassis_Punit_FSM"}):  # upi non-error socket
                print('Check "First MCERR Source" failed')
                _fail.append(f'First MCERR Source: core{core}')

        for i in range(int(_cpu_info.get("cores"))):    # UPI UCE Core Check
            if str(i) not in _cores:
                print(f"## FDMlog missing of UPI UCE: core={i}")
                # _fail.append(f"core{i}")
        return (not _fail) and (_err_detect)

    def system_hang(self):
        pass

    def maint_mem_ppr(self, socket: int, channel:int, dimm:int) -> bool:
        """
        1. Error Type: mainboard DIMM{socket}{channel}{dimm} Post Package Repair Event
        2. Support Check: socket, channel, dimm

        Parameters
        ----------
        socket: int
            ppr socket number
        channel: int
            ppr channel number
        dimm: int
            ppr dimm number

        Returns
        -------
        bool
            return True if PPR error found and all physical addrsss match, else False
        """

        maint_log = self.log_split(self.get_new_log(self.get_maintenance_log(), self.test_time, "\n"), "\n")
        print(f"## {len(maint_log)} error record in maintenance_log")
        phy_addr = []
        for _log in maint_log:
            if "Post Package Repair Event" not in _log:
                continue
            _addr = "".join(re.findall("mainboard DIMM(\d+) Post Package Repair Event", _log))
            if _addr not in phy_addr:
                phy_addr.append(_addr)
        if len(phy_addr) > 1:
            print("## Multiple addresses report PPR event, please double check")
            return False
        _socket, _channel ,_dimm = phy_addr[0]

        _fail = []
        if not self.compare(socket, _socket, name="socket"):
            _fail.append("socket")
        if not self.compare(channel, _channel, name="channel"):
            _fail.append("channel")
        if not self.compare(dimm, _dimm, name="dimm"):
            _fail.append("dimm")
        if not _fail:
            return True
        print(f"## Check PPR fail: {_fail}")

    def maint_mem_ce(self, *args) -> bool:
        """
        1. mainboard DIMM{socket}{channel}{dimm} CE overflow,
            rank num is {rank}.
        2. mainboard DIMM{socket}{channel}{dimm} FailDimmInfo,
            rank num is {rank},
            dev num is {dev},
            bank_group num is {bank_group},
            bank num is {bank}.
        3. mainboard DIMM{socket}{channel}{dimm} DDDC sparing.
           mainboard DIMM{socket}{channel}{dimm} Failure detected by Memory_CE_Bucket.

        Parameters
        ----------
        args: list
            list format as below for maintenance log check:
                ["{socket} {channel} {dimm} {rank} {bank_group} {bank} {dev}", count, event]
            Testcase Examples:
                ["0 0 0 0 0 0 1", 3, "DDDC sparing"], ["0 0 0 0 0 1 1", 3, "DDDC sparing"], ["0 0 0 0 3 1 3", 2, ""], ["0 0 0 0 3 2 4", 1, "Memory_CE_Bucket"]
            ["0 0 0 0 0 0 1", 3, "DDDC sparing"] means:
                socket0, channel0, dimm0, rank0, bank_group0, bank0, device1 have 3 maint log record, then follow a "DDDC sparing" event log
        Returns
        -------
        bool
            return True if all error sequence, address, event match with expected, else False
        """

        maint_log = self.log_split(self.get_new_log(self.get_maintenance_log(), self.test_time, "\n"), "\n")
        print(f"## {len(maint_log)} error record in maintenance_log")

        # Parse the maintenance log
        _mem_flag = "mainboard DIMM"
        _log_type = ["CE overflow", "FailDimmInfo"]
        _maint_event = ["DDDC sparing", "Memory_CE_Bucket"]

        overflow_log = []
        faildimm_log = []
        event_log = []

        for line in maint_log:
            if _mem_flag not in line:
                continue
            line_split = re.split(_mem_flag, line)
            _info = line_split[1]
            rank_id = "".join(re.findall('rank num is (\d)', _info))
            dev_id = "".join(re.findall('dev num is (\d+)', _info))
            bg_id = "".join(re.findall('bank_group num is (\d)', _info))
            ba_id = "".join(re.findall('bank num is (\d)', _info))

            if _log_type[0] in _info:
                _ce = f"{_info[0]} {_info[1]} {_info[2]} {rank_id}"
                overflow_log.append(_ce)
            elif _log_type[1] in _info:
                _fail_dimm = f"{_info[0]} {_info[1]} {_info[2]} {rank_id} {bg_id} {ba_id} {dev_id}"
                faildimm_log.append(_fail_dimm)

            if _maint_event[0] in _info:
                event_log.append(_maint_event[0])
            elif _maint_event[1] in _info:
                event_log.append(_maint_event[1])
            else:
                event_log.append("")

        # Check the maintenance log
        _fail = []
        if len(overflow_log) != len(faildimm_log):
            print("## Every [CE overflow] should follow a [FailDimmInfo]")
            _fail.append("ce_overflow != fail_dimm_info")

        overflow_expect = []
        faildimm_expect = []
        event_expect = []
        for arg in args:
            overflow_expect += [arg[0][:7]] * arg[1]
            faildimm_expect += [arg[0]] * arg[1]
            event_expect += [""]*arg[1]*2 + [arg[2]] if arg[2] else [""]*arg[1]*2

        for ci, cv in enumerate(overflow_expect):
            if ci+1 > len(overflow_log):
                _fail.append(f"ce_ov_index_miss={ci}")
                continue
            if not self.compare(cv, overflow_log[ci], name=f"CE Overflow addrress in {ci+1} records"):
                _fail.append(f"ce_ov_index={ci}")
        for di, dv in enumerate(faildimm_expect):
            if di+1 > len(faildimm_log):
                _fail.append(f"faildimm_index_miss={di}")
                continue
            if not self.compare(dv, faildimm_log[di], name=f"FailDimmInfo addrress in {di+1} records"):
                _fail.append(f"fail_dimm_index={di}")
        for ei, ev in enumerate(event_expect):
            if not ev:
                continue
            if ei+1 > len(event_log):
                _fail.append(f"fail_maint_event_miss={ev}")
                continue
            if not self.compare(ev.lower(), event_log[ei].lower(), name=f"Maintenabce Event in {ei+1} records"):
                _fail.append(f"fail_maint_event={ev}")
        if not _fail:
            return True
        print(f"## Check Maintenance log failed: {_fail}")

    def smi_storm(self, storm_list: list) -> bool:
        """
        Check If SMI Storm assert and the count is right

        Parameters
        ----------
        storm_list: list
            SMI Storm Times list, like [1,2,3, 1,2,3]

        Returns
        -------
        bool
            return True if SMI Storm asserted and the count match, else None
        """
        storm_flag = "CE_SMI_Mask_Times:"
        fdm_logs = self.log_split(self.get_new_log(self.get_fdm_log(), self.test_time))
        storm_list_read = []
        for _log in fdm_logs:
            _storm_assert = re.findall(f"{storm_flag}\s*(\d+)", _log)
            if _storm_assert:
                storm_list_read.append(int(_storm_assert[0][0]))
        return self.compare(storm_list, storm_list_read, "smi storm")


class OsStatus:
    def __init__(self, log_file):
        self.log = log_file

    def dmesg_no_err(self):
        pass

    def dmesg_mem_ce(self):
        pass

    def dmesg_pcie_ce(self):
        pass

    def lspci_ur(self, status=""):
        pass

