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
    ADD=[chr(0x2B)]#+
    SUBTRACT=[chr(0x2D)]#-
    ENTER = [chr(0x0D)]
    DEL = [chr(0x7F)]
    F2 = [chr(0x1b), chr(0x32)]
    F5 = [chr(0x1b),chr(0x35)]
    F6 = [chr(0x1b), chr(0x36)]
    F7 = [chr(0x1b), chr(0x37)]
    F9 = [chr(0x1b), chr(0x39)]
    F10 = [chr(0x1b), chr(0x30)]
    F11 = [chr(0x1b), chr(0x21)]
    F12 = [chr(0x1b), chr(0x40)]
    ESC = '\33' + ' '
    CTRL_ALT_DELETE = '\33R\33r\33R'
    UP = [chr(0x1b), chr(0x5b), chr(0x41)]
    DOWN = [chr(0x1b), chr(0x5b), chr(0x42)]
    LEFT = [chr(0x1b), chr(0x5b), chr(0x44)]
    RIGHT = [chr(0x1b), chr(0x5b), chr(0x43)]
    Y = [chr(0x59)]
    N=[chr(0x4e)]
    CONTROL = '\ue009'
    DISCARD_CHANGES = ['N']
    RESET_DEFAULT = [F9, Y]
    SAVE_RESET = [F10, Y]
    CONTROL_F11 = [CONTROL, F11]
    PAGE_UP = '\x1b?'
    PAGE_DOWN = '\x1b/'

