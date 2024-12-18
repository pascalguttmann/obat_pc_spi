from abc import ABC, abstractmethod
from typing import TypeVar


class SpiMasterBase(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Initialize the SPI bus master to allow data transfer to slave devices"""

    @abstractmethod
    def transfer(self, cs: int, buf: bytearray):
        """Transfer content of 'buf' via SPI bus with chip select 'cs' enabled

        :param cs: id of chip select used for SPI transfer
        :param buf: bytearray containing bytes to be sent, will be filled with received bytes
        """


SpiMaster = TypeVar("SpiMaster", bound=SpiMasterBase)
