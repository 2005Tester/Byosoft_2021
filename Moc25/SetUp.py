#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
# -*- encoding=utf8 -*-
import logging
import time
import os
import re
from Moc25 import Moc25TcLib
from Moc25 import SutConfig
from Common.LogAnalyzer import LogAnalyzer
from Moc25.SutConfig import Msg
from Report import ReportGen

# Key mapping
ENTER = [chr(0x0D)]
DEL = [chr(0x7F)]
F2 = [chr(0x1b), chr(0x4f), chr(0x51)]
F9 = [chr(0x1b), chr(0x4f), chr(0x58)]
F10 = [chr(0x1b), chr(0x4f), chr(0x59)]
F11 = [chr(0x1b), chr(0x4f), chr(0x5a)]
F12 = [chr(0x1b), chr(0x4f), chr(0x5b)]
UP = [chr(0x1b), chr(0x5b), chr(0x41)]
DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
Y = [chr(0x59)]


# global variables of string to catch for a specific setup option
SKT_CONFIG = "Socket Configuration"
SKT_CONFIG_MSG = "Processor Configuration"
PLAT_CONFIG = "Platform Configuration"
PCHIO_CONFIG = "PCH-IO Configuration"
IIO_CONFIG = "IIO Configuration"
IIO_SKT0_CONFIG = "Socket0 Configuration"

HOT_KEY_PROMPT = "Press <DEL> to SETUP"
MSG_SETUP_MAIN = "Byosoft ByoCore"


# send multiple keys in a row with delay, keys = list
def send_keys_with_delay(serial, keys, delay):
    for key in keys:
        serial.send_keys(key)
        time.sleep(delay)


# Navigate in a setup page and verify multiple setup options are correct
def verify_setup_options(serial, setup_options, try_count):
    if serial.navigate_and_verify(DOWN, setup_options, try_count):
        return True
    if not len(setup_options) == 0:
        if serial.navigate_and_verify(UP, setup_options, try_count):
            return True
          

# Boot with hotkey
def boot_with_hotkey(serial, key, msg):
    logging.info("Moc25 Common Test Lib: boot with hotkey")
    logging.info("Rebooting SUT...")
    if not Moc25TcLib.force_reset(serial):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Looking for {0}".format(HOT_KEY_PROMPT))
    if not serial.boot_with_hotkey(key, msg, 300, hotkey_prompt=HOT_KEY_PROMPT):
        logging.info("Boot by hotkey failed.")
        return
    return True


# Boot to boot manager by hotkey
def boot_manager(serial):
    logging.info("Moc25 Common Test Lib: boot to boot manager")
    msg = "Please select boot device"
    if not boot_with_hotkey(serial, F11, msg):
        logging.info("Booting to boot manager failed.")
        return
    return True


# Boot to Setup by hotkey
def boot_to_setup(serial):
    logging.info("Moc25 Common Test Lib: boot to Setup by Del")
    if not boot_with_hotkey(serial, DEL, MSG_SETUP_MAIN):
        logging.info("Boot to BIOS Setup failed.")
        return
    return True


# Boot to Setup advanced page
def boot_to_setup_advanced(serial):
    if not boot_to_setup(serial):
        return
    serial.send_keys(RIGHT)
    if not serial.is_msg_present_general('All Cpu Information'):
        logging.info("Moc25 Common Test Lib: Failed to enter advanced page")
        return
    return True


# Search and attempt specific boot option in bootmanager
def attempt_boot_option(serial, boot_option):
    if not boot_manager(serial):
        return
    for i in range(0, 35):
        if not serial.is_msg_present_general(boot_option,2):
            serial.send_keys(UP)
        else:
            serial.send_keys(ENTER)
            logging.info("{0} found in bootmanager".format(boot_option))
            return True

    logging.info("{0} not found in bootmanager".format(boot_option))
    return




# Reset BIOS default by F9
def reset_default(serial):
    if not boot_to_setup(serial):
        return
    time.sleep(2)
    logging.info("Reset BIOS to default.")
    send_keys_with_delay(serial, [F9, Y], 3)
    time.sleep(10)
    send_keys_with_delay(serial, [F10, Y], 3)
    if not serial.is_msg_present_general(Msg.OS_MSG, 180):
        return
    logging.info("Reset BIOS default and reboot to OS successful")
    return True


