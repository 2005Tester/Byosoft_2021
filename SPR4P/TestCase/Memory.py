from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Memory Test Case
# TC 1100-1129
####################################


def _cke_idle_timer_count(cke_idle_set_int):
    factor = int(1 / (SutConfig.Sys.MEM_FREQ / 2) * 10000000)
    cke_idle_timer = ((cke_idle_set_int * 1000 * 1000) // ((factor + 5) // 10) + 998) // 1000
    return cke_idle_timer


def _check_mem_freq_in_post_log(mem_freq):
    mrc_mem_freq_flag = f"DDR Freq[ \|]*DDR5-{mem_freq}"
    return SetUpLib.wait_boot_msgs(mrc_mem_freq_flag)


@core.test_case(("1100", "[TC1100] Testcase_MemoryCompa_001", "内存初始化测试"))
def Testcase_MemoryCompa_001():
    """
    Name:       内存初始化测试
    Condition:  1、单板满插内存。
    Steps:      1、单板启动检查MRC阶段内存拓扑表，内存型号、容量、厂家、位宽等信息，结果A；
                2、启动按DEL进Setup菜单，进入Memory界面，查看内存槽位、型号、容量、厂家、位宽等信息，有结果A；
    Result:     A：内存信息正确。
    Remark:     1、查看MRC阶段内存具体信息需要开全打印。
    """
    try:
        assert BmcLib.force_reset()
        mem_info = SerialLib.cut_log(Sut.BIOS_COM, Msg.CPU_RSC_ALLOC, "STOP_DIMMINFO_SYSTEM_TABLE",
                                     duration=180, timeout=SutConfig.Env.BOOT_DELAY)
        assert mem_info, "empty mem info"
        dimm_size = f"{SutConfig.Sys.DIMM_SIZE}GB"
        dimm_rank_bw = f"{SutConfig.Sys.DIMM_RANK_TYPE[2:]}\s+{SutConfig.Sys.DIMM_RANK_TYPE[0:2]}"
        dimm_type = f"DDR5 {SutConfig.Sys.DIMM_TYPE}"
        dimm_freq = f"{SutConfig.Sys.DIMM_FREQ}\s+(?:\w+-){{2,}}"
        dimm_vendor = f"DIMM: {SutConfig.Sys.DIMM_VENDOR}"
        mem_size = f"Active Memory.+?{SutConfig.Sys.MEM_SIZE}GB"
        for dimm_check in [dimm_size, dimm_rank_bw, dimm_type, dimm_freq, dimm_vendor]:
            assert len(re.findall(dimm_check, mem_info)) == SutConfig.Sys.DIMM_CNT, f"{dimm_check}"
        assert re.search(mem_size, mem_info), "mem_size"
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG + [Msg.MEM_TOP], Key.UP, 15, "DIMM000")
        assert SetUpLib.verify_info(SutConfig.Sys.DIMM_INFO, trycounts=65)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1101", "[TC1101] Testcase_MemoryCompa_005", "SMBIOS TYPE17测试"))
def Testcase_MemoryCompa_005():
    """
    Name:       SMBIOS TYPE17测试
    Condition:  1、满插内存条。
    Steps:      1、单板启动进OS，dmidecode -t 17查看TYPE17信息；
                2、BMC Web界面查看内存信息，有结果A。
    Result:     A：内存所在槽位、容量、频率、RANK数等信息正确。
    Remark:
    """
    try:
        dimm_current_speed = f"{SutConfig.Sys.MEM_FREQ} MT/s"
        dimm_max_speed = f"{SutConfig.Sys.DIMM_FREQ} MT/s"
        dimm_size_g = f"{SutConfig.Sys.DIMM_SIZE} GB"
        dimm_size_m = f"{SutConfig.Sys.DIMM_SIZE * 1024} MB"

        assert SetUpLib.boot_to_default_os()
        type17 = SshLib.execute_command(Sut.OS_SSH, "dmidecode -t 17")
        assert type17, "Invalid smbios type17 data"
        type17_list = PlatMisc.smbios_to_dict(type17)["type17"]
        for slot in type17_list:
            locator = "".join(re.findall("DIMM(\d+)", slot["Locator"]))
            if locator not in SutConfig.Sys.DIMM_POP:
                assert slot["Size"] == "No Module Installed", f"slot fail: DIMM{locator} should not installed"  # 槽位
                continue
            assert slot["Speed"] == dimm_max_speed, f"Speed fail: DIMM{locator}"  # 频率
            assert slot["Configured Memory Speed"] == dimm_current_speed, f"Configured Memory Speed fail: DIMM{locator}"  # 频率
            assert slot["Size"] == dimm_size_g, f"Size fail: DIMM{locator}"  # 容量
            assert slot["Rank"] == f"{SutConfig.Sys.DIMM_RANK_CNT}", f"Rank fail: DIMM{locator}"  # RANK数

        mem_info_web = BMC_WEB.memory_info()
        for dimm_loc, dimm_info in mem_info_web.items():
            assert dimm_loc in [f"DIMM{loc}" for loc in SutConfig.Sys.DIMM_POP], f"Web Locator fail: {dimm_loc}"
            assert dimm_info["Size"] == dimm_size_m, f"Web Size fail: {dimm_loc}"
            assert dimm_info["CurrentSpeed"] == dimm_current_speed, f"Web CurrentSpeed fail: {dimm_loc}"
            assert dimm_info["MaxSpeed"] == dimm_max_speed, f"Web MaxSpeed fail: {dimm_loc}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1102", "[TC1102] Testcase_MemoryCompa_006", "内存容量一致性测试"))
