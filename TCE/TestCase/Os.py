import logging, os
from batf import SerialLib, SshLib, MiscLib, core
from batf.SutInit import Sut
from TCE.Config import SutConfig
from TCE.Config.PlatConfig import Key, Msg, BiosCfg
from TCE.BaseLib import SetUpLib, PlatMisc, BmcLib
from batf.Report import ReportGen

# Test case ID: TC300-TC320

##########################################
#         OS and Boot Test Cases         #
##########################################

# function Module : 開啓全打印重啓后，在串口中查找str_flag
def EquipmentModeFlag_ser_log(path,str_flag):
    with open(path, 'r') as r:
        lines = [line.strip('\n') for line in r.readlines() if line.strip()]    #去掉空行和換行符
        if str_flag in lines:
            logging.info("**{} is found ".format(str_flag))
            return True
        else:
            return False


# Boot to SUSE Linux from boot manager
def boot_to_suse():
    tc = ('300', '[TC300] Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    if not SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, Msg.SUSE_GRUB):
        result.log_fail()
        return
    # if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
    #     result.log_fail()
    #     return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


# Boot to SUSE Linux from boot manager
def boot_to_suse_mfg():
    tc = ('301', '[TC301] 装备模式:Boot to UEFI SUSE Linux', 'Boot to UEFI SUSE Linux in Manufacture mode')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.boot_to_bootmanager():
        result.log_fail()
        return
    msg = "Welcome to GRUB"
    if not SetUpLib.enter_menu(Key.DOWN, Msg.BOOT_OPTION_SUSE, 20, msg):
        result.log_fail()
        return
    # if not SerialLib.is_msg_present(Sut.BIOS_COM, Msg.BIOS_BOOT_COMPLETE):
    #     result.log_fail()
    #     return
    logging.info("OS Boot Successful")
    result.log_pass()
    return True


def move_suse_to_first():
    tc = ('302', '[TC302] Move UEFI SUSE Linux to first boot option', 'Move UEFI SUSE Linux to first boot option')
    result = ReportGen.LogHeaderResult(tc)
    if not SetUpLib.move_boot_option_up(Msg.BOOT_OPTION_SUSE, 5):
        result.log_fail(capture=True)
        return
    result.log_pass()
    return True


# Author: Fubaolin
# 多次执行装备模式脚本测试
# Precondition:EquipmentMode,linux-OS
# OnStart: NA
# OnComplete: NA
def EquipmentModeFlag_test():
    tc = ('303', '[TC303] Equipment_Mode_007', '多次执行装备模式脚本测试')
    result = ReportGen.LogHeaderResult(tc)
    assert BmcLib.force_reset()
    try:
        for n in range(5):
            assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
            for m in range(10):
                res = Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG)
                if not res:
                    result.log_fail()
                    logging.info("**set equipment mode flag fail.")
                    return
            assert BmcLib.force_reset()
        result.log_pass()
        return True
    except AssertionError:
        result.log_fail()
    finally:
        BmcLib.clear_cmos()


# Author: Fubaolin
# 装备模式恢复测试
# Precondition:EquipmentMode,linux-OS
# OnStart: NA
# OnComplete: NA
def EquipmentModeFlag_Valid_once():
    tc = ('304', '[TC304] Equipment_Mode_010', '装备模式恢复测试,，配置一次有效')
    result = ReportGen.LogHeaderResult(tc)
    str_Flag = 'Get EquipmentEnableFlag Variable 1(Success)'
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG), "**set equipment_mode_flag fail."
        assert BmcLib.debug_message(enable=True), "debug message enable fail"   #開啓全打印
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, 'Welcome to GRUB!', delay=1200), "boot up fail"
        ser_log = os.path.join(SutConfig.Env.LOG_DIR, 'TC304.log')
        assert (EquipmentModeFlag_ser_log(ser_log, str_Flag)), "EquipmentEnableFlag not found"
        assert BmcLib.debug_message(enable=False)       #關閉全打印，減少啓動時間
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        res1 = Sut.UNITOOL.read(*BiosCfg.EQUIP_FLAG)
        assert res1, "**read equipment_mode_flag fail."
        assert res1.get(list(BiosCfg.EQUIP_FLAG.keys())[0]) == '0', 'equipment_mode_flag test fail'
        logging.info('equipment_mode_flag test pass')
        result.log_pass()
        return True
    except AssertionError as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# Author: Fubaolin
