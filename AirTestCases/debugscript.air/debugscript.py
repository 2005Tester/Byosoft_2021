# -*- encoding=utf8 -*-
__author__ = "barton"
auto_setup(__file__)# -*- encoding=utf8 -*-
import logging
from airtest.core.api import *
from airtest.utils.logger import get_logger
from pywinauto import keyboard
using("HaiYan5Common.air")
import HaiYan5Common

auto_setup(__file__)
logger=get_logger("airtest")
logger.setLevel(logging.INFO) 

HaiYan5Common.switch_to_legacy()

