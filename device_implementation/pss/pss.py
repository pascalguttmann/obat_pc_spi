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

    _pss_min_voltage_set: float = 0.0  # V
    _pss_max_voltage_set: float = 5.0  # V
    _pss_zero_offset_current: float = 25.0  # A
    _pss_min_current_set: float = -20.0  # A
    _pss_max_current_set: float = 20.0  # A
    _pss_sensitivity: float = 0.1  # V/A

    def __init__(self) -> None:
        super().__init__(
            [
                Ad5672(),
                Ads866x(),
                Ads866x(),
            ]
        )

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
            self.get_conf_dac().nop(callback=collect_ops_responses),
            self.get_curr_adc().nop(callback=collect_ops_responses),
            self.get_volt_adc().nop(callback=collect_ops_responses),
        ]

        return ar

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
            self.get_curr_adc().write_gpo(
                callback=collect_ops_responses,
                gpo_val=Ads866xGpoVal.HIGH,
            ),
            self.get_volt_adc().initialize(
                callback=collect_ops_responses,
                input_range=Ads866xInputRange.UNIPOLAR_5V12,
            ),
            self.get_volt_adc().write_gpo(
                callback=collect_ops_responses,
                gpo_val=Ads866xGpoVal.HIGH,
            ),
            self.output_disconnect(
                callback=collect_ops_responses,
            ),
            self.write_config(
                callback=collect_ops_responses,
                tracking_mode=PssTrackingMode.voltage,
                target_voltage=0.0,
                target_current=0.0,
                lower_voltage_limit=0.0,
                upper_voltage_limit=5.0,
                lower_current_limit=-20.0,
                upper_current_limit=+20.0,
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

        def adc_voltage_to_conf_voltage(voltage: float) -> float:
            return voltage

        def adc_voltage_to_conf_current(voltage: float) -> float:
            return voltage / self._pss_sensitivity - self._pss_zero_offset_current

        ar = AsyncReturn(callback)
        sequence_callback = ar.get_callback()

        responses = [{"data": None, "called": False}, {"data": None, "called": False}]

        def collect_ops_responses(response: Any, id: int):
            responses[id]["data"] = response
            responses[id]["called"] = True

            if all([rsp["called"] for rsp in responses]) and sequence_callback:
                sequence_return = (
                    adc_voltage_to_conf_voltage(responses[0]["data"]),
                    adc_voltage_to_conf_current(responses[1]["data"]),
                )
                sequence_callback(sequence_return)
            return None

        self.get_volt_adc().read(callback=partial(collect_ops_responses, id=0))
        self.get_curr_adc().read(callback=partial(collect_ops_responses, id=1))
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

        if tracking_mode is None:
            raise ValueError("tracking_mode must be defined by caller")
        if tracking_mode == PssTrackingMode.voltage:
            if target_voltage is None:
                raise ValueError(
                    "target_voltage must be defined by caller for tracking_mode == PssTrackingMode.voltage"
                )
            if upper_current_limit is None:
                raise ValueError(
                    "upper_current_limit must be defined by caller for tracking_mode == PssTrackingMode.voltage"
                )
            if lower_current_limit is None:
                raise ValueError(
                    "lower_current_limit must be defined by caller for tracking_mode == PssTrackingMode.voltage"
                )
        elif tracking_mode == PssTrackingMode.current:
            if target_current is None:
                raise ValueError(
                    "target_current must be defined by caller for tracking_mode == PssTrackingMode.current"
                )
            if upper_voltage_limit is None:
                raise ValueError(
                    "upper_voltage_limit must be defined by caller for tracking_mode == PssTrackingMode.current"
                )
            if lower_voltage_limit is None:
                raise ValueError(
                    "lower_voltage_limit must be defined by caller for tracking_mode == PssTrackingMode.current"
                )
        else:
            raise RuntimeError(  # pyright: ignore
                f"PssTrackingMode is unknown: {tracking_mode=}"
            )

        if upper_voltage_limit and lower_voltage_limit:
            if upper_voltage_limit < lower_voltage_limit:
                raise ValueError(
                    f"Invalid configuration: {upper_voltage_limit=} is smaller than {lower_voltage_limit=}"
                )

        if upper_current_limit and lower_current_limit:
            if upper_current_limit < lower_current_limit:
                raise ValueError(
                    f"Invalid configuration: {upper_current_limit=} is smaller than {lower_current_limit=}"
                )

        def clamp(val: float, min_val: float, max_val: float) -> float:
            return min(max(val, min_val), max_val)

        def conf_voltage_to_adc_voltage(voltage: float) -> float:
            return clamp(
                voltage,
                min_val=self._pss_min_voltage_set,
                max_val=self._pss_max_voltage_set,
            )

        def conf_current_to_adc_voltage(current: float) -> float:
            return (
                clamp(current, self._pss_min_current_set, self._pss_max_current_set)
                + self._pss_zero_offset_current
            ) * self._pss_sensitivity

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
