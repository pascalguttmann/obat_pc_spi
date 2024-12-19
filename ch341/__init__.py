from typing import Optional
from ctypes import (
    c_bool,
    c_uint8,
    c_uint32,
    c_int32,
    c_ulong,
    c_ulonglong,
    c_void_p,
    create_string_buffer,
    byref,
)

import sys


from .constants import SPI_CS_STATE_USED, SPI_OUTPUT_MODE_1LINE, SPI_DATA_MODE_MSB
from .dll import load_CH341DLL as ch341dll
from ..spi_master_base import SpiMasterBase


class CH341(SpiMasterBase):
    def __init__(
        self, id: Optional[int] = None, device_path: Optional[str] = None
    ) -> None:
        """Initializes the CH341 as spi master with mode 0 (CPHA = 0, CPOL = 0) with a
        fixed clock rate of approx. 1.6 MHz

        :param id: CH341 device number index, defaults to 0 on Windows and
        /dev/ch341_pis1 on posix systems
        """
        if sys.platform == "win32":
            if id is None:
                self._id = id
                self._fd = None
                self._device_path = device_path
                self._init_win()
        else:
            if device_path is None:
                self._id = id
                self._fd = None
                self._device_path = b"/dev/ch341x_pis1"
                self._init_posix()

    def _init_win(self) -> None:
        """Initializes the CH341 as spi master on windows systems"""
        self._fd = c_int32(
            ch341dll.CH341OpenDevice(c_ulong(self._id))  # pyright: ignore
        )
        if self._fd.value < c_int32(0).value:
            raise OSError(f"CH341OpenDevice({self._id}) failed.")

        iMode = c_ulong(SPI_DATA_MODE_MSB | SPI_OUTPUT_MODE_1LINE)
        ret = ch341dll.CH341OpenDevice(c_ulong(self._fd), iMode)  # pyright: ignore
        if ret == c_bool(False):
            raise OSError(f"CH34xSetStream({self._fd}, {iMode}) failed.")

        raise NotImplementedError

    def _init_posix(self) -> None:
        """Initializes the CH341 as spi master on posix systems"""
        self._fd = c_int32(
            ch341dll.CH341OpenDevice(  # pyright: ignore
                create_string_buffer(
                    self._device_path.encode("utf-8")  # pyright: ignore
                )
            )
        )
        if self._fd.value < c_int32(0).value:
            raise OSError(f"CH341OpenDevice({self._device_path}) failed.")

        # Mandatory call to CH34x_GetChipVersion for operation of other API calls
        chip_ver: c_uint8 = c_uint8(0)
        ret = c_bool(
            ch341dll.CH34x_GetChipVersion(self._fd, byref(chip_ver))  # pyright: ignore
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
        if sys.platform == "win32":
            return self._transfer_win(cs, buf)
        else:
            return self._transfer_posix(cs, buf)

    def _transfer_win(self, cs: int, buf: bytearray) -> bytearray:
        cbuf = (c_uint8 * len(buf)).from_buffer(buf)

        ret = c_bool(
            ch341dll.CH341StreamSPI5(  # pyright: ignore
                c_ulong(self._id),  # pyright: ignore
                c_ulong(SPI_CS_STATE_USED | cs),
                c_ulong(len(buf)),
                byref(cbuf),
                c_void_p(0),
            )
        )
        if ret == c_bool(False):
            raise OSError(
                f"CH341StreamSPI5({self._id}, {hex(SPI_CS_STATE_USED | cs)}, {len(buf)}, {byref(cbuf)}, {c_void_p(0)}) failed."
            )

        return bytearray(cbuf)

    def _transfer_posix(self, cs: int, buf: bytearray) -> bytearray:
        cbuf = (c_uint8 * len(buf)).from_buffer(buf)

        ret = c_bool(
            ch341dll.CH34xStreamSPIx(  # pyright: ignore
                self._fd,
                c_uint32(SPI_CS_STATE_USED | cs),
                c_uint32(len(buf)),
                byref(cbuf),
                c_void_p(0),
            )
        )
        if ret == c_bool(False):
            raise OSError(
                f"CH34xStreamSPIx({self._fd}, {hex(SPI_CS_STATE_USED | cs)}, {len(buf)}, {byref(cbuf)}, {c_void_p(0)}) failed."
            )

        return bytearray(cbuf)
