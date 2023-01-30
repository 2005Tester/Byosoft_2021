from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# Acpi Test Case
# TC 2200-2200
####################################


@core.test_case(("2200", "[TC2200] Testcase_Acpi_001", "ACPI规范测试"))
def Testcase_Acpi_001():
    """
    Name:       ACPI规范测试
    Condition:
    Steps:      1、OS下使用acpidump工具导出ACPI表信息acpidump > acpi.out，检查能否dump成功，有结果A；
                2、使用命令acpixtract -a acpidump.out分离各表数据，检查是否异常，有结果B。
    Result:     A：能dump出完整的ACPI表格，无异常；
                B：能分离每个具体的ACPI表项。
    Remark:
    """
    try:
        path_acpi = f"~/dump_acpi_list"
        cmd_dump = "acpidump -o AcpiTable.out"
        cmd_xtract = "acpixtract -a AcpiTable.out"
        cmds = f"rm -rf {path_acpi}; mkdir {path_acpi};cd {path_acpi};{cmd_dump};{cmd_xtract}"
        acpi_tables = ['apic.dat', 'bdat.dat', 'bert.dat', 'dmar.dat', 'dsdt.dat', 'erst.dat', 'facp.dat',
                    'facs.dat', 'fpdt.dat', 'hest.dat', 'hmat.dat', 'hpet.dat', 'mcfg.dat', 'msct.dat', 'oem\d.dat',
                    'prmt.dat', 'slit.dat', 'spcr.dat', 'srat.dat', 'ssdm.dat', 'ssdt\d.dat', 'wddt.dat', 'wsmt.dat']
        if SutConfig.Sys.TPM:
            acpi_tables.append("tpm2.dat")

        if not MiscLib.ping_sut(SutConfig.Env.OS_IP, 10):
            assert SetUpLib.boot_to_default_os()
        assert SshLib.execute_command(Sut.OS_SSH, cmds), 'acpidump is fail'
        result = SshLib.execute_command(Sut.OS_SSH, f"cd {path_acpi};ls *.dat")
        logging.info(f"{result}")
        table_miss = [dat for dat in acpi_tables if not re.search(dat, result)]
        assert not table_miss, f"{table_miss}"
        logging.info("All ACPI table dump success")
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.clear_cmos()