def Testcase_MemoryCompa_006():
    """
    Name:       内存容量一致性测试
    Condition:  1、满插内存条。
    Steps:      1、单板启动进OS，free -m查看OS下内存容量，检查是否与实际容量一致，有结果A；
                2、reboot系统，重复步骤1。
    Result:     A：每次重启OS下内存容量与实际一致。
    Remark:     
    """
    try:
        for t in range(2):
            assert SetUpLib.boot_to_default_os()
            free_m = SshLib.execute_command(Sut.OS_SSH, "free -m")
            assert free_m, "exec cmd 'free -m' fail"
            total_m = "".join(re.findall("Mem:\s+(\d+)\s+", free_m))
            assert total_m, "get total free memory size fail"
            free_mem_reduced = SutConfig.Sys.MEM_SIZE - int(total_m) // 1024
            # 空闲内存为随机值，但一般只是少一小部分; 总内存与空闲内存之差应该小于单根内存的大小，以确保重启时没有丢内存
            assert free_mem_reduced < SutConfig.Sys.DIMM_SIZE, f"Check free memory reduced fail: {free_mem_reduced}GB"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1103", "[TC1103] Testcase_MemoryCompa_008", "内存Margin功能测试"))
def Testcase_MemoryCompa_008():
    """
    Name:       内存Margin功能测试
    Condition:  1、已安装支持装备脚本OS。
    Steps:      1、OS下uniCfg打开Margin开关，设置打印级别为max；
                2、复位系统，检查Margin测试情况，有结果A;
                3、多次重启，查看Margin测试情况，有结果A。
    Result:     A：Margin测试正常完成。
    Remark:     
    """
    try:
        cpu_with_dimm = {dimm[0] for dimm in Sys.DIMM_POP}
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.RMT_EN)
        assert BmcLib.force_reset()
        ser_rmt_list = []
        for cpu in cpu_with_dimm:
            rmt_per_cpu = SerialLib.cut_log(Sut.BIOS_COM, Msg.RMT_START, Msg.RMT_END, 15,
                                            timeout=SutConfig.Env.BOOT_RMT)
            assert rmt_per_cpu, f"Fail to get RMT data for cpu{cpu}"
            ser_rmt_list.append(rmt_per_cpu)
        assert ser_rmt_list, f"No RMT data found in serial log after wait {SutConfig.Env.BOOT_RMT}s"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1104", "[TC1104] Testcase_MemoryCompa_010", "内存mirror模式功能测试"))
