import random

from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# BootDevice Test Case
# TC 1500-1556
####################################

boot_override_op = ['Disabled', 'PCIe SSD First', 'iSCSI First', 'FC First', 'FCOE First', 'PCH Direct First',
                    'RAID First', 'USB First', 'Local Disk Boot Only']

# @core.test_case(("1500", "[TC1500] Testcase_BootDeviceTypeUefi_001", "【UEFI】四大类启动类型分类"))
# def Testcase_BootDeviceTypeUefi_001():
#     """
#     Name:       【UEFI】四大类启动类型分类
#     Condition:  1、UEFI模式；
#                 2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
#     Steps:      1、系统启动，进入Boot Manager界面，检查启动项分类是否正确，有结果A；
#                 2、进入Setup菜单Boot->UEFI菜单下，检查启动项分类是否正确，有结果A。
#     Result:     A：启动设备分类正确HDD\DVD-ROM\PXE\Other，U盘和软驱为Others，M.2为HDD。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1501", "[TC1501] Testcase_BootDeviceTypeUefi_002", "【UEFI】Boot界面启动项顺序调整"))
# def Testcase_BootDeviceTypeUefi_002():
#     """
#     Name:       【UEFI】Boot界面启动项顺序调整
#     Condition:  1、UEFI模式；
#                 2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
#     Steps:      1、系统启动，进入Setup菜单Boot界面，通过F5/F6调整启动项顺序（包含大类和小类），有结果A；
#                 2、F10保存重启，进入Boot Manager下查看启动项顺序显示，有结果B；
#                 3、重启系统，检查系统实际启动顺序，有结果C。
#     Result:     A：正常调整大类、小类启动顺序；
#                 B：Boot Manager启动项顺序与设置保持一致；
#                 C：按照设置的启动顺序进行启动。
#     Remark:     验证实际启动顺序时，可以先断开优先级高的启动项介质。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1502", "[TC1502] Testcase_BootDeviceTypeUefi_003", "【UEFI】Boot Manager界面启动项顺序调整"))
# def Testcase_BootDeviceTypeUefi_003():
#     """
#     Name:       【UEFI】Boot Manager界面启动项顺序调整
#     Condition:  1、UEFI模式；
#                 2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
#     Steps:      1、系统启动，进入Boot Manager界面，通过F5/F6调整启动项顺序，有结果A；
#                 2、重启再次进入Boot Manager下查看启动项顺序显示，有结果B；
#                 3、重启系统，检查系统实际启动顺序，有结果C。
#     Result:     A：正常调整小类启动顺序，大类之间启动顺序无法调整；
#                 B：Boot Manager启动项顺序与上次设置保持一致；
#                 C：按照设置的启动顺序进行启动。
#     Remark:     验证实际启动顺序时，可以先断开优先级高的启动项介质。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1503", "[TC1503] Testcase_BootDeviceTypeUefi_004", "【UEFI】SP启动项不显示在启动菜单"))
def Testcase_BootDeviceTypeUefi_004():
    """
    Name:       【UEFI】SP启动项不显示在启动菜单
    Condition:  1、UEFI模式；
                2、SP环境已部署
    Steps:      1、系统启动，进入Boot Manager界面，检查是否存在SP启动项，有结果A；
                2、重启再次进入Setup Boot界面下查看是否存在SP启动项，有结果A；
                3、重启系统，选择F6从SP启动，检查能否启动成功，有结果B。
    Result:     A：无SP启动项；
                B：成功从SP启动。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_bootmanager()
        boot_options = SetUpLib.get_all_options()
        for op in boot_options:
            assert "sp" not in op.lower(), f"SP boot found: {op}"
        assert SolLib.boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_UEFI)
        assert PlatMisc.is_sp_boot_success()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("1504", "[TC1504] Testcase_BootDeviceTypeLegacy_001", "【Legacy】四大类启动类型分类"))
# def Testcase_BootDeviceTypeLegacy_001():
#     """
#     Name:       【Legacy】四大类启动类型分类
#     Condition:  1、Legacy模式；
#                 2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
#     Steps:      1、系统启动，进入Boot Manager界面，检查启动项分类是否正确，有结果A；
#                 2、进入Setup菜单Boot->UEFI菜单下，检查启动项分类是否正确，有结果A。
#     Result:     A：启动设备分类正确HDD\DVD-ROM\PXE\Other，U盘和软驱为Others，M.2为HDD。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1505", "[TC1505] Testcase_BootDeviceTypeLegacy_002", "【Legacy】Boot界面启动项顺序调整"))
# def Testcase_BootDeviceTypeLegacy_002():
#     """
#     Name:       【Legacy】Boot界面启动项顺序调整
#     Condition:  1、Legacy模式；
#                 2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
#     Steps:      1、系统启动，进入Setup菜单Boot界面，通过F5/F6调整启动项顺序（包含大类和小类），有结果A；
#                 2、F10保存重启，进入Boot Manager下查看启动项顺序显示，有结果B；
#                 3、重启系统，检查系统实际启动顺序，有结果C。
#     Result:     A：正常调整大类、小类启动顺序；
#                 B：Boot Manager启动项顺序与设置保持一致；
#                 C：按照设置的启动顺序进行启动。
#     Remark:     验证实际启动顺序时，可以先断开优先级高的启动项介质。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1506", "[TC1506] Testcase_BootDeviceTypeLegacy_003", "【Legacy】Boot Manager界面启动项顺序调整"))
# def Testcase_BootDeviceTypeLegacy_003():
#     """
#     Name:       【Legacy】Boot Manager界面启动项顺序调整
#     Condition:  1、Legacy模式；
#                 2、安装所有可启动设备：硬盘、PXE、光驱、U盘、M.2、软驱等。
#     Steps:      1、系统启动，进入Boot Manager界面，通过F5/F6调整启动项顺序，有结果A；
#                 2、重启再次进入Boot Manager下查看启动项顺序显示，有结果B；
#                 3、重启系统，检查系统实际启动顺序，有结果C。
#     Result:     A：正常调整小类启动顺序，大类之间启动顺序无法调整；
#                 B：Boot Manager启动项顺序与上次设置保持一致；
#                 C：按照设置的启动顺序进行启动。
#     Remark:     验证实际启动顺序时，可以先断开优先级高的启动项介质。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1507", "[TC1507] Testcase_BootDeviceTypeLegacy_004", "【Legacy】SP启动项不显示在启动菜单"))
@mark_legacy_test
def Testcase_BootDeviceTypeLegacy_004():
    """
    Name:       【Legacy】SP启动项不显示在启动菜单
    Condition:  1、Legacy模式；
                2、SP环境已部署
    Steps:      1、系统启动，进入Boot Manager界面，检查是否存在SP启动项，有结果A；
                2、重启再次进入Setup Boot界面下查看是否存在SP启动项，有结果A；
                3、重启系统，选择F6从SP启动，检查能否启动成功，有结果B。
    Result:     A：无SP启动项；
                B：成功从SP启动。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_bootmanager()
        boot_options = SetUpLib.get_all_options()
        for op in boot_options:
            assert "sp" not in op.lower(), f"SP boot found: {op}"
        assert SolLib.boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_LEGACY)
        assert PlatMisc.is_sp_boot_success()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1508", "[TC1508] Testcase_BootOverrideUefi_001", "【UEFI】Boot Override设置菜单检查"))
def Testcase_BootOverrideUefi_001():
    """
    Name:       【UEFI】Boot Override设置菜单检查
    Condition:  1、UEFI模式；
    Steps:      1、单板启动进Setup菜单Boot界面，检查是否提供Boot Override选项，默认值选项如何，有结果A；
                2、检查该选项提供的可设置值，有结果B。
    Result:     A：提供Special Boot选项且默认值为Disabled；
                B：可设置值见备注1。
    Remark:     1、选项可选值：
                0：Disabled
                1：PCIE SSD First（仅UEFI模式开放）
                2：iSCSI First
                3：FC First
                4：FCOE First
                5：PCH Direct First
                6：RAID First（包含NVME的VMD）
                7：USB First
                8：Local Disk Boot Only
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.locate_option(Msg.BOOT_OVERRIDE)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BOOT_OVERRIDE), boot_override_op)
        assert SetUpLib.get_option_value(Msg.BOOT_OVERRIDE) == Msg.DISABLE
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1509", "[TC1509] Testcase_BootOverrideUefi_002", "【UEFI】Boot Override功能验证"))
# def Testcase_BootOverrideUefi_002():
#     """
#     Name:       【UEFI】Boot Override功能验证
#     Condition:  1、UEFI模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First（SATA和sSATA）/Raid First（包括NVME的VMD）/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、进Setup菜单Boot界面，设置Boot Override选项为PCIE SSD First，保存退出；
#                 2、启动进BootManager界面，查看启动设备顺序，有结果A；
#                 3、按ESC退出继续启动，检查第一启动设备，有结果B；
#                 4、重启进Setup菜单，遍历设置PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First/Local Disk Boot Only/Disable，重复步骤1~3，有结果C。
#     Result:     A：PCIE SSD设备排在第一位，剩余启动设备的顺序按照默认顺序保持不变；
#                 B：从PCIE SSD设备启动，且启动成功。
#                 C：Boot override设置的启动设备排在第一位，剩余启动设备的顺序按照默认顺序保持不变，按ESC继续启动时从Boot override设置的启动设备第一启动；Boot override设置为Disable时，保持默认四大类启动顺序不变。
#     Remark:     1、调整动作基于4大启动项分类的基础上进行；除了调整到最高优先级的启动项，其他启动项还是按照4大类进行排序；
#                 2、如果某一类启动项有多个，不支持多个启动项的顺序固定和调整。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1510", "[TC1510] Testcase_BootOverrideUefi_003", "【UEFI】热键功能与Boot Override优先级测试"))
# def Testcase_BootOverrideUefi_003():
#     """
#     Name:       【UEFI】热键功能与Boot Override优先级测试
#     Condition:  1、UEFI模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、在Setup菜单Boot界面设置Boot Override选项为USB First，保存退出；
#                 2、系统启动过程中，按F12选择从PXE启动，有结果A；
#                 3、重启系统，按F6选择从SP启动，有结果B。
#     Result:     A：从PXE启动；
#                 B：从SP启动。
#     Remark:     没有用户按键时，BootOverride启动项的优先级最高；但是用户如果通过热键进入Setup，则用户选择的启动设备优先级高于override启动设备。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1511", "[TC1511] Testcase_BootOverrideUefi_005", "【UEFI】Boot Override设置Local Disk Boot Only测试"))
# def Testcase_BootOverrideUefi_005():
#     """
#     Name:       【UEFI】Boot Override设置Local Disk Boot Only测试
#     Condition:  1、UEFI模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、进Setup菜单Boot界面，设置Boot Override选项为Local Disk Boot Only，保存退出；
#                 2、启动进BootManager界面，查看启动设备顺序，有结果A；
#                 3、按ESC退出继续启动，检查第一启动设备，有结果B。
#     Result:     A：仅保留PCIE SSD、PCH直出硬盘、Raid卡（包括NVME的VMD）启动项；
#                 B：从Local Disk启动项启动。
#     Remark:     当选择Local Disk Boot Only时，系统只有PCIE SSD、PCH直出硬盘、Raid卡（包括NVME的VMD）启动项可用于启动。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()