# boot to setup menu , socket configuration
def boot_to_skt_config(serial):
    logging.info("Moc25 Common Test Lib: boot to socket configuration")
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, [SKT_CONFIG], 10, SKT_CONFIG_MSG):
        logging.info("Failed to enter socket configuration menu")
        return
    logging.info("Moc25 Common Test Lib: boot to socket configuration Pass")
    return True


# boot to setup menu , processor configuration
def boot_to_processor_config(serial):
    logging.info("Moc25 Common Test Lib: boot to processor configuration")
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, [SKT_CONFIG, SKT_CONFIG_MSG], 10, "Per-Socket Configuration"):
        logging.info("Failed to enter processor configuration menu")
        return
    logging.info("Moc25 Common Test Lib: boot to processor configuration Pass")
    return True


# boot to memory configuration
def boot_to_mem_config(serial):
    logging.info("Moc25 Common Test Lib: boot to memory configuration")
    mem_menu = [SKT_CONFIG, "Memory Configuration"]
    mem_menu_msg = "Integrated Memory Controller"
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, mem_menu, 10, mem_menu_msg):
        logging.info("Failed to enter memory configuration menu")
        return
    logging.info("Moc25 Common Test Lib: boot to memory configuration Pass")
    return True

# Boot to Common RefCode Configuration
def boot_to_common_rc_config(serial):
    logging.info("Moc25 Common Test Lib: boot to Common RefCode Configuration")
    rc_menu = [SKT_CONFIG, "Common RefCode Configuration"]
    rc_menu_msg = "Common RefCode Configuration"
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, rc_menu, 10, rc_menu_msg):
        logging.info("Failed to enter Common RefCode configuration menu")
        return
    logging.info("Moc25 Common Test Lib: boot to Common RefCode configuration Pass")
    return True

# boot to server management
def boot_to_server_manager(serial):
    if not boot_to_setup(serial):
        return
    server_mgmt = ["Server Configuration"]
    serer_mgmt_msg = "Server Configuration"
    logging.info("Moc25 Common Test Lib: Go to Server Manager")
    if not serial.enter_setup_menu(RIGHT, server_mgmt, 10, serer_mgmt_msg):
        return
    logging.info("Moc25 Common Test Lib: Enter Server Manager Successfully")
    return True

# boot to boot manager menu in setup->Boot page
def boot_to_setup_bm(serial):
    if not boot_to_setup(serial):
        return
    boot_order_cfg = "Boot Maintenance Manager"
    if not serial.find_setup_option(RIGHT, boot_order_cfg, 12):
        logging.info("{0} not found".format(boot_order_cfg))
        return
    logging.info("{0} found".format(boot_order_cfg))
    boot_manager = "Boot Manager"
    if not serial.find_setup_option(DOWN, boot_manager, 2):
        logging.info("{0} not found".format(boot_manager))
        return
    logging.info("{0} found".format(boot_manager))
    return True


# navigate to boot order configuration menu in setup->boot page
def locate_boot_bootorder(serial):
    if not boot_to_setup(serial):
        return
    boot_order_cfg = "Boot Maintenance Manager"
    logging.info("Locate boot configuration")
    if not serial.find_setup_option(RIGHT, boot_order_cfg, 12):
        logging.info("{0} not found".format(boot_order_cfg))
        return
    logging.info("{0} found".format(boot_order_cfg))
    if not serial.find_setup_option(DOWN, "Boot Manager", 2):
        logging.info("Boot Manager not found")
        return
    return True


# boot to security configuration
def boot_to_security_config(serial):
    if not boot_to_setup(serial):
        return
    password_setting = ["Set Administrator Password"]
    security_cfg_msg = "type"
    logging.info("Moc25 Common Test Lib: Go to Security Configuration")
    if not serial.enter_setup_menu(RIGHT, password_setting, 10, security_cfg_msg):
        return
    logging.info("Moc25 Common Test Lib: Enter Security Configuration Successfully")
    return True


# boot to PCH-IO Configuration
def boot_to_pchio(serial):
    logging.info("Moc25 Common Test Lib: boot to PCH-IO configuration")
    pchio_menu = [PLAT_CONFIG, PCHIO_CONFIG]
    pchio_menu_msg = "PCI Express Configuration"
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, pchio_menu, 10, pchio_menu_msg):
        logging.info("Failed to enter PCH-IO configuration menu")
        return
    logging.info("Moc25 Common Test Lib: boot to PCH-IO configuration Pass")
    return True


