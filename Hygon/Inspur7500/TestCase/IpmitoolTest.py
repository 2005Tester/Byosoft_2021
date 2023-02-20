# -*- encoding=utf8 -*-
from Inspur7500.Config import *
from Inspur7500.BaseLib import *
from Inspur7500.Base import *

'''
Ipmitool  case 编号:501~600
'''


@core.test_case(('501', '[TC501]UEFI PXE ONCE Normal', 'UEFI模式下IPMITOOL PXE启动一次(normal)'))
def uefi_pxe_once_nor():
    """
    Name:   UEFI模式下IPMITOOL PXE启动一次(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
            2.IPMITOOL修改UEFI PXE 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入PXE，且启动模式为UEFI
            4.进入U盘
            5.启动模式和最初保持一致
    """
    try:
        assert IpmBootNormal.uefi_pxe_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('502', '[TC502]UEFI SETUP ONCE Normal', 'UEFI模式下IPMITOOL Setup启动一次(normal)'))
def uefi_setup_once_nor():
    """
    Name:   UEFI模式下IPMITOOL SetUp启动一次(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
            2.IPMITOOL修改UEFI SetUp 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入SetUp，且启动模式为UEFI
            4.进入U盘
            5.启动模式和最初保持一致
    """
    try:
        assert IpmBootNormal.uefi_setup_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('503', '[TC503]UEFI HDD ONCE Normal', 'UEFI模式下IPMITOOL 硬盘启动一次(normal)'))
def uefi_hdd_once_nor():
    """
    Name:   UEFI模式下IPMITOOL HDD启动一次(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
            2.IPMITOOL修改UEFI HDD 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入HDD，且启动模式为UEFI
            4.进入U盘
            5.启动模式和最初保持一致
    """
    try:
        assert IpmBootNormal.uefi_hdd_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('504', '[TC504]UEFI USB ONCE Normal', 'UEFI模式下IPMITOOL USB启动一次(normal)'))
def uefi_usb_once_nor():
    """
    Name:   UEFI模式下IPMITOOL USB启动一次(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为PXE
            2.IPMITOOL修改UEFI USB 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入USB，且启动模式为UEFI
            4.进入网络启动
            5.启动模式和最初保持一致
    """
    try:
        assert IpmBootNormal.uefi_usb_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('506', '[TC506]UEFI PXE ALWAYS Normal', 'UEFI模式下IPMITOOL 永久启动到PXE(normal)'))
def uefi_pxe_always_nor():
    """
    Name:   UEFI模式下IPMITOOL PXE启动永久(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
            2.IPMITOOL修改UEFI PXE 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式,第一启动项

    Result: 3.进入PXE，且启动模式为UEFI
            4.进入PXE，且启动模式为UEFI
            5.启动模式为UEFI，第一启动项为PXE
    """
    try:
        assert IpmBootNormal.uefi_pxe_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('507', '[TC507]UEFI SETUP ALWAYS Normal', 'UEFI模式下IPMITOOL 永久启动到SETUP(normal)'))
def uefi_setup_always_nor():
    """
    Name:   UEFI模式下IPMITOOL SetUp启动永久(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
            2.IPMITOOL修改UEFI SetUp 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入SetUp，且启动模式为UEFI
            4.进入SetUp，且启动模式为UEFI
            5.启动模式为UEFI
    """
    try:
        assert IpmBootNormal.uefi_setup_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('508', '[TC508]UEFI HDD ALWAYS Normal', 'UEFI模式下IPMITOOL 永久启动到硬盘(normal)'))
def uefi_hdd_always_nor():
    """
   Name:   UEFI模式下IPMITOOL HDD 启动永久(normal)

   Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
           2.IPMITOOL修改UEFI HDD 启动永久
           3.重启，查看结果
           4.重启，查看结果
           5.进入SetUp查看启动模式,第一启动项

   Result: 3.进入HDD，且启动模式为UEFI
           4.进入HDD，且启动模式为UEFI
           5.启动模式为UEFI，第一启动项为HDD
   """
    try:
        assert IpmBootNormal.uefi_hdd_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('509', '[TC509]UEFI USB ALWAYS Normal', 'UEFI模式下IPMITOOL 永久启动到USB(normal)'))
