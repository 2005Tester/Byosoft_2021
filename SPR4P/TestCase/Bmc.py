from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Bmc Test Case
# TC 1700-1806
####################################


@core.test_case(("1700", "[TC1700] Testcase_ReportPcieBdfToBmc_001", "PCIe设备BDF信息上报BMC"))
def Testcase_ReportPcieBdfToBmc_001():
    """
    Name:       PCIe设备BDF信息上报BMC
    Condition:  1、接PCIe卡；
                2、开启BT通道。
    Steps:      1、启动进OS，检查串口日志中PCIe设备BDF信息，有结果A；
                2、BMC Web侧检查PCIe设备所属CPU和SLOT信息是否正确，有结果B；
                3、BT通道搜索“58 C6”检查PCIe上报BDF信息，有结果C。
    Result:     A：串口打印BDF信息正确；
                B：Web界面显示信息正确；
                C：BT通道上报BDF信息正确。
    Remark:     1、BMC命令行输入以下指令打开BT通道：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、串口搜索关键字“RootBusBDF”。
    """
    str_flg = []
    pcie_bdf = (lambda z: dict([(x, y) for y, x in z.items()]))(SutConfig.Sys.PCIE_SLOT)
    for key, value in pcie_bdf.items():
        for i in value.split('.'):
            if len(i) > 2:
                str_flg.append(''.join(i.replace(':', ' ')))
        '''
        bios only upload func0 bdf to bt channel.
        '''
    str_flg_func0 = [str(j) + ' 00' for j in str_flg]
    flag = ['58 c6'] + str_flg_func0
    try:
        assert BmcLib.force_reset()
        assert BmcLib.read_bt_data(flag, timeout=SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    # finally:
    #     BmcLib.clear_cmos()


@core.test_case(("1701", "[TC1701] Testcase_ReportPcieBdfToBmc_002", "PCIe设备BDF信息上报BMC_设备不在位"))
def Testcase_ReportPcieBdfToBmc_002():
    """
    Name:       PCIe设备BDF信息上报BMC_设备不在位
    Condition:  1、不接PCIe卡；
                2、开启BT通道。
    Steps:      1、启动进OS，检查串口日志中PCIe设备BDF信息，有结果A；
                2、BMC Web侧检查PCIe设备所属CPU和SLOT信息是否正确，有结果B；
                3、BT通道搜索“58 C6”检查PCIe上报BDF信息，有结果C。
    Result:     A：未接设备时BDF为FF，若未接任何Pcie设备，不打印BDF分配表；
                B：Web界面对应SLOT不显示设备信息；
                C：BT通道对应SLOT的BDF为FF。
    Remark:     1、BMC命令行输入以下指令打开BT通道：
                maint_debug_cli
                attach ipmi
                trace ch=bt
                2、串口搜索关键字“RootBusBDF”。
    """
    str_flg = []
    pcie_bdf = (lambda z: dict([(x, y) for y, x in z.items()]))(SutConfig.Sys.PCIE_SLOT)
    for key, value in pcie_bdf.items():
        for i in value.split('.'):
            if len(i) > 2:
                str_flg.append(''.join(i.replace(':', ' ')))
        '''
        bios only upload func0 bdf to bt channel.
        '''
    str_flg_func0 = [str(j) + ' 00' for j in str_flg]
    flag = ['58 c6'] + str_flg_func0
    try:
        assert BmcLib.force_reset()
        assert not BmcLib.read_bt_data(flag, timeout=SutConfig.Env.BOOT_DELAY), \
            'devices should be removed before run the test'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1702", "[TC1702] Testcase_ReportNvmeBdfToBmc_001", "Nvme设备BDF信息上报BMC"))
# def Testcase_ReportNvmeBdfToBmc_001():
#     """
#     Name:       Nvme设备BDF信息上报BMC
#     Condition:  1、接NVMe盘；
#                 2、开启BT通道。
#     Steps:      1、启动进OS，检查串口日志中NVMe盘BDF信息，有结果A；
#                 2、BMC Web侧检查NVMe盘所属CPU和丝印信息是否正确，有结果B；
#                 3、BT通道搜索“58 C8”检查NVMe上报BDF信息，有结果C。
#     Result:     A：串口打印BDF信息正确；
#                 B：Web界面显示信息正确；
#                 C：BT通道上报BDF信息正确。
#     Remark:     1、BMC命令行输入以下指令打开BT通道：
#                 maint_debug_cli
#                 attach ipmi
#                 trace ch=bt
#                 2、串口搜索关键字“RootBusBDF”。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1703", "[TC1703] Testcase_ReportVerToBmc_001", "BIOS版本号上报BMC测试"))
def Testcase_ReportVerToBmc_001():
    """
    Name:       BIOS版本号上报BMC测试
    Condition:
    Steps:      1、启动进Setup菜单，BMC Web界面检查BIOS版本号显示是否正确，有结果A；
                2、对比Setup菜单与BMC Web显示版本号是否一致，有结果B
    Result:     A：BMC Web页面正确显示BIOS版本号；
                B：版本号一致。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.bios_version() == SutConfig.Env.BIOS_VER_LATEST
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1704", "[TC1704] Testcase_ReportSmbiosToBmc_001", "SMBIOS信息上报BMC测试"))
def Testcase_ReportSmbiosToBmc_001():
    """
    Name:       SMBIOS信息上报BMC测试
    Condition:  1、开启BT通道。
    Steps:      1、单板启动，检查启动阶段BT通道是否上报SMBIOS信息到BMC(关键字：DB 07 00 04 00)，有结果A。
    Result:     A：BT通道上报SMBIOS信息到BMC。
    Remark:     1、BMC命令行输入以下指令打开BT通道：
                maint_debug_cli
                attach ipmi
                trace ch=bt
    """
    flag = ["92 14 E3 00 04 00"]
    try:
        assert BmcLib.force_reset()
        assert BmcLib.read_bt_data(flag, timeout=SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1705", "[TC1705] Testcase_BmcSetBootOptionUefi_001", "【UEFI】BMC设置硬盘为优先引导介质、单次有效"))
# def Testcase_BmcSetBootOptionUefi_001():
#     """
#     Name:       【UEFI】BMC设置硬盘为优先引导介质、单次有效
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置硬盘为优先引导介质、单次有效；
#                 4、Setup菜单设置启动顺序为Other->PXE->DVD->HDD。
#     Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
#                 2、再次复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：从硬盘启动；
#                 B：从软驱启动。
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


@core.test_case(("1706", "[TC1706] Testcase_BmcSetBootOptionUefi_002", "【UEFI】BMC设置硬盘为优先引导介质、永久有效"))
def Testcase_BmcSetBootOptionUefi_002():
    """
    Name:       【UEFI】BMC设置硬盘为优先引导介质、永久有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置硬盘为优先引导介质、永久有效；
                4、Setup菜单设置启动顺序为Other->PXE->DVD->HDD。
    Steps:      1、复位单板3次，查看是否每次都从硬盘启动，有结果A。
    Result:     A：从硬盘启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('Hard Drive', once=False)
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.BOOT_SEQUENCE)
        assert SetUpLib.locate_option(Msg.MENU_OTHERS_BOOT)
        SetUpLib.send_key(Key.F6 * 3)
        assert SetUpLib.locate_option(Msg.MENU_PXE_BOOT)
        SetUpLib.send_key(Key.F6 * 2)
        assert SetUpLib.locate_option(Msg.MENU_DVD_BOOT)
        SetUpLib.send_key(Key.F6)
        SetUpLib.send_keys(Key.SAVE_RESET)
        for i in range(1, 4):
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY), f"No.{i} boot to HDD is fail"
            BmcLib.force_reset()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


# @core.test_case(("1707", "[TC1707] Testcase_BmcSetBootOptionUefi_003", "【UEFI】BMC设置DVD为优先引导介质、单次有效"))
# def Testcase_BmcSetBootOptionUefi_003():
#     """
#     Name:       【UEFI】BMC设置DVD为优先引导介质、单次有效
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置光驱为优先引导介质、单次有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
#                 2、再次复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：从DVD启动；
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


# @core.test_case(("1708", "[TC1708] Testcase_BmcSetBootOptionUefi_004", "【UEFI】BMC设置DVD为优先引导介质、永久有效"))
# def Testcase_BmcSetBootOptionUefi_004():
#     """
#     Name:       【UEFI】BMC设置DVD为优先引导介质、永久有效
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置光驱为优先引导介质、永久有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、复位单板3次，查看是否每次都从光驱启动，有结果A。
#     Result:     A：从DVD启动。
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


@core.test_case(("1709", "[TC1709] Testcase_BmcSetBootOptionUefi_005", "【UEFI】BMC设置PXE为优先引导介质、单次有效"))
def Testcase_BmcSetBootOptionUefi_005():
    """
    Name:       【UEFI】BMC设置PXE为优先引导介质、单次有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、单次有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、再次复位单板，查看从何种启动介质启动，有结果B；
    Result:     A：从PXE启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=True)
        BmcLib.force_reset()
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG, SutConfig.Env.BOOT_DELAY)
        BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1710", "[TC1710] Testcase_BmcSetBootOptionUefi_006", "【UEFI】BMC设置PXE为优先引导介质、永久有效"))
def Testcase_BmcSetBootOptionUefi_006():
    """
    Name:       【UEFI】BMC设置PXE为优先引导介质、永久有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、复位单板3次，查看是否每次都从PXE启动，有结果A。
    Result:     A：从PXE启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=False)
        for i in range(1, 4):
            BmcLib.force_reset()
            assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG, SutConfig.Env.BOOT_DELAY), f"No.{i} boot from PXE is fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


# @core.test_case(("1711", "[TC1711] Testcase_BmcSetBootOptionUefi_007", "【UEFI】BMC设置软驱为优先引导介质、单次有效"))
# def Testcase_BmcSetBootOptionUefi_007():
#     """
#     Name:       【UEFI】BMC设置软驱为优先引导介质、单次有效
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置软驱/可移动插拔设备为优先引导介质、单次有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
#                 2、再次复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：从软驱启动；
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


# @core.test_case(("1712", "[TC1712] Testcase_BmcSetBootOptionUefi_008", "【UEFI】BMC设置软驱为优先引导介质、永久有效"))
# def Testcase_BmcSetBootOptionUefi_008():
#     """
#     Name:       【UEFI】BMC设置软驱为优先引导介质、永久有效
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置软驱/可移动插拔设备为优先引导介质、永久有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、复位单板3次，查看是否每次都从软驱启动，有结果A。
#     Result:     A：从软驱启动。
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

