import os
import re
import filecmp
import logging
from batf import SshLib, MiscLib, var, core
from batf.SutInit import Sut
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Key, Msg, BiosCfg
from TCE.BaseLib import BmcLib, SetUpLib, Update, PlatMisc
from batf.Report import ReportGen
from TCE.TestCase import UpdateBIOS


# Test case ID: 9xx

##########################################
#            Release Test Cases          #
##########################################


def bios_parallel_flash():
    tc = ('900', '[TC900] Parallel flash', "Check BIOS version under setup and iBMC Web")
    result = ReportGen.LogHeaderResult(tc)
    release_branch = var.get("branch")
    try:
        img = Update.get_test_image(SutConfig.Env.LOG_DIR, release_branch, 'debug-build')
        assert Update.update_bios(img)
        assert SetUpLib.update_default_password()
        assert SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail(capture=True)


def me_version_status():
    tc = ('901', '[TC901] ME_Check ME Version and status',
          'ME version should be match within BIOS bin file, ME Status shoule be normal.')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_page(Msg.PAGE_ADVANCED):
        result.log_fail()
        return
    if not SetUpLib.enter_menu(Key.DOWN, ["Server ME Configuration"], 20, "General ME Configuration"):
        result.log_fail()
        return
    me_info = ['Oper. Firmware Version\s+{0}'.format(Msg.ME_VERSION),
               'Recovery Firmware Version\s+{0}'.format(Msg.ME_VERSION),
               'Current State\s+Operational']
    if not SetUpLib.verify_info(me_info, 13):
        result.log_fail()
        return
    logging.info("ME Version and status verified.")
    result.log_pass()
    return True


# 非装备模式BIOS设置装备模式flag, 预期设置不成功.
def equip_mode_flag_check():
    tc = ('902', '[TC902] Equipment mode flag check', '非装备模式BIOS设置装备模式flag, 预期设置不成功.')
    result = ReportGen.LogHeaderResult(tc)
    if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 10):
        BmcLib.force_reset()
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 300):
            result.log_skip()
            return
    res = Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG)
    if res:
        result.log_fail()
        return
    logging.info("Unbale to set equipment mode flag.")
    result.log_pass()
    return True


# 装备模式BIOS version = 5.xx.
def equip_mode_version_check():
    tc = ('903', '[TC903] 装备模式: Equipment mode version check', '装备模式版本号为5.xx.')
    result = ReportGen.LogHeaderResult(tc)
    mfg_version = ['BIOS Revision\s+5.[0-9]{2}']
    if not SetUpLib.boot_to_bios_config():
        result.log_fail(capture=True)
        return
    logging.info("Verify bios version.")
    if not SetUpLib.verify_info(mfg_version, 30):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


# 检查BMC是否记录异常告警信息
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def check_bmc_warning():
    tc = ('907', '[TC907] iBMC warning info in web', "Check no any warning info")
    result = ReportGen.LogHeaderResult(tc)
    check_result = BmcLib.bmc_warning_check().status
    if check_result is None:
        result.log_skip()
        return
    if not check_result:
        result.log_fail()
        return
    result.log_pass()
    return True


# Author: WangQingshan
# 启动到UEFI系统并检查dmesg信息
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def boot_to_uefi_os():
    tc = ('910', '[TC910] Boot to UEFI OS', 'Boot to UEFI OS and check dmesg info')
    result = ReportGen.LogHeaderResult(tc)
    err_ignore = ["XFS .*?: Metadata (?:I/O|CRC) error", "ERST.*? support is initialized", "regulatory.(?:0|db)"]
    try:
        assert SetUpLib.boot_to_bootmanager()
        assert SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, Msg.BIOS_BOOT_COMPLETE)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert not PlatMisc.get_dmesg_keywords(["error", "fail"], err_ignore)
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()


