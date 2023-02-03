import logging

from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Pch Test Case
# TC 1200-1205
####################################


@core.test_case(("1200", "[TC1200] Testcase_GpioSetting_002", "BIOS启动阶段GPIO初始化测试"))
def Testcase_GpioSetting_002():
    """
    Name:       BIOS启动阶段GPIO初始化测试
    Condition:
    Steps:      1、上电启动检查启动阶段串口信息是否存在GPIO错误打印，有结果A。
    Result:     A：GPIO初始化正常，无错误打印。
    Remark:
    """
    try:
        assert BmcLib.force_reset()
        ser_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.BIOS_BOOT_COMPLETE, SutConfig.Env.BOOT_DELAY,
                                    SutConfig.Env.BOOT_DELAY)
        assert Msg.BIOS_BOOT_COMPLETE in ser_log
        assert MiscLib.msg_exclude(msg=ser_log, words=Msg.GPIO_ERR)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1201", "[TC1201] Testcase_UsbPort_001", "USB端口分组控制菜单检查"))
def Testcase_UsbPort_001():
    """
    Name:       USB端口分组控制菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，PCH Configuration页面下检查USB端口分组是否正确，有结果A；
                2、检查每组USB端口数量是否正确，可选值及默认值，有结果B；
    Result:     A：分组数量与产品软硬件接口文档一致。
                B：每组USB端口数量与产品软硬件接口文档一致，Enabled、Disabled可选，默认Enabled。
    Remark:     1、组名包含Front USB Control，Rear USB Control，Built-in USB Control三类。
                2、不同产品USB分组数及每组USB端口数量不同，参考软硬件接口文档定义。
    """
    usb_port_op = f"USB Port .*<(?:{Msg.ENABLE}|{Msg.DISABLE})>"

    def usb_ports_option(group: str, port_num: int, row_lines: list):
        if (port_num == 0) and (group not in row_lines):
            logging.info(f"Current sut have no USB group: {group}")
            return True
        if group not in row_lines:
            logging.error(f"USB group not found: {group}")
            return
        group_index = row_lines.index(group)
        group_ports = set()
        for line in row_lines[group_index+1:]:
            if re.search(usb_port_op, line):
                group_ports.add(line)
            else:
                break
        for port in group_ports:
            logging.info(f"{group} -> {port}")
        assert port_num == len(group_ports), f"USB group ports number mismatch: {group} = {port_num}"
        logging.info(f"USB group ports number match: {group} = {port_num}")
        return True

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PCH_CONFIG)
        assert SetUpLib.locate_option(Msg.USB_CONFIG)
        option_row_lines = SetUpLib.get_visiable_text(key=Key.ENTER)
        if BmcLib.get_fw_version().PRODUCT == SutConfig.Env.PROJECT_NAME:
            logging.debug("no front usb on 2P W/A")
            pass
        else:
            assert usb_ports_option(group='Front USB Port Control', port_num=Sys.USB_PORT_FRONT, row_lines=option_row_lines)
        assert usb_ports_option(group='Rear USB Port Control', port_num=Sys.USB_PORT_REAR, row_lines=option_row_lines)
        assert usb_ports_option(group='Built-in USB Port Control', port_num=Sys.USB_PORT_BUILDIN, row_lines=option_row_lines)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1202", "[TC1202] Testcase_SataHotplug_001", "默认开启SATA硬盘热插拔功能"))
