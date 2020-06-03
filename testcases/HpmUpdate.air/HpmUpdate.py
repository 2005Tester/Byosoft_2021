# -*- encoding=utf8 -*-
__author__ = "barton"

from airtest.core.api import *
from airtest.utils.logger import get_logger
import logging
auto_setup(__file__)
using("HaiYan5Common.air")
import HaiYan5Common
using("HpmUpdateCommon.air")
import HpmUpdateCommon

logger=get_logger("airtest")
logger.setLevel(logging.INFO)

"""
Verify added setup option after HPM update:
ServeMEDebug -General - Region_Select Message ["Disable",Enable]	增加
ServeMEDebug -General - Watchdog Control Message [Enable]	增加


"""
print("Reboot SUT to verify upgrade...")
sleep(5)
HpmUpdateCommon.verify_hpm_update()
    