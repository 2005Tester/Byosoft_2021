# Byosoft Automation Test Framework

## 环境准备
1.Linux系统:打开SSH服务,/root目录下放置三种工具  
2.U盘:根目录下新建文件夹命名为项目名(例如:FeiTeng),文件夹中放置  
  (1)三种工具和BIOS文件(包括要刷新的文件'命名为latest.bin,previous.bin',其他平台文件'others.bin',未签名的文件'unsigned.bin')   
  (2)SecureBoot文件夹(文件夹内放置ByoAuditModeTest.efi工具,正确的key文件'correct-key',错误的key文件'error-key')  
3.USB端口测试:  
  (1)USB端口测试(接Hub)相关CaseID,TC107,108:Hub上插上所有的USB设备(包括:键鼠,存储设备,其他设备),测试前需要修改Config中USB_PORT_OPTION_NAME(Hub插在USB端口的名称)  
  (2)USB端口测试(接不接Hub都行)相关CaseID,TC105,106:测试前需要修改Config中PORT_DEVICE_DICT(所有USB设备的类型)
 


## 测试项目
测试文件为'AllTest.csv',每一个case后面都有中文描述(如果没有中文描述就运行AddDescription.py文件中的add_description()函数)  
跑测试只能按照一列来跑,即如果运行'batf D2000 D2000 daily'则只会运行Daily那一列中所有'Yes'的case  




## 注意事项
1.测试使用的BIOS必须串口默认打开,语言默认英文  
2.ByoDmi测试需要事先在Tools/ByoDmi_Smbios下放好三种环境下ByoDmi工具读取的smbios信息  
3.Config文件中'MACHINE_TYPE'如果测试机器支持IPMI命令开关机则为'Server',反之则为'Desktop';
'OEM_SUPPORT'如果测试机器支持OEM命令修改SetUp选型值则为True,反之则为False  




## Test Case ID 分配

### ByoTool
| Module | ID Range |
| ------ | ------ |
|  BootTest | 001-099 |
|  SetupTest | 101~199 |
|  PCIETest | 201~299 |
|  UpdateTest | 301~399 |
|  FlashTest | 0000-0299 |
|  ByoDmiTest | 1001~1299 |
|  ByoCfgTest | 2001~2299 |
|  SecureBootTest | 3001~3401 |
|  SetupPswTest | 4001~4100 |






