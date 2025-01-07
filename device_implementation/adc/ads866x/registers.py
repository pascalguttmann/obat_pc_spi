from dataclasses import dataclass, field
from bitarray import bitarray


def int_to_bitarray(n: int, bitlen: int):
    return bitarray(bin(n)[2:].zfill(bitlen))


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
class RstPwrctlReg(Ads866xRegister):
    WKEY: bitarray = field(init=False)
    VDD_AL_DIS: bitarray = field(init=False)
    IN_AL_DIS: bitarray = field(init=False)
    RSTN_APP: bitarray = field(init=False)
    NAP_EN: bitarray = field(init=False)
    PWRDN: bitarray = field(init=False)

    def __init__(
        self, data: bitarray = bitarray("00000000 00000000 00000000 00000000")
    ):
        super().__init__(address=0x04, data=data)

    def __post_init__(self):
        super().__post_init__()
        self.WKEY = self.data[8:16]
        self.VDD_AL_DIS = self.data[5:6]
        self.IN_AL_DIS = self.data[4:5]
        self.RSTN_APP = self.data[2:3]
        self.NAP_EN = self.data[1:2]
        self.PWRDN = self.data[0:1]
