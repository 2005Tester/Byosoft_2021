#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.
import logging.config
import os
from sys import argv
from Common import LogConfig, Unitool
from Common import SutSerial
from Common import ssh
from ICX2P import UpdateBIOS, biosTest, DefaultValueTest, Pwd, Os, Release, Smbios, Legacy, DIMM, Cpu, \
    Pch, Hotkey
from ICX2P.Config import SutConfig 
from Report.ReportGen import ReportGenerator

# init seril
ser = SutSerial.SutControl(SutConfig.BIOS_SERIAL, 115200, 0.5, SutConfig.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)
sftp_bmc = ssh.sftp(SutConfig.BMC_IP, SutConfig.BMC_USER, SutConfig.BMC_PASSWORD)

# init OS SSH interface
ssh_os = ssh.SshConnection(SutConfig.OS_IP,SutConfig.OS_USER,SutConfig.OS_PASSWORD)
unitool = Unitool.SshUnitool(SutConfig.OS_IP, SutConfig.OS_USER, SutConfig.OS_PASSWORD, SutConfig.UNI_PATH)

# Init log setting
def init_log():
    log_dir = SutConfig.LOG_DIR
    log_format = LogConfig.gen_config(log_dir)
    logging.config.dictConfig(log_format)
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.info("Test Project: {0}".format(SutConfig.PROJECT_NAME))
    logging.info("SUT Configuration: {0}".format(SutConfig.SUT_CONFIG))
    return log_dir


# Generate html test report
def gen_report(log_dir):
    template = SutConfig.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.write_to_html()
    if len(argv) == 2 and argv[1] == "daily":
        report.post_result()


# for debug purpose
def debug_run():
    log_dir = init_log()
    Cpu.cpu_mem_info(ser, ssh_bmc)
    DIMM.Testcase_MemoryCompa_001(ser, ssh_bmc)
    DIMM.Testcase_MemoryCompa_006(ser, ssh_bmc, ssh_os)
    Hotkey.Testcase_SystemInfo_001(ser, ssh_bmc)
    Hotkey.Testcase_SystemInfo_002(ser, ssh_bmc)
    Hotkey.Testcase_SystemInfo_003(ser, ssh_bmc)
    Smbios.smbios_type128(ser,ssh_os, ssh_bmc, unitool)
    DIMM.Testcase_MemoryCompa_009(ser, ssh_bmc, unitool)
    biosTest.Testcase_SerialPrint_001(ser, ssh_bmc)
    biosTest.Testcase_SerialPrint_002(ser, ssh_bmc)
    gen_report(log_dir)


# Define test scope here
def run_test():
    log_dir = init_log()
    UpdateBIOS.update_bios(ser, ssh_bmc, sftp_bmc, 'master')
    biosTest.POST_Test(ser, ssh_bmc)
    biosTest.PM(ser, ssh_bmc)
    biosTest.usbTest(ser, ssh_bmc)
    Cpu.cpu_mem_info(ser, ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    Cpu.static_turbo_default(ser, ssh_bmc)
    Cpu.ufs_default_value(ser, ssh_bmc)
    DefaultValueTest.rrqirq(ser, ssh_bmc)
    biosTest.dram_rapl_option_check(ser, ssh_bmc)
    biosTest.securityBoot(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    biosTest.cnd_default_enable(ser, ssh_bmc)
    Cpu.upi_link_status(ser, ssh_bmc)
    Cpu.cpu_cores_active_enable_1(ser, ssh_bmc, ssh_os)
    Cpu.cpu_cores_active_enable_middle(ser, ssh_bmc, ssh_os)
    Cpu.cpu_cores_active_enable_max(ser, ssh_bmc, ssh_os)
    if Os.boot_to_suse(ser, ssh_bmc):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.Pwd_test(ser, ssh_bmc, ssh_os)
    DIMM.DPM.dimm_power_mgt_01(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_02(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_04(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_05(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_07(ser, ssh_bmc)
    Release.me_version_status(ser, ssh_bmc)
    biosTest.loadDefault(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    DIMM.Testcase_MemMargin_001(ser, ssh_bmc)
    Pch.usb_default_enable_check(ser, ssh_bmc)
    Pch.post_gpio_error_check(ser, ssh_bmc)
    if Legacy.enable_legacy_boot(ser, ssh_bmc):
        Legacy.disable_legacy_boot(ser, ssh_bmc)
    if UpdateBIOS.update_bios_mfg(ser, ssh_bmc, sftp_bmc, 'master'):
        Release.equip_mode_version_check(ser, ssh_bmc)
        Os.boot_to_suse_mfg(ser, ssh_bmc)
        Smbios.smbios_type128(ser, ssh_os, ssh_bmc, unitool)
    gen_report(log_dir)


if __name__ == '__main__':
    if len(argv) == 1 or argv[1] == "daily":
        run_test()

    elif argv[1] == "loop":
        cycle = 1
        while True:
            logging.info("-"*50 + "\n" + " "*45 + "Test Cycle:{0}".format(cycle))
            logging.info("-"*50)
            run_test()
            cycle += 1
    elif argv[1] == "debug":
        debug_run()
