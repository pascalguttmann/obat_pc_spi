from typing import Any, List
from bitarray import bitarray
from itertools import accumulate

from spi_operation import SingleTransferOperation
from spi_elements.spi_operation_iterator import (
    SpiOperationIteratorBase,
    SingleTransferOperationRequest,
)


class AggregateOperation(SingleTransferOperation):
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


class AggregateOperationIterator(SpiOperationIteratorBase):
    def __init__(
        self, operation_request_iterators: List[SpiOperationIteratorBase]
    ) -> None:
        self._operation_request_iterators = operation_request_iterators

    def __next__(self) -> SingleTransferOperationRequest:
        return self._get_default_operation_request()

    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        operation_requests = [
            next(op_req_it) for op_req_it in self._operation_request_iterators
        ]

        def process_sub_operation_requests(*args) -> None:
            for op_req, response in zip(operation_requests, args):
                if op_req.operation.get_response_required():
                    op_req.operation.set_response(response)
                if op_req.callback:
                    op_req.callback(op_req.operation.get_parsed_response())
            return None

        return SingleTransferOperationRequest(
            operation=AggregateOperation(
                [op_req.operation for op_req in operation_requests]
            ),
            callback=process_sub_operation_requests,
        )
