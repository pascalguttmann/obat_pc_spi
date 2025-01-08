from __future__ import annotations

from abc import abstractmethod
from typing import Optional, Tuple
from copy import deepcopy
from bitarray import bitarray
from warnings import warn
from spi_operation import SingleTransferOperation, SequenceTransferOperation

# ADS866x WORD == 32 bit


class Ads866xSingleTransferOperation(SingleTransferOperation):
    """SingleTransferOperation of Ads866x with its structure."""

    def __init__(
        self,
        op: bitarray = bitarray("00000"),
        byte_selector: bitarray = bitarray("00"),
        addr: bitarray = bitarray("0 00000000"),
        data: bitarray = bitarray("00000000 00000000"),
        response: Optional[bitarray] = None,
        response_required: bool = True,
    ):
        super().__init__(
            command=self.check_op(bitarray(op))
            + self.check_byte_selector(bitarray(byte_selector))
            + self.check_addr(bitarray(addr))
            + self.check_data(bitarray(data)),
            response=response,
            response_required=response_required,
        )

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
        if addr[-1] == 1:
            warn(
                f"ADS866x: Address {addr} is not aligned to 2-byte, aligning to {bitarray(addr[:-1]+bitarray('0'))}"
            )
            addr[-1] = 0
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
            op=bitarray("11000"),
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
            op=bitarray("11011"),
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
            op=bitarray("11001"),
            addr=addr,
            response_required=True,
        )


class WriteHword(Ads866xSingleTransferOperation):
    """Write a half word read operation"""

    def __init__(self, addr: bitarray, data: bitarray):
        """Write the data of the half word at address 'addr'.

        :param addr: 9-bit addr of halfword
        :param data: 16-bit data
        """

        super().__init__(
            op=bitarray("11010"),
            addr=addr,
            data=data,
            response_required=False,
        )


class Ads866xWordOperation(SequenceTransferOperation):

    def __init__(
        self,
        addr: bitarray,
        data: bitarray = bitarray("00000000 00000000 00000000 00000000"),
    ):
        addr_ba = self.check_addr(bitarray(addr))
        data_ba = self.check_data(bitarray(data))

        addr_upper = deepcopy(addr_ba)
        addr_upper[-2] = 1
        addr_lower = deepcopy(addr_ba)
        data_upper = data_ba[:16]
        data_lower = data_ba[16:]

        upper_hword, lower_hword = self._create_upper_and_lower_operation(
            addr_upper, addr_lower, data_upper, data_lower
        )
        super().__init__([upper_hword, lower_hword])

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
        if addr[-1] == 1 or addr[-2] == 1:
            warn(
                f"ADS866x: Address {addr} is not aligned to 4-byte, aligning to {bitarray(addr[:-2]+bitarray('00'))}"
            )
            addr[-2] = 0
            addr[-1] = 0
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
    """Read a word read operation"""

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


class WriteWord(Ads866xWordOperation):
    """Write a word read operation"""

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