def uefi_usb_always_nor():
    """
    Name:   UEFI模式下IPMITOOL USB启动永久(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为PXE
            2.IPMITOOL修改UEFI USB 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式,第一启动项

    Result: 3.进入USB，且启动模式为UEFI
            4.进入USB，且启动模式为UEFI
            5.启动模式为UEFI，第一启动项为USB
    """
    try:
        assert IpmBootNormal.uefi_usb_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('510', '[TC510]UEFI ODD ALWAYS Normal', 'UEFI模式下IPMITOOL 永久启动到ODD(normal)'))
def uefi_odd_always_nor():
    """
    Name:   UEFI模式下IPMITOOL ODD启动永久(normal)

    Steps:  1.进入SetUp调整UEFI模式下第一启动项为USB
            2.IPMITOOL修改UEFI ODD 启动永久
            3.进入SetUp查看启动模式,第一启动项

    Result: 3.启动模式为UEFI，第一启动项为ODD
    """
    try:
        assert IpmBootNormal.uefi_odd_always_nor()
        assert SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        logging.error(e)
        return core.Status.Fail


@core.test_case(('511', '[TC511]Legacy PXE ONCE Normal', 'Legacy模式下IPMITOOL启动到PXE一次(normal)'))
def legacy_pxe_once_nor():
    """
    Name:   Legacy模式下IPMITOOL PXE启动一次(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy PXE 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入PXE，且启动模式为Legacy
            4.进入U盘
            5.启动模式与原来保持一致
    """
    try:
        assert IpmBootNormal.legacy_pxe_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('512', '[TC512]Legacy Setup ONCE Normal', 'Legacy模式下IPMITOOL启动到Setup一次(normal)'))
def legacy_setup_once_nor():
    """
    Name:   Legacy模式下IPMITOOL Setup启动一次(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy Setup 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入Setup，且启动模式为Legacy
            4.进入U盘
            5.启动模式与原来保持一致
    """
    try:
        assert IpmBootNormal.legacy_setup_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('513', '[TC513]Legacy USB ONCE Normal', 'Legacy模式下IPMITOOL启动到USB一次(normal)'))
def legacy_usb_once_nor():
    """
    Name:   Legacy模式下IPMITOOL USB启动一次(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为PXE
            2.IPMITOOL修改Legacy USB 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入USB，且启动模式为Legacy
            4.进入网络启动
            5.启动模式与原来保持一致
    """
    try:
        assert IpmBootNormal.legacy_usb_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('514', '[TC514]Legacy HDD ONCE Normal', 'Legacy模式下IPMITOOL启动到HDD一次(normal)'))
def legacy_hdd_once_nor():
    """
    Name:   Legacy模式下IPMITOOL HDD启动一次(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy HDD 启动一次
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入HDD，且启动模式为Legacy
            4.进入U盘
            5.启动模式与原来保持一致
    """
    try:
        assert IpmBootNormal.legacy_hdd_once_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('516', '[TC516]Legacy PXE ALWAYS Normal', 'Legacy模式下IPMITOOL永久启动到PXE(normal)'))
def legacy_pxe_always_nor():
    """
    Name:   Legacy模式下IPMITOOL PXE启动永久(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy PXE 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式，第一启动项

    Result: 3.进入PXE，且启动模式为Legacy
            4.进入PXE，且启动模式为Legacy
            5.启动模式为Legacy，第一启动项为PXE
    """
    try:
        assert IpmBootNormal.legacy_pxe_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('517', '[TC517]Legacy SETUP ALWAYS Normal', 'Legacy模式下IPMITOOL永久启动到SETUP(normal)'))
def legacy_setup_always_nor():
    """
    Name:   Legacy模式下IPMITOOL Setup启动永久(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy SetUp 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式

    Result: 3.进入SetUp，且启动模式为Legacy
            4.进入SetUp，且启动模式为Legacy
            5.启动模式为Legacy
    """
    try:
        assert IpmBootNormal.legacy_setup_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('518', '[TC518]Legacy USB ALWAYS', 'Legacy模式下IPMITOOL永久启动到USB(normal)'))
