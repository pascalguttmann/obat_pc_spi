from __future__ import annotations

from abc import abstractmethod
from typing import Any, List, Optional, Tuple
from copy import deepcopy
from bitarray import bitarray
from warnings import warn
from util import reverse_string, concat_bitarray
from spi_operation import SingleTransferOperation, SequenceTransferOperation

# ADS866x WORD == 32 bit


class Ads866xSingleTransferOperation(SingleTransferOperation):
    """SingleTransferOperation of Ads866x with its structure."""

    def __init__(
        self,
        op: bitarray | None = None,
        byte_selector: bitarray | None = None,
        addr: bitarray | None = None,
        data: bitarray | None = None,
        response: Optional[bitarray] = None,
        response_required: bool = True,
    ):
        if not op:
            op = bitarray(reverse_string("00000"))
        if not byte_selector:
            byte_selector = bitarray(reverse_string("00"))
        if not addr:
            addr = bitarray(reverse_string("0 00000000"))
        if not data:
            data = bitarray(reverse_string("00000000 00000000"))

        super().__init__(
            command=concat_bitarray(
                self.check_data(data),
                self.check_addr(addr),
                self.check_byte_selector(byte_selector),
                self.check_op(op),
            ),
            response=response,
            response_required=response_required,
        )

    def _parse_response(self, rsp: bitarray) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        Implements the default _parse_response() method for all
        Ads866xSingleTransferOperations to return 'None'. Should be
        overwritten, by operations that require response parsing.

        :param rsp: bitarray response of spi transfer.
        :return: None
        """
        if not len(rsp) == 32:
            raise ValueError(
                f"Ads866xSingleTransferOperation expected 32-Bit response, but got {rsp=}"
            )

        return None

    def check_op(self, op: bitarray):
        if len(op) != 5:
            raise ValueError(f"Expected 5-bit op, but got {op=}")
        return op

    def check_byte_selector(self, bs: bitarray):
        if len(bs) != 2:
            raise ValueError(f"Expected 2-bit byteselector, but got {bs=}")
        return bs

    def check_addr(self, addr: bitarray):
        if len(addr) != 9:
            raise ValueError(f"Expected 9-bit addr, but got {addr=}")
        if addr[0] == 1:
            addr_old = deepcopy(addr)
            addr[0] = 0
            warn(
                f"ADS866x: Address {addr_old} is not aligned to 2-byte, aligned to {addr}"
            )
        return addr

    def check_data(self, data: bitarray):
        if len(data) != 16:
            raise ValueError(f"Expected 16-bit data, but got {data=}")
        return data


class Nop(Ads866xSingleTransferOperation):
    """No operation"""

    def __init__(self):
        super().__init__(response_required=False)


class ClearHword(Ads866xSingleTransferOperation):
    """Clear up to half word worth bits of a register"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Any bit marked 1 in the data field results in that particular bit of
        the specified register being reset to 0, leaving the other bits
        unchanged.

        :param addr: 9-bit addr of halfword
        :param data: 16-bit data
        """

        super().__init__(
            op=bitarray(reverse_string("11000")),
            addr=addr,
            data=data,
            response_required=False,
        )


class SetHword(Ads866xSingleTransferOperation):
    """Set up to half word worth bits of a register"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Any bit marked 1 in the data field results in that particular bit of
        the specified register being set to 1, leaving the other bits
        unchanged.

        :param addr: 9-bit addr of halfword
        :param data: 16-bit data
        """

        super().__init__(
            op=bitarray(reverse_string("11011")),
            addr=addr,
            data=data,
            response_required=False,
        )


class ReadHword(Ads866xSingleTransferOperation):
    """Read a half word read operation"""

    def __init__(self, addr: bitarray):
        """Read the data of the half word at address 'addr'.

        :param addr: 9-bit addr of halfword
        """

        super().__init__(
            op=bitarray(reverse_string("11001")),
            addr=addr,
            response_required=True,
        )

    def _parse_response(self, rsp: bitarray) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        :param rsp: bitarray response of spi transfer.
        :return: 16-Bit bitarray containing halfword register data.
        """
        if len(rsp) != 32:
            raise ValueError(f"ReadHword expected 32-Bit response, but got {rsp=}")

        register_data = rsp[16:32]

        # No information in the datasheet are found, that parity is appended
        # after the ReadHword Frame. But from observation it seems to be
        # appended. Only checking for last 14-Bits. (Parity is unchecked,
        # because it is undocumented behavior.)
        zeros = rsp[0:14]

        if any(zeros):
            raise ValueError(
                f"ReadHword expected 14-Bit trailing zeros in response, but got {rsp=}"
            )

        return register_data