# Common module, For TC1512, TC1518
def _check_boot_override():
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.get_option_value(Msg.BOOT_OVERRIDE) == boot_override_op[8]
        return True
    except Exception as e:
        logging.error(e)
        return False

@core.test_case(("1512", "[TC1512] Testcase_BootOverrideUefi_006", "【UEFI】带外设置Boot Override选项"))
def Testcase_BootOverrideUefi_006():
    """
    Name:       【UEFI】带外设置Boot Override选项
    Condition:  1、UEFI模式；
    Steps:      1、进OS下通过uniCfg -r BootOverride读取变量，检查默认值，有结果A；
                2、OS下通过uniCfg -w BootOverride:X设置变量后重启，进入Setup菜单Boot界面，检查是否生效，有结果B；
                3、通过Redfish接口重复步骤1~2。
    Result:     A：默认值为0，Disabled
                B：设置生效，结果为X
    Remark:     1、选项可选值：
                0：Disabled
                1：PCIE SSD First（仅UEFI模式开放）
                2：iSCSI First
                3：FC First
                4：FCOE First
                5：PCH Direct First
                6：RAID First（包含NVME的VMD）
                7：USB First
                8：Local Disk Boot Only
    """
    try:
        boot_over = 'BootOverride'
        assert SetUpLib.boot_to_default_os(delay=10)
        assert Sut.UNITOOL.check(**BiosCfg.Boot_Override_def)
        assert Sut.UNITOOL.write(**BiosCfg.Boot_Override_aft)
        assert _check_boot_override()
        SetUpLib.send_keys(Key.RESET_DEFAULT)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert Sut.BMC_RFISH.read_bios_option(boot_over).get(boot_over) == Msg.DISABLE
        assert Sut.BMC_RFISH.set_bios_option(**{boot_over: boot_override_op[-1]}).status == 200, 'Error: PATCH Fail'
        assert _check_boot_override()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1513", "[TC1513] Testcase_BootOverrideUefi_007", "【UEFI】BMC设置与Boot Override优先级测试"))
