class SPR:
    """
    You can get the information from CPU Vendor's official website.
    Following attributes must be overwritten when create a new CPU sku:
    1. Type
    2. BaseFreq
    3. TurboFreq
    4. Cores
    5. Stepping
    6. Cache
    7. Max_Mem_Freq
    8. TDP
    """
    Name = "Intel(R) Xeon(R)"
    Level = "Gold"
    Type = "0000"  # 6430
    Code = "SPR"
    CodeLong = "Sapphire Rapids"
    BaseFreq = "0.0"  # GHz
    TurboFreq = "0.0"  # GHz
    Cores = 0
    Stepping = "00"
    L1_Cache = 4480  # KB
    L2_Cache = 114688  # KB
    L3_Cache = 0  # KB
    Max_MemFreq_2DPC = 4400  # MHz
    Max_MemFreq_1DPC = 4800  # MHz
    Voltage = 1.6  # V
    CPUID = "806F3"
    TDP = 0  # W
    UpiSpeed = 16  # GT/s
    UpiPorts = 4
    MCs = 4
    CHs = 2


class QYFR(SPR):
    Name = "Genuine Intel(R)"
    Type = "0000%@"
    Level = "CPU"
    BaseFreq = 1.9  # GHz
    TurboFreq = 2.8  # GHz
    Cores = 56
    Stepping = "D0"
    L3_Cache = 105 * 1024  # KB
    Max_MemFreq_2DPC = 4400  # MHz
    Max_MemFreq_1DPC = 4800  # MHz
    TDP = 350


class QYFN(SPR):
    Name = "Genuine Intel(R)"
    Type = "0000%@"
    Level = "CPU"
    BaseFreq = 1.5  # GHz
    TurboFreq = 2.6  # GHz
    Cores = 48
    Stepping = "D0"
    L3_Cache = 90 * 1024  # KB
    Max_MemFreq_2DPC = 4000  # MHz
    Max_MemFreq_1DPC = 4000  # MHz
    TDP = 270


class QYFP(SPR):
    BaseFreq = 1.5  # GHz
    TurboFreq = 2.5  # GHz
    Cores = 48
    Stepping = "D0"
    L3_Cache = 90 * 1024  # KB
    L1_Cache = 3840 #KB
    L2_Cache = 98304 #KB
    Max_MemFreq_2DPC = 4800  # MHz
    Max_MemFreq_1DPC = 4800  # MHz
    TDP = 270


class Q16W(SPR):
    Name = "Intel(R) Xeon(R)"
    BaseFreq = 1.9  # GHz
    TurboFreq = 2.6  # GHz
    Cores = 32
    CPUID = "806F6"
    Stepping = "E3"
    Type = "6430"
    L1_Cache = 2560  # KB
    L2_Cache = 65536  # KB
    L3_Cache = 60 * 1024  # KB
    Max_MemFreq_2DPC = 4400  # MHz
    Max_MemFreq_1DPC = 4400  # MHz
    TDP = 270


class Q16X(SPR):
    Name = "Intel(R) Xeon(R)"
    BaseFreq = 2.2  # GHz
    TurboFreq = 2.8  # GHz
    Cores = 32
    CPUID = "806F6"
    Stepping = "E3"
    Type = "6454S"
    L1_Cache = 2560  # KB
    L2_Cache = 65536  # KB
    L3_Cache = 60 * 1024  # KB
    Max_MemFreq_2DPC = 4400  # MHz
    Max_MemFreq_1DPC = 4800  # MHz
    TDP = 270


class Q1VW(SPR):
    Name = "Intel(R) Xeon(R)"
    BaseFreq = 2.1  # GHz
    TurboFreq = 3  # GHz
    Cores = 32
    CPUID = "806F7"
    Stepping = "S2"
    Type = "6448Y"
    L1_Cache = 2560  # KB
    L2_Cache = 65536  # KB
    L3_Cache = 60 * 1024  # KB
    Max_MemFreq_2DPC = 4400  # MHz
    Max_MemFreq_1DPC = 4800  # MHz
    TDP = 225


class Q1VN(SPR):
    Name = "Intel(R) Xeon(R)"
    BaseFreq = 2  # GHz
    TurboFreq = 2.8  # GHz
    Cores = 12
    CPUID = "806F7"
    Stepping = "S2"
    Type = "4410Y"
    Level = "Silver"
    L1_Cache = 960  # KB
    L2_Cache = 24576  # KB
    L3_Cache = 30 * 1024  # KB
    Max_MemFreq_2DPC = 4000  # MHz
    Max_MemFreq_1DPC = 4000  # MHz
    TDP = 150


class Q17J(SPR):
    Name = "Intel(R) Xeon(R)"
    BaseFreq = 2.9  # GHz
    TurboFreq = 3.2  # GHz
    Cores = 16
    CPUID = "806F6"
    Stepping = "E3"
    Type = "8444H"
    Level = "Platinum"
    L1_Cache = 1280  # KB
    L2_Cache = 32768  # KB
    L3_Cache = 45 * 1024  # KB
    Max_MemFreq_2DPC = 4400  # MHz
    Max_MemFreq_1DPC = 4800  # MHz
    TDP = 270