def _boot_os_form_bios(type_os_ip):
    try:
        BmcLib.force_reset()
        assert SetUpLib.wait_msg(Msg.PW_PROMPT, timeout=Env.BOOT_DELAY)
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        SetUpLib.send_key(Key.ENTER)
        assert MiscLib.ping_sut(type_os_ip, Env.BOOT_DELAY), f"boot to os from bios is fail"
        return True
    except Exception as e:
        logging.error(e)
        return False


@core.test_case(("1713", "[TC1713] Testcase_BmcSetBootOptionUefi_009", "【UEFI】BMC设置BIOS设置为优先引导介质、单次有效"))
def Testcase_BmcSetBootOptionUefi_009():
    """
    Name:       【UEFI】BMC设置BIOS设置为优先引导介质、单次有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置BIOS设置为优先引导介质、单次有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、再次复位单板，查看从何种启动介质启动，有结果B；
    Result:     A：从“BIOS设置”启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        # Steps 1
        assert BmcWeb.BMC_WEB.set_boot_overwrite('BIOS Settings', once=True)
        assert _boot_os_form_bios(SutConfig.Env.OS_IP)
        # Steps 2
        BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY), f"boot from HDD is fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1714", "[TC1714] Testcase_BmcSetBootOptionUefi_010", "【UEFI】BMC设置BIOS设置为优先引导介质、永久有效"))
def Testcase_BmcSetBootOptionUefi_010():
    """
    Name:       【UEFI】BMC设置BIOS设置为优先引导介质、永久有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置BIOS设置为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、复位单板3次，查看是否每次都从BIOS设置启动，有结果A。
    Result:     A：从“BIOS设置”启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('BIOS Settings', once=False)
        for i in range(1, 4):
            assert _boot_os_form_bios(SutConfig.Env.OS_IP)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


def _boot_no_override(pxe_type_msg, type_os_ip, tag: bool = False):
    try:
        BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=False)
        BmcLib.force_reset()
        assert SetUpLib.wait_msg(pxe_type_msg, SutConfig.Env.BOOT_DELAY)
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=tag)
        for i in range(1, 4):
            BmcLib.force_reset()
            assert MiscLib.ping_sut(type_os_ip, SutConfig.Env.BOOT_DELAY), f"boot from HDD is fail"
        return True
    except Exception as e:
        logging.error(e)
        return False

@core.test_case(("1715", "[TC1715] Testcase_BmcSetBootOptionUefi_011", "【UEFI】BMC设置未配置为优先引导介质、单次有效"))
def Testcase_BmcSetBootOptionUefi_011():
    """
    Name:       【UEFI】BMC设置未配置为优先引导介质、单次有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、BMC设置"未配置"为优先引导介质、单次有效；
                3、复位单板3次，查看从何种启动介质启动，有结果B；
    Result:     A：从PXE启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert _boot_no_override(SutConfig.Sys.PXE_UEFI_MSG, SutConfig.Env.OS_IP, True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1716", "[TC1716] Testcase_BmcSetBootOptionUefi_012", "【UEFI】BMC设置未配置为优先引导介质、永久有效"))
def Testcase_BmcSetBootOptionUefi_012():
    """
    Name:       【UEFI】BMC设置未配置为优先引导介质、永久有效
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、BMC设置"未配置"为优先引导介质、永久有效；
                3、复位单板3次，查看从何种启动介质启动，有结果B；
    Result:     A：从PXE启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert _boot_no_override(SutConfig.Sys.PXE_UEFI_MSG, SutConfig.Env.OS_IP)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1717", "[TC1717] Testcase_BmcSetBootOptionUefi_013", "【UEFI】BMC设置优先引导介质与BootOverride优先级"))