def Testcase_MemoryCompa_010():
    """
    Name:       内存mirror模式功能测试
    Condition:  1、内存插法符合mirror模式要求。
    Steps:      1、启动进Setup菜单，打开mirror模式，保存退出；
                2、检查MRC内存拓扑表中，内存模式是否是mirror模式，有结果A。
    Result:     A：mirror模式正常开启。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os(delay=10)
        assert Sut.UNITOOL.write(**BiosCfg.ADDDC_DIS)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG + [Msg.MEM_RAS_CFG], Key.UP, 15, "")
        assert SetUpLib.set_option_value(Msg.MIRROR_MODE, Msg.FULL_MIRROR, save=True)
        assert SerialLib.is_msg_present_clean(Sut.BIOS_COM, f"Total Memory\s+: {SutConfig.Sys.MEM_SIZE // 2}GB",
                                              delay=SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1105", "[TC1105] Testcase_MemoryCompa_011", "长时间powercycle测试"))
def Testcase_MemoryCompa_011():
    """
    Name:       长时间powercycle测试
    Condition:  1、满插内存条。
    Steps:      1、执行powercycle，系统启动进OS，反复执行10次，有结果A。
    Result:     A：系统正常启动进OS。
    Remark:     
    """
    try:
        for i in range(10):
            assert BmcLib.force_power_cycle()
            time.sleep(30)
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1106", "[TC1106] Testcase_MemoryCompa_012", "长时间reboot测试"))
def Testcase_MemoryCompa_012():
    """
    Name:       长时间reboot测试
    Condition:  1、满插内存条。
    Steps:      1、OS下执行reboot，系统启动进OS，反复执行10次，有结果A。
    Result:     A：系统正常启动进OS。
    Remark:     
    """
    try:
        assert BmcLib.force_reset()
        for i in range(10):
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
            SshLib.execute_command(Sut.OS_SSH, "reboot")
            time.sleep(30)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1107", "[TC1107] Testcase_MemPower_003", "CKE Power Down设置菜单检查"))
def Testcase_MemPower_003():
    """
    Name:       CKE Power Down设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，电源管理界面下查看是否存在CKE Power Down选项，检查可选值及默认值，有结果A。
    Result:     A：存在CKE Power down选项，Enabled、Disabled可选，默认Disabled。
    Remark:     
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.load_default_in_setup(save=False)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.UP, 15, Msg.CKE)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.CKE, Key.DOWN, 5), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.get_option_value(Msg.CKE, Key.DOWN, 5) == Msg.DISABLE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1108", "[TC1108] Testcase_MemPower_004", "开启CKE Power down测试"))
def Testcase_MemPower_004():
    """
    Name:       开启CKE Power down测试
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，使能CKE Power Down选项，检查菜单联动关系，有结果A；
                2、F10保存重启，检查能否正常启动进OS，有结果B。
    Result:     A：CKE Power down使能后，开放CKE Feature菜单；
                B：能正常启动进OS。
    Remark:     
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.load_default_in_setup(save=False)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.UP, 15, Msg.CKE)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.CKE, Key.DOWN, 5), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.get_option_value(Msg.CKE, Key.DOWN, 5) == Msg.DISABLE
        assert SetUpLib.set_option_value(Msg.CKE, Msg.ENABLE, save=True)  # Set
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.UP, 15, Msg.CKE)
        assert SetUpLib.get_option_value(Msg.CKE, Key.DOWN, 5) == Msg.ENABLE  # Check
        SetUpLib.send_key(Key.CTRL_ALT_DELETE)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)  # Check Boot
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1109", "[TC1109] Testcase_MemPower_005", "CKE Feature参数检查"))
def Testcase_MemPower_005():
    """
    Name:       CKE Feature参数检查
    Condition:  1、CKE Power Down选项已开启。
    Steps:      1、启动进Setup菜单，检查CKE Feature菜单下各参数默认状态，有结果A；
                2、设置CKE Idle Timer为范围外的值，检查能否设置成功，有结果B；
                3、设置APD选项为Enabled，查看PPD选项状态，有结果C；
                4、设置PPD选项为Enabled，查看APD选项状态，有结果D。
    Result:     A：CKE Idle Timer默认20ns，APD默认Disabled，PPD默认Enabled；
                B：范围外选项无法设置成功（数值范围参考Help信息）；
                C：APD选项Enabled时，PPD选项隐藏或置灰；
                D：APD选项Disabled时才可设置PPD为Enabled。
    Remark:     
    """
    try:
        cke_timer_range = (0, 255)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.UP, 15, Msg.CKE)
        assert SetUpLib.set_option_value(Msg.CKE, Msg.ENABLE)
        assert SetUpLib.enter_menu([Msg.CKE_FEATURE], Key.DOWN, 10, Msg.CKE_IDLE_TIMER)
        cke_idle_default = SetUpLib.get_option_value(Msg.CKE_IDLE_TIMER, Key.DOWN, 5, integer=True)
        assert cke_idle_default == Msg.VAL_CKE_IDLE, "CKE default value!= 20"
        SetUpLib.send_key(Key.ENTER)
        cke_set_value = f"{cke_timer_range[1] + 1}"
        SetUpLib.send_data_enter(cke_set_value)
        assert SetUpLib.get_option_value(Msg.CKE_IDLE_TIMER, Key.DOWN, try_counts=5, integer=True) != cke_set_value
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.PPD, Key.DOWN, 5), [Msg.ENABLE, Msg.DISABLE])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1110", "[TC1110] Testcase_MemPower_006", "CKE Feature参数默认时寄存器检查"))
def Testcase_MemPower_006():
    """
    Name:       CKE Feature参数默认时寄存器检查
    Condition:  1、默认配置。
    Steps:      1、启动进OS，使用lspci -s "BDF"  -xxxx命令查询6A0~6A3四字节，检查Bit24是否为0，四字节默认值是否正确，有结果A。
    Result:     A：Bit24为0，四字节由低到高为80 00 00 10（HY3.0 CPU默认为0080 1000）。
    Remark:     1、BDF号和内存所插的位置相关对应关系参考Intel手册，B(2)表示CPU的Stk2，如V5服务器CPU0则B(2)表示0x3A：
                DIMM000----B(2):A.2
                DIMM010----B(2):A.6
                DIMM020----B(2):B.2
                DIMM030----B(2):C.2
                DIMM040----B(2):C.6
                DIMM050----B(2):D.2
    """
    try:
        assert SetUpLib.boot_to_default_os()
        cke_idle_timer = _cke_idle_timer_count(int(Msg.VAL_CKE_IDLE))
        read_cke_reg = PlatMisc.cscripts_rw(SutConfig.Sys.CS_CKE)
        assert read_cke_reg.get("ddrt_cke_en") == 0, "ddrt_cke_en"  # bit 24
        assert read_cke_reg.get("ppd_en") == 0, "ppd_en"  # bit 9
        assert read_cke_reg.get("apd_en") == 0, "apd_en"  # bit 8
        if read_cke_reg.get("cke_idle_timer") != cke_idle_timer:  # bit 0~7
            logging.warning(f"Default cke_idle_timer={cke_idle_timer}, value mismatch possible due to DIMM 'RTD' limit")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1111", "[TC1111] Testcase_MemPower_007", "PPD使能时寄存器检查"))
def Testcase_MemPower_007():
    """
    Name:       PPD使能时寄存器检查
    Condition:  1、CKE Power Down选项已开启；
                2、PPD选项已开启。
    Steps:      1、启动进OS，使用lspci -s "BDF"  -xxxx命令查询6A0~6A3四字节，分别检查Bit8、Bit9值是否正确，有结果A。
    Result:     A：Bit8=0，Bit9=1。
    Remark:     1、BDF号和内存所插的位置相关对应关系参考Intel手册，B(2)表示CPU的Stk2，如V5服务器CPU0则B(2)表示0x3A：
                DIMM000----B(2):A.2
                DIMM010----B(2):A.6
                DIMM020----B(2):B.2
                DIMM030----B(2):C.2
                DIMM040----B(2):C.6
                DIMM050----B(2):D.2
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.load_default_in_setup(save=False)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.UP, 15, Msg.CKE)
        assert SetUpLib.set_option_value(Msg.CKE, Msg.ENABLE)
        assert SetUpLib.enter_menu([Msg.CKE_FEATURE], Key.DOWN, 10, Msg.CKE_IDLE_TIMER)
        assert SetUpLib.set_option_value(Msg.PPD, Msg.ENABLE, save=True)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.DOWN, 15, Msg.CKE)
        assert SetUpLib.verify_options([[Msg.CKE, Msg.ENABLE]], Key.DOWN, 7)
        assert SetUpLib.enter_menu([Msg.CKE_FEATURE], Key.DOWN, 12, Msg.CKE_IDLE_TIMER)
        assert SetUpLib.verify_options([[Msg.PPD, Msg.ENABLE]], Key.DOWN, 5)
        assert SetUpLib.boot_os_from_bm()
        read_cke_reg = PlatMisc.cscripts_rw(SutConfig.Sys.CS_CKE)
        assert read_cke_reg.get("ddrt_cke_en") == 1, "ddrt_cke_en"
        assert read_cke_reg.get("ppd_en") == 1, "ppd_en"
        assert read_cke_reg.get("apd_en") == 0, "apd_en"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1112", "[TC1112] Testcase_MemPower_009", "更改定时器选项时寄存器检查"))
