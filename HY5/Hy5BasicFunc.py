# -*- encoding=utf8 -*-

__author__ = 'arthur'

import logging

from HY5.Hy5Config import Key
from Common import Misc
from Common.LogAnalyzer import LogAnalyzer
from HY5 import updatebios, Hy5TcLib, Hy5Config, Hy5BaseAPI

P = LogAnalyzer(Hy5Config.LOG_DIR)


# Basic Function Test Case: Flash, POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
# Flash: Upgrade flash, Parallel flash and Downgrade flash
def updateBios(serial, img):
    tc = ('010', 'Update BIOS by BMC', 'Outband BIOS update')
    result = Misc.LogHeaderResult(tc, serial)
    if not img:
        result.log_fail()
        return
    if not updatebios.update_specific_img(img, serial):
        result.log_fail()
        return
    result.log_pass()
    return True


# hpm update-downgrade cases,
def updateHPM(serial, ssh, img):
    tc = ('045', 'Update HPM', '配置不变升级')
    result = Misc.LogHeaderResult(tc, serial)

    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2OS)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.OS, timeout=30):
        result.log_fail()
        return
    if not Hy5TcLib.ping_sut():
        return
    if not Hy5TcLib.sftpFile(ssh):
        result.log_fail()
        return
    if not img:
        result.log_fail()
        return
    if not updatebios.upload_bios(img):
        result.log_fail()
        return
    if not updatebios.hpm_update():
        result.log_fail()
        return
    if not Hy5TcLib.cmpFile(ssh):
        result.log_fail()
        return
    if not Hy5TcLib.clearCMOS(ssh):
        pass
    result.log_pass()
    return True


# POST: POST Log(TBD) and Information Check
def POST_Test(serial, ssh):
    tc = ('012', 'POST Information Test', 'POST Information Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5TcLib.force_reset(ssh):
        result.log_fail()
        return
    msg_list = [Hy5Config.msg, Hy5Config.msg1, Hy5Config.msg2, Hy5Config.msg3]
    if not serial.waitStrings(msg_list, timeout=300):  # 考虑到满载配置
        result.log_fail()
        return
    result.log_pass()
    return True


# PM: Warm reset n times, Cold reset n times and AC (TBD)
def PM(serial, ssh, n=5):
    tc = ('014', 'Power Control Test', 'Power Control Test')
    result = Misc.LogHeaderResult(tc, serial)
    status = 0
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    logging.info("Warm reset loops: {0}".format(n))
    for i in range(n):
        try:
            logging.info("Warm reset cycle: {0}".format(i + 1))
            serial.send_keys_with_delay(Key.CTRL_ALT_DELETE)
            logging.debug("Ctrl + Alt + Del key sent")
            if not Hy5BaseAPI.toBIOSnp(serial):
                logging.info("Warm reset Test:Fail")
                status = 1
                continue
        except Exception as e:
            logging.error(e)
    # DC cycle n times
    logging.info("Cold reset loops: {0}".format(n))
    for j in range(n):
        try:
            logging.info("DC reset cycle: {0}".format(j + 1))
            if not Hy5BaseAPI.dcCycle(serial, ssh):
                logging.info("DC cycle Test:Fail")
                status = 2
                return
        except Exception as e:
            logging.error(e)
    if status == 1 and 2:
        result.log_fail()
        return

    result.log_pass()
    return True


# PXE Test
def pxeTest(serial, ssh, n=1):
    tc = ('015', 'PXE Test', 'PXE Test')
    result = Misc.LogHeaderResult(tc, serial)
    for i in range(n):
        if not Hy5BaseAPI.pressF12(serial, ssh):
            result.log_fail()
            return
        if not serial.waitString('Install', timeout=15):
            result.log_fail()
            return
    result.log_pass()
    return True


# Https Test
def httpsTest(serial, ssh):
    tc = ('016', 'Https Test', 'Https Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Key.RIGHT + Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.PXE_option, timeout=60):
        result.log_fail()
        return
    serial.send_data(Hy5Config.default_pwd)
    serial.send_data(chr(0x0D))
    if not serial.waitString('Start HTTPS Boot over IPv4', timeout=30):
        result.log_fail()
        return
    if not serial.waitString('Shell', timeout=60):
        result.log_fail()
        return
    result.log_pass()
    return True


# USB Test
def usbTest(serial, ssh):
    tc = ('017', 'USB Test', 'USB Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys(Key.RIGHT)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option1):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    msg_list = [Hy5Config.msg5, Hy5Config.msg6, Hy5Config.msg7]
    if not Hy5BaseAPI.verify_setup_options_down(serial, msg_list, 7):
        result.log_fail()
        return
    result.log_pass()
    return True


# Processor/DIMM Test
def ProcessorDIMM(serial, ssh):
    tc = ('019', 'Processor/DIMM Test', 'CPU/DIMM Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        return
    if not Hy5BaseAPI.toBIOSConf(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.RIGHT, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option2):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option3):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ENTER, Key.UP])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option4):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.CPU_info, 20):
        result.log_fail()
        return
    serial.send_keys_with_delay([Key.ESC, Key.ESC])
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.option5, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5BaseAPI.verify_setup_options_down(serial, Hy5Config.DIMM_info, 20):
        result.log_fail()
        return
    result.log_pass()
    return True


