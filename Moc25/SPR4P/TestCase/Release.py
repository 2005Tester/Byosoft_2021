import glob
from batf.Common.LogAnalyzer import LogAnalyzer
from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Release Basic Function Test
# TC 900-1000
####################################

P = LogAnalyzer(SutConfig.Env.LOG_DIR)


# 标记Release测试状态，避免重复测试
class TestStatus:
    new_bin_img = None
    old_bin_img = None
    new_hpm_img = None
    old_hpm_img = None

    downgrade_test = None
    registry_old = None
    registry_new = None

    pxe_boot_uefi = None
    pxe_boot_legacy = None

    collect_information = False


def _get_bios_bin_image():
    """获取新旧版本的bin镜像"""
    new_branch = SutConfig.Env.BRANCH_RELEASE
    old_branch = SutConfig.Env.BRANCH_OLD
    if not TestStatus.old_bin_img:
        TestStatus.old_bin_img = Update.get_test_image(old_branch)
    if not TestStatus.new_bin_img:
        TestStatus.new_bin_img = Update.get_test_image(new_branch)
    if os.path.exists(TestStatus.new_bin_img) and os.path.exists(TestStatus.old_bin_img):
        return True


def _get_bios_hpm_image():
    """获取新旧版本的hpm镜像"""
    new_branch = SutConfig.Env.BRANCH_RELEASE
    old_branch = SutConfig.Env.BRANCH_OLD
    if not TestStatus.new_hpm_img:
        new_path_local = os.path.join(SutConfig.Env.BIOS_PATH, new_branch)
        if os.path.exists(new_path_local):
            new_hpm_local = glob.glob(os.path.join(new_path_local, "*.hpm"))
            TestStatus.new_hpm_img = new_hpm_local[0] if new_hpm_local else None
        else:
            logging.error(f"New hpm BIOS path not exists: {new_branch}")
    if not TestStatus.old_hpm_img:
        old_path_local = os.path.join(SutConfig.Env.BIOS_PATH, old_branch)
        if os.path.exists(old_path_local):
            old_hpm_local = glob.glob(os.path.join(old_path_local, "*.hpm"))
            TestStatus.old_hpm_img = old_hpm_local[0] if old_hpm_local else None
        else:
            logging.error(f"Old hpm BIOS path not exists: {old_branch}")
    if os.path.exists(TestStatus.new_hpm_img) and os.path.exists(TestStatus.new_hpm_img):
        return True


def _env_restore():
    """环境恢复"""
    try:
        BmcLib.clear_cmos()
        bios_ver = PlatMisc.match_config_version().BiosVer
        if BmcLib.get_fw_version().BIOS == bios_ver:
            return True
        assert _get_bios_bin_image()
        assert Update.flash_bios_bin_and_init(TestStatus.new_bin_img)
        return True
    except Exception:
        return


acpi_tables = ['apic', 'bdat', 'bert', 'bgrt', 'dmar', 'dsdt', 'erst', 'facp',
               'facs', 'fpdt', 'hest', 'hmat', 'hpet', 'mcfg', 'msct', 'oem1', 'oem2',
               'prmt', 'slit', 'spcr', 'srat', 'ssdm', 'ssdt1', 'ssdt2', 'ssdt3',
               'ssdt4', 'ssdt5', 'ssdt6', 'ssdt7', 'ssdt8', 'ssdt9', 'wddt', 'wsmt']
types = [0, 1, 2, 3, 4, 7, 9, 13, 16, 17, 19, 38, 39, 41, 127]


def _creat_log_folder():
    log_folder_dic = {}
    for caseid in range(923, 935 + 1):
        log_folder = SutConfig.Env.LOG_DIR + f"\\TC{caseid}"
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
            log_folder_dic[caseid] = log_folder
    return log_folder_dic


# 写入文件
def _write_to_file(file_name, content):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)


