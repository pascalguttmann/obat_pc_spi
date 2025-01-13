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
from typing import Callable, Optional

from functional_operations import (
    Initialize,
    ReadVoltage,
    Ads866xInputRange,
    Ads866xGpoVal,
    SetGpo,
    ClearGpo,
)
from spi_elements.async_return import AsyncReturn
from spi_elements.spi_operation_request_iterator import (
    SequenceTransferOperationRequest,
    SingleTransferOperationRequest,
)


class Ads866x(AdcBase):
    def __init__(self) -> None:
        super().__init__()

    def initialize(
        self,
        callback: Optional[Callable[..., None]] = None,
        input_range: Ads866xInputRange = Ads866xInputRange.UNIPOLAR_5V12,
    ) -> AsyncReturn:
        """Adc device must implement the behavior to initialize the hardware
        and enable subsequent calls to other methods of the adc."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SequenceTransferOperationRequest(
                operation=Initialize(input_range),
                callback=ar.get_callback(),
            ),
        )
        return ar

    def read(self, callback: Optional[Callable[..., None]] = None) -> AsyncReturn:
        """Read the quantizied analog voltage(s) and return the voltage as float."""
        ar = AsyncReturn(callback)

        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                operation=ReadVoltage(),
                callback=ar.get_callback(),
            ),
        )
        return ar

    def write_gpo(
        self,
        callback: Optional[Callable[..., None]] = None,
        gpo_val: Optional[Ads866xGpoVal] = None,
    ):
        """Write the specified value to the digital general purpose output of the adc."""
        if not gpo_val:
            raise ValueError("gpo_val must be defined by caller")

        ar = AsyncReturn(callback)
        if gpo_val == Ads866xGpoVal.HIGH:
            self._put_unprocessed_operation_request(
                SingleTransferOperationRequest(
                    operation=SetGpo(),
                    callback=ar.get_callback(),
                )
            )
        elif gpo_val == Ads866xGpoVal.LOW:
            self._put_unprocessed_operation_request(
                SingleTransferOperationRequest(
                    operation=ClearGpo(),
                    callback=ar.get_callback(),
                )
            )
        else:
            raise RuntimeError(  # pyright: ignore
                f"Ads866xGpoVal is unknown: {gpo_val}"
            )
        return ar