# PCIe card Test, TBD
def pcie():
    pass


# chipsec Test
def chipsecTest(serial, ssh):
    # username - OS user name, pwd - OS user password
    tc = ('020', 'chipsec Test', 'chipsec Test')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(Hy5Config.key2OS)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.OS, timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5TcLib.ping_sut():
        result.log_fail()
        return
    if not Hy5TcLib.chipsecMerge(ssh):
        result.log_fail()
        return
    result.log_pass()
    return True


# press F2
def pressF2(serial, ssh):
    tc = ('041', 'Setup菜单用户输入界面按F2切换键盘制式', '支持热键配置')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5TcLib.force_reset(ssh):
        result.log_fail()
        return
    if not serial.waitString(Hy5Config.msg, timeout=300):
        result.log_fail()
        return
    serial.send_keys(Key.DEL)
    if not serial.waitString("Press F2", timeout=30):
        result.log_fail()
        return
    serial.send_keys(Key.F2)
    if not serial.waitString('fr-FR'):
        result.log_fail()
        return
    serial.send_keys(Key.F2)
    if not serial.waitString('ja-JP'):
        result.log_fail()
        return
    serial.send_keys(Key.F2)
    if not serial.waitString('en-US'):
        result.log_fail()
        return
    serial.send_data("Admin@9000")
    serial.send_data(chr(0x0D))  # Send Enter
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if not serial.waitString('Continue', timeout=30):
        return
    result.log_pass()
    return True


def equipmentMode(serial, ssh):
    tc = ('050', 'Equipment Mode Test', '支持Equipment Mode')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5BaseAPI.toBIOS(serial, ssh):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2OS)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.suse):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5TcLib.ping_sut():
        result.log_fail()
        return
    if not Hy5TcLib.equipment(ssh):
        result.log_fail()
        return
    if not Hy5BaseAPI.toBIOSnp(serial):
        result.log_fail()
        return
    serial.send_keys_with_delay(Hy5Config.key2OS)
    if not serial.to_highlight_option(Key.DOWN, Hy5Config.suse):
        result.log_fail()
        return
    serial.send_keys(Key.ENTER)
    if not Hy5TcLib.ping_sut():
        result.log_fail()
        return
    cmd = 'dmidecode -t 128'
    path = Hy5Config.LOG_DIR
    Hy5TcLib.dump_smbios(ssh, cmd)
    if not P.smbiosCheck(cmd, path, Hy5Config.SMBIOS_TEMPLATE):
        result.log_fail()
        return
    result.log_pass()
    return True


# Main Func...
def hy5BasicTest(serial, ssh, n=1):
    # hpm image defined,
    lst_image = updatebios.get_test_image(Hy5Config.HPM_DIR)
    prev_image = updatebios.get_previous_test_image(Hy5Config.HPM_DIR)

    lst_binary_img = updatebios.get_test_image(Hy5Config.BINARY_DIR)
    prev_binary_img = updatebios.get_previous_test_image(Hy5Config.BINARY_DIR)
    for i in range(n):
        logging.info("Basic Func Test Cycle: {0}".format(i + 1))
        updateBios(serial, lst_binary_img)
        updateBios(serial, prev_binary_img)
        updateHPM(serial, ssh, prev_image)
        updateHPM(serial, ssh, lst_image)
        POST_Test(serial, ssh)
        PM(serial, ssh)
        pxeTest(serial, ssh)
        httpsTest(serial, ssh)
        usbTest(serial, ssh)
        ProcessorDIMM(serial, ssh)
        chipsecTest(serial, ssh)
        pressF2(serial, ssh)
    logging.info('Hy5 Basic Function test Completed...')