def Testcase_BmcSetBootOptionUefi_013():
    """
    Name:       【UEFI】BMC设置优先引导介质与BootOverride优先级
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
    Steps:      1、BMC设置优先引导介质为BIOS设置、永久生效，保存；
                2、启动进Setup菜单，随机设置BootOverride一种类型（此类型有启动项）；
                3、F10保存重启，查看从何种启动介质启动，有结果A；
    Result:     A：从BootOverride设置的启动类型启动。
    Remark:
    """
    try:
        BmcWeb.BMC_WEB.set_boot_overwrite('BIOS Settings', once=False)
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.BOOT_SEQUENCE)
        assert SetUpLib.locate_option(Msg.MENU_PXE_BOOT)
        SetUpLib.send_key(Key.F6 * 2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1718", "[TC1718] Testcase_BmcSetBootOptionUefi_014", "【UEFI】BMC设置优先引导介质与BootOverride优先级_遍历测试"))
# def Testcase_BmcSetBootOptionUefi_014():
#     """
#     Name:       【UEFI】BMC设置优先引导介质与BootOverride优先级_遍历测试
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
#     Steps:      1、BMC设置优先引导介质为BIOS设置、永久生效，保存；
#                 2、启动进Setup菜单，随机设置BootOverride一种类型（此类型有启动项）；
#                 3、F10保存重启，查看从何种启动介质启动，有结果A；
#                 4、BMC遍历其他优先引导介质永久生效，重复步骤2~3。
#     Result:     A：从BootOverride设置的启动类型启动。
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


# @core.test_case(("1719", "[TC1719] Testcase_BmcSetBootOptionUefi_015", "【UEFI】BMC设置BIOS启动顺序"))
# def Testcase_BmcSetBootOptionUefi_015():
#     """
#     Name:       【UEFI】BMC设置BIOS启动顺序
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置启动顺序为其他->PXE->硬盘->光盘；
#                 4、BIOS默认启动顺序。
#     Steps:      1、启动进Bootmanager界面，查看四大类启动顺序，有结果A；
#                 2、进Setup菜单Boot界面，查看四大类启动顺序，有结果A；
#                 3、复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：以BMC设置的启动顺序为准；
#                 B：从BMC设置的启动顺序中第一类启动介质启动。
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


# @core.test_case(("1720", "[TC1720] Testcase_BmcSetBootOptionUefi_017", "【UEFI】BMC、BIOS同时设置启动顺序"))
# def Testcase_BmcSetBootOptionUefi_017():
#     """
#     Name:       【UEFI】BMC、BIOS同时设置启动顺序
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
#     Steps:      1、BMC设置启动顺序为Other->PXE->硬盘->DVD，保存；
#                 2、Setup菜单设置启动顺序为DVD->硬盘->PXE->Other，保存；
#                 3、重启进Bootmanager界面，查看四大类启动顺序，有结果A；
#                 4、进Setup菜单Boot界面，查看四大类启动顺序，有结果A；
#                 5、复位单板，查看从何种启动介质启动，有结果B；
#                 6、步骤1、2交换顺序，重复步骤3~5。
#     Result:     A：以BMC设置的启动顺序为准；
#                 B：从BMC设置的启动顺序中第一类启动介质启动。
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


# @core.test_case(("1721", "[TC1721] Testcase_BmcSetBootOptionUefi_019", "【UEFI】BMC同时设置优先引导介质、启动顺序"))
# def Testcase_BmcSetBootOptionUefi_019():
#     """
#     Name:       【UEFI】BMC同时设置优先引导介质、启动顺序
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置PXE为优先引导介质单次或永久有效；
#                 4、BMC设置启动顺序为其他->PXE->硬盘->光盘。
#     Steps:      1、启动进Bootmanager界面，查看四大类启动顺序，有结果A；
#                 2、退出到Frontpage，按Continue，查看从何种启动介质启动，有结果B。
#     Result:     A：启动顺序为PXE->Other->硬盘->DVD；
#                 B：从PXE启动.
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


# @core.test_case(("1722", "[TC1722] Testcase_BmcSetBootOptionUefi_021", "【UEFI】BMC设置启动顺序与BootOverride优先级"))
# def Testcase_BmcSetBootOptionUefi_021():
#     """
#     Name:       【UEFI】BMC设置启动顺序与BootOverride优先级
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
#     Steps:      1、BMC设置启动顺序为Other->PXE->硬盘->DVD，保存；
#                 2、启动进Setup菜单，随机设置BootOverride一种类型（此类型有启动项）；
#                 3、F10保存重启，查看从何种启动介质启动，有结果A；
#     Result:     A：从BootOverride设置的启动类型启动。
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

# Common module, For TC1723, TC1744
def _to_bootmanager(pxe_type_msg):
    try:
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_front_page_icon(Msg.BOOT_MANAGER)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(3)
        SetUpLib.send_key(Key.ESC)
        assert SetUpLib.wait_msg(Msg.BOOT_MANAGER)
        assert SetUpLib.locate_front_page_icon(Msg.HOME_PAGE)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(pxe_type_msg, 300)
        return True
    except Exception as e:
        logging.error(e)
        return False

@core.test_case(("1723", "[TC1723] Testcase_BmcSetBootOptionUefi_023", "【UEFI】BMC设置优先引导介质后从Frontpage选Continue启动"))
def Testcase_BmcSetBootOptionUefi_023():
    """
    Name:       【UEFI】BMC设置优先引导介质后从Frontpage选Continue启动
    Condition:  1、UEFI模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
    Steps:      1、BMC设置优先引导介质为PXE、单次生效，保存；
                2、重启进Frontpage界面到Bootmanager页面后Esc退出，按Continue继续启动，查看从何种启动介质启动，有结果A；
                3、BMC设置优先引导介质为PXE、永久生效，保存；
                4、重启进Frontpage界面到Bootmanager页面后Esc退出，按Continue继续启动，查看从何种启动介质启动，有结果A；
    Result:     A：从BMC设置的优先引导介质启动。
    Remark:
    """
    set_once = [True, False]
    try:
        for set_option in set_once:
            BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=set_option)
            assert _to_bootmanager(SutConfig.Sys.PXE_UEFI_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


# @core.test_case(("1724", "[TC1724] Testcase_BmcSetBootOptionUefi_025", "【UEFI】BMC设置启动顺序、PXE Only优先级测试"))
# def Testcase_BmcSetBootOptionUefi_025():
#     """
#     Name:       【UEFI】BMC设置启动顺序、PXE Only优先级测试
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、PXE服务器未部署；
#                 4、Boot Retry选项已开启；
#                 5、Setup设置PXE Retry Count为99。
#     Steps:      1、BMC设置启动顺序为Other->PXE->硬盘->DVD；
#                 2、单板拔掉Others类启动设备
#                 3、复位单板，查看从何种启动介质启动，有结果A；
#     Result:     A：反复轮询PXE，不会从其它启动设备启动。
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


# @core.test_case(("1725", "[TC1725] Testcase_BmcSetBootOptionUefi_026", "【UEFI】BMC设置DVD启动后进入Bootmanage选择从硬盘启动"))
# def Testcase_BmcSetBootOptionUefi_026():
#     """
#     Name:       【UEFI】BMC设置DVD启动后进入Bootmanage选择从硬盘启动
#     Condition:  1、UEFI模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置光驱为优先引导介质、单次有效；
#     Steps:      1、启动进Frontpage页面，再进入Bootmanage选择从硬盘启动，查看启动情况，有结果A；
#     Result:     A：从硬盘启动，无异常。
#     Remark:     【历史问题】BMC Web配置光驱永久启动，启动时按Del，选择从HDD启动，概率性exception挂死。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1726", "[TC1726] Testcase_BmcSetBootOptionLegacy_001", "【Legacy】BMC设置硬盘为优先引导介质、单次有效"))
# def Testcase_BmcSetBootOptionLegacy_001():
#     """
#     Name:       【Legacy】BMC设置硬盘为优先引导介质、单次有效
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置硬盘为优先引导介质、单次有效；
#                 4、Setup菜单设置启动顺序为Other->PXE->DVD->HDD。
#     Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
#                 2、再次复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：从硬盘启动；
#                 B：从软驱启动。
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


# @core.test_case(("1727", "[TC1727] Testcase_BmcSetBootOptionLegacy_002", "【Legacy】BMC设置硬盘为优先引导介质、永久有效"))
# def Testcase_BmcSetBootOptionLegacy_002():
#     """
#     Name:       【Legacy】BMC设置硬盘为优先引导介质、永久有效
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置硬盘为优先引导介质、永久有效；
#                 4、Setup菜单设置启动顺序为Other->PXE->DVD->HDD。
#     Steps:      1、复位单板3次，查看是否每次都从硬盘启动，有结果A。
#     Result:     A：从硬盘启动。
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


# @core.test_case(("1728", "[TC1728] Testcase_BmcSetBootOptionLegacy_003", "【Legacy】BMC设置DVD为优先引导介质、单次有效"))
# def Testcase_BmcSetBootOptionLegacy_003():
#     """
#     Name:       【Legacy】BMC设置DVD为优先引导介质、单次有效
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置光驱为优先引导介质、单次有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
#                 2、再次复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：从DVD启动；
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


# @core.test_case(("1729", "[TC1729] Testcase_BmcSetBootOptionLegacy_004", "【Legacy】BMC设置DVD为优先引导介质、永久有效"))
# def Testcase_BmcSetBootOptionLegacy_004():
#     """
#     Name:       【Legacy】BMC设置DVD为优先引导介质、永久有效
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置光驱为优先引导介质、永久有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、复位单板3次，查看是否每次都从光驱启动，有结果A。
#     Result:     A：从DVD启动。
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


@core.test_case(("1730", "[TC1730] Testcase_BmcSetBootOptionLegacy_005", "【Legacy】BMC设置PXE为优先引导介质、单次有效"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_005():
    """
    Name:       【Legacy】BMC设置PXE为优先引导介质、单次有效
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、单次有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、再次复位单板，查看从何种启动介质启动，有结果B；
    Result:     A：从PXE启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=True)
        BmcLib.force_reset()
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_LEGACY_MSG, SutConfig.Env.BOOT_DELAY)
        assert SetUpLib.boot_to_default_os(uefi=False)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1731", "[TC1731] Testcase_BmcSetBootOptionLegacy_006", "【Legacy】BMC设置PXE为优先引导介质、永久有效"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_006():
    """
    Name:       【Legacy】BMC设置PXE为优先引导介质、永久有效
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、复位单板3次，查看是否每次都从PXE启动，有结果A。
    Result:     A：从PXE启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=False)
        for i in range(1, 4):
            BmcLib.force_reset()
            assert SetUpLib.wait_boot_msgs(Sys.PXE_LEGACY_MSG), f"No.{i} boot from PXE is fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


# @core.test_case(("1732", "[TC1732] Testcase_BmcSetBootOptionLegacy_007", "【Legacy】BMC设置软驱为优先引导介质、单次有效"))
# def Testcase_BmcSetBootOptionLegacy_007():
#     """
#     Name:       【Legacy】BMC设置软驱为优先引导介质、单次有效
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置软驱/可移动插拔设备为优先引导介质、单次有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
#                 2、再次复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：从软驱启动；
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


# @core.test_case(("1733", "[TC1733] Testcase_BmcSetBootOptionLegacy_008", "【Legacy】BMC设置软驱为优先引导介质、永久有效"))
# def Testcase_BmcSetBootOptionLegacy_008():
#     """
#     Name:       【Legacy】BMC设置软驱为优先引导介质、永久有效
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置软驱/可移动插拔设备为优先引导介质、永久有效；
#                 4、BIOS默认启动顺序。
#     Steps:      1、复位单板3次，查看是否每次都从软驱启动，有结果A。
#     Result:     A：从软驱启动。
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


@core.test_case(("1734", "[TC1734] Testcase_BmcSetBootOptionLegacy_009", "【Legacy】BMC设置BIOS设置为优先引导介质、单次有效"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_009():
    """
    Name:       【Legacy】BMC设置BIOS设置为优先引导介质、单次有效
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置BIOS设置为优先引导介质、单次有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、再次复位单板，查看从何种启动介质启动，有结果B；
    Result:     A：从“BIOS设置”启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('BIOS Settings', once=True)
        assert _boot_os_form_bios(SutConfig.Env.OS_IP_LEGACY)
        BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP_LEGACY, SutConfig.Env.BOOT_DELAY), f"boot from HDD is fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1735", "[TC1735] Testcase_BmcSetBootOptionLegacy_010", "【Legacy】BMC设置BIOS设置为优先引导介质、永久有效"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_010():
    """
    Name:       【Legacy】BMC设置BIOS设置为优先引导介质、永久有效
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置BIOS设置为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、复位单板3次，查看是否每次都从BIOS设置启动，有结果A。
    Result:     A：从“BIOS设置”启动。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('BIOS Settings', once=False)
        for i in range(1, 4):
            assert _boot_os_form_bios(SutConfig.Env.OS_IP_LEGACY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


@core.test_case(("1736", "[TC1736] Testcase_BmcSetBootOptionLegacy_011", "【Legacy】BMC设置未配置为优先引导介质、单次有效"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_011():
    """
    Name:       【Legacy】BMC设置未配置为优先引导介质、单次有效
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、BMC设置"未配置"为优先引导介质、单次有效；
                3、复位单板3次，查看从何种启动介质启动，有结果B；
    Result:     A：从PXE启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert _boot_no_override(SutConfig.Sys.PXE_LEGACY_MSG, SutConfig.Env.OS_IP_LEGACY, True)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1737", "[TC1737] Testcase_BmcSetBootOptionLegacy_012", "【Legacy】BMC设置未配置为优先引导介质、永久有效"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_012():
    """
    Name:       【Legacy】BMC设置未配置为优先引导介质、永久有效
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
                3、BMC设置PXE为优先引导介质、永久有效；
                4、BIOS默认启动顺序。
    Steps:      1、单板上电启动，查看从何种启动介质启动，有结果A；
                2、BMC设置"未配置"为优先引导介质、永久有效；
                3、复位单板3次，查看从何种启动介质启动，有结果B；
    Result:     A：从PXE启动；
                B：从硬盘启动。
    Remark:
    """
    try:
        assert _boot_no_override(SutConfig.Sys.PXE_LEGACY_MSG, SutConfig.Env.OS_IP_LEGACY)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1738", "[TC1738] Testcase_BmcSetBootOptionLegacy_013", "【Legacy】BMC设置优先引导介质与BootOverride优先级"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_013():
    """
    Name:       【Legacy】BMC设置优先引导介质与BootOverride优先级
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
    Steps:      1、BMC设置优先引导介质为BIOS设置、永久生效，保存；
                2、启动进Setup菜单，随机设置BootOverride一种类型（此类型有启动项）；
                3、F10保存重启，查看从何种启动介质启动，有结果A；
    Result:     A：从BootOverride设置的启动类型启动。
    Remark:
    """
    try:
        BmcWeb.BMC_WEB.set_boot_overwrite('BIOS Settings', once=False)
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.enter_menu(Msg.BOOT_SEQUENCE)
        assert SetUpLib.locate_option(Msg.MENU_PXE_BOOT)
        SetUpLib.send_key(Key.F6 * 2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1739", "[TC1739] Testcase_BmcSetBootOptionLegacy_014", "【Legacy】BMC设置优先引导介质与BootOverride优先级_遍历测试"))
# def Testcase_BmcSetBootOptionLegacy_014():
#     """
#     Name:       【Legacy】BMC设置优先引导介质与BootOverride优先级_遍历测试
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
#     Steps:      1、BMC设置优先引导介质为BIOS设置、永久生效，保存；
#                 2、启动进Setup菜单，随机设置BootOverride一种类型（此类型有启动项）；
#                 3、F10保存重启，查看从何种启动介质启动，有结果A；
#                 4、BMC遍历其他优先引导介质永久生效，重复步骤2~3。
#     Result:     A：从BootOverride设置的启动类型启动。
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


# @core.test_case(("1740", "[TC1740] Testcase_BmcSetBootOptionLegacy_015", "【Legacy】BMC设置BIOS启动顺序"))
# def Testcase_BmcSetBootOptionLegacy_015():
#     """
#     Name:       【Legacy】BMC设置BIOS启动顺序
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置启动顺序为其他->PXE->硬盘->光盘；
#                 4、BIOS默认启动顺序。
#     Steps:      1、启动进Bootmanager界面，查看四大类启动顺序，有结果A；
#                 2、进Setup菜单Boot界面，查看四大类启动顺序，有结果A；
#                 3、复位单板，查看从何种启动介质启动，有结果B；
#     Result:     A：以BMC设置的启动顺序为准；
#                 B：从BMC设置的启动顺序中第一类启动介质启动。
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


# @core.test_case(("1741", "[TC1741] Testcase_BmcSetBootOptionLegacy_017", "【Legacy】BMC、BIOS同时设置启动顺序"))
# def Testcase_BmcSetBootOptionLegacy_017():
#     """
#     Name:       【Legacy】BMC、BIOS同时设置启动顺序
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
#     Steps:      1、BMC设置启动顺序为Other->PXE->硬盘->DVD，保存；
#                 2、Setup菜单设置启动顺序为DVD->硬盘->PXE->Other，保存；
#                 3、重启进Bootmanager界面，查看四大类启动顺序，有结果A；
#                 4、进Setup菜单Boot界面，查看四大类启动顺序，有结果A；
#                 5、复位单板，查看从何种启动介质启动，有结果B；
#                 6、步骤1、2交换顺序，重复步骤3~5。
#     Result:     A：以BMC设置的启动顺序为准；
#                 B：从BMC设置的启动顺序中第一类启动介质启动。
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


# @core.test_case(("1742", "[TC1742] Testcase_BmcSetBootOptionLegacy_019", "【Legacy】BMC同时设置优先引导介质、启动顺序"))
# def Testcase_BmcSetBootOptionLegacy_019():
#     """
#     Name:       【Legacy】BMC同时设置优先引导介质、启动顺序
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置PXE为优先引导介质单次或永久有效；
#                 4、BMC设置启动顺序为其他->PXE->硬盘->光盘。
#     Steps:      1、启动进Bootmanager界面，查看四大类启动顺序，有结果A；
#                 2、退出到Frontpage，按Continue，查看从何种启动介质启动，有结果B。
#     Result:     A：启动顺序为PXE->Other->硬盘->DVD；
#                 B：从PXE启动.
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


# @core.test_case(("1743", "[TC1743] Testcase_BmcSetBootOptionLegacy_021", "【Legacy】BMC设置启动顺序与BootOverride优先级"))
# def Testcase_BmcSetBootOptionLegacy_021():
#     """
#     Name:       【Legacy】BMC设置启动顺序与BootOverride优先级
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
#     Steps:      1、BMC设置启动顺序为Other->PXE->硬盘->DVD，保存；
#                 2、启动进Setup菜单，随机设置BootOverride一种类型（此类型有启动项）；
#                 3、F10保存重启，查看从何种启动介质启动，有结果A；
#     Result:     A：从BootOverride设置的启动类型启动。
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


@core.test_case(("1744", "[TC1744] Testcase_BmcSetBootOptionLegacy_023", "【Legacy】BMC设置优先引导介质后从Frontpage选Continue启动"))
@mark_legacy_test
def Testcase_BmcSetBootOptionLegacy_023():
    """
    Name:       【Legacy】BMC设置优先引导介质后从Frontpage选Continue启动
    Condition:  1、Legacy模式；
                2、单板配置HDD、DVD、PXE、Others四大类可启动设备。
    Steps:      1、BMC设置优先引导介质为PXE、单次生效，保存；
                2、重启进Frontpage界面到Bootmanager页面后Esc退出，按Continue继续启动，查看从何种启动介质启动，有结果A；
                3、BMC设置优先引导介质为PXE、永久生效，保存；
                4、重启进Frontpage界面到Bootmanager页面后Esc退出，按Continue继续启动，查看从何种启动介质启动，有结果A；
    Result:     A：从BMC设置的优先引导介质启动。
    Remark:
    """
    set_once = [True, False]
    try:
        for set_option in set_once:
            BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=set_option)
            assert _to_bootmanager(SutConfig.Sys.PXE_LEGACY_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


# @core.test_case(("1745", "[TC1745] Testcase_BmcSetBootOptionLegacy_025", "【Legacy】BMC设置启动顺序、PXE Only优先级测试"))
# def Testcase_BmcSetBootOptionLegacy_025():
#     """
#     Name:       【Legacy】BMC设置启动顺序、PXE Only优先级测试
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、PXE服务器未部署；
#                 4、Setup设置PXE Retry Count为99。
#     Steps:      1、BMC设置启动顺序为Other->PXE->硬盘->DVD；
#                 2、单板拔掉Others类启动设备
#                 3、复位单板，查看从何种启动介质启动，有结果A；
#     Result:     A：反复轮询PXE，不会从其它启动设备启动。
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


# @core.test_case(("1746", "[TC1746] Testcase_BmcSetBootOptionLegacy_026", "【Legacy】BMC设置DVD启动后进入Bootmanage选择从硬盘启动"))
# def Testcase_BmcSetBootOptionLegacy_026():
#     """
#     Name:       【Legacy】BMC设置DVD启动后进入Bootmanage选择从硬盘启动
#     Condition:  1、Legacy模式；
#                 2、单板配置HDD、DVD、PXE、Others四大类可启动设备；
#                 3、BMC设置光驱为优先引导介质、单次有效；
#     Steps:      1、启动进Frontpage页面，再进入Bootmanage选择从硬盘启动，查看启动情况，有结果A；
#     Result:     A：从硬盘启动，无异常。
#     Remark:     【历史问题】BMC Web配置光驱永久启动，启动时按Del，选择从HDD启动，概率性exception挂死。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1747", "[TC1747] Testcase_BmcLogin_001", "BMC用户名设置菜单检查"))
def Testcase_BmcLogin_001():
    """
    Name:       BMC用户名设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，BMC配置界面查看是否存在BMC用户名设置选项及默认值，有结果A；
                2、查看BMC用户名帮助信息，检查用户名设置要求是否正确，有结果B；
    Result:     A：存在BMC用户名设置选项，默认值为Administrator；
                B：BMC用户名设置要求与BMC要求保持一致。
    Remark:     1、用户名以及密码修改规则参考右侧Help信息
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.BMC_CONFIG, Msg.BMC_CONFIG], Key.DOWN, 12)
        assert SetUpLib.get_option_value('BMC User Name', integer=None) == 'Administrator'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    # finally:
    #     BmcLib.clear_cmos()


# @core.test_case(("1748", "[TC1748] Testcase_BmcLogin_002", "设置合法BMC用户名"))
# def Testcase_BmcLogin_002():
#     """
#     Name:       设置合法BMC用户名
#     Condition:  
#     Steps:      1、启动进Setup菜单，BMC配置界面设置合法BMC用户名（满足Help信息要求），检查是否成功，有结果A；
#                 2、设置完成后立即使用新设置的用户名登录BMC Web，检查是否登录成功，有结果B；
#                 3、使用修改之前的用户名登录BMC Web，检查是否登录成功，有结果C。
#     Result:     A：用户名设置成功；
#                 B：新用户名登录成功（用户名设置立即生效）；
#                 C：登录失败。
#     Remark:     1、用户名以及密码修改规则参考右侧Help信息；
#                 2、用户名设置立即生效；
#                 3、若BMC用户名设置不成功，检查BMC Web界面->维护诊断->告警上报->Trap报文通知界面下Trap版本是否为SNMPv3，修改为V2或关闭即可。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1749", "[TC1749] Testcase_BmcLogin_004", "BMC密码设置菜单检查"))
# def Testcase_BmcLogin_004():
#     """
#     Name:       BMC密码设置菜单检查
#     Condition:  
#     Steps:      1、启动进Setup菜单，BMC配置界面查看是否存在BMC密码设置选项，密码是否以明文显示，有结果A；
#                 2、查看BMC密码帮助信息，检查密码设置要求是否正确，有结果B；
#     Result:     A：存在BMC密码设置选项，密码信息非明文显示；
#                 B：BMC密码设置要求与BMC要求保持一致。
#     Remark:     1、用户名以及密码修改规则参考右侧Help信息
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1750", "[TC1750] Testcase_BmcLogin_005", "设置合法BMC密码"))
# def Testcase_BmcLogin_005():
#     """
#     Name:       设置合法BMC密码
#     Condition:  
#     Steps:      1、启动进Setup菜单，BMC配置界面修改BMC密码（满足Help信息要求），检查是否需要校验旧密码，是否明文显示，设置是否成功，有结果A；
#                 2、设置完成后立即使用新设置的密码登录BMC Web，检查是否登录成功，有结果B；
#                 3、使用修改之前的密码登录BMC Web，检查是否登录成功，有结果C；
#                 4、BMC Web检查是否存在设置密码的安全日志，有结果D。
#     Result:     A：密码设置成功，无需校验旧密码，非明文显示；
#                 B：登录成功；
#                 C：登录失败；
#                 D：存在密码设置成功的安全日志记录。
#     Remark:     1、用户名以及密码修改规则参考右侧Help信息；
#                 2、密码设置立即生效。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1751", "[TC1751] Testcase_BmcLogin_009", "同时设置BMC用户名和密码"))
# def Testcase_BmcLogin_009():
#     """
#     Name:       同时设置BMC用户名和密码
#     Condition:  
#     Steps:      1、启动进Setup菜单，BMC配置界面同时设置合法BMC用户名、密码（满足Help信息要求），检查设置是否成功，有结果A；
#                 2、使用新设置的用户名和密码登录BMC Web，检查是否登录成功，有结果B；
#     Result:     A：设置用户名、密码成功；
#                 B：新用户名和密码登录成功。
#     Remark:     1、用户名以及密码修改规则参考右侧Help信息
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1752", "[TC1752] Testcase_BmcLogin_010", "BIOS支持创建UserID为2的BMC用户密码"))
# def Testcase_BmcLogin_010():
#     """
#     Name:       BIOS支持创建UserID为2的BMC用户密码
#     Condition:  1、BMC Web增加一个管理员账户；
#                 2、BMC Web删除UserID为2用户。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置BMC用户名和密码（非原密码），状态和权限选项，检查是否设置成功，有结果A；
#                 2、使用UserID2的用户名密码登录BMC Web，检查是否登录成功，有结果B。
#     Result:     A：设置成功；
#                 B：登录成功。
#     Remark:     1、用户名以及密码修改规则参考右侧Help信息
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1753", "[TC1753] Testcase_NetworkMode_001", "网口模式设置菜单检查"))
def Testcase_NetworkMode_001():
    """
    Name:       网口模式设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，BMC配置界面查看是否提供网口模式设置选项，默认值及可选值，有结果A；
    Result:     A：提供网口模式设置菜单，管理、自适应、OCP1共享、OCP2共享（Dedicated、Auto、OCP1 shared、OCP2 shared）模式可选，默认Dedicated。
    Remark:     1、机架服务器增加PCIe Shared模式；高密服务器增加汇聚模式，减少管理模式。
    """
    network_value = ['Dedicated', 'Auto', 'PCIe Shared', 'Onboard OCP Shared']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, confirm_msg=Msg.BMC_NET_MODE)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BMC_NET_MODE), network_value)
        assert SetUpLib.get_option_value(Msg.BMC_NET_MODE) == network_value[0]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1754", "[TC1754] Testcase_NetworkMode_002", "网口模式联动检查"))
# def Testcase_NetworkMode_002():
#     """
#     Name:       网口模式联动检查
#     Condition:  1、默认配置。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置不同网口模式，检查菜单联动，有结果A；
#                 2、检查Port Select菜单提供的Port口数量，有结果B；
#                 3、设置Vlan ID为Help信息范围内取值，检查能否设置成功，有结果C；
#                 4、设置Vlan ID为Help信息范围外取值，检查能否设置成功，有结果D；
#     Result:     A：Auto模式、共享模式开放Vlan ID、Port Select选项选择，其他模式无此选项；
#                 B：Port口数量与实际网卡的网口数量一致；
#                 C：设置成功，0表示Disabled，其他值表示具体Vlan ID；
#                 D：无法设置成功。
#     Remark:     1、机架服务器增加PCIe Shared模式；高密服务器增加汇聚模式，减少管理模式；
#                 2、高密服务器仅支持一张OCP网卡；
#                 3、PCIe Shared以实际接NCSI线缆的网卡为准。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1755", "[TC1755] Testcase_NetworkMode_003", "Dedicated模式测试"))
# def Testcase_NetworkMode_003():
#     """
#     Name:       Dedicated模式测试
#     Condition:  1、物理串口已连接（防止网络中断）。
#     Steps:      1、启动进Setup菜单，BMC配置界面修改网口模式为Dedicated，保存不退出；
#                 2、网线连接管理网口，检查能否登录BMC，有结果A；
#                 3、BMC Web检查网口模式选项是否正确，有结果B；
#                 4、网线连接非管理网口，检查能否登录BMC，有结果C；
#     Result:     A：登录BMC成功；
#                 B：Web显示与菜单设置一致；
#                 C：无法登录BMC。
#     Remark:     1、高密服务器无此选项。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1756", "[TC1756] Testcase_NetworkMode_004", "Auto模式测试"))
# def Testcase_NetworkMode_004():
#     """
#     Name:       Auto模式测试
#     Condition:  1、物理串口已连接（防止网络中断）；
#                 2、网卡支持NCSI，且NCSI线缆已连接。
#     Steps:      1、启动进Setup菜单，BMC配置界面修改网口模式为Auto，保存不退出；
#                 2、网线连接管理网口，检查能否登录BMC，有结果A；
#                 3、BMC Web检查网口模式选项是否正确，有结果B；
#                 4、遍历其他网口模式（包含管理、OCP Shared、PCIe Shared等），执行步骤2，结果A。
#     Result:     A：登录BMC成功；
#                 B：Web显示与菜单设置一致；
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


# @core.test_case(("1757", "[TC1757] Testcase_NetworkMode_011", "F9不恢复网口模式选项"))
# def Testcase_NetworkMode_011():
#     """
#     Name:       F9不恢复网口模式选项
#     Condition:  1、物理串口已连接（防止网络中断）;
#     Steps:      1、启动进Setup菜单，BMC配置界面修改网口模式，F9检查能否恢复修改前配置，有结果A；
#                 2、网口模式设置为Auto，并设置Vlan ID，F9检查能否恢复修改前配置，有结果A；
#                 3、网口模式设置为Shared模式，并设置Vlan ID及Port口，F9检查能否恢复修改前配置，有结果A；
#     Result:     A：不会恢复为修改前配置。
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


# @core.test_case(("1758", "[TC1758] Testcase_NetworkMode_012", "BMC设置Dedicated模式"))
# def Testcase_NetworkMode_012():
#     """
#     Name:       BMC设置Dedicated模式
#     Condition:  1、物理串口已连接（防止网络中断）;
#                 2、专业网口已接网线。
#     Steps:      1、BMC Web设置网口模式为Dedicated，保存；
#                 2、启动进Setup菜单，BMC配置界面查看网口模式，有结果A。
#     Result:     A：菜单显示与BMC设置一致。
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


# @core.test_case(("1759", "[TC1759] Testcase_NetworkMode_013", "BMC设置Auto模式"))
# def Testcase_NetworkMode_013():
#     """
#     Name:       BMC设置Auto模式
#     Condition:  1、物理串口已连接（防止网络中断）;
#                 2、网口已接网线。
#     Steps:      1、BMC Web设置网口模式为Auto，保存；
#                 2、启动进Setup菜单，BMC配置界面查看网口模式，有结果A。
#     Result:     A：菜单显示与BMC设置一致。
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


# @core.test_case(("1760", "[TC1760] Testcase_NetworkMode_014", "BMC设置PCIe Shared模式"))
# def Testcase_NetworkMode_014():
#     """
#     Name:       BMC设置PCIe Shared模式
#     Condition:  1、物理串口已连接（防止网络中断）;
#                 2、PCIe NCSI Porta 已接网线；
#                 3、PC、BMC网口通过交换机连接，并配置交换机Vlan。
#     Steps:      1、BMC设置网口模式为PCIe Shared模式并设置Port为a，设置Vlan ID为b，保存；
#                 2、启动进Setup菜单，BMC配置界面查看网口模式及Port口，有结果A。
#     Result:     A：菜单显示与BMC设置一致。
#     Remark:     1、机架服务器特有选项；
#                 2、Vlan仅对NCSI网口有效，自动模式时网线需接NCSI网口上；
#                 2、交换机配置access类型的端口接PC，Vlan为a；配置trunk类型的端口接BMC。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1761", "[TC1761] Testcase_NetworkMode_015", "BMC设置OCP Shared模式"))
# def Testcase_NetworkMode_015():
#     """
#     Name:       BMC设置OCP Shared模式
#     Condition:  1、物理串口已连接（防止网络中断）;
#                 2、OCP Porta 已接网线；
#                 3、PC、BMC网口通过交换机连接，并配置交换机Vlan。
#     Steps:      1、BMC设置网口模式为OCP Shared模式并设置Port为a，设置Vlan ID为b，保存；
#                 2、启动进Setup菜单，BMC配置界面查看网口模式及Port口，有结果A。
#     Result:     A：菜单显示与BMC设置一致。
#     Remark:     1、Vlan仅对NCSI网口有效，自动模式时网线需接NCSI网口上；
#                 2、交换机配置access类型的端口接PC，Vlan为a；配置trunk类型的端口接BMC。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1762", "[TC1762] Testcase_NetworkMode_016", "BMC设置Aggregation模式"))
# def Testcase_NetworkMode_016():
#     """
#     Name:       BMC设置Aggregation模式
#     Condition:  1、物理串口已连接（防止网络中断）;
#                 2、汇聚网口已接网线。
#     Steps:      1、BMC Web设置网口模式为Aggregation，保存；
#                 2、启动进Setup菜单，BMC配置界面查看网口模式，有结果A。
#     Result:     A：菜单显示与BMC设置一致。
#     Remark:     1、高密服务器特有选项。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1763", "[TC1763] Testcase_SetBmcIp_001", "BMC IP设置菜单检查"))
# def Testcase_SetBmcIp_001():
#     """
#     Name:       BMC IP设置菜单检查
#     Condition:  
#     Steps:      1、启动进Setup菜单，BMC IP配置界面下检查是否存在IPV4、IPV6设置选项及可选值，有结果A；
#                 2、分别检查IPV4、IPV6动静态设置联动是否合理，有结果B。
#     Result:     A：存在IPV4、IPV6设置开关，Static、DHCP可选；
#                 B：IPV4、IPV6联动合理；设置静态模式时，IP可设置，动态模式时，IP不可设置。
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


# @core.test_case(("1764", "[TC1764] Testcase_SetBmcIp_002", "设置合法静态IPV4"))
# def Testcase_SetBmcIp_002():
#     """
#     Name:       设置合法静态IPV4
#     Condition:  1、IPV4设置静态模式；
#                 2、单板连物理串口（防止网络中断后无法恢复）。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置合法IPV4 IP、掩码及网关；
#                 2、F10保存重启再次进Setup菜单检查是否生效，有结果A；
#                 3、通过设置后的IP登录BMC Web界面，检查能否登录成功，有结果B。
#     Result:     A：IP设置生效；
#                 B：登录成功。
#     Remark:     1、参考IPV4定义规范。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1765", "[TC1765] Testcase_SetBmcIp_003", "设置非法静态IPV4"))
# def Testcase_SetBmcIp_003():
#     """
#     Name:       设置非法静态IPV4
#     Condition:  1、IPV4设置静态模式；
#                 2、单板连物理串口（防止网络中断后无法恢复）。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置IPV4地址为非法值（如空值、非四段、含字母、含特殊字符、数值超过IPV4范围等），检查是否设置成功，有结果A；
#                 2、设置掩码为非法值（如空值、非四段、含字母、含特殊字符、数值超过IPV4范围等），检查是否设置成功，有结果A；
#                 3、设置网关为非法值（如空值、非四段、含字母、含特殊字符、数值超过IPV4范围等），检查是否设置成功，有结果A；
#     Result:     A：设置失败，弹框提示非法输入，地址、掩码、网关保持不变。
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


# @core.test_case(("1766", "[TC1766] Testcase_SetBmcIp_004", "IPV4地址网关合理性检查"))
# def Testcase_SetBmcIp_004():
#     """
#     Name:       IPV4地址网关合理性检查
#     Condition:  1、IPV4设置静态模式；
#                 2、单板连物理串口。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置IPV4地址与网关不匹配，检查能否设置成功，有结果A；
#                 2、F10保存重启再次进入Setup菜单检查设置是否生效，有结果B；
#     Result:     A：设置成功；
#                 B：设置未生效。
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


# @core.test_case(("1767", "[TC1767] Testcase_SetBmcIp_005", "动态获取IPV4"))
# def Testcase_SetBmcIp_005():
#     """
#     Name:       动态获取IPV4
#     Condition:  1、IPV4 DHCP服务器已搭建；
#                 2、IPV4设置动态模式；
#                 3、单板连物理串口。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面下检查是否分配到IPV4地址，掩码、网关是否正确，有结果A；
#                 2、使用动态分配的地址登录BMC Web，检查能否登录成功，有结果B。
#     Result:     A：地址分配成功，掩码、网关正确；
#                 B：登录成功。
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


# @core.test_case(("1768", "[TC1768] Testcase_SetBmcIp_006", "设置合法静态IPV6"))
# def Testcase_SetBmcIp_006():
#     """
#     Name:       设置合法静态IPV6
#     Condition:  1、IPV4可登陆BMC；
#                 2、IPV6设置静态模式；
#                 3、单板连物理串口（防止网络中断后无法恢复）。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置合法IPV6 IP、前缀及网关；
#                 2、F10保存重启再次进Setup菜单检查是否生效，有结果A；
#                 3、通过设置后的IP登录BMC Web界面，检查能否登录成功，有结果B。
#     Result:     A：IP设置生效；
#                 B：登录成功。
#     Remark:     1、参考IPV6定义规范。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1769", "[TC1769] Testcase_SetBmcIp_007", "设置非法静态IPV6"))
# def Testcase_SetBmcIp_007():
#     """
#     Name:       设置非法静态IPV6
#     Condition:  1、IPV4可登陆BMC；
#                 2、IPV6设置静态模式；
#                 3、单板连物理串口（防止网络中断后无法恢复）。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置IPV6地址为非法值（如空值、非八段、含特殊字符、多个双冒号、数值超过IPV6范围等），检查是否设置成功，有结果A；
#                 2、设置前缀为非法值（非0~128范围的其他字符），检查是否设置成功，有结果B；
#                 3、设置网关为非法值（如空值、非八段、含特殊字符、多个双冒号、数值超过IPV6范围、与IPV6地址一致等），检查是否设置成功，有结果A；
#     Result:     A：设置失败，弹框提示非法输入，地址、掩码、网关保持不变；
#                 B：不支持非非0~128范围的其他字符输入。
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


# @core.test_case(("1770", "[TC1770] Testcase_SetBmcIp_008", "IPV6地址网关合理性检查"))
# def Testcase_SetBmcIp_008():
#     """
#     Name:       IPV6地址网关合理性检查
#     Condition:  1、IPV6设置静态模式；
#                 2、单板连物理串口。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置IPV6地址与网关不匹配，检查能否设置成功，有结果A；
#                 2、F10保存重启再次进入Setup菜单检查设置是否生效，有结果B；
#     Result:     A：设置成功；
#                 B：设置未生效。
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


# @core.test_case(("1771", "[TC1771] Testcase_SetBmcIp_009", "动态获取IPV6"))
# def Testcase_SetBmcIp_009():
#     """
#     Name:       动态获取IPV6
#     Condition:  1、IPV6 DHCP服务器已搭建；
#                 2、IPV6设置动态模式；
#                 3、IPV4可登陆BMC；
#                 4、单板连物理串口。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面下检查是否分配到IPV6地址，前缀、网关是否正确，有结果A；
#                 2、使用动态分配的地址登录BMC Web，检查能否登录成功，有结果B。
#     Result:     A：地址分配成功，前缀、网关正确；
#                 B：登录成功。
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


# @core.test_case(("1772", "[TC1772] Testcase_SetBmcIp_010", "接口一致性检查"))
# def Testcase_SetBmcIp_010():
#     """
#     Name:       接口一致性检查
#     Condition:  1、单板连物理串口。
#     Steps:      1、启动进Setup菜单，BMC IP配置界面设置IPV4、IPV6的模式及地址，保存不重启；
#                 2、通过设置的地址登录BMC Web，检查Web下IPV4、IPV6模式及地址是否一致；有结果A；
#                 3、BMC Web设置IPV4、IPV6的模式及地址，保存；
#                 4、重启进Setup菜单，BMC IP配置界面检查IPV4、IPV6的模式及地址是否一致，有结果A。
#     Result:     A：IPV4、IPV6的模式及地址保持一致。
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


@core.test_case(("1773", "[TC1773] Testcase_Ssh_001", "SSH服务选项检查"))
def Testcase_Ssh_001():
    """
    Name:       SSH服务选项检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，BMC配置界面检查是否有BMC Service开关选项，可选值、默认值是否正确，有结果A；
    Result:     A：存在BMC Service选项，Enabled、Disabled可选，默认Enabled。
    Remark:
    """
    opt_val = [Msg.DISABLE, Msg.ENABLE]
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BMC_SERVICE), opt_val)
        assert SetUpLib.get_option_value(Msg.BMC_SERVICE) == opt_val[1]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1774", "[TC1774] Testcase_Ssh_002", "BIOS设置SSH服务"))
# def Testcase_Ssh_002():
#     """
#     Name:       BIOS设置SSH服务
#     Condition:  
#     Steps:      1、启动进Setup菜单，BMC配置界面关闭SSH服务，保存不退出，刷新BMC Web界面检查SSH服务是否同步关闭，SSH登录BMC是否成功，有结果A；
#                 2、开启SSH服务，保存不退出，刷新BMC Web界面检查SSH服务是否同步打开，SSH登录BMC是否成功，有结果B；
#     Result:     A：BMC web同步关闭，SSH登录失败；
#                 B：BMC web同步开启，SSH登录成功；
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


# @core.test_case(("1775", "[TC1775] Testcase_Ssh_003", "BIOS获取SSH服务"))
# def Testcase_Ssh_003():
#     """
#     Name:       BIOS获取SSH服务
#     Condition:  
#     Steps:      1、BMC web界面关闭SSH服务，保存；
#                 2、启动进Setup菜单，BMC配置界面检查SSH服务是否同步关闭，SSH登录BMC是否成功，有结果A；
#                 3、BMC web界面开启SSH服务，保存；
#                 4、启动进Setup菜单，BMC配置界面检查SSH服务是否同步开启，SSH登录BMC是否成功，有结果B；
#     Result:     A：Setup同步关闭，SSH登录失败；
#                 B：Setup同步开启，SSH登录成功；
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


@core.test_case(("1776", "[TC1776] Testcase_SmartCoolingAir_001", "Smart Cooling设置菜单检查_风冷"))
def Testcase_SmartCoolingAir_001():
    """
    Name:       Smart Cooling设置菜单检查_风冷
    Condition:  1、产品支持风冷。
    Steps:      1、启动进Setup菜单，BMC配置界面检查是否存在Smart Cooling选项，可选值、默认值是否正确，有结果A。
    Result:     A：存在Smart Cooling选项，Energy saving mode、Low noise mode、
                High performance mode、Custom mode四种模式可选。
    Remark:     1、支持风冷或液冷由产品决定。
    """
    cooling_mode = ['Energy Saving Mode', 'Low Noise Mode', 'High Performance Mode', 'Custom Mode']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.BMC_SMART_COOLING), cooling_mode)
        assert SetUpLib.get_option_value(Msg.BMC_SMART_COOLING) == cooling_mode[0]
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(("1777", "[TC1777] Testcase_SmartCoolingAir_002", "设置风扇策略为节能模式"))
# def Testcase_SmartCoolingAir_002():
#     """
#     Name:       设置风扇策略为节能模式
#     Condition:  1、产品支持风冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Energy saving mode，保存不退出，观察风扇调速速率，有结果A；
#                 2、BMC Web查看风扇策略显示是否正确，有结果B。
#     Result:     A：风扇调速为Energy saving mode；
#                 B：BMC Web界面显示为Energy saving mode。
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


