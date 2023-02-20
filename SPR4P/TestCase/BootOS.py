from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# BootOS Test Case
# TC 2100-2110
####################################


@core.test_case(("2100", "[TC2100] Testcase_OsCompaUefi_005", "【UEFI】BIOS版本升降级OS启动测试"))
def Testcase_OsCompaUefi_005():
    """
    Name:       【UEFI】BIOS版本升降级OS启动测试
    Condition:  1、指定OS已安装。
    Steps:      1、上电从硬盘启动OS，检查OS启动情况，结果A；
                2、回退老版本BIOS，上电检查OS启动情况，结果A；
                3、再升级新版本BIOS，上电检查OS启动情况，结果A。
    Result:     A：OS启动正常。
    Remark:
    """
    branch_vn = [SutConfig.Env.BRANCH_OLD, SutConfig.Env.BRANCH_RELEASE]
    try:
        assert SetUpLib.boot_to_default_os()
        for branch in branch_vn:
            image = Update.get_test_image(branch)
            assert Update.flash_bios_bin_and_init(image)
            assert SetUpLib.boot_to_default_os()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        if BmcLib.get_fw_version().BIOS != SutConfig.Env.BIOS_VER_LATEST:
            img = var.get("biosimage") if var.get("biosimage") else Update.get_test_image("master")
            Update.flash_bios_bin_and_init(img)


@core.test_case(("2101", "[TC2101] Testcase_OsCompaUefi_006", "【UEFI】ACPI规范测试_FACP表"))
def Testcase_OsCompaUefi_006():
    """
    Name:       【UEFI】ACPI规范测试_FACP表
    Condition:
    Steps:      1、OS下使用acpidump工具导出ACPI表信息acpidump > acpi.out；
                2、分离各表格数据，会生成多个数据文件，使用命令acpixtract -a acpidump.out；
                3、反汇编FACP表，使用命令iasl -d facp.dat，然后使用cat命令查看FACP表项信息，有结果A。
    Result:     A：关闭平台时钟：Use Platform Timer为0。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os()
        acpi_data = PlatMisc.get_acpi_table_linux("facp")
        assert re.search("Use Platform Timer(.*): 0", acpi_data), 'Use Platform Timer不为0'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2102", "[TC2102] Testcase_OsCompaLegacy_005", "【Legacy】ACPI规范测试_FACP表"))
@mark_legacy_test
def Testcase_OsCompaLegacy_005():
    """
    Name:       【Legacy】ACPI规范测试_FACP表
    Condition:
    Steps:      1、OS下使用acpidump工具导出ACPI表信息acpidump > acpi.out；
                2、分离各表格数据，会生成多个数据文件，使用命令acpixtract -a acpidump.out；
                3、反汇编FACP表，使用命令iasl -d facp.dat，然后使用cat命令查看FACP表项信息，有结果A。
    Result:     A：关闭平台时钟：Use Platform Timer为0。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_default_os(uefi=False)
        acpi_data = PlatMisc.get_acpi_table_linux("facp", uefi=False)
        assert re.search("Use Platform Timer(.*): 0", acpi_data), 'Use Platform Timer不为0'
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2103", "[TC2103] Testcase_PxeBootUefi_001", "【UEFI】PXE启动测试"))
def Testcase_PxeBootUefi_001():
    """
    Name:       【UEFI】PXE启动测试
    Condition:  1、UEFI模式；
                2、PXE服务器已搭建。
    Steps:      1、BMC Web界面界面设置PXE第一启动，检查PXE启动是否正常，有结果A；
    Result:     A：PXE正常启动进OS。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=True)
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Sys.PXE_UEFI_MSG, pw_prompt=Msg.PW_PROMPT, pw=Msg.BIOS_PASSWORD)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2104", "[TC2104] Testcase_PxeBootUefi_003", "【UEFI】PXE启动长时间测试"))
def Testcase_PxeBootUefi_003():
    """
    Name:       【UEFI】PXE启动长时间测试
    Condition:  1、UEFI模式；
                2、PXE服务器已搭建。
    Steps:      1、BMC Web界面界面设置PXE第一启动，检查PXE启动是否正常，有结果A；
                2、反复上下电10次，检查PXE是否正常，有结果A；
    Result:     A：PXE正常启动进OS。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=False)
        for i in range(1, 11):
            BmcLib.force_reset()
            assert SetUpLib.wait_boot_msgs(Sys.PXE_UEFI_MSG, pw_prompt=Msg.PW_PROMPT, pw=Msg.BIOS_PASSWORD), f"{i}th PXE boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


