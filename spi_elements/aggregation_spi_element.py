from typing import Any, List
from bitarray import bitarray
from itertools import accumulate

from spi_operation import SingleTransferOperation


class AggregationOperation(SingleTransferOperation):
    def __init__(self, ops: List[SingleTransferOperation]) -> None:
        self._ops = ops
        cmd = sum([op.get_command() for op in ops], bitarray())
        super().__init__(cmd)

    def _parse_response(self, rsp: bitarray) -> Any:
        bitlens = [op.get_bitlength() for op in self._ops]
        offsets = list(accumulate(bitlens, initial=0))
        return (
            rsp[offset : offset + bitlen] for offset, bitlen in zip(offsets, bitlens)
        )