# @core.test_case(("1778", "[TC1778] Testcase_SmartCoolingAir_003", "设置风扇策略为低噪声模式"))
# def Testcase_SmartCoolingAir_003():
#     """
#     Name:       设置风扇策略为低噪声模式
#     Condition:  1、产品支持风冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Low noise mode，保存不退出，观察风扇调速速率，有结果A；
#                 2、BMC Web查看风扇策略显示是否正确，有结果B。
#     Result:     A：风扇调速为Low noise mode；
#                 B：BMC Web界面显示为Low noise mode。
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


# @core.test_case(("1779", "[TC1779] Testcase_SmartCoolingAir_004", "设置风扇策略为高性能模式"))
# def Testcase_SmartCoolingAir_004():
#     """
#     Name:       设置风扇策略为高性能模式
#     Condition:  1、产品支持风冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为High performance mode，保存不退出，观察风扇调速速率，有结果A；
#                 2、BMC Web查看风扇策略显示是否正确，有结果B。
#     Result:     A：风扇调速为High performance mode；
#                 B：BMC Web界面显示为High performance mode。
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


# @core.test_case(("1780", "[TC1780] Testcase_SmartCoolingAir_005", "自定义模式合理性测试"))
# def Testcase_SmartCoolingAir_005():
#     """
#     Name:       自定义模式合理性测试
#     Condition:  1、产品支持风冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Custom mode，观察菜单联动是否正确，有结果A；
#                 2、设置CPU目标温度值为任意值，检查能否正常设置，有结果B；
#                 3、设置风扇速率1、2、3、4为任意值，检查能否正常设置，有结果C；
#                 4、选择风扇策略为其他模式时，观察菜单联动是否正确，有结果D；
#     Result:     A：选择Custom mode时，开放CPU目标温度、风扇速率1、2、3、4共五个选项可设置；
#                 B：温度仅支持设置规定区间值，非区间范围值不支持输入；
#                 C：风扇速率仅支持设置规定区间值，非区间范围值不支持输入，且1、2、3、4速率值必须递增；
#                 D：选择其他模式时，CPU目标温度、风扇速率1、2、3、4选项均隐藏；
#     Remark:     1、设置值范围及规则参考Help信息，且与BMC显示IDE设置范围一致。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1781", "[TC1781] Testcase_SmartCoolingAir_006", "设置风扇策略为自定义模式"))
# def Testcase_SmartCoolingAir_006():
#     """
#     Name:       设置风扇策略为自定义模式
#     Condition:  1、产品支持风冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Custom mode，设置CPU温度值及风扇速率，保存不退出，观察风扇调速速率，有结果A；
#                 2、BMC Web查看风扇策略显示是否正确，温度及风扇速率值是否与设置一致，有结果B。
#     Result:     A：风扇调速为Custom mode；
#                 B：BMC Web界面显示为Custom mode，数值与设置一致。
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


