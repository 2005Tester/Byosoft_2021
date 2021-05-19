from Core import SutInit
from Core.SutInit import Sut

from Hygon.BaseLib import BmcLib, SetUpLib
from Hygon import Release

# init SUT
SutInit.SutInit("Hygon")
ser = Sut.BIOS_COM


# Define test scope for daily test
def DailyTest():
    pass


def ReleaseTest():
    pass


def Debug():
    Release.check_usb_info()
