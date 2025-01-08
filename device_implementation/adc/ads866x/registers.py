from dataclasses import dataclass, field
from bitarray import bitarray


def int_to_bitarray(n: int, bitlen: int):
    return bitarray(bin(n)[2:].zfill(bitlen))


@dataclass
class BitfieldSpec:
    data: bitarray
    const: dict[str, bitarray]


@dataclass(kw_only=True)
class Ads866xRegister:
    address: int
    address_lower_halfword: int = field(init=False)
    address_upper_halfword: int = field(init=False)
    address_ba: bitarray = field(init=False)
    address_lower_halfword_ba: bitarray = field(init=False)
    address_upper_halfword_ba: bitarray = field(init=False)
    data: bitarray = field(default=bitarray("00000000 00000000 00000000 00000000"))

    def __post_init__(self):
        if len(self.data) != 32:
            raise ValueError("Ads866xRegister must have exactly 32 bits")

        if self.address % 4 != 0:
            raise ValueError("Ads866xRegister must be aligned to 4 bytes")

        address_len = 9

        if self.address < 0 or self.address > 2**address_len - 1:
            raise ValueError(
                f"Ads866xRegister must have an address in [0, {2**address_len -1}], but has address {self.address}"
            )

        self.address_ba: bitarray = int_to_bitarray(self.address, address_len)

        self.address_lower_halfword: int = self.address
        self.address_lower_halfword_ba: bitarray = int_to_bitarray(
            self.address_lower_halfword, address_len
        )

        self.address_upper_halfword: int = self.address + 2
        self.address_upper_halfword_ba: bitarray = int_to_bitarray(
            self.address_upper_halfword, address_len
        )


@dataclass
class DeviceIdReg(Ads866xRegister):
    DEVICE_ADDR: BitfieldSpec = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x00, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.DEVICE_ADDR = BitfieldSpec(
            self.data[16:20], {"DEFAULT_ADDR": bitarray("0000")}
        )


@dataclass
class RstPwrctlReg(Ads866xRegister):
    WKEY: BitfieldSpec = field(init=False)
    VDD_AL_DIS: BitfieldSpec = field(init=False)
    IN_AL_DIS: BitfieldSpec = field(init=False)
    RSTN_APP: BitfieldSpec = field(init=False)
    NAP_EN: BitfieldSpec = field(init=False)
    PWRDN: BitfieldSpec = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x04, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.WKEY = BitfieldSpec(
            self.data[8:16], {"PROTECTION_KEY": int_to_bitarray(0x69, 8)}
        )
        self.VDD_AL_DIS = BitfieldSpec(
            self.data[5:6],
            {"VDD_AL_ENABLED": bitarray("0"), "VDD_AL_DISABLED": bitarray("1")},
        )
        self.IN_AL_DIS = BitfieldSpec(
            self.data[4:5],
            {"IN_AL_ENABLED": bitarray("0"), "IN_AL_DISABLED": bitarray("1")},
        )
        self.RSTN_APP = BitfieldSpec(
            self.data[2:3], {"RSTN_POR": bitarray("0"), "RSTN_APP": bitarray("1")}
        )
        self.NAP_EN = BitfieldSpec(
            self.data[1:2],
            {"NAP_DISABLED": bitarray("0"), "NAP_ENABLED": bitarray("1")},
        )
        self.PWRDN = BitfieldSpec(
            self.data[0:1],
            {"MODE_ACTIVE": bitarray("0"), "MODE_PWR_DOWN": bitarray("1")},
        )


@dataclass
class SdiCtlReg(Ads866xRegister):
    SDI_MODE: BitfieldSpec = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x08, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.SDI_MODE = BitfieldSpec(
            self.data[0:2],
            {
                "SPI_MODE_0_CPOL_0_CPHA_0": bitarray("00"),
                "SPI_MODE_1_CPOL_0_CPHA_1": bitarray("01"),
                "SPI_MODE_2_CPOL_1_CPHA_0": bitarray("10"),
                "SPI_MODE_3_CPOL_1_CPHA_1": bitarray("11"),
            },
        )
