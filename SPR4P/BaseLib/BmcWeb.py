import re
import os
import time
import logging
from functools import wraps
from pathlib import Path
from batf import var, MiscLib
from batf.WebLib import Chrome
from SPR4P.Config.PlatConfig import Msg
from SPR4P.Config import SutConfig
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

logging.getLogger("selenium").setLevel(logging.WARNING)


def bmc_login(func):
    """Class method decorator, login before func and logout after func"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            assert self.login()
            fun = func(*args, **kwargs)
            return fun
        except Exception as e:
            logging.error(e)
            self.screen_shot(filename=os.path.join(SutConfig.Env.LOG_DIR, var.get('current_test')))
        finally:
            self.logout_quit()
    return wrapper


class Url:
    HOME = "/#/navigate/home"  # 首页
    SYS_INFO = "/#/navigate/system/info/product"  # 系统信息
    MONITOR = "/#/navigate/system/monitor"  # 性能监控
    STORAGE = "/#/navigate/system/storage"  # 存储管理
    POWER = "/#/navigate/system/power"  # 电源功率
    FAN = "/#/navigate/system/fans"  # 风扇散热
    BIOS = "/#/navigate/system/bios"  # BIOS配置
    SEL = "/#/navigate/maintance/alarm"  # 告警事件
    SYS_LOG = "/#/navigate/maintance/systemlog"  # 系统日志
    IBMC_LOG = "/#/navigate/maintance/ibmclog"  # iBMC日志
    USER_INFO = "/#/navigate/user/localuser"  # 本地用户
    SECURE = "/#/navigate/user/security"  # 安全配置
    UPDATE = "/#/navigate/manager/upgrade"  # 固件升级
    CONFIG = "/#/navigate/manager/configupgrade"  # 配置更新


class BmcWeb(Chrome):
    def __init__(self, ip, user, password):
        chrome_driver = Path(__file__).parent.parent/"Resource/WebDriver/chromedriver.exe"
        super(BmcWeb, self).__init__(str(chrome_driver), interval=0, imp_wait=5)
        self.host = f"https://{ip}"
        self.user = user
        self.password = password
        self.is_login = False
        self.options.add_argument('lang=en_US')

    def login(self):
        self.open_page(self.host)
        self.max_window()
        assert self.send_element("css", "#account", self.user, "用户名")
        assert self.send_element("css", "#loginPwd", self.password, "密码")
        assert self.click_element("css", "#btLogin", "登录")
        if self.wait_element("css", "#navHome", 30, "首页"):
            self.is_login = True
            return True
        logging.error("BMC Web login failed")
        self.is_login = False

    def logout(self):
        time.sleep(0.5)
        assert self.move_to_element("css", "#localUserIcon")
        assert self.click_until("css", "#loginOut")
        time.sleep(0.5)
        self.is_login = False

    def logout_quit(self):
        try:
            self.logout()
        except Exception as e:
            logging.error(e)
        finally:
            self.quit_browser()
            self.is_login = False

    def goto_url(self, url_name):
        assert self.new_page(url_name)
        assert self.switch_page_index(-1)
        self.wait_loading()
        return True

    def wait_loading(self, timeout=15):
        if self.wait_element_not_exist("id", "loading", timeout):
            time.sleep(0.5)
            return True

    def wait_operate_success(self, timeout=15):
        return self.wait_element("css", "#ti_auto_id_1_label", timeout=timeout, name="Operate Successfully")

    @bmc_login
    def processor_info(self) -> list:
        """
        Return list of Processor Model
        For Example:
        ['Genuine Intel(R) CPU 0000%@', 'Genuine Intel(R) CPU 0000%@']
        """
        assert self.goto_url(Url.SYS_INFO)
        assert self.click_until("css", "#systemInfoProcessor")
        self.wait_loading()
        proc_list = []
        proc_found = self.find_element("css", f"#processorTable td:nth-child(4) > span", "CPU型号")
        if not proc_found:
            return proc_list
        for proc in proc_found:
            proc_list.append(proc.text)
        return proc_list

    @bmc_login
    def memory_info(self) -> dict:
        """
        Return dict of Memory Info
        For Example:
        {
            "DIMM000": {"Size":32, "CurrentSpeed":4400, "MaxSpeed":4800, "RankCount":2, "DimmBitWidth":80}
            "DIMM001": ...
        }
        """
        assert self.goto_url(Url.SYS_INFO)
        assert self.click_until("css", "#systemInfoMemory")
        self.wait_loading()
        mem_list = {}
        dimm_found = self.find_element("css", "#memoryTable td:nth-child(1)")
        if not dimm_found:
            return mem_list

        self.js_click("css", "#detailInfo0 a i")
        dimm_rank = self.get_text("css", "#detailInfo0 div:nth-child(12) span:nth-child(2)", name="Rank数量")
        dimm_rank_str = "".join(re.findall("(\d+) rank", dimm_rank)) if dimm_rank else None

        dimm_bw = self.get_text("css", "#detailInfo0 div:nth-child(10) span:nth-child(2)", name="内存位宽")
        dimm_bitwidth = "".join(re.findall("(\d+) bit", dimm_bw)) if dimm_bw else None
        self.js_click("css", "#detailInfo0 a i")

        for row, dimm in enumerate(dimm_found):
            dimm_loc = self.get_text("css", f"#memoryTable tr:nth-child({row+1}) > td:nth-child(2)", name="内存位置")
            dimm_size = self.get_text("css", f"#memoryTable tr:nth-child({row+1}) > td:nth-child(4)", name=f"{dimm_loc}:内存大小")
            dimm_speed_real = self.get_text("css", f"#memoryTable tr:nth-child({row+1}) > td:nth-child(5)", name=f"{dimm_loc}:配置速度")
            dimm_speed_max = self.get_text("css", f"#memoryTable tr:nth-child({row+1}) > td:nth-child(6)", name=f"{dimm_loc}:最大速度")
            mem_list[dimm_loc] = {"Size": dimm_size,
                                  "CurrentSpeed": dimm_speed_real,
                                  "MaxSpeed": dimm_speed_max,
                                  "RankCount": int(dimm_rank_str) if dimm_rank_str else None,
                                  "DimmBitWidth": int(dimm_bitwidth) if dimm_bitwidth else None}
        return mem_list

    @bmc_login
    def bios_version(self) -> str:
        """
        return str of BIOS Version
        For Example:
        '2.00.15'
        """
        return self.get_text("css", "#homeDetailForm tr:nth-child(2) > td:nth-child(7) span", name="BIOS固件版本")

    @bmc_login
    def bmc_version(self) -> str:
        """
        return str of BIOS Version
        For Example:
        '3.03.07.83'
        """
        return self.get_text("css", "#homeDetailForm tr:nth-child(2) > td:nth-child(3) span", name="iBMC固件版本")

    @bmc_login
    def product_info(self):
        """
        Return the object of Product Information
        """
        class Product:
            name = None
            product_manuf = None
            sn = None
            bmc_ver = None
            bios_ver = None
            cpld_ver = None
            board_manuf = None
            pch = None

        assert self.goto_url(Url.SYS_INFO)
        Product.name = self.get_text("css", "#productInfoName", name="产品名称")
        Product.product_manuf = self.get_text("css", "#productManufacturer", name="生产厂商")
        Product.sn = self.get_text("css", "#productSerialNum", name="产品序列号")
        Product.bmc_ver = self.get_text("css", "#ibmcVersion", name="iBMC固件版本")
        Product.bios_ver = self.get_text("css", "#biosVersion", name="BIOS版本")
        Product.cpld_ver = self.get_text("css", "#cpldVersion", name="CPLD版本")
        Product.board_manuf = self.get_text("css", "#boardManu", name="主板厂商")
        Product.pch = self.get_text("css", "#pchVersion", name="PCH型号")
        return Product

    @bmc_login
    def get_boot_info(self):
        """
        Return the object of Boot Device Information
        Refer to the text of BMC Web display in English Language
        """
        class Boot:
            mode = None  # "UEFI" / "Legacy"
            overwrite = None
            order = []

        assert self.goto_url(Url.BIOS)
        Boot.mode = Msg.UEFI if self.find_element("css", "#bootModeUEFI").is_selected() else Msg.LEGACY
        Boot.overwrite = self.get_text("css", "#bootMediaId_dominator_input section", name="启动优先级")
        for _order in self.find_element("css", "#bootSequenceId li > div > span", name="启动顺序"):
            Boot.order.append(_order.text)
        return Boot

    @bmc_login
    def set_boot_overwrite(self, device: str = None, once=True, mode=None):
        """
        Set the boot overwrite device and boot order.
        device name refer to BMC Web with English language
            - 'Hard Drive'
            - 'CD/DVD'
            - 'FDD/Removable Device'
            - 'PXE'
            - 'BIOS Settings'
            - 'No Override'
        """
        assert self.goto_url(Url.BIOS)
        # Set Boot Mode
        if mode:
            mode = mode.lower()
            ele_mode = {"legacy": '[for="bootModeLegacy"]', "uefi": '[for="bootModeUEFI"]'}
            assert mode in ele_mode, f"Mode not in support list {list(ele_mode.keys())}"
            assert self.click_until("css", ele_mode[mode], name=mode)
            self.wait_loading()
        # Set Overwrite
        if device:
            assert self.click_until("css", "#bootMediaId_dominator_input > section", name="启动优先级")
            self.wait_loading()
            dev_list = []
            for index, dev in enumerate(self.find_element("css", ".ti3-drop-list-ul li section")):
                dev_list.append(self.get_text("css", f"#bootMediaId_droplist_list_{index} section"))
            if device not in dev_list:
                raise TypeError(f"Boot Overwrite option'{device}' not in support list: {dev_list}")
            dev_index = dev_list.index(device)
            assert self.click_element("css", f"#bootMediaId_droplist_list_{dev_index} section", name=device)
        if once:
            assert self.click_element("css", "[for=bootMediaOne]", name="单次有效")
        else:
            assert self.click_element("css", "[for=bootMediaPermanent]", name="永久有效")
        assert self.click_element("css", "#bootDeviceSaveId", name="保存")
        self.wait_operate_success()
        return True

    @bmc_login
    def get_power_policy(self):
        """
        Return str of Current Power Policy
        Refer to BMC Web display in English Language
        For Example:
        "On" / "Off" / "Restore"
        """
        assert self.goto_url(Url.POWER)
        assert self.click_until("css", "#powerTabs_powerControlTab_a")
        self.wait_loading()
        if self.find_element("css", "#TurnOn", name="Power On").is_selected():
            return 1  # Power On
        elif self.find_element("css", "#StayOff", name="Power On").is_selected():
            return 0  # Power Off
        elif self.find_element("css", "#RestorePreviousState", name="Power On").is_selected():
            return -1  # Last State

    @bmc_login
    def set_power_policy(self, mode: int):
        """
        1:   Power On
        0:   Power Off
        -1:  Restore to Last State
        """
        support_mode = {1: "[for=TurnOn]", 0: "[for=StayOff]", -1: "[for=RestorePreviousState]"}
        assert mode in support_mode, f"Power policy mode not in support list: {support_mode}"
        assert self.goto_url(Url.POWER)
        assert self.click_until("css", "#powerTabs_powerControlTab_a")
        self.wait_loading()
        if not self.find_element("css", support_mode[mode], name="System State Upon Power Supply").is_selected():
            self.js_click("css", support_mode[mode], name="System State Upon Power Supply")
        assert self.js_click("css", "#powerContorlSaveId", name="保存")
        return True

    @bmc_login
    def is_ocp_exist(self):
        assert self.goto_url(Url.SYS_INFO)
        assert self.click_until("css", "#systemInfoOthers")
        self.wait_loading()
        ocp_info = self.get_text("id", "OCPCardNode", name="OCP卡")
        if re.search("[1-9]/\d", ocp_info):
            logging.info("OCP Card exist in current system")
            return True
        logging.info("OCP Card not exist in current system")
        return False

    @bmc_login
    def get_ibmc_log(self, from_time: str = None, operate=None, running=None, security=None) -> list:
        """
        获取BMC网页上的操作日志/运行日志/安全日志,其中的任意一种或多种
        返回第一页的15条日志内容(序号,产生时间,详细信息), 如果设置起始时间,则只返回某个时间点之后的日志内容
        For Example:
        [[index, '2022-07-26 14:01:03', "Security,BIOS,Check Password error"], [...], [...]]
        """
        if not (running or security or operate):
            raise TypeError(f"At least one type of bmc log need to be specified: [operate/running/security]")

        ibmc_dict = {"操作日志": "#logTabs_operate_a span",
                     "运行日志": "#logTabs_running_a span",
                     "安全日志": "#logTabs_security_a span"}
        column_no = {"Generated": 5, "No.": 1, "Details": 6}
        log_types = []
        if operate:
            log_types.append("操作日志")
        if running:
            log_types.append("运行日志")
        if security:
            log_types.append("安全日志")

        assert self.move_to_element("css", "#navMaintance", name="维护诊断")
        assert self.click_until("css", "#secMainIbmcLog", name="iBMC日志")
        assert self.wait_loading()
        log_list = []
        for log in log_types:
            assert self.click_until("css", ibmc_dict[log], name=log)
            assert self.wait_loading()
            logs = self.find_element("css", "#tableComponent table tbody tr", name="第一页")
            head = self.find_element("css", "#tableComponent table thead th")
            for col, h in enumerate(head):
                if h.text in column_no:
                    column_no[h.text] = col+1  # 更新不同页面的索引列,只关注 "序号,产生时间,详细信息"
            time_n = column_no['Generated']
            num_n = column_no['No.']
            detail_n = column_no['Details']
            for row, line in enumerate(logs):
                date = self.get_text("css", f"#tableComponent table tbody tr:nth-child({row + 1}) td:nth-child({time_n})")
                if from_time and MiscLib.time_str_offset(from_time, date) < 0:
                    break
                index = self.get_text("css", f"#tableComponent table tbody tr:nth-child({row + 1}) td:nth-child({num_n})")
                log = self.get_text("css", f"#tableComponent table tbody tr:nth-child({row + 1}) td:nth-child({detail_n})")
                log_list.append([int(index), date, log])
        if not log_list:
            raise Exception("Failed to get security logs from bmc")
        return log_list

    def get_selected(self, ratio_elements):
        for elem in ratio_elements:
            if self.find_element("css", elem).is_selected():
                return elem

    @bmc_login
    def get_network(self):
        class Net:
            protocol = None
            class IPv4:
                manual = None
                address = None
                netmask = None
                gateway = None
                mac = None
            class IPv6:
                manual = None
                address = None
                prefix = None
                gateway = None
                addr_id = None

        assert self.move_to_element("css", "#navIbmcManager")
        assert self.click_until("css", "#secNetworkConfig")
        self.wait_loading()
        proto_elements = {"#chooseIPv4": "IPv4", "#chooseIPv6": "IPv6", "#chooseIPv4AndIPv6": "IPv4/IPv6"}
        manual_ipv4 = {"#StaticIpv4": "Static", "#DHCPIpv4": "DHCP"}
        manual_ipv6 = {"#StaticIpv6": "Static", "#DHCPv6Ipv6": "DHCP"}
        Net.protocol = proto_elements.get(self.get_selected(proto_elements.keys()))
        if "IPv4" in Net.protocol:
            Net.IPv4.manual = manual_ipv4.get(self.get_selected(manual_ipv4.keys()))
            ipv4_addr = ["#ipV4_0", "#ipV4_1", "#ipV4_2", "#ipV4_3"]
            ipv4_mask = ["#ipMaskCode_0", "#ipMaskCode_1", "#ipMaskCode_2", "#ipMaskCode_3"]
            ipv4_gateway = ["#ipGateway_0", "#ipGateway_1", "#ipGateway_2", "#ipGateway_3"]
            ipv4_mac = "#netMacAddress"
            Net.IPv4.address = ".".join([self.find_element("css", ad4).get_attribute("value") for ad4 in ipv4_addr])
            Net.IPv4.netmask = ".".join([self.find_element("css", ms4).get_attribute("value") for ms4 in ipv4_mask])
            Net.IPv4.gateway = ".".join([self.find_element("css", gt4).get_attribute("value") for gt4 in ipv4_gateway])
            Net.IPv4.mac = self.get_text("css", ipv4_mac)

        if "IPv6" in Net.protocol:
            Net.IPv6.manual = manual_ipv6.get(self.get_selected(manual_ipv6.keys()))
            ipv6_addr = "#ipAddressIdV6"
            ipv6_prefix = "#maskCodeIdV6"
            ipv6_gateway = "#gatewayIdV6"
            ipv6_add_id = "#addressIdV6"
            Net.IPv6.address = self.find_element("css", ipv6_addr).get_attribute("value")
            Net.IPv6.prefix = self.find_element("css", ipv6_prefix).get_attribute("value")
            Net.IPv6.gateway = self.find_element("css", ipv6_gateway).get_attribute("value")
            Net.IPv6.addr_id = self.get_text("css", ipv6_add_id)

        return Net

    @bmc_login
    def set_network(self, protocol, dhcp4=False, addr4=None, dhcp6=False, addr6=None):
        """
        protocol: 设置网络协议为["IPv4", "IPv6", "IPv4/IPv6"]
        dhcp4:    设置IPV4为DHCP模式.
        dhcp6:    设置IPV6为DHCP模式.
        addr4:    IPv4地址，需要包括['IP', 'MASK', 'GATEWAY'], 静态IPv4模式才需要传参
        addr6:    IPv6地址，需要包括['IP', 'MASK', 'GATEWAY'], 静态IPv6模式才需要传参
        """
        protocol_support = ["IPv4", "IPv6", "IPv4/IPv6"]
        assert protocol in protocol_support, f"Invalid protocol: {protocol}, support {protocol_support}"
        assert self.move_to_element("css", "#navIbmcManager")
        assert self.click_until("css", "#secNetworkConfig")
        self.wait_loading()
        proto_elements = {"IPv4": "#chooseIPv4_radio", "IPv6": "#chooseIPv6_radio", "IPv4/IPv6": "#chooseIPv4AndIPv6_radio"}
        if protocol in proto_elements:
            assert self.click_until("css", proto_elements[protocol])
        manual_ele = {"IPv4": {"Static": "#StaticIpv4_radio", "DHCP": "#DHCPIpv4_radio"},
                      "IPv6": {"Static": "#StaticIpv6_radio", "DHCP": "#DHCPv6Ipv6_radio"}}
        action = ActionChains(self.browser)
        if "IPv4" in protocol:
            if dhcp4:
                logging.info("Set DHCP IPV4 address")
                assert self.click_element("css", manual_ele["IPv4"]["DHCP"])
            else:
                logging.info("Set Static IPV4 address")
                assert isinstance(addr4, list) and len(
                    addr4) == 3, f"Invalid IPv4 addr: {addr4}, should be list like ['IP', 'MASK', 'GATEWAY']"
                assert self.click_element("css", manual_ele["IPv4"]["Static"])
                ipv4_addr = ["#ipV4_0", "#ipV4_1", "#ipV4_2", "#ipV4_3"]
                ipv4_mask = ["#ipMaskCode_0", "#ipMaskCode_1", "#ipMaskCode_2", "#ipMaskCode_3"]
                ipv4_gateway = ["#ipGateway_0", "#ipGateway_1", "#ipGateway_2", "#ipGateway_3"]
                self.click_element("css", ipv4_addr[0])
                action.send_keys(Keys.BACKSPACE * 3)
                action.perform()
                action.send_keys(addr4[0])
                action.perform()
                self.click_element("css", ipv4_mask[0])
                action.send_keys(Keys.BACKSPACE * 3)
                action.perform()
                action.send_keys(addr4[1])
                action.perform()
                self.click_element("css", ipv4_gateway[0])
                action.send_keys(Keys.BACKSPACE * 3)
                action.perform()
                action.send_keys(addr4[2])
                action.perform()
        if "IPv6" in protocol:
            if dhcp6:
                logging.info("Set DHCP IPV6 address")
                assert self.click_element("css", manual_ele["IPv6"]["DHCP"])
            else:
                logging.info("Set Static IPV6 address")
                assert isinstance(addr6, list) and len(
                    addr6) == 3, f"Invalid IPv6 addr: {addr6}, should be list like ['IP', 'MASK', 'GATEWAY']"
                assert self.click_element("css", manual_ele["IPv6"]["Static"])
                ipv6_addr = "#ipAddressIdV6"
                ipv6_prefix = "#maskCodeIdV6"
                ipv6_gateway = "#gatewayIdV6"
                assert self.send_element("css", ipv6_addr, addr6[0])
                assert self.send_element("css", ipv6_prefix, addr6[1])
                assert self.send_element("css", ipv6_gateway, addr6[2])
        assert self.js_click("css", "#protocolButton", name="保存")
        assert self.wait_element("css", "#netProtocol_ok_btn", 10)
        assert self.click_element("css", "#netProtocol_ok_btn", name="确认")
        return True

    @bmc_login
    def get_tpm_info(self):
        assert self.goto_url(Url.SYS_INFO)
        assert self.click_until("css", "#systemInfoOthers")
        self.wait_loading()
        assert self.click_element("css", "#SecurityModuleNode")
        self.wait_loading()
        if not self.element_exist("css", "#tableBody"):
            logging.info("TPM信息不存在")
            return {}
        logging.info("TPM卡在位")
        protocol = self.get_text("css", "#tableBody td:nth-child(1)", name="协议类型")
        ver = self.get_text("css", "#tableBody td:nth-child(2)", name="协议版本")
        vendor = self.get_text("css", "#tableBody td:nth-child(3)", name="厂商")
        selftest = self.get_text("css", "#tableBody td:nth-child(5)", name="自检结果")
        return {"Protocol": protocol, "Version": ver, "Vendor": vendor, "selftest": selftest}

    @bmc_login
    def set_dynamic_power_saving(self, mode):
        assert self.goto_url(Url.BIOS)
        assert self.click_until("css", "#biosTabs_energyTab_a", name="动态节能设置")
        self.wait_loading()
        assert self.click_until("css", "#Performance\ Profile_dominator_btn", name="Performance Profile")
        mode_support = {}
        drop_down_op = self.find_element("css", ".ti3-dropdown-option", name="节能模式列表")
        for index, mode_name in enumerate(drop_down_op):
            mode_support[mode_name.text] = index
        assert mode in mode_support, f"Mode {mode} not in support list: {list(mode_support.keys())}"
        assert self.click_until("css", f"#Performance\ Profile_droplist_list_{mode_support[mode]} > section", name=mode)
        assert self.click_until("css", "#energySaveId", name="保存")
        self.wait_loading()
        self.wait_operate_success()
        return True


BMC_WEB = BmcWeb(SutConfig.Env.BMC_IP, SutConfig.Env.BMC_USER, SutConfig.Env.BMC_PASSWORD)