def legacy_usb_always_nor():
    """
    Name:   Legacy模式下IPMITOOL USB启动永久(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为PXE
            2.IPMITOOL修改Legacy USB 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式，第一启动项

    Result: 3.进入USB，且启动模式为Legacy
            4.进入USB，且启动模式为Legacy
            5.启动模式为Legacy，第一启动项为USB
    """
    try:
        assert IpmBootNormal.legacy_usb_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('519', '[TC519]Legacy HDD ALWAYS Normal', 'Legacy模式下IPMITOOL永久启动到HDD(normal)'))
def legacy_hdd_always_nor():
    """
    Name:   Legacy模式下IPMITOOL HDD启动永久(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy HDD 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看启动模式，第一启动项

    Result: 3.进入HDD，且启动模式为Legacy
            4.进入HDD，且启动模式为Legacy
            5.启动模式为Legacy，第一启动项为HDD
    """
    try:
        assert IpmBootNormal.legacy_hdd_always_nor()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('520', '[TC520]Legacy ODD ALWAYS Normal', 'Legacy模式下IPMITOOL永久启动到ODD(normal)'))
def legacy_odd_always_nor():
    """
    Name:   Legacy模式下IPMITOOL ODD启动永久(normal)

    Steps:  1.进入SetUp调整Legacy模式下第一启动项为USB
            2.IPMITOOL修改Legacy ODD 启动永久
            3.进入SetUp查看启动模式，第一启动项

    Result: 3.启动模式为Legacy，第一启动项为ODD
    """
    try:
        assert IpmBootNormal.legacy_odd_always_nor()
        assert SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        logging.error(e)
        return core.Status.Fail


@core.test_case(('521', '[TC521]UEFI PXE ONCE Specific', 'UEFI模式下IPMITOOL PXE启动一次(specific)'))
def uefi_pxe_once_spe():
    """
    Name:   UEFI模式下IPMITOOL PXE启动一次(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为内置Shell
            2.IPMITOOL修改PXE 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入PXE
            4.进入内置Shell
    """
    try:
        assert IpmBootSpecific.uefi_pxe_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('522', '[TC522]UEFI SETUP ONCE Specific', 'UEFI模式下IPMITOOL Setup启动一次(specific)'))
def uefi_setup_once_spe():
    """
    Name:   UEFI模式下IPMITOOL Setup启动一次(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为USB
            2.IPMITOOL修改SetUp 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入SetUp
            4.进入U盘
    """
    try:
        assert IpmBootSpecific.uefi_setup_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('523', '[TC523]UEFI HDD ONCE Specific', 'UEFI模式下IPMITOOL 硬盘启动一次(specific)'))
def uefi_hdd_once_spe():
    """
    Name:   UEFI模式下IPMITOOL 硬盘启动一次(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为内置Shell
            2.IPMITOOL修改HDD 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入系统
            4.进入内置Shell
    """
    try:
        assert IpmBootSpecific.uefi_hdd_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('524', '[TC524]UEFI USB ONCE Specific', 'UEFI模式下IPMITOOL USB启动一次(specific)'))
def uefi_usb_once_spe():
    """
    Name:   UEFI模式下IPMITOOL USB启动一次(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为硬盘
            2.IPMITOOL修改USB 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入U盘
            4.进入系统
    """
    try:
        assert IpmBootSpecific.uefi_usb_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('526', '[TC526]UEFI PXE ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到PXE(specific)'))
def uefi_pxe_always_spe():
    """
    Name:   UEFI模式下IPMITOOL 永久启动到PXE(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为内置Shell
            2.IPMITOOL修改PXE 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看第一启动项

    Result: 3.进入PXE
            4.进入PXE
            5.第一启动项为PXE
    """
    try:
        assert IpmBootSpecific.uefi_pxe_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('527', '[TC527]UEFI SETUP ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到SETUP(specific)'))
def uefi_setup_always_spe():
    """
    Name:   UEFI模式下IPMITOOL 永久启动到SETUP(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为U盘
            2.IPMITOOL修改SetUp 启动永久
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入SetUp
            4.进入SetUp

    """
    try:
        assert IpmBootSpecific.uefi_setup_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('528', '[TC528]UEFI HDD ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到硬盘(specific)'))
