# Byosoft Automation Test Framework

## 环境准备
同automation目录下的README.md中的环境准备


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
|  UpdateBIOS | 001~100 |
|  SmbiosTest | 101~200 |
|  PXETest | 201~250 |
|  PCIETest | 251~300 |
|  CpuTest | 301~400 |
|  BootTest	| 401-500 |
|  IpmitoolTest | 501~600 |
|  SetUpTest | 601~700 |
|  SetupPasswordTest | 701~800 |
|  HddPasswordTest | 801~900 |
|  RedFish | 901~950 |
|  RAS | 1001~1050 |
|  ByoCfg | 2001~2300 |
|  SecureBoot | 3001~3500 |


### InspurStorage
| Module | ID Range |
| ------ | ------ |
| UpdateBIOS | 001~100 |
| Smbios | 101~200 |
| PCIE | 251~300 |
| CPU | 301~400 |
| Boot | 401~500 |
| CheckMsg | 501~600 |
| SetUpPassword | 701~800 |

### ByoTool
| Module | ID Range |
| ------ | ------ |
| ByoFlash | 0001~0300 |
| ByoDmi | 1001~1300 |
| ByoCfg | 2001~2300 |
| SecureBoot | 3001~3500 |
| SetUpPsw | 4001~4100 |
| HddPsw | 5001~5100 |
| TPM | 5301~5400 |
| PXE | 5401~5500 |


