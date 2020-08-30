# Byo Automation Test Tool

## Enviroment Setup
python 3.8  
pip install paramiko  
pip install pyserial  


# Linux OS allow root login from SSH  
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


### Value Test
1. registry.json and currentvalue.json must be updated
2. run python Redfishtest.py valuetest
3. Test script will set all the supported optins to a non-default value
4. reboot SUT after test complete, SUt should boot successfully
5. Review test log, error due to dependency options are expectd.


### gen nondeptc