# def Testcase_BootOverrideUefi_007():
#     """
#     Name:       【UEFI】BMC设置与Boot Override优先级测试
#     Condition:  1、UEFI模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、单板启动进Setup菜单，此时WEB界面设置从PXE第一启动永久有效； 
#                 2、在Setup菜单Boot界面设置Boot Override选项为USB First，保存退出；
#                 3、启动进BootManager界面，查看启动设备顺序，有结果A；
#                 4、按ESC退出继续启动，检查第一启动设备，有结果B。
#     Result:     A：USB设备均会排在第一位（光驱、软驱），其他启动设备顺序保持设置不变，PXE->硬盘->DVD->Other；
#                 B：从USB设备启动。
#     Remark:     没有用户按键时，BootOverride启动项的优先级最高；但是用户如果通过热键进入Setup，则用户选择的启动设备优先级高于override启动设备。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1514", "[TC1514] Testcase_BootOverrideLegacy_001", "【Legacy】Boot Override设置菜单检查"))
@mark_legacy_test
def Testcase_BootOverrideLegacy_001():
    """
    Name:       【Legacy】Boot Override设置菜单检查
    Condition:  1、Legacy模式；
    Steps:      1、单板启动进Setup菜单Boot界面，检查是否提供Boot Override选项，默认值选项如何，有结果A；
                2、检查该选项提供的可设置值，有结果B。
    Result:     A：提供Special Boot选项且默认值为Disabled；
                B：可设置值见备注1。
    Remark:     1、选项可选值：
                0：Disabled
                1：PCIE SSD First（仅UEFI模式开放）
                2：iSCSI First
                3：FC First
                4：FCOE First
                5：PCH Direct First
                6：RAID First（包含NVME的VMD）
                7：USB First
                8：Local Disk Boot Only
    """
    op_val = ['Disabled', 'PCIe SSD First', 'iSCSI First', 'FC First', 'FCOE First', 'PCH Direct First',
              'RAID First', 'USB First', 'Local Disk Boot Only']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.get_option_value(Msg.BOOT_OVERRIDE) == Msg.DISABLE
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BOOT_OVERRIDE), op_val)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1515", "[TC1515] Testcase_BootOverrideLegacy_002", "【Legacy】Boot Override功能验证"))
# def Testcase_BootOverrideLegacy_002():
#     """
#     Name:       【Legacy】Boot Override功能验证
#     Condition:  1、Legacy模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First（SATA和sSATA）/Raid First（包括NVME的VMD）/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、进Setup菜单Boot界面，设置Boot Override选项为PCIE SSD First，保存退出；
#                 2、启动进BootManager界面，查看启动设备顺序，有结果A；
#                 3、按ESC退出继续启动，检查第一启动设备，有结果B；
#                 4、重启进Setup菜单，遍历设置PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First/Local Disk Boot Only/Disable，重复步骤1~3，有结果C。
#     Result:     A：PCIE SSD设备排在第一位，剩余启动设备的顺序按照默认顺序保持不变；
#                 B：从PCIE SSD设备启动，且启动成功。
#                 C：Boot override设置的启动设备排在第一位，剩余启动设备的顺序按照默认顺序保持不变，按ESC继续启动时从Boot override设置的启动设备第一启动；Boot override设置为Disable时，保持默认四大类启动顺序不变。
#     Remark:     1、调整动作基于4大启动项分类的基础上进行；除了调整到最高优先级的启动项，其他启动项还是按照4大类进行排序；
#                 2、如果某一类启动项有多个，不支持多个启动项的顺序固定和调整。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1516", "[TC1516] Testcase_BootOverrideLegacy_003", "【Legacy】热键功能与Boot Override优先级测试"))
# def Testcase_BootOverrideLegacy_003():
#     """
#     Name:       【Legacy】热键功能与Boot Override优先级测试
#     Condition:  1、Legacy模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、在Setup菜单Boot界面设置Boot Override选项为USB First，保存退出；
#                 2、系统启动过程中，按F12选择从PXE启动，有结果A；
#                 3、重启系统，按F6选择从SP启动，有结果B。
#     Result:     A：从PXE启动；
#                 B：从SP启动。
#     Remark:     没有用户按键时，BootOverride启动项的优先级最高；但是用户如果通过热键进入Setup，则用户选择的启动设备优先级高于override启动设备。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1517", "[TC1517] Testcase_BootOverrideLegacy_005", "【Legacy】Boot Override设置Local Disk Boot Only测试"))
# def Testcase_BootOverrideLegacy_005():
#     """
#     Name:       【Legacy】Boot Override设置Local Disk Boot Only测试
#     Condition:  1、Legacy模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、进Setup菜单Boot界面，设置Boot Override选项为Local Disk Boot Only，保存退出；
#                 2、启动进BootManager界面，查看启动设备顺序，有结果A；
#                 3、按ESC退出继续启动，检查第一启动设备，有结果B。
#     Result:     A：仅保留PCIE SSD、PCH直出硬盘、Raid卡（包括NVME的VMD）启动项；
#                 B：从Local Disk启动项启动。
#     Remark:     当选择Local Disk Boot Only时，系统只有PCIE SSD、PCH直出硬盘、Raid卡（包括NVME的VMD）启动项可用于启动。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1518", "[TC1518] Testcase_BootOverrideLegacy_006", "【Legacy】带外设置Boot Override选项"))
@mark_legacy_test
def Testcase_BootOverrideLegacy_006():
    """
    Name:       【Legacy】带外设置Boot Override选项
    Condition:  1、Legacy模式；
    Steps:      1、进OS下通过uniCfg -r BootOverride读取变量，检查默认值，有结果A；
                2、OS下通过uniCfg -w BootOverride:X设置变量后重启，进入Setup菜单Boot界面，检查是否生效，有结果B；
                3、通过Redfish接口重复步骤1~2。
    Result:     A：默认值为0，Disabled
                B：设置生效，结果为X
    Remark:     1、选项可选值：
                0：Disabled
                1：PCIE SSD First（仅UEFI模式开放）
                2：iSCSI First
                3：FC First
                4：FCOE First
                5：PCH Direct First
                6：RAID First（包含NVME的VMD）
                7：USB First
                8：Local Disk Boot Only
    """
    try:
        SetUpLib.boot_to_default_os(uefi=False)
        assert PlatMisc.linux_tool_ready(Env.UNI_PATH, PlatMisc.root_path() / "Resource/Unitools/uniCfg", uefi=False)
        assert Sut.UNITOOL_LEGACY_OS.check(**BiosCfg.Boot_Override_def)
        assert Sut.UNITOOL_LEGACY_OS.write(**BiosCfg.Boot_Override_aft)
        assert _check_boot_override()
        BmcLib.clear_cmos()
        assert SetUpLib.boot_to_default_os(uefi=True)  # clear CMOS will reset BootType to UEFI
        assert Sut.BMC_RFISH.read_bios_option(Attr.BOOT_OVERRITE).get(Attr.BOOT_OVERRITE) == Msg.DISABLE
        assert Sut.BMC_RFISH.set_bios_option(**{Attr.BOOT_OVERRITE: boot_override_op[-1]}).status == 200, 'Error: PATCH Fail'
        assert _check_boot_override()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1519", "[TC1519] Testcase_BootOverrideLegacy_007", "【Legacy】BMC设置与Boot Override优先级测试"))
