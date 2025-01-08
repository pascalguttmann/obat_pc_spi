from __future__ import annotations

from typing import List, TypeVar

from queue import Queue, Empty
from threading import Lock

from spi_operation_request_iterator import (
    SpiOperationRequestIteratorBase,
    SingleTransferOperationRequest,
)


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
        self._queue_lock = Lock()

    def __next__(self) -> SingleTransferOperationRequest:
        """Return operation request from fifo if available. Fallback to the
        default operation request."""
        with self._queue_lock:
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
        return self._operation_request.get_nowait()

    def _put_unprocessed_operation_request(
        self,
        op_req: SingleTransferOperationRequest | List[SingleTransferOperationRequest],
    ) -> None:
        """Put operation request(s), into the fifo that will be processed by
        the physical SpiElement. This method should be used by child classes to
        request the processing of spi operations.
        """
        if not isinstance(op_req, list):
            op_req_list = [op_req]
        else:
            op_req_list = op_req

        with self._queue_lock:
            for x in op_req_list:
                self._operation_request.put_nowait(x)


SpiElement = TypeVar("SpiElement", bound=SpiElementBase)
