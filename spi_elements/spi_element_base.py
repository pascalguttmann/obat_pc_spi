from __future__ import annotations

from typing import List, TypeVar, Any

from queue import Queue, Empty
from threading import RLock

from spi_elements.spi_operation_request_iterator import (
    SpiOperationRequestIteratorBase,
    SingleTransferOperationRequest,
    SequenceTransferOperationRequest,
)
from spi_operation import SingleTransferOperation, SequenceTransferOperation


class SpiElementBase(SpiOperationRequestIteratorBase):
    """SpiElementBase is intended to represent physical Spi devices. They have
    a fifo of operation requests, that shall be processed in sequence. The
    operation requests can be retrieved by calling next(mySpiElementObj).

    The child class representing the type of SpiElement which is used,

    - shall implement methods to fill the operation request queue by calling
      self._put_unprocessed_operation_request().
    - must implement self._get_default_operation_request() to return the
      operation request, that shall be processed when no operation request can
      be retrieved from the fifo.
    """

    def __init__(self) -> None:
        """Initialize the SpiElement with an empty queue."""
        self._operation_request = Queue()
        self._queue_rlock = RLock()

    def __next__(self) -> SingleTransferOperationRequest:
        """Return operation request from fifo if available. Fallback to the
        default operation request."""
        with self._queue_rlock:
            try:
                return self._pop_unprocessed_operation_request()
            except Empty:
                return self._get_default_operation_request()

    def _pop_unprocessed_operation_request(self) -> SingleTransferOperationRequest:
        """Pop the next operation request, that should be written to the
        physical SpiElement from the fifo of unprocessed operations.

        :return: SingleTransferOperationRequest containing the
        SingleTransferOperation with command in binary format (MSB first) that
        shoud be run next.
        """
        with self._queue_rlock:
            return self._operation_request.get_nowait()

    def _put_unprocessed_operation_request(
        self,
        op_req: (
            SingleTransferOperationRequest
            | List[SingleTransferOperationRequest]
            | SequenceTransferOperationRequest
            | List[SequenceTransferOperationRequest]
        ),
    ) -> None:
        """Put operation request(s), into the fifo that will be processed by
        the physical SpiElement. This method should be used by child classes to
        request the processing of spi operations.
        """
        if not isinstance(op_req, list):
            op_req_list = [op_req]
        else:
            op_req_list = op_req

        with self._queue_rlock:
            for x in op_req_list:
                if isinstance(x, SingleTransferOperationRequest):
                    self._operation_request.put_nowait(x)
                elif isinstance(x, SequenceTransferOperationRequest):
                    ops = x.operation.get_operations()
                    sequence_callback = x.callback

                    responses = []

                    def collect_ops_responses(response: Any):
                        responses.append(response)
                        if len(responses) == len(ops) and sequence_callback:
                            sequence_callback(x.operation.get_parsed_response())
                        return None

                    for op in ops:
                        if isinstance(op, SingleTransferOperation):
                            self._put_unprocessed_operation_request(
                                SingleTransferOperationRequest(
                                    operation=op,
                                    callback=collect_ops_responses,
                                )
                            )
                        elif isinstance(op, SequenceTransferOperation):
                            self._put_unprocessed_operation_request(
                                SequenceTransferOperationRequest(
                                    operation=op,
                                    callback=collect_ops_responses,
                                )
                            )
                        else:
                            raise ValueError(
                                f"Operation must be of type SingleTransferOperation or SequenceTransferOperation, but got {op} of type {type(op)}"
                            )

                else:
                    raise ValueError(
                        f"OperationRequest must be of type SingleTransferOperationRequest or SequenceTransferOperationRequest, but got {x} of type {type(x)}"
                    )


SpiElement = TypeVar("SpiElement", bound=SpiElementBase)