@core.test_case(("2105", "[TC2105] Testcase_PxeBootLegacy_001", "【Legacy】PXE启动测试"))
@mark_legacy_test
def Testcase_PxeBootLegacy_001():
    """
    Name:       【Legacy】PXE启动测试
    Condition:  1、Legacy模式；
                2、PXE服务器已搭建。
    Steps:      1、BMC Web界面设置PXE第一启动，检查PXE启动是否正常，有结果A；
    Result:     A：PXE正常启动进OS。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=True)
        BmcLib.force_reset()
        assert SetUpLib.wait_boot_msgs(Sys.PXE_LEGACY_MSG, pw_prompt=Msg.PW_PROMPT, pw=Msg.BIOS_PASSWORD)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(("2106", "[TC2106] Testcase_PxeBootLegacy_003", "【Legacy】PXE启动长时间测试"))
@mark_legacy_test
def Testcase_PxeBootLegacy_003():
    """
    Name:       【Legacy】PXE启动长时间测试
    Condition:  1、Legacy模式；
                2、PXE服务器已搭建。
    Steps:      1、BMC Web界面设置PXE第一启动，检查PXE启动是否正常，有结果A；
                2、反复上下电10次，检查PXE是否正常，有结果A；
    Result:     A：PXE正常启动进OS。
    Remark:
    """
    try:
        assert BmcWeb.BMC_WEB.set_boot_overwrite('PXE', once=False)
        for i in range(1, 11):
            BmcLib.force_reset()
            assert SetUpLib.wait_boot_msgs(Sys.PXE_LEGACY_MSG, pw_prompt=Msg.PW_PROMPT, pw=Msg.BIOS_PASSWORD), f"{i}th PXE boot fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcWeb.BMC_WEB.set_boot_overwrite('No Override', once=False)


@core.test_case(("2107", "Testcase_PxeBootUefi_006", "【UEFI】反复修改网卡MAC PXE启动测试"))
def Testcase_PxeBootUefi_006():
    """
    Name:       【UEFI】反复修改网卡MAC PXE启动测试
    Condition:  1、UEFI模式；
                2、PXE服务器已搭建
    Steps:      1、启动进OS通过工具修改网卡MAC地址，
                2、PowerCycle启动检查PXE启动情况，有结果A；
                3、重复1~2步骤300次，检查PXE启动情况，有结果A。
    Result:     A：PXE正常启动进OS。
    """
    # Generate MAC address
    boot_success = 0
    try:
        for i in range(0,3):
            for j in range(0,100):
                mac = "4cf55b38"
                if i // 10 == 0:
                    mac = mac + '0' + str(i)
                else:
                    mac = mac + str(i)
                if j // 10 == 0:
                    mac = mac + '0' + str(j)
                else:
                    mac = mac + str(j)
                assert SetUpLib.boot_to_default_os(), "boot to OS fail"
                assert PlatMisc.linux_tool_ready("/usr/bin/eeupdate64e", "Resource/EthTools/eeupdate64e")
                logging.info("modify MAC")
                SshLib.execute_command(Sut.OS_SSH,f"eeupdate64e /NIC=2 /MAC={mac}")
                assert SetUpLib.boot_to_bootmanager()
                assert SetUpLib.locate_option(SutConfig.Sys.PXE_UEFI_DEV, refresh=True), f"{boot_success}th times find PXE Boot devices fail"
                SetUpLib.send_key(Key.ENTER)
                assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG),f"{boot_success}th times PXE Boot fail"
                boot_success = boot_success + 1
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2108", "连接PXE环境检测", "连接PXE环境检测"))
def Testcase_Connect_PXE():
    """
    Name:       连接PXE环境检测
    Condition:  1、网卡连接PXE环境；
    Steps:      1.  启动到setup下，pxe timeout control设置为disabled，保存重启；
                2.  按F12从pxe启动，结果A；
                3. 遍历pxe timeout control的所有设置，保存重启，按F12， pxe启动，结果A；
    Result:     A：正常启动到pxe环境。
    """
    try:
        pxe_success = SutConfig.Sys.PXE_UEFI_MSG
        pxe_timeout = "Server response timeout."
        for pxe_time_control in Msg.VAL_PXE_TIMEOUT_CONTROL:
            assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
            assert SetUpLib.set_option_value(Msg.PXE_TIMEOUT_CONTROL, pxe_time_control, save=True)
            assert SetUpLib.continue_boot_with_hotkey(Key.F12, msg=Msg.F12_CONFIRM), f"set Pxe Timeout Control: {pxe_time_control} pxe boot fail"
            if pxe_time_control.isdigit():
                assert SetUpLib.wait_msg(msg=f"{pxe_success}|{pxe_timeout}", timeout=int(pxe_time_control)*60+1)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2109", "redfish修改检测", "redfish修改检测"))
def Testcase_Redfish_Check_PxeTimeOutControl():
    """
    Name:       redfish修改检测
    Condition:
    Steps:      1.  通过redfish修改pxe timeout control， 结果A；
                2.  遍历pxe timeout control所有选项值，结果A；
    Result:     A：成功修改pxe timeout control设置。
    """
    try:
        for pxe_time_control in Msg.VAL_PXE_TIMEOUT_CONTROL:
            assert Sut.BMC_RFISH.set_bios_option(**{"PxeTimeoutRetryCtrl": pxe_time_control}).result, f"redfish set fail"
            assert BmcLib.force_reset()
            assert SetUpLib.wait_boot_msgs(Msg.BIOS_BOOT_COMPLETE)
            assert Sut.BMC_RFISH.read_bios_option("PxeTimeoutRetryCtrl").get("PxeTimeoutRetryCtrl") \
                   == pxe_time_control, f"redfish check fail"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(("2110", "PXE boot 异常退出后检查网口", "PXE boot 异常退出后检查网口"))
def Testcase_Check_PxePort():
    """
    Name:       PXE boot 异常退出后检查网口
    Condition:
    Steps:      1. PXE boot， 结果A；
                2. 在PXE boot 成功的界面，手动退回到bootmanager，检查网口，有结果B；
    Result:     A：PXE boot 成功。
                B: 网口数量正确
    """
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.locate_option(r'UEFI PXEv4:', order=Sys.NETWORK_PORT, exact=False, refresh=True)
        assert SetUpLib.locate_option(SutConfig.Sys.PXE_UEFI_DEV), f" find PXE Boot devices fail"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG)
        SetUpLib.send_key("c")
        SetUpLib.wait_msg("grub>")
        SetUpLib.send_key("exit")
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.locate_option(r'UEFI PXEv4:', order=Sys.NETWORK_PORT, exact=False)
        assert SetUpLib.locate_option(SutConfig.Sys.PXE_UEFI_DEV), f" find PXE Boot devices fail"
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()





