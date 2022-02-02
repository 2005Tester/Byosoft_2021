import logging
import time
from batf.Report import ReportGen
from Inspur7500.Config.PlatConfig import Key
from Inspur7500.BaseLib import BmcLib,SetUpLib
from Inspur7500.Base import SetUp
from Inspur7500.Config import SutConfig
from batf import core



'''
SetUp case 编号: 601~700
'''



@core.test_case(('604','[TC604]Interface Information','界面信息'))
def Interface_information():

    try:
        assert SetUp.Interface_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('605','[TC605]Onboard Ethernet Controller','修改板载网卡配置'))
def Onboard_Ethernet_Controller():

    try:
        assert SetUp.Onboard_Ethernet_Controller()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('606','[TC606]Wake Online','网络唤醒'))
def wake_online():

    try:
        assert SetUp.wake_online()
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    


@core.test_case(('607','[TC607]USB Mass Storage Support','USB存储设备支持'))
def usb_mass_storage_support():

    try:
        assert SetUp.usb_mass_storage_support()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('608','[TC608]USB Port Configuration','USB端口配置'))
def usb_port_configuration():

    try:
        assert SetUp.usb_port_configuration()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('609','[TC609]HDD Bind','硬盘绑定'))
def HDD_Bind():

    try:
        assert SetUp.HDD_bind()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN,SutConfig.Sup.HDD_BIND3,18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('610','[TC610]Secure Boot','安全启动'))
def secure_boot():

    try:
       assert SetUp.secure_boot()
       return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('611','[TC611]Quiet Boot','安静启动'))
def quiet_boot():

    try:
        assert SetUp.quiet_boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail

    

@core.test_case(('612','[TC612]User Wait Time','用户等待时间'))
def user_wait_time():

    try:
        assert SetUp.user_wait_time()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('615','[TC615]Spi BIOS Lock','SPI BIOS　锁住'))
def spi_bios_lock():

    try:
       assert SetUp.spi_bios_lock()
       return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('616','[TC616]IOMMU','IOMMU'))
def iommu():

    try:
        assert SetUp.iommu()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('617','[TC617]SVM','SVM'))
def svm():

    try:
        assert SetUp.svm()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('618','[TC618]SR-IOV','SR-IOV'))
def sriov():

    try:
        assert SetUp.sriov()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('621','[TC621]Memory Speed','内存频率'))
def memory_speed():

    try:
        assert SetUp.memory_speed()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('622','[TC622]Save Change by ESC','通过ESC键保存设置'))
def save_change_esc():

    try:
        assert SetUp.save_change_esc()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('623','[TC623]Save Change','保存修改'))
def save_change():

    try:
        assert SetUp.save_change()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('624','[TC624]Save And Exit','保存并且退出'))
def save_and_exit():

    try:
        assert SetUp.save_and_exit()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('625','[TC625]Exit Without Save','不保存并且退出'))
def exit_without_save():

    try:
        assert SetUp.exit_without_save()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('626','[TC626]Load Default','恢复初始值'))
def load_default():

    try:
        assert SetUp.load_default()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('627','[TC627]Load Default By F9','F9快捷键恢复初始值'))
def load_default_f9():

    try:
        assert SetUp.load_default_f9()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('628','[TC628]Check Default after Update BIOS','全刷BIOS后默认值检查'))
def check_default_bios():

    try:
        assert SetUp.check_default_bios()
        BmcLib.power_off()
        return core.Status.Pass
    except Exception as e:
        BmcLib.power_off()
        logging.error(e)
        return core.Status.Fail



@core.test_case(('629', '[TC629]SATA Controller Configuration', 'SATA 控制器配置'))
def sata_controller():

    try:
        assert SetUp.sata_controller()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('630', '[TC630]TPM', 'TPM'))
def tpm():

    try:
        assert SetUp.tpm()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('631', '[TC631]Boot Logo', '开机Logo'))
def boot_logo():
    try:
        assert SetUp.boot_logo()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('632', '[TC632]Link Relation', '联动关系测试'))
def link_relation():
    try:
        assert SetUp.link_relation()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail



@core.test_case(('633', '[TC633]Option Rom', 'OPtion Rom'))
def option_rom():
    try:
        assert SetUp.option_rom()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_UEFI, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.error(e)
        return core.Status.Fail