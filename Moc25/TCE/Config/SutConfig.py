#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

# -*- encoding=utf8 -*-
import importlib
from batf import var


SutCfgMde = importlib.import_module(var.get('SutCfg'), var.get('project'))


class BootOS(SutCfgMde.BootOS):
    pass


class Env(SutCfgMde.Env):
    pass


class SysCfg(SutCfgMde.SysCfg):
    pass