# 获取TC923 ~ TC935所需要的文件
# TC923  或取新旧版本的CurrentValue、Registry文件
# TC924  或取新旧版本的ACPI表
# TC925  或取新旧版本的SMBIOS信息
# TC926  或取新旧版本的PCIe资源
# TC927  或取新旧版本的CPU Flag信息
# TC928  或取新旧版本的IO Mem信息
# TC929  或取新旧版本的IO port信息
# TC930  或取新旧版本的E820信息
# TC931  或取新旧版本的CPUID信息
# TC932  或取新旧版本的装备包
# TC933  或取新旧版本的定制化选项
# TC934  或取新旧版本的定制化选项默认值
# TC935  配置导入导出测试
def _get_testfile(biosVersion):
    _creat_log_folder()
    assert SetUpLib.boot_to_default_os()
    logging.info("dump registry")
    Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR + f"\\TC923", name=f"Registry_{biosVersion}.json")
    Sut.BMC_RFISH.current_dump(dump_json=True, path=SutConfig.Env.LOG_DIR + f"\\TC923", name=f"CurrentValue_{biosVersion}.json")

    logging.info("dump ACPI table")
    PlatMisc.get_acpi_table_linux(acpi_tables)
    for acpi_table in acpi_tables:
        src_acpi_table = f"/root/acpi_dump/{acpi_table}.dsl"
        dst_acpi_table = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC924", f"{acpi_table}_{biosVersion}.dsl")
        SshLib.sftp_download_file(Sut.OS_SFTP, src_acpi_table, dst_acpi_table)

    logging.info("dump SmBIOS info")
    for type_n in types:
        smbios_type_n = SshLib.execute_command(Sut.OS_SSH, f"dmidecode -t {type_n}")
        dst_smbios_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC925", f"smbios_type{type_n}_{biosVersion}.txt")
        _write_to_file(dst_smbios_file, smbios_type_n)
        if type_n == 0:
            PlatMisc.del_lines_from_file(["Version:", "Release"], dst_smbios_file)

    logging.info("dump CPU Flag info")
    cpu_flag = SshLib.execute_command(Sut.OS_SSH, f"cat /proc/cpuinfo |grep flags | head -n1")
    dst_cpu_flag_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC927", f"cpu_flag_{biosVersion}.txt")
    _write_to_file(dst_cpu_flag_file, cpu_flag)

    logging.info("dump IO Mem info")
    iomem_info = SshLib.execute_command(Sut.OS_SSH, f"cat /proc/iomem")
    dst_iomem_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC928", f"iomem_{biosVersion}.txt")
    _write_to_file(dst_iomem_file, iomem_info)

    logging.info("dump IO ports info")
    ioports_info = SshLib.execute_command(Sut.OS_SSH, f"cat /proc/ioports")
    dst_ioports_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC929", f"ioports_{biosVersion}.txt")
    _write_to_file(dst_ioports_file, ioports_info)

    logging.info("dump e820 info")
    e820_info = SshLib.execute_command(Sut.OS_SSH, f"dmesg |grep -i e820")
    dst_e820_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC930", f"e820_{biosVersion}.txt")
    _write_to_file(dst_e820_file, e820_info)

    logging.info("dump cpuid info")
    cpuid_info = SshLib.execute_command(Sut.OS_SSH, f"cpuid")
    dst_cpuid_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC931", f"cpuid_{biosVersion}.txt")
    _write_to_file(dst_cpuid_file, cpuid_info)

    logging.info("dump 定制化选项默认值")
    assert PlatMisc.linux_tool_ready(SutConfig.Env.UNI_PATH, "Resource/SetupBase/Custom.ini")
    SshLib.execute_command(Sut.OS_SSH, r'cd {};./uniCfg -rf Custom.ini'.format(SutConfig.Env.UNI_PATH))
    src_all_setup_file = f"{SutConfig.Env.UNI_PATH}/uniCfg.ini"
    dst_all_setup_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC934", f"uniCfg_{biosVersion}.ini")
    SshLib.sftp_download_file(Sut.OS_SFTP, src_all_setup_file, dst_all_setup_file)

    logging.info("BMC 导出配置")
    SshLib.execute_command(Sut.BMC_SSH, "ipmcget -t config -d export -v /tmp/Config.xml")
    src_all_setup_file = "/tmp/Config.xml"
    dst_all_setup_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC935", f"Config_{biosVersion}.xml")
    PlatMisc.SshLib.sftp_download_file(Sut.BMC_SFTP, src_all_setup_file, dst_all_setup_file)

    # 需要重启，放在后面
    logging.info("dump PCIe info")
    if not BmcLib.force_reset():
        return
    cpu_resource = SerialLib.cut_log(Sut.BIOS_COM, "CPU Resource Allocation", "START_SOCKET_0_DIMMINFO_TABLE", 10, 120)
    dst_cpu_rsc_file = os.path.join(SutConfig.Env.LOG_DIR + f"\\TC926", f"cpu_resource_{biosVersion}.txt")
    _write_to_file(dst_cpu_rsc_file, cpu_resource)


def _get_all_file():
    try:
        assert _get_bios_bin_image()
        assert Update.flash_bios_bin_and_init(TestStatus.old_bin_img)
        logging.info("dump old version test files")
        _get_testfile(SutConfig.Env.BRANCH_OLD)

        assert Update.flash_bios_bin_and_init(TestStatus.new_bin_img)
        logging.info("dump new version test files")
        _get_testfile(SutConfig.Env.BRANCH_RELEASE)

        TestStatus.collect_information = True
    except Exception as e:
        logging.error(e)
    finally:
        _env_restore()


@core.test_case(("901", "[TC901] Parallel flash", "Check BIOS version under setup and BMC Web"))
def release_parallel_flash_test():
    bios_ver = PlatMisc.match_config_version().BiosVer
    try:
        assert _get_bios_bin_image()
        assert Update.flash_bios_bin_and_init(TestStatus.new_bin_img)
        assert BMC_WEB.bios_version() == bios_ver
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('902', '[TC902] Downgrade flash', "Check BIOS version under setup and BMC Web"))
def release_downgrade_flash_test():
    bios_ver = PlatMisc.match_config_version().BiosVer
    last_version = f"{bios_ver[:-2]}{SutConfig.Env.BRANCH_OLD[-2:]}"  # 2.00. + xx
    try:
        assert _get_bios_bin_image()
        if TestStatus.downgrade_test:
            logging.info("Bios downgrade flash is already verified in other test")
            return core.Status.Pass
        assert Update.flash_bios_bin_and_init(TestStatus.old_bin_img)
        assert BMC_WEB.bios_version() == last_version
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _env_restore()


@core.test_case(("903", "[TC903] ME_Check ME Version and status",
                 "ME version should be match within BIOS bin file, ME Status shoule be normal."))
def release_me_version_status():
    me_ver = PlatMisc.match_config_version().ME
    me_info = ['Oper. Firmware Version\s+{0}'.format(me_ver),
               'Recovery Firmware Version\s+{0}'.format(me_ver),
               'Intel ME Target Image Boot\s+Success']
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu([Msg.ME_CONFIG, "Server ME Configuration"], Key.DOWN, 20, "Oper. Firmware Version")
        assert SetUpLib.verify_info(me_info, 13)
        logging.info("ME Version and status verified.")
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


@core.test_case(('904', '[TC904] HPM升级保持配置不变', "HPM升级BIOS后，原来设置的非默认BIOS设置不变"))
def release_hpm_upgrade_test():
    try:
        assert _get_bios_hpm_image() and _get_bios_bin_image()
        assert Update.flash_bios_bin_and_init(TestStatus.old_bin_img)
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.update_bios_hpm(TestStatus.new_hpm_img)
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        return core.Status.Pass
    except Exception:
        return core.Status.Fail
    finally:
        _env_restore()