class WriteHword(Ads866xSingleTransferOperation):
    """Write a half word read operation"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Write the data of the half word at address 'addr'.

        :param addr: 9-bit addr of halfword
        :param data: 16-bit data
        """

        super().__init__(
            op=bitarray(reverse_string("11010")),
            addr=addr,
            data=data,
            response_required=False,
        )


class Ads866xWordOperation(SequenceTransferOperation):

    def __init__(
        self,
        addr: bitarray,
        data: bitarray = bitarray(
            reverse_string("00000000 00000000 00000000 00000000")
        ),
    ):
        addr_ba = self.check_addr(bitarray(addr))
        data_ba = self.check_data(bitarray(data))

        addr_upper = deepcopy(addr_ba)
        addr_upper[1] = 1
        addr_lower = deepcopy(addr_ba)
        data_upper = data_ba[16:32]
        data_lower = data_ba[0:16]

        upper_hword, lower_hword = self._create_upper_and_lower_operation(
            addr_upper, addr_lower, data_upper, data_lower
        )
        super().__init__([upper_hword, lower_hword])

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        Implements the default _parse_response() method for all
        Ads866xWordOperation to return 'None'. Should be overwritten, by
        operations that require response parsing.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        :return: None
        """
        if not len(operations_rsp) == 2:
            raise ValueError(
                f"Ads866xWordOperation expected list of two responses, but got {operations_rsp=}"
            )

        return None

    @abstractmethod
    def _create_upper_and_lower_operation(
        self,
        addr_upper: bitarray,
        addr_lower: bitarray,
        data_upper: bitarray,
        data_lower: bitarray,
    ) -> Tuple[Ads866xSingleTransferOperation, Ads866xSingleTransferOperation]:
        """Create and return a tuple of two Ads866xSingleTransferOperations
        which write the upper and lower data to the corresponding address."""

    def check_addr(self, addr: bitarray):
        if len(addr) != 9:
            raise ValueError(f"Expected 9-bit addr, but got {addr=}")
        if addr[0] == 1 or addr[1] == 1:
            addr_old = deepcopy(addr)
            addr[-2] = 0
            addr[-1] = 0
            warn(
                f"ADS866x: Address {addr_old} is not aligned to 4-byte, aligned to {addr}"
            )
        return addr

    def check_data(self, data: bitarray):
        if len(data) != 32:
            raise ValueError(f"Expected 32-bit data, but got {data=}")
        return data


class ClearWord(Ads866xWordOperation):
    """Clear up to word worth bits of a register"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Any bit marked 1 in the data field results in that particular bit of
        the specified register being reset to 0, leaving the other bits
        unchanged.

        :param addr: 9-bit addr ofword
        :param data: 32-bit data
        """
        super().__init__(addr, data)

    def _create_upper_and_lower_operation(
        self,
        addr_upper: bitarray,
        addr_lower: bitarray,
        data_upper: bitarray,
        data_lower: bitarray,
    ) -> Tuple[Ads866xSingleTransferOperation, Ads866xSingleTransferOperation]:
        """Create and return a tuple of two Ads866xSingleTransferOperations
        which write the upper and lower data to the corresponding address."""
        return (ClearHword(addr_upper, data_upper), ClearHword(addr_lower, data_lower))


class SetWord(Ads866xWordOperation):
    """Set up to word worth bits of a register"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Any bit marked 1 in the data field results in that particular bit of
        the specified register being set to 1, leaving the other bits
        unchanged.

        :param addr: 9-bit addr ofword
        :param data: 32-bit data
        """
        super().__init__(addr, data)

    def _create_upper_and_lower_operation(
        self,
        addr_upper: bitarray,
        addr_lower: bitarray,
        data_upper: bitarray,
        data_lower: bitarray,
    ) -> Tuple[Ads866xSingleTransferOperation, Ads866xSingleTransferOperation]:
        """Create and return a tuple of two Ads866xSingleTransferOperations
        which write the upper and lower data to the corresponding address."""
        return (SetHword(addr_upper, data_upper), SetHword(addr_lower, data_lower))


class ReadWord(Ads866xWordOperation):
    """Read a word operation"""

    def __init__(self, addr: bitarray):
        """Read the data of the word at address 'addr'.

        :param addr: 9-bit addr ofword
        """
        super().__init__(addr)

    def _create_upper_and_lower_operation(
        self,
        addr_upper: bitarray,
        addr_lower: bitarray,
        data_upper: bitarray,
        data_lower: bitarray,
    ) -> Tuple[Ads866xSingleTransferOperation, Ads866xSingleTransferOperation]:
        """Create and return a tuple of two Ads866xSingleTransferOperations
        which write the upper and lower data to the corresponding address."""
        _, _ = data_upper, data_lower
        return (ReadHword(addr_upper), ReadHword(addr_lower))

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        :return: 32-Bit bitarray containing word register data.
        """
        if not len(operations_rsp) == 2:
            raise ValueError(
                f"ReadWord expected list of two responses, but got {operations_rsp=}"
            )
        for op_rsp in operations_rsp:
            if not isinstance(op_rsp, bitarray):
                raise ValueError(
                    f"ReadWord expected sub operations to return bitarrays, but got {type(op_rsp)=}"
                )
            if not len(op_rsp) == 16:
                raise ValueError(
                    f"ReadWord expected sub operations 16-Bit bitarray, but got {len(op_rsp)=}"
                )

        upper_hword = operations_rsp[0]
        lower_hword = operations_rsp[1]

        word = concat_bitarray(lower_hword, upper_hword)

        return word


