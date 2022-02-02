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

**0.1.1**
1. batf.core 增加dump_acpi()， 具体使用方法见代码提示  
2. batf.SerialLib 增加 get_supported_values() 和 locate_setup_option()，完善文档  
3. batf.Common.SutSerial修复get_value_list()和locate_value()无法处理选项支持几十个值,需要翻页才能显示完整的情况， 以及单字符选项值匹配不到问题    
4. 移除全局报告url配置, 需要在每个项目Sut0xConfig.py的Env class中配置.  
5. 增强测试执行前对CSV文件的检查, 加入的case必须包含module名称和括号.  
6. SerilLib增加is_msg_present_clean(), 确保不会匹配到上一次操作获取到的串口数据.  
7. Enhance MiscLib.compare_images.  
8. Enhance logging.  
9. 从gitlab下载image增加一层以分支名称和commit hash命名的目录.  
10. 全局变量(var.set())允许写入未事先定义的变量名.
11. batf 增加-t (--trace)参数, 用于打开和关闭日志信息中的模块,函数名, 默认为精简模式.     


**0.1.2**
1. 增加core.dump_and_verify()用于dump并与预期信息比较, 如smbios测试等.   
2. SshLib增加使用帮助信息   
3. 修复core.test_case()返回值一直为None的问题.   


