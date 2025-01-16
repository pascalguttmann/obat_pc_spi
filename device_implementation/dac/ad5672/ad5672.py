"""Analog Devices
Octal, 12-Bit nanoDAC+ with 2 ppm/°C Reference, SPI Interface

Datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad5672r_5676r.pdf
"""

from typing import Callable, Optional
from math import floor

from util import uint_to_bitarray

from device_implementation.dac import DacBase
from device_implementation.dac.ad5672.operations import (
    Nop,
    Initialize,
    WriteInputRegister,
    LoadAllChannels,
)
from spi_elements.async_return import AsyncReturn
from spi_elements.spi_operation_request_iterator import (
    SequenceTransferOperationRequest,
    SingleTransferOperationRequest,
)


class Ad5672(DacBase):
    def __init__(self) -> None:
        super().__init__()

    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        return SingleTransferOperationRequest(
            operation=Nop(),
            callback=None,
        )

    def nop(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Perform no operation. Can be used to wait for a cycle to
        synchoronize multiple spi_elements."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                operation=Nop(),
                callback=ar.get_callback(),
            ),
        )
        return ar

    def initialize(self, callback: Optional[Callable[..., None]] = None) -> AsyncReturn:
        """Dac device must implement the behavior to initialize the hardware
        and enable subsequent calls to other methods of the dac."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SequenceTransferOperationRequest(
                operation=Initialize(),
                callback=ar.get_callback(),
            )
        )
        return ar

    def write(
        self,
        callback: Optional[Callable[..., None]] = None,
        addr: int | None = None,
        voltage: float | None = None,
    ) -> AsyncReturn:
        """Write the quantized analog voltage to the dac without updating the
        analog output voltage. To update all prior written voltages to the
        output use .load_all_channels().

        :param addr: address of the dac channel. Must be in the interval [0, 7].
        :param voltage: the voltage that should be set at the channel.
        Constrained to the interval [0V, 5V]. The actual voltage is quantized
        and floored to the next quantization step resulting from the resolution
        of the dac."""
        if not addr:
            raise ValueError("Address must not be None.")
        if not voltage:
            raise ValueError("Voltage must not be None.")
        if addr < 0 or addr > 7:
            raise ValueError(
                f"Addrress must be in the interval [0, 7], but is: {addr=}"
            )

        def clamp(val: int, min_val: int, max_val: int) -> int:
            return min(max(val, min_val), max_val)

        resolution: int = 2**12
        n_max: int = resolution - 1
        n: int = clamp(floor(n_max * voltage / 5.0), 0, n_max)

        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                operation=WriteInputRegister(
                    addr=uint_to_bitarray(addr, 4),
                    data=uint_to_bitarray(n, 12),
                ),
                callback=ar.get_callback(),
            ),
        )
        return ar

    def load_all_channels(
        self, callback: Optional[Callable[..., None]] = None
    ) -> AsyncReturn:
        """Update all analog output voltages according to the data written
        prior with .write()."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                operation=LoadAllChannels(),
                callback=ar.get_callback(),
            ),
        )
        return ar
