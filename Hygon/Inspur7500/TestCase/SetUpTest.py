# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *
'''
SetUp case 编号:601~700
'''


@core.test_case(('604', '[TC604]Interface Information', '界面信息'))
def Interface_information():
    """
    Name:   界面信息

    Steps:  1.检查SetUp界面是否包含要求的

    """
    try:
        assert SetUp.Interface_information()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('605', '[TC605]Onboard Ethernet Controller', '修改板载网卡配置'))
def Onboard_Ethernet_Controller(oem=False):
    """
    Name:   修改板载网卡配置

    Steps:  1.关闭板载网卡
            2.检查启动菜单是否有板载网卡启动项，SetUpPCIE设备列表是否有板载网卡
            3.打开板载网卡

    Result: 2.启动菜单没有板载网卡启动项，PCIE设备列表没有板载网卡

    """
    try:
        assert SetUp.Onboard_Ethernet_Controller(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('606', '[TC606]Wake Online', '网络唤醒'))
def wake_online(oem=False):
    """
    Name:   网络唤醒

    Steps:  1.SetUp下关闭网络唤醒
            2.启动到系统，关机
            3.使用工具网络唤醒机器
            4.SetUp下打开网络唤醒
            5.启动到系统，关机
            6.使用工具网络唤醒机器

    Result: 3.无法唤醒
            6.唤醒成功
    """
    try:
        assert SetUp.wake_online(oem)
        return core.Status.Pass

    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('607', '[TC607]USB Mass Storage Support', 'USB存储设备支持'))
def usb_mass_storage_support(oem=False):
    """
    Name:   USB存储设备支持

    Steps:  1.SetUp下关闭USB存储设备支持
            2.查看启动菜单
            3.进入OS
            4.打开USB存储设备支持
            5.查看启动菜单

    Result: 2.启动菜单没有USB
            3.系统下能正常识别U盘
            5.启动菜单有USB

    """
    try:
        assert SetUp.usb_mass_storage_support(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('608', '[TC608]USB Port Configuration', 'USB端口配置'))
def usb_port_configuration(oem=False):
    """
    Name:   USB端口配置

    Steps:  1.打开前置USB端口，关闭后置USB端口，查看USB设备列表
            2.关闭前置USB端口，打开后置USB端口，查看USB设备列表
            3.关闭前置USB端口，关闭后置USB端口，查看USB设备列表

    Result: 1.USB设备列表只有前置USB口的信息
            2.USB设备列表只有后置USB口的信息
            3.USB设备列表没有USB信息
    """
    try:
        assert SetUp.usb_port_configuration(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('609', '[TC609]HDD Bind', '硬盘绑定'))
def HDD_Bind():
    """
    Name:   硬盘绑定

    Steps:  1.绑定第一个硬盘
            2.启动菜单依次进入两块硬盘
            3.绑定第二个硬盘
            4.启动菜单依次进入两块硬盘

    Result: 2.可以进入第一个硬盘，无法进入第二个硬盘
            4.可以进入第二个硬盘，无法进入第一个硬盘
    """
    try:
        assert SetUp.HDD_bind()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.HDD_BIND3, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        logging.error(e)
        return core.Status.Fail


@core.test_case(('610', '[TC610]Secure Boot', '安全启动'))
def secure_boot():
    """
    Name:   安全启动

    Steps:  1.打开安全启动
            2.使用刷新工具刷新BIOS

    Result: 2.安全启动打开无法使用刷新工具刷新BIOS

    """
    try:
        assert SetUp.secure_boot()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('611', '[TC611]Quiet Boot', '安静启动'))
def quiet_boot(oem=False):
    """
    Name:   安静启动

    Steps:  1.打开安静启动
            2.POST界面没有信息展示

    """
    try:
        assert SetUp.quiet_boot(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('612', '[TC612]User Wait Time', '用户等待时间'))
def user_wait_time(oem=False):
    """
    Name:   用户等待时间

    Steps:  1.随机设置用户等待时间的值
            2.查看POST界面等待时间是否为设定的值

    Result: 2.POST界面等待时间是设定的值
    """
    try:
        assert SetUp.user_wait_time(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('615', '[TC615]Spi BIOS Lock', 'SPI BIOS　锁住'))
def spi_bios_lock(oem=False):
    """
    Name:   SPI BIOS 锁住

    Steps:  1.SetUp下打开SPI BIOS　锁住
            2.Shell下工具刷新BIOS
            3.SetUp下关闭SPI BIOS　锁住
            4.Shell下工具刷新BIOS

    Result: 2.无法刷新BIOS
            4.成功刷新BIOS

    """
    try:
        assert SetUp.spi_bios_lock(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('616', '[TC616]IOMMU', 'IOMMU'))
