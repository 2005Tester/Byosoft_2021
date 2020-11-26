# -*- encoding=utf8 -*-

__author__ = 'arthur'

import logging
import time

from HY5 import Hy5TcLib, updatebios, Hy5Config
from HY5.Hy5Config import Key
from Common import Misc

# Basic Function Test Case: Flash, POST, Boot, Setup, OS Installation, PM, Device, Chipsec Test and Source code cons.
msg = 'Press Del go to Setup Utility'
msg1 = 'Press F11 go to BootManager'
msg2 = 'Press F12 go to PXE boot'
msg3 = 'Press F6 go to SP boot'
msg4 = 'BIOS Configuration'
msg5 = 'USB Mouse\s+1'
msg6 = 'USB Keyboard\s+1'
msg7 = 'USB Mass Storage\s+2'
pwd_info = 'The current password is the default password.Please update password!'

# CPU, DIMM info
CPU_info = ['Processor ID\s+0005065B', 'Processor Frequency\s+2.500GHz', 'Microcode Revision\s+0700001E']
DIMM_info = ['DIMM000\s+S0.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM', 'DIMM100\s+S1.CA.D0:2933MT/s Hynix DRx4 32GB RDIMM']


# to BIOS with power action, for restore test Env,
def toBIOS(serial, ssh, pwd='Admin@9000'):
    if not Hy5TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    logging.info("Booting to setup")
    if not serial.waitString(msg, timeout=300):
        return
    serial.send_keys_with_delay(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString("Press F2", timeout=15):
        return
    serial.send_data(pwd)
    time.sleep(0.2)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if serial.waitString(pwd_info):
        serial.send_data(chr(0x0D))  # Send Enter
    else:
        # 新密码输入没有提示信息，无需按两次回车键
        logging.info('The default pwd may be modified before, ignore it and try the new pwd next step')
        serial.send_keys_with_delay(Key.RIGHT + Key.LEFT)
        pass
    if not serial.waitString('Continue', timeout=60):
        return
    logging.info("Booting to setup successfully")
    return True

# to BIOS without power action
def toBIOSnp(serial, pwd='Admin@9000'):
    logging.info("HaiYan5 Common Test Lib: boot to setup")
    if not serial.waitString(msg, timeout=600):  # set to 600 开启全打印，启动时间较长
        return
    serial.send_keys_with_delay(Key.DEL)
    logging.info("Hot Key sent")
    if not serial.waitString("Press F2", timeout=30):  # 考虑全打印，延长15s
        return
    serial.send_data(pwd)
    serial.send_data(chr(0x0D))  # Send Enter
    logging.info("Send password...")
    if serial.waitString(pwd_info):
        serial.send_data(chr(0x0D))  # Send Enter
    else:
        # 新密码输入没有提示信息，无需按两次回车键
        logging.info('The default pwd may be modified before, ignore it and try the new pwd next step')
        serial.send_keys_with_delay(Key.RIGHT + Key.LEFT)
        pass
    if not serial.waitString('Continue', timeout=60):   # 考虑全打印，延长至1分钟
        return
    logging.info("Booting to setup successfully")
    return True


def dcCycle(serial, ssh):
    if not toBIOS(serial, ssh):
        return
    if not Hy5TcLib.force_power_cycle(ssh):
        return
    logging.info("Booting to setup")
    if not toBIOSnp(serial):
        return
    logging.info("Booting to setup successfully")
    return True

# for load default test
def verify_setup_options_up(serial, setup_options, try_count):
    if serial.navigate_and_verify(Key.UP, setup_options, try_count):
        return True
    if serial.navigate_and_verify(Key.DOWN, setup_options, try_count):
        return True

def verify_setup_options_down(serial, setup_options, try_count):
    if serial.navigate_and_verify(Key.DOWN, setup_options, try_count):
        return True
    if serial.navigate_and_verify(Key.UP, setup_options, try_count):
        return True

# Flash: Upgrade flash, Parallel flash and Downgrade flash
def Upgrade_Test(serial):
    logging.info("<TC010><Tittle>Update BIOS by BMC:Start")
    logging.info("<TC010><Description>Outband BIOS update")
    image = updatebios.get_test_image(Hy5Config.BINARY_DIR)
    if not image:
        logging.info("Update BIOS by BMC:Skip")
        return
    if not updatebios.update_specific_img(image, serial):
        logging.info("<TC010><Result>Update BIOS by BMC:Fail")
        return
    logging.info("<TC010><Result>Update BIOS by BMC:Pass")
    return True

def Downgrade_Test(serial):
    logging.info("<TC011><Tittle>Downgrade BIOS by BMC:Start")
    logging.info("<TC011><Description>Outband BIOS downgrade")
    image = updatebios.get_previous_test_image(Hy5Config.BINARY_DIR)
    if not image:
        logging.info("Downgrade BIOS by BMC:Skip")
        return
    if not updatebios.update_specific_img(image, serial):
        logging.info("<TC011><Result>Downgrade BIOS by BMC:Fail")
        return
    logging.info("<TC011><Result>Downgrade BIOS by BMC:Pass")
    return True

# POST: POST Log(TBD) and Information Check
def POST_Test(serial, ssh):
    logging.info("<TC012><Tittle>POST Information Test:Start")
    logging.info("<TC012><Description>POST Information Check")
    logging.info("Rebooting SUT...")
    if not Hy5TcLib.force_reset(ssh):
        logging.info("Rebooting SUT Failed.")
        return
    msg_list = [msg, msg1, msg2, msg3]
    if not serial.waitStrings(msg_list, 100):
        logging.info("<TC012><Result>POST Information Test:Fail")
        return
    logging.info("<TC012><Result>POST Information Test:Pass")
    return True


# PM: Warm reset n times, Cold reset n times and AC (TBD)
def PM(serial, ssh, n):
    status = 0
    logging.info("<TC014><Tittle>Power Control Test:Start")
    logging.info("<TC014><Description>Power action Test")
    if not toBIOS(serial, ssh):
        return
    logging.info("Warm reset loops: {0}".format(n))
    for i in range(n):
        try:
            logging.info("Warm reset cycle: {0}".format(i + 1))
            serial.send_keys_with_delay(Key.CTRL_ALT_DELETE)
            logging.info("Ctrl + Alt + Del key sent")
            if not toBIOSnp(serial):
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
            if not dcCycle(serial, ssh):
                logging.info("DC cycle Test:Fail")
                status = 2
                return
        except Exception as e:
            logging.error(e)
    if status != 1 and 2:
        logging.info("<TC014><Result>PM cycle Test:Pass")
        return True


# PXE Test
def pxeTest(serial, ssh, n):
    logging.info("<TC015><Tittle>PXE Test:Start")
    logging.info("<TC015><Description>PXEv4 Test")
    for i in range(n):
        if not Hy5TcLib.force_reset(ssh):
            logging.info("Rebooting SUT Failed.")
            return
        logging.info("Booting to PXE")
        if not serial.hotkey_f12():
            logging.info("Booting to PXE failed.")
            return
        if not serial.waitString('Install', timeout=15):
            logging.info('<TC015><Result>PXE Test:Fail')
            return
    logging.info('<TC015><Result>PXE Test:Pass')
    return True


# Https Test
def httpsTest(serial, ssh, option=r'UEFI HTTPSv4: Network - Port00 SLOT1'):
    logging.info("<TC016><Tittle>Https Test:Start")
    logging.info("<TC016><Description>Https Test")
    key1 = Key.RIGHT + Key.ENTER
    if not toBIOS(serial, ssh):
        logging.info('<TC016><Result>Https Test:Fail')
        return
    serial.send_keys_with_delay(key1)
    if not serial.to_highlight_option(option, timeout=100):
        logging.info('<TC016><Result>Https Test:Fail')
        return
    serial.send_keys(Key.ENTER)
    if not serial.waitString('Start HTTPS Boot over IPv4', timeout=30):
        logging.info('<TC016><Result>Https Test:Fail')
        return
    if not serial.waitString('Shell', timeout=60):
        logging.info('<TC016><Result>Https Test:Fail')
        return
    logging.info('<TC016><Result>Https Test:Pass')
    return True


# USB Test
def usbTest(serial, ssh):
    logging.info("<TC017><Tittle>USB Test:Start")
    logging.info("<TC017><Description>USB Test")
    key1 = Key.RIGHT * 2 + Key.DOWN + Key.ENTER
    key2 = Key.RIGHT + Key.ENTER + Key.DOWN * 2 + Key.ENTER
    if not toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(key1)
    if not serial.waitString('System Time', timeout=15):
        logging.info("Boot to BIOS Configuration Failed")
        return
    logging.info("Boot to BIOS Configuration Pass")
    serial.send_keys_with_delay(key2)
    msg_list = [msg5, msg6, msg7]
    if not verify_setup_options_down(serial, msg_list, 7):
        logging.info('<TC017><Result>USB Test:Fail')
        return
    logging.info('<TC017><Result>USB Test:Pass')
    return True


# Processor/DIMM Test
def ProcessorDIMM(serial, ssh):
    logging.info("<TC019><Tittle>Processor/DIMM Test:Start")
    logging.info("<TC019><Description>CPU/DIMM Test")
    key1 = Key.RIGHT * 2 + Key.DOWN + Key.ENTER
    key2 = Key.RIGHT + Key.DOWN * 8 + Key.ENTER * 2 + Key.DOWN + Key.ENTER
    key3 = Key.DOWN * 4 + Key.ENTER
    if not toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(key1)
    if not serial.waitString('System Time', timeout=15):
        logging.info("Boot to BIOS Configuration Failed")
        logging.info('<TC019><Result>Processor/DIMM Test:Fail')
        return
    logging.info("Boot to BIOS Configuration Pass")
    serial.send_keys_with_delay(key2)
    if not verify_setup_options_down(serial, CPU_info, 20):
        logging.info('<TC019><Result>Processor/DIMM Test:Fail')
        return
    serial.send_keys(Key.ESC * 2)
    serial.send_keys_with_delay(key3)
    if not verify_setup_options_down(serial, DIMM_info, 20):
        logging.info('<TC019><Result>Processor/DIMM Test:Fail')
        return
    logging.info('<TC019><Result>Processor/DIMM Test:Pass')
    return True


# PCIe card Test, TBD
def pcie():
    pass


# chipsec Test
def chipsecTest(serial, ssh, username, pwd):
    # username - OS user name, pwd - OS user password
    logging.info("<TC020><Tittle>chipsec Test:Start")
    logging.info("<TC020><Description>chipsec Test")
    key1 = Key.RIGHT + Key.ENTER
    if not toBIOS(serial, ssh):
        return
    serial.send_keys_with_delay(key1)
    if not serial.waitString('ubuntu', timeout=15):
        return
    serial.send_keys_with_delay(Key.ENTER)
    if not serial.waitString('LTS byo-DH140-V6 ttyS0', timeout=300):
        return
    serial.send_keys_with_delay(Key.ENTER)
    serial.send_data(username)
    serial.send_keys_with_delay(Key.ENTER)
    serial.send_data(pwd)
    serial.send_keys_with_delay(Key.ENTER)
    if not serial.waitString("byo-DH140-V6", timeout=15):
        return
    serial.send_data("cd Desktop/chipsec_murge_0819/")
    serial.send_keys_with_delay(Key.ENTER)
    serial.send_data("sudo python chipsec_main.py")
    serial.send_keys_with_delay(Key.ENTER)
    serial.send_data(pwd)
    serial.send_keys_with_delay(Key.ENTER)
    if serial.waitString('FAILED', timeout=30):
        logging.info('<TC020><Result>chipsec Test:Fail')
        return
    logging.info('<TC020><Result>chipsec Test:Pass')
    return True


# press F2
def pressF2(serial, ssh):
    tc = ('041', 'Setup菜单用户输入界面按F2切换键盘制式', '支持热键配置')
    result = Misc.LogHeaderResult(tc, serial)
    if not Hy5TcLib.force_reset(ssh):
        result.log_fail()
        return
    if not serial.waitString(msg, timeout=300):
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


# Main Func...
def hy5BasicTest(serial, ssh):
    Upgrade_Test(serial)
    Downgrade_Test(serial)
    POST_Test(serial, ssh)
    PM(serial, ssh, 5)
    pxeTest(serial, ssh, 1)
    httpsTest(serial, ssh)
    usbTest(serial, ssh)
    ProcessorDIMM(serial, ssh)
    chipsecTest(serial, ssh, 'byo', '1')
    pressF2(serial, ssh)
    logging.info('Hy5 Basic Function test Completed...')
