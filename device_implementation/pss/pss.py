from __future__ import annotations

from typing import Any, Callable, Optional, cast
from enum import Enum
from functools import partial

from spi_elements.async_return import AsyncReturn
from spi_elements.aggregate_operation_request_iterator import (
    AggregateOperationRequestIterator,
    AggregateOperation,
)
from device_implementation.dac.ad5672 import Ad5672
from device_implementation.adc.ads866x import Ads866x, Ads866xInputRange

# From PowerSupplySink Schematic 1.0.0:
#
# spi_operation_request_iterator[0] = configuration dac
# spi_operation_request_iterator[1] = current adc
# spi_operation_request_iterator[2] = voltage adc


class Pss(AggregateOperationRequestIterator):
    def __init__(self) -> None:
        super().__init__(
            [
                Ad5672(),
                Ads866x(),
                Ads866x(),
            ]
        )

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

        # Add a delay for the conf DAC reset to finish before transimitting
        # init sequence for adc
        for _ in range(3):
            _ = self.get_curr_adc().nop()
            _ = self.get_volt_adc().nop()

        sub_ar = [
            self.get_conf_dac().initialize(callback=collect_ops_responses),
            self.get_curr_adc().initialize(callback=collect_ops_responses),
            self.get_volt_adc().initialize(callback=collect_ops_responses),
        ]
        return ar

    def read_output(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Read the output voltage and current of the power supply sink.

        :return: tuple of voltage and current. (voltage: float, current: float)
        """
        ar = AsyncReturn(callback)
        sequence_callback = ar.get_callback()

        responses = [None, None]

        def collect_ops_responses(id: int, response: Any):
            responses[id] = response
            if len(responses) == len(sub_ar) and sequence_callback:
                sequence_return = (responses[0], response[1])
                sequence_callback(sequence_return)
            return None

        sub_ar = [
            self.get_volt_adc().read(callback=partial(collect_ops_responses, id=0)),
            self.get_curr_adc().read(callback=partial(collect_ops_responses, id=1)),
        ]
        return ar

    # TODO: def write_config()
    # TODO: def connect_output()
    # TODO: def disconnect_output()

    def get_conf_dac(self) -> Ad5672:
        return cast(Ad5672, self._operation_request_iterators[0])

    def get_curr_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[1])

    def get_volt_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[2])
