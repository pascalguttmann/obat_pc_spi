from __future__ import annotations

from typing import Any, Callable, Optional, cast
from enum import Enum
from functools import partial

from spi_elements.async_return import AsyncReturn
from spi_elements.aggregate_operation_request_iterator import (
    AggregateOperationRequestIterator,
)
from device_implementation.dac.ad5672 import Ad5672
from device_implementation.adc.ads866x import Ads866x, Ads866xInputRange

# From PowerSupplySink Schematic 1.0.0:
#
# spi_operation_request_iterator[0] = configuration dac
# spi_operation_request_iterator[1] = current adc
# spi_operation_request_iterator[2] = voltage adc


class PssTrackingMode(Enum):
    current = 0
    voltage = 1


class Pss(AggregateOperationRequestIterator):
    conf_output_addr: int = 0
    conf_refselect_addr: int = 1
    conf_target_voltage_addr: int = 2
    conf_target_current_addr: int = 3
    conf_lower_voltage_limit_addr: int = 4
    conf_upper_voltage_limit_addr: int = 5
    conf_lower_current_limit_addr: int = 6
    conf_upper_current_limit_addr: int = 7

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
            self.get_curr_adc().initialize(
                callback=collect_ops_responses,
                input_range=Ads866xInputRange.UNIPOLAR_5V12,
            ),
            self.get_volt_adc().initialize(
                callback=collect_ops_responses,
                input_range=Ads866xInputRange.UNIPOLAR_5V12,
            ),
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

    def write_config(
        self,
        callback: Optional[Callable[..., None]] = None,
        tracking_mode: PssTrackingMode | None = None,
        target_voltage: float | None = None,
        target_current: float | None = None,
        upper_voltage_limit: float | None = None,
        lower_voltage_limit: float | None = None,
        upper_current_limit: float | None = None,
        lower_current_limit: float | None = None,
    ) -> AsyncReturn:
        """Write a given configuration to the PowerSupplySink.
        The voltages shall be specified in the interval [0V, 5V].
        The currents shall be specified in the interval [-20A, +20A]. Positive
        current flows out of the PowerSupplySink.
        If a specified value is not in the interval it is clamped to the
        closest border of the interval.

        :param tracking_mode: PssTrackingMode specifying either
        - PssTrackingMode.voltage
            - target_voltage is followed by PowerSupplySink
            - upper_current_limit limits the maximal current (out) of the PowerSupplySink
            - lower_current_limit limits the minimal current (out) of the PowerSupplySink
        - PssTrackingMode.current
            - target_current is followed by PowerSupplySink
            - upper_voltage_limit limits the maximal output voltage of the PowerSupplySink
            - lower_voltage_limit limits the minimal output voltage of the PowerSupplySink
        :param target_voltage: float specifying the target output voltage in Volts
        :param target_current: float specifying the target output current in Amperes.
        :param upper_voltage_limit: float specifying the upper voltage limit during current tracking
        :param lower_voltage_limit: float specifying the lower voltage limit during current tracking
        :param upper_current_limit: float specifying the upper current limit during voltage tracking
        :param lower_current_limit: float specifying the lower current limit during voltage tracking
        :return: None (in AsyncReturn)
        """

        if not tracking_mode:
            raise ValueError("tracking_mode must be defined by caller")
        if tracking_mode == PssTrackingMode.voltage:
            if not target_voltage:
                raise ValueError(
                    "target_voltage must be defined by caller for tracking_mode == PssTrackingMode.voltage"
                )
            if not upper_voltage_limit:
                raise ValueError(
                    "upper_voltage_limit must be defined by caller for tracking_mode == PssTrackingMode.voltage"
                )
            if not lower_voltage_limit:
                raise ValueError(
                    "lower_voltage_limit must be defined by caller for tracking_mode == PssTrackingMode.voltage"
                )
        elif tracking_mode == PssTrackingMode.current:
            if not target_current:
                raise ValueError(
                    "target_current must be defined by caller for tracking_mode == PssTrackingMode.current"
                )
            if not upper_current_limit:
                raise ValueError(
                    "upper_current_limit must be defined by caller for tracking_mode == PssTrackingMode.current"
                )
            if not lower_current_limit:
                raise ValueError(
                    "lower_current_limit must be defined by caller for tracking_mode == PssTrackingMode.current"
                )
        else:
            raise RuntimeError(  # pyright: ignore
                f"PssTrackingMode is unknown: {tracking_mode=}"
            )

        def clamp(val: float, min_val: float, max_val: float) -> float:
            return min(max(val, min_val), max_val)

        def conf_voltage_to_adc_voltage(voltage: float) -> float:
            return clamp(voltage, min_val=0.0, max_val=5.0)

        def conf_current_to_adc_voltage(current: float) -> float:
            zero_offset_current: float = 25.0
            min_current: float = -20.0
            max_current: float = 20.0
            sensitivity: float = 0.1
            return (
                clamp(current, min_current, max_current) + zero_offset_current
            ) * sensitivity

        ar = AsyncReturn(callback)

        if tracking_mode == PssTrackingMode.voltage:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_refselect_addr,
                voltage=0.0,
            )
        if tracking_mode == PssTrackingMode.current:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_refselect_addr,
                voltage=5.0,
            )
        if target_voltage:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_target_voltage_addr,
                voltage=conf_voltage_to_adc_voltage(target_voltage),
            )
        if target_current:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_target_current_addr,
                voltage=conf_current_to_adc_voltage(target_current),
            )
        if upper_voltage_limit:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_upper_voltage_limit_addr,
                voltage=conf_voltage_to_adc_voltage(upper_voltage_limit),
            )
        if lower_voltage_limit:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_lower_voltage_limit_addr,
                voltage=conf_voltage_to_adc_voltage(lower_voltage_limit),
            )
        if upper_current_limit:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_upper_current_limit_addr,
                voltage=conf_current_to_adc_voltage(upper_current_limit),
            )
        if lower_current_limit:
            _ = self.get_conf_dac().write(
                addr=Pss.conf_lower_current_limit_addr,
                voltage=conf_current_to_adc_voltage(lower_current_limit),
            )

        self.get_conf_dac().load_all_channels(callback=ar.get_callback())
        return ar

    def output_connect(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Connect the output of the PowerSupplySink."""
        ar = AsyncReturn(callback)

        self.get_conf_dac().write_and_load(
            callback=ar.get_callback(),
            addr=Pss.conf_output_addr,
            voltage=5.0,
        )

        return ar

    def output_disconnect(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Disconnect the output of the PowerSupplySink."""
        ar = AsyncReturn(callback)

        self.get_conf_dac().write_and_load(
            callback=ar.get_callback(),
            addr=Pss.conf_output_addr,
            voltage=0.0,
        )

        return ar

    def get_conf_dac(self) -> Ad5672:
        return cast(Ad5672, self._operation_request_iterators[0])

    def get_curr_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[1])

    def get_volt_adc(self) -> Ads866x:
        return cast(Ads866x, self._operation_request_iterators[2])
