from Core import SutInit
from Core.SutInit import Sut

from Hygon.BaseLib import BmcLib, SetUpLib

# init SUT
SutInit.SutInit("Nvwa")
ser = Sut.BIOS_COM
ssh_os = Sut.OS_SSH


# Define test scope for daily test
def DailyTest():
    pass


def ReleaseTest():
    pass


def Debug():
    SetUpLib.change_default_language()
