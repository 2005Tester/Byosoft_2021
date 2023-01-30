eeupdate64e.efi:  修改网卡MAC地址工具


eeupdate工具使用方法：
（1）查看网卡的MAC地址
–>在文件目录下下直接调用

./eeupdate64e /NIC=[num] /MAC_DUMP
1
其中[num]是对应的虚拟适配器
（2）修改某一个网卡的MAC地址

./eeupdate64e /NIC=[num] /MAC=[addr]
1
其中[addr]是要改为的MAC地址，例如00A023450900这种格式
修改之后需要重启设备生效
