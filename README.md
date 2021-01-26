# Byo Automation Test Tool

## Enviroment Setup
1. Install python 3.8  
2. pip install paramiko  
3. pip install pyserial  


## 2288V6 Usage
1. 自动测试入口脚本：TestIcx2P.py, 所有调通的case, 添加到runtest()里面 
   可选参数: 不跟任何参数 - runtest() 里面包含的所有case执行一遍  
            daily - runtest() 里面包含的所有case执行一遍 并把执行结果写入数据库, 测试结果呈现到Web页面   
            debug - debug_run() 里面包含的所有case执行一遍  
            loop - 循环执行runtest() 里面包含的所有case  
2. Case 开发尽可能使用BaseLib里面已有API， 如果不能满足需求, 在BaseLib里面添加, 不直接调用Common下面的module.  
3. Case按照手动测试用例列表分类, 不要全部放在同一个文件里面. 比如Cpu相关的可以全部放在Cpu.py里面.  
4. 开发新Case尽可能跟手动测试用例一一对应，用例的tittle直接使用用例列表里面Testcase_Number, 如Testcase_DRAM_RAPL_001. description使用Testcase_Name, 如01 菜单项DRAM RAPL选单检查.  


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