# Author: WangQingshan
# 装备模式BIOS IIO菜单需要显示IOU信息 测试
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def equip_iou_not_hidden():
    tc = ('911', '[TC911] BIOS bin with equipment mode, IOU not hidden', 'BIOS bin with equipment mode, IOU not hidden')
    result = ReportGen.LogHeaderResult(tc)
    iou_info = "IOU\d \(IIO PCIe Port \d\)\s+x(?:16|8|4)"
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_IIO_CONFIG, 10, "CPU 1 Configuration")
        for cpu in range(SutConfig.SysCfg.CPU_CNT):
            assert SetUpLib.enter_menu(Key.DOWN, [f"CPU {cpu + 1} Configuration"], 10, iou_info)
            SetUpLib.send_keys([Key.ESC])
        result.log_pass()
    except AssertionError:
        result.log_fail()


# Author: WangQingshan
# 装备模式BIOS，用装备工具设置选项/密码/Logo并恢复默认测试
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def equip_tool_set_and_restore():
    tc = (
        '912', '[TC912] Restore BIOS default setting via equipment tool',
        'Restore BIOS default setting via equipment tool')
    result = ReportGen.LogHeaderResult(tc)
    try:
        # 抓取默认logo和bios设置
        origin_logo = PlatMisc.save_logo(SutConfig.Env.LOG_DIR, name="origin_logo")
        assert origin_logo
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        default_config = Sut.UNITOOL.read(*BiosCfg.HPM_KEEP)
        # # 修改为非默认
        assert Sut.UNITOOL.write(**BiosCfg.HPM_KEEP)
        assert PlatMisc.unipwd_tool("set", "admin@9001")
        assert PlatMisc.unilogo_update(name="CustomLogo.bmp")
        # 重启并检查修改结果
        modify_logo = PlatMisc.save_logo(SutConfig.Env.LOG_DIR, name="modify_logo")
        assert modify_logo
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(**BiosCfg.HPM_KEEP)
        assert PlatMisc.unipwd_tool("check", "admin@9001")
        # 恢复默认
        assert "Load Default success" in SshLib.execute_command(Sut.OS_SSH, f"cd {SutConfig.Env.UNI_PATH};./unitool -c")
        logging.info("Unitool load default scuuess")
        assert PlatMisc.unipwd_tool("set", Msg.BIOS_PW_DEFAULT)
        assert PlatMisc.unilogo_update(name=os.path.split(origin_logo)[1], path=os.path.split(origin_logo)[0])
        # 重启并检查恢复默认结果
        restore_logo = PlatMisc.save_logo(SutConfig.Env.LOG_DIR, name="restore_logo")
        assert restore_logo
        assert MiscLib.compare_images(origin_logo, restore_logo)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert Sut.UNITOOL.check(**default_config)
        assert PlatMisc.unipwd_tool("check", Msg.BIOS_PW_DEFAULT)
        result.log_pass()
    except AssertionError:
        result.log_fail()
    finally:
        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 600):
            BmcLib.force_reset()
            MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        PlatMisc.unipwd_tool("set", Msg.BIOS_PASSWORD)
        BmcLib.clear_cmos()


# Author: WangQingshan
# 检查启动logo
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
def post_logo_check():
    tc = ('913', '[TC913] POST Logo', 'Check POST Logo.')
    result = ReportGen.LogHeaderResult(tc)
    try:
        default_logo = os.path.abspath(os.path.join(os.path.dirname(__file__), r"..\Tools\Logo\CustomLogo.bmp"))
        logging.info(f"Default logo: {default_logo}")
        post_logo = PlatMisc.save_logo(name="post_logo")
        if not post_logo:
            logging.info("Post logo cat't be captured, please confirm the KVM is open as share mode, not private mode")
            result.log_skip()
            return
        assert MiscLib.compare_images(default_logo, post_logo)
        result.log_pass()
    except AssertionError:
        result.log_fail()