# def Testcase_BootOverrideLegacy_007():
#     """
#     Name:       【Legacy】BMC设置与Boot Override优先级测试
#     Condition:  1、Legacy模式；
#                 2、单板接入不同硬件接口的启动设备，如下：
#                 PCIE SSD First/iSCSI First/FC First/FCOE First/PCH Direct First/Raid First/USB First；
#                 3、BIOS存在四大类启动设备，硬盘、PXE、光驱、软驱，且是默认启动顺序。
#     Steps:      1、单板启动进Setup菜单，此时WEB界面设置从PXE第一启动永久有效； 
#                 2、在Setup菜单Boot界面设置Boot Override选项为USB First，保存退出；
#                 3、启动进BootManager界面，查看启动设备顺序，有结果A；
#                 4、按ESC退出继续启动，检查第一启动设备，有结果B。
#     Result:     A：USB设备均会排在第一位（光驱、软驱），其他启动设备顺序保持设置不变，PXE->硬盘->DVD->Other；
#                 B：从USB设备启动。
#     Remark:     没有用户按键时，BootOverride启动项的优先级最高；但是用户如果通过热键进入Setup，则用户选择的启动设备优先级高于override启动设备。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1520", "[TC1520] Testcase_BootOrderUefi_001", "【UEFI】默认启动顺序测试"))
# def Testcase_BootOrderUefi_001():
#     """
#     Name:       【UEFI】默认启动顺序测试
#     Condition:  1、UEFI模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
#     Steps:      1、单板启动进入Setup菜单Boot->Boot Sequence界面查询默认启动顺序是否正确，有结果A；
#                 3、退出菜单后正常启动，检查是否从硬盘启动，有结果B。
#                 4、x86下电后，去除所有硬盘启动设备；再次上电后，检查是否从第二个启动项启动，有结果C；
#                 5、去除DVD启动项，检查是否从第三个启动项启动，有结果D；
#                 6、去除PXE启动项，检查是否从第四个启动项启动，有结果E。
#     Result:     A：默认大类优先级：HDD,DVD-ROM,PXE,Others；
#                 B：正常从硬盘启动；
#                 C：正常从DVD启动；
#                 D：正常从PXE启动；
#                 E：正常从软驱/U盘启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1521", "[TC1521] Testcase_BootOrderUefi_002", "【UEFI】Setup菜单启动顺序调整测试"))
# def Testcase_BootOrderUefi_002():
#     """
#     Name:       【UEFI】Setup菜单启动顺序调整测试
#     Condition:  1、UEFI模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
#     Steps:      1、单板启动进入Setup菜单Boot->Boot Sequence界面调整启动顺序（Other->PXE->DVD->HDD），保存复位；
#                 2、启动进BootManager界面，查看启动顺序，按ESC退出继续启动OS，检查启动情况，有结果A。
#                 3、重启进Boot->Boot Sequence界面调整启动顺序（PXE->Other->DVD->HDD），保存复位；
#                 4、启动进BootManager界面，查看启动顺序，按ESC退出继续启动OS，检查启动情况，有结果B；
#                 5、重启进Boot->Boot Sequence界面调整启动顺序（DVD->PXE->Other->HDD），保存复位；
#                 6、启动进BootManager界面，查看启动顺序，按ESC退出继续启动OS，检查启动情况，有结果C。
#     Result:     A：启动顺序为Other->PXE->DVD->HDD，正常从U盘（或虚拟软驱启动项）启动；
#                 B：启动顺序为PXE->Other->DVD->HDD，正常从PXE启动；
#                 C：启动顺序为DVD->PXE->Other->HDD，正常从DVD启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1522", "[TC1522] Testcase_BootOrderUefi_003", "【UEFI】启动顺序优先级_Setup菜单和BMC设置"))
# def Testcase_BootOrderUefi_003():
#     """
#     Name:       【UEFI】启动顺序优先级_Setup菜单和BMC设置
#     Condition:  1、UEFI模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
#                 3、Setup菜单设置优先从DVD启动。
#     Steps:      1、BMC Web界面设置启动顺序PXE优先，单次有效；
#                 2、检查是否从PXE启动，有结果A。
#     Result:     A：正常从PXE启动，BMC设置第一启动项优先于Setup菜单。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1523", "[TC1523] Testcase_BootOrderUefi_004", "【UEFI】启动顺序优先级_BMC设置和DEL热键"))
# def Testcase_BootOrderUefi_004():
#     """
#     Name:       【UEFI】启动顺序优先级_BMC设置和DEL热键
#     Condition:  1、UEFI模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
#                 3、Setup菜单启动顺序保持默认设置。
#     Steps:      1、BMC Web界面设置启动顺序PXE优先，单次有效；
#                 2、BIOS启动过程中，按DEL进入FrontPage，选择从DVD启动；
#                 3、检查是否从DVD启动，有结果A。
#     Result:     A：正常从DVD启动，DEL热键优先于BMC设置第一启动项和Setup菜单。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1524", "[TC1524] Testcase_BootOrderUefi_005", "【UEFI】启动顺序优先级_BMC设置和F11热键"))
# def Testcase_BootOrderUefi_005():
#     """
#     Name:       【UEFI】启动顺序优先级_BMC设置和F11热键
#     Condition:  1、UEFI模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
#                 3、Setup菜单启动顺序保持默认设置。
#     Steps:      1、BMC Web界面设置启动顺序PXE优先，单次有效；
#                 2、BIOS启动过程中，按F11进入BootManager，选择从DVD启动；
#                 3、检查是否从DVD启动，有结果A。
#     Result:     A：正常从DVD启动，F11优先于BMC设置第一启动项和Setup菜单。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1525", "[TC1525] Testcase_BootOrderUefi_006", "【UEFI】启动顺序优先级_BMC设置和F12热键"))
def Testcase_BootOrderUefi_006():
    """
    Name:       【UEFI】启动顺序优先级_BMC设置和F12热键
    Condition:  1、UEFI模式；
                2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
                3、Setup菜单启动顺序保持默认设置。
    Steps:      1、BMC Web界面设置启动顺序DVD优先，单次有效；
                2、BIOS启动过程中，按F12选择从PXE启动；
                3、检查是否从PXE启动，有结果A。
    Result:     A：正常从PXE启动，F12优先于BMC设置第一启动项和Setup菜单。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('CD/DVD', once=True)
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Sys.PXE_UEFI_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1526", "[TC1526] Testcase_BootOrderLegacy_001", "【Legacy】默认启动顺序测试"))
# def Testcase_BootOrderLegacy_001():
#     """
#     Name:       【Legacy】默认启动顺序测试
#     Condition:  1、Legacy模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
#     Steps:      1、单板启动进入Setup菜单Boot->Boot Sequence界面查询默认启动顺序是否正确，有结果A；
#                 3、退出菜单后正常启动，检查是否从硬盘启动，有结果B。
#                 4、x86下电后，去除所有硬盘启动设备；再次上电后，检查是否从第二个启动项启动，有结果C；
#                 5、去除DVD启动项，检查是否从第三个启动项启动，有结果D；
#                 6、去除PXE启动项，检查是否从第四个启动项启动，有结果E。
#     Result:     A：默认大类优先级：HDD,DVD-ROM,PXE,Others；
#                 B：正常从硬盘启动；
#                 C：正常从DVD启动；
#                 D：正常从PXE启动；
#                 E：正常从软驱/U盘启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1527", "[TC1527] Testcase_BootOrderLegacy_002", "【Legacy】Setup菜单启动顺序调整测试"))
# def Testcase_BootOrderLegacy_002():
#     """
#     Name:       【Legacy】Setup菜单启动顺序调整测试
#     Condition:  1、Legacy模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘。
#     Steps:      1、单板启动进入Setup菜单Boot->Boot Sequence界面调整启动顺序（Other->PXE->DVD->HDD），保存复位；
#                 2、启动进BootManager界面，查看启动顺序，按ESC退出继续启动OS，检查启动情况，有结果A。
#                 3、重启进Boot->Boot Sequence界面调整启动顺序（PXE->Other->DVD->HDD），保存复位；
#                 4、启动进BootManager界面，查看启动顺序，按ESC退出继续启动OS，检查启动情况，有结果B；
#                 5、重启进Boot->Boot Sequence界面调整启动顺序（DVD->PXE->Other->HDD），保存复位；
#                 6、启动进BootManager界面，查看启动顺序，按ESC退出继续启动OS，检查启动情况，有结果C。
#     Result:     A：启动顺序为Other->PXE->DVD->HDD，正常从U盘（或虚拟软驱启动项）启动；
#                 B：启动顺序为PXE->Other->DVD->HDD，正常从PXE启动；
#                 C：启动顺序为DVD->PXE->Other->HDD，正常从DVD启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1528", "[TC1528] Testcase_BootOrderLegacy_003", "【Legacy】启动顺序优先级_Setup菜单和BMC设置"))
# def Testcase_BootOrderLegacy_003():
#     """
#     Name:       【Legacy】启动顺序优先级_Setup菜单和BMC设置
#     Condition:  1、Legacy模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
#                 3、Setup菜单设置优先从DVD启动。。
#     Steps:      1、BMC Web界面设置启动顺序PXE优先，单次有效；
#                 2、检查是否从PXE启动，有结果A。
#     Result:     A：正常从PXE启动，BMC设置第一启动项优先于Setup菜单。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1529", "[TC1529] Testcase_BootOrderLegacy_004", "【Legacy】启动顺序优先级_BMC设置和DEL热键Continue"))
@mark_legacy_test
def Testcase_BootOrderLegacy_004():
    """
    Name:       【Legacy】启动顺序优先级_BMC设置和DEL热键Continue
    Condition:  1、Legacy模式；
                2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
                3、Setup菜单启动顺序保持默认设置。
    Steps:      1、BMC Web界面设置启动顺序PXE优先，单次有效；
                2、BIOS启动过程中，按DEL进入FrontPage，选择Continue继续启动；
                3、检查是否从PXE启动，有结果A。
    Result:     A：按照BMC设置从PXE启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=True)
        assert SetUpLib.boot_to_setup()
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_LEGACY_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1530", "[TC1530] Testcase_BootOrderLegacy_005", "【Legacy】启动顺序优先级_BMC设置和F11热键"))
# def Testcase_BootOrderLegacy_005():
#     """
#     Name:       【Legacy】启动顺序优先级_BMC设置和F11热键
#     Condition:  1、Legacy模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
#                 3、Setup菜单启动顺序保持默认设置。
#     Steps:      1、BMC Web界面设置启动顺序PXE优先，单次有效；
#                 2、BIOS启动过程中，按F11进入BootManager，选择从DVD启动；
#                 3、检查是否从DVD启动，有结果A。
#     Result:     A：正常从DVD启动，F11优先于BMC设置第一启动项和Setup菜单。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1531", "[TC1531] Testcase_BootOrderLegacy_006", "【Legacy】启动顺序优先级_BMC设置和F12热键"))
@mark_legacy_test
def Testcase_BootOrderLegacy_006():
    """
    Name:       【Legacy】启动顺序优先级_BMC设置和F12热键
    Condition:  1、Legacy模式；
                2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
                3、Setup菜单启动顺序保持默认设置。
    Steps:      1、BMC Web界面设置启动顺序DVD优先，单次有效；
                2、BIOS启动过程中，按F12选择从PXE启动；
                3、检查是否从PXE启动，有结果A。
    Result:     A：正常从PXE启动，F12优先于BMC设置第一启动项和Setup菜单。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('CD/DVD', once=True)
        assert SetUpLib.boot_with_hotkey(Key.F12, SutConfig.Sys.PXE_LEGACY_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1532", "[TC1532] Testcase_BootOrderLegacy_007", "【Legacy】启动顺序优先级_BMC设置和Oprom热键"))
# def Testcase_BootOrderLegacy_007():
#     """
#     Name:       【Legacy】启动顺序优先级_BMC设置和Oprom热键
#     Condition:  1、Legacy模式；
#                 2、单板安装四大类启动设备，硬盘、PXE、DVD光驱、软驱/U盘；
#                 3、Setup菜单启动顺序保持默认设置。
#     Steps:      1、BMC Web界面设置启动顺序Others优先，单次有效；
#                 2、BIOS启动过程中，根据Pcie设备Oprom提示按热键，检查能否进入设备的配置界面，有结果A；
#                 3、退出配置界面继续启动，检查是否从Others启动，有结果B。
#     Result:     A：正常进入设备的配置界面；
#                 B：从Others启动项启动。
#     Remark:     1、不同设备进入配置界面的热键不同，以实际热键提示为准。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1533", "[TC1533] Testcase_PchHddBootNameUefi_001", "【UEFI】主板SATA口启动项丝印显示"))
# def Testcase_PchHddBootNameUefi_001():
#     """
#     Name:       【UEFI】主板SATA口启动项丝印显示
#     Condition:  1、UEFI模式；
#                 2、主板SATA口满配硬盘，且已安装PCH直出OS。
#     Steps:      1、启动进BootManager界面，检查SATA硬盘启动项是否正确显示对应Port口，有结果A。
#     Result:     A：启动项带对应Port口丝印，HDD0和HDD1。
#     Remark:     1、主板出两个SATA口。
#                 2、5885H V7主板SATA口接的是M.2，对应port0和port1。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1534", "[TC1534] Testcase_PchHddBootNameUefi_002", "【UEFI】背板SATA口启动项丝印显示"))
# def Testcase_PchHddBootNameUefi_002():
#     """
#     Name:       【UEFI】背板SATA口启动项丝印显示
#     Condition:  1、UEFI模式；
#                 2、接PCH直出硬盘背板；
#                 3、背板接PCH直出OS的硬盘。
#     Steps:      1、启动进BootManager界面，检查SATA硬盘启动项是否正确显示对应Port口，有结果A；
#                 2、遍历硬盘背板上所有槽位，重复步骤1。
#     Result:     A：启动项带对应Port口丝印，编号从2开始，依次递增。
#     Remark:     1、5885H V7 SATA0控制器port口丝印编号为0-4；SATA1下SATA盘丝印编号为4-7。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1535", "[TC1535] Testcase_PchHddBootNameLegacy_001", "【Legacy】主板SATA口启动项丝印显示"))
# def Testcase_PchHddBootNameLegacy_001():
#     """
#     Name:       【Legacy】主板SATA口启动项丝印显示
#     Condition:  1、Legacy模式；
#                 2、主板SATA口满配硬盘，且已安装PCH直出OS。
#     Steps:      1、启动进BootManager界面，检查SATA硬盘启动项是否正确显示对应Port口，有结果A。
#     Result:     A：启动项带对应Port口丝印，HDD0和HDD1。
#     Remark:     1、主板出两个SATA口;
#                 2、5885H V7主板SATA口接的是M.2，对应port0和port1。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1536", "[TC1536] Testcase_PchHddBootNameLegacy_002", "【Legacy】背板SATA口启动项丝印显示"))
# def Testcase_PchHddBootNameLegacy_002():
#     """
#     Name:       【Legacy】背板SATA口启动项丝印显示
#     Condition:  1、Legacy模式；
#                 2、接PCH直出硬盘背板；
#                 3、背板接PCH直出OS的硬盘。
#     Steps:      1、启动进BootManager界面，检查SATA硬盘启动项是否正确显示对应Port口，有结果A；
#                 2、遍历硬盘背板上所有槽位，重复步骤1。
#     Result:     A：启动项带对应Port口丝印，编号从2开始，依次递增。
#     Remark:     1、5885H V7 SATA0控制器port口丝印编号为0-4；SATA1下SATA盘丝印编号为4-7。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1537", "[TC1537] Testcase_PxePortPrintUefi_001", "【UEFI】PXE网口丝印显示功能测试_ipv4"))
# def Testcase_PxePortPrintUefi_001():
#     """
#     Name:       【UEFI】PXE网口丝印显示功能测试_ipv4
#     Condition:  1、UEFI模式；
#                 2、ipv4模式；
#                 3、存在PXE设备。
#     Steps:      1、启动进Boot Manage菜单，检查PXE启动项显示，有结果A；
#                 2、从PXE启动，检查KVM显示PXE启动过程，结果B。
#     Result:     A：在PXE启动项末尾增加“ - PortX"，X从1开始编码，Port口丝印与实际一致；
#                 B：PXE启动时打印提示信息： Booting EFI Network for IPv4(MAC)- PortX。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1538", "[TC1538] Testcase_PxePortPrintUefi_002", "【UEFI】PXE网口丝印显示功能测试_ipv6"))
# def Testcase_PxePortPrintUefi_002():
#     """
#     Name:       【UEFI】PXE网口丝印显示功能测试_ipv6
#     Condition:  1、UEFI模式；
#                 2、ipv6模式；
#                 3、存在PXE设备。
#     Steps:      1、单板启动进入Boot Manage菜单，检查PXE启动项显示，有结果A；
#                 2、从PXE启动，检查KVM显示PXE启动过程，结果B。
#     Result:     A：在PXE启动项末尾增加“ - PortX"，X从1开始编码，Port口丝印与实际一致；
#                 B：PXE启动时打印提示信息： Booting EFI Network for IPv6(MAC)- PortX。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()