@core.test_case(('905', '[TC905] HPM降级保持配置不变', "HPM降级BIOS后，原来设置的非默认BIOS设置不变"))
def release_hpm_downgrade_test():
    try:
        assert _get_bios_hpm_image() and _get_bios_bin_image()
        assert Update.flash_bios_bin_and_init(TestStatus.new_bin_img)
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert Update.update_bios_hpm(TestStatus.old_hpm_img)
        assert SetUpLib.boot_to_default_os()
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        _env_restore()


@core.test_case(('906', '[TC906] POST Logo', 'Check POST Logo.'))
def release_post_logo_check():
    try:
        default_logo = os.path.join(PlatMisc.root_path(), "Resource/Logo/PostLogo.bmp")
        logging.info(f"Post logo: {default_logo}")
        post_logo = PlatMisc.save_logo(name="post_logo")
        if not post_logo:
            logging.info("Post logo is not captured, please confirm the KVM is open as share mode, not private mode")
            return core.Status.Fail
        assert MiscLib.compare_images(default_logo, post_logo)
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


@core.test_case(('907', '[TC907] Check Hotkey', 'Check hotkey info during POST; Verify per hotkey function;'))
def release_post_hotkey_check():
    hotkey_info = [
        (Key.DEL, Msg.HOME_PAGE, "Del"),
        (Key.F11, Msg.F11_CONFIRM, "F11"),
        (Key.F12, Msg.F12_CONFIRM, "F12"),
        (Key.F6, Msg.F6_CONFIRM_UEFI, "F6")
    ]
    try:
        fail_cnt = []
        for key_info in hotkey_info:
            if not SetUpLib.boot_with_hotkey(key=key_info[0], msg=key_info[1]):
                fail_cnt.append(key_info[2])
                if key_info[2] == "F6":
                    assert PlatMisc.is_sp_boot_success()
        assert not fail_cnt, f"Check Hot key failed: {fail_cnt} "
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('908', '[TC908] Check Information', 'Check information during POST.'))
def release_post_info_check():
    cut_log_start = "CPU Resource Allocation"
    boot_time = SutConfig.Env.BOOT_DELAY
    check_point = Msg.OEM_LOG_COMMON + SutConfig.Sys.OEM_LOG_SUT
    try:
        assert BmcLib.force_reset()
        boot_log = SerialLib.cut_log(Sut.BIOS_COM, cut_log_start, Msg.BIOS_BOOT_COMPLETE, boot_time, boot_time)
        assert Msg.BIOS_BOOT_COMPLETE in boot_log, "capture post serial log failed"
        msg_miss = []
        for point in check_point:
            if not re.search(point, boot_log):
                msg_miss.append(point)
        assert not msg_miss, f"Msg missed in post log: {msg_miss}"
        assert PlatMisc.no_error_at_post()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('909', '[TC909] Boot to UEFI OS', 'Normally boot to UEFI OS; Check dmesg without error or fail info.'))
def release_boot_uefi_os():
    try:
        assert BmcLib.set_boot_mode(mode="UEFI", once=False)
        assert BmcLib.force_system_reset()
        assert SetUpLib.continue_to_os_from_bm(Msg.BOOT_OPTION_OS)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY)
        assert not PlatMisc.check_dmesg(Msg.DMESG_WORDS, ignore_list=Msg.DMESG_IGNORE)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('910', '[TC910] Boot to Setup UI', 'Login frontpage with default password required;'))
def release_boot_setup_ui():
    try:
        assert BmcLib.force_reset()
        assert SetUpLib.continue_to_pw_prompt(), "Password is required for Bios Setup Login"
        SetUpLib.send_data_enter(Msg.BIOS_PASSWORD)
        assert SetUpLib.wait_msg(Msg.HOME_PAGE)
        assert SetUpLib.move_to_bios_config()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('911', '[TC911] Boot to boot device list', 'Boot success from DVDROM/HDD/PXE/U-Disk'))
def release_boot_device_list():
    try:
        boot_dev = (("DVD", SutConfig.Sys.BOOT_DVD, Msg.LINUX_GRUB),
                    ("HDD", Msg.BOOT_OPTION_OS, Msg.LINUX_GRUB),
                    ("PXE", SutConfig.Sys.PXE_UEFI_DEV, SutConfig.Sys.PXE_UEFI_MSG),
                    ("USB", SutConfig.Sys.BOOT_USB, Msg.LINUX_GRUB))

        # Check Config
        dev_not_config = [boot_type for boot_type in boot_dev if not boot_type[1]]
        if dev_not_config:
            logging.info(f"Boot Device is not config: {dev_not_config}")
            return core.Status.Skip

        # Verify Config
        assert SetUpLib.boot_to_bootmanager()
        dev_not_found = []
        for boot_type in boot_dev:
            if not SetUpLib.locate_option([boot_type[1]], Key.DOWN, try_counts=12):
                logging.info(f"Boot Device not found in boot manager: {boot_dev[1]}")
                dev_not_found.append(boot_type[0])
        if dev_not_found:
            return core.Status.Skip

        # Verify Boot Capability
        dev_boot_fail = []
        for boot_type in boot_dev:
            if not SetUpLib.enter_menu([boot_type[1]], Key.DOWN, try_counts=12, confirm_msg=boot_type[2]):
                logging.info(f"Device boot failed: {boot_type[0]}")
                dev_boot_fail.append(boot_type[0])
                continue
            if boot_type[0] == "PXE":
                TestStatus.pxe_boot_uefi = True
        assert not dev_boot_fail, f"Device boot failed: {dev_boot_fail}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('912', '[TC912] PXE boot (UEFI)', 'UEFI (IPv4 & IPv6)'))
