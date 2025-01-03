from __future__ import annotations
from typing import Callable, Optional

from spi_master_base import SpiMasterBase


class Virtual(SpiMasterBase):
    def __init__(
        self,
        init_func: Optional[Callable[[], None]] = None,
        transfer_func: Optional[Callable[[int, bytearray], bytearray]] = None,
    ) -> None:
        """Creates a virtual SpiMaster object with no physical hardware.
        Intended use as a mock for unittests.
        """
        self._init_called = False
        self._init_func = init_func
        self._transfer_func = transfer_func

    def init(self) -> None:
        """Initializes the virtual SpiMaster."""
        self._init_called = True
        if self._init_func:
            return self._init_func()

    def transfer(self, cs: int, buf: bytearray) -> bytearray:
        """Transfer content of 'buf' via SPI bus with chip select 'cs' enabled

        :param cs: id of chip select used for SPI transfer
        :param buf: bytearray containing bytes to be sent
        :return: bytearray containing bytes received
        """
        if not self._init_called:
            raise RuntimeError("Virtual SpiMaster, transfer() without initialization.")

        if self._transfer_func:
            return self._transfer_func(cs, buf)

        return self._transfer_fallback(cs, buf)

    def _transfer_fallback(self, cs: int, buf: bytearray) -> bytearray:
        if not hasattr(self, "_counter"):
            self._counter = 0

        num_maxsize: int = 2 ** (8 * len(buf))
        num: int = self._counter % num_maxsize

        self._counter += 1

        return bytearray(num.to_bytes(len(buf), "big", signed=False))
