from typing import Optional

import sys

from ..spi_master_base import SpiMasterBase


class CH341(SpiMasterBase):
    def __init__(self, id: Optional[int | str] = None) -> None:
        """Initializes the CH341 as spi master with mode 0 (CPHA = 0, CPOL = 0) with a
        fixed clock rate of approx. 1.6 MHz

        :param id: CH341 device number index, defaults to 0 on Windows and
        /dev/ch341_pis1 on posix systems
        """
        if id is None:
            if sys.platform == "win32":
                id = 0
                self._fd = id
                self._device_path = None
                self._init_win()
            else:
                id = "/dev/ch341_pis1"
                self._fd = None
                self._device_path = id
                self._init_posix()

    def _init_win(self) -> None:
        """Initializes the CH341 as spi master on windows systems"""
        raise NotImplementedError

    def _init_posix(self) -> None:
        """Initializes the CH341 as spi master on posix systems"""
        raise NotImplementedError

    def transfer(self, cs: int, buf: bytearray) -> bytearray:
        """Transfer content of 'buf' via SPI bus with chip select 'cs' enabled

        :param cs: id of chip select used for SPI transfer
        :param buf: bytearray containing bytes to be sent
        :return: bytearray containing bytes received
        """
        raise NotImplementedError
