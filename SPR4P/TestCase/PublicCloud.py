from SPR4P.Config import *
from SPR4P.BaseLib import *

####################################
# PublicCloud Test Case
# TC 2900-2902
####################################


@core.test_case(("2900", "[TC2900] Testcase_CstateOsIndicator_001", "C状态标志位设置菜单检查"))
def Testcase_CstateOsIndicator_001():
    """
    Name:       C状态标志位设置菜单检查
    Condition:  1、默认配置。
    Steps:      1、启动进Setup菜单，C状态控制界面下查看是否提供C状态标志位设置开关，可选值及默认值，有结果A；
    Result:     A：提供C1E OS Indicator、C6 OS Indicator两个控制开关，Enabled、Disabled可选，默认均Disabled。
    Remark:
    """
    try:
        assert SetUpLib.boot_to_page(Msg.PAGE_ADVANCED)
        assert SetUpLib.enter_menu(Msg.PATH_CSTATE_CTL, Key.DOWN, 20, Msg.CPU_C_STATE)
        assert SetUpLib.set_option_value(Msg.MWAIT, Msg.ENABLE)
        assert SetUpLib.set_option_value(Msg.C6_REPORT, Msg.ENABLE)
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.C1E_OS), [Msg.ENABLE, Msg.DISABLE])
        assert MiscLib.same_values(SetUpLib.get_all_values(Msg.C6_OS), [Msg.ENABLE, Msg.DISABLE])
        return core.Status.Pass
    except Exception as e:
        logging.error(e)
        return core.Status.Fail


# @core.test_case(("2901", "[TC2901] Testcase_CstateOsIndicator_005", "C1E状态标志位功能测试"))
# def Testcase_CstateOsIndicator_005():
#     """
#     Name:       C1E状态标志位功能测试
#     Condition:  1、Enable Monitor MWAIT已开启；
#                 2、Enhanced Halt State (C1E)已开启；
#                 3、已知C1E标志位对应内存地址，假定为a（V7为0x770B499E，获取方法见备注）；
#                 4、Windows系统及RW工具已安装。
#     Steps:      1、启动进Setup菜单，C状态控制界面下设置C1E OS Indicator为Enabled，F10保存重启；
#                 2、启动进Windows系统，RW工具读取Memory，查看地址a对应数值，有结果A；
#                 3、启动进Setup菜单，C状态控制界面下设置C1E OS Indicator为Disabled，F10保存重启；
#                 4、启动进Windows系统，RW工具读取Memory，查看地址a对应数值，有结果B。
#     Result:     A：对应数值为01；
#                 B：对应数值为00。
#     Remark:     1、对应地址获取方法步骤如下：
#                 a)、Windows系统下RW读取ACPI的DSDT表；
#                 b)、搜索“GNVS”关键字查找到存储区域的起始地址x及长度y（OperationRegion的第三、第四个参数）
#                 c)、x+y-1为C6状态标志位的存储位置
#                 d)、x+y-2为C1E状态标志位的存储位置
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()


# @core.test_case(("2902", "[TC2902] Testcase_CstateOsIndicator_006", "C6状态标志位功能测试"))
# def Testcase_CstateOsIndicator_006():
#     """
#     Name:       C6状态标志位功能测试
#     Condition:  1、Enable Monitor MWAIT已开启；
#                 2、CPU C6 report为已开启；
#                 3、已知C6标志位对应内存地址，假定为a（V7为0x770B499F，获取方法见备注）；
#                 4、Windows系统及RW工具已安装。
#     Steps:      1、启动进Setup菜单，C状态控制界面下设置C6 OS Indicator为Enabled，F10保存重启；
#                 2、启动进Windows系统，RW工具读取Memory，查看地址a对应数值，有结果A；
#                 3、启动进Setup菜单，C状态控制界面下设置C6 OS Indicator为Disabled，F10保存重启；
#                 4、启动进Windows系统，RW工具读取Memory，查看地址a对应数值，有结果B。
#     Result:     A：对应数值为01；
#                 B：对应数值为00。
#     Remark:     1、对应地址获取方法步骤如下：
#                 a)、Windows系统下RW读取ACPI的DSDT表；
#                 b)、搜索“GNVS”关键字查找到存储区域的起始地址x及长度y（OperationRegion的第三、第四个参数）
#                 c)、x+y-1为C6状态标志位的存储位置
#                 d)、x+y-2为C1E状态标志位的存储位置
#     """
#     try:
#         
#         return core.Status.Pass
#     except Exception as e:
#         logging.error(e)
#         return core.Status.Fail
#     finally:
#         BmcLib.clear_cmos()