# boot to IIO socket0 configuration
def boot_to_iio_skt0(serial):
    logging.info("Moc25 Common Test Lib: boot to IIO Socket0 configuration")
    iio_skt0_menu = [SKT_CONFIG, IIO_CONFIG, IIO_SKT0_CONFIG]
    iio_skt0_menu_msg = "Socket0 Configuration"
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, iio_skt0_menu, 10, iio_skt0_menu_msg):
        logging.info("Failed to enter IIO Socket0 configuration menu")
        return
    logging.info("Moc25 Common Test Lib: boot to IIO Socket0 configuration Pass")
    return True   

# Boot to Miscellaneous Configuration
def boot_to_misc_configuration(serial):
    logging.info("Moc25 Common Test Lib: boot to Miscellaneous Configuration")
    if not boot_to_setup_advanced(serial):
        return
    misc_configuration = [PLAT_CONFIG, "Miscellaneous Configuration"]
    msg_confirm = "Application Profile"
    if not serial.enter_setup_menu(DOWN, misc_configuration, 12, msg_confirm):
        logging.info("Moc25 Common Test Lib: boot to Miscellaneous Configuration Failed")
        return
    logging.info("Moc25 Common Test Lib: boot to Miscellaneous Configuration Pass")
    return True


# Reboot system and navigate to CPU C State Control menu
def boot_to_c_state_control(serial):
    logging.info("Reboot and go to CPU C State Control")
    adv_pm_cfg = "Advanced Power Management Configuration"
    c_state_control = "CPU C State Control"
    c_state = [SKT_CONFIG, adv_pm_cfg, c_state_control]
    msg = "Enable Monitor MWAIT"
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, c_state, 10, msg):
        logging.info("Failed to enter CPU C State Control")
        return
    logging.info("Booted to CPU C State Control")
    return True


# Reboot system and navigate to CPU P State Control menu
def boot_to_p_state_control(serial):
    logging.info("Reboot and go to CPU P State Control")
    adv_pm_cfg = "Advanced Power Management Configuration"
    p_state_control = "CPU P State Control"
    p_state = [SKT_CONFIG, adv_pm_cfg, p_state_control]
    msg = "CPU P State Control"
    if not boot_to_setup_advanced(serial):
        return
    if not serial.enter_setup_menu(DOWN, p_state, 10, msg):
        logging.info("Failed to enter CPU P State Control")
        return
    logging.info("Booted to CPU P State Control")
    return True

# Change cpu core count in setup and verify in OS
def change_cpu_core(bitmap, num, serial):
    if not boot_to_skt_config(serial):
        return
    send_keys_with_delay(serial, [ENTER, ENTER, ENTER], 2)
    if not serial.is_msg_present_general('Available Bitmap'):
        logging.info("Failed to enter socket 0 configutation")
        return
    keys_set_max_core = [DOWN, ENTER, bitmap, ENTER, F10, Y]
    send_keys_with_delay(serial, keys_set_max_core, 2)
    logging.info("Verify Core count in OS...")
    if not serial.is_msg_present_general(Msg.OS_MSG, 180):
        logging.info("Boot to AliOS Fail")
        return
    if not Moc25TcLib.login_os(serial):
        logging.info("Login AliOS Fail")
        return
    serial.send_data("cat /proc/cpuinfo | grep \"cpu cores\" | uniq\n")
    if not serial.is_msg_present_general("cpu cores\s+: {0}".format(num)):
        return
    logging.info("Core count verified in OS")
    return True


# Verify shell timeout setup option
def verify_shell_timeout(serial, value):
    if not boot_to_setup_advanced(serial):
        return
    logging.info("Go to Boot Options menu")
    if not serial.enter_setup_menu(Moc25Config.Key.DOWN, ["Boot Options"], 10, "Boot Manager"):
        return
    if not verify_setup_options(serial, ["\[{0}\]\s+System Shell Timeout".format(value)], 3):
        logging.info("Shell timeout verify failed")
        return
    return True