def uefi_hdd_always_spe():
    """
    Name:   UEFI模式下IPMITOOL 永久启动到硬盘(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为内置Shell
            2.IPMITOOL修改硬盘 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看第一启动项

    Result: 3.进入HDD
            4.进入HDD
            5.第一启动项为HDD
    """
    try:
        assert IpmBootSpecific.uefi_hdd_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('529', '[TC529]UEFI USB ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到USB(specific)'))
def uefi_usb_always_spe():
    """
    Name:   UEFI模式下IPMITOOL 永久启动到USB(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为硬盘
            2.IPMITOOL修改USB 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看第一启动项

    Result: 3.进入USB
            4.进入USB
            5.第一启动项为USB
    """
    try:
        assert IpmBootSpecific.uefi_usb_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('530', '[TC530]UEFI ODD ALWAYS Specific', 'UEFI模式下IPMITOOL 永久启动到ODD(specific)'))
def uefi_odd_always_spe():
    """
    Name:   UEFI模式下IPMITOOL 永久启动到ODD(specific)

    Steps:  1.进入SetUp修改UEFI模式，第一启动项为PXE
            2.IPMITOOL修改ODD 启动永久
            3.进入SetUp查看第一启动项

    Result: 3.第一启动项为ODD
    """
    try:
        assert IpmBootSpecific.uefi_odd_always_spe()
        assert SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        logging.error(e)
        return core.Status.Fail


@core.test_case(('531', '[TC531]Legacy PXE ONCE Specific', 'Legacy模式下IPMITOOL启动到PXE一次(specific)'))
def legacy_pxe_once_spe():
    """
    Name:   Legacy模式下IPMITOOL PXE启动一次(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为USB
            2.IPMITOOL修改PXE 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入PXE
            4.进入内置Shell
    """
    try:
        assert IpmBootSpecific.legacy_pxe_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('532', '[TC532]Legacy Setup ONCE Specific', 'Legacy模式下IPMITOOL启动到Setup一次(specific)'))
def legacy_setup_once_spe():
    """
    Name:   Legacy模式下IPMITOOL Setup启动一次(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为USB
            2.IPMITOOL修改SetUp 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入SetUp
            4.进入U盘
    """
    try:
        assert IpmBootSpecific.legacy_setup_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('533', '[TC533]Legacy USB ONCE Specific', 'Legacy模式下IPMITOOL启动到USB一次(specific)'))
def legacy_usb_once_spe():
    """
    Name:   Legacy模式下IPMITOOL USB启动一次(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为PXE
            2.IPMITOOL修改USB 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入U盘
            4.进入PXE
    """
    try:
        assert IpmBootSpecific.legacy_usb_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('534', '[TC534]Legacy HDD ONCE Specific', 'Legacy模式下IPMITOOL启动到HDD一次(specific)'))
def legacy_hdd_once_spe():
    """
    Name:   Legacy模式下IPMITOOL 硬盘启动一次(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为USB
            2.IPMITOOL修改HDD 启动一次
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入系统
            4.进入USB
    """
    try:
        assert IpmBootSpecific.legacy_hdd_once_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('536', '[TC536]Legacy PXE ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到PXE(specific)'))
def legacy_pxe_always_spe():
    """
    Name:   Legacy模式下IPMITOOL 永久启动到PXE(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为USB
            2.IPMITOOL修改PXE 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看第一启动项

    Result: 3.进入PXE
            4.进入PXE
            5.第一启动项为PXE
    """
    try:
        assert IpmBootSpecific.legacy_pxe_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('537', '[TC537]Legacy SETUP ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到SETUP(specific)'))
def legacy_setup_always_spe():
    """
    Name:   Legacy模式下IPMITOOL 永久启动到SETUP(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为U盘
            2.IPMITOOL修改SetUp 启动永久
            3.重启，查看结果
            4.重启，查看结果

    Result: 3.进入SetUp
            4.进入SetUp

    """
    try:
        assert IpmBootSpecific.legacy_setup_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('538', '[TC538]Legacy USB ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到USB(specific)'))
def legacy_usb_always_spe():
    """
    Name:   Legacy模式下IPMITOOL 永久启动到USB(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为PXE
            2.IPMITOOL修改USB 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看第一启动项

    Result: 3.进入USB
            4.进入USB
            5.第一启动项为USB
    """
    try:
        assert IpmBootSpecific.legacy_usb_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('539', '[TC539]Legacy HDD ALWAYS Specific', 'Legacy模式下IPMITOOL永久启动到HDD(specific)'))
