from bitarray import bitarray
from copy import deepcopy
from typing import Optional, List

from operation_base import OperationBase
from single_transfer_operation import SingleTransferOperation


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

    def get_single_transfer_operations(self) -> List[SingleTransferOperation]:
        list_list_op = [op.get_single_transfer_operations() for op in self._operations]
        return [op for list_op in list_list_op for op in list_op]