class WriteWord(Ads866xWordOperation):
    """Write a word operation"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Write the data of the word at address 'addr'.

        :param addr: 9-bit addr ofword
        :param data: 32-bit data
        """
        super().__init__(addr, data)

    def _create_upper_and_lower_operation(
        self,
        addr_upper: bitarray,
        addr_lower: bitarray,
        data_upper: bitarray,
        data_lower: bitarray,
    ) -> Tuple[Ads866xSingleTransferOperation, Ads866xSingleTransferOperation]:
        """Create and return a tuple of two Ads866xSingleTransferOperations
        which write the upper and lower data to the corresponding address."""
        return (WriteHword(addr_upper, data_upper), WriteHword(addr_lower, data_lower))


class WriteVerifyWord(SequenceTransferOperation):
    """Write a word and verify written data by readback."""

    def __init__(self, addr: bitarray, data: bitarray):
        """Write the data of the word at address 'addr'.

        :param addr: 9-bit addr ofword
        :param data: 32-bit data
        """
        ops = []
        ops.append(WriteWord(addr=addr, data=data))
        ops.append(ReadWord(addr=addr))

        self._expected_data = data
        super().__init__(ops)

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        :return: bool, True if verification successful, False otherwise
        """
        if not len(operations_rsp) == 2:
            raise ValueError(
                f"WriteVerifyWord expected list of two responses, but got {operations_rsp=}"
            )

        write_rsp = operations_rsp[0]
        if write_rsp is not None:
            raise ValueError(
                f"WriteVerifyWord expected WriteWord to return 'None', but got {write_rsp=}"
            )

        read_rsp = operations_rsp[1]
        if not isinstance(read_rsp, bitarray):
            raise ValueError(
                f"WriteVerifyWord expected sub operations to return bitarrays, but got {type(read_rsp)=}"
            )
        if not len(read_rsp) == 32:
            raise ValueError(
                f"WriteVerifyWord expected sub operations 32-Bit bitarray, but got {len(read_rsp)=}"
            )

        return self._expected_data == read_rsp
