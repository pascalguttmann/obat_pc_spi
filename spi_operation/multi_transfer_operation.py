from bitarray import bitarray
from copy import deepcopy
from typing import Optional, List

from operation_base import OperationBase


class MultiTransferOperation(OperationBase):
    def __init__(self, operations: List[OperationBase]) -> None:
        if not operations:
            raise ValueError(f"Excpected a non-empty list, but got {operations}")

        self._operations = deepcopy(operations)

    def __repr__(self) -> str:
        return f"MultiTransferOperation: operations={self._operations}"

    def __len__(self) -> int:
        return sum(map(len, self._operations))

    def __eq__(self, other: object, /) -> bool:
        if (
            isinstance(other, MultiTransferOperation)
            and self._operations == other._operations
        ):
            return True
        else:
            return False
