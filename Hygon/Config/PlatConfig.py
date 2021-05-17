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
    HOTKEY_PROMPT_DEL = 'Press Del to enter SETUP'
    HOTKEY_PROMPT_F11 = 'Press F11 to enter Boot Menu'
    HOTKEY_PROMPT_F12 = 'Press F12 to enter PXE boot'
    HOTKEY_PROMPT_F1 = ''
    HOTKEY_PROMPT_F9 = ''
    HOTKEY_PROMPT_F10 = ''
    POST_INFO = 'Press Del to enter SETUP, and Press F11 to enter Boot Menu, and Press F12 to enter PXE boot.'

    # pages in bios configuration
    PAGE_MAIN = "Building Info"
    PAGE_ADVANCED = 'Console Redirection'
    PAGE_SECURITY = 'Set Administrator Password'
    PAGE_BOOT = 'User Wait Time'
    PAGE_EXIT = 'Save and Exit'

    # menus of CPU configuration
    CPU_CONFIG = 'CPU Configuration'

    # menus of PCH configuration
    PCH_CONFIG = 'PCH Configuration'
    NETWORK_CONFIG = 'Network Configuration'
    USB_CONFIG = 'USB Configuration'

    # Misc Configuration Menu
    MISC_CONFIG = 'Miscellaneous Configuration'

    # menus of Password configuration
    MGT_SPV_PWD = 'Manage Supervisor Password'
    SP_PWD = 'Simple Password'

    # path of setup menus
    # PATH_UNCORE_GENERAL = [CPU_CONFIG, UNCORE_CONFIG]

    # menus of Boot page
    PXE_PORT1 = "UEFI Onboard: Port 0 - WangXun\(R\) PXE IPv4"
    PXE_PORT2 = "UEFI Onboard: Port 1 - WangXun\(R\) PXE IPv4"
    ENTER_SETUP = "Enter Setup"
    Kylin_Os = ["Kylin Linux Advanced Server\(SATA2-0: INTEL SSDSCKKB960G8\)"]

    # Firmware version info
    ME_VERSION = '0F:4.4.4.53'
    RC_VERSION = 'RC Version : 0.2.2.002D'