def Testcase_MemPower_009():
    """
    Name:       更改定时器选项时寄存器检查
    Condition:  1、CKE Power Down选项已开启。
    Steps:      1、启动进Setup菜单，更改CKE Idle Timer选项的数值，F10保存重启；
                2、启动进OS，使用lspci -s "BDF"  -xxxx命令查询6A0字节，有结果A。
    Result:     A：6A0字节数值和Setup菜单设置的数值一致，寄存器值 = BIOS设置值 * 系数 /10000（OS下的为十六进制数，Setup菜单为十进制，注意转换）。
    Remark:     1、BDF号和内存所插的位置相关对应关系参考Intel手册，B(2)表示CPU的Stk2，如V5服务器CPU0则B(2)表示0x3A：
                DIMM000----B(2):A.2
                DIMM010----B(2):A.6
                DIMM020----B(2):B.2
                DIMM030----B(2):C.2
                DIMM040----B(2):C.6
                DIMM050----B(2):D.2
                2、系数与内存频率一一对应，具体如下：
                内存频率：
                800, 1000, 1066, 1200, 1333, 1400, 1600, 1800, 1866, 2000, 2133, 2200, 2400  2600, 2666, 2800, 2933, 3000, 3200, 3400, 3467, 3600, 3733, 3800, 4000, 4200, 4266, 4400
                系数：
                25000, 20000, 18750, 16667, 15000, 14286, 12500, 11111, 10714, 10000, 9375, 9091, 8333, 7692, 7500, 7143, 6818, 6667, 6250, 5883, 5769, 5556, 5358, 5264, 5000, 4762, 4689, 4546
    """
    try:
        cke_idle_set_value = 60
        cke_idle_timer = _cke_idle_timer_count(cke_idle_set_value)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.load_default_in_setup(save=False)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.UP, 15, Msg.CKE)
        assert SetUpLib.set_option_value(Msg.CKE, Msg.ENABLE)
        assert SetUpLib.enter_menu([Msg.CKE_FEATURE], Key.DOWN, 10, Msg.CKE_IDLE_TIMER)
        assert SetUpLib.get_option_value(Msg.CKE_IDLE_TIMER, Key.DOWN, 5, integer=True) == "20"
        SetUpLib.send_key(Key.ENTER)  # Send Enter
        SetUpLib.send_data_enter(f'{cke_idle_set_value}')  # set 255
        SetUpLib.send_keys(Key.SAVE_RESET, 2)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_POWER_ADV, Key.DOWN, 15, Msg.CKE)
        assert SetUpLib.verify_options([[Msg.CKE, Msg.ENABLE]], Key.DOWN, 7)
        assert SetUpLib.enter_menu([Msg.CKE_FEATURE], Key.DOWN, 12, Msg.CKE_IDLE_TIMER)
        assert SetUpLib.verify_options([['CKE Idle Timer', f'\[{cke_idle_set_value}\]']], Key.DOWN, 5, integer=True)
        assert SetUpLib.boot_os_from_bm()
        read_cke_reg = PlatMisc.cscripts_rw(SutConfig.Sys.CS_CKE)
        assert read_cke_reg.get("ddrt_cke_en") == 1, "ddrt_cke_en"
        assert read_cke_reg.get("ppd_en") == 1, "ppd_en"
        assert read_cke_reg.get("apd_en") == 0, "apd_en"
        assert read_cke_reg.get("cke_idle_timer") == cke_idle_timer, "cke_idle_timer"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1113", "[TC1113] Testcase_MemRefresh_001", "内存刷新模式设置菜单检查"))
