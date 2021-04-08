
from Core import SutInit
from Moc25 import SutConfig, Boot, Smbios, SetUp


# init Sut



# Define test scope for daily test
def DailyTest():
    pass



def ReleaseTest():
    pass


def Debug():
    moc25 = SutInit.SutInit('Moc25')
    SetUp.init_test(moc25)
    Boot.boot_uefi_shell(moc25)
    if Boot.boot_AliOS(moc25):
        Smbios.type0(moc25)
        Smbios.type1(moc25)

