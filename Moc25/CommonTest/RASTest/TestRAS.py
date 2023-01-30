import os
import sys
import time
import argparse
import importlib

platforms = ["CPX", "ICX", "SPR"]
curpath = os.path.dirname(os.path.abspath(__file__))
temp = "_temp"  # 临时文件名

welcome_msg = r"""
===========================================================
请输入正确的参数:
示例1： StartTest.py -p ICX -t ADDDC
示例2： StartTest.py -p ICX -t FDM Mirror -f RASTest
示例3： StartTest.py -p ICX -t Testcase_MemRAS_013
-----------------------------------------------------------
-p:                   【 必选参数 | 测试平台 | 单个 】
    -- ICX/CPX/SPR
-----------------------------------------------------------
-t:                   【 必选参数 | 测试项目 | 单个/多个 】
    -- CPU                      *************************
    -- MEM                      *  输入FeatureName
    -- PCIE                     *  可批量测试所有相关Case
    -- FDM                      *************************
    -- ...                   

    -- Testcase_MemRAS_010      *************************
    -- Testcase_FDM_SMI_002     * 直接输入测试Case编号
    -- ...                      *************************
-----------------------------------------------------------
-f：                  【 可选参数 | 测试FLAG | 单个 】
    FLAG说明：
    如果加自定义参数"FLAG"，停止后还可以继续此FLAG的测试
    同一个"FLAG"的测试结果会放在以FLAG命名的文件夹内
    不加"FLAG"参数，FLAG默认为测试开始时间
    测试LOG默认保存路径：我的文档\PythonSV\{FLAG}
===========================================================
"""


def init_env():
    tmp_logs = ["dflaunch.log", "last_exception.log", "socket_discovery"]
    for files in os.listdir(curpath):
        if any(_tmp_log in files for _tmp_log in tmp_logs):
            try:
                os.remove(files)
            except:
                pass
        if files not in platforms:
            continue
        tmpFile = os.path.join(curpath, files+"\\"+temp)
        if os.path.exists(tmpFile):
            os.remove(tmpFile)


def argvs():
    parser = argparse.ArgumentParser(description='RAS Test Scripts for ICX/CPX/SPR')
    parser.add_argument('-p', '--platform', type=str, required=True, choices=platforms, help='Platform SKU')
    parser.add_argument('-t', '--test', type=str, nargs='+', required=True, help='Test Items')
    parser.add_argument('-f', '--flag', type=str, required=False, help='Test Flag')
    return parser.parse_args()


def main():
    if len(sys.argv) < 5:
        print(welcome_msg)
        return
    if sys.argv[2] not in platforms:
        print(welcome_msg)
        return
    init_env()
    args = argvs()
    try:
        config = importlib.import_module(name="{}.RasConfig".format(args.platform), package="RASTest")
        cs_path = config.Cscript_Path
        print("Cscripts Path: {}".format(cs_path))
    except:
        print("Import Config Failed, Please double check!")
        return
    entry_path = os.path.join(curpath, args.platform)
    now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    flag = args.flag if args.flag else now
    with open(os.path.join(entry_path, temp), "w") as f:
        f.write("{}\n".format(flag))
        for t in args.test:
            f.write("{}\n".format(t))
    os.system(rf'dflaunch {cs_path}\startCscripts.py -a ipc -p {args.platform} -s {entry_path}\TestLoader.py')


if __name__ == "__main__":
    main()
