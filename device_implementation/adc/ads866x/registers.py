from dataclasses import dataclass, field
from util import reverse_string, uint_to_bitarray
from bitarray import bitarray


@dataclass
class BitfieldSpec:
    slice: slice
    const: dict[str, bitarray]


@dataclass(kw_only=True)
class Ads866xRegister:
    address: int
    address_lower_halfword: int = field(init=False)
    address_upper_halfword: int = field(init=False)
    address_ba: bitarray = field(init=False)
    address_lower_halfword_ba: bitarray = field(init=False)
    address_upper_halfword_ba: bitarray = field(init=False)
    data: bitarray = field(
        default_factory=lambda: bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    )

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

        self.address_ba: bitarray = uint_to_bitarray(self.address, address_len)

        self.address_lower_halfword: int = self.address
        self.address_lower_halfword_ba: bitarray = uint_to_bitarray(
            self.address_lower_halfword, address_len
        )

        self.address_upper_halfword: int = self.address + 2
        self.address_upper_halfword_ba: bitarray = uint_to_bitarray(
            self.address_upper_halfword, address_len
        )


@dataclass
class DeviceIdReg(Ads866xRegister):
    DEVICE_ADDR: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x00, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.DEVICE_ADDR = BitfieldSpec(
            slice(16, 20), {"DEFAULT_ADDR": bitarray(reverse_string("0000"))}
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
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x04, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.WKEY = BitfieldSpec(
            slice(8, 16), {"PROTECTION_KEY": uint_to_bitarray(0x69, 8)}
        )
        self.VDD_AL_DIS = BitfieldSpec(
            slice(5, 6),
            {
                "VDD_AL_ENABLED": bitarray(reverse_string("0")),
                "VDD_AL_DISABLED": bitarray(reverse_string("1")),
            },
        )
        self.IN_AL_DIS = BitfieldSpec(
            slice(4, 5),
            {
                "IN_AL_ENABLED": bitarray(reverse_string("0")),
                "IN_AL_DISABLED": bitarray(reverse_string("1")),
            },
        )
        self.RSTN_APP = BitfieldSpec(
            slice(2, 3),
            {
                "RSTN_POR": bitarray(reverse_string("0")),
                "RSTN_APP": bitarray(reverse_string("1")),
            },
        )
        self.NAP_EN = BitfieldSpec(
            slice(1, 2),
            {
                "NAP_DISABLED": bitarray(reverse_string("0")),
                "NAP_ENABLED": bitarray(reverse_string("1")),
            },
        )
        self.PWRDN = BitfieldSpec(
            slice(0, 1),
            {
                "MODE_ACTIVE": bitarray(reverse_string("0")),
                "MODE_PWR_DOWN": bitarray(reverse_string("1")),
            },
        )


@dataclass
class SdiCtlReg(Ads866xRegister):
    SDI_MODE: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x08, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.SDI_MODE = BitfieldSpec(
            slice(0, 2),
            {
                "SPI_MODE_0_CPOL_0_CPHA_0": bitarray(reverse_string("00")),
                "SPI_MODE_1_CPOL_0_CPHA_1": bitarray(reverse_string("01")),
                "SPI_MODE_2_CPOL_1_CPHA_0": bitarray(reverse_string("10")),
                "SPI_MODE_3_CPOL_1_CPHA_1": bitarray(reverse_string("11")),
            },
        )


@dataclass
class SdoCtlReg(Ads866xRegister):
    GPO_VAL: BitfieldSpec = field(init=False)
    SDO1_CONFIG: BitfieldSpec = field(init=False)
    SSYNC_CLK: BitfieldSpec = field(init=False)
    SDO_MODE: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x0C, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.GPO_VAL = BitfieldSpec(
            slice(12, 13),
            {
                "LOW": bitarray(reverse_string("0")),
                "HIGH": bitarray(reverse_string("1")),
            },
        )
        self.SDO1_CONFIG = BitfieldSpec(
            slice(8, 10),
            {
                "SDO1_TRISTATE": bitarray(reverse_string("00")),
                "SDO1_ALARM": bitarray(reverse_string("01")),
                "SDO1_GPO": bitarray(reverse_string("10")),
                "SDO1_SPI_2BIT_SDO": bitarray(reverse_string("11")),
            },
        )
        self.SSYNC_CLK = BitfieldSpec(
            slice(6, 7),
            {
                "CLK_EXT": bitarray(reverse_string("0")),
                "CLK_INT": bitarray(reverse_string("1")),
            },
        )
        self.SDO_MODE = BitfieldSpec(
            slice(0, 2),
            {
                "SDO_DEFAULT_CLK": bitarray(reverse_string("00")),
                "SDO_INTERNAL_CLK": bitarray(reverse_string("11")),
            },
        )


@dataclass
class DataOutCtlReg(Ads866xRegister):
    DEVICE_ADDR_INCL: BitfieldSpec = field(init=False)
    VDD_ACTIVE_L_ALARM_INCL: BitfieldSpec = field(init=False)
    VDD_ACTIVE_H_ALARM_INCL: BitfieldSpec = field(init=False)
    IN_ACTIVE_L_ALARM_INCL: BitfieldSpec = field(init=False)
    IN_ACTIVE_H_ALARM_INCL: BitfieldSpec = field(init=False)
    RANGE_INCL: BitfieldSpec = field(init=False)
    PAR_EN: BitfieldSpec = field(init=False)
    DATA_VAL: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x10, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.DEVICE_ADDR_INCL = BitfieldSpec(
            slice(14, 15),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.VDD_ACTIVE_L_ALARM_INCL = BitfieldSpec(
            slice(13, 14),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.VDD_ACTIVE_H_ALARM_INCL = BitfieldSpec(
            slice(12, 13),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.IN_ACTIVE_L_ALARM_INCL = BitfieldSpec(
            slice(11, 12),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.IN_ACTIVE_H_ALARM_INCL = BitfieldSpec(
            slice(10, 11),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.RANGE_INCL = BitfieldSpec(
            slice(8, 9),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.PAR_EN = BitfieldSpec(
            slice(3, 4),
            {
                "EXCLUDE": bitarray(reverse_string("0")),
                "INCLUDE": bitarray(reverse_string("1")),
            },
        )
        self.DATA_VAL = BitfieldSpec(
            slice(0, 3),
            {
                "CONVERSION_RESULT": bitarray(reverse_string("000")),
                "ALL_ZEROS": bitarray(reverse_string("100")),
                "ALL_ONES": bitarray(reverse_string("101")),
                "ALTERNATE_ZEROS_ONES": bitarray(reverse_string("110")),
                "ALTERNATE_DOUBLE_ZEROS_DOUBLE_ONES": bitarray(reverse_string("111")),
            },
        )


@dataclass
class RangeSelReg(Ads866xRegister):
    INTREF_DIS: BitfieldSpec = field(init=False)
    RANGE_SEL: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x14, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.INTREF_DIS = BitfieldSpec(
            slice(6, 7),
            {
                "INTREF_ENABLE": bitarray(reverse_string("0")),
                "INTREF_DISABLE": bitarray(reverse_string("1")),
            },
        )
        self.RANGE_SEL = BitfieldSpec(
            slice(0, 4),
            {
                "BIPOLAR_12V288": bitarray(reverse_string("0000")),
                "BIPOLAR_10V24": bitarray(reverse_string("0001")),
                "BIPOLAR_6V144": bitarray(reverse_string("0010")),
                "BIPOLAR_5V12": bitarray(reverse_string("0011")),
                "BIPOLAR_2V56": bitarray(reverse_string("0100")),
                "UNIPOLAR_12V288": bitarray(reverse_string("1000")),
                "UNIPOLAR_10V24": bitarray(reverse_string("1001")),
                "UNIPOLAR_6V144": bitarray(reverse_string("1010")),
                "UNIPOLAR_5V12": bitarray(reverse_string("1011")),
            },
        )


@dataclass
class AlarmReg(Ads866xRegister):
    ACTIVE_VDD_L_FLAG: BitfieldSpec = field(init=False)
    ACTIVE_VDD_H_FLAG: BitfieldSpec = field(init=False)
    ACTIVE_IN_L_FLAG: BitfieldSpec = field(init=False)
    ACTIVE_IN_H_FLAG: BitfieldSpec = field(init=False)
    TRP_VDD_L_FLAG: BitfieldSpec = field(init=False)
    TRP_VDD_H_FLAG: BitfieldSpec = field(init=False)
    TRP_IN_L_FLAG: BitfieldSpec = field(init=False)
    TRP_IN_H_FLAG: BitfieldSpec = field(init=False)
    OVW_ALARM: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=0x20, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.ACTIVE_VDD_L_FLAG = BitfieldSpec(
            slice(15, 16),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.ACTIVE_VDD_H_FLAG = BitfieldSpec(
            slice(14, 15),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.ACTIVE_IN_L_FLAG = BitfieldSpec(
            slice(11, 12),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.ACTIVE_IN_H_FLAG = BitfieldSpec(
            slice(10, 11),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.TRP_VDD_L_FLAG = BitfieldSpec(
            slice(7, 8),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.TRP_VDD_H_FLAG = BitfieldSpec(
            slice(6, 7),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.TRP_IN_L_FLAG = BitfieldSpec(
            slice(5, 6),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.TRP_IN_H_FLAG = BitfieldSpec(
            slice(4, 5),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )
        self.OVW_ALARM = BitfieldSpec(
            slice(0, 1),
            {
                "NO_ALARM": bitarray(reverse_string("0")),
                "ALARM": bitarray(reverse_string("1")),
            },
        )


@dataclass
class AlarmHThReg(Ads866xRegister):  # Alarm hysteresis and high threshold
    INP_ALARM_HYST: BitfieldSpec = field(init=False)
    INP_ALARM_HIGH_TH: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=24, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.INP_ALARM_HYST = BitfieldSpec(
            slice(30, 32),
            {
                "HYST_00": bitarray(reverse_string("00")),
                "HYST_01": bitarray(reverse_string("01")),
                "HYST_10": bitarray(reverse_string("10")),
                "HYST_11": bitarray(reverse_string("11")),
            },
        )
        self.INP_ALARM_HIGH_TH = BitfieldSpec(
            slice(4, 16), {"DEFAULT": uint_to_bitarray(0xFFF, 12)}
        )


@dataclass
class AlarmLThReg(Ads866xRegister):  # Alarm low threshold
    INP_ALARM_LOW_TH: BitfieldSpec = field(init=False)

    def __init__(
        self,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        super().__init__(address=28, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.INP_ALARM_LOW_TH = BitfieldSpec(
            slice(4, 16), {"DEFAULT": uint_to_bitarray(0x000, 12)}
        )
