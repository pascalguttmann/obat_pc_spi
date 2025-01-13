from copy import deepcopy
from typing import Any, List, Sequence

from operation_base import OperationBase
from single_transfer_operation import SingleTransferOperation


class SequenceTransferOperation(OperationBase):
    def __init__(self, operations: Sequence[OperationBase]) -> None:
        if not operations:
            raise ValueError(f"Excpected a non-empty list, but got {operations}")

        self._operations = deepcopy(operations)

    def __repr__(self) -> str:
        return f"SequenceTransferOperation: operations={self._operations}"

    def __len__(self) -> int:
        return sum(map(len, self._operations))

    def __eq__(self, other: object, /) -> bool:
        if (
            isinstance(other, SequenceTransferOperation)
            and self._operations == other._operations
        ):
            return True
        else:
            return False

    def get_operations(self) -> Sequence[OperationBase]:
        return self._operations

    def get_single_transfer_operations(self) -> List[SingleTransferOperation]:
        list_list_op = [op.get_single_transfer_operations() for op in self._operations]
        return [op for list_op in list_list_op for op in list_op]

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        Method shall be implemented by child class, which defines structure of
        response.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        """
        _ = operations_rsp
        raise NotImplementedError(
            "SequenceTransferOperation does not implement response parsing."
        )

    def get_parsed_response(self) -> Any:
        try:
            operations_rsp = [op.get_parsed_response() for op in self._operations]
        except NotImplementedError as e:
            raise e
        except ValueError as e:
            raise e

        if all(rsp is None for rsp in operations_rsp):
            return None

        return self._parse_response(operations_rsp)
