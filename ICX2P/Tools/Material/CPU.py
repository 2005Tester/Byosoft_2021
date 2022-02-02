class ICX:
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
    Name = "Intel\(R\) Xeon\(R\)"
    Level = "Gold"
    Code = "ICX"
    CodeLong = "Ice Lake"
    Type = "Xeon"  # Product Name   [to be Overwrite]
    BaseFreq = 1.0  # GHz           [to be Overwrite]
    TurboFreq = 1.0  # GHz          [to be Overwrite]
    Cores = 0                     # [to be Overwrite]
    Stepping = "00"               # [to be Overwrite]
    L1_Cache = 80  # KB
    L2_Cache = 1280  # KB
    L3_Cache = 0  # KB              [to be Overwrite]
    Max_Mem_Freq = 3200  # MHz      [to be Overwrite]
    Voltage = 1.6  # V
    CPUID = "606A6"
    TDP = 0  # Thermal Design Power [to be Overwrite]
    UpiSpeed = 11.2  # Upi Speed (GT/s)
    UpiPorts = 3  # Upi Ports
    MCs = 4  # Memory Controller
    CHs = 2  # Memory Channel per MC


class Icx6330(ICX):
    Type = "6330"
    BaseFreq = 2.0
    TurboFreq = 2.6  # AVX / All Cores
    Cores = 28
    Stepping = "D1"
    L3_Cache = 43008
    Max_Mem_Freq = 2933
    TDP = 205


class Icx8352Y(ICX):
    Type = "8352Y"
    BaseFreq = 2.2
    TurboFreq = 2.8  # AVX / All Cores
    Cores = 32
    Stepping = "D2"
    L3_Cache = 49152
    TDP = 205


class Icx6348(ICX):
    Type = "6348"
    BaseFreq = 2.6
    TurboFreq = 3.4  # AVX / All Cores
    Cores = 28
    Stepping = "D1"
    L3_Cache = 43008
    TDP = 235

