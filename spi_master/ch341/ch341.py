from __future__ import annotations

from typing import Optional
from ctypes import (
    c_bool,
    c_uint8,
    c_uint32,
    c_int32,
    c_void_p,
    create_string_buffer,
    byref,
)

import copy
import sys


from spi_master.ch341.constants import (
    SPI_CS_STATE_USED,
    SPI_OUTPUT_MODE_1LINE,
    SPI_OUTPUT_MODE_2LINE,
    SPI_DATA_MODE_LSB,
    SPI_DATA_MODE_MSB,
)
from spi_master.ch341.dll import ch341dll
from spi_master.spi_master_base import SpiMasterBase


class CH341(SpiMasterBase):
    def __init__(
        self, id: Optional[int] = None, device_path: Optional[str] = None
    ) -> None:
        """Creates the CH341 object as spi master with mode 0 (CPHA = 0, CPOL =
        0) with a fixed clock rate of approx. 1.6 MHz

        :param id: CH341 device number index, defaults to 0 on Windows and
        /dev/ch341_pis1 on posix systems
        """
        if sys.platform == "win32":
            if id is None:
                self._id = 0
            else:
                self._id = id
            self._fd = None
            self._device_path = device_path
        else:
            if device_path is None:
                self._device_path = b"/dev/ch34x_pis1"
            else:
                self._device_path = device_path
            self._id = id
            self._fd = None

    def init(self) -> None:
        """Initializes the CH341 as spi master with mode 0 (CPHA = 0, CPOL = 0) with a
        fixed clock rate of approx. 1.6 MHz"""
        if sys.platform == "win32":
            self._init_win()
        else:
            self._init_posix()

    def _init_win(self) -> None:
        """Initializes the CH341 as spi master on windows systems"""
        self._fd = c_int32(ch341dll.CH341OpenDevice((self._id)))
        if self._fd.value < c_int32(0).value:
            raise OSError(f"CH341OpenDevice({self._id}) failed.")

        # SPI_DATA_MODE_MSB Does NOT work as expected from API Doc
        iMode = SPI_DATA_MODE_LSB | SPI_OUTPUT_MODE_1LINE
        ret = ch341dll.CH341SetStream((self._fd), iMode)  # pyright: ignore
        if ret == c_bool(False):
            raise OSError(f"CH34xSetStream({self._fd}, {iMode}) failed.")

        return

    def _init_posix(self) -> None:
        """Initializes the CH341 as spi master on posix systems"""
        self._fd = c_int32(
            ch341dll.CH34xOpenDevice(  # pyright: ignore
                create_string_buffer(self._device_path)  # pyright: ignore
            )
        )
        if self._fd.value < c_int32(0).value:
            raise OSError(f"CH34xOpenDevice({self._device_path}) failed.")

        # Mandatory call to CH34x_GetChipVersion for operation of other API calls

        chip_ver = create_string_buffer(256)
        ret = c_bool(
            ch341dll.CH34x_GetChipVersion(self._fd, chip_ver)  # pyright: ignore
        )  # pyright: ignore
        if ret == c_bool(False):
            raise OSError(
                f"CH34x_GetChipVersion({self._fd}, {byref(chip_ver)}) failed."
            )

        iMode = c_uint8(SPI_DATA_MODE_MSB | SPI_OUTPUT_MODE_1LINE)
        ret = c_bool(ch341dll.CH34xSetStream(self._fd, iMode))  # pyright: ignore
        if ret == c_bool(False):
            raise OSError(f"CH34xSetStream({self._fd}, {iMode}) failed.")

        return

    def transfer(self, cs: int, buf: bytearray) -> bytearray:
        """Transfer content of 'buf' via SPI bus with chip select 'cs' enabled

        :param cs: id of chip select used for SPI transfer
        :param buf: bytearray containing bytes to be sent
        :return: bytearray containing bytes received
        """

        buf = copy.deepcopy(buf)
        if sys.platform == "win32":
            return self._transfer_win(cs, buf)
        else:
            return self._transfer_posix(cs, buf)

    def _transfer_win(self, cs: int, buf: bytearray) -> bytearray:
        cbuf = (c_uint8 * len(buf)).from_buffer(super().reverse_bit_order(buf))

        ret = c_bool(
            ch341dll.CH341StreamSPI4(  # pyright: ignore
                (self._id),  # pyright: ignore
                (SPI_CS_STATE_USED | cs),
                (len(buf)),
                byref(cbuf),
            )
        )
        if ret == c_bool(False):
            raise OSError(
                f"CH341StreamSPI4({self._id}, {hex(SPI_CS_STATE_USED | cs)}, {len(buf)}, {byref(cbuf)}) failed."
            )

        return super().reverse_bit_order(bytearray(cbuf))

    def _transfer_posix(self, cs: int, buf: bytearray) -> bytearray:
        cbuf = (c_uint8 * len(buf)).from_buffer(buf)

        ret = c_bool(
            ch341dll.CH34xStreamSPI4(  # pyright: ignore
                self._fd,
                c_uint32(SPI_CS_STATE_USED | cs),
                c_uint32(len(buf)),
                cbuf,
            )
        )
        if ret == c_bool(False):
            raise OSError(
                f"CH34xStreamSPIx({self._fd}, {hex(SPI_CS_STATE_USED | cs)}, {len(buf)}, {byref(cbuf)}, {c_void_p(0)}) failed."
            )

        return bytearray(cbuf)