# Modify shell timeout setup option
def change_shell_timeout(serial):
    logging.info("Boot to setup advanced menu")
    if not boot_to_setup_advanced(serial):
        return
    logging.info("Go to Boot Options menu")
    if not serial.enter_setup_menu(Moc25Config.Key.DOWN, ["Boot Options"], 10, "Boot Manager"):
        return
    key_change_timeout = [DOWN, ENTER, '99', ENTER, F10, Y]
    logging.info("Change shell timeout value")
    send_keys_with_delay(serial, key_change_timeout, 2)
    logging.info("Reboot to setup")
    if not serial.boot_with_hotkey_general(DEL, HOT_KEY_PROMPT, MSG_SETUP_MAIN, 300):
        return
    if not verify_shell_timeout(serial, "99"):
        return
    return True


# def init enviroment for automation test
def init_test(sut):
    serial = sut.bios_serial
    bmc_serial = sut.bmc_serial
    tc = ('000', 'Init Test Enviroment', 'Intilize test enviroment for auotmation test execution')
    result = ReportGen.LogHeaderResult(tc, serial)
    logging.info("Reset BIOS default")
    if not reset_default(serial):
        result.log_fail()
        return
    logging.info("Reset ipmi bootdev to none")
    cmd = 'ipmitool chassis bootdev none\n'
    ret = 'Set Boot Device to none'
    if not Moc25TcLib.ipmi_command_com(bmc_serial, cmd, ret):
        result.log_fail()
        return
    result.log_pass()
    return True


# check BIOS version
def check_bios_version(serial):
    tc = ('010', 'Check BIOS Version', 'Verify Whether BIOS version is correct in setup main page.')
    result = Misc.LogHeaderResult(tc, serial)

    keys = DOWN
    if not boot_to_setup(serial):
        result.log_fail()
        return
    serial.send_keys(keys)
    if not serial.is_msg_present_general(Moc25Config.BIOS_VERSION, 120):
        result.log_fail()
        return
    result.log_pass()
    return True

# check ME status
def check_me_status(serial):
    tc = ('011', 'Check ME Status', 'Verify Whether ME is working in operational mode.')
    result = Misc.LogHeaderResult(tc, serial)

    if not boot_to_setup(serial):
        result.log_fail()
        return
    keys = [RIGHT, DOWN, DOWN, DOWN, DOWN, ENTER, DOWN, DOWN, DOWN, DOWN, ENTER]
    for key in keys:
        serial.send_keys(key)
        time.sleep(1)
    if not serial.is_msg_present_general('General ME Configuration'):
        result.log_fail()
        return
    keys = [DOWN, DOWN, DOWN, DOWN, DOWN]
    for key in keys:
        serial.send_keys(key)
        time.sleep(1)
    if not serial.is_msg_present_general('Operational'):
        result.log_fail()
        return
    result.log_pass()
    return True

# Precondition: No
# Status on Test Complete: BIOS Setup
def reset_bios_default_test(serial):
    tc = ('012', 'Reset Default by Hotkey', '使用F9恢复BIOS默认设置')
    result = Misc.LogHeaderResult(tc, serial)
    if not change_shell_timeout(serial):
        result.log_fail()
        return
    logging.info("Resetting BIOS default by F9.")
    if not reset_default(serial):
        result.log_fail()
        return
    if not verify_shell_timeout(serial, "5"):
        result.log_fail()
        return
  
    result.log_pass()
    return True

# Test full debug message
def debug_msg_level_test(serial):
    tc = ('013', '支持串口日志记录', '串口日志级别测试')
    result = Misc.LogHeaderResult(tc, serial)
    if not boot_to_setup_advanced(serial):
        result.log_fail()
        return
    misc_configuration = [PLAT_CONFIG, "Miscellaneous Configuration"]
    msg_confirm = "Application Profile"
    if not serial.enter_setup_menu(DOWN, misc_configuration, 12, msg_confirm):
        result.log_fail()
        return
    dbg_msg_option = "System Debug Mode"
    if not serial.find_setup_option(DOWN, dbg_msg_option, 30):
        result.log_fail()
        return
    key_en_dbg_msg = [ENTER, DOWN, ENTER, F10, Y]
    send_keys_with_delay(serial, key_en_dbg_msg, 2)
    if not serial.is_msg_present_general("START_MRC_RUN"):
        result.log_fail()
        return
    logging.info("Booting in full debug message level")
    if not serial.is_msg_present_general("InstallProtocolInterface", 300):
        result.log_fail()
        return
    logging.info("Continue Boot...")
    if not serial.is_msg_present_general(Msg.OS_MSG, 600):
        logging.info("Failed to boot to OS after full debug message level enabled.")
        result.log_fail()
        return
    result.log_pass()
    return True