@core.test_case(("1539", "[TC1539] Testcase_BootFailPolicy_001", "Boot Fail Policy设置菜单检查"))
def Testcase_BootFailPolicy_001():
    """
    Name:       Boot Fail Policy设置菜单检查
    Condition:
    Steps:      1、单板启动进入Setup菜单，查看Boot Fail Policy菜单选项，有结果A;
                2、通过带外配置设置Boot Fail Policy，有结果B；
                3、查看BMC操作日志，有结果C。
    Result:     A：提供Boot Fail Policy菜单，选项为Boot Retry/Cold Boot/None，默认Boot Retry;
                B: 可正常配置为Boot Retry/Cold Boot/None，且配置能够生效；
                C:有记录1条修改Boot Fail Policy选项日志。
    Remark:
    """
    boot_fail_policy = ['Boot Retry', 'Cold Boot', 'None']
    set_boot_fail_policy = "Set global enables to (RAW:0c) successfully"
    try:
        # Set 1
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.get_option_value(Msg.BOOT_FAIL_POLICY) == boot_fail_policy[0]
        assert SetUpLib.get_all_values(Msg.BOOT_FAIL_POLICY) == boot_fail_policy
        # Set 2
        assert SetUpLib.boot_to_default_os()
        time_now = BmcLib.get_bmc_datetime()
        Sut.UNITOOL.write(**BiosCfg.Boot_Fail_Policy_aft)
        Sut.UNITOOL.check(**BiosCfg.Boot_Fail_Policy_aft)
        # Set 3
        assert SetUpLib.boot_with_hotkey(Key.DEL, Msg.HOME_PAGE)
        assert PlatMisc.bmc_log_exist(set_boot_fail_policy, time_now, operate=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1540", "[TC1540] Testcase_BootFailPolicy_003", "上报Boot Fail Policy选项操作日志到BMC测试"))
def Testcase_BootFailPolicy_003():
    """
    Name:       上报Boot Fail Policy选项操作日志到BMC测试
    Condition:
    Steps:      1、设置Boot Fail Policy菜单，F10保存退出，查看BMC操作日志，有结果A。
    Result:     A：菜单操作正常上报。
    Remark:
    """
    web_boot_fail_policy = "Set Setup item Boot Fail Policy value from Boot Retry to Cold Boot success"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        time_now = BmcLib.get_bmc_datetime()
        SetUpLib.set_option_value(Msg.BOOT_FAIL_POLICY, "Cold Boot", save=True)
        assert PlatMisc.bmc_log_exist(web_boot_fail_policy, time_now, operate=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1541", "[TC1541] Testcase_PxeRetry_001", "PXE Retry菜单设置测试"))
# def Testcase_PxeRetry_001():
#     """
#     Name:       PXE Retry菜单设置测试
#     Condition:  1、BIOS默认值配置。
#     Steps:      1、启动进Boot菜单，查看是否存在PXE Retry Count菜单，有结果A；
#                 2、Boot Fail Policy设置为Cold Boot或None，检查PXE Retry Count菜单，有结果B。
#     Result:     A：显示PXE Retry Count菜单，默认值为1；
#                 B：PXE Retry Count菜单隐藏或置灰。
#     Remark:     只有Boot Retry使能，才可进行多次PXE retry。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1542", "[TC1542] Testcase_PxeRetry_002", "PXE Retry设置范围测试"))
def Testcase_PxeRetry_002():
    """
    Name:       PXE Retry设置范围测试
    Condition:
    Steps:      1、启动进Boot菜单修改PXE Retry Count选项，设置为0，有结果A；
                2、设置PXE Retry Count选项为100，有结果A；
                3、设置PXE Retry Count选项为1~99之间的值，有结果B。
    Result:     A：设置失败；
                B：设置成功。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert not SetUpLib.set_option_value(Msg.PXE_RETRY_COUNT, str(0), integer=True)
        assert SetUpLib.set_option_value(Msg.PXE_RETRY_COUNT, str(random.randint(1, 99)), integer=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1543", "[TC1543] Testcase_PxeRetryUefi_001", "【UEFI】设置PXE Retry次数测试"))
# def Testcase_PxeRetryUefi_001():
#     """
#     Name:       【UEFI】设置PXE Retry次数测试
#     Condition:  1、BIOS默认值配置；
#                 2、PXE服务器未搭建，硬盘OS能正常启动。
#     Steps:      1、启动进Boot菜单修改PXE Retry Count选项，设置为5，保存退出；
#                 2、启动过程中按F12热键，开始PXE引导，检查PXE启动轮询次数与菜单设置是否一致,有结果A；
#                 3、轮询结束后，检查能否从硬盘启动，有结果B。
#     Result:     A：PXE启动失败，轮询5次；
#                 B：从硬盘启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1544", "[TC1544] Testcase_PxeRetryUefi_002", "【UEFI】设置PXE Retry次数边界值测试"))
# def Testcase_PxeRetryUefi_002():
#     """
#     Name:       【UEFI】设置PXE Retry次数边界值测试
#     Condition:  1、BIOS默认值配置；
#                 2、PXE服务器未搭建，硬盘OS能正常启动。
#     Steps:      1、启动进Boot菜单修改PXE Retry Count选项，设置为1，保存退出；
#                 2、启动过程中按F12热键，开始PXE引导，检查PXE启动轮询次数与菜单设置是否一致，有结果A；
#                 3、轮询结束后，检查能否从硬盘启动，有结果B。
#     Result:     A：PXE启动失败，轮询1次；
#                 B：从硬盘启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1545", "[TC1545] Testcase_PxeRetryLegacy_001", "【Legacy】设置PXE Retry次数测试"))
# def Testcase_PxeRetryLegacy_001():
#     """
#     Name:       【Legacy】设置PXE Retry次数测试
#     Condition:  1、Legacy模式；
#                 2、PXE服务器未搭建，硬盘OS能正常启动。
#     Steps:      1、启动进Boot菜单修改PXE Retry Count选项，设置为5，保存退出；
#                 2、启动过程中按F12热键，开始PXE引导，检查PXE启动轮询次数与菜单设置是否一致,有结果A；
#                 3、轮询结束后，检查能否从硬盘启动，有结果B。
#     Result:     A：PXE启动失败，轮询5次；
#                 B：从硬盘启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1546", "[TC1546] Testcase_PxeRetryLegacy_002", "【Legacy】设置PXE Retry次数边界值测试"))
# def Testcase_PxeRetryLegacy_002():
#     """
#     Name:       【Legacy】设置PXE Retry次数边界值测试
#     Condition:  1、Legacy模式；
#                 2、PXE服务器未搭建，硬盘OS能正常启动。
#     Steps:      1、启动进Boot菜单修改PXE Retry Count选项，设置为1，保存退出；
#                 2、启动过程中按F12热键，开始PXE引导，检查PXE启动轮询次数与菜单设置是否一致，有结果A；
#                 3、轮询结束后，检查能否从硬盘启动，有结果B。
#     Result:     A：PXE启动失败，轮询1次；
#                 B：从硬盘启动。
#     Remark:     
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1547", "[TC1547] Testcase_SpBoot_001", "SP Boot设置菜单检查"))
def Testcase_SpBoot_001():
    """
    Name:       SP Boot设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，Boot界面查看是否有SP Boot开关，可选值及默认值，有结果A；
                2、关闭USB Boot选项，检查SP Boot选项是否可设置，有结果B。
    Result:     A：有SP Boot选项，Enabled、Disabled可选，默认Enabled；
                B：SP Boot选项隐藏。
    Remark:
    """
    sp_value = [Msg.DISABLE, Msg.ENABLE]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.get_option_value(Msg.SP_BOOT) == sp_value[1]
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.SP_BOOT), sp_value)
        assert SetUpLib.set_option_value(Msg.USB_BOOT, sp_value[0])
        assert not SetUpLib.locate_option(Msg.SP_BOOT)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1548", "[TC1548] Testcase_SpBoot_002", "SP启动密码校验"))