def Testcase_SataHotplug_001():
    """
    Name:       默认开启SATA硬盘热插拔功能
    Condition:  1、默认配置；
                2、装备包已放置OS。
    Steps:      1、启动进Setup菜单，PCH Configuration界面下检查SATA Port口数量是否正确，有结果A；
                2、检查每个SATA Port口是否存在热插拔选项，有结果B；
                3、启动进OS，使用uniCfg读取每个SATA Port口热插拔变量值SataHotPlugController*[*]，检查是否使能，有结果C。
    Result:     A：SATA Port口数量与软硬件接口文档一致；
                B：SATA热插拔选项已隐藏；
                C：SATA热插拔开关默认使能。
    Remark:     1、变量名SataHotPlugController*[*]，*代表具体编号。
    """
    res_list = []
    try:
        assert SetUpLib.boot_to_default_os(delay=10)
        for i in SutConfig.Sys.HDDBP_port:
            if not Sut.UNITOOL.check(**{f"SataHotPlugController{SutConfig.Sys.HDDBP_controller}"
                                        f"[{i}]": 1}):
                res_list.append(f"Port {i} 热插拔未使能")
        assert len(res_list) == 0, f"{res_list}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1203", "[TC1203] Testcase_DefaultRtcTime_003", "Clear CMOS不恢复缺省时间测试"))
def Testcase_DefaultRtcTime_003():
    """
    Name:       Clear CMOS不恢复缺省时间测试
    Condition:
    Steps:      1、X86上电，按键进入Setup菜单。修改系统时间，保存退出；
                2、启动进Setup菜单，确认修改的选项已经生效，此时BMC Clear CMOS；
                3、单板重启上电，进Setup菜单，检查系统时间是否恢复默认值，有结果A。
    Result:     A：系统时间不会恢复默认。
    Remark:     1、RTC默认时间一般为TR3时间点
    """
    try:
        assert SetUpLib.boot_to_default_os()
        sut_time0 = MiscLib.date_time_delta(BmcLib.get_bmc_datetime(), days=1)
        assert PlatMisc.set_rtc_time_linux(sut_time0)
        assert SetUpLib.boot_to_setup()
        assert BmcLib.clear_cmos()
        assert SetUpLib.boot_to_setup()
        sut_time1 = BmcLib.get_bmc_datetime()
        assert MiscLib.time_str_offset(sut_time0, sut_time1) < SutConfig.Env.BOOT_DELAY * 2
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        PlatMisc.set_rtc_time_linux(None)


@core.test_case(("1204", "[TC1204] Testcase_DefaultRtcTime_004", "Clear CMOS恢复菜单配置测试"))
def Testcase_DefaultRtcTime_004():
    """
    Name:       Clear CMOS恢复菜单配置测试
    Condition:
    Steps:      1、X86上电，按键进入Setup菜单，修改部分选项为非默认值，保存重启后进入Setup菜单检查是否生效，有结果A；
                2、BMC命令行执行Clear cmos操作后重启单板进入Setup菜单，检查修改选项是否恢复默认值，有结果B。
    Result:     A：选项修改生效；
                B：选项恢复默认配置。
    Remark:
    """
    try:
        # set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.set_option_value(Msg.ACT_CPU_CORES, f"{int(SutConfig.Sys.CPU_CORES/2)}", save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.get_option_value(Msg.ACT_CPU_CORES) == f"{int(SutConfig.Sys.CPU_CORES/2)}"
        # set
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_PRO_CFG)
        assert SetUpLib.get_option_value(Msg.ACT_CPU_CORES) == "All"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1205", "[TC1205] Testcase_SpinUp_001", "错峰上电默认检查"))
def Testcase_SpinUp_001():
    """
    Name:       错峰上电默认检查
    Condition:  1、默认配置；
                2、已安装Linux系统；
                3、装备包已上传OS。
    Steps:      1、启动进OS，装备路径下执行"./uniCfg -r SataSpinUpController*[*]"命令读取spin up默认状态，有结果A。
    Result:     A：spin up默认使能。
    Remark:     1、变量名SataSpinUpController*[*]，*代表具体编号。
    """
    res_list = []
    try:
        assert SetUpLib.boot_to_default_os(delay=10)
        for i in SutConfig.Sys.HDDBP_port:
            if not Sut.UNITOOL.check(**{f"SataSpinUpController{SutConfig.Sys.HDDBP_controller}"
                                        f"[{i}]": 1}):
                res_list.append(f"Port {i} 未使能")
        assert len(res_list) == 0, f"{res_list}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