def release_pxe_boot_test():
    if TestStatus.pxe_boot_uefi:
        return core.Status.Pass
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.locate_option(SutConfig.Sys.PXE_UEFI_DEV)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG)

        # PXE IPV6
        assert SetUpLib.boot_to_page(Msg.PAGE_BOOT)
        assert SetUpLib.set_option_value(Msg.PXE_BOOT_CAPABILITY, Msg.VAL_PXE_CAP[2], save=True)
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.locate_option(SutConfig.Sys.PXE_UEFI_DEV_IPV6)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_UEFI_MSG)
        return core.Status.Pass
    except Exception:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('913', '[TC913] BMC warning info in web', "Check no any warning info"))
def check_bmc_warning():
    try:
        bmc_alarm = BmcLib.bmc_warning_check(ignore=SutConfig.Env.BMC_WARN_IG)
        check_result = bmc_alarm.status
        if check_result is None:
            logging.error("Get BMC warning information failed")
            return core.Status.Skip
        assert check_result
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('914', '[TC914] Load default and setting saving Test', 'BIOS Load default Test'))
def release_set_load_default():
    options_pick = [(Msg.PATH_PRO_CFG, "Hardware Prefetcher", "Enabled", "Disabled"),
                    (Msg.PATH_MEM_CONFIG, "DDR PPR Type", "Soft PPR", "Hard PPR"),
                    ([Msg.SYS_EVENT_LOG], "System Errors", "Enabled", "Disabled")]
    try:
        # Set Option Value
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        for op in options_pick:
            op_path, op_name, op_default, op_set = op
            assert SetUpLib.enter_menu(op_path, Key.DOWN, 15, confirm_msg=op_name)
            assert SetUpLib.locate_option([op_name, op_default], Key.DOWN, 15)
            assert SetUpLib.set_option_value(op_name, op_set, Key.DOWN, save=False)
            assert SetUpLib.back_to_setup_toppage()
        SerialLib.send_keys_with_delay(Sut.BIOS_COM, Key.SAVE_RESET)
        # Check Save
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        for op in options_pick:
            op_path, op_name, op_default, op_set = op
            assert SetUpLib.enter_menu(op_path, Key.DOWN, 15, confirm_msg=op_name)
            assert SetUpLib.get_option_value(op_name, Key.DOWN, 15) == op_set
            assert SetUpLib.back_to_setup_toppage()
        # Check Load Default
        assert SetUpLib.load_default_in_setup()
        for op in options_pick:
            op_path, op_name, op_default, op_set = op
            assert SetUpLib.enter_menu(op_path, Key.DOWN, 15, confirm_msg=op_name)
            assert SetUpLib.get_option_value(op_name, Key.DOWN, 15) == op_default
            assert SetUpLib.back_to_setup_toppage()
        return core.Status.Pass
    except Exception:
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('915', f'[TC915] Warm reset 5 times', 'Warm reset 5 times test'))
def release_warm_reboot(count=5):
    reboot_fail = 0
    try:
        warn_ignore = SutConfig.Env.BMC_WARN_IG
        assert BmcLib.enable_fdmlog_dump()
        tc_dir = os.path.join(SutConfig.Env.LOG_DIR, f"TC915")  # check fdmlog
        dump_dir_b = BmcLib.bmc_dumpinfo(tc_dir, "dump_before", uncom=True)
        fdmlog_b = PlatMisc.read_bmc_dump_log(dump_dir_b, "dump_info/LogDump/fdm_log")

        if SutConfig.Env.PROJECT_NAME == "2288 V7":  # 2P IERR错误可以把TDP限定到225w以下再试试
            assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            assert SetUpLib.enter_menu([Msg.CPU_CONFIG, Msg.ADV_POWER_MGF_CONFIG, Msg.CPU_P_STATE])
            assert SetUpLib.set_option_value("Intel SST-PP", "Level 4", Key.DOWN, save=True)

        assert SetUpLib.boot_to_setup()

        logging.info("Warm reset loops: {0}".format(count))
        for i in range(count):  # warm reboot
            logging.info("Warm reset cycle: {0}".format(i + 1))
            SetUpLib.send_key(Key.CTRL_ALT_DELETE)
            logging.debug("Ctrl + Alt + Del key sent")
            boot_fail = not SetUpLib.continue_to_setup()
            bmc_warning = not BmcLib.bmc_warning_check(warn_ignore).status
            if bmc_warning:
                logging.warning(f"New BMC warning found in test loop: {i}")
            if boot_fail or bmc_warning:
                reboot_fail += 1

        dump_dir_a = BmcLib.bmc_dumpinfo(tc_dir, "dump_after", uncom=True)  # check fdmlog
        fdmlog_a = PlatMisc.read_bmc_dump_log(dump_dir_a, "dump_info/LogDump/fdm_log")
        assert fdmlog_b == fdmlog_a, f"New fdmlog recorded after {count} times warm reset"
        assert not reboot_fail, f"Warm reset fail times: {reboot_fail}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('916', f'[TC916] Cold reset 5 times', 'Cold reset 5 times test'))