# @core.test_case(("1782", "[TC1782] Testcase_SmartCoolingAir_007", "BIOS获取调速策略_风冷"))
# def Testcase_SmartCoolingAir_007():
#     """
#     Name:       BIOS获取调速策略_风冷
#     Condition:  1、产品支持风冷。
#     Steps:      1、BMC Web设置风扇策略为Energy saving mode，保存；
#                 2、启动进Setup菜单，BMC配置界面查看风扇策略显示是否正确，有结果A；
#                 3、遍历风冷其他三种模式，重复步骤1~2。
#     Result:     A：显示与BMC Web设置一致。
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


# @core.test_case(("1783", "[TC1783] Testcase_SmartCoolingLiquid_001", "Smart Cooling设置菜单检查_液冷"))
# def Testcase_SmartCoolingLiquid_001():
#     """
#     Name:       Smart Cooling设置菜单检查_液冷
#     Condition:  1、产品支持液冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面检查是否存在Smart Cooling选项，可选值、默认值是否正确，有结果A。
#     Result:     A：存在Smart Cooling选项，Liquid cooling mode、Custom mode两种模式可选。
#     Remark:     1、支持风冷或液冷由产品决定。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1784", "[TC1784] Testcase_SmartCoolingLiquid_002", "设置风扇策略为液冷模式"))
# def Testcase_SmartCoolingLiquid_002():
#     """
#     Name:       设置风扇策略为液冷模式
#     Condition:  1、产品支持液冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Liquid cooling mode，保存不退出，观察风扇调速速率，有结果A；
#                 2、BMC Web查看风扇策略显示是否正确，有结果B。
#     Result:     A：风扇调速为Liquid cooling mode；
#                 B：BMC Web界面显示为Liquid cooling mode。
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


