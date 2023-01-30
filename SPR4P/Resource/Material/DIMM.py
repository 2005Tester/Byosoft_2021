class DDR5:
    Vendor = "NA"       # Vendor Name
    Size = 0            # GB
    Freq = 0            # MHz
    RankCnt = 2         # Rank Counts
    DRAM_BW = 4         # DRAM Bit Width
    RankType = "0Rx0"   # Rank/BitWidth
    Type = "RDIMM"      # UDIMM/RDIMM/SODIMMM
    SN = "NA"           # Serial Number
    DIMM_BW = 80        # DDR5 Fixed Value (32bit per sub-ch + 8bit ECC) x 2 Sub-Channel
    Voltage = 1100      # mV (DDR5 Default Voltage 1100 mV)


class Samsung_64G_2Rx4_4800(DDR5):
    Vendor = "Samsung"
    Size = 64
    Freq = 4800
    RankCnt = 2
    DRAM_BW = 4
    RankType = "DRx4"


class Samsung_32G_2Rx8_4800(DDR5):
    Vendor = "Samsung"
    Size = 32
    Freq = 4800
    RankCnt = 2
    DRAM_BW = 4
    RankType = "DRx4"

class Samsung_16G_1Rx8_4800(DDR5):
    Vendor = "Samsung"
    Size = 16
    Freq = 4800
    RankCnt = 1
    DRAM_BW = 8
    RankType = "SRx8"