def Testcase_SpBoot_002():
    """
    Name:       SP启动密码校验
    Condition:  1、使能SP Boot；
                2、系统密码不为空。
    Steps:      1、启动时按F6热键选择从SP启动，检查是否校验密码，有结果A；
                2、输入错误的登录密码，检查启动情况，有结果B；
                3、输入正确的登录密码，检查启动情况，有结果C。
    Result:     A：需要校验密码；
                B：密码错误，无法启动，BMC Web安全日志记录SP启动密码校验失败；
                C：从SP启动成功，BMC Web安全日志提示SP登录成功；
    Remark:
    """
    pw_error = PwdLib.gen_pw(total=PwdLib.PW.MIN)
    pw_list = [pw_error, Msg.BIOS_PASSWORD]
    bmc_security_log = ["Security,BIOS,Check SP Boot Password error",
                        "Security,BIOS,User(Administrator),SP Boot login success"]
    try:
        for pw in pw_list:
            assert SetUpLib.boot_with_hotkey(Key.F6, Msg.F6_PRESSED)
            assert SetUpLib.wait_msg(Msg.DEL_CONFIRM)
            time_now = BmcLib.get_bmc_datetime()
            SetUpLib.send_data_enter(pw)
            if SetUpLib.wait_msg(PwdLib.pw_invalid, timeout=2):
                assert PlatMisc.bmc_log_exist(bmc_security_log[0], time_now, security=True)
            else:
                assert PlatMisc.bmc_log_exist(bmc_security_log[1], time_now, security=True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1549", "[TC1549] Testcase_SpBootUefi_001", "【UEFI】SP启动功能测试_F6"))
def Testcase_SpBootUefi_001():
    """
    Name:       【UEFI】SP启动功能测试_F6
    Condition:  1、UEFI模式；
                2、SP已部署。
    Steps:      1、启动进Setup菜单，关闭SP Boot开关，F10保存重启，启动时按F6检查SP启动情况，有结果A；
                2、启动进Setup菜单，打开SP Boot开关，F10保存重启，启动时按F6检查SP启动情况，有结果B；
    Result:     A：SP启动失败；
                B：SP启动成功。
    Remark:
    """
    sp_value = [Msg.DISABLE, Msg.ENABLE]
    try:
        for sp in sp_value:
            assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
            assert SetUpLib.locate_option(Msg.SP_BOOT)
            assert SetUpLib.set_option_value(Msg.SP_BOOT, sp, save=True)
            if sp == sp_value[1]:
                assert SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.PW_PROMPT)
                assert PlatMisc.is_sp_boot_success()
                logging.info("SP set enable pass")
            else:
                SetUpLib.wait_boot_msgs(Msg.LINUX_GRUB)
                logging.info("SP set disable pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1550", "[TC1550] Testcase_SpBootUefi_002", "【UEFI】SP启动功能测试_IPMI"))