# @core.test_case(("1785", "[TC1785] Testcase_SmartCoolingLiquid_003", "自定义模式合理性测试"))
# def Testcase_SmartCoolingLiquid_003():
#     """
#     Name:       自定义模式合理性测试
#     Condition:  1、产品支持液冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Custom mode，观察菜单联动是否正确，有结果A；
#                 2、设置风扇速率1、2、3、4为任意值，检查能否正常设置，有结果B；
#                 3、选择风扇策略为其他模式时，观察菜单联动是否正确，有结果C；
#     Result:     A：选择Custom mode时，开放风扇速率1、2、3、4共四个选项可设置；
#                 B：风扇速率仅支持设置规定区间值，非区间范围值不支持输入，且1、2、3、4速率值必须递增；
#                 C：选择其他模式时，风扇速率1、2、3、4选项均隐藏；
#     Remark:     1、设置值范围及规则参考Help信息，且与BMC显示IDE设置范围一致。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1786", "[TC1786] Testcase_SmartCoolingLiquid_004", "设置风扇策略为自定义模式"))
# def Testcase_SmartCoolingLiquid_004():
#     """
#     Name:       设置风扇策略为自定义模式
#     Condition:  1、产品支持液冷。
#     Steps:      1、启动进Setup菜单，BMC配置界面设置风扇策略为Custom mode，设置风扇速率，保存不退出，观察风扇调速速率，有结果A；
#                 2、BMC Web查看风扇策略显示是否正确，温度及风扇速率值是否与设置一致，有结果B。
#     Result:     A：风扇调速为Custom mode；
#                 B：BMC Web界面显示为Custom mode，数值与设置一致。
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


