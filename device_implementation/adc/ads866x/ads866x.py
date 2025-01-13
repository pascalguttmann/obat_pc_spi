"""Texas Instruments
ADS866x 12-Bit, High-Speed, Single-Supply, SAR ADC Data Acquisition System With
Programmable, Bipolar Input Ranges

- ADS8661: 1.25 MSPS
- ADS8665: 500 kSPS
- Software programmable input ranges:
    – Bipolar ranges: ±12.288 V, ±10.24 V, ±6.144 V, ±5.12 V, and ±2.56 V
    – Unipolar ranges: 0 V–12.288 V, 0 V–10.24 V, 0 V–6.144 V, and 0 V–5.12 V

Datasheet: https://www.ti.com/lit/ds/symlink/ads8661.pdf
"""

from adc_base import AdcBase
from typing import Callable, Optional, Any

from functional_operations import Initialize, ReadVoltage, Ads866xInputRange
from spi_elements.async_return import AsyncReturn
from spi_elements.spi_operation_request_iterator import (
    SequenceTransferOperationRequest,
    SingleTransferOperationRequest,
)


class Ads866x(AdcBase):
    def __init__(self) -> None:
        super().__init__()

    def initialize(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Adc device must implement the behavior to initialize the hardware
        and enable subsequent calls to other methods of the adc."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SequenceTransferOperationRequest(
                operation=Initialize(Ads866xInputRange.UNIPOLAR_5V12),
                callback=ar.get_callback(),
            ),
        )
        return ar

    def read(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Read the quantizied analog voltage(s) and return the voltage as float."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                operation=ReadVoltage(),
                callback=ar.get_callback(),
            ),
        )
        return ar