# 1、BIOS正常启动；
# 2、检查KVM界面显示的热键信息是否正确，有结果A。
# A：KVM正确显示热键信息，包括DEL、F6、F11、F12。
@core.test_case(('915', '[TC915] 01 BIOS启动阶段KVM热键显示测试', '支持热键配置'))
def kvm_logo_check():
    try:
        default_logo = os.path.abspath(os.path.join(os.path.dirname(__file__), r"..\Tools\Logo\Key.bmp"))
        logging.info(f"Default logo: {default_logo}")
        key_logo = PlatMisc.save_logo(cut_str=Msg.HOTKEY_PROMPT_DEL, name="key_logo", logo_loc=(0, 0, 243, 78))
        if not key_logo:
            logging.info("Post logo can't be captured, please confirm the KVM is open as share mode, not private mode")
            raise AssertionError
        assert MiscLib.compare_images(default_logo, key_logo)
        return core.Status.Pass
    except AssertionError:
        core.capture_screen()
        return core.Status.Fail


# Author: WangQingshan
# Chipsec工具检查是否有fail或warning
# Precondition: Linux
# OnStart: NA
# OnComplete: NA
def chipsec_test():
    tc = ('914', '[TC914] Chipsec Test', 'The version is scanned by chipsec without warning')
    result = ReportGen.LogHeaderResult(tc)

    tme_en = [[Msg.PROCESSOR_CONFIG], "Total Memory Encryption \(TME\)", "Enabled"]
    sgx_en = [[], "SW Guard Extensions \(SGX\)", "Enabled"]
    uma_base = [[Msg.COMMON_REF_CONFIG], "UMA-Based Clustering", "Disable (All2All)"]
    adddc_en = [[Msg.MEMORY_CONFIG, Msg.MEMORY_RAS_CFG], "ADDDC Sparing", "Disabled"]
    warnning_ignored = [
        "WARNING: chipsec.modules.biosguard",
        "WARNING: chipsec.modules.common.debugenabled",
        "WARNING: chipsec.modules.common.uefi.access_platform",
        "WARNING: chipsec.modules.common.uefi.s3bootscript"]

    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, [Msg.CPU_CONFIG], 15, Msg.PROCESSOR_CONFIG)

        assert SetUpLib.enter_menu(Key.DOWN, uma_base[0], 15, "MMIO High Base")
        assert SetUpLib.set_option_value(uma_base[1], uma_base[2], key=Key.UP)
        SetUpLib.send_keys([Key.ESC] * len(uma_base[0]))

        assert SetUpLib.enter_menu(Key.DOWN, adddc_en[0], 15, "Memory RAS Configuration Setup")
        assert SetUpLib.set_option_value(adddc_en[1], adddc_en[2], key=Key.UP)
        SetUpLib.send_keys([Key.ESC] * len(adddc_en[0]))

        assert SetUpLib.enter_menu(Key.DOWN, tme_en[0], 15, Msg.ACT_CPU_CORES)
        assert SetUpLib.set_option_value(tme_en[1], tme_en[2], key=Key.UP)
        assert SetUpLib.set_option_value(sgx_en[1], sgx_en[2])
        assert SetUpLib.save_without_reset()

        assert SetUpLib.back_to_front_page("Administer Secure Boot")
        SetUpLib.send_key(Key.ENTER)
        assert SetUpLib.enter_menu(Key.UP, ["Secure Boot Factory Options"], 5, "Erase all Secure Boot Settings")
        assert SetUpLib.locate_option(Key.DOWN, ["Restore Secure Boot to Factory Settings"], 3)
        SetUpLib.send_keys([Key.ENTER])
        SetUpLib.send_keys([Key.Y], delay=15)
        SetUpLib.send_keys([Key.ESC])
        assert SetUpLib.locate_option(Key.DOWN, ["Attempt Secure Boot", "\[X\]"], 5)
        SetUpLib.send_keys([Key.ENTER] * 2 + Key.SAVE_RESET)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 600)
        assert SshLib.interaction(Sut.OS_SSH,
                                  [f"cd {SutConfig.Env.CHIPSEC_PATH}\n", "python3 chipsec_main.py > chipsec_log.txt"],
                                  ["", ""])
        chipsec_log = os.path.join(SutConfig.Env.LOG_DIR, "chipsec_log.txt")
        assert SshLib.sftp_download_file(Sut.OS_SFTP, f"{SutConfig.Env.CHIPSEC_PATH}/chipsec_log.txt", chipsec_log)
        assert os.path.exists(chipsec_log)
        with open(chipsec_log) as ch_log:
            fail_cnt = 0
            warn_cnt = 0
            for line in ch_log.readlines():
                if re.search("WARNING: chipsec\.", line, re.I) and not any(ig in line for ig in warnning_ignored):
                    warn_cnt += 1
                    logging.info(line.strip())
                elif re.search("FAILED: chipsec\.", line, re.I):
                    fail_cnt += 1
                    logging.info(line.strip())
        assert (not fail_cnt) and (not warn_cnt), f"Chipsec test: {fail_cnt} failed, {warn_cnt} warnings"
        logging.info("** Chipsec test pass: No any unexpected fail or warning")
        result.log_pass()
    except Exception as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# 已安装产品规划内的Linux系统；