# def Testcase_SpBootUefi_002():
#     """
#     Name:       【UEFI】SP启动功能测试_IPMI
#     Condition:  1、UEFI模式；
#                 2、SP已部署。
#     Steps:      1、启动进Setup菜单，关闭SP Boot开关，IPMI发送SP启动标志位，F10保存重启检查SP启动情况，有结果A；
#                 2、启动进Setup菜单，打开SP Boot开关，IPMI发送SP启动标志位，F10保存重启检查SP启动情况，有结果B；
#     Result:     A：SP启动失败；
#                 B：SP启动成功。
#     Remark:     IPMI设置SPStartFlag属性：ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x35 0x80 0x00 0x01 0x00 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00 0x00 0x01 0x01
#                 IPMI查询SPStartFlag属性：
#                 ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x36 0x80 0x00 0x01 0xff 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1551", "[TC1551] Testcase_SpBootUefi_005", "【UEFI】IPMI命令设置SP启动后不响应热键测试"))
# def Testcase_SpBootUefi_005():
#     """
#     Name:       【UEFI】IPMI命令设置SP启动后不响应热键测试
#     Condition:  1、UEFI模式；
#                 2、SP已部署。
#     Steps:      1、IPMI发送SP启动标志位，启动时按下Del热键，检查启动情况，有结果A；
#                 2、重启系统，启动时按下Del热键，检查启动情况，有结果B；
#                 3、遍历所有热键，重复步骤1~2。
#     Result:     A：不响应按键操作，SP启动成功；
#                 B：响应按键操作，进入对应菜单。
#     Remark:     IPMI设置SPStartFlag属性：ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x35 0x80 0x00 0x01 0x00 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00 0x00 0x01 0x01
#                 IPMI查询SPStartFlag属性：
#                 ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x36 0x80 0x00 0x01 0xff 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1552", "[TC1552] Testcase_SpBootUefi_007", "【UEFI】SP启动过程中异常复位测试"))
def Testcase_SpBootUefi_007():
    """
    Name:       【UEFI】SP启动过程中异常复位测试
    Condition:  1、UEFI模式；
                2、使能SP Boot；
                3、SP已部署。
    Steps:      1、启动时按F6从SP启动，SP启动过程中复位系统；
                2、启动时再次按F6从SP启动，检查启动情况，有结果A；
                3、重复步骤1~2 3次，有结果A。
    Result:     A：SP启动成功。
    Remark:
    """
    try:
        for i in range(1, 4):
            assert SetUpLib.boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_UEFI)
            time.sleep(15)
            assert BmcLib.force_reset()
            assert SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_UEFI)
            assert PlatMisc.is_sp_boot_success()
            logging.info(f"No.{i} boot from SP pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1553", "[TC1553] Testcase_SpBootLegacy_001", "【Legacy】SP启动功能测试_F6"))
