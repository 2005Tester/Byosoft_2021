class SPR:
    Name = "Genuine Intel(R) CPU"
    Code = "SPR"
    CodeLong = "Sapphire Rapids"
    Level = "Gold"
    BaseFreq = "0.0"  # GHz
    TurboFreq = "0.0"  # GHz
    Cores = 0
    Stepping = "00"
    L1_Cache = 80  # KB
    L2_Cache = 2048  # KB
    L3_Cache = 0  # KB
    Max_MemFreq_2DPC = 4800  # MHz
    Max_MemFreq_1DPC = 4400  # MHz
    Voltage = 1.6  # V
    CPUID = "000806F3"
    TDP = 0  # W
    UpiSpeed = 16  # GT/s
    UpiPorts = 4


class QYFR(SPR):
    BaseFreq = "1.9"  # GHz
    TurboFreq = "3.7"  # GHz
    Cores = 56
    Stepping = "D0"
    L3_Cache = 107520  # KB
    Max_MemFreq_2DPC = 4800  # MHz
    Max_MemFreq_1DPC = 4400  # MHz
    TDP = 350