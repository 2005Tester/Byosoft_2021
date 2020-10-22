# Byo Automation Test Tool

## Enviroment Setup
1. Install python 3.8  
2. pip install paramiko  
3. pip install pyserial  


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