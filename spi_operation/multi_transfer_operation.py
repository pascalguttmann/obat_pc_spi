from bitarray import bitarray
from typing import Optional, List

from operation_base import OperationBase


class MultiTransferOperation(OperationBase):
    def __init__(self, operations: List[OperationBase]) -> None:
        self._operations = operations

    def __repr__(self) -> str:
        return f"MultiTransferOperation: operations={self._operations}"

    def __len__(self) -> int:
        return sum(map(len, self._operations))
