#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation

# -*- encoding=utf8 -*-
import importlib
from batf import var


SutCfgMde = importlib.import_module(var.get('SutCfg'), var.get('project'))


class Env(SutCfgMde.Env):
    pass

class Msg(SutCfgMde.Msg):
    pass

class Boot(SutCfgMde.Boot):
    pass

class Cpu(SutCfgMde.Cpu):
    pass

class Psw(SutCfgMde.Psw):
    pass

class Ipm(SutCfgMde.Ipm):
    pass

class Pci(SutCfgMde.Pci):
    pass

class Pxe(SutCfgMde.Pxe):
    pass

class Sup(SutCfgMde.Sup):
    pass

class Upd(SutCfgMde.Upd):
    pass


class Rfs(SutCfgMde.Rfs):
    pass

class Tool(SutCfgMde.Tool):
    pass

class Sec(SutCfgMde.Sec):
    pass

class Ras(SutCfgMde.Ras):
    pass