def Testcase_MemRefresh_001():
    """
    Name:       内存刷新模式设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，Memory Configuration界面下查看是否存在Refresh Options选项，检查可选值及默认值，有结果A。
    Result:     A：存在Refresh Options选项，Dynamic Mode、Static 2x Mode可选，2P默认Dynamic Mode，4P默认Static 2x Mode。
    Remark:     
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.load_default_in_setup(save=False)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        if SutConfig.Env.MAX_CPU_CNT == 4:
            assert SetUpLib.get_option_value(Msg.MEM_REFRESH, Key.UP) == Msg.VAL_MEM_REF[0]
        else:
            assert SetUpLib.get_option_value(Msg.MEM_REFRESH, Key.UP) == Msg.VAL_MEM_REF[1]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1114", "[TC1114] Testcase_MemRefresh_002", "动态刷新模式寄存器检查"))
def Testcase_MemRefresh_002():
    """
    Name:       动态刷新模式寄存器检查
    Condition:  1、内存刷新模式为动态刷新。
    Steps:      1、启动进OS，使用lspci -s "BDF"  -xxxx命令查询120~122三字节数值是否正确，有结果A。
    Result:     A：120~122三字节分别为temp_lo、temp_mid、temp_high，值为85、95、100，与代码定义一致（数值主要进制换算，不同单板定义可能不同，参照SKX_2_10_2_CFG_h、Memthrot.c）。
    Remark:     1、内存温度在temp_lo以内时按照标准频率进行刷新，超过temp_lo后进入双倍刷新模式；
                2、BDF号和内存所插的位置相关对应关系参考Intel手册，B(2)表示CPU的Stk2，如V5服务器CPU0则B(2)表示0x3A：
                DIMM000----B(2):A.2
                DIMM010----B(2):A.6
                DIMM020----B(2):B.2
                DIMM030----B(2):C.2
                DIMM040----B(2):C.6
                DIMM050----B(2):D.2
    """
    try:
        refresh_mode = Msg.VAL_MEM_REF[1]
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN, 15, Msg.MEM_TURBO)
        assert SetUpLib.set_option_value(Msg.MEM_REFRESH, refresh_mode, Key.UP, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        dimm_temp_reg = PlatMisc.cscripts_rw(SutConfig.Sys.CS_TEMP_TH)
        assert dimm_temp_reg.get("temp_lo") == 0x55, "temp_lo"
        assert dimm_temp_reg.get("temp_mid") == 0x5f, "temp_mid"
        assert dimm_temp_reg.get("temp_hi") == 0x64, "temp_hi"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1115", "[TC1115] Testcase_MemRefresh_004", "静态2X刷新模式寄存器检查"))
def Testcase_MemRefresh_004():
    """
    Name:       静态2X刷新模式寄存器检查
    Condition:  1、内存刷新模式为静态2倍刷新。
    Steps:      1、启动进OS，使用lspci -s "BDF"  -xxxx命令查询120~122三字节数值是否正确，有结果A。
    Result:     A：120~122三字节分别为temp_lo、temp_mid、temp_high，值为0、95、100，与代码定义一致（数值主要进制换算，不同单板定义可能不同，参照SKX_2_10_2_CFG_h、Memthrot.c）。
    Remark:     1、BDF号和内存所插的位置相关对应关系参考Intel手册，B(2)表示CPU的Stk2，如V5服务器CPU0则B(2)表示0x3A：
                DIMM000----B(2):A.2
                DIMM010----B(2):A.6
                DIMM020----B(2):B.2
                DIMM030----B(2):C.2
                DIMM040----B(2):C.6
                DIMM050----B(2):D.2
    """
    try:
        refresh_mode = Msg.VAL_MEM_REF[0]
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN, 15, Msg.MEM_TURBO)
        assert SetUpLib.set_option_value(Msg.MEM_REFRESH, refresh_mode, Key.UP, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        dimm_temp_reg = PlatMisc.cscripts_rw(SutConfig.Sys.CS_TEMP_TH)
        assert dimm_temp_reg.get("temp_lo") == 0, "temp_lo"
        assert dimm_temp_reg.get("temp_mid") == 0x5f, "temp_mid"
        assert dimm_temp_reg.get("temp_hi") == 0x64, "temp_hi"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1116", "[TC1116] Testcase_SetMemFreq_001", "内存频率设置菜单检查"))
def Testcase_SetMemFreq_001():
    """
    Name:       内存频率设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，Memory Configuration界面下查看是否存在内存频率设置选项，检查可选值及默认值，有结果A。
    Result:     A：存在频率设置选项，Auto、3200，3600，4000、4400、4800六档可选，默认Auto。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN, 15, Msg.MEM_TURBO)
        freq_get = SetUpLib.get_all_values(Msg.MEM_FREQ, Key.DOWN, 15)
        assert MiscLib.same_values(Msg.VAL_MEM_FREQ, freq_get)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1117", "[TC1117] Testcase_SetMemFreq_002", "内存频率自适应测试"))
