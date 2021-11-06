# Byosoft Automation Test Framework 使用指南  

## 环境搭建  
Host - SUT

## SUT资源  
测试执行中, Host需要访问SUT资源同SUT进行交互, 如串口, 网络，测试工具等.  
在ProjectConfig.json 里面配置测试需要使用的SUT资源，目前支持:   
BIOS_COM, BMC_COM, BMC_SSH, BMC_SFTP, BMC_RFISH, OS_SSH, OS_SFTP, OS_LEGACY_SSH, OS_LEGACY_SFTP, UNITOOL   
```
    {
    "ProjectName": "ICX2P",
    "Resources": ["BIOS_COM", "BMC_SSH", "BMC_SFTP", "BMC_RFISH", "OS_SSH", "OS_SFTP", "OS_LEGACY_SSH", "OS_LEGACY_SFTP", "UNITOOL"],
    "ConfigMapping": {
        "Sut01": "Sut01Config",
        "Sut02": "Sut02Config",
        "Sut03": "Sut03Config"
        }
    }
```
具体内容比如串口号, IP地址, ssh登录的用户名密码等在config\SutxxConfig.py里面配置.  


## batf Reference  
**测试用例的返回值定义:**  
Global Status Code:  
```
core.Status.Pass = 1
core.Status.Skip = 2
core.Status.Fail = None
```

**截图功能:**  
1.在需要时截图:  
core.capture_screen(img_dir=None, img_file=None)  
默认保存在测试日志目录, 可自定义保存路径和文件名(不需要扩展名).    
比如: core.capture_screen(Env.LOG_DIR, "usb001")    

2. 测试Fail时会自动截图  


## Change Log
**0.0.9** 
1. First working version  

**0.1.0**
1. batf.core 增加test_case装饰器  
2. batf.core 增加独立的屏幕截图方法  
3. batf.core 增加stylelog方法 
4. batf.SerialLib, batf.SshLib 增加使用方法, 参数及返回类型提示    
5. Redfish API 路径可配置, Env下面配置字典:     
```
REDFISH_API = {
        "SYSTEM": "/redfish/v1/Systems/1",
        "CHASSIS": "/redfish/v1/Chassis/1",
        "MANAGER": "/redfish/v1/Managers/1"
    }
6. 修复带冒号的串口选项值匹配问题.
```
