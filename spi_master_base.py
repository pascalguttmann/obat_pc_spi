from abc import ABC, abstractmethod
from typing import TypeVar


class SpiMasterBase(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the SPI bus master to allow data transfer to slave devices"""

    @abstractmethod
    def transfer(self, cs: int, buf: bytearray) -> bytearray:
        """Transfer content of 'buf' via SPI bus with chip select 'cs' enabled and
        receive bytes

        :param cs: id of chip select used for SPI transfer
        :param buf: bytearray containing bytes to be sent
        :return: bytearray containing bytes received
        """

    @staticmethod
    def reverse_bit_order(buf: bytearray) -> bytearray:
        """Reverse the bit order of individual bytes in a bytearray. This allows for sw
        implementation of MSB/LSB first.

        :param buf: buffer of bytes to reverse the bit order
        :return: bytearray of bytes with reversed bit order
        """
        result = bytearray(len(buf))
        for i, byte in enumerate(buf):
            reversed_byte = 0
            for j in range(8):
                reversed_byte <<= 1  # shift left
                reversed_byte |= byte & 1
                byte >>= 1  # shift right
            result[i] = reversed_byte
        return result


SpiMaster = TypeVar("SpiMaster", bound=SpiMasterBase)