def Testcase_SetMemFreq_002():
    """
    Name:       内存频率自适应测试
    Condition:  1、接兼容性规格内内存条，假定频率为a；
                2、内存频率选项设置Auto；
                3、关闭Memory Turbo。
    Steps:      1、单板上电，检查MRC初始化阶段和Setup Main菜单显示内存运行频率，有结果A；
                2、检查启动过程中串口是否异常打印，能否正常启动进系统，有结果B；
    Result:     A：内存运行频率为a；
                B：系统运行在a频率，OS引导正常。
    Remark:     1、内存频率设置与Memory Turbo菜单联动时，需要先关闭Memory Turbo；
                2、实际运行频率=Min[CPU支持最大频率，内存规格频率，Setup设置频率]
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.set_option_value(option=Msg.MEM_TURBO, value=Msg.DISABLE, save=True)
        assert _check_mem_freq_in_post_log(SutConfig.Sys.MEM_FREQ)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1119", "[TC1119] Testcase_SetMemFreq_004", "设置内存规格内频率测试"))
def Testcase_SetMemFreq_004():
    """
    Name:       设置内存规格内频率测试
    Condition:  1、接兼容性规格内内存条，假定频率为a；
                2、关闭Memory Turbo。
    Steps:      1、启动进Setup菜单，Memory Configuration界面下设置内存频率为a，F10保存重启，检查启动内存运行频率是否正确，OS引导是否正常，有结果A；
                2、启动进Setup菜单，Memory Configuration界面下设置内存频率遍历a以下的所有档位，假定为b，F10保存重启，检查启动内存运行频率是否正确，OS引导是否正常，有结果B；
    Result:     A：内存运行频率为a，OS启动正常；
                B：内存运行频率为b，OS启动正常；
    Remark:     1、内存频率设置与Memory Turbo菜单联动时，需要先关闭Memory Turbo；
                2、实际运行频率=Min[CPU支持最大频率，内存规格频率，Setup设置频率]
    """
    try:
        dimm_freq = SutConfig.Sys.DIMM_FREQ
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.set_option_value(Msg.MEM_TURBO, Msg.DISABLE)
        default_freq = SetUpLib.get_option_value(Msg.MEM_FREQ, Key.DOWN)
        for set_freq in Msg.VAL_MEM_FREQ:
            if set_freq == default_freq:
                logging.info(f"Skip default value: {default_freq}")
                continue
            if int(set_freq) > dimm_freq:
                logging.info(f"Current install DIMM={dimm_freq} not support setting {set_freq}")
                continue
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
            assert SetUpLib.set_option_value(Msg.MEM_TURBO, Msg.DISABLE)
            assert SetUpLib.set_option_value(Msg.MEM_FREQ, set_freq, save=True)
            assert _check_mem_freq_in_post_log(min(int(set_freq), Sys.MEM_FREQ))
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1120", "[TC1120] Testcase_Mtrr_001", "MTRR寄存器预留测试"))
def Testcase_Mtrr_001():
    """
    Name:       MTRR寄存器预留测试
    Condition:  1、已安装Windows系统；
                2、满配内存（单根内存容量尽量大）；
                3、系统下已安装RW工具。
    Steps:      1、启动进OS，使用RW工具读取MSR寄存器，查看是否有预留一个MTRR寄存器，有结果A。
    Result:     A：至少有预留一组MTRR寄存器。
    Remark:     1、PHYSBASE和PHYSMASK合为一组MTRR寄存器，后面数字全显示为0算有预留。
    """
    try:
        assert SetUpLib.boot_to_default_os()
        msr_base = list(range(200, 213 + 1, 2))
        msr_mask = list(range(201, 213 + 1, 2))
        msr_pairs = list(zip(msr_base, msr_mask))
        mtrr_reserve = 0
        for mtrr_msr in msr_pairs:
            base, mask = mtrr_msr
            if PlatMisc.cscripts_rw(f"msr(0x{base})") == 0 and PlatMisc.cscripts_rw(f"msr(0x{mask})") == 0:
                mtrr_reserve += 1
                logging.info(f"MTRR_PHYBASE=MSR(0x{base}) and MTRR_PHYBASE=MSR(0x{mask}) are reserved")
                break
        assert mtrr_reserve > 0, "No Reversed MTRR register found"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1121", "[TC1121] Testcase_Mtrr_002", "MTRR Fixed ranges测试"))
def Testcase_Mtrr_002():
    """
    Name:       MTRR Fixed ranges测试
    Condition:  1、已安装Linux系统。
    Steps:      1、单板上电启动，检查BIOS启动过程打印是否存在告警，有结果A；
                2、OS下输入dmesg命令，查询MTRR Fixed ranges，有结果B。
    Result:     A：串口打印无"0xa0300"的MCE告警；
                B：A0000~BFFFF设置为UC。
    Remark:     1、MTRR Fixed ranges段参考各厂家定义。
    """
    try:
        fail_msg = "0xa0300"
        search_mtrr_fix = "MTRR fixed ranges"
        mtrr_uc_start = "A0000"
        mtrr_uc_end = "BFFFF"
        assert BmcLib.force_reset()
        boot_log = SerialLib.cut_log(Sut.BIOS_COM, Msg.POST_START, Msg.BIOS_BOOT_COMPLETE,
                                     SutConfig.Env.BOOT_DELAY, SutConfig.Env.BOOT_DELAY)
        assert boot_log, "Invalid boot log"
        assert fail_msg not in boot_log, f"'{fail_msg}' found in boot log"
        dmesg_mtrr_fix = SshLib.execute_command(Sut.OS_SSH, f"dmesg |grep -i -A 15 '{search_mtrr_fix}'")
        mtrr_range_found = re.findall("(\w+)-(\w+)\s+uncachable", dmesg_mtrr_fix)
        assert mtrr_range_found, "MTRR Fixed ranges of uncachable not found"
        mtrr_found_start, mtrr_found_end = mtrr_range_found[0]
        assert int(mtrr_found_start, 16) <= int(mtrr_uc_start, 16), "MTRR start out of range"
        assert int(mtrr_found_end, 16) >= int(mtrr_uc_end, 16), "MTRR end out of range"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1122", "[TC1122] Testcase_SpdCrcCheck_001", "SPD设置菜单检查"))
def Testcase_SpdCrcCheck_001():
    """
    Name:       SPD设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，查看内存SPD菜单选项默认值，有结果A。
    Result:     A：提供菜单用于SPD检测，选项为：Enable，Disable，默认Enable。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.get_option_value(Msg.SPD_CRC, Key.DOWN, 10) == Msg.ENABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.SPD_CRC), [Msg.Auto, Msg.ENABLE, Msg.DISABLE])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1123", "[TC1123] Testcase_SpdCrcCheck_009", "SPD CRC开启时功能测试_无故障内存条"))