# 2、已安装acpidump和iasl；
# 3、老BIOS版本已导出所有ACPI表。
# Steps:
# 1、升级新版本BIOS，启动进入OS；
# 2、导出ACPI的数据：使用acpidump导出所有的ACPI表，但这些表都是二进制的
# acpidump > acpi.dat
# 3、分离各表格数据，会生成多个数据文件：上面的输出包含了很多个ACPI表，使用acpixtract命令将它们进行分离
# acpixtract -a acpidump.dat
# 4、反汇编每个表项，然后可以使用cat命令查看表信息，以facp表项为例：
# iasl -d facp.dat，cat apic.dsl
# 5、重复步骤4，使用diff命令对比新老BIOS版本的ACPI表项是否一致。
# Results:
# A：新老版本BIOS的ACPI表项一致。

# defined branch name, used below case tc916 - tc919, do not call.
lst_bios = SutConfig.Env.RELEASE_BRANCH
pre_bios = SutConfig.Env.PREVIOUS_BRANCH
err_msg = 'No such file or directory'


# this def used to tc916,
def compare_interface_data(bios_branch, tag, ip=SutConfig.Env.OS_IP, ssh_type=Sut.OS_SSH):
    img = Update.get_test_image(SutConfig.Env.LOG_DIR, bios_branch, 'debug-build')
    dsl_path = os.path.join(SutConfig.Env.LOG_DIR, bios_branch, tag)
    # if not os.path.exists(dsl_path):
    #     os.makedirs(dsl_path)
    try:
        assert Update.update_bios(img), 'update bios failed'
        assert SetUpLib.update_default_password(), 'update bios pwd failed'
        assert SetUpLib.boot_suse_from_bm(), 'boot to suse failed'
        assert MiscLib.ping_sut(ip, 300), 'ping os ip failed'
        if tag == 'acpi':
            if not os.path.exists(dsl_path):
                os.makedirs(dsl_path)
            assert SshLib.execute_command(Sut.OS_SSH, 'acpidump > acpi.dat') is not None, 'msg1 none or cmd1 failed'
            assert SshLib.execute_command(Sut.OS_SSH, 'acpixtract -a acpi.dat') is not None, 'msg2 none or cmd2 failed'
            res_dat = SshLib.execute_command(Sut.OS_SSH, 'ls *.dat')
            if res_dat is not None and err_msg not in res_dat:
                for i in res_dat.split('\n'):
                    if len(i) != 0:
                        assert SshLib.execute_command(Sut.OS_SSH, 'iasl -d {0}'.format(i)), '{0} is blank'.format(i)
            res_dsl = SshLib.execute_command(Sut.OS_SSH, 'ls *.dsl')
            if res_dsl is not None and err_msg not in res_dsl:
                for j in res_dsl.split('\n'):
                    if len(j) != 0:
                        assert SshLib.sftp_download_file(Sut.OS_SFTP, j, os.path.join(dsl_path, j))
        elif tag == 'cpuinfo':
            assert SshLib.execute_command(Sut.OS_SSH, 'cat /proc/cpuinfo |grep flags | head -n1 > {0}.txt'.format(bios_branch + tag)) == ''
        elif tag == 'iomem':
            assert SshLib.execute_command(ssh_type, 'cat /proc/iomem > {0}.txt'.format(bios_branch + tag)) == ''
        elif tag == 'ioports':
            assert SshLib.execute_command(ssh_type, 'cat /proc/ioports > {0}.txt'.format(bios_branch + tag)) == ''
        else:
            logging.info('Unknown tag, break')
            raise Exception
        return dsl_path, True
    except Exception as e:
        logging.error(e)
        return dsl_path, False


