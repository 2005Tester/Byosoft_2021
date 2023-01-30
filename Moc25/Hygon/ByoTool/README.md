# Byosoft Automation Test Framework

## 环境准备
1.Windows系统:安装,打开SSH服务,在用户根目录放置三种工具和BIOS文件(
包括要刷新的文件'命名为latest.bin,previous.bin',其他平台文件'others.bin',未签名的文件'unsigned.bin')  
2.Linux系统:打开SSH服务,/root目录下放置三种工具  
3.U盘:根目录下新建文件夹命名为项目名(例如:CRB3000),文件夹中放置  
  (1)三种工具和BIOS文件(包括要刷新的文件'命名为latest.bin,previous.bin',其他平台文件'others.bin',未签名的文件'unsigned.bin')   
  (2)SecureBoot文件夹(文件夹内放置ByoAuditModeTest.efi工具,正确的key文件'correct-key',错误的key文件'error-key')  

 


## 测试项目
测试文件为'ToolTest.csv',每一个case后面都有中文描述
**如果测试case同时涉及Windows系统和Linux系统,则第一个测试case必须是FlashTest.flash_tool_0000()以初始化SSH



## 注意事项
1.测试使用的BIOS必须串口默认打开,语言默认英文  
2.ByoDmi测试需要事先在Tools/ByoDmi_Smbios下放好三种环境下ByoDmi工具读取的smbios信息  
3.Config文件中'MACHINE_TYPE'如果测试机器支持IPMI命令开关机则为'Server',反之则为'Desktop';
'OEM_SUPPORT'如果测试机器支持OEM命令修改SetUp选型值则为True,反之则为False  



## Test Case ID 分配

### ByoTool
| Module | ID Range |
| ------ | ------ |
|  FlashTest | 0000-0299 |
|  ByoDmiTest | 1001~1299 |
|  ByoCfgTest | 2001~2299 |
|  SecureBootTest | 3001~3401 |






