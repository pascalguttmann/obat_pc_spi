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


@dataclass
class SdoCtlReg(Ads866xRegister):
    GPO_VAL: BitfieldSpec = field(init=False)
    SDO1_CONFIG: BitfieldSpec = field(init=False)
    SSYNC_CLK: BitfieldSpec = field(init=False)
    SDO_MODE: BitfieldSpec = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x0C, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.GPO_VAL = BitfieldSpec(
            self.data[12:13], {"LOW": bitarray("0"), "HIGH": bitarray("1")}
        )
        self.SDO1_CONFIG = BitfieldSpec(
            self.data[8:10],
            {
                "SDO1_TRISTATE": bitarray("00"),
                "SDO1_ALARM": bitarray("01"),
                "SDO1_GPO": bitarray("10"),
                "SDO1_SPI_2BIT_SDO": bitarray("11"),
            },
        )
        self.SSYNC_CLK = BitfieldSpec(
            self.data[6:7], {"CLK_EXT": bitarray("0"), "CLK_INT": bitarray("1")}
        )
        self.SDO_MODE = BitfieldSpec(
            self.data[0:2],
            {
                "SDO_DEFAULT_CLK": bitarray("00"),
                "SDO_INTERNAL_CLK": bitarray("11"),
            },
        )


@dataclass
class DataOutCtlReg(Ads866xRegister):
    DEVICE_ADDR_INCL: BitfieldSpec = field(init=False)
    VDD_ACTIVE_L_ALARM_INCL: BitfieldSpec = field(init=False)
    VDD_ACTIVE_H_ALARM_INCL: BitfieldSpec = field(init=False)
    IN_ACTIVE_L_ALARM_INCL: BitfieldSpec = field(init=False)
    IN_ACTIVE_H_ALARM_INCL: BitfieldSpec = field(init=False)
    RANGLE_INCL: BitfieldSpec = field(init=False)
    PAR_EN: BitfieldSpec = field(init=False)
    DATA_VAL: BitfieldSpec = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x10, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.DEVICE_ADDR_INCL = BitfieldSpec(
            self.data[14:15], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.VDD_ACTIVE_L_ALARM_INCL = BitfieldSpec(
            self.data[13:14], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.VDD_ACTIVE_H_ALARM_INCL = BitfieldSpec(
            self.data[12:13], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.IN_ACTIVE_L_ALARM_INCL = BitfieldSpec(
            self.data[11:12], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.IN_ACTIVE_H_ALARM_INCL = BitfieldSpec(
            self.data[10:11], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.RANGLE_INCL = BitfieldSpec(
            self.data[8:9], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.PAR_EN = BitfieldSpec(
            self.data[3:4], {"EXCLUDE": bitarray("0"), "INCLUDE": bitarray("1")}
        )
        self.DATA_VAL = BitfieldSpec(
            self.data[0:3],
            {
                "CONVERSION_RESULT": bitarray("000"),
                "ALL_ZEROS": bitarray("100"),
                "ALL_ONES": bitarray("101"),
                "ALTERNATE_ZEROS_ONES": bitarray("110"),
                "ALTERNATE_DOUBLE_ZEROS_DOUBLE_ONES": bitarray("111"),
            },
        )


@dataclass
class RangeSelReg(Ads866xRegister):
    INTREF_DIS: BitfieldSpec = field(init=False)
    RANGE_SEL: BitfieldSpec = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x14, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.INTREF_DIS = BitfieldSpec(
            self.data[6:7],
            {"INTREF_ENABLE": bitarray("0"), "INTREF_DISABLE": bitarray("1")},
        )
        self.RANGLE_SEL = BitfieldSpec(
            self.data[0:4],
            {
                "BIPOLAR_12V288": bitarray("0000"),
                "BIPOLAR_10V24": bitarray("0001"),
                "BIPOLAR_6V144": bitarray("0010"),
                "BIPOLAR_5V12": bitarray("0011"),
                "BIPOLAR_2V56": bitarray("0100"),
                "UNIPOLAR_12V288": bitarray("1000"),
                "UNIPOLAR_10V24": bitarray("1001"),
                "UNIPOLAR_6V144": bitarray("1010"),
                "UNIPOLAR_5V12": bitarray("1011"),
            },
        )