@core.test_case(('916', '[TC916] 02 新老版本ACPI表一致性检查', '周边接口基线对比测试'))
def testcase_releaseInterface_002():
    input_tag = 'acpi'
    try:
        logging.info('compare the 2 versions dsl files...')
        # assume the current bios is latest,
        assert filecmp.dircmp(compare_interface_data(pre_bios, input_tag)[0], compare_interface_data(lst_bios, input_tag)[0]), 'ACPI files compare failed'
        logging.info('ACPI files compare pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
    finally:
        SshLib.execute_command(Sut.OS_SSH, 'rm -rf *.dat *.dsl')
        filecmp.clear_cache()
        logging.info('Restore ENV, move suse to first boot option')
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
            UpdateBIOS.update_bios_local()


# Precondition: 1、老BIOS版本已导出CPU Flag信息；# 2、新老BIOS环境一致。
# OnStart: N/A
# Steps:
# 1、升级新版本BIOS，进入OS执行cat /proc/cpuinfo |grep flags | head -n1导出一份结果；
# 2、对比新老版本之间的CPU Flag差异，有结果A.
# A：新老版本CPU  Flag一致，如有其它差异与开发确认无影响。
# Completed: SUSE OS
@core.test_case(('917', '[TC917] 05 新老版本CPU Flag对比测试', '周边接口基线对比测试'))
def testcase_releaseInterface_005():
    tag = 'cpuinfo'
    try:
        logging.info('compare the 2 versions cpuinfo files...')
        # assume the current bios is latest,
        assert compare_interface_data(pre_bios, tag)[1]
        assert compare_interface_data(lst_bios, tag)[1]
        res_cpuinfo = SshLib.execute_command(Sut.OS_SSH, 'diff {0}.txt {1}.txt'.format(pre_bios + tag, lst_bios + tag))
        if res_cpuinfo is not None and err_msg not in res_cpuinfo:
            logging.debug(res_cpuinfo)
        logging.info('CPUINFO files compare pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
    finally:
        # SshLib.execute_command(Sut.OS_SSH, 'rm -rf *{0}.txt'.format(tag))
        logging.info('Restore ENV, move suse to first boot option')
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
            UpdateBIOS.update_bios_local()


# Precondition: 1、老BIOS版本已导出IO Mem信息；# 2、新老BIOS环境一致。
# OnStart: N/A
# Steps:
# 1、升级新版本BIOS，进入OS执行cat /proc/iomem导出一份结果；
# 2、对比新老版本之间的iomem差异，有结果A。
# 3、遍历EFI、Legacy两种模式。  # legacy mode通用
# A：新老版本iomem一致，如有其它差异与开发确认无影响。
# Completed: SUSE OS
@core.test_case(('918', '[TC918] 06 新老版本IO Mem对比测试', '周边接口基线对比测试'))
def testcase_releaseInterface_006():
    tag = 'iomem'
    try:
        logging.info('compare the 2 versions iomem files...')
        # assume the current bios is latest,
        assert compare_interface_data(pre_bios, tag, SutConfig.Env.OS_IP, Sut.OS_SSH)[1]
        assert compare_interface_data(lst_bios, tag, SutConfig.Env.OS_IP, Sut.OS_SSH)[1]
        res_iomem = SshLib.execute_command(Sut.OS_SSH, 'diff {0}.txt {1}.txt'.format(pre_bios + tag, lst_bios + tag))
        if res_iomem is not None and err_msg not in res_iomem:
            logging.debug(res_iomem)
        logging.info('IO MEM files compare pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
    finally:
        # SshLib.execute_command(Sut.OS_SSH, 'rm -rf *{0}.txt'.format(tag))
        logging.info('Restore ENV, move suse to first boot option')
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
            UpdateBIOS.update_bios_local()


# Precondition: 1、老BIOS版本已导出ioports信息；# 2、新老BIOS环境一致。
# OnStart: N/A
# Steps:
# 1、升级新版本BIOS，进入OS执行cat /proc/ioports导出一份结果；
# 2、对比新老版本之间的ioports差异，有结果A。
# 3、遍历EFI、Legacy两种模式。  # legacy mode通用
# A：新老版本ioports一致，如有其它差异与开发确认无影响。
# Completed: SUSE OS
@core.test_case(('919', '[TC919] 07 新老版本IO port对比测试', '周边接口基线对比测试'))
def testcase_releaseInterface_007():
    tag = 'ioports'
    try:
        logging.info('compare the 2 versions ioports files...')
        # assume the current bios is latest,
        assert compare_interface_data(pre_bios, tag, SutConfig.Env.OS_IP, Sut.OS_SSH)[1]
        assert compare_interface_data(lst_bios, tag, SutConfig.Env.OS_IP, Sut.OS_SSH)[1]
        res_ioports = SshLib.execute_command(Sut.OS_SSH, 'diff {0}.txt {1}.txt'.format(pre_bios + tag, lst_bios + tag))
        if res_ioports is not None and err_msg not in res_ioports:
            logging.debug(res_ioports)
        logging.info('IO PORTS files compare pass')
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
    finally:
        # SshLib.execute_command(Sut.OS_SSH, 'rm -rf *{0}.txt'.format(tag))
        logging.info('Restore ENV, move suse to first boot option')
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
            UpdateBIOS.update_bios_local()


# Precondition: EQU BIOS
# OnStart: N/A
# Steps:
# '1、OS下进入装备工具路径， ./uniCfg -w DisableCESMIThrotting: 查看变量设置是否成功，有结果A。
#  A：变量设置成功。
# Completed: SUSE OS
@core.test_case(('920', '[TC920] 01 DisableCESMIThrotting变量检查', '装备测试TU分解用例'))
def testcase_equ_disCEStorm_001():
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config({"DisableCESMIThrotting": 1})
        return core.Status.Pass
    except AssertionError:
        return core.Status.Fail


# 检查新旧版本BIOS的Registry.json文件是否一致
# Precondition: BMC正常登录
# OnStart: NA
# OnComplete: NA
@core.test_case(('908', '[TC908] Compare registry.json', 'Compare registry.json file with previous version'))
def registry_check():
    old_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, SutConfig.Env.PREVIOUS_BRANCH, 'debug-build')
    new_bios = Update.get_test_image(SutConfig.Env.LOG_DIR, SutConfig.Env.RELEASE_BRANCH, 'debug-build')
    try:
        # old branch bios image registry dump
        assert Update.update_bios(old_bios)
        logging.info("dump old registry")
        registry_old = Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Registry_old.json")
        # new branch bios image registry dump
        assert Update.update_bios(new_bios)
        logging.info("dump new registry")
        registry_new = Sut.BMC_RFISH.registry_dump(dump_json=True, path=SutConfig.Env.LOG_DIR, name="Registry_new.json")
        assert registry_old == registry_new, "Check old registry is different from new registry"
        logging.info("Check old registry is same with new registry")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        assert SetUpLib.update_default_password()
        if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
            UpdateBIOS.update_bios_local()