# 装备流程完成后BIOS恢复正常启动测试
# Precondition:EquipmentMode,linux-OS,unitool
# OnStart: 'UEFI'模式
# Set:
# 1、在EquipDefaultSet.ini配置文件中设置多个不同变量的值；
# 2、设置EquipmentModeFlag为1，备份所有Setup变量并根据EquipDefaultSet.ini配置文件进行选项修改；
# 3、重启，查看BIOS串口打印是否获取到EquipmentModeFlag，有结果A；
# 4、进入OS下再重启，查询BIOS串口打印是否获取到EquipmentModeFlag，有结果B；
# 5、进入Setup菜单查看变量值是否均已恢复正常启动时的值，有结果C。
# A：第3步可成功获取到EquipmentModeFlag，获取所有备份的Setup变量，打印出备份的变量。
# B：OS下重启后BIOS没有获取到EquipmentModeFlag；
# C：进入Setup菜单查看更改的变量值均已恢复正常启动时的值。
# OnComplete: NA
def EquipmentModeFlag_Valid_Recovery():
    tc = ('305', '[TC305] Equipment_Mode_008', '装备流程完成后BIOS恢复正常启动测试')
    result = ReportGen.LogHeaderResult(tc)
    str_Flag = 'Get EquipmentEnableFlag Variable 1(Success)'
    str_Flag_Recover = 'Get EquipmentEnableFlag Variable 0(Success)'
    ActiveCpuCores = {"ActiveCpuCores": 20}
    ActiveCpuCores_Default = ['Active Processor Cores', '<All>']

    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config(BiosCfg.EQUIP_FLAG), "**set equipment_mode_flag fail."
        assert PlatMisc.unitool_command('b'), '** unitool backup fail'
        assert PlatMisc.unitool_command('setCustomDefault'), '** unitool setCustomDefault fail'
        assert Sut.UNITOOL.set_config(ActiveCpuCores)
        assert BmcLib.debug_message(enable=True), "debug message enable fail"  # 開啓全打印
        # set--3, results--A
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, "Clear EquipmentEnableFlag success", delay=600)
        ser_log = os.path.join(SutConfig.Env.LOG_DIR, 'TC305.log')
        assert EquipmentModeFlag_ser_log(ser_log, str_Flag), "EquipmentEnableFlag_1 not found"
        with open(ser_log, 'r+') as r:
            lines = [line.strip('\n') for line in r.readlines() if line.strip()]
            assert set(SutConfig.SysCfg.Unitool_Backup_Name) < set(lines), "Unitool_Backup_Name not found"
            logging.info("first reboot,found all key")
        # set--4, results--B
        assert BmcLib.force_reset()
        assert SerialLib.is_msg_present(Sut.BIOS_COM, "OnExitBootServices...", delay=600)
        assert EquipmentModeFlag_ser_log(ser_log, str_Flag_Recover), "EquipmentEnableFlag_0 not found"
        logging.info("second reboot,found all key")
        assert BmcLib.debug_message(enable=False)  # 關閉全打印，減少啓動時間
        # set--5, results--c
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.verify_info(ActiveCpuCores_Default, 20)
        logging.info('equipment_mode_flag test pass')
        result.log_pass()
        return True
    except AssertionError as e:
        logging.error(e)
        result.log_fail()
    finally:
        BmcLib.debug_message(enable=False)
        BmcLib.clear_cmos()


# Author: Fubaolin
# UEFI模式下使用uniCFG工具文件方式定制化菜单测试
# Precondition:EquipmentMode,linux-OS,unitool
# OnStart: EquipmentMode
# Set:
# 1、OS下使用unicfg工具使用文件方式生成用户定制化菜单,覆盖Advance、boot、power界面下的变量；
# 2、./uniCfg setCustomDefault生成客户定制化设置；
# 3、reboot复位，按DEL进入setup菜单，查看选项是否设置成功，有结果A；
# 4、检查setup菜单是否存在"Load Custom default"选项，有结果B。
#   A：选项设置成功。
#   B：setup菜单存在"Load Custom default"选项,且该选项功能正常.
@core.test_case(('307', '[TC307] Testcase_Equipment_Tools_002_003', '【Equipment模式】unitool方式定制化菜单测试'))
def EquipmentMode_Custom():
    custom_set = {"ActiveCpuCores": 20, "StaticTurbo": 2, "SPBoot": 0}
    verify_list = [['Active Processor Cores', '<20>'], ['Static Turbo', '<Auto>'], ['SP Boot', '<Disabled>']]
    load_cst_def = ['Load Custom Defaults']
    try:
        assert BmcLib.force_reset()
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        assert Sut.UNITOOL.set_config(custom_set), "**set equipment_mode_flag fail."
        res = Sut.UNITOOL.read(*custom_set)
        assert PlatMisc.unitool_command('setCustomDefault', Sut.OS_SSH), '** unitool setCustomDefault fail'
        assert PlatMisc.unitool_command('setCustomDefault', Sut.OS_SSH), '** unitool setCustomDefault fail'
        # verify verify_list[0],ActiveCpuCores
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_PRO_CFG, 20, Msg.PROCESSOR_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, verify_list[0], 20)
        assert SetUpLib.set_option_value('Active Processor Cores', '19', Key.UP, 1, save=True), 'set verify_list[0] ->failed'
        # verify verify_list[1],StaticTurbo
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Key.DOWN, Msg.PATH_ADV_PM_CFG, 20, Msg.ADV_POWER_MGF_CONFIG)
        assert SetUpLib.locate_option(Key.DOWN, verify_list[1], 20), '** verify ACT_CPU_CORES fail'
        assert SetUpLib.set_option_value('Static Turbo', 'Manual', Key.DOWN, 1, save=True), 'set verify_list[1] ->failed'
        # verify verify_list[2],SP Boot
        assert SetUpLib.continue_to_page(Msg.PAGE_ADVANCED)
        assert Sut.BIOS_COM.locate_setup_option(Key.RIGHT, [Msg.PAGE_BOOT], 10)
        assert SetUpLib.locate_option(Key.UP, verify_list[2], 10), '** SP Boot not found'
        assert SetUpLib.set_option_value('SP Boot', 'Enabled', Key.DOWN, 1, save=True), 'set verify_list[2] ->failed'
        # verify 存在"Load Custom default"选项,功能正常
        assert SetUpLib.continue_to_page(Msg.PAGE_SAVE)
        assert SetUpLib.locate_option(Key.DOWN, load_cst_def, 10), '** Load Custom default not found'  #验证LOAD_CST_DEF 选项存在
        SetUpLib.send_keys([Key.ENTER,  Key.Y, Key.F10, Key.Y], 5)
        assert MiscLib.ping_sut(SutConfig.Env.OS_IP, 300)
        res1 = Sut.UNITOOL.read(*custom_set)
        assert res == res1, '**Load_Custom_default function fail'
        return core.Status.Pass
    except AssertionError as e:
        logging.error(e)
    finally:
        BmcLib.clear_cmos()