def release_cold_reboot(count=5):
    reboot_fail = 0
    try:
        warn_ignore = SutConfig.Env.BMC_WARN_IG
        assert BmcLib.enable_fdmlog_dump()
        tc_dir = os.path.join(SutConfig.Env.LOG_DIR, f"TC916")  # check fdmlog
        dump_dir_b = BmcLib.bmc_dumpinfo(tc_dir, "dump_before", uncom=True)
        fdmlog_b = PlatMisc.read_bmc_dump_log(dump_dir_b, "dump_info/LogDump/fdm_log")

        if SutConfig.Env.PROJECT_NAME == "2288 V7":  # 2P IERR错误可以把TDP限定到225w以下再试试
            SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
            SetUpLib.enter_menu([Msg.CPU_CONFIG, Msg.ADV_POWER_MGF_CONFIG, Msg.CPU_P_STATE])
            SetUpLib.set_option_value("Intel SST-PP", "Level 4", Key.DOWN, save=True)

        assert SetUpLib.boot_to_setup()
        logging.info("Cold reset loops: {0}".format(count))
        for i in range(count):  # cold reboot
            logging.info("DC reset cycle: {0}".format(i + 1))
            cycle_fail = not PlatMisc.dc_cycle()
            bmc_warning = not BmcLib.bmc_warning_check(warn_ignore).status
            if bmc_warning:
                logging.warning(f"New BMC warning found in test loop: {i + 1}")
            if cycle_fail or bmc_warning:
                reboot_fail += 1

        dump_dir_a = BmcLib.bmc_dumpinfo(tc_dir, "dump_after", uncom=True)  # check fdmlog
        fdmlog_a = PlatMisc.read_bmc_dump_log(dump_dir_a, "dump_info/LogDump/fdm_log")
        assert fdmlog_b == fdmlog_a, f"New fdmlog recorded after {count} times cold reset"
        assert not reboot_fail, f"Cold reset fail times: {reboot_fail}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('917', f'[TC917] AC cycle 3 times', 'AC cycle 3 times'))
def release_ac_cycle(count=3):
    reboot_fail = 0
    try:
        warn_ignore = SutConfig.Env.BMC_WARN_IG
        assert BmcLib.enable_fdmlog_dump()
        tc_dir = os.path.join(SutConfig.Env.LOG_DIR, f"TC917")  # check fdmlog
        dump_dir_b = BmcLib.bmc_dumpinfo(tc_dir, "dump_before", uncom=True)
        fdmlog_b = PlatMisc.read_bmc_dump_log(dump_dir_b, "dump_info/LogDump/fdm_log")

        assert SetUpLib.boot_to_setup()
        logging.info("AC cycle loops: {0}".format(count))
        for i in range(count):  # cold reboot
            logging.info("AC cycle: {0}".format(i + 1))
            cycle_fail = not BmcLib.power_ac_cycle(SutConfig.Env.AC_CMD)
            boot_fail = not SetUpLib.boot_to_default_os(reset=False)
            bmc_warning = not BmcLib.bmc_warning_check(warn_ignore).status
            if bmc_warning:
                logging.warning(f"New BMC warning found in test loop: {i + 1}")
            if cycle_fail or boot_fail or bmc_warning:
                reboot_fail += 1

        dump_dir_a = BmcLib.bmc_dumpinfo(tc_dir, "dump_after", uncom=True)  # check fdmlog
        fdmlog_a = PlatMisc.read_bmc_dump_log(dump_dir_a, "dump_info/LogDump/fdm_log")
        assert fdmlog_b == fdmlog_a, f"New fdmlog recorded after {count} times cold reset"
        assert not reboot_fail, f"Cold reset fail times: {reboot_fail}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('918', f'[TC918] Processor/DIMM', f'All processor/DIMM detected in OS and iBMC web'))
def release_processor_dimm_check():
    mem_size_keyword = "Total online memory"
    cpu_type_keyword = "Model name"
    cpu_count_keyword = "Socket"
    try:
        assert SetUpLib.boot_to_default_os()
        cpu_name_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "^{cpu_type_keyword}"')
        cpu_count_cmd = SshLib.execute_command(Sut.OS_SSH, f'lscpu |grep "{cpu_count_keyword}"')
        mem_size_cmd = SshLib.execute_command(Sut.OS_SSH, f'lsmem |grep "{mem_size_keyword}"')
        assert cpu_name_cmd, f"[{cpu_type_keyword}] not found in lscpu"
        assert cpu_count_cmd, f"[{cpu_count_keyword}] not found in lscpu"
        assert mem_size_cmd, f"[{mem_size_keyword}] not found in lsmem"
        cpu_type = "".join(re.findall(f"{cpu_type_keyword}.*:\s*(.+)", cpu_name_cmd))
        cpu_count = "".join(re.findall(f"{cpu_count_keyword}.*:\s*(.+)", cpu_count_cmd))
        mem_size = "".join(re.findall(f"{mem_size_keyword}.*:\s*(.+)G", mem_size_cmd))
        if mem_size_cmd.strip().endswith("T"):
            mem_size = "".join(re.findall(f"{mem_size_keyword}.*:\s*(.+)T", mem_size_cmd))
            assert mem_size, "Fail to get mem size with cmd: 'lsmem'"
            mem_size = f"{int(mem_size) * 1024}"
        check_cpu_os = (SutConfig.Sys.CPU_FULL_NAME == cpu_type)
        check_cpu_count = (int(cpu_count) == SutConfig.Sys.CPU_CNT)
        check_mem_os = (int(mem_size) == SutConfig.Sys.MEM_SIZE)
        assert check_mem_os, f"Check MEM Size fail in OS: {mem_size}"
        assert check_cpu_os, f"Check CPU Name fail in OS: {cpu_type}"
        assert check_cpu_count, f"Check CPU Count fail in OS: {cpu_count}"

        proc_info_web = BMC_WEB.processor_info()
        assert proc_info_web, "Fail to get processor info from web"
        for proc in proc_info_web:
            assert SutConfig.Sys.CPU_FULL_NAME == proc, f"{proc} != {SutConfig.Sys.CPU_FULL_NAME}"
        mem_info_web = BMC_WEB.memory_info()
        dimm_size_all = 0
        for dimm_loc, dimm_info in mem_info_web.items():
            print(dimm_loc, dimm_info)
            dimm_size_str = "".join(re.findall("(\d+)", dimm_info["Size"]))
            assert dimm_size_str, "Empty DIMM Size"
            dimm_size_all += int(dimm_size_str) / 1024
        assert dimm_size_all == SutConfig.Sys.MEM_SIZE, f"Check MEM Size fail in BMC web: {dimm_size_all}G"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('919', '[TC919] Secure Boot default check', 'Default should be disabled.'))
