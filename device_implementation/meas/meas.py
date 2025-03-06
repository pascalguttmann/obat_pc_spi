from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Callable, Optional, cast
from enum import Enum
from functools import partial

from bitarray import bitarray
from util.util_bitarray import uint_to_bitarray

from spi_elements.async_return import AsyncReturn
from spi_elements.aggregate_operation_request_iterator import (
    AggregateOperationRequestIterator,
)
from device_implementation.dac.ad5672 import Ad5672
from device_implementation.adc.ads866x import Ads866x, Ads866xInputRange, Ads866xGpoVal

# From Meas Schematic 2.0.0:
#
# spi_operation_request_iterator[0] = voltage adc
# spi_operation_request_iterator[1] = current adc
# spi_operation_request_iterator[2] = temperature adc


class Meas(AggregateOperationRequestIterator):

    _meas_zero_offset_current: float = 25.0 - 0.4  # A
    _meas_sensitivity: float = 0.1  # V/A

    def __init__(self) -> None:
        super().__init__(
            [
                Ads866x(),
                Ads866x(),
                Ads866x(),
            ]
        )

    def get_pre_transfer_initialization(self) -> Sequence[bitarray]:
        return []

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
            self.get_volt_adc().nop(callback=collect_ops_responses),
            self.get_curr_adc().nop(callback=collect_ops_responses),
            self.get_temp_adc().nop(callback=collect_ops_responses),
        ]

        return ar

    def initialize(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Initialize the Measurement Electronic to be used with other class methods
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
            self.get_volt_adc().initialize(
                callback=collect_ops_responses,
                input_range=Ads866xInputRange.UNIPOLAR_5V12,
            ),
            self.get_volt_adc().write_gpo(
                callback=collect_ops_responses,
                gpo_val=Ads866xGpoVal.HIGH,
            ),
            self.get_curr_adc().initialize(
                callback=collect_ops_responses,
                input_range=Ads866xInputRange.UNIPOLAR_5V12,
            ),
            self.get_curr_adc().write_gpo(
                callback=collect_ops_responses,
                gpo_val=Ads866xGpoVal.HIGH,
            ),
            self.get_temp_adc().initialize(
                callback=collect_ops_responses,
                input_range=Ads866xInputRange.UNIPOLAR_5V12,
            ),
            self.get_temp_adc().write_gpo(
                callback=collect_ops_responses,
                gpo_val=Ads866xGpoVal.HIGH,
            ),
        ]
        return ar

    def read(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Read the voltage, current and temperature measured by the
        measurement electronic.

        :return: tuple of voltage [V], current [A] and temperature [°C].
        (voltage: float, current: float, temperature: float)"""

        def adc_volt_voltage_to_input_voltage(voltage: float) -> float:
            return voltage

        def adc_curr_voltage_to_input_current(voltage: float) -> float:
            return voltage / self._meas_sensitivity - self._meas_zero_offset_current

        def adc_temp_voltage_to_input_temperature(voltage: float) -> float:
            # From labeling of LKM Type 102 with Thermocouple Type K:
            # 0V...10V linearly maps to 0°C ... 600°C
            return voltage / 5.0 * 600

        ar = AsyncReturn(callback)
        sequence_callback = ar.get_callback()

        responses = [
            {"data": None, "called": False},
            {"data": None, "called": False},
            {"data": None, "called": False},
        ]

        def collect_ops_responses(response: Any, id: int):
            responses[id]["data"] = response
            responses[id]["called"] = True

            if all([rsp["called"] for rsp in responses]) and sequence_callback:
                sequence_return = (
                    adc_volt_voltage_to_input_voltage(responses[0]["data"]),
                    adc_curr_voltage_to_input_current(responses[1]["data"]),
                    adc_temp_voltage_to_input_temperature(responses[2]["data"]),
                )
                sequence_callback(sequence_return)
            return None

        self.get_volt_adc().read(callback=partial(collect_ops_responses, id=0))
        self.get_curr_adc().read(callback=partial(collect_ops_responses, id=1))
        self.get_temp_adc().read(callback=partial(collect_ops_responses, id=2))
        return ar

    def get_volt_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[0])

    def get_curr_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[1])

    def get_temp_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[2])
