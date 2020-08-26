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