# @core.test_case(("1787", "[TC1787] Testcase_SmartCoolingLiquid_005", "BIOS获取调速策略_液冷"))
# def Testcase_SmartCoolingLiquid_005():
#     """
#     Name:       BIOS获取调速策略_液冷
#     Condition:  1、产品支持液冷。
#     Steps:      1、BMC Web设置风扇策略为Liquid cooling mode，保存；
#                 2、启动进Setup菜单，BMC配置界面查看风扇策略显示是否正确，有结果A；
#                 3、遍历液冷其他模式，重复步骤1~2。
#     Result:     A：显示与BMC Web设置一致。
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


@core.test_case(("1788", "[TC1788] Testcase_PowerPolicy_001", "上电策略设置菜单检查"))
def Testcase_PowerPolicy_001():
    """
    Name:       上电策略设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，BMC配置界面检查是否有上电策略选项，默认值及可选值是否正确，有结果A；
    Result:     A：存在上电策略选项，Power On/Power Off/Last State三种可选，默认Power On。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.locate_option([Msg.POWER_POLICY, Msg.VAL_POWER_ON], Key.DOWN)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.POWER_POLICY), [Msg.VAL_POWER_ON, Msg.VAL_POWER_LAST, Msg.VAL_POWER_OFF])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1789", "[TC1789] Testcase_PowerPolicy_005", "BIOS设置上电策略"))
def Testcase_PowerPolicy_005():
    """
    Name:       BIOS设置上电策略
    Condition:
    Steps:      1、启动进Setup菜单，BMC配置界面设置上电策略为Power On，保存不退出；
                2、BMC Web查看上电策略显示是否与设置一致，有结果A；
                3、遍历其他两种上电策略，重复步骤1~2。
    Result:     A：显示与Setup设置一致。
    Remark:
    """
    try:
        # power on by default,
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.get_option_value(Msg.POWER_POLICY) == Msg.VAL_POWER_ON
        assert BmcWeb.BMC_WEB.get_power_policy() == 1, f"{BmcWeb.BMC_WEB.get_power_policy()}"
        assert SetUpLib.set_option_value(Msg.POWER_POLICY, Msg.VAL_POWER_LAST, Key.DOWN, 20, save=True)
        assert SetUpLib.wait_boot_msgs(Msg.LOGO_SHOW)
        assert BmcWeb.BMC_WEB.get_power_policy() == -1, f"{BmcWeb.BMC_WEB.get_power_policy()}"
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.set_option_value(Msg.POWER_POLICY, Msg.VAL_POWER_OFF, Key.DOWN, 20, save=True)
        assert SetUpLib.wait_boot_msgs(Msg.LOGO_SHOW)
        assert BmcWeb.BMC_WEB.get_power_policy() == 0, f"{BmcWeb.BMC_WEB.get_power_policy()}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_power_policy(1)
        BmcLib.clear_cmos()


@core.test_case(("1790", "[TC1790] Testcase_PowerPolicy_006", "BIOS获取上电策略"))
def Testcase_PowerPolicy_006():
    """
    Name:       BIOS获取上电策略
    Condition:
    Steps:      1、BMC Web设置上电策略为Power On，保存；
                2、启动进Setup菜单，BMC配置界面查看上电策略选项是否正确，有结果A；
                3、遍历其他两种上电策略，重复步骤1~2。
    Result:     A：显示与BMC Web设置一致。
    Remark:
    """
    try:
        # power on by default,
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.verify_options([Msg.POWER_POLICY, Msg.VAL_POWER_ON], Key.DOWN)
        assert BmcWeb.BMC_WEB.set_power_policy(-1)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.verify_options([Msg.POWER_POLICY, Msg.VAL_POWER_LAST], Key.DOWN)
        assert BmcWeb.BMC_WEB.set_power_policy(0)
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.verify_options([Msg.POWER_POLICY, Msg.VAL_POWER_OFF], Key.DOWN)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_power_policy(1)
        BmcLib.clear_cmos()


@core.test_case(("1791", "[TC1791] Testcase_BootModeSet_001", "BIOS设置启动模式"))
def Testcase_BootModeSet_001():
    """
    Name:       BIOS设置启动模式
    Condition:
    Steps:      1、启动进Setup菜单，Boot界面设置启动模式为Legacy，F10保存重启；
                2、BMC Web查看启动模式，有结果A；
                3、启动进Setup菜单，Boot界面设置启动模式为UEFI，F10保存重启；
                4、BMC Web查看启动模式，有结果B；
    Result:     A：启动模式为Legacy；
                B：启动模式为UEFI。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.BOOT_TYPE)
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, f"{Msg.LEGACY}Boot", save=True)
        assert SetUpLib.continue_to_page(Msg.BOOT_TYPE)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.LEGACY
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, f"{Msg.UEFI}Boot", save=True)
        assert SetUpLib.wait_boot_msgs(Msg.LOGO_SHOW)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.UEFI
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1792", "[TC1792] Testcase_BootModeSet_002", "BMC设置启动模式"))
def Testcase_BootModeSet_002():
    """
    Name:       BMC设置启动模式
    Condition:
    Steps:      1、BMC Web设置启动模式为UEFI，保存；
                2、启动进Setup菜单，Boot界面查看启动模式，有结果A；
                3、BMC设置BIOS启动模式为Legacy模式；
                4、启动进Setup菜单，Boot界面查看启动模式，有结果B。
    Result:     A：启动模式为UEFI；
                B：启动模式为Legacy。
    Remark:
    """
    try:
        assert BmcLib.set_boot_mode(Msg.UEFI)
        assert SetUpLib.boot_to_page(Msg.BOOT_TYPE)
        assert SetUpLib.verify_options([Msg.BOOT_TYPE, f"{Msg.UEFI}Boot"], Key.DOWN)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.UEFI
        assert BmcLib.set_boot_mode(Msg.LEGACY)
        assert SetUpLib.boot_to_page(Msg.BOOT_TYPE)
        assert SetUpLib.verify_options([Msg.BOOT_TYPE, f"{Msg.LEGACY}Boot"], Key.DOWN)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.LEGACY
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1793", "[TC1793] Testcase_BootModeSet_003", "BMC、BIOS同时设置启动模式"))
def Testcase_BootModeSet_003():
    """
    Name:       BMC、BIOS同时设置启动模式
    Condition:
    Steps:      1、Setup菜单界面下，BMC Web设置启动模式为UEFI，Boot界面设置启动模式为Legacy，F10保存重启；
                2、启动进Setup菜单，Boot界面查看启动模式，BMC Web查看启动模式，有结果A；
                3、Boot界面设置启动模式为UEFI，F10保存退出；
                4、启动进Setup菜单，Boot界面查看启动模式，BMC Web查看启动模式，有结果B；
    Result:     A：启动模式为Legacy；
                B：启动模式为UEFI。
    Remark:
    """
    try:
        assert BmcLib.set_boot_mode(Msg.UEFI, once=False)
        assert SetUpLib.boot_to_page(Msg.BOOT_TYPE)
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, f"{Msg.LEGACY}Boot", save=True)
        assert SetUpLib.continue_to_page(Msg.BOOT_TYPE)
        assert SetUpLib.verify_options([Msg.BOOT_TYPE, f"{Msg.LEGACY}Boot"], Key.DOWN)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.LEGACY
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, f"{Msg.UEFI}Boot", save=True)
        assert SetUpLib.continue_to_page(Msg.BOOT_TYPE)
        assert SetUpLib.verify_options([Msg.BOOT_TYPE, f"{Msg.UEFI}Boot"], Key.DOWN)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.UEFI
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.set_boot_mode(Msg.UEFI, once=False)
        BmcLib.clear_cmos()


