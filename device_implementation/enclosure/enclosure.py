from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Callable, Optional, cast
from enum import Enum

from bitarray import bitarray
from util.util_bitarray import uint_to_bitarray

from spi_elements.async_return import AsyncReturn
from spi_elements.aggregate_operation_request_iterator import (
    AggregateOperationRequestIterator,
)
from device_implementation.dac.ad5672 import Ad5672

# From Enclosure Schematic 1.1.2:
#
# spi_operation_request_iterator[0] = dac


class EnclosurePeltierPolarity(Enum):
    cooling = 0
    heating = 1


class Enclosure(AggregateOperationRequestIterator):
    dac_dutycycle_heater_addr: int = 0
    dac_dutycycle_peltier_addr: int = 1
    dac_dutycycle_fan_addr: int = 2
    dac_polarity_heater_addr: int = 4  # ignored by hw if `JP101` pin 1 & 2 connected
    dac_polarity_peltier_addr: int = 5
    dac_polarity_fan_addr: int = 6  # ignored by hw if `JP102` pin 1 & 2 connected

    _enclosure_min_dutycycle = 0.0
    _enclosure_max_dutycycle = 1.0
    _enclosure_dutycycle_control_voltage_low_threshold = 0.5
    _enclosure_dutycycle_control_voltage_high_threshold = 4.5

    _enclosure_heater_power_max = 50  # W
    _enclosure_peltier_power_max = 144  # W

    def __init__(self) -> None:
        super().__init__(
            [
                Ad5672(),
            ]
        )

    def get_dac(self) -> Ad5672:
        return cast(Ad5672, self._operation_request_iterators[0])

    def _heater_power_to_dutycycle(self, power: float) -> float:
        return power / Enclosure._enclosure_heater_power_max

    def _peltier_power_to_dutycycle(self, power: float) -> float:
        return power / Enclosure._enclosure_peltier_power_max

    def get_pre_transfer_initialization(self) -> Sequence[bitarray]:
        dac_ad5672r_reset_opcode = 0x601234
        dac_ad5672r_dcen_opcode = 0x800001
        dac_ad5672r_word_bitlen = 24
        return [
            uint_to_bitarray(dac_ad5672r_reset_opcode, dac_ad5672r_word_bitlen),
            uint_to_bitarray(dac_ad5672r_dcen_opcode, dac_ad5672r_word_bitlen),
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
            self.get_dac().nop(callback=collect_ops_responses),
        ]

        return ar

    def initialize(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Initialize the Enclosure to be used with other class methods
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
            self.get_dac().initialize(callback=collect_ops_responses),
        ]
        return ar

    def _dutycycle_to_dac_voltage(self, dutycycle: float) -> float:
        if dutycycle >= Enclosure._enclosure_max_dutycycle:
            return 5.0
        elif dutycycle <= Enclosure._enclosure_min_dutycycle:
            return 0.0
        else:
            return (
                dutycycle
                * (
                    +Enclosure._enclosure_dutycycle_control_voltage_high_threshold
                    - Enclosure._enclosure_dutycycle_control_voltage_low_threshold
                )
                + Enclosure._enclosure_dutycycle_control_voltage_low_threshold
            )

    def write_fan(
        self,
        callback: Optional[Callable[..., None]] = None,
        fan_speed_duty_cycle: float = 0.0,
    ) -> AsyncReturn:
        """Write a given fan speed to the enclosure electronics.
        The fan spped shall be specified in the interval [0, 1].
        If a specified value is not in the interval it is clamped to the
        closest border of the interval.

        :param fan_speed_duty_cycle: float specifying the duty cycle of the
        applied voltage at the fan.
        :return: None (in AsyncReturn)
        """
        ar = AsyncReturn(callback)

        dac_voltage = self._dutycycle_to_dac_voltage(fan_speed_duty_cycle)

        _ = self.get_dac().write_and_load(
            callback=ar.get_callback(),
            addr=Enclosure.dac_dutycycle_fan_addr,
            voltage=dac_voltage,
        )

        return ar

    def write_heater(
        self, callback: Optional[Callable[..., None]] = None, heater_power: float = 0.0
    ) -> AsyncReturn:
        """Write a given heater power to the enclosure electronics.
        The heater power shall be specified in the interval [0W, 50W].
        If a specified value is not in the interval it is clamped to the
        closest border of the interval.

        :param heater_power: float specifying the power delivered to the
        resistive heater in Watt.
        :return: None (in AsyncReturn)
        """
        ar = AsyncReturn(callback)

        dutycycle = self._heater_power_to_dutycycle(heater_power)

        dac_voltage = self._dutycycle_to_dac_voltage(dutycycle)

        _ = self.get_dac().write_and_load(
            callback=ar.get_callback(),
            addr=Enclosure.dac_dutycycle_heater_addr,
            voltage=dac_voltage,
        )

        return ar

    def write_peltier(
        self,
        callback: Optional[Callable[..., None]] = None,
        peltier_power: float = 0.0,
        peltier_polarity: EnclosurePeltierPolarity | None = None,
    ) -> AsyncReturn:
        """Write a given peltier power to the enclosure electronics.
        The peltier power shall be specified in the interval [0W, 144W].
        If a specified value is not in the interval it is clamped to the
        closest border of the interval.
        The polarity of the voltage applied to the peltier element determines
        whether the peltier elements is heating or cooling and must be
        specified.

        :param peltier_power: float specifying the power delivered to the
        peltier in Watt.
        :param peltier_polarity: EnclosurePeltierPolarity specifying the
        polarity of the voltage applied to the peltier element.
        :return: None (in AsyncReturn)
        """
        ar = AsyncReturn(callback)

        if peltier_polarity is None:
            raise ValueError("peltier_polarity must be defined by caller")
        elif peltier_polarity == EnclosurePeltierPolarity.cooling:
            _ = self.get_dac().write(
                addr=Enclosure.dac_polarity_peltier_addr,
                voltage=0.0,
            )
        elif peltier_polarity == EnclosurePeltierPolarity.heating:
            _ = self.get_dac().write(
                addr=Enclosure.dac_polarity_peltier_addr,
                voltage=5.0,
            )

        dutycycle = self._peltier_power_to_dutycycle(peltier_power)

        dac_voltage = self._dutycycle_to_dac_voltage(dutycycle)

        _ = self.get_dac().write(
            addr=Enclosure.dac_dutycycle_peltier_addr,
            voltage=dac_voltage,
        )

        return ar