def Testcase_SpdCrcCheck_009():
    """
    Name:       SPD CRC开启时功能测试_无故障内存条
    Condition:  1、单板无SPD故障内存条；
                2、SPD CRC选项开启。
    Steps:      1、上电启动，检查内存MRC初始化，串口是否报错，能否进入系统，有结果A；
                2、BMC Web下检查是否有SPD告警记录，有结果B。
    Result:     A：无内存SPD报错，正常进入系统；
                B：BMC下无SPD内存告警。
    Remark:     1、仅V7支持。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN, 10)
        assert SetUpLib.set_option_value(Msg.SPD_CRC, Msg.ENABLE, save=True)
        assert PlatMisc.no_error_at_post()
        bmc_warning = BmcLib.bmc_warning_check(SutConfig.Env.BMC_WARN_IG)
        assert bmc_warning.status
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1124", "[TC1124] Testcase_MemMargin_001", "内存margin测试菜单选项测试"))
def Testcase_MemMargin_001():
    """
    Name:       内存margin测试菜单选项测试
    Condition:  1、开启串口全打印
    Steps:      1、启动进Setup菜单，查看Memory Configuration->RMT Configuration Menu下是否有Rank Margin Tool菜单选项，可选择及默认值，有结果A；
                2、设置Rank Margin Tool为Enabled，F10保存重启检查串口日志是否有Margin测试，有结果B。
    Result:     A：提供Rank Margin Tool选项，Enabled、Disabled可选，默认Disabled；
                B：串口打印margin测试数据。
    Remark:     1、串口搜索关键字"Rank Margin Tool -- Started"。

                RMT串口打印菜单Memory Print Level被隐藏，测RMT只能通过uniCfg修改
    """
    try:
        # assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        # assert SetUpLib.enter_menu(Msg.MISC_CONFIG, Key.UP)
        # assert SetUpLib.set_option_value(Msg.MEM_PRINT_LEVEL, "Minimum", Key.UP, save=False)
        # assert SetUpLib.back_to_setup_toppage()
        # assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG + [Msg.BSSA_CFG], Key.UP)
        # assert MiscLib.same_values(SetUpLib.get_all_values(Msg.RMT), [Msg.ENABLE, Msg.DISABLE])
        # assert SetUpLib.set_option_value(Msg.RMT, Msg.ENABLE, save=True)
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.RMT_EN)
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Msg.RMT_START, timeout=SutConfig.Env.BOOT_RMT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1126", "[TC1126] Testcase_MemMargin_003", "使能内存margin选项测试_长时间"))
def Testcase_MemMargin_003():
    """
    Name:       使能内存margin选项测试_长时间
    Condition:  1、开启串口全打印
    Steps:      1、打开Margin测试相关选项：
                ./uniCfg -w EnableBiosSsaRMT:1；
                3、复位单板执行Margin测试；
                5、多次重启，查看margin测试结果，有结果A。
    Result:     A：串口日志正常上报Margin测试数据。
    Remark:     1、RMT菜单不联动打印级别（总开关和MRC都不做），如果要看详细打印，需要手工设置（工具或菜单）打印级别
    """
    try:
        for i in range(2):
            assert SetUpLib.boot_to_default_os()
            assert Sut.UNITOOL.write(**BiosCfg.RMT_EN)
            assert BmcLib.force_reset()
            assert SetUpLib.wait_boot_msgs(Msg.RMT_START, timeout=SutConfig.Env.BOOT_RMT)
            assert BmcLib.clear_cmos()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1127", "[TC1127] Testcase_MemoryTurbo_001", "内存Turbo设置菜单检查"))
@mark_skip_if(PlatMisc.dimm_per_channel, reason="Current DIMM config not support memory turbo: 1 DPC", equal=False, value=2)
def Testcase_MemoryTurbo_001():
    """
    Name:       内存Turbo设置菜单检查
    Condition:  1、当前CPU支持Memory Turbo功能（可查看Intel官网）
                2、同一通道下接2根2933内存条
    Steps:      1、单板上电进入Setup菜单，查看Memory Configuration->Memory Turbo选项默认值，有结果A；
                2、Enabled Memory Turbo选项，查看Memory Frequency，有结果B;
                3、Disabled Memory Turbo选项，查看Memory Frequency，有结果C。
    Result:     A：存在此菜单，且选项为：Enable，Disabled，默认Disabled;
                B: Memory Frequency置灰，运行频率为turbo频率；
                C: Memory Frequency可设置，运行频率为设置频率。
    Remark:     1、开启状态下，V7 4800内存条，支持2DPC运行4800MHZ，关闭状态运行频率为4400MHZ。
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.get_option_value(Msg.MEM_TURBO, Key.DOWN) == Msg.DISABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.MEM_TURBO), [Msg.ENABLE, Msg.DISABLE])
        assert SetUpLib.set_option_value(Msg.MEM_TURBO, Msg.ENABLE, save=False)
        assert not SetUpLib.locate_option(Msg.MEM_FREQ, Key.DOWN, try_counts=35)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _check_mem_freq_in_post_log(min(SutConfig.SutCfgMde.CPU.Max_MemFreq_1DPC, Sys.DIMM_FREQ))

        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.set_option_value(Msg.MEM_TURBO, Msg.DISABLE, save=False)
        assert SetUpLib.locate_option(Msg.MEM_FREQ, Key.DOWN, try_counts=35)
        SetUpLib.send_keys(Key.SAVE_RESET)
        assert _check_mem_freq_in_post_log(SutConfig.Sys.MEM_FREQ)

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1128", "[TC1128] Testcase_MemoryTurbo_002", "内存Turbo功能2DPC测试"))
@mark_skip_if(PlatMisc.dimm_per_channel, reason="Current DIMM config not support memory turbo: 1 DPC", equal=False, value=2)
def Testcase_MemoryTurbo_002():
    """
    Name:       内存Turbo功能2DPC测试
    Condition:  1、当前CPU支持Memory Turbo功能（可查看Intel官网）
                2、同一Channel下接2根2933内存条（可不满配所有Channel）
    Steps:      1、单板上电进入Setup菜单，检查运行频率是否正确，有结果A；
                2、设置Memory Configuration->Memory Turbo选项为Enable，保存重启检查内存频率，有结果B；
                3、设置Memory Configuration->Memory Turbo选项为Disable，保存重启检查内存频率，有结果A；
    Result:     A：默认Disablsd时内存频率为2666MHZ；
                B：内存频率为2933MHZ
    Remark:     1、V5/V6开启状态下，更改POR表，支持2DPC运行2933MHz;
                2、开启状态下，V7 4800内存条，支持2DPC运行4800MHZ，关闭状态运行频率为4400MHZ。
    """
    try:
        assert BmcLib.force_reset()
        assert _check_mem_freq_in_post_log(SutConfig.Sys.MEM_FREQ)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.get_option_value(Msg.MEM_TURBO, Key.DOWN) == Msg.DISABLE

        assert SetUpLib.set_option_value(Msg.MEM_TURBO, Msg.ENABLE, save=True)
        assert _check_mem_freq_in_post_log(min(SutConfig.SutCfgMde.CPU.Max_MemFreq_1DPC, Sys.DIMM_FREQ))
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1129", "[TC1129] Testcase_MemoryTurbo_006", "内存Turbo功能Legacy模式测试"))
@mark_skip_if(PlatMisc.dimm_per_channel, reason="Current DIMM config not support memory turbo: 1 DPC", equal=False, value=2)
@mark_legacy_test
def Testcase_MemoryTurbo_006():
    """
    Name:       内存Turbo功能Legacy模式测试
    Condition:  1、当前CPU支持Memory Turbo功能（可查看Intel官网）
                2、Setup菜单里已打开Memory Turbo开关。
                3、设置启动模式为Legacy。
                4、同一Channel下接2根2933内存条（可不满配所有Channel）
    Steps:      1、单板上电，检查MRC阶段内存初始化信息，是否有报错，有结果A；
                2、按键进入Setup菜单Main界面查看内存运行频率，有结果B；
                3、进入Setup菜单Memory界面检查内存容量、规格频率、内存槽位、型号等信息，有结果C；
                4、启动到OS，输入cat /proc/meminfo和dmidecode -t 17命令查询内存信息，有结果D。
    Result:     A：MRC阶段无报错；
                B：main界面显示内存运行频率为2933MHZ；
                C：菜单显示内存相关信息正确无多余内存槽位；
                D：OS下内存容量及信息正确。
    Remark:
    """
    try:
        assert BmcLib.force_reset()
        assert _check_mem_freq_in_post_log(SutConfig.Sys.MEM_FREQ)
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN)
        assert SetUpLib.get_option_value(Msg.MEM_TURBO, Key.DOWN) == Msg.DISABLE

        assert SetUpLib.set_option_value(Msg.MEM_TURBO, Msg.ENABLE, save=True)
        assert _check_mem_freq_in_post_log(min(SutConfig.SutCfgMde.CPU.Max_MemFreq_1DPC, Sys.DIMM_FREQ))
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

