#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-


# Key mapping
class Key:
    ENTER = [chr(0x0D)]
    DEL = [chr(0x7F)]
    F2 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x32), chr(0x7e)]
    F5 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x35), chr(0x7e)]
    F6 = [chr(0x1b), chr(0x5b), chr(0x31), chr(0x37), chr(0x7e)]
    F9 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x30), chr(0x7e)]
    F10 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x31), chr(0x7e)]
    F11 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x33), chr(0x7e)]
    F12 = [chr(0x1b), chr(0x5b), chr(0x32), chr(0x34), chr(0x7e)]
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]
    DISCARD_CHANGES = ['N']
    RESET_DEFAULT = [F9, Y, F10, Y]
    SAVE_RESET = [F10, Y]


# Messages to identify a specific boot option, page, menu or system status
class Msg:
    HOTKEY_PROMPT_DEL = 'Del to enter SETUP,'
    HOTKEY_PROMPT_DEL_CN = '进入固件配置'
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu,'
    HOTKEY_PROMPT_F11_CN = '按 F11 进入启动菜单'
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot,'
    HOTKEY_PROMPT_F12_CN = '按 F12 进入网络启动'

    # pages in bios configuration
    PAGE_MAIN = "Building Info"
    PAGE_MAIN_CN = "编译信息"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_ADVANCED_CN = '串口重定向'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_SECURITY_CN = '设置管理员密码'
    PAGE_BOOT = 'User Wait Time'
    PAGE_BOOT_CN = '用户等待时间'
    PAGE_EXIT = 'Save and Exit'
    PAGE_EXIT_CN = '保存并且退出'

    # menus of main page
    CPU_INFO_CN = '处理器信息'

    # menus of USB configuration
    USB_CONFIG_CN = 'USB配置'
    USB_PORT_CONFIG_CN = 'USB端口配置'

    # path of setup menus
    PATH_USB_CFG_CN = [USB_CONFIG_CN, USB_PORT_CONFIG_CN]

    # menus of boot page
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    ENTER_SETUP = "Enter Setup"
    ENTER_SETUP_CN = "设备启动菜单"
    Kylin_Os = "Kylin Linux Advanced Server\(SATA2-0: INTEL SSDSCKKB960G8\)"