def release_security_boot():
    keys_secure_boot = [Key.RIGHT, Key.DOWN, Key.ENTER]
    secureboot_disable = ['Secure Boot State\s+Disabled']
    try:
        assert SetUpLib.boot_to_setup()
        logging.info("Enter secure boot configuration.")
        SetUpLib.send_keys(keys_secure_boot)
        logging.info("Checking secure boot status")
        assert SetUpLib.verify_info(secureboot_disable, 5)
        logging.info("**Secure boot default status verified.")
        return core.Status.Pass
    except Exception:
        return core.Status.Fail


@core.test_case(('920', '[TC920] Restore BIOS default setting via equipment tool',
                 'Restore BIOS default setting via equipment tool'))
def equip_tool_set_and_restore():
    new_pw = PwdLib.gen_pw(prefix="admin@", digit=4)
    try:
        # 抓取默认logo和bios设置
        origin_logo = PlatMisc.save_logo(path=SutConfig.Env.LOG_DIR, name="origin_logo")
        assert origin_logo, "fail to get origin_logo"
        assert SetUpLib.boot_to_default_os(reset=False)
        default_config = Sut.UNITOOL.read(*BiosCfg.HPM_KEEP)
        # 修改为非默认
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert PwdLib.set_admin_pw_by_unipwd(new_pw, Msg.BIOS_PASSWORD)
        assert PlatMisc.uni_command("-getlogo logo_backup.bmp")  # backup logo
        assert PlatMisc.unilogo_update(name="CustomLogo.bmp")
        # 重启并检查修改结果
        modify_logo = PlatMisc.save_logo(path=SutConfig.Env.LOG_DIR, name="modify_logo")
        assert modify_logo, "fail to get modify_logo"
        assert not MiscLib.compare_images(modify_logo, origin_logo), "Modify logo should be different with origin logo"
        assert SetUpLib.boot_to_default_os(reset=False)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        assert PlatMisc.unipwd_tool(new_pw, cmd="check")
        # 恢复默认
        assert PlatMisc.uni_command("-c")
        logging.info("Unitool load default scuuess")
        assert PwdLib.set_admin_pw_by_unipwd(Msg.BIOS_PW_DEFAULT, new_pw)
        assert PlatMisc.uni_command("-setlogo logo_backup.bmp")  # restore logo
        # 重启并检查恢复默认结果
        restore_logo = PlatMisc.save_logo(path=SutConfig.Env.LOG_DIR, name="restore_logo")
        assert restore_logo, "fail to get restore_logo"
        assert MiscLib.compare_images(restore_logo, origin_logo), "Restore logo should be same with origin logo"
        assert SetUpLib.boot_to_default_os(reset=False, timeout=Env.BOOT_DELAY * 2)
        assert Sut.UNITOOL.check(**default_config)
        assert PlatMisc.unipwd_tool(Msg.BIOS_PW_DEFAULT, cmd="check")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        PwdLib.restore_admin_password()
        PlatMisc.unilogo_update(name="Logo.bmp")


@core.test_case(('921', '[TC921] Testcase_Release_021', 'AC Cycle长时间测试'))
def Testcase_Release_021():
    """
    Name:       AC Cycle长时间测试
    Condition:  1、机架服务器可升级rw版本BMC，通过maint_debug_cli 2P：SshLib ,4P：regwrite 0x391 0x80命令模拟AC掉电实现自动化；
                2、非机架服务器需手工执行至少15次；
    Steps:      1、AC上电，检查单板能否正常启动进OS，得结果A。
                2、检查串口有无异常打印，BMC Web有无异常告警信息，得结果B。
                3、步骤1重复至少100次。
    Result:     A：单板正常进入OS，无挂死、反复重启现象； B：串口无Assert等异常打印，BMC无异常告警信息

    """
    reset_count = 100
    try:
        for i in range(reset_count):
            assert BmcLib.power_ac_cycle(SutConfig.Env.AC_CMD), f"AC fail after test {i + 1} times"
            post_check = PlatMisc.no_error_at_post(reboot=False)
            MiscLib.ping_sut(SutConfig.Env.OS_IP, SutConfig.Env.BOOT_DELAY * 2)
            sel_check = BmcLib.bmc_warning_check(ignore=SutConfig.Env.BMC_WARN_IG)
            assert post_check and sel_check, f"Check result fail: post_check = {post_check}, sel_check={sel_check}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('922', '[TC922] PXE boot (Legacy)', 'Legacy (IPv4 & IPv6)'))
def release_legacy_pxe_boot_test():
    if TestStatus.pxe_boot_legacy:
        return core.Status.Pass
    try:
        assert BmcLib.set_boot_mode("Legacy", once=False)
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.locate_option(SutConfig.Sys.PXE_LEGACY_DEV)
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.wait_msg(SutConfig.Sys.PXE_LEGACY_MSG)
        return core.Status.Pass
    except Exception:
        return core.Status.Fail
    finally:
        BmcLib.set_boot_mode("UEFI", once=False)


@core.test_case(('923', '[TC923] Testcase_Interface_001', '新老版本带外配置文件一致性检查'))
def Testcase_Interface_001():
    """
    Name:       新老版本带外配置文件一致性检查
    Condition:  1、Redfish工具已部署；
    Steps:      1、通过Redfish获取分别获取上一个Release版本和当前版本的CurrentValue、Registry文件。
                2、通过Compare工具对比CurrentValue、Registry文件，检查文件差异部分，有结果A。
    Result:     A：文件差异部分无错误
    """
    try:
        new_registry = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\Registry_{SutConfig.Env.BRANCH_RELEASE}.json"
        old_registry = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\Registry_{SutConfig.Env.BRANCH_OLD}.json"
        new_currentvalue = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\CurrentValue_{SutConfig.Env.BRANCH_RELEASE}.json"
        old_currentvalue = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\CurrentValue_{SutConfig.Env.BRANCH_OLD}.json"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_registry, new_registry)
        assert len(difference) == 0, f"{difference}"
        diff_current = PlatMisc.compare_file(old_currentvalue, new_currentvalue)
        assert len(diff_current) == 0, f"{diff_current}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('924', '[TC924] Testcase_Interface_002', '新老版本ACPI表一致性检查'))
