from typing import Optional
from bitarray import bitarray
from warnings import warn
from spi_operation import SingleTransferOperation

# ADS866x WORD == 32 bit


class Ads866xSingleTransferOperation(SingleTransferOperation):
    """SingleTransferOperation of Ads866x with its structure."""

    def __init__(
        self,
        op: str = "00000",
        byte_selector: str = "00",
        addr: str = "0 00000000",
        data: str = "00000000 00000000",
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

    def __init__(self, addr: str, data: str):
        """Any bit marked 1 in the data field results in that particular bit of
        the specified register being reset to 0, leaving the other bits
        unchanged.

        :param addr: 9-bit addr of halfword
        :param data: 16-bit data
        """

        super().__init__(
            op="11000",
            addr=addr,
            data=data,
            response_required=False,
        )


class SetHword(Ads866xSingleTransferOperation):
    """Set up to half word worth bits of a register"""

    def __init__(self, addr: str, data: str):
        """Any bit marked 1 in the data field results in that particular bit of
        the specified register being set to 1, leaving the other bits
        unchanged.

        :param addr: 9-bit addr of halfword
        :param data: 16-bit data
        """

        super().__init__(
            op="11011",
            addr=addr,
            data=data,
            response_required=False,
        )


class ReadHword(Ads866xSingleTransferOperation):
    """Read a half word read operation"""

    def __init__(self, addr: str):
        """Read the data of the half word at address 'addr'.

        :param addr: 9-bit addr of halfword
        """

        super().__init__(
            op="11001",
            addr=addr,
            response_required=True,
        )


class WriteHword(Ads866xSingleTransferOperation):
    """Write a half word read operation"""

    def __init__(self, addr: str):
        """Write the data of the half word at address 'addr'.

        :param addr: 9-bit addr of halfword
        """

        super().__init__(
            op="11010",
            addr=addr,
            response_required=False,
        )