def legacy_hdd_always_spe():
    """
    Name:   Legacy模式下IPMITOOL 永久启动到硬盘(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为USB
            2.IPMITOOL修改硬盘 启动永久
            3.重启，查看结果
            4.重启，查看结果
            5.进入SetUp查看第一启动项

    Result: 3.进入HDD
            4.进入HDD
            5.第一启动项为HDD
    """
    try:
        assert IpmBootSpecific.legacy_hdd_always_spe()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('540', '[TC540]Legacy ODD ALWAYS Sepcific', 'Legacy模式下IPMITOOL永久启动到ODD(specific)'))
def legacy_odd_always_spe():
    """
    Name:   Legacy模式下IPMITOOL 永久启动到ODD(specific)

    Steps:  1.进入SetUp修改Legacy模式，第一启动项为PXE
            2.IPMITOOL修改ODD 启动永久
            3.进入SetUp查看第一启动项

    Result: 3.第一启动项为ODD
    """
    try:
        assert IpmBootSpecific.legacy_odd_always_spe()
        assert SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        return core.Status.Pass
    except Exception as e:
        SetUpLib.boot_to_setup()
        SetUpLib.default_save()
        logging.error(e)
        return core.Status.Fail


@core.test_case(('541', '[TC541]FRB2 Watchdog', 'FRB2 Watchdog'))
def frb2_watchdog(oem=False):
    """
    Name:   FRB2 Watchdog

    Steps:  1.SetUp下关闭FRB2 Watchdog，Ipmi工具验证
            2.SetUp下打开FRB2 Watchdog，设置重启，10分钟，Ipmi工具验证
            3.SetUp下打开FRB2 Watchdog，设置关闭电源，30分钟，Ipmi工具验证
            4.SetUp下打开FRB2 Watchdog，设置重启，5分钟，Ipmi工具验证
            5.F12进入网络启动，Ipmi工具验证FRB2 Watchdog状态
            6.IPMITOOL UEFI PXE 启动一次，Ipmi工具验证FRB2 Watchdog状态
            7.IPMITOOL Legacy PXE 启动一次，Ipmi工具验证FRB2 Watchdog状态
            8.设置SetUp管理员密码，POST输入密码界面，Ipmi工具验证FRB2 Watchdog状态，删除管理员密码
            9.设置硬盘密码，POST输入硬盘密码界面，Ipmi工具验证FRB2 Watchdog状态，删除硬盘密码
    Result: 1/2/3/4:Ipmi工具与SetUp设置的一致
            5/6/7/8/9:自动禁用FRB2
    """
    try:
        assert Ipmitool.frb2_watchdog(oem)

        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('542', '[TC542]OS Watchdog', 'OS Watchdog'))
def os_watchdog():
    """
    Name:   OS Watchdog

    Steps:  1.SetUp下打开OS Watchdog,关闭电源，10分钟，进入系统，Ipmi工具验证
            2.SetUp下打开OS Watchdog,重启，30分钟，进入系统，Ipmi工具验证
            3.SetUp下打开OS Watchdog,重启，5分钟，进入系统，Ipmi工具验证
            4.SetUp下关闭OS Watchdog，Ipmi工具验证

    Result: 1/2/3/4:Ipmi工具与SetUp设置的一致
    """
    try:
        assert Ipmitool.os_watchdog()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('543', '[TC543]Power Loss', '电源丢失策略'))
def power_loss():
    """
    Name:   电源丢失策略

    Steps:  1.Setup下修改电源丢失策略为上电,Ipmi工具验证
            2.Setup下修改电源丢失策略为上次状态,Ipmi工具验证
            3.Setup下修改电源丢失策略为保持关闭,Ipmi工具验证
            4.Ipmi修改电源丢失策略为上电,SetUp验证
            5.Ipmi修改电源丢失策略为上次状态,SetUp验证
            6.Ipmi修改电源丢失策略为保持关闭,SetUp验证

    Result: 1/2/3/4/5/6:两者一致
    """
    try:
        assert Ipmitool.power_loss()
        BmcLib.power_off()
        time.sleep(5)
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('544', '[TC544]OEM', 'OEM命令获取和修改Setup选项'))
def oem():
    """
    Name:   OEM命令获取和修改Setup选项

    Steps:  1.Ipmi使用OEM命令修改SetUp选项
            2.重启，IPmi读取的值是否为修改的值

    Result: 2.读取的值为修改的值
    """
    try:
        assert Ipmitool.oem()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('545', '[TC545]BMC User Test', 'BMC User Test'))
