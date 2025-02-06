from typing import Any, List

from bitarray import bitarray

from spi_operation import SequenceTransferOperation
import device_implementation.dac.ad5672.register_operations as op
from util.util_str import reverse_string


class Initialize(SequenceTransferOperation):
    """Initialize the Ad5672R dac."""

    def __init__(self):
        """Initialize the dac for operation in daisychain with 0V to 5V output range."""
        ops = []

        # DAISYCHAIN mode
        # ===============
        #
        # For daisychain operation with multiple devices the device MUST NOT be
        # reset or the daisychain mode disabled. In order to not put the entire
        # daisychain in a disfunctional state. (The chain can only be brought back
        # into functional state, by a write sequence of unequal bitlength, which is
        # by design not supported by the obat software at this point (06. Feb 2025).)
        #
        # Reason
        # ------
        #
        # Ad5672R features daisychain mode == enabled or daisychain mode == disabled
        #
        # ### daisychain mode == enabled
        #
        # The chip works, as one would expect, like a shift register.
        #
        # ### daisychain mode == disabled
        #
        # The chip requires exact writes of
        # 24-bit in order to execute the desired command. Contrary to behavior, that
        # would be easy to implement with equal length writes, the chip in this mode
        # clocks in the first 24 bits transmitted and ignores following bits.
        # I.e. a write sequence preceeded by zeros for other chips behind the
        # ad5672r in mode daisychain disabled prevents a following 0x800001
        # (command to set daisychain mode to enabled) to be executed by the
        # ad5672r, because the leading zeros filled the 24 bit expected by the
        # ad5672r.
        #
        # This violates the mental model of the ad5672r in daisychain mode
        # disabled as a shift register, that has a disable output (i.e. bits
        # which would be shifted out are just shifted into "nothingness").
        #
        # Workaround
        # ----------
        #
        # Before using equal length transfers use a write sequence, _specialized_ to
        # the daisychain configuration connected to set all the ad5672r chips to
        # daisychain mode enabled.
        # After that, continue normally with equal length transfers, without
        # setting any of the ad5672r to daisychain mode disabled.
        # Possible ways to set daisychain mode to disabled:
        #   - Power on reset
        #   - Software reset (command 0x601234)
        #   - Explicitly set daisychain mode to disabled (command 0x800000)

        # LDAC Mask register
        # ==================
        #
        # The ldac mask register masks, the functionality of the LDAC pin.
        #
        # ldac mask bit == 0
        # ------------------
        #
        # Loading DAC register from input register is possible with:
        #   - LDAC hardware pin falling *edge*
        #   - Software command 0x2
        #   - Software command 0x3
        #
        # ldac mask bit == 1
        # ------------------
        #
        # Loading DAC register from input register is possible with:
        #   - Software command 0x2
        #   - Software command 0x3
        #
        # LDAC hardware pin falling *edges* are ignored.
        #
        # When tying LDAC hardware pin permanently low it is possible, that
        # ad5672r detects this and distinguishes between falling *edges* and
        # low voltage *levels*.

        ops.append(
            op.WriteLoadDacMaskRegister(data=bitarray(reverse_string("11111111")))
        )
        ops.append(op.InternalReferenceSetup())

        super().__init__(ops)

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        :return: None
        """
        if not len(operations_rsp) == 4:
            raise ValueError(
                f"Initialize expected list of 4 responses, but got {operations_rsp=}"
            )
        return None


class LoadAllChannels(op.UpdateDacRegisters):
    def __init__(self):
        """Load input register contents to dac registers updating the analog
        voltage output for all channels."""
        super().__init__(data=bitarray(reverse_string("11111111")))