def Testcase_Interface_002():
    """
    Name:       新老版本ACPI表一致性检查
    Condition:  1、已安装产品规划内的Linux系统；
                2、已安装acpidump和iasl；
                3、老BIOS版本已导出所有ACPI表。
    Steps:      1、升级新版本BIOS，启动进OS；apic_2288HV7_016.dat
                2、导出ACPI的数据：使用acpidump导出所有的ACPI表，但这些表都是二进制的 # acpidump > acpi.dat
                3、分离各表格数据，会生成多个数据文件：上面的输出包含了很多个ACPI表，使用acpixtract命令将它们进行分离 # acpixtract -a acpidump.dat
                4、反汇编每个表项，然后可以使用cat命令查看表信息，以facp表项为例： # iasl -d facp.dat，cat apic.dsl
                5、重复步骤4，使用diff命令对比新老BIOS版本的ACPI表项是否一致。
    Result:     A：新老版本BIOS的ACPI表项一致。
    """
    try:
        fail_count = 0
        for table in acpi_tables:
            new_table = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\{table}_{SutConfig.Env.BRANCH_RELEASE}.dsl"
            old_table = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\{table}_{SutConfig.Env.BRANCH_OLD}.dsl"
            if not TestStatus.collect_information:
                _get_all_file()
            difference = PlatMisc.compare_file(old_table, new_table)
            if len(difference) != 0:
                logging.error(f"{difference}")
                fail_count += 1
        if fail_count == 0:
            return core.Status.Pass
        else:
            return core.Status.Fail
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('925', '[TC925] Testcase_Interface_003', '新老版本SMBIOS信息一致性检查'))
def Testcase_Interface_003():
    """
    Name:       新老版本SMBIOS信息一致性检查
    Condition:  1、老BIOS版本已导出SMBIOS信息；
                2、新老BIOS环境一致。
    Steps:      1、升级新版本BIOS，进入OS通过dmidecode命令导出所有的SMBIOS信息；
                2、对比新老版本之间的SMBIOS信息差异，有结果A。
    Result:     A：除版本信息差异，新老版本SMBIOS信息一致，如有其它差异与开发确认无影响。
    """
    try:
        fail_count = 0
        for type_n in types:
            new_smbios = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\smbios_type{type_n}_{SutConfig.Env.BRANCH_RELEASE}.txt"
            old_smbios = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\smbios_type{type_n}_{SutConfig.Env.BRANCH_OLD}.txt"
            if not TestStatus.collect_information:
                _get_all_file()
            difference = PlatMisc.compare_file(old_smbios, new_smbios)
            if len(difference) != 0:
                logging.error(f"{difference}")
                fail_count += 1
        if fail_count == 0:
            return core.Status.Pass
        else:
            return core.Status.Fail
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('926', '[TC926] Testcase_Interface_004', '新老版本PCIe资源一致性检查'))
def Testcase_Interface_004():
    """
    Name:       新老版本PCIe资源一致性检查
    Condition:  1、老BIOS版本已导出PCIe资源；
                2、新老BIOS环境一致
                1、串口搜索信息：CPU Resource Allocation
    Steps:      1、升级新版本BIOS，检查串口中PCIe资源分配静态表，包括MMIO、IO、Bus等资源；
                2、对比新老版本之间的PCIe资源的差异，有结果A。
    Result:     A：新老版本PCIe资源一致，如有其它差异与开发确认无影响。
    """
    try:
        new_cpu_resource = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\cpu_resource_{SutConfig.Env.BRANCH_RELEASE}.txt"
        old_cpu_resource = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\cpu_resource_{SutConfig.Env.BRANCH_OLD}.txt"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_cpu_resource, new_cpu_resource)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('927', '[TC927] Testcase_Interface_005', '新老版本CPU Flag信息一致性检查'))
def Testcase_Interface_005():
    """
    Name:       新老版本CPU Flag信息一致性检查
    Condition:  1、老BIOS版本已导出CPU Flag信息；
                2、新老BIOS环境一致。
    Steps:      1、升级新版本BIOS，进入OS执行cat /proc/cpuinfo |grep flags | head -n1导出一份结果；
                2、对比新老版本之间的CPU Flag差异，有结果A。
    Result:     A：新老版本CPU Flag一致，如有其它差异与开发确认无影响。
    """
    try:
        new_cpu_flag = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\cpu_flag_{SutConfig.Env.BRANCH_RELEASE}.txt"
        old_cpu_flag = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\cpu_flag_{SutConfig.Env.BRANCH_OLD}.txt"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_cpu_flag, new_cpu_flag)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('928', '[TC928] Testcase_Interface_006', '新老版本IO Mem信息一致性检查'))
def Testcase_Interface_006():
    """
    Name:       新老版本IO Mem信息一致性检查
    Condition:  1、老BIOS版本已导出IO Mem信息；
                2、新老BIOS环境一致。
    Steps:      1、升级新版本BIOS，进入OS执行cat /proc/iomem导出一份结果；
                2、对比新老版本之间的iomem差异，有结果A。 3、遍历EFI、Legacy两种模式。
    Result:     A:新老版本iomem一致，如有其它差异与开发确认无影响
    """
    try:
        new_iomem = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\iomem_{SutConfig.Env.BRANCH_RELEASE}.txt"
        old_iomem = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\iomem_{SutConfig.Env.BRANCH_OLD}.txt"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_iomem, new_iomem)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('929', '[TC929] Testcase_Interface_007', '新老版本IO port信息一致性检查'))
