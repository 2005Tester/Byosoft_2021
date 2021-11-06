
from Moc25 import Boot, Smbios, SetUp

# Define test scope for daily test
def DailyTest():
    pass

def ReleaseTest():
    pass

def Debug():
    SetUp.init_test()
    if Boot.boot_AliOS():
        Smbios.type0()
        Smbios.type1()

