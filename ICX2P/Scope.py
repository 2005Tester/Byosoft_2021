from Core import SutInit
from Core import var
from Core.TcExecutor import TestScope
from ICX2P.Config import SutConfig
from ICX2P.TestCase import UpdateBIOS, BiosTest, Os, Release, Legacy, CpuInit01, Smbios09, BootDevice06

# init SUT
SutInit.SutInit("ICX2P")


def release_basic(branch):  # Release minimal self test score
    var.set('branch', branch)
    # default mode test scope
    if UpdateBIOS.update_bios(branch):
        BiosTest.post_test()
        BiosTest.power_cycling()
        Release.check_bmc_warning()
        Release.me_version_status()
        BiosTest.pxe_test()
        BiosTest.load_default()
        BiosTest.security_boot()
        Release.registry_check()
        Release.compare_fdm_log()
        Release.hpm_downgrade_test()
        if Os.boot_to_suse():
            Smbios09.smbios_test_all()

    # Equip mode test scope
    if UpdateBIOS.update_bios_mfg(branch):
        Release.equip_mode_version_check()
        Smbios09.smbios_type128()
        if Os.boot_to_suse_mfg():
            Release.equip_mode_flag_check()


# Supported type (case senstive): Release, Daily, Weekly
def scope(type, branch='master'):
    test_scope = TestScope(SutConfig.TESTCASE_CSV, type)
    if UpdateBIOS.update_bios(branch):
        if Os.boot_to_suse():
            test_scope.run_test('os')
        test_scope.run_test('default')

    if Legacy.enable_legacy_boot():
        test_scope.run_test('legacy')
        Legacy.disable_legacy_boot()

    if UpdateBIOS.update_bios_mfg(branch):
        test_scope.run_test('equip')


# Define test scope for daily test
def daily_scope():
    scope("Daily")


# Entry for weekly test
def weekly_scope():
    scope("Weekly")


def release_scope():
    """Release Basic Function Test"""
    release_branch = "2288V6_012"
    var.set('branch', release_branch)
    scope("Release", release_branch)


# Bascic check for csv test plan file
def check_csv():
    test_scope = TestScope(SutConfig.TESTCASE_CSV, "Daily")
    test_scope.check_csv()


def debug_scope():
    UpdateBIOS.update_bios('master')
    CpuInit01.cpu_mem_info()
    BiosTest.power_efficiency_mode_loop()
    BootDevice06.boot_order_001()
    BootDevice06.boot_order_003()
    BootDevice06.boot_order_004()
    BootDevice06.boot_order_005()