def iommu(oem=False):
    """
    Name:   IOMMU

    Steps:  1.SetUp下关闭IOMMU
            2.OS下检查
            3.SetUp下打开IOMMU
            4.OS下检查

    Result: 2.OS内核打印没有iommu
            4.OS内核打印有iommu
    """
    try:
        assert SetUp.iommu(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('617', '[TC617]SVM', 'SVM'))
def svm(oem=False):
    """
    Name:   SVM

    Steps:  1.SetUp下关闭SVM
            2.OS下检查
            3.SetUp下打开SVM
            4.OS下检查

    Result: 2.OS内核打印没有SVM
            4.OS内核打印有SVM
    """
    try:
        assert SetUp.svm(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('618', '[TC618]SR-IOV', 'SR-IOV'))
def sriov(oem=False):
    """
    Name:   SR-IOV

    Steps:  1.SetUp下打开SR-IOV总开关
            2.OS下验证
            3.SetUp下关闭SR-IOV总开关
            4.OS下验证
            5.SetUp下打开SR-IOV总开关，依次只打开单独网卡的SR-IOV功能
            6.OS下验证

    Result: 2.所有网卡都能虚拟出虚拟网卡
            4.所有网卡都不能虚拟出虚拟网卡
            6.只有打开的网卡能虚拟出虚拟网卡，其他网卡不能虚拟出虚拟网卡
    """

    try:
        assert SetUp.sriov(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('621', '[TC621]Memory Speed', '内存频率'))
def memory_speed():
    """
    Name:   内存频率

    Steps:  遍历所有的频率
            1.SetUp下修改内存频率为指定值
            2.检查SetUp下内存信息中内存频率是否为修改的值

    Result: 2.内存信息中内存频率与修改的值相同
    """
    try:
        assert SetUp.memory_speed()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('622', '[TC622]Save Change by ESC', '通过ESC键保存设置'))
def save_change_esc():
    """
    Name:   ESC键保存设置

    Steps:  1.SetUp下修改选项值
            2.ESC键保存设置
            3.进入SetUp查看值是否修改成功

    Result: 3.修改成功
    """
    try:
        assert SetUp.save_change_esc()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('623', '[TC623]Save Change', '保存修改'))
def save_change():
    """
    Name:   保存修改

    Steps:  1.SetUp下修改选项值
            2.退出菜单保存修改，重启
            3.进入SetUp查看值是否修改成功

    Result: 3.修改成功
    """
    try:
        assert SetUp.save_change()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('624', '[TC624]Save And Exit', '保存并且退出'))
def save_and_exit():
    """
    Name:   保存并且退出

    Steps:  1.SetUp下修改选项值
            2.退出菜单，保存并且退出
            3.进入SetUp查看值是否修改成功

    Result: 3.修改成功
    """
    try:
        assert SetUp.save_and_exit()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('625', '[TC625]Exit Without Save', '不保存并且退出'))
def exit_without_save():
    """
    Name:   不保存并且退出

    Steps:  1.SetUp下修改选项值
            2.退出菜单，不保存并且退出
            3.进入SetUp查看值是否修改成功

    Result: 3.修改失败
    """
    try:
        assert SetUp.exit_without_save()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('626', '[TC626]Load Default', '恢复初始值'))
def load_default():
    """
    Name:   恢复初始值

    Steps:  1.SetUp下修改选项值，保存重启到SetUp
            2.退出菜单，恢复初始值
            3.进入SetUp查看是否恢复默认值

    Result: 3.恢复默认值
    """
    try:
        assert SetUp.load_default()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('627', '[TC627]Load Default By F9', 'F9快捷键恢复初始值'))
def load_default_f9():
    """
    Name:   恢复初始值

    Steps:  1.SetUp下修改选项值，保存重启到SetUp
            2.F9恢复初始值
            3.进入SetUp查看是否恢复默认值

    Result: 3.恢复默认值
    """
    try:
        assert SetUp.load_default_f9()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('628', '[TC628]F9,IPMITOOL,Update BIOS Check Default', 'F9,IPMITOOL,全刷BIOS默认值检查'))
def check_default_bios():
    """
    Name:   F9,IPMITOOL,全刷BIOS默认值检查

    Steps:  1.F9恢复默认值
            2.IPMITOOL恢复默认值
            3.全刷BIOS默认值
            4.三者是否相同

    Result: 4.相同
    """
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
    """
    Name:   SATA控制器配置

    Steps:  1.关闭Asmedia控制器1061R_A
            2.检查SATA配置
            3.关闭Asmedia控制器1061R_B
            4.检查SATA配置
            5.关闭Asmedia控制器1061R_A和Asmedia控制器1061R_B
            6.检查SATA配置

    Result: 2.SATA配置下SATA端口被关闭
            4.SATA配置下M.2端口被关闭
            6.SATA配置下SATA端口和M.2端口都被关闭
    """
    try:
        assert SetUp.sata_controller()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('630', '[TC630]TPM', 'TPM'))
