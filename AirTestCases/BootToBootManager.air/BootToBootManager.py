# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *

auto_setup(__file__)

using("HaiYan5Common.air")
import HaiYan5Common


HaiYan5Common.boot_to_bootmanager()