def Testcase_Interface_007():
    """
    Name:       新老版本IO port信息一致性检查
    Condition:  1、老BIOS版本已导出ioports信息；
                2、新老BIOS环境一致。
    Steps:      1、升级新版本BIOS，进入OS执行cat /proc/ioports导出一份结果；
                2、对比新老版本之间的ioports差异，有结果A。 3、遍历EFI、Legacy两种模式。
    Result:     A：新老版本ioports一致，如有其它差异与开发确认无影响。
    """
    try:
        new_ioports = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\ioports_{SutConfig.Env.BRANCH_RELEASE}.txt"
        old_ioports = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\ioports_{SutConfig.Env.BRANCH_OLD}.txt"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_ioports, new_ioports)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('930', '[TC930] Testcase_Interface_008', ' 新老版本E820信息一致性检查'))
def Testcase_Interface_008():
    """
    Name:       新老版本E820信息一致性检查
    Condition:  1、老BIOS版本已导出E820信息；
                2、新老BIOS环境一致。
    Steps:      1、升级新版本BIOS，进入OS执行dmesg |grep -i e820导出一份结果；
                2、对比新老版本之间的e820差异，有结果A。
                3、遍历EFI、Legacy两种模式。
    Result:     A：新老版本E820一致，如有其它差异与开发确认无影响。
    """
    try:
        new_e820 = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\e820_{SutConfig.Env.BRANCH_RELEASE}.txt"
        old_e820 = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\e820_{SutConfig.Env.BRANCH_OLD}.txt"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_e820, new_e820)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


@core.test_case(('931', '[TC931] Testcase_Interface_009', ' 新老版本CPUID信息一致性检查'))
def Testcase_Interface_009():
    """
    Name:       新老版本CPUID信息一致性检查
    Condition:  1、老BIOS版本已导出CPUID信息；
                2、新老BIOS环境一致。
                3、CPUID工具已安装
                1、工具路径：\\10.186.48.184\bios测试组工作基线\01 IT服务器项目组\01 V5服务器\LOG-uniBIOS Purley V100R008C20\09 测试工具\CPUID
                2、安装方法：rpm -ivh cpuid-20170122-6.x86_64.rpm
    Steps:      1、升级新版本BIOS，进入OS执行cpuid导出一份结果；
                2、对比新老版本之间的差异，有结果A。
                3、遍历EFI、Legacy两种模式。
    Result:     A：新老版本cpuid一致，如有其它差异与开发确认无影响。
    """
    try:
        new_cpuid = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\cpuid_{SutConfig.Env.BRANCH_RELEASE}.txt"
        old_cpuid = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\cpuid_{SutConfig.Env.BRANCH_OLD}.txt"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_cpuid, new_cpuid)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()


# @core.test_case(('932', '[TC932] Testcase_Interface_010', ' 新老版本装备包一致性检查'))
# def Testcase_Interface_010():
#     """
#     Name:       新老版本装备包一致性检查
#     Condition:  1、9008、A9010两个产品装备打包方式与其他产品不一样，必需执行，其他产品打包方式一样，可适当策略
#     Steps:      1、通过BeyondCompare或其他工具对比新老版本0502装备包，检查装备包中包含的所有文件名称及内容是否发生变化，有结果A
#     Result:     A：文件名称及内容需保持跟上个发生产版本一致，除非有需求或问题单要求变更。
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()
#
# @core.test_case(('933', '[TC933] Testcase_Interface_011', ' 新老版本定制化选项一致性检查'))
# def Testcase_Interface_011():
#     """
#     Name:       新老版本定制化选项一致性检查
#     Condition:  1、已提供支持定制化选项列表
#     Steps:      1、对比新老版本定制化选项列表，检查已有变量描述是否一致，有结果A；
#                 2、检查定制化选项列表中是否已包含版本新增变量的描述，描述是否正确，有结果B；
#     Result:     A：新老版本描述一致；
#                 B：已包含新增变量信息。
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()

@core.test_case(('934', '[TC934] Testcase_Interface_012', ' 新老版本定制化选项默认值一致性检查'))
def Testcase_Interface_012():
    """
    Name:       新老版本定制化选项默认值一致性检查
    Condition:  1、已提供支持定制化选项列表；
                2、生成一份支持定制化选项全集变量ini文件，假定为Custom.ini
                3、默认配置。
    Steps:      1、升级新版本BIOS，进入OS执行./uniCfg -rf Custom.ini导出一份结果；
                2、对比新老版本之间的结果差异，有结果A。
                3、遍历EFI、Legacy两种模式。
    Result:     A：新老版本默认值一致。
    """
    try:
        new_Custom = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\uniCfg_{SutConfig.Env.BRANCH_RELEASE}.ini"
        old_Custom = SutConfig.Env.LOG_DIR + f"\\{var.get('current_test')}\\uniCfg_{SutConfig.Env.BRANCH_OLD}.ini"
        if not TestStatus.collect_information:
            _get_all_file()
        difference = PlatMisc.compare_file(old_Custom, new_Custom)
        assert len(difference) == 0, f"{difference}"
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

# @core.test_case(('935', '[TC935] Testcase_Interface_013', ' 配置导入导出测试'))
# def Testcase_Interface_013():
#     """
#     Name:       配置导入导出测试
#     Condition:  1、BMC web界面导出一份老版本配置；
#     Steps:      1、升级新版本BIOS，进入BMC Web界面导入老版本配置；
#                 2、查看导入情况，有结果A;
#                 3、查看启动情况，有结果B；
#                 4、修改部分选项，保存重启，导出新版本配置，重复步骤1-3。
#     Result:     A：配置导入成功；
#     B: 系统启动成功
#     """
#     try:
#
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()