def tpm():
    """
    Name:   TPM

    Steps:  1.设置TPM为DTPM
            2.检查SetUp下DTPM Version
            3.清除TPM2
            4.POST阶段检查ESC,F12行为，系统下是否显示DTPM，一次启动之后TPM2操作的值
            5.设置TPM为FTPM
            6.检查SetUp下FTPM Version
            7.清除TPM2
            8.POST阶段检查ESC,F12行为，系统下是否显示FTPM，一次启动之后TPM2操作的值

    Result: 2.DTPM 版本显示正确
            4.ESC继续启动，F12重启，系统下显示DTPM，一次启动之后TPM2操作变为无动作
            4.FTPM 版本显示正确
            8.ESC继续启动，F12重启，系统下显示FTPM，一次启动之后TPM2操作变为无动作

    """
    try:
        assert SetUp.tpm()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('631', '[TC631]Boot Logo', '开机Logo'))
def boot_logo(oem=False):
    """
    Name:   开机Logo

    Steps:  1.隐藏开机Logo
            2.检查POST是否出现Logo，type1,type2,type3,SetUp界面

    Result: 2.POST隐藏Logo，Smbios type1,type2,type3,不显示制造商，SetUp不显示制造商
    """
    try:
        assert SetUp.boot_logo(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('632', '[TC632]Link Relation', '联动关系测试'))
def link_relation(oem=False):
    """
    Name:   联动关系

    Steps:  1.启动模式Legacy,UEFI HII 配置菜单隐藏
            2.Legacy 下打开安全启动,启动模式变为UEFI
            3.启动模式更改为Legacy,安全启动关闭
            4.网络协议栈关闭,UEFI HII 配置菜单不显示,Ipv4,Ipv6,VLAN

    """
    try:
        assert SetUp.link_relation(oem)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('633', '[TC633]Option Rom', 'OPtion Rom'))
def option_rom(oem=False):
    """
    Name:   Option Rom

    Steps:  1.打开OPtion Rom
            2.关闭Option Rom

    Result: 1.Option Rom中有板载网卡信息，Asmedia信息
            2.Option Rom中没有板载网卡信息，Asmedia信息
    """
    try:
        assert SetUp.option_rom(oem)
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sup.BOOT_UEFI, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(3)
        logging.error(e)
        return core.Status.Fail


@core.test_case(('634', '[TC634]TPM附加测试', 'TPM附加测试'))
def tpm_plus():
    """
    Name:   TPM附加测试

    Steps:  1.设置TPM为FTPM,关闭TPM State
            2.关闭Platform Hierarchy
            3.关闭'Platform Hierarchy', 'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'
            4.依次修改PPI,Rev,重启进SetUp检查是否为修改的值
            5.全选PCR Bank,POST显示，ESC,F12是否正常
            6.依次修改所有能设置的PCR Bank,POST显示，ESC,F12是否正常
            7.设置TPM为DTPM,关闭TPM State
            8.关闭Platform Hierarchy
            9.关闭'Platform Hierarchy', 'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'
            10.依次修改PPI,Rev,重启进SetUp检查是否为修改的值
            11.全选PCR Bank,POST显示，ESC,F12是否正常
            12.依次修改所有能设置的PCR Bank,POST显示，ESC,F12是否正常

    Result: 1.关闭TPM State,底下所有选项自动隐藏，SetUp显示FTPM信息
            2.'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'置灰
            3.正常启动
            4.修改成功
            5.POST显示全部PCR BANK，ESC继续启动，F12重启
            6.POST显示设置的PCR BANK，ESC继续启动，F12重启
            7.关闭TPM State,底下所有选项自动隐藏，SetUp显示DTPM信息
            8.'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'置灰
            9.正常启动
            10.修改成功
            11.POST显示全部PCR BANK，ESC继续启动，F12重启
            12.POST显示设置的PCR BANK，ESC继续启动，F12重启
    """
    try:
        assert SetUp.tpm_plus()
        return core.Status.Pass
    except Exception as e:
        BmcLib.init_sut()
        if SetUpLib.wait_message(SutConfig.Sup.POST_MSG,100):
            SetUpLib.send_key(Key.F12)
        logging.error(e)
        return core.Status.Fail



@core.test_case(('635', '[TC635]TPCM', 'TPCM'))
def tpcm():
    try:

        return SetUp.tpcm()
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
