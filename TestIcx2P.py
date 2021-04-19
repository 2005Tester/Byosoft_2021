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
from ICX2P import UpdateBIOS, SutConfig, biosTest, DefaultValueTest, Pwd, Os, Release, Smbios, Legacy, DIMM, Cpu
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
#    Os.move_suse_to_first(ser, ssh_bmc)
#     DIMM.DPM.dimm_power_mgt_010(ser, ssh_os, ssh_bmc)
    if UpdateBIOS.update_bios_mfg(ser, log_dir, 'master'):
        Os.move_suse_to_first(ser, ssh_bmc)
        Release.equip_mode_version_check(ser, ssh_bmc)
        Os.boot_to_suse_mfg(ser, ssh_bmc)
        Smbios.smbios_type128(ser, ssh_os, ssh_bmc, unitool)
    UpdateBIOS.update_bios(ser, ssh_bmc, sftp_bmc, 'master')
    gen_report(log_dir)


# Define test scope here
def run_test():
    log_dir = init_log()
    UpdateBIOS.update_bios(ser, ssh_bmc, sftp_bmc, 'master')
    biosTest.POST_Test(ser, ssh_bmc)
    biosTest.PM(ser, ssh_bmc)
    biosTest.usbTest(ser, ssh_bmc)
    biosTest.ProcessorDIMM(ser, ssh_bmc)
    biosTest.pressF2(ser, ssh_bmc)
    biosTest.staticTurbo(ser, ssh_bmc)
    biosTest.ufs(ser, ssh_bmc)
    DefaultValueTest.rrqirq(ser, ssh_bmc)
    biosTest.dramRAPL(ser, ssh_bmc)
    biosTest.securityBoot(ser, ssh_bmc)
    biosTest.vtd(ser, ssh_bmc)
    biosTest.cnd_default_enable(ser, ssh_bmc)
    Cpu.upi_link_status(ser, ssh_bmc)
    if Os.boot_to_suse(ser, ssh_bmc):
        Smbios.smbios_test_all(ssh_os)
        Release.equip_mode_flag_check(unitool)
    Pwd.simplePWDTest(ser, ssh_bmc)
    Pwd.Simple_password_validity(ser, ssh_bmc)
    Pwd.Simple_password_disenable(ser, ssh_bmc)
    Pwd.Simple_password_save_enable(ser, ssh_bmc)
    Pwd.Simple_password_save_disable(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_002(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_003(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_004(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_005_019_021(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_006(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_007(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_008(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_009(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_010(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_011_012_014(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_013(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_015(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_016(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_020(ser, ssh_bmc)
    Pwd.PBPWS.Testcase_BiosPasswordSecurity_022(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_01(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_07(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_08(ser, ssh_bmc)
    Pwd.PWDAUTHMGT.pwd_auth_mgt_09(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_01(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_02(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_04(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_05(ser, ssh_bmc)
    DIMM.DPM.dimm_power_mgt_07(ser, ssh_bmc)
    Release.me_version_status(ser, ssh_bmc)
    biosTest.loadDefault(ser, ssh_bmc)
    if Legacy.enable_legacy_boot(ser, ssh_bmc):
        Legacy.disable_legacy_boot(ser, ssh_bmc)
    if UpdateBIOS.update_bios_mfg(ser, ssh_bmc, sftp_bmc, 'master'):
        Os.move_suse_to_first(ser, ssh_bmc)
        Release.equip_mode_version_check(ser, ssh_bmc)
        Os.boot_to_suse_mfg(ser, ssh_bmc)
#        Smbios.smbios_type128(ser, ssh_os, ssh_bmc, unitool)
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