@mark_legacy_test
def Testcase_SpBootLegacy_001():
    """
    Name:       【Legacy】SP启动功能测试_F6
    Condition:  1、Legacy模式；
                2、SP已部署。
    Steps:      1、启动进Setup菜单，关闭SP Boot开关，F10保存重启，启动时按F6检查SP启动情况，有结果A；
                2、启动进Setup菜单，打开SP Boot开关，F10保存重启，启动时按F6检查SP启动情况，有结果B；
    Result:     A：SP启动失败；
                B：SP启动成功。
    Remark:
    """
    sp_value = [Msg.DISABLE, Msg.ENABLE]
    try:
        for sp in sp_value:
            assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
            assert SetUpLib.locate_option(Msg.SP_BOOT)
            assert SetUpLib.set_option_value(Msg.SP_BOOT, sp, save=True)
            if sp == sp_value[1]:
                assert SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.PW_PROMPT)
                assert PlatMisc.is_sp_boot_success()
                logging.info("SP set enable pass")
            else:
                SetUpLib.wait_boot_msgs(Msg.LINUX_GRUB)
                logging.info("SP set disable pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1554", "[TC1554] Testcase_SpBootLegacy_002", "【Legacy】SP启动功能测试_IPMI"))
# def Testcase_SpBootLegacy_002():
#     """
#     Name:       【Legacy】SP启动功能测试_IPMI
#     Condition:  1、Legacy模式；
#                 2、SP已部署。
#     Steps:      1、启动进Setup菜单，关闭SP Boot开关，IPMI发送SP启动标志位，F10保存重启检查SP启动情况，有结果A；
#                 2、启动进Setup菜单，打开SP Boot开关，IPMI发送SP启动标志位，F10保存重启检查SP启动情况，有结果B；
#     Result:     A：SP启动失败；
#                 B：SP启动成功。
#     Remark:     IPMI设置SPStartFlag属性：ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x35 0x80 0x00 0x01 0x00 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00 0x00 0x01 0x01
#                 IPMI查询SPStartFlag属性：
#                 ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x36 0x80 0x00 0x01 0xff 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1555", "[TC1555] Testcase_SpBootLegacy_005", "【Legacy】IPMI命令设置SP启动后不响应热键测试"))
# def Testcase_SpBootLegacy_005():
#     """
#     Name:       【Legacy】IPMI命令设置SP启动后不响应热键测试
#     Condition:  1、Legacy模式；
#                 2、SP已部署。
#     Steps:      1、IPMI发送SP启动标志位，启动时按下Del热键，检查启动情况，有结果A；
#                 2、重启系统，启动时按下Del热键，检查启动情况，有结果B；
#                 3、遍历所有热键，重复步骤1~2。
#     Result:     A：不响应按键操作，SP启动成功；
#                 B：响应按键操作，进入对应菜单。
#     Remark:     IPMI设置SPStartFlag属性：ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x35 0x80 0x00 0x01 0x00 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00 0x00 0x01 0x01
#                 IPMI查询SPStartFlag属性：
#                 ipmitool -I lanplus -H 192.168.49.19 -U Administrator -P Admin@9000 raw 0x30 0x93 0xdb 0x07 0x00 0x36 0x80 0x00 0x01 0xff 0x00 0x00 0xff 0xff 0x00 0x01 0x00 0x02 0x00
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1556", "[TC1556] Testcase_SpBootLegacy_007", "【Legacy】SP启动过程中异常复位测试"))
@mark_legacy_test
def Testcase_SpBootLegacy_007():
    """
    Name:       【Legacy】SP启动过程中异常复位测试
    Condition:  1、Legacy模式；
                2、使能SP Boot；
                3、SP已部署。
    Steps:      1、启动时按F6从SP启动，SP启动过程中复位系统；
                2、启动时再次按F6从SP启动，检查启动情况，有结果A；
                3、重复步骤1~2 3次，有结果A。
    Result:     A：SP启动成功。
    Remark:
    """
    try:
        for i in range(1, 4):
            assert SetUpLib.boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_LEGACY)
            time.sleep(15)
            assert BmcLib.force_reset()
            assert SetUpLib.continue_boot_with_hotkey(Key.F6, Msg.F6_CONFIRM_LEGACY)
            assert PlatMisc.is_sp_boot_success()
            logging.info(f"No.{i} boot from SP pass")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

