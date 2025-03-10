from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Callable, Optional, cast

from bitarray import bitarray
from util.util_bitarray import uint_to_bitarray

from spi_elements.async_return import AsyncReturn
from spi_elements.aggregate_operation_request_iterator import (
    AggregateOperationRequestIterator,
)
from device_implementation.enclosure import Enclosure, EnclosurePeltierPolarity
from device_implementation.pss import Pss, PssTrackingMode
from device_implementation.meas import Meas

# From Obat Instance_1 setup
#
# spi_operation_request_iterator[0] = Enclosure
# spi_operation_request_iterator[1] = Pss
# spi_operation_request_iterator[2] = Meas


class Obat(AggregateOperationRequestIterator):
    def __init__(self) -> None:
        super().__init__(
            [
                Enclosure(),
                Pss(),
                Meas(),
            ]
        )

    def get_pre_transfer_initialization(self) -> Sequence[bitarray]:
        dac_ad5672r_dcen_opcode = 0x800001
        dac_ad5672r_nop_opcode = 0x000000
        dac_ad5672r_word_bitlen = 24
        return [
            uint_to_bitarray(dac_ad5672r_dcen_opcode, dac_ad5672r_word_bitlen),
            uint_to_bitarray(dac_ad5672r_nop_opcode, dac_ad5672r_word_bitlen),
        ]

    def nop(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Perform no operation. Can be used to wait for a cycle to
        synchoronize multiple spi_elements."""
        ar = AsyncReturn(callback)
        sequence_callback = ar.get_callback()

        responses = []

        def collect_ops_responses(response: Any):
            responses.append(response)
            if len(responses) == len(sub_ar) and sequence_callback:
                sequence_return = None
                sequence_callback(sequence_return)
            return None

        sub_ar = [
            self.get_enclosure().nop(callback=collect_ops_responses),
            self.get_pss().nop(callback=collect_ops_responses),
            self.get_meas().nop(callback=collect_ops_responses),
        ]

        return ar

    def get_enclosure(self) -> Enclosure:
        return cast(Enclosure, self._operation_request_iterators[0])

    def get_pss(self) -> Pss:
        return cast(Pss, self._operation_request_iterators[0])

    def get_meas(self) -> Meas:
        return cast(Meas, self._operation_request_iterators[0])

    def initialize(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Initialize the PowerSupplySink to be used with other class methods
        after initialization."""
        ar = AsyncReturn(callback)
        sequence_callback = ar.get_callback()

        responses = []

        def collect_ops_responses(response: Any):
            responses.append(response)
            if len(responses) == len(sub_ar) and sequence_callback:
                sequence_return = None
                sequence_callback(sequence_return)
            return None

        sub_ar = [
            self.get_enclosure().initialize(callback=collect_ops_responses),
            self.get_pss().initialize(callback=collect_ops_responses),
            self.get_meas().initialize(callback=collect_ops_responses),
        ]
        return ar