@core.test_case(("1794", "[TC1794] Testcase_BootModeSet_004", "BMC设置启动模式后BIOS再设置"))
def Testcase_BootModeSet_004():
    """
    Name:       BMC设置启动模式后BIOS再设置
    Condition:
    Steps:      1、BMC Web设置启动模式为Legacy，启动进Setup菜单，Boot界面查看启动模式，有结果A；
                2、Boot界面设置启动模式为UEFI，F10保存退出；
                3、启动进Setup菜单，Boot界面查看启动模式，BMC Web查看启动模式，有结果B；
    Result:     A：启动模式为Legacy；
                B：启动模式为UEFI。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_setup()
        assert BMC_WEB.set_boot_overwrite(mode="Legacy", once=False)
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.verify_options([Msg.BOOT_TYPE, f"{Msg.LEGACY}Boot"], Key.DOWN)
        assert SetUpLib.set_option_value(Msg.BOOT_TYPE, f"{Msg.UEFI}Boot", save=True)
        assert SetUpLib.wait_boot_msgs(Msg.LOGO_SHOW)
        assert BmcWeb.BMC_WEB.get_boot_info().mode == Msg.UEFI
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.set_boot_mode(Msg.UEFI, once=False)
        BmcLib.clear_cmos()


@core.test_case(("1795", "[TC1795] Testcase_PchTypeReport_001", "PCH型号上报BMC"))
def Testcase_PchTypeReport_001():
    """
    Name:       PCH型号上报BMC
    Condition:
    Steps:      1、启动进Setup菜单，PCH界面检查PCH型号并记录；
                2、BMC Web界面查看PCH型号，是否与Setup菜单一致，有结果A。
    Result:     A：显示PCH型号与Setup菜单一致。
    Remark:
    """
    try:
        pch_ver = BmcWeb.BMC_WEB.product_info().pch
        assert pch_ver == SutConfig.Env.PCH_VERSION, f"{pch_ver}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("1796", "[TC1796] Testcase_PcieMacReport_001", "PCIe卡MAC上报BMC"))
# def Testcase_PcieMacReport_001():
#     """
#     Name:       PCIe卡MAC上报BMC
#     Condition:  1、接PCIe卡；
#                 2、BT通道打开。
#     Steps:      1、启动进OS，BT通道查看PCIe MAC地址是否上报BMC，有结果A；
#                 2、BMC Web查看PCIe网卡信息显示是否正确，有结果B；
#                 3、OS下执行"ip addr show"命令查看PCIe网卡MAC显示，有结果C；
#     Result:     A：PCIe MAC上报BMC；
#                 B：Web显示MAC正确，与BT一致；
#                 C：MAC显示正确，与BT一致。
#     Remark:     1、当前支持MAC读取的卡有：X710、X550、82599、I350、X540、5719、MELLANOX；
#                 2、BT搜索关键字"58 CB"，每个设备上报一条，对应BDF。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1797", "[TC1797] Testcase_PcieMacReport_004", "OCP卡MAC上报BMC"))
# def Testcase_PcieMacReport_004():
#     """
#     Name:       OCP卡MAC上报BMC
#     Condition:  1、满配OCP卡；
#                 2、BT通道打开。
#     Steps:      1、启动进OS，BT通道查看OCP MAC地址是否上报BMC，有结果A；
#                 2、BMC Web查看OCP网卡信息显示是否正确，有结果B；
#                 3、OS下执行"ip addr show"命令查看OCP网卡MAC显示，有结果C；
#     Result:     A：OCP MAC上报BMC；
#                 B：Web显示MAC正确，与BT一致；
#                 C：MAC显示正确，与BT一致。
#     Remark:     1、当前支持MAC读取的卡有：X710、X550、82599、I350、X540、5719、MELLANOX；
#                 2、BT搜索关键字"58 CB"，每个设备上报一条，对应BDF。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1798", "[TC1798] Testcase_PcieMacReport_005", "SR-IOV不影响PCIe网卡MAC上报"))
# def Testcase_PcieMacReport_005():
#     """
#     Name:       SR-IOV不影响PCIe网卡MAC上报
#     Condition:  
#     Steps:      1、启动进Setup菜单，Peripheral配置界面设置PCIe SR-IOV为Disabled，F10保存重启进系统，BMC Web查看PCIe网卡信息显示，有结果A；
#                 2、启动进Setup菜单，Peripheral配置界面设置PCIe SR-IOV为Enabled，F10保存重启进系统，BMC Web查看PCIe网卡信息显示，有结果A；
#     Result:     A：Web显示MAC正确。
#     Remark:     1、当前支持MAC读取的卡有：X710、X550、82599、I350、X540、5719、MELLANOX。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("1799", "[TC1799] Testcase_PcieMacReport_006", "Slot PXE不影响PCIe网卡MAC上报"))
# def Testcase_PcieMacReport_006():
#     """
#     Name:       Slot PXE不影响PCIe网卡MAC上报
#     Condition:  
#     Steps:      1、启动进Setup菜单，PXE配置界面设置Slot PXE为Disabled，F10保存重启进系统，BMC Web查看PCIe网卡信息显示，有结果A；
#                 2、启动进Setup菜单，PXE配置界面设置Slot PXE为Enabled，F10保存重启进系统，BMC Web查看PCIe网卡信息显示，有结果A；
#     Result:     A：Web显示MAC正确。
#     Remark:     1、当前支持MAC读取的卡有：X710、X550、82599、I350、X540、5719、MELLANOX。
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


@core.test_case(("1800", "[TC1800] Testcase_BmcUserId2_001", "默认场景下串口修改BMC用户权限"))
def Testcase_BmcUserId2_001():
    """
    Name:       默认场景下串口修改BMC用户权限
    Condition:  1、串口已连接；
                2、BMC默认用户。
    Steps:      1、启动进入BIOS Setup菜单下的BMC设置界面，通过串口修改BMC用户权限，有结果A。
    Result:     A：选项置灰，无法设置。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert not SetUpLib.locate_option(['BMC User Rights'], Key.DOWN), '选项未置灰，可设置'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("1801", "[TC1801] Testcase_BmcUserId2_002", "默认场景下串口修改BMC用户开关"))
def Testcase_BmcUserId2_002():
    """
    Name:       默认场景下串口修改BMC用户开关
    Condition:  1、串口已连接；
                2、BMC默认用户。
    Steps:      1、启动进入BIOS Setup菜单下的BMC设置界面，通过串口修改BMC用户开关，有结果A。
    Result:     A：选项置灰，无法设置。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert not SetUpLib.locate_option(['BMC User Status'], Key.DOWN), '选项未置灰，可设置'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    # finally:
    #     BmcLib.clear_cmos()


@core.test_case(("1802", "[TC1802] Testcase_WakeOnline_001", "Wake On Line设置菜单检查"))
def Testcase_WakeOnline_001():
    """
    Name:       Wake On Line设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，查看是否存在此选项，可选值及默认值，有结果A。
    Result:     A：存在Wake on PME选项，Enabled、Disabled可选，默认Disabled；
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_MISC_CONFIG, Key.DOWN)
        assert SetUpLib.locate_option([Msg.WAKE_ON_LAN, Msg.DISABLE], Key.UP)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.WAKE_ON_LAN), [Msg.ENABLE, Msg.DISABLE])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("1803", "[TC1803] Testcase_LoadBmcDefault_001", "LoadBmcDefault设置菜单检查"))
def Testcase_LoadBmcDefault_001():
    """
    Name:       LoadBmcDefault设置菜单检查
    Condition:
    Steps:      1、启动进Setup菜单，BMC配置界面查看是否存在LoadBmcDefault选项，有结果A；
    Result:     A：存在LoadBmcDefault选项，且帮助信息显示正确；
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_WDT_CONFIG, Key.DOWN)
        assert SetUpLib.locate_option([Msg.LOAD_BMC_DEFAULT], Key.UP)  # 不支持help信息检查
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("1804", "[TC1804] Testcase_LoadBmcDefault_002", "LoadBmcDefault功能测试"))
# def Testcase_LoadBmcDefault_002():
#     """
#     Name:       LoadBmcDefault功能测试
#     Condition:  1、已知设置还原点指令；
#                 2、BMC已设置还原点；
#                 3、物理串口已连接。
#     Steps:      1、启动进Setup菜单，BMC配置界面修改部分选项（尽可能多修改，如用户名、密码、IP等）；
#                 2、F10保存重启再次进Setup菜单，检查修改是否生效，有结果A；
#                 3、Load BMC Default操作后重启系统再次进Setup菜单，查看修改选项，有结果B。
#     Result:     A：修改选项已生效；
#                 B：BMC相关选项已恢复成还原点时状态值。
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


# @core.test_case(("1805", "[TC1805] Testcase_LoadBmcDefault_003", "LoadBmcDefault不恢复非BMC相关选项"))
# def Testcase_LoadBmcDefault_003():
#     """
#     Name:       LoadBmcDefault不恢复非BMC相关选项
#     Condition:  1、已知设置还原点指令；
#                 2、BMC已设置还原点；
#                 3、物理串口已连接。
#     Steps:      1、启动进Setup菜单，BMC配置界面修改部分选项（尽可能多修改，如用户名、密码、IP等），同时其他界面修改部分非BMC选项；
#                 2、F10保存重启再次进Setup菜单，检查修改是否生效，有结果A；
#                 3、Load BMC Default操作后重启系统再次进Setup菜单，查看修改选项，有结果B。
#     Result:     A：修改选项已生效；
#                 B：BMC相关选项已恢复成还原点时状态值，非BMC相关选项保持不变。
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


# @core.test_case(("1806", "[TC1806] Testcase_LoadBmcDefault_006", "LoadBmcDefault操作日志记录"))
# def Testcase_LoadBmcDefault_006():
#     """
#     Name:       LoadBmcDefault操作日志记录
#     Condition:  1、已知设置还原点指令；
#                 2、BMC已设置还原点；
#                 3、物理串口已连接。
#     Steps:      1、启动进Setup菜单，BMC配置界面修改部分选项（尽可能多修改，如用户名、密码、IP等）；
#                 2、F10保存重启再次进Setup菜单，检查修改是否生效，有结果A；
#                 3、Load BMC Default操作后重启系统再次进Setup菜单，查看修改选项，有结果B；
#                 4、BMC Web查看是否有日志记录，有结果C。
#     Result:     A：修改选项已生效；
#                 B：BMC相关选项已恢复成还原点时状态值；
#                 C：存在BMC恢复默认的操作日志。
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

