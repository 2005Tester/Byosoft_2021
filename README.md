# Byo Automation Test Tool

## Enviroment Setup
1. Install python 3.8  
2. pip install paramiko  
3. pip install pyserial  

or Run pip install -r requirements.txt  


## Test Case Development Rules
1. 自动测试入口脚本：Test[projectname].py, 所有调通的case, 添加到runtest()里面   
   可选参数: **不跟任何参数** - runtest() 里面包含的所有case执行一遍  
            **daily** - runtest() 里面包含的所有case执行一遍 并把执行结果写入数据库, 测试结果呈现到Web页面   
            **debug** - debug_run() 里面包含的所有case执行一遍，可用于调试    
            **loop** - 循环执行runtest() 里面包含的所有case， 用于stress或者测试脚本本身的健壮性    
2. Case 开发尽可能使用BaseLib里面已有API， 如果不能满足需求, 在BaseLib里面添加, 不直接调用Common下面的module.  
3. Case按照手动测试用例列表分类, 不要全部放在同一个文件里面. 比如Cpu相关的可以全部放在Cpu.py里面.  
4. 开发新Case尽可能跟手动测试用例一一对应，用例的tittle直接使用用例列表里面Testcase_Number加上脚本里面定义的TCID,  
如：TC101_Testcase_DRAM_RAPL_001    
Description使用Testcase_Name  
如：01 菜单项DRAM RAPL选单检查.     
5.  Release自验报告里面的case, title 加上前缀 Basci_Function, 如 Basci_Function Chipsec Test.  
6. Test case id 确保唯一, 注释注明测试执行的先决条件等信息：  
   **Precondition**: Case执行的先决条件, 比如网络连接, 依赖的相关测试工具等  
   **OnStart**: 测试用例开始执行时, SUT所处的状态, 比如Boot到os， 没有依赖, 任何情况下都可以执行, 则写NA  
   **OnComplete**：测试用例执行完成时， SUT所处的状态, 比如在OS， Setup 等   
7. 确保每个case的log 包含<Start>, <Description>, <Result>标签, 如下:
 
2021-04-17 04:20:42 INFO: <TC901><Tittle>ME_Check ME Version and status:Start  
2021-04-17 04:20:42 INFO: <TC901><Description>ME version should be match within BIOS bin file, ME Status shoule be normal.  
...   
2021-04-17 04:25:56 INFO: <TC901><Result>ME_Check ME Version and status:Fail  



代码示例:  
\# 非装备模式BIOS设置装备模式flag, 预期设置不成功.  
\# Precondition: 装备模式image， Unitool  
\# OnStart: in SUSE  
\# OnComplete: in SUSE  
def equip_mode_flag_check(unitool):  
    tc = ('902', 'TC902 Equipment mode flag check', '非装备模式BIOS设置装备模式flag, 预期设置不成功.')  
    result = ReportGen.LogHeaderResult(tc)  
    res = unitool.set_config(BiosCfg.EQUIP_FLAG)  
    if res:  
        result.log_fail()  
        return  
    logging.info("Unbale to set equipment mode flag.")  
    result.log_pass()  
    return True  

## 使用截图功能  
1. 创建LogHeaderResult()对象实例时传入截图保存路径,如:  
result = ReportGen.LogHeaderResult(tc, serial, SutConfig.LOG_DIR)  
2. 需要的时候调用 result.capture_screen()  
3. 有fail自动截屏, result.log_fail(capture=True)  


# Allow root login from SSH in Linux  
## Ubuntu Instructions  
sudo apt install openssh-server  
sudo passwd root  
sudo vim /etc/ssh/sshd_config  
Find # Authentication change "PermitRootLogin prohibit-password" to "PermitRootLogin yes"  
sudo systemctl restart sshd  


# Redfish
## Prepare Test
1. Update BIOS, dump registry.json and currentvalue.json from BMC web, override the same files in RedFish\baseline
2. update RedFish\baseline\baseline.txt based on  
3. Redfish\config.py must be updated  
    BIOS = "C:\\UpdateTool\\HY5V020_candidate1.bin"


### Value Test
1. registry.json and currentvalue.json must be updated
2. run python Redfishtest.py valuetest
3. Test script will set all the supported optins to a non-default value
4. reboot SUT after test complete, SUt should boot successfully
5. Review test log, error due to dependency options are expectd.


### gen nondeptc


### CMD Windows Setting
1. Close all active CMD Windows
2. Open a CMD Windows with administrator priv and run the following command:
    reg add HKEY_CURRENT_USER\Console /v QuickEdit /t REG_DWORD /d 00000000 /f
3. Open a new CMD Windows to execute the AT sctipt