# read bios configuration by byocfg and compare with expected default values
def bios_config_read(ssh):
    tc = ('014', '带内配置工具支持BIOS配置读取', '读取配置并与默认值比较')
    result = Misc.LogHeaderResult(tc)

    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Failed to login.")
        result.log_fail()
        return
    logging.info("Dump bios configuration")
    ssh.dump_info('python /root/ByoCfg/byocfg.py -r /root/ByoCfg/Setup.Cfg', Moc25Config.LOG_DIR, "bios_config.log")
    if not os.path.exists(os.path.join(Moc25Config.LOG_DIR, "bios_config.log")):
        logging.info("Failed to dump setup configuration data.")
        result.log_fail()
        return

    expected_values = ".\\Moc25\\Logs\\bios_config.log"
    current_values = os.path.join(Moc25Config.LOG_DIR, "bios_config.log")
    diffs = LogAnalyzer.check_diff(expected_values, current_values)
    if diffs:
        for diff in diffs:
            logging.info(diff)
        result.log_fail()
        return
    logging.info("Default value of bios configuration is verified.")
    result.log_pass()
    return
    
# Change setup options by byocfg tool and verify in setup
def bios_config_write(serial, ssh):
    tc = ('015', '带内配置工具支持BIOS配置设置', '带内配置工具修改选项并验证')
    result = Misc.LogHeaderResult(tc)
    Moc25TcLib.force_reset(serial)
    if not Moc25TcLib.continue_boot_and_login_os(serial):
        result.log_fail()
        return
    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Failed to login.")
        result.log_fail()
        return
    logging.info("Write bios configuration")
    ssh.execute_command('python /root/ByoCfg/byocfg.py -w /root/ByoCfg/tc015.Cfg')
    logging.info("Reboot and verify changed setup options.")
    logging.info("Verify: SpeedStep (Pstates)=0")
    if not boot_to_p_state_control(serial):
        result.log_fail()
        return
    speed_step = [r"<Disable>\s+SpeedStep \(Pstates\)"]
    if not verify_setup_options(serial, speed_step, 6):
        result.log_fail()
        return
    logging.info("Verified: SpeedStep (Pstates)=0")
    logging.info("Verify: State After G3=0, External SSC Enable=3, WDT Enable=0")
    if not boot_to_pchio(serial):
        result.log_fail()
        return
    afterg3 = r"<S0 State>\s+State After G3"
    external_ssc = r"<0.5%>\s+External SSC Enable - CK441"
    wdt = r"<Disabled>\s+ WDT Enable "
    options = [external_ssc, afterg3]
    if not verify_setup_options(serial, options,30):
        result.log_fail()
        return
    logging.info("BIOS configurations are changed and verified.")
    result.log_pass()
    return
  

# read bios configuration by byocfg and compare with expected default values
def bios_config_read_all(ssh):
    tc = ('016', 'Setup 基线测试', 'Setup 基线测试, 菜单选项一致性测试')
    result = Misc.LogHeaderResult(tc)

    if not ssh.login(Moc25Config.OS_IP, Moc25Config.OS_USER, Moc25Config.OS_PASSWORD):
        logging.info("Failed to login.")
        result.log_fail()
        return
    logging.info("Dump bios configuration")
    ssh.dump_info('python /root/ByoCfg/byocfg.py -r /root/ByoCfg/All_Setup.Cfg', Moc25Config.LOG_DIR, "bios_config_all.log")
    if not os.path.exists(os.path.join(Moc25Config.LOG_DIR, "bios_config_all.log")):
        logging.info("Failed to dump setup configuration data.")
        result.log_fail()
        return

    expected_values = ".\\Moc25\\Logs\\bios_config_all.log"
    current_values = os.path.join(Moc25Config.LOG_DIR, "bios_config_all.log")
  
    diffs = LogAnalyzer.check_diff(expected_values, current_values)
    if diffs:
        for diff in diffs:
            logging.info(diff)
        result.log_fail()
        return
    logging.info("Default value of all bios configuration is verified.")

    logcheck = LogAnalyzer(Moc25Config.LOG_DIR)
    if logcheck.check_options_auto(current_values):
        result.log_fail()
        return

    result.log_pass()
    return


