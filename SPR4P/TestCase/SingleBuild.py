from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# SingleBuild Test Case
# TC 2800-2803
####################################

# defined memory redfish key_name,
RC = "RankCount"
CM = "CapacityMiB"
ASM = "AllowedSpeedsMHz"
DWB = "DataWidthBits"


@core.test_case(("2800", "[TC2800] Testcase_ReportMeminfoToBmc_001", "内存信息上报检查"))
def Testcase_ReportMeminfoToBmc_001():
    """
    Name:       内存信息上报检查
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish内存接口查询内存条上报信息（Rank数量、容量、规格频率、位宽）是否正确，有结果A；
                2、检查已接入的所有内存条，重复步骤1；
    Result:     A：内存信息与实际一致。
    Remark:     1、使用Get方法，内存对应接口：https://155.1.7.103/redfish/v1/Systems/1/Memory
                2、内存检查字段如下：
                RankCount---->Rank数量
                CapacityMiB---->内存容量
                AllowedSpeedsMHz---->规格频率
                ChipBitWidth---->内存位宽
    """
    res_list = []
    try:
        Sut.BMC_RFISH.registry_dump(True, path=SutConfig.Env.LOG_DIR, name="registry_tc2800.json")  # 获取registry数据
        for i in SutConfig.Sys.DIMM_POP:
            res_info = Sut.BMC_RFISH.get_info("{0}/Memory/mainboardDIMM{1}".format(Sut.BMC_RFISH.SYSTEM, i))
            for key, value in res_info.items():
                if key == RC:
                    if value != SutConfig.Sys.DIMM_RANK_CNT:
                        res_list.append(f"{i, value}")

                if key == CM:
                    if value != SutConfig.Sys.DIMM_SIZE * 1024:
                        res_list.append(f"{i, value}")

                if key == ASM:
                    if value != [SutConfig.Sys.DIMM_FREQ]:
                        res_list.append(f"{i, value}")

                if key == DWB:
                    if value != SutConfig.Sys.DIMM_BW:
                        res_list.append(f"{i, value}")
        assert len(res_list) == 0, f"Test failed - {res_list}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2801", "[TC2801] Testcase_ReportMeminfoToBmc_002", "内存信息上报检查_修改内存频率"))
def Testcase_ReportMeminfoToBmc_002():
    """
    Name:       内存信息上报检查_修改内存频率
    Condition:  1、Postman工具已安装。
    Steps:      1、通过Redfish内存接口查询内存条上报信息（Rank数量、容量、规格频率、位宽）是否正确，有结果A；
                2、启动进Setup菜单，修改内存频率，重启再次查询内存条上报频率信息是否正确，有结果B。
    Result:     A：内存信息与实际一致；
                B：规格频率保持不变。
    Remark:     1、使用Get方法，内存对应接口：https://155.1.7.103/redfish/v1/Systems/1/Memory
                2、内存检查字段如下：
                RankCount---->Rank数量
                CapacityMiB---->内存容量
                AllowedSpeedsMHz---->规格频率
                ChipBitWidth---->内存位宽
    """
    res_list = []
    try:
        Sut.BMC_RFISH.registry_dump(True, path=SutConfig.Env.LOG_DIR, name="registry_tc2801.json")  # 获取registry数据
        for i in SutConfig.Sys.DIMM_POP:
            res_info = Sut.BMC_RFISH.get_info("{0}/Memory/mainboardDIMM{1}".format(Sut.BMC_RFISH.SYSTEM, i))
            for key, value in res_info.items():
                if key == RC:
                    if value != SutConfig.Sys.DIMM_RANK_CNT:
                        res_list.append(f"{i, value}")

                if key == CM:
                    if value != SutConfig.Sys.DIMM_SIZE * 1024:
                        res_list.append(f"{i, value}")

                if key == ASM:
                    if value != [SutConfig.Sys.DIMM_FREQ]:
                        res_list.append(f"{i, value}")

                if key == DWB:
                    if value != SutConfig.Sys.DIMM_BW:
                        res_list.append(f"{i, value}")

        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MEM_CONFIG, Key.DOWN, 20, Msg.MEMORY_CONFIG)
        assert SetUpLib.set_option_value(Msg.MEM_FREQ, "3200", save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert SetUpLib.boot_to_default_os()
        for i in SutConfig.Sys.DIMM_POP:
            res_info = Sut.BMC_RFISH.get_info("{0}/Memory/mainboardDIMM{1}".format(Sut.BMC_RFISH.SYSTEM, i))
            for key, value in res_info.items():
                if key == ASM:
                    if value != [SutConfig.Sys.DIMM_FREQ]:
                        res_list.append(f"Freq modified - {i, value}")
        assert len(res_list) == 0, f"Test failed - {res_list}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2802", "[TC2802] Testcase_ReportMeminfoToBmc_004", "ADDDC开启时上报检查"))
def Testcase_ReportMeminfoToBmc_004():
    """
    Name:       ADDDC开启时上报检查
    Condition:  1、Postman工具已安装。
    Steps:      1、启动进Setup菜单，内存RAS界面设置ADDDC Sparing选项为Enabled，F10保存重启；
                2、通过Redfish Setup菜单接口查询ADDDC开关状态是否正确，有结果A；
    Result:     A：ADDDCEn状态为Enabled。
    Remark:     1、使用Get方法，Setup菜单对应接口：https://155.1.7.103/redfish/v1/Systems/1/Bios

    """
    try:
        # enabled by default on 4P,
        Sut.BMC_RFISH.registry_dump(True, path=SutConfig.Env.LOG_DIR, name="registry_tc2802.json")
        assert Sut.BMC_RFISH.check_bios_option(**{Attr.ADDDC_EN: Msg.ENABLE})
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2803", "[TC2803] Testcase_ReportMeminfoToBmc_005", "ADDDC关闭时上报检查"))
def Testcase_ReportMeminfoToBmc_005():
    """
    Name:       ADDDC关闭时上报检查
    Condition:  1、Postman工具已安装。
    Steps:      1、启动进Setup菜单，内存RAS界面设置ADDDC Sparing选项为Disabled，F10保存重启；
                2、通过Redfish Setup菜单接口查询ADDDC开关状态是否正确，有结果A；
    Result:     A：ADDDCEn状态为Disabled。
    Remark:     1、使用Get方法，Setup菜单对应接口：https://155.1.7.103/redfish/v1/Systems/1/Bios

    """
    ras_path = Msg.PATH_MEM_CONFIG + [Msg.MEM_RAS_CFG]
    try:
        Sut.BMC_RFISH.registry_dump(True, path=SutConfig.Env.LOG_DIR, name="registry_tc2803.json")
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(ras_path, Key.DOWN, 30, Msg.MEM_RAS_CFG)
        assert SetUpLib.set_option_value(Msg.ADDDC_SP, Msg.DISABLE, save=True)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert SetUpLib.boot_to_default_os()
        assert Sut.BMC_RFISH.check_bios_option(**{Attr.ADDDC_EN: Msg.DISABLE})
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

