from dataclasses import dataclass, field
from bitarray import bitarray


def int_to_bitarray(n: int, bitlen: int):
    return bitarray(bin(n)[2:].zfill(bitlen))


@dataclass
class Ads866xRegister:
    data: bitarray
    address: int
    address_lower_halfword: int = field(init=False)
    address_upper_halfword: int = field(init=False)
    address_ba: bitarray = field(init=False)
    address_lower_halfword_ba: bitarray = field(init=False)
    address_upper_halfword_ba: bitarray = field(init=False)

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
