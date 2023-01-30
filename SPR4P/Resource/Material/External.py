# to define external equipment on SUT, e.g hdd bp, ocp, PCIe...
class PCIE:
    Width = "x0"
    Speed = "0GT/s"


class HDDBP8:
    # 8硬盘背板对应SataSpinUpController1[4]~[7]
    Controller = 1           # BIOS定义 1
    Ports = [4, 5, 6, 7]     # 8*2.5 SAS/SATA


class TPM_NTZ_2P0:
    Protocol = "TPM"
    Version = "2.0"
    Vendor = "NTZ"
    VendorVer = "7.51"
    HashAlgo = ["SHA1", "SHA256", "SM3_256"]


class OCP_SC381(PCIE):
    Width = "x8"
    Speed = "8GT/s"


class X550T(PCIE):
    Width = "x8"
    Speed = "5GT/s"

class X710(PCIE):
    Width = "x8"
    Speed = "8GT/s"

class Hi1822(PCIE):
    Width = "x16"
    Speed = "8GT/s"

class Broadcom_9560_8i(PCIE):
    Width = "x8"
    Speed = "16GT/s"