def bmc_user():
    """
    Name:   BMC User Test

    Steps:  1.SetUp下新增BMC用户，输入不符合要求的用户名
            2.SetUp下新增一个BMC用户
            3.Setup下新增bmc用户时，输入存在的用户名
            4.Ipmi 查看user list 中是否有步骤2新增的BMC用户
            5.SetUp下修改用户时，输入错误的用户密码
            6.SetUp下修改用户时，输入正确的用户密码，输入符合要求的新密码
            7.Ipmi验证密码是否修改成功
            8.SetUp下依次更改用户权限为回叫，用户，操作人，管理员，无法访问，Ipmi工具验证
            9.SetUp下删除该用户，Ipmi 查看user list 是否有该用户
            10.SetUp下新建用户
            11.修改用户时，输错用户密码4次，第5次输入正确密码
            12.修改用户时，输错用户密码5次，第6次输入正确密码
            13.Ipmi增加用户，SetUp下验证
            14.Ipmi更改用户状态为，Enabled,Disabled，SetUp下验证
            15.Ipmi修改用户密码，SetUp下验证
            16.Ipmi依次更改用户权限为回叫，用户，操作人，管理员，无法访问，Setup验证

    Result: 1/3.新增用户名失败
            4.user list 中有新增的用户
            5.提示密码错误
            6.用户密码修改成功
            7.Ipmi验证密码修改成功
            8.Ipmi验证成功
            9.SetUp下删除用户成功，user list中没有该用户
            11.提示密码正确
            12.提示密码错误
            13.SetUp下验证成功
            14.SetUp下验证成功
            15.SetUp下验证成功
            16.SetUp下验证成功
    """
    try:
        assert Ipmitool.bmc_user()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('546', '[TC546]Ipmi change SOL', 'Ipmi命令打开关闭SOL'))
def sol():
    """
    Name:   Ipmi命令打开关闭SOL

    Steps:  1.SetUp下关闭SOL，Ipmi验证
            2.Ipmi打开SOL，SetUp下验证
            3.Ipmi关闭SOL，SetUp下验证
            4.SetUp下打开SOL，Ipmi验证

    Result: 1/2/3/4:两者保持一致

    """
    try:
        assert Ipmitool.sol()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('547', '[TC547]BMC System Log', 'BMC 系统日志'))
def bmc_system_log():
    """
    Name:   BMC系统日志

    Steps:  1.SetUp下收集系统日志与Ipmi收集的系统日志对比
            2.SetUp下清除系统日志，查看SetUp下系统日志和Ipmi的系统日志

    Result: 1.SetUp下收集系统日志与Ipmi收集的系统日志相同
            2.SetUp下收集系统日志与Ipmi收集的系统日志相同且只有一条
    """
    try:
        assert Ipmitool.bmc_system_log()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('548', '[TC548]FRU Message Confirm', 'FRU 信息验证'))
def fru():
    """
    Name:   FRU信息

    Steps:  1.SetUp下的FRU与Ipmi的FRU信息对比

    Result: 1..SetUp下的FRU与Ipmi的FRU信息相同
    """
    try:
        assert Ipmitool.fru()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


@core.test_case(('549','[TC549]SOL Terminal Test','SOL终端测试'))
def sol_terminal():
    """
    Name:   SOL终端测试

    Steps:  遍历UTF-8,VT100+,VT100
            1.打开SOL
            2.SOL进入F11启动菜单,Shell,DOS,F12网络启动,SetUp
            3.验证ESC,F1,F9,F10功能键

    Result: 1.SOL打开成功
            2.成功进入F11启动菜单,Shell,DOS,F12网络启动,SetUp
            3.ESC,F1,F9,F10功能键正常
    """
    try:
        assert Ipmitool.sol_terminal()
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
    finally:
        BmcLib.change_bios_value(['BootMode:UEFI'])
