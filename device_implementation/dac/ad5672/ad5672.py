"""Analog Devices
Octal, 12-Bit nanoDAC+ with 2 ppm/°C Reference, SPI Interface

Datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad5672r_5676r.pdf
"""

from device_implementation.dac import DacBase

from device_implementation.dac.ad5672.operations import (
    Nop,
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
