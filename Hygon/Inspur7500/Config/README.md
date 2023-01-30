# Byosoft Automation Test Framework

## 环境准备
1,U盘：同时具备DOS和SHELL环境,根目录新建文件夹'BIOS',存放BIOS文件(最新的命名为latest.bin,以前的命名为previous.bin)、各种环境下BIOS刷新工具、未签名的BIOS文件(命名为unsigned.bin)、其他平台BIOS(命名为others.bin)。  
2,系统盘两个：一个UEFI系统，一个Legacy系统。打开SSH，/root目录下放CPU测试工具(monitor_0.1.8,pstate-set.sh,SMUToolSuite)  


## 修改Config  
修改对应平台的Config
### 必须修改
1,串口端口号  
2,BMC IP地址，用户名，密码  
3,OS  IP地址，用户名，密码  
4,Linux下执行下'fdisk -l | grep Disk'中U盘名称,SHELL下U盘盘符  
5,启动菜单各启动项名称(UEFI系统要包含在UEFI,Legacy两种模式下的启动名称,Legacy系统要包含在UEFI,Legacy两种模式下的启动名称)  
6,设置硬盘密码时硬盘名及其对应系统  
7,硬盘绑定 硬盘名及对应系统  
8,刷新BIOS前设置的管理员,用户密码
### 指定测试修改
1,外插网卡：如果有外插网卡需要修改外插网卡名以及外插网卡启动项的名称  
2,




## 添加新项目
目前Hygon平台的所有自动化测试都需要放在Hygon的目录下，目录的名字即为项目的名称，目录结构可以参照Inspur7500项目
新添加的项目需要在Hygon目录下的ProjectConfig.json中定义下


## 运行测试 
打开cmd，切换到Hygon目录下，然后运行
batf ProjectName SutName ExecutionType  
例如: batf Inspur7500 Puti release
若是执行测试时，报缺少python的某些库，通过pip install安装后继续执行
其中：   
ProjectName: Inspur7500, InspurStorage, Hygon7500CRB, Hygon3000CRB，即在Hygon目录下的每个目录即为一个项目
SutName: 在ProjectConfig.json中定义, 例如：Puti，Nvwa，Huike1，根据项目代号命名更直观，例如Puti对应的配置文件为Config目录下的PutiConfig.py
Execution: Release, daily, weekly，比如release参数，就表示执行AllTest.csv文件里Release这一列为Yes的测试项，路径为项目名称-->AllTest.csv
-p: 产生报告到web   
-h: 帮助信息
-t: 可以看到每一步执行的时哪个函数的哪一行代码


## 代码风格
整体风格同automation目录下的README.md中的代码风格部分
每个模块里的方法（每个方法对应着一个测试项），每个方法之间尽量保持统一的空行数，定为3行


## Test Case ID 分配

### Inspur7500
| Module | ID Range |
| ------ | ------ |
|  BootTest	| 401-500 |
|  CpuTest | 301~400 |
|  HddPasswordTest | 801~900 |
|  IpmitoolTest | 501~600 |
|  PCIETest | 251~300 |
|  PXETest | 201~250 |
|  SetupPasswordTest | 701~800 |
|  SetUpTest | 601~700 |
|  SmbiosTest | 101~200 |
|  UpdateBIOS | 001~100 |