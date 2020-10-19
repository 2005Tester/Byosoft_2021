import logging.config
import os
from Common import LogConfig
from Common import SutSerial
from Common import ssh
from Moc25 import updatebios
from Moc25 import Moc25Config
from Moc25 import Moc25TcLib
from Moc25 import SetUp
from Report.ReportGen import ReportGenerator
from Common.LogAnalyzer import LogAnalyzer

# Init log setting
log_dir = Moc25Config.LOG_DIR
log_format = LogConfig.gen_config(log_dir)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)


# init seril
ser = SutSerial.SutControl("com9", 115200, 0.5, Moc25Config.SERIAL_LOG)

# init BMC SSH interface
ssh_bmc = ssh.SshConnection()

# Test case for log analysis
def check_log():
    log = LogAnalyzer(log_dir)
    logging.info("<TC900><Tittle>Check BIOS Log:Start")
    logging.info("<TC900><Description>Check whether there are asserts or exception in test")
    if log.check_bios_log():
        logging.info("<TC900><Result>Check BIOS Log:Pass")
    else:
        logging.info("<TC900><Result>Check BIOS Log:Fail")


def gen_report():
    template = Moc25Config.REPORT_TEMPLATE
    report = ReportGenerator(template, os.path.join(log_dir, "test.log"), os.path.join(log_dir, "report.html"))
    report.collect_test_result()
    report.write_to_html()


if __name__ == '__main__':
    #updatebios.get_test_image(Moc25Config.BINARY_DIR)
    SetUp.check_bios_version(ser, ssh_bmc)
    Moc25TcLib.boot_AliOS(ser, ssh_bmc)
    SetUp.boot_uefi_shell(ser, ssh_bmc)
    check